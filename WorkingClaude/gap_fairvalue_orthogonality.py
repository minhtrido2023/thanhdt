"""Orthogonality test: does justified-multiple discount (d_pb_just) ADD alpha on top of the EXISTING
rating_8l value composite (v3 = ey 1/PE + cfy 1/PCF + ps 1/PS, no-reward for negatives)?

Method (Fama-MacBeth): per date, rank-normalize both signals to z; cross-sectional OLS
  fwd_return ~ a + b1*composite_z + b2*d_pb_just_z ; collect b1,b2 across dates -> mean + t (IS/OOS).
If b2 (justified discount) stays significantly >0 CONTROLLING for composite -> it adds NEW info.
Also residual-IC: IC( d_pb_just orthogonalized to composite , fwd ). Redundant -> collapses to ~0.

d_pb_just = (ROIC5Y/r)/PB - 1, r=0.13 cost-of-equity placeholder. Quality-gated, liquid, 2014+.
CAVEAT: overlapping forward windows inflate t -> read t as directional, not precise.
"""
import duckdb, numpy as np, pandas as pd
PARQ = "data/bq_cache/ticker_prune.parquet"
cols = duckdb.connect().execute(f"DESCRIBE SELECT * FROM read_parquet('{PARQ}') LIMIT 1").df()["column_name"].tolist()
has_ps = "PS" in cols
print(f"PCF present: {'PCF' in cols} | PS present: {has_ps}")
ps_sel = "PS," if has_ps else ""
q = f"""SELECT time,ticker,PE,PCF,{ps_sel}PB,ROIC5Y,profit_1M,profit_2M
FROM read_parquet('{PARQ}')
WHERE time>=DATE '2014-01-01' AND PE>0 AND PB>0 AND ROIC5Y IS NOT NULL
AND ROE_Min3Y>=0 AND FSCORE>=5 AND Trading_Value_1M_P50>=5e9 AND profit_1M IS NOT NULL"""
df = duckdb.connect().execute(q).df()
df["ey"]  = np.where(df.PE>0, 1/df.PE, 0.0)
df["cfy"] = np.where(df.PCF>0, 1/df.PCF, 0.0)
df["ps_"] = np.where((df.PS>0), 1/df.PS, 0.0) if has_ps else 0.0
df["d_pb_just"] = (df.ROIC5Y/0.13)/df.PB - 1
df["yr"] = pd.to_datetime(df.time).dt.year

def zc(s):                                   # cross-sectional z, winsorized
    s = s.clip(s.quantile(.01), s.quantile(.99)); sd = s.std()
    return (s - s.mean())/sd if sd > 0 else s*0
gt = df.groupby("time")
df["composite"] = gt["ey"].transform(zc) + gt["cfy"].transform(zc) + (gt["ps_"].transform(zc) if has_ps else 0)
df["comp_z"] = df.groupby("time")["composite"].transform(zc)
df["just_z"] = df.groupby("time")["d_pb_just"].transform(zc)

def fama_macbeth(d, fwd):
    B1=[]; B2=[]; ICc=[]; ICj=[]; ICr=[]
    for _, g in d.groupby("time"):
        g = g.dropna(subset=["comp_z","just_z",fwd])
        if len(g) < 25: continue
        X = np.column_stack([np.ones(len(g)), g.comp_z, g.just_z]); y = g[fwd].values
        try: b = np.linalg.lstsq(X, y, rcond=None)[0]
        except Exception: continue
        B1.append(b[1]); B2.append(b[2])
        ICc.append(g.comp_z.corr(g[fwd], method="spearman"))
        ICj.append(g.just_z.corr(g[fwd], method="spearman"))
        # residual of just_z on comp_z -> orthogonal part
        rr = g.just_z - np.polyval(np.polyfit(g.comp_z, g.just_z, 1), g.comp_z)
        ICr.append(pd.Series(rr.values).corr(g[fwd].reset_index(drop=True), method="spearman"))
    def mt(a): a=np.array([x for x in a if pd.notna(x)]); return a.mean(), a.mean()/(a.std()/np.sqrt(len(a)))
    return mt(B1), mt(B2), mt(ICc), mt(ICj), mt(ICr), len(B2)

print(f"\n{'window':>9} {'horizon':>8} {'b_comp(t)':>14} {'b_just|comp(t)':>16} {'IC_comp':>8} {'IC_just':>8} {'IC_just|comp_resid':>18} {'ndates':>7}")
for wlab, dd in [("ALL", df), ("IS14-19", df[df.yr<=2019]), ("OOS20+", df[df.yr>=2020])]:
    for fwd in ["profit_1M","profit_2M"]:
        b1,b2,icc,icj,icr,n = fama_macbeth(dd, fwd)
        print(f"{wlab:>9} {fwd:>8} {b1[0]:>7.3f}({b1[1]:>4.1f}) {b2[0]:>9.3f}({b2[1]:>4.1f}) "
              f"{icc[0]:>8.3f} {icj[0]:>8.3f} {icr[0]:>14.3f}({icr[1]:>4.1f}) {n:>7}")
print("\nREAD: b_just|comp = justified-discount slope CONTROLLING for composite. IC_just|comp_resid = IC of the")
print("part of d_pb_just orthogonal to composite. Both stay >0 & significant OOS -> ADDS new alpha. Collapse -> redundant.")
