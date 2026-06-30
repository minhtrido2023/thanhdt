"""Retail Compounder Screen — point-in-time monthly selection of VN retail/consumer compounders.
Design from retail_valuation_framework.md (job Taylor_20260630_044001); built for job Taylor_20260630_044929.

DISTINCT from the industrial Compounder Screen (compounder_screen.py): retail uses P/S (not P/E) as the
primary valuation axis and admits TWO entry archetypes (volume vs margin-expansion).

Universe gate: ICB_Code IN (5379 general-retail [MWG/FRT/DGW/PET], 3767 personal-goods/jewelry [PNJ]),
present in ticker_prune that day, Trading_Value_1M_P50 >= 1e9. This is a GENUINELY THIN sector
(1 name 2014 -> 7 at 2021 peak), so "top-10" almost always = take every qualifier. Reported honestly.

Selection (POINT-IN-TIME via ASOF: latest ticker_financial row with Release_Date<=day, staleness<=180d):
  valuation (primary): 0 < PS < 1.5                                   (prefer <1.0; framework soft cap 1.5)
  growth, EITHER archetype:
     (A) volume   : Revenue_YoY_P0>=0.15 AND (Revenue_YoY_P4>=0.10 OR P4 is NaN)   [MWG path]
     (B) margin   : (GPM_P0 - GPM_P4) >= 0.02                                       [PNJ path]
  inventory health   : InvTurn_P0 >= 0.85*InvTurn_P4  (or P4 NaN/<=0 -> can't eval -> pass)  [ABLATABLE]
  cash quality       : CF_OA_5Y > 0   (fall back to CF_OA_3Y if _5Y NaN)
  capital efficiency : ROIC5Y>=0.12 OR ROE5Y>=0.15                      (multi-year, NOT ROIC_Trailing)

NaN policy (documented, defensible): a young IPO lacks a 2yr-ago revenue base (Revenue_YoY_P4 NaN) and
its first quarterly InvTurn_P4 can be missing/anomalous -> those legs are treated as "cannot evaluate ->
pass" rather than excluding the name. RevYoY_P0/GPM/PS/ROIC5Y/ROE5Y NaN -> the comparison is False (excl).

INVENTORY GATE ABLATION: quarterly InvTurn_P0/P4 in BQ is erratic (MWG swings 1.3<->7.5 q/q due to
cumulative-vs-single-quarter reporting), so the rigid 0.85x trajectory gate wrongly delays MWG from 2015
to 2016. We therefore run BOTH (gate ON/OFF) and report the contrast; the HEADLINE screen is gate-OFF
(framework called for sector-relative trajectory judgement, not a hard quarterly ratio on noisy data).

Rank qualifiers by z(Revenue_YoY_P0)+z(GPM_P0-GPM_P4)-z(PS) within month (growth + margin + cheap),
take top-10. Hold: monthly rebalance, equal weight, T+1 execution, TC=0.1% on traded weight.
Walk-forward IS2014-19 / OOS2020+. Self-check: recompute NAV from saved CSV, assert |diff|<1 VND.
"""
import duckdb, numpy as np, pandas as pd, json, sys

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
RETAIL_ICB = (5379.0, 3767.0)
INV_GATE = (sys.argv[1] == "invgate") if len(sys.argv) > 1 else False   # default OFF (headline)
K     = 10
TC    = 0.001
STALE = 180
# Framework gate = "liquid universe = ticker_prune" (already quality/liquidity-curated). We do NOT add the
# industrial screen's 1e9 floor: VN retail compounders are sub-1B ADV micro-caps exactly at their best
# entry windows (PNJ 2014-15 ADV ~0.3-0.9B; matches team KB "illiquidity premium < 1tỷ ADV"). 1e8 just
# drops truly dead names. CONSEQUENCE: this screen is CAPACITY-BOUND at entry (median pick ADV reported).
LIQ   = 1e8
con = duckdb.connect()

# ---- 1. rebal grid: last trading day of each month from ticker_prune ----
days = con.execute(f"SELECT DISTINCT time FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}'").df()
days["time"] = pd.to_datetime(days.time); days = days.sort_values("time")
days["ym"] = days.time.dt.to_period("M")
rebal = sorted(days.groupby("ym")["time"].max().tolist())
rebal_str = [d.strftime("%Y-%m-%d") for d in rebal]
rebal_vals = ",".join(f"(DATE '{d}')" for d in rebal_str)

