"""Livestock / Animal-Feed (hog cycle) — sector #17 valuation framework + screen (point-in-time monthly).
Design + backlook: job Taylor_20260705_160724. Framework: mike/agents/Taylor/livestock_valuation_framework.md.

Vietnam livestock/feed is a genuine PROTEIN / HOG-CYCLE commodity group (unlike the defensive F&B/FMCG of
sector #10). Margins swing violently quarter-to-quarter on: hog price (supply — African Swine Fever ASF
disease shocks) vs feed-input cost (imported corn/soybean). At the cycle TROUGH, hog price < cost of
production -> the pure farmers post LOSSES -> trailing P/E goes NEGATIVE or absurd (DBC 2023Q1 PE -19.8,
2023Q3 -87.1, 2023Q4 +251.6). So the international protein-cycle playbook (Tyson, WH Group/Smithfield,
Muyuan, Charoen Pokphand) says: value cyclicals on **P/B trough-buy** + a **margin-turning-up** trigger,
NOT on P/E. Two things this script settles quantitatively:

  (1) CYCLE-SIGNAL TEST. There is NO direct hog-price field in BQ. Proxy the cycle with quarterly GPM.
      Test whether (a) P/B-vs-own-history (PB/PB_MA1Y, causal) and (b) GPM turning up (GPM_P0 - GPM_P4)
      predict forward T+20/40/60 return (profit_1M/2M/3M — EVALUATION ONLY, never a live filter).

  (2) A TROUGH-BUY SCREEN and whether it is a tradeable BOOK or only a lens (sweep Rule 3), and whether
      any name looks like an HPG-2014/DGC-2016/MWG-2014 catchable compounder rather than pure cyclical timing.

Universe (hand-curated; ICB lumps agri/food). Prices pulled from the FULL ticker table (data/livestock_prices.csv)
because the ticker_prune cache is stale for the recently-added BAF/HNG. Liquid core (rolling ADV>5B):
  DBC (Dabaco — integrated feed->3F breeding->hog->food, the flagship hog-cycle name),
  BAF (BaF Viet Nam — pure-play hog-farm expansion, IPO 2021),
  HAG (HAGL — diversified agri conglomerate: pork + banana, ex-rubber/sugar/RE turnaround),
  HNG (HAGL Agrico — crop/banana plantation, chronic-loss restructuring; trong-trot, a DIFFERENT sub-group).
Thin tail (kept in universe, liquidity-gated out most months, all ADV<3B): MML (Masan MEATLife branded meat),
  VLC (Vilico livestock/dairy holding), VSN (Vissan meat proc, ADV 0.1B untradeable), APF/HKB/AGM (feed/agri).
Aquaculture protein (VHC/ANV/MPC pangasius/shrimp) is DELIBERATELY EXCLUDED — it is an EXPORT-FX protein
cycle (USD revenue), a different animal from the domestic hog cycle (that is the textile-#16 FX story).

Backlook (ticker_financial cache) — the DBC hog cycle is textbook:
  DBC 2019Q4 PB0.68<MA1Y0.75  GPM10% IC4.7  -> TROUGH pre-ASF: cheap-vs-own-history + margin about to turn
  DBC 2020Q1-Q3  GPM10->30%  NP 348B->401B->387B  PE 3.2-5  IC 5.5-7  -> ASF SUPERCYCLE (supply shock) explosion
  DBC 2022Q4-2023Q3  GPM->10%  NP -79B,-321B  PE NEGATIVE(-19.8,-87.1)/absurd(251) -> feed-cost trough, P/E useless
  DBC 2024Q4-2025Q3  GPM->20%  NP -> 508B record  PE 6-8  IC 7-9  -> recovery; PB re-rated 1.0->1.6
  BAF 2021-2026  PE 18-177 (NEVER cheap)  PB 1.5-5.4  GPM 0-20% thin  ROE5Y ~0.10-0.15  DE 2-2.5  -> a LEVERED
                 EXPANSION/GROWTH bet (building farms), not a value entry -> the TNG-of-this-sector
  HAG/HNG  messy conglomerate / chronic-loss plantation turnaround -> not clean hog plays

The transferable alpha is the STEEL-parallel: P/B-trough is a TRAP unless margin is turning up AND the name
survives the downcycle (CF_OA_3Y>0). DBC (integrated, survives) catches the ASF cycle; BAF (thin-margin,
levered, never-cheap) is correctly declined by a value screen; HAG/HNG are messy.
"""
import duckdb, numpy as np, pandas as pd, json

FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
PRUNE = "data/bq_cache/ticker_prune/*.parquet"       # only for the 8L-top25 orthogonality liquidity universe
PXCSV = "data/livestock_prices.csv"                # full-ticker daily panel (BAF/HNG not in stale prune cache)
IXCSV = "data/livestock_vnindex.csv"
START = "2014-01-01"
TC, STALE = 0.001, 120
KA = 10
LIQ = 5e9   # 5B rolling ADV liquid-core gate (thin tail is structurally untradeable)

UNIVERSE = ("DBC","BAF","HAG","HNG","MML","VLC","VSN","APF","HKB","AGM")
LIQUID_CORE = ["DBC","BAF","HAG","HNG"]

con = duckdb.connect()

# ---------- price panel (from full ticker, not stale prune) ----------
raw = pd.read_csv(PXCSV); raw["time"] = pd.to_datetime(raw.time)
raw = raw[raw.time >= START]
px = raw.pivot_table(index="time", columns="ticker", values="Close").sort_index()
alldays = px.index
# rolling ADV proxy = 21-session trailing mean of daily traded value (Volume * unadjusted Price)
raw["tvday"] = raw.Volume * raw.Price
tv = raw.pivot_table(index="time", columns="ticker", values="tvday").sort_index()
adv = tv.rolling(21, min_periods=5).mean()

ix = pd.read_csv(IXCSV); ix["time"] = pd.to_datetime(ix.time)
vix = ix[ix.time >= START].set_index("time")["VNINDEX"].sort_index()

def next_session(d):
    pos = alldays.searchsorted(d, side="right"); return alldays[pos] if pos < len(alldays) else None

# ---------- rebalance calendar (month-end sessions) ----------
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

inl = ",".join(f"'{t}'" for t in UNIVERSE)

# ============================================================================
# PART 1 — CYCLE-SIGNAL TEST (evaluation-only forward returns; never a live filter)
#   proxy the hog cycle with GPM (no direct hog-price field in BQ)
# ============================================================================
# daily forward returns from the full-ticker panel
fwd = raw[["time","ticker","profit_1M","profit_2M","profit_3M"]].dropna(subset=["profit_2M"]).copy()
# ASOF financials mapped to each name-day: PB/PB_MA1Y (trough) and GPM turn
finq = con.execute(f"""SELECT ticker, Release_Date, PB, PB_MA1Y, GPM_P0, GPM_P4 FROM read_parquet('{FIN}')
  WHERE ticker IN ({inl}) AND Release_Date IS NOT NULL ORDER BY ticker, Release_Date""").df()
finq["Release_Date"] = pd.to_datetime(finq.Release_Date).astype("datetime64[ns]")
fwd["time"] = fwd["time"].astype("datetime64[ns]")
sig = pd.merge_asof(fwd.sort_values("time"), finq.sort_values("Release_Date"),
                    left_on="time", right_on="Release_Date", by="ticker", direction="backward")
sig = sig[(sig.time - sig.Release_Date).dt.days <= STALE].copy()
sig["pb_rel"] = sig.PB / sig.PB_MA1Y                    # <1 = cheap vs own history (trough proxy)
sig["gpm_turn"] = sig.GPM_P0 - sig.GPM_P4               # >0 = margin turning up YoY
sig = sig.dropna(subset=["pb_rel","gpm_turn"])
cyc_ic = {f"{c}_vs_{r}": round(float(spearman(sig[c], sig[r])), 4)
          for c in ["pb_rel","gpm_turn"] for r in ["profit_1M","profit_2M","profit_3M"]}
# regime split: trough-buy = cheap PB AND margin turning up
sig["reg"] = np.where((sig.pb_rel < 1.0) & (sig.gpm_turn > 0), "trough_up",
              np.where((sig.pb_rel >= 1.0) & (sig.gpm_turn <= 0), "rich_down", "mixed"))
cyc_reg = sig.groupby("reg")[["profit_1M","profit_2M","profit_3M"]].mean().round(3)
cyc_reg_n = sig.groupby("reg").size()
# whole-market baseline: is PB-trough a stronger signal here than market-wide?
mkt = con.execute(f"""SELECT p.time, p.ticker, p.profit_3M, f.PB, f.PB_MA1Y FROM read_parquet('{PRUNE}') p
  ASOF LEFT JOIN read_parquet('{FIN}') f ON p.ticker=f.ticker AND p.time>=f.Release_Date
  WHERE p.time>=DATE '{START}' AND p.profit_3M IS NOT NULL AND f.PB_MA1Y IS NOT NULL""").df()
