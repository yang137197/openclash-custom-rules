#!/usr/bin/env python3
"""Generate the rolling Manual-Direct inline payload from its canonical source."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from strict_yaml import load_yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "rules/manual-direct.yaml"
ROLLING_PATH = "profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf"
CATALOG_PATH = "profiles/catalog.json"
PROFILE_ID = "tiktok-router-loongproxy-jp-us"
PROVIDER_HEADER = "  Manual-Direct!:\n"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_payload(payload):
    require(isinstance(payload, list), "manual direct source payload must be a list")

    label_pattern = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\Z")
    for index, rule in enumerate(payload, start=1):
        require(isinstance(rule, str), f"manual direct entry {index} must be a string")
        parts = rule.split(",")
        require(len(parts) == 2 and parts[0] in {"DOMAIN", "DOMAIN-SUFFIX"},
                f"manual direct entry {index} must use DOMAIN or DOMAIN-SUFFIX: {rule}")
        domain = parts[1]
        require(domain and domain == domain.strip() and "://" not in domain and
                "/" not in domain and ":" not in domain,
                f"invalid manual direct domain at entry {index}: {domain}")
        try:
            ascii_domain = domain.encode("idna").decode("ascii")
        except UnicodeError as error:
            raise ValueError(f"invalid internationalized domain at entry {index}: {domain}") from error
        labels = ascii_domain.split(".")
        require(len(ascii_domain) <= 253 and len(labels) >= 2 and
                all(label_pattern.fullmatch(label) for label in labels),
                f"invalid manual direct domain at entry {index}: {domain}")
    return payload


def parse_payload(source_text):
    document = load_yaml(source_text)
    require(isinstance(document, dict), "manual direct source must be a YAML mapping")
    return validate_payload(document.get("payload"))


def render_provider(payload):
    lines = [
        "  Manual-Direct!:",
        "    type: inline",
        "    behavior: classical",
    ]
    if payload:
        lines.append("    payload:")
        lines.extend(f"      - {rule}" for rule in payload)
    else:
        lines.append("    payload: []")
    return "\n".join(lines) + "\n\n"


def replace_provider(module_text, payload):
    require(module_text.count(PROVIDER_HEADER) == 1,
            "rolling module must contain exactly one Manual-Direct inline provider")
    start = module_text.index(PROVIDER_HEADER)
    rules_match = re.search(r"(?m)^rules!:\s*$", module_text[start:])
    require(rules_match is not None, "rolling module is missing the root rules! section")
    end = start + rules_match.start()
    generated = module_text[:start] + render_provider(payload) + module_text[end:]

    # v1.0.6 represented Huzhou as a separate rule. v1.0.7 moves it into the
    # canonical inline payload; remove that legacy standalone copy on every run.
    rule_start = generated.index("rules!:", start)
    prefix, rule_section = generated[:rule_start], generated[rule_start:]
    lines = rule_section.splitlines(keepends=True)
    lines = [line for line in lines if line.rstrip("\r\n") != "  - DOMAIN-SUFFIX,huzhou.host,DIRECT"]
    return prefix + "".join(lines)


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_utf8(path, text):
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def synchronize(root=ROOT, write=False):
    source_path = root / SOURCE_PATH
    rolling_path = root / ROLLING_PATH
    catalog_path = root / CATALOG_PATH
    payload = parse_payload(source_path.read_text(encoding="utf-8"))
    current_module = rolling_path.read_text(encoding="utf-8")
    generated_module = replace_provider(current_module, payload)

    catalog_text = catalog_path.read_text(encoding="utf-8")
    catalog = json.loads(catalog_text)
    profile = catalog["profiles"][PROFILE_ID]
    require(profile.get("latestModulePath") == ROLLING_PATH,
            "catalog rolling module path does not match the generator target")
    generated_hash = sha256(generated_module)
    profile["latestModuleSha256"] = generated_hash
    generated_catalog = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"

    module_changed = current_module != generated_module
    catalog_changed = catalog_text != generated_catalog
    if write:
        if module_changed:
            write_utf8(rolling_path, generated_module)
        if catalog_changed:
            write_utf8(catalog_path, generated_catalog)
        print(f"Synchronized {len(payload)} manual direct rules; module changed={module_changed}, catalog changed={catalog_changed}")
        return module_changed or catalog_changed

    require(not module_changed, f"{ROLLING_PATH} is out of sync with {SOURCE_PATH}")
    require(not catalog_changed, f"{CATALOG_PATH} rolling module hash is out of date")
    print(f"OK: {len(payload)} manual direct rules match the rolling module and catalog hash")
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="update rolling module and catalog hash")
    mode.add_argument("--check", action="store_true", help="fail if generated files are out of sync")
    args = parser.parse_args()
    synchronize(write=args.write)


if __name__ == "__main__":
    try:
        main()
    except (KeyError, OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
