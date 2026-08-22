#!/usr/bin/env python
"""Ma tran chien luoc DT5G x Value Radar — job Taylor_20260822_101400.

Nguon (da tra mike/kb/data_registry/):
  - DAILY rows cua pin R3 2026-08-03 (CANONICAL, results_registry "RE-PIN R3 ... LAG_ADV_BASIS=price"):
    per-phien nav_bal_ref / nav_lag_ref / combined_nav / state (DT5G) / vni_close. self-check 0 VND.
  - data/value_radar_series.csv qua value_radar.load_series(update=False) — CANONICAL, DISPLAY-ONLY.
    Dung cho phan tich lich su conditional; KHONG wire vao sizing.
Output: CSV cells + stdout bang.
"""
import os, sys, json
import numpy as np, pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, W)
OUT = os.path.join(W, "mike", "agents", "Taylor", "research", "strategy_regime_matrix_20260822")
os.makedirs(OUT, exist_ok=True)

PIN = os.path.join(W, "data",
    "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_repin0803_price_univpit.csv")
SPY = 249.2785102175346   # sessions_per_year tu METRIC cua chinh file pin
STATE = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}

# ---------------------------------------------------------------- 1. NAV per book
cols = ["record_type","key","value","ymd","book","ticker","action","play_type","holding_id",
        "shares","adj_price","buy_amount","sell_amount","fee","cash_after","reason","state",
        "nav_bal_ref","nav_lag_ref","bal_cash_ref","bal_stocks_ref","bal_etf_ref","lag_cash_ref",
        "lag_stocks_ref","lag_etf_ref","w_lag_tgt","rebal_cost","cap_bal","cap_lag",
        "combined_nav","vni_close"]
