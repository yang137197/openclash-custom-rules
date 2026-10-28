#!/usr/bin/env python3
"""Validate profile catalogs, version evidence and profile-specific OpenClash contracts."""

import hashlib
import json
import re
import subprocess
import sys
from argparse import ArgumentParser
from datetime import date
from functools import cmp_to_key
from pathlib import Path

from strict_yaml import load_yaml
from sync_manual_direct import (
    parse_payload as parse_manual_direct_payload,
    validate_payload as validate_manual_direct_payload,
)

ROOT = Path(__file__).resolve().parents[1]
JP = "tiktok-router-loongproxy-jp-us"
BASELINE_VERSION = "1.0.0"
# The first stable release predates environment manifests and remains immutable.
LEGACY_ENVIRONMENT_EXEMPTIONS = {(JP, "1.0.0")}
# Historical modules keep their published .conf.example template paths. New
# profile versions must use an extension accepted by OpenClash's local uploader.
LEGACY_EXAMPLE_TEMPLATE_VERSIONS = {"1.0.0", "1.0.1", "1.0.4"}
# User-approved cleanup baseline. Only retired files/snapshots listed in this
# baseline may be removed; published files that remain active cannot be edited.
RETIREMENT_BASELINE = "dc39b92933164f71a4660321dfb5b62d7b172101"
GUIDE = "https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md"
JAPAN_FILTER = "(?i)(🇯🇵|日本|japan|jp)"
USA_FILTER = "(?i)(🇺🇸|美国|美國|(^|[ _-])United[ _-]?States($|[ _-]|[0-9])|(^|[ _-])USA($|[ _-]|[0-9])|(^|[ _-])US($|[ _-]|[0-9]))"
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
    "每个方案（profile）独立维护 SemVer：同一方案的新候选版和正式版必须严格高于该方案已记录最高版本；禁止回退、复用或覆盖。不同方案的版本号互不比较，例如 A v1.0.0 与 B v1.0.0 可以同时存在。每个新版本必须在 `CHANGELOG.md` 增加同方案、同版本标题和具体更新内容。已发布版本目录、标签和 Release 不得改写；更新一律在对应方案内创建递增版本。\n\n"
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


def valid_iso_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def validate_no_raw_debug_logs():
    section_markers = {"## 系统信息", "## 依赖检查", "## 内核检查", "## 插件设置",
                       "## 覆写模块设置", "## 活动连接信息"}
    candidates = git("ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")
    for relative in candidates:
        if not relative:
            continue
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            continue
        if path.suffix.lower() == ".log":
            raise ValueError(f"raw log files must not be committed: {relative}")
        if path.suffix.lower() in {".txt", ".md"}:
            found = set()
            overlap = ""
            overlap_size = max(map(len, section_markers)) - 1
            with path.open(encoding="utf-8", errors="ignore") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), ""):
                    sample = overlap + chunk
                    found.update(marker for marker in section_markers if marker in sample)
                    if len(found) >= 3:
                        raise ValueError(f"raw OpenClash debug log sections detected: {relative}")
                    overlap = sample[-overlap_size:]


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


def expected_stable_rules(profile_id, version):
    rules = expected_rules()
    if profile_id == JP and version in {"1.0.4", "1.0.5", "1.0.6", "1.0.7"}:
        # Claude/Anthropic endpoints stay on the static ISP, while GitHub uses US.
        rules[12:12] = [
            "DOMAIN-SUFFIX,anthropic.com,TikTok-ISP",
            "DOMAIN-SUFFIX,claude.ai,TikTok-ISP",
            "DOMAIN-SUFFIX,claude.com,TikTok-ISP",
            "DOMAIN,storage.googleapis.com,TikTok-ISP",
            "DOMAIN-SUFFIX,npmjs.org,TikTok-ISP",
            "DOMAIN-SUFFIX,claudeusercontent.com,TikTok-ISP",
            "DOMAIN-SUFFIX,claudemcpcontent.com,TikTok-ISP",
            "DOMAIN-SUFFIX,github.com,美国",
            "DOMAIN-SUFFIX,githubusercontent.com,美国",
            "DOMAIN-SUFFIX,githubassets.com,美国",
            "DOMAIN-WILDCARD,*-review.googlesource.com,TikTok-ISP",
            "DOMAIN,http-intake.logs.us5.datadoghq.com,TikTok-ISP",
            "DOMAIN,browser-intake-us5-datadoghq.com,TikTok-ISP",
            "DOMAIN,formulae.brew.sh,TikTok-ISP",
        ]
    if profile_id == JP and version == "1.0.6":
        google_index = rules.index("GEOSITE,google,美国")
        rules.insert(google_index + 1, "DOMAIN-SUFFIX,huzhou.host,DIRECT")
    return rules


