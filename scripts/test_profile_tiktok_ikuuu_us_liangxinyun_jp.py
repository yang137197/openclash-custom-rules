import subprocess
import unittest

from strict_yaml import load_yaml
from validate_repository import ROOT


BASELINE = "f59e24c2f0400528ffac393aff4f0270b861c360"
BASE_MODULE = "profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf"
CANDIDATE = ROOT / "profiles/tiktok-ikuuu-us-liangxinyun-jp/versions/v1.0.0"
JAPAN = "良心云-日本"
TIKTOK = "TikTok-ISP-Local"
FIRST_HOP = "iKuuu-US-FirstHop"


class DualSubscriptionProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        baseline = subprocess.check_output(
            ["git", "show", f"{BASELINE}:{BASE_MODULE}"], cwd=ROOT, encoding="utf-8"
        )
        cls.baseline = load_yaml(baseline, module=True)
        cls.module = load_yaml((CANDIDATE / "openclash-overwrite.conf").read_text(encoding="utf-8"), module=True)
        cls.local = load_yaml((CANDIDATE / "local-tiktok-proxy.conf").read_text(encoding="utf-8"), module=True)

    def test_routing_keeps_order_and_limits_us_chain_to_tiktok(self):
        previous_targets = {"美国": JAPAN, "TikTok-ISP": JAPAN}
        expected = []
        for rule in self.baseline["rules!"]:
            match, target = rule.rsplit(",", 1)
            if rule == "GEOSITE,tiktok,TikTok-ISP":
                expected.append(f"{match},{TIKTOK}")
            else:
                expected.append(f"{match},{previous_targets.get(target, target)}")
        self.assertEqual(self.module["rules!"], expected)
        tiktok = expected.index(f"GEOSITE,tiktok,{TIKTOK}")
        self.assertEqual(expected[tiktok + 1], "GEOSITE,tiktok,REJECT")
        self.assertEqual(expected[-1], f"MATCH,{JAPAN}")

    def test_rule_providers_and_dns_only_change_outbound_targets(self):
        providers = self.baseline["rule-providers"]
        providers["oc-cn-domain"]["proxy"] = JAPAN
        self.assertEqual(self.module["rule-providers"], providers)
        dns = self.baseline["dns"].copy()
        dns["nameserver-policy!"] = {
            domain: [url.replace("#TikTok-ISP", f"#{TIKTOK}").replace("#美国", f"#{JAPAN}") for url in servers]
            for domain, servers in dns["nameserver-policy!"].items()
        }
        self.assertEqual(self.module["dns"], dns)

    def test_node_sources_and_empty_group_are_explicit(self):
        self.assertEqual(self.module["proxy-groups!"], [{
            "name": JAPAN, "type": "select", "use": ["Liangxinyun-JP"], "empty-fallback": "REJECT",
        }])
        self.assertEqual(set(self.local), {"proxies!", "proxy-providers!"})
        first, isp = self.local["proxies!"]
        self.assertEqual(first["name"], FIRST_HOP)
        self.assertEqual(isp["name"], TIKTOK)
        self.assertEqual(isp["dialer-proxy"], FIRST_HOP)
        self.assertIs(isp["udp"], False)
        self.assertEqual(set(self.local["proxy-providers!"]), {"Liangxinyun-JP"})
        provider = self.local["proxy-providers!"]["Liangxinyun-JP"]
        self.assertEqual(provider["proxy"], "DIRECT")
        self.assertEqual(provider["filter"], "^FILL_ME_VERIFIED_JAPAN_NODE_NAME$")
