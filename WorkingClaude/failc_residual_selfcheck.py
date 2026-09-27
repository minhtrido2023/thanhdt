#!/usr/bin/env python3
"""Selfcheck cho 2 ton du FAIL-C (job Taylor_20260927_100121).

Doi tuong:
  (1) deploy_golive_dt5g_v4/golive_recommend_v23.py::w_lag_target — DUONG LIVE, phai index
      tren `known_date`, va phai FALLBACK sang `entry` + canh bao khi thieu cot (khong crash,
      khong fail-closed: day la allocator tien that).
  (2) edge_health_monitor.py::neg_month_streak — neg_streak phai neo `known_date`, khong `entry`.

Ky luat (coding_guidelines §19 + skill verify-before-done):
  * MUTATION: doi nhan ve `entry` thi test phai CHET. Khong chet = test khong do gi.
  * 3 TZ: chay lai toan bo duoi UTC / Asia/Ho_Chi_Minh / America/New_York (+ `env -u TZ`
    o wrapper) — logic ngay/thang cua resample('ME') va asof() phu thuoc nhan ngay, nen
    bat ky lech TZ nao la mot finding.

Chay:  $DNA_PYEXE failc_residual_selfcheck.py            # 1 TZ (TZ hien hanh)
       $DNA_PYEXE failc_residual_selfcheck.py --all-tz   # spawn lai chinh minh o 3 TZ + env -u TZ
"""
import os, sys, subprocess, tempfile, textwrap, importlib.util

WC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC)
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")   # §5b: khong bao gio ban event ra bus tu selfcheck

import numpy as np
import pandas as pd

N_ASSERT = 0
FAILS = []


def ck(cond, msg):
    global N_ASSERT
    N_ASSERT += 1
    if not cond:
        FAILS.append(msg)
        print(f"  FAIL: {msg}")
    return bool(cond)


# ----------------------------------------------------------------------------- fixture
# Bang DUNG TAY, khong sinh may moc: de 2 truc nhan THUC SU khong dong y thi phai co dau
# mean12 XEN KE quanh ranh gioi thang — buoc lui 25 phien lam DOI dong nao la "dong cuoi thang".
# Mot chuoi dang bac thang (duong roi am) KHONG phan biet duoc 2 nhan (thu roi: entry=3,
# known_date=3) — do la ly do co guard `ns_entry != ns_known` ben duoi.
#
#   entry        known_date (~entry+25 phien)   mean12
#   2026-03-05   2026-04-09                     +4.0
#   2026-04-06   2026-05-11                     +4.0
#   2026-05-05   2026-06-09                     +3.5
#   2026-06-01   2026-07-06                     +3.0
#   2026-06-28   2026-08-02                     +3.0
#   2026-07-05   2026-08-09                     +1.0
#   2026-07-28   2026-09-01                     -1.0
#   2026-08-05   2026-09-09                     +2.0
#   2026-08-28   2026-10-02                     -1.5
#   2026-09-05   2026-10-10                     -2.0
#
# => thang-cuoi theo `entry`:      06:+3.0  07:-1.0  08:-1.5  09:-2.0  -> neg_streak 3  (VUOT >=3)
# => thang-cuoi theo `known_date`: 08:+1.0  09:+2.0  10:-2.0           -> neg_streak 1  (KHONG vuot)
# Nghia la mutation doi nhan khong chi lam lech con so, no DOI QUYET DINH ha w_LAG.
FIXTURE_ROWS = [
    ("2026-03-05", "2026-04-09", +4.0),
    ("2026-04-06", "2026-05-11", +4.0),
    ("2026-05-05", "2026-06-09", +3.5),
    ("2026-06-01", "2026-07-06", +3.0),
    ("2026-06-28", "2026-08-02", +3.0),
    ("2026-07-05", "2026-08-09", +1.0),
    ("2026-07-28", "2026-09-01", -1.0),
    ("2026-08-05", "2026-09-09", +2.0),
    ("2026-08-28", "2026-10-02", -1.5),
    ("2026-09-05", "2026-10-10", -2.0),
]


