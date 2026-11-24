"""v5 (job Taylor_20261124_073243): them stage v5add (cuoi file) — MSR cho MSN look-through. Phan duoi giu nguyen v4.
v4 (job Taylor_20261124_053704): them stage capevents4 (ISS day du cot: total_value, value_per_share, ref_price, issue_date, public_date)
  + kbs4 (KBS co dong lon MOI cho con co PP/Rights, ghi raw/kbs_sh_v4/, khong ghi de cache v3). Phan duoi giu nguyen v3.
CK holding VN v3 — buoc 1: gom dau vao (job Taylor_20261124_041821; sua tu v2 Taylor_20261124_032640). Can mang + BQ cache local.
v3: BO tien loc 1-ngay (30/10/2026, VCSH tong) -> sub_set() = TOAN BO 116 holding qualify + moi con; do phu loc PIT theo thang o calc (VCSH me VCI).
    Them stage capevents: su kien co phieu (thuong/co tuc CP/phat hanh) tu tav2_bq.corporate_action cho moi ma trong mau.
Chay: cd WorkingClaude && source wc_env.sh && python3 <this> [stage...]   (threads=1; moi stage cache raw/)

QUY TRINH CHON MAU (tai lap, thay danh sach hardcode 17 ma cua v1):
  U0 = {ma co in_universe=TRUE trong universe_pit (ruleset moi nhat) tai >=1 ngay cuoi thang trong cua so}
       U {17 ma v1} (de doi chieu v1; ma v1 ngoai universe_pit duoc danh co parent_in_pit=False)
  Voi moi p in U0: KBS subsidiaries (con + lien ket, ownership_percent, update_date).
  Khop ten chuan hoa CHINH XAC -> ma niem yet (listing VCI). Them VCI subs (sub_organ_code 3 ky tu = ma).
  Tang 2: con KHONG niem yet q cua p (s_pq >= 50%) ; neu q xuat hien (ten chuan hoa) trong co dong lon KBS
       cua ma niem yet c => loi ich hieu dung s_pq * s_qc (ngay = max(update_date, ngay co dong)).
  NHAN VAO mau: p co >=1 con/lien ket NIEM YET (truc tiep hoac 2 tang) voi loi ich >= 20%.
  Loai: HHS/TCH/CRV (luat mu gia: KHONG doc gia).
"""
import os, sys, json, glob, time, unicodedata, subprocess, io
import duckdb, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, 'raw'); OUT = os.path.join(HERE, 'inputs')
V1 = os.path.join(os.path.dirname(HERE), 'ck_holding_vn_20261123')  # listing VCI + vci_subs cache cua v1 (chi doc)
WC = '/home/trido/thanhdt/WorkingClaude'; sys.path.insert(0, WC)
for d in ['kbs_subs', 'kbs_sh', 'vci_subs', 'vci_bs']: os.makedirs(os.path.join(RAW, d), exist_ok=True)
os.makedirs(OUT, exist_ok=True)
V1_PARENTS = ['VIC', 'GEX', 'SNZ', 'TVN', 'VGT', 'PAN', 'IPA', 'FIT', 'REE', 'GVR', 'KDC', 'SJG', 'CII', 'BCM', 'PLX', 'DXG', 'VEA']
EXCL = {'HHS', 'TCH', 'CRV'}
EXTRA = ['GEL']   # ca tang chong that GEX->GEL(Ha tang GELEX)->VGC 50,21% (brief ghi GEE; du lieu KBS cho thay VGC thuoc GEL); GEL ngoai universe_pit
W0, W1 = '2024-12-01', '2026-11-20'
con = duckdb.connect(config={'threads': 1})
PQ = f"read_parquet('{WC}/data/bq_cache/ticker/*.parquet')"
FINPQ = f"read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')"
STAGES = sys.argv[1:] or ['universe', 'kbs', 'match', 'vci', 'market']


def norm(s):
    s = unicodedata.normalize('NFD', str(s).lower()); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('đ', 'd')
    for w in ['cong ty co phan', 'cong ty tnhh mot thanh vien', 'cong ty tnhh mtv', 'cong ty tnhh', 'ctcp', 'tong cong ty', 'cong ty',
              'joint stock company', 'jsc', 'tap doan', 'mtv', '.', ',', '-', '(', ')']:
        s = s.replace(w, ' ')
    return ' '.join(s.split())


