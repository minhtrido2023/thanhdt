#!/usr/bin/env python3
"""Rights-offering (ISS/Rights) event study — job Taylor_20260821_103727.
Spec khoá trước ở PREREG.md cùng thư mục. Script chỉ thực thi spec đó."""
import os
import numpy as np
import pandas as pd
from scipy import stats

D = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260821)
N_BOOT = 5000

ev = pd.read_csv(f"{D}/events.csv", parse_dates=["exright_date", "t0"])
ct = pd.read_csv(f"{D}/control.csv", parse_dates=["t0"])

# ---- lọc theo PREREG §4: in_universe tại t0 ----
ev["in_universe"] = ev.in_universe.astype(str).str.lower() == "true"
full = ev.copy()
ev = ev[ev.in_universe].copy()

ev["period"] = np.where(ev.exright_date <= pd.Timestamp("2019-12-31"), "IS", "OOS")
ev["block"] = ev.exright_date.dt.to_period("M").astype(str)

# ---- control ghép cặp (cùng t0, cùng icb_lv1) ----
ev = ev.merge(ct, left_on=["t0", "icb_code_lv1"], right_on=["t0", "icb"], how="left")
ev["net_close"] = ev.bhar60_close - ev.ctrl_bhar60_close
ev["net_price"] = ev.bhar60_price - ev.ctrl_bhar60_price

# ---- H2: discount (PREREG §3.1 deviation 2) ----
ip = pd.to_numeric(ev.issue_price, errors="coerce")
ip = ip.where((ip >= 1000) & (ip <= 500000))
ev["issue_price_ok"] = ip
ev["discount"] = 1.0 - ip / pd.to_numeric(ev.price_t0, errors="coerce")
ev["disc_grp"] = np.where(ev.discount.isna(), "unknown",
                          np.where(ev.discount >= 0.30, "deep_ge30", "shallow_lt30"))
ev.to_csv(f"{D}/results_events_enriched.csv", index=False)


def onesample(x):
    x = pd.to_numeric(x, errors="coerce").dropna().to_numpy(float)
    if len(x) < 2:
        return np.nan, np.nan, len(x)
    t, p = stats.ttest_1samp(x, 0.0)
    return float(t), float(p), len(x)


def boot_mean(df, col):
    """Block bootstrap theo tháng lịch của exright_date; vectorised trên sum/count mỗi block."""
    d = df[["block", col]].dropna()
    if d.empty:
        return (np.nan, np.nan, np.nan)
    g = d.groupby("block")[col].agg(["sum", "count"])
    s, c = g["sum"].to_numpy(float), g["count"].to_numpy(float)
    idx = RNG.integers(0, len(s), size=(N_BOOT, len(s)))
    S, C = s[idx].sum(1), c[idx].sum(1)
    out = np.where(C > 0, S / np.where(C == 0, np.nan, C), np.nan)
    out = out[~np.isnan(out)]
    return (float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5)), float(np.mean(out < 0)))


rows = []
scopes = [("FULL", ev), ("IS", ev[ev.period == "IS"]), ("OOS", ev[ev.period == "OOS"])]
# robustness: loại CRISIS(0) và EX-BULL(4)
ex_reg = ev[~ev.dt5g_state.isin([0, 4])]
scopes += [("EX_REGIME(no CRISIS/EXBULL)", ex_reg),
           ("EX_REGIME_IS", ex_reg[ex_reg.period == "IS"]),
           ("EX_REGIME_OOS", ex_reg[ex_reg.period == "OOS"])]
# STRICT: chi giu su kien CO nhan DT5G (bang chi phu tu 2014) — tranh doc NaN thanh "khong phai CRISIS"
strict = ev[ev.dt5g_state.notna() & ~ev.dt5g_state.isin([0, 4])]
scopes += [("EX_REGIME_STRICT(co nhan DT5G)", strict),
           ("EX_REGIME_STRICT_IS", strict[strict.period == "IS"]),
           ("EX_REGIME_STRICT_OOS", strict[strict.period == "OOS"])]
