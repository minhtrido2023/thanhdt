"""Viec 2 — doi chieu navsize:0,25 (12,5 ty tren so 50 ty) voi tran %ADV THAT.

Tai lap DUNG cong thuc production `golive_recommend_v23.capit_adv_caps`:
    cap_vnd_i = ADV_X * ADV20_i * ADV_D,  ADV_X=0.10, ADV_D=2.0
    ADV20_i   = MEDIAN(Price*Volume) tren 20 phien NGAY TRUOC ngay fire (khong tinh ngay fire),
                cua so 90 ngay lich, nguon ticker_prune (== CAPIT_POOL_SOURCE='prune' live).
Ro CAPIT moi su kien lay tu chinh audit CSV cua leg navsize:0.25 (play_type CAPITB_E*/CAPITL_E*).
"""
import glob, re
import numpy as np
import pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
CACHE = f"{W}/data/bq_cache_asof20260729_postrestate/ticker_prune"
CSV = glob.glob(f"{W}/data/v23_golive_audit_2014_now_szbnavsize025_*_exp_capsz_navsize25_univpit.csv")[0]
ADV_X, ADV_D = 0.10, 2.0
NAV_TOTAL = 50e9

df = pd.read_csv(CSV, low_memory=False)
ev = df[df.record_type == "EVENT_CAPIT"][["ymd", "value"]].copy()
ev["ymd"] = pd.to_datetime(ev.ymd)
ev["size"] = pd.to_numeric(ev.value)
ev = ev.reset_index(drop=True)

tx = df[(df.record_type == "TX") & df.play_type.astype(str).str.startswith("CAPIT")].copy()
tx["ymd"] = pd.to_datetime(tx.ymd)
tx["eid"] = tx.play_type.str.extract(r"_E(\d+)$")[0].astype(int)
tx["buy_amount"] = pd.to_numeric(tx.buy_amount, errors="coerce").fillna(0.0)
ent = tx[tx.reason.astype(str).str.startswith("ENTRY")]

px = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Price", "Close", "Volume"])
                for f in sorted(glob.glob(f"{CACHE}/*.parquet"))], ignore_index=True)
px["time"] = pd.to_datetime(px.time)
px["turn"] = px.Price.fillna(px.Close) * px.Volume
px = px.dropna(subset=["turn"]).sort_values("time")

rows = []
for eid in sorted(ent.eid.unique()):
    g = ent[ent.eid == eid]
    d0 = ev.loc[eid, "ymd"]
    size = ev.loc[eid, "size"]
    names = sorted(g.ticker.unique())
    lo = d0 - pd.Timedelta(days=90)
    sub = px[(px.ticker.isin(names)) & (px.time < d0) & (px.time >= lo)]
    advs, miss = {}, []
    for t in names:
        s = sub[sub.ticker == t].sort_values("time").tail(20)["turn"]
        if len(s) == 0:
            miss.append(t)
        else:
            advs[t] = float(s.median())
    caps = {t: ADV_X * v * ADV_D for t, v in advs.items()}
    cap_tot = sum(caps.values())
    tgt = size * 0.25 * NAV_TOTAL          # navsize:0.25 target (VND, ca fleet 50 ty)
    per_name_tgt = tgt / len(names) if names else 0.0   # equal-weight xap xi
    binding = [t for t in names if t in caps and caps[t] < per_name_tgt]
    # tran THUC TE kha thi cho su kien nay, quy ve he so navsize (cap_tot = k*size*NAV)
    k_feasible = cap_tot / (size * NAV_TOTAL) if size > 0 else np.nan
    rows.append(dict(E=eid, ngay=d0.date(), size=size, n=len(names),
                     deployed_actual_bn=g.buy_amount.sum() / 1e9,
                     tgt_bn=tgt / 1e9, cap_tot_bn=cap_tot / 1e9,
                     util=tgt / cap_tot if cap_tot > 0 else np.nan,
                     n_binding=len(binding), binding=",".join(binding),
                     k_feasible=k_feasible, missing=",".join(miss),
                     names=",".join(names)))

R = pd.DataFrame(rows)
pd.set_option("display.width", 240, "display.max_columns", 50)
print(R[["E", "ngay", "size", "n", "tgt_bn", "cap_tot_bn", "util", "n_binding", "k_feasible", "missing"]]
      .to_string(index=False, float_format=lambda x: f"{x:.3f}"))

print("\n--- tong hop ---")
print(f"so su kien co ro: {len(R)}")
print(f"util (target / tong cap ADV toan ro): median {R.util.median():.3f}  "
      f"min {R.util.min():.3f}  max {R.util.max():.3f}")
print(f"so su kien util > 1.0 (VUOT suc hap thu ro): {(R.util > 1).sum()}/{len(R)}")
print(f"so su kien co it nhat 1 ten binding: {(R.n_binding > 0).sum()}/{len(R)}")
print(f"k_feasible (he so navsize toi da khong cham cap TONG): "
      f"min {R.k_feasible.min():.3f}  p10 {R.k_feasible.quantile(0.10):.3f}  "
      f"median {R.k_feasible.median():.3f}")
# tran per-name (chat hon tran tong vi ro equal-weight)
kn = []
for _, r in R.iterrows():
    caps_line = r["names"].split(",")
    kn.append(r["k_feasible"])
print("\nSu kien chat nhat (k_feasible thap nhat):")
print(R.nsmallest(4, "k_feasible")[["E", "ngay", "size", "n", "tgt_bn", "cap_tot_bn", "util",
                                    "k_feasible", "names"]].to_string(index=False,
                                                                      float_format=lambda x: f"{x:.3f}"))
R.to_csv(f"{W}/mike/agents/Taylor/research/capit_adv_check_20260731.csv", index=False)
print(f"\nwrote research/capit_adv_check_20260731.csv")
