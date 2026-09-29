"""CCS Phase 1 — conditional expectancy map for the 7 pre-registered hypotheses.

Job Taylor_20260905_141801.  Input = the Phase 0 trade ledger (job Taylor_20260905_135003).
NO sizing backtest is run here (that is Phase 2); this maps win-rate / expectancy / avg-R only.

Six design decisions locked by Mike BEFORE any number was looked at (dispatch 2026-09-05):
  D1  ABANDONED_REFUND excluded from the PRIMARY measure, reported as a parallel sensitivity
      branch.  A conclusion that FLIPS SIGN between the two branches = hypothesis not alive.
  D2  H2 "recovery" redefined on BREADTH (tercile leaves LOW into MID/HIGH within <=21 sessions
      before signal_date), not on a DT5G upgrade.  Public amendment => N_trials = 7, not 6.
  D3  H5 is DESCRIPTIVE-ONLY (21 episodes on the upsize side is a structural ceiling).
  D4  H3 concludes at BOTH-books or LAG level only; BAL alone is descriptive-only.
  D5  H6 must control for sig_n_cands (the TOP/MID/BOTTOM 1098/544/308 split is engine
      construction, not signal).
  D6  rating_8l is a descriptive column, never a discriminator.

Statistics: N counted as INDEPENDENT EPISODES (same convention as Phase 0 — entries in the same
bucket separated by <=10 trading sessions are one episode).  All contrasts are episode-CLUSTER
bootstrapped; effect sizes are reported with 95% CI, never a bare p-value.
"""
import json
import os

import numpy as np
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
P0 = os.path.join(WC, "mike/agents/Taylor/research/ccs_phase0_Taylor_20260905_135003")
OUT = os.path.join(WC, "mike/agents/Taylor/research/ccs_phase1_Taylor_20260905_141801")
PIN = os.path.join(WC, "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_"
                       "etfliqcustompitg_wtnamecap_advprice_exp_repin0803_price_univpit.csv")

GAP = 10                 # episode gap, sessions (Phase 0 headline)
MIN_EP = 30              # below this: descriptive only
B = 10000                # bootstrap resamples
SEED = 20260905
N_TRIALS = 7             # 6 pre-registered + 1 public amendment (D2)
K_UPSIZE = 1.5           # optimistic end of the Phase 2 range, for the feasibility bound
NOISE_FLOOR_PP = 0.385   # measured harness noise, margin-valuation-spread 2026-08-23
IS_END = 2019            # IS = 2014..2019, OOS = 2020+

rng = np.random.default_rng(SEED)

# --------------------------------------------------------------------------- load
d = pd.read_csv(os.path.join(P0, "trade_ledger_bal_lag_exp.csv"),
                parse_dates=["signal_date", "entry_fill_date", "exit_date"])
cal = pd.read_csv(os.path.join(P0, "breadth_pit_frozen_exp.csv"), parse_dates=["time"])
cal = cal.sort_values("time").reset_index(drop=True)
sessions = pd.DatetimeIndex(cal.time)
sidx = {t: i for i, t in enumerate(sessions)}
d["sess_i"] = d.signal_date.map(sidx)
d["year"] = d.signal_date.dt.year

# --- D2 amendment: breadth-based recovery, computed on the calendar then read at t-1 ------
bt = cal.btile.to_numpy(dtype=object)
rec_cal = np.zeros(len(bt), dtype=bool)
for i in range(len(bt)):
    if bt[i] in ("MID", "HIGH"):
        rec_cal[i] = "LOW" in bt[max(0, i - 21):i]
# breadth enters the ledger at t-1, so recovery is read at t-1 too
d["recovery_breadth"] = d.sess_i.map(
    lambda i: bool(rec_cal[int(i) - 1]) if pd.notna(i) and int(i) >= 1 else False)
d["recovery_dt5g"] = d.sessions_since_dt5g_upgrade <= 10          # original H2/H5 axis

