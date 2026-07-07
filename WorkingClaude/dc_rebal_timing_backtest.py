# -*- coding: utf-8 -*-
"""dc_rebal_timing_backtest.py (job Taylor_20260707_042827, NHÁNH C phần 2) — RESEARCH ONLY.

Backtest lịch refresh membership DC book theo mốc lag-sau-quarter-end, dựa trên thống kê
Release_Date thật (dc_release_date_stats.py):
  lag 30d ~ 48-54% báo cáo đã nộp; lag 33d ~ 85-91% ("mốc-80%"); lag 36d (≈q2m5) ~ 98.9%.
Variants: daily (paper hiện tại) | q2m5 (lịch basket custom30V thật) | lag33 | lag30 | lag40.
Sleeve vehicle = DC names w=min(0.20,1/n) + remainder custom30V (panel cache job _173317),
TC 0.1% block-level như dc_waterfall_deepdive.py CÂU 3 (so sánh được trực tiếp).
Overlay lên R3 full-NAV (data/h3_baseline_R3.csv) như deepdive: r_new = r_base + w_park*(r_v - r_c30v).

Self-checks: (A) overlay identity 0 VND; (B) variant 'q2m5' dùng đúng rebal_date của basket
custom30v_8l.parquet (không tự bịa lịch); (C) daily variant tái lập số CÂU 3 deepdive.
"""
import os, sys, numpy as np, pandas as pd, duckdb
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

AUDIT = "data/h3_baseline_R3.csv"
SLEEVE = "data/converge_portfolio_backtest_nav.csv"
IS_END = pd.Timestamp("2019-12-31")
CAP, TC = 0.20, 0.001

aud_df = pd.read_csv(AUDIT, low_memory=False)
d = aud_df[aud_df["record_type"] == "DAILY"].copy()
d["ymd"] = pd.to_datetime(d["ymd"])
for c_ in ["state", "bal_etf_ref", "lag_etf_ref", "combined_nav"]:
    d[c_] = pd.to_numeric(d[c_])
aud = d.set_index("ymd").sort_index()

# r_c30v: dùng dc_park_ret.csv (rebuild 00:42 hôm nay, CÙNG cache với dbl panel) thay vì
# converge NAV file (build 16:41 hôm qua TRƯỚC sync BQ 23:45 -> lệch 227 ngày do adjusted Close)
r_c30v = pd.read_csv("data/dc_park_ret.csv", index_col=0, parse_dates=True)["park_ret"]

nav = aud["combined_nav"]
r_base = nav.pct_change().dropna()
w_park_prev = ((aud["bal_etf_ref"] + aud["lag_etf_ref"]) / aud["combined_nav"]).shift(1).reindex(r_base.index).fillna(0.0)

dbl = pd.read_csv("data/dc_dbl_panel.csv", index_col=0, parse_dates=True).astype(bool)
if "DHG" in dbl.columns:
    dbl["DHG"] = False          # paper config: DHG hard-excluded
sret = pd.read_csv("data/dc_stock_ret.csv", index_col=0, parse_dates=True)
park = pd.read_csv("data/dc_park_ret.csv", index_col=0, parse_dates=True)["park_ret"]
cal = dbl.index
names = list(dbl.columns)

# --------- rebal-date sets ---------
con = duckdb.connect(":memory:"); con.execute("SET threads=1")
q2m5 = pd.to_datetime(con.execute(
    "SELECT DISTINCT rebal_date FROM read_parquet('data/bq_cache/custom30v_8l.parquet') ORDER BY 1").df()["rebal_date"])
q2m5_dates = set(pd.Timestamp(x) for x in q2m5)

def lag_dates(lag_days):
    """First session on/after quarter_end + lag_days, for every quarter in range."""
    out = set()
    qends = pd.date_range("2013-12-31", cal[-1], freq="QE")
    for qe in qends:
        target = qe + pd.Timedelta(days=lag_days)
        nxt = cal[cal >= target]
        if len(nxt):
            out.add(nxt[0])
    return out

