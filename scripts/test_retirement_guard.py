"""The one-time cleanup must not authorize unrelated published-file edits."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import validate_repository as validator


class RetirementGuardTests(unittest.TestCase):
    def run_guard(self, status="D", profile_id="retired-example"):
        directory = f"profiles/{profile_id}/versions/v1.0.0"
        base = {"profiles": {profile_id: {"immutableVersionDirectories": [directory]}}}
        approved = {"profiles": {"retired-example": {"immutableVersionDirectories": [
            "profiles/retired-example/versions/v1.0.0"]}}}
        responses = [json.dumps(base), json.dumps(approved),
                     f"{status}\t{directory}/openclash-overwrite.conf\n"]
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(validator, "ROOT", Path(temporary)), \
                    patch.object(validator, "git", side_effect=responses), \
                    contextlib.redirect_stdout(io.StringIO()):
                validator.check_history("test-base", {validator.JP: {}})

    def test_approved_retirement_allows_deletion(self):
        self.run_guard()

    def test_approved_retirement_does_not_allow_rewriting_snapshot(self):
        with self.assertRaisesRegex(ValueError, "published snapshot changed"):
            self.run_guard(status="M")

    def test_unapproved_profile_cannot_be_retired(self):
        with self.assertRaisesRegex(ValueError, "unapproved profile retirement"):
            self.run_guard(profile_id="unapproved-example")


if __name__ == "__main__":
    unittest.main()
