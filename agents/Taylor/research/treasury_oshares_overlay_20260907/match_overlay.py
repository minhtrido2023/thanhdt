#!/usr/bin/env python3
"""
Treasury-buyback OShares PIT overlay — matches consecutive-quarter OShares deltas in
ticker_financial to buy_done/sell_done events in treasury_news, to recover a TRUE effective
date (news public_date) for the share-count change instead of the (too-early) quarter filing
date. Magnitude source = ticker_financial delta (treasury_news.shares_delta only 24% populated,
ref_price 100% NULL). Overlay only — does not touch ticker_financial or oshares_live.py.
"""
import csv
import os
from collections import defaultdict
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))

WINDOW_BEFORE_PREV_DAYS = 10
WINDOW_AFTER_CURR_DAYS = 150
MIN_DELTA_ABS = 1000  # ignore sub-1000-share noise/rounding

def parse_date(s):
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))

def load_oshares(path):
    by_ticker = defaultdict(list)
    with open(path) as f:
        r = csv.DictReader(f)
        for row in r:
            by_ticker[row["ticker"]].append(
                (parse_date(row["time"]), row["quarter"], float(row["OShares"]))
            )
    for t in by_ticker:
        by_ticker[t].sort(key=lambda x: x[0])
    return by_ticker

def load_events(path):
    """Collapse duplicate press rows for the SAME (ticker, date, action_type) into one logical
    event — treasury_news carries multiple news-source rows for one real corporate action, and
    treating each row as independently consumable lets two unrelated OShares deltas both claim
    'a match' against what is really a single event (caught by self-check (a) on CTD 2018-02-06)."""
    raw = defaultdict(list)
    with open(path) as f:
        r = csv.DictReader(f)
        for row in r:
            sd = row["shares_delta"]
            raw[(row["ticker"], row["public_date"], row["action_type"])].append(
                {"shares_delta": float(sd) if sd else None, "title": row["title"]}
            )
    by_ticker = defaultdict(list)
    for (ticker, dstr, action), rows in raw.items():
        shares_delta = next((r["shares_delta"] for r in rows if r["shares_delta"] is not None), None)
        by_ticker[ticker].append(
            {
                "date": parse_date(dstr),
                "action_type": action,
                "shares_delta": shares_delta,
                "title": " | ".join(r["title"] for r in rows),
                "n_press_rows": len(rows),
                "used": False,
            }
        )
    for t in by_ticker:
        by_ticker[t].sort(key=lambda e: e["date"])
    return by_ticker

MAGNITUDE_TOL_PCT = 25

def _base_row(ticker, prev_q, curr_q, prev_date, curr_date, prev_v, curr_v, delta, direction):
    return dict(
        ticker=ticker, prev_quarter=prev_q, curr_quarter=curr_q,
        prev_filing_date=prev_date, curr_filing_date=curr_date,
        prev_oshares=prev_v, curr_oshares=curr_v, delta=delta, direction=direction,
        matched=False, effective_date=None, matched_action=None,
        matched_shares_delta=None, magnitude_diff_pct=None, confidence=None, n_candidates=0,
    )

def _candidates(evs, want_action, win_start, win_end):
    return [
        e for e in evs
        if not e["used"] and e["action_type"] == want_action and win_start <= e["date"] <= win_end
    ]

