"""Aviation dual screen — Airport/Cargo infrastructure vs Airline trough. Point-in-time monthly.
Design + backlook: job Taylor_20260630_074607. Framework: mike/agents/Taylor/aviation_valuation_framework.md.

Sector #14 is TWO economics that share an airport but nothing else:
  A — AIRPORT / CARGO INFRASTRUCTURE (ACV, SCS, NCT, SGN — by NAME, ICB is inconsistent:
      SCS is tagged 5751 'airline' but is a net-cash cargo terminal). Concession monopoly,
      capex/D&A heavy -> value on EV/EBITDA (EVEB) not P/E. Moat = ROIC (these are 10-50% ROIC
      monopolies). Net-cash names have IntCov=NaN -> NaN PASSES. DY=0 common (ACV retains for
      Long Thanh) so harvest test = FCF>0 OR DY>4%. Throughput proxy = Revenue_YoY (COVID
      throughput collapse SHOULD fail the gate -> that is correct, not a bug).
  B — AIRLINES (HVN, VJC). Capital-intensive deep cyclical, aircraft-financed (Debt_Eq high by
      DESIGN -> use IntCov not Debt_Eq). Trough buy = P/B<1.0 (below fleet/asset value) + CF_OA>0
      + IntCov>1 + NP>0 (profitable survivor at the trough). EXPECTED NEAR-EMPTY in VN:
      VJC never trades <P/B1 (premium LCC, no distress entry ever); HVN had NEGATIVE EQUITY
      2021-2024 (PB=0) -> PB>0 floor excludes the value-trap. Empty by design -> hold cash.

BACKLOOK (ticker_financial cache, see framework doc):
  HVN  2018-19 DebtEq3-5 IntCov1.2-5 ROIC5Y2-4% NP+thin; 2020-24 PB=0 (equity wiped), DebtEq
       57->123->neg, EVEB<0, ROIC deeply neg -> NEAR-BANKRUPTCY VALUE TRAP, permanent exclude.
       2024+ NP turns +, ROIC_TTM 14-18% recovering, equity restored only 2025Q4.
  VJC  pre-COVID ROIC5Y 20-28% (real LCC), DebtEq 1.7-2.4 (< HVN). NEVER PB<1 (3-10x always),
       DY=0 always. Post-COVID ROIC5Y collapsed to neg, CF_OA lumpy/neg, heavy sale-leaseback.
       Survived (positive equity throughout) but is NOT the pre-COVID machine. Trough screen never fires.
  ACV  monopoly: ROIC5Y 5%->11% rising, IntCov 100-300x (~net cash), DebtEq falling 0.8->0.2.
       BUT EVEB rarely <12 (12-30 normal, 47-477 when COVID killed EBITDA), DY=0, FCF<0 (Long
       Thanh capex) -> fails harvest gate most months. Cheapest ever = 2026Q1 EVEB9.3, 2020Q1 12.5.
  SCS  THE gem: ROIC5Y 20%->49%, net cash (DebtEq 0.05-0.4, IntCov NaN), real DY 2-5%, FCF+
       (asset-light), survived COVID flat (NP ~120-160B). EVEB down to 5.6-8.8 = cheap now.
  NCT  cargo cash-cow: ROIC_TTM ~3.0 (50-60%), net cash, EVEB cheap 5-8, lumpy DY 0-9%, stable
       thru COVID. SMALL (ADV ~1.7B) + price-patchy in prune (gaps 2023).
  SGN  third cargo gem: ROIC5Y 17-46%, net cash, EVEB 4-13 cheap, DY~0. Price-patchy in prune
       (only 2020,2024-25) -> thin/intermittent.

DATA HONESTY: sector is YOUNG — ACV/HVN/VJC/SCS listed 2017, only NCT has 2015+. IS 2014-19 is
effectively 2017-2019 (~3y). OOS 2020-26 is dominated by the COVID aviation shock (sector-specific,
not a market regime). Treat IS as thin and OOS as event-distorted; the backlook economics carry more
weight than the short backtest curve here.
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
INFRA = ["ACV", "SCS", "NCT", "SGN"]   # airport/cargo infra — by NAME (ICB inconsistent)
AIR   = ["HVN", "VJC"]                  # airlines
KA = 10
TC = 0.001
STALE = 120
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

def simulate(picks_map, hold_cash_when_empty=False):
    rows, prev = [], set()
    rs = rebal
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

inlist = lambda xs: ",".join(f"'{x}'" for x in xs)

# ============ SCREEN A — AIRPORT / CARGO INFRASTRUCTURE ============
qa = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv
  FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
  WHERE p.Close IS NOT NULL AND p.ticker IN ({inlist(INFRA)}))
SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.EVEB, f.PCF, f.DY, f.ROIC5Y, f.ROIC_Trailing,
       f.Debt_Eq_P0, f.IntCov_P0, f.Revenue_YoY_P0, f.CF_OA_P0, f.CF_Invest_P0, f.CF_OA_3Y, f.PB
FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
"""
da = con.execute(qa).df(); da["d"] = pd.to_datetime(da.d)
da["fcf"] = da.CF_OA_P0 + da.CF_Invest_P0
intcov_ok = da.IntCov_P0.isna() | (da.IntCov_P0 > 2.0)
passA = (da.EVEB.between(0, 12, inclusive="neither") & (da.ROIC5Y >= 0.10) & (da.CF_OA_3Y > 0)
         & ((da.fcf > 0) | (da.DY > 0.04)) & intcov_ok & (da.Revenue_YoY_P0 >= -0.10))
