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
if profile.get("tag") != f"v{version}":
    fail("tag must match currentVersion")

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

if args.base_ref and set(args.base_ref) != {"0"}:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-status",
            f"{args.base_ref}...HEAD",
            "--",
            "profiles/*/versions/*",
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
