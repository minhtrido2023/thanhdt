#!/usr/bin/env python3
"""Pre-ex-date buy avoidance study — job Taylor_20260821_103727.

Spec khoá trước ở PREREG.md cùng thư mục. Script này CHỈ thực thi spec đó.
Chạy: $DNA_PYEXE analyze.py   (từ WorkingClaude root hoặc bất kỳ đâu — path tự neo)
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

D = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260821)
N_BOOT = 5000

# ---------- nạp ----------
ent = pd.read_csv(f"{D}/entries.csv", parse_dates=["entry_date"])
ent = ent[ent.play_type != "ETF_PARK"].copy()          # rổ parking không phải mã đơn lẻ
px = pd.read_csv(f"{D}/px_entries.csv", parse_dates=["time"])
div = pd.read_csv(f"{D}/div_events.csv", parse_dates=["exright_date"])
vni = pd.read_csv(f"{D}/vni.csv", parse_dates=["time"])

# ---------- BHAR_20 ----------
ent = ent.merge(px, left_on=["ticker", "entry_date"], right_on=["ticker", "time"], how="left")
ent = ent.merge(vni.rename(columns={"Close": "vni_0", "Close_f20": "vni_f20"}),
                left_on="entry_date", right_on="time", how="left", suffixes=("", "_v"))

def _ret(a, b):
    a, b = pd.to_numeric(a, errors="coerce"), pd.to_numeric(b, errors="coerce")
    return np.where((a > 0) & (b > 0), b / a - 1.0, np.nan)

ent["r20_close"] = _ret(ent.Close, ent.Close_f20)
ent["r20_price"] = _ret(ent.Price, ent.Price_f20)
ent["r20_vni"] = _ret(ent.vni_0, ent.vni_f20)
ent["bhar20_close"] = ent.r20_close - ent.r20_vni     # PRIMARY (giá điều chỉnh)
ent["bhar20_price"] = ent.r20_price - ent.r20_vni     # chứng minh cơ học (giá thô)

# ---------- days_to_ex: ex-date tương lai gần nhất trong (0,60] ngày ----------
div = div.dropna(subset=["exright_date"]).sort_values(["ticker", "exright_date"])
ex_by_tk = {t: g.exright_date.values for t, g in div.groupby("ticker")}
val_by_tk = {t: g.value_per_share.values for t, g in div.groupby("ticker")}

d2e, dps = [], []
for t, e in zip(ent.ticker.values, ent.entry_date.values):
    arr = ex_by_tk.get(t)
    if arr is None:
        d2e.append(np.nan); dps.append(np.nan); continue
    delta = (arr - e).astype("timedelta64[D]").astype(int)
    m = (delta > 0) & (delta <= 60)
    if not m.any():
        d2e.append(np.nan); dps.append(np.nan); continue
    i = int(np.argmin(np.where(m, delta, 10**6)))
    d2e.append(int(delta[i])); dps.append(val_by_tk[t][i])
ent["days_to_ex"] = d2e
ent["div_vnd_per_share"] = dps
ent["div_yield_pct"] = 100.0 * ent.div_vnd_per_share / pd.to_numeric(ent.Price, errors="coerce")

def _bin(d):
    if pd.isna(d):
        return "no_ex"
    if d <= 10:
        return "near_ex"
    if d <= 29:
        return "mid"
    return "far"
ent["cohort"] = ent.days_to_ex.map(_bin)
ent["period"] = np.where(ent.entry_date <= pd.Timestamp("2019-12-31"), "IS", "OOS")
ent["block"] = ent.entry_date.dt.to_period("M").astype(str)

ent.to_csv(f"{D}/results_entries_binned.csv", index=False)

# ---------- thống kê ----------
def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan, len(a), len(b)
    t, p = stats.ttest_ind(a, b, equal_var=False)
    return float(t), float(p), len(a), len(b)

def block_boot(df, col):
    """Block bootstrap theo tháng lịch: resample THÁNG (có hoàn lại), tính lại hiệu số near-far.
    Vectorised: gộp sum/count theo (block, cohort) trước, resample chỉ trên chỉ số block."""
    d = df[df.cohort.isin(["near_ex", "far"])][["block", "cohort", col]].dropna(subset=[col])
    if d.empty:
        return (np.nan, np.nan, np.nan, 0)
    g = d.groupby(["block", "cohort"])[col].agg(["sum", "count"]).unstack(fill_value=0.0)
    for c in ["near_ex", "far"]:
        for st in ["sum", "count"]:
            if (st, c) not in g.columns:
                g[(st, c)] = 0.0
    sn = g[("sum", "near_ex")].to_numpy(float); cn = g[("count", "near_ex")].to_numpy(float)
    sf = g[("sum", "far")].to_numpy(float);     cf = g[("count", "far")].to_numpy(float)
    nb = len(sn)
    idx = RNG.integers(0, nb, size=(N_BOOT, nb))
    SN, CN = sn[idx].sum(1), cn[idx].sum(1)
    SF, CF = sf[idx].sum(1), cf[idx].sum(1)
    ok = (CN >= 2) & (CF >= 2)
    out = np.where(ok, SN / np.where(CN == 0, np.nan, CN) - SF / np.where(CF == 0, np.nan, CF), np.nan)
    out = out[~np.isnan(out)]
    if len(out) == 0:
        return (np.nan, np.nan, np.nan, 0)
    return (float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5)),
            float(np.mean(out < 0)), len(out))

rows = []
for col in ["bhar20_close", "bhar20_price"]:
    for scope, sub in [("FULL", ent), ("IS", ent[ent.period == "IS"]), ("OOS", ent[ent.period == "OOS"]),
                       ("BAL", ent[ent.book == "BAL"]), ("LAG", ent[ent.book == "LAG"])]:
        n = sub[sub.cohort == "near_ex"][col]
        f = sub[sub.cohort == "far"][col]
        t, p, na, nb = welch(n, f)
        lo, hi, pneg, _ = block_boot(sub, col) if scope in ("FULL", "IS", "OOS") else (np.nan,)*4
        rows.append(dict(metric=col, scope=scope, n_near=na, n_far=nb,
                         mean_near_pp=100*np.nanmean(n) if na else np.nan,
                         mean_far_pp=100*np.nanmean(f) if nb else np.nan,
                         delta_pp=100*(np.nanmean(n)-np.nanmean(f)) if na and nb else np.nan,
                         t=t, p=p, boot_lo_pp=100*lo if lo==lo else np.nan,
                         boot_hi_pp=100*hi if hi==hi else np.nan, boot_p_neg=pneg))
res = pd.DataFrame(rows)
res.to_csv(f"{D}/results_stats.csv", index=False)

coh = ent.groupby(["cohort", "period"]).agg(
    n=("bhar20_close", "size"),
    bhar_close_pp=("bhar20_close", lambda s: 100*s.mean()),
    bhar_price_pp=("bhar20_price", lambda s: 100*s.mean()),
    div_yield_pct=("div_yield_pct", "mean")).reset_index()
coh.to_csv(f"{D}/results_cohorts.csv", index=False)

pd.set_option("display.width", 200)
print("=== COHORT (n, BHAR_20 trung bình, pp) ===")
print(coh.to_string(index=False))
print("\n=== near_ex vs far ===")
print(res.to_string(index=False))

# ---------- verdict theo PREREG §7 ----------
def get(metric, scope):
    r = res[(res.metric == metric) & (res.scope == scope)].iloc[0]
    return r
f_c, is_c, oos_c = get("bhar20_close", "FULL"), get("bhar20_close", "IS"), get("bhar20_close", "OOS")
weak = (is_c.n_near < 30) or (oos_c.n_near < 30)
go = (not weak and f_c.delta_pp <= -1.5 and abs(is_c.t) >= 2.0 and abs(oos_c.t) >= 2.0
      and np.sign(is_c.delta_pp) == np.sign(oos_c.delta_pp)
      and not (f_c.boot_lo_pp < 0 < f_c.boot_hi_pp))
verdict = "WEAK_N" if weak else ("GO" if go else "NO-GO")
print(f"\nVERDICT (PREREG §7) = {verdict}")
print(f"  FULL Close delta={f_c.delta_pp:.2f}pp t={f_c.t:.2f} boot95=[{f_c.boot_lo_pp:.2f},{f_c.boot_hi_pp:.2f}]")
print(f"  IS   delta={is_c.delta_pp:.2f}pp t={is_c.t:.2f} n_near={is_c.n_near}")
print(f"  OOS  delta={oos_c.delta_pp:.2f}pp t={oos_c.t:.2f} n_near={oos_c.n_near}")
f_p = get("bhar20_price", "FULL")
print(f"  [cơ học] FULL Price delta={f_p.delta_pp:.2f}pp t={f_p.t:.2f} — kỳ vọng âm ~div yield nếu hiệu ứng thuần kế toán")
print(f"  div yield trung bình near_ex = {ent[ent.cohort=='near_ex'].div_yield_pct.mean():.2f}%")
