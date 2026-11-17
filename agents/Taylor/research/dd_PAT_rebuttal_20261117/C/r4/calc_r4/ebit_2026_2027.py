"""Cầu EBIT 9T/26 quy năm (khung mô hình) → E[EBIT 2027] r3. Cộng dồn, thứ tự cố định."""
import json, model_r3 as M
R = M.run(); E27 = R['En'][2027]
w_h1, w_q3 = 939.271, 440.032
coke9 = (w_h1*1541 + w_q3*2040)/(w_h1+w_q3)
nvl9 = (w_h1*0.4864 + w_q3*0.5520)/(w_h1+w_q3)
def e(nvl, f, p, sx, elec, fsx=None):
    rev = M.REV*f*p; sga = 0.0385*(fsx if fsx is not None else sx*f)*M.REV*p + 28.3
    return rev - M.REV*(nvl + M.DV*elec) - M.REV*M.REST - sga
rows=[]; cur = e(nvl9, 1.0, 1.0, R['Esx'], 1.0); rows.append(('9T/26 quy năm trong khung mô hình (thuế XK 10%%, NVL 9T, cốc 9T ≈ %.0f, điện cũ)'%coke9, cur))
fsx = sum(w*sx*(0.97*(1-s*M.STEP)+0.03) for s,sx,w in M.PT.values())
steps=[('bước thuế 10→15%% (E[f]=%.4f)'%R['Ef'], lambda: e(nvl9, R['Ef'], 1.0, R['Esx'], 1.0, fsx)),
 ('cốc 9T→2.108 (+%.1fpp NVL)'%(100*M.K*(2108-coke9)), lambda: e(nvl9+M.K*(2108-coke9), R['Ef'], 1.0, R['Esx'], 1.0, fsx)),
 ('quặng: H1/27 GĐ2 + H2 theo xác suất (E NVL27=%.2f%%)'%(100*E27), lambda: e(E27, R['Ef'], 1.0, R['Esx'], 1.0, fsx)),
 ('điện ×%.4f'%R['elec'], lambda: e(E27, R['Ef'], 1.0, R['Esx'], R['elec'], fsx)),
 ('giá E[p]=%.4f'%R['EP'], lambda: e(E27, R['Ef'], R['EP'], R['Esx'], R['elec'], fsx))]
for k,fn in steps:
    v=fn(); rows.append((k, v))
for i,(k,v) in enumerate(rows):
    print(f"{k:80s} {v:8.1f} {'' if i==0 else f'{v-rows[i-1][1]:+7.1f}'}")
print('kiểm: base ebit27 r3 =', round(json.load(open('model_out_r3.json'))['base']['ebit27'],1))
print('2026E EBIT thực (H1 151,7 + Q3 53,8 + Q4≈Q3 53,8) =', round(151.717+53.844*2,1))
