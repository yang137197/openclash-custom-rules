-- Lua 5.1 strict selector controller; default mode is read-only preflight.
local M = {}
M.GROUP = "良心云"
M.PROVIDER = "liangxinyun"
M.TEST_URL = "https://www.gstatic.com/generate_204"
M.TIERS = {"日本专线", "日本高速", "美国流媒体", "美国高速"}
M.GROUP_PATH = "/proxies/%E8%89%AF%E5%BF%83%E4%BA%91"
M.PROVIDER_PATH = "/providers/proxies/liangxinyun"

local function finite(n)
  return type(n) == "number" and n == n and n > -math.huge and n < math.huge
end

local function has(s, part)
  return s:find(part, 1, true) ~= nil
end

function M.tier(name)
  if type(name) ~= "string" or name:sub(1, 5) ~= "LXY: " then return nil end
  if has(name, "日本专线") then return 1 end
  if has(name, "日本高速") then return 2 end
  if has(name, "美国") and has(name, "流媒体") then return 3 end
  if has(name, "美国高速") then return 4 end
end

-- Parse Go/RFC3339 timestamps in UTC, independently of the router's timezone.
function M.timestamp(text)
  if type(text) ~= "string" or #text > 40 then return nil end
  local y, m, d, h, minute, second, tail = text:match(
    "^(%d%d%d%d)%-(%d%d)%-(%d%d)T(%d%d):(%d%d):(%d%d)(.*)$")
  if not y then return nil end
  y, m, d, h, minute, second = tonumber(y), tonumber(m), tonumber(d),
    tonumber(h), tonumber(minute), tonumber(second)
  if y < 1970 or m < 1 or m > 12 or h > 23 or minute > 59 or second > 59 then return nil end
  local leap = y % 400 == 0 or (y % 4 == 0 and y % 100 ~= 0)
  local days = {31, leap and 29 or 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31}
  if d < 1 or d > days[m] then return nil end
  local fraction = 0
  if tail:sub(1, 1) == "." then
    local digits, zone = tail:match("^%.(%d+)(.*)$")
    if not digits or #digits > 9 then return nil end
    fraction, tail = tonumber("0." .. digits), zone
  end
  local offset = 0
  if tail ~= "Z" then
    local sign, zh, zm = tail:match("^([+-])(%d%d):(%d%d)$")
    if not sign or tonumber(zh) > 23 or tonumber(zm) > 59 then return nil end
    offset = (tonumber(zh) * 60 + tonumber(zm)) * 60 * (sign == "+" and 1 or -1)
  end
  local year = y - (m <= 2 and 1 or 0)
  local era = math.floor(year / 400)
  local yoe = year - era * 400
  local month = m + (m > 2 and -3 or 9)
  local doy = math.floor((153 * month + 2) / 5) + d - 1
  local doe = yoe * 365 + math.floor(yoe / 4) - math.floor(yoe / 100) + doy
  return (era * 146097 + doe - 719468) * 86400 + h * 3600 + minute * 60
    + second + fraction - offset
end