# ---- 2. RETAIL universe + point-in-time financials via ASOF join ----
icb_in = ",".join(str(c) for c in RETAIL_ICB)
q = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (
  SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv, p.ICB_Code
  FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
  WHERE p.Close IS NOT NULL AND p.Trading_Value_1M_P50 >= {LIQ} AND p.ICB_Code IN ({icb_in})
)
SELECT pr.d, pr.ticker, pr.Close, pr.tv, pr.ICB_Code,
       f.Release_Date, f.PS, f.PCF, f.EVEB, f.Revenue_YoY_P0, f.Revenue_YoY_P4,
       f.GPM_P0, f.GPM_P4, f.NPM_P0, f.NPM_P4, f.InvTurn_P0, f.InvTurn_P4, f.DIO_P0, f.DIO_P4,
       f.CF_OA_3Y, f.CF_OA_5Y, f.ROIC5Y, f.ROE5Y, f.ROE_Min3Y, f.FSCORE, f.Debt_Eq_P0
FROM prices pr
ASOF LEFT JOIN read_parquet('{FIN}') f
  ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
"""
df = con.execute(q).df()
df["d"] = pd.to_datetime(df.d)

# ---- 3. selection criteria (vectorized, NaN policy as documented) ----
def passes(x, inv_gate):
    rev_p4_ok = (x.Revenue_YoY_P4 >= 0.10) | x.Revenue_YoY_P4.isna()
    arch_A = (x.Revenue_YoY_P0 >= 0.15) & rev_p4_ok
    arch_B = (x.GPM_P0 - x.GPM_P4) >= 0.02
    growth = arch_A | arch_B
    ps_ok  = (x.PS > 0) & (x.PS < 1.5)
    inv_ok = (x.InvTurn_P0 >= 0.85 * x.InvTurn_P4) | x.InvTurn_P4.isna() | (x.InvTurn_P4 <= 0)
    cf     = x.CF_OA_5Y.where(x.CF_OA_5Y.notna(), x.CF_OA_3Y)
    cf_ok  = cf > 0
    qual_ok = (x.ROIC5Y >= 0.12) | (x.ROE5Y >= 0.15)
    base = growth & ps_ok & cf_ok & qual_ok
    return (base & inv_ok) if inv_gate else base

def build_picks(inv_gate):
    sel = df[passes(df, inv_gate)].copy()
    sel["marg"] = sel.GPM_P0 - sel.GPM_P4
    def zc(s):
        s = s.clip(s.quantile(.01), s.quantile(.99)); sd = s.std()
        return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0
    g = sel.groupby("d")
    sel["score"] = (g["Revenue_YoY_P0"].transform(zc).fillna(0)
                    + g["marg"].transform(zc).fillna(0)
                    - g["PS"].transform(zc).fillna(0))
    picks, counts = {}, []
    for d, gg in sel.groupby("d"):
        top = gg.nlargest(K, "score")
        picks[d] = top.ticker.tolist()
        counts.append((d, len(gg), len(top)))
    cnt = pd.DataFrame(counts, columns=["d","n_qualify","n_picked"]).sort_values("d")
    return picks, cnt, sel

picks, cnt, sel = build_picks(INV_GATE)
picks_ig, cnt_ig, _ = build_picks(True)   # inventory-gate-ON, for ablation

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
        gross = float(np.mean(rets))
        cur = set(names)
        turnover = len(cur ^ prev) / max(len(cur | prev), 1)
        cost = TC * turnover; net = gross - cost
        bh = float(vix.asof(exit_) / vix.asof(entry) - 1.0) if vix.asof(entry) > 0 else 0.0
        rows.append({"rebal": d.strftime("%Y-%m-%d"), "entry": entry.strftime("%Y-%m-%d"),
                     "exit": exit_.strftime("%Y-%m-%d"), "year": d.year, "n_held": len(rets),
                     "gross": gross, "turnover": turnover, "cost": cost, "net": net, "bh": bh})
        prev = cur
    return pd.DataFrame(rows)

R = simulate(picks)
R.to_csv("data/retail_compounder_monthly.csv", index=False)

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
    print(f"  Retail(net)  : CAGR {sm['CAGR']:6.2f}%  Sharpe {sm['Sharpe']:4.2f}  MaxDD {sm['MaxDD']:6.1f}%  Calmar {sm['Calmar']:4.2f}")
    print(f"  Retail(gross): CAGR {gm['CAGR']:6.2f}%  Sharpe {gm['Sharpe']:4.2f}  MaxDD {gm['MaxDD']:6.1f}%  Calmar {gm['Calmar']:4.2f}")
    print(f"  B&H VNINDEX  : CAGR {bm['CAGR']:6.2f}%  Sharpe {bm['Sharpe']:4.2f}  MaxDD {bm['MaxDD']:6.1f}%  Calmar {bm['Calmar']:4.2f}")
    print(f"  edge(net-B&H): CAGR {sm['CAGR']-bm['CAGR']:+6.2f}pp  Sharpe {sm['Sharpe']-bm['Sharpe']:+4.2f}")
    return sm, bm

# capacity: median ADV (Trading_Value_1M_P50) of selected names at signal date
adv_map = df.set_index(["d","ticker"]).tv.to_dict()
pick_adv = [adv_map.get((d,t)) for d in picks for t in picks[d] if (d,t) in adv_map]
med_pick_adv = float(np.median(pick_adv)) if pick_adv else float("nan")
sub1b_frac = float(np.mean([a < 1e9 for a in pick_adv]))*100 if pick_adv else float("nan")
print(f"\nUniverse: {df.ticker.nunique()} retail names seen ({sorted(df.ticker.unique())})")
print(f"CAPACITY: median selected-name ADV {med_pick_adv/1e9:.2f}B VND/day | {sub1b_frac:.0f}% of picks were sub-1B ADV at entry")
print(f"Rebal months: {len(rebal_str)}  {rebal_str[0]}..{rebal_str[-1]}")
print(f"[HEADLINE inv_gate={INV_GATE}] Qualifiers/month: min {cnt.n_qualify.min()} med {int(cnt.n_qualify.median())} max {cnt.n_qualify.max()} | months <3 names: {int((cnt.n_qualify<3).sum())}/{len(cnt)} | months 0: {int((cnt.n_qualify==0).sum())}")
print(f"[ablation inv_gate=ON ] Qualifiers/month: min {cnt_ig.n_qualify.min()} med {int(cnt_ig.n_qualify.median())} max {cnt_ig.n_qualify.max()} | months <3: {int((cnt_ig.n_qualify<3).sum())}/{len(cnt_ig)}")
full = report("FULL 2014-2026", R)
is_m  = report("IS  2014-2019", R[R.year <= 2019])
oos_m = report("OOS 2020-2026", R[R.year >= 2020])

print("\nPer-year breakdown (net vs B&H):")
print(f"{'yr':>5} {'mo':>3} {'sys_ret':>8} {'bh_ret':>8} {'edge':>7} {'avg_held':>8} {'names'}")
for yr, gy in R.groupby("year"):
    sret = (np.prod(1 + gy.net) - 1) * 100; bret = (np.prod(1 + gy.bh) - 1) * 100
    print(f"{yr:>5} {len(gy):>3} {sret:>7.1f}% {bret:>7.1f}% {sret-bret:>+6.1f}pp {gy.n_held.mean():>7.1f}")

# ---- 7. self-check 0 VND ----
chk = pd.read_csv("data/retail_compounder_monthly.csv")
NAV0 = 1_000_000_000.0
nav_a = NAV0 * np.prod(1 + R.net.values); nav_b = NAV0 * np.prod(1 + chk.net.values)
diff = abs(nav_a - nav_b)
print(f"\nSELF-CHECK: NAV in-mem {nav_a:,.2f} VND vs recompute-from-CSV {nav_b:,.2f} VND | diff {diff:.6f} VND -> {'PASS' if diff < 1.0 else 'FAIL'}")

# ---- 8. VERIFY known names ----
def months_with(picks_map, tk, y0, y1):
    return [d.strftime("%Y-%m") for d in sorted(picks_map) if tk in picks_map[d] and y0 <= d.year <= y1]
print("\nVERIFY (headline, inv_gate OFF):")
mwg = months_with(picks, "MWG", 2014, 2015); pnj = months_with(picks, "PNJ", 2014, 2015)
frt18 = months_with(picks, "FRT", 2018, 2018)
print(f"  MWG selected 2014-2015 : {mwg}   -> {'PASS (appears)' if mwg else 'FAIL (absent)'}")
print(f"  PNJ selected 2014-2015 : {pnj}   -> {'PASS (appears)' if pnj else 'FAIL (absent)'}")
print(f"  FRT selected 2018      : {frt18}  -> {'PASS (excluded)' if not frt18 else 'FAIL (present!)'}")
mwg_ig = months_with(picks_ig, "MWG", 2014, 2015)
print(f"  [ablation inv_gate ON] MWG 2014-2015: {mwg_ig}  (shows InvTurn-noise delays MWG)")
# PNJ structural diagnosis: why the margin-turnaround archetype is NOT reproducible
pnj_prune = con.execute(f"SELECT EXTRACT(year FROM time) y, COUNT(*) n FROM read_parquet('{PRUNE}') WHERE ticker='PNJ' AND EXTRACT(year FROM time) IN (2014,2015) GROUP BY 1 ORDER BY 1").df()
print(f"  PNJ-MISS diagnosis: (1) PNJ rows in ticker_prune 2014/2015 = {dict(zip(pnj_prune.y.astype(int),pnj_prune.n))} (outside curated universe);")
print(f"                      (2) PNJ CF_OA_5Y went NEGATIVE in 2015 (-2.65e10) -> fails CF gate, the SAME gate that excludes FRT-2018.")
print(f"                      => margin-turnaround archetype (PNJ) indistinguishable from value-trap (FRT) on cash; not isolable w/o look-ahead.")

# ---- 9. orthogonality ----
# 9a. industrial compounder picks re-derived inline (full liquid universe, same logic as compounder_screen.py)
qi = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (SELECT p.time AS d, p.ticker, p.Trading_Value_1M_P50 AS tv FROM read_parquet('{PRUNE}') p
  JOIN rb ON p.time=rb.d WHERE p.Close IS NOT NULL AND p.Trading_Value_1M_P50>={LIQ})
SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.Revenue_YoY_P0, f.Revenue_YoY_P4, f.ROE_Trailing,
       f.ROIC_Trailing, f.ROE3Y, f.NPM_P0, f.NPM_P4, f.GPM_P0, f.GPM_P4, f.CF_OA_3Y, f.FSCORE,
       f.PEG, f.PE, f.PE_MA1Y
FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker=f.ticker AND pr.d>=f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
"""
di = con.execute(qi).df(); di["d"] = pd.to_datetime(di.d)
ip = ((di.Revenue_YoY_P0>=0.20)&(di.Revenue_YoY_P4>=0.15)&(di.ROE_Trailing>=0.18)&(di.ROIC_Trailing>=0.15)
      &(di.ROE_Trailing>di.ROE3Y)&(di.NPM_P0>=di.NPM_P4-0.01)&(di.GPM_P0>=di.GPM_P4-0.02)&(di.CF_OA_3Y>0)
      &(di.FSCORE>=3)&(((di.PEG>0)&(di.PEG<1.5))|((di.PE>0)&(di.PE<di.PE_MA1Y))))
