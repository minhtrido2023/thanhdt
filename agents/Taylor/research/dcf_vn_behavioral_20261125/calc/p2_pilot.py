# -*- coding: utf-8 -*-
"""p2_pilot.py — pilot G0 theo PRELOCK_PILOT §3–§5. Out: ../out/pilot_results.json, pilot_table.md, pilot_pred_h{12,24}.parquet
Env: LABEL=h50|h0|h100 (mặc định h50), TAG (hậu tố file)."""
import os, json, sys
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
V3 = os.environ.get("V3_DIR", f"{WC}/wt-dcf-v3-20261125/agents/Taylor/research/dcf_vn_redesign_20261125c")
LABEL = os.environ.get("LABEL", "h50"); TAG = os.environ.get("TAG", ""); SEED = 20261125; B = 2000
pan = pd.read_parquet(f"{V3}/out_F/vp2.parquet", columns=["ticker", "ym", "time", "in_universe", "src", "route", "ep", "lv_ENS2", "lv_L2_ENS2",
                      "fwd12_" + LABEL, "fwd24_" + LABEL, "ended12", "ended24"])
ft = pd.read_parquet(os.path.join(OUT, "feat.parquet")).rename(columns={"time": "ftime"})
d = pan[pan.in_universe].merge(ft, on=["ticker", "ym"], how="left")
RES = {"label": LABEL, "date_match_share": float((d.time == d.ftime).mean())}
FEATS = ["mom", "rev1", "ep", "lv_ENS2", "hi52", "cgo", "lv_L2_ENS2"]
CORE = ["mom", "rev1", "ep", "lv_ENS2", "hi52", "cgo"]                      # mẫu chung = đủ đặc trưng của F
MODELS = {"B1": ["mom", "rev1"], "B2": ["ep"], "B3": ["lv_ENS2"], "B4": ["lv_L2_ENS2"], "F0": ["mom", "rev1", "ep", "lv_ENS2"],
          "F": ["mom", "rev1", "ep", "lv_ENS2", "hi52", "cgo"], "A": ["lv_ENS2", "hi52", "cgo"]}
d["mi"] = d.ym.str[:4].astype(int) * 12 + d.ym.str[5:7].astype(int) - 1
RES["n_inuni"] = int(len(d)); d = d.dropna(subset=CORE).copy(); RES["n_core"] = int(len(d))
for f in FEATS:                                                             # hạng trong tháng → [−0,5; +0,5]
    d["r_" + f] = d.groupby("mi")[f].rank(pct=True) - 0.5
d["r_lv_L2_ENS2"] = d["r_lv_L2_ENS2"].fillna(0.0)                           # B4 thiếu lớp 2 ⇒ trung tính
MI = lambda s: int(s[:4]) * 12 + int(s[5:7]) - 1
S0 = MI("2013-01"); FREEZE = MI("2019-12")
WIN = {12: (MI("2015-01"), MI("2019-12"), MI("2020-01"), MI("2025-10")), 24: (MI("2016-01"), MI("2019-12"), MI("2020-01"), MI("2024-10"))}

def sp(a, b):
    return np.corrcoef(pd.Series(a).rank().values, pd.Series(b).rank().values)[0, 1]

def boot(vals_by_year, seed=SEED):
    yrs = sorted(vals_by_year); rng = np.random.default_rng(seed); out = []
    for _ in range(B):
        pick = rng.choice(yrs, len(yrs)); out.append(np.mean(np.concatenate([vals_by_year[y] for y in pick])))
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))

