"""(b) Book-level A/B: add CFO-yield (1/PCF) rank into BAL momentum selection. Self-contained, T+1-Open.

BAL sleeve replicated faithfully (isolates the SELECTION effect; both arms share identical mechanics so
the DELTA = pure yield-rank effect): buyable = momentum/recovery play_types from SIGNAL_V11 (fresh from BQ,
no pickle); each day fill free slots (max 12) with top-scored non-held candidates from the PRIOR day's
signal, enter at T+1 Open, equal-weight, hold 45 trading days, stop -20% (close-based, exit next open),
TC 0.1%. score = rank_pct(ta) + lam*rank_pct(cfo_yield). lam=0 == pure-ta book (baseline).
"""
import numpy as np, pandas as pd, subprocess, io

WD = "/home/trido/thanhdt/WorkingClaude"
TC = 0.001; MAXPOS = 12; HOLD = 45; STOP = -0.20; LIQ = 5e9; INIT = 1e9

sig = pd.read_csv(f"{WD}/data/bal_signal_panel.csv", parse_dates=["time"])
opx = pd.read_csv(f"{WD}/data/bal_open_pcf.csv", parse_dates=["time"])

BUY = sig.play_type.str.contains("MOMENTUM", na=False) | sig.play_type.isin(["DEEP_VALUE_RECOVERY", "MEGA"])
close_by = {tk: dict(zip(g.time, g.Close.astype(float))) for tk, g in sig.groupby("ticker")}
open_by  = {tk: dict(zip(g.time, g.Open.astype(float)))  for tk, g in opx.groupby("ticker")}
opx["cfo"] = np.where(opx.PCF > 0, 1.0/opx.PCF, np.nan)
cfo_by = {tk: dict(zip(g.time, g.cfo)) for tk, g in opx.groupby("ticker")}
dates = sorted(sig.time.unique())

# candidate rows (buyable + liquid) with ta + cfo
cand = sig[BUY & (sig.liq >= LIQ)][["ticker", "time", "ta"]].copy()
cand["cfo"] = [cfo_by.get(t, {}).get(d, np.nan) for t, d in zip(cand.ticker, cand.time)]

def cand_by_day(lam):
    """per day -> list of (ticker, score) sorted desc, score=rank_pct(ta)+lam*rank_pct(cfo)."""
    out = {}
    for d, g in cand.groupby("time"):
        g = g.copy()
        ta_r = g.ta.rank(pct=True)
        cfo_r = g.cfo.rank(pct=True).fillna(0.5)   # missing cfo -> neutral
        g["score"] = ta_r + lam*cfo_r
        g = g.sort_values("score", ascending=False)
        out[d] = list(zip(g.ticker, g.score))
    return out

def simulate(lam):
    cbd = cand_by_day(lam)
    pos = {}; cash = INIT; navs = []; rets = []; nav_prev = INIT
    n_entries = 0; n_room = 0   # room = entry-days where #cand(prev) > free slots
    for di, d in enumerate(dates):
        # 1. exits at open (flagged yesterday)
        for tk in list(pos):
            if pos[tk]["exit_flag"]:
                op = open_by.get(tk, {}).get(d)
                if op is None or op <= 0:  # can't trade -> carry one day
                    continue
                cash += pos[tk]["shares"]*op*(1-TC); del pos[tk]
        # 2. entries at open using PREVIOUS day's signal (T+1)
        if di > 0:
            cl = cbd.get(dates[di-1], [])
            cl = [(t, s) for t, s in cl if t not in pos and open_by.get(t, {}).get(d, 0) > 0]
            free = MAXPOS - len(pos)
            if free > 0 and cl:
                if len(cl) > free: n_room += 1
                nav_open = cash + sum(p["shares"]*open_by.get(t, {}).get(d, close_by.get(t, {}).get(d, p["entry_open"]))
                                      for t, p in pos.items())
                target = nav_open/MAXPOS
                for tk, sc in cl:
                    if free <= 0: break
                    op = open_by[tk][d]
                    spend = min(target, cash)
                    if spend < target*0.5: break       # not enough cash for a full-ish slot
                    sh = spend*(1-TC)/op
                    cash -= spend
                    pos[tk] = dict(entry_open=op, shares=sh, days_held=0, exit_flag=False)
                    free -= 1; n_entries += 1
        # 3. mark close, age, set exit flags
        for tk, p in pos.items():
            p["days_held"] += 1
            c = close_by.get(tk, {}).get(d)
            if c is None: continue
            if p["days_held"] >= HOLD or (c/p["entry_open"]-1) <= STOP:
                p["exit_flag"] = True
        nav = cash + sum(p["shares"]*close_by.get(tk, {}).get(d, p["entry_open"]) for tk, p in pos.items())
        if nav <= 0: nav = nav_prev
        navs.append(nav); rets.append(nav/nav_prev-1); nav_prev = nav
        assert cash >= -1.0, f"negative cash {cash} at {d}"   # no leverage
    return pd.Series(navs, index=dates), np.array(rets), n_entries, n_room

