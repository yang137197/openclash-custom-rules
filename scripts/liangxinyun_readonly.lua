-- One-shot diagnostic. No probing, configuration writes or selection writes.
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

local PUBLIC_URLS = {
  [M.TEST_URL] = true,
  ["http://www.gstatic.com/generate_204"] = true,
  ["https://cp.cloudflare.com/generate_204"] = true,
  ["https://www.google.com/generate_204"] = true
}

function M.url_coverage(proxies)
  local covered, out = {}, {}
  for _, node in ipairs(proxies) do
    if M.tier(node.name) and type(node.extra) == "table" then
      for url, state in pairs(node.extra) do
        if type(state) == "table" and type(state.history) == "table" and #state.history > 0 then
          local label = PUBLIC_URLS[url] and url or "<custom URL redacted>"
          covered[label] = covered[label] or {}
          covered[label][node.name] = true
        end
      end
    end
  end
  for url, nodes in pairs(covered) do
    local count = 0
    for _ in pairs(nodes) do count = count + 1 end
    out[#out + 1] = {url = url, nodesWithHistory = count}
  end
  table.sort(out, function(a, b) return a.url < b.url end)
  return out
end

function M.quote(text)
  return "'" .. text:gsub("'", "'\\''") .. "'"
end

-- The child reads the existing credential itself. Its argv contains code, never the credential.
local AUTH = [[
local u = require("luci.model.uci").cursor()
local s = u:get("openclash", "config", "dashboard_password") or ""
if type(s) ~= "string" or s:find("[%c]") then os.exit(1) end
s = s:gsub("\\", "\\\\"):gsub('"', '\\"')
if #s > 0 then io.write('header = "Authorization: Bearer '..s..'"\n') end
]]

function M.reader(json, port)
  port = tostring(port or "")
  local n = tonumber(port)
  if not port:match("^%d+$") or not n or n < 1 or n > 65535 then error("api-port-invalid", 0) end
  local allowed = {["/version"] = true, [M.GROUP_PATH] = true, [M.PROVIDER_PATH] = true}
  return function(path)
    if not allowed[path] then error("api-path-refused", 0) end
    local command = "lua -e " .. M.quote(AUTH)
      .. " | curl -q --config - --silent --fail --max-redirs 0"
      .. " --proxy '' --noproxy '*' --proto '=http'"
      .. " --connect-timeout 2 --max-time 8 --max-filesize 2097152"
      .. " --write-out '\\n%{http_code}\\n' --request GET --url "
      .. M.quote("http://127.0.0.1:" .. port .. path) .. " 2>/dev/null"
    local pipe = io.popen(command, "r")
    if not pipe then error("api-process-failed", 0) end
    local output = pipe:read("*a")
    pipe:close()
    local body, status = output:match("^(.*)\n(%d%d%d)\n$")
    if status ~= "200" then error("api-http-" .. (status or "unknown"), 0) end
    local ok, value = pcall(json.parse, body)
    if not ok or type(value) ~= "table" then error("api-json-invalid", 0) end
    return value
  end
end

local function arguments(args)
  local options = {url = M.TEST_URL, max_age = 130}
  local index = 1
  while args[index] do
    local flag = args[index]
    if flag == "--help" then options.help = true; index = index + 1
    elseif (flag == "--test-url" or flag == "--max-age") and args[index + 1] then
      local value = args[index + 1]
      if flag == "--test-url" then options.url = value else options.max_age = tonumber(value) end
      index = index + 2
    else error("arguments-invalid", 0) end
  end
  if type(options.url) ~= "string" or #options.url > 2048 or not options.url:match("^https?://")
    or options.url:find("[%c]") or not finite(options.max_age) or options.max_age % 1 ~= 0
    or options.max_age < 1 or options.max_age > 3600 then error("arguments-invalid", 0) end
  return options
end

function M.main(args)
  local parsed, options = pcall(arguments, args)
  if not parsed then print("arguments-invalid"); return 2 end
  if options.help then
    print("Read-only, one-shot Liangxinyun simulation. No apply mode.\n--test-url URL (lookup key only)\n--max-age SECONDS (default 130)")
    return 0
  end
  local available, json = pcall(require, "luci.jsonc")
  if not available then print("lua-json-module-unavailable"); return 1 end
  local ok, result = pcall(function()
    local uci = require("luci.model.uci").cursor()
    local nixio = require "nixio"
    local read = M.reader(json, uci:get("openclash", "config", "cn_port"))
    local version = read("/version")
    if type(version.version) ~= "string" then error("api-version-invalid", 0) end
    local before = read(M.GROUP_PATH)
    local provider = read(M.PROVIDER_PATH)
    local after = read(M.GROUP_PATH)
    local members = M.snapshot_members(before, provider, after)
    local seconds, microseconds = nixio.gettimeofday()
    if not finite(seconds) or not finite(microseconds) or microseconds < 0 or microseconds >= 1000000 then
      error("clock-invalid", 0)
    end
    options.now, options.current = seconds + microseconds / 1000000, before.now
    local decision = M.decide(provider.proxies, members, options)
    local data = {
      mode = "read-only-simulation", readOnly = true, selectionApplied = false,
      coreVersion = version.version, currentSelection = before.now,
      providerNodes = #provider.proxies, groupMembers = #before.all,
      testUrl = PUBLIC_URLS[options.url] and options.url or "<custom URL redacted>",
      maxAgeSeconds = options.max_age, futureToleranceSeconds = 5,
      snapshotNamesAndSelectionConsistent = true,
      providerHealthContractMatches = provider.testUrl == options.url and provider.expectedStatus == "204",
      observedTestUrls = M.url_coverage(provider.proxies), recommendation = decision,
      formalAcceptance = false
    }
    if not data.providerHealthContractMatches then
      data.warning = "provider-test-url-or-expected-204-unconfirmed; recommendation-is-provisional"
    end
    return data
  end)
  if ok then print(json.stringify(result)); return 0 end
  local code = type(result) == "string" and result or "script-error"
  if not code:match("^api%-%w[%w%-]*$") and not code:match("^snapshot%-%w[%w%-]*$")
    and code ~= "clock-invalid" then code = "script-error" end
  print(json.stringify({mode = "read-only-simulation", readOnly = true, selectionApplied = false, error = code}))
  return 1
end

if (...) == "__library_only" then return M end
os.exit(M.main(arg or {}))
