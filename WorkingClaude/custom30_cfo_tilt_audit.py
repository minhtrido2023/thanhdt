"""(b) Book-level validation: CFO-yield tilt on the custom30 PARKING basket, T+1-Open, BQ-audited.

Faithful surface: uses the PUBLISHED production membership (tav2_bq.custom30_8l, data/custom30_membership.csv)
-- so BASELINE == the live parking basket (namecap10 cap-weight). The TILTED variants keep the SAME
membership / gate / namecap10 cap; only the per-name weight is tilted toward high CFO-yield (1/PCF, PIT).
This isolates the valuation tilt. Execution: rebalance to target weights at the OPEN of each rebal's
effective_from (no look-ahead -- weights use only PCF as-of <= effective_from); hold (shares fixed,
drift with Close) between rebals; TC=0.1% on traded notional. Single audit CSV + self-check + BQ spotcheck.

Variants:
  base     : published weight (namecap10 cap-weight)           <- the live parking basket
  tilt0.5  : w_base * cfo_score^0.5, renorm, re-cap namecap10   (mild)
  tilt1.0  : w_base * cfo_score^1.0, renorm, re-cap namecap10   (linear)
  yieldwt  : w ∝ cfo_score, re-cap namecap10                    (pure yield, extreme)
cfo_score_i = rank-normalized 1/PCF within the basket (PCF<=0 or missing -> neutral=1.0).
"""
import numpy as np, pandas as pd, subprocess, io

WD = "/home/trido/thanhdt/WorkingClaude"
TC = 0.001; NAME_CAP = 0.10; INIT = 1e9
PROJ = "lithe-record-440915-m9"

def bq(sql):
    r = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJ}",
                        "--format=csv", "--max_rows=2000000", sql], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-800:])
    return pd.read_csv(io.StringIO(r.stdout))

def cap_names(w, cap):
    w = np.array(w, float); s = w.sum()
    if s <= 0: return w
    w = w/s
    for _ in range(100):
        over = w > cap + 1e-12
        if not over.any(): break
        exc = (w[over]-cap).sum(); w[over] = cap
        und = ~over; us = w[und].sum()
        if us <= 1e-12: break
        w[und] += exc*w[und]/us
    return w

# ---- data ----
mem = pd.read_csv(f"{WD}/data/custom30_membership.csv", parse_dates=["rebal_date", "effective_from", "effective_to"])
px  = pd.read_csv(f"{WD}/data/custom30_prices.csv", parse_dates=["time"])
opn = {tk: dict(zip(g.time, g.Open.astype(float)))  for tk, g in px.groupby("ticker")}
cls = {tk: dict(zip(g.time, g.Close.astype(float))) for tk, g in px.groupby("ticker")}
pcf_s = {tk: g.set_index("time").PCF.sort_index() for tk, g in px.groupby("ticker")}
dates = sorted(px.time.unique())
date_idx = {d: i for i, d in enumerate(dates)}

def pcf_asof(tk, d):
    s = pcf_s.get(tk)
    if s is None: return np.nan
    s2 = s[s.index <= d]
    return float(s2.iloc[-1]) if len(s2) else np.nan

# cashflow-peak (asof rebal): trailing TTM CFO/assets >= 1.5x its 5Y norm (same def as rating_8l.py)
cfoa = pd.read_csv(f"{WD}/data/custom30_cfoa.csv", parse_dates=["time"])
cfoa["ttm"] = cfoa[["CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3"]].sum(axis=1, min_count=1)
cfoa["peak"] = (cfoa.ttm > 0) & (cfoa.CF_OA_5Y/5.0 > 0) & (cfoa.ttm >= 1.5*cfoa.CF_OA_5Y/5.0)
peak_s = {tk: g.set_index("time").peak.sort_index() for tk, g in cfoa.groupby("ticker")}

def peak_asof(tk, d):
    s = peak_s.get(tk)
    if s is None: return False
    s2 = s[s.index <= d]
    return bool(s2.iloc[-1]) if len(s2) else False

# rebal exec dates = effective_from (first trading day on/after the 05th); exec at OPEN of that date
rebals = []
for ef, g in mem.groupby("effective_from"):
    # find first available trading date >= ef
    cand = [d for d in dates if d >= np.datetime64(ef)]
    if not cand: continue
    exec_d = cand[0]
    rebals.append((exec_d, g))
