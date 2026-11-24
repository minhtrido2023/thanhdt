# -*- coding: utf-8 -*-
"""d_metrics2.py — đo theo PRELOCK V2 §2–§4. In: ../out/vp2.parquet.
Out: metrics2.csv (mô hình × era × phạm vi), ic_year2.csv, cases2.csv, sample2.csv, ablation2.json, base2.json.
Phạm vi: ALL = BQ + mã vắng BQ, H = −50% (chính); ALL_h0 / ALL_h100 = cận; BQ = chỉ mã BQ, bỏ dòng mất giá (như vòng 1)."""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
SEED = 20261124; B_YEAR = 2000; B_TK = 500
ONLY = os.environ.get("ONLY"); SFX = os.environ.get("SFX", "")
pan = pd.read_parquet(os.path.join(OUT, "vp2.parquet")).sort_values(["ticker", "mi"]).reset_index(drop=True)
MODELS = ["A_pit", "A_RI", "D0", "D0J", "D0B", "DDM", "EPV", "MULT", "HEDf", "HEDr", "HEDL", "REL", "G1", "ENS1", "ENS1w", "ENS2", "META",
          "L2_ENS1", "L2_ENS2", "L2_D0B", "L2_MULT", "L2_ENS1w", "N0", "EP", "BP"]
pan["lv_EP"] = pan.ep; pan["lv_BP"] = np.log(pan.bp.where(pan.bp > 0))      # EP/BP chỉ dùng cho IC (hạng), không có "tâm"
if ONLY:
    MODELS = ONLY.split(",")
tks = sorted(pan.ticker.unique()); tid = {t: i for i, t in enumerate(tks)}; m0 = int(pan.mi.min()); T = int(pan.mi.max()) - m0 + 1; N = len(tks)
ri = (pan.mi.values - m0); ci = pan.ticker.map(tid).values
def dense(v, fill=np.nan, dtype=float):
    M = np.full((T, N), fill, dtype=dtype); M[ri, ci] = v; return M
LP = dense(np.log(pan.Close.values)); IU = dense(pan.in_universe.values, False, bool); SRCB = dense((pan.src == "BQ").values, False, bool)
def mi_of(ym):
    p = pd.Period(ym, freq="M"); return p.year * 12 + p.month - m0
