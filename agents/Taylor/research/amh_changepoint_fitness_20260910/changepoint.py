"""
AMH #3 — Change-point detection on the monthly IC series (PAPER-ONLY, diagnostic).

Replaces the current fixed-12M-window LABEL (alive/fading/decayed/flipped, |t|>=2) with a
PROBABILITY that the edge has changed regime, plus an estimated break month.

Detectors (both strictly CAUSAL / online — at month t they see only x[0..t]):
  * CUSUM      : two-sided standardised CUSUM, textbook params k=0.5 (1-sigma shift), h=5.
  * BOCPD      : Adams & MacKay (2007) Bayesian online change-point, Gaussian-NIG conjugate,
                 constant hazard 1/lambda. Output P(run_length <= 2) = P(regime shift).

Ground truth (offline, hindsight — NOT available to the detectors):
  * binary segmentation with a two-sample t-statistic, min segment 12 months, family-wise
    threshold calibrated by 999 permutations of the series (alpha = 0.05).

Incumbent baseline: causal replay of edge_health_monitor.classify() month by month.

ALL parameters below are PRE-REGISTERED textbook defaults, declared before any result was
looked at. No grid search. Sensitivity (h in {4,5,6}, lambda in {24,36,60}) is reported as
robustness, NOT as selection.

Inputs : data/edge_health_ic.csv (canonical fwd-3M IC, written by edge_health_monitor.py)
         data/edge_panel.csv     (to rebuild the control leg + a fwd-1M IC series)
Outputs: cp_detections.csv, cp_eval.csv, cp_prob_latest.csv, changepoint_out.txt
"""
import sys, json
import numpy as np
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
OUT = WC + "/mike/agents/Taylor/research/amh_changepoint_fitness_20260910"

# ---- PRE-REGISTERED PARAMS (textbook defaults, not tuned) -------------------
CUSUM_K, CUSUM_H = 0.5, 5.0
CUSUM_BURN = 24          # months of burn-in before the chart is armed
CUSUM_MINSEG = 6         # months after a reset before a new alarm may fire
BOCPD_LAMBDA = 36        # expected regime length in months (~3y; VN cycle count ~2-3)
BOCPD_SHIFT_R = 2        # P(run_length <= 2) = "a break happened in the last ~2 months"
BOCPD_ALARM_P = 0.50     # alarm threshold on that probability
GT_MINSEG = 12           # offline ground truth: min segment length
GT_NPERM = 999
GT_BLOCK = 3            # block length for the permutation null = fwd-3M overlap (months)
GT_ALPHA = 0.05
MATCH_WIN = 6            # +/- months for calling a detection a hit on a ground-truth break
FP_SD_FRAC = 0.5         # a detection is a FALSE ALARM if |mean(next12)-mean(prev12)| < this*sd

# incumbent rule constants, copied verbatim from edge_health_monitor.py
ROLL_RECENT, T_SIG, MAG_MIN = 12, 2.0, 0.015
MIN_NAMES = 25
QUAL_DROP0 = {"ROIC5Y", "ROE_Min5Y"}   # drop_zero=True signals in edge_health_monitor.SIGNALS

SIGNALS = ["pb_z", "PB", "PE", "ROIC5Y", "FSCORE", "ROE_Min5Y",
           "mom_200", "D_RSI", "D_CMF", "C_L1M"]


# ---------------------------------------------------------------- data ------
def spearman(a, b):
    return pd.Series(a).rank().corr(pd.Series(b).rank())


def monthly_ic_from_panel(df, col, fwd):
    """Re-implementation of edge_health_monitor.monthly_ic (control leg / fwd-1M leg)."""
    out = {}
    for ym, g in df.groupby("ym"):
        s = g[[col, fwd]].dropna()
        if col in QUAL_DROP0:
            s = s[s[col] != 0.0]
        if len(s) < MIN_NAMES or s[col].nunique() < 5:
            continue
        ic = spearman(s[col].values, s[fwd].values)
        if ic is not None and np.isfinite(ic):
            out[ym.to_timestamp()] = ic
    return pd.Series(out).sort_index()


