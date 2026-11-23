-- State-machine tests: actual Lua 5.1; no networking or router writes.
local M = assert(loadfile(assert(arg[1])))("__library_only")
local count = 0
local function eq(a,b,label) count=count+1; assert(a==b,(label or '')..': '..tostring(a)..' ~= '..tostring(b)) end
local function copy(v)
 if type(v)~='table' then return v end
 local o={}; for k,x in pairs(v) do o[k]=copy(x) end; return o
end
local stamp, now = '2026-11-23T12:34:56Z', 1795437296
local labels={'日本专线','日本高速','美国流媒体','美国高速'}
local nodes={}
for rank,label in ipairs(labels) do
 for i=1,2 do
  nodes[#nodes+1]={name='LXY: '..label..i, ['provider-name']='liangxinyun',
   extra={[M.TEST_URL]={alive=true,history={{time=stamp,delay=100-rank*10-i}}}}}
 end
end
local function fixture()
 local group={type='Selector',all={'REJECT'},now=nodes[1].name}
 for _,n in ipairs(nodes) do group.all[#group.all+1]=n.name end
 local provider={name=M.PROVIDER,proxies=copy(nodes),testUrl=M.TEST_URL,expectedStatus='204',updatedAt='fixture-1'}
 local requests, probes={},0
 local function request(method,path,body)
  requests[#requests+1]={method=method,path=path,body=body}
  if method=='PUT' then eq(path,M.GROUP_PATH,'only Liangxinyun mutable'); group.now=body.name; return true end
  if path==M.GROUP_PATH then return copy(group) end
  if path==M.PROVIDER_PATH then return copy(provider) end
  if path==M.PROVIDER_PATH..'/healthcheck' then probes=probes+1; return true end
  error('unexpected request')
 end
 local c=M.controller(request,{url=M.TEST_URL,max_age=130,now=function() return now end})
 return c,group,provider,requests,function() return probes end
end
local function dead(n) n.extra[M.TEST_URL]={alive=false,history={{time=stamp,delay=0}}} end
local function decision(c,name) local v=c:step(false); eq(v.wouldSelect,name); eq(v.verifiedSelection,true) end
local c,g,p,requests,probes=fixture()
decision(c,nodes[2].name)
for _,r in ipairs(requests) do
 if r.method=='PUT' then eq(r.body.name,'REJECT','first mutation fails closed'); break end
 eq(r.path~=M.PROVIDER_PATH..'/healthcheck',true,'startup rejects before probing')
end
eq(probes(),0)
dead(p.proxies[2]); decision(c,nodes[1].name)
for rank=1,3 do
 dead(p.proxies[rank*2-1]); dead(p.proxies[rank*2])
 decision(c,nodes[rank*2+2].name)
end
dead(p.proxies[7]); dead(p.proxies[8]); decision(c,'REJECT')
p.proxies[1]=copy(nodes[1]); decision(c,nodes[1].name)
p.proxies[2]=copy(nodes[2]); p.proxies[2].extra[M.TEST_URL].history[1].delay=nodes[1].extra[M.TEST_URL].history[1].delay
decision(c,nodes[1].name)
p.proxies[1].extra={}; p.proxies[2].extra={}; decision(c,'REJECT')
p.proxies[2]=copy(nodes[2]); decision(c,nodes[2].name)
now=now+131; decision(c,'REJECT'); now=now-131
eq(c:reject(),true); eq(g.now,'REJECT')
c:step(true); eq(probes(),1,'explicit provider detection')

for _,kind in ipairs({'legacy','source','contract','duplicate','race'}) do
 local cc,gg,pp,rr=fixture()
 if kind=='legacy' then table.remove(gg.all,1)
 elseif kind=='source' then pp.proxies[1]['provider-name']='ikuuu'
 elseif kind=='contract' then pp.expectedStatus='200'
 elseif kind=='duplicate' then pp.proxies[2].name=pp.proxies[1].name
 elseif kind=='race' then table.remove(gg.all) end
 eq(pcall(function() cc:step(true) end),false,kind..' refused')
 eq(cc.managed,false)
 for _,r in ipairs(rr) do eq(r.method,'GET',kind..' never writes'); eq(r.path~=M.PROVIDER_PATH..'/healthcheck',true) end
end

-- The dry controller computes recommendations without startup REJECT/probes/PUT.
local _,dg,dp,dr=fixture()
local dc=M.controller(function(method,path)
 dr[#dr+1]={method=method,path=path}
 eq(method,'GET'); eq(path~=M.PROVIDER_PATH..'/healthcheck',true)
 return copy(path==M.GROUP_PATH and dg or dp)
end,{dry=true,url=M.TEST_URL,max_age=130,now=function() return now end})
eq(dc:step(true).wouldSelect,nodes[2].name); eq(dc:reject(),false)
eq(dg.now,nodes[1].name)
for _,name in ipairs({'LXY: 美国05|流媒体|0.1x','LXY: 流媒体美国05'}) do eq(M.tier(name),3) end
eq(M.tier('iKuuu 日本专线01'),nil)
-- Exhaust all healthy/failed combinations across two nodes in each tier.
for mask=0,255 do
 local sample,ms,expected=copy(nodes),{},'REJECT'
 for i,n in ipairs(sample) do
  ms[n.name]=true
  if math.floor(mask/2^(i-1))%2==0 then dead(n) end
 end
 for rank=1,4 do
  local a,b=sample[rank*2-1],sample[rank*2]
  if b.extra[M.TEST_URL].alive then expected=b.name; break end
  if a.extra[M.TEST_URL].alive then expected=a.name; break end
 end
 eq(M.decide(sample,ms,{url=M.TEST_URL,now=now,max_age=130}).wouldSelect,expected,'combination '..mask)
end
-- A selector write must be read back, not accepted solely on HTTP success.
local cc,gg,pp=fixture()
local broken=M.controller(function(method,path)
 if method=='PUT' then return true end
 return copy(path==M.GROUP_PATH and gg or pp)
end,{url=M.TEST_URL,max_age=130,now=function() return now end})
eq(pcall(function() broken:step(false) end),false,'write acknowledgement without effect refused')
-- Simulate history loss after core restart with a persisted lower-tier choice.
local rc,rg,rp,rr=fixture()
rc:step(false)
rg.now=nodes[6].name
for _,n in ipairs(rp.proxies) do n.extra={} end
local start=#rr
rc:step(true)
local rejected_before_probe=false
for i=start+1,#rr do
 local r=rr[i]
 if r.method=='PUT' and r.body.name=='REJECT' then rejected_before_probe=true end
 if r.path==M.PROVIDER_PATH..'/healthcheck' then eq(rejected_before_probe,true,'reject history loss before probe') end
end
print('PASS Lua controller assertions: '..count)
