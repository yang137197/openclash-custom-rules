-- Actual Lua, simulated nixio: covers diagnostic decisions, not native locking.
local M=assert(loadfile(assert(arg[1])))('__library_only')
local checks=0
local function eq(a,b) checks=checks+1; assert(a==b,tostring(a)..' ~= '..tostring(b)) end
local function fixture(fault)
  local locked,closed=false,false
  local forks,kills,waits=0,0,0
  local nx={const={EACCES=13,EAGAIN=11,SIGKILL=9},nanosleep=function() end}
  local file={lock=function(_,mode)
    if mode=='tlock' then locked=true; return fault~='parent' end
    eq(mode,'ulock'); locked=false; return fault~='release'
  end,close=function() closed=true; return true end}
  nx.mkstemp=function(template) eq(template,'liangxinyun-native-lock'); return fault~='temp' and file or nil end
  nx.fork=function()
    forks=forks+1; eq(locked,forks==1)
    if fault=='fork' then return nil end
    return 100+forks
  end
  nx.wait=function(pid,flag)
    waits=waits+1
    if fault=='timeout' and flag then return false end
    if fault=='wait' then return nil,10 end
    return pid,'exited',fault=='child' and 1 or 0
  end
  nx.kill=function(pid,signal) eq(pid,101); eq(signal,9); kills=kills+1; return true end
  return nx,function() return closed,forks,kills,waits end
end
local nx,stats=fixture()
M.inspect(nx); local closed,forks=stats(); eq(closed,false); eq(forks,0)
local result=M.test(nx,os.exit)
eq(result.competingChildBlocked,true); eq(result.childAcquiredAfterUnlock,true)
closed,forks=stats(); eq(closed,true); eq(forks,2)
for _,fault in ipairs({'temp','parent','release','fork','wait','child','timeout'}) do
  nx,stats=fixture(fault)
  local ok,err=pcall(M.test,nx,os.exit)
  eq(ok,false); eq(type(err),'string')
  local c,f,k,w=stats()
  eq(c,fault~='temp')
  eq(k,fault=='timeout' and 1 or 0)
  if fault=='timeout' then eq(w,101) end
end
for _,errno in ipairs({11,13,22,38}) do
  local c={EACCES=13,EAGAIN=11}
  local fake={lock=function() return nil,errno end}
  eq(M.child_check(fake,false,c),errno==11 or errno==13)
  eq(M.child_check(fake,true,c),false)
end
eq(M.child_check({lock=function() return true end},true,{EACCES=13,EAGAIN=11}),true)
eq(M.child_check({lock=function() return true end},false,{EACCES=13,EAGAIN=11}),false)
for _,name in ipairs({'mkstemp','fork','wait','kill','nanosleep'}) do
 nx=fixture(); nx[name]=nil; eq(pcall(M.inspect,nx),false)
end
nx=fixture(); nx.const.EAGAIN=nil; eq(pcall(M.inspect,nx),false)
print('PASS native lock diagnostic assertions: '..checks..' (nixio substituted)')
