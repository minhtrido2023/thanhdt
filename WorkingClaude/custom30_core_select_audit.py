"""(a) custom30 as a QUALITY-VALUE CORE: select members by a liquidity x CFO-yield blend (vs pure
liquidity), cap-weight namecap10, T+1-Open BQ-audited. Self-contained (replicates custom_basket.build_pit
PIT selection: prior-quarter liquidity + as-of fa_ratings_8l<=3 gate + q2m5 rebal). Keeps a LIQUIDITY
FLOOR (candidates = top-60 liquid gated) so the 'core' stays tradable, then tilts the pick by yield.

variants (all cap-weight namecap10, same gate/universe, only MEMBER SELECTION differs):
  liq        : top-30 by prior-quarter liquidity        <- reproduces the live parking basket
  core0.5    : top-30 by rank_pct(liq)+0.5*rank_pct(cfo_yield) among top-60 liquid gated
  core1.0    : top-30 by rank_pct(liq)+1.0*rank_pct(cfo_yield)
cfo_yield as-of = 1/(prior-quarter median PCF). PIT, no look-ahead.
"""
import numpy as np, pandas as pd, subprocess, io, bisect

WD = "/home/trido/thanhdt/WorkingClaude"; PROJ = "lithe-record-440915-m9"
TC = 0.001; NAME_CAP = 0.10; INIT = 1e9; TOPN = 30; POOL = 60

def bq(sql):
    r = subprocess.run(["bq","query","--use_legacy_sql=false",f"--project_id={PROJ}","--format=csv","--max_rows=3000000",sql],
                       capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-800:])
    return pd.read_csv(io.StringIO(r.stdout))

def cap_names(w, cap):
    w = np.array(w, float); s = w.sum()
    if s <= 0: return w
    w = w/s
    for _ in range(100):
        over = w > cap+1e-12
        if not over.any(): break
        exc = (w[over]-cap).sum(); w[over] = cap
        und = ~over; us = w[und].sum()
        if us <= 1e-12: break
        w[und] += exc*w[und]/us
    return w

print("[1] pull selection inputs (liquidity / ratings / cfo by quarter)...")
qliq = bq("""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q, AVG(t.Volume_3M_P50*t.Close) AS liq, COUNT(*) nd
FROM tav2_bq.ticker t WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
  AND t.ICB_Code IS NOT NULL AND t.time BETWEEN DATE '2013-06-01' AND DATE '2026-06-16'
GROUP BY t.ticker,q HAVING nd>=20""")
qliq["q"] = pd.to_datetime(qliq["q"])
rat = bq("SELECT r.ticker,r.time,r.rating FROM tav2_bq.fa_ratings_8l r WHERE r.time<=DATE '2026-06-16' ORDER BY r.ticker,r.time")
rat["time"] = pd.to_datetime(rat["time"])
rat_by = {tk:(list(g["time"]),list(g["rating"])) for tk,g in rat.groupby("ticker")}
def rating_asof(tk,d):
    e = rat_by.get(tk)
    if not e: return np.nan
    i = bisect.bisect_right(e[0], d)-1
    return float(e[1][i]) if i>=0 else np.nan
cfo = bq("""SELECT t.ticker, DATE_TRUNC(t.time,QUARTER) AS q, AVG(SAFE_DIVIDE(1,t.PCF)) AS cfoy
FROM tav2_bq.ticker t WHERE t.PCF>0 AND t.time BETWEEN DATE '2013-06-01' AND DATE '2026-06-16'
GROUP BY t.ticker,q""")
cfo["q"] = pd.to_datetime(cfo["q"])
cfo_piv = cfo.pivot_table(index="q", columns="ticker", values="cfoy")
liq_piv = qliq.pivot_table(index="q", columns="ticker", values="liq")
cal = bq("SELECT DISTINCT t.time FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '2014-01-01' AND DATE '2026-06-16' ORDER BY t.time")
cal["time"] = pd.to_datetime(cal["time"]); days = list(cal["time"]); days_arr = np.array(days, dtype="datetime64[ns]")
rebal_dates = []
for Y in range(2014, 2027):
    for mo in (2,5,8,11):
        i = int(np.searchsorted(days_arr, np.datetime64(pd.Timestamp(Y,mo,5)), side="left"))
        if i < len(days_arr): rebal_dates.append(pd.Timestamp(days_arr[i]))
