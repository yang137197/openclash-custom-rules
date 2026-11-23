"""Exercise the read-only tool with real Lua 5.1/curl and a local HTTP fixture.

The fixture substitutes UCI, the clock and the JSON codec; it does not emulate
the router's luCI C modules. No router, subscription or actual credentials used.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


SCRIPT = Path(__file__).with_name("liangxinyun_readonly.lua").resolve()
GROUP_PATH = "/proxies/%E8%89%AF%E5%BF%83%E4%BA%91"
PROVIDER_PATH = "/providers/proxies/liangxinyun"
PATHS = ["/version", GROUP_PATH, PROVIDER_PATH, GROUP_PATH]
URL = "https://www.gstatic.com/generate_204"
STAMP = "2026-11-23T12:34:56Z"
NOW = 1795437296
FAKE_SECRET = 'synthetic-only-quote"-slash\\-single\'-dollar$-percent%'
CODEC_SAMPLE = r'{"extra":{"https:\/\/www.gstatic.com\/generate_204":{"alive":true,"history":[{"delay":7}]}}}'


def lua_string(value: str) -> str:
    marker = "="
    while "]" + marker + "]" in value:
        marker += "="
    # Prefix ensures Lua's long-string leading-newline rule cannot alter data.
    return "(" + "[" + marker + "[x" + value + "]" + marker + "]):sub(2)"


def lua_value(value) -> str:
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return lua_string(value)
    if isinstance(value, list):
        return "{" + ",".join(lua_value(item) for item in value) + "}"
    return "{" + ",".join(
        f"[{lua_string(key)}]={lua_value(item)}" for key, item in value.items()
    ) + "}"


JSON_ENCODER = r'''
local function quoted(s)
  return '"' .. s:gsub('[%c\\"]', function(c)
    if c == '"' then return '\\"' end
    if c == '\\' then return '\\\\' end
    return string.format('\\u%04x', string.byte(c))
  end) .. '"'
end
local function encode(v)
  local t = type(v)
  if t == 'string' then return quoted(v) end
  if t == 'number' or t == 'boolean' then return tostring(v) end
  if t == 'nil' then return 'null' end
  assert(t == 'table')
  local parts, size, array = {}, 0, #v > 0
  for k in pairs(v) do
    size = size + 1
    if type(k) ~= 'number' or k < 1 or k > #v or k % 1 ~= 0 then array = false end
  end
  if size ~= #v then array = false end
  if array then
    for _, item in ipairs(v) do parts[#parts + 1] = encode(item) end
    return '[' .. table.concat(parts, ',') .. ']'
  end
  for k, item in pairs(v) do parts[#parts + 1] = quoted(k) .. ':' .. encode(item) end
  return '{' .. table.concat(parts, ',') .. '}'
end
'''


def fixture():
    nodes = []
    for tier in ("日本专线", "日本高速", "US美国", "美国高速"):
        for i in (1, 2):
            name = f"LXY: {tier}{i:02d}|" + ("流媒体|0.1x" if tier == "US美国" else "BGP")
            nodes.append({"name": name, "extra": {URL: {
                "alive": True, "history": [{"delay": 50 - i, "time": STAMP}],
            }}})
    group = {"type": "Selector", "now": nodes[0]["name"], "all": [n["name"] for n in nodes]}
    provider = {"name": "liangxinyun", "testUrl": "", "expectedStatus": "", "proxies": nodes}
    return [{"version": "synthetic-core"}, group, provider, copy.deepcopy(group)]


class Harness:
    def __init__(self, lua: Path, curl: str, *, script: Path = SCRIPT, paths=None):
        self.lua, self.curl = lua, curl
        self.script, self.paths = script, PATHS if paths is None else paths
        self.cases = 0

    def run(self, responses, *, statuses=None, args=(), port_override=None, stdin_script=False,
            incompatible_codec=False):
        requests = []
        failures = []
        statuses = statuses or [200] * len(responses)
        bodies = [item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
                  for item in responses]
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_GET(self):
                index = len(requests)
                requests.append((self.command, self.path, self.headers.get("Authorization")))
                try:
                    assert index < len(responses), "unexpected additional request"
                    assert self.path == owner.paths[index], "unexpected API path"
                    assert self.headers.get("Authorization") == "Bearer " + FAKE_SECRET, "auth mismatch"
                except AssertionError as exc:
                    failures.append(str(exc))
                if index >= len(responses):
                    self.send_response(500)
                    self.end_headers()
                    return
                self.send_response(statuses[index])
                if statuses[index] == 302:
                    self.send_header("Location", "/forbidden-redirect")
                self.send_header("Content-Type", "application/json")
                encoded = bodies[index].encode()
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def refuse(self):
                failures.append("write request: " + self.command)
                self.send_response(405)
                self.end_headers()

            do_PUT = do_POST = do_PATCH = do_DELETE = refuse

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory(prefix="liangxinyun-readonly-") as directory:
                root = Path(directory)
                modules, bin_dir = root / "modules", root / "bin"
                (modules / "luci/model").mkdir(parents=True)
                bin_dir.mkdir()
                (bin_dir / "lua").symlink_to(self.lua)
                (root / "fixture-secret").write_text(FAKE_SECRET)
                (modules / "luci/model/uci.lua").write_text('''
return {cursor=function() return {get=function(_, package, section, key)
  assert(package == "openclash" and section == "config")
  if key == "cn_port" then return os.getenv("LXY_FIXTURE_PORT") end
  assert(key == "dashboard_password")
  local file = assert(io.open(os.getenv("LXY_FIXTURE_SECRET"), "r"))
  local secret = file:read("*a"); file:close(); return secret
end} end}
''')
                (modules / "nixio.lua").write_text(f"return {{gettimeofday=function() return {NOW},0 end}}")
                mapping = {body: item for body, item in zip(bodies, responses)
                           if not isinstance(item, str)}
                if not incompatible_codec:
                    mapping[CODEC_SAMPLE] = json.loads(CODEC_SAMPLE)
                (modules / "luci/jsonc.lua").write_text(
                    "local known=" + lua_value(mapping) + "\n" + JSON_ENCODER +
                    "\nreturn {parse=function(body) return known[body] end, stringify=encode}\n")
                # Log argv, then exec real curl. Authorization must arrive via stdin.
                (bin_dir / "curl").write_text(
                    "#!/usr/bin/python3\nimport json,os,sys\n"
                    "with open(os.environ['LXY_FIXTURE_ARGV'], 'a') as f: "
                    "f.write(json.dumps(sys.argv[1:])+'\\n')\n"
                    f"os.execv({owner.curl!r}, [{owner.curl!r}, *sys.argv[1:]])\n")
                (bin_dir / "curl").chmod(0o700)
                env = os.environ.copy()
                env.update({
                    "PATH": str(bin_dir) + os.pathsep + env["PATH"],
                    "LUA_PATH": str(modules / "?.lua"),
                    "LXY_FIXTURE_SECRET": str(root / "fixture-secret"),
                    "LXY_FIXTURE_PORT": str(port_override or server.server_port),
                    "LXY_FIXTURE_ARGV": str(root / "curl-argv"),
                    "http_proxy": "http://127.0.0.1:1", "all_proxy": "http://127.0.0.1:1",
                })
                completed = subprocess.run(
                    [str(self.lua), "-" if stdin_script else str(self.script), *args], env=env,
                    input=self.script.read_text() if stdin_script else None,
                    text=True, capture_output=True, timeout=45)
                assert FAKE_SECRET not in completed.stdout + completed.stderr, "secret in output"
                assert not completed.stderr, "unexpected stderr: " + completed.stderr
                argv_file = root / "curl-argv"
                curl_args = [json.loads(line) for line in argv_file.read_text().splitlines()] if argv_file.exists() else []
                for argv in curl_args:
                    assert FAKE_SECRET not in repr(argv), "secret in curl argv"
                    assert argv[0] == "-q" and argv[1:3] == ["--config", "-"], "curl config isolation"
                    assert argv[argv.index("--request") + 1] == "GET", "write method"
                    assert argv[argv.index("--url") + 1].startswith("http://127.0.0.1:"), "non-loopback target"
                assert not failures, failures
                assert len(curl_args) == len(requests), "unexpected transport activity"
                self.cases += 1
                return completed, requests
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lua", required=True, type=Path, help="real Lua 5.1 binary, not installed by this test")
    args = parser.parse_args()
    lua = args.lua.resolve(strict=True)
    version = subprocess.run([str(lua), "-v"], text=True, capture_output=True, check=True)
    assert "Lua 5.1" in version.stdout + version.stderr, "Lua 5.1 required"
    curl = shutil.which("curl")
    assert curl, "existing curl required"
    subprocess.run([str(lua), str(SCRIPT.with_name("test_liangxinyun_readonly.lua")), str(SCRIPT)], check=True)
    harness = Harness(lua, curl)

    def simulate(responses, **kwargs):
        completed, requests = harness.run(responses, **kwargs)
        assert completed.returncode == 0, completed.stdout
        report = json.loads(completed.stdout)
        assert report["readOnly"] is True and report["selectionApplied"] is False
        assert report["formalAcceptance"] is False
        assert report["jsonUrlArraySelfTest"] is True
        assert [r[1] for r in requests] == PATHS
        return report

    data = fixture()
    report = simulate(data, stdin_script=True)
    assert report["recommendation"]["wouldSelect"] == data[2]["proxies"][1]["name"]
    assert report["currentSelection"] == data[1]["now"]
    assert report["providerHealthContractMatches"] is False and report["warning"]
    assert report["historyDiagnostics"]["eligibleNodes"]["nodesWithAnyExtraHistory"] == 8

    data = fixture()
    data[2]["testUrl"], data[2]["expectedStatus"] = URL, "204"
    assert simulate(data)["providerHealthContractMatches"] is True

    data = fixture()
    data[2]["proxies"][1]["extra"] = {}
    assert simulate(data)["recommendation"]["wouldSelect"] == data[2]["proxies"][0]["name"]

    data = fixture()
    for node in data[2]["proxies"][:2]:
        node["extra"][URL] = {"alive": False, "history": [{"time": STAMP, "delay": 0}]}
    assert simulate(data)["recommendation"]["wouldSelect"] == data[2]["proxies"][3]["name"]

    data = fixture()
    for node in data[2]["proxies"][:2]:
        node["extra"][URL]["history"][0]["time"] = "2026-11-23T12:00:00Z"
    report = simulate(data)
    assert report["recommendation"]["wouldSelect"] == "REJECT"
    assert report["recommendation"]["reason"] == "higher-tier-measurements-unknown"

    data = fixture()
    for node in data[2]["proxies"]:
        node["extra"][URL] = {"alive": False, "history": [{"time": STAMP, "delay": 0}]}
    assert simulate(data)["recommendation"]["reason"] == "all-tiers-failed-or-empty"

    data = fixture()
    private_url = "https://fixture.invalid/?token=synthetic-only"
    for node in data[2]["proxies"]:
        node["extra"] = {private_url: node["extra"][URL]}
    report = simulate(data, args=("--test-url", private_url))
    assert report["recommendation"]["wouldSelect"] == data[2]["proxies"][1]["name"]
    assert private_url not in json.dumps(report)

    for status in (401, 302):
        completed, requests = harness.run(fixture(), statuses=[status, 200, 200, 200])
        assert completed.returncode == 1 and len(requests) == 1
        assert json.loads(completed.stdout)["error"] == f"api-http-{status}"

    data = fixture(); data[2] = "not-json"
    completed, requests = harness.run(data)
    assert completed.returncode == 1 and len(requests) == 3
    assert json.loads(completed.stdout)["error"] == "api-json-invalid"

    data = fixture(); data[3]["now"] = data[3]["all"][1]
    completed, requests = harness.run(data)
    assert completed.returncode == 1 and len(requests) == 4
    assert json.loads(completed.stdout)["error"] == "snapshot-selection-changed-or-invalid"

    data = fixture(); data[3]["all"].pop()
    completed, requests = harness.run(data)
    assert completed.returncode == 1 and len(requests) == 4
    assert json.loads(completed.stdout)["error"] == "snapshot-members-changed"

    completed, requests = harness.run(fixture(), port_override="9090;echo fixture")
    assert completed.returncode == 1 and not requests
    assert json.loads(completed.stdout)["error"] == "api-port-invalid"

    completed, requests = harness.run(fixture(), args=("--apply",))
    assert completed.returncode == 2 and not requests and completed.stdout.strip() == "arguments-invalid"

    # Same visible shape as the user's latest result: 21 eligible, 24 ignored,
    # no URL history. This is unknown data, never an all-nodes-failed verdict.
    data = fixture()
    nodes = data[2]["proxies"]
    for i, count in enumerate((4, 5, 7, 5)):
        prototype = copy.deepcopy(nodes[i * 2])
        for j in range(count - 2):
            added = copy.deepcopy(prototype)
            added["name"] += f"|fixture-extra-{j}"
            nodes.append(added)
    for i in range(24):
        nodes.append({"name": f"LXY: 新加坡专线{i:02d}", "extra": {URL: {
            "alive": True, "history": [{"time": STAMP, "delay": 1}],
        }}})
    for node in nodes[:21]:
        node["extra"] = {}
        node["history"] = [{"time": STAMP, "delay": 1}]
    data[1]["all"] = [node["name"] for node in nodes]
    data[3] = copy.deepcopy(data[1])
    report = simulate(data)
    assert [row["total"] for row in report["recommendation"]["tiers"]] == [4, 5, 7, 5]
    assert report["recommendation"]["ignoredProviderNodes"] == 24
    assert report["recommendation"]["wouldSelect"] == "REJECT"
    assert report["recommendation"]["reason"] == "higher-tier-measurements-unknown"
    assert not report["observedTestUrls"]
    stats = report["historyDiagnostics"]
    assert stats["eligibleNodes"]["extraEmptyNodes"] == 21
    assert stats["eligibleNodes"]["nodesWithGlobalHistory"] == 21
    assert stats["allProvider"]["nodesWithAnyExtraHistory"] == 24

    completed, requests = harness.run(fixture(), incompatible_codec=True)
    assert completed.returncode == 1 and not requests
    assert json.loads(completed.stdout)["error"] == "api-json-shape-incompatible"
    print(f"PASS real Lua 5.1/curl HTTP fixture scenarios: {harness.cases}")


if __name__ == "__main__":
    main()