_r = d.r_multiple_vol.to_numpy(float)
_fin = _r[np.isfinite(_r) & (d.exit_reason != "ABANDONED_REFUND").to_numpy()]
R_LO, R_HI = np.percentile(_fin, [1, 99])
d["R_w"] = np.clip(np.where(np.isfinite(_r), _r, np.nan), R_LO, R_HI)
N_R_CLIPPED = int((np.isfinite(_r) & ((_r < R_LO) | (_r > R_HI))).sum())
N_R_INF = int((~np.isfinite(_r)).sum())

PRIMARY = d[d.exit_reason != "ABANDONED_REFUND"].copy()
SENS = d.copy()

# --------------------------------------------------------------------------- episode helper
def ep_ids(sub, gap=GAP):
    """Episode id per row: entry sessions separated by more than `gap` sessions start a new one."""
    s = sub.sess_i.to_numpy(dtype=float)
    order = np.argsort(s, kind="mergesort")
    ids = np.empty(len(s), dtype=np.int64)
    cur, prev = -1, None
    for pos in order:
        v = s[pos]
        if prev is None or (v - prev) > gap:
            cur += 1
        ids[pos] = cur
        prev = v
    return ids


def agg_by_ep(vals, weights, eids):
    """Per-episode sums so a bootstrap over episodes is an exact weighted mean."""
    n = eids.max() + 1 if len(eids) else 0
    sw = np.bincount(eids, weights=weights, minlength=n)
    sv = np.bincount(eids, weights=vals * weights, minlength=n)
    return sv, sw


def boot_diff(a, b, col="ret", weight=None, B=B, seed=SEED):
    """Episode-cluster bootstrap of mean(a[col]) - mean(b[col]).  Returns point, lo, hi, p."""
    out = {}
    parts = []
    for g in (a, b):
        w = np.ones(len(g)) if weight is None else g[weight].to_numpy(dtype=float)
        sv, sw = agg_by_ep(g[col].to_numpy(dtype=float), w, ep_ids(g))
        parts.append((sv, sw))
    pt = parts[0][0].sum() / parts[0][1].sum() - parts[1][0].sum() / parts[1][1].sum()
    r = np.random.default_rng(seed)
    draws = np.empty(B)
    for i in range(B):
        m = []
        for sv, sw in parts:
            sel = r.integers(0, len(sv), len(sv))
            m.append(sv[sel].sum() / sw[sel].sum())
        draws[i] = m[0] - m[1]
    lo, hi = np.percentile(draws, [2.5, 97.5])
    p = 2 * min((draws <= 0).mean(), (draws >= 0).mean())
    out.update(diff=pt, lo=lo, hi=hi, p_boot=min(1.0, p))
    return out


def desc(sub):
    if len(sub) == 0:
        return dict(n=0, n_ep=0, win=np.nan, exp=np.nan, exp_cw=np.nan, avg_R=np.nan,
                    med_ret=np.nan, med_hold=np.nan, cap_bn=0.0, years=0)
    e = ep_ids(sub)
    cost = sub.cost_vnd.to_numpy(dtype=float)
    return dict(n=int(len(sub)), n_ep=int(e.max() + 1),
                win=float((sub.ret > 0).mean()), exp=float(sub.ret.mean()),
                exp_cw=float(np.average(sub.ret, weights=cost)),
                avg_R=float(sub.R_w.mean(skipna=True)), med_R=float(sub.R_w.median(skipna=True)),
                mean_hold=float(sub.holding_sessions.mean()),
                med_ret=float(sub.ret.median()), med_hold=float(sub.holding_sessions.median()),
                cap_bn=float(cost.sum() / 1e9), years=int(sub.year.nunique()))


