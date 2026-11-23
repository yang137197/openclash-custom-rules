-- Explicitly authorized diagnostic: one named node, one URLTest call, no retries.
-- No selection/configuration writes, service installation or file writes.
local NODE = "LXY: 🇯🇵日本专线01|BGP|流媒体"
local URL = "https://www.gstatic.com/generate_204"
local GROUP = "/proxies/%E8%89%AF%E5%BF%83%E4%BA%91"
local PROVIDER = "/providers/proxies/liangxinyun"
local function encode(s)
  return (s:gsub("([^A-Za-z0-9%-%._~])", function(c) return string.format("%%%02X", c:byte()) end))
end
local PROBE = PROVIDER .. "/" .. encode(NODE) .. "/healthcheck?url=" .. encode(URL)
  .. "&timeout=5000&expected=204"
local function quote(s) return "'" .. s:gsub("'", "'\\''") .. "'" end
local AUTH = [[
local u = require("luci.model.uci").cursor()
local s = u:get("openclash", "config", "dashboard_password") or ""
if type(s) ~= "string" or s:find("[%c]") then os.exit(1) end
s = s:gsub("\\", "\\\\"):gsub('"', '\\"')
if #s > 0 then io.write('header = "Authorization: Bearer '..s..'"\n') end
]]
local report = {mode = "single-node-probe", selectionApplied = false, formalAcceptance = false,
  probeRequestAttempted = false, probeRequests = 0, node = NODE, testUrl = URL, timeoutMs = 5000,
  expectedStatus = 204}
