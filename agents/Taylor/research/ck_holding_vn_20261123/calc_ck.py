"""CK holding VN — buoc 2: tinh tu inputs/*.csv (da khoa md5 o inputs/LOCK_md5.txt). Tat dinh, khong mang.
Chay: python3 calc_ck.py > run1.txt ; lan 2 > run2.txt ; md5 phai trung. Ghi calc_out.json.

Dinh nghia (moi holding p, moi ngay do D, chi dung du lieu da cong bo <= D):
  MV_i      = Price_i(D, CHUA dieu chinh) x SoCP_i(D, oshares_at PIT; fallback dong quy da cong bo)
  E_i, E_p  = VCSH thuoc co dong ME (owners_equity - minority_interests, VCI CDKT) cua quy moi nhat co
              Release_Date <= D. Thieu CDKT VCI -> E_i = VCSH tong BQ (BVPS x OShares, GOM NCI) [co fallback].
  s_i       = ty le loi ich theo BCTC (KBS, update_date); chi dung khi update_date + 90 ngay <= D (han nop BCTC nam).
  SOTP_p    = sum s_i MV_i  +  (E_p - sum s_i E_i)          <- phan "con lai theo SO" gom no rong/ tien cap me,
                                                              cong ty khong niem yet, BDS... (VCSH me da tru no me)
  DoPhu_p   = sum s_i MV_i / SOTP_p ;   CK_p = 1 - MV_p / SOTP_p
  Giu holding co DoPhu >= 0,60 (luat brief). Con thanh khoan thap (ngoai universe_pit) duoc dem rieng.
N = so HOLDING. Thong ke: trung vi, IQR, bootstrap theo holding (10.000 lan, seed 20261123).
"""
import os, json, hashlib
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); IN = os.path.join(HERE, 'inputs')
DATES = ['2026-03-31', '2026-06-30', '2026-09-30', '2026-11-20']
COV_MIN = 0.60
ST = pd.read_csv(os.path.join(IN, 'stakes.csv'))
FIN = pd.read_csv(os.path.join(IN, 'fin_equity.csv'))
PX = pd.read_csv(os.path.join(IN, 'prices.csv'))
SH = pd.read_csv(os.path.join(IN, 'shares_pit.csv'))
DV = pd.read_csv(os.path.join(IN, 'divs_24m.csv'))
QEND = {'Q1': '-03-31', 'Q2': '-06-30', 'Q3': '-09-30', 'Q4': '-12-31'}


def qend(q): return pd.Timestamp(q[:4] + QEND[q[4:]])


FIN['rel'] = pd.to_datetime(FIN.rel)
# khong co Release_Date (ma khong co trong BQ ticker_financial) -> bao thu: cuoi quy + 90 ngay
FIN['rel_used'] = FIN.rel.fillna(FIN.quarter.map(qend) + pd.Timedelta(days=90))


def equity(t, D):
    f = FIN[(FIN.ticker == t) & (FIN.rel_used <= D)].sort_values('rel_used')
    if len(f) and not np.isnan(f.eq_parent.iloc[-1]) and f.eq_parent.iloc[-1] != 0:
        return float(f.eq_parent.iloc[-1]), f.quarter.iloc[-1], 'VCI_parent'
    f2 = FIN[(FIN.ticker == t) & (FIN.rel <= D) & FIN.eq_tot_bq.notna()].sort_values('rel')
    if len(f2): return float(f2.eq_tot_bq.iloc[-1]), f2.quarter.iloc[-1], 'BQ_total_inclNCI'
    return np.nan, None, 'NONE'


def mv(t, d):
    p = PX[(PX.ticker == t) & (PX.date == d)]; s = SH[(SH.ticker == t) & (SH.date == d)]
    if not len(p) or not len(s) or np.isnan(s.shares.iloc[0]): return np.nan, None, None, None
    return float(p.price.iloc[0] * s.shares.iloc[0]), bool(p.in_universe.iloc[0]), s.method.iloc[0], float(p.adv60.iloc[0])


rows, detail = [], []
for p in sorted(ST.parent.unique()):
    for d in DATES:
        D = pd.Timestamp(d)
        Ep, qp, srcp = equity(p, D); MVp, _, mp, advp = mv(p, d)
        lmv = lbook = lmv_liq = lmv_ctrl = nci_est = 0.0; n_used = 0; fb = 0
        for _, r in ST[ST.parent == p].iterrows():
            if pd.Timestamp(r.stake_date) + pd.Timedelta(days=90) > D: continue
            s = r.stake_kbs / 100.0; MVi, liq, mi, _ = mv(r['sub'], d); Ei, qi, srci = equity(r['sub'], D)
            if np.isnan(MVi) or np.isnan(Ei) or MVi <= 0: continue   # khong co gia/so -> de nguyen trong phan theo so
            n_used += 1; fb += srci != 'VCI_parent'
            lmv += s * MVi; lbook += s * Ei
            if liq: lmv_liq += s * MVi
            if s >= 0.5: lmv_ctrl += s * MVi; nci_est += (1 - s) * Ei
            detail.append(dict(parent=p, date=d, sub=r['sub'], stake=s, mv_bn=MVi / 1e9, eq_bn=Ei / 1e9, eq_src=srci, eq_q=qi,
                               in_universe=liq, shares_method=mi))
        if np.isnan(Ep) or np.isnan(MVp): continue
        if srcp == 'BQ_total_inclNCI':   # VCSH me xap xi: tru NCI cua con NIEM YET hop nhat; NCI con khong niem yet BO SOT -> CK lech LEN
            Ep -= nci_est; srcp = 'BQ_total_minus_listedNCI'
        sotp = lmv + (Ep - lbook)
        rows.append(dict(parent=p, date=d, mv_parent_bn=MVp / 1e9, eq_parent_bn=Ep / 1e9, eq_q=qp, eq_src=srcp,
                         listed_mv_bn=lmv / 1e9, listed_book_bn=lbook / 1e9, rest_book_bn=(Ep - lbook) / 1e9, sotp_bn=sotp / 1e9,
                         coverage=lmv / sotp if sotp > 0 else np.nan, cov_liquid=lmv_liq / sotp if sotp > 0 else np.nan,
                         ctrl_share=lmv_ctrl / lmv if lmv > 0 else np.nan,
                         ck=1 - MVp / sotp if sotp > 0 else np.nan, n_subs=n_used, n_eq_fallback=fb, adv60_parent_bn=advp / 1e9))