yrs = (pd.Timestamp(dates[-1])-pd.Timestamp(dates[0])).days/365.25
spy = len(dates)/yrs
def metrics(nav, r):
    cagr = (nav.iloc[-1]/INIT)**(1/yrs)-1
    sh = r.mean()/r.std()*np.sqrt(spy) if r.std() > 0 else np.nan
    dd = (nav/nav.cummax()-1).min()
    return cagr, sh, dd, (cagr/abs(dd) if dd < 0 else np.nan)

LAMS = [("base(ta)", 0.0), ("blend0.3", 0.3), ("blend0.5", 0.5), ("blend1.0", 1.0)]
res = {}
print(f"{'arm':10} | {'CAGR':>7} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>6} | {'ΔCAGR':>7} {'ΔSh':>6} {'ΔDD':>7} | entries room")
print("-"*98)
b = None
for lab, lam in LAMS:
    nav, r, ne, nr = simulate(lam); res[lab] = (nav, r)
    c, s, dd, cal = metrics(nav, r)
    if b is None: b = (c, s, dd)
    print(f"{lab:10} | {c*100:>6.2f}% {s:>7.2f} {dd*100:>6.1f}% {cal:>6.2f} | "
          f"{(c-b[0])*100:>+6.2f}pp {s-b[1]:>+6.2f} {(dd-b[2])*100:>+6.1f}pp | {ne:>6} {nr:>5}")

# self-check + spotcheck
print("\n--- by-year return: base(ta) vs blend0.5 (anti-artifact) ---")
nb, _ = res["base(ta)"]; nbl, _ = res["blend0.5"]
yb = nb.groupby(nb.index.year).apply(lambda s: s.iloc[-1]/s.iloc[0]-1)
ybl = nbl.groupby(nbl.index.year).apply(lambda s: s.iloc[-1]/s.iloc[0]-1)
wins = 0
for y in yb.index:
    d = (ybl[y]-yb[y])*100; wins += d > 0
    print(f"  {y}: base {yb[y]*100:>+6.1f}%  blend {ybl[y]*100:>+6.1f}%  Δ {d:>+5.1f}pp {'+' if d>0 else ''}")
print(f"  blend beats base in {wins}/{len(yb)} years")

print("\n--- self-check ---")
ok = True
for lab, lam in LAMS:
    nav, r = res[lab]
    recon = INIT*np.prod(1+r); err = abs(recon-nav.iloc[-1])
    print(f"  {lab:10}: nav_recon_err={err:.2f} VND")
    ok &= err < 1.0
print(f"  {'PASS' if ok else 'FAIL'}  (cash>=0 leverage assert held in-sim)")

print("\n--- BQ spotcheck (5 open prices) ---")
rng = np.random.RandomState(11); sp = True
flat = [(t, d) for t in list(open_by)[:200] for d in list(open_by[t])[::400]]
picks = [flat[i] for i in rng.randint(0, len(flat), 5)]
inl = ",".join(f"('{t}',DATE '{np.datetime64(d,'D')}')" for t, d in picks)
chk = subprocess.run(["bq","query","--use_legacy_sql=false","--project_id=lithe-record-440915-m9","--format=csv",
                      f"SELECT t.ticker,t.time,t.Open FROM tav2_bq.ticker AS t WHERE (t.ticker,t.time) IN ({inl})"],
                     capture_output=True, text=True)
cm = pd.read_csv(io.StringIO(chk.stdout))
cmap = {(r.ticker, str(np.datetime64(r.time,'D'))): float(r.Open) for r in cm.itertuples()}
for t, d in picks:
    bqp = cmap.get((t, str(np.datetime64(d,'D'))), np.nan); sv = open_by[t][d]
    m = np.isfinite(bqp) and abs(bqp-sv) < 1e-6; sp &= m
    print(f"  {t} {np.datetime64(d,'D')}: script={sv:.1f} bq={bqp:.1f} {'OK' if m else 'MISMATCH'}")
print(f"  SPOTCHECK {'PASS' if sp else 'FAIL'}")
