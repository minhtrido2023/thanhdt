"""5F r3 MVC (job Taylor_20261107_124458): kiem V_NNC ngam trong BAN CHAT-3C MVC co nhat quan CHAT-3C cua NNC r2 (48.181 sau CK NNC 3,63%) khong.
Tham so TRUNG TAM engine MVC r9 (import calc/mvc_redo_r2.py, khong sua); trong so CHAT-3C: ADMIN 0,45 (ramp/full moi 1/2) + CYCLICAL 0,35, chuan hoa.
Chay (tu thu muc nay): $DNA_PYEXE -B vnnc_check_5f.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); CALC = os.path.abspath(os.path.join(HERE, '..', 'calc'))
sys.path.insert(0, CALC); _c = os.getcwd(); os.chdir(CALC)
import mvc_redo_r2 as M  # noqa: E402
os.chdir(_c)
V8, ND = M.V8, M.NODELAY
b = {('ADMIN_GATED', a): V8.branch('ADMIN_GATED', dict(ND), admin=a) for a in ('perm05', 'ramp', 'full')}
b[('CYCLICAL', '-')] = V8.branch('CYCLICAL', dict(ND)); b[('STRUCTURAL', '-')] = V8.branch('STRUCTURAL', dict(ND))
W = {'current': {('STRUCTURAL', '-'): .20, ('ADMIN_GATED', 'perm05'): .15, ('ADMIN_GATED', 'ramp'): .15, ('ADMIN_GATED', 'full'): .15, ('CYCLICAL', '-'): .35},
     'chat3c': {('ADMIN_GATED', 'ramp'): .225, ('ADMIN_GATED', 'full'): .225, ('CYCLICAL', '-'): .35}}
out = {'cells': {f'{k[0]}|{k[1]}': dict(V_MVC=float(x['vm']), V_NNC=float(x['vn'])) for k, x in b.items()}}
for lab, ws in W.items():
    s = sum(ws.values()); out[lab] = {f: sum(w * float(b[k][key]) for k, w in ws.items()) / s for f, key in (('V_MVC', 'vm'), ('V_NNC', 'vn'))}
NNC_CHAT_POST, NNC_CK = 48181, 0.03632771556437639
out['nnc_r2_chat3c_pre_ck'] = NNC_CHAT_POST / (1 - NNC_CK)
out['gap_vnnc_chat_vs_nnc_r2'] = out['chat3c']['V_NNC'] / out['nnc_r2_chat3c_pre_ck'] - 1
out['mvc_slope_per10k_vnnc'] = 965.917  # dd_MVC_20261103/r8/calc/model_r8_out.txt:78
for k in ('current', 'chat3c'): print(k, {a: round(v) for a, v in out[k].items()})
print('NNC r2 CHAT-3C truoc CK', round(out['nnc_r2_chat3c_pre_ck']), 'lech', f"{out['gap_vnnc_chat_vs_nnc_r2']:+.1%}")
json.dump(out, open(os.path.join(HERE, 'vnnc_check_5f_out.json'), 'w'), indent=1, sort_keys=True)