R = pd.DataFrame(rows); DT = pd.DataFrame(detail)

# ---- co tuc tien 24 thang: con -> me (theo ty le) va me -> co dong; dung so CP 2026-09-30 ----
def shares(t, d='2026-09-30'):
    s = SH[(SH.ticker == t) & (SH.date == d)]; return float(s.shares.iloc[0]) if len(s) else np.nan


DVs = DV.groupby('ticker').value_per_share.sum()
divrow = {}
for p in sorted(ST.parent.unique()):
    sub = ST[ST.parent == p]
    din = sum(r.stake_kbs / 100 * shares(r['sub']) * DVs.get(r['sub'], 0.0) for _, r in sub.iterrows() if not np.isnan(shares(r['sub'])))
    dout = shares(p) * DVs.get(p, 0.0)
    divrow[p] = dict(div_in_24m_bn=din / 1e9, div_out_24m_bn=dout / 1e9)

# ---- tong hop theo holding: trung vi qua cac ngay do ----
H = R.groupby('parent').agg(ck=('ck', 'median'), ck_min=('ck', 'min'), ck_max=('ck', 'max'), coverage=('coverage', 'median'),
                            cov_liquid=('cov_liquid', 'median'), ctrl_share=('ctrl_share', 'median'), n_dates=('ck', 'count'),
                            sotp_bn=('sotp_bn', 'last'), listed_mv_bn=('listed_mv_bn', 'last'), eq_src=('eq_src', 'last'),
                            n_eq_fallback=('n_eq_fallback', 'max')).reset_index()
H['parent_eq_exact'] = H.eq_src == 'VCI_parent'
H['div_in_24m_bn'] = H.parent.map(lambda p: divrow[p]['div_in_24m_bn'])
H['div_out_24m_bn'] = H.parent.map(lambda p: divrow[p]['div_out_24m_bn'])
H['div_in_yield_ann'] = H.div_in_24m_bn / 2 / H.listed_mv_bn
H['control'] = H.ctrl_share >= 0.5
H['keep'] = H.coverage >= COV_MIN


def summ(x, label, B=10000, seed=20261123):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    if len(x) == 0: return dict(group=label, N=0)
    rng = np.random.default_rng(seed); bs = np.median(rng.choice(x, size=(B, len(x)), replace=True), axis=1)
    return dict(group=label, N=int(len(x)), median=float(np.median(x)), q25=float(np.percentile(x, 25)), q75=float(np.percentile(x, 75)),
                min=float(x.min()), max=float(x.max()), boot_med_p5=float(np.percentile(bs, 5)), boot_med_p95=float(np.percentile(bs, 95)))


K = H[H.keep]
groups = [summ(K.ck, 'toan bo (do phu >= 60%)'),
          summ(K[K.control].ck, '(i) kiem soat: >=50% gia tri niem yet tu con >=50%'),
          summ(K[K.control & (K.div_in_yield_ann < 0.01)].ck, '(i)+(ii) kiem soat + co tuc tien tu con < 1%/nam (giong HHS nhat)'),
          summ(K[K.control & (K.div_in_yield_ann >= 0.01)].ck, '(i) kiem soat + co tuc tien tu con >= 1%/nam'),
          summ(K[~K.control].ck, 'khong kiem soat (chu yeu lien ket)'),
          summ(H[(H.cov_liquid >= COV_MIN)].ck, 'do nhay: do phu THANH KHOAN (universe_pit) >= 60%'),
          summ(H[H.coverage >= 0.5].ck, 'do nhay: nguong do phu 50%'),
          summ(H[H.coverage >= 0.7].ck, 'do nhay: nguong do phu 70%'),
          summ(K[K.parent_eq_exact].ck, 'do nhay: chi holding co VCSH me CHINH XAC (VCI CDKT)')]
# kiem cheo 2: tuong quan hang CK vs co tuc tien tu con (Spearman, N nho -> chi mo ta)
rho = float(K[['ck', 'div_in_yield_ann']].rank().corr().iloc[0, 1]) if len(K) >= 4 else np.nan

pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
print('== CK holding VN — theo holding (trung vi 4 ngay do 2026-03-31/06-30/09-30/11-20) ==')
print(H.round(4).to_string(index=False))
print('\n== chi tiet theo ngay ==')
print(R.round(4).to_string(index=False))
print('\n== nhom ==')
for g in groups: print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in g.items()})
print(f'\nSpearman(CK, co tuc tien tu con/nam / gia tri niem yet) tren nhom giu: {rho:.3f} (N={len(K)})')
out = dict(by_holding=H.round(6).to_dict('records'), by_date=R.round(6).to_dict('records'), groups=groups,
           spearman_ck_vs_divin=rho, cov_min=COV_MIN, dates=DATES,
           detail_subs=DT.round(6).to_dict('records'))
s = json.dumps(out, ensure_ascii=False, sort_keys=True, default=str)
open(os.path.join(HERE, 'calc_out.json'), 'w').write(s)
print('calc_out md5', hashlib.md5(s.encode()).hexdigest())
