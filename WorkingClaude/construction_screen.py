"""Construction contractors (civil / industrial EPC) — sector #18 valuation framework + screen.
Design + backlook: job Taylor_20260706_033659. Framework: mike/agents/Taylor/construction_valuation_framework.md.

Vietnam listed construction is a PURE-CONTRACTOR group (general contractor / EPC / foundations / roads),
distinct from the BOT-toll infra OWNERS (CII/HHV/CTI/PC1 — routed to rating_8l D&A_HEAVY, EXCLUDED here)
and from pure RE developers. The defining economics:

  (a) PERCENTAGE-OF-COMPLETION accounting. Revenue/profit is booked as a project progresses, long before
      cash is collected -> reported earnings can diverge violently from cash. Trailing P/E is therefore
      NOISE (CTD 2022Q2 PE -65.6, 2022Q4 +140, 2023Q1 +322; HBC negative through 2023). P/E is unusable.
  (b) RECEIVABLES ARE THE WHOLE RISK. The contractor finances the developer: AR balloons (CTD carries
      ~11T VND of AR on ~3T quarterly revenue; DSO 230-300 days is STRUCTURAL for the sector). When the
      developer client is stressed (NVL-era 2022-23), AR is not collected, is written down, and — because
      gross margins are razor-thin (0-8%) — a single bad-debt provision wipes out YEARS of profit and can
      eat the equity itself.
  (c) THIN MARGINS. GPM 0-8%, NPM ~0-2%. There is no cushion. Small AR deterioration = large P&L swing.

International EPC-contractor valuation (Fluor, AECOM, Larsen & Toubro, Vinci, Bouygues) leans on
BACKLOG-to-revenue coverage (forward visibility) + margin + CASH CONVERSION, NOT trailing P/E. The
canonical blow-up is Carillion (UK, 2018): aggressive POC revenue, ballooning receivables, operating cash
flow persistently below reported profit -> insolvency. That is EXACTLY the HBC (Hoa Binh) 2022-23 script.

Two things this script settles quantitatively:

  (1) SIGNAL TEST. Which of {P/B-trough (PB/PB_MA1Y), cash-quality (CF_OA), receivables-deterioration
      (DSO_P0-DSO_P4 rising, AR/Revenue)} predicts forward T+20/40/60 return (profit_1M/2M/3M — EVALUATION
      ONLY, never a live filter). Hypothesis (steel-parallel): naive P/B-trough is a TRAP (the cheap-P/B
      names are the AR-distressed ones); the durable signal is the CASH/RECEIVABLES QUALITY gate.

  (2) SCREENS + is-it-a-book-or-a-lens (Rule 3): (A) AR-quality contractor screen (cheap AND cash-clean AND
      receivables not deteriorating), (B) sector-basket EW beta reference, (C) naive P/B-trough counterfactual
      that SHOULD walk into HBC and prove the gate matters.

Universe (hand-curated; ICB lumps contractors with RE-developers and BOT owners). Liquid core ADV(2024+)>5B:
  CTD (Coteccons     — flagship civil GC, survived the 2022-23 stress: the quality anchor),
  VCG (Vinaconex     — civil + public-infra GC, also carries a RE arm),
  HBC (Hoa Binh CG   — the CRISIS CASE STUDY: 2022-23 receivables blow-up, equity near-wiped),
  FCN (Fecon         — foundations / ground-engineering / infra),
  LCG (Licogi 16     — infra + renewable-EPC; structurally very high DSO 400-600 yet survives),
  C4G (Cienco4       — roads / public infra),
  HTN (Hung Thinh Incons — civil GC, heavy captive exposure to one stressed RE developer),
  DPG (Dat Phuong    — bridge/road EPC that diversified into hydropower+materials; cleaner metrics),
  VC3 (Vinaconex 3), DC4 (DIC No.4), G36 (Tong 36 military construction) — small-cap tail.
EXCLUDED: CII/HHV/CTI/PC1 (BOT-toll asset OWNERS -> D&A_HEAVY route), CTR (telecom-infra, ICB trap),
  ROS/PVX (fraud / delisted). Pure RE developers are a separate sector (#3, P/B-vs-NAV).

Auditable: prices + forward returns from tav2_bq.ticker_prune cache; financials ASOF-joined from
ticker_financial cache. Self-check 0 VND, threads=1, no look-ahead (profit_* eval-only). AUDIT_END 2026-06-26.
"""
import duckdb, numpy as np, pandas as pd, json