# ------------------------------------------------------------ detectors -----
def cusum_online(x, k=CUSUM_K, h=CUSUM_H, burn=CUSUM_BURN, minseg=CUSUM_MINSEG):
    """Two-sided standardised CUSUM. Causal: mu/sd re-estimated only from data since the
    last reset (>= burn points required). Returns list of (alarm_idx, est_break_idx, side)."""
    n = len(x)
    alarms = []
    ref_start = 0
    sp = sm = 0.0
    sp_start = sm_start = None
    for t in range(n):
        seg = x[ref_start:t]
        if len(seg) < burn:
            continue
        mu, sd = seg.mean(), seg.std(ddof=1)
        if not np.isfinite(sd) or sd <= 0:
            continue
        z = (x[t] - mu) / sd
        new_sp = max(0.0, sp + z - k)
        new_sm = max(0.0, sm - z - k)
        if sp == 0.0 and new_sp > 0.0:
            sp_start = t
        if sm == 0.0 and new_sm > 0.0:
            sm_start = t
        sp, sm = new_sp, new_sm
        if (sp > h or sm > h) and (t - ref_start) >= minseg:
            side = "up" if sp > h else "down"
            est = (sp_start if side == "up" else sm_start)
            alarms.append((t, est if est is not None else t, side))
            ref_start = t          # reset: re-learn the new regime from here
            sp = sm = 0.0
            sp_start = sm_start = None
    return alarms


def bocpd(x, lam=BOCPD_LAMBDA, mu0=0.0, kappa0=1.0, alpha0=1.0, beta0=None):
    """Adams & MacKay 2007 with a Normal-Inverse-Gamma conjugate prior.
    Returns (T x T+1) run-length posterior R[t, r] (causal by construction)."""
    from scipy.stats import t as student_t
    n = len(x)
    if beta0 is None:
        beta0 = max(float(np.var(x[:24], ddof=1)), 1e-6)
    H = 1.0 / lam
    R = np.zeros((n + 1, n + 1))
    R[0, 0] = 1.0
    mu = np.array([mu0]); kap = np.array([kappa0])
    al = np.array([alpha0]); be = np.array([beta0])
    for t in range(n):
        df_ = 2 * al
        scale = np.sqrt(be * (kap + 1.0) / (al * kap))
        pred = student_t.pdf(x[t], df=df_, loc=mu, scale=scale)
        growth = R[t, :t + 1] * pred * (1.0 - H)
        cp = (R[t, :t + 1] * pred * H).sum()
        R[t + 1, 1:t + 2] = growth
        R[t + 1, 0] = cp
        s = R[t + 1, :t + 2].sum()
        if s <= 0:
            R[t + 1, :t + 2] = 0.0; R[t + 1, 0] = 1.0
        else:
            R[t + 1, :t + 2] /= s
        # conjugate update, prepending the fresh-prior branch
        mu_n = np.concatenate(([mu0], (kap * mu + x[t]) / (kap + 1.0)))
        be_n = np.concatenate(([beta0], be + kap * (x[t] - mu) ** 2 / (2.0 * (kap + 1.0))))
        kap_n = np.concatenate(([kappa0], kap + 1.0))
        al_n = np.concatenate(([alpha0], al + 0.5))
        mu, kap, al, be = mu_n, kap_n, al_n, be_n
    return R


def bocpd_pshift(x, lam=BOCPD_LAMBDA, rmax=BOCPD_SHIFT_R):
    R = bocpd(x, lam=lam)
    n = len(x)
    return np.array([R[t + 1, :rmax + 1].sum() for t in range(n)])


