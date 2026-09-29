#!/usr/bin/env python3
"""ISS/rights offering — test TRUNG VI lam primary. Job Taylor_20260821_111228.
Spec khoa truoc o PREREG.md cung thu muc. Du lieu H1/H2 TAI DUNG tu ../iss_event_study_20260821/."""
import os
import numpy as np
import pandas as pd
from scipy import stats

D = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(D), "iss_event_study_20260821")
DEAL = os.path.join(os.path.dirname(D), "pre_exdate_avoidance_20260821")
RNG = np.random.default_rng(20260821)
N_BOOT = 5000

# ---------- H1/H2: tai dung mau study truoc (KHONG pull lai) ----------
ev = pd.read_csv(f"{SRC}/events.csv", parse_dates=["exright_date", "t0"])
ct = pd.read_csv(f"{SRC}/control.csv", parse_dates=["t0"])
ev["in_universe"] = ev.in_universe.astype(str).str.lower() == "true"
ev = ev[ev.in_universe].copy()
ev["period"] = np.where(ev.exright_date <= pd.Timestamp("2019-12-31"), "IS", "OOS")
ev["block"] = ev.exright_date.dt.to_period("M").astype(str)
ev = ev.merge(ct, left_on=["t0", "icb_code_lv1"], right_on=["t0", "icb"], how="left")
ev["net_close"] = ev.bhar60_close - ev.ctrl_bhar60_close
ev["net_price"] = ev.bhar60_price - ev.ctrl_bhar60_price


def boot_median(df, col):
    """Block bootstrap theo thang lich cua exright_date, thong ke = TRUNG VI."""
    d = df[["block", col]].dropna()
    if len(d) < 5:
        return (np.nan, np.nan, np.nan)
    blocks = [g[col].to_numpy(float) for _, g in d.groupby("block")]
    k = len(blocks)
    out = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = RNG.integers(0, k, size=k)
        out[i] = np.median(np.concatenate([blocks[j] for j in idx]))
    return (float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5)),
            float(np.mean(out >= -0.02)))


scopes = [("FULL", ev), ("IS", ev[ev.period == "IS"]), ("OOS", ev[ev.period == "OOS"])]
ex_reg = ev[~ev.dt5g_state.isin([0, 4])]
scopes += [("EX_REGIME", ex_reg),
           ("EX_REGIME_IS", ex_reg[ex_reg.period == "IS"]),
           ("EX_REGIME_OOS", ex_reg[ex_reg.period == "OOS"])]
strict = ev[ev.dt5g_state.notna() & ~ev.dt5g_state.isin([0, 4])]
scopes += [("EX_REGIME_STRICT", strict)]

rows = []
for col in ["bhar60_close", "net_close", "bhar60_price", "net_price"]:
    for name, sub in scopes:
        x = pd.to_numeric(sub[col], errors="coerce").dropna()
        if len(x) < 5:
            continue
        w = stats.wilcoxon(x) if len(x) > 10 else None
        lo, hi, p_ge = boot_median(sub, col)
        rows.append(dict(metric=col, scope=name, n=len(x),
                         median=float(x.median()), mean=float(x.mean()),
                         pct_negative=100 * float((x < 0).mean()),
                         wilcoxon_p=float(w.pvalue) if w is not None else np.nan,
                         boot_med_lo=lo, boot_med_hi=hi, boot_p_median_ge_minus2pp=p_ge))
res = pd.DataFrame(rows)
res.to_csv(f"{D}/results_median.csv", index=False)

# ---------- H3: tan suat ISS "trung" vao portfolio that ----------
ent = pd.read_csv(f"{DEAL}/entries.csv", parse_dates=["entry_date"])
ent = ent[ent.play_type != "ETF_PARK"].copy()          # PREREG §2 H3
iss = pd.read_csv(f"{DEAL}/../iss_median_study_20260821/iss_ledger.csv",
                  parse_dates=["exright_date"])
ex_by_tk = {t: g.exright_date.values for t, g in iss.groupby("ticker")}

hit, dsince, npre = [], [], []
for t, e in zip(ent.ticker.values, ent.entry_date.values):
    arr = ex_by_tk.get(t)
    if arr is None:
        hit.append(False); dsince.append(np.nan); npre.append(0); continue
    delta = (e - arr).astype("timedelta64[D]").astype(int)   # >0 = ex-date TRUOC entry
    m = (delta >= 0) & (delta <= 60)
    npre.append(int(m.sum()))
    if m.any():
        hit.append(True); dsince.append(int(delta[m].min()))
    else:
        hit.append(False); dsince.append(np.nan)
ent["iss_hit_60d"] = hit
ent["days_since_ex"] = dsince
ent["n_iss_in_window"] = npre
ent["period"] = np.where(ent.entry_date <= pd.Timestamp("2019-12-31"), "IS", "OOS")
ent.to_csv(f"{D}/results_h3_hits.csv", index=False)

h3 = []
for name, sub in [("FULL", ent), ("IS", ent[ent.period == "IS"]),
                  ("OOS", ent[ent.period == "OOS"]),
                  ("BAL", ent[ent.book == "BAL"]), ("LAG", ent[ent.book == "LAG"])]:
    h3.append(dict(scope=name, n_deals=len(sub), n_hit=int(sub.iss_hit_60d.sum()),
                   hit_pct=100 * float(sub.iss_hit_60d.mean()) if len(sub) else np.nan,
                   n_tickers=sub.ticker.nunique(),
                   n_tickers_hit=sub[sub.iss_hit_60d].ticker.nunique()))
h3 = pd.DataFrame(h3)
h3.to_csv(f"{D}/results_h3.csv", index=False)

pd.set_option("display.width", 220, "display.max_columns", 40)
print("=== H1/H2: TRUNG VI ===")
print(res.round(5).to_string(index=False))
print("\n=== H3: ISS trung vao deal thuc ===")
print(h3.round(3).to_string(index=False))
print("\nn deal co >=1 ISS trong [-60,0]:", int(ent.iss_hit_60d.sum()), "/", len(ent))
print("phan bo days_since_ex cua cac deal hit:")
print(ent.loc[ent.iss_hit_60d, "days_since_ex"].describe().round(2).to_string())