FIN   = "data/bq_cache/ticker_financial.parquet"
PRUNE = "data/bq_cache/ticker_prune/*.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
TC, STALE = 0.001, 120
KA = 8
LIQ = 5e9   # 5B rolling ADV liquid gate

UNIVERSE = ("CTD","VCG","HBC","FCN","LCG","C4G","HTN","DPG","VC3","DC4","G36")

con = duckdb.connect(config={"threads": 1})
inl = ",".join(f"'{t}'" for t in UNIVERSE)

# ---------- price / forward-return panel (all names present in prune cache) ----------
raw = con.execute(f"""SELECT ticker, time, Close, Volume, Price, profit_1M, profit_2M, profit_3M
  FROM read_parquet('{PRUNE}') WHERE ticker IN ({inl}) AND time >= DATE '{START}'""").df()
raw["time"] = pd.to_datetime(raw.time)
px  = raw.pivot_table(index="time", columns="ticker", values="Close").sort_index()
alldays = px.index
raw["tvday"] = raw.Volume * raw.Price
adv = raw.pivot_table(index="time", columns="ticker", values="tvday").sort_index().rolling(21, min_periods=5).mean()

ixq = con.execute(f"""SELECT DISTINCT time, VNINDEX FROM read_parquet('{PRUNE}')
  WHERE time >= DATE '{START}' AND VNINDEX IS NOT NULL ORDER BY time""").df()
ixq["time"] = pd.to_datetime(ixq.time)
vix = ixq.set_index("time")["VNINDEX"].sort_index()

def next_session(d):
    pos = alldays.searchsorted(d, side="right"); return alldays[pos] if pos < len(alldays) else None

cal = pd.DataFrame({"time": alldays}); cal["ym"] = cal.time.dt.to_period("M")
rebal = sorted(cal.groupby("ym")["time"].max().tolist())
rebal_str = [d.strftime("%Y-%m-%d") for d in rebal]
rebal_vals = ",".join(f"(DATE '{d}')" for d in rebal_str)

def zc(s):
    s = s.clip(s.quantile(.01), s.quantile(.99)); sd = s.std()
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0
negz = lambda s: -zc(s)
def spearman(a, b):
    m = a.notna() & b.notna()
    if m.sum() < 30: return np.nan
    return a[m].rank().corr(b[m].rank())

# ============================================================================
# PART 1 — SIGNAL TEST (evaluation-only forward returns; never a live filter)
# ============================================================================
fwd = raw[["time","ticker","profit_1M","profit_2M","profit_3M"]].dropna(subset=["profit_2M"]).copy()
finq = con.execute(f"""SELECT ticker, Release_Date, PB, PB_MA1Y, EVEB, DSO_P0, DSO_P4, AR_P0, Revenue_P0,
    GPM_P0, NPM_P0, CF_OA_P0, CF_OA_3Y, Debt_Eq_P0, IntCov_P0, NP_P0
  FROM read_parquet('{FIN}') WHERE ticker IN ({inl}) AND Release_Date IS NOT NULL
  ORDER BY ticker, Release_Date""").df()
finq["Release_Date"] = pd.to_datetime(finq.Release_Date).astype("datetime64[ns]")
fwd["time"] = fwd["time"].astype("datetime64[ns]")
sig = pd.merge_asof(fwd.sort_values("time"), finq.sort_values("Release_Date"),
                    left_on="time", right_on="Release_Date", by="ticker", direction="backward")
