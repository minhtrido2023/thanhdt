"""Principled leverage for the deep-cheap + capitulation deploy — Bayes-shrunk Kelly under a
margin-call ruin constraint. User: 'we borrow too little; size with Bayes + Kelly.'

The honest tension: the point-estimate edge looks huge (fwd6M ~19%, ~100% positive), but it rests on
only ~6 crisis EPISODES (the 190 G2 days are one-per-episode autocorrelated). Naive Kelly on 6 points
over-bets on noise. So: (1) measure the bet distribution at episode level, (2) Bayes-shrink the mean
toward a skeptical prior (n_eff = episodes, not days), (3) Kelly f*=(mu-borrow)/sigma^2, (4) cap by the
worst Max-Adverse-Excursion so a levered position survives the further fall to the true bottom without a
forced margin-call liquidation. Final lever = min(half-Kelly_shrunk, MAE-constrained). Cache threads=1."""
import os, sys
os.environ.setdefault("BQ_LOCAL_CACHE", "data/bq_cache")
os.chdir("/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd
from bq_local_cache import get_cache
lc = get_cache()

# --- VNINDEX path + market PE + liquid pbz_med (the deploy vehicle proxy = index; custom30V does BETTER
#     per the 2012 stock-pick finding, so index = a CONSERVATIVE bet estimate) ---
v = lc.query("""SELECT t.time, MAX(t.VNINDEX) vni, MAX(t.VNINDEX_PE) pe
FROM tav2_bq.ticker t WHERE t.time>=DATE '2013-01-01' AND t.VNINDEX IS NOT NULL GROUP BY t.time ORDER BY t.time""")
v["time"] = pd.to_datetime(v["time"]); v = v.sort_values("time").reset_index(drop=True)
v["pe_pct5y"] = v["pe"].rolling(1250, min_periods=250).apply(lambda s: (s.iloc[-1] >= s).mean())
pb = lc.query("""SELECT t.time, APPROX_QUANTILES((t.PB-t.PB_MA5Y)/NULLIF(t.PB_SD5Y,0),2)[OFFSET(1)] pbz_med
FROM tav2_bq.ticker_prune t WHERE t.time>=DATE '2013-01-01' AND t.PB_SD5Y>0 GROUP BY t.time""")
pb["time"] = pd.to_datetime(pb["time"]); v = v.merge(pb, on="time", how="left")

H = 126                                                  # 6M holding horizon
v["fwd6M"]  = v["vni"].shift(-H)/v["vni"] - 1
v["fwd12M"] = v["vni"].shift(-2*H)/v["vni"] - 1
# Max Adverse Excursion over the next 63d (the drawdown a levered entry must survive before recovery)
mae = []
for i in range(len(v)):
    j = min(i+63, len(v)); seg = v["vni"].iloc[i:j]
    mae.append(seg.min()/v["vni"].iloc[i]-1 if len(seg) else np.nan)
v["mae63"] = mae

# --- deploy signal G2 = deep-cheap (pbz<=-0.5) AND absolute-cheap (PE_pctile<=0.20) ---
fire = v[(v["pbz_med"]<=-0.5) & (v["pe_pct5y"]<=0.20) & v["fwd6M"].notna()].copy()
# collapse autocorrelated fire-days into EPISODES (gap > 63 trading days = new episode)
fire = fire.sort_values("time"); gaps = fire.index.to_series().diff().fillna(999) > 63
fire["ep"] = gaps.cumsum()
ep = fire.groupby("ep").agg(start=("time","first"), n_days=("vni","size"),
        fwd6M=("fwd6M","mean"), fwd12M=("fwd12M","mean"), mae63=("mae63","min")).reset_index(drop=True)
print(f"=== deploy-signal episodes (G2: pbz<=-0.5 & PE_pct<=0.20), {len(ep)} episodes / {len(fire)} days ===")
print(ep.assign(fwd6M=(ep.fwd6M*100).round(1), fwd12M=(ep.fwd12M*100).round(1),
                mae63=(ep.mae63*100).round(1)).to_string(index=False))

r6 = ep["fwd6M"].values                                  # episode-level 6M returns (the bet outcomes)
n = len(r6); mu_hat = r6.mean(); sig = r6.std(ddof=1)
BORROW_6M = 0.10/2                                        # 10%/yr borrow over a 6M hold
print(f"\n--- bet distribution (episode-level, n_eff={n}) ---")
print(f"  mean fwd6M = {mu_hat*100:.1f}%   std = {sig*100:.1f}%   Sharpe(6M) = {mu_hat/sig:.2f}   "
      f"win-rate = {(r6>0).mean()*100:.0f}%   worst fwd6M = {r6.min()*100:.1f}%")
print(f"  worst MAE63 (further fall after signal) = {ep['mae63'].min()*100:.1f}%   "
      f"median MAE63 = {ep['mae63'].median()*100:.1f}%")

# --- Kelly (continuous, financed at borrow): f* = (mu - borrow)/sigma^2 ---
def kelly(mu): return (mu - BORROW_6M)/sig**2
f_naive = kelly(mu_hat)
print(f"\n--- KELLY (f* = (mu-borrow_6M)/sigma^2), borrow_6M={BORROW_6M*100:.0f}% ---")
print(f"  naive full-Kelly  = {f_naive:.2f}x   (half = {f_naive/2:.2f}x)  <- over-bets on n={n} noise")

# --- Bayesian shrinkage of mu (n_eff = episodes, skeptical-but-not-nihilist prior) ---
print(f"\n--- BAYES-shrunk Kelly (posterior mean of mu; se = sigma/sqrt(n_eff)) ---")
se = sig/np.sqrt(n)
for m0, s0, lbl in [(0.05,0.05,"skeptical (edge=just borrow)"),
                    (0.10,0.06,"moderate (real but modest edge)"),
                    (0.15,0.08,"believer (event-study magnitude)")]:
    prec = 1/se**2 + 1/s0**2
    mu_post = (mu_hat/se**2 + m0/s0**2)/prec
    fk = kelly(mu_post)
    print(f"  prior~N({m0*100:.0f}%,{s0*100:.0f}%) [{lbl:32s}] -> mu_post={mu_post*100:4.1f}%  "
          f"full-Kelly={fk:.2f}x  HALF-Kelly={fk/2:.2f}x")

# --- margin-call ruin constraint: a 1+L levered position must survive the worst MAE without breaching
#     maintenance margin. VN retail: initial margin 50% (max 2x), maintenance ~ m_maint. Gross G=1+L_borrow.
#     Equity after MAE drop d (d<0): E' = 1 + G*d ; call when E'/(G*(1+d)) < m_maint. Solve max G. ---
print(f"\n--- MARGIN-CALL ruin cap (survive worst MAE without forced liquidation at the bottom) ---")
for d, dl in [(ep['mae63'].min(),"worst MAE63"), (ep['mae63'].median(),"median MAE63")]:
    for m_maint in (0.30, 0.40):
        # E'/(pos value) >= m_maint  with pos=G*(1+d), E'=1+G*d  ->  (1+G*d)/(G*(1+d)) >= m_maint
        # solve for max G:  1+G*d >= m_maint*G*(1+d)  -> 1 >= G*(m_maint*(1+d) - d) -> G <= 1/(m_maint*(1+d)-d)
        denom = m_maint*(1+d) - d
        Gmax = (1/denom) if denom>0 else float('inf')
        print(f"  {dl}={d*100:5.1f}%, maint={m_maint*100:.0f}%  -> max gross G <= {Gmax:.2f}x  (lever L<= {Gmax-1:.2f})")

print("\nREAD: final lever = min( HALF-Kelly under the chosen prior , MARGIN-CALL cap at worst-MAE ).")
print("Fractional (half) Kelly + Bayes shrink + MAE cap is the disciplined size; full-Kelly on n~6 = ruin-prone.")
print("Hold-as-neutral (user req 2) cuts FORCED selling -> lets us sit closer to the MAE cap safely.")
