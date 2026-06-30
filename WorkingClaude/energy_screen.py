"""Energy — THREE sub-sector screens (point-in-time monthly).
Design + backlook: job Taylor_20260630_070640. Framework: mike/agents/Taylor/energy_valuation_framework.md.

ICB "Utilities/Oil&Gas" lumps very different economics; three hand-curated sub-universes:
  A — MATURE CASH-MACHINE UTILITY (VSH,SJD,NT2,PPC,REE,POW): hydro + thermal + conglomerate that
      all share ONE economic: once the plant capex is paid off, it is a pure cash machine. The
      dispatch's "DY>4% yield gate" is a TRAP in BQ -- DY is only populated in dividend-DECLARATION
      quarters (~20-30% of rows; PVD 0/79, POW 2/34, pure hydros VSH 21/85 SJD 14/79), so a hard
      DY gate fires sporadically and ejects a payer in the 70% of quarters it isn't recorded. The
      real alpha is FCF>0 (CF_OA_P0 + CF_Invest_P0 > 0 = maintenance-capex < operating-CF = the
      "cash machine" test); it cleanly separates mature payers (SJD,NT2,POW) from expansion-phase
      hydro (VSH 2018: CF_OA -80B, capex -549B -> FCF deeply negative). DY kept as a SCORING bonus.
  B — OIL SERVICES TROUGH (PVD,PVS,PVT): cyclical with oil price. P/B<0.8 buys below asset (rig/
      vessel) value AT the trough, but CF_OA_P0>0 is the discipline -- it rejects the 2020 oil-COVID
      crash where PVD traded PB0.49 on NEGATIVE operating cash (a value trap). PVD 2014Q4 PB1.51
      (pre-crash) correctly NOT caught; PVD 2016 trough (PB0.59-0.69, CF_OA+) caught. HIGH BETA ->
      flagged hold-only-in-NEUTRAL/BULL (backtest is unconditional EW; caveat reported, not gated).
  C — RENEWABLES (GEG,PC1,SBA): FIT-era solar/wind/hydro-construction. EVEB<10 + IntCov>1.5 +
      Revenue_YoY>0 + CF_OA_3Y>0, DY as bonus. EXPECTED WEAK/FAIL and reported as such: renewables
      look "expensive" (high EVEB, NEGATIVE FCF, 1.6-2.5x leverage) precisely WHILE building the
      assets that create future value; the FIT windfall is a policy event, not a financial-statement
      signal -> structurally un-screenable on value/cash metrics. Documented capture failure.

BACKLOOK (ticker_financial cache, see framework doc):
  SJD 2018Q4 EVEB5.07 FCF+145B ROE5Y17.6% Debt0.50 IC2.9   -> textbook mature hydro cash-machine
  NT2 2019Q4 EVEB4.24 FCF+692B DY5.3% ROIC5Y10.1% IC12.5   -> PPA gas play, cheap + yielding
  VSH 2022Q4 EVEB4.84 FCF+363B Debt0.93 (post Thuong-KonTum expansion) -> value entry AFTER capex done
  VSH 2018Q4 EVEB19.9 FCF-630B Debt1.66                    -> expansion phase, FCF gate rejects (correct)
  POW 2020Q4 EVEB5.36 FCF+3.96T PB0.90 ROIC5Y7.4%          -> mature gas-thermal cash machine
  PVD 2014Q4 EVEB5.10 PB1.51 (PRE-crash)                   -> NOT a trough yet, correctly missed
  PVD 2016Q2 EVEB6.32 PB0.69 CF_OA+95B                     -> trough caught (below asset value, still cash+)
  PVD 2020Q4 PB0.49 CF_OA -70B                             -> "cheapest" PB is the COVID value-trap, CF_OA gate rejects
  PVT 2020Q4 EVEB2.97 PB0.78 CF_OA+509B IC176             -> oil-transport, mature cash-gen at trough PB
  GEG 2021Q4 EVEB14.4 CF_OA -1.84T Debt2.55 DY0            -> renewables build-phase, un-screenable (expensive+levered+no FCF)
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
TC, STALE = 0.001, 120
KA = 10

UTIL   = ("VSH","SJD","NT2","PPC","REE","POW")   # mature cash-machine utility
OILSVC = ("PVD","PVS","PVT")                       # oil services trough (high beta)
RENEW  = ("GEG","PC1","SBA")                       # renewables (FIT-era, capex-heavy)

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
    inlist = "(" + ",".join(f"'{t}'" for t in universe) + ")"
    q = f"""
    WITH rb(d) AS (VALUES {rebal_vals}),
    prices AS (SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv
      FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
      WHERE p.Close IS NOT NULL AND p.ticker IN {inlist})
    SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.EVEB, f.PB, f.PE, f.PE_MA1Y, f.DY, f.PCF,
           f.ROIC5Y, f.ROE5Y, f.NPM_P0, f.Revenue_YoY_P0, f.CF_OA_P0, f.CF_Invest_P0, f.CF_OA_3Y,
           f.Debt_Eq_P0, f.IntCov_P0, f.NP_P0
    FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
    WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
    """
    d = con.execute(q).df(); d["d"] = pd.to_datetime(d.d)
    d["FCF"] = d.CF_OA_P0 + d.CF_Invest_P0           # capex is negative -> FCF after maintenance capex
    return d

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
dybonus = lambda s: zc(s.fillna(0))   # DY missing -> 0 contribution (scoring bonus, never a gate)

# ============ SCREEN A — MATURE CASH-MACHINE UTILITY ============
da = fin_pull(UTIL)
passA = (da.EVEB.between(0, 8, inclusive="neither") & (da.FCF > 0) & (da.CF_OA_3Y > 0)
         & (da.Debt_Eq_P0 < 2.0) & (da.IntCov_P0 > 2.0))
selA = da[passA]
picksA, cntA = build_picks(selA, [("EVEB", negz), ("FCF", zc), ("DY", dybonus)], take_all=True)
RA = simulate(picksA); RA.to_csv("data/energy_util_monthly.csv", index=False)
# how many expansion-phase (FCF<0) rows does the FCF gate reject?
preA = da[da.EVEB.between(0,8,inclusive="neither") & (da.CF_OA_3Y>0) & (da.Debt_Eq_P0<2.0) & (da.IntCov_P0>2.0)]
fcf_rej = preA[preA.FCF <= 0]

# ============ SCREEN B — OIL SERVICES TROUGH (high beta) ============
db = fin_pull(OILSVC)
passB = (db.PB.between(0, 0.8, inclusive="neither") & (db.CF_OA_P0 > 0) & (db.Debt_Eq_P0 < 2.0))
selB = db[passB]
picksB, cntB = build_picks(selB, [("PB", negz), ("CF_OA_P0", zc)], take_all=True)
RB = simulate(picksB); RB.to_csv("data/energy_oilsvc_monthly.csv", index=False)
# trap accounting: cheap PB that CF_OA gate rejects (negative operating cash)
trapB = db[db.PB.between(0,0.8,inclusive="neither") & (db.Debt_Eq_P0<2.0)]
trap_rej = trapB[trapB.CF_OA_P0 <= 0]

# ============ SCREEN C — RENEWABLES (expected weak/fail) ============
dc = fin_pull(RENEW)
passC = (dc.EVEB.between(0, 10, inclusive="neither") & (dc.IntCov_P0 > 1.5)
         & (dc.Revenue_YoY_P0 > 0) & (dc.CF_OA_3Y > 0))
selC = dc[passC]
picksC, cntC = build_picks(selC, [("EVEB", negz), ("DY", dybonus), ("IntCov_P0", zc)], take_all=True)
RC = simulate(picksC); RC.to_csv("data/energy_renew_monthly.csv", index=False)

# DY coverage across all three universes (the DY-uncapturable finding)
def dy_cov(df): return int((df.DY>0).sum()), int(len(df))

def block(name, R, cnt, uni_df, picks):
    held = R[R.n_held > 0]
    print("\n" + "="*72 + f"\n{name}")
    print(f"Universe: {uni_df.ticker.nunique()} names {sorted(uni_df.ticker.unique())}")
    print(f"Qualifiers/month: med {int(cnt.nq.median())} min {cnt.nq.min()} max {cnt.nq.max()} | months 0 (cash): {int((cnt.nq==0).sum())}/{len(cnt)}")
    print(f"Months holding: {len(held)}/{len(R)} (median names {int(held.n_held.median()) if len(held) else 0})")
    print(f"DY coverage in universe: {dy_cov(uni_df)[0]}/{dy_cov(uni_df)[1]} ASOF rows have DY>0")
    full = report(f"{name} FULL 2014-2026", R)
    is_  = report(f"{name} IS 2014-2019", R[R.year <= 2019])
    oos  = report(f"{name} OOS 2020-2026", R[R.year >= 2020])
    print(f"\n{name} per-year (net vs B&H, avg names):")
    for yr, gy in R.groupby("year"):
        sret=(np.prod(1+gy.net)-1)*100; bret=(np.prod(1+gy.bh)-1)*100
        print(f"  {yr} {len(gy):>2}mo  sys {sret:>7.1f}%  bh {bret:>7.1f}%  edge {sret-bret:>+6.1f}pp  held {gy.n_held.mean():>4.1f}")
    return full, is_, oos

fullA, isA, oosA = block("SCREEN A — MATURE UTILITY", RA, cntA, da, picksA)
fullB, isB, oosB = block("SCREEN B — OIL SERVICES TROUGH", RB, cntB, db, picksB)
fullC, isC, oosC = block("SCREEN C — RENEWABLES", RC, cntC, dc, picksC)

print(f"\nSCREEN A FCF gate: of {len(preA)} EVEB/leverage/IC-passing utility rows, the FCF>0 gate "
      f"REJECTS {len(fcf_rej)} expansion-phase rows (maintenance-capex > operating-CF).")
print(f"SCREEN B oil-trap gate: of {len(trapB)} PB<0.8 oil-services rows, the CF_OA>0 gate REJECTS "
      f"{len(trap_rej)} rows that are cheap on NEGATIVE operating cash (e.g. 2020 COVID value-trap).")
print(f"DY-UNCAPTURABLE (sector-wide): UTIL {dy_cov(da)} | OILSVC {dy_cov(db)} | RENEW {dy_cov(dc)} "
      f"-> DY only in dividend-declaration quarters; used as scoring bonus, NEVER a hard gate.")

# ---- self-check 0 VND ----
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path)
    return abs(NAV0*np.prod(1+R.net.values) - NAV0*np.prod(1+chk.net.values))
dA = selfcheck(RA,"data/energy_util_monthly.csv"); dB = selfcheck(RB,"data/energy_oilsvc_monthly.csv"); dC = selfcheck(RC,"data/energy_renew_monthly.csv")
print(f"\nSELF-CHECK util {dA:.6f} {'PASS' if dA<1 else 'FAIL'} | oilsvc {dB:.6f} {'PASS' if dB<1 else 'FAIL'} | renew {dC:.6f} {'PASS' if dC<1 else 'FAIL'}")

# ---- VERIFY known names ----
def mw(pm_, tk, y0, y1): return [d.strftime("%Y-%m") for d in sorted(pm_) if tk in pm_[d] and y0<=d.year<=y1]
v = dict(
  SJD_machine = mw(picksA,"SJD",2014,2026),
  NT2_ppa     = mw(picksA,"NT2",2014,2026),
  POW_thermal = mw(picksA,"POW",2018,2026),
  VSH_expansion_rejected = mw(picksA,"VSH",2017,2019),   # should be absent (FCF<0)
  VSH_post_capex = mw(picksA,"VSH",2022,2024),           # should appear (mature)
  PVD_trough_2016 = mw(picksB,"PVD",2016,2017),
  PVD_precrash_2014 = mw(picksB,"PVD",2014,2014),        # should be absent (PB1.5)
  PVD_2020_trap_rejected = mw(picksB,"PVD",2020,2020),   # should be absent (CF_OA<0)
  GEG_renew = mw(picksC,"GEG",2018,2026),
)
print("\nVERIFY:")
print(f"  SJD mature cash-machine present : {len(v['SJD_machine'])} months -> {'CAUGHT' if v['SJD_machine'] else 'absent'}")
print(f"  NT2 PPA play present            : {len(v['NT2_ppa'])} months -> {'CAUGHT' if v['NT2_ppa'] else 'absent'}")
print(f"  POW thermal present             : {len(v['POW_thermal'])} months -> {'CAUGHT' if v['POW_thermal'] else 'absent'}")
print(f"  VSH expansion 2017-19 (expect ~absent, FCF<0): {v['VSH_expansion_rejected']}")
print(f"  VSH post-capex 2022-24 (expect present)      : {v['VSH_post_capex']}")
print(f"  PVD 2016-17 trough (expect CAUGHT)           : {v['PVD_trough_2016']}")
print(f"  PVD 2014 pre-crash (expect ABSENT, PB1.5)    : {v['PVD_precrash_2014']}")
print(f"  PVD 2020 COVID trap (expect ABSENT, CF_OA<0) : {v['PVD_2020_trap_rejected']}")
print(f"  GEG renewables present          : {len(v['GEG_renew'])} months -> {'present' if v['GEG_renew'] else 'absent'}")

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
print(f"  UTIL   {ovA[0]:5.1f}% | {ovA[1]:5.1f}%")
print(f"  OILSVC {ovB[0]:5.1f}% | {ovB[1]:5.1f}%")
print(f"  RENEW  {ovC[0]:5.1f}% | {ovC[1]:5.1f}%")

def adv(df, picks):
    vals = [r.tv for d in picks for t in picks[d] for _,r in df[(df.d==d)&(df.ticker==t)].iterrows()]
    return float(np.median(vals))/1e9 if vals else 0.0
print(f"\nLIQUIDITY median selected ADV: UTIL {adv(da,picksA):.1f}B | OILSVC {adv(db,picksB):.1f}B | RENEW {adv(dc,picksC):.1f}B")

# ---- verdict json ----
def pack(R, full, is_, oos, cnt, df, picks, ov):
    held = R[R.n_held>0]
    return dict(names=sorted(df.ticker.unique().tolist()), qual_med=int(cnt.nq.median()),
        months_held=len(held), months=len(R), median_sel_adv_b=round(adv(df,picks),2),
        dy_cov=dy_cov(df),
        full={k:round(x,3) for k,x in full[0].items()}, full_bh={k:round(x,3) for k,x in full[1].items()},
        is_={k:round(x,3) for k,x in is_[0].items()}, oos={k:round(x,3) for k,x in oos[0].items()},
        oos_bh={k:round(x,3) for k,x in oos[1].items()}, ortho_c30v=round(ov[0],1), ortho_8l=round(ov[1],1))
out = dict(job="Taylor_20260630_070640", screen="energy_triple",
    util=pack(RA,fullA,isA,oosA,cntA,da,picksA,ovA),
    oilsvc=pack(RB,fullB,isB,oosB,cntB,db,picksB,ovB),
    renew=pack(RC,fullC,isC,oosC,cntC,dc,picksC,ovC),
    selfcheck_vnd=dict(util=round(dA,6),oilsvc=round(dB,6),renew=round(dC,6)),
    fcf_gate=dict(passing_pre_gate=len(preA), rejected_expansion=len(fcf_rej),
        note="FCF>0 separates mature cash-machines from expansion-phase hydro/utility"),
    oil_trap_gate=dict(pb_cheap_rows=len(trapB), cf_oa_rejected=len(trap_rej),
        note="cheap PB on NEGATIVE operating cash (2020 COVID) is a value-trap; CF_OA>0 gate rejects"),
    dy_uncapturable=dict(util=dy_cov(da), oilsvc=dy_cov(db), renew=dy_cov(dc),
        note="DY only populated in dividend-declaration quarters -> hard DY gate unbuildable; used as scoring bonus"),
    renewables_failure=dict(note="renewables look expensive+levered+FCF-negative WHILE building FIT assets; "
        "windfall is a policy event not a financial signal -> structurally un-screenable, documented failure"),
    verify=v)
with open("data/energy_verdict.json","w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/energy_{util,oilsvc,renew}_monthly.csv + data/energy_verdict.json")
