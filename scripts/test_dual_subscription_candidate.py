import copy
import json
import re
import unittest

from build_dual_subscription import (DIRECTORY, ROOT, PROFILE, VERSION, FIRST, EXIT, MEDIA, DEFAULT,
                                     IK_FILTER, LXY_FILTER, LXY_MEMBER_FILTER, TEST_URL)
from strict_yaml import load_yaml
from dual_subscription_contract import validate




class DualSubscriptionTests(unittest.TestCase):
    def setUp(self):
        self.cloud = load_yaml((DIRECTORY / "openclash-overwrite.conf").read_text(encoding="utf-8"), module=True)
        self.local = load_yaml((DIRECTORY / "local-tiktok-proxy.conf").read_text(encoding="utf-8"), module=True)
        self.payload = self.cloud["rule-providers"]["Manual-Direct"]["payload"]

    def test_complete_contract(self):
        validate(self.cloud, self.local, self.payload)

    def test_daily_rolling_payload_matches_source_without_changing_runtime_contract(self):
        source = load_yaml((ROOT / "rules/manual-direct.yaml").read_text(encoding="utf-8"))["payload"]
        rolling = load_yaml((ROOT / f"profiles/{PROFILE}/overwrite/openclash-overwrite.conf").read_text(encoding="utf-8"), module=True)
        expected = copy.deepcopy(self.cloud)
        expected["rule-providers"]["Manual-Direct"]["payload"] = source
        self.assertEqual(rolling, expected)
        validate(rolling, self.local, source)

    def test_candidate_extends_existing_version_line_and_keeps_stable_rolling(self):
        import validate_repository as validator
        catalog = json.loads((ROOT / "profiles/catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(set(catalog["profiles"]), {PROFILE})
        profile = catalog["profiles"][PROFILE]
        entry = profile["versions"][VERSION]
        self.assertGreaterEqual(validator.compare_versions(profile["currentVersion"], VERSION), 0)
        self.assertEqual(VERSION, "1.0.8")
        self.assertEqual(entry["status"], "stable")
        self.assertTrue(entry["localModuleTemplatePath"].endswith("/local-tiktok-proxy.conf"))
        self.assertEqual(profile["latestModulePath"], f"profiles/{PROFILE}/overwrite/openclash-overwrite.conf")
        self.assertEqual(entry["moduleSha256"], validator.sha(validator.read(entry["modulePath"])))
        self.assertEqual(entry["localTemplateSha256"], validator.sha(validator.read(entry["localModuleTemplatePath"])))

    def test_native_direct_generation_is_byte_idempotent(self):
        from sync_manual_direct import replace_provider
        text = (DIRECTORY / "openclash-overwrite.conf").read_text(encoding="utf-8")
        self.assertEqual(replace_provider(text, self.payload), text)

    def test_native_direct_add_modify_delete_duplicates_and_empty(self):
        from sync_manual_direct import replace_provider
        text = (DIRECTORY / "openclash-overwrite.conf").read_text(encoding="utf-8")
        for payload in (["DOMAIN,exact.example", "DOMAIN-SUFFIX,new.example", "DOMAIN,exact.example"], []):
            generated = load_yaml(replace_provider(text, payload), module=True)
            expected = copy.deepcopy(self.cloud)
            expected["rule-providers"]["Manual-Direct"]["payload"] = payload
            self.assertEqual(generated, expected)

    def test_ambiguous_direct_provider_aliases_are_rejected(self):
        from sync_manual_direct import replace_provider
        text = "[YAML]\nrule-providers:\n  Manual-Direct!:\n    payload: []\n  Manual-Direct:\n    payload: []\nrules!: []\n"
        with self.assertRaisesRegex(ValueError, "exactly one"):
            replace_provider(text, [])

    def test_native_stable_validator_rejects_non_direct_rolling_changes(self):
        import validate_repository as validator
        catalog = json.loads((ROOT / "profiles/catalog.json").read_text(encoding="utf-8"))
        profile = catalog["profiles"][PROFILE]
        entry = profile["versions"][VERSION]
        modules = {entry["modulePath"]: self.cloud, entry["localModuleTemplatePath"]: self.local,
                   profile["latestModulePath"]: copy.deepcopy(self.cloud)}
        modules[profile["latestModulePath"]]["dns"]["prefer-h3"] = True
        with self.assertRaisesRegex(ValueError, "only the generated"):
            validator.validate_native_stable(PROFILE, profile, modules)

    def test_generator_refuses_to_overwrite_published_snapshot(self):
        from build_dual_subscription import build
        with self.assertRaisesRegex(ValueError, "immutable"):
            build()

    def test_ikuuu_accepts_new_numbers_prefixes_spaces_but_not_other_categories(self):
        for name in ("🇯🇵 日本Z01 | IEPL", "IK: 日本 Z12|IEPL|x1", "日本Z105 | IEPL"):
            self.assertRegex(name, IK_FILTER)
        for name in ("美国Z01 | IEPL", "日本高速01|BGP|CUCM", "日本Z01 | IPLC", "日本Z01|IEPLX"):
            self.assertNotRegex(name, IK_FILTER)

    def test_numbered_media_filters_ignore_subscription_shuffle(self):
        names = ["🇯🇵日本高速05|BGP|CUCM", "LXY: 日本专线02|BGP|流媒体", "日本专线01|BGP|流媒体", "日本专线05|BGP|流媒体"]
        ordered = list(dict.fromkeys(n for pattern in LXY_FILTER.split("`") for n in names if re.search(pattern, n)))
        self.assertEqual(ordered, [names[2], names[1], names[3], names[0]])

    def test_unknown_tiers_and_unsupported_numbering_never_silently_join(self):
        for name in ("日本专线100|BGP|流媒体", "日本专线00|BGP|流媒体", "美国专线01|BGP|流媒体", "日本高速01|BGP|CUMC", "日本专线01|BGP|普通"):
            self.assertNotRegex(name, LXY_MEMBER_FILTER)
        self.assertRegex("🇯🇵 日本 高速 99 | BGP | CUCM | x1", LXY_MEMBER_FILTER)

    def test_wrong_supplier_is_rejected(self):
        self.cloud["proxy-groups!"][0]["use"] = ["dual-liangxinyun"]
        with self.assertRaises(ValueError):
            validate(self.cloud, self.local, self.payload)

    def test_media_minimum_delay_substitution_is_rejected(self):
        self.cloud["proxy-groups!"][2]["type"] = "url-test"
        with self.assertRaises(ValueError):
            validate(self.cloud, self.local, self.payload)

    def test_isp_airport_fallback_is_rejected(self):
        self.cloud["proxy-groups!"][1]["proxies"] = [DEFAULT]
        with self.assertRaises(ValueError):
            validate(self.cloud, self.local, self.payload)

    def test_direct_removal_and_reordering_are_rejected(self):
        for replacement in (self.payload[:-1], list(reversed(self.payload))):
            changed = copy.deepcopy(self.cloud)
            changed["rule-providers"]["Manual-Direct"]["payload"] = replacement
            with self.assertRaises(ValueError):
                validate(changed, self.local, self.payload)

    def test_media_cannot_steal_direct_or_china(self):
        rules = self.cloud["rules!"]
        index = next(i for i, rule in enumerate(rules) if rule.endswith("," + MEDIA))
        rules[index] = "GEOSITE,youtube," + MEDIA
        with self.assertRaises(ValueError):
            validate(self.cloud, self.local, self.payload)

    def test_tiktok_reject_guard_cannot_be_removed(self):
        self.cloud["rules!"].remove("GEOSITE,tiktok,REJECT")
        with self.assertRaises(ValueError):
            validate(self.cloud, self.local, self.payload)

    def test_provider_health_must_not_depend_on_panel(self):
        self.local["proxy-providers"]["dual-ikuuu"]["health-check"]["lazy"] = True
        with self.assertRaises(ValueError):
            validate(self.cloud, self.local, self.payload)


if __name__ == "__main__":
    unittest.main()
