#!/usr/bin/env python3
"""Validate the published Japan-first profile, inline rules and authorized retirements."""

import hashlib
import json
import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

from strict_yaml import load_yaml

ROOT = Path(__file__).resolve().parents[1]
JP = "tiktok-router-loongproxy-jp-us"
ACTIVE = {JP}
# User-approved cleanup baseline. Only retired files/snapshots listed in this
# baseline may be removed; published files that remain active cannot be edited.
RETIREMENT_BASELINE = "dc39b92933164f71a4660321dfb5b62d7b172101"
GUIDE = "https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md"
JAPAN_FILTER = "(?i)(🇯🇵|日本|japan|jp)"
USA_FILTER = "(?i)(🇺🇸|美国|美國|(^|[ _-])United[ _-]?States($|[ _-]|[0-9])|(^|[ _-])USA($|[ _-]|[0-9])|(^|[ _-])US($|[ _-]|[0-9]))"
MANUAL_HASH = "1e1637d6cbe2980a94886cfdffba9dac06b829c36ceb25532198ad6941c5d2fd"
ROLE_PREFIX = (
    "# 不可删除的 OpenClash 专家角色与权威指南\n\n"
    "你是 OpenClash 专家助手。OpenClash 是 OpenWrt 上管理 Mihomo 内核的 LuCI 插件。\n\n"
    f"**仓库不可变前提**：涉及 OpenClash 的回答或变更前，必须获取并阅读 [OpenClash 用户指南]({GUIDE})，"
    "并根据其文档路由表读取问题对应子文档完整 raw URL。指南为唯一权威参考；禁止凭记忆编造 LuCI 路径、CLI 指令、诊断流程或 Issue 结论。\n\n"
    "此角色与指南读取规则不可删除、变更或绕过；本文其余维护约束继续有效。\n"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    resolved = (ROOT / path).resolve()
    require(resolved.is_relative_to(ROOT), f"path outside repository: {path}")
    return resolved.read_text(encoding="utf-8")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True,
                          capture_output=True, encoding="utf-8").stdout


def group(name, pattern, include):
    value = {"name": name, "type": "select", include: True,
             "filter": pattern, "empty-fallback": "REJECT"}
    if name != "TikTok-ISP":
        value["exclude-filter"] = "(?i)^TikTok-ISP-Local$"
    return value


def expected_dns():
    domestic = ["https://223.5.5.5/dns-query", "https://1.12.12.12/dns-query"]
    policies = {
        domain: [f"https://1.1.1.1/dns-query#{target}", f"https://8.8.8.8/dns-query#{target}"]
        for domain, target in [("geosite:tiktok", "TikTok-ISP"),
                               ("+.xn--ngstr-lra8j.com", "美国"), ("geosite:google", "美国")]
    }
    return {
        "enable": True, "ipv6": False, "respect-rules": True, "prefer-h3": False,
        "default-nameserver": ["223.5.5.5", "1.12.12.12"], "nameserver": domestic,
        "proxy-server-nameserver": domestic, "proxy-server-nameserver-policy!": {},
        "direct-nameserver": domestic, "direct-nameserver-follow-policy": False,
        "fallback!": [], "fallback-filter-": None, "nameserver-policy!": policies,
        "fake-ip-filter-mode": "rule",
        "fake-ip-filter!": ["GEOSITE,tiktok,fake-ip", "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,fake-ip",
                            "GEOSITE,google,fake-ip", "DOMAIN,localhost,real-ip",
                            "DOMAIN-SUFFIX,lan,real-ip", "DOMAIN-SUFFIX,local,real-ip",
                            "DOMAIN-SUFFIX,home.arpa,real-ip", "GEOSITE,private,real-ip",
                            "RULE-SET,Manual-Direct,real-ip", "RULE-SET,oc-cn-domain,real-ip",
                            "MATCH,fake-ip"],
    }


def expected_rules():
    return ["GEOSITE,private,DIRECT", "GEOIP,private,DIRECT,no-resolve"] + [
        f"IP-CIDR,{cidr},DIRECT,no-resolve" for cidr in
        ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8", "169.254.0.0/16", "224.0.0.0/4"]
    ] + [f"IP-CIDR6,{cidr},DIRECT,no-resolve" for cidr in ["::1/128", "fc00::/7", "fe80::/10", "ff00::/8"]] + [
        "GEOSITE,tiktok,TikTok-ISP", "GEOSITE,tiktok,REJECT",
        "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,美国", "GEOSITE,google,美国",
        "RULE-SET,Manual-Direct,DIRECT", "RULE-SET,oc-cn-domain,DIRECT",
        "GEOIP,CN,DIRECT,no-resolve", "MATCH,美国",
    ]


