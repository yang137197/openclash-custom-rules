"""Build the native dual-subscription candidate; no router or credentials access."""
import hashlib
import json
from pathlib import Path

import yaml

from strict_yaml import load_yaml
from sync_manual_direct import parse_payload

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "tiktok-router-dual-subscription-jp"
VERSION = "1.0.0"
DIRECTORY = ROOT / "profiles" / PROFILE / "versions" / f"v{VERSION}"
FIRST = "TikTok首跳"
EXIT = "Tiktok美国出口测速"
MEDIA = "良心云-日本专线流媒体"
DEFAULT = "ikuuu-默认代理"
TEST_URL = "https://www.gstatic.com/generate_204"
IK_FILTER = r"(?i)日本\s*Z\s*[0-9]+\s*\|\s*IEPL(?:\s|\||$)"
# The service's xx convention is two digits. Explicit filters impose order even
# if the subscription shuffles nodes. Arbitrary renamed/un-numbered nodes never
# silently receive a priority inferred from subscription order.
LXY_FILTERS = [
    rf"(?i)日本\s*{kind}\s*{number:02d}\s*\|\s*BGP\s*\|\s*{network}(?:\s|\||$)"
    for kind, network in (("专线", "流媒体"), ("高速", "CUCM"))
    for number in range(1, 100)
]
LXY_FILTER = "`".join(LXY_FILTERS)
LXY_MEMBER_FILTER = r"(?i)日本\s*(?:专线\s*(?:0[1-9]|[1-9][0-9])\s*\|\s*BGP\s*\|\s*流媒体|高速\s*(?:0[1-9]|[1-9][0-9])\s*\|\s*BGP\s*\|\s*CUCM)(?:\s|\||$)"
SERVICES = ("youtube", "netflix", "telegram", "disney", "hbo", "primevideo",
            "twitch", "spotify", "apple-tvplus", "steam", "epicgames", "blizzard",
            "mega", "dropbox")


def dump(document):
    return yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=100000)


def cloud(payload):
    baseline = load_yaml((ROOT / "profiles/tiktok-router-loongproxy-jp-us/overwrite/openclash-overwrite.conf").read_text(encoding="utf-8"), module=True)
    dns = baseline["dns"]
    for addresses in dns["nameserver-policy!"].values():
        for index, address in enumerate(addresses):
            addresses[index] = address.replace("#TikTok-ISP", "#" + EXIT).replace("#美国", "#" + DEFAULT)
    common = dict(url=TEST_URL, interval=60, timeout=5000, lazy=False,
                  **{"expected-status": "204", "empty-fallback": "REJECT"})
    def automatic(name, provider, kind, pattern):
        return dict(name=name, type=kind, use=[provider], filter=pattern,
                    **common, **({"tolerance": 0} if kind == "url-test" else {}))
    groups = [automatic(FIRST, "dual-ikuuu", "url-test", IK_FILTER),
              dict(name=EXIT, type="select", **{"include-all-proxies": True,
                   "filter": "^TikTok-ISP-Local$"}, **common),
              automatic(MEDIA, "dual-liangxinyun", "fallback", LXY_FILTER),
              automatic(DEFAULT, "dual-ikuuu", "url-test", IK_FILTER)]
    providers = {"oc-cn-domain": dict(baseline["rule-providers"]["oc-cn-domain"], proxy=DEFAULT)}
    for service in SERVICES:
        providers["dual-" + service] = dict(type="http", behavior="domain", format="mrs",
            proxy=DEFAULT, url=f"https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/{service}.mrs",
            path=f"./rule_provider/dual-{service}.mrs", interval=86400)
    # Plain nested keys also work when the base has no rule-providers mapping.
    # OpenClash does not recursively interpret suffix operators in a new hash.
    providers["Manual-Direct"] = dict(type="inline", behavior="classical", payload=payload)
    # Existing exceptions retain priority over each newly introduced service.
    # Exclusions preserve Manual-Direct and CN behavior without moving the
    # baseline Google-before-Manual rules or touching the source list.
    def media_rule(condition):
        return (f"AND,(({condition}),(NOT,((RULE-SET,Manual-Direct))),"
                f"(NOT,((RULE-SET,oc-cn-domain))),(NOT,((GEOIP,CN,no-resolve)))),{MEDIA}")
    private = baseline["rules!"][:12]
    rules = private + [f"GEOSITE,tiktok,{EXIT}", "GEOSITE,tiktok,REJECT"]
    rules += [media_rule("RULE-SET,dual-" + service) for service in SERVICES]
    rules += [media_rule("GEOIP,telegram,no-resolve")]
    rules += [media_rule("DOMAIN-SUFFIX," + host) for host in
              ("release-assets.githubusercontent.com", "objects.githubusercontent.com")]
    rules += [f"DOMAIN-SUFFIX,xn--ngstr-lra8j.com,{DEFAULT}", f"GEOSITE,google,{DEFAULT}",
              "RULE-SET,Manual-Direct,DIRECT", "RULE-SET,oc-cn-domain,DIRECT",
              "GEOIP,CN,DIRECT,no-resolve", f"MATCH,{DEFAULT}"]
    return dict(ipv6=baseline["ipv6"], profile=baseline["profile"], dns=dns,
                **{"proxy-groups!": groups, "rule-providers": providers, "rules!": rules})


def local():
    health = dict(enable=True, url=TEST_URL, interval=60, timeout=5000,
                  lazy=False, **{"expected-status": "204"})
    providers = {}
    for key, placeholder, pattern in (("dual-ikuuu", "FILL_ME_IKUUU_SUBSCRIPTION_URL", IK_FILTER),
                                     ("dual-liangxinyun", "FILL_ME_LIANGXINYUN_SUBSCRIPTION_URL", LXY_MEMBER_FILTER)):
        providers[key] = dict(type="http", url=placeholder, path=f"./proxy_provider/{key}.yaml",
                              interval=3600, proxy="DIRECT", filter=pattern,
                              override={"additional-prefix": "IK: " if key == "dual-ikuuu" else "LXY: "},
                              **{"health-check": health})
    proxy = dict(name="TikTok-ISP-Local", type="socks5", server="FILL_ME_PROXY_HOST",
                 port="FILL_ME_PROXY_PORT", username="FILL_ME_USERNAME", password="FILL_ME_PASSWORD",
                 udp=False, **{"dialer-proxy": FIRST})
    # Initialize a missing DNS hash before the cloud's nested suffix operators.
    # Merging an empty hash preserves every pre-existing DNS setting.
    return {"dns": {}, "proxy-providers": providers, "proxies+": [proxy]}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build():
    payload = parse_payload((ROOT / "rules/manual-direct.yaml").read_text(encoding="utf-8"))
    write(DIRECTORY / "openclash-overwrite.conf", "# Native dual-subscription candidate; generated by scripts/build_dual_subscription.py\n[YAML]\n" + dump(cloud(payload)))
    write(DIRECTORY / "local-tiktok-proxy.conf", "# Router-local placeholders only. Never publish a filled copy.\n[YAML]\n" + dump(local()))
    return payload


if __name__ == "__main__":
    print(f"Built {PROFILE} v{VERSION}; Manual-Direct entries={len(build())}")
