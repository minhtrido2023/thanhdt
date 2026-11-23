"""CK holding VN — buoc 1: gom dau vao thanh CSV khoa md5 (job Taylor_20261123_120407).
Nguon:
  - ty le so huu: raw/kbs_subs/*.json (KBS, ownership_percent theo BCTC update_date) + raw/vci_subs/*.json (VCI, doi chieu)
  - ten -> ma niem yet: raw/listing_vci_20261123.csv (khop ten chuan hoa, CHINH XAC)
  - VCSH me / NCI: raw/bs/<T>.csv (VCI CDKT quy: owners_equity, minority_interests)
  - ngay cong bo quy: data/bq_cache/ticker_financial.parquet (Release_Date, quarter)
  - gia CHUA dieu chinh: data/bq_cache/ticker/*.parquet cot Price (KHONG dung Close adj)
  - so CP point-in-time: oshares_live.oshares_at (neo AIS, tu choi khi khong chung nhan) -> fallback
    ticker_financial.OShares dong quy da cong bo <= D (gan co)
  - thanh khoan: data/bq_cache/universe_pit (in_universe, ruleset moi nhat) + ADV60 trung vi Price*Volume
Chay: cd WorkingClaude && source wc_env.sh && python3 <this>  (threads=1). Ghi inputs/*.csv.
"""
import os, sys, json, glob, unicodedata
import duckdb, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, 'raw'); OUT = os.path.join(HERE, 'inputs')
WC = '/home/trido/thanhdt/WorkingClaude'; sys.path.insert(0, WC)
os.makedirs(OUT, exist_ok=True)
PARENTS = ['VIC', 'GEX', 'SNZ', 'TVN', 'VGT', 'PAN', 'IPA', 'FIT', 'REE', 'GVR', 'KDC', 'SJG', 'CII', 'BCM', 'PLX', 'DXG', 'VEA']
EXCL = {'HHS', 'TCH', 'CRV'}   # doi tuong DD + chuoi cua no: KHONG dung gia (luat mu gia)
DATES = ['2026-03-31', '2026-06-30', '2026-09-30', '2026-11-20']


def norm(s):
    s = unicodedata.normalize('NFD', str(s).lower()); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('đ', 'd')
    for w in ['cong ty co phan', 'cong ty tnhh mot thanh vien', 'cong ty tnhh', 'ctcp', 'tong cong ty', 'cong ty',
              'joint stock company', 'jsc', 'tap doan', '.', ',', '-', '(', ')']:
        s = s.replace(w, ' ')
    return ' '.join(s.split())


# ---- 1. stakes ----
L = pd.read_csv(os.path.join(RAW, 'listing_vci_20261123.csv')); name2tk = dict(zip(L.organ_name.map(norm), L.symbol))
vci = {}
for f in glob.glob(os.path.join(RAW, 'vci_subs', '*.json')):
    for r in json.load(open(f)):
        if r.get('sub_organ_code') and len(str(r['sub_organ_code'])) == 3:
            vci[(r['parent'], r['sub_organ_code'])] = float(r['ownership_percent']) * 100
rows = []
for p in PARENTS:
    seen = set()
    for r in json.load(open(os.path.join(RAW, 'kbs_subs', p + '.json'))):
        tk = name2tk.get(norm(r.get('name')))
        if not tk or tk == p or tk in seen or tk in EXCL: continue
        seen.add(tk)
        rows.append(dict(parent=p, sub=tk, stake_kbs=float(r['ownership_percent']), type=r.get('type'),
                         stake_date=str(r.get('update_date'))[:10], stake_vci=vci.get((p, tk), np.nan), kbs_name=r.get('name')))
ST = pd.DataFrame(rows).sort_values(['parent', 'sub']); ST.to_csv(os.path.join(OUT, 'stakes.csv'), index=False)
TICK = sorted(set(PARENTS) | set(ST['sub']))

# ---- 2. VCSH me (VCI CDKT) + ngay cong bo (BQ cache) ----
con = duckdb.connect(config={'threads': 1})
rel = con.execute(f"""SELECT ticker, quarter, MIN(Release_Date) rel, MAX(BVPS*OShares) eq_tot_bq
  FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')
  WHERE ticker IN ({','.join(repr(t) for t in TICK)}) AND quarter >= '2025Q3' GROUP BY 1,2""").df()
