#!/usr/bin/env python3
import json
import league_full as L

ELAPSED=85.0; REM=102.0
def n(x):
    x=x.strip()
    if x in ("NaN",""): return None
    try: return float(x) if "." in x else int(x)
    except: return None

def myros(std,l30,l15):
    rates=[];wts=[]
    if std is not None: rates.append(std/ELAPSED);wts.append(.45)
    if l30 is not None: rates.append(l30/30.0);wts.append(.35)
    if l15 is not None: rates.append(l15/15.0);wts.append(.20)
    if not rates: return 0
    rate=sum(r*w for r,w in zip(rates,wts))/sum(wts)
    return max(0,round(rate*REM))

def trend(std,l30,l15):
    rec = l15 if l15 is not None else l30
    recd = 15.0 if l15 is not None else 30.0
    if rec is None or std is None or std<=0: return "steady"
    rr=rec/recd; sr=std/ELAPSED
    if sr<=0: return "steady"
    r=rr/sr
    return "hot" if r>1.18 else "cold" if r<0.82 else "steady"

def pct(a,b): return round(a/b*100,1) if b else 0

players=[]
for line in L.HITTERS.strip().splitlines():
    f=line.split("|"); v=[f[0],f[1],f[2],f[3],f[4],f[5]]+[n(x) for x in f[6:]]
    pid,name,mlb,ft,pos,inj,std,l30,l15,l7,PA,AB,AVG,OBP,SLG,HR,R,RBI,BB,SB,K=v
    PA=PA or 0
    players.append(dict(id=pid,name=name,mlb=mlb,ft=ft,pos=pos,inj="" if inj=="OK" else inj,type="H",
        std=std,l30=l30,l15=l15,l7=l7,myros=myros(std,l30,l15),trend=trend(std,l30,l15),
        st={"PA":PA,"AB":AB,"AVG":AVG,"OBP":OBP,"SLG":SLG,"OPS":round((OBP or 0)+(SLG or 0),3),
            "HR":HR,"R":R,"RBI":RBI,"BB":BB,"SB":SB,"K":K,
            "ISO":round((SLG or 0)-(AVG or 0),3),"BB%":pct(BB or 0,PA),"K%":pct(K or 0,PA)}))
for line in L.PITCHERS.strip().splitlines():
    f=line.split("|"); v=[f[0],f[1],f[2],f[3],f[4],f[5]]+[n(x) for x in f[6:]]
    pid,name,mlb,ft,pos,inj,std,l30,l15,l7,GS,IP,ERA,WHIP,K9,K,W,Ln,SV,HD,BB,H=v
    IP=IP or 0
    players.append(dict(id=pid,name=name,mlb=mlb,ft=ft,pos=pos,inj="" if inj=="OK" else inj,type="P",
        std=std,l30=l30,l15=l15,l7=l7,myros=myros(std,l30,l15),trend=trend(std,l30,l15),
        st={"GS":GS,"IP":IP,"ERA":ERA,"WHIP":WHIP,"K9":K9,"K":K,"W":W,"L":Ln,"SV":SV,"HD":HD,
            "K/BB":round((K or 0)/BB,2) if BB else (K or 0),"BB9":round((BB or 0)/IP*9,2) if IP else 0,
            "H9":round((H or 0)/IP*9,2) if IP else 0}))

# tier by myros
def tier(m):
    return "Elite" if m>=230 else "Strong" if m>=185 else "Solid" if m>=145 else "Role" if m>=100 else "Bench"
for p in players: p["tier"]=tier(p["myros"])

TEAMS={"Beer":("ICECOLDBEERHERE","10-3","East",99),"GOON":("Bronze Beaters","8-4-1","West",85),
 "DDT":("Trash can beaters","8-5","East",15),"SSs":("Troll Toll For The Boys Hole","8-5","West",44),
 "CT":("Chubbyville Tubbster","6-6-1","East",15),"OBP":("ObiWan KenoLee","6-7","East",47),
 "GGT":("Garrett's Great Team","7-6","West",60),"WWT":("Will's Wild Team","6-7","West",35),
 "Gav":("Reaper's Playground","4-9","East",1),"SUFF":("You Need A Tennis Racket","1-12","West",0)}
