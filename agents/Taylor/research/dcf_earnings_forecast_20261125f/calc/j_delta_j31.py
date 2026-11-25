# -*- coding: utf-8 -*-
"""j_delta_j31.py — J3.1: bảng delta J3 (panel V3.1, ..d/out_J3C + out_CYC_*) → J3.1 (panel V3.2, ./out_J3C + out_CYC_*). Chỉ đọc CSV/JSON, không tính lại mô hình.
Out: ../out_delta/{delta_ic36.csv, delta_pairs.csv, delta_pbo_dsr.json}"""
import os, json
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(HERE, ".."); J3 = os.path.join(F, "..", "dcf_earnings_forecast_20261125d")
O = os.path.join(F, "out_delta"); os.makedirs(O, exist_ok=True)
SETS = [("C_J2", "out_J3C"), ("CYC_ALL", "out_CYC_ALL"), ("CYC_CYC", "out_CYC_CYC"), ("CYC_REST", "out_CYC_REST")]
rows, prs, pd_ = [], [], {}
for tag, d in SETS:
    a = pd.read_csv(os.path.join(J3, d, "metrics2_C.csv")); b = pd.read_csv(os.path.join(F, d, "metrics2_C.csv"))
    a, b = a[a.scope == "ALL"], b[b.scope == "ALL"]
    m = a.merge(b, on=["model", "era"], suffixes=("_J3", "_J31"))
    for _, r in m.iterrows():
        rows.append({"set": tag, "model": r.model, "era": r.era, "ic36_J3": round(r.ic36_J3, 4), "ic36_J31": round(r.ic36_J31, 4), "d": round(r.ic36_J31 - r.ic36_J3, 4),
                     "resid_J3": round(r.ic36_resid_J3, 4), "resid_J31": round(r.ic36_resid_J31, 4), "U_hit_J3": round(r.U_hit_J3, 3), "U_hit_J31": round(r.U_hit_J31, 3),
                     "O_right_rel_J3": round(r.O_right_rel_J3, 3), "O_right_rel_J31": round(r.O_right_rel_J31, 3)})
    ca = pd.read_csv(os.path.join(J3, d, "C_diff.csv")); cb = pd.read_csv(os.path.join(F, d, "C_diff.csv"))
    mc = ca.merge(cb, on=["era", "variant", "ref"], suffixes=("_J3", "_J31"))
    for _, r in mc.iterrows():
        prs.append({"set": tag, "era": r.era, "pair": f"{r.variant}-{r.ref}", "dIC36_J3": round(r.dIC36_J3, 4), "dIC36_J31": round(r.dIC36_J31, 4),
                    "yrs_pos_J3": f"{r.n_years_pos_J3}/{r.n_years_J3}", "yrs_pos_J31": f"{r.n_years_pos_J31}/{r.n_years_J31}", "ci95_J31": r.ci95_J31})
    pd_[tag] = {"PBO_J3": round(json.load(open(os.path.join(J3, d, "C_pbo.json")))["PBO"], 3), "PBO_J31": round(json.load(open(os.path.join(F, d, "C_pbo.json")))["PBO"], 3)}
da, db = json.load(open(os.path.join(J3, "out_CYC_ALL", "dsr_cycle.json"))), json.load(open(os.path.join(F, "out_CYC_ALL", "dsr_cycle.json")))
pd_["DSR"] = {t: {k: {"J3": [da[t][k]["DSR"], da[t][k]["years_pos"], da[t][k]["mean"]], "J31": [db[t][k]["DSR"], db[t][k]["years_pos"], db[t][k]["mean"]]} for k in da[t]} for t in da}
pd.DataFrame(rows).to_csv(os.path.join(O, "delta_ic36.csv"), index=False); pd.DataFrame(prs).to_csv(os.path.join(O, "delta_pairs.csv"), index=False)
json.dump(pd_, open(os.path.join(O, "delta_pbo_dsr.json"), "w"), indent=1)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(pd.DataFrame(rows)[["set", "model", "era", "ic36_J3", "ic36_J31", "d", "resid_J3", "resid_J31"]].to_string(index=False))
print(pd.DataFrame(prs)[["set", "era", "pair", "dIC36_J3", "dIC36_J31", "yrs_pos_J3", "yrs_pos_J31"]].to_string(index=False)); print(json.dumps(pd_, indent=1))