mkt["pb_rel"] = mkt.PB / mkt.PB_MA1Y
mkt_ic = round(float(spearman(mkt.pb_rel, mkt.profit_3M)), 4)

print("="*72); print("PART 1 — HOG-CYCLE SIGNAL (PB-trough + GPM-turn vs forward return)")
print(f"  rows {len(sig)}  names {sig.ticker.nunique()}")
for k, v in cyc_ic.items(): print(f"  Spearman {k:22s}: {v:+.4f}")
print(f"  whole-market pb_rel vs profit_3M: {mkt_ic:+.4f}  (livestock: {cyc_ic['pb_rel_vs_profit_3M']:+.4f})")
print("  mean forward return by cycle regime:"); print(cyc_reg.to_string())
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

# ASOF financials at each rebalance date (rb x ticker grid, then per-ticker ASOF join)
tk_vals = ",".join(f"('{t}')" for t in UNIVERSE)
q = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
tk(ticker) AS (VALUES {tk_vals}),
grid AS (SELECT rb.d, tk.ticker FROM rb CROSS JOIN tk)
SELECT g.d, g.ticker, f.Release_Date, f.PB, f.PB_MA1Y, f.EVEB, f.EVEB_MA1Y, f.PE, f.PE_MA1Y, f.DY,
       f.ROE5Y, f.ROIC5Y, f.GPM_P0, f.GPM_P4, f.NPM_P0, f.Revenue_YoY_P0,
       f.CF_OA_P0, f.CF_OA_3Y, f.Debt_Eq_P0, f.IntCov_P0, f.NP_P0
