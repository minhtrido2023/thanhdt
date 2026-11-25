# -*- coding: utf-8 -*-
"""h_null_ep.py — [V3 B-1 + NB-5] ĐỘC LẬP với d_metrics2 (tự dựng ma trận + sự kiện bằng numpy/pandas riêng).
(1) Cảnh báo đắt: ENS1w, D0 so với null "cờ theo E/P cùng tỉ lệ cờ mỗi tháng" (EPN) — cùng luật 6 tháng liên tiếp + re-arm 36 tháng — và
    các tổ hợp: WBOTH (ENS1w VÀ E/P cùng cờ trong tháng), WONLY (ENS1w cờ, E/P không), EONLY (E/P cờ, ENS1w không). CHỈ BÁO CÁO, không dùng chọn.
    Tái lập đối chiếu: số ENS1w/D0 phải KHỚP metrics2.csv (assert) ⇒ cùng phép đo, khác đường code.
    CI hiệu ENS1w − EPN: bootstrap theo NĂM của sự kiện (B = 2000, seed 20261124).
(2) NB-5: nền U-static công bằng hơn — thay vì ngưỡng cố định "tăng ≥ 25%" áp cho mọi dòng, so U-static của sự kiện rẻ với xác suất vô điều kiện
    P(max 36T ≥ x_i) tại CHÍNH mức x_i = log(V/P) mà sự kiện i cần (trung bình theo sự kiện).
Out: ../out/null_ep.csv, null_ep.json."""
import os, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "..", "out"); SEED = 20261124
vp = pd.read_parquet(os.path.join(OUT, "vp2.parquet"), columns=["ticker", "mi", "ym", "in_universe", "Close", "fwd36_h50", "lv_ENS1w", "lv_D0", "lv_N0", "lv_ENS2", "lv_EPN", "lv_WBOTH", "lv_WONLY", "lv_EONLY", "lv_EPN_E2", "lv_WBOTH_E2", "lv_WONLY_E2", "lv_EONLY_E2"])
m0, m1 = int(vp.mi.min()), int(vp.mi.max()); T = m1 - m0 + 1
def grid(col, fill=np.nan):
    return vp.pivot(index="mi", columns="ticker", values=col).reindex(range(m0, m1 + 1)).values
IU = vp.pivot(index="mi", columns="ticker", values="in_universe").reindex(range(m0, m1 + 1)).fillna(False).astype(bool).values
LP = np.log(grid("Close")); F36 = grid("fwd36_h50")
# lợi suất vượt trội 36T so trung bình số học của universe cùng tháng (đúng định nghĩa d_metrics2 scope ALL)
with np.errstate(all="ignore"):
    BM = np.log(np.nanmean(np.where(IU, np.exp(F36), np.nan), axis=1))
EX = F36 - BM[:, None]
def mi_of(ym):
    y, m = int(ym[:4]), int(ym[5:]); return y * 12 + m - m0
ERA = {"IS": (mi_of("2014-01"), mi_of("2019-12")), "OOS": (mi_of("2020-01"), mi_of("2023-10"))}
THR_E = np.log(0.67); THR_C = np.log(1.25)
def exp_events(LV, lo, hi):
    ev = []
    for j in range(LV.shape[1]):
        last, run = -99, 0
        for t in range(max(0, lo - 6), hi + 1):
            run = run + 1 if LV[t, j] <= THR_E else 0
            if t >= lo and IU[t, j] and run >= 6 and t - last >= 36:
                ev.append((t, j)); last = t
    return ev