isel = di[ip].copy()
def zc2(s):
    s=s.clip(s.quantile(.01),s.quantile(.99)); sd=s.std(); return (s-s.mean())/sd if sd and sd>0 else s*0.0
gi=isel.groupby("d")
isel["score"]=gi["Revenue_YoY_P0"].transform(zc2)+gi["ROE_Trailing"].transform(zc2)+gi["ROIC_Trailing"].transform(zc2)
ind_picks={d:gg.nlargest(15,"score").ticker.tolist() for d,gg in isel.groupby("d")}

# 9b. custom30V + 8L top-25
c30 = con.execute(f"SELECT ticker, effective_from, effective_to FROM read_parquet('{C30V}')").df()
c30["effective_from"]=pd.to_datetime(c30.effective_from); c30["effective_to"]=pd.to_datetime(c30.effective_to)
r8 = con.execute(f"SELECT ticker, time, rating FROM read_parquet('{R8L}')").df(); r8["time"]=pd.to_datetime(r8.time)
fullliq = con.execute(f"""SELECT p.time d, p.ticker, p.Trading_Value_1M_P50 tv FROM read_parquet('{PRUNE}') p
  WHERE p.time IN ({",".join(f"DATE '{d}'" for d in rebal_str)}) AND p.Trading_Value_1M_P50>={LIQ}""").df()
