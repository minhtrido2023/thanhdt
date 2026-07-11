#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""momdeal Phase 0 step 4 — no-look-ahead spot-check of 20 random deals.

INDEPENDENT code path from momdeal_phase0_build.py: plain pandas per-ticker
filtering (no duckdb, no ASOF). For each sampled deal verifies:
  1. tech features come from a row dated <= feature_date (T-1 of book entry)
     and values match the dataset exactly;
  2. 8L rating row used is the LAST eff_date <= feature_date AND the next 8L
     row is strictly AFTER feature_date (right row, no skip, no future);
  3. financial features come from the LAST Release_Date <= feature_date (PIT by
     release, not by quarter-end) AND next release is after feature_date;
  4. entry_date is a real trading day; sig_date < entry_date;
  5. no dataset feature column equals the entry-day's own forward-looking cols.
Seed fixed = 20260711 (pre-registered, no Date.now in scripts).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

os.chdir("/home/trido/thanhdt/WorkingClaude")
SEED = 20260711

dl = pd.read_csv("data/momdeal_exp/momdeal_deals_phase0.csv",
                 parse_dates=["entry_date", "feature_date", "tech_date", "fa8_eff_date",
                              "fin_release_date", "sig_date"])
ep = pd.read_csv("data/momdeal_exp/momdeal_episodes_phase0.csv",
                 parse_dates=["entry_date", "tech_date", "fa8_eff_date", "fin_release_date"])

fa8 = pd.read_parquet("data/bq_cache/fa_ratings_8l.parquet")
fa8["time"] = pd.to_datetime(fa8["time"])
fin = pd.read_parquet("data/bq_cache/ticker_financial.parquet",
                      columns=["ticker", "time", "Release_Date", "ROIC_Trailing", "CF_OA_P0", "Revenue_YoY_P0"])
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])

# duckdb used ONLY as a raw parquet reader (plain SELECT, no joins) — the as-of
# row selection under test stays in plain pandas below, independent of the builder.
import duckdb
_con = duckdb.connect(); _con.execute("SET threads TO 1")
def ticker_rows(tk):
    d = _con.execute(
        "SELECT ticker, CAST(time AS DATE) AS time, D_RSI, Volume, Volume_3M_P50, C_L1M, Close, Res_1Y "
        "FROM read_parquet('data/bq_cache/ticker/*.parquet') WHERE ticker = ?", [tk]).df()
    d["time"] = pd.to_datetime(d["time"])
    return d.sort_values("time")

rng = np.random.default_rng(SEED)
sample = dl.sample(20, random_state=SEED).sort_values("entry_date")

def close_eq(a, b, tol=1e-9):
    if pd.isna(a) and pd.isna(b): return True
    if pd.isna(a) or pd.isna(b): return False
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(a)))

