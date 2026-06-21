# -*- coding: utf-8 -*-
"""audit_spotcheck_generic.py — independent verifier for ANY audit file produced by the
generic N-book emitter (audit_lib.emit_audit_file). Reads the book labels from the META 'books'
row, then verifies for each book: price sampling vs raw BQ, amount identities, cash-flow identity,
final NAV identity; and recomputes the headline metrics from the DAILY combined_nav.
Usage: python data/audit_spotcheck_generic.py <N_sample> <audit_file.csv>
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
FILE = sys.argv[2]
A = pd.read_csv(FILE, low_memory=False)
meta = A[A["record_type"] == "META"].set_index("key")["value"]
books = [b.strip() for b in str(meta.get("books", "")).split(",") if b.strip()]
init_by_book = {b: float(x) for b, x in (kv.split(":") for kv in str(meta.get("init_by_book", "")).split(";") if ":" in kv)}
tx = A[A["record_type"] == "TX"].copy(); tx["ymd"] = pd.to_datetime(tx["ymd"])
daily = A[A["record_type"] == "DAILY"].copy(); daily["ymd"] = pd.to_datetime(daily["ymd"])
metric = A[A["record_type"] == "METRIC"].set_index("key")["value"]
print(f"file {os.path.basename(FILE)} | books {books} | TX {len(tx):,} | DAILY {len(daily):,}")

# 1. amount identities
b = tx[tx["action"] == "buy"]; s = tx[(tx["action"] == "sell") & (~tx["reason"].astype(str).str.startswith("MTM"))]
eb = (b["buy_amount"] - b["shares"] * b["adj_price"]).abs() / b["buy_amount"].clip(lower=1)
es = (s["sell_amount"] - s["shares"] * s["adj_price"]).abs() / s["sell_amount"].clip(lower=1)
print(f"[1] amount identity: buy {eb.max():.1e} | sell {es.max():.1e}")

# 2. price spot-check vs BQ (Open for fills, Close ffill for ETF + MTM)
stk = tx[(tx["ticker"] != "E1VFVN30") & tx["adj_price"].notna() & (tx["ticker"] != "(pending_partial_fill)")]
samp = stk.sample(min(N, len(stk)), random_state=7)
etf = tx[(tx["ticker"] == "E1VFVN30") & tx["adj_price"].notna()]
if len(etf): samp = pd.concat([samp, etf.sample(min(50, len(etf)), random_state=7)])
keys = samp[["ticker", "ymd"]].drop_duplicates()
in_t = ",".join(f"'{t}'" for t in keys["ticker"].unique())
mind = (keys["ymd"].min() - pd.Timedelta(days=20)).date(); maxd = keys["ymd"].max().date()
px = bq(f"SELECT t.ticker,t.time,t.Open,t.Close FROM tav2_bq.ticker t WHERE t.ticker IN ({in_t}) AND t.time BETWEEN DATE '{mind}' AND DATE '{maxd}'")
px["time"] = pd.to_datetime(px["time"])
po = {(r.ticker, r.time): r.Open for r in px.itertuples()}
cw = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill()
def cff(tk, d):
    if tk not in cw.columns: return None
    v = cw[tk].reindex([d], method="ffill"); return float(v.iloc[0]) if len(v) and pd.notna(v.iloc[0]) else None
bad = 0
for r in samp.itertuples():
    if r.ticker == "E1VFVN30" or str(r.reason).startswith("MTM"):
        ref = cff(r.ticker, r.ymd); ok = ref and abs(r.adj_price/ref-1) < 0.005
    else:
        ro = po.get((r.ticker, r.ymd)); rc = cff(r.ticker, r.ymd)
        ok = any(x and abs(r.adj_price/x-1) < 0.005 for x in (ro, rc))
    if not ok: bad += 1
print(f"[2] price vs BQ: {len(samp)} sampled, {bad} mismatches")

# 3. per-book cash-flow identity
fl = tx[~tx["reason"].astype(str).str.startswith("MTM")].copy()
fl["net"] = np.where(fl["action"] == "sell", fl["sell_amount"] - fl["fee"], -(fl["buy_amount"] + fl["fee"]))
d = daily.set_index("ymd")
for bk in books:
    col = f"{bk.lower()}_cash_ref"
    if col not in d.columns: print(f"[3] {bk}: no col {col}"); continue
    f = fl[fl["book"] == bk].groupby("ymd")["net"].sum()
    cash = d[col].astype(float); dc = cash.diff(); dc.iloc[0] = cash.iloc[0] - init_by_book.get(bk, 25e9)
    net = f.reindex(cash.index).fillna(0)
    carry = d[f"{bk.lower()}_cash_carry"].astype(float) if f"{bk.lower()}_cash_carry" in d.columns else 0.0
    err = (dc - net - carry).abs().max()
    cmax = float(np.abs(carry).max()) if hasattr(carry, "max") else 0.0
    print(f"[3] {bk} cash-flow identity max err: {err:,.2f} VND (carry incl; max daily carry {cmax:,.0f} VND = borrow on neg cash)")

# 4. combination check: static sum, OR ensemble-switched recurrence (cap_switched present)
if "cap_switched" in d.columns and "ensemble_signal" in d.columns:
    # V12.1 ensemble: combined = nav_bal_ref + cap_switched; replay cap_switched from VN30/LAGGED returns
    SW = 0.005
    nb = d["nav_bal_ref"].astype(float); nv = d["nav_vn30_ref"].astype(float); nl = d["nav_lagged_ref"].astype(float)
    sgc = d["ensemble_signal"].astype(float).astype(int).values
    v30r = nv.pct_change().fillna(0).values; lagr = nl.pct_change().fillna(0).values
    sp = np.full(len(d), 25e9); prev = int(sgc[0])
    for i in range(1, len(d)):
        c = int(sgc[i]); sp[i] = sp[i-1]*(1-SW) if c != prev else sp[i-1]; sp[i] *= (1+(v30r[i] if c == 1 else lagr[i])); prev = c
    err_rec = np.abs(sp - d["cap_switched"].astype(float).values).max()
    err_comb = (nb + d["cap_switched"].astype(float) - d["combined_nav"].astype(float)).abs().max()
    print(f"[4] switched-recurrence replay err {err_rec:,.2f} VND | combined=nav_bal+cap_switched err {err_comb:,.2f} VND")
else:
    nav_cols = [f"nav_{bk.lower()}_ref" for bk in books if f"nav_{bk.lower()}_ref" in d.columns]
    recomb = sum(d[c].astype(float) for c in nav_cols)
    err = (recomb - d["combined_nav"].astype(float)).abs().max()
    print(f"[4] sum(book NAV refs) vs combined_nav max err: {err:,.2f} VND")

# 5. metric recompute
s_nav = d["combined_nav"].astype(float); yrs = (s_nav.index[-1]-s_nav.index[0]).days/365.25
r = s_nav.pct_change().dropna()
cagr = (s_nav.iloc[-1]/s_nav.iloc[0])**(1/yrs)-1; sh = r.mean()/r.std()*np.sqrt(252); mdd = (s_nav/s_nav.cummax()-1).min()
print(f"[5] recomputed CAGR {cagr*100:.2f}% (file {float(metric['cagr'])*100:.2f}%) | "
      f"Sharpe {sh:.3f} (file {float(metric['sharpe_252']):.3f}) | MaxDD {mdd*100:.2f}% (file {float(metric['max_dd'])*100:.2f}%)")
print("done.")
