# -*- coding: utf-8 -*-
"""Selfcheck knob DCF_RATE_FRAME (job Taylor_20261030_041731; hardening Taylor_20261030_050926 — 5 điều kiện
quant-skeptic trước khi bật domestic_v2, logs/verify_20261030_044415_*.log). Chạy: $DNA_PYEXE dcf_rate_frame_selfcheck.py
(a) DCF_RATE_FRAME=legacy ⇒ fair_value/MoS/status/robust toàn rổ universe_pit asof 2026-10-29 TRÙNG BYTE với dcf_valuation.py
    của main (/home/trido/thanhdt/WorkingClaude) — rollback 1 từ là thật.
(b) mặc định (không env) = RATE_FRAME_DEFAULT; =domestic_v2 khớp mô phỏng nghiên cứu (out_imp_asof_per_ticker.csv).
(c) DGC tầng A r7 21.407/32.925/41.779 (EV 29.817) tái lập (model_ke.py KHÔNG import dcf_valuation: "số gốc không bị đụng").
[1] domestic_v2 ép cap_rf: env DCF_TERMINAL_MODE≠cap_rf bị bỏ qua + kêu; term_mode≠cap_rf tường minh ⇒ ValueError;
    legacy vẫn tôn trọng DCF_TERMINAL_MODE.
[2] knob gõ sai ⇒ KHÔNG raise, fallback legacy (trùng byte (a)) + kêu stderr; khối CHECKDCFRF của ops_health_check.sh WARN.
[3] MỘT nguồn sự thật: không launcher/cron/wc_env.sh/script nào gán biến khung; import dưới mọi kiểu khởi chạy
    (env -i kiểu cron, source wc_env.sh, python3 hệ thống, venv, TZ khác) đều thấy cùng frame = RATE_FRAME_DEFAULT.
[4] dcf_earning_power cap_rf = production (legacy trùng float; v2 dùng cap 5,5 chứ không 5,75).
[5] hiển thị r dưới domestic_v2 mang khoảng Ke 12,5–13,5% (β1,1); [5b] cả CLI dcf_earning_power.
[M] mutation: mỗi vá ở [1][2][4][5] bị gỡ ⇒ đúng check tương ứng đỏ.
Đầu vào bất biến: bản chụp tài chính + rổ của nghiên cứu (RES). ops_health_check.sh: env DCF_RF_OPS_HEALTH (mặc định main)."""
import os, sys, json, re, subprocess, hashlib, importlib.util, tempfile, shutil, glob, io, contextlib, atexit

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = "/home/trido/thanhdt/WorkingClaude"
MAIN = os.path.join(PROD, "dcf_valuation.py")
WT = os.path.join(HERE, "dcf_valuation.py")
EPF = os.path.join(HERE, "dcf_earning_power.py")
RES = os.path.join(PROD, "mike/agents/Taylor/research/erp_domestic_v2_20261030")
SNAP = os.path.join(RES, "..", "erp_domestic_20261030", "data", "snap_universe_pit_qe.csv")
OPS = os.environ.get("DCF_RF_OPS_HEALTH", os.path.join(PROD, "mike/bin/ops_health_check.sh"))
VENV = "/home/trido/thanhdt/wc_venv/bin/python"
ASOF = "2026-10-29"
SHOUT = "!!!!! [dcf_valuation]"
_TMPDIRS = []


def _mkdtemp(prefix):
    """tempfile.mkdtemp + đăng ký dọn khi thoát (kể cả sys.exit/assert giữa chừng) — trước đây rò /tmp/dcfrf_*."""
    d = tempfile.mkdtemp(prefix=prefix)
    _TMPDIRS.append(d)
    return d


@atexit.register
def _cleanup_tmp():
    for d in _TMPDIRS:
        shutil.rmtree(d, ignore_errors=True)


def _load(path, name="dcfv_under_test"):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def driver(path):
    import pandas as pd
    D = _load(path)
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


