# Local validation only. Load the official helper; never start OpenClash or a core.
require 'yaml'
require 'json'
require 'digest'

class MergeCheckFailure < StandardError; end
def check(value, code)
  raise MergeCheckFailure, code unless value
end
def clone_value(value)
  Marshal.load(Marshal.dump(value))
end

GROUP_FIELDS = %w[type proxies use include-all include-all-proxies include-all-providers exclude-filter default-selected filter empty-fallback].freeze
GROUP_SET_FIELDS = %w[type proxies! use! include-all- include-all-proxies- include-all-providers- exclude-filter- default-selected filter empty-fallback].freeze
PROVIDER_FIELDS = %w[filter health-check].freeze

def validate_targets(base)
  groups = base['proxy-groups']
  check(groups.is_a?(Array), 'groups-invalid')
  positions = groups.each_index.select { |i| groups[i].is_a?(Hash) && groups[i]['name'] == '良心云' }
  check(positions.size == 1, 'target-group-missing-or-duplicate')
  check(base['proxy-providers'].is_a?(Hash) && base['proxy-providers']['liangxinyun'].is_a?(Hash), 'target-provider-missing-or-invalid')
  positions.first
end

def validate_patch(patch)
  check(patch.is_a?(Hash) && patch.keys.sort == ['proxy-groups*', 'proxy-providers*'], 'patch-root-outside-scope')
  group, provider = patch.values_at('proxy-groups*', 'proxy-providers*')
  check(group.is_a?(Hash) && provider.is_a?(Hash), 'patch-shape-invalid')
  check(group.keys.sort == %w[set where] && provider.keys.sort == %w[set where], 'patch-shape-invalid')
  check(group['where'] == {'name'=>'良心云'} && provider['where'] == {'key'=>'liangxinyun'}, 'patch-target-outside-scope')
  check(group['set'].is_a?(Hash) && group['set'].keys.sort == GROUP_SET_FIELDS.sort, 'patch-group-fields-invalid')
  check(provider['set'].is_a?(Hash) && provider['set'].keys.sort == ['filter', 'health-check!'], 'patch-provider-fields-invalid')
end

def protected_view(base)
  # Break shared references before masking allowed paths, so aliases cannot hide an outside change.
  out = JSON.parse(JSON.generate(base))
  index = validate_targets(out)
  GROUP_FIELDS.each { |key| out['proxy-groups'][index].delete(key) }
  PROVIDER_FIELDS.each { |key| out['proxy-providers']['liangxinyun'].delete(key) }
  out
end

def scope_preserved(before, after)
  protected_view(before) == protected_view(after)
end

def merge_checked(base, patch)
  index = validate_targets(base)
  validate_patch(patch)
  backup = Marshal.dump(base)
  # The official implementation may mutate nested input objects. Keep an independent baseline.
  merged = YAML.overwrite(clone_value(base), clone_value(patch))
  check(scope_preserved(base, merged), 'merged-outside-authorized-scope')
  check(Marshal.load(backup) == base, 'baseline-mutated')
  group = merged['proxy-groups'][index]
  provider = merged['proxy-providers']['liangxinyun']
  check(group['type'] == 'select' && group['proxies'] == ['REJECT'] && group['use'] == ['liangxinyun'], 'merged-selector-invalid')
  check(group['default-selected'] == 'REJECT' && group['empty-fallback'] == 'REJECT', 'merged-reject-invalid')
  %w[include-all include-all-proxies include-all-providers exclude-filter].each { |k| check(!group.key?(k), 'legacy-group-field-retained') }
  expected = {'enable'=>true, 'url'=>'https://www.gstatic.com/generate_204', 'expected-status'=>204,
              'interval'=>60, 'timeout'=>5000, 'lazy'=>false}
  check(provider['health-check'] == expected, 'merged-health-contract-invalid')
  check(group['filter'] == patch['proxy-groups*']['set']['filter'] && provider['filter'] == group['filter'], 'merged-filter-invalid')
  check(base['rules'] == merged['rules'], 'rules-changed')
  check(base['rule-providers'] == merged['rule-providers'], 'rule-providers-changed')
  changed = GROUP_FIELDS.select { |k| base['proxy-groups'][index].key?(k) != group.key?(k) || base['proxy-groups'][index][k] != group[k] }
                        .map { |k| '/proxy-groups/良心云/' + k }
  changed += PROVIDER_FIELDS.select { |k| base['proxy-providers']['liangxinyun'][k] != provider[k] }
                            .map { |k| '/proxy-providers/liangxinyun/' + k }
  [merged, changed]
end

