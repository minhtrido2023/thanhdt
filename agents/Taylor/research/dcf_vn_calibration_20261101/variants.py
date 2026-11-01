# -*- coding: utf-8 -*-
"""FV theo biến thể ⇒ level (median P/FV, %RẺ), IC MoS 3/12T IS/OOS, LOYO g_T, DSR. PREREG §4(iii), §5(b)(d)."""
import os
import numpy as np
import pandas as pd
from scipy.stats import norm
from common import DATA, OUT, month_close, add_fwd, ic_by_date, ic_summary
import engine as E

P = print
pd.set_option("display.width", 250)
p = pd.read_parquet(os.path.join(DATA, "panel_monthly.parquet"))
mc, me = month_close()
p = add_fwd(p, mc, me)
m, base = E.base_valid(p)
p = p[m & p.Price.notna() & (p.Price > 0)].copy()
base = base[p.index]
p["base"] = base.values
# beta PIT: quý gần nhất T ≤ t
B = pd.read_parquet(os.path.join(DATA, "beta_panel.parquet"))
bb = B[(B.freq == "d") & (B.win == 1) & (B.bench == "VNINDEX")][["T", "ticker", "blume"]].dropna()
bb = bb.sort_values("T")
p = pd.merge_asof(p.sort_values("t"), bb.rename(columns={"blume": "beta_b1"}), left_on="t", right_on="T",
                  by="ticker", direction="backward")
p.loc[(p.t - p["T"]).dt.days > 120, "beta_b1"] = np.nan
p["beta_rel"] = p.beta_b1 / p.groupby("t").beta_b1.transform("median")
RF, ERP = 6.75, 5.5
G_FLOOR, G_CAP = -0.02, 0.20


def fv(p, s=0.5, N=5, gT_cap=0.055, r=None, kind="2s", n1=None, n2=None, h=None):
    gT = np.minimum(p.g_T.values * 0 + np.minimum(p.g_T_raw.values, gT_cap), gT_cap)
    rr = np.full(len(p), (RF + ERP) / 100) if r is None else r
    gT = np.where(rr <= gT, rr - 0.01, gT)                          # Gordon guard như production
    graw = np.where(np.isnan(p.g_raw.values), gT, p.g_raw.values)
    gc = np.clip(graw, G_FLOOR, G_CAP)
    ge = gT + s * (gc - gT)
    if kind == "2s":
        path = np.repeat(ge[:, None], N, axis=1)
    elif kind == "3s":
        N = n1 + n2
        path = np.zeros((len(p), N))
        for y in range(N):
            path[:, y] = ge if y < n1 else ge + (y - n1 + 1) / (n2 + 1) * (gT - ge)
    elif kind == "H":
        N = 10
        path = np.column_stack([gT + (ge - gT) * 0.5 ** (y / h) for y in range(N)])
    return E.fv_path(p.base.values, path, gT, rr, p.OShares.values)


# g_T thô (trước cap 5,5%) = cpi + GDP; panel lưu g_T đã cap ⇒ tính lại
import gdp_growth_vn as _gdp  # noqa: E402
gt_raw = {}
for t in p.t.unique():
    cpi = E.D.terminal_growth(t)
    gt_raw[t] = cpi + _gdp.longrun_real_gdp(t)
p["g_T_raw"] = p.t.map(gt_raw)
P("g_T thô (CPI5Y+GDP15Y) min/median/max:", round(min(gt_raw.values()), 4), round(np.median(list(gt_raw.values())), 4),
  round(max(gt_raw.values()), 4), "⇒ cap 5,5% chạm ở", f"{np.mean([v > 0.055 for v in gt_raw.values()]):.0%}", "tháng")

lo_b, hi_b = 0.05, 2.37        # p5/p95 beta thật OOS (out/run_beta_eval.txt) — luật PREREG
V = {}
V["V0 hiện tại (s.5 N5 gT5.5 r hằng)"] = fv(p)
_chk, _ = E.current_fv(p.reset_index(drop=True))
_d = np.nanmax(np.abs(_chk - V["V0 hiện tại (s.5 N5 gT5.5 r hằng)"]) / _chk)
P("selfcheck V0 == engine.current_fv (== dcf_valuation.fair_value): max lệch tương đối =", _d)
assert _d < 1e-9
for s in (0, 0.25, 0.75, 1.0):
    V[f"G s={s}"] = fv(p, s=s)
for N in (3, 7, 10):
    V[f"G N={N}"] = fv(p, N=N)
V["G 3-stage s.5 N3+fade5"] = fv(p, kind="3s", n1=3, n2=5)
V["G H-model s.5 h2"] = fv(p, kind="H", h=2)
for g in (0.045, 0.05, 0.06, 0.07):
    V[f"T gT={g}"] = fv(p, gT_cap=g)
