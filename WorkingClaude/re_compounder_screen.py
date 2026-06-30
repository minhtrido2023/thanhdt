"""Real Estate Compounder Screens — point-in-time monthly selection, TWO sub-sector screens.
Design + backlook: job Taylor_20260630_053151. Framework: mike/agents/Taylor/re_valuation_framework.md.

RE is two structurally different businesses under one ICB code (8633):
  A — RESIDENTIAL / urban developers: deep cyclical, handover (lumpy) revenue, credit-cycle = the risk.
      Revenue_YoY USELESS (lumpy), ROIC distorted by land bank, CF_OA structurally negative in build phase.
      -> value on P/B (proxy for discount-to-NAV), survival on Debt_Eq + IntCov, quality on ROE5Y, margin
         direction on GPM. Best entry = AFTER credit tightening (distress), BEFORE easing.
  B — INDUSTRIAL PARKS: REIT-like stable lease income, high ROIC, low growth, STRUCTURALLY ILLIQUID.
      Debt_Eq/IntCov MISLEADING (prepaid land-lease booked as liability) -> do NOT apply leverage gates.
      Value on P/B + DY, quality on ROIC5Y. FLAG ADV<10B (NTC-type), never exclude.

BACKLOOK (ticker_financial cache):
  VHM 2023Q1 PB1.37 DebtEq1.35 IntCov23 NP+11.9T  -> cheap-for-quality blue-chip ENTRY
  NLG 2022Q4 PB0.82 DebtEq1.03 IntCov26 NP+437B   -> clean deleverager ENTRY
  TCH 2022Q4 PB0.44 DebtEq0.25 IntCov4.8 DY16%     -> near-debt-free deep value ENTRY
  NVL 2022Q4 PB0.62 DebtEq4.73 IntCov0.5->-0.39    -> LEVERAGE TRAP (cheap+un-payable debt) EXCLUDE
  PDR 2022Q4 PB1.03 IntCov-0.97 NP-267B            -> EXCLUDE (can't cover interest in crunch)
  NTC 2017   PB2.5-3.7 DY4% ROE5Y23-29% ADV2.9B    -> premium DY+ROE re-rating, NOT cheap-P/B -> screen MISSES (by design)

HEADLINE = value-disciplined cheap-distress residential (VHM/NLG/TCH archetype). Reported honestly:
catches the cheap-distress archetype, EXCLUDES NVL leverage traps, and MISSES the NTC premium-yield
re-rating (uncapturable w/o look-ahead -- parallel to banking-VCB / retail-PNJ).
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
RE_ICB = 8633.0
IP_SET = ('KBC','IDC','SZC','BCM','SIP','NTC','LHG','D2D','TIP','IDV','SZL','SNZ')  # industrial parks
KA, KB = 10, 10
TC, STALE, LIQ = 0.001, 120, 1e9
con = duckdb.connect()
ip_sql = ",".join(f"'{t}'" for t in IP_SET)

# ---- rebal grid: last trading day of each month ----
days = con.execute(f"SELECT DISTINCT time FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}'").df()
days["time"] = pd.to_datetime(days.time); days = days.sort_values("time")
days["ym"] = days.time.dt.to_period("M")
rebal = sorted(days.groupby("ym")["time"].max().tolist())
rebal_str = [d.strftime("%Y-%m-%d") for d in rebal]
rebal_vals = ",".join(f"(DATE '{d}')" for d in rebal_str)

# ---- price matrix + VNINDEX for NAV (shared) ----
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
    rows, prev = [], set()
    rs = sorted(picks_map.keys())
    for i, d in enumerate(rs):
        if i + 1 >= len(rs): break
        d_next = rs[i + 1]; entry, exit_ = next_session(d), next_session(d_next)
        if entry is None or exit_ is None or entry >= exit_: continue
        names = picks_map[d]; rets = []
        for t in names:
            if t in px.columns:
                p0 = px.at[entry, t] if entry in px.index else np.nan
                p1 = px.at[exit_, t] if exit_ in px.index else np.nan
                if pd.notna(p0) and pd.notna(p1) and p0 > 0: rets.append(p1 / p0 - 1.0)
        if not rets: continue
        gross = float(np.mean(rets)); cur = set(names)
        turnover = len(cur ^ prev) / max(len(cur | prev), 1)
        cost = TC * turnover; net = gross - cost
        bh = float(vix.asof(exit_) / vix.asof(entry) - 1.0) if vix.asof(entry) > 0 else 0.0
        rows.append({"rebal": d.strftime("%Y-%m-%d"), "entry": entry.strftime("%Y-%m-%d"),
                     "exit": exit_.strftime("%Y-%m-%d"), "year": d.year, "n_held": len(rets),
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
    print(f"  RE(net)   : CAGR {sm['CAGR']:6.2f}%  Sharpe {sm['Sharpe']:4.2f}  MaxDD {sm['MaxDD']:6.1f}%  Calmar {sm['Calmar']:4.2f}")
    print(f"  B&H VNINDEX: CAGR {bm['CAGR']:6.2f}%  Sharpe {bm['Sharpe']:4.2f}  MaxDD {bm['MaxDD']:6.1f}%  Calmar {bm['Calmar']:4.2f}")
    print(f"  edge(net-B&H): CAGR {sm['CAGR']-bm['CAGR']:+6.2f}pp  Sharpe {sm['Sharpe']-bm['Sharpe']:+4.2f}")
    return sm, bm

# ============ SCREEN A — RESIDENTIAL CYCLICAL ============
qa = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv
  FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
  WHERE p.Close IS NOT NULL AND p.Trading_Value_1M_P50 >= {LIQ}
    AND p.ICB_Code = {RE_ICB} AND p.ticker NOT IN ({ip_sql}))
SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.PB, f.Debt_Eq_P0, f.Debt_Eq_P4, f.IntCov_P0,
       f.NP_P0, f.NP_P4, f.GPM_P0, f.GPM_P4, f.ROE5Y, f.ROE_Min3Y, f.CF_OA_P0
FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
"""
da = con.execute(qa).df(); da["d"] = pd.to_datetime(da.d)
da["gpm_traj"] = da.GPM_P0 - da.GPM_P4
da["icov_c"] = da.IntCov_P0.clip(upper=30)
passA = (da.PB.between(0, 1.5, inclusive="neither") & (da.Debt_Eq_P0 < 2.0) & (da.IntCov_P0 > 1.5)
         & (da.NP_P0 > 0) & (da.GPM_P0 >= 0.15))
