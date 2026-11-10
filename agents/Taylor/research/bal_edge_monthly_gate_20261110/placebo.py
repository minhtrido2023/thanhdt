"""Placebo + signal diagnostics on the trade-subtraction approximator (pin0% blind) — job Taylor_20261110_053025.
Placebo: random lock schedules with the SAME number of locked months and SAME number of lock episodes as the
real variant (random composition of locked/unlocked run lengths), N_PLAC draws. Same approximator for real
and placebo => apples to apples. Writes placebo.json."""
import os, json, sys
import numpy as np, pandas as pd
import approx

HERE = os.path.dirname(os.path.abspath(__file__))
N_PLAC = 2000
rng = np.random.default_rng(20261110)

daily, M, first, ptype = approx.get()
dates = daily.index
st = pd.read_csv(f"{HERE}/blocks/states.csv")
st["ym"] = pd.PeriodIndex(st["ym"], freq="M")
yms = list(st["ym"])
ym_of_day = dates.to_period("M")
blind_c = approx.combine(daily, daily["nav_bal_ref"].values)
mb = approx.metrics(blind_c, dates); mbb = approx.metrics(daily["nav_bal_ref"].values, dates)


def eval_months(locked_months, exempt=False):
    lm = set(locked_months)
    blk = dates[np.array([m in lm for m in ym_of_day])]
    bal, nrm = approx.gated(daily, M, first, ptype, blk, exempt)
    c = approx.combine(daily, bal)
    mc = approx.metrics(c, dates); mbal = approx.metrics(bal, dates)
    return {k: mc[k] - mb[k] for k in mc}, {k: mbal[k] - mbb[k] for k in mbal}, nrm


def random_schedule(n_lock, n_ep, n=len(yms)):
    """random binary sequence of length n with n_lock ones in exactly n_ep runs (start state random-free: begins unlocked)"""
    n_un = n - n_lock
    # lock runs: composition of n_lock into n_ep positive parts; unlocked runs: n_ep or n_ep+1 parts (first part >=1 since start unlocked)
    def comp(total, k):
        cuts = np.sort(rng.choice(np.arange(1, total), k - 1, replace=False)) if k > 1 else np.array([], int)
        return np.diff(np.r_[0, cuts, total])
    lk = comp(n_lock, n_ep)
    tail = rng.random() < 0.5
    k_un = n_ep + (1 if tail else 0)
    un = comp(n_un, k_un)
    seq = []
    for i in range(n_ep):
        seq += [0] * un[i] + [1] * lk[i]
    if tail:
        seq += [0] * un[-1]
    return [yms[i] for i, v in enumerate(seq) if v]


out = {"approx_blind_combined": mb, "approx_blind_bal": mbb, "variants": {}}
summ = pd.read_csv(f"{HERE}/blocks/summary.csv").set_index("variant")
for v in ["G1_L0", "G1_L1", "G1_L2", "G2_3m_L0", "G3_x2_L0", "G4_hu2_L0", "G5_hl2_L0", "G6_n3_L0"]:
    lm = list(st.loc[st[f"lk_{v}"].astype(bool), "ym"])
    dc, dbal, nrm = eval_months(lm)
    n_ep = int(summ.loc[v, "lock_episodes"])
    pl = []
    for _ in range(N_PLAC):
        pc, pb, _n = eval_months(random_schedule(len(lm), n_ep))
        pl.append([pc["cagr"], pc["sharpe"], pc["calmar"], pc["maxdd"], pb["cagr"], pb["sharpe"]])
    pl = np.array(pl)
    real = [dc["cagr"], dc["sharpe"], dc["calmar"], dc["maxdd"], dbal["cagr"], dbal["sharpe"]]
    keys = ["comb_dcagr", "comb_dsharpe", "comb_dcalmar", "comb_dmaxdd", "bal_dcagr", "bal_dsharpe"]
    out["variants"][v] = dict(removed_holdings=nrm, months_locked=len(lm), episodes=n_ep,
                              real={k: float(x) for k, x in zip(keys, real)},
                              placebo_pctile={k: float((pl[:, i] < real[i]).mean()) for i, k in enumerate(keys)},
                              placebo_median={k: float(np.median(pl[:, i])) for i, k in enumerate(keys)},
                              placebo_p5_p95={k: [float(np.percentile(pl[:, i], 5)), float(np.percentile(pl[:, i], 95))] for i, k in enumerate(keys)})
    print(v, {k: round(x, 4) for k, x in zip(keys, real)}, "pctile", {k: round(out['variants'][v]['placebo_pctile'][k], 3) for k in keys[:3]})
    sys.stdout.flush()

# --- signal diagnostics for G1_L0: precision / recall of 'locked month is negative' ---
v = "G1_L0"
s = st[st["sample_ok"]]
lk = s[f"lk_{v}"].astype(bool)
neg = s["ret"] < 0
out["signal_G1_L0"] = dict(
    sample_months=int(len(s)), base_rate_neg=float(neg.mean()),
    precision=float(neg[lk].mean()), recall=float(lk[neg].mean()),
    mean_ret_locked=float(s.loc[lk, "ret"].mean()), mean_ret_unlocked=float(s.loc[~lk, "ret"].mean()),
    n_locked_sample=int(lk.sum()))
# --- decomposition: P&L (blind, VND, final) of holdings removed by G1_L0 ---
lm = set(st.loc[st[f"lk_{v}"].astype(bool), "ym"])
blk = set(dates[np.array([m in lm for m in ym_of_day])])
rm = first.isin(blk).values
fin = M[-1, :]
out["decomp_G1_L0"] = dict(removed=int(rm.sum()), kept=int((~rm).sum()),
                           avoided_losses_B=float(-fin[rm & (fin < 0)].sum() / 1e9),
                           missed_gains_B=float(fin[rm & (fin > 0)].sum() / 1e9),
                           net_removed_pnl_B=float(fin[rm].sum() / 1e9),
                           removed_winrate=float((fin[rm] > 0).mean()), kept_winrate=float((fin[~rm] > 0).mean()),
                           removed_mean_pnl_M=float(fin[rm].mean() / 1e6), kept_mean_pnl_M=float(fin[~rm].mean() / 1e6))
print(json.dumps({k: out[k] for k in ["signal_G1_L0", "decomp_G1_L0"]}, indent=1))
json.dump(out, open(f"{HERE}/placebo.json", "w"), indent=1)
