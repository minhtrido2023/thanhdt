# -*- coding: utf-8 -*-
"""DSR + PBO(CSCV) + sign-test/LOO cho HO gate kha-thi-thi-hanh — job Taylor_20260804_085248.
Tai dung ham cua dsr_pbo_annex.py (khong viet lai cong thuc). Kiem tra khoi suy bien truoc
khi chay CSCV (bai hoc CAPIT navsize 2026-07-31)."""
import glob
import os
import sys

import numpy as np

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import dsr_pbo_annex as A  # noqa: E402

DATA = "/home/trido/thanhdt/WorkingClaude/data"
EXP = os.path.dirname(os.path.abspath(__file__))


def csv_for(tag):
    return glob.glob(os.path.join(DATA, f"*_exp_{tag}_univpit*.csv"))[0]


FAM = {
    "NAV=50B (K = 0 / 1,00 / 2,59 / 5,18 / 12,95 / 44,4)":
        ["n50_ctrl", "n50_K1_00", "n50_K2_59", "n50_K5_18", "n50_K12_95", "n50_K44_4"],
    "NAV=1B  (K = 0 / 1,00 / 5,18 / 44,4)":
        ["n1_ctrl", "n1_K1_00", "n1_K5_18", "n1_K44_4"],
}

for title, tags in FAM.items():
    print(f"\n{'='*100}\n{title}\n{'='*100}")
    rets, srs = [], []
    for t in tags:
        s = A.load_nav(csv_for(t))
        r = A.daily_logret(s)
        rets.append(r)
        srs.append(r.mean() / r.std(ddof=1))
        print(f"{t:12s} T={len(r):5d}  final NAV={s.iloc[-1]/1e9:9.2f}B  SR/obs={srs[-1]:.5f}")

    T = min(len(r) for r in rets)
    M = np.column_stack([r[-T:] for r in rets])
    S = 16
    T2 = (T // S) * S
    blocks = np.array_split(M[:T2], S, axis=0)
    bad = [(i, float(np.nanmin(b.std(axis=0, ddof=1)))) for i, b in enumerate(blocks)
           if np.nanmin(b.std(axis=0, ddof=1)) <= 1e-12 or np.isnan(b).any()]
    print(f"khoi suy bien (sd~0 hoac NaN) trong {S} khoi: {len(bad)} -> {bad}")

    sr0 = A.expected_max_sr(np.var(srs, ddof=1), len(tags))
    for t, r, sr in zip(tags, rets, srs):
        mo = A.moments(r)
        g3, g4 = (mo[2], mo[3]) if len(mo) >= 4 else (0.0, 3.0)
        d, _ = A.dsr(sr, sr0, g3, g4, len(r))
        print(f"DSR {t:12s} SR/obs={sr:.5f}  sr0(exp max ho N={len(tags)})={sr0:.5f} -> DSR={d:.4f}")

    pbo, logits, ncombo, ncfg, t2 = A.cscv_pbo(M, S=S)
    print(f"PBO(CSCV, S={S}, {ncombo} to hop, Ncfg={ncfg}, T={t2}) = {pbo:.3f}  "
          f"median logit={np.median(logits):+.3f}")

# --- sign test / LOO cho phep so QUYET DINH: K=5,18 vs L1 o NAV=1B --------------------
print(f"\n{'='*100}\nPHEP SO QUYET DINH — NAV=1B: K=5,18 (treat) vs L1 LIQ_ZERO_BLOCK=lag (base)\n{'='*100}")
import re  # noqa: E402


def annual(tag):
    txt = open(os.path.join(EXP, tag + ".log"), encoding="utf-8", errors="replace").read()
    return {int(y): float(v) for y, v in
            re.findall(r"^\s{2}(\d{4}): ([\+\-][\d\.]+)%", txt, re.M)}


base, treat = annual("n1_L1ctrl"), annual("n1_K5_18")
yrs = sorted(base)
dl = {y: treat[y] - base[y] for y in yrs}
for y in yrs:
    print(f"  {y}: base {base[y]:+7.2f}%  treat {treat[y]:+7.2f}%  Δ {dl[y]:+7.2f}pp")
w = sum(1 for y in yrs if dl[y] > 0)
n = len(yrs)
from math import comb  # noqa: E402
p = sum(comb(n, k) for k in range(w, n + 1)) / 2 ** n
print(f"\nsign test: thang {w}/{n} nam, P(X>={w} | p=0,5) = {p:.3f}")


def cagr_ex(tag, drop):
    """CAGR khi BO cac nam trong `drop` — ghep lai tu ty suat nam (xap xi hinh hoc)."""
    a = annual(tag)
    keep = [y for y in yrs if y not in drop]
    g = np.prod([1 + a[y] / 100.0 for y in keep])
    return (g ** (1.0 / len(keep)) - 1) * 100


print("\nLOO / bo-nhom (CAGR ghep tu ty suat nam, xap xi):")
for drop in ([], [2021], [2020], [2014], [2020, 2021], [2014, 2020, 2021]):
    b, t = cagr_ex("n1_L1ctrl", drop), cagr_ex("n1_K5_18", drop)
    lbl = "khong bo" if not drop else "bo " + "+".join(map(str, drop))
    print(f"  {lbl:22s} base {b:6.2f}%  treat {t:6.2f}%  Δ {t-b:+6.2f}pp")
