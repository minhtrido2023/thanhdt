# -*- coding: utf-8 -*-
"""v23_audit_spotcheck.py — independent spot-check of data/v23_golive_audit_2014_now.csv.
Plays the role of the external audit bot on a sample: verifies TX prices against raw
tav2_bq.ticker, amount identities, fee bounds, cash-flow identity, allocator replay,
and recomputes the headline metrics from DAILY rows.
Run: python data/v23_audit_spotcheck.py [n_sample]
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq

N_SAMPLE = int(sys.argv[1]) if len(sys.argv) > 1 else 400
AUDIT_FILE = sys.argv[2] if len(sys.argv) > 2 else os.path.join(WORKDIR, "data", "v23_golive_audit_2014_now.csv")
A = pd.read_csv(AUDIT_FILE, low_memory=False)
_mode_meta = A[(A["record_type"] == "META") & (A["key"] == "mode")]["value"]
IS_ALLOC = str(_mode_meta.iloc[0]).strip().lower().startswith("v23a") if len(_mode_meta) else True
print(f"file: {os.path.basename(AUDIT_FILE)} | mode: {'ALLOCATOR (v23a)' if IS_ALLOC else 'STATIC 50/50 (v23c)'}")
tx = A[A["record_type"] == "TX"].copy()
tx["ymd"] = pd.to_datetime(tx["ymd"])
# Parking vehicle: real ETF (E1VFVN30) or synthetic ex-VIC basket (ETF_LIQ=custom*, §5).
_meta = A[A["record_type"] == "META"].set_index("key")["value"]
CB_MODE = str(_meta.get("custom_basket_mode", "")).split()[0] if "custom_basket_mode" in _meta.index else ""
CUSTOM_MODE = CB_MODE.startswith("custom")
_bk_tk = A[A["record_type"] == "CUSTOM_BASKET"]["ticker"]
PARK = (_bk_tk.iloc[0] if len(_bk_tk) else "CUSTOM_VN30EXVIC") if CUSTOM_MODE else "E1VFVN30"
CB_IS_PIT = CB_MODE in ("custompit", "custompitq", "custompitg", "custompitgq")
# PIT rebuild params: prefer the explicit META string, else infer from the mode name
_pp = str(_meta.get("custom_basket_pit_params", "")) if "custom_basket_pit_params" in _meta.index else ""
def _kv(s, k, d):
    import re
    m = re.search(rf"{k}=(\S+)", s); return m.group(1) if m else d
CB_QUALITY = _kv(_pp, "quality", "tilt" if CB_MODE in ("custompitq", "custompitgq") else "none")
CB_REBAL = _kv(_pp, "rebal", "q2m5" if CB_MODE in ("custompitg", "custompitgq") else "qstart")
_g = _kv(_pp, "gate_rating", "3" if CB_MODE in ("custompitg", "custompitgq") else "None")
CB_GATE = None if _g in ("None", "none") else int(_g)
CB_WT = _kv(_pp, "weight_scheme", "capwt")   # de-concentration review 2026-06-15; legacy files = capwt
CB_TOPN = int(_kv(_pp, "top_n", "30"))       # C+D size x cap sweep 2026-06-16; legacy files = 30 / 0.10
CB_NAMECAP = float(_kv(_pp, "name_cap", "0.10"))
_qt = _kv(_pp, "qtilt", "")                  # dir B tilt-strength sweep 2026-06-16; legacy = unset -> default
CB_QTILT = ({int(k): float(v) for k, v in (p.split(":") for p in _qt.split(";"))} if _qt else None)
print(f"parking vehicle: {PARK}" + (f"  (mode={CB_MODE}, wt={CB_WT})" if CUSTOM_MODE else ""))
daily = A[A["record_type"] == "DAILY"].copy()
daily["ymd"] = pd.to_datetime(daily["ymd"])
metric = A[A["record_type"] == "METRIC"].set_index("key")["value"]
INIT_TOTAL = float(metric["init_nav_vnd"])      # scale-aware: 50e9 default, or NAV_TOTAL_B sweep
INIT_BOOK = INIT_TOTAL / 2.0                     # BAL/LAG each get half
print(f"audit file: {len(A):,} rows | TX {len(tx):,} | DAILY {len(daily):,} | init {INIT_TOTAL/1e9:.0f}B")

# ---------- 1. amount identities (ALL rows, no BQ needed) ----------
b = tx[tx["action"] == "buy"]
s = tx[(tx["action"] == "sell") & (~tx["reason"].astype(str).str.startswith("MTM"))]
err_b = (b["buy_amount"] - b["shares"] * b["adj_price"]).abs() / b["buy_amount"].clip(lower=1)
err_s = (s["sell_amount"] - s["shares"] * s["adj_price"]).abs() / s["sell_amount"].clip(lower=1)
print(f"[1] amount identity: buy max rel err {err_b.max():.2e} | sell max rel err {err_s.max():.2e}")

# ---------- 2. fee bounds ----------
fb = (b["fee"] / b["buy_amount"].clip(lower=1)).describe()
fs = (s["fee"] / s["sell_amount"].clip(lower=1)).describe()
print(f"[2] fee/buy_amount: min {fb['min']:.5f} max {fb['max']:.5f} (expect 0.0015..0.0025 stocks, 0.0015 ETF)")
print(f"    fee/sell_amount: min {fs['min']:.5f} max {fs['max']:.5f} (expect 0.0015 ETF .. ~0.0095 stocks)")

# ---------- 3. price spot-check vs raw BQ ----------
# Stock fills (T+1 Open) -> verify against raw tav2_bq.ticker. The parking vehicle is handled
# separately (real-ETF Close, or synthetic basket reconstructed from BQ in custom mode) in [3b].
stk = tx[(tx["ticker"] != PARK) & tx["adj_price"].notna()].copy()
samp = stk.sample(min(N_SAMPLE, len(stk)), random_state=42)
if not CUSTOM_MODE:
    etf = tx[(tx["ticker"] == PARK) & tx["adj_price"].notna()].sample(
        min(60, len(tx[tx["ticker"] == PARK])), random_state=42)
    pairs = pd.concat([samp, etf])
else:
    pairs = samp
keys = pairs[["ticker", "ymd"]].drop_duplicates()
in_t = ",".join(f"'{t}'" for t in keys["ticker"].unique())
in_d = ",".join(f"DATE '{d.date()}'" for d in keys["ymd"].unique())
# fetch a 14-day lookback so MTM marks on halted tickers (last Close <= ymd) resolve
min_d = (keys["ymd"].min() - pd.Timedelta(days=20)).date()
px = bq(f"""SELECT t.ticker, t.time, t.Open, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({in_t}) AND t.time BETWEEN DATE '{min_d}' AND DATE '{keys['ymd'].max().date()}'""")
px["time"] = pd.to_datetime(px["time"])
px_o = {(r.ticker, r.time): r.Open for r in px.itertuples()}
px_c = {(r.ticker, r.time): r.Close for r in px.itertuples()}
# forward-filled Close per ticker for MTM verification
_cwide = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill()
def close_ffill(tk, d):
    if tk not in _cwide.columns: return None
    sub = _cwide[tk].reindex([d], method="ffill")
    return float(sub.iloc[0]) if len(sub) and pd.notna(sub.iloc[0]) else None
bad = []
for r in pairs.itertuples():
    k = (r.ticker, r.ymd)
    if r.ticker == "E1VFVN30" or str(r.reason).startswith("MTM"):
        ref = px_c.get(k)          # exact-day Close first
        if ref is None or pd.isna(ref):
            ref = close_ffill(r.ticker, r.ymd)   # halted ticker: last Close <= ymd
        ok = ref is not None and not pd.isna(ref) and abs(r.adj_price / ref - 1) < 0.005
        if not ok: bad.append((r.ticker, str(r.ymd.date()), r.action, r.adj_price, ref, "Close_ffill"))
    else:
        ref_o, ref_c = px_o.get(k), px_c.get(k)
        ok = False
        for ref in (ref_o, ref_c):  # fills at Open; engine falls back to Close if Open missing
            if ref is not None and not pd.isna(ref) and abs(r.adj_price / ref - 1) < 0.005:
                ok = True; break
        if not ok: bad.append((r.ticker, str(r.ymd.date()), r.action, r.adj_price, ref_o, "Open"))
print(f"[3] price spot-check vs BQ: {len(pairs)} sampled, {len(bad)} mismatches")
for x in bad[:15]: print("    MISMATCH", x)

# ---------- 3b. custom parking basket: rebuild from raw BQ and verify ----------
if CUSTOM_MODE:
    import custom_basket as cbm
    d0 = pd.to_datetime(daily["ymd"]).min().date(); d1 = pd.to_datetime(daily["ymd"]).max().date()
    if CB_IS_PIT:
        # (a) rebuild PIT basket deterministically from BQ (membership re-derived from prior-quarter liq)
        lvl_bq, _, mem_bq, _ = cbm.build_pit(bq, str(d0), str(d1), quality=CB_QUALITY,
                                             rebal=CB_REBAL, gate_rating=CB_GATE, weight_scheme=CB_WT,
                                             top_n=CB_TOPN, name_cap=CB_NAMECAP, qtilt=CB_QTILT)
        # membership cross-check: file's per-quarter CUSTOM_MEMBERS vs BQ re-derivation
        fm = A[A["record_type"] == "CUSTOM_MEMBERS"][["ymd", "ticker"]].copy()
        file_pairs = set(zip(fm["ymd"].astype(str), fm["ticker"]))
        bq_pairs = set(zip(mem_bq["rebal_date"].astype(str), mem_bq["ticker"]))
        members_match = file_pairs == bq_pairs
    else:
        # (a) static: file member list must match deterministic re-selection from BQ
        cm = str(_meta.get("custom_basket_members", "")).split("  ")[0].split(",")
        bq_members = cbm.select_members(bq)
        members_match = set(bq_members) == set(cm)
        lvl_bq, _, _ = cbm.build(bq, cm, str(d0), str(d1))
    lvl_bq = pd.Series(lvl_bq)
    bk = A[A["record_type"] == "CUSTOM_BASKET"].copy()
    bk["ymd"] = pd.to_datetime(bk["ymd"]); bk["value"] = bk["value"].astype(float)
    file_lvl = bk.set_index("ymd")["value"]
    # both start at base 1000; compare RATIO to the common first date (scale-free)
    common_b = file_lvl.index.intersection(lvl_bq.index)
    fl_n = file_lvl.loc[common_b] / file_lvl.loc[common_b].iloc[0]
    bq_n = lvl_bq.loc[common_b] / lvl_bq.loc[common_b].iloc[0]
    lvl_relerr = (fl_n / bq_n - 1).abs().max()
    print(f"[3b] custom basket: members_match={members_match} | "
          f"file-level vs BQ-rebuild max rel err {lvl_relerr:.2e} over {len(common_b)} days")
    # (c) verify a sample of parking TX/MTM rows against the file's CUSTOM_BASKET levels (same
    # run-scale as adj_price; (b) above already proved those levels are BQ-reconstructable).
    park = tx[(tx["ticker"] == PARK) & tx["adj_price"].notna()]
    if len(park):
        psamp = park.sample(min(60, len(park)), random_state=42)
        lvl_ff = file_lvl.sort_index()
        pbad = 0
        for r in psamp.itertuples():
            sub = lvl_ff.reindex([r.ymd], method="ffill")
            ref = float(sub.iloc[0]) if len(sub) and pd.notna(sub.iloc[0]) else None
            if ref is None or abs(r.adj_price / ref - 1) > 0.005: pbad += 1
        print(f"     parking rows vs file basket levels: {len(psamp)} sampled, {pbad} mismatches")

# ---------- 4. cash-flow identity from TX vs DAILY cash refs ----------
fl = tx[~tx["reason"].astype(str).str.startswith("MTM")].copy()
fl["net"] = np.where(fl["action"] == "sell", fl["sell_amount"] - fl["fee"],
                     -(fl["buy_amount"] + fl["fee"]))
for book, col, init in [("BAL", "bal_cash_ref", INIT_BOOK), ("LAG", "lag_cash_ref", INIT_BOOK)]:
    f = fl[fl["book"] == book].groupby("ymd")["net"].sum()
    cash = daily.set_index("ymd")[col].astype(float)
    dc = cash.diff(); dc.iloc[0] = cash.iloc[0] - init
    err = (dc - f.reindex(cash.index).fillna(0)).abs().max()
    print(f"[4] {book} cash-flow identity max err: {err:,.2f} VND")

# ---------- 5. combination replay + combined NAV ----------
d = daily.set_index("ymd")
if IS_ALLOC:
    # replay using the STORED w_lag_tgt column (works for any allocator rule incl edge-conditional)
    BAND = 0.10; TC = 0.001
    rbv = d["nav_bal_ref"].astype(float).pct_change().fillna(0).values
    rlv = d["nav_lag_ref"].astype(float).pct_change().fillna(0).values
    wv = d["w_lag_tgt"].astype(float).values
    cb = (1 - wv[0]) * INIT_TOTAL; cl = wv[0] * INIT_TOTAL
    for i in range(len(d)):
        if i: cb *= 1 + rbv[i]; cl *= 1 + rlv[i]
        P = cb + cl; wt = wv[i]
        if P > 0 and abs(cl / P - wt) > BAND:
            P -= TC * abs(wt * P - cl); cl = wt * P; cb = (1 - wt) * P
    err_a = abs((cb + cl) - float(d["combined_nav"].iloc[-1]))
    print(f"[5] allocator replay (via stored w_lag_tgt) err vs combined_nav: {err_a:,.2f} VND")
else:
    # static 50/50: combined_nav must equal nav_bal_ref + nav_lag_ref every day
    recomb = d["nav_bal_ref"].astype(float) + d["nav_lag_ref"].astype(float)
    err_a = (recomb - d["combined_nav"].astype(float)).abs().max()
    print(f"[5] static-sum replay max err (nav_bal_ref+nav_lag_ref vs combined_nav): {err_a:,.2f} VND")

# ---------- 6. metrics recompute from DAILY ----------
s_nav = d["combined_nav"].astype(float)
yrs = (s_nav.index[-1] - s_nav.index[0]).days / 365.25
r = s_nav.pct_change().dropna()
cagr = (s_nav.iloc[-1] / s_nav.iloc[0]) ** (1 / yrs) - 1
sh = r.mean() / r.std() * np.sqrt(252)
mdd = (s_nav / s_nav.cummax() - 1).min()
print(f"[6] recomputed: CAGR {cagr*100:.2f}% (file {float(metric['cagr'])*100:.2f}%) | "
      f"Sharpe252 {sh:.3f} (file {float(metric['sharpe_252']):.3f}) | "
      f"MaxDD {mdd*100:.2f}% (file {float(metric['max_dd'])*100:.2f}%)")
print("\nSpot-check done.")
