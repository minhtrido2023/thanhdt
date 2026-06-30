"""gq_score (growth-WITH-quality, "golden eggs") — DECISIVE GATE before wiring into rating_8l.py.

Design (Taylor_20260630_040305): a THIRD selection axis, orthogonal to rating(quality) + value.
gq_score = revenue-growth-smooth + margin-stable + CF_OA>0 anchor (anti-fiction, same principle as the floor).
  - growth   = Revenue_YoY_P0           (current YoY revenue growth; revenue not NP => smoother)
  - sustain  = Revenue_YoY_P0>0 AND Revenue_YoY_P4>0   (2yr sustained, not a one-year base effect)
  - margin   = GPM_P0 - GPM_P4          (gross margin NOT compressing YoY)
  - cf_ok    = CF_OA_P0 > 0             (operating cash real => anti-fiction anchor/gate)
gq_score (per-month cross-sectional) = z(growth)+z(margin), credited ONLY when sustain & cf_ok else floored.

Point-in-time: ASOF join latest ticker_financial (fin.time = release date <= selection month-end). No look-ahead.
Outcome = forward profit_1M/2M label already in ticker_prune (label-only, never a live filter).

THREE GATES (all must read positive OOS to recommend wiring):
  1. residual-IC : Spearman(gq_score, fwd residualized on quality_z+value_z) per month, IS/OOS.
                   (the bar fair-value/ROIC-PB FAILED here — must add ABOVE the saturated value+quality axes)
  2. walk-forward IC : raw IC(gq_score, fwd) IS 2014-19 vs OOS 2020+.
  3. selection A/B : monthly top-25, A=quality+value vs B=+gq_score, paired delta net forward return IS/OOS.
"""
import duckdb, numpy as np, pandas as pd
def spearman(a,b):
    a=pd.Series(np.asarray(a,float)); b=pd.Series(np.asarray(b,float))
    if len(a)<3: return np.nan
    return a.rank().corr(b.rank())

PR = "data/bq_cache/ticker_prune.parquet"
FI = "data/bq_cache/ticker_financial.parquet"
con = duckdb.connect()

# ---- 1. monthly selection rows from ticker_prune (last trading day each month) -------------------
px = con.execute(f"""
WITH base AS (
  SELECT time,ticker,PE,PCF,PB,ROIC5Y,FSCORE,ROE_Min3Y,Trading_Value_1M_P50,profit_1M,profit_2M,
         date_trunc('month',time) ym
  FROM read_parquet('{PR}')
  WHERE time>=DATE '2014-01-01' AND PE>0 AND PB>0 AND ROIC5Y IS NOT NULL
    AND ROE_Min3Y>=0 AND FSCORE>=5 AND Trading_Value_1M_P50>=5e9 AND profit_1M IS NOT NULL
),
mlast AS (SELECT ym, max(time) mt FROM base GROUP BY ym)
SELECT b.* FROM base b JOIN mlast m ON b.ym=m.ym AND b.time=m.mt
""").df()

# ---- 2. ASOF point-in-time join of growth fundamentals (fin.time = release date <= selection date)
fin = con.execute(f"""
SELECT ticker,time AS ftime,Revenue_YoY_P0,Revenue_YoY_P4,GPM_P0,GPM_P4,CF_OA_P0
FROM read_parquet('{FI}')
WHERE Revenue_YoY_P0 IS NOT NULL
""").df()
px["time"]=pd.to_datetime(px.time); fin["ftime"]=pd.to_datetime(fin.ftime)
px=px.sort_values("time"); fin=fin.sort_values("ftime")
m = pd.merge_asof(px, fin, left_on="time", right_on="ftime", by="ticker", direction="backward")
# staleness guard: drop financials older than 9 months (no fresh release => can't judge current growth)
m = m[(m.ftime.notna()) & ((m.time - m.ftime).dt.days <= 280)].copy()

# ---- 3. gq_score construction -------------------------------------------------------------------
m["growth"]   = m.Revenue_YoY_P0
m["margin"]   = m.GPM_P0 - m.GPM_P4
m["sustain"]  = ((m.Revenue_YoY_P0>0) & (m.Revenue_YoY_P4>0)).astype(float)
m["cf_ok"]    = (m.CF_OA_P0>0).astype(float)
m = m.dropna(subset=["growth","margin"]).copy()
m["ym"]=pd.to_datetime(m.time).dt.to_period("M"); m["yr"]=m.time.dt.year

def zc(s):
    s=s.clip(s.quantile(.01),s.quantile(.99)); sd=s.std(); return (s-s.mean())/sd if sd>0 else s*0
g=m.groupby("ym")
m["zgrowth"]=g["growth"].transform(zc); m["zmargin"]=g["margin"].transform(zc)
# value + quality proxies (the existing two rating_8l axes, equal-weight unbiased proxies)
m["ey"]=1/m.PE; m["cfy"]=np.where(m.PCF>0,1/m.PCF,0.0); m["rb"]=m.ROIC5Y
m["zey"]=g["ey"].transform(zc); m["zcfy"]=g["cfy"].transform(zc)
m["zroic"]=g["ROIC5Y"].transform(zc); m["zfs"]=g["FSCORE"].transform(zc)
m["value_z"]   = m.zey + m.zcfy
m["quality_z"] = m.zroic + m.zfs
# gq raw, gated: growth+margin credited only when sustained & cash-real, else floored to the gate penalty
gq_raw = m.zgrowth + m.zmargin
m["gq_score"] = np.where((m.sustain>0)&(m.cf_ok>0), gq_raw, np.minimum(gq_raw, 0.0)*0.0 - 0.5)

