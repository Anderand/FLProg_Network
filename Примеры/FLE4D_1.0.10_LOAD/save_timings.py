from pathlib import Path
import json,re
p=Path(r'E:\SAI\FLProg_Network\_work\load_fle4d\BROWSER_TIMINGS.json');p.write_text(json.dumps({'cold_ms':2448,'warm_ms':[1406,1765,1393,1373,1119],'timing_scope':'inline root bootstrap to metadata, widgets and first state; excludes TCP navigation before HTML execution'},indent=2),encoding='utf-8')
