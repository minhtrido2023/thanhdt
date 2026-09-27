#!/usr/bin/env python3
"""PROTOTYPE (R&D, NOT production) — self-computed back-adjustment factor from tav2_bq.corporate_action.

Question: when `tav2_bq.ticker.Close` carries an INCOMPLETE corp-action back-adjustment (FPT
2026-09-21 bonus 10%: factor applied to only 4 sessions 09-15..09-18, missing on all of
2026-06-22..2026-09-14), can we recompute the factor OURSELVES from the corp-action table and
(a) DETECT the gap, (b) REPAIR the Close series — without waiting for the vendor backfill?

Definitions (sign conventions measured against real vendor data, not assumed):
  r_obs(t)  = Price(t) / Close(t)                      -- vendor-implied cumulative factor
  r_pred(t) = PROD over price-adjusting events e with exright_date(e) > t of f_e
  f_e       = 1 + exercise_ratio            for ISS bonus / stock dividend
            = P_cum / (P_cum - value_per_share)  for DIV cash (P_cum = raw close, last cum session)
  Close_self(t) = Price(t) / r_pred(t)

Taxonomy is REUSED from corp_action_lib.is_price_adjusting (ESOP / private placement do NOT
adjust price) -- not re-derived here. The multiplier helpers in daily_nav_snapshot.py
(confirmed_qty_multiplier_after / confirmed_share_event_multiplier) are QUANTITY multipliers for
the account side and are deliberately NOT reused: they return 1.0 for DIV by design, which is
correct for share counts and wrong for a price factor.

Usage:
  python3 selfcomp_adjfactor.py fpt
  python3 selfcomp_adjfactor.py control [--since 2026-01-01] [--min-adv 5e10]
  python3 selfcomp_adjfactor.py coverage
"""
import argparse
import subprocess
import sys
from collections import defaultdict
from datetime import date, timedelta

WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
import corp_action_lib as cal  # noqa: E402

BQ = cal.BQ_PROJECT
TOL = 0.001          # 0,1% — nguong "khop gan tuyet doi" theo dispatch
PRICE_BAND_SLACK = 1e-9


# ---------------------------------------------------------------- data access

def price_rows(tickers, start, end):
    """Raw+adjusted price series. `Price` = unadjusted (cafef GiaDongCua), `Close` = back-adjusted.

    High/Low come along because `ticker.Price` can be a silent forward-fill of T-1 on the ex-date
    row (ticker_price_stale_on_exdate.md, VHM 2026-08-06) -- the only self-contained detector is
    `Low <= Price <= High`. A factor computed off a ffilled Price is wrong by the whole factor.
    """
    tk = ",".join(f'"{t}"' for t in sorted(set(tickers)))
    return cal.bq(f"""
        SELECT t.ticker AS tk, CAST(t.time AS STRING) AS d,
               t.Close AS close, t.Price AS price, t.High AS hi, t.Low AS lo, t.Volume AS vol
        FROM `{BQ}.tav2_bq.ticker` AS t
        WHERE t.ticker IN ({tk}) AND t.time BETWEEN DATE "{start}" AND DATE "{end}"
          AND t.Close > 0 AND t.Price > 0
        ORDER BY t.ticker, t.time
    """)


def series_by_ticker(rows):
    out = defaultdict(list)
    for r in rows:
        out[r["tk"]].append({
            "d": r["d"], "close": float(r["close"]), "price": float(r["price"]),
            "hi": float(r["hi"] or 0), "lo": float(r["lo"] or 0), "vol": float(r["vol"] or 0),
        })
    return out


# ------------------------------------------------------------ factor building

def price_stale_suspect(series, idx):
    """True when `Price` cannot be a real trade of that session (VHM-class ffill signature).

    `High`/`Low` live in the BACK-ADJUSTED frame (same as `Close`), `Price` does not -- comparing
    them directly reports every pre-event session as broken (measured: FPT 2025-06-11 Price=117900
    vs adjusted band [97750,99520], a perfectly healthy row). The band must be lifted into the raw
    frame first, and the lifting ratio must come from a NEIGHBOUR row, never from the suspect row
    itself: on a ffilled row `Price/Close` is exactly the quantity that broke. The previous session
    is the right neighbour here because the bar we test is always a CUM session, so its predecessor
    shares the same adjustment regime (an ex-date row would not).
    """
    bar = series[idx]
    if bar["hi"] <= 0 or bar["lo"] <= 0 or idx == 0:
        return False
    prev = series[idx - 1]
    if prev["close"] <= 0:
        return False
    r_ref = prev["price"] / prev["close"]
    lo, hi = bar["lo"] * r_ref, bar["hi"] * r_ref
    return not (lo * (1 - 1e-6) <= bar["price"] <= hi * (1 + 1e-6))