# --------------------------------------------------------------------------- book NAV for feasibility
dl = pd.read_csv(PIN, low_memory=False)
dl = dl[dl.record_type == "DAILY"].copy()
dl["ymd"] = pd.to_datetime(dl.ymd)
dl["year"] = dl.ymd.dt.year
for c in ("nav_bal_ref", "nav_lag_ref", "combined_nav", "cap_bal", "cap_lag"):
    dl[c] = pd.to_numeric(dl[c], errors="coerce")
navy = dl.groupby("year").agg(nav_bal=("nav_bal_ref", "mean"), nav_lag=("nav_lag_ref", "mean"),
                              cap_bal=("cap_bal", "mean"), cap_lag=("cap_lag", "mean"),
                              comb=("combined_nav", "mean"))
navy["w_bal"] = navy.cap_bal / navy.comb
navy["w_lag"] = navy.cap_lag / navy.comb


def feasibility_pp(treat, rest, k=K_UPSIZE):
    """Rough upper bound on dCAGR (pp/yr) of moving (k-1)*capital into `treat`, funded from `rest`.

    dPnL(book, year) = (k-1) * capital_deployed_in_treat * (e_treat - e_rest), cost-weighted.
    Converted to a book-return delta by that year's average book NAV, then mixed into the combined
    NAV by the allocator's own realised weights.  First-order and OPTIMISTIC: ignores compounding,
    path, capacity (%ADV), and the drawdown cost of concentrating.
    """
    if len(treat) == 0 or len(rest) == 0:
        return np.nan
    de = (np.average(treat.ret, weights=treat.cost_vnd)
          - np.average(rest.ret, weights=rest.cost_vnd))
    per_year = []
    for y in sorted(set(treat.year) | set(rest.year)):
        if y not in navy.index:
            continue
        row, tot = navy.loc[y], 0.0
        for bk, navc, wc in (("BAL", "nav_bal", "w_bal"), ("LAG", "nav_lag", "w_lag")):
            cap_t = treat[(treat.year == y) & (treat.book == bk)].cost_vnd.sum()
            cap_r = rest[(rest.year == y) & (rest.book == bk)].cost_vnd.sum()
            # cannot move more capital than the funding group actually deployed that year
            moved = min((k - 1) * cap_t, cap_r)
            if moved > 0 and row[navc] > 0:
                tot += row[wc] * moved * de / row[navc]
        per_year.append(tot)
    return float(np.mean(per_year) * 100) if per_year else np.nan


# --------------------------------------------------------------------------- hypotheses
def m_h1(f):   return (f.dd52 <= -0.20), (f.dd52 > -0.20)
def m_h2(f):
    t = (f.ey_tercile == "CHEAP") & f.recovery_breadth
    return t, (f.ey_tercile.notna() & ~t)
def m_h2o(f):
    t = (f.ey_tercile == "CHEAP") & f.recovery_dt5g
    return t, (f.ey_tercile.notna() & ~t)
def m_h3(f):   return (f.breadth_tercile_tm1 == "LOW"), (f.breadth_tercile_tm1.isin(["MID", "HIGH"]))
def m_h4(f):
    t = (f.lag_surprise_tercile == "HIGH") & (f.ey_tercile == "CHEAP")
    return t, (f.lag_surprise_tercile.notna() & f.ey_tercile.notna() & ~t)
def m_h5(f):   return (f.sessions_since_dt5g_upgrade <= 10), (f.sessions_since_dt5g_upgrade > 10)
def m_h6(f):   return (f.sig_rank_tercile == "TOP"), (f.sig_rank_tercile == "BOTTOM")

