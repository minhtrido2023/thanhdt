#!/usr/bin/env python3
"""signal_holds — tạm giữ tín hiệu/book/mã không cho MỞ LỆNH MỚI tới ngày `until`.

Nguồn dữ liệu: data/signal_holds.json (WC_ROOT). Fix triệt để lỗi #3 trong
research/plan_pipeline_3loi_rca_20260820.md: ranh giới "đừng mua tín hiệu X" trước đây chỉ nằm
ở kb/current_ops.md (file DollarBill KHÔNG import) và không có cơ chế code nào cưỡng chế.

Cưỡng chế 2 tầng (đúng mẫu P0/P1 funding gate):
  (a) prompt_note()  — bơm vào prompt DollarBill khi lập plan (tầng sinh plan)
  (b) check_plan()   — gate deterministic, loại order vi phạm (tầng chặn cứng), gọi trước
                       send_plan_report và trong bot_execute.py

Chỉ chặn MỞ MỚI/khớp lệnh theo `side`; KHÔNG đụng vị thế đang giữ. So bằng GIÁ TRỊ chuẩn hoá
(§28 coding_guidelines): ticker/book upper-case, ngày ISO so chuỗi.

CLI:
  signal_holds.py --note                 # in prompt note (rỗng nếu không có hold)
  signal_holds.py --check <plan.json>    # exit 0 nếu sạch, 2 nếu có vi phạm (in JSON)
  signal_holds.py --list [--asof DATE]   # liệt kê hold còn hiệu lực
"""
import argparse
import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")


def _wc_root():
    # file nằm ở mike/bin/ -> WC_ROOT là 2 cấp trên mike/
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, "..", ".."))


def _holds_path():
    return os.path.join(_wc_root(), "data", "signal_holds.json")


def _today_ict():
    return datetime.now(_ICT).strftime("%Y-%m-%d")


def load_holds():
    """Trả về list hold thô (chưa lọc ngày). File thiếu/hỏng -> [] (fail-open cho READER,
    KHÔNG fail-open cho GATE — gate tự quyết, xem check_plan)."""
    p = _holds_path()
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        return d.get("holds", []) if isinstance(d, dict) else (d or [])
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, OSError) as e:
        print(f"[signal_holds] WARN không đọc được {p}: {e}", file=sys.stderr)
        return []


def active_holds(asof=None):
    """Hold còn hiệu lực tại ngày `asof` (mặc định hôm nay ICT)."""
    asof = asof or _today_ict()
    out = []
    for h in load_holds():
        until = str(h.get("until") or "")
        if not until or asof <= until:
            out.append(h)
    return out


def _side_match(hold_side, order_side):
    hs = (hold_side or "both").lower()
    os_ = (order_side or "").lower()
    return hs == "both" or hs == os_


def match_order(ticker, side, book, asof=None, plan_date=None):
    """Trả về hold ĐẦU TIÊN chặn order này, hoặc None.

    Chặn khi: (scope==ticker & ticker khớp) HOẶC (scope==book & book khớp), VÀ side khớp,
    VÀ ngày plan (plan_date, fallback asof) <= until."""
    ref_date = plan_date or asof or _today_ict()
    tk = (ticker or "").upper()
    bk = (book or "").upper()
    for h in load_holds():
        until = str(h.get("until") or "")
        if until and ref_date > until:
            continue
        if not _side_match(h.get("side"), side):
            continue
        scope = (h.get("scope") or "").lower()
        val = (h.get("value") or "").upper()
        if scope == "ticker" and tk and tk == val:
            return h
        if scope == "book" and bk and bk == val:
            return h
    return None


def check_plan(plan_path):
    """Kiểm 1 plan JSON. Trả (violations, plan_date). violations = list dict order vi phạm."""
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    plan_date = plan.get("plan_date")
    violations = []
    for o in plan.get("orders", []):
        # chỉ chặn MỞ MỚI/khớp — mọi order trong orders[] đều là lệnh sắp đặt, nên check hết
        h = match_order(o.get("ticker"), o.get("side"),
                        o.get("book"), plan_date=plan_date)
        if h:
            violations.append({
                "order_id": o.get("id"),
                "ticker": o.get("ticker"),
                "side": o.get("side"),
                "book": o.get("book"),
                "qty": o.get("qty") or o.get("quantity"),
                "hold": {"scope": h.get("scope"), "value": h.get("value"),
                         "side": h.get("side"), "until": h.get("until"),
                         "reason": h.get("reason"), "decided_by": h.get("decided_by")},
            })
    return violations, plan_date


