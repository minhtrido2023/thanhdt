"""Layer 3 forward paper-trade tracker (30-60 day rolling validation).

Three modes:
  log    — capture today's Layer 3 verdicts on the BA-system watchlist
            (run after 14:50 each session)
  update — backfill realized T+0 / T+1 / T+5 / T+20 returns for past signals
            (run periodically, e.g. weekly)
  stats  — analyze hit-rate + average return per verdict bucket

Persistent store: layer3_paper_trade_log.csv (append-only).
Each row: log_date, ticker, verdict, score, factor breakdown, then later filled:
  px_T0_close, px_T1_open, px_T1_close, px_T5_close, px_T20_close,
  ret_T0d, ret_T1d, ret_T5d, ret_T20d.

Usage:
  python layer3_paper_trade.py log [YYYY-MM-DD]    # capture today's verdicts
  python layer3_paper_trade.py update              # fill outcomes for past rows
  python layer3_paper_trade.py stats               # compute aggregate stats
"""
import os
import sys
import io
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
LOG_PATH = os.path.join(WORKDIR, "layer3_paper_trade_log.csv")
sys.path.insert(0, WORKDIR)


def _load_log() -> pd.DataFrame:
    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
        df["log_date"] = pd.to_datetime(df["log_date"]).dt.date
        return df
    return pd.DataFrame()


def _save_log(df: pd.DataFrame):
    df.to_csv(LOG_PATH, index=False)


def cmd_log(target_date: str = None):
    """Capture Layer 3 verdicts on today's BA-core watchlist."""
    from layer3_intraday_timing import analyze_ticker_intraday
    sys.path.insert(0, os.path.join(WORKDIR, "stockquery"))
    from stockquery_agent import StockQuery

    target = target_date or datetime.now().strftime("%Y-%m-%d")
    print(f"[LOG] Layer 3 paper-trade capture for {target}")

    # 1) Get BA-core watchlist tickers from latest holistic CSV
    import glob
    files = sorted(glob.glob(os.path.join(WORKDIR, f"holistic_{target}.csv")))
    if not files:
        files = sorted(glob.glob(os.path.join(WORKDIR, "holistic_*.csv")))
        if not files:
            print("  No holistic_*.csv. Run recommend_holistic.py first.")
            return
        latest = files[-1]
        print(f"  Using latest holistic file: {os.path.basename(latest)}")
    else:
        latest = files[-1]

    df_h = pd.read_csv(latest)
    BA_CORE = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
    INFO_TIERS = ["S_PRO", "MOMENTUM_QUALITY", "MOMENTUM_A", "COMPOUNDER_BUY"]
    pick = df_h[df_h["play_type"].isin(BA_CORE + INFO_TIERS)].copy()
    if pick.empty:
        print("  No BA-core/info tier candidates today (BEAR or no setup).")
        # Still capture an empty marker row for tracking
        return
    print(f"  {len(pick)} candidate tickers: "
          f"{', '.join(pick['ticker'].head(15).tolist())}…")

    # 2) Run Layer 3 intraday on each ticker
    sq = StockQuery()
    rows = []
    for _, r in pick.iterrows():
        tk = r["ticker"]
        play_type = r["play_type"]
        ta_score = r["ta_score"]
        fa_tier = r.get("fa_tier", "")
        result = analyze_ticker_intraday(sq, tk, target_date=target)
        if result.get("verdict") in ("ERROR", "NO_DATA"):
            print(f"    {tk}: skipped ({result.get('reason', '')})")
            continue
        rows.append({
            "log_date": target,
            "ticker": tk,
            "play_type": play_type,
            "ta_score": ta_score,
            "fa_tier": fa_tier,
            "verdict": result.get("verdict"),
            "score": result.get("score"),
            "reason": result.get("reason"),
            "px_T0_close": result.get("close"),
            "vwap": result.get("vwap"),
            "vs_vwap_pct": result.get("vs_vwap_pct"),
            "rsi15m": result.get("rsi15m"),
            "macd_hist": result.get("macd_hist"),
            "pos_in_range": result.get("pos_in_range"),
            "trend_1h_pct": result.get("trend_1h_pct"),
            "vol_burst_x": result.get("vol_burst_x"),
            "day_chg_pct": result.get("day_chg_pct"),
            # outcomes filled by update():
            "px_T1_open": np.nan, "px_T1_close": np.nan,
            "px_T5_close": np.nan, "px_T20_close": np.nan,
            "ret_T1d_pct": np.nan, "ret_T5d_pct": np.nan,
            "ret_T20d_pct": np.nan,
        })
        print(f"    {tk:6} {play_type:20} verdict={result.get('verdict'):10} "
              f"score={result.get('score'):>3}  "
              f"@{result.get('close')}")

    if not rows:
        print("  No valid Layer 3 rows captured.")
        return

    new_df = pd.DataFrame(rows)
    log = _load_log()
    # Drop existing rows for the same (date, ticker) — overwrite if rerun
    if not log.empty:
        log = log[~((log["log_date"].astype(str) == target)
                    & (log["ticker"].isin(new_df["ticker"])))]
    out = pd.concat([log, new_df], ignore_index=True)
    _save_log(out)
    cnt = new_df["verdict"].value_counts().to_dict()
    print(f"\n  Logged {len(rows)} rows. Verdict distribution: {cnt}")
    print(f"  Saved → {LOG_PATH}")