rb = (RF + np.clip(p.beta_b1.fillna(1.0).values, lo_b, hi_b) * ERP) / 100
V["B beta Blume1Y ngày, kẹp p5-p95"] = fv(p, r=rb)
rb2 = (RF + np.clip(p.beta_b1.fillna(1.0).values, 0.6, 1.6) * ERP) / 100
V["B beta Blume1Y ngày, kẹp 0.6-1.6"] = fv(p, r=rb2)
rb3 = (RF + np.clip(p.beta_rel.fillna(1.0).values, 0.6, 1.6) * ERP) / 100
V["B beta tương đối (β/median) kẹp 0.6-1.6"] = fv(p, r=rb3)
V["S s=0 + gT5.5"] = V["G s=0"]
for g in (0.045, 0.05, 0.06):
    V[f"S s=0 + gT={g}"] = fv(p, s=0, gT_cap=g)
V["S s=0 + beta tương đối 0.6-1.6"] = fv(p, s=0, r=rb3)
V["S s=0.25 + gT5.5"] = V["G s=0.25"]

rows, ics = [], {}
p["yr"] = p.t.dt.year
for name, f in V.items():
    q = p[["t", "yr", "ticker", "Price", "fwd3", "fwd12"]].copy()
    q["fv"] = f
    q = q[np.isfinite(q.fv) & (q.fv > 0)]
    q["mos"] = (q.fv - q.Price) / q.fv
    q["lpfv"] = np.log(q.Price / q.fv)
    lv = q.groupby("t").agg(med_lpfv=("lpfv", "median"), cheap=("mos", lambda s: (s > 0).mean()), n=("mos", "size"))
    lvy = lv.groupby(lv.index.year).med_lpfv.mean()
    i3 = ic_by_date(q, "mos", "fwd3")
    i12 = ic_by_date(q, "mos", "fwd12")
    s3 = ic_summary(i3, 3)
    s12 = ic_summary(i12, 12)
    ics[name] = (i3, i12)
    last = q[q.t == q.t.max()]
    rows.append({"variant": name, "medPFV_all": float(np.exp(lv.med_lpfv.mean())),
                 "medPFV_IS": float(np.exp(lv.med_lpfv[lv.index.year <= 2019].mean())),
                 "medPFV_OOS": float(np.exp(lv.med_lpfv[lv.index.year >= 2020].mean())),
                 "medPFV_yr_min": float(np.exp(lvy.min())), "medPFV_yr_max": float(np.exp(lvy.max())),
                 "pct_cheap_all": lv.cheap.mean(), "pct_cheap_2026-10": float((last.mos > 0).mean()),
                 "medFV_vs_V0_2026-10": np.nan,
                 "ic3": s3.get("ic"), "ic3_IS": s3.get("ic_is"), "ic3_OOS": s3.get("ic_oos"), "ic3_t": s3.get("t_nw"),
                 "ic12": s12.get("ic"), "ic12_IS": s12.get("ic_is"), "ic12_OOS": s12.get("ic_oos"),
                 "ic12_lo": s12.get("ci_lo"), "ic12_hi": s12.get("ci_hi"), "ic12_t": s12.get("t_nw"),
                 "n_obs": len(q)})
R = pd.DataFrame(rows)
v0 = pd.Series(V["V0 hiện tại (s.5 N5 gT5.5 r hằng)"], index=p.index)
lastm = p.t == p.t.max()
for i, name in enumerate(V):
    f = pd.Series(V[name], index=p.index)
    j = lastm & np.isfinite(f) & np.isfinite(v0)
    R.loc[i, "medFV_vs_V0_2026-10"] = float(np.median(f[j] / v0[j]) - 1)
# ΔIC so với V0, ghép cặp theo ngày + bootstrap khối năm
base3, base12 = ics["V0 hiện tại (s.5 N5 gT5.5 r hằng)"]
rng = np.random.default_rng(11)
for i, name in enumerate(V):
    for h, (a, b0) in ((3, (ics[name][0], base3)), (12, (ics[name][1], base12))):
        d = a.merge(b0, on="t", suffixes=("", "_0"))
        d["dd"] = d.ic - d.ic_0
        yrs = d.t.dt.year.unique()
        bs = [np.mean(np.concatenate([d.dd[d.t.dt.year == y].values for y in rng.choice(yrs, len(yrs))])) for _ in range(1000)]
        R.loc[i, f"dIC{h}"] = d.dd.mean()
        R.loc[i, f"dIC{h}_OOS"] = d.dd[d.t.dt.year >= 2020].mean()
        R.loc[i, f"dIC{h}_IS"] = d.dd[d.t.dt.year <= 2019].mean()
        R.loc[i, f"dIC{h}_lo"] = np.percentile(bs, 2.5)
        R.loc[i, f"dIC{h}_hi"] = np.percentile(bs, 97.5)
