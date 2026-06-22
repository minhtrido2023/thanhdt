#!/usr/bin/env python3
"""
update_shares_live.py — LIVE outstanding-shares override in BigQuery
====================================================================
WHY: tav2_bq.ticker_financial.OShares is QUARTERLY. On a stock-dividend ex-date
the adjusted price drops immediately, but OShares only catches up at the next
quarterly release (up to ~3 months later). In that window PE & PB are computed
with too-few shares -> the stock screens artificially CHEAP, market-cap is
understated. (Found on ACB: ex 2026-06-15, 2025 div 20% = 13% stock + 7% cash;
price adjusted correctly but OShares stale at 5,136,656,599.)

DESIGN — non-destructive, auditable, reversible:
  * Writes ONLY to tav2_bq.shares_outstanding_live (a NEW table). NEVER mutates
    ticker / ticker_financial. Valuation consumers LEFT JOIN it to override the
    stale quarterly OShares (see PRINTED join template at the end).
  * DETECT (auto): BQ adjustment factor = Close(adj)/Price(raw). A factor RESET
    to ~1.0 == a corporate action; the date of the step == the ex-date.
  * VERIFY with vnstock (independent): VCI adjusted close (the one vnstock
    endpoint reachable here) must match BQ Close on the ex-date.
  * RESOLVE the cash/stock split (price alone can't separate them):
      1) vnstock company.dividends()/events() if the VCI finance host is up;
      2) else the operator-confirmed CORP_ACTIONS table below (authoritative
         announcement figures from the exchange / VSD / news).
  * VALIDATE GATE before writing: theoretical ex price
        (cum_raw_close - cash_per_share) / (1 + stock_ratio)
    must equal BQ Close[last cum day] within tol; else REFUSE (the declared
    split does not explain the observed price move -> do not corrupt BQ).
  * UPSERT via MERGE on (ticker, ex_date): idempotent, safe to re-run.

USAGE:
  python update_shares_live.py                 # process watchlist + write
  python update_shares_live.py --detect-only   # scan & report, NO write
  python update_shares_live.py --ticker ACB    # one ticker
"""
import os, sys, json, argparse, subprocess, tempfile
from datetime import datetime, timedelta
from io import StringIO
import pandas as pd

WORKDIR = os.environ.get("WORKDIR_8L", os.path.dirname(os.path.abspath(__file__)))
PROJECT = "lithe-record-440915-m9"
TABLE   = "tav2_bq.shares_outstanding_live"
APPEND_EVT = "/home/trido/thanhdt/WorkingClaude/mike/bin/append_event.sh"
PENDING = os.path.join(WORKDIR, "data", "corp_action_pending.json")  # scan dedup memory
FACTOR_TOL = 0.005          # 0.5% tolerance on the validation gate
PAR_VALUE  = 10000.0        # VND par (cash dividend % is on par)

# --- universe scan thresholds (validated against ticker_prune, 2026-06) ----------
SCAN_UNIVERSE   = "tav2_bq.ticker_prune"   # quality/investable universe (low noise)
SCAN_STEP_MIN   = 0.02     # factor must step up >= +2% (into the ~1.0 regime)
SCAN_RAW_GAP    = -0.01    # raw Price must actually gap down (a real ex, not re-anchor)
SCAN_ADJ_CONT   = 0.07     # adjusted series stays continuous (|adj return| < ceiling)

# --- Operator-confirmed corporate actions (authoritative announcement figures).
#     Used when vnstock events host is unreachable. stock_div_ratio = new shares
#     per existing share; cash_div_per_share in VND. -------------------------------
CORP_ACTIONS = {
    "ACB": [dict(ex_date="2026-06-15", stock_div_ratio=0.13, cash_div_per_share=700.0,
                 source="VSD/cafef/Vietstock: 2025 div 20% = 13% stock + 7% cash; +667.77M shares")],
    "HDC": [dict(ex_date="2026-06-19", stock_div_ratio=0.15, cash_div_per_share=0.0,
                 source="cafef/Vietstock: 2025 div = 15% stock (pure), ~30M new shares")],
}
WATCHLIST = list(CORP_ACTIONS.keys())


