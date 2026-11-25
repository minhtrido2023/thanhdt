# -*- coding: utf-8 -*-
"""c_diff_j4.py — PRELOCK_J4 §4: ΔIC36 theo năm (Mk − P1/D0/EP; P1 − D0/EP), tiêu chí GO, DSR (N thử 13), PBO {P1,M1..M5}.
In: ../out_{ALL,CYC,REST}/ic_year2_J4.csv. Out: ../out_ALL/J4_diff.csv, ../out_ALL/J4_verdict.json"""
import os, json, itertools
import numpy as np, pandas as pd
from scipy.stats import norm, skew, kurtosis
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, ".."); NTRIAL = 13; EG = 0.5772156649
MS = ["M1", "M2", "M3", "M4", "M5"]
def dsr(x):
    T = len(x); sr = x.mean() / x.std(ddof=1)
    sr0 = np.sqrt(1.0 / T) * ((1 - EG) * norm.ppf(1 - 1.0 / NTRIAL) + EG * norm.ppf(1 - 1.0 / (NTRIAL * np.e)))
    g3, g4 = skew(x), kurtosis(x, fisher=False)
    return float(norm.cdf((sr - sr0) * np.sqrt(T - 1) / np.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))), float(sr), float(sr0)
rows = []; V = {}
for tag in ("ALL", "CYC", "REST"):
    icy = pd.read_csv(os.path.join(D, f"out_{tag}", "ic_year2_J4.csv")); icy = icy[icy.scope == "ALL"]
    piv = icy.pivot_table(index=["t", "year"], columns="model", values="ic36").reset_index()
    Y = piv.groupby("year")[["D0", "EP", "P1"] + MS].mean().loc[2014:2023]
    for v in MS + ["P1"]:
        for ref in (["P1", "D0", "EP"] if v != "P1" else ["D0", "EP"]):
            for era, (a, b) in (("IS", (2014, 2019)), ("OOS", (2020, 2023))):
                x = piv[piv.year.between(a, b)][["year", v, ref]].dropna(); df = x[v] - x[ref]; by = (x.assign(df=df).groupby("year").df.mean())
                rows.append({"scope": tag, "variant": v, "ref": ref, "era": era, "dIC36": float(df.mean()), "n_dates": int(len(x)), "n_years": int(len(by)),
                             "n_years_pos": int((by > 0).sum()), "by_year": {int(k): round(float(q), 4) for k, q in by.items()},
                             "ic_v": float(x[v].mean()), "ic_ref": float(x[ref].mean())})
    if tag == "ALL":
        for v in MS:
            d_, sr, sr0 = dsr((Y[v] - Y["P1"]).values); V.setdefault("DSR_vs_P1", {})[v] = {"DSR": round(d_, 3), "SR_year": round(sr, 3), "SR0": round(sr0, 3)}
        d_, sr, sr0 = dsr((Y["P1"] - Y["D0"]).values); V["DSR_P1_vs_D0"] = {"DSR": round(d_, 3), "SR_year": round(sr, 3)}
        Z = Y[["P1"] + MS]; yrs = list(Z.index); S = len(yrs); lam = []
        for comb in itertools.combinations(range(S), S // 2):
            te = [i for i in range(S) if i not in comb]; best = Z.iloc[list(comb)].mean().idxmax(); rk = Z.iloc[te].mean().rank()[best] / (Z.shape[1] + 1)
            lam.append(np.log(rk / (1 - rk)))
        V["PBO_P1_M1_M5"] = float(np.mean(np.array(lam) <= 0)); V["IC36_by_year_ALL"] = Y.round(4).to_dict()
Dd = pd.DataFrame(rows); Dd.to_csv(os.path.join(D, "out_ALL", "J4_diff.csv"), index=False)
A = Dd[Dd.scope == "ALL"]
def get(v, ref, era):
    r = A[(A.variant == v) & (A.ref == ref) & (A.era == era)].iloc[0]; return r
verdict = {}
for v in MS:
    o = {ref: get(v, ref, "OOS") for ref in ("P1", "D0", "EP")}; i = get(v, "P1", "IS")
    beat_p1 = bool(o["P1"].dIC36 > 0 and o["P1"].n_years_pos >= 3)
    go = beat_p1 and all(o[r].dIC36 > 0 and o[r].n_years_pos >= 3 for r in ("D0", "EP")) and i.dIC36 >= 0 and V["DSR_vs_P1"][v]["DSR"] >= 0.95
    verdict[v] = {"OOS_dP1": round(float(o["P1"].dIC36), 4), "OOS_yrs_pos_P1": int(o["P1"].n_years_pos), "OOS_dD0": round(float(o["D0"].dIC36), 4), "OOS_yrs_pos_D0": int(o["D0"].n_years_pos),
                  "OOS_dEP": round(float(o["EP"].dIC36), 4), "OOS_yrs_pos_EP": int(o["EP"].n_years_pos), "IS_dP1": round(float(i.dIC36), 4), "IS_yrs_pos_P1": int(i.n_years_pos),
                  "beats_P1_rule": beat_p1, "GO": bool(go)}
V["verdict"] = verdict; V["NO_NEW"] = not any(x["beats_P1_rule"] for x in verdict.values())
V["P1_ref"] = {era: {ref: [round(float(get("P1", ref, era).dIC36), 4), int(get("P1", ref, era).n_years_pos), int(get("P1", ref, era).n_years)] for ref in ("D0", "EP")} for era in ("IS", "OOS")}
json.dump(V, open(os.path.join(D, "out_ALL", "J4_verdict.json"), "w"), indent=1); print(json.dumps({k: V[k] for k in ("verdict", "NO_NEW", "P1_ref", "DSR_vs_P1", "PBO_P1_M1_M5")}, indent=1))
pd.set_option("display.width", 250)
print(Dd[["scope", "variant", "ref", "era", "ic_v", "ic_ref", "dIC36", "n_years_pos", "n_years"]].round(4).to_string(index=False))
