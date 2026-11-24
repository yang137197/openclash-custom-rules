-- Offline supervisor diagnostic: synthetic worker only, no API/UCI/controller.
local M = {}
M.SUPERVISOR_SOURCE = ([=[x#!/bin/sh
# Lua 5.1/nixio only offer default/ignored signals. This parent handles graceful stop.
# Arguments are the Lua executable, candidate script and fixed non-secret options.
umask 077
stop_file="/tmp/liangxinyun-stop.$$"
rm -f "$stop_file"
stopping=0
request_stop() {
    stopping=1
    : > "$stop_file"
}
trap request_stop TERM INT
trap 'rm -f "$stop_file"' EXIT
"$@" --stop-file "$stop_file" &
child=$!
wait "$child"
result=$?
if [ "$stopping" = 1 ]; then
    # Interrupted wait does not mean the child exited. Allow its bounded API call to finish.
    while kill -0 "$child" 2>/dev/null; do
        wait "$child"
        result=$?
    done
fi
exit "$result"
]=]):sub(2)

M.WORKER_SOURCE = ([=[xlocal nx=require 'nixio'
local root,label=arg[1],arg[2]
assert(type(root)=='string' and root:match('^/tmp/liangxinyun%-supervisor%-%x+$'))
assert(label=='immediate' or label=='delayed')
local parent,pid=nx.getppid(),nx.getpid()
local stop='/tmp/liangxinyun-stop.'..parent
assert(arg[3]=='--stop-file' and arg[4]==stop and arg[5]==nil)
local function write(name,data)
 local f=assert(io.open(root..'/'..label..'-'..name,'w'))
 assert(f:write(data)); assert(f:close())
end
local work=root..'/'..label..'-work'
write('work','synthetic-only\n')
write('ready',pid..' '..parent..'\n')
for _=1,200 do
 if nx.getppid()~=parent then
  os.remove(work); write('done','parent-exited '..pid..'\n'); os.exit(4)
 end
 local f=io.open(stop,'r')
 if f then
  f:close()
  if label=='delayed' then nx.nanosleep(0,100000000); nx.nanosleep(0,100000000) end
  assert(os.remove(work))
  write('done','stopped-and-cleaned '..pid..'\n')
  os.exit(0)
 end
 nx.nanosleep(0,100000000)
end
os.remove(work); write('done','deadline-expired '..pid..'\n'); os.exit(3)
]=]):sub(2)

local function fail(code) error(code,0) end
local function safe_error(value)
 return type(value)=='string' and value:match('^offline%-supervisor%-[a-z%-]+$') and value or 'offline-supervisor-error'
end
function M.inspect(nx)
 for _,key in ipairs({'open','open_flags','fork','exec','wait','kill','getpid','getppid','dup','nanosleep'}) do
  if type(nx[key])~='function' then fail('offline-supervisor-interface-missing') end
 end
 if not nx.stdout or not nx.stderr or type(nx.fs)~='table' or type(nx.const)~='table' then
  fail('offline-supervisor-interface-missing')
 end
 for _,key in ipairs({'mkdir','stat','lstat','unlink','rmdir'}) do
  if type(nx.fs[key])~='function' then fail('offline-supervisor-interface-missing') end
 end
 for _,key in ipairs({'SIGTERM','SIGKILL','ENOENT'}) do
  if type(nx.const[key])~='number' then fail('offline-supervisor-interface-missing') end
 end
end

function M.poll(nx,job)
 if job.reaped then return true end
 local pid,kind,code=nx.wait(job.pid,'nohang')
 if pid==false then return false end
 if pid~=job.pid then job.signalSafe=false; fail('offline-supervisor-wait-failed') end
 job.reaped=true
 job.exitCode=kind=='exited' and code or -1
 return true
end
function M.wait(nx,job,count)
 for _=1,count do
  if M.poll(nx,job) then return true end
  nx.nanosleep(0,100000000)
 end
 return false
end
function M.signal(nx,job,signal)
 if not job.signalSafe or job.pid<=1 or M.poll(nx,job) then return false end
 return nx.kill(job.pid,signal)==true
end

