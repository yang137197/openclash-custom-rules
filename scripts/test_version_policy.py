import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from validate_repository import (compare_versions, validate_environment_record,
                                 validate_reused_environment_source, validate_version_catalog,
                                 validate_version_sequence)


class VersionPolicyTests(unittest.TestCase):
    def test_semver_orders_prerelease_before_release(self):
        self.assertLess(compare_versions("1.0.1-beta.2", "1.0.1-beta.10"), 0)
        self.assertLess(compare_versions("1.0.1-beta.10", "1.0.1"), 0)
        self.assertGreater(compare_versions("1.0.1", "1.0.0"), 0)

    def test_new_version_requires_higher_number_and_changelog_content(self):
        changelog = "## tiktok-router-loongproxy-jp-us v1.0.1 — 2026-10-17\n\n- Update route behavior.\n"
        validate_version_sequence("tiktok-router-loongproxy-jp-us", ["1.0.0", "1.0.1"],
                                  ["1.0.0"], changelog)

    def test_version_downgrade_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "move backwards"):
            validate_version_sequence("tiktok-router-loongproxy-jp-us", ["1.0.0", "1.0.1"],
                                      ["1.0.0", "1.0.1"], "", "1.0.0", "1.0.1")

    def test_new_candidate_must_exceed_highest_recorded_version(self):
        with self.assertRaisesRegex(ValueError, "must exceed"):
            validate_version_sequence("tiktok-router-loongproxy-jp-us",
                                      ["1.0.0", "1.0.1", "1.0.2"],
                                      ["1.0.0", "1.0.2"], "", "1.0.0", "1.0.0")

    def test_independent_profiles_may_each_start_at_v1(self):
        changelog = (
            "## rule-a v1.0.0 — 2026-10-17\n\n- First profile.\n"
            "## rule-b v1.0.0 — 2026-10-17\n\n- Separate profile.\n"
        )
        validate_version_sequence("rule-a", ["1.0.0"], [], changelog)
        validate_version_sequence("rule-b", ["1.0.0"], [], changelog)

    def test_candidate_only_profile_is_valid(self):
        profile = {
            "status": "candidate",
            "currentVersion": "1.0.0",
            "immutableVersionDirectories": [],
            "versions": {
                "1.0.0": {
                    "status": "candidate",
                    "versionDirectory": "profiles/rule-b/versions/v1.0.0",
                }
            },
        }
        changelog = "## rule-b v1.0.0 — 2026-10-17\n\n- Initial candidate.\n"
        validate_version_catalog("rule-b", profile, changelog)

    def test_candidate_environment_can_be_pending_without_fabricating_versions(self):
        record = {
            "schemaVersion": 1,
            "profileId": "rule-b",
            "version": "1.0.0",
            "status": "pending",
            "behaviorChanged": True,
            "environment": {
                "openclashVersion": "unknown",
                "openclashBuild": "unknown",
                "mihomoVersion": "unknown",
                "mihomoBuild": "unknown",
                "openwrtVersion": "unknown",
                "deviceArchitecture": "unknown",
                "deviceModel": "unknown",
            },
            "runtimeConfiguration": {
                "activeConfigLabel": "unknown",
                "enabledModulesInOrder": [],
                "settingsBaseline": "unknown",
                "settingsDeviations": [],
            },
            "evidence": {
                "source": "none",
                "capturedAt": None,
                "rawDebugLogCommitted": False,
                "runtimeAcceptance": "not-run",
                "userConfirmed": False,
                "summary": "等待用户提供目标设备环境信息。",
            },
            "reusedFromVersion": None,
            "setupDocument": "SETUP.md",
        }
        validate_environment_record("rule-b", "1.0.0", "candidate", record)

    def test_behavior_changing_stable_release_requires_log_and_user_acceptance(self):
        record = {
            "schemaVersion": 1,
            "profileId": "rule-b",
            "version": "1.0.0",
            "status": "verified",
            "behaviorChanged": True,
            "environment": {
                "openclashVersion": "fixture-openclash-version",
                "openclashBuild": "fixture-openclash-build",
                "mihomoVersion": "fixture-mihomo-version",
                "mihomoBuild": "fixture-mihomo-build",
                "openwrtVersion": "fixture-openwrt-version",
                "deviceArchitecture": "fixture-architecture",
                "deviceModel": "fixture-device",
            },
            "runtimeConfiguration": {
                "activeConfigLabel": "fixture-profile",
                "enabledModulesInOrder": ["fixture-cloud-module", "fixture-local-module"],
                "settingsBaseline": "matched-setup",
                "settingsDeviations": [],
            },
            "evidence": {
                "source": "debug-log",
                "capturedAt": "2026-10-17",
                "rawDebugLogCommitted": False,
                "runtimeAcceptance": "passed",
                "userConfirmed": True,
                "summary": "用户确认版本合同中的实机验收通过。",
            },
            "reusedFromVersion": None,
            "setupDocument": "SETUP.md",
        }
        validate_environment_record("rule-b", "1.0.0", "stable", record)
        record["behaviorChanged"] = False
        validate_environment_record("rule-b", "1.0.0", "stable", record)
        record["behaviorChanged"] = True
        record["evidence"]["capturedAt"] = "2026-99-99"
        with self.assertRaisesRegex(ValueError, "debug-log date"):
            validate_environment_record("rule-b", "1.0.0", "stable", record)
        record["evidence"]["capturedAt"] = "2026-10-17"
        record["evidence"]["rawDebugLogCommitted"] = True
        with self.assertRaisesRegex(ValueError, "raw logs must stay out of Git"):
            validate_environment_record("rule-b", "1.0.0", "stable", record)

    def test_reused_environment_must_reference_latest_verified_stable_record(self):
        record = {
            "reusedFromVersion": "1.0.0",
            "environment": {"openclashVersion": "fixture-version"},
            "runtimeConfiguration": {"activeConfigLabel": "fixture-profile"},
        }
        profile = {
            "versions": {
                "1.1.0": {"status": "stable", "environmentPath": "env/v1.1.0.json"},
            },
        }
        with self.assertRaisesRegex(ValueError, "source version 1.0.0 is not indexed"):
            validate_reused_environment_source("rule-b", "1.2.0", profile, record)

    def test_legacy_release_without_environment_record_cannot_be_cited_as_verified(self):
        record = {
            "reusedFromVersion": "1.0.0",
            "environment": {"openclashVersion": "fixture-version"},
            "runtimeConfiguration": {"activeConfigLabel": "fixture-profile"},
        }
        profile = {
            "versions": {
                "1.0.0": {"status": "stable"},
                "1.1.0": {"status": "stable", "environmentPath": "env/v1.1.0.json"},
            },
        }
        with self.assertRaisesRegex(ValueError, "source has no environment record"):
            validate_reused_environment_source("rule-b", "1.1.0", profile, record)

    def test_matching_verified_environment_snapshot_can_be_reused(self):
        source_environment = {"openclashVersion": "fixture-version"}
        source_runtime = {"activeConfigLabel": "fixture-profile"}
        source_record = {
            "status": "verified",
            "environment": source_environment,
            "runtimeConfiguration": source_runtime,
        }
        record = {
            "reusedFromVersion": "1.0.0",
            "environment": source_environment,
            "runtimeConfiguration": source_runtime,
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment_path = root / "env" / "v1.0.0.json"
            environment_path.parent.mkdir(parents=True)
            environment_path.write_text(json.dumps(source_record), encoding="utf-8")
            profile = {
                "versions": {
                    "1.0.0": {"status": "stable", "environmentPath": "env/v1.0.0.json"},
                    "1.1.0": {"status": "stable", "environmentPath": "env/v1.1.0.json"},
                },
            }
            with patch("validate_repository.ROOT", root):
                validate_reused_environment_source("rule-b", "1.1.0", profile, record)

    def test_new_version_without_update_content_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "CHANGELOG entry"):
            validate_version_sequence("tiktok-router-loongproxy-jp-us", ["1.0.0", "1.0.1"],
                                      ["1.0.0"], "## tiktok-router-loongproxy-jp-us v1.0.1\n\nNo details.\n")

    def test_recorded_version_cannot_be_removed(self):
        with self.assertRaisesRegex(ValueError, "version was removed"):
            validate_version_sequence("tiktok-router-loongproxy-jp-us", ["1.0.1"],
                                      ["1.0.0"], "")


if __name__ == "__main__":
    unittest.main()