def outcome(ev):
    ex = np.array([EX[t, j] for t, j in ev]); f = np.array([F36[t, j] for t, j in ev]); yr = np.array([(m0 + t - 1) // 12 for t, j in ev])
    ok = np.isfinite(ex); okf = np.isfinite(f)
    return ({"n": len(ev), "n_ok": int(ok.sum()), "right_rel": float((ex[ok] < 0).mean()), "right_abs": float((f[okf] <= 0.10).mean()), "false": float((ex[ok] > 0.30).mean()),
             "ex_mean": float(ex[ok].mean())}, ex, yr, ok)
rows = []; EV = {}
LVS = {"ENS1w": grid("lv_ENS1w"), "D0": grid("lv_D0"), "ENS2": grid("lv_ENS2"), **{k: grid("lv_" + k) for k in ("EPN", "WBOTH", "WONLY", "EONLY", "EPN_E2", "WBOTH_E2", "WONLY_E2", "EONLY_E2")}}
base = {}
for era, (lo, hi) in ERA.items():
    m = IU[lo:hi + 1] & np.isfinite(EX[lo:hi + 1]); ex = EX[lo:hi + 1][m]; f = F36[lo:hi + 1][m]
    base[era] = {"right_rel": float((ex < 0).mean()), "false": float((ex > 0.30).mean()), "right_abs": float((f <= 0.10).mean()), "n": int(m.sum())}
    for nm, LV in LVS.items():
        ev = exp_events(LV, lo, hi); EV[(nm, era)] = ev; o, ex_, yr_, ok_ = outcome(ev); rows.append({"model": nm, "era": era, **o})
        EV[(nm, era, "arr")] = (ex_, yr_, ok_)
res = pd.DataFrame(rows)
# đối chiếu với d_metrics2 (metrics2.csv)
met = pd.read_csv(os.path.join(OUT, "metrics2.csv")); met = met[met.scope == "ALL"].set_index(["model", "era"])
chk = {}
for nm in ("ENS1w", "D0", "ENS2"):
    for era in ERA:
        r = res[(res.model == nm) & (res.era == era)].iloc[0]; q = met.loc[(nm, era)]
        chk[f"{nm}|{era}"] = {"n": [int(r.n), int(q.O_n)], "right_rel": [r.right_rel, q.O_right_rel], "false": [r["false"], q.O_false],
                              "ok": bool(int(r.n) == int(q.O_n) and abs(r.right_rel - q.O_right_rel) < 1e-9 and abs(r["false"] - q.O_false) < 1e-9 and abs(r.right_abs - q.O_right_abs) < 1e-9)}
assert all(v["ok"] for v in chk.values()), chk
# CI hiệu ENS1w − EPN (bootstrap theo năm sự kiện)
def boot_diff(a, b, B=2000):
    rng = np.random.RandomState(SEED); out = {}
    for key, fn in (("right_rel", lambda e: (e < 0)), ("false", lambda e: (e > 0.30))):
        (ea, ya, oka), (eb, yb, okb) = a, b
        ea, ya, eb, yb = ea[oka], ya[oka], eb[okb], yb[okb]; ys = np.union1d(np.unique(ya), np.unique(yb)); d = []
        pa = {y: fn(ea[ya == y]) for y in ys}; pb = {y: fn(eb[yb == y]) for y in ys}
        for _ in range(B):
            pick = rng.choice(ys, len(ys), replace=True); xa = np.concatenate([pa[y] for y in pick]); xb = np.concatenate([pb[y] for y in pick])
            if len(xa) and len(xb):
                d.append(xa.mean() - xb.mean())
        pt = fn(ea).mean() - fn(eb).mean(); out[key] = [float(pt), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]
    return out
diff = {era: boot_diff(EV[("ENS1w", era, "arr")], EV[("EPN", era, "arr")]) for era in ERA}
diffD = {era: boot_diff(EV[("D0", era, "arr")], EV[("EPN", era, "arr")]) for era in ERA}
diffE2 = {era: boot_diff(EV[("ENS2", era, "arr")], EV[("EPN_E2", era, "arr")]) for era in ERA}
# trùng sự kiện: tỉ lệ sự kiện ENS1w có E/P cũng cờ ở CÙNG tháng đó
ov = {}
for nm, en in (("ENS1w", "EPN"), ("ENS2", "EPN_E2")):
    for era in ERA:
        ev = EV[(nm, era)]; both = np.mean([LVS[en][t, j] <= THR_E for t, j in ev]); ov[f"{nm}|{era}"] = {"events": len(ev), "share_EP_flag_same_month": float(both)}
# NB-5: nền U-static khớp ngưỡng
def cheap_events(LV, lo, hi):
    ev = []
    for j in range(LV.shape[1]):
        a = LV[:, j]; last = -99
        for t in range(lo, hi + 1):
            if not IU[t, j] or not (a[t] >= THR_C) or t - last < 36:
                continue
            if np.any(a[max(0, t - 6):t] >= THR_C):
                continue
            ev.append((t, j)); last = t
    return ev
FMAX = np.full_like(LP, np.nan)
d_ = pd.DataFrame(LP)[::-1]; FMAX = d_.rolling(36, min_periods=1).max()[::-1].shift(-1).values
GAIN = FMAX - LP; us = {}
for nm in ("ENS1w", "ENS2", "D0", "N0"):
    LV = grid("lv_" + nm)
    for era, (lo, hi) in ERA.items():
        ev = cheap_events(LV, lo, hi); x = np.array([LV[t, j] for t, j in ev]); st = np.array([np.nanmax(np.append(LP[t + 1:min(T, t + 37), j], -np.inf)) - LP[t, j] >= LV[t, j] for t, j in ev])
        G = GAIN[lo:hi + 1][IU[lo:hi + 1] & np.isfinite(GAIN[lo:hi + 1])]
        Gs = np.sort(G); p_i = 1.0 - np.searchsorted(Gs, x, side="left") / len(Gs)
        us[f"{nm}|{era}"] = {"n": len(ev), "U_static": float(st.mean()), "baseline_fixed_125": float((G >= THR_C).mean()), "baseline_matched_mean": float(p_i.mean()),
                             "median_required_gain_x": float(np.median(np.exp(x)) - 1), "gap_vs_fixed_pp": float(100 * (st.mean() - (G >= THR_C).mean())),
                             "gap_vs_matched_pp": float(100 * (st.mean() - p_i.mean()))}
res.to_csv(os.path.join(OUT, "null_ep.csv"), index=False)
json.dump({"baseline_uncond": base, "crosscheck_vs_metrics2": chk, "diff_ENS1w_minus_EPN_[pt,lo,hi]": diff, "diff_D0_minus_EPN_[pt,lo,hi]": diffD, "diff_ENS2_minus_EPN_E2_[pt,lo,hi]": diffE2, "overlap": ov, "ustatic_matched_baseline": us},
          open(os.path.join(OUT, "null_ep.json"), "w"), indent=1, ensure_ascii=False)
print(res.round(4).to_string()); print(json.dumps({"base": base, "diff": diff, "diffD": diffD, "diffE2": diffE2, "overlap": ov, "ustatic": us}, ensure_ascii=False, indent=1))
