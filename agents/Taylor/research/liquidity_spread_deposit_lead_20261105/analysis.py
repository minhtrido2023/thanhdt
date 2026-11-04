#!/usr/bin/env python3
"""D2 — liquidity spread (IB3M - policy) lead on Big-4 deposit rates. Runs PREREG.md verbatim.
Usage: $DNA_PYEXE analysis.py [--asof YYYY-MM-DD]   (asof default = today ICT; only for fail-closed staleness)
Outputs: results.json, episodes_<thr>.csv, stdout report. Deterministic (seed fixed, no wall clock in output)."""
import argparse, hashlib, json, os, sys
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"
TE_CSV = os.environ.get("D2_TE_CSV", os.path.join(HERE, "data", "te_ib3m_policy.csv"))
TE_MD5 = "fb65e9bf9f5ee93a73006978968b7c6c"
DEP1M_CSV = os.environ.get("D2_DEP1M_CSV", os.path.join(HERE, "data", "fiinprox_deposit_1m_big4_monthly_2019_2026.csv"))
THR_MAIN, THR_SENS = 1.0, (0.0, 2.0)
HORIZONS = (1, 3, 6)
RUN, END_RUN, SEP_DAYS = 5, 20, 183
B, SEED = 10_000, 20261105


def die(msg):
    print(f"FAIL-CLOSED: {msg}", file=sys.stderr)
    sys.exit(2)


def load_te(asof):
    if not os.path.exists(TE_CSV):
        die(f"thiếu {TE_CSV}")
    md5 = hashlib.md5(open(TE_CSV, "rb").read()).hexdigest()
    if md5 != TE_MD5:
        die(f"md5 snapshot TE lệch PREREG: {md5} != {TE_MD5}")
    d = pd.read_csv(TE_CSV, parse_dates=["observation_date"])
    ib = d[d.series_key == "vn_interbank_3m"].set_index("observation_date").value.sort_index()
    pol = d[d.series_key == "vn_policy_rate"].set_index("observation_date").value.sort_index()
    if ib.empty or pol.empty:
        die(f"series rỗng: ib={len(ib)} policy={len(pol)}")
    stale = (asof - ib.index.max()).days
    if stale > 7:
        die(f"vn_interbank_3m stale {stale} ngày (obs cuối {ib.index.max().date()}, asof {asof.date()})")
    # policy forward-filled from its month-end obs date (only known from that date on — PREREG §2)
    pol_ff = pol.reindex(ib.index.union(pol.index)).ffill().reindex(ib.index)
    s = (ib - pol_ff).dropna()
    return ib, pol, pol_ff, s


def load_dep1m():
    if not os.path.exists(DEP1M_CSV):
        die(f"thiếu {DEP1M_CSV}")
    d = pd.read_csv(DEP1M_CSV, parse_dates=["asof"])
    if len(d) != 92 or d.series.nunique() != 1 or d.series.iloc[0] != "big4_1m_individual":
        die(f"CSV 1T sai cấu trúc: rows={len(d)} series={d.series.unique().tolist()}")
    if d.period.min() != "2019-02" or d.period.max() != "2026-09":
        die(f"CSV 1T sai khoảng: {d.period.min()}→{d.period.max()}")
    return d.set_index("asof").rate_pct.sort_index()


def load_dep12m():
    sys.path.insert(0, WC)
    import deposit_rate_vn  # read-only import; frozen anchors + append-only CSV
    ev = deposit_rate_vn.deposit_events_df().sort_values("time")
    return ev.set_index("time").deposit_rate


def episodes(s, thr):
    """Onset = 5th consecutive obs with S>=thr; signal = next obs (1-session publication lag).
    Episode ends after 20 consecutive obs < thr. Counted onsets must be >=183d apart."""
    above = (s >= thr).values
    idx = s.index
    out, run, in_ep, below, last_counted = [], 0, False, 0, None
    for i, a in enumerate(above):
        if in_ep:
            below = 0 if a else below + 1
            if below >= END_RUN:
                in_ep, below = False, 0
            continue
        run = run + 1 if a else 0
        if run >= RUN and i + 1 < len(idx):
            onset, sig = idx[i], idx[i + 1]
            in_ep, run, below = True, 0, 0
            if last_counted is None or (sig - last_counted).days >= SEP_DAYS:
                out.append({"onset": onset, "signal": sig, "S_onset": round(float(s.iloc[i]), 4)})
                last_counted = sig
    return out


def val_at(dep, t):
    """last observed value with asof <= t; None if t before series start."""
    sub = dep.loc[:t]
    return (None, None) if sub.empty else (float(sub.iloc[-1]), sub.index[-1])


