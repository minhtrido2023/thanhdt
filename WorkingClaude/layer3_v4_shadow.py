# -*- coding: utf-8 -*-
"""Layer 3 v4 paper-trade shadow tracker.

Daily tracker for the asymmetric BUY-ATC / SELL-OPEN rule deployed 2026-05-17.
For each BA-system pick, computes the realized alpha vs T+1 Open baseline.

Modes (run from CLI):
  --update     : process all BA picks not yet logged; append to shadow CSV
  --backfill   : same as --update but from a start date (e.g. 2025-06-01)
  --report     : print full markdown report with statistical alarms
  --alert      : print one-line traffic-light status (Telegram-ready)

Rule under test (Layer 3 v4 HYBRID):
  - T1_TOP tickers (ADV >= 50B/day): place MOC at T+1 14:45 ATC
  - Non-T1_TOP: place LIMIT @ p_open at T+1 (filled if intraday touches),
                fallback to T+1 11:15 market
  - Baseline: T+1 09:00 OPEN/ATO market (the OLD rule)
  - Sell side: T+1 OPEN (canonical, no change) — not paper-traded here

Output: data/layer3_v4_shadow_log.csv
Alarms:
  GREEN  : rolling 30-entry alpha >= +0.50pp/trade AND p_one_tail < 0.10
  YELLOW : alpha 0 to +0.50pp OR n < 20 OR CI crosses zero
  RED    : alpha < 0 with p_one_tail < 0.10 (statistical breakage signal)
"""
import os, sys, argparse, glob
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import pickle

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

LOG_CSV = os.path.join(WORKDIR, "data", "layer3_v4_shadow_log.csv")
INTRADAY_PKL = os.path.join(WORKDIR, "data/intraday_full.pkl")
REPORT_MD = os.path.join(WORKDIR, "data", "layer3_v4_shadow_report.md")

POSITION_VND = 1.25e9          # per book leg @ 50B NAV, 2-book, 10-pos
FILL_CAP = 0.20                 # max 20% of bar volume
T1_TOP_ADV = 50e9               # ADV >= 50B/day = T1_TOP tier
T2_MID_ADV = 10e9
T3_LIQUID_ADV = 2e9
ROLLING_N = 30                  # alarm window
DECISION_ALPHA_PP = 0.50        # GREEN threshold (per-trade pp, derived from full sim)

LOG_COLS = [
    "signal_date", "t1_date", "ticker", "book", "play_type",
    "adv_vnd", "tier",
    "size_vnd", "fill_cap_vnd_atc", "fill_cap_vnd_t1115",
    "fill_feasible_atc", "fill_feasible_t1115",
    "p_open", "p_atc", "p_t1115", "p_applied", "applied_rule",
    "alpha_vs_open_pp",        # (p_open - p_applied) / p_open * 100
    "intraday_source", "logged_at"
]


def load_intraday():
    """Load cached intraday pickle (vnstock 15m bars × 335 tickers)."""
    if not os.path.exists(INTRADAY_PKL):
        return {}
    with open(INTRADAY_PKL, "rb") as f:
        return pickle.load(f)


def fetch_t1_intraday_for_ticker(ticker, t1_date_str):
    """Pull a single ticker's intraday on a specific date from vnstock if not in cache."""
    sys.path.insert(0, os.path.join(WORKDIR, "stockquery"))
    from stockquery_agent import StockQuery
    sq = StockQuery()
    sq.start_date = (pd.Timestamp(t1_date_str) - pd.Timedelta(days=3)).strftime("%Y-%m-%d")
    sq.end_date = (pd.Timestamp(t1_date_str) + pd.Timedelta(days=2)).strftime("%Y-%m-%d")
    try:
        df = sq.get_historical_symbol(ticker, interval="15m")
        if df is None or len(df) < 5:
            return None
        df["time"] = pd.to_datetime(df["time"])
        return df
    except Exception as e:
        print(f"  vnstock fetch failed {ticker} {t1_date_str}: {e}")
        return None


