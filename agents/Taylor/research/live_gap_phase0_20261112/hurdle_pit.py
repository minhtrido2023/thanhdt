#!/usr/bin/env python3
"""GD0 viec 1 — HURDLE PIT = lai tiet kiem hieu dung theo ngay, max(Big-4 12M, CCTG) .
Nguon: deposit_rate_vn.effective_deposit_events_df() (step series; Big-4 12M online + CCTG 6M->12M tu 2026-09-30/10-05)
       + chuoi dep1m (fiinprox_deposit_1m_big4, thang) chi de THAM CHIEU (khong vao hurdle).
Quy uoc: lai DON, actual/365, buoc (step) theo ngay hieu luc; accrual tren [d0,d1): moi ngay lich dung muc co hieu luc tai ngay do.
Doan phuc dung: Big-4 12M truoc 2019 = anchor dong bang trong deposit_rate_vn.DEPOSIT_EVENTS (26 moc tay, KHONG phai chuoi cong bo theo ngay).
Chay: /home/trido/thanhdt/wc_venv/bin/python hurdle_pit.py   (xuat hurdle_pit.csv + selfcheck)
"""
import sys, os
import pandas as pd, numpy as np
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import deposit_rate_vn as D
HERE = os.path.dirname(os.path.abspath(__file__))
DEP1M = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/idle_cash_proxy_20260927/fiinprox_deposit_1m_big4_monthly_2019_2026.csv"

def build(end="2026-11-12"):
    big4 = D.deposit_events_df().rename(columns={"deposit_rate": "big4_12m"})
    eff = D.effective_deposit_events_df().rename(columns={"deposit_rate": "hurdle_pct"})
    days = pd.DataFrame({"date": pd.date_range("2011-01-01", end, freq="D")})
    days = pd.merge_asof(days, big4.rename(columns={"time": "date"}), on="date")
    days = pd.merge_asof(days, eff.rename(columns={"time": "date"}), on="date")
    d1 = pd.read_csv(DEP1M)
    d1["avail"] = pd.to_datetime(d1["period"] + "-01") + pd.offsets.MonthBegin(1)   # PIT: mốc tháng T dùng từ ngày đầu T+1
    days = pd.merge_asof(days, d1[["avail", "rate_pct"]].rename(columns={"avail": "date", "rate_pct": "dep1m_big4_ref"}), on="date")
    days["segment"] = np.where(days.date < "2019-01-01", "RECON_frozen_anchor(Big4-12M tay, khong cong bo theo ngay)",
                        np.where(days.date < "2026-09-30", "Big4-12M_anchor(tay) ", "max(Big4-12M,CCTG)"))
    return days

H = build()

def accrual_pct(d0, d1, df=H):
    """Loi suat tiet kiem tich luy [d0,d1) (%), lai don act/365, muc buoc theo ngay."""
    d0, d1 = pd.Timestamp(d0), pd.Timestamp(d1)
    s = df[(df.date >= d0) & (df.date < d1)].hurdle_pct
    return float(s.sum() / 365.0)

def flat_pct(d0, d1, rate=None):
    """Quy uoc 'phang' Mike dung: rate hien tai x so ngay/365."""
    rate = float(H.hurdle_pct.iloc[-1]) if rate is None else rate
    return rate * (pd.Timestamp(d1) - pd.Timestamp(d0)).days / 365.0

if __name__ == "__main__":
    H.to_csv(os.path.join(HERE, "hurdle_pit.csv"), index=False, float_format="%.4f")
    cur = float(H.hurdle_pct.iloc[-1])
    print("hurdle hien tai (2026-11-12) =", cur)
    a = accrual_pct("2026-07-01", "2026-11-11"); f = flat_pct("2026-07-01", "2026-11-11")
    print(f"01/07->11/11 (133 ngay): PIT-buoc = {a:.3f}% | phang 7.4% = {f:.3f}%")
    assert abs(cur - 7.4) < 1e-9
    assert abs(f - 2.696) < 0.005
    print("n dong", len(H), "| min", H.date.min().date(), "max", H.date.max().date())
    for y in range(2011, 2027):
        print(y, round(H[H.date.dt.year == y].hurdle_pct.mean(), 2))
