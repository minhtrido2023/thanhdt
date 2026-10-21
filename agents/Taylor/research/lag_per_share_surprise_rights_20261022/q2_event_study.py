# -*- coding: utf-8 -*-
"""Q2: event study production vs per-share (PS1/PS2) trên drift R+5→R+30 (y_ex = post_ret − VNINDEX).
Bootstrap cụm theo Release_Date và theo mùa (năm-quý Release). IS entry 2014-19 / OOS 2020+. LOYO."""
import numpy as np, pandas as pd
from scipy.stats import spearmanr
rng = np.random.default_rng(20261022)
B = 2000
e = pd.read_csv("events_ps.csv", parse_dates=["Release_Date", "entry"])
e = e[e.y_ex.notna()].copy()
e["season"] = e.Release_Date.dt.year.astype(str) + "Q" + e.Release_Date.dt.quarter.astype(str)
e["year"] = e.entry.dt.year
e["half"] = np.where(e.year <= 2019, "IS", "OOS")

def boot_diff(a, b, cl):
    """mean(a.y)−mean(b.y), cluster bootstrap (multinomial weights over clusters of union)."""
    keys = pd.Index(pd.concat([a[cl], b[cl]]).unique())
    ga, gb = a.groupby(cl).y_ex, b.groupby(cl).y_ex
    sa, na = ga.sum().reindex(keys, fill_value=0).values, ga.size().reindex(keys, fill_value=0).values
    sb, nb = gb.sum().reindex(keys, fill_value=0).values, gb.size().reindex(keys, fill_value=0).values
    W = rng.multinomial(len(keys), np.full(len(keys), 1 / len(keys)), size=B)
    with np.errstate(invalid="ignore", divide="ignore"):
        out = (W @ sa) / (W @ na) - (W @ sb) / (W @ nb)
    out = out[np.isfinite(out)]
    obs = a.y_ex.mean() - b.y_ex.mean()
    lo, hi = np.percentile(out, [2.5, 97.5]); return obs, lo, hi

def show(name, a, b):
    res = {"grp": name, "n_a": len(a), "dates_a": a.Release_Date.nunique(), "seasons_a": a.season.nunique(),
           "mean_a": a.y_ex.mean(), "n_b": len(b), "mean_b": b.y_ex.mean()}
    for cl in ("Release_Date", "season"):
        o, lo, hi = boot_diff(a, b, cl); res.update({"diff": o, f"ci_{cl[:4]}": f"[{lo:+.2f},{hi:+.2f}]"})
    for h in ("IS", "OOS"):
        aa, bb = a[a.half == h], b[b.half == h]
        res[f"diff_{h}"] = aa.y_ex.mean() - bb.y_ex.mean(); res[f"n_a_{h}"] = len(aa)
    return res

rows = []
U = e[e.U]
for v in ("ps1", "ps2"):
    drop = U[~U[f"U_{v}"]]; keep = U[U[f"U_{v}"]]
    rows.append(show(f"{v}: rớt qualify vs giữ", drop, keep))
    hl = U[U[f"U_{v}"] & (U.tier == "HI") & (U[f"tier_{v}"] == "LO")]
    hi_keep = U[U[f"U_{v}"] & (U.tier == "HI") & (U[f"tier_{v}"] == "HI")]
    lo_keep = U[U[f"U_{v}"] & (U.tier == "LO") & (U[f"tier_{v}"] == "LO")]
    rows.append(show(f"{v}: HI→LO vs HI giữ", hl, hi_keep))
    rows.append(show(f"{v}: HI→LO vs LO giữ", hl, lo_keep))
# reliable-share subset only (share_src == explained)
Ue = U[U.share_src == "explained"]
d2 = Ue[~Ue.U_ps2]; rows.append(show("ps2 [explained]: rớt vs giữ", d2, Ue[Ue.U_ps2]))
# Group L: |g-1|>=10% — does the production tier/qualify still sort returns?
L = U[(U.g - 1).abs() >= 0.10]; nL = U[(U.g - 1).abs() < 0.10]
rows.append(show("L(|g-1|>=10%) vs không L", L, nL))
rows.append(show("L: HI vs LO (production)", L[L.tier == "HI"], L[L.tier == "LO"]))
rows.append(show("L: HI vs LO (ps2)", L[L.U_ps2 & (L.tier_ps2 == "HI")], L[L.U_ps2 & (L.tier_ps2 == "LO")]))
rows.append(show("toàn U: HI vs LO (production)", U[U.tier == "HI"], U[U.tier == "LO"]))
rows.append(show("toàn U: HI vs LO (ps2)", U[U.U_ps2 & (U.tier_ps2 == "HI")], U[U.U_ps2 & (U.tier_ps2 == "LO")]))
res = pd.DataFrame(rows)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(res.round(2).to_string(index=False))
res.to_csv("q2_groups.csv", index=False)

# IC (Spearman) on the union where each variant qualifies; also on L
def ic(df, col):
    return spearmanr(df[col], df.y_ex).correlation if len(df) > 10 else np.nan
icrows = []
for nm, df in (("U", U), ("L", L)):
    for h in ("ALL", "IS", "OOS"):
        d = df if h == "ALL" else df[df.half == h]
        icrows.append({"set": nm, "half": h, "n": len(d), "IC_prod": ic(d, "surprise_B_MA"),
                       "IC_ps1": ic(d, "sur_ps1"), "IC_ps2": ic(d, "sur_ps2")})
# cluster bootstrap of IC_ps2 − IC_prod on L (season clusters)
idx = {k: g.index.values for k, g in L.groupby("season")}; keys = list(idx)
dd = []
for _ in range(B):
    s = L.loc[np.concatenate([idx[k] for k in rng.choice(keys, len(keys))])]
    dd.append(ic(s, "sur_ps2") - ic(s, "surprise_B_MA"))
print(pd.DataFrame(icrows).round(4).to_string(index=False))
print("L: IC_ps2−IC_prod season-cluster 95% CI:", np.round(np.percentile(dd, [2.5, 50, 97.5]), 4))

# LOYO for main contrast: ps2 rớt-qualify vs giữ
lo = []
for y in sorted(U.year.unique()):
    s = U[U.year != y]; lo.append((y, s[~s.U_ps2].y_ex.mean() - s[s.U_ps2].y_ex.mean(), int((U[U.year == y].U_ps2 == False).sum())))
print("LOYO ps2 rớt−giữ (bỏ năm y, n_rớt trong năm y):", [(y, round(d, 2), n) for y, d, n in lo])
print("per-year ps2 rớt−giữ:", [(y, round(g[~g.U_ps2].y_ex.mean() - g[g.U_ps2].y_ex.mean(), 2), int((~g.U_ps2).sum()))
                                 for y, g in U.groupby("year")])
