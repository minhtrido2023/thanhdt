# -*- coding: utf-8 -*-
"""SELFCHECK — CAPIT per-name %ADV position cap (job Taylor_20260720_170223).

Verifies the cap formula agreed in job Taylor_20260720_164006 (exp_capitexit/RESULT.md §3c):

    w_i = min( capit_size / len(basket),  X * ADV20_i * D / NAV_book_LAG )

  X    = 0.10   (10% of ADV — INDUSTRY CONVENTION against market impact, NOT a backtested
                 parameter; no real market-impact data exists to calibrate it. Do not cite
                 as empirically validated.)
  D    = 2      (assume the position is exited over 2 sessions — same convention caveat)
  ADV20_i = median daily turnover (VND bn) over the 20 sessions STRICTLY BEFORE the washout
            day. The washout day is a volume spike BY CONSTRUCTION; using it as the baseline
            systematically overstates tradable liquidity (measured: median ADV20-after /
            ADV-on-entry-day = 0.54, p10 = 0.32 — exp_capitexit/RESULT.md §3a).
  Residual (capit_size/n - w_i) is NOT redistributed to other names -> deliberate sleeve
  under-deployment, left in cash. Equal-weight + selection logic unchanged.

Purpose of this run: confirm the cap is DORMANT at the current sleeve scale, i.e. it binds
on 0 of the 14 historical washout events -> wiring it changes nothing in live behaviour or
in the historical backtest. If it DOES bind, stop and report (per dispatch).
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd, duckdb

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
OUT = f"{WORKDIR}/mike/agents/Taylor/exp_capitadvcap"
os.makedirs(OUT, exist_ok=True)
con = duckdb.connect(":memory:"); con.execute("SET threads=1")
PRUNE = f"read_parquet('{WORKDIR}/data/bq_cache/ticker_prune/*.parquet')"

X, D = 0.10, 2.0
EVENTS = ["2014-05-08","2015-08-24","2016-01-18","2018-05-28","2020-03-12","2022-04-20",
          "2022-06-20","2022-09-29","2023-10-31","2024-04-19","2024-08-05","2025-04-03",
          "2025-10-20","2026-03-09"]

# ---- 1. reproduce the production basket at each event (pt_v23_audit_2014.py::capit_basket,
#         no-overflow path == golive_recommend_v23.py CAPIT block) -----------------------
rows = []
for ds in EVENTS:
    e = con.execute(f"""
        SELECT ticker, (PB-PB_MA5Y)/NULLIF(PB_SD5Y,0) AS pbz
        FROM {PRUNE}
        WHERE time = DATE '{ds}'
          AND ROE_Min5Y >= 0.12 AND ROIC5Y >= 0.10 AND FSCORE >= 6
          AND COALESCE(Price, Close) * Volume / 1e9 >= 2
    """).df().dropna(subset=["pbz"])
    g = e[e["pbz"] < -1]; c = e[e["pbz"] < 0]
    pick = g if len(g) >= 3 else (c if len(c) >= 3 else e)
    pick = pick.nsmallest(15, "pbz") if len(pick) > 15 else pick
    for t in pick["ticker"]:
        rows.append(dict(event=ds, ticker=t, n=len(pick)))
B = pd.DataFrame(rows)
print(f"baskets rebuilt: {len(EVENTS)} events, {len(B)} positions, "
      f"size min={B.groupby('event')['n'].first().min()} "
      f"median={B.groupby('event')['n'].first().median():.0f} "
      f"max={B.groupby('event')['n'].first().max()}")

# ---- 2. causal ADV20: median daily turnover over the 20 sessions BEFORE the washout day --
adv = con.execute(f"""
    WITH px AS (
        SELECT ticker, time, COALESCE(Price, Close) * Volume / 1e9 AS turn_b
        FROM {PRUNE} WHERE time >= DATE '2013-06-01'
    )
    SELECT * FROM px
