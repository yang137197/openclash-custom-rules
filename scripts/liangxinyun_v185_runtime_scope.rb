# v1.8.5 read-only file scope/plan check. Ruby YAML only; no router API.
require 'yaml'
LIMIT = 8 * 1024 * 1024
GROUP = '良心云-按档位自动切换'
OLD_GROUP = '良心云'
OLD_INNER = '良心云-严格控制'
NAMES = {'TikTok首跳' => 'TIKTOK首跳', 'TikTok测速' => 'TIKTOK访问检测', OLD_GROUP => GROUP}.freeze
EXPECTED_PATCH = YAML.safe_load(<<~'PATCH', permitted_classes: [], permitted_symbols: [], aliases: false)
{"proxy-groups!":[{"name":"TIKTOK首跳","type":"select","url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204,"proxies":["REJECT"],"default-selected":"REJECT","include-all":true,"filter":"^(REJECT|(?:🇯🇵 )?日本Z0[1-4] \\| IEPL[ \\t]*)$","empty-fallback":"REJECT"},{"name":"TIKTOK访问检测","type":"select","url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204,"include-all-proxies":true,"filter":"^TikTok-ISP-Local$","empty-fallback":"REJECT"},{"name":"良心云-按档位自动切换","type":"select","proxies":["REJECT"],"use":["liangxinyun"],"default-selected":"REJECT","filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","empty-fallback":"REJECT","hidden":false,"url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204}],"proxies*":{"where":{"name":"TikTok-ISP-Local"},"set":{"dialer-proxy":"TIKTOK首跳"}},"proxy-providers*":{"where":{"key":"liangxinyun"},"set":{"filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","health-check!":{"enable":true,"url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204}}},"dns":{"nameserver-policy!":{"geosite:tiktok":["https://1.1.1.1/dns-query#TIKTOK访问检测","https://8.8.8.8/dns-query#TIKTOK访问检测"],"+.xn--ngstr-lra8j.com":["https://1.1.1.1/dns-query#良心云-按档位自动切换","https://8.8.8.8/dns-query#良心云-按档位自动切换"],"geosite:google":["https://1.1.1.1/dns-query#良心云-按档位自动切换","https://8.8.8.8/dns-query#良心云-按档位自动切换"]}},"rule-providers*":{"where":{"proxy":"良心云"},"set":{"proxy":"良心云-按档位自动切换"}},"rules!":["GEOSITE,private,DIRECT","GEOIP,private,DIRECT,no-resolve","IP-CIDR,10.0.0.0/8,DIRECT,no-resolve","IP-CIDR,172.16.0.0/12,DIRECT,no-resolve","IP-CIDR,192.168.0.0/16,DIRECT,no-resolve","IP-CIDR,127.0.0.0/8,DIRECT,no-resolve","IP-CIDR,169.254.0.0/16,DIRECT,no-resolve","IP-CIDR,224.0.0.0/4,DIRECT,no-resolve","IP-CIDR6,::1/128,DIRECT,no-resolve","IP-CIDR6,fc00::/7,DIRECT,no-resolve","IP-CIDR6,fe80::/10,DIRECT,no-resolve","IP-CIDR6,ff00::/8,DIRECT,no-resolve","DOMAIN-SUFFIX,github.com,良心云-按档位自动切换","DOMAIN-SUFFIX,githubusercontent.com,良心云-按档位自动切换","DOMAIN-SUFFIX,githubassets.com,良心云-按档位自动切换","GEOSITE,tiktok,TIKTOK访问检测","GEOSITE,tiktok,REJECT","DOMAIN-SUFFIX,xn--ngstr-lra8j.com,良心云-按档位自动切换","GEOSITE,google,良心云-按档位自动切换","RULE-SET,Manual-Direct,DIRECT","RULE-SET,oc-cn-domain,DIRECT","GEOIP,CN,DIRECT,no-resolve","MATCH,良心云-按档位自动切换","MATCH,REJECT"]}
PATCH
EXPECTED_GROUPS = EXPECTED_PATCH.fetch('proxy-groups!').freeze
PROBES = %w[url interval timeout lazy expected-status].freeze
PREVIOUS_INNER = YAML.safe_load(<<~'INNER', permitted_classes: [], permitted_symbols: [], aliases: false)
{"name":"良心云-严格控制","type":"select","proxies":["REJECT"],"use":["liangxinyun"],"default-selected":"REJECT","filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","empty-fallback":"REJECT","hidden":false,"url":"https://www.gstatic.com/generate_204","interval":60,"timeout":5000,"lazy":false,"expected-status":204}
INNER
LEGACY_INNER = YAML.safe_load(<<~'INNER', permitted_classes: [], permitted_symbols: [], aliases: false)
{"name":"良心云-严格控制","type":"select","proxies":["REJECT"],"use":["liangxinyun"],"default-selected":"REJECT","filter":"日本专线|日本高速|美国.*流媒体|流媒体.*美国|美国高速","empty-fallback":"REJECT","hidden":true}
INNER

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