for col in ["bhar60_close", "net_close", "bhar60_price", "net_price"]:
    for name, sub in scopes:
        t, p, n = onesample(sub[col])
        lo, hi, pneg = boot_mean(sub, col)
        x = pd.to_numeric(sub[col], errors="coerce").dropna()
        w = float(stats.wilcoxon(x)[1]) if len(x) > 10 else np.nan
        rows.append(dict(metric=col, scope=name, n=n,
                         pct_negative=100 * float((x < 0).mean()) if len(x) else np.nan,
                         wilcoxon_p=w,
                         mean_pp=100 * pd.to_numeric(sub[col], errors="coerce").mean(),
                         median_pp=100 * pd.to_numeric(sub[col], errors="coerce").median(),
                         t=t, p_two_sided=p,
                         boot_lo_pp=100 * lo if lo == lo else np.nan,
                         boot_hi_pp=100 * hi if hi == hi else np.nan, boot_p_neg=pneg))
res = pd.DataFrame(rows)
res.to_csv(f"{D}/results_stats.csv", index=False)

# ---- H2 ----
h2 = []
for name, sub in [("FULL", ev), ("IS", ev[ev.period == "IS"]), ("OOS", ev[ev.period == "OOS"])]:
    d = sub[sub.disc_grp == "deep_ge30"]["bhar60_close"].dropna()
    s = sub[sub.disc_grp == "shallow_lt30"]["bhar60_close"].dropna()
    t, p = (stats.ttest_ind(d, s, equal_var=False) if len(d) > 1 and len(s) > 1 else (np.nan, np.nan))
    h2.append(dict(scope=name, n_deep=len(d), n_shallow=len(s),
                   mean_deep_pp=100 * d.mean() if len(d) else np.nan,
                   mean_shallow_pp=100 * s.mean() if len(s) else np.nan,
                   delta_pp=100 * (d.mean() - s.mean()) if len(d) and len(s) else np.nan,
                   t=float(t) if t == t else np.nan, p=float(p) if p == p else np.nan))
h2 = pd.DataFrame(h2)
h2.to_csv(f"{D}/results_h2_discount.csv", index=False)

pd.set_option("display.width", 220)
print(f"=== MẪU === events có giá tại t0: {len(full)} | in_universe_pit: {len(ev)} "
      f"| IS {int((ev.period=='IS').sum())} / OOS {int((ev.period=='OOS').sum())}")
print(f"    range {ev.exright_date.min().date()} .. {ev.exright_date.max().date()} | "
      f"mã {ev.ticker.nunique()} | có control ghép cặp: {ev.ctrl_bhar60_close.notna().sum()} "
      f"(n_ctrl trung vị {ev.n_ctrl.median():.0f})")
print(f"    dt5g_state có: {ev.dt5g_state.notna().sum()} | discount tính được: {ev.discount.notna().sum()}")
print("\n=== KẾT QUẢ ===")
print(res.to_string(index=False))
print("\n=== H2 discount (secondary, KHÔNG quyết GO) ===")
print(h2.to_string(index=False))

def g(metric, scope):
    return res[(res.metric == metric) & (res.scope == scope)].iloc[0]
F, I, O = g("bhar60_close", "FULL"), g("bhar60_close", "IS"), g("bhar60_close", "OOS")
N = g("net_close", "FULL")
weak = (I.n < 30) or (O.n < 30)
go = (not weak and I.mean_pp <= -2.0 and O.mean_pp <= -2.0 and I.t <= -2.0 and O.t <= -2.0
      and not (F.boot_lo_pp < 0 < F.boot_hi_pp) and N.mean_pp < 0)
verdict = "WEAK_N" if weak else ("GO" if go else "NO-GO")
print(f"\nVERDICT (PREREG §7) = {verdict}")
print(f"  FULL BHAR_60(Close) = {F.mean_pp:+.2f}pp t={F.t:+.2f} p={F.p_two_sided:.4f} "
      f"boot95=[{F.boot_lo_pp:+.2f},{F.boot_hi_pp:+.2f}]")
print(f"  IS  = {I.mean_pp:+.2f}pp t={I.t:+.2f} n={I.n}   OOS = {O.mean_pp:+.2f}pp t={O.t:+.2f} n={O.n}")
print(f"  Hiệu ròng ghép cặp FULL = {N.mean_pp:+.2f}pp t={N.t:+.2f} p={N.p_two_sided:.4f}")
