import subprocess
import unittest

from strict_yaml import load_yaml
from validate_repository import ROOT


BASELINE = "57ff42265dd3dffe44e86b7f78206b3d768f3d81"
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

    def test_v101_keeps_baseline_rules_and_uses_tiktok_isp_group(self):
        candidate = CANDIDATE.parent / "v1.0.1"
        module = load_yaml((candidate / "openclash-overwrite.conf").read_text(encoding="utf-8"), module=True)
        expected = self.module.copy()
        groups = expected.pop("proxy-groups!")
        expected["rules!"] = [
            "GEOSITE,tiktok,TikTok-ISP" if rule == f"GEOSITE,tiktok,{TIKTOK}" else rule
            for rule in expected["rules!"]
        ]
        dns = expected["dns"].copy()
        policy = dns["nameserver-policy!"].copy()
        policy["geosite:tiktok"] = [url.replace(f"#{TIKTOK}", "#TikTok-ISP") for url in policy["geosite:tiktok"]]
        dns["nameserver-policy!"] = policy
        expected["dns"] = dns

        new_groups = module.pop("proxy-groups!")
        self.assertEqual(module, expected)
        self.assertEqual(new_groups[2:], groups)
        first, isp = new_groups[:2]
        self.assertEqual(first["name"], "TikTok-首跳")
        self.assertEqual(first["type"], "fallback")
        self.assertEqual(first["proxies"], ["iKuuu-US-Z01", "iKuuu-US-Z02"])
        self.assertEqual(first["interval"], 60)
        self.assertEqual(isp["name"], "TikTok-ISP")
        self.assertEqual(isp["type"], "select")
        self.assertEqual(isp["proxies"], [TIKTOK])
        self.assertEqual(isp["interval"], 300)
        for group in (first, isp):
            self.assertEqual(group["url"], "https://www.gstatic.com/generate_204")
            self.assertFalse(group["lazy"])
            self.assertEqual(group["expected-status"], 204)
            self.assertEqual(group["empty-fallback"], "REJECT")

    def test_v101_local_template_links_only_the_two_us_nodes_and_isp(self):
        candidate = CANDIDATE.parent / "v1.0.1"
        local = load_yaml((candidate / "local-tiktok-proxy.conf").read_text(encoding="utf-8"), module=True)
        self.assertEqual(set(local), set(self.local))
        self.assertEqual(local["proxy-providers!"], self.local["proxy-providers!"])
        z01, z02, isp = local["proxies!"]
        self.assertEqual(z01["name"], "iKuuu-US-Z01")
        self.assertEqual(z02["name"], "iKuuu-US-Z02")
        self.assertEqual(isp, {**self.local["proxies!"][1], "dialer-proxy": "TikTok-首跳"})
