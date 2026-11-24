"""Local-only LuCI/nixio substitutes, not a CatWrt compatibility claim.

JSON parsing and POSIX record locking use Python helpers. Actual Lua 5.1, curl,
HTTP, shell supervision and Mihomo execute without mocking their behavior.
"""
from pathlib import Path
import os

from verify_liangxinyun_readonly import JSON_ENCODER, lua_string


def install(root: Path, lua: Path):
    modules, binaries = root / 'modules', root / 'bin'
    (modules / 'luci').mkdir(parents=True)
    binaries.mkdir()
    (binaries / 'lua').symlink_to(lua)
    bridge = root / 'json_bridge.py'
    bridge.write_text('''import json,sys
def lua(v):
 if v is None: return "nil"
 if v is True: return "true"
 if v is False: return "false"
 if isinstance(v,(int,float)): return repr(v)
 if isinstance(v,str): return '"'+''.join('\\\\'+str(b).zfill(3) for b in v.encode())+'"'
 if isinstance(v,list): return '{'+','.join(lua(x) for x in v)+'}'
 return '{'+','.join('['+lua(k)+']='+lua(x) for k,x in v.items())+'}'
with open(sys.argv[1]) as f: print('return '+lua(json.load(f)))
''')
    (modules / 'luci/jsonc.lua').write_text(JSON_ENCODER + '''
local function parse(body)
 local path=os.tmpname()
 local f=assert(io.open(path,'w')); f:write(body); f:close()
 local p=assert(io.popen('python3 '..''' + lua_string(str(bridge)) + '''..' '..path..' 2>/dev/null','r'))
 local data=p:read('*a'); p:close(); os.remove(path)
 local code=loadstring(data)
 if code then return code() end
end
return {parse=parse,stringify=encode}
''')
    lock_helper = root / 'lock.py'
    lock_helper.write_text('''import fcntl,os,sys,time
path,pid,stop=sys.argv[1],int(sys.argv[2]),sys.argv[3]
f=open(path,'a+')
try: fcntl.lockf(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
except OSError:
 print('0',flush=True); sys.exit(0)
print('1',flush=True)
while not os.path.exists(stop):
 try: os.kill(pid,0)
 except ProcessLookupError: break
 time.sleep(.03)
''')
    metadata = root / 'metadata.py'
    metadata.write_text('''import os,stat,sys
try: s=os.lstat(sys.argv[1])
except FileNotFoundError: sys.exit(0)
kind='dir' if stat.S_ISDIR(s.st_mode) else 'reg' if stat.S_ISREG(s.st_mode) else 'other'
print(kind,stat.filemode(s.st_mode)[1:],s.st_dev,s.st_ino)
''')
    (modules / 'nixio.lua').write_text('''
local function q(s) return "'"..s:gsub("'", "'\\\\''").."'" end
local function pid()
 local f=assert(io.open('/proc/self/stat')); local p=f:read('*n'); f:close(); return p
end
-- Match the native API's permission convention, not POSIX bit-value numbers.
-- Numeric 600 is accepted; 384 is rejected because an octal digit cannot be 8.
local function permission(mode)
 if type(mode)=='string' and #mode==9 then
  local digits={0,0,0}
  for i=1,9 do
   local c=mode:sub(i,i); local expected=({'r','w','x'})[(i-1)%3+1]
   if c~='-' and c~=expected then error('nixio-mode-invalid',0) end
   if c~='-' then local group=math.floor((i-1)/3)+1; digits[group]=digits[group]+2^(2-(i-1)%3) end
  end
  return table.concat(digits)
 end
 local octal=type(mode)=='number' and mode%1==0 and tostring(mode) or ''
 if #octal<1 or #octal>4 or octal:find('[^0-7]') then error('nixio-mode-invalid',0) end
 return octal
end
local function open(path,flags,mode)
 local octal=permission(mode)
 if flags.excl then local f=io.open(path); if f then f:close(); return nil,17 end end
 local f=io.open(path,flags.wronly and 'w' or 'a+')
 if not f then return nil end
 os.execute('chmod '..octal..' '..q(path))
 local pipe,stop
 return {
 write=function(_,data) local ok=f:write(data); return ok and #data end,
 lock=function(_,kind)
  assert(kind=='tlock')
  stop=path..'.'..pid()..'.release'
  os.remove(stop)
  pipe=assert(io.popen('python3 '..q(''' + lua_string(str(lock_helper)) + ''')..' '..q(path)..' '..pid()..' '..q(stop),'r'))
  return pipe:read('*l')=='1'
 end,
 close=function()
  if pipe then local marker=assert(io.open(stop,'w')); marker:close(); pipe:close(); os.remove(stop) end
  return f:close()
 end}
end
local function stat(path)
 local p=assert(io.popen('python3 '..q(''' + lua_string(str(metadata)) + ''')..' '..q(path),'r'))
 local data=p:read('*a'); p:close()
 local kind,mode,dev,ino=data:match('^(%S+) (%S+) (%d+) (%d+)')
 if not kind then return nil end
 return {type=kind,modestr=mode,dev=tonumber(dev),ino=tonumber(ino)}
end
local fs={stat=stat,lstat=stat,unlink=os.remove,rmdir=os.remove,
 mkdir=function(path,mode) return os.execute('mkdir -m '..permission(mode)..' '..q(path)..' 2>/dev/null')==0 end}
local function ppid()
 local f=assert(io.open('/proc/self/stat')); local data=f:read('*a'); f:close()
 return tonumber(data:match('^%d+ %(.+%) %S+ (%d+)'))
end
return {getpid=pid,getppid=ppid,open=open,fs=fs,const={EEXIST=17},open_flags=function(...)
 local t={}; for _,v in ipairs({...}) do t[v]=true end; return t
end,gettimeofday=function() return os.time(),0 end,
nanosleep=function(s,ns) os.execute('sleep '..tostring(s+ns/1000000000)) end}
''')
    env = os.environ.copy()
    env['LUA_PATH'] = str(modules / '?.lua')
    env['PATH'] = str(binaries) + os.pathsep + env['PATH']
    return env