def validate_rolling_direct_additions(additions, baseline_rules):
    require(isinstance(additions, list), "rolling direct additions must be a list")
    seen = set()
    baseline_normalized = set()
    for baseline_rule in baseline_rules:
        baseline_parts = baseline_rule.split(",")
        if (len(baseline_parts) == 3 and
                baseline_parts[0] in {"DOMAIN", "DOMAIN-SUFFIX"} and
                baseline_parts[2] == "DIRECT"):
            baseline_normalized.add((baseline_parts[0], baseline_parts[1].casefold()))
    for rule in additions:
        require(isinstance(rule, str), "rolling direct rule must be a string")
        parts = rule.split(",")
        require(len(parts) == 2 and parts[0] in {"DOMAIN", "DOMAIN-SUFFIX"},
                f"unsupported manual direct source rule: {rule}")
        domain = parts[1]
        labels = domain.split(".")
        label_pattern = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\Z")
        require(len(domain) <= 253 and len(labels) >= 2 and
                all(label_pattern.fullmatch(label) for label in labels),
                f"invalid domain in manual direct source rule: {rule}")
        normalized = (parts[0], domain.casefold())
        require(normalized not in seen, f"duplicate manual direct source rule: {rule}")
        require(normalized not in baseline_normalized,
                f"manual direct source rule duplicates a stable rule: {rule}")
        seen.add(normalized)
    return [f"{rule},DIRECT" for rule in additions]


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
            if stable_versions:
                latest_stable = max(stable_versions, key=cmp_to_key(compare_versions))
                require(compare_versions(version, latest_stable) > 0,
                        f"{profile_id}: candidate {version} must exceed current stable {latest_stable}")
    if stable_versions:
        latest_stable = max(stable_versions, key=cmp_to_key(compare_versions))
        require(current_version == latest_stable,
                f"{profile_id}: currentVersion must be the latest stable version")
        require(profile["status"] == versions[current_version]["status"] == "stable",
                f"{profile_id}: stable profile must point to its latest stable version")
    else:
        latest_candidate = max(versions, key=cmp_to_key(compare_versions))
        require(profile["status"] == "candidate" and
                versions[current_version]["status"] == "candidate" and
                current_version == latest_candidate,
                f"{profile_id}: a profile without a stable release must point to its latest candidate")
    require(set(profile["immutableVersionDirectories"]) == immutable_directories,
            f"{profile_id}: immutable directories must match published stable versions")


