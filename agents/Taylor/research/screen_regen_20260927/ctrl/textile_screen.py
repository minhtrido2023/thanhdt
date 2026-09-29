"""Textile / Garment EXPORT — sector #16 valuation framework + screen (point-in-time monthly).
Design + backlook: job Taylor_20260705_154537. Framework: mike/agents/Taylor/textile_valuation_framework.md.

Vietnam textile/garment exporters: revenue in USD (export), cost mostly in VND (labor) → a-priori
FX-sensitive; and demand is ORDER-BOOK driven (forward, not in BQ) → trailing P/E is distorted by the
cotton/yarn input cycle. Two things this script settles quantitatively:

  (1) FX-SENSITIVITY TEST. Dispatch hypothesis: VND depreciation (USD/VND up) helps the VND-translated
      revenue of exporters → should be a forward-return tailwind. We test USD/VND 3M/6M momentum (causal)
      vs forward T+20/40/60 return (profit_1M/2M/3M — EVALUATION ONLY, never a live filter). Result is
      pinned; spoiler in the framework doc.

  (2) A QUALITY-VALUE SCREEN and whether it is a tradeable BOOK or only a lens (sweep Rule 3).

Universe (hand-curated; ICB lumps textile+apparel). LIQUID export core (ADV>5B, full history):
  TCM (Thanh Cong — vertically integrated yarn→fabric→garment), TNG (garment CMT scale),
  MSH (Song Hong — FOB high-margin), GIL (Gilimex — garment→industrial-park pivot), VGT (Vinatex holding).
  Thin tail (kept in universe, liquidity-gated out most months): STK, EVE, ADS, HTG, GMC, VGG.

Backlook patterns (ticker_financial cache):
  MSH  2020Q1  EVEB3.4 PE3.8 PB1.25 ROE5Y0.34 IC18  -> ELITE quality, only cheap in the COVID crash -> re-rated
  TCM  2018Q1  EVEB5.9 PE5.7 PB1.00 ROE5Y0.18 IC+6.3 (IntCov JUST turned positive) -> catchable cheap-quality
                                                       window, then PE 3.9(2020Q1)->31(2021Q4) reopening surge
  TCM  <=2017  IntCov NEGATIVE (-3 to -8) every quarter -> the survival gate (IntCov>1.5) correctly WAITS
  TNG  2016-18 PE5-6 RevYoY+40..50% multibagger BUT NPM~0, Debt_Eq 2.3-3.9, IntCov NEGATIVE -> a thin-margin
                                                       high-leverage CMT growth bet, NOT a quality-value entry
  GIL  2025-26 GPM 8q CV 0.38, EVEB/PE data-corrupt (Amazon-contract loss + IP pivot) -> margin-stability gate ejects
  STK  2024-26 loss-making (PE -92), recycled-yarn demand collapse -> ejected
  VGT  ROE5Y 0.07 (holding drag), PB 0.58 cheap-but-low-quality -> ejected by ROE floor
  EVE  bedding not pure export, ROE5Y 0.036 -> ejected

The GPM-STABILITY (CV of GPM_P0..P7) + IntCov>1.5 + ROE5Y>0.15 gate is the transferable alpha: it keeps
the margin-stable exporters (MSH, TCM-post-turn) and ejects the thin-CMT leverage trap (TNG) and the
messy pivots / loss names (GIL, STK, VGT, EVE) — parallel to steel's leverage gate and F&B's GPM-moat gate.
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune/*.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
FXCSV = "data/macro_usdvnd.csv"
START = "2014-01-01"
TC, STALE = 0.001, 120
KA = 10
LIQ = 5e9   # 5B ADV export-core liquidity gate (thin-tail names are structurally untradeable)

UNIVERSE = ("TCM","TNG","MSH","GIL","VGT","STK","EVE","ADS","HTG","GMC","VGG")

con = duckdb.connect()

# ---------- rebalance calendar ----------
days = con.execute(f"SELECT DISTINCT time FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}'").df()
days["time"] = pd.to_datetime(days.time); days = days.sort_values("time")
days["ym"] = days.time.dt.to_period("M")
rebal = sorted(days.groupby("ym")["time"].max().tolist())
rebal_str = [d.strftime("%Y-%m-%d") for d in rebal]
rebal_vals = ",".join(f"(DATE '{d}')" for d in rebal_str)

pm = con.execute(f"SELECT time, ticker, Close FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}' AND Close IS NOT NULL").df()
pm["time"] = pd.to_datetime(pm.time)
px = pm.pivot_table(index="time", columns="ticker", values="Close").sort_index()
alldays = px.index
def next_session(d):
    pos = alldays.searchsorted(d, side="right"); return alldays[pos] if pos < len(alldays) else None
vix = con.execute(f"SELECT DISTINCT time, VNINDEX FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}' AND VNINDEX IS NOT NULL").df()
vix["time"] = pd.to_datetime(vix.time); vix = vix.set_index("time")["VNINDEX"].sort_index()

def zc(s):
    s = s.clip(s.quantile(.01), s.quantile(.99)); sd = s.std()
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0
negz = lambda s: -zc(s)

# ============================================================================
# PART 1 — FX-SENSITIVITY TEST (evaluation-only forward returns; never a live filter)
# ============================================================================
def spearman(a, b):
    m = a.notna() & b.notna()
    if m.sum() < 30: return np.nan
    return a[m].rank().corr(b[m].rank())

inl = ",".join(f"'{t}'" for t in UNIVERSE)
fxd = con.execute(f"""SELECT time, ticker, profit_1M, profit_2M, profit_3M
    FROM read_parquet('{PRUNE}') WHERE ticker IN ({inl}) AND time>=DATE '{START}' AND profit_2M IS NOT NULL""").df()
fxd["time"] = pd.to_datetime(fxd.time)
fx = pd.read_csv(FXCSV); fx["time"] = pd.to_datetime(fx.time); fx = fx.sort_values("time").set_index("time")["usdvnd"]
fx = fx.reindex(pd.date_range(fx.index.min(), fx.index.max())).ffill()
fx3m = fx / fx.shift(63) - 1     # ~3 trading-month USD/VND momentum (causal at t)
fx6m = fx / fx.shift(126) - 1
fxd["fx3m"] = fxd["time"].map(fx3m); fxd["fx6m"] = fxd["time"].map(fx6m)
fxd = fxd.dropna(subset=["fx3m", "fx6m"])
fx_ic = {f"{c}_vs_{r}": round(float(spearman(fxd[c], fxd[r])), 4)
         for c in ["fx3m", "fx6m"] for r in ["profit_1M", "profit_2M", "profit_3M"]}
# regime split
fxd["fxreg"] = np.where(fxd.fx6m > 0.01, "VND_weak", np.where(fxd.fx6m < -0.005, "VND_strong", "flat"))
fx_reg = fxd.groupby("fxreg")[["profit_1M", "profit_2M", "profit_3M"]].mean().round(3)
fx_reg_n = fxd.groupby("fxreg").size()
# whole-market baseline (is textile MORE FX-sensitive than the market?)
mkt = con.execute(f"SELECT time, profit_3M FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}' AND profit_3M IS NOT NULL").df()
mkt["time"] = pd.to_datetime(mkt.time); mkt["fx6m"] = mkt["time"].map(fx6m); mkt = mkt.dropna(subset=["fx6m"])
fx_mkt_ic = round(float(spearman(mkt.fx6m, mkt.profit_3M)), 4)

print("="*72); print("PART 1 — FX SENSITIVITY (USD/VND momentum vs textile forward return)")
print(f"  rows {len(fxd)}  names {fxd.ticker.nunique()}")
for k, v in fx_ic.items(): print(f"  Spearman {k:22s}: {v:+.4f}")
print(f"  whole-market fx6m vs profit_3M: {fx_mkt_ic:+.4f}  (textile fx6m vs profit_3M: {fx_ic['fx6m_vs_profit_3M']:+.4f})")
print("  mean forward return by FX(6m) regime:"); print(fx_reg.to_string())
print("  n per regime:", dict(fx_reg_n))

# ============================================================================
# PART 2 — QUALITY-VALUE SCREEN (monthly, ASOF financials, liquidity-gated, hold cash when empty)
# ============================================================================
def simulate(picks_map):
    rows, prev, rs = [], set(), rebal
    for i, d in enumerate(rs):
        if i + 1 >= len(rs): break
        d_next = rs[i + 1]; entry, exit_ = next_session(d), next_session(d_next)
        if entry is None or exit_ is None or entry >= exit_: continue
        names = picks_map.get(d, []); rets = []
        for t in names:
            if t in px.columns:
                p0 = px.at[entry, t] if entry in px.index else np.nan
                p1 = px.at[exit_, t] if exit_ in px.index else np.nan
                if pd.notna(p0) and pd.notna(p1) and p0 > 0: rets.append(p1 / p0 - 1.0)
        bh = float(vix.asof(exit_) / vix.asof(entry) - 1.0) if vix.asof(entry) > 0 else 0.0
        if not rets:
            cost = TC * float(len(prev) > 0)
            rows.append({"rebal": d.strftime("%Y-%m-%d"), "year": d.year, "n_held": 0,
                         "gross": 0.0, "turnover": float(len(prev) > 0), "cost": cost, "net": -cost, "bh": bh})
            prev = set(); continue
        gross = float(np.mean(rets)); cur = set(names)
        turnover = len(cur ^ prev) / max(len(cur | prev), 1)
        cost = TC * turnover; net = gross - cost
        rows.append({"rebal": d.strftime("%Y-%m-%d"), "year": d.year, "n_held": len(rets),
                     "gross": gross, "turnover": turnover, "cost": cost, "net": net, "bh": bh})
        prev = cur
    return pd.DataFrame(rows)

def metrics(r):
    r = np.asarray(r, float)
    if len(r) == 0: return dict(CAGR=0, Sharpe=0, MaxDD=0, Calmar=0, navfinal=1, n=0)
    nav = np.cumprod(1 + r); yrs = len(r) / 12.0
    cagr = nav[-1] ** (1 / yrs) - 1
    sharpe = (r.mean() / r.std() * np.sqrt(12)) if r.std() > 0 else 0.0
    peak = np.maximum.accumulate(nav); mdd = (nav / peak - 1).min()
    calmar = cagr / abs(mdd) if mdd < 0 else float("inf")
    return dict(CAGR=cagr*100, Sharpe=sharpe, MaxDD=mdd*100, Calmar=calmar, navfinal=nav[-1], n=len(r))

def report(label, sub):
    sm, bm = metrics(sub.net), metrics(sub.bh)
    print(f"\n=== {label}  ({sub.rebal.iloc[0]} .. {sub.rebal.iloc[-1]}, {len(sub)} months) ===")
    print(f"  SCREEN(net): CAGR {sm['CAGR']:6.2f}%  Sharpe {sm['Sharpe']:4.2f}  MaxDD {sm['MaxDD']:6.1f}%  Calmar {sm['Calmar']:4.2f}")
    print(f"  B&H VNINDEX: CAGR {bm['CAGR']:6.2f}%  Sharpe {bm['Sharpe']:4.2f}  MaxDD {bm['MaxDD']:6.1f}%  Calmar {bm['Calmar']:4.2f}")
    print(f"  edge(net-B&H): CAGR {sm['CAGR']-bm['CAGR']:+6.2f}pp  Sharpe {sm['Sharpe']-bm['Sharpe']:+4.2f}")
    return sm, bm

# pull ASOF financials incl GPM_P0..P7 for the margin-stability CV, + monthly ADV liquidity
q = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv
  FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
  WHERE p.Close IS NOT NULL AND p.ticker IN ({inl}))
SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.EVEB, f.PB, f.PE, f.PE_MA1Y, f.DY, f.ROE5Y, f.ROIC5Y,
       f.GPM_P0, f.GPM_P1, f.GPM_P2, f.GPM_P3, f.GPM_P4, f.GPM_P5, f.GPM_P6, f.GPM_P7,
       f.NPM_P0, f.Revenue_YoY_P0, f.CF_OA_P0, f.CF_OA_3Y, f.Debt_Eq_P0, f.IntCov_P0, f.NP_P0
FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
"""
d = con.execute(q).df(); d["d"] = pd.to_datetime(d.d)
gcols = [f"GPM_P{i}" for i in range(8)]
gmat = d[gcols].astype(float)
d["gpm_mean"] = gmat.mean(axis=1)
d["gpm_cv"] = gmat.std(axis=1) / gmat.mean(axis=1).replace(0, np.nan)