STREAK={"Beer":"W5","GOON":"W1","DDT":"W1","SSs":"L1","CT":"L3","OBP":"L5","GGT":"L1","WWT":"W2","Gav":"W2","SUFF":"L11"}
PF={"Beer":3720,"GOON":3644,"DDT":3123,"SSs":3183,"CT":3253,"OBP":3586,"GGT":3455,"WWT":3308,"Gav":3171,"SUFF":2571}
PA_={"Beer":3176,"GOON":3274,"DDT":3017,"SSs":3099,"CT":3341,"OBP":3504,"GGT":3412,"WWT":3299,"Gav":3290,"SUFF":3602}

# power rankings by MyROS (best 9 H + 7 P among rostered)
teamrows=[]
for code,(nm,rec,div,po) in TEAMS.items():
    hs=sorted([p for p in players if p["ft"]==code and p["type"]=="H"],key=lambda r:-r["myros"])
    ps=sorted([p for p in players if p["ft"]==code and p["type"]=="P"],key=lambda r:-r["myros"])
    hit=sum(p["myros"] for p in hs[:9]); pit=sum(p["myros"] for p in ps[:7])
    teamrows.append(dict(code=code,name=nm,rec=rec,div=div,po=po,streak=STREAK[code],pf=PF[code],pa=PA_[code],
        hit=hit,pit=pit,total=hit+pit,status="SELLER" if code in("Gav","SUFF") else "BUYER",
        best=(hs+ps and max(hs+ps,key=lambda r:r["myros"])["name"])))
teamrows.sort(key=lambda t:-t["total"])
for i,t in enumerate(teamrows,1): t["rank"]=i

alerts=[
 ("good","You're 6-7 (7th seed) and HOT - won your last two (W2). The 4th playoff spot is 4 games back with 8 weeks left; a strong run puts you right in it."),
 ("buy","MP14 is vs Reaper's Playground (4-9) - your softest matchup. MUST-WIN. Lean into pitching volume: you roster THREE two-start arms this week (E-Rod, Eury Perez, Gage Jump)."),
 ("warn","ACTIVATE Eury Perez - he's sitting in your IL slot but he's healthy and has TWO starts this week (Tue @COL, Sun @ATH). Move him to a P slot or you lose those starts."),
 ("buy","Gage Jump has rounded into form (L30 75) and has TWO starts this week (vLAD, vMIA) - start him, don't drop him. Want more pitching? Sean Burke (FA) is a clean two-start streamer (@BAL, @CLE) over a cold arm."),
 ("good","Roster moves paid off: Brooks Lee (197) fills the 3B hole and Robbie Ray (182) adds strikeouts. Yelich and Riley are gone. Your core - Wood, Ohtani, Gilbert, Reynolds, Abrams - is genuinely strong."),
]
schedule=[(14,"Reaper's Playground (4-9)","Easy","MUST-WIN"),(15,"ObiWan KenoLee (6-7)","Toss-up","Leverage"),
 (16,"Chubbyville (6-6-1)","Toss-up","Leverage"),(17,"Tennis Racket (1-12)","Easy","MUST-WIN"),
 (18,"ICECOLDBEERHERE (10-3)","Hard","Steal it"),(19,"Trash can beaters (8-5)","Hard","Compete"),
 (20,"Garrett's Great Team (7-6)","Toss-up","MUST-WIN"),(21,"Bronze Beaters (8-4-1)","Hard","Finale")]
