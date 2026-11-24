-- Actual Lua contract parity; no OS process, API, or router access.
local M=assert(loadfile(assert(arg[1])))("__library_only")
local C=assert(loadfile(assert(arg[2])))("__library_only")
local count=0
local function eq(a,b,label) count=count+1; assert(a==b,(label or '')..': '..tostring(a)..' ~= '..tostring(b)) end
local function copy(v)
 if type(v)~='table' then return v end
 local out={}; for k,x in pairs(v) do out[k]=copy(x) end; return out
end
local function fixture()
 local g={type='Selector',all={'REJECT'},now='LXY: 日本专线01'}
 local p={name='liangxinyun',testUrl=M.TEST_URL,expectedStatus='204',proxies={}}
 for _,tier in ipairs(M.TIERS) do
  for i=1,2 do
   local name='LXY: '..tier..string.format('%02d',i)
   g.all[#g.all+1]=name; p.proxies[#p.proxies+1]={name=name,['provider-name']='liangxinyun'}
  end
 end
 return g,p,copy(g)
end
local function run(change)
 local g,p,a=fixture(); if change then change(g,p,a) end
 local r=M.inspect(g,p,a)
 eq(r.candidateCompatible,pcall(C.validate,g,p,a,C.TEST_URL),'candidate parity')
 if r.inspectionComplete then eq(r.contractChecksAgree,true) end
 return r
end
local r=run(); eq(r.candidateCompatible,true); eq(#r.blockingReasons,0)
eq(r.groupMembers,9); eq(r.providerNodes,8); eq(r.selectionUnchanged,true)
for _,row in ipairs(r.tiers) do eq(row.nodes,2) end
local faults={
 function(g,p,a) table.remove(g.all,1); table.remove(a.all,1) end,
 function(g,p,a) local name='LXY: 香港01'; g.all[#g.all+1]=name; a.all[#a.all+1]=name; p.proxies[#p.proxies+1]={name=name} end,
 function(g,p,a) p.testUrl='https://custom.invalid/private-token' end,
 function(g,p,a) p.expectedStatus='' end,
 function(g,p,a) p.expectedStatus=204 end,
 function(g,p,a) p.proxies[1]['provider-name']='wrong-source' end,
 function(g,p,a) g.type='URLTest' end,
 function(g,p,a) a.now='REJECT' end,
 function(g,p,a) a.all[2]='changed' end,
 function(g,p,a) p.name='other-provider' end,
 function(g,p,a) p.proxies[1].name='different-node' end,
 function(g,p,a) g.now='absent'; a.now='absent' end,
 function(g,p,a) g.all[99]='hole' end,
 function(g,p,a) g.all[3]=g.all[2]; a.all[3]=a.all[2] end,
 function(g,p,a) p.proxies[1]=false end,
 function(g,p,a) p.proxies=false end,
}
for _,change in ipairs(faults) do
 r=run(change); eq(r.candidateCompatible,false); eq(#r.blockingReasons>0,true)
 eq(type(r.firstRejection),'string')
end
r=run(function(g,p,a)
 g.all={}; a.all={}; p.proxies={}
 for i=1,45 do
  local name=i<=21 and ('LXY: 日本专线'..i) or ('LXY: 香港'..i)
  g.all[i],a.all[i]=name,name; p.proxies[i]={name=name}
 end
 g.now,a.now=g.all[1],a.all[1]; p.testUrl=''; p.expectedStatus=''
end)
eq(r.inspectionComplete,true); eq(r.groupMembers,45); eq(r.providerNodes,45)
eq(r.outsideTierGroupNodes,24); eq(r.outsideTierProviderNodes,24)
eq(r.checks.rejectFirst,false); eq(r.checks.testUrlMatches,false)
eq(r.checks.expectedStatusMatches,false)
for _,port in ipairs({'0','65536','127.0.0.1:9090','9090/secret','x'}) do
 eq(pcall(M.reader,{},port),false,'invalid port')
end
local reader=M.reader({},'9090')
for _,path in ipairs({'/configs',M.PROVIDER_PATH..'/healthcheck','/connections','PUT',M.GROUP_PATH..'/delay'}) do
 eq(pcall(reader,path),false,'non-allowlisted path')
end
print('PASS candidate read-only assertions: '..count)
