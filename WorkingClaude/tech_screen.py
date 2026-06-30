"""Technology (IT services) — FPT timing-lens + small tradeable basket.
Design + backlook: job Taylor_20260630_071941. Framework: mike/agents/Taylor/tech_valuation_framework.md.

VN "tech" is NOT product/SaaS — it is IT SERVICES (offshore outsourcing for JP/US/KR) + system
integration + education, archetype Infosys/TCS/Wipro. STRUCTURAL REALITY: the liquid+quality
universe is essentially ONE name. In ticker_prune 2014->:
  FPT  continuously liquid, ADV 45->866B, ROIC5Y 12->17.7%, ROE5Y 22->27%, NPM 0.10->0.20 (genuine
       compounder: offshore IT grows faster + margin expands with scale)
  CMG  liquid only 2024+ (ADV<4B before); ROIC5Y 7.8% -> low-quality infra/cloud capex sink
  ELC  ROIC5Y 4-6%, ROE5Y 5-7%, project-lumpy RevYoY -> low quality
  ITD  micro-cap (<5B ADV), negative-earnings periods -> un-investable
  CTR  ROIC5Y 21-24% ROE5Y 28-30% (only name hitting the GLOBAL IT-svc ROIC bar) BUT it is Viettel
       Construction = tower-co/telecom-INFRA (NPM 0.04 construction margin), not software -> belongs
       to telecom, flagged borderline.

=> The dispatch's literal gate ROIC5Y>18 (calibrated to Infosys/TCS @ 25-30% ROIC) collapses the VN
   tech universe to ~empty: FPT only crosses 18 in 2025, because FPT's blended ROIC is diluted by
   capital-heavy FPT Telecom (fiber capex) + education. The honest VN structure is a SINGLE-NAME
   (FPT) TIMING LENS, not a sector book. We test BOTH gate variants and report the divergence.

PRIMARY SIGNAL (lens) — FPT cheap-vs-own-history timing:
  flag when PE < PE_MA1Y*0.9  AND ROIC5Y>0.12 AND ROE5Y>0.15 AND NPM_P0>=NPM_P4*0.85
  (RevYoY gate DELIBERATELY DROPPED for FPT: 2015-2018 RevYoY went -20..-50% purely from the
   FRT/Synnex divestment deconsolidation -- an artifact, not a decline; gating on it wrongly ejects
   the great 2018 entry. We report RevYoY's effect separately.)
  -> compute flagged vs unflagged forward-12M return.

TRADEABLE BASKET (honesty check) — FPT,CMG,ELC,ITD EW, hold qualifiers / cash when none, monthly,
  T+1, TC 0.1%, two gate variants:
    G_LIT  = dispatch-literal: PE<MA1Y*0.9 & ROIC5Y>0.18 & ROE5Y>0.15 & RevYoY>0.12 & NPM0>=NPM4*0.85
    G_VN   = VN-calibrated   : PE<MA1Y*0.9 & ROIC5Y>0.12 & ROE5Y>0.15 &                 NPM0>=NPM4*0.85
  IS 2014-19 / OOS 2020-26. Self-check 0 VND. AUDIT_END 2026-06-26.

BACKLOOK (financial cache):
  FPT 2018Q2 PE8.3/MA11.7 (=0.71 CHEAP) RevYoY-45% (divestment artifact) ROIC13% -> G_VN catches, G_LIT rejects (RevYoY). Great entry.
  FPT 2022Q3 PE15.3/MA20.0(=0.77 CHEAP) RevYoY+28% ROIC15.4% -> IT-spend-slowdown entry, both catch. FPT then ~doubled into 2024.
  FPT 2024Q4 PE28.7/MA26.2(=1.10 RICH)  -> correctly NOT flagged (euphoria top).
  FPT 2025Q1 PE19.7/MA26.8(=0.74 CHEAP) RevYoY+14% ROIC17.3% -> flagged.
  CTR ROIC5Y 21-24% (only global-bar passer) but tower-co/telecom-infra -> excluded from IT book.
  CMG ROIC5Y 7.8% -> never passes quality; liquid only 2024.
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
TC, STALE = 0.001, 120
KA = 10

IT_UNIV = ("FPT", "CMG", "ELC", "ITD")   # pure IT (CTR excluded -> telecom-infra)

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
negz = lambda s: -zc(s)

def simulate(picks_map):
    """Monthly EW, hold CASH when no qualifier (correct for a wait-for-cheap screen)."""
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
    SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.PE, f.PE_MA1Y, f.PB, f.EVEB, f.DY,
           f.ROIC5Y, f.ROE5Y, f.NPM_P0, f.NPM_P4, f.Revenue_YoY_P0, f.CF_OA_P0, f.Debt_Eq_P0
    FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
    WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
    """
    d = con.execute(q).df(); d["d"] = pd.to_datetime(d.d)
    return d

