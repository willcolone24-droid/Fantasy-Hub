#!/usr/bin/env python3
# Applies actuals_log.json (per scoring period) into the matchup + Projection Accuracy.
# SP0 (day-1 scoring period) is derived from the log, so it self-adjusts each matchup week.
import json, os
if not os.path.exists("actuals_log.json"):
    print("no actuals_log.json"); raise SystemExit
log=json.load(open("actuals_log.json"))
if not log:
    print("empty actuals_log"); raise SystemExit
SP0=min(int(k) for k in log)
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
for sp,entry in sorted(log.items(), key=lambda kv:int(kv[0])):
    apply(sp,entry["me"],"me"); apply(sp,entry["opp"],"opp")
m["hasActuals"]=any(x is not None for x in m["actualTeam"]["me"])
played=[x["actual"] for x in acc["dayByDay"] if x["actual"] is not None]
if len(played)>=7:
    tot=sum(played); w=acc["weekByWeek"][0]; w["actual"]=tot; w["err"]=tot-w["proj"]
    w["acc"]=round(100-abs(w["err"])/tot*100) if tot else None
json.dump(d,open("hub_data.json","w"))
print("injected; my daily actuals:", m["actualTeam"]["me"])
