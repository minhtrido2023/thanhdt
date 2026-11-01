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


def load(name, base, src_patch=None, alias=None):
    src = open(os.path.join(base, name + ".py"), encoding="utf-8").read()
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

print("\nCONTROL: FV/MoS/phân loại KHÔNG đổi so với bản canonical (code mới chỉ thêm field):")
CV = load("dcf_valuation", CANON, alias="dcf_valuation_canon")
sys.modules["dcf_valuation"] = DV
same, n, stale_seen = True, 0, 0
for tk in ("HPG", "FPT", "VNM", "MWG", "PNJ", "DGC", "REE", "GMD"):
    a, b = DV.fair_value(tk, "2026-10-30", price=30000.0), CV.fair_value(tk, "2026-10-30", price=30000.0)
    if a.get("ok") != b.get("ok"):
        same = False
    if a.get("ok"):
        n += 1
        same &= (a["fair_value_ps"] == b["fair_value_ps"] and a["margin_of_safety"] == b["margin_of_safety"]
                 and a["fin_age_days"] == DV.fin_age_days(a["fin_time"], "2026-10-30"))
        ca, cb = DV.classify_dcf(a["margin_of_safety"], a["sensitivity"], 30000.0), CV.classify_dcf(b["margin_of_safety"], b["sensitivity"], 30000.0)
        same &= (ca == cb)
        print(f"     {tk}: fin_time={a['fin_time']} age={a['fin_age_days']}d MoS={a['margin_of_safety']:+.4f}")
check(f"FV/MoS/classify khớp bản canonical trên {n} mã tính được (>=3)", same and n >= 3)

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
sys.modules["dcf_valuation"] = DV

print(f"\n{'ALL PASS' if not fails else 'FAILURES: ' + ', '.join(fails)}")
sys.exit(1 if fails else 0)
