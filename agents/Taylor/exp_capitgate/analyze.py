# -*- coding: utf-8 -*-
"""CAPIT gate-relaxation study — Panels A/B/C per PREREG.md (job Taylor_20260720_160852)."""
import sys, io, itertools
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
OUT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_capitgate"
X = pd.read_csv(f"{OUT}/panel.csv", parse_dates=["obs"])
EVENTS = pd.to_datetime(["2014-05-08","2015-08-24","2016-01-18","2018-05-28","2020-03-12",
  "2022-04-20","2022-06-20","2022-09-29","2023-10-31","2024-04-19","2024-08-05","2025-04-03",
  "2025-10-20","2026-03-09"])
rng = np.random.default_rng(12345)

GATES = {  # id -> (roe, roic, fscore, adv)
 "G0": (0.12, 0.10, 6, 2.0), "G1": (0.09, 0.10, 6, 2.0), "G2": (0.12, 0.08, 6, 2.0),
 "G3": (0.12, 0.10, 5, 2.0), "G4": (0.12, 0.10, 6, 1.0), "G5": (0.09, 0.08, 5, 2.0),
 "G6": (0.055, 0.073, 5, 2.0)}

def mask(df, g):
    roe, roic, fs, adv = GATES[g]
    return (df.roe >= roe) & (df.roic >= roic) & (df.fs >= fs) & (df.adv >= adv)

def tstat(v):
    v = np.asarray([x for x in v if np.isfinite(x)])
    return (v.mean(), v.mean()/(v.std(ddof=1)/np.sqrt(len(v))) if len(v) > 1 and v.std(ddof=1) > 0 else np.nan, len(v))

# ---------- non-overlapping quarterly obs dates (>=60 sessions apart ~ 1 per quarter) ----------
alld = sorted(X.obs.unique())
q_dates, last = [], None
for d in alld:
    if last is None or (pd.Timestamp(d) - pd.Timestamp(last)).days >= 92:
        q_dates.append(d); last = d
q_dates = pd.to_datetime(q_dates)
print(f"quarterly non-overlapping obs dates: {len(q_dates)}")

# ============ PANEL A — MARGINAL vs CORE ============
def panelA(g, dates, cheap_only=True, h=60):
    """per-date: mean demeaned fwd-return of MARGINAL(Gk\\G0) minus CORE(G0), + tail stats pooled."""
    rows, marg_r, core_r = [], [], []
    for d in dates:
        s = X[X.obs == d].copy()
        if cheap_only: s = s[s.pbz < 0]
        s = s.dropna(subset=[f"r{h}"])
        core = s[mask(s, "G0")]; new = s[mask(s, g) & ~mask(s, "G0")]
        if len(core) < 2 or len(new) < 1: continue
        pool = pd.concat([core, new])
        mu = pool[f"r{h}"].mean()                        # demean within date+pool
        rows.append({"obs": d, "diff": (new[f"r{h}"] - mu).mean() - (core[f"r{h}"] - mu).mean(),
                     "n_new": len(new), "n_core": len(core)})
        marg_r += list(new[f"r{h}"] - mu); core_r += list(core[f"r{h}"] - mu)
    R = pd.DataFrame(rows)
    m, t, n = tstat(R["diff"]) if len(R) else (np.nan, np.nan, 0)
    mr, cr = np.array(marg_r), np.array(core_r)
    return {"g": g, "n_dates": n, "diff": m, "t": t,
            "n_marg": len(mr), "n_core": len(cr),
            "p20_marg": (mr <= -0.20).mean() if len(mr) else np.nan,
            "p20_core": (cr <= -0.20).mean() if len(cr) else np.nan,
            "p5_marg": np.percentile(mr, 5) if len(mr) else np.nan,
            "p5_core": np.percentile(cr, 5) if len(cr) else np.nan,
            "wd_marg": mr[mr <= np.percentile(mr, 10)].mean() if len(mr) else np.nan,
            "wd_core": cr[cr <= np.percentile(cr, 10)].mean() if len(cr) else np.nan,
            "_R": R}

print("\n=== PANEL A (primary: quarterly non-overlap, pb_z<0, h=60) ===")
print(f"{'g':4} {'#dt':>4} {'#marg':>6} {'#core':>6} {'diff':>8} {'t':>6} "
      f"{'P<=-20% M/C':>14} {'p5 M/C':>16} {'worst-dec M/C':>16}")
A = {}
for g in ["G1","G2","G3","G4","G5","G6"]:
    a = panelA(g, q_dates); A[g] = a
    print(f"{g:4} {a['n_dates']:>4} {a['n_marg']:>6} {a['n_core']:>6} {a['diff']*100:>+7.2f}pp {a['t']:>+6.2f} "
          f"{a['p20_marg']*100:>6.1f}/{a['p20_core']*100:<6.1f} "
          f"{a['p5_marg']*100:>+7.1f}/{a['p5_core']*100:<+7.1f} "
          f"{a['wd_marg']*100:>+7.1f}/{a['wd_core']*100:<+7.1f}")

