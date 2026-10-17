import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import validate_repository as validator


class LogPrivacyTests(unittest.TestCase):
    def test_raw_log_file_extension_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            (Path(temporary) / "openclash_debug.log").write_text("log", encoding="utf-8")
            with patch.object(validator, "ROOT", Path(temporary)), \
                    patch.object(validator, "git", return_value="openclash_debug.log\0"):
                with self.assertRaisesRegex(ValueError, "raw log files must not be committed"):
                    validator.validate_no_raw_debug_logs()

    def test_debug_log_renamed_to_text_is_rejected_by_section_signature(self):
        with tempfile.TemporaryDirectory() as temporary:
            raw_log = "\n".join(("## 系统信息", "## 依赖检查", "## 内核检查", "## 活动连接信息"))
            (Path(temporary) / "router-info.txt").write_text(raw_log, encoding="utf-8")
            with patch.object(validator, "ROOT", Path(temporary)), \
                    patch.object(validator, "git", return_value="router-info.txt\0"):
                with self.assertRaisesRegex(ValueError, "raw OpenClash debug log sections detected"):
                    validator.validate_no_raw_debug_logs()

    def test_large_debug_log_renamed_to_text_is_also_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            raw_log = "x" * 5_000_001 + "\n".join(
                ("## 系统信息", "## 依赖检查", "## 内核检查", "## 活动连接信息"))
            (Path(temporary) / "large-router-info.txt").write_text(raw_log, encoding="utf-8")
            with patch.object(validator, "ROOT", Path(temporary)), \
                    patch.object(validator, "git", return_value="large-router-info.txt\0"):
                with self.assertRaisesRegex(ValueError, "raw OpenClash debug log sections detected"):
                    validator.validate_no_raw_debug_logs()

    def test_ignored_local_log_is_not_treated_as_a_commit_candidate(self):
        with tempfile.TemporaryDirectory() as temporary:
            (Path(temporary) / "local-debug.log").write_text("private log", encoding="utf-8")
            with patch.object(validator, "ROOT", Path(temporary)), \
                    patch.object(validator, "git", return_value=""):
                validator.validate_no_raw_debug_logs()


if __name__ == "__main__":
    unittest.main()
