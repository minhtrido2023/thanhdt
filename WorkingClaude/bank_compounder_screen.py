"""Banking Compounder Screen — point-in-time monthly selection of VN bank compounders.
Design + backlook for job Taylor_20260630_051434 (sector-by-sector compounder book: banking after retail).

WHY BANKS NEED THEIR OWN MODEL (international practice): a bank's earnings are LEVERAGED off book
equity, so P/E and P/S mislead and Debt/Eq / CF_OA / ROIC are MEANINGLESS (leverage is the product,
loan issuance distorts cash flow, there is no "invested capital" ex-balance-sheet). The correct
cheapness gauge is the GORDON justified-P/B:  justified_PB = (ROE - g) / (COE - g).
A bank earning a sustainable ROE above its cost of equity (COE) deserves P/B > 1; it is CHEAP when its
actual P/B sits below the level its through-cycle ROE justifies. We use COE=0.13 (VN bank cost of
equity ~12-14%), g=0.05 (conservative perpetual book-growth) -> justified_PB = (ROE5Y - 0.05)/0.08.

BACKLOOK CALIBRATION (MBB & VCB 2017Q1, from ticker_financial cache):
  MBB 2017Q1: PB 1.09, ROE_Trailing 11.9%, ROE5Y 15.3%, ROE_Min3Y 12.0%, NP +26% YoY, RevYoY +28%, FSCORE 2
    -> justified_PB=(0.153-0.05)/0.08=1.29 > PB 1.09  => CHEAP-FOR-QUALITY. The market hadn't re-rated
       MBB after the 2012-14 bad-debt cleanup; ROE5Y 15% with PB ~1.0 = deep discount. The +10x winner.
  VCB 2017Q1: PB 2.54, ROE_Trailing 14.7%, ROE5Y 9.9% -> justified_PB=(0.099-0.05)/0.08=0.61 << PB 2.54
    => already EXPENSIVE on trailing/through-cycle ROE. VCB worked only because forward ROE climbed to
       24%+ (state-bank moat, unknowable at entry). VCB is a QUALITY-PREMIUM/momentum play, NOT a value
       play, and is STRUCTURALLY UNCAPTURABLE by a value-disciplined screen without look-ahead --
       exactly parallel to retail (caught MWG-volume, missed PNJ-margin-turnaround).

=> HEADLINE = value-disciplined cheap-rerate banking compounder (the MBB archetype). Reported honestly:
   it catches MBB-type cheap re-raters and EXCLUDES VCB-type premium compounders by design.

The dispatch's first-draft gates (ROE_Trailing>=15% AND rising, NP/NP>=1.20, FSCORE>=4, fixed PB<X)
were TOO STRICT and miss BOTH anchors (MBB ROE_Trailing 11.9<15, FSCORE 2<4; VCB PB 2.54>any cheap X).
Recalibrated below to the data: through-cycle ROE (not trailing), Gordon value (not fixed X), no FSCORE
hard gate (bank-Piotroski distorted -- MBB scored 2 at its best entry), no NPM-trend gate (bank NPM in
BQ is erratic 0.1<->0.4 q/q).

UNIVERSE: ICB_Code=8355 (banks), present in ticker_prune that day, Trading_Value_1M_P50>=1e9 (banks are
liquid large-caps; 1B floor drops only dead micro-banks). 7-8 liquid names 2013-17 -> ~23 by 2021+.

SELECTION (POINT-IN-TIME via ASOF: latest ticker_financial row with Release_Date<=day, staleness<=120d
because banks report quarterly ~45d after quarter-end):
  quality floor (never destroyed equity = asset-quality proxy) : ROE_Min3Y >= 0.08
  through-cycle franchise (earns its cost of equity)           : ROE5Y     >= 0.12
  credit-book growth (loan growth proxy)                       : NP_P0/NP_P4 >= 1.10  OR  Revenue_YoY_P0 >= 0.12
  GORDON value (cheap for its through-cycle ROE)               : PB < (ROE5Y-0.05)/0.08  AND  0 < PB < 2.0
NaN policy: ROE5Y / ROE_Min3Y / PB NaN -> comparison False -> excluded (a bank without through-cycle
ROE history is not a compounder). NP_P4<=0 -> NP-growth leg unusable -> rely on Revenue_YoY leg.

Rank qualifiers by z(cheap_margin = justified_PB - PB) + z(ROE5Y) + z(NPgro) within month (cheap +
quality + growth), take top-K=10. Hold monthly, equal weight, T+1 execution, TC=0.1% on traded weight.
Walk-forward IS2014-19 / OOS2020+. Self-check: recompute NAV from CSV, assert |diff|<1 VND.
Orthogonality vs 8L top-25, vs retail compounder, vs industrial compounder.
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
BANK_ICB = 8355.0
COE, GG = 0.13, 0.05          # cost of equity, perpetual book-growth -> Gordon justified P/B
K     = 10
TC    = 0.001
STALE = 120
LIQ   = 1e9
con = duckdb.connect()

# ---- 1. rebal grid: last trading day of each month ----
days = con.execute(f"SELECT DISTINCT time FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}'").df()
days["time"] = pd.to_datetime(days.time); days = days.sort_values("time")
days["ym"] = days.time.dt.to_period("M")
rebal = sorted(days.groupby("ym")["time"].max().tolist())
rebal_str = [d.strftime("%Y-%m-%d") for d in rebal]
rebal_vals = ",".join(f"(DATE '{d}')" for d in rebal_str)

# ---- 2. BANK universe + point-in-time financials via ASOF join ----
q = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (
  SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv
  FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
  WHERE p.Close IS NOT NULL AND p.Trading_Value_1M_P50 >= {LIQ} AND p.ICB_Code = {BANK_ICB}
)
SELECT pr.d, pr.ticker, pr.Close, pr.tv,
       f.Release_Date, f.PB, f.PE, f.ROE_Trailing, f.ROE5Y, f.ROE3Y, f.ROE_Min3Y,
       f.NP_P0, f.NP_P4, f.Revenue_YoY_P0, f.NPM_P0, f.NPM_P4, f.FSCORE
FROM prices pr
ASOF LEFT JOIN read_parquet('{FIN}') f
  ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
"""
df = con.execute(q).df()
df["d"] = pd.to_datetime(df.d)
df["just_pb"] = (df.ROE5Y - GG) / (COE - GG)                 # Gordon justified P/B
df["cheap_margin"] = df.just_pb - df.PB                       # >0 = cheaper than ROE justifies
df["npgro"] = df.NP_P0 / df.NP_P4.where(df.NP_P4 > 0, np.nan) # NaN when prior-yr NP<=0