def match(oshares_ts, events_ts):
    # build one delta-record per (ticker, quarter transition), keep ticker/window/direction fixed
    deltas = []
    for ticker, rows in oshares_ts.items():
        evs = events_ts.get(ticker, [])
        if not evs:
            continue
        for i in range(1, len(rows)):
            prev_date, prev_q, prev_v = rows[i - 1]
            curr_date, curr_q, curr_v = rows[i]
            delta = curr_v - prev_v
            if abs(delta) < MIN_DELTA_ABS:
                continue
            direction = "buy" if delta < 0 else "sell"
            want_action = "buy_done" if direction == "buy" else "sell_done"
            win_start = prev_date - timedelta(days=WINDOW_BEFORE_PREV_DAYS)
            win_end = curr_date + timedelta(days=WINDOW_AFTER_CURR_DAYS)
            row = _base_row(ticker, prev_q, curr_q, prev_date, curr_date, prev_v, curr_v, delta, direction)
            row["_evs"] = evs
            row["_want_action"] = want_action
            row["_win"] = (win_start, win_end)
            deltas.append(row)

    # Pass 1 — magnitude-confirmed (shares_delta present, within tolerance). Process the
    # tightest magnitude matches first so a good match wins any window-overlap contention.
    pass1_scored = []
    for row in deltas:
        cands = _candidates(row["_evs"], row["_want_action"], *row["_win"])
        for c in cands:
            if c["shares_delta"] is None:
                continue
            diff = abs(abs(c["shares_delta"]) - abs(row["delta"])) / abs(row["delta"]) * 100
            if diff <= MAGNITUDE_TOL_PCT:
                pass1_scored.append((diff, row, c))
    pass1_scored.sort(key=lambda x: x[0])
    for diff, row, c in pass1_scored:
        if row["matched"] or c["used"]:
            continue
        c["used"] = True
        row.update(
            matched=True, effective_date=c["date"], matched_action=c["action_type"],
            matched_shares_delta=c["shares_delta"], magnitude_diff_pct=diff, confidence="HIGH",
            n_candidates=1,
        )

    # Pass 2 — direction+window only (no/unusable shares_delta). Require the delta's candidate
    # set (after pass-1 consumption) to be exactly one event, else leave unmatched/ambiguous
    # rather than guess which delta a shared event really belongs to.
    for row in deltas:
        if row["matched"]:
            continue
        cands = _candidates(row["_evs"], row["_want_action"], *row["_win"])
        row["n_candidates"] = len(cands)
        if len(cands) == 1:
            c = cands[0]
            c["used"] = True
            mag_diff = None
            if c["shares_delta"] is not None:
                mag_diff = abs(abs(c["shares_delta"]) - abs(row["delta"])) / abs(row["delta"]) * 100
            row.update(
                matched=True, effective_date=c["date"], matched_action=c["action_type"],
                matched_shares_delta=c["shares_delta"], magnitude_diff_pct=mag_diff, confidence="MEDIUM",
            )

    for row in deltas:
        row.pop("_evs", None)
        row.pop("_want_action", None)
        row.pop("_win", None)
    return deltas

