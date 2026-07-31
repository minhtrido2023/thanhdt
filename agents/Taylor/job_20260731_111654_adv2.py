"""Viec 2b — cung so lieu ADV nhung quy ve NAV FLEET THAT (khong phai so 50 ty cua backtest).

Doc lai research/capit_adv_check_20260731.csv (da tinh o buoc truoc, cung cong thuc production).
"""
import numpy as np, pandas as pd, glob, json

W = "/home/trido/thanhdt/WorkingClaude"
R = pd.read_csv(f"{W}/research/../mike/agents/Taylor/research/capit_adv_check_20260731.csv")
NAV_BT = 50e9
nav_real = 0.0
for lab in ("SpaceX", "ZaloPay"):
    d = pd.read_csv(f"{W}/data/execution_logs/nav_history_{lab}.csv").iloc[-1]
    print(f"  {lab}: NAV {float(d.nav)/1e9:.3f}B @ {d.date}")
    nav_real += float(d.nav)
print(f"  FLEET NAV that = {nav_real/1e9:.3f}B VND (backtest dung {NAV_BT/1e9:.0f}B => x{NAV_BT/nav_real:.1f})\n")

# cap_tot_bn khong phu thuoc NAV; target thi co
R["tgt_real_bn"] = R["size"] * 0.25 * nav_real / 1e9
R["util_real"] = R.tgt_real_bn / R.cap_tot_bn
R["pername_real_bn"] = R.tgt_real_bn / R.n

print(R[["E", "ngay", "size", "n", "tgt_real_bn", "cap_tot_bn", "util_real"]]
      .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
print(f"\nO NAV THAT ({nav_real/1e9:.2f}B): util median {R.util_real.median():.4f}, "
      f"max {R.util_real.max():.4f} (E{int(R.loc[R.util_real.idxmax(),'E'])} "
      f"{R.loc[R.util_real.idxmax(),'ngay']}), so su kien util>1: {(R.util_real>1).sum()}/{len(R)}")

# NAV nguong: navsize:0.25 cham tran TONG cua su kien chat nhat
for lab, q in (("worst", R.k_feasible.min()), ("p10", R.k_feasible.quantile(0.10)),
               ("median", R.k_feasible.median())):
    print(f"  NAV toi da de navsize:0.25 KHONG cham cap tong ({lab} event): "
          f"{NAV_BT*q/0.25/1e9:.1f}B VND")

# tran navsize kha thi o NAV that (nguoc lai: he so k lon nhat con vua)
k_at_real = (R.cap_tot_bn * 1e9 / (R["size"] * nav_real))
print(f"\nHe so navsize TOI DA con vua cap tong tai NAV that: "
      f"min {k_at_real.min():.2f} (E{int(R.loc[k_at_real.idxmin(),'E'])}), "
      f"p10 {k_at_real.quantile(0.10):.2f}, median {k_at_real.median():.2f}")
print("  => o quy mo hien tai, tran ADV KHONG phai rang buoc rang buoc navsize:0.25.")
