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

    def test_candidate_routes_only_exact_samsung_update_host_direct(self):
        catalog = json.loads(validator.read("profiles/catalog.json"))
        profile = catalog["profiles"][validator.JP]
        candidate = profile["versions"]["1.0.1"]
        self.assertEqual(candidate["status"], "candidate")
        expected = "DOMAIN,update.kies.samsung.com,DIRECT"
        supplemental = load_yaml(validator.read(candidate["additionalDirectRulesPath"]))["payload"]
        module = load_yaml(validator.read(candidate["modulePath"]), module=True)
        rules = module["rules!"]
        self.assertEqual(supplemental, [expected])
        self.assertEqual(rules.count(expected), 1)
        self.assertLess(rules.index("GEOSITE,google,美国"), rules.index(expected))
        self.assertLess(rules.index(expected), rules.index("RULE-SET,Manual-Direct,DIRECT"))
        samsung_rules = [rule for rule in rules if "samsung" in rule.lower()]
        self.assertEqual(samsung_rules, [expected])
        self.assertEqual(candidate["manualRuleCount"], 129)


if __name__ == "__main__":
    unittest.main()
