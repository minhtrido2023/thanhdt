"""SIP recheck 24/11: exec nguyên văn model_r3.py (md5 343f4b43) trong mirror/ (đầu vào bị TRIM khỏi git, khôi phục từ lịch sử,
md5 khớp LOCK_md5.txt r3). CONTROL: output chạy lại trùng bản gốc model_r3_out.json (c78d9b8a, so theo nội dung) + stdout = model_r3_out.txt (e11f6f4b).
Sau đó gọi run(AX, r, disc, PX) cho E15/dải Ke (cùng mô hình, chỉ đổi r)."""
import hashlib, json, os, sys, io, contextlib
H = os.path.dirname(os.path.abspath(__file__)); M = os.path.join(H, 'mirror'); CD = os.path.join(M, 'dd_redo_20261105', 'SIP', 'calc_r3')
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
LOCK = {'SIP/calc_r3/assumptions_r3.json': '627a563f0133692f5889a344813716d4', 'SIP/calc_r3/model_r3.py': '343f4b438861012e335e849616aa1275',
        'SIP/calc_r3/px_sip_r3_20261106.csv': '6bffdef96b53d65916150b72b32a5cbb', '_common_g2r2/ddr2.py': '95d8fe38f5c17c3f723d6c175ffac49b',
        '_common_g2r2/px_g2r2_20261104.csv': '89b5306ea5c456f2f9adbdeec335277b', '_common_g2/ddg2.py': '81a87069f3f895a3a93d62d85b8fb5f0', '_shared/wpct.py': '4597bc083f0d64d8873141b12fbfb3a6'}
for f, h in LOCK.items():
    assert md5(os.path.join(M, 'dd_redo_20261105', f)) == h, f
assert md5(os.path.join(M, 'orig_model_r3_out.json')) == 'c78d9b8a30b2f2ea4f3f8e31cc5b433e' and md5(os.path.join(M, 'orig_model_r3_out.txt')) == 'e11f6f4b796df5c79e0e429143a06a29'
SRC = os.path.join(CD, 'model_r3.py'); ns = {'__file__': SRC, '__name__': '__main__'}; buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(compile(open(SRC).read(), SRC, 'exec'), ns)
assert buf.getvalue() == open(os.path.join(M, 'orig_model_r3_out.txt')).read(), 'CONTROL stdout lệch'
assert json.load(open(os.path.join(CD, 'model_r3_out.json'))) == json.load(open(os.path.join(M, 'orig_model_r3_out.json'))), 'CONTROL json lệch'
run, AX, disc, PX, D = ns['run'], ns['AX'], ns['disc'], ns['PX'], ns['D']
base = dict(r=ns['R0'], center_post=round(D['center_post']), p10=round(D['P_post']['p10']), p90=round(D['P_post']['p90']))
assert (base['center_post'], base['p10'], base['p90']) == (54466, 43257, 69818), base
res = {'control': 'stdout + json trùng bản gốc r3', 'base': base}
for r in (0.123, 0.125, 0.130, 0.134, 0.140, 0.145):
    d = run(AX, r, disc, PX)[1]; c = d['center_post']; pp = d.get('pct') or {}
    res[f'r{r:.3f}'] = dict(center_post=round(c), p10=round(d['P_post']['p10']), p90=round(d['P_post']['p90']), d=round(c - D['center_post']), d_pct=round((c / D['center_post'] - 1) * 100, 2))
res['sens_r_r3'] = {k: round(v['post']) for k, v in ns['sens_r'].items()}
json.dump(res, open(os.path.join(H, 'calc_recheck_out.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
