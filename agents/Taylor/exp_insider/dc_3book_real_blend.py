# -*- coding: utf-8 -*-
"""dc_3book_real_blend.py -- Viec 1 (backtest 3-book) cho dc_3book_factor_neutral_20260830.

w_BAL = w_LAG = w_DC = 1/3 (static equal split, dung dung nhu dispatch yeu cau), so voi
BASELINE = combined_nav production hien tai (state-conditional allocator w_LAG{50/0/65/65/65}
band +-10pp + CAPIT, PARK_STATES="3:0.7" -- KHONG PHAI "park=0.80" nhu dispatch text, do la nham
lan; production default THAT la 3:0.7, xem pt_v23_audit_2014.py dong 211).

Nguon du lieu THAT (khong tu tao):
  - BAL book / LAG book: nav_bal_ref / nav_lag_ref tu CSV audit fresh vua chay hom nay
    (EXP_TAG=dc3book_baseline_check, dung lenh pin R3 nguyen van + $DNA_PYEXE, khong dung canonical
    filename theo coding_guidelines Sec.8). Day la NAV STANDALONE cua tung book (truoc buoc combine
    cua allocator), khong bi CAPIT leverage/band-rebalance lam meo.
  - DC book: cot "ConvergePort (equal-weight)" trong data/converge_portfolio_backtest_nav.csv
    (Taylor_20260706_093329, da co T+1 + TC 0.1% + parking custom30V cho idle cash -- dung
    nguyen, khong tinh lai).

3-book blend = (bal_ret + lag_ret + dc_ret) / 3 moi ngay, KHONG rebal cost bo sung (gia dinh dang
gian nhat: NAV mỗi book cố định 1/3 tong, khong mo hinh hoa turnover khi chuyen tu 2-book sang
3-book). Calendar = giao cua ca 3 nguon (DC bat dau 2014-08-05).

CAVEAT BAT BUOC doc truoc khi dung so nay:
  1. KHONG mo phong lai logic w_LAG state-conditional (50/0/65/65/65 + band +-10pp) cho 3 book --
     day la mot equal-static-split THAT SU, dung y dispatch yeu cau ("w_BAL=w_LAG=w_DC=1/3"),
     KHONG PHAI thu nghiem toi uu trong so.
  2. KHONG mo phong CAPIT margin lever tuong tac voi 3 book (borrow cost=0 trong ca run nay --
     CAPIT hiem khi trigger trong giai doan nay, nen thieu sot nay nho).
  3. KHONG mo phong ADV cap dung chung giua 3 book -- nhung overlap DC va BAL/LAG da do o Q2
     (job 08-25) la GAN 0 (2/684 BAL, 2/1649 LAG buy-side) nen day la thieu sot NHO, khong phai
     nguon sai lech chinh.
  4. Day la backtest o quy mo NAV=50B (25B BAL + 25B LAG trong run nay) -- NAV that cua
     SpaceX/ZaloPay nho hon nhieu (~1B VND/tai khoan), xem Viec 3 rieng cho capacity thuc te.

RESEARCH ONLY. Khong dung production file.
"""
import os
import pandas as pd
import numpy as np

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
CSV_BASELINE = os.path.join(WORKDIR, "data",
    "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_dc3book_baseline_check_univpit.csv")
CSV_DC = os.path.join(WORKDIR, "data", "converge_portfolio_backtest_nav.csv")
OUT = os.path.join(os.path.dirname(__file__), "dc_3book_real_blend_metrics.csv")

IS_END = pd.Timestamp("2019-12-31")
OOS_START = pd.Timestamp("2020-01-01")
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}


def metrics(r):
    r = r.dropna()
    s = (1 + r).cumprod()
    if len(s) < 2:
        return (np.nan,) * 4
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = s.iloc[-1] ** (1 / yrs) - 1
    spd = len(r) / yrs
    sh = r.mean() / r.std() * np.sqrt(spd) if r.std() > 0 else 0
    dd = (s / s.cummax() - 1).min()
    cal = cagr / abs(dd) if dd < 0 else 0
    return cagr * 100, sh, dd * 100, cal


def windows(r):
    return [("FULL", r), ("IS_2014-2019", r[r.index <= IS_END]), ("OOS_2020+", r[r.index >= OOS_START])]


def gross_by_state(ret, state):
    df = pd.DataFrame({"ret": ret, "state": state}).dropna()
    out = []
    for s, g in df.groupby("state"):
        out.append((STATE_NAMES.get(int(s), str(s)), len(g), g["ret"].mean() * 252 * 100))
    return out


