# -*- coding: utf-8 -*-
"""Mechanism diagnostic for the exit NO-GO + axis 2 (sizing/weighting) + axis 3 (liquidity).
Job Taylor_20260720_164006.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

OUT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_capitexit"
pan = pd.read_csv(f"{OUT}/panel.csv", parse_dates=["time"])
pos = pd.read_csv(f"{OUT}/positions.csv")
HOLD = 60

def op(g, k):
    s = g[(g["k"] <= k) & g["open"].notna() & (g["open"] > 0)]
    return float(s.iloc[-1]["open"]) if len(s) else np.nan

# ---- DIAGNOSTIC: what happens AFTER an exit fires? -----------------------------------
print("="*78); print("DIAGNOSTIC — return foregone between exit day and session 60"); print("="*78)
print(f"{'variant':8s} {'n_fire':>7s} {'med_exit_k':>11s} {'ret@exit':>9s} {'ret@60':>9s} {'foregone':>9s}")
for vid in ["E1", "E2", "E3", "E4", "E6"]:
    rows = []
    for _, r in pos[pos[f"{vid}_xk"].notna()].iterrows():
        g = pan[(pan["event"] == r["event"]) & (pan["ticker"] == r["ticker"])].sort_values("k")
        k = int(r[f"{vid}_xk"]); kend = min(HOLD, int(g["k"].max()))
        if k >= kend: continue
        pin = float(g.iloc[0]["px_in"])
        rows.append((k, op(g, k)/pin - 1, op(g, kend)/pin - 1))
    if not rows: continue
    a = pd.DataFrame(rows, columns=["k", "r_exit", "r60"])
    print(f"{vid:8s} {len(a):7d} {a['k'].median():11.0f} {a['r_exit'].mean():+9.2%} "
          f"{a['r60'].mean():+9.2%} {(a['r_exit']-a['r60']).mean():+9.2%}")
print("\nNegative 'foregone' = the exit sold BEFORE the recovery it was waiting for.")

# ---- AXIS 2a: is the 15-name cap ever binding? --------------------------------------
print("\n" + "="*78); print("AXIS 2a — basket size vs the production cap of 15"); print("="*78)
bs = pos.groupby("event").size()
print(f"basket sizes: min={bs.min()} median={bs.median():.0f} max={bs.max()} "
      f"| events where cap15 binds: {(bs >= 15).sum()}/14")
print(f"events where basket < 5: {(bs < 5).sum()}/14  -> a 'K=5 slot' would be non-binding too")

# ---- AXIS 2b: depth-weight vs equal-weight ------------------------------------------
print("\n" + "="*78); print("AXIS 2b — pb_z depth-weight vs equal-weight (h=60)"); print("="*78)
ent = pan[pan["k"] == 0][["event", "ticker", "pbz_entry"]].drop_duplicates()
m = pos[["event", "ticker", "E0"]].merge(ent, on=["event", "ticker"])
rows = []
for ev, g in m.groupby("event"):
    eq = g["E0"].mean()
    d = (-g["pbz_entry"]).clip(lower=0.01)                 # deeper (more negative pbz) -> heavier
    dw = float((g["E0"] * d / d.sum()).sum())
    r = g["pbz_entry"].rank(ascending=True)                # rank-based (bounded) alternative
    rw = float((g["E0"] * (len(g) - r + 1) / (len(g) - r + 1).sum()).sum())
    rows.append(dict(event=ev, equal=eq, depth=dw, rank=rw))
w = pd.DataFrame(rows)
for c in ["equal", "depth", "rank"]:
    print(f"  {c:6s} mean={w[c].mean():+7.2%} median={w[c].median():+7.2%} worst={w[c].min():+7.2%}")
for c in ["depth", "rank"]:
    d = w[c] - w["equal"]
    t = d.mean()/(d.std(ddof=1)/np.sqrt(len(d)))
    signs = {np.sign(d.drop(i).mean()) for i in d.index}
    print(f"  {c} vs equal: diff={d.mean():+.2%} t={t:.2f} LOO={'STABLE' if len(signs)==1 else 'FLIP'}")

# ---- AXIS 2c: does entry-day pb_z depth predict the 60d return at all? --------------
ic = m.groupby("event").apply(lambda g: g["pbz_entry"].corr(g["E0"], method="spearman")
                              if g["ticker"].nunique() >= 3 else np.nan, include_groups=False).dropna()
print(f"\n  Spearman IC(pb_z_entry, ret60) per event: mean={ic.mean():+.3f} "
      f"median={ic.median():+.3f} n={len(ic)} (negative = deeper pb_z -> better)")

# ---- AXIS 3: liquidity / %ADV capacity ----------------------------------------------
print("\n" + "="*78); print("AXIS 3 — liquidity capacity of the CAPIT basket"); print("="*78)
adv = pan[pan["k"] <= 0].groupby(["event", "ticker"])["adv_b"].first()
adv20 = (pan[pan["k"] <= 20].groupby(["event", "ticker"])["adv_b"].median()
         .rename("adv20_b"))
a = adv20.reset_index()
print(f"per-position ADV(20d, tỷ VND): p10={a['adv20_b'].quantile(.1):.2f} "
      f"p50={a['adv20_b'].median():.2f} p90={a['adv20_b'].quantile(.9):.2f} min={a['adv20_b'].min():.2f}")
worst = a.groupby("event")["adv20_b"].min()
print(f"thinnest name per event: median={worst.median():.2f} tỷ, min={worst.min():.2f} tỷ")

print("\n  Sleeve capacity at X% ADV/day, 2-session exit, equal-weight over the basket:")
print(f"  {'event':12s} {'n':>3s} {'thinnest':>9s} {'cap@10%':>10s} {'cap@15%':>10s}")
caps = []
for ev, g in a.groupby("event"):
    n = len(g); thin = g["adv20_b"].min()
    # binding constraint = thinnest name; each name gets sleeve/n, exit over 2 sessions
    c10 = thin * 0.10 * 2 * n
    c15 = thin * 0.15 * 2 * n
    caps.append(dict(event=ev, n=n, thin=thin, c10=c10, c15=c15))
    print(f"  {ev:12s} {n:3d} {thin:9.2f} {c10:10.1f} {c15:10.1f}")
c = pd.DataFrame(caps)
print(f"\n  median sleeve capacity: {c['c10'].median():.1f} tỷ @10%ADV | "
      f"{c['c15'].median():.1f} tỷ @15%ADV")
print(f"  tightest event:         {c['c10'].min():.1f} tỷ @10%ADV ({c.loc[c['c10'].idxmin(),'event']})")
