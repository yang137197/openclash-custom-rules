-- Read existing runtime-path file only; no API, no probing, no writes.
local M={}
M.REFERENCE={
 "DOMAIN-SUFFIX,pve.yangnas.cn",
 "DOMAIN-SUFFIX,auth.yangnas.cn",
 "DOMAIN-SUFFIX,nexus.yangnas.cn",
 "DOMAIN-SUFFIX,gdwzy.top",
 "DOMAIN-SUFFIX,siwiot.com",
 "DOMAIN-SUFFIX,askdwl.com",
 "DOMAIN-SUFFIX,faw-vw.com",
 "DOMAIN-SUFFIX,audi.cn",
 "DOMAIN-SUFFIX,kimi.com",
 "DOMAIN-SUFFIX,moonshot.cn",
 "DOMAIN-SUFFIX,alimama.com",
 "DOMAIN-SUFFIX,stellarhub.top",
 "DOMAIN-SUFFIX,mp.microsoft.com",
 "DOMAIN-SUFFIX,windowsupdate.com",
 "DOMAIN-SUFFIX,update.microsoft.com",
 "DOMAIN-SUFFIX,download.microsoft.com",
 "DOMAIN-SUFFIX,packages.microsoft.com",
 "DOMAIN-SUFFIX,definitionupdates.microsoft.com",
 "DOMAIN-SUFFIX,ctldl.windowsupdate.com",
 "DOMAIN-SUFFIX,adl.windows.com",
 "DOMAIN-SUFFIX,storeedge.microsoft.com",
 "DOMAIN-SUFFIX,apps.microsoft.com",
 "DOMAIN-SUFFIX,store-images.microsoft.com",
 "DOMAIN-SUFFIX,images-eds-ssl.xboxlive.com",
 "DOMAIN-SUFFIX,assets.onestore.ms",
 "DOMAIN-SUFFIX,wcpstatic.microsoft.com",
 "DOMAIN-SUFFIX,c1.microsoft.com",
 "DOMAIN-SUFFIX,go.microsoft.com",
 "DOMAIN-SUFFIX,storesdk.dsx.mp.microsoft.com",
 "DOMAIN-SUFFIX,manage.devcenter.microsoft.com",
 "DOMAIN-SUFFIX,activation.sls.microsoft.com",
 "DOMAIN-SUFFIX,activation-v2.sls.microsoft.com",
 "DOMAIN-SUFFIX,crl.microsoft.com",
 "DOMAIN-SUFFIX,mscrl.microsoft.com",
 "DOMAIN-SUFFIX,cs.dds.microsoft.com",
 "DOMAIN-SUFFIX,dmd.metaservices.microsoft.com",
 "DOMAIN-SUFFIX,storequality.microsoft.com",
 "DOMAIN-SUFFIX,s-microsoft.com",
 "DOMAIN-SUFFIX,img-prod-cms-rt-microsoft-com.akamaized.net",
 "DOMAIN-SUFFIX,account.live.com",
 "DOMAIN-SUFFIX,login.live.com",
 "DOMAIN-SUFFIX,oauth.live.com",
 "DOMAIN-SUFFIX,login.microsoftonline.com",
 "DOMAIN-SUFFIX,login.microsoft.com",
 "DOMAIN-SUFFIX,login.windows.net",
 "DOMAIN-SUFFIX,graph.windows.net",
 "DOMAIN-SUFFIX,msauth.net",
 "DOMAIN-SUFFIX,msauthimages.net",
 "DOMAIN-SUFFIX,msftauth.net",
 "DOMAIN-SUFFIX,msftauthimages.net",
 "DOMAIN-SUFFIX,microsoftaik.azure.net",
 "DOMAIN-SUFFIX,token.cp.microsoft.com",
 "DOMAIN-SUFFIX,msftconnecttest.com",
 "DOMAIN-SUFFIX,data.microsoft.com",
 "DOMAIN-SUFFIX,telemetry.microsoft.com",
 "DOMAIN-SUFFIX,activity.windows.com",
 "DOMAIN-SUFFIX,notify.windows.com",
 "DOMAIN-SUFFIX,wns.windows.com",
 "DOMAIN-SUFFIX,dm.microsoft.com",
 "DOMAIN-SUFFIX,time.windows.com",
 "DOMAIN-SUFFIX,aria.microsoft.com",
 "DOMAIN-SUFFIX,wdcp.microsoft.com",
 "DOMAIN-SUFFIX,wdcpalt.microsoft.com",
 "DOMAIN-SUFFIX,checkappexec.microsoft.com",
 "DOMAIN-SUFFIX,fpt.dfp.microsoft.com",
 "DOMAIN-SUFFIX,smartscreen-prod.microsoft.com",
 "DOMAIN-SUFFIX,smartscreen.microsoft.com",
 "DOMAIN-SUFFIX,endpoint.security.microsoft.com",
 "DOMAIN-SUFFIX,fs.microsoft.com",
 "DOMAIN-SUFFIX,inference.location.live.net",
 "DOMAIN-SUFFIX,maps.windows.com",
 "DOMAIN-SUFFIX,ecn.dev.virtualearth.net",
 "DOMAIN-SUFFIX,ecn-us.dev.virtualearth.net",
 "DOMAIN-SUFFIX,edge.microsoft.com",
 "DOMAIN-SUFFIX,api.cdp.microsoft.com",
 "DOMAIN-SUFFIX,officecdn.microsoft.com",
 "DOMAIN-SUFFIX,cdn.office.net",
 "DOMAIN-SUFFIX,static.microsoft",
 "DOMAIN-SUFFIX,manage.microsoft.com",
 "DOMAIN-SUFFIX,officeclient.microsoft.com",
 "DOMAIN-SUFFIX,odc.officeapps.live.com",
 "DOMAIN-SUFFIX,shellprod.msocdn.com",
 "DOMAIN-SUFFIX,partner.outlook.cn",
 "DOMAIN-SUFFIX,protection.partner.outlook.cn",
 "DOMAIN-SUFFIX,office365-net.cn",
 "DOMAIN-SUFFIX,partner.office365.cn",
 "DOMAIN-SUFFIX,sharepoint.cn",
 "DOMAIN-SUFFIX,microsoftonline.cn",
 "DOMAIN-SUFFIX,partner.microsoftonline.cn",
 "DOMAIN-SUFFIX,office365.cn",
 "DOMAIN-SUFFIX,officewebapps.cn",
 "DOMAIN-SUFFIX,loki.office365.cn",
 "DOMAIN-SUFFIX,onmschina.cn",
 "DOMAIN-SUFFIX,partner.microsoftonline-p.cn",
 "DOMAIN-SUFFIX,partner.microsoftonline-m-i.net.cn",
 "DOMAIN-SUFFIX,partner.microsoftonline-m.net.cn",
 "DOMAIN-SUFFIX,partner.microsoftonline-p.net.cn",
 "DOMAIN-SUFFIX,msauth.cn",
 "DOMAIN-SUFFIX,msauthimages.cn",
 "DOMAIN-SUFFIX,msftauth.cn",
 "DOMAIN-SUFFIX,msftauthimages.cn",
 "DOMAIN-SUFFIX,auth.microsoft.cn",
 "DOMAIN-SUFFIX,aadrm.cn",
 "DOMAIN-SUFFIX,sovcloud.cn",
 "DOMAIN-SUFFIX,sovcloud-static.cn",
 "DOMAIN-SUFFIX,sovcloud-usercontent.cn",
 "DOMAIN-SUFFIX,sovcloud-mx.cn",
 "DOMAIN-SUFFIX,portal.partner.microsoftonline.cdnsvc.com",
 "DOMAIN-SUFFIX,chinacloudapi.cn",
 "DOMAIN-SUFFIX,chinacloudapp.cn",
 "DOMAIN-SUFFIX,chinacloud-mobile.cn",
 "DOMAIN-SUFFIX,azure-mobile.cn",
 "DOMAIN-SUFFIX,windowsazure.cn",
 "DOMAIN-SUFFIX,azure.cn",
 "DOMAIN-SUFFIX,azconfig.azure.cn",
 "DOMAIN-SUFFIX,azurehdinsight.cn",
 "DOMAIN-SUFFIX,microservices.azure.cn",
 "DOMAIN-SUFFIX,azurecontainerapps-dev.cn",
 "DOMAIN-SUFFIX,botframework.azure.cn",
 "DOMAIN-SUFFIX,vault.azure.cn",
 "DOMAIN-SUFFIX,signalr.azure.cn",
 "DOMAIN-SUFFIX,timeseries.azure.cn",
 "DOMAIN-SUFFIX,joiner.i95.me",
 "DOMAIN-SUFFIX,au.i95.me",
 "DOMAIN-SUFFIX,556902.xyz",
 "DOMAIN-SUFFIX,jollytoday.com",
 "DOMAIN-SUFFIX,hyjidi.com",
 "DOMAIN-SUFFIX,xiaodecheji.com",
 "DOMAIN-SUFFIX,okcaros.com",
 "DOMAIN-SUFFIX,ping0.cc",
 "DOMAIN-SUFFIX,ippure.com",
 "DOMAIN-SUFFIX,ipkk.com",
 "DOMAIN-SUFFIX,whoer.net",
 "DOMAIN-SUFFIX,wyctt.com",
 "DOMAIN-SUFFIX,medeyun.com",
 "DOMAIN-SUFFIX,mede.com",
 "DOMAIN-SUFFIX,gdmd.com",
 "DOMAIN-SUFFIX,os.medeyun.com",
 "DOMAIN-SUFFIX,mede.vip",
 "DOMAIN-SUFFIX,mede.cn",
 "DOMAIN-SUFFIX,one.alimama.com",
 "DOMAIN-SUFFIX,alimama.com",
 "DOMAIN-SUFFIX,one.alimama.com",
 "DOMAIN-SUFFIX,mmstat.com",
 "DOMAIN-SUFFIX,huzhou.host",
 "DOMAIN-SUFFIX,galaxyappstore.com",
 "DOMAIN-SUFFIX,Samsung.com",
 "DOMAIN-SUFFIX,galaxy.com",
}
M.BASELINE_OMITTED={
 ["DOMAIN-SUFFIX,wyctt.com"]=true,
 ["DOMAIN-SUFFIX,medeyun.com"]=true,
 ["DOMAIN-SUFFIX,mede.com"]=true,
 ["DOMAIN-SUFFIX,gdmd.com"]=true,
 ["DOMAIN-SUFFIX,os.medeyun.com"]=true,
 ["DOMAIN-SUFFIX,mede.vip"]=true,
 ["DOMAIN-SUFFIX,mede.cn"]=true,
}

