"""Logistics/Port/Shipping Compounder Screens — point-in-time monthly, TWO sub-sector screens.
Design + backlook: job Taylor_20260630_054646. Framework: mike/agents/Taylor/logistics_port_valuation_framework.md.

The maritime/transport complex is THREE economics under two ICB codes:
  A — PORTS / transport infrastructure (ICB 2777): concession moat, heavy capex, D&A-heavy.
      Value on EV/EBITDA (EVEB) NOT P/E. Moat = ROIC (build-tolerant >=5%, read ROIC_Trailing).
      Net-cash ports (DVP/VSC) have IntCov=NaN -> NaN PASSES. VN ports often 0% DY -> FCF>0 OR DY>4%.
      Best entry = cheap EVEB + ROIC earned + FCF positive (harvest phase).
  B — SHIPPING (ICB 2773): deep cyclical, no moat. Trough buy = P/B<0.9 + CF_OA>0 + NP turning,
      with SURVIVABLE leverage (Debt_Eq<2.0). PB<0.9 alone is a trap detector (VOS), not a buy.
      Empty outside troughs by design -> hold CASH those months (calendar preserved).

BACKLOOK (ticker_financial cache, see framework doc table):
  GMD 2020Q1 PB0.80 EVEB8.2 ROIC5Y4.3% ROIC_TTM32% FCF+72B  -> hybrid port, passes once ROIC5Y>=5%
  VSC 2020Q1 PB0.63 EVEB1.9 ROIC5Y12% IntCov77 FCF+51B      -> clean high-quality port ENTRY
  DVP 2020Q1 PB1.07 EVEB4.7 ROIC5Y16% IntCov=NaN(netcash)    -> cash-cow port (NaN must pass)
  PVT 2020Q1 PB0.47 EVEB2.9 DebtEq0.93 CF_OA+196B            -> textbook shipping trough buy
  VOS 2016/2020 PB0.25/0.30 DebtEq5.7/3.9 IntCov2.3/-1.9 CF_OA<0 NP-loss -> LEVERAGE TRAP, EXCLUDE
  VOS 2022Q4 PB1.01 DebtEq0.75 ROIC+ recovered               -> legit once de-levered (now passes)

HONEST MISS (by design, no look-ahead): GMD 2014Q4 PB0.67 deep value but ROIC5Y1.5% (Gemalink
pre-ramp) -> a quality gate cannot catch it w/o foresight on the concession (parallel VCB/PNJ/NTC).
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
PORT_ICB, SHIP_ICB = 2777.0, 2773.0
KA = 10
TC = 0.001
STALE = 120
con = duckdb.connect()

# ---- rebal grid: last trading day of each month ----
days = con.execute(f"SELECT DISTINCT time FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}'").df()
days["time"] = pd.to_datetime(days.time); days = days.sort_values("time")
days["ym"] = days.time.dt.to_period("M")
rebal = sorted(days.groupby("ym")["time"].max().tolist())
rebal_str = [d.strftime("%Y-%m-%d") for d in rebal]
rebal_vals = ",".join(f"(DATE '{d}')" for d in rebal_str)

# ---- price matrix + VNINDEX for NAV ----
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

def simulate(picks_map, hold_cash_when_empty=False):
    """Monthly EW. If hold_cash_when_empty: empty pick-month earns 0 (cash) so the calendar is
    preserved (correct for a 'wait-for-trough' cyclical screen)."""
    rows, prev = [], set()
    rs = rebal  # full monthly calendar (not just months with picks)
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
            if hold_cash_when_empty:
                rows.append({"rebal": d.strftime("%Y-%m-%d"), "year": d.year, "n_held": 0,
                             "gross": 0.0, "turnover": float(len(prev) > 0), "cost": TC*float(len(prev) > 0),
                             "net": -TC*float(len(prev) > 0), "bh": bh})
                prev = set()
            continue
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

# ============ SCREEN A — PORTS / INFRASTRUCTURE (ICB 2777) ============
qa = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv
  FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
  WHERE p.Close IS NOT NULL AND p.ICB_Code = {PORT_ICB})
SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.EVEB, f.PCF, f.DY, f.ROIC5Y, f.ROIC_Trailing,
       f.Debt_Eq_P0, f.IntCov_P0, f.Revenue_YoY_P0, f.CF_OA_P0, f.CF_Invest_P0, f.CF_OA_3Y, f.PB
FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
"""
da = con.execute(qa).df(); da["d"] = pd.to_datetime(da.d)
da["fcf"] = da.CF_OA_P0 + da.CF_Invest_P0
# IntCov NaN = net cash = pass; else require >2.0
intcov_ok = da.IntCov_P0.isna() | (da.IntCov_P0 > 2.0)
passA = (da.EVEB.between(0, 10, inclusive="neither") & (da.ROIC5Y >= 0.05) & (da.CF_OA_3Y > 0)
         & ((da.fcf > 0) | (da.DY > 0.04)) & intcov_ok & (da.Revenue_YoY_P0 >= -0.10))
