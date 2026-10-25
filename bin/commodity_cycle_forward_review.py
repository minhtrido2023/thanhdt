#!/usr/bin/env python3
"""Verdict PREREG-2 (commodity early-cycle 1,05/3M). Từ chối chạy trước ngày xem xét (PREREG §7).

Chạy: $DNA_PYEXE mike/bin/commodity_cycle_forward_review.py [--data-dir DIR] [--asof YYYY-MM-DD] [--peek]
`--peek` bỏ cổng ngày (ghi 'PEEK' vào output; vi phạm tinh thần PREREG §7, chỉ để selfcheck/debug)."""
import argparse
import datetime as dt
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import binomtest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commodity_cycle_forward_tracker as T  # noqa: E402

REVIEWS = ["2028-01-31", "2029-01-31", "2030-01-31", "2031-01-31"]
FINAL = REVIEWS[-1]
N_MIN, N_FAIL_EARLY, MEAN_MIN, BASE_MARGIN = 5, 3, 0.05, 0.03


def cluster_means(ev, days):
    ev = ev.sort_values("entry_date").reset_index(drop=True)
    pos = [days.get_loc(pd.Timestamp(e)) for e in ev.entry_date]
    cl, c = [], 0
    for k, p in enumerate(pos):
        if k and p - pos[k - 1] >= 126:
            c += 1
        cl.append(c)
    ev["cluster"] = cl
    return ev, ev.groupby("cluster").X.mean()


def verdict(cm, ev, base_mix, final):
    n = len(cm)
    if n == 0:
        return "KHÔNG PHÂN BIỆT ĐƯỢC (thiếu N)" if final else "CHƯA ĐỦ DỮ LIỆU (N=0)", {}
    rng = np.random.default_rng(20261025)
    boots = [cm.sample(n, replace=True, random_state=int(rng.integers(1e9))).mean() for _ in range(10000)]
    pos = int((cm > 0).sum())
    st = dict(n=n, mean=float(cm.mean()), median=float(cm.median()), ci90_lo=float(np.percentile(boots, 5)),
              pos=pos, sign_p=float(binomtest(pos, n, 0.5, alternative="greater").pvalue),
              loco_min=float(min(cm.drop(k).mean() for k in cm.index)) if n > 1 else float("nan"),
              ev_minus_base=float(ev.X.mean() - base_mix) if base_mix is not None else float("nan"))
    c = [st["mean"] >= MEAN_MIN and st["median"] > 0, st["ci90_lo"] > 0,
         pos >= 2 / 3 * n and st["sign_p"] < 0.10, n > 1 and st["loco_min"] > 0,
         st["ev_minus_base"] >= BASE_MARGIN]
    st["criteria"] = c
    if n >= N_FAIL_EARLY and st["mean"] <= 0:
        return "FAIL (dừng sớm: N≥3 và TB cụm ≤ 0)", st
    if n >= N_MIN and not all(c):
        return "FAIL (N≥5, trượt tiêu chí " + ",".join(str(i + 1) for i, v in enumerate(c) if not v) + ")", st
    if not final:
        return "TIẾP TỤC (chưa FAIL; SUCCESS chỉ xét ở ngày cuối)", st
    return ("SUCCESS (ứng viên R&D — cần quant-skeptic + user, không tự wire)" if n >= N_MIN and all(c)
            else "KHÔNG PHÂN BIỆT ĐƯỢC (thiếu N)"), st


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=os.path.join(T.WC_ROOT, "data"))
    ap.add_argument("--asof", default=dt.datetime.now(T.ICT).strftime("%Y-%m-%d"))
    ap.add_argument("--peek", action="store_true")
    a = ap.parse_args(argv)
    if a.asof < REVIEWS[0] and not a.peek:
        print(f"TỪ CHỐI: {a.asof} < mốc xem xét đầu {REVIEWS[0]} (PREREG-2 §7).")
        return 3
    bad = T.check_locks()
    if bad:
        print("LOCK MISMATCH:\n  " + "\n  ".join(bad))
        return 2
    final = a.asof >= FINAL
    out = pd.read_csv(os.path.join(a.data_dir, "commodity_cycle_forward_outcomes.csv"))
    ev = out[(out.counts.astype(str) == "True") & out.X.notna()].copy()
    ev["entry_date"] = pd.to_datetime(ev.entry_date)
    mk = T.load_market()
    base_mix = None
    if len(ev):
        lo, hi = ev.entry_date.min().to_period("M") - 1, ev.entry_date.max().to_period("M")
        base = {}
        for f in ev.family.unique():
            xs = []
            for m in pd.period_range(lo, hi, freq="M"):
                t = T.entry_session(mk.days, T.day11(m))
                if t is not None and mk.days.get_loc(t) + T.H <= len(mk.days) - 1:
                    r = mk.measure(f, t)
                    if r:
                        xs.append(r["X"])
            base[f] = float(np.mean(xs)) if xs else np.nan
        base_mix = float(np.nanmean([base[f] for f in ev.family]))
    ev, cm = cluster_means(ev, mk.days) if len(ev) else (ev, pd.Series(dtype=float))
    v, st = verdict(cm, ev, base_mix, final)
    print(("PEEK " if a.peek else "") + f"as-of {a.asof} · {'CUỐI' if final else 'giữa kỳ'} · verdict: {v}")
    print(st)
    return 0


if __name__ == "__main__":
    sys.exit(main())