def outcome(dep, T):
    base, base_asof = val_at(dep, T)
    res = {"base": base, "base_asof": None if base_asof is None else str(base_asof.date())}
    for h in HORIZONS:
        th = T + pd.DateOffset(months=h)
        if base is None or th > dep.index.max():
            res[f"d{h}"] = None
            continue
        v, _ = val_at(dep, th)
        res[f"d{h}"] = round(v - base, 4)
    pre, _ = val_at(dep, T - pd.DateOffset(months=3))
    res["pre3"] = None if (pre is None or base is None) else round(base - pre, 4)
    return res


def verdict(eps_out, plac_p90, plac_med):
    d6 = [e["d6"] for e in eps_out if e["d6"] is not None]
    n = len(d6)
    if n < 2:
        return "KHÔNG KẾT LUẬN", n, f"N_eval={n} < 2"
    med = float(np.median(d6))
    pre = [e["pre3"] for e in eps_out if e["d6"] is not None and e["pre3"] is not None]
    medpre = float(np.median(pre)) if pre else None
    if n >= 3 and sum(x > 0 for x in d6) >= n - 1 and med >= 0.25 and plac_p90 is not None \
            and med > plac_p90 and medpre is not None and medpre <= 0.10:
        return "ỦNG HỘ", n, f"median Δ6={med:+.3f} > P90 placebo {plac_p90:+.3f}, pre3={medpre:+.3f}"
    if med <= 0 or (plac_med is not None and med <= plac_med):
        return "KHÔNG ỦNG HỘ", n, f"median Δ6={med:+.3f}, placebo median={plac_med}"
    return "KHÔNG KẾT LUẬN", n, f"median Δ6={med:+.3f}, N_eval={n}, placebo P90={plac_p90}"


def placebo(s, dep, n_eval, lo):
    """random signal dates within outcome window (needs full 6m future). Returns dist of median Δh."""
    pool = s.index[(s.index >= lo) & (s.index + pd.DateOffset(months=6) <= dep.index.max())]
    rows = {d: outcome(dep, d) for d in pool}
    arr = {h: np.array([rows[d][f"d{h}"] for d in pool], dtype=float) for h in HORIZONS}
    drift = {h: round(float(np.nanmean(arr[h])), 4) for h in HORIZONS}
    rng = np.random.default_rng(SEED)
    pick = rng.integers(0, len(pool), size=(B, n_eval))
    dist = {h: np.median(arr[h][pick], axis=1) for h in HORIZONS}
    q = {h: {"p50": round(float(np.percentile(dist[h], 50)), 4),
             "p90": round(float(np.percentile(dist[h], 90)), 4)} for h in HORIZONS}
    return drift, q, len(pool), dist, rows, pool


