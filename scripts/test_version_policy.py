import unittest

from validate_repository import compare_versions, validate_version_sequence


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
