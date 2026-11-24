"""Actual shell/Lua worker regression; native Lua-driver process calls are substituted separately."""
import argparse
import os
from pathlib import Path
import secrets
import signal
import subprocess
import tempfile
import time
import shutil

from lua_controller_fixture_runtime import install
from verify_liangxinyun_readonly import lua_string, lua_value

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT/'scripts/liangxinyun_supervisor_offline.lua'
CANDIDATE = ROOT/'profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.1/liangxinyun-controller.run'


def extract(lua, field):
    code = f"local m=assert(loadfile({lua_string(str(MODULE))}))('__library_only'); io.write(m.{field})"
    return subprocess.check_output([str(lua), '-'], input=code.encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lua', type=Path, required=True)
    lua = parser.parse_args().lua.resolve(strict=True)
    subprocess.run([str(lua), str(MODULE.with_name('test_liangxinyun_supervisor_offline.lua')), str(MODULE)], check=True)
    source, worker = extract(lua, 'SUPERVISOR_SOURCE'), extract(lua, 'WORKER_SOURCE')
    assert source == CANDIDATE.read_bytes(), 'embedded supervisor differs from candidate'
    cases = 1
    with tempfile.TemporaryDirectory(prefix='lxy-supervisor-runtime-') as directory:
        env = install(Path(directory), lua)
        for label, fault in (('immediate', None), ('delayed', None), ('delayed', 'marker'),
                             ('delayed', 'status'), ('delayed', 'early-stop')):
            root = Path('/tmp')/('liangxinyun-supervisor-'+secrets.token_hex(8))
            root.mkdir(mode=0o700)
            process = None
            marker = None
            try:
                current = source
                if fault == 'marker':
                    current = current.replace(b"trap 'rm -f \"$stop_file\"' EXIT", b': # intentionally omit cleanup')
                elif fault == 'status':
                    current = current.replace(b'exit "$result"', b'exit 7')
                elif fault == 'early-stop':
                    current = current.replace(b'trap request_stop TERM INT', b"trap 'exit 0' TERM INT")
                (root/'supervisor.run').write_bytes(current)
                (root/'worker.lua').write_bytes(worker)
                def guard():
                    if Path(f'/tmp/liangxinyun-stop.{os.getpid()}').exists():
                        os._exit(125)
                with (root/'test.log').open('wb') as log:
                    process = subprocess.Popen(['/bin/sh', str(root/'supervisor.run'), str(lua), str(root/'worker.lua'),
                                                str(root), label], env=env, stdout=log, stderr=subprocess.STDOUT,
                                               preexec_fn=guard, start_new_session=True)
                    marker = Path(f'/tmp/liangxinyun-stop.{process.pid}')
                    ready = root/(label+'-ready')
                    deadline = time.monotonic()+5
                    ready_fields = []
                    while process.poll() is None and time.monotonic()<deadline:
                        ready_fields = ready.read_text().split() if ready.exists() else []
                        if len(ready_fields)==2 and all(value.isdigit() for value in ready_fields):
                            break
                        time.sleep(.01)
                    assert len(ready_fields)==2, (fault, (root/'test.log').read_text())
                    worker_pid, parent = map(int, ready_fields)
                    assert parent == process.pid
                    process.send_signal(signal.SIGTERM)
                    code = process.wait(timeout=5)
                    deadline = time.monotonic()+3
                    while Path(f'/proc/{worker_pid}').exists() and time.monotonic()<deadline:
                        time.sleep(.03)
                    done = root/(label+'-done')
                    row = dict(supervisorReaped=True, supervisorExitCode=code,
                               workerStoppedCleanly=done.exists() and done.read_text()==f'stopped-and-cleaned {worker_pid}\n',
                               workerGone=not Path(f'/proc/{worker_pid}').exists(),
                               workerTemporaryCleaned=not (root/(label+'-work')).exists(),
                               stopMarkerRemoved=not marker.exists())
                    if fault == 'marker':
                        assert code==0 and row['workerStoppedCleanly'] and row['workerGone']
                        assert not row['stopMarkerRemoved']
                    elif fault == 'status':
                        assert code==7 and row['workerStoppedCleanly'] and row['workerGone']
                        assert row['stopMarkerRemoved'] and row['workerTemporaryCleaned']
                    elif fault == 'early-stop':
                        assert not row['workerStoppedCleanly'] and row['workerGone']
                    check = f"local m=assert(loadfile({lua_string(str(MODULE))}))('__library_only'); print(m.evaluate({lua_value(row)}))"
                    passed = subprocess.check_output([str(lua), '-'], input=check.encode()).strip()==b'true'
                    assert passed is (fault is None), (label, fault, row)
                    cases += 1
                    print(f'PASS actual shell/{label}/{fault or "normal-stop"}', flush=True)
            finally:
                if process and process.poll() is None:
                    # This session/process group was created solely for this fixture.
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=5)
                if marker and marker.exists():
                    marker.unlink()
                assert root.resolve().parent == Path('/tmp') and root.name.startswith('liangxinyun-supervisor-')
                shutil.rmtree(root)
        for status in (0, 7):
            command = ['/bin/sh', str(CANDIDATE), '/bin/sh', '-c', f'exit {status}']
            assert subprocess.run(command, capture_output=True, timeout=5).returncode == status
            cases += 1
    print(f'PASS: {cases} shell/worker/source regression scenarios; target CatWrt driver not tested')


if __name__ == '__main__':
    main()