def group_price_factor(ex, evs, series):
    """(factor, note) for ALL price-adjusting events sharing one ex-date. None = cannot compute.

    Same-day events must be combined INSIDE the exchange's reference-price formula, never
    multiplied as independent factors:

        P_ref = (P_cum - D_total) / (1 + q_total)      ->   f = (1 + q_total) * P_cum / (P_cum - D)

    Measured proof that multiplying is wrong, on two different event shapes:
      GEX 2026-05-05 (bonus 20% + stock dividend 25%): sum 1+0.45 = 1.450 matches the vendor's
        1.450191; the product 1.20*1.25 = 1.500 is off by -3.32%.
      DGC 2026-09-14 (cash 3.000 + cash 5.000 on raw 46.750): 46750/38750 = 1.206452 matches the
        vendor's 1.206452 to 6 decimals; the product of the two single-dividend factors gives
        1.196544, off by +0.83%.
    Both would have been reported as vendor defects by the naive version of this function -- i.e.
    the compounding bug manufactures false accusations, the most expensive kind of error here.

    A cash dividend's denominator needs the RAW (unadjusted) price of the last cum session, so the
    ffill guard applies; a pure stock event needs no price at all and stays computable even when
    the price row is unusable.
    """
    q_total, d_total, kinds = 0.0, 0.0, []
    for ev in evs:
        code = ev["event_code"]
        method = (ev.get("issue_method_name_vi") or "").strip()
        if code == "ISS":
            if method == "Quyền mua CP cho Cổ đông hiện hữu":
                return None, (f"{ex} ISS rights issue: subscription price is NOT a column of "
                              f"corporate_action -> factor unknowable from our data")
            try:
                ratio = float(ev.get("exercise_ratio") or 0.0)
            except (TypeError, ValueError):
                return None, f"{ex} ISS exercise_ratio unparsable"
            if ratio <= 0:
                return None, f"{ex} ISS exercise_ratio<=0"
            q_total += ratio
            kinds.append(f"ISS {method} {ratio:g}")
        elif code == "DIV":
            try:
                dps = float(ev.get("value_per_share") or 0.0)
            except (TypeError, ValueError):
                return None, f"{ex} DIV value_per_share unparsable"
            if dps <= 0:
                return None, f"{ex} DIV value_per_share<=0"
            d_total += dps
            kinds.append(f"DIV {dps:g}d")
        else:
            return None, f"{ex} unsupported event_code={code}"

    desc = " + ".join(kinds)
    if d_total <= 0:
        return 1.0 + q_total, f"{ex} {desc} -> f={1.0 + q_total:.6f} (no cash leg)"

    idxs = [i for i, b in enumerate(series) if b["d"] < ex]
    if not idxs:
        return None, f"{ex} {desc}: no cum session inside the price window"
    idx = idxs[-1]
    bar = series[idx]
    if price_stale_suspect(series, idx):
        return None, (f"{ex} {desc}: last cum bar {bar['d']} Price={bar['price']:.0f} outside the "
                      f"raw-lifted band -> ffill suspect, refuse")
    p_cum = bar["price"]
    if p_cum - d_total <= 0:
        return None, f"{ex} {desc}: cash {d_total:.0f} >= raw price {p_cum:.0f}"
    f = (1.0 + q_total) * p_cum / (p_cum - d_total)
    return f, (f"{ex} {desc} on raw {p_cum:.0f} ({bar['d']}) -> f={f:.6f}")


