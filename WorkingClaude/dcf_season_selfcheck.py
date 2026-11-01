# -*- coding: utf-8 -*-
"""
dcf_season_selfcheck.py — selfcheck lịch mùa BCTC + cờ STALE (job Taylor_20261101_181016).
Code under test nạp từ thư mục CẠNH file này (worktree-aware); control = bản canonical WORKDIR.
Chạy: $DNA_PYEXE dcf_season_selfcheck.py   (thử cả `env -u TZ` và TZ=Pacific/Kiritimati). Exit !=0 nếu FAIL.
"""
import os, sys, json, tempfile, importlib.util
from datetime import date, timedelta
HERE = os.path.dirname(os.path.abspath(__file__))
CANON = "/home/trido/thanhdt/WorkingClaude"
fails = []


def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        fails.append(name)


def load(name, base, src_patch=None, alias=None, src=None):
    src = src if src is not None else open(os.path.join(base, name + ".py"), encoding="utf-8").read()
    if src_patch:
        a, b = src_patch
        assert src.count(a) >= 1, f"mutation anchor missing: {a!r}"
        src = src.replace(a, b)
    spec = importlib.util.spec_from_loader(alias or name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = os.path.join(base, name + ".py")
    sys.modules[alias or name] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod


sys.path.insert(0, CANON)
DV = load("dcf_valuation", HERE)                      # code under test (đăng ký là 'dcf_valuation')
GATE = load("dcf_refresh_gate", HERE)                 # gate import `dcf_valuation` => bản HERE ở trên


def slot_battery(G):
    """Trả list (name, ok) cho season_slot — dùng cho cả bản thật và bản đột biến."""
    r = []
    exp = {(2, 5): "early", (2, 15): "full", (5, 5): "early", (5, 15): "full",
           (8, 3): "early", (8, 15): "full", (11, 3): "early", (11, 15): "full"}
    for (m, d), k in exp.items():
        sc, sid, kind, why = G.season_slot(date(2026, m, d), [])
        r.append((f"slot {m:02d}-{d:02d} -> scan {k}", sc and kind == k and sid == f"2026-{m:02d}-{d:02d}:{k}"))
    r.append(("04-01 ngoài cửa sổ -> không quét", G.season_slot(date(2026, 4, 1), [])[0] is False))
    r.append(("02-04 (trước slot) -> không quét", G.season_slot(date(2026, 2, 4), [])[0] is False))
    r.append(("01-31 / 12-31 -> không quét", not G.season_slot(date(2026, 1, 31), [])[0]
              and not G.season_slot(date(2026, 12, 31), [])[0]))
    r.append(("grace: slot+7 vẫn quét bù", G.season_slot(date(2026, 11, 22), ["2026-11-03:early"])[0] is True))
    r.append(("grace: slot+8 hết hạn", G.season_slot(date(2026, 11, 23), [])[0] is False))
    r.append(("early +7 (11-10) vẫn thuộc early, không nhảy sang full",
              G.season_slot(date(2026, 11, 10), [])[2] == "early"))
    r.append(("đã chạy -> idempotent", G.season_slot(date(2026, 11, 15), ["2026-11-15:full"])[:2] == (False, "2026-11-15:full")))
    r.append(("early đã chạy KHÔNG chặn full cùng mùa", G.season_slot(date(2026, 11, 15), ["2026-11-03:early"])[0] is True))
    return r


print("season_slot():")
for n, ok in slot_battery(GATE):
    check(n, ok)

print("\nrun_season() — state/log/idempotent (tmp paths):")
d = tempfile.mkdtemp(); sp, lp = os.path.join(d, "s.json"), os.path.join(d, "g.log")
json.dump({"last_check_date": "2026-10-11", "last_used_date": "2026-08-11", "last_used_rate": 6.8}, open(sp, "w"))
fake = lambda a: {"n_tickers": 3, "n_stale": 1, "stale_days": 105, "age_p50": 40.0, "by_quarter": {}}
r1 = GATE.run_season(asof="2026-11-15", state_path=sp, log_path=lp, stats_fn=fake)
st = GATE.load_state(sp)
check("lần 1: scan + slot full", r1["scan"] is True and r1["slot"] == "2026-11-15:full")
check("state ghi season_done", st.get("season_done") == ["2026-11-15:full"])
check("khóa lãi suất cũ KHÔNG đổi", (st["last_used_rate"], st["last_used_date"], st["last_check_date"]) == (6.8, "2026-08-11", "2026-10-11"))
r2 = GATE.run_season(asof="2026-11-15", state_path=sp, log_path=lp, stats_fn=fake)
check("lần 2 cùng ngày: no-op", r2["scan"] is False and r2["reason"] == "slot_already_done")
check("lần 2: season_done không nhân đôi", GATE.load_state(sp)["season_done"] == ["2026-11-15:full"])
r3 = GATE.run_season(asof="2026-11-18", state_path=sp, log_path=lp, stats_fn=fake)
check("bù 3 ngày sau: vẫn no-op", r3["scan"] is False)
check("log hợp lệ JSON, 3 dòng (scan + 2 already_done)", len(open(lp).read().splitlines()) == 3
      and all(json.loads(x) for x in open(lp)))
r4 = GATE.run_season(asof="2026-12-20", state_path=sp, log_path=lp, stats_fn=fake)
check("ngoài cửa sổ: không ghi log", r4["reason"] == "no_slot_in_window" and len(open(lp).read().splitlines()) == 3)
boom = lambda a: (_ for _ in ()).throw(RuntimeError("boom"))
r5 = GATE.run_season(asof="2027-02-15", state_path=sp, log_path=lp, stats_fn=boom)
check("stats lỗi: không đánh dấu done, reason season_error",
      r5["scan"] is False and r5["reason"].startswith("season_error") and "2027-02-15:full" not in GATE.load_state(sp)["season_done"])
r6 = GATE.run_season(asof="2027-02-15", state_path=sp, log_path=lp, stats_fn=fake)
check("lượt sau thử lại thành công", r6["scan"] is True)
d2 = tempfile.mkdtemp(); sp2 = os.path.join(d2, "s.json")
GATE.run_season(asof="2026-11-15", state_path=sp2, log_path=os.path.join(d2, "l"), stats_fn=fake, dry=True)
check("dry: không ghi state/log", not os.path.exists(sp2) and not os.path.exists(os.path.join(d2, "l")))
old = GATE.run_gate(asof="2026-11-11", state_path=sp, log_path=lp, dry=True)
check("run_gate cũ vẫn chạy, không bị ảnh hưởng", "refresh" in old)
many = {"season_done": [f"x{i}" for i in range(20)]}
json.dump(many, open(sp2, "w"))
GATE.run_season(asof="2026-11-15", state_path=sp2, log_path=os.path.join(d2, "l"), stats_fn=fake)
check("season_done cắt còn <=8", len(GATE.load_state(sp2)["season_done"]) == 8)

print("\nseason_stats() thật trên cache local:")
try:
    ss = GATE.season_stats("2026-10-30")
    check("n_tickers > 500 và 0<=n_stale<=n_tickers", ss["n_tickers"] > 500 and 0 <= ss["n_stale"] <= ss["n_tickers"])
    print("    ", ss)
except Exception as e:
    check(f"season_stats chạy được ({type(e).__name__}: {e})", False)

print("\nSTALE helpers:")
check("age 105 -> chưa STALE (ngưỡng '>')", DV.is_stale_bctc(105) is False)
check("age 106 -> STALE", DV.is_stale_bctc(106) is True)
check("age None -> không STALE", DV.is_stale_bctc(None) is False)
check("fin_age_days lịch", DV.fin_age_days("2026-07-20", "2026-10-30") == 102)
check("fin_age_days không âm", DV.fin_age_days("2026-11-01", "2026-10-30") == 0)
orig = DV.dcf_check
try:
    DV.dcf_check = lambda *a, **k: {"status": "CHEAP", "margin_of_safety": 0.184, "robust": True, "fin_age_days": 120, "stale": True}
    check("dcf_line: STALE hiện cờ", DV.dcf_line("X", "2026-10-30").endswith("⚠ STALE BCTC 120d"))
    DV.dcf_check = lambda *a, **k: {"status": "CHEAP", "margin_of_safety": 0.184, "robust": True, "fin_age_days": 50, "stale": False}
    check("dcf_line: tươi = dòng cũ y nguyên", DV.dcf_line("X", "2026-10-30") == "DCF: CHEAP (MoS +18.4%, robust)")
    DV.dcf_check = lambda *a, **k: {"status": "NOT_COMPUTED", "reason": "no_price"}
    check("dcf_line: NOT_COMPUTED không đổi", DV.dcf_line("X", "2026-10-30") == "DCF: N/A (thiếu giá)")
finally:
    DV.dcf_check = orig

BASE_COMMIT = "39519ea16"       # cha của commit tính năng: dcf_valuation CHƯA có fin_age_days/stale (bất biến)
BASE_PATH = "WorkingClaude/dcf_valuation.py"


def base_src():
    import subprocess
    return subprocess.run(["git", "-C", CANON, "show", f"{BASE_COMMIT}:{BASE_PATH}"], capture_output=True,
                          text=True, check=True).stdout


def control_same(DVm, CVm, verbose=False):
    """FV/MoS/classify của DVm khớp bản gốc CVm; trả (ok, n_tính_được)."""
    sys.modules["dcf_valuation"] = DVm
    same, n = True, 0
    for tk in ("HPG", "FPT", "VNM", "MWG", "PNJ", "DGC", "REE", "GMD"):
        a, b = DVm.fair_value(tk, "2026-10-30", price=30000.0), CVm.fair_value(tk, "2026-10-30", price=30000.0)
        if a.get("ok") != b.get("ok"):
            same = False
        if a.get("ok"):
            n += 1
            same &= (a["fair_value_ps"] == b["fair_value_ps"] and a["margin_of_safety"] == b["margin_of_safety"]
                     and a["fin_age_days"] == DVm.fin_age_days(a["fin_time"], "2026-10-30"))
            same &= (DVm.classify_dcf(a["margin_of_safety"], a["sensitivity"], 30000.0)
                     == CVm.classify_dcf(b["margin_of_safety"], b["sensitivity"], 30000.0))
            if verbose:
                print(f"     {tk}: fin_time={a['fin_time']} age={a['fin_age_days']}d MoS={a['margin_of_safety']:+.4f}")
    return bool(same), n


print(f"\nCONTROL: FV/MoS/phân loại KHÔNG đổi so với commit gốc {BASE_COMMIT} (git show, bất biến — không tautology sau merge):")
CV = load("dcf_valuation", CANON, alias="dcf_valuation_base", src=base_src())
check("bản gốc thật sự chưa có fin_age_days (control đúng là bản trước)", not hasattr(CV, "fin_age_days"))
ok_c, n_c = control_same(DV, CV, verbose=True)
check(f"FV/MoS/classify khớp commit gốc trên {n_c} mã tính được (>=3)", ok_c and n_c >= 3)
sys.modules["dcf_valuation"] = DV


def hist_battery(DVm):
    """(a) as-of lịch sử 2024-04-20: PIT (fin_time<=asof), tuổi lịch đúng, dải 80-89 ngày."""
    sys.modules["dcf_valuation"] = DVm
    r, ages = [], []
    ok_pit = ok_age = True
    for tk in ("HPG", "FPT", "VNM", "MWG", "PNJ", "DGC"):
        x = DVm.fair_value(tk, "2024-04-20", price=30000.0)
        if not x.get("ok"):
            ok_pit = False
            continue
        ft = date.fromisoformat(x["fin_time"])
        ok_pit &= ft <= date(2024, 4, 20)
        ok_age &= x["fin_age_days"] == (date(2024, 4, 20) - ft).days
        ages.append(x["fin_age_days"])
    r.append(("as-of 2024-04-20: fin_time <= asof (không nhìn trước)", ok_pit and len(ages) >= 5))
    r.append(("as-of 2024-04-20: fin_age_days = ngày lịch (asof - fin_time)", ok_age and len(ages) >= 5))
    r.append(("as-of 2024-04-20: tuổi trong 80-89 ngày (không phải 0 / toàn cục)", bool(ages) and all(80 <= g <= 89 for g in ages)))
    return r


def check_battery(DVm):
    """(b) dcf_check THẬT (fair_value stub): stale/fin_age_days đi đúng từ fair_value ra dict."""
    sys.modules["dcf_valuation"] = DVm
    orig_fv, r = DVm.fair_value, []
    try:
        for age, stale in ((120, True), (50, False), (105, False), (106, True)):
            DVm.fair_value = lambda *a, _g=age, **k: {"ok": True, "margin_of_safety": 0.25, "sensitivity": {}, "fin_age_days": _g}
            c = DVm.dcf_check("HPG", "2026-10-30", price=30000.0)
            r.append((f"dcf_check age={age} -> stale={stale}, fin_age_days={age}",
                      c.get("stale") is stale and c.get("fin_age_days") == age and c.get("status") != "NOT_COMPUTED"))
    finally:
        DVm.fair_value = orig_fv
    return r


def stats_battery(Gm, DVm):
    """(c) season_stats trên parquet tổng hợp qua fin_path."""
    import pandas as pd
    sys.modules["dcf_valuation"] = DVm
    t = tempfile.mkdtemp(); fp = os.path.join(t, "fin.parquet")
    rows = [("A", "2026-10-20"), ("B", "2026-06-01"), ("C", "2026-07-20"), ("D", "2025-01-01"),
            ("E", "2026-08-01"), ("E", "2026-11-10"), ("F", "2026-07-17"),
            ("G", "2026-11-05")]      # F: tuổi đúng 105; E có dòng TƯƠNG LAI; G CHỈ có dòng tương lai
    pd.DataFrame({"ticker": [x for x, _ in rows], "time": pd.to_datetime([y for _, y in rows]),
                  "quarter": "2026Q2"}).to_parquet(fp)
    try:
        st = Gm.season_stats("2026-10-30", fin_path=fp)
    except Exception as e:
        return [(f"season_stats chạy được ({type(e).__name__})", False)]
    return [("season_stats: n_tickers=5 (A,B,C,E,F; D>400d loại, G chỉ-tương-lai loại)", st["n_tickers"] == 5),
            ("season_stats: n_stale=1 (chỉ B; F tuổi đúng 105 KHÔNG stale)", st["n_stale"] == 1),
            ("season_stats: age_p50=102.0 (10,90,102,105,151)", st["age_p50"] == 102.0)]


class _FakeDT:
    """datetime giả: now(tz) = 2026-11-14 18:30 UTC. Không tz ⇒ trả naive-UTC (host UTC), có tz ⇒ đổi múi."""
    @staticmethod
    def now(tz=None):
        from datetime import datetime as _d, timezone
        u = _d(2026, 11, 14, 18, 30, tzinfo=timezone.utc)
        return u.astimezone(tz) if tz is not None else u.replace(tzinfo=None)


def clock_battery(Gm):
    """(e) asof=None neo ICT: 18:30 UTC 14/11 = 01:30 ICT 15/11 ⇒ slot full 15/11, không phải ngày UTC."""
    real, r = Gm.datetime, []
    Gm.datetime = _FakeDT
    try:
        r.append(("asof=None: _now_ict_date = 2026-11-15 (ICT, không phải ngày UTC 14)", Gm._now_ict_date() == "2026-11-15"))
        t = tempfile.mkdtemp()
        o = Gm.run_season(asof=None, state_path=os.path.join(t, "s.json"), log_path=os.path.join(t, "l"), stats_fn=fake, dry=True)
        r.append(("run_season(asof=None): slot 2026-11-15:full", o["slot"] == "2026-11-15:full" and o["scan"] is True))
    finally:
        Gm.datetime = real
    return r


def cli_battery(gate_patch=None):
    """(d) mã thoát CLI: season_error ⇒ rc=1 + dòng '❌ dcf_refresh_gate --season:' ở stderr; bình thường ⇒ rc=0."""
    import subprocess
    src = open(os.path.join(HERE, "dcf_refresh_gate.py"), encoding="utf-8").read()
    src = src.replace('fp = fin_path or f"{WORKDIR}/data/bq_cache/ticker_financial.parquet"',
                      'fp = fin_path or "/nonexistent/ticker_financial.parquet"')
    if gate_patch:
        assert gate_patch[0] in src, gate_patch[0]
        src = src.replace(*gate_patch)
    t = tempfile.mkdtemp(); gp = os.path.join(t, "dcf_refresh_gate.py"); open(gp, "w", encoding="utf-8").write(src)
    env = {k: v for k, v in os.environ.items() if k != "TZ"}
    bad = subprocess.run([sys.executable, gp, "--season", "--asof", "2026-11-15", "--dry"], capture_output=True, text=True, env=env)
    ok = subprocess.run([sys.executable, gp, "--season", "--asof", "2026-12-20", "--dry"], capture_output=True, text=True, env=env)
    return [("CLI season_error -> rc=1", bad.returncode == 1),
            ("CLI season_error -> stderr có dòng '❌ dcf_refresh_gate --season:' (cron_health_check bắt)",
             any(l.startswith("❌ dcf_refresh_gate --season:") for l in bad.stderr.splitlines())),
            ("CLI ngoài cửa sổ -> rc=0 và in JSON no_slot_in_window", ok.returncode == 0 and "no_slot_in_window" in ok.stdout)]


print("\n(a) as-of lịch sử:")
for n, ok in hist_battery(DV):
    check(n, ok)
print("\n(b) dcf_check thật (fair_value stub):")
for n, ok in check_battery(DV):
    check(n, ok)
print("\n(c) season_stats parquet tổng hợp:")
for n, ok in stats_battery(GATE, DV):
    check(n, ok)
print("\n(d) CLI exit code:")
for n, ok in cli_battery():
    check(n, ok)
print("\n(e) asof=None neo ICT (host TZ=%r):" % os.environ.get("TZ"))
for n, ok in clock_battery(GATE):
    check(n, ok)
sys.modules["dcf_valuation"] = DV

print("\nMUTATION (mỗi đột biến PHẢI làm ít nhất 1 assertion đỏ):")
G_SRC = [("<= SEASON_GRACE_DAYS", "< SEASON_GRACE_DAYS", "grace off-by-one"),
         ("    if sid in (done or []):\n        return False, sid, kind, \"slot_already_done\"\n", "", "bỏ idempotent"),
         ("SEASON_GRACE_DAYS = 7 ", "SEASON_GRACE_DAYS = 12 ", "grace 12 ngày"),
         ("(11, 3, \"early\")", "(11, 4, \"early\")", "lệch ngày slot"),
         ("(8, 15, \"full\")", "(8, 15, \"early\")", "sai kind")]
for a, b, why in G_SRC:
    M = load("dcf_refresh_gate", HERE, src_patch=(a, b), alias="gate_mut")
    check(f"gate mutation '{why}' bị bắt", any(not ok for _, ok in slot_battery(M)))
M = load("dcf_refresh_gate", HERE, src_patch=("new_state[\"season_done\"] = (list(done) + [sid])[-SEASON_KEEP:]", "pass", ), alias="gate_mut")
dm = tempfile.mkdtemp(); spm = os.path.join(dm, "s.json")
M.run_season(asof="2026-11-15", state_path=spm, log_path=os.path.join(dm, "l"), stats_fn=fake)
M.run_season(asof="2026-11-15", state_path=spm, log_path=os.path.join(dm, "l"), stats_fn=fake)
check("gate mutation 'không ghi season_done' bị bắt (lượt 2 lại quét)",
      len(open(os.path.join(dm, "l")).read().splitlines()) == 2 and '"scan": true' in open(os.path.join(dm, "l")).read().splitlines()[1].replace('"scan": True', '"scan": true'))
for a, b, why in [("age_days > STALE_BCTC_DAYS", "age_days >= STALE_BCTC_DAYS", "STALE '>=' "),
                  ("STALE_BCTC_DAYS = 105", "STALE_BCTC_DAYS = 90", "ngưỡng 90")]:
    M = load("dcf_valuation", HERE, src_patch=(a, b), alias="dv_mut")
    bad = (M.is_stale_bctc(105) is True) or (M.is_stale_bctc(106) is not True) or (M.is_stale_bctc(100) is True)
    check(f"dcf_valuation mutation '{why}' bị bắt", bad)
def killed(battery_results):
    return any(not ok for _, ok in battery_results)


print("  -- đột biến cho (a)-(f):")
FV_LOOK = ("rows = fin[(fin.ticker == ticker) & (fin.time <= a)]", "rows = fin[(fin.ticker == ticker)]")
for (a, b), why in [(FV_LOOK, "(a) fair_value bỏ lọc time<=asof (nhìn trước)"),
                    (('"fin_age_days": fin_age_days(last.time, a),', '"fin_age_days": fin_age_days(fin.time.max(), a),'),
                     "(a) fin_age dùng time.max() toàn cục"),
                    (('"fin_time": str(pd.Timestamp(last.time).date()),', '"fin_time": str(pd.Timestamp(fin.time.max()).date()),'),
                     "(a) fin_time lấy max toàn cục")]:
    M = load("dcf_valuation", HERE, src_patch=(a, b), alias="dv_mut")
    check(f"mutant {why} bị bắt", killed(hist_battery(M)))
for (a, b), why in [(('"stale": is_stale_bctc(res.get("fin_age_days")),', '"stale": False,'), "(b) dcf_check stale=False cứng"),
                    (('"fin_age_days": res.get("fin_age_days"),', '"fin_age_days": None,'), "(b) dcf_check fin_age_days=None")]:
    M = load("dcf_valuation", HERE, src_patch=(a, b), alias="dv_mut")
    check(f"mutant {why} bị bắt", killed(check_battery(M)))
for (a, b), why in [(("df = df[df.time <= a].sort_values", "df = df.sort_values"), "(c) season_stats bỏ lọc time<=asof"),
                    (("(a - last.time).dt.days <= 400", "(a - last.time).dt.days <= 4000"), "(c) bỏ cửa sổ 400 ngày"),
                    (('int((ages > _dv.STALE_BCTC_DAYS).sum())', 'int((ages >= _dv.STALE_BCTC_DAYS).sum())'), "(c) n_stale dùng >="),
                    (('int((ages > _dv.STALE_BCTC_DAYS).sum())', '0'), "(c) n_stale=0 cứng")]:
    M = load("dcf_refresh_gate", HERE, src_patch=(a, b), alias="gate_mut")
    check(f"mutant {why} bị bắt", killed(stats_battery(M, DV)))
sys.modules["dcf_valuation"] = DV
for (a, b), why in [(("sys.exit(1)", "sys.exit(0)"), "(d) CLI lỗi vẫn rc=0"),
                    (("print(f\"❌ dcf_refresh_gate --season: {d['reason']}\", file=sys.stderr)", "pass"), "(d) bỏ dòng ❌ stderr")]:
    check(f"mutant {why} bị bắt", killed(cli_battery(gate_patch=(a, b))))
M = load("dcf_refresh_gate", HERE, src_patch=('datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))', 'datetime.now()'), alias="gate_mut")
check("mutant (e) datetime.now() trần bị bắt", killed(clock_battery(M)))
M = load("dcf_refresh_gate", HERE, src_patch=('datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))', 'datetime.now(ZoneInfo("UTC"))'), alias="gate_mut")
check("mutant (e) neo UTC thay ICT bị bắt", killed(clock_battery(M)))
sys.modules["dcf_valuation"] = DV
M = load("dcf_valuation", HERE, src_patch=("base_fcfe = (cfoa3 + cfinv3) / 3.0", "base_fcfe = (cfoa3 + cfinv3) / 2.0"), alias="dv_mut")
check("mutant (f) FV đổi (base_fcfe/2) bị control-pin bắt", control_same(M, CV)[0] is False)
M = load("dcf_valuation", HERE, src_patch=("def is_stale_bctc(age_days):", "def classify_dcf_x(*a):\n    return None\n\n\ndef is_stale_bctc(age_days):"), alias="dv_mut")
check("control-pin: biến thể vô hại không làm control đỏ (không báo giả)", control_same(M, CV)[0] is True)
sys.modules["dcf_valuation"] = DV

sys.modules["dcf_valuation"] = DV

print(f"\n{'ALL PASS' if not fails else 'FAILURES: ' + ', '.join(fails)}")
sys.exit(1 if fails else 0)