sig = sig[(sig.time - sig.Release_Date).dt.days <= STALE].copy()
sig["pb_rel"]  = sig.PB / sig.PB_MA1Y                       # <1 = cheap vs own history (trough proxy)
sig["dso_chg"] = sig.DSO_P0 - sig.DSO_P4                    # >0 = receivables deteriorating YoY
sig["ar_rev"]  = sig.AR_P0 / (sig.Revenue_P0 * 4.0)        # receivables intensity (AR / annualized revenue)
sig["cfoa"]    = sig.CF_OA_P0                               # cash quality (>0 good)

feats = ["pb_rel","dso_chg","ar_rev","cfoa"]
cyc_ic = {f"{c}_vs_{r}": round(float(spearman(sig[c], sig[r])), 4)
          for c in feats for r in ["profit_1M","profit_2M","profit_3M"]}

# regime split: CLEAN contractor (cash-generative, receivables NOT deteriorating, solvent)
#               vs STRESSED (cash-burning OR receivables deteriorating)
sig["clean"] = (sig.CF_OA_P0 > 0) & (sig.dso_chg <= 0) & (sig.IntCov_P0 > 1.5) & (sig.Debt_Eq_P0 < 2.5)
sig["reg"] = np.where(sig.clean, "clean",
              np.where((sig.CF_OA_P0 <= 0) | (sig.dso_chg > 30), "stressed", "mixed"))
cyc_reg   = sig.groupby("reg")[["profit_1M","profit_2M","profit_3M"]].mean().round(3)
cyc_reg_n = sig.groupby("reg").size()

# whole-market P/B-trough baseline: is PB-trough a stronger signal HERE than market-wide?
mkt = con.execute(f"""SELECT p.time, p.ticker, p.profit_3M, f.PB, f.PB_MA1Y FROM read_parquet('{PRUNE}') p
  ASOF LEFT JOIN read_parquet('{FIN}') f ON p.ticker=f.ticker AND p.time>=f.Release_Date
  WHERE p.time>=DATE '{START}' AND p.profit_3M IS NOT NULL AND f.PB_MA1Y IS NOT NULL""").df()
mkt["pb_rel"] = mkt.PB / mkt.PB_MA1Y
mkt_ic = round(float(spearman(mkt.pb_rel, mkt.profit_3M)), 4)

print("="*74); print("PART 1 — SIGNAL TEST (value/quality/receivables vs forward return)")
print(f"  rows {len(sig)}  names {sig.ticker.nunique()}")
for k, v in cyc_ic.items(): print(f"  Spearman {k:24s}: {v:+.4f}")
print(f"  whole-market pb_rel vs profit_3M: {mkt_ic:+.4f}  (construction: {cyc_ic['pb_rel_vs_profit_3M']:+.4f})")
print("  mean forward return by quality regime:"); print(cyc_reg.to_string())
print("  n per regime:", dict(cyc_reg_n))

# ============================================================================
# PART 2 — SCREENS (monthly, ASOF financials, liquidity-gated, hold cash when empty)
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

# ASOF financials at each rebalance date
tk_vals = ",".join(f"('{t}')" for t in UNIVERSE)
q = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
tk(ticker) AS (VALUES {tk_vals}),
grid AS (SELECT rb.d, tk.ticker FROM rb CROSS JOIN tk)
SELECT g.d, g.ticker, f.Release_Date, f.PB, f.PB_MA1Y, f.EVEB, f.PE,
       f.DSO_P0, f.DSO_P4, f.AR_P0, f.Revenue_P0, f.GPM_P0, f.NPM_P0,
       f.CF_OA_P0, f.CF_OA_3Y, f.Debt_Eq_P0, f.IntCov_P0, f.NP_P0
