-- Standalone /tmp state-file diagnostic. No API, UCI, curl, service or controller.
local M = {}
local function fail(code) error(code, 0) end
local function safe_error(value)
  return type(value)=='string' and value:match('^native%-state%-[a-z%-]+$') and value or 'native-state-error'
end

function M.inspect(nx)
  if type(nx.open)~='function' or type(nx.open_flags)~='function' or type(nx.fs)~='table'
    or type(nx.const)~='table' or type(nx.const.EEXIST)~='number' then fail('native-state-interface-missing') end
  for _,name in ipairs({'mkdir','stat','lstat','unlink','rmdir'}) do
    if type(nx.fs[name])~='function' then fail('native-state-interface-missing') end
  end
end

function M.test(nx,json,ops)
  M.inspect(nx)
  ops=ops or {open=io.open,rename=os.rename}
  local root,owned,handles=nil,false,{}
  local result={stateFileTestPassed=false,cleanupComplete=false}
  local function track(file)
    if not file then fail('native-state-open-failed') end
    local h={file=file,closed=false}; handles[#handles+1]=h; return h
  end
  local function close(h)
    if h.file:close()~=true then fail('native-state-close-failed') end
    h.closed=true
  end
  local function read(path)
    local h=track(ops.open(path,'r')); local data=h.file:read('*a'); close(h); return data
  end
  local function revision(data,expected)
    local value=json.parse(data)
    if type(value)~='table' or value.revision~=expected or value.sample~='离线状态测试'
      or value.selectionApplied~=false then fail('native-state-readback-mismatch') end
  end
  local function stat(path,kind,permission)
    local value=nx.fs.stat(path)
    if type(value)~='table' or value.type~=kind or value.modestr~=permission then
      fail('native-state-permission-mismatch')
    end
    return value
  end
  local ok,reason=pcall(function()
    local random=track(ops.open('/dev/urandom','rb'))
    local bytes=random.file:read(8); close(random)
    if type(bytes)~='string' or #bytes~=8 then fail('native-state-random-failed') end
    local hex=bytes:gsub('.',function(c) return string.format('%02x',c:byte()) end)
    root='/tmp/liangxinyun-state-'..hex
    -- An existing directory is never reused or cleaned. mkdir is exclusive.
    if not nx.fs.mkdir(root,'rwx------') then fail('native-state-directory-create-failed') end
    owned=true
    stat(root,'dir','rwx------'); result.privateDirectory=true
    local state,temporary=root..'/state.json',root..'/replacement.tmp'
    local function write(path,version)
      local data=json.stringify({sample='离线状态测试',revision=version,selectionApplied=false})..'\n'
      local h=track(nx.open(path,nx.open_flags('creat','excl','wronly'),'rw-------'))
      local offset=0
      while offset<#data do
        local n=h.file:write(data:sub(offset+1))
        if type(n)~='number' or n%1~=0 or n<=0 or n>#data-offset then fail('native-state-write-failed') end
        offset=offset+n
      end
      close(h); return stat(path,'reg','rw-------')
    end
    local first=write(state,1)
    revision(read(state),1); result.stateWriteReadback=true
    local duplicate,errno=nx.open(state,nx.open_flags('creat','excl','wronly'),'rw-------')
    if duplicate then close(track(duplicate)); fail('native-state-exclusive-create-failed') end
    if errno~=nx.const.EEXIST then fail('native-state-exclusive-create-failed') end
    result.exclusiveCreateRespected=true
    local second=write(temporary,2)
    revision(read(state),1); result.originalPreservedBeforeReplace=true
    local old=track(ops.open(state,'r'))
    if not ops.rename(temporary,state) then fail('native-state-rename-failed') end
    revision(read(state),2)
    revision(old.file:read('*a'),1); close(old)
    local current=stat(state,'reg','rw-------')
    if current.dev~=first.dev or current.dev~=second.dev or current.ino~=second.ino
      or current.ino==first.ino then fail('native-state-inode-mismatch') end
    result.replacementReadback=true
    result.oldOpenFilePreserved=true
    result.stateFileMode='rw-------'
    result.sameDirectoryRename=true
  end)
  local cleaned=true
  for _,h in ipairs(handles) do
    if not h.closed then
      local closed,value=pcall(function() return h.file:close() end)
      if not closed or value~=true then cleaned=false end
    end
  end
  if owned then
    -- Fixed basenames inside our newly created directory only; never recursive.
    for _,name in ipairs({'state.json','replacement.tmp'}) do
      local path=root..'/'..name
      if nx.fs.lstat(path) and not nx.fs.unlink(path) then cleaned=false end
    end
    if not nx.fs.rmdir(root) then cleaned=false end
    if nx.fs.lstat(root) then cleaned=false end
  end
  result.cleanupComplete=cleaned
  result.stateFileTestPassed=ok and cleaned
  if not ok then result.error=safe_error(reason)
  elseif not cleaned then result.error='native-state-cleanup-failed' end
  if not cleaned and owned then result.temporaryDirectory=root end
  return result
end

function M.main(args)
  local ready,json=pcall(require,'luci.jsonc')
  if not ready then print('native-state-json-unavailable'); return 1 end
  local testing=#args==1 and args[1]=='--test-once'
  local ok,result=pcall(function()
    if not testing and not (#args==0 or (#args==1 and args[1]=='--inspect-only')) then
      fail('native-state-arguments-invalid')
    end
    local nx=require 'nixio'; M.inspect(nx)
    return testing and M.test(nx,json) or {}
  end)
  if not ok then result={error=safe_error(result),stateFileTestPassed=false} end
  result.mode=testing and 'native-state-test' or 'native-state-inspection'
  result.readOnly=not testing
  result.apiRequests,result.probeRequests,result.selectionApplied=0,0,false
  result.formalAcceptance=false
  print(json.stringify(result))
  return ok and (not testing or result.stateFileTestPassed) and 0 or 1
end
if (...)=='__library_only' then return M end
os.exit(M.main(arg or {}))
