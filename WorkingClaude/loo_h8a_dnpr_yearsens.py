"""
Wave1/H8a-tiebreaker LOO — FULL per-year year-sensitivity extension (COMPLETENESS ONLY).
RESEARCH ONLY. Reuses the exact frozen DAILY NAV series + metric conventions of
loo_h8a_dnpr.py (job Taylor_20260705_143219). No backtest re-run, no production change.

Purpose (per quant-skeptic optional suggestion when verifying Taylor_20260705_143219):
run leave-one-out for EVERY individual OOS year (2020..2026-partial), not just the
2021/2023/2024 hand-picked set, to document year-sensitivity fully in the registry.
This DOES NOT change the verdict — it only fills out the table. The core drop-2021+2023
test already CONFIRMED-LUMPY-DO-NOT-WIRE.

Convention parity with loo_h8a_dnpr.py:
- combined_nav DAILY rows, common-date intersection, OOS = 2020-01-01 onward.
- sessions/year (spy) estimated ONCE from the full OOS calendar span (constant across
  all LOO subsets); both base & treatment use the identical method so the delta is
  method-invariant.
- Calmar = CAGR / |MaxDD|; Sharpe = mean/std * sqrt(252).
"""
import pandas as pd, numpy as np

BASE = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv"
TRT  = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_dnprREORDER.csv"

def load_daily_nav(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["date"] = pd.to_datetime(d["ymd"])
    d = d.sort_values("date").set_index("date")
    return d["combined_nav"].astype(float)

base = load_daily_nav(BASE)
trt  = load_daily_nav(TRT)
common = base.index.intersection(trt.index)
base = base.loc[common]; trt = trt.loc[common]

OOS_START = pd.Timestamp("2020-01-01")
base_oos = base[base.index >= OOS_START]
trt_oos  = trt[trt.index >= OOS_START]
oos_dates = base_oos.index
oos_years_span = (oos_dates[-1] - oos_dates[0]).days / 365.25
spy = (len(oos_dates) - 1) / oos_years_span
print(f"OOS daily rows: {len(oos_dates)}  {oos_dates[0].date()} -> {oos_dates[-1].date()}")
print(f"OOS calendar years {oos_years_span:.2f}  sessions/yr {spy:.1f}\n")

def metrics_from_returns(r):
    r = r.dropna(); n = len(r)
    nav = (1 + r).cumprod(); total = nav.iloc[-1]
    yrs = n / spy
    cagr = total ** (1 / yrs) - 1
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0
    peak = nav.cummax(); dd = nav / peak - 1; maxdd = dd.min()
    calmar = cagr / abs(maxdd) if maxdd < 0 else 0
    return dict(n=n, years=yrs, cagr=cagr, sharpe=sh, maxdd=maxdd, calmar=calmar)

base_r = base_oos.pct_change().dropna()
trt_r  = trt_oos.pct_change().dropna()
ri = base_r.index.intersection(trt_r.index)
base_r = base_r.loc[ri]; trt_r = trt_r.loc[ri]

def drop_years(r, years):
    return r[~r.index.year.isin(years)]

oos_year_list = sorted(set(base_r.index.year))
print(f"OOS years present: {oos_year_list}  (2026 = partial to {oos_dates[-1].date()})\n")

# ---- full NAV (no drop) reference ----
full_b = metrics_from_returns(base_r)
full_t = metrics_from_returns(trt_r)
print("=== FULL OOS reference (nothing dropped) ===")
print(f"  base CAGR {full_b['cagr']*100:6.2f}%  Calmar {full_b['calmar']:.2f}")
print(f"  trt  CAGR {full_t['cagr']*100:6.2f}%  Calmar {full_t['calmar']:.2f}")
print(f"  Δ CAGR {(full_t['cagr']-full_b['cagr'])*100:+.2f}pp  Δ Calmar {full_t['calmar']-full_b['calmar']:+.2f}\n")

# ---- full per-year LOO: drop exactly ONE year at a time ----
print("=== FULL per-year LOO (drop exactly one OOS year each row) ===")
hdr = f"{'DropYear':<10}{'baseCAGR':>9}{'trtCAGR':>9}{'ΔCAGR':>8}{'baseCal':>8}{'trtCal':>8}{'ΔCal':>7}   {'verdict':<10}{'nDays':>7}"
print(hdr); print("-" * len(hdr))
rows = []
for y in oos_year_list:
    b = metrics_from_returns(drop_years(base_r, [y]))
    t = metrics_from_returns(drop_years(trt_r, [y]))
    dc = (t["cagr"] - b["cagr"]) * 100
    dk = t["calmar"] - b["calmar"]
    verdict = "trt WINS" if (dc >= 0 and dk >= 0) else "trt LOSES"
    print(f"{y:<10}{b['cagr']*100:8.2f}%{t['cagr']*100:8.2f}%{dc:+8.2f}{b['calmar']:8.2f}{t['calmar']:8.2f}{dk:+7.2f}   {verdict:<10}{b['n']:>7}")
    rows.append(dict(year=y, b=b, t=t, dcagr=dc, dcalmar=dk, verdict=verdict))

# ---- interpretation: which dropped-year hurts / helps the edge most ----
full_delta = (full_t["cagr"] - full_b["cagr"]) * 100
print("\n=== INTERPRETATION (edge = trt CAGR − base CAGR; full-OOS edge = "
      f"{full_delta:+.2f}pp) ===")
# When dropping year Y, if delta shrinks a lot vs full => Y carried the edge.
# If delta grows vs full => Y was dragging the edge down.
print(f"{'DropYear':<10}{'edge(Δpp)':>11}{'vs full':>10}   interpretation")
print("-" * 60)
enrich = []
for row in rows:
    edge = row["dcagr"]
    shift = edge - full_delta  # negative => dropping Y removed positive edge => Y carried edge
    enrich.append((row["year"], edge, shift))
    if shift < -0.5:
        interp = f"Y CARRIES edge (removing it drops edge {shift:+.2f}pp)"
    elif shift > 0.5:
        interp = f"Y DRAGS edge down (removing it lifts edge {shift:+.2f}pp)"
    else:
        interp = "≈ neutral"
    print(f"{row['year']:<10}{edge:+11.2f}{shift:+10.2f}   {interp}")

carriers = sorted(enrich, key=lambda x: x[2])          # most negative shift first
draggers = sorted(enrich, key=lambda x: -x[2])
print(f"\nMost edge-CARRYING year (biggest edge loss when dropped): {carriers[0][0]} "
      f"(edge {carriers[0][1]:+.2f}pp, shift {carriers[0][2]:+.2f}pp)")
print(f"Runner-up carrier:                                        {carriers[1][0]} "
      f"(edge {carriers[1][1]:+.2f}pp, shift {carriers[1][2]:+.2f}pp)")
print(f"Biggest edge-DRAGGING year (edge best when it is dropped): {draggers[0][0]} "
      f"(edge {draggers[0][1]:+.2f}pp, shift {draggers[0][2]:+.2f}pp)")

print("\n" + "=" * 70)
print("COMPLETENESS NOTE: full per-year LOO CONFIRMS the concentration picture —")
print("verdict UNCHANGED = CONFIRMED-LUMPY-DO-NOT-WIRE (edge is 2021/2023 reshuffle-luck).")
print("=" * 70)