HYP = [
    # id, label, scope-book, mask fn, status
    ("H1",  "dd52 <= -20% at entry (per-name washout)",              "BOTH", m_h1, "TESTABLE"),
    ("H2",  "ey=CHEAP x breadth-recovery (AMENDED, D2)",             "BOTH", m_h2, "TESTABLE"),
    ("H2o", "ey=CHEAP x DT5G-upgrade recovery (ORIGINAL, superseded)", "BOTH", m_h2o, "DESCRIPTIVE"),
    ("H3",  "breadth tercile LOW (t-1) vs MID/HIGH",                 "BOTH", m_h3, "TESTABLE"),
    ("H4",  "LAG: surprise HIGH x ey CHEAP (interaction)",           "LAG",  m_h4, "TESTABLE"),
    ("H5",  "<=10 sessions after a DT5G upgrade",                    "BOTH", m_h5, "DESCRIPTIVE"),
    ("H6",  "in-book signal rank TOP vs BOTTOM",                     "BOTH", m_h6, "TESTABLE"),
]


def scope(f, bk):
    return f if bk == "BOTH" else f[f.book == bk]


def run_contrast(f, mfn, bk, seed=SEED, label=""):
    g = scope(f, bk)
    mt, mc = mfn(g)
    t, c = g[mt.fillna(False)], g[mc.fillna(False)]
    row = dict(bucket=label, n_t=len(t), n_c=len(c))
    row.update({f"t_{k}": v for k, v in desc(t).items()})
    row.update({f"c_{k}": v for k, v in desc(c).items()})
    if len(t) and len(c):
        row.update(boot_diff(t, c, "ret", None, B, seed))
        wb = boot_diff(t, c, "ret", "cost_vnd", 2000, seed + 1)
        row["diff_cw"] = wb["diff"]; row["cw_lo"] = wb["lo"]; row["cw_hi"] = wb["hi"]
        row["win_diff"] = float((t.ret > 0).mean() - (c.ret > 0).mean())
        comp = g.drop(index=t.index)          # everything else in scope funds the upsize
        row["feas_pp"] = feasibility_pp(t, comp)
        row["feas_pp_vs_ctrl"] = feasibility_pp(t, c)
    return row, t, c


def split_stats(t, c, seed=SEED):
    """IS / OOS point estimates and the per-year leave-one-out sign profile."""
    o = {}
    for tag, lo, hi in (("IS", 2014, IS_END), ("OOS", IS_END + 1, 2100)):
        tt, cc = t[t.year.between(lo, hi)], c[c.year.between(lo, hi)]
        o[f"{tag}_n_t"], o[f"{tag}_n_c"] = len(tt), len(cc)
        o[f"{tag}_ep_t"] = int(ep_ids(tt).max() + 1) if len(tt) else 0
        o[f"{tag}_diff"] = float(tt.ret.mean() - cc.ret.mean()) if len(tt) and len(cc) else np.nan
    yrs = sorted(set(t.year) | set(c.year))
    loo = {}
    for y in yrs:
        tt, cc = t[t.year != y], c[c.year != y]
        loo[int(y)] = float(tt.ret.mean() - cc.ret.mean()) if len(tt) and len(cc) else np.nan
    o["loo"] = loo
    full = float(t.ret.mean() - c.ret.mean())
    vals = [v for v in loo.values() if np.isfinite(v)]
    o["loo_same_sign"] = bool(vals) and all(np.sign(v) == np.sign(full) for v in vals)
    o["loo_min"], o["loo_max"] = (min(vals), max(vals)) if vals else (np.nan, np.nan)
    # per-year contribution: which single year carries the effect
    per_y = {int(y): float(t[t.year == y].ret.mean() - c[c.year == y].ret.mean())
             if len(t[t.year == y]) and len(c[c.year == y]) else np.nan for y in yrs}
    o["per_year"] = per_y
    return o


# --------------------------------------------------------------------------- main sweep
report = {"meta": {"job": "Taylor_20260905_141801", "n_trials": N_TRIALS, "seed": SEED,
                   "episode_gap_sessions": GAP, "min_episodes": MIN_EP, "bootstrap": B,
                   "k_upsize_for_feasibility": K_UPSIZE, "noise_floor_pp": NOISE_FLOOR_PP,
                   "primary_excludes": "ABANDONED_REFUND (D1)",
                   "n_primary": int(len(PRIMARY)), "n_sensitivity": int(len(SENS)),
                   "R_winsor_bounds": [float(R_LO), float(R_HI)],
                   "R_rows_clipped": N_R_CLIPPED, "R_rows_nonfinite": N_R_INF}}

