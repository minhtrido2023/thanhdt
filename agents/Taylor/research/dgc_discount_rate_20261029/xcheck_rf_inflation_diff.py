"""Kiểm chéo rf theo chênh lệch lạm phát (job Taylor_20261030_031028). KHÔNG đổi luật PREREG, KHÔNG đổi out_*.csv cũ.
rf_VND = (1+UST10Y)(1+π_VN)/(1+π_US) − 1.  UST10Y = FRED DGS10 2026-10-28 = 5,05% [SRC: fred.stlouisfed.org/series/DGS10,
tải qua fredgraph.csv?id=DGS10 ngày 30/10/2026]. π_US kỳ vọng = FRED T10YIE (breakeven 10Y) 2026-10-28 = 2,38% [SRC]. π_VN = mục tiêu 4,0/4,25/4,5 [UL].
UST đã gồm phần bù kỳ hạn Mỹ, KHÔNG gồm rủi ro quốc gia VN (CRP đã nằm trong ERP Damodaran 3,90) ⇒ nếu có tính đôi thì nằm ở (c): lãi thực 2,5% đã '+đến 1pp EM'."""
import os, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
UST, PI_US, BETA, ERP = 5.05, 2.38, 1.11, 8.13
rows = []
for pv in (4.0, 4.25, 4.5):
    rf = ((1 + UST / 100) * (1 + pv / 100) / (1 + PI_US / 100) - 1) * 100
    rows.append(dict(pi_vn=pv, rf_infl_diff=round(rf, 2), ke_if_rf=round(rf + BETA * ERP, 2),
                     delta_vs_c_giua_pp=round(rf - 6.75, 2)))
d = pd.DataFrame(rows); print(d.to_string(index=False))
print(f"Lãi thực Mỹ ngầm định = UST − T10YIE = {UST - PI_US:.2f}% (so với lãi thực 2,5% của (c))")
d.to_csv(os.path.join(HERE, "out_rf_infl_diff.csv"), index=False)
