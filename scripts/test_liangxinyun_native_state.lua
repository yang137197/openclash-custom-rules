-- Actual Lua, in-memory filesystem; actual filesystem smoke is a separate check.
local M=assert(loadfile(assert(arg[1])))('__library_only')
local checks=0
local function eq(a,b,label) checks=checks+1; assert(a==b,(label or '')..': '..tostring(a)..' ~= '..tostring(b)) end
local function fixture(fault)
  local files,serial,opened={},0,0
  local root
  local function make(kind,perm,data)
    serial=serial+1; return {type=kind,modestr=perm,data=data or '',dev=1,ino=serial}
  end
  local function handle(node)
    opened=opened+1
    local closed=false
    return {close=function()
      if not closed then opened=opened-1; closed=true end
      return fault~='close'
    end,read=function(_,size)
      if size==8 then return fault=='random' and 'short' or '12345678' end
      return node.data
    end,write=function(_,data)
      if fault=='zero-write' then return 0 end
      local n=math.min(#data,3); node.data=node.data..data:sub(1,n); return n
    end}
  end
  local fs={}
  fs.mkdir=function(path,perm)
    eq(perm,'rwx------'); eq(path:match('^/tmp/liangxinyun%-state%-%x+$')~=nil,true)
    if fault=='mkdir' then return nil end
    eq(files[path],nil); root=path; files[path]=make('dir',perm); return true
  end
  fs.stat=function(path)
    local n=files[path]
    if not n then return nil end
    return {type=n.type,modestr=fault=='permissions' and 'rwxrwxrwx' or n.modestr,
      dev=n.dev,ino=fault=='inode' and 1 or n.ino}
  end
  fs.lstat=function(path) return files[path] end
  fs.unlink=function(path)
    eq(path==root..'/state.json' or path==root..'/replacement.tmp',true,'cleanup scope')
    if fault=='unlink' then return nil end
    files[path]=nil; return true
  end
  fs.rmdir=function(path)
    eq(path,root); if fault=='rmdir' then return nil end
    for p in pairs(files) do if p:sub(1,#path+1)==path..'/' then return nil end end
    files[path]=nil; return true
  end
  local nx={fs=fs,const={EEXIST=17},open_flags=function(...) return table.concat({...},',') end}
  nx.open=function(path,flags,perm)
    eq(perm,'rw-------'); eq(flags,'creat,excl,wronly')
    if fault=='open' then return nil end
    if files[path] then
      if fault=='exclusive' then return nil,22 end
      return nil,17
    end
    files[path]=make('reg',perm); return handle(files[path])
  end
  local ops={open=function(path)
    if path=='/dev/urandom' then return handle({}) end
    return files[path] and handle(files[path]) or nil
  end,rename=function(a,b)
    eq(a,root..'/replacement.tmp'); eq(b,root..'/state.json')
    if fault=='rename' then return nil end
    files[b],files[a]=files[a],nil; return true
  end}
  local json={stringify=function(v) return 'v'..v.revision end,parse=function(s)
    if fault=='readback' then return {} end
    return {sample='离线状态测试',revision=tonumber(s:match('v(%d)')),selectionApplied=false}
  end}
  return nx,json,ops,function() return files,opened end
end
local nx,json,ops,stats=fixture()
M.inspect(nx); local files,opened=stats(); eq(next(files),nil); eq(opened,0)
local result=M.test(nx,json,ops)
for _,name in ipairs({'stateFileTestPassed','cleanupComplete','stateWriteReadback','replacementReadback',
  'exclusiveCreateRespected','oldOpenFilePreserved','originalPreservedBeforeReplace','sameDirectoryRename'}) do
  eq(result[name],true,name)
end
files,opened=stats(); eq(next(files),nil); eq(opened,0)
for _,fault in ipairs({'mkdir','permissions','open','zero-write','close','exclusive','rename','readback','inode','unlink','rmdir','random'}) do
  nx,json,ops,stats=fixture(fault)
  result=M.test(nx,json,ops)
  eq(result.stateFileTestPassed,false,fault)
  eq(type(result.error),'string',fault)
  files,opened=stats(); eq(opened,0,fault..' descriptors')
  if fault~='unlink' and fault~='rmdir' then eq(next(files),nil,fault..' cleanup')
  else eq(result.cleanupComplete,false,fault..' cleanup failure reported') end
end
print('PASS native state diagnostic assertions: '..checks..' (filesystem substituted)')
