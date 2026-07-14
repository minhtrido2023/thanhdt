# -*- coding: utf-8 -*-
"""basket_compare.py — side-by-side custom30V membership, yieldcombo (production) vs v3route.
Job Taylor_20260714_112932. Research/audit only; writes NOTHING production reads.

Same PIT params the R3 harness uses for ETF_LIQ=custompitg:
  quality="none", rebal="q2m5", gate_rating=3, weight_scheme="namecap", top_n=30, name_cap=0.10.

Run: $DNA_PYEXE mike/agents/Taylor/route_exp/basket_compare.py
"""
import os, sys
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq  # noqa: E402
import custom_basket as cb  # noqa: E402

START, END = "2014-01-02", "2026-06-19"
FOCUS = pd.Timestamp("2026-05-05")
OUT = os.path.join(WORKDIR, "mike", "agents", "Taylor", "route_exp")

PANEL = pd.read_csv(os.path.join(WORKDIR, "data", "value_panel_2014.csv"), parse_dates=["time"])
PANEL["qstart"] = PANEL["time"].dt.to_period("Q").dt.start_time
ROUTE = (PANEL.sort_values("time").groupby("ticker")["route"].last().to_dict())


def build(mode):
    _prev = os.environ.get("BASKET_SELECT")
    os.environ["BASKET_SELECT"] = mode
    try:
        lvl, adv, mem, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                         gate_rating=3, weight_scheme="namecap",
                                         top_n=30, name_cap=0.10, qtilt=None)
    finally:
        if _prev is None: os.environ.pop("BASKET_SELECT", None)
        else: os.environ["BASKET_SELECT"] = _prev
    return lvl, mem


print("=" * 90)
print("Building baskets (this hits BQ/local cache; a few minutes)")
lvl_y, mem_y = build("yieldcombo")
print(f"  yieldcombo: {len(mem_y)} member-rows, {mem_y.ticker.nunique()} union names")
lvl_r, mem_r = build("v3route")
print(f"  v3route   : {len(mem_r)} member-rows, {mem_r.ticker.nunique()} union names")

mem_y.to_csv(os.path.join(OUT, "members_yieldcombo.csv"), index=False)
mem_r.to_csv(os.path.join(OUT, "members_v3route.csv"), index=False)


def lvl_df(d):   # build_pit returns level as a {timestamp: level} dict, not a frame
    s = pd.Series(d); s.index = pd.to_datetime(s.index)
    return s.sort_index().rename("level").reset_index().rename(columns={"index": "time"})


lvl_y, lvl_r = lvl_df(lvl_y), lvl_df(lvl_r)
lvl_y.to_csv(os.path.join(OUT, "vehicle_level_yieldcombo.csv"), index=False)
lvl_r.to_csv(os.path.join(OUT, "vehicle_level_v3route.csv"), index=False)


def at(mem, d):
    m = mem.copy(); m["rebal_date"] = pd.to_datetime(m["rebal_date"])
    ds = sorted(m.rebal_date.unique())
    pick = max([x for x in ds if x <= d], default=ds[0])
    return pick, m[m.rebal_date == pick].copy()


d_y, b_y = at(mem_y, FOCUS)
d_r, b_r = at(mem_r, FOCUS)
for b in (b_y, b_r): b["route"] = b.ticker.map(ROUTE).fillna("?")

print("\n" + "=" * 90)
print(f"BASKET at rebal {pd.Timestamp(d_y).date()} (nearest on/before {FOCUS.date()})")
print("=" * 90)
sy, sr = set(b_y.ticker), set(b_r.ticker)
print(f"\nyieldcombo (production) — {len(sy)} names:\n  " + ", ".join(sorted(sy)))
print(f"\nv3route — {len(sr)} names:\n  " + ", ".join(sorted(sr)))
print(f"\noverlap {len(sy & sr)}/30")
print(f"  DROPPED by v3route ({len(sy-sr)}): " + ", ".join(f"{t}[{ROUTE.get(t,'?')}]" for t in sorted(sy - sr)))
print(f"  ADDED   by v3route ({len(sr-sy)}): " + ", ".join(f"{t}[{ROUTE.get(t,'?')}]" for t in sorted(sr - sy)))

print("\n--- route composition (name count) ---")
comp = pd.DataFrame({"yieldcombo": b_y.route.value_counts(), "v3route": b_r.route.value_counts()}).fillna(0).astype(int)
comp.loc["TOTAL"] = comp.sum()
print(comp.to_string())

