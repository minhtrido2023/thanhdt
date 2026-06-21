#!/usr/bin/env python3
"""
fa_ic_audit.py
==============
Diagnostic for the 7-axis FA layer (fundamental_rating.py output).
Answers, before we build new factors:
  1. Per-axis IC (Spearman of axis score vs forward profit_3M) — which axes earn their weight?
  2. Regime-conditional IC (IC within each 5-state market regime) — does FA edge live in
     specific regimes (e.g. NEUTRAL/BEAR) and vanish in BULL (FOMO)?
  3. Tier monotonicity (median profit_3M A>B>C>D>E) overall AND by regime.
  4. Axis redundancy — correlation matrix between the 7 axis scores (are Stability & Cash
     measuring the same thing?).
  5. total_score IC vs equal-weight IC — is the hand-set 18/18/18/15/13/8/10 better than naive?

No look-ahead: profit_3M is the forward outcome already stored; state is the MARKET state on
the FA report date (forward-filled from vnindex_5state, on-or-before the row's time).

Output: console tables + data/fa_ic_audit.md
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"

AXES = ["quality", "stability", "cash", "shareholder", "growth", "health", "valuation"]
WEIGHTS = {"quality":0.18,"stability":0.18,"cash":0.18,"shareholder":0.15,
           "growth":0.13,"health":0.08,"valuation":0.10}
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}


def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = (f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
               f'--project_id={PROJECT} --format=csv --max_rows=10000000')
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0:
        raise RuntimeError(f"[BQ ERROR] {(r.stdout or r.stderr)[:600]}")
    return pd.read_csv(StringIO(r.stdout.strip()))


def ic(x, y):
    """Spearman rank IC, NaN-tolerant; returns (rho, n)."""
    x = pd.Series(np.asarray(x, dtype=float)); y = pd.Series(np.asarray(y, dtype=float))
    m = (~x.isna()) & (~y.isna())
    if m.sum() < 30:
        return (np.nan, int(m.sum()))
    rx = x[m].rank(); ry = y[m].rank()
    rho = np.corrcoef(rx, ry)[0, 1]
    return (rho, int(m.sum()))


def main():
    lines = []
    def P(s=""):
        print(s); lines.append(s)

    # ── Load FA scores ────────────────────────────────────────────────────
    df = pd.read_csv(os.path.join(WORKDIR, "fundamental_rating_all.csv"))
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    # ── Load 5-state, forward-fill to FA report date ──────────────────────
    st = bq_query("SELECT time, state FROM tav2_bq.vnindex_5state ORDER BY time")
    st["time"] = pd.to_datetime(st["time"])
    st = st.sort_values("time")
    df = pd.merge_asof(df, st, on="time", direction="backward")
    df["state"] = df["state"].astype("Int64")

    have = df.dropna(subset=["profit_3M"]).copy()
    P(f"# FA 7-axis IC Audit")
    P(f"")
    P(f"Rows total {len(df):,} | with forward profit_3M {len(have):,} "
      f"| date {have['time'].min().date()}→{have['time'].max().date()}")
    P(f"State coverage: " + ", ".join(
        f"{STATE_NAMES[s]}={int((have['state']==s).sum())}" for s in [1,2,3,4,5]
        if (have['state']==s).any()))
    P("")

    # ── 1. Per-axis IC overall ────────────────────────────────────────────
    P("## 1. Per-axis IC vs forward profit_3M (overall)")
    P("")
    P(f"{'axis':<13}{'weight':>8}{'IC':>9}{'N':>8}")
    P("-"*38)
    axis_ic = {}
    for a in AXES:
        rho, n = ic(have[f"score_{a}"], have["profit_3M"])
        axis_ic[a] = rho
        P(f"{a:<13}{WEIGHTS[a]*100:>6.0f}% {rho:>+8.4f}{n:>8,}")
    rho_tot, n_tot = ic(have["total_score"], have["profit_3M"])
    P("-"*38)
    P(f"{'total_score':<13}{'100%':>8}{rho_tot:>+8.4f}{n_tot:>8,}")
    # equal-weight composite
    have["ew_score"] = have[[f"score_{a}" for a in AXES]].mean(axis=1)
    rho_ew, _ = ic(have["ew_score"], have["profit_3M"])
    P(f"{'equal-weight':<13}{'(1/7)':>8}{rho_ew:>+8.4f}")
    P("")
    P("Interpretation: axes with IC near 0 or negative are not earning their weight;")
    P("if equal-weight ≈ total_score, the hand-set weights add little.")
    P("")

    # ── 2. Regime-conditional IC ──────────────────────────────────────────
    P("## 2. Regime-conditional IC (total_score vs profit_3M, per 5-state)")
    P("")
    P(f"{'state':<10}{'IC':>9}{'N':>8}{'med_p3M':>10}")
    P("-"*37)
    for s in [1,2,3,4,5]:
        g = have[have["state"]==s]
        if len(g) < 30: continue
        rho, n = ic(g["total_score"], g["profit_3M"])
        P(f"{STATE_NAMES[s]:<10}{rho:>+8.4f}{n:>8,}{g['profit_3M'].median():>9.2f}%")
    P("")

    # per-axis IC by state (compact matrix)
    P("### Per-axis IC by state")
    P("")
    hdr = f"{'axis':<13}" + "".join(f"{STATE_NAMES[s][:4]:>9}" for s in [1,2,3,4,5])
    P(hdr); P("-"*len(hdr))
    for a in AXES:
        row = f"{a:<13}"
        for s in [1,2,3,4,5]:
            g = have[have["state"]==s]
            rho, n = ic(g[f"score_{a}"], g["profit_3M"]) if len(g)>=30 else (np.nan,0)
            row += f"{rho:>+9.3f}" if not np.isnan(rho) else f"{'·':>9}"
        P(row)
    P("")

    # ── 3. Tier monotonicity overall + by state ───────────────────────────
    P("## 3. Tier monotonicity (median profit_3M, want A>B>C>D>E)")
    P("")
    def tier_row(g, label):
        meds = []
        for t in ["A","B","C","D","E"]:
            v = g[g["tier"]==t]["profit_3M"]
            meds.append(v.median() if len(v) else np.nan)
        mono = "✓" if all(meds[i]>=meds[i+1] for i in range(4)
                           if not (np.isnan(meds[i]) or np.isnan(meds[i+1]))) else "✗"
        return f"{label:<10}" + "".join(f"{m:>8.2f}" if not np.isnan(m) else f"{'·':>8}" for m in meds) + f"   {mono}"
    P(f"{'cohort':<10}{'A':>8}{'B':>8}{'C':>8}{'D':>8}{'E':>8}   mono")
    P("-"*58)
    P(tier_row(have, "ALL"))
    for s in [1,2,3,4,5]:
        g = have[have["state"]==s]
        if len(g) >= 50:
            P(tier_row(g, STATE_NAMES[s]))
    P("")

    # ── 4. Axis redundancy ────────────────────────────────────────────────
    P("## 4. Axis score correlation (redundancy check)")
    P("")
    corr = have[[f"score_{a}" for a in AXES]].corr(method="spearman")
    short = [a[:4] for a in AXES]
    P(f"{'':<6}" + "".join(f"{s:>7}" for s in short))
    for i,a in enumerate(AXES):
        row = f"{a[:5]:<6}"
        for j,b in enumerate(AXES):
            row += f"{corr.iloc[i,j]:>7.2f}"
        P(row)
    P("")
    # flag high pairs
    pairs = []
    for i in range(len(AXES)):
        for j in range(i+1,len(AXES)):
            c = corr.iloc[i,j]
            if abs(c) >= 0.45:
                pairs.append((AXES[i],AXES[j],c))
    if pairs:
        P("High-correlation pairs (|ρ|≥0.45 → candidate redundancy):")
        for a,b,c in sorted(pairs,key=lambda x:-abs(x[2])):
            P(f"  {a} ↔ {b}: {c:+.2f}")
    else:
        P("No axis pair with |ρ|≥0.45 — axes are reasonably orthogonal.")
    P("")

    with open(os.path.join(WORKDIR,"data","fa_ic_audit.md"),"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    P("Saved data/fa_ic_audit.md")


if __name__ == "__main__":
    main()