""").df()
adv["time"] = pd.to_datetime(adv["time"])
cal = np.array(sorted(adv["time"].unique()))

def adv20_pre(ticker, ds):
    """median turnover over the 20 sessions STRICTLY BEFORE ds (washout day excluded)."""
    d = np.datetime64(pd.Timestamp(ds))
    i = np.searchsorted(cal, d, side="left")          # first index >= ds -> window is [i-20, i)
    lo = cal[max(0, i - 20)]
    s = adv[(adv["ticker"] == ticker) & (adv["time"] >= lo) & (adv["time"] < pd.Timestamp(ds))]
    return float(s["turn_b"].median()) if len(s) else np.nan

def adv_on(ticker, ds):
    s = adv[(adv["ticker"] == ticker) & (adv["time"] == pd.Timestamp(ds))]
    return float(s["turn_b"].iloc[0]) if len(s) else np.nan

B["adv20_pre"] = [adv20_pre(r.ticker, r.event) for r in B.itertuples()]
B["adv_washout"] = [adv_on(r.ticker, r.event) for r in B.itertuples()]
B["cap_vnd_bn"] = X * B["adv20_pre"] * D            # max VND (bn) allowed in one name
assert B["adv20_pre"].notna().all(), "missing ADV20 for some position"

print(f"\nADV20(pre-washout) vs ADV(washout day): median ratio = "
      f"{(B['adv20_pre'] / B['adv_washout']).median():.2f}  "
      f"(<1 confirms the washout day is a volume spike -> must not be the baseline)")
print(f"thinnest name per event (ADV20_pre, VND bn): "
      f"min={B.groupby('event')['adv20_pre'].min().min():.2f}  "
      f"median={B.groupby('event')['adv20_pre'].min().median():.2f}")

# ---- 3. does the cap BIND? -------------------------------------------------------------
# uncapped per-name VND = sleeve / n, where sleeve = NAV_book_LAG * capit_size.
# cap binds  <=>  sleeve / n > X * ADV20_i * D  for some name i.
def bind_report(sleeve_bn):
    b = B.copy()
    b["uncapped_bn"] = sleeve_bn / b["n"]
    b["binds"] = b["uncapped_bn"] > b["cap_vnd_bn"] + 1e-12
    ev = b.groupby("event")["binds"].any()
    return b, ev

print("\n" + "=" * 78)
print("CAP BINDING vs SLEEVE SIZE   (sleeve = NAV_book_LAG x capit_size)")
print("=" * 78)
print(f"  {'sleeve (VND bn)':>16s} {'events binding':>16s} {'positions binding':>19s}")
for s in [0.38, 0.75, 1.50, 3.75, 7.50, 15.0]:
    b, ev = bind_report(s)
    print(f"  {s:16.2f} {int(ev.sum()):>13d}/14 {int(b['binds'].sum()):>16d}/{len(b)}")

# ---- 4. PRIMARY ASSERTION — dormant at the scale the proposal was agreed on -------------
SLEEVE_REF = 0.38     # exp_capitexit/RESULT.md §3b: 14/14 events have capacity at 0.38 bn
b, ev = bind_report(SLEEVE_REF)
n_ev, n_pos = int(ev.sum()), int(b["binds"].sum())
print("\n" + "=" * 78)
print(f"SELFCHECK @ sleeve = {SLEEVE_REF} VND bn (the reference scale of the agreed proposal)")
print("=" * 78)
print(f"  events with cap binding    : {n_ev}/14   (expected 0)")
print(f"  positions with cap binding : {n_pos}/{len(b)}   (expected 0)")
if n_ev == 0:
    print("  -> PASS: cap is DORMANT. Wiring it produces ZERO change in historical backtest")
    print("     behaviour and ZERO change in live sizing at the current sleeve scale.")
else:
    print("  -> FAIL: cap binds. STOP — either the formula is implemented wrong or the")
    print("     premise from job Taylor_20260720_164006 is wrong. Report before proceeding.")
    print(b[b["binds"]][["event","ticker","n","adv20_pre","cap_vnd_bn","uncapped_bn"]].to_string(index=False))

# self-check 0 VND: no NAV path is touched by this change (dormant safeguard, and the
# backtest engine sizes CAPIT at tier level `wt/len(names)` with no per-name weight vector
# — see REPORT.md §2). The invariant asserted here is exactly that: the capped weight equals
# the uncapped weight for every historical position at the reference scale.
delta = (b["uncapped_bn"] - np.minimum(b["uncapped_bn"], b["cap_vnd_bn"])).sum()
print(f"\n  self-check: total VND (bn) reallocated by the cap over all 14 events = {delta:.6f}")
print(f"  self-check 0 VND: {'PASS' if abs(delta) < 1e-12 else 'FAIL'}")

B.to_csv(f"{OUT}/adv_cap_selfcheck.csv", index=False)
print(f"\nwrote {OUT}/adv_cap_selfcheck.csv")
