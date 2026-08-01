#!/usr/bin/env python
"""CAPIT quality-exit — descriptive panel (job Taylor_20260801_073610).

Reads the PINNED control run's CAPIT transaction ledger (so entry dates/prices/shares are the
real ones the pinned R3 backtest produced, not a re-derivation) and answers, per holding:
  - did this name fall BELOW the CAPIT entry-quality gate at any point inside its hold window?
  - if so, on which session, driven by which leg (ROE/ROIC multi-year vs FSCORE vs 8L rating)?
  - what would exiting at T+1 Open after that session have returned vs holding to TIME?

Pure measurement. No production wiring. Snapshot: bq_cache_asof20260729_postrestate.
"""
import os
import sys

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
CACHE = os.path.join(WORKDIR, "data", "bq_cache_asof20260729_postrestate")
CTRL = os.path.join(WORKDIR, "data",
                    "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg"
                    "_wtnamecap_exp_capsz_ctrl_univpit.csv")
OUT = os.path.join(WORKDIR, "data", "capit_qexit_20260801")

# ---------------------------------------------------------------- 1. CAPIT holdings from ctrl run
df = pd.read_csv(CTRL)
tx = df[(df.record_type == "TX") & df["play_type"].astype(str).str.startswith("CAPIT")].copy()
tx["ymd"] = pd.to_datetime(tx["ymd"])
buys = tx[(tx.action == "buy") & (tx.reason == "ENTRY_FILL")]
sells = tx[(tx.action == "sell") & (tx.reason != "ABANDONED_REFUND")]

hold = []
for hid, g in buys.groupby("holding_id"):
    sh = g["shares"].sum()
    cost = g["buy_amount"].sum()
    s = sells[sells.holding_id == hid]
    if not len(s) or sh <= 0:
        continue
    hold.append({
        "holding_id": hid, "ticker": g["ticker"].iloc[0], "book": g["book"].iloc[0],
        "tier": g["play_type"].iloc[0], "entry": g["ymd"].min(), "entry_px": cost / sh,
        "exit": s["ymd"].iloc[0], "exit_px": float(s["adj_price"].iloc[0]),
        "shares": sh, "cost": cost, "proceeds": float(s["sell_amount"].sum()),
    })
H = pd.DataFrame(hold).sort_values(["entry", "ticker"]).reset_index(drop=True)
H["event"] = H["tier"].str.extract(r"_E(\d+)$").astype(int)
H["ret_hold"] = H["exit_px"] / H["entry_px"] - 1
print(f"[1] {len(H)} CAPIT holdings, {H.event.nunique()} events, "
      f"{H.entry.min().date()} -> {H.exit.max().date()}")

# ---------------------------------------------------------------- 2. quality panel
names = sorted(H.ticker.unique())
yrs = sorted(int(f[:4]) for f in os.listdir(os.path.join(CACHE, "ticker_prune")) if f.endswith(".parquet"))
qp = pd.concat([pd.read_parquet(os.path.join(CACHE, "ticker_prune", f"{y}.parquet"),
                                columns=["ticker", "time", "ROE_Min5Y", "ROIC5Y", "FSCORE"])
                for y in yrs], ignore_index=True)
qp = qp[qp.ticker.isin(names)].copy()
qp["time"] = pd.to_datetime(qp["time"])
qp["ok_nf"] = (qp.ROE_Min5Y >= 0.12) & (qp.ROIC5Y >= 0.10)      # multi-year quality legs
qp["ok_fs"] = (qp.FSCORE >= 6)                                   # Piotroski leg
qp["ok_floor"] = qp.ok_nf & qp.ok_fs                             # the CAPIT entry gate itself

r8 = pd.read_parquet(os.path.join(CACHE, "fa_ratings_8l.parquet"))
r8 = r8[r8.ticker.isin(names)].copy()
r8["time"] = pd.to_datetime(r8["time"])
r8 = r8.sort_values("time").drop_duplicates(["ticker", "time"], keep="last")

# session calendar = the pinned run's own DAILY records (identical to engine vni_dates)
vd = pd.DatetimeIndex(sorted(pd.to_datetime(df[df.record_type == "DAILY"]["ymd"]).unique()))

QCOLS = {"floor": "ok_floor", "floornf": "ok_nf", "fscore": "ok_fs"}
bad = {}
for m, col in QCOLS.items():
    s = qp.set_index(["ticker", "time"])[col]
    bad[m] = {k: True for k, v in s.items() if not bool(v)}
# NaN fundamentals: rows simply absent from ticker_prune are unknown, not "bad" -> treated as OK
# (conservative: we never fire an exit on missing data).
r8bad = {}
for tk, g in r8.groupby("ticker"):
    s = g.set_index("time")["rating"].reindex(vd, method="ffill")   # as-of, no hindsight
    for d, v in s.items():
        if pd.notna(v) and float(v) > 3:
            r8bad[(tk, d)] = True
bad["r8l"] = r8bad

# ---------------------------------------------------------------- 3. price panel for exit pricing
px = pd.concat([pd.read_parquet(os.path.join(CACHE, "ticker_prune", f"{y}.parquet"),
                                columns=["ticker", "time", "Open", "Close"]) for y in yrs],
               ignore_index=True)