actionPlan={"TODAY":["Win MP14 vs Reaper's (4-9) - your easiest game; it gets you to 7-7.",
   "Activate Eury Perez off IL (he's healthy, 2 starts this week).",
   "Stream Sean Burke (FA, two starts @BAL/@CLE) if you open a slot from a cold arm - Gage Jump is hot now and stays.",
   "Set your strong nine: Wood, Ohtani(DH), Alonso, Abrams, Turang, Brooks Lee, Moreno, Reynolds, Chourio."],
 "THIS WEEK":["Start every two-start arm you roster: E-Rod (vSF, vMIL), Eury Perez (@ATH), Gage Jump (vLAD, vMIA - hot).",
   "Bench Robbie Ray this week - his lone start is @COL (Coors); hold him for ROS strikeouts.",
   "Single-start arms all go: Kirby (vLAA), Ohtani (@ATH), Valdez (@TEX). Check Friday for Gilbert's weekend start.",
   "Keep Williams + Baker active all week for saves."],
 "ALL SEASON":["Win the soft spots: Reaper's (MP14), Tennis Racket (MP17) are must-wins.",
   "Stream pitchers every week - fill all 7 P slots with arms that throw; chase innings + Ks.",
   "MP20 vs Garrett (7-6) is your season swing game - both fighting for the same spot.",
   "Target 9-1 down the stretch to reach ~15 wins and steal the 4th seed."]}
# Yelich-centered ideas; verdicts are computed live in the bot from MyROS
tradeIdeas=[
 (["Christian Yelich"],["Cade Smith"],"Chubbyville","Sell a DH-only bat (UTIL-locked) for an elite reliever banking saves + Ks; they need the bat."),
 (["Christian Yelich"],["Drew Rasmussen"],"OBP Kwanobi","OBP is thin in the OF and SP-rich; you add rotation innings."),
 (["Bryan Reynolds"],["Cristopher Sanchez"],"Chubbyville","Reynolds is above his level; Sanchez is a workhorse SP - innings win points leagues."),
 (["Christian Yelich","Bryan Reynolds"],["Cade Smith","Ranger Suarez"],"Chubbyville","Turn an OF/UTIL surplus into a closer + a starter; upgrades two active slots."),
]
trollDeal={"title":"Brother Troll's offer: you give Gilbert + Greene, you get Jordan Walker",
 "verdict":"REJECT - you'd ship your ace for a part-time bat. Load it below and the bot will show how lopsided it is.",
 "counters":["Keep Gilbert - your most valuable arm.","Offer Yelich instead (he only fits UTIL and is blocked).",
   "Yelich -> MacKenzie Gore is the closest-to-fair brotherly swap (you get SP innings).",
   "If Gilbert must be in it, demand Alex Bregman (fixes 3B) - not Walker."]}


# ===================== PROJECTION ENGINE (daily + weekly) =====================
import math as _math
DAYS=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
def _k(full):
    p=(full or "").split(); return (p[0][0]+"."+p[-1]).lower() if p else ""
# live ESPN probables: 2-start board + my known 1-start arms -> start day indices
_TWO=[("A. Nola",["Mon","Sun"]),("B. Ashcraft",["Mon","Sat"]),("B. Chandler",["Tue","Sun"]),
 ("C. Mize",["Mon","Sun"]),("E. Fedde",["Tue","Sun"]),("E. Lauer",["Mon","Sun"]),("E. Perez",["Tue","Sun"]),
 ("E. Rodriguez",["Mon","Sun"]),("G. Jax",["Tue","Sun"]),("G. Jump",["Mon","Sun"]),("J. Sears",["Tue","Sun"]),
 ("M. Liberatore",["Tue","Sun"]),("M. Mikolas",["Mon","Sun"]),("M. Perez",["Tue","Sun"]),("N. Lodolo",["Mon","Sat"]),
 ("P. Lambert",["Mon","Sun"]),("P. Messick",["Mon","Sat"]),("R. Gasser",["Mon","Sun"]),("R. Johnson",["Mon","Sun"]),
 ("R. Lowder",["Tue","Sun"]),("R. Suarez",["Mon","Sun"]),("R. Weathers",["Mon","Sun"]),("S. Alcantara",["Mon","Sat"]),
 ("S. Burke",["Mon","Sat"]),("S. Imanaga",["Mon","Sun"])]
