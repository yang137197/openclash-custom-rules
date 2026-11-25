"""Independent Ruby scope/plan guard regressions; synthetic input only."""
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
DIR = ROOT/'profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.8.5'
PATCH = load_yaml((DIR/'liangxinyun-incremental.conf').read_text(), module=True)
SCRIPT = ROOT/'scripts/liangxinyun_v185_runtime_scope.rb'
REVERSE = {'TIKTOK首跳':'TikTok首跳','TIKTOK访问检测':'TikTok测速','良心云-按档位自动切换':'良心云'}


def fixture():
    groups = copy.deepcopy(PATCH['proxy-groups!'][:2])
    for g in groups:
        g['name'] = REVERSE[g['name']]
    groups.append({'name':'良心云','type':'select','use':['liangxinyun'],'empty-fallback':'REJECT'})
    policy = {key:[value.rpartition('#')[0]+'#'+REVERSE[value.rpartition('#')[2]] for value in servers]
              for key,servers in PATCH['dns']['nameserver-policy!'].items()}
    rules = [','.join(REVERSE.get(part,part) for part in row.split(',')) for row in PATCH['rules!']]
    before = {
        'proxies':[{'name':'TikTok-ISP-Local','type':'socks5','server':'127.0.0.1','port':9,
                    'username':'FAKE_ONLY','password':'FAKE_ONLY','dialer-proxy':'TikTok首跳','udp':False}],
        'proxy-groups':groups,
        'proxy-providers':{'liangxinyun':{'type':'http','url':'https://synthetic.invalid/FAKE_ONLY',
            'path':'./provider.yaml','override':{'additional-prefix':'LXY: '}}},
        'rule-providers':{'Manual-Direct':{'type':'inline','behavior':'classical','payload':['DOMAIN,before.invalid']},
                          'oc-cn-domain':{'type':'http','proxy':'良心云','url':'https://synthetic.invalid/cn'}},
        'dns':{'enable':True,'nameserver':['127.0.0.1'],'nameserver-policy':policy},'rules':rules}
    current=copy.deepcopy(before)
    current['proxy-groups']=copy.deepcopy(PATCH['proxy-groups!'])
    current['proxies'][0]['dialer-proxy']='TIKTOK首跳'
    current['proxy-providers']['liangxinyun'].update({
        'filter':PATCH['proxy-providers*']['set']['filter'],
        'health-check':copy.deepcopy(PATCH['proxy-providers*']['set']['health-check!'])})
    current['dns']['nameserver-policy']=copy.deepcopy(PATCH['dns']['nameserver-policy!'])
    current['rule-providers']['oc-cn-domain']['proxy']='良心云-按档位自动切换'
    current['rules']=copy.deepcopy(PATCH['rules!'])
    cloud={'rule-providers':{'Manual-Direct':{'type':'inline',
           'payload':['DOMAIN,before.invalid','DOMAIN,new-authorised.invalid']}}}
    current['rule-providers']['Manual-Direct']['payload']=copy.deepcopy(cloud['rule-providers']['Manual-Direct']['payload'])
    return before,current,cloud,copy.deepcopy(PATCH)


