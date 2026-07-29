"""Chot GO/NO-GO: tach ro MUC (level) vs HANG (rank), da kiem dinh, va kich ban chuan hoa E."""
import pandas as pd, numpy as np
from scipy import stats

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_roe/'
pd.set_option('display.width', 260)
df = pd.read_csv(EXP + 'panel_roe_fwd2.csv', parse_dates=['time'])
df['ym'] = df.time.dt.strftime('%Y-%m')
cur = df.dropna(subset=['roe_agg']).iloc[-1]

# --- A. cong tuyen: MUC vs HANG ---
print('=== A. MUC (level) vs HANG (rank): ROE co the "them thong tin" o dau? ===')
ann = df[df.ym.str.endswith('-07')].groupby(df.time.dt.year).tail(1)
ann = ann.dropna(subset=['fwd_12M', 'pe_agg', 'pb_agg', 'roe_agg', 'pe_agg_pex', 'pb_agg_pex', 'roe_agg_pex'])
def r2(cols, tgt='fwd_12M'):
    Xm = np.column_stack([np.ones(len(ann))] + [ann[c].values for c in cols]); yv = ann[tgt].values
    bb, *_ = np.linalg.lstsq(Xm, yv, rcond=None)
    return 1 - ((yv - Xm @ bb) ** 2).sum() / ((yv - yv.mean()) ** 2).sum()
print('N nam doc lap = %d' % len(ann))
print('-- dung MUC log (o day ROE = logPB - logPE, cong tuyen HOAN HAO) --')
for cols in [['pe_agg'], ['pb_agg'], ['roe_agg'], ['pe_agg', 'pb_agg'], ['pe_agg', 'pb_agg', 'roe_agg']]:
    for c in cols: ann['l_' + c] = np.log(ann[c])
    print('   R2(fwd12M ~ %-32s) = %.4f' % ('+'.join(cols), r2(['l_' + c for c in cols])))
print('   => R2 cua {PE,PB} va {PE,PB,ROE} BANG NHAU: o dang muc, ROE khong them 1 bit nao.')
print('-- dung HANG (PIT percentile, bien doi don dieu PHI TUYEN, xep hang RIENG tung bien) --')
for cols in [['pe_agg_pex'], ['pb_agg_pex'], ['roe_agg_pex'], ['pe_agg_pex', 'pb_agg_pex'], ['pe_agg_pex', 'pb_agg_pex', 'roe_agg_pex']]:
    print('   R2(fwd12M ~ %-45s) = %.4f' % ('+'.join(cols), r2(cols)))
print('   => o dang HANG, ROE_pctile KHONG con la ham tuyen tinh cua 2 hang kia => co the tang R2.')
print('      Nhung do la LOI ICH CUA PHEP BIEN DOI, khong phai thong tin kinh te moi.')

# --- B. da kiem dinh ---
print('\n=== B. DA KIEM DINH (multiple testing) tren mau 1 diem/nam ===')
sigs = ['pe_agg_pex', 'pb_agg_pex', 'roe_agg_pex', 'pe_agg_p3y', 'pb_agg_p3y', 'roe_agg_p3y']
tgts = ['fwd_12M', 'minfwd_12M']
res = []
for s in sigs:
    for t in tgts:
        a = ann.dropna(subset=[s, t]) if s in ann else None
        a = df[df.ym.str.endswith('-07')].groupby(df.time.dt.year).tail(1).dropna(subset=[s, t])
        if len(a) < 8: continue
        rho, pv = stats.spearmanr(a[s], a[t])
        res.append(dict(signal=s, target=t, N=len(a), rho=round(rho, 3), p=round(pv, 4)))
B = pd.DataFrame(res).sort_values('p')
ntest = len(B)
B['p_bonferroni'] = (B.p * ntest).clip(upper=1).round(3)
# Benjamini-Hochberg
B = B.reset_index(drop=True)
B['rank'] = B.index + 1
B['BH_thresh'] = (0.05 * B['rank'] / ntest).round(4)
B['pass_BH_05'] = B.p <= B.BH_thresh
print(B.to_string(index=False))
print('  So kiem dinh = %d. Nguong Bonferroni 5%% = %.4f.' % (ntest, 0.05 / ntest))
B.to_csv(EXP + 'multipletest.csv', index=False)

# --- C. kich ban chuan hoa loi nhuan ---
print('\n=== C. KICH BAN: PE se thanh bao nhieu neu ROE ve cac muc lich su? ===')
w10 = df[df.time >= cur.time - pd.DateOffset(years=10)].roe_agg
w5 = df[df.time >= cur.time - pd.DateOffset(years=5)].roe_agg
scen = [('ROE giu nguyen (hien tai)', cur.roe_agg),
        ('ve trung vi 5 nam', w5.median()), ('ve trung vi 10 nam', w10.median()),
        ('ve p25 cua 10 nam', w10.quantile(.25)), ('ve p05 cua 10 nam', w10.quantile(.05)),
        ('ve MUC THAP NHAT 10 nam', w10.min())]
rows = []
for lab, roe in scen:
    pe_n = cur.pb_agg / roe
    rows.append(dict(kich_ban=lab, ROE=round(100 * roe, 2), PE_ngu_y=round(pe_n, 2),
                     chenh_vs_PE_hien_tai='%+.1f%%' % (100 * (pe_n / cur.pe_agg - 1)),
                     pctile_PE_trong_10Y=round(100 * (df[df.time >= cur.time - pd.DateOffset(years=10)].pe_agg < pe_n).mean(), 1)))
C = pd.DataFrame(rows); print(C.to_string(index=False))
print('  (gia KHONG doi trong moi kich ban -> PE_ngu_y = PB hien tai / ROE kich ban)')
C.to_csv(EXP + 'scenario_normalized_pe.csv', index=False)

# --- D. hien trang ROE cao: bao nhieu lan trong lich su, ket cuc ra sao (co mau THAT) ---
print('\n=== D. Cac dot ROE pctile-3Y >= 0.90 trong lich su — liet ke EPISODE ===')
m = df.roe_agg_p3y >= 0.90
sub = df[m]
grp = (sub.index.to_series().diff() > 21).cumsum()
for g, gd in sub.groupby(grp.values):
    i0 = gd.index[0]
    f12 = df.fwd_12M.iloc[i0]; mn = df.minfwd_12M.iloc[i0]
    print('  %s -> %s  n=%3d  ROE@start=%.2f%%  fwd12M@start=%s  dayNhat12M=%s' % (
        gd.time.iloc[0].date(), gd.time.iloc[-1].date(), len(gd), 100 * gd.roe_agg.iloc[0],
        ('%+.1f%%' % (100 * f12)) if pd.notna(f12) else 'chua du',
        ('%.1f%%' % (100 * mn)) if pd.notna(mn) else 'chua du'))
