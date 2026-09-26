#!/usr/bin/env python3
"""H2 (a) — thay tang T2/T3 cua cpi_vn.py bang CPI that FiinPro, dem so thang DOI NHAN regime
trong macro_confidence_regime.py.

GIOI HAN DA DO, KHONG SUY DIEN: macro_confidence_regime.py can /tmp/vn_turnover.csv va
/tmp/gold_world.csv — CA HAI DA KHONG CON TON TAI tren may nay (kiem 2026-09-26) ⇒ hai co
REG_A / REG_A_strict (phu thuoc vang) KHONG tai lap duoc. Bao cao chi 2 co dung duoc:
  REG_C = stress_leg            = infl_hot | dep_rising            (CPI vao TRUC TIEP)
  REG_B = usd_up126 & stress_leg
`infl_hot` = (cpi_yoy_chg3 > 0) | (cpi_yoy > 4.0)   <- dong duy nhat CPI cham vao
"""
import sys, csv
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd
from pathlib import Path
from cpi_vn import cpi_monthly_df
from deposit_rate_vn import merge_deposit
D = Path(__file__).resolve().parent; ROOT = Path("/home/trido/thanhdt/WorkingClaude")

proxy = cpi_monthly_df(end="2026-08-01")[["time", "cpi_yoy", "is_real_nso", "is_backfill_2007_2010"]]
fp = pd.read_csv(ROOT / "mike/data/fiinprox_cpi_monthly_20260914.csv")
fp["time"] = pd.to_datetime(fp["month"] + "-01") if fp["month"].astype(str).str.len().max() == 7 \
             else pd.to_datetime(fp["month"])
fp = fp[["time", "cpi_yoy_pct"]].rename(columns={"cpi_yoy_pct": "cpi_real"})
m = proxy.merge(fp, on="time", how="outer").sort_values("time").reset_index(drop=True)
# Tang moi: T1 NSO that GIU NGUYEN; moi cho khac lay FiinPro neu co, khong thi giu proxy
m["cpi_new"] = np.where(m["is_real_nso"].fillna(False), m["cpi_yoy"],
                        m["cpi_real"].fillna(m["cpi_yoy"]))
m = m[m["time"] <= "2026-08-01"]
n_sw = int(((~m["is_real_nso"].fillna(False)) & m["cpi_real"].notna()).sum())
print(f"[nguon] {len(m)} thang 2007-01..2026-08; thay bang FiinPro {n_sw} thang; "
      f"giu T1 NSO that {int(m['is_real_nso'].fillna(False).sum())} thang")
both = m.dropna(subset=["cpi_yoy", "cpi_real"])
print(f"[lech ] n={len(both)} MAE={ (both['cpi_yoy']-both['cpi_real']).abs().mean():.3f}pp "
      f"max={ (both['cpi_yoy']-both['cpi_real']).abs().max():.2f}pp")

def flags(col):
    s = m.set_index("time")[col]
    return pd.DataFrame({"cpi": s, "chg3": s.diff(3)}).assign(
        infl_hot=lambda d: (d["chg3"] > 0) | (d["cpi"] > 4.0))

fo, fn = flags("cpi_yoy"), flags("cpi_new")
diff_hot = fo.index[(fo["infl_hot"].values != fn["infl_hot"].values)]
print(f"\n[infl_hot] doi {len(diff_hot)}/{len(fo)} thang ({100.0*len(diff_hot)/len(fo):.1f}%)")

# USD + deposit de dung REG_B / REG_C tren luoi NGAY roi quy ve thang
mf = pd.read_csv(ROOT / "data/macro_features.csv", parse_dates=["time"])[["time", "USDVND"]]
mf = merge_deposit(mf.sort_values("time"))
mf["usd_up126"] = (mf["USDVND"] / mf["USDVND"].shift(6*21) - 1.0) > 0
mf["dep_rising"] = (mf["deposit_rate"] - mf["deposit_rate"].shift(6*21)) > 0
for tag, f in (("old", fo), ("new", fn)):
    c = f.reset_index().rename(columns={"time": "ctime"})[["ctime", "infl_hot"]]
    mf = pd.merge_asof(mf.sort_values("time"), c.sort_values("ctime"),
                       left_on="time", right_on="ctime", direction="backward")
    mf = mf.rename(columns={"infl_hot": f"infl_hot_{tag}", "ctime": f"ct_{tag}"})
for tag in ("old", "new"):
    mf[f"REG_C_{tag}"] = mf[f"infl_hot_{tag}"] | mf["dep_rising"]
    mf[f"REG_B_{tag}"] = mf["usd_up126"] & mf[f"REG_C_{tag}"]
mf["ym"] = mf["time"].dt.to_period("M")
rows = []
for reg in ("REG_B", "REG_C"):
    g = mf.groupby("ym").agg(o=(f"{reg}_old", "mean"), n=(f"{reg}_new", "mean"))
    # "doi nhan thang" = nhan da so trong thang doi
    o, n = (g["o"] >= 0.5), (g["n"] >= 0.5)
    ch = g.index[o.values != n.values]
    print(f"[{reg}] doi nhan {len(ch)}/{len(g)} thang ({100.0*len(ch)/len(g):.1f}%) "
          f"| khoang {g.index.min()}..{g.index.max()}")
    for ym in ch:
        rows.append([reg, str(ym), bool(o.loc[ym]), bool(n.loc[ym]),
                     round(float(m.loc[m['time'].dt.to_period('M') == ym, 'cpi_yoy'].mean()), 2),
                     round(float(m.loc[m['time'].dt.to_period('M') == ym, 'cpi_new'].mean()), 2)])
    if len(ch):
        print("   thang doi: " + ", ".join(str(x) for x in ch))
with open(D / "h2_regime_flips.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["regime", "month", "label_old", "label_new", "cpi_old", "cpi_new"])
    w.writerows(rows)
# infl_hot theo nam de doi chieu episode lam phat
fo2 = fo.assign(y=fo.index.year); fn2 = fn.assign(y=fn.index.year)
d = (fo2["infl_hot"] != fn2["infl_hot"]).groupby(fo2["y"]).sum()
print("\n[infl_hot doi theo nam] " + " ".join(f"{y}:{int(v)}" for y, v in d.items() if v))
m[["time", "cpi_yoy", "cpi_real", "cpi_new"]].to_csv(D / "h2_cpi_series.csv", index=False)
print(f"-> {D/'h2_regime_flips.csv'} ; {D/'h2_cpi_series.csv'}")