def session_prices(bars, t1_date):
    """Return dict of slot prices/vols for one ticker × one date.

    Returns None if no session bars on t1_date.
    """
    if bars is None or bars.empty:
        return None
    b = bars.copy()
    b["time"] = pd.to_datetime(b["time"])
    b["date_ts"] = b["time"].dt.normalize()
    b["hm"] = b["time"].dt.strftime("%H:%M")
    target = pd.Timestamp(t1_date).normalize()
    g = b[b["date_ts"] == target].sort_values("time").reset_index(drop=True)
    if len(g) < 3:
        return None
    # scale vnstock prices ×1000 to raw VND
    for c in ("open", "high", "low", "close"):
        g[c] = g[c].astype(float) * 1000.0
    g["vnd_traded"] = g["close"] * g["volume"].astype(float)

    def at(hm):
        row = g[g["hm"] == hm]
        if row.empty: return (np.nan, np.nan)
        return float(row.iloc[0]["close"]), float(row.iloc[0]["vnd_traded"])

    p_open, _   = at("09:15")
    if pd.isna(p_open):
        p_open = float(g.iloc[0]["close"])
    p_t1115, vol_t1115 = at("11:15")
    p_atc, vol_atc = at("14:45")
    if pd.isna(p_atc):
        # fallback last bar
        p_atc = float(g.iloc[-1]["close"])
        vol_atc = float(g.iloc[-1]["vnd_traded"])

    return {
        "p_open": p_open, "p_t1115": p_t1115, "p_atc": p_atc,
        "vol_t1115": vol_t1115, "vol_atc": vol_atc,
        "session_vnd": float(g["vnd_traded"].sum()),
        "day_low_pre_1115": float(g[g["hm"].isin(["09:15","09:30","09:45","10:00",
                                                    "10:15","10:30","10:45","11:00","11:15"])]["low"].min())
            if len(g[g["hm"].isin(["09:15","09:30","09:45","10:00","10:15","10:30","10:45","11:00","11:15"])]) else np.nan,
    }


def liq_tier(adv_vnd):
    if pd.isna(adv_vnd): return "T4_THIN"
    if adv_vnd >= T1_TOP_ADV: return "T1_TOP"
    if adv_vnd >= T2_MID_ADV: return "T2_MID"
    if adv_vnd >= T3_LIQUID_ADV: return "T3_LIQUID"
    return "T4_THIN"


def apply_v4_rule(tier, prices):
    """Return (applied_price, applied_rule_label) per the v4 HYBRID rule.

    Matches Phase 4b validated config:
      T1_TOP : MOC market BUY at 14:45 ATC (with liquidity gate fallback to OPEN)
      Others : MARKET BUY at 11:15 close price (with fallback to OPEN if no bar)

    Per Phase 5, sell-side stays at T+1 Open (canonical, not paper-traded here).
    """
    p_open = prices["p_open"]
    p_atc = prices["p_atc"]
    p_t1115 = prices["p_t1115"]
    vol_atc = prices["vol_atc"]
    vol_t1115 = prices["vol_t1115"]

    if tier == "T1_TOP":
        if pd.notna(vol_atc) and vol_atc * FILL_CAP >= POSITION_VND and pd.notna(p_atc):
            return p_atc, "ATC_full"
        else:
            return p_open, "ATC_unfilled_fallback_OPEN"
    else:
        # T1115 market BUY: fill at 11:15 close price (no limit logic, no oracle)
        if pd.notna(p_t1115):
            if pd.notna(vol_t1115) and vol_t1115 * FILL_CAP >= POSITION_VND:
                return p_t1115, "T1115_MKT_full"
            else:
                # T1115 bar volume insufficient; still use 11:15 as best-effort price
                # but flag as partial-feasibility (the trade may be split across bars in practice)
                return p_t1115, "T1115_MKT_thin_liquidity"
        else:
            return p_open, "T1115_unavailable_fallback_OPEN"


def find_next_trading_day(d_ts, vni_dates):
    """Next trading day strictly after d_ts."""
    d_ts = pd.Timestamp(d_ts).normalize()
    for vd in vni_dates:
        vd_ts = pd.Timestamp(vd).normalize()
        if vd_ts > d_ts:
            return vd_ts
    return None


