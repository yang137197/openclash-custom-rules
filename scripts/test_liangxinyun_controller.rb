#!/usr/bin/env ruby
# Deterministic policy, freshness and write-scope checks without an API server.
require_relative '../profiles/tiktok-router-loongproxy-jp-us-liangxinyun/versions/v1.7.0/liangxinyun-controller'
require 'stringio'

Policy = LiangxinyunStrict
NOW = Time.utc(2026, 11, 23, 0)
URL = Policy::TEST_URL
checks = 0
assert = lambda do |condition, description|
  raise description unless condition
  checks += 1
end

def node(name, delay, alive: true, at: NOW, url: URL)
  { 'name' => 'LXY: ' + name, 'extra' => { url => {
    'alive' => alive, 'history' => [{ 'time' => at.iso8601, 'delay' => delay }]
  } } }
end

proxies = [node('🇯🇵日本专线01|BGP|流媒体', 120), node('🇯🇵日本专线02|BGP|流媒体', 40),
           node('🇯🇵日本高速01|BGP|CUCM', 30), node('🇯🇵日本高速02|BGP|CUCM', 20),
           node('🇺🇸美国05|流媒体|0.1x', 12), node('🇺🇸美国06|流媒体|0.1x', 10),
           node('🇺🇸美国高速05|CTCU|0.1x', 6), node('🇺🇸美国高速06|CTCU|0.1x', 5)]
members = ['REJECT', *proxies.map { |p| p['name'] }]
decide = ->(items, current = 'REJECT') { Policy.decide(items, members, url: URL, now: NOW, max_age: 130, current: current) }

(0...256).each do |mask|
  items = Marshal.load(Marshal.dump(proxies))
  items.each_with_index do |proxy, index|
    next if mask[index] == 1
    proxy['extra'][URL]['alive'] = false
    proxy['extra'][URL]['history'].last['delay'] = 0
  end
  choice = decide.call(items)
  survivors = (0...8).select { |index| mask[index] == 1 }
  if survivors.empty?
    assert.call(choice[:name] == 'REJECT', 'all-failed must reject')
  else
    first_tier = survivors.map { |index| index / 2 }.min
    candidates = survivors.select { |index| index / 2 == first_tier }
    best = candidates.min_by { |index| proxies[index]['extra'][URL]['history'].last['delay'] }
    assert.call(choice[:name] == proxies[best]['name'], "tier priority/minimum violated for mask #{mask}")
  end
end

missing = Marshal.load(Marshal.dump(proxies))
missing[0].delete('extra')
missing[1]['extra'][URL]['alive'] = false
missing[1]['extra'][URL]['history'].last['delay'] = 0
assert.call(decide.call(missing)[:name] == 'REJECT', 'unknown high tier must not permit a lower tier')
missing[0]['extra'] = nil
assert.call(decide.call(missing)[:name] == 'REJECT', 'null history must be unknown')
missing[0] = node(proxies[0]['name'].delete_prefix('LXY: '), 20, at: NOW - 131)
assert.call(decide.call(missing)[:name] == 'REJECT', 'stale high-tier history must block downgrade')
missing[0] = node(proxies[0]['name'].delete_prefix('LXY: '), 20, at: NOW + 6)
assert.call(decide.call(missing)[:name] == 'REJECT', 'future clock data must not be trusted')
missing[0] = node(proxies[0]['name'].delete_prefix('LXY: '), 20, url: 'https://other.test/')
assert.call(decide.call(missing)[:name] == 'REJECT', 'tests for a different URL must not authorize downgrade')
equal = [node('日本专线01', 20), node('日本专线02', 20)]
equal_members = equal.map { |p| p['name'] }
choice = Policy.decide(equal, equal_members, url: URL, now: NOW, max_age: 130, current: equal_members[1])
assert.call(choice[:name] == equal_members[1], 'equal delays should retain the current node')
['日本专线01', 'LXY: 香港专线01|流媒体', 'LXY: 新加坡专线01|流媒体', 'TikTok-ISP-Local', 'DIRECT'].each do |name|
  assert.call(Policy.tier(name).nil?, "wrong source/category accepted: #{name}")
end

class FakeAPI
  attr_accessor :g, :p
  attr_reader :writes
  def initialize(proxies)
    @g = { 'type' => 'Selector', 'all' => ['REJECT', *proxies.map { |p| p['name'] }], 'now' => 'REJECT' }
    @p = { 'testUrl' => URL, 'expectedStatus' => '204', 'proxies' => proxies }
    @writes = []
  end
  def group = @g.dup
  def provider = @p
  def probe; end
  def select(name)
    @writes << name
    @g['now'] = name
  end
end

original_stdout = $stdout
$stdout = StringIO.new
begin
  api = FakeAPI.new([node('日本专线01', 20, at: Time.now)])
  controller = Policy::Controller.new(api, url: URL, max_age: 130)
  api.g['now'] = api.p['proxies'][0]['name']
  controller.step
  assert.call(api.writes == ['REJECT', api.p['proxies'][0]['name']], 'startup must reject then restore a freshly justified choice')
  api.p['proxies'][0].delete('extra')
  controller.step
  assert.call(api.writes.last == 'REJECT', 'loss of measurements must reject')
  controller.reject
  assert.call(api.writes.last == 'REJECT', 'graceful shutdown must reject')
  %w[Selector Fallback].each do |type|
    bad = FakeAPI.new([node('日本专线01', 20)])
    bad.g['type'] = type
    bad.g['all'].delete('REJECT') if type == 'Selector'
    begin
      Policy::Controller.new(bad, url: URL, max_age: 130).step
      raise 'noncandidate profile was accepted'
    rescue Policy::Error
      assert.call(bad.writes.empty?, 'existing stable/fallback profile must not be mutated')
    end
  end
  changed = FakeAPI.new([node('日本专线01', 20)])
  changed.p['proxies'] << node('日本专线12', 5)
  begin
    Policy::Controller.new(changed, url: URL, max_age: 130).step
    raise 'inconsistent snapshot was accepted'
  rescue Policy::Error
    assert.call(!changed.writes.empty? && changed.writes.all? { |name| name == 'REJECT' },
                'membership race must reject instead of authorizing a lower-tier choice')
  end
  broken = FakeAPI.new([node('日本专线01', 20, at: Time.now)])
  def broken.provider = raise(Policy::Error, 'provider temporarily unavailable')
  begin
    Policy::Controller.new(broken, url: URL, max_age: 130).step
    raise 'provider failure was ignored'
  rescue Policy::Error
    assert.call(broken.writes.all? { |name| name == 'REJECT' } && !broken.writes.empty?,
                'provider API failure must still reject on a recognized strict selector')
    last_event = JSON.parse($stdout.string.lines.last)
    assert.call(last_event['verifiedSelection'] == false && !last_event.key?('name'),
                'API error output must not claim a verified actual selection')
  end
ensure
  $stdout = original_stdout
end

['http://example.com:9090', 'http://127.0.0.1:9090/path', 'http://user@127.0.0.1:9090'].each do |url|
  begin
    Policy::API.new(url, '')
    raise 'nonloopback or credential-bearing API URL accepted'
  rescue Policy::Error
    assert.call(true, 'unsafe API URL rejected')
  end
end
puts "PASS: #{checks} strict controller assertions"
