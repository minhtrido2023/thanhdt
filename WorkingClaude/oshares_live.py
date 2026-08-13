#!/usr/bin/env python3
"""oshares_live.py — shares outstanding at ANY date, without waiting for the next quarterly report.

STATUS: NOT WIRED. No consumer may read this module until a second quant-skeptic pass clears it
(round 1 REFUTED it on 2026-08-13 for the two defects rewritten below).

Replaces the manual path (`update_shares_live.py`, run by hand into the 4-row
`tav2_bq.shares_outstanding_live`) with a computed answer from two sources that already exist:
`ticker_financial.OShares` (quarterly) + `tav2_bq.corporate_action` (per-event).

THE PROBLEM
-----------
`ticker_financial.OShares` only moves when a quarter is published, so between reports it is stale
by up to ~3 months — and it is the denominator of market cap, EPS and every per-share metric. A
15% bonus issue makes it 15% wrong the day the stock goes ex.

WHY THE FIRST VERSION WAS WRONG (both defects measured, both fixed here)
------------------------------------------------------------------------
(1) It picked whichever of `ticker_financial` / `AIS` carried the LATEST date and called that the
    "freshest asserted fact". But `ticker_financial.OShares` is **RESTATED, not point-in-time**:
    a quarterly row is rewritten later to carry the share count as it stands at publication (or
    later still). Measured 2026-08-13 on the whole table: **2.667 quarterly rows across 576
    tickers** carry a value that equals an AIS listed count which only became effective LATER —
    up to **2.693 days** later, **626 of them since 2024-01-01**. So "ticker_financial moves
    first" is mostly a restatement artifact, i.e. LOOK-AHEAD, not early data.

    Concrete: HAH's quarterly row dated **2026-02-02** already carries **185.840.401** — the count
    that only came into existence with the AIS of **2026-05-27** (listing 16.979.189 shares from a
    convertible-bond conversion on 2026-03-12 and an ESOP on 2026-04-17, both AFTER 02-02). The
    old code answered 185.840.401 for 2026-03-01. The truth that day was 168.861.212.

(2) It rolled forward with `(1 + exercise_ratio)` for every ISS — but `exercise_ratio` is 0 or
    NULL for **3.914 of 9.297** executed ISS rows (42%), and the zeros are concentrated exactly in
    the methods that do not accrue to existing holders: private placement 2.187/2.280, ESOP
    1.105/1.222, convertible-bond conversion 240/243, auction 140/142, merger 85/99. Multiplying
    by 1.0 there is a silent no-op that was nevertheless labelled `ISS_ESTIMATE`, i.e. reported as
    if the event had been accounted for. `shares_delta` cannot rescue it: that column is
    **NULL on 100% of ISS rows (0 of 9.297)** — it is populated only on AIS/NLIS/SUSP.

THE METHOD — an anchor that must EXPLAIN ITSELF, then a fail-closed roll-forward
-------------------------------------------------------------------------------
For a target date D, using only facts knowable at D (no row dated after D is consulted, in either
direction — the gate below is point-in-time, so a backtest at D gets the same answer live-at-D):

  1. `AIS.shares_total_after` (latest `effective_date <= D`) is the exact anchor: it is the
     registry's own statement of the listed count.
  2. A `ticker_financial` row (latest `time <= D`) is admitted as an anchor ONLY IF its value is
     EXPLAINED — i.e. the last AIS at-or-before that row, rolled forward through the executed ISS
     between them, reproduces it within 0,1%. FPT's 2025Q2 row (dated 07-22, carrying the
     post-bonus 1.703.507.121 seven weeks before the AIS) IS explained — the 15% bonus went ex on
     07-21, one day earlier — so genuine early data still gets used. HAH's 2026-02-02 row is NOT
     explained (no event between the 2025-09-09 AIS and 02-02 accounts for +16.979.189) and is
     rejected. A row that cannot be explained because an intervening ISS has no usable ratio is
     also rejected: unverifiable is not the same as verified.
  3. Roll the surviving anchor forward through every executed ISS with `exright_date` in
     (anchor_date, D], preferring `shares_delta` when present (additive, exact) and falling back
     to `(1 + exercise_ratio)`. An ISS with NEITHER — ratio in {0, NULL} and no delta — **fails
     CLOSED**: `value=None`, `method="UNKNOWN_RATIO"`, the blocking events listed. It is not
     multiplied by 1.0 and it is not labelled as handled.

WHICH EVENTS COUNT — every ISS, not just the price-adjusting ones
-----------------------------------------------------------------
Share count and price adjustment are different questions (see `corp_action_lib`). An ESOP issue
creates shares without touching the price; excluding it because "the price didn't move" would
undercount. Verified on FPT's two 2025-05-07 ESOP tranches: rolling the 2025-04-23 quarterly count
forward through both gives 1.481.340.xxx against the 2025-06-19 AIS ground truth of 1.481.330.122
— 0,0007% apart. Both gaps are fractional-share rounding, not method error.

ACCURACY, STATED HONESTLY
-------------------------
`AIS_EXACT`      — the anchor is an AIS and nothing ratio-derived happened since: the registry's
                   own number.
`ANCHOR_ONLY`    — the anchor is a quarterly row that PASSED the explanation gate, nothing since.
`ANCHOR_UNVERIFIED` — the anchor is a quarterly row for a ticker with no AIS before it, so the
                   gate had nothing to check it against (DHG). The number is returned because
                   blanking every never-listed-again ticker is a coverage loss the data does not
                   justify — but it is NOT cleared, and a consumer that needs a checked number
                   must treat this like a miss.
`ISS_ESTIMATE`   — rolled through at least one ratio-derived event: ~0,001% observed error on FPT;
                   an ESTIMATE because `exercise_ratio` is rounded and treasury/fractional-share
                   handling is not modelled.
`UNKNOWN_RATIO`  — an intervening ISS carries no usable size. **`value is None`** — the caller
                   gets nothing, deliberately, rather than a number that is quietly the old one.
`NO_ANCHOR`      — nothing admissible at or before D.

RESIDUAL LIMITATION, STATED BECAUSE IT CANNOT BE CLOSED FROM THIS SIDE
-----------------------------------------------------------------------
The explanation gate can only reject a restated quarterly row when the restatement contradicts
events the feed already carries. A row restated to a count whose backing AIS has not been ingested
yet is invisible to it — the same blind spot every point-in-time reconstruction has. That is one
more reason `ticker_financial.OShares` is filed TRAP in the data registry
(`mike/kb/data_registry/fundamentals/ticker_financial_oshares.md`) and why AIS, not the quarterly
row, is the primary anchor here.
"""
from __future__ import annotations