def cmd_update():
    """Fill T+1, T+5, T+20 prices/returns for log rows missing outcomes."""
    log = _load_log()
    if log.empty:
        print("[UPDATE] Empty log — nothing to update.")
        return

    print(f"[UPDATE] Loaded {len(log)} log rows. Filling outcomes…")

    # Find rows still missing T+20 (the longest horizon)
    today = datetime.now().date()
    pending = log[log["ret_T20d_pct"].isna()].copy()
    if pending.empty:
        print("  All rows have full outcomes. Nothing to do.")
        return
    print(f"  {len(pending)} rows pending updates")

    # Get unique (ticker, log_date) pairs and figure out which need refresh
    # We need T+1 close, T+5 close, T+20 close from BigQuery `ticker` table
    tickers = sorted(pending["ticker"].unique())
    date_min = pending["log_date"].min()
    # Need future window 25 trading days from min log_date
    fetch_end = today

    sql = f"""
    SELECT t.ticker, t.time, t.Close
    FROM tav2_bq.ticker AS t
    WHERE t.ticker IN ({','.join(repr(tk) for tk in tickers)})
      AND t.time BETWEEN DATE '{date_min}' AND DATE '{fetch_end}'
    ORDER BY t.ticker, t.time
    """
    from recommend_holistic import bq
    px_df = bq(sql)
    px_df["time"] = pd.to_datetime(px_df["time"]).dt.date
    px_idx = {(r["ticker"], r["time"]): r["Close"] for _, r in px_df.iterrows()}

    # Build per-ticker sorted date lists for relative-day lookup
    by_ticker = {}
    for tk, g in px_df.groupby("ticker"):
        by_ticker[tk] = sorted(g["time"].tolist())

    def shift_n(tk, dt0, n):
        dates = by_ticker.get(tk, [])
        if dt0 not in dates:
            # find first date > dt0
            future = [d for d in dates if d > dt0]
            if not future:
                return None, None
            dt0 = future[0]
            n -= 0  # counted
        try:
            i = dates.index(dt0)
        except ValueError:
            return None, None
        if i + n >= len(dates):
            return None, None
        d_target = dates[i + n]
        return d_target, px_idx.get((tk, d_target))

    n_filled = 0
    for idx, r in pending.iterrows():
        tk = r["ticker"]
        d0 = r["log_date"]
        # T+1 close (next trading day)
        d1, p1 = shift_n(tk, d0, 1)
        # T+5 close
        d5, p5 = shift_n(tk, d0, 5)
        # T+20 close
        d20, p20 = shift_n(tk, d0, 20)
        p0 = r["px_T0_close"]
        if p0 and p0 > 0:
            if p1: log.at[idx, "px_T1_close"] = p1
            if p5: log.at[idx, "px_T5_close"] = p5
            if p20: log.at[idx, "px_T20_close"] = p20
            if p1: log.at[idx, "ret_T1d_pct"] = (p1 / p0 - 1) * 100
            if p5: log.at[idx, "ret_T5d_pct"] = (p5 / p0 - 1) * 100
            if p20: log.at[idx, "ret_T20d_pct"] = (p20 / p0 - 1) * 100
            if p1 or p5 or p20:
                n_filled += 1

    _save_log(log)
    print(f"  Filled outcomes for {n_filled} rows")
    fully_done = log[log["ret_T20d_pct"].notna()].shape[0]
    print(f"  Total rows with full T+20 outcome: {fully_done} / {len(log)}")


