# -*- coding: utf-8 -*-
"""dc_release_date_stats.py (job Taylor_20260707_042827, NHÁNH C phần 1) — RESEARCH ONLY.

Thống kê phân phối ngày nộp BCTC (Release_Date) theo quý, 2014Q1-2025Q4, để trả lời:
mốc rebalance q2m5 (ngày 5 tháng thứ 2 của quý ~ 36 ngày sau quarter-end) là kinh nghiệm —
thống kê thật nói ngày nào tích lũy 50/80/90/95% báo cáo đã nộp?

- Universe: ticker_prune (tên chất lượng/thanh khoản — đúng universe mà custom30V/DC book chọn từ đó).
- lag = Release_Date - quarter_end (ngày lịch).
- Tách Q1-Q3 vs Q4 (BCTC năm audited muộn hơn).
- Riêng cho 2 vehicle: WL 16 tên DC book + tên từng vào custom30V basket.
- Bias nộp muộn: so NP YoY (NP_P0/NP_P4-1) của báo cáo nộp sau mốc-80% vs nộp trước.
"""
import duckdb, numpy as np, pandas as pd

CACHE = "/home/trido/thanhdt/WorkingClaude/data/bq_cache"
WL_TK = ["MBB","ACB","HDB","TCB","VCB","FPT","SSI","VCI","VND","HCM","CTR","MSH","DHG","PVT","HAH","DBC"]

c = duckdb.connect(":memory:"); c.execute("SET threads=1")

prune_tk = set(c.execute(f"SELECT DISTINCT ticker FROM read_parquet('{CACHE}/ticker_prune/*.parquet')").df()["ticker"])
c30v_tk = set(c.execute(f"SELECT DISTINCT ticker FROM read_parquet('{CACHE}/custom30v_8l.parquet')").df()["ticker"])

fin = c.execute(f"""
    SELECT ticker, quarter, Release_Date, NP_P0, NP_P4
    FROM read_parquet('{CACHE}/ticker_financial.parquet')
    WHERE Release_Date IS NOT NULL AND quarter IS NOT NULL
""").df()
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
fin["qy"] = fin["quarter"].str[:4].astype(int)
fin["qn"] = fin["quarter"].str[-1].astype(int)
fin = fin[(fin["qy"] >= 2014) & (fin["qy"] <= 2025)]
qend = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
fin["q_end"] = pd.to_datetime(fin["qy"].astype(str) + "-" + fin["qn"].map(qend))
fin["lag"] = (fin["Release_Date"] - fin["q_end"]).dt.days
# vệ sinh: lag âm (nộp trước quarter-end?) hoặc quá 250 ngày = dữ liệu bẩn, loại và đếm
bad = fin[(fin["lag"] < 0) | (fin["lag"] > 250)]
print(f"records loại vì lag<0 hoặc >250 ngày: {len(bad)}/{len(fin)} ({len(bad)/len(fin)*100:.2f}%)")
fin = fin[(fin["lag"] >= 0) & (fin["lag"] <= 250)]
fin_p = fin[fin["ticker"].isin(prune_tk)]
print(f"universe: prune={len(prune_tk)} tickers; records prune={len(fin_p)}, all={len(fin)}")

PCTS = [50, 80, 90, 95]

def cum_pct(df, label):
    rows = []
    for tag, sub in [("Q1-Q3", df[df["qn"] <= 3]), ("Q4", df[df["qn"] == 4])]:
        if not len(sub): continue
        q = {p: np.percentile(sub["lag"], p) for p in PCTS}
        rows.append((tag, len(sub), q))
    print(f"\n--- {label} ---")
    print(f"{'quý':<8}{'n':>7}" + "".join(f"{'p'+str(p):>8}" for p in PCTS))
    for tag, n, q in rows:
        print(f"{tag:<8}{n:>7}" + "".join(f"{q[p]:>7.0f}d" for p in PCTS))
    return rows

cum_pct(fin_p, "ticker_prune universe (2014-2025)")
cum_pct(fin_p[fin_p["ticker"].isin(WL_TK)], "DC watchlist 16 tên")
cum_pct(fin_p[fin_p["ticker"].isin(c30v_tk)], f"custom30V basket historical members ({len(c30v_tk)} tên)")

