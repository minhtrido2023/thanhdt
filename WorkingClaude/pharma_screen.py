"""Pharmaceuticals — defensive P/E mean-reversion compounder screen (point-in-time monthly).
Design + backlook: job Taylor_20260630_072007. Framework: mike/agents/Taylor/pharma_valuation_framework.md.

VN pharma = generics + distribution (NOT innovative R&D pipeline). Defensive, recurring demand.
Moat = brand at point-of-dispensing + foreign strategic partner (Taisho/Abbott/Daewoong).

Screen (dispatched): PE>0 AND PE<PE_MA1Y*0.9 (cheap vs own 1Y mean) AND ROIC5Y>0.15 AND ROE5Y>0.15
  (moat/quality floor) AND GPM_P0>=GPM_P4-0.02 (stable gross margin) AND CF_OA_3Y>0 AND Debt_Eq_P0<0.5.
Hold top-8 (= take-all here, tiny universe), monthly EW, T+1, TC 0.1%, CASH when none qualify.

Three structural facts baked into the read (see framework):
  - IMP (ETC champion) has ROE5Y/ROIC5Y ~10-11% -> EXCLUDED by the quality floor = documented capture
    failure of the ETC-growth archetype (returns depressed by EU-GMP capex + tender working capital).
  - ROIC5Y has a scale artifact pre-2017 (DMC/TRA show 1.8-2.7); >0.15 gate passes them anyway, but the
    ROIC value itself is untrustworthy early -- don't read as moat.
  - Liquid window thins: DHG/IMP -> 2026, DBD from 2017, DMC stops 2023-09, TRA stops 2022-07, MKP not in prune.
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
TC, STALE = 0.001, 120
KA = 8

PHARMA = ("DHG", "DMC", "IMP", "TRA", "DBD", "MKP")

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
    """Monthly EW, hold CASH when no qualifier (correct for a wait-for-cheapness defensive screen)."""
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
    SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.PE, f.PE_MA1Y, f.DY, f.PCF,
           f.ROIC5Y, f.ROE5Y, f.GPM_P0, f.GPM_P4, f.NPM_P0, f.Revenue_YoY_P0, f.CF_OA_3Y,
           f.Debt_Eq_P0, f.NP_P0
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

negz = lambda s: -zc(s)                       # cheaper PE/MA ratio -> higher score
dybonus = lambda s: zc(s.fillna(0))           # DY missing -> 0 contribution (scoring bonus, never a gate)

# ============ SCREEN — DEFENSIVE PHARMA COMPOUNDER ============
d = fin_pull(PHARMA)
d["pe_ratio"] = d.PE / d.PE_MA1Y              # <0.9 = cheap relative to own 1Y mean
d["gpm_chg"]  = d.GPM_P0 - d.GPM_P4
PASS = ((d.PE > 0) & (d.PE_MA1Y > 0) & (d.pe_ratio < 0.9)
        & (d.ROIC5Y > 0.15) & (d.ROE5Y > 0.15)
        & (d.gpm_chg >= -0.02) & (d.CF_OA_3Y > 0) & (d.Debt_Eq_P0 < 0.5))
sel = d[PASS]
picks, cnt = build_picks(sel, [("pe_ratio", negz), ("DY", dybonus), ("GPM_P0", zc)])
R = simulate(picks); R.to_csv("data/pharma_monthly.csv", index=False)

# gate-attribution: how each clause prunes the universe (cumulative)
def gcount(mask): return int(mask.sum())
base = (d.PE > 0) & (d.PE_MA1Y > 0)
g_pe   = base & (d.pe_ratio < 0.9)
g_roic = g_pe & (d.ROIC5Y > 0.15)
g_roe  = g_roic & (d.ROE5Y > 0.15)
g_gpm  = g_roe & (d.gpm_chg >= -0.02)
g_cf   = g_gpm & (d.CF_OA_3Y > 0)
g_full = g_cf & (d.Debt_Eq_P0 < 0.5)
# IMP exclusion accounting: PE-cheap IMP rows that the ROE/ROIC floor ejects
imp = d[(d.ticker == "IMP") & g_pe]
imp_rej = imp[~((imp.ROE5Y > 0.15) & (imp.ROIC5Y > 0.15))]

held = R[R.n_held > 0]
print("="*72)
print(f"Universe: {d.ticker.nunique()} names {sorted(d.ticker.unique())}")
print(f"Qualifiers/month: med {int(cnt.nq.median())} min {cnt.nq.min()} max {cnt.nq.max()} | months 0 (cash): {int((cnt.nq==0).sum())}/{len(cnt)}")
print(f"Months holding: {len(held)}/{len(R)} (median names {int(held.n_held.median()) if len(held) else 0})")
print(f"\nGATE ATTRIBUTION (ASOF rows surviving each cumulative clause):")
print(f"  PE>0 & MA1Y>0            : {gcount(base)}")
print(f"  + PE<MA1Y*0.9 (cheap)    : {gcount(g_pe)}")
print(f"  + ROIC5Y>0.15            : {gcount(g_roic)}")
print(f"  + ROE5Y>0.15             : {gcount(g_roe)}   <- IMP class drops out here")
print(f"  + GPM_P0>=GPM_P4-2pp     : {gcount(g_gpm)}")
print(f"  + CF_OA_3Y>0             : {gcount(g_cf)}")
print(f"  + Debt_Eq<0.5            : {gcount(g_full)}")
print(f"\nIMP CAPTURE FAILURE: of {len(imp)} PE-cheap IMP rows, the ROE/ROIC>15% floor REJECTS "
      f"{len(imp_rej)} ({len(imp_rej)/max(len(imp),1)*100:.0f}%). IMP ROE5Y~{imp.ROE5Y.median():.3f} "
      f"ROIC5Y~{imp.ROIC5Y.median():.3f} -- ETC-growth archetype structurally sub-15% (un-screenable).")

full = report("PHARMA FULL 2014-2026", R)
is_  = report("PHARMA IS 2014-2019", R[R.year <= 2019])
oos  = report("PHARMA OOS 2020-2026", R[R.year >= 2020])
print(f"\nPer-year (net vs B&H, avg names):")
for yr, gy in R.groupby("year"):
    sret=(np.prod(1+gy.net)-1)*100; bret=(np.prod(1+gy.bh)-1)*100
    print(f"  {yr} {len(gy):>2}mo  sys {sret:>7.1f}%  bh {bret:>7.1f}%  edge {sret-bret:>+6.1f}pp  held {gy.n_held.mean():>4.1f}")

# ---- buy-and-hold-the-same-names baseline (does the PE-MA timing add anything?) ----
# EW hold of every name that EVER qualifies, full sample, monthly rebal among available prices
everqual = sorted(sel.ticker.unique())
bh_names = {d_: [t for t in everqual if t in px.columns] for d_ in rebal}
RBH = simulate(bh_names)
bhn = report("BASELINE B&H qualifying-names (no PE-timing)", RBH)

# ---- self-check 0 VND ----
NAV0 = 1e9
chk = pd.read_csv("data/pharma_monthly.csv")
sc = abs(NAV0*np.prod(1+R.net.values) - NAV0*np.prod(1+chk.net.values))
print(f"\nSELF-CHECK 0 VND: {sc:.6f} {'PASS' if sc<1 else 'FAIL'}")

# ---- VERIFY known names ----
def mw(pm_, tk, y0, y1): return [dd.strftime("%Y-%m") for dd in sorted(pm_) if tk in pm_[dd] and y0<=dd.year<=y1]
v = dict(
  DHG = mw(picks,"DHG",2014,2026),
  DMC = mw(picks,"DMC",2014,2026),
  TRA = mw(picks,"TRA",2014,2026),
  IMP_excluded = mw(picks,"IMP",2014,2026),   # expect EMPTY (ROE/ROIC floor)
  DBD = mw(picks,"DBD",2017,2026),
)
print("\nVERIFY:")
print(f"  DHG present : {len(v['DHG'])} months -> {'CAUGHT' if v['DHG'] else 'absent'}")
print(f"  DMC present : {len(v['DMC'])} months -> {'CAUGHT' if v['DMC'] else 'absent'}")
print(f"  TRA present : {len(v['TRA'])} months -> {'CAUGHT' if v['TRA'] else 'absent'}")
print(f"  IMP (expect ABSENT, ROE/ROIC<15%) : {len(v['IMP_excluded'])} months -> {v['IMP_excluded'][:3]}")
print(f"  DBD present : {len(v['DBD'])} months -> {'CAUGHT' if v['DBD'] else 'absent'}")

# ---- ORTHOGONALITY ----
c30 = con.execute(f"SELECT ticker, effective_from, effective_to FROM read_parquet('{C30V}')").df()
c30["effective_from"]=pd.to_datetime(c30.effective_from); c30["effective_to"]=pd.to_datetime(c30.effective_to)
r8 = con.execute(f"SELECT ticker, time, rating FROM read_parquet('{R8L}')").df(); r8["time"]=pd.to_datetime(r8.time)
fullliq = con.execute(f"""SELECT p.time d, p.ticker, p.Trading_Value_1M_P50 tv FROM read_parquet('{PRUNE}') p
  WHERE p.time IN ({",".join(f"DATE '{x}'" for x in rebal_str)}) AND p.Trading_Value_1M_P50>=1e9""").df()
fullliq["d"]=pd.to_datetime(fullliq.d)
def ortho(picks):
    ov_v, ov_8l = [], []
    for d_ in sorted(picks):
        C = set(picks[d_])
        if not C: continue
        vbask = set(c30[(c30.effective_from<=d_)&(c30.effective_to>=d_)].ticker)
        if vbask: ov_v.append(len(C & vbask)/len(C)*100)
        asof = r8[r8.time<=d_].sort_values("time").groupby("ticker").tail(1)
        m = asof.merge(fullliq[fullliq.d==d_][["ticker","tv"]], on="ticker", how="inner")
        if len(m) >= 25:
            top25 = set(m.sort_values(["rating","tv"], ascending=False).head(25).ticker)
            ov_8l.append(len(C & top25)/len(C)*100)
    return (float(np.mean(ov_v)) if ov_v else 0.0, float(np.mean(ov_8l)) if ov_8l else 0.0)
ov = ortho(picks)
print(f"\nORTHOGONALITY: vs custom30V {ov[0]:.1f}% | vs 8L top-25 {ov[1]:.1f}%")

def adv(df, picks):
    vals = [r.tv for d_ in picks for t in picks[d_] for _,r in df[(df.d==d_)&(df.ticker==t)].iterrows()]
    return float(np.median(vals))/1e9 if vals else 0.0
median_adv = adv(d, picks)
print(f"LIQUIDITY median selected ADV: {median_adv:.2f}B")

# ---- verdict json ----
def m3(mm): return {k:round(x,3) for k,x in mm.items()}
out = dict(job="Taylor_20260630_072007", screen="pharma_defensive_compounder",
    framework="mike/agents/Taylor/pharma_valuation_framework.md",
    universe=sorted(d.ticker.unique().tolist()), qual_med=int(cnt.nq.median()),
    months_held=len(held), months=len(R), median_sel_adv_b=round(median_adv,2),
    full=m3(full[0]), full_bh=m3(full[1]), is_=m3(is_[0]), oos=m3(oos[0]), oos_bh=m3(oos[1]),
    bh_samenames=m3(bhn[0]), bh_samenames_bh=m3(bhn[1]),
    ortho_c30v=round(ov[0],1), ortho_8l=round(ov[1],1), selfcheck_vnd=round(sc,6),
    gate_attribution=dict(pe_cheap=gcount(g_pe), plus_roic=gcount(g_roic), plus_roe=gcount(g_roe),
        plus_gpm=gcount(g_gpm), plus_cf=gcount(g_cf), full=gcount(g_full)),
    imp_capture_failure=dict(pe_cheap_imp_rows=len(imp), rejected_by_quality_floor=len(imp_rej),
        imp_roe5y_median=round(float(imp.ROE5Y.median()),3), imp_roic5y_median=round(float(imp.ROIC5Y.median()),3),
        note="ETC-growth champion structurally sub-15% ROE/ROIC (EU-GMP capex + tender WC) -> un-screenable on a backward quality floor"),
    roic_artifact=dict(note="ROIC5Y shows 1.8-2.7 for DMC/TRA pre-2017 (scale artifact, tiny equity base); >0.15 gate passes them anyway but ROIC value untrustworthy early"),
    liquidity_decay=dict(note="DHG/IMP to 2026, DBD from 2017, DMC stops 2023-09, TRA stops 2022-07, MKP not in prune -> tradeable universe collapses to ~2-3 names post-2023"),
    verify=v)
with open("data/pharma_verdict.json","w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/pharma_monthly.csv + data/pharma_verdict.json")
