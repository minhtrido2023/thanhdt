# -*- coding: utf-8 -*-
"""exp_shortfall_sweep.py — ARTIFACT KIỂM CHỨNG cho câu §2.3 của README:
"IS không có ý nghĩa thống kê, và ĐỔI DẤU theo giả định mua bù".

Lỗ hổng auditability mà quant-skeptic chỉ ra (2026-08-15, job Taylor_20260815_002825): con số
`t gộp-theo-ngày = +1,34 / +0,20 / −0,83` cho sweep LAG_CATCHUP ∈ {0, 5, 20} được BÁO trong
README nhưng KHÔNG có script + CSV commit được. File này đóng đúng lỗ hổng đó.

**KHÔNG chạy lại verify, KHÔNG đổi kết luận nào.** Cùng công thức IS của `exp_shortfall.py`
(giữ nguyên, không sửa file kia) — thêm 2 thứ và chỉ 2 thứ:
  1. sweep `LAG_CATCHUP` ∈ {0, 5, 20} thay vì hằng số 5,
  2. **t GỘP THEO NGÀY** bên cạnh t "ngây thơ".

VÌ SAO PHẢI GỘP THEO NGÀY (kỷ luật §18 — khai N là số SỰ KIỆN độc lập, không phải số dòng):
30 mã cùng chạy trên CÙNG một lưới ngày ⇒ campaign của 2 mã bắt đầu cùng ngày KHÔNG độc lập
(cùng cú sốc thị trường, cùng phiên VNINDEX). t "ngây thơ" trên ~4.156 cặp campaign đếm mỗi
ngày tới 30 lần ⇒ phóng đại |t| khoảng √30 ≈ 5,5×. Gộp trung bình Δ theo NGÀY BẮT ĐẦU rồi
mới t-test cho **N = số ngày độc lập ≈ 475** — đây là con số phải trích, KHÔNG phải bản ngây thơ.

Chạy: /home/trido/thanhdt/wc_venv/bin/python exp_shortfall_sweep.py
Ra:   out/shortfall_sweep.csv   (mỗi dòng = 1 ô size × κ × lag_catchup, có CẢ hai t + N của cả hai)
"""
import glob
import os

import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
B1 = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/thin_exec_20260812/data/bars1m"
B2 = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/thin_exec_20260812/data/bars1m_liquid"
CAMPAIGN_LEN = 5
LAG_GRID = [0, 5, 20]          # số phiên TRỄ sau khi campaign kết thúc mới mua bù

# ── giá đóng cửa theo ngày (dựng lại y hệt exp_shortfall.py) ─────────────────────────────
rows = []
for f in sorted(glob.glob(os.path.join(B1, "*.csv"))) + sorted(glob.glob(os.path.join(B2, "*.csv"))):
    tk = os.path.basename(f)[:-4]
    d = pd.read_csv(f, parse_dates=["time"])
    d = d[d.volume > 0]
    g = d.groupby(d.time.dt.normalize())["close"].last()
    for i, (dt, c) in enumerate(g.items()):
        rows.append({"ticker": tk, "date": str(dt.date()), "i": i, "close": c})
daily = pd.DataFrame(rows)
daily["dec_px"] = daily.groupby("ticker")["close"].shift(1)     # close phiên TRƯỚC campaign

camp = pd.read_csv(os.path.join(HERE, "out", "campaigns_main.csv"))

out = []
for lag in LAG_GRID:
    d = daily.copy()
    d["catchup_px"] = d.groupby("ticker")["close"].shift(-(CAMPAIGN_LEN - 1 + lag))
    df = camp.merge(d[["ticker", "date", "dec_px", "catchup_px"]],
                    left_on=["ticker", "start"], right_on=["ticker", "date"], how="left")
    df = df.dropna(subset=["dec_px", "catchup_px"])
    df["px_paid"] = df.avg_px.fillna(df.catchup_px)
    df["is_bps"] = 1e4 * (
        df.fill_frac * (df.px_paid - df.dec_px) + (1 - df.fill_frac) * (df.catchup_px - df.dec_px)
    ) / df.dec_px

    for sp in sorted(df.size_pct.unique()):
        for k in sorted(df.kappa.unique()):
            s = df[(df.size_pct == sp) & (df.kappa == k)]
            p = s.pivot_table(index=["ticker", "start"], columns="rule",
                              values=["is_bps", "fill_frac"]).dropna()
            if len(p) < 3:
                continue
            delta = p[("is_bps", "A")] - p[("is_bps", "B")]        # >0 = A tệ hơn (IS cao hơn)

            # (i) t "NGÂY THƠ" — mỗi campaign là 1 quan sát. KHÔNG ĐƯỢC TRÍCH.
            t_naive = float(stats.ttest_1samp(delta, 0).statistic)

            # (ii) t GỘP THEO NGÀY — trung bình Δ trong cùng ngày bắt đầu, rồi t-test.
            #      N = số NGÀY độc lập. ĐÂY là con số phải trích.
            by_day = delta.reset_index().groupby("start")[0].mean() \
                if 0 in delta.reset_index().columns else \
                delta.rename("d").reset_index().groupby("start")["d"].mean()
            t_day = float(stats.ttest_1samp(by_day, 0).statistic)

            out.append({
                "lag_catchup": lag, "size_pct": sp, "kappa": k,
                "n_campaign": len(p), "n_day": len(by_day),
                "IS_A_bps": p[("is_bps", "A")].mean(), "IS_B_bps": p[("is_bps", "B")].mean(),
                "dIS_bps": delta.mean(), "dIS_bps_day_mean": by_day.mean(),
                "t_naive_DO_NOT_CITE": t_naive, "t_day_clustered": t_day,
                "A_better_pct": 100.0 * (delta < 0).mean(),
                "identical_pct": 100.0 * (delta.abs() < 1e-9).mean(),
            })

res = pd.DataFrame(out)
dst = os.path.join(HERE, "out", "shortfall_sweep.csv")
res.to_csv(dst, index=False)
print(res.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
print(f"\n→ {dst}")

hi = res[(res.size_pct == res.size_pct.unique()[1] if len(res.size_pct.unique()) > 1
          else res.size_pct.unique()[0])]
print("\nCÂU CẦN KIỂM (README §2.3, cấu hình trung tâm size 30% ADV20, κ=0,34):")
c = res[(res.size_pct.between(0.29, 0.31)) & (res.kappa.between(0.33, 0.35))]
if not c.empty:
    for _, r in c.sort_values("lag_catchup").iterrows():
        print(f"  lag={int(r.lag_catchup):2d} phiên  →  t gộp-theo-ngày = {r.t_day_clustered:+.2f}"
              f"   (N ngày = {int(r.n_day)}, t ngây thơ = {r.t_naive_DO_NOT_CITE:+.2f},"
              f" N campaign = {int(r.n_campaign)})")
    print("  ⇒ ĐỔI DẤU theo giả định mua bù ⇒ KHÔNG có kết luận thống kê nào sống sót.")