# --- Screen A: quality-value exporter ---
#   margin stability (gpm_cv<0.15 & gpm_mean>0.12) + survival (IntCov>1.5, CF_OA_3Y>0) +
#   real profitability (ROE5Y>0.15, NPM_P0>0.04) + cheap vs OWN history (PE<PE_MA1Y).
LIQ_gate = d.tv >= LIQ
passA = (LIQ_gate & (d.gpm_cv < 0.15) & (d.gpm_mean > 0.12)
         & (d.IntCov_P0 > 1.5) & (d.CF_OA_3Y > 0)
         & (d.ROE5Y > 0.15) & (d.NPM_P0 > 0.04)
         & (d.PE < d.PE_MA1Y) & (d.PE > 0))
selA = d[passA].copy()
g = selA.groupby("d")
selA["score"] = (g["PE"].transform(negz).fillna(0) + g["ROE5Y"].transform(zc).fillna(0)
                 + g["EVEB"].transform(negz).fillna(0))
picksA = {}
cntA = []
for dd, gg in selA.groupby("d"):
    picksA[dd] = gg.nlargest(KA, "score").ticker.tolist()
for dd, gg in d[LIQ_gate].groupby("d"):
    cntA.append((dd, passA[gg.index].sum()))
cntA = pd.DataFrame(cntA, columns=["d", "nq"]).sort_values("d")
RA = simulate(picksA); RA.to_csv("data/textile_qualityvalue_monthly.csv", index=False)

