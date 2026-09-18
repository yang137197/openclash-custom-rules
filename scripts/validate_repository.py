#!/usr/bin/env python3
"""Validate version mapping and protected OpenClash invariants using stdlib only."""

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

required_module_fragments = [
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

for candidate_version, candidate in candidate_versions.items():
    if candidate.get("status") != "candidate":
        fail(f"v{candidate_version} candidate must have status=candidate")

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

    candidate_required_fragments = required_module_fragments + [
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

if args.base_ref and set(args.base_ref) != {"0"}:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-status",
            f"{args.base_ref}...HEAD",
            "--",
            *immutable_version_directories,
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
