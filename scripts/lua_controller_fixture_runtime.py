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
    (modules / 'nixio.lua').write_text('''
local function q(s) return "'"..s:gsub("'", "'\\\\''").."'" end
local function pid()
 local f=assert(io.open('/proc/self/stat')); local p=f:read('*n'); f:close(); return p
end
local function open(path,flags,mode)
 if flags.excl then local f=io.open(path); if f then f:close(); return nil end end
 local f=io.open(path,flags.wronly and 'w' or 'a+')
 if not f then return nil end
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
  f:close()
 end}
end
return {getpid=pid,open=open,open_flags=function(...)
 local t={}; for _,v in ipairs({...}) do t[v]=true end; return t
end,gettimeofday=function() return os.time(),0 end,
nanosleep=function(s,ns) os.execute('sleep '..tostring(s+ns/1000000000)) end}
''')
    env = os.environ.copy()
    env['LUA_PATH'] = str(modules / '?.lua')
    env['PATH'] = str(binaries) + os.pathsep + env['PATH']
    return env
