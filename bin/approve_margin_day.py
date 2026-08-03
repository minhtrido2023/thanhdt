#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ghi BẢN GHI DUYỆT RIÊNG cho MỘT ngày có dùng margin (sleeve CAPIT).

Chính sách (user chốt 2026-08-03): `capit_margin_lever.enabled=true` là công tắc TỔNG — điều
kiện CẦN nhưng KHÔNG ĐỦ. Mỗi NGÀY mà plan thật sự có lệnh được cấp đòn bẩy còn cần MỘT lần
user duyệt riêng cho ĐÚNG ngày đó, trước khi bot_execute.py (09:05) được phép đặt các lệnh ấy
bằng tiền vay.

VÌ SAO LÀ FILE RIÊNG, KHÔNG PHẢI FIELD TRONG PLAN: plan là JSON do LLM (DollarBill) sinh hoặc
người sửa tay. Đặt cờ duyệt đòn bẩy vào đó = trao quyền duyệt cho chính nơi sinh plan — đúng
cái mà `trading_bot.plan.apply_capit_lever` tồn tại để chặn (coding_guidelines §7). Script này
là đường DUY NHẤT ghi bản ghi duyệt, và nó chỉ được chạy khi user đã xác nhận thật.

AI CHẠY: Mike, sau khi user duyệt trong Discord plan channel (kb/current_ops.md — mọi lần duyệt
plan đều mirror về topic đó). KHÔNG agent nào tự duyệt hộ: mỗi lần chạy đều ghi bus event +
Discord, nên một lần tự duyệt là một dòng ai cũng thấy, không phải một thay đổi im lặng.

DÙNG:
    python3 mike/bin/approve_margin_day.py --account SpaceX --date 2026-08-04 \
        --approved-by "user (John) — Discord plan channel 21:37, xác nhận vay 75tr"
    # xem trước, không ghi gì:
    python3 mike/bin/approve_margin_day.py --account SpaceX --date 2026-08-04 --dry-run
    # thu hồi (user đổi ý trước 09:05):
    python3 mike/bin/approve_margin_day.py --account SpaceX --date 2026-08-04 --revoke \
        --approved-by "user (John) rút duyệt 08:10"

Rổ mã + trần VND KHÔNG gõ tay: script tự lấy từ `trading_bot.plan.preview_margin_day()` —
CÙNG hàm mà báo cáo duyệt plan 21:00 dùng để hiển thị, nên số user nhìn thấy đúng bằng số bị
ràng buộc lúc thực thi. `--max-total-vnd` chỉ để user duyệt một mức THẤP HƠN preview.
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MIKE_ROOT = os.path.join(WC_ROOT, "mike")
sys.path.insert(0, WC_ROOT)

APPROVAL_DIR = os.path.join(WC_ROOT, "data", "margin_approvals")
ICT = ZoneInfo("Asia/Ho_Chi_Minh")          # §16: neo múi giờ tường minh, không tin TZ của host

# MỘT nguồn duy nhất cho danh sách "không phải người duyệt thật": hàm ĐỌC bản duyệt
# (trading_bot.plan.margin_day_approval) và script GHI phải từ chối đúng cùng một tập chuỗi —
# hai bản sao là cách chắc chắn để một chuỗi qua được bên này mà bị bên kia chặn (hoặc ngược lại).
from trading_bot.plan import APPROVAL_PLACEHOLDERS as PLACEHOLDER  # noqa: E402


def approval_path(account, date):
    return os.path.join(APPROVAL_DIR, f"margin_approval_{account}_{date}.json")


def _bus(kind, topic, payload):
    """Ghi bus — bản ghi duyệt tiền vay phải để lại dấu vết ai cũng thấy. → True nếu ghi được.

    KIỂM returncode, không chỉ bắt exception (arch-reviewer vòng 3 #5): docstring của script
    này tuyên bố "không agent nào tự duyệt hộ được, vì mỗi lần chạy đều để lại một dòng ai
    cũng thấy". Nếu `append_event.sh` trả rc≠0 (bus hỏng) mà ta nuốt im lặng thì lá chắn ấy
    biến mất đúng lúc nó cần nhất, và không ai biết. Bản ghi duyệt vẫn hợp lệ — nhưng NGƯỜI
    CHẠY phải biết dấu vết đã mất, nên caller đổi exit code.
    """
    try:
        r = subprocess.run([os.path.join(MIKE_ROOT, "bin", "append_event.sh"), "Mike", kind,
                            topic, json.dumps(payload, ensure_ascii=False)],
                           check=False, capture_output=True, timeout=60)
        if r.returncode != 0:
            print(f"⚠ append_event.sh trả rc={r.returncode}: "
                  f"{(r.stderr or b'').decode('utf-8', 'replace').strip()[:300]}")
            return False
        return True
    except Exception as ex:
        print(f"⚠ không ghi được bus event ({type(ex).__name__}: {ex})")
        return False


