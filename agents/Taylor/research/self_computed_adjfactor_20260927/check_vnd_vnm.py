#!/usr/bin/env python3
"""Ad-hoc check for VND/VNM using the same machinery as cmd_fpt in selfcomp_adjfactor.py.

Dispatch Taylor_20260928_103533: verify whether VND (ex 05-29) and VNM (ex 06-26), both flagged
UNCOMPUTABLE by Layer 1 (price_ffill_suspect), are real corp-action drift like FPT, or just an
over-cautious guard.
"""
import sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/self_computed_adjfactor_20260927")
from selfcomp_adjfactor import (series_by_ticker, price_rows, build_factor_curve, segments, TOL)
import corp_action_lib as cal


def check(tk, start, end, ev_since):
    series = series_by_ticker(price_rows([tk], start, end))[tk]
    events = cal.events([tk], since=ev_since, until=end)
    curve, used, notes, unknown = build_factor_curve(tk, series, events)

    print(f"=== {tk}  {series[0]['d']} .. {series[-1]['d']}  ({len(series)} sessions) ===\n")
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

    bad = [b for b in series if abs((b["price"] / b["close"]) / curve[b["d"]] - 1.0) > TOL]
    print(f"\n   mismatching sessions: {len(bad)} / {len(series)}"
          f"   window: {bad[0]['d'] if bad else '-'} .. {bad[-1]['d'] if bad else '-'}")
    if worst:
        print(f"   worst segment deviation: {worst[1]:+.4%} "
              f"({worst[0]['d0']}..{worst[0]['d1']})")
    print()
    return unknown, bad, worst


if __name__ == "__main__":
    check("VND", "2026-04-01", "2026-09-25", "2026-03-31")
    check("VNM", "2026-04-01", "2026-09-25", "2026-03-31")
