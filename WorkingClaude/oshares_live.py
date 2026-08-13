#!/usr/bin/env python3
"""oshares_live.py — shares outstanding at ANY date, without waiting for the next quarterly report.

Replaces the manual path (`update_shares_live.py`, run by hand into the 4-row
`tav2_bq.shares_outstanding_live`) with a computed answer from two sources that already exist:
`ticker_financial.OShares` (quarterly) + `tav2_bq.corporate_action` (per-event).

THE PROBLEM
-----------
`ticker_financial.OShares` only moves when a quarter is published, so between reports it is stale
by up to ~3 months — and it is the denominator of market cap, EPS and every per-share metric. A
15% bonus issue makes it 15% wrong the day the stock goes ex.

THE METHOD — roll forward from the most recent AUTHORITATIVE count
------------------------------------------------------------------
For a target date D:

  1. Collect the candidate anchors, each a (date, count) pair that some source states as fact:
       - the latest `ticker_financial` row with `time <= D`     -> OShares
       - the latest executed `AIS` with `effective_date <= D`   -> shares_total_after
  2. Take the anchor with the LATEST date (the freshest thing anyone has actually asserted).
  3. Roll it forward: multiply by (1 + exercise_ratio) for every executed `ISS` with
     `exright_date` in (anchor_date, D].

Step 2 is what makes this correct rather than clever. `AIS` is exact but lags `exright_date` by
weeks (FPT 2025: ex 07-21, listed 09-12 — ~7 weeks, Bẫy 1 of the registry doc), while
`ticker_financial` sometimes moves FIRST (FPT's 2025Q2 row, dated 07-22, already carried the
post-bonus 1.703.507.121 — one day after ex-right and 7 weeks before the AIS). Neither source
dominates the other, so pick per-date instead of picking a favourite.

WHICH EVENTS COUNT — every ISS, not just the price-adjusting ones
-----------------------------------------------------------------
Share count and price adjustment are different questions (see `corp_action_lib`). An ESOP issue
creates shares without touching the price; excluding it because "the price didn't move" would
undercount. Verified on FPT's two 2025-05-07 ESOP tranches: rolling the 2025-04-23 quarterly count
forward through both gives 1.481.340.xxx against the 2025-06-19 AIS ground truth of 1.481.330.122
— 0,0007% apart. Rolling through the 15% bonus instead gives 1.703.529.640 vs 1.703.507.121
(0,0013%). Both gaps are fractional-share rounding, not method error.

ACCURACY, STATED HONESTLY
-------------------------
`AIS_EXACT`    — D is at or after the listing: the number is the registry's own, exact.
`ISS_ESTIMATE` — D is inside the ex-right→listing gap: ratio-derived, ~0,001% observed error on
                 FPT, and it is an ESTIMATE because `exercise_ratio` is rounded and treasury
                 shares/fractional-share handling are not modelled.
`ANCHOR_ONLY`  — no event since the anchor: the anchor's own number, unmodified.
"""
from __future__ import annotations

from corp_action_lib import TABLE, bq, dilutes_share_count

FIN_TABLE = "lithe-record-440915-m9.tav2_bq.ticker_financial"


def _dedup_iss(events):
    """Drop revisions of the same issuance; keep genuinely distinct tranches.

    Bẫy (3) of the registry: rows can repeat on (ticker, exright_date, event_code). Two rows on
    one day are REAL when they are different issuances (MBB 2026-08-11 = a 10% rights issue AND a
    15% stock dividend, both of which add shares) and a DUPLICATE when they restate the same one.
    Key on (exright_date, issue_method_name_vi, exercise_ratio): FPT's two 2025-05-07 ESOP rows
    differ in ratio (0,00225 vs 0,00472) and both survive, as they must.
    """
    seen, out = set(), []
    for e in events:
        key = (e["exright_date"], e.get("issue_method_name_vi"), str(e.get("exercise_ratio")))
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out