rows, detail = [], {}
for hid, lab, bk, mfn, status in HYP:
    r_p, t_p, c_p = run_contrast(PRIMARY, mfn, bk, label=f"{hid} PRIMARY")
    r_s, t_s, c_s = run_contrast(SENS, mfn, bk, label=f"{hid} +ABANDONED")
    for r in (r_p, r_s):
        r.update(hypothesis=hid, book=bk, status=status, desc=lab)
    rows += [r_p, r_s]
    sp = split_stats(t_p, c_p)
    flip = (np.isfinite(r_p.get("diff", np.nan)) and np.isfinite(r_s.get("diff", np.nan))
            and np.sign(r_p["diff"]) != np.sign(r_s["diff"]))
    detail[hid] = dict(label=lab, book=bk, status=status, primary=r_p, sensitivity=r_s,
                       sign_flip_vs_sensitivity=bool(flip), splits=sp)

# ---- per-book descriptive breakdown for every hypothesis (D4: BAL alone never concludes)
book_rows = []
for hid, lab, bk, mfn, status in HYP:
    for b in (["BAL", "LAG"] if bk == "BOTH" else [bk]):
        r, _, _ = run_contrast(PRIMARY, mfn, b, label=f"{hid} {b} PRIMARY")
        r.update(hypothesis=hid, book=b, status="DESCRIPTIVE (per-book split)")
        book_rows.append(r)

# ---- H6 with sig_n_cands controlled (D5)
h6 = PRIMARY[PRIMARY.sig_rank_tercile.isin(["TOP", "BOTTOM"]) & PRIMARY.sig_n_cands.notna()].copy()
edges = [0, 4, 8, 17, 10 ** 9]                       # quartile-ish cuts of sig_n_cands
h6["strat"] = pd.cut(h6.sig_n_cands, bins=edges, labels=["1-4", "5-8", "9-17", "18+"])
strat_rows, num, den = [], 0.0, 0.0
for s, g in h6.groupby("strat", observed=True):
    t, c = g[g.sig_rank_tercile == "TOP"], g[g.sig_rank_tercile == "BOTTOM"]
    if len(t) == 0 or len(c) == 0:
        strat_rows.append(dict(strat=str(s), n_top=len(t), n_bot=len(c), diff=np.nan)); continue
    dd = float(t.ret.mean() - c.ret.mean())
    w = len(t) * len(c) / (len(t) + len(c))          # Mantel-Haenszel-style precision weight
    num += w * dd; den += w
    strat_rows.append(dict(strat=str(s), n_top=len(t), n_bot=len(c),
                           ep_top=int(ep_ids(t).max() + 1), ep_bot=int(ep_ids(c).max() + 1),
                           exp_top=float(t.ret.mean()), exp_bot=float(c.ret.mean()), diff=dd,
                           win_top=float((t.ret > 0).mean()), win_bot=float((c.ret > 0).mean())))
h6_ctrl = num / den if den else np.nan
# stratified bootstrap CI: resample episodes inside each stratum-arm
r = np.random.default_rng(SEED + 7)
arms = []
for s, g in h6.groupby("strat", observed=True):
    t, c = g[g.sig_rank_tercile == "TOP"], g[g.sig_rank_tercile == "BOTTOM"]
    if len(t) == 0 or len(c) == 0:
        continue
    arms.append((agg_by_ep(t.ret.to_numpy(float), np.ones(len(t)), ep_ids(t)),
                 agg_by_ep(c.ret.to_numpy(float), np.ones(len(c)), ep_ids(c)),
                 len(t) * len(c) / (len(t) + len(c))))