def make_fixture(tmpdir, with_known_date=True):
    d = pd.DataFrame({
        "entry": pd.to_datetime([r[0] for r in FIXTURE_ROWS]),
        "known_date": pd.to_datetime([r[1] for r in FIXTURE_ROWS]),
        "ret": [r[2] for r in FIXTURE_ROWS],
        "mean12": [r[2] for r in FIXTURE_ROWS],
        "win12": 40.0, "n12": 100.0,
    })
    if not with_known_date:
        d = d.drop(columns=["known_date"])
    p = os.path.join(tmpdir, "lag_edge_health.csv")
    d.to_csv(p, index=False)
    return p, d


def _gate(d, label, asof, thr=1.0):
    """Cong thuc DUNG cua w_lag_target's edge gate, dung de chon as-of phan biet duoc."""
    e = d.copy()
    e[label] = pd.to_datetime(e[label])
    s = e.drop_duplicates(label).set_index(label).sort_index()["mean12"]
    m = s.asof(pd.Timestamp(asof))
    return (0.65 if (pd.notna(m) and m >= thr) else 0.50), m


def pick_discriminating_asof(d):
    """Tim ngay ma 2 nhan cho w_LAG KHAC nhau, VA ca hai deu co so thuc (khong NaN).

    Yeu cau non-NaN la co y: giai doan dau chuoi, `known_date` chua co du lieu trong khi
    `entry` da co -> 2 nhan cung khac nhau nhung chi vi THIEU DU LIEU, khong phai vi dau
    mean12 xen ke. Ca do la mot discriminator YEU (mutant chet vi ly do tam thuong). Ca manh
    = ca hai nhan deu doc duoc mot so nhung so do KHAC dau so voi nguong.
    """
    lo = pd.Timestamp("2026-04-01"); hi = pd.Timestamp("2026-10-31")
    weak = None
    for day in pd.date_range(lo, hi, freq="D"):
        wk, mk = _gate(d, "known_date", day)
        we, me = _gate(d, "entry", day)
        if wk == we:
            continue
        if pd.notna(mk) and pd.notna(me):
            return day.date(), (wk, mk), (we, me)     # ca MANH
        if weak is None:
            weak = (day.date(), (wk, mk), (we, me))
    if weak:
        print(f"     WARNING: chi tim duoc discriminator YEU (mot ben NaN) tai {weak[0]}")
        return weak
    return None, None, None


# ------------------------------------------------------------------- (2) neg_month_streak
def load_ehm():
    spec = importlib.util.spec_from_file_location(
        "ehm_under_test", os.path.join(WC, "edge_health_monitor.py"))
    m = importlib.util.module_from_spec(spec)
    # edge_health_monitor imports matplotlib/lag_live_schedule at module level; that is fine.
    spec.loader.exec_module(m)
    return m


def test_neg_streak(mutate_label=None):
    """mutate_label='entry' => gia lap bug goc (neo nhan `entry`). Test PHAI chet."""
    print(f"\n[T2] neg_month_streak  (mutate_label={mutate_label!r})")
    ehm = load_ehm()
    tmp = tempfile.mkdtemp(prefix="failc_t2_")
    _, d = make_fixture(tmp, with_known_date=True)

    label = mutate_label or "known_date"
    ns, mo = ehm.neg_month_streak(d, label)
    ns_entry, _ = ehm.neg_month_streak(d, "entry")
    ns_known, _ = ehm.neg_month_streak(d, "known_date")
    print(f"     streak(entry)={ns_entry}  streak(known_date)={ns_known}  used({label})={ns}")

    # Fixture phai THUC SU phan biet duoc 2 nhan — neu khong, test la vo nghia.
    ck(ns_entry != ns_known,
       f"fixture KHONG phan biet duoc nhan (entry={ns_entry}, known_date={ns_known}) "
       f"-> test nay khong do gi, phai sua fixture")
    ck(ns_entry == 3, f"fixture: nhan `entry` phai cho streak 3 (vuot nguong hanh dong), dang {ns_entry}")
    ck(ns_known == 1, f"fixture: nhan `known_date` phai cho streak 1 (khong vuot), dang {ns_known}")
    # DAY la assertion se CHET khi mutate:
    ck(ns == ns_known,
       f"neg_streak phai neo `known_date` (ky vong {ns_known}), nhung nhan dang dung cho "
       f"ket qua {ns} (label={label})")
    ck(ns < 3,
       f"neg_streak dung cho nguong hanh dong phai <3 (khong ha w_LAG); dang {ns} "
       f"-> se HA w_LAG SOM ~1,2 thang")
    return ns