def cmd_stats(min_horizon: str = "T1"):
    """Compute hit rate + avg return by verdict bucket."""
    log = _load_log()
    if log.empty:
        print("[STATS] Empty log.")
        return

    # Drop rows with no outcome yet
    col = f"ret_{min_horizon}d_pct"
    if col not in log.columns:
        print(f"  Unknown horizon {min_horizon}. Use T1 / T5 / T20.")
        return
    df = log[log[col].notna()].copy()
    if df.empty:
        print(f"  No rows with realized {col} yet — wait for outcomes to land.")
        return

    print(f"[STATS] Layer 3 paper-trade — {len(df)} samples with realized {col}")
    print(f"        Date range: {df['log_date'].min()} → {df['log_date'].max()}")
    print(f"\n{'═' * 80}")
    print(f"  HIT-RATE & AVG RETURN BY VERDICT BUCKET")
    print(f"{'═' * 80}")
    print(f"\n  {'Verdict':<12} {'n':>5} {'avg T+1':>10} {'avg T+5':>10} {'avg T+20':>10} "
          f"{'win T+1':>10} {'win T+5':>10} {'win T+20':>10}")
    print("  " + "-" * 90)

    for v in ["GO_STRONG", "GO", "WAIT", "AVOID"]:
        sub = df[df["verdict"] == v]
        if sub.empty:
            continue
        n = len(sub)
        a1 = sub["ret_T1d_pct"].mean()
        a5 = sub["ret_T5d_pct"].mean()
        a20 = sub["ret_T20d_pct"].mean()
        w1 = (sub["ret_T1d_pct"] > 0).mean() * 100 if sub["ret_T1d_pct"].notna().any() else np.nan
        w5 = (sub["ret_T5d_pct"] > 0).mean() * 100 if sub["ret_T5d_pct"].notna().any() else np.nan
        w20 = (sub["ret_T20d_pct"] > 0).mean() * 100 if sub["ret_T20d_pct"].notna().any() else np.nan
        print(f"  {v:<12} {n:>5} {a1:>+9.2f}% {a5:>+9.2f}% {a20:>+9.2f}% "
              f"{w1:>+9.1f}% {w5:>+9.1f}% {w20:>+9.1f}%")

    # Also break down by play_type × verdict
    print(f"\n  AVG T+5 RETURN BY (PLAY_TYPE × VERDICT)")
    print("  " + "-" * 60)
    pivot = df.pivot_table(index="play_type", columns="verdict",
                           values="ret_T5d_pct", aggfunc="mean")
    if not pivot.empty:
        print(pivot.round(2).fillna(0).to_string())
    counts = df.pivot_table(index="play_type", columns="verdict",
                            values="ret_T5d_pct", aggfunc="count")
    if not counts.empty:
        print("\n  Sample counts:")
        print(counts.fillna(0).astype(int).to_string())

    # Score correlation with outcomes
    print(f"\n  SCORE-RETURN CORRELATION")
    print("  " + "-" * 60)
    if df["score"].notna().any():
        for h in ["T1", "T5", "T20"]:
            c = df[["score", f"ret_{h}d_pct"]].dropna()
            if len(c) >= 10:
                corr = c.corr().iloc[0, 1]
                print(f"  corr(score, ret_{h}d) = {corr:+.3f}  (n={len(c)})")

    # Most recent 30 days summary
    cutoff = pd.Timestamp.now().date() - timedelta(days=30)
    recent = df[pd.to_datetime(df["log_date"]).dt.date >= cutoff]
    if not recent.empty:
        print(f"\n  RECENT 30 DAYS ONLY ({len(recent)} samples)")
        print(f"  GO_STRONG count: {(recent['verdict']=='GO_STRONG').sum()}")
        print(f"  GO count:        {(recent['verdict']=='GO').sum()}")
        if "ret_T5d_pct" in recent.columns and recent["ret_T5d_pct"].notna().any():
            print(f"  avg T+5 ret all: {recent['ret_T5d_pct'].mean():+.2f}%")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1].lower()
    if cmd == "log":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_log(target)
    elif cmd == "update":
        cmd_update()
    elif cmd == "stats":
        horizon = sys.argv[2] if len(sys.argv) > 2 else "T1"
        cmd_stats(horizon)
    else:
        print(f"Unknown mode: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
