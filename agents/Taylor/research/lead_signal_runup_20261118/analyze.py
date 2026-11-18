"""Phân tích theo PREREG md5 ef70c866. Đọc panel.parquet → results.csv, event_view.csv, climax.csv, strata.csv,
base_rates.csv, heatmap.png, summary.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from scipy.stats import norm, skew, kurtosis

OUT = os.path.dirname(os.path.abspath(__file__))
B, SEED = 2000, 20261118
P = pd.read_parquet(f"{OUT}/panel.parquet")
P = P[P.E].reset_index(drop=True)
P["month"] = P.time.dt.to_period("M").astype(str)
# tercile ADV thực, mốc từ IS
q = P.loc[~P.OOS, "ADV20_real"].quantile([1 / 3, 2 / 3]).to_numpy()
P["terc"] = np.digitize(P.ADV20_real, q)
S = P[~P.chase].copy()
summary = {"adv_real_tercile_breaks_bn": [round(x / 1e9, 2) for x in q], "rows_E": len(P), "rows_primary": len(S),
           "rows_chase_excluded": int(P.chase.sum())}

def add_base(D, X):
    c = f"y{int(X*100)}"
    br = D.groupby(["year", "terc"])[c].mean().rename(f"b{c}")
    return D.join(br, on=["year", "terc"]), br

for X in XS:
    S, br = add_base(S, X)
    P, _ = add_base(P, X)
    br.reset_index().to_csv(f"{OUT}/base_rates_{int(X*100)}.csv", index=False)

rng = np.random.default_rng(SEED)
def boot_ratio(D, num, den, months):
    """block bootstrap theo tháng: tỉ lệ Σnum/Σden. Trả (CI lo, hi, mảng bootstrap)."""
    a = D.groupby("month")[num].sum().reindex(months, fill_value=0).to_numpy(float)
    b = D.groupby("month")[den].sum().reindex(months, fill_value=0).to_numpy(float)
    idx = rng.integers(0, len(months), size=(B, len(months)))
    bs = a[idx].sum(1) / np.where(b[idx].sum(1) == 0, np.nan, b[idx].sum(1))
    return np.nanpercentile(bs, 2.5), np.nanpercentile(bs, 97.5), bs

def lift_of(D, c):
    return D[c].sum() / D[f"b{c}"].sum() if len(D) else np.nan

rows = []
months = {p: sorted(S.loc[S.OOS == (p == "OOS"), "month"].unique()) for p in ["IS", "OOS"]}
nyears = {"IS": 6.0, "OOS": (S.loc[S.OOS, "time"].max() - pd.Timestamp("2020-01-01")).days / 365.25}
for sg in SIGS:
    for X in XS:
        c = f"y{int(X*100)}"
        r = {"sig": sg, "name": NAMES[sg], "X": X}
        for p in ["IS", "OOS"]:
            D = S[(S.OOS == (p == "OOS")) & S[sg]]
            D = D.assign(_y=D[c].astype(float), _b=D[f"b{c}"])
            L = lift_of(D, c)
            r[f"n_{p}"] = len(D); r[f"hits_{p}"] = int(D[c].sum()); r[f"L_{p}"] = L
            r[f"prec_{p}"] = D[c].mean() if len(D) else np.nan
            r[f"base_{p}"] = S.loc[S.OOS == (p == "OOS"), c].mean()
            if p == "OOS" and len(D) > 0:
                lo, hi, bs = boot_ratio(D, "_y", "_b", months[p])
                r.update(L_lo=lo, L_hi=hi, p_boot=(np.sum(bs <= 1) + 1) / (B + 1))
                lb = np.log(bs[np.isfinite(bs) & (bs > 0)]); r["MDE"] = float(np.exp(2.8 * lb.std()))
                r["eps_caught"] = int(D.loc[D[c], f"ep_{c}"].nunique())
                r["fp_rows_per_yr"] = (len(D) - D[c].sum()) / nyears[p]
                # cụm tín hiệu (cách ≥10 dòng) ⇒ FP theo cụm
                dd = D.sort_values(["ticker", "nhist"])
                start = dd.groupby("ticker").nhist.diff().fillna(99) >= 10
                cs = dd[start.to_numpy()]
                r["clusters"] = len(cs); r["cluster_prec"] = cs[c].mean(); r["fp_clusters_per_yr"] = (len(cs) - cs[c].sum()) / nyears[p]
                # LOYO
                yrs = sorted(D.year.unique()); ly = [lift_of(D[D.year != y], c) for y in yrs]
                r["LOYO_min"] = np.nanmin(ly) if ly else np.nan
                top2 = D.groupby("year")[c].sum().nlargest(2).index
                r["L_drop2"] = lift_of(D[~D.year.isin(top2)], c)
                # giao dịch
                T = D[~D.unfill & D.net_ex.notna()]
                T = T.assign(_one=1.0)
                r["n_unfill"] = int(D.unfill.sum()); r["n_trades"] = len(T)
                r["gross_ex"] = T.trade_ex.mean(); r["net_ex"] = T.net_ex.mean()
                if len(T):
                    lo2, hi2, _ = boot_ratio(T, "net_ex", "_one", months[p]); r.update(net_lo=lo2, net_hi=hi2)
                    mser = T.groupby("month").net_ex.mean()
                    r["SR_m"] = mser.mean() / mser.std() if len(mser) > 2 and mser.std() > 0 else np.nan
                    r["SR_T"] = len(mser); r["SR_skew"] = skew(mser) if len(mser) > 2 else 0; r["SR_kurt"] = kurtosis(mser, fisher=False) if len(mser) > 3 else 3
                r["cap_med_bn"] = 0.1 * D.ADV20.median() / 1e9
                r["cap_ge1bn_share"] = (0.1 * D.ADV20 >= 1e9).mean()
        rows.append(r)
R = pd.DataFrame(rows)
# BH
pv = R.p_boot.fillna(1).to_numpy(); m = len(pv); o = np.argsort(pv)
thr = (np.arange(1, m + 1) / m) * 0.10; passed = pv[o] <= thr
kmax = np.max(np.where(passed)[0]) + 1 if passed.any() else 0
R["BH"] = False; R.loc[o[:kmax], "BH"] = True
# DSR
srs = R.SR_m.dropna(); Nt = len(R); g = 0.5772156649
sr0 = np.sqrt(srs.var()) * ((1 - g) * norm.ppf(1 - 1 / Nt) + g * norm.ppf(1 - 1 / (Nt * np.e)))
def dsr(r):
    if pd.isna(r.SR_m): return np.nan
    den = np.sqrt(max(1e-9, 1 - r.SR_skew * r.SR_m + (r.SR_kurt - 1) / 4 * r.SR_m ** 2))
    return norm.cdf((r.SR_m - sr0) * np.sqrt(r.SR_T - 1) / den)
R["DSR"] = R.apply(dsr, axis=1)
R["G1"] = (R.L_OOS >= 1.5) & (R.L_lo > 1.0)
R["G2"] = R.BH
R["G3"] = R.L_IS > 1.0
R["G5"] = (R.LOYO_min >= 1.3) & (R.L_drop2 >= 1.2)
R["G4"] = (R.net_ex > 0) & (R.net_lo > 0)
R["G6"] = R.cap_med_bn >= 1.0
R["underpowered"] = R.MDE > 1.5
summary["SR0_monthly"] = sr0

# placebo: trial qua G1-G5 + top-3 L_OOS
cand = R[R.G1 & R.G2 & R.G3 & R.G5].index.tolist()
cand += [i for i in R.sort_values("L_OOS", ascending=False).index[:3] if i not in cand]
SO = S[S.OOS].sort_values(["ticker", "nhist"]).reset_index(drop=True)
grp = SO.groupby("ticker").indices
R["placebo_p"] = np.nan
for i in cand:
    sg, X = R.loc[i, "sig"], R.loc[i, "X"]; c = f"y{int(X*100)}"
    sig = SO[sg].to_numpy(); y = SO[c].to_numpy(float); b = SO[f"b{c}"].to_numpy()
    Lobs = (y * sig).sum() / (b * sig).sum(); cnt = 0
    prng = np.random.default_rng(SEED + i)
    for rep in range(200):
        sh = np.empty_like(sig)
        for tk, idx in grp.items():
            n = len(idx); kmaxm = n // 21 - 3
            k = 21 * prng.integers(3, kmaxm + 1) if kmaxm >= 3 else 0
            sh[idx] = np.roll(sig[idx], k)
        Lp = (y * sh).sum() / max((b * sh).sum(), 1e-12)
        cnt += Lp >= Lobs
    R.loc[i, "placebo_p"] = (cnt + 1) / 201
R["informative"] = R.G1 & R.G2 & R.G3 & R.G5 & (R.placebo_p < 0.05)
R["GO_paper"] = R.informative & R.G4 & (R.DSR >= 0.95) & R.G6
R.to_csv(f"{OUT}/results.csv", index=False)

# bản không lọc đuổi giá (mô tả)
U = []
for sg in SIGS:
    for X in XS:
        c = f"y{int(X*100)}"; D = P[P.OOS & P[sg]]
        U.append({"sig": sg, "X": X, "n_OOS_all": len(D), "L_OOS_all": lift_of(D, c), "prec_OOS_all": D[c].mean()})
pd.DataFrame(U).to_csv(f"{OUT}/results_unfiltered.csv", index=False)

# event view (hai chiều), OOS
EV = []
for X in XS:
    c = f"y{int(X*100)}"; O_ = P[P.OOS]
    t0 = O_[O_[f"T0_{c}"]]; neg = O_[~O_[c]]
    for sg in SIGS:
        EV.append({"sig": sg, "name": NAMES[sg], "X": X, "N_episodes": len(t0),
                   "recall_pre5": t0[f"pre5_{sg}"].mean(), "fpr_pre5": neg[f"pre5_{sg}"].mean(),
                   "recall_T0": t0[sg].mean(), "fpr_T0": neg[sg].mean()})
EVd = pd.DataFrame(EV); EVd["ratio_pre5"] = EVd.recall_pre5 / EVd.fpr_pre5; EVd["ratio_T0"] = EVd.recall_T0 / EVd.fpr_T0
EVd.to_csv(f"{OUT}/event_view.csv", index=False)

# tần suất nền
fr = []
for X in XS:
    c = f"y{int(X*100)}"
    for y_, D in P.groupby("year"):
        fr.append({"X": X, "year": y_, "rows": len(D), "base_rate": D[c].mean(), "episodes": int(D[f"T0_{c}"].sum()),
                   "tickers": D.ticker.nunique()})
    for t_, D in P[P.OOS].groupby("terc"):
        fr.append({"X": X, "year": f"OOS_terc{t_}", "rows": len(D), "base_rate": D[c].mean(), "episodes": int(D[f"T0_{c}"].sum()),
                   "tickers": D.ticker.nunique(), "adv_med_bn": D.ADV20.median() / 1e9})
pd.DataFrame(fr).to_csv(f"{OUT}/base_freq.csv", index=False)

# phân tầng top-5 (X=20), OOS
top5 = R[R.X == 0.20].sort_values("L_OOS", ascending=False).sig.head(5).tolist()
SO2 = S[S.OOS].copy(); SO2["btc"] = pd.qcut(SO2.breadth, 3, labels=["low", "mid", "high"])
st = []
for sg in top5:
    for col in ["dt5g", "btc"]:
        for v, D in SO2[SO2[sg]].groupby(col, observed=True):
            st.append({"sig": sg, "by": col, "level": v, "n": len(D), "L": lift_of(D, "y20"), "prec": D.y20.mean()})
    D = SO2[SO2[sg] & (0.1 * SO2.ADV20 >= 1e9)]
    st.append({"sig": sg, "by": "capacity>=1bn", "level": "ADV20>=10bn", "n": len(D), "L": lift_of(D, "y20"), "prec": D.y20.mean()})
pd.DataFrame(st).to_csv(f"{OUT}/strata.csv", index=False)

# climax / kết thúc đợt (mô tả)
CL = []
IR = P[P.run20 >= 0.30].copy(); IR["D"] = (IR.minex <= -0.15).astype(float); IR["_one"] = 1.0
for per, D0 in [("ALL", IR), ("OOS", IR[IR.OOS])]:
    base = D0.D.mean(); ms = sorted(D0.month.unique())
    for k in KS:
        D = D0[D0[k]]
        lo, hi, bs = boot_ratio(D.assign(_b=base), "D", "_one", ms) if len(D) else (np.nan, np.nan, np.array([np.nan]))
        CL.append({"K": k, "period": per, "n_inrun": len(D0), "base_D": base, "n": len(D), "P_D": D.D.mean(),
                   "lift": D.D.mean() / base if len(D) else np.nan, "P_lo": lo, "P_hi": hi,
                   "p_boot": (np.nansum(bs <= base) + 1) / (B + 1)})
pd.DataFrame(CL).to_csv(f"{OUT}/climax.csv", index=False)

# heatmap
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
hm = R.pivot(index="sig", columns="X", values="L_OOS").reindex(SIGS)
lo_ = R.pivot(index="sig", columns="X", values="L_lo").reindex(SIGS); hi_ = R.pivot(index="sig", columns="X", values="L_hi").reindex(SIGS)
fig, ax = plt.subplots(figsize=(6.4, 10))
im = ax.imshow(np.log2(hm.to_numpy(float)), cmap="RdBu_r", vmin=-1.6, vmax=1.6, aspect="auto")
for i in range(len(SIGS)):
    for j in range(2):
        ax.text(j, i, f"{hm.iat[i,j]:.2f}\n[{lo_.iat[i,j]:.2f}–{hi_.iat[i,j]:.2f}]", ha="center", va="center", fontsize=7)
ax.set_xticks([0, 1]); ax.set_xticklabels(["run-up ≥20%", "run-up ≥30%"])
ax.set_yticks(range(len(SIGS))); ax.set_yticklabels([f"{s} {NAMES[s]}" for s in SIGS], fontsize=7)
ax.axvline(0.5, color="w")
ax.set_title("Lift OOS 2020+ (chuẩn hoá năm×thanh khoản), CI95 khối tháng\nMẫu chống đuổi giá; ngưỡng GO: ≥1,5 và CI dưới >1", fontsize=8)
plt.colorbar(im, ax=ax, fraction=0.04, label="log2 lift"); plt.tight_layout(); plt.savefig(f"{OUT}/heatmap.png", dpi=130)

summary.update({"n_trials": len(R), "G1": int(R.G1.sum()), "BH": int(R.BH.sum()), "G3": int(R.G3.sum()), "G5": int(R.G5.sum()),
                "G4": int(R.G4.sum()), "informative": int(R.informative.sum()), "GO_paper": int(R.GO_paper.sum()),
                "underpowered": int(R.underpowered.sum()), "placebo_tested": [f"{R.sig[i]}@{R.X[i]}" for i in cand]})
json.dump(summary, open(f"{OUT}/summary.json", "w"), indent=1, default=float)
print(json.dumps(summary, indent=1, default=float))