def test_neg_streak_missing_col():
    print("\n[T2b] neg_month_streak: thieu cot known_date -> tra (None, None), KHONG crash")
    ehm = load_ehm()
    tmp = tempfile.mkdtemp(prefix="failc_t2b_")
    _, d = make_fixture(tmp, with_known_date=False)
    try:
        ns, mo = ehm.neg_month_streak(d, "known_date")
        ck(ns is None and mo is None, f"thieu cot phai tra (None, None), dang ({ns}, {mo})")
    except Exception as e:
        ck(False, f"thieu cot lam CRASH: {type(e).__name__}: {e}")


def test_producer_end_to_end_keys():
    """lag_edge_health() tra ve dict co ca 3 key moi — hop dong voi consumer (block MD)."""
    print("\n[T2c] hop dong return dict cua lag_edge_health()")
    src = open(os.path.join(WC, "edge_health_monitor.py"), encoding="utf-8").read()
    for k in ("neg_streak_anchor", "neg_streak_entry_legacy"):
        ck(f"{k}=" in src, f"return dict thieu key `{k}`")
    ck('neg_month_streak(d, "known_date")' in src,
       "lag_edge_health() khong goi neg_month_streak voi nhan `known_date`")
    ck('d.set_index("entry")["mean12"].resample' not in src,
       "VAN CON resample tren nhan `entry` (bug goc) trong edge_health_monitor.py")
    # dong verdict phai noi ro moc
    ck("neg_streak_anchor" in src and "nhan cu 'entry'" in src,
       "dong verdict khong ghi ro moc / khong in so legacy doi chieu")


# --------------------------------------------------------------- (1) LIVE w_lag_target
LIVE_SRC = os.path.join(WC, "deploy_golive_dt5g_v4", "golive_recommend_v23.py")


def extract_w_lag_target(mutate_label=None):
    """Tach nguyen van ham w_lag_target ra module doc lap.

    Vi sao khong `import golive_recommend_v23`: module do keo BQ client + config live ngay o
    import-time. Tach ham ra la cach do DUNG CAI VUA SUA ma khong cham mang/tien that. Doi lai
    phai NEO chat: neu dau ham doi thi extract se fail loud (assert duoi), khong lang le do
    mot ban copy cu.
    """
    src = open(LIVE_SRC, encoding="utf-8").read()
    start = src.index("def w_lag_target(state, asof):")
    end = src.index("\nALLOC_BAND", start)
    body = src[start:end]
    assert "known_date" in body, "extract sai vung: khong thay 'known_date' trong w_lag_target"
    if mutate_label:
        # MUTATION: bo hoan toan nhanh known_date, quay ve bug goc.
        body = body.replace('key = "known_date" if "known_date" in eh.columns else "entry"',
                            'key = "entry"')
        assert 'key = "entry"' in body, "mutation khong ap duoc"
    shim = textwrap.dedent('''
        import os
        import pandas as pd
        WORKDIR = os.environ["FAILC_WORKDIR"]
        EDGE_THR = 1.0
        STATE_LAG_WEIGHT = {1: 0.50, 2: 0.0, 3: 0.65, 4: 0.65, 5: 0.65}
    ''')
    return shim + "\n" + body