def probe(path, ep_path=None):
    """Cheap per-process view of the frame (no universe run)."""
    import pandas as pd
    D = _load(path)
    sys.modules["dcf_valuation"] = D           # so dcf_earning_power's `import dcf_valuation as D` binds THIS file
    a = pd.Timestamp(ASOF)
    o = {"frame": D.RATE_FRAME, "default": D.RATE_FRAME_DEFAULT, "term_mode": D.DEFAULT_TERM_MODE,
         "r": D.discount_rate(a), "g_T": D.terminal_growth_mode(a), "ke_note": D.ke_range_note()}
    try:
        o["explicit_full"] = D.terminal_growth_mode(a, "cpi_gdp_full")
    except ValueError as e:
        o["explicit_full"] = f"ValueError: {e}"
    import gdp_growth_vn as G
    o["cpi_gdp"] = D.terminal_growth(a) + G.longrun_real_gdp(a)
    if ep_path:
        EP = _load(ep_path, "ep_under_test")
        o["ep_cap_rf"] = EP.terminal_growth_mode(a, "cap_rf")
        try:
            o["ep_full"] = EP.terminal_growth_mode(a, "cpi_gdp_full")
        except ValueError as e:
            o["ep_full"] = f"ValueError: {e}"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        D._print_report({"ok": True, "ticker": "X", "asof": ASOF, "quarter": "q", "base_fcfe_vnd": 1e9,
                         "growth_points": [], "g_explicit_raw": 0.1, "g_explicit": 0.08, "g_terminal_frac_real": 1.0,
                         "discount_rate": o["r"], "g_terminal": o["g_T"], "term_mode": "cap_rf", "oshares": 1e6,
                         "fair_value_ps": 1.0, "price": None,
                         "sensitivity": {k: {"pct": 0.0} for k in ("r-1%", "r+1%", "g-2%", "g+2%")}})
    o["cli"] = buf.getvalue()
    print(json.dumps(o))


def _env(frame=..., term=None, base=None):
    env = dict(os.environ if base is None else base)
    env.pop("DCF_RATE_FRAME", None); env.pop("DCF_TERMINAL_MODE", None)
    if frame is not ...:
        env["DCF_RATE_FRAME"] = frame
    if term is not None:
        env["DCF_TERMINAL_MODE"] = term
    return env


def run(path, frame=..., mode="--driver", term=None, py=None, base=None, extra=()):
    return subprocess.run([py or sys.executable, __file__, mode, path, *extra], capture_output=True, text=True,
                          env=_env(frame, term, base))


def pj(p):
    assert p.returncode == 0, p.stderr[-800:]
    return json.loads(p.stdout.strip().splitlines()[-1])


def mutant(src_path, old, new, tag):
    s = open(src_path, encoding="utf-8").read()
    assert s.count(old) == 1, f"mutant {tag}: anchor not unique/absent"
    d = _mkdtemp(f"dcfrf_{tag}_")
    p = os.path.join(d, os.path.basename(src_path))
    open(p, "w", encoding="utf-8").write(s.replace(old, new))
    return p


def ops_block():
    src = open(OPS, encoding="utf-8").read()
    m = re.search(r"^# CHECKDCFRF_BEGIN.*?\n(.*?)^# CHECKDCFRF_END", src, re.S | re.M)
    return m.group(1) if m else None


def run_ops(block, wc_root, env_val=None, crontab=""):
    lines, warn = [], [0]

    class _SP:                                  # stub subprocess: crontab -l => given text
        @staticmethod
        def run(*a, **k):
            return type("R", (), {"stdout": crontab, "returncode": 0})()
    old = os.environ.pop("DCF_RATE_FRAME", None)
    if env_val is not None:
        os.environ["DCF_RATE_FRAME"] = env_val
    try:
        ns = {"os": os, "re": re, "glob": glob, "subprocess": _SP, "wc_root": wc_root, "account": "SpaceX",
              "runonce_label": "SpaceX", "lines": lines,
              "W": lambda m: (warn.__setitem__(0, warn[0] + 1), lines.append("⚠️ " + m)),
              "OK": lambda m: lines.append("✅ " + m)}
        exec(block, ns)
    finally:
        os.environ.pop("DCF_RATE_FRAME", None)
        if old is not None:
            os.environ["DCF_RATE_FRAME"] = old
    return warn[0], lines


