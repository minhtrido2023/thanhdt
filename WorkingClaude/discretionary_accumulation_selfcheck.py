#!/usr/bin/env python3
"""discretionary_accumulation_selfcheck.py — selfcheck cho playbook Low-Liquidity
Discretionary Accumulation (engine + injector). Chạy: python3 discretionary_accumulation_selfcheck.py

Bao phủ đúng 5 yêu cầu bắt buộc của dispatch + bất biến no-chase:
  (a) opportunistic trigger đúng điều kiện (turnover ≥ k×adv_ref VÀ giá ≤ ceiling)
  (b) không chèn lệnh trùng / không đếm sai filled khi chạy lại (idempotent)
  (c) fail-safe khi thiếu broker/giá/KL (KHÔNG mua bởi thiếu thông tin)
  (d) KHÔNG chạm V2.4 book (chỉ append order book=DISCRETIONARY_SPECIAL, order V2.4 giữ nguyên)
  (e) dừng khi đủ target (không mua quá)
Cộng: no-chase invariant, lot rounding, per-session cap, validate_state.
"""
import copy
import json
import os
import sys
import tempfile

WC_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC_ROOT)
sys.path.insert(0, os.path.join(WC_ROOT, "mike", "bin"))

from trading_bot.discretionary_accumulation import compute_session_order, validate_state, BOOK
import trading_bot.brokers as brokers_mod
import discretionary_accumulation_inject as inj

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")


def base_state():
    return {
        "ticker": "TV1", "account": "SpaceX", "book": BOOK, "status": "active",
        "target_qty": 400, "min_acceptable_qty": 200, "baseline_qty_before_program": 0,
        "lot_size": 100, "priority": 5,
        "price_band": {"resting_limit": 19900, "no_chase_ceiling": 20000, "floor": None},
        "adv_ref_vnd": 701_000_000, "per_session_cap_pct_adv": 0.10,
        "opportunistic": {"k": 2.0, "m": 2.0},
        "soft_window_sessions": 20, "soft_window_start_date": "2026-07-27",
        "hard_expiry": {"manual_only": True, "halted": False, "halted_reason": None},
        "ledger": [],
    }


ADV = 701_000_000
BENIGN_TURN = 0.5 * ADV   # phiên bình thường (< k×adv_ref)
BLOCK_TURN = 2.5 * ADV    # phiên có "bán thật" (> k×adv_ref)


