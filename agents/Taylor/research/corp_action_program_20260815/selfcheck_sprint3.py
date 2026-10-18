#!/usr/bin/env python3
"""Independent invariants for Sprint 3 artifacts; no network access."""
import json, os, re
import numpy as np
import pandas as pd

HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,"out3")
d=pd.read_csv(os.path.join(OUT,"linked_panel.csv")); a=pd.read_csv(os.path.join(OUT,"analysis_panel.csv")); r=json.load(open(os.path.join(OUT,"results.json")))
m=pd.read_csv(os.path.join(OUT,"matched_control.csv"))
checks=[]
def ck(name,cond):
    checks.append((name,bool(cond))); print(("PASS" if cond else "FAIL"),name)

ck("S01 raw panel count",len(d)==1914)
ck("S02 canonical ledger present",(d.ledger_components>0).all())
ck("S03 SQL ratios equal ledger",np.allclose(d.ratio_total,d.ledger_ratio_total,atol=1e-12))
ck("S04 two known subtypes only",set(d.subtype_list)<=set(["STOCK_DIVIDEND","BONUS","BONUS,STOCK_DIVIDEND"]))
ck("S05 exact core N",r["funnel"]["core"]==862)
ck("S06 core ticker N",r["funnel"]["core_tickers"]==333)
ck("S07 extreme-ratio count disclosed",r["funnel"]["ratio_gt_200pct"]==2)
ck("S08 AIS conflict count",r["funnel"]["ais_conflicts"]==242)
ck("S09 AIS confirmatory floor",r["funnel"]["ais_confirmatory"]>=200 and r["funnel"]["ais_tickers"]>=60)
ck("S10 ex primary N",r["ex_horizons"]["EX_20"]["n"]==862)
ck("S11 ex primary recompute",np.isclose(a[(a.in_universe_pit==1)&(a.ratio_total<=2)&(a.ratio_total>0)&(a.v_0>0)&(a.n_other_adjust_21==0)].BHAR_EX_20.mean(),r["ex_horizons"]["EX_20"]["mean"]))
ck("S12 ex primary CI contains zero",r["ex_horizons"]["EX_20"]["lo"]<0<r["ex_horizons"]["EX_20"]["hi"])
ck("S13 ex Holm primary not significant",r["ex_holm"]["EX_20"]>=.05)
ck("S14 AIS Holm 20 significant",r["ais_holm"]["AIS_20"]<.05)
ck("S15 AIS OOS CI contains zero",r["ais_splits"]["OOS"]["lo"]<0<r["ais_splits"]["OOS"]["hi"])
ck("S16 ex OOS CI contains zero",r["primary_splits"]["OOS"]["lo"]<0<r["primary_splits"]["OOS"]["hi"])
ck("S17 placebo positive",r["robustness"]["placebo"]["lo"]>0)
ck("S18 pretrend positive",r["robustness"]["pretrend"]["lo"]>0)
ck("S19 mechanical gate passes",r["mechanical"]["factor_match_1pct"]>=.80)
ck("S20 no ex-date Price in analysis source","p_0" not in a.columns)
ck("S21 matched N floor",r["robustness"]["matched_control"]["n"]>=200)
ck("S22 matched caliper",r["robustness"]["matched_balance"]["max_abs_z"]<=.5+1e-12)
ck("S23 matched CI contains zero",r["robustness"]["matched_control"]["lo"]<0<r["robustness"]["matched_control"]["hi"])
ck("S24 ratio return coefficient null",abs(r["regression"]["bhar_ex20"]["ratio_log_t"])<1.96)
ck("S25 ratio liquidity coefficient null",abs(r["regression"]["dlog_adtv"]["ratio_log_t"])<1.96)
ck("S26 prereg marker",os.path.exists(os.path.join(HERE,"SPRINT3_PREREG.md")))
ck("S27 report marker",os.path.exists(os.path.join(HERE,"SPRINT3_STOCK_DISTRIBUTION.md")))
ck("S28 no BQ mutation SQL",not any(re.search(r"\b(CREATE|INSERT|UPDATE|DELETE|MERGE|DROP|TRUNCATE)\b",open(os.path.join(dp,f)).read(),re.I) for dp,_,fs in os.walk(os.path.join(OUT,"sql")) for f in fs if f.endswith('.sql')))
ck("S29 controls unique within month",not m.assign(month=m.ex_date.str[:7]).duplicated(["month","control_ticker"]).any())
ck("S30 matched outcomes finite",np.isfinite(m.MATCHED_DIFF_20).all())
bad=[x for x in checks if not x[1]]; print(f"\n{len(checks)-len(bad)}/{len(checks)} PASS")
raise SystemExit(1 if bad else 0)