def validate_environment_record(profile_id, version, status, record):
    require(record.get("schemaVersion") == 1, f"{profile_id} v{version}: environment schema must be 1")
    require(record.get("profileId") == profile_id and record.get("version") == version,
            f"{profile_id} v{version}: environment identity mismatch")
    require(record.get("status") in {"pending", "verified"},
            f"{profile_id} v{version}: invalid environment status")
    require(isinstance(record.get("behaviorChanged"), bool),
            f"{profile_id} v{version}: behaviorChanged must be boolean")
    environment = record.get("environment")
    required_environment = {"openclashVersion", "openclashBuild", "mihomoVersion", "mihomoBuild",
                            "openwrtVersion", "deviceArchitecture", "deviceModel"}
    require(isinstance(environment, dict) and set(environment) == required_environment,
            f"{profile_id} v{version}: invalid environment fields")
    require(all(isinstance(value, str) and value.strip() for value in environment.values()),
            f"{profile_id} v{version}: environment fields must be explicit strings")
    runtime = record.get("runtimeConfiguration")
    runtime_fields = {"activeConfigLabel", "enabledModulesInOrder", "settingsBaseline", "settingsDeviations"}
    require(isinstance(runtime, dict) and set(runtime) == runtime_fields,
            f"{profile_id} v{version}: invalid runtime configuration fields")
    require(isinstance(runtime.get("activeConfigLabel"), str) and runtime["activeConfigLabel"].strip() and
            isinstance(runtime.get("enabledModulesInOrder"), list) and
            all(isinstance(name, str) and name.strip() for name in runtime["enabledModulesInOrder"]) and
            runtime.get("settingsBaseline") in {"unknown", "matched-setup", "deviations"} and
            isinstance(runtime.get("settingsDeviations"), list) and
            all(isinstance(item, str) and item.strip() for item in runtime["settingsDeviations"]),
            f"{profile_id} v{version}: invalid active configuration or settings snapshot")
    evidence = record.get("evidence")
    required_evidence = {"source", "capturedAt", "rawDebugLogCommitted",
                         "runtimeAcceptance", "userConfirmed", "summary"}
    require(isinstance(evidence, dict) and set(evidence) == required_evidence,
            f"{profile_id} v{version}: invalid environment evidence fields")
    require(evidence.get("source") in {"none", "user-report", "debug-log", "reused"},
            f"{profile_id} v{version}: invalid environment evidence source")
    require(evidence.get("runtimeAcceptance") in {"not-run", "passed", "failed"},
            f"{profile_id} v{version}: invalid runtime acceptance state")
    require(isinstance(evidence.get("userConfirmed"), bool) and
            evidence.get("rawDebugLogCommitted") is False,
            f"{profile_id} v{version}: confirmation must be boolean and raw logs must stay out of Git")
    require(isinstance(evidence.get("summary"), str) and evidence["summary"].strip(),
            f"{profile_id} v{version}: evidence summary is required")
    if evidence["source"] == "debug-log":
        require(valid_iso_date(evidence["capturedAt"]),
                f"{profile_id} v{version}: debug-log date must use YYYY-MM-DD")
    reused_from = record.get("reusedFromVersion")
    require(reused_from is None or isinstance(reused_from, str),
            f"{profile_id} v{version}: reusedFromVersion must be a version or null")
    require(record.get("setupDocument") == "SETUP.md",
            f"{profile_id} v{version}: setupDocument must point to SETUP.md")

    if record["status"] == "verified":
        require(all(value.lower() not in {"unknown", "not provided", "待补充"}
                    for value in environment.values()),
                f"{profile_id} v{version}: verified environment versions cannot be unknown")
        require(runtime["activeConfigLabel"].lower() != "unknown" and
                runtime["enabledModulesInOrder"] and
                runtime["settingsBaseline"] in {"matched-setup", "deviations"},
                f"{profile_id} v{version}: verified record must capture active config, modules and settings baseline")
        require((runtime["settingsBaseline"] == "deviations") == bool(runtime["settingsDeviations"]),
                f"{profile_id} v{version}: settings deviations must be documented consistently")
        if evidence["source"] == "debug-log":
            require(valid_iso_date(evidence["capturedAt"]) and
                    evidence["runtimeAcceptance"] == "passed" and evidence["userConfirmed"],
                    f"{profile_id} v{version}: verified log-backed environment needs accepted runtime testing")
        else:
            require(evidence["source"] == "reused" and not record["behaviorChanged"] and reused_from,
                    f"{profile_id} v{version}: verified environment needs a log or an unchanged-version reference")

    if status == "candidate":
        if record["status"] == "verified":
            require(evidence["source"] == "debug-log" and evidence["capturedAt"] and
                    evidence["runtimeAcceptance"] == "passed" and evidence["userConfirmed"],
                    f"{profile_id} v{version}: verified candidate needs log-backed accepted runtime evidence")
        return

    require(record["status"] == "verified", f"{profile_id} v{version}: stable release needs verified environment evidence")
    if record["behaviorChanged"]:
        require(evidence["source"] == "debug-log" and
                valid_iso_date(evidence["capturedAt"]) and
                evidence["runtimeAcceptance"] == "passed" and evidence["userConfirmed"],
                f"{profile_id} v{version}: behavior-changing stable release needs dated debug-log and user acceptance")
        require(reused_from is None, f"{profile_id} v{version}: behavior-changing release cannot reuse old evidence")
    else:
        require(evidence["source"] in {"reused", "debug-log"},
                f"{profile_id} v{version}: no-behavior-change release needs reusable or fresh environment evidence")
        if evidence["source"] == "reused":
            require(reused_from and compare_versions(reused_from, version) < 0,
                    f"{profile_id} v{version}: reused environment must cite an earlier version")
        else:
            require(reused_from is None and
                    valid_iso_date(evidence["capturedAt"]) and
                    evidence["runtimeAcceptance"] == "passed" and evidence["userConfirmed"],
                    f"{profile_id} v{version}: fresh environment evidence needs dated accepted runtime testing")
        require(all(value.lower() not in {"unknown", "not provided", "待补充"}
                    for value in environment.values()),
                f"{profile_id} v{version}: stable environment values cannot be unknown")