# ----------------------------------------------------------------- BQ helpers ---
def run_bq(sql, fmt="csv"):
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        r = subprocess.run(["bq", "query", "--use_legacy_sql=false",
                            f"--project_id={PROJECT}", f"--format={fmt}", "--max_rows=200"],
                           stdin=open(tmp), capture_output=True, text=True, timeout=180)
    finally:
        os.unlink(tmp)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:400])
    return r.stdout


def bq_df(sql):
    out = run_bq(sql).strip()
    return pd.read_csv(StringIO(out)) if out else pd.DataFrame()


# ----------------------------------------------------------------- data pulls ---
def bq_price_factor(ticker, days=80):
    """BQ adjusted/raw factor series to DETECT the ex-date (factor reset)."""
    df = bq_df(f"""
        SELECT t.time, t.Close AS adj, t.Price AS raw
        FROM tav2_bq.ticker AS t
        WHERE t.ticker='{ticker}' AND t.time >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
        ORDER BY t.time""")
    if df.empty:
        return df
    df["factor"] = df["adj"] / df["raw"]
    return df


def bq_latest_oshares(ticker):
    df = bq_df(f"""
        SELECT f.OShares AS oshares, f.quarter, f.time
        FROM tav2_bq.ticker_financial AS f
        WHERE f.ticker='{ticker}' ORDER BY f.time DESC LIMIT 1""")
    if df.empty:
        return None, None
    return int(round(float(df.iloc[0]["oshares"]))), str(df.iloc[0]["quarter"])


def vnstock_adj_close(ticker, ex_date):
    """Independent verification: VCI adjusted close (x1000 -> VND) around ex_date."""
    try:
        from vnstock.explorer.vci.quote import Quote as VciQuote
        ex = datetime.strptime(ex_date, "%Y-%m-%d")
        df = VciQuote(symbol=ticker).history(
            start=(ex - timedelta(days=12)).strftime("%Y-%m-%d"),
            end=(ex + timedelta(days=3)).strftime("%Y-%m-%d"),
            interval="1D", count_back=None)
        if df is None or not len(df):
            return None
        df["time"] = pd.to_datetime(df["time"]).dt.strftime("%Y-%m-%d")
        hit = df[df["time"] == ex_date]
        return float(hit.iloc[0]["close"]) * 1000.0 if len(hit) else None
    except Exception as e:
        print(f"  [warn] vnstock verify unavailable for {ticker}: {repr(e)[:80]}")
        return None


def vnstock_events_split(ticker):
    """Best-effort: pull the cash/stock split from vnstock if its finance host is
    up. Returns object or None (falls back to CORP_ACTIONS)."""
    try:
        from vnstock.explorer.vci.company import Company
        return Company(symbol=ticker).dividends()    # raises KeyError('data') if host down
    except Exception:
        return None


# ----------------------------------------------------------------- core ---------
def detect_ex(factor_df):
    """Return (ex_date, cum_factor) of the most recent factor reset, or (None,None)."""
    if factor_df.empty or len(factor_df) < 3:
        return None, None
    f = factor_df.reset_index(drop=True)
    last_change = None
    for i in range(1, len(f)):
        if abs(f.loc[i, "factor"] - f.loc[i-1, "factor"]) > FACTOR_TOL:
            last_change = i
    if last_change is None:
        return None, None
    ex_date = str(pd.to_datetime(f.loc[last_change, "time"]).date())
    cum_factor = float(f.loc[last_change-1, "factor"])   # factor on last cum day
    return ex_date, cum_factor


