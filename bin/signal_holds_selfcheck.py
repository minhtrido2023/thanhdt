#!/usr/bin/env python3
"""Selfcheck cho signal_holds (fix lỗi #3 RCA 2026-08-20).

Bất biến (assert lên QUAN HỆ, không lên trạng thái sống — §23): khớp theo ticker & book,
lọc theo side, hết hạn theo until, enforce strip idempotent + fail-safe cho plan đã duyệt,
fail-open khi file thiếu. Dùng fixture đóng băng, KHÔNG đọc data/signal_holds.json thật.
"""
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "signal_holds.py")


def _load(holds_file):
    """Nạp module với _holds_path() trỏ tới fixture."""
    spec = importlib.util.spec_from_file_location("signal_holds_sc", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m._holds_path = lambda: holds_file
    return m


def _write(d):
    fd, p = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f)
    return p


FIX = {"holds": [
    {"scope": "book", "value": "BAL", "side": "buy", "until": "2026-09-16",
     "reason": "r", "decided_by": "user"},
    {"scope": "ticker", "value": "XYZ", "side": "both", "until": "2026-09-16",
     "reason": "r2", "decided_by": "user"},
]}

n = 0


def ok(cond, msg):
    global n
    n += 1
    if not cond:
        print(f"FAIL: {msg}")
        sys.exit(1)
    print(f"  ok: {msg}")


def main():
    hf = _write(FIX)
    m = _load(hf)

    # 1. book match, side buy
    ok(m.match_order("VPI", "buy", "BAL", plan_date="2026-08-21"), "BAL buy khớp hold book")
    # 2. book match nhưng side sell -> không khớp (hold side=buy)
    ok(m.match_order("VPI", "sell", "BAL", plan_date="2026-08-21") is None,
       "BAL sell KHÔNG khớp (hold buy-only)")
    # 3. ticker match side both -> cả buy lẫn sell
    ok(m.match_order("XYZ", "buy", "LAG", plan_date="2026-08-21"), "XYZ buy khớp ticker hold")
    ok(m.match_order("XYZ", "sell", "LAG", plan_date="2026-08-21"), "XYZ sell khớp (side both)")
    # 4. mã/book không dính hold
    ok(m.match_order("FPT", "buy", "LAG", plan_date="2026-08-21") is None, "FPT/LAG không khớp")
    # 5. hết hạn: plan_date > until
    ok(m.match_order("VPI", "buy", "BAL", plan_date="2026-09-17") is None, "quá until -> hết hiệu lực")
    # 6. case-insensitive
    ok(m.match_order("vpi", "BUY", "bal", plan_date="2026-08-21"), "khớp không phân biệt hoa/thường")

    # 7. check_plan bắt vi phạm
    plan = {"plan_date": "2026-08-21", "approved_by": None, "orders": [
        {"id": "o1", "ticker": "VPI", "side": "buy", "book": "BAL", "qty": 400},
        {"id": "o2", "ticker": "FPT", "side": "buy", "book": "LAG", "qty": 100}]}
    pf = _write(plan)
    viol, pd = m.check_plan(pf)
    ok(len(viol) == 1 and viol[0]["ticker"] == "VPI", "check_plan bắt đúng 1 vi phạm (VPI)")

    # 8. enforce strip -> orders sạch, deferred có VPI, exit action 'stripped'
    action, viol = m.enforce_plan(pf)
    ok(action == "stripped", "enforce action=stripped")
    d = json.load(open(pf))
    ok(len(d["orders"]) == 1 and d["orders"][0]["ticker"] == "FPT", "orders còn FPT")
    ok(len(d["deferred_orders"]) == 1 and d["deferred_orders"][0]["ticker"] == "VPI",
       "VPI vào deferred_orders")
    ok("deferred_reason" in d["deferred_orders"][0], "có deferred_reason")
    # 9. idempotent: enforce lần 2 -> clean
    action2, _ = m.enforce_plan(pf)
    ok(action2 == "clean", "enforce lần 2 idempotent (clean)")

    # 10. plan ĐÃ DUYỆT có vi phạm -> refused_approved, KHÔNG sửa file
    plan_appr = {"plan_date": "2026-08-21", "approved_by": "user", "orders": [
        {"id": "o1", "ticker": "VPI", "side": "buy", "book": "BAL", "qty": 400}]}
    pfa = _write(plan_appr)
    action3, viol3 = m.enforce_plan(pfa)
    ok(action3 == "refused_approved", "plan đã duyệt -> refused_approved")
    da = json.load(open(pfa))
    ok(len(da["orders"]) == 1, "plan đã duyệt KHÔNG bị sửa (fail-safe)")

    # 10b. KILLER OBJECTION arch-reviewer 2026-08-20: ≥2 order THIẾU id, 1 vi phạm —
    # KHÔNG được gỡ oan order hợp lệ (trước đây khoá theo id=None trùng nhau -> gỡ sạch).
    plan_noid = {"plan_date": "2026-08-21", "approved_by": None, "orders": [
        {"ticker": "VPI", "side": "buy", "book": "BAL", "qty": 400},   # vi phạm, KHÔNG id
        {"ticker": "FPT", "side": "buy", "book": "LAG", "qty": 100}]}  # hợp lệ, KHÔNG id
    pfn = _write(plan_noid)
    act_n, _ = m.enforce_plan(pfn)
    dn = json.load(open(pfn))
    ok(act_n == "stripped", "thiếu id: action=stripped")
    ok([o["ticker"] for o in dn["orders"]] == ["FPT"],
       "thiếu id: CHỈ VPI bị gỡ, FPT hợp lệ GIỮ LẠI (không gỡ oan)")
    ok(len(dn["deferred_orders"]) == 1 and dn["deferred_orders"][0]["ticker"] == "VPI",
       "thiếu id: chỉ VPI vào deferred")
    os.unlink(pfn)

    # 10c. VPI-buy gắn book RỖNG/khác BAL -> vẫn bị chặn nhờ hold ticker=VPI (defense-in-depth).
    # Fixture cần cả hold ticker=VPI (khác FIX ở trên) -> nạp fixture riêng.
    fix2 = {"holds": [{"scope": "ticker", "value": "VPI", "side": "buy",
                       "until": "2026-09-16", "reason": "r", "decided_by": "user"}]}
    hf2 = _write(fix2)
    m2 = _load(hf2)
    ok(m2.match_order("VPI", "buy", "", plan_date="2026-08-21"),
       "VPI-buy book RỖNG bị chặn bởi hold ticker=VPI")
    ok(m2.match_order("VPI", "buy", "DISCRETIONARY", plan_date="2026-08-21"),
       "VPI-buy book khác BAL bị chặn bởi hold ticker=VPI")
    os.unlink(hf2)

    # 11. fail-open: file hold thiếu -> match None, không raise
    m.MOD_MISSING = _load("/nonexistent/holds.json")
    ok(m.MOD_MISSING.match_order("VPI", "buy", "BAL", plan_date="2026-08-21") is None,
       "file thiếu -> load_holds() rỗng -> không khớp (không raise)")

    # 12. prompt_note không rỗng khi có hold còn hạn, rỗng khi hết
    ok(m.prompt_note(asof="2026-08-21").strip() != "", "prompt_note có nội dung trong hạn")
    ok(m.prompt_note(asof="2026-12-31").strip() == "", "prompt_note rỗng khi mọi hold hết hạn")

    for p in (hf, pf, pfa):
        try:
            os.unlink(p)
        except OSError:
            pass
    print(f"\nsignal_holds_selfcheck: {n}/{n} PASS")


if __name__ == "__main__":
    main()