def fake_root(default_line, wc_env_extra="", sh_extra="", extra=None):
    d = _mkdtemp("dcfrf_root_")
    os.makedirs(os.path.join(d, "mike", "bin"))
    for rel, txt in (extra or {}).items():
        os.makedirs(os.path.dirname(os.path.join(d, rel)), exist_ok=True)
        open(os.path.join(d, rel), "w").write(txt)
    open(os.path.join(d, "dcf_valuation.py"), "w").write(f"# DCF_RATE_FRAME knob\n{default_line}\n")
    open(os.path.join(d, "wc_env.sh"), "w").write("export TZ=Asia/Ho_Chi_Minh\n" + wc_env_extra)
    open(os.path.join(d, "mike", "bin", "x.sh"), "w").write("#!/bin/bash\n# DCF_RATE_FRAME=legacy (comment ok)\n" + sh_extra)
    return d


def main():
    fails = []

    def check(name, cond, detail=""):
        print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")
        if not cond:
            fails.append(name)
    h = lambda p: hashlib.md5(p.stdout.encode()).hexdigest()
    src = open(WT, encoding="utf-8").read()
    dflt = re.search(r'^RATE_FRAME_DEFAULT\s*=\s*"([^"]*)"', src, re.M).group(1)
    print(f"RATE_FRAME_DEFAULT (nguồn sự thật) = {dflt!r}")

    # ---- (a) legacy == main byte-for-byte ----------------------------------------------------------
    # Post-merge (30/10 12:48 ICT) main's DEFAULT is domestic_v2, so the pre-knob baseline is main under
    # DCF_RATE_FRAME=legacy, anchored to the pinned md5 of the ORIGINAL pre-knob main output.
    LEG_MD5 = "4c0cf6e6ee6b267937c793c7dfda9a44"
    base = run(MAIN, "legacy"); assert base.returncode == 0, base.stderr[-500:]
    rows = json.loads(base.stdout)
    n_ok = sum(1 for r in rows if len(r) == 7)
    check("(a0) main chạy được", n_ok > 100, f"n={len(rows)} ok={n_ok} md5={h(base)}")
    check("(a-pin) main legacy == md5 ghim của main trước khi có knob", h(base) == LEG_MD5, f"md5={h(base)}")
    leg = run(WT, "legacy")
    check("(a) worktree DCF_RATE_FRAME=legacy trùng byte main", leg.returncode == 0 and leg.stdout == base.stdout,
          f"md5={h(leg)}")
    check("(a') env legacy kêu 'override' đúng khi mặc định khác legacy",
          (SHOUT in leg.stderr) == (dflt != "legacy"))

    # ---- (b) default == RATE_FRAME_DEFAULT; v2 == research simulation -------------------------------
    v2 = run(WT, "domestic_v2"); assert v2.returncode == 0, v2.stderr[-500:]
    dfl = run(WT); assert dfl.returncode == 0, dfl.stderr[-500:]
    check(f"(b0) không env ⇒ trùng byte frame mặc định {dflt}, không kêu",
          dfl.stdout == (v2 if dflt == "domestic_v2" else leg).stdout and SHOUT not in dfl.stderr, f"md5={h(dfl)}")
    import pandas as pd
    sim = pd.read_csv(os.path.join(RES, "out_imp_asof_per_ticker.csv")).set_index("ticker")
    got = {r[0]: r for r in json.loads(v2.stdout) if len(r) == 7}
    bad = [tk for tk, s in sim.iterrows() if (g := got.get(tk)) is None or round(float(g[2]), 4) != round(float(s.mos_N_c), 4)
           or g[3] != s.st_N_c or bool(g[4]) != bool(s.rb_N_c)]
    check("(b) domestic_v2 khớp mô phỏng nghiên cứu (MoS 4 chữ số, status, robust)", not bad and len(got) == len(sim),
          f"n_sim={len(sim)} n_v2={len(got)} lệch={bad[:5]} md5={h(v2)}")
    rs = {round(float(r[5]), 10) for r in got.values()}; gs = {round(float(r[6]), 10) for r in got.values()}
    check("(b2) domestic_v2 r = 12,25% hằng, g_T ≤ 5,5%", rs == {0.1225} and max(gs) <= 0.055, f"r={rs} g_T max={max(gs)}")

    # ---- (c) DGC research numbers untouched --------------------------------------------------------
    K = _load(os.path.join(RES, "..", "dgc_discount_rate_20261029", "model_ke.py"), "mke")
    A = K.run_cfg(K.M.CFG_A, K.KE_R7)
    check("(c) DGC r7 21407/32925/41779/29817", (A["dcf_nghich"], A["dcf_coso"], A["dcf_thuan"], A["ev"]) == (21407, 32925, 41779, 29817),
          str((A["dcf_nghich"], A["dcf_coso"], A["dcf_thuan"], A["ev"])))

    # ---- [1] domestic_v2 forces cap_rf ---------------------------------------------------------------
    def c1(path):
        p_ok = pj(run(path, "domestic_v2", "--probe"))
        p = run(path, "domestic_v2", "--probe", term="cpi_gdp_full")
        if p.returncode != 0:                   # env-mode crash = per-ticker ValueError => NOT_COMPUTED flood
            return False, False, {"term_mode": f"CRASH rc={p.returncode}", "g_T": float("nan"),
                                  "explicit_full": p.stderr.strip().splitlines()[-1][:90]}
        q = pj(p)
        ok_env = q["term_mode"] == "cap_rf" and q["g_T"] == p_ok["g_T"] and q["r"] == 0.1225 and SHOUT in p.stderr
        ok_expl = str(q["explicit_full"]).startswith("ValueError")
        return ok_env, ok_expl, q
    ok_env, ok_expl, q = c1(WT)
    check("[1a] v2 + env DCF_TERMINAL_MODE=cpi_gdp_full ⇒ ép cap_rf (g_T như mặc định, r 12,25) + kêu stderr", ok_env,
          f"term_mode={q['term_mode']} g_T={q['g_T']:.4f}")
    check("[1b] v2 + term_mode='cpi_gdp_full' tường minh ⇒ ValueError", ok_expl, str(q["explicit_full"])[:90])
    ql = pj(run(WT, "legacy", "--probe", term="cpi_gdp_full"))
    check("[1c] legacy vẫn tôn trọng DCF_TERMINAL_MODE (ép chỉ áp cho v2)",
          ql["term_mode"] == "cpi_gdp_full" and abs(ql["g_T"] - ql["cpi_gdp"]) < 1e-12, f"g_T={ql['g_T']:.4f}")

    # ---- [2] typo ⇒ fallback legacy, loud; ops_health WARNs ------------------------------------------
    def c2(path):
        p = run(path, "domestic")
        return p.returncode == 0 and p.stdout == base.stdout and SHOUT in p.stderr and "KHONG HOP LE" in p.stderr, p
    ok2, p2 = c2(WT)
    check("[2a] DCF_RATE_FRAME='domestic' (gõ sai) ⇒ rc 0, KHÔNG NOT_COMPUTED, trùng byte legacy, kêu stderr", ok2,
          f"rc={p2.returncode} md5={h(p2)} stderr={p2.stderr.strip().splitlines()[0][:110] if p2.stderr.strip() else ''!r}")
    p2b = pj(run(WT, " ", "--probe"))
    check("[2b] DCF_RATE_FRAME rỗng/space ⇒ mặc định nguồn sự thật", p2b["frame"] == dflt)
    def c2k(path):
        pr = run(path, mode="--probe")
        return pr.returncode == 0 and pj(pr)["frame"] == "legacy" and "KHONG HOP LE" in pr.stderr, pr
    mk = mutant(WT, 'RATE_FRAME_DEFAULT = "domestic_v2"\n', 'RATE_FRAME_DEFAULT = "domestic-v2"\n', "n1")
    check("[2k] hằng RATE_FRAME_DEFAULT gõ sai ⇒ fallback legacy + kêu stderr (không im lặng)", c2k(mk)[0],
          c2k(mk)[1].stderr.strip()[:110])
    blk = ops_block()
    check("[2c] ops_health_check.sh có khối CHECKDCFRF", blk is not None, OPS)
    if blk:
        good = fake_root(f'RATE_FRAME_DEFAULT = "{dflt}"')
        w0, l0 = run_ops(blk, good)
        check("[2d] ops_health: sạch ⇒ 0 WARN, 1 OK nêu frame", w0 == 0 and any(dflt in x for x in l0), str(l0)[:140])
        w1, l1 = run_ops(blk, good, env_val="domestc")
        check("[2e] ops_health: env gõ sai ⇒ WARN 'KHÔNG HỢP LỆ'", w1 == 1 and "KHÔNG HỢP LỆ" in l1[0], str(l1)[:160])
        w2, l2 = run_ops(blk, fake_root('RATE_FRAME_DEFAULT = "domestic-v2"'))
        check("[2f] ops_health: RATE_FRAME_DEFAULT sai giá trị ⇒ WARN", w2 == 1, str(l2)[:160])
        w3, l3 = run_ops(blk, fake_root(f'RATE_FRAME_DEFAULT = "{dflt}"', wc_env_extra="export DCF_RATE_FRAME=legacy\n"))
        check("[2g] ops_health: wc_env.sh gán DCF_RATE_FRAME ⇒ WARN launcher", w3 == 1 and "wc_env.sh" in l3[0], str(l3)[:160])
        w4, l4 = run_ops(blk, good, crontab="5 2 * * 1-5 DCF_TERMINAL_MODE=cpi /x/run_bot.sh\n# 0 1 * * * DCF_RATE_FRAME=x y\n")
        check("[2h] ops_health: crontab gán DCF_TERMINAL_MODE ⇒ WARN (dòng comment bỏ qua)", w4 == 1 and "crontab" in l4[0]
              and l4[0].count("crontab:") == 1, str(l4)[:160])
        w5, l5 = run_ops(blk, fake_root(f'RATE_FRAME_DEFAULT = "{dflt}"', sh_extra='cd x && DCF_RATE_FRAME=legacy python3 a.py\n'))
        check("[2i] ops_health: mike/bin/*.sh gán inline ⇒ WARN", w5 == 1 and "x.sh" in l5[0], str(l5)[:160])
        PYSET = 'import os\nos.environ.setdefault("DCF_RATE_FRAME", "legacy")\n'
        fr = lambda **kw: fake_root(f'RATE_FRAME_DEFAULT = "{dflt}"', **kw)
        w7, l7 = run_ops(blk, fr(extra={"run_x.sh": "#!/bin/bash\nDCF_RATE_FRAME=legacy python3 a.py\n"}))
        check("[2j] ops_health: WorkingClaude/*.sh gán inline ⇒ WARN", w7 == 1 and "run_x.sh" in l7[0], str(l7)[:160])
        w8, l8 = run_ops(blk, fr(extra={"trading_bot/b.py": PYSET}))
        check("[2l] ops_health: trading_bot/*.py setdefault biến khung ⇒ WARN", w8 == 1 and "trading_bot/b.py" in l8[0], str(l8)[:160])
        w9, l9 = run_ops(blk, fr(extra={"trading_bot/r.sh": "export DCF_TERMINAL_MODE=cpi\n"}))
        check("[2m] ops_health: trading_bot/*.sh export biến mode ⇒ WARN", w9 == 1 and "trading_bot/r.sh" in l9[0], str(l9)[:160])
        w10, l10 = run_ops(blk, fr(extra={"mike/bin/p.py": 'os.environ["DCF_TERMINAL_MODE"] = "cpi"\n'}))
        check("[2n] ops_health: mike/bin/*.py gán os.environ[...]= ⇒ WARN", w10 == 1 and "mike/bin/p.py" in l10[0], str(l10)[:160])
        w11, l11 = run_ops(blk, fr(extra={"x_selfcheck.py": PYSET, "test_x.py": PYSET, "dcf_earning_power.py": PYSET,
                                          "dcf_valuation.py": PYSET + "RATE_FRAME_DEFAULT = \"%s\"\n" % dflt,
                                          "trading_bot/c.py": "# os.environ.setdefault('DCF_RATE_FRAME', 'x')\n"}))
        check("[2o] ops_health: selfcheck/test_/dcf_earning_power/dcf_valuation + dòng comment KHÔNG gây WARN",
              w11 == 0, str(l11)[:160])
        bm_sh = blk.replace('glob.glob(os.path.join(wc_root, "*.sh")) + ', '', 1)
        bm_tb = blk.replace(' + glob.glob(os.path.join(wc_root, "trading_bot", "*.py"))', '', 1)
        bm_py = blk.replace('if not _ln.lstrip().startswith("#") and (_rf_pat_py if _is_py else _rf_pat).search(_ln)',
                            'if not _ln.lstrip().startswith("#") and _rf_pat.search(_ln)', 1)
        assert bm_sh != blk and bm_tb != blk and bm_py != blk, "mutation anchor trôi"
        check("[M2j] gỡ quét WorkingClaude/*.sh ⇒ [2j] đỏ", run_ops(bm_sh, fr(extra={"run_x.sh": "DCF_RATE_FRAME=legacy x\n"}))[0] == 0)
        check("[M2l] gỡ quét trading_bot/*.py ⇒ [2l] đỏ", run_ops(bm_tb, fr(extra={"trading_bot/b.py": PYSET}))[0] == 0)
        check("[M2n] bỏ regex python (dùng regex shell cho .py) ⇒ [2n] đỏ",
              run_ops(bm_py, fr(extra={"mike/bin/p.py": 'os.environ["DCF_TERMINAL_MODE"] = "cpi"\n'}))[0] == 0)
        w6, l6 = run_ops(blk, PROD)
        print(f"INFO ops_health trên cây PROD hiện tại (trước merge dcf_valuation): warn={w6} {l6}")

    # ---- [3] one source of truth -------------------------------------------------------------------
    pat_sh = re.compile(r"(^|[\s;&|(])(export\s+)?DCF_(RATE_FRAME|TERMINAL_MODE)=")       # shell / crontab assignment
    pat_py = re.compile(r"environ\[\s*['\"]DCF_(RATE_FRAME|TERMINAL_MODE)['\"]\s*\]\s*=|"   # python setting the env
                        r"(setdefault|putenv)\(\s*['\"]DCF_(RATE_FRAME|TERMINAL_MODE)|['\"]DCF_(RATE_FRAME|TERMINAL_MODE)['\"]\s*:")
    scan = [os.path.join(PROD, "wc_env.sh")]
    for root in (PROD, HERE):
        scan += glob.glob(os.path.join(root, "*.py")) + glob.glob(os.path.join(root, "*.sh")) \
            + glob.glob(os.path.join(root, "trading_bot", "*.py"))
    scan += glob.glob(os.path.join(PROD, "mike", "bin", "*.sh")) + glob.glob(os.path.join(PROD, "mike", "bin", "*.py"))
    hits = []
    for f in sorted(set(scan)):
        if "selfcheck" in os.path.basename(f) or os.path.basename(f) in ("ops_health_check.sh", "dcf_rate_robustness.py"):
            continue                            # dcf_rate_robustness.py = nghiên cứu cố ý ghim legacy (cùng danh sách loại với ops_health)
        pat = pat_py if f.endswith(".py") else pat_sh
        for i, ln in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
            if not ln.lstrip().startswith("#") and pat.search(ln):
                hits.append(f"{f}:{i}: {ln.strip()[:80]}")
    ct = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
    hits += [f"crontab: {ln[:80]}" for ln in ct.splitlines() if not ln.lstrip().startswith("#") and pat_sh.search(ln)]
    check("[3a0] đối chứng dương: regex quét bắt được gán shell/crontab + python env (không thì [3a] rỗng nghĩa)",
          all(pat_sh.search(x) for x in ("export DCF_RATE_FRAME=legacy", "5 2 * * * cd /x && DCF_TERMINAL_MODE=cpi y"))
          and all(pat_py.search(x) for x in ('os.environ["DCF_RATE_FRAME"] = "legacy"', "os.environ.setdefault('DCF_TERMINAL_MODE', 'cpi')",
                                             'env={"DCF_RATE_FRAME": "legacy"}'))
          and not pat_py.search("    DCF_TERMINAL_MODE=cap_rf clamps g_term at r_f."))
    check("[3a] không launcher/cron/wc_env.sh/script production nào gán DCF_RATE_FRAME/DCF_TERMINAL_MODE",
          not hits, f"quét {len(set(scan))} file + crontab; hits={hits[:4]}")
    cronlike = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/home/trido"), "SHELL": "/bin/sh"}
    views = {}
    for label, py, b in (("cron env -i + python3 hệ thống", "/usr/bin/python3", cronlike),
                         ("cron env -i + venv", VENV, cronlike),
                         ("cron env -i, TZ=Pacific/Kiritimati", VENV, dict(cronlike, TZ="Pacific/Kiritimati")),
                         ("env phiên này (venv)", VENV, None)):
        p = run(WT, ..., "--probe", py=py, base=b)
        views[label] = (pj(p)["frame"] if p.returncode == 0 else f"rc={p.returncode}:{p.stderr[-120:]}", SHOUT in p.stderr)
    wcenv = subprocess.run(["bash", "-c", f'source {PROD}/wc_env.sh >/dev/null 2>&1; exec "$DNA_PYEXE" {__file__} --probe {WT}'],
                           capture_output=True, text=True, env=_env(..., base=cronlike))
    views["source wc_env.sh (DNA_PYEXE)"] = (pj(wcenv)["frame"] if wcenv.returncode == 0 else f"rc={wcenv.returncode}",
                                              SHOUT in wcenv.stderr)
    check(f"[3b] mọi kiểu khởi chạy thấy CÙNG frame = {dflt}, không cảnh báo", all(v == (dflt, False) for v in views.values()),
          json.dumps(views, ensure_ascii=False))

    # ---- [4] dcf_earning_power cap_rf ----------------------------------------------------------------
    def c4(dpath, eppath):
        pl = pj(run(dpath, "legacy", "--probe", extra=(eppath,)))
        pv = pj(run(dpath, "domestic_v2", "--probe", extra=(eppath,)))
        return (pl["ep_cap_rf"] == pl["g_T"], abs(pv["ep_cap_rf"] - min(pv["cpi_gdp"], 0.055)) < 1e-12), pl, pv
    (ok4l, ok4v), pl, pv = c4(WT, EPF)
    check("[4a] earning_power cap_rf legacy == production (cùng float)", ok4l, f"{pl['ep_cap_rf']!r} vs {pl['g_T']!r}")
    check("[4b] earning_power cap_rf v2 == min(cpi+gdp, 5,5%) (không phải 5,75)", ok4v, f"{pv['ep_cap_rf']!r}")

    def c4c(dpath, eppath):
        pl = pj(run(dpath, "legacy", "--probe", extra=(eppath,)))
        pv = pj(run(dpath, "domestic_v2", "--probe", extra=(eppath,)))
        return (isinstance(pl["ep_full"], float) and abs(pl["ep_full"] - pl["cpi_gdp"]) < 1e-12,
                isinstance(pv["ep_full"], str) and pv["ep_full"].startswith("ValueError")), pl, pv
    (ok4cl, ok4cv), pl4, pv4 = c4c(WT, EPF)
    check("[4c] earning_power mode≠cap_rf: legacy vẫn chạy (cpi_gdp_full), v2 ⇒ ValueError (không đổi riêng r)",
          ok4cl and ok4cv, f"legacy={pl4['ep_full']!r} v2={str(pv4['ep_full'])[:60]!r}")

    # ---- [5] Ke range in display -------------------------------------------------------------------
    def c5(path):
        a, b = pj(run(path, "domestic_v2", "--probe")), pj(run(path, "legacy", "--probe"))
        return ("12.5-13.5" in a["cli"] and "KHOANG" in a["cli"] and b["ke_note"] == "" and "KHOANG" not in b["cli"]), a
    ok5, a5 = c5(WT)
    check("[5] CLI r dưới v2 kèm khoảng Ke 12,5–13,5% (β1,1); legacy không đổi", ok5,
          [ln.strip() for ln in a5["cli"].splitlines() if "KHOANG" in ln][:1])

    def c5b(ep_path):                           # CLI dcf_earning_power: r dạng điểm phải mang khoảng Ke dưới v2
        def cli(frame):
            e = _env(frame); e["TZ"] = "UTC"
            return subprocess.run([VENV, ep_path, "FPT", "--asof", ASOF, "--price", "100000", "--term", "cap_rf"],
                                  capture_output=True, text=True, env=e, cwd=os.path.dirname(ep_path))
        a, b = cli("domestic_v2"), cli("legacy")
        n_r = sum("r=12.25%" in ln for ln in a.stdout.splitlines())
        n_k = sum("KHOANG" in ln for ln in a.stdout.splitlines())
        return (a.returncode == 0 and b.returncode == 0 and n_r == 2 and n_k == n_r and "KHOANG" not in b.stdout), (n_r, n_k, a.stderr[-120:])
    ok5b, d5b = c5b(EPF)
    check("[5b] dcf_earning_power CLI: mỗi dòng r= dưới v2 kèm khoảng Ke (2 basis); legacy không đổi", ok5b, str(d5b))

    # ---- [M] mutations: undo each fix ⇒ its check must go red -----------------------------------------
    m1 = mutant(WT, '    DEFAULT_TERM_MODE = "cap_rf"\n', "    pass\n", "m1")
    check("[M1] gỡ ép cap_rf qua env ⇒ [1a] đỏ", not c1(m1)[0])
    m1b = mutant(WT, '    if RATE_FRAME == "domestic_v2" and mode != "cap_rf":\n', '    if False:\n', "m1b")
    check("[M1b] gỡ raise term_mode tường minh ⇒ [1b] đỏ", not c1(m1b)[1])
    m2 = mutant(WT, '        return "legacy", (f"DCF_RATE_FRAME=',
                '        raise ValueError(env_val)\n        return "legacy", (f"DCF_RATE_FRAME=', "m2")
    check("[M2] trả lại ValueError lúc import ⇒ [2a] đỏ", not c2(m2)[0])
    epm = mutant(EPF, '            g = D.terminal_growth_mode(asof, "cap_rf", erp)\n',
                 '            rf = D.discount_rate(asof, erp) - erp / 100.0\n            g = min(cpi + gdp, rf)\n', "m4")
    check("[M4] khôi phục dòng :53 cũ ⇒ [4b] đỏ ([4a] legacy vẫn xanh)", c4(WT, epm)[0] == (True, False))
    m5 = mutant(WT, '    if RATE_FRAME != "domestic_v2":\n        return ""\n    lo, hi',
                '    return ""\n    lo, hi', "m5")
    check("[M5] ke_range_note rỗng ⇒ [5] đỏ", not c5(m5)[0])
    mkm = mutant(mk, '    if default not in RATE_FRAMES:\n', '    if False:\n', "n1m")
    check("[M2k] gỡ guard hằng default ⇒ [2k] đỏ", not c2k(mkm)[0])
    epm2 = mutant(EPF, '    if D.RATE_FRAME == "domestic_v2" and mode != "cap_rf":\n', '    if False:\n', "m4c")
    check("[M4c] gỡ raise của earning_power ⇒ [4c] đỏ (legacy vẫn xanh)", c4c(WT, epm2)[0] == (True, False))
    epm5 = mutant(EPF, '        if D.ke_range_note():\n            print(f"  {D.ke_range_note()}")\n', '', "m5b")
    check("[M5b] gỡ in ke_range_note ở dcf_earning_power ⇒ [5b] đỏ", not c5b(epm5)[0])
    for p in (m1, m1b, m2, epm, m5, mk, mkm, epm2, epm5):
        shutil.rmtree(os.path.dirname(p), ignore_errors=True)

    print("SELFCHECK", "OK" if not fails else f"FAIL {fails}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--driver":
        driver(sys.argv[2])
    elif len(sys.argv) in (3, 4) and sys.argv[1] == "--probe":
        probe(sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else None)
    else:
        main()
