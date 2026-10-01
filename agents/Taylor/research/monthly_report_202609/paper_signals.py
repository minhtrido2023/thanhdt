import csv, glob, os, re, json, subprocess, statistics as st, collections
EX = "/home/trido/thanhdt/WorkingClaude/data/execution_logs"
MARK = ("EXTREME_PAUSE", "EXTREME_FLOOR_GUARD", "EXTREME_DOWN sell-to-floor")
BUYB = ["11:00","11:15","13:00","13:15","13:30"]; SELLB = ["09:15","09:30","09:45","10:00"]
def inblk(t, blocks):
    m = int(t[:2])*60+int(t[3:5])
    return any(int(b[:2])*60+int(b[3:]) <= m < int(b[:2])*60+int(b[3:])+15 for b in blocks)
def inwin(t, a, b): return a <= t[:5] < b
rows_all = []
stats = {}
for acc in ["main", "SpaceX", "ZaloPay"]:
    for mon in ["2026-08", "2026-09"]:
        fs = sorted(glob.glob(f"{EX}/exec_{acc}_{mon}-*_journal.csv"))
        s = collections.Counter(); ev = 0; fails = collections.Counter(); marks = 0; failday = collections.Counter()
        for f in fs:
            d = os.path.basename(f).split("_")[2]
            rs = list(csv.DictReader(open(f, encoding="utf-8")))
            if any(r["event"] == "PLACE" for r in rs): ev += 1
            for r in rs:
                e = r["event"]; s[e] += 1
                if any(m in (e or "") or m in (r.get("note") or "") for m in MARK): marks += 1
                if re.search("FAIL|ERROR|REJECT", e or ""): fails[e] += 1; failday[d] += 1
                if e == "FILL":
                    t = r["ts"][11:19]
                    rows_all.append(dict(acc=acc, mon=mon, d=d, tk=r["ticker"], side=r["side"], qty=float(r["qty"]), px=float(r["price"]), t=t, play=r["play_type"]))
        stats[(acc, mon)] = dict(files=len(fs), evidence=ev, place=s["PLACE"], fill=s["FILL"], fails=dict(fails), fail_days=dict(failday), markers=marks, hybrid_defer=s["HYBRID_DEFER"], expvol_shadow=s["EXPVOL_SHADOW"])
# BQ open
pairs = sorted({(r["tk"], r["d"]) for r in rows_all})
tks = sorted({p[0] for p in pairs})
q = ("SELECT t.ticker, CAST(t.time AS STRING) d, t.Open, t.Close, t.Price FROM tav2_bq.ticker AS t "
     "WHERE t.time BETWEEN '2026-08-01' AND '2026-09-30' AND t.ticker IN (" + ",".join(f"'{x}'" for x in tks) + ")")
out = subprocess.run(["bash","-c", f"source /home/trido/thanhdt/WorkingClaude/wc_env.sh; bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=json --max_rows=100000 \"{q}\""], capture_output=True, text=True).stdout
px = {(r["ticker"], r["d"]): r for r in json.loads(out)}
for r in rows_all:
    b = px.get((r["tk"], r["d"]))
    if b and float(b["Close"]) > 0:
        o_raw = float(b["Open"]) * float(b["Price"]) / float(b["Close"])
        r["open_raw"] = o_raw; r["bps"] = (r["px"]/o_raw - 1) * 1e4
def daymean(rs):
    by = collections.defaultdict(list)
    for r in rs:
        if "bps" in r: by[r["d"]].append(r["bps"])
    m = [st.mean(v) for v in by.values()]
    if not m: return None
    sd = st.stdev(m) if len(m) > 1 else None
    return dict(n_days=len(m), n_fills=sum(len(v) for v in by.values()), mean=round(st.mean(m),1), sd=round(sd,1) if sd else None, se=round(sd/len(m)**0.5,1) if sd else None)
fv = {}
for acc in ["main","SpaceX","ZaloPay"]:
    for mon in ["2026-08","2026-09"]:
        rs = [r for r in rows_all if r["acc"]==acc and r["mon"]==mon]
        buys = [r for r in rs if r["side"]=="buy"]; sells = [r for r in rs if r["side"]=="sell"]
        fv[f"{acc}|{mon}"] = dict(
            buy_fills=len(buys), buy_in_block=sum(inblk(r["t"],BUYB) for r in buys), buy_in_oldwin=sum(inwin(r["t"],"10:45","11:15") for r in buys),
            buy_days=sorted({r["d"] for r in buys}),
            sell_fills=len(sells), sell_in_block=sum(inblk(r["t"],SELLB) for r in sells), sell_in_oldwin=sum(inwin(r["t"],"09:15","09:45") for r in sells),
            buy_vs_open=daymean(buys), sell_vs_open=daymean(sells),
            buy_vs_open_hybrid_blocks=daymean([r for r in buys if inblk(r["t"],BUYB)]),
            missing_open=sum("bps" not in r for r in rs), plays=dict(collections.Counter(r["play"] for r in rs)))
res = dict(stats={f"{a}|{m}": v for (a,m),v in stats.items()}, fill_vs_open=fv)
json.dump(res, open("paper_signals_202608_202609.json","w"), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))

# --- per-day BUY bps main (leave-one-out check on sd)
for mon in ["2026-08","2026-09"]:
    by = collections.defaultdict(list)
    for r in rows_all:
        if r["acc"]=="main" and r["mon"]==mon and r["side"]=="buy" and "bps" in r and inblk(r["t"],BUYB): by[r["d"]].append(r["bps"])
    dm = {d: round(st.mean(v),1) for d,v in sorted(by.items())}
    vals = list(dm.values())
    loo = [round(st.stdev(vals[:i]+vals[i+1:]),1) for i in range(len(vals))]
    print(mon, dm, "sd", round(st.stdev(vals),1), "LOO sd range", min(loo), max(loo), "median", round(st.median(vals),1))
