import json
import re
import unittest

from validate_repository import ROOT, validate_current_document_versions


class CurrentDocumentVersionTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT / "profiles/catalog.json").read_text(encoding="utf-8"))
        self.profile_id = self.catalog["currentProfile"]
        self.profile = self.catalog["profiles"][self.profile_id]
        self.version = self.profile["currentVersion"]
        self.profile_readme = self.profile["profileReadmePath"]
        paths = ("README.md", "AGENTS.md", "MAINTENANCE.md", self.profile_readme)
        self.documents = {path: (ROOT / path).read_text(encoding="utf-8") for path in paths}

    def test_current_documents_allow_historical_versions(self):
        self.documents["README.md"] += "\n历史版本：v0.0.0。\n"
        validate_current_document_versions(self.catalog, self.documents)

    def test_stale_current_claims_are_rejected_even_if_current_version_exists_elsewhere(self):
        v = self.version
        p = self.profile_id
        cases = (
            ("README.md", f"当前正式方案为 **{p} v{v} /", f"当前正式方案为 **{p} v0.0.0 /"),
            ("README.md", f"| v{v} |", "| v0.0.0 |"),
            ("README.md", f"v{v} 是当前正式版", "v0.0.0 是当前正式版"),
            ("AGENTS.md", f"当前正式方案：`{p} v{v}`", f"当前正式方案：`{p} v0.0.0`"),
            ("AGENTS.md", f"当前 `v{v}` 为正式稳定版本", "当前 `v0.0.0` 为正式稳定版本"),
            ("MAINTENANCE.md", f"当前唯一支持方案是 `{p} v{v}`", f"当前唯一支持方案是 `{p} v0.0.0`"),
            ("MAINTENANCE.md", f"当前正式版 v{v}", "当前正式版 v0.0.0"),
            ("MAINTENANCE.md", f"当前稳定版本为 `v{v}`", "当前稳定版本为 `v0.0.0`"),
            (self.profile_readme, f"**v{v} stable**", "**v0.0.0 stable**"),
            (self.profile_readme, f"- [v{v} GitHub Release]", "- [v0.0.0 GitHub Release]"),
            (self.profile_readme, f"(versions/v{v}/REQUIREMENTS.md)", "(versions/v0.0.0/REQUIREMENTS.md)"),
            (self.profile_readme, f"v{v} 固定完整云覆写：", "v0.0.0 固定完整云覆写："),
            (self.profile_readme, self.profile["versions"][v]["versionedModuleUrl"], "https://example.invalid/old"),
        )
        for path, original, replacement in cases:
            with self.subTest(path=path, original=original):
                self.assertIn(original, self.documents[path])
                changed = dict(self.documents)
                changed[path] = changed[path].replace(original, replacement, 1)
                with self.assertRaisesRegex(ValueError, re.escape(path)):
                    validate_current_document_versions(self.catalog, changed)

    def test_missing_current_declaration_is_rejected(self):
        path = "MAINTENANCE.md"
        changed = dict(self.documents)
        original = f"当前稳定版本为 `v{self.version}`"
        self.assertIn(original, changed[path])
        changed[path] = changed[path].replace(original, "稳定版本参见 catalog", 1)
        with self.assertRaisesRegex(ValueError, re.escape(path)):
            validate_current_document_versions(self.catalog, changed)


if __name__ == "__main__":
    unittest.main()