function M.measurement(proxy, url, now, max_age)
  local state = type(proxy.extra) == "table" and proxy.extra[url] or nil
  if type(state) ~= "table" then return "unknown", nil, "test-url-record-missing" end
  local history = state.history
  local last = type(history) == "table" and history[#history] or nil
  if type(last) ~= "table" then return "unknown", nil, "history-missing" end
  local stamp = M.timestamp(last.time)
  if not stamp then return "unknown", nil, "timestamp-invalid" end
  if now - stamp > max_age then return "unknown", nil, "history-stale" end
  if stamp - now > 5 then return "unknown", nil, "timestamp-in-future" end
  local delay = last.delay
  if state.alive == false and delay == 0 then return "failed" end
  if state.alive == true and finite(delay) and delay % 1 == 0 and delay >= 1 and delay <= 65534 then
    return "healthy", delay
  end
  return "unknown", nil, "state-and-delay-inconsistent"
end

function M.decide(proxies, members, options)
  local counts, buckets, ignored = {}, {}, 0
  for i, label in ipairs(M.TIERS) do
    counts[i] = {tier = label, total = 0, healthy = 0, failed = 0, unknown = 0, unknownReasons = {}}
    buckets[i] = {}
  end
  for _, proxy in ipairs(proxies) do
    local rank = M.tier(proxy.name)
    if rank and members[proxy.name] then
      local status, delay, reason = M.measurement(proxy, options.url, options.now, options.max_age)
      local row = counts[rank]
      row.total, row[status] = row.total + 1, row[status] + 1
      if status == "healthy" then
        buckets[rank][#buckets[rank] + 1] = {name = proxy.name, delay = delay}
      elseif status == "unknown" then
        row.unknownReasons[reason] = (row.unknownReasons[reason] or 0) + 1
      end
    else
      ignored = ignored + 1
    end
  end
  local decision = {wouldSelect = "REJECT", reason = "all-tiers-failed-or-empty"}
  for rank, row in ipairs(counts) do
    if #buckets[rank] > 0 then
      table.sort(buckets[rank], function(a, b)
        if a.delay ~= b.delay then return a.delay < b.delay end
        if (a.name == options.current) ~= (b.name == options.current) then
          return a.name == options.current
        end
        return a.name < b.name
      end)
      local best = buckets[rank][1]
      decision = {wouldSelect = best.name, tier = row.tier, delayMs = best.delay,
        reason = "lowest-delay-in-highest-healthy-tier"}
      break
    elseif row.unknown > 0 then
      decision = {wouldSelect = "REJECT", tier = row.tier, reason = "higher-tier-measurements-unknown"}
      break
    end
  end
  decision.tiers, decision.ignoredProviderNodes = counts, ignored
  return decision
end

local function names(array, objects)
  if type(array) ~= "table" then error("snapshot-invalid-members", 0) end
  local out, count = {}, 0
  for index, item in pairs(array) do
    if type(index) ~= "number" or index % 1 ~= 0 or index < 1 or index > #array then
      error("snapshot-invalid-members", 0)
    end
    local name = objects and type(item) == "table" and item.name or (not objects and item)
    if type(name) ~= "string" or name == "" or out[name] then error("snapshot-invalid-members", 0) end
    out[name], count = true, count + 1
  end
  if count ~= #array then error("snapshot-invalid-members", 0) end
  return out
end

local function same(a, b)
  for name in pairs(a) do if not b[name] then return false end end
  for name in pairs(b) do if not a[name] then return false end end
  return true
end

function M.snapshot_members(before, provider, after)
  if type(before) ~= "table" or type(after) ~= "table" or before.type ~= "Selector"
    or after.type ~= "Selector" or type(before.now) ~= "string" or before.now ~= after.now then
    error("snapshot-selection-changed-or-invalid", 0)
  end
  if type(provider) ~= "table" or provider.name ~= M.PROVIDER then error("snapshot-invalid-provider", 0) end
  local first, last, source = names(before.all), names(after.all), names(provider.proxies, true)
  if not same(first, last) then error("snapshot-members-changed", 0) end
  last.REJECT = nil
  if not same(last, source) then error("snapshot-provider-members-mismatch", 0) end
  if not first[before.now] then error("snapshot-current-selection-missing", 0) end
  return first
end

local function fail(code) error(code, 0) end
local function quote(s) return "'" .. s:gsub("'", "'\\''") .. "'" end
local function exists(path)
  local f = io.open(path, "r")
  if f then f:close(); return true end
  return false
end
local function wall(nixio)
  local s, us = nixio.gettimeofday()
  if not finite(s) or not finite(us) or us < 0 or us >= 1000000 then fail("clock-invalid") end
  return s + us / 1000000
end
local function monotonic()
  local f = io.open("/proc/uptime", "r")
  if not f then fail("monotonic-clock-unavailable") end
  local s = tonumber(f:read("*n")); f:close()
  if not finite(s) then fail("monotonic-clock-invalid") end
  return s
end

-- Fail closed on any incompatible candidate shape, including the old 45-node selector.
function M.validate(group, provider, after, url)
  local members = M.snapshot_members(group, provider, after)
  if group.all[1] ~= "REJECT" then fail("candidate-selector-required") end
  for name in pairs(members) do
    if name ~= "REJECT" and not M.tier(name) then fail("candidate-selector-required") end
  end
  if provider.testUrl ~= url or provider.expectedStatus ~= "204" then fail("provider-health-contract-mismatch") end
  for _, node in ipairs(provider.proxies) do
    if not M.tier(node.name) then fail("provider-node-outside-allowed-tiers") end
    if node["provider-name"] and node["provider-name"] ~= M.PROVIDER then fail("provider-source-mismatch") end
  end
  return members
end

function M.api(json, base, secret_file)
  -- Local HTTP only, no userinfo, path, redirect, proxy environment or curlrc.
  local host, port = base:match("^http://(127%.0%.0%.1):(%d+)$")
  if not host or tonumber(port) < 1 or tonumber(port) > 65535 then fail("api-address-invalid") end
  local auth = secret_file and (
    "local f=io.open(" .. string.format("%q", secret_file) .. ",'r'); if not f then os.exit(1) end; " ..
    "local s=f:read('*a'); f:close(); s=s:gsub('[\\r\\n]+$',''); ") or (
    "local u=require('luci.model.uci').cursor(); local s=u:get('openclash','config','dashboard_password') or ''; ")
  auth = auth .. [[
if type(s) ~= 'string' or s:find('[%c]') then os.exit(1) end
s=s:gsub('\\','\\\\'):gsub('"','\\"')
if #s>0 then io.write('header = "Authorization: Bearer '..s..'"\n') end
]]
  local allowed = {["/version"] = true, [M.GROUP_PATH] = true, [M.PROVIDER_PATH] = true,
    [M.PROVIDER_PATH .. "/healthcheck"] = true}
  return function(method, path, body)
    if not allowed[path] or (method ~= "GET" and not (method == "PUT" and path == M.GROUP_PATH))
      or (method == "GET" and body ~= nil) then fail("api-operation-refused") end
    if method == "PUT" and (type(body) ~= "table" or
      (body.name ~= "REJECT" and not M.tier(body.name))) then fail("api-selection-refused") end
    local payload = body and ('data-binary = "' .. json.stringify(body):gsub("\\", "\\\\"):gsub('"', '\\"') .. '"\n') or ""
    local producer = auth .. "\nio.write(" .. string.format("%q", payload) .. ")"
    local command = "lua -e " .. quote(producer) .. " | curl -q --config - --silent --fail"
      .. " --max-redirs 0 --proxy '' --noproxy '*' --proto '=http' --connect-timeout 2"
      .. " --max-time 30 --max-filesize 2097152 --header 'Content-Type: application/json'"
      .. " --write-out '\\n%{http_code}\\n' --request " .. method .. " --url " .. quote(base .. path) .. " 2>/dev/null"
    local pipe = io.popen(command, "r")
    if not pipe then fail("api-process-failed") end
    local output = pipe:read("*a"); pipe:close()
    local data, status = output:match("^(.*)\n(%d%d%d)\n$")
    if status ~= "200" and status ~= "204" then fail("api-http-failed") end
    if method == "PUT" or path == M.PROVIDER_PATH .. "/healthcheck" then return true end
    local ok, value = pcall(json.parse, data)
    if not ok or type(value) ~= "table" then fail("api-json-invalid") end
    return value
  end
end

function M.controller(request, options)
  local self = {managed = false}
  function self:snapshot()
    local before = request("GET", M.GROUP_PATH)
    local provider = request("GET", M.PROVIDER_PATH)
    local after = request("GET", M.GROUP_PATH)
    return after, provider, M.validate(before, provider, after, options.url)
  end
  function self:select(name, guard)
    local group, provider, members = self:snapshot()
    if not members[name] then fail("selection-target-disappeared") end
    if guard and (group.now ~= guard.current or provider.updatedAt ~= guard.updatedAt
      or not same(members, guard.members)) then fail("snapshot-changed-before-selection") end
    if guard and name ~= "REJECT" then
      local latest = M.decide(provider.proxies, members,
        {url=options.url, max_age=options.max_age, now=options.now(), current=group.now})
      if latest.wouldSelect ~= name then fail("measurements-changed-before-selection") end
    end
    if group.now ~= name then request("PUT", M.GROUP_PATH, {name = name}) end
    local verified = self:snapshot()
    if verified.now ~= name then fail("selection-readback-mismatch") end
  end
  function self:reject()
    if not self.managed or options.dry then return false end
    return pcall(function() self:select("REJECT") end)
  end
  function self:step(probe)
    local group, provider, members = self:snapshot()
    if not self.managed and not options.dry then
      self:select("REJECT")
      self.managed = true
      group, provider, members = self:snapshot()
    end
    if probe and not options.dry then
      -- A core reload/new subscription can remove history while restoring an old
      -- selection. Apply the current safe decision before waiting for a probe.
      local prior = M.decide(provider.proxies, members,
        {url=options.url, max_age=options.max_age, now=options.now(), current=group.now})
      self:select(prior.wouldSelect, {current=group.now, updatedAt=provider.updatedAt, members=members})
      request("GET", M.PROVIDER_PATH .. "/healthcheck")
      group, provider, members = self:snapshot()
    end
    local decision = M.decide(provider.proxies, members,
      {url = options.url, max_age = options.max_age, now = options.now(), current = group.now})
    if not options.dry then
      -- Resample immediately before mutation; membership/selection changes abort this cycle.
      local again, latest, observed = self:snapshot()
      if again.now ~= group.now or not same(observed, members)
        or latest.updatedAt ~= provider.updatedAt then fail("snapshot-changed-before-selection") end
      decision = M.decide(latest.proxies, observed,
        {url = options.url, max_age = options.max_age, now = options.now(), current = again.now})
      self:select(decision.wouldSelect, {current=again.now, updatedAt=latest.updatedAt, members=observed})
    end
    decision.selectionApplied = not options.dry
    decision.verifiedSelection = not options.dry
    decision.readOnly = options.dry == true
    return decision
  end
  return self
end

local function arguments(args)
  local o = {mode = "preflight", interval = 60, poll = 2, max_age = 130, url = M.TEST_URL,
    lock_file = "/var/run/liangxinyun-controller.lock"}
  local modes, values = 0, {['--interval']='interval', ['--poll']='poll', ['--max-age']='max_age',
    ['--test-url']='url', ['--api-url']='base', ['--secret-file']='secret_file',
    ['--lock-file']='lock_file', ['--state-file']='state_file', ['--stop-file']='stop_file'}
  local i = 1
  while args[i] do
    local flag = args[i]
    if flag == "--preflight" or flag == "--run" or flag == "--once" or flag == "--dry-run" then
      modes, o.mode, i = modes + 1, flag:sub(3), i + 1
    elseif values[flag] and args[i + 1] then o[values[flag]], i = args[i + 1], i + 2
    else fail("arguments-invalid") end
  end
  if modes > 1 then fail("arguments-conflicting-modes") end
  for _, key in ipairs({'interval', 'poll', 'max_age'}) do
    o[key] = tonumber(o[key])
    if not finite(o[key]) or o[key] <= 0 then fail("arguments-invalid-timing") end
  end
  if o.interval <= o.poll or o.max_age <= o.interval then fail("arguments-invalid-timing") end
  if o.base and not o.secret_file then fail("arguments-secret-file-required") end
  if type(o.url) ~= "string" or #o.url > 2048 or not o.url:match("^https?://") or o.url:find("[%c]") then
    fail("arguments-invalid-url")
  end
  if o.mode == "run" and not o.stop_file then fail("arguments-supervisor-required") end
  return o
end

local function safe_error(message)
  -- Never publish raw exceptions (may include API payloads, paths or credentials).
  if type(message) == "string" and message:match("^[a-z]+[a-z%-]+$") then return message end
  return "controller-error"
end

function M.main(args)
  local lock, controller, json, options
  local ok, result = pcall(function()
    json = require "luci.jsonc"
    options = arguments(args)
    local codec = json.parse([[{"extra":{"https:\/\/www.gstatic.com\/generate_204":{"alive":true,"history":[{"delay":7}]}}}]])
    local sample = type(codec)=="table" and type(codec.extra)=="table" and codec.extra[M.TEST_URL]
    if type(sample)~="table" or sample.alive~=true or type(sample.history)~="table"
      or #sample.history~=1 or type(sample.history[1])~="table" or sample.history[1].delay~=7 then
      fail("json-codec-incompatible")
    end
    local nixio = require "nixio"
    if type(nixio.open) ~= "function" or type(nixio.open_flags) ~= "function"
      or type(nixio.nanosleep) ~= "function" or type(nixio.getpid) ~= "function" then fail("native-runtime-incomplete") end
    if not options.base then
      local uci = require("luci.model.uci").cursor()
      local port = tostring(uci:get("openclash", "config", "cn_port") or "")
      if not port:match("^%d+$") then fail("api-port-invalid") end
      options.base = "http://127.0.0.1:" .. port
    end
    local request = M.api(json, options.base, options.secret_file)
    options.now = function() return wall(nixio) end
    options.dry = options.mode == "dry-run"
    controller = M.controller(request, options)
    if options.mode == "preflight" then
      local version = request("GET", "/version")
      local group = request("GET", M.GROUP_PATH)
      local provider = request("GET", M.PROVIDER_PATH)
      local after = request("GET", M.GROUP_PATH)
      local compatible = pcall(M.validate, group, provider, after, options.url)
      options.now(); monotonic()
      print(json.stringify({mode="preflight", readOnly=true, selectionApplied=false,
        candidateCompatible=compatible, coreVersion=version.version, luaVersion=_VERSION,
        currentSelection=after.now, formalAcceptance=false, nativeLockTested=false}))
      return 0
    end
    if not options.dry then
      if options.stop_file and exists(options.stop_file) then fail("stop-already-requested") end
      lock = nixio.open(options.lock_file, nixio.open_flags("creat", "rdwr"), "rw-------")
      if not lock or not lock:lock("tlock") then fail("another-controller-or-lock-unavailable") end
    end
    local counter, last, next_probe = 0, nil, 0
    local function publish(event)
      event.group, event.formalAcceptance = M.GROUP, false
      event.at = os.date("!%Y-%m-%dT%H:%M:%SZ")
      local encoded = json.stringify(event) .. "\n"
      if options.state_file and not options.dry then
        counter = counter + 1
        local temporary = options.state_file .. "." .. nixio.getpid() .. "." .. counter .. ".tmp"
        local f = nixio.open(temporary, nixio.open_flags("creat", "excl", "wronly"), "rw-------")
        if not f then fail("state-file-open-failed") end
        local offset = 0
        while offset < #encoded do
          local n = f:write(encoded:sub(offset + 1))
          if not n or n <= 0 then f:close(); os.remove(temporary); fail("state-file-write-failed") end
          offset = offset + n
        end
        f:close()
        if not os.rename(temporary, options.state_file) then os.remove(temporary); fail("state-file-rename-failed") end
      end
      local fingerprint = tostring(event.wouldSelect) .. ":" .. tostring(event.reason) .. ":" .. tostring(event.delayMs)
        .. ":" .. tostring(event.verifiedSelection)
      if fingerprint ~= last then io.write(encoded); io.flush(); last = fingerprint end
    end
    repeat
      local cycle_ok, event = pcall(function()
        local now = monotonic()
        local probe = now >= next_probe
        if probe then next_probe = now + options.interval end
        return controller:step(probe)
      end)
      if not cycle_ok then
        local rejected = controller:reject()
        event = {wouldSelect="REJECT", reason=safe_error(event), verifiedSelection=rejected,
          selectionApplied=rejected, readOnly=options.dry}
      end
      publish(event)
      if options.mode ~= "run" then return cycle_ok and 0 or 1 end
      local deadline = monotonic() + options.poll
      repeat
        if exists(options.stop_file) then
          local rejected = controller:reject()
          publish({wouldSelect="REJECT", reason="supervisor-stop", verifiedSelection=rejected,
            selectionApplied=rejected})
          if rejected or not controller.managed then return 0 end
          return 1
        end
        nixio.nanosleep(0, 100000000)
      until monotonic() >= deadline
    until false
  end)
  if not ok and controller then controller:reject() end
  if lock then lock:close() end
  if not ok then
    local event = {error=safe_error(result), selectionApplied=false, formalAcceptance=false}
    if json then print(json.stringify(event)) else print('controller-runtime-unavailable') end
    return 1
  end
  return type(result) == "number" and result or (result == true and 0 or 1)
end

if (...) == "__library_only" then return M end
os.exit(M.main(arg or {}))