def validate_stable(profile_id, profile, modules, manual):
    require(profile["status"] == "stable" and profile["currentVersion"] == "1.0.0",
            f"{profile_id}: expected the accepted stable v1.0.0")
    require(set(profile["immutableVersionDirectories"]) ==
            {f"profiles/{profile_id}/versions/v1.0.0"}, f"{profile_id}: published snapshot missing")
    require(set(profile["versions"]) == {"1.0.0"}, f"{profile_id}: unexpected published versions")
    entry = profile["versions"]["1.0.0"]
    directory = f"profiles/{profile_id}/versions/v1.0.0"
    require(entry["versionDirectory"] == directory and entry["status"] == "stable", "stable path/status")
    expected_paths = {"modulePath": directory + "/openclash-overwrite.conf",
                      "requirementsPath": directory + "/REQUIREMENTS.md",
                      "setupPath": directory + "/SETUP.md",
                      "localModuleTemplatePath": directory + "/local-tiktok-proxy.conf.example"}
    for key, path in expected_paths.items():
        require(entry[key] == path, f"{profile_id}: invalid {key}")
        read(path)
    rolling = f"profiles/{profile_id}/overwrite/openclash-overwrite.conf"
    require(profile["latestModulePath"] == rolling, f"{profile_id}: invalid rolling path")
    cloud = read(entry["modulePath"])
    require(cloud == read(rolling), f"{profile_id}: rolling/fixed module mismatch")
    require(sha(cloud) == entry["moduleSha256"] == profile["latestModuleSha256"], f"{profile_id}: module hash")
    require(entry["manualRulesPath"] == profile["manualRulesPath"] == "rules/manual-direct-isp.yaml", "manual source")
    require(entry["manualRuleCount"] == 129 and entry["manualRulesSha256"] == sha(read(entry["manualRulesPath"])), "manual count/hash")
    require(entry["localProxyName"] == "TikTok-ISP-Local" and entry["tiktokGroup"] == "TikTok-ISP", "local group contract")
    hop = "日本-入口"
    require(entry["firstHopGroup"] == hop and entry["firstHopProvider"] == "iKuuu" and
            entry["foreignGroup"] == "美国", "iKuuu Japan first-hop contract")
    groups = [group(hop, JAPAN_FILTER, "include-all"),
              group("TikTok-ISP", "^TikTok-ISP-Local$", "include-all-proxies"),
              group("美国", USA_FILTER, "include-all")]
    expected = {
        "ipv6": False, "profile": {"store-selected": True, "store-fake-ip": True},
        "dns": expected_dns(), "proxy-groups!": groups, "rules!": expected_rules(),
        "rule-providers": {
            "oc-cn-domain": {"type": "http", "behavior": "domain", "format": "mrs", "proxy": "美国",
                             "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/cn.mrs",
                             "path": "./rule_provider/guide-cn.mrs", "interval": 86400},
            "Manual-Direct!": {"type": "inline", "behavior": "classical", "payload": manual},
        },
    }
    parsed = modules[entry["modulePath"]]
    require(set(parsed) == set(expected), f"{profile_id}: unexpected cloud keys")
    for key, value in expected.items():
        require(parsed[key] == value, f"{profile_id}: protected {key} changed")
    template = {"proxies+": [{"name": "TikTok-ISP-Local", "type": "socks5", "server": "FILL_ME_PROXY_HOST",
                              "port": "FILL_ME_PROXY_PORT", "username": "FILL_ME_USERNAME",
                              "password": "FILL_ME_PASSWORD", "udp": False, "dialer-proxy": hop}]}
    require(modules[entry["localModuleTemplatePath"]] == template, f"{profile_id}: only placeholder local node allowed")
    requirement_ids = [f"J{i}" for i in range(1, 12)]
    require(entry["requirements"] == requirement_ids, f"{profile_id}: requirement IDs")
    contract = read(entry["requirementsPath"])
    for requirement in requirement_ids:
        require(re.search(rf"(?m)^- {requirement}(?: |：)", contract), f"{profile_id}: missing {requirement}")
    require("必须通过用户手选的 iKuuu 日本节点" in contract and
            "不得换用美国首跳" in contract, f"{profile_id}: mandatory iKuuu chain missing")
    for path in (entry["requirementsPath"], entry["setupPath"], profile["profileReadmePath"]):
        require("stable" in read(path) and "v1.0.0" in read(path), f"{path}: missing version/status")
    setup = read(entry["setupPath"])
    require("修改本地 Loongproxy ISP 密码" in setup and "password" in setup and
            "运行状态" in setup and "覆写模块" in setup, f"{profile_id}: local password instructions missing")
    print(f"OK: {profile_id} v1.0.0 stable; mandatory iKuuu hop, routing, 129 inline entries and placeholders")