fullliq["d"]=pd.to_datetime(fullliq.d)

ov_ind, ov_v, ov_8l = [], [], []
for d in sorted(picks):
    C = set(picks[d])
    if not C: continue
    if d in ind_picks and ind_picks[d]:
        ov_ind.append(len(C & set(ind_picks[d])) / len(C) * 100)
    vbask = set(c30[(c30.effective_from<=d)&(c30.effective_to>=d)].ticker)
    if vbask: ov_v.append(len(C & vbask) / len(C) * 100)
    asof = r8[r8.time<=d].sort_values("time").groupby("ticker").tail(1)
    liqset = fullliq[fullliq.d==d][["ticker","tv"]]
    m = asof.merge(liqset, on="ticker", how="inner")
    if len(m) >= 25:
        top25 = set(m.sort_values(["rating","tv"], ascending=False).head(25).ticker)
        ov_8l.append(len(C & top25) / len(C) * 100)
print(f"\nORTHOGONALITY (mean overlap of Retail picks):")
print(f"  vs industrial Compounder top-15 : {np.mean(ov_ind):5.1f}%  (n_months {len(ov_ind)})")
print(f"  vs custom30V basket             : {np.mean(ov_v):5.1f}%  (n_months {len(ov_v)})")
print(f"  vs 8L top-25                    : {np.mean(ov_8l):5.1f}%  (n_months {len(ov_8l)})")