def build_picks(sel, score_cols):
    g = sel.groupby("d"); sel = sel.copy()
    sel["score"] = sum(g[c].transform(f).fillna(0) for c, f in score_cols)
    picks, cnt = {}, []
    for d, gg in sel.groupby("d"):
        picks[d] = gg.nlargest(KA, "score").ticker.tolist()
        cnt.append((d, len(gg)))
    return picks, pd.DataFrame(cnt, columns=["d","nq"]).sort_values("d")

# ===================== FPT TIMING LENS (primary signal) =====================
fpt = fin_pull(("FPT",)).sort_values("d").reset_index(drop=True)
fpt["close_now"] = [px.at[next_session(d), "FPT"] if next_session(d) in px.index else np.nan for d in fpt.d]
# forward 12M close: price at the rebal ~12 months later
fwd = []
for i, r in fpt.iterrows():
    tgt = r.d + pd.DateOffset(months=12)
    ns = next_session(tgt)
    fwd.append(px.at[ns, "FPT"] if (ns is not None and ns in px.index) else np.nan)
fpt["close_fwd12"] = fwd
fpt["fwd12m"] = (fpt.close_fwd12 / fpt.close_now - 1.0) * 100
fpt["cheap"] = fpt.PE < fpt.PE_MA1Y * 0.9
fpt["quality"] = (fpt.ROIC5Y > 0.12) & (fpt.ROE5Y > 0.15) & (fpt.NPM_P0 >= fpt.NPM_P4 * 0.85)
fpt["flagged"] = fpt.cheap & fpt.quality
# RevYoY variant (shows the divestment artifact damage)
fpt["flagged_revyoy"] = fpt.flagged & (fpt.Revenue_YoY_P0 > 0.12)
fpt.to_csv("data/tech_fpt_lens.csv", index=False)

def lens_stat(mask):
    s = fpt[mask & fpt.fwd12m.notna()].fwd12m
    return len(s), (s.mean() if len(s) else float("nan")), ((s > 0).mean()*100 if len(s) else float("nan"))

fl_n, fl_m, fl_w = lens_stat(fpt.flagged)
un_n, un_m, un_w = lens_stat(~fpt.flagged)
rv_n, rv_m, rv_w = lens_stat(fpt.flagged_revyoy)
print("="*72)
print("FPT TIMING LENS — cheap(PE<PE_MA1Y*0.9) + quality(ROIC5Y>12 & ROE5Y>15 & NPM stable)")
print(f"  monthly snapshots with fwd-12M defined: {int(fpt.fwd12m.notna().sum())}")
print(f"  FLAGGED   : n={fl_n:3d}  avg fwd-12M={fl_m:+6.1f}%  winrate={fl_w:4.0f}%")
print(f"  UNFLAGGED : n={un_n:3d}  avg fwd-12M={un_m:+6.1f}%  winrate={un_w:4.0f}%")
print(f"  SPREAD (flagged-unflagged) = {fl_m-un_m:+.1f}pp")
print(f"  + RevYoY>12% gate added (divestment-artifact trap): n={rv_n:3d}  avg fwd-12M={rv_m:+6.1f}%  "
      f"-> drops {fl_n-rv_n} flagged months (incl. the 2018 deconsolidation entry)")

