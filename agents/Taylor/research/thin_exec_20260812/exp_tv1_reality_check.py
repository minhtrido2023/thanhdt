"""Đối chiếu mô phỏng với KẾT QUẢ THẬT DUY NHẤT đã biết: TV1 2026-08-11.
Thật (email khớp lệnh DNSE): SpaceX 100/2.000cp, ZaloPay 0/1.300cp.
Nếu mô phỏng cho ra số lớn hơn NHIỀU thì κ (hoặc mô hình fill) đang quá lạc quan —
phải nói ra, không được im."""
import pandas as pd, exp_ceiling_tolerance as T
df = T.load(f"{T.BARS}/TV1.csv")
dd = df.groupby("date").agg(vol=("volume","sum"), close=("close","last"))
dd["turn"]=dd.vol*dd.close; dd["adv20"]=dd.turn.rolling(20,min_periods=10).mean().shift(1)
import datetime as dt
for day in (dt.date(2026,8,11), dt.date(2026,8,12)):
    b = df[df.date==day]; adv20=float(dd.loc[day,"adv20"])
    print(f"\n--- TV1 {day} | ADV20={adv20/1e6:.0f}tr | KL phiên={int(b.volume.sum())}cp "
          f"| low={b.low.min():.0f} high={b.high.max():.0f} ---")
    for kap in (0.15,0.34,0.60,1.00):
        for pac,lab in (("current","hiện tại"),("adv_only","bỏ trần")):
            f,c = T.run_session(b, 3300, 20000.0, adv20, kap, pac)
            print(f"  κ={kap:.2f} {lab:9s} → mô phỏng khớp {f:5d}cp / 3.300cp cần "
                  f"(2 account gộp)")
print("\nTHẬT 08-11: 100cp/3.300cp (SpaceX 100/2000, ZaloPay 0/1300).")