def validate_reused_environment_source(profile_id, version, profile, record):
    source_version = record["reusedFromVersion"]
    versions = profile["versions"]
    require(source_version in versions,
            f"{profile_id} v{version}: reused environment source version {source_version} is not indexed")
    prior_stable = [candidate for candidate, entry in versions.items()
                    if entry.get("status") == "stable" and compare_versions(candidate, version) < 0]
    require(prior_stable and source_version == max(prior_stable, key=cmp_to_key(compare_versions)),
            f"{profile_id} v{version}: reused environment must cite the latest earlier stable version")
    source_entry = versions[source_version]
    source_path = source_entry.get("environmentPath")
    require((profile_id, source_version) not in LEGACY_ENVIRONMENT_EXEMPTIONS and source_path,
            f"{profile_id} v{version}: reused environment source has no environment record")
    source_record = json.loads(read(source_path))
    require(source_record.get("status") == "verified" and
            source_record.get("environment") == record.get("environment") and
            source_record.get("runtimeConfiguration") == record.get("runtimeConfiguration"),
            f"{profile_id} v{version}: reused environment must match a verified source snapshot")


def validate_profile_artifacts(profile_id, profile, modules):
    profile_readme = profile["profileReadmePath"]
    require(profile_readme == f"profiles/{profile_id}/README.md", f"{profile_id}: invalid profile README path")
    profile_readme_text = read(profile_readme)
    test_path = f"scripts/test_profile_{profile_id.replace('-', '_')}.py"
    require(profile.get("validationTestPath") == test_path and (ROOT / test_path).is_file(),
            f"{profile_id}: dedicated profile regression test is required at {test_path}")
    environment_records = {}
    for version, entry in profile["versions"].items():
        directory = f"profiles/{profile_id}/versions/v{version}"
        require(entry.get("versionDirectory") == directory, f"{profile_id} v{version}: invalid version directory")
        expected = {
            "modulePath": directory + "/openclash-overwrite.conf",
            "requirementsPath": directory + "/REQUIREMENTS.md",
            "setupPath": directory + "/SETUP.md",
        }
        for key, path in expected.items():
            require(entry.get(key) == path, f"{profile_id} v{version}: invalid {key}")
            read(path)
        module_path = entry["modulePath"]
        require(module_path in modules, f"{profile_id} v{version}: module missing from parsed modules")
        require(entry.get("moduleSha256") == sha(read(module_path)),
                f"{profile_id} v{version}: module hash mismatch")
        requirement_ids = entry.get("requirements", [])
        require(isinstance(requirement_ids, list) and requirement_ids,
                f"{profile_id} v{version}: requirement IDs are required")
        contract = read(entry["requirementsPath"])
        for requirement in requirement_ids:
            require(isinstance(requirement, str) and
                    re.search(rf"(?m)^- {re.escape(requirement)}(?: |：)", contract),
                    f"{profile_id} v{version}: missing requirement {requirement}")
        setup = read(entry["setupPath"])
        require("OpenClash" in setup and "设置" in setup,
                f"{profile_id} v{version}: OpenClash setup guidance is missing")
        if entry["status"] == "candidate":
            require(f"v{version}" in profile_readme_text and "candidate" in profile_readme_text,
                    f"{profile_id} v{version}: candidate must be indexed in its profile README")

        environment_path = entry.get("environmentPath")
        if (profile_id, version) in LEGACY_ENVIRONMENT_EXEMPTIONS:
            require(environment_path is None,
                    f"{profile_id} v{version}: immutable legacy version must not be rewritten")
        else:
            require(environment_path == directory + "/ENVIRONMENT.json",
                    f"{profile_id} v{version}: ENVIRONMENT.json path is required")
            record = json.loads(read(environment_path))
            validate_environment_record(profile_id, version, entry["status"], record)
            environment_records[version] = record

        local_template_path = entry.get("localModuleTemplatePath")
        if local_template_path:
            expected_template = directory + "/local-tiktok-proxy.conf"
            if version in LEGACY_EXAMPLE_TEMPLATE_VERSIONS:
                expected_template += ".example"
            require(local_template_path == expected_template,
                    f"{profile_id} v{version}: invalid local credential template path")
            require(local_template_path in modules,
                    f"{profile_id} v{version}: local template missing from parsed modules")
        additional_direct_rules_path = entry.get("additionalDirectRulesPath")
        if additional_direct_rules_path:
            read(additional_direct_rules_path)

        if entry["status"] == "stable":
            tag = f"{profile_id}-v{version}"
            module_url = ("https://raw.githubusercontent.com/yang137197/openclash-custom-rules/"
                          f"{tag}/{module_path}")
            release_url = f"https://github.com/yang137197/openclash-custom-rules/releases/tag/{tag}"
            require(entry.get("releaseTag") == tag and entry.get("versionedModuleUrl") == module_url and
                    entry.get("releaseUrl") == release_url,
                    f"{profile_id} v{version}: immutable release tag and module links are required")

    for version, record in environment_records.items():
        if record.get("evidence", {}).get("source") == "reused":
            validate_reused_environment_source(profile_id, version, profile, record)

    if profile.get("status") == "stable":
        rolling = f"profiles/{profile_id}/overwrite/openclash-overwrite.conf"
        require(profile.get("latestModulePath") == rolling and rolling in modules,
                f"{profile_id}: stable profile rolling module path is required")
        require(profile.get("latestModuleSha256") == sha(read(rolling)),
                f"{profile_id}: rolling module hash mismatch")