_ONE=[("G. Kirby",["Mon"]),("F. Valdez",["Thu"]),("S. Ohtani",["Wed"]),("R. Ray",["Sat"]),("W. Urena",["Thu"]),
 ("A. Pallante",["Fri"]),("Z. Gallen",["Wed"]),("A. Abbott",["Wed"]),("M. Keller",["Fri"]),("N. Cameron",["Tue"]),
 ("W. Buehler",["Wed"]),("A. Kay",["Fri"]),("S. Gray",["Sat"]),("J. deGrom",["Tue"]),("N. Eovaldi",["Wed"]),
 ("M. Wacha",["Thu"]),("J. Ginn",["Fri"]),("P. Tolle",["Sat"]),("J. Wrobleski",["Fri"])]
START_DAYS={nm.replace(" ","").lower():[DAYS.index(d) for d in ds] for nm,ds in _TWO+_ONE}

def project(p):
    perDay=p["myros"]/102.0
    pos=p.get("pos") or ""
    k=_k(p["name"])
    if p["type"]=="P":
        isSP=("SP" in pos) or (pos=="P")
        days=START_DAYS.get(k)
        if isSP:
            starts=len(days) if days else 1
            perStart=perDay*7/1.1
            wk=perStart*starts
            p["startsWk"]=starts; p["startDays"]=days or []; p["perStart"]=round(perStart)
        else:
            wk=perDay*7
            p["startsWk"]=0; p["startDays"]=[]; p["perStart"]=None
    else:
        wk=perDay*7
        p["startsWk"]=None; p["startDays"]=[]; p["perStart"]=None
    p["projWk"]=round(wk); p["projDay"]=round(wk/7,1)
for p in players: project(p)

def daily_vec(p):
    v=[0.0]*7; wk=p["projWk"]
    if p["type"]=="P" and (("SP" in (p.get("pos") or "")) or (p.get("pos")=="P")):
        ds=p["startDays"]
        if ds:
            per=wk/len(ds)
            for d in ds: v[d]+=per
        else:
            v[3]+=wk  # unknown start -> assume one mid-week start
    else:
        for d in range(7): v[d]+=wk/7.0
    return v

def ACTIVE_OUT(p): return any(x in (p.get("inj") or "") for x in ("SIXTY","TEN_DAY"))
PSLOTS=8

def slim(p,slot=None):
    if p is None:
        return {"id":0,"name":"(open)","mlb":"","pos":"","type":"H","projWk":0,"projDay":0,"trend":"steady","myros":0,"std":0,"l30":0,"inj":"","slot":slot}
    d={"id":p["id"],"name":p["name"],"mlb":p["mlb"],"pos":p["pos"],"type":p["type"],
       "projWk":p["projWk"],"projDay":p["projDay"],"trend":p["trend"],"myros":p["myros"],
       "std":p["std"],"l30":p["l30"],"inj":p.get("inj","")}
    d["daily"]=[round(x,1) for x in daily_vec(p)]
    if p["type"]=="P":
        d["starts"]=p.get("startsWk"); d["days"]=[DAYS[x] for x in p.get("startDays",[])]; d["perStart"]=p.get("perStart")
    if slot: d["slot"]=slot
    return d