R.to_csv(os.path.join(OUT, "t_variants_summary.csv"), index=False)
P(f"=== Biến thể: level + IC (N trials IC = {len(V)}); medPFV = trung vị Price/FV (TB log theo tháng)")
cols = ["variant", "medPFV_all", "medPFV_IS", "medPFV_OOS", "medPFV_yr_min", "medPFV_yr_max", "pct_cheap_all",
        "pct_cheap_2026-10", "medFV_vs_V0_2026-10"]
P(R[cols].round(3).to_string(index=False))
cols = ["variant", "ic3", "ic3_IS", "ic3_OOS", "ic12", "ic12_IS", "ic12_OOS", "ic12_lo", "ic12_hi", "ic12_t",
        "dIC12", "dIC12_IS", "dIC12_OOS", "dIC12_lo", "dIC12_hi", "dIC3_OOS"]
P(R[cols].round(4).to_string(index=False))

# DSR trên chuỗi IC 12T (non-overlap: lấy tháng 12 mỗi năm) — Bailey & López de Prado
def dsr(sr_series_list, chosen):
    srs = []
    for name, (a, b) in ics.items():
        x = b.set_index("t").ic
        x = x[x.index.month == 12]
        srs.append(x.mean() / x.std(ddof=1))
    x = ics[chosen][1].set_index("t").ic
    x = x[x.index.month == 12]
    T = len(x)
    sr = x.mean() / x.std(ddof=1)
    var_sr = np.var(srs, ddof=1)
    Nn = len(srs)
    emc = 0.5772156649
    sr0 = np.sqrt(var_sr) * ((1 - emc) * norm.ppf(1 - 1 / Nn) + emc * norm.ppf(1 - 1 / (Nn * np.e)))
    from scipy.stats import skew, kurtosis
    sk, ku = skew(x), kurtosis(x, fisher=False)
    z = (sr - sr0) * np.sqrt(T - 1) / np.sqrt(1 - sk * sr + (ku - 1) / 4 * sr ** 2)
    return sr, sr0, T, norm.cdf(z)


for name in ("V0 hiện tại (s.5 N5 gT5.5 r hằng)", "G s=0", "G s=0.25", "B beta tương đối (β/median) kẹp 0.6-1.6",
             "S s=0 + beta tương đối 0.6-1.6"):
    sr, sr0, T, d = dsr(None, name)
    P(f"DSR {name}: SR(IC12, tháng 12 mỗi năm)={sr:.3f} SR0={sr0:.3f} T={T} DSR={d:.3f}")

# LOYO: chọn gT (lưới mịn) để TB log median P/FV = 0 trên các năm còn lại, cho từng cấu trúc
grid = np.round(np.arange(0.03, 0.0801, 0.0025), 4)
for label, s in (("s=0.5 (hiện tại)", 0.5), ("s=0", 0.0), ("s=0.25", 0.25)):
    lv = {}
    for g in grid:
        f = fv(p, s=s, gT_cap=g)
        q = pd.DataFrame({"t": p.t.values, "l": np.log(p.Price.values / f)})
        q = q[np.isfinite(q.l)]
        lv[g] = q.groupby("t").l.median()
    L = pd.DataFrame(lv)
    Ly = L.groupby(L.index.year).mean()
    full = Ly.mean().abs().idxmin()
    loyo = {y: Ly.drop(y).mean().abs().idxmin() for y in Ly.index}
    oos_only = Ly[Ly.index >= 2020].mean().abs().idxmin()
    is_only = Ly[Ly.index <= 2019].mean().abs().idxmin()
    P(f"LOYO g_T [{label}]: toàn kỳ={full}  IS-only={is_only}  OOS-only={oos_only}  LOYO min/max={min(loyo.values())}/{max(loyo.values())}"
      f"  | log medPFV theo năm @5,5%: " + ", ".join(f"{y}:{v:+.2f}" for y, v in Ly[0.055].items()))
p_out = p[["t", "ticker", "Price", "base", "OShares", "g_raw", "g_T", "beta_b1", "beta_rel"]].copy()
for k in ("V0 hiện tại (s.5 N5 gT5.5 r hằng)", "G s=0", "S s=0 + beta tương đối 0.6-1.6", "B beta tương đối (β/median) kẹp 0.6-1.6"):
    p_out[k] = V[k]
p_out.to_parquet(os.path.join(DATA, "fv_variants.parquet"))
