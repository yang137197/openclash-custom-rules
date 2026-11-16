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