def month_ends():
    """Ngay giao dich cuoi moi thang (theo VNINDEX trong BQ cache) tu 12/2024; diem cuoi = 2026-11-20."""
    d = con.execute(f"SELECT DISTINCT time FROM {PQ} WHERE ticker='VNINDEX' AND time BETWEEN DATE '{W0}' AND DATE '{W1}' ORDER BY 1").df()
    d['time'] = pd.to_datetime(d.time); d['m'] = d.time.dt.to_period('M')
    return [t.strftime('%Y-%m-%d') for t in d.groupby('m').time.max()]


DATES = month_ends()
L = pd.read_csv(os.path.join(V1, 'raw', 'listing_vci_20261123.csv')); LISTED = set(L.symbol)
name2tk = {}
for n, s in zip(L.organ_name.map(norm), L.symbol): name2tk.setdefault(n, s)


def kbs(kind, t):
    f = os.path.join(RAW, 'kbs_subs' if kind == 'subs' else 'kbs_sh', t + '.json')
    if os.path.exists(f): return json.load(open(f))
    v1f = os.path.join(V1, 'raw', 'kbs_subs', t + '.json')
    if kind == 'subs' and os.path.exists(v1f):   # cung API, chup 23/11 (v1) -> tai dung, ghi lai ban sao
        d = json.load(open(v1f)); json.dump(d, open(f, 'w'), ensure_ascii=False); return d
    # goi thang endpoint KBS profile (1 lan cho ca subs + shareholders); vnstock wrapper bi gioi han 20 req/phut phia client
    import requests
    from vnstock.explorer.kbs.const import _STOCK_INFO_URL
    from vnstock.explorer.kbs.company import _SUBSIDIARIES_MAP, _SHAREHOLDERS_MAP
    for k in range(4):
        try:
            r = requests.get(f"{_STOCK_INFO_URL}/profile/{t}", params={'l': 1}, timeout=30,
                             headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
            if r.status_code != 200: raise RuntimeError(f'HTTP {r.status_code}')
            js = r.json() or {}
            sub = [{_SUBSIDIARIES_MAP.get(k2, k2): v for k2, v in x.items()} for x in (js.get('Subsidiaries') or [])]
            sh = [{_SHAREHOLDERS_MAP.get(k2, k2): v for k2, v in x.items()} for x in (js.get('Shareholders') or [])]
            fs = os.path.join(RAW, 'kbs_subs', t + '.json'); fh = os.path.join(RAW, 'kbs_sh', t + '.json')
            if not os.path.exists(fs): json.dump(sub, open(fs, 'w'), ensure_ascii=False)
            json.dump(sh, open(fh, 'w'), ensure_ascii=False); time.sleep(0.2)
            return json.load(open(f))
        except Exception as e:
            print(kind, t, 'ERR', repr(e)[:120], flush=True); time.sleep(10 * (k + 1))
    json.dump([], open(f, 'w')); return []


# ---------------- stage universe ----------------
if 'universe' in STAGES:
    q = ",".join(f"DATE '{d}'" for d in DATES)
    up = con.execute(f"""SELECT ticker, time, in_universe, ruleset_version FROM read_parquet('{WC}/data/bq_cache/universe_pit/*.parquet')
      WHERE time IN ({q})""").df()
    up = up.sort_values('ruleset_version').groupby(['ticker', 'time']).tail(1)
    pit = sorted(set(up[up.in_universe].ticker))
    U0 = sorted((set(pit) | set(V1_PARENTS) | set(EXTRA)) - EXCL - {'VNINDEX'})
    U0 = [t for t in U0 if t in LISTED]
    pd.DataFrame({'ticker': U0, 'in_pit_any_monthend': [t in pit for t in U0]}).to_csv(os.path.join(OUT, 'universe_U0.csv'), index=False)
    up.to_csv(os.path.join(OUT, 'universe_pit_monthend.csv'), index=False)
    json.dump(DATES, open(os.path.join(OUT, 'dates.json'), 'w'))
    print('U0', len(U0), 'dates', len(DATES), DATES[0], DATES[-1])

U0 = pd.read_csv(os.path.join(OUT, 'universe_U0.csv')).ticker.tolist()

# ---------------- stage kbs: subs cho U0 + co dong lon cho ma niem yet MV >= 1.000 ty ----------------
if 'kbs' in STAGES:
    for i, t in enumerate(U0):
        kbs('subs', t)
        if i % 50 == 0: print('kbs subs', i, t, flush=True)
    osh = con.execute(f"""SELECT ticker, arg_max(OShares, Release_Date) sh FROM {FINPQ} WHERE OShares>0 GROUP BY 1""").df()
    px = con.execute(f"SELECT ticker, Price FROM {PQ} WHERE time = DATE '2026-10-30'").df().merge(osh, on='ticker')
    px['mv'] = px.Price * px.sh
    tg = sorted(set(px[px.mv >= 1e12].ticker) & LISTED - EXCL)
    pd.DataFrame({'ticker': tg}).to_csv(os.path.join(OUT, 'sh_scan_targets.csv'), index=False)
    for i, t in enumerate(tg):
        kbs('sh', t)
        if i % 50 == 0: print('kbs sh', i, t, flush=True)
    print('kbs done subs', len(U0), 'sh', len(tg))

# ---------------- stage match: ty le so huu truc tiep + 2 tang ----------------
if 'match' in STAGES:
    vci = {}
    for f in glob.glob(os.path.join(V1, 'raw', 'vci_subs', '*.json')) + glob.glob(os.path.join(RAW, 'vci_subs', '*.json')):
        if os.path.basename(f).startswith('_'): continue
        for r in json.load(open(f)):
            vci[(r['parent'], norm(r['organ_name']))] = (float(r['ownership_percent']) * 100, str(r.get('sub_organ_code')))
    # co dong lon: ten co dong (chuan hoa) -> [(ma niem yet c, %, ngay)]
    holder = {}
    for f in glob.glob(os.path.join(RAW, 'kbs_sh', '*.json')):
        c = os.path.basename(f)[:-5]
        for r in json.load(open(f)):
            nm = r.get('name') or r.get('shareholder_name') or r.get('owner_name')
            pct = r.get('ownership_percentage') or r.get('ownership_percent')
            dt = str(r.get('update_date') or r.get('date') or '')[:10]
            if nm is None or pct is None: continue
            holder.setdefault(norm(nm), []).append((c, float(pct), dt))
    rows = []
    for p in U0:
        subs = kbs('subs', p); seen = {}
        own_holders = {norm(h.get('name')) for h in kbs('sh', p)}
        subs = [r for r in subs if norm(r.get('name')) not in own_holders]   # KBS ghi nham co dong me vao danh sach con
        for r in subs:
            nm = norm(r.get('name')); s = float(r.get('ownership_percent') or 0); dt = str(r.get('update_date'))[:10]
            tk = name2tk.get(nm)
            if tk and tk != p and tk not in EXCL:
                if tk not in seen or s > seen[tk]['stake']:
                    seen[tk] = dict(parent=p, sub=tk, stake=s, stake_date=dt, layer=1, src='KBS', via='', type=r.get('type'), name=r.get('name'))
            elif not tk and s >= 50:   # tang 2 qua con trung gian khong niem yet
                for c, s2, d2 in holder.get(nm, []):
                    if c == p or c in EXCL: continue
                    eff = s * s2 / 100
                    if c not in seen or eff > seen[c]['stake']:
                        seen[c] = dict(parent=p, sub=c, stake=eff, stake_date=max(dt, d2), layer=2, src='KBS+KBS_sh', via=f"{r.get('name')} {s}% x {s2}%",
                                       type='qua con trung gian', name=r.get('name'))
        # VCI: bo sung ma 3 ky tu co trong listing ma KBS khong co (ngay: khong co -> gan 2025-12-31 + co VCI_NODATE)
        for (pp, nm), (s, code) in vci.items():
            if pp != p: continue
            tk = code if (len(code) == 3 and code in LISTED) else name2tk.get(nm)
            if tk and tk != p and tk not in EXCL and tk not in seen and s > 0:
                seen[tk] = dict(parent=p, sub=tk, stake=s, stake_date='2025-12-31', layer=1, src='VCI_NODATE', via='', type='vci', name=nm)
            if not tk and s >= 50:
                for c, s2, d2 in holder.get(nm, []):
                    if c == p or c in EXCL: continue
                    eff = s * s2 / 100
                    if c not in seen or eff > seen[c]['stake']:
                        seen[c] = dict(parent=p, sub=c, stake=eff, stake_date=max('2025-12-31', d2), layer=2, src='VCI_NODATE+KBS_sh',
                                       via=f"{nm} {s}% x {s2}%", type='qua con trung gian', name=nm)
        for v in seen.values():
            v['stake_vci'] = next((vs for (pp, nm), (vs, code) in vci.items() if pp == p and (code == v['sub'] or name2tk.get(nm) == v['sub'])), np.nan)
            rows.append(v)
    ST = pd.DataFrame(rows).sort_values(['parent', 'sub'])
    ST.to_csv(os.path.join(OUT, 'stakes_all.csv'), index=False)
    Q = ST[ST.stake >= 20].groupby('parent').sub.count()
    qual = sorted(Q.index)
    pd.DataFrame({'parent': qual, 'n_listed_ge20': [int(Q[p]) for p in qual]}).to_csv(os.path.join(OUT, 'qualified_parents.csv'), index=False)
    print('stakes rows', len(ST), 'qualified parents', len(qual)); print(qual)


# ---------------- stage prescreen: loc so bo do phu (KHONG dung VCI) de gioi han so lan goi VCI ----------------
# do phu xap xi tai 2026-10-30 = sum s_i MV_i / [sum s_i MV_i + (E_tot_p - sum s_i E_tot_i)], E_tot = BVPS x OShares BQ (gom NCI),
# ty le hien tai (bo cong PIT). Nguong 30% << nguong do nhay thap nhat 50% => holding bi loai o day khong the dat 50%
# tru khi sai so E rat lon; danh sach loai + do phu xap xi ghi ra inputs/prescreen.csv.
if 'prescreen' in STAGES:
    ST = pd.read_csv(os.path.join(OUT, 'stakes_all.csv')); qual = pd.read_csv(os.path.join(OUT, 'qualified_parents.csv')).parent.tolist()
    T = sorted(set(qual) | set(ST[ST.parent.isin(qual)]['sub'])); tl = ','.join(repr(t) for t in T)
    f = con.execute(f"SELECT ticker, arg_max(BVPS*OShares, Release_Date) eqt, arg_max(OShares, Release_Date) shq FROM {FINPQ} WHERE ticker IN ({tl}) AND OShares>0 AND Release_Date <= DATE '2026-10-30' GROUP BY 1").df().set_index('ticker')
    p = con.execute(f"SELECT ticker, arg_max(Price, time) px FROM {PQ} WHERE ticker IN ({tl}) AND time <= DATE '2026-10-30' AND time >= DATE '2026-09-30' AND Volume>0 GROUP BY 1").df().set_index('ticker').px
    rows = []
    for q in qual:
        g = ST[ST.parent == q]; lmv = lb = 0.0
        for _, r in g.iterrows():
            if r['sub'] in p.index and r['sub'] in f.index: lmv += r.stake / 100 * p[r['sub']] * f.shq[r['sub']]; lb += r.stake / 100 * f.eqt[r['sub']]
        ep = f.eqt.get(q, np.nan); sotp = lmv + ep - lb
        rows.append(dict(parent=q, cov_approx=lmv / sotp if sotp > 0 else np.nan, listed_mv_bn=lmv / 1e9, eq_tot_bn=ep / 1e9))
    PS = pd.DataFrame(rows); FORCE = {'GEL', 'CII', 'GEE', 'SNZ', 'PAN', 'IPA', 'GEX', 'VIC', 'MSN'}   # v1 giu 6 + ca brief yeu cau do (GEE tang chong, MSN nhieu tang): do de bao cao, van chiu loc do phu o calc
    PS['pass'] = (PS.cov_approx >= 0.30) | PS.parent.isin(FORCE)
    PS.sort_values('cov_approx', ascending=False).to_csv(os.path.join(OUT, 'prescreen.csv'), index=False)
    print('prescreen pass', int(PS['pass'].sum()), 'of', len(PS)); print(PS[PS['pass']].round(3).to_string(index=False))


def sub_set():
    """v3: khong tien loc — moi holding qualify (>=1 con niem yet >=20%) + moi con cua chung."""
    ST = pd.read_csv(os.path.join(OUT, 'stakes_all.csv')); qual = sorted(pd.read_csv(os.path.join(OUT, 'qualified_parents.csv')).parent)
    return ST[ST.parent.isin(qual)], qual


# ---------------- stage vci: CDKT quy DAY DU lich su (VCI REST tra het quy; gioi han 4 ky cua vnstock la cat phia client) ----------------
def vci_bs(t):
    f = os.path.join(RAW, 'vci_bs', t + '.csv')
    if os.path.exists(f): return f
    from vnstock.explorer.vci.financial import Finance
    for k in range(3):
        try:
            df = Finance(t, period='quarter')._get_report(report_type='balance_sheet', period='quarter', limit=80, lang='en')
            df.to_csv(f, index=False); time.sleep(3.5); return f
        except BaseException as e:   # vnstock co the sys.exit khi cham gioi han -> bat ca SystemExit
            print('vci', t, 'ERR', repr(e)[:150], flush=True)
            if 'Không nhận được dữ liệu' in str(e): break   # v3: VCI khong co du lieu (tat dinh) -> khong retry
            time.sleep(65)
    open(f + '.fail', 'w').write('fail'); return None


if 'vci' in STAGES:
    ST, qual = sub_set()
    order = list(qual) + [s for s in ST.sort_values('stake', ascending=False)['sub'].unique() if s not in qual]
    for i, t in enumerate(order):
        if os.path.exists(os.path.join(RAW, 'vci_bs', t + '.csv.fail')): continue
        vci_bs(t)
        if i % 10 == 0: print('vci', i, len(order), t, flush=True)

# ---------------- stage market: gia CHUA dieu chinh, phien cuoi, ADV60, universe_pit, so CP PIT, BCTC BQ, co tuc tien ----------------
if 'market' in STAGES:
    ST, qual = sub_set(); TICK = sorted(set(qual) | set(ST['sub']))
    tl = ','.join(repr(t) for t in TICK)
    px = con.execute(f"""SELECT ticker, time, Price, Volume FROM {PQ} WHERE ticker IN ({tl}) AND time BETWEEN DATE '2024-08-01' AND DATE '{W1}'""").df()
    px['time'] = pd.to_datetime(px.time)
    sess = pd.to_datetime(con.execute(f"SELECT DISTINCT time FROM {PQ} WHERE ticker='VNINDEX' AND time BETWEEN DATE '2024-08-01' AND DATE '{W1}' ORDER BY 1").df().time)
    up = pd.read_csv(os.path.join(OUT, 'universe_pit_monthend.csv')); up['time'] = pd.to_datetime(up.time)
    P = []
    for d in DATES:
        D = pd.Timestamp(d); s60 = sess[sess <= D].iloc[-60:]
        for t, g in px[px.time <= D].sort_values('time').groupby('ticker'):
            tr = g[g.Volume > 0]
            if not len(tr): continue
            last = tr.iloc[-1]; w = g[g.time.isin(s60)]
            n_since = int(((sess > last.time) & (sess <= D)).sum())
            u = up[(up.ticker == t) & (up.time == D)]
            P.append(dict(date=d, ticker=t, px_date=last.time.strftime('%Y-%m-%d'), price=float(last.Price), sessions_since_trade=n_since,
                          adv60_mean=float((w.Price * w.Volume).sum() / 60), days_traded60=int((w.Volume > 0).sum()),
                          in_universe=bool(u.in_universe.iloc[0]) if len(u) else False))
    pd.DataFrame(P).to_csv(os.path.join(OUT, 'prices.csv'), index=False)
    from oshares_live import oshares_at
    osq = con.execute(f"SELECT ticker, quarter, Release_Date rel, OShares, BVPS FROM {FINPQ} WHERE ticker IN ({tl})").df()
    osq.to_csv(os.path.join(OUT, 'bq_fin.csv'), index=False); osq['rel'] = pd.to_datetime(osq.rel)
    S = []
    for d in DATES:
        res = oshares_at(TICK, d)
        for t in TICK:
            r = res.get(t) or {}
            fb = osq[(osq.ticker == t) & (osq.rel <= pd.Timestamp(d)) & (osq.OShares > 0)].sort_values('rel').tail(1)
            S.append(dict(date=d, ticker=t, live_value=r.get('value'), method=r.get('method'), anchor_date=r.get('anchor_date'),
                          fin_released=float(fb.OShares.iloc[0]) if len(fb) else np.nan, fin_q=fb.quarter.iloc[0] if len(fb) else None))
        print('shares', d, flush=True)
    pd.DataFrame(S).to_csv(os.path.join(OUT, 'shares_pit.csv'), index=False)
    q = f"""SELECT ticker, CAST(exright_date AS STRING) exright_date, value_per_share, event_status
    FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
    WHERE event_code = 'DIV' AND ticker IN ({tl}) AND exright_date BETWEEN DATE '2022-12-01' AND DATE '{W1}' AND event_status = 'executed'"""
    r = subprocess.run(['bq', 'query', '--use_legacy_sql=false', '--format=csv', '--max_rows=100000',
                        '--project_id=lithe-record-440915-m9', q], capture_output=True, text=True, check=True)
    pd.read_csv(io.StringIO(r.stdout)).sort_values(['ticker', 'exright_date']).to_csv(os.path.join(OUT, 'divs.csv'), index=False)
    print('market done (gia/so CP/co tuc)', len(P), len(S))

# v3: tach CDKT VCI -> bang dai thanh stage rieng 'vcilong' (chay sau khi stage vci tai xong)
if 'vcilong' in STAGES:
    ST, qual = sub_set(); TICK = sorted(set(qual) | set(ST['sub']))
    rows = []
    for t in TICK:
        f = os.path.join(RAW, 'vci_bs', t + '.csv')
        if not os.path.exists(f) or os.path.getsize(f) < 10: continue
        b = pd.read_csv(f)
        if 'item_id' not in b.columns: continue
        b = b.drop_duplicates('item_id').set_index('item_id')
        for c in [c for c in b.columns if str(c)[:2] == '20' and '-Q' in str(c)]:
            g = lambda k: float(b.loc[k, c]) if k in b.index and pd.notna(b.loc[k, c]) else np.nan
            rows.append(dict(ticker=t, quarter=c.replace('-', ''), owners_equity=g('owners_equity'), minority_interests=g('minority_interests'),
                             paid_in=next((g(k) for k in ['paid_in_capital', 'common_shares', 'owners_capital', 'share_capital'] if k in b.index), np.nan)))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, 'vci_bs_long.csv'), index=False)
    print('vcilong done', len(rows))