def build_factor_curve(ticker, series, events):
    """r_pred(d) for every d in `series`, plus per-event provenance.

    r_pred(t) = product over EX-DATES strictly after t of that date's combined factor. Grouping by
    ex-date first is not a tidiness choice -- see `group_price_factor`.

    Duplicate rows on one (ex-date, code) are deduped on the ECONOMIC term only. corporate_action
    legitimately holds several tranches on one day (registry Bẫy 3) and those must sum, but a
    re-stated amendment of the same tranche must not double-count. Identical (code, ratio, dps)
    rows are indistinguishable from each other, so treating them as one term is the conservative
    read; it is also what matched the vendor on every control event with duplicates.
    """
    notes, unknown, used = [], [], []
    by_ex = defaultdict(list)
    for ev in events:
        if not cal.is_price_adjusting(ev):
            notes.append(f"{ev['exright_date']} {ev['event_code']} "
                         f"{(ev.get('issue_method_name_vi') or '').strip()!r}: NON price-adjusting")
            continue
        by_ex[ev["exright_date"]].append(ev)

    for ex in sorted(by_ex):
        seen, uniq = set(), []
        for ev in by_ex[ex]:
            key = (ev["event_code"], str(ev.get("exercise_ratio")), str(ev.get("value_per_share")))
            if key in seen:
                notes.append(f"{ex} {ev['event_code']}: identical economic term repeated, dropped")
                continue
            seen.add(key)
            uniq.append(ev)
        f, note = group_price_factor(ex, uniq, series)
        notes.append(note)
        if f is None:
            unknown.append(ex)
        else:
            used.append((ex, f))

    curve, acc = {}, 1.0
    ex_after = sorted(used, key=lambda x: x[0], reverse=True)
    i = 0
    for bar in sorted(series, key=lambda b: b["d"], reverse=True):
        while i < len(ex_after) and ex_after[i][0] > bar["d"]:
            acc *= ex_after[i][1]
            i += 1
        curve[bar["d"]] = acc
    return curve, used, notes, unknown


def load_window(tks, since, end, lookback_days=25):
    """Prices from `since - lookback_days`, events strictly after `since`.

    Events with an ex-date BEFORE the price window are irrelevant to r(t) inside it (they are in
    the past for every t), but an event right at the left edge still needs its LAST CUM session,
    which lies before `since`. Loading events from an earlier date than the prices is the bug that
    made 44/46 control tickers report UNCOMPUTABLE on the first run -- a fail-closed that was an
    artifact of the window, not of the data.
    """
    p_start = (date.fromisoformat(since) - timedelta(days=lookback_days)).isoformat()
    series = series_by_ticker(price_rows(tks, p_start, end))
    by_tk = defaultdict(list)
    for e in cal.events(tks, since=since, until=end):
        by_tk[e["ticker"]].append(e)
    return series, by_tk


def segments(series, keyfn, tol=5e-4):
    """Collapse a per-day value into constant runs (so a 200-row table reads as 5 lines)."""
    out, prev = [], None
    for bar in series:
        v = keyfn(bar)
        if prev is None or abs(v / prev[-1]["v"] - 1.0) > tol:
            out.append([{"d": bar["d"], "v": v}])
        else:
            out[-1].append({"d": bar["d"], "v": v})
        prev = out[-1]
    return [{"d0": s[0]["d"], "d1": s[-1]["d"], "n": len(s),
             "v_min": min(x["v"] for x in s), "v_max": max(x["v"] for x in s)} for s in out]


