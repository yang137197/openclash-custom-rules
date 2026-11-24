-- Standalone native lock diagnostic. No API, UCI, curl or controller invocation.
-- Default is inspection only. --test-once requires separate temporary-file authorization.
local M = {}
local function fail(code) error(code, 0) end

function M.inspect(nixio)
  for _, name in ipairs({'mkstemp', 'fork', 'wait', 'kill', 'nanosleep'}) do
    if type(nixio[name]) ~= 'function' then fail('native-lock-interface-missing') end
  end
  if type(nixio.const) ~= 'table' or type(nixio.const.EACCES) ~= 'number'
    or type(nixio.const.EAGAIN) ~= 'number' or type(nixio.const.SIGKILL) ~= 'number' then
    fail('native-lock-constants-missing')
  end
end

function M.child_check(file, expected_available, constants)
  -- nixio errors return false/nil, errno, message (errno is the second value).
  local acquired, errno = file:lock('tlock')
  if acquired then
    if not file:lock('ulock') then return false end
    return expected_available
  end
  return not expected_available and (errno == constants.EACCES or errno == constants.EAGAIN)
end

function M.test(nixio, exit_child)
  M.inspect(nixio)
  local file, closed
  local ok, reason = pcall(function()
    -- Upstream mkstemp creates /tmp/<template>.XXXXXX, immediately unlinks it,
    -- and returns its open descriptor. This cannot touch the controller's lock.
    file = nixio.mkstemp('liangxinyun-native-lock')
    if not file then fail('native-lock-tempfile-failed') end
    if not file:lock('tlock') then fail('native-lock-parent-acquire-failed') end
    local function child(expected_available)
      local pid = nixio.fork()
      if type(pid) ~= 'number' or pid < 0 or pid % 1 ~= 0 then fail('native-lock-fork-failed') end
      if pid == 0 then
        local success, matches = pcall(M.child_check, file, expected_available, nixio.const)
        pcall(function() file:close() end)
        return exit_child(success and matches and 0 or 1)
      end
      for _ = 1, 100 do
        local waited, status, code = nixio.wait(pid, 'nohang')
        if waited == pid then
          if status ~= 'exited' or code ~= 0 then fail('native-lock-child-check-failed') end
          return
        end
        if waited ~= false then fail('native-lock-wait-failed') end
        nixio.nanosleep(0, 50000000)
      end
      -- This PID is still our unreaped child; never signal an arbitrary PID.
      nixio.kill(pid, nixio.const.SIGKILL)
      nixio.wait(pid)
      fail('native-lock-child-timeout')
    end
    child(false)
    if not file:lock('ulock') then fail('native-lock-parent-release-failed') end
    child(true)
  end)
  if file then closed = file:close() == true end
  if not closed and file then fail('native-lock-close-failed') end
  if not ok then error(reason, 0) end
  return {parentLockAcquired=true, competingChildBlocked=true,
    childAcquiredAfterUnlock=true, descriptorClosed=true}
end

function M.main(args)
  local available, json = pcall(require, 'luci.jsonc')
  if not available then print('native-lock-json-unavailable'); return 1 end
  local testing = #args == 1 and args[1] == '--test-once'
  local ok, result = pcall(function()
    if not testing and not (#args == 0 or (#args == 1 and args[1] == '--inspect-only')) then
      fail('native-lock-arguments-invalid')
    end
    local nixio = require 'nixio'
    M.inspect(nixio)
    local data = testing and M.test(nixio, os.exit) or {}
    data.mode = testing and 'native-lock-test' or 'native-lock-inspection'
    data.readOnly, data.nativeLockTested = not testing, testing
    data.apiRequests, data.probeRequests, data.selectionApplied = 0, 0, false
    data.formalAcceptance = false
    return data
  end)
  if not ok then
    local code = type(result) == 'string' and result:match('^native%-lock%-[a-z%-]+$')
      and result or 'native-lock-error'
    result = {error=code, mode=testing and 'native-lock-test' or 'native-lock-inspection',
      readOnly=not testing, nativeLockTested=false, apiRequests=0, probeRequests=0,
      selectionApplied=false, formalAcceptance=false}
  end
  print(json.stringify(result))
  return ok and 0 or 1
end

if (...) == '__library_only' then return M end
os.exit(M.main(arg or {}))