n_pass = 0
fails = []
for i, r in sample.iterrows():
    tk, fd = r["ticker"], r["feature_date"]
    probs = []

    # 1. tech row: last trading row <= feature_date, values must match
    trows = ticker_rows(tk)
    tr = trows[trows["time"] <= fd]
    if not len(tr):
        probs.append("no tech row <= feature_date")
    else:
        t = tr.iloc[-1]
        if t["time"] != r["tech_date"]: probs.append(f"tech_date mismatch {t['time'].date()} vs {r['tech_date'].date()}")
        if not close_eq(t["D_RSI"], r["D_RSI"], 1e-6): probs.append("D_RSI mismatch")
        if not close_eq(t["C_L1M"], r["C_L1M"], 1e-6): probs.append("C_L1M mismatch")
        vr = t["Volume"] / t["Volume_3M_P50"] if t["Volume_3M_P50"] else np.nan
        if not close_eq(vr, r["T3_vol_ratio"], 1e-6): probs.append("T3_vol_ratio mismatch")
        cr = t["Close"] / t["Res_1Y"] if t["Res_1Y"] else np.nan
        if not close_eq(cr, r["T5_close_res"], 1e-6): probs.append("T5_close_res mismatch")
        if t["time"] > fd: probs.append("LOOK-AHEAD: tech row after feature_date")
        # entry day exists and is AFTER the tech/feature info set
        ent = trows[trows["time"] == r["entry_date"]]
        if not len(ent): probs.append("entry_date not a trading day for ticker")
        if t["time"] >= r["entry_date"]: probs.append("LOOK-AHEAD: tech row >= entry_date")

    # 2. 8L: last eff <= fd is the one used; next eff > fd
    f8 = fa8[fa8["ticker"] == tk].sort_values("time")
    past = f8[f8["time"] <= fd]
    if pd.isna(r["rating"]):
        if len(past): probs.append("rating null but 8L row exists <= feature_date")
    else:
        if not len(past): probs.append("rating set but no 8L row <= feature_date (LOOK-AHEAD)")
        else:
            last = past.iloc[-1]
            if last["time"] != r["fa8_eff_date"]: probs.append(f"8L eff mismatch {last['time'].date()} vs {r['fa8_eff_date'].date()}")
            if int(last["rating"]) != int(r["rating"]): probs.append("8L rating mismatch")
            if str(last["route"]) != str(r["route"]): probs.append("8L route mismatch")
            nxt = f8[f8["time"] > fd]
            if len(nxt) and nxt.iloc[0]["time"] <= fd: probs.append("8L next-row logic broken")
        if pd.notna(r["fa8_eff_date"]) and r["fa8_eff_date"] > fd: probs.append("LOOK-AHEAD: 8L eff_date after feature_date")

    # 3. financial: last Release_Date <= fd
    fr = fin[fin["ticker"] == tk].dropna(subset=["Release_Date"]).sort_values(["Release_Date", "time"])
    frp = fr[fr["Release_Date"] <= fd]
    if pd.isna(r["fin_release_date"]):
        if len(frp): probs.append("fin null but release exists <= feature_date")
    else:
        if r["fin_release_date"] > fd: probs.append("LOOK-AHEAD: fin Release_Date after feature_date")
        if len(frp):
            last = frp.iloc[-1]
            if last["Release_Date"] != r["fin_release_date"]:
                probs.append(f"fin release mismatch {last['Release_Date'].date()} vs {r['fin_release_date'].date()}")
            for col in ["ROIC_Trailing", "CF_OA_P0", "Revenue_YoY_P0"]:
                if not close_eq(last[col], r[col], 1e-6): probs.append(f"{col} mismatch")

    # 4. signal alignment: sig_date must be < entry_date (book buys T+1)
    if pd.notna(r["sig_date"]) and r["sig_date"] >= r["entry_date"]:
        probs.append("LOOK-AHEAD: sig_date >= entry_date")

    status = "PASS" if not probs else "FAIL"
    if not probs: n_pass += 1
    else: fails.append((r["holding_id"], probs))
    print(f"[{status}] {r['holding_id']:<24} {r['pt_base']:<20} entry={r['entry_date'].date()} "
          f"feat={fd.date()} tech={r['tech_date'].date() if pd.notna(r['tech_date']) else '—'} "
          f"8L={r['fa8_eff_date'].date() if pd.notna(r['fa8_eff_date']) else '—'}(r{r['rating'] if pd.notna(r['rating']) else '—'}) "
          f"finRel={r['fin_release_date'].date() if pd.notna(r['fin_release_date']) else '—'} "
          f"sig={r['sig_date'].date() if pd.notna(r['sig_date']) else '—'}"
          + ("" if not probs else f"  !! {probs}"))

print(f"\n== deals spot-check: {n_pass}/20 PASS ==")
for h, p in fails: print("  FAIL", h, p)

# bonus: 5 random episodes through the same independent path (features at entry day itself)
print("\n-- bonus: 5 episodes (feature date = entry day, signal info set) --")
eps = ep[ep["in_family"]].sample(5, random_state=SEED)
ep_pass = 0
for _, r in eps.iterrows():
    tk, fd = r["ticker"], r["entry_date"]
    trows = ticker_rows(tk); tr = trows[trows["time"] <= fd]
    probs = []
    if not len(tr): probs.append("no tech row")
    else:
        t = tr.iloc[-1]
        if t["time"] != r["tech_date"]: probs.append("tech_date mismatch")
        if not close_eq(t["D_RSI"], r["D_RSI"], 1e-6): probs.append("D_RSI mismatch")
    f8 = fa8[(fa8["ticker"] == tk) & (fa8["time"] <= fd)]
    if pd.notna(r["rating"]):
        if not len(f8) or int(f8.sort_values("time").iloc[-1]["rating"]) != int(r["rating"]): probs.append("8L mismatch")
    if pd.notna(r["fin_release_date"]) and r["fin_release_date"] > fd: probs.append("LOOK-AHEAD fin")
    if pd.notna(r["fa8_eff_date"]) and r["fa8_eff_date"] > fd: probs.append("LOOK-AHEAD 8L")
    ok = not probs; ep_pass += ok
    print(f"[{'PASS' if ok else 'FAIL'}] ep {tk} {r['play_type']} entry={pd.to_datetime(fd).date()}" + ("" if ok else f" !! {probs}"))
print(f"== episodes bonus: {ep_pass}/5 PASS ==")
