# -*- coding: utf-8 -*-
"""exp_dc3book_factorcheck_20260825.py — Phan B: factor-neutral check.

Is DC's BULL outperformance (Q4, job Taylor_20260825_145251: ConvergePort
eq-weight BULL gross +64.1% full / +68.9% OOS, vs baseline park +45.3%/+46.5%)
alpha from the double-confirm gate, or just beta from a Banking/Securities-
heavy universe re-rating hard in BULL?

Control leg: naive equal-weight buy-and-hold basket of the 5 Banking names in
DC's universe (MBB/ACB/HDB/TCB/VCB) -- NO sector-lens gate, NO 8L rating gate,
always fully invested (100%, no parking/idle cash) -- computed over the exact
same DT5G BULL sessions. If naive-basket gross ~= DC gross -> pure beta. If DC
clearly beats naive-basket -> the double-confirm gate adds real alpha on top
of the sector beta.

RESEARCH ONLY. Reads local BQ cache parquets (duckdb, read-only). No writes to
production files.
"""
import os, sys
import numpy as np
import pandas as pd
import duckdb

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
CACHE = os.path.join(WORKDIR, "data", "bq_cache")
OUTDIR = os.path.dirname(os.path.abspath(__file__))

BANK5 = ["MBB", "ACB", "HDB", "TCB", "VCB"]
STATE_NAMES = {0: "CRISIS", 1: "BEAR", 2: "NEUTRAL", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
# NOTE: DT5G live table uses 1..5 (CRISIS..EXBULL); golive audit CSV uses a
# different 1..5 mapping (3=NEUTRAL). We read DT5G's own `state` column
# directly and map by its own convention (verified below by cross-checking
# against known NEUTRAL/BULL session counts from job _134238: NEUTRAL~1895,
# BULL~422 full-period in the golive numbering; DT5G table may differ
# slightly in session count due to different calendar/backfill -- printed for
# audit, not assumed).

OOS_START = pd.Timestamp("2020-01-01")


def con():
    c = duckdb.connect(":memory:")
    c.execute("SET threads=1")
    return c


def load_dt5g():
    c = con()
    df = c.execute(
        f"SELECT time, state FROM read_parquet('{CACHE}/vnindex_5state_dt5g_live.parquet') ORDER BY time"
    ).df()
    c.close()
    df["time"] = pd.to_datetime(df["time"])
    return df


def load_bank_prices():
    c = con()
    q = ",".join(f"'{t}'" for t in BANK5)
    df = c.execute(f"""
        SELECT time, ticker, Close
        FROM read_parquet('{CACHE}/ticker/*.parquet')
        WHERE ticker IN ({q})
        ORDER BY time, ticker""").df()
    c.close()
    df["time"] = pd.to_datetime(df["time"])
    return df


def main():
    print("Loading DT5G state series (live table, local cache) ...")
    dt5g = load_dt5g()
    print(f"  DT5G range: {dt5g['time'].min().date()} -> {dt5g['time'].max().date()}, "
          f"{len(dt5g)} rows, state values present: {sorted(dt5g['state'].dropna().unique().astype(int))}")
    print(f"  session counts by state (DT5G raw numbering):")
    print(dt5g["state"].value_counts().sort_index())

    print("\nLoading Bank5 (MBB/ACB/HDB/TCB/VCB) daily prices ...")
    px = load_bank_prices()
    wide = px.pivot_table(index="time", columns="ticker", values="Close")
    ret = wide[BANK5].pct_change()
    # naive equal-weight, rebalanced daily to equal-weight (upper bound: no
    # rebalance-drag friction charged, matches "always fully invested" framing)
    naive_ret = ret.mean(axis=1)

    state = dt5g.set_index("time")["state"].reindex(naive_ret.index).ffill()

    # infer which raw DT5G code == BULL by cross-referencing known full-period
    # BULL session count (~422, from job _134238 golive numbering, 1=CRISIS..5=EXBULL)
    vc = state.value_counts().sort_index()
    print(f"\nnaive_ret aligned session counts by DT5G raw state code:\n{vc}")

    full_rows = []
    for st in sorted(state.dropna().unique()):
        sub = naive_ret[state == st]
        n = len(sub.dropna())
        ann = sub.mean() * 252
        full_rows.append(("naive_bank5_FULL", int(st), n, ann))

    oos_mask = naive_ret.index >= OOS_START
    oos_rows = []
    for st in sorted(state.dropna().unique()):
        sub = naive_ret[(state == st) & pd.Series(oos_mask, index=naive_ret.index)]
        n = len(sub.dropna())
        if n == 0:
            continue
        ann = sub.mean() * 252
        oos_rows.append(("naive_bank5_OOS2020+", int(st), n, ann))

    print("\n" + "=" * 78)
    print("Naive Bank5 equal-weight (no gate, always 100% invested) gross by DT5G state")
    print("=" * 78)
    print(f"{'window':<22}{'state_code':>11}{'N':>7}{'ann_gross':>12}")
    for r in full_rows + oos_rows:
        print(f"{r[0]:<22}{r[1]:>11}{r[2]:>7}{r[3]*100:>11.2f}%")

    out = pd.DataFrame(full_rows + oos_rows, columns=["config", "dt5g_state_code", "n_sessions", "ann_gross"])
    outcsv = os.path.join(OUTDIR, "exp_dc3book_factorcheck_naive_bank5.csv")
    out.to_csv(outcsv, index=False)
    print(f"\nwrote {outcsv}")

    print("\n--- FULL series stats (self-check) ---")
    print(f"naive_bank5 mean daily ret: {naive_ret.mean():.6f}, std: {naive_ret.std():.6f}, "
          f"N valid days: {naive_ret.dropna().shape[0]}")
    print(f"any NaN in state alignment: {state.isna().sum()} / {len(state)}")


if __name__ == "__main__":
    main()