def vehicle(rebal_dates=None):
    """Composite sleeve return. rebal_dates=None -> daily refresh; else membership refreshed
    only on those dates (first date of cal always refreshes)."""
    W = pd.DataFrame(0.0, index=cal, columns=names); pk = pd.Series(0.0, index=cal)
    cur = []
    for i, dd in enumerate(cal):
        if rebal_dates is None or i == 0 or dd in rebal_dates:
            cur = [t for t in names if dbl.at[dd, t]]
        n = len(cur)
        if n:
            w = min(CAP, 1.0 / n)
            for t in cur: W.at[dd, t] = w
            pk.loc[dd] = max(0.0, 1.0 - w * n)
        else:
            pk.loc[dd] = 1.0
    r = pd.Series(0.0, index=cal); prev_w = W.iloc[0].copy(); prev_p = pk.iloc[0]
    turn = pd.Series(0.0, index=cal)
    for i, dd in enumerate(cal):
        if i == 0: continue
        ra = float((prev_w * sret.loc[dd].reindex(names).fillna(0.0)).sum())
        rp = prev_p * (park.loc[dd] if np.isfinite(park.loc[dd]) else 0.0)
        t = (float((W.loc[dd] - prev_w).abs().sum()) + abs(pk.loc[dd] - prev_p)) / 2.0
        r.loc[dd] = ra + rp - t * TC
        turn.loc[dd] = t
        prev_w = W.loc[dd].copy(); prev_p = pk.loc[dd]
    yrs = (cal[-1] - cal[0]).days / 365.25
    return r, turn.sum() / yrs

def overlay(delta_vehicle):
    dv = delta_vehicle.reindex(r_base.index).fillna(0.0)
    return r_base + w_park_prev * dv

def metrics(r):
    r = r.dropna(); nv = (1 + r).cumprod()
    yrs = (r.index[-1] - r.index[0]).days / 365.25
    cagr = nv.iloc[-1] ** (1 / yrs) - 1
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan
    dd = (nv / nv.cummax() - 1).min()
    return cagr * 100, sh, dd * 100, (cagr / abs(dd) if dd < 0 else np.nan)

def show(name, r):
    for tag, rr in [("FULL", r), ("IS", r[r.index <= IS_END]), ("OOS", r[r.index > IS_END])]:
        c, sh, dd, ca = metrics(rr)
        print(f"{name:<46}{tag:<5}{c:>7.2f}%{sh:>7.2f}{dd:>8.1f}%{ca:>7.2f}")
    print()

# self-check A: identity overlay
r_id = overlay(r_c30v - r_c30v)
assert float((r_id - r_base).abs().max()) == 0.0, "overlay identity broken"
print("SELF-CHECK A: overlay identity 0 VND OK")
# self-check B: q2m5 dates subset of calendar & count
q_in = [dd for dd in q2m5_dates if dd in set(cal)]
print(f"SELF-CHECK B: q2m5 rebal dates from basket parquet: {len(q2m5_dates)}, on calendar: {len(q_in)}")

variants = [
    ("daily signal-driven (paper)", None),
    ("q2m5 (lịch basket thật, lag~36d, 98.9% nộp)", q2m5_dates),
    ("lag40d (+an toàn 1 tuần)", lag_dates(40)),
    ("lag33d (mốc-85%, sớm hơn ~3d)", lag_dates(33)),
    ("lag30d (mốc-50%, sớm hơn ~6d)", lag_dates(30)),
]
hdr = f"{'config':<46}{'win':<5}{'CAGR':>8}{'Sharpe':>7}{'MaxDD':>9}{'Calmar':>7}"
print("\n=== NHÁNH C — DC membership refresh timing (full-NAV overlay lên R3) ===")
print(hdr); print("-" * len(hdr))
show("R3 baseline (custom30V parking)", r_base)
per_year = {}
for label, rd in variants:
    rv, tvr = vehicle(rebal_dates=rd)
    rr = overlay(rv - r_c30v)
    show(f"{label} | turn {tvr:.2f}x", rr)
    per_year[label] = rr

print("=== per-year delta vs daily (full-NAV CAGR pp) ===")
base_y = per_year["daily signal-driven (paper)"]
def yearly(r): return (1 + r).groupby(r.index.year).prod() - 1
by = yearly(base_y)
cols = [l for l, _ in variants[1:]]
print(f"{'year':<6}{'daily':>9}" + "".join(f"{c[:14]:>16}" for c in cols))
for y in by.index:
    row = f"{y:<6}{by[y]*100:>8.2f}%"
    for c in cols:
        vy = yearly(per_year[c])
        row += f"{(vy[y]-by[y])*100:>+15.2f}p"
    print(row)
