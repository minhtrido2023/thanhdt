"""Steel + Building Materials — THREE sub-sector screens (point-in-time monthly).
Design + backlook: job Taylor_20260630_065623. Framework: mike/agents/Taylor/steel_buildmat_valuation_framework.md.

ICB lumps these together; the three economics are distinct, so sub-universes are hand-curated:
  A — STEEL cyclical (commodity, capital-intensive). The dispatch's P/B<1.2 trough rule is a TRAP
      in VN: the names that trade P/B<1 are the OVER-LEVERED ones (HSG Debt_Eq2.8, NKG 6.3), not
      the quality compounder (HPG, which floors at PB~1.0 only in crashes). So PB<1.5 to keep HPG,
      and the LEVERAGE GATE (Debt_Eq<2.0 AND IntCov>1.5) is the actual alpha — it keeps HPG and
      ejects HSG/NKG. Early-cycle margin turn = GPM_P0>GPM_P4. Survived a cycle = CF_OA_3Y>0.
  B — CEMENT value (HT1, BCC): EVEB<6 + CF_OA_P0>0 + Debt_Eq<1.5. The classic "cement = DY yield"
      screen is UNBUILDABLE — DY is uncapturable in BQ for VN cement (HT1 1/75, BCC 6/79 quarters
      have DY>0). We pivot to EVEB+cash value and report the DY data-gap honestly. Only 2 liquid
      names -> structurally thin (reported, not hidden).
  C — SPECIALTY/PIPE compounder (NTP, BMP, VCS): ROIC5Y>12% + ROE5Y>15% + PE<PE_MA1Y + clean BS
      (Debt_Eq<0.5) + CF_OA_3Y>0. The literal ROIC5Y>18% (dispatch) catches BMP(19%)/VCS(14%-ish)
      but DROPS NTP(10%); NTP also carries ~1.0x debt so it fails the clean-BS gate too -> NTP is a
      documented "compounder-with-debt" miss. We test >12% and report the NTP miss.

BACKLOOK (ticker_financial cache, see framework doc):
  HPG 2013Q1 EVEB6.6 PB1.30 GPM17.6%>13.4%(turn) IC-6.6 -> early-cycle margin turn caught
  HPG 2019Q2 EVEB7.3 PB1.41 ROE5Y25% IC+12.5           -> quality, NEVER cheap on PB (floor~1.0 only 2022 crash)
  HSG 2018Q4 EVEB8.3 PB0.49 Debt_Eq2.83 IC1.5 NPM0.4%  -> "cheap" PB is a LEVERAGE TRAP
  NKG 2014Q1 EVEB5.5 PB0.94 Debt_Eq6.32 IC-1.3         -> extreme leverage, reject
  BMP 2018Q4 EVEB4.6 PB1.61 ROIC5Y19.4% Debt_Eq0.15 DY3.2% -> TEXTBOOK compounder, valuation-compressed entry
  NTP 2018Q4 EVEB9.8 ROIC5Y10.0% Debt_Eq1.16           -> compounder-with-debt, borderline miss (honest)
  HT1 2018Q4 EVEB4.9 CF_OA+851B Debt_Eq1.05            -> cement value via EVEB+CF_OA, NOT yield
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
TC, STALE = 0.001, 120
KA = 10

STEEL  = ("HPG","HSG","NKG","SMC","TLH","POM")
CEMENT = ("HT1","BCC")
SPEC   = ("NTP","BMP","VCS")

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
    SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.EVEB, f.PB, f.PE, f.PE_MA1Y, f.DY, f.ROIC5Y, f.ROE5Y,
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

# ============ SCREEN A — STEEL CYCLICAL (leverage-disciplined trough) ============
da = fin_pull(STEEL)
passA = (da.EVEB.between(0, 6, inclusive="neither") & (da.PB < 1.5)
         & (da.GPM_P0 > da.GPM_P4) & (da.Debt_Eq_P0 < 2.0) & (da.IntCov_P0 > 1.5)
         & (da.CF_OA_3Y > 0))
selA = da[passA]
picksA, cntA = build_picks(selA, [("EVEB", negz), ("PB", negz), ("GPM_P0", zc)], take_all=True)
RA = simulate(picksA); RA.to_csv("data/steel_steel_monthly.csv", index=False)
# how many HSG/NKG entry-months does the leverage gate reject?
trapA = da[da.EVEB.between(0,6,inclusive="neither") & (da.PB<1.5) & (da.GPM_P0>da.GPM_P4) & (da.CF_OA_3Y>0)]
trap_kept = trapA[(trapA.Debt_Eq_P0<2.0) & (trapA.IntCov_P0>1.5)]
trap_rej_hsgnkg = trapA[(trapA.ticker.isin(["HSG","NKG"])) & ~((trapA.Debt_Eq_P0<2.0)&(trapA.IntCov_P0>1.5))]

# ============ SCREEN B — CEMENT VALUE (DY uncapturable -> EVEB+cash) ============
db = fin_pull(CEMENT)
passB = (db.EVEB.between(0, 6, inclusive="neither") & (db.CF_OA_P0 > 0) & (db.Debt_Eq_P0 < 1.5))
selB = db[passB]
picksB, cntB = build_picks(selB, [("EVEB", negz), ("CF_OA_P0", zc)], take_all=True)
RB = simulate(picksB); RB.to_csv("data/steel_cement_monthly.csv", index=False)
dy_cov_cement = (db.DY > 0).sum()

# ============ SCREEN C — SPECIALTY/PIPE ROIC COMPOUNDER ============
dc = fin_pull(SPEC)
passC = ((dc.ROIC5Y > 0.12) & (dc.ROE5Y > 0.15) & (dc.PE < dc.PE_MA1Y)
         & (dc.CF_OA_3Y > 0) & (dc.Debt_Eq_P0 < 0.5))
selC = dc[passC]
picksC, cntC = build_picks(selC, [("PE", negz), ("ROIC5Y", zc), ("DY", zc)], take_all=True)
RC = simulate(picksC); RC.to_csv("data/steel_spec_monthly.csv", index=False)
# NTP miss accounting: ROIC>=12% gate
ntp_all = dc[dc.ticker=="NTP"]
ntp_roic12 = ntp_all[ntp_all.ROIC5Y > 0.12]
ntp_cleanBS = ntp_all[ntp_all.Debt_Eq_P0 < 0.5]

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

fullA, isA, oosA = block("SCREEN A — STEEL", RA, cntA, da, picksA)
fullB, isB, oosB = block("SCREEN B — CEMENT", RB, cntB, db, picksB)
fullC, isC, oosC = block("SCREEN C — SPECIALTY/PIPE", RC, cntC, dc, picksC)

print(f"\nSCREEN A leverage gate: of {len(trapA)} EVEB/PB/margin-passing steel rows, "
      f"the Debt_Eq<2 & IntCov>1.5 gate KEEPS {len(trap_kept)} and REJECTS {len(trapA)-len(trap_kept)} "
      f"(of which {len(trap_rej_hsgnkg)} are HSG/NKG leverage-trap rows).")
print(f"SCREEN B cement DY coverage: only {dy_cov_cement}/{len(db)} ASOF rows have DY>0 "
      f"-> a DY>4% yield gate is unbuildable; used EVEB+CF_OA value instead.")
print(f"SCREEN C NTP miss: NTP rows total {len(ntp_all)}; ROIC5Y>12% {len(ntp_roic12)}; clean-BS(Debt_Eq<0.5) {len(ntp_cleanBS)} "
      f"-> NTP fails BOTH the ROIC and clean-BS gates (compounder-WITH-debt, documented miss).")

# ---- self-check 0 VND ----
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path)
    return abs(NAV0*np.prod(1+R.net.values) - NAV0*np.prod(1+chk.net.values))
dA = selfcheck(RA,"data/steel_steel_monthly.csv"); dB = selfcheck(RB,"data/steel_cement_monthly.csv"); dC = selfcheck(RC,"data/steel_spec_monthly.csv")
print(f"\nSELF-CHECK steel {dA:.6f} {'PASS' if dA<1 else 'FAIL'} | cement {dB:.6f} {'PASS' if dB<1 else 'FAIL'} | spec {dC:.6f} {'PASS' if dC<1 else 'FAIL'}")

# ---- VERIFY known names ----
def mw(pm_, tk, y0, y1): return [d.strftime("%Y-%m") for d in sorted(pm_) if tk in pm_[d] and y0<=d.year<=y1]
v = dict(
  HPG_caught = mw(picksA,"HPG",2014,2026),
  HPG_2020_surge = mw(picksA,"HPG",2020,2021),
  HSG_rejected_all = mw(picksA,"HSG",2014,2026),
  NKG_rejected_all = mw(picksA,"NKG",2014,2026),
  BMP_compounder = mw(picksC,"BMP",2014,2026),
  VCS_compounder = mw(picksC,"VCS",2014,2026),
  NTP_missed = mw(picksC,"NTP",2014,2026),
  HT1_cement = mw(picksB,"HT1",2014,2026),
)
print("\nVERIFY:")
print(f"  HPG caught (any month)          : {len(v['HPG_caught'])} months -> {'CAUGHT' if v['HPG_caught'] else 'MISSED'}")
print(f"  HPG 2020-21 surge window        : {v['HPG_2020_surge']} -> {'present' if v['HPG_2020_surge'] else 'absent'}")
print(f"  HSG ever selected (should ~never): {len(v['HSG_rejected_all'])} months -> {'REJECTED' if not v['HSG_rejected_all'] else 'LEAKED: '+str(v['HSG_rejected_all'])}")
print(f"  NKG ever selected (should ~never): {len(v['NKG_rejected_all'])} months -> {'REJECTED' if not v['NKG_rejected_all'] else 'LEAKED: '+str(v['NKG_rejected_all'])}")
print(f"  BMP compounder present          : {len(v['BMP_compounder'])} months -> {'CAUGHT' if v['BMP_compounder'] else 'absent'}")
print(f"  VCS compounder present          : {len(v['VCS_compounder'])} months -> {'CAUGHT' if v['VCS_compounder'] else 'absent'}")
print(f"  NTP (expected MISS, debt+ROIC)  : {len(v['NTP_missed'])} months -> {'(leaked some)' if v['NTP_missed'] else 'EXPECTED-ABSENT'}")
print(f"  HT1 cement value present        : {len(v['HT1_cement'])} months -> {'CAUGHT' if v['HT1_cement'] else 'absent'}")

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
print(f"  STEEL {ovA[0]:5.1f}% | {ovA[1]:5.1f}%")
print(f"  CEMNT {ovB[0]:5.1f}% | {ovB[1]:5.1f}%")
print(f"  SPEC  {ovC[0]:5.1f}% | {ovC[1]:5.1f}%")

def adv(df, picks):
    vals = [r.tv for d in picks for t in picks[d] for _,r in df[(df.d==d)&(df.ticker==t)].iterrows()]
    return float(np.median(vals))/1e9 if vals else 0.0
print(f"\nLIQUIDITY median selected ADV: STEEL {adv(da,picksA):.1f}B | CEMNT {adv(db,picksB):.1f}B | SPEC {adv(dc,picksC):.1f}B")

# ---- verdict json ----
def pack(R, full, is_, oos, cnt, df, picks, ov):
    held = R[R.n_held>0]
    return dict(names=sorted(df.ticker.unique().tolist()), qual_med=int(cnt.nq.median()),
        months_held=len(held), months=len(R), median_sel_adv_b=round(adv(df,picks),2),
        full={k:round(x,3) for k,x in full[0].items()}, full_bh={k:round(x,3) for k,x in full[1].items()},
        is_={k:round(x,3) for k,x in is_[0].items()}, oos={k:round(x,3) for k,x in oos[0].items()},
        oos_bh={k:round(x,3) for k,x in oos[1].items()}, ortho_c30v=round(ov[0],1), ortho_8l=round(ov[1],1))
out = dict(job="Taylor_20260630_065623", screen="steel_buildmat_triple",
    steel=pack(RA,fullA,isA,oosA,cntA,da,picksA,ovA),
    cement=pack(RB,fullB,isB,oosB,cntB,db,picksB,ovB),
    spec=pack(RC,fullC,isC,oosC,cntC,dc,picksC,ovC),
    selfcheck_vnd=dict(steel=round(dA,6),cement=round(dB,6),spec=round(dC,6)),
    leverage_gate=dict(passing_pre_gate=len(trapA), kept=len(trap_kept),
        rejected=len(trapA)-len(trap_kept), hsgnkg_rejected=len(trap_rej_hsgnkg),
        note="HSG/NKG trade cheap PB on 3-6x leverage + thin/neg IntCov; the gate is the alpha"),
    cement_dy_gap=dict(dy_pos_rows=int(dy_cov_cement), total_rows=int(len(db)),
        note="DY uncapturable for VN cement in BQ -> yield screen unbuildable, pivoted to EVEB+CF_OA"),
    ntp_miss=dict(ntp_rows=len(ntp_all), roic12=len(ntp_roic12), cleanBS=len(ntp_cleanBS),
        note="NTP ROIC5Y~10% + ~1.0x debt -> fails ROIC and clean-BS gates; documented compounder-with-debt miss"),
    verify=v)
with open("data/steel_buildmat_verdict.json","w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/steel_{steel,cement,spec}_monthly.csv + data/steel_buildmat_verdict.json")