def get_advs(intraday):
    """Compute per-ticker ADV from intraday cache."""
    adv = {}
    for tk, bars in intraday.items():
        if bars is None or bars.empty: continue
        b = bars.copy()
        b["time"] = pd.to_datetime(b["time"])
        b["date_ts"] = b["time"].dt.normalize()
        b["vnd"] = b["close"].astype(float) * 1000.0 * b["volume"].astype(float)
        sess = b.groupby("date_ts")["vnd"].sum()
        adv[tk] = float(sess.mean()) if len(sess) else 0.0
    return adv


def scan_ba_picks(start_date=None, include_sim_trades=True):
    """Yield BA-system entries from multiple sources:
      1. Live recommendations: ba_book_bal_*.csv and ba_book_vn30_*.csv (post-2025-06)
      2. Historical sim trades: data/v11_realistic_transactions.csv (Jun 2025+)

    Sim trades treated as "would-have-picked" entries — same signal-date semantics.
    Dedup happens later via (signal_date, ticker, book) key.
    """
    picks = []
    # Source 1: live recommendation CSVs
    pattern_bal = os.path.join(WORKDIR, "ba_book_bal_*.csv")
    pattern_vn30 = os.path.join(WORKDIR, "ba_book_vn30_*.csv")
    for fp in sorted(glob.glob(pattern_bal) + glob.glob(pattern_vn30)):
        book = "BAL" if "bal" in os.path.basename(fp) else "VN30"
        try:
            df = pd.read_csv(fp)
        except Exception as e:
            print(f"  skip {fp}: {e}")
            continue
        if "time" not in df.columns: continue
        df["time"] = pd.to_datetime(df["time"])
        for _, row in df.iterrows():
            sig = pd.Timestamp(row["time"]).normalize()
            if start_date and sig < pd.Timestamp(start_date):
                continue
            picks.append({
                "signal_date": sig,
                "ticker": row["ticker"],
                "book": book,
                "play_type": row.get("play_type", "?"),
                "liq_b_vnd_signal": float(row.get("liq_b_vnd", np.nan)) if "liq_b_vnd" in df.columns else np.nan,
                "source_file": os.path.basename(fp),
            })

    # Source 2: historical sim trades — treated as virtual picks
    if include_sim_trades:
        sim_csv = os.path.join(WORKDIR, "data", "v11_realistic_transactions.csv")
        if os.path.exists(sim_csv):
            df = pd.read_csv(sim_csv)
            df = df[df["action"] == "buy"]
            for _, row in df.iterrows():
                # The sim's `ymd` is when fill happened (T+1 Open). Signal date = ymd - 1 trading day.
                # For shadow tracking purposes, signal_date = ymd - 1 calendar day approx.
                # Simpler: use ymd directly as the T+1 (fill) date. We'll back out signal_date as ymd-1bday.
                fill_d = pd.Timestamp(row["ymd"]).normalize()
                # Signal day = previous business day
                sig = fill_d - pd.tseries.offsets.BDay(1)
                if start_date and sig < pd.Timestamp(start_date):
                    continue
                picks.append({
                    "signal_date": sig,
                    "ticker": row["ticker"],
                    "book": "SIM",
                    "play_type": "v11_sim",
                    "liq_b_vnd_signal": np.nan,
                    "source_file": "v11_realistic_transactions.csv",
                })
    return picks


