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
FILTER = "日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速"
INNER_NAME = "良心云-严格控制"
GROUP_FIELDS = tuple(json.loads(r'''["type","proxies","use","include-all","include-all-proxies","include-all-providers","exclude-filter","default-selected","filter","empty-fallback","url","expected-status","interval","timeout","lazy","tolerance","hidden"]'''))
HEALTH = json.loads(r'''{"enable":true,"url":"https://www.gstatic.com/generate_204","expected-status":204,"interval":60,"timeout":5000,"lazy":false}''')
INNER = json.loads(r'''{"name":"良心云-严格控制","type":"select","proxies":["REJECT"],"use":["liangxinyun"],"default-selected":"REJECT","filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","empty-fallback":"REJECT","hidden":true}''')
OUTER = json.loads(r'''{"name":"良心云","type":"url-test","proxies":["良心云-严格控制"],"url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204,"tolerance":0,"empty-fallback":"REJECT","hidden":false}''')
EXPECTED_PATCH = json.loads(r'''{"proxy-groups*":{"where":{"name":"良心云"},"set":{"type":"url-test","url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204,"tolerance":0,"empty-fallback":"REJECT","hidden":false,"proxies!":["良心云-严格控制"],"use-":null,"include-all-":null,"include-all-proxies-":null,"include-all-providers-":null,"exclude-filter-":null,"default-selected-":null,"filter-":null}},"proxy-groups+":[{"name":"良心云-严格控制","type":"select","proxies":["REJECT"],"use":["liangxinyun"],"default-selected":"REJECT","filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","empty-fallback":"REJECT","hidden":true}],"proxy-providers*":{"where":{"key":"liangxinyun"},"set":{"filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","health-check!":{"enable":true,"url":"https://www.gstatic.com/generate_204","expected-status":204,"interval":60,"timeout":5000,"lazy":false}}}}''')


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
    require(names.count('良心云') == 1, 'target-group-required')
    providers = config.get('proxy-providers')
    require(type(providers) is dict and type(providers.get('liangxinyun')) is dict, 'target-provider-required')
    return groups[names.index('良心云')], providers['liangxinyun']


def internal(config, required=False):
    groups = [g for g in config['proxy-groups'] if g['name'] == INNER_NAME]
    require(len(groups) <= 1, 'duplicate-internal-group')
    if not groups:
        require(not required, 'internal-group-required')
        return None
    require(canonical(groups[0]) == canonical(INNER), 'reserved-internal-group-conflict')
    return groups[0]


def outer_contract(group):
    actual = {k: group[k] for k in GROUP_FIELDS if k in group}
    expected = {k: v for k, v in OUTER.items() if k != 'name'}
    require(canonical(actual) == canonical(expected), 'public-wrapper-contract-invalid')


def baseline_contract(config):
    _, provider = targets(config)
    require(provider.get('override', {}).get('additional-prefix') == 'LXY: ', 'provider-prefix-invalid')
    require(provider.get('type') in ('http', 'file') and type(provider.get('path')) is str,
            'provider-definition-incomplete')
    if provider['type'] == 'http':
        require(type(provider.get('url')) is str and bool(provider['url']), 'provider-url-required')
    groups = {g['name']: g for g in config['proxy-groups']}
    require(all(groups.get(n, {}).get('type') == 'select' for n in ('TikTok首跳', 'TikTok测速')),
            'tiktok-manual-groups-required')
    isp = [p for p in config.get('proxies', []) if p.get('name') == 'TikTok-ISP-Local']
    require(len(isp) == 1 and isp[0].get('type') == 'socks5'
            and isp[0].get('dialer-proxy') == 'TikTok首跳' and isp[0].get('udp') is False,
            'tiktok-isp-definition-required')
    direct = config.get('rule-providers', {}).get('Manual-Direct')
    require(type(direct) is dict and direct.get('type') == 'inline'
            and type(direct.get('payload')) is list, 'direct-baseline-required')
    require(type(config.get('rules')) is list and type(config.get('dns')) is dict,
            'complete-baseline-required')
    if internal(config) is not None:
        outer_contract(targets(config)[0])


def protected(config):
    # Detach references before masking; shared aliases must never hide outside changes.
    config = json.loads(canonical(config))
    group, provider = targets(config)
    if internal(config) is not None:
        config['proxy-groups'] = [g for g in config['proxy-groups'] if g['name'] != INNER_NAME]
    for key in GROUP_FIELDS:
        group.pop(key, None)
    for key in ('filter', 'health-check'):
        provider.pop(key, None)
    return canonical(config)


def compare(before, after):
    baseline_contract(before)
    baseline_contract(after)
    require(protected(before) == protected(after), 'change-outside-liangxinyun')
    group, provider = targets(after)
    outer_contract(group)
    internal(after, required=True)
    require(provider.get('filter') == FILTER and canonical(provider.get('health-check')) == canonical(HEALTH),
            'health-contract-invalid')
    return {'scopePreserved': True, 'tiktokPreserved': True, 'allRulesPreserved': True,
            'directOrderPreserved': True, 'dnsPreserved': True}


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
    require(manifest.get('version') == '1.8.3' and manifest.get('status') == 'candidate', 'candidate-manifest-invalid')
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
    manifest = {'schemaVersion': 1, 'candidateVersion': '1.8.3', 'complete': True,
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
    require(manifest.get('schemaVersion') == 1 and manifest.get('candidateVersion') == '1.8.3'
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
