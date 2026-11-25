"""Offline PC tool. Never contacts a router, installs a service or overwrites inputs.

Python/PyYAML and Ruby are local validation dependencies, NOT router requirements.
Backups contain secrets: keep the output outside Git and do not share it.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import yaml

HERE = Path(__file__).resolve().parent
SOURCE_SHA = '1249abf411e1df9e8fe542fb3584f34a27e6e3a587942e5d9f759a32b1bd8261'
GROUP = "良心云-按档位自动切换"
OLD_GROUP = "良心云"
OLD_INNER = "良心云-严格控制"
NAMES = {"TikTok首跳": "TIKTOK首跳", "TikTok测速": "TIKTOK访问检测", OLD_GROUP: GROUP}
FILTER = "日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速"
PROBES = json.loads(r'''{"url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204}''')
HEALTH = json.loads(r'''{"enable":true,"url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204}''')
EXPECTED_PATCH = json.loads(r'''{"proxy-groups!":[{"name":"TIKTOK首跳","type":"select","url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204,"proxies":["REJECT"],"default-selected":"REJECT","include-all":true,"filter":"^(REJECT|(?:🇯🇵 )?日本Z0[1-4] \\| IEPL[ \\t]*)$","empty-fallback":"REJECT"},{"name":"TIKTOK访问检测","type":"select","url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204,"include-all-proxies":true,"filter":"^TikTok-ISP-Local$","empty-fallback":"REJECT"},{"name":"良心云-按档位自动切换","type":"select","proxies":["REJECT"],"use":["liangxinyun"],"default-selected":"REJECT","filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","empty-fallback":"REJECT","hidden":false,"url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204}],"proxies*":{"where":{"name":"TikTok-ISP-Local"},"set":{"dialer-proxy":"TIKTOK首跳"}},"proxy-providers*":{"where":{"key":"liangxinyun"},"set":{"filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","health-check!":{"enable":true,"url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204}}},"dns":{"nameserver-policy!":{"geosite:tiktok":["https://1.1.1.1/dns-query#TIKTOK访问检测","https://8.8.8.8/dns-query#TIKTOK访问检测"],"+.xn--ngstr-lra8j.com":["https://1.1.1.1/dns-query#良心云-按档位自动切换","https://8.8.8.8/dns-query#良心云-按档位自动切换"],"geosite:google":["https://1.1.1.1/dns-query#良心云-按档位自动切换","https://8.8.8.8/dns-query#良心云-按档位自动切换"]}},"rule-providers*":{"where":{"proxy":"良心云"},"set":{"proxy":"良心云-按档位自动切换"}},"rules!":["GEOSITE,private,DIRECT","GEOIP,private,DIRECT,no-resolve","IP-CIDR,10.0.0.0/8,DIRECT,no-resolve","IP-CIDR,172.16.0.0/12,DIRECT,no-resolve","IP-CIDR,192.168.0.0/16,DIRECT,no-resolve","IP-CIDR,127.0.0.0/8,DIRECT,no-resolve","IP-CIDR,169.254.0.0/16,DIRECT,no-resolve","IP-CIDR,224.0.0.0/4,DIRECT,no-resolve","IP-CIDR6,::1/128,DIRECT,no-resolve","IP-CIDR6,fc00::/7,DIRECT,no-resolve","IP-CIDR6,fe80::/10,DIRECT,no-resolve","IP-CIDR6,ff00::/8,DIRECT,no-resolve","DOMAIN-SUFFIX,github.com,良心云-按档位自动切换","DOMAIN-SUFFIX,githubusercontent.com,良心云-按档位自动切换","DOMAIN-SUFFIX,githubassets.com,良心云-按档位自动切换","GEOSITE,tiktok,TIKTOK访问检测","GEOSITE,tiktok,REJECT","DOMAIN-SUFFIX,xn--ngstr-lra8j.com,良心云-按档位自动切换","GEOSITE,google,良心云-按档位自动切换","RULE-SET,Manual-Direct,DIRECT","RULE-SET,oc-cn-domain,DIRECT","GEOIP,CN,DIRECT,no-resolve","MATCH,良心云-按档位自动切换","MATCH,REJECT"]}''')
EXPECTED_GROUPS = EXPECTED_PATCH["proxy-groups!"]
PREVIOUS_INNER = json.loads(r'''{"name":"良心云-严格控制","type":"select","proxies":["REJECT"],"use":["liangxinyun"],"default-selected":"REJECT","filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","empty-fallback":"REJECT","hidden":false,"url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204}''')
LEGACY_INNER = json.loads(r'''{"name":"良心云-严格控制","type":"select","proxies":["REJECT"],"use":["liangxinyun"],"default-selected":"REJECT","filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","empty-fallback":"REJECT","hidden":true}''')

def require(value, code):
    if not value:
        raise ValueError(code)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    # String-only mapping keys avoid JSON coercion collisions. Distinguish true from 1.
    def visit(v):
        if isinstance(v, dict):
            require(all(type(k) is str for k in v), 'non-string-key')
            for x in v.values():
                visit(x)
        elif isinstance(v, list):
            for x in v:
                visit(x)
        else:
            require(type(v) in (str, int, float, bool, type(None)), 'unsupported-value')
    visit(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False,
                      separators=(',', ':')).encode()


class UniqueLoader(yaml.SafeLoader):
    pass


def mapping(loader, node):
    result = {}
    for key, value in node.value:
        key = loader.construct_object(key)
        require(type(key) is str and key not in result, 'duplicate-or-invalid-yaml-key')
        result[key] = loader.construct_object(value)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def parse(data, module=False):
    text = data.decode('utf-8-sig')
    if module:
        lines = text.splitlines()
        sections = [i for i, line in enumerate(lines) if re.fullmatch(r'\[[^\]]+\]', line.strip())]
        require(len(sections) == 1 and lines[sections[0]].strip() == '[YAML]', 'invalid-module-section')
        require(all(not line.strip() or line.lstrip().startswith('#') for line in lines[:sections[0]]),
                'module-content-before-section')
        text = '\n'.join(lines[sections[0]+1:])
    require(not any(isinstance(t, (yaml.tokens.AnchorToken, yaml.tokens.AliasToken))
                    for t in yaml.scan(text)), 'yaml-alias-not-supported')
    value = yaml.load(text, Loader=UniqueLoader)
    require(type(value) is dict, 'mapping-required')
    canonical(value)
    return value


def read_file(path):
    path = Path(path).absolute()
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'symlink-not-allowed')
    require(path.is_file(), 'regular-file-required')
    data = path.read_bytes()
    require(len(data) <= 8*1024*1024, 'file-too-large')
    return data


def targets(config):
    groups = config.get('proxy-groups')
    require(type(groups) is list and all(type(g) is dict for g in groups), 'groups-invalid')
    names = [g.get('name') for g in groups]
    require(all(type(n) is str for n in names) and len(names) == len(set(names)), 'group-names-invalid')
    target = GROUP if GROUP in names else OLD_GROUP
    require(names.count(target) == 1, 'target-group-required')
    providers = config.get('proxy-providers')
    require(type(providers) is dict and type(providers.get('liangxinyun')) is dict, 'target-provider-required')
    return groups[names.index(target)], providers['liangxinyun']


def baseline_contract(config):
    target, provider = targets(config)
    names = [g['name'] for g in config['proxy-groups']]
    old_names = ['TikTok首跳', 'TikTok测速', OLD_GROUP]
    new_names = [g['name'] for g in EXPECTED_GROUPS]
    require(names in (old_names, old_names + [OLD_INNER], new_names), 'unsupported-group-layout')
    require(target.get('type') in ('select', 'url-test'), 'target-type-invalid')
    if OLD_INNER in names:
        inner = config['proxy-groups'][-1]
        require(canonical(inner) in (canonical(PREVIOUS_INNER), canonical(LEGACY_INNER)),
                'reserved-internal-group-conflict')
        require(target.get('type') == 'url-test' and target.get('proxies') == [OLD_INNER]
                and not target.get('use'), 'old-wrapper-contract-invalid')
    else:
        require(target.get('type') == 'select' and target.get('use') == ['liangxinyun'],
                'selector-provider-required')
    require(provider.get('override', {}).get('additional-prefix') == 'LXY: ', 'provider-prefix-invalid')
    require(provider.get('type') in ('http', 'file') and type(provider.get('path')) is str,
            'provider-definition-incomplete')
    if provider['type'] == 'http':
        require(type(provider.get('url')) is str and bool(provider['url']), 'provider-url-required')
    require(all(g.get('type') == 'select' for g in config['proxy-groups'][:2]),
            'tiktok-manual-groups-required')
    isp = [p for p in config.get('proxies', []) if p.get('name') == 'TikTok-ISP-Local']
    require(len(isp) == 1 and isp[0].get('type') == 'socks5'
            and isp[0].get('dialer-proxy') == names[0] and isp[0].get('udp') is False,
            'tiktok-isp-definition-required')
    direct = config.get('rule-providers', {}).get('Manual-Direct')
    require(type(direct) is dict and direct.get('type') == 'inline'
            and type(direct.get('payload')) is list
            and all(type(v) is str for v in direct['payload']), 'direct-baseline-required')
    require(type(config.get('rules')) is list and type(config.get('dns')) is dict,
            'complete-baseline-required')


def rename_rule(rule):
    require(type(rule) is str, 'rule-string-required')
    parts = rule.split(',')
    pos = -2 if parts[-1] == 'no-resolve' else -1
    parts[pos] = NAMES.get(parts[pos], parts[pos])
    return ','.join(parts)


def protected(config):
    # Normalise ONLY authorised group references, never arbitrary secrets/strings.
    value = json.loads(canonical(config))
    target, provider = targets(value)
    groups = []
    for item in value['proxy-groups']:
        if item['name'] == OLD_INNER:
            continue
        if item is target:
            groups.append({'name': GROUP})
            continue
        item['name'] = NAMES.get(item['name'], item['name'])
        for key in PROBES:
            item.pop(key, None)
        groups.append(item)
    value['proxy-groups'] = groups
    for node in value.get('proxies', []):
        if node.get('name') == 'TikTok-ISP-Local':
            node['dialer-proxy'] = NAMES.get(node.get('dialer-proxy'), node.get('dialer-proxy'))
    for key in ('filter', 'health-check'):
        provider.pop(key, None)
    for item in value.get('rule-providers', {}).values():
        if type(item) is dict and type(item.get('proxy')) is str:
            item['proxy'] = NAMES.get(item['proxy'], item['proxy'])
    policy = value['dns'].get('nameserver-policy', {})
    require(type(policy) is dict, 'dns-policy-invalid')
    for key, servers in policy.items():
        was_list = type(servers) is list
        updated = []
        for server in servers if was_list else [servers]:
            require(type(server) is str, 'dns-server-invalid')
            base, sep, tag = server.rpartition('#')
            updated.append(base + sep + NAMES.get(tag, tag) if sep else server)
        policy[key] = updated if was_list else updated[0]
    value['rules'] = [rename_rule(rule) for rule in value['rules']]
    return canonical(value)


def compare(before, after):
    baseline_contract(before)
    baseline_contract(after)
    require(canonical(after['proxy-groups']) == canonical(EXPECTED_GROUPS), 'candidate-groups-invalid')
    require(canonical(after['rules']) == canonical(EXPECTED_PATCH['rules!']), 'candidate-rule-references-invalid')
    require(canonical(after['dns'].get('nameserver-policy')) ==
            canonical(EXPECTED_PATCH['dns']['nameserver-policy!']), 'candidate-dns-references-invalid')
    require(all(p.get('proxy') not in NAMES for p in after['rule-providers'].values()
                if type(p) is dict), 'candidate-provider-reference-invalid')
    require(all(p.get('dialer-proxy') not in NAMES for p in after.get('proxies', [])),
            'candidate-dialer-reference-invalid')
    require(protected(before) == protected(after), 'change-outside-authorized-scope')
    _, provider = targets(after)
    require(provider.get('filter') == FILTER and canonical(provider.get('health-check')) == canonical(HEALTH),
            'health-contract-invalid')
    # GLOBAL is deliberately NOT defined: the core creates its default manual group,
    # with a disabled (interval zero) compatible-provider health check.
    return {'scopePreserved': True, 'tiktokRoutingPreserved': True,
            'automaticProbesConfigured': True, 'globalScheduledProbe': False,
            'threeExplicitGroups': True, 'allRulesPreservedApartFromNames': True,
            'directOrderPreserved': True, 'dnsPreservedApartFromNames': True}


def apply_official(before, patch, source, command):
    require(digest(read_file(source)) == SOURCE_SHA, 'official-source-hash-mismatch')
    require(type(command) is list and command and all(type(v) is str for v in command), 'ruby-argv-invalid')
    result = subprocess.run([*command, str(HERE/'merge_official.rb'), str(Path(source).resolve())],
                            input=json.dumps({'baseline': before, 'patch': patch}, ensure_ascii=False),
                            text=True, encoding='utf-8', capture_output=True, timeout=45)
    require(result.returncode == 0 and not result.stderr, 'official-merge-failed')
    return json.loads(result.stdout)


def official_merge(before, source, command):
    baseline_contract(before)
    verify_candidate()
    patch = parse(read_file(HERE/'liangxinyun-incremental.conf'), module=True)
    require(canonical(patch) == canonical(EXPECTED_PATCH), 'incremental-contract-invalid')
    after = apply_official(before, patch, source, command)
    compare(before, after)
    return after


def verify_module_stack(before, inventory, saved, source, command):
    # Replay enabled cached YAML modules, in the plugin's descending-order execution.
    # This detects a 148-rule cache against a 141-rule runtime before adding a candidate.
    replay = json.loads(canonical(before))
    ordered = sorted(enumerate(inventory['modules']), key=lambda pair: pair[1]['order'], reverse=True)
    for index, item in ordered:
        if item['enabled']:
            replay = apply_official(replay, parse(saved[f'module-{index:03}.conf'], module=True), source, command)
    require(protected(before) == protected(replay), 'cached-modules-change-protected-config')
    return True


def private_write(path, data):
    # Never replace an existing destination. On Windows use a private user directory/ACL.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def outside_git(path):
    require(not any((p/'.git').exists() for p in (path, *path.parents)), 'private-output-inside-git')


def verify_candidate():
    manifest = json.loads(read_file(HERE/'BUNDLE.json'))
    require(manifest.get('version') == '1.8.5' and manifest.get('status') == 'candidate', 'candidate-manifest-invalid')
    expected = {'openclash-overwrite.conf', 'local-tiktok-proxy.conf', 'liangxinyun-incremental.conf',
                'liangxinyun-controller.lua', 'liangxinyun-controller.run', 'liangxinyun-controller.init',
                'scope_guard.py', 'merge_official.rb'}
    require(type(manifest.get('files')) is dict and set(manifest['files']) == expected, 'candidate-files-invalid')
    for name, checksum in manifest['files'].items():
        require(digest(read_file(HERE/name)) == checksum, 'candidate-integrity-failed')


def prepare(baseline, module_state, output, source, command):
    raw, inventory_raw = read_file(baseline), read_file(module_state)
    before = parse(raw)
    baseline_contract(before)
    inventory = json.loads(inventory_raw)
    require(type(inventory) is dict and inventory.get('schemaVersion') == 1, 'inventory-invalid')
    require(type(inventory.get('selection')) is str and inventory['selection'].startswith('LXY: '), 'selection-required')
    binding = inventory.get('configBinding')
    require(type(binding) is str and binding.startswith('/etc/openclash/config/'), 'binding-required')
    modules = inventory.get('modules')
    require(type(modules) is list and bool(modules), 'module-backups-required')
    saved, ids, orders = {}, set(), set()
    for i, item in enumerate(modules):
        require(type(item) is dict and type(item.get('id')) is str and item['id'] not in ids,
                'module-id-invalid')
        require(type(item.get('enabled')) is bool and type(item.get('order')) is int
                and item['order'] not in orders and item.get('config') in (binding, 'all'), 'module-metadata-invalid')
        require(item.get('sourceType') in ('http', 'file'), 'module-source-invalid')
        ids.add(item['id']); orders.add(item['order'])
        saved[f'module-{i:03}.conf'] = read_file(item['file'])
    verify_module_stack(before, inventory, saved, source, command)
    after = official_merge(before, source, command)
    # Detect input changes during preparation; this is not an atomic router snapshot.
    require(read_file(baseline) == raw and read_file(module_state) == inventory_raw
            and all(read_file(item['file']) == saved[f'module-{i:03}.conf'] for i, item in enumerate(modules)),
            'input-changed-during-preparation')
    output = Path(output).absolute()
    outside_git(output)
    require(output.parent.is_dir() and not any(p.is_symlink() for p in (output, *output.parents)), 'output-parent-invalid')
    output.mkdir(mode=0o700)  # Existing directories, including incomplete bundles, are never reused.
    payload = {'before.yaml': raw, 'candidate.yaml': yaml.safe_dump(after, allow_unicode=True, sort_keys=False).encode(),
               'module-state.json': inventory_raw, **saved}
    manifest = {'schemaVersion': 1, 'candidateVersion': '1.8.5', 'complete': True,
                'files': {name: digest(data) for name, data in payload.items()},
                'incrementalSha256': digest(read_file(HERE/'liangxinyun-incremental.conf')),
                'officialSourceSha256': SOURCE_SHA}
    # Manifest is published last. A failed write cannot become a valid bundle.
    for name, data in payload.items():
        private_write(output/name, data)
    private_write(output/'manifest.json', canonical(manifest)+b'\n')
    verify_bundle(output)
    return {'prepared': True, **compare(before, after), 'routerContacted': False,
            'serviceInstalled': False, 'formalAcceptance': False}


def verify_bundle(bundle):
    verify_candidate()
    bundle = Path(bundle)
    manifest = json.loads(read_file(bundle/'manifest.json'))
    require(manifest.get('schemaVersion') == 1 and manifest.get('candidateVersion') == '1.8.5'
            and manifest.get('complete') is True, 'bundle-incomplete')
    files = manifest.get('files')
    require(type(files) is dict and {'before.yaml', 'candidate.yaml', 'module-state.json'} <= files.keys(),
            'bundle-files-invalid')
    require(manifest.get('officialSourceSha256') == SOURCE_SHA
            and manifest.get('incrementalSha256') == digest(read_file(HERE/'liangxinyun-incremental.conf')),
            'bundle-version-mismatch')
    require(set(p.name for p in bundle.iterdir()) == {*files, 'manifest.json'}, 'bundle-unexpected-files')
    for name, checksum in files.items():
        require(name in ('before.yaml', 'candidate.yaml', 'module-state.json')
                or re.fullmatch(r'module-[0-9]{3}\.conf', name), 'bundle-path-invalid')
        require(digest(read_file(bundle/name)) == checksum, 'bundle-integrity-failed')
    inventory = json.loads(read_file(bundle/'module-state.json'))
    require(set(files) == {'before.yaml', 'candidate.yaml', 'module-state.json',
                           *(f'module-{i:03}.conf' for i in range(len(inventory['modules'])))}, 'module-backup-missing')
    compare(parse(read_file(bundle/'before.yaml')), parse(read_file(bundle/'candidate.yaml')))
    return manifest


def restore_copy(bundle, current, output):
    verify_bundle(bundle)
    bundle, output = Path(bundle), Path(output).absolute()
    require(not output.is_relative_to(bundle.absolute()), 'output-inside-backup-bundle')
    require(canonical(parse(read_file(current))) == canonical(parse(read_file(bundle/'candidate.yaml'))),
            'current-config-drifted')
    outside_git(output)
    require(not any(p.is_symlink() for p in (output, *output.parents)), 'output-parent-invalid')
    private_write(output, read_file(bundle/'before.yaml'))
    return {'rollbackCopyPrepared': True, 'originalBytesRestored': True,
            'routerContacted': False, 'serviceInstalled': False, 'formalAcceptance': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    p = sub.add_parser('prepare')
    for flag in ('baseline', 'module-state', 'output', 'openclash-yaml'):
        p.add_argument('--'+flag, type=Path, required=True)
    p.add_argument('--ruby-command', default='["ruby"]')
    p = sub.add_parser('compare')
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p = sub.add_parser('verify-bundle')
    p.add_argument('--bundle', type=Path, required=True)
    p = sub.add_parser('restore-copy')
    for flag in ('bundle', 'current', 'output'):
        p.add_argument('--'+flag, type=Path, required=True)
    a = parser.parse_args()
    if a.mode == 'prepare':
        report = prepare(a.baseline, a.module_state, a.output, a.openclash_yaml, json.loads(a.ruby_command))
    elif a.mode == 'compare':
        report = compare(parse(read_file(a.baseline)), parse(read_file(a.candidate)))
    elif a.mode == 'restore-copy':
        report = restore_copy(a.bundle, a.current, a.output)
    else:
        verify_bundle(a.bundle)
        report = {'bundleVerified': True}
    print(json.dumps({'mode': a.mode, **report}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        # Inputs may contain credentials. Do not echo parser errors, values, paths or stderr.
        print('{"passed":false,"error":"offline-candidate-guard-failed"}')
        raise SystemExit(1) from None
