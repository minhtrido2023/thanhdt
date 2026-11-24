"""DRI recheck 24/11: exec nguyên văn dri_redo_r3.py v2 (md5 89eb0871) trong mirror/ (đầu vào bị TRIM khỏi git, khôi phục từ lịch sử,
md5 khớp LOCK_r3_md5.txt). Chỉ thêm: common.LIQ_CSV trỏ bản trong mirror (đường dẫn tuyệt đối cũ không còn file).
CONTROL: output r3 chạy lại phải TRÙNG BYTE dri_redo_r3_out.txt (6c55c8ed) / .json (09e2c313). Sau đó gọi grid(r=…) cho E15/dải Ke."""
import hashlib, json, os, sys, io, contextlib, builtins
H = os.path.dirname(os.path.abspath(__file__)); M = os.path.join(H, 'mirror'); RED = os.path.join(M, 'dd_redo_20261105'); CD = os.path.join(RED, 'DRI', 'calc')
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
LOCK = {'dd_redo_20261105/DRI/calc/dri_redo_r3.py': '89eb0871234cc59d668642e8814b29d8', 'dd_redo_20261105/DRI/calc/assumptions_r3.json': 'e6a86891ccb46cc731a47f17e3c8e539',
        'dri_val_supply_adj_r4_20261027/model.py': 'e0bba9b8748c6d2891e92c3fa6d7dcd0', 'dri_val_supply_adj_r3_20261027/model.py': 'b68f3311e32df525dad9529ff5dfc94d',
        'dd_redo_20261105/common.py': 'e430be2363c19983d8d83120a3743e98', 'dd_redo_20261105/bq_liq_nnc_mvc_dri_20261104.csv': 'adcfd34d718d70c34cd92fa6ac69f00b',
        'dd_redo_20261105/DRI/calc/r3data/px_dri_20261106.csv': 'd9d72d4a89f68ff5ff45ddd5b4891d4e'}
for f, h in LOCK.items():
    assert md5(os.path.join(M, f)) == h, f
ORIG = {'txt': '6c55c8ed972236a85fe94f568fb46900', 'json': '09e2c313fdc5f925a230f62ff1a46325'}
sys.path.insert(0, RED); import common  # noqa: E402
common.LIQ_CSV = os.path.join(RED, 'bq_liq_nnc_mvc_dri_20261104.csv')
SRC = os.path.join(CD, 'dri_redo_r3.py'); ns = {'__file__': SRC, '__name__': '__main__'}
buf = io.StringIO(); cwd = os.getcwd(); os.chdir(CD)
with contextlib.redirect_stdout(buf):
    exec(compile(open(SRC).read(), SRC, 'exec'), ns)
os.chdir(cwd)
assert md5(os.path.join(M, 'orig_dri_redo_r3_out.json')) == ORIG['json']
_o = json.load(open(os.path.join(M, 'orig_dri_redo_r3_out.json'))); _n = json.load(open(os.path.join(CD, 'dri_redo_r3_out.json')))
_o.pop('files_read'); _n.pop('files_read')   # chỉ khác đường dẫn tuyệt đối mirror vs bản gốc
assert _o == _n, 'CONTROL: output r3 chạy lại lệch bản gốc (ngoài files_read)'
ctl = {'json': 'trùng bản gốc 09e2c313 trừ files_read (đường dẫn)'}
out0 = ns['out']; f = ns['f']; grid, st_ = ns['grid'], ns['st_']
base = dict(center_post=round(out0['post']['mean']), p10=round(out0['post']['p10']), p90=round(out0['post']['p90']), center_pre=round(out0['pre']['mean']), r=ns['R'])
assert (base['center_post'], base['p10'], base['p90']) == (15257, 12908, 17549), base
res = {'control': {'json_md5': ctl['json'], 'match': True}, 'base': base}
for r in (0.123, 0.125, 0.130, 0.134, 0.140, 0.145):
    s = st_(grid(r=r), f); c = s['mean']
    res[f'r{r:.3f}'] = dict(center_post=round(c), p10=round(s['p10']), p90=round(s['p90']), d=round(c - out0['post']['mean']), d_pct=round((c / out0['post']['mean'] - 1) * 100, 2))
res['sens_r_in_r3_out'] = {k: round(v) for k, v in out0['sens_mean_post'].items() if 'lai huy dong' in k}
json.dump(res, open(os.path.join(H, 'calc_recheck_out.json'), 'w'), indent=1)
print(json.dumps(res, indent=1, ensure_ascii=False))