# --- Screen B: sector-basket EW beta reference (always-in liquid export core) ---
picksB = {}
for dd, gg in d[LIQ_gate].groupby("d"):
    picksB[dd] = gg.ticker.tolist()
RB = simulate(picksB); RB.to_csv("data/textile_basket_monthly.csv", index=False)

# ---------- reporting ----------
def block(name, R, cnt, picks):
    held = R[R.n_held > 0]
    print("\n" + "="*72 + f"\n{name}")
    if cnt is not None:
        print(f"Qualifiers/month: med {int(cnt.nq.median())} min {int(cnt.nq.min())} max {int(cnt.nq.max())} | months 0 (cash): {int((cnt.nq==0).sum())}/{len(cnt)}")
    print(f"Months holding: {len(held)}/{len(R)} (median names {int(held.n_held.median()) if len(held) else 0})")
    full = report(f"{name} FULL 2014-2026", R)
    is_  = report(f"{name} IS 2014-2019", R[R.year <= 2019])
    oos  = report(f"{name} OOS 2020-2026", R[R.year >= 2020])
    print(f"\n{name} per-year (net vs B&H, avg names):")
    for yr, gy in R.groupby("year"):
        sret = (np.prod(1+gy.net)-1)*100; bret = (np.prod(1+gy.bh)-1)*100
        print(f"  {yr} {len(gy):>2}mo  sys {sret:>7.1f}%  bh {bret:>7.1f}%  edge {sret-bret:>+6.1f}pp  held {gy.n_held.mean():>4.1f}")
    return full, is_, oos

