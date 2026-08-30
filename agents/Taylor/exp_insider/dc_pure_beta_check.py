# -*- coding: utf-8 -*-
"""dc_pure_beta_check.py -- Viec 2 (factor-neutral check) cho dc_3book_factor_neutral_20260830.

Cau hoi: outperformance BULL cua ConvergePort (double-confirm) so voi baseline (100% custom30V
park) la ALPHA chon ma hay chi la BETA thuan cua 16 ma universe DC (56% Banking+Securities, tu
nhien re-rate manh trong BULL theo chu ky tin dung VN)?

Cach lam: dung 1 ro doi chung CAP-WEIGHT THUAN cua dung 16 ma universe DC (sector_lens_monitor.NAMES),
KHONG ap double-confirm gate (luon full-invested, cap-weight theo OShares*Close, rebal quy),
so annualized return theo state voi ConvergePort (co gate) tren CUNG 1 calendar/state series da
co san trong data/converge_portfolio_backtest_nav.csv (Taylor_20260706_093329).

RESEARCH ONLY. Khong dung code moi trong production. Doc parquet cache co san
(data/bq_cache/ticker/*.parquet, ticker_financial.parquet, vnindex_5state_dt5g_live.parquet).
"""
import os, sys
import numpy as np, pandas as pd
import duckdb

WORKDIR = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, WORKDIR)
CACHE = os.path.join(WORKDIR, "data", "bq_cache")
OUT = os.path.join(os.path.dirname(__file__), "dc_pure_beta_check_by_state.csv")

import sector_lens_monitor as slm
WL_TK = [n[0] for n in slm.NAMES]
START = "2014-08-05"
TC = 0.001


def con():
    c = duckdb.connect(":memory:"); c.execute("SET threads=1"); return c


def load_prices():
    c = con()
    q = ",".join(f"'{t}'" for t in WL_TK)
    df = c.execute(f"""
        SELECT time, ticker, Close
        FROM read_parquet('{CACHE}/ticker/*.parquet')
        WHERE ticker IN ({q}) AND time >= '{START}'
        ORDER BY time, ticker""").df()
    c.close()
    df["time"] = pd.to_datetime(df["time"])
    return df


def load_oshares():
    c = con()
    q = ",".join(f"'{t}'" for t in WL_TK)
    df = c.execute(f"""
        SELECT ticker, Release_Date, OShares
        FROM read_parquet('{CACHE}/ticker_financial.parquet')
        WHERE ticker IN ({q}) AND Release_Date IS NOT NULL AND OShares IS NOT NULL
        ORDER BY ticker, Release_Date""").df()
    c.close()
    df["Release_Date"] = pd.to_datetime(df["Release_Date"])
    return df


def build_pure_cap_weight_returns(calendar, price_wide, oshares):
    """Quarterly-rebalanced cap-weight (OShares * Close-at-rebal) portfolio of the 16-name
    universe. No gate -- always fully invested (parking=0). Rebal on the first trading day of
    each calendar quarter (mirrors custom30V's quarterly-rebal cadence, no lookahead: uses the
    latest Release_Date <= rebal day OShares)."""
    ret = price_wide.pct_change()
    q_marks = pd.PeriodIndex(calendar, freq="Q")
    rebal_days = calendar.to_series().groupby(q_marks).min().values
    rebal_set = set(pd.Timestamp(d) for d in rebal_days)

    holdings = None  # ticker -> value
    port = pd.Series(0.0, index=calendar)
    turn = pd.Series(0.0, index=calendar)
    for i, d in enumerate(calendar):
        if d in rebal_set or holdings is None:
            asof = oshares[oshares["Release_Date"] <= d]
            if asof.empty:
                if holdings is None:
                    continue
            else:
                last = asof.sort_values("Release_Date").groupby("ticker").tail(1)
                px = price_wide.loc[d] if d in price_wide.index else None
                mc = {}
                for _, row in last.iterrows():
                    tk = row["ticker"]
                    p = px.get(tk) if px is not None else np.nan
                    if np.isfinite(p) and p > 0 and np.isfinite(row["OShares"]) and row["OShares"] > 0:
                        mc[tk] = row["OShares"] * p
                if mc:
                    tot = sum(mc.values())
                    target = {tk: v / tot for tk, v in mc.items()}
                    if holdings is not None and i > 0:
                        prev_val_tot = sum(holdings.values())
                        turn.loc[d] = sum(abs(target.get(tk, 0.0) - (holdings.get(tk, 0.0) / prev_val_tot if prev_val_tot > 0 else 0.0))
                                           for tk in set(list(target) + list(holdings))) / 2.0
                    holdings = target
        if holdings is None or i == 0:
            continue
        r = ret.loc[d]
        num = 0.0; den = 0.0; newh = {}
        for tk, val in holdings.items():
            rt = r.get(tk); rt = rt if np.isfinite(rt) else 0.0
            nv = val * (1 + rt)
            num += val * rt; den += val
            newh[tk] = nv
        port.loc[d] = (num / den if den > 0 else 0.0) - turn.loc[d] * TC
        holdings = newh
    return port, turn