local available, json = pcall(require, "luci.jsonc")
if not available then print("lua-json-module-unavailable"); os.exit(1) end
local ok, failure = pcall(function()
  if not arg or (arg[1] ~= "--probe-once" and arg[1] ~= "--inspect-only") or arg[2] ~= nil then
    error("arguments-invalid", 0)
  end
  local inspect_only = arg[1] == "--inspect-only"
  if inspect_only then report.mode, report.readOnly = "selection-inspection", true end
  local sample = json.parse([[{"extra":{"https:\/\/www.gstatic.com\/generate_204":{"alive":true,"history":[{"delay":7}]}}}]])
  local state = type(sample) == "table" and type(sample.extra) == "table" and sample.extra[URL] or nil
  if type(state) ~= "table" or state.alive ~= true or type(state.history) ~= "table"
    or #state.history ~= 1 or type(state.history[1]) ~= "table" or state.history[1].delay ~= 7 then
    error("json-shape-incompatible", 0)
  end
  local port = require("luci.model.uci").cursor():get("openclash", "config", "cn_port") or ""
  if type(port) ~= "string" or not port:match("^%d+$") or not tonumber(port)
    or tonumber(port) < 1 or tonumber(port) > 65535 then error("api-port-invalid", 0) end
  local function request(path)
    if path ~= "/version" and path ~= GROUP and path ~= PROVIDER and path ~= PROBE then
      error("api-path-refused", 0)
    end
    if path == PROBE then
      if report.probeRequestAttempted then error("repeat-probe-refused", 0) end
      report.probeRequestAttempted, report.probeRequests = true, 1
    end
    local command = "lua -e " .. quote(AUTH)
      .. " | curl -q --config - --silent --max-redirs 0 --retry 0"
      .. " --proxy '' --noproxy '*' --proto '=http' --connect-timeout 2 --max-time 8"
      .. " --max-filesize 2097152 --request GET --write-out '\\n%{http_code}\\n' --url "
      .. quote("http://127.0.0.1:" .. port .. path) .. " 2>/dev/null"
    local pipe = io.popen(command, "r")
    if not pipe then error("api-process-failed", 0) end
    local output = pipe:read("*a"); pipe:close()
    local body, status = output:match("^(.*)\n(%d%d%d)\n$")
    local parsed, value = pcall(json.parse, body or "")
    if not parsed or type(value) ~= "table" then value = nil end
    return tonumber(status) or 0, value
  end
  local function read(path)
    local status, value = request(path)
    if status ~= 200 then error("api-http-" .. status, 0) end
    if not value then error("api-json-invalid", 0) end
    return value
  end
  local function members(group)
    if type(group) ~= "table" or group.type ~= "Selector" or type(group.all) ~= "table"
      or type(group.now) ~= "string" then error("group-shape-invalid", 0) end
    local names = {}
    for _, name in ipairs(group.all) do
      if type(name) ~= "string" or names[name] then error("group-members-invalid", 0) end
      names[name] = true
    end
    return names
  end
  local function same(a, b)
    for name in pairs(a) do if not b[name] then return false end end
    for name in pairs(b) do if not a[name] then return false end end
    return true
  end
  local function target(provider)
    if provider.name ~= "liangxinyun" or type(provider.proxies) ~= "table" then
      error("provider-shape-invalid", 0)
    end
    local found
    for _, node in ipairs(provider.proxies) do
      if type(node) == "table" and node.name == NODE then
        if found then error("duplicate-target-node", 0) end
        found = node
      end
    end
    return found
  end
  local function history(node)
    local extra = node and type(node.extra) == "table" and node.extra[URL] or nil
    if extra == nil then return nil, {}, false end
    if type(extra) ~= "table" or type(extra.history) ~= "table" then
      error("test-history-shape-invalid", 0)
    end
    return extra, extra.history, true
  end
  local version = read("/version")
  if version.version ~= "alpha-gbc76c13" then error("core-version-changed", 0) end
  report.coreVersion = version.version
  local before = read(GROUP)
  local before_members = members(before)
  report.currentSelection = before.now
  report.authorizedNodeSelected = before.now == NODE
  report.authorizedNodeInGroup = before_members[NODE] == true
  local function hex(s)
    return (s:gsub(".", function(c) return string.format("%02x", c:byte()) end))
  end
  report.currentSelectionUtf8Hex, report.authorizedNodeUtf8Hex = hex(before.now), hex(NODE)
  if inspect_only then report.inspectionComplete = true; return end
  -- Provider-scoped URLTest addresses NODE directly; the manual choice stays as-is.
  if not before_members[NODE] then error("authorized-node-not-in-group", 0) end
  local provider_before = read(PROVIDER)
  local node_before = target(provider_before)
  if not node_before then error("target-not-in-provider", 0) end
  local _, old_history, existing_bucket = history(node_before)
  if #old_history > 0 then error("existing-test-history-no-repeat", 0) end
  if existing_bucket then error("existing-test-state-no-repeat", 0) end
  local ready = read(GROUP)
  if ready.now ~= before.now or not same(before_members, members(ready)) then
    error("selection-or-members-changed-before-probe", 0)
  end
  -- Exactly one active API call. Even errors proceed only to ordinary readback.
  local status, response = request(PROBE)
  report.probeHttpStatus = status
  report.probeJsonParsed = response ~= nil
  if response and type(response.delay) == "number" and response.delay >= 0 and response.delay <= 65535 then
    report.apiDelayMs = response.delay
  end
  local provider_after = read(PROVIDER)
  local node_after = target(provider_after)
  local after = read(GROUP)
  report.currentSelectionUnchanged = after.now == before.now
  report.groupMembersUnchanged = same(before_members, members(after))
  report.providerTimestampComparable = type(provider_before.updatedAt) == "string"
    and type(provider_after.updatedAt) == "string"
  report.providerUpdatedAtUnchanged = report.providerTimestampComparable
    and provider_before.updatedAt == provider_after.updatedAt
  report.targetPresentAfter = node_after ~= nil
  local url_state, new_history = history(node_after)
  local last = new_history[#new_history]
  report.urlHistoryCount = #new_history
  report.recordAppearedAfterProbe = type(last) == "table" and type(last.time) == "string" and last.time ~= ""
  if url_state and type(url_state.alive) == "boolean" then report.urlAlive = url_state.alive end
  local delay = type(last) == "table" and last.delay or nil
  if type(delay) == "number" and delay >= 0 and delay <= 65535 then report.urlDelayMs = delay end
  report.result = "unknown"
  if report.currentSelectionUnchanged and report.groupMembersUnchanged and report.providerUpdatedAtUnchanged
    and report.recordAppearedAfterProbe and response and (status == 200 or status == 503 or status == 504) then
    if url_state.alive == true and type(delay) == "number" and delay % 1 == 0
      and delay >= 1 and delay <= 65534 and status == 200 and response.delay == delay then
      report.result = "healthy-for-requested-204"
    elseif url_state.alive == false and delay == 0 then
      report.result = "failed-for-requested-204"
    end
  end
end)
if not ok then
  local code = type(failure) == "string" and failure or "script-error"
  if not code:match("^[a-z][a-z0-9%-]+$") then code = "script-error" end
  report.error = code
end
print(json.stringify(report))
os.exit(ok and 0 or 1)
