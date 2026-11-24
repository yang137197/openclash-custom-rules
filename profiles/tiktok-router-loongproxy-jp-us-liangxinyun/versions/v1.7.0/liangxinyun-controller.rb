#!/usr/bin/env ruby
# No subscriptions or credentials are written by this controller.
require 'json'
require 'open3'
require 'optparse'
require 'time'
require 'uri'

module LiangxinyunStrict
  GROUP = '良心云'.freeze
  PROVIDER = 'liangxinyun'.freeze
  TEST_URL = 'https://www.gstatic.com/generate_204'.freeze
  TIERS = ['日本专线', '日本高速', '美国流媒体', '美国高速'].freeze
  FILTERS = [/日本专线/, /日本高速/, /美国.*流媒体|流媒体.*美国/, /美国高速/].freeze
  class Error < StandardError; end

  def self.tier(name)
    return nil unless name.is_a?(String) && name.start_with?('LXY: ')
    FILTERS.index { |pattern| pattern.match?(name) }
  end

  # Missing/stale measurements are unknown, never proof of an entire tier failing.
  def self.measurement(proxy, url, now, max_age)
    extra = proxy['extra']
    return [:unknown, nil] unless extra.is_a?(Hash)
    state = extra[url]
    return [:unknown, nil] unless state.is_a?(Hash)
    history = state['history']
    return [:unknown, nil] unless history.is_a?(Array)
    last = history.last
    return [:unknown, nil] unless last.is_a?(Hash)
    stamp = Time.iso8601(last.fetch('time'))
    return [:unknown, nil] if now - stamp > max_age || stamp - now > 5
    delay = last['delay']
    return [:dead, nil] if state['alive'] == false && delay == 0
    return [:unknown, nil] unless state['alive'] == true && delay.is_a?(Integer) && delay.between?(1, 65_534)
    [:healthy, delay]
  rescue ArgumentError, KeyError, TypeError
    [:unknown, nil]
  end

  def self.decide(proxies, members, url:, now:, max_age:, current:)
    rows = proxies.filter_map do |proxy|
      name = proxy['name']
      rank = tier(name)
      next if rank.nil? || !members.include?(name)
      status, delay = measurement(proxy, url, now, max_age)
      { name: name, tier: rank, status: status, delay: delay }
    end
    counts = TIERS.each_index.map do |rank|
      group = rows.select { |row| row[:tier] == rank }
      { tier: TIERS[rank], total: group.length,
        healthy: group.count { |row| row[:status] == :healthy },
        unknown: group.count { |row| row[:status] == :unknown } }
    end
    TIERS.each_index do |rank|
      group = rows.select { |row| row[:tier] == rank }
      healthy = group.select { |row| row[:status] == :healthy }
      unless healthy.empty?
        # Equal measurements retain the current choice; no nonzero tolerance.
        best = healthy.min_by { |row| [row[:delay], row[:name] == current ? 0 : 1, row[:name]] }
        return { name: best[:name], tier: TIERS[rank], delay: best[:delay], reason: 'lowest-delay-in-highest-healthy-tier', counts: counts }
      end
      if group.any? { |row| row[:status] == :unknown }
        return { name: 'REJECT', tier: TIERS[rank], reason: 'higher-tier-measurements-unknown', counts: counts }
      end
    end
    { name: 'REJECT', tier: nil, reason: 'all-tiers-failed-or-empty', counts: counts }
  end

  class API
    def initialize(base, secret, timeout: 30)
      uri = URI.parse(base)
      unless uri.scheme == 'http' && ['127.0.0.1', 'localhost', '[::1]', '::1'].include?(uri.host) &&
             uri.userinfo.nil? && uri.query.nil? && uri.fragment.nil? && ['', '/'].include?(uri.path)
        raise Error, 'API must use a loopback HTTP address without userinfo or a path'
      end
      raise Error, 'invalid API secret' if secret.match?(/[\r\n\x00]/)
      @base, @secret, @timeout = base.sub(%r{/$}, ''), secret, timeout
    rescue URI::InvalidURIError
      raise Error, 'invalid API address'
    end

    def request(method, path, body = nil)
      # stdin curl config keeps the API secret out of argv and shell expansion.
      config = ["url = #{JSON.generate(@base + path)}", "request = #{JSON.generate(method)}",
                'silent', 'show-error', 'fail', 'noproxy = "*"', 'connect-timeout = "2"',
                "max-time = #{@timeout}", 'header = "Content-Type: application/json"']
      config << "header = #{JSON.generate('Authorization: Bearer ' + @secret)}" unless @secret.empty?
      config << "data-binary = #{JSON.generate(JSON.generate(body))}" unless body.nil?
      output, _errors, status = Open3.capture3('curl', '--config', '-', stdin_data: config.join("\n") + "\n")
      raise Error, "API request failed (curl exit #{status.exitstatus})" unless status.success?
      output.empty? ? nil : JSON.parse(output)
    rescue JSON::ParserError
      raise Error, 'API returned invalid JSON'
    rescue Errno::ENOENT
      raise Error, 'curl executable is missing'
    end

    def group
      request('GET', '/proxies/' + escape(GROUP))
    end

    def provider
      request('GET', '/providers/proxies/' + PROVIDER)
    end

    def probe
      request('GET', '/providers/proxies/' + PROVIDER + '/healthcheck')
    end

    def select(name)
      raise Error, 'refused selection outside the allowed source/categories' unless name == 'REJECT' || !LiangxinyunStrict.tier(name).nil?
      request('PUT', '/proxies/' + escape(GROUP), { 'name' => name })
    end

    def escape(value)
      URI.encode_www_form_component(value).gsub('+', '%20')
    end
  end

  class Controller
    def initialize(api, url:, max_age:, state_file: nil, dry_run: false)
      @api, @url, @max_age, @state_file, @dry_run = api, url, max_age, state_file, dry_run
      @managed, @last_event = false, nil
    end

    def validate_group(group)
      raise Error, 'API returned an invalid group snapshot' unless group.is_a?(Hash)
      members = group['all']
      unless group['type'] == 'Selector' && members.is_a?(Array) && members.first == 'REJECT' &&
             members.all? { |name| name == 'REJECT' || !LiangxinyunStrict.tier(name).nil? }
        raise Error, 'waiting for the strict candidate selector; existing profile untouched'
      end
      members
    end

    def validate(group, provider)
      members = validate_group(group)
      raise Error, 'API returned an invalid provider snapshot' unless provider.is_a?(Hash)
      unless provider['testUrl'] == @url && provider['expectedStatus'] == '204' && provider['proxies'].is_a?(Array) &&
             provider['proxies'].all? { |proxy| proxy.is_a?(Hash) && !LiangxinyunStrict.tier(proxy['name']).nil? }
        raise Error, 'provider must expose only allowed LXY nodes and the agreed test URL'
      end
      # A concurrent subscription update must not make unobserved nodes look absent.
      unless (members - ['REJECT']).sort == provider['proxies'].map { |p| p['name'] }.sort
        raise Error, 'subscription membership changed during the snapshot; retry required'
      end
      members
    end

    def step(probe: false)
      group = @api.group
      validate_group(group)
      unless @managed
        @api.select('REJECT') unless @dry_run
        group['now'] = 'REJECT' unless @dry_run
        @managed = true
      end
      provider = @api.provider
      members = validate(group, provider)
      if probe
        @api.probe
        group, provider = @api.group, @api.provider
        members = validate(group, provider)
      end
      decision = LiangxinyunStrict.decide(provider['proxies'], members, url: @url,
                                         now: Time.now, max_age: @max_age, current: group['now'])
      @api.select(decision[:name]) unless @dry_run || group['now'] == decision[:name]
      publish(decision.merge(dryRun: @dry_run))
      decision
    rescue Error, IOError, SystemCallError => e
      reject
      publish(requestedName: 'REJECT', reason: e.message, verifiedSelection: false)
      raise Error, e.message
    end

    def reject
      return unless @managed && !@dry_run
      validate_group(@api.group)
      @api.select('REJECT')
    rescue Error, IOError, SystemCallError
      # Never claim the core changed selection when its API is unavailable.
      nil
    end

    def publish(event)
      data = event.merge(at: Time.now.utc.iso8601, group: GROUP)
      if @state_file
        temporary = @state_file + ".#{Process.pid}.#{Time.now.nsec}.tmp"
        File.open(temporary, File::WRONLY | File::CREAT | File::EXCL, 0o600) { |file| file.write(JSON.generate(data) + "\n") }
        File.rename(temporary, @state_file)
      end
      fingerprint = event.reject { |key, _| key == :counts }
      if fingerprint != @last_event
        puts JSON.generate(data)
        $stdout.flush
        @last_event = fingerprint
      end
    end
  end

  def self.uci(key, required: false)
    output, _errors, status = Open3.capture3('uci', '-q', 'get', "openclash.config.#{key}")
    raise Error, "OpenClash #{key} is unavailable" if required && !status.success?
    status.success? ? output.chomp : ''
  rescue Errno::ENOENT
    raise Error, 'uci is missing; fixture runs must supply a loopback API and secret file'
  end

  def self.main(argv)
    options = { interval: 60.0, poll: 2.0, max_age: 130.0, url: TEST_URL }
    parser = OptionParser.new do |p|
      p.on('--once') { options[:once] = true }
      p.on('--dry-run') { options[:dry_run] = true }
      p.on('--preflight') { options[:preflight] = true }
      p.on('--interval SECONDS', Float) { |v| options[:interval] = v }
      p.on('--poll SECONDS', Float) { |v| options[:poll] = v }
      p.on('--max-age SECONDS', Float) { |v| options[:max_age] = v }
      p.on('--test-url URL') { |v| options[:url] = v }
      p.on('--api-url URL') { |v| options[:api_url] = v }
      p.on('--secret-file PATH') { |v| options[:secret_file] = v }
      p.on('--state-file PATH') { |v| options[:state_file] = v }
      p.on('--lock-file PATH') { |v| options[:lock_file] = v }
    end
    parser.parse!(argv)
    raise Error, 'unexpected arguments' unless argv.empty?
    raise Error, 'interval, poll and max-age must be positive' unless [:interval, :poll, :max_age].all? { |key| options[key].finite? && options[key] > 0 }
    if options[:api_url]
      raise Error, 'explicit API address requires a local secret file (empty for an unprotected fixture)' unless options[:secret_file]
      secret = File.read(options[:secret_file]).chomp
      base = options[:api_url]
    else
      port = uci('cn_port', required: true)
      raise Error, 'invalid OpenClash API port' unless port.match?(/\A[0-9]+\z/) && port.to_i.between?(1, 65_535)
      base, secret = "http://127.0.0.1:#{port}", uci('dashboard_password')
    end
    api = API.new(base, secret)
    if options[:preflight]
      group, provider = api.group, api.provider
      compatible = begin
        Controller.new(api, url: options[:url], max_age: options[:max_age]).validate(group, provider)
        true
      rescue Error
        false
      end
      version = api.request('GET', '/version')
      puts JSON.generate(rubyVersion: RUBY_VERSION, coreVersion: version['version'], apiReachable: true,
                         candidateCompatible: compatible, selection: group['now'], readOnly: true,
                         providerHasPerURLState: provider.fetch('proxies', []).all? { |p| p['extra'].is_a?(Hash) })
      return 0
    end
    lock = nil
    if options[:lock_file]
      lock = File.open(options[:lock_file], File::RDWR | File::CREAT, 0o600)
      raise Error, 'another strict controller is running' unless lock.flock(File::LOCK_EX | File::LOCK_NB)
    end
    controller = Controller.new(api, url: options[:url], max_age: options[:max_age],
                                state_file: options[:state_file], dry_run: options[:dry_run])
    stop = false
    ['TERM', 'INT'].each { |signal| Signal.trap(signal) { stop = true } }
    next_probe = 0
    loop do
      begin
        now = Process.clock_gettime(Process::CLOCK_MONOTONIC)
        probe = now >= next_probe
        next_probe = now + options[:interval] if probe
        controller.step(probe: probe)
      rescue Error
        return 1 if options[:once]
      end
      break if options[:once] || stop
      deadline = Process.clock_gettime(Process::CLOCK_MONOTONIC) + options[:poll]
      sleep 0.1 while !stop && Process.clock_gettime(Process::CLOCK_MONOTONIC) < deadline
    end
    0
  rescue Error, OptionParser::ParseError, IOError, SystemCallError => e
    warn "strict controller: #{e.message}"
    1
  ensure
    controller.reject if controller && !options[:once]
    lock.close if lock
  end
end

exit LiangxinyunStrict.main(ARGV) if $PROGRAM_NAME == __FILE__