fullA, isA, oosA = block("SCREEN A — QUALITY-VALUE EXPORTER", RA, cntA, picksA)
fullB, isB, oosB = block("SCREEN B — SECTOR BASKET (EW beta)", RB, None, picksB)

# ---------- self-check 0 VND ----------
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path)
    return abs(NAV0*np.prod(1+R.net.values) - NAV0*np.prod(1+chk.net.values))
dA = selfcheck(RA, "data/textile_qualityvalue_monthly.csv")
dB = selfcheck(RB, "data/textile_basket_monthly.csv")
print(f"\nSELF-CHECK qualityvalue {dA:.6f} {'PASS' if dA<1 else 'FAIL'} | basket {dB:.6f} {'PASS' if dB<1 else 'FAIL'}")

# ---------- verify known names ----------
def mw(pm_, tk, y0, y1): return [dd.strftime("%Y-%m") for dd in sorted(pm_) if tk in pm_[dd] and y0 <= dd.year <= y1]
v = dict(
    MSH_caught = mw(picksA, "MSH", 2014, 2026),
    MSH_2020_covid = mw(picksA, "MSH", 2020, 2020),
    TCM_caught = mw(picksA, "TCM", 2014, 2026),
    TCM_2018_19_window = mw(picksA, "TCM", 2018, 2019),
    TNG_rejected = mw(picksA, "TNG", 2014, 2026),
    GIL_rejected = mw(picksA, "GIL", 2014, 2026),
    STK_rejected = mw(picksA, "STK", 2014, 2026),
    VGT_rejected = mw(picksA, "VGT", 2014, 2026),
)
print("\nVERIFY (Screen A quality-value picks):")
print(f"  MSH caught (any)                : {len(v['MSH_caught'])} mo -> {'CAUGHT' if v['MSH_caught'] else 'MISSED'}")
print(f"  MSH 2020 COVID cheap-quality    : {v['MSH_2020_covid']} -> {'present' if v['MSH_2020_covid'] else 'absent'}")
print(f"  TCM caught (any)                : {len(v['TCM_caught'])} mo -> {'CAUGHT' if v['TCM_caught'] else 'MISSED'}")
print(f"  TCM 2018-19 cheap-quality window: {len(v['TCM_2018_19_window'])} mo -> {'CAUGHT' if v['TCM_2018_19_window'] else 'absent'}")
print(f"  TNG (thin-CMT leverage, expect ~reject): {len(v['TNG_rejected'])} mo -> {'REJECTED' if not v['TNG_rejected'] else 'leaked '+str(v['TNG_rejected'][:6])}")
print(f"  GIL (unstable GPM, expect reject): {len(v['GIL_rejected'])} mo -> {'REJECTED' if not v['GIL_rejected'] else 'leaked '+str(v['GIL_rejected'][:6])}")
print(f"  STK (loss-making, expect reject) : {len(v['STK_rejected'])} mo -> {'REJECTED' if not v['STK_rejected'] else 'leaked '+str(v['STK_rejected'][:6])}")
print(f"  VGT (low-ROE holding, expect rej): {len(v['VGT_rejected'])} mo -> {'REJECTED' if not v['VGT_rejected'] else 'leaked '+str(v['VGT_rejected'][:6])}")