# ===================== TRADEABLE BASKET (two gate variants) =====================
du = fin_pull(IT_UNIV)
g_lit = (du.PE < du.PE_MA1Y*0.9) & (du.ROIC5Y > 0.18) & (du.ROE5Y > 0.15) \
        & (du.Revenue_YoY_P0 > 0.12) & (du.NPM_P0 >= du.NPM_P4*0.85)
g_vn  = (du.PE < du.PE_MA1Y*0.9) & (du.ROIC5Y > 0.12) & (du.ROE5Y > 0.15) \
        & (du.NPM_P0 >= du.NPM_P4*0.85)
selL, selV = du[g_lit], du[g_vn]
picksL, cntL = build_picks(selL, [("PE", negz), ("ROIC5Y", zc)])
picksV, cntV = build_picks(selV, [("PE", negz), ("ROIC5Y", zc)])
RL = simulate(picksL); RL.to_csv("data/tech_basket_lit_monthly.csv", index=False)
RV = simulate(picksV); RV.to_csv("data/tech_basket_vn_monthly.csv", index=False)

def block(name, R, cnt, picks, sel):
    held = R[R.n_held > 0]
    print("\n" + "="*72 + f"\n{name}")
    print(f"Universe: {sorted(IT_UNIV)} | qualifying picks span: {sorted(set(sel.ticker))}")
    print(f"Qualifiers/month: med {int(cnt.nq.median()) if len(cnt) else 0} max {cnt.nq.max() if len(cnt) else 0} | months holding: {len(held)}/{len(R)}")
    full = report(f"{name} FULL 2014-2026", R)
    is_  = report(f"{name} IS 2014-2019", R[R.year <= 2019])
    oos  = report(f"{name} OOS 2020-2026", R[R.year >= 2020])
    print(f"\n{name} per-year (net vs B&H, avg names held):")
    for yr, gy in R.groupby("year"):
        sret=(np.prod(1+gy.net)-1)*100; bret=(np.prod(1+gy.bh)-1)*100
        print(f"  {yr} {len(gy):>2}mo  sys {sret:>7.1f}%  bh {bret:>7.1f}%  edge {sret-bret:>+6.1f}pp  held {gy.n_held.mean():>4.1f}")
    return full, is_, oos

fullL, isL, oosL = block("G_LIT (dispatch-literal ROIC>18 + RevYoY>12)", RL, cntL, picksL, selL)
fullV, isV, oosV = block("G_VN  (VN-calibrated ROIC>12, no RevYoY gate)", RV, cntV, picksV, selV)

# ---- self-check 0 VND ----
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path)
    return abs(NAV0*np.prod(1+R.net.values) - NAV0*np.prod(1+chk.net.values))
dL = selfcheck(RL,"data/tech_basket_lit_monthly.csv"); dV = selfcheck(RV,"data/tech_basket_vn_monthly.csv")
print(f"\nSELF-CHECK lit {dL:.6f} {'PASS' if dL<1 else 'FAIL'} | vn {dV:.6f} {'PASS' if dV<1 else 'FAIL'}")

# ---- VERIFY known windows ----
def mw(picks, tk, y0, y1): return [d.strftime("%Y-%m") for d in sorted(picks) if tk in picks[d] and y0<=d.year<=y1]
v = dict(
  FPT_2018_divest_VN = mw(picksV,"FPT",2018,2018),   # G_VN should catch (RevYoY artifact ignored)
  FPT_2018_divest_LIT = mw(picksL,"FPT",2018,2018),  # G_LIT should MISS (RevYoY<0)
  FPT_2022_slowdown  = mw(picksV,"FPT",2022,2023),   # both should catch
  FPT_2024_euphoria  = mw(picksV,"FPT",2024,2024),   # should be ~absent (PE rich)
  FPT_2025_cheap     = mw(picksV,"FPT",2025,2025),
)
print("\nVERIFY:")
print(f"  FPT 2018 divestment entry  G_VN  (expect CAUGHT): {v['FPT_2018_divest_VN']}")
print(f"  FPT 2018 divestment entry  G_LIT (expect MISSED, RevYoY<0): {v['FPT_2018_divest_LIT']}")
print(f"  FPT 2022-23 IT-slowdown entry (expect CAUGHT): {v['FPT_2022_slowdown']}")
print(f"  FPT 2024 euphoria (expect ~ABSENT, PE rich)  : {v['FPT_2024_euphoria']}")
print(f"  FPT 2025 cheap re-entry                       : {v['FPT_2025_cheap']}")

