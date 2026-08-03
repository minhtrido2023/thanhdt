# -*- coding: utf-8 -*-
"""bridge_sim_vs_verified.py — NOI T4 (fill THAT) voi mo phong: so LAG cua sim chay o %ADV nao?

Job Taylor_20260803_045138. T4 xac nhan mo hinh fill AN TOAN toi 3,86% ADV/phien (su kien mua that
lon nhat tung khop tron). Cau hoi con lai: sim VAN HANH o dau tren truc do?

Do thang tu so lenh: gop ENTRY_FILL cua so LAG theo (ticker, phien), chia cho ADV cung dinh nghia
engine (Volume_3M_P50 * Close, tu CHINH snapshot bq_cache_asof20260729_postrestate ma cac chan da
dung — khong dung BQ live, tranh lech vintage).
"""
import glob
import sys
import duckdb
import pandas as pd

WD = "/home/trido/thanhdt/WorkingClaude"
BASE = f"{WD}/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap"
CACHE = f"{WD}/data/bq_cache_asof20260729_postrestate/ticker/*.parquet"
T4_VERIFIED = 0.0386          # nguong T4 (NCT 07-21, khop 100%)

adv = duckdb.connect().execute(
    f"SELECT ticker, CAST(time AS DATE) d, Volume_3M_P50*Close AS adv FROM read_parquet('{CACHE}') "
    "WHERE Volume_3M_P50 IS NOT NULL AND Close IS NOT NULL").df()
adv["d"] = pd.to_datetime(adv["d"])
print(f"ADV lookup (cung vintage voi cac chan): {len(adv):,} dong")

LEGS = [("L0@50B (= chan pin R3)", f"{BASE}_exp_cap_p020_L0_univpit.csv"),
        ("L1@50B (LIQ_ZERO_BLOCK)", f"{BASE}_liqzblag_exp_L1_liqzb_univpit.csv"),
        ("L0@5B  (NAV nho nhat)", f"{BASE}_exp_nav005_L0_univpit_nav5B.csv")]

for tag, path in LEGS:
    fs = glob.glob(path)
    if not fs:
        print(f"[{tag}] MISSING {path}"); continue
    d = pd.read_csv(fs[0], low_memory=False)
    tx = d[(d.record_type == "TX") & (d.book == "LAG") & (d.reason == "ENTRY_FILL")].copy()
    tx["d"] = pd.to_datetime(tx["ymd"])
    tx["buy_amount"] = pd.to_numeric(tx["buy_amount"], errors="coerce")
    g = tx.groupby(["ticker", "d"], as_index=False)["buy_amount"].sum()
    m = g.merge(adv, on=["ticker", "d"], how="left")
    miss = len(g) - len(m[m.adv.notna() & (m.adv > 0)])
    m = m[m.adv.notna() & (m.adv > 0)].copy()
    m["pct_adv"] = m.buy_amount / m.adv
    q = m.pct_adv.quantile([.25, .5, .75, .9, .99])
    w = m.buy_amount.sum()
    print(f"\n[{tag}] n phien-fill = {len(m):,} (bo qua {miss} thieu ADV)")
    print(f"  %ADV/phien cua MOT vi the: p25 {q[.25]*100:.2f}%  TRUNG VI {q[.5]*100:.2f}%  "
          f"p75 {q[.75]*100:.2f}%  p90 {q[.9]*100:.2f}%  p99 {q[.99]*100:.2f}%")
    print(f"  ty le phien-fill CHAM TRAN (>=19,5% ADV): {(m.pct_adv >= 0.195).mean()*100:.1f}%")
    print(f"  ty le phien-fill VUOT nguong T4 da xac nhan ({T4_VERIFIED*100:.2f}% ADV): "
          f"{(m.pct_adv > T4_VERIFIED).mean()*100:.1f}%")
    print(f"  TRONG SO THEO TIEN: % von mua o size > nguong T4 = "
          f"{m.loc[m.pct_adv > T4_VERIFIED, 'buy_amount'].sum()/w*100:.1f}%")