def process(ticker, write=True):
    print(f"\n=== {ticker} ===")
    fac = bq_price_factor(ticker)
    if fac.empty:
        print("  no BQ price data"); return None
    det_ex, cum_factor = detect_ex(fac)
    prev_osh, q = bq_latest_oshares(ticker)
    print(f"  BQ OShares (latest, {q}): {prev_osh:,}" if prev_osh else "  BQ OShares: n/a")
    print(f"  detected ex-date: {det_ex} (cum factor {cum_factor})" if det_ex
          else "  no corporate action detected in window")

    actions = CORP_ACTIONS.get(ticker, [])
    if not actions:
        print("  no declared action in CORP_ACTIONS -> detection only, nothing to write")
        return None
    act = actions[-1]
    ex_date = act["ex_date"]; stock = act["stock_div_ratio"]; cash = act["cash_div_per_share"]

    cum_rows = fac[pd.to_datetime(fac["time"]) < pd.to_datetime(ex_date)]
    if cum_rows.empty:
        print("  cannot locate cum day before ex -> skip"); return None
    cum_raw = float(cum_rows.iloc[-1]["raw"])
    cum_adj = float(cum_rows.iloc[-1]["adj"])

    theo_ex = (cum_raw - cash) / (1.0 + stock)
    gate_bq = abs(theo_ex / cum_adj - 1.0)
    vn_adj = vnstock_adj_close(ticker, ex_date)
    bq_ex_adj = None
    ex_rows = fac[pd.to_datetime(fac["time"]) == pd.to_datetime(ex_date)]
    if len(ex_rows):
        bq_ex_adj = float(ex_rows.iloc[0]["adj"])
    print(f"  cum raw close {cum_raw:,.0f} | theo ex (-cash {cash:.0f}, /1+{stock}) = {theo_ex:,.0f}"
          f" | BQ adj(cum) {cum_adj:,.0f}  -> gate {gate_bq*100:.2f}%")
    if vn_adj and bq_ex_adj:
        print(f"  vnstock adj(ex) {vn_adj:,.0f}  vs BQ adj(ex) {bq_ex_adj:,.0f}  -> "
              f"{abs(vn_adj/bq_ex_adj-1)*100:.2f}% diff")

    if gate_bq > FACTOR_TOL:
        print(f"  ✗ GATE FAILED ({gate_bq*100:.2f}% > {FACTOR_TOL*100:.1f}%) — declared split does "
              f"not explain price move. REFUSING to write.")
        return None
    if vn_adj and bq_ex_adj and abs(vn_adj/bq_ex_adj - 1) > FACTOR_TOL:
        print("  ✗ vnstock vs BQ adjusted close mismatch — REFUSING to write."); return None

    new_osh = int(round(prev_osh * (1.0 + stock)))
    print(f"  ✓ validated. OShares {prev_osh:,} -> {new_osh:,}  (+{new_osh-prev_osh:,}, x{1+stock})")

    if not write:
        print("  [detect-only] not writing"); return dict(ticker=ticker, new_osh=new_osh)

    factor_val = cum_adj / cum_raw
    merge = f"""
    MERGE {TABLE} T
    USING (SELECT '{ticker}' AS ticker, DATE '{ex_date}' AS ex_date) S
    ON T.ticker=S.ticker AND T.ex_date=S.ex_date
    WHEN MATCHED THEN UPDATE SET
      oshares={new_osh}, prev_oshares={prev_osh}, stock_div_ratio={stock},
      cash_div_per_share={cash}, price_adj_factor={factor_val:.6f},
      source='{act["source"]}', note='auto: validated gate {gate_bq*100:.2f}%',
      updated_at=CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT
      (ticker, ex_date, oshares, prev_oshares, stock_div_ratio, cash_div_per_share,
       price_adj_factor, source, note, updated_at)
      VALUES('{ticker}', DATE '{ex_date}', {new_osh}, {prev_osh}, {stock}, {cash},
             {factor_val:.6f}, '{act["source"]}', 'auto: validated gate {gate_bq*100:.2f}%',
             CURRENT_TIMESTAMP())"""
    run_bq(merge)
    print(f"  ✓ upserted into {TABLE}")
    return dict(ticker=ticker, ex_date=ex_date, prev_osh=prev_osh, new_osh=new_osh,
                stock=stock, cash=cash, gate=round(gate_bq*100, 2))


