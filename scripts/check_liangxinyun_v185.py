#!/usr/bin/env python3
"""Opt-in, loopback-only real Mihomo + Ruby/Lua controller regression fixture."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import yaml
from strict_yaml import load_yaml
from check_liangxinyun_priority import LocalProxy, Tunnel, free_port, outgoing

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.5'
TEST_URL = 'http://fixture.test/generate_204'
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
GROUP = '良心云-按档位自动切换'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core', required=True, type=Path)
    runtime = parser.add_mutually_exclusive_group(required=True)
    runtime.add_argument('--ruby-command', help='JSON array, e.g. ["ruby"]')
    runtime.add_argument('--lua', type=Path, help='Lua 5.1 executable; local LuCI/nixio substitutes are used')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--candidate-directory', type=Path, help='local Lua candidate directory')
    args = parser.parse_args()
    ruby = json.loads(args.ruby_command) if args.ruby_command else [str(args.lua.resolve(strict=True))]
    directory = DIRECTORY
    if args.candidate_directory:
        assert args.lua, 'candidate-directory is for the Lua fixture'
        directory = args.candidate_directory.resolve(strict=True)
    core = args.core.resolve(strict=True)
    module = load_yaml((directory / 'openclash-overwrite.conf').read_text(encoding='utf-8'), module=True)
    local = load_yaml((directory / 'local-tiktok-proxy.conf').read_text(encoding='utf-8'), module=True)
    core_version = subprocess.check_output([str(core), '-v'], text=True).strip()
    ruby_version = subprocess.check_output([*ruby, '-v'], text=True, stderr=subprocess.STDOUT).strip()
    nodes, servers, by_tier, results = [], [], [], []
    states = {}
    secret = 'fixture "secret" $ backslash\\token'

    def add(label, delay):
        server = LocalProxy(('127.0.0.1', 0), Tunnel)
        server.label = 'LXY: ' + label
        server.state = {'up': True, 'delay': delay}
        threading.Thread(target=server.serve_forever, daemon=True).start()
        servers.append(server)
        states[server.label] = server.state
        nodes.append({'name': label, 'type': 'http', 'server': '127.0.0.1', 'port': server.server_address[1]})
        return server.label

    for labels, delays in (
        (('🇯🇵日本专线01|BGP|流媒体', '🇯🇵日本专线02|BGP|流媒体'), (.12, .04)),
        (('🇯🇵日本高速01|BGP|CUCM', '🇯🇵日本高速02|BGP|CUCM'), (.08, .02)),
        (('🇺🇸美国05|流媒体|0.1x', '🇺🇸美国06|流媒体|0.1x'), (.06, .01)),
        (('🇺🇸美国高速05|CTCU|0.1x', '🇺🇸美国高速06|CTCU|0.1x'), (.05, .005)),
    ):
        by_tier.append([add(label, delay) for label, delay in zip(labels, delays)])
    allowed = set(states)
    add('🇭🇰香港专线01|BGP|流媒体', 0)
    add('🇸🇬新加坡专线01|BGP|流媒体', 0)

    class Subscription(BaseHTTPRequestHandler):
        def do_GET(self):
            content = yaml.safe_dump({'proxies': nodes}, allow_unicode=True).encode()
            self.send_response(200)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        def log_message(self, *_):
            pass

    subscription = ThreadingHTTPServer(('127.0.0.1', 0), Subscription)
    threading.Thread(target=subscription.serve_forever, daemon=True).start()
    controller_address = f'127.0.0.1:{free_port()}'
    mixed = free_port()

    def api(method, path, body=None):
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(f'http://{controller_address}{path}', data=data, method=method)
        request.add_header('Authorization', 'Bearer ' + secret)
        if body is not None:
            request.add_header('Content-Type', 'application/json')
        with OPENER.open(request, timeout=5) as response:
            data = response.read()
            return json.loads(data) if data else None

    def group(name=GROUP):
        return api('GET', '/proxies/' + urllib.parse.quote(name))

    provider = copy.deepcopy(local['proxy-providers']['liangxinyun'])
    provider.update(copy.deepcopy(module['proxy-providers']['liangxinyun']))
    provider['url'] = f'http://127.0.0.1:{subscription.server_port}/subscription'
    provider['health-check'].update(url=TEST_URL, interval=1, timeout=300)
    groups = copy.deepcopy(module['proxy-groups!'])
    for item in groups:
        if 'url' in item:
            item.update(url=TEST_URL, interval=1, timeout=300)
    manual_nodes = []
    for node_name in ('TikTok-ISP-Local', '🇯🇵 日本Z04 | IEPL'):
        server = LocalProxy(('127.0.0.1', 0), Tunnel)
        server.label = 'SYNTHETIC-TIKTOK-PROBE'
        server.state = {'up': True, 'delay': .005}
        threading.Thread(target=server.serve_forever, daemon=True).start()
        servers.append(server)
        manual_nodes.append({'name': node_name, 'type': 'http',
                             'server': '127.0.0.1', 'port': server.server_address[1]})
    # This top-level leaf appears only in the default GLOBAL compatible provider.
    # None of the three configured groups match it, so zero CONNECTs demonstrates
    # GLOBAL does not independently schedule checks while other timers run.
    class SentinelTunnel(Tunnel):
        def do_CONNECT(self):
            self.server.calls += 1
            return super().do_CONNECT()
    global_sentinel = LocalProxy(('127.0.0.1', 0), SentinelTunnel)
    global_sentinel.label = 'GLOBAL-UNTESTED-SENTINEL'
    global_sentinel.state = {'up': True, 'delay': 0}
    global_sentinel.calls = 0
    threading.Thread(target=global_sentinel.serve_forever, daemon=True).start()
    servers.append(global_sentinel)
    manual_nodes.append({'name': 'GLOBAL-UNTESTED-SENTINEL', 'type': 'http',
                         'server': '127.0.0.1', 'port': global_sentinel.server_address[1]})
    config = {
        'mixed-port': mixed, 'bind-address': '127.0.0.1', 'allow-lan': False,
        'external-controller': controller_address, 'secret': secret,
        'log-level': 'warning', 'mode': 'rule', 'ipv6': False,
        'profile': {'store-selected': True},
        'proxies': manual_nodes,
        'proxy-providers': {'liangxinyun': provider}, 'proxy-groups': groups,
        'rules': ['MATCH,良心云-按档位自动切换'],
    }
    ruby_process = None

    def check_tiktok():
        proxies = api('GET', '/proxies')['proxies']
        actual_groups = {name for name, value in proxies.items() if 'all' in value}
        assert actual_groups == {'TIKTOK首跳', 'TIKTOK访问检测', GROUP, 'GLOBAL'}
        assert group()['type'] == 'Selector'
        assert group('GLOBAL')['type'] == 'Selector'
        assert all(item['name'] != 'GLOBAL' for item in groups)
        assert global_sentinel.calls == 0, 'GLOBAL unexpectedly generated a probe'
        assert group()['hidden'] is False
        assert group('TIKTOK首跳')['now'] == '🇯🇵 日本Z04 | IEPL'
        assert group('TIKTOK访问检测')['all'] == ['TikTok-ISP-Local']

    def native_probes():
        # No delay/healthcheck request here: only read histories produced by native timers.
        expected = {'TIKTOK首跳': '🇯🇵 日本Z04 | IEPL', 'TIKTOK访问检测': 'TikTok-ISP-Local'}
        initial = {}
        for group_name, node_name in expected.items():
            value = group(group_name)
            assert value['type'] == 'Selector' and value['now'] == node_name
            assert value['testUrl'] == TEST_URL
            configured = next(item for item in groups if item['name'] == group_name)
            assert configured['expected-status'] == 204
            initial[node_name] = None
        deadline = time.monotonic() + 10
        complete = set()
        while time.monotonic() < deadline:
            for node_name in expected.values():
                node = api('GET', '/proxies/' + urllib.parse.quote(node_name))
                history = node.get('extra', {}).get(TEST_URL, {}).get('history', [])
                recent = [row for row in history if row.get('delay', 0) > 0]
                if recent:
                    if initial[node_name] is None:
                        initial[node_name] = recent[-1]['time']
                    elif recent[-1]['time'] != initial[node_name]:
                        complete.add(node_name)
            if len(complete) == len(expected):
                break
            time.sleep(.1)
        assert len(complete) == len(expected), ('native timer failed', initial, complete)
        check_tiktok()
        results.append({'case': 'exactly-four-groups-and-global-has-no-independent-probes', 'passed': True})
        results.append({'case': 'tiktok-native-timers-refresh-without-auto-selection-or-api-probes', 'passed': True})
        assert set(group()['all']) == {'REJECT', *allowed}
        results.append({'case': 'single-visible-selector-exposes-all-filtered-leaves', 'passed': True})

    def settle(label, expected, timeout=15):
        start, since = time.monotonic(), None
        while time.monotonic() - start < timeout:
            assert ruby_process.poll() is None, 'controller exited unexpectedly'
            actual = group()['now']
            if actual == expected:
                since = since or time.monotonic()
                if time.monotonic() - since > .6:
                    check_tiktok()
                    status, marker = outgoing(mixed)
                    if expected == 'REJECT':
                        assert status == 0 or status >= 400, (status, marker)
                    else:
                        assert status == 200 and marker == expected, (label, status, marker)
                    result = {'case': label, 'passed': True, 'settledSeconds': round(time.monotonic()-start, 2), 'node': actual}
                    results.append(result)
                    print(json.dumps(result, ensure_ascii=False), flush=True)
                    return
            else:
                since = None
            time.sleep(.06)
        raise AssertionError((label, group()))

    try:
        with tempfile.TemporaryDirectory(prefix='lxy-strict-controller-') as temporary:
            home = Path(temporary)
            path = home / 'config.yaml'
            path.write_text(yaml.safe_dump(config, allow_unicode=True), encoding='utf-8')
            token = home / 'api-secret'
            token.write_text(secret, encoding='utf-8')
            token.chmod(0o600)
            core_command = [str(core), '-d', str(home), '-f', str(path)]
            syntax = subprocess.run([*core_command, '-t'], capture_output=True, text=True)
            assert syntax.returncode == 0, (syntax.stdout, syntax.stderr)
            with (home/'core.log').open('wb') as log, (home/'controller.log').open('wb') as controller_log:
                process = subprocess.Popen(core_command, stdout=log, stderr=subprocess.STDOUT)
                extension = 'lua' if args.lua else 'rb'
                environment = None
                if args.lua:
                    from lua_controller_fixture_runtime import install
                    environment = install(home, args.lua.resolve())
                command = [*ruby, str(directory/f'liangxinyun-controller.{extension}'), '--api-url', 'http://'+controller_address,
                           '--secret-file', str(token), '--test-url', TEST_URL, '--interval', '1', '--poll', '.15',
                           '--max-age', '3', '--state-file', str(home/'status.json'), '--lock-file', str(home/'lock')]
                try:
                    for _ in range(80):
                        try:
                            if set(group()['all']) == {'REJECT', *allowed}:
                                break
                        except OSError:
                            pass
                        time.sleep(.1)
                    else:
                        raise AssertionError('Mihomo/provider did not become ready')
                    api('PUT', '/proxies/'+urllib.parse.quote('TIKTOK首跳'), {'name': '🇯🇵 日本Z04 | IEPL'})
                    native_probes()
                    before = group()['now']
                    preflight = subprocess.run([*command, '--preflight'], capture_output=True, text=True, env=environment)
                    assert preflight.returncode == 0, preflight.stderr
                    assert json.loads(preflight.stdout)['readOnly'] is True
                    assert json.loads(preflight.stdout)['candidateCompatible'] is True
                    assert group()['now'] == before and not (home/'status.json').exists()
                    check_tiktok()
                    results.append({'case': 'preflight-read-only-no-selection-or-file-write', 'passed': True})
                    run_command = ['sh', str(directory/'liangxinyun-controller.run'), *command, '--run'] if args.lua else command
                    ruby_process = subprocess.Popen(run_command, stdout=controller_log, stderr=subprocess.STDOUT, env=environment)
                    settle('highest-tier-lowest-delay', by_tier[0][1])
                    assert secret not in ' '.join(command)
                    duplicate = subprocess.run([*command, '--once'], capture_output=True, text=True, env=environment)
                    assert duplicate.returncode == 1
                    assert ('another-controller-or-lock-unavailable' in duplicate.stdout if args.lua else
                            'another strict controller' in duplicate.stderr)
                    results.append({'case': 'single-instance-and-secret-out-of-argv', 'passed': True})

                    states[by_tier[0][1]]['up'] = False
                    start = time.monotonic()
                    seen = set()
                    while time.monotonic() - start < 4:
                        actual = group()['now']
                        seen.add(actual)
                        assert actual in {*by_tier[0], 'REJECT'}, ('premature downgrade', actual)
                        time.sleep(.04)
                    settle('partial-failure-stays-in-highest-tier', by_tier[0][0])
                    results[-1]['observedNodesDuringFailure'] = sorted(seen)
                    for rank in range(3):
                        for name in by_tier[rank]:
                            states[name]['up'] = False
                        settle(f'whole-tier-{rank+1}-downgrade', by_tier[rank+1][1])
                    for name in by_tier[3]:
                        states[name]['up'] = False
                    settle('all-tiers-failed-reject', 'REJECT')
                    states[by_tier[0][1]]['up'] = True
                    settle('automatic-top-tier-recovery', by_tier[0][1])
                    states[by_tier[0][0]].update(up=True, delay=.005)
                    states[by_tier[0][1]]['delay'] = .1
                    settle('same-tier-new-lowest-delay', by_tier[0][0])
                    for name in by_tier[1]:
                        states[name]['up'] = True
                    nodes[:] = [node for node in nodes if 'LXY: '+node['name'] not in by_tier[0]]
                    api('PUT', '/providers/proxies/liangxinyun')
                    settle('empty-top-tier-skipped', by_tier[1][1])
                    added = add('🇯🇵日本专线12|BGP|流媒体', .005)
                    api('PUT', '/providers/proxies/liangxinyun')
                    settle('subscription-new-node-return', added)
                    ruby_process.terminate()
                    ruby_process.wait(timeout=20)
                    assert ruby_process.returncode == 0
                    assert group()['now'] == 'REJECT'
                    check_tiktok()
                    contents = (home/'controller.log').read_text(encoding='utf-8')
                    assert secret not in contents
                    results.append({'case': 'graceful-stop-reject-no-tiktok-mutation-or-secret-log', 'passed': True})
                except Exception:
                    print((home/'controller.log').read_text(encoding='utf-8')[-6000:], flush=True)
                    print((home/'core.log').read_text(encoding='utf-8')[-4000:], flush=True)
                    raise
                finally:
                    if ruby_process and ruby_process.poll() is None:
                        ruby_process.terminate()
                        ruby_process.wait(timeout=20)
                    process.terminate()
                    process.wait(timeout=8)
    finally:
        subscription.shutdown()
        subscription.server_close()
        for server in servers:
            server.shutdown()
            server.server_close()

    report = {'passed': True, 'version': directory.name.removeprefix('v'), 'coreVersion': core_version,
              'runtimeVersion': ruby_version, 'luaNativeModulesSubstituted': bool(args.lua),
              'fixture': {'loopbackOnly': True, 'intervalSeconds': 1, 'timeoutMs': 300,
                          'targetRouterTested': False, 'productionTimingsTested': False}, 'cases': results}
    report['luaVersion' if args.lua else 'rubyVersion'] = ruby_version
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'PASS: {len(results)} strict-controller real-core fixture cases', flush=True)


if __name__ == '__main__':
    main()