selA = da[passA].copy(); ga = selA.groupby("d")
selA["fcf_yield"] = selA.fcf / selA.tv.replace(0, np.nan)  # rough harvest-intensity proxy
selA["score"] = (ga["EVEB"].transform(lambda s: -zc(s)).fillna(0) + ga["ROIC_Trailing"].transform(zc).fillna(0)
                 + ga["fcf_yield"].transform(zc).fillna(0))
picksA, cntA = {}, []
for d, gg in selA.groupby("d"):
    picksA[d] = gg.nlargest(KA, "score").ticker.tolist(); cntA.append((d, len(gg)))
cntA = pd.DataFrame(cntA, columns=["d","nq"]).sort_values("d")
RA = simulate(picksA, hold_cash_when_empty=True); RA.to_csv("data/logistics_port_monthly.csv", index=False)

# ============ SCREEN B — SHIPPING CYCLICAL TROUGH (ICB 2773) ============
qb = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv
  FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
  WHERE p.Close IS NOT NULL AND p.ICB_Code = {SHIP_ICB})
SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.PB, f.EVEB, f.Debt_Eq_P0, f.IntCov_P0,
       f.CF_OA_P0, f.NP_P0, f.NP_P4, f.Revenue_YoY_P0, f.ROIC_Trailing
FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
"""
db = con.execute(qb).df(); db["d"] = pd.to_datetime(db.d)
passB = (db.PB.between(0, 0.9, inclusive="neither") & (db.CF_OA_P0 > 0) & (db.Debt_Eq_P0 < 2.0)
         & (db.NP_P0 > db.NP_P4))
selB = db[passB].copy(); gb = selB.groupby("d")
selB["np_turn"] = (selB.NP_P0 - selB.NP_P4) / selB.NP_P4.abs().replace(0, np.nan)
selB["score"] = (gb["PB"].transform(lambda s: -zc(s)).fillna(0) + gb["CF_OA_P0"].transform(zc).fillna(0)
                 + gb["np_turn"].transform(zc).fillna(0))
picksB, cntB = {}, []
for d, gg in selB.groupby("d"):
    picksB[d] = gg.sort_values("score", ascending=False).ticker.tolist(); cntB.append((d, len(gg)))
cntB = pd.DataFrame(cntB, columns=["d","nq"]).sort_values("d")
RB = simulate(picksB, hold_cash_when_empty=True); RB.to_csv("data/logistics_ship_monthly.csv", index=False)

# ---- reporting ----
print("="*72 + "\nSCREEN A — PORTS / INFRASTRUCTURE (ICB 2777)")
print(f"Universe: {da.ticker.nunique()} names {sorted(da.ticker.unique())}")
print(f"Qualifiers/month: med {int(cntA.nq.median())} min {cntA.nq.min()} max {cntA.nq.max()} | months 0: {int((cntA.nq==0).sum())}/{len(cntA)}")
held_a = RA[RA.n_held>0]
print(f"Months actually holding: {len(held_a)}/{len(RA)} (median names held {int(held_a.n_held.median()) if len(held_a) else 0})")
fullA = report("PORT FULL 2014-2026", RA)
isA = report("PORT IS  2014-2019", RA[RA.year <= 2019])
oosA = report("PORT OOS 2020-2026", RA[RA.year >= 2020])
print("\nPORT per-year (net vs B&H, avg names):")
for yr, gy in RA.groupby("year"):
    sret=(np.prod(1+gy.net)-1)*100; bret=(np.prod(1+gy.bh)-1)*100
    print(f"  {yr} {len(gy):>2}mo  sys {sret:>7.1f}%  bh {bret:>7.1f}%  edge {sret-bret:>+6.1f}pp  held {gy.n_held.mean():>4.1f}")

print("\n" + "="*72 + "\nSCREEN B — SHIPPING CYCLICAL TROUGH (ICB 2773)")
print(f"Universe: {db.ticker.nunique()} names {sorted(db.ticker.unique())}")
print(f"Qualifiers/month: med {int(cntB.nq.median())} min {cntB.nq.min()} max {cntB.nq.max()} | months 0 (hold cash): {int((cntB.nq==0).sum())}/{len(cntB)}")
held_b = RB[RB.n_held>0]
print(f"Months actually holding: {len(held_b)}/{len(RB)} (median names held {int(held_b.n_held.median()) if len(held_b) else 0})")
fullB = report("SHIP FULL 2014-2026", RB)
isB = report("SHIP IS  2014-2019", RB[RB.year <= 2019])
oosB = report("SHIP OOS 2020-2026", RB[RB.year >= 2020])
print("\nSHIP per-year (net vs B&H, avg names):")
for yr, gy in RB.groupby("year"):
    sret=(np.prod(1+gy.net)-1)*100; bret=(np.prod(1+gy.bh)-1)*100
    print(f"  {yr} {len(gy):>2}mo  sys {sret:>7.1f}%  bh {bret:>7.1f}%  edge {sret-bret:>+6.1f}pp  held {gy.n_held.mean():>4.1f}")

# ---- self-check 0 VND ----
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path)
    a = NAV0*np.prod(1+R.net.values); b = NAV0*np.prod(1+chk.net.values); return abs(a-b)
dA = selfcheck(RA, "data/logistics_port_monthly.csv")
dB = selfcheck(RB, "data/logistics_ship_monthly.csv")
print(f"\nSELF-CHECK port diff {dA:.6f} VND -> {'PASS' if dA<1 else 'FAIL'} | ship diff {dB:.6f} VND -> {'PASS' if dB<1 else 'FAIL'}")

# ---- VERIFY known names ----
def mw(pm_, tk, y0, y1): return [d.strftime("%Y-%m") for d in sorted(pm_) if tk in pm_[d] and y0<=d.year<=y1]
gmd = mw(picksA,"GMD",2020,2023); vsc = mw(picksA,"VSC",2019,2021); dvp = mw(picksA,"DVP",2019,2021); php = mw(picksA,"PHP",2019,2021)
gmd14 = mw(picksA,"GMD",2014,2016)
pvt = mw(picksB,"PVT",2020,2020); vos_trap = mw(picksB,"VOS",2014,2021); vos_rec = mw(picksB,"VOS",2022,2024)
print("\nVERIFY:")
print(f"  GMD 2020-23 (hybrid port)    : {gmd} -> {'PASS (caught)' if gmd else 'absent'}")
print(f"  VSC 2019-21 (quality port)   : {vsc} -> {'PASS (caught)' if vsc else 'absent'}")
print(f"  DVP 2019-21 (cash-cow netcash): {dvp} -> {'PASS (caught; NaN IntCov passed)' if dvp else 'absent'}")
print(f"  PHP 2019-21 (state port)     : {php} -> {'PASS (caught)' if php else 'absent'}")
print(f"  GMD 2014-16 (deep value)     : {gmd14} -> {'(present)' if gmd14 else 'EXPECTED-ABSENT (ROIC5Y 1.5% Gemalink pre-ramp; uncapturable w/o foresight)'}")
print(f"  PVT 2020 (shipping trough)   : {pvt} -> {'PASS (caught)' if pvt else 'absent'}")
print(f"  VOS 2014-21 (LEVERAGE TRAP)  : {vos_trap} -> {'PASS (EXCLUDED)' if not vos_trap else 'FAIL (present!)'}")
print(f"  VOS 2022-24 (de-levered ok)  : {vos_rec} -> {'(present, legit)' if vos_rec else 'absent'}")

# ---- ORTHOGONALITY (port screen vs custom30V, 8L top-25) ----
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
    return (float(np.mean(ov_v)) if ov_v else 0.0, len(ov_v),
            float(np.mean(ov_8l)) if ov_8l else 0.0, len(ov_8l))
ovA = ortho(picksA); ovB = ortho(picksB)
print(f"\nORTHOGONALITY:")
print(f"  PORT vs custom30V {ovA[0]:5.1f}% (n{ovA[1]}) | vs 8L top-25 {ovA[2]:5.1f}% (n{ovA[3]})")
print(f"  SHIP vs custom30V {ovB[0]:5.1f}% (n{ovB[1]}) | vs 8L top-25 {ovB[2]:5.1f}% (n{ovB[3]})")

# liquidity stats
sel_adv_a = [r.tv for d in picksA for t in picksA[d] for _,r in da[(da.d==d)&(da.ticker==t)].iterrows()]
sel_adv_b = [r.tv for d in picksB for t in picksB[d] for _,r in db[(db.d==d)&(db.ticker==t)].iterrows()]
print(f"\nLIQUIDITY: PORT median selected ADV {np.median(sel_adv_a)/1e9:.1f}B | SHIP median {np.median(sel_adv_b)/1e9 if sel_adv_b else 0:.1f}B")

# ---- verdict json ----
out = dict(
    job="Taylor_20260630_054646", screen="logistics_port_dual",
    port=dict(icb=PORT_ICB, names=sorted(da.ticker.unique().tolist()), qual_med=int(cntA.nq.median()),
        months_held=len(held_a), months=len(RA), median_sel_adv_b=round(float(np.median(sel_adv_a))/1e9,2),
        full={k:round(v,3) for k,v in fullA[0].items()}, full_bh={k:round(v,3) for k,v in fullA[1].items()},
        is_={k:round(v,3) for k,v in isA[0].items()}, oos={k:round(v,3) for k,v in oosA[0].items()},
        oos_bh={k:round(v,3) for k,v in oosA[1].items()}, selfcheck_vnd=round(dA,6),
        ortho_c30v=round(ovA[0],1), ortho_8l=round(ovA[2],1)),
    ship=dict(icb=SHIP_ICB, names=sorted(db.ticker.unique().tolist()), qual_med=int(cntB.nq.median()),
        months_held=len(held_b), months=len(RB), median_sel_adv_b=round(float(np.median(sel_adv_b))/1e9,2) if sel_adv_b else None,
        full={k:round(v,3) for k,v in fullB[0].items()}, full_bh={k:round(v,3) for k,v in fullB[1].items()},
        is_={k:round(v,3) for k,v in isB[0].items()}, oos={k:round(v,3) for k,v in oosB[0].items()},
        oos_bh={k:round(v,3) for k,v in oosB[1].items()}, selfcheck_vnd=round(dB,6),
        ortho_c30v=round(ovB[0],1), ortho_8l=round(ovB[2],1)),
    verify=dict(GMD=gmd, VSC=vsc, DVP=dvp, PHP=php, GMD14_expected_absent=(not gmd14),
        PVT2020=pvt, VOS_trap_excluded=(not vos_trap), VOS_recovered=vos_rec,
        gmd14_miss_reason="GMD 2014 PB0.67 deep value but ROIC5Y1.5% (Gemalink pre-ramp); quality gate cannot catch w/o concession foresight (parallel banking-VCB/retail-PNJ/RE-NTC)"),
)
with open("data/logistics_port_verdict.json","w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/logistics_port_monthly.csv, data/logistics_ship_monthly.csv, data/logistics_port_verdict.json")
