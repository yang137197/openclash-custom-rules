import contextlib
import io
import json
import unittest

import validate_repository as validator
from strict_yaml import load_yaml
from sync_manual_direct import parse_payload, replace_provider


class JapanFirstProfileTests(unittest.TestCase):
    def test_published_profile_contract(self):
        catalog = json.loads(validator.read("profiles/catalog.json"))
        profile = catalog["profiles"][validator.JP]
        stable = profile["versions"][profile["currentVersion"]]
        manual = load_yaml(validator.read(stable["manualRulesPath"]))["payload"]
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

    def test_v104_snapshot_keeps_claude_on_isp_and_github_on_us(self):
        catalog = json.loads(validator.read("profiles/catalog.json"))
        profile = catalog["profiles"][validator.JP]
        candidate = profile["versions"]["1.0.4"]
        self.assertEqual(candidate["status"], "stable")
        self.assertEqual(candidate["requirements"], ["J13", "J14", "J15"])
        self.assertEqual(candidate["releaseTag"], "tiktok-router-loongproxy-jp-us-v1.0.4")
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

    def test_v105_stable_release_uses_openclash_uploadable_conf_template_without_route_changes(self):
        catalog = json.loads(validator.read("profiles/catalog.json"))
        profile = catalog["profiles"][validator.JP]
        release = profile["versions"]["1.0.5"]
        stable = profile["versions"]["1.0.4"]
        self.assertEqual(profile["currentVersion"], "1.0.6")
        self.assertEqual(release["status"], "stable")
        self.assertEqual(release["requirements"], ["J13", "J14", "J15", "J16"])
        self.assertTrue(release["localModuleTemplatePath"].endswith("/local-tiktok-proxy.conf"))
        self.assertEqual(release["releaseTag"], "tiktok-router-loongproxy-jp-us-v1.0.5")
        self.assertEqual(release["releaseUrl"], "https://github.com/yang137197/openclash-custom-rules/releases/tag/tiktok-router-loongproxy-jp-us-v1.0.5")
        self.assertEqual(release["versionedModuleUrl"], "https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.5/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.5/openclash-overwrite.conf")
        self.assertEqual(release["localTemplateSha256"], validator.sha(validator.read(release["localModuleTemplatePath"])))
        self.assertEqual(
            validator.read(release["localModuleTemplatePath"]),
            validator.read(stable["localModuleTemplatePath"]),
        )
        template = load_yaml(validator.read(release["localModuleTemplatePath"]), module=True)
        self.assertEqual(template["proxies+"][0]["name"], "TikTok-ISP-Local")
        self.assertEqual(template["proxies+"][0]["dialer-proxy"], "日本-入口")
        self.assertFalse(template["proxies+"][0]["udp"])
        self.assertEqual(
            validator.read(release["modulePath"]),
            validator.read(stable["modulePath"]),
        )
        evidence = json.loads(validator.read(release["environmentPath"]))
        self.assertEqual(evidence["status"], "verified")
        self.assertFalse(evidence["behaviorChanged"])
        self.assertEqual(evidence["reusedFromVersion"], "1.0.4")
        self.assertEqual(evidence["evidence"]["runtimeAcceptance"], "not-run")
        self.assertFalse(evidence["evidence"]["userConfirmed"])

    def test_v106_stable_release_routes_huzhou_apex_and_subdomains_direct(self):
        catalog = json.loads(validator.read("profiles/catalog.json"))
        profile = catalog["profiles"][validator.JP]
        release = profile["versions"]["1.0.6"]
        self.assertEqual(profile["currentVersion"], "1.0.6")
        self.assertEqual(release["status"], "stable")
        self.assertEqual(release["requirements"], ["J17"])
        self.assertEqual(release["manualRulesPath"], "rules/manual-direct-isp.yaml")
        self.assertEqual(release["additionalDirectRulesPath"], "rules/manual-direct.yaml")
        self.assertEqual(release["releaseTag"], "tiktok-router-loongproxy-jp-us-v1.0.6")
        self.assertEqual(release["versionedModuleUrl"],
                         "https://raw.githubusercontent.com/yang137197/openclash-custom-rules/tiktok-router-loongproxy-jp-us-v1.0.6/profiles/tiktok-router-loongproxy-jp-us/versions/v1.0.6/openclash-overwrite.conf")

        self.assertEqual(release["manualRuleCount"], 129)
        self.assertEqual(release["manualRulesSha256"], validator.sha(validator.read(release["manualRulesPath"])))

        module = load_yaml(validator.read(release["modulePath"]), module=True)
        rules = module["rules!"]
        expected = "DOMAIN-SUFFIX,huzhou.host,DIRECT"
        self.assertEqual(rules.count(expected), 1)
        self.assertLess(rules.index("GEOSITE,google,美国"), rules.index(expected))
        self.assertLess(rules.index(expected), rules.index("RULE-SET,Manual-Direct,DIRECT"))
        self.assertEqual(release["moduleSha256"], validator.sha(validator.read(release["modulePath"])))

        rolling = load_yaml(validator.read(profile["latestModulePath"]), module=True)
        self.assertEqual(rolling["rules!"].count(expected), 0)
        self.assertEqual(profile["latestModuleSha256"], validator.sha(validator.read(profile["latestModulePath"])))

        environment = json.loads(validator.read(release["environmentPath"]))
        self.assertEqual(environment["status"], "verified")
        self.assertTrue(environment["behaviorChanged"])
        self.assertEqual(environment["evidence"]["source"], "debug-log")
        self.assertEqual(environment["evidence"]["capturedAt"], "2026-10-28")
        self.assertEqual(environment["evidence"]["runtimeAcceptance"], "passed")
        self.assertTrue(environment["evidence"]["userConfirmed"])

    def test_v107_snapshot_uses_one_manual_source_without_runtime_rule_changes(self):
        catalog = json.loads(validator.read("profiles/catalog.json"))
        profile = catalog["profiles"][validator.JP]
        candidate = profile["versions"]["1.0.7"]
        self.assertIn(candidate["status"], {"candidate", "stable"})
        self.assertEqual(candidate["requirements"], ["J18", "J19", "J20", "J21"])
        self.assertEqual(candidate["manualRulesPath"], "rules/manual-direct.yaml")

        historical = load_yaml(validator.read("rules/manual-direct-isp.yaml"))["payload"]
        expected_candidate_payload = historical + ["DOMAIN-SUFFIX,huzhou.host"]

        stable = profile["versions"]["1.0.6"]
        stable_module = load_yaml(validator.read(stable["modulePath"]), module=True)
        candidate_module = load_yaml(validator.read(candidate["modulePath"]), module=True)
        candidate_payload = candidate_module["rule-providers"]["Manual-Direct!"]["payload"]
        self.assertEqual(parse_payload("payload:\n" + "".join(f"  - {rule}\n" for rule in candidate_payload)),
                         candidate_payload)
        self.assertEqual(candidate_payload, expected_candidate_payload)
        for key in set(stable_module) - {"rules!", "rule-providers"}:
            self.assertEqual(candidate_module[key], stable_module[key])
        self.assertEqual(
            candidate_module["rule-providers"]["oc-cn-domain"],
            stable_module["rule-providers"]["oc-cn-domain"],
        )
        self.assertEqual(
            candidate_module["rules!"],
            [rule for rule in stable_module["rules!"]
             if rule != "DOMAIN-SUFFIX,huzhou.host,DIRECT"],
        )
        self.assertEqual(candidate["moduleSha256"],
                         validator.sha(validator.read(candidate["modulePath"])))

        rolling = load_yaml(validator.read(profile["latestModulePath"]), module=True)
        source = parse_payload(validator.read(candidate["manualRulesPath"]))
        self.assertEqual(rolling["rule-providers"]["Manual-Direct!"]["payload"], source)
        self.assertNotIn("DOMAIN-SUFFIX,huzhou.host,DIRECT", rolling["rules!"])

        environment = json.loads(validator.read(candidate["environmentPath"]))
        self.assertEqual(environment["status"],
                         "pending" if candidate["status"] == "candidate" else "verified")
        self.assertFalse(environment["behaviorChanged"])
        self.assertEqual(environment["reusedFromVersion"], "1.0.6")
        if candidate["status"] == "candidate":
            self.assertEqual(environment["evidence"]["runtimeAcceptance"], "not-run")

    def test_manual_direct_generator_add_modify_delete_exactly_tracks_source(self):
        module_template = (
            "[YAML]\n"
            "rule-providers:\n"
            "  Manual-Direct!:\n"
            "    type: inline\n"
            "    behavior: classical\n"
            "    payload:\n"
            "      - DOMAIN-SUFFIX,old.example\n"
            "rules!:\n"
            "  - RULE-SET,Manual-Direct,DIRECT\n"
        )
        initial = parse_payload(
            "payload:\n  - DOMAIN-SUFFIX,old.example\n  - DOMAIN,api.old.example\n"
        )
        updated = parse_payload(
            "payload:\n  - DOMAIN,api.new.example\n  - DOMAIN-SUFFIX,new.example\n"
        )
        generated_initial = load_yaml(replace_provider(module_template, initial), module=True)
        generated_updated = load_yaml(replace_provider(module_template, updated), module=True)
        self.assertEqual(generated_initial["rule-providers"]["Manual-Direct!"]["payload"], initial)
        self.assertEqual(generated_updated["rule-providers"]["Manual-Direct!"]["payload"], updated)
        self.assertNotIn("DOMAIN-SUFFIX,old.example",
                         generated_updated["rule-providers"]["Manual-Direct!"]["payload"])

    def test_manual_direct_generator_preserves_duplicates_and_suffix_vs_exact(self):
        source = (
            "payload:\n"
            "  - DOMAIN-SUFFIX,example.com\n"
            "  - DOMAIN,api.example.com\n"
            "  - DOMAIN-SUFFIX,example.com\n"
        )
        payload = parse_payload(source)
        generated = load_yaml(
            replace_provider(
                "[YAML]\nrule-providers:\n  Manual-Direct!:\n"
                "    type: inline\n    behavior: classical\n    payload: []\n"
                "rules!:\n  - RULE-SET,Manual-Direct,DIRECT\n",
                payload,
            ),
            module=True,
        )
        self.assertEqual(
            generated["rule-providers"]["Manual-Direct!"]["payload"],
            ["DOMAIN-SUFFIX,example.com", "DOMAIN,api.example.com", "DOMAIN-SUFFIX,example.com"],
        )


if __name__ == "__main__":
    unittest.main()