def _fetch(tickers, until):
    tk = ",".join(f'"{t}"' for t in tickers)
    quarters = bq(f"""
        SELECT ticker, CAST(time AS STRING) time, OShares
        FROM `{FIN_TABLE}`
        WHERE ticker IN ({tk}) AND time <= DATE "{until}" AND OShares IS NOT NULL AND OShares > 0
        ORDER BY ticker, time
    """)
    corp = bq(f"""
        SELECT ticker, event_code, CAST(exright_date AS STRING) exright_date,
               CAST(effective_date AS STRING) effective_date,
               exercise_ratio, issue_method_name_vi, shares_total_after,
               SUBSTR(event_title_vi, 1, 70) AS title
        FROM `{TABLE}`
        WHERE ticker IN ({tk}) AND event_status = "executed" AND event_code IN ("ISS", "AIS")
        ORDER BY ticker, COALESCE(exright_date, effective_date)
    """)
    return quarters, corp


def oshares_at(tickers, asof, _cache=None):
    """{ticker: dict} — shares outstanding at `asof`, with the derivation shown.

    Each value carries `value`, `method`, `anchor_date`, `anchor_value`, `anchor_source` and the
    list of ISS events applied, so any number can be re-derived by hand from the output alone.
    """
    if isinstance(tickers, str):
        tickers = [tickers]
    quarters, corp = _cache if _cache else _fetch(tickers, asof)

    out = {}
    for tk in tickers:
        qs = [q for q in quarters if q["ticker"] == tk and q["time"] <= asof]
        ais = [c for c in corp if c["ticker"] == tk and c["event_code"] == "AIS"
               and c["effective_date"] and c["effective_date"] <= asof
               and c["shares_total_after"]]
        iss = [c for c in corp if c["ticker"] == tk and c["event_code"] == "ISS"
               and c["exright_date"] and c["exright_date"] <= asof
               and c["exercise_ratio"] is not None and dilutes_share_count(c)]

        anchors = []
        if qs:
            q = max(qs, key=lambda r: r["time"])
            anchors.append((q["time"], float(q["OShares"]), "ticker_financial"))
        if ais:
            a = max(ais, key=lambda r: r["effective_date"])
            anchors.append((a["effective_date"], float(a["shares_total_after"]), "corporate_action.AIS"))

        if not anchors:
            out[tk] = {"ticker": tk, "asof": asof, "value": None, "method": "NO_ANCHOR",
                       "note": "không có OShares quý nào lẫn AIS nào <= ngày cần tính"}
            continue

        # freshest asserted fact wins; AIS breaks a same-date tie (it is a registry statement
        # about the listed count, not a figure copied into a financial statement)
        anchor_date, anchor_value, anchor_src = max(
            anchors, key=lambda a: (a[0], a[2] == "corporate_action.AIS"))

        applied = _dedup_iss([e for e in iss if e["exright_date"] > anchor_date])
        value = anchor_value
        for e in applied:
            value *= (1.0 + float(e["exercise_ratio"]))

        if applied:
            method = "ISS_ESTIMATE"
        elif anchor_src == "corporate_action.AIS":
            method = "AIS_EXACT"
        else:
            method = "ANCHOR_ONLY"

        out[tk] = {
            "ticker": tk, "asof": asof, "value": value, "method": method,
            "anchor_date": anchor_date, "anchor_value": anchor_value, "anchor_source": anchor_src,
            "events_applied": [
                {"exright_date": e["exright_date"], "ratio": float(e["exercise_ratio"]),
                 "method_vi": e.get("issue_method_name_vi"), "title": e.get("title")}
                for e in applied
            ],
        }
    return out


