#!/usr/bin/env python3
"""Verdict PREREG-4 (tách SUE của LAG: hàng hoá vs bất ngờ thật). Từ chối chạy trước mốc review đầu (PREREG-4 §4).

Chạy: $DNA_PYEXE mike/bin/commodity_sue_decomp_forward_review.py [--data-dir DIR] [--asof YYYY-MM-DD] [--peek]
`--peek` bỏ cổng ngày (ghi 'PEEK' vào output; vi phạm tinh thần PREREG-4, chỉ để selfcheck/debug).
Mốc đầu 2027-09-01 CHỈ kiểm toàn vẹn nhật ký (không verdict). FAIL sớm từ 2028-09-01; PASS chỉ ở mốc CUỐI 2031-09-01."""
import argparse
import datetime as dt
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, ttest_1samp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commodity_sue_decomp_forward_tracker as T  # noqa: E402

REVIEWS = ["2027-09-01", "2028-09-01", "2029-09-01", "2030-09-01", "2031-09-01"]
FINAL = REVIEWS[-1]
MIN_EV, MIN_FAM = 6, 3
N_FAIL_EARLY, N_PASS, FRAC_POS, ALPHA = 8, 16, 0.6, 0.05
SPECS = [("S1", "sue1"), ("S2", "sue2")]          # S1 chính, S2 phụ — Holm ×2


def season_dic(ev, s):
    """ev: sự kiện TIER_A counts=True có post60. → DataFrame mùa hợp lệ (quarter, n, nfam, ic_res, ic_raw, d)."""
    rows = []
    for q, g in ev.dropna(subset=[s, f"{s}_res", "post60"]).groupby("quarter"):
        if len(g) < MIN_EV or g.family.nunique() < MIN_FAM:
            continue
        a, b = spearmanr(g[f"{s}_res"], g.post60)[0], spearmanr(g[s], g.post60)[0]
        rows.append(dict(quarter=q, n=len(g), nfam=g.family.nunique(), ic_res=a, ic_raw=b, d=a - b))
    return pd.DataFrame(rows, columns=["quarter", "n", "nfam", "ic_res", "ic_raw", "d"]).sort_values("quarter")


def stats(ev, s):
    S = season_dic(ev, s)
    n = len(S)
    st = dict(n_seasons=n)
    if n == 0:
        return st, S
    st.update(mean=float(S.d.mean()), median=float(S.d.median()), frac_pos=float((S.d > 0).mean()))
    st["p_one_sided"] = float(ttest_1samp(S.d, 0, alternative="greater").pvalue) if n >= 2 else float("nan")
    st["lofo_min"] = float(min((season_dic(ev[ev.family != f], s).d.mean() for f in ev.family.unique()),
                               default=float("nan")))
    h = n // 2
    st["half1"], st["half2"] = (float(S.d.iloc[:h].mean()), float(S.d.iloc[h:].mean())) if n >= 2 else (np.nan, np.nan)
    return st, S


def holm(ps):
    """ps: {k: p} → {k: p_holm}."""
    ks = sorted(ps, key=lambda k: ps[k])
    out, run = {}, 0.0
    for i, k in enumerate(ks):
        run = max(run, min(1.0, (len(ks) - i) * ps[k]))
        out[k] = run
    return out


def verdict(st, p_holm, stage):
    """stage ∈ {'integrity', 'mid', 'final'} → chuỗi verdict cho 1 S."""
    n = st.get("n_seasons", 0)
    if stage == "integrity":
        return "KIỂM TOÀN VẸN (mốc đầu — không verdict)"
    if n >= N_FAIL_EARLY and st["mean"] <= 0:
        return f"FAIL (dừng sớm: N={n}≥{N_FAIL_EARLY} mùa và TB ΔIC ≤ 0)"
    if stage == "mid":
        return "TIẾP TỤC (PASS chỉ xét ở mốc cuối)"
    if n < N_PASS:
        return f"KHÔNG PHÂN BIỆT ĐƯỢC (N={n}<{N_PASS} mùa) — đóng, không tự gia hạn"
    c = [p_holm < ALPHA, st["mean"] > 0 and st["median"] > 0, st["frac_pos"] >= FRAC_POS, st["lofo_min"] > 0,
         st["half1"] > 0 and st["half2"] > 0]
    if all(c):
        return "PASS (ứng viên R&D — cần quant-skeptic CONFIRMED + user, KHÔNG tự wire vào LAG)"
    return "FAIL (trượt tiêu chí " + ",".join(str(i + 1) for i, v in enumerate(c) if not v) + ")"


