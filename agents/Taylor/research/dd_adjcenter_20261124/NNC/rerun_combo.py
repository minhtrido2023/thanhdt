"""NNC tâm điều chỉnh — CHẠY LẠI mô hình r3 (dd_redo_20261105/NNC/calc/nnc_redo_r3.py) với TỔ HỢP hạng mục (PREREG_adj_v2 §5).
Mù giá: chỉ đổi dòng tiền NNC trong hàm nnc_ex gốc (MVC model_r5), không đọc giá mới.
Hook: thay N3._nnc_ex6 (model_r3 gọi qua tên toàn cục lúc chạy) bằng bản:
  - KT  = tỷ lệ trích quỹ KTPL / LNST: thuế hiệu dụng 1-(1-0,2)(1-KT) CHỈ trong lời gọi NNC (MVC không đổi);
          trừ thêm KT x (LNST 9T/26 160,08 + Q4/26) — LN 2026 đang nằm trong tiền ròng, sẽ trích năm 2027.
  - G   = capex vượt khấu hao (tỷ/năm), 2027–2043, trừ PV (cùng hàm M.pv, cùng r của ô lưới).
  - DQ4 = điều chỉnh LNST Q4/26 so với ước lượng 60 tỷ.
Khôi phục mô hình (bị TRIM 19/11) vào <root> theo dd_recheck_20261124/NNC/calc/calc_recheck.py; LOCK md5 assert.
Chạy: /home/trido/thanhdt/wc_venv/bin/python -I rerun_combo.py /tmp/ddrestore_B/agents/Taylor/research
"""
import sys, os, json, hashlib, subprocess
ROOT = os.path.abspath(sys.argv[1]); CALC = os.path.join(ROOT, 'dd_redo_20261105', 'NNC', 'calc'); PY = sys.executable
HERE = os.path.dirname(os.path.abspath(__file__))
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(os.path.join(HERE, '..', 'PREREG_adj.md')) == 'ef5157cb3f762d58623ed550ebc214c7'
assert md5(os.path.join(HERE, '..', 'PREREG_adj_v2.md')) == '835dfc1e07f9c67ac7f6c3028b529d13'
LOCK = {'dd_redo_20261105/NNC/calc/assumptions_r3.json': 'c36da69593e28d05ad92acca530a2cb4', 'dd_redo_20261105/NNC/calc/nnc_redo_r3.py': '9b8969ec8ea8c2ba93728deb0caee45d',
 'dd_redo_20261105/NNC/calc/nnc_redo_r2_out.json': 'c1522cb0b75385543cd4a2d2c4a16470', 'dd_NNC_20261030/r6/calc/nnc_model_r6.py': '6688f1e61c8568f63fae889312462442',
 'dd_NNC_20261030/r5/calc/nnc_model_r5.py': '14f3fb87c2d0b4c340382a371b26be29', 'dd_NNC_20261030/r4/calc/model_r4.py': '812ca351e968913e2e4787bbcff9f552',
 'dd_NNC_20261030/r3/calc/model_r3.py': 'c992769f86794f5d6f39b0df7e13bd91', 'dd_MVC_20261103/r6/calc/model_r6.py': 'bd93107a93a7f958eea03e1a5f01eed0',
 'dd_MVC_20261103/r6/calc/model_r5.py': '9fd64a26a7daca9b0244c3f62ce7dd91', 'dd_MVC_20261103/r6/calc/valuation_base.py': 'd3fb9637389ca6d9c7472e28f4846506',
 'dd_redo_20261105/common.py': 'e430be2363c19983d8d83120a3743e98', 'dd_redo_20261105/_shared/wpct.py': '4597bc083f0d64d8873141b12fbfb3a6'}