rebals.sort(key=lambda x: x[0])
rebal_exec = {ed: g for ed, g in rebals}
assert len(set(rebal_exec)) == len(rebals)

def target_weights(g, exec_d, variant):
    """Return dict {ticker: weight} for names with an open price on exec_d."""
    sub = g[g.ticker.apply(lambda t: exec_d in opn.get(t, {}))].copy()
    if sub.empty: return {}
    tks = sub.ticker.tolist()
    wbase = sub.weight.values.astype(float)
    wbase = wbase/wbase.sum()
    if variant == "base":
        w = wbase
    else:
        # CFO yield score, PIT as-of exec_d (PCF is prior-quarter financial, no look-ahead)
        y = np.array([pcf_asof(t, exec_d) for t in tks], float)
        yld = np.where((y > 0) & np.isfinite(y), 1.0/y, np.nan)
        # rank-normalize to mean 1 (neutral for missing)
        sr = pd.Series(yld)
        rk = sr.rank()
        score = (rk/rk.mean()).fillna(1.0).values   # ~[0.x .. 1.x], mean 1
        if variant == "tilt0.5": w = wbase * score**0.5
        elif variant == "tilt1.0": w = wbase * score**1.0
        elif variant == "tiltG":   # tilt1.0 but NEUTRALIZE peak-cashflow names (score=1) -> user's peak guard
            pk = np.array([peak_asof(t, exec_d) for t in tks])
            score = np.where(pk, 1.0, score)
            w = wbase * score**1.0
        elif variant == "yieldwt": w = np.where(np.isfinite(yld), yld, np.nanmedian(yld))
        else: raise ValueError(variant)
        w = w/np.nansum(w)
        w = cap_names(w, NAME_CAP)
    return dict(zip(tks, w))

def simulate(variant):
    shares = {}; nav_prev = INIT; navs = []; rets = []; rebal_log = []
    first = True
    for d in dates:
        # rebal at open
        if d in rebal_exec:
            tgt = target_weights(rebal_exec[d], d, variant)
            if tgt:
                nav_open = INIT if first else sum(shares.get(t, 0)*opn[t][d] for t in shares if d in opn.get(t, {}))
                cur_mv = {t: shares.get(t, 0)*opn[t][d] for t in set(shares) | set(tgt) if d in opn.get(t, {})}
                tgt_mv = {t: nav_open*tgt.get(t, 0.0) for t in cur_mv}
                turn = sum(abs(tgt_mv[t]-cur_mv.get(t, 0.0)) for t in tgt_mv)
                tc = TC*turn
                nav_after = nav_open - tc
                scale = nav_after/nav_open if nav_open > 0 else 1.0
                shares = {t: (nav_open*tgt[t]*scale)/opn[t][d] for t in tgt}
                rebal_log.append((str(np.datetime64(d, "D")), len(tgt), turn/nav_open, tc,
                                  max(tgt.values())))
                first = False
        # mark close
        nav_c = sum(shares.get(t, 0)*cls[t][d] for t in shares if d in cls.get(t, {}))
        if nav_c <= 0: nav_c = nav_prev
        navs.append(nav_c); rets.append(nav_c/nav_prev - 1.0); nav_prev = nav_c
    return pd.Series(navs, index=dates), np.array(rets), rebal_log

# ---- run variants ----
VAR = ["base", "tilt0.5", "tilt1.0", "tiltG", "yieldwt"]
results = {}
for v in VAR:
    results[v] = simulate(v)

# ---- metrics (calendar time, actual sessions/yr) ----
yrs = (pd.Timestamp(dates[-1])-pd.Timestamp(dates[0])).days/365.25
spy = len(dates)/yrs
def metrics(nav, rets):
    cagr = (nav.iloc[-1]/INIT)**(1/yrs)-1
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std() > 0 else np.nan
    dd = (nav/nav.cummax()-1).min()
    cal = cagr/abs(dd) if dd < 0 else np.nan
    return cagr, sh, dd, cal