# ─────────────────────────── ENGINE TESTS ───────────────────────────
def test_engine():
    print("[ENGINE]")

    # (e) đủ target → completed, không mua quá
    s = base_state()
    o, d = compute_session_order(s, 400, BENIGN_TURN, 19900, "2026-07-28", "T")
    check("(e) filled==target → completed, order None", o is None and d["action"] == "completed", str(d))
    o, d = compute_session_order(s, 450, BENIGN_TURN, 19900, "2026-07-28", "T")
    check("(e) filled>target → completed (không mua quá)", o is None and d["action"] == "completed", str(d))

    # base accumulation phiên thường
    o, d = compute_session_order(s, 200, BENIGN_TURN, 19900, "2026-07-27", "T")
    check("base: filled 200/400 → inject", o is not None and d["action"] == "inject", str(d))
    check("base: qty = remaining 200 (cap không bind)", o and o["qty"] == 200, str(o and o["qty"]))
    check("no-chase: limit ≤ ceiling", o and o["limit_price_vnd"] <= 20000, str(o))
    check("(d) order book == DISCRETIONARY_SPECIAL", o and o["book"] == BOOK, str(o and o.get("book")))
    check("order stop_exempt & slot_exempt & outside_v24", o and o["stop_exempt"] and o["slot_exempt"] and o["outside_v24_system"], str(o))

    # (a) opportunistic: turnover ≥ k×adv_ref VÀ giá ≤ ceiling → boost
    o1, d1 = compute_session_order(s, 0, BENIGN_TURN, 19900, "2026-07-27", "T")
    o2, d2 = compute_session_order(s, 0, BLOCK_TURN, 19900, "2026-07-27", "T")
    check("(a) benign turnover → opportunistic False", d1["opportunistic"] is False, str(d1))
    check("(a) block turnover (≥2×adv) + giá≤ceiling → opportunistic True", d2["opportunistic"] is True, str(d2))
    check("(a) opportunistic boost tăng cap (cap2 == 2×cap1)", d2["cap_qty"] == 2 * d1["cap_qty"], f"{d1['cap_qty']} vs {d2['cap_qty']}")
    # giá > ceiling thì KHÔNG opportunistic dù turnover cao
    o3, d3 = compute_session_order(s, 0, BLOCK_TURN, 20500, "2026-07-27", "T")
    check("(a) turnover cao nhưng giá>ceiling → opportunistic False", d3["opportunistic"] is False, str(d3))

    # per-session cap binding: hạ adv_ref rất thấp để cap < remaining
    s2 = base_state(); s2["adv_ref_vnd"] = 2_000_000  # 10% = 200k VND → 200k/19900≈10cp → 0 lô (floor 100)
    o, d = compute_session_order(s2, 0, 1_000, 19900, "2026-07-27", "T")
    check("cap: adv_ref siêu nhỏ → cap_qty=0 → skip (không cưỡng chèn)", o is None and d["action"] == "skip", str(d))
    s3 = base_state(); s3["adv_ref_vnd"] = 40_000_000  # 10%=4M → 4M/19900≈201 → 200cp lô
    o, d = compute_session_order(s3, 0, 1_000, 19900, "2026-07-27", "T")
    check("cap: bind → qty=min(remaining400, cap200)=200", o and o["qty"] == 200, str(o and o.get("qty")))
    check("cap: qty là bội của lot_size", o and o["qty"] % 100 == 0, str(o))

    # (c) fail-safe
    o, d = compute_session_order(s, None, BENIGN_TURN, 19900, "2026-07-27", "T")
    check("(c) filled None (broker fail) → failsafe, order None", o is None and d["action"] == "failsafe", str(d))
    o, d = compute_session_order(s, 100, None, 19900, "2026-07-27", "T")
    check("(c) turnover None → failsafe", o is None and d["action"] == "failsafe", str(d))
    o, d = compute_session_order(s, 100, BENIGN_TURN, None, "2026-07-27", "T")
    check("(c) price None → failsafe", o is None and d["action"] == "failsafe", str(d))

    # halted / inactive
    sh = base_state(); sh["hard_expiry"]["halted"] = True; sh["hard_expiry"]["halted_reason"] = "audit adverse"
    o, d = compute_session_order(sh, 100, BENIGN_TURN, 19900, "2026-07-27", "T")
    check("halted → order None, action halted", o is None and d["action"] == "halted", str(d))
    si = base_state(); si["status"] = "completed"
    o, d = compute_session_order(si, 100, BENIGN_TURN, 19900, "2026-07-27", "T")
    check("status inactive → order None", o is None and d["action"] == "inactive", str(d))

    # validate_state: no-chase invariant vi phạm → raise
    sv = base_state(); sv["price_band"]["resting_limit"] = 21000  # > ceiling
    try:
        validate_state(sv); ok = False
    except ValueError:
        ok = True
    check("validate_state: resting_limit>ceiling → raise (bảo vệ no-chase)", ok)


# ─────────────────────────── INJECTOR TESTS ───────────────────────────
class FakeQuote:
    def __init__(self, last, day_volume):
        self.last = last
        self.day_volume = day_volume


class FakeBroker:
    """Mock DNSEBroker cho selfcheck — không mạng. Tham số qua class attr set trước."""
    total = 0
    price = 19900.0
    day_volume = 30000.0
    fail_positions = False
    fail_quote = False

    def __init__(self, *a, **k):
        pass

    def connect(self):
        pass

    def get_positions(self):
        if FakeBroker.fail_positions:
            raise RuntimeError("mock positions fail")
        if FakeBroker.total <= 0:
            return {}
        return {"TV1": {"total": FakeBroker.total, "sellable": FakeBroker.total}}

    def get_quote(self, sym):
        if FakeBroker.fail_quote:
            raise RuntimeError("mock quote fail")
        return FakeQuote(FakeBroker.price, FakeBroker.day_volume)