from corp_action_lib import TABLE, bq, dilutes_share_count

FIN_TABLE = "lithe-record-440915-m9.tav2_bq.ticker_financial"

# a quarterly count is "explained" by the rolled-forward AIS when it lands this close. The largest
# real gap measured is FPT's 0,0013% (fractional-share rounding on a 15% bonus); 0,1% leaves two
# orders of magnitude of headroom over that while still rejecting HAH's 10,1% jump.
EXPLAIN_TOL = 0.001


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


def _roll(anchor_value, events):
    """(value, blockers) — roll `anchor_value` through `events` in ex-date order, fail-closed.

    `shares_delta` first (additive, the registry's own count of new shares) then
    `(1 + exercise_ratio)`. An event offering neither is a BLOCKER: it is returned, not skipped,
    and the caller must refuse to answer. Measured on 2026-08-13, `shares_delta` is NULL on every
    one of the 9.297 executed ISS rows, so the delta branch is dead today — it is here because the
    fallback order is the correctness statement, and a vendor backfill must not silently keep
    using the rounded ratio once the exact number arrives.
    """
    value, applied, blockers = float(anchor_value), [], []
    for e in sorted(events, key=lambda r: r["exright_date"]):
        delta = e.get("shares_delta")
        ratio = e.get("exercise_ratio")
        if delta is not None and float(delta) != 0.0:
            value += float(delta)
            applied.append((e, "shares_delta", float(delta)))
        elif ratio is not None and float(ratio) > 0.0:
            value *= (1.0 + float(ratio))
            applied.append((e, "exercise_ratio", float(ratio)))
        else:
            blockers.append(e)
    return value, applied, blockers


