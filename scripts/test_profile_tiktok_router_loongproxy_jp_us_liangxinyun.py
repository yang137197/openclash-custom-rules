"""Regression checks for the candidate with a separate Liangxinyun subscription."""

import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest

from strict_yaml import load_yaml
from sync_manual_direct import SOURCE_PATH, synchronize
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

    def test_rollings_share_the_source_without_editing_versioned_modules(self):
        rules = ["DOMAIN,only.example.com", "DOMAIN-SUFFIX,new.example.net", "DOMAIN,only.example.com"]
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog = self.catalog["profiles"]
            enabled = {profile_id: catalog[profile_id] for profile_id in (JP, PROFILE)}
            relative_source = root / SOURCE_PATH
            relative_source.parent.mkdir()
            relative_source.write_text("payload:\n" + "".join(f"  - {rule}\n" for rule in rules), encoding="utf-8")
            index = root / "profiles/catalog.json"
            for entry in enabled.values():
                rolling = root / entry["latestModulePath"]
                rolling.parent.mkdir(parents=True)
                rolling.write_text(read(entry["latestModulePath"]), encoding="utf-8")
                snapshot_path = entry["versions"][entry["currentVersion"]]["modulePath"]
                snapshot = root / snapshot_path
                snapshot.parent.mkdir(parents=True)
                snapshot.write_text(read(snapshot_path), encoding="utf-8")
            index.write_text(json.dumps({"profiles": enabled}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            self.assertTrue(synchronize(root, write=True))
            resulting = json.loads(index.read_text(encoding="utf-8"))["profiles"]
            for profile_id, provider_name in ((JP, "Manual-Direct!"), (PROFILE, "Manual-Direct")):
                entry = resulting[profile_id]
                rolling_text = (root / entry["latestModulePath"]).read_text(encoding="utf-8")
                self.assertEqual(load_yaml(rolling_text, module=True)["rule-providers"][provider_name]["payload"], rules)
                self.assertEqual(sha(rolling_text), entry["latestModuleSha256"])
                snapshot = entry["versions"][entry["currentVersion"]]["modulePath"]
                self.assertEqual((root / snapshot).read_text(encoding="utf-8"), read(snapshot))
            self.assertFalse(synchronize(root, write=False))

    def automatic_candidate(self):
        entry = self.catalog["profiles"][PROFILE]["versions"]["1.6.0"]
        return entry, load_yaml(read(entry["modulePath"]), module=True)

    def test_automatic_candidate_preserves_tiktok_dns_rules_and_direct_snapshot(self):
        entry, module = self.automatic_candidate()
        rolling_path = self.catalog["profiles"][PROFILE]["latestModulePath"]
        # A candidate is a snapshot; later daily source updates must remain free
        # to change the rolling module without rewriting this historical input.
        baseline = load_yaml(git("show", f"3372eb5:{rolling_path}"), module=True)
        for key in baseline:
            if key != "proxy-groups!":
                self.assertEqual(module[key], baseline[key], key)
        self.assertEqual(set(module), set(baseline) | {"proxy-providers"})
        self.assertEqual(module["proxy-groups!"][:2], baseline["proxy-groups!"][:2])
        self.assertEqual(read(entry["localModuleTemplatePath"]),
                         read(self.catalog["profiles"][PROFILE]["versions"]["1.5.0"]["localModuleTemplatePath"]))
        self.assertEqual(self.catalog["profiles"][PROFILE]["currentVersion"], "1.5.0")
        self.assertEqual(entry["status"], "candidate")

    def test_automatic_candidate_accepts_numbered_categories_and_excludes_other_nodes(self):
        _, module = self.automatic_candidate()
        groups = {g["name"]: g for g in module["proxy-groups!"]}
        provider_filter = module["proxy-providers"]["liangxinyun"]["filter"]
        cases = {
            "日本专线": ("🇯🇵日本专线01|BGP|流媒体", "日本专线12|BGP|流媒体"),
            "日本高速": ("🇯🇵日本高速04|BGP|CUCM", "日本高速11|BGP|CUCM"),
            "美国流媒体": ("🇺🇸美国05|流媒体|0.1x", "美国流媒体12|BGP", "流媒体|美国09"),
            "美国高速": ("🇺🇸美国高速05|CTCU|0.1x", "美国高速12|BGP"),
        }
        for category, names in cases.items():
            for raw in names:
                name = "LXY: " + raw
                self.assertIsNotNone(re.search(provider_filter, name), name)
                matched = [key for key in cases if re.search(groups["良心云-" + key]["filter"], name)]
                self.assertEqual(matched, [category], name)
        for name in ("LXY: 🇭🇰香港专线01|BGP|流媒体", "LXY: 🇸🇬新加坡专线01|BGP|流媒体",
                     "LXY: 美国普通01|BGP", "LXY: 日本普通01|BGP", "TikTok-ISP-Local", "REJECT"):
            self.assertIsNone(re.search(provider_filter, name), name)

    def test_automatic_candidate_priority_is_separate_from_latency_and_fails_closed(self):
        _, module = self.automatic_candidate()
        _, _, total, *tiers = module["proxy-groups!"]
        expected_names = ["良心云-" + c for c in ("日本专线", "日本高速", "美国流媒体", "美国高速")]
        self.assertEqual(total["name"], "良心云")
        self.assertEqual(total["type"], "fallback")
        self.assertEqual(total["proxies"], expected_names)
        self.assertNotIn("use", total)
        self.assertEqual([tier["name"] for tier in tiers], expected_names)
        for tier in tiers:
            self.assertEqual(tier["type"], "url-test")
            self.assertEqual(tier["use"], ["liangxinyun"])
            self.assertEqual(tier["tolerance"], 0)
            for forbidden in ("proxies", "include-all", "include-all-providers", "include-all-proxies", "default-selected"):
                self.assertNotIn(forbidden, tier)
        for group in (total, *tiers):
            self.assertEqual(group["empty-fallback"], "REJECT")
            self.assertIs(group["lazy"], False)
            self.assertEqual((group["interval"], group["timeout"], group["expected-status"]), (60, 5000, 204))
            self.assertEqual(group["url"], "https://www.gstatic.com/generate_204")

    def test_automatic_candidate_checks_provider_nodes_without_overwriting_credentials(self):
        _, module = self.automatic_candidate()
        provider = module["proxy-providers"]["liangxinyun"]
        self.assertEqual(set(module["proxy-providers"]), {"liangxinyun"})
        self.assertEqual(set(provider), {"filter", "health-check"})
        self.assertEqual(provider["health-check"], {
            "enable": True, "url": "https://www.gstatic.com/generate_204", "expected-status": 204,
            "interval": 60, "timeout": 5000, "lazy": False,
        })

    def test_strict_controller_candidate_preserves_stable_routing_and_local_credentials_template(self):
        profile = self.catalog["profiles"][PROFILE]
        entry = profile["versions"]["1.7.0"]
        module = load_yaml(read(entry["modulePath"]), module=True)
        baseline = load_yaml(git("show", f"3372eb5:{profile['latestModulePath']}"), module=True)
        for key in baseline:
            if key != "proxy-groups!":
                self.assertEqual(module[key], baseline[key], key)
        self.assertEqual(module["proxy-groups!"][:2], baseline["proxy-groups!"][:2])
        self.assertEqual(set(module), set(baseline) | {"proxy-providers"})
        self.assertEqual(read(entry["localModuleTemplatePath"]),
                         read(profile["versions"]["1.5.0"]["localModuleTemplatePath"]))

    def test_strict_controller_candidate_exposes_only_a_guarded_leaf_selector(self):
        entry = self.catalog["profiles"][PROFILE]["versions"]["1.7.0"]
        module = load_yaml(read(entry["modulePath"]), module=True)
        _, _, group = module["proxy-groups!"]
        pattern = module["proxy-providers"]["liangxinyun"]["filter"]
        self.assertEqual(group, {
            "name": "良心云", "type": "select", "proxies": ["REJECT"], "default-selected": "REJECT",
            "use": ["liangxinyun"], "filter": pattern, "empty-fallback": "REJECT",
        })
        _, automatic = self.automatic_candidate()
        self.assertEqual(module["proxy-providers"], automatic["proxy-providers"])

    def test_strict_controller_artifacts_are_hashed_and_runtime_acceptance_is_pending(self):
        profile = self.catalog["profiles"][PROFILE]
        entry = profile["versions"]["1.7.0"]
        directory = entry["versionDirectory"]
        for field, filename in (("controller", "liangxinyun-controller.rb"),
                                ("controllerService", "liangxinyun-controller.init")):
            self.assertEqual(entry[field + "Path"], directory + "/" + filename)
            self.assertEqual(entry[field + "Sha256"], sha(read(entry[field + "Path"])))
        self.assertEqual(profile["currentVersion"], "1.5.0")
        self.assertEqual(entry["status"], "candidate")
        environment = json.loads(read(entry["environmentPath"]))
        self.assertEqual(environment["status"], "pending")
        self.assertEqual(environment["evidence"]["runtimeAcceptance"], "not-run")
        self.assertFalse(environment["evidence"]["userConfirmed"])

    def test_lua_candidate_keeps_routing_dns_tiktok_and_local_template(self):
        profile = self.catalog["profiles"][PROFILE]
        entry = profile["versions"]["1.8.0"]
        before = profile["versions"]["1.7.0"]
        self.assertEqual(load_yaml(read(entry["modulePath"]), module=True),
                         load_yaml(read(before["modulePath"]), module=True))
        self.assertEqual(read(entry["localModuleTemplatePath"]), read(before["localModuleTemplatePath"]))
        self.assertEqual(profile["currentVersion"], "1.5.0")
        self.assertEqual(entry["status"], "candidate")

    def test_lua_candidate_has_complete_hashed_artifacts_and_pending_acceptance(self):
        entry = self.catalog["profiles"][PROFILE]["versions"]["1.8.0"]
        self.assertEqual(entry["controllerRuntime"], "lua5.1")
        for field, filename in (("controller", "liangxinyun-controller.lua"),
                                ("controllerService", "liangxinyun-controller.init"),
                                ("controllerSupervisor", "liangxinyun-controller.run")):
            self.assertEqual(entry[field + "Path"], entry["versionDirectory"] + "/" + filename)
            self.assertEqual(entry[field + "Sha256"], sha(read(entry[field + "Path"])))
        env = json.loads(read(entry["environmentPath"]))
        self.assertEqual(env["status"], "pending")
        self.assertEqual(env["evidence"]["runtimeAcceptance"], "not-run")
        self.assertFalse(env["evidence"]["userConfirmed"])

    def test_lua_permission_fix_changes_only_two_open_modes_and_preserves_routing(self):
        profile = self.catalog["profiles"][PROFILE]
        before, after = (profile["versions"][v] for v in ("1.8.0", "1.8.1"))
        self.assertEqual(read(before["controllerPath"]).count(', 384)'), 2)
        self.assertEqual(read(after["controllerPath"]),
                         read(before["controllerPath"]).replace(', 384)', ', "rw-------")'))
        self.assertEqual(load_yaml(read(before["modulePath"]), module=True),
                         load_yaml(read(after["modulePath"]), module=True))
        for field in ("localModuleTemplatePath", "controllerServicePath", "controllerSupervisorPath"):
            self.assertEqual(read(before[field]), read(after[field]))

    def test_lua_permission_fix_candidate_keeps_pending_runtime_acceptance(self):
        profile = self.catalog["profiles"][PROFILE]
        entry = profile["versions"]["1.8.1"]
        self.assertEqual(profile["currentVersion"], "1.5.0")
        self.assertEqual(entry["status"], "candidate")
        for key in ("module", "controller", "controllerService", "controllerSupervisor"):
            self.assertEqual(entry[key + "Sha256"], sha(read(entry[key + "Path"])))
        env = json.loads(read(entry["environmentPath"]))
        self.assertEqual(env["status"], "pending")
        self.assertEqual(env["evidence"]["runtimeAcceptance"], "not-run")
        self.assertFalse(env["evidence"]["userConfirmed"])

    def test_v182_complete_candidate_preserves_runtime_and_is_not_published(self):
        profile = self.catalog["profiles"][PROFILE]
        before, after = (profile["versions"][v] for v in ("1.8.1", "1.8.2"))
        self.assertEqual(profile["currentVersion"], "1.5.0")
        self.assertEqual(after["status"], "candidate")
        self.assertEqual(after["moduleUsage"], "reference-only")
        for field in ("controllerPath", "controllerServicePath", "controllerSupervisorPath", "localModuleTemplatePath"):
            self.assertEqual(read(before[field]), read(after[field]))
        self.assertEqual(load_yaml(read(before["modulePath"]), module=True), load_yaml(read(after["modulePath"]), module=True))
        env = json.loads(read(after["environmentPath"]))
        self.assertEqual(env["evidence"]["runtimeAcceptance"], "not-run")
        self.assertFalse(env["evidence"]["userConfirmed"])

    def test_v182_public_manifest_and_scope_contract(self):
        entry = self.catalog["profiles"][PROFILE]["versions"]["1.8.2"]
        manifest = json.loads(read(entry["bundleManifestPath"]))
        self.assertEqual(manifest["version"], "1.8.2")
        self.assertFalse(manifest["targetRouterTested"])
        for filename, checksum in manifest["files"].items():
            self.assertEqual(checksum, sha(read(entry["versionDirectory"] + "/" + filename)))
        for field in ("incrementalModule", "scopeGuard", "mergeHelper", "bundleManifest"):
            self.assertEqual(entry[field + "Sha256"], sha(read(entry[field + "Path"])))
        patch = load_yaml(read(entry["incrementalModulePath"]), module=True)
        self.assertEqual(set(patch), {"proxy-groups*", "proxy-providers*"})
        self.assertEqual(patch["proxy-groups*"]["where"], {"name": "良心云"})
        self.assertEqual(patch["proxy-providers*"]["where"], {"key": "liangxinyun"})
        self.assertEqual(patch["proxy-groups*"]["set"]["proxies!"], ["REJECT"])
        self.assertEqual(patch["proxy-providers*"]["set"]["health-check!"]["expected-status"], 204)


    def test_v183_native_auto_wrapper_has_one_guarded_internal_selector(self):
        entry = self.catalog["profiles"][PROFILE]["versions"]["1.8.3"]
        module = load_yaml(read(entry["modulePath"]), module=True)
        groups = {g["name"]: g for g in module["proxy-groups!"]}
        outer, inner = groups["良心云"], groups["良心云-严格控制"]
        self.assertEqual(outer["type"], "url-test")
        self.assertEqual(outer["proxies"], ["良心云-严格控制"])
        self.assertNotIn("use", outer)
        self.assertFalse(outer["hidden"])
        self.assertEqual(outer["empty-fallback"], "REJECT")
        self.assertEqual(inner["type"], "select")
        self.assertEqual(inner["proxies"], ["REJECT"])
        self.assertEqual(inner["use"], ["liangxinyun"])
        self.assertTrue(inner["hidden"])
        self.assertEqual(inner["default-selected"], "REJECT")
        self.assertEqual(self.catalog["profiles"][PROFILE]["currentVersion"], "1.5.0")

    def test_v183_keeps_policy_bytes_and_public_artifact_integrity(self):
        versions = self.catalog["profiles"][PROFILE]["versions"]
        prior, entry = versions["1.8.2"], versions["1.8.3"]
        before, after = read(prior["controllerPath"]), read(entry["controllerPath"])
        policy = lambda s: s[s.index("local function finite"):s.index("local function names")]
        self.assertEqual(policy(before), policy(after))
        for field in ("controllerServicePath", "controllerSupervisorPath", "localModuleTemplatePath"):
            self.assertEqual(read(prior[field]), read(entry[field]))
        manifest = json.loads(read(entry["bundleManifestPath"]))
        self.assertEqual(manifest["version"], "1.8.3")
        for name, checksum in manifest["files"].items():
            self.assertEqual(checksum, sha(read(entry["versionDirectory"] + "/" + name)))
        env = json.loads(read(entry["environmentPath"]))
        self.assertFalse(env["evidence"]["userConfirmed"])
        self.assertEqual(env["evidence"]["runtimeAcceptance"], "not-run")
        patch = load_yaml(read(entry["incrementalModulePath"]), module=True)
        self.assertEqual(set(patch), {"proxy-groups*", "proxy-groups+", "proxy-providers*"})
        self.assertEqual(patch["proxy-groups*"]["where"], {"name": "良心云"})
        self.assertEqual(patch["proxy-groups+"][0]["name"], "良心云-严格控制")

    def test_v184_visible_nodes_and_native_probes_preserve_manual_tiktok_and_strict_routes(self):
        versions = self.catalog['profiles'][PROFILE]['versions']
        old, new = versions['1.8.3'], versions['1.8.4']
        before = load_yaml(read(old['modulePath']), module=True)
        after = load_yaml(read(new['modulePath']), module=True)
        groups = {g['name']: g for g in after['proxy-groups!']}
        probe = {'url': 'https://www.gstatic.com/generate_204', 'interval': 60,
                 'timeout': 5000, 'lazy': False, 'expected-status': 204}
        for group in groups.values():
            self.assertEqual({k: group[k] for k in probe}, probe)
        self.assertFalse(groups['良心云-严格控制']['hidden'])
        self.assertEqual(groups['良心云']['proxies'], ['良心云-严格控制'])
        self.assertEqual(groups['良心云-严格控制']['use'], ['liangxinyun'])
        for group in groups.values():
            if group['name'] != '良心云':
                self.assertEqual(group['type'], 'select')
        old_groups = {g['name']: g for g in before['proxy-groups!']}
        for name in ('TikTok首跳', 'TikTok测速'):
            self.assertEqual({k:v for k,v in groups[name].items() if k not in probe}, old_groups[name])
        self.assertEqual({k:v for k,v in after.items() if k != 'proxy-groups!'},
                         {k:v for k,v in before.items() if k != 'proxy-groups!'})
        for field in ('controllerPath', 'controllerSupervisorPath', 'controllerServicePath',
                      'localModuleTemplatePath', 'mergeHelperPath'):
            self.assertEqual(read(new[field]), read(old[field]))
        manifest = json.loads(read(new['bundleManifestPath']))
        self.assertFalse(manifest['targetRouterTested'])
        self.assertEqual(manifest['version'], '1.8.4')
        for name, checksum in manifest['files'].items():
            self.assertEqual(checksum, sha(read(new['versionDirectory'] + '/' + name)))
        env = json.loads(read(new['environmentPath']))
        self.assertEqual(env['evidence']['runtimeAcceptance'], 'not-run')
        self.assertFalse(env['evidence']['userConfirmed'])