def build_hitters(code):
    hs=[p for p in players if p["ft"]==code and p["type"]=="H" and not ACTIVE_OUT(p)]
    slots=["C","1B","2B","3B","SS","OF","OF","OF"]
    def elig(p,slot):
        pos=(p.get("pos") or "").split("/")
        return ("OF" in pos) if slot=="OF" else (slot in pos)
    n=len(hs)
    em=[[elig(hs[j],slots[i]) for j in range(n)] for i in range(len(slots))]
    memo={}
    def rec(i,mask):
        if i==len(slots): return (0,[])
        key=(i,mask)
        if key in memo: return memo[key]
        bv,ba=rec(i+1,mask)              # leave slot open
        best=(bv,[None]+ba)
        for j in range(n):
            if em[i][j] and not (mask>>j)&1:
                v,asg=rec(i+1,mask|(1<<j))
                tot=hs[j]["projWk"]+v
                if tot>best[0]: best=(tot,[hs[j]]+asg)
        memo[key]=best; return best
    _,assign=rec(0,0)
    disp=list(zip(slots,assign))
    used=set(id(p) for p in assign if p)
    benchH=[p for p in sorted(hs,key=lambda r:-r["projWk"]) if id(p) not in used]
    return disp,benchH

def arms(code): return [p for p in players if p["ft"]==code and p["type"]=="P" and not ACTIVE_OUT(p)]

def hit_daily(H):
    daily=[0.0]*7
    for s,p in H:
        if not p: continue
        v=daily_vec(p)
        for d in range(7): daily[d]+=v[d]
    return daily

def pitch_daily_opt(ps):
    daily=[0.0]*7; perp={id(p):daily_vec(p) for p in ps}
    for d in range(7):
        daily[d]=sum(sorted([perp[id(p)][d] for p in ps],reverse=True)[:PSLOTS])
    return daily

def team_full(code):
    H,benchH=build_hitters(code); ps=arms(code)
    hd=hit_daily(H); pd=pitch_daily_opt(ps)
    return H,ps,benchH,hd,pd,round(sum(hd)),round(sum(pd))

for t in teamrows:
    H,ps,bH,hd,pd,hw,pw=team_full(t["code"])
    t["projWk"]=hw+pw; t["projDay"]=round((hw+pw)/7,1); t["projHit"]=hw; t["projPit"]=pw

OPP="Gav"
mH,mPs,mBench,mHd,mPd,mHit,mPit=team_full("WWT")
oH,oPs,oBench,oHd,oPd,oHit,oPit=team_full(OPP)
mTot=mHit+mPit; oTot=oHit+oPit; margin=mTot-oTot
winMe=round(1/(1+_math.exp(-margin/55.0))*100)

slotEdges=[]
for (s1,a),(s2,b) in zip(mH,oH):
    av=a["projWk"] if a else 0; bv=b["projWk"] if b else 0
    slotEdges.append({"slot":s1,"me":(slim(a) if a else slim(None,s1)),"opp":(slim(b) if b else slim(None,s2)),
        "win":("me" if av>bv+1 else "opp" if bv>av+1 else "even")})

def cum(v):
    out=[]; r=0
    for x in v: r+=x; out.append(round(r))
    return out
meDaily=[round(mHd[i]+mPd[i]) for i in range(7)]; opDaily=[round(oHd[i]+oPd[i]) for i in range(7)]
meCum=cum(meDaily); opCum=cum(opDaily)

mP=sorted(mPs,key=lambda r:-r["projWk"]); oP=sorted(oPs,key=lambda r:-r["projWk"])
twoMe=[slim(p) for p in mP if (p.get("startsWk") or 0)>=2]; twoOpp=[slim(p) for p in oP if (p.get("startsWk") or 0)>=2]

def bench_list(code,benchH):
    L=[]
    for p in benchH:
        d=slim(p); d["status"]="BENCH (daily swap)"; L.append(d)
    for p in players:
        if p["ft"]==code and ACTIVE_OUT(p):
            d=slim(p); d["status"]=(p.get("inj") or "OUT").replace("_"," ").title(); L.append(d)
    return L
mBenchL=bench_list("WWT",mBench); oBenchL=bench_list(OPP,oBench)

