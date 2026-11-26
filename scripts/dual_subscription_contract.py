"""Runtime contract shared by stable validation and mutation regressions."""
from build_dual_subscription import FIRST, EXIT, MEDIA, DEFAULT, LXY_FILTER, LXY_MEMBER_FILTER, TEST_URL

def _require(condition, message):
    if not condition:
        raise ValueError(message)

def validate(cloud, local, payload):
    groups = {g['name']: g for g in cloud['proxy-groups!']}
    _require(list(groups) == [FIRST, EXIT, MEDIA, DEFAULT], 'four public groups')
    _require(groups[FIRST]['use'] == groups[DEFAULT]['use'] == ['dual-ikuuu'], 'iKuuu isolated')
    _require(groups[MEDIA]['use'] == ['dual-liangxinyun'], 'media isolated')
    _require(groups[FIRST]['type'] == groups[DEFAULT]['type'] == 'url-test', 'minimum delay')
    _require(groups[MEDIA]['type'] == 'fallback', 'fixed priority')
    _require(groups[MEDIA]['filter'] == LXY_FILTER, 'ordered priority filters')
    for group in groups.values():
        _require(group['url'] == TEST_URL and group['interval'] == 60 and (group['timeout'] == 5000), 'native dual-subscription contract mismatch')
        _require(group['lazy'] is False and group['expected-status'] == '204', 'native dual-subscription contract mismatch')
        _require(group['empty-fallback'] == 'REJECT', 'native dual-subscription contract mismatch')
        _require(not group.get('include-all') and (not group.get('include-all-providers')), 'native dual-subscription contract mismatch')
        _require(not group.get('hidden'), 'native dual-subscription contract mismatch')
    _require(groups[EXIT]['type'] == 'select' and groups[EXIT]['filter'] == '^TikTok-ISP-Local$', 'native dual-subscription contract mismatch')
    _require(not groups[EXIT].get('use') and (not groups[EXIT].get('proxies')), 'native dual-subscription contract mismatch')
    _require(len(local['proxies+']) == 1, 'native dual-subscription contract mismatch')
    isp = local['proxies+'][0]
    _require((isp['name'], isp['type'], isp['udp'], isp['dialer-proxy']) == ('TikTok-ISP-Local', 'socks5', False, FIRST), 'native dual-subscription contract mismatch')
    _require(set(local['proxy-providers']) == {'dual-ikuuu', 'dual-liangxinyun'}, 'native dual-subscription contract mismatch')
    _require(local['proxy-providers']['dual-liangxinyun']['filter'] == LXY_MEMBER_FILTER, 'native dual-subscription contract mismatch')
    for provider in local['proxy-providers'].values():
        health = provider['health-check']
        _require(health == dict(enable=True, url=TEST_URL, interval=60, timeout=5000, lazy=False, **{'expected-status': '204'}), 'native dual-subscription contract mismatch')
        _require(provider['url'].startswith('FILL_ME_'), 'native dual-subscription contract mismatch')
    _require(cloud['rule-providers']['Manual-Direct']['payload'] == payload, 'manual list/order/duplicates')
    rules = cloud['rules!']
    tiktok = rules.index('GEOSITE,tiktok,' + EXIT)
    _require(rules[tiktok + 1] == 'GEOSITE,tiktok,REJECT', 'native dual-subscription contract mismatch')
    _require(rules[-1] == 'MATCH,' + DEFAULT, 'native dual-subscription contract mismatch')
    for rule in rules:
        if rule.endswith(',' + MEDIA):
            _require(rules.index(rule) > tiktok + 1, 'native dual-subscription contract mismatch')
            _require('(NOT,((RULE-SET,Manual-Direct)))' in rule, 'native dual-subscription contract mismatch')
            _require('(NOT,((RULE-SET,oc-cn-domain)))' in rule, 'native dual-subscription contract mismatch')
            _require('(NOT,((GEOIP,CN,no-resolve)))' in rule, 'native dual-subscription contract mismatch')
        if rule.endswith(',' + EXIT):
            _require(rule == 'GEOSITE,tiktok,' + EXIT, 'only TikTok uses ISP')
    _require(not any(('#TikTok-ISP' in str(value) or '#美国' in str(value) for value in cloud['dns'].values())), 'no obsolete DNS group references')