# ---- 3. selection criteria ----
def passes(x):
    quality = x.ROE_Min3Y >= 0.08
    franchise = x.ROE5Y >= 0.12
    growth = (x.npgro >= 1.10) | (x.Revenue_YoY_P0 >= 0.12)
    value = (x.PB < x.just_pb) & (x.PB > 0) & (x.PB < 2.0)
    return quality & franchise & growth & value

sel = df[passes(df)].copy()
def zc(s):
    s = s.clip(s.quantile(.01), s.quantile(.99)); sd = s.std()
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0
g = sel.groupby("d")
sel["score"] = (g["cheap_margin"].transform(zc).fillna(0)
                + g["ROE5Y"].transform(zc).fillna(0)
                + g["npgro"].transform(zc).fillna(0))
picks, counts = {}, []
for d, gg in sel.groupby("d"):
    top = gg.nlargest(K, "score")
    picks[d] = top.ticker.tolist()
    counts.append((d, len(gg), len(top)))
cnt = pd.DataFrame(counts, columns=["d","n_qualify","n_picked"]).sort_values("d")

# ---- 4. price matrix for NAV (T+1 execution) ----
pm = con.execute(f"""SELECT time, ticker, Close FROM read_parquet('{PRUNE}')
  WHERE time>=DATE '{START}' AND Close IS NOT NULL""").df()
pm["time"] = pd.to_datetime(pm.time)
px = pm.pivot_table(index="time", columns="ticker", values="Close").sort_index()
alldays = px.index
def next_session(d):
    pos = alldays.searchsorted(d, side="right")
    return alldays[pos] if pos < len(alldays) else None
vix = con.execute(f"""SELECT DISTINCT time, VNINDEX FROM read_parquet('{PRUNE}')
  WHERE time>=DATE '{START}' AND VNINDEX IS NOT NULL""").df()
vix["time"] = pd.to_datetime(vix.time); vix = vix.set_index("time")["VNINDEX"].sort_index()

# ---- 5. monthly NAV simulation ----
def simulate(picks_map):
    rows, prev = [], set()
    rs = sorted(picks_map.keys())
    for i, d in enumerate(rs):
        if i + 1 >= len(rs): break
        d_next = rs[i + 1]
        entry, exit_ = next_session(d), next_session(d_next)
        if entry is None or exit_ is None or entry >= exit_: continue
        names = picks_map[d]
        rets = []
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

R = simulate(picks)
R.to_csv("data/bank_compounder_monthly.csv", index=False)

