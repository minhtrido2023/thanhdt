#!/usr/bin/env python3
"""discretionary_target_pct_selfcheck.py — selfcheck cho MỤC TIÊU THEO TỶ TRỌNG
(`target_pct_active_nav`) của chương trình DISCRETIONARY_SPECIAL + cổng tươi active_nav
trong injector. Job Taylor_20260812_161457 (reconcile P1 ↔ quy trình lập plan TV1).

Chạy: python3 discretionary_target_pct_selfcheck.py
§16: chạy thêm một lần dưới `env -u TZ TZ=America/New_York` — mọi ca so ngày ở đây đều
truyền `now` tường minh nên kết quả PHẢI y hệt; khác nhau = phát hiện, không phải nhiễu.

Bao phủ:
  A. resolve_target_qty — chế độ cố định (hành vi cũ) vs tỷ trọng, số học chính xác.
  B. KHÔNG fail-OPEN: mọi input active_nav thiếu/rác ⇒ failsafe, KHÔNG có lệnh nào.
  C. Đủ tỷ trọng ⇒ `skip` GIỮ state active (KHÔNG `completed`) — khác hẳn chế độ cố định.
  D. Deadband top-up, kèm CA CHỨNG MINH NGƯỢC (bỏ deadband ⇒ thật sự có lệnh).
  E. Cổng tươi active_nav (computed_at phải ĐÚNG hôm nay).
  F. E2E qua injector: target đúng, ledger đúng, order V2.4 không bị đụng, state không đóng.
  G. Hồi quy: state target CỐ ĐỊNH vẫn chạy y như cũ (không đọc active_nav).
"""
import copy
import datetime as dt
import json
import os
import sys
import tempfile

WC_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC_ROOT)
sys.path.insert(0, os.path.join(WC_ROOT, "mike", "bin"))

from trading_bot.discretionary_accumulation import (
    compute_session_order, resolve_target_qty, validate_state, BOOK,
    TARGET_PCT_ACTIVE_NAV_MAX)
import trading_bot.brokers as brokers_mod
import discretionary_accumulation_inject as inj

PASS = 0
FAIL = 0

ADV = 720_000_000
BENIGN_TURN = 0.5 * ADV          # < k×adv_ref ⇒ không opportunistic
PLAN_DATE = "2026-08-13"
NOW_ISO = "2026-08-12T20:30:00+07:00"


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")


def pct_state(**over):
    """State TV1 thật rút gọn (target theo tỷ trọng)."""
    st = {
        "ticker": "TV1", "account": "SELFCHK", "book": BOOK, "status": "active",
        "target_basis": "pct_active_nav", "target_pct_active_nav": 0.05,
        "topup_min_gap_pct_active_nav": 0.005,
        "baseline_qty_before_program": 0, "lot_size": 100, "priority": 5,
        "price_band": {"resting_limit": 19900, "no_chase_ceiling": 20000,
                       "max_no_chase_ceiling": 25000, "floor": None},
        "adv_ref_vnd": ADV, "per_session_cap_pct_adv": 0.10,
        "opportunistic": {"k": 2.0, "m": 2.0},
        "hard_expiry": {"manual_only": True, "halted": False, "halted_reason": None},
        "ledger": [],
    }
    st.update(over)
    return st


def fixed_state(**over):
    """State chế độ CỐ ĐỊNH (bản gốc 07-24) — dùng cho ca hồi quy."""
    st = pct_state()
    st.pop("target_pct_active_nav")
    st.pop("topup_min_gap_pct_active_nav")
    st.pop("target_basis")
    st["target_qty"] = 400
    st.update(over)
    return st


def run(state, filled, price=20_300.0, nav=974_337_205.0, turnover=BENIGN_TURN):
    return compute_session_order(state, filled, turnover, price, PLAN_DATE, NOW_ISO,
                                 active_nav_vnd=nav)


