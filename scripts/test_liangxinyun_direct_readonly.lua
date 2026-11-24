-- Actual Lua, read/JSON/UCI interfaces substituted; no API or OS writes.
local M=assert(loadfile(assert(arg[1])))("__library_only")
local count=0
local function eq(a,b,label) count=count+1; assert(a==b,(label or '')..': '..tostring(a)..' ~= '..tostring(b)) end
local function text(items,indent)
 local out='rule-providers:\n  Manual-Direct:\n    type: inline\n    behavior: classical\n    payload:\n'
 for _,v in ipairs(items) do out=out..(indent or '    ')..'- '..v..'\n' end
 return out..'  other:\n    type: http\nproxy-groups: []\n'
end
local rules=M.parse(text({'DOMAIN-SUFFIX,example.com','DOMAIN,api.example.com','DOMAIN-SUFFIX,example.com'}))
eq(#rules,3); eq(rules[1],rules[3]); eq(rules[2],'DOMAIN,api.example.com')
eq(M.parse(text({'"DOMAIN-SUFFIX,example.com"'},'      '))[1],'DOMAIN-SUFFIX,example.com')
eq(M.parse(text({"'DOMAIN,api.example.com' # comment"}))[1],'DOMAIN,api.example.com')
local baseline={}
for _,v in ipairs(M.REFERENCE) do if not M.BASELINE_OMITTED[v] then baseline[#baseline+1]=v end end
local report=M.compare(M.parse(text(baseline)))
eq(report.matchesNov23Snapshot,true); eq(report.currentOnlyCount,0)
eq(report.matchesReferenceOrder,false)
for _,v in ipairs(report.referenceOnly) do eq(M.BASELINE_OMITTED[v],true) end
report=M.compare(M.REFERENCE); eq(report.matchesReferenceOrder,true); eq(#report.referenceOnly,0)
local extra={}; for i,v in ipairs(baseline) do extra[i]=v end; extra[#extra+1]='DOMAIN,private.invalid'
report=M.compare(extra); eq(report.currentOnlyCount,1)
for _,v in ipairs(report.referenceOnly) do eq(v~='DOMAIN,private.invalid',true) end
local unsupported={
 '', 'rule-providers:\n  Manual-Direct: *alias\n',
 text({'DOMAIN-SUFFIX,example.com'})..'rule-providers:\n',
 text({'DOMAIN-SUFFIX,example.com'}):gsub('    type: inline','    type: http'),
 text({'DOMAIN-SUFFIX,example.com'}):gsub('    behavior: classical','    behavior: domain'),
 text({'DOMAIN-SUFFIX,example.com'}):gsub('    payload:','    payload: &anchor'),
 text({'DOMAIN-SUFFIX,example.com'}):gsub('    payload:','    payload:\n    payload:'),
 text({'DOMAIN-SUFFIX,example.com'}):gsub('  other:','  Manual-Direct:'),
 text({'DOMAIN-SUFFIX,example.com'}):gsub('    payload:','    unexpected: value\n    payload:'),
 text({'DOMAIN-SUFFIX,example.com,DIRECT'}), text({'DOMAIN-SUFFIX,https://secret.invalid'}),
 text({'DOMAIN-SUFFIX,a..com'}),text({'DOMAIN,-invalid.com'}),text({'!ruby/object:Secret'}),
 text({'DOMAIN-SUFFIX,example.com'},'\t'),text({}),
}
for _,value in ipairs(unsupported) do eq(pcall(M.parse,value),false) end
local function uci(raw,override)
 return {get=function(_,p,s,k) eq(p,'openclash'); eq(s,'config'); eq(k,'config_path'); return raw end,
 foreach=function(_,p,s,fn) eq(p,'openclash'); eq(s,'overwrite'); for _,v in ipairs(override or {}) do fn(v) end end}
end
local raw,path=M.paths(uci('/etc/openclash/config/iKuuu.yaml'))
eq(raw,'/etc/openclash/config/iKuuu.yaml'); eq(path,'/etc/openclash/iKuuu.yaml')
for _,value in ipairs({'/tmp/secret.yaml','/etc/openclash/config/../a.yaml','/etc/openclash/.a.yaml','/etc/openclash/config/a.conf','/etc/openclash/a.yaml\n'}) do
 eq(pcall(M.paths,uci(value)),false)
end
eq(pcall(M.paths,uci(raw,{{config_path=raw},{config_path=raw}})),false)
local oldOpen,oldPrint=io.open,print
local oldJson,oldUci=package.loaded['luci.jsonc'],package.loaded['luci.model.uci']
local output,reads=nil,0
package.loaded['luci.jsonc']={stringify=function(value) output=value; return 'fixture-json' end}
package.loaded['luci.model.uci']={cursor=function() return uci(raw) end}
print=function() end
io.open=function(name,mode)
 eq(name,path); eq(mode,'rb'); reads=reads+1
 return {read=function(_,size) eq(size,4194305); return text(baseline) end,close=function() return true end}
end
eq(M.main({}),0); eq(reads,2); eq(output.matchesNov23Snapshot,true)
eq(output.readOnly,true); eq(output.apiRequests,0); eq(output.fileWrites,0)
eq(output.probeRequests,0); eq(output.configurationWritten,false)
eq(output.runtimeFileSnapshotOnly,true); eq(output.activeCoreConfigurationVerified,false)
reads=0; eq(M.main({'--apply'}),1); eq(reads,0); eq(output.inspectionComplete,false)
io.open=function() return nil,'sensitive-private-error' end
eq(M.main({}),1); eq(output.error,'direct-runtime-file-unavailable')
local changed=0
io.open=function() return {read=function() changed=changed+1; return text(baseline)..string.rep('#',changed) end,close=function() return true end} end
eq(M.main({}),1); eq(output.error,'direct-file-or-config-changed')
io.open,print=oldOpen,oldPrint
package.loaded['luci.jsonc'],package.loaded['luci.model.uci']=oldJson,oldUci
print('PASS direct file read-only assertions: '..count..' (interfaces substituted)')
