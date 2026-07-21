# -*- coding: utf-8 -*-
"""
lag_sector_split_20260721.py — job Taylor_20260721_133858

Kiểm chứng giả thuyết user: "surprise của nhóm chứng khoán = xổ số, PEAD yếu hơn
nhóm sản xuất bền vững".

Phương pháp = mirror đúng job Taylor_20260721_130404:
  - event qualify LAG: NP_R>=15 & prior_n_good>=4 & pa_HL3>=5 (lag_live_schedule)
  - entry T+5 -> exit T+30 (post_ret trong earnings_events_classified.csv)
  - excess = post_ret - VNINDEX return CÙNG cửa sổ (+5 -> +30 phiên từ Release_Date)
  - 2014-01-01 -> nay
Tách nhóm theo ICB_Code (point-in-time không có -> dùng ICB hiện tại, nêu rõ hạn chế).
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
# cache local đang verified=false (07-20) -> đọc BQ live cho chắc
os.environ.pop("BQ_LOCAL_CACHE", None)

from lag_live_schedule import live_lag_candidates
from simulate_holistic_nav import bq


# ── 1. ICB map ────────────────────────────────────────────────────────────
icb = bq("""SELECT t.ticker, ANY_VALUE(t.ICB_Code) AS icb
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL GROUP BY t.ticker""")
icb["icb"] = icb["icb"].astype(int)
icb_map = dict(zip(icb["ticker"], icb["icb"]))
print(f"[icb] {len(icb_map)} tickers có ICB_Code")

# xác minh: mã chứng khoán nổi tiếng mang code nào
KNOWN_BROKERS = ["SSI", "VND", "HCM", "VCI", "MBS", "SHS", "BSI", "FTS", "CTS",
                 "VIX", "AGR", "BVS", "TVS", "ORS", "IVS", "APS", "PSI", "VDS"]
print("[verify] ICB của các CTCK đã biết:")
for tk in KNOWN_BROKERS:
    print(f"   {tk}: {icb_map.get(tk)}")

BROKER_CODES = sorted({icb_map[t] for t in KNOWN_BROKERS if t in icb_map})
print(f"[verify] => BROKER_CODES = {BROKER_CODES}")

# nhóm sản xuất/công nghiệp: ICB industry 1000 Basic Materials, 2000 Industrials,
# 3000 Consumer Goods (TRC=1353, TMG=1757 nằm trong 1000)
def group_of(tk):
    c = icb_map.get(tk)
    if c is None:
        return "UNKNOWN"
    if c in BROKER_CODES:
        return "BROKER"
    ind = c // 1000
    if ind in (1, 2, 3):
        return "MANUF"
    return "OTHER"


# ── 2. events + qualify ───────────────────────────────────────────────────
cand = live_lag_candidates(workdir=WORKDIR)
ev = pd.read_csv(os.path.join(WORKDIR, "data/earnings_events_classified.csv"),
                 parse_dates=["Release_Date"])
df = cand.merge(ev[["ticker", "quarter", "Release_Date", "post_ret"]],
                on=["ticker", "quarter", "Release_Date"], how="inner")
df = df[df["qualify"] & df["post_ret"].notna()].copy()
df = df[df["Release_Date"] >= "2014-01-01"].copy()
print(f"\n[events] qualify & có post_ret & >=2014: N={len(df)}")


# ── 3. VNINDEX benchmark cùng cửa sổ ──────────────────────────────────────
vni = bq("""SELECT t.time, ANY_VALUE(t.VNINDEX) AS vni
FROM tav2_bq.ticker AS t WHERE t.VNINDEX IS NOT NULL AND t.time >= '2013-01-01'
GROUP BY t.time ORDER BY t.time""")
vni["time"] = pd.to_datetime(vni["time"])
vdates = vni["time"].values.astype("datetime64[ns]")
vvals = vni["vni"].to_numpy(float)


def vni_off(ref, off):
    pos = np.searchsorted(vdates, np.datetime64(ref), side="right") - 1
    t = pos + off
    if pos < 0 or t < 0 or t >= len(vvals):
        return np.nan
    return vvals[t]


b5 = np.array([vni_off(d, 5) for d in df["Release_Date"]])
b30 = np.array([vni_off(d, 30) for d in df["Release_Date"]])
df["bench_ret"] = (b30 / b5 - 1) * 100
df = df[df["bench_ret"].notna()].copy()
df["excess"] = df["post_ret"] - df["bench_ret"]
df["grp"] = df["ticker"].map(group_of)

print(f"[events] sau khi ghép benchmark: N={len(df)}")
print(f"[sanity] excess toàn bộ: mean={df['excess'].mean():.2f}%  "
      f"t={stats.ttest_1samp(df['excess'], 0).statistic:.2f}  N={len(df)}")


# ── 4. thống kê theo nhóm ─────────────────────────────────────────────────
def block(sub, name):
    x = sub["excess"].to_numpy(float)
    if len(x) < 2:
        return dict(grp=name, N=len(x))
    t = stats.ttest_1samp(x, 0)
    return dict(grp=name, N=len(x), mean=x.mean(), med=np.median(x),
                sd=x.std(ddof=1), t=t.statistic, p=t.pvalue,
                win=(x > 0).mean() * 100, ntk=sub["ticker"].nunique())


print("\n" + "=" * 92)
print("PHẦN 2 — EXCESS RETURN THEO NHÓM NGÀNH (2014 -> nay, qualify LAG, T+5->T+30)")
print("=" * 92)
rows = [block(df[df["grp"] == g], g) for g in ["BROKER", "MANUF", "OTHER", "UNKNOWN"]]
rows.append(block(df, "ALL"))
res = pd.DataFrame(rows)
print(res.to_string(index=False, float_format=lambda v: f"{v:.3f}"))

# Welch: broker vs manuf, broker vs (manuf+other)
bk = df[df["grp"] == "BROKER"]["excess"].to_numpy(float)
mf = df[df["grp"] == "MANUF"]["excess"].to_numpy(float)
nb = df[df["grp"].isin(["MANUF", "OTHER"])]["excess"].to_numpy(float)
if len(bk) > 1:
    w1 = stats.ttest_ind(bk, mf, equal_var=False)
    w2 = stats.ttest_ind(bk, nb, equal_var=False)
    print(f"\n[Welch] BROKER vs MANUF : diff={bk.mean()-mf.mean():+.2f}pp  "
          f"t={w1.statistic:.2f}  p={w1.pvalue:.4f}")
    print(f"[Welch] BROKER vs NON-BROKER: diff={bk.mean()-nb.mean():+.2f}pp  "
          f"t={w2.statistic:.2f}  p={w2.pvalue:.4f}")
    # power: MDE 2-sided 80%
    from math import sqrt
    sp = np.sqrt((bk.var(ddof=1) / len(bk)) + (nb.var(ddof=1) / len(nb)))
    print(f"[power] SE của chênh lệch = {sp:.2f}pp -> MDE(80%,2-sided) ≈ {2.8*sp:.2f}pp")

# theo tier
print("\n-- theo tier --")
for tier in ["LAG_HI", "LAG_LO"]:
    sub = df[df["tier"] == tier]
    r = [block(sub[sub["grp"] == g], f"{tier}/{g}") for g in ["BROKER", "MANUF", "OTHER"]]
    print(pd.DataFrame(r).to_string(index=False, float_format=lambda v: f"{v:.3f}"))

# IS/OOS
print("\n-- IS 2014-2019 / OOS 2020+ --")
for lbl, msk in [("IS 2014-19", df["Release_Date"] < "2020-01-01"),
                 ("OOS 2020+", df["Release_Date"] >= "2020-01-01")]:
    sub = df[msk]
    r = [block(sub[sub["grp"] == g], f"{lbl}/{g}") for g in ["BROKER", "MANUF", "OTHER"]]
    print(pd.DataFrame(r).to_string(index=False, float_format=lambda v: f"{v:.3f}"))


# ── 5. PHẦN 3 — IC của magnitude surprise ─────────────────────────────────
print("\n" + "=" * 92)
print("PHẦN 3 — SPEARMAN IC: surprise magnitude vs excess return")
print("=" * 92)
# universe rộng hơn cho IC: mọi event NP_R>=15 có post_ret (không cần prior gate)
allev = cand.merge(ev[["ticker", "quarter", "Release_Date", "post_ret"]],
                   on=["ticker", "quarter", "Release_Date"], how="inner")
allev = allev[(allev["NP_R"] >= 15) & allev["post_ret"].notna()
              & (allev["Release_Date"] >= "2014-01-01")].copy()
b5a = np.array([vni_off(d, 5) for d in allev["Release_Date"]])
b30a = np.array([vni_off(d, 30) for d in allev["Release_Date"]])
allev["excess"] = allev["post_ret"] - (b30a / b5a - 1) * 100
allev = allev[allev["excess"].notna()].copy()
allev["grp"] = allev["ticker"].map(group_of)

for label, d_ in [("qualify-only", df), ("all NP_R>=15", allev)]:
    print(f"\n[{label}]")
    for g in ["BROKER", "MANUF", "OTHER", "ALL"]:
        sub = d_ if g == "ALL" else d_[d_["grp"] == g]
        if len(sub) < 10:
            print(f"  {g:7s} N={len(sub):5d}  (quá mỏng)")
            continue
        for xcol in ["surprise_B_MA", "NP_R"]:
            ic, p = stats.spearmanr(sub[xcol], sub["excess"])
            print(f"  {g:7s} N={len(sub):5d}  IC({xcol:13s})={ic:+.4f}  p={p:.4f}")

df.to_csv(os.path.join(WORKDIR, "mike/agents/Taylor/data_lag_sector_split_20260721.csv"),
          index=False)
print("\n[saved] mike/agents/Taylor/data_lag_sector_split_20260721.csv")
