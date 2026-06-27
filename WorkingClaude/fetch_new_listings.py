"""
fetch_new_listings.py — Winston daily feed: new listings on HOSE/HNX/UPCOM

Output:
  data/new_listings.csv          — all new listings since LOOKBACK_DAYS, with 8L research flag
  data/new_listings_history.csv  — append-only running log

Cron: runs daily after market close (18:30 ICT) via crontab managed by Winston.
Bus: posts findings to mike-fleet event bus via append_event.sh.
"""

import subprocess
import sys
import os
import json
import warnings
from datetime import date, timedelta

import pandas as pd

warnings.filterwarnings("ignore")

BQ_PROJECT = "lithe-record-440915-m9"

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
DATA_DIR = os.path.join(WORKDIR, "data")
APPEND_EVENT = os.path.join(WORKDIR, "mike/bin/append_event.sh")

# Lookback for "new" = listed in last N days (running window; 90 days catches quarterly refreshes)
LOOKBACK_DAYS = int(os.environ.get("NEW_LISTING_LOOKBACK", 90))
# Tickers with fewer than MIN_QUARTERS quarters of history need 8L manual research
MIN_QUARTERS = 20  # ~5 years
# Flag extra-short history (fresh IPO, needs urgent research)
FRESH_IPO_QUARTERS = 8  # < 2 years


def bq(sql: str) -> pd.DataFrame:
    """Run a BigQuery SQL via SDK and return DataFrame."""
    from google.cloud import bigquery
    client = bigquery.Client(project=BQ_PROJECT)
    return client.query(sql).to_dataframe()


def get_new_tickers_from_bq(lookback_days: int) -> pd.DataFrame:
    """Find tickers whose first BQ data date is within lookback_days from today."""
    cutoff = (date.today() - timedelta(days=lookback_days)).isoformat()
    sql = f"""
SELECT t.ticker, MIN(t.time) AS listing_date, t.ICB_Code
FROM `tav2_bq.ticker` AS t
GROUP BY t.ticker, t.ICB_Code
HAVING MIN(t.time) >= "{cutoff}"
ORDER BY MIN(t.time) DESC
"""
    df = bq(sql)
    df["listing_date"] = pd.to_datetime(df["listing_date"]).dt.date
    return df


def get_financial_history_depth(tickers: list) -> pd.DataFrame:
    """Return number of quarters of financial data available per ticker."""
    if not tickers:
        return pd.DataFrame(columns=["ticker", "n_quarters", "first_fin_date"])
    ticker_list = ", ".join(f'"{t}"' for t in tickers)
    sql = f"""
SELECT t.ticker,
  COUNT(DISTINCT t.quarter) AS n_quarters,
  MIN(t.time) AS first_fin_date
FROM `tav2_bq.ticker_financial` AS t
WHERE t.ticker IN ({ticker_list})
GROUP BY t.ticker
"""
    df = bq(sql)
    return df


def get_exchange_industry_from_vnstock(retries: int = 3, delay: float = 10.0) -> pd.DataFrame:
    """Pull exchange + ICB industry name from vnstock Listing API."""
    import time
    for attempt in range(retries):
        try:
            from vnstock import Listing
            lst = Listing(source="vci")
            df = lst.symbols_by_exchange(lang="vi")
            df = df.rename(columns={
                "symbol": "ticker",
                "exchange": "exchange",
                "organ_name": "company_name",
                "organ_short_name": "company_short",
                "icb_code2": "icb_code_vnstock",
            })
            return df[["ticker", "exchange", "company_name", "company_short", "icb_code_vnstock"]]
        except Exception as e:
            if attempt < retries - 1:
                print(f"[WARN] vnstock Listing API attempt {attempt+1} failed: {e}. Retrying in {delay}s...", file=sys.stderr)
                time.sleep(delay)
            else:
                print(f"[WARN] vnstock Listing API failed after {retries} attempts: {e}. Exchange info will be empty.", file=sys.stderr)
    return pd.DataFrame(columns=["ticker", "exchange", "company_name", "company_short", "icb_code_vnstock"])


