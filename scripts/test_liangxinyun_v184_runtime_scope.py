"""Read-only router helper regression: synthetic data, Ruby YAML only."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml

from strict_yaml import load_yaml

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'profiles/tiktok-router-loongproxy-jp-us-liangxinyun'
PATCH = load_yaml((PROFILE / 'versions/v1.8.4/liangxinyun-incremental.conf').read_text(), module=True)
SCRIPT = ROOT / 'scripts/liangxinyun_v184_runtime_scope.rb'


def fixture():
    before = {
        'proxies': [{'name': 'TikTok-ISP-Local', 'type': 'socks5', 'server': '127.0.0.1',
                     'port': 9, 'username': 'FAKE_ONLY', 'password': 'FAKE_ONLY',
                     'dialer-proxy': 'TikTok首跳', 'udp': False}],
        'proxy-groups': [
            {'name': 'TikTok首跳', 'type': 'select', 'proxies': ['REJECT']},
            {'name': 'TikTok测速', 'type': 'select', 'proxies': ['TikTok-ISP-Local']},
            {'name': '良心云', 'type': 'select', 'use': ['liangxinyun'], 'empty-fallback': 'REJECT'}],
        'proxy-providers': {'liangxinyun': {
            'type': 'http', 'url': 'https://synthetic.invalid/FAKE_ONLY', 'path': './provider.yaml',
            'override': {'additional-prefix': 'LXY: '}}},
        'rule-providers': {'Manual-Direct': {
            'type': 'inline', 'behavior': 'classical', 'payload': ['DOMAIN-SUFFIX,before.invalid']}},
        'rules': ['RULE-SET,Manual-Direct,DIRECT', 'MATCH,良心云'],
        'dns': {'enable': True, 'nameserver': ['127.0.0.1']}
    }
    current = copy.deepcopy(before)
    outer = current['proxy-groups'][2]
    for key, value in PATCH['proxy-groups*']['set'].items():
        if key.endswith('-'):
            outer.pop(key[:-1], None)
        else:
            outer[key.rstrip('!')] = copy.deepcopy(value)
    for group in current['proxy-groups']:
        if group['name'] in ('TikTok首跳', 'TikTok测速'):
            group.update(copy.deepcopy(PATCH['<proxy-groups>*']['set']))
    current['proxy-groups'].extend(copy.deepcopy(PATCH['proxy-groups+']))
    provider_set = PATCH['proxy-providers*']['set']
    current['proxy-providers']['liangxinyun'].update({
        'filter': provider_set['filter'], 'health-check': copy.deepcopy(provider_set['health-check!'])})
    cloud = {'rule-providers': {'Manual-Direct': {
        'type': 'inline', 'payload': ['DOMAIN-SUFFIX,before.invalid', 'DOMAIN-SUFFIX,authorised.invalid']}}}
    current['rule-providers']['Manual-Direct']['payload'] = cloud['rule-providers']['Manual-Direct']['payload'][:]
    return before, current, cloud, copy.deepcopy(PATCH)


@unittest.skipUnless(shutil.which('ruby'), 'Ruby is required in CI only')
class RuntimeScopeTests(unittest.TestCase):
    def run_case(self, *, mutate=None, raw_baseline=None):
        before, current, cloud, patch = fixture()
        if mutate:
            mutate(before, current, cloud, patch)
        encoded = lambda obj: yaml.safe_dump(obj, allow_unicode=True, sort_keys=False).encode()
        before_raw = raw_baseline if raw_baseline is not None else encoded(before)
        with tempfile.TemporaryDirectory(prefix='lxy-runtime-scope-') as directory:
            home = Path(directory)
            contents = [encoded(current), b'[YAML]\n'+encoded(cloud), b'[YAML]\n'+encoded(patch)]
            paths = [home/name for name in ('current.yaml', 'cloud.conf', 'increment.conf')]
            for path, content in zip(paths, contents):
                path.write_bytes(content)
            result = subprocess.run(['ruby', str(SCRIPT), *map(str, paths)], input=before_raw,
                                    capture_output=True, timeout=15)
            self.assertEqual(result.stderr, b'')
            self.assertNotIn(b'FAKE_ONLY', result.stdout)
            self.assertEqual([path.read_bytes() for path in paths], contents)
            self.assertEqual(set(p.name for p in home.iterdir()), {p.name for p in paths})
            report = json.loads(result.stdout)
            for key in ('apiRequests', 'probeRequests'):
                self.assertEqual(report[key], 0)
            for key in ('selectionApplied', 'configurationWritten', 'formalAcceptance'):
                self.assertFalse(report[key])
            self.assertEqual(result.returncode, 0 if report['passed'] else 1)
            return report

    def test_accepts_authorised_source_update_and_exact_scope_without_writes(self):
        report = self.run_case()
        self.assertTrue(report['passed'])
        self.assertEqual((report['baselineDirectCount'], report['expectedDirectCount'],
                          report['currentDirectCount']), (1, 2, 2))
        self.assertTrue(report['outsideAuthorizedScopeUnchanged'])
        self.assertFalse(report['activeCoreConfigurationVerified'])

    def test_detects_outside_changes_and_preserves_types(self):
        for label, mutate in (
            ('dns', lambda b,c,s,p: c['dns'].update(enable=False)),
            ('boolean-to-integer', lambda b,c,s,p: c['dns'].update(enable=1)),
            ('isp', lambda b,c,s,p: c['proxies'][0].update(password='CHANGED_FAKE')),
            ('tiktok', lambda b,c,s,p: c['proxy-groups'][0].update(type='url-test')),
            ('rule', lambda b,c,s,p: c['rules'].append('MATCH,DIRECT')),
            ('provider-url', lambda b,c,s,p: c['proxy-providers']['liangxinyun'].update(url='https://changed.invalid')),
        ):
            with self.subTest(label=label):
                self.assertFalse(self.run_case(mutate=mutate)['passed'])

    def test_detects_wrong_policy_or_internal_group(self):
        for label, mutate in (
            ('missing-probe', lambda b,c,s,p: c['proxy-groups'][0].pop('interval')),
            ('probe-status', lambda b,c,s,p: c['proxy-groups'][1].update(**{'expected-status': 200})),
            ('hide-internal', lambda b,c,s,p: c['proxy-groups'][3].update(hidden=True)),
            ('extra-route', lambda b,c,s,p: c['proxy-groups'][2]['proxies'].append('DIRECT')),
            ('internal-route', lambda b,c,s,p: c['proxy-groups'][3]['proxies'].append('DIRECT')),
            ('duplicate', lambda b,c,s,p: c['proxy-groups'].append(copy.deepcopy(c['proxy-groups'][3]))),
            ('health', lambda b,c,s,p: c['proxy-providers']['liangxinyun']['health-check'].update(**{'expected-status': 200})),
            ('tampered-policy', lambda b,c,s,p: p['proxy-groups*']['set'].update(**{'routing-mark': 7})),
        ):
            with self.subTest(label=label):
                self.assertFalse(self.run_case(mutate=mutate)['passed'])

    def test_rejects_direct_reorder_and_does_not_freeze_rule_count(self):
        self.assertFalse(self.run_case(
            mutate=lambda b,c,s,p: c['rule-providers']['Manual-Direct']['payload'].reverse())['passed'])
        for count in (0, 3, 149):
            def changed(b,c,s,p):
                payload = ['DOMAIN-SUFFIX,duplicate.invalid']*count
                s['rule-providers']['Manual-Direct']['payload'] = payload
                c['rule-providers']['Manual-Direct']['payload'] = payload[:]
            with self.subTest(count=count):
                self.assertTrue(self.run_case(mutate=changed)['passed'])

    def test_rejects_alias_duplicate_keys_and_invalid_yaml_without_echoing_values(self):
        for raw in (
            b'FAKE_ONLY: [unterminated',
            b'a: FAKE_ONLY\na: other\n',
            b'a: &shared {secret: FAKE_ONLY}\nb: *shared\n',
        ):
            with self.subTest(raw=raw):
                self.assertFalse(self.run_case(raw_baseline=raw)['passed'])

    def test_accepts_upgrade_from_exact_v183_internal_shape(self):
        def mutate(b,c,s,p):
            b['proxy-groups'][2] = copy.deepcopy(c['proxy-groups'][2])
            prior = copy.deepcopy(c['proxy-groups'][3])
            for key in PATCH['<proxy-groups>*']['set']:
                prior.pop(key, None)
            prior['hidden'] = True
            b['proxy-groups'].append(prior)
        self.assertTrue(self.run_case(mutate=mutate)['passed'])

    def test_tiktok_routing_fields_remain_protected(self):
        for key, value in (('filter', '.*'), ('proxies', ['DIRECT']),
                           ('include-all', True), ('default-selected', 'DIRECT')):
            def mutate(b,c,s,p):
                c['proxy-groups'][1][key] = value
            with self.subTest(key=key):
                self.assertFalse(self.run_case(mutate=mutate)['passed'])
