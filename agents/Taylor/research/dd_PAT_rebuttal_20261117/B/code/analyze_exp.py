#!/usr/bin/env python3
"""B — kiểm khẳng định "cổ tức ổn định vượt lãi gửi thì không bị giảm sâu" + spread r* ngầm.

Theo PREREG.md (md5 trong PREREG.md5). Đọc data/*_exp.parquet (fetch_exp.py), ghi out/*_exp.*.
Chạy: /home/trido/thanhdt/wc_venv/bin/python code/analyze_exp.py
"""
import json
import os
import sys

import db_dtypes  # noqa: F401  (đọc cột dbdate)
import numpy as np
import pandas as pd

ROOT_WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, ROOT_WC)
from deposit_rate_vn import deposit_events_df  # noqa: E402

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, OUT = os.path.join(B, "data"), os.path.join(B, "out")
os.makedirs(OUT, exist_ok=True)
SBV_CSV = os.path.join(ROOT_WC, "mike/agents/Taylor/research/idle_cash_proxy_20260927/"
                       "fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv")
MODEL_SPREAD = 0.061
SEED, NBOOT = 20261117, 5000
ICB1 = {"0": "Dầu khí", "1": "Nguyên vật liệu", "2": "Công nghiệp", "3": "Hàng tiêu dùng", "4": "Y tế",
        "5": "Dịch vụ tiêu dùng", "6": "Viễn thông", "7": "Tiện ích", "8": "Tài chính", "9": "Công nghệ"}
ICB2 = {"83": "Ngân hàng", "85": "Bảo hiểm", "86": "Bất động sản", "87": "DV tài chính"}

# ---------------------------------------------------------------- dữ liệu
panel = pd.read_parquet(os.path.join(DATA, "panel_exp.parquet"))
ev = pd.read_parquet(os.path.join(DATA, "events_exp.parquet"))
assert not (panel.ticker == "PAT").any() and not (ev.ticker == "PAT").any()
for c in ["D", "last_dt", "min_dt"]:
    panel[c] = pd.to_datetime(panel[c].astype(str), errors="coerce")
ev["exright_date"] = pd.to_datetime(ev["exright_date"].astype(str))

div = (ev[ev.event_code == "DIV"]
       .drop_duplicates(["ticker", "exright_date", "event_title_vi", "value_per_share"])
       .groupby(["ticker", "exright_date"], as_index=False)["value_per_share"].sum())
iss = (ev[ev.event_code == "ISS"]
       .drop_duplicates(["ticker", "exright_date", "issue_method_name_vi", "exercise_ratio"]))
iss = (iss.assign(f=1.0 + iss.exercise_ratio)
       .groupby(["ticker", "exright_date"], as_index=False)["f"].prod())
DIVS = {t: (g.exright_date.values, g.value_per_share.values) for t, g in div.groupby("ticker")}
ISSS = {t: (g.exright_date.values, g.f.values) for t, g in iss.groupby("ticker")}

dep_ev = deposit_events_df()
def dep_big4(d):
    return float(dep_ev.loc[dep_ev.time <= d, "deposit_rate"].iloc[-1]) / 100.0

sbv = pd.read_csv(SBV_CSV)
sbv = sbv[sbv.series.str.contains("cao nhất")].copy()
sbv["avail"] = (pd.to_datetime(sbv.period + "-01") + pd.offsets.MonthBegin(1))  # mốc tháng T dùng từ T+1
def dep_sbv(d):
    s = sbv.loc[sbv.avail <= d, "rate_pct"]
    return float(s.iloc[-1]) / 100.0 if len(s) else np.nan

DAY = np.timedelta64(1, "D")

def factor(tk, lo, hi):
    """Π(1+ratio) của CP thưởng/cổ tức CP có exright trong (lo, hi]."""
    if tk not in ISSS:
        return 1.0
    d, f = ISSS[tk]
    m = (d > lo) & (d <= hi)
    return float(np.prod(f[m])) if m.any() else 1.0