def by_year(mis, vals):
    o = {}
    for m, v in zip(mis, vals):
        if np.isfinite(v): o.setdefault(m // 12, []).append(v)
    return {k: np.array(v) for k, v in o.items()}

def stat(mis, vals):
    v = np.array(vals, float); ok = np.isfinite(v)
    if ok.sum() == 0: return None
    lo, hi = boot(by_year(np.array(mis)[ok], v[ok])); return {"mean": float(v[ok].mean()), "lo": lo, "hi": hi, "n_m": int(ok.sum()), "n_y": len(set(np.array(mis)[ok] // 12))}

lines = []
for h in (12, 24):
    ycol = f"fwd{h}_{LABEL}"; x = d.dropna(subset=[ycol]).copy()
    x["ydm"] = x[ycol] - x.groupby("mi")[ycol].transform("mean")
    lo_, hi_ = x.groupby("mi").ydm.transform(lambda s: s.quantile(0.01)), x.groupby("mi").ydm.transform(lambda s: s.quantile(0.99))
    x["yw"] = x.ydm.clip(lo_, hi_)
    mu_m = x.groupby("mi")[ycol].mean()                                    # lợi suất EW h tháng của tháng as-of
    # hệ số cắt ngang từng tháng
    coef = {k: {} for k in MODELS}
    for mi, gdf in x.groupby("mi"):
        if mi < S0 or len(gdf) < 30: continue
        for k, fs in MODELS.items():
            X = np.column_stack([gdf["r_" + f].values for f in fs]); coef[k][mi] = np.linalg.lstsq(X, gdf.yw.values, rcond=None)[0]
    is0, is1, o0, o1 = WIN[h]
    def beta(k, t, frozen):
        lim = (FREEZE if frozen else t) - h
        ms = [m for m in coef[k] if m <= lim]
        return np.mean([coef[k][m] for m in ms], axis=0) if len(ms) >= 12 else None
    def mu_hat(t, frozen):
        lim = (FREEZE if frozen else t) - h; v = mu_m[(mu_m.index <= lim) & (mu_m.index >= S0)]
        return float(v.mean()) if len(v) >= 12 else np.nan
    preds = []
    for mi, gdf in x.groupby("mi"):
        era = "IS" if is0 <= mi <= is1 else ("OOS" if o0 <= mi <= o1 else None)
        if era is None: continue
        fr = era == "OOS"; row = gdf[["ticker", "ym", "mi", "route", "src", ycol, "ydm", "r_lv_ENS2"]].copy(); row["era"] = era; row["mu"] = mu_hat(mi, fr)
        for k, fs in MODELS.items():
            b = beta(k, mi, fr); row["p_" + k] = np.nan if b is None else np.column_stack([gdf["r_" + f].values for f in fs]) @ b
        bF = beta("F", mi, fr)
        if bF is not None:                                                  # thành phần hành vi của F: mom, rev1, hi52, cgo
            idx = [MODELS["F"].index(f) for f in ("mom", "rev1", "hi52", "cgo")]
            row["beh"] = np.column_stack([gdf["r_" + f].values for f in ("mom", "rev1", "hi52", "cgo")]) @ bF[idx]
        preds.append(row)
    P = pd.concat(preds, ignore_index=True); P.to_parquet(os.path.join(OUT, f"pilot_pred_h{h}{TAG}.parquet"), index=False)
    R = {"coef_frozen": {k: [float(v) for v in beta(k, 0, True)] for k in MODELS}, "n_coef_months_frozen": int(sum(m <= FREEZE - h for m in coef["F"]))}
    for era in ("IS", "OOS"):
        E = P[P.era == era]; r = {"n_rows": int(len(E)), "n_tk": int(E.ticker.nunique()), "n_months": int(E.mi.nunique())}
        per = {k: {} for k in MODELS}; mae = {k: {} for k in list(MODELS) + ["RW"]}; hit = {k: {} for k in MODELS}; icside = {}
        absm = {"RW": {}, "RWmu": {}, "F": {}, "F0": {}}
        for mi, gdf in E.groupby("mi"):
            y = gdf.ydm.values; mae["RW"][mi] = np.abs(y).mean(); ya = gdf[ycol].values; mu = gdf.mu.iloc[0]
            absm["RW"][mi] = np.abs(ya).mean(); absm["RWmu"][mi] = np.abs(ya - mu).mean()
            for k in MODELS:
                p = gdf["p_" + k].values
                if not np.isfinite(p).all(): continue
                per[k][mi] = sp(p, y); mae[k][mi] = np.abs(y - p).mean()
                q1, q2 = np.quantile(p, [1 / 3, 2 / 3]); top = p >= q2; bot = p <= q1
                hit[k][mi] = 0.5 * ((y[top] > 0).mean() + (y[bot] < 0).mean())
                if k in absm: absm[k][mi] = np.abs(ya - mu - p).mean()
            for side, msk in (("cheap", gdf.r_lv_ENS2.values >= 1 / 6), ("exp", gdf.r_lv_ENS2.values <= -1 / 6)):
                for k in ("F", "F0", "B1"):
                    p = gdf["p_" + k].values[msk]
                    if np.isfinite(p).all() and msk.sum() >= 15: icside.setdefault(f"{k}_{side}", {})[mi] = sp(p, y[msk])
        ms = sorted(mae["RW"])
        r["ic"] = {k: stat(list(per[k]), list(per[k].values())) for k in MODELS}
        def diff(a, b, src=per):
            cm = sorted(set(src[a]) & set(src[b])); return stat(cm, [src[a][m] - src[b][m] for m in cm])
        r["dic"] = {f"{a}-{b}": diff(a, b) for a, b in (("F", "F0"), ("A", "B3"), ("F", "B1"), ("F", "B2"), ("F", "B3"), ("F", "B4"), ("F0", "B2"), ("B3", "B2"))}
        def skill(k):
            cm = sorted(mae[k]); a = np.array([mae[k][m] for m in cm]); b = np.array([mae["RW"][m] for m in cm]); return float(1 - a.sum() / b.sum())
        r["skill_rel"] = {k: skill(k) for k in MODELS}
        cm = sorted(set(mae["F"]) & set(mae["F0"])); r["dskill_F_F0"] = stat(cm, [(mae["F0"][m] - mae["F"][m]) / mae["RW"][m] for m in cm])
        r["hit"] = {k: stat(list(hit[k]), list(hit[k].values())) for k in MODELS}
        r["mae_abs"] = {k: float(np.mean(list(v.values()))) for k, v in absm.items() if v}
        r["ic_side"] = {k: stat(list(v), list(v.values())) for k, v in icside.items()}
        r["dic_side"] = {s: (lambda cm: stat(cm, [icside[f"F_{s}"][m] - icside[f"F0_{s}"][m] for m in cm]))(sorted(set(icside.get(f"F_{s}", {})) & set(icside.get(f"F0_{s}", {})))) for s in ("cheap", "exp")}
        Eb = E.dropna(subset=["beh"]).copy()
        Eb["val"] = np.where(Eb.r_lv_ENS2 >= 0, "noi_tai_re", "noi_tai_dat"); Eb["bh"] = np.where(Eb.beh >= Eb.groupby("mi").beh.transform("median"), "hanhvi_cao", "hanhvi_thap")
        q = Eb.groupby(["mi", "val", "bh"]).ydm.mean().reset_index(); r["quad"] = {f"{a}|{b}": stat(list(gq.mi), list(gq.ydm)) for (a, b), gq in q.groupby(["val", "bh"])}
        R[era] = r
        for k in MODELS:
            s = r["ic"][k]; lines.append(f"| h={h} | {era} | {k} | {s['mean']:+.3f} [{s['lo']:+.3f}; {s['hi']:+.3f}] | {r['skill_rel'][k]:+.4f} | {r['hit'][k]['mean']:.3f} | {s['n_m']} / {s['n_y']} |")
    RES[f"h{h}"] = R
json.dump(RES, open(os.path.join(OUT, f"pilot_results{TAG}.json"), "w"), indent=1, ensure_ascii=False)
open(os.path.join(OUT, f"pilot_table{TAG}.md"), "w").write("| h | era | mô hình | IC [CI khối năm] | kỹ năng sai số tương đối | đúng chiều | tháng / năm |\n|---|---|---|---|---|---|---|\n" + "\n".join(lines) + "\n")
print(open(os.path.join(OUT, f"pilot_table{TAG}.md")).read())
for h in (12, 24):
    for era in ("IS", "OOS"):
        r = RES[f"h{h}"][era]; print(h, era, "n", r["n_rows"], r["n_tk"], "dIC", {k: (round(v["mean"], 4), round(v["lo"], 4), round(v["hi"], 4)) for k, v in r["dic"].items()})
        print("   dskill F-F0", r["dskill_F_F0"], "mae_abs", r["mae_abs"]); print("   side", {k: round(v["mean"], 3) for k, v in r["ic_side"].items()}, "dside", {k: (round(v["mean"], 4), round(v["lo"], 4), round(v["hi"], 4)) for k, v in r["dic_side"].items()})
        print("   quad", {k: (round(v["mean"], 4), round(v["lo"], 4), round(v["hi"], 4)) for k, v in r["quad"].items()})
    print("  coef_frozen", {k: np.round(v, 3).tolist() for k, v in RES[f"h{h}"]["coef_frozen"].items()}, RES[f"h{h}"]["n_coef_months_frozen"])
print({k: RES[k] for k in ("date_match_share", "n_inuni", "n_core")})
