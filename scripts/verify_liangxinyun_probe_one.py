"""Test the single authorized probe using synthetic local HTTP only."""

import argparse
import copy
import json
from pathlib import Path
import shutil
from urllib.parse import quote

from verify_liangxinyun_readonly import Harness, GROUP_PATH, PROVIDER_PATH, URL, STAMP


NODE = "LXY: 🇯🇵日本专线01|BGP|流媒体"
PROBE = f"{PROVIDER_PATH}/{quote(NODE, safe='')}/healthcheck?url={quote(URL, safe='')}&timeout=5000&expected=204"
PATHS = ["/version", GROUP_PATH, PROVIDER_PATH, GROUP_PATH, PROBE, PROVIDER_PATH, GROUP_PATH]


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
        completed, requests = harness.run(data or fixture(), args=flags, **kwargs)
        report = json.loads(completed.stdout)
        assert report["selectionApplied"] is False and report["formalAcceptance"] is False
        actual = [request for request in requests if request[1] == PROBE]
        assert len(actual) == probes == report["probeRequests"]
        assert report["probeRequestAttempted"] is bool(probes)
        assert [r[1] for r in requests] == PATHS[:len(requests)]
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

    data = fixture(); data[1]["now"] = "LXY: 日本高速02"
    run(data, probes=0, error="current-selection-not-authorized-node")

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
    print(f"PASS real Lua 5.1/curl single-node probe fixture scenarios: {harness.cases}")


if __name__ == "__main__":
    main()