def _selfcheck() -> int:
    fails = []

    def check(name, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            fails.append(name)

    print("== FPT 2025: thưởng CP 15% ex 2025-07-21 → AIS hiệu lực 2025-09-12 ==")
    AIS_TRUTH = 1_703_507_121
    PRE = 1_481_330_122          # AIS 2025-06-19, ground truth trước sự kiện

    cache = _fetch(["FPT"], "2026-08-13")
    series = {}
    for d in ["2025-07-18", "2025-07-20", "2025-07-21", "2025-07-22",
              "2025-08-15", "2025-09-11", "2025-09-12", "2025-10-01"]:
        r = oshares_at(["FPT"], d, _cache=cache)["FPT"]
        series[d] = r
        print(f"  {d}: {r['value']:>15,.0f}  [{r['method']:12s}] anchor={r['anchor_date']}"
              f" ({r['anchor_source']}) +{len(r.get('events_applied', []))} ISS")

    check("1. trước ex-right: bằng ĐÚNG AIS 2025-06-19 (1.481.330.122)",
          series["2025-07-20"]["value"] == PRE, f"{series['2025-07-20']['value']:,.0f}")
    check("2. ĐÚNG ngày ex-right 07-21: nhảy lên ~1,7 tỷ (không chờ 7 tuần tới AIS)",
          abs(series["2025-07-21"]["value"] - AIS_TRUTH) / AIS_TRUTH < 0.001
          and series["2025-07-21"]["method"] == "ISS_ESTIMATE",
          f"{series['2025-07-21']['value']:,.0f} — lệch "
          f"{abs(series['2025-07-21']['value']-AIS_TRUTH)/AIS_TRUTH*100:.4f}%")
    # The series is non-decreasing EXCEPT at the one step where an ISS_ESTIMATE is superseded by
    # a hard number (07-21 1.703.529.640 -> 07-22 1.703.507.121). That -22.519 is the estimate
    # converging onto truth, not shares disappearing, so the honest assertion is "no MATERIAL
    # decrease, and any decrease must be an estimate giving way to a measured anchor".
    drops = [(a, b) for a, b in zip(list(series)[:-1], list(series)[1:])
             if series[b]["value"] < series[a]["value"] - 1e-6]
    check("3. chuỗi không giảm ĐÁNG KỂ; mọi bước giảm đều là ước lượng nhường chỗ cho số đo",
          all(series[a]["method"] == "ISS_ESTIMATE"
              and series[b]["method"] in ("AIS_EXACT", "ANCHOR_ONLY")
              and abs(series[b]["value"] - series[a]["value"]) / series[a]["value"] < 0.0001
              for a, b in drops),
          f"{len(drops)} bước giảm: " + (", ".join(
              f"{a}→{b} ({(series[b]['value']/series[a]['value']-1)*100:+.4f}%)" for a, b in drops)
              or "không có"))
    check("3b. đầu chuỗi < cuối chuỗi (thực sự đã tăng qua sự kiện)",
          series["2025-07-18"]["value"] < series["2025-10-01"]["value"],
          f"{series['2025-07-18']['value']:,.0f} → {series['2025-10-01']['value']:,.0f}")
    check("4. sau AIS hiệu lực: KHỚP TUYỆT ĐỐI shares_total_after = 1.703.507.121",
          series["2025-09-12"]["value"] == AIS_TRUTH and series["2025-10-01"]["value"] == AIS_TRUTH,
          f"{series['2025-09-12']['value']:,.0f}")
    check("5. không đếm hai lần: sau AIS không nhân lại ISS đã nằm trong AIS",
          series["2025-10-01"]["events_applied"] == [])

    print("== Kiểm chứng ESOP (loại KHÔNG điều chỉnh giá nhưng VẪN tăng số CP) ==")
    r = oshares_at(["FPT"], "2025-06-18", _cache=cache)["FPT"]
    print(f"  2025-06-18 (trước AIS 06-19): {r['value']:>15,.0f} [{r['method']}] "
          f"+{len(r['events_applied'])} ISS")
    check("6. lăn qua 2 đợt ESOP 2025-05-07 ⇒ khớp AIS 06-19 trong 0,01%",
          abs(r["value"] - PRE) / PRE < 0.0001 and len(r["events_applied"]) == 2,
          f"{r['value']:,.0f} vs {PRE:,.0f} — lệch {abs(r['value']-PRE)/PRE*100:.4f}%")
    check("7. hai đợt ESOP cùng ngày, KHÁC tỉ lệ ⇒ giữ CẢ HAI (không dedup nhầm)",
          sorted(e["ratio"] for e in r["events_applied"]) == [0.00225, 0.00472])

    print("== Ca đối chứng: không có sự kiện sau anchor ⇒ KHÔNG được đụng vào số anchor ==")
    ctrl = oshares_at(["DHG", "PVT", "TCB", "ACB", "HDB"], "2026-08-12")
    for tk, r in sorted(ctrl.items()):
        print(f"  {tk}: {r['value']:>15,.0f} [{r['method']:12s}] anchor={r['anchor_date']}"
              f" ({r['anchor_source']}) +{len(r['events_applied'])} ISS")
    # property, not an assumption about which tickers happen to be event-free — the earlier
    # version hardcoded "PVT has no events", which was simply false and masked a real bug
    check("8. mọi mã không có ISS sau anchor ⇒ value == anchor_value TUYỆT ĐỐI",
          all(r["value"] == r["anchor_value"]
              for r in ctrl.values() if not r["events_applied"]))
    check("8b. có ít nhất 1 mã đối chứng thật sự không sự kiện (test không rỗng)",
          any(not r["events_applied"] for r in ctrl.values()),
          f"{[t for t, r in ctrl.items() if not r['events_applied']]}")
    # regression: the bq CLI truncates at 100 rows by default; batching several tickers used to
    # silently drop the newest quarters and fall back to a year-old anchor (fixed in
    # corp_action_lib.bq via --max_rows). Batched must equal one-at-a-time, always.
    solo = {t: oshares_at([t], "2026-08-12")[t] for t in ctrl}
    check("8c. gọi theo LÔ == gọi từng mã (không bị bq cắt 100 dòng)",
          all(abs(ctrl[t]["value"] - solo[t]["value"]) < 1e-6 and
              ctrl[t]["anchor_date"] == solo[t]["anchor_date"] for t in ctrl),
          "; ".join(f"{t}: lô {ctrl[t]['anchor_date']} vs đơn {solo[t]['anchor_date']}"
                    for t in ctrl if ctrl[t]["anchor_date"] != solo[t]["anchor_date"]) or "khớp hết")

    print("== MBB: 2 đợt CÙNG NGÀY 2026-08-11 (quyền mua 10% + cổ tức CP 15%) ==")
    m = oshares_at(["MBB"], "2026-08-12")["MBB"]
    print(f"  {m['value']:,.0f} [{m['method']}] anchor={m['anchor_date']} "
          f"({m['anchor_source']}) events={[(e['exright_date'], e['ratio']) for e in m['events_applied']]}")
    check("9. cộng CẢ HAI đợt cùng ngày (×1,10×1,15), không gộp thành một",
          sorted(e["ratio"] for e in m["events_applied"] if e["exright_date"] == "2026-08-11")
          == [0.1, 0.15])

    print()
    if fails:
        print(f"FAILED {len(fails)}: {fails}")
        return 1
    print("OK — oshares_live selfcheck PASS")
    return 0


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--ticker", help="mã, phân tách bằng dấu phẩy")
    ap.add_argument("--asof", help="YYYY-MM-DD")
    a = ap.parse_args()

    if a.selfcheck:
        raise SystemExit(_selfcheck())
    if a.ticker and a.asof:
        print(json.dumps(oshares_at(a.ticker.split(","), a.asof), indent=2, ensure_ascii=False))
    else:
        ap.error("cần --selfcheck hoặc --ticker/--asof")