def mike_check(s):
    last = s.index.max()
    hist = s.loc["2012-01-01":]
    v = float(s.iloc[-1])
    return {"last_obs": str(last.date()), "S_last": round(v, 4),
            "pct_le": round(100 * float((hist <= v).mean()), 2),
            "pct_lt": round(100 * float((hist < v).mean()), 2),
            "n_hist": int(len(hist))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", default=None)
    a = ap.parse_args()
    asof = pd.Timestamp(a.asof) if a.asof else pd.Timestamp(datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date())
    ib, pol, pol_ff, s = load_te(asof)
    dep1 = load_dep1m()
    dep12 = load_dep12m()
    R = {"prereg_md5": hashlib.md5(open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest(),
         "te_md5": TE_MD5, "mike_check": mike_check(s)}
    # PIT window for the primary outcome: real 1M data first usable for signals whose baseline is real
    lo1 = dep1.index.min()
    R["by_thr"] = {}
    for thr in (THR_MAIN,) + THR_SENS:
        eps = episodes(s, thr)
        for e in eps:
            # no-look-ahead assert: S used up to onset only, signal strictly after onset
            assert e["signal"] > e["onset"]
            e["out1m"] = outcome(dep1, e["signal"]) if e["signal"] >= lo1 else None
            e["out12m"] = outcome(dep12, e["signal"]) if e["signal"] >= dep12.index.min() else None
            e["policy_at_signal"] = float(pol_ff.loc[:e["signal"]].iloc[-1])
            e["ib_at_onset"] = float(ib.loc[e["onset"]])
            e["S_max_6m"] = round(float(s.loc[e["signal"]:e["signal"] + pd.DateOffset(months=6)].max()), 4)
        R["by_thr"][str(thr)] = eps
        rows = []
        for e in eps:
            r = {k: (str(v.date()) if isinstance(v, pd.Timestamp) else v) for k, v in e.items()
                 if k not in ("out1m", "out12m")}
            for tag in ("out1m", "out12m"):
                for k, v in (e[tag] or {}).items():
                    r[f"{tag}_{k}"] = v
            rows.append(r)
        pd.DataFrame(rows).to_csv(os.path.join(HERE, f"episodes_thr{thr:+.1f}.csv"), index=False)

    main_eps = [e for e in R["by_thr"][str(THR_MAIN)] if e["out1m"] is not None]
    n_eval = sum(1 for e in main_eps if e["out1m"]["d6"] is not None)
    pl = placebo(s, dep1, max(n_eval, 1), lo1)
    drift, q = pl[0], pl[1]
    R["placebo_1m"] = {"pool_days": pl[2], "drift_mean": drift, "median_dist": q, "B": B, "seed": SEED,
                       "n_eval_used": max(n_eval, 1)}
    # low-S illustration (PREREG §5d): days in window with S <= P20 of window
    pool, rows = pl[5], pl[4]
    sw = s.loc[pool]
    low = sw[sw <= sw.quantile(0.20)].index
    R["low_S_1m"] = {f"d{h}": round(float(np.nanmean([rows[d][f'd{h}'] for d in low])), 4) for h in HORIZONS}
    R["low_S_1m"]["n_days"] = int(len(low))
    if n_eval >= 1:
        actual_med = {h: float(np.median([e["out1m"][f"d{h}"] for e in main_eps if e["out1m"][f"d{h}"] is not None]))
                      for h in HORIZONS}
        R["placebo_1m"]["actual_median"] = {h: round(v, 4) for h, v in actual_med.items()}
        R["placebo_1m"]["actual_pctile"] = {h: round(100 * float((pl[3][h] < actual_med[h]).mean()), 2)
                                            for h in HORIZONS}
    v, n, why = verdict([e["out1m"] for e in main_eps], q[6]["p90"], q[6]["p50"])
    R["verdict"] = {"label": v, "n_eval": n, "why": why}
    # POST-HOC (NGOÀI PREREG, không đổi verdict): leave-one-episode-out trên luật verdict
    loo = {}
    for i, e in enumerate(main_eps):
        rest = [x["out1m"] for j, x in enumerate(main_eps) if j != i]
        loo[str(e["signal"].date())] = verdict(rest, q[6]["p90"], q[6]["p50"])[0]
    R["post_hoc_loo"] = loo
    # POST-HOC: verdict-rule applied to sensitivity thresholds + 12M (illustration only)
    R["post_hoc_rule_by_thr_1m"] = {}
    R["post_hoc_rule_by_thr_12m_nonPIT"] = {}
    for thr in (THR_MAIN,) + THR_SENS:
        e1 = [e["out1m"] for e in R["by_thr"][str(thr)] if e["out1m"] is not None]
        e12 = [e["out12m"] for e in R["by_thr"][str(thr)] if e["out12m"] is not None]
        R["post_hoc_rule_by_thr_1m"][str(thr)] = verdict(e1, q[6]["p90"], q[6]["p50"])
        R["post_hoc_rule_by_thr_12m_nonPIT"][str(thr)] = [e["d6"] for e in e12]

    # cycle illustration 2008 / 2011 / 2022Q4 (spread + policy only where no deposit data)
    ill = {}
    for name, a0, a1 in (("2008", "2007-10-01", "2009-06-30"), ("2011", "2010-09-01", "2012-06-30"),
                         ("2022Q4", "2022-06-01", "2023-06-30")):
        ss = s.loc[a0:a1]
        mm = ss.resample("ME").mean().round(2)
        ill[name] = {"S_max": round(float(ss.max()), 3), "S_max_date": str(ss.idxmax().date()),
                     "days_S_ge_1": int((ss >= 1.0).sum()), "S_monthly_mean": {str(k.date())[:7]: float(x) for k, x in mm.items()},
                     "policy_path": {str(k.date())[:7]: float(x) for k, x in pol.loc[a0:a1].items()}}
    R["cycles"] = ill

    def ser(o):
        if isinstance(o, pd.Timestamp):
            return str(o.date())
        if isinstance(o, dict):
            return {str(k): ser(v) for k, v in o.items()}
        if isinstance(o, list):
            return [ser(x) for x in o]
        return o
    out = json.dumps(ser(R), ensure_ascii=False, indent=1, sort_keys=True)
    open(os.path.join(HERE, "results.json"), "w").write(out + "\n")
    print(out)


if __name__ == "__main__":
    main()
