from pathlib import Path
import json,re
W=Path(r'E:\SAI\FLProg_Network\_work\load_fle4d');p=W/'BROWSER_TIMINGS.json';d=json.loads(p.read_text());d['warm_after_stress_ms']=[1694,979,1241,1237,993,1249,1376,1230,1003,999];d['warm_after_stress_navigation_ms']=991;p.write_text(json.dumps(d,indent=2),encoding='utf-8')
log=(W/'uart.log').read_text(encoding='utf-8-sig',errors='replace');rows=[tuple(map(int,m)) for m in re.findall(r'1.0.10-LOAD #\d+ ms=(\d+).*?HEAP_USED=(\d+) HEAP_ARENA_FREE=(\d+)',log)]
assert rows
r={'samples':len(rows),'first_ms':rows[0][0],'last_ms':rows[-1][0],'used_min':min(x[1]for x in rows),'used_max':max(x[1]for x in rows),'used_last':rows[-1][1],'arena_free_last':rows[-1][2]};(W/'HEAP_VERIFICATION.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(r)