def clone_value(value)
  Marshal.load(Marshal.dump(value))
end

def targets(config)
  groups = config.fetch('proxy-groups')
  require_check(groups.is_a?(Array) && groups.all? { |g| g.is_a?(Hash) })
  names = groups.map { |g| g['name'] }
  require_check(names.all? { |n| n.is_a?(String) } && names.uniq.length == names.length)
  name = names.include?(GROUP) ? GROUP : OLD_GROUP
  require_check(names.count(name) == 1)
  provider = config.fetch('proxy-providers').fetch('liangxinyun')
  require_check(provider.is_a?(Hash))
  [groups.find { |g| g['name'] == name }, provider]
end

def direct(config)
  data = config.fetch('rule-providers').fetch('Manual-Direct')
  require_check(data['type'] == 'inline' && data['payload'].is_a?(Array))
  require_check(data['payload'].all? { |v| v.is_a?(String) })
  data['payload']
end

def baseline_contract(config)
  target, provider = targets(config)
  names = config['proxy-groups'].map { |g| g['name'] }
  old = ['TikTok首跳', 'TikTok测速', OLD_GROUP]
  require_check([old, old + [OLD_INNER], EXPECTED_GROUPS.map { |g| g['name'] }].include?(names))
  if names.include?(OLD_INNER)
    inner = config['proxy-groups'][-1]
    require_check([canonical(PREVIOUS_INNER), canonical(LEGACY_INNER)].include?(canonical(inner)))
    require_check(target['type'] == 'url-test' && target['proxies'] == [OLD_INNER] && !target['use'])
  else
    require_check(target['type'] == 'select' && target['use'] == ['liangxinyun'])
  end
  require_check(provider.fetch('override', {})['additional-prefix'] == 'LXY: ')
  require_check(%w[http file].include?(provider['type']) && provider['path'].is_a?(String))
  require_check(provider['type'] != 'http' || (provider['url'].is_a?(String) && !provider['url'].empty?))
  require_check(config['proxy-groups'][0, 2].all? { |g| g['type'] == 'select' })
  isp = config.fetch('proxies').select { |p| p['name'] == 'TikTok-ISP-Local' }
  require_check(isp.length == 1 && isp[0]['type'] == 'socks5' &&
                isp[0]['dialer-proxy'] == names[0] && isp[0]['udp'] == false)
  direct(config)
  require_check(config['rules'].is_a?(Array) && config['dns'].is_a?(Hash))
end

def protected(config)
  value = clone_value(config)
  target, provider = targets(value)
  value['proxy-groups'] = value['proxy-groups'].filter_map do |g|
    next nil if g['name'] == OLD_INNER
    next({'name' => GROUP}) if g.equal?(target)
    g['name'] = NAMES.fetch(g['name'], g['name'])
    PROBES.each { |k| g.delete(k) }
    g
  end
  value['proxies'].each do |p|
    if p['name'] == 'TikTok-ISP-Local'
      p['dialer-proxy'] = NAMES.fetch(p['dialer-proxy'], p['dialer-proxy'])
    end
  end
  %w[filter health-check].each { |k| provider.delete(k) }
  value['rule-providers'].each_value do |p|
    p['proxy'] = NAMES.fetch(p['proxy'], p['proxy']) if p.is_a?(Hash) && p['proxy'].is_a?(String)
  end
  policy = value['dns'].fetch('nameserver-policy', {})
  require_check(policy.is_a?(Hash))
  policy.each do |key, servers|
    list = servers.is_a?(Array)
    updated = (list ? servers : [servers]).map do |server|
      require_check(server.is_a?(String))
      base, sep, tag = server.rpartition('#')
      sep.empty? ? server : base + sep + NAMES.fetch(tag, tag)
    end
    policy[key] = list ? updated : updated[0]
  end
  value['rules'].map! do |rule|
    require_check(rule.is_a?(String))
    parts = rule.split(',', -1)
    pos = parts[-1] == 'no-resolve' ? -2 : -1
    parts[pos] = NAMES.fetch(parts[pos], parts[pos])
    parts.join(',')
  end
  canonical(value)
