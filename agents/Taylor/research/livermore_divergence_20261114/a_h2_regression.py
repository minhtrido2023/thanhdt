"""A (H2): hồi quy call Livermore lên mom20/mom60/rp250. Theo A_PREDECL.md (md5 fd01a1ca)."""
import csv, json, sys
import numpy as np, pandas as pd
B = "/home/trido/thanhdt/WorkingClaude/mike/agents/Mike/research/livermore_stock_battery_20261105"
truth = {x["label"]: x for x in json.load(open(f"{B}/SEALED_truth.json"))}
res = list(csv.DictReader(open(f"{B}/livermore_results.csv")))
rows = []
for r in res:
    c = pd.read_csv(f"{B}/cases/{r['label']}.csv")
    assert len(c) == 250
    cl = c.close.values
    T = truth[r["label"]]
    rows.append(dict(label=r["label"], p=float(r["H20_P_UP"]), d=int(r["H20_DIR"] == "UP"),
                     rec=r["RECOGNIZED"].strip().lower() == "true", up=T["up"], fwd20=T["fwd20"], year=T["asof"][:4],
                     mom20=cl[249] / cl[229] - 1, mom60=cl[249] / cl[189] - 1,
                     rp250=(cl[249] - c.low.min()) / (c.high.max() - c.low.min()),
                     tmom20=T["mom20"], tmom60=T["mom60"]))
D = pd.DataFrame(rows)
# kiểm: mom20 sign từ case == mom20 trong truth (cùng chuỗi, normalize không đổi tỉ lệ)
agree_m20 = ((D.mom20 > 0).astype(int) == D.tmom20).mean(); agree_m60 = ((D.mom60 > 0).astype(int) == D.tmom60).mean()
X = np.column_stack([np.ones(len(D)), D.mom20, D.mom60, D.rp250])

def ols(y, X):
    b, *_ = np.linalg.lstsq(X, y, rcond=None); e = y - X @ b
    r2 = 1 - (e @ e) / ((y - y.mean()) @ (y - y.mean())); n, k = X.shape
    adj = 1 - (1 - r2) * (n - 1) / (n - k)
    pr = np.empty(n)
    for i in range(n):
        m = np.arange(n) != i; bi, *_ = np.linalg.lstsq(X[m], y[m], rcond=None); pr[i] = X[i] @ bi
    loo = 1 - ((y - pr) @ (y - pr)) / ((y - y.mean()) @ (y - y.mean()))
    return b, r2, adj, loo

def logit(y, X, it=100):
    b = np.zeros(X.shape[1])
    for _ in range(it):
        p = 1 / (1 + np.exp(-X @ b)); W = p * (1 - p)
        b = b + np.linalg.solve(X.T @ (X * W[:, None]) + 1e-9 * np.eye(len(b)), X.T @ (y - p))
    p = np.clip(1 / (1 + np.exp(-X @ b)), 1e-9, 1 - 1e-9)
    ll = (y * np.log(p) + (1 - y) * np.log(1 - p)).sum(); p0 = y.mean()
    ll0 = len(y) * (p0 * np.log(p0) + (1 - p0) * np.log(1 - p0))
    return b, 1 - ll / ll0

out = {"N": len(D), "n_recognized_true": int(D.rec.sum()),
       "check_sign_mom20_case_vs_truth": float(agree_m20), "check_sign_mom60_case_vs_truth": float(agree_m60)}
for nm, y in [("P_UP", D.p.values), ("DIR", D.d.values.astype(float))]:
    b, r2, adj, loo = ols(y, X)
    out[f"ols_{nm}"] = dict(coef=dict(zip(["const", "mom20", "mom60", "rp250"], np.round(b, 4).tolist())),
                            R2=round(r2, 4), R2_adj=round(adj, 4), R2_LOO=round(loo, 4))
    # đơn biến
    for f in ["mom20", "mom60", "rp250"]:
        out[f"corr_{nm}_{f}"] = round(float(np.corrcoef(y, D[f])[0, 1]), 4)
bl, mcf = logit(D.d.values.astype(float), np.column_stack([np.ones(len(D)), (D.mom20 - D.mom20.mean()) / D.mom20.std(),
                                                         (D.mom60 - D.mom60.mean()) / D.mom60.std(), (D.rp250 - D.rp250.mean()) / D.rp250.std()]))
out["logit_DIR_McFadden_R2"] = round(float(mcf), 4)
out["logit_DIR_coef_std"] = dict(zip(["const", "mom20", "mom60", "rp250"], np.round(bl, 4).tolist()))
rules = {"R1_contra_mom20": (D.mom20 <= 0).astype(int), "R2_contra_mom60": (D.mom60 <= 0).astype(int),
         "R3_contra_rp250": (D.rp250 <= 0.5).astype(int)}
for k, call in rules.items():
    out[k] = dict(agree_with_livermore=int((call == D.d).sum()), hit_vs_truth=int((call == D.up).sum()),
                  n_UP_calls=int(call.sum()))
out["livermore_hit"] = int((D.d == D.up).sum()); out["base_rate_up"] = float(D.up.mean())
# tách recognized
for g, sub in D.groupby("rec"):
    out[f"rec={g}"] = dict(N=len(sub), hit=int((sub.d == sub.up).sum()))
D.to_csv("A_features.csv", index=False)
json.dump(out, open("A_result.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