def get_icb_name_map(retries: int = 3, delay: float = 10.0) -> dict:
    """Return icb_code (int, any level) → industry name (vi) dict.

    vnstock industries_icb returns codes like "0533", "8633", "OTHER".
    We parse all numeric codes and build a lookup so BQ's ICB_Code (e.g. 8633) maps to a name.
    """
    import time
    for attempt in range(retries):
        try:
            from vnstock import Listing
            lst = Listing(source="vci")
            df = lst.industries_icb(lang="vi")
            result = {}
            for _, row in df.iterrows():
                code_str = str(row.get("icb_code", "")).strip().lstrip("0")
                if not code_str or not code_str.isdigit():
                    continue
                result[int(code_str)] = row["icb_name"]
            return result
        except Exception as e:
            if attempt < retries - 1:
                print(f"[WARN] vnstock industries_icb attempt {attempt+1} failed: {e}. Retrying in {delay}s...", file=sys.stderr)
                time.sleep(delay)
            else:
                print(f"[WARN] vnstock industries_icb failed after {retries} attempts: {e}. Industry names will be empty.", file=sys.stderr)
    return {}


def prospectus_search_url(ticker: str, exchange) -> str:
    """Return a best-effort URL to search for the prospectus on the relevant exchange."""
    ex = (str(exchange) if exchange and str(exchange) != "nan" else "").upper()
    if ex == "HSX":
        return f"https://www.hsx.vn/Modules/Cms/Web/ArrCmsPage.aspx?cmsid=1&key={ticker}"
    elif ex == "HNX":
        return f"https://hnx.vn/en-gb/co-phieu-etf-cq.html?nid={ticker}"
    else:
        # UPCOM — UPCOM uses UPCoM portal (same HNX infrastructure)
        return f"https://upcom.vn/en-gb/home/directory/overview.aspx?StockSymbol={ticker}"


def append_event(event_type: str, subject: str, payload: dict) -> None:
    """Post event to fleet bus."""
    payload_str = json.dumps(payload, ensure_ascii=False)
    subprocess.run(
        [APPEND_EVENT, "Winston", event_type, subject, payload_str],
        capture_output=True,
        text=True,
    )