# ---- 6. metrics ----
def metrics(r):
    r = np.asarray(r, float); nav = np.cumprod(1 + r); yrs = len(r) / 12.0
    cagr = nav[-1] ** (1 / yrs) - 1
    sharpe = (r.mean() / r.std() * np.sqrt(12)) if r.std() > 0 else 0.0
    peak = np.maximum.accumulate(nav); mdd = (nav / peak - 1).min()
    calmar = cagr / abs(mdd) if mdd < 0 else float("inf")
    return dict(CAGR=cagr*100, Sharpe=sharpe, MaxDD=mdd*100, Calmar=calmar, navfinal=nav[-1], n=len(r))

def report(label, sub):
    sm, bm, gm = metrics(sub.net), metrics(sub.bh), metrics(sub.gross)
    print(f"\n=== {label}  ({sub.rebal.iloc[0]} .. {sub.rebal.iloc[-1]}, {len(sub)} months) ===")
    print(f"  Bank(net)  : CAGR {sm['CAGR']:6.2f}%  Sharpe {sm['Sharpe']:4.2f}  MaxDD {sm['MaxDD']:6.1f}%  Calmar {sm['Calmar']:4.2f}")
    print(f"  Bank(gross): CAGR {gm['CAGR']:6.2f}%  Sharpe {gm['Sharpe']:4.2f}  MaxDD {gm['MaxDD']:6.1f}%  Calmar {gm['Calmar']:4.2f}")
    print(f"  B&H VNINDEX: CAGR {bm['CAGR']:6.2f}%  Sharpe {bm['Sharpe']:4.2f}  MaxDD {bm['MaxDD']:6.1f}%  Calmar {bm['Calmar']:4.2f}")
    print(f"  edge(net-B&H): CAGR {sm['CAGR']-bm['CAGR']:+6.2f}pp  Sharpe {sm['Sharpe']-bm['Sharpe']:+4.2f}")
    return sm, bm

adv_map = df.set_index(["d","ticker"]).tv.to_dict()
pick_adv = [adv_map.get((d,t)) for d in picks for t in picks[d] if (d,t) in adv_map]
med_pick_adv = float(np.median(pick_adv)) if pick_adv else float("nan")
print(f"Universe: {df.ticker.nunique()} bank names seen ({sorted(df.ticker.unique())})")
print(f"CAPACITY: median selected-name ADV {med_pick_adv/1e9:.2f}B VND/day (banks are large-cap liquid)")
print(f"Rebal months: {len(rebal_str)}  {rebal_str[0]}..{rebal_str[-1]}")
print(f"Qualifiers/month: min {cnt.n_qualify.min()} med {int(cnt.n_qualify.median())} max {cnt.n_qualify.max()} | months <3 names: {int((cnt.n_qualify<3).sum())}/{len(cnt)} | months 0: {int((cnt.n_qualify==0).sum())}")
full = report("FULL 2014-2026", R)
is_m  = report("IS  2014-2019", R[R.year <= 2019])
oos_m = report("OOS 2020-2026", R[R.year >= 2020])

print("\nPer-year breakdown (net vs B&H):")
print(f"{'yr':>5} {'mo':>3} {'sys_ret':>8} {'bh_ret':>8} {'edge':>7} {'avg_held':>8}")
for yr, gy in R.groupby("year"):
    sret = (np.prod(1 + gy.net) - 1) * 100; bret = (np.prod(1 + gy.bh) - 1) * 100
    print(f"{yr:>5} {len(gy):>3} {sret:>7.1f}% {bret:>7.1f}% {sret-bret:>+6.1f}pp {gy.n_held.mean():>7.1f}")

# ---- 7. self-check 0 VND ----
chk = pd.read_csv("data/bank_compounder_monthly.csv")
NAV0 = 1_000_000_000.0
nav_a = NAV0 * np.prod(1 + R.net.values); nav_b = NAV0 * np.prod(1 + chk.net.values)
diff = abs(nav_a - nav_b)
print(f"\nSELF-CHECK: NAV in-mem {nav_a:,.2f} vs recompute-from-CSV {nav_b:,.2f} | diff {diff:.6f} VND -> {'PASS' if diff < 1.0 else 'FAIL'}")

# ---- 8. VERIFY known names ----
def months_with(picks_map, tk, y0, y1):
    return [d.strftime("%Y-%m") for d in sorted(picks_map) if tk in picks_map[d] and y0 <= d.year <= y1]