def edge_count(side): return sum(1 for e in slotEdges if e["win"]==side)
ins=[]
ins.append(f"You project <b>{mTot}</b> pts vs <b>{oTot}</b> — a <b>{'+' if margin>=0 else ''}{margin}</b> edge and a <b>{winMe}%</b> win projection (best daily lineup from your full roster).")
ins.append(f"Pitching is {'your edge' if mPit>oPit else 'the soft spot'}: <b>{mPit}</b> vs <b>{oPit}</b>. With 8 P slots and daily swaps you rotate <b>{len(mPs)}</b> arms through the week — two-start guys: {', '.join(p['name'] for p in twoMe) or '—'}.")
ins.append(f"Hitting slots: you win <b>{edge_count('me')}</b>, they win <b>{edge_count('opp')}</b>, {edge_count('even')} even. Note: no UTIL/DH slot, so DH-only bats can't start (it costs them Schwarber).")
hot_opp=sorted([p for s,p in oH if p],key=lambda r:-(r['l30'] or 0))[:2]
ins.append("Watch their hot bats: "+", ".join(f"{p['name']} (L30 {p['l30']})" for p in hot_opp)+". Field your best eight every day.")
ins.append("Daily edge: set your lineup every morning - start the arms pitching that day and swap your bench bat in for anyone resting. That's how you bank the full projection.")

def teamhdr(code):
    t=[x for x in teamrows if x["code"]==code][0]; return {"code":code,"name":t["name"],"rec":t["rec"]}

matchup={"mp":14,"week":"Mon Jun 29 – Sun Jul 5","live":"0.0 – 0.0 (week just started)",
 "me":{**teamhdr("WWT"),"proj":mTot,"hit":mHit,"pit":mPit,"hitters":[slim(p,s) for s,p in mH],"pitchers":[slim(p) for p in mP],"bench":mBenchL},
 "opp":{**teamhdr(OPP),"proj":oTot,"hit":oHit,"pit":oPit,"hitters":[slim(p,s) for s,p in oH],"pitchers":[slim(p) for p in oP],"bench":oBenchL},
 "winMe":winMe,"winOpp":100-winMe,"margin":margin,
 "slotEdges":slotEdges,"twoStartMe":twoMe,"twoStartOpp":twoOpp,
 "dayRace":{"days":DAYS,"meDaily":meDaily,"meCum":meCum,"oppDaily":opDaily,"oppCum":opCum},
 "insights":ins}
# ===================== END ENGINE =====================


# ===================== ANALYTICS ENGINE =====================
import statistics as _st
from collections import defaultdict as _dd

def _primary(p):
    pos=(p.get("pos") or "").split("/")
    if p["type"]=="P": return "SP" if "SP" in pos else "RP"
    for o in ["C","SS","2B","3B","1B","OF","DH"]:
        if o in pos: return o
    return pos[0] if pos and pos[0] else "?"
for p in players: p["ppos"]=_primary(p)

_bypos=_dd(list)
for p in players: _bypos[p["ppos"]].append(p)
for pos,lst in _bypos.items():
    lst.sort(key=lambda r:-(r["myros"] or 0)); n=len(lst)
    for i,p in enumerate(lst):
        p["posRank"]=i+1; p["posN"]=n
        p["posPct"]=round(100*(1-(i/(n-1)))) if n>1 else 100

_SLOTS={"C":10,"1B":10,"2B":10,"3B":10,"SS":10,"OF":30,"SP":52,"RP":22,"DH":1}
_repl={}
for pos,lst in _bypos.items():
    k=min(_SLOTS.get(pos,10),len(lst)-1) if lst else 0
    _repl[pos]=lst[k]["myros"] if lst else 0
for p in players: p["vorp"]=round((p["myros"] or 0)-_repl.get(p["ppos"],0))

def _consistency(p):
    base=(p["std"]/85.0) if p["std"] else 0
    if base<=0: return 50
    rs=[(v/d)/base for v,d in [(p["l30"],30),(p["l15"],15),(p["l7"],7)] if v is not None]
    if len(rs)<2: return 60
    return max(5,min(99,round(100-_st.pstdev(rs)*110)))