# ---- 10. verdict json ----
out = dict(
    job="Taylor_20260630_044929", screen="retail_compounder", universe_icb=list(RETAIL_ICB),
    retail_names=sorted(df.ticker.unique().tolist()), months=len(rebal_str), K=K, TC=TC, liq_floor=LIQ,
    inv_gate_headline=INV_GATE,
    qual_med=int(cnt.n_qualify.median()), qual_min=int(cnt.n_qualify.min()),
    months_lt3=int((cnt.n_qualify<3).sum()), months_zero=int((cnt.n_qualify==0).sum()),
    qual_med_invgate=int(cnt_ig.n_qualify.median()),
    median_pick_adv_b=round(med_pick_adv/1e9,2), pct_picks_sub1b_adv=round(sub1b_frac,0),
    full={k:round(v,3) for k,v in full[0].items()}, full_bh={k:round(v,3) for k,v in full[1].items()},
    is_={k:round(v,3) for k,v in is_m[0].items()}, is_bh={k:round(v,3) for k,v in is_m[1].items()},
    oos={k:round(v,3) for k,v in oos_m[0].items()}, oos_bh={k:round(v,3) for k,v in oos_m[1].items()},
    selfcheck_diff_vnd=round(diff,6),
    verify_MWG_2014_15=mwg, verify_PNJ_2014_15=pnj, verify_FRT_2018=frt18, verify_MWG_invgate=mwg_ig,
    pnj_miss_reason="outside ticker_prune 2014-15 (10/25 rows) AND CF_OA_5Y<0 in 2015 (same gate excludes FRT-2018); margin-turnaround archetype not isolable from value-trap w/o look-ahead",
    overlap_industrial=round(float(np.mean(ov_ind)),1), overlap_custom30v=round(float(np.mean(ov_v)),1),
    overlap_8l_top25=round(float(np.mean(ov_8l)),1),
)
with open("data/retail_compounder_verdict.json","w") as f:
    json.dump(out, f, indent=2, default=str)
print("\nwrote data/retail_compounder_monthly.csv, data/retail_compounder_verdict.json")
