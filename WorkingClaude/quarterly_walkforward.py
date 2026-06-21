# -*- coding: utf-8 -*-
"""Quarterly walk-forward continuous validation for BA-system.

Run at the end of each quarter (or any time on demand) to verify that the
production system is still performing within expected bounds.

Outputs:
  - Recent-quarter NAV vs VNINDEX baseline
  - Trailing-1Y, trailing-3Y CAGR / Sharpe / MaxDD
  - Comparison to historical norms (full-period baseline)
  - Traffic-light status: GREEN / YELLOW / RED per metric

The historical norms are baked-in (validated 2014-2026, BA-system 50B v11
realistic T+1 Open execution — 2026-05-17 canonical):
  CAGR=18.18%, Sharpe=1.15, MaxDD=-16.0%, Calmar=1.10, Q-Win=80%

(Prior legacy T-close baseline was CAGR=17.15%/Sh=1.21/DD=-14.5% but contained
look-ahead bias and OVERSTATED returns by ~1.92pp CAGR — see ba_system_definition.md)

Usage:
  python quarterly_walkforward.py            # use latest available date
  python quarterly_walkforward.py 2026-03-31 # run snapshot ending YYYY-MM-DD
"""
import os
import sys
import io

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY, START_DATE
from test_round14_stability import SIGNAL_V10

# Historical baselines (BA-system v11 stack 50B realistic T+1 Open execution,
# validated 2014-2026 12yr — 2026-05-17 canonical)
# Realistic = signal at T-close → fill at T+1 Open (entry AND exit); no look-ahead.
# Prior legacy T-close baseline overstated CAGR by ~1.92pp.
BASELINE = {
    "cagr_pct": 18.18,
    "sharpe": 1.15,
    "max_dd_pct": -16.0,
    "calmar": 1.10,
    "q_win_pct": 80.0,
}

# Tolerances (drift bands)
GREEN_BAND = {  # within these → still within normal (do not change)
    "cagr_pct": 5.0,    # ±5pp
    "sharpe": 0.30,
    "max_dd_pct": 5.0,  # +5pp worse
    "calmar": 0.30,
    "q_win_pct": 15.0,  # ±15pp
}
YELLOW_BAND = {  # outside green but inside yellow → monitor
    "cagr_pct": 10.0,
    "sharpe": 0.50,
    "max_dd_pct": 10.0,
    "calmar": 0.50,
    "q_win_pct": 25.0,
}


def status(actual: float, baseline: float, metric: str) -> tuple:
    """Return (status_label, delta) for a single metric."""
    delta = actual - baseline
    if metric == "max_dd_pct":
        # Lower (more negative) = worse; we look at how much WORSE
        worse = baseline - actual  # positive = worse
        if worse <= GREEN_BAND[metric]:
            return ("🟢 GREEN", delta)
        if worse <= YELLOW_BAND[metric]:
            return ("🟡 YELLOW", delta)
        return ("🔴 RED", delta)
    # higher is better
    if abs(delta) <= GREEN_BAND[metric]:
        return ("🟢 GREEN", delta)
    if abs(delta) <= YELLOW_BAND[metric]:
        # if drift is positive → still GREEN-ish
        if delta > 0:
            return ("🟢 GREEN+", delta)
        return ("🟡 YELLOW", delta)
    if delta > 0:
        return ("🟢 GREEN++", delta)
    return ("🔴 RED", delta)


def run_simulation(end_date: str):
    """Run BA-system 50B simulate up to end_date and return aligned NAVs."""
    start_ts = pd.Timestamp(START_DATE)
    end_ts = pd.Timestamp(end_date)

    print(f"  Loading v10 signals up to {end_date}…")
    sig = bq(SIGNAL_V10.format(start=START_DATE, end=end_date))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"    {len(sig):,} signal rows")
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

    vni = bq(VNI_QUERY.format(start=START_DATE, end=end_date))
    vni["time"] = pd.to_datetime(vni["time"])
    vni_dates = sorted(vni["time"].unique())
    vni_close = vni.set_index("time")["Close"]

    sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
    top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

    TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
    LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
                "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    print("  Simulating BAL+Fin/RE-max-4 (50B)…")
    nav_bal, trades_bal = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    print("  Simulating VN30_BAL (50B)…")
    sig_vn30 = sig[sig["ticker"].isin(top30)]
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    ba_nav.name = "ba_nav"

    return ba_nav, vni_close, trades_bal