def validate_stable(profile_id, profile, modules, manual):
    version = profile["currentVersion"]
    entry = profile["versions"][version]
    directory = f"profiles/{profile_id}/versions/v{version}"
    require(entry["versionDirectory"] == directory and entry["status"] == "stable", "stable path/status")
    expected_paths = {"modulePath": directory + "/openclash-overwrite.conf",
                      "requirementsPath": directory + "/REQUIREMENTS.md",
                      "setupPath": directory + "/SETUP.md",
                      "localModuleTemplatePath": directory + "/local-tiktok-proxy.conf.example"
                      if version in LEGACY_EXAMPLE_TEMPLATE_VERSIONS
                      else directory + "/local-tiktok-proxy.conf"}
    for key, path in expected_paths.items():
        require(entry[key] == path, f"{profile_id}: invalid {key}")
        read(path)
    rolling = f"profiles/{profile_id}/overwrite/openclash-overwrite.conf"
    require(profile["latestModulePath"] == rolling, f"{profile_id}: invalid rolling path")
    fixed_text = read(entry["modulePath"])
    require(sha(fixed_text) == entry["moduleSha256"], f"{profile_id}: fixed module hash")
    require(profile["latestModuleSha256"] == sha(read(rolling)), f"{profile_id}: rolling module hash")
    require(profile.get("manualRulesPath") in {"rules/manual-direct-isp.yaml", "rules/manual-direct.yaml"},
            "profile manual source path")
    parsed = modules[entry["modulePath"]]
    if entry["manualRulesPath"] == "rules/manual-direct-isp.yaml":
        require(entry.get("manualRuleCount") == 129 and
                entry.get("manualRulesSha256") == sha(read(entry["manualRulesPath"])),
                "historical manual count/hash")
        manual_payload = manual
    else:
        require(entry["manualRulesPath"] == profile.get("manualRulesPath") == "rules/manual-direct.yaml",
                "generated-source stable manual path")
        manual_provider = parsed.get("rule-providers", {}).get("Manual-Direct!")
        require(isinstance(manual_provider, dict) and
                manual_provider.get("type") == "inline" and
                manual_provider.get("behavior") == "classical",
                "generated-source stable inline provider")
        manual_payload = validate_manual_direct_payload(manual_provider.get("payload"))
    require(entry["localProxyName"] == "TikTok-ISP-Local" and entry["tiktokGroup"] == "TikTok-ISP", "local group contract")
    hop = "日本-入口"
    require(entry["firstHopGroup"] == hop and entry["firstHopProvider"] == "iKuuu" and
            entry["foreignGroup"] == "美国", "iKuuu Japan first-hop contract")
    groups = [group(hop, JAPAN_FILTER, "include-all"),
              group("TikTok-ISP", "^TikTok-ISP-Local$", "include-all-proxies"),
              group("美国", USA_FILTER, "include-all")]
    expected = {
        "ipv6": False, "profile": {"store-selected": True, "store-fake-ip": True},
        "dns": expected_dns(), "proxy-groups!": groups,
        "rules!": expected_stable_rules(profile_id, version),
        "rule-providers": {
            "oc-cn-domain": {"type": "http", "behavior": "domain", "format": "mrs", "proxy": "美国",
                             "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/cn.mrs",
                             "path": "./rule_provider/guide-cn.mrs", "interval": 86400},
            "Manual-Direct!": {"type": "inline", "behavior": "classical", "payload": manual_payload},
        },
    }
    require(set(parsed) == set(expected), f"{profile_id}: unexpected cloud keys")
    for key, value in expected.items():
        require(parsed[key] == value, f"{profile_id}: protected {key} changed")
    # v1.0.6's immutable snapshot remains validated above. Once the catalog
    # selects the generated-source architecture, the rolling module is instead
    # checked against the editable source by validate_manual_direct_sync().
    if profile.get("manualRulesPath") == "rules/manual-direct-isp.yaml":
        require(modules[rolling] == parsed,
                f"{profile_id}: legacy rolling module must match the stable snapshot")
    template = {"proxies+": [{"name": "TikTok-ISP-Local", "type": "socks5", "server": "FILL_ME_PROXY_HOST",
                              "port": "FILL_ME_PROXY_PORT", "username": "FILL_ME_USERNAME",
                              "password": "FILL_ME_PASSWORD", "udp": False, "dialer-proxy": hop}]}
    require(modules[entry["localModuleTemplatePath"]] == template, f"{profile_id}: only placeholder local node allowed")
    requirement_ids = [f"J{i}" for i in range(1, 12)]
    require(entry["requirements"], f"{profile_id}: current stable requirement IDs")
    baseline_contract = read(f"profiles/{profile_id}/versions/v1.0.0/REQUIREMENTS.md")
    for requirement in requirement_ids:
        require(re.search(rf"(?m)^- {requirement}(?: |：)", baseline_contract),
                f"{profile_id}: baseline contract missing {requirement}")
    contract = read(entry["requirementsPath"])
    for requirement in entry["requirements"]:
        require(re.search(rf"(?m)^- {requirement}(?: |：)", contract), f"{profile_id}: missing {requirement}")
    if version != "1.0.0":
        require("J1–J11" in contract and "v1.0.0" in contract,
                f"{profile_id}: stable contract must preserve the original baseline reference")
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
    print(f"OK: {profile_id} v{version} stable; mandatory iKuuu hop, routing, {len(manual_payload)} inline rules and placeholders")


