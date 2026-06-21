# -*- coding: utf-8 -*-
"""basket_concentration.py — measure the CAP-WEIGHT concentration of the current 8L custom30
parking basket: by ICB sector and by single name. Answers "are we over-concentrated in one group?"
Source members = latest rebal in the custompitg audit CSV; mcap/ICB from BQ (live)."""
import pandas as pd, os, glob, re, sys
sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude")
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq

cands = [c for c in glob.glob("data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg*.csv")
         if "custompitgq" not in c]
df = pd.read_csv(max(cands, key=os.path.getmtime), low_memory=False)
m = df[df["record_type"] == "CUSTOM_MEMBERS"].copy()
m["ymd"] = pd.to_datetime(m["ymd"])
last = m["ymd"].max()
tickers = sorted(m[m["ymd"] == last]["ticker"].unique())
print(f"rổ rebal {last.date()} — {len(tickers)} mã\n")
inlist = ",".join(f"'{t}'" for t in tickers)

q = f"""
WITH px AS (SELECT t.ticker AS ticker, t.Close AS Close, t.ICB_Code AS ICB_Code,
       ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) rn
     FROM tav2_bq.ticker AS t WHERE t.ticker IN ({inlist}) AND t.Close IS NOT NULL),
sh AS (SELECT f.ticker AS ticker, f.OShares AS OShares,
       ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) rn
     FROM tav2_bq.ticker_financial AS f WHERE f.ticker IN ({inlist}) AND f.OShares IS NOT NULL)
SELECT p.ticker AS ticker, p.Close AS Close, p.ICB_Code AS ICB_Code, s.OShares AS OShares,
       p.Close*s.OShares AS mcap
FROM px AS p JOIN sh AS s ON p.ticker=s.ticker WHERE p.rn=1 AND s.rn=1"""
d = bq(q)
d["mcap"] = d["mcap"].astype(float)
d["w"] = d["mcap"] / d["mcap"].sum() * 100
d["icb4"] = d["ICB_Code"].astype(int)
d["sec1"] = (d["icb4"] // 1000)

# VN ICB subsector labels (common ones in this universe)
def lab(icb):
    if 8350 <= icb < 8360: return "Ngân hàng"
    if 8770 <= icb < 8790: return "Chứng khoán/DV tài chính"
    if 8630 <= icb < 8640: return "Bất động sản"
    if 8500 <= icb < 8600: return "Bảo hiểm"
    if icb // 1000 == 8:    return "Tài chính khác"
    if icb // 1000 == 0:    return "Dầu khí"
    if icb // 1000 == 1:    return "Vật liệu cơ bản"
    if icb // 1000 == 2:    return "Công nghiệp"
    if icb // 1000 == 3:    return "Hàng tiêu dùng"
    if icb // 1000 == 5:    return "Dịch vụ tiêu dùng"
    if icb // 1000 == 7:    return "Tiện ích"
    if icb // 1000 == 9:    return "Công nghệ"
    return f"ICB{icb}"
d["nhom"] = d["icb4"].apply(lab)

print("=== TỪNG MÃ (cap-weight %) ===")
for _, r in d.sort_values("w", ascending=False).iterrows():
    print(f"  {r['ticker']:<5} {r['w']:5.1f}%   {r['nhom']}")

print("\n=== THEO NHÓM (cap-weight) ===")
g = d.groupby("nhom").agg(n=("ticker","size"), w=("w","sum")).sort_values("w", ascending=False)
for nm, r in g.iterrows():
    print(f"  {nm:<26} {int(r['n']):2d} mã   {r['w']:5.1f}%")

fin = d[d["sec1"] == 8]
print("\n=== TẬP TRUNG ===")
print(f"  Tài chính+BĐS (ICB-8) :  {len(fin)} mã  =  {fin['w'].sum():.1f}% vốn hóa rổ")
ds = d.sort_values("w", ascending=False)
print(f"  Top-3 mã              :  {', '.join(ds['ticker'].head(3))}  =  {ds['w'].head(3).sum():.1f}%")
print(f"  Top-5 mã              :  {ds['w'].head(5).sum():.1f}%")
print(f"  Top-10 mã             :  {ds['w'].head(10).sum():.1f}%")
hhi = (d['w']**2).sum()
print(f"  HHI (Herfindahl)      :  {hhi:.0f}  (equal-weight 30 mã = {10000/30:.0f}; càng cao càng tập trung)")
print(f"  Số mã hiệu dụng (1/ΣwΒ²): {10000/hhi:.1f}  / 30")
