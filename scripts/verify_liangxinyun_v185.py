"""Official OpenClash merge, rename-only scope, read-only router guard and byte-exact rollback."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT/'profiles/tiktok-router-loongproxy-jp-us-liangxinyun'
CANDIDATE = PROFILE/'versions/v1.8.5'
SOURCE_URL = 'https://raw.githubusercontent.com/vernesong/OpenClash/e553e82e01c697aefbe1555261a503f425e00ccd/luci-app-openclash/root/usr/share/openclash/YAML.rb'
spec = importlib.util.spec_from_file_location('scope_guard_v185', CANDIDATE/'scope_guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    a = parser.parse_args()
    cases = []
    def passed(label):
        cases.append({'case': label, 'passed': True})
    def rejected(label, operation):
        try:
            operation()
        except (ValueError, OSError):
            passed(label)
        else:
            raise AssertionError(label)

    with tempfile.TemporaryDirectory(prefix='lxy-v185-offline-') as temp:
        home = Path(temp)
        source = home/'YAML.rb'
        with urllib.request.urlopen(SOURCE_URL, timeout=45) as response:
            source.write_bytes(response.read(1024*1024))
        assert guard.digest(source.read_bytes()) == guard.SOURCE_SHA
        merge = lambda base, patch: guard.apply_official(base, patch, source, ['ruby'])
        local_raw = (PROFILE/'versions/v1.5.0/local-tiktok-proxy.conf').read_bytes()
        full_raw = (PROFILE/'overwrite/openclash-overwrite.conf').read_bytes()
        baseline = merge(merge({'dns': {}}, guard.parse(local_raw, True)), guard.parse(full_raw, True))
        baseline['proxy-providers']['liangxinyun'].update(
            url='https://synthetic.invalid/FAKE_ONLY', headers={'X-Private': 'FAKE_ONLY'})
        baseline['proxies'][0].update(server='127.0.0.1', port=9, username='FAKE_ONLY', password='FAKE_ONLY')
        after = guard.official_merge(baseline, source, ['ruby'])
        assert guard.protected(baseline) == guard.protected(after)
        assert after['proxy-groups'] == guard.EXPECTED_GROUPS
        assert after['proxies'][0] == {**baseline['proxies'][0], 'dialer-proxy': 'TIKTOK首跳'}
        passed('official-merge-three-explicit-groups-and-reference-only-renames')
        assert after['rule-providers']['Manual-Direct'] == baseline['rule-providers']['Manual-Direct']
        passed('all-current-direct-content-order-and-duplicates-preserved')
        assert guard.official_merge(after, source, ['ruby']) == after
        passed('candidate-incremental-is-idempotent')
        for version in ('1.8.3', '1.8.4'):
            old = guard.parse((PROFILE/f'versions/v{version}/liangxinyun-incremental.conf').read_bytes(), True)
            prior = merge(baseline, old)
            assert guard.official_merge(prior, source, ['ruby']) == after
            passed('official-upgrade-from-'+version+'-removes-both-old-liangxinyun-groups')
        reference = merge(merge({'dns': {}}, guard.parse((CANDIDATE/'local-tiktok-proxy.conf').read_bytes(), True)),
                          guard.parse((CANDIDATE/'openclash-overwrite.conf').read_bytes(), True))
        for key in ('proxy-groups', 'rules', 'dns'):
            assert reference[key] == after[key], key
        assert reference['rule-providers'] == after['rule-providers']
        passed('full-reference-incremental-and-local-template-name-contracts-agree')
        for count in (0, 3, 141, 149):
            varied = copy.deepcopy(baseline)
            varied['rule-providers']['Manual-Direct']['payload'] = ['DOMAIN,duplicate.invalid']*count
            checked = guard.official_merge(varied, source, ['ruby'])
            assert checked['rule-providers']['Manual-Direct'] == varied['rule-providers']['Manual-Direct']
            passed('direct-count-is-not-frozen-'+str(count))
        for label, mutate in (
            ('dns-address', lambda v: v['dns'].update(nameserver=['https://changed.invalid'])),
            ('dns-type', lambda v: v['dns'].update(enable=1)),
            ('rule-order', lambda v: v['rules'].reverse()),
            ('extra-rule', lambda v: v['rules'].append('MATCH,DIRECT')),
            ('direct-order', lambda v: v['rule-providers']['Manual-Direct']['payload'].reverse()),
            ('isp-password', lambda v: v['proxies'][0].update(password='CHANGED_FAKE')),
            ('isp-server', lambda v: v['proxies'][0].update(server='192.0.2.1')),
            ('isp-udp', lambda v: v['proxies'][0].update(udp=True)),
            ('isp-reference', lambda v: v['proxies'][0].update(**{'dialer-proxy':'TikTok首跳'})),
            ('subscription', lambda v: v['proxy-providers']['liangxinyun'].update(url='https://changed.invalid')),
            ('provider-private-header', lambda v: v['proxy-providers']['liangxinyun']['headers'].update({'X-Private':'CHANGED'})),
            ('first-hop-auto', lambda v: v['proxy-groups'][0].update(type='url-test')),
            ('first-hop-filter', lambda v: v['proxy-groups'][0].update(filter='.*')),
            ('probe-disabled', lambda v: v['proxy-groups'][1].update(interval=0)),
            ('probe-status', lambda v: v['proxy-groups'][1].update(**{'expected-status':200})),
            ('lxy-auto-bypass', lambda v: v['proxy-groups'][2].update(type='url-test')),
            ('lxy-direct-route', lambda v: v['proxy-groups'][2]['proxies'].append('DIRECT')),
            ('lxy-hidden', lambda v: v['proxy-groups'][2].update(hidden=True)),
            ('extra-global-timer', lambda v: v['proxy-groups'].append({'name':'GLOBAL','type':'select','proxies':['DIRECT'],'interval':60})),
            ('extra-group', lambda v: v['proxy-groups'].append({'name':'unexpected','type':'select','proxies':['DIRECT']})),
            ('dangling-old-rule-name', lambda v: v['rules'].__setitem__(-2,'MATCH,良心云')),
            ('dangling-old-dns-name', lambda v: v['dns']['nameserver-policy']['geosite:tiktok'].__setitem__(0,'https://1.1.1.1/dns-query#TikTok测速')),
            ('old-dns-tag', lambda v: v['dns']['nameserver-policy']['geosite:tiktok'].__setitem__(0,'https://wrong.invalid#TikTok测速')),
            ('health-status', lambda v: v['proxy-providers']['liangxinyun']['health-check'].update(**{'expected-status':200})),
        ):
            invalid = copy.deepcopy(after)
            mutate(invalid)
            rejected(label+'-refused', lambda: guard.compare(baseline, invalid))
        # Fixed YAML patch does not dynamically rewrite unknown custom routing.
        for label, mutate in (
            ('extra-custom-group', lambda v: v['proxy-groups'].append({'name':'custom','type':'select','proxies':['DIRECT']})),
            ('extra-custom-rule', lambda v: v['rules'].append('MATCH,DIRECT')),
            ('custom-dns-policy', lambda v: v['dns']['nameserver-policy'].update({'custom.invalid':['https://custom.invalid']})),
            ('custom-hop-filter', lambda v: v['proxy-groups'][0].update(filter='custom')),
            ('missing-provider', lambda v: v['proxy-providers'].pop('liangxinyun')),
            ('missing-isp', lambda v: v.update(proxies=[])),
            ('duplicate-group', lambda v: v['proxy-groups'].append(copy.deepcopy(v['proxy-groups'][0]))),
        ):
            invalid = copy.deepcopy(baseline)
            mutate(invalid)
            rejected(label+'-baseline-rejected-before-private-output',
                     lambda: guard.official_merge(invalid, source, ['ruby']))
        for label, raw in (
            ('duplicate-yaml', b'a: 1\na: 2\n'),
            ('yaml-alias', b'a: &shared {secret: FAKE_ONLY}\nb: *shared\n'),
            ('non-string-key', b'1: value\n'),
            ('nan', b'a: .nan\n'),
        ):
            rejected(label+'-refused', lambda: guard.parse(raw))

        before_raw = b'# preserve these exact original bytes\r\n'+yaml.safe_dump(
            baseline, allow_unicode=True, sort_keys=False).replace('\n','\r\n').encode()
        (home/'before.yaml').write_bytes(before_raw)
        (home/'cloud.conf').write_bytes(full_raw)
        filled = {'proxies+':[baseline['proxies'][0]],
                  'proxy-providers':{'liangxinyun':baseline['proxy-providers']['liangxinyun']}}
        filled_raw = ('[YAML]\n'+yaml.safe_dump(filled, allow_unicode=True, sort_keys=False)).encode()
        (home/'local.conf').write_bytes(filled_raw)
        binding = '/etc/openclash/config/synthetic.yaml'
        inventory = {'schemaVersion':1,'selection':'LXY: 日本专线02','configBinding':binding,'modules':[
            {'id':name,'file':str(home/(name+'.conf')),'enabled':True,'order':i,'config':binding,'sourceType':kind}
            for i,(name,kind) in enumerate((('cloud','http'),('local','file')))]}
        inventory_raw = json.dumps(inventory,ensure_ascii=False).encode()
        (home/'inventory.json').write_bytes(inventory_raw)
        bundle = home/'bundle'
        guard.prepare(home/'before.yaml', home/'inventory.json', bundle, source, ['ruby'])
        passed('private-preparation-replays-cached-modules-and-checks-before-writing')
        restored = home/'restored.yaml'
        guard.restore_copy(bundle, bundle/'candidate.yaml', restored)
        assert restored.read_bytes() == before_raw
        assert (home/'before.yaml').read_bytes() == before_raw
        assert (bundle/'module-000.conf').read_bytes() == full_raw
        assert (bundle/'module-001.conf').read_bytes() == filled_raw
        passed('rollback-copy-restores-original-bytes-comments-crlf-and-module-backups')
        rejected('existing-rollback-never-overwritten',
                 lambda: guard.restore_copy(bundle,bundle/'candidate.yaml',restored))
        rejected('existing-private-bundle-never-overwritten',
                 lambda: guard.prepare(home/'before.yaml',home/'inventory.json',bundle,source,['ruby']))
        for name in ('before.yaml','candidate.yaml','module-state.json','module-000.conf'):
            path=bundle/name; original=path.read_bytes(); path.write_bytes(original+b'\n')
            rejected('backup-tamper-'+name,lambda:guard.verify_bundle(bundle))
            path.write_bytes(original)
        cache = guard.parse(full_raw, True)
        cache['rule-providers']['Manual-Direct']['payload'].append('DOMAIN,cache-drift.invalid')
        (home/'cloud.conf').write_text('[YAML]\n'+yaml.safe_dump(cache,allow_unicode=True))
        rejected('cached-direct-drift-refused',
                 lambda: guard.prepare(home/'before.yaml',home/'inventory.json',home/'blocked',source,['ruby']))
        assert not (home/'blocked').exists()
        (home/'cloud.conf').write_bytes(full_raw)
        # Cross-check the independent no-dependency Ruby projection against official Ruby merge.
        (home/'after.yaml').write_text(yaml.safe_dump(after,allow_unicode=True))
        helper = ROOT/'scripts/liangxinyun_v185_runtime_scope.rb'
        for mode, current in ((['--plan'], home/'before.yaml'), ([], home/'after.yaml')):
            result=subprocess.run(['ruby',str(helper),*mode,str(current),str(home/'cloud.conf'),
                str(CANDIDATE/'liangxinyun-incremental.conf')],input=before_raw,capture_output=True,timeout=20)
            assert result.returncode == 0 and not result.stderr, result.stdout
            report=json.loads(result.stdout)
            assert report['passed'] and not report['globalScheduledProbe']
            assert report['apiRequests'] == report['probeRequests'] == 0
            assert not report['configurationWritten']
            passed('ruby-'+('plan' if mode else 'actual-official-merge')+'-agrees-readonly')
        assert set(p.name for p in bundle.iterdir()) == {
            'before.yaml','candidate.yaml','module-state.json','module-000.conf','module-001.conf','manifest.json'}
        assert bundle.stat().st_mode & 0o777 == 0o700
        assert all(p.stat().st_mode & 0o777 == 0o600 for p in bundle.iterdir())
        passed('private-bundle-directory-and-files-permissions')
        report={'passed':True,'candidateVersion':'1.8.5','caseCount':len(cases),'cases':cases,
                'officialSourceSha256':guard.SOURCE_SHA,'sourceUrl':SOURCE_URL,
                'routerContacted':False,'serviceInstalled':False,'privateBaselineUsed':False,
                'formalAcceptance':False,'targetRouterTested':False}
        if a.report:
            a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':
    main()
