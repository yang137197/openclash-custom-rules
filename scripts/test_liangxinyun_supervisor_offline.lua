-- Actual Lua, substituted process/filesystem interfaces; no OS process signals.
local M=assert(loadfile(assert(arg[1])))('__library_only')
local count=0
local function eq(a,b,label) count=count+1; assert(a==b,(label or '')..': '..tostring(a)..' ~= '..tostring(b)) end
local function fixture(fault)
 local files,root,jobs,serial,signals={},nil,{},0,{}
 local nx={const={SIGTERM=15,SIGKILL=9,ENOENT=2},stdout={},stderr={}}
 nx.getpid=function() return 101 end; nx.getppid=function() return 100 end
 nx.exec=function(...) return nil end; nx.dup=function() return true end
 nx.open_flags=function(...) return table.concat({...},',') end
 nx.nanosleep=function() end
 nx.fs={mkdir=function(path,mode)
  eq(mode,'rwx------'); if fault=='mkdir' then return nil end
  root=path; files[path]='directory'; return true
 end,stat=function() return {type='dir',modestr='rwx------'} end,
 lstat=function(path) if files[path] then return {type='reg'} end; return nil,2 end,
 unlink=function(path)
  eq(path:sub(1,#root+1)==root..'/' or path:match('^/tmp/liangxinyun%-stop%.10[12]$')~=nil,true,'cleanup scope')
  if fault=='unlink' then return nil end
  files[path]=nil; return true
 end,rmdir=function(path)
  eq(path,root)
  for p in pairs(files) do if p:sub(1,#root+1)==root..'/' then return nil end end
  files[path]=nil; return true
 end}
 nx.open=function(path,flags,mode)
  eq(mode,'rw-------'); eq(flags,'creat,excl,wronly'); eq(files[path],nil)
  files[path]=''
  return {write=function(_,data) files[path]=files[path]..data; return #data end,close=function() return true end}
 end
 nx.fork=function()
  if fault=='fork' then return nil end
  serial=serial+1
  local label=serial==1 and 'immediate' or 'delayed'
  local j={pid=100+serial,worker=1100+serial,label=label,present=true}; jobs[j.pid]=j
  if fault~='ready' and fault~='early' then
   files[root..'/'..label..'-ready']=j.worker..' '..j.pid..'\n'
   files[root..'/'..label..'-work']='synthetic'
  end
  return j.pid
 end
 nx.wait=function(pid,flag)
  eq(flag,'nohang'); local j=assert(jobs[pid])
  if fault=='early' then j.present=false; return pid,'exited',7 end
  if not j.stopping then return false end
  if fault=='timeout' and not j.killed then return false end
  if not j.finished then
   j.finished=true; j.present=fault=='worker-alive'
   files[root..'/'..j.label..'-done']='stopped-and-cleaned '..j.worker..'\n'
   files[root..'/'..j.label..'-work']=nil
   if fault~='marker' then files['/tmp/liangxinyun-stop.'..pid]=nil end
  end
  return pid,'exited',fault=='exit' and 7 or j.killed and 1 or 0
 end
 nx.kill=function(pid,signal)
  eq(pid>1 and pid<200,true,'only owned supervisor signalable')
  signals[#signals+1]={pid,signal}; local j=assert(jobs[pid])
  j.stopping=true; if signal==9 then j.killed=true end
  files['/tmp/liangxinyun-stop.'..pid]=''
  return true
 end
 local ops={exit=function(code) error('unexpected child branch '..code) end}
 ops.open=function(path)
  if path=='/dev/urandom' then return {read=function() return '12345678' end,close=function() return true end} end
  local pid=tonumber(path:match('^/proc/(%d+)/stat$'))
  if pid then
   for _,j in pairs(jobs) do
    if j.worker==pid and j.present then
     local fields={'S',tostring(j.pid)}; for i=3,19 do fields[i]='0' end; fields[20]='1000'
     return {read=function() return pid..' (lua) '..table.concat(fields,' ') end,close=function() return true end}
    end
   end
   return nil,'absent',2
  end
  if not files[path] then return nil,'absent',2 end
  return {read=function() return files[path] end,close=function() return true end}
 end
 return nx,ops,function() return files,signals end
end
local nx,ops,stats=fixture()
M.inspect(nx); local files,signals=stats(); eq(next(files),nil); eq(#signals,0)
local result=M.test(nx,ops)
eq(result.supervisorTestPassed,true); eq(result.cleanupComplete,true); eq(#result.cases,2)
files,signals=stats(); eq(next(files),nil); eq(#signals,2)
for _,fault in ipairs({'mkdir','fork','ready','early','timeout','exit','marker','worker-alive','unlink'}) do
 nx,ops,stats=fixture(fault); result=M.test(nx,ops)
 eq(result.supervisorTestPassed,false,fault); eq(type(result.error),'string',fault)
 if fault=='worker-alive' or fault=='unlink' then eq(result.cleanupComplete,false,fault)
 else eq(result.cleanupComplete,true,fault) end
 if fault=='timeout' then eq(result.forcedCleanupUsed,true) end
end
local good={supervisorReaped=true,supervisorExitCode=0,workerStoppedCleanly=true,
 workerGone=true,workerTemporaryCleaned=true,stopMarkerRemoved=true}
eq(M.evaluate(good),true)
for key,v in pairs(good) do
 good[key]=key=='supervisorExitCode' and 7 or false; eq(M.evaluate(good),false,key); good[key]=v
end
nx=fixture(); nx.wait=function() return 101,'exited',0 end
local job={pid=101,signalSafe=true,reaped=false}
nx.kill=function() error('must not signal a reaped child') end
eq(M.signal(nx,job,15),false); eq(job.reaped,true)
nx=fixture(); nx.wait=function() return nil,10 end
job={pid=101,signalSafe=true,reaped=false}
eq(pcall(M.poll,nx,job),false); eq(job.signalSafe,false)
nx=fixture(); nx.fs.lstat=function() return {},nil end
eq(M.exec_child(nx,'/tmp/test','immediate'),125,'preexisting marker never touched')
nx=fixture(); nx.fs.lstat=function() return nil,2 end
local calls={}
nx.open=function() return {close=function() return true end} end
nx.exec=function(...) calls={...}; return nil end
eq(M.exec_child(nx,'/tmp/test','delayed'),126)
eq(calls[1],'/bin/sh'); eq(calls[2],'/tmp/test/supervisor.run'); eq(calls[3],'lua')
for _,name in ipairs({'fork','exec','wait','dup','getppid'}) do
 nx=fixture(); nx[name]=nil; eq(pcall(M.inspect,nx),false)
end
local printed,oldPrint,oldNixio,oldJson=nil,print,package.loaded.nixio,package.loaded['luci.jsonc']
nx,ops,stats=fixture()
package.loaded.nixio=nx
package.loaded['luci.jsonc']={stringify=function(value) printed=value; return 'synthetic-json' end}
print=function() end
for _,args in ipairs({{}, {'--inspect-only'}}) do
 eq(M.main(args),0); eq(printed.mode,'offline-supervisor-inspection'); eq(printed.readOnly,true)
 eq(printed.apiRequests,0); eq(printed.probeRequests,0); eq(printed.selectionApplied,false)
 eq(printed.formalAcceptance,false)
 files,signals=stats(); eq(next(files),nil); eq(#signals,0)
end
eq(M.main({'--unexpected'}),1); eq(printed.error,'offline-supervisor-arguments-invalid')
files,signals=stats(); eq(next(files),nil); eq(#signals,0)
package.loaded.nixio,package.loaded['luci.jsonc'],print=oldNixio,oldJson,oldPrint
print('PASS offline supervisor assertions: '..count..' (interfaces substituted)')