# ---- LOO by year + IS/OOS on the paired diff series ----
print("\n=== PANEL A — LOO by year / IS-OOS (diff, pp) ===")
for g in ["G1","G2","G3","G4","G5","G6"]:
    R = A[g]["_R"]
    if not len(R): continue
    R["yr"] = R.obs.dt.year
    loo = {y: R[R.yr != y]["diff"].mean()*100 for y in sorted(R.yr.unique())}
    worst_y, worst_v = min(loo.items(), key=lambda kv: kv[1])
    best_y, best_v = max(loo.items(), key=lambda kv: kv[1])
    IS = R[R.yr <= 2019]["diff"].mean()*100; OOS = R[R.yr >= 2020]["diff"].mean()*100
    signflip = "SIGN-FLIP" if (worst_v < 0) != (R["diff"].mean()*100 < 0) else "stable"
    print(f"{g}: full {R['diff'].mean()*100:+.2f} | LOO range [{worst_v:+.2f} (drop {worst_y}) .. "
          f"{best_v:+.2f} (drop {best_y})] {signflip} | IS {IS:+.2f} / OOS {OOS:+.2f} "
          f"{'SAME-sign' if IS*OOS>0 else 'OPPOSITE-sign'}")

# ---- year-block cluster bootstrap ----
print("\n=== PANEL A — year-block cluster bootstrap (2000 draws) ===")
for g in ["G1","G2","G3","G4","G5","G6"]:
    R = A[g]["_R"]
    if not len(R): continue
    blocks = [grp["diff"].values for _, grp in R.groupby(R.obs.dt.year)]
    bs = [np.concatenate([blocks[i] for i in rng.integers(0, len(blocks), len(blocks))]).mean()
          for _ in range(2000)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f"{g}: mean {np.mean(bs)*100:+.2f}pp CI95 [{lo*100:+.2f}, {hi*100:+.2f}] P(>0)={np.mean(np.array(bs)>0):.2f}")

# ---- robustness: no pb_z filter; h=250 ----
print("\n=== PANEL A robustness ===")
for lab, kw in [("no pbz filter, h=60", dict(cheap_only=False, h=60)),
                ("pbz<0, h=250", dict(cheap_only=True, h=250))]:
    out = []
    for g in ["G1","G2","G3","G4","G5","G6"]:
        a = panelA(g, q_dates, **kw)
        out.append(f"{g} {a['diff']*100:+.2f}pp(t={a['t']:+.2f}, P<=-20% {a['p20_marg']*100:.0f}/{a['p20_core']*100:.0f})")
    print(f"  {lab}: " + " | ".join(out))

# ============ PANEL B — pool structure at the 14 washout events ============
def cascade(s):
    """production pb_z cascade: prefer pbz<-1 (>=3), else pbz<0 (>=3), else all; cap 15."""
    g_ = s[s.pbz < -1]; c_ = s[s.pbz < 0]
    pick = g_ if len(g_) >= 3 else (c_ if len(c_) >= 3 else s)
    return pick.nsmallest(15, "pbz") if len(pick) > 15 else pick

print("\n=== PANEL B — pool size at 14 washout events (K=5) ===")
K = 5
tab = {}
for g in GATES:
    sizes = []
    for d in EVENTS:
        s = X[(X.obs == d) & mask(X[X.obs == d], g)]
        sizes.append(len(cascade(s)) if len(s) else 0)
    tab[g] = sizes
    print(f"{g}: sizes {sizes} | median {int(np.median(sizes))} | pool>K: {sum(1 for x in sizes if x>K)}/14")

# ============ PANEL C — portfolio-level 14 events (K=5, rank pb_z, equal-weight) ============
print("\n=== PANEL C — 14-event basket return (K=5, pb_z rank) — N=14, NOT powered ===")
def basket_ret(g, h):
    rs = []
    for d in EVENTS:
        s = X[(X.obs == d)]; s = s[mask(s, g)]
        if s.empty: continue
        p = cascade(s).sort_values(["pbz", "ticker"]).head(K)       # stable tie-break
        r = p[f"r{h}"].dropna()
        if len(r): rs.append(r.mean())
    return np.array(rs)
for h in (60, 250):
    base = basket_ret("G0", h)
    line = []
    for g in ["G1","G2","G3","G4","G5","G6"]:
        v = basket_ret(g, h); d = v - base[:len(v)]
        m, t, n = tstat(d)
        line.append(f"{g} {m*100:+.2f}pp(t={t:+.2f})")
    print(f"  h={h}: base mean {base.mean()*100:+.2f}pp | " + " | ".join(line))