FROM grid g ASOF LEFT JOIN read_parquet('{FIN}') f ON g.ticker = f.ticker AND g.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, g.d) <= {STALE}
"""
d = con.execute(q).df(); d["d"] = pd.to_datetime(d.d).astype("datetime64[ns]")
# attach rolling ADV at each rebalance date (from the full-ticker panel)
def adv_at(row):
    t = row.ticker
    if t not in adv.columns: return np.nan
    s = adv[t]; s = s[s.index <= row.d]
    return s.iloc[-1] if len(s) else np.nan
d["tv"] = d.apply(adv_at, axis=1)
d["pb_rel"] = d.PB / d.PB_MA1Y
d["gpm_turn"] = d.GPM_P0 - d.GPM_P4

# --- Screen A: hog-cycle trough-buy ---
#   cheap vs own history (PB < PB_MA1Y) + margin turning up (GPM_P0 > GPM_P4) + survived cycle (CF_OA_3Y>0)
#   + not-a-solvency-wreck (IntCov_P0 > 1.0, loose — these names carry expansion debt).
LIQ_gate = d.tv >= LIQ
passA = (LIQ_gate & (d.PB < d.PB_MA1Y) & (d.GPM_P0 > d.GPM_P4)
         & (d.CF_OA_3Y > 0) & (d.IntCov_P0 > 1.0))
selA = d[passA].copy()
g = selA.groupby("d")
selA["score"] = (g["pb_rel"].transform(negz).fillna(0) + g["gpm_turn"].transform(zc).fillna(0)
                 + g["EVEB"].transform(negz).fillna(0))
picksA = {}
for dd, gg in selA.groupby("d"):
    picksA[dd] = gg.nlargest(KA, "score").ticker.tolist()
cntA = pd.DataFrame([(dd, int(passA[gg.index].sum())) for dd, gg in d[LIQ_gate].groupby("d")],
                    columns=["d", "nq"]).sort_values("d")
RA = simulate(picksA); RA.to_csv("data/livestock_troughbuy_monthly.csv", index=False)

# --- Screen B: sector-basket EW beta reference (always-in liquid core) ---
picksB = {dd: gg.ticker.tolist() for dd, gg in d[LIQ_gate].groupby("d")}
RB = simulate(picksB); RB.to_csv("data/livestock_basket_monthly.csv", index=False)

# ---------- reporting ----------
def block(name, R, cnt):
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

fullA, isA, oosA = block("SCREEN A — HOG-CYCLE TROUGH-BUY", RA, cntA)
fullB, isB, oosB = block("SCREEN B — SECTOR BASKET (EW beta)", RB, None)

# ---------- self-check 0 VND ----------
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path)
    return abs(NAV0*np.prod(1+R.net.values) - NAV0*np.prod(1+chk.net.values))
dA = selfcheck(RA, "data/livestock_troughbuy_monthly.csv")
dB = selfcheck(RB, "data/livestock_basket_monthly.csv")
print(f"\nSELF-CHECK troughbuy {dA:.6f} {'PASS' if dA<1 else 'FAIL'} | basket {dB:.6f} {'PASS' if dB<1 else 'FAIL'}")

# ---------- verify known names ----------
def mw(pm_, tk, y0, y1): return [dd.strftime("%Y-%m") for dd in sorted(pm_) if tk in pm_[dd] and y0 <= dd.year <= y1]
v = dict(
    DBC_caught = mw(picksA, "DBC", 2014, 2026),
    DBC_2019_20_ASF = mw(picksA, "DBC", 2019, 2020),
    BAF_rejected = mw(picksA, "BAF", 2014, 2026),
    HAG_picks = mw(picksA, "HAG", 2014, 2026),
    HNG_picks = mw(picksA, "HNG", 2014, 2026),
)
print("\nVERIFY (Screen A trough-buy picks):")
print(f"  DBC caught (any)                 : {len(v['DBC_caught'])} mo -> {'CAUGHT' if v['DBC_caught'] else 'MISSED'}")
print(f"  DBC 2019-20 pre/into-ASF window  : {v['DBC_2019_20_ASF']}")
print(f"  BAF (levered never-cheap, expect ~reject): {len(v['BAF_rejected'])} mo -> {'REJECTED' if not v['BAF_rejected'] else 'leaked '+str(v['BAF_rejected'][:6])}")
print(f"  HAG picks: {len(v['HAG_picks'])} mo   HNG picks: {len(v['HNG_picks'])} mo")

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
def adv_med(picks):
    vals = [d[(d.d == dd) & (d.ticker == t)].tv.values for dd in picks for t in picks[dd]]
    vals = [x[0] for x in vals if len(x) and pd.notna(x[0])]
    return float(np.median(vals))/1e9 if vals else 0.0
advA = adv_med(picksA)
print(f"LIQUIDITY median selected ADV Screen A: {advA:.1f}B")

# ---------- verdict json ----------
def pack(R, full, is_, oos):
    held = R[R.n_held > 0]
    return dict(months_held=len(held), months=len(R),
        full={k: round(x, 3) for k, x in full[0].items()}, full_bh={k: round(x, 3) for k, x in full[1].items()},
        is_={k: round(x, 3) for k, x in is_[0].items()}, oos={k: round(x, 3) for k, x in oos[0].items()},
        oos_bh={k: round(x, 3) for k, x in oos[1].items()})
out = dict(job="Taylor_20260705_160724", screen="livestock_animal_feed_hog_cycle", universe=list(UNIVERSE),
    liquid_core=LIQUID_CORE, liq_gate_vnd=LIQ,
    cycle_signal=dict(spearman_ic=cyc_ic, whole_market_pb_rel_profit3M=mkt_ic,
        regime_mean_fwd_return={k: {c: round(float(cyc_reg.loc[k, c]), 3) for c in cyc_reg.columns} for k in cyc_reg.index},
        regime_n={k: int(cyc_reg_n[k]) for k in cyc_reg_n.index},
        note="No direct hog-price field in BQ; GPM used as cycle proxy. Tests whether PB-trough (PB/PB_MA1Y) "
             "and GPM-turn (GPM_P0-GPM_P4) predict forward return for the livestock/feed group."),
    troughbuy=pack(RA, fullA, isA, oosA), basket=pack(RB, fullB, isB, oosB),
    selfcheck_vnd=dict(troughbuy=round(dA, 6), basket=round(dB, 6)),
    ortho_c30v=round(ovA[0], 1), ortho_8l=round(ovA[1], 1), median_sel_adv_b=round(advA, 2),
    gate_note="PB<PB_MA1Y + GPM_P0>GPM_P4 + CF_OA_3Y>0 + IntCov>1.0. DBC (integrated, survives cycle) is meant "
              "to catch the ASF up-cycle; BAF (thin-margin, levered, never-cheap) is the levered-growth name a "
              "value screen declines; HAG/HNG messy conglomerate/plantation.",
    verify=v)
with open("data/livestock_verdict.json", "w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/livestock_{troughbuy,basket}_monthly.csv + data/livestock_verdict.json")