rebal_dates = sorted(set(d for d in rebal_dates if pd.Timestamp('2014-08-01')<=d<=pd.Timestamp('2026-06-16')))

def select(variant):
    """return {rebal_date(ts): [tickers]}"""
    out = {}
    for d in rebal_dates:
        qd = pd.Timestamp(d).to_period("Q").start_time
        pq = [q for q in liq_piv.index if q < qd]
        if not pq: continue
        src = max(pq)
        liq_row = liq_piv.loc[src].dropna().sort_values(ascending=False)
        gated = [tk for tk in liq_row.index if (lambda r: pd.notna(r) and r<=3)(rating_asof(tk,d))]
        if variant == "liq":
            picks = gated[:TOPN]
        else:
            lam = 0.5 if variant=="core0.5" else 1.0
            pool = gated[:POOL]                              # liquidity floor: only top-60 liquid gated
            cf = cfo_piv.loc[src] if src in cfo_piv.index else pd.Series(dtype=float)
            df = pd.DataFrame({"tk":pool})
            df["liq"] = [liq_row.get(t,np.nan) for t in pool]
            df["cfo"] = [cf.get(t,np.nan) for t in pool]
            df["score"] = df.liq.rank(pct=True) + lam*df.cfo.rank(pct=True).fillna(0.5)
            picks = list(df.sort_values("score",ascending=False).tk[:TOPN])
        out[d] = picks
    return out

VARS = ["liq","core0.5","core1.0"]
mem = {v: select(v) for v in VARS}
union = sorted(set(t for v in VARS for ps in mem[v].values() for t in ps))
print(f"    rebals={len(rebal_dates)} union_tickers={len(union)}")

print("[2] pull prices (Open/Close/OShares) for union...")
inl = ",".join(f"'{t}'" for t in union)
px = bq(f"""SELECT t.ticker,t.time,t.Open,t.Close,t.OShares FROM tav2_bq.ticker t
WHERE t.ticker IN ({inl}) AND t.time BETWEEN DATE '2014-07-01' AND DATE '2026-06-16' AND t.Open IS NOT NULL ORDER BY t.ticker,t.time""")
px["time"] = pd.to_datetime(px["time"])
opn = {t:dict(zip(g.time,g.Open.astype(float))) for t,g in px.groupby("ticker")}
cls = {t:dict(zip(g.time,g.Close.astype(float))) for t,g in px.groupby("ticker")}
mcap = {t:dict(zip(g.time,(g.Close*g.OShares).astype(float))) for t,g in px.groupby("ticker")}
dates = sorted(px.time.unique())

# exec date per rebal = first trading date >= rebal_date
rebal_exec = {}
for d in rebal_dates:
    c = [x for x in dates if x >= np.datetime64(d)]
    if c: rebal_exec[c[0]] = d

def weights(tickers, exec_d):
    tk = [t for t in tickers if exec_d in opn.get(t,{}) and mcap.get(t,{}).get(exec_d,0)>0]
    if not tk: return {}
    m = np.array([mcap[t][exec_d] for t in tk]); w = m/m.sum()
    w = cap_names(w, NAME_CAP)
    return dict(zip(tk,w))

def simulate(variant):
    sh = {}; cash_navprev = INIT; navs=[]; rets=[]; nav_prev=INIT; first=True; rl=[]
    for d in dates:
        if d in rebal_exec:
            rd = rebal_exec[d]; tgt = weights(mem[variant].get(rd,[]), d)
            if tgt:
                nav_open = INIT if first else sum(sh.get(t,0)*opn[t][d] for t in sh if d in opn.get(t,{}))
                cur = {t:sh.get(t,0)*opn[t][d] for t in set(sh)|set(tgt) if d in opn.get(t,{})}
                tm = {t:nav_open*tgt.get(t,0.0) for t in cur}
                turn = sum(abs(tm[t]-cur.get(t,0.0)) for t in tm); tc=TC*turn
                scale = (nav_open-tc)/nav_open if nav_open>0 else 1.0
                sh = {t:(nav_open*tgt[t]*scale)/opn[t][d] for t in tgt}; first=False
                rl.append(max(tgt.values()))
        nav = sum(sh.get(t,0)*cls[t][d] for t in sh if d in cls.get(t,{}))
        if nav<=0: nav=nav_prev
        navs.append(nav); rets.append(nav/nav_prev-1); nav_prev=nav
    return pd.Series(navs,index=dates), np.array(rets), rl