# ---------------- stage capevents (v3): su kien CO PHIEU (ISS) cho moi ma trong mau -> kiem so CP sau ngay ex ----------------
if 'capevents' in STAGES:
    ST, qual = sub_set(); TICK = sorted(set(qual) | set(ST['sub'])); tl = ','.join(repr(t) for t in TICK)
    q = f"""SELECT ticker, CAST(exright_date AS STRING) exright_date, CAST(listing_date AS STRING) listing_date, issue_method_code, exercise_ratio,
      issue_volumn, shares_delta, shares_total_after, event_status, event_title_vi
    FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
    WHERE event_code = 'ISS' AND ticker IN ({tl}) AND exright_date BETWEEN DATE '2024-06-01' AND DATE '{W1}'"""
    r = subprocess.run(['bq', 'query', '--use_legacy_sql=false', '--format=csv', '--max_rows=100000',
                        '--project_id=lithe-record-440915-m9', q], capture_output=True, text=True, check=True)
    ev = pd.read_csv(io.StringIO(r.stdout)).sort_values(['ticker', 'exright_date'])
    ev.to_csv(os.path.join(OUT, 'cap_events.csv'), index=False); print('cap_events', len(ev)); print(ev.issue_method_code.value_counts())

# ---------------- stage capevents4 (v4): ISS day du cot cho quy tac pha loang PP/Rights + khu dong trung ----------------
if 'capevents4' in STAGES:
    ST, qual = sub_set(); TICK = sorted(set(qual) | set(ST['sub'])); tl = ','.join(repr(t) for t in TICK)
    q = f"""SELECT id, ticker, CAST(exright_date AS STRING) exright_date, CAST(record_date AS STRING) record_date, CAST(issue_date AS STRING) issue_date,
      CAST(listing_date AS STRING) listing_date, CAST(public_date AS STRING) public_date, issue_method_code, exercise_ratio, issue_volumn,
      value_per_share, total_value, ref_price, shares_delta, shares_total_after, issue_status_code, event_status, event_title_vi
    FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
    WHERE event_code = 'ISS' AND ticker IN ({tl}) AND exright_date BETWEEN DATE '2024-06-01' AND DATE '{W1}'"""
    r = subprocess.run(['bq', 'query', '--use_legacy_sql=false', '--format=csv', '--max_rows=100000',
                        '--project_id=lithe-record-440915-m9', q], capture_output=True, text=True, check=True)
    ev = pd.read_csv(io.StringIO(r.stdout)).sort_values(['ticker', 'exright_date', 'issue_method_code', 'id'])
    ev.to_csv(os.path.join(OUT, 'cap_events_v4.csv'), index=False); print('cap_events_v4', len(ev)); print(ev.issue_method_code.value_counts())