for p in players: p["consistency"]=_consistency(p)
for p in players:
    p["signal"]="RISING" if p["trend"]=="hot" else "FADING" if p["trend"]=="cold" else "STEADY"

def slimA(p):
    return {"id":p["id"],"name":p["name"],"mlb":p["mlb"],"pos":p["pos"],"ppos":p["ppos"],"ft":p["ft"],
            "type":p["type"],"std":p["std"],"l30":p["l30"],"l15":p["l15"],"myros":p["myros"],
            "projWk":p["projWk"],"vorp":p["vorp"],"trend":p["trend"],"tier":p["tier"],
            "consistency":p["consistency"],"posRank":p["posRank"],"posN":p["posN"],
            "st":{k:p["st"].get(k) for k in ("AVG","OPS","HR","SB","ERA","WHIP","K9","K","SV")}}

def _top(pred,key,n=15,rev=True):
    pool=[p for p in players if pred(p)]
    pool.sort(key=lambda r:(r.get(key) if r.get(key) is not None else -1e9),reverse=rev)
    return [slimA(p) for p in pool[:n]]

# recent weekly pace for risers
for p in players:
    r=(p["l15"]/15.0) if p["l15"] is not None else ((p["l30"]/30.0) if p["l30"] is not None else 0)
    p["_pace"]=round(r*7,1)

leadersHit=_top(lambda p:p["type"]=="H", "myros")
leadersPit=_top(lambda p:p["type"]=="P", "myros")
risers=_top(lambda p:p["trend"]=="hot" and (p["std"] or 0)>0, "_pace")
faRisers=_top(lambda p:p["ft"]=="FA" and p["trend"]=="hot", "_pace", 12)
# buy-low: rostered by OTHERS, hot + strong vorp (acquire targets)
buyLow=_top(lambda p:p["ft"] not in ("FA","WWT") and p["trend"]=="hot" and p["vorp"]>20, "vorp", 12)
# sell-high on MY team: overperforming season vs my ROS (name value > my projection)  -> cold/steady but high season pts
def _regress(p):
    sp=(p["std"]/85.0*102) if p["std"] else 0
    return (p["myros"] or 0)-sp
sellHigh=[slimA(p) for p in sorted([p for p in players if p["ft"]=="WWT" and _regress(p)<-12 and (p["std"] or 0)>90],key=lambda r:_regress(r))[:6]]
buyHold=[slimA(p) for p in sorted([p for p in players if p["ft"]=="WWT" and _regress(p)>12],key=lambda r:-_regress(r))[:6]]

# my roster positional grades using the ACTUAL optimal lineup assignment (mH) + arms
_slotmap=_dd(list)
for slot,p in mH:
    if p: _slotmap[slot].append(p)
_myarms=arms("WWT")
_sp=sorted([p for p in _myarms if "SP" in (p.get("pos") or "")],key=lambda r:-r["myros"])[:5]
_rp=sorted([p for p in _myarms if "SP" not in (p.get("pos") or "")],key=lambda r:-r["myros"])[:2]
rosterGrade=[]
def _grade(edge): return "A+" if edge>180 else "A" if edge>120 else "B" if edge>60 else "C" if edge>0 else "D" if edge>-80 else "F"
for pos in ["C","1B","2B","3B","SS","OF","SP","RP"]:
    if pos=="SP": starters=_sp; need=5
    elif pos=="RP": starters=_rp; need=2
    else: starters=_slotmap.get(pos,[]); need={"C":1,"1B":1,"2B":1,"3B":1,"SS":1,"OF":3}[pos]
    val=sum(p["myros"] for p in starters); rep=_repl.get(pos,0)*need; edge=round(val-rep)
    rosterGrade.append({"pos":pos,"edge":edge,"grade":_grade(edge),
        "best":(max(starters,key=lambda r:r["myros"])["name"] if starters else "—"),
        "names":[p["name"] for p in starters]})