def main():
    today_str = date.today().isoformat()
    print(f"[fetch_new_listings] {today_str} — lookback {LOOKBACK_DAYS} days")

    # --- 1. Detect new tickers from BQ ---
    print("  Querying BQ for new tickers...")
    new_df = get_new_tickers_from_bq(LOOKBACK_DAYS)
    if new_df.empty:
        print(f"  No new listings found in last {LOOKBACK_DAYS} days.")
        append_event("status", "new-listings-daily", {
            "date": today_str, "count": 0, "lookback_days": LOOKBACK_DAYS,
            "note": "no new listings detected"
        })
        return

    tickers = new_df["ticker"].tolist()
    print(f"  Found {len(tickers)} new ticker(s): {tickers}")

    # --- 2. Financial history depth ---
    print("  Checking financial history depth...")
    fin_df = get_financial_history_depth(tickers)

    # --- 3. Exchange + company info from vnstock ---
    print("  Fetching exchange/industry from vnstock...")
    exchange_df = get_exchange_industry_from_vnstock()
    icb_names = get_icb_name_map()

    # --- 4. Merge ---
    merged = new_df.merge(exchange_df, on="ticker", how="left")
    merged = merged.merge(fin_df[["ticker", "n_quarters", "first_fin_date"]], on="ticker", how="left")
    merged["n_quarters"] = merged["n_quarters"].fillna(0).astype(int)

    # Map ICB code from BQ (ICB_Code column is level-4 float) to name
    merged["ICB_Code"] = merged["ICB_Code"].fillna(0).astype(int)
    merged["industry_name"] = merged["ICB_Code"].map(icb_names).fillna("")

    # Fall back to vnstock ICB code if BQ ICB_Code is 0
    merged["icb_code_vnstock"] = merged["icb_code_vnstock"].fillna(0).astype(int)
    merged["industry_name"] = merged.apply(
        lambda r: r["industry_name"] if r["industry_name"] else icb_names.get(r["icb_code_vnstock"], ""),
        axis=1
    )

    # --- 5. 8L research flags ---
    merged["needs_manual_rating"] = merged["n_quarters"] < MIN_QUARTERS
    merged["is_fresh_ipo"] = merged["n_quarters"] < FRESH_IPO_QUARTERS

    # Prospectus URL
    merged["prospectus_search_url"] = merged.apply(
        lambda r: prospectus_search_url(r["ticker"], r.get("exchange", "")), axis=1
    )

    # --- 6. Final schema ---
    out = merged[[
        "ticker", "listing_date", "exchange", "company_name", "company_short",
        "industry_name", "ICB_Code", "n_quarters", "is_fresh_ipo",
        "needs_manual_rating", "prospectus_search_url"
    ]].rename(columns={"ICB_Code": "icb_code"})

    out = out.sort_values("listing_date", ascending=False).reset_index(drop=True)

    # --- 7. Save snapshot ---
    snapshot_path = os.path.join(DATA_DIR, "new_listings.csv")
    out.to_csv(snapshot_path, index=False)
    print(f"  Saved snapshot → {snapshot_path}")

    # --- 8. Append to history log ---
    history_path = os.path.join(DATA_DIR, "new_listings_history.csv")
    out["fetched_date"] = today_str
    if os.path.exists(history_path):
        hist = pd.read_csv(history_path)
        # Avoid duplicate entries: deduplicate by ticker + listing_date + fetched_date
        combined = pd.concat([hist, out], ignore_index=True)
        combined = combined.drop_duplicates(subset=["ticker", "listing_date"], keep="last")
        combined.to_csv(history_path, index=False)
    else:
        out.to_csv(history_path, index=False)
    print(f"  Updated history → {history_path}")

    # --- 9. Summary print ---
    need_research = out[out["needs_manual_rating"]]
    fresh_ipos = out[out["is_fresh_ipo"]]
    print(f"\n  === SUMMARY (last {LOOKBACK_DAYS} days) ===")
    print(f"  Total new listings: {len(out)}")
    print(f"  Needs 8L manual rating (< {MIN_QUARTERS} quarters): {len(need_research)}")
    print(f"  Fresh IPO (< {FRESH_IPO_QUARTERS} quarters): {len(fresh_ipos)}")
    if not need_research.empty:
        print("\n  Tickers needing manual research:")
        for _, r in need_research.iterrows():
            flag = " *** FRESH IPO" if r["is_fresh_ipo"] else ""
            exch = str(r.get('exchange', '?') or '?')
            ind = str(r.get('industry_name', '') or '')[:30]
            print(f"    {r['ticker']:6s} | {str(r['listing_date']):12s} | {exch:6s} | "
                  f"{ind:30s} | {r['n_quarters']:2d}Q{flag}")

    # --- 10. Post to bus ---
    research_list = need_research[["ticker", "listing_date", "exchange", "industry_name",
                                   "n_quarters", "is_fresh_ipo", "prospectus_search_url"]].to_dict(orient="records")
    # Convert date objects to string for JSON
    for row in research_list:
        row["listing_date"] = str(row["listing_date"])
        row["is_fresh_ipo"] = bool(row["is_fresh_ipo"])

    append_event("finding", "new-listings-daily", {
        "date": today_str,
        "lookback_days": LOOKBACK_DAYS,
        "total_new": len(out),
        "needs_manual_rating": len(need_research),
        "fresh_ipo": len(fresh_ipos),
        "research_queue": research_list,
        "snapshot": snapshot_path,
        "note": (
            f"{len(need_research)} mã mới < {MIN_QUARTERS}Q lịch sử → cần 8L manual rating. "
            f"Taylor flag để đọc bản cáo bạch + tạo override documented reason+expiry."
        ),
    })

    print("\n  [OK] Bus updated.")


if __name__ == "__main__":
    main()
