"""DGC tâm điều chỉnh — chạy lại mô hình r3b (dd_redo_20261105/DGC/calc_r3b/model_r3b.py) với hạng mục bổ sung (PREREG_adj v2).
Mù giá: không đọc giá. Khôi phục mô hình (TRIM) vào <root> theo dd_recheck_20261124/DGC/calc/calc_recheck.py; LOCK md5 assert.
Hook (vá trong namespace của model_r3b, không sửa file):
  - Q4: MR2.Q4_EX (EBIT lõi Q4 trước dự phòng; base = 9T/3 = 417,92) → base + dQ4.
  - KT: trích quỹ KTPL hằng năm = KT × LNST ⇒ core × (1−KT) (mọi số hạng của core đều tỉ lệ (1−thuế)) và trừ KT × LNST mẹ 9T/26 1.267,10 (đang nằm trong tiền).
  - Trục độ nhạy (bậc C / luật / quyết định user): tồn kho ngoại trừ, giải phóng VLĐ, trục dự phòng, pháp lý, biến thể r3b.
Chạy: /home/trido/thanhdt/wc_venv/bin/python -I rerun_combo.py /tmp/ddrestore_B/agents/Taylor/research"""
import sys, os, json, hashlib, runpy
ROOT = os.path.abspath(sys.argv[1]); RED = os.path.join(ROOT, 'dd_redo_20261105'); HERE = os.path.dirname(os.path.abspath(__file__))
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(os.path.join(HERE, '..', 'PREREG_adj.md')) == 'ef5157cb3f762d58623ed550ebc214c7'
assert md5(os.path.join(HERE, '..', 'PREREG_adj_v2.md')) == '835dfc1e07f9c67ac7f6c3028b529d13'
LOCK = {'dd_redo_20261105/DGC/calc_r3b/model_r3b.py': 'b1a44b72cb52b200b8bac89701bebb18', 'dd_redo_20261105/DGC/calc_r3b/model_r3b_out.json': 'a8fa8dac3439d64f3bffdfd4429fbd73',
 'dd_redo_20261105/DGC/calc/model_r3_out.json': 'ba91265ff8014116f6e4b9179a73d0fa', 'dd_redo_20261105/DGC/calc/model_r3.py': 'a6a38309532a4c146a48483eb8080519',
 'dd_redo_20261105/DGC/calc/model_r2.py': 'e951b6fde1b50cd674d22771c0bcbe48', 'dd_redo_20261105/DGC/calc/model.py': '99ff32c92d864a70220a81005aa9cf2b',
 'dd_redo_20261105/_common_014127/common.py': '24943cb1a1d35d91bee6ca1fab9d7202', 'dd_redo_20261105/_common_014127/common_r2.py': '95da3038b3710b57e66747acfcd95722',
 'dgc_valuation_20261029_r12/MIKE_EXTRACT_BCTC_Q3_2026.md': '0e8288ee53d4fd906e56f469457ab4da'}
for k, v in LOCK.items(): assert md5(os.path.join(ROOT, k)) == v, k
g = runpy.run_path(os.path.join(RED, 'DGC', 'calc_r3b', 'model_r3b.py'), run_name='r3b')
NS = g['value_ps'].__globals__                       # namespace thật mà grid/value_ps/core tra cứu
grid, mean, CFG3B, M1, MR2, cx, VAR = NS['grid'], NS['mean'], NS['CFG3B'], NS['M1'], NS['MR2'], NS['cx'], NS['VARIANTS']
CK = json.load(open(os.path.join(RED, 'DGC', 'calc_r3b', 'summary_r3b_core.json')))['ck_ref_size']['disc_adv250']; F = 1 - CK
_core, _vps = NS['core'], NS['value_ps']; Q4_0 = MR2.Q4_EX; PROV0 = {k: dict(v) for k, v in MR2.PROV.items()}
assert abs(Q4_0 - 417.92) < 1e-6
NP9T_PARENT = 1267.10
ST = dict(KT=0.0, other=0.0)
def core_adj(s, o, m, r, cfg): return _core(s, o, m, r, cfg) * (1 - ST['KT'])
def vps_adj(s, o, p, ns, m, r, cfg, legal_h=0.0):
    return _vps(s, o, p, ns, m, r, cfg, legal_h) - (ST['KT'] * NP9T_PARENT - ST['other']) * 1e9 / M1.SH
