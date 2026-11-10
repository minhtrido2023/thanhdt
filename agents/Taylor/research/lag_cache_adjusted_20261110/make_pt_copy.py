"""BẢN SAO pt_v22_dt5g.py (main 32d65bbf6, liquidity_require_positive bật) — chỉ đổi: 2 pkl giá, events csv,
output → pt/<tag>_*.csv (§8 non-canonical). Edge-health qua env EDGE_HEALTH_CSV (knob có sẵn).
usage: make_pt_copy.py tag pxpkl ovpkl events_csv"""
import sys, re, subprocess
tag, pxp, ovp, evp = sys.argv[1:5]
WC = "/home/trido/thanhdt/WorkingClaude"; R = __file__.rsplit("/", 1)[0] + "/pt"
src = subprocess.run(["git", "-C", WC, "show", "32d65bbf6:./pt_v22_dt5g.py"], capture_output=True, text=True, check=True).stdout
assert src == open(f"{WC}/pt_v22_dt5g.py").read(), "pt_v22_dt5g.py canonical != 32d65bbf6"
s = src
for a, b in [('open("data/earnings_px.pkl","rb")', f'open(r"{pxp}","rb")'), ('open("data/lagged_pos_ov.pkl","rb")', f'open(r"{ovp}","rb")'),
             ('pd.read_csv("data/earnings_events_classified.csv"', f'pd.read_csv(r"{evp}"')]:
    assert s.count(a) == 1, a; s = s.replace(a, b)
s, k = re.subn(r'os\.path\.join\(WORKDIR, "data", "pt_v22_dt5g_', f'os.path.join(r"{R}", "{tag}_', s)
assert "\"data\", \"pt_v22_dt5g_" not in s, "còn đường ghi canonical?"
open(f"{R}/pt_{tag}.py", "w").write(s); print(tag, "output paths patched", k)
