#!/usr/bin/env python3
"""Cloud build: pulls live ESPN data (auth via ESPN_S2 + SWID secrets), refreshes
actuals/scores, rebuilds the hub into index.html for GitHub Pages.
Runs headless in GitHub Actions — no browser needed (cookie-authenticated HTTP)."""
import os, json, subprocess, urllib.request, urllib.error

S2  = os.environ.get("ESPN_S2","").strip()
SWID= os.environ.get("SWID","").strip()
LEAGUE, SEASON, TEAM = "622960213", "2026", 4
SP0 = 97  # MP14 day-1 scoring period; bump by 7 each new matchup period (see SETUP.md)
BASE=f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/{SEASON}/segments/0/leagues/{LEAGUE}"

def get(params):
    req=urllib.request.Request(BASE+params, headers={
        "Cookie": f"espn_s2={S2}; SWID={SWID}",
        "User-Agent":"Mozilla/5.0", "Accept":"application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)

def main():
    if not S2 or not SWID:
        print("WARNING: ESPN_S2/SWID not set — rebuilding from committed data only.")
    else:
        try:
            s=get("?view=mSettings"); cur=s["scoringPeriodId"]; mp=s["status"]["currentMatchupPeriod"]
            j=get(f"?view=mMatchupScore&view=mBoxscore&scoringPeriodId={cur}&matchupPeriodId={mp}")
            g=next(x for x in j.get("schedule",[]) if x.get("matchupPeriodId")==mp and
                   ((x.get("home") or {}).get("teamId")==TEAM or (x.get("away") or {}).get("teamId")==TEAM))
            def grab(side):
                ent=((side.get("rosterForCurrentScoringPeriod") or {}).get("entries")) or []
                players={}
                for e in ent:
                    pp=e.get("playerPoolEntry") or {}
                    if pp.get("appliedStatTotal") is not None:
                        players[str(pp["id"])]=round(pp["appliedStatTotal"]*10)/10
                return {"day":side.get("pointsByScoringPeriod") or {}, "players":players}
            me = g["home"] if g["home"]["teamId"]==TEAM else g["away"]
            op = g["away"] if g["home"]["teamId"]==TEAM else g["home"]
            log={}
            if os.path.exists("actuals_log.json"):
                log=json.load(open("actuals_log.json"))
            log[str(cur)]={"me":grab(me),"opp":grab(op)}
            json.dump(log, open("actuals_log.json","w"))
            print(f"pulled actuals: SP={cur} MP={mp} me={me.get('pointsByScoringPeriod')} opp={op.get('pointsByScoringPeriod')}")
        except (urllib.error.HTTPError, urllib.error.URLError, StopIteration, KeyError) as e:
            print("ESPN pull failed (cookies expired? off-season?):", e, "— rebuilding from committed data.")

    subprocess.run(["python3","generate_hub2.py"], check=True)
    subprocess.run(["python3","inject_actuals.py"], check=True)
    d=json.load(open("hub_data.json"))
    html=open("site2.html").read().replace("--mut:#8severe;","").replace("/*__DATA__*/null", json.dumps(d))
    open("index.html","w").write(html)
    print("built index.html (", len(html), "bytes )")

if __name__=="__main__":
    main()