NS['core'] = core_adj; NS['value_ps'] = vps_adj
def run(KT=0.0, dQ4=0.0, other=0.0, prov=None, cfg=None, legal=False):
    ST.update(KT=KT, other=other); MR2.Q4_EX = Q4_0 + dQ4
    if prov:
        for k in MR2.PROV: MR2.PROV[k]['w'] = prov.get(k, 0.0)
    try:
        v, w = grid(cfg or CFG3B, legal=legal)
    finally:
        ST.update(KT=0.0, other=0.0); MR2.Q4_EX = Q4_0
        for k in MR2.PROV: MR2.PROV[k]['w'] = PROV0[k]['w']
    return mean(v, w) * F
C0 = run(); assert round(C0) == 41849, C0
# Đầu vào (nguồn: ADJ_CENTER.md)
EBIT_Q3_EX = 506.35 - 76.18 - 48.96 + 100.0      # LN gộp − BH − QLDN Q3/26 + dự phòng 100 ghi trong giá vốn Q3 = 481,21
DQ4 = EBIT_Q3_EX - Q4_0                            # +63,29
KT_LO = 187.1 / 3024.9                             # Δ quỹ KTPL Q3/26 (405,7→592,8) / LNST mẹ 2025 (BQ) = 6,19%
KT_HI = 0.10                                       # ước lượng trần (không có số DGC)
P = dict(KT=(0.50, 0.25, 0.75), Q4=(0.50, 0.25, 0.75))
cases = {
 'Q4_q3runrate': dict(dQ4=DQ4), 'KT_lo': dict(KT=KT_LO), 'KT_hi': dict(KT=KT_HI),
 'COMBO_center': dict(KT=P['KT'][0] * KT_LO, dQ4=P['Q4'][0] * DQ4),
 'COMBO_low': dict(KT=P['KT'][2] * KT_HI, dQ4=0.0),
 'COMBO_high': dict(KT=P['KT'][1] * KT_LO, dQ4=P['Q4'][2] * DQ4),
 # chỉ độ nhạy
 'S_inv_qual_full': dict(other=-950.9 * (1 - M1.S_EQ)), 'S_inv_qual_full_aftertax': dict(other=-950.9 * (1 - M1.T_NEAR) * (1 - M1.S_EQ)),
 'S_wc_release_to_YE25': dict(other=(2085.9 - 1681.9) * (1 - M1.S_EQ)),
 'S_prov_mot_lan': dict(prov={'mot_lan': 1.0}), 'S_prov_4q': dict(prov={'huu_han_4q': 1.0}), 'S_prov_vinh_vien': dict(prov={'vinh_vien': 1.0}),
 'S_legal_axis': dict(legal=True),
}
for k in ('ore_w0', 'ore_w1.0', 'ore_w0.5_term', 'shield20', 'ronic20', 'r4_fix'): cases['S_' + k] = dict(cfg=VAR[k][1])
res = {}
for lab, kw in cases.items():
    c = run(**kw); res[lab] = dict({k: (round(v, 6) if isinstance(v, float) else v) for k, v in kw.items() if k != 'cfg'},
                                   center=round(c), d_vnd=round(c - C0), d_pct=round((c / C0 - 1) * 100, 3))
assert round(run()) == 41849
out = dict(control_center=round(C0), ck=CK, q4_base=Q4_0, ebit_q3_ex_prov=round(EBIT_Q3_EX, 2), dq4=round(DQ4, 2), kt_lo=round(KT_LO, 5), kt_hi=KT_HI, p=P, cases=res)
json.dump(out, open(os.path.join(HERE, 'rerun_combo_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
print(json.dumps(out, ensure_ascii=False, sort_keys=True))
