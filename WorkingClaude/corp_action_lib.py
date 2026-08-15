#!/usr/bin/env python3
"""corp_action_lib.py — shared reader + taxonomy for `tav2_bq.corporate_action`.

Registry: `mike/kb/data_registry/price-volume/corporate_action_bq.md` (read it before changing
anything here — it carries the three measured traps).

THE DISTINCTION THIS MODULE EXISTS FOR
--------------------------------------
An `ISS` (share issuance) event does one, or both, of two very different things, and which one
decides whether a given consumer must care about it:

  * it DILUTES THE SHARE COUNT — always true, for every ISS. Oshares must count all of them.
  * it ACCRUES A RIGHT TO EXISTING SHAREHOLDERS — true only for some. Only these move the price
    on `exright_date`, and therefore only these appear in the `Close/Price` adjustment ratio.

Measured proof (2026-08-13): HAH issued 1,86% ESOP with `exright_date = 2026-07-28`, and the
price series shows NO ratio step on that day (1,000000 → 1,000000) — correctly, because employees
bought those shares, not existing holders. FPT's two 2026-06-24 ESOP issues behave identically.
A rebase that expected a step there would report a false mismatch; an Oshares model that skipped
them would undercount shares. Same rows, opposite treatment — hence one taxonomy, stated once.
"""
from __future__ import annotations

import json
import subprocess

BQ_PROJECT = "lithe-record-440915-m9"
TABLE = f"{BQ_PROJECT}.tav2_bq.corporate_action"

# ISS methods that give existing shareholders something -> the price adjusts at exright_date.
PRICE_ADJUSTING_ISS = {
    "Trả Cổ tức bằng Cổ phiếu",          # stock dividend
    "Cổ phiếu thưởng",                    # bonus shares
    "Quyền mua CP cho Cổ đông hiện hữu",  # rights issue to existing holders
}

# ISS methods that create shares for SOMEONE ELSE -> share count rises, price does NOT adjust.
NON_ACCRUING_ISS = {
    "Phát hành cho CBCNV",                # ESOP
    "Phát hành riêng lẻ",                 # private placement
    "Chuyển từ trái phiếu chuyển đổi",    # convertible bond conversion
    "Phát hành rộng rãi qua đấu giá",     # public auction
    "Phát hành để sáp nhập",              # merger consideration
    "Phát hành cho trái chủ",             # to bondholders
}


def is_price_adjusting(event: dict) -> bool:
    """True if this event should move the Close/Price ratio on its exright_date.

    DIV (cash dividend) always does. ISS depends on who receives the shares. Unknown/blank
    issue methods are treated as NON-adjusting: an unrecognised method is far more likely to be
    a placement variant than a shareholder right, and guessing "adjusting" would turn a data gap
    into a false mismatch report.
    """
    code = event.get("event_code")
    if code == "DIV":
        return True
    if code != "ISS":
        return False
    return (event.get("issue_method_name_vi") or "").strip() in PRICE_ADJUSTING_ISS


def dilutes_share_count(event: dict) -> bool:
    """True if this event increases shares outstanding (every executed ISS does)."""
    return event.get("event_code") == "ISS"


MAX_ROWS = 1_000_000


def bq(sql: str, timeout: int = 300):
    """Run a query through the bq CLI and return a list of dict rows.

    `--max_rows` is MANDATORY, not tuning: the bq CLI silently truncates a result set at **100
    rows** by default and reports success. That bug bit for real on 2026-08-13 — `oshares_live`
    fetching quarterly share counts for two tickers at once got 100 of ~150 rows, lost PVT's
    recent quarters, and silently fell back to a year-old anchor while looking perfectly healthy.
    A truncated read is indistinguishable from a short history unless you ask for the ceiling.
    """
    out = subprocess.run(
        ["bq", "query", "--use_legacy_sql=false", f"--project_id={BQ_PROJECT}",
         "--format=json", "--quiet", f"--max_rows={MAX_ROWS}", sql],
        capture_output=True, text=True, timeout=timeout,
    )
    if out.returncode != 0:
        raise RuntimeError(f"bq failed: {out.stderr[-400:]}")
    rows = json.loads(out.stdout or "[]")
    if len(rows) >= MAX_ROWS:
        raise RuntimeError(f"kết quả chạm trần {MAX_ROWS} dòng — có thể đã bị cắt, "
                           f"thu hẹp truy vấn thay vì tin số này")
    return rows


def feed_freshness() -> dict:
    """MAX(ingested_at)/MAX(public_date)/row count — verify the artifact, never the promise.

    The registry records a user statement that this table refreshes daily from 2026-08-13. Every
    consumer must check rather than assume (coding_guidelines §14): as of 2026-08-13 the whole
    table was still the single 2026-08-12 15:22→15:48 load batch.
    """
    return bq(f"SELECT CAST(MAX(ingested_at) AS STRING) max_ingested, "
              f"CAST(MAX(public_date) AS STRING) max_public, COUNT(*) n FROM `{TABLE}`")[0]