draws = np.empty(B)
for i in range(B):
    n_, d_ = 0.0, 0.0
    for (tv, tw), (cv, cw), w in arms:
        st = r.integers(0, len(tv), len(tv)); sc = r.integers(0, len(cv), len(cv))
        n_ += w * (tv[st].sum() / tw[st].sum() - cv[sc].sum() / cw[sc].sum()); d_ += w
    draws[i] = n_ / d_
h6_lo, h6_hi = np.percentile(draws, [2.5, 97.5])
h6_p = 2 * min((draws <= 0).mean(), (draws >= 0).mean())

R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUT, "ccs_phase1_contrasts_exp.csv"), index=False)
pd.DataFrame(book_rows).to_csv(os.path.join(OUT, "ccs_phase1_perbook_exp.csv"), index=False)
pd.DataFrame(strat_rows).to_csv(os.path.join(OUT, "ccs_phase1_h6_stratified_exp.csv"), index=False)
report["h6_controlled"] = dict(diff=float(h6_ctrl), lo=float(h6_lo), hi=float(h6_hi),
                               p_boot=float(min(1.0, h6_p)), strata=strat_rows,
                               naive_diff=float(detail["H6"]["primary"].get("diff", np.nan)))
report["hypotheses"] = detail
with open(os.path.join(OUT, "ccs_phase1_report_exp.json"), "w") as fh:
    json.dump(report, fh, indent=2, default=float)

# --------------------------------------------------------------------------- print
pd.set_option("display.width", 250, "display.max_columns", 60)
print("=" * 118)
print(f"CCS PHASE 1 — conditional expectancy map | primary N={len(PRIMARY)} trades "
      f"(ABANDONED_REFUND excluded, D1) | sensitivity N={len(SENS)} | N_trials={N_TRIALS}")
print("=" * 118)
show = ["hypothesis", "bucket", "status", "n_t", "t_n_ep", "t_win", "t_exp", "t_avg_R", "t_med_R",
        "n_c", "c_n_ep", "c_win", "c_exp", "c_avg_R", "c_med_R", "diff", "lo", "hi", "p_boot", "feas_pp"]
print(R[show].round(4).to_string(index=False))
print("\n--- per-book descriptive split (D4: BAL alone never concludes) ---")
pb = pd.DataFrame(book_rows)
print(pb[["hypothesis", "book", "n_t", "t_n_ep", "t_win", "t_exp", "n_c", "c_n_ep", "c_win",
          "c_exp", "diff", "lo", "hi", "p_boot"]].round(4).to_string(index=False))
print("\n--- H6 with sig_n_cands controlled (D5) ---")
print(pd.DataFrame(strat_rows).round(4).to_string(index=False))
print(f"  naive TOP-BOTTOM  = {detail['H6']['primary'].get('diff', float('nan')):+.4f}")
print(f"  stratified TOP-BOTTOM = {h6_ctrl:+.4f}  95%CI [{h6_lo:+.4f}, {h6_hi:+.4f}]  "
      f"p_boot={h6_p:.4f}")
print("\n--- IS / OOS + leave-one-year-out ---")
for hid, dd in detail.items():
    s = dd["splits"]
    print(f"\n[{hid}] {dd['label']}  ({dd['status']})")
    print(f"   full diff={dd['primary'].get('diff', float('nan')):+.4f} | "
          f"IS(2014-{IS_END}) {s['IS_diff']:+.4f} (n_t={s['IS_n_t']}, ep={s['IS_ep_t']}) | "
          f"OOS(2020+) {s['OOS_diff']:+.4f} (n_t={s['OOS_n_t']}, ep={s['OOS_ep_t']}) | "
          f"same sign={np.sign(s['IS_diff']) == np.sign(s['OOS_diff'])}")
    print(f"   LOO same sign={s['loo_same_sign']}  range=[{s['loo_min']:+.4f}, {s['loo_max']:+.4f}]"
          f" | sensitivity sign flip={dd['sign_flip_vs_sensitivity']}")
    py = " ".join(f"{y}:{v:+.3f}" for y, v in s["per_year"].items() if np.isfinite(v))
    print(f"   per-year diff: {py}")