def validate_manual_direct_sync(profile, modules):
    source_path = profile.get("manualRulesPath")
    if source_path != "rules/manual-direct.yaml":
        return
    payload = parse_manual_direct_payload(read(source_path))
    rolling_path = profile["latestModulePath"]
    rolling = modules[rolling_path]
    provider = rolling.get("rule-providers", {}).get("Manual-Direct!")
    require(provider == {"type": "inline", "behavior": "classical", "payload": payload},
            "rolling Manual-Direct inline payload must exactly match rules/manual-direct.yaml")
    rules = rolling.get("rules!", [])
    require(rules.count("RULE-SET,Manual-Direct,DIRECT") == 1,
            "rolling module must call the generated Manual-Direct provider exactly once")
    google_index = rules.index("GEOSITE,google,美国")
    manual_index = rules.index("RULE-SET,Manual-Direct,DIRECT")
    china_index = rules.index("RULE-SET,oc-cn-domain,DIRECT")
    require(google_index < manual_index < china_index,
            "generated Manual-Direct provider must stay after Google and before China rules")
    direct_domains = [rule for rule in rules if rule.split(",", 1)[0] in {"DOMAIN", "DOMAIN-SUFFIX"}
                      and rule.endswith(",DIRECT")]
    require(not direct_domains,
            "manual domain DIRECT rules must come only from rules/manual-direct.yaml")


