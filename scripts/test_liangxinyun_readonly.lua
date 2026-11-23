-- Pure-policy checks run with a real Lua 5.1 interpreter; no router or network.
local M = assert(loadfile(assert(arg[1], "module path required")))("__library_only")
local checks = 0
local function eq(actual, expected, label)
  checks = checks + 1
  assert(actual == expected, (label or "check") .. ": expected " .. tostring(expected) .. ", got " .. tostring(actual))
end
local function rejected(fn, label)
  local ok = pcall(fn)
  eq(ok, false, label)
end
local function copy(value)
  if type(value) ~= "table" then return value end
  local out = {}
  for key, item in pairs(value) do out[key] = copy(item) end
  return out
end

eq(M.timestamp("1970-01-01T00:00:00Z"), 0, "epoch")
eq(M.timestamp("2026-11-23T12:34:56Z"), 1795437296, "UTC")
eq(M.timestamp("2026-11-23T20:34:56.125+08:00"), 1795437296.125, "fraction and east offset")
eq(M.timestamp("2026-11-23T04:34:56-08:00"), 1795437296, "west offset")
for _, stamp in ipairs({"2026-02-29T00:00:00Z", "2100-02-29T00:00:00Z", "2026-11-31T00:00:00Z",
  "2026-00-01T00:00:00Z", "2026-01-00T00:00:00Z", "2026-01-01T24:00:00Z", "2026-01-01T00:60:00Z",
  "2026-01-01T00:00:60Z", "2026-01-01T00:00:00", "2026-01-01T00:00:00+24:00", "bad",
  "2026-01-01T00:00:00.1234567890Z"}) do eq(M.timestamp(stamp), nil, "invalid timestamp") end
eq(type(M.timestamp("2000-02-29T00:00:00Z")), "number", "Gregorian leap year")

local url, stamp = M.TEST_URL, "2026-11-23T12:34:56Z"
local now = M.timestamp(stamp)
local function node(name, delay, alive)
  return {name = name, extra = {[url] = {alive = alive, history = {{time = stamp, delay = delay}}}}}