def run_live(mod_src, workdir, asof):
    """Chay w_lag_target trong subprocess sach (de mutation khong nhiem sang test khac)."""
    script = mod_src + textwrap.dedent(f'''

        import json, sys
        _out = []
        class _Cap:
            def write(self, s): _out.append(s)
            def flush(self): pass
        _real = sys.stdout
        sys.stdout = _Cap()
        w = w_lag_target(3, "{asof}")
        sys.stdout = _real
        print(json.dumps({{"w": w, "log": "".join(_out)}}))
    ''')
    f = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    f.write(script); f.close()
    env = dict(os.environ, FAILC_WORKDIR=workdir)
    r = subprocess.run([sys.executable, f.name], capture_output=True, text=True, env=env)
    os.unlink(f.name)
    if r.returncode != 0:
        return None, r.stderr[-800:]
    import json
    return json.loads(r.stdout.strip().splitlines()[-1]), None


def test_live(mutate_label=None):
    print(f"\n[T1] LIVE w_lag_target  (mutate_label={mutate_label!r})")
    tmp = tempfile.mkdtemp(prefix="failc_t1_")
    os.makedirs(os.path.join(tmp, "data"), exist_ok=True)
    p, d = make_fixture(tmp, with_known_date=True)
    os.replace(p, os.path.join(tmp, "data", "lag_edge_health.csv"))

    src = extract_w_lag_target(mutate_label)
    asof, exp_known, exp_entry = pick_discriminating_asof(d)
    if not ck(asof is not None,
              "fixture KHONG co ngay nao ma 2 nhan cho w_LAG khac nhau -> test vo nghia"):
        return
    print(f"     as-of={asof}: nhan known_date -> w_LAG {exp_known[0]} (mean12 {exp_known[1]:+.2f}) | "
          f"nhan entry -> w_LAG {exp_entry[0]} (mean12 {exp_entry[1]:+.2f})")

    res, err = run_live(src, tmp, asof)
    if err:
        ck(False, f"chay LIVE that bai: {err}")
        return
    print(f"     w_LAG={res['w']}  log={res['log'].strip()}")

    if not mutate_label:
        ck("label_col=known_date" in res["log"],
           f"log LIVE khong in label_col=known_date: {res['log'].strip()}")
    # Assertion CHINH — chet khi mutate (mutant se tra dung exp_entry[0] != exp_known[0]):
    ck(res["w"] == exp_known[0],
       f"tai as-of={asof} duong LIVE phai dung nhan `known_date` -> w_LAG {exp_known[0]}; "
       f"dang {res['w']} (= ket qua cua nhan `entry` = {exp_entry[0]})")


def test_live_missing_col():
    print("\n[T1b] LIVE thieu cot known_date -> FALLBACK `entry` + canh bao, KHONG crash")
    tmp = tempfile.mkdtemp(prefix="failc_t1b_")
    os.makedirs(os.path.join(tmp, "data"), exist_ok=True)
    p, d = make_fixture(tmp, with_known_date=False)
    os.replace(p, os.path.join(tmp, "data", "lag_edge_health.csv"))
    src = extract_w_lag_target(None)
    asof = d["entry"].max().date()
    res, err = run_live(src, tmp, asof)
    if err:
        ck(False, f"thieu cot lam CRASH duong LIVE: {err}")
        return
    print(f"     w_LAG={res['w']}  log={res['log'].strip()}")
    ck(res["w"] in (0.50, 0.65),
       f"thieu cot phai van tra w_LAG hop le (khong fail-closed ra None), dang {res['w']}")
    ck("thieu cot" in res["log"] and "fallback" in res["log"].lower(),
       f"thieu cot nhung KHONG in canh bao ro rang: {res['log'].strip()}")
    ck("label_col=entry" in res["log"],
       f"log khong noi ro dang dung nhan `entry`: {res['log'].strip()}")


