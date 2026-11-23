"""Test the single authorized probe using synthetic local HTTP only."""

import argparse
import copy
import json
from pathlib import Path
import shutil
from urllib.parse import quote

from verify_liangxinyun_readonly import Harness, GROUP_PATH, PROVIDER_PATH, URL, STAMP


NODE = "LXY: 🇯🇵日本专线01|BGP|流媒体"
NODE_02 = "LXY: 🇯🇵日本专线02|BGP|流媒体"
PROBE = f"{PROVIDER_PATH}/{quote(NODE, safe='')}/healthcheck?url={quote(URL, safe='')}&timeout=5000&expected=204"
PATHS = ["/version", GROUP_PATH, PROVIDER_PATH, GROUP_PATH, PROBE, PROVIDER_PATH, GROUP_PATH]
PROBE_02 = f"{PROVIDER_PATH}/{quote(NODE_02, safe='')}/healthcheck?url={quote(URL, safe='')}&timeout=5000&expected=204"
PATHS_02 = ["/version", GROUP_PATH, PROVIDER_PATH, GROUP_PATH, PROBE_02, PROVIDER_PATH, GROUP_PATH]


def fixture(*, alive=True, delay=37):
    node = {"name": NODE, "extra": {}, "history": []}
    group = {"type": "Selector", "now": NODE, "all": [NODE, "LXY: 日本高速02"]}
    provider = {"name": "liangxinyun", "updatedAt": STAMP, "proxies": [node]}
    after = copy.deepcopy(provider)
    after["proxies"][0]["extra"][URL] = {
        "alive": alive, "history": [{"time": STAMP, "delay": delay if alive else 0}],
    }
    return [{"version": "alpha-gbc76c13"}, group, provider, copy.deepcopy(group),
            {"delay": delay}, after, copy.deepcopy(group)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lua", required=True, type=Path)
    args = parser.parse_args()
    lua = args.lua.resolve(strict=True)
    harness = Harness(lua, shutil.which("curl"), script=Path(__file__).with_name("liangxinyun_probe_one.lua"), paths=PATHS)

    def run(data=None, *, probes=1, error=None, flags=("--probe-once",), **kwargs):
        paths = PATHS_02 if flags == ("--probe-node-02-once",) else PATHS
        harness.paths = paths
        completed, requests = harness.run(data or fixture(), args=flags, **kwargs)
        report = json.loads(completed.stdout)
        assert report["selectionApplied"] is False and report["formalAcceptance"] is False
        actual = [request for request in requests if request[1] in (PROBE, PROBE_02)]
        assert len(actual) == probes == report["probeRequests"]
        assert not actual or actual[0][1] == paths[4]
        assert report["probeRequestAttempted"] is bool(probes)
        assert [r[1] for r in requests] == paths[:len(requests)]
        if flags == ("--inspect-only",) and not error:
            assert [r[1] for r in requests] == PATHS[:2]
        if error:
            assert completed.returncode == 1 and report["error"] == error, report
        else:
            assert completed.returncode == 0 and "error" not in report, report
        return report

    report = run(stdin_script=True)
    assert report["result"] == "healthy-for-requested-204" and report["urlDelayMs"] == 37
    assert report["recordAppearedAfterProbe"] is True and report["currentSelectionUnchanged"] is True
    assert report["providerUpdatedAtUnchanged"] is True

    for status in (503, 504):
        data = fixture(alive=False)
        data[4] = {"message": "synthetic detection failure"}
        report = run(data, statuses=[200, 200, 200, 200, status, 200, 200])
        assert report["result"] == "failed-for-requested-204" and report["urlDelayMs"] == 0
        assert "apiDelayMs" not in report

    # Target core may return API HTTP 200 despite an unexpected target status.
    report = run(fixture(alive=False))
    assert report["probeHttpStatus"] == 200 and report["result"] == "failed-for-requested-204"

    data = fixture(); data[5]["proxies"][0]["extra"] = {}
    report = run(data)
    assert report["result"] == "unknown" and not report["recordAppearedAfterProbe"]

    data = fixture(); data[6]["now"] = "LXY: 日本高速02"
    report = run(data)
    assert report["result"] == "unknown" and not report["currentSelectionUnchanged"]

    data = fixture(); data[5]["updatedAt"] = "2026-11-23T12:34:57Z"
    assert run(data)["result"] == "unknown"

    data = fixture()
    current = "LXY: 🇯🇵日本专线02|BGP|流媒体"
    for group in (data[1], data[3], data[6]):
        group["now"], group["all"] = current, [NODE, current]
    report = run(data)
    assert report["currentSelection"] == current and not report["authorizedNodeSelected"]
    assert report["authorizedNodeInGroup"] is True
    assert report["node"] == NODE and report["result"] == "healthy-for-requested-204"
    assert report["currentSelectionUnchanged"] is True

    data = fixture(); data[1]["all"].remove(NODE)
    run(data, probes=0, error="authorized-node-not-in-group")

    data = fixture(); data[3]["now"] = "LXY: 日本高速02"
    run(data, probes=0, error="selection-or-members-changed-before-probe")

    data = fixture(); data[3]["all"].append("LXY: 日本高速03")
    run(data, probes=0, error="selection-or-members-changed-before-probe")

    data = fixture(); data[2]["proxies"][0]["extra"] = copy.deepcopy(data[5]["proxies"][0]["extra"])
    run(data, probes=0, error="existing-test-history-no-repeat")

    data = fixture(); data[2]["proxies"][0]["extra"][URL] = {"alive": True, "history": []}
    run(data, probes=0, error="existing-test-state-no-repeat")

    data = fixture(); data[2]["proxies"] = []
    run(data, probes=0, error="target-not-in-provider")

    data = fixture(); data[0]["version"] = "different-core"
    run(data, probes=0, error="core-version-changed")

    run(flags=(), probes=0, error="arguments-invalid")
    run(probes=0, error="json-shape-incompatible", incompatible_codec=True)
    run(statuses=[401] * 7, probes=0, error="api-http-401")
    run(statuses=[200, 200, 200, 200, 302, 200, 200])

    report = run(flags=("--inspect-only",), probes=0, stdin_script=True)
    assert report["readOnly"] is True and report["mode"] == "selection-inspection"
    assert report["inspectionComplete"] is True and report["authorizedNodeSelected"] is True
    assert report["currentSelectionUtf8Hex"] == NODE.encode().hex()

    data = fixture(); data[1]["now"] = "LXY: 日本高速02"
    report = run(data, flags=("--inspect-only",), probes=0)
    assert report["authorizedNodeSelected"] is False and report["authorizedNodeInGroup"] is True

    data = fixture(); data[1]["all"].remove(NODE)
    report = run(data, flags=("--inspect-only",), probes=0)
    assert report["authorizedNodeSelected"] is True and report["authorizedNodeInGroup"] is False

    data = fixture(); data[1]["now"] = NODE + " "
    report = run(data, flags=("--inspect-only",), probes=0)
    assert report["authorizedNodeSelected"] is False
    assert report["currentSelectionUtf8Hex"] == (NODE + " ").encode().hex()

    def fixture_02(*, alive=True):
        data = fixture()
        # Node 01's earlier failure stays present; only node 02 may be probed.
        failed_01 = {"name": NODE, "extra": {URL: {"alive": False,
                     "history": [{"time": STAMP, "delay": 0}]}}, "history": []}
        empty_02 = {"name": NODE_02, "extra": {}, "history": []}
        measured_02 = copy.deepcopy(empty_02)
        measured_02["extra"][URL] = {"alive": alive,
            "history": [{"time": STAMP, "delay": 37 if alive else 0}]}
        data[2]["proxies"] = [copy.deepcopy(failed_01), empty_02]
        data[5]["proxies"] = [copy.deepcopy(failed_01), measured_02]
        for group in (data[1], data[3], data[6]):
            group["now"], group["all"] = NODE_02, [NODE, NODE_02]
        return data

    report = run(fixture_02(), flags=("--probe-node-02-once",), stdin_script=True)
    assert report["node"] == NODE_02 and report["result"] == "healthy-for-requested-204"
    assert report["currentSelection"] == NODE_02 and report["currentSelectionUnchanged"] is True

    data = fixture_02(alive=False); data[4] = {"message": "synthetic request timeout"}
    report = run(data, flags=("--probe-node-02-once",), statuses=[200, 200, 200, 200, 504, 200, 200])
    assert report["node"] == NODE_02 and report["result"] == "failed-for-requested-204"

    data = fixture_02()
    data[2]["proxies"][1]["extra"] = copy.deepcopy(data[5]["proxies"][1]["extra"])
    run(data, flags=("--probe-node-02-once",), probes=0, error="existing-test-history-no-repeat")

    data = fixture_02(); data[2]["proxies"].pop()
    run(data, flags=("--probe-node-02-once",), probes=0, error="target-not-in-provider")
    print(f"PASS real Lua 5.1/curl single-node probe fixture scenarios: {harness.cases}")


if __name__ == "__main__":
    main()