def bocpd_alarms(p, thr=BOCPD_ALARM_P, minseg=CUSUM_MINSEG, burn=CUSUM_BURN):
    """Rising-edge alarms on P(shift), with the same burn-in / refractory period as CUSUM."""
    out, last = [], -10**9
    for t in range(len(p)):
        if t < burn:
            continue
        if p[t] >= thr and p[t - 1] < thr and (t - last) >= minseg:
            out.append(t); last = t
    return out


# ------------------------------------------------- offline ground truth -----
def _best_split(x, minseg):
    n = len(x)
    best = (0.0, None)
    for c in range(minseg, n - minseg + 1):
        a, b = x[:c], x[c:]
        va, vb = a.var(ddof=1), b.var(ddof=1)
        se = np.sqrt(va / len(a) + vb / len(b))
        if se <= 0 or not np.isfinite(se):
            continue
        tstat = abs(a.mean() - b.mean()) / se
        if tstat > best[0]:
            best = (tstat, c)
    return best


def _circ_block_perm(x, block, rng):
    """Circular block permutation: preserves short-range autocorrelation while destroying
    any mean shift. Plain i.i.d. permutation would understate the null here, because the
    monthly fwd-3M IC series is OVERLAPPING (3-month forward window sampled monthly) and is
    therefore MA(2)-autocorrelated BY CONSTRUCTION, not by any market regime."""
    n = len(x)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=nb)
    out = np.concatenate([np.take(x, range(s, s + block), mode="wrap") for s in starts])
    return out[:n]


def binseg_gt(x, minseg=GT_MINSEG, nperm=GT_NPERM, alpha=GT_ALPHA, rng=None,
              block=GT_BLOCK):
    """Binary segmentation; threshold = (1-alpha) quantile of the max split-t under a
    BLOCK permutation of the SAME series (calibrated to that series' own noise AND its
    overlap-induced autocorrelation)."""
    rng = rng or np.random.default_rng(20260910)
    null = []
    for _ in range(nperm):
        xp = _circ_block_perm(x, block, rng)
        null.append(_best_split(xp, minseg)[0])
    thr = float(np.quantile(null, 1 - alpha))
    cps = []
    def rec(lo, hi):
        seg = x[lo:hi]
        if len(seg) < 2 * minseg:
            return
        tstat, c = _best_split(seg, minseg)
        if c is None or tstat < thr:
            return
        cps.append(lo + c)
        rec(lo, lo + c); rec(lo + c, hi)
    rec(0, len(x))
    return sorted(cps), thr


# -------------------------------------------------- incumbent baseline ------
def classify(full, recent, tstat):
    if not np.isfinite(tstat) or abs(tstat) < T_SIG:
        return "WEAK"
    if np.sign(recent) != np.sign(full) and abs(recent) >= MAG_MIN:
        return "FLIPPED"
    ratio = abs(recent) / abs(full) if full else 0.0
    if ratio < 0.33:   return "DECAYED"
    if ratio < 0.66:   return "FADING"
    if ratio > 1.30:   return "STRENGTH"
    return "HEALTHY"


def incumbent_labels(s):
    """Causal replay: at month t the monitor sees s[:t+1] only (n<18 -> no verdict)."""
    labs = []
    for t in range(len(s)):
        ic = s.iloc[:t + 1]
        if len(ic) < 18:
            labs.append(None); continue
        full = ic.mean(); sd = ic.std(ddof=1)
        tstat = full / (sd / np.sqrt(len(ic))) if sd and sd > 0 else 0.0
        recent = ic.tail(ROLL_RECENT).mean()
        labs.append(classify(full, recent, tstat))
    return labs


def incumbent_alarm_idx(labs, start):
    """First month at/after `start` where the incumbent label enters an 'edge broke' state."""
    bad = {"FLIPPED", "DECAYED"}
    prev = labs[start - 1] if start > 0 else None
    for t in range(start, len(labs)):
        if labs[t] in bad and labs[t] != prev:
            return t
        prev = labs[t]
    return None