raw = pd.read_csv(PIN, names=cols, header=0, low_memory=False)
d = raw[raw.record_type == "DAILY"].copy()
d["time"] = pd.to_datetime(d["ymd"])
for c in ["state","nav_bal_ref","nav_lag_ref","combined_nav","vni_close","w_lag_tgt",
          "bal_cash_ref","lag_cash_ref","bal_stocks_ref","lag_stocks_ref","bal_etf_ref","lag_etf_ref"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")
d = d.sort_values("time").reset_index(drop=True)
assert len(d) == 3107, len(d)
# identity check: combined == bal + lag
# combination_rule (META cua chinh file pin): combined_nav = cap_bal + cap_lag, trong do cap_*
# la VON allocator (compound theo daily return cua so, co rebalance band). nav_*_ref la so cai
# tham chieu 25B doc lap cua tung so => daily return cua nav_*_ref la LUONG LAI/LO THUAN cua so,
# KHONG bi allocator rebalance lam nhay. Dung nav_*_ref cho per-book return.
err = (d.combined_nav - d.cap_bal - d.cap_lag).abs().max()
print(f"[selfcheck] max |combined - (cap_bal+cap_lag)| = {err:.6f} VND  (phai ~0)")
errb = (d.nav_bal_ref - d.bal_cash_ref - d.bal_stocks_ref - d.bal_etf_ref).abs().max()
errl = (d.nav_lag_ref - d.lag_cash_ref - d.lag_stocks_ref - d.lag_etf_ref).abs().max()
print(f"[selfcheck] nav_identity BAL={errb:.6f} LAG={errl:.6f} VND (phai ~0)")
n_rebal = len(set(pd.to_datetime(raw[raw.record_type == "REBAL"]["ymd"]).dt.normalize()))
print(f"[selfcheck] n_rebal_days = {n_rebal} (chi anh huong cap_*, KHONG anh huong nav_*_ref)")

d["r_bal"] = d.nav_bal_ref.pct_change()
d["r_lag"] = d.nav_lag_ref.pct_change()
d["r_comb"] = d.combined_nav.pct_change()
d["r_vni"] = d.vni_close.pct_change()

d["regime"] = d.state.map(STATE)

# ---------------------------------------------------------------- 2. Value Radar
import value_radar
vr = value_radar.load_series(update=False)[["time","score","label","pe_cap10","pb_cap10","spread",
                                            "p_pe","p_pb","p_sp","score_expanding"]]
vr["time"] = pd.to_datetime(vr["time"])
d = d.merge(vr, on="time", how="left")
print(f"[selfcheck] radar score NaN rows = {int(d.score.isna().sum())} / {len(d)}")
VN = {"CHEAP":"RE","FAIR":"TRUNGTINH","EXPENSIVE":"DAT"}
d["zone"] = d["label"].map(VN)

# ---------------------------------------------------------------- 3. Alpha Lens (Tier-1)
AL = ["FPT","ACB","MBB","HDB"]
al_csv = os.path.join(OUT, "alphalens_px.csv")
if not os.path.exists(al_csv):
    q = ("SELECT time, ticker, Close FROM `lithe-record-440915-m9.tav2_bq.ticker` "
         "WHERE ticker IN ('FPT','ACB','MBB','HDB') AND time BETWEEN '2013-12-01' AND '2026-06-19' "
         "ORDER BY time, ticker")
    import subprocess
    r = subprocess.run(["bq","query","--use_legacy_sql=false","--format=csv","--max_rows=200000",
                        "--project_id=lithe-record-440915-m9", q],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("[BQ FAIL]", r.stderr[-800:]); sys.exit(1)
    open(al_csv,"w").write(r.stdout)
px = pd.read_csv(al_csv, parse_dates=["time"])
wide = px.pivot(index="time", columns="ticker", values="Close").sort_index()
rets = wide.pct_change()
have = rets.notna().sum()
print("[alphalens] obs/ticker:", dict(have))
d = d.merge(rets.mean(axis=1, skipna=True).rename("r_al").reset_index(), on="time", how="left")
for t in AL:
    d = d.merge(rets[t].rename(f"r_{t}").reset_index(), on="time", how="left")

d.to_csv(os.path.join(OUT, "panel_daily.csv"), index=False)

# ---------------------------------------------------------------- 4. thong ke
def blocks(flags):
    """so doan lien tuc True = so 'su kien doc lap' xap xi."""
    f = flags.to_numpy()
    return int(((f) & (~np.r_[False, f[:-1]])).sum())

def stat(sub, col, ref=None):
    r = sub[col].dropna()
    n = len(r)
    if n < 20:
        return dict(n=n, cagr=np.nan, vol=np.nan, sharpe=np.nan, dd=np.nan, hit=np.nan, excess=np.nan)
    cum = float((1+r).prod())
    cagr = cum ** (SPY/n) - 1
    vol = float(r.std(ddof=1)) * np.sqrt(SPY)
    sh = (float(r.mean())*SPY) / vol if vol > 0 else np.nan
    eq = (1+r).cumprod(); dd = float((eq/eq.cummax() - 1).min())
    hit = float((r > 0).mean())
    ex = np.nan
    if ref is not None and ref != col:
        rr = sub[[col, ref]].dropna()
        if len(rr) >= 20:
            cb = float((1+rr[col]).prod()) ** (SPY/len(rr)) - 1
            cv = float((1+rr[ref]).prod()) ** (SPY/len(rr)) - 1
            ex = cb - cv
    return dict(n=n, cagr=cagr, vol=vol, sharpe=sh, dd=dd, hit=hit, excess=ex)

rows = []
for reg in ["CRISIS","BEAR","NEUTRAL","BULL","EXBULL"]:
    for zn in ["RE","TRUNGTINH","DAT","*ALL*"]:
        sub = d[d.regime == reg] if zn == "*ALL*" else d[(d.regime == reg) & (d.zone == zn)]
        if len(sub) == 0:
            continue
        rec = dict(regime=reg, zone=zn, days=len(sub),
                   episodes=blocks((d.regime == reg) if zn=="*ALL*" else ((d.regime==reg)&(d.zone==zn))),
                   first=str(sub.time.min().date()), last=str(sub.time.max().date()),
                   radar_mean=float(sub.score.mean()) if sub.score.notna().any() else np.nan,
                   w_lag=float(sub.w_lag_tgt.mean()))
        for nm, col in [("VNI","r_vni"),("BAL","r_bal"),("LAG","r_lag"),("COMB","r_comb"),("AL","r_al")]:
            s = stat(sub, col, ref="r_vni")
            rec[f"{nm}_cagr"] = s["cagr"]; rec[f"{nm}_sharpe"] = s["sharpe"]
            rec[f"{nm}_dd"] = s["dd"]; rec[f"{nm}_ex"] = s["excess"]; rec[f"{nm}_hit"] = s["hit"]
        for t in AL:
            s = stat(sub, f"r_{t}", ref="r_vni")
            rec[f"{t}_cagr"] = s["cagr"]; rec[f"{t}_ex"] = s["excess"]
        rows.append(rec)
cells = pd.DataFrame(rows)
cells.to_csv(os.path.join(OUT, "cells.csv"), index=False)

pd.set_option("display.width", 250, "display.max_columns", 60)
def pc(x): return "  n/a " if pd.isna(x) else f"{100*x:+6.1f}"
print("\n================ MA TRAN 5x3 — CAGR annualised trong tung o (VND, gross backtest) ============")
print(f"{'regime':8s} {'zone':10s} {'days':>5s} {'ep':>3s} {'radar':>6s} {'wLAG':>5s} "
      f"{'VNI':>7s} {'BAL':>7s} {'LAG':>7s} {'COMB':>7s} {'AL4':>7s} | "
      f"{'BALex':>7s} {'LAGex':>7s} {'ALex':>7s} | {'BALsh':>6s} {'LAGsh':>6s} {'ALsh':>6s}")
for _, r in cells.iterrows():
    print(f"{r.regime:8s} {r.zone:10s} {r.days:5.0f} {r.episodes:3.0f} "
          f"{r.radar_mean:6.1f} {r.w_lag:5.2f} "
          f"{pc(r.VNI_cagr)} {pc(r.BAL_cagr)} {pc(r.LAG_cagr)} {pc(r.COMB_cagr)} {pc(r.AL_cagr)} | "
          f"{pc(r.BAL_ex)} {pc(r.LAG_ex)} {pc(r.AL_ex)} | "
          f"{r.BAL_sharpe:6.2f} {r.LAG_sharpe:6.2f} {r.AL_sharpe:6.2f}")

print("\n================ ALPHA LENS — tung ma, excess vs VNI ============")
print(f"{'regime':8s} {'zone':10s} {'days':>5s} " + " ".join(f"{t:>7s}" for t in AL) + " | " + " ".join(f"{t+'ex':>7s}" for t in AL))
for _, r in cells.iterrows():
    print(f"{r.regime:8s} {r.zone:10s} {r.days:5.0f} " + " ".join(pc(r[f'{t}_cagr']) for t in AL)
          + " | " + " ".join(pc(r[f'{t}_ex']) for t in AL))

# ---------------------------------------------------------------- 5. zone marginal (all regimes)
print("\n================ MARGINAL theo ZONE (gop moi regime) ============")
for zn in ["RE","TRUNGTINH","DAT"]:
    sub = d[d.zone == zn]
    line = f"{zn:10s} days={len(sub):5d} ep={blocks(d.zone==zn):3d} "
    for nm, col in [("VNI","r_vni"),("BAL","r_bal"),("LAG","r_lag"),("COMB","r_comb"),("AL","r_al")]:
        s = stat(sub, col, ref="r_vni")
        line += f"{nm}={pc(s['cagr'])}({pc(s['excess'])}) "
    print(line)

# ---------------------------------------------------------------- 6. transition: forward return sau khi doi state
print("\n================ TRANSITION — forward 60-phien COMB/VNI sau moi lan DOI state ============")
d["st_prev"] = d.state.shift(1)
tr = d[(d.state != d.st_prev) & d.st_prev.notna()].copy()
fwd = {}
for h in (20, 60):
    for col in ["r_comb","r_vni","r_bal","r_lag","r_al"]:
        d[f"f{h}_{col}"] = (1+d[col].fillna(0)).rolling(h).apply(np.prod, raw=True).shift(-(h-1)) - 1
tr = d[(d.state != d.st_prev) & d.st_prev.notna()].copy()
g = tr.groupby([tr.st_prev.map(STATE), tr.state.map(STATE)])
for k, sub in g:
    if len(sub) < 2: continue
    print(f"{k[0]:8s}->{k[1]:8s} n={len(sub):2d} | f60 COMB={pc(sub.f60_r_comb.mean())} "
          f"BAL={pc(sub.f60_r_bal.mean())} LAG={pc(sub.f60_r_lag.mean())} "
          f"AL={pc(sub.f60_r_al.mean())} VNI={pc(sub.f60_r_vni.mean())}")

# ---------------------------------------------------------------- 7. o hien tai NEUTRAL+RE
cur = d[(d.regime=="NEUTRAL") & (d.zone=="RE")]
print(f"\n[NEUTRAL+RE] days={len(cur)} episodes={blocks((d.regime=='NEUTRAL')&(d.zone=='RE'))} "
      f"periods={sorted(set(cur.time.dt.year))}")

# block bootstrap cho o hien tai: BAL-LAG spread
def block_boot(x, y, nb=5000, L=20, seed=7):
    rng = np.random.default_rng(seed)
    v = (x - y).dropna().to_numpy()
    if len(v) < 3*L: return np.nan, np.nan, np.nan
    nblk = len(v)//L
    out = np.empty(nb)
    for i in range(nb):
        idx = rng.integers(0, len(v)-L, nblk)
        out[i] = np.concatenate([v[j:j+L] for j in idx]).mean()
    return float(v.mean()*SPY), float(np.percentile(out,2.5)*SPY), float(np.percentile(out,97.5)*SPY)

for reg in ["CRISIS","BEAR","NEUTRAL","BULL","EXBULL"]:
    for zn in ["RE","TRUNGTINH","DAT"]:
        sub = d[(d.regime==reg)&(d.zone==zn)]
        if len(sub) < 100: continue
        m, lo, hi = block_boot(sub.r_bal, sub.r_lag)
        m2, lo2, hi2 = block_boot(sub.r_comb, sub.r_vni)
        print(f"[boot L=20] {reg:8s} {zn:10s} n={len(sub):4d} BAL-LAG ann={pc(m)} CI[{pc(lo)},{pc(hi)}] "
              f"| COMB-VNI ann={pc(m2)} CI[{pc(lo2)},{pc(hi2)}]")

print("\nOUT:", OUT)