# ────────────────────────────── A. số học target ──────────────────────────────
def test_resolve():
    print("[A] resolve_target_qty")
    # Chế độ cố định: KHÔNG đụng active_nav, trả đúng target_qty.
    q, info = resolve_target_qty(fixed_state(), active_nav_vnd=None, price_vnd=None)
    check("A1 chế độ cố định trả target_qty=400 dù active_nav=None", q == 400 and info["mode"] == "fixed_qty",
          f"{q} {info}")

    # Ground truth tính TAY: 0,05 × 974.337.205 = 48.716.860,25đ; ÷ 20.300 = 2.399,84cp;
    # làm tròn XUỐNG lô 100 ⇒ 2.300cp.
    q, info = resolve_target_qty(pct_state(), 974_337_205.0, 20_300.0)
    check("A2 SpaceX thật: 5%×974.337.205 ÷ 20.300 → 2.300cp (floor lô)", q == 2300, str(q))
    check("A2b info mang đủ số để tái lập",
          info["target_value_vnd"] == round(0.05 * 974_337_205.0)
          and info["active_nav_vnd"] == 974_337_205.0 and info["price_vnd"] == 20_300.0, str(info))

    # ZaloPay thật: 0,05 × 516.017.365 = 25.800.868,25 ÷ 20.300 = 1.270,98 → 1.200cp.
    q, _ = resolve_target_qty(pct_state(), 516_017_365.0, 20_300.0)
    check("A3 ZaloPay thật: 5%×516.017.365 ÷ 20.300 → 1.200cp", q == 1200, str(q))

    # Đơn điệu: NAV gấp đôi ⇒ target gấp đôi; giá gấp đôi ⇒ target giảm nửa.
    q1, _ = resolve_target_qty(pct_state(), 1_000_000_000.0, 20_000.0)   # 50tr/20k = 2500
    q2, _ = resolve_target_qty(pct_state(), 2_000_000_000.0, 20_000.0)   # 100tr/20k = 5000
    q3, _ = resolve_target_qty(pct_state(), 1_000_000_000.0, 40_000.0)   # 50tr/40k = 1250 → 1200
    check("A4 target tỷ lệ THUẬN với active_nav", (q1, q2) == (2500, 5000), f"{q1},{q2}")
    check("A5 target tỷ lệ NGHỊCH với giá", q3 == 1200, str(q3))

    # Mục tiêu < 1 lô ⇒ FAILSAFE, tuyệt đối KHÔNG trả 0 (0 sẽ bị đọc nhầm là "đã gom đủ").
    q, info = resolve_target_qty(pct_state(), 1_000_000.0, 20_300.0)     # 50.000đ < 1 lô
    check("A6 target < 1 lô ⇒ None (KHÔNG phải 0)", q is None, str(q))
    check("A6b lý do nói rõ 'không đủ để đặt lệnh'", "1 lô" in info["reason"], info.get("reason"))


# ─────────────────────────── B. không có đường fail-OPEN ───────────────────────────
def test_failsafe():
    print("[B] không fail-OPEN")
    bad_navs = [None, 0, -1, True, "974337205", float("nan")]
    for nav in bad_navs:
        order, d = run(pct_state(), 500, nav=nav)
        check(f"B active_nav={nav!r} ⇒ failsafe, KHÔNG có order",
              order is None and d["action"] == "failsafe", f"{d['action']} {order is not None}")
    # inf: mục tiêu vô hạn ⇒ phải chặn ở tầng NÀO ĐÓ, tuyệt đối không ra một lệnh.
    order, d = run(pct_state(), 500, nav=float("inf"))
    check("B active_nav=inf ⇒ KHÔNG có order", order is None, str(d.get("action")))

    # pct sai đơn vị (5 thay vì 0,05) — bị chặn NGAY Ở validate_state (tầng sớm nhất), tức
    # compute_session_order NÉM lỗi chứ không trả một quyết định. Đó là hành vi ĐÚNG: injector
    # gọi validate_state lúc load state (load_active_states) nên state hỏng bị loại trước khi
    # tới đây — xem ca B-e2e bên dưới chứng minh đường thật cũng không ra lệnh.
    try:
        run(pct_state(target_pct_active_nav=5.0), 500)
        check("B pct=5.0 (sai đơn vị) ⇒ compute_session_order NÉM ValueError", False, "không raise")
    except ValueError:
        check("B pct=5.0 (sai đơn vị) ⇒ compute_session_order NÉM ValueError", True)
    try:
        validate_state(pct_state(target_pct_active_nav=5.0))
        check("B validate_state chặn pct sai đơn vị", False, "không raise")
    except ValueError:
        check("B validate_state chặn pct sai đơn vị", True)
    try:
        validate_state(pct_state(target_pct_active_nav=TARGET_PCT_ACTIVE_NAV_MAX))
        check("B validate_state CHO PHÉP pct = đúng trần max", True)
    except ValueError as exc:
        check("B validate_state CHO PHÉP pct = đúng trần max", False, str(exc))
    try:
        validate_state(pct_state(topup_min_gap_pct_active_nav=0.9))
        check("B validate_state chặn deadband ≥ target", False, "không raise")
    except ValueError:
        check("B validate_state chặn deadband ≥ target", True)

    # giá thiếu: tầng 3 của engine đã chặn trước (fail-safe chung), vẫn phải là failsafe.
    order, d = run(pct_state(), 500, price=None)
    check("B giá phiên gần nhất=None ⇒ failsafe", order is None and d["action"] == "failsafe", str(d["action"]))


# ────────────── C. đủ tỷ trọng ⇒ skip, KHÔNG đóng chương trình ──────────────
def test_reached_stays_active():
    print("[C] đạt tỷ trọng ⇒ GIỮ active")
    order, d = run(pct_state(), 2300)          # filled == target
    check("C1 filled == target ⇒ action=skip (không phải completed)",
          order is None and d["action"] == "skip", str(d["action"]))
    check("C2 KHÔNG có cờ mark_completed ⇒ injector không đóng state",
          not d.get("mark_completed"), str(d.get("mark_completed")))
    order, d = run(pct_state(), 9999)          # vượt xa target
    check("C3 filled ≫ target vẫn chỉ skip", order is None and d["action"] == "skip", str(d["action"]))

    # Hồi quy chế độ CỐ ĐỊNH: phải vẫn completed + mark_completed (hành vi cũ nguyên vẹn).
    order, d = run(fixed_state(), 400)
    check("C4 HỒI QUY chế độ cố định: filled==target ⇒ completed + mark_completed",
          order is None and d["action"] == "completed" and d.get("mark_completed") is True, str(d))


