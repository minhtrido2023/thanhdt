# -*- coding: utf-8 -*-
"""Cau hoi provenance quyet dinh: neu chay CHINH chien luoc tren tape FiinX vs tape vnstock
cho CUNG 80 phien trung nhau, ket qua co giong nhau khong? Neu giong => doan mo rong
2022-02..2023-09 (chi co FiinX) dung duoc; neu lech he thong => khong dung duoc."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, ".")
import extend as E  # tai dung days_from_local/sim

L = E.days_from_local()
F = pd.read_csv("fiinx_daily_overlap.csv"); F["src"] = "fiinx"
F = F[(F["nop"] >= 10) & (F["nseg29"] > 0) & (F["hmL"] >= "14:25")]
common = sorted(set(L["date"]) & set(F["date"]))
Lc = L[L["date"].isin(common)].sort_values("date").reset_index(drop=True)
Fc = F[F["date"].isin(common)].sort_values("date").reset_index(drop=True)
print("Ngay trung: %d (%s..%s)\n" % (len(common), common[0], common[-1]))

print("=== Lech o muc DAI LUONG dau vao ===")
for c in ["c_first", "entry", "exit29", "exit30", "minlow29", "maxhigh29"]:
    dv = (Fc[c].astype(float).values - Lc[c].astype(float).values)
    print("  %-11s khop=%2d/%d  maxabs=%.4f  mean_bias=%+.5f" %
          (c, int((abs(dv) <= 1e-9).sum()), len(dv), abs(dv).max(), dv.mean()))

print("\n=== Lech o muc KET QUA CHIEN LUOC (cai thuc su quan trong) ===")
for ec in ["exit29", "exit30"]:
    rF = E.sim(Fc, ec); rL = E.sim(Lc, ec)
    mm = rF[["date", "sig", "net"]].merge(rL[["date", "sig", "net"]], on="date", suffixes=("_f", "_l"))
    dn = (mm["net_f"] - mm["net_l"])
    print("  exit=%s | trade FiinX=%d vnstock=%d khop ngay=%d | sig khac=%d"
          % (ec, len(rF), len(rL), len(mm), int((mm["sig_f"] != mm["sig_l"]).sum())))
    print("      mean FiinX=%+7.2fbps  vnstock=%+7.2fbps  delta=%+6.2fbps  |delta| max=%.2fbps"
          % (rF["net"].mean()*1e4, rL["net"].mean()*1e4, dn.mean()*1e4, dn.abs().max()*1e4))
    print("      Sharpe FiinX=%+.2f  vnstock=%+.2f"
          % (rF["net"].mean()/rF["net"].std(ddof=1)*np.sqrt(252),
             rL["net"].mean()/rL["net"].std(ddof=1)*np.sqrt(252)))