local function fail(code) error(code,0) end
local function valid(rule)
 local kind,host=rule:match("^(DOMAIN[^,]*),([^,]+)$")
 if kind~="DOMAIN" and kind~="DOMAIN-SUFFIX" then return false end
 if #host>253 or host:find("[^A-Za-z0-9%.%-]") or host:find("%.%.")
  or host:sub(1,1)=="." or host:sub(-1)=="." then return false end
 for label in host:gmatch("[^.]+") do
  if #label>63 or label:sub(1,1)=="-" or label:sub(-1)=="-" then return false end
 end
 return host~=""
end
-- Narrow reader for OpenClash's dumped inline/classical block, not a general YAML parser.
function M.parse(text)
 if type(text)~="string" or #text>4194304 then fail("direct-file-too-large-or-invalid") end
 local lines={}; for line in (text.."\n"):gmatch("(.-)\n") do lines[#lines+1]=line:gsub("\r$","") end
 local root
 for i,line in ipairs(lines) do
  if line=="rule-providers:" then
   if root then fail("direct-providers-ambiguous") end
   root=i
  end
 end
 if not root then fail("direct-providers-missing") end
 local first,last
 for i=root+1,#lines do
  local line=lines[i]
  if line:match("^%S") and not line:match("^#") then break end
  if line:match("^  Manual%-Direct:%s*$") then
   if first then fail("direct-provider-ambiguous") end
   first=i
  elseif first and line:match("^  %S") and not last then last=i-1 end
 end
 if not first then fail("direct-provider-missing") end
 if not last then
  last=#lines
  for i=first+1,#lines do
   if lines[i]:match("^%S") and not lines[i]:match("^#") then last=i-1; break end
  end
 end
 local inline,classical,payload=false,false,false
 local seen,rules={},{}
 for i=first+1,last do
  local line=lines[i]
  if line:match("^%s*$") or line:match("^%s*#") then
   -- Comments carry no rules.
  elseif line:match("^    type:%s*inline%s*$") then
   if seen.type then fail("direct-block-unsupported") end; seen.type=true; inline=true
  elseif line:match("^    behavior:%s*classical%s*$") then
   if seen.behavior then fail("direct-block-unsupported") end; seen.behavior=true; classical=true
  elseif line:match("^    payload:%s*$") then
   if payload then fail("direct-block-unsupported") end; payload=true
  else
   local value=line:match("^    %- (.+)$") or line:match("^      %- (.+)$")
   if not payload or not value then fail("direct-block-unsupported") end
   value=value:gsub("%s+#.*$",""):gsub("%s+$","")
   local quote=value:sub(1,1)
   if quote=="'" or quote=='"' then
    if value:sub(-1)~=quote then fail("direct-block-unsupported") end
    value=value:sub(2,-2)
   end
   if not valid(value) then fail("direct-rule-unsupported") end
   rules[#rules+1]=value
  end
 end
 if not inline or not classical or not payload or #rules==0 then fail("direct-block-unsupported") end
 return rules
end
local function same(a,b)
 if #a~=#b then return false end
 for i,v in ipairs(a) do if b[i]~=v then return false end end
 return true
end
function M.compare(current)
 local remaining={}; for _,v in ipairs(current) do remaining[v]=(remaining[v] or 0)+1 end
 local missing={}
 for _,v in ipairs(M.REFERENCE) do
  if (remaining[v] or 0)>0 then remaining[v]=remaining[v]-1 else missing[#missing+1]=v end
 end
 local extra=0; for _,n in pairs(remaining) do extra=extra+n end
 local baseline={}; for _,v in ipairs(M.REFERENCE) do if not M.BASELINE_OMITTED[v] then baseline[#baseline+1]=v end end
 return {referenceCount=#M.REFERENCE,referenceOnly=missing,currentOnlyCount=extra,
  currentCount=#current,matchesReferenceOrder=same(current,M.REFERENCE),
  matchesNov23Snapshot=same(current,baseline)}
end
function M.paths(uci)
 local raw=uci:get("openclash","config","config_path")
 local overrides=0
 uci:foreach("openclash","overwrite",function(section)
  if section.config_path~=nil then overrides=overrides+1; raw=section.config_path end
 end)
 if overrides>1 or type(raw)~="string" or raw:find("[%c]") or raw:find("..",1,true)
  or not raw:match("^/etc/openclash/[^/].+%.ya?ml$") then fail("direct-config-path-unconfirmed") end
 local basename=raw:match("([^/]+)$")
 if basename:sub(1,1)=="." then fail("direct-config-path-unconfirmed") end
 return raw,"/etc/openclash/"..basename
end
local function read(path)
 local f=io.open(path,"rb"); if not f then fail("direct-runtime-file-unavailable") end
 local data=f:read(4194305); f:close()
 if type(data)~="string" or #data>4194304 then fail("direct-file-too-large-or-invalid") end
 return data
end
function M.main(args)
 local available,json=pcall(require,"luci.jsonc")
 if not available then print("direct-json-unavailable"); return 1 end
 local ok,out=pcall(function()
  if #args~=0 then fail("direct-arguments-invalid") end
  local factory=require("luci.model.uci")
  local raw,path=M.paths(factory.cursor())
  local before=read(path)
  local result=M.compare(M.parse(before))
  local raw2,path2=M.paths(factory.cursor())
  if raw2~=raw or path2~=path or read(path2)~=before then fail("direct-file-or-config-changed") end
  result.inspectionComplete=true
  result.fileReadTwiceSame=true
  return result
 end)
 if not ok then
  out={inspectionComplete=false,error=type(out)=="string" and
   out:match("^direct%-[a-z%-]+$") and out or "direct-inspection-failed"}
 end
 out.mode="direct-file-readonly"
 out.referenceCommit="5ae361f2ea6ae9adc06956491476da6c4203ad1b"
 out.referenceDate,out.baselineDate="2026-11-24","2026-11-23"
 out.readOnly,out.fileWrites,out.apiRequests,out.probeRequests=true,0,0,0
 out.selectionApplied,out.configurationWritten,out.formalAcceptance=false,false,false
 out.runtimeFileSnapshotOnly,out.activeCoreConfigurationVerified=true,false
 print(json.stringify(out))
 return ok and 0 or 1
end
if (...)=="__library_only" then return M end
os.exit(M.main(arg or {}))
