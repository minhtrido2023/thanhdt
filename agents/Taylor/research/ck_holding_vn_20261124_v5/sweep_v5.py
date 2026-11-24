"""v5 muc 2: QUET HE THONG con niem yet thieu trong stakes_all cho moi holding trong N (13) va moi holding qualify (116).
Nguon: raw/kbs_sh/*.json (co dong lon cua ~570 ma niem yet MV>=1.000 ty), raw/kbs_subs/<p>.json, VCI subs (v1 cache).
Ung vien (p, c): c niem yet, c khong nam trong stakes_all cua p, co dong lon h cua c (>=5%) thoa 1 trong:
  (A) ten chuan hoa h == ten mot con/lien ket KHONG niem yet cua p (KBS subs hoac VCI subs, MOI muc %, v4 chi xet >=50% va chi KBS/VCI);
  (B) ten h chua TU THUONG HIEU cua p (khai tay ben duoi, co ghi trong report).
Cung kiem (C): cap (p, c) DA co trong stakes_all nhung co dong lon KBS cua c ghi chinh p voi % khac > 3pp.
Tat dinh, khong mang. Ghi inputs/sweep_v5.csv."""
import os, json, glob, unicodedata
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, 'raw'); IN = os.path.join(HERE, 'inputs')
V1 = os.path.join(os.path.dirname(HERE), 'ck_holding_vn_20261123')


def norm(s):
    s = unicodedata.normalize('NFD', str(s).lower()); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('đ', 'd')
    for w in ['cong ty co phan', 'cong ty tnhh mot thanh vien', 'cong ty tnhh mtv', 'cong ty tnhh', 'ctcp', 'tong cong ty', 'cong ty',
              'joint stock company', 'jsc', 'tap doan', 'mtv', '.', ',', '-', '(', ')']:
        s = s.replace(w, ' ')
    return ' '.join(s.split())


L = pd.read_csv(os.path.join(V1, 'raw', 'listing_vci_20261123.csv')); name2tk = {}
for n, s in zip(L.organ_name.map(norm), L.symbol): name2tk.setdefault(n, s)
ST = pd.read_csv(os.path.join(IN, 'stakes_all.csv')); QUAL = pd.read_csv(os.path.join(IN, 'qualified_parents.csv')).parent.tolist()
N13 = ['APH', 'CMX', 'GEX', 'IPA', 'KSF', 'LHC', 'MSN', 'MVN', 'OGC', 'PAN', 'SNZ', 'VIC', 'VSC']
BRAND = {'MSN': ['masan'], 'VIC': ['vingroup', 'vinhomes', 'vinpearl', 'vinfast', 'vincom'], 'GEX': ['gelex'], 'SNZ': ['sonadezi'],
         'PAN': ['pan '], 'OGC': ['dai duong', 'ocean'], 'MVN': ['hang hai viet nam', 'vimc', 'vinalines'], 'KSF': ['sunshine'],
         'IPA': ['i p a', 'ipa '], 'CMX': ['camimex'], 'APH': ['an phat'], 'VSC': ['container viet nam', 'viconship', 'vsc '],
         'LHC': ['thuy loi lam dong']}
vci = {}
for f in glob.glob(os.path.join(V1, 'raw', 'vci_subs', '*.json')):
    if os.path.basename(f).startswith('_'): continue
    for r in json.load(open(f)): vci.setdefault(r['parent'], []).append((norm(r['organ_name']), float(r['ownership_percent']) * 100))
holders = []
for f in sorted(glob.glob(os.path.join(RAW, 'kbs_sh', '*.json'))):
    c = os.path.basename(f)[:-5]
    for r in json.load(open(f)):
        pct = float(r.get('ownership_percentage') or 0)
        if pct >= 5: holders.append((c, r.get('name'), norm(r.get('name')), pct, str(r.get('update_date'))[:10]))
rows = []
for p in sorted(set(QUAL) | set(N13)):
    have = set(ST[ST.parent == p]['sub'])
    fs = os.path.join(RAW, 'kbs_subs', p + '.json')
    subn = {norm(r.get('name')): float(r.get('ownership_percent') or 0) for r in (json.load(open(fs)) if os.path.exists(fs) else [])}
    for nm, s in vci.get(p, []): subn.setdefault(nm, s)
    unl = {nm: s for nm, s in subn.items() if not name2tk.get(nm)}
    br = BRAND.get(p, [])
    for c, hn, h, pct, dt in holders:
        if c == p: continue
        hk = name2tk.get(h)
        if hk == p and c in have:
            s0 = float(ST[(ST.parent == p) & (ST['sub'] == c)].stake.iloc[0])
            if abs(s0 - pct) > 3: rows.append(dict(parent=p, sub=c, rule='C_stake_diff', holder=hn, holder_pct=pct, date=dt, stake_v4=s0, via_pct=None, inN=p in N13))
            continue
        if c in have or hk: continue
        if h in unl: rows.append(dict(parent=p, sub=c, rule='A_unlisted_sub_name', holder=hn, holder_pct=pct, date=dt, stake_v4=None, via_pct=unl[h], inN=p in N13))
        elif any(b in h + ' ' for b in br): rows.append(dict(parent=p, sub=c, rule='B_brand', holder=hn, holder_pct=pct, date=dt, stake_v4=None, via_pct=None, inN=p in N13))
R = pd.DataFrame(rows).sort_values(['inN', 'parent', 'sub'], ascending=[False, True, True])
R.to_csv(os.path.join(IN, 'sweep_v5.csv'), index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
print(R.to_string(index=False)); print('n', len(R), 'inN', int(R.inN.sum()))
