"""F&B (Food & Beverage) — TWO sub-sector screens (point-in-time monthly).
Design + backlook: job Taylor_20260630_071901. Framework: mike/agents/Taylor/fnb_valuation_framework.md.

ICB lumps "Food & Beverage" but two sub-sectors have OPPOSITE economics:
  A — FMCG / CONSUMER-STAPLES DEFENSIVE (VNM,SAB,MSN,MCH,QNS,KDC): recurring branded revenue.
      International method = P/E primary + a brand moat = STABLE, HIGH gross margin. VN screen:
      PE < PE_MA1Y (cheap vs OWN 1y history = mean-reversion entry for a name that rarely gets cheap)
      + ROE5Y>18% (brand+distribution leverage) + GPM moat (avg8q>=22% AND CV<25% = high & stable).
      The dispatch's "DY>3%" gate is a TRAP in BQ -- DY is only populated in dividend-DECLARATION
      quarters (VNM 36/83, MSN 7/67, MCH 15/39), so a hard DY gate fires sporadically and ejects a
      known payer in the ~60-90% of quarters it isn't recorded. DY kept as a SCORING bonus only.
      GPM-moat gate is the discriminator: it KEEPS VNM/SAB/MCH/QNS (CV 0.05-0.18) and REJECTS KDC
      (CV 0.38 -- serial restructurer, no stable margin = no moat).
  B — SEAFOOD EXPORT CYCLICAL (VHC,FMC,MPC,ANV,IDI,CMX): OPPOSITE of FMCG -- tied to global shrimp/
      catfish ASP + US/EU anti-dumping duty cycles. P/B<1.2 trough-buy (below ~book when ASP+duty
      crush sentiment) + GPM_P0>GPM_P4 (margin/ASP turning UP yoy = proxy ASP direction) + CF_OA_3Y>0
      (the survival discipline -- not destroyed by a duty cycle) + Debt_Eq<1.5 (survivable B/S, rejects
      CMX med-Debt 3.5). VHC (PB min 0.91) is the QUALITY name that structurally rarely gets cheap ->
      few trough entries = the screen correctly says "VHC is seldom a trough buy"; the duty-cycle
      troughs are MPC/ANV/FMC/IDI.

BACKLOOK (ticker_financial cache, see framework doc):
  VNM     GPM avg0.39 CV0.18 ROE5Y0.29  -> branded dairy moat, qualifies when PE mean-reverts down
  MCH     GPM avg0.44 CV0.05 ROE5Y0.36  -> HIGHEST & most stable margin in VN FMCG (Masan Consumer)
  SAB     GPM avg0.28 CV0.12 ROE5Y~0.29 -> beer moat (only in prune from 2017 -> thin IS)
  QNS     GPM avg0.32 CV0.11            -> Vinasoy soymilk + sugar, stable margin (from 2017)
  KDC     GPM avg0.28 CV0.38            -> UNSTABLE margin, GPM-moat gate REJECTS (no moat)
  MSN     GPM avg0.33 CV0.20 ROE5Y low  -> conglomerate (resources+consumer+retail), lower ROE
  VHC     PB min0.91 CF_OA_3Y+ 66/74    -> quality catfish, rarely <1.2 (few trough entries, correct)
  ANV     PB min0.22 CF_OA_3Y+ 58/75    -> deep duty-cycle troughs, survives -> trough-buy candidate
  MPC     PB min0.78 GPM avg0.13        -> shrimp, levered, trough entries when CF+ and Debt<1.5
  IDI/CMX PB low but CF_OA_3Y often <0  -> duty-cycle damage; CF/Debt gates reject the traps
"""
import duckdb, numpy as np, pandas as pd, json

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
TC, STALE = 0.001, 120
KA = 10

