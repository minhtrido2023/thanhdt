# -*- coding: utf-8 -*-
"""basket_scheme_concentration.py — for the CURRENT basket, show how each weight scheme
de-concentrates: ICB-8 (financials+RE), banks, single-name, HHI. Cheap (one mcap snapshot)."""
import pandas as pd, numpy as np, os, glob, sys
sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude")
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq
from custom_basket import _cap_names, _cap_sector

cands = [c for c in glob.glob("data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg*.csv")
         if "custompitgq" not in c and "_wt" not in c]
df = pd.read_csv(max(cands, key=os.path.getmtime), low_memory=False)
m = df[df["record_type"] == "CUSTOM_MEMBERS"].copy(); m["ymd"] = pd.to_datetime(m["ymd"])
tickers = sorted(m[m["ymd"] == m["ymd"].max()]["ticker"].unique())
inlist = ",".join(f"'{t}'" for t in tickers)
q = f"""
WITH px AS (SELECT t.ticker AS ticker, t.Close AS Close, t.ICB_Code AS ICB_Code,
       ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) rn
     FROM tav2_bq.ticker AS t WHERE t.ticker IN ({inlist}) AND t.Close IS NOT NULL),
sh AS (SELECT f.ticker AS ticker, f.OShares AS OShares,
       ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) rn
     FROM tav2_bq.ticker_financial AS f WHERE f.ticker IN ({inlist}) AND f.OShares IS NOT NULL)
SELECT p.ticker AS ticker, p.ICB_Code AS ICB_Code, p.Close*s.OShares AS mcap
FROM px AS p JOIN sh AS s ON p.ticker=s.ticker WHERE p.rn=1 AND s.rn=1"""
d = bq(q)
d["mcap"] = d["mcap"].astype(float)
d["icb"] = d["ICB_Code"].astype(int)
d["sec1"] = d["icb"] // 1000
d["bank"] = (d["icb"] >= 8350) & (d["icb"] < 8360)
tk = list(d["ticker"]); mc = d["mcap"].values; s1 = d["sec1"].values; bk = d["bank"].values

def report(w, label):
    w = np.array(w, dtype=float); w = w / w.sum()
    icb8 = w[s1 == 8].sum() * 100
    banks = w[bk].sum() * 100
    top1 = w.max() * 100
    top5 = np.sort(w)[::-1][:5].sum() * 100
    hhi = (w ** 2).sum()
    eff = 1.0 / hhi
    print(f"  {label:<24} ICB8 {icb8:5.1f}%  banks {banks:5.1f}%  top1 {top1:5.1f}%  "
          f"top5 {top5:5.1f}%  eff_names {eff:4.1f}")

base = mc / mc.sum()
print(f"rổ hiện hành — {len(tk)} mã\n")
print("scheme                    nhóm tài chính+BĐS    NH      mã lớn nhất   top5      số mã hiệu dụng")
report(base, "A capwt (HIỆN TẠI)")
report(np.ones(len(tk)), "D equal-weight")
report(_cap_names(base, 0.10), "B namecap 10%")
report(_cap_names(_cap_sector(base, s1, 8, 0.50), 0.10), "C sectorcap50+namecap10")
