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

    def test_candidate_routes_claude_code_official_hosts_to_tiktok_isp(self):
        catalog = json.loads(validator.read("profiles/catalog.json"))
        profile = catalog["profiles"][validator.JP]
        candidate = profile["versions"]["1.0.2"]
        self.assertEqual(candidate["status"], "candidate")
        self.assertEqual(candidate["requirements"], ["J13"])
        module = load_yaml(validator.read(candidate["modulePath"]), module=True)
        rules = module["rules!"]
        expected_private = validator.expected_rules()[:12]
        expected_claude = [
            "DOMAIN-SUFFIX,anthropic.com,TikTok-ISP",
            "DOMAIN-SUFFIX,claude.ai,TikTok-ISP",
            "DOMAIN-SUFFIX,claude.com,TikTok-ISP",
            "DOMAIN,storage.googleapis.com,TikTok-ISP",
            "DOMAIN-SUFFIX,npmjs.org,TikTok-ISP",
            "DOMAIN-SUFFIX,claudeusercontent.com,TikTok-ISP",
            "DOMAIN-SUFFIX,github.com,TikTok-ISP",
            "DOMAIN-SUFFIX,githubusercontent.com,TikTok-ISP",
            "DOMAIN-WILDCARD,*-review.googlesource.com,TikTok-ISP",
            "DOMAIN,http-intake.logs.us5.datadoghq.com,TikTok-ISP",
            "DOMAIN,browser-intake-us5-datadoghq.com,TikTok-ISP",
            "DOMAIN,formulae.brew.sh,TikTok-ISP",
        ]
        self.assertEqual(rules[:len(expected_private)], expected_private)
        start = len(expected_private)
        self.assertEqual(rules[start:start + len(expected_claude)], expected_claude)
        last_claude_rule = start + len(expected_claude) - 1
        self.assertLess(last_claude_rule, rules.index("GEOSITE,tiktok,TikTok-ISP"))
        self.assertLess(last_claude_rule, rules.index("RULE-SET,Manual-Direct,DIRECT"))
        self.assertNotIn("SRC-IP-CIDR,192.168.100.216/32,TikTok-ISP", rules)
        self.assertNotIn("DOMAIN,update.kies.samsung.com,DIRECT", rules)
        self.assertEqual(candidate["manualRuleCount"], 129)

    def test_latest_candidate_routes_claude_first_party_domains_to_one_isp_group(self):
        catalog = json.loads(validator.read("profiles/catalog.json"))
        profile = catalog["profiles"][validator.JP]
        candidate = profile["versions"]["1.0.3"]
        self.assertEqual(candidate["status"], "candidate")
        self.assertEqual(candidate["requirements"], ["J13", "J14"])
        module = load_yaml(validator.read(candidate["modulePath"]), module=True)
        rules = module["rules!"]
        expected_private = validator.expected_rules()[:12]
        expected_claude = [
            "DOMAIN-SUFFIX,anthropic.com,TikTok-ISP",
            "DOMAIN-SUFFIX,claude.ai,TikTok-ISP",
            "DOMAIN-SUFFIX,claude.com,TikTok-ISP",
            "DOMAIN,storage.googleapis.com,TikTok-ISP",
            "DOMAIN-SUFFIX,npmjs.org,TikTok-ISP",
            "DOMAIN-SUFFIX,claudeusercontent.com,TikTok-ISP",
            "DOMAIN-SUFFIX,claudemcpcontent.com,TikTok-ISP",
            "DOMAIN-SUFFIX,github.com,TikTok-ISP",
            "DOMAIN-SUFFIX,githubusercontent.com,TikTok-ISP",
            "DOMAIN-WILDCARD,*-review.googlesource.com,TikTok-ISP",
            "DOMAIN,http-intake.logs.us5.datadoghq.com,TikTok-ISP",
            "DOMAIN,browser-intake-us5-datadoghq.com,TikTok-ISP",
            "DOMAIN,formulae.brew.sh,TikTok-ISP",
        ]
        self.assertEqual(rules[:len(expected_private)], expected_private)
        start = len(expected_private)
        self.assertEqual(rules[start:start + len(expected_claude)], expected_claude)
        last_claude_rule = start + len(expected_claude) - 1
        self.assertLess(last_claude_rule, rules.index("GEOSITE,tiktok,TikTok-ISP"))
        self.assertLess(last_claude_rule, rules.index("RULE-SET,Manual-Direct,DIRECT"))
        self.assertEqual(candidate["manualRuleCount"], 129)

    def test_latest_candidate_keeps_claude_on_isp_and_github_on_us(self):
        catalog = json.loads(validator.read("profiles/catalog.json"))
        profile = catalog["profiles"][validator.JP]
        candidate = profile["versions"]["1.0.4"]
        self.assertEqual(candidate["status"], "candidate")
        self.assertEqual(candidate["requirements"], ["J13", "J14", "J15"])
        module = load_yaml(validator.read(candidate["modulePath"]), module=True)
        rules = module["rules!"]
        expected_private = validator.expected_rules()[:12]
        expected_service_rules = [
            "DOMAIN-SUFFIX,anthropic.com,TikTok-ISP",
            "DOMAIN-SUFFIX,claude.ai,TikTok-ISP",
            "DOMAIN-SUFFIX,claude.com,TikTok-ISP",
            "DOMAIN,storage.googleapis.com,TikTok-ISP",
            "DOMAIN-SUFFIX,npmjs.org,TikTok-ISP",
            "DOMAIN-SUFFIX,claudeusercontent.com,TikTok-ISP",
            "DOMAIN-SUFFIX,claudemcpcontent.com,TikTok-ISP",
            "DOMAIN-SUFFIX,github.com,美国",
            "DOMAIN-SUFFIX,githubusercontent.com,美国",
            "DOMAIN-SUFFIX,githubassets.com,美国",
            "DOMAIN-WILDCARD,*-review.googlesource.com,TikTok-ISP",
            "DOMAIN,http-intake.logs.us5.datadoghq.com,TikTok-ISP",
            "DOMAIN,browser-intake-us5-datadoghq.com,TikTok-ISP",
            "DOMAIN,formulae.brew.sh,TikTok-ISP",
        ]
        self.assertEqual(rules[:len(expected_private)], expected_private)
        start = len(expected_private)
        self.assertEqual(rules[start:start + len(expected_service_rules)], expected_service_rules)
        end = start + len(expected_service_rules)
        self.assertLessEqual(end, rules.index("GEOSITE,tiktok,TikTok-ISP"))
        self.assertLess(end, rules.index("RULE-SET,Manual-Direct,DIRECT"))
        self.assertNotIn("DOMAIN-SUFFIX,github.com,TikTok-ISP", rules)
        self.assertNotIn("DOMAIN-SUFFIX,githubusercontent.com,TikTok-ISP", rules)
        self.assertNotIn("DOMAIN-SUFFIX,githubassets.com,TikTok-ISP", rules)
        self.assertEqual(candidate["manualRuleCount"], 129)


if __name__ == "__main__":
    unittest.main()