fin = []
for t in TICK:
    f = os.path.join(RAW, 'bs', t + '.csv')
    if not os.path.exists(f) or os.path.getsize(f) < 10: continue
    b = pd.read_csv(f).set_index('item_id')
    for q in [c for c in b.columns if c[:2] == '20' and '-Q' in c]:
        def g(k):
            v = b.loc[k, q] if k in b.index else np.nan
            return float(v.iloc[0] if isinstance(v, pd.Series) else v)
        eq, mi = g('owners_equity'), g('minority_interests')
        fin.append(dict(ticker=t, quarter=q.replace('-', ''), eq_total=eq, nci=0.0 if np.isnan(mi) else mi))
FIN = pd.DataFrame(fin).merge(rel, on=['ticker', 'quarter'], how='outer')  # outer: ma khong co CDKT VCI van co VCSH tong BQ (fallback)
FIN['eq_parent'] = FIN.eq_total - FIN.nci
FIN.to_csv(os.path.join(OUT, 'fin_equity.csv'), index=False)

# ---- 3. gia chua dieu chinh + ADV60 + universe_pit ----
px = con.execute(f"""SELECT ticker, time, Price, Volume FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
  WHERE ticker IN ({','.join(repr(t) for t in TICK)}) AND time BETWEEN DATE '2025-12-01' AND DATE '2026-11-20'""").df()
px['time'] = pd.to_datetime(px.time)
up = con.execute(f"""SELECT ticker, time, in_universe, ruleset_version FROM read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet')
  WHERE ticker IN ({','.join(repr(t) for t in TICK)}) AND time BETWEEN DATE '2026-03-01' AND DATE '2026-11-20'""").df()
up['time'] = pd.to_datetime(up.time); up = up.sort_values('ruleset_version').groupby(['ticker', 'time']).tail(1)
P = []
for d in DATES:
    D = pd.Timestamp(d)
    for t, g in px[px.time <= D].sort_values('time').groupby('ticker'):
        last = g.iloc[-1]; w = g.tail(60)
        u = up[(up.ticker == t) & (up.time <= D)].sort_values('time').tail(1)
        P.append(dict(date=d, ticker=t, px_date=last.time.strftime('%Y-%m-%d'), price=float(last.Price),
                      adv60=float(np.median(w.Price * w.Volume)), in_universe=bool(u.in_universe.iloc[0]) if len(u) else False))
PX = pd.DataFrame(P); PX.to_csv(os.path.join(OUT, 'prices.csv'), index=False)

# ---- 4. so CP point-in-time ----
from oshares_live import oshares_at
osq = con.execute(f"""SELECT ticker, Release_Date rel, OShares FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')
  WHERE ticker IN ({','.join(repr(t) for t in TICK)}) AND OShares > 0""").df()
osq['rel'] = pd.to_datetime(osq.rel)
S = []
for d in DATES:
    res = oshares_at(TICK, d)
    for t in TICK:
        r = res.get(t) or {}
        fb = osq[(osq.ticker == t) & (osq.rel <= pd.Timestamp(d))].sort_values('rel').tail(1)
        fbv = float(fb.OShares.iloc[0]) if len(fb) else np.nan
        v = r.get('value')
        S.append(dict(date=d, ticker=t, shares=v if v else fbv, method=r.get('method') if v else 'FALLBACK_FIN_RELEASED',
                      live_value=v, fin_released=fbv))
pd.DataFrame(S).to_csv(os.path.join(OUT, 'shares_pit.csv'), index=False)
print('stakes', len(ST), 'tickers', len(TICK), 'fin', len(FIN), 'px', len(PX), 'shares', len(S))

# ---- 5. co tuc TIEN (DIV executed) 24 thang toi 2026-11-20: dong tien con -> me, me -> co dong ----
import subprocess, io
q = f"""SELECT ticker, CAST(exright_date AS STRING) exright_date, value_per_share, event_status
FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
WHERE event_code = 'DIV' AND ticker IN ({','.join(repr(t) for t in TICK)})
  AND exright_date BETWEEN DATE '2024-11-21' AND DATE '2026-11-20' AND event_status = 'executed'"""
r = subprocess.run(['bq', 'query', '--use_legacy_sql=false', '--format=csv', '--max_rows=100000',
                    '--project_id=lithe-record-440915-m9', q], capture_output=True, text=True, check=True)
DV = pd.read_csv(io.StringIO(r.stdout)).sort_values(['ticker', 'exright_date'])
DV.to_csv(os.path.join(OUT, 'divs_24m.csv'), index=False)
print('divs', len(DV))