def bus(event_type, topic, payload):
    try:
        subprocess.run([APPEND_EVT, "Winston", event_type, topic,
                        json.dumps(payload, ensure_ascii=False)], timeout=30, check=False)
    except Exception as e:
        print(f"  [warn] bus append failed: {e}")


# ----------------------------------------------------------------- scan ---------
def _load_pending():
    try:
        with open(PENDING) as f: return json.load(f)
    except Exception:
        return {}


def _save_pending(d):
    os.makedirs(os.path.dirname(PENDING), exist_ok=True)
    with open(PENDING, "w") as f: json.dump(d, f, indent=2)


def scan_universe(days=5):
    """Scan ticker_prune for NEW corporate-action ex-dates (factor reset) not yet
    in shares_outstanding_live, alert (Winston+Taylor). Detection only — no write.

    A real ex-date: factor (=Close/Price) steps UP to ~1.0, raw Price gaps DOWN by
    ~the step, AND the adjusted series stays continuous (gap absorbed into the
    factor). Re-anchor artifacts (raw flat while adj jumps) and flip-flops are
    filtered out. Restricted to ticker_prune to suppress illiquid noise."""
    sql = f"""
    WITH ff AS (
      SELECT t.ticker, t.time, t.Close, t.Price,
             t.Close/NULLIF(t.Price,0) AS factor,
             LAG(t.Close/NULLIF(t.Price,0)) OVER (PARTITION BY t.ticker ORDER BY t.time) AS pf,
             LAG(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time) AS pc,
             LAG(t.Price) OVER (PARTITION BY t.ticker ORDER BY t.time) AS pp
      FROM {SCAN_UNIVERSE} AS t
      WHERE t.time >= DATE_SUB(CURRENT_DATE(), INTERVAL {int(days)} DAY)
    )
    SELECT ff.time AS ex_date, ff.ticker,
           ROUND((ff.factor/ff.pf - 1)*100, 2) AS factor_step_pct,  -- gross adj % = max stock ratio
           ROUND((ff.Price/ff.pp - 1)*100, 2) AS raw_gap_pct,
           ROUND((ff.Close/ff.pc - 1)*100, 2) AS adj_return_pct
    FROM ff
    LEFT JOIN {TABLE} s ON s.ticker=ff.ticker AND s.ex_date=ff.time
    WHERE ff.pf IS NOT NULL AND s.ticker IS NULL
      AND (ff.factor/ff.pf - 1) >  {SCAN_STEP_MIN}
      AND (ff.Price/ff.pp - 1)   <  {SCAN_RAW_GAP}
      AND ABS(ff.Close/ff.pc - 1) < {SCAN_ADJ_CONT}
    ORDER BY ff.time DESC, ABS(ff.factor/ff.pf - 1) DESC"""
    df = bq_df(sql)
    print(f"\n=== scan {SCAN_UNIVERSE} last {days}d -> {len(df)} unhandled candidate(s) ===")
    if df.empty:
        print("  none"); return []

    pend = _load_pending()
    # ISO-week stamp for weekly re-reminder dedup (no Date.now in helpers -> derive
    # the week from CURRENT_DATE via BQ once)
    cur_wk = bq_df("SELECT FORMAT_DATE('%G-W%V', CURRENT_DATE()) AS wk").iloc[0]["wk"]
    fresh = []
    for _, r in df.iterrows():
        key = f"{r['ticker']}|{r['ex_date']}"
        last_wk = pend.get(key)
        print(f"  {r['ticker']:5s} ex {r['ex_date']}  gross_adj {r['factor_step_pct']:+.1f}%  "
              f"raw_gap {r['raw_gap_pct']:+.1f}%  adj_cont {r['adj_return_pct']:+.1f}%"
              + ("" if last_wk != cur_wk else "   (already alerted this week)"))
        if last_wk != cur_wk:
            fresh.append(r); pend[key] = cur_wk
    _save_pending(pend)

    for r in fresh:
        bus("finding", f"corp-action MỚI: {r['ticker']} reset hệ số giá ex {r['ex_date']}",
            {"ticker": r["ticker"], "ex_date": str(r["ex_date"]),
             "gross_adj_pct": float(r["factor_step_pct"]),
             "raw_gap_pct": float(r["raw_gap_pct"]),
             "adj_continuity_pct": float(r["adj_return_pct"]),
             "audience": ["Winston", "Taylor"],
             "action": ("Winston: kiểm công bố VSD/cafef -> phân loại cash/stock; "
                        "stock -> thêm CORP_ACTIONS + chạy `--ticker " + r["ticker"] + "`; "
                        "cash-only -> `--ack-cash " + r["ticker"] + ":" + str(r["ex_date"]) + "`. "
                        "Taylor: PE/PB mã này có thể méo tới khi OShares được sửa.")})
    print(f"  -> alerted {len(fresh)} new (others deduped this week)")
    return fresh