def _write(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def test_injector():
    print("[INJECTOR]")
    tmp = tempfile.mkdtemp(prefix="disc_selfcheck_")
    disc_dir = os.path.join(tmp, "discretionary")
    plan_dir = tmp
    os.makedirs(disc_dir)

    # patch module globals → isolate khỏi data thật
    inj.DISC_DIR = disc_dir
    inj.PLAN_DIR = plan_dir
    brokers_mod.DNSEBroker = FakeBroker
    # patch account profile lookup: process_account đọc secrets thật → thay bằng shim
    orig_open = open  # noqa

    # state file (dùng account "SELFCHK" để không đụng account thật)
    st = base_state(); st["account"] = "SELFCHK"
    state_path = os.path.join(disc_dir, "state_TV1_SELFCHK.json")
    _write(state_path, st)

    # plan file với 1 order V2.4 sẵn có (để test (d) không đụng)
    plan_date = "2026-07-27"
    v24_order = {"id": "BUY-PVT-00", "ticker": "PVT", "side": "buy", "qty": 500,
                 "book": "CAPIT", "estimated_cost_vnd": 8475000}
    plan_path = os.path.join(plan_dir, f"plan_SELFCHK_{plan_date}.json")
    _write(plan_path, {"plan_date": plan_date, "account": "SELFCHK", "orders": [copy.deepcopy(v24_order)]})

    # shim secrets: process_account đọc secrets/trading_bot_accounts.json — tạo profile giả
    secrets_dir = os.path.join(WC_ROOT, "secrets")
    real_secrets = os.path.join(secrets_dir, "trading_bot_accounts.json")
    # thay vì sửa file thật, monkeypatch json.load-path bằng cách override process_account's
    # profile read: đơn giản nhất — set env account_no qua monkeypatch của hàm.
    # process_account đọc trực tiếp file; ta patch bằng cách chèn account SELFCHK vào bản sao tmp
    # và trỏ biến. Nhưng đường dẫn hardcode → dùng cách patch open cho riêng path đó.
    import builtins
    real_data = json.load(open(real_secrets, encoding="utf-8"))
    patched = copy.deepcopy(real_data)
    patched.setdefault("accounts", []).append({"label": "SELFCHK", "account_id": "9999999999"})
    _patched_secrets_path = os.path.join(tmp, "secrets_accounts.json")
    _write(_patched_secrets_path, patched)
    _real_join = os.path.join

    def fake_join(*parts):
        if parts and parts[-1] == "trading_bot_accounts.json" and "secrets" in parts:
            return _patched_secrets_path
        return _real_join(*parts)
    inj.os.path.join = fake_join

    try:
        # SCENARIO 1: filled 200/400, benign turnover → inject 200
        FakeBroker.total = 200; FakeBroker.price = 19900.0; FakeBroker.day_volume = 30000.0
        rc = inj.process_account("SELFCHK", plan_date, dry_run=False)
        plan = json.load(open(plan_path, encoding="utf-8"))
        disc = [o for o in plan["orders"] if o.get("book") == BOOK]
        v24 = [o for o in plan["orders"] if o.get("book") == "CAPIT"]
        check("inject rc==0", rc == 0)
        check("scenario1: đúng 1 order DISCRETIONARY chèn vào", len(disc) == 1, f"got {len(disc)}")
        check("scenario1: qty = remaining 200", disc and disc[0]["qty"] == 200, str(disc and disc[0].get("qty")))
        check("(d) order V2.4 (CAPIT) GIỮ NGUYÊN, không bị đụng", len(v24) == 1 and v24[0] == v24_order, str(v24))
        st_after = json.load(open(state_path, encoding="utf-8"))
        check("scenario1: ledger có đúng 1 bản ghi plan_date", len([e for e in st_after["ledger"] if e["plan_date"] == plan_date]) == 1, str(st_after["ledger"]))

        # (b) IDEMPOTENT: chạy lại — KHÔNG chèn trùng, KHÔNG đếm 2 lần
        rc2 = inj.process_account("SELFCHK", plan_date, dry_run=False)
        plan2 = json.load(open(plan_path, encoding="utf-8"))
        disc2 = [o for o in plan2["orders"] if o.get("book") == BOOK]
        st2 = json.load(open(state_path, encoding="utf-8"))
        check("(b) rerun: vẫn đúng 1 order DISCRETIONARY (không chèn trùng)", len(disc2) == 1, f"got {len(disc2)}")
        check("(b) rerun: ledger vẫn 1 bản ghi (không đếm 2 lần)", len(st2["ledger"]) == len(st_after["ledger"]), f"{len(st_after['ledger'])}→{len(st2['ledger'])}")

        # (b') filled KHÔNG tăng ảo: dù đã inject 200 (pending, chưa khớp), broker vẫn 200 →
        # nếu xoá order khỏi plan & chạy lại, remaining vẫn tính từ broker=200 (không +200 ảo)
        plan2["orders"] = [o for o in plan2["orders"] if o.get("book") != BOOK]
        st2["ledger"] = []  # giả lập mất ledger để test filled không nhân đôi
        _write(plan_path, plan2); _write(state_path, st2)
        inj.process_account("SELFCHK", plan_date, dry_run=False)
        plan3 = json.load(open(plan_path, encoding="utf-8"))
        disc3 = [o for o in plan3["orders"] if o.get("book") == BOOK]
        check("(b') filled tính từ broker (200), không cộng dồn ledger cũ → vẫn inject 200 not 400",
              disc3 and disc3[0]["qty"] == 200, str(disc3 and disc3[0].get("qty")))

        # (c) fail-safe broker: reset plan, broker positions fail → KHÔNG chèn
        _write(plan_path, {"plan_date": plan_date, "account": "SELFCHK", "orders": [copy.deepcopy(v24_order)]})
        _write(state_path, {**base_state(), "account": "SELFCHK"})
        FakeBroker.fail_positions = True
        inj.process_account("SELFCHK", plan_date, dry_run=False)
        planf = json.load(open(plan_path, encoding="utf-8"))
        check("(c) broker fail → KHÔNG chèn lệnh nào", len([o for o in planf["orders"] if o.get("book") == BOOK]) == 0)
        FakeBroker.fail_positions = False

        # (c) fail-safe quote: broker ok nhưng quote fail → KHÔNG chèn
        _write(plan_path, {"plan_date": plan_date, "account": "SELFCHK", "orders": [copy.deepcopy(v24_order)]})
        _write(state_path, {**base_state(), "account": "SELFCHK"})
        FakeBroker.total = 200; FakeBroker.fail_quote = True
        inj.process_account("SELFCHK", plan_date, dry_run=False)
        planq = json.load(open(plan_path, encoding="utf-8"))
        check("(c) quote fail → KHÔNG chèn lệnh nào", len([o for o in planq["orders"] if o.get("book") == BOOK]) == 0)
        FakeBroker.fail_quote = False

        # (e) đủ target qua injector → mark completed, không chèn
        _write(plan_path, {"plan_date": plan_date, "account": "SELFCHK", "orders": [copy.deepcopy(v24_order)]})
        _write(state_path, {**base_state(), "account": "SELFCHK"})
        FakeBroker.total = 400
        inj.process_account("SELFCHK", plan_date, dry_run=False)
        plane = json.load(open(plan_path, encoding="utf-8"))
        ste = json.load(open(state_path, encoding="utf-8"))
        check("(e) filled==target → KHÔNG chèn", len([o for o in plane["orders"] if o.get("book") == BOOK]) == 0)
        check("(e) state → completed", ste.get("status") == "completed", str(ste.get("status")))

        # opportunistic end-to-end: block turnover → boost (nhưng vẫn ≤ remaining)
        _write(plan_path, {"plan_date": plan_date, "account": "SELFCHK", "orders": []})
        s_opp = {**base_state(), "account": "SELFCHK", "adv_ref_vnd": 40_000_000, "target_qty": 100000}
        _write(state_path, s_opp)
        FakeBroker.total = 0; FakeBroker.price = 19900.0
        # benign: turnover = day_volume×price = 30000×19900 ≈ 597M < 2×40M? 597M >> 80M → thực ra là block.
        # điều chỉnh: benign muốn < 2×adv_ref(=80M) → day_volume nhỏ
        FakeBroker.day_volume = 2000.0  # 2000×19900 = 39.8M < 80M benign
        inj.process_account("SELFCHK", plan_date, dry_run=False)
        pb = json.load(open(plan_path, encoding="utf-8"))
        qb = [o for o in pb["orders"] if o.get("book") == BOOK][0]["qty"]
        _write(plan_path, {"plan_date": plan_date, "account": "SELFCHK", "orders": []})
        _write(state_path, s_opp)
        FakeBroker.day_volume = 6000.0  # 6000×19900 = 119.4M > 80M block
        inj.process_account("SELFCHK", plan_date, dry_run=False)
        pbo = json.load(open(plan_path, encoding="utf-8"))
        qbo = [o for o in pbo["orders"] if o.get("book") == BOOK][0]["qty"]
        check("(a) e2e: opportunistic phiên block chèn NHIỀU hơn phiên benign", qbo > qb, f"benign={qb} block={qbo}")

    finally:
        inj.os.path.join = _real_join


if __name__ == "__main__":
    test_engine()
    test_injector()
    print(f"\n=== SELFCHECK: {PASS} passed, {FAIL} failed ===")
    sys.exit(1 if FAIL else 0)