px = px[px.ticker.isin(names)].copy()
px["time"] = pd.to_datetime(px["time"])
opens = {(t, d): o for t, d, o in zip(px.ticker, px.time, px.Open) if pd.notna(o)}
closes = {(t, d): c for t, d, c in zip(px.ticker, px.time, px.Close) if pd.notna(c)}

vidx = {d: i for i, d in enumerate(vd)}


def flag_date(metric, tk, d0, d1, K):
    """First session in (d0, d1] with K consecutive below-floor sessions."""
    b = bad[metric]
    i0, i1 = vidx.get(d0), vidx.get(d1)
    if i0 is None or i1 is None:
        return None
    run = 0
    for j in range(i0 + 1, i1 + 1):
        run = run + 1 if b.get((tk, vd[j])) else 0
        if run >= max(K, 1):
            return vd[j]
    return None


def exit_px_after(tk, d):
    """T+1 Open after signal session d (engine convention); fall back to that session's Close."""
    i = vidx.get(d)
    if i is None:
        return None
    for j in range(i + 1, min(i + 4, len(vd))):
        p = opens.get((tk, vd[j])) or closes.get((tk, vd[j]))
        if p:
            return float(p), vd[j]
    return None


rows = []
for _, h in H.iterrows():
    r = {k: h[k] for k in ("holding_id", "ticker", "book", "tier", "event", "entry", "exit",
                           "entry_px", "exit_px", "ret_hold", "cost")}
    for metric in ("floor", "floornf", "fscore", "r8l"):
        for K in (1, 5, 20):
            fd = flag_date(metric, h.ticker, h.entry, h.exit, K)
            r[f"{metric}_K{K}_date"] = fd
            if fd is not None:
                e = exit_px_after(h.ticker, fd)
                r[f"{metric}_K{K}_ret"] = (e[0] / h.entry_px - 1) if e else np.nan
                r[f"{metric}_K{K}_days"] = vidx[e[1]] - vidx[h.entry] if e else np.nan
            else:
                r[f"{metric}_K{K}_ret"] = h.ret_hold          # never flagged -> same as baseline
                r[f"{metric}_K{K}_days"] = vidx[h.exit] - vidx[h.entry]
    rows.append(r)
P = pd.DataFrame(rows)
P.to_csv(os.path.join(OUT, "holdings_panel.csv"), index=False)

# ---------------------------------------------------------------- 4. report
print("\n[2] Flag frequency inside the hold window (85 holdings):")
for metric in ("floor", "floornf", "fscore", "r8l"):
    for K in (1, 5, 20):
        n = P[f"{metric}_K{K}_date"].notna().sum()
        print(f"    {metric:8s} K={K:2d}: {n:3d}/{len(P)} flagged ({n/len(P)*100:4.1f}%)")

print("\n[3] Cost-weighted sleeve return, baseline vs exit-on-flag (frac=1.0):")
w = P["cost"] / P["cost"].sum()
base = float((w * P.ret_hold).sum())
print(f"    baseline (hold 60td)            : {base*100:+6.2f}%  (equal-wt {P.ret_hold.mean()*100:+.2f}%)")
for metric in ("floor", "floornf", "fscore", "r8l"):
    for K in (1, 5, 20):
        v = float((w * P[f"{metric}_K{K}_ret"]).sum())
        n = P[f"{metric}_K{K}_date"].notna().sum()
        print(f"    exit {metric:8s} K={K:2d} (n_flag={n:3d}): {v*100:+6.2f}%   delta {(v-base)*100:+5.2f}pp")

print("\n[4] Flagged holdings only — did the flag pick the losers? (metric=floor, K=1)")
m = P["floor_K1_date"].notna()
if m.any():
    print(f"    flagged   n={m.sum():3d}  mean hold-to-TIME ret {P.loc[m,'ret_hold'].mean()*100:+6.2f}%  "
          f"exit-at-flag {P.loc[m,'floor_K1_ret'].mean()*100:+6.2f}%")
    print(f"    unflagged n={(~m).sum():3d}  mean hold-to-TIME ret {P.loc[~m,'ret_hold'].mean()*100:+6.2f}%")
    print("\n    per-holding detail (flagged):")
    d = P.loc[m, ["event", "ticker", "book", "entry", "floor_K1_date", "ret_hold", "floor_K1_ret"]]
    d = d.assign(delta=(d.floor_K1_ret - d.ret_hold) * 100)
    print(d.to_string(index=False))

print("\n[5] Per-event roll-up (cost-weighted within event), floor K=1:")
for ev, g in P.groupby("event"):
    ww = g["cost"] / g["cost"].sum()
    b = float((ww * g.ret_hold).sum()); q = float((ww * g.floor_K1_ret).sum())
    nf = g["floor_K1_date"].notna().sum()
    print(f"    E{ev:<3d} {g.entry.min().date()}  n={len(g):2d} flagged={nf:2d}  "
          f"hold {b*100:+7.2f}%  qexit {q*100:+7.2f}%  delta {(q-b)*100:+6.2f}pp")