def build_pure_equal_weight_returns(calendar, price_wide):
    """Quarterly-rebalanced EQUAL-weight (1/16) portfolio of the 16-name universe. No gate.
    Cross-check for build_pure_cap_weight_returns: cap-weighting lets giant banks (VCB) dominate
    and can understate true sector beta if smaller/higher-beta names (VCI, HAH, DBC) drive the
    BULL re-rating -- equal-weight removes that size skew."""
    ret = price_wide.pct_change()
    q_marks = pd.PeriodIndex(calendar, freq="Q")
    rebal_days = calendar.to_series().groupby(q_marks).min().values
    rebal_set = set(pd.Timestamp(d) for d in rebal_days)

    holdings = None
    port = pd.Series(0.0, index=calendar)
    turn = pd.Series(0.0, index=calendar)
    for i, d in enumerate(calendar):
        if d in rebal_set or holdings is None:
            px = price_wide.loc[d] if d in price_wide.index else None
            avail = [tk for tk in WL_TK if px is not None and np.isfinite(px.get(tk)) and px.get(tk) > 0]
            if avail:
                target = {tk: 1.0 / len(avail) for tk in avail}
                if holdings is not None and i > 0:
                    prev_val_tot = sum(holdings.values())
                    turn.loc[d] = sum(abs(target.get(tk, 0.0) - (holdings.get(tk, 0.0) / prev_val_tot if prev_val_tot > 0 else 0.0))
                                       for tk in set(list(target) + list(holdings))) / 2.0
                holdings = target
        if holdings is None or i == 0:
            continue
        r = ret.loc[d]
        num = 0.0; den = 0.0; newh = {}
        for tk, val in holdings.items():
            rt = r.get(tk); rt = rt if np.isfinite(rt) else 0.0
            nv = val * (1 + rt)
            num += val * rt; den += val
            newh[tk] = nv
        port.loc[d] = (num / den if den > 0 else 0.0) - turn.loc[d] * TC
        holdings = newh
    return port, turn


def gross_by_state(ret, state):
    df = pd.DataFrame({"ret": ret, "state": state}).dropna()
    out = []
    for s, g in df.groupby("state"):
        ann = g["ret"].mean() * 252 * 100
        out.append((int(s), len(g), ann))
    return sorted(out)


STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}


