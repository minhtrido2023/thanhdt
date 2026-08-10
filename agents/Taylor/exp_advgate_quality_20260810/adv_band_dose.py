# -*- coding: utf-8 -*-
"""Thang lieu theo BANG ADV — cau hoi quyet dinh that.
Live DA chan ADV<=0/stale (lag_filter_illiquid). Nen nhom "bi gate 2 ty chan" trong chan control
bi duoi ADV~0 chi phoi. Bang RIENG can doc = 1e8 < ADV < 2e9 (mong nhung con song) — dung vung
SCL (1,30 ty) nam.
"""
import json
import numpy as np
import pandas as pd

pos = pd.read_csv("mike/agents/Taylor/exp_advgate_quality_20260810/pos_lag_blocked_flag.csv")
pos["abandoned"] = pos["abandoned"].astype(bool)

# ADV cho vi the KHONG bi chan: lay tu chinh bang ung vien day du (candidates_ctrl) neu co,
# nguoc lai chi doc duoc ADV cua nhom bi chan -> nhom giu lai = ">= 2 ty" theo dinh nghia gate.
BANDS = [(0, 1e8, "A. ADV <= 0,1 ty (CHET - live DA chan)"),
         (1e8, 5e8, "B. 0,1 - 0,5 ty"),
         (5e8, 1e9, "C. 0,5 - 1 ty"),
         (1e9, 2e9, "D. 1 - 2 ty  <- SCL 1,30 ty nam o day"),
         (2e9, np.inf, "E. >= 2 ty (khong bi gate)")]

def stat(d):
    if len(d) == 0:
        return None
    cap = d["buy"].sum()
    pnl = d["sell"].sum() - d["buy"].sum() - d["fee"].sum()
    done = d[~d.abandoned]
    r = pd.to_numeric((done["sell"] - done["buy"] - done["fee"]) / done["buy"].replace(0, np.nan),
                      errors="coerce").dropna()
    return dict(n=len(d), bo_do=f"{d.abandoned.mean()*100:.1f}%", von_B=round(cap/1e9, 1),
                pnl_B=round(pnl/1e9, 2), ln_chu_ky=f"{pnl/cap*100:+.2f}%",
                n_deal=len(r),
                tb=f"{r.mean()*100:+.2f}%" if len(r) else "-",
                trung_vi=f"{r.median()*100:+.2f}%" if len(r) else "-",
                winrate=f"{(r>0).mean()*100:.1f}%" if len(r) else "-",
                lo_gt20=f"{(r<-0.20).mean()*100:.1f}%" if len(r) else "-"), r

rows, rets = [], {}
for lo, hi, name in BANDS:
    if name.startswith("E"):
        d = pos[~pos.blocked]
    else:
        d = pos[pos.blocked & (pos.adv_vnd > lo) & (pos.adv_vnd <= hi)]
    s = stat(d)
    if s:
        rows.append(dict(bang=name, **s[0])); rets[name] = s[1]

print(pd.DataFrame(rows).to_string(index=False))

ref = rets[BANDS[-1][2]]
rng = np.random.default_rng(20260810)
print("\nCI95 bootstrap chenh return/deal so voi bang E (>=2 ty):")
for _, _, name in BANDS[:-1]:
    r = rets.get(name)
    if r is None or len(r) < 10:
        print(f"  {name}: n_deal={0 if r is None else len(r)} — qua mong, khong bootstrap"); continue
    a, b = r.values, ref.values
    d = np.array([rng.choice(a, len(a), True).mean() - rng.choice(b, len(b), True).mean() for _ in range(10000)])
    print(f"  {name}: diem {(a.mean()-b.mean())*100:+.2f}pp | CI95 [{np.percentile(d,2.5)*100:+.2f}; {np.percentile(d,97.5)*100:+.2f}] "
          f"| {'KHAC 0' if (np.percentile(d,2.5)>0)==(np.percentile(d,97.5)>0) else 'CHUA KHAC 0'}")

# nhom "song" 1e8..2e9 gop lai = vung gate 2 ty THEM vao so voi gate ADV>0 hien co
live = pos[pos.blocked & (pos.adv_vnd > 1e8) & (pos.adv_vnd < 2e9)]
s = stat(live)
print("\n*** VUNG QUYET DINH THAT (0,1 ty < ADV < 2 ty = phan gate 2 ty THEM vao tren nen live) ***")
print(pd.DataFrame([dict(bang="THEM vao boi gate 2 ty", **s[0])]).to_string(index=False))
a, b = s[1].values, ref.values
d = np.array([rng.choice(a, len(a), True).mean() - rng.choice(b, len(b), True).mean() for _ in range(10000)])
print(f"chenh return/deal vs nhom >=2 ty: {(a.mean()-b.mean())*100:+.2f}pp | CI95 "
      f"[{np.percentile(d,2.5)*100:+.2f}; {np.percentile(d,97.5)*100:+.2f}]")
live.to_csv("mike/agents/Taylor/exp_advgate_quality_20260810/pos_band_live_relevant.csv", index=False)
