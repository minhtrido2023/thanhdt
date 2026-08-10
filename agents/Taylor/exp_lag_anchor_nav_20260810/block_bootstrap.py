# -*- coding: utf-8 -*-
"""Paired block-bootstrap cho Δ CAGR giữa 2 chân trần anchor — artifact chạy được.

Vì sao tồn tại: vòng quant-skeptic 2026-08-10 (job Taylor_20260810_101717) chỉ ra bootstrap là
THỐNG KÊ QUYẾT ĐỊNH duy nhất của báo cáo mà KHÔNG có script nào tái lập được — người kiểm phải tự
viết lại. File này đóng lỗ hổng đó (§18 "verify artifact, not self-report").

Đọc THẲNG CSV audit từng chân, không tin số in ra log.
Chạy: $DNA_PYEXE block_bootstrap.py
"""
import os
import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
BASE = ("v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_"
        "wtnamecap_advprice_exp_{tag}_univpit.csv")

BLOCK = 21        # ~1 tháng giao dịch — giữ tự tương quan trong khối
NREP = 4000
SEED = 20260810
SPY = 252.0

# (nhãn, chân A = cơ sở, chân B = so sánh)
PAIRS = [
    ("Ho 5 phien : LD(x1,03) - LA(=anchor)", "anch_LA_cap000", "anch_LD_cap003"),
    ("Ho 3 phien : WD(x1,03) - WA(=anchor)", "anch_WA_w3cap000", "anch_WD_w3cap003"),
]


def load_nav(tag):
    """Chuỗi NAV cuối ngày, index theo ngày."""
    path = os.path.join(WORKDIR, "data", BASE.format(tag=tag))
    df = pd.read_csv(path, low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    s = d.groupby("ymd")["combined_nav"].last()
    return s


def ann_pct(logret_sum, n_days):
    """Đổi tổng log-return sang CAGR %/năm."""
    return (np.exp(logret_sum / n_days * SPY) - 1.0) * 100.0


def run_pair(label, tag_a, tag_b):
    a, b = load_nav(tag_a), load_nav(tag_b)
    idx = a.index.intersection(b.index)          # cùng lịch ⇒ ghép cặp đúng theo NGÀY
    ra = np.diff(np.log(a.loc[idx].values))
    rb = np.diff(np.log(b.loc[idx].values))
    n = len(ra)

    point = ann_pct(rb.sum(), n) - ann_pct(ra.sum(), n)

    # bootstrap GHÉP CẶP: cùng bộ khối cho cả 2 chân ⇒ khử rủi ro thị trường chung,
    # chỉ còn lại chênh lệch do đúng 1 tham số (trần).
    rng = np.random.default_rng(SEED)
    nblk = int(np.ceil(n / BLOCK))
    diffs = np.empty(NREP)
    for i in range(NREP):
        starts = rng.integers(0, n - BLOCK + 1, size=nblk)
        take = (starts[:, None] + np.arange(BLOCK)[None, :]).ravel()[:n]
        diffs[i] = ann_pct(rb[take].sum(), n) - ann_pct(ra[take].sum(), n)

    lo, hi = np.percentile(diffs, [2.5, 97.5])
    p_pos = float((diffs > 0).mean())
    print(f"\n{label}")
    print(f"  n phien={n}  block={BLOCK}  nrep={NREP}  seed={SEED}")
    print(f"  Diem uoc luong Δ CAGR = {point:+.3f} pp")
    print(f"  CI95 = [{lo:+.3f}; {hi:+.3f}] pp   ->  {'CHUA 0 (khong bac duoc H0)' if lo < 0 < hi else 'KHONG chua 0'}")
    print(f"  P(Δ>0) = {p_pos:.3f}")
    return point, lo, hi, p_pos


if __name__ == "__main__":
    print("Paired block-bootstrap — Δ CAGR (pp/nam), tran anchor NAV-level")
    for label, ta, tb in PAIRS:
        run_pair(label, ta, tb)
    print("\nLuu y: CI xe dich ~0,01-0,05pp theo SEED. Ket luan (CI chua 0, P~0,5) khong doi theo seed.")
