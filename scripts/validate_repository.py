#!/usr/bin/env python3
"""Validate the published Japan-first profile, inline rules and authorized retirements."""

import hashlib
import json
import re
import subprocess
import sys
from argparse import ArgumentParser
from functools import cmp_to_key
from pathlib import Path

from strict_yaml import load_yaml

ROOT = Path(__file__).resolve().parents[1]
JP = "tiktok-router-loongproxy-jp-us"
ACTIVE = {JP}
BASELINE_VERSION = "1.0.0"
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
VERSION_POLICY_TEXT = (
    "## 不可变版本规则\n\n"
    "正式版本 `tiktok-router-loongproxy-jp-us v1.0.0` 是本仓库第一版正式版。此前的历史版本及 beta 版本已从当前文件树、Git 标签和 GitHub Releases 清理；Git 提交历史保留。\n\n"
    "每个后续候选版和正式版都必须使用严格高于仓库已记录最高版本的 SemVer；禁止回退、复用或覆盖版本号。每个新版本必须在 `CHANGELOG.md` 增加同版本标题和具体更新内容。已发布版本目录、标签和 Release 不得改写；更新一律创建递增版本。\n\n"
    "`AGENTS.md` 开头的专家角色和官方指南入口，以及正式版 `SETUP.md` 中的 OpenClash 设置建议，都是不可删除的仓库前提；任何整理不得删除或削弱这些内容。"
)
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def semver_parts(version):
    match = SEMVER_PATTERN.fullmatch(version)
    require(match is not None, f"invalid SemVer version: {version}")
    prerelease = match.group(4)
    identifiers = prerelease.split(".") if prerelease is not None else None
    if identifiers:
        require(all(identifiers), f"invalid SemVer prerelease: {version}")
        require(all(not (part.isdigit() and len(part) > 1 and part.startswith("0"))
                    for part in identifiers), f"invalid numeric prerelease: {version}")
    return tuple(int(match.group(i)) for i in range(1, 4)), identifiers


def compare_versions(left, right):
    left_core, left_pre = semver_parts(left)
    right_core, right_pre = semver_parts(right)
    if left_core != right_core:
        return (left_core > right_core) - (left_core < right_core)
    if left_pre is None or right_pre is None:
        if left_pre is None and right_pre is None:
            return 0
        return 1 if left_pre is None else -1
    for left_id, right_id in zip(left_pre, right_pre):
        if left_id == right_id:
            continue
        left_numeric = left_id.isdigit()
        right_numeric = right_id.isdigit()
        if left_numeric and right_numeric:
            return (int(left_id) > int(right_id)) - (int(left_id) < int(right_id))
        if left_numeric != right_numeric:
            return -1 if left_numeric else 1
        return (left_id > right_id) - (left_id < right_id)
    return (len(left_pre) > len(right_pre)) - (len(left_pre) < len(right_pre))


def changelog_has_update(changelog, profile_id, version):
    header = re.compile(rf"^##\s+{re.escape(profile_id)} v{re.escape(version)}(?:\s|$)", re.M)
    match = header.search(changelog)
    if not match:
        return False
    next_heading = re.search(r"^##\s+", changelog[match.end():], re.M)
    body = changelog[match.end():match.end() + next_heading.start()] if next_heading else changelog[match.end():]
    return any(re.match(r"^\s*[-*]\s+\S", line) for line in body.splitlines())


def validate_version_sequence(profile_id, versions, prior_versions, changelog,
                              current_version=None, prior_current_version=None):
    version_set = set(versions)
    require(version_set, f"{profile_id}: version catalog must not be empty")
    for version in version_set:
        require(compare_versions(version, BASELINE_VERSION) >= 0,
                f"{profile_id}: version precedes the v{BASELINE_VERSION} baseline")
    require(set(prior_versions) <= version_set,
            f"{profile_id}: a recorded version was removed or reused")
    if current_version is not None and prior_current_version is not None:
        require(compare_versions(current_version, prior_current_version) >= 0,
                f"{profile_id}: current version cannot move backwards from {prior_current_version}")
    added = sorted(version_set - set(prior_versions), key=cmp_to_key(compare_versions))
    if prior_versions:
        threshold = max(prior_versions, key=cmp_to_key(compare_versions))
        for version in added:
            require(compare_versions(version, threshold) > 0,
                    f"{profile_id}: new version {version} must exceed {threshold}")
            require(changelog_has_update(changelog, profile_id, version),
                    f"{profile_id}: new version {version} needs a CHANGELOG entry with update content")
            threshold = version
    else:
        for version in added:
            require(changelog_has_update(changelog, profile_id, version),
                    f"{profile_id}: new version {version} needs a CHANGELOG entry with update content")


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