# ổn định theo năm (prune, Q1-Q3): p80 từng năm
print("\n--- Ổn định theo năm — p50/p80/p90 lag (prune) ---")
print(f"{'năm':<6}{'Q13_n':>7}{'p50':>6}{'p80':>6}{'p90':>6}   {'Q4_n':>6}{'p50':>6}{'p80':>6}{'p90':>6}")
for y in range(2014, 2026):
    a = fin_p[(fin_p["qy"] == y) & (fin_p["qn"] <= 3)]["lag"]
    b = fin_p[(fin_p["qy"] == y) & (fin_p["qn"] == 4)]["lag"]
    fa = "".join(f"{np.percentile(a,p):>6.0f}" for p in (50,80,90)) if len(a) else " " * 18
    fb = "".join(f"{np.percentile(b,p):>6.0f}" for p in (50,80,90)) if len(b) else " " * 18
    print(f"{y:<6}{len(a):>7}{fa}   {len(b):>6}{fb}")

# mốc hiện tại q2m5 = ngày 05 tháng+1 sau quarter-end -> lag ngày lịch
# Q1 end 03-31 -> 05-05 = 35d; Q2 06-30 -> 08-05 = 36d; Q3 09-30 -> 11-05 = 36d; Q4 12-31 -> 02-05 = 36d
print("\nq2m5 tương đương lag ~35-36 ngày lịch sau quarter-end.")
for tag, sub in [("Q1-Q3", fin_p[fin_p["qn"] <= 3]), ("Q4", fin_p[fin_p["qn"] == 4])]:
    for L in (20, 25, 30, 33, 36, 40, 45, 90):
        pct = (sub["lag"] <= L).mean() * 100
        print(f"  {tag}: đến lag {L:>3}d đã nộp {pct:5.1f}%")
    print()

# --- bias nộp muộn: NP YoY của báo cáo nộp muộn vs sớm (prune, Q1-Q3) ---
print("--- Bias nộp muộn (prune, Q1-Q3): NP YoY theo nhóm lag ---")
s = fin_p[(fin_p["qn"] <= 3) & fin_p["NP_P0"].notna() & fin_p["NP_P4"].notna()].copy()
s = s[s["NP_P4"].abs() > 1e-9]
s["np_yoy"] = np.where(s["NP_P4"] > 0, s["NP_P0"] / s["NP_P4"] - 1, np.nan)
s["np_declined"] = s["NP_P0"] < s["NP_P4"]
s["np_loss"] = s["NP_P0"] < 0
p80 = np.percentile(fin_p[fin_p["qn"] <= 3]["lag"], 80)
for tag, sub in [(f"nộp sớm (lag<=p80={p80:.0f}d)", s[s["lag"] <= p80]),
                 (f"nộp muộn (lag>p80)", s[s["lag"] > p80])]:
    yy = sub["np_yoy"].replace([np.inf, -np.inf], np.nan).dropna()
    yy = yy.clip(-2, 2)
    print(f"  {tag:<28} n={len(sub):>6}  NPyoy median {yy.median()*100:+6.1f}%  "
          f"%NP giảm YoY {sub['np_declined'].mean()*100:5.1f}%  %lỗ {sub['np_loss'].mean()*100:5.1f}%")

# cho riêng WL + c30v members: nộp muộn có tồn tại không
print("\n--- Tên vehicle nộp sau mốc lag 33d (Q1-Q3, 2020-2025) — đếm theo tên ---")
recent = fin_p[(fin_p["qn"] <= 3) & (fin_p["qy"] >= 2020)]
for label, tks in [("DC WL16", set(WL_TK)), ("c30v members", c30v_tk)]:
    sub = recent[recent["ticker"].isin(tks)]
    late = sub[sub["lag"] > 33].groupby("ticker").size().sort_values(ascending=False)
    tot = sub.groupby("ticker").size()
    frac = (len(sub[sub['lag'] > 33]) / len(sub) * 100) if len(sub) else np.nan
    print(f"  {label}: {len(sub)} báo cáo, {frac:.1f}% nộp sau 33d; top muộn: "
          + ", ".join(f"{t}({n}/{tot[t]})" for t, n in late.head(8).items()))
