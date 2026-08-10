# -*- coding: utf-8 -*-
"""Cau 3: san 2 ty BOP RO UNG VIEN bao nhieu? Do tren universe LAG-eligible HOM NAY.
Universe quyet dinh cua LAG = universe_pit (production tu 2026-07-29). ADV = cong thuc
production Volume_3M_P50 x COALESCE(Price, Close) (due_diligence.adv_vnd).
"""
import glob
import numpy as np
import pandas as pd

up = pd.read_parquet(sorted(glob.glob("data/bq_cache/universe_pit_q/*.parquet"))[-1])
up.columns = [c.lower() for c in up.columns]
up["time"] = pd.to_datetime(up["time"])
asof = up["time"].max()
uni = set(up.loc[(up["time"] == asof) & (up["in_universe"]), "ticker"])
print(f"universe_pit as-of {asof:%Y-%m-%d}: {len(uni)} ma")

f = sorted(glob.glob("data/bq_cache/ticker/*.parquet"))[-1]
t = pd.read_parquet(f, columns=["ticker", "time", "Volume_3M_P50", "Price", "Close"])
t["time"] = pd.to_datetime(t["time"])
t = t.sort_values("time").groupby("ticker", as_index=False).last()
print(f"ticker chunk {f.split('/')[-1]}, dong moi nhat {t.time.max():%Y-%m-%d}")

t["px"] = t["Price"].fillna(t["Close"])
t["adv"] = t["Volume_3M_P50"] * t["px"]
u = t[t.ticker.isin(uni)].copy()
u = u[u.adv.notna()]
print(f"do duoc ADV: {len(u)}/{len(uni)} ma\n")

rows = []
for thr, lab in [(1e8, "0,1 ty (gan chet)"), (5e8, "0,5 ty"), (1e9, "1 ty"),
                 (2e9, "2 ty (san dang hoi)"), (5e9, "5 ty"), (17e9, "17 ty (nang luc fill that)")]:
    m = u.adv < thr
    rows.append(dict(nguong=lab, so_ma_bi_loai=int(m.sum()),
                     pct_universe=f"{m.mean()*100:.1f}%",
                     con_lai=int((~m).sum())))
print(pd.DataFrame(rows).to_string(index=False))
print(f"\nADV phan vi universe (ty/phien): "
      f"p10 {u.adv.quantile(.10)/1e9:.2f} | p25 {u.adv.quantile(.25)/1e9:.2f} | "
      f"trung vi {u.adv.median()/1e9:.2f} | p75 {u.adv.quantile(.75)/1e9:.2f} | p90 {u.adv.quantile(.90)/1e9:.2f}")
print("\nVD ma bi san 2 ty loai (ADV cao nhat trong nhom bi loai):")
print(u[u.adv < 2e9].nlargest(12, "adv")[["ticker", "adv"]].assign(
      adv_ty=lambda d: (d.adv/1e9).round(2)).drop(columns="adv").to_string(index=False))
for tk in ("SCL",):
    r = u[u.ticker == tk]
    if len(r):
        print(f"\n{tk}: ADV3T = {float(r.adv.iloc[0])/1e9:.2f} ty/phien "
              f"({'BI LOAI' if float(r.adv.iloc[0]) < 2e9 else 'qua'} boi san 2 ty)")