# ------------------------------------------------------------------ main ----
def main():
    ic3 = pd.read_csv(WC + "/data/edge_health_ic.csv", index_col=0, parse_dates=True)
    ic3 = ic3[SIGNALS]

    panel = pd.read_csv(WC + "/data/edge_panel.csv", parse_dates=["time"])
    # replicate edge_health_monitor.load_panel() EXACTLY: drop NaN fwd, then winsorise
    # the forward return at 0.5%/99.5% BEFORE ranking (this clip is why a naive rebuild
    # misses the pinned series by ~6e-3 — it changes ties in the extreme tails).
    panel = panel[panel["fwd_3m"].notna()].copy()
    lo, hi = panel["fwd_3m"].quantile([0.005, 0.995])
    panel["fwd_3m"] = panel["fwd_3m"].clip(lo, hi)
    lo1, hi1 = panel["fwd_1m"].quantile([0.005, 0.995])
    panel["fwd_1m"] = panel["fwd_1m"].clip(lo1, hi1)
    panel["ym"] = panel["time"].dt.to_period("M")

    print("=" * 78)
    print("CONTROL LEG — rebuild fwd-3M IC from the panel, must match the pinned artifact")
    print("=" * 78)
    maxdiff = 0.0
    ic1 = {}
    for c in SIGNALS:
        rebuilt = monthly_ic_from_panel(panel, c, "fwd_3m")
        joined = pd.concat([ic3[c].rename("pinned"), rebuilt.rename("rebuilt")],
                           axis=1).dropna()
        d = float((joined["pinned"] - joined["rebuilt"]).abs().max())
        maxdiff = max(maxdiff, d)
        ic1[c] = monthly_ic_from_panel(panel, c, "fwd_1m")
    ic1 = pd.DataFrame(ic1)
    print(f"control-leg max |pinned - rebuilt| fwd-3M IC = {maxdiff:.2e}   "
          f"({'PASS' if maxdiff < 1e-9 else 'FAIL'})")
    print(f"fwd-3M series: {len(ic3)} months {ic3.index.min():%Y-%m} -> {ic3.index.max():%Y-%m}")
    print(f"fwd-1M series: {len(ic1)} months {ic1.index.min():%Y-%m} -> {ic1.index.max():%Y-%m}")

    # ---- N discipline: the monthly fwd-3M IC series is NOT 150 independent months ----
    print("\n" + "=" * 78)
    print("N DISCIPLINE — the fwd-3M IC series is OVERLAPPING (MA(2) by construction)")
    print("=" * 78)
    print(f"{'signal':<11}{'ac1_3m':>8}{'ac2_3m':>8}{'n_eff_3m':>10}"
          f"{'ac1_1m':>8}{'n_eff_1m':>10}")
    for c in SIGNALS:
        s3 = ic3[c].dropna(); s1 = ic1[c].dropna()
        a1, a2 = s3.autocorr(1), s3.autocorr(2)
        # Bartlett/Bayley effective sample size for the mean of an autocorrelated series
        neff3 = len(s3) * (1 - a1) / (1 + a1)
        b1 = s1.autocorr(1)
        neff1 = len(s1) * (1 - b1) / (1 + b1)
        print(f"{c:<11}{a1:>8.2f}{a2:>8.2f}{neff3:>10.0f}{b1:>8.2f}{neff1:>10.0f}")
    print("  -> the incumbent |t|>=2 gate divides by sqrt(150). At ac1~0.6 the honest divisor "
          "is sqrt(~35),\n     i.e. the incumbent t-stat is inflated ~2x. Same caveat applies to "
          "every verdict below.")

    det_rows, eval_rows, latest_rows = [], [], []

    for horizon, mat in (("fwd_3m", ic3), ("fwd_1m", ic1)):
        print("\n" + "=" * 78)
        print(f"HORIZON = {horizon}")
        print("=" * 78)
        for sig in SIGNALS:
            s = mat[sig].dropna()
            x = s.values.astype(float)
            idx = s.index
            if len(x) < 40:
                continue

            gt, gt_thr = binseg_gt(x)
            cu = cusum_online(x)
            p_shift = bocpd_pshift(x)
            bo = bocpd_alarms(p_shift)
            labs = incumbent_labels(s)

            sd_pool = float(np.std(x, ddof=1))

            def reversal_flag(i):
                """FALSE ALARM if the 12M mean before/after the detection barely moved."""
                a = x[max(0, i - 12):i]
                b = x[i:i + 12]
                if len(a) < 6 or len(b) < 6:
                    return "unknown"
                return "false" if abs(b.mean() - a.mean()) < FP_SD_FRAC * sd_pool else "true"

            for kind, alarms in (("CUSUM", [(a, e) for a, e, _ in cu]),
                                 ("BOCPD", [(a, a) for a in bo])):
                for a_i, e_i in alarms:
                    near = [g for g in gt if abs(g - a_i) <= MATCH_WIN]
                    det_rows.append(dict(
                        horizon=horizon, signal=sig, detector=kind,
                        alarm_month=idx[a_i].strftime("%Y-%m"),
                        est_break_month=idx[e_i].strftime("%Y-%m"),
                        matched_gt=(idx[near[0]].strftime("%Y-%m") if near else ""),
                        lag_vs_gt=(a_i - near[0]) if near else np.nan,
                        sustained=reversal_flag(a_i),
                        p_shift=round(float(p_shift[a_i]), 3) if kind == "BOCPD" else np.nan,
                    ))

            # per ground-truth break: who saw it, and how late
            for g in gt:
                row = dict(horizon=horizon, signal=sig,
                           gt_break=idx[g].strftime("%Y-%m"))
                cu_hit = [a for a, _, _ in cu if 0 <= a - g <= 24]
                bo_hit = [a for a in bo if 0 <= a - g <= 24]
                inc = incumbent_alarm_idx(labs, g)
                row["cusum_lag_m"] = (cu_hit[0] - g) if cu_hit else np.nan
                row["bocpd_lag_m"] = (bo_hit[0] - g) if bo_hit else np.nan
                row["incumbent_lag_m"] = (inc - g) if (inc is not None and inc - g <= 24) else np.nan
                row["gt_thr_t"] = round(gt_thr, 2)
                row["mean_before"] = round(float(x[max(0, g - 12):g].mean()), 4)
                row["mean_after"] = round(float(x[g:g + 12].mean()), 4)
                eval_rows.append(row)

            latest_rows.append(dict(
                horizon=horizon, signal=sig,
                asof=idx[-1].strftime("%Y-%m"),
                P_regime_shift=round(float(p_shift[-1]), 3),
                P_max_last6=round(float(p_shift[-6:].max()), 3),
                cusum_last_alarm=(idx[cu[-1][0]].strftime("%Y-%m") if cu else ""),
                incumbent_label=labs[-1],
                ic_recent12=round(float(x[-12:].mean()), 4),
                ic_full=round(float(x.mean()), 4),
                n_gt_breaks=len(gt),
            ))
            print(f"{sig:<10} gt_breaks={[idx[g].strftime('%Y-%m') for g in gt]}  "
                  f"thr_t={gt_thr:.2f}  cusum={len(cu)}  bocpd={len(bo)}  "
                  f"P_shift_now={p_shift[-1]:.2f}  incumbent={labs[-1]}")

    D = pd.DataFrame(det_rows); E = pd.DataFrame(eval_rows); L = pd.DataFrame(latest_rows)
    D.to_csv(OUT + "/cp_detections.csv", index=False)
    E.to_csv(OUT + "/cp_eval.csv", index=False)
    L.to_csv(OUT + "/cp_prob_latest.csv", index=False)

    print("\n" + "=" * 78)
    print("SUMMARY — false-alarm rate (detection NOT followed by a sustained 12M mean shift)")
    print("=" * 78)
    for h in ("fwd_3m", "fwd_1m"):
        sub = D[(D.horizon == h) & (D.sustained != "unknown")]
        for k in ("CUSUM", "BOCPD"):
            ss = sub[sub.detector == k]
            if len(ss) == 0:
                continue
            fa = (ss.sustained == "false").mean()
            matched = (ss.matched_gt != "").mean()
            print(f"{h} {k:<6} n_alarms={len(ss):3d}  false-alarm={fa:5.1%}  "
                  f"matched a hindsight break (+/-{MATCH_WIN}m)={matched:5.1%}")

    print("\n" + "=" * 78)
    print("SUMMARY — detection LAG vs the hindsight break (months; lower = earlier warning)")
    print("=" * 78)
    for h in ("fwd_3m", "fwd_1m"):
        sub = E[E.horizon == h]
        if len(sub) == 0:
            continue
        print(f"\n[{h}]  n_ground_truth_breaks = {len(sub)}")
        for c in ("cusum_lag_m", "bocpd_lag_m", "incumbent_lag_m"):
            v = sub[c].dropna()
            print(f"  {c:<18} detected {len(v):2d}/{len(sub):2d}  "
                  f"median={v.median() if len(v) else float('nan'):.1f}  "
                  f"mean={v.mean() if len(v) else float('nan'):.1f}")
        both = sub.dropna(subset=["bocpd_lag_m", "incumbent_lag_m"])
        if len(both):
            print(f"  BOCPD vs incumbent on the {len(both)} breaks BOTH caught: "
                  f"median delta = {(both.bocpd_lag_m - both.incumbent_lag_m).median():+.1f} months "
                  f"(negative = BOCPD earlier)")
        both2 = sub.dropna(subset=["cusum_lag_m", "incumbent_lag_m"])
        if len(both2):
            print(f"  CUSUM vs incumbent on the {len(both2)} breaks BOTH caught: "
                  f"median delta = {(both2.cusum_lag_m - both2.incumbent_lag_m).median():+.1f} months")

    print("\n" + "=" * 78)
    print("LATEST STATE — P(regime shift) as of the last realised month")
    print("=" * 78)
    print(L.to_string(index=False))

    # ---- sensitivity (robustness, NOT selection) ----
    print("\n" + "=" * 78)
    print("SENSITIVITY — n_alarms / false-alarm rate under other textbook params (fwd_3m)")
    print("=" * 78)
    for h_ in (4.0, 5.0, 6.0):
        na = fa_n = fa_d = 0
        for sig in SIGNALS:
            s = ic3[sig].dropna(); x = s.values.astype(float)
            sd = float(np.std(x, ddof=1))
            for a, _, _ in cusum_online(x, h=h_):
                na += 1
                aa, bb = x[max(0, a - 12):a], x[a:a + 12]
                if len(aa) >= 6 and len(bb) >= 6:
                    fa_d += 1
                    if abs(bb.mean() - aa.mean()) < FP_SD_FRAC * sd:
                        fa_n += 1
        print(f"  CUSUM h={h_:.0f}: n_alarms={na:3d}  false-alarm={fa_n/fa_d:5.1%}" if fa_d else "")
    for lam in (24, 36, 60):
        na = fa_n = fa_d = 0
        for sig in SIGNALS:
            s = ic3[sig].dropna(); x = s.values.astype(float)
            sd = float(np.std(x, ddof=1))
            p = bocpd_pshift(x, lam=lam)
            for a in bocpd_alarms(p):
                na += 1
                aa, bb = x[max(0, a - 12):a], x[a:a + 12]
                if len(aa) >= 6 and len(bb) >= 6:
                    fa_d += 1
                    if abs(bb.mean() - aa.mean()) < FP_SD_FRAC * sd:
                        fa_n += 1
        print(f"  BOCPD lambda={lam:2d}: n_alarms={na:3d}  false-alarm={fa_n/fa_d:5.1%}" if fa_d else "")


if __name__ == "__main__":
    main()