# ---- SELF-CHECK ---------------------------------------------------------------------------------
print("="*92)
print("SELF-CHECK")
print(f"  selection rows {len(m):,} | names {m.ticker.nunique()} | months {m.ym.nunique()} "
      f"({m.ym.min()}..{m.ym.max()})")
look = (m.ftime > m.time).sum()
print(f"  look-ahead violations (ftime>selection time): {look}  [MUST be 0]")
print(f"  median financial staleness: {(m.time-m.ftime).dt.days.median():.0f}d (cap 280d)")
print(f"  gq_score NaN: {m.gq_score.isna().sum()}  | sustain&cf rate: {((m.sustain>0)&(m.cf_ok>0)).mean():.1%}")

# ---- GATE 1+2 : IC per month (raw + residual) ---------------------------------------------------
rows=[]
for ym,gg in m.groupby("ym"):
    if len(gg)<40: continue
    for h in ["profit_1M","profit_2M"]:
        d=gg.dropna(subset=[h,"gq_score","value_z","quality_z"])
        if len(d)<40: continue
        ic_raw=spearman(d.gq_score,d[h])
        # residualize fwd on value_z+quality_z (OLS), IC of gq vs residual
        X=np.column_stack([np.ones(len(d)),d.value_z,d.quality_z])
        beta,_,_,_=np.linalg.lstsq(X,d[h].values,rcond=None)
        resid=d[h].values - X@beta
        ic_res=spearman(d.gq_score,resid)
        rows.append({"ym":ym,"yr":ym.year,"h":h,"ic_raw":ic_raw,"ic_res":ic_res,"n":len(d)})
IC=pd.DataFrame(rows)

def ic_rep(lab,d):
    for h in ["profit_1M","profit_2M"]:
        s=d[d.h==h]; n=len(s)
        if n==0: continue
        rmu=s.ic_raw.mean(); rt=rmu/(s.ic_raw.std()/np.sqrt(n))
        emu=s.ic_res.mean(); et=emu/(s.ic_res.std()/np.sqrt(n))
        print(f"  {lab:>9} {h} | raw-IC {rmu:+.4f} (t={rt:>4.1f}) | RESID-IC {emu:+.4f} (t={et:>4.1f}) | n_mo {n}")
print("\n"+"="*92); print("GATE 1+2 — IC of gq_score on forward return (raw) and RESIDUAL to value_z+quality_z")
ic_rep("ALL",IC); ic_rep("IS14-19",IC[IC.yr<=2019]); ic_rep("OOS20+",IC[IC.yr>=2020])

# ---- GATE 3 : selection A/B ----------------------------------------------------------------------
m["A"]=m.quality_z+m.value_z; m["B"]=m.quality_z+m.value_z+m.gq_score
K=25; ab=[]
for ym,gg in m.groupby("ym"):
    gg=gg.dropna(subset=["A","B","profit_1M","profit_2M"])
    if len(gg)<50: continue
    tA=gg.nlargest(K,"A"); tB=gg.nlargest(K,"B")
    ab.append({"ym":ym,"yr":ym.year,
               "A_1M":tA.profit_1M.mean(),"B_1M":tB.profit_1M.mean(),
               "A_2M":tA.profit_2M.mean(),"B_2M":tB.profit_2M.mean(),
               "overlap":len(set(tA.ticker)&set(tB.ticker))})
AB=pd.DataFrame(ab)
def ab_rep(lab,d):
    n=len(d)
    for h in ["1M","2M"]:
        a,b=d[f"A_{h}"].mean(),d[f"B_{h}"].mean(); dl=d[f"B_{h}"]-d[f"A_{h}"]
        t=dl.mean()/(dl.std()/np.sqrt(n)); win=(dl>0).mean()*100
        print(f"  {lab:>9} {h} | A {a:>5.2f}% B {b:>5.2f}% | delta {dl.mean():+.2f}pp (t={t:>4.1f}) win {win:>3.0f}% | n_mo {n}")
print("\n"+"="*92)
print(f"GATE 3 — selection A/B, top-{K} monthly | A=quality+value  B=+gq_score | mean overlap {AB.overlap.mean():.0f}/{K}")
ab_rep("ALL",AB); ab_rep("IS14-19",AB[AB.yr<=2019]); ab_rep("OOS20+",AB[AB.yr>=2020])
print("\nPer-year selection delta (B-A, profit_1M, pp):")
print(AB.groupby("yr").apply(lambda x:(x.B_1M-x.A_1M).mean(),include_groups=False).round(2).to_string())

# ---- orthogonality cross-check ------------------------------------------------------------------
print("\n"+"="*92); print("ORTHOGONALITY (pooled corr of gq_score vs existing axes)")
for c in ["value_z","quality_z","zroic","zey"]:
    print(f"  corr(gq_score,{c}) = {m.gq_score.corr(m[c]):+.3f}")
print("\nVERDICT RULE: wire only if RESID-IC OOS>0 (clears the value+quality bar) AND A/B delta OOS>0.")
