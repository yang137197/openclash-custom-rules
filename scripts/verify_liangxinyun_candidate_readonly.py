"""Real Lua/curl read-only contract inspection against synthetic loopback HTTP."""
import argparse
import copy
import json
from pathlib import Path
import shutil
import subprocess

from verify_liangxinyun_readonly import Harness, fixture, PATHS, URL

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'scripts/liangxinyun_candidate_readonly.lua'
CANDIDATE = ROOT/'profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.1/liangxinyun-controller.lua'
READER = ROOT/'scripts/liangxinyun_readonly.lua'


def block(source, start, end):
    return source[source.index(start):source.index(end)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lua', type=Path, required=True)
    lua = parser.parse_args().lua.resolve(strict=True)
    source, candidate, reader = SCRIPT.read_text(), CANDIDATE.read_text(), READER.read_text()
    for start, end in (('local function has', '-- Parse Go/RFC3339'),
                       ('local function names', 'local function fail'),
                       ('-- Fail closed', 'function M.api')):
        assert block(candidate, start, end) in source, 'candidate contract drift'
    assert block(reader, 'function M.quote', 'local function arguments') in source, 'GET reader drift'
    assert '/healthcheck' not in source and '--request GET' in source
    subprocess.run([str(lua), str(SCRIPT.with_name('test_liangxinyun_candidate_readonly.lua')),
                    str(SCRIPT), str(CANDIDATE)], check=True)
    harness = Harness(lua, shutil.which('curl'), script=SCRIPT)

    def inspect(data, **kwargs):
        done, requests = harness.run(data, **kwargs)
        assert done.returncode == 0, done.stdout
        out = json.loads(done.stdout)
        assert [r[1] for r in requests] == PATHS and out['apiRequests']==4
        assert out['readOnly'] and not out['selectionApplied'] and not out['configurationWritten']
        assert out['probeRequests']==0 and not out['formalAcceptance']
        assert out['inspectionComplete'] and out['contractChecksAgree']
        return out

    data = fixture()
    out = inspect(data, stdin_script=True)
    assert not out['candidateCompatible'] and not out['checks']['rejectFirst']
    assert not out['checks']['testUrlMatches'] and not out['checks']['expectedStatusMatches']
    assert all(n['name'] not in json.dumps(out, ensure_ascii=False) for n in data[2]['proxies'])
    data[1]['all'].insert(0, 'REJECT'); data[3] = copy.deepcopy(data[1])
    data[2]['testUrl'], data[2]['expectedStatus'] = URL, '204'
    assert inspect(data)['candidateCompatible']
    data[2]['testUrl'] = 'https://custom.invalid/private-token'
    out = inspect(data)
    assert not out['candidateCompatible'] and 'private-token' not in json.dumps(out)
    for statuses, body in (([302], {}), ([401], {}), ([200], 'invalid-json')):
        done, requests = harness.run([body], statuses=statuses)
        out = json.loads(done.stdout)
        assert done.returncode==1 and len(requests)==1
        assert not out['inspectionComplete'] and out['apiRequests']==1
    done, requests = harness.run([], args=('--run',))
    assert done.returncode==1 and not requests
    done, requests = harness.run([], port_override='0')
    assert done.returncode==1 and not requests
    assert json.loads(done.stdout)['apiRequests']==0
    print(f'PASS: {harness.cases} actual Lua/curl candidate-readonly HTTP scenarios; native JSON/UCI substituted')


if __name__ == '__main__':
    main()
