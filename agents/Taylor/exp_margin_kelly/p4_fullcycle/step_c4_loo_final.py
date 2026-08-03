#!/usr/bin/env python
"""BUOC C — LOO CHUNG CUOC tren phep do DA SUA (guard #10 audit xong).

Sau khi step_c3 chung minh dCAGR_OOS am o ban cong-them la AO ANH DO LUONG, tieu chi con lai
cua G-C quyet dinh ket qua la TAP TRUNG (LOO). Chay lai LOO tren ban TAI DAU TU / cua so FULL
— tuc ban CO LOI NHAT cho phe "margin tot" — de ket luan tap trung khong the bi quy cho phep
do bat loi.

Chay CA HAI: LOO theo NAM (gate dang ky §5) va LOO theo SU KIEN (chan doan dung hon, bai hoc p3
bus 2026-08-03T09:03: LOO theo nam tren chuoi compounding la ao anh).
"""
import numpy as np
import pandas as pd
from pathlib import Path
import step_c3_clean_isoos as C3

F = [1.1, 1.2, 1.3, 1.5]
LO, HI = "2014-01-01", "2026-12-31"


def cagr_of(f, drop_ev=None, drop_yr=None):
    keep = C3.ev.copy()
    if drop_ev is not None:
        keep = keep[keep["event"] != drop_ev]
    if drop_yr is not None:
        keep = keep[keep["event"].dt.year != drop_yr]
    old = C3.ev
    C3.ev = keep.reset_index(drop=True)
    try:
        s, _ = C3.run(f, 0.140, 0.35, 0.02, LO, HI, True)
        return C3.cagr(s)
    finally:
        C3.ev = old


def main():
    lines = []; P = lines.append
    P("=" * 92)
    P("LOO CHUNG CUOC — ban TAI DAU TU, cua so FULL, adversarial (c=14%, maint 35%, pen 2%)")
    P("=" * 92)
    base = cagr_of(1.0)
    P(f"control (f=1,0) CAGR = {base:.4%}")
    P("")
    for f in F:
        tot = cagr_of(f) - base
        P(f"--- f = {f:.2f}   dCAGR toan ky = {tot:+.2%} ---")
        shr_y = {}
        for y in sorted(C3.ev["event"].dt.year.unique()):
            shr_y[int(y)] = (tot - (cagr_of(f, drop_yr=int(y)) - base)) / tot
        shr_e = {}
        for _, e in C3.ev.iterrows():
            shr_e[str(e["event"].date())] = (tot - (cagr_of(f, drop_ev=e["event"]) - base)) / tot
        ymax = max(shr_y, key=lambda k: shr_y[k])
        emax = max(shr_e, key=lambda k: shr_e[k])
        P(f"  LOO NAM     — gong nhat {ymax}: {shr_y[ymax]:.1%}  "
          f"({'PASS' if shr_y[ymax] < 0.5 else 'FAIL nguong 50%'})")
        P(f"     " + ", ".join(f"{y}:{v:+.0%}" for y, v in shr_y.items()))
        P(f"  LOO SU KIEN — gong nhat {emax}: {shr_e[emax]:.1%}  "
          f"({'PASS' if shr_e[emax] < 0.5 else 'FAIL nguong 50%'})")
        P(f"     " + ", ".join(f"{k[5:]}:{v:+.0%}" for k, v in shr_e.items()))
        P("")
    txt = "\n".join(lines)
    print(txt)
    (Path(__file__).parent / "step_c4_loo_final.log").write_text(txt + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
