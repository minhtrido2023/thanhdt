# -*- coding: utf-8 -*-
"""Selfcheck knob DCF_RATE_FRAME (job Taylor_20261030_041731). Chạy: $DNA_PYEXE dcf_rate_frame_selfcheck.py
(a) knob mặc định / =legacy ⇒ fair_value/MoS/status/robust toàn rổ universe_pit asof 2026-10-29 TRÙNG BYTE với
    dcf_valuation.py của main (/home/trido/thanhdt/WorkingClaude).
(b) =domestic_v2 ⇒ khớp mô phỏng nghiên cứu (out_imp_asof_per_ticker.csv cột mos_N_c/st_N_c/rb_N_c).
(c) DGC tầng A r7 21.407/32.925/41.779 (EV 29.817) tái lập — model_ke.py KHÔNG import dcf_valuation, nên đây là
    kiểm "số gốc không bị đụng", không phải kiểm knob.
(d) giá trị knob sai ⇒ ValueError lúc import.
Đầu vào bất biến: bản chụp tài chính + rổ của nghiên cứu (đường dẫn RES dưới)."""
import os, sys, json, subprocess, hashlib, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = "/home/trido/thanhdt/WorkingClaude/dcf_valuation.py"
WT = os.path.join(HERE, "dcf_valuation.py")
RES = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/erp_domestic_v2_20261030"
SNAP = os.path.join(RES, "..", "erp_domestic_20261030", "data", "snap_universe_pit_qe.csv")
ASOF = "2026-10-29"


def driver(path):
    import pandas as pd
    spec = importlib.util.spec_from_file_location("dcfv_under_test", path)
    D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)
    fin = pd.read_parquet(os.path.join(RES, "data", "fin_snapshot.parquet")); fin["time"] = pd.to_datetime(fin.time)
    fm = {t: g.reset_index(drop=True) for t, g in fin.groupby("ticker")}
    s = pd.read_csv(SNAP); s = s[(s.time == ASOF) & s.Price.notna()]
    out = []
    for r in s.itertuples():
        if r.ticker not in fm:
            out.append([r.ticker, "no_fin"]); continue
        x = D.fair_value(r.ticker, pd.Timestamp(ASOF), price=float(r.Price), fin=fm[r.ticker])
        if not x["ok"]:
            out.append([r.ticker, x["reason"]]); continue
        st, rb = D.classify_dcf(x["margin_of_safety"], x["sensitivity"], float(r.Price))
        out.append([r.ticker, repr(x["fair_value_ps"]), repr(x["margin_of_safety"]), st, rb,
                    repr(x["discount_rate"]), repr(x["g_terminal"])])
    print(json.dumps(out))


def run(path, frame):
    env = dict(os.environ)
    env.pop("DCF_RATE_FRAME", None)
    if frame is not None:
        env["DCF_RATE_FRAME"] = frame
    p = subprocess.run([sys.executable, __file__, "--driver", path], capture_output=True, text=True, env=env)
    return p


def main():
    fails = []
    def check(name, cond, detail=""):
        print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")
        if not cond:
            fails.append(name)
    base = run(MAIN, None); assert base.returncode == 0, base.stderr[-500:]
    h = lambda p: hashlib.md5(p.stdout.encode()).hexdigest()
    rows = json.loads(base.stdout)
    n_ok = sum(1 for r in rows if len(r) == 7)
    check("(a0) main chạy được", n_ok > 100, f"n={len(rows)} ok={n_ok} md5={h(base)}")
    for fr in (None, "legacy"):
        w = run(WT, fr)
        check(f"(a) worktree DCF_RATE_FRAME={fr} trùng byte main", w.returncode == 0 and w.stdout == base.stdout, f"md5={h(w)}")
    v2 = run(WT, "domestic_v2"); assert v2.returncode == 0, v2.stderr[-500:]
    import pandas as pd
    sim = pd.read_csv(os.path.join(RES, "out_imp_asof_per_ticker.csv")).set_index("ticker")
    got = {r[0]: r for r in json.loads(v2.stdout) if len(r) == 7}
    bad = []
    for tk, s in sim.iterrows():
        g = got.get(tk)
        if g is None or round(float(g[2]), 4) != round(float(s.mos_N_c), 4) or g[3] != s.st_N_c or bool(g[4]) != bool(s.rb_N_c):
            bad.append(tk)
    check("(b) domestic_v2 khớp mô phỏng nghiên cứu (MoS 4 chữ số, status, robust)", not bad and len(got) == len(sim),
          f"n_sim={len(sim)} n_v2={len(got)} lệch={bad[:5]}")
    rs = {round(float(r[5]), 10) for r in got.values()}; gs = {round(float(r[6]), 10) for r in got.values()}
    check("(b2) domestic_v2 r = 12,25% hằng, g_T ≤ 5,5%", rs == {0.1225} and max(gs) <= 0.055, f"r={rs} g_T={sorted(gs)[:3]}")
    spec = importlib.util.spec_from_file_location("mke", os.path.join(RES, "..", "dgc_discount_rate_20261029", "model_ke.py"))
    K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)
    A = K.run_cfg(K.M.CFG_A, K.KE_R7)
    check("(c) DGC r7 21407/32925/41779/29817", (A["dcf_nghich"], A["dcf_coso"], A["dcf_thuan"], A["ev"]) == (21407, 32925, 41779, 29817),
          str((A["dcf_nghich"], A["dcf_coso"], A["dcf_thuan"], A["ev"])))
    bogus = run(WT, "domestic")
    check("(d) knob sai ⇒ ValueError", bogus.returncode != 0 and "DCF_RATE_FRAME" in bogus.stderr)
    print("SELFCHECK", "OK" if not fails else f"FAIL {fails}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--driver":
        driver(sys.argv[2])
    else:
        main()
