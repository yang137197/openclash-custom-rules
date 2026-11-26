"""Isolated native-core regression: localhost fixtures, no router or subscriptions."""
import argparse
import copy
import hashlib
import http.client
import http.server
import json
import select
import socket
import socketserver
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

from build_dual_subscription import ROOT, DIRECTORY, FIRST, EXIT, MEDIA, DEFAULT, SERVICES
from strict_yaml import load_yaml

URLLIB = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def field(number, value):
    def varint(n):
        result = bytearray()
        while n > 127:
            result.append((n & 127) | 128)
            n >>= 7
        result.append(n)
        return bytes(result)
    return varint(number * 8 + 2) + varint(len(value)) + value


def geosite(code, domains):
    return field(1, field(1, code.encode()) + b"".join(field(2, b"\x08\x02" + field(2, d.encode())) for d in domains))


def exact(stream, size):
    value = stream.read(size)
    if len(value) != size:
        raise OSError("short fixture request")
    return value


class TCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


TRAIL = []


class Proxy(socketserver.StreamRequestHandler):
    def handle(self):
        self.connection.settimeout(3)
        try:
            if self.server.kind == "http":
                line = self.rfile.readline().decode().strip()
                while self.rfile.readline() not in (b"\r\n", b"\n", b""):
                    pass
                if not line.startswith("CONNECT ") or not self.server.alive:
                    self.wfile.write(b"HTTP/1.1 502 Failed\r\nContent-Length: 0\r\n\r\n")
                    return
                host, port = line.split()[1].rsplit(":", 1)
                time.sleep(self.server.delay)
                ok = b"HTTP/1.1 200 Connection established\r\n\r\n"
            else:
                version, count = exact(self.rfile, 2)
                methods = exact(self.rfile, count)
                method = 2 if 2 in methods else 0
                self.wfile.write(bytes((5, method)))
                self.wfile.flush()
                if method == 2:
                    exact(self.rfile, 1)
                    exact(self.rfile, exact(self.rfile, 1)[0])
                    exact(self.rfile, exact(self.rfile, 1)[0])
                    self.wfile.write(b"\x01\x00")
                    self.wfile.flush()
                version, command, reserved, address_type = exact(self.rfile, 4)
                if command != 1:
                    return
                host = (socket.inet_ntoa(exact(self.rfile, 4)) if address_type == 1 else
                        exact(self.rfile, exact(self.rfile, 1)[0]).decode())
                port = int.from_bytes(exact(self.rfile, 2), "big")
                ok = b"\x05\x00\x00\x01\x7f\x00\x00\x01\x00\x00"
            # Every connection in this harness stays on the local computer.
            if int(port) not in self.server.allowed_ports:
                return
            with socket.create_connection(("127.0.0.1", int(port)), timeout=2) as upstream:
                TRAIL.append((self.server.label, host, int(port)))
                self.wfile.write(ok)
                self.wfile.flush()
                sockets = (self.connection, upstream)
                while True:
                    ready, _, _ = select.select(sockets, [], [], 3)
                    if not ready:
                        return
                    for source in ready:
                        data = source.recv(65536)
                        if not data:
                            return
                        (upstream if source is self.connection else self.connection).sendall(data)
        except (OSError, ValueError):
            return


