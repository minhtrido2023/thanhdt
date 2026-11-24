"""CK holding VN v5 (job Taylor_20261124_073243) = v4 + PREREG_v5.md: S1 ty le so huu co ngay (stakes_override_v5.csv: MSN->MCH/TCB/MML/MSR, VSC->VGR, PAN->FMC),
  S2 lai pha loang cua me khi khong tham gia, S3 bo PROCEEDS_ADD khi BCTC con cu >4 quy, S4 bien the ambiguous dung chu. Ghi calc_out_v5.json + panel_v5.csv.
CK holding VN v4 (job Taylor_20261124_053704) = v3 + sua theo PREREG_v4.md (F1 pha loang PP/Rights/PUBL, F2 khu trung, F3 i-v, F5).
Goc v3: CK holding VN v3 — buoc 2 (job Taylor_20261124_041821). Tat dinh, khong mang. Chay duoc ca pandas 2.x va 3 (ket qua phai trung).
Chay: python3 calc_ck_v4.py > run1.txt ; lan 2 > run2.txt ; $DNA_PYEXE > run_dna.txt ; md5 phai trung. Ghi calc_out_v4.json + panel_v4.csv.
SUA so voi v2 (theo SKEPTIC_v2): (1) cau noi ISS: thuong/co tuc CP da ex ma so CP chua cap nhat -> S_pre x (1+r) (co ISS_FIX);
  co phieu quy: neu AIS (CP phat hanh) > BQ OShares da cong bo cung quy (sau moi su kien) 0,5-15% -> dung BQ (CP luu hanh), co TREASURY_FIX;
  (2) T_eff chi tren thang n>=11; (3) KHONG tien loc: ca 116 holding, loc do phu PIT theo thang bang VCSH me;
  (4) co con mong (ADV60 < 0,1 ty hoac <20 phien khop/60) + do nhay mong->so / mong 50%; (5) isinstance(nested_via, str).
Ung vien dai: xem PREREG_v3.md (khong doi) + PREREG_v4.md (sua F1-F5), khoa md5 truoc khi chay.

Dinh nghia (holding p, ngay cuoi thang D; chi du lieu da cong bo <= D):
  MV_x   = Price_x(D, CHUA dieu chinh, phien co KL>0 cuoi cung) x SoCP_x(D)
           SoCP: oshares_at PIT (neo AIS, ap ISS theo ngay ex) ; tu choi -> dong quy BQ da cong bo (co FIN_FALLBACK)
  STALE  = phien cuoi > 10 phien truoc D  HOAC  ADV60 (trung binh 60 phien, ngay khong khop = 0) = 0
           -> gia STALE KHONG tinh la gia thi truong: phan do de nguyen trong nhom 'theo so'. Ban 'v1' giu gia stale.
  E_x    = VCSH thuoc co dong ME = owners_equity - minority_interests (CDKT quy VCI) cua quy moi nhat cong bo <= D
           (ngay cong bo = BQ Release_Date cua quy; khong co -> cuoi quy + 90 ngay). Thieu VCI -> fallback co gan co.
  s_i    = loi ich theo BCTC nam (KBS update_date; tang 2 = tich 2 tang, ngay = max). PIT: dung khi ngay + 90 <= D.
           Che do 'fixed' (do nhay): bo cong PIT, ty le hien tai ap lui ca cua so (LOOK-AHEAD, chi doi chieu).
  Con long nhau: con j bi bo neu mot con niem yet i khac cua cung p nam >= 20% j (gia tri j da nam trong gia i).
  SOTP_p = sum_{i khong stale} s_i MV_i + (E_p - sum_{i khong stale} s_i E_i) ; DoPhu = sum s_i MV_i / SOTP ; CK = 1 - MV_p/SOTP
  Gia me STALE -> bo quan sat (p, D).
N = so HOLDING; bootstrap khoi: holding (co hoan lai) x khoi thoi gian 3 thang (circular) ; seed 20261124.
"""
import os, json, glob, hashlib, unicodedata
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); IN = os.path.join(HERE, 'inputs'); RAW = os.path.join(HERE, 'raw')
V1 = os.path.join(os.path.dirname(HERE), 'ck_holding_vn_20261123')
DATES = json.load(open(os.path.join(IN, 'dates.json')))
ST = pd.read_csv(os.path.join(IN, 'stakes_all.csv')); QUAL = pd.read_csv(os.path.join(IN, 'qualified_parents.csv')).parent.tolist()
PX = pd.read_csv(os.path.join(IN, 'prices.csv')); SH = pd.read_csv(os.path.join(IN, 'shares_pit.csv'))
BQF = pd.read_csv(os.path.join(IN, 'bq_fin.csv')); VB = pd.read_csv(os.path.join(IN, 'vci_bs_long.csv')); DV = pd.read_csv(os.path.join(IN, 'divs.csv'))
U0 = pd.read_csv(os.path.join(IN, 'universe_U0.csv'))
QEND = {'Q1': '-03-31', 'Q2': '-06-30', 'Q3': '-09-30', 'Q4': '-12-31'}
STALE_SESS = 10


def norm(s):
    s = unicodedata.normalize('NFD', str(s).lower()); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('đ', 'd')
    for w in ['cong ty co phan', 'cong ty tnhh mot thanh vien', 'cong ty tnhh mtv', 'cong ty tnhh', 'ctcp', 'tong cong ty', 'cong ty',
              'joint stock company', 'jsc', 'tap doan', 'mtv', '.', ',', '-', '(', ')']:
        s = s.replace(w, ' ')
    return ' '.join(s.split())


L = pd.read_csv(os.path.join(V1, 'raw', 'listing_vci_20261123.csv')); name2tk = {}
for n, s in zip(L.organ_name.map(norm), L.symbol): name2tk.setdefault(n, s)

# ---- ngay cong bo quy ----
BQF['rel'] = pd.to_datetime(BQF.rel)
REL = BQF.groupby(['ticker', 'quarter']).rel.min().to_dict()
VB['rel'] = [REL.get((t, q), pd.Timestamp(q[:4] + QEND[q[4:]]) + pd.Timedelta(days=90)) for t, q in zip(VB.ticker, VB.quarter)]
VB['rel_src'] = ['BQ' if (t, q) in REL else 'QEND+90' for t, q in zip(VB.ticker, VB.quarter)]
VB['eq_parent'] = VB.owners_equity - VB.minority_interests.fillna(0)
VB = VB[VB.owners_equity.notna() & (VB.owners_equity != 0)]
BQF['eq_tot'] = BQF.BVPS * BQF.OShares


def equity0(t, D):
    f = VB[(VB.ticker == t) & (VB.rel <= D)].sort_values('rel')
    if len(f): r = f.iloc[-1]; return float(r.eq_parent), r.quarter, 'VCI_parent', float(r.paid_in) / 1e4 if pd.notna(r.paid_in) else np.nan
    f = BQF[(BQF.ticker == t) & (BQF.rel <= D) & BQF.eq_tot.notna()].sort_values('rel')
    if len(f): r = f.iloc[-1]; return float(r.eq_tot), r.quarter, 'BQ_total_inclNCI', np.nan
    return np.nan, None, 'NONE', np.nan


PROCLOG = {}; STALELOG = {}


def _qidx(q):
    return int(q[:4]) * 4 + int(q[5]) - 1 if isinstance(q, str) and len(q) == 6 else None