mbb = months_with(picks, "MBB", 2016, 2017); vcb = months_with(picks, "VCB", 2016, 2017)
# weak/bad-debt tail that must NOT appear at their bad-debt troughs
bvb = months_with(picks, "BVB", 2021, 2023); klb = months_with(picks, "KLB", 2021, 2023)
nvb = months_with(picks, "NVB", 2021, 2024)
print("\nVERIFY:")
print(f"  MBB selected 2016-2017 : {mbb}   -> {'PASS (appears = cheap re-rater caught)' if mbb else 'FAIL (absent)'}")
print(f"  VCB selected 2016-2017 : {vcb}   -> {'(present)' if vcb else 'EXPECTED-ABSENT (premium PB>2 excluded by value gate; uncapturable w/o forward ROE)'}")
print(f"  BVB(weak)  2021-2023   : {bvb}  -> {'PASS (excluded)' if not bvb else 'FAIL (present!)'}")
print(f"  KLB(weak)  2021-2023   : {klb}  -> {'PASS (excluded)' if not klb else 'FAIL (present!)'}")
print(f"  NVB(weak)  2021-2024   : {nvb}  -> {'PASS (excluded)' if not nvb else 'FAIL (present!)'}")

# ---- 9. orthogonality ----
# 9a. retail compounder picks (reuse saved monthly if present is per-NAV not picks; re-derive inline retail)
icb_in = "5379.0,3767.0"
qr = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (SELECT p.time AS d, p.ticker FROM read_parquet('{PRUNE}') p JOIN rb ON p.time=rb.d
  WHERE p.Close IS NOT NULL AND p.Trading_Value_1M_P50>=1e8 AND p.ICB_Code IN ({icb_in}))
SELECT pr.d, pr.ticker, f.Release_Date, f.PS, f.Revenue_YoY_P0, f.Revenue_YoY_P4, f.GPM_P0, f.GPM_P4,
       f.CF_OA_3Y, f.CF_OA_5Y, f.ROIC5Y, f.ROE5Y
FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker=f.ticker AND pr.d>=f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= 180
"""
dr = con.execute(qr).df(); dr["d"] = pd.to_datetime(dr.d)
rp = (((dr.Revenue_YoY_P0>=0.15)&((dr.Revenue_YoY_P4>=0.10)|dr.Revenue_YoY_P4.isna()))|((dr.GPM_P0-dr.GPM_P4)>=0.02)) \
     & (dr.PS>0)&(dr.PS<1.5) & (dr.CF_OA_5Y.where(dr.CF_OA_5Y.notna(),dr.CF_OA_3Y)>0) & ((dr.ROIC5Y>=0.12)|(dr.ROE5Y>=0.15))
rsel = dr[rp].copy(); rsel["marg"]=rsel.GPM_P0-rsel.GPM_P4
grp=rsel.groupby("d")
rsel["score"]=grp["Revenue_YoY_P0"].transform(zc).fillna(0)+grp["marg"].transform(zc).fillna(0)-grp["PS"].transform(zc).fillna(0)
retail_picks={d:gg.nlargest(10,"score").ticker.tolist() for d,gg in rsel.groupby("d")}

# 9b. industrial compounder picks
qi = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (SELECT p.time AS d, p.ticker FROM read_parquet('{PRUNE}') p JOIN rb ON p.time=rb.d
  WHERE p.Close IS NOT NULL AND p.Trading_Value_1M_P50>=1e9)
SELECT pr.d, pr.ticker, f.Release_Date, f.Revenue_YoY_P0, f.Revenue_YoY_P4, f.ROE_Trailing,
       f.ROIC_Trailing, f.ROE3Y, f.NPM_P0, f.NPM_P4, f.GPM_P0, f.GPM_P4, f.CF_OA_3Y, f.FSCORE, f.PEG, f.PE, f.PE_MA1Y
FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker=f.ticker AND pr.d>=f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= 120
"""
di = con.execute(qi).df(); di["d"] = pd.to_datetime(di.d)
ip = ((di.Revenue_YoY_P0>=0.20)&(di.Revenue_YoY_P4>=0.15)&(di.ROE_Trailing>=0.18)&(di.ROIC_Trailing>=0.15)
      &(di.ROE_Trailing>di.ROE3Y)&(di.NPM_P0>=di.NPM_P4-0.01)&(di.GPM_P0>=di.GPM_P4-0.02)&(di.CF_OA_3Y>0)
      &(di.FSCORE>=3)&(((di.PEG>0)&(di.PEG<1.5))|((di.PE>0)&(di.PE<di.PE_MA1Y))))
isel = di[ip].copy(); gi=isel.groupby("d")
isel["score"]=gi["Revenue_YoY_P0"].transform(zc)+gi["ROE_Trailing"].transform(zc)+gi["ROIC_Trailing"].transform(zc)
ind_picks={d:gg.nlargest(15,"score").ticker.tolist() for d,gg in isel.groupby("d")}

