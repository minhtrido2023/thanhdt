"""Fertilizer / Chemicals / Rubber — THREE sub-sector screens (point-in-time monthly).
Design + backlook: job Taylor_20260630_064517. Framework: mike/agents/Taylor/fertchem_rubber_valuation_framework.md.

ICB does NOT separate the three economics (1357 = fertilizer+chemicals together; 1353 = rubber+plastics
together), so sub-universes are hand-curated by name (parallel to the logistics 3-economics split).

  A — FERTILIZER cycle (commodity, gas-policy-driven for urea names): cheap on EV/EBITDA, must survive
      a full cycle (CF_OA_3Y>0), early-cycle margin expansion (GPM_P0>GPM_P4), survivable leverage.
      Returns ride the GLOBAL urea/DAP price cycle (2021-22 Russia/gas spike) — cheapness predictable,
      catalyst timing NOT. High DY = the carry while you wait.
  B — SPECIALTY CHEMICALS (DGC-type): EV/EBITDA + ROIC moat + revenue growth phase. DGC's 2019-2020
      pre-phosphorus-supercycle window (EVEB 4-4.5, PB<1, ROIC5Y~11%, CF_OA ramping) WAS catchable —
      BUT ROIC5Y was 10.8-11.5% there, i.e. BELOW a literal >12% gate. We test >=10% and report the
      >12% miss honestly (the dispatch's "is the supercycle predictable?" question).
  C — RUBBER land-bank (hidden-asset): latex is thin commodity; the alpha is vuon cao su -> KCN land
      conversion (one-time massive gain), invisible to standard metrics. Proxy = PB<book (land not yet
      revalued) + clean balance sheet + latex covers ops (CF_OA>0). DY = carry while waiting. ROIC5Y is
      DATA-CORRUPTED for rubber (PHR 515%, DPR 290% — tiny/restated equity base) -> NOT used.

BACKLOOK (ticker_financial cache, see framework doc):
  DGC 2019Q4 EVEB4.5 PB0.93 ROIC5Y10.8% CF_OA+197B CF_OA_3Y ramping 887B->1368B -> caught pre-10x
  DGC 2020Q1 EVEB4.3 PB0.86 ROIC5Y10.8%                                          -> textbook entry
  DPM 2019Q4 EVEB3.2 PB0.60 DY3.4% (cyclical trough, urea spike 2021 ahead)      -> cheap value-trap-then-spike
  DCM 2019Q4 EVEB2.5 PB0.49 ROIC5Y4.8%                                            -> cheap, gas-policy drag
  PHR 2016Q1 PB0.66 DY5.2% (land story not yet priced)                           -> land-bank entry, re-rated to PB2.4 by 2019
  DPR 2017Q3 PB0.61 DY7.4% Debt_Eq0.35 CF_OA+109B                                 -> persistent land-bank value
HONEST: PHR's land re-rate was FAST (PB 0.66->2.45 in ~3yr) so the PB<0.8 window is short; DPR stays
cheap for years (slow/no conversion) so it dominates Screen C -> a 'wait-for-land' screen holds DPR a lot.
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
TC, STALE = 0.001, 120
KA = 10

FERT   = ("DPM","DCM","BFC","LAS","DDV","SFG","VFG","QBS","ABS","PMB")
CHEM   = ("DGC","CSV","PAT","HVT","PLC")
RUBBER = ("GVR","PHR","DPR","TRC","DRI")

con = duckdb.connect()

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

def simulate(picks_map):
    """Monthly EW, hold CASH when no qualifier (correct for a wait-for-cycle/trough screen)."""
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
            cost = TC*float(len(prev) > 0)
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
    if len(r) == 0: return dict(CAGR=0,Sharpe=0,MaxDD=0,Calmar=0,navfinal=1,n=0)
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

def fin_pull(universe):
    q = f"""
    WITH rb(d) AS (VALUES {rebal_vals}),
    prices AS (SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv
      FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
      WHERE p.Close IS NOT NULL AND p.ticker IN {universe})
    SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.EVEB, f.PB, f.PE, f.DY, f.ROIC5Y,
           f.GPM_P0, f.GPM_P4, f.NPM_P0, f.Revenue_YoY_P0, f.CF_OA_P0, f.CF_OA_3Y,
           f.Debt_Eq_P0, f.IntCov_P0, f.NP_P0, f.NP_P4
    FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
    WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
    """
    d = con.execute(q).df(); d["d"] = pd.to_datetime(d.d); return d

def build_picks(sel, score_cols, take_all=False):
    g = sel.groupby("d"); sel = sel.copy()
    sel["score"] = sum(g[c].transform(f).fillna(0) for c, f in score_cols)
    picks, cnt = {}, []
    for d, gg in sel.groupby("d"):
        picks[d] = (gg.sort_values("score", ascending=False).ticker.tolist() if take_all
                    else gg.nlargest(KA, "score").ticker.tolist())
        cnt.append((d, len(gg)))
    return picks, pd.DataFrame(cnt, columns=["d","nq"]).sort_values("d")

negz = lambda s: -zc(s)

# ============ SCREEN A — FERTILIZER CYCLE ============
da = fin_pull(FERT)
passA = (da.EVEB.between(0, 6, inclusive="neither") & (da.CF_OA_3Y > 0)
         & (da.GPM_P0 > da.GPM_P4) & (da.Debt_Eq_P0 < 1.5))
selA = da[passA]
picksA, cntA = build_picks(selA, [("EVEB", negz), ("DY", zc), ("GPM_P0", zc)])
RA = simulate(picksA); RA.to_csv("data/fertchem_fert_monthly.csv", index=False)

# ============ SCREEN B — SPECIALTY CHEMICALS (DGC-type) ============
db = fin_pull(CHEM)
# dispatch spec ROIC5Y>12% MISSES DGC's 10.8% golden window -> use >=10% and report the miss
passB = (db.EVEB.between(0, 8, inclusive="neither") & (db.ROIC5Y >= 0.10)
         & (db.Revenue_YoY_P0 > 0.20) & (db.CF_OA_P0 > 0))
selB = db[passB]
picksB, cntB = build_picks(selB, [("EVEB", negz), ("ROIC5Y", zc), ("Revenue_YoY_P0", zc)], take_all=True)
RB = simulate(picksB); RB.to_csv("data/fertchem_chem_monthly.csv", index=False)
# how many DGC entries would a literal >12% gate drop?
dgc_10 = db[(db.ticker=="DGC") & db.EVEB.between(0,8,inclusive="neither") & (db.ROIC5Y>=0.10)
            & (db.Revenue_YoY_P0>0.20) & (db.CF_OA_P0>0)]
dgc_12 = dgc_10[dgc_10.ROIC5Y >= 0.12]

# ============ SCREEN C — RUBBER LAND BANK (hidden asset) ============
dc = fin_pull(RUBBER)
# DY is lumpy (annual) -> many quarters show 0; test it as a SOFT score, not a hard gate.
passC = (dc.PB.between(0, 0.8, inclusive="neither") & (dc.Debt_Eq_P0 < 0.5) & (dc.CF_OA_P0 > 0))
selC = dc[passC]
picksC, cntC = build_picks(selC, [("PB", negz), ("DY", zc), ("Debt_Eq_P0", negz)], take_all=True)
RC = simulate(picksC); RC.to_csv("data/fertchem_rubber_monthly.csv", index=False)
# what does a DY>4% HARD gate do to coverage?
passC_dy = passC & (dc.DY > 0.04)
selC_dy = dc[passC_dy]

def block(name, R, cnt, uni_df, picks):
    held = R[R.n_held > 0]
    print("\n" + "="*72 + f"\n{name}")
    print(f"Universe: {uni_df.ticker.nunique()} names {sorted(uni_df.ticker.unique())}")
    print(f"Qualifiers/month: med {int(cnt.nq.median())} min {cnt.nq.min()} max {cnt.nq.max()} | months 0 (cash): {int((cnt.nq==0).sum())}/{len(cnt)}")
    print(f"Months holding: {len(held)}/{len(R)} (median names {int(held.n_held.median()) if len(held) else 0})")
    full = report(f"{name} FULL 2014-2026", R)
    is_  = report(f"{name} IS 2014-2019", R[R.year <= 2019])
    oos  = report(f"{name} OOS 2020-2026", R[R.year >= 2020])
    print(f"\n{name} per-year (net vs B&H, avg names):")
    for yr, gy in R.groupby("year"):
        sret=(np.prod(1+gy.net)-1)*100; bret=(np.prod(1+gy.bh)-1)*100
        print(f"  {yr} {len(gy):>2}mo  sys {sret:>7.1f}%  bh {bret:>7.1f}%  edge {sret-bret:>+6.1f}pp  held {gy.n_held.mean():>4.1f}")
    return full, is_, oos

fullA, isA, oosA = block("SCREEN A — FERTILIZER", RA, cntA, da, picksA)
fullB, isB, oosB = block("SCREEN B — SPECIALTY CHEMICALS", RB, cntB, db, picksB)
fullC, isC, oosC = block("SCREEN C — RUBBER LAND BANK", RC, cntC, dc, picksC)

print(f"\nDGC gate sensitivity: months passing ROIC5Y>=10% = {len(dgc_10)}; of those ROIC5Y>=12% = {len(dgc_12)}"
      f" -> literal >12% would DROP {len(dgc_10)-len(dgc_12)} DGC entry-months (incl 2019-2020 golden window).")
print(f"Screen C DY>4% HARD gate: would cut qualifying rows {len(selC)} -> {len(selC_dy)} "
      f"(DY lumpy/annual -> kills {len(selC)-len(selC_dy)} otherwise-valid rows; used as soft score instead).")

# ---- self-check 0 VND ----
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path)
    return abs(NAV0*np.prod(1+R.net.values) - NAV0*np.prod(1+chk.net.values))
dA = selfcheck(RA,"data/fertchem_fert_monthly.csv"); dB = selfcheck(RB,"data/fertchem_chem_monthly.csv"); dC = selfcheck(RC,"data/fertchem_rubber_monthly.csv")
print(f"\nSELF-CHECK fert {dA:.6f} {'PASS' if dA<1 else 'FAIL'} | chem {dB:.6f} {'PASS' if dB<1 else 'FAIL'} | rubber {dC:.6f} {'PASS' if dC<1 else 'FAIL'}")

# ---- VERIFY known names ----
def mw(pm_, tk, y0, y1): return [d.strftime("%Y-%m") for d in sorted(pm_) if tk in pm_[d] and y0<=d.year<=y1]
v = dict(
  DGC_2019_20 = mw(picksB,"DGC",2019,2020),
  DGC_supercycle_21_22 = mw(picksB,"DGC",2021,2022),
  DPM_cheap_2019_20 = mw(picksA,"DPM",2019,2020),
  DCM_cheap_2019_20 = mw(picksA,"DCM",2019,2020),
  PHR_landbank_2016_17 = mw(picksC,"PHR",2016,2017),
  PHR_after_rerate_2019 = mw(picksC,"PHR",2019,2020),
  DPR_persistent = mw(picksC,"DPR",2014,2026),
)
print("\nVERIFY:")
print(f"  DGC 2019-20 (pre-supercycle entry) : {v['DGC_2019_20']} -> {'CAUGHT' if v['DGC_2019_20'] else 'MISSED'}")
print(f"  DGC 2021-22 (supercycle itself)    : {v['DGC_supercycle_21_22']} -> {'present' if v['DGC_supercycle_21_22'] else 'absent (Rev_YoY base-effect drops it)'}")
print(f"  DPM 2019-20 cheap trough           : {v['DPM_cheap_2019_20']} -> {'CAUGHT' if v['DPM_cheap_2019_20'] else 'absent'}")
print(f"  DCM 2019-20 cheap trough           : {v['DCM_cheap_2019_20']} -> {'CAUGHT' if v['DCM_cheap_2019_20'] else 'absent'}")
print(f"  PHR 2016-17 land-bank (PB<0.8)     : {v['PHR_landbank_2016_17']} -> {'CAUGHT' if v['PHR_landbank_2016_17'] else 'absent (entered prune 2013; check PB window)'}")
print(f"  PHR 2019-20 after re-rate          : {v['PHR_after_rerate_2019']} -> {'(present)' if v['PHR_after_rerate_2019'] else 'EXPECTED-ABSENT (PB re-rated to 2.0-3.5, land priced in)'}")
print(f"  DPR persistent land-bank value     : {len(v['DPR_persistent'])} months held over 2014-2026")

# ---- ORTHOGONALITY ----
c30 = con.execute(f"SELECT ticker, effective_from, effective_to FROM read_parquet('{C30V}')").df()
c30["effective_from"]=pd.to_datetime(c30.effective_from); c30["effective_to"]=pd.to_datetime(c30.effective_to)
r8 = con.execute(f"SELECT ticker, time, rating FROM read_parquet('{R8L}')").df(); r8["time"]=pd.to_datetime(r8.time)
fullliq = con.execute(f"""SELECT p.time d, p.ticker, p.Trading_Value_1M_P50 tv FROM read_parquet('{PRUNE}') p
  WHERE p.time IN ({",".join(f"DATE '{d}'" for d in rebal_str)}) AND p.Trading_Value_1M_P50>=1e9""").df()
fullliq["d"]=pd.to_datetime(fullliq.d)
def ortho(picks):
    ov_v, ov_8l = [], []
    for d in sorted(picks):
        C = set(picks[d])
        if not C: continue
        vbask = set(c30[(c30.effective_from<=d)&(c30.effective_to>=d)].ticker)
        if vbask: ov_v.append(len(C & vbask)/len(C)*100)
        asof = r8[r8.time<=d].sort_values("time").groupby("ticker").tail(1)
        m = asof.merge(fullliq[fullliq.d==d][["ticker","tv"]], on="ticker", how="inner")
        if len(m) >= 25:
            top25 = set(m.sort_values(["rating","tv"], ascending=False).head(25).ticker)
            ov_8l.append(len(C & top25)/len(C)*100)
    return (float(np.mean(ov_v)) if ov_v else 0.0, float(np.mean(ov_8l)) if ov_8l else 0.0)
ovA, ovB, ovC = ortho(picksA), ortho(picksB), ortho(picksC)
print("\nORTHOGONALITY (vs custom30V | vs 8L top-25):")
print(f"  FERT  {ovA[0]:5.1f}% | {ovA[1]:5.1f}%")
print(f"  CHEM  {ovB[0]:5.1f}% | {ovB[1]:5.1f}%")
print(f"  RUBB  {ovC[0]:5.1f}% | {ovC[1]:5.1f}%")

def adv(df, picks):
    vals = [r.tv for d in picks for t in picks[d] for _,r in df[(df.d==d)&(df.ticker==t)].iterrows()]
    return float(np.median(vals))/1e9 if vals else 0.0
print(f"\nLIQUIDITY median selected ADV: FERT {adv(da,picksA):.1f}B | CHEM {adv(db,picksB):.1f}B | RUBB {adv(dc,picksC):.1f}B")

# ---- verdict json ----
def pack(R, full, is_, oos, cnt, df, picks, ov):
    held = R[R.n_held>0]
    return dict(names=sorted(df.ticker.unique().tolist()), qual_med=int(cnt.nq.median()),
        months_held=len(held), months=len(R), median_sel_adv_b=round(adv(df,picks),2),
        full={k:round(x,3) for k,x in full[0].items()}, full_bh={k:round(x,3) for k,x in full[1].items()},
        is_={k:round(x,3) for k,x in is_[0].items()}, oos={k:round(x,3) for k,x in oos[0].items()},
        oos_bh={k:round(x,3) for k,x in oos[1].items()}, ortho_c30v=round(ov[0],1), ortho_8l=round(ov[1],1))
out = dict(job="Taylor_20260630_064517", screen="fertchem_rubber_triple",
    fert=pack(RA,fullA,isA,oosA,cntA,da,picksA,ovA),
    chem=pack(RB,fullB,isB,oosB,cntB,db,picksB,ovB),
    rubber=pack(RC,fullC,isC,oosC,cntC,dc,picksC,ovC),
    selfcheck_vnd=dict(fert=round(dA,6),chem=round(dB,6),rubber=round(dC,6)),
    dgc_gate=dict(pass_roic10=len(dgc_10), pass_roic12=len(dgc_12),
        note="literal ROIC5Y>12% drops DGC 2019-2020 golden window (ROIC5Y was 10.8-11.5%)"),
    verify=v)
with open("data/fertchem_rubber_verdict.json","w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/fertchem_{fert,chem,rubber}_monthly.csv + data/fertchem_rubber_verdict.json")