# remaining strength of schedule (avg opp projWk), reuse playoff sim schedule
_idcode={1:"Beer",2:"SUFF",3:"GGT",4:"WWT",5:"DDT",6:"CT",7:"Gav",8:"GOON",9:"OBP",10:"SSs"}
_proj={t["code"]:t["projWk"] for t in teamrows}
_sched={14:[(9,6),(5,3),(7,4),(1,8),(10,2)],15:[(6,3),(4,9),(8,5),(2,7),(10,1)],16:[(4,6),(3,8),(9,2),(5,10),(7,1)],17:[(6,8),(2,4),(10,3),(1,9),(7,5)],18:[(2,6),(8,10),(4,1),(3,7),(9,5)],19:[(6,10),(1,2),(7,8),(5,4),(9,3)],20:[(1,6),(10,7),(2,5),(8,9),(4,3)],21:[(6,7),(5,1),(9,10),(3,2),(4,8)]}
_opps=_dd(list)
for mp,gs in _sched.items():
    for a,h in gs: _opps[a].append(h); _opps[h].append(a)
sos=[]
for tid,code in _idcode.items():
    opp_codes=[_idcode[o] for o in _opps[tid]]
    avg=round(sum(_proj[c] for c in opp_codes)/len(opp_codes))
    sos.append({"code":code,"name":[t["name"] for t in teamrows if t["code"]==code][0],
                "avgOpp":avg,"opps":[ [t["name"] for t in teamrows if t["code"]==_idcode[o]][0] for o in _opps[tid]]})
sos.sort(key=lambda x:x["avgOpp"])  # easiest first

analytics={"replacement":{k:round(v) for k,v in _repl.items()},
 "leadersHit":leadersHit,"leadersPit":leadersPit,"risers":risers,"faRisers":faRisers,
 "buyLow":buyLow,"sellHigh":sellHigh,"buyHold":buyHold,"rosterGrade":rosterGrade,"sos":sos}
# ===================== END ANALYTICS =====================


# ===================== ACTUALS + PROJECTION ACCURACY SCAFFOLD =====================
for _arr in (matchup["me"]["hitters"],matchup["me"]["pitchers"],matchup["opp"]["hitters"],matchup["opp"]["pitchers"]):
    for _p in _arr: _p["actual"]=[None]*7
matchup["actualTeam"]={"me":[None]*7,"opp":[None]*7}
matchup["hasActuals"]=False
_seasonAvg=round(PF["WWT"]/13)
_modelWeekly=matchup["me"]["proj"]
accuracy={
 "startMP":14,
 "note":"Live projection tracking begins this week (MP14) - the first week with formal daily/weekly projections. Actuals populate automatically with the daily 6 AM refresh as each day's games finalize.",
 "calibration":{"modelWeekly":_modelWeekly,"seasonAvg":_seasonAvg,"gap":_modelWeekly-_seasonAvg},
 "weekByWeek":[{"mp":14,"opp":matchup["opp"]["name"],"proj":_modelWeekly,"actual":None,"err":None,"acc":None}],
 "dayByDay":[{"day":matchup["dayRace"]["days"][i],"proj":matchup["dayRace"]["meDaily"][i],"actual":None} for i in range(7)],
 "playerLog":[]
}
# ===================== END =====================

DATA=dict(players=players,teams=teamrows,alerts=alerts,schedule=schedule,actionPlan=actionPlan,
          tradeIdeas=tradeIdeas,trollDeal=trollDeal,
          teamNames={c:v[0] for c,v in TEAMS.items()},matchup=matchup,analytics=analytics,accuracy=accuracy)
open("hub_data.json","w").write(json.dumps(DATA))
print("data ready: players",len(players),"| rostered",sum(1 for p in players if p["ft"]!="FA"),"| FA",sum(1 for p in players if p["ft"]=="FA"))
