# -*- coding: utf-8 -*-
"""Dung chuoi dinh gia cap-index hang ngay theo NHIEU phuong phap (cap-weighted THO
va cac ban BEN voi outlier don le), theo dung bai hoc Phu luc B (VIC).

Ro (basket) = top-100 von hoa moi phien (trong so cac ma co metric hop le).
Ban ra: metrics_daily.csv
"""
import numpy as np, pandas as pd
EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_valframe/'

p = pd.read_parquet(EXP + 'panel150.parquet')
p['time'] = pd.to_datetime(p['time'])
p = p[np.isfinite(p.mcap) & (p.mcap > 0)].copy()
# KHOP DUNG Phu luc B: ro = ma co cot PB>0; ty so P/B tinh = mcap/book (= Price/BVPS),
# KHONG dung thang cot PB (cot PB dung Close da dieu chinh -> lech nhe).
p['pb_i'] = p.mcap / p.book
p['pe_i'] = p.PE

def cap_weights(w, cap=0.10):
    w = np.asarray(w, float).copy()
    for _ in range(60):
        w = w / w.sum(); over = w > cap + 1e-12
        if not over.any(): break
        ex = (w[over] - cap).sum(); w[over] = cap; fr = ~over
        if w[fr].sum() <= 0: break
        w[fr] += ex * w[fr] / w[fr].sum()
    return w / w.sum()

def harm(w, x):   # trung binh dieu hoa co trong so = dung cach gop ty so dinh gia
    return w.sum() / (w / x).sum()

def three(mc, ratio, minn=30):
    """tra (cap-weighted THO, capped-10%, trung vi EW) cho 1 ty so dinh gia."""
    ok = np.isfinite(ratio) & (ratio > 0) & np.isfinite(mc) & (mc > 0)
    if ok.sum() < minn: return (np.nan, np.nan, np.nan, int(ok.sum()))
    r = ratio[ok]; m = mc[ok]; w = m / m.sum()
    return (harm(w, r), harm(cap_weights(w), r), float(np.median(r)), int(ok.sum()))

rows = []
for t, d in p.groupby('time'):
    d = d.sort_values('mcap', ascending=False)
    rec = {'time': t, 'n_raw': len(d)}
    # --- PB / PE: ro = top-100 trong so ma co ty so > 0 (khop Phu luc B)
    for name, col, filt in (('pb', 'pb_i', 'PB'), ('pe', 'pe_i', 'PE')):
        s = d[np.isfinite(d[filt]) & (d[filt] > 0) & np.isfinite(d[col]) & (d[col] > 0)].head(100)
        cw, c10, med, n = three(s.mcap.values, s[col].values)
        rec[f'{name}_cw'], rec[f'{name}_cap10'], rec[f'{name}_ewmed'], rec[f'n_{name}'] = cw, c10, med, n
        if len(s):
            rec[f'{name}_top1'] = s.iloc[0].ticker
            rec[f'{name}_top1w'] = float(s.iloc[0].mcap / s.mcap.sum())
    # --- EVEB: gop dung = sum(EV)/sum(EBITDA), EV_i = EVEB_i * EBITDA_i
    s = d[np.isfinite(d.EVEB) & (d.EVEB > 0) & np.isfinite(d.EBITDA_P0) & (d.EBITDA_P0 > 0)].head(100)
    if len(s) >= 30:
        ev = s.EVEB.values * s.EBITDA_P0.values
        rec['eveb_cw'] = ev.sum() / s.EBITDA_P0.values.sum()
        w = s.mcap.values / s.mcap.values.sum()
        rec['eveb_cap10'] = harm(cap_weights(w), s.EVEB.values)
        rec['eveb_ewmed'] = float(np.median(s.EVEB.values))
    rec['n_eveb'] = int(len(s))
    # --- PCF (kiem tra bo sung)
    s = d[np.isfinite(d.PCF) & (d.PCF > 0)].head(100)
    if len(s) >= 30:
        w = s.mcap.values / s.mcap.values.sum()
        rec['pcf_cap10'] = harm(cap_weights(w), s.PCF.values)
        rec['pcf_ewmed'] = float(np.median(s.PCF.values))
    rows.append(rec)

S = pd.DataFrame(rows).sort_values('time').reset_index(drop=True)
# loai ngay du lieu hong (ro qua mong) — cung tieu chi Phu luc B
S = S[S.n_pb >= 50].reset_index(drop=True)
S.to_csv(EXP + 'metrics_daily.csv', index=False)
print(S.shape, S.time.min().date(), '->', S.time.max().date())
print(S.tail(3)[['time','pb_cw','pb_cap10','pb_ewmed','pe_cw','pe_cap10','pe_ewmed',
                 'eveb_cw','eveb_cap10','eveb_ewmed','n_eveb']].to_string(index=False))

# --- kiem chung tai lap voi Phu luc B (pb_variants_final.csv) ---
try:
    B = pd.read_csv('/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pb_exvic/pb_variants_final.csv',
                    parse_dates=['time'])[['time','pb_cw','pb_cap10','pb_ewmed','pe_cw']]
    m = S.merge(B, on='time', suffixes=('', '_B')).dropna(subset=['pb_cw_B'])
    for c in ['pb_cw','pb_cap10','pb_ewmed','pe_cw']:
        d_ = (m[c] - m[c + '_B']).abs()
        print(f'  tai lap {c}: N={len(m)} sai so tuyet doi TB={d_.mean():.6f} max={d_.max():.6f}')
except Exception as e:
    print('khong kiem chung duoc:', e)
