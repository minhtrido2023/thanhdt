#!/usr/bin/env python3
"""Đối chứng SỐ HỌC cho chân engine: haircut thuế cổ tức áp post-hoc trên chính ledger anchor.

Cùng công thức đã dùng 2 lần trước (measurement_integrity_audit_20260927/part2/nav_drag.txt và
park_fraction_grid_20260927/park_haircut.py) — chép lại ĐÚNG, không đổi:
    k    = thuế + (1−thuế)×phí_tái_đầu_tư                (phí 0,1% = TC 1 chiều, CLAUDE.md)
    drag = 1 − Π_p(1 − k·DY_p·park_share_p)^(1/yrs)
`DY_p` lấy nguyên 49 kỳ rebal từ part2/dy_by_rebal.csv; `park_share_p` ĐO THẬT trên ledger
((bal_etf_ref+lag_etf_ref)/combined_nav, trung bình ngày trong cửa sổ kỳ) — không giả định tỷ lệ
tuyến tính theo knob park.

Vì sao cần cả HAI cách đo: cách số học này KHÔNG có hồi tiếp (NAV nhỏ hơn ⇒ vị thế nhỏ hơn ⇒ ...),
chân engine thì CÓ. Hai số khớp nhau ở bậc nhất là bằng chứng chân engine hiệu chuẩn đúng; lệch
bậc hai chính là phần hồi tiếp mà chỉ engine đo được.
Dùng: arith_crosscheck.py <ledger.csv> <cagr_gross_pct> [tax]
"""
import sys
import pandas as pd

DY = ("/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/"
      "measurement_integrity_audit_20260927/part2/dy_by_rebal.csv")
FEE = 0.001

csv_path, cagr_gross = sys.argv[1], float(sys.argv[2]) / 100.0
TAX = float(sys.argv[3]) if len(sys.argv) > 3 else 0.05
k = TAX + (1 - TAX) * FEE

df = pd.read_csv(csv_path, low_memory=False)
d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
d = d.dropna(subset=["ymd"]).sort_values("ymd")
g = d.groupby(d["ymd"].dt.normalize()).last()
park = (g["bal_etf_ref"].fillna(0) + g["lag_etf_ref"].fillna(0)) / g["combined_nav"].astype(float)
nav = g["combined_nav"].astype(float)
yrs = (nav.index[-1] - nav.index[0]).days / 365.25

dy = pd.read_csv(DY)
prod = 1.0
for _, r in dy.iterrows():
    m = park[(park.index >= pd.Timestamp(r["start"])) & (park.index < pd.Timestamp(r["end"]))]
    prod *= 1 - k * float(r["dy_period"]) * (float(m.mean()) if len(m) else 0.0)

drag_pp = (1 - prod ** (1 / yrs)) * 100 * (1 + cagr_gross)
print(f"ledger        = {csv_path.split('/')[-1]}")
print(f"tax           = {TAX:.2%}   k = {k:.6f}   fee = {FEE:.3%}")
print(f"window        = {nav.index[0].date()}..{nav.index[-1].date()} = {yrs:.3f} yrs lịch")
print(f"park_share    = trung bình toàn kỳ {park.mean():.4f} (= % NAV, KHÔNG phải knob park)")
print(f"PROD(1-k·DY·park_share) over {len(dy)} kỳ = {prod:.6f}")
print(f"drag CAGR     = {drag_pp:.4f} pp/năm  ⇒  {cagr_gross*100:.4f}% → "
      f"{((1+cagr_gross)*prod**(1/yrs)-1)*100:.4f}%")
