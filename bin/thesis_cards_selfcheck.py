#!/usr/bin/env python3
"""Selfcheck B3: sổ thẻ thật + mutation tests + sổ lô (mã đang giữ). Chạy: env -u TZ ... ; TZ=Pacific/Kiritimati ..."""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thesis_cards as T  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        fails.append(name)


doc = T.read_json(T.CARDS)
led = T.read_json(T.LEDGER)["entries"]

# 1) sổ thật hợp lệ (chưa xét held)
e0 = T.validate(doc, led, None)
check("real ledger valid (schema/invariants/dd_ref)", not e0, "; ".join(e0[:3]))

# 2) mã đang giữ thật phải có thẻ active
held, src, herr = T.held_discretionary()
print("held source:", src, "| errors:", herr)
print("held:", held)
check("held non-empty (không im lặng rỗng)", bool(held))
e1 = T.validate(doc, led, held)
check("every held DISCRETIONARY_SPECIAL ticker has active card", not e1, "; ".join(e1[:3]))
# 22/11 23:28 user duyệt thẻ nháp (6) ⇒ rev2 active, KHÔNG còn cờ draft, có approved_by; NNC/VGS = value_long/user_decides
check("FPT,NNC,VGS đều có thẻ active đã duyệt (không draft, có approved_by)", all(
    T.latest_cards(doc).get(t, {}).get("status") == "active"
    and not T.latest_cards(doc)[t].get("draft_pending_user_review")
    and "decided_by: user" in str(T.latest_cards(doc)[t].get("approved_by"))
    for t in ("FPT", "NNC", "VGS")))
check("NNC,VGS rev mới = value_long/user_decides", all(
    T.latest_cards(doc)[t]["deal_type"] == "value_long" and T.latest_cards(doc)[t]["exit_policy"]["kind"] == "user_decides"
    for t in ("NNC", "VGS")))


def mut(name, fn, expect, held_=None):
    d = copy.deepcopy(doc)
    fn(d)
    errs = T.validate(d, led, held_)
    check(f"mutation: {name}", any(expect in x for x in errs), "; ".join(errs[:2]) or "không bắt được")


def c0(d, t="FPT"):
    # thẻ rev CAO NHẤT của mã (bản thắng) — mutation phải đánh vào bản đang hiệu lực
    return max((c for c in d["cards"] if c["ticker"] == t), key=lambda c: c["rev"])


mut("deal_type lạ", lambda d: c0(d).__setitem__("deal_type", "yolo"), "deal_type")
mut("value_long mà exit_policy.kind=stop", lambda d: c0(d)["exit_policy"].__setitem__("kind", "stop"), "user_decides")
mut("thiếu approval_ref", lambda d: c0(d)["exit_policy"].pop("approval_ref"), "approval_ref")
mut("milestone date không ISO", lambda d: c0(d)["milestones"][0].__setitem__("date", "27/11/2026"), "date không ISO")
mut("milestone thiếu source", lambda d: c0(d)["milestones"][0].pop("source"), "thiếu source")
mut("milestone id trùng", lambda d: c0(d)["milestones"][1].__setitem__("id", c0(d)["milestones"][0]["id"]), "id thiếu/trùng")
mut("đã chấm thiếu checked_at", lambda d: c0(d)["milestones"][0].update(status="checked_ok"), "checked_at")
mut("abandon thiếu how_measured", lambda d: c0(d)["abandon_triggers"][0].pop("how_measured"), "how_measured")
mut("dd_ref center lệch sổ giá", lambda d: c0(d)["dd_ref"].__setitem__("center", 1), "dd_ref.center")
mut("dd_ref rev lệch sổ giá", lambda d: c0(d)["dd_ref"].__setitem__("rev", 1), "dd_ref.rev")
mut("thesis >3 dòng", lambda d: c0(d).__setitem__("thesis", ["a", "b", "c", "d"]), "thesis")
mut("drawdown pct≠15", lambda d: c0(d)["drawdown_review"].__setitem__("pct", 10), "drawdown_review")
mut("rev nhảy cóc (append-only)", lambda d: c0(d).__setitem__("rev", 9), "rev không liên tục")
mut("mã đang giữ không có thẻ", lambda d: d.__setitem__("cards", [c for c in d["cards"] if c["ticker"] != "VGS"]), "KHÔNG có thẻ active", held)
mut("thẻ closed ⇒ không tính active", lambda d: c0(d, "NNC").__setitem__("status", "closed"), "KHÔNG có thẻ active", held)
# dd_ref lệch nhưng có stale_reason ⇒ qua
d2 = copy.deepcopy(doc)
c0(d2)["dd_ref"]["center"] = 1
c0(d2)["dd_ref"]["stale_reason"] = "test"
check("dd_ref lệch + stale_reason ⇒ qua", not any("dd_ref.center" in x for x in T.validate(d2, led, None)))
# append rev2 hợp lệ ⇒ latest = rev2
d3 = copy.deepcopy(doc)
n = copy.deepcopy(c0(d3))
n["rev"] = c0(d3)["rev"] + 1
d3["cards"].append(n)
check("append rev kế tiếp ⇒ hợp lệ & thắng", not T.validate(d3, led, None) and T.latest_cards(d3)["FPT"]["rev"] == n["rev"])
# sổ lô lỗi ⇒ fallback degraded có nêu lý do thật
def boom(a, b):
    raise RuntimeError("broker down")
h2, s2, er2 = T.held_discretionary(lot_fn=boom)
check("sổ lô lỗi ⇒ degraded + lý do thật", s2.startswith("degraded") and any("broker down" in x for x in er2), s2)
# fallback degraded KHÔNG phụ thuộc exit-rules (file có thể rỗng từ 22/11): trỏ EXIT_RULES vào file positions=[]
import json as _json, tempfile as _tf
with _tf.NamedTemporaryFile("w", suffix=".json", delete=False) as _f:
    _json.dump({"positions": []}, _f)
_old = T.EXIT_RULES
T.EXIT_RULES = _f.name
try:
    h3, s3, er3 = T.held_discretionary(lot_fn=boom)
finally:
    T.EXIT_RULES = _old
    os.unlink(_f.name)
check("degraded + exit-rules RỖNG ⇒ held vẫn có FPT/NNC/VGS (nguồn tên = thẻ)", all(t in h3 for t in ("FPT", "NNC", "VGS")), f"{sorted(h3)} | {s3}")
print(f"\n{'ALL PASS' if not fails else 'FAILED: ' + str(fails)}  (TZ={os.environ.get('TZ')!r})")
sys.exit(1 if fails else 0)
