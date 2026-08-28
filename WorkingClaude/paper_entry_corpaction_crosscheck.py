#!/usr/bin/env python3
"""paper_entry_corpaction_crosscheck.py — verify the paper entry rebase against an INDEPENDENT source.

`paper_entry_adjust.py` derives its adjustment factor from `Close/Price` (the price series itself).
This script checks that result against `tav2_bq.corporate_action` — a completely different data
path (vendor per-event corp-action feed, not the price ETL). Agreement between two independent
sources is the evidence; the rebase asserting its own correctness is not.

Two tests per ticker:

  T1 (binary, the important one)
      factor < 1  MUST hold  iff  an executed DIV/ISS exists with exright_date in (asof, today].
      A factor < 1 with no event = the price ETL adjusted for something that did not happen.
      A factor == 1 with an event = the report is still silently mispricing that position.

  T2 (timing — where the adjustment actually lands)
      For every executed event in the window, the `Close/Price` ratio must STEP UP exactly on
      `exright_date` (the ratio is flat between events and jumps toward 1,0 at each ex-date).
      This catches an off-by-one or a mis-dated adjustment that T1 cannot see: T1 only says
      "something was adjusted somewhere in the window", T2 says "it was adjusted on the day the
      corp-action feed says the stock went ex". Applies to DIV and ISS alike, so — unlike a
      per-share magnitude test — it needs no rights-issue subscription price (a field this table
      does not carry).

Usage:  python3 paper_entry_corpaction_crosscheck.py            # both paper books
        python3 paper_entry_corpaction_crosscheck.py --json     # machine-readable
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from corp_action_lib import is_price_adjusting
from paper_entry_adjust import WORKDIR, adjust_entries

BQ_PROJECT = "lithe-record-440915-m9"
TABLE = f"{BQ_PROJECT}.tav2_bq.corporate_action"
import os as _os
_GCP_SDK_BIN = "/home/trido/google-cloud-sdk/bin"
_BQ_BIN = shutil.which("bq") or f"{_GCP_SDK_BIN}/bq"
_GCP_ENV = {**_os.environ,
            "CLOUDSDK_CONFIG": _os.environ.get("CLOUDSDK_CONFIG",
                                               "/home/trido/thanhdt/gcloud_dtienthanh"),
            "PATH": _os.environ.get("PATH", "") + f":{_GCP_SDK_BIN}"}


def _bq(sql: str):
    """Run a BQ query via the CLI (same auth path as every other script here)."""
    out = subprocess.run(
        [_BQ_BIN, "query", "--use_legacy_sql=false", f"--project_id={BQ_PROJECT}",
         "--format=json", "--quiet", sql],
        capture_output=True, text=True, timeout=300, env=_GCP_ENV,
    )
    if out.returncode != 0:
        raise RuntimeError(f"bq failed: {out.stderr[-400:]}")
    return json.loads(out.stdout or "[]")


def _ratio_step(ticker, exright_date):
    """(ratio on the trading day BEFORE exright_date, ratio ON exright_date), or None."""
    import duckdb

    con = duckdb.connect()
    con.execute("SET threads=1")
    try:
        rows = con.execute(
            f"""
            SELECT time, Close / NULLIF(Price, 0) AS ratio
            FROM read_parquet('{WORKDIR}/data/bq_cache/ticker/*.parquet')
            WHERE ticker = ?
              AND time BETWEEN CAST(? AS DATE) - INTERVAL 15 DAY AND CAST(? AS DATE)
              AND Price > 0 AND Close > 0
            ORDER BY time DESC LIMIT 2
            """,
            [ticker, exright_date, exright_date],
        ).fetchall()
    finally:
        con.close()

    # LIMIT 2 descending gives [exright_date, previous trading day] — only valid if the first
    # row IS the ex-date (else the ex-date is missing from the cache and the test is meaningless)
    if len(rows) < 2 or str(rows[0][0]) != exright_date:
        return None
    return float(rows[1][1]), float(rows[0][1])


def load_books():
    """[(book, ticker, asof, entry_price)] from both paper portfolio files."""
    rows = []

    p = WORKDIR / "data" / "alphalens_paper.json"
    if p.exists():
        d = json.loads(p.read_text())
        # entry_price is demonstrably the 2026-06-30 raw close for all 4 names even though
        # entry_date says 2026-07-01 — honour an explicit entry_price_asof when present.
        default_asof = d.get("meta", {}).get("entry_price_asof")
        for pos in d.get("positions", []):
            rows.append(("alphalens", pos["ticker"],
                         default_asof or pos.get("entry_date"), float(pos["entry_price"])))

    p = WORKDIR / "data" / "converge_portfolio_paper.json"
    if p.exists():
        d = json.loads(p.read_text())
        asof = d.get("meta", {}).get("entry_price_asof")
        for pos in d.get("seed_double_confirm_set", []):
            rows.append(("converge", pos["ticker"], asof, float(pos["entry_price"])))
    return rows


def main(as_json=False):
    books = load_books()
    if not books:
        print("không tìm thấy file paper nào")
        return 1

    adj = adjust_entries([(t, a, p) for _, t, a, p in books])

    # freshness of the corp-action feed — verify the artifact, never the promise (§14)
    fresh = _bq(f"SELECT CAST(MAX(ingested_at) AS STRING) mi, CAST(MAX(public_date) AS STRING) mp, "
                f"COUNT(*) n FROM `{TABLE}`")[0]
    print(f"corporate_action: MAX(ingested_at)={fresh['mi']} MAX(public_date)={fresh['mp']} n={fresh['n']}")
    print()

    tickers = sorted({t for _, t, _, _ in books})
    asof_min = min(a for _, _, a, _ in books)
    tk_sql = ",".join(f'"{t}"' for t in tickers)
    events = _bq(f"""
        SELECT ticker, event_code, CAST(exright_date AS STRING) exright_date,
               value_per_share, exercise_ratio, event_status, issue_method_name_vi,
               SUBSTR(event_title_vi, 1, 60) AS title
        FROM `{TABLE}`
        WHERE ticker IN ({tk_sql})
          AND event_code IN ("DIV", "ISS")
          AND event_status = "executed"        -- Bẫy: loại not_executed / announced
          AND exright_date > DATE "{asof_min}"
          AND exright_date <= CURRENT_DATE()
        ORDER BY ticker, exright_date
    """)

    by_ticker = {}
    for e in events:
        by_ticker.setdefault(e["ticker"], []).append(e)

    results, fails = [], []
    for book, ticker, asof, entry_price in books:
        a = adj[(ticker, asof)]
        evs = [e for e in by_ticker.get(ticker, []) if e["exright_date"] > asof]
        # only events that accrue to EXISTING holders move the price (corp_action_lib);
        # an ESOP/placement dilutes the count without an ex-right, so it must not be expected here
        adj_evs = [e for e in evs if is_price_adjusting(e)]
        has_event = bool(adj_evs)
        # neo vào factor_terp (Close/Price thô), KHÔNG vào factor dùng để báo cáo: T1 hỏi "chuỗi
        # giá có điều chỉnh không" — câu hỏi về chuỗi giá. Quy ước accrue-only loại quyền mua, nên
        # một sự kiện quyền-mua-đơn-thuần cho factor = 1,0 hoàn toàn đúng đắn và sẽ sinh báo động
        # giả nếu neo vào nó. Cùng lý lẽ với report_return_gate.paper_t1_verdict().
        factor_moved = a.factor_terp is not None and a.factor_terp < 1.0 - 1e-6

        t1 = (has_event == factor_moved)
        if not t1:
            fails.append(f"{book}/{ticker} T1")

        kinds = sorted({e["event_code"] for e in evs})
        detail = ", ".join(f"{e['event_code']} {e['exright_date']}"
                           f"{' ' + str(e['value_per_share']) + 'đ' if e['value_per_share'] else ''}"
                           f"{' r=' + str(e['exercise_ratio']) if e['event_code'] == 'ISS' else ''}"
                           for e in evs) or "—"

        results.append({
            "book": book, "ticker": ticker, "asof": asof,
            "entry_price": entry_price, "entry_adj": round(a.entry_adj, 2),
            "factor": a.factor, "status": a.status,
            "n_events": len(evs), "event_kinds": kinds, "events": detail,
            "T1_pass": t1, "note": a.note,
        })

        flag = "OK " if t1 else "MISMATCH"
        print(f"[{flag}] {book:9s} {ticker:4s} asof={asof} factor="
              f"{a.factor if a.factor is not None else float('nan'):.6f} "
              f"entry {entry_price:>9,.0f} → {a.entry_adj:>9,.0f}  | {detail}")
        if a.note:
            print(f"           ⚠ {a.note}")

    print()
    print(f"T1 (factor<1 ⟺ có corp-action executed): {len(results)-len(fails)}/{len(results)} khớp")
    if fails:
        print(f"KHÔNG KHỚP: {fails}")

    # ---- T2: the ratio step must land ON exright_date ----
    print()
    t2_ok, t2_bad = 0, []
    seen = set()
    for e in events:
        if not is_price_adjusting(e):
            print(f"  n/a  {e['ticker']:4s} {e['exright_date']}: "
                  f"{e['issue_method_name_vi']} — không phát sinh quyền cho cổ đông hiện hữu, "
                  f"KHÔNG kỳ vọng bậc nhảy giá")
            continue
        key = (e["ticker"], e["exright_date"])
        if key in seen:
            continue          # 2 events same ticker+day (MBB 08-11) = one price step, test once
        seen.add(key)
        step = _ratio_step(e["ticker"], e["exright_date"])
        if step is None:
            print(f"  SKIP {e['ticker']} {e['exright_date']} — thiếu giá quanh ex-date")
            continue
        prev_r, ex_r = step
        ok = ex_r > prev_r + 1e-6
        print(f"  {'OK  ' if ok else 'FAIL'} {e['ticker']:4s} {e['exright_date']}: "
              f"ratio {prev_r:.6f} → {ex_r:.6f}")
        if ok:
            t2_ok += 1
        else:
            t2_bad.append(key)
    print(f"T2 (bậc nhảy ratio rơi ĐÚNG exright_date): {t2_ok}/{t2_ok + len(t2_bad)} khớp")
    if t2_bad:
        print(f"KHÔNG KHỚP: {t2_bad}")
        fails.extend(f"{t}/{d} T2" for t, d in t2_bad)

    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    return 1 if fails else 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    raise SystemExit(main(as_json=a.json))