def enforce_plan(plan_path):
    """Loại MỌI order vi phạm hold khỏi orders[] → deferred_orders (atomic, tmp+replace).

    Fail-safe: chỉ GỠ lệnh (chiều an toàn), gắn deferred_reason dẫn hold. Idempotent — chạy
    lại trên plan đã sạch = no-op. TỪ CHỐI đụng plan đã duyệt (approved_by != None) để không
    âm thầm sửa thứ user đã ký; trả ('refused_approved', violations) trong trường hợp đó.

    Trả (action, violations): action ∈ {'clean','stripped','refused_approved'}."""
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    violations, plan_date = check_plan(plan_path)
    if not violations:
        return "clean", []
    if plan.get("approved_by") is not None:
        # plan đã ký — KHÔNG tự sửa; để tầng bot_execute chặn + escalate cho người.
        return "refused_approved", violations

    viol_ids = {v.get("order_id") for v in violations}
    kept, moved = [], []
    for o in plan.get("orders", []):
        if o.get("id") in viol_ids:
            v = next(x for x in violations if x.get("order_id") == o.get("id"))
            h = v["hold"]
            o["deferred_reason"] = (
                f"AUTO-DEFERRED by signal_holds gate: vi phạm hold [{h['scope']}={h['value']}, "
                f"side={h['side']}] tới {h['until']} — {h['reason']} (decided_by={h['decided_by']}).")
            moved.append(o)
        else:
            kept.append(o)
    plan["orders"] = kept
    plan.setdefault("deferred_orders", []).extend(moved)

    tmp = plan_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    os.replace(tmp, plan_path)
    return "stripped", violations


def prompt_note(asof=None):
    """Chuỗi bơm vào prompt DollarBill. Rỗng nếu không có hold còn hiệu lực."""
    holds = active_holds(asof)
    if not holds:
        return ""
    lines = [(" RANH GIỚI TẠM GIỮ TÍN HIỆU (signal_holds — BẮT BUỘC tuân thủ, đây là quyết "
              "định user/ranh giới rủi ro, KHÔNG phải gợi ý). TUYỆT ĐỐI KHÔNG tạo lệnh MỞ MỚI "
              "vi phạm các hold dưới đây — nếu tín hiệu fire, ghi mã vào deferred_orders với "
              "deferred_reason dẫn hold, KHÔNG đưa vào orders[]. (Gate deterministic sẽ loại "
              "order vi phạm dù bạn quên, nhưng đừng để tới đó.):")]
    for h in holds:
        scope = h.get("scope")
        val = h.get("value")
        side = h.get("side", "both")
        lines.append(
            f" • [{scope}={val}, side={side}] GIỮ tới {h.get('until')} — "
            f"{h.get('reason')} (decided_by={h.get('decided_by')}, {h.get('ref','')})")
    return "".join(lines)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--note", action="store_true")
    g.add_argument("--check", metavar="PLAN_JSON")
    g.add_argument("--enforce", metavar="PLAN_JSON")
    g.add_argument("--list", action="store_true")
    ap.add_argument("--asof")
    args = ap.parse_args()

    if args.note:
        sys.stdout.write(prompt_note(args.asof))
        return 0
    if args.list:
        print(json.dumps(active_holds(args.asof), ensure_ascii=False, indent=2))
        return 0
    if args.check:
        violations, plan_date = check_plan(args.check)
        if violations:
            print(json.dumps({"plan_date": plan_date, "violations": violations},
                             ensure_ascii=False, indent=2))
            return 2
        print(json.dumps({"plan_date": plan_date, "violations": []}, ensure_ascii=False))
        return 0
    if args.enforce:
        action, violations = enforce_plan(args.enforce)
        print(json.dumps({"action": action, "violations": violations}, ensure_ascii=False,
                         indent=2 if violations else None))
        # exit: 0 clean, 3 stripped (đã sửa, không phải lỗi), 2 refused_approved (cần người)
        return {"clean": 0, "stripped": 3, "refused_approved": 2}[action]
    return 1


if __name__ == "__main__":
    sys.exit(main())