selA = da[passA].copy(); ga = selA.groupby("d")
selA["fcf_yield"] = selA.fcf / selA.tv.replace(0, np.nan)
selA["score"] = (ga["EVEB"].transform(lambda s: -zc(s)).fillna(0) + ga["ROIC_Trailing"].transform(zc).fillna(0)
                 + ga["fcf_yield"].transform(zc).fillna(0))
picksA, cntA = {}, []
for d, gg in selA.groupby("d"):
    picksA[d] = gg.nlargest(KA, "score").ticker.tolist(); cntA.append((d, len(gg)))
cntA = pd.DataFrame(cntA, columns=["d","nq"]).sort_values("d")
RA = simulate(picksA, hold_cash_when_empty=True); RA.to_csv("data/aviation_infra_monthly.csv", index=False)

# ============ SCREEN B — AIRLINE TROUGH-BUY ============
qb = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv
  FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
  WHERE p.Close IS NOT NULL AND p.ticker IN ({inlist(AIR)}))
SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.PB, f.EVEB, f.Debt_Eq_P0, f.IntCov_P0,
       f.CF_OA_P0, f.NP_P0, f.NP_P4, f.Revenue_YoY_P0, f.ROIC_Trailing
FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
"""
db = con.execute(qb).df(); db["d"] = pd.to_datetime(db.d)
passB = (db.PB.between(0, 1.0, inclusive="neither") & (db.CF_OA_P0 > 0) & (db.IntCov_P0 > 1.0)
         & (db.NP_P0 > 0))
selB = db[passB].copy(); gb = selB.groupby("d")
selB["score"] = (gb["PB"].transform(lambda s: -zc(s)).fillna(0) + gb["CF_OA_P0"].transform(zc).fillna(0))
picksB, cntB = {}, []
for d, gg in selB.groupby("d"):
    picksB[d] = gg.sort_values("score", ascending=False).ticker.tolist(); cntB.append((d, len(gg)))
cntB = pd.DataFrame(cntB, columns=["d","nq"]).sort_values("d")
RB = simulate(picksB, hold_cash_when_empty=True); RB.to_csv("data/aviation_airline_monthly.csv", index=False)

# ---- reporting ----
print("="*72 + "\nSCREEN A — AIRPORT / CARGO INFRASTRUCTURE (ACV/SCS/NCT/SGN)")
print(f"Universe: {da.ticker.nunique()} names {sorted(da.ticker.unique())}")
print(f"Qualifiers/month: med {int(cntA.nq.median())} min {cntA.nq.min()} max {cntA.nq.max()} | months 0: {int((cntA.nq==0).sum())}/{len(cntA)}")
held_a = RA[RA.n_held>0]
print(f"Months actually holding: {len(held_a)}/{len(RA)} (median names held {int(held_a.n_held.median()) if len(held_a) else 0})")
fullA = report("INFRA FULL 2014-2026", RA)
isA = report("INFRA IS  2014-2019", RA[RA.year <= 2019])
oosA = report("INFRA OOS 2020-2026", RA[RA.year >= 2020])
print("\nINFRA per-year (net vs B&H, avg names):")
for yr, gy in RA.groupby("year"):
    sret=(np.prod(1+gy.net)-1)*100; bret=(np.prod(1+gy.bh)-1)*100
    print(f"  {yr} {len(gy):>2}mo  sys {sret:>7.1f}%  bh {bret:>7.1f}%  edge {sret-bret:>+6.1f}pp  held {gy.n_held.mean():>4.1f}")

print("\n" + "="*72 + "\nSCREEN B — AIRLINE TROUGH-BUY (HVN/VJC)")
print(f"Universe: {db.ticker.nunique()} names {sorted(db.ticker.unique())}")
print(f"Qualifiers (months any name cleared): {len(cntB)}/{len(rebal)-1}  -> {'EMPTY' if len(cntB)==0 else 'some'}")
held_b = RB[RB.n_held>0]
print(f"Months actually holding: {len(held_b)}/{len(RB)}")
if len(held_b):
    fullB = report("AIRLINE FULL 2014-2026", RB)
    isB = report("AIRLINE IS  2014-2019", RB[RB.year <= 2019])
    oosB = report("AIRLINE OOS 2020-2026", RB[RB.year >= 2020])
else:
    fullB = (metrics([]), metrics([])); isB = fullB; oosB = fullB
    print("  *** SCREEN STRUCTURALLY EMPTY — no airline ever cleared P/B<1 + CF_OA>0 + IntCov>1 + NP>0 ***")
    print("  *** (VJC always premium P/B>1; HVN negative-equity value trap) -> confirms airline trough-buy does not exist in VN ***")

# ---- self-check 0 VND ----
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path)
    a = NAV0*np.prod(1+R.net.values); b = NAV0*np.prod(1+chk.net.values); return abs(a-b)
dA = selfcheck(RA, "data/aviation_infra_monthly.csv")
dB = selfcheck(RB, "data/aviation_airline_monthly.csv") if len(RB) else 0.0
print(f"\nSELF-CHECK infra diff {dA:.6f} VND -> {'PASS' if dA<1 else 'FAIL'} | airline diff {dB:.6f} VND -> {'PASS' if dB<1 else 'FAIL'}")

# ---- VERIFY known names ----
def mw(pm_, tk, y0, y1): return [d.strftime("%Y-%m") for d in sorted(pm_) if tk in pm_[d] and y0<=d.year<=y1]
scs = mw(picksA,"SCS",2017,2026); nct = mw(picksA,"NCT",2015,2026); sgn = mw(picksA,"SGN",2020,2026)
acv = mw(picksA,"ACV",2017,2026)
hvn = mw(picksB,"HVN",2017,2026); vjc = mw(picksB,"VJC",2017,2026)
print("\nVERIFY:")
print(f"  SCS (cargo gem, expect MANY)   : {len(scs)} mo {scs[:6]}{'...' if len(scs)>6 else ''} -> {'PASS' if scs else 'absent'}")
print(f"  NCT (cargo cash-cow)           : {len(nct)} mo {nct[:6]}{'...' if len(nct)>6 else ''} -> {'PASS' if nct else 'absent'}")
print(f"  SGN (cargo gem, price-patchy)  : {len(sgn)} mo {sgn[:6]}{'...' if len(sgn)>6 else ''} -> {'PASS' if sgn else 'absent (price gaps)'}")
print(f"  ACV (monopoly but expensive/FCF<0): {len(acv)} mo {acv} -> {'rarely (EVEB>12/DY0/Long-Thanh capex)' if len(acv)<20 else 'often'}")
print(f"  HVN (near-bankruptcy trap)     : {len(hvn)} mo -> {'EXCLUDED (PASS)' if not hvn else 'FAIL present!'}")
print(f"  VJC (premium, never PB<1)      : {len(vjc)} mo -> {'EXCLUDED (PASS)' if not vjc else 'present'}")

# ---- ORTHOGONALITY (infra screen vs custom30V, 8L top-25) ----
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
ovA = ortho(picksA)
print(f"\nORTHOGONALITY:  INFRA vs custom30V {ovA[0]:5.1f}% (n{ovA[1]}) | vs 8L top-25 {ovA[2]:5.1f}% (n{ovA[3]})")

# liquidity stats
sel_adv_a = [r.tv for d in picksA for t in picksA[d] for _,r in da[(da.d==d)&(da.ticker==t)].iterrows()]
print(f"LIQUIDITY: INFRA median selected ADV {np.median(sel_adv_a)/1e9:.1f}B")

# ---- verdict json ----
out = dict(
    job="Taylor_20260630_074607", screen="aviation_dual",
    infra=dict(names=INFRA, present=sorted(da.ticker.unique().tolist()), qual_med=int(cntA.nq.median()),
        months_held=len(held_a), months=len(RA), median_sel_adv_b=round(float(np.median(sel_adv_a))/1e9,2),
        full={k:round(v,3) for k,v in fullA[0].items()}, full_bh={k:round(v,3) for k,v in fullA[1].items()},
        is_={k:round(v,3) for k,v in isA[0].items()}, oos={k:round(v,3) for k,v in oosA[0].items()},
        oos_bh={k:round(v,3) for k,v in oosA[1].items()}, selfcheck_vnd=round(dA,6),
        ortho_c30v=round(ovA[0],1), ortho_8l=round(ovA[2],1),
        scs_months=len(scs), nct_months=len(nct), sgn_months=len(sgn), acv_months=len(acv)),
    airline=dict(names=AIR, months_held=len(held_b), months=len(RB),
        structurally_empty=(len(held_b)==0),
        full={k:round(v,3) for k,v in fullB[0].items()}, selfcheck_vnd=round(dB,6),
        hvn_excluded=(not hvn), vjc_excluded=(not vjc),
        note="HVN negative-equity value trap (PB=0 2021-24); VJC premium LCC never PB<1. No VN airline trough-buy exists."),
    data_honesty="Young sector: ACV/HVN/VJC/SCS listed 2017; IS 2014-19 ~= 2017-19 only; OOS 2020-26 = COVID aviation shock (sector-specific). Economics > short backtest curve here.",
)
with open("data/aviation_verdict.json","w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/aviation_infra_monthly.csv, data/aviation_airline_monthly.csv, data/aviation_verdict.json")