# ---- ORTHOGONALITY (vs custom30V | 8L top-25) ----
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
ovL, ovV = ortho(picksL), ortho(picksV)
print("\nORTHOGONALITY (vs custom30V | vs 8L top-25):")
print(f"  G_LIT {ovL[0]:5.1f}% | {ovL[1]:5.1f}%")
print(f"  G_VN  {ovV[0]:5.1f}% | {ovV[1]:5.1f}%")

def adv(df, picks):
    vals = [r.tv for d in picks for t in picks[d] for _,r in df[(df.d==d)&(df.ticker==t)].iterrows()]
    return float(np.median(vals))/1e9 if vals else 0.0
print(f"\nLIQUIDITY median selected ADV: G_LIT {adv(du,picksL):.1f}B | G_VN {adv(du,picksV):.1f}B")

# ---- verdict json ----
def pack(R, full, is_, oos, cnt, picks, ov):
    held = R[R.n_held>0]
    return dict(qual_med=int(cnt.nq.median()) if len(cnt) else 0, months_held=len(held), months=len(R),
        median_sel_adv_b=round(adv(du,picks),2),
        full={k:round(x,3) for k,x in full[0].items()}, full_bh={k:round(x,3) for k,x in full[1].items()},
        is_={k:round(x,3) for k,x in is_[0].items()}, oos={k:round(x,3) for k,x in oos[0].items()},
        oos_bh={k:round(x,3) for k,x in oos[1].items()}, ortho_c30v=round(ov[0],1), ortho_8l=round(ov[1],1))
out = dict(job="Taylor_20260630_071941", screen="tech_it_services",
    structural_reality="VN tech = IT services (Infosys/TCS archetype); liquid+quality universe is "
        "essentially ONE name (FPT). CMG ROIC5Y 7.8% + liquid only 2024; ELC/ITD low-quality micro-caps; "
        "CTR (ROIC 21-24%) is a Viettel tower-co/telecom-infra, not software.",
    dispatch_gate_problem="ROIC5Y>18 is an Infosys/TCS bar (25-30% ROIC); FPT runs blended 12-17% "
        "because FPT Telecom (fiber capex) + education dilute the pure-IT ROIC -> FPT crosses 18 only "
        "in 2025. Literal gate collapses the universe to ~empty. VN-calibrated bar = ROIC5Y>12.",
    revyoy_artifact="FPT RevYoY went -20..-50% in 2015-2018 purely from FRT/Synnex divestment "
        "(deconsolidation), not a real decline -> a RevYoY>12% gate wrongly ejects the great 2018 entry.",
    fpt_lens=dict(flagged_n=fl_n, flagged_fwd12m=round(fl_m,1), flagged_winrate=round(fl_w,0),
        unflagged_n=un_n, unflagged_fwd12m=round(un_m,1), spread_pp=round(fl_m-un_m,1),
        revyoy_drops=fl_n-rv_n),
    basket_lit=pack(RL,fullL,isL,oosL,cntL,picksL,ovL),
    basket_vn=pack(RV,fullV,isV,oosV,cntV,picksV,ovV),
    selfcheck_vnd=dict(lit=round(dL,6), vn=round(dV,6)),
    verify=v)
with open("data/tech_verdict.json","w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/tech_fpt_lens.csv + data/tech_basket_{lit,vn}_monthly.csv + data/tech_verdict.json")
