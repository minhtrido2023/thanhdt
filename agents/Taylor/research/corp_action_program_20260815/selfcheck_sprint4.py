#!/usr/bin/env python3
import json,os,re
import numpy as np
import pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__));OUT=os.path.join(HERE,'out4')
r=json.load(open(os.path.join(OUT,'results.json')));rp=pd.read_csv(os.path.join(OUT,'rights_analysis.csv'));ap=pd.read_csv(os.path.join(OUT,'ais_analysis.csv'));mr=pd.read_csv(os.path.join(OUT,'rights_matched.csv'));ma=pd.read_csv(os.path.join(OUT,'ais_matched.csv'))
cs=[]
def ck(n,c):cs.append((n,bool(c)));print('PASS' if c else 'FAIL',n)
ck('S01 rights raw',r['funnel']['rights_raw']==548);ck('S02 rights core',r['funnel']['rights_core']==201);ck('S03 rights tickers',r['funnel']['rights_tickers']==152)
ck('S04 AIS raw',r['funnel']['ais_raw']==2044);ck('S05 pooled AIS core',r['funnel']['ais_core_pooled']==363);ck('S06 AIS conflicts disclosed',r['funnel']['ais_conflicts']==596)
ck('S07 issue price identity',np.allclose(rp.issue_price,rp.total_value/rp.issue_volume,equal_nan=True));ck('S08 TERP identity',np.allclose(rp.TERP,(rp.p_m1+rp.ratio_total*rp.issue_price)/(1+rp.ratio_total),equal_nan=True))
ck('S09 no raw ex Price column','p_0' not in rp.columns);ck('S10 TERP gate pass',r['rights_mechanical']['factor_match_1pct']>=.8)
ck('S11 primary rights N',r['rights_horizons']['R_20']['n']==201);ck('S12 primary rights CI includes zero',r['rights_horizons']['R_20']['lo']<0<r['rights_horizons']['R_20']['hi']);ck('S13 rights Holm primary null',r['rights_holm']['R_20']>=.05)
ck('S14 rights median negative',r['rights_horizons']['R_20']['median']<0);ck('S15 rights IS null',r['rights_splits']['IS']['lo']<0<r['rights_splits']['IS']['hi']);ck('S16 rights OOS null',r['rights_splits']['OOS']['lo']<0<r['rights_splits']['OOS']['hi'])
ck('S17 pooled AIS primary N',r['ais_horizons']['A_20']['n']==363);ck('S18 pooled AIS CI includes zero',r['ais_horizons']['A_20']['lo']<0<r['ais_horizons']['A_20']['hi']);ck('S19 all AIS Holm null',all(x>=.05 for x in r['ais_holm'].values()))
ck('S20 ESOP below floor',r['ais_splits']['ESOP']['n']<200);ck('S21 placement below floor',r['ais_splits']['PRIVATE_PLACEMENT']['n']<200);ck('S22 rights AIS below floor',r['ais_splits']['RIGHTS_AIS']['n']<200)
ck('S23 dilution bounded',ap.dilution.dropna().between(0,1).mean()>.95);ck('S24 dilution regression null',abs(r['dose_response']['regression']['dilution_t'])<1.96);ck('S25 discount regression null',abs(r['dose_response']['regression']['discount_t'])<1.96)
ck('S26 rights match caliper',r['robustness']['rights_match_balance']['max_abs_z']<=.5);ck('S27 AIS match caliper',r['robustness']['ais_match_balance']['max_abs_z']<=.5)
ck('S28 match uniqueness rights',not mr.assign(month=mr.anchor_date.str[:7]).duplicated(['month','control_ticker']).any());ck('S29 match uniqueness AIS',not ma.assign(month=ma.anchor_date.str[:7]).duplicated(['month','control_ticker']).any())
ck('S30 matched rights null',r['robustness']['rights_matched']['lo']<0<r['robustness']['rights_matched']['hi']);ck('S31 matched AIS null',r['robustness']['ais_matched']['lo']<0<r['robustness']['ais_matched']['hi'])
ck('S32 no BQ mutation',not any(re.search(r'\b(CREATE|INSERT|UPDATE|DELETE|MERGE|DROP|TRUNCATE)\b',open(os.path.join(dp,f)).read(),re.I) for dp,_,fs in os.walk(os.path.join(OUT,'sql')) for f in fs if f.endswith('.sql')))
bad=[x for x in cs if not x[1]];print(f'\n{len(cs)-len(bad)}/{len(cs)} PASS');raise SystemExit(1 if bad else 0)