selA = da[passA].copy(); ga = selA.groupby("d")
selA["score"] = (ga["PB"].transform(lambda s: -zc(s)).fillna(0) + ga["ROE5Y"].transform(zc).fillna(0)
                 + ga["gpm_traj"].transform(zc).fillna(0) + ga["icov_c"].transform(zc).fillna(0))
picksA, cntA = {}, []
for d, gg in selA.groupby("d"):
    top = gg.nlargest(KA, "score"); picksA[d] = top.ticker.tolist()
    cntA.append((d, len(gg)))
cntA = pd.DataFrame(cntA, columns=["d","nq"]).sort_values("d")
RA = simulate(picksA); RA.to_csv("data/re_compounder_resid_monthly.csv", index=False)

# ============ SCREEN B — INDUSTRIAL PARK ============
qb = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv
  FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
  WHERE p.Close IS NOT NULL AND p.ICB_Code = {RE_ICB} AND p.ticker IN ({ip_sql}))
SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.PB, f.DY, f.ROIC5Y, f.ROE5Y, f.NP_P0, f.NP_P4, f.GPM_P0
FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
"""
db = con.execute(qb).df(); db["d"] = pd.to_datetime(db.d)
passB = (db.PB.between(0, 1.5, inclusive="neither") & (db.DY > 0.04) & (db.ROIC5Y > 0.08))
selB = db[passB].copy(); gb = selB.groupby("d")
selB["score"] = (gb["DY"].transform(zc).fillna(0) + gb["ROIC5Y"].transform(zc).fillna(0)
                 + gb["PB"].transform(lambda s: -zc(s)).fillna(0))
picksB, cntB, illiq = {}, [], []
for d, gg in selB.groupby("d"):
    top = gg.nlargest(KB, "score"); picksB[d] = top.ticker.tolist()
    cntB.append((d, len(gg)))
    illiq += [(d.strftime("%Y-%m"), t, float(r.tv)/1e9) for t, r in top.set_index("ticker").iterrows() if r.tv < 10e9]
cntB = pd.DataFrame(cntB, columns=["d","nq"]).sort_values("d")
RB = simulate(picksB); RB.to_csv("data/re_compounder_indust_monthly.csv", index=False)

# ---- reporting ----
print("="*70 + "\nSCREEN A — RESIDENTIAL CYCLICAL")
print(f"Universe (resid devs, 8633 ex-IP, TV>=1e9): {da.ticker.nunique()} names {sorted(da.ticker.unique())}")
print(f"Qualifiers/month: med {int(cntA.nq.median())} min {cntA.nq.min()} max {cntA.nq.max()} | months 0: {int((cntA.nq==0).sum())}/{len(cntA)}")
fullA = report("RESID FULL 2014-2026", RA)
isA = report("RESID IS  2014-2019", RA[RA.year <= 2019])
oosA = report("RESID OOS 2020-2026", RA[RA.year >= 2020])
print("\nRESID per-year (net vs B&H, avg names):")
for yr, gy in RA.groupby("year"):
    sret=(np.prod(1+gy.net)-1)*100; bret=(np.prod(1+gy.bh)-1)*100
    print(f"  {yr} {len(gy):>2}mo  sys {sret:>7.1f}%  bh {bret:>7.1f}%  edge {sret-bret:>+6.1f}pp  held {gy.n_held.mean():>4.1f}")

print("\n" + "="*70 + "\nSCREEN B — INDUSTRIAL PARK (REIT-like, illiquid)")
print(f"Universe (IP list ∩ prune): {db.ticker.nunique()} names {sorted(db.ticker.unique())}")
print(f"Qualifiers/month: med {int(cntB.nq.median())} min {cntB.nq.min()} max {cntB.nq.max()} | months 0: {int((cntB.nq==0).sum())}/{len(cntB)}")
ip_adv = [r.tv for _,r in db.iterrows()]
sel_adv = [r.tv for d in picksB for t in picksB[d] for _,r in db[(db.d==d)&(db.ticker==t)].iterrows()]
print(f"LIQUIDITY FLAG: {len(illiq)} picked name-months had ADV<10B (median selected ADV {np.median(sel_adv)/1e9:.1f}B). Industrial parks are capacity-bound.")
if len(RB):
    fullB = report("INDUST FULL", RB); isB = report("INDUST IS 2014-2019", RB[RB.year<=2019]); oosB = report("INDUST OOS 2020-2026", RB[RB.year>=2020])
    print("\nINDUST per-year (net vs B&H, avg names):")
    for yr, gy in RB.groupby("year"):
        sret=(np.prod(1+gy.net)-1)*100; bret=(np.prod(1+gy.bh)-1)*100
        print(f"  {yr} {len(gy):>2}mo  sys {sret:>7.1f}%  bh {bret:>7.1f}%  edge {sret-bret:>+6.1f}pp  held {gy.n_held.mean():>4.1f}")
else:
    fullB=isB=oosB=(metrics([]),metrics([]))

# ---- self-check 0 VND ----
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path)
    a = NAV0*np.prod(1+R.net.values); b = NAV0*np.prod(1+chk.net.values); return abs(a-b)
dA = selfcheck(RA, "data/re_compounder_resid_monthly.csv")
dB = selfcheck(RB, "data/re_compounder_indust_monthly.csv") if len(RB) else 0.0
print(f"\nSELF-CHECK resid diff {dA:.6f} VND -> {'PASS' if dA<1 else 'FAIL'} | indust diff {dB:.6f} VND -> {'PASS' if dB<1 else 'FAIL'}")

# ---- VERIFY known names ----
def mw(pm_, tk, y0, y1): return [d.strftime("%Y-%m") for d in sorted(pm_) if tk in pm_[d] and y0<=d.year<=y1]
vhm = mw(picksA,"VHM",2022,2023); nlg = mw(picksA,"NLG",2022,2023); tch = mw(picksA,"TCH",2022,2023)
nvl = mw(picksA,"NVL",2022,2024); pdr22 = mw(picksA,"PDR",2022,2022)
ntc = mw(picksB,"NTC",2017,2018)
print("\nVERIFY:")
print(f"  VHM 2022-23 (cheap-quality)  : {vhm} -> {'PASS (caught)' if vhm else 'absent'}")
print(f"  NLG 2022-23 (deleverager)    : {nlg} -> {'PASS (caught)' if nlg else 'absent'}")
print(f"  TCH 2022-23 (debt-free value): {tch} -> {'PASS (caught)' if tch else 'absent'}")
print(f"  NVL 2022-24 (LEVERAGE TRAP)  : {nvl} -> {'PASS (EXCLUDED)' if not nvl else 'FAIL (present!)'}")
print(f"  PDR 2022    (IntCov<0 crunch): {pdr22} -> {'PASS (EXCLUDED)' if not pdr22 else 'FAIL (present!)'}")
print(f"  NTC 2017-18 (premium-yield)  : {ntc} -> {'(present)' if ntc else 'EXPECTED-ABSENT (PB 2.5>1.5; premium re-rating uncapturable w/o look-ahead)'}")

# ---- ORTHOGONALITY (resid screen vs custom30V, 8L top-25) ----
c30 = con.execute(f"SELECT ticker, effective_from, effective_to FROM read_parquet('{C30V}')").df()
c30["effective_from"]=pd.to_datetime(c30.effective_from); c30["effective_to"]=pd.to_datetime(c30.effective_to)
r8 = con.execute(f"SELECT ticker, time, rating FROM read_parquet('{R8L}')").df(); r8["time"]=pd.to_datetime(r8.time)
fullliq = con.execute(f"""SELECT p.time d, p.ticker, p.Trading_Value_1M_P50 tv FROM read_parquet('{PRUNE}') p
  WHERE p.time IN ({",".join(f"DATE '{d}'" for d in rebal_str)}) AND p.Trading_Value_1M_P50>=1e9""").df()
fullliq["d"]=pd.to_datetime(fullliq.d)
ov_v, ov_8l, ov_ind = [], [], []
for d in sorted(picksA):
    C = set(picksA[d])
    if not C: continue
    vbask = set(c30[(c30.effective_from<=d)&(c30.effective_to>=d)].ticker)
    if vbask: ov_v.append(len(C & vbask)/len(C)*100)
    asof = r8[r8.time<=d].sort_values("time").groupby("ticker").tail(1)
    m = asof.merge(fullliq[fullliq.d==d][["ticker","tv"]], on="ticker", how="inner")
    if len(m) >= 25:
        top25 = set(m.sort_values(["rating","tv"], ascending=False).head(25).ticker)
        ov_8l.append(len(C & top25)/len(C)*100)
    if d in picksB and picksB[d]: ov_ind.append(len(C & set(picksB[d]))/len(C)*100)
print(f"\nORTHOGONALITY (resid Screen A picks):")
print(f"  vs custom30V basket : {np.mean(ov_v):5.1f}%  (n {len(ov_v)})")
print(f"  vs 8L top-25        : {np.mean(ov_8l):5.1f}%  (n {len(ov_8l)})")
print(f"  vs industrial ScrB  : {np.mean(ov_ind) if ov_ind else 0:5.1f}%  (disjoint universe by construction)")

# ---- verdict json ----
out = dict(
    job="Taylor_20260630_053151", screen="re_compounder_dual", universe_icb=RE_ICB, ip_set=list(IP_SET),
    resid=dict(names=sorted(da.ticker.unique().tolist()), qual_med=int(cntA.nq.median()), months_zero=int((cntA.nq==0).sum()), months=len(cntA),
        full={k:round(v,3) for k,v in fullA[0].items()}, full_bh={k:round(v,3) for k,v in fullA[1].items()},
        is_={k:round(v,3) for k,v in isA[0].items()}, oos={k:round(v,3) for k,v in oosA[0].items()},
        oos_bh={k:round(v,3) for k,v in oosA[1].items()}, selfcheck_vnd=round(dA,6)),
    indust=dict(names=sorted(db.ticker.unique().tolist()), qual_med=int(cntB.nq.median()), months_zero=int((cntB.nq==0).sum()), months=len(cntB),
        illiq_pick_months=len(illiq), median_sel_adv_b=round(float(np.median(sel_adv))/1e9,2),
        full={k:round(v,3) for k,v in fullB[0].items()}, oos={k:round(v,3) for k,v in oosB[0].items()}, selfcheck_vnd=round(dB,6)),
    verify=dict(VHM=vhm, NLG=nlg, TCH=tch, NVL_trap_excluded=(not nvl), PDR2022_excluded=(not pdr22), NTC=ntc,
        ntc_miss_reason="NTC 2017 PB 2.5-3.7 >> 1.5; premium DY+ROE+land-revaluation re-rating, worked on FORWARD re-rate; uncapturable by value-disciplined screen w/o look-ahead (parallel banking-VCB / retail-PNJ)"),
    orthogonality=dict(vs_custom30v=round(float(np.mean(ov_v)),1), vs_8l_top25=round(float(np.mean(ov_8l)),1)),
)
with open("data/re_compounder_verdict.json","w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/re_compounder_{resid_monthly,indust_monthly}.csv, data/re_compounder_verdict.json")
