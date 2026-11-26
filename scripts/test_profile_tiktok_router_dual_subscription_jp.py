import copy
import json
import re
import unittest

from build_dual_subscription import (DIRECTORY, ROOT, FIRST, EXIT, MEDIA, DEFAULT,
                                     IK_FILTER, LXY_FILTER, LXY_MEMBER_FILTER, TEST_URL)
from strict_yaml import load_yaml


def validate(cloud, local, payload):
    groups = {g["name"]: g for g in cloud["proxy-groups!"]}
    assert list(groups) == [FIRST, EXIT, MEDIA, DEFAULT], "four public groups"
    assert groups[FIRST]["use"] == groups[DEFAULT]["use"] == ["dual-ikuuu"], "iKuuu isolated"
    assert groups[MEDIA]["use"] == ["dual-liangxinyun"], "media isolated"
    assert groups[FIRST]["type"] == groups[DEFAULT]["type"] == "url-test", "minimum delay"
    assert groups[MEDIA]["type"] == "fallback", "fixed priority"
    assert groups[MEDIA]["filter"] == LXY_FILTER, "ordered priority filters"
    for group in groups.values():
        assert group["url"] == TEST_URL and group["interval"] == 60 and group["timeout"] == 5000
        assert group["lazy"] is False and group["expected-status"] == "204"
        assert group["empty-fallback"] == "REJECT"
        assert not group.get("include-all") and not group.get("include-all-providers")
        assert not group.get("hidden")
    assert groups[EXIT]["type"] == "select" and groups[EXIT]["filter"] == "^TikTok-ISP-Local$"
    assert not groups[EXIT].get("use") and not groups[EXIT].get("proxies")
    assert len(local["proxies+"]) == 1
    isp = local["proxies+"][0]
    assert (isp["name"], isp["type"], isp["udp"], isp["dialer-proxy"]) == ("TikTok-ISP-Local", "socks5", False, FIRST)
    assert set(local["proxy-providers"]) == {"dual-ikuuu", "dual-liangxinyun"}
    assert local["proxy-providers"]["dual-liangxinyun"]["filter"] == LXY_MEMBER_FILTER
    for provider in local["proxy-providers"].values():
        health = provider["health-check"]
        assert health == dict(enable=True, url=TEST_URL, interval=60, timeout=5000, lazy=False, **{"expected-status": "204"})
        assert provider["url"].startswith("FILL_ME_")
    assert cloud["rule-providers"]["Manual-Direct"]["payload"] == payload, "manual list/order/duplicates"
    rules = cloud["rules!"]
    tiktok = rules.index("GEOSITE,tiktok," + EXIT)
    assert rules[tiktok + 1] == "GEOSITE,tiktok,REJECT"
    assert rules[-1] == "MATCH," + DEFAULT
    for rule in rules:
        if rule.endswith("," + MEDIA):
            assert rules.index(rule) > tiktok + 1
            assert "(NOT,((RULE-SET,Manual-Direct)))" in rule
            assert "(NOT,((RULE-SET,oc-cn-domain)))" in rule
            assert "(NOT,((GEOIP,CN,no-resolve)))" in rule
        if rule.endswith("," + EXIT):
            assert rule == "GEOSITE,tiktok," + EXIT, "only TikTok uses ISP"
    assert not any("#TikTok-ISP" in str(value) or "#美国" in str(value)
                   for value in cloud["dns"].values()), "no obsolete DNS group references"


class DualSubscriptionTests(unittest.TestCase):
    def setUp(self):
        self.cloud = load_yaml((DIRECTORY / "openclash-overwrite.conf").read_text(encoding="utf-8"), module=True)
        self.local = load_yaml((DIRECTORY / "local-tiktok-proxy.conf").read_text(encoding="utf-8"), module=True)
        self.payload = load_yaml((ROOT / "rules/manual-direct.yaml").read_text(encoding="utf-8"))["payload"]

    def test_complete_contract(self):
        validate(self.cloud, self.local, self.payload)

    def test_new_profile_does_not_inherit_original_legacy_example_extension(self):
        import validate_repository as validator
        profile_id = "tiktok-router-dual-subscription-jp"
        catalog = json.loads((ROOT / "profiles/catalog.json").read_text(encoding="utf-8"))
        profile = catalog["profiles"][profile_id]
        entry = profile["versions"]["1.0.0"]
        validator.validate_profile_artifacts(profile_id, profile, {
            entry["modulePath"]: self.cloud, entry["localModuleTemplatePath"]: self.local})

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
        with self.assertRaises(AssertionError):
            validate(self.cloud, self.local, self.payload)

    def test_media_minimum_delay_substitution_is_rejected(self):
        self.cloud["proxy-groups!"][2]["type"] = "url-test"
        with self.assertRaises(AssertionError):
            validate(self.cloud, self.local, self.payload)

    def test_isp_airport_fallback_is_rejected(self):
        self.cloud["proxy-groups!"][1]["proxies"] = [DEFAULT]
        with self.assertRaises(AssertionError):
            validate(self.cloud, self.local, self.payload)

    def test_direct_removal_and_reordering_are_rejected(self):
        for replacement in (self.payload[:-1], list(reversed(self.payload))):
            changed = copy.deepcopy(self.cloud)
            changed["rule-providers"]["Manual-Direct"]["payload"] = replacement
            with self.assertRaises(AssertionError):
                validate(changed, self.local, self.payload)

    def test_media_cannot_steal_direct_or_china(self):
        rules = self.cloud["rules!"]
        index = next(i for i, rule in enumerate(rules) if rule.endswith("," + MEDIA))
        rules[index] = "GEOSITE,youtube," + MEDIA
        with self.assertRaises(AssertionError):
            validate(self.cloud, self.local, self.payload)

    def test_tiktok_reject_guard_cannot_be_removed(self):
        self.cloud["rules!"].remove("GEOSITE,tiktok,REJECT")
        with self.assertRaises(AssertionError):
            validate(self.cloud, self.local, self.payload)

    def test_provider_health_must_not_depend_on_panel(self):
        self.local["proxy-providers"]["dual-ikuuu"]["health-check"]["lazy"] = True
        with self.assertRaises(AssertionError):
            validate(self.cloud, self.local, self.payload)


if __name__ == "__main__":
    unittest.main()
