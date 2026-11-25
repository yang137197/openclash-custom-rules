"""Lua/curl controller HTTP fault fixture; all traffic is loopback/synthetic."""
import argparse
import copy
import datetime
import json
from pathlib import Path
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.parse

from lua_controller_fixture_runtime import install
from verify_liangxinyun_readonly import FAKE_SECRET, GROUP_PATH, PROVIDER_PATH, URL

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.5'
GROUP_PATH = '/proxies/' + urllib.parse.quote('良心云-按档位自动切换', safe='')
CASES = []


def run(lua, case, *, mode='--once', mutate=None, fault=None, args=(), expected=0):
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    names = ['LXY: 日本专线01', 'LXY: 日本专线02', 'LXY: 日本高速01', 'LXY: 美国05|流媒体']
    group = {'type': 'Selector', 'all': ['REJECT', *names], 'now': names[0]}
    provider = {'name': 'liangxinyun', 'testUrl': URL, 'expectedStatus': '204', 'updatedAt': 'fixture',
                'proxies': [{'name': name, 'extra': {URL: {'alive': True,
                             'history': [{'time': stamp, 'delay': 100-i*10}]}}}
                            for i, name in enumerate(names)]}
    if mutate:
        mutate(group, provider)
    before = group['now']
    requests, failures = [], []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def request(self):
            requests.append((self.command, self.path))
            if self.headers.get('Authorization') != 'Bearer '+FAKE_SECRET:
                failures.append('authorization missing or misquoted')
            status, body = 200, None
            if self.path == '/version':
                body = {'version': 'synthetic-core'}
            elif self.path == GROUP_PATH:
                if self.command == 'PUT':
                    selected = json.loads(self.rfile.read(int(self.headers['Content-Length'])))['name']
                    if fault != 'unapplied-write':
                        group['now'] = selected
                    status = 204
                else:
                    body = group
            elif self.path == PROVIDER_PATH:
                body = provider
            elif self.path == PROVIDER_PATH+'/healthcheck' and self.command == 'GET':
                status = 204
            else:
                failures.append('unexpected method/path')
                status = 405
            if fault == 'http-503':
                status = 503
            elif fault == 'redirect':
                status = 302
            elif fault == 'provider-race' and self.path == GROUP_PATH:
                group['now'] = names[1] if group['now'] == names[0] else names[0]
            data = b'invalid-json' if fault == 'bad-json' else json.dumps(body, ensure_ascii=False).encode() if body else b''
            self.send_response(status)
            if status == 302:
                self.send_header('Location', 'http://127.0.0.1:1/forbidden')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        do_GET = do_PUT = do_POST = do_DELETE = request

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with tempfile.TemporaryDirectory(prefix='lua-controller-api-') as directory:
            home = Path(directory)
            env = install(home, lua)
            secret = home/'secret'
            secret.write_text(FAKE_SECRET)
            argv_log = home/'curl-argv'
            (home/'bin/curl').write_text(
                '#!/usr/bin/python3\nimport json,os,sys\n'
                f'with open({str(argv_log)!r},"a") as f: f.write(json.dumps(sys.argv[1:])+"\\n")\n'
                'os.execv("/usr/bin/curl", ["/usr/bin/curl",*sys.argv[1:]])\n')
            (home/'bin/curl').chmod(0o700)
            command = [str(lua), str(DIRECTORY/'liangxinyun-controller.lua'), mode,
                       '--api-url', f'http://127.0.0.1:{server.server_port}', '--secret-file', str(secret),
                       '--lock-file', str(home/'lock'), '--state-file', str(home/'state'), *args]
            completed = subprocess.run(command, env=env, capture_output=True, text=True, timeout=35)
            assert completed.returncode == expected, (case, completed.stdout, completed.stderr)
            assert not completed.stderr, (case, completed.stderr)
            assert FAKE_SECRET not in completed.stdout+completed.stderr
            output = json.loads(completed.stdout.splitlines()[-1])
            if mode in ('--preflight', '--dry-run'):
                assert group['now'] == before
                assert not (home/'state').exists() and not (home/'lock').exists()
                assert all(method == 'GET' and not path.endswith('/healthcheck') for method, path in requests)
            elif (home/'state').exists():
                assert (home/'state').stat().st_mode & 0o777 == 0o600
                assert (home/'lock').stat().st_mode & 0o777 == 0o600
            if argv_log.exists():
                assert FAKE_SECRET not in argv_log.read_text(), 'credential in argv'
            assert not failures, failures
    finally:
        server.shutdown()
        server.server_close()
    assert all(method != 'PUT' or path == GROUP_PATH for method, path in requests)
    CASES.append(case)
    print('PASS '+case, flush=True)
    return output, requests, group


def main():
    global DIRECTORY
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lua', type=Path, required=True)
    parser.add_argument('--candidate-directory', type=Path, default=DIRECTORY)
    a = parser.parse_args()
    DIRECTORY = a.candidate_directory.resolve(strict=True)
    lua = a.lua.resolve(strict=True)
    out, _, _ = run(lua, 'compatible-preflight-readonly', mode='--preflight')
    assert out['candidateCompatible'] and not out['selectionApplied']
    out, _, _ = run(lua, 'dry-run-no-probe-no-write', mode='--dry-run')
    assert out['wouldSelect'] == 'LXY: 日本专线02' and out['readOnly']
    out, requests, group = run(lua, 'control-startup-probe-select-readback')
    first_write = next(i for i,r in enumerate(requests) if r[0]=='PUT')
    assert requests.index(('GET', PROVIDER_PATH+'/healthcheck')) > first_write
    assert group['now'] == out['wouldSelect'] == 'LXY: 日本专线02' and out['verifiedSelection']
    for label, change in (
        ('legacy-selector', lambda g,p: g['all'].remove('REJECT')),
        ('provider-contract', lambda g,p: p.update(expectedStatus='200')),
        ('provider-source', lambda g,p: p.update(name='ikuuu')),
        ('member-mismatch', lambda g,p: g['all'].pop()),
        ('ineligible-node', lambda g,p: (g['all'].append('LXY: 香港01'),p['proxies'].append({'name':'LXY: 香港01'}))),
    ):
        _, rr, _ = run(lua, label+'-not-adopted', mutate=change, expected=1)
        assert all(method=='GET' and not path.endswith('/healthcheck') for method,path in rr)
    out, _, _ = run(lua, 'old-profile-preflight-stays-readonly', mode='--preflight',
                    mutate=lambda g,p: g['all'].remove('REJECT'))
    assert not out['candidateCompatible']
    for fault in ('http-503', 'redirect', 'bad-json', 'provider-race', 'unapplied-write'):
        out, _, _ = run(lua, fault, fault=fault, expected=1)
        assert not out.get('verifiedSelection', False)
    def unknown(g,p):
        p['proxies'][0]['extra'] = p['proxies'][1]['extra'] = {}
    out, _, group = run(lua, 'unknown-high-tier-reject', mutate=unknown)
    assert out['wouldSelect'] == group['now'] == 'REJECT'
    for label, args in (
        ('non-loopback', ('--api-url','http://192.0.2.1:9090')),
        ('URL-injection', ('--api-url','http://127.0.0.1:9090/path')),
        ('timing-invalid', ('--poll','70')),
        ('conflicting-modes', ('--dry-run',)),
    ):
        _, rr, _ = run(lua, label, args=args, expected=1)
        assert not rr
    print(f'PASS: {len(CASES)} v1.8.5 Lua/curl HTTP and CLI scenarios (native modules substituted)')


if __name__ == '__main__':
    main()