def _event_dict(e, how=None, size=None):
    d = {"exright_date": e["exright_date"], "method_vi": e.get("issue_method_name_vi"),
         "title": e.get("title"), "ratio": e.get("exercise_ratio"),
         "shares_delta": e.get("shares_delta")}
    if how:
        d["applied_via"], d["applied_size"] = how, size
    return d


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
               exercise_ratio, issue_method_name_vi, shares_delta, shares_total_after,
               SUBSTR(event_title_vi, 1, 70) AS title
        FROM `{TABLE}`
        WHERE ticker IN ({tk}) AND event_status = "executed" AND event_code IN ("ISS", "AIS")
        ORDER BY ticker, COALESCE(exright_date, effective_date)
    """)
    return quarters, corp


def _explain_quarterly(q, ais, iss):
    """(ok, verified, reason) — can the last AIS at-or-before `q` be rolled forward INTO `q`?

    This is the gate that makes a restated quarterly row unusable. `ais`/`iss` are already clipped
    to `asof` by the caller, and the primary test looks only at rows dated at or before
    `q["time"]`, so it never consults the future to answer a question about the past.

    Two outcomes short of a clean pass:
      * no AIS at all before `q` — nothing to check against. Rejecting outright would blank out
        every ticker that has never listed additional shares (DHG), which is a coverage loss the
        data does not justify. Admit it, but return `verified=False` so the answer is labelled
        `ANCHOR_UNVERIFIED` rather than passed off as checked — unless an AIS AFTER `q` (still at
        or before `asof`) already carries exactly this value, which is the restatement signature
        with no innocent reading available here.
      * an intervening ISS with no usable size — the expectation cannot be built, so the row
        cannot be cleared. Unverifiable is not the same as verified.
    """
    t, v = q["time"], float(q["OShares"])
    prior = [a for a in ais if a["effective_date"] <= t]
    if not prior:
        hit = [a for a in ais if a["effective_date"] > t
               and abs(float(a["shares_total_after"]) - v) < 1.0]
        if hit:
            return False, False, (
                f"{v:,.0f} trùng ĐÚNG số của AIS {hit[0]['effective_date']} (SAU ngày quý "
                f"{t}) và không có AIS nào trước đó để giải thích ⇒ RESTATE")
        return True, False, "không có AIS nào <= ngày quý ⇒ nhận nhưng KHÔNG kiểm chứng được"
    a = max(prior, key=lambda r: r["effective_date"])
    between = _dedup_iss([e for e in iss if a["effective_date"] < e["exright_date"] <= t])
    expected, _applied, blockers = _roll(float(a["shares_total_after"]), between)
    if blockers:
        return False, False, (f"ISS {[b['exright_date'] for b in blockers]} không có tỉ lệ/"
                              f"shares_delta ⇒ không dựng được kỳ vọng để đối chiếu")
    if abs(v - expected) / expected > EXPLAIN_TOL:
        return False, False, (f"{v:,.0f} không giải thích được từ AIS {a['effective_date']} "
                              f"({float(a['shares_total_after']):,.0f}) + {len(between)} ISS "
                              f"⇒ kỳ vọng {expected:,.0f}, lệch {(v/expected-1)*100:+.2f}% "
                              f"— dấu hiệu số đã bị RESTATE về sau")
    return True, True, ""


def oshares_at(tickers, asof, _cache=None):
    """{ticker: dict} — shares outstanding at `asof`, with the derivation shown.

    Each value carries `value`, `method`, `anchor_date`, `anchor_value`, `anchor_source` and the
    list of ISS events applied, so any number can be re-derived by hand from the output alone.
    `value is None` whenever the method is `UNKNOWN_RATIO` or `NO_ANCHOR` — callers MUST handle
    that; there is no "best effort" number behind it.
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
               and c["exright_date"] and c["exright_date"] <= asof and dilutes_share_count(c)]

        anchors, rejected, unverified = [], [], False
        if ais:
            a = max(ais, key=lambda r: r["effective_date"])
            anchors.append((a["effective_date"], float(a["shares_total_after"]),
                            "corporate_action.AIS"))
        if qs:
            q = max(qs, key=lambda r: r["time"])
            ok, verified, why = _explain_quarterly(q, ais, iss)
            if ok:
                anchors.append((q["time"], float(q["OShares"]), "ticker_financial"))
                unverified = not verified
            else:
                rejected.append({"source": "ticker_financial", "date": q["time"],
                                 "value": float(q["OShares"]), "reason": why})

        if not anchors:
            out[tk] = {"ticker": tk, "asof": asof, "value": None, "method": "NO_ANCHOR",
                       "anchor_date": None, "anchor_value": None, "anchor_source": None,
                       "events_applied": [], "rejected_anchors": rejected,
                       "note": "không có AIS nào <= ngày cần tính, và số quý (nếu có) không "
                               "kiểm chứng được"}
            continue

        # freshest ADMISSIBLE fact wins; AIS breaks a same-date tie (it is a registry statement
        # about the listed count, not a figure copied into a financial statement)
        anchor_date, anchor_value, anchor_src = max(
            anchors, key=lambda a: (a[0], a[2] == "corporate_action.AIS"))

        pending = _dedup_iss([e for e in iss if e["exright_date"] > anchor_date])
        value, applied, blockers = _roll(anchor_value, pending)

        anchor_verified = not (unverified and anchor_src == "ticker_financial")
        base = {"ticker": tk, "asof": asof, "anchor_date": anchor_date,
                "anchor_value": anchor_value, "anchor_source": anchor_src,
                "anchor_verified": anchor_verified, "rejected_anchors": rejected}

        if blockers:
            out[tk] = {**base, "value": None, "method": "UNKNOWN_RATIO",
                       "blocking_events": [_event_dict(b) for b in blockers],
                       "events_applied": [_event_dict(e, h, s) for e, h, s in applied],
                       "note": f"{len(blockers)} sự kiện ISS sau anchor không có exercise_ratio "
                               f"lẫn shares_delta ⇒ KHÔNG trả số (fail-closed)"}
            continue

        if applied and any(h == "exercise_ratio" for _e, h, _s in applied):
            method = "ISS_ESTIMATE"
        elif anchor_src == "corporate_action.AIS":
            method = "AIS_EXACT"           # applied deltas, if any, are exact registry counts
        else:
            method = "ANCHOR_ONLY" if anchor_verified else "ANCHOR_UNVERIFIED"

        out[tk] = {**base, "value": value, "method": method,
                   "events_applied": [_event_dict(e, h, s) for e, h, s in applied]}
    return out


