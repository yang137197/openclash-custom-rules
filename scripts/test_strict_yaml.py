import unittest

from strict_yaml import load_yaml


class StrictYamlTests(unittest.TestCase):
    def test_rejects_broken_quote_from_japan_profile(self):
        with self.assertRaises(ValueError):
            load_yaml("[YAML]\nproxy-groups!:\n"
                      "  - name: 日本-入口\n"
                      "    exclude-filter: '(?i)^TikTok-ISP-Local  - name: TikTok-ISP\n"
                      "    filter: '^TikTok-ISP-Local$'\n", module=True)

    def test_rejects_duplicate_sections_and_nested_keys(self):
        for body in ("rules!: []\nrules!: []\n",
                     "dns:\n  enable: true\n  enable: false\n"):
            with self.subTest(body=body), self.assertRaisesRegex(ValueError, "duplicate key"):
                load_yaml("[YAML]\n" + body, module=True)

    def test_preserves_operator_keys_and_duplicate_rule_entries(self):
        data = load_yaml("[YAML]\nproxies+: []\nfallback-filter-:\n"
                         "rules!:\n  - DOMAIN-SUFFIX,example.com,DIRECT\n"
                         "  - DOMAIN-SUFFIX,example.com,DIRECT\n", module=True)
        self.assertEqual(len(data["rules!"]), 2)
        self.assertEqual(data["proxies+"], [])
        self.assertIsNone(data["fallback-filter-"])


if __name__ == "__main__":
    unittest.main()