def main():
    print("Loading caches ...")
    price = load_prices()
    oshares = load_oshares()
    calendar = pd.DatetimeIndex(sorted(price["time"].unique()))
    price_wide = price.pivot_table(index="time", columns="ticker", values="Close").reindex(calendar)

    print("Building pure cap-weight (no gate) return series ...")
    pure_ret, turn = build_pure_cap_weight_returns(calendar, price_wide, oshares)
    ann_turn = turn.sum() / ((calendar[-1] - calendar[0]).days / 365.25)
    print(f"  annualized one-way turnover (pure cap-weight, quarterly rebal) = {ann_turn:.2f}x/yr")

    print("Building pure equal-weight (no gate) return series (robustness cross-check) ...")
    pure_eq_ret, turn_eq = build_pure_equal_weight_returns(calendar, price_wide)
    ann_turn_eq = turn_eq.sum() / ((calendar[-1] - calendar[0]).days / 365.25)
    print(f"  annualized one-way turnover (pure equal-weight, quarterly rebal) = {ann_turn_eq:.2f}x/yr")

    c = con()
    dt5g = c.execute(f"SELECT time, state FROM read_parquet('{CACHE}/vnindex_5state_dt5g_live.parquet') ORDER BY time").df()
    c.close()
    dt5g["time"] = pd.to_datetime(dt5g["time"])
    state = dt5g.set_index("time")["state"].reindex(calendar).ffill()

    conv = pd.read_csv(os.path.join(WORKDIR, "data", "converge_portfolio_backtest_nav.csv"))
    conv["date"] = pd.to_datetime(conv["date"])
    conv = conv.set_index("date").reindex(calendar)

    print("\nSelf-check: pure cap-weight weights sum to 1.0 by construction (always full-invested, "
          "no parking) -- 0 VND leak by construction (single loop, num/den normalized each day).")

    is_end = pd.Timestamp("2019-12-31")
    oos_start = pd.Timestamp("2020-01-01")
    windows = [("FULL", calendar), ("OOS_2020+", calendar[calendar >= oos_start])]

    rows = []
    for wname, idx in windows:
        pure_bystate = dict((s, (n, a)) for s, n, a in gross_by_state(pure_ret.reindex(idx), state.reindex(idx)))
        eq_bystate = dict((s, (n, a)) for s, n, a in gross_by_state(pure_eq_ret.reindex(idx), state.reindex(idx)))
        base_bystate = dict((s, (n, a)) for s, n, a in gross_by_state(conv["baseline_ret"].reindex(idx), state.reindex(idx)))
        conv_bystate = dict((s, (n, a)) for s, n, a in gross_by_state(conv["ConvergePort (equal-weight)"].reindex(idx), state.reindex(idx)))
        print(f"\n=== {wname} ===")
        print(f"  {'state':<8}{'N':>6}{'baseline':>11}{'pure16-cap':>12}{'pure16-eq':>11}{'ConvergePort':>14}{'excess_total':>14}{'excess_beta(cap)':>18}{'excess_beta(eq)':>17}{'excess_alpha(cap)':>19}")
        for s in sorted(set(pure_bystate) & set(base_bystate) & set(conv_bystate) & set(eq_bystate)):
            n_p, a_p = pure_bystate[s]
            n_e, a_e = eq_bystate[s]
            n_b, a_b = base_bystate[s]
            n_c, a_c = conv_bystate[s]
            excess_total = a_c - a_b
            excess_beta = a_p - a_b
            excess_beta_eq = a_e - a_b
            excess_alpha = a_c - a_p
            beta_share = (excess_beta / excess_total * 100) if abs(excess_total) > 1e-9 else float("nan")
            sn = STATE_NAMES.get(s, str(s))
            print(f"  {sn:<8}{n_b:>6}{a_b:>10.2f}%{a_p:>11.2f}%{a_e:>10.2f}%{a_c:>13.2f}%{excess_total:>13.2f}pp{excess_beta:>17.2f}pp{excess_beta_eq:>16.2f}pp{excess_alpha:>18.2f}pp")
            rows.append(dict(window=wname, state=sn, n=n_b, baseline=a_b, pure16_capweight=a_p,
                              pure16_eqweight=a_e, convergeport=a_c, excess_total=excess_total,
                              excess_beta_capw=excess_beta, excess_beta_eqw=excess_beta_eq,
                              excess_alpha_vs_capw=excess_alpha, beta_share_pct_capw=beta_share))

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