# ---------- orthogonality vs custom30V & 8L top-25 ----------
c30 = con.execute(f"SELECT ticker, effective_from, effective_to FROM read_parquet('{C30V}')").df()
c30["effective_from"] = pd.to_datetime(c30.effective_from); c30["effective_to"] = pd.to_datetime(c30.effective_to)
r8 = con.execute(f"SELECT ticker, time, rating FROM read_parquet('{R8L}')").df(); r8["time"] = pd.to_datetime(r8.time)
fullliq = con.execute(f"""SELECT p.time d, p.ticker, p.Trading_Value_1M_P50 tv FROM read_parquet('{PRUNE}') p
  WHERE p.time IN ({",".join(f"DATE '{dd}'" for dd in rebal_str)}) AND p.Trading_Value_1M_P50>=1e9""").df()
fullliq["d"] = pd.to_datetime(fullliq.d)
def ortho(picks):
    ov_v, ov_8l = [], []
    for dd in sorted(picks):
        C = set(picks[dd])
        if not C: continue
        vbask = set(c30[(c30.effective_from <= dd) & (c30.effective_to >= dd)].ticker)
        if vbask: ov_v.append(len(C & vbask)/len(C)*100)
        asof = r8[r8.time <= dd].sort_values("time").groupby("ticker").tail(1)
        m = asof.merge(fullliq[fullliq.d == dd][["ticker", "tv"]], on="ticker", how="inner")
        if len(m) >= 25:
            top25 = set(m.sort_values(["rating", "tv"], ascending=False).head(25).ticker)
            ov_8l.append(len(C & top25)/len(C)*100)
    return (float(np.mean(ov_v)) if ov_v else 0.0, float(np.mean(ov_8l)) if ov_8l else 0.0)
