-- Read-only candidate contract inspection; GET allowlist only, no probe or apply mode.
local M = {}
M.GROUP = "良心云"
M.PROVIDER = "liangxinyun"
M.TEST_URL = "https://www.gstatic.com/generate_204"
M.TIERS = {"日本专线", "日本高速", "美国流媒体", "美国高速"}
M.GROUP_PATH = "/proxies/%E8%89%AF%E5%BF%83%E4%BA%91"
M.PROVIDER_PATH = "/providers/proxies/liangxinyun"

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

local function fail(code) error(code,0) end
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

function M.inspect(group, provider, after)
  local result={candidateVersion="1.8.1",checks={},blockingReasons={}}
  local checks=result.checks
  local function check(key,ok,reason)
    checks[key]=ok
    if not ok then result.blockingReasons[#result.blockingReasons+1]=reason end
  end
  local stable,members=pcall(M.snapshot_members,group,provider,after)
  check("snapshotConsistent",stable,"snapshot-invalid-or-changed")
  local compatible,first=pcall(M.validate,group,provider,after,M.TEST_URL)
  result.candidateCompatible=compatible
  if not compatible then
    local known={["snapshot-selection-changed-or-invalid"]=true,["snapshot-invalid-provider"]=true,
      ["snapshot-invalid-members"]=true,["snapshot-members-changed"]=true,
      ["snapshot-provider-members-mismatch"]=true,["snapshot-current-selection-missing"]=true,
      ["candidate-selector-required"]=true,["provider-health-contract-mismatch"]=true,
      ["provider-node-outside-allowed-tiers"]=true,["provider-source-mismatch"]=true}
    result.firstRejection=known[first] and first or "contract-check-failed"
  end
  result.inspectionComplete=stable
  if not stable then return result end
  check("rejectFirst",group.all[1]=="REJECT","selector-reject-not-first")
  local outsideGroup,outsideProvider,wrongSource=0,0,0
  local tiers={}
  for _,label in ipairs(M.TIERS) do tiers[#tiers+1]={tier=label,nodes=0} end
  for name in pairs(members) do
    if name~="REJECT" and not M.tier(name) then outsideGroup=outsideGroup+1 end
  end
  for _,node in ipairs(provider.proxies) do
    local rank=M.tier(node.name)
    if rank then tiers[rank].nodes=tiers[rank].nodes+1 else outsideProvider=outsideProvider+1 end
    if node["provider-name"] and node["provider-name"]~=M.PROVIDER then wrongSource=wrongSource+1 end
  end
  check("groupOnlyAllowedTiers",outsideGroup==0,"selector-has-outside-tier-nodes")
  check("providerOnlyAllowedTiers",outsideProvider==0,"provider-has-outside-tier-nodes")
  check("providerSourcesMatch",wrongSource==0,"provider-source-mismatch")
  check("testUrlMatches",provider.testUrl==M.TEST_URL,"provider-test-url-mismatch")
  check("expectedStatusMatches",provider.expectedStatus=="204","provider-expected-status-mismatch")
  result.groupMembers,result.providerNodes=#group.all,#provider.proxies
  result.outsideTierGroupNodes,result.outsideTierProviderNodes=outsideGroup,outsideProvider
  result.wrongSourceNodes,result.tiers=wrongSource,tiers
  result.expectedStatusType=type(provider.expectedStatus)
  result.selectionUnchanged=true -- snapshot_members verified this, not a claim about later traffic.
  result.contractChecksAgree=(#result.blockingReasons==0)==compatible
  if not result.contractChecksAgree then fail("diagnostic-contract-disagreement") end
  return result
end

function M.main(args)
  local available,json=pcall(require,"luci.jsonc")
  if not available then print("candidate-readonly-json-unavailable"); return 1 end
  local attempts=0
  local ok,result=pcall(function()
    if #args~=0 then fail("arguments-invalid") end
    local uci=require("luci.model.uci").cursor()
    local get=M.reader(json,uci:get("openclash","config","cn_port"))
    local function read(path) attempts=attempts+1; return get(path) end
    local version=read("/version")
    if type(version.version)~="string" or #version.version>100
      or not version.version:match("^[%w%._%+%-]+$") then fail("api-version-invalid") end
    local before=read(M.GROUP_PATH)
    local provider=read(M.PROVIDER_PATH)
    local after=read(M.GROUP_PATH)
    local out=M.inspect(before,provider,after)
    out.coreVersion=version.version
    return out
  end)
  if not ok then
    local known={["arguments-invalid"]=true,["api-port-invalid"]=true,["api-process-failed"]=true,
      ["api-json-invalid"]=true,["api-version-invalid"]=true,["diagnostic-contract-disagreement"]=true}
    local code=type(result)=="string" and
      (known[result] or result:match("^api%-http%-%d%d%d$") or result=="api-http-unknown")
    result={error=code and result or "candidate-readonly-failed",inspectionComplete=false}
  end
  result.mode="candidate-config-readonly"
  result.readOnly,result.selectionApplied,result.configurationWritten,result.formalAcceptance=true,false,false,false
  result.apiRequests,result.probeRequests=attempts,0
  print(json.stringify(result))
  return ok and result.inspectionComplete and 0 or 1
end
if (...)=="__library_only" then return M end
os.exit(M.main(arg or {}))