def _bs_stale(q, ex):
    e = pd.Timestamp(ex); qi = _qidx(q)
    return qi is None or (e.year * 4 + (e.month - 1) // 3) - qi > 4


def ev_state(t, D, ev):
    """VCSH con tai D co chua tien thu cua ev khong: 'reflected' (CDKT da co) | 'added' (PROCEEDS_ADD) | 'none'."""
    E, q, src, pin = equity0(t, D)
    if np.isnan(E): return 'none'
    refl = (pin >= ev['S_post'] * 0.99) if pin == pin else (q is not None and _q_end(q) >= pd.Timestamp(ev['ex']))
    if refl: return 'reflected'
    if not CFG['proceeds'] or (CFG['stale_proc'] and _bs_stale(q, ev['ex'])): return 'none'
    return 'added'


def equity(t, D):
    """F1 (v4): cong tien thu PP/Rights/PUBL (total_value) khi CDKT dang dung chua phan anh (paid_in/1e4 < S_post*0,99; khong paid_in -> cuoi quy < ex)."""
    E, q, src, pin = equity0(t, D)
    if np.isnan(E) or not CFG['proceeds']: return E, q, src, pin
    add = 0.0
    for ev in DIL.get(t, []):
        if pd.Timestamp(ev['ex']) > D or not ev['tv'] > 0: continue
        if CFG['stale_proc'] and _bs_stale(q, ev['ex']):   # S3 (v5): BCTC con cu > 4 quy so voi quy ex -> khong cong tien thu
            STALELOG[(t, ev['ex'])] = dict(ticker=t, ex=ev['ex'], bs_q=q, tv_bn=ev['tv'] / 1e9); continue
        reflected = (pin == pin and pin >= ev['S_post'] * 0.99) if pin == pin else (q is not None and _q_end(q) >= pd.Timestamp(ev['ex']))
        if not reflected:
            add += ev['tv']; PROCLOG[(t, str(D.date()), ev['ex'])] = dict(ticker=t, date=str(D.date()), ex=ev['ex'], add_bn=ev['tv'] / 1e9, bs_q=q,
                                                                           paid_in_sh=pin if pin == pin else None, S_post=ev['S_post'])
    return E + add, q, src + ('+PROCEEDS_ADD' if add else ''), pin


PXi = PX.set_index(['ticker', 'date']); SHi = SH.set_index(['ticker', 'date'])
CE0 = pd.read_csv(os.path.join(IN, 'cap_events_v4.csv'))
# F2: khu dong trung (ma, ex, method, ratio, volume) TRUOC khi cong cung ngay ex; giu dong co listing_date
CE0['_hasl'] = CE0.listing_date.notna()
CE0 = CE0.sort_values(['ticker', 'exright_date', 'issue_method_code', '_hasl', 'id'], ascending=[True, True, True, False, True])
_DK = ['ticker', 'exright_date', 'issue_method_code', 'exercise_ratio', 'issue_volumn']
DEDUP = CE0[CE0.duplicated(_DK, keep='first')][_DK + ['id', 'listing_date']].copy()
CE = CE0.drop_duplicates(_DK, keep='first').drop(columns='_hasl').reset_index(drop=True)
ISSUE = ['PP', 'Rights', 'PUBL']
# ngay co cap volume am/duong cung method -> mo ho, khong dung (F1)
_neg = CE[CE.issue_method_code.isin(ISSUE) & (CE.issue_volumn < 0)][['ticker', 'exright_date']].drop_duplicates()
AMBIG = CE.merge(_neg, on=['ticker', 'exright_date'])[_DK].copy()
AMB_WIDE = set(zip(_neg.ticker, _neg.exright_date))
# S4 (v5): ban DUNG CHU PREREG_v4 F1 — chi (ma, ex) co CUNG method ca dong am lan duong
_ci = CE[CE.issue_method_code.isin(ISSUE)]
AMB_LETTER = {(t, e) for (t, e, m), g in _ci.groupby(['ticker', 'exright_date', 'issue_method_code']) if (g.issue_volumn < 0).any() and (g.issue_volumn > 0).any()}
_amb = AMB_WIDE
CFG = dict(iss='two', comb='sum', part='main', dilute=True, cap=True, proceeds=True, ambig=False, override=True,
           stale_proc=True, pgain=True, amb='wide', ovr5=True, ovr5_off=(), msr_s=None, posthoc=True)
EVCHK = []
THIN_ADV = 1e8; THIN_DAYS = 20


def _q_end(q):
    return pd.Timestamp(q[:4] + QEND[q[4:]]) if isinstance(q, str) and len(q) == 6 else pd.NaT


def build_shares():
    """so CP cuoi cung (t, D): nguon v2 -> TREASURY_FIX (F3i) -> su kien theo thu tu ex: Bonus/DIV (ISS_FIX, F3ii/iii) + PP/Rights/PUBL (CAP_FIX, F1).
    Tra SHFIX, SHLOG, DIL (su kien pha loang theo ma con)."""
    shfix = {}; log = []; dil = {}; EVCHK.clear()
    for t, g in SH.groupby('ticker'):
        g = g.sort_values('date'); cur = {}
        ev_t = CE[CE.ticker == t]
        for _, s0 in g.iterrows():
            sh, meth = (s0.live_value, s0.method) if pd.notna(s0.live_value) else (s0.fin_released, 'FIN_FALLBACK')
            if pd.isna(sh) or sh <= 0: continue
            # F3(i) co phieu quy: AIS dem CP PHAT HANH; BQ OShares = CP luu hanh. v4: chan neu co su kien ISS ex >= cuoi quy BQ (bao gom bang).
            if str(meth).startswith('AIS') and pd.notna(s0.fin_released) and s0.fin_released > 0:
                qe = _q_end(s0.fin_q); dev = sh / s0.fin_released - 1
                later = ev_t[(pd.to_datetime(ev_t.exright_date) >= qe) & (pd.to_datetime(ev_t.exright_date) <= pd.Timestamp(s0.date))] if qe == qe else ev_t.iloc[:0]
                if 0.005 < dev <= 0.15 and not len(later):
                    log.append(dict(ticker=t, date=s0.date, rule='TREASURY_FIX', before=float(sh), after=float(s0.fin_released), meth=meth,
                                    note=f"AIS {sh:,.0f} > BQ {s0.fin_q} {s0.fin_released:,.0f} (+{dev:.2%})"))
                    sh, meth = float(s0.fin_released), meth + '+TREASURY_FIX'
            cur[s0.date] = [float(sh), meth]
        ds = sorted(cur)
        exs = sorted(set(ev_t[ev_t.issue_method_code.isin(['Bonus', 'DIV'] + ISSUE)].exright_date))
        other = sorted(set(ev_t.exright_date))   # cua so ISS hai chieu ket thuc o su kien CP KE TIEP bat ky (Khac PREREG: v3 ghi 'khac loai'; su kien cung loai sau do tu sua lai)
        for E in exs:
            e = ev_t[ev_t.exright_date == E]
            b = e[e.issue_method_code.isin(['Bonus', 'DIV'])]; rr = b.exercise_ratio.fillna(0).astype(float)
            r = float(rr.sum()) if CFG['comb'] == 'sum' else float(np.prod(1 + rr) - 1)
            iss = e[e.issue_method_code.isin(ISSUE) & (e.issue_volumn > 0)]
            use_iss = len(iss) and (t, E) not in (AMB_WIDE if CFG['amb'] == 'wide' else AMB_LETTER)
            vol = float(iss.issue_volumn.sum()) if use_iss else 0.0
            tv = float(iss.total_value.fillna(0).clip(lower=0).sum()) if use_iss else 0.0
            pre = [d for d in ds if d < E]
            if not pre and vol > 0: EVCHK.append(dict(ticker=t, ex=E, status='no_pre_shares', vol=vol, methods='+'.join(sorted(set(iss.issue_method_code)))))
            if not pre or not (r > 0 or vol > 0): continue
            Spre = cur[pre[-1]][0]; Sb = Spre * (1 + r); exp = Sb + vol
            if vol > 0:
                # KIEM KHOP ty le/khoi luong (them sau lan chay thu 1 — xem 'Khac PREREG'): goc theo ty le = vol / ratio.
                #  pre  : S_pre ~ goc (+-3%)            -> ap nhu PREREG (pha loang, CAP_FIX, tien thu)
                #  post : S_pre ~ goc(1+r_b) + vol        -> chuoi so CP da neo lui bang so SAU phat hanh: khong CAP_FIX, S_post = S_pre, f = (S_pre-vol)/S_pre
                #  ambig: ratio = 0 hoac khong khop ca hai -> KHONG ap (main), liet ke; do nhay 'ambig_applied' ap nhu pre
                rat = float(iss.exercise_ratio.fillna(0).sum()); base = vol / rat if rat > 0 else np.nan
                if base == base and abs(Spre / base - 1) <= 0.03: stt = 'pre'
                elif base == base and abs(Spre / (base * (1 + r) + vol) - 1) <= 0.03: stt = 'post'
                else: stt = 'ambig'
                if stt == 'post': Sb, exp = Spre - vol, Spre
                lst = iss.listing_date.dropna()
                rec = dict(ex=E, f=Sb / exp, S_pre=Spre, S_post=exp, vol=vol, tv=tv, r_b=r, ratio=rat, base_by_ratio=base, status=stt,
                           listing=str(lst.min()) if len(lst) else None, methods='+'.join(sorted(set(iss.issue_method_code))))
                EVCHK.append(dict(ticker=t, **rec))
                if stt == 'ambig' and not CFG['ambig']:
                    vol = 0.0; exp = Sb
                    if not r > 0: continue
                else:
                    dil.setdefault(t, []).append(rec)
            nxt = [x for x in other if x > E]; wend = nxt[0] if nxt else '9999-12-31'
            tag = '+'.join(sorted(e.issue_method_code))
            for d in [d for d in ds if d >= E]:
                v = cur[d][0]
                if r > 0 and CFG['iss'] == 'two' and d < wend:
                    fix = abs(v / exp - 1) > 0.02
                elif r > 0 and CFG['iss'] == 'one':   # v3: mot chieu, chi khi chua cap nhat
                    fix = v < exp * 0.98 and v <= Spre * (1 + r / 2) + vol
                else:
                    fix = CFG['cap'] and vol > 0 and v < exp * 0.98
                if r == 0 and not CFG['cap']: fix = False
                if fix:
                    rule = 'ISS_FIX' if r > 0 else 'CAP_FIX'
                    log.append(dict(ticker=t, date=d, rule=rule, before=v, after=exp, meth=cur[d][1],
                                    note=f"{tag} r_b {r:.4f} vol {vol:,.0f} ex {E}; S_pre {pre[-1]} {Spre:,.0f}" + (' (gap+)' if v > exp else '')))
                    cur[d] = [exp, cur[d][1] + '+' + rule]
        for d, v in cur.items(): shfix[(t, d)] = v
    return shfix, pd.DataFrame(log), dil


# F1: doi chieu KBS — ban ghi co dong lon cua CHINH ME tai con, update_date >= ex
import functools


OVR = pd.read_csv(os.path.join(IN, 'participation_override.csv'))   # them sau lan chay thu 2 (Khac PREREG): bang chung ngoai KBS ve viec me tham gia


@functools.lru_cache(maxsize=None)
def _kbs_post(parent, sub, ex, ovr, posthoc=True):
    if ovr:
        o = OVR[(OVR.parent == parent) & (OVR['sub'] == sub) & (OVR.ex == ex)]
        if not posthoc: o = o[~o.source.str.startswith('POSTHOC')]
        if len(o): return float(o.pct.iloc[0]) / 100, str(o.date.iloc[0]), 'OVERRIDE'
    for dd in ['kbs_sh_v4', 'kbs_sh']:
        f = os.path.join(RAW, dd, sub + '.json')
        if not os.path.exists(f): continue
        for r in json.load(open(f)):
            if name2tk.get(norm(r.get('name'))) == parent and str(r.get('update_date'))[:10] >= ex:
                return float(r.get('ownership_percentage') or 0) / 100, str(r.get('update_date'))[:10], dd
    return None


def kbs_post(parent, sub, ex):
    return _kbs_post(parent, sub, ex, bool(CFG.get('override', True)), bool(CFG.get('posthoc', True)))


DILLOG = {}


def stake_eff(parent, sub, s, stake_date, D):
    """Tra (s, tag, applied): applied = [(ev, s_truoc, s_sau)] cho su kien ap MAC DINH 'me khong tham gia' (dung cho S2 lai pha loang)."""
    applied = []
    if not CFG['dilute'] or CFG['part'] == 'full': return s, '', applied
    tag = []
    for ev in DIL.get(sub, []):
        if ev['ex'] <= stake_date or pd.Timestamp(ev['ex']) > D: continue
        kp = kbs_post(parent, sub, ev['ex'])
        if kp is not None:
            sw = (pd.Timestamp(kp[1]) if kp[2] == 'OVERRIDE' else pd.Timestamp(ev['listing']) if (CFG['part'] == 'main' and ev['listing']) else pd.Timestamp(kp[1]) + pd.Timedelta(days=90))
            if D >= sw:
                s = kp[0]; tag.append(f"KBS{kp[1]}"); DILLOG[(parent, sub, ev['ex'], 'kbs')] = dict(parent=parent, sub=sub, ex=ev['ex'], methods=ev['methods'],
                    f=ev['f'], s_after_default=None, kbs_pct=kp[0], kbs_date=kp[1], switch=str(sw.date()), src=kp[2]); continue
        s0 = s; s = s * ev['f']; tag.append(f"dil{ev['ex']}"); applied.append((ev, s0, s))
        DILLOG.setdefault((parent, sub, ev['ex'], 'dil'), dict(parent=parent, sub=sub, ex=ev['ex'], methods=ev['methods'], f=ev['f'], s_before=s0,
                                                               s_after_default=s, kbs_pct=kp[0] if kp else None, kbs_date=kp[1] if kp else None,
                                                               S_pre=ev['S_pre'], S_post=ev['S_post'], vol=ev['vol'], tv_bn=ev['tv'] / 1e9))
    return s, ','.join(tag), applied


def set_cfg(**kw):
    global SHFIX, SHLOG, DIL
    CFG.update(kw); SHFIX, SHLOG, DIL = build_shares(); EQC.clear()


EQC = {}; PGLOG = {}
SHFIX, SHLOG, DIL = build_shares()


def mv(t, d, stale_ok=False):
    if (t, d) not in PXi.index or (t, d) not in SHFIX: return None
    p = PXi.loc[(t, d)]; sh, meth = SHFIX[(t, d)]
    stale = (p.sessions_since_trade > STALE_SESS) or (p.adv60_mean <= 0)
    return dict(mv=float(p.price * sh), stale=bool(stale), liq=bool(p.in_universe), meth=meth, shares=float(sh), px_date=p.px_date,
                thin=bool((p.days_traded60 < THIN_DAYS) or (p.adv60_mean < THIN_ADV)), adv60=float(p.adv60_mean))


# ---- con long nhau: j bi bo neu i (con niem yet khac cua p) nam >= 20% j ----
def holds(i, j):
    f = os.path.join(RAW, 'kbs_subs', i + '.json')
    if os.path.exists(f) and any(name2tk.get(norm(r.get('name'))) == j and float(r.get('ownership_percent') or 0) >= 20 for r in json.load(open(f))): return True
    f = os.path.join(RAW, 'kbs_sh', j + '.json')
    return os.path.exists(f) and any(name2tk.get(norm(r.get('name'))) == i and float(r.get('ownership_percentage') or 0) >= 20 for r in json.load(open(f)))


def _nest(T):
    out = []
    for p, g in T.groupby('parent'):
        subs = sorted(set(g['sub']))
        for j in subs:
            by = [i for i in subs if i != j and holds(i, j)]
            if by: out.append((p, j, by[0]))
    nm = {(p, j): i for p, j, i in out}
    T['nested_via'] = [nm.get((p, j), '') for p, j in zip(T.parent, T['sub'])]
    return T, out


ST4 = ST[ST.parent.isin(QUAL)].copy(); ST4['valid_from'] = pd.to_datetime(ST4.stake_date) + pd.Timedelta(days=90); ST4['ovr5'] = False
ST4, nested_v4 = _nest(ST4)
# S1 (v5): ty le so huu co ngay — thay cap (me, con) trong stakes_all bang dong override (nhieu dong/cap theo thoi gian)
OV5 = pd.read_csv(os.path.join(IN, 'stakes_override_v5.csv'), dtype={'valid_from': str})
_ovp = set(zip(OV5.parent, OV5['sub']))
_add = OV5[OV5.action == 'set'].copy()
_add['valid_from'] = [pd.Timestamp(v) if isinstance(v, str) and v else pd.Timestamp(sd) + pd.Timedelta(days=90) for v, sd in zip(_add.valid_from, _add.stake_date)]
_add = _add.assign(layer=1, via='', type='v5_override', name=_add.note.str[:60], stake_vci=np.nan, ovr5=True)
ST5 = pd.concat([ST4[[(p, j) not in _ovp for p, j in zip(ST4.parent, ST4['sub'])]].drop(columns='nested_via'),
                 _add[[c for c in ST4.columns if c != 'nested_via']]], ignore_index=True)
ST5 = ST5[ST5.parent.isin(QUAL)].sort_values(['parent', 'sub', 'valid_from']).reset_index(drop=True)
ST5, nested = _nest(ST5)


def rows_for(p, regime, D):
    """Dong ty le dung cho me p tai D: v5 (override) tru khi CFG tat; moi (p, con) lay dong valid_from <= D moi nhat (pit) / dong cuoi (fixed)."""
    use5 = CFG['ovr5'] and p not in CFG['ovr5_off']
    T = (ST5 if use5 else ST4); T = T[T.parent == p]
    if use5 and not CFG['posthoc']: T = T[~T.src.astype(str).str.startswith('POSTHOC')]
    out = []
    for j, g in T.groupby('sub', sort=True):
        g = g.sort_values('valid_from')
        if regime == 'pit': g = g[g.valid_from <= D]
        if not len(g): continue
        r = g.iloc[-1].copy()
        if use5 and p == 'MSN' and j == 'MSR' and CFG['msr_s'] is not None:
            if CFG['msr_s'] <= 0: continue
            r['stake'] = CFG['msr_s']
        out.append(r)
    return out


# ---- panel (p, D, regime pit|fixed, stale rule main|v1, thin rule market|book|half) ----


def equity_c(t, D):
    k = (t, D)
    if k not in EQC: EQC[k] = equity(t, D)
    return EQC[k]


def run(regime, stale_rule, thin_rule='market'):
    rows = []
    for p in QUAL:
        for d in DATES:
            D = pd.Timestamp(d); m = mv(p, d)
            Ep, qp, srcp, _ = equity_c(p, D)
            if m is None or np.isnan(Ep): continue
            lmv = lbook = lmv_ctrl = lmv_liq = nci_est = stale_book = thin_mv = 0.0; n_used = n_stale = n_fb = n_thin = 0; subs_used = []
            pgain = 0.0
            for r in rows_for(p, regime, D):
                if isinstance(r.nested_via, str) and r.nested_via: continue
                s, dtag, appl = stake_eff(p, r['sub'], r.stake / 100.0, r.stake_date, D); mi = mv(r['sub'], d); Ei, qi, srci, _ = equity_c(r['sub'], D)
                if mi is None or np.isnan(Ei): continue
                # S2 (v5): lai pha loang cua me khi KHONG tham gia, toi khi BCTC me phan anh (cuoi quy BCTC me < ex)
                if CFG['pgain']:
                    for ev, sb, sa in appl:
                        if not ev['tv'] > 0 or (qp is not None and _q_end(qp) >= pd.Timestamp(ev['ex'])) or ev_state(r['sub'], D, ev) == 'none': continue
                        g_ = sa * Ei - sb * (Ei - ev['tv']); pgain += g_
                        PGLOG[(p, r['sub'], ev['ex'], d)] = dict(parent=p, sub=r['sub'], ex=ev['ex'], date=d, s_before=sb, s_after=sa, E_sub_bn=Ei / 1e9,
                                                                tv_bn=ev['tv'] / 1e9, gain_bn=g_ / 1e9, parent_bs_q=qp)
                if s >= 0.5: nci_est += (1 - s) * Ei
                if mi['stale'] and stale_rule == 'main': n_stale += 1; stale_book += s * Ei; continue
                w = 1.0
                if mi['thin']:
                    n_thin += 1; thin_mv += s * mi['mv']
                    w = {'market': 1.0, 'book': 0.0, 'half': 0.5}[thin_rule]
                n_used += 1; n_fb += not str(srci).startswith('VCI_parent')
                lmv += w * s * mi['mv']; lbook += w * s * Ei
                if s >= 0.5: lmv_ctrl += w * s * mi['mv']
                if mi['liq']: lmv_liq += w * s * mi['mv']
                subs_used.append(f"{r['sub']}:{s:.3f}" + ('t' if mi['thin'] else '') + (f"[{dtag}]" if dtag else ''))
            eq_src = srcp; Ep = Ep + pgain
            if pgain: eq_src += '+PARENT_DIL_GAIN'
            if srcp.startswith('BQ_total_inclNCI'): Ep -= nci_est; eq_src = srcp.replace('BQ_total_inclNCI', 'APPROX_BQtot_minus_listedNCI')
            sotp = lmv + (Ep - lbook)
            if sotp <= 0: continue
            rows.append(dict(parent=p, date=d, mv_p=m['mv'] / 1e9, parent_stale=m['stale'], parent_liq=m['liq'], parent_sh_meth=m['meth'],
                             eq_p=Ep / 1e9, eq_q=qp, parent_dil_gain=pgain / 1e9, eq_src=eq_src, listed_mv=lmv / 1e9, listed_book=lbook / 1e9, stale_book=stale_book / 1e9,
                             resid_book=(Ep - lbook) / 1e9, sotp=sotp / 1e9, coverage=lmv / sotp, cov_liq=lmv_liq / sotp,
                             thin_share=thin_mv / lmv if lmv > 0 else np.nan,
                             ctrl_share=lmv_ctrl / lmv if lmv > 0 else np.nan,
                             ck=1 - m['mv'] / sotp, n_subs=n_used, n_stale=n_stale, n_thin=n_thin, n_sub_eq_fallback=n_fb, subs=' '.join(subs_used)))
    R = pd.DataFrame(rows)
    return R[~R.parent_stale.astype(bool)].reset_index(drop=True) if len(R) else R


KEYS = [('pit', 'main', 'market'), ('pit', 'main', 'book'), ('pit', 'main', 'half'), ('pit', 'v1', 'market'),
        ('fixed', 'main', 'market'), ('fixed', 'v1', 'market')]
PAN = {k: run(*k) for k in KEYS}
MAIN = PAN[('pit', 'main', 'market')]

# ---- co tuc tien con -> me (12 thang truoc D) / gia tri niem yet ; tang chong ----
DV['ex'] = pd.to_datetime(DV.exright_date)
def div_in_yield(p, d):
    D = pd.Timestamp(d); tot = 0.0
    for r in rows_for(p, 'pit', D):
        if isinstance(r.nested_via, str) and r.nested_via: continue
        m = mv(r['sub'], d, True)
        if m is None: continue
        dps = DV[(DV.ticker == r['sub']) & (DV.ex > D - pd.Timedelta(days=365)) & (DV.ex <= D)].value_per_share.sum()
        tot += r.stake / 100 * m['shares'] * dps
    return tot / 1e9


ALLST = pd.read_csv(os.path.join(IN, 'stakes_all.csv'))


def stacked(p):
    f = os.path.join(RAW, 'kbs_sh', p + '.json'); up = []
    if os.path.exists(f): up += [(name2tk.get(norm(r.get('name'))), r.get('ownership_percentage')) for r in json.load(open(f))
                                 if name2tk.get(norm(r.get('name'))) and float(r.get('ownership_percentage') or 0) >= 50]
    g = ALLST[(ALLST['sub'] == p) & (ALLST.stake >= 50)]
    up += list(zip(g.parent, g.stake))
    return sorted(set((a, float(s)) for a, s in up))


def major_holders(p):
    """Tong % co dong lon >=5% cua me (KBS shareholders); None neu khong co du lieu."""
    f = os.path.join(RAW, 'kbs_sh', p + '.json')
    if not os.path.exists(f): return None
    x = [float(r.get('ownership_percentage') or 0) for r in json.load(open(f))]
    return float(sum(v for v in x if v >= 5)) if x else None


def hold_summary(R, cov_min=0.60, min_months=3):
    K = R[R.coverage >= cov_min]
    H = K.groupby('parent').agg(ck=('ck', 'median'), ck_mean=('ck', 'mean'), ck_min=('ck', 'min'), ck_max=('ck', 'max'), months=('ck', 'count'),
                                coverage=('coverage', 'median'), cov_liq=('cov_liq', 'median'), ctrl_share=('ctrl_share', 'median'),
                                thin_share=('thin_share', 'median'), resid_book=('resid_book', 'median'),
                                eq_src=('eq_src', 'last'), sub_fb=('n_sub_eq_fallback', 'max'), first=('date', 'min'), last=('date', 'max')).reset_index()
    return H[H.months >= min_months].reset_index(drop=True)


def stats(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    if not len(x): return dict(N=0)
    return dict(N=int(len(x)), median=float(np.median(x)), q25=float(np.percentile(x, 25)), q75=float(np.percentile(x, 75)),
                min=float(x.min()), max=float(x.max()))


def loo(x):
    x = list(map(float, x))
    if len(x) < 3: return {}
    v = [float(np.median(x[:i] + x[i + 1:])) for i in range(len(x))]
    return dict(loo_min=min(v), loo_max=max(v))


def monthly(R, parents, cov_min=0.60, nmin=1):
    K = R[(R.coverage >= cov_min) & R.parent.isin(list(parents))]
    g = K.groupby('date').ck.agg(['median', 'count']); g.columns = ['median', 'n']
    return g[g.n >= nmin]


def block_boot(R, H, B=5000, blk=3, seed=20261124, cov_min=0.60):
    rng = np.random.default_rng(seed); K = R[(R.coverage >= cov_min) & R.parent.isin(list(H.parent))]
    ser = [K[K.parent == p].sort_values('date').ck.to_numpy() for p in H.parent]
    out = np.empty(B)
    for b in range(B):
        hs = rng.integers(0, len(ser), len(ser)); vals = []
        for h in hs:
            x = ser[h]; T = len(x); nb = int(np.ceil(T / blk)); st = rng.integers(0, T, nb)
            idx = np.concatenate([(s0 + np.arange(blk)) % T for s0 in st])[:T]; vals.append(np.median(x[idx]))
        out[b] = np.median(vals)
    return dict(boot_p5=float(np.percentile(out, 5)), boot_p50=float(np.percentile(out, 50)), boot_p95=float(np.percentile(out, 95)), B=B, block_months=blk)


def enrich(H):
    H = H.copy()
    H['div_in_ann_yield'] = [float(np.mean([div_in_yield(p, d) for d in MAIN[MAIN.parent == p].date]) /
                                   max(MAIN[MAIN.parent == p].listed_mv.mean(), 1e-9)) for p in H.parent]
    H['control'] = H.ctrl_share >= 0.5
    H['stacked_above'] = [';'.join(f"{a}:{s:.1f}" for a, s in stacked(p)) for p in H.parent]
    H['eq_exact'] = H.eq_src.str.startswith('VCI_parent') & (H.sub_fb == 0)
    H['parent_in_pit'] = H.parent.map(dict(zip(U0.ticker, U0.in_pit_any_monthend))).fillna(False).astype(bool)
    H['major_holders_pct'] = [major_holders(p) for p in H.parent]
    H['R1_freefloat'] = [v is not None and v >= 85 for v in H.major_holders_pct]
    H['R2_neg_resid_book'] = H.resid_book < 0
    return H


H = enrich(hold_summary(MAIN))
res = {'N_main': int(len(H)), 'all': {**stats(H.ck), **block_boot(MAIN, H), **loo(H.ck)}}

# ---- (d) duong theo thang + T_eff chi tren thang n>=11 ----
lines = {}
for k, R in PAN.items():
    K = R[R.coverage >= 0.60]
    g = K.groupby('date').ck.agg(['median', 'count', lambda s: s.quantile(.25), lambda s: s.quantile(.75)])
    g.columns = ['median', 'n', 'q25', 'q75']; lines['_'.join(k)] = g.round(4).reset_index().to_dict('records')
ml_all = pd.DataFrame(lines['pit_main_market']); ml = ml_all[ml_all.n >= 11].reset_index(drop=True)
rho = float(pd.Series(ml['median'].to_numpy()).autocorr(1)) if len(ml) > 3 else np.nan
T = len(ml)
res['time'] = dict(T_months_n_ge11=T, months=list(ml.date), lag1_autocorr=rho,
                   T_eff=float(T * (1 - rho) / (1 + rho)) if rho == rho and rho < 1 else np.nan,
                   v2_style_all_months=dict(T=len(ml_all), rho=float(pd.Series(ml_all['median'].to_numpy()).autocorr(1)) if len(ml_all) > 3 else np.nan))

# ---- do nhay ----
sens = {}
for c in [0.5, 0.6, 0.7]: sens[f'cov{int(c*100)}'] = stats(hold_summary(MAIN, c).ck)
sens['v1_stale_kept_pit'] = stats(hold_summary(PAN[('pit', 'v1', 'market')]).ck)
sens['thin_to_book'] = stats(hold_summary(PAN[('pit', 'main', 'book')]).ck)
sens['thin_half'] = stats(hold_summary(PAN[('pit', 'main', 'half')]).ck)
sens['fixed_stake_main'] = stats(hold_summary(PAN[('fixed', 'main', 'market')]).ck)
sens['fixed_stake_v1'] = stats(hold_summary(PAN[('fixed', 'v1', 'market')]).ck)
sens['eq_exact_only'] = stats(H[H.eq_exact].ck)
sens['cov_liquid_ge60'] = stats(H[H.cov_liq >= 0.6].ck)
sens['parent_in_pit_only'] = stats(H[H.parent_in_pit].ck)
sens['ex_VIC'] = stats(H[H.parent != 'VIC'].ck)
sens['ex_VIC_MVN'] = stats(H[~H.parent.isin(['VIC', 'MVN'])].ck)
sens['ex_thin_dominated(thin_share>=0.5)'] = stats(H[~(H.thin_share >= 0.5)].ck)

V2N = ['APH', 'CMX', 'GEX', 'IPA', 'LHC', 'MSN', 'MVN', 'OGC', 'PAN', 'SNZ', 'VIC', 'VSC']
BANNED = ['PC1', 'VVS', 'KSF', 'NKG', 'HSG', 'HVN', 'VJC', 'NVL', 'GEG', 'SBA', 'DMC', 'IMP', 'TRA', 'TOS', 'VTP', 'BAF']   # fleet BANNED (KB)
sens['v2_sample_12_v3_rules'] = stats(H[H.parent.isin(V2N)].ck)
sens['ex_banned(KSF)'] = stats(H[~H.parent.isin(BANNED)].ck)
mv2 = monthly(MAIN, V2N, nmin=11)
sens['v2_sample_monthly_n_ge11'] = mv2.round(4).reset_index().to_dict('records')
# POST-HOC (khong dung de chon dai): chi R1, de thay R2 bat ca holding no rong o cap me
Hb1 = H[~H.R1_freefloat]
sens['POSTHOC_b_R1_only'] = {**stats(Hb1.ck), 'excluded': sorted(set(H.parent) - set(Hb1.parent))}
sens['POSTHOC_b_R1_plus_VIC'] = {**stats(Hb1[Hb1.parent != 'VIC'].ck)}

# ---- PHAN 2: ung vien dai (theo PREREG_v3.md) ----
cand = {}
# (a) luoi dac ta PIT: cov {50,60,70} x VIC {co,khong} x mong {gia,so}
grid = []
for c in [0.5, 0.6, 0.7]:
    for vic in [True, False]:
        for th in ['market', 'book']:
            Hg = hold_summary(PAN[('pit', 'main', th)], c)
            if not vic: Hg = Hg[Hg.parent != 'VIC']
            grid.append(dict(cov=c, with_VIC=vic, thin=th, N=int(len(Hg)), median=float(np.median(Hg.ck)) if len(Hg) else np.nan))
G = pd.DataFrame(grid)
cand['a_spec_grid'] = dict(low=float(G['median'].min()), mid=float(res['all']['median']), high=float(G['median'].max()),
                           N_range=[int(G.N.min()), int(G.N.max())], **loo(H.ck), what='bat dinh TRUNG TAM qua dac ta (PIT)')
# (b) loai cau truc R1/R2
Hb = H[~(H.R1_freefloat | H.R2_neg_resid_book)]
mb = monthly(MAIN, Hb.parent, nmin=5)
cand['b_struct_excl_IQR'] = dict(low=float(np.percentile(Hb.ck, 25)), mid=float(np.median(Hb.ck)), high=float(np.percentile(Hb.ck, 75)),
                                 N=int(len(Hb)), excluded=sorted(set(H.parent) - set(Hb.parent)), **loo(Hb.ck),
                                 center_monthly_min=float(mb['median'].min()) if len(mb) else np.nan,
                                 center_monthly_max=float(mb['median'].max()) if len(mb) else np.nan,
                                 what='PHAN TAN lien-holding (mot holding bat ky), sau loai cau truc')
cand['b_struct_excl_center'] = stats(Hb.ck)
# (c) co dieu kien giong HHS
t1 = float(np.percentile(H.div_in_ann_yield, 100 / 3)) if len(H) else np.nan
condsets = {'c1_control_lowdiv(<1%)': H[H.control & (H.div_in_ann_yield < 0.01)],
            'c2_lowest_div_tercile': H[H.div_in_ann_yield <= t1],
            'c3_control': H[H.control],
            'c3b_control_struct_excl': Hb[Hb.control]}
for k, Hc in condsets.items():
    mc = monthly(MAIN, Hc.parent, nmin=3)
    cand[k] = dict(N=int(len(Hc)), parents=sorted(Hc.parent), **(dict(low=float(np.percentile(Hc.ck, 25)), mid=float(np.median(Hc.ck)),
                   high=float(np.percentile(Hc.ck, 75))) if len(Hc) else {}), **loo(Hc.ck), enough=bool(len(Hc) >= 8),
                   center_monthly_min=float(mc['median'].min()) if len(mc) else np.nan, center_monthly_max=float(mc['median'].max()) if len(mc) else np.nan)
cand['c2_tercile_cut'] = t1
# (d) theo thoi gian (thang n>=11)
cand['d_monthly_n_ge11'] = dict(low=float(ml['median'].min()) if T else np.nan, mid=float(ml['median'].median()) if T else np.nan,
                                high=float(ml['median'].max()) if T else np.nan, q25=float(ml['median'].quantile(.25)) if T else np.nan,
                                q75=float(ml['median'].quantile(.75)) if T else np.nan, T=T, n_range=[int(ml.n.min()), int(ml.n.max())] if T else [],
                                what='trung tam troi theo thoi gian (1 che do)')
# loo theo thang cho (d): bo tung holding, trung vi duong thang
dl = []
for p in H.parent:
    m2 = monthly(MAIN, [q for q in H.parent if q != p], nmin=11)   # F3(v): n>=11 nhu PREREG
    dl.append((p, float(m2['median'].min()), float(m2['median'].max())))
cand['d_loo'] = dict(min_low=min(x[1] for x in dl), max_low=max(x[1] for x in dl), min_high=min(x[2] for x in dl), max_high=max(x[2] for x in dl))
for k, v in cand.items():
    if isinstance(v, dict) and 'low' in v and 'high' in v: v['width_pp'] = float((v['high'] - v['low']) * 100)
# chon theo PREREG C
# F3(iv): (c) DAU TIEN theo thu tu c1, c2, c3 dat N>=8 thay (a) — dung chu PREREG v3 §C2. Bao kem hull (a)u(d).
def hull(A, src_name):
    Dd = cand['d_monthly_n_ge11']; lo = min(A['low'], Dd['low']); hi = max(A['high'], Dd['high'])
    loo_ok = ('loo_min' in res['all']) and lo <= res['all']['loo_min'] and res['all']['loo_max'] <= hi
    w = (hi - lo) * 100
    return dict(source=src_name, low=lo, mid=float(res['all']['median']), high=hi, width_pp=w, meaningful=bool(w <= 20 and loo_ok), loo_inside=bool(loo_ok),
                zero_position=('duoi dai' if 0 < lo else 'tren dai' if 0 > hi else f"trong dai, phan vi {(0 - lo) / (hi - lo):.2f}"),
                zero_pct=float((0 - lo) / (hi - lo)) if hi > lo else None)
ck = next((k for k in ['c1_control_lowdiv(<1%)', 'c2_lowest_div_tercile', 'c3_control'] if cand[k]['enough']), None)
choice = hull(cand[ck], ck + '+d') if ck else hull(cand['a_spec_grid'], 'a+d')
choice_ad = hull(cand['a_spec_grid'], 'a+d')
choice['c_used'] = ck
# F5: trung tam la KHOANG
Hk = H[H.parent != 'KSF']; Hkc = H[~H.parent.isin(['KSF', 'CMX'])]
bb = block_boot(MAIN, H)
def _bq(R, H_, qs=(5, 25, 75, 95), B=5000, blk=3, seed=20261124):
    rng = np.random.default_rng(seed); K = R[(R.coverage >= 0.60) & R.parent.isin(list(H_.parent))]
    ser = [K[K.parent == p].sort_values('date').ck.to_numpy() for p in H_.parent]; out = np.empty(B)
    for b in range(B):
        hs = rng.integers(0, len(ser), len(ser)); vals = []
        for h in hs:
            x = ser[h]; T_ = len(x); nb = int(np.ceil(T_ / blk)); st = rng.integers(0, T_, nb)
            vals.append(np.median(x[np.concatenate([(s0 + np.arange(blk)) % T_ for s0 in st])[:T_]]))
        out[b] = np.median(vals)
    return {f'p{q}': float(np.percentile(out, q)) for q in qs}
center = dict(median_N=float(np.median(H.ck)), N=int(len(H)), **loo(H.ck), median_exKSF=float(np.median(Hk.ck)), N_exKSF=int(len(Hk)),
              median_exKSF_CMX=float(np.median(Hkc.ck)), N_exKSF_CMX=int(len(Hkc)), boot=_bq(MAIN, H))
center['interval_low'] = min(center['median_N'], center['loo_min'], center['median_exKSF'], center['median_exKSF_CMX'])
center['interval_high'] = max(center['median_N'], center['loo_max'], center['median_exKSF'], center['median_exKSF_CMX'])
srt = sorted(H.ck); center['middle_pair'] = [float(srt[len(srt) // 2 - 1]), float(srt[len(srt) // 2]), float(srt[len(srt) // 2 + 1])] if len(srt) >= 3 else []
# PREREG_v4 §C: moc de xuat HHS
hhs = dict(base=0.0, center_high=center['interval_high'], current_month=float(ml['median'].iloc[-1]) if T else np.nan, current_date=ml.date.iloc[-1] if T else None,
           dispersion_q75=float(np.percentile(H.ck, 75)), dispersion_q25=float(np.percentile(H.ck, 25)),
           R1R2_parents=sorted(H[H.R1_freefloat | H.R2_neg_resid_book].parent))

# ---- bien the de tach tac dong tung sua (chi dac ta chinh pit/main/market) ----
def quick(R):
    Hq = hold_summary(R); mlq = monthly(R, Hq.parent, nmin=11)
    return dict(N=int(len(Hq)), median=float(np.median(Hq.ck)) if len(Hq) else np.nan, parents=sorted(Hq.parent),
                line=[[str(i), float(v)] for i, v in mlq['median'].round(4).items()],
                d_low=float(mlq['median'].min()) if len(mlq) else np.nan, d_high=float(mlq['median'].max()) if len(mlq) else np.nan,
                last=float(mlq['median'].iloc[-1]) if len(mlq) else np.nan,
                ck_by_parent={p: float(v) for p, v in Hq.set_index('parent').ck.round(4).items()},
                MSN_last=float(R[(R.parent == 'MSN') & (R.date == DATES[-1])].ck.iloc[0]) if len(R[(R.parent == 'MSN') & (R.date == DATES[-1])]) else None,
                MSN_months=int(len(R[(R.parent == 'MSN') & (R.coverage >= 0.6)])))
_main_logs = (SHLOG.copy(), dict(DILLOG), dict(PROCLOG), dict(PGLOG), dict(STALELOG)); EVCHK_MAIN = pd.DataFrame(list(EVCHK))
VAR = {'v5_main': quick(MAIN)}
BASE5 = dict(iss='two', comb='sum', part='main', dilute=True, cap=True, proceeds=True, ambig=False, override=True,
             stale_proc=True, pgain=True, amb='wide', ovr5=True, ovr5_off=(), msr_s=None, posthoc=True)
V5LIST = [('CONTROL_v4(S1,S2,S3 off)', dict(ovr5=False, pgain=False, stale_proc=False)),
          ('S1_off(stakes v4)', dict(ovr5=False)), ('S1_MSN_as_v4', dict(ovr5_off=('MSN',))), ('S1_VSC_VGR_as_v4', dict(ovr5_off=('VSC',))),
          ('S1_PAN_FMC_as_v4', dict(ovr5_off=('PAN',))),
          ('MSR_s0(strict_KBS+90)', dict(msr_s=0)), ('MSR_s25', dict(msr_s=25.0)), ('MSR_s43.7', dict(msr_s=43.7)), ('MSR_s94.9(econ_incl_pref)', dict(msr_s=94.9)),
          ('S2_parent_gain_off', dict(pgain=False)), ('POSTHOC_MCH_participation_off', dict(posthoc=False)), ('S3_stale_proceeds_kept(v4)', dict(stale_proc=False)), ('S4_ambig_letter_PREREGv4', dict(amb='letter'))]
for name, kw in [('no_F1(dilute,cap,proceeds off)', dict(dilute=False, cap=False, proceeds=False)),
                 ('F1_dilute_only_off', dict(dilute=False)), ('F1_proceeds_off', dict(proceeds=False)), ('F1_cap_off', dict(cap=False)),
                 ('F1_part_strict(update+90)', dict(part='strict')), ('F1_part_full(no dilution)', dict(part='full')),
                 ('F1_ambig_applied', dict(ambig=True)), ('F1_no_override(LBM default)', dict(override=False)), ('F3iii_iss_one_way(v3)', dict(iss='one')), ('F3ii_prod(1+r)', dict(comb='prod'))]:
    base = dict(BASE5); base.update(kw); set_cfg(**base)
    VAR[name] = quick(run('pit', 'main', 'market'))
for name, kw in V5LIST:
    base = dict(BASE5); base.update(kw); set_cfg(**base)
    VAR[name] = quick(run('pit', 'main', 'market'))
# MSN rieng: duong thang chinh vs MSN-nhu-v4 (bao truoc/sau)
set_cfg(**dict(BASE5, ovr5_off=('MSN',))); _Rm4 = run('pit', 'main', 'market')
set_cfg(**BASE5)
MSN_CMP = MAIN[MAIN.parent == 'MSN'][['date', 'coverage', 'ck', 'eq_p', 'listed_mv', 'listed_book', 'sotp', 'subs']].merge(
    _Rm4[_Rm4.parent == 'MSN'][['date', 'coverage', 'ck', 'subs']], on='date', how='outer', suffixes=('', '_v4stakes')).sort_values('date')
SHLOG, DILLOG, PROCLOG, PGLOG, STALELOG = _main_logs

# ---- phan tach troi ----
dec = []
for p in H.parent:
    g = MAIN[(MAIN.parent == p) & (MAIN.coverage >= 0.6)].sort_values('date')
    if len(g) < 2: continue
    a, b = g.iloc[0], g.iloc[-1]
    dec.append(dict(parent=p, d0=a.date, d1=b.date, ck0=a.ck, ck1=b.ck, dln_mv_parent=np.log(b.mv_p / a.mv_p), dln_sotp=np.log(b.sotp / a.sotp)))
DEC = pd.DataFrame(dec)

# ---- loai tru + vao/ra so voi v2 ----
allq = pd.read_csv(os.path.join(IN, 'qualified_parents.csv')).parent.tolist(); EXC = []
for p in allq:
    if p in set(H.parent): continue
    g = MAIN[MAIN.parent == p]
    if not len(g): EXC.append(dict(parent=p, reason='khong co gia me / VCSH me / so CP (hoac gia me STALE, SOTP<=0) tai moi ngay')); continue
    k = g[g.coverage >= 0.6]
    EXC.append(dict(parent=p, reason=f"do phu trung vi {g.coverage.median():.2f}; so thang >=60%: {len(k)} (<3)"
                    + (f"; co con STALE (toi da {int(g.n_stale.max())})" if g.n_stale.max() > 0 else '')))
EXC = pd.DataFrame(EXC)
inout = dict(new_in=sorted(set(H.parent) - set(V2N)), out=sorted(set(V2N) - set(H.parent)))
# ---- audit so CP: moi ma trong panel chinh (me + con dung) ----
used = set(MAIN.parent) | {x.split(':')[0] for s_ in MAIN.subs for x in s_.split() if x}
SHA = SHLOG[SHLOG.ticker.isin(sorted(used))] if len(SHLOG) else SHLOG
# su kien CP (moi loai) ex trong cua so cua ma dang dung: kiem lech so CP dung vs S_pre x (1+r) (chi bao, Rights/PP/EMPL khong sua)
aud = []
for _, e in CE[CE.ticker.isin(sorted(used))].iterrows():
    ds = [d for d in DATES if (e.ticker, d) in SHFIX]
    pre = [d for d in ds if d < e.exright_date]; post = [d for d in ds if d >= e.exright_date]
    if not pre or not post: continue
    a0 = SHFIX[(e.ticker, pre[-1])][0]; a1 = SHFIX[(e.ticker, post[0])][0]
    aud.append(dict(ticker=e.ticker, ex=e.exright_date, method=e.issue_method_code, ratio=e.exercise_ratio, d_pre=pre[-1], d_post=post[0],
                    sh_ratio=a1 / a0, expected=1 + (e.exercise_ratio if pd.notna(e.exercise_ratio) else 0), listing=e.listing_date))
AUD = pd.DataFrame(aud)
if len(AUD):
    AUD['expected_sameday'] = AUD.groupby(['ticker', 'ex']).ratio.transform(lambda x: 1 + x.fillna(0).sum())
    AUD['gap'] = AUD.sh_ratio - AUD.expected_sameday
# ma thuoc tap N (me + con dang dung cua holding trong N)
usedN = set(H.parent) | {x.split(':')[0] for s_ in MAIN[MAIN.parent.isin(list(H.parent))].subs for x in s_.split() if x}
AUDN = AUD[AUD.ticker.isin(sorted(usedN))] if len(AUD) else AUD
SHAN = SHA[SHA.ticker.isin(sorted(usedN))] if len(SHA) else SHA

pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40); pd.set_option('display.max_colwidth', 70); pd.set_option('display.max_rows', 500)
print('== sua so CP (TREASURY_FIX / ISS_FIX) tren ma dang dung ==\n', SHA.to_string(index=False) if len(SHA) else '(rong)')
print('\n== audit su kien CP (ma dang dung) ==\n', AUD.round(4).to_string(index=False) if len(AUD) else '(rong)')
print('\n== sua so CP tren tap N ==\n', SHAN.to_string(index=False) if len(SHAN) else '(rong)')
print('\n== audit su kien CP tren tap N (|gap|>2%) ==\n', AUDN[AUDN.gap.abs() > 0.02].round(4).to_string(index=False) if len(AUDN) else '(rong)')
print('\n== loai tru ==\n', EXC.to_string(index=False))
print('\n== vao/ra so voi v2 ==', json.dumps(inout))
print('\n== holding (PIT, loai stale, do phu>=60%, >=3 thang) ==\n', H.round(4).to_string(index=False))
print('\n== ket qua ==', json.dumps(res, default=float, indent=0))
print('\n== do nhay ==\n', json.dumps(sens, default=float, indent=0))
print('\n== luoi dac ta (a) ==\n', G.round(4).to_string(index=False))
print('\n== ung vien dai ==\n', json.dumps(cand, default=float, indent=0, ensure_ascii=False))
print('\n== chon (PREREG C, C2 dung chu) ==\n', json.dumps(choice, default=float, indent=0, ensure_ascii=False))
print('\n== hull (a)u(d) ==\n', json.dumps(choice_ad, default=float, indent=0, ensure_ascii=False))
print('\n== trung tam la khoang (F5) ==\n', json.dumps(center, default=float, indent=0))
print('\n== moc de xuat HHS (PREREG_v4 C) ==\n', json.dumps(hhs, default=float, indent=0))
print('\n== khu trung (F2) ==\n', DEDUP.to_string(index=False)); print('\n== mo ho (cap volume am/duong, khong dung) ==\n', AMBIG.to_string(index=False))
DLG = pd.DataFrame(list(DILLOG.values())); PLG = pd.DataFrame(list(PROCLOG.values()))
print('\n== kiem khop su kien phat hanh (F1) ==\n', EVCHK_MAIN.round(4).fillna('-').to_string(index=False))
print('\n== pha loang ty le me (F1) — moi ca ==\n', DLG.round(4).fillna('-').to_string(index=False) if len(DLG) else '(rong)')
print('\n== cong tien thu vao VCSH (F1) ==\n', PLG.groupby(['ticker', 'ex']).agg(add_bn=('add_bn', 'first'), n_dates=('date', 'count'), first=('date', 'min'), last=('date', 'max')).reset_index().to_string(index=False) if len(PLG) else '(rong)')
print('\n== bien the (tac dong tung sua) ==\n', json.dumps({k: {kk: vv for kk, vv in v.items() if kk != 'ck_by_parent'} for k, v in VAR.items()}, default=float, indent=0))
print('\n== CK theo holding theo bien the ==\n', pd.DataFrame({k: v['ck_by_parent'] for k, v in VAR.items()}).round(4).to_string())
print('\n== duong theo thang pit_main_market ==\n', ml_all.to_string(index=False))
for k in ['pit_main_book', 'pit_v1_market', 'fixed_main_market']: print(f'\n== duong {k} ==\n', pd.DataFrame(lines[k]).to_string(index=False))
print('\n== phan tach troi ==\n', DEC.round(4).to_string(index=False))
print('\n== con long nhau bi bo ==', nested)
PGL = pd.DataFrame(list(PGLOG.values())); SLG = pd.DataFrame(list(STALELOG.values()))
print('\n== S1 bang ty le override v5 ==\n', ST5[ST5.ovr5.astype(bool)][['parent', 'sub', 'stake', 'stake_date', 'valid_from', 'src']].astype(str).to_string(index=False))
print('\n== S1 MSN theo thang (chinh vs ty le v4) ==\n', MSN_CMP.round(4).to_string(index=False))
print('\n== S2 lai pha loang me (PARENT_DIL_GAIN) ==\n', PGL.round(4).to_string(index=False) if len(PGL) else '(rong)')
print('\n== S3 bo cong tien thu (BCTC con cu >4 quy) ==\n', SLG.to_string(index=False) if len(SLG) else '(rong)')
print('\n== S4 tap ambiguous: rong (code) vs dung chu ==', sorted(AMB_WIDE), sorted(AMB_LETTER))
ALL = pd.concat([R.assign(regime=k[0], stale_rule=k[1], thin_rule=k[2]) for k, R in PAN.items()])
ALL.round(6).to_csv(os.path.join(HERE, 'panel_v5.csv'), index=False)
out = dict(holdings=H.round(6).to_dict('records'), result=res, sens=sens, grid=G.round(6).to_dict('records'), candidates=cand, choice=choice, choice_a_d=choice_ad,
           center=center, hhs_marks=hhs, variants=VAR, dedup=DEDUP.to_dict('records'), ambiguous=AMBIG.to_dict('records'),
           dilution=DLG.to_dict('records') if len(DLG) else [], event_check=EVCHK_MAIN.to_dict('records'), proceeds=PLG.to_dict('records') if len(PLG) else [],
           lines=lines, decomposition=DEC.round(6).to_dict('records'), nested=nested, nested_v4=nested_v4,
           stakes_v5=ST5[ST5.ovr5.astype(bool)][['parent', 'sub', 'stake', 'stake_date', 'valid_from', 'src']].astype(str).to_dict('records'),
           msn_compare=MSN_CMP.round(6).to_dict('records'), parent_dil_gain=PGL.to_dict('records') if len(PGL) else [],
           stale_proceeds_skipped=SLG.to_dict('records') if len(SLG) else [], ambig_wide=sorted(map(list, AMB_WIDE)), ambig_letter=sorted(map(list, AMB_LETTER)), excluded=EXC.to_dict('records'), inout_vs_v2=inout,
           share_fixes=SHA.to_dict('records') if len(SHA) else [], share_fixes_N=SHAN.to_dict('records') if len(SHAN) else [], share_audit_N=AUDN.round(6).to_dict('records') if len(AUDN) else [], share_audit=AUD.round(6).to_dict('records') if len(AUD) else [])


def _clean(o):
    if isinstance(o, dict): return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_clean(v) for v in o]
    if isinstance(o, (bool, np.bool_)): return bool(o)
    if isinstance(o, (int, np.integer)): return int(o)
    if isinstance(o, (float, np.floating)): return None if o != o else round(float(o), 6)
    if o is None or (not isinstance(o, str) and pd.isna(o)): return None
    return str(o)


s = json.dumps(_clean(out), ensure_ascii=False, sort_keys=True)
open(os.path.join(HERE, 'calc_out_v5.json'), 'w').write(s)
print('calc_out md5', hashlib.md5(s.encode()).hexdigest())
