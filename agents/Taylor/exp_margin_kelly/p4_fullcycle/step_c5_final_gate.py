#!/usr/bin/env python
"""GATE G-C CHUNG CUOC — tinh 1 CHO DUY NHAT, tren phep do da sua (step_c3 audit).

Kiem CA HAI truc fragility DANG KY o §5 (12,5% vs 14%) VA truc ke toan phat sinh trong khi chay
(cong-them vs tai dau tu), de khong ai phai ghep tay ket qua tu nhieu log.

Tieu chi G-C (§5, nguyen van): dCAGR > 0 o CA IS(2014-19) LAN OOS(2020+);
dMaxDD toan-so <= +1,0pp (xau di); LOO khong nam nao ganh >=50%; 0 margin call adversarial.
"""
import numpy as np
import pandas as pd
from pathlib import Path
import step_c3_clean_isoos as C3

F = [1.1, 1.2, 1.3, 1.5]
WINS = {"IS": ("2014-01-01", "2019-12-31"), "OOS": ("2020-01-01", "2026-12-31"),
        "FULL": ("2014-01-01", "2026-12-31")}


def loo_max(f, c, mt, pen, comp):
    s, _ = C3.run(f, c, mt, pen, *WINS["FULL"], comp)
    b, _ = C3.run(1.0, c, mt, pen, *WINS["FULL"], comp)
    tot = C3.cagr(s) - C3.cagr(b)
    if abs(tot) < 1e-12:
        return np.nan, np.nan, tot
    old = C3.ev
    ys, es = {}, {}
    try:
        for y in sorted(old["event"].dt.year.unique()):
            C3.ev = old[old["event"].dt.year != int(y)].reset_index(drop=True)
            sy, _ = C3.run(f, c, mt, pen, *WINS["FULL"], comp)
            ys[int(y)] = (tot - (C3.cagr(sy) - C3.cagr(b))) / tot
        for _, e in old.iterrows():
            C3.ev = old[old["event"] != e["event"]].reset_index(drop=True)
            se, _ = C3.run(f, c, mt, pen, *WINS["FULL"], comp)
            es[str(e["event"].date())] = (tot - (C3.cagr(se) - C3.cagr(b))) / tot
    finally:
        C3.ev = old
    return max(ys.values()), max(es.values()), tot


def main():
    lines = []; P = lines.append
    P("=" * 100)
    P("GATE G-C CHUNG CUOC — tren phep do DA SUA (overlay do trong DUNG cua so, khong mang")
    P("von IS sang OOS duoi dang tien mat 0%). Xem step_c3 cho chan doan ao anh do luong.")
    P("=" * 100)
    P("Tieu chi §5: dCAGR>0 o CA IS lan OOS | dMaxDD xau di <=+1,0pp | LOO nam <50% | 0 call")
    P("")

    for cname, c, mt, pen in [("BASE 12,5%/30%/1%", 0.125, 0.30, 0.01),
                              ("ADV  14%/35%/2%  ", 0.140, 0.35, 0.02)]:
        for aname, comp in [("cong-them", False), ("tai dau tu", True)]:
            P("-" * 100)
            P(f"{cname}  |  ke toan: {aname}")
            P("-" * 100)
            P(f"{'f':>6}{'dCAGR_IS':>11}{'dCAGR_OOS':>12}{'dCAGR_FULL':>12}"
              f"{'dMaxDD xau':>13}{'LOO nam':>10}{'LOO sk':>9}{'#call':>7}  verdict")
            for f in F:
                out = {}
                for w, (lo, hi) in WINS.items():
                    s, cl = C3.run(f, c, mt, pen, lo, hi, comp)
                    b, _ = C3.run(1.0, c, mt, pen, lo, hi, comp)
                    out[w] = (C3.cagr(s) - C3.cagr(b),
                              (C3.maxdd(b) - C3.maxdd(s)) * 100, len(cl))
                ly, le, _ = loo_max(f, c, mt, pen, comp)
                ok = (out["IS"][0] > 0 and out["OOS"][0] > 0
                      and out["FULL"][1] <= 1.0 and out["FULL"][2] == 0 and ly < 0.50)
                P(f"{f:>6.2f}{out['IS'][0]:>+11.2%}{out['OOS'][0]:>+12.2%}"
                  f"{out['FULL'][0]:>+12.2%}{out['FULL'][1]:>+12.2f}pp"
                  f"{ly:>10.1%}{le:>9.1%}{out['FULL'][2]:>7d}  "
                  f"{'PASS' if ok else 'FAIL'}")
            P("")

    txt = "\n".join(lines)
    print(txt)
    (Path(__file__).parent / "step_c5_final_gate.log").write_text(txt + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