class Origin(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        body = b"local-fixture-ok"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class DNS(socketserver.BaseRequestHandler):
    def handle(self):
        packet, sock = self.request
        end = 12
        while packet[end]:
            end += packet[end] + 1
        end += 5
        question = packet[12:end]
        is_a = packet[end - 4:end - 2] == b"\x00\x01"
        header = packet[:2] + b"\x81\x80\x00\x01" + (b"\x00\x01" if is_a else b"\x00\x00") + b"\x00\x00\x00\x00"
        answer = b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x01\x00\x04\x7f\x00\x00\x01" if is_a else b""
        sock.sendto(header + question + answer, self.client_address)


def start(server):
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def free_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def official_merge(ruby, library, base, modules, output):
    code = ("require 'yaml'; require ARGV.shift; value=YAML.load_file(ARGV.shift); "
            "ARGV.each {|p| value=YAML.overwrite(value,YAML.load(File.read(p).split('[YAML]',2).last))}; "
            "STDOUT.write(YAML.dump(value))")
    result = subprocess.run([ruby, "-EUTF-8:UTF-8", "-e", code, str(library), str(base), *map(str, modules)],
                            capture_output=True, check=True)
    output.write_bytes(result.stdout)
    return yaml.safe_load(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", required=True)
    parser.add_argument("--ruby", required=True)
    parser.add_argument("--official-yaml", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    assert hashlib.sha256(args.official_yaml.read_bytes()).hexdigest() == "1249abf411e1df9e8fe542fb3584f34a27e6e3a587942e5d9f759a32b1bd8261"
    cases = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        cases.append(name)
    servers = []
    process = None
    with tempfile.TemporaryDirectory(prefix="dual-jp-native-") as directory:
        home = Path(directory)
        try:
            origin = start(http.server.ThreadingHTTPServer(("127.0.0.1", 0), Origin))
            servers.append(origin)
            origin_port = origin.server_port
            def proxy(label, delay=0.01, kind="http"):
                server = TCPServer(("127.0.0.1", 0), Proxy)
                server.kind, server.label, server.delay, server.alive = kind, label, delay, True
                server.allowed_ports = {origin_port}
                servers.append(start(server))
                return server
            jp_fast, jp_slow = proxy("IK-fast", .01), proxy("IK-slow", .12)
            a, b, c = proxy("A"), proxy("B"), proxy("C")
            isp = proxy("ISP", kind="socks")
            for server in (jp_fast, jp_slow):
                server.allowed_ports.add(isp.server_address[1])
            cloud = load_yaml((DIRECTORY / "openclash-overwrite.conf").read_text(encoding="utf-8"), module=True)
            local = load_yaml((DIRECTORY / "local-tiktok-proxy.conf").read_text(encoding="utf-8"), module=True)
            base = dict(**{"mixed-port": free_port(), "allow-lan": False, "mode": "rule",
                           "external-controller": "127.0.0.1:" + str(free_port()),
                           "proxy-groups": [{"name": "美国", "type": "select", "proxies": ["DIRECT"]}],
                           "sentinel": {"keep": ["plugin-base", 1]}})
            base_path, local_path = home / "base.yaml", home / "local.conf"
            base_path.write_text(yaml.safe_dump(base), encoding="utf-8")
            local["proxies+"][0].update(server="127.0.0.1", port=isp.server_address[1], username="fixture", password="fixture")
            # Fill only placeholders for the real merge. Provider input remains
            # HTTP at this stage; synthetic files are substituted afterwards.
            for pd in local["proxy-providers"].values():
                pd["url"] = "http://127.0.0.1:1/local-fixture-only"
            local_path.write_text("[YAML]\n" + yaml.safe_dump(local, allow_unicode=True), encoding="utf-8")
            merged = official_merge(args.ruby, args.official_yaml, base_path,
                                    [local_path, DIRECTORY / "openclash-overwrite.conf"], home / "merged.yaml")
            check("official-merge-replaces-groups-keeps-plugin-base", merged["sentinel"] == base["sentinel"] and
                  [g["name"] for g in merged["proxy-groups"]] == [FIRST, EXIT, MEDIA, DEFAULT])
            check("official-merge-retains-entire-current-direct-source", merged["rule-providers"]["Manual-Direct"]["payload"] ==
                  load_yaml((ROOT / "rules/manual-direct.yaml").read_text(encoding="utf-8"))["payload"])
            check("official-merge-consumes-nested-dns-operators-with-absent-base", "nameserver-policy" in merged["dns"] and
                  not any(key.endswith(("!", "+", "-", "*")) for key in merged["dns"]))
            def node(name, server):
                return dict(name=name, type="http", server="127.0.0.1", port=server.server_address[1])
            ik_nodes = [node(f"🇯🇵 日本Z{n:02d} | IEPL", jp_fast if n == 12 else jp_slow) for n in range(12, 0, -1)]
            ik_nodes += [node("🇺🇸 美国Z01 | IEPL", jp_fast), node("日本专线01|BGP|流媒体", jp_fast)]
            lxy_nodes = [node(f"🇯🇵日本高速{n:02d}|BGP|CUCM", c) for n in range(6, 0, -1)]
            lxy_nodes += [node(f"🇯🇵日本专线{n:02d}|BGP|流媒体", a if n == 1 else b) for n in range(5, 0, -1)]
            lxy_nodes += [node("新加坡专线01|BGP|流媒体", c), node("日本Z01 | IEPL", c), node("日本专线100|BGP|流媒体", c)]
            test_url = f"http://127.0.0.1:{origin_port}/generate_204"
            for key, nodes in (("dual-ikuuu", ik_nodes), ("dual-liangxinyun", lxy_nodes)):
                fixture_path = home / (key + ".yaml")
                fixture_path.write_text(yaml.safe_dump({"proxies": nodes}, allow_unicode=True), encoding="utf-8")
                pd = merged["proxy-providers"][key]
                pd["type"], pd["path"] = "file", str(fixture_path)
                pd.pop("url")
                pd["health-check"].update(url=test_url, interval=3600)
            for g in merged["proxy-groups"]:
                g.update(url=test_url, interval=3600)
            service_domains = {s: f"{s}.example.test" for s in SERVICES}
            for name, pd in merged["rule-providers"].items():
                if pd["type"] != "http":
                    continue
                fixture_path = home / (name + ".yaml")
                domains = [service_domains[name[5:]]] if name.startswith("dual-") else ["china.example.test"]
                fixture_path.write_text(yaml.safe_dump({"payload": domains}), encoding="utf-8")
                pd.update(type="file", format="yaml", path=str(fixture_path))
                pd.pop("url")
            (home / "geosite.dat").write_bytes(geosite("tiktok", ["tiktok.example.test"]) + geosite("google", ["google.example.test"]) + geosite("private", ["lan"]) + geosite("cn", ["china.example.test"]))
            # Non-matching CIDRs avoid external geodata downloads while retaining
            # actual GEOIP-rule parsing in the native core.
            geo = b"".join(field(1, field(1, code.encode()) + field(2, field(1, bytes(ip)) + b"\x10\x20"))
                           for code, ip in (("CN", (192, 0, 2, 1)), ("telegram", (192, 0, 2, 2)), ("private", (192, 0, 2, 3))))
            (home / "geoip.dat").write_bytes(geo)
            merged["geodata-mode"] = True
            merged["geo-auto-update"] = False
            merged["geox-url"] = {"geosite": "http://127.0.0.1:1/no-external-geodata", "geoip": "http://127.0.0.1:1/no-external-geodata"}
            dns_server = start(socketserver.ThreadingUDPServer(("127.0.0.1", 0), DNS))
            servers.append(dns_server)
            dns_address = "127.0.0.1:" + str(dns_server.server_address[1])
            # Resolve only after rule matching: static hosts would turn every
            # fixture destination into a private IP before the real rules run.
            merged["dns"] = {"enable": True, "listen": "127.0.0.1:" + str(free_port()),
                             "nameserver": [dns_address], "default-nameserver": [dns_address],
                             "proxy-server-nameserver": [dns_address], "enhanced-mode": "redir-host"}
            config_path = home / "config.yaml"
            config_path.write_text(yaml.safe_dump(merged, allow_unicode=True, sort_keys=False, width=100000), encoding="utf-8")
            tested = subprocess.run([args.core, "-t", "-d", str(home), "-f", str(config_path)], capture_output=True)
            if tested.returncode:
                raise AssertionError(tested.stdout.decode("utf-8", errors="replace") + tested.stderr.decode("utf-8", errors="replace"))
            check("native-core-parses-all-real-logical-rules-and-groups", True)
            core_log = (home / "core.txt").open("w", encoding="utf-8")
            process = subprocess.Popen([args.core, "-d", str(home), "-f", str(config_path)], stdout=core_log, stderr=subprocess.STDOUT)
            endpoint = "http://" + merged["external-controller"]
            def api(path):
                with URLLIB.open(endpoint + path, timeout=8) as response:
                    return json.loads(response.read() or b"{}")
            def wait_for(fn, seconds=15):
                deadline = time.monotonic() + seconds
                while time.monotonic() < deadline:
                    try:
                        if fn():
                            return True
                    except (OSError, ValueError):
                        pass
                    time.sleep(.2)
                return False
            def group(name):
                return api("/proxies/" + urllib.parse.quote(name, safe=""))
            check("native-core-starts", wait_for(lambda: "proxies" in api("/proxies")))
            expected = [f"LXY: 🇯🇵日本专线{n:02d}|BGP|流媒体" for n in range(1, 6)] + [f"LXY: 🇯🇵日本高速{n:02d}|BGP|CUCM" for n in range(1, 7)]
            check("subscription-shuffle-and-added-numbers-preserve-priority", group(MEDIA)["all"] == expected)
            check("supplier-isolation-and-new-ikuuu-Z12-in-both-groups", group(FIRST)["all"] == group(DEFAULT)["all"] and len(group(FIRST)["all"]) == 12 and all("日本Z" in n for n in group(FIRST)["all"]))
            check("isp-group-only-fixed-local-exit", group(EXIT)["all"] == ["TikTok-ISP-Local"])
            def refresh():
                def history():
                    entry = api("/providers/proxies/dual-liangxinyun")["proxies"][0]
                    return entry.get("extra", {}).get(test_url, {}).get("history", entry.get("history"))
                previous = history()
                # Native health checks share a one-second singleDo cache.
                time.sleep(1.1)
                api("/providers/proxies/dual-liangxinyun/healthcheck")
                if not wait_for(lambda: history() != previous, 8):
                    raise AssertionError("provider health refresh produced no new history")
                time.sleep(.2)
            refresh()
            check("all-healthy-uses-A-not-latency-ranking", group(MEDIA)["now"] == expected[0])
            a.alive = False
            refresh()
            check("A-failed-uses-B", wait_for(lambda: group(MEDIA)["now"] == expected[1], 8))
            b.alive = False
            refresh()
            check("all-dedicated-failed-uses-first-highspeed", group(MEDIA)["now"] == expected[5])
            b.alive = True
            refresh()
            check("B-recovers-preempts-highspeed", group(MEDIA)["now"] == expected[1])
            a.alive = True
            refresh()
            check("A-recovers-preempts-B", group(MEDIA)["now"] == expected[0])
            fast_name = "IK: 🇯🇵 日本Z12 | IEPL"
            check("ikuuu-both-groups-select-lowest-delay", wait_for(lambda: group(FIRST)["now"] == fast_name and group(DEFAULT)["now"] == fast_name, 20))
            def route(host):
                before = len(TRAIL)
                connection = http.client.HTTPConnection("127.0.0.1", merged["mixed-port"], timeout=5)
                connection.request("GET", f"http://{host}:{origin_port}/sample", headers={"Connection": "close"})
                response = connection.getresponse()
                body = response.read()
                connection.close()
                assert response.status == 200 and body == b"local-fixture-ok", host
                return [entry[0] for entry in TRAIL[before:] if entry[2] == origin_port]
            for service, host in service_domains.items():
                check("route-media-" + service, route(host) == ["A"])
            for host in ("claude.ai", "github.com", "google.example.test"):
                check("route-default-" + host, route(host) == ["IK-fast"])
            check("route-dedicated-github-download", route("objects.githubusercontent.com") == ["A"])
            check("manual-direct-remains-direct", route("pve.yangnas.cn") == [])
            check("china-domain-remains-direct", route("china.example.test") == [])
            check("tiktok-full-chain-includes-fixed-ISP", route("tiktok.example.test") == ["ISP"])
            report = dict(passed=True, caseCount=len(cases), cases=cases,
                          coreVersion=subprocess.check_output([args.core, "-v"], text=True).splitlines()[0],
                          officialMergeSource="vernesong/OpenClash@e553e82", fixturesOnly=True,
                          routerAccess=False, realSubscriptionsUsed=False, formalAcceptance=False)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report))
        except Exception:
            if process and process.poll() is None:
                state = api("/providers/proxies/dual-liangxinyun")
                print(json.dumps({"providerDiagnostic": {k: v for k, v in state.items() if k != "proxies"},
                                  "sampleNode": state["proxies"][0]}))
                core_log.flush()
                print((home / "core.txt").read_text(encoding="utf-8")[-3500:])
            raise
        finally:
            if process:
                process.terminate()
                process.wait(timeout=10)
                core_log.close()
            for server in servers:
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    main()