def cmd_fpt(args):
    tk, start, end = "FPT", "2025-01-01", args.end
    series = series_by_ticker(price_rows([tk], start, end))[tk]
    events = cal.events([tk], since="2024-12-31", until=end)
    curve, used, notes, unknown = build_factor_curve(tk, series, events)

    print(f"=== FPT  {series[0]['d']} .. {series[-1]['d']}  ({len(series)} sessions) ===\n")
    print("-- events read from tav2_bq.corporate_action (executed only) --")
    for n in notes:
        print(f"   {n}")
    print(f"\n   factors USED: {len(used)}   UNKNOWN (fail-closed): {unknown or 'none'}\n")

    print("-- r_obs = Price/Close (vendor)  vs  r_pred = self-computed --")
    print(f"{'d0':<12}{'d1':<12}{'n':>4}  {'r_obs':>10}  {'r_pred':>10}  {'ratio-1':>10}  verdict")
    worst = None
    for seg in segments(series, lambda b: b["price"] / b["close"]):
        r_obs = (seg["v_min"] + seg["v_max"]) / 2
        r_pred = curve[seg["d0"]]
        dev = r_obs / r_pred - 1.0
        vd = "OK" if abs(dev) <= TOL else "MISMATCH"
        if worst is None or abs(dev) > abs(worst[1]):
            worst = (seg, dev)
        print(f"{seg['d0']:<12}{seg['d1']:<12}{seg['n']:>4}  {r_obs:>10.6f}  {r_pred:>10.6f}"
              f"  {dev:>+10.4%}  {vd}")

    print("\n-- repair on the mismatching window: Close_self = Price / r_pred --")
    print(f"{'date':<12}{'Price':>10}{'Close_obs':>12}{'Close_self':>12}{'delta':>10}")
    bad = [b for b in series if abs((b["price"] / b["close"]) / curve[b["d"]] - 1.0) > TOL]
    for b in ([bad[0], bad[len(bad) // 2], bad[-1]] if len(bad) >= 3 else bad):
        cs = b["price"] / curve[b["d"]]
        print(f"{b['d']:<12}{b['price']:>10.0f}{b['close']:>12.2f}{cs:>12.2f}"
              f"{cs / b['close'] - 1.0:>+10.4%}")
    print(f"\n   mismatching sessions: {len(bad)} / {len(series)}"
          f"   window: {bad[0]['d'] if bad else '-'} .. {bad[-1]['d'] if bad else '-'}")
    if worst:
        print(f"   worst segment deviation: {worst[1]:+.4%} "
              f"({worst[0]['d0']}..{worst[0]['d1']})")


def liquid_tickers(since, end, min_adv, limit):
    rows = cal.bq(f"""
        SELECT t.ticker AS tk, AVG(t.Close * t.Volume) AS adv
        FROM `{BQ}.tav2_bq.ticker` AS t
        WHERE t.time BETWEEN DATE "{since}" AND DATE "{end}" AND t.Close > 0 AND t.Volume > 0
          AND t.ticker != "VNINDEX"
        GROUP BY t.ticker HAVING adv >= {min_adv}
        ORDER BY adv DESC LIMIT {limit}
    """)
    return [r["tk"] for r in rows]


def cmd_control(args):
    """Cross-check on tickers OTHER than the known-bad case: does r_pred reproduce r_obs?"""
    tks = liquid_tickers(args.since, args.end, args.min_adv, args.limit)
    print(f"control universe: {len(tks)} tickers, ADV >= {args.min_adv:.3g} VND, "
          f"{args.since}..{args.end}\n")
    series, by_tk = load_window(tks, args.since, args.end)

    rows_out, n_unk = [], 0
    unk_rows = []
    for tk in sorted(series):
        s = series[tk]
        curve, used, _notes, unknown = build_factor_curve(tk, s, by_tk.get(tk, []))
        if unknown:
            n_unk += 1
            unk_rows.append((tk, unknown))
            continue
        s = [b for b in s if b["d"] >= args.since]
        devs = [(b["d"], (b["price"] / b["close"]) / curve[b["d"]] - 1.0) for b in s]
        bad = [d for d, x in devs if abs(x) > TOL]
        # longest CONSECUTIVE run of bad sessions -- separates the two defect classes. A single
        # stale `Price` row (documented VHM class) is 1-2 days; an incomplete back-adjustment
        # window is tens to hundreds. Lumping them hides the one we are trying to detect.
        idx = {b["d"]: i for i, b in enumerate(s)}
        run = best = 0
        prev = None
        for d in bad:
            run = run + 1 if prev is not None and idx[d] == idx[prev] + 1 else 1
            best = max(best, run)
            prev = d
        mx = max((abs(x) for _d, x in devs), default=0.0)
        med_bad = sorted(abs(x) for d, x in devs if abs(x) > TOL)
        rows_out.append({
            "tk": tk, "max": mx, "n_bad": len(bad), "n": len(s), "run": best,
            "n_ex": len([1 for d, _f in used if args.since < d <= args.end]),
            "med_bad": med_bad[len(med_bad) // 2] if med_bad else 0.0,
            "cls": ("AGREE" if not bad else "GLITCH_1_2D" if best <= 2 else "WINDOW_MISMATCH"),
        })

    by_cls = defaultdict(list)
    for r in rows_out:
        by_cls[r["cls"]].append(r)
    print(f"tickers evaluated               : {len(rows_out)}")
    print(f"  AGREE (no day off by >{TOL:.1%})   : {len(by_cls['AGREE'])}")
    print(f"  GLITCH_1_2D (isolated rows)   : {len(by_cls['GLITCH_1_2D'])}")
    print(f"  WINDOW_MISMATCH (>=3d run)    : {len(by_cls['WINDOW_MISMATCH'])}")
    print(f"  UNCOMPUTABLE (fail-closed)    : {n_unk}\n")
    for cls in ("WINDOW_MISMATCH", "GLITCH_1_2D"):
        if not by_cls[cls]:
            continue
        print(f"-- {cls} --")
        print(f"{'tk':<7}{'max|dev|':>10}{'med|dev|bad':>13}{'n_bad':>7}{'run':>6}{'n_ex':>6}{'n':>6}")
        for r in sorted(by_cls[cls], key=lambda x: -x["max"]):
            print(f"{r['tk']:<7}{r['max']:>10.4%}{r['med_bad']:>13.4%}{r['n_bad']:>7}"
                  f"{r['run']:>6}{r['n_ex']:>6}{r['n']:>6}")
        print()
    if unk_rows:
        print("uncomputable (rights issue / bad field) -- fail-closed, NOT counted as agreement:")
        for tk, u in unk_rows:
            print(f"   {tk}: {u}")


def cmd_coverage(args):
    """Reverse risk: vendor ratio JUMPS with no matching event in OUR corp-action table.

    If our table is the repair source, its own gaps are the ceiling on this whole idea. A jump in
    r_obs is the market telling us an adjustment happened; no matching row = our DB is the one
    that is blind.
    """
    tks = liquid_tickers(args.since, args.end, args.min_adv, args.limit)
    series, by_tk = load_window(tks, args.since, args.end)
    ex_by_tk = defaultdict(set)
    for tk, evs in by_tk.items():
        for e in evs:
            if cal.is_price_adjusting(e):
                ex_by_tk[tk].add(e["exright_date"])

    jumps = orphan = transient = 0
    orphans = []
    for tk in sorted(series):
        s = [b for b in series[tk] if b["d"] >= args.since]
        r = [b["price"] / b["close"] for b in s]
        for i in range(1, len(s) - 3):
            if r[i - 1] / r[i] - 1.0 <= 0.005:
                continue
            # A real ex-date moves the factor PERMANENTLY. A stale/ffilled `Price` row moves the
            # ratio for one session and it snaps back -- and that shape dominates the raw count
            # (2026-01-30 alone forward-fills `Price` on 662/1252 tickers). Counting transients as
            # missing corp-action rows would overstate our table's blind spots ~4x.
            sustained = all(abs(r[i + k] / r[i] - 1.0) <= 0.001 for k in (1, 2, 3))
            if not sustained:
                transient += 1
                continue
            jumps += 1
            if s[i]["d"] not in ex_by_tk[tk]:
                orphan += 1
                orphans.append((tk, s[i]["d"], r[i - 1] / r[i] - 1.0))
    print(f"sustained factor drops (real ex-date candidates) : {jumps}")
    print(f"  matched by a price-adjusting corporate_action row: {jumps - orphan}")
    print(f"  ORPHAN (our table blind)                        : {orphan}")
    print(f"transient 1-day ratio spikes (stale `Price`, NOT ex-dates, excluded): {transient}")
    for tk, d, mag in sorted(orphans, key=lambda x: -x[2])[:25]:
        print(f"   ORPHAN {tk:<6} {d}  implied f={1 + mag:.6f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fpt", "control", "coverage"])
    ap.add_argument("--since", default="2026-01-01")
    ap.add_argument("--end", default="2026-09-25")
    ap.add_argument("--min-adv", type=float, default=5e10)
    ap.add_argument("--limit", type=int, default=60)
    a = ap.parse_args()
    {"fpt": cmd_fpt, "control": cmd_control, "coverage": cmd_coverage}[a.cmd](a)
