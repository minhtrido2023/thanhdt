"""Capacity-aware capit-sleeve NAV: OLD golden (deep pb_z<=-1 + strict, illiquid) vs NEW (custom30 + pb_z<0,
liquid). The KEY new value is DEPLOYABILITY — illiquid picks can't absorb capital (capit's capacity trap),
liquid custom30 names can. We model liquidity-capped fills (capit ramps ~3 sessions, ~15% ADV participation)
and realize each pick's true 60d return (profit_3M). Sleeve gets a target deploy per event; unfilled capital
stays in cash (0 return). Isolates the selection change; full BASE+CAPIT integration is pickle-blocked
(ba_v11_unified_12y_sig.pkl StringDtype). Compares deploy%, return-ON-WALLET, and cumulative contribution.
"""
import numpy as np, pandas as pd
WD = "/home/trido/thanhdt/WorkingClaude"
d = pd.read_csv(f"{WD}/data/golden_gate_test.csv", parse_dates=["time"])
d = d[d.liq >= 2e9].copy()
mem = pd.read_csv(f"{WD}/data/custom30_membership.csv", parse_dates=["effective_from", "effective_to"])
mem["effective_to"] = mem.effective_to.fillna(pd.Timestamp("2100-01-01"))
iv = {tk: list(zip(g.effective_from.values, g.effective_to.values)) for tk, g in mem.groupby("ticker")}
d["cust30"] = d.apply(lambda r: any(f <= np.datetime64(r.time) < t for f, t in iv.get(r.ticker, [])), axis=1)

strict = (d.ROE_Min5Y >= 0.12) & (d.ROIC5Y >= 0.10) & (d.FSCORE >= 6)
VARIANTS = {
 "OLD golden (pb_z<=-1 + strict)": strict & (d.pb_z <= -1),
 "NEW custom30 + pb_z<0":          d.cust30 & (d.pb_z < 0),
}
WALLET = 50e9             # capit sleeve wallet
TARGET = 0.50            # try to deploy 50% of wallet into the washout basket
RAMP_DAYS, PARTIC = 3, 0.15   # ramp over 3 sessions at 15% of ADV/day

def sleeve(mask, partic=PARTIC):
    """per-event: liquidity-capped equal-weight fills; realized return ON THE WALLET."""
    rows = []
    for ev, g in d[mask].groupby("time"):
        n = len(g)
        if n == 0: continue
        tgt_per = TARGET*WALLET/n
        cap = partic*g["liq"].values*RAMP_DAYS        # max VND fillable per name
        fill = np.minimum(tgt_per, cap)
        deployed = fill.sum()
        ret_on_wallet = float((fill*g["profit_3M"].values/100.0).sum()/WALLET)
        rows.append((ev, n, deployed/WALLET, ret_on_wallet))
    r = pd.DataFrame(rows, columns=["ev", "n", "deploy", "ret"])
    return r

print(f"wallet {WALLET/1e9:.0f}B, target deploy {TARGET:.0%}, ramp {RAMP_DAYS}d @ {PARTIC:.0%} ADV/day\n")
print(f"{'variant':32} {'avg n':>6} {'avg deploy%':>12} {'avg ret/ev':>11} {'cumul Σret':>11} {'win%':>6}")
print("-"*88)
res = {}
for lbl, m in VARIANTS.items():
    r = sleeve(m); res[lbl] = r
    print(f"{lbl:32} {r.n.mean():>6.1f} {r.deploy.mean()*100:>10.1f}% {r.ret.mean()*100:>+10.2f}% "
          f"{r.ret.sum()*100:>+10.2f}% {(r.ret>0).mean()*100:>5.0f}%")

old, new = res["OLD golden (pb_z<=-1 + strict)"], res["NEW custom30 + pb_z<0"]
print(f"\n  DEPLOY: old fills {old.deploy.mean()*100:.0f}% of target (capacity-choked) vs new {new.deploy.mean()*100:.0f}% "
      f"-> new puts {new.deploy.mean()/max(old.deploy.mean(),1e-9):.1f}x more capital to work")
print(f"  CONTRIBUTION: old cumulative {old.ret.sum()*100:+.1f}% vs new {new.ret.sum()*100:+.1f}% on wallet over events")
print(f"  (per-name return gap was +5.4% vs +10.5%; capacity AMPLIFIES it to the wallet-level gap above)")

print("\n  participation sensitivity (avg ret/ev on wallet):")
for p in (0.08, 0.15, 0.25):
    o, nw = sleeve(VARIANTS["OLD golden (pb_z<=-1 + strict)"], p), sleeve(d.cust30 & (d.pb_z < 0), p)
    print(f"    {p:.0%} ADV: OLD {o.ret.mean()*100:+.2f}% (deploy {o.deploy.mean()*100:.0f}%)  vs  "
          f"NEW {nw.ret.mean()*100:+.2f}% (deploy {nw.deploy.mean()*100:.0f}%)")
