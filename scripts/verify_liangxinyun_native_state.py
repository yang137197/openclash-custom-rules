"""Real Lua/POSIX state-file smoke; LuCI JSON/nixio are substituted, never a router test."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

from lua_controller_fixture_runtime import install

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/liangxinyun_native_state.lua'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lua', type=Path, required=True)
    lua = parser.parse_args().lua.resolve(strict=True)
    subprocess.run([str(lua), str(SCRIPT.with_name('test_liangxinyun_native_state.lua')), str(SCRIPT)], check=True)
    with tempfile.TemporaryDirectory(prefix='lxy-native-state-fixture-') as directory:
        home = Path(directory)
        env = install(home, lua)
        before = set(Path('/tmp').glob('liangxinyun-state-*'))
        for flags in ([], ['--inspect-only'], ['--test-once'], ['--bad-argument']):
            completed = subprocess.run([str(lua), '-', *flags], input=SCRIPT.read_text(), env=env,
                                       capture_output=True, text=True, timeout=20)
            expected = 1 if flags == ['--bad-argument'] else 0
            assert completed.returncode == expected, (flags, completed.stdout, completed.stderr)
            assert not completed.stderr, completed.stderr
            value = json.loads(completed.stdout)
            assert value['apiRequests'] == value['probeRequests'] == 0
            assert value['selectionApplied'] is value['formalAcceptance'] is False
            if flags == ['--test-once']:
                for field in ('stateFileTestPassed', 'stateWriteReadback', 'replacementReadback',
                              'cleanupComplete', 'oldOpenFilePreserved', 'exclusiveCreateRespected'):
                    assert value[field] is True, (field, value)
                assert value['stateFileMode'] == 'rw-------'
                assert value['readOnly'] is False
            else:
                assert value['readOnly'] is True
            assert set(Path('/tmp').glob('liangxinyun-state-*')) == before, 'temporary path left behind'
        # This fixture used to accept all permission arguments and hid the defect.
        script = '''local nx=require 'nixio'
local p=assert(arg[1])
assert(not pcall(nx.open,p..'/invalid',nx.open_flags('creat','excl','wronly'),384))
assert(io.open(p..'/invalid','r')==nil)
for i,mode in ipairs({'rw-------',600}) do
 local f=assert(nx.open(p..'/valid'..i,nx.open_flags('creat','excl','wronly'),mode))
 assert(f:close())
end
'''
        completed = subprocess.run([str(lua), '-', str(home)], env=env, input=script,
                                   capture_output=True, text=True, timeout=10)
        assert completed.returncode == 0, completed.stderr
        for i in (1, 2):
            assert (home/f'valid{i}').stat().st_mode & 0o777 == 0o600
        original = ROOT / 'profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.0/liangxinyun-controller.lua'
        token = home/'empty-secret'
        token.write_text('')
        completed = subprocess.run([str(lua), str(original), '--once', '--api-url', 'http://127.0.0.1:1',
                                   '--secret-file', str(token), '--lock-file', str(home/'old-lock')],
                                  env=env, capture_output=True, text=True, timeout=10)
        assert completed.returncode == 1
        assert json.loads(completed.stdout)['error'] == 'nixio-mode-invalid'
        assert not (home/'old-lock').exists()
    print('PASS: 6 Lua/POSIX state and permission regression scenarios (native modules substituted)')


if __name__ == '__main__':
    main()
