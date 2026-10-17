import contextlib
import io
import json
import unittest

import validate_repository as validator
from strict_yaml import load_yaml


class JapanFirstProfileTests(unittest.TestCase):
    def test_published_profile_contract(self):
        catalog = json.loads(validator.read("profiles/catalog.json"))
        profile = catalog["profiles"][validator.JP]
        manual = load_yaml(validator.read(profile["manualRulesPath"]))["payload"]
        modules = {}
        for path in (validator.ROOT / "profiles" / validator.JP).rglob("*.conf*"):
            relative = path.relative_to(validator.ROOT).as_posix()
            modules[relative] = load_yaml(validator.read(relative), module=True)
        with contextlib.redirect_stdout(io.StringIO()):
            validator.validate_stable(validator.JP, profile, modules, manual)


if __name__ == "__main__":
    unittest.main()
