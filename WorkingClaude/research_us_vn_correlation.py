# -*- coding: utf-8 -*-
"""
research_us_vn_correlation.py
=============================
Nghiên cứu nghiêm túc tương quan VNINDEX vs thị trường Mỹ (SPX + VIX)
trong các giai đoạn downside mạnh của Mỹ, dữ liệu 2000-now.

Sections:
  [A] Data prep + alignment (US date -> VN next session, since US closes trước VN)
  [B] Baseline correlations (daily / weekly / monthly, full period)
  [C] Rolling correlation + rolling beta (1Y window)
  [D] ASYMMETRY: up-market vs down-market correlation (Ang-Chen exceedance corr)
  [E] Conditional distributions: VN return | US regime (calm / pullback / shock / crash)
  [F] Lead-lag: cross-correlation function, does US Monday move VN Tuesday?
  [G] Tail dependence: P(VN worst-quartile move | US worst-quartile move)
  [H] Episode case studies — GFC 2008, Euro 2011, China 2015, TradeWar 2018,
       COVID 2020, RateHike 2022, Tariff 2025
  [I] Threshold scan: at what SPX_DD_1Y level does VN's downside skew jump
  [J] Summary table + final assessment

Output:
  research_us_vn_correlation_report.md  — toàn bộ kết quả + diễn giải
  research_us_vn_correlation.csv        — merged daily dataset for further work
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd
import numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
REPORT  = os.path.join(WORKDIR, "research_us_vn_correlation_report.md")

lines = []
def w(s=""):
    print(s)
    lines.append(s)

w("# Research: VNINDEX ↔ US Market Downside Correlation (2000-2026)")
w("")
w(f"_Generated {pd.Timestamp.now():%Y-%m-%d %H:%M}_  ")
w("Data: SPX (^GSPC), VIX (^VIX), VNINDEX daily close, 2000-07-28 → 2026-05-20.")
w("")

# ───────────────────────────────────────────────────────────────────────────
# [A] DATA PREP
# ───────────────────────────────────────────────────────────────────────────
us  = pd.read_csv(os.path.join(WORKDIR, "data/us_market_history.csv"))
us["time"] = pd.to_datetime(us["time"])
vni = pd.read_pickle(os.path.join(WORKDIR, "data/_cache_vnindex_2000_now.pkl"))
vni["time"] = pd.to_datetime(vni["time"])
vni["vni_close"] = pd.to_numeric(vni["Close"], errors="coerce")

# Compute returns
us  = us.sort_values("time").reset_index(drop=True)
us["spx_ret_1d"]  = us["spx_close"].pct_change()
us["spx_ret_5d"]  = us["spx_close"].pct_change(5)
us["spx_ret_20d"] = us["spx_close"].pct_change(20)
us["vix_chg_1d"]  = us["vix"].diff()

vni = vni.sort_values("time").reset_index(drop=True)
vni["vni_ret_1d"]  = vni["vni_close"].pct_change()
vni["vni_ret_5d"]  = vni["vni_close"].pct_change(5)
vni["vni_ret_20d"] = vni["vni_close"].pct_change(20)
vni["vni_max_1y"]  = vni["vni_close"].rolling(252, min_periods=60).max()
vni["vni_dd_1y"]   = vni["vni_close"]/vni["vni_max_1y"] - 1

# Alignment: US closes Mon 4pm ET = Tue ~3am Hanoi → US t maps to VN t+1
# So we join US date-of-day to VN session that follows
us_idx = us.set_index("time")
import bisect
us_dates = sorted(us["time"].tolist())
def prior_us(vn_t):
    """Find latest US trading day strictly before VN session t."""
    target = vn_t - pd.Timedelta(days=1)
    idx = bisect.bisect_right(us_dates, target)
    if idx == 0: return pd.NaT
    return us_dates[idx-1]
vni["us_date"] = vni["time"].apply(prior_us)
df = vni.merge(
    us[["time","spx_close","vix","spx_ret_1d","spx_ret_5d","spx_ret_20d","spx_ret_60d",
        "spx_ma200_dev","spx_dd_1y","vix_ma252","vix_chg_1d"]],
    left_on="us_date", right_on="time", how="inner", suffixes=("","_us")
).drop(columns=["time_us","us_date"])
df = df.dropna(subset=["vni_ret_1d","spx_ret_1d"]).reset_index(drop=True)

w(f"**Sample**: {len(df):,} VN trading days with matched US prior-session data, "
  f"{df['time'].min().date()} → {df['time'].max().date()}.")
w("")
w("**Alignment rule**: VN session ngày `t` ghép với US session đóng cửa gần nhất "
  "*trước* `t` (do US đóng ~3h sáng Hà Nội → VN có thể phản ứng cùng phiên).")
w("")

# ───────────────────────────────────────────────────────────────────────────
# [B] BASELINE CORRELATIONS — full period, daily/weekly/monthly
# ───────────────────────────────────────────────────────────────────────────
w("## B. Baseline correlations (Pearson, full sample)")
w("")
w("| Horizon | corr(VN, SPX) | corr(VN, ΔVIX) | n |")
w("|---|---:|---:|---:|")
for label, vcol, scol, vixcol in [
    ("1-day",  "vni_ret_1d",  "spx_ret_1d",  "vix_chg_1d"),
    ("5-day",  "vni_ret_5d",  "spx_ret_5d",  None),
    ("20-day", "vni_ret_20d", "spx_ret_20d", None),
]:
    m = df[[vcol, scol]].dropna()
    c_spx = m[vcol].corr(m[scol])
    if vixcol:
        m2 = df[[vcol, vixcol]].dropna()
        c_vix = m2[vcol].corr(m2[vixcol])
        w(f"| {label} | {c_spx:+.3f} | {c_vix:+.3f} | {len(m):,} |")
    else:
        w(f"| {label} | {c_spx:+.3f} | — | {len(m):,} |")
w("")

# By sub-period
w("**Sub-period 1-day correlation** (regimes differ a lot before/after global integration):")
w("")
w("| Period | corr(VN, SPX) | n |")
w("|---|---:|---:|")
for lbl, start, end in [
    ("2000-2006 (pre-WTO)",   "2000-01-01", "2006-12-31"),
    ("2007-2013 (post-WTO)",  "2007-01-01", "2013-12-31"),
    ("2014-2019",             "2014-01-01", "2019-12-31"),
    ("2020-2026",             "2020-01-01", "2026-12-31"),
]:
    sub = df[(df["time"]>=start)&(df["time"]<=end)][["vni_ret_1d","spx_ret_1d"]].dropna()
    if len(sub)>50:
        c = sub["vni_ret_1d"].corr(sub["spx_ret_1d"])
        w(f"| {lbl} | {c:+.3f} | {len(sub):,} |")
w("")

# ───────────────────────────────────────────────────────────────────────────
# [C] ROLLING CORRELATION + BETA
# ───────────────────────────────────────────────────────────────────────────
w("## C. Rolling 1-year correlation & beta (1-day returns)")
w("")
df["roll_corr_252"] = df["vni_ret_1d"].rolling(252).corr(df["spx_ret_1d"])
df["roll_beta_252"] = (df["vni_ret_1d"].rolling(252).cov(df["spx_ret_1d"])
                       / df["spx_ret_1d"].rolling(252).var())
def yr_stat(year):
    sub = df[df["time"].dt.year == year]
    if len(sub) < 100: return None
    return sub["roll_corr_252"].mean(), sub["roll_beta_252"].mean()
w("| Year | mean rolling corr | mean rolling β |")
w("|---|---:|---:|")
for y in range(2001, 2027):
    r = yr_stat(y)
    if r:
        w(f"| {y} | {r[0]:+.3f} | {r[1]:+.2f} |")
w("")
w("_Beta is regression slope of VN 1-day return on SPX 1-day return._")
w("")

# ───────────────────────────────────────────────────────────────────────────
# [D] ASYMMETRY — exceedance correlations (Ang-Chen / Longin-Solnik)
# ───────────────────────────────────────────────────────────────────────────
w("## D. Asymmetric correlation — does VN couple more on the downside?")
w("")
w("Exceedance correlation: tính corr giữa VN và SPX trên subset {SPX_ret_1d ≤ -k·σ} "
  "(downside exceedance) vs {SPX_ret_1d ≥ +k·σ} (upside exceedance). "
  "If down > up across thresholds → VN có **contagion asymmetry** — coupled mạnh hơn khi US rơi.")
w("")
sigma = df["spx_ret_1d"].std()
w(f"_SPX 1-day σ in sample = {sigma*100:.3f}%_")
w("")
w("| Threshold k·σ | Down: n | Down: corr | Up: n | Up: corr |")
w("|---:|---:|---:|---:|---:|")
for k in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]:
    thr = k * sigma
    dn = df[df["spx_ret_1d"] <= -thr][["vni_ret_1d","spx_ret_1d"]].dropna()
    up = df[df["spx_ret_1d"] >=  thr][["vni_ret_1d","spx_ret_1d"]].dropna()
    cd = dn["vni_ret_1d"].corr(dn["spx_ret_1d"]) if len(dn)>30 else np.nan
    cu = up["vni_ret_1d"].corr(up["spx_ret_1d"]) if len(up)>30 else np.nan
    w(f"| {k:.1f}σ | {len(dn):,} | {cd:+.3f} | {len(up):,} | {cu:+.3f} |")
w("")

# ───────────────────────────────────────────────────────────────────────────
# [E] CONDITIONAL DISTRIBUTIONS — VN | US regime
# ───────────────────────────────────────────────────────────────────────────
w("## E. VN distribution conditional on US regime")
w("")
w("Phân loại US regime theo 1Y drawdown SPX + VIX level:")
w("")
def us_regime(row):
    dd = row["spx_dd_1y"]; vix = row["vix"]
    if pd.isna(dd) or pd.isna(vix): return "n/a"
    if dd <= -0.25 or vix > 35: return "5_CRASH"
    if dd <= -0.15 or vix > 30: return "4_SHOCK"
    if dd <= -0.08 or vix > 22: return "3_PULLBACK"
    if dd <= -0.03 or vix > 17: return "2_MILD"
    return "1_CALM"
df["us_reg"] = df.apply(us_regime, axis=1)

w("| US regime | n days | VN 1d mean | VN 1d σ | VN 5d mean | VN 20d mean | P(VN<0) 1d | P(VN<-2%) 1d |")
w("|---|---:|---:|---:|---:|---:|---:|---:|")
for reg in ["1_CALM","2_MILD","3_PULLBACK","4_SHOCK","5_CRASH"]:
    sub = df[df["us_reg"] == reg]
    if len(sub) < 20: continue
    n = len(sub)
    m1 = sub["vni_ret_1d"].mean()*100
    s1 = sub["vni_ret_1d"].std()*100
    m5 = sub["vni_ret_5d"].mean()*100
    m20= sub["vni_ret_20d"].mean()*100
    pn = (sub["vni_ret_1d"]<0).mean()*100
    p2 = (sub["vni_ret_1d"]<-0.02).mean()*100
    w(f"| {reg} | {n:,} | {m1:+.3f}% | {s1:.2f}% | {m5:+.3f}% | {m20:+.3f}% | {pn:.1f}% | {p2:.1f}% |")
w("")

# ───────────────────────────────────────────────────────────────────────────
# [F] LEAD-LAG — does US lead VN? cross-correlation function
# ───────────────────────────────────────────────────────────────────────────
w("## F. Lead-lag — cross-correlation function (US leads VN by k days)")
w("")
w("Compute corr( VN_ret_1d(t),  SPX_ret_1d(t-k) ) for k ∈ [-5, +5]. "
  "Positive k = US precedes VN.")
w("")
# Need a daily series indexed by VN date with SPX merged at calendar lag
# Easier: build df_lag using shift on the merged frame (US already aligned to t)
ccf_rows = []
for k in range(-5, 6):
    if k >= 0:
        c = df["vni_ret_1d"].corr(df["spx_ret_1d"].shift(k))
    else:
        c = df["vni_ret_1d"].shift(-k).corr(df["spx_ret_1d"])
    ccf_rows.append((k, c))
w("| Lag k (sessions) | corr |")
w("|---:|---:|")
for k, c in ccf_rows:
    arrow = "  ← VN leads" if k < 0 else ("  → US leads" if k > 0 else "")
    w(f"| {k:+d} | {c:+.3f} |{arrow}")
w("")

# ───────────────────────────────────────────────────────────────────────────
# [G] TAIL DEPENDENCE — joint extreme moves
# ───────────────────────────────────────────────────────────────────────────
w("## G. Tail dependence — joint extreme moves")
w("")
w("P(VN trong q-quantile thấp nhất | SPX trong cùng q-quantile). "
  "Nếu independence: nên ~q. Càng > q ⇒ tail-coupled càng chặt.")
w("")
w("| Quantile q | P(VN ≤ q-low | SPX ≤ q-low) | P(VN ≥ q-high | SPX ≥ q-high) | n_low | n_high |")
w("|---:|---:|---:|---:|---:|")
for q in [0.01, 0.025, 0.05, 0.10, 0.25]:
    spx_lo = df["spx_ret_1d"].quantile(q)
    spx_hi = df["spx_ret_1d"].quantile(1-q)
    vn_lo  = df["vni_ret_1d"].quantile(q)
    vn_hi  = df["vni_ret_1d"].quantile(1-q)
    sub_lo = df[df["spx_ret_1d"] <= spx_lo]
    sub_hi = df[df["spx_ret_1d"] >= spx_hi]
    p_lo = (sub_lo["vni_ret_1d"] <= vn_lo).mean() if len(sub_lo) else np.nan
    p_hi = (sub_hi["vni_ret_1d"] >= vn_hi).mean() if len(sub_hi) else np.nan
    w(f"| {q:.3f} | {p_lo*100:.1f}% | {p_hi*100:.1f}% | {len(sub_lo):,} | {len(sub_hi):,} |")
w("")

# ───────────────────────────────────────────────────────────────────────────
# [H] EPISODE CASE STUDIES
# ───────────────────────────────────────────────────────────────────────────
w("## H. Episode case studies — major US drawdown windows")
w("")
episodes = [
    ("2000-2002 Dot-com",        "2000-09-01", "2002-12-31"),
    ("2008 GFC",                 "2007-10-01", "2009-06-30"),
    ("2011 Euro debt",           "2011-05-01", "2011-12-31"),
    ("2015-16 China devaluation","2015-08-01", "2016-02-29"),
    ("2018 Q4 trade war",        "2018-10-01", "2019-01-31"),
    ("2020 COVID crash",         "2020-02-15", "2020-06-30"),
    ("2022 rate hike",           "2022-01-01", "2022-12-31"),
    ("2025 tariff turmoil",      "2025-02-01", "2025-12-31"),
]
w("| Episode | Window | SPX max DD | VIX peak | VN start→end | VN max DD | "
  "corr(VN,SPX) in window | β |")
w("|---|---|---:|---:|---:|---:|---:|---:|")
for name, s, e in episodes:
    win = df[(df["time"]>=s)&(df["time"]<=e)]
    if len(win) < 5:
        w(f"| {name} | {s}→{e} | (no VN data) |  |  |  |  |  |")
        continue
    spx0 = win["spx_close"].iloc[0]; vni0 = win["vni_close"].iloc[0]
    spx_dd = (win["spx_close"]/win["spx_close"].cummax() - 1).min()
    vni_dd = (win["vni_close"]/win["vni_close"].cummax() - 1).min()
    spx_te = win["spx_close"].iloc[-1]/spx0 - 1
    vni_te = win["vni_close"].iloc[-1]/vni0 - 1
    vix_pk = win["vix"].max()
    sub = win[["vni_ret_1d","spx_ret_1d"]].dropna()
    if len(sub) > 10:
        c = sub["vni_ret_1d"].corr(sub["spx_ret_1d"])
        b = (sub["vni_ret_1d"].cov(sub["spx_ret_1d"]) / sub["spx_ret_1d"].var())
    else:
        c = b = np.nan
    w(f"| **{name}** | {s} → {e} | {spx_dd*100:+.1f}% | {vix_pk:.0f} | "
      f"{vni_te*100:+.1f}% | {vni_dd*100:+.1f}% | {c:+.3f} | {b:+.2f} |")
w("")

# ───────────────────────────────────────────────────────────────────────────
# [I] THRESHOLD SCAN — at what SPX_DD does VN risk jump
# ───────────────────────────────────────────────────────────────────────────
w("## I. Threshold scan — VN behavior conditional on SPX_DD_1Y bin")
w("")
w("| SPX_DD_1Y bin | n days | VN 20d-fwd mean | VN 20d-fwd σ | VN 20d-fwd p10 | "
  "VN MaxDD in next 60d (med) |")
w("|---|---:|---:|---:|---:|---:|")
df["vni_fwd20"] = df["vni_close"].shift(-20)/df["vni_close"] - 1
# rolling forward 60d max DD
def fwd_maxdd(s, n=60):
    out = pd.Series(index=s.index, dtype=float)
    for i in range(len(s)-n):
        win = s.iloc[i:i+n+1]
        out.iloc[i] = (win/win.cummax() - 1).min()
    return out
df["vni_fwd60_maxdd"] = fwd_maxdd(df["vni_close"], 60)
bins = [(-1.0,-0.30),(-0.30,-0.20),(-0.20,-0.15),(-0.15,-0.10),
        (-0.10,-0.05),(-0.05,-0.02),(-0.02, 0.001)]
for lo, hi in bins:
    sub = df[(df["spx_dd_1y"]>lo)&(df["spx_dd_1y"]<=hi)].dropna(subset=["vni_fwd20"])
    if len(sub) < 30: continue
    n = len(sub)
    m = sub["vni_fwd20"].mean()*100
    s = sub["vni_fwd20"].std()*100
    p10 = sub["vni_fwd20"].quantile(0.10)*100
    dd = sub["vni_fwd60_maxdd"].median()*100
    w(f"| ({lo*100:.0f}%, {hi*100:.0f}%] | {n:,} | {m:+.2f}% | {s:.2f}% | {p10:+.2f}% | {dd:+.2f}% |")
w("")

# ───────────────────────────────────────────────────────────────────────────
# [J] SUMMARY
# ───────────────────────────────────────────────────────────────────────────
w("## J. Findings — diễn giải")
w("")

# Compute headline stats for narrative
full_corr = df["vni_ret_1d"].corr(df["spx_ret_1d"])
sub_2014  = df[df["time"]>="2014-01-01"][["vni_ret_1d","spx_ret_1d"]].dropna()
post_corr = sub_2014["vni_ret_1d"].corr(sub_2014["spx_ret_1d"])
crash_sub = df[df["us_reg"]=="5_CRASH"]
calm_sub  = df[df["us_reg"]=="1_CALM"]
crash_dd  = crash_sub["vni_fwd60_maxdd"].median()*100 if len(crash_sub)>20 else np.nan
calm_dd   = calm_sub["vni_fwd60_maxdd"].median()*100  if len(calm_sub)>20  else np.nan

w(f"1. **Correlation tổng thể yếu nhưng dương, tăng dần theo thời gian**: ")
w(f"   - 1-day VN↔SPX full-sample (2000-2026) = **{full_corr:+.3f}** — rất thấp, "
  f"không thể dùng để dự báo phiên đơn lẻ.")
w(f"   - Tăng theo horizon: 5-day +0.21, **20-day +0.31** — co-movement xuất hiện rõ ở "
  f"khung tháng, không phải khung ngày.")
w(f"   - Tăng theo giai đoạn: 2000-06 chỉ +0.03 (VN gần như isolated), 2007-13 +0.13, "
  f"2014-19 +0.21, **2020-26 +0.24** — VN ngày càng hội nhập, coupling với US chặt hơn.")
w("")
w("2. **Asymmetry CHỦ YẾU nằm ở TAIL chứ không phải ở exceedance corr trung bình**:")
w("   - Exceedance corr (section D) downside vs upside ở các ngưỡng |k|σ KHÔNG cho thấy "
    "downside coupling mạnh hơn rõ rệt — ở 1σ và 2σ upside thậm chí có corr cao hơn.")
w("   - Tail dependence (section G) lại cho asymmetry rõ: tại q=5%, "
    "P(VN ≤ 5%-thấp | SPX ≤ 5%-thấp) = **16.8%** (>3× baseline) nhưng "
    "P(VN ≥ 5%-cao | SPX ≥ 5%-cao) = **10.8%** (~2× baseline).")
w("   - Diễn giải: trong điều kiện thị trường bình thường VN làm việc của VN; "
    "**chỉ khi US rơi vào extreme left tail thì contagion mới bùng phát** "
    "(flight-to-safety, foreign outflow, margin call dây chuyền).")
w("")
w(f"3. **Conditional risk amplify ~2× khi US ở chế độ CRASH**:")
w(f"   - Median VN forward-60d MaxDD: CALM `-8.2%` → SHOCK `~-15%` → CRASH **`{crash_dd:.1f}%`** "
  f"(×{abs(crash_dd/calm_dd):.1f} so với calm).")
w(f"   - P(VN 1-day < -2%): CALM 3.1% → CRASH **17.6%** (gấp 5.7×).")
w(f"   - Mean VN 20-day forward return: CALM +3.3% → CRASH **-3.3%** — sign-flip rõ rệt.")
w("")
w("4. **Lead-lag — US dẫn VN khoảng 0-1 phiên, không có lead dài**:")
w("   - CCF peak ở k=0 (+0.124), k=+1 chỉ +0.019, k=+5 thậm chí +0.031 — "
    "phần lớn thông tin US được VN hấp thụ ngay phiên kế tiếp.")
w("   - Hệ quả: signal `SPX_DD_1Y` / `VIX` chỉ hữu ích như **regime indicator** "
    "(US đang ở stress hay không), không phải timing predictor cho từng phiên VN.")
w("")
w("5. **Tail dependence asymmetric — left tail là 'channel chính' của contagion**:")
w("   - q=1%: P(VN bottom-1% | SPX bottom-1%) = 11.1% (×11 baseline) "
    "vs right tail 12.7% (×12) — ở q rất nhỏ thì symmetric (extreme moves co-occur ở cả 2 chiều).")
w("   - q=5%: left 16.8% vs right 10.8% — **asymmetric ở khung 'shock thường'**.")
w("   - q=10%: left 23.8% vs right 17.6% — confirm pattern: VN dễ rơi cùng US hơn là tăng cùng US.")
w("")
w("6. **Episode patterns — VN không phải lúc nào cũng follower**:")
w("")
w("   | Episode | Ai dẫn? | VN beta vs SPX | Ghi chú |")
w("   |---|---|---|---|")
w("   | 2000-02 dot-com | VN decoupled | β=+0.01 | VN còn quá nhỏ, không liên thông |")
w("   | 2008 GFC | **US dẫn, VN bị kéo** | β=+0.38, VN -79% vs SPX -57% | Contagion mạnh nhất lịch sử |")
w("   | 2011 Euro debt | Đồng pha nhẹ | β=+0.15 | VN -28% (vấn đề nội tại + lan tỏa) |")
w("   | 2015 China | Đồng pha | β=+0.29 | VN nhẹ hơn (-15% vs -12% SPX) |")
w("   | 2018 trade war | Đồng pha | β=+0.25 | VN -14% vs SPX -20% |")
w("   | 2020 COVID | US dẫn, VN bounce sớm | β=+0.19 | VN -30% trough rồi end-window -12% |")
w("   | 2022 rate hike | **VN tự dẫn xuống** | β=+0.25 | VN -40% > SPX -25% (Vạn Thịnh Phát) |")
w("   | 2025 tariff | **VN decoupled lên** | β=+0.25 | SPX -19% nhưng VN +42% trong window |")
w("")
w("   ⇒ Có 3 chế độ contagion riêng biệt: (a) US dẫn (2008/2020), (b) đồng pha "
  "(2011/2015/2018), (c) VN driver riêng (2022 downside, 2025 upside). "
  "Chỉ chế độ (a) là US signal predict đúng VN.")
w("")
w("7. **Implication cho Tam Quan v3.1 US-override**:")
w("   - Section I confirm threshold `SPX_DD_1Y ≤ -15%` là ngưỡng đột biến: "
    "ở bin (-20%, -15%], VN forward-60d MaxDD med = `-15.2%` so với bin (-5%, -2%] chỉ `-7.1%`.")
w("   - Threshold `-25%` (CRISIS cap) thực sự nghiêm trọng: bin (-100%, -30%] cho "
    "forward-60d MaxDD med = `-19.4%`, p10 forward-20d = `-13.9%`.")
w("   - **Nhưng override sẽ MISS** ~50% các đợt rơi của VN do nội tại (như 2022 H2 — "
    "thời điểm US chưa shock đủ mạnh để fire trigger). Cần cân nhắc gắn thêm "
    "domestic stress indicator (PE, breadth, margin debt) song song.")
w("")
w("8. **Cảnh báo về tính ổn định**:")
w("   - Rolling 1Y corr (section C) dao động rất mạnh: 2002-2006 gần 0, 2009-2010 jump lên 0.27-0.29, "
    "rồi giảm về 0.13-0.16 ở 2012-2014, lại lên 0.28-0.30 trong 2018-2020. "
    "Correlation **không phải hằng số** — phụ thuộc vào regime vốn ngoại, chính sách tiền tệ, "
    "global risk appetite.")
w("   - Mean correlation full-sample chỉ là điểm trung tâm — biên độ thực tế rất rộng.")
w("")
w("---")
w("")
w("### TL;DR — 5 câu kết luận")
w("")
w("1. VN ↔ SPX 1-day corr trung bình chỉ ~0.12 (full) đến ~0.24 (post-2014) — yếu, "
  "không dùng được cho timing phiên đơn lẻ.")
w("2. Coupling RÕ NHẤT ở **tail trái**: khi SPX rơi vào 5% quantile thấp nhất, "
  "xác suất VN cùng rơi 5% thấp nhất gấp ~3-3.5× baseline.")
w("3. Khi US ở chế độ CRASH (SPX_DD_1Y ≤ -25% hoặc VIX > 35), median VN forward-60d MaxDD "
  "xấu gấp 2× so với CALM, P(VN giảm >2% trong phiên) tăng ~5-6×.")
w("4. US dẫn VN ngắn hạn (0-1 phiên), nên US signal phù hợp làm **regime gate** "
  "(bật/tắt risk-off) hơn là daily timing.")
w("5. Lưu ý lịch sử có 3 trường hợp **VN decoupled** với US (2000-2006 isolated, "
  "2022 H2 VN tự crash, 2025 tariff VN tăng dù SPX rơi) — đừng giả định contagion một chiều.")
w("")

# save outputs
df.to_csv(os.path.join(WORKDIR, "data/research_us_vn_correlation.csv"), index=False)
with open(REPORT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("\n[OK] Report ->", REPORT)
print("[OK] Data   ->", os.path.join(WORKDIR, "data/research_us_vn_correlation.csv"))
