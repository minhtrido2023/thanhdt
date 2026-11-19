import pandas as pd
import os; MAP=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','commodity_cycle_te_20261026','commodity_map_te.csv')  # path-only edit after PREREG
def hh_set():
    m=pd.read_csv(MAP); return set(m[m.tier.isin(['A','B'])].ticker)
def grp(icb,tk,hh):
    if tk in hh: return '1_HANGHOA(tierA/B)'
    p=icb//100
    if p==83: return '2_NGANHANG'
    if p in (85,87) or icb in (8773,8775,8777): return '3_CK+BH'
    if p==86: return '4_BDS'
    if p in (23,27): return '5_XD-VLXD/CN-VANTAI'
    if p in (33,35,37,45,53,55,57): return '6_TIEUDUNG-DV'
    return '7_KHAC'
def era(y): return '2014-19' if y<=2019 else ('2020-23' if y<=2023 else '2024+')
def load(f):
    d=pd.read_csv(f); d=d[(~d.abandoned)&(~d.mtm)].copy(); hh=hh_set()
    d['grp']=[grp(int(i),t,hh) for i,t in zip(d.ICB_Code,d.ticker)]
    d['era']=d.year.map(era); d['ret_pct']=d.ret*100
    return d