end

def project(before)
  # Independent fixed-patch projection; no code execution or filesystem writes.
  value = clone_value(before)
  value['proxy-groups'] = clone_value(EXPECTED_GROUPS)
  value['proxies'].each do |p|
    p['dialer-proxy'] = 'TIKTOK首跳' if p['name'] == 'TikTok-ISP-Local'
  end
  provider = value['proxy-providers'].fetch('liangxinyun')
  set = EXPECTED_PATCH.fetch('proxy-providers*').fetch('set')
  provider['filter'] = set.fetch('filter')
  provider['health-check'] = clone_value(set.fetch('health-check!'))
  value['dns']['nameserver-policy'] = clone_value(EXPECTED_PATCH.fetch('dns').fetch('nameserver-policy!'))
  value['rule-providers'].each_value do |p|
    p['proxy'] = GROUP if p.is_a?(Hash) && p['proxy'] == OLD_GROUP
  end
  value['rules'] = clone_value(EXPECTED_PATCH.fetch('rules!'))
  value
end

begin
  stage = 'arguments'
  plan = ARGV[0] == '--plan'
  ARGV.shift if plan
  require_check(ARGV.length == 3)
  baseline_raw = STDIN.read(LIMIT + 1)
  raws = ARGV.map { |path| File.binread(path, LIMIT + 1) }
  stage = 'input'
  baseline = parse_input(baseline_raw)
  actual = parse_input(raws[0])
  cloud = parse_input(raws[1], true)
  patch = parse_input(raws[2], true)
  canonical(baseline); canonical(actual)
  stage = 'patch-contract'
  require_check(canonical(patch) == canonical(EXPECTED_PATCH))
  stage = 'baseline-contract'
  baseline_contract(baseline)
  baseline_contract(actual)
  require_check(!plan || canonical(baseline) == canonical(actual))
  stage = 'direct-source'
  baseline_count = direct(baseline).length
  expected_direct = direct(cloud)
  require_check(canonical(direct(actual)) == canonical(expected_direct))
  baseline.fetch('rule-providers').fetch('Manual-Direct')['payload'] = expected_direct
  current = plan ? project(actual) : actual
  stage = 'candidate-contract'
  baseline_contract(current)
  require_check(canonical(current['proxy-groups']) == canonical(EXPECTED_GROUPS))
  set = EXPECTED_PATCH.fetch('proxy-providers*').fetch('set')
  _, provider = targets(current)
  require_check(provider['filter'] == set.fetch('filter'))
  require_check(canonical(provider['health-check']) == canonical(set.fetch('health-check!')))
  require_check(canonical(current['rules']) == canonical(EXPECTED_PATCH.fetch('rules!')))
  require_check(canonical(current['dns']['nameserver-policy']) == canonical(EXPECTED_PATCH.fetch('dns').fetch('nameserver-policy!')))
  require_check(current['rule-providers'].values.all? { |p| !p.is_a?(Hash) || !NAMES.key?(p['proxy']) })
  require_check(current['proxies'].all? { |p| !NAMES.key?(p['dialer-proxy']) })
  stage = 'outside-scope'
  require_check(protected(baseline) == protected(current))
  stage = 'file-snapshot'
  require_check(ARGV.each_with_index.all? { |path, i| File.binread(path, LIMIT + 1) == raws[i] })
  mode = plan ? 'candidate-plan-readonly' : 'runtime-scope-readonly'
  puts '{"mode":"' + mode + '","candidateVersion":"1.8.5","passed":true,"directMatchesCloud":true,' +
       '"outsideAuthorizedScopeUnchanged":true,"tiktokRoutingUnchanged":true,"automaticProbesConfigured":true,' +
       '"globalScheduledProbe":false,"threeExplicitGroups":true,"baselineDirectCount":' + baseline_count.to_s +
       ',"expectedDirectCount":' + expected_direct.length.to_s + ',"currentDirectCount":' + direct(current).length.to_s +
       ',"apiRequests":0,"probeRequests":0,"selectionApplied":false,"configurationWritten":false,' +
       '"activeCoreConfigurationVerified":false,"formalAcceptance":false}'
rescue StandardError
  puts '{"mode":"scope-check-readonly","passed":false,"check":"' + stage.to_s +
       '","apiRequests":0,"probeRequests":0,"selectionApplied":false,"configurationWritten":false,"formalAcceptance":false}'
  exit 1
end