print(f"\n[files] {OUT}")


# --------------------------------------------------------------------------- survival screen
def stratified_diff(g, tmask, cmask, seed, Bn=B):
    """TOP/BOTTOM-style contrast with sig_n_cands held fixed (D5).  Returns diff + CI + p."""
    gg = g[tmask.fillna(False) | cmask.fillna(False)].copy()
    gg["is_t"] = tmask.reindex(gg.index).fillna(False)
    gg["strat"] = pd.cut(gg.sig_n_cands, bins=edges, labels=["1-4", "5-8", "9-17", "18+"])
    arms, num, den = [], 0.0, 0.0
    for s_, sub in gg.groupby("strat", observed=True):
        t_, c_ = sub[sub.is_t], sub[~sub.is_t]
        if len(t_) == 0 or len(c_) == 0:
            continue
        w = len(t_) * len(c_) / (len(t_) + len(c_))
        num += w * (t_.ret.mean() - c_.ret.mean()); den += w
        arms.append((agg_by_ep(t_.ret.to_numpy(float), np.ones(len(t_)), ep_ids(t_)),
                     agg_by_ep(c_.ret.to_numpy(float), np.ones(len(c_)), ep_ids(c_)), w))
    if not arms:
        return dict(diff=np.nan, lo=np.nan, hi=np.nan, p_boot=np.nan)
    rr = np.random.default_rng(seed)
    dr = np.empty(Bn)
    for i in range(Bn):
        n_, d_ = 0.0, 0.0
        for (tv, tw), (cv, cw), w in arms:
            st = rr.integers(0, len(tv), len(tv)); sc = rr.integers(0, len(cv), len(cv))
            n_ += w * (tv[st].sum() / tw[st].sum() - cv[sc].sum() / cw[sc].sum()); d_ += w
        dr[i] = n_ / d_
    lo_, hi_ = np.percentile(dr, [2.5, 97.5])
    return dict(diff=num / den, lo=lo_, hi=hi_,
                p_boot=float(min(1.0, 2 * min((dr <= 0).mean(), (dr >= 0).mean()))))


survive = []
for hid, lab, bk, mfn, status in HYP:
    g = scope(PRIMARY, bk)
    mt, mc = mfn(g)
    t, c = g[mt.fillna(False)], g[mc.fillna(False)]
    s = detail[hid]["splits"]
    ep_t, ep_c = desc(t)["n_ep"], desc(c)["n_ep"]
    oos_t, oos_c = t[t.year > IS_END], c[c.year > IS_END]
    oos = boot_diff(oos_t, oos_c, "ret", None, 4000, SEED + 3) if len(oos_t) and len(oos_c) else {}
    rv = boot_diff(t[t.R_w.notna()], c[c.R_w.notna()], "R_w", None, 3000, SEED + 5)
    same_sign = bool(np.isfinite(s["IS_diff"]) and np.isfinite(s["OOS_diff"])
                     and np.sign(s["IS_diff"]) == np.sign(s["OOS_diff"]))
    p = detail[hid]["primary"].get("p_boot", np.nan)
    fails = []
    if status == "DESCRIPTIVE":
        fails.append("descriptive-only by design decision")
    if min(ep_t, ep_c) < MIN_EP:
        fails.append(f"N thin (min arm {min(ep_t, ep_c)} episodes < {MIN_EP})")
    if not same_sign:
        fails.append("IS/OOS opposite sign")
    if not s["loo_same_sign"]:
        fails.append("leave-one-year-out flips sign")
    if detail[hid]["sign_flip_vs_sensitivity"]:
        fails.append("sign flips vs +ABANDONED_REFUND branch (D1)")
    survive.append(dict(hypothesis=hid, label=lab, book=bk, status=status,
                        ep_t=ep_t, ep_c=ep_c, diff=detail[hid]["primary"].get("diff", np.nan),
                        lo=detail[hid]["primary"].get("lo", np.nan),
                        hi=detail[hid]["primary"].get("hi", np.nan), p_boot=p,
                        p_bonf=min(1.0, p * N_TRIALS) if np.isfinite(p) else np.nan,
                        IS_diff=s["IS_diff"], OOS_diff=s["OOS_diff"],
                        OOS_lo=oos.get("lo", np.nan), OOS_hi=oos.get("hi", np.nan),
                        OOS_p=oos.get("p_boot", np.nan),
                        dR=rv["diff"], dR_lo=rv["lo"], dR_hi=rv["hi"], dR_p=rv["p_boot"],
                        feas_pp=detail[hid]["primary"].get("feas_pp", np.nan),
                        verdict="ALIVE" if not fails else "DEAD", why="; ".join(fails) or "-"))

