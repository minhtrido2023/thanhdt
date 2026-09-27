#!/usr/bin/env python3
"""Part A, witness #2 — FiinX (FiinGroup) adjusted close vs our self-computed repair.

Why a second witness at all: `tav2_bq.ticker_1m` is written by the SAME ETL as the broken
`ticker`, so it is only a PARTIAL witness (measured: it carries the identical unadjusted frame on
part of its own window) and it does not reach the thinnest names at all. FiinX is a different
vendor, not the cafef/VCI chain that feeds `tav2_bq`, so agreement here is independent in the way
that matters.

`fiinx_witness.csv` = FiinX adjusted AND unadjusted closes, fetched via the FiinX MCP 2026-09-27.

Two preconditions are enforced on every witness row before it is allowed to confirm or refute,
because without them FiinX's own artifacts get read as verdicts on our factor:

  P1  FiinX unadjusted close == `tav2_bq.ticker.Price`. Two adjusted frames are only comparable
      when they sit on the same raw bar. (Measured: P1 holds on 44/44 rows here, so no row is
      dropped by it -- it is recorded because a future run where it fails must not silently
      compare a FiinX bar against a different raw price.)
  P2  FiinX's OWN implied factor is a legal back-adjustment: r_fx = raw/adj must be >= 1 and
      non-increasing forward in time (a cumulative product over FUTURE ex-dates can only shrink as
      t advances). A row failing P2 is a FiinX defect, not evidence about us -- e.g. BTD 09-17 has
      adj 14.550,95 ABOVE raw 14.500 (r_fx = 0,9965 < 1, impossible), and AMS's implied factor
      RISES from 1,05254 (09-17) to 1,05962 (09-18) on a flat raw price.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTO = HERE.parent / "self_computed_adjfactor_20260927" / "selfcomp_adjfactor.py"
exec(PROTO.read_text().split("if __name__")[0])          # noqa: S102

TOL = 0.003          # 0,3% precision floor (prototype README §5.4)
RAW_TOL = 1e-6
SINCE, END = "2026-06-01", "2026-09-25"
TKS = ["AMS", "BTD", "DRI", "E29", "FPT", "GAS", "HTL", "PGD", "PHC",
       "TVN", "V12", "VCC", "VFR", "VPB", "VTB"]


def usable_witness(tk, wit):
    """Rows of `wit` (dict d -> (adj, raw)) that pass P2. Returns (kept, dropped_with_reason)."""
    kept, dropped = {}, []
    prev_r = None
    for d in sorted(wit):
        adj, raw = wit[d]
        r = raw / adj
        if r < 1.0 - RAW_TOL:
            dropped.append((d, f"r_fx={r:.6f} < 1 (FiinX adj above its own raw)"))
            continue
        if prev_r is not None and r > prev_r + 1e-9:
            dropped.append((d, f"r_fx={r:.6f} > previous {prev_r:.6f} — factor rises forward "
                               f"in time, not a legal back-adjustment"))
            continue
        prev_r = r
        kept[d] = (adj, raw, r)
    return kept, dropped


def main():
    wit = defaultdict(dict)
    with open(HERE / "fiinx_witness.csv") as f:
        for r in csv.DictReader(f):
            wit[r["ticker"]][r["d"]] = (float(r["close_adj"]), float(r["close_raw"]))

    series, by_tk = load_window(TKS, SINCE, END)
    out = {}
    print(f"{'tk':<6}{'date':<12}{'raw BQ':>10}{'raw FX':>10}{'r_pred':>10}{'r_fx':>10}"
          f"{'Close_self':>12}{'FiinX adj':>12}{'dev':>10}")
    for tk in TKS:
        curve, _used, _n, unknown = build_factor_curve(tk, series[tk], by_tk.get(tk, []))
        kept, dropped = usable_witness(tk, wit.get(tk, {}))
        devs, p1_fail = [], []
        for d, (adj, raw_fx, r_fx) in kept.items():
            bar = next((b for b in series[tk] if b["d"] == d), None)
            if bar is None or d not in curve:
                continue
            if abs(bar["price"] / raw_fx - 1.0) > RAW_TOL:
                p1_fail.append((d, bar["price"], raw_fx))
                continue
            self_close = bar["price"] / curve[d]
            dev = self_close / adj - 1.0
            devs.append(dev)
            print(f"{tk:<6}{d:<12}{bar['price']:>10,.0f}{raw_fx:>10,.0f}{curve[d]:>10.6f}"
                  f"{r_fx:>10.6f}{self_close:>12,.2f}{adj:>12,.2f}{dev:>+10.4%}")
        rec = {"n_rows_offered": len(wit.get(tk, {})), "n_dropped_P2": len(dropped),
               "dropped_P2": [{"d": d, "why": w} for d, w in dropped],
               "n_dropped_P1": len(p1_fail), "n_used": len(devs)}
        if not devs:
            rec["verdict"] = "NO_USABLE_FIINX_ROW"
        else:
            adev = sorted(abs(x) for x in devs)
            rec.update(dev_max=adev[-1], dev_median=adev[len(adev) // 2])
            rec["verdict"] = ("CONFIRMED" if adev[-1] <= TOL and not unknown
                              else "WITNESS_DISAGREES")
        out[tk] = rec
    (HERE / "confirmed_fiinx.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print()
    for tk in TKS:
        r = out[tk]
        if r["n_dropped_P2"]:
            for x in r["dropped_P2"]:
                print(f"  P2 drop  {tk} {x['d']}: {x['why']}")
    print()
    for v in ("CONFIRMED", "WITNESS_DISAGREES", "NO_USABLE_FIINX_ROW"):
        names = sorted(k for k, r in out.items() if r["verdict"] == v)
        print(f"{v:<22}{len(names):>3}  {names}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
