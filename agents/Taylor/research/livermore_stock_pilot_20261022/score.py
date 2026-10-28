#!/usr/bin/env python3
"""Chấm điểm cơ khí theo PREREG (md5 018bd323…). CHỈ chạy SAU khi reads.csv đã khoá md5 trong reads_md5.lock.log."""
import hashlib, os, re, sys
import numpy as np, pandas as pd
from scipy.stats import chi2
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
D = os.path.dirname(os.path.abspath(__file__)); B = 5000; rng = np.random.default_rng(20261022)
lock = open(f"{D}/reads_md5.lock.log").read().strip().split("\n")[-1]
m = hashlib.md5(open(f"{D}/reads.csv", "rb").read()).hexdigest(); assert m in lock, (m, lock)
print("reads.csv md5", m, "khớp lock log")
rd = pd.read_csv(f"{D}/reads.csv"); key = pd.read_csv(f"{D}/case_key_HIDDEN.csv", parse_dates=["ent"])
df = key.merge(rd, on="id"); assert len(df) == len(key), (len(df), len(key))
df["Q"] = df.ent.dt.year.astype(str) + "Q" + df.ent.dt.quarter.astype(str)
df["POS"] = (df.ret > 0).astype(int); df["HIT"] = df.HIT15.astype(int); df["gv"] = df.G_VOL.astype(bool)
con_txt = df.CONTAMINATION.fillna("").str.strip()
df["contam"] = ~con_txt.str.match(r"(?i)^(none|không|khong|no\b|n/a|null)")
print(f"N={len(df)} | dương tính HIT15={df.HIT.sum()} (base {df.HIT.mean():.3f}) | cờ nhiễm={df.contam.sum()}")
print("Nhiễm (đọc tay):"); [print("  ", r.id, "|", r.CONTAMINATION[:110]) for r in df[df.contam].itertuples()]

def auc(y, p):
    return roc_auc_score(y, p) if 0 < y.sum() < len(y) else np.nan
def pooled(d, score="P_HIT15"):
    a, w = [], []
    for g in (True, False):
        s = d[d.gv == g]; au = auc(s.HIT.values, s[score].values)
        if not np.isnan(au): a.append(au); w.append(s.HIT.sum())
    return np.average(a, weights=w) if a else np.nan
quarters = df.Q.unique(); idx = {q: np.where(df.Q.values == q)[0] for q in quarters}
def boot(fn):
    out = []
    for _ in range(B):
        qs = rng.choice(quarters, len(quarters)); ii = np.concatenate([idx[q] for q in qs])
        v = fn(df.iloc[ii].reset_index(drop=True))
        if not np.isnan(v): out.append(v)
    o = np.array(out); return np.percentile(o, [2.5, 97.5]), len(o)
def rep(name, pt, ci): print(f"{name}: {pt:.4f}  CI95 cụm-quý [{ci[0][0]:.4f}, {ci[0][1]:.4f}]  (boot hợp lệ {ci[1]}/{B}, {len(quarters)} quý)")
res = {}
# ---- (1)
for lab, d in (("TẤT CẢ", df), ("LOẠI nhiễm", df[~df.contam])):
    pt = pooled(d); ci = boot(pooled) if lab == "TẤT CẢ" else None
    if lab != "TẤT CẢ":
        sub = df[~df.contam].reset_index(drop=True); q2 = sub.Q.unique(); ix2 = {q: np.where(sub.Q.values == q)[0] for q in q2}
        o = []
        for _ in range(B):
            qs = rng.choice(q2, len(q2)); v = pooled(sub.iloc[np.concatenate([ix2[q] for q in qs])].reset_index(drop=True))
            if not np.isnan(v): o.append(v)
        ci = (np.percentile(o, [2.5, 97.5]), len(o))
    rep(f"(1) AUC trong-tầng gộp [{lab}, n={len(d)}]", pt, ci); res[lab] = (pt, ci)
    for g in (True, False):
        s = d[d.gv == g]; print(f"     tầng G_VOL={g}: AUC {auc(s.HIT.values, s.P_HIT15.values):.4f}  (n={len(s)}, dương={s.HIT.sum()})")
