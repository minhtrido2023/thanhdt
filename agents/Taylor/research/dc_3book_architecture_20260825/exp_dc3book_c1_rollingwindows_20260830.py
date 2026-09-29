# -*- coding: utf-8 -*-
"""exp_dc3book_c1_rollingwindows_20260830.py -- R&D: rolling 4-window IS/OOS
breakdown for C1 (state-conditional BULL-only LAG->DC swap).

Job Taylor_20260829_173433 (dispatch Mike), viec 3 trong danh sach nghien cuu
cuoi tuan -- dieu kien mo lai C1 do quant-skeptic dat ra khi REFUTED plan
live-25% (2026-08-26): "rolling 3-4 window IS/OOS split (not just 2), de xem
OOS benefit co tap trung vao 1-2 lucky episodes khong."

RESEARCH ONLY -- khong sua production code/CSV, khong wire gi. Tai dung 100%
data da co san tu job Taylor_20260825_153800 (Phan A + Phan B), khong backtest
lai tu dau:
  - exp_dc3book_c1_stateswap_univpit.csv (Phan A): date, state, r_bal, r_lag,
    r_dc, port_c1_stateswap, baseline_2book_prod -- daily, 2014-08-05..2026-06-19
  - Doi chieu voi P3_B_factormatrix_bootstrap.md (Phan B, da co san 3-giai-doan
    OOS stability: pre-2017/2017-2020/2020-nay) -- script nay LAM MIN HON o
    OOS (tach 2020-2022 vs 2023-2026) de tra loi cau hoi cu the "COVID-era
    concentration" ma Phan B chua tach.

Windows (4, non-overlapping, khop dung ranh gioi IS/OOS goc):
  W1 2014-01-01..2016-12-31   (IS early)
  W2 2017-01-01..2019-12-31   (IS late)     -- W1+W2 = "IS 2014-19" goc
  W3 2020-01-01..2022-12-31   (OOS early, covid rally + 2021 breakout)
  W4 2023-01-01..2026-06-19   (OOS late)     -- W3+W4 = "OOS 2020+" goc

Cho moi window: (a) CAGR port_c1_stateswap vs baseline_2book_prod + delta
(portfolio-level, tinh tu cumulative product cua daily return trong window --
KHONG phai CAGR toan mau bi cat, day la CAGR CUC BO cua window do, dung de so
sanh magnitude giua cac window, khong dung de cong don ve CAGR full-sample).
(b) BULL-only gross_BAL/gross_LAG/gross_DC (arithmetic annualization = mean
daily return trong (window AND state==BULL) x 252 -- dung convention Phan B).
(c) N BULL days + N BULL episode rieng biet (dem qua transition vao/ra BULL)
trong window do.
"""
import os

import numpy as np
import pandas as pd

OUTDIR = os.path.dirname(os.path.abspath(__file__))
INCSV = os.path.join(OUTDIR, "exp_dc3book_c1_stateswap_univpit.csv")
BULL_STATE = 4  # state coding: 1 CRISIS,2 BEAR,3 NEUTRAL,4 BULL,5 EXBULL (khop exp_dc3book_c1_stateswap_20260825.py)

WINDOWS = [
    ("W1_2014_2016", "2014-01-01", "2016-12-31"),
    ("W2_2017_2019", "2017-01-01", "2019-12-31"),
    ("W3_2020_2022", "2020-01-01", "2022-12-31"),
    ("W4_2023_2026", "2023-01-01", "2026-06-19"),
]


def port_cagr_window(r):
    r = r.dropna()
    if len(r) < 2:
        return np.nan, 0
    s = (1 + r).cumprod()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    if yrs <= 0:
        return np.nan, len(r)
    cagr = (s.iloc[-1] ** (1 / yrs) - 1) * 100
    return cagr, len(r)


def count_bull_episodes(state_series):
    """Dem so lan bat dau mot chuoi lien tuc state==BULL (episode) trong series da cat theo window.
    Mot episode co the bi CAT NGANG boi bien window (vi du 2020-12->2021-03 nam giua W3) -- ham nay
    dem episode BAT DAU trong window, khop dung dinh nghia 'episode' cua Phan A (dem qua flip)."""
    is_bull = (state_series == BULL_STATE).values
    n_ep = 0
    prev = False
    for b in is_bull:
        if b and not prev:
            n_ep += 1
        prev = b
    return n_ep


def main():
    df = pd.read_csv(INCSV, parse_dates=["date"]).set_index("date").sort_index()
    print(f"Loaded {INCSV}: {df.index[0].date()} -> {df.index[-1].date()}, {len(df)} rows")

    rows = []
    for name, start, end in WINDOWS:
        sub = df.loc[start:end]
        n_days_total = len(sub)

        cagr_c1, n_c1 = port_cagr_window(sub["port_c1_stateswap"])
        cagr_base, n_base = port_cagr_window(sub["baseline_2book_prod"])
        delta = cagr_c1 - cagr_base if (np.isfinite(cagr_c1) and np.isfinite(cagr_base)) else np.nan

        bull = sub[sub["state"] == BULL_STATE]
        n_bull_days = len(bull)
        n_bull_ep = count_bull_episodes(sub["state"])
        if n_bull_days > 0:
            gross_bal = bull["r_bal"].mean() * 252 * 100
            gross_lag = bull["r_lag"].mean() * 252 * 100
            gross_dc = bull["r_dc"].mean() * 252 * 100
            leader = max([("BAL", gross_bal), ("LAG", gross_lag), ("DC", gross_dc)], key=lambda x: x[1])[0]
            dc_vs_lag = gross_dc - gross_lag
        else:
            gross_bal = gross_lag = gross_dc = dc_vs_lag = np.nan
            leader = "N/A (0 BULL days)"

        rows.append(dict(
            window=name, start=start, end=end, n_days_total=n_days_total,
            cagr_c1_pct=cagr_c1, cagr_baseline_pct=cagr_base, delta_pp=delta,
            n_bull_days=n_bull_days, n_bull_episodes=n_bull_ep,
            gross_BAL_bull_pct=gross_bal, gross_LAG_bull_pct=gross_lag, gross_DC_bull_pct=gross_dc,
            DC_minus_LAG_pp=dc_vs_lag, leader_in_BULL=leader,
        ))

    out = pd.DataFrame(rows)
    outcsv = os.path.join(OUTDIR, "exp_dc3book_c1_rollingwindows_metrics.csv")
    out.to_csv(outcsv, index=False)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 20)
    print("\n" + "=" * 120)
    print("ROLLING 4-WINDOW: C1 stateswap vs baseline (portfolio-level) + BULL-only gross factor leadership")
    print("=" * 120)
    print(out.to_string(index=False))

    # summary check requested by dispatch: OOS benefit (W3+W4) spread or concentrated?
    is_delta_sum = out.loc[out["window"].isin(["W1_2014_2016", "W2_2017_2019"]), "delta_pp"].sum()
    oos_w3 = out.loc[out["window"] == "W3_2020_2022", "delta_pp"].iloc[0]
    oos_w4 = out.loc[out["window"] == "W4_2023_2026", "delta_pp"].iloc[0]
    print(f"\nIS windows (W1+W2) delta sum: {is_delta_sum:+.2f}pp (window-local CAGR delta, khong cong don duoc "
          f"thanh CAGR full-sample -- chi de xem DAU cua tung window)")
    print(f"OOS W3 (2020-2022) delta: {oos_w3:+.2f}pp | OOS W4 (2023-2026) delta: {oos_w4:+.2f}pp")
    print(f"wrote {outcsv}")


if __name__ == "__main__":
    main()