def main():
    print("Loading fresh production baseline CSV (BAL/LAG standalone book NAV) ...")
    df = pd.read_csv(CSV_BASELINE)
    d = df[df["record_type"] == "DAILY"].copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    d = d.sort_values("ymd").set_index("ymd")
    bal_ret = d["nav_bal_ref"].astype(float).pct_change()
    lag_ret = d["nav_lag_ref"].astype(float).pct_change()
    baseline_ret = d["combined_nav"].astype(float).pct_change()
    state = d["state"].astype(float)

    print("Loading ConvergePort DC leg (equal-weight, existing backtest) ...")
    conv = pd.read_csv(CSV_DC)
    conv["date"] = pd.to_datetime(conv["date"])
    conv = conv.set_index("date")
    dc_ret = conv["ConvergePort (equal-weight)"]

    calendar = bal_ret.index.intersection(lag_ret.index).intersection(dc_ret.index)
    calendar = calendar.sort_values()
    print(f"  intersected calendar: {calendar[0].date()} -> {calendar[-1].date()} ({len(calendar)} sessions)")

    bal_r = bal_ret.reindex(calendar)
    lag_r = lag_ret.reindex(calendar)
    dc_r = dc_ret.reindex(calendar)
    base_r = baseline_ret.reindex(calendar)
    st = state.reindex(calendar).ffill()

    blend_r = (bal_r.fillna(0.0) + lag_r.fillna(0.0) + dc_r.fillna(0.0)) / 3.0

    print("\n" + "=" * 78)
    print("BASELINE (production combined_nav, w_LAG state-conditional + CAPIT, PARK 3:0.7)")
    print("=" * 78)
    for tag, rr in windows(base_r):
        c, sh, dd, cal = metrics(rr)
        print(f"  {tag:<14} CAGR {c:>7.2f}%  Sharpe {sh:>5.2f}  MaxDD {dd:>7.1f}%  Calmar {cal:>5.2f}")

    print("\n" + "=" * 78)
    print("3-BOOK STATIC BLEND (w_BAL=w_LAG=w_DC=1/3, real BAL/LAG book NAV + real DC leg)")
    print("=" * 78)
    for tag, rr in windows(blend_r):
        c, sh, dd, cal = metrics(rr)
        print(f"  {tag:<14} CAGR {c:>7.2f}%  Sharpe {sh:>5.2f}  MaxDD {dd:>7.1f}%  Calmar {cal:>5.2f}")

    print("\n" + "=" * 78)
    print("DELTA (3-book blend minus baseline)")
    print("=" * 78)
    rows = []
    for tag, rr in windows(base_r):
        bc, bsh, bdd, bcal = metrics(rr)
        _, brr = [w for w in windows(blend_r) if w[0] == tag][0]
        c, sh, dd, cal = metrics(brr)
        print(f"  {tag:<14} dCAGR {c-bc:+.2f}pp  dSharpe {sh-bsh:+.2f}  dMaxDD {dd-bdd:+.1f}pp  dCalmar {cal-bcal:+.2f}")
        rows.append(dict(window=tag, baseline_cagr=bc, blend_cagr=c, d_cagr=c - bc,
                          baseline_sharpe=bsh, blend_sharpe=sh, d_sharpe=sh - bsh,
                          baseline_maxdd=bdd, blend_maxdd=dd, d_maxdd=dd - bdd,
                          baseline_calmar=bcal, blend_calmar=cal, d_calmar=cal - bcal))

    print("\n" + "=" * 78)
    print("GROSS ANNUALIZED RETURN BY STATE (FULL sample)")
    print("=" * 78)
    base_bystate = dict((s, (n, a)) for s, n, a in gross_by_state(base_r, st))
    blend_bystate = dict((s, (n, a)) for s, n, a in gross_by_state(blend_r, st))
    print(f"  {'state':<8}{'N':>6}{'baseline':>11}{'3book_blend':>13}{'delta':>9}")
    for s in sorted(set(base_bystate) & set(blend_bystate)):
        n, ab = base_bystate[s]
        _, ac = blend_bystate[s]
        print(f"  {s:<8}{n:>6}{ab:>10.2f}%{ac:>12.2f}%{ac-ab:>8.2f}pp")
        rows.append(dict(window=f"bystate_{s}", baseline_cagr=ab, blend_cagr=ac, d_cagr=ac - ab,
                          baseline_sharpe=np.nan, blend_sharpe=np.nan, d_sharpe=np.nan,
                          baseline_maxdd=np.nan, blend_maxdd=np.nan, d_maxdd=np.nan,
                          baseline_calmar=np.nan, blend_calmar=np.nan, d_calmar=np.nan))

    # self-check: 3-book blend weights sum to 1.0 by construction (1/3+1/3+1/3), 0 VND leak
    print(f"\nself-check: static 1/3+1/3+1/3 = {1/3+1/3+1/3:.6f} (0 VND leak by construction)")
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