# ─────────────────────── D. deadband + ca chứng minh ngược ───────────────────────
def test_deadband():
    print("[D] deadband top-up")
    NAV, PX = 1_000_000_000.0, 20_000.0        # target = 50tr/20k = 2.500cp; deadband = 5tr
    order, d = run(pct_state(), 2400, price=PX, nav=NAV)   # thiếu 100cp = 2tr < 5tr
    check("D1 gap 2tr < ngưỡng 5tr ⇒ skip", order is None and d["action"] == "skip", str(d["action"]))
    check("D1b lý do nêu đúng 'deadband'", "deadband" in d["reason"], d["reason"])

    # CA CHỨNG MINH NGƯỢC: y hệt nhưng BỎ deadband ⇒ thật sự có lệnh. Không có ca này thì
    # "D1 chặn được" có thể chỉ là một fail-safe khác đang chặn hộ (§24 kỷ luật selfcheck).
    st = pct_state(); st.pop("topup_min_gap_pct_active_nav")
    order2, d2 = run(st, 2400, price=PX, nav=NAV)
    check("D2 CHỨNG MINH NGƯỢC: bỏ deadband ⇒ CÓ lệnh 100cp",
          order2 is not None and order2["qty"] == 100 and d2["action"] == "inject",
          f"{d2['action']} {order2 and order2.get('qty')}")

    order, d = run(pct_state(), 2200, price=PX, nav=NAV)   # thiếu 300cp = 6tr > 5tr
    check("D3 gap 6tr > ngưỡng ⇒ inject 300cp",
          order is not None and order["qty"] == 300, f"{d['action']} {order and order.get('qty')}")

    # Biên CHÍNH XÁC: gap == ngưỡng ⇒ vẫn mua (so sánh là ≥, không phải >).
    order, d = run(pct_state(), 2250, price=PX, nav=NAV)   # thiếu 250cp = 5,0tr == ngưỡng
    check("D4 gap == ngưỡng ⇒ inject (so sánh ≥)",
          order is not None and d["action"] == "inject", str(d["action"]))
    check("D4b qty làm tròn XUỐNG lô: 250 → 200", order and order["qty"] == 200,
          str(order and order.get("qty")))


# ─────────────────────────── E. cổng tươi active_nav ───────────────────────────
def test_freshness_gate():
    print("[E] cổng tươi active_nav")
    tmp = tempfile.mkdtemp(prefix="disc_nav_")
    orig = inj.ACTIVE_NAV_DIR
    inj.ACTIVE_NAV_DIR = tmp
    now = dt.datetime(2026, 8, 12, 20, 30)
    path = os.path.join(tmp, "active_nav_SELFCHK.json")
    try:
        nav, info = inj.load_active_nav("SELFCHK", now=now)
        check("E1 thiếu file ⇒ None", nav is None and "chưa có file" in info["reason"], str(info))

        json.dump({"computed_at": "2026-08-12", "active_nav": 974_337_205.0,
                   "cash_basis": "totalCash-totalDebt"}, open(path, "w"))
        nav, info = inj.load_active_nav("SELFCHK", now=now)
        check("E2 computed_at == hôm nay ⇒ trả đúng số", nav == 974_337_205.0, str(info))

        json.dump({"computed_at": "2026-08-11", "active_nav": 974_337_205.0}, open(path, "w"))
        nav, info = inj.load_active_nav("SELFCHK", now=now)
        check("E3 computed_at = HÔM QUA ⇒ None (dung sai chặt, §14)",
              nav is None and "CŨ" in info["reason"], str(info))

        # Cũ 1 ngày mà vẫn qua = đúng cái bug §14 cấm; nên kiểm cả chiều "tương lai".
        json.dump({"computed_at": "2026-08-13", "active_nav": 1.0}, open(path, "w"))
        check("E4 computed_at NGÀY MAI ⇒ None", inj.load_active_nav("SELFCHK", now=now)[0] is None)

        for bad in (0, -5, None, "974337205", True):
            json.dump({"computed_at": "2026-08-12", "active_nav": bad}, open(path, "w"))
            nav, info = inj.load_active_nav("SELFCHK", now=now)
            check(f"E5 active_nav={bad!r} ⇒ None", nav is None, str(info))

        open(path, "w").write("{ khong phai json")
        check("E6 file hỏng ⇒ None (không ném exception)",
              inj.load_active_nav("SELFCHK", now=now)[0] is None)
    finally:
        inj.ACTIVE_NAV_DIR = orig


# ─────────────────────────── F/G. E2E qua injector ───────────────────────────
class FakeQuote:
    def __init__(self, price, vol):
        self.last = price
        self.day_volume = vol
        self.exchange = "UPCOM"


class FakeBroker:
    total = 500
    price = 20_300.0
    day_volume = 20_000.0
    client = None            # ⇒ anchor_prices_for fail-safe về band cố định (có chủ đích)

    def __init__(self, *a, **k):
        pass

    def connect(self):
        return True

    def get_positions(self):
        return {"TV1": {"total": FakeBroker.total}}

    def get_quote(self, sym):
        return FakeQuote(FakeBroker.price, FakeBroker.day_volume)


