# -*- coding: utf-8 -*-
"""Phan ra vi the LAG: nhom BI GATE 2 ty CHAN vs nhom GIU LAI (job Taylor_20260810_073541).
Nguon: control CSV chan LAG_ADV_MIN_VND=0 (= pin R3) cua job Taylor_20260804_080547
       + dropped_gate2000m.json. Chi doc; khong ghi de gi canonical.
Khoa noi: holding_id mang NGAY VAO SO = phien KE TIEP ngay tin hieu (fill T+1 Open).
          -> map moi sd trong dropped list sang phien ke tiep theo LICH GIAO DICH lay tu
             chinh cot ymd cua audit CSV, roi join CHINH XAC (ticker, ngay vao so).
"""
import json
import numpy as np
import pandas as pd

CSV = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_ctrl0804_univpit.csv"
DROP = "mike/agents/Taylor/exp_lag_advgate_20260804/dropped_gate2000m.json"

df = pd.read_csv(CSV, low_memory=False)
df["ymd"] = pd.to_datetime(df["ymd"], errors="coerce")
cal = np.array(sorted(df["ymd"].dropna().unique()))          # lich phien tu chinh audit

tx = df[(df.record_type == "TX") & (df.book == "LAG") & (df.play_type != "ETF_PARK")].copy()
for c in ("buy_amount", "sell_amount", "fee"):
    tx[c] = pd.to_numeric(tx[c], errors="coerce").fillna(0.0)

tx["pos_key"] = tx["holding_id"].astype(str).str.replace(r"_[^_]+$", "", regex=True)  # gop mieng le _? (1 ca VCR_20200427)
g = tx.groupby("pos_key")
pos = pd.DataFrame({
    "ticker": g["ticker"].first(), "play": g["play_type"].first(),
    "d0": g["ymd"].min(), "d1": g["ymd"].max(),
    "buy": g["buy_amount"].sum(), "sell": g["sell_amount"].sum(), "fee": g["fee"].sum(),
    "abandoned": g["reason"].apply(lambda s: (s == "ABANDONED_REFUND").any()),
}).reset_index()
pos["entry_d"] = pd.to_datetime(pos["pos_key"].str.extract(r"_(\d{8})$")[0], format="%Y%m%d")

drop = pd.DataFrame(json.load(open(DROP)))
drop["sd"] = pd.to_datetime(drop["sd"])
idx = np.searchsorted(cal, drop["sd"].values, side="right")   # phien ke tiep sau sd
idx = np.clip(idx, 0, len(cal) - 1)
drop["entry_d"] = pd.to_datetime(cal[idx])
drop["k"] = drop["ticker"] + "|" + drop["entry_d"].dt.strftime("%Y%m%d")

pos["k"] = pos["ticker"] + "|" + pos["entry_d"].dt.strftime("%Y%m%d")
pos["blocked"] = pos["k"].isin(set(drop["k"]))
pos = pos.merge(drop.groupby("k", as_index=False).agg(adv_vnd=("adv_vnd", "min"),
                                                      sd=("sd", "min"),
                                                      surprise=("surprise", "max")),
                on="k", how="left")

print(f"vi the LAG (khong ETF_PARK): {len(pos)} | blocked {int(pos.blocked.sum())} | kept {int((~pos.blocked).sum())}")
print(f"ung vien bi loai: {len(drop)} su kien / {drop.ticker.nunique()} ma; khop duoc vao vi the: "
      f"{drop['k'].isin(set(pos['k'])).sum()} su kien")

def blk(d, name):
    n = len(d)
    cap, pnl = d["buy"].sum(), d["sell"].sum() - d["buy"].sum() - d["fee"].sum()
    done = d[~d.abandoned]
    r = pd.to_numeric((done["sell"] - done["buy"] - done["fee"]) / done["buy"].replace(0, np.nan),
                      errors="coerce").dropna()
    print(f"\n[{name}] n={n}  bo_do={int(d.abandoned.sum())} ({d.abandoned.mean()*100:.1f}%)")
    print(f"  von trien khai {cap/1e9:,.1f}B | P&L {pnl/1e9:+,.2f}B | LN/chu ky von {pnl/cap*100:+.3f}%")
    if len(r):
        print(f"  deal hoan tat n={len(r)}: TB {r.mean()*100:+.2f}% | trung vi {r.median()*100:+.2f}% | "
              f"winrate {(r>0).mean()*100:.1f}% | p10 {r.quantile(.10)*100:+.1f}% | p90 {r.quantile(.90)*100:+.1f}% | "
              f"%lo>20% {(r<-0.20).mean()*100:.1f}%")
    return r

r_all = blk(pos, "TOAN SO LAG (nen)")
r_b = blk(pos[pos.blocked], "BI GATE 2 TY CHAN")
r_k = blk(pos[~pos.blocked], "GIU LAI")

# bootstrap CI cho chenh lech return/deal (blocked - kept)
rng = np.random.default_rng(20260810)
b, k = r_b.values, r_k.values
d = np.array([rng.choice(b, len(b), True).mean() - rng.choice(k, len(k), True).mean() for _ in range(10000)])
print(f"\nCI95 bootstrap (return/deal blocked - kept): {np.percentile(d,2.5)*100:+.2f}pp .. "
      f"{np.percentile(d,97.5)*100:+.2f}pp | diem {(b.mean()-k.mean())*100:+.2f}pp")

pos.to_csv("mike/agents/Taylor/exp_advgate_quality_20260810/pos_lag_blocked_flag.csv", index=False)
print("-> pos_lag_blocked_flag.csv")