print(f"{'variant':9} | {'CAGR':>7} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} | {'ΔCAGR':>7} {'ΔSh':>6} {'ΔDD':>7}")
print("-"*78)
base_nav, base_r, _ = results["base"]; bc, bs, bd, bcal = metrics(base_nav, base_r)
metric_rows = []
for v in VAR:
    nav, r, rl = results[v]; c, s, dd, cal = metrics(nav, r)
    print(f"{v:9} | {c*100:>6.2f}% {s:>7.2f} {dd*100:>6.1f}% {cal:>7.2f} | "
          f"{(c-bc)*100:>+6.2f}pp {s-bs:>+6.2f} {(dd-bd)*100:>+6.1f}pp")
    metric_rows.append((v, c, s, dd, cal, len(rl), np.mean([x[2] for x in rl]), max(x[4] for x in rl)))

# ---- self-checks ----
print("\n--- self-checks ---")
ok = True
for v in VAR:
    nav, r, rl = results[v]
    recon = INIT*np.prod(1+r)
    err = abs(recon-nav.iloc[-1])
    maxw = max(x[4] for x in rl)
    # namecap asserted only on tilted variants (we re-cap them); base uses PUBLISHED weights verbatim
    capok = True if v == "base" else (maxw <= NAME_CAP+1e-6)
    note = " (published, not re-capped)" if v == "base" else ""
    print(f"  {v:9}: nav_recon_err={err:.4f} VND | rebals={len(rl)} | max_rebal_weight={maxw:.4f}{note} "
          f"namecap_ok={capok}")
    ok &= (err < 1.0) and capok
# weights sum to 1 check on a sample rebal
samp = rebals[20][0]
for v in VAR:
    w = target_weights(rebal_exec[samp], samp, v)
    print(f"  {v:9}: sample rebal {str(np.datetime64(samp,'D'))} sum_w={sum(w.values()):.6f} n={len(w)}")
print(f"  ALL SELF-CHECKS {'PASS' if ok else 'FAIL'}")

# ---- BQ price spotcheck (re-query 6 random rebal-day opens) ----
print("\n--- BQ spotcheck (open prices vs fresh BQ pull) ---")
rng = np.random.RandomState(7)
checks = []
flat = [(ed, t) for ed, g in rebals for t in g.ticker.tolist() if ed in opn.get(t, {})]
for ed, t in [flat[i] for i in rng.randint(0, len(flat), 6)]:
    checks.append((t, str(np.datetime64(ed, "D")), opn[t][ed]))
inlist = ",".join(f"('{t}',DATE '{d}')" for t, d, _ in checks)
chk = bq(f"SELECT t.ticker,t.time,t.Open FROM tav2_bq.ticker AS t WHERE (t.ticker,t.time) IN ({inlist})")
chkmap = {(r.ticker, str(np.datetime64(r.time,'D'))): float(r.Open) for r in chk.itertuples()}
spok = True
for t, d, p in checks:
    bqp = chkmap.get((t, d), np.nan)
    match = np.isfinite(bqp) and abs(bqp-p) < 1e-6
    spok &= match
    print(f"  {t} {d}: script={p:.1f} bq={bqp:.1f} {'OK' if match else 'MISMATCH'}")
print(f"  SPOTCHECK {'PASS' if spok else 'FAIL'}")

# ---- emit single audit CSV ----
out = []
out.append(["SECTION", "k", "v", "", ""])
for k, v in [("system", "custom30_cfo_tilt"), ("init_vnd", INIT), ("TC", TC), ("name_cap", NAME_CAP),
             ("exec", "T+1 effective_from OPEN"), ("n_dates", len(dates)),
             ("start", str(np.datetime64(dates[0],'D'))), ("end", str(np.datetime64(dates[-1],'D'))),
             ("selfcheck", "PASS" if ok else "FAIL"), ("spotcheck", "PASS" if spok else "FAIL")]:
    out.append(["META", k, v, "", ""])
for (v, c, s, dd, cal, nreb, avgturn, maxw) in metric_rows:
    out.append(["METRIC", v, f"CAGR={c:.4f}", f"Sharpe={s:.3f}", f"MaxDD={dd:.4f};Calmar={cal:.3f};rebals={nreb};avgturn={avgturn:.3f};maxw={maxw:.4f}"])
daily = pd.DataFrame({v: results[v][0] for v in VAR})
for d, row in daily.iterrows():
    out.append(["DAILY", str(np.datetime64(d,'D'))] + [f"{row[v]:.2f}" for v in VAR[:3]])
pd.DataFrame(out).to_csv(f"{WD}/data/custom30_cfo_tilt_audit.csv", index=False, header=False)
print(f"\nwrote data/custom30_cfo_tilt_audit.csv ({len(out)} rows)")
