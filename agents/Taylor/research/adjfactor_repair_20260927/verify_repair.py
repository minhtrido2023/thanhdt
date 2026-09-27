#!/usr/bin/env python3
"""Part A — independent confirmation of the self-computed repair, per ticker.

For every BROKEN ticker of the 2026-09-19..09-25 cohort, ask a SECOND source whether
`Close_self = Price / r_pred` is the right adjusted close. The witness used here is
`tav2_bq.ticker_1m` (written by the same ETL on a DIFFERENT, ~1-month window — the window that
was already repaired while `ticker`'s full-history rewrite never ran). Where `ticker_1m` does not
cover a broken session, this script says so instead of guessing; a third source is then required.

Emits `confirmed.json` — the machine-readable artifact for anything downstream. It carries ONLY
what was confirmed against a second source, with the source named per ticker.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTO = HERE.parent / "self_computed_adjfactor_20260927" / "selfcomp_adjfactor.py"
exec(PROTO.read_text().split("if __name__")[0])          # noqa: S102 — reuse, do not fork

TOL_CONFIRM = 0.003      # 0,3% — precision floor measured in the prototype (README §5.4)
TOL_BROKEN = 0.003       # same threshold used to call a session broken
MIN_WITNESS_DAYS = 3     # the factor is a CONSTANT between ex-dates, so a handful of witnessed
                         # sessions pins it; 3 guards against a single rounding coincidence
BROKEN = ["AMS", "BTD", "DRI", "E29", "FPT", "GAS", "HTL", "PGD", "PHC",
          "TVN", "V12", "VCC", "VFR", "VPB", "VTB"]
SINCE, END = "2026-06-01", "2026-09-25"


def ticker_1m_rows(tks):
    tk = ",".join(f'"{t}"' for t in sorted(set(tks)))
    return cal.bq(f"""
        SELECT ticker AS tk, CAST(time AS STRING) AS d, Close AS close, Price AS price
        FROM `{BQ}.tav2_bq.ticker_1m`
        WHERE ticker IN ({tk}) AND Close > 0 AND Price > 0
        ORDER BY ticker, time
    """)


def main():
    series, by_tk = load_window(BROKEN, SINCE, END)
    w1m = {}
    for r in ticker_1m_rows(BROKEN):
        w1m.setdefault(r["tk"], {})[r["d"]] = (float(r["close"]), float(r["price"]))

    out = {}
    print(f"{'tk':<6}{'r_pred':>10}{'n_brk':>7}{'n_wit':>7}{'dev_max':>10}{'dev_med':>10}"
          f"{'1m_agrees':>11}  verdict")
    for tk in BROKEN:
        curve, used, _notes, unknown = build_factor_curve(tk, series[tk], by_tk.get(tk, []))
        if unknown:
            out[tk] = {"verdict": "UNCOMPUTABLE", "unknown_ex": unknown}
            print(f"{tk:<6}{'':>10}{'':>7}{'':>7}{'':>10}{'':>10}{'':>11}  UNCOMPUTABLE")
            continue
        bars = [b for b in series[tk] if b["d"] >= SINCE]
        broken_days = [b for b in bars
                       if abs((b["price"] / b["close"]) / curve[b["d"]] - 1.0) > TOL_BROKEN]
        wit = w1m.get(tk, {})
        # `ticker_1m` carries the SAME defect on part of its window (measured: FPT is adjusted
        # 09-08..09-18 and raw 08-26..09-07). A row still in the pre-event frame is not a second
        # opinion -- it is a copy of the row under test. Only rows whose own Price/Close already
        # equals r_pred count as a witness; the rest are recorded as "no witness", not as a
        # disagreement. Lumping them together reports the defect itself as a refutation.
        devs, n_overlap, n_nowit = [], 0, 0
        for b in broken_days:
            if b["d"] not in wit:
                continue
            n_overlap += 1
            c1m, p1m = wit[b["d"]]
            if abs((p1m / c1m) / curve[b["d"]] - 1.0) > TOL_CONFIRM:
                n_nowit += 1
                continue
            devs.append(b["price"] / curve[b["d"]] / c1m - 1.0)
        n_1m_adj = len(devs)
        rec = {
            "r_pred_oldest": curve[bars[0]["d"]],
            "ex_dates_used": [[d, f] for d, f in used],
            "n_broken_sessions": len(broken_days),
            "broken_range": [broken_days[0]["d"], broken_days[-1]["d"]] if broken_days else None,
            "witness": "tav2_bq.ticker_1m",
            "n_witness_overlap": n_overlap,
            "n_witness_usable": n_1m_adj,
            "n_witness_same_defect": n_nowit,
        }
        if n_1m_adj < MIN_WITNESS_DAYS:
            rec["verdict"] = "NO_SECOND_SOURCE"
        else:
            adev = sorted(abs(x) for x in devs)
            rec["dev_max"] = adev[-1]
            rec["dev_median"] = adev[len(adev) // 2]
            rec["verdict"] = "CONFIRMED" if adev[-1] <= TOL_CONFIRM else "WITNESS_DISAGREES"
        out[tk] = rec
        print(f"{tk:<6}{rec['r_pred_oldest']:>10.6f}{len(broken_days):>7}{n_1m_adj:>7}"
              f"{rec.get('dev_max', float('nan')):>10.5%}{rec.get('dev_median', float('nan')):>10.5%}"
              f"{f'{n_1m_adj}/{n_overlap}':>11}  {rec['verdict']}")

    (HERE / "confirmed.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print("\n-> confirmed.json")
    for v in ("CONFIRMED", "WITNESS_DISAGREES", "NO_SECOND_SOURCE", "UNCOMPUTABLE"):
        names = sorted(k for k, r in out.items() if r["verdict"] == v)
        print(f"{v:<20}{len(names):>3}  {names}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