def check_version_progression(base_ref, catalog):
    changelog = read("CHANGELOG.md")
    base_profiles = {}
    if base_ref and set(base_ref) != {"0"}:
        base = json.loads(git("show", f"{base_ref}:profiles/catalog.json"))
        base_profiles = base["profiles"]
    for profile_id, profile in catalog["profiles"].items():
        prior = base_profiles.get(profile_id, {})
        prior_versions = list(prior.get("versions", {}))
        prior_current_version = prior.get("currentVersion")
        validate_version_sequence(profile_id, profile["versions"], prior_versions, changelog,
                                  profile.get("currentVersion"), prior_current_version)
    print("OK: version sequences are monotonic independently for each profile")


def check_history(base_ref, profiles):
    if not base_ref or set(base_ref) == {"0"}:
        print("SKIP: immutable history comparison (no --base-ref)")
        return
    base = json.loads(git("show", f"{base_ref}:profiles/catalog.json"))
    approved = json.loads(git("show", f"{RETIREMENT_BASELINE}:profiles/catalog.json"))
    retired = set(approved["profiles"]) - {JP}
    require(not (retired & set(profiles)), "retired profiles must not be reintroduced")
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
    require(isinstance(catalog.get("profiles"), dict) and catalog["profiles"] and
            catalog.get("currentProfile") in catalog["profiles"],
            "catalog must index one or more profiles and identify a default profile")
    require(catalog["profiles"][catalog["currentProfile"]]["status"] == "stable",
            "catalog default profile must be stable")
    require(not (ROOT / "overwrite/openclash-overwrite.conf").exists(), "retired compatibility entry remains")
    require(read("AGENTS.md").startswith(ROLE_PREFIX), "immutable expert role/guide changed")
    for path in ("AGENTS.md", "MAINTENANCE.md"):
        require(VERSION_POLICY_TEXT in read(path), f"{path}: immutable version policy changed or removed")
    require("DEVELOPMENT_RULES.md" in read("AGENTS.md") and
            "DEVELOPMENT_RULES.md" in read("README.md"),
            "cross-tool development workflow must be discoverable from AGENTS.md and README.md")
    require("请你先读取仓库，我们继续开发" in read("DEVELOPMENT_RULES.md") and
            "请你先读取仓库，我们继续开发" in read("README.md"),
            "tool-agnostic repository handoff prompt must be documented")
    validate_no_raw_debug_logs()
    manual = load_yaml(read("rules/manual-direct-isp.yaml"))["payload"]
    parse_manual_direct_payload(read("rules/manual-direct.yaml"))
    require(all(rule.startswith("DOMAIN-SUFFIX,") for rule in manual), "manual domains must include subdomains")
    modules = {}
    for path in ROOT.glob("profiles/**/*.conf*"):
        relative = path.relative_to(ROOT).as_posix()
        content = read(relative)
        require("uci set " not in content.lower(), f"{relative}: plugin mutation not allowed")
        modules[relative] = load_yaml(content, module=True)
    expected_modules = set()
    for profile in catalog["profiles"].values():
        if profile["status"] == "stable":
            expected_modules.add(profile["latestModulePath"])
        for version_entry in profile["versions"].values():
            expected_modules.update(version_entry[key] for key in ("modulePath", "localModuleTemplatePath")
                                    if key in version_entry)
    require(set(modules) == expected_modules, "module files must match the version catalog")
    for profile_id, profile in catalog["profiles"].items():
        validate_version_catalog(profile_id, profile, read("CHANGELOG.md"))
        validate_profile_artifacts(profile_id, profile, modules)
        validate_manual_direct_sync(profile, modules)
        if profile_id == JP and profile["status"] == "stable":
            validate_stable(profile_id, profile, modules, manual)
    for path in ("README.md", "AGENTS.md", "MAINTENANCE.md", "CHANGELOG.md"):
        content = read(path)
        for profile_id in catalog["profiles"]:
            require(profile_id in content, f"{path}: missing indexed profile {profile_id}")
            if path == "README.md":
                profile = catalog["profiles"][profile_id]
                current_version = profile["currentVersion"]
                require(f"v{current_version}" in content and profile["status"] in content,
                        f"README.md: missing current version/status for {profile_id}")
                if profile["status"] == "stable":
                    entry = profile["versions"][current_version]
                    require(entry["releaseUrl"] in content and entry["versionedModuleUrl"] in content,
                            f"README.md: missing fixed release links for {profile_id} v{current_version}")
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