-- PID identity reads never authorize signaling a worker/grandchild.
function M.process(open,pid)
 local f,_,errno=open('/proc/'..pid..'/stat','r')
 if not f then return nil,errno==2 and 'absent' or 'unknown' end
 local raw=f:read('*a'); f:close()
 local tail=type(raw)=='string' and raw:match('^%d+ %(.+%) (.+)$')
 if not tail then return nil,'unknown' end
 local fields={}; for field in tail:gmatch('%S+') do fields[#fields+1]=field end
 if not tonumber(fields[2]) or not fields[20] then return nil,'unknown' end
 return {parent=tonumber(fields[2]),start=fields[20],state=fields[1]}
end
function M.worker_gone(open,worker)
 local current,reason=M.process(open,worker.pid)
 if not current then return reason=='absent' end
 return current.start~=worker.start
end
function M.evaluate(row)
 return row.supervisorReaped==true and row.supervisorExitCode==0
  and row.workerStoppedCleanly==true and row.workerGone==true
  and row.workerTemporaryCleaned==true and row.stopMarkerRemoved==true
end

function M.exec_child(nx,root,label)
 local marker='/tmp/liangxinyun-stop.'..nx.getpid()
 local existing,errno=nx.fs.lstat(marker)
 if existing~=nil or errno~=nx.const.ENOENT then return 125 end
 local log=nx.open(root..'/'..label..'-log',nx.open_flags('creat','excl','wronly'),'rw-------')
 if not log then return 126 end
 if not nx.dup(log,nx.stdout) or not nx.dup(log,nx.stderr) then log:close(); return 126 end
 if not log:close() then return 126 end
 nx.exec('/bin/sh',root..'/supervisor.run','lua',root..'/worker.lua',root,label)
 return 126 -- exec returns only on failure.
end
function M.spawn(nx,root,label,exit_child)
 local pid=nx.fork()
 if pid==0 then
  local ok,status=pcall(M.exec_child,nx,root,label)
  return exit_child(ok and status or 126)
 end
 if type(pid)~='number' or pid%1~=0 or pid<=1 then fail('offline-supervisor-fork-failed') end
 return {pid=pid,signalSafe=true,reaped=false}
end

function M.test(nx,ops)
 M.inspect(nx)
 ops=ops or {open=io.open,exit=os.exit}
 local root,owned,job,worker,stop,markerOwned,stopSent
 local result={supervisorTestPassed=false,cleanupComplete=false,cases={},forcedCleanupUsed=false}
 local function missing(path)
  local value,errno=nx.fs.lstat(path)
  return value==nil and errno==nx.const.ENOENT
 end
 local function read(path)
  local f=ops.open(path,'r'); if not f then return nil end
  local data=f:read('*a'); f:close(); return data
 end
 local function write(path,data)
  local f=nx.open(path,nx.open_flags('creat','excl','wronly'),'rw-------')
  if not f then fail('offline-supervisor-file-create-failed') end
  local offset=0
  while offset<#data do
   local n=f:write(data:sub(offset+1))
   if type(n)~='number' or n%1~=0 or n<=0 or n>#data-offset then
    f:close(); fail('offline-supervisor-file-write-failed')
   end
   offset=offset+n
  end
  if not f:close() then fail('offline-supervisor-file-close-failed') end
 end
 local ok,reason=pcall(function()
  local random=ops.open('/dev/urandom','rb')
  if not random then fail('offline-supervisor-random-failed') end
  local bytes=random:read(8); random:close()
  if type(bytes)~='string' or #bytes~=8 then fail('offline-supervisor-random-failed') end
  root='/tmp/liangxinyun-supervisor-'..bytes:gsub('.',function(c) return string.format('%02x',c:byte()) end)
  if not nx.fs.mkdir(root,'rwx------') then fail('offline-supervisor-directory-create-failed') end
  owned=true
  local meta=nx.fs.stat(root)
  if type(meta)~='table' or meta.type~='dir' or meta.modestr~='rwx------' then
   fail('offline-supervisor-directory-permissions')
  end
  write(root..'/supervisor.run',M.SUPERVISOR_SOURCE)
  write(root..'/worker.lua',M.WORKER_SOURCE)
  for _,label in ipairs({'immediate','delayed'}) do
   worker,markerOwned,stopSent=nil,false,false
   job=M.spawn(nx,root,label,ops.exit)
   stop='/tmp/liangxinyun-stop.'..job.pid
   for _=1,50 do
    local ready=read(root..'/'..label..'-ready')
    local pid,parent
    if type(ready)=='string' then pid,parent=ready:match('^(%d+) (%d+)\n$') end
    pid,parent=tonumber(pid),tonumber(parent)
    if pid and pid>1 and parent==job.pid then
     local info=M.process(ops.open,pid)
     if info and info.parent==job.pid and info.state~='Z' then
      worker={pid=pid,start=info.start}; markerOwned=true; break
     end
    end
    if M.poll(nx,job) then
     fail(job.exitCode==125 and 'offline-supervisor-marker-already-exists' or 'offline-supervisor-early-exit')
    end
    nx.nanosleep(0,100000000)
   end
   if not worker then fail('offline-supervisor-worker-not-ready') end
   if not M.signal(nx,job,nx.const.SIGTERM) then fail('offline-supervisor-signal-failed') end
   stopSent=true
   if not M.wait(nx,job,80) then fail('offline-supervisor-stop-timeout') end
   for _=1,20 do
    if M.worker_gone(ops.open,worker) then break end
    nx.nanosleep(0,100000000)
   end
   local row={case=label,supervisorReaped=job.reaped,supervisorExitCode=job.exitCode,
    workerStoppedCleanly=read(root..'/'..label..'-done')=='stopped-and-cleaned '..worker.pid..'\n',
    workerGone=M.worker_gone(ops.open,worker),workerTemporaryCleaned=missing(root..'/'..label..'-work'),
    stopMarkerRemoved=missing(stop)}
   row.passed=M.evaluate(row); result.cases[#result.cases+1]=row
   if not row.passed then fail('offline-supervisor-case-failed') end
  end
 end)
 -- Only our unreaped direct child is signalable. Never signal by a worker PID.
 local cleanupOK=true
 if job and not job.reaped and job.signalSafe then
  if not stopSent then pcall(M.signal,nx,job,nx.const.SIGTERM) end
  local waited,finished=pcall(M.wait,nx,job,30)
  if not waited or not finished then
   result.forcedCleanupUsed=true
   pcall(M.signal,nx,job,nx.const.SIGKILL)
   waited,finished=pcall(M.wait,nx,job,20)
   if not waited or not finished then cleanupOK=false end
  end
 end
 if job and not job.reaped then cleanupOK=false end
 if worker then
  for _=1,220 do
   if M.worker_gone(ops.open,worker) then break end
   nx.nanosleep(0,100000000)
  end
  if not M.worker_gone(ops.open,worker) then cleanupOK=false end
 end
 if markerOwned and cleanupOK and stop and not missing(stop) then
  if not nx.fs.unlink(stop) then cleanupOK=false end
 end
 if owned and cleanupOK then
  local names={'supervisor.run','worker.lua'}
  for _,label in ipairs({'immediate','delayed'}) do
   for _,suffix in ipairs({'log','ready','work','done'}) do names[#names+1]=label..'-'..suffix end
  end
  for _,name in ipairs(names) do
   local path=root..'/'..name
   if not missing(path) and not nx.fs.unlink(path) then cleanupOK=false end
  end
  if not nx.fs.rmdir(root) or not missing(root) then cleanupOK=false end
 end
 result.cleanupComplete=cleanupOK
 result.supervisorTestPassed=ok and cleanupOK and not result.forcedCleanupUsed
 if not ok then result.error=safe_error(reason)
 elseif not cleanupOK then result.error='offline-supervisor-cleanup-failed' end
 if not cleanupOK and owned then result.temporaryDirectory=root end
 return result
end

function M.main(args)
 local available,json=pcall(require,'luci.jsonc')
 if not available then print('offline-supervisor-json-unavailable'); return 1 end
 local testing=#args==1 and args[1]=='--test-once'
 local ok,result=pcall(function()
  if not testing and not (#args==0 or (#args==1 and args[1]=='--inspect-only')) then
   fail('offline-supervisor-arguments-invalid')
  end
  local nx=require 'nixio'; M.inspect(nx)
  return testing and M.test(nx) or {}
 end)
 if not ok then result={error=safe_error(result),supervisorTestPassed=false,cleanupComplete=false} end
 result.mode=testing and 'offline-supervisor-test' or 'offline-supervisor-inspection'
 result.readOnly=not testing
 result.apiRequests,result.probeRequests,result.selectionApplied,result.formalAcceptance=0,0,false,false
 print(json.stringify(result))
 return ok and (not testing or result.supervisorTestPassed) and 0 or 1
end
if (...)=='__library_only' then return M end
os.exit(M.main(arg or {}))
