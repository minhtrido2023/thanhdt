"""Cầu EBIT 9T/26 quy năm (khung r4, cước 4,686%) → E[EBIT 2027] r4. Cộng dồn, thứ tự như r3."""
import json, model_r4 as M
R = M.run(); E27 = R['En'][2027][0]; fr = R['freight']
w_h1, w_q3 = 939.271, 440.032
coke9 = (w_h1*1541 + w_q3*2040)/(w_h1+w_q3)
nvl9 = (w_h1*0.4864 + w_q3*0.5520)/(w_h1+w_q3)
fsx = sum(w*sx*(0.97*(1-s*M.STEP)+0.03) for s,sx,w in M.PT_R3.values())
def e(nvl, f, p, elec, fs):
    rev = M.REV*f*p; return rev - M.REV*(nvl + M.DV*elec) - M.REV*M.REST - (fr*fs*M.REV*p + 28.3)
rows = [('9T/26 quy năm, khung r4 (thuế 10%, NVL 9T, cốc 9T, điện cũ)', e(nvl9, 1, 1, 1, R['Esx'])),
 ('bước thuế 10→15%', e(nvl9, R['Ef'], 1, 1, fsx)),
 ('cốc 9T→2.108', e(nvl9+M.K*(2108-coke9), R['Ef'], 1, 1, fsx)),
 ('quặng H1/27 GĐ2 + H2 theo xác suất', e(E27, R['Ef'], 1, 1, fsx)),
 ('điện', e(E27, R['Ef'], 1, R['elec'], fsx)),
 ('giá E[p] r4', e(E27, R['Ef'], R['EP'], R['elec'], fsx))]
for i,(k,v) in enumerate(rows): print(f"{k:60s} {v:8.1f} {'' if i==0 else f'{v-rows[i-1][1]:+7.1f}'}")
print('9T/26 thực quy năm (205,559×4/3) =', round(205.559*4/3,1), '| tại s_exp 9T 0,353:', round(e(nvl9,1,1,1,0.353),1))