S = pd.DataFrame(survive)
# Benjamini-Hochberg across the 7 declared trials
ok = S.p_boot.notna()
order = S.loc[ok, "p_boot"].sort_values().index
S["p_bh"] = np.nan
prev = 1.0
for rank, i in enumerate(reversed(list(order)), start=1):
    m = len(order); k_ = m - rank + 1
    prev = min(prev, S.at[i, "p_boot"] * m / k_)
    S.at[i, "p_bh"] = prev
S.to_csv(os.path.join(OUT, "ccs_phase1_survival_exp.csv"), index=False)

# H6 stratified, OOS-only (D5 control must hold out of sample too)
g6 = PRIMARY[PRIMARY.year > IS_END]
h6_oos = stratified_diff(g6, g6.sig_rank_tercile == "TOP", g6.sig_rank_tercile == "BOTTOM",
                         SEED + 11, 4000)
g6i = PRIMARY[PRIMARY.year <= IS_END]
h6_is = stratified_diff(g6i, g6i.sig_rank_tercile == "TOP", g6i.sig_rank_tercile == "BOTTOM",
                        SEED + 12, 4000)
report["h6_controlled"]["IS"] = h6_is
report["h6_controlled"]["OOS"] = h6_oos
report["survival"] = S.to_dict("records")
with open(os.path.join(OUT, "ccs_phase1_report_exp.json"), "w") as fh:
    json.dump(report, fh, indent=2, default=float)

print("\n" + "=" * 118)
print("SURVIVAL SCREEN — pre-registered pass criteria, N_trials = 7")
print("=" * 118)
print(S[["hypothesis", "book", "ep_t", "ep_c", "diff", "lo", "hi", "p_boot", "p_bonf", "p_bh",
         "IS_diff", "OOS_diff", "OOS_lo", "OOS_hi", "dR", "dR_p", "feas_pp",
         "verdict"]].round(4).to_string(index=False))
print()
for _, r_ in S.iterrows():
    print(f"  {r_.hypothesis:4s} {r_.verdict:5s}  {r_.why}")
print(f"\nH6 stratified on sig_n_cands (D5):  IS  {h6_is['diff']:+.4f} "
      f"[{h6_is['lo']:+.4f},{h6_is['hi']:+.4f}] p={h6_is['p_boot']:.3f}   |   "
      f"OOS {h6_oos['diff']:+.4f} [{h6_oos['lo']:+.4f},{h6_oos['hi']:+.4f}] "
      f"p={h6_oos['p_boot']:.3f}")
print(f"\nPractical floor: Phase 2 must clear {NOISE_FLOOR_PP}pp CAGR of harness noise. "
      f"feas_pp above = OPTIMISTIC first-order bound at k={K_UPSIZE}.")