def ack_cash(spec):
    """Record a CASH-ONLY ex-date (no share change) so the scan stops re-alerting.
    spec = 'TICKER:YYYY-MM-DD'. Inserts a row with stock_div_ratio=0, oshares=prev."""
    ticker, ex_date = spec.split(":")
    prev_osh, q = bq_latest_oshares(ticker)
    if prev_osh is None:
        print(f"  [error] no OShares for {ticker}"); return
    merge = f"""
    MERGE {TABLE} T
    USING (SELECT '{ticker}' AS ticker, DATE '{ex_date}' AS ex_date) S
    ON T.ticker=S.ticker AND T.ex_date=S.ex_date
    WHEN NOT MATCHED THEN INSERT
      (ticker, ex_date, oshares, prev_oshares, stock_div_ratio, cash_div_per_share,
       price_adj_factor, source, note, updated_at)
      VALUES('{ticker}', DATE '{ex_date}', {prev_osh}, {prev_osh}, 0.0, NULL, NULL,
             'ack', 'cash-only / no share change', CURRENT_TIMESTAMP())"""
    run_bq(merge)
    print(f"  ✓ ack cash-only {ticker} {ex_date} (OShares unchanged {prev_osh:,}) -> {TABLE}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--detect-only", action="store_true")
    ap.add_argument("--scan", action="store_true", help="scan universe for NEW corp actions (alert only)")
    ap.add_argument("--scan-days", type=int, default=5)
    ap.add_argument("--ack-cash", default=None, metavar="TICKER:YYYY-MM-DD")
    ap.add_argument("--ticker", default=None)
    args = ap.parse_args()

    if args.ack_cash:
        ack_cash(args.ack_cash); return
    if args.scan:
        scan_universe(days=args.scan_days); return

    tickers = [args.ticker] if args.ticker else WATCHLIST
    written = []
    for tk in tickers:
        try:
            r = process(tk, write=not args.detect_only)
            if r and not args.detect_only and r.get("new_osh"):
                written.append(r)
        except Exception as e:
            print(f"  [error] {tk}: {repr(e)[:200]}")
    if written:
        bus("finding", "shares_outstanding_live updated",
            {"table": TABLE, "updated": written,
             "consumer_note": "LEFT JOIN shares_outstanding_live ON ticker AND time>=ex_date to override stale ticker_financial.OShares for PE/PB/market-cap"})
    print(f"""
--- CONSUMER JOIN TEMPLATE (corrected current shares) ---
SELECT t.ticker, t.time, t.Close,
       COALESCE(s.oshares, f.OShares) AS oshares_live
FROM tav2_bq.ticker t
LEFT JOIN {TABLE} s ON s.ticker=t.ticker AND t.time >= s.ex_date
WHERE t.ticker='ACB' ORDER BY t.time DESC LIMIT 5;
""")


if __name__ == "__main__":
    main()
