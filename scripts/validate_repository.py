#!/usr/bin/env python3
"""Validate YAML syntax, version mapping and protected OpenClash invariants."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

parser = ArgumentParser()
parser.add_argument(
    "--base-ref",
    help="Optional git base revision used to reject edits to published versions",
)
args = parser.parse_args()


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        fail(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


try:
    from strict_yaml import load_yaml
except ImportError:
    fail("install validation dependencies: python -m pip install -r scripts/requirements-validation.txt")

parsed_modules = {}
for path in sorted(set(ROOT.glob("profiles/**/*.conf*")) | set(ROOT.glob("overwrite/*.conf"))):
    relative = path.relative_to(ROOT).as_posix()
    try:
        parsed_modules[relative] = load_yaml(read_text(relative), module=True)
    except ValueError as error:
        fail(f"{relative}: {error}")
for path in sorted(ROOT.glob("rules/*.yaml")):
    relative = path.relative_to(ROOT).as_posix()
    try:
        load_yaml(read_text(relative))
    except ValueError as error:
        fail(f"{relative}: {error}")
print(f"OK: strict YAML parsing of {len(parsed_modules)} modules; duplicate mapping keys rejected")


catalog_path = ROOT / "profiles" / "catalog.json"
if not catalog_path.is_file():
    fail("missing profiles/catalog.json")

catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
profile_id = catalog.get("currentProfile")
profiles = catalog.get("profiles", {})
if profile_id not in profiles:
    fail("currentProfile is not present in profiles")

profile = profiles[profile_id]
if profile.get("status") != "stable":
    fail("current profile must be stable")

version = profile.get("currentVersion")
if catalog.get("tagConvention") != "{profileId}-v{version}":
    fail("tagConvention must keep profile tags independent")

expected_tag = (
    f"v{version}"
    if profile.get("legacyTag") is True
    else f"{profile_id}-v{version}"
)
if profile.get("tag") != expected_tag:
    fail(f"tag must be profile-specific; expected {expected_tag}")

requirements = profile.get("requirements", [])
baseline_requirements = [f"R{number}" for number in range(1, 9)]
if requirements[:8] != baseline_requirements:
    fail("current profile must preserve the R1-R8 stable baseline")

module_text = read_text(profile["modulePath"])
compatibility_text = read_text(profile["compatibilityModulePath"])
manual_rules_text = read_text(profile["sharedManualRulesPath"])
requirements_text = read_text(profile["requirementsPath"])
profile_readme_text = read_text(profile["profileReadmePath"])

if module_text != compatibility_text:
    fail("compatibility overwrite differs from the current stable version module")

if sha256(module_text) != profile.get("moduleSha256"):
    fail("current stable module hash differs from catalog")

if sha256(manual_rules_text) != profile.get("manualRulesSha256"):
    fail("manual-direct rules changed without a version/catalog update")

section_headers = [
    line.strip()
    for line in module_text.splitlines()
    if re.fullmatch(r"\[[^\]]+\]", line.strip())
]
if section_headers != ["[YAML]"]:
    fail(
        "overwrite must contain exactly one section header, [YAML]; "
        f"found: {section_headers}"
    )

module_lines = module_text.splitlines()
yaml_header_index = module_lines.index("[YAML]")
unexpected_prefix_lines = [
    line
    for line in module_lines[:yaml_header_index]
    if line.strip() and not line.lstrip().startswith("#")
]
if unexpected_prefix_lines:
    fail("only comments are allowed before [YAML]")

for forbidden_text in [
    "uci set ",
    "uci -q set ",
    "openclash.config.",
    "overwrite_restart_flag",
]:
    if forbidden_text in module_text.lower():
        fail(f"overwrite contains forbidden OpenClash setting text: {forbidden_text}")

legacy_required_module_fragments = [
    "'geosite:tiktok': rcode://success",
    "GEOSITE,tiktok,REJECT",
    "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,美国",
    "GEOSITE,google,美国",
    "RULE-SET,Manual-Direct,DIRECT",
    "GEOSITE,cn,DIRECT",
    "GEOIP,CN,DIRECT,no-resolve",
    "MATCH,美国",
    "empty-fallback: REJECT",
]
required_module_fragments = list(legacy_required_module_fragments)
if profile.get("kind") == "guide-mainland-bypass":
    required_module_fragments.remove("GEOSITE,cn,DIRECT")
    required_module_fragments.append("RULE-SET,oc-cn-domain,DIRECT")
for fragment in required_module_fragments:
    if fragment not in module_text:
        fail(f"missing protected module fragment: {fragment}")

ordered_rules = [
    "GEOSITE,tiktok,REJECT",
    "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,美国",
    "GEOSITE,google,美国",
    "RULE-SET,Manual-Direct,DIRECT",
    "GEOSITE,cn,DIRECT",
    "GEOIP,CN,DIRECT,no-resolve",
    "MATCH,美国",
]
if profile.get("kind") == "guide-mainland-bypass":
    ordered_rules[4] = "RULE-SET,oc-cn-domain,DIRECT"
positions = [module_text.index(rule) for rule in ordered_rules]
if positions != sorted(positions):
    fail("protected routing order changed")

if module_text.count("'geosite:google':") != 1:
    fail("geosite:google DNS policy must be one independent key")
if module_text.count("'+.xn--ngstr-lra8j.com':") != 1:
    fail("Google Play download DNS policy must be one independent key")

manual_entries = [
    line.strip()
    for line in manual_rules_text.splitlines()
    if line.lstrip().startswith("- ")
]
if len(manual_entries) != profile.get("manualRuleCount"):
    fail("manual-direct entry count changed without a new version")

for requirement in requirements:
    if requirement not in requirements_text:
        fail(f"version requirements file does not mention {requirement}")

version_marker = f"v{version}"
for relative_path, text in [
    ("README.md", read_text("README.md")),
    ("AGENTS.md", read_text("AGENTS.md")),
    ("CHANGELOG.md", read_text("CHANGELOG.md")),
    (profile["profileReadmePath"], profile_readme_text),
]:
    if version_marker not in text:
        fail(f"{relative_path} does not mention current version {version_marker}")

version_directory = (ROOT / profile["versionDirectory"]).resolve()
if (ROOT / profile["modulePath"]).resolve().parent != version_directory:
    fail("modulePath is outside the declared versionDirectory")
if (ROOT / profile["requirementsPath"]).resolve().parent != version_directory:
    fail("requirementsPath is outside the declared versionDirectory")

immutable_version_directories = profile.get("immutableVersionDirectories", [])
if profile["versionDirectory"] not in immutable_version_directories:
    fail("current stable version directory must be immutable")

candidate_versions = profile.get("candidateVersions", {})
if not isinstance(candidate_versions, dict):
    fail("candidateVersions must be an object")


def validate_guide_version(candidate_version: str, candidate: dict) -> None:
    """Validate the v2 DNS/firewall contract for a candidate or stable version."""
    if candidate_version != "2.0.0":
        fail("guide-mainland-bypass requires an explicitly reviewed major version")
    declared = baseline_requirements + ["R11", "R12"]
    if candidate.get("requirements") != declared:
        fail("guide candidate must declare R1-R8 and R11-R12")
    module = read_text(candidate["modulePath"])
    contract = read_text(candidate["requirementsPath"])
    setup = read_text(candidate["setupPath"])
    if sha256(module) != candidate.get("moduleSha256"):
        fail("guide candidate module hash differs from catalog")
    if candidate.get("sharedManualRulesPath") != profile["sharedManualRulesPath"]:
        fail("guide candidate must reuse the unchanged manual-direct source")
    if candidate.get("manualRulesSha256") != sha256(manual_rules_text):
        fail("guide candidate manual-direct snapshot differs from catalog")
    if candidate.get("manualRuleCount") != len(manual_entries):
        fail("guide candidate manual-direct count differs from catalog")
    if any(not re.fullmatch(r"- DOMAIN(?:-SUFFIX)?,[^,\s]+", entry)
           for entry in manual_entries):
        fail("manual-direct must remain domain-only for v2 Fake-IP rule filtering")
    headers = re.findall(r"^\[[^\]]+\]$", module, re.MULTILINE)
    if headers != ["[YAML]"]:
        fail("guide candidate must contain exactly [YAML]")
    prefix = module.split("[YAML]", 1)[0]
    if any(line.strip() and not line.lstrip().startswith("#")
           for line in prefix.splitlines()):
        fail("guide candidate permits only comments before [YAML]")
    for forbidden in ("uci set ", "uci -q set ", "openclash.config.",
                      "overwrite_restart_flag", "- name: 日本", "SRC-IP-CIDR,"):
        if forbidden.lower() in module.lower():
            fail(f"guide candidate contains forbidden fragment: {forbidden}")
    # Each DNS override owns its value; a merged hash must not retain old policies.
    for fragment in (
        "fake-ip-filter-mode: rule", "fake-ip-filter!:", "fallback!: []",
        "fallback-filter-:", "nameserver-policy!:",
        "proxy-server-nameserver-policy!: {}", "proxy-server-nameserver:",
        "direct-nameserver-follow-policy: false", "respect-rules: true",
        "'geosite:tiktok': rcode://success", "'geosite:google':",
        "'+.xn--ngstr-lra8j.com':", "https://223.5.5.5/dns-query",
        "https://1.12.12.12/dns-query", "'https://1.1.1.1/dns-query#美国'",
        "'https://8.8.8.8/dns-query#美国'", "behavior: domain", "format: mrs",
        "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/cn.mrs",
        "/main/rules/manual-direct.yaml", "behavior: classical",
        "empty-fallback: REJECT", "exclude-filter: '(?i)^IPRoyal-'",
    ):
        if fragment not in module:
            fail(f"guide candidate is missing protected fragment: {fragment}")
    filter_block = module.split("  fake-ip-filter!:\n", 1)[1].split("\nproxy-groups!:", 1)[0]
    filter_rules = re.findall(r"^    - (.+)$", filter_block, re.MULTILINE)
    expected_filter = [
        "GEOSITE,tiktok,fake-ip",
        "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,fake-ip",
        "GEOSITE,google,fake-ip",
        "DOMAIN,localhost,real-ip", "DOMAIN-SUFFIX,lan,real-ip",
        "DOMAIN-SUFFIX,local,real-ip", "DOMAIN-SUFFIX,home.arpa,real-ip",
        "GEOSITE,private,real-ip", "RULE-SET,Manual-Direct,real-ip",
        "RULE-SET,oc-cn-domain,real-ip", "MATCH,fake-ip",
    ]
    if filter_rules != expected_filter:
        fail("guide candidate must protect Google/TikTok before CN real-IP bypass")
    routing = module.split("\nrules!:\n", 1)[1]
    expected_order = [
        "GEOSITE,private,DIRECT", "GEOSITE,tiktok,REJECT",
        "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,美国", "GEOSITE,google,美国",
        "RULE-SET,Manual-Direct,DIRECT", "RULE-SET,oc-cn-domain,DIRECT",
        "GEOIP,CN,DIRECT,no-resolve", "MATCH,美国",
    ]
    if any(rule not in routing for rule in expected_order):
        fail("guide candidate routing contract is incomplete")
    if [routing.index(rule) for rule in expected_order] != sorted(
        routing.index(rule) for rule in expected_order
    ):
        fail("guide candidate routing priority differs from its contract")
    directory = (ROOT / candidate["versionDirectory"]).resolve()
    for key in ("modulePath", "requirementsPath", "setupPath"):
        if (ROOT / candidate[key]).resolve().parent != directory:
            fail(f"guide candidate {key} is outside its versionDirectory")
    if any(requirement not in contract for requirement in declared):
        fail("guide candidate contract omits a declared requirement")
    for path in ("README.md", "AGENTS.md", "CHANGELOG.md", profile["profileReadmePath"]):
        if "v2.0.0" not in read_text(path):
            fail(f"{path} does not document the guide candidate")
    for fragment in ("绕过中国大陆", "cn.mrs", "规则（rule）", "Dnsmasq 转发",
                     "回退", "alpha-gbc76c13"):
        if fragment not in setup + contract:
            fail(f"guide candidate documentation omits {fragment}")


if profile.get("kind") == "guide-mainland-bypass":
    validate_guide_version(version, profile)
    if profile.get("candidateVersions", {}).get(version):
        fail("current stable guide version must not remain a candidate")
    if profile.get("acceptanceSource") != "user-confirmed" or not profile.get("acceptedAt"):
        fail("stable guide version must record user confirmation and date")


for candidate_version, candidate in candidate_versions.items():
    if candidate.get("status") != "candidate":
        fail(f"v{candidate_version} candidate must have status=candidate")

    if candidate.get("kind") == "guide-mainland-bypass":
        validate_guide_version(candidate_version, candidate)
        continue

    candidate_requirements = candidate.get("requirements", [])
    expected_candidate_requirements = [f"R{number}" for number in range(1, 11)]
    if candidate_requirements != expected_candidate_requirements:
        fail(f"v{candidate_version} must preserve R1-R8 and add R9-R10")

    candidate_module_text = read_text(candidate["modulePath"])
    candidate_requirements_text = read_text(candidate["requirementsPath"])
    manual_japan_text = read_text(candidate["manualJapanRulesPath"])

    if sha256(candidate_module_text) != candidate.get("moduleSha256"):
        fail(f"v{candidate_version} candidate module hash differs from catalog")
    if sha256(manual_japan_text) != candidate.get("manualJapanRulesSha256"):
        fail("manual-japan rules changed without a candidate/catalog update")

    candidate_headers = [
        line.strip()
        for line in candidate_module_text.splitlines()
        if re.fullmatch(r"\[[^\]]+\]", line.strip())
    ]
    if candidate_headers != ["[YAML]"]:
        fail(
            f"v{candidate_version} overwrite must contain exactly [YAML]; "
            f"found: {candidate_headers}"
        )

    candidate_lines = candidate_module_text.splitlines()
    candidate_yaml_index = candidate_lines.index("[YAML]")
    candidate_unexpected_prefix = [
        line
        for line in candidate_lines[:candidate_yaml_index]
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if candidate_unexpected_prefix:
        fail(f"v{candidate_version} allows only comments before [YAML]")

    for forbidden_text in [
        "uci set ",
        "uci -q set ",
        "openclash.config.",
        "overwrite_restart_flag",
    ]:
        if forbidden_text in candidate_module_text.lower():
            fail(
                f"v{candidate_version} overwrite contains forbidden text: "
                f"{forbidden_text}"
            )

    candidate_required_fragments = legacy_required_module_fragments + [
        "- name: 日本",
        "RULE-SET,Manual-Japan,日本",
        "/main/rules/manual-japan.yaml",
        "./rule_provider/manual-japan.yaml",
    ]
    for fragment in candidate_required_fragments:
        if fragment not in candidate_module_text:
            fail(f"v{candidate_version} is missing protected fragment: {fragment}")

    candidate_ordered_rules = [
        "GEOSITE,tiktok,REJECT",
        "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,美国",
        "GEOSITE,google,美国",
        "RULE-SET,Manual-Japan,日本",
        "RULE-SET,Manual-Direct,DIRECT",
        "GEOSITE,cn,DIRECT",
        "GEOIP,CN,DIRECT,no-resolve",
        "MATCH,美国",
    ]
    candidate_positions = [
        candidate_module_text.index(rule) for rule in candidate_ordered_rules
    ]
    if candidate_positions != sorted(candidate_positions):
        fail(f"v{candidate_version} protected routing order changed")

    if candidate_module_text.count("'geosite:google':") != 1:
        fail(f"v{candidate_version} must keep one independent Google DNS key")
    if candidate_module_text.count("'+.xn--ngstr-lra8j.com':") != 1:
        fail(f"v{candidate_version} must keep one independent Google Play DNS key")
    if candidate_module_text.count("empty-fallback: REJECT") != 2:
        fail(f"v{candidate_version} US and Japan groups must both fail closed")
    if candidate_module_text.count("exclude-filter: '(?i)^IPRoyal-'") != 2:
        fail(f"v{candidate_version} US and Japan groups must exclude IPRoyal")

    manual_japan_entries = [
        line.strip()
        for line in manual_japan_text.splitlines()
        if line.lstrip().startswith("- ")
    ]
    expected_japan_entries = [
        "- DOMAIN,t27.cdn2020.com",
        "- DOMAIN-SUFFIX,hscangku.com",
        "- DOMAIN,222.0cck.cc",
        "- DOMAIN-SUFFIX,51cg1.com",
        "- DOMAIN,tx.doudou520.online",
        "- DOMAIN,mts.hhjd.mobi",
    ]
    if manual_japan_entries != expected_japan_entries:
        fail("manual-japan rules differ from the approved domain set")
    if len(manual_japan_entries) != candidate.get("manualJapanRuleCount"):
        fail("manual-japan entry count differs from catalog")

    for requirement in candidate_requirements:
        if requirement not in candidate_requirements_text:
            fail(
                f"v{candidate_version} requirements file does not mention {requirement}"
            )

    candidate_directory = (ROOT / candidate["versionDirectory"]).resolve()
    if (ROOT / candidate["modulePath"]).resolve().parent != candidate_directory:
        fail(f"v{candidate_version} modulePath is outside its versionDirectory")
    if (ROOT / candidate["requirementsPath"]).resolve().parent != candidate_directory:
        fail(f"v{candidate_version} requirementsPath is outside its versionDirectory")

    candidate_marker = f"v{candidate_version}"
    for relative_path, text in [
        ("README.md", read_text("README.md")),
        ("AGENTS.md", read_text("AGENTS.md")),
        ("CHANGELOG.md", read_text("CHANGELOG.md")),
        (profile["profileReadmePath"], profile_readme_text),
    ]:
        if candidate_marker not in text:
            fail(f"{relative_path} does not mention candidate {candidate_marker}")

hybrid_profile_id = "tiktok-hybrid-device-us"
hybrid_profile = profiles.get(hybrid_profile_id)
if not isinstance(hybrid_profile, dict):
    fail(f"missing stable profile: {hybrid_profile_id}")
if hybrid_profile.get("status") != "stable":
    fail(f"{hybrid_profile_id} must be stable after device acceptance")
if hybrid_profile.get("currentVersion") != "1.0.1":
    fail(f"{hybrid_profile_id} currentVersion must be 1.0.1")
if hybrid_profile.get("tag") != "tiktok-hybrid-device-us-v1.0.1":
    fail(f"{hybrid_profile_id} stable tag differs from the profile tag convention")
if hybrid_profile.get("legacyTag") is not False:
    fail(f"{hybrid_profile_id} must use the profile-specific tag convention")

hybrid_requirements = hybrid_profile.get("requirements", [])
expected_hybrid_requirements = [f"H{number}" for number in range(1, 10)]
if hybrid_requirements != expected_hybrid_requirements:
    fail(f"{hybrid_profile_id} must declare H1-H9")
if hybrid_profile.get("authorizedTikTokUsDevices") != ["192.168.100.198/32"]:
    fail(f"{hybrid_profile_id} authorized device list changed without a new version")

hybrid_module_text = read_text(hybrid_profile["modulePath"])
hybrid_requirements_text = read_text(hybrid_profile["requirementsPath"])
hybrid_readme_text = read_text(hybrid_profile["profileReadmePath"])

if sha256(hybrid_module_text) != hybrid_profile.get("moduleSha256"):
    fail(f"{hybrid_profile_id} stable module hash differs from catalog")

hybrid_headers = [
    line.strip()
    for line in hybrid_module_text.splitlines()
    if re.fullmatch(r"\[[^\]]+\]", line.strip())
]
if hybrid_headers != ["[YAML]"]:
    fail(f"{hybrid_profile_id} overwrite must contain exactly [YAML]")

hybrid_lines = hybrid_module_text.splitlines()
hybrid_yaml_index = hybrid_lines.index("[YAML]")
hybrid_unexpected_prefix = [
    line
    for line in hybrid_lines[:hybrid_yaml_index]
    if line.strip() and not line.lstrip().startswith("#")
]
if hybrid_unexpected_prefix:
    fail(f"{hybrid_profile_id} allows only comments before [YAML]")

for forbidden_text in [
    "uci set ",
    "uci -q set ",
    "openclash.config.",
    "overwrite_restart_flag",
]:
    if forbidden_text in hybrid_module_text.lower():
        fail(f"{hybrid_profile_id} overwrite contains forbidden text: {forbidden_text}")

hybrid_device_rule = (
    "AND,((SRC-IP-CIDR,192.168.100.198/32),(GEOSITE,tiktok)),美国"
)
hybrid_required_fragments = [
    "'geosite:tiktok':",
    "'https://1.1.1.1/dns-query#美国'",
    hybrid_device_rule,
    "GEOSITE,tiktok,REJECT",
    "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,美国",
    "GEOSITE,google,美国",
    "RULE-SET,Manual-Direct,DIRECT",
    "GEOSITE,cn,DIRECT",
    "GEOIP,CN,DIRECT,no-resolve",
    "MATCH,美国",
    "empty-fallback: REJECT",
]
for fragment in hybrid_required_fragments:
    if fragment not in hybrid_module_text:
        fail(f"{hybrid_profile_id} is missing protected fragment: {fragment}")
if "SRC-IP-CIDR,192.168.100.248/32" in hybrid_module_text:
    fail(f"{hybrid_profile_id} v1.0.1 must remove the old .248 authorization")
if "'geosite:tiktok': rcode://success" in hybrid_module_text:
    fail(f"{hybrid_profile_id} cannot return empty TikTok DNS to the allowed device")
if "RULE-SET,Manual-Japan,日本" in hybrid_module_text or "- name: 日本" in hybrid_module_text:
    fail(f"{hybrid_profile_id} must not silently inherit the unverified Japan candidate")

hybrid_ordered_rules = [
    hybrid_device_rule,
    "GEOSITE,tiktok,REJECT",
    "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,美国",
    "GEOSITE,google,美国",
    "RULE-SET,Manual-Direct,DIRECT",
    "GEOSITE,cn,DIRECT",
    "GEOIP,CN,DIRECT,no-resolve",
    "MATCH,美国",
]
hybrid_positions = [
    hybrid_module_text.index(rule) for rule in hybrid_ordered_rules
]
if hybrid_positions != sorted(hybrid_positions):
    fail(f"{hybrid_profile_id} protected routing order changed")

if hybrid_module_text.count("'geosite:google':") != 1:
    fail(f"{hybrid_profile_id} must keep one independent Google DNS key")
if hybrid_module_text.count("'+.xn--ngstr-lra8j.com':") != 1:
    fail(f"{hybrid_profile_id} must keep one independent Google Play DNS key")
if hybrid_module_text.count("exclude-filter: '(?i)^IPRoyal-'") != 1:
    fail(f"{hybrid_profile_id} US group must exclude IPRoyal")

for requirement in hybrid_requirements:
    if requirement not in hybrid_requirements_text:
        fail(f"{hybrid_profile_id} requirements file does not mention {requirement}")

hybrid_directory = (ROOT / hybrid_profile["versionDirectory"]).resolve()
if (ROOT / hybrid_profile["modulePath"]).resolve().parent != hybrid_directory:
    fail(f"{hybrid_profile_id} modulePath is outside its versionDirectory")
if (ROOT / hybrid_profile["requirementsPath"]).resolve().parent != hybrid_directory:
    fail(f"{hybrid_profile_id} requirementsPath is outside its versionDirectory")
if hybrid_profile.get("immutableVersionDirectories") != [
    "profiles/tiktok-hybrid-device-us/versions/v1.0.0",
    "profiles/tiktok-hybrid-device-us/versions/v1.0.1",
]:
    fail(f"{hybrid_profile_id} published version directories must be immutable")

for relative_path, text in [
    ("README.md", read_text("README.md")),
    ("AGENTS.md", read_text("AGENTS.md")),
    ("CHANGELOG.md", read_text("CHANGELOG.md")),
    (hybrid_profile["profileReadmePath"], hybrid_readme_text),
]:
    if (
        hybrid_profile_id not in text
        or "v1.0.1" not in text
        or "192.168.100.198" not in text
    ):
        fail(f"{relative_path} does not document stable {hybrid_profile_id} v1.0.1")

hybrid_candidates = hybrid_profile.get("candidateVersions", {})
if hybrid_candidates:
    fail(f"{hybrid_profile_id} must not retain v1.0.1 as a candidate after release")

# The router-hosted profile is independent of the published phone/VPN contracts.
router_id = "tiktok-router-iproyal-us"
router_profile = profiles.get(router_id, {})
if catalog.get("developmentProfile") not in {"tiktok-router-isp-us", "tiktok-router-loongproxy-jp-us"}:
    fail("developmentProfile must identify the current local ISP TikTok candidate")
if router_profile.get("status") != "deprecated" or router_profile.get("currentVersion") is not None:
    fail("superseded IPRoyal router profile must stay deprecated and non-current")
if router_profile.get("tag") or router_profile.get("compatibilityModulePath"):
    fail("router candidate must not claim a stable tag or compatibility entry")
beta1_directory = f"profiles/{router_id}/versions/v1.0.2-beta.1"
beta2_directory = f"profiles/{router_id}/versions/v1.0.2-beta.2"
beta3_directory = f"profiles/{router_id}/versions/v1.0.2-beta.3"
if router_profile.get("immutableVersionDirectories") != [beta1_directory, beta2_directory, beta3_directory]:
    fail("router profile must preserve all published beta snapshots")
if router_profile.get("sharedManualRulesPath") != "rules/manual-direct.yaml":
    fail("router profile must preserve the shared manual-direct source")
router_candidates = router_profile.get("candidateVersions", {})
if set(router_candidates) != {"1.0.0", "1.0.1", "1.0.2-beta.1", "1.0.2-beta.2", "1.0.2-beta.3"}:
    fail("router profile must retain prior candidates and declare beta.3")
latest_module_path = "profiles/tiktok-router-iproyal-us/overwrite/openclash-overwrite.conf"
if router_profile.get("latestModulePath") != latest_module_path:
    fail("router profile must expose its scheme-specific rolling subscription module")
latest_module_text = read_text(latest_module_path)
if sha256(latest_module_text) != router_profile.get("latestModuleSha256"):
    fail("router rolling module hash differs from catalog")
router = router_candidates["1.0.0"]
if router.get("status") != "candidate" or router.get("kind") != "router-iproyal":
    fail("router candidate kind/status differ from the authorized contract")
if router.get("requirements") != [f"P{i}" for i in range(1, 10)]:
    fail("router candidate must declare P1-P9")
if router.get("localProxyName") != "IPRoyal-US-ISP" or router.get("tiktokGroup") != "TikTok-ISP":
    fail("router candidate local node/group identity changed")
router_directory = f"profiles/{router_id}/versions/v1.0.0"
if router.get("versionDirectory") != router_directory:
    fail("router candidate version directory is not independent")
for key, filename in (("modulePath", "openclash-overwrite.conf"),
                      ("requirementsPath", "REQUIREMENTS.md"), ("setupPath", "SETUP.md")):
    if router.get(key) != f"{router_directory}/{filename}":
        fail(f"router {key} must stay in its independent version directory")
router_module = read_text(router["modulePath"])
if sha256(router_module) != router.get("moduleSha256"):
    fail("router candidate module hash differs from catalog")
if router.get("manualRulesSha256") != sha256(manual_rules_text) or router.get("manualRuleCount") != len(manual_entries):
    fail("router candidate manual-direct snapshot differs from the shared list")


def config_body(text: str) -> str:
    """Ignore comments only; preserve the full YAML/operator contract."""
    return "\n".join(line for line in text.splitlines()
                     if line.strip() and not line.lstrip().startswith("#"))


# Exactly three behavioral changes from the immutable guide baseline. Comparing
# the full body also prevents credentials, extra routes or fallback groups from
# being hidden beside the expected fragments, even after a hash is refreshed.
router_expected = read_text("profiles/tiktok-sockstun-us/versions/v2.0.0/openclash-overwrite.conf")
router_expected = router_expected.replace(
    "    'geosite:tiktok': rcode://success",
    "    'geosite:tiktok':\n      - 'https://1.1.1.1/dns-query#TikTok-ISP'\n"
    "      - 'https://8.8.8.8/dns-query#TikTok-ISP'",
).replace(
    "proxy-groups!:\n",
    "proxy-groups!:\n  - name: TikTok-ISP\n    type: select\n"
    "    include-all-proxies: true\n    filter: '^IPRoyal-US-ISP$'\n"
    "    empty-fallback: REJECT\n",
).replace(
    "  - GEOSITE,tiktok,REJECT",
    "  - GEOSITE,tiktok,TikTok-ISP\n  - GEOSITE,tiktok,REJECT",
)
if config_body(router_module) != config_body(router_expected):
    fail("router candidate changed protected guide baseline or TikTok fail-closed contract")
router_contract = read_text(router["requirementsPath"])
router_setup = read_text(router["setupPath"])
if any(item not in router_contract for item in router["requirements"]):
    fail("router contract omits declared requirements")
for marker in ("无需 SocksTun", "proxies+", "dialer-proxy: DIRECT", "udp: false",
               "重启 OpenClash", "Dnsmasq 转发", "订阅", "回退"):
    if marker not in router_setup:
        fail(f"router setup omits {marker}")
for doc in ("README.md", "AGENTS.md", "CHANGELOG.md", router_profile["profileReadmePath"]):
    if router_id not in read_text(doc):
        fail(f"{doc} does not identify the deprecated router IPRoyal profile")
if "已弃用" not in read_text(router_profile["profileReadmePath"]):
    fail("router IPRoyal README must clearly mark the old candidate deprecated")
print("OK: router IPRoyal historical snapshots preserved and profile deprecated")

router_chain = router_candidates["1.0.1"]
chain_directory = f"profiles/{router_id}/versions/v1.0.1"
if router_chain.get("status") != "candidate" or router_chain.get("kind") != "router-iproyal":
    fail("router chain candidate must remain unpublished")
if router_chain.get("requirements") != [f"P{i}" for i in range(1, 11)]:
    fail("router chain candidate must declare P1-P10")
if router_chain.get("versionDirectory") != chain_directory:
    fail("router chain candidate must have its own version directory")
for key, filename in (("modulePath", "openclash-overwrite.conf"),
                      ("requirementsPath", "REQUIREMENTS.md"),
                      ("setupPath", "SETUP.md"),
                      ("chainPatchPath", "iproyal-chain-hop.conf")):
    if router_chain.get(key) != f"{chain_directory}/{filename}":
        fail(f"router chain {key} must stay in its version directory")
if router_chain.get("localProxyName") != "IPRoyal-US-ISP" or router_chain.get("tiktokGroup") != "TikTok-ISP":
    fail("router chain node/group identity changed")
chain_module = read_text(router_chain["modulePath"])
chain_patch = read_text(router_chain["chainPatchPath"])
chain_contract = read_text(router_chain["requirementsPath"])
chain_setup = read_text(router_chain["setupPath"])
if sha256(chain_module) != router_chain.get("moduleSha256"):
    fail("router chain complete module hash differs from catalog")
if sha256(chain_patch) != router_chain.get("chainPatchSha256"):
    fail("router chain patch hash differs from catalog")
if config_body(chain_module) != config_body(router_module):
    fail("router chain candidate must preserve the complete routing/DNS module")
expected_chain_patch = (
    "[YAML]\nproxies*:\n  where:\n    name: IPRoyal-US-ISP\n"
    "  set:\n    dialer-proxy: 美国\n"
)
if chain_patch != expected_chain_patch:
    fail("router chain patch must only update the existing exact local node")
if router_chain.get("manualRulesSha256") != sha256(manual_rules_text) or router_chain.get("manualRuleCount") != len(manual_entries):
    fail("router chain candidate changed shared manual-direct snapshot")
if any(item not in chain_contract for item in router_chain["requirements"]):
    fail("router chain contract omits a declared requirement")
for marker in ("v1.0.1", "候选", "上方", "重启 OpenClash", "IPRoyal", "回退"):
    if marker not in chain_setup:
        fail(f"router chain setup omits {marker}")
print("OK: router IPRoyal v1.0.1 candidate; exact chain patch only, no credentials")

router_beta1 = router_candidates["1.0.2-beta.1"]
if router_beta1.get("status") != "candidate" or router_beta1.get("kind") != "router-iproyal":
    fail("router beta candidate must remain unpublished as stable")
if router_beta1.get("tag") != "tiktok-router-iproyal-us-v1.0.2-beta.1" or router_beta1.get("releaseType") != "pre-release":
    fail("router beta.1 tag must remain an explicitly marked prerelease")
if router_beta1.get("requirements") != [f"P{i}" for i in range(1, 11)]:
    fail("router beta.1 candidate must declare P1-P10")
if router_beta1.get("versionDirectory") != beta1_directory:
    fail("router beta.1 candidate must retain its original version directory")
for key, filename in (("modulePath", "openclash-overwrite.conf"),
                      ("requirementsPath", "REQUIREMENTS.md"),
                      ("setupPath", "SETUP.md"),
                      ("chainPatchPath", "iproyal-chain-hop.conf")):
    if router_beta1.get(key) != f"{beta1_directory}/{filename}":
        fail(f"router beta.1 {key} must stay in its original version directory")
if router_beta1.get("localProxyName") != "IPRoyal-US-ISP" or router_beta1.get("tiktokGroup") != "TikTok-ISP":
    fail("router beta.1 node/group identity changed")
beta1_module = read_text(router_beta1["modulePath"])
beta1_patch = read_text(router_beta1["chainPatchPath"])
beta1_contract = read_text(router_beta1["requirementsPath"])
beta1_setup = read_text(router_beta1["setupPath"])
if sha256(beta1_module) != router_beta1.get("moduleSha256"):
    fail("router beta.1 module hash differs from catalog")
if sha256(beta1_patch) != router_beta1.get("chainPatchSha256"):
    fail("router beta.1 patch hash differs from catalog")
if config_body(beta1_module) != config_body(chain_module):
    fail("router beta.1 must preserve the v1.0.1 routing/DNS module body")
if beta1_patch != expected_chain_patch:
    fail("router beta.1 patch must only update the existing exact local node")
if router_beta1.get("manualRulesSha256") != "49ef958515dab7ed19d4736ca36ad8dcf070bcc1d04fe917d535ea45da8666da" or router_beta1.get("manualRuleCount") != 129:
    fail("router beta.1 must retain the original tagged Manual-Direct snapshot metadata")
if "DOMAIN,d-gm.mmstat.com" not in beta1_contract:
    fail("router beta.1 requirements must preserve its original exact d-gm rule contract")
if any(item not in beta1_contract for item in router_beta1["requirements"]):
    fail("router beta.1 contract omits a declared requirement")
for marker in ("v1.0.2-beta.1", "beta", "d-gm.mmstat.com", "重启 OpenClash", "DIRECT", "回退"):
    if marker not in beta1_setup:
        fail(f"router beta.1 setup omits {marker}")

router_beta2 = router_candidates["1.0.2-beta.2"]
if router_beta2.get("status") != "candidate" or router_beta2.get("kind") != "router-iproyal":
    fail("router beta.2 candidate must remain candidate until real-device acceptance")
if router_beta2.get("tag") != "tiktok-router-iproyal-us-v1.0.2-beta.2" or router_beta2.get("releaseType") != "pre-release":
    fail("router beta.2 tag must be an explicitly marked prerelease")
if router_beta2.get("requirements") != [f"P{i}" for i in range(1, 11)]:
    fail("router beta.2 candidate must declare P1-P10")
if router_beta2.get("versionDirectory") != beta2_directory:
    fail("router beta.2 candidate must have its own version directory")
for key, filename in (("modulePath", "openclash-overwrite.conf"),
                      ("requirementsPath", "REQUIREMENTS.md"),
                      ("setupPath", "SETUP.md"),
                      ("chainPatchPath", "iproyal-chain-hop.conf")):
    if router_beta2.get(key) != f"{beta2_directory}/{filename}":
        fail(f"router beta.2 {key} must stay in its version directory")
if router_beta2.get("localProxyName") != "IPRoyal-US-ISP" or router_beta2.get("tiktokGroup") != "TikTok-ISP":
    fail("router beta.2 node/group identity changed")
beta2_module = read_text(router_beta2["modulePath"])
beta2_patch = read_text(router_beta2["chainPatchPath"])
beta2_contract = read_text(router_beta2["requirementsPath"])
beta2_setup = read_text(router_beta2["setupPath"])
if sha256(beta2_module) != router_beta2.get("moduleSha256"):
    fail("router beta.2 module hash differs from catalog")
if sha256(beta2_patch) != router_beta2.get("chainPatchSha256"):
    fail("router beta.2 patch hash differs from catalog")
if config_body(beta2_module) != config_body(chain_module):
    fail("router beta.2 must preserve the v1.0.1 routing/DNS module body")
if beta2_patch != expected_chain_patch:
    fail("router beta.2 patch must only update the existing exact local node")
if router_beta2.get("manualRulesSha256") != sha256(manual_rules_text) or router_beta2.get("manualRuleCount") != len(manual_entries):
    fail("router beta.2 manual-direct data differs from the shared list")
if "DOMAIN-SUFFIX,mmstat.com" not in manual_rules_text or "DOMAIN,d-gm.mmstat.com" in manual_rules_text:
    fail("router beta.2 must use a suffix rule for all mmstat.com domains")
if "DOMAIN-SUFFIX,mmstat.com" not in beta2_contract or "全部子域名" not in beta2_contract:
    fail("router beta.2 requirements must document mmstat.com suffix coverage")
if any(item not in beta2_contract for item in router_beta2["requirements"]):
    fail("router beta.2 contract omits a declared requirement")
for marker in ("v1.0.2-beta.2", "beta", "DOMAIN-SUFFIX,mmstat.com", "另一个 `mmstat.com` 子域名", "DIRECT", "回退"):
    if marker not in beta2_setup:
        fail(f"router beta.2 setup omits {marker}")
print("OK: router IPRoyal v1.0.2-beta.1 prerelease snapshot preserved")
print("OK: router IPRoyal v1.0.2-beta.2 prerelease; all mmstat.com subdomains direct, chain patch only, no credentials")

router_beta3 = router_candidates["1.0.2-beta.3"]
if router_beta3.get("status") != "candidate" or router_beta3.get("kind") != "router-iproyal":
    fail("router beta.3 must remain a candidate until real-device acceptance")
if router_beta3.get("tag") != "tiktok-router-iproyal-us-v1.0.2-beta.3" or router_beta3.get("releaseType") != "pre-release":
    fail("router beta.3 must identify its candidate pre-release tag")
if router_beta3.get("requirements") != [f"P{i}" for i in range(1, 12)]:
    fail("router beta.3 must declare P1-P11")
if router_beta3.get("versionDirectory") != beta3_directory:
    fail("router beta.3 candidate must have its own version directory")
for key, filename in (("modulePath", "openclash-overwrite.conf"),
                      ("requirementsPath", "REQUIREMENTS.md"),
                      ("setupPath", "SETUP.md"),
                      ("chainPatchPath", "iproyal-chain-hop.conf")):
    if router_beta3.get(key) != f"{beta3_directory}/{filename}":
        fail(f"router beta.3 {key} must stay in its version directory")
if router_beta3.get("localProxyName") != "IPRoyal-US-ISP" or router_beta3.get("tiktokGroup") != "TikTok-ISP":
    fail("router beta.3 node/group identity changed")
beta3_module = read_text(router_beta3["modulePath"])
beta3_patch = read_text(router_beta3["chainPatchPath"])
beta3_contract = read_text(router_beta3["requirementsPath"])
beta3_setup = read_text(router_beta3["setupPath"])
if sha256(beta3_module) != router_beta3.get("moduleSha256"):
    fail("router beta.3 module hash differs from catalog")
if beta3_module != latest_module_text:
    fail("router rolling module must match the latest beta snapshot")
if sha256(beta3_patch) != router_beta3.get("chainPatchSha256") or beta3_patch != expected_chain_patch:
    fail("router beta.3 chain patch must remain the exact no-credential IPRoyal update")
if router_beta3.get("manualRulesSha256") != sha256(manual_rules_text) or router_beta3.get("manualRuleCount") != len(manual_entries):
    fail("router beta.3 manual-direct snapshot metadata differs from the shared list")
manual_provider_match = re.search(r"(?ms)^  Manual-Direct!:\n(.*?)(?=^rules!:\n)", beta3_module)
if not manual_provider_match:
    fail("router beta.3 must replace only Manual-Direct with an inline provider")
manual_provider_body = manual_provider_match.group(1)
if not re.search(r"(?m)^    type: inline$", manual_provider_body):
    fail("router beta.3 Manual-Direct provider must use type inline")
if re.search(r"(?m)^    (?:url|path|interval):", manual_provider_body):
    fail("router beta.3 Manual-Direct must not depend on a separately refreshed file")
inline_entries = [line.strip() for line in manual_provider_body.splitlines() if line.startswith("      - ")]
if inline_entries != manual_entries:
    fail("router beta.3 inline Manual-Direct payload must exactly match rules/manual-direct.yaml")
if any(item not in beta3_contract for item in router_beta3["requirements"]):
    fail("router beta.3 requirements omit a declared requirement")
for marker in ("v1.0.2-beta.3", "inline", "不需要单独更新 Rule Provider", "滚动订阅地址", "重启 OpenClash", "DIRECT", "回退"):
    if marker not in beta3_setup:
        fail(f"router beta.3 setup omits {marker}")
print("OK: router IPRoyal v1.0.2-beta.3 inline Manual-Direct matches all 129 source rules; one module refresh path")

# Current local-ISP candidate: cloud routing module plus a credential-local node module.
isp_id = "tiktok-router-isp-us"
isp_profile = profiles.get(isp_id, {})
if catalog.get("developmentProfile") not in {isp_id, "tiktok-router-loongproxy-jp-us"}:
    fail("developmentProfile must point to the local ISP candidate")
if isp_profile.get("status") != "candidate" or isp_profile.get("currentVersion") is not None:
    fail("local ISP profile must remain a candidate until phone acceptance")
if isp_profile.get("supersededBy"):
    fail("active local ISP candidate cannot itself be superseded")
isp_versions = isp_profile.get("candidateVersions", {})
isp = isp_versions.get("1.0.0", {})
if set(isp_versions) != {"1.0.0"} or isp.get("kind") != "router-isp-local-node" or isp.get("status") != "candidate":
    fail("local ISP profile must declare only the v1.0.0 candidate")
if isp.get("requirements") != [f"C{i}" for i in range(1, 12)]:
    fail("local ISP candidate must declare C1-C11")
if isp.get("localProxyName") != "TikTok-ISP-Local" or isp.get("tiktokGroup") != "TikTok-ISP":
    fail("local ISP candidate node/group identity changed")
isp_directory = "profiles/tiktok-router-isp-us/versions/v1.0.0"
if isp.get("versionDirectory") != isp_directory:
    fail("local ISP candidate must use its independent version directory")
for key, filename in (("modulePath", "openclash-overwrite.conf"),
                      ("requirementsPath", "REQUIREMENTS.md"),
                      ("setupPath", "SETUP.md"),
                      ("localModuleTemplatePath", "local-tiktok-proxy.conf.example")):
    if isp.get(key) != f"{isp_directory}/{filename}":
        fail(f"local ISP {key} must stay in its candidate directory")
if isp.get("manualRulesPath") != "rules/manual-direct-isp.yaml":
    fail("local ISP candidate must use an isolated manual-direct rule source")
isp_module = read_text(isp["modulePath"])
isp_rolling_path = "profiles/tiktok-router-isp-us/overwrite/openclash-overwrite.conf"
isp_rolling = read_text(isp_rolling_path)
if isp_profile.get("latestModulePath") != isp_rolling_path:
    fail("local ISP profile must expose its own rolling cloud module")
if isp_module != isp_rolling:
    fail("local ISP rolling module must match the current candidate module")
if sha256(isp_module) != isp.get("moduleSha256") or sha256(isp_rolling) != isp_profile.get("latestModuleSha256"):
    fail("local ISP candidate/rolling module hash differs from catalog")
if "username:" in isp_module or "password:" in isp_module or "st02.loongproxy.com" in isp_module:
    fail("cloud module must not contain local proxy credentials or endpoint")
if isp_module.count("[YAML]") != 1 or re.search(r"(?m)^\[(?!YAML\])", isp_module):
    fail("local ISP cloud module must contain only one [YAML] section")
if "filter: '^TikTok-ISP-Local$'" not in isp_module:
    fail("TikTok group must select only the exact local ISP node")
if "exclude-filter: '(?i)^TikTok-ISP-Local$'" not in isp_module:
    fail("USA group must exclude the local chained node")
if "empty-fallback: REJECT" not in isp_module:
    fail("TikTok group must fail closed when its local node is absent")
if "  - GEOSITE,tiktok,TikTok-ISP\n  # 核心可能跳过不支持 UDP 的代理；同分类拒绝规则阻止落入美国或直连。\n  - GEOSITE,tiktok,REJECT" not in isp_module:
    fail("TikTok REJECT must immediately follow the TikTok proxy rule")
manual_isp_text = read_text(isp["manualRulesPath"])
manual_isp_entries = [line.strip()[2:] for line in manual_isp_text.splitlines()
                      if line.lstrip().startswith("- DOMAIN")]
if len(manual_isp_entries) != isp.get("manualRuleCount") or len(manual_isp_entries) != len(manual_entries):
    fail("local ISP manual-direct rules must retain all 129 existing entries")
if any(not entry.startswith("DOMAIN-SUFFIX,") for entry in manual_isp_entries):
    fail("every local ISP manual-direct entry must include its domain suffix")
expected_manual_isp = [entry[2:].replace("DOMAIN,", "DOMAIN-SUFFIX,", 1) for entry in manual_entries]
if manual_isp_entries != expected_manual_isp:
    fail("local ISP manual-direct rules must preserve every original entry and only broaden exact domains")
if sha256(manual_isp_text) != isp.get("manualRulesSha256") or isp_profile.get("manualRulesPath") != isp["manualRulesPath"]:
    fail("local ISP manual-direct source hash/path differs from catalog")
inline_match = re.search(r"(?ms)^  Manual-Direct!:\n(.*?)(?=^rules!:\n)", isp_module)
if not inline_match or not re.search(r"(?m)^    type: inline$", inline_match.group(1)):
    fail("local ISP cloud module must inline Manual-Direct")
if re.search(r"(?m)^    (?:url|path|interval):", inline_match.group(1)):
    fail("local ISP Manual-Direct inline rules must not require a separate provider refresh")
inline_isp_entries = [line.strip()[2:] for line in inline_match.group(1).splitlines()
                      if line.startswith("      - DOMAIN")]
if inline_isp_entries != manual_isp_entries:
    fail("local ISP inline Manual-Direct payload must exactly match its isolated source")
local_template = read_text(isp["localModuleTemplatePath"])
if "name: TikTok-ISP-Local" not in local_template or "dialer-proxy: 美国" not in local_template:
    fail("local ISP node template must chain the exact node through the USA group")
if not all(marker in local_template for marker in ("FILL_ME_PROXY_HOST", "FILL_ME_PROXY_PORT", "FILL_ME_USERNAME", "FILL_ME_PASSWORD")):
    fail("repository local-node template must contain placeholders, not real credentials")
if "st02.loongproxy.com" in local_template:
    fail("provider endpoint belongs only in the user's local module")
isp_contract = read_text(isp["requirementsPath"])
isp_setup = read_text(isp["setupPath"])
if any(item not in isp_contract for item in isp["requirements"]):
    fail("local ISP contract omits declared requirements")
for marker in ("v1.0.0", "candidate", "手选", "TikTok-ISP-Local", "DOMAIN-SUFFIX", "手机", "REJECT", "回退"):
    if marker not in isp_setup:
        fail(f"local ISP setup omits {marker}")
for doc in ("README.md", "AGENTS.md", "CHANGELOG.md", isp_profile["profileReadmePath"]):
    if isp_id not in read_text(doc) or "v1.0.0" not in read_text(doc):
        fail(f"{doc} does not document the current local ISP candidate")
print("OK: local ISP v1.0.0 candidate; exact local node, USA chain, fail-closed TikTok, and 129 domain-suffix direct rules")

# Immutable OpenClash specialist role and authoritative guide entry.
role_doc = read_text("AGENTS.md")
role_prefix = (
    "# 不可删除的 OpenClash 专家角色与权威指南\n\n"
    "你是 OpenClash 专家助手。OpenClash 是 OpenWrt 上管理 Mihomo 内核的 LuCI 插件。\n\n"
)
if not role_doc.startswith(role_prefix):
    fail("OpenClash expert role must never be removed or changed")
if "https://raw.githubusercontent.com/vernesong/OpenClash/dev/.github/skills/openclash-user-guide/SKILL.md" not in role_doc:
    fail("OpenClash authoritative user guide URL must be retained")
if "文档路由表" not in role_doc or "唯一权威参考" not in role_doc:
    fail("OpenClash guide knowledge-routing obligation was removed")

# Validate independent iKuu-Japan -> Loongproxy-USA candidate without altering historical snapshots.
jp_id = "tiktok-router-loongproxy-jp-us"
jp_profile = profiles.get(jp_id)
if not isinstance(jp_profile, dict):
    fail("new Japan/Loongproxy candidate is not indexed")
if jp_profile.get("status") != "candidate" or jp_profile.get("currentVersion") is not None:
    fail("new Japan/Loongproxy candidate must remain unpublished")
jp = jp_profile.get("candidateVersions", {}).get("1.0.0", {})
jp_dir = "profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.0"
if jp.get("status") != "candidate" or jp.get("versionDirectory") != jp_dir:
    fail("Japan/Loongproxy v1.0.0 candidate version not registered")
if jp.get("requirements") != [f"J{i}" for i in range(1, 13)]:
    fail("Japan/Loongproxy requires J1-J12")
for key, name in (("modulePath", "openclash-overwrite.conf"),
                  ("requirementsPath", "REQUIREMENTS.md"),
                  ("setupPath", "SETUP.md"),
                  ("localModuleTemplatePath", "local-tiktok-proxy.conf.example")):
    if jp.get(key) != f"{jp_dir}/{name}":
        fail(f"Japan/Loongproxy missing {key}")
if jp_profile.get("profileReadmePath") != "profiles/tiktok-router-loongproxy-jp-us/README.md":
    fail("Japan/Loongproxy README path changed")
jp_cloud = read_text(jp["modulePath"])
jp_yaml = parsed_modules[jp["modulePath"]]
jp_groups = jp_yaml.get("proxy-groups!")
if (not isinstance(jp_groups, list)
        or not all(isinstance(g, dict) for g in jp_groups)
        or [g.get("name") for g in jp_groups] != ["日本-入口", "TikTok-ISP", "美国"]):
    fail("Japan/Loongproxy must define exactly three distinct proxy groups")
for group in jp_groups:
    if group.get("type") != "select" or group.get("empty-fallback") != "REJECT":
        fail(f"{group['name']} must be manual select and reject when empty")
    if "proxies" in group or "use" in group:
        fail(f"{group['name']} must not bypass its node filter through explicit members")
for group in (jp_groups[0], jp_groups[2]):
    if group.get("include-all") is not True or group.get("exclude-filter") != "(?i)^TikTok-ISP-Local$":
        fail("Japan/USA must filter subscription nodes and exclude local ISP")
if jp_groups[0].get("filter") != r"(?i)(🇯🇵|日本|japan|(^|[ _|:-])JP([ _|:-]|[0-9]|$))":
    fail("Japan first-hop node filter changed")
if jp_groups[1].get("include-all-proxies") is not True or jp_groups[1].get("include-all") or jp_groups[1].get("include-all-providers") or jp_groups[1].get("filter") != "^TikTok-ISP-Local$":
    fail("TikTok-ISP must select only the exact local ISP node")
jp_rules = jp_yaml.get("rules!")
if not isinstance(jp_rules, list) or not all(isinstance(rule, str) for rule in jp_rules):
    fail("Japan/Loongproxy routing rules must be a string list")
if jp_rules.count("GEOSITE,tiktok,TikTok-ISP") != 1 or jp_rules.count("GEOSITE,tiktok,REJECT") != 1:
    fail("Japan/Loongproxy requires exactly one TikTok route and reject guard")
jp_tiktok_index = jp_rules.index("GEOSITE,tiktok,TikTok-ISP")
if jp_rules[jp_tiktok_index + 1:jp_tiktok_index + 2] != ["GEOSITE,tiktok,REJECT"]:
    fail("TikTok REJECT must immediately follow the ISP rule")
jp_dns = jp_yaml.get("dns", {})
jp_fakeip = jp_dns.get("fake-ip-filter!", [])
if jp_dns.get("fake-ip-filter-mode") != "rule" or jp_fakeip[:3] != ["GEOSITE,tiktok,fake-ip", "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,fake-ip", "GEOSITE,google,fake-ip"]:
    fail("TikTok/Google Fake-IP exceptions must precede China real-IP rules")
jp_rolling = "profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf"
if jp_profile.get("latestModulePath") != jp_rolling or read_text(jp_rolling) != jp_cloud:
    fail("Japan/Loongproxy single rolling module differs from v1.0.0 candidate")
if jp.get("moduleSha256") != sha256(jp_cloud) or jp_profile.get("latestModuleSha256") != sha256(jp_cloud):
    fail("Japan/Loongproxy cloud module SHA mismatch")
if jp_cloud.count("[YAML]") != 1 or re.search(r"(?m)^\[(?!YAML\])", jp_cloud):
    fail("Japan/Loongproxy cloud module must only contain [YAML]")
if any(term in jp_cloud.lower() for term in ("username:", "password:", "st02.loongproxy.com", "uci set ")):
    fail("Japan/Loongproxy cloud must not include private credentials/endpoint/UCI")
for needle in (
    "  - name: 日本-入口", "  - name: TikTok-ISP", "filter: '^TikTok-ISP-Local$'",
    "  - name: 美国", "exclude-filter: '(?i)^TikTok-ISP-Local$'",
    "  - GEOSITE,tiktok,TikTok-ISP", "  - GEOSITE,tiktok,REJECT",
    "  - DOMAIN-SUFFIX,xn--ngstr-lra8j.com,美国", "  - GEOSITE,google,美国",
    "  - RULE-SET,Manual-Direct,DIRECT", "  - RULE-SET,oc-cn-domain,DIRECT",
    "  - GEOIP,CN,DIRECT,no-resolve", "  - MATCH,美国"
):
    if needle not in jp_cloud:
        fail(f"Japan/Loongproxy missing routing/group fragment: {needle}")
jp_order = (
    "GEOSITE,private,DIRECT", "GEOSITE,tiktok,TikTok-ISP", "GEOSITE,tiktok,REJECT",
    "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,美国", "GEOSITE,google,美国",
    "RULE-SET,Manual-Direct,DIRECT", "RULE-SET,oc-cn-domain,DIRECT",
    "GEOIP,CN,DIRECT,no-resolve", "MATCH,美国"
)
jp_positions = [jp_cloud.index(k) for k in jp_order]
if jp_positions != sorted(jp_positions):
    fail("Japan/Loongproxy priority broken")
jp_manual = read_text("rules/manual-direct-isp.yaml")
jp_entries = [line.strip()[2:] for line in jp_manual.splitlines()
              if line.lstrip().startswith("- DOMAIN")]
if jp.get("manualRulesPath") != "rules/manual-direct-isp.yaml" or jp_profile.get("manualRulesPath") != "rules/manual-direct-isp.yaml":
    fail("Japan/Loongproxy must use shared existing ISP-specific manual rule data")
if len(jp_entries) != 129 or jp.get("manualRuleCount") != 129:
    fail("Japan/Loongproxy must preserve all 129 Manual-Direct entries")
if any(not x.startswith("DOMAIN-SUFFIX,") for x in jp_entries):
    fail("Japan/Loongproxy must include suffix domains")
if sha256(jp_manual) != jp.get("manualRulesSha256"):
    fail("Japan/Loongproxy Manual-Direct SHA mismatch")
jp_inline = re.search(r"(?ms)^  Manual-Direct!:\n(.*?)(?=^rules!:\n)", jp_cloud)
if not jp_inline or "    type: inline" not in jp_inline.group(1):
    fail("Japan/Loongproxy Manual-Direct is not inline")
if re.search(r"(?m)^    (?:url|path|interval):", jp_inline.group(1)):
    fail("Japan/Loongproxy Manual-Direct cannot require separate provider refresh")
jp_embedded = [line.strip()[2:] for line in jp_inline.group(1).splitlines()
               if line.startswith("      - DOMAIN")]
if jp_embedded != jp_entries:
    fail("Japan/Loongproxy rolling module does not embed all latest 129 manual entries")
jp_provider = jp_yaml.get("rule-providers", {}).get("Manual-Direct!", {})
if jp_provider != {"type": "inline", "behavior": "classical", "payload": jp_entries}:
    fail("Japan/Loongproxy parsed Manual-Direct provider must exactly match its source")
jp_local = read_text(jp["localModuleTemplatePath"])
if parsed_modules[jp["localModuleTemplatePath"]] != {"proxies+": [{
    "name": "TikTok-ISP-Local", "type": "socks5", "server": "FILL_ME_PROXY_HOST",
    "port": "FILL_ME_PROXY_PORT", "username": "FILL_ME_USERNAME",
    "password": "FILL_ME_PASSWORD", "udp": False, "dialer-proxy": "日本-入口",
}]}:
    fail("Japan/Loongproxy local template must append only the placeholder SOCKS5 node")
for needle in ("[YAML]", "name: TikTok-ISP-Local", "type: socks5", "udp: false",
               "dialer-proxy: 日本-入口", "FILL_ME_PROXY_HOST", "FILL_ME_PROXY_PORT",
               "FILL_ME_USERNAME", "FILL_ME_PASSWORD"):
    if needle not in jp_local:
        fail(f"Japan/Loongproxy local proxy template missing {needle}")
for doc in ("README.md", "AGENTS.md", "MAINTENANCE.md", "CHANGELOG.md",
            jp_profile["profileReadmePath"]):
    if jp_id not in read_text(doc):
        fail(f"{doc} omits Japan/Loongproxy candidate")
for key in ("requirementsPath", "setupPath"):
    if "v1.0.0" not in read_text(jp[key]) or "candidate" not in read_text(jp[key]):
        fail(f"Japan/Loongproxy missing candidate status in {key}")
if not all(t in read_text(jp["requirementsPath"]) for t in jp["requirements"]):
    fail("Japan/Loongproxy J1-J12 requirements not fully documented")
print("OK: independent JP-first-hop/Loongproxy-US candidate, 129 inline direct entries, protected routing, no credentials")

if args.base_ref and set(args.base_ref) != {"0"}:
    try:
        base_catalog_result = subprocess.run(
            ["git", "show", f"{args.base_ref}:profiles/catalog.json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        base_catalog = json.loads(base_catalog_result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as error:
        fail(f"cannot read base catalog from {args.base_ref}: {error}")

    protected_at_base = []
    for base_profile in base_catalog.get("profiles", {}).values():
        protected_at_base.extend(
            base_profile.get("immutableVersionDirectories", [])
        )

    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-status",
            f"{args.base_ref}...HEAD",
            "--",
            *protected_at_base,
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    forbidden = [
        line
        for line in result.stdout.splitlines()
        if line and not line.startswith("A\t")
    ]
    if forbidden:
        fail("published version files were modified or removed: " + "; ".join(forbidden))

print(
    f"OK: profile={profile_id} version=v{version} "
    f"requirements={','.join(requirements)}"
)
print(f"OK: module sha256={sha256(module_text)}")
print(f"OK: manual-direct entries={len(manual_entries)} sha256={sha256(manual_rules_text)}")
print("OK: protected DNS keys and routing order")
for candidate_version, candidate in candidate_versions.items():
    candidate_module_text = read_text(candidate["modulePath"])
    if candidate.get("kind") == "guide-mainland-bypass":
        print(f"OK: guide_candidate=v{candidate_version} module_sha256={sha256(candidate_module_text)}")
        print("OK: ordered Fake-IP exceptions, CN MRS, explicit DNS ownership, manual-direct unchanged")
        continue
    manual_japan_text = read_text(candidate["manualJapanRulesPath"])
    manual_japan_entries = [
        line.strip()
        for line in manual_japan_text.splitlines()
        if line.lstrip().startswith("- ")
    ]
    print(
        f"OK: candidate=v{candidate_version} "
        f"module_sha256={sha256(candidate_module_text)}"
    )
    print(
        f"OK: manual-japan entries={len(manual_japan_entries)} "
        f"sha256={sha256(manual_japan_text)}"
    )
print(
    f"OK: stable_profile={hybrid_profile_id} version=v1.0.1 "
    f"module_sha256={sha256(hybrid_module_text)}"
)
print("OK: authorized TikTok US device=192.168.100.198/32")