def test_live_real_file_no_regression():
    """Bang chung 0-regression tren FILE THAT: ca 2 nhan cho cung w_LAG hom nay."""
    print("\n[T1c] file THAT: nhan entry vs known_date -> cung w_LAG (0 regression tien that)")
    real = "/home/trido/thanhdt/WorkingClaude"
    fp = os.path.join(real, "data", "lag_edge_health.csv")
    if not os.path.exists(fp):
        print("     SKIP: khong co file that"); return
    eh = pd.read_csv(fp)
    out = {}
    for label in ("entry", "known_date"):
        if label not in eh.columns: continue
        e = eh.copy(); e[label] = pd.to_datetime(e[label])
        s = e.drop_duplicates(label).set_index(label).sort_index()["mean12"]
        m = s.asof(pd.Timestamp("2026-09-27"))
        out[label] = (float(m), 0.65 if m >= 1.0 else 0.50, str(s.index[-1].date()))
    print(f"     {out}")
    ck(out["entry"][1] == out["known_date"][1],
       f"file that: w_LAG lech giua 2 nhan -> KHONG con la va phong ngua benign: {out}")
    ck(out["entry"][2] != out["known_date"][2],
       f"file that: nhan as-of GIONG nhau -> khong chung minh duoc bug nhan: {out}")


# ----------------------------------------------------------------------------- mutation
def mutation_round():
    print("\n" + "=" * 78)
    print("MUTATION: doi nhan ve `entry` (bug goc) — cac test tren PHAI CHET")
    print("=" * 78)
    global FAILS, N_ASSERT
    killed = []
    for name, fn in (("T1 live", lambda: test_live("entry")),
                     ("T2 neg_streak", lambda: test_neg_streak("entry"))):
        saved_f, saved_n = FAILS, N_ASSERT
        FAILS, N_ASSERT = [], 0
        try:
            fn()
        except Exception as e:
            FAILS.append(f"exception: {e}")
        died = len(FAILS) > 0
        killed.append((name, died, len(FAILS)))
        FAILS, N_ASSERT = saved_f, saved_n
        print(f"  -> mutant {name}: {'KILLED' if died else 'SURVIVED (!!!)'} "
              f"({len(killed[-1]) and killed[-1][2]} assertion chet)")
    survived = [n for n, d, _ in killed if not d]
    if survived:
        FAILS.append(f"MUTANT SONG SOT (test khong do gi): {survived}")
    return killed


def main():
    if "--all-tz" in sys.argv:
        rcs = {}
        for tz in ("UTC", "Asia/Ho_Chi_Minh", "America/New_York", None):
            env = dict(os.environ)
            if tz is None:
                env.pop("TZ", None); tzlab = "env -u TZ"
            else:
                env["TZ"] = tz; tzlab = tz
            print("\n" + "#" * 78)
            print(f"# TZ = {tzlab}")
            print("#" * 78)
            r = subprocess.run([sys.executable, os.path.abspath(__file__)],
                               env=env, capture_output=True, text=True)
            print(r.stdout[-6000:])
            if r.returncode != 0:
                print(r.stderr[-2000:])
            rcs[tzlab] = r.returncode
        print("\n" + "=" * 78)
        print("TONG HOP 3 TZ + env -u TZ:", rcs)
        bad = {k: v for k, v in rcs.items() if v != 0}
        print("KET QUA:", "PASS o MOI TZ" if not bad else f"FAIL: {bad}")
        sys.exit(0 if not bad else 1)

    print(f"FAIL-C residual selfcheck | TZ={os.environ.get('TZ', '<unset>')} "
          f"| python={sys.version.split()[0]} | pandas={pd.__version__}")
    test_live(None)
    test_live_missing_col()
    test_live_real_file_no_regression()
    test_neg_streak(None)
    test_neg_streak_missing_col()
    test_producer_end_to_end_keys()
    killed = mutation_round()

    print("\n" + "=" * 78)
    n_mut = len(killed); n_killed = sum(1 for _, d, _ in killed if d)
    print(f"assertion: {N_ASSERT} | mutation: {n_killed}/{n_mut} KILLED | fail: {len(FAILS)}")
    for f in FAILS:
        print("  FAIL:", f)
    print("KET QUA:", "PASS" if not FAILS else "FAIL")
    sys.exit(0 if not FAILS else 1)


if __name__ == "__main__":
    main()