def _write(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def test_e2e():
    print("[F] E2E qua injector")
    tmp = tempfile.mkdtemp(prefix="disc_e2e_")
    disc_dir = os.path.join(tmp, "discretionary")
    nav_dir = os.path.join(tmp, "nav")
    os.makedirs(disc_dir)
    os.makedirs(nav_dir)
    o_disc, o_plan, o_nav = inj.DISC_DIR, inj.PLAN_DIR, inj.ACTIVE_NAV_DIR
    o_broker = brokers_mod.DNSEBroker
    inj.DISC_DIR, inj.PLAN_DIR, inj.ACTIVE_NAV_DIR = disc_dir, tmp, nav_dir
    brokers_mod.DNSEBroker = FakeBroker

    # secrets shim (giống discretionary_accumulation_selfcheck.py)
    real_secrets = os.path.join(WC_ROOT, "secrets", "trading_bot_accounts.json")
    patched = copy.deepcopy(json.load(open(real_secrets, encoding="utf-8")))
    patched.setdefault("accounts", []).append({"label": "SELFCHK", "account_id": "9999999999"})
    patched_path = os.path.join(tmp, "secrets_accounts.json")
    _write(patched_path, patched)
    _real_join = os.path.join

    def fake_join(*parts):
        if parts and parts[-1] == "trading_bot_accounts.json" and "secrets" in parts:
            return patched_path
        return _real_join(*parts)
    inj.os.path.join = fake_join

    state_path = os.path.join(disc_dir, "state_TV1_SELFCHK.json")
    plan_path = os.path.join(tmp, f"plan_SELFCHK_{PLAN_DATE}.json")
    nav_path = _real_join(nav_dir, "active_nav_SELFCHK.json")
    v24 = {"id": "BUY-PVT-00", "ticker": "PVT", "side": "buy", "qty": 500, "book": "CAPIT",
           "estimated_cost_vnd": 8_475_000}
    today = inj.now_ict().date().isoformat()

    def reset(state, nav_obj):
        _write(state_path, state)
        _write(plan_path, {"plan_date": PLAN_DATE, "account": "SELFCHK", "mode": "paper",
                           "cash_vnd": 500_000_000, "orders": [copy.deepcopy(v24)]})
        if nav_obj is None and os.path.exists(nav_path):
            os.remove(nav_path)
        elif nav_obj is not None:
            _write(nav_path, nav_obj)

    def disc_orders():
        return [o for o in json.load(open(plan_path, encoding="utf-8"))["orders"]
                if o.get("book") == BOOK]

    try:
        fresh_nav = {"computed_at": today, "active_nav": 974_337_205.0,
                     "cash_basis": "totalCash-totalDebt"}

        # F1 — đường sống: target 2.300, đang giữ 500 ⇒ lệnh 1.800cp.
        reset(pct_state(account="SELFCHK"), fresh_nav)
        FakeBroker.total = 500
        rc = inj.process_account("SELFCHK", PLAN_DATE, dry_run=False)
        o = disc_orders()
        check("F1 rc==0 và chèn đúng 1 lệnh", rc == 0 and len(o) == 1, f"rc={rc} n={len(o)}")
        check("F1b qty = 2.300 − 500 = 1.800", o and o[0]["qty"] == 1800, str(o and o[0].get("qty")))
        check("F1c order mang target_rule tái lập được",
              o and o[0]["accumulation_program"]["target_rule"]["target_qty"] == 2300, str(o))
        check("F1d order V2.4 (CAPIT) giữ nguyên",
              [x for x in json.load(open(plan_path, encoding="utf-8"))["orders"]
               if x.get("book") == "CAPIT"] == [v24])
        check("F1e state VẪN active sau khi chèn",
              json.load(open(state_path, encoding="utf-8"))["status"] == "active")

        # F2 — active_nav CŨ ⇒ không lệnh nào + lý do ghi thẳng vào plan (không im lặng).
        reset(pct_state(account="SELFCHK"), {"computed_at": "2000-01-01", "active_nav": 1e9})
        inj.process_account("SELFCHK", PLAN_DATE, dry_run=False)
        plan = json.load(open(plan_path, encoding="utf-8"))
        check("F2 active_nav cũ ⇒ 0 lệnh discretionary", len(disc_orders()) == 0)
        check("F2b plan có discretionary_inject_notes giải thích vì sao vắng lệnh",
              len(plan.get("discretionary_inject_notes", [])) == 1
              and plan["discretionary_inject_notes"][0]["ticker"] == "TV1",
              str(plan.get("discretionary_inject_notes")))

        # F3 — thiếu HẲN file active_nav ⇒ vẫn fail-safe, không rơi về số cũ.
        reset(pct_state(account="SELFCHK"), None)
        inj.process_account("SELFCHK", PLAN_DATE, dry_run=False)
        check("F3 thiếu file active_nav ⇒ 0 lệnh", len(disc_orders()) == 0)

        # F4 — đã đủ tỷ trọng ⇒ 0 lệnh NHƯNG state KHÔNG bị đóng (khác chế độ cố định).
        reset(pct_state(account="SELFCHK"), fresh_nav)
        FakeBroker.total = 2300
        inj.process_account("SELFCHK", PLAN_DATE, dry_run=False)
        check("F4 đủ tỷ trọng ⇒ 0 lệnh", len(disc_orders()) == 0)
        check("F4b state VẪN active (không completed) ⇒ phiên sau còn đo lại",
              json.load(open(state_path, encoding="utf-8"))["status"] == "active",
              json.load(open(state_path, encoding="utf-8")).get("status"))

        # F5 — idempotent: chạy lại không chèn trùng.
        reset(pct_state(account="SELFCHK"), fresh_nav)
        FakeBroker.total = 500
        inj.process_account("SELFCHK", PLAN_DATE, dry_run=False)
        inj.process_account("SELFCHK", PLAN_DATE, dry_run=False)
        check("F5 chạy 2 lần ⇒ vẫn đúng 1 lệnh", len(disc_orders()) == 1, str(len(disc_orders())))

        # F5b — state pct SAI ĐƠN VỊ trên đường THẬT: load_active_states loại nó (validate_state
        # ném), injector không sập và KHÔNG chèn lệnh nào. Đây là ca e2e của [B] pct=5.0.
        reset(pct_state(account="SELFCHK", target_pct_active_nav=5.0), fresh_nav)
        rc = inj.process_account("SELFCHK", PLAN_DATE, dry_run=False)
        check("F5b state pct sai đơn vị ⇒ injector rc==0, 0 lệnh (state bị loại, không sập)",
              rc == 0 and len(disc_orders()) == 0, f"rc={rc} n={len(disc_orders())}")

        # F6 — dry-run KHÔNG ghi gì.
        reset(pct_state(account="SELFCHK"), fresh_nav)
        before_state = open(state_path, encoding="utf-8").read()
        before_plan = open(plan_path, encoding="utf-8").read()
        inj.process_account("SELFCHK", PLAN_DATE, dry_run=True)
        check("F6 dry-run không đổi plan lẫn state",
              open(state_path, encoding="utf-8").read() == before_state
              and open(plan_path, encoding="utf-8").read() == before_plan)

        # G — HỒI QUY: state target CỐ ĐỊNH chạy y như cũ, KHÔNG cần active_nav.
        print("[G] hồi quy chế độ cố định")
        reset(fixed_state(account="SELFCHK"), None)     # cố tình KHÔNG có file active_nav
        FakeBroker.total = 200
        inj.process_account("SELFCHK", PLAN_DATE, dry_run=False)
        o = disc_orders()
        check("G1 target cố định 400, filled 200 ⇒ lệnh 200cp dù KHÔNG có active_nav",
              len(o) == 1 and o[0]["qty"] == 200, str(o and o[0].get("qty")))
        reset(fixed_state(account="SELFCHK"), None)
        FakeBroker.total = 400
        inj.process_account("SELFCHK", PLAN_DATE, dry_run=False)
        check("G2 target cố định đủ hàng ⇒ state ĐÓNG (completed) như cũ",
              json.load(open(state_path, encoding="utf-8"))["status"] == "completed",
              json.load(open(state_path, encoding="utf-8")).get("status"))
    finally:
        inj.os.path.join = _real_join
        inj.DISC_DIR, inj.PLAN_DIR, inj.ACTIVE_NAV_DIR = o_disc, o_plan, o_nav
        brokers_mod.DNSEBroker = o_broker


# ───────────── I. TRẦN NGÂN SÁCH PHIÊN — bất biến bằng TIỀN (có ca chứng minh ngược) ─────────────
# Vì sao khối này tồn tại: vòng quant-skeptic 1 (2026-08-12) bác đúng một chỗ — trần ngân sách
# được rao là 1 trong 4 trụ thiết kế VÀ là lớp DUY NHẤT đứng giữa một feed sai đơn vị và một lệnh
# phình 100×, nhưng lúc đó KHÔNG có ca test nào trong toàn repo, và 2 con số minh hoạ chỉ sống
# trong comment mã nguồn. Ở đây chúng được đo LẠI bằng ca chạy được, và comment trong
# `discretionary_accumulation.py` nay trỏ về đúng tên ca dưới đây thay vì một con số mồ côi.
def test_session_budget_cap():
    print("[I] trần ngân sách phiên (bất biến bằng TIỀN)")
    import trading_bot.discretionary_accumulation as da

    DYN = {"enabled": True, "tau": 0.03, "sessions": 5}
    BIG_ADV = 5_000_000_000          # để trần %ADV KHÔNG bind — cô lập đúng trần ngân sách

    def measure(state, filled, price, nav, anchors, slack=None):
        """Chạy 1 phiên, trả (order, decision, chi phí xấu nhất / nav). `slack=None` ⇒ dùng
        trần thật; truyền số lớn ⇒ VÔ HIỆU trần (ca chứng minh ngược)."""
        old = da.SESSION_BUDGET_CAP_SLACK
        if slack is not None:
            da.SESSION_BUDGET_CAP_SLACK = slack
        try:
            o, d = compute_session_order(state, filled, BENIGN_TURN, price, PLAN_DATE, NOW_ISO,
                                         anchor_prices=anchors, active_nav_vnd=nav)
        finally:
            da.SESSION_BUDGET_CAP_SLACK = old
        cost = (o["qty"] * o["limit_price_vnd"]) if o else 0
        return o, d, cost / nav

    # ── I-a. THỊ TRƯỜNG RƠI NHANH: trần động neo TRUNG BÌNH 5 phiên, target neo giá phiên CUỐI.
    # Hai mốc giá lệch pha ⇒ số lượng suy từ giá thấp mà tiền trả theo giá cao.
    NAV = 1_000_000_000.0
    FALL = [24_000.0, 23_000.0, 22_000.0, 20_000.0, 14_000.0]   # anchor cũ→mới
    LAST = 14_000.0                                             # giá phiên cuối (mẫu số target)
    st = pct_state(adv_ref_vnd=BIG_ADV, dynamic_ceiling=DYN,
                   price_band={"resting_limit": 19900, "no_chase_ceiling": 20000,
                               "max_no_chase_ceiling": 25000, "floor": None})

    o_off, d_off, pct_off = measure(st, 0, LAST, NAV, FALL, slack=1e9)   # CHỨNG MINH NGƯỢC
    check("I1 CHỨNG MINH NGƯỢC: bỏ trần ngân sách ⇒ lệnh THẬT SỰ vượt mục tiêu "
          f"(đo được {pct_off:.2%} NAV trên mục tiêu 5%)",
          o_off is not None and pct_off > 0.06, f"{pct_off:.4%}")

    o_on, d_on, pct_on = measure(st, 0, LAST, NAV, FALL)
    shrink = d_on.get("session_budget_shrink")
    check(f"I2 CÓ trần ⇒ chi phí ≤ 1,03 × mục tiêu (đo được {pct_on:.2%} NAV)",
          o_on is not None and pct_on <= 0.05 * (1 + da.SESSION_BUDGET_CAP_SLACK) + 1e-9,
          f"{pct_on:.4%}")
    check("I3 lệnh bị CO chứ không bị huỷ, và việc co được ghi lại thành số",
          o_on is not None and shrink is not None
          and shrink["to_qty"] < shrink["from_qty"] == o_off["qty"],
          str(shrink))
    check("I4 trần ngân sách CHẶT HƠN trần %ADV trong ca này (đúng lớp đang được đo)",
          o_on["qty"] < d_on["cap_qty"], f"{o_on['qty']} vs cap_qty={d_on['cap_qty']}")

    # ── I-b. FEED SAI ĐƠN VỊ: giá về ÷100 ⇒ target nở 100×. Guard sanity đơn vị chỉ tồn tại ở
    # nhánh TRẦN (resolve_price_band ⇒ fail-safe về band cố định), KHÔNG ở nhánh TARGET — nên
    # nếu trần ngân sách không đứng đây thì không còn gì đứng cả.
    NAV2 = 974_337_205.0
    GOOD = [19_500.0, 19_700.0, 19_800.0, 20_200.0, 20_300.0]
    BAD_PX = 203.0                                              # đúng 20.300 ÷ 100
    st2 = pct_state(adv_ref_vnd=BIG_ADV, dynamic_ceiling=DYN,
                    price_band={"resting_limit": 19900, "no_chase_ceiling": 20000,
                                "max_no_chase_ceiling": 25000, "floor": None})
    q_bad, _ = resolve_target_qty(st2, NAV2, BAD_PX)
    q_ok, _ = resolve_target_qty(st2, NAV2, 20_300.0)
    check(f"I5 sai đơn vị làm target nở đúng ~100× ({q_ok:,}cp → {q_bad:,}cp)",
          q_bad >= 90 * q_ok, f"{q_ok} → {q_bad}")

    o_off2, _, pct_off2 = measure(st2, 0, BAD_PX, NAV2, GOOD, slack=1e9)
    check("I6 CHỨNG MINH NGƯỢC: bỏ trần ngân sách ⇒ lệnh sai-đơn-vị phình tới "
          f"{pct_off2:.2%} NAV", o_off2 is not None and pct_off2 > 0.10, f"{pct_off2:.4%}")

    o_on2, d_on2, pct_on2 = measure(st2, 0, BAD_PX, NAV2, GOOD)
    check(f"I7 CÓ trần ⇒ kéo về ≤ 1,03 × mục tiêu (đo được {pct_on2:.2%} NAV)",
          pct_on2 <= 0.05 * (1 + da.SESSION_BUDGET_CAP_SLACK) + 1e-9, f"{pct_on2:.4%}")

    # ── I-b2. CÙNG ca sai đơn vị nhưng ở adv_ref THẬT (720tr) — tức bán kính vụ nổ THẬT.
    # Vì sao phải có cặp này bên cạnh I6/I7: I6 cố ý thổi ADV lên 5 tỷ để CÔ LẬP trần ngân
    # sách, nên 51,26% là số của một giàn thí nghiệm, KHÔNG phải của cấu hình production.
    # `cap_vnd = per_session_cap_pct_adv × adv_ref_vnd` là một bờ tính bằng TIỀN nên nó MIỄN
    # NHIỄM với lỗi đơn vị giá ⇒ trần %ADV mới là bờ NGOÀI, trần ngân sách là bờ TRONG chặt
    # hơn. Nói "lớp duy nhất" là sai thứ tự lớp (quant-skeptic vòng 2 bác đúng chỗ này).
    st3 = pct_state(dynamic_ceiling=DYN,
                    price_band={"resting_limit": 19900, "no_chase_ceiling": 20000,
                                "max_no_chase_ceiling": 25000, "floor": None})   # adv_ref THẬT
    o_r_off, d_r_off, pct_r_off = measure(st3, 0, BAD_PX, NAV2, GOOD, slack=1e9)
    cap_vnd_real = st3["per_session_cap_pct_adv"] * st3["adv_ref_vnd"]
    check("I10 BỜ NGOÀI: bỏ trần ngân sách ở adv_ref THẬT ⇒ trần %ADV vẫn giữ chi phí "
          f"≤ cap_vnd {cap_vnd_real:,.0f}đ (đo được {pct_r_off:.2%} NAV)",
          o_r_off is not None and o_r_off["qty"] * o_r_off["limit_price_vnd"] <= cap_vnd_real,
          f"{pct_r_off:.4%}")
    check("I11 trần %ADV MIỄN NHIỄM lỗi đơn vị giá (nó là bờ bằng TIỀN, không bằng số cp)",
          pct_r_off < 0.10, f"{pct_r_off:.4%} — nếu ≥10% thì bờ ngoài đã thủng")

    o_r_on, d_r_on, pct_r_on = measure(st3, 0, BAD_PX, NAV2, GOOD)
    check(f"I12 BỜ TRONG: trần ngân sách siết tiếp {pct_r_off:.2%} → {pct_r_on:.2%} NAV",
          pct_r_on < pct_r_off
          and pct_r_on <= 0.05 * (1 + da.SESSION_BUDGET_CAP_SLACK) + 1e-9,
          f"{pct_r_off:.4%} → {pct_r_on:.4%}")

    # ── I-c. Trần KHÔNG được đụng vào lệnh hợp lệ. Nếu nó bind ở ca thật thì nó là một núm
    # sizing lén, không phải lưới an toàn — đây là ca phân biệt hai thứ đó.
    o_ok, d_ok, pct_ok = measure(pct_state(dynamic_ceiling=DYN,
                                           price_band={"resting_limit": 19900,
                                                       "no_chase_ceiling": 20000,
                                                       "max_no_chase_ceiling": 25000,
                                                       "floor": None}),
                                 500, 20_300.0, 974_337_205.0, GOOD)
    check("I8 ca THẬT (SpaceX 08-13: giữ 500, target 2300) ⇒ 1800cp, trần ngân sách KHÔNG bind",
          o_ok is not None and o_ok["qty"] == 1800
          and d_ok.get("session_budget_shrink") is None,
          f"{o_ok and o_ok.get('qty')} shrink={d_ok.get('session_budget_shrink')}")

    # ── I-d. Co xuống dưới 1 lô ⇒ BỎ phiên, không đặt lệnh rác.
    tiny = pct_state(adv_ref_vnd=BIG_ADV, dynamic_ceiling=DYN, lot_size=1000,
                     price_band={"resting_limit": 19900, "no_chase_ceiling": 20000,
                                 "max_no_chase_ceiling": 25000, "floor": None})
    o_t, d_t, _ = measure(tiny, 0, 203.0, 30_000_000.0, GOOD)
    check("I9 co xuống dưới 1 lô ⇒ skip có lý do, KHÔNG ra lệnh",
          o_t is None and d_t["action"] == "skip" and "ngân sách" in d_t["reason"],
          f"{d_t['action']}: {d_t['reason'][:80]}")


# ───────────── J. hồi quy CHỮ KÝ load_active_states (bug đã giết injector 2026-08-12) ─────────────
def test_loader_signature():
    print("[J] chữ ký load_active_states — hồi quy bug (b)")
    # Bug thật: hàm đổi sang trả (out, skipped) mà caller giữ nguyên `states = load_...` ⇒
    # `if not states` luôn sai (tuple luôn truthy) rồi `for _, s in states` ném ValueError ⇒
    # injector CHẾT NGAY LỐI VÀO cho mọi account. Ca này neo cả hai đầu của hợp đồng để một
    # lần đổi chữ ký sau này không thể lặng lẽ giết lại injector.
    import inspect
    with tempfile.TemporaryDirectory() as td:
        old_dir = inj.DISC_DIR
        inj.DISC_DIR = td
        try:
            ret = inj.load_active_states("NOBODY")
        finally:
            inj.DISC_DIR = old_dir
    check("J1 trả TUPLE 2 phần tử (active, skipped)",
          isinstance(ret, tuple) and len(ret) == 2, str(type(ret)))
    check("J2 cả hai phần tử là list", all(isinstance(x, list) for x in ret), str(ret))
    src = inspect.getsource(inj.process_account)
    check("J3 caller UNPACK 2 biến (không nhận nguyên tuple)",
          "states, skipped_states = load_active_states(" in src,
          "process_account không unpack — injector sẽ ném ValueError ở vòng lặp đầu")


# ───────────────────────── H. state THẬT đang dùng cho tiền thật ─────────────────────────
def test_real_state_files():
    """§23 quy ước 1: selfcheck KHÔNG assert lên TRẠNG THÁI SỐNG.

    Chia làm hai. Trên file THẬT chỉ kiểm BẤT BIẾN — thứ phải đúng dù chương trình đang chạy,
    đã dừng, hay bị `halted` bởi một catalyst pháp lý thật. Trên FIXTURE ĐÓNG BĂNG mới kiểm
    GIÁ TRỊ cấu hình đã duyệt. Bản cũ (vòng 1) kiểm `status=="active"` / `halted is False`
    thẳng trên file production ⇒ một lần `halted=true` HỢP LỆ (đúng thiết kế: người xác nhận
    tin kiểm toán rồi dừng chương trình) sẽ làm bộ test đỏ và biến nó thành nhiễu nền.
    """
    print("[H] state file THẬT — chỉ BẤT BIẾN (§23)")
    from trading_bot.discretionary_accumulation import resolve_price_band
    for acct in ("SpaceX", "ZaloPay"):
        p = os.path.join(WC_ROOT, "data", "trade_plans", "discretionary",
                         f"state_TV1_{acct}.json")
        st = json.load(open(p, encoding="utf-8"))
        check(f"H {acct}: validate_state PASS", validate_state(st) is True)
        check(f"H {acct}: account khớp tên file", st["account"] == acct, st.get("account"))
        check(f"H {acct}: ticker khớp tên file", st.get("ticker") == "TV1", st.get("ticker"))
        # Trần tuyệt đối là quyết định CHÍNH SÁCH của user — nới nó phải là một hành động có
        # chủ đích của người, nên "không vượt 25.000đ" là bất biến, còn "đúng bằng" thì không.
        check(f"H {acct}: trần tuyệt đối ≤ 25.000đ (mức user duyệt 08-12)",
              float(st["price_band"]["max_no_chase_ceiling"]) <= 25000,
              str(st["price_band"].get("max_no_chase_ceiling")))
        ceil, rest, info = resolve_price_band(st, [99_000.0] * 5, 99_000.0)
        check(f"H {acct}: anchor 99.000 vẫn bị kẹp ≤ trần tuyệt đối (hoặc fail-safe band cố định)",
              ceil <= float(st["price_band"]["max_no_chase_ceiling"]) and rest <= ceil,
              f"{ceil}/{rest} {info.get('mode')}")
        if st.get("target_pct_active_nav") is not None:
            # NAV thăm dò CỐ ĐỊNH (không phải NAV thật của account này) — ta đang kiểm bất biến
            # "ra bội số của lô", không phải giá trị target hôm nay.
            q, _ = resolve_target_qty(st, 1_000_000_000.0, 20_300.0)
            check(f"H {acct}: mode tỷ trọng ⇒ target ra bội số của lô ({q}cp @NAV thăm dò 1 tỷ)",
                  q and q > 0 and q % st["lot_size"] == 0, str(q))

    print("[H2] FIXTURE đóng băng — giá trị cấu hình đã duyệt 2026-08-12")
    for acct in ("SpaceX", "ZaloPay"):
        fx = os.path.join(WC_ROOT, "data", "fixtures", f"state_TV1_{acct}_pct_20260812.json")
        st = json.load(open(fx, encoding="utf-8"))
        check(f"H2 {acct}: status=active", st["status"] == "active", st.get("status"))
        check(f"H2 {acct}: target 5% active_nav", st["target_pct_active_nav"] == 0.05,
              str(st.get("target_pct_active_nav")))
        check(f"H2 {acct}: trần tuyệt đối = 25.000đ", st["price_band"]["max_no_chase_ceiling"] == 25000,
              str(st["price_band"].get("max_no_chase_ceiling")))
        check(f"H2 {acct}: trần động BẬT, tau=3%, 5 phiên",
              st["dynamic_ceiling"]["enabled"] is True and st["dynamic_ceiling"]["tau"] == 0.03
              and st["dynamic_ceiling"]["sessions"] == 5, str(st.get("dynamic_ceiling")))
        check(f"H2 {acct}: baseline=0 (400cp chương trình cũ TÍNH vào 5%)",
              st["baseline_qty_before_program"] == 0, str(st.get("baseline_qty_before_program")))
        check(f"H2 {acct}: chưa halted", st["hard_expiry"]["halted"] is False)
        check(f"H2 {acct}: deadband 0,5% active_nav",
              st["topup_min_gap_pct_active_nav"] == 0.005,
              str(st.get("topup_min_gap_pct_active_nav")))


if __name__ == "__main__":
    print(f"TZ env = {os.environ.get('TZ', '(không đặt)')}")
    test_resolve()
    test_failsafe()
    test_reached_stays_active()
    test_deadband()
    test_freshness_gate()
    test_e2e()
    test_session_budget_cap()
    test_loader_signature()
    test_real_state_files()
    print(f"\n=== SELFCHECK: {PASS} passed, {FAIL} failed ===")
    sys.exit(1 if FAIL else 0)