# ---------------- stage kbs4 (v4): co dong lon KBS hien tai cua con co PP/Rights (doi chieu ty le me sau su kien) ----------------
if 'kbs4' in STAGES:
    import requests
    from vnstock.explorer.kbs.const import _STOCK_INFO_URL
    from vnstock.explorer.kbs.company import _SHAREHOLDERS_MAP
    os.makedirs(os.path.join(RAW, 'kbs_sh_v4'), exist_ok=True)
    ST, qual = sub_set(); ev = pd.read_csv(os.path.join(OUT, 'cap_events_v4.csv'))
    tk = sorted(set(ev[ev.issue_method_code.isin(['PP', 'Rights', 'PUBL'])].ticker) & set(ST['sub']))
    for t in tk:
        f = os.path.join(RAW, 'kbs_sh_v4', t + '.json')
        if os.path.exists(f): continue
        try:
            r = requests.get(f"{_STOCK_INFO_URL}/profile/{t}", params={'l': 1}, timeout=30, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
            js = r.json() or {}
            sh = [{_SHAREHOLDERS_MAP.get(k2, k2): v for k2, v in x.items()} for x in (js.get('Shareholders') or [])]
            json.dump(sh, open(f, 'w'), ensure_ascii=False); time.sleep(0.5)
        except Exception as e:
            print('kbs4', t, 'ERR', repr(e)[:120], flush=True)
    print('kbs4', len(tk), tk)

# ---------------- stage v5add (v5, job Taylor_20261124_073243): them ma con MOI (MSR) vao inputs/ — APPEND, khong ghi de dong cu ----------------
# Cung cong thuc stage market/vci/vcilong/capevents4 o tren, chi cho ADD5. Ma da co du lieu (MML, MCH, TCB) khong tai lai.
ADD5 = ['MSR']
if 'v5add' in STAGES:
    tl = ','.join(repr(t) for t in ADD5)
    px = con.execute(f"""SELECT ticker, time, Price, Volume FROM {PQ} WHERE ticker IN ({tl}) AND time BETWEEN DATE '2024-08-01' AND DATE '{W1}'""").df()
    px['time'] = pd.to_datetime(px.time)
    sess = pd.to_datetime(con.execute(f"SELECT DISTINCT time FROM {PQ} WHERE ticker='VNINDEX' AND time BETWEEN DATE '2024-08-01' AND DATE '{W1}' ORDER BY 1").df().time)
    up = pd.read_csv(os.path.join(OUT, 'universe_pit_monthend.csv')); up['time'] = pd.to_datetime(up.time)
    P = []
    for d in DATES:
        D = pd.Timestamp(d); s60 = sess[sess <= D].iloc[-60:]
        for t, g in px[px.time <= D].sort_values('time').groupby('ticker'):
            tr = g[g.Volume > 0]
            if not len(tr): continue
            last = tr.iloc[-1]; w = g[g.time.isin(s60)]
            n_since = int(((sess > last.time) & (sess <= D)).sum())
            u = up[(up.ticker == t) & (up.time == D)]
            P.append(dict(date=d, ticker=t, px_date=last.time.strftime('%Y-%m-%d'), price=float(last.Price), sessions_since_trade=n_since,
                          adv60_mean=float((w.Price * w.Volume).sum() / 60), days_traded60=int((w.Volume > 0).sum()),
                          in_universe=bool(u.in_universe.iloc[0]) if len(u) else False))
    # append dang TEXT (ghi lai ca file lam lech chu so cuoi float cua dong cu); chay lai: xoa dong ADD5 truoc
    _pf = os.path.join(OUT, 'prices.csv'); _keep = [l for l in open(_pf) if l.split(',')[1] not in ADD5]
    open(_pf, 'w').write(''.join(_keep) + pd.DataFrame(P).to_csv(index=False, header=False))
    from oshares_live import oshares_at
    osq = con.execute(f"SELECT ticker, quarter, CAST(Release_Date AS DATE) rel, OShares, BVPS FROM {FINPQ} WHERE ticker IN ({tl})").df()
    osq['rel'] = pd.to_datetime(osq.rel).dt.strftime('%Y-%m-%d')   # cung dinh dang ngay voi dong cu (v5: lan dau ghi '... 00:00:00', da sua tay bang sed)
    oldq = pd.read_csv(os.path.join(OUT, 'bq_fin.csv')); oldq = oldq[~oldq.ticker.isin(ADD5)]
    pd.concat([oldq, osq]).to_csv(os.path.join(OUT, 'bq_fin.csv'), index=False); osq['rel'] = pd.to_datetime(osq.rel)
    S = []
    for d in DATES:
        res = oshares_at(ADD5, d)
        for t in ADD5:
            r = res.get(t) or {}
            fb = osq[(osq.ticker == t) & (osq.rel <= pd.Timestamp(d)) & (osq.OShares > 0)].sort_values('rel').tail(1)
            S.append(dict(date=d, ticker=t, live_value=r.get('value'), method=r.get('method'), anchor_date=r.get('anchor_date'),
                          fin_released=float(fb.OShares.iloc[0]) if len(fb) else np.nan, fin_q=fb.quarter.iloc[0] if len(fb) else None))
    olds = pd.read_csv(os.path.join(OUT, 'shares_pit.csv')); olds = olds[~olds.ticker.isin(ADD5)]
    pd.concat([olds, pd.DataFrame(S)]).to_csv(os.path.join(OUT, 'shares_pit.csv'), index=False)
    for t in ADD5: vci_bs(t)
    rows = []
    for t in ADD5:
        f = os.path.join(RAW, 'vci_bs', t + '.csv')
        b = pd.read_csv(f).drop_duplicates('item_id').set_index('item_id')
        for c in [c for c in b.columns if str(c)[:2] == '20' and '-Q' in str(c)]:
            g = lambda k: float(b.loc[k, c]) if k in b.index and pd.notna(b.loc[k, c]) else np.nan
            rows.append(dict(ticker=t, quarter=c.replace('-', ''), owners_equity=g('owners_equity'), minority_interests=g('minority_interests'),
                             paid_in=next((g(k) for k in ['paid_in_capital', 'common_shares', 'owners_capital', 'share_capital'] if k in b.index), np.nan)))
    oldb = pd.read_csv(os.path.join(OUT, 'vci_bs_long.csv')); oldb = oldb[~oldb.ticker.isin(ADD5)]
    pd.concat([oldb, pd.DataFrame(rows)]).to_csv(os.path.join(OUT, 'vci_bs_long.csv'), index=False)
    q = f"""SELECT id, ticker, CAST(exright_date AS STRING) exright_date, CAST(record_date AS STRING) record_date, CAST(issue_date AS STRING) issue_date,
      CAST(listing_date AS STRING) listing_date, CAST(public_date AS STRING) public_date, issue_method_code, exercise_ratio, issue_volumn,
      value_per_share, total_value, ref_price, shares_delta, shares_total_after, issue_status_code, event_status, event_title_vi
    FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
    WHERE event_code = 'ISS' AND ticker IN ({tl}) AND exright_date BETWEEN DATE '2024-06-01' AND DATE '{W1}'"""
    r = subprocess.run(['bq', 'query', '--use_legacy_sql=false', '--format=csv', '--max_rows=100000', '--project_id=lithe-record-440915-m9', q],
                       capture_output=True, text=True, check=True)
    ev = pd.read_csv(io.StringIO(r.stdout)) if r.stdout.strip() else pd.DataFrame()
    olde = pd.read_csv(os.path.join(OUT, 'cap_events_v4.csv')); olde = olde[~olde.ticker.isin(ADD5)]
    pd.concat([olde, ev]).sort_values(['ticker', 'exright_date', 'issue_method_code', 'id']).to_csv(os.path.join(OUT, 'cap_events_v4.csv'), index=False)
    q = f"""SELECT ticker, CAST(exright_date AS STRING) exright_date, value_per_share, event_status
    FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
    WHERE event_code = 'DIV' AND ticker IN ({tl}) AND exright_date BETWEEN DATE '2022-12-01' AND DATE '{W1}' AND event_status = 'executed'"""
    r = subprocess.run(['bq', 'query', '--use_legacy_sql=false', '--format=csv', '--max_rows=100000', '--project_id=lithe-record-440915-m9', q],
                       capture_output=True, text=True, check=True)
    dv = pd.read_csv(io.StringIO(r.stdout)) if r.stdout.strip() else pd.DataFrame()
    oldd = pd.read_csv(os.path.join(OUT, 'divs.csv')); oldd = oldd[~oldd.ticker.isin(ADD5)]
    pd.concat([oldd, dv]).sort_values(['ticker', 'exright_date']).to_csv(os.path.join(OUT, 'divs.csv'), index=False)
    print('v5add', ADD5, 'px', len(P), 'sh', len(S), 'vci', len(rows), 'iss', len(ev), 'div', len(dv))