end
local labels = {"🇯🇵日本专线", "JP日本高速", "US美国", "🇺🇸美国高速"}
local nodes, members = {}, {}
for rank, label in ipairs(labels) do
  for index = 1, 2 do
    local name = "LXY: " .. label .. string.format("%02d", index) .. (rank == 3 and "|流媒体|0.1x" or "|BGP")
    nodes[#nodes + 1] = node(name, (5 - rank) * 20 + (3 - index), true)
    members[name] = true
    eq(M.tier(name), rank, "classification")
  end
end
eq(M.tier("LXY: 流媒体|美国05"), 3, "nonadjacent US media")
eq(M.tier("美国高速01"), nil, "prefix required")
eq(M.tier("LXY: 新加坡专线01"), nil, "other region excluded")
eq(M.tier("LXY: 日本普通01"), nil, "other category excluded")

-- Every two-node/four-tier availability mask, including full failure.
for mask = 0, 255 do
  local sample, expected = copy(nodes), "REJECT"
  for i, value in ipairs(sample) do
    local up = math.floor(mask / 2 ^ (i - 1)) % 2 == 1
    local state = value.extra[url]
    state.alive, state.history[1].delay = up, up and nodes[i].extra[url].history[1].delay or 0
  end
  for rank = 1, 4 do
    local a, b = sample[rank * 2 - 1], sample[rank * 2]
    if b.extra[url].alive then expected = b.name; break end
    if a.extra[url].alive then expected = a.name; break end
  end
  local result = M.decide(sample, members, {url = url, now = now, max_age = 130})
  eq(result.wouldSelect, expected, "availability mask " .. mask)
end

local function measured(sample, time)
  return M.measurement(sample, url, time or now, 130)
end
local changed = copy(nodes[1]); changed.extra = nil
eq(measured(changed), "unknown", "missing extra does not use global history")
changed.history = {{time = stamp, delay = 1}}
eq(measured(changed), "unknown", "global history never substitutes for URL history")
changed = copy(nodes[1]); changed.extra = {["https://other.test/204"] = changed.extra[url]}
eq(measured(changed), "unknown", "wrong test URL")
changed = copy(nodes[1]); changed.extra[url].history = {}
eq(measured(changed), "unknown", "empty history")
eq(measured(nodes[1], now + 130), "healthy", "maximum age inclusive")
eq(measured(nodes[1], now + 130.001), "unknown", "stale")
eq(measured(nodes[1], now - 5), "healthy", "future tolerance inclusive")
eq(measured(nodes[1], now - 5.001), "unknown", "future record")
for _, delay in ipairs({0, -1, 1.5, 65535, math.huge, "20"}) do
  changed = copy(nodes[1]); changed.extra[url].history[1].delay = delay
  eq(measured(changed), "unknown", "invalid healthy delay")
end
changed = copy(nodes[1]); changed.extra[url].alive = false
eq(measured(changed), "unknown", "failed flag with positive delay is inconsistent")
changed.extra[url].history[1].delay = 0
eq(measured(changed), "failed", "explicit failure")

local sample = copy(nodes)
sample[1].extra, sample[2].extra = {}, {}
eq(M.decide(sample, members, {url = url, now = now, max_age = 130}).wouldSelect, "REJECT", "unknown higher tier blocks downgrade")
sample[1] = copy(nodes[1])
eq(M.decide(sample, members, {url = url, now = now, max_age = 130}).wouldSelect, sample[1].name, "healthy peer keeps same tier")
sample = copy(nodes)
sample[1].extra[url].history[1].delay = sample[2].extra[url].history[1].delay
eq(M.decide(sample, members, {url = url, now = now, max_age = 130, current = sample[1].name}).wouldSelect,
  sample[1].name, "equal delay retains current")
local subset = copy(members); subset[nodes[1].name], subset[nodes[2].name] = nil, nil
eq(M.decide(nodes, subset, {url = url, now = now, max_age = 130}).wouldSelect, nodes[4].name, "empty tier skipped")
eq(M.decide({}, {}, {url = url, now = now, max_age = 130}).wouldSelect, "REJECT", "empty provider")

local group = {type = "Selector", now = nodes[1].name, all = {}}
for _, value in ipairs(nodes) do group.all[#group.all + 1] = value.name end
local provider = {name = M.PROVIDER, proxies = nodes, testUrl = ""}
eq(M.snapshot_members(group, provider, copy(group))[nodes[1].name], true, "legacy group and empty provider testUrl accepted for reading")
local after = copy(group); after.now = nodes[2].name
rejected(function() M.snapshot_members(group, provider, after) end, "selection race")
after = copy(group); table.remove(after.all)
rejected(function() M.snapshot_members(group, provider, after) end, "membership race")
local other = copy(provider); other.proxies[1].name = "LXY: other"
rejected(function() M.snapshot_members(group, other, group) end, "provider membership mismatch")
other = copy(provider); other.proxies[2].name = other.proxies[1].name
rejected(function() M.snapshot_members(group, other, group) end, "duplicate source name")
other = copy(provider); other.name = "ikuuu"
rejected(function() M.snapshot_members(group, other, group) end, "provider source")

local coverage = M.url_coverage({node(nodes[1].name, 10, true),
  {name = nodes[2].name, extra = {["https://private.test/?secret=fixture"] = {history = {{delay = 1}}}}}})
eq(#coverage, 2, "URL coverage")
eq(coverage[1].url, "<custom URL redacted>", "unlisted URL not disclosed")
local summary = M.history_diagnostics({
  {name = nodes[1].name, extra = {}, history = {{delay = 1}}},
  {name = nodes[2].name},
  {name = nodes[3].name, extra = {[url] = {history = {}}}},
  {name = nodes[4].name, extra = {[url] = {alive = true}}},
  {name = nodes[5].name, extra = {[url] = false}},
  node(nodes[6].name, 10, true),
  {name = nodes[7].name, extra = {other = {history = {{delay = 2}}}}},
  node("LXY: 新加坡专线01", 10, true)
})
eq(summary.eligibleNodes.nodes, 7, "eligible diagnostics scope")
eq(summary.allProvider.nodes, 8, "provider diagnostics scope")
eq(summary.eligibleNodes.nodesWithGlobalHistory, 1, "global history counted separately")
eq(summary.eligibleNodes.extraEmptyNodes, 1, "empty extra")
eq(summary.eligibleNodes.extraMissingOrNonTableNodes, 1, "missing extra")
eq(summary.eligibleNodes.emptyHistoryEntries, 1, "empty URL history")
eq(summary.eligibleNodes.missingOrNonTableHistoryEntries, 1, "missing URL history")
eq(summary.eligibleNodes.nonTableStateEntries, 1, "invalid state")
eq(summary.eligibleNodes.nonUrlExtraEntries, 1, "non URL key")
eq(summary.eligibleNodes.nodesWithAnyExtraHistory, 2, "extra histories include unknown keys")
eq(summary.eligibleNodes.urlStateEntries, 4, "URL key count")
eq(summary.allProvider.nodesWithAnyExtraHistory, 3, "excluded node histories counted separately")
eq(M.check_json({parse = function() return {extra = {[url] = {alive = true, history = {{delay = 7}}}}} end}),
  true, "codec shape accepted")
eq(M.check_json({parse = function() return {extra = {[url] = {alive = true, history = {[0] = {delay = 7}}}}} end}),
  false, "zero based codec shape refused")
eq(M.check_json({parse = function() return {} end}), false, "missing URL key refused")
local read = M.reader({}, 9090)
rejected(function() read("/providers/proxies/liangxinyun/healthcheck") end, "active health check refused")
rejected(function() read("/proxies/other") end, "other proxy refused")
for _, value in ipairs({"9090/path", "9090;echo fixture", "0", "65536", "http://example.test"}) do
  rejected(function() M.reader({}, value) end, "invalid port")
end
print("PASS Lua 5.1 policy assertions: " .. checks)