# AUC thô và theo book
print(f"     AUC thô toàn mẫu: {auc(df.HIT.values, df.P_HIT15.values):.4f}; theo book: " + ", ".join(f"{b} {auc(s.HIT.values, s.P_HIT15.values):.4f} (n={len(s)})" for b, s in df.groupby('book')))
print(f"     P_HIT15 TB theo tầng: " + ", ".join(f"G_VOL={g} {s.P_HIT15.mean():.3f} (thực {s.HIT.mean():.3f})" for g, s in df.groupby('gv')))
print("     RISK vs HIT:", df.groupby("RISK").HIT.agg(["mean", "size"]).round(3).to_dict("index"))
# ---- (2)
feat = ["VOL60", "RUN20", "DIST52"]; ok = df[feat].notna().all(axis=1); print(f"(2) thiếu đặc trưng cơ học: {(~ok).sum()} (loại khỏi (2))")
d2 = df[ok].reset_index(drop=True)
lg = lambda p: np.log(np.clip(p, .01, .99) / (1 - np.clip(p, .01, .99)))
X1 = d2[feat].values; X2 = np.c_[X1, lg(d2.P_HIT15.values)]; y = d2.HIT.values; grp = d2.Q.values
def oof(X):
    p = np.zeros(len(y)); skf = StratifiedGroupKFold(5, shuffle=True, random_state=20261022)
    for tr, te in skf.split(X, y, grp):
        sc = StandardScaler().fit(X[tr]); mdl = LogisticRegression(penalty=None, max_iter=2000).fit(sc.transform(X[tr]), y[tr])
        p[te] = mdl.predict_proba(sc.transform(X[te]))[:, 1]
    return p
p1, p2 = oof(X1), oof(X2); a1, a2 = roc_auc_score(y, p1), roc_auc_score(y, p2)
q2 = d2.Q.unique(); ix = {q: np.where(grp == q)[0] for q in q2}; dd = []
for _ in range(B):
    ii = np.concatenate([ix[q] for q in rng.choice(q2, len(q2))])
    if 0 < y[ii].sum() < len(ii): dd.append(roc_auc_score(y[ii], p2[ii]) - roc_auc_score(y[ii], p1[ii]))
ci_d = np.percentile(dd, [2.5, 97.5])
def ll(X):
    sc = StandardScaler().fit(X); mdl = LogisticRegression(penalty=None, max_iter=5000).fit(sc.transform(X), y)
    p = np.clip(mdl.predict_proba(sc.transform(X))[:, 1], 1e-12, 1 - 1e-12); return (y * np.log(p) + (1 - y) * np.log(1 - p)).sum()
lr = 2 * (ll(X2) - ll(X1)); pv = chi2.sf(lr, 1)
print(f"(2) B1 cơ học AUC CV={a1:.4f} | +logit(P_HIT15) AUC CV={a2:.4f} | ΔAUC={a2-a1:+.4f} CI95 cụm-quý [{ci_d[0]:+.4f}, {ci_d[1]:+.4f}] | LR={lr:.2f} p={pv:.4g}")
# ---- (3) baselines
print(f"(3) B0 AUC 0.5 | B1 cơ học AUC CV {a1:.4f} | B2 cờ G_VOL AUC {auc(df.HIT.values, df.gv.astype(int).values):.4f} | Livermore thô {auc(df.HIT.values, df.P_HIT15.values):.4f}")
# ---- (4) P_POS
base = df.POS.mean(); br_l = brier_score_loss(df.POS, df.P_POS); br_0 = brier_score_loss(df.POS, np.full(len(df), base))
bb = []
for _ in range(B):
    ii = np.concatenate([idx[q] for q in rng.choice(quarters, len(quarters))]); s = df.iloc[ii]
    bb.append(brier_score_loss(s.POS, np.full(len(s), s.POS.mean())) - brier_score_loss(s.POS, s.P_POS))
ca = []
for _ in range(B):
    ii = np.concatenate([idx[q] for q in rng.choice(quarters, len(quarters))]); s = df.iloc[ii]; v = auc(s.POS.values, s.P_POS.values)
    if not np.isnan(v): ca.append(v)
print(f"(4) P_POS: AUC {auc(df.POS.values, df.P_POS.values):.4f} CI [{np.percentile(ca,2.5):.4f},{np.percentile(ca,97.5):.4f}] | Brier {br_l:.4f} vs B0 {br_0:.4f} (Δ=B0−L {br_0-br_l:+.4f} CI [{np.percentile(bb,2.5):+.4f},{np.percentile(bb,97.5):+.4f}]) | base POS {base:.3f}")
# ---- nhãn
a_ok = res["TẤT CẢ"][0] >= .58 and res["TẤT CẢ"][1][0][0] > .5
b_ok = ci_d[0] > 0
c_ok = (res["LOẠI nhiễm"][0] - .5) * (res["TẤT CẢ"][0] - .5) > 0
nog = (not a_ok) or (not b_ok) or res["TẤT CẢ"][0] <= .52
lab = "GO-LẠI" if (a_ok and b_ok and c_ok) else ("NO-GO" if nog else "INCONCLUSIVE")
print(f"\nTIÊU CHÍ: (a)={a_ok} (b)={b_ok} (c)={c_ok} AUC<=0.52:{res['TẤT CẢ'][0] <= .52}  =>  NHÃN: {lab}")