T_IS0, T_IS1, T_OOS1 = mi_of("2014-01"), mi_of("2019-12"), mi_of("2023-10")
ERA = {"IS": (T_IS0, T_IS1), "OOS": (T_IS1 + 1, T_OOS1)}
QM = np.array([((m0 + t - 1) % 12 + 1) in (3, 6, 9, 12) for t in range(T)]); YR = np.array([(m0 + t - 1) // 12 for t in range(T)])
def fwd_stat(M, fn):
    """thống kê trên cửa sổ (t, t+36] theo từng cột."""
    d = pd.DataFrame(M)[::-1]
    r = getattr(d.rolling(36, min_periods=1), fn)()[::-1].shift(-1)
    return r.values
FMAXP = fwd_stat(LP, "max")
SC = {}                                                                 # phạm vi: nhãn + mặt nạ
def scope(name, fcol, bq_only):
    F = {n: dense(pan[f"fwd{n}_{fcol}"].values) for n in (12, 24, 36)}
    S = IU & (SRCB if bq_only else True)
    EX = {}
    for n, f in F.items():
        with np.errstate(all="ignore"):
            bm = np.log(np.nanmean(np.where(S, np.exp(f), np.nan), axis=1))
        EX[n] = f - bm[:, None]
    SC[name] = {"S": S, "F": F, "EX": EX}
scope("ALL", "h50", False); scope("ALL_h0", "h0", False); scope("ALL_h100", "h100", False); scope("BQ", "raw", True)

def spearman(a, b):
    ra = pd.Series(a).rank().values; rb = pd.Series(b).rank().values
    return np.corrcoef(ra, rb)[0, 1]
def ic_dates(LV, EXn, S, lo, hi, resid=None):
    out = []
    for t in range(lo, hi + 1):
        if not QM[t]:
            continue
        m = S[t] & np.isfinite(LV[t]) & np.isfinite(EXn[t])
        if resid is not None:
            for Rm in resid:
                m &= np.isfinite(Rm[t])
        if m.sum() < 30:
            continue
        x = LV[t, m]
        if resid is not None:
            Xr = np.column_stack([np.ones(m.sum())] + [pd.Series(Rm[t, m]).rank().values for Rm in resid]); xr = pd.Series(x).rank().values
            x = xr - Xr @ np.linalg.lstsq(Xr, xr, rcond=None)[0]
        out.append((t, YR[t], spearman(x, EXn[t, m]), int(m.sum())))
    return out
def boot_year(icl, seed=SEED):
    if len(icl) == 0:
        return (np.nan, np.nan, np.nan, 0)
    d = pd.DataFrame(icl, columns=["t", "y", "ic", "n"]); ys = d.y.unique(); rng = np.random.RandomState(seed)
    by = {y: d[d.y == y].ic.values for y in ys}; res = np.empty(B_YEAR)
    for b in range(B_YEAR):
        pick = rng.choice(ys, len(ys), replace=True); res[b] = np.concatenate([by[y] for y in pick]).mean()
    return (float(d.ic.mean()), float(np.percentile(res, 2.5)), float(np.percentile(res, 97.5)), int(len(ys)))
def boot_ticker(LV, EXn, S, lo, hi, seed=SEED):
    rng = np.random.RandomState(seed); ts = [t for t in range(lo, hi + 1) if QM[t]]; res = []
    for b in range(B_TK):
        w = rng.multinomial(N, np.ones(N) / N); vals = []
        for t in ts:
            m = S[t] & np.isfinite(LV[t]) & np.isfinite(EXn[t]) & (w > 0)
            if m.sum() < 30:
                continue
            idx = np.repeat(np.where(m)[0], w[m]); vals.append(spearman(LV[t, idx], EXn[t, idx]))
        res.append(np.mean(vals) if vals else np.nan)
    return float(np.nanpercentile(res, 2.5)), float(np.nanpercentile(res, 97.5))

THR_C = np.log(1.25); THR_E = np.log(0.67)
def cheap_events(LV, S, lo, hi):
    ev = []
    for j in range(N):
        a = LV[:, j]; last = -99
        for t in range(lo, hi + 1):
            if not S[t, j] or not (a[t] >= THR_C) or t - last < 36:
                continue
            prev = a[max(0, t - 6):t]
            if np.any(prev >= THR_C):
                continue
            ev.append((t, j)); last = t
    return ev
def exp_events(LV, S, lo, hi):
    ev = []
    for j in range(N):
        a = LV[:, j]; last = -99; run = 0
        for t in range(max(0, lo - 6), hi + 1):
            run = run + 1 if (a[t] <= THR_E) else 0
            if t >= lo and S[t, j] and run >= 6 and t - last >= 36:
                ev.append((t, j)); last = t
    return ev
def cheap_outcome(LV, ev, EX36):
    hit = stat = fall = 0; mths = []; exs = []
    for t, j in ev:
        w = slice(t + 1, min(T, t + 37)); lv = LV[w, j]; lp = LP[w, j]; p0 = LP[t, j]
        touch = (lv <= 0) & (lp > p0)
        if touch.any():
            hit += 1; mths.append(int(np.argmax(touch)) + 1)
        elif (lv <= 0).any():
            fall += 1
        if np.nanmax(np.append(lp, -np.inf)) - p0 >= LV[t, j]:
            stat += 1
        exs.append(EX36[t, j])
    n = len(ev)
    return {"U_n": n, "U_hit": hit / n if n else np.nan, "U_static": stat / n if n else np.nan, "U_touch_by_fall": fall / n if n else np.nan,
            "U_mths_med": float(np.median(mths)) if mths else np.nan, "U_ex36_mean": float(np.nanmean(exs)) if n else np.nan,
            "U_ex36_pos": float(np.nanmean(np.array(exs)[np.isfinite(exs)] > 0)) if n and np.isfinite(exs).any() else np.nan}
def exp_outcome(ev, EX36, F36):
    ex = np.array([EX36[t, j] for t, j in ev]); f = np.array([F36[t, j] for t, j in ev]); pk = []; cool = []
    for t, j in ev:
        w = slice(t, min(T, t + 37)); lp = LP[w, j]
        if np.isfinite(lp).sum() == 0:
            continue
        pk.append(int(np.nanargmax(lp))); d = np.where(lp - LP[t, j] <= np.log(0.85))[0]; cool.append(int(d[0]) if len(d) else np.nan)
    n = len(ev); okx = np.isfinite(ex)
    return {"O_n": n, "O_right_rel": float((ex[okx] < 0).mean()) if okx.any() else np.nan, "O_right_abs": float((f[np.isfinite(f)] <= 0.10).mean()) if np.isfinite(f).any() else np.nan,
            "O_false": float((ex[okx] > 0.30).mean()) if okx.any() else np.nan, "O_ex36_mean": float(ex[okx].mean()) if okx.any() else np.nan,
            "O_lag_peak_med": float(np.median(pk)) if pk else np.nan, "O_lag_cool15_med": float(np.nanmedian(cool)) if len(cool) and np.isfinite(cool).any() else np.nan,
            "O_never_cool15": float(np.mean(np.isnan(cool))) if len(cool) else np.nan}

LVS = {m: dense(pan["lv_" + m].values) for m in MODELS}
EPd = dense(pan.ep.values); BPd = dense(np.log(pan.bp.where(pan.bp > 0)).values); SZd = dense(np.log(pan.mc.values))
rows = []; icy = []; base = {}
for sname, sc in SC.items():
    S = sc["S"]
    for era, (lo, hi) in ERA.items():
        m = S[lo:hi + 1]; ex = sc["EX"][36][lo:hi + 1]; ok = m & np.isfinite(ex)
        gain = (FMAXP - LP)[lo:hi + 1]
        base[f"{sname}|{era}"] = {"n": int(ok.sum()), "P_ex36_neg": float((ex[ok] < 0).mean()), "P_ex36_gt030": float((ex[ok] > 0.30).mean()),
                                  "P_max36_ge_125": float((gain[m & np.isfinite(gain)] >= THR_C).mean()),
                                  "P_f36_le_010": float((sc["F"][36][lo:hi + 1][ok] <= 0.10).mean())}
for mname in MODELS:
    LV = LVS[mname]; is_rank_only = mname in ("EP", "BP")
    FMAX = fwd_stat(LV, "max"); FMIN = fwd_stat(LV, "min")
    for sname, sc in SC.items():
        if sname in ("ALL_h0", "ALL_h100") and is_rank_only is False and mname not in ("D0", "D0B", "ENS1", "ENS2", "MULT", "HEDf", "N0", "L2_ENS2", "L2_D0B", "A_pit", "META", "ENS1w"):
            continue
        S = sc["S"]
        for era, (lo, hi) in ERA.items():
            r = {"model": mname, "scope": sname, "era": era}
            m = S[lo:hi + 1] & np.isfinite(LV[lo:hi + 1]); r["n_rows"] = int(m.sum()); r["coverage"] = float(m.sum() / max(S[lo:hi + 1].sum(), 1))
            for n in (12, 24, 36):
                icl = ic_dates(LV, sc["EX"][n], S, lo, hi); mu, l, h, ny = boot_year(icl)
                r[f"ic{n}"] = mu; r[f"ic{n}_lo"] = l; r[f"ic{n}_hi"] = h; r["n_years"] = ny; r[f"ic{n}_ndates"] = len(icl)
                if n == 36 and sname in ("ALL", "BQ"):
                    for (t, y, v, nn) in icl:
                        icy.append({"model": mname, "scope": sname, "t": t, "year": y, "ic36": v, "n": nn})
            icr = ic_dates(LV, sc["EX"][36], S, lo, hi, resid=[EPd, BPd, SZd]); r["ic36_resid"], r["ic36_resid_lo"], r["ic36_resid_hi"], _ = boot_year(icr)
            if sname == "ALL" and mname in ("D0", "D0B", "ENS1", "ENS2", "MULT", "HEDf", "EP", "ENS1w", "META", "A_pit", "A_RI"):
                r["ic36_tk_lo"], r["ic36_tk_hi"] = boot_ticker(LV, sc["EX"][36], S, lo, hi)
            if not is_rank_only:
                a = LV[lo:hi + 1]; exp_ = m & (a < 0); chp = m & (a > 0)
                crs = (exp_ & (FMAX[lo:hi + 1] > 0)) | (chp & (FMIN[lo:hi + 1] < 0))
                r["cross36"] = float(crs[m].mean()) if m.any() else np.nan
                r["cross36_exp"] = float(crs[exp_].mean()) if exp_.any() else np.nan; r["cross36_cheap"] = float(crs[chp].mean()) if chp.any() else np.nan
                r["share_exp"] = float(exp_.sum() / max(m.sum(), 1)); r["iqr"] = float(np.subtract(*np.nanpercentile(a[m], [75, 25]))) if m.any() else np.nan
                ev = cheap_events(LV, S, lo, hi); r.update(cheap_outcome(LV, ev, sc["EX"][36]))
                ev2 = exp_events(LV, S, lo, hi); r.update(exp_outcome(ev2, sc["EX"][36], sc["F"][36]))
            rows.append(r)
    print(mname, "done", flush=True)
met = pd.DataFrame(rows); met.to_csv(os.path.join(OUT, f"metrics2{SFX}.csv"), index=False)
pd.DataFrame(icy).to_csv(os.path.join(OUT, f"ic_year2{SFX}.csv"), index=False)
json.dump(base, open(os.path.join(OUT, f"base2{SFX}.json"), "w"), indent=1)
if ONLY:
    sys.exit(0)
# ---------- độ tin cậy ENS2: tercile SD giữa các phương pháp ----------
SD = dense(pan.sd_ENS2.values); LV = LVS["ENS2"]; conf = []
for era, (lo, hi) in ERA.items():
    S = SC["ALL"]["S"]; EX = SC["ALL"]["EX"][36]
    q = np.full((T, N), np.nan)
    for t in range(lo, hi + 1):
        m = S[t] & np.isfinite(SD[t]) & np.isfinite(LV[t])
        if m.sum() >= 30:
            q[t, m] = pd.qcut(pd.Series(SD[t, m]).rank(method="first"), 3, labels=False).values
    for k, lab in ((0, "SD thấp"), (2, "SD cao")):
        LVk = np.where(q == k, LV, np.nan); icl = ic_dates(LVk, EX, S, lo, hi)
        ev = [(t, j) for (t, j) in cheap_events(LV, S, lo, hi) if q[t, j] == k]; co = cheap_outcome(LV, ev, EX)
        conf.append({"era": era, "tercile": lab, "ic36": float(np.mean([x[2] for x in icl])) if icl else np.nan, "U_n": co["U_n"], "U_hit": co["U_hit"], "U_static": co["U_static"]})
pd.DataFrame(conf).to_csv(os.path.join(OUT, "confidence2.csv"), index=False)
# ---------- ablation FCFE → RI trên CÙNG mẫu ----------
abl = {}
for era, (lo, hi) in ERA.items():
    S = SC["ALL"]["S"]; EX = SC["ALL"]["EX"][36]
    common = np.isfinite(LVS["A_pit"]) & np.isfinite(LVS["A_RI"]) & np.isfinite(LVS["D0"])
    d = {}
    for nm, M in (("A_pit", LVS["A_pit"]), ("A_RI", LVS["A_RI"]), ("D0", LVS["D0"]), ("FCFE_minus_RI", LVS["A_pit"] - LVS["A_RI"]), ("RIbase_minus_D0", LVS["A_RI"] - LVS["D0"])):
        Mx = np.where(common, M, np.nan); icl = ic_dates(Mx, EX, S, lo, hi); mu, l, h, _ = boot_year(icl)
        blk = Mx[lo:hi + 1][S[lo:hi + 1] & np.isfinite(Mx[lo:hi + 1])]
        d[nm] = {"ic36": mu, "lo": l, "hi": h, "var": float(np.var(blk)), "n": int(len(blk))}
    a = LVS["A_pit"][lo:hi + 1]; b = LVS["A_RI"][lo:hi + 1]; mk = S[lo:hi + 1] & common[lo:hi + 1]
    d["corr_A_pit_A_RI"] = float(np.corrcoef(a[mk], b[mk])[0, 1]); d["corr_A_RI_D0"] = float(np.corrcoef(b[mk], LVS["D0"][lo:hi + 1][mk])[0, 1])
    abl[era] = d
json.dump(abl, open(os.path.join(OUT, "ablation2.json"), "w"), indent=1)
# ---------- 5 ca ----------
def path(tk, mname):
    j = tid.get(tk)
    return None if j is None else LVS[mname][:, j]
def case_rows(mname):
    out = []
    def share(tk, a, b, sign):
        lv = path(tk, mname)
        if lv is None:
            return np.nan, 0
        w = lv[mi_of(a):mi_of(b) + 1]; w = w[np.isfinite(w)]
        return (float((w > 0).mean() if sign > 0 else (w < 0).mean()), len(w)) if len(w) >= 3 else (np.nan, len(w))
    for nm, tk, a, b, sg in (("VCS2015", "VCS", "2015-01", "2015-12", 1), ("DGC2016", "DGC", "2016-01", "2016-12", 1), ("VNM2011", "VNM", "2011-01", "2011-12", 1),
                             ("VNM2015-16_dat", "VNM", "2015-07", "2016-12", -1)):
        s, n = share(tk, a, b, sg); res = "NA" if not np.isfinite(s) else ("ĐẠT" if s >= 0.5 else "TRƯỢT")
        extra = ""
        lv = path(tk, mname); j = tid[tk]
        if sg > 0 and lv is not None:
            w = np.where(lv[mi_of(a):mi_of(b) + 1] >= THR_C)[0]
            if len(w):
                t = mi_of(a) + int(w[0]); co = cheap_outcome(LVS[mname], [(t, j)], SC["ALL"]["EX"][36])
                extra = f"rẻ≥25% từ {pd.Period(ordinal=0, freq='M') + (m0 + t - 1970 * 12 - 1)}: U-hit={int(co['U_hit'])}, tháng chạm={co['U_mths_med']}, U-static={int(co['U_static'])}"
        if sg < 0 and lv is not None:
            t = mi_of(b); w = slice(mi_of(a), min(T, mi_of(a) + 37)); lp = LP[w, j]
            extra = f"tháng tới đỉnh từ 2015-07={int(np.nanargmax(lp))}; logP(+36T)={lp[min(36, len(lp) - 1)] - lp[0]:.2f}; V/P 2015-12={np.exp(lv[mi_of('2015-12')]):.2f}"
        out.append({"model": mname, "case": nm, "share": s, "n_obs": n, "result": res, "note": extra})
    lv = path("HPG", mname); j = tid["HPG"]; V = lv + LP[:, j]
    need = [mi_of(x) for x in ("2018-12", "2019-12", "2019-06", "2020-06")]
    if not all(np.isfinite(V[k]) for k in need):
        out.append({"model": mname, "case": "HPG2019", "share": np.nan, "n_obs": 0, "result": "NA", "note": ""})
    else:
        c1 = V[need[1]] > V[need[0]]; c2 = V[need[3]] > V[need[2]]; c3 = bool(np.nanmax(lv[mi_of("2019-01"):mi_of("2019-12") + 1]) > 0)
        out.append({"model": mname, "case": "HPG2019", "share": np.nan, "n_obs": 4, "result": "ĐẠT" if (c1 and c2 and c3) else "TRƯỢT",
                    "note": f"V 12/18→12/19: {np.exp(V[need[0]]):.0f}→{np.exp(V[need[1]]):.0f}; V 06/19→06/20: {np.exp(V[need[2]]):.0f}→{np.exp(V[need[3]]):.0f}; có tháng 2019 V>P: {c3}"})
    return out
cs = pd.DataFrame([r for mname in MODELS if mname not in ("EP", "BP") for r in case_rows(mname)])
cs.to_csv(os.path.join(OUT, "cases2.csv"), index=False)
sc_ = cs.groupby("model").result.agg(lambda s: f"{(s == 'ĐẠT').sum()}/{(s != 'NA').sum()}")
jh = tid["HPG"]; eh = dense(pan.E.values)[:, jh]
print("HPG vốn chủ 12/2018→12/2019:", eh[mi_of("2018-12")] / 1e12, eh[mi_of("2019-12")] / 1e12)
print(sc_.to_string())
# ---------- mẫu ngẫu nhiên 24 mã + ca thất bại ép ----------
ever = sorted(pan[pan.in_universe & (pan.ym >= "2014-01")].ticker.unique()); rng = np.random.RandomState(SEED)
samp = list(rng.choice(ever, 24, replace=False)); forced = ["FLC", "ROS", "HVG", "KSA", "AMD", "HAI", "ART", "GTN", "TGG", "TTF", "HNG", "OGC", "ITA", "HBC", "PVX", "DLG", "HAG", "QBS", "POM"]
srow = []
for tk in samp + forced:
    if tk not in tid:
        srow.append({"ticker": tk, "group": "ép" if tk in forced else "ngẫu nhiên", "note": "không có dữ liệu"}); continue
    j = tid[tk]; s = SC["ALL"]["S"][:, j] & (np.arange(T) >= T_IS0); r = {"ticker": tk, "group": "ép" if tk in forced else "ngẫu nhiên", "src": pan[pan.ticker == tk].src.iloc[0],
         "months_in_uni": int(s.sum()), "last_ym": pan[pan.ticker == tk].last_ym.iloc[0]}
    lp = LP[:, j]; idx = np.where(s)[0]
    if len(idx):
        r["P_end/P_start"] = float(np.exp(lp[np.where(np.isfinite(lp))[0][-1]] - lp[idx[0]]))
    for mname in ("D0B", "ENS2", "MULT", "L2_ENS2"):
        a = LVS[mname][s, j]; a = a[np.isfinite(a)]
        r[f"{mname}_medVP"] = float(np.exp(np.median(a))) if len(a) else np.nan; r[f"{mname}_%đắt"] = float((a < 0).mean()) if len(a) else np.nan
        r[f"{mname}_%cảnh_báo"] = float((a <= THR_E).mean()) if len(a) else np.nan
    srow.append(r)
pd.DataFrame(srow).to_csv(os.path.join(OUT, "sample2.csv"), index=False)
print("base", json.dumps(base["ALL|IS"]), json.dumps(base["ALL|OOS"]))