@unittest.skipUnless(shutil.which('ruby'),'CI Ruby required')
class RuntimeScopeTests(unittest.TestCase):
    def run_case(self, mutate=None, raw=None, plan=False):
        before,current,cloud,patch=fixture()
        if plan:
            before['rule-providers']['Manual-Direct']['payload']=copy.deepcopy(cloud['rule-providers']['Manual-Direct']['payload'])
            current=copy.deepcopy(before)
        if mutate:
            mutate(before,current,cloud,patch)
        encode=lambda v:yaml.safe_dump(v,allow_unicode=True,sort_keys=False).encode()
        with tempfile.TemporaryDirectory(prefix='scope-v185-') as temp:
            home=Path(temp); paths=[home/n for n in ('current.yaml','cloud.conf','increment.conf')]
            contents=[encode(current),b'[YAML]\n'+encode(cloud),b'[YAML]\n'+encode(patch)]
            for path,data in zip(paths,contents):path.write_bytes(data)
            command=['ruby',str(SCRIPT),*(['--plan'] if plan else []),*map(str,paths)]
            result=subprocess.run(command,input=raw if raw is not None else encode(before),
                                  capture_output=True,timeout=20)
            self.assertEqual(result.stderr,b'')
            self.assertNotIn(b'FAKE_ONLY',result.stdout)
            self.assertEqual([p.read_bytes() for p in paths],contents)
            self.assertEqual(set(p.name for p in home.iterdir()),{p.name for p in paths})
            report=json.loads(result.stdout)
            self.assertEqual(result.returncode,0 if report['passed'] else 1)
            self.assertEqual(report['apiRequests'],0); self.assertEqual(report['probeRequests'],0)
            self.assertFalse(report['selectionApplied']); self.assertFalse(report['configurationWritten'])
            return report

    def test_accepts_exact_rename_and_authorised_source_without_writes(self):
        r=self.run_case()
        self.assertTrue(r['passed'])
        self.assertEqual((r['baselineDirectCount'],r['currentDirectCount']),(1,2))
        self.assertFalse(r['globalScheduledProbe'])
        self.assertFalse(r['activeCoreConfigurationVerified'])

    def test_plan_does_not_apply_or_write(self):
        r=self.run_case(plan=True)
        self.assertTrue(r['passed'])
        self.assertEqual(r['mode'],'candidate-plan-readonly')

    def test_rejects_unexpected_routing_changes(self):
        changes=[
            lambda b,c,s,p:c['dns'].update(enable=1),
            lambda b,c,s,p:c['dns'].update(nameserver=['192.0.2.1']),
            lambda b,c,s,p:c['proxies'][0].update(password='CHANGED'),
            lambda b,c,s,p:c['proxies'][0].update(**{'dialer-proxy':'TikTok首跳'}),
            lambda b,c,s,p:c['rules'].reverse(),
            lambda b,c,s,p:c['rules'].__setitem__(-2,'MATCH,良心云'),
            lambda b,c,s,p:c['dns']['nameserver-policy']['geosite:tiktok'].__setitem__(0,'https://1.1.1.1/dns-query#TikTok测速'),
            lambda b,c,s,p:c['proxy-providers']['liangxinyun'].update(url='https://changed.invalid'),
            lambda b,c,s,p:c['rule-providers']['oc-cn-domain'].update(proxy='良心云'),
        ]
        for change in changes:
            with self.subTest(change=change): self.assertFalse(self.run_case(mutate=change)['passed'])

    def test_rejects_group_timer_and_policy_changes(self):
        for index in range(3):
            for change in (
                lambda g:g.update(type='url-test'),
                lambda g:g.update(interval=0),
                lambda g:g.update(filter='.*'),
                lambda g:g.update(**{'expected-status':200}),
            ):
                def mutate(b,c,s,p):change(c['proxy-groups'][index])
                with self.subTest(index=index,change=change):
                    self.assertFalse(self.run_case(mutate=mutate)['passed'])
        self.assertFalse(self.run_case(mutate=lambda b,c,s,p:c['proxy-groups'].append({
            'name':'GLOBAL','type':'select','proxies':['DIRECT'],'interval':60}))['passed'])

    def test_plan_refuses_unsupported_custom_baseline(self):
        for change in (
            lambda v:v['rules'].append('MATCH,DIRECT'),
            lambda v:v['dns']['nameserver-policy'].update({'custom.invalid':['https://custom.invalid']}),
            lambda v:v['proxy-groups'].append({'name':'custom','type':'select','proxies':['DIRECT']}),
            lambda v:v['proxy-groups'][0].update(filter='.*'),
        ):
            def mutate(b,c,s,p):change(b);change(c)
            with self.subTest(change=change):self.assertFalse(self.run_case(mutate=mutate,plan=True)['passed'])

    def test_keeps_all_direct_counts_order_and_duplicates(self):
        for count in (0,3,141,149):
            def mutate(b,c,s,p):
                data=['DOMAIN,duplicate.invalid']*count
                s['rule-providers']['Manual-Direct']['payload']=data[:]
                c['rule-providers']['Manual-Direct']['payload']=data[:]
            self.assertTrue(self.run_case(mutate=mutate)['passed'])
        self.assertFalse(self.run_case(mutate=lambda b,c,s,p:c['rule-providers']['Manual-Direct']['payload'].reverse())['passed'])

    def test_refuses_tampered_patch_and_invalid_private_yaml(self):
        self.assertFalse(self.run_case(mutate=lambda b,c,s,p:p['proxy-groups!'][0].update(interval=1))['passed'])
        for raw in (b'a: FAKE_ONLY\na: other\n',b'a: &same {secret: FAKE_ONLY}\nb: *same\n',b'a: [FAKE_ONLY'):
            self.assertFalse(self.run_case(raw=raw)['passed'])


if __name__=='__main__':
    unittest.main()
