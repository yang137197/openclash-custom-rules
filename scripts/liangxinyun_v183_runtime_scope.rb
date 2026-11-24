# Read-only v1.8.3 runtime scope check. Ruby YAML only; no JSON/Open3/OptionParser dependencies.
# Baseline YAML arrives on stdin; argv: current-runtime.yaml cloud.conf incremental.conf.
require 'yaml'

LIMIT = 8 * 1024 * 1024
PUBLIC = '良心云'
INTERNAL = '良心云-严格控制'
EXPECTED_PATCH = YAML.safe_load(<<~'PATCH', permitted_classes: [], permitted_symbols: [], aliases: false)
{"proxy-groups*":{"where":{"name":"良心云"},"set":{"type":"url-test","url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204,"tolerance":0,"empty-fallback":"REJECT","hidden":false,"proxies!":["良心云-严格控制"],"use-":null,"include-all-":null,"include-all-proxies-":null,"include-all-providers-":null,"exclude-filter-":null,"default-selected-":null,"filter-":null}},"proxy-groups+":[{"name":"良心云-严格控制","type":"select","proxies":["REJECT"],"use":["liangxinyun"],"default-selected":"REJECT","filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","empty-fallback":"REJECT","hidden":true}],"proxy-providers*":{"where":{"key":"liangxinyun"},"set":{"filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","health-check!":{"enable":true,"url":"https://www.gstatic.com/generate_204","expected-status":204,"interval":60,"timeout":5000,"lazy":false}}}}
PATCH
LEGACY_FIELDS = %w[type proxies use include-all include-all-proxies include-all-providers exclude-filter default-selected filter empty-fallback].freeze

def require_check(value)
  raise 'check-failed' unless value
end

def parse_input(raw, mod = false)
  require_check(raw.bytesize <= LIMIT)
  text = raw.dup.force_encoding(Encoding::UTF_8)
  require_check(text.valid_encoding?)
  if mod
    lines = text.lines
    sections = lines.each_index.select { |i| lines[i].strip.match?(/\A\[[^\]]+\]\z/) }
    require_check(sections.length == 1 && lines[sections[0]].strip == '[YAML]')
    require_check(lines[0...sections[0]].all? { |line| line.strip.empty? || line.lstrip.start_with?('#') })
    text = lines[(sections[0] + 1)..].join
  end
  walk = lambda do |node|
    require_check(!node.is_a?(Psych::Nodes::Alias))
    require_check(!node.respond_to?(:anchor) || node.anchor.nil?)
    if node.is_a?(Psych::Nodes::Mapping)
      keys = node.children.each_slice(2).map { |key, _| require_check(key.is_a?(Psych::Nodes::Scalar)); key.value }
      require_check(keys.uniq.length == keys.length)
    end
    (node.children || []).each { |child| walk.call(child) }
  end
  walk.call(Psych.parse_stream(text))
  value = YAML.safe_load(text, permitted_classes: [], permitted_symbols: [], aliases: false)
  require_check(value.is_a?(Hash))
  value
end

def canonical(value)
  case value
  when Hash
    require_check(value.keys.all? { |key| key.is_a?(String) })
    ['Hash', value.keys.sort.map { |key| [key, canonical(value[key])] }]
  when Array
    ['Array', value.map { |item| canonical(item) }]
  when String, Integer, TrueClass, FalseClass, NilClass
    [value.class.name, value]
  when Float
    require_check(value.finite?)
    ['Float', value]
  else
    raise 'unsupported-value'
  end
end

def targets(config)
  groups = config.fetch('proxy-groups')
  require_check(groups.is_a?(Array) && groups.all? { |group| group.is_a?(Hash) })
  names = groups.map { |group| group['name'] }
  require_check(names.all? { |name| name.is_a?(String) } && names.uniq.length == names.length)
  require_check(names.count(PUBLIC) == 1)
  provider = config.fetch('proxy-providers').fetch('liangxinyun')
  require_check(provider.is_a?(Hash))
  [groups.find { |group| group['name'] == PUBLIC }, provider]
end

def direct(config)
  data = config.fetch('rule-providers').fetch('Manual-Direct')
  require_check(data['type'] == 'inline' && data['payload'].is_a?(Array))
  require_check(data['payload'].all? { |item| item.is_a?(String) })
  data['payload']
end

begin
  stage = 'arguments'
  require_check(ARGV.length == 3)
  baseline_raw = STDIN.read(LIMIT + 1)
  stage = 'read-files'
  raws = ARGV.map { |path| File.binread(path, LIMIT + 1) }
  stage = 'input'
  baseline = parse_input(baseline_raw)
  current = parse_input(raws[0])
  cloud = parse_input(raws[1], true)
  patch = parse_input(raws[2], true)
  canonical(baseline); canonical(current)
  baseline_count = direct(baseline).length
  expected_direct = direct(cloud)
  stage = 'direct-source'
  require_check(canonical(direct(current)) == canonical(expected_direct))
  # Authorised source updates replace only this expected payload, with order/duplicates preserved.
  baseline.fetch('rule-providers').fetch('Manual-Direct')['payload'] = expected_direct

  stage = 'patch-contract'
  require_check(canonical(patch) == canonical(EXPECTED_PATCH))
  require_check(patch.keys.sort == ['proxy-groups*', 'proxy-groups+', 'proxy-providers*'].sort)
  require_check(patch.fetch('proxy-groups*').fetch('where') == {'name' => PUBLIC})
  require_check(patch.fetch('proxy-providers*').fetch('where') == {'key' => 'liangxinyun'})
  additions = patch.fetch('proxy-groups+')
  require_check(additions.is_a?(Array) && additions.length == 1)
  expected_inner = additions[0]
  require_check(expected_inner['name'] == INTERNAL)
  outer_set = patch.fetch('proxy-groups*').fetch('set')
  provider_set = patch.fetch('proxy-providers*').fetch('set')
  fields = (LEGACY_FIELDS + outer_set.keys.map { |key| key.sub(/[!+*-]\z/, '') }).uniq

  stage = 'outer-group'
  outer, provider = targets(current)
  outer_set.each do |key, expected|
    plain = key.sub(/[!+*-]\z/, '')
    if key.end_with?('-')
      require_check(!outer.key?(plain))
    else
      require_check(canonical(outer.fetch(plain)) == canonical(expected))
    end
  end
  stage = 'internal-group'
  require_check(current.fetch('proxy-groups').count { |group| group['name'] == INTERNAL } == 1)
  inner = current['proxy-groups'].find { |group| group['name'] == INTERNAL }
  require_check(canonical(inner) == canonical(expected_inner))
  stage = 'provider-contract'
  require_check(canonical(provider.fetch('filter')) == canonical(provider_set.fetch('filter')))
  require_check(canonical(provider.fetch('health-check')) == canonical(provider_set.fetch('health-check!')))

  mask = lambda do |input|
    value = Marshal.load(Marshal.dump(input))
    group, imported = targets(value)
    internals = value['proxy-groups'].select { |item| item['name'] == INTERNAL }
    require_check(internals.length <= 1)
    require_check(internals.empty? || canonical(internals[0]) == canonical(expected_inner))
    value['proxy-groups'].reject! { |item| item['name'] == INTERNAL }
    fields.each { |field| group.delete(field) }
    %w[filter health-check].each { |field| imported.delete(field) }
    canonical(value)
  end
  stage = 'outside-scope'
  require_check(mask.call(baseline) == mask.call(current))
  stage = 'file-snapshot'
  require_check(ARGV.each_with_index.all? { |path, index| File.binread(path, LIMIT + 1) == raws[index] })
  puts '{"mode":"runtime-scope-readonly","passed":true,"directMatchesCloud":true,"outsideLiangxinyunUnchanged":true,"baselineDirectCount":' +
       baseline_count.to_s + ',"expectedDirectCount":' + expected_direct.length.to_s +
       ',"currentDirectCount":' + direct(current).length.to_s +
       ',"apiRequests":0,"probeRequests":0,"selectionApplied":false,"configurationWritten":false,"activeCoreConfigurationVerified":false,"formalAcceptance":false}'
rescue StandardError
  puts '{"mode":"runtime-scope-readonly","passed":false,"check":"' + stage.to_s +
       '","apiRequests":0,"probeRequests":0,"selectionApplied":false,"configurationWritten":false,"formalAcceptance":false}'
  exit 1
end