def metrics_window(nav: pd.Series, start: pd.Timestamp, end: pd.Timestamp,
                   label: str = ""):
    sub = nav[(nav.index >= start) & (nav.index <= end)]
    if len(sub) < 30:
        return {"label": label, "n": len(sub), "cagr_pct": np.nan,
                "sharpe": np.nan, "max_dd_pct": np.nan, "calmar": np.nan}
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    rm = sub.cummax()
    dd = (sub - rm) / rm
    mdd = dd.min()
    cal = cagr / abs(mdd) if mdd < 0 else 0
    return {"label": label, "n": len(sub),
            "cagr_pct": cagr * 100, "sharpe": sharpe,
            "max_dd_pct": mdd * 100, "calmar": cal,
            "wealth_x": sub.iloc[-1] / sub.iloc[0]}


def quarterly_returns(nav: pd.Series) -> pd.DataFrame:
    """Compute per-quarter returns. Win = quarter with positive return."""
    q = nav.resample("QE").last().pct_change().dropna() * 100
    q.name = "ret_pct"
    out = q.to_frame()
    out["win"] = out["ret_pct"] > 0
    return out


def main():
    end_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if end_arg is None:
        latest_q = bq("SELECT MAX(t.time) AS d FROM tav2_bq.ticker AS t WHERE t.D_RSI IS NOT NULL")
        end_date = str(latest_q["d"].iloc[0])
    else:
        end_date = end_arg

    print("=" * 88)
    print(f"  BA-SYSTEM QUARTERLY WALK-FORWARD VALIDATION — snapshot at {end_date}")
    print("=" * 88)

    print("\n[1/3] Running BA-system simulation through snapshot…")
    ba_nav, vni_close, trades = run_simulation(end_date)
    print(f"      NAV span: {ba_nav.index[0].date()} → {ba_nav.index[-1].date()} "
          f"({len(ba_nav)} sessions)")

    end_ts = ba_nav.index[-1]
    start_ts = ba_nav.index[0]

    print("\n[2/3] Computing metrics per window…")
    windows = [
        ("Latest Q (3M)",   end_ts - pd.Timedelta(days=92), end_ts),
        ("Trailing 1Y",     end_ts - pd.Timedelta(days=365), end_ts),
        ("Trailing 3Y",     end_ts - pd.Timedelta(days=3*365), end_ts),
        ("Trailing 5Y",     end_ts - pd.Timedelta(days=5*365), end_ts),
        ("Full history",    start_ts, end_ts),
    ]
    win_metrics = []
    for label, ws, we in windows:
        m_ba = metrics_window(ba_nav, ws, we, label)
        # VNINDEX baseline same window
        vni_window = vni_close[(vni_close.index >= ws) & (vni_close.index <= we)]
        if len(vni_window) >= 30:
            vni_norm = vni_window / vni_window.iloc[0]
            m_vni = metrics_window(vni_norm, vni_norm.index[0], vni_norm.index[-1],
                                    label + " (VNI)")
        else:
            m_vni = {"cagr_pct": np.nan, "sharpe": np.nan, "max_dd_pct": np.nan, "calmar": np.nan}
        m_ba["vni_cagr_pct"] = m_vni["cagr_pct"]
        m_ba["vni_sharpe"] = m_vni["sharpe"]
        m_ba["alpha_pct"] = m_ba["cagr_pct"] - m_vni["cagr_pct"] if not pd.isna(m_vni["cagr_pct"]) else np.nan
        win_metrics.append(m_ba)

    # Quarterly win rate (full history & trailing 3Y)
    qrets_full = quarterly_returns(ba_nav)
    q_win_full = qrets_full["win"].mean() * 100 if len(qrets_full) else np.nan
    qrets_3y = qrets_full[qrets_full.index >= end_ts - pd.Timedelta(days=3*365)]
    q_win_3y = qrets_3y["win"].mean() * 100 if len(qrets_3y) else np.nan

    print("\n[3/3] Status check…")
    print()
    print(f"  {'Window':<18} {'n':>5} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} {'Calmar':>7} "
          f"{'vs VNI':>9} {'Wealth':>8}")
    print(f"  {'-'*18} {'-'*5} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*9} {'-'*8}")
    for m_ba in win_metrics:
        print(f"  {m_ba['label']:<18} {m_ba['n']:>5} "
              f"{m_ba['cagr_pct']:>+7.2f}% {m_ba['sharpe']:>+7.2f} "
              f"{m_ba['max_dd_pct']:>+7.1f}% {m_ba['calmar']:>+7.2f} "
              f"{m_ba['alpha_pct']:>+7.2f}pp {m_ba.get('wealth_x', 1):>+7.2f}×")

    # ── Status against baseline (use Trailing 3Y as reference) ──────────
    print(f"\n{'═' * 88}")
    print(f"  STATUS vs HISTORICAL BASELINE (realistic T+1 Open, v11 stack: "
          f"CAGR={BASELINE['cagr_pct']:.2f}%, Sharpe={BASELINE['sharpe']:.2f}, "
          f"DD={BASELINE['max_dd_pct']:.1f}%, Calmar={BASELINE['calmar']:.2f}, "
          f"QWin={BASELINE['q_win_pct']:.1f}%)")
    print(f"{'═' * 88}")

    # Use trailing 3Y as the most relevant comparison
    t3y = next((m for m in win_metrics if m["label"] == "Trailing 3Y"), None)
    if t3y and not pd.isna(t3y["cagr_pct"]):
        print(f"\n  Reference: Trailing 3Y window\n")
        for metric, label in [("cagr_pct", "CAGR"), ("sharpe", "Sharpe"),
                              ("max_dd_pct", "MaxDD"), ("calmar", "Calmar")]:
            actual = t3y[metric]
            base = BASELINE[metric]
            stat, delta = status(actual, base, metric)
            unit = "%" if metric in ("cagr_pct", "max_dd_pct") else ""
            unit_d = "pp" if metric in ("cagr_pct", "max_dd_pct") else ""
            print(f"  {label:<10} actual={actual:>+7.2f}{unit}  baseline={base:>+7.2f}{unit}  "
                  f"Δ={delta:>+6.2f}{unit_d}  → {stat}")

        # Q-win rate
        if not pd.isna(q_win_3y):
            stat, delta = status(q_win_3y, BASELINE["q_win_pct"], "q_win_pct")
            print(f"  {'Q-Win':<10} actual={q_win_3y:>+7.1f}%   baseline={BASELINE['q_win_pct']:>+7.1f}%   "
                  f"Δ={delta:>+6.1f}pp  → {stat}")

    # ── Latest 8 quarters detailed ──────────────────────────────────────
    print(f"\n{'═' * 88}")
    print(f"  RECENT 8 QUARTERS (BA-system vs VNINDEX baseline)")
    print(f"{'═' * 88}")
    last_q = qrets_full.tail(8)
    if not last_q.empty:
        # Compute VNI quarterly
        vni_q = vni_close.resample("QE").last().pct_change().dropna() * 100
        vni_q_aligned = vni_q.reindex(last_q.index)
        print(f"\n  {'Quarter':<10} {'BA ret':>10} {'VNI ret':>10} {'Δ alpha':>10}")
        print("  " + "-" * 46)
        for ts, row in last_q.iterrows():
            ba_r = row["ret_pct"]
            vni_r = vni_q_aligned.loc[ts] if ts in vni_q_aligned.index else np.nan
            alpha = ba_r - vni_r if not pd.isna(vni_r) else np.nan
            ql = f"{ts.year}-Q{(ts.month-1)//3+1}"
            print(f"  {ql:<10}  {ba_r:>+9.2f}% {vni_r:>+9.2f}% {alpha:>+9.2f}pp")

    # ── Save report ─────────────────────────────────────────────────────
    out_path = os.path.join(WORKDIR, f"qwf_report_{end_date}.csv")
    pd.DataFrame(win_metrics).to_csv(out_path, index=False)
    print(f"\n  Saved snapshot: {out_path}")

    nav_path = os.path.join(WORKDIR, f"qwf_ba_nav_{end_date}.csv")
    ba_nav.to_csv(nav_path, header=True)
    print(f"  Saved NAV trace: {nav_path}")

    # Append to long-term tracking log
    track_path = os.path.join(WORKDIR, "data/qwf_tracking_log.csv")
    track_row = {
        "snapshot_date": end_date,
        "trailing_3y_cagr_pct": t3y["cagr_pct"] if t3y else np.nan,
        "trailing_3y_sharpe": t3y["sharpe"] if t3y else np.nan,
        "trailing_3y_dd_pct": t3y["max_dd_pct"] if t3y else np.nan,
        "trailing_3y_calmar": t3y["calmar"] if t3y else np.nan,
        "q_win_3y_pct": q_win_3y,
        "trailing_1y_cagr_pct": next((m["cagr_pct"] for m in win_metrics
                                      if m["label"] == "Trailing 1Y"), np.nan),
        "latest_q_ret_pct": last_q["ret_pct"].iloc[-1] if len(last_q) else np.nan,
    }
    if os.path.exists(track_path):
        existing = pd.read_csv(track_path)
        existing = existing[existing["snapshot_date"] != end_date]
        out = pd.concat([existing, pd.DataFrame([track_row])], ignore_index=True)
    else:
        out = pd.DataFrame([track_row])
    out = out.sort_values("snapshot_date").reset_index(drop=True)
    out.to_csv(track_path, index=False)
    print(f"  Tracking log: {track_path}  ({len(out)} snapshots)")


if __name__ == "__main__":
    main()