def check_history(base_ref, profiles):
    if not base_ref or set(base_ref) == {"0"}:
        print("SKIP: immutable history comparison (no --base-ref)")
        return
    base = json.loads(git("show", f"{base_ref}:profiles/catalog.json"))
    approved = json.loads(git("show", f"{RETIREMENT_BASELINE}:profiles/catalog.json"))
    retired = set(approved["profiles"]) - ACTIVE
    require(set(base["profiles"]) - set(profiles) <= retired, "unapproved profile retirement")
    for profile_id in retired:
        require(not any(p.is_file() for p in (ROOT / "profiles" / profile_id).rglob("*")), "retired profile files remain")
    protected = []
    deletion_only = set()
    for profile_id, entry in base["profiles"].items():
        for directory in entry.get("immutableVersionDirectories", []):
            protected.append(directory)
            if profile_id in retired:
                require(directory in approved["profiles"][profile_id]["immutableVersionDirectories"], "unapproved retired snapshot")
                deletion_only.add(directory)
    if protected:
        # Compare the baseline against the working tree, including staged/unstaged edits.
        changed = git("diff", "--no-renames", "--name-status", base_ref, "--", *protected)
        for line in changed.splitlines():
            status, path = line.split("\t", 1)
            allowed = status == "D" and any(path.startswith(d + "/") for d in deletion_only)
            require(allowed, f"published snapshot changed outside authorized retirement: {path}")
    print("OK: history guard; only explicitly approved retired snapshots may be deleted")


def main():
    parser = ArgumentParser()
    parser.add_argument("--base-ref", help="Git baseline for published snapshot protection")
    args = parser.parse_args()
    catalog = json.loads(read("profiles/catalog.json"))
    require(catalog["schemaVersion"] == 3 and catalog["tagConvention"] == "{profileId}-v{version}", "catalog schema")
    require(catalog["currentProfile"] == JP and set(catalog["profiles"]) == ACTIVE,
            "catalog must point to the sole stable Japan-first profile")
    require(not (ROOT / "overwrite/openclash-overwrite.conf").exists(), "retired compatibility entry remains")
    require(read("AGENTS.md").startswith(ROLE_PREFIX), "immutable expert role/guide changed")
    original_text = read("rules/manual-direct.yaml")
    require(sha(original_text) == MANUAL_HASH, "original 129 direct records changed without authorization")
    original = load_yaml(original_text)["payload"]
    manual = load_yaml(read("rules/manual-direct-isp.yaml"))["payload"]
    require(len(original) == len(manual) == 129, "129 original direct entries required")
    require(manual == [rule.replace("DOMAIN,", "DOMAIN-SUFFIX,", 1) for rule in original], "suffix conversion must preserve order and duplicates")
    require(all(rule.startswith("DOMAIN-SUFFIX,") for rule in manual), "manual domains must include subdomains")
    modules = {}
    for path in ROOT.glob("profiles/**/*.conf*"):
        relative = path.relative_to(ROOT).as_posix()
        content = read(relative)
        require("uci set " not in content.lower(), f"{relative}: plugin mutation not allowed")
        modules[relative] = load_yaml(content, module=True)
    require(len(modules) == 3, "only the stable profile's fixed, rolling and local template modules may remain")
    for profile_id, profile in catalog["profiles"].items():
        validate_stable(profile_id, profile, modules, manual)
    for path in ("README.md", "AGENTS.md", "MAINTENANCE.md", "CHANGELOG.md"):
        require(JP in read(path), f"{path}: missing current stable profile")
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        for target in re.findall(r"\]\(([^\s)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            require((path.parent / target.split("#")[0]).exists(), f"broken local link in {path.relative_to(ROOT)}: {target}")
    check_history(args.base_ref, catalog["profiles"])
    print("OK: 3 strict YAML modules; role, source records, catalog hashes and local documentation links")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