def expect_rejected(code)
  rejected = false
  begin
    yield
  rescue MergeCheckFailure
    rejected = true
  end
  check(rejected, code)
end

begin
  source_path, plan_path, root_path = ARGV
  check(ARGV.size == 3, 'arguments-invalid')
  source_hash = Digest::SHA256.file(source_path).hexdigest
  check(source_hash == '1249abf411e1df9e8fe542fb3584f34a27e6e3a587942e5d9f759a32b1bd8261', 'official-source-hash-mismatch')
  require File.expand_path(source_path)
  blocks = File.read(plan_path, encoding:'UTF-8').scan(/```ini\n(\[YAML\]\n.*?)\n```/m)
  check(blocks.size == 1, 'plan-block-missing-or-ambiguous')
  draft = blocks.first.first
  patch = YAML.safe_load(draft.sub("[YAML]\n", ''), aliases:false)
  validate_patch(patch)
  input = JSON.parse(STDIN.read)
  reference = File.read(File.join(root_path, 'scripts/liangxinyun_direct_readonly.lua'), encoding:'UTF-8').scan(/^ "(DOMAIN[^"\n]+)",$/).flatten
  audit = JSON.parse(File.read(File.join(root_path, 'profiles/tiktok-router-loongproxy-jp-us-liangxinyun/DIRECT_DIFF_AUDIT.json')))
  direct = reference.reject { |v| audit['repositoryOnly'].include?(v) }
  check(!direct.empty?, 'reference-fixture-missing')
  profile = File.join(root_path, 'profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.5.0')
  parse_module = ->(name) { YAML.safe_load(File.read(File.join(profile, name), encoding:'UTF-8').split('[YAML]',2).last, aliases:false) }
  base = YAML.overwrite(YAML.overwrite({}, parse_module.call('local-tiktok-proxy.conf')), parse_module.call('openclash-overwrite.conf'))
  base['rule-providers']['Manual-Direct']['payload'] = direct
  base['proxy-providers']['liangxinyun']['url'] = 'https://synthetic.invalid/subscription?key=SYNTHETIC_ONLY'
  base['proxy-providers']['liangxinyun']['headers'] = {'X-Synthetic'=>'SYNTHETIC_ONLY'}
  cases = []
  merged, changed = merge_checked(base, patch)
  isp_before = base.fetch('proxies', []).find { |p| p['name']=='TikTok-ISP-Local' }
  isp_after = merged.fetch('proxies', []).find { |p| p['name']=='TikTok-ISP-Local' }
  check(isp_before.is_a?(Hash) && isp_after==isp_before, 'synthetic-isp-node-not-preserved')
  protected_summary = {'allRulesPreserved'=>base['rules']==merged['rules'],
    'allRuleProvidersPreserved'=>base['rule-providers']==merged['rule-providers'],
    'dnsPreserved'=>base['dns']==merged['dns'], 'syntheticIspNodePreserved'=>isp_before==isp_after,
    'tiktokGroupsPreserved'=>%w[TikTok首跳 TikTok测速].all? { |name|
      a=base['proxy-groups'].find { |g| g['name']==name }; b=merged['proxy-groups'].find { |g| g['name']==name }
      a.is_a?(Hash) && a==b }, 'syntheticDirectCount'=>direct.size}
  check(protected_summary.values_at('allRulesPreserved','allRuleProvidersPreserved','dnsPreserved','syntheticIspNodePreserved','tiktokGroupsPreserved').all?, 'protected-data-not-preserved')
  cases << {'case'=>'synthetic-stable-profile', 'passed'=>true, 'changedPaths'=>changed}
  legacy = clone_value(base)
  index = validate_targets(legacy)
  %w[include-all include-all-proxies include-all-providers].each { |k| legacy['proxy-groups'][index][k] = true }
  legacy['proxy-groups'][index]['exclude-filter'] = 'obsolete'
  legacy['proxy-groups'] << {'name'=>'良心云-备用', 'type'=>'select', 'proxies'=>['DIRECT']}
  legacy['proxy-providers']['liangxinyun-backup'] = {'type'=>'file', 'path'=>'synthetic-unused'}
  merge_checked(legacy, patch)
  cases << {'case'=>'legacy-fields-and-similar-names', 'passed'=>true}
  arbitrary = clone_value(base)
  arbitrary['rule-providers']['Manual-Direct']['payload'] = ['DOMAIN,synthetic.invalid', 'DOMAIN,synthetic.invalid', *direct.reverse]
  merge_checked(arbitrary, patch)
  cases << {'case'=>'arbitrary-direct-order-and-duplicates', 'passed'=>true}
  again, _ = merge_checked(merged, patch)
  check(again == merged, 'not-idempotent')
  cases << {'case'=>'idempotent-remerge', 'passed'=>true}
  restored = Marshal.load(Marshal.dump(base))
  check(restored == base && restored != merged, 'backup-roundtrip-failed')
  cases << {'case'=>'in-memory-backup-restore', 'passed'=>true}
  aliased = clone_value(base)
  aliased['dns']['synthetic-shared-provider'] = aliased['proxy-providers']['liangxinyun']
  expect_rejected('alias-scope-guard-failed') { merge_checked(aliased, patch) }
  cases << {'case'=>'shared-target-alias-rejected', 'passed'=>true}
  {
    'missing-group'=>->(v) { v['proxy-groups'].reject! { |g| g['name']=='良心云' } },
    'duplicate-group'=>->(v) { v['proxy-groups'] << clone_value(v['proxy-groups'][validate_targets(v)]) },
    'missing-provider'=>->(v) { v['proxy-providers'].delete('liangxinyun') },
    'non-hash-provider'=>->(v) { v['proxy-providers']['liangxinyun'] = false }
  }.each do |label, change|
    invalid = clone_value(base); change.call(invalid)
    expect_rejected('target-guard-failed') { merge_checked(invalid, patch) }
    cases << {'case'=>label+'-rejected', 'passed'=>true}
  end
  {
    'bare-groups'=>->(v) { v['proxy-groups'] = v.delete('proxy-groups*') },
    'dns-patch'=>->(v) { v['dns'] = {'enable'=>false} },
    'tiktok-target'=>->(v) { v['proxy-groups*']['where']['name'] = 'TikTok首跳' },
    'other-provider-target'=>->(v) { v['proxy-providers*']['where']['key'] = 'other' }
  }.each do |label, change|
    invalid = clone_value(patch); change.call(invalid)
    expect_rejected('patch-guard-failed') { merge_checked(base, invalid) }
    cases << {'case'=>label+'-rejected', 'passed'=>true}
  end
  {
    'dns-change'=>->(v) { v['dns']['enable'] = !v['dns']['enable'] },
    'tiktok-change'=>->(v) { v['proxy-groups'].find { |g| g['name']=='TikTok首跳' }['type'] = 'url-test' },
    'direct-reorder'=>->(v) { v['rule-providers']['Manual-Direct']['payload'].reverse! }
  }.each do |label, change|
    invalid = clone_value(merged); change.call(invalid)
    check(!scope_preserved(base, invalid), 'scope-guard-failed')
    cases << {'case'=>label+'-detected', 'passed'=>true}
  end
  private_summary = nil
  if input['privateBaseline']
    private_base = input['privateBaseline']
    supplied = !private_base.fetch('proxy-providers', {})['liangxinyun'].is_a?(Hash)
    if supplied
      private_base['proxy-providers'] ||= {}
      check(private_base['proxy-providers'].is_a?(Hash), 'private-provider-container-invalid')
      private_base['proxy-providers']['liangxinyun'] = clone_value(base['proxy-providers']['liangxinyun'])
    end
    private_merged, private_changed = merge_checked(private_base, patch)
    private_summary = {'case'=>'private-historical-config', 'passed'=>true, 'sourceDate'=>'2026-11-23',
      'providerReconstructedWithSyntheticFields'=>supplied,
      'ispNodePresentInHistoricalLog'=>private_base.fetch('proxies', []).any? { |p| p['name']=='TikTok-ISP-Local' },
      'directCount'=>private_base.dig('rule-providers','Manual-Direct','payload').size,
      'allOutsideScopePreserved'=>scope_preserved(private_base,private_merged), 'changedPaths'=>private_changed}
    cases << private_summary
  end
  puts JSON.generate({'passed'=>true, 'mode'=>'local-official-overwrite-validation',
    'rubyVersion'=>RUBY_VERSION, 'openclashVersion'=>'0.48.002',
    'upstreamCommit'=>'e553e82e01c697aefbe1555261a503f425e00ccd', 'officialSourceSha256'=>source_hash,
    'draftSha256'=>Digest::SHA256.hexdigest(draft), 'cases'=>cases, 'caseCount'=>cases.size,
    'protectedData'=>protected_summary,
    'allOutsideScopePreserved'=>true, 'routerContacted'=>false, 'serviceInstalled'=>false,
    'coreStarted'=>false, 'formalAcceptance'=>false, 'privateBaselineUsed'=>!private_summary.nil?})
rescue MergeCheckFailure => e
  puts JSON.generate({'passed'=>false,'error'=>e.message}); exit 1
rescue StandardError
  puts JSON.generate({'passed'=>false,'error'=>'local-merge-validation-failed'}); exit 1
end
