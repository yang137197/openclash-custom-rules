"""Regression checks for the candidate with a separate Liangxinyun subscription."""

import json
import re
import unittest

from strict_yaml import load_yaml
from validate_repository import JP, git, read, sha


PROFILE = JP + "-liangxinyun"
BASELINE = "57ff42265dd3dffe44e86b7f78206b3d768f3d81"
DOMAIN_PROVIDERS = ("oc-youtube-domain", "oc-telegram-domain")
MEDIA_PROVIDERS = (*DOMAIN_PROVIDERS, "oc-telegram-ip")


class LiangxinyunProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog = json.loads(read("profiles/catalog.json"))
        entry = catalog["profiles"][PROFILE]["versions"]["1.0.0"]
        stable = catalog["profiles"][JP]
        cls.baseline = load_yaml(git("show", f"{BASELINE}:{stable['latestModulePath']}"), module=True)
        cls.module = load_yaml(read(entry["modulePath"]), module=True)
        local = read(entry["localModuleTemplatePath"])
        cls.local = load_yaml(local, module=True)
        cls.local_hash = sha(local)
        cls.catalog = catalog
        cls.entry = entry
        next_entry = catalog["profiles"][PROFILE]["versions"]["1.1.0"]
        cls.default_module = load_yaml(read(next_entry["modulePath"]), module=True)
        cls.default_local = read(next_entry["localModuleTemplatePath"])
        cls.default_local_hash = next_entry["localTemplateSha256"]

    def test_preserves_stable_rules_dns_and_direct_snapshot(self):
        self.assertEqual(self.catalog["currentProfile"], JP)
        self.assertEqual(set(self.module), set(self.baseline))
        for key in ("ipv6", "profile", "dns"):
            self.assertEqual(self.module[key], self.baseline[key])
        providers = self.module["rule-providers"]
        self.assertEqual({name: value for name, value in providers.items() if name not in MEDIA_PROVIDERS},
                         self.baseline["rule-providers"])
        self.assertEqual(
            [rule for rule in self.module["rules!"] if not any(name in rule for name in MEDIA_PROVIDERS)],
            self.baseline["rules!"],
        )

    def test_media_rules_respect_direct_exceptions_and_reject_unsupported_traffic(self):
        rules = self.module["rules!"]
        google = rules.index("GEOSITE,google,美国")
        direct_guard = "NOT,((OR,((RULE-SET,Manual-Direct),(RULE-SET,oc-cn-domain),(GEOIP,CN,no-resolve))))"
        expected_domains = [
            f"AND,((RULE-SET,{provider}),({direct_guard})),{group}"
            for provider in DOMAIN_PROVIDERS
            for group in ("良心云", "REJECT")
        ]
        self.assertEqual(rules[google - 5:google], ["DOMAIN-SUFFIX,xn--ngstr-lra8j.com,美国", *expected_domains])
        self.assertEqual(rules[-4:], [
            "GEOIP,CN,DIRECT,no-resolve",
            "RULE-SET,oc-telegram-ip,良心云,no-resolve",
            "RULE-SET,oc-telegram-ip,REJECT,no-resolve",
            "MATCH,美国",
        ])
        for name, behavior, category in (
            ("oc-youtube-domain", "domain", "geosite/youtube"),
            ("oc-telegram-domain", "domain", "geosite/telegram"),
            ("oc-telegram-ip", "ipcidr", "geoip/telegram"),
        ):
            self.assertEqual(self.module["rule-providers"][name], {
                "type": "http", "behavior": behavior, "format": "mrs", "proxy": "美国",
                "url": f"https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/{category}.mrs",
                "path": f"./rule_provider/{name}.mrs", "interval": 86400,
            })

    def test_subscription_nodes_are_isolated_from_both_existing_groups(self):
        groups = self.module["proxy-groups!"]
        self.assertEqual(groups[-1], {
            "name": "良心云", "type": "select", "use": ["liangxinyun"], "empty-fallback": "REJECT",
        })
        self.assertEqual({group["name"] for group in groups}, {"日本-入口", "TikTok-ISP", "美国", "良心云"})
        baseline_groups = self.baseline["proxy-groups!"]
        provider = self.local["proxy-providers"]["liangxinyun!"]
        self.assertEqual(provider["override"], {"additional-prefix": "LXY: "})
        for original, group in zip(baseline_groups, groups[:-1], strict=True):
            if original["name"] == "TikTok-ISP":
                self.assertEqual(group, original)
                continue
            self.assertEqual({**group, "exclude-filter": original["exclude-filter"]}, original)
            self.assertRegex("LXY: 日本", group["exclude-filter"])
            self.assertRegex("LXY: 美国", group["exclude-filter"])
            self.assertRegex("TikTok-ISP-Local", group["exclude-filter"])
            self.assertIsNone(re.search(group["exclude-filter"], "iKuuu Japan 01"))
            self.assertIsNone(re.search(group["exclude-filter"], "iKuuu USA 01"))

    def test_local_module_preserves_isp_and_uses_only_placeholders(self):
        stable_local = load_yaml(read(f"profiles/{JP}/versions/v1.0.7/local-tiktok-proxy.conf"), module=True)
        self.assertEqual(self.local, {
            **stable_local,
            "proxy-providers": {"liangxinyun!": {
                "type": "http", "url": "FILL_ME_LIANGXINYUN_MIHOMO_URL",
                "path": "./proxy_provider/liangxinyun.yaml", "interval": 3600, "proxy": "DIRECT",
                "override": {"additional-prefix": "LXY: "},
            }},
        })
        self.assertEqual(self.local_hash, self.entry["localTemplateSha256"])

    def test_default_proxy_preserves_direct_precedence_and_has_no_claude_exceptions(self):
        expected = []
        for rule in self.baseline["rules!"]:
            if rule.endswith(",TikTok-ISP") and rule != "GEOSITE,tiktok,TikTok-ISP":
                continue
            expected.append(rule.removesuffix(",美国") + ",良心云" if rule.endswith(",美国") else rule)
        self.assertEqual(self.default_module["rules!"], [*expected, "MATCH,REJECT"])
        self.assertEqual(self.default_module["rule-providers"], {
            **self.baseline["rule-providers"],
            "oc-cn-domain": {**self.baseline["rule-providers"]["oc-cn-domain"], "proxy": "良心云"},
        })

    def test_default_proxy_dns_uses_liangxinyun_except_for_tiktok(self):
        dns = self.baseline["dns"]
        policies = {
            category: [server.replace("#美国", "#良心云") for server in servers]
            for category, servers in dns["nameserver-policy!"].items()
        }
        self.assertEqual(self.default_module["dns"], {**dns, "nameserver-policy!": policies})

    def test_default_proxy_isolates_ikuuu_to_tiktok_and_preserves_local_module(self):
        japan, tiktok, _, liangxinyun = self.module["proxy-groups!"]
        self.assertEqual(self.default_module["proxy-groups!"], [japan, tiktok, liangxinyun])
        self.assertEqual(sha(self.default_local), self.local_hash)
        self.assertEqual(self.default_local_hash, self.local_hash)

    def test_startup_fix_uses_literal_provider_names_when_the_parent_is_new(self):
        entry = self.catalog["profiles"][PROFILE]["versions"]["1.1.1"]
        cloud = load_yaml(read(entry["modulePath"]), module=True)
        local_text = read(entry["localModuleTemplatePath"])
        local = load_yaml(local_text, module=True)
        # OpenClash copies a previously missing parent mapping with its keys intact.
        self.assertEqual(local["proxy-providers"], {
            "liangxinyun": self.local["proxy-providers"]["liangxinyun!"],
        })
        self.assertEqual(local["proxies+"], self.local["proxies+"])
        self.assertEqual(sha(local_text), entry["localTemplateSha256"])
        original = self.default_module["rule-providers"]
        self.assertEqual(cloud["rule-providers"], {
            "oc-cn-domain": original["oc-cn-domain"],
            "Manual-Direct": original["Manual-Direct!"],
        })
        self.assertEqual({**cloud, "rule-providers": original}, self.default_module)

    def test_us_first_hop_only_admits_the_two_manual_choices(self):
        entry = self.catalog["profiles"][PROFILE]["versions"]["1.2.0"]
        module = load_yaml(read(entry["modulePath"]), module=True)
        first_hop, speed, liangxinyun = module["proxy-groups!"]
        self.assertEqual(first_hop["name"], "TikTok首跳")
        self.assertEqual(first_hop["type"], "select")
        self.assertEqual(first_hop["proxies"], ["REJECT"])
        self.assertEqual(first_hop["default-selected"], "REJECT")
        self.assertEqual(first_hop["empty-fallback"], "REJECT")
        self.assertTrue(first_hop["include-all"])
        self.assertEqual(first_hop["exclude-filter"], "^LXY: ")
        for name in (
            "REJECT", "美国Z01 | IEPL | x1.5", "美国Z02 | IEPL | x1.5  ",
        ):
            self.assertIsNotNone(re.fullmatch(first_hop["filter"], name), name)
        for name in (
            "日本Z01 | IEPL | x1.5", "美国Z03 | IEPL | x1.5", "美国Z01 | IEPL | x11.5",
            "LXY: 美国Z02 | IEPL | x1.5", "TikTok-ISP-Local", "DIRECT",
        ):
            self.assertIsNone(re.fullmatch(first_hop["filter"], name), name)
        self.assertEqual(speed, {**self.default_module["proxy-groups!"][1], "name": "TikTok测速"})
        self.assertEqual(liangxinyun, self.default_module["proxy-groups!"][2])

    def test_renamed_tiktok_groups_preserve_direct_rules_and_landing_node(self):
        versions = self.catalog["profiles"][PROFILE]["versions"]
        old = load_yaml(read(versions["1.1.1"]["modulePath"]), module=True)
        new = load_yaml(read(versions["1.2.0"]["modulePath"]), module=True)
        self.assertEqual(new["rule-providers"], old["rule-providers"])
        self.assertEqual(new["rules!"], [
            "GEOSITE,tiktok,TikTok测速" if rule == "GEOSITE,tiktok,TikTok-ISP" else rule
            for rule in old["rules!"]
        ])
        dns = old["dns"]
        policies = {
            name: [server.replace("#TikTok-ISP", "#TikTok测速") for server in servers]
            for name, servers in dns["nameserver-policy!"].items()
        }
        self.assertEqual(new["dns"], {**dns, "nameserver-policy!": policies})
        self.assertEqual(new["profile"], old["profile"])
        old_local = load_yaml(read(versions["1.1.1"]["localModuleTemplatePath"]), module=True)
        new_path = read(versions["1.2.0"]["localModuleTemplatePath"])
        new_local = load_yaml(new_path, module=True)
        self.assertEqual(new_local, {
            **old_local, "proxies+": [{**old_local["proxies+"][0], "dialer-proxy": "TikTok首跳"}],
        })
        self.assertEqual(sha(new_path), versions["1.2.0"]["localTemplateSha256"])

    def test_first_hop_filter_accepts_actual_flag_prefix_without_broadening_node_scope(self):
        versions = self.catalog["profiles"][PROFILE]["versions"]
        old = load_yaml(read(versions["1.2.0"]["modulePath"]), module=True)
        new = load_yaml(read(versions["1.2.1"]["modulePath"]), module=True)
        old_group, *remaining = old["proxy-groups!"]
        new_group = new["proxy-groups!"][0]
        actual_names = ("🇺🇲 美国Z01 | IEPL | x1.5", "🇺🇲 美国Z02 | IEPL | x1.5")
        for name in actual_names:
            self.assertIsNone(re.fullmatch(old_group["filter"], name))
            self.assertIsNotNone(re.fullmatch(new_group["filter"], name))
            self.assertIsNotNone(re.fullmatch(new_group["filter"], name.removeprefix("🇺🇲 ")))
        for name in (
            "🇺🇲 美国Z03 | IEPL | x1.5", "🇺🇲 美国Z01 | IEPL | x2",
            "🇯🇵 美国Z01 | IEPL | x1.5", "LXY: 🇺🇲 美国Z01 | IEPL | x1.5",
        ):
            self.assertIsNone(re.fullmatch(new_group["filter"], name))
        self.assertIsNotNone(re.fullmatch(new_group["filter"], "REJECT"))
        expected = {**old, "proxy-groups!": [{**old_group, "filter": new_group["filter"]}, *remaining]}
        self.assertEqual(new, expected)
        self.assertEqual(read(versions["1.2.1"]["localModuleTemplatePath"]),
                         read(versions["1.2.0"]["localModuleTemplatePath"]))

    def test_comparison_group_accepts_only_the_specified_us_and_japan_nodes(self):
        versions = self.catalog["profiles"][PROFILE]["versions"]
        old = load_yaml(read(versions["1.2.1"]["modulePath"]), module=True)
        new = load_yaml(read(versions["1.3.0"]["modulePath"]), module=True)
        old_group, *remaining = old["proxy-groups!"]
        new_group = new["proxy-groups!"][0]
        accepted = (
            "REJECT",
            "🇺🇲 美国Z01 | IEPL | x1.5", "🇺🇲 美国Z02 | IEPL | x1.5",
            *(f"🇯🇵 日本Z0{index} | IEPL" for index in range(1, 5)),
        )
        for name in accepted:
            self.assertIsNotNone(re.fullmatch(new_group["filter"], name), name)
            bare_name = name.removeprefix("🇺🇲 ").removeprefix("🇯🇵 ")
            self.assertIsNotNone(re.fullmatch(new_group["filter"], bare_name), bare_name)
        for name in (
            "🇭🇰 香港Z02 | IEPL", "🇯🇵 日本Z05 | IEPL", "🇺🇲 美国Z03 | IEPL | x1.5",
            "LXY: 🇯🇵 日本Z01 | IEPL", "🇺🇲 日本Z01 | IEPL", "DIRECT",
        ):
            self.assertIsNone(re.fullmatch(new_group["filter"], name), name)
        self.assertEqual(new, {
            **old, "proxy-groups!": [{**old_group, "filter": new_group["filter"]}, *remaining],
        })
        local = read(versions["1.3.0"]["localModuleTemplatePath"])
        self.assertEqual(load_yaml(local, module=True),
                         load_yaml(read(versions["1.2.1"]["localModuleTemplatePath"]), module=True))
        self.assertEqual(sha(local), versions["1.3.0"]["localTemplateSha256"])

    def test_liangxinyun_comparison_admits_only_eight_prefixed_bgp_nodes(self):
        versions = self.catalog["profiles"][PROFILE]["versions"]
        old = load_yaml(read(versions["1.3.0"]["modulePath"]), module=True)
        new = load_yaml(read(versions["1.4.0"]["modulePath"]), module=True)
        old_group, *remaining = old["proxy-groups!"]
        updated = dict(old_group)
        del updated["exclude-filter"]
        pattern = new["proxy-groups!"][0]["filter"]
        updated["filter"] = pattern
        for region in ("🇯🇵日本", "🇸🇬新加坡"):
            for number in range(1, 5):
                name = f"{region}专线0{number}|BGP|流媒体"
                self.assertIsNotNone(re.fullmatch(pattern, f"LXY: {name}"), name)
                self.assertIsNone(re.fullmatch(pattern, name), name)
        accepted = (
            "REJECT",
            *(f"🇺🇲 美国Z0{index} | IEPL | x1.5" for index in range(1, 3)),
            *(f"🇯🇵 日本Z0{index} | IEPL" for index in range(1, 5)),
        )
        for name in accepted:
            self.assertIsNotNone(re.fullmatch(pattern, name), name)
        for name in (
            "LXY: 🇯🇵日本专线05|BGP|流媒体", "LXY: 🇸🇬新加坡专线01|BGP|游戏",
            "LXY: 🇭🇰香港专线01|BGP|流媒体", "LXY: 🇯🇵 日本Z01 | IEPL",
            "LXY: 🇯🇵日本专线03|BGP|流媒体额外", "DIRECT",
        ):
            self.assertIsNone(re.fullmatch(pattern, name), name)
        self.assertEqual(new, {**old, "proxy-groups!": [updated, *remaining]})
        local = read(versions["1.4.0"]["localModuleTemplatePath"])
        self.assertEqual(load_yaml(local, module=True),
                         load_yaml(read(versions["1.3.0"]["localModuleTemplatePath"]), module=True))
        self.assertEqual(sha(local), versions["1.4.0"]["localTemplateSha256"])

    def test_acceptance_candidate_limits_the_first_hop_to_ikuuu_japan(self):
        versions = self.catalog["profiles"][PROFILE]["versions"]
        old = load_yaml(read(versions["1.4.0"]["modulePath"]), module=True)
        new = load_yaml(read(versions["1.5.0"]["modulePath"]), module=True)
        original, *remaining = old["proxy-groups!"]
        pattern = new["proxy-groups!"][0]["filter"]
        for number in range(1, 5):
            name = f"日本Z0{number} | IEPL"
            self.assertIsNotNone(re.fullmatch(pattern, name), name)
            self.assertIsNotNone(re.fullmatch(pattern, f"🇯🇵 {name}"), name)
        self.assertIsNotNone(re.fullmatch(pattern, "REJECT"))
        for name in (
            "🇺🇲 美国Z01 | IEPL | x1.5", "🇯🇵 日本Z05 | IEPL", "LXY: 🇯🇵 日本Z04 | IEPL",
            "LXY: 🇯🇵日本专线04|BGP|流媒体", "LXY: 🇸🇬新加坡专线04|BGP|流媒体", "DIRECT",
        ):
            self.assertIsNone(re.fullmatch(pattern, name), name)
        self.assertEqual(new, {**old, "proxy-groups!": [{**original, "filter": pattern}, *remaining]})
        local = read(versions["1.5.0"]["localModuleTemplatePath"])
        self.assertEqual(load_yaml(local, module=True),
                         load_yaml(read(versions["1.4.0"]["localModuleTemplatePath"]), module=True))
        self.assertEqual(sha(local), versions["1.5.0"]["localTemplateSha256"])