def events(tickers, since=None, until=None, codes=("DIV", "ISS"), executed_only=True):
    """Executed corp-action events for `tickers`, ordered by (ticker, exright_date).

    `executed_only` drops `announced` (not yet certain) and `not_executed` (cancelled) — Bẫy of
    the registry doc. Rows are returned raw, including duplicates on (ticker, exright_date,
    event_code): those are real (several tranches can go ex on one day) and the CALLER must
    decide whether to sum them or take the latest revision, after reading `event_title_vi`.

    ⚠️ NOT usable as a forward PRICE CALENDAR — use `pricing_events()` for that. A future event
    sits at `announced` until the ~22:2x ICT reload of its own ex-date, so `executed_only=True`
    returns EMPTY for exactly the days a pricing gate needs to fire.
    """
    return _events(tickers, since, until, codes,
                   status_sql='event_status = "executed"' if executed_only else None)


def pricing_events(tickers, since=None, until=None, codes=("DIV", "ISS")):
    """Corp-action events usable as a forward PRICE CALENDAR (includes `announced`).

    Filters `event_status != "not_executed"` — i.e. drops only CANCELLED events. Anything else
    is a real scheduled ex-date the exchange will price against.

    Why this exists as a separate reader instead of a flag on `events()`: the `announced` trap
    is a measured bug (`mike/bin/corp_action_daily.py:422-437`, quant-skeptic REFUTED round 1),
    and a boolean flag invites callers to guess. A pricing consumer that reaches for the wrong
    reader gets silence — an empty result on the one day it matters, indistinguishable from
    "no event today". Named readers make the choice explicit at the call site.
    """
    return _events(tickers, since, until, codes,
                   status_sql='event_status != "not_executed"')


def _events(tickers, since, until, codes, status_sql):
    tk = ",".join(f'"{t}"' for t in tickers)
    cd = ",".join(f'"{c}"' for c in codes)
    where = [f"ticker IN ({tk})", f"event_code IN ({cd})"]
    if status_sql:
        where.append(status_sql)
    if since:
        where.append(f'exright_date > DATE "{since}"')
    if until:
        where.append(f'exright_date <= DATE "{until}"')
    return bq(f"""
        SELECT ticker, event_code, CAST(exright_date AS STRING) exright_date,
               CAST(effective_date AS STRING) effective_date, event_status,
               value_per_share, exercise_ratio, issue_method_name_vi,
               shares_delta, shares_total_after, event_title_vi,
               CAST(public_date AS STRING) public_date
        FROM `{TABLE}`
        WHERE {' AND '.join(where)}
        ORDER BY ticker, exright_date, public_date
    """)


def _selfcheck() -> int:
    fails = []

    def check(name, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            fails.append(name)

    check("1. cổ tức tiền mặt điều chỉnh giá",
          is_price_adjusting({"event_code": "DIV"}))
    check("2. cổ tức CP / thưởng / quyền mua ⇒ điều chỉnh giá",
          all(is_price_adjusting({"event_code": "ISS", "issue_method_name_vi": m})
              for m in PRICE_ADJUSTING_ISS))
    check("3. ESOP / riêng lẻ / chuyển đổi TP ⇒ KHÔNG điều chỉnh giá (ca thật HAH 2026-07-28)",
          not any(is_price_adjusting({"event_code": "ISS", "issue_method_name_vi": m})
                  for m in NON_ACCRUING_ISS))
    check("4. issue_method lạ/rỗng ⇒ mặc định KHÔNG điều chỉnh (fail-safe)",
          not is_price_adjusting({"event_code": "ISS", "issue_method_name_vi": "Phát hành kiểu mới"})
          and not is_price_adjusting({"event_code": "ISS", "issue_method_name_vi": None}))
    check("5. MỌI ISS đều làm tăng số lượng CP, kể cả loại không điều chỉnh giá",
          all(dilutes_share_count({"event_code": "ISS", "issue_method_name_vi": m})
              for m in PRICE_ADJUSTING_ISS | NON_ACCRUING_ISS))
    check("6. DIV KHÔNG làm tăng số lượng CP",
          not dilutes_share_count({"event_code": "DIV"}))
    check("7. hai tập phân loại không giao nhau",
          not (PRICE_ADJUSTING_ISS & NON_ACCRUING_ISS))

    print()
    if fails:
        print(f"FAILED {len(fails)}: {fails}")
        return 1
    print("OK — corp_action_lib selfcheck PASS")
    return 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--freshness", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        raise SystemExit(_selfcheck())
    if a.freshness:
        print(json.dumps(feed_freshness(), indent=2))
    else:
        ap.error("cần --selfcheck hoặc --freshness")