def _selfcheck() -> int:
    fails, ran = [], []

    # counted, never typed: the previous version's summary line said "11/11" while the file
    # actually ran 12 checks. A hand-written total is a number nobody re-derives.
    def check(name, cond, detail=""):
        ran.append(name)
        print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            fails.append(name)

    def fmt(v):
        return f"{v:,.0f}" if v is not None else "None"

    print("== FPT 2025: thưởng CP 15% ex 2025-07-21 → AIS hiệu lực 2025-09-12 ==")
    AIS_TRUTH = 1_703_507_121
    PRE = 1_481_330_122          # AIS 2025-06-19, ground truth trước sự kiện

    cache = _fetch(["FPT"], "2026-08-13")
    series = {}
    for d in ["2025-07-18", "2025-07-20", "2025-07-21", "2025-07-22",
              "2025-08-15", "2025-09-11", "2025-09-12", "2025-10-01"]:
        r = oshares_at(["FPT"], d, _cache=cache)["FPT"]
        series[d] = r
        print(f"  {d}: {fmt(r['value']):>15}  [{r['method']:13s}] anchor={r['anchor_date']}"
              f" ({r['anchor_source']}) +{len(r.get('events_applied', []))} ISS")

    check("1. trước ex-right: bằng ĐÚNG AIS 2025-06-19 (1.481.330.122)",
          series["2025-07-20"]["value"] == PRE, fmt(series['2025-07-20']['value']))
    check("2. ĐÚNG ngày ex-right 07-21: nhảy lên ~1,7 tỷ (không chờ 7 tuần tới AIS)",
          series["2025-07-21"]["value"] is not None
          and abs(series["2025-07-21"]["value"] - AIS_TRUTH) / AIS_TRUTH < 0.001
          and series["2025-07-21"]["method"] == "ISS_ESTIMATE",
          f"{fmt(series['2025-07-21']['value'])} — lệch "
          f"{abs(series['2025-07-21']['value']-AIS_TRUTH)/AIS_TRUTH*100:.4f}%")
    # The series is non-decreasing EXCEPT at the one step where an ISS_ESTIMATE is superseded by
    # a hard number (1.703.529.640 -> 1.703.507.121). That -22.519 is the estimate converging onto
    # truth, not shares disappearing, so the honest assertion is "no MATERIAL decrease, and any
    # decrease must be an estimate giving way to a measured anchor".
    drops = [(a, b) for a, b in zip(list(series)[:-1], list(series)[1:])
             if series[b]["value"] is not None and series[a]["value"] is not None
             and series[b]["value"] < series[a]["value"] - 1e-6]
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
          f"{fmt(series['2025-07-18']['value'])} → {fmt(series['2025-10-01']['value'])}")
    check("4. sau AIS hiệu lực: KHỚP TUYỆT ĐỐI shares_total_after = 1.703.507.121",
          series["2025-09-12"]["value"] == AIS_TRUTH and series["2025-10-01"]["value"] == AIS_TRUTH,
          fmt(series['2025-09-12']['value']))
    check("5. không đếm hai lần: sau AIS không nhân lại ISS đã nằm trong AIS",
          series["2025-10-01"]["events_applied"] == [])
    # the quarterly row dated 07-22 carries the post-bonus count ONE DAY after ex-right. That is
    # genuine early data (the 15% bonus explains it exactly), so the restatement gate must LET IT
    # THROUGH — a gate that rejected everything would pass the HAH test for the wrong reason.
    q722 = oshares_at(["FPT"], "2025-07-22", _cache=cache)["FPT"]
    check("5b. cổng RESTATE không chặn nhầm số quý CÓ căn cứ (FPT 07-22, thưởng 07-21 giải thích)",
          not q722["rejected_anchors"],
          f"rejected={q722['rejected_anchors']}")

    print("== Kiểm chứng ESOP (loại KHÔNG điều chỉnh giá nhưng VẪN tăng số CP) ==")
    r = oshares_at(["FPT"], "2025-06-18", _cache=cache)["FPT"]
    print(f"  2025-06-18 (trước AIS 06-19): {fmt(r['value']):>15} [{r['method']}] "
          f"+{len(r.get('events_applied', []))} ISS")
    check("6. lăn qua 2 đợt ESOP 2025-05-07 ⇒ khớp AIS 06-19 trong 0,01%",
          r["value"] is not None and abs(r["value"] - PRE) / PRE < 0.0001
          and len(r["events_applied"]) == 2,
          f"{fmt(r['value'])} vs {PRE:,.0f}")
    check("7. hai đợt ESOP cùng ngày, KHÁC tỉ lệ ⇒ giữ CẢ HAI (không dedup nhầm)",
          sorted(e["applied_size"] for e in r["events_applied"]) == [0.00225, 0.00472])

    # ------------------------------------------------------------------ HỒI QUY: 2 lỗi đã đo
    print("== HỒI QUY VIỆC B — HAH: số quý RESTATE + ISS không có tỉ lệ ==")
    hcache = _fetch(["HAH"], "2026-08-13")

    # (1) look-ahead: the 2026-02-02 quarterly row already carries 185.840.401, a count created by
    # the 2026-03-12 conversion + 2026-04-17 ESOP and only listed by the AIS of 2026-05-27.
    h = oshares_at(["HAH"], "2026-03-01", _cache=hcache)["HAH"]
    print(f"  2026-03-01: {fmt(h['value'])} [{h['method']}] anchor={h['anchor_date']} "
          f"({h['anchor_source']}) rejected={len(h['rejected_anchors'])}")
    for rj in h["rejected_anchors"]:
        print(f"     ⛔ loại anchor {rj['source']} {rj['date']} = {rj['value']:,.0f}: {rj['reason']}")
    check("H1. 2026-03-01 KHÔNG trả 185.840.401 (số của AIS 2026-05-27 — look-ahead 115 ngày)",
          h["value"] != 185_840_401, fmt(h["value"]))
    check("H2. 2026-03-01 trả ĐÚNG 168.861.212 (AIS 2025-09-09, chưa có sự kiện nào sau đó)",
          h["value"] == 168_861_212 and h["anchor_source"] == "corporate_action.AIS",
          f"{fmt(h['value'])} anchor={h['anchor_date']} ({h['anchor_source']})")
    check("H3. lý do loại anchor được NÊU RA, không im lặng",
          any(r["source"] == "ticker_financial" and r["value"] == 185_840_401
              for r in h["rejected_anchors"]))

    # (2) fail-closed: two convertible-bond conversions carry exercise_ratio = 0.0 and no
    # shares_delta. The old code multiplied by 1.0 and stamped ISS_ESTIMATE on the result.
    for d, exr in (("2025-03-25", "2025-03-20"), ("2026-03-13", "2026-03-12")):
        hh = oshares_at(["HAH"], d, _cache=hcache)["HAH"]
        print(f"  {d}: {fmt(hh['value'])} [{hh['method']}] "
              f"blocking={[b['exright_date'] for b in hh.get('blocking_events', [])]}")
        check(f"H4/{d}. chuyển đổi TP {exr} (ratio 0,0, không shares_delta) ⇒ UNKNOWN_RATIO, "
              f"value=None — KHÔNG âm thầm nhân 1,0",
              hh["value"] is None and hh["method"] == "UNKNOWN_RATIO"
              and any(b["exright_date"] == exr for b in hh["blocking_events"]),
              f"value={fmt(hh['value'])} method={hh['method']}")

    print("== HỒI QUY VIỆC B — 'Phát hành riêng lẻ' (2.187/2.280 dòng ratio 0/NULL) ==")
    pp = bq(f"""
        SELECT ticker, CAST(exright_date AS STRING) exright_date
        FROM `{TABLE}`
        WHERE event_code = "ISS" AND event_status = "executed"
          AND issue_method_name_vi = "Phát hành riêng lẻ"
          AND (exercise_ratio IS NULL OR exercise_ratio = 0) AND shares_delta IS NULL
          AND exright_date BETWEEN DATE "2025-01-01" AND DATE "2026-06-30"
        ORDER BY exright_date DESC LIMIT 1
    """)
    check("P0. tìm được ít nhất 1 ca 'Phát hành riêng lẻ' thật để kiểm (test không rỗng)",
          bool(pp), str(pp))
    if pp:
        tkp, exrp = pp[0]["ticker"], pp[0]["exright_date"]
        after = (__import__("datetime").date.fromisoformat(exrp)
                 + __import__("datetime").timedelta(days=1)).isoformat()
        p = oshares_at([tkp], after)[tkp]
        print(f"  {tkp} {after}: {fmt(p['value'])} [{p['method']}] "
              f"blocking={[b['exright_date'] for b in p.get('blocking_events', [])]}")
        check(f"P1. {tkp} ngay sau phát hành riêng lẻ {exrp} ⇒ UNKNOWN_RATIO, value=None",
              p["value"] is None and p["method"] == "UNKNOWN_RATIO"
              and any(b["exright_date"] == exrp for b in p["blocking_events"]),
              f"value={fmt(p['value'])} method={p['method']}")

    print("== Ca đối chứng: không có sự kiện sau anchor ⇒ KHÔNG được đụng vào số anchor ==")
    ctrl = oshares_at(["DHG", "PVT", "TCB", "ACB", "HDB"], "2026-08-12")
    for tk, r in sorted(ctrl.items()):
        print(f"  {tk}: {fmt(r['value']):>15} [{r['method']:17s}] anchor={r['anchor_date']}"
              f" ({r['anchor_source']}) +{len(r.get('events_applied', []))} ISS")
    # coverage must not be bought with a false label: DHG has no AIS at all, so its quarterly
    # anchor cannot be cleared — it is returned, and it says so.
    check("8d. mã không có AIS nào ⇒ vẫn trả số nhưng gắn nhãn ANCHOR_UNVERIFIED",
          ctrl["DHG"]["value"] is not None and ctrl["DHG"]["method"] == "ANCHOR_UNVERIFIED"
          and ctrl["DHG"]["anchor_verified"] is False,
          f"{fmt(ctrl['DHG']['value'])} [{ctrl['DHG']['method']}]")
    # property, not an assumption about which tickers happen to be event-free — the earlier
    # version hardcoded "PVT has no events", which was simply false and masked a real bug
    check("8. mọi mã không có ISS sau anchor ⇒ value == anchor_value TUYỆT ĐỐI",
          all(r["value"] == r["anchor_value"]
              for r in ctrl.values() if r["value"] is not None and not r["events_applied"]))
    check("8b. có ít nhất 1 mã đối chứng thật sự không sự kiện (test không rỗng)",
          any(r.get("events_applied") == [] and r["value"] is not None for r in ctrl.values()),
          f"{[t for t, r in ctrl.items() if r.get('events_applied') == []]}")
    # regression: the bq CLI truncates at 100 rows by default; batching several tickers used to
    # silently drop the newest quarters and fall back to a year-old anchor (fixed in
    # corp_action_lib.bq via --max_rows). Batched must equal one-at-a-time, always.
    solo = {t: oshares_at([t], "2026-08-12")[t] for t in ctrl}
    check("8c. gọi theo LÔ == gọi từng mã (không bị bq cắt 100 dòng)",
          all(ctrl[t]["value"] == solo[t]["value"]
              and ctrl[t].get("anchor_date") == solo[t].get("anchor_date") for t in ctrl),
          "; ".join(f"{t}: lô {ctrl[t].get('anchor_date')} vs đơn {solo[t].get('anchor_date')}"
                    for t in ctrl if ctrl[t].get("anchor_date") != solo[t].get("anchor_date"))
          or "khớp hết")

    print("== MBB: 2 đợt CÙNG NGÀY 2026-08-11 (quyền mua 10% + cổ tức CP 15%) ==")
    m = oshares_at(["MBB"], "2026-08-12")["MBB"]
    print(f"  {fmt(m['value'])} [{m['method']}] anchor={m['anchor_date']} "
          f"({m['anchor_source']}) events="
          f"{[(e['exright_date'], e.get('applied_size')) for e in m.get('events_applied', [])]}")
    check("9. cộng CẢ HAI đợt cùng ngày (×1,10×1,15), không gộp thành một",
          sorted(e["applied_size"] for e in m.get("events_applied", [])
                 if e["exright_date"] == "2026-08-11") == [0.1, 0.15])

    print("== Bất biến chung: value is None ⟺ method ∈ {UNKNOWN_RATIO, NO_ANCHOR} ==")
    every = [h, m, *ctrl.values(), *series.values()]
    check("10. không bao giờ trả số kèm nhãn 'không biết', và ngược lại",
          all((r["value"] is None) == (r["method"] in ("UNKNOWN_RATIO", "NO_ANCHOR"))
              for r in every))

    print()
    if fails:
        print(f"FAILED {len(fails)}/{len(ran)}: {fails}")
        return 1
    print(f"OK — oshares_live selfcheck PASS {len(ran)}/{len(ran)}")
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