def _notify(msg):
    """Đẩy Discord → True nếu gửi được (xem lý do kiểm rc ở `_bus`)."""
    try:
        r = subprocess.run([os.path.join(MIKE_ROOT, "bin", "notify_thread.sh"), msg,
                            "plan_approval"], check=False, capture_output=True, timeout=60)
        if r.returncode != 0:
            print(f"⚠ notify_thread.sh trả rc={r.returncode}: "
                  f"{(r.stderr or b'').decode('utf-8', 'replace').strip()[:300]}")
            return False
        return True
    except Exception as ex:
        print(f"⚠ không đẩy được Discord ({type(ex).__name__}: {ex})")
        return False


def _trace_exit(ok_bus, ok_notify, rc_ok=0):
    """Exit code phản ánh việc DẤU VẾT có để lại được không (bản ghi duyệt đã ghi xong)."""
    if ok_bus and ok_notify:
        return rc_ok
    print("\n" + "=" * 78)
    print("⚠️  CẢNH BÁO: BẢN GHI DUYỆT ĐÃ GHI, NHƯNG DẤU VẾT KHÔNG ĐỂ LẠI ĐƯỢC ĐẦY ĐỦ")
    print(f"   bus={'OK' if ok_bus else 'HỎNG'} · Discord={'OK' if ok_notify else 'HỎNG'}")
    print("   Lá chắn duy nhất chống 'tự duyệt hộ' là việc mỗi lần duyệt đều hiện ra cho")
    print("   người khác thấy. Báo lại kênh duyệt plan BẰNG TAY, hoặc --revoke rồi chạy lại.")
    print("=" * 78)
    return 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--date", required=True, help="plan_date (ngày THỰC THI, YYYY-MM-DD)")
    ap.add_argument("--approved-by", default="",
                    help="ai duyệt + căn cứ (bắt buộc, trừ --dry-run)")
    ap.add_argument("--max-total-vnd", type=float, default=None,
                    help="trần Σ giá trị lệnh được vay; mặc định = đúng số preview")
    ap.add_argument("--decided-by", choices=["user", "agent"], default="agent",
                    help="ai THẬT SỰ quyết (coding_guidelines §20) — 'user' CHỈ khi user xác "
                         "nhận trực tiếp lúc chạy; mặc định 'agent'")
    ap.add_argument("--revoke", action="store_true", help="thu hồi bản duyệt đã ghi")
    ap.add_argument("--revoked-reason", default="")
    ap.add_argument("--dry-run", action="store_true", help="chỉ in preview, KHÔNG ghi file")
    args = ap.parse_args()

    from trading_bot.plan import (preview_margin_day, CAPIT_LEVER_APPROVED_F,
                                  CAPIT_LEVER_APPROVED_PACKAGE, CAPIT_LEVER_APPROVED_ACCOUNTS)

    path = approval_path(args.account, args.date)

    if args.revoke:
        if not os.path.exists(path):
            print(f"⚠ không có bản duyệt nào để thu hồi: {path}")
            return 1
        with open(path, encoding="utf-8") as f:
            rec = json.load(f)
        rec["revoked"] = True
        rec["revoked_reason"] = args.revoked_reason or args.approved_by or "không ghi lý do"
        rec["revoked_at"] = dt.datetime.now(ICT).isoformat(timespec="seconds")
        if args.dry_run:
            print(f"[dry-run] sẽ thu hồi: {path}\n{json.dumps(rec, ensure_ascii=False, indent=2)}")
            return 0
        tmp = path + ".tmp"                  # ghi nguyên tử như đường TẠO bên dưới (§5) —
        with open(tmp, "w", encoding="utf-8") as f:   # kill giữa chừng KHÔNG được để lại JSON
            json.dump(rec, f, ensure_ascii=False, indent=2)   # cụt trong bản ghi ủy quyền vay
        os.replace(tmp, path)
        msg = (f"🚫 THU HỒI duyệt đòn bẩy margin — {args.account} ngày {args.date} "
               f"(lý do: {rec['revoked_reason']}). Phiên đó sẽ chạy bằng VỐN TỰ CÓ.")
        print(msg)
        ok_b = _bus("decision", f"margin-day-approval-revoked-{args.account}-{args.date}", rec)
        ok_n = _notify(msg)
        return _trace_exit(ok_b, ok_n)

    if args.account not in CAPIT_LEVER_APPROVED_ACCOUNTS:
        print(f"❌ account {args.account!r} KHÔNG nằm trong phạm vi user duyệt "
              f"{CAPIT_LEVER_APPROVED_ACCOUNTS} — nới phạm vi phải sửa CODE "
              f"(trading_bot/plan.py) + review, không duyệt lẻ ở đây.", file=sys.stderr)
        return 2

    pv = preview_margin_day(args.account, args.date)
    print(f"== Preview đòn bẩy CAPIT — {args.account} · plan_date {args.date} ==")
    if pv["error"]:
        print(f"❌ {pv['error']}")
        return 2
    if not pv["orders"]:
        print("Không có lệnh nào ĐỦ ĐIỀU KIỆN đòn bẩy trong plan này ⇒ KHÔNG cần duyệt riêng.")
        for r in pv["reasons"][:5]:
            print(f"  · {r}")
        print("Không ghi bản duyệt (duyệt khống là thứ duy nhất bản ghi này không được phép).")
        return 1
    for o in pv["orders"]:
        print(f"  · {o['ticker']:6s} {o['order_id']:14s} {o['value_vnd']:>16,.0f} VND")
    print(f"  Σ giá trị lệnh được cấp đòn bẩy : {pv['total_vnd']:>16,.0f} VND "
          f"({len(pv['orders'])} lệnh, f={pv['lever_f']}, gói {pv['loan_package_id']})")
    print(f"  → phần VAY thật (Σ × (1 − 1/f))  : {pv['borrow_vnd']:>16,.0f} VND")
    print("  (Σ là CẬN TRÊN: chưa trừ trần %ADV áp lúc thực thi — lệnh thật chỉ nhỏ hơn)")

    cap = pv["total_vnd"] if args.max_total_vnd is None else float(args.max_total_vnd)
    if args.max_total_vnd is not None and cap > pv["total_vnd"]:
        print(f"❌ --max-total-vnd {cap:,.0f} LỚN HƠN Σ preview {pv['total_vnd']:,.0f} — trần "
              f"duyệt chỉ được bằng hoặc thấp hơn số vừa hiển thị cho user.", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"\n[dry-run] KHÔNG ghi gì. Lệnh thật sẽ ghi: {path}")
        return 0

    who = (args.approved_by or "").strip()
    if who.lower() in PLACEHOLDER:
        print(f"❌ --approved-by {args.approved_by!r} không phải một người duyệt thật. Ghi rõ "
              f"AI duyệt + căn cứ (vd \"user (John) — Discord plan channel 21:37\"). Đây là "
              f"bản ghi ủy quyền vay tiền, không phải một cờ kỹ thuật.", file=sys.stderr)
        return 2

    rec = {
        "account": args.account,
        "plan_date": args.date,
        "approved_by": who,
        "approved_at": dt.datetime.now(ICT).isoformat(timespec="seconds"),
        "lever_f": CAPIT_LEVER_APPROVED_F,
        "loan_package_id": CAPIT_LEVER_APPROVED_PACKAGE,
        "max_lever_total_vnd": round(cap),
        "tickers": pv["tickers"],
        "preview_total_vnd": round(pv["total_vnd"]),
        "preview_borrow_vnd": round(pv["borrow_vnd"]),
        "orders_at_approval": pv["orders"],
        "written_by": "mike/bin/approve_margin_day.py",
        "note": ("Duyệt CHỈ cho plan_date này. Rổ mã đổi hoặc Σ vượt trần ⇒ "
                 "trading_bot.plan._enforce_margin_day_approval GỠ đòn bẩy (lệnh vẫn chạy "
                 "bằng vốn tự có), phải duyệt lại."),
    }
    os.makedirs(APPROVAL_DIR, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)                    # ghi nguyên tử (coding_guidelines §5)
    print(f"\n✅ ĐÃ GHI bản duyệt: {path}")

    msg = (f"✅ **DUYỆT ĐÒN BẨY MARGIN** — {args.account} · phiên {args.date}\n"
           f"• {len(pv['orders'])} lệnh CAPIT: {', '.join(pv['tickers'])}\n"
           f"• Σ giá trị được vay ≤ **{cap/1e6:,.1f}tr** (phần vay thật "
           f"~{pv['borrow_vnd']/1e6:,.1f}tr, f={CAPIT_LEVER_APPROVED_F}, gói "
           f"{CAPIT_LEVER_APPROVED_PACKAGE})\n"
           f"• Người duyệt: {who}\n"
           f"_Duyệt chỉ có hiệu lực cho phiên {args.date}. Rổ đổi/Σ vượt trần ⇒ bot tự GỠ đòn "
           f"bẩy và chạy bằng vốn tự có._")
    # `decided_by` KHÔNG hard-code "user" (coding_guidelines §20: chỉ ghi "user" khi user xác
    # nhận THẬT trong thời điểm đó). Script này chạy được bởi cả người lẫn agent, nên nó phải
    # KHAI, không được TỰ NHẬN. Mặc định "agent" = giả định thận trọng.
    ok_b = _bus("decision", f"margin-day-approval-{args.account}-{args.date}",
                {**rec, "decided_by": args.decided_by})
    ok_n = _notify(msg)
    return _trace_exit(ok_b, ok_n)


if __name__ == "__main__":
    sys.exit(main())