FROM grid g ASOF LEFT JOIN read_parquet('{FIN}') f ON g.ticker = f.ticker AND g.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, g.d) <= {STALE}
"""
d = con.execute(q).df(); d["d"] = pd.to_datetime(d.d).astype("datetime64[ns]")
def adv_at(row):
    t = row.ticker
    if t not in adv.columns: return np.nan
    s = adv[t]; s = s[s.index <= row.d]
    return s.iloc[-1] if len(s) else np.nan
d["tv"] = d.apply(adv_at, axis=1)
d["pb_rel"]  = d.PB / d.PB_MA1Y
d["dso_chg"] = d.DSO_P0 - d.DSO_P4
d["ar_rev"]  = d.AR_P0 / (d.Revenue_P0 * 4.0)
LIQ_gate = d.tv >= LIQ

# --- Screen A: AR-QUALITY CONTRACTOR (the differentiated gate) ---
#   cheap-ish (PB < PB_MA1Y) AND cash-clean (CF_OA_P0>0 AND CF_OA_3Y>0)
#   AND receivables NOT deteriorating (DSO_P0 <= DSO_P4*1.15)
#   AND solvent (IntCov_P0>1.5, Debt_Eq_P0<2.5)
passA = (LIQ_gate & (d.PB < d.PB_MA1Y) & (d.CF_OA_P0 > 0) & (d.CF_OA_3Y > 0)
         & (d.DSO_P0 <= d.DSO_P4 * 1.15) & (d.IntCov_P0 > 1.5) & (d.Debt_Eq_P0 < 2.5))
selA = d[passA].copy()
g = selA.groupby("d")
selA["score"] = (g["pb_rel"].transform(negz).fillna(0) + g["EVEB"].transform(negz).fillna(0)
                 + g["dso_chg"].transform(negz).fillna(0))
picksA = {dd: gg.nlargest(KA, "score").ticker.tolist() for dd, gg in selA.groupby("d")}
cntA = pd.DataFrame([(dd, int(passA[gg.index].sum())) for dd, gg in d[LIQ_gate].groupby("d")],
                    columns=["d", "nq"]).sort_values("d")
RA = simulate(picksA); RA.to_csv("data/construction_arquality_monthly.csv", index=False)

# --- Screen B: sector-basket EW beta reference (all liquid names) ---
picksB = {dd: gg.ticker.tolist() for dd, gg in d[LIQ_gate].groupby("d")}
RB = simulate(picksB); RB.to_csv("data/construction_basket_monthly.csv", index=False)

# --- Screen C: NAIVE P/B-trough counterfactual (NO quality gate) — expect a TRAP ---
passC = LIQ_gate & (d.PB < d.PB_MA1Y)
selC = d[passC].copy()
gc = selC.groupby("d")
selC["score"] = gc["pb_rel"].transform(negz).fillna(0)
picksC = {dd: gg.nlargest(KA, "score").ticker.tolist() for dd, gg in selC.groupby("d")}
RC = simulate(picksC); RC.to_csv("data/construction_pbtrough_monthly.csv", index=False)

def block(name, R, cnt):
    held = R[R.n_held > 0]
    print("\n" + "="*74 + f"\n{name}")
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

fullA, isA, oosA = block("SCREEN A — AR-QUALITY CONTRACTOR", RA, cntA)
fullB, isB, oosB = block("SCREEN B — SECTOR BASKET (EW beta)", RB, None)
fullC, isC, oosC = block("SCREEN C — NAIVE P/B-TROUGH (counterfactual, expect TRAP)", RC, None)

# ---------- self-check 0 VND ----------
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path)
    return abs(NAV0*np.prod(1+R.net.values) - NAV0*np.prod(1+chk.net.values))
dA = selfcheck(RA, "data/construction_arquality_monthly.csv")
dB = selfcheck(RB, "data/construction_basket_monthly.csv")
dC = selfcheck(RC, "data/construction_pbtrough_monthly.csv")
print(f"\nSELF-CHECK arquality {dA:.6f} {'PASS' if dA<1 else 'FAIL'} | basket {dB:.6f} {'PASS' if dB<1 else 'FAIL'} | pbtrough {dC:.6f} {'PASS' if dC<1 else 'FAIL'}")

# ---------- verify HBC (crisis case) is REJECTED by the quality gate 2022-2023 ----------
def mw(pm_, tk, y0, y1): return [dd.strftime("%Y-%m") for dd in sorted(pm_) if tk in pm_[dd] and y0 <= dd.year <= y1]
v = dict(
    HBC_in_A_crisis  = mw(picksA, "HBC", 2022, 2024),   # AR-quality screen: expect EMPTY (rejects the blow-up)
    HBC_in_C_crisis  = mw(picksC, "HBC", 2022, 2024),   # naive P/B-trough: expect it WALKS INTO HBC
    CTD_in_A         = mw(picksA, "CTD", 2014, 2026),   # the survivor/anchor
    all_A_names      = sorted({t for dd in picksA for t in picksA[dd]}),
)
print("\nVERIFY (crisis gate):")
print(f"  HBC in AR-quality screen during 2022-24 crisis : {v['HBC_in_A_crisis']}  -> {'REJECTED (good)' if not v['HBC_in_A_crisis'] else 'LEAKED (bad)'}")
print(f"  HBC in naive P/B-trough during 2022-24 crisis  : {v['HBC_in_C_crisis']}  -> {'TRAP fired' if v['HBC_in_C_crisis'] else 'not held'}")
print(f"  CTD (survivor) months in AR-quality screen     : {len(v['CTD_in_A'])}")
print(f"  distinct names ever selected by Screen A        : {v['all_A_names']}")

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
def adv_med(picks):
    vals = [d[(d.d == dd) & (d.ticker == t)].tv.values for dd in picks for t in picks[dd]]
    vals = [x[0] for x in vals if len(x) and pd.notna(x[0])]
    return float(np.median(vals))/1e9 if vals else 0.0
advA = adv_med(picksA)
print(f"\nORTHOGONALITY Screen A (vs custom30V | vs 8L top-25): {ovA[0]:.1f}% | {ovA[1]:.1f}%")
print(f"LIQUIDITY median selected ADV Screen A: {advA:.1f}B")

# ---------- verdict json ----------
def pack(R, full, is_, oos):
    held = R[R.n_held > 0]
    return dict(months_held=len(held), months=len(R),
        full={k: round(x, 3) for k, x in full[0].items()}, full_bh={k: round(x, 3) for k, x in full[1].items()},
        is_={k: round(x, 3) for k, x in is_[0].items()}, oos={k: round(x, 3) for k, x in oos[0].items()},
        oos_bh={k: round(x, 3) for k, x in oos[1].items()})
out = dict(job="Taylor_20260706_033659", screen="construction_contractors_epc", universe=list(UNIVERSE),
    liq_gate_vnd=LIQ,
    signal_test=dict(spearman_ic=cyc_ic, whole_market_pb_rel_profit3M=mkt_ic,
        regime_mean_fwd_return={k: {c: round(float(cyc_reg.loc[k, c]), 3) for c in cyc_reg.columns} for k in cyc_reg.index},
        regime_n={k: int(cyc_reg_n[k]) for k in cyc_reg_n.index},
        note="POC accounting makes P/E noise; receivables (AR/DSO) are the risk. Tests whether P/B-trough, "
             "cash-quality (CF_OA), and receivables-deterioration (DSO_P0-DSO_P4, AR/Rev) predict fwd return."),
    arquality=pack(RA, fullA, isA, oosA), basket=pack(RB, fullB, isB, oosB), pbtrough=pack(RC, fullC, isC, oosC),
    selfcheck_vnd=dict(arquality=round(dA, 6), basket=round(dB, 6), pbtrough=round(dC, 6)),
    ortho_c30v=round(ovA[0], 1), ortho_8l=round(ovA[1], 1), median_sel_adv_b=round(advA, 2),
    gate_note="Screen A = PB<PB_MA1Y + CF_OA_P0>0 + CF_OA_3Y>0 + DSO_P0<=DSO_P4*1.15 + IntCov>1.5 + Debt_Eq<2.5. "
              "The AR/CASH quality gate is the differentiator vs the naive P/B-trough (Screen C).",
    verify=v)
with open("data/construction_verdict.json", "w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/construction_{arquality,basket,pbtrough}_monthly.csv + data/construction_verdict.json")
