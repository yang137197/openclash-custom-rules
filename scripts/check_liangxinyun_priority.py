#!/usr/bin/env python3
"""Exercise the candidate's actual groups with a caller-supplied Mihomo binary.

All subscription, proxy and destination responses are synthetic and local.
Only health-check URL/timing and fixture transport are substituted. This is
opt-in, not a network test against the user's subscription or router.
"""

import argparse
import copy
import http.client
import json
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

from strict_yaml import load_yaml


ROOT = Path(__file__).resolve().parents[1]
PROFILE = "tiktok-router-loongproxy-jp-us-liangxinyun"
CATEGORIES = ("日本专线", "日本高速", "美国流媒体", "美国高速")
TIERS = ["良心云-" + category for category in CATEGORIES]
TEST_URL = "http://fixture.test/generate_204"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class LocalProxy(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    block_on_close = False


class Tunnel(socketserver.StreamRequestHandler):
    def handle(self):
        self.connection.settimeout(3)
        try:
            line = self.rfile.readline(8192)
            if not line.startswith(b"CONNECT "):
                return
            while self.rfile.readline(8192) not in (b"\r\n", b"\n", b""):
                pass
            self.wfile.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            self.wfile.flush()
            line = self.rfile.readline(8192)
            while self.rfile.readline(8192) not in (b"\r\n", b"\n", b""):
                pass
            state = self.server.state.copy()
            if not state["up"]:
                # Greater than the 300 ms fixture timeout: a real probe timeout.
                time.sleep(.8)
                return
            time.sleep(state["delay"])
            body = self.server.label.encode("utf-8")
            if line.startswith(b"HEAD "):
                self.wfile.write(b"HTTP/1.1 204 No Content\r\nConnection: close\r\n\r\n")
            else:
                self.wfile.write(b"HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Length: "
                                 + str(len(body)).encode() + b"\r\n\r\n" + body)
            self.wfile.flush()
        except (OSError, ValueError):
            pass


def api(controller, method, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(f"http://{controller}{path}", data=data, method=method)
    if data is not None:
        request.add_header("Content-Type", "application/json")
    with OPENER.open(request, timeout=3) as response:
        content = response.read()
        return json.loads(content) if content else None


def outgoing(port):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        connection.request("GET", "http://fixture.test/probe")
        response = connection.getresponse()
        return response.status, response.read().decode("utf-8", errors="replace")
    except OSError:
        return 0, "connection-failed"
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    core = args.core.resolve(strict=True)
    entry = json.loads((ROOT / "profiles/catalog.json").read_text(encoding="utf-8"))["profiles"][PROFILE]["versions"]["1.6.0"]
    module = load_yaml((ROOT / entry["modulePath"]).read_text(encoding="utf-8"), module=True)
    local = load_yaml((ROOT / entry["localModuleTemplatePath"]).read_text(encoding="utf-8"), module=True)
    version = subprocess.check_output([str(core), "-v"], text=True, encoding="utf-8").strip()
    servers = []
    nodes = []
    states = {}
    by_tier = []
    results = []

    def add_node(label, delay):
        server = LocalProxy(("127.0.0.1", 0), Tunnel)
        server.label = "LXY: " + label
        server.state = {"up": True, "delay": delay}
        states[server.label] = server.state
        threading.Thread(target=server.serve_forever, daemon=True).start()
        servers.append(server)
        node = {"name": label, "type": "http", "server": "127.0.0.1", "port": server.server_address[1]}
        nodes.append(node)
        return server.label

    for labels, delays in (
        (("🇯🇵日本专线01|BGP|流媒体", "🇯🇵日本专线02|BGP|流媒体"), (.12, .04)),
        (("🇯🇵日本高速01|BGP|CUCM", "🇯🇵日本高速02|BGP|CUCM"), (.08, .02)),
        (("🇺🇸美国05|流媒体|0.1x", "🇺🇸美国06|流媒体|0.1x"), (.06, .01)),
        (("🇺🇸美国高速05|CTCU|0.1x", "🇺🇸美国高速06|CTCU|0.1x"), (.05, .005)),
    ):
        by_tier.append([add_node(label, delay) for label, delay in zip(labels, delays)])
    allowed = set(states)
    for label in ("🇭🇰香港专线01|BGP|流媒体", "🇸🇬新加坡专线01|BGP|流媒体", "美国普通01|BGP"):
        add_node(label, 0)

    class Subscription(BaseHTTPRequestHandler):
        def do_GET(self):
            content = yaml.safe_dump({"proxies": nodes}, allow_unicode=True).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, *_):
            pass

    subscription = ThreadingHTTPServer(("127.0.0.1", 0), Subscription)
    threading.Thread(target=subscription.serve_forever, daemon=True).start()
    controller = f"127.0.0.1:{free_port()}"
    mixed = free_port()
    provider = copy.deepcopy(local["proxy-providers"]["liangxinyun"])
    provider.update(copy.deepcopy(module["proxy-providers"]["liangxinyun"]))
    provider["url"] = f"http://127.0.0.1:{subscription.server_port}/subscription"
    check = provider["health-check"]
    check.update(url=TEST_URL, interval=1, timeout=300)
    groups = copy.deepcopy(module["proxy-groups!"])
    for group in groups:
        if "url" in group:
            group.update(url=TEST_URL, interval=1, timeout=300)
    config = {
        "mixed-port": mixed, "bind-address": "127.0.0.1", "allow-lan": False,
        "external-controller": controller, "log-level": "warning", "mode": "rule", "ipv6": False,
        "profile": {"store-selected": True},
        "proxies": [{"name": name, "type": "socks5", "server": "127.0.0.1", "port": 9}
                    for name in ("TikTok-ISP-Local", "🇯🇵 日本Z04 | IEPL")],
        "proxy-providers": {"liangxinyun": provider}, "proxy-groups": groups,
        "rules": ["MATCH,良心云"],
    }

    def snapshot():
        return api(controller, "GET", "/proxies")["proxies"]

    def settle(label, tier, leaf=None, membership=None, timeout=25):
        start = time.monotonic()
        good_since = None
        seen = set()
        transitions = []
        counterexample = None
        last = None
        while time.monotonic() - start < timeout:
            try:
                last = snapshot()
                current = last["良心云"]["now"]
                seen.add(current)
                if not transitions or transitions[-1]["tier"] != current:
                    transitions.append({"tier": current, "afterSeconds": round(time.monotonic() - start, 2)})
                if label == "one-node-timeout-stays-in-tier" and current != tier and counterexample is None:
                    imported = api(controller, "GET", "/providers/proxies/liangxinyun")["proxies"]
                    healthy = next((p for p in imported if p["name"] == leaf), {})
                    status, actual = outgoing(mixed)
                    if healthy.get("alive") and status == 200 and actual != leaf:
                        counterexample = {"healthyHigherTierNode": leaf, "providerAlive": True,
                                          "actualLowerTierEgress": actual, "httpStatus": status}
                matched = current == tier
                if leaf is not None:
                    matched &= last[tier]["now"] == leaf
                if membership is not None:
                    matched &= set(last[tier]["all"]) == set(membership)
                if matched:
                    if good_since is None:
                        good_since = time.monotonic()
                    if time.monotonic() - good_since >= 1.2:
                        status, actual = outgoing(mixed)
                        assert status == 200 and actual == last[tier]["now"], (label, status, actual)
                        result = {"case": label, "passed": True, "settledSeconds": round(time.monotonic() - start, 2),
                                  "tier": tier, "node": actual, "observedTiers": sorted(seen), "transitions": transitions}
                        if label == "one-node-timeout-stays-in-tier":
                            result["passed"] = seen == {tier}
                            result["eventualRecoveryPassed"] = True
                            result["counterexample"] = counterexample
                        results.append(result)
                        print(json.dumps(result, ensure_ascii=False), flush=True)
                        return last
                else:
                    good_since = None
            except (OSError, KeyError):
                pass
            time.sleep(.15)
        raise AssertionError((label, {key: last.get(key) for key in ["良心云", *TIERS]} if last else None))

    try:
        with tempfile.TemporaryDirectory(prefix="openclash-lxy-priority-") as directory:
            home = Path(directory)
            path = home / "config.yaml"
            path.write_text(yaml.safe_dump(config, allow_unicode=True), encoding="utf-8")
            command = [str(core), "-d", str(home), "-f", str(path)]
            checked = subprocess.run([*command, "-t"], capture_output=True, text=True, encoding="utf-8")
            assert checked.returncode == 0, (checked.stdout, checked.stderr)
            with (home / "core.log").open("wb") as log:
                process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
                try:
                    first = settle("priority-over-lower-latency", TIERS[0], by_tier[0][1])
                    for tier, names in zip(TIERS, by_tier):
                        assert set(first[tier]["all"]) == set(names), (tier, first[tier])
                    imported = api(controller, "GET", "/providers/proxies/liangxinyun")["proxies"]
                    assert {node["name"] for node in imported} == allowed
                    assert first["TikTok首跳"]["now"] == "REJECT"
                    assert set(first["TikTok首跳"]["all"]) == {"REJECT", "🇯🇵 日本Z04 | IEPL"}
                    assert first["TikTok测速"]["all"] == ["TikTok-ISP-Local"]
                    results.append({"case": "membership-source-isolation-and-tiktok-groups", "passed": True})

                    states[by_tier[0][1]]["up"] = False
                    settle("one-node-timeout-stays-in-tier", TIERS[0], by_tier[0][0])
                    for index in range(3):
                        for name in by_tier[index]:
                            states[name]["up"] = False
                        settle(f"whole-tier-timeout-to-{CATEGORIES[index+1]}", TIERS[index+1], by_tier[index+1][1])

                    states[by_tier[0][1]]["up"] = True
                    settle("automatic-high-priority-recovery", TIERS[0], by_tier[0][1])
                    states[by_tier[0][0]].update(up=True, delay=.005)
                    states[by_tier[0][1]]["delay"] = .1
                    settle("automatic-lower-latency-within-tier", TIERS[0], by_tier[0][0])

                    for name in by_tier[1]:
                        states[name]["up"] = True
                    nodes[:] = [node for node in nodes if "LXY: " + node["name"] not in by_tier[0]]
                    api(controller, "PUT", "/providers/proxies/liangxinyun")
                    settle("empty-first-tier-skipped", TIERS[1], by_tier[1][1])
                    assert snapshot()[TIERS[0]]["all"] == ["REJECT"]
                    added = add_node("🇯🇵日本专线12|BGP|流媒体", .005)
                    api(controller, "PUT", "/providers/proxies/liangxinyun")
                    settle("subscription-new-number-auto-return", TIERS[0], added, [added])

                    for state in states.values():
                        state["up"] = False
                    start = time.monotonic()
                    while time.monotonic() - start < 25:
                        last = snapshot()
                        if all(not last[tier]["alive"] for tier in TIERS):
                            status, _ = outgoing(mixed)
                            assert status == 0 or status >= 400, status
                            results.append({"case": "all-tiers-timeout-no-successful-egress", "passed": True})
                            print("all-tiers-timeout-no-successful-egress passed", flush=True)
                            break
                        time.sleep(.2)
                    else:
                        raise AssertionError("all-failed state did not converge")
                    states[added]["up"] = True
                    settle("recovery-after-total-outage", TIERS[0], added)
                except Exception:
                    print((home / "core.log").read_text(encoding="utf-8", errors="replace")[-7000:], flush=True)
                    raise
                finally:
                    process.terminate()
                    process.wait(timeout=8)
    finally:
        subscription.shutdown()
        subscription.server_close()
        for server in servers:
            server.shutdown()
            server.server_close()

    passed = all(case["passed"] for case in results)
    report = {"passed": passed, "coreVersion": version, "profileId": PROFILE, "version": "1.6.0",
              "fixture": {"scope": "loopback synthetic HTTP CONNECT proxies and subscription only",
                          "intervalSeconds": 1, "timeoutMs": 300, "target": TEST_URL,
                          "productionTimingsTested": False, "targetRouterTested": False},
              "cases": results}
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    failures = sum(not case["passed"] for case in results)
    print(f"{'PASS' if passed else 'FAIL'}: {len(results)} real-core fixture cases, {failures} failures; target router remains unverified", flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
