"""
Wave1/H8a-tiebreaker LOO (leave-one-out) verification — RESEARCH ONLY.
Reuses frozen DAILY NAV series from the two prior H8a runs (job Taylor_20260705_135028).
No backtest re-run, no production change. Reads only the two audit CSVs.

Question: the CONDITIONAL-PASS (OOS +1.61pp CAGR) for LAG_FUND_DNPR reorder was LUMPY —
all edge from 2021 (+12.24pp) and 2023 (+10.27pp). Does the edge survive dropping those years?

Metrics match pt_v23_audit_2014.calc_metrics conventions (Sharpe*sqrt(252), Calmar=CAGR/|MaxDD|).
LOO annualization: sessions/year estimated from the full OOS series (constant), then
years_retained = n_retained_returns / spy. Both series use the identical method, so the
treatment-vs-baseline delta is method-invariant.
"""
import pandas as pd, numpy as np

BASE = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv"
TRT  = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_dnprREORDER.csv"

def load_daily_nav(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["date"] = pd.to_datetime(d["ymd"])
    d = d.sort_values("date").set_index("date")
    s = d["combined_nav"].astype(float)
    return s

base = load_daily_nav(BASE)
trt  = load_daily_nav(TRT)

# align to common dates
common = base.index.intersection(trt.index)
base = base.loc[common]
trt  = trt.loc[common]
print(f"Common daily rows full: {len(common)}  {common[0].date()} -> {common[-1].date()}")

# OOS = 2020-01-01 onwards
OOS_START = pd.Timestamp("2020-01-01")
base_oos = base[base.index >= OOS_START]
trt_oos  = trt[trt.index >= OOS_START]
oos_dates = base_oos.index
print(f"OOS daily rows: {len(oos_dates)}  {oos_dates[0].date()} -> {oos_dates[-1].date()}")

# sessions/year estimated from full OOS calendar span (constant for all LOO subsets)
oos_years = (oos_dates[-1] - oos_dates[0]).days / 365.25
spy = (len(oos_dates) - 1) / oos_years  # returns per calendar year
print(f"OOS calendar years {oos_years:.2f}  sessions/yr {spy:.1f}\n")

def metrics_from_returns(r):
    """r: pd.Series of daily returns (already subset). Chain into synthetic NAV."""
    r = r.dropna()
    n = len(r)
    nav = (1 + r).cumprod()
    total = nav.iloc[-1]
    yrs = n / spy
    cagr = total ** (1 / yrs) - 1
    sh252 = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0
    peak = nav.cummax(); dd = nav / peak - 1
    maxdd = dd.min()
    calmar = cagr / abs(maxdd) if maxdd < 0 else 0
    return dict(n=n, years=yrs, cagr=cagr, sharpe=sh252, maxdd=maxdd, calmar=calmar)

def oos_returns(series):
    return series.pct_change().dropna()  # first OOS day return relative to prior OOS day

base_r = oos_returns(base_oos)
trt_r  = oos_returns(trt_oos)
# align return indices
ri = base_r.index.intersection(trt_r.index)
base_r = base_r.loc[ri]; trt_r = trt_r.loc[ri]

def drop_years(r, years):
    mask = ~r.index.year.isin(years)
    return r[mask]

scenarios = [
    ("OOS full (2020+)",            []),
    ("OOS drop 2021",              [2021]),
    ("OOS drop 2023",              [2023]),
    ("OOS drop 2021+2023",         [2021, 2023]),
    ("OOS drop 2024",              [2024]),
]

print(f"{'Scenario':<24}{'':<3}{'CAGR%':>8}{'Shrp':>7}{'MaxDD%':>8}{'Calmar':>8}   (n days)")
print("-" * 78)
rows = []
for name, yrs_drop in scenarios:
    b = metrics_from_returns(drop_years(base_r, yrs_drop))
    t = metrics_from_returns(drop_years(trt_r, yrs_drop))
    dcagr = (t["cagr"] - b["cagr"]) * 100
    dcalm = t["calmar"] - b["calmar"]
    print(f"{name:<27}base {b['cagr']*100:7.2f}{b['sharpe']:7.2f}{b['maxdd']*100:8.1f}{b['calmar']:8.2f}   n={b['n']}")
    print(f"{'':<27}trt  {t['cagr']*100:7.2f}{t['sharpe']:7.2f}{t['maxdd']*100:8.1f}{t['calmar']:8.2f}")
    verdict = "trt WINS" if (dcagr >= 0 and dcalm >= 0) else ("trt LOSES" if (dcagr < 0 or dcalm < 0) else "mixed")
    print(f"{'':<27}Δ    {dcagr:+7.2f}pp CAGR   Δcalmar {dcalm:+.2f}   -> {verdict}\n")
    rows.append(dict(scenario=name, base=b, trt=t, dcagr=dcagr, dcalmar=dcalm, verdict=verdict))

# focus verdict on scenario (c) drop 2021+2023
core = [r for r in rows if r["scenario"] == "OOS drop 2021+2023"][0]
print("=" * 78)
print("CORE LOO TEST (c) — drop BOTH 2021 & 2023:")
print(f"  base CAGR {core['base']['cagr']*100:.2f}%  Calmar {core['base']['calmar']:.2f}")
print(f"  trt  CAGR {core['trt']['cagr']*100:.2f}%  Calmar {core['trt']['calmar']:.2f}")
print(f"  Δ CAGR {core['dcagr']:+.2f}pp   Δ Calmar {core['dcalmar']:+.2f}")
if core["dcagr"] >= 0 and core["dcalmar"] >= 0:
    print("  => ROBUST CORE survives outside 2021/2023 -> WIRE-WORTHY (pending skeptic)")
else:
    print("  => edge is reshuffle-luck of 2021/2023 -> CONFIRMED-LUMPY-DO-NOT-WIRE")
print("=" * 78)