def main():
    oshares_ts = load_oshares(os.path.join(HERE, "oshares_timeseries.csv"))
    events_ts = load_events(os.path.join(HERE, "treasury_events.csv"))

    results = match(oshares_ts, events_ts)

    matched = [r for r in results if r["matched"]]
    unmatched = [r for r in results if not r["matched"]]

    # Post-hoc sanity cap: a MEDIUM match (no shares_delta corroboration) whose delta is a large
    # fraction of prior OShares is more likely a mis-tagged bonus-issue/other event grabbing an
    # unrelated buy_done/sell_done nearby than a real buyback of that size (VN treasury programs
    # actually completed in one quarter are typically single-digit % of float — see MCH false
    # positive: 22.6% jump was really a treasury-share stock-dividend + new issuance tagged
    # action_type='other', outside the buy_done/sell_done candidate pool). Downgrade instead of
    # dropping — still worth surfacing for manual review, just not trusted as-is.
    SUSPECT_RATIO_PCT = 15.0
    for r in results:
        if r["matched"] and r["confidence"] == "MEDIUM" and r["prev_oshares"] > 0:
            ratio = abs(r["delta"]) / r["prev_oshares"] * 100
            r["delta_pct_of_prev_oshares"] = ratio
            if ratio > SUSPECT_RATIO_PCT:
                r["confidence"] = "SUSPECT"
        else:
            r["delta_pct_of_prev_oshares"] = (
                abs(r["delta"]) / r["prev_oshares"] * 100 if r["prev_oshares"] > 0 else None
            )

    out_path = os.path.join(HERE, "overlay_results.csv")
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "ticker", "prev_quarter", "curr_quarter", "prev_filing_date", "curr_filing_date",
                "prev_oshares", "curr_oshares", "delta", "delta_pct_of_prev_oshares", "direction",
                "matched", "effective_date", "matched_action", "matched_shares_delta",
                "magnitude_diff_pct", "confidence", "n_candidates",
            ]
        )
        for r in results:
            w.writerow(
                [
                    r["ticker"], r["prev_quarter"], r["curr_quarter"], r["prev_filing_date"],
                    r["curr_filing_date"], f"{r['prev_oshares']:.0f}", f"{r['curr_oshares']:.0f}",
                    f"{r['delta']:.0f}",
                    f"{r['delta_pct_of_prev_oshares']:.1f}" if r["delta_pct_of_prev_oshares"] is not None else "",
                    r["direction"], r["matched"],
                    r["effective_date"], r["matched_action"], r["matched_shares_delta"],
                    f"{r['magnitude_diff_pct']:.1f}" if r["magnitude_diff_pct"] is not None else "",
                    r["confidence"], r["n_candidates"],
                ]
            )

    tickers_all = sorted(set(r["ticker"] for r in results))
    tickers_matched = sorted(set(r["ticker"] for r in matched))
    tickers_unmatched_only = sorted(set(r["ticker"] for r in unmatched) - set(tickers_matched))

    # Per-ticker classification for tickers_{handled,suspect,unexplained}.txt — derived here
    # (not by a separate ad-hoc shell command) so the 3 output files stay reproducible from a
    # single `python3 match_overlay.py` run. handled = >=1 delta matched HIGH/MEDIUM; suspect =
    # matched deltas exist but ALL got downgraded to SUSPECT; unexplained = 0 matched deltas.
    confs_by_ticker = defaultdict(list)
    for r in results:
        if r["matched"]:
            confs_by_ticker[r["ticker"]].append(r["confidence"])
    tickers_handled, tickers_suspect_only, tickers_unexplained = [], [], []
    for t in tickers_all:
        confs = confs_by_ticker.get(t, [])
        if any(c in ("HIGH", "MEDIUM") for c in confs):
            tickers_handled.append(t)
        elif confs:
            tickers_suspect_only.append(t)
        else:
            tickers_unexplained.append(t)

    for fname, tickers in (
        ("tickers_handled.txt", tickers_handled),
        ("tickers_suspect.txt", tickers_suspect_only),
        ("tickers_unexplained.txt", tickers_unexplained),
    ):
        with open(os.path.join(HERE, fname), "w") as f:
            f.write("\n".join(tickers) + "\n" if tickers else "")
    print(
        f"\nwrote tickers_handled.txt ({len(tickers_handled)}) / "
        f"tickers_suspect.txt ({len(tickers_suspect_only)}) / "
        f"tickers_unexplained.txt ({len(tickers_unexplained)})"
    )

    print(f"total quarter-pair deltas evaluated: {len(results)}")
    print(f"matched: {len(matched)}  unmatched: {len(unmatched)}")
    print(f"tickers with >=1 nontrivial delta: {len(tickers_all)}")
    print(f"tickers with >=1 matched delta: {len(tickers_matched)}")
    print(f"tickers with ALL deltas unmatched: {len(tickers_unmatched_only)}")
    conf_counts = defaultdict(int)
    for r in matched:
        conf_counts[r["confidence"]] += 1
    print("confidence breakdown:", dict(conf_counts))

    # self-checks
    print("\n--- self-check (a): no event used twice ---")
    used_events = defaultdict(list)
    for t, evs in events_ts.items():
        for e in evs:
            if e["used"]:
                used_events[(t, e["date"], e["action_type"])].append(e)
    dupes = {k: v for k, v in used_events.items() if len(v) > 1}
    print("PASS (0 dupes)" if not dupes else f"FAIL: {dupes}")

    print("\n--- self-check (b): sign consistency ---")
    bad_sign = [
        r for r in matched
        if (r["direction"] == "buy" and r["delta"] >= 0)
        or (r["direction"] == "sell" and r["delta"] <= 0)
    ]
    print("PASS (0 violations)" if not bad_sign else f"FAIL: {bad_sign}")

    print("\n--- self-check (c): VRE resolves to 2019-12-19 (buy_done), not 2019-10-29 ---")
    vre = [r for r in results if r["ticker"] == "VRE"]
    for r in vre:
        print(r["ticker"], r["curr_quarter"], "delta=", r["delta"], "eff_date=", r["effective_date"], "conf=", r["confidence"])

    print(f"\nwrote {out_path}")

if __name__ == "__main__":
    main()