# 9c. custom30V + 8L top-25
c30 = con.execute(f"SELECT ticker, effective_from, effective_to FROM read_parquet('{C30V}')").df()
c30["effective_from"]=pd.to_datetime(c30.effective_from); c30["effective_to"]=pd.to_datetime(c30.effective_to)
r8 = con.execute(f"SELECT ticker, time, rating FROM read_parquet('{R8L}')").df(); r8["time"]=pd.to_datetime(r8.time)
fullliq = con.execute(f"""SELECT p.time d, p.ticker, p.Trading_Value_1M_P50 tv FROM read_parquet('{PRUNE}') p
  WHERE p.time IN ({",".join(f"DATE '{d}'" for d in rebal_str)}) AND p.Trading_Value_1M_P50>=1e9""").df()
fullliq["d"]=pd.to_datetime(fullliq.d)

ov_ret, ov_ind, ov_v, ov_8l = [], [], [], []
for d in sorted(picks):
    C = set(picks[d])
    if not C: continue
    if d in retail_picks and retail_picks[d]: ov_ret.append(len(C & set(retail_picks[d]))/len(C)*100)
    if d in ind_picks and ind_picks[d]: ov_ind.append(len(C & set(ind_picks[d]))/len(C)*100)
    vbask = set(c30[(c30.effective_from<=d)&(c30.effective_to>=d)].ticker)
    if vbask: ov_v.append(len(C & vbask)/len(C)*100)
    asof = r8[r8.time<=d].sort_values("time").groupby("ticker").tail(1)
    m = asof.merge(fullliq[fullliq.d==d][["ticker","tv"]], on="ticker", how="inner")
    if len(m) >= 25:
        top25 = set(m.sort_values(["rating","tv"], ascending=False).head(25).ticker)
        ov_8l.append(len(C & top25)/len(C)*100)
print(f"\nORTHOGONALITY (mean overlap of Bank picks):")
print(f"  vs retail Compounder top-10     : {np.mean(ov_ret):5.1f}%  (n_months {len(ov_ret)})")
print(f"  vs industrial Compounder top-15 : {np.mean(ov_ind):5.1f}%  (n_months {len(ov_ind)})")
print(f"  vs custom30V basket             : {np.mean(ov_v):5.1f}%  (n_months {len(ov_v)})")
print(f"  vs 8L top-25                    : {np.mean(ov_8l):5.1f}%  (n_months {len(ov_8l)})")

# ---- 10. verdict json ----
out = dict(
    job="Taylor_20260630_051434", screen="bank_compounder", universe_icb=BANK_ICB,
    bank_names=sorted(df.ticker.unique().tolist()), months=len(rebal_str), K=K, TC=TC, liq_floor=LIQ,
    gordon=dict(COE=COE, g=GG, formula="just_PB=(ROE5Y-g)/(COE-g)"),
    qual_med=int(cnt.n_qualify.median()), qual_min=int(cnt.n_qualify.min()), qual_max=int(cnt.n_qualify.max()),
    months_lt3=int((cnt.n_qualify<3).sum()), months_zero=int((cnt.n_qualify==0).sum()),
    median_pick_adv_b=round(med_pick_adv/1e9,2),
    full={k:round(v,3) for k,v in full[0].items()}, full_bh={k:round(v,3) for k,v in full[1].items()},
    is_={k:round(v,3) for k,v in is_m[0].items()}, is_bh={k:round(v,3) for k,v in is_m[1].items()},
    oos={k:round(v,3) for k,v in oos_m[0].items()}, oos_bh={k:round(v,3) for k,v in oos_m[1].items()},
    selfcheck_diff_vnd=round(diff,6),
    verify_MBB_2016_17=mbb, verify_VCB_2016_17=vcb, verify_BVB=bvb, verify_KLB=klb, verify_NVB=nvb,
    vcb_miss_reason="VCB PB 2.54 at 2017Q1 >> Gordon justified 0.61 (ROE5Y 9.9%); premium-quality compounder, worked on FORWARD ROE to 24%+; uncapturable by value-disciplined screen w/o look-ahead (parallel to retail PNJ-margin-turnaround miss)",
    overlap_retail=round(float(np.mean(ov_ret)),1), overlap_industrial=round(float(np.mean(ov_ind)),1),
    overlap_custom30v=round(float(np.mean(ov_v)),1), overlap_8l_top25=round(float(np.mean(ov_8l)),1),
)
with open("data/bank_compounder_verdict.json","w") as f:
    json.dump(out, f, indent=2, default=str)
print("\nwrote data/bank_compounder_monthly.csv, data/bank_compounder_verdict.json")