FIN = {"BANK", "INSURANCE", "SECURITIES"}
print(f"\nFINANCIAL names: yieldcombo {b_y.route.isin(FIN).sum()}/30  ->  v3route {b_r.route.isin(FIN).sum()}/30")
print(f"  of which BANK : yieldcombo {(b_y.route=='BANK').sum()}      ->  v3route {(b_r.route=='BANK').sum()}")
print(f"  yieldcombo banks: " + ", ".join(sorted(b_y[b_y.route=='BANK'].ticker)))
print(f"  v3route    banks: " + ", ".join(sorted(b_r[b_r.route=='BANK'].ticker)))

print("\n--- HPG / LPB standing (user asked) ---")
for tk in ("HPG", "LPB"):
    iy = b_y[b_y.ticker == tk]; ir = b_r[b_r.ticker == tk]
    print(f"  {tk} [{ROUTE.get(tk,'?')}]: yieldcombo {'IN  (liq_rank %2d)' % iy.liq_rank.iloc[0] if len(iy) else 'OUT'}"
          f"   |  v3route {'IN  (liq_rank %2d)' % ir.liq_rank.iloc[0] if len(ir) else 'OUT'}")

# ---- financial-route abstention: how much of the delta is "better rank" vs "dropped for no pb_z" ----
qd = pd.Timestamp(d_r).to_period("Q").start_time
prior = [q for q in sorted(PANEL.qstart.unique()) if q < qd]
src_q = max(prior) if prior else qd
pf = PANEL[(PANEL.qstart == src_q) & (PANEL.route.isin(FIN))]
print(f"\n--- financial coverage at src_q {pd.Timestamp(src_q).date()} ---")
print(f"  financial names in panel: {pf.ticker.nunique()}; with pb_z: {pf.pb_z.notna().sum()} "
      f"({pf.pb_z.notna().mean():.0%}) -> the rest ABSTAIN (score -1) under v3route by rating_8l's own rule")

# ---- vehicle-level (custom30V standalone) metrics: the mechanism, undiluted by the 2-book system ----
print("\n" + "=" * 90)
print("VEHICLE-LEVEL custom30V (standalone, undiluted — the mechanism)")
print("=" * 90)


def vmetrics(lvl, label):
    s = lvl.copy(); s["time"] = pd.to_datetime(s["time"]); s = s.sort_values("time")
    col = "level" if "level" in s.columns else s.columns[1]
    v = s[col].astype(float).values; t = s["time"].values
    yrs = (t[-1] - t[0]) / np.timedelta64(365, "D")
    cagr = (v[-1] / v[0]) ** (1 / yrs) - 1
    r = pd.Series(v).pct_change().dropna()
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan
    dd = (pd.Series(v) / pd.Series(v).cummax() - 1).min()
    out = dict(label=label, CAGR=100 * cagr, Sharpe=sh, MaxDD=100 * dd, Calmar=cagr / abs(dd) if dd else np.nan)
    # IS/OOS
    for tag, a, b in (("IS", "2014-01-01", "2019-12-31"), ("OOS", "2020-01-01", "2026-12-31")):
        m = (s["time"] >= a) & (s["time"] <= b)
        vv = s.loc[m, col].astype(float).values; tt = s.loc[m, "time"].values
        if len(vv) > 20:
            yy = (tt[-1] - tt[0]) / np.timedelta64(365, "D")
            out[f"CAGR_{tag}"] = 100 * ((vv[-1] / vv[0]) ** (1 / yy) - 1)
            ddx = (pd.Series(vv) / pd.Series(vv).cummax() - 1).min()
            out[f"MaxDD_{tag}"] = 100 * ddx
    return out


R = pd.DataFrame([vmetrics(lvl_y, "yieldcombo"), vmetrics(lvl_r, "v3route")]).set_index("label")
print(R.round(2).to_string())
print("\ndelta v3route - yieldcombo:")
print((R.loc["v3route"] - R.loc["yieldcombo"]).round(2).to_string())
R.to_csv(os.path.join(OUT, "vehicle_metrics.csv"))

# turnover
for lab, mem in (("yieldcombo", mem_y), ("v3route", mem_r)):
    m = mem.copy(); m["rebal_date"] = pd.to_datetime(m["rebal_date"])
    ds = sorted(m.rebal_date.unique()); ch = []
    for i in range(1, len(ds)):
        a = set(m[m.rebal_date == ds[i-1]].ticker); b = set(m[m.rebal_date == ds[i]].ticker)
        ch.append(len(b - a))
    print(f"  {lab}: mean names replaced per rebal = {np.mean(ch):.2f}/30 over {len(ch)} rebals")
print("\nDONE — artifacts in", OUT)