for k, v in LOCK.items(): assert md5(os.path.join(ROOT, k)) == v, k
CHILD = r'''
import sys, os
CALC, KT, G, DQ4 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
PATCH = KT != 0 or G != 0 or DQ4 != 0
os.chdir(CALC); f = os.path.join(CALC, 'nnc_redo_r3.py'); src = open(f, encoding='utf-8').read()
A2 = ["assert abs(c0_r2 - r2['center_param_nodelay']) < 1e-6, (c0_r2, r2['center_param_nodelay'])",
      "assert abs(br['r2_rebuild']['mean'] - r2['pre']['mean']) < 1e-6, (br['r2_rebuild']['mean'], r2['pre']['mean'])"]
ANCH = "N5, N4, N3, S = N6.N5, N6.N4, N6.N3, N6.S\n"
assert src.count(ANCH) == 1
HOOK = """
_KT, _G, _DQ4, _NP9T = %r, %r, %r, 160.08
_orig6 = N3._nnc_ex6; _M = N3.M
def _nnc_ex_adj(k, path, P):
    t0 = _M.TAX; _M.TAX = 1 - (1 - t0) * (1 - _KT)
    try:
        v = _orig6(k, path, P)
    finally:
        _M.TAX = t0
    v += _DQ4 - _KT * (_NP9T + _M.n_q4 + _DQ4)
    v -= _M.pv([(y, _G) for y in range(2027, 2044)], P['r'])
    return v
N3._nnc_ex6 = _nnc_ex_adj
""" % (KT, G, DQ4)
if PATCH:
    src = src.replace(ANCH, ANCH + HOOK)
    for a in A2:
        assert src.count(a) == 1; src = src.replace(a, 'pass')  # 2 kiểm tái lập r2 chỉ đúng khi không patch (đã chạy ở CONTROL)
exec(compile(src, f, 'exec'), {'__name__': '__main__', '__file__': f})
'''
def run(kt, g, dq4):
    p = subprocess.run([PY, '-I', '-B', '-c', CHILD, CALC, repr(kt), repr(g), repr(dq4)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-2000:]
    o = json.load(open(os.path.join(CALC, 'nnc_redo_r3_out.json'))); return p.stdout, o
so, o = run(0.0, 0.0, 0.0)  # CONTROL
assert hashlib.md5(so.encode()).hexdigest() == '857c7adb3a319e2a819cbfa4de08caa4', 'CONTROL lệch'
base = o['post']; C0 = base['mean']; assert round(C0) == 61273
# Đầu vào (nguồn trong ADJ_CENTER.md / adj.json)
KT_LO, KT_HI = 0.046, 0.082     # cận dưới tỷ lệ trích KTPL: Δtồn quỹ/LNST (2 kỳ)
G_C, G_LO, G_HI = 7.5, 0.0, 19.0  # capex − khấu hao, tỷ/năm
DQ4_C, DQ4_HI = 9.29, 28.3        # Q4/26 = Q3/26 69,29 (phẳng) ; = Q3×1,275 (TB Q4/Q3 2024–25)
P = dict(KT=(0.50, 0.25, 0.75), G=(0.65, 0.40, 0.90), Q4=(0.35, 0.15, 0.55))
cases = {
 'KT_4.6': (KT_LO, 0, 0), 'KT_8.2': (KT_HI, 0, 0),
 'G_7.5': (0, G_C, 0), 'G_19': (0, G_HI, 0),
 'Q4_flat': (0, 0, DQ4_C), 'Q4_seasonal': (0, 0, DQ4_HI),
 'COMBO_center': (P['KT'][0] * KT_LO, P['G'][0] * G_C, P['Q4'][0] * DQ4_C),
 'COMBO_low': (P['KT'][2] * KT_HI, P['G'][2] * G_HI, P['Q4'][1] * 0.0),
 'COMBO_high': (P['KT'][1] * KT_LO, P['G'][1] * G_LO, P['Q4'][2] * DQ4_HI),
}
res = {}
for lab, (kt, g, dq) in cases.items():
    _, x = run(kt, g, dq); s = x['post']
    res[lab] = dict(KT=round(kt, 5), G=round(g, 4), DQ4=round(dq, 4), center=round(s['mean']), p10=round(s['p10']), p90=round(s['p90']),
                    d_vnd=round(s['mean'] - C0), d_pct=round((s['mean'] / C0 - 1) * 100, 3))
_ = run(0.0, 0.0, 0.0)  # trả output gốc
assert md5(os.path.join(CALC, 'nnc_redo_r3_out.json')) == '02a4e6ca744e2390367103f7296e12be'
out = dict(control_center=round(C0), control_stdout_md5='857c7adb3a319e2a819cbfa4de08caa4', p=P, cases=res)
json.dump(out, open(os.path.join(HERE, 'rerun_combo_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
print(json.dumps(out, ensure_ascii=False, sort_keys=True))