yrs = (pd.Timestamp(dates[-1])-pd.Timestamp(dates[0])).days/365.25; spy=len(dates)/yrs
def met(nav,r):
    cagr=(nav.iloc[-1]/INIT)**(1/yrs)-1; sh=r.mean()/r.std()*np.sqrt(spy) if r.std()>0 else np.nan
    dd=(nav/nav.cummax()-1).min(); return cagr,sh,dd,(cagr/abs(dd) if dd<0 else np.nan)

print(f"\n{'variant':9} | {'CAGR':>7} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>6} | {'ΔCAGR':>7} {'ΔSh':>6} {'ΔDD':>7}")
print("-"*78)
res={}; b=None
for v in VARS:
    nav,r,rl = simulate(v); res[v]=(nav,r,rl); c,s,dd,cal=met(nav,r)
    if b is None: b=(c,s,dd)
    print(f"{v:9} | {c*100:>6.2f}% {s:>7.2f} {dd*100:>6.1f}% {cal:>6.2f} | {(c-b[0])*100:>+6.2f}pp {s-b[1]:>+6.2f} {(dd-b[2])*100:>+6.1f}pp")

# membership overlap liq vs core
ov = []
for d in rebal_dates:
    a=set(mem["liq"].get(d,[])); c=set(mem["core0.5"].get(d,[]))
    if a: ov.append(len(a&c)/len(a))
print(f"\nmembership overlap liq vs core0.5: {np.mean(ov)*100:.0f}% (avg names shared / 30)")

print("\n--- by-year: liq vs core0.5 ---")
nl,_,_=res["liq"]; nc,_,_=res["core0.5"]
yl=nl.groupby(nl.index.year).apply(lambda s:s.iloc[-1]/s.iloc[0]-1); yc=nc.groupby(nc.index.year).apply(lambda s:s.iloc[-1]/s.iloc[0]-1)
w=0
for y in yl.index:
    dd=(yc[y]-yl[y])*100; w+=dd>0
    print(f"  {y}: liq {yl[y]*100:>+6.1f}%  core {yc[y]*100:>+6.1f}%  Δ {dd:>+5.1f}pp")
print(f"  core beats liq {w}/{len(yl)} years")

print("\n--- self-check + spotcheck ---")
okk=True
for v in VARS:
    nav,r,rl=res[v]; err=abs(INIT*np.prod(1+r)-nav.iloc[-1]); mw=max(rl)
    print(f"  {v:9}: nav_recon_err={err:.2f} VND  max_rebal_w={mw:.4f}")
    okk &= err<1.0 and mw<=NAME_CAP+1e-6
rng=np.random.RandomState(3); flat=[(d,t) for d in rebal_exec for t in mem['liq'].get(rebal_exec[d],[]) if d in opn.get(t,{})]
ck=[flat[i] for i in rng.randint(0,len(flat),5)]; inl2=",".join(f"('{t}',DATE '{np.datetime64(d,'D')}')" for d,t in ck)
cm=bq(f"SELECT t.ticker,t.time,t.Open FROM tav2_bq.ticker t WHERE (t.ticker,t.time) IN ({inl2})")
cmap={(r.ticker,str(np.datetime64(r.time,'D'))):float(r.Open) for r in cm.itertuples()}; sp=True
for d,t in ck:
    bqp=cmap.get((t,str(np.datetime64(d,'D'))),np.nan); m=np.isfinite(bqp) and abs(bqp-opn[t][d])<1e-6; sp&=m
    print(f"  {t} {np.datetime64(d,'D')}: script={opn[t][d]:.1f} bq={bqp:.1f} {'OK' if m else 'X'}")
print(f"  SELF-CHECK {'PASS' if okk else 'FAIL'} | SPOTCHECK {'PASS' if sp else 'FAIL'}")
