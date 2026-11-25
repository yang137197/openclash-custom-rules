"""Local official-merge / scope-guard / byte-exact rollback integration, synthetic data only."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.request

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT/'profiles/tiktok-router-loongproxy-jp-us-liangxinyun'
CANDIDATE = PROFILE/'versions/v1.8.4'
SOURCE_URL = 'https://raw.githubusercontent.com/vernesong/OpenClash/e553e82e01c697aefbe1555261a503f425e00ccd/luci-app-openclash/root/usr/share/openclash/YAML.rb'
spec = importlib.util.spec_from_file_location('scope_guard_v184', CANDIDATE/'scope_guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ruby-command', default='["ruby"]')
    parser.add_argument('--openclash-yaml', type=Path)
    parser.add_argument('--core', type=Path, help='optional existing local Mihomo, syntax check only')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    command = json.loads(args.ruby_command)
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

    with tempfile.TemporaryDirectory(prefix='lxy-v184-offline-') as temp:
        home = Path(temp)
        source = args.openclash_yaml
        if source is None:
            source = home/'YAML.rb'
            with urllib.request.urlopen(SOURCE_URL, timeout=45) as response:
                source.write_bytes(response.read(1024*1024))
        assert guard.digest(guard.read_file(source)) == guard.SOURCE_SHA

        def merge(base, patch):
            result = subprocess.run([*command, str(CANDIDATE/'merge_official.rb'), str(source.resolve())],
                                    input=json.dumps({'baseline': base, 'patch': patch}, ensure_ascii=False),
                                    text=True, capture_output=True, timeout=30)
            assert result.returncode == 0 and not result.stderr
            return json.loads(result.stdout)

        stable = PROFILE/'versions/v1.5.0'
        local_raw = (stable/'local-tiktok-proxy.conf').read_bytes()
        full_raw = (stable/'openclash-overwrite.conf').read_bytes()
        baseline = merge(merge({'dns': {}}, guard.parse(local_raw, True)), guard.parse(full_raw, True))
        assert not any(k.endswith(('!', '+', '-', '*')) for k in baseline['dns'])
        reference = re.findall(r'^ "(DOMAIN[^"\n]+)",$', (ROOT/'scripts/liangxinyun_direct_readonly.lua').read_text(), re.M)
        audit = json.loads((PROFILE/'DIRECT_DIFF_AUDIT.json').read_text())
        direct = [v for v in reference if v not in audit['repositoryOnly']]
        assert len(direct) == 141
        baseline['rule-providers']['Manual-Direct']['payload'] = direct
        baseline['proxy-providers']['liangxinyun']['url'] = 'https://synthetic.invalid/private?token=FAKE_ONLY'
        baseline['proxy-providers']['liangxinyun']['headers'] = {'X-Private': 'FAKE_ONLY'}
        baseline['proxies'][0].update(server='127.0.0.1', port=9, username='FAKE_ONLY', password='FAKE_ONLY')
        after = guard.official_merge(baseline, source, command)
        guard.compare(baseline, after)
        passed('official-merge-only-authorised-probes-and-liangxinyun-full-tree-preserved')
        for item in after['proxy-groups']:
            if item['name'] in ('TikTok首跳', 'TikTok测速'):
                assert item['type'] == 'select'
                assert all(item[k] == v for k,v in guard.PROBES.items())
        passed('both-tiktok-selectors-have-native-probes-with-routing-preserved')
        assert direct == after['rule-providers']['Manual-Direct']['payload']
        passed('141-direct-content-order-preserved-no-seven-additions')
        full_reference = merge(merge({'dns': {}}, guard.parse(local_raw, True)),
                               guard.parse((CANDIDATE/'openclash-overwrite.conf').read_bytes(), True))
        for a, b, fields in zip(guard.targets(after), guard.targets(full_reference),
                                (guard.GROUP_FIELDS, ('filter', 'health-check'))):
            assert guard.canonical({k: a[k] for k in fields if k in a}) == guard.canonical({k: b[k] for k in fields if k in b})
        passed('incremental-and-full-reference-controller-contract-agree')
        assert guard.official_merge(after, source, command) == after
        passed('incremental-idempotent')
        old_patch = guard.parse((PROFILE/'versions/v1.8.3/liangxinyun-incremental.conf').read_bytes(), True)
        previous_runtime = guard.apply_official(baseline, old_patch, source, command)
        upgraded = guard.official_merge(previous_runtime, source, command)
        assert upgraded == after
        passed('official-upgrade-from-v183-removes-exact-old-hidden-group-without-duplicates')
        for label, change in (
            ('public-extra-route', lambda v: guard.targets(v)[0]['proxies'].append('DIRECT')),
            ('public-hidden', lambda v: guard.targets(v)[0].update(hidden=True)),
            ('public-provider-bypass', lambda v: guard.targets(v)[0].update(use=['liangxinyun'])),
            ('internal-hidden', lambda v: guard.internal(v).update(hidden=True)),
            ('internal-extra-route', lambda v: guard.internal(v)['proxies'].append('DIRECT')),
            ('missing-internal', lambda v: v['proxy-groups'].remove(guard.internal(v))),
        ):
            invalid = copy.deepcopy(after)
            change(invalid)
            rejected(label+'-refused', lambda: guard.compare(baseline, invalid))
        collision = copy.deepcopy(baseline)
        collision['proxy-groups'].append(dict(guard.INNER, proxies=['DIRECT']))
        rejected('reserved-internal-name-collision-refused',
                 lambda: guard.official_merge(collision, source, command))
        for key, change in (
            ('dns', lambda v: v['dns'].update(enable=False)),
            ('tiktok-hop', lambda v: next(g for g in v['proxy-groups'] if g['name']=='TikTok首跳').update(type='url-test')),
            ('tiktok-probe', lambda v: next(g for g in v['proxy-groups'] if g['name']=='TikTok首跳').update(interval=0)),
            ('isp', lambda v: v['proxies'][0].update(udp=True)),
            ('direct-reorder', lambda v: v['rule-providers']['Manual-Direct']['payload'].reverse()),
            ('rules', lambda v: v['rules'].append('MATCH,DIRECT')),
            ('subscription', lambda v: v['proxy-providers']['liangxinyun'].update(url='https://wrong.invalid')),
            ('health', lambda v: v['proxy-providers']['liangxinyun']['health-check'].update(**{'expected-status': 200})),
            ('provider-credential', lambda v: v['proxy-providers']['liangxinyun']['headers'].update(**{'X-Private': 'changed'})),
        ):
            invalid = copy.deepcopy(after)
            change(invalid)
            rejected(key+'-change-rejected', lambda: guard.compare(baseline, invalid))
        for label, change in (
            ('missing-group', lambda v: v['proxy-groups'].pop(next(i for i,g in enumerate(v['proxy-groups']) if g['name']=='良心云'))),
            ('duplicate-group', lambda v: v['proxy-groups'].append(copy.deepcopy(guard.targets(v)[0]))),
            ('missing-provider', lambda v: v['proxy-providers'].pop('liangxinyun')),
            ('missing-isp', lambda v: v.update(proxies=[])),
        ):
            invalid = copy.deepcopy(baseline)
            change(invalid)
            rejected(label+'-rejected', lambda: guard.official_merge(invalid, source, command))
        for label, raw in (
            ('duplicate-yaml', b'a: 1\na: 2\n'),
            ('shared-yaml-alias', b'a: &same {x: 1}\nb: *same\n'),
            ('non-string-key', b'1: value\n'),
            ('nan', b'a: .nan\n'),
        ):
            rejected(label+'-rejected', lambda: guard.parse(raw))
        arbitrary = copy.deepcopy(baseline)
        arbitrary['rule-providers']['Manual-Direct']['payload'] = ['DOMAIN,example.invalid']*2+direct[::-1]
        guard.official_merge(arbitrary, source, command)
        passed('arbitrary-direct-count-order-duplicates-preserved')
        before_path = home/'input.yaml'
        before_raw = b'# exact bytes for rollback\r\n'+yaml.safe_dump(baseline, allow_unicode=True, sort_keys=False).replace('\n', '\r\n').encode()
        before_path.write_bytes(before_raw)
        (home/'cloud.conf').write_bytes(full_raw)
        # Inventory contains filled synthetic modules that match the running snapshot.
        filled_local = '[YAML]\n' + yaml.safe_dump({
            'proxies+': [baseline['proxies'][0]],
            'proxy-providers': {'liangxinyun': baseline['proxy-providers']['liangxinyun']}
        }, allow_unicode=True, sort_keys=False)
        local_raw = filled_local.encode()
        (home/'local.conf').write_bytes(local_raw)
        binding = '/etc/openclash/config/synthetic.yaml'
        inventory = {'schemaVersion': 1, 'selection': 'LXY: 日本专线02', 'configBinding': binding,
                     'modules': [{'id': name, 'file': str(home/(name+'.conf')), 'enabled': True,
                                  'order': i, 'config': binding, 'sourceType': kind}
                                 for i,(name,kind) in enumerate((('cloud','http'),('local','file')))]}
        inventory_path = home/'inventory.json'
        inventory_raw = json.dumps(inventory, ensure_ascii=False).encode()
        inventory_path.write_bytes(inventory_raw)
        bundle = home/'bundle'
        # Reproduce the observed 148 cached / 141 running discrepancy before writing a bundle.
        cache_drift = home/'cloud-148.conf'
        cache_patch = guard.parse(full_raw, True)
        cache_patch['rule-providers']['Manual-Direct']['payload'] += [
            f'DOMAIN,cache-fixture-{i}.invalid' for i in range(7)]
        assert len(cache_patch['rule-providers']['Manual-Direct']['payload']) == 148
        cache_drift.write_text('[YAML]\n' + yaml.safe_dump(cache_patch, allow_unicode=True, sort_keys=False))
        drift_inventory = copy.deepcopy(inventory)
        drift_inventory['modules'][0]['file'] = str(cache_drift)
        drift_inventory_path = home/'drift-inventory.json'
        drift_inventory_path.write_text(json.dumps(drift_inventory))
        rejected('cached-cloud-runtime-direct-disagreement-refused',
                 lambda: guard.prepare(before_path, drift_inventory_path, home/'blocked-cache-bundle', source, command))
        assert not (home/'blocked-cache-bundle').exists()
        guard.prepare(before_path, inventory_path, bundle, source, command)
        guard.verify_bundle(bundle)
        for label, argv in (
            ('compare-cli', ['compare', '--baseline', str(before_path), '--candidate', str(bundle/'candidate.yaml')]),
            ('verify-bundle-cli', ['verify-bundle', '--bundle', str(bundle)]),
            ('restore-copy-cli', ['restore-copy', '--bundle', str(bundle), '--current', str(bundle/'candidate.yaml'),
                                  '--output', str(home/'cli-restored.yaml')]),
        ):
            result = subprocess.run([sys.executable, str(CANDIDATE/'scope_guard.py'), *argv],
                                    capture_output=True, text=True, timeout=20)
            assert result.returncode == 0 and not result.stderr
            assert json.loads(result.stdout)['mode'] == argv[0]
            passed(label)
        assert (home/'cli-restored.yaml').read_bytes() == before_raw
        bad_input = home/'invalid.yaml'
        bad_input.write_text('private_password: FAKE_ONLY\nprivate_password: other\n')
        result = subprocess.run([sys.executable, str(CANDIDATE/'scope_guard.py'), 'compare',
                                 '--baseline', str(bad_input), '--candidate', str(bundle/'candidate.yaml')],
                                capture_output=True, text=True, timeout=20)
        assert result.returncode == 1 and not result.stderr and 'FAKE_ONLY' not in result.stdout
        assert json.loads(result.stdout) == {'passed': False, 'error': 'offline-candidate-guard-failed'}
        passed('invalid-private-cli-input-fails-without-details')
        assert before_path.read_bytes() == before_raw and inventory_path.read_bytes() == inventory_raw
        assert (bundle/'module-state.json').read_bytes() == inventory_raw
        assert (bundle/'module-000.conf').read_bytes() == full_raw
        assert (bundle/'module-001.conf').read_bytes() == local_raw
        passed('private-bundle-preserves-module-bytes-metadata-and-original-inputs')
        if __import__('os').name != 'nt':
            assert bundle.stat().st_mode & 0o777 == 0o700
            assert all(p.stat().st_mode & 0o777 == 0o600 for p in bundle.iterdir())
            passed('private-directory-and-file-permissions')
        current = bundle/'candidate.yaml'
        restored = home/'restored.yaml'
        guard.restore_copy(bundle, current, restored)
        assert restored.read_bytes() == before_raw
        passed('rollback-copy-byte-exact-including-comments-and-crlf')
        rejected('rollback-existing-output-never-overwritten', lambda: guard.restore_copy(bundle, current, restored))
        rejected('rollback-output-inside-backup-refused', lambda: guard.restore_copy(bundle, current, bundle/'new-file'))
        rejected('prepare-existing-directory-refused', lambda: guard.prepare(before_path, inventory_path, bundle, source, command))
        drifted = home/'drifted.yaml'
        drifted.write_text(yaml.safe_dump({**after, 'ipv6': True}, allow_unicode=True))
        rejected('rollback-current-drift-refused', lambda: guard.restore_copy(bundle, drifted, home/'no-copy'))
        assert not (home/'no-copy').exists()
        rejected('private-output-in-repository-refused', lambda: guard.prepare(before_path, inventory_path, CANDIDATE/'private-output', source, command))
        # Whole-bundle integrity, not just candidate config.
        for name in ('before.yaml', 'candidate.yaml', 'module-state.json', 'module-000.conf'):
            path = bundle/name
            original = path.read_bytes()
            path.write_bytes(original+b'\n# modified')
            rejected(name+'-tamper-refused', lambda: guard.verify_bundle(bundle))
            path.write_bytes(original)
        missing = bundle/'manifest.json'
        original = missing.read_bytes()
        missing.unlink()
        rejected('incomplete-bundle-refused', lambda: guard.verify_bundle(bundle))
        missing.write_bytes(original)
        bad_source = home/'bad-YAML.rb'
        bad_source.write_bytes(guard.read_file(source)+b'\n# modified')
        rejected('modified-official-source-refused', lambda: guard.official_merge(baseline, bad_source, command))
        # The serialized comparison must not treat integer 1 as boolean true.
        changed_type = copy.deepcopy(after)
        changed_type['dns']['enable'] = 1
        rejected('boolean-integer-outside-scope-change-refused', lambda: guard.compare(baseline, changed_type))
        if args.core:
            # File-only provider avoids external subscription access even during core -t.
            config = copy.deepcopy(after)
            config['proxy-providers']['liangxinyun'] = {
                **config['proxy-providers']['liangxinyun'], 'type': 'file', 'path': str(home/'provider.yaml')}
            config['proxy-providers']['liangxinyun'].pop('url', None)
            (home/'provider.yaml').write_text(yaml.safe_dump({'proxies': [
                {'name': '日本专线01', 'type': 'http', 'server': '127.0.0.1', 'port': 9}]}))
            # Syntax fixture uses only synthetic loopback endpoints and no GEO assets.
            config['rules'] = ['MATCH,良心云']
            config.pop('rule-providers', None)
            config['dns'] = {'enable': False}
            config['proxies'].append({'name':'🇯🇵 日本Z04 | IEPL','type':'http','server':'127.0.0.1','port':9})
            syntax = home/'syntax.yaml'
            syntax.write_text(yaml.safe_dump(config, allow_unicode=True))
            result = subprocess.run([str(args.core.resolve()), '-d', str(home), '-f', str(syntax), '-t'],
                                    capture_output=True, text=True, timeout=30)
            assert result.returncode == 0, result.stdout+result.stderr
            passed('real-core-synthetic-scoped-selector-syntax')
        report = {'passed': True, 'candidateVersion': '1.8.4', 'caseCount': len(cases), 'cases': cases,
                  'officialSourceSha256': guard.SOURCE_SHA, 'sourceUrl': SOURCE_URL,
                  'routerContacted': False, 'serviceInstalled': False, 'privateBaselineUsed': False,
                  'formalAcceptance': False, 'targetRouterTested': False}
        if args.report:
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
