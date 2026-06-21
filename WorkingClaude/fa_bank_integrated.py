#!/usr/bin/env python3
"""
fa_bank_integrated.py — integrated validation of the bank FA sub-model
======================================================================
Tests whether replacing the GENERIC FA tier with the bank-specific tier (for
ICB 8355 names only) improves the BA-core stock selection used by v11/v12.

Faithful to production: ports classify_play_type() from recommend_holistic.py
(v11 thresholds) exactly. The only change between the two scenarios is the FA
tier fed for bank (8355) rows. ta_score's sector-8 ±10 FA term is recomputed
with whichever tier the scenario uses (fully consistent).

Metric: among BA-core BUY signals, forward profit_3M mean/median/win-rate/N and
an annualized proxy (compounding 4 independent 3M trades). Reported for the FULL
book and BANK-only signals, GENERIC vs BANK-augmented, plus IS/OOS split.

Realized profit_3M = the 63-session forward return already stored in BQ; this is
the same outcome variable the canonical backtest_holistic.py uses.
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd

WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"
BQ_BIN=r"bq"

# ta WITHOUT the sector-8 fa-dependent term (added in Python per-scenario)
SQL="""
WITH fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
),
vmax AS (SELECT t.time, t.D_RSI AS vni_rsi_max3m FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX')
SELECT t.ticker, t.time, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sector,
  IF(ABS(t.profit_3M)>400, NULL, t.profit_3M) AS p3m,
  s5.state AS state5, fa.fa_tier AS fa_generic,
  SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1 AS np_yoy, fin.Revenue_YoY_P0 AS rev_yoy,
  (t.PE-t.PE_MA5Y)/NULLIF(t.PE_SD5Y,0) AS pe_z,
  (t.D_RSI>0.90 OR (t.MA20>0 AND t.Close/t.MA20>1.25) OR (t.HI_3M_T1>0 AND t.Close/t.HI_3M_T1<0.85)) AS warn_ext,
  (CASE WHEN t.D_RSI>0.50 THEN 25 ELSE 0 END
  +CASE WHEN t.Close>t.MA50 AND t.MA50>t.MA200 THEN 25 ELSE 0 END
  +CASE WHEN t.Volume>=t.Volume_3M_P50*1.3 AND t.Close>t.Close_T1 THEN 20 ELSE 0 END
  +CASE WHEN t.D_MACDdiff>0 THEN 15 ELSE 0 END
  +CASE WHEN t.Close>t.MA20 THEN 15 ELSE 0 END
  +CASE WHEN t.D_RSI>0.75 THEN 5 ELSE 0 END
  +CASE WHEN t.D_RSI<0.30 THEN -10 ELSE 0 END
  +CASE WHEN t.PE>0 AND t.PE_MA5Y>0 AND t.PE<t.PE_MA5Y-0.5*t.PE_SD5Y THEN 15 ELSE 0 END
  +CASE WHEN t.PE>0 AND t.PE_MA5Y>0 AND t.PE>t.PE_MA5Y+1.0*t.PE_SD5Y THEN -15 ELSE 0 END
  +CASE WHEN vmax.vni_rsi_max3m>0.65 THEN 10 ELSE 0 END
  +CASE WHEN t.ID_HI_3Y<=5 THEN 8 ELSE 0 END
  +CASE WHEN t.D_RSI_Max1W>0.65 THEN 5 ELSE 0 END
  +CASE WHEN t.FSCORE>=8 THEN 10 ELSE 0 END
  +CASE WHEN t.NP_P0>t.NP_P4*1.5 AND t.NP_P4>0 THEN 8 ELSE 0 END
  +CASE WHEN t.NP_P0<t.NP_P4*0.7 AND t.NP_P4>0 THEN -8 ELSE 0 END
  +CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (8,9) THEN 5 ELSE 0 END
  +CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (4,7) THEN -5 ELSE 0 END
  +CASE WHEN t.MA50_T1>0 AND t.MA50>t.MA50_T1 THEN 5 ELSE 0 END
  +CASE WHEN t.MA50_T1>0 AND t.MA50>t.MA50_T1*1.005 THEN 5 ELSE 0 END
  +CASE WHEN t.MA50_T1>0 AND t.MA50<t.MA50_T1 THEN -5 ELSE 0 END
  +CASE WHEN t.HI_3M_T1>0 AND t.Close/t.HI_3M_T1<0.85 THEN -10 ELSE 0 END
  +CASE WHEN t.NP_P0>t.NP_P1*1.2 AND t.NP_P1>0 THEN 8 ELSE 0 END) AS ta_base
FROM tav2_bq.ticker AS t
LEFT JOIN tav2_bq.vnindex_5state AS s5 ON s5.time=t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time
     AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time
     AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN vmax ON vmax.time=t.time
WHERE t.time BETWEEN DATE "2014-01-01" AND DATE "2026-01-16"
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.profit_3M IS NOT NULL AND t.Volume_3M_P50*t.Close>=1e9
"""

BA_CORE={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"}

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as fh:
        fh.write(sql); tmp=fh.name
    try:
        cmd=(f'"{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} '
             f'--format=csv --max_rows=3000000 < "{tmp}"')
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=1200,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode!=0: raise RuntimeError((r.stdout or r.stderr)[:800])
    return pd.read_csv(StringIO(r.stdout.strip()))

def classify(ta, fa_tier, state5, pe_z, np_yoy, rev_yoy, warn):
    """Port of recommend_holistic.classify_play_type (v11), minus RE_BACKLOG (RE not banks)."""
    if pd.isna(state5) or int(state5) in (1,2): return "AVOID_bear"
    s=int(state5)
    if fa_tier=="E": return "AVOID_faE"
    if ta>=170 and s in (4,5) and fa_tier in ("C","D"): return "MEGA"
    if ta>=170 and s in (4,5): return "S_PRO"
    if ta>=155 and s in (4,5) and fa_tier in ("C","D"): return "MOMENTUM"
    if ta>=155 and s in (4,5) and fa_tier in ("A","B"): return "MOMENTUM_QUALITY"
    if ta>=155 and s==3 and fa_tier in ("C","D"): return "MOMENTUM_N"
    if fa_tier in ("A","B") and not pd.isna(pe_z) and pe_z<-0.5 and ta>=95 and s in (3,4,5) and not warn:
        return "COMPOUNDER_BUY"
    if fa_tier=="C" and ta>=100 and s in (4,5) and ((not pd.isna(np_yoy) and np_yoy>0.20) or (not pd.isna(rev_yoy) and rev_yoy>0.20)):
        return "DEEP_VALUE_RECOVERY"
    if ta>=140 and s in (4,5): return "MOMENTUM_S"
    if ta>=125 and s in (4,5): return "MOMENTUM_A"
    if ta>=140 and s==3: return "MOMENTUM_S_N"
    if fa_tier in ("A","B") and 70<=ta<130: return "COMPOUNDER_HOLD"
    if fa_tier in ("A","B"): return "WAIT"
    return "PASS"

def ta_with_sector8(ta_base, sector, fa_tier):
    if sector==8 and fa_tier=="D": return ta_base+10
    if sector==8 and fa_tier=="A": return ta_base-10
    return ta_base

def book_stats(df, label, P):
    g=df[df["is_core"]].copy()
    n=len(g);
    if n==0: P(f"{label:<22}{'(no signals)':>10}"); return
    mean=g["p3m"].median()*0+g["p3m"].mean(); med=g["p3m"].median(); win=(g["p3m"]>0).mean()*100
    ann=((1+g["p3m"].mean()/100)**4-1)*100
    P(f"{label:<22}{n:>8,}{mean:>9.2f}%{med:>9.2f}%{win:>8.1f}%{ann:>10.1f}%")

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    cache=os.path.join(WORKDIR,"data","_fa_bank_integrated_raw.csv")
    if os.path.exists(cache):
        df=pd.read_csv(cache); P0=lambda *a:None
    else:
        df=bq_query(SQL); df.to_csv(cache,index=False)
    df["time"]=pd.to_datetime(df["time"])
    P("# Integrated validation: bank FA sub-model in v11 BA-core book")
    P("")
    P(f"daily signal rows {len(df):,} | {df['time'].min().date()}→{df['time'].max().date()}")

    # ── as-of join bank_tier (ICB 8355) ───────────────────────────────────
    bk=pd.read_csv(os.path.join(WORKDIR,"data/fundamental_rating_banks.csv"))[["ticker","time","bank_tier"]]
    bk["time"]=pd.to_datetime(bk["time"])
    bk=bk.sort_values("time")
    parts=[]
    for tk,g in df[df["sector"]==8].sort_values("time").groupby("ticker"):
        b=bk[bk["ticker"]==tk]
        if len(b)==0:
            g["bank_tier"]=np.nan
        else:
            g=pd.merge_asof(g, b[["time","bank_tier"]], on="time", direction="backward")
        parts.append(g)
    banks=pd.concat(parts) if parts else df.iloc[0:0].assign(bank_tier=np.nan)
    df=df.merge(banks[["ticker","time","bank_tier"]], on=["ticker","time"], how="left")

    n_bank_rows=(df["sector"]==8).sum()
    n_bank_tiered=df["bank_tier"].notna().sum()
    P(f"bank (8355) rows {n_bank_rows:,} | with bank_tier mapped {n_bank_tiered:,}")
    P("")

    # ── build two tier columns ─────────────────────────────────────────────
    df["fa_bank"]=np.where((df["sector"]==8)&df["bank_tier"].notna(), df["bank_tier"], df["fa_generic"])

    # ── classify both scenarios ────────────────────────────────────────────
    for scen,tcol in [("gen","fa_generic"),("bank","fa_bank")]:
        ta=df.apply(lambda r: ta_with_sector8(r["ta_base"], r["sector"], r[tcol]), axis=1)
        df[f"play_{scen}"]=[classify(ta.iloc[i], df[tcol].iloc[i], df["state5"].iloc[i],
                                     df["pe_z"].iloc[i], df["np_yoy"].iloc[i],
                                     df["rev_yoy"].iloc[i], bool(df["warn_ext"].iloc[i]))
                            for i in range(len(df))]
        df[f"core_{scen}"]=df[f"play_{scen}"].isin(BA_CORE)

    def report(sub, title):
        P(f"## {title}")
        P(f"{'scenario':<22}{'N':>8}{'mean':>9}{'median':>9}{'win%':>8}{'annualized':>11}")
        P("-"*67)
        for scen in ["gen","bank"]:
            s=sub.copy(); s["is_core"]=s[f"core_{scen}"]
            book_stats(s, f"{'GENERIC' if scen=='gen' else 'BANK-augmented'}", P)
        P("")

    # full book
    report(df, "FULL BA-core book (all sectors)")
    # bank-only signals
    report(df[df["sector"]==8], "BANK-only BA-core signals (where the change lands)")
    # OOS bank-only
    report(df[(df["sector"]==8)&(df["time"]>="2020-01-01")], "BANK-only BA-core, OOS 2020+")

    # ── what changed: bank signals added/removed ──────────────────────────
    bdf=df[df["sector"]==8].copy()
    added=bdf[~bdf["core_gen"] & bdf["core_bank"]]      # bank model ADDS to book
    removed=bdf[bdf["core_gen"] & ~bdf["core_bank"]]    # bank model REMOVES from book
    kept=bdf[bdf["core_gen"] & bdf["core_bank"]]
    P("## Composition change in bank signals (generic → bank-augmented)")
    P(f"{'group':<24}{'N':>8}{'mean p3m':>11}{'win%':>8}")
    P("-"*51)
    for nm,gg in [("ADDED by bank model",added),("REMOVED by bank model",removed),("kept in both",kept)]:
        if len(gg):
            P(f"{nm:<24}{len(gg):>8,}{gg['p3m'].mean():>10.2f}%{(gg['p3m']>0).mean()*100:>7.1f}%")
        else:
            P(f"{nm:<24}{0:>8}")
    P("")
    P("Read: if ADDED signals have higher mean/win than REMOVED, the bank model")
    P("improves selection (adds winners, drops losers among bank names).")
    P("")

    # ── RIGHT CHANNEL: quality model should help the COMPOUNDER (A/B hold) book,
    #    and the E-tier EXCLUSION — NOT the C/D momentum book. ────────────────
    QUAL={"COMPOUNDER_BUY","COMPOUNDER_HOLD","WAIT"}
    P("## Quality channels for banks (where a quality ranker SHOULD help)")
    P(f"{'channel / scenario':<30}{'N':>8}{'mean p3m':>11}{'win%':>8}")
    P("-"*57)
    bdf=df[df["sector"]==8]
    for nm,sel in [("COMPOUNDER_BUY",lambda s:df[f"play_{s}"]=="COMPOUNDER_BUY"),
                   ("Quality-hold (A/B route)",lambda s:df[f"play_{s}"].isin(QUAL)),
                   ("AVOID_faE (exclusion)",lambda s:df[f"play_{s}"]=="AVOID_faE")]:
        for scen in ["gen","bank"]:
            g=bdf[sel(scen).reindex(bdf.index).fillna(False)]
            tag=f"{nm} [{'GEN' if scen=='gen' else 'BANK'}]"
            if len(g): P(f"{tag:<30}{len(g):>8,}{g['p3m'].mean():>10.2f}%{(g['p3m']>0).mean()*100:>7.1f}%")
            else: P(f"{tag:<30}{0:>8}")
        P("")
    P("Read: for COMPOUNDER/quality-hold, HIGHER mean = bank model picks better")
    P("quality banks to hold. For AVOID_faE, LOWER mean = better blow-up exclusion.")
    P("")

    with open(os.path.join(WORKDIR,"data","fa_bank_integrated.md"),"w",encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    P("Saved data/fa_bank_integrated.md")

if __name__=="__main__":
    main()
