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


# ───────────────────────── H. state THẬT đang dùng cho tiền thật ─────────────────────────
def test_real_state_files():
    print("[H] state file THẬT (SpaceX/ZaloPay)")
    for acct, nav_hint in (("SpaceX", 974_337_205.0), ("ZaloPay", 516_017_365.0)):
        p = os.path.join(WC_ROOT, "data", "trade_plans", "discretionary",
                         f"state_TV1_{acct}.json")
        st = json.load(open(p, encoding="utf-8"))
        check(f"H {acct}: validate_state PASS", validate_state(st) is True)
        check(f"H {acct}: status=active", st["status"] == "active", st.get("status"))
        check(f"H {acct}: target 5% active_nav", st["target_pct_active_nav"] == 0.05,
              str(st.get("target_pct_active_nav")))
        check(f"H {acct}: trần tuyệt đối = 25.000đ (user duyệt 08-12)",
              st["price_band"]["max_no_chase_ceiling"] == 25000,
              str(st["price_band"].get("max_no_chase_ceiling")))
        check(f"H {acct}: trần động BẬT, tau=3%, 5 phiên",
              st["dynamic_ceiling"]["enabled"] is True and st["dynamic_ceiling"]["tau"] == 0.03
              and st["dynamic_ceiling"]["sessions"] == 5, str(st.get("dynamic_ceiling")))
        check(f"H {acct}: baseline=0 (400cp chương trình cũ TÍNH vào 5%)",
              st["baseline_qty_before_program"] == 0, str(st.get("baseline_qty_before_program")))
        check(f"H {acct}: account khớp tên file", st["account"] == acct, st.get("account"))
        check(f"H {acct}: chưa halted", st["hard_expiry"]["halted"] is False)
        # trần động không bao giờ được vượt trần tuyệt đối, kể cả khi anchor bay lên trời
        from trading_bot.discretionary_accumulation import resolve_price_band
        ceil, rest, info = resolve_price_band(st, [99_000.0] * 5, 99_000.0)
        check(f"H {acct}: anchor 99.000 vẫn bị kẹp ≤ 25.000 (hoặc fail-safe về band cố định)",
              ceil <= 25000 and rest <= ceil, f"{ceil}/{rest} {info.get('mode')}")
        # số cp mục tiêu với NAV thật hôm nay phải ra một lệnh có nghĩa
        q, _ = resolve_target_qty(st, nav_hint, 20_300.0)
        check(f"H {acct}: target với active_nav thật = {q}cp (>0, chia hết lô)",
              q and q > 0 and q % st["lot_size"] == 0, str(q))


if __name__ == "__main__":
    print(f"TZ env = {os.environ.get('TZ', '(không đặt)')}")
    test_resolve()
    test_failsafe()
    test_reached_stays_active()
    test_deadband()
    test_freshness_gate()
    test_e2e()
    test_real_state_files()
    print(f"\n=== SELFCHECK: {PASS} passed, {FAIL} failed ===")
    sys.exit(1 if FAIL else 0)
