#!/usr/bin/env python3
# Run AFTER generate_hub2.py. Applies the accumulating actuals_log.json (per scoring period)
# into the matchup (per-day per-player actual points) + the Projection Accuracy log.
import json, os
SP0=97  # MP14 day-1 scoring period (Mon Jun 29). Updated weekly by the refresh task.
if not os.path.exists("actuals_log.json"):
    print("no actuals_log.json"); raise SystemExit
log=json.load(open("actuals_log.json"))
d=json.load(open("hub_data.json")); m=d["matchup"]; acc=d["accuracy"]
def apply(sp,side,key):
    idx=int(sp)-SP0
    if not (0<=idx<7): return
    pl={str(k):v for k,v in side.get("players",{}).items()}
    for arr in (m[key]["hitters"],m[key]["pitchers"]):
        for p in arr:
            if str(p["id"]) in pl: p["actual"][idx]=pl[str(p["id"])]
    for spk,pts in side.get("day",{}).items():
        i2=int(spk)-SP0
        if 0<=i2<7: m["actualTeam"][key][i2]=round(pts)
        if key=="me" and 0<=i2<len(acc["dayByDay"]): acc["dayByDay"][i2]["actual"]=round(pts)
for sp,entry in log.items():
    apply(sp,entry["me"],"me"); apply(sp,entry["opp"],"opp")
m["hasActuals"]=any(x is not None for x in m["actualTeam"]["me"])
played=[x["actual"] for x in acc["dayByDay"] if x["actual"] is not None]
if len(played)>=7:
    tot=sum(played); w=acc["weekByWeek"][0]; w["actual"]=tot; w["err"]=tot-w["proj"]
    w["acc"]=round(100-abs(w["err"])/tot*100) if tot else None
json.dump(d,open("hub_data.json","w"))
print("injected days:", [i for i,x in enumerate(m['actualTeam']['me']) if x is not None], "| my totals", m["actualTeam"]["me"])
