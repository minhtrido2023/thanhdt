# -*- coding: utf-8 -*-
"""lag_dd_zone_gate_selfcheck.py — self-check cho trading_bot.plan.filter_lag_dd_zone_orders
(luật user 2026-11-09: mua LAG cần DD + giá ≤ tâm). Offline: sổ DD giả qua monkeypatch _lag_dd_zone_deps.
Chạy: python3 lag_dd_zone_gate_selfcheck.py [--live]   (--live: replay trên sổ THẬT + plan 10/11 nếu có)
Không phụ thuộc TZ (asof tường minh, §16); chạy lại dưới `env -u TZ`.
"""
import datetime as dt
import os
import sys

CODE_ROOT = os.environ.get("LAGZONE_CODE_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_ROOT)
from trading_bot import plan as pm                                  # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan                # noqa: E402

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    PASS, FAIL = (PASS + 1, FAIL) if cond else (PASS, FAIL + 1)
    print(("  PASS  " if cond else "  FAIL  ") + name + ("" if cond else "  " + str(detail)))


def mk(specs, asof="2026-11-10"):
    os_ = [PlannedOrder(id=f"{s[2].upper()}-{s[0]}-{i}", ticker=s[0], side=s[2], qty=1000,
                        ref_price=s[3], book=s[1]) for i, s in enumerate(specs)]
    return TradePlan(plan_date=asof, signal_date=asof, strategy="t", strategy_version="0", state=3,
                     state_name="N", nav_basis={}, orders=os_, account="SELFCHECK")


def E(t, center, d="2026-11-09", rev=1, lo=1, hi=None, exp="2027-02-01"):
    return {"ticker": t, "dd_date": d, "rev": rev, "center": center, "zone_low": lo,
            "zone_high": hi or center * 1.3, "expires_on": exp}


LEDGER = {"entries": [E("AAA", 10000), E("BBB", 10000, d="2026-11-20"), E("CCC", 10000),
                      E("CCC", 12000, rev=2), E("LCK", 10000),
                      E("EXP", 10000, exp="2026-11-10"), E("FRM", 10000), E("ZHI", 10000, hi=9000)]}


def fake_deps(lock_bad=(), events=None, frame_block=()):
    def latest(ledger, asof=None):
        out = {}
        for e in ledger["entries"]:
            if asof is not None and e["dd_date"] > asof.isoformat():
                continue
            k = (e["dd_date"], e.get("rev", 1))
            t = e["ticker"]
            if t not in out or k >= (out[t]["dd_date"], out[t].get("rev", 1)):
                out[t] = e
        return out
    def expiry_of(e, asof, newer):
        return (asof >= dt.date.fromisoformat(e["expires_on"]), "quá hạn DD")

    def frame(e, evs, asof):
        return [], e["ticker"] in frame_block
    ev = (lambda tk, en, a: {}) if events != "NONE" else (lambda tk, en, a: None)
    return lambda: (latest, (lambda e: "md5 lệch" if e["ticker"] in lock_bad else None), LEDGER,
                    expiry_of, ev, frame)


def run(specs, lock_bad=(), deps=None, **kw):
    pm._lag_dd_zone_deps = deps or fake_deps(lock_bad, **kw)
    return pm.filter_lag_dd_zone_orders(mk(specs))


print("== unit ==")
p, b = run([("AAA", "LAG", "buy", 9000)]);               check("giá < tâm ⇒ GIỮ", len(p.orders) == 1 and not b)
p, b = run([("AAA", "LAG", "buy", 10000)]);              check("giá == tâm ⇒ GIỮ", len(p.orders) == 1 and not b)
p, b = run([("AAA", "LAG", "buy", 10001)]);              check("giá > tâm 1đ ⇒ LOẠI", len(p.orders) == 0 and len(b) == 1)
p, b = run([("ZZZ", "LAG", "buy", 5000)]);               check("không có DD ⇒ LOẠI", len(p.orders) == 0 and "chưa có DD" in b[0]["reason"])
p, b = run([("BBB", "LAG", "buy", 5000)]);               check("DD tương lai (dd_date > asof) ⇒ coi như chưa có ⇒ LOẠI", len(p.orders) == 0)
p, b = run([("CCC", "LAG", "buy", 11000)]);              check("rev mới nhất thắng (tâm 12000) ⇒ GIỮ", len(p.orders) == 1)
p, b = run([("LCK", "LAG", "buy", 5000)], lock_bad=("LCK",)); check("khoá md5 lệch ⇒ LOẠI", len(p.orders) == 0 and "md5" in b[0]["reason"])
p, b = run([("AAA", "LAG", "sell", 99999)]);             check("SELL LAG không bao giờ bị chặn", len(p.orders) == 1 and not b)
p, b = run([("AAA", "BAL", "buy", 99999)]);              check("book khác (BAL) không bị cổng này", len(p.orders) == 1 and not b)
p, b = run([("AAA", "lag", "buy", 99999)]);              check("book 'lag' thường vẫn là LAG (upper)", len(p.orders) == 0)
p, b = run([("AAA", "LAG_X", "buy", 99999)]);            check("khớp TUYỆT ĐỐI: 'LAG_X' không phải LAG", len(p.orders) == 1)
p, b = run([("AAA", "LAG", "buy", 9000), ("AAA", "LAG", "buy", 20000), ("BAL1", "BAL", "buy", 1)])
check("hỗn hợp: giữ lệnh đạt, loại lệnh không đạt, không đụng book khác", [o.ref_price for o in p.orders] == [9000, 1] and len(b) == 1)

def boom():
    raise OSError("sổ hỏng")
p, b = run([("AAA", "LAG", "buy", 1), ("AAA", "BAL", "buy", 1)], deps=boom)
check("sổ lỗi ⇒ FAIL-CLOSED: loại LAG buy, giữ book khác", len(p.orders) == 1 and p.orders[0].book == "BAL" and "fail-closed" in b[0]["reason"])
p, b = run([("EXP", "LAG", "buy", 5000)]);              check("DD hết hạn (asof ≥ expires_on) ⇒ LOẠI", len(p.orders) == 0 and "quá hạn" in b[0]["reason"])
p, b = run([("FRM", "LAG", "buy", 5000)], frame_block=("FRM",)); check("sự kiện quyền điều chỉnh giá sau DD ⇒ LOẠI", len(p.orders) == 0 and "hệ giá" in b[0]["reason"])
p, b = run([("AAA", "LAG", "buy", 5000)], events="NONE"); check("không kiểm được corp-action ⇒ FAIL-CLOSED", len(p.orders) == 0 and "fail-closed" in b[0]["reason"])
p, b = run([("ZHI", "LAG", "buy", 9500)]);              check("tâm 10000 nhưng đỉnh vùng 9000: giá 9500 ⇒ LOẠI (≤ min(tâm, đỉnh vùng))", len(p.orders) == 0)
p, b = run([("ZHI", "LAG", "buy", 8900)]);              check("…giá 8900 ⇒ GIỮ", len(p.orders) == 1)
p, b = run([("AAA", "LAG", "buy", 9000)]);              check("lệnh GIỮ bị ép trần cứng = tâm (10000)", p.orders[0].hard_no_chase_ceiling_vnd == 10000.0, p.orders[0].hard_no_chase_ceiling_vnd)
pm._lag_dd_zone_deps = fake_deps()
pl = mk([("AAA", "LAG", "buy", 11000)])
pl.orders[0].hard_no_chase_ceiling_vnd = 9500.0
p, b = pm.filter_lag_dd_zone_orders(pl);                check("giá = min(ref, trần) ⇒ trần 9500 ≤ tâm ⇒ GIỮ, trần giữ 9500", len(p.orders) == 1 and p.orders[0].hard_no_chase_ceiling_vnd == 9500.0)
pm.LAG_DD_ZONE_GATE_ENABLED = False
p, b = pm.filter_lag_dd_zone_orders(mk([("ZZZ", "LAG", "buy", 1)])); check("công tắc OFF ⇒ no-op", len(p.orders) == 1 and not b)
pm.LAG_DD_ZONE_GATE_ENABLED = True

print("== D1/D5: LAG_DD_REQUIRE_CONFIRMED (user 22/11) — sổ fixture riêng ==")
check("module đang test là bản cạnh selfcheck (không phải canonical qua .pth)",
      os.path.dirname(os.path.dirname(os.path.abspath(pm.__file__))) == os.path.abspath(CODE_ROOT), pm.__file__)
check("hằng mặc định LAG_DD_REQUIRE_CONFIRMED is False (không commit bản bật)", pm.LAG_DD_REQUIRE_CONFIRMED is False)


def EK(t, sk="__MISSING__", afm=None, center=10000):
    e = E(t, center)
    if sk != "__MISSING__":
        e["skeptic_final"] = sk
    if afm is not None:
        e["audited_fy_missing"] = afm
    return e


LEDGER_D = {"entries": [EK("CNF", "CONFIRMED", False), EK("FXU", "FIXED_UNVERIFIED", False),
                        EK("RFO", "REFUTED_OPEN", False), EK("NON", "NONE", False), EK("MIS"),
                        EK("NUL", None, False), EK("AFM", "CONFIRMED", True), EK("AFN", "CONFIRMED"),
                        EK("PXH", "FIXED_UNVERIFIED", True), EK("LCK", "FIXED_UNVERIFIED", True)]}


def d_cases(mod, flag):
    """→ list (tên, ok). Chạy trên module `mod` (pm thật hoặc mutant) với hằng = flag."""
    fd = fake_deps(lock_bad=("LCK",))
    mod._lag_dd_zone_deps = lambda: fd()[:2] + (LEDGER_D,) + fd()[3:]
    mod.LAG_DD_REQUIRE_CONFIRMED = flag
    res = []

    def one(t, px=9000):
        return mod.filter_lag_dd_zone_orders(mk([(t, "LAG", "buy", px)]))
    if not flag:
        for t in ("FXU", "RFO", "NON", "MIS", "AFM", "CNF"):
            p, b = one(t)
            res.append((f"hằng False ⇒ {t} vẫn QUA (hành vi cũ)", len(p.orders) == 1 and not b))
        return res
    p, b = one("CNF"); res.append(("hằng True ⇒ CONFIRMED + audited_fy_missing=False ⇒ QUA", len(p.orders) == 1 and not b))
    p, b = one("AFN"); res.append(("hằng True ⇒ CONFIRMED + thiếu trường audited_fy_missing ⇒ QUA (chỉ `is True` mới chặn)", len(p.orders) == 1 and not b))
    for t, lab in (("FXU", "'FIXED_UNVERIFIED'"), ("RFO", "'REFUTED_OPEN'"), ("NON", "'NONE'"),
                   ("MIS", "<thiếu trường>"), ("NUL", "None")):
        p, b = one(t)
        ok = len(p.orders) == 0 and len(b) == 1 and f"skeptic_final={lab}" in b[0]["reason"] \
            and "rev1" in b[0]["reason"] and "2026-11-09" in b[0]["reason"] and "D1" in b[0]["reason"]
        res.append((f"hằng True ⇒ {t} bị CHẶN, lý do in nhãn thật {lab} + rev + dd_date", ok))
    p, b = one("AFM")
    res.append(("hằng True ⇒ CONFIRMED nhưng audited_fy_missing=True ⇒ CHẶN (D5), lý do có rev+dd_date",
                len(p.orders) == 0 and len(b) == 1 and "audited_fy_missing=True" in b[0]["reason"]
                and "D5" in b[0]["reason"] and "rev1" in b[0]["reason"] and "2026-11-09" in b[0]["reason"]))
    p, b = one("PXH", 10500)
    res.append(("hằng True ⇒ giá > tâm VẪN báo lý do cũ (điều kiện mới đặt SAU, không che)",
                len(b) == 1 and "luật 09/11" in b[0]["reason"] and "skeptic_final" not in b[0]["reason"]))
    p, b = one("LCK")
    res.append(("hằng True ⇒ khoá md5 lệch VẪN báo lý do cũ", len(b) == 1 and "md5" in b[0]["reason"]
                and "skeptic_final" not in b[0]["reason"]))
    p, b = mod.filter_lag_dd_zone_orders(mk([("FXU", "LAG", "sell", 9000), ("FXU", "BAL", "buy", 9000)]))
    res.append(("hằng True ⇒ SELL LAG / BUY book khác không bị cổng con chặn", len(p.orders) == 2 and not b))
    p, b = one("CNF")
    res.append(("hằng True ⇒ lệnh QUA vẫn bị ép trần = tâm", p.orders[0].hard_no_chase_ceiling_vnd == 10000.0))
    return res


for flag in (False, True):
    for n, ok in d_cases(pm, flag):
        check(n, ok)
pm.LAG_DD_REQUIRE_CONFIRMED = False

print("== mutation (mỗi mutant phải làm ≥1 ca D1/D5 FAIL) ==")
import types
_SRC = open(pm.__file__, encoding="utf-8").read()
_C1 = 'elif LAG_DD_REQUIRE_CONFIRMED and e.get("skeptic_final") != "CONFIRMED":'
_C2 = 'elif LAG_DD_REQUIRE_CONFIRMED and e.get("audited_fy_missing") is True:'
_LM = "            if lm:\n"
MUTANTS = {
    "M1 bỏ điều kiện skeptic_final": (_C1, "elif False:"),
    "M2 bỏ điều kiện audited_fy_missing": (_C2, "elif False:"),
    "M3 thiếu trường ⇒ coi CONFIRMED (fail-open)": ('e.get("skeptic_final") != "CONFIRMED"',
                                                     'e.get("skeptic_final", "CONFIRMED") != "CONFIRMED"'),
    "M4 bỏ hằng (luôn bật)": (_C1, 'elif e.get("skeptic_final") != "CONFIRMED":'),
    "M5 đặt điều kiện mới TRƯỚC điều kiện cũ": (_LM, '            if LAG_DD_REQUIRE_CONFIRMED and '
                                                     'e.get("skeptic_final") != "CONFIRMED":\n'
                                                     '                why = "skeptic_final sớm"\n'
                                                     '            elif lm:\n'),
    "M6 chỉ chặn đúng chuỗi FIXED_UNVERIFIED": ('e.get("skeptic_final") != "CONFIRMED"',
                                                 'e.get("skeptic_final") == "FIXED_UNVERIFIED"'),
    "M7 hằng mặc định True": ("LAG_DD_REQUIRE_CONFIRMED = False", "LAG_DD_REQUIRE_CONFIRMED = True"),
}
for name, (a, b_) in MUTANTS.items():
    if _SRC.count(a) < 1:
        check(f"{name}: tìm thấy điểm đột biến", False, a)
        continue
    msrc = _SRC.replace(a, b_, 1)
    m = types.ModuleType("trading_bot._plan_mut")
    m.__package__ = "trading_bot"
    m.__file__ = pm.__file__
    sys.modules[m.__name__] = m
    exec(compile(msrc, pm.__file__ + "<mut>", "exec"), m.__dict__)
    default_true = m.LAG_DD_REQUIRE_CONFIRMED is not False
    fails = [n for flag in (False, True) for n, ok in d_cases(m, flag) if not ok]
    killed = bool(fails) or default_true
    check(f"{name}: KILLED" + (f" (vd: {fails[0][:60]})" if fails else " (hằng mặc định khác False)"), killed)
    del sys.modules[m.__name__]

print("== đường nạp THẬT (importlib, mike root tạm) ==")
import json, shutil, tempfile
real_root = next(r for r in ("/home/trido/thanhdt/WorkingClaude/mike",) if os.path.isfile(r + "/bin/dd_price_zone_watch.py"))
tmp = tempfile.mkdtemp()
os.makedirs(tmp + "/bin"); os.makedirs(tmp + "/kb")
shutil.copy(real_root + "/bin/dd_price_zone_watch.py", tmp + "/bin/")
json.dump({"entries": [E("AAA", 10000)]}, open(tmp + "/kb/dd_price_zones.json", "w"))
importlib_pm = __import__("importlib").reload(pm)
os.environ["LAG_DD_ZONE_MIKE_ROOT"] = tmp
before = sys.path[:]
deps = pm._lag_dd_zone_deps()
check("nạp thật: sys.path KHÔNG đổi sau _lag_dd_zone_deps", sys.path == before, [x for x in sys.path if x not in before])
check("nạp thật: đọc đúng sổ tạm", deps[2]["entries"][0]["ticker"] == "AAA" and len(deps) == 6)
e0 = deps[0](deps[2], dt.date(2026, 11, 10))["AAA"]
check("nạp thật: latest_entries chạy", e0["center"] == 10000)
check("nạp thật: lock_mismatch None khi entry không khai khoá", deps[1](e0) is None)
pl = mk([("AAA", "LAG", "buy", 12000)])
pm._lag_dd_zone_deps = importlib_pm._lag_dd_zone_deps
p, b = pm.filter_lag_dd_zone_orders(pl)
check("nạp thật end-to-end: giá > tâm ⇒ LOẠI, sys.path vẫn nguyên", len(p.orders) == 0 and sys.path == before)
shutil.rmtree(tmp)
os.environ.pop("LAG_DD_ZONE_MIKE_ROOT", None)

print("== wiring (cấu trúc bot_execute) ==")
src = open(os.path.join(CODE_ROOT, "bot_execute.py"), encoding="utf-8").read()
i_dd, i_lz, i_net = (src.find("plan, dd_blocked = filter_dd_flag_orders(plan)"),
                     src.find("plan, lagzone_blocked = filter_lag_dd_zone_orders(plan)"),
                     src.find("plan, net_adj = net_offsetting_orders(plan)"))
check("cổng LAG-zone được gọi trong bot_execute", i_lz > 0)
check("thứ tự: dd_flag < lag_zone < netting", 0 < i_dd < i_lz < i_net, (i_dd, i_lz, i_net))

if "--live" in sys.argv:
    print("== live replay (sổ thật) ==")
    import importlib
    importlib.reload(pm)
    for acct in ("SpaceX", "ZaloPay"):
        import glob
        cands = sorted(glob.glob(f"/home/trido/thanhdt/WorkingClaude/data/trade_plans/plan_{acct}_2026-*.json"))
        cands = [c for c in cands if ".bak" not in c]
        if not cands:
            check(f"{acct}: có plan để replay", False, "không thấy plan nào")
            continue
        f = cands[-1]
        print("  plan:", os.path.basename(f))
        import json
        raw = json.load(open(f, encoding="utf-8"))
        orders = [PlannedOrder(**{k: v for k, v in o.items() if k in PlannedOrder.__dataclass_fields__})
                  for o in raw["orders"]]
        plan = TradePlan(plan_date=raw["plan_date"], signal_date=raw["signal_date"], strategy="x", strategy_version="x",
                         state=3, state_name="N", nav_basis={}, orders=orders, account=acct)
        nlag = sum(1 for o in orders if o.book.upper() == "LAG" and o.side == "buy")
        p, b = pm.filter_lag_dd_zone_orders(plan)
        for a in b:
            print("   ", acct, a["ticker"], a["price"], "tâm", a["center"], "|", a["reason"][:90])
        check(f"{acct}: mọi LAG buy plan 10/11 ({nlag}) đã đối chiếu sổ thật", nlag == len(b) + sum(
            1 for o in p.orders if o.book.upper() == "LAG"))

print(f"\n{PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