rows = []
for r in panel.itertuples(index=False):
    D = np.datetime64(r.D)
    dps = [0.0] * 5
    fwd, first_fwd_dt, first_fwd_amt = 0.0, pd.NaT, np.nan
    if r.ticker in DIVS:
        dd, vv = DIVS[r.ticker]
        for e, v in zip(dd, vv):
            if e <= D:
                k = int((D - e) / DAY) // 365  # e∈W_k=(D-(k+1)365, D-k365] ⇔ D-e∈[k·365,(k+1)·365)
                if 0 <= k < 5:
                    dps[k] += v / factor(r.ticker, e, D)
            elif e <= D + 365 * DAY:
                amt = v * factor(r.ticker, D, e)
                fwd += amt
                if pd.isna(first_fwd_dt):
                    first_fwd_dt, first_fwd_amt = pd.Timestamp(e), amt
    rows.append(dict(dps0=dps[0], dps1=dps[1], dps2=dps[2], dps3=dps[3], dps4=dps[4], dps_fwd=fwd,
                     first_fwd_dt=first_fwd_dt, first_fwd_amt=first_fwd_amt,
                     bonus_fwd=factor(r.ticker, D, np.datetime64(r.last_dt) if pd.notna(r.last_dt) else D)))
df = pd.concat([panel.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
df = df[(df.Price > 0) & (df.Close > 0)].copy()
df["dep"] = df.D.map(dep_big4)
df["dep_sbv"] = df.D.map(dep_sbv)
df["y"] = df.dps0 / df.Price
df["year"] = df.D.dt.year
df["annual"] = df.D.dt.month == 12
df["has_fwd"] = df.n_fwd.fillna(0) > 0
df["delist"] = df.has_fwd & (df.last_dt < df.D + pd.Timedelta(days=335))
df["TR12"] = df.last_close / df.Close - 1
df["MDD12"] = np.minimum(df.min_close / df.Close - 1, 0.0)
df["PX12"] = df.last_price * df.bonus_fwd / df.Price - 1     # giá thô, quy đổi CP thưởng, KHÔNG cổ tức
df["TR12_raw"] = (df.last_price * df.bonus_fwd + df.dps_fwd) / df.Price - 1  # đường độc lập (self-check)
df["excess"] = df.TR12 - df.dep
df["fwd_ratio"] = np.where(df.dps0 > 0, df.dps_fwd / df.dps0, np.nan)
icb = df.ICB_Code.fillna(-1).astype(int).astype(str)
df["ind"] = icb.str[0].map(ICB1).fillna("?")
df.loc[icb.str[:2].isin(ICB2), "ind"] = icb.str[:2].map(ICB2)


def stable(d, N, X):
    cols = [f"dps{k}" for k in range(N)]
    ok = (d[cols] > 0).all(axis=1)
    for k in range(N - 1):
        ok &= d[f"dps{k}"] >= (1 - X) * d[f"dps{k+1}"]
    return ok


def g_hist(d, N):
    g = (d.dps0 / d[f"dps{N-1}"]) ** (1.0 / (N - 1)) - 1
    return g.clip(0.0, 0.08)


VARIANTS = {
    "P0": dict(N=5, X=0.25, bench="dep", payout=False, extra=0.0, freq="annual"),
    "V1": dict(N=3, X=0.25, bench="dep", payout=False, extra=0.0, freq="annual"),
    "V2": dict(N=5, X=0.10, bench="dep", payout=False, extra=0.0, freq="annual"),
    "V3": dict(N=5, X=0.25, bench="dep_sbv", payout=False, extra=0.0, freq="annual"),
    "V4": dict(N=5, X=0.25, bench="dep", payout=True, extra=0.0, freq="annual"),
    "V5": dict(N=5, X=0.25, bench="dep", payout=False, extra=0.0, freq="quarterly"),
    "V6": dict(N=5, X=0.25, bench="dep", payout=False, extra=0.02, freq="annual"),
    "V7": dict(N=3, X=0.10, bench="dep", payout=False, extra=0.0, freq="annual"),
}


def label(d, v):
    m = stable(d, v["N"], v["X"]) & (d.y > d[v["bench"]] + v["extra"])
    if v["payout"]:
        m &= (d.PE > 0) & (d.y * d.PE <= 1.0)
    return m


rng = np.random.default_rng(SEED)


def boot(d, stat, nb=NBOOT):
    """bootstrap khối-năm: lấy lại NĂM có hoàn lại, mang mọi dòng của năm đó."""
    d = d.reset_index(drop=True)
    years = np.array(sorted(d.year.unique()))
    pos = {y: np.flatnonzero(d.year.values == y) for y in years}
    vals = []
    for _ in range(nb):
        pick = rng.choice(years, size=len(years), replace=True)
        vals.append(stat(d.iloc[np.concatenate([pos[y] for y in pick])]))
    vals = np.array(vals, dtype=float)
    vals = vals[~np.isnan(vals)]
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def base_sample(v, full_only=True):
    d = df[df.has_fwd].copy()
    d = d[d.annual] if v["freq"] == "annual" else d
    if full_only:
        d = d[d.year <= 2024] if v["freq"] == "annual" else d[d.D <= "2025-09-30"]
    d = d[d.D >= "2011-12-01"]  # dep series bắt đầu 2011-01-01 ⇒ D đầu tiên = cuối 2011
    if v["freq"] == "quarterly":
        d = d[d.D <= pd.Timestamp("2025-09-30") - pd.Timedelta(days=365)]  # cửa sổ đủ 12T: D ≤ 2024-09-30
    d["coh"] = label(d, v)
    d["payer_other"] = (~d.coh) & (d.dps0 > 0)
    N = v["N"]
    d["g"] = g_hist(d, N).where(d.coh)
    d["rstar0"] = d.y
    d["rstar_g"] = d.y * (1 + d.g) + d.g
    d["spr0"] = d.rstar0 - d[v["bench"]]
    d["spr_g"] = d.rstar_g - d[v["bench"]]
    return d


def summarize(d, tag):
    c = d[d.coh]
    po = d[d.payer_other]
    nd = c[~c.delist]
    out = dict(tag=tag, n_rows=int(len(c)), n_tickers=int(c.ticker.nunique()), n_years=int(c.year.nunique()),
               n_delist=int(c.delist.sum()))
    for th in (0.30, 0.40, 0.50):
        k = f"{int(th*100)}"
        out[f"mdd{k}_n"] = int((c.MDD12 <= -th).sum())
        out[f"mdd{k}_years"] = int(c.loc[c.MDD12 <= -th, "year"].nunique())
        out[f"mdd{k}_freq"] = float((c.MDD12 <= -th).mean()) if len(c) else np.nan
        out[f"tr{k}_n"] = int((c.TR12 <= -th).sum())
        out[f"px{k}_n"] = int((c.PX12 <= -th).sum())
        out[f"po_mdd{k}_freq"] = float((po.MDD12 <= -th).mean())
        out[f"all_mdd{k}_freq"] = float((d.MDD12 <= -th).mean())
    out["mdd30_n_nodelist"] = int((nd.MDD12 <= -0.30).sum())
    out["mdd30_years_nodelist"] = int(nd.loc[nd.MDD12 <= -0.30, "year"].nunique())
    out["px_neg_freq"] = float((c.PX12 < 0).mean()) if len(c) else np.nan
    out["tr_neg_freq"] = float((c.TR12 < 0).mean()) if len(c) else np.nan
    out["excess_mean"] = float(c.excess.mean()) if len(c) else np.nan
    out["excess_median"] = float(c.excess.median()) if len(c) else np.nan
    out["po_excess_mean"] = float(po.excess.mean())
    out["all_excess_mean"] = float(d.excess.mean())
    out["spr0_median"] = float(c.spr0.median()) if len(c) else np.nan
    out["sprg_median"] = float(c.spr_g.median()) if len(c) else np.nan
    out["share_rstar_below_model"] = float((c.spr_g < MODEL_SPREAD).mean()) if len(c) else np.nan
    out["yield_median"] = float(c.y.median()) if len(c) else np.nan
    out["g_median"] = float(c.g.median()) if len(c) else np.nan
    if len(c) and c.year.nunique() >= 3:
        out["mdd30_freq_ci"] = boot(d, lambda x: (x.loc[x.coh, "MDD12"] <= -0.30).mean())
        out["diff_mdd30_coh_minus_po_ci"] = boot(
            d, lambda x: (x.loc[x.coh, "MDD12"] <= -0.30).mean() - (x.loc[x.payer_other, "MDD12"] <= -0.30).mean())
        out["excess_mean_ci"] = boot(d, lambda x: x.loc[x.coh, "excess"].mean())
        out["diff_excess_coh_minus_po_ci"] = boot(
            d, lambda x: x.loc[x.coh, "excess"].mean() - x.loc[x.payer_other, "excess"].mean())
        out["sprg_median_ci"] = boot(d, lambda x: x.loc[x.coh, "spr_g"].median())
    return out


results, samples = {}, {}
for name, v in VARIANTS.items():
    d = base_sample(v)
    samples[name] = d
    results[name] = summarize(d, name)
    if v["freq"] == "quarterly":  # đếm phản ví dụ theo mã-năm duy nhất
        c = d[d.coh & (d.MDD12 <= -0.30)]
        results[name]["mdd30_unique_ticker_years"] = int(c[["ticker", "year"]].drop_duplicates().shape[0])
        results[name]["coh_unique_ticker_years"] = int(d[d.coh][["ticker", "year"]].drop_duplicates().shape[0])

# ---------------------------------------------------------------- P0 chi tiết
P0 = samples["P0"]
coh = P0[P0.coh].copy()
by_year = (P0.groupby("year").apply(lambda x: pd.Series(dict(
    n_univ=len(x), n_coh=int(x.coh.sum()), dep=x.dep.iloc[0],
    coh_mdd30=int((x.coh & (x.MDD12 <= -0.30)).sum()),
    coh_mdd30_freq=(x.loc[x.coh, "MDD12"] <= -0.30).mean() if x.coh.any() else np.nan,
    po_mdd30_freq=(x.loc[x.payer_other, "MDD12"] <= -0.30).mean(),
    all_mdd30_freq=(x.MDD12 <= -0.30).mean(),
    coh_excess_mean=x.loc[x.coh, "excess"].mean() if x.coh.any() else np.nan,
    po_excess_mean=x.loc[x.payer_other, "excess"].mean(),
    coh_sprg_median=x.loc[x.coh, "spr_g"].median() if x.coh.any() else np.nan,
    coh_y_median=x.loc[x.coh, "y"].median() if x.coh.any() else np.nan)), include_groups=False))
by_year.to_csv(os.path.join(OUT, "P0_by_year_exp.csv"))

by_ind = coh.groupby("ind").apply(lambda x: pd.Series(dict(
    n=len(x), mdd30=int((x.MDD12 <= -0.30).sum()), mdd30_freq=(x.MDD12 <= -0.30).mean(),
    excess_mean=x.excess.mean(), sprg_median=x.spr_g.median())), include_groups=False).sort_values("n", ascending=False)
by_ind.to_csv(os.path.join(OUT, "P0_by_industry_exp.csv"))

cx = coh[coh.MDD12 <= -0.30].copy()
cx["div_after"] = pd.cut(cx.fwd_ratio, [-1e-9, 1e-9, 0.9 - 1e-9, 1e9], labels=["bỏ", "cắt", "giữ/tăng"])
cx["trough_vs_first_fwd_div"] = np.where(cx.first_fwd_dt.isna(), "không có cổ tức trong 12T",
                                         np.where(cx.min_dt < cx.first_fwd_dt, "đáy TRƯỚC ex-date kế tiếp",
                                                  "đáy SAU ex-date kế tiếp"))
cx["first_fwd_vs_dps0"] = cx.first_fwd_amt / cx.dps0
keep = ["ticker", "D", "ind", "y", "dep", "dps0", "dps1", "dps2", "dps3", "dps4", "MDD12", "min_dt", "TR12", "PX12",
        "dps_fwd", "fwd_ratio", "div_after", "first_fwd_dt", "first_fwd_vs_dps0", "trough_vs_first_fwd_div", "delist"]
cx[keep].sort_values(["D", "MDD12"]).to_csv(os.path.join(OUT, "P0_counterexamples_exp.csv"), index=False)
ck = [k for k in keep if k in coh.columns]
coh[ck + ["g", "spr_g", "excess"]].to_csv(os.path.join(OUT, "P0_cohort_exp.csv"), index=False)
# chia nhóm hành vi cổ tức cho TOÀN cohort (so phản ví dụ vs không)
coh["div_after"] = pd.cut(coh.fwd_ratio, [-1e-9, 1e-9, 0.9 - 1e-9, 1e9], labels=["bỏ", "cắt", "giữ/tăng"])
div_tab = pd.crosstab(coh.div_after, coh.MDD12 <= -0.30, margins=True)
div_tab.to_csv(os.path.join(OUT, "P0_div_behaviour_exp.csv"))

# ---------------------------------------------------------------- walk-forward IS/OOS + LOO
wf = {}
for nm in ["P0", "V1", "V5"]:
    d = samples[nm]
    is_, oos = d[d.year <= 2019], d[d.year >= 2020]
    if nm == "V5":
        is_, oos = d[d.D <= "2019-12-31"], d[d.D >= "2020-01-01"]
    s_is_real = float(is_.loc[is_.coh, "excess"].mean())
    s_is_impl = float(is_.loc[is_.coh, "spr_g"].median())
    wf[nm] = dict(
        IS_n=int(is_.coh.sum()), OOS_n=int(oos.coh.sum()),
        IS_years=int(is_.loc[is_.coh, "year"].nunique()), OOS_years=int(oos.loc[oos.coh, "year"].nunique()),
        s_IS_realized=s_is_real, s_IS_realized_ci=boot(is_, lambda x: x.loc[x.coh, "excess"].mean(), 3000),
        s_IS_implied_median=s_is_impl,
        OOS_realized_mean=float(oos.loc[oos.coh, "excess"].mean()),
        OOS_realized_ci=boot(oos, lambda x: x.loc[x.coh, "excess"].mean(), 3000),
        OOS_implied_median=float(oos.loc[oos.coh, "spr_g"].median()),
        OOS_implied_ci=boot(oos, lambda x: x.loc[x.coh, "spr_g"].median(), 3000),
        IS_mdd30_freq=float((is_.loc[is_.coh, "MDD12"] <= -0.30).mean()),
        OOS_mdd30_freq=float((oos.loc[oos.coh, "MDD12"] <= -0.30).mean()),
        IS_po_mdd30_freq=float((is_.loc[is_.payer_other, "MDD12"] <= -0.30).mean()),
        OOS_po_mdd30_freq=float((oos.loc[oos.payer_other, "MDD12"] <= -0.30).mean()),
        OOS_po_excess_mean=float(oos.loc[oos.payer_other, "excess"].mean()),
        IS_po_excess_mean=float(is_.loc[is_.payer_other, "excess"].mean()),
    )
loo = {}
for y in sorted(coh.year.unique()):
    x = coh[coh.year != y]
    loo[int(y)] = dict(excess_mean=float(x.excess.mean()), mdd30_freq=float((x.MDD12 <= -0.30).mean()),
                       sprg_median=float(x.spr_g.median()))
eqw = dict(excess_mean_equal_year=float(by_year.coh_excess_mean.mean()),
           mdd30_freq_equal_year=float(by_year.coh_mdd30_freq.mean()))

# ---------------------------------------------------------------- 2025 (cửa sổ dở, báo riêng)
d25 = df[df.has_fwd & df.annual & (df.year == 2025)].copy()
d25["coh"] = label(d25, VARIANTS["P0"])
p25 = dict(n_coh=int(d25.coh.sum()), mdd30=int((d25.coh & (d25.MDD12 <= -0.30)).sum()),
           window_end=str(d25.last_dt.max().date()) if len(d25) else None)

# ---------------------------------------------------------------- self-check
sc = {}
c = coh.copy()
m = c.DY.notna() & (c.DY > 0)
# DY của ETL lưu dạng PHÂN SỐ (không phải %) — phát hiện ở lần chạy 1 (median ratio đúng 100,0)
rel = (c.loc[m, "y"] / c.loc[m, "DY"] - 1).abs()
sc["yield_vs_ETL_DY_within10pct"] = float((rel <= 0.10).mean())
sc["yield_vs_ETL_DY_within25pct"] = float((rel <= 0.25).mean())
sc["yield_vs_ETL_DY_n"] = int(m.sum())
sc["yield_vs_ETL_DY_median_ratio"] = float((c.loc[m, "y"] / c.loc[m, "DY"]).median())
mm = c.last_price.notna() & ~c.delist
diff = (c.loc[mm, "TR12_raw"] - c.loc[mm, "TR12"]).abs()
sc["TR12_raw_vs_close_n"] = int(mm.sum())
sc["TR12_raw_vs_close_within2pp"] = float((diff <= 0.02).mean())
sc["TR12_raw_vs_close_median_absdiff"] = float(diff.median())
# đếm phản ví dụ bằng đường giá thô độc lập: MDD không có ở đường thô ⇒ dùng TR12_raw ≤ -30%
sc["tr30_count_close"] = int((c.TR12 <= -0.30).sum())
sc["tr30_count_raw"] = int((c.TR12_raw <= -0.30).sum())

# ---------------------------------------------------------------- KHÁM PHÁ (KHÔNG có trong PREREG)
# E1: tăng trưởng cổ tức THỰC HIỆN sau D (ex-post) — ước lượng g "đáng lẽ kỳ vọng"; chỉ D ≤ 2022 (đủ 3 năm sau).
def fwd_dps(tk, D, j):
    if tk not in DIVS:
        return 0.0
    dd, vv = DIVS[tk]
    lo, hi = D + (j - 1) * 365 * DAY, D + j * 365 * DAY
    return float(sum(v * factor(tk, D, e) for e, v in zip(dd, vv) if lo < e <= hi))
e1 = coh[coh.year <= 2022].copy()
f = np.array([[fwd_dps(t, np.datetime64(d), j) for j in (1, 2, 3)] for t, d in zip(e1.ticker, e1.D)])
e1["g_fwd_real"] = (f.mean(axis=1) / e1.dps0) ** 0.5 - 1   # trung bình 3 năm sau ~ tâm năm 2
e1["rstar_realg"] = e1.y * (1 + e1.g_fwd_real) + e1.g_fwd_real
e1["spr_realg"] = e1.rstar_realg - e1.dep
E1 = dict(n=int(len(e1)), g_fwd_real_median=float(e1.g_fwd_real.median()),
          g_fwd_real_p25=float(e1.g_fwd_real.quantile(.25)), g_fwd_real_p75=float(e1.g_fwd_real.quantile(.75)),
          spr_realg_median=float(e1.spr_realg.median()),
          spr_realg_median_ci=boot(e1.assign(coh=True), lambda x: x.spr_realg.median(), 3000),
          share_spr_realg_below_model=float((e1.spr_realg < MODEL_SPREAD).mean()),
          IS_spr_realg_median=float(e1.loc[e1.year <= 2019, "spr_realg"].median()),
          OOS_spr_realg_median=float(e1.loc[e1.year >= 2020, "spr_realg"].median()),
          OOS_n=int((e1.year >= 2020).sum()))
# E2: g ngầm thị trường đang định giá NẾU r = dep + 6,1pp (mô hình):  g* = (r − y)/(1+y)
coh["r_model"] = coh.dep + MODEL_SPREAD
coh["g_star_at_model_r"] = (coh.r_model - coh.y) / (1 + coh.y)
E2 = dict(g_star_median=float(coh.g_star_at_model_r.median()),
          g_star_p25=float(coh.g_star_at_model_r.quantile(.25)), g_star_p75=float(coh.g_star_at_model_r.quantile(.75)),
          share_y_above_model_r=float((coh.y > coh.r_model).mean()))
# E3: độ nhạy loại yield bất thường (>25%, nghi cổ tức đặc biệt/lỗi dữ liệu)
cc = coh[coh.y <= 0.25]
E3 = dict(n=int(len(cc)), mdd30_n=int((cc.MDD12 <= -0.30).sum()), mdd30_freq=float((cc.MDD12 <= -0.30).mean()),
          excess_mean=float(cc.excess.mean()), excess_median=float(cc.excess.median()))
# E4: phân loại phản ví dụ theo năm khủng hoảng toàn thị trường (all_mdd30_freq năm đó ≥ 25%)
crash_years = set(by_year.index[by_year.all_mdd30_freq >= 0.25])
cxx = coh[coh.MDD12 <= -0.30]
E4 = dict(crash_years=sorted(int(y) for y in crash_years),
          cx_in_crash_years=int(cxx.year.isin(crash_years).sum()), cx_other_years=int((~cxx.year.isin(crash_years)).sum()))
# Bảng nhóm (P0): cohort vs payer khác vs universe — excess thực hiện + spread yield (g=0), bootstrap khối-năm
grp = {}
for gname, sel in [("cohort", "coh"), ("payer_khac", "payer_other"), ("universe", None)]:
    x = P0 if sel is None else P0[P0[sel]]
    xx = P0.assign(_s=True) if sel is None else P0.assign(_s=P0[sel])
    grp[gname] = dict(n=int(len(x)), excess_mean=float(x.excess.mean()), excess_median=float(x.excess.median()),
                      excess_mean_ci=boot(xx, lambda z: z.loc[z._s, "excess"].mean(), 3000),
                      excess_median_ci=boot(xx, lambda z: z.loc[z._s, "excess"].median(), 3000),
                      y_minus_dep_median=float((x.y - x.dep).median()),
                      mdd30_freq=float((x.MDD12 <= -0.30).mean()), mdd50_freq=float((x.MDD12 <= -0.50).mean()))
pd.DataFrame(grp).T.to_csv(os.path.join(OUT, "P0_groups_exp.csv"))
explore = dict(groups_P0=grp, E1_realized_div_growth=E1, E2_implied_g_at_model_r=E2, E3_ex_yield_gt25=E3, E4_crash_split=E4)

summary = dict(explore_not_prereg=explore, prereg_md5=open(os.path.join(B, "PREREG.md5")).read().split()[0:4:2],
               variants=VARIANTS, results=results, walk_forward=wf, loo_P0=loo, equal_year_P0=eqw,
               partial_2025=p25, selfcheck=sc, n_trials=len(VARIANTS))
with open(os.path.join(OUT, "summary_exp.json"), "w") as f:
    json.dump(summary, f, ensure_ascii=False, indent=1, default=str)
pd.DataFrame(results).T.to_csv(os.path.join(OUT, "variants_exp.csv"))
print(json.dumps(summary, ensure_ascii=False, indent=1, default=str)[:20000])
print(by_year.round(3).to_string())
print(by_ind.round(3).to_string())
print(div_tab.to_string())