def cmd_update(args):
    """Process BA picks not yet in log; append realized alpha."""
    intraday = load_intraday()
    print(f"  Loaded intraday cache: {len(intraday)} tickers")
    adv_map = get_advs(intraday)

    # Sorted trading-day index from intraday
    all_dates = set()
    for tk, bars in intraday.items():
        if bars is None or bars.empty: continue
        all_dates |= set(pd.to_datetime(bars["time"]).dt.normalize().unique())
    vni_dates = sorted(all_dates)

    picks = scan_ba_picks(start_date=args.from_date)
    print(f"  Found {len(picks)} BA picks (from {args.from_date or 'all'})")

    # Load existing log
    if os.path.exists(LOG_CSV):
        log = pd.read_csv(LOG_CSV)
        log["signal_date"] = pd.to_datetime(log["signal_date"])
        already = set(zip(log["signal_date"].dt.strftime("%Y-%m-%d"),
                          log["ticker"], log["book"]))
    else:
        log = pd.DataFrame(columns=LOG_COLS)
        already = set()
    print(f"  Already logged: {len(already)}")

    new_rows = []
    skipped_no_t1 = skipped_no_intraday = 0
    for pk in picks:
        key = (pk["signal_date"].strftime("%Y-%m-%d"), pk["ticker"], pk["book"])
        if key in already:
            continue
        t1 = find_next_trading_day(pk["signal_date"], vni_dates)
        if t1 is None:
            skipped_no_t1 += 1
            continue

        bars = intraday.get(pk["ticker"])
        sp = session_prices(bars, t1) if bars is not None else None
        intraday_source = "cache"
        if sp is None and args.fetch_missing:
            print(f"  fetching {pk['ticker']} @ {t1.date()}...")
            new_bars = fetch_t1_intraday_for_ticker(pk["ticker"], t1.strftime("%Y-%m-%d"))
            if new_bars is not None:
                sp = session_prices(new_bars, t1)
                intraday_source = "vnstock_live"

        if sp is None or pd.isna(sp["p_open"]):
            skipped_no_intraday += 1
            continue

        adv = adv_map.get(pk["ticker"], pk["liq_b_vnd_signal"]*1e9 if pd.notna(pk["liq_b_vnd_signal"]) else np.nan)
        tier = liq_tier(adv)
        applied_px, rule_label = apply_v4_rule(tier, sp)
        if pd.isna(applied_px) or applied_px <= 0:
            skipped_no_intraday += 1
            continue

        alpha_pp = (sp["p_open"] - applied_px) / sp["p_open"] * 100

        fill_atc = pd.notna(sp["vol_atc"]) and sp["vol_atc"]*FILL_CAP >= POSITION_VND
        fill_t1115 = pd.notna(sp["vol_t1115"]) and sp["vol_t1115"]*FILL_CAP >= POSITION_VND

        new_rows.append({
            "signal_date": pk["signal_date"].strftime("%Y-%m-%d"),
            "t1_date": t1.strftime("%Y-%m-%d"),
            "ticker": pk["ticker"],
            "book": pk["book"],
            "play_type": pk["play_type"],
            "adv_vnd": adv,
            "tier": tier,
            "size_vnd": POSITION_VND,
            "fill_cap_vnd_atc": sp["vol_atc"]*FILL_CAP if pd.notna(sp["vol_atc"]) else np.nan,
            "fill_cap_vnd_t1115": sp["vol_t1115"]*FILL_CAP if pd.notna(sp["vol_t1115"]) else np.nan,
            "fill_feasible_atc": fill_atc,
            "fill_feasible_t1115": fill_t1115,
            "p_open": sp["p_open"],
            "p_atc": sp["p_atc"],
            "p_t1115": sp["p_t1115"],
            "p_applied": applied_px,
            "applied_rule": rule_label,
            "alpha_vs_open_pp": alpha_pp,
            "intraday_source": intraday_source,
            "logged_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        out = pd.concat([log, new_df], ignore_index=True)
        out = out.sort_values(["signal_date", "ticker", "book"])
        out.to_csv(LOG_CSV, index=False)
        print(f"  Appended {len(new_rows)} new entries -> {LOG_CSV}")
    else:
        print("  No new entries.")
    print(f"  Skipped: no_t1={skipped_no_t1}, no_intraday={skipped_no_intraday}")
    print(f"  Total log size: {len(log)+len(new_rows)} entries")


def compute_alarm(alpha_series):
    """Traffic-light verdict for a Series of per-trade alpha (pp)."""
    a = pd.Series(alpha_series).dropna()
    n = len(a)
    if n == 0:
        return "NO_DATA", "no entries"
    mean = a.mean()
    sd = a.std()
    se = sd / np.sqrt(n) if n > 1 else np.nan
    # one-tail p-value for H0: mean <= 0 (we test alpha > 0)
    if n >= 2 and sd > 0:
        from math import erf, sqrt
        z = mean / se
        p_one = 0.5 * (1 - erf(z / sqrt(2)))
    else:
        p_one = np.nan
    # One-tail p-value for H0: mean >= 0 (we test alpha < 0 -- RED alarm)
    if n >= 2 and sd > 0:
        from math import erf, sqrt
        z_neg = -mean / se
        p_neg = 0.5 * (1 - erf(z_neg / sqrt(2)))
    else:
        p_neg = np.nan

    if n < 20:
        return "YELLOW", f"n={n} (need 20+ for confidence)"
    if not pd.isna(p_neg) and mean < 0 and p_neg < 0.10:
        return "RED", f"mean={mean:+.3f}pp, p(neg)={p_neg:.3f} -- RULE BREAKAGE SIGNAL"
    if mean >= DECISION_ALPHA_PP and not pd.isna(p_one) and p_one < 0.10:
        return "GREEN", f"mean={mean:+.3f}pp, p={p_one:.3f}, n={n}"
    if mean > 0:
        return "YELLOW", f"mean={mean:+.3f}pp positive but weak (need >={DECISION_ALPHA_PP}pp at p<0.10)"
    return "YELLOW", f"mean={mean:+.3f}pp, p(neg)={p_neg:.3f}"


def cmd_report(args):
    if not os.path.exists(LOG_CSV):
        print("No log yet. Run --update first.")
        return
    log = pd.read_csv(LOG_CSV)
    log["signal_date"] = pd.to_datetime(log["signal_date"])
    log["t1_date"] = pd.to_datetime(log["t1_date"])
    n = len(log)

    # Overall
    overall_status, overall_msg = compute_alarm(log["alpha_vs_open_pp"])
    # Rolling 30
    recent = log.sort_values("t1_date").tail(ROLLING_N)
    rolling_status, rolling_msg = compute_alarm(recent["alpha_vs_open_pp"])

    # Per tier
    tier_summary = log.groupby("tier")["alpha_vs_open_pp"].agg(
        n="count", mean="mean", std="std").round(3)

    # Per book
    book_summary = log.groupby("book")["alpha_vs_open_pp"].agg(
        n="count", mean="mean", std="std").round(3)

    # Per play_type
    play_summary = log.groupby("play_type")["alpha_vs_open_pp"].agg(
        n="count", mean="mean", std="std").round(3)

    # Fill feasibility
    fill_atc_pct = (log["fill_feasible_atc"]==True).mean() * 100 if n else 0
    fill_t1115_pct = (log["fill_feasible_t1115"]==True).mean() * 100 if n else 0

    # Recent 10 detail
    recent10 = log.sort_values("t1_date").tail(10)[["t1_date","ticker","book","tier","applied_rule","alpha_vs_open_pp"]]

    # Markdown report
    out = []
    out.append(f"# Layer 3 v4 Shadow Tracker Report")
    out.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    out.append(f"## Status")
    out.append(f"\n| Window | Status | Detail |")
    out.append(f"|---|---|---|")
    out.append(f"| Overall (n={n}) | **{overall_status}** | {overall_msg} |")
    out.append(f"| Rolling {ROLLING_N} (n={len(recent)}) | **{rolling_status}** | {rolling_msg} |")

    out.append(f"\n## Summary")
    out.append(f"- Total entries logged: **{n}**")
    out.append(f"- Date range: {log['signal_date'].min().date()} → {log['signal_date'].max().date()}")
    out.append(f"- Mean alpha vs T+1 Open: **{log['alpha_vs_open_pp'].mean():+.3f}pp** (sd {log['alpha_vs_open_pp'].std():.3f})")
    out.append(f"- ATC fill feasible: **{fill_atc_pct:.1f}%** | T1115 fill feasible: **{fill_t1115_pct:.1f}%**")
    out.append(f"- Win rate (alpha > 0): **{(log['alpha_vs_open_pp']>0).mean()*100:.1f}%**")

    out.append(f"\n## By Liquidity Tier")
    out.append(f"\n| Tier | n | mean alpha pp | std |")
    out.append(f"|---|---|---|---|")
    for t in ["T1_TOP","T2_MID","T3_LIQUID","T4_THIN"]:
        if t in tier_summary.index:
            r = tier_summary.loc[t]
            out.append(f"| {t} | {int(r['n'])} | {r['mean']:+.3f} | {r['std']:.3f} |")

    out.append(f"\n## By Book")
    out.append(f"\n| Book | n | mean alpha pp | std |")
    out.append(f"|---|---|---|---|")
    for b in book_summary.index:
        r = book_summary.loc[b]
        out.append(f"| {b} | {int(r['n'])} | {r['mean']:+.3f} | {r['std']:.3f} |")

    out.append(f"\n## By Play Type")
    out.append(f"\n| Play Type | n | mean alpha pp | std |")
    out.append(f"|---|---|---|---|")
    for p in play_summary.index:
        r = play_summary.loc[p]
        out.append(f"| {p} | {int(r['n'])} | {r['mean']:+.3f} | {r['std']:.3f} |")

    out.append(f"\n## Recent 10 entries")
    out.append(f"\n| T+1 date | Ticker | Book | Tier | Rule | Alpha (pp) |")
    out.append(f"|---|---|---|---|---|---|")
    for _, r in recent10.iterrows():
        out.append(f"| {r['t1_date'].date()} | {r['ticker']} | {r['book']} | {r['tier']} | {r['applied_rule']} | {r['alpha_vs_open_pp']:+.3f} |")

    out.append(f"\n## Decision rule")
    out.append(f"- **GREEN**: rolling {ROLLING_N} alpha >= +{DECISION_ALPHA_PP}pp AND p<0.10 → rule healthy, continue")
    out.append(f"- **YELLOW**: alpha 0 to +{DECISION_ALPHA_PP}pp or sample too small (n<20) → monitor")
    out.append(f"- **RED**: alpha < 0 with p<0.10 → **RULE BREAKAGE**, revert to T+1 Open canonical")

    text = "\n".join(out)
    print(text)
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\n[Saved {REPORT_MD}]")


def cmd_alert(args):
    """One-line traffic light for Telegram / morning summary."""
    if not os.path.exists(LOG_CSV):
        print("⚪ NO_DATA")
        return
    log = pd.read_csv(LOG_CSV)
    log["t1_date"] = pd.to_datetime(log["t1_date"])
    recent = log.sort_values("t1_date").tail(ROLLING_N)
    status, msg = compute_alarm(recent["alpha_vs_open_pp"])
    icon = {"GREEN":"🟢", "YELLOW":"🟡", "RED":"🔴", "NO_DATA":"⚪"}.get(status, "?")
    print(f"{icon} Layer3-v4 shadow: {status} - {msg}")


def main():
    ap = argparse.ArgumentParser(description="Layer 3 v4 paper-trade shadow tracker")
    sub = ap.add_subparsers(dest="cmd")

    p_up = sub.add_parser("update", help="Process new BA picks and append to log")
    p_up.add_argument("--from-date", default=None,
                      help="YYYY-MM-DD; only process picks on or after this date")
    p_up.add_argument("--fetch-missing", action="store_true",
                      help="Fetch missing intraday from vnstock live (slow)")

    p_bf = sub.add_parser("backfill", help="Same as update --from-date 2025-06-01")
    p_bf.add_argument("--from-date", default="2025-06-01")
    p_bf.add_argument("--fetch-missing", action="store_true")

    sub.add_parser("report", help="Print full markdown report + save to data/")
    sub.add_parser("alert", help="One-line traffic-light status")

    args = ap.parse_args()
    if args.cmd in ("update", "backfill"):
        cmd_update(args)
    elif args.cmd == "report":
        cmd_report(args)
    elif args.cmd == "alert":
        cmd_alert(args)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