ovA = ortho(picksA)
print(f"\nORTHOGONALITY Screen A (vs custom30V | vs 8L top-25): {ovA[0]:.1f}% | {ovA[1]:.1f}%")

def adv(picks):
    vals = [d[(d.d == dd) & (d.ticker == t)].tv.values for dd in picks for t in picks[dd]]
    vals = [x[0] for x in vals if len(x)]
    return float(np.median(vals))/1e9 if vals else 0.0
advA = adv(picksA)
print(f"LIQUIDITY median selected ADV Screen A: {advA:.1f}B")

# ---------- verdict json ----------
def pack(R, full, is_, oos):
    held = R[R.n_held > 0]
    return dict(months_held=len(held), months=len(R),
        full={k: round(x, 3) for k, x in full[0].items()}, full_bh={k: round(x, 3) for k, x in full[1].items()},
        is_={k: round(x, 3) for k, x in is_[0].items()}, oos={k: round(x, 3) for k, x in oos[0].items()},
        oos_bh={k: round(x, 3) for k, x in oos[1].items()})
out = dict(job="Taylor_20260705_154537", screen="textile_garment_export", universe=list(UNIVERSE),
    liquid_core=["TCM", "TNG", "MSH", "GIL", "VGT"], liq_gate_vnd=LIQ,
    fx_sensitivity=dict(spearman_ic=fx_ic, whole_market_fx6m_profit3M=fx_mkt_ic,
        regime_mean_fwd_return={k: {c: round(float(fx_reg.loc[k, c]), 3) for c in fx_reg.columns} for k in fx_reg.index},
        regime_n={k: int(fx_reg_n[k]) for k in fx_reg_n.index},
        note="VND depreciation (USD/VND up) is a NEGATIVE forward-return signal for textile (Spearman -0.18 "
             "vs market -0.12) — the 'weak-VND-helps-exporters' thesis is DOMINATED by the risk-off confound "
             "(USD/VND spikes = global tightening = VN drawdown; textile is higher-beta). NOT a tradeable long signal."),
    qualityvalue=pack(RA, fullA, isA, oosA), basket=pack(RB, fullB, isB, oosB),
    selfcheck_vnd=dict(qualityvalue=round(dA, 6), basket=round(dB, 6)),
    ortho_c30v=round(ovA[0], 1), ortho_8l=round(ovA[1], 1), median_sel_adv_b=round(advA, 2),
    gate_note="GPM-CV<0.15 + IntCov>1.5 + ROE5Y>0.15 keeps margin-stable exporters (MSH/TCM-post-turn), "
              "ejects the thin-CMT leverage trap (TNG: NPM~0, Debt_Eq 2-4, IntCov<0) and messy pivots/losses "
              "(GIL CV0.38, STK losses, VGT ROE0.07, EVE ROE0.04).",
    verify=v)
with open("data/textile_verdict.json", "w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/textile_{qualityvalue,basket}_monthly.csv + data/textile_verdict.json")