def validate_version_catalog(profile_id, profile, changelog):
    versions = profile["versions"]
    require(isinstance(versions, dict) and versions, f"{profile_id}: version catalog must not be empty")
    current_version = profile["currentVersion"]
    require(current_version in versions, f"{profile_id}: current version is not indexed")
    stable_versions = []
    immutable_directories = set()
    for version, entry in versions.items():
        semver_parts(version)
        require(compare_versions(version, BASELINE_VERSION) >= 0,
                f"{profile_id}: version precedes the v{BASELINE_VERSION} baseline")
        require(entry["versionDirectory"] == f"profiles/{profile_id}/versions/v{version}",
                f"{profile_id}: invalid version directory for {version}")
        require(entry["status"] in {"stable", "candidate"}, f"{profile_id}: invalid status for {version}")
        require(changelog_has_update(changelog, profile_id, version),
                f"{profile_id}: CHANGELOG entry missing for {version}")
        if entry["status"] == "stable":
            stable_versions.append(version)
            immutable_directories.add(entry["versionDirectory"])
        else:
            require(compare_versions(version, current_version) > 0,
                    f"{profile_id}: candidate {version} must exceed current stable {current_version}")
    require(stable_versions and current_version == max(stable_versions, key=cmp_to_key(compare_versions)),
            f"{profile_id}: currentVersion must be the latest stable version")
    require(profile["status"] == versions[current_version]["status"] == "stable",
            f"{profile_id}: current profile must point to a stable version")
    require(set(profile["immutableVersionDirectories"]) == immutable_directories,
            f"{profile_id}: immutable directories must match published stable versions")


def validate_stable(profile_id, profile, modules, manual):
    version = profile["currentVersion"]
    entry = profile["versions"][version]
    directory = f"profiles/{profile_id}/versions/v{version}"
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
        require("stable" in read(path) and f"v{version}" in read(path), f"{path}: missing version/status")
    setup = read(entry["setupPath"])
    require("修改本地 Loongproxy ISP 密码" in setup and "password" in setup and
            "运行状态" in setup and "覆写模块" in setup, f"{profile_id}: local password instructions missing")
    setup_markers = ["## 独立手工设置", "运行模式 / 代理模式", "实验性：绕过指定区域 IPv4",
                     "禁用 QUIC", "IPv6 设置", "DNS 顺序为"]
    require(all(marker in setup for marker in setup_markers),
            f"{profile_id}: protected OpenClash settings recommendations are missing")
    print(f"OK: {profile_id} v{version} stable; mandatory iKuuu hop, routing, 129 inline entries and placeholders")


def check_version_progression(base_ref, catalog):
    changelog = read("CHANGELOG.md")
    prior_versions = []
    prior_current_version = None
    if base_ref and set(base_ref) != {"0"}:
        base = json.loads(git("show", f"{base_ref}:profiles/catalog.json"))
        prior = base["profiles"].get(JP)
        if prior:
            prior_versions = list(prior["versions"])
            prior_current_version = prior["currentVersion"]
    profile = catalog["profiles"][JP]
    validate_version_sequence(JP, profile["versions"], prior_versions, changelog,
                              profile["currentVersion"], prior_current_version)
    print("OK: version sequence is monotonic and each version has CHANGELOG update content")


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
    for path in ("AGENTS.md", "MAINTENANCE.md"):
        require(VERSION_POLICY_TEXT in read(path), f"{path}: immutable version policy changed or removed")
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
    expected_modules = set()
    for profile in catalog["profiles"].values():
        expected_modules.add(profile["latestModulePath"])
        for version_entry in profile["versions"].values():
            expected_modules.update(version_entry[key] for key in ("modulePath", "localModuleTemplatePath")
                                    if key in version_entry)
    require(set(modules) == expected_modules, "module files must match the version catalog")
    for profile_id, profile in catalog["profiles"].items():
        validate_version_catalog(profile_id, profile, read("CHANGELOG.md"))
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
    check_version_progression(args.base_ref, catalog)
    check_history(args.base_ref, catalog["profiles"])
    print("OK: strict YAML modules; role, version policy, source records, catalog hashes and local links")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