def stage_of(asof):
    return "final" if asof >= FINAL else ("mid" if asof >= REVIEWS[1] else "integrity")


def load_events(data_dir):
    ev = pd.read_csv(os.path.join(data_dir, "commodity_sue_decomp_forward_events.csv"))
    out = pd.read_csv(os.path.join(data_dir, "commodity_sue_decomp_forward_outcomes.csv"))
    dup = int(ev.duplicated(T.KEY).sum()) + int(out.duplicated(T.KEY).sum())
    return ev.merge(out[T.KEY + ["post60", "note"]], on=T.KEY, how="left"), dup


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=os.path.join(T.WC_ROOT, "data"))
    ap.add_argument("--asof", default=dt.datetime.now(T.ICT).strftime("%Y-%m-%d"))
    ap.add_argument("--peek", action="store_true")
    a = ap.parse_args(argv)
    if a.asof < REVIEWS[0] and not a.peek:
        print(f"TỪ CHỐI: {a.asof} < mốc review đầu {REVIEWS[0]} (PREREG-4 §4).")
        return 3
    bad = T.check_locks()
    if bad:
        print("LOCK MISMATCH:\n  " + "\n  ".join(bad))
        return 2
    stage = stage_of(a.asof)
    E, dup = load_events(a.data_dir)
    A = E[(E.group == "TIER_A") & (E.status == "FORWARD") & (E.counts.astype(str) == "True")]
    pfx = "PEEK " if a.peek else ""
    print(f"{pfx}as-of {a.asof} · giai đoạn {stage} · khoá trùng {dup} · TIER_A FORWARD counts={len(A)} "
          f"(có post60 {int(A.post60.notna().sum())}) · loại {E[E.counts.astype(str) != 'True'].reason.value_counts().to_dict()}")
    if stage == "integrity":
        print(verdict({}, 1.0, stage))
        return 0
    res = {k: stats(A, s) for k, s in SPECS}
    ph = holm({k: (res[k][0].get("p_one_sided", 1.0) if res[k][0].get("n_seasons", 0) >= 2 else 1.0) for k, _ in SPECS})
    for k, s in SPECS:
        st, _ = res[k]
        print(f"{k} ({s}): {verdict(st, ph[k], stage)} · {st} · p_holm={ph[k]:.4f}")
    # mô tả (không phải tiêu chí)
    desc = {"lag_qualify=1": A[A.lag_qualify.astype(str) == "1"], "bỏ banned": A[A.banned.astype(str) != "1"]}
    for lab, sub in desc.items():
        print(f"  mô tả {lab}: " + " · ".join(f"{k} {stats(sub, s)[0]}" for k, s in SPECS))
    nc = E[(E.group == "NO_COMMODITY") & E.post60.notna()]
    for k, s in SPECS:
        ic_nc = [spearmanr(g[s], g.post60)[0] for _, g in nc.dropna(subset=[s]).groupby("quarter") if len(g) >= MIN_EV]
        print(f"  mô tả NO_COMMODITY {k}: TB IC thô {np.nanmean(ic_nc) if ic_nc else float('nan'):.4f} "
              f"({len(ic_nc)} mùa) vs TIER_A TB IC thô {res[k][1].ic_raw.mean() if len(res[k][1]) else float('nan'):.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