FMCG    = ("VNM","SAB","MSN","MCH","QNS","KDC")    # consumer-staples defensive
SEAFOOD = ("VHC","FMC","MPC","ANV","IDI","CMX")    # export cyclical (ASP + anti-dumping duty)

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
    """Monthly EW, hold CASH when no qualifier (correct for a wait-for-cheapness/trough screen)."""
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
    SELECT pr.d, pr.ticker, pr.tv, f.Release_Date, f.PE, f.PE_MA1Y, f.PB, f.DY, f.PCF, f.EVEB,
           f.ROE5Y, f.ROIC5Y, f.NPM_P0, f.Revenue_YoY_P0, f.CF_OA_P0, f.CF_OA_3Y, f.Debt_Eq_P0,
           f.GPM_P0, f.GPM_P1, f.GPM_P2, f.GPM_P3, f.GPM_P4, f.GPM_P5, f.GPM_P6, f.GPM_P7
    FROM prices pr ASOF LEFT JOIN read_parquet('{FIN}') f ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
    WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
    """
    d = con.execute(q).df(); d["d"] = pd.to_datetime(d.d)
    gcols = [f"GPM_P{i}" for i in range(8)]
    g = d[gcols]
    d["gpm_avg8"] = g.mean(axis=1)
    d["gpm_cv"] = g.std(axis=1) / g.mean(axis=1).abs()
    d["pe_rel"] = d.PE / d.PE_MA1Y                       # <1 = cheaper than own 1y average
    d["gpm_yoy"] = d.GPM_P0 - d.GPM_P4                   # >0 = margin/ASP turning up yoy
    return d

def build_picks(sel, score_cols, take_all=True):
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
stabz   = lambda s: -zc(s)            # lower GPM CV (more stable) = better -> negative z

# ============ SCREEN A — FMCG / CONSUMER-STAPLES DEFENSIVE ============
da = fin_pull(FMCG)
passA = ((da.PE > 0) & (da.pe_rel < 1.0)                 # cheap vs OWN 1y history
         & (da.ROE5Y > 0.18)                             # brand + distribution leverage
         & (da.gpm_avg8 >= 0.22) & (da.gpm_cv < 0.25))   # high & STABLE gross margin = moat
selA = da[passA]
picksA, cntA = build_picks(selA, [("pe_rel", negz), ("ROE5Y", zc), ("gpm_cv", stabz), ("DY", dybonus)])
RA = simulate(picksA); RA.to_csv("data/fnb_fmcg_monthly.csv", index=False)
# moat-gate accounting: how many ROE/PE-passing rows does the GPM-stability gate reject?
preA = da[(da.PE > 0) & (da.pe_rel < 1.0) & (da.ROE5Y > 0.18)]
gpm_rej = preA[~((preA.gpm_avg8 >= 0.22) & (preA.gpm_cv < 0.25))]

# ============ SCREEN B — SEAFOOD EXPORT CYCLICAL ============
db = fin_pull(SEAFOOD)
passB = (db.PB.between(0, 1.2, inclusive="neither")      # trough-buy below ~book
         & (db.gpm_yoy > 0)                              # margin/ASP turning up yoy
         & (db.CF_OA_3Y > 0)                             # survives the duty cycle
         & (db.Debt_Eq_P0 < 1.5))                        # survivable balance sheet
selB = db[passB]
picksB, cntB = build_picks(selB, [("PB", negz), ("gpm_yoy", zc), ("CF_OA_3Y", zc)])
RB = simulate(picksB); RB.to_csv("data/fnb_seafood_monthly.csv", index=False)
# trap accounting: cheap PB that the CF_OA_3Y / Debt gates reject (duty-cycle damage)
trapB = db[db.PB.between(0,1.2,inclusive="neither") & (db.gpm_yoy>0)]
trap_rej = trapB[~((trapB.CF_OA_3Y>0) & (trapB.Debt_Eq_P0<1.5))]

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

fullA, isA, oosA = block("SCREEN A — FMCG DEFENSIVE", RA, cntA, da, picksA)
fullB, isB, oosB = block("SCREEN B — SEAFOOD CYCLICAL", RB, cntB, db, picksB)

print(f"\nSCREEN A GPM-moat gate: of {len(preA)} PE-cheap + ROE5Y>18% FMCG rows, the GPM-stability gate "
      f"(avg8>=22% AND CV<25%) REJECTS {len(gpm_rej)} rows lacking a stable-margin moat "
      f"(rejected names: {sorted(gpm_rej.ticker.unique().tolist())}).")
print(f"SCREEN B duty-trap gate: of {len(trapB)} PB<1.2 + margin-up seafood rows, the CF_OA_3Y>0 & "
      f"Debt<1.5 gates REJECT {len(trap_rej)} rows damaged by the duty cycle "
      f"(rejected names: {sorted(trap_rej.ticker.unique().tolist())}).")
print(f"DY-UNCAPTURABLE (FMCG): {dy_cov(da)} ASOF rows have DY>0 -> hard DY>3% gate unbuildable; scoring bonus only.")

# ---- self-check 0 VND ----
NAV0 = 1e9
def selfcheck(R, path):
    chk = pd.read_csv(path)
    return abs(NAV0*np.prod(1+R.net.values) - NAV0*np.prod(1+chk.net.values))
dA = selfcheck(RA,"data/fnb_fmcg_monthly.csv"); dB = selfcheck(RB,"data/fnb_seafood_monthly.csv")
print(f"\nSELF-CHECK fmcg {dA:.6f} {'PASS' if dA<1 else 'FAIL'} | seafood {dB:.6f} {'PASS' if dB<1 else 'FAIL'}")

# ---- VERIFY known names ----
def mw(pm_, tk, y0, y1): return [d.strftime("%Y-%m") for d in sorted(pm_) if tk in pm_[d] and y0<=d.year<=y1]
v = dict(
  VNM_meanrev   = mw(picksA,"VNM",2014,2026),
  MCH_moat      = mw(picksA,"MCH",2017,2026),
  SAB_moat      = mw(picksA,"SAB",2017,2026),
  KDC_rejected  = mw(picksA,"KDC",2014,2026),   # should be ~absent (GPM CV 0.38, no moat)
  VHC_rare_trough = mw(picksB,"VHC",2014,2026), # quality name rarely <1.2 -> few entries
  ANV_dutytrough = mw(picksB,"ANV",2014,2026),
  MPC_dutytrough = mw(picksB,"MPC",2014,2026),
  CMX_rejected  = mw(picksB,"CMX",2014,2026),   # should be ~absent (Debt med 3.5)
)
print("\nVERIFY:")
print(f"  VNM PE mean-revert entries      : {len(v['VNM_meanrev'])} months -> {'CAUGHT' if v['VNM_meanrev'] else 'absent'}")
print(f"  MCH branded moat present        : {len(v['MCH_moat'])} months -> {'CAUGHT' if v['MCH_moat'] else 'absent'}")
print(f"  SAB branded moat present        : {len(v['SAB_moat'])} months -> {'CAUGHT' if v['SAB_moat'] else 'absent'}")
print(f"  KDC unstable-margin (expect ~ABSENT): {len(v['KDC_rejected'])} months -> {v['KDC_rejected'][:6]}")
print(f"  VHC quality rare-trough (expect FEW): {len(v['VHC_rare_trough'])} months -> {v['VHC_rare_trough'][:6]}")
print(f"  ANV duty-cycle trough present   : {len(v['ANV_dutytrough'])} months -> {'CAUGHT' if v['ANV_dutytrough'] else 'absent'}")
print(f"  MPC duty-cycle trough present   : {len(v['MPC_dutytrough'])} months -> {'CAUGHT' if v['MPC_dutytrough'] else 'absent'}")
print(f"  CMX over-levered (expect ~ABSENT, Debt3.5): {len(v['CMX_rejected'])} months -> {v['CMX_rejected'][:6]}")

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
ovA, ovB = ortho(picksA), ortho(picksB)
print("\nORTHOGONALITY (vs custom30V | vs 8L top-25):")
print(f"  FMCG    {ovA[0]:5.1f}% | {ovA[1]:5.1f}%")
print(f"  SEAFOOD {ovB[0]:5.1f}% | {ovB[1]:5.1f}%")

def adv(df, picks):
    vals = [r.tv for d in picks for t in picks[d] for _,r in df[(df.d==d)&(df.ticker==t)].iterrows()]
    return float(np.median(vals))/1e9 if vals else 0.0
print(f"\nLIQUIDITY median selected ADV: FMCG {adv(da,picksA):.1f}B | SEAFOOD {adv(db,picksB):.1f}B")

# ---- verdict json ----
def pack(R, full, is_, oos, cnt, df, picks, ov):
    held = R[R.n_held>0]
    return dict(names=sorted(df.ticker.unique().tolist()), qual_med=int(cnt.nq.median()),
        months_held=len(held), months=len(R), median_sel_adv_b=round(adv(df,picks),2),
        dy_cov=dy_cov(df),
        full={k:round(x,3) for k,x in full[0].items()}, full_bh={k:round(x,3) for k,x in full[1].items()},
        is_={k:round(x,3) for k,x in is_[0].items()}, oos={k:round(x,3) for k,x in oos[0].items()},
        oos_bh={k:round(x,3) for k,x in oos[1].items()}, ortho_c30v=round(ov[0],1), ortho_8l=round(ov[1],1))
out = dict(job="Taylor_20260630_071901", screen="fnb_dual",
    fmcg=pack(RA,fullA,isA,oosA,cntA,da,picksA,ovA),
    seafood=pack(RB,fullB,isB,oosB,cntB,db,picksB,ovB),
    selfcheck_vnd=dict(fmcg=round(dA,6),seafood=round(dB,6)),
    gpm_moat_gate=dict(pe_roe_passing=len(preA), rejected_no_moat=len(gpm_rej),
        rejected_names=sorted(gpm_rej.ticker.unique().tolist()),
        note="GPM avg8>=22% AND CV<25% = stable-margin brand moat; rejects serial restructurers (KDC)"),
    duty_trap_gate=dict(pb_cheap_rows=len(trapB), cf_debt_rejected=len(trap_rej),
        rejected_names=sorted(trap_rej.ticker.unique().tolist()),
        note="cheap PB on negative 3y operating cash / over-leverage = duty-cycle value-trap; CF_OA_3Y>0 & Debt<1.5 reject"),
    dy_uncapturable=dict(fmcg=dy_cov(da),
        note="DY only populated in dividend-declaration quarters -> hard DY>3% gate unbuildable; scoring bonus only"),
    verify=v)
with open("data/fnb_verdict.json","w") as f: json.dump(out, f, indent=2, default=str)
print("\nwrote data/fnb_{fmcg,seafood}_monthly.csv + data/fnb_verdict.json")
