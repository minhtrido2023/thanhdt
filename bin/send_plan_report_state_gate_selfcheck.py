#!/usr/bin/env python3
"""Selfcheck cho gate "plan sinh từ state cũ" trong bin/send_plan_report.sh (Wags 2026-08-11).

VÌ SAO CÓ FILE NÀY. Gate cũ so `plan['state_source']` với `golive['source']` bằng `!=`.
`state_source` là prose TỰ DO do bên sinh plan viết — thực tế đã thấy ít nhất 3 cách viết cho
CÙNG một nguồn ('DT5G_macro', 'DT5G_macro (…, published_at …)',
'deploy_golive_dt5g_v4/golive_state_today.json (… qua get_gated_state)'). Nên gate báo động giả,
CHẶN việc gửi plan → user không nhận plan để duyệt → sáng hôm sau bot từ chối chạy. Đã cắn thật
2026-08-07 và 2026-08-10/11 (30 lệnh lỡ phiên). Gate mới so `state` (int 0-4) — tín hiệu THẬT.

Chạy script THẬT trong sandbox (SEND_PLAN_WORKDIR_OVERRIDE + SEND_PLAN_MARKER_DIR + --dry-run)
nên KHÔNG gửi Discord/Telegram và KHÔNG ghi bus.

  python3 bin/send_plan_report_state_gate_selfcheck.py

Case 3 là case quan trọng nhất: gate MỚI chặt HƠN gate cũ, không phải lỏng hơn — lệch state thật
mà nhãn source trùng nhau thì bản cũ KHÔNG bao giờ bắt được.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SEND_PLAN_SCRIPT: trỏ sang một BẢN KHÁC của script để chạy đối chứng RED trên code cũ
# (kỷ luật: test phải FAIL trên cây hỏng trước khi tin nó PASS trên cây đã sửa). Bản đối chứng
# phải đặt trong chính bin/ để $ROOT bên trong script resolve y hệt bản thật.
SCRIPT = os.environ.get("SEND_PLAN_SCRIPT") or os.path.join(ROOT, "bin", "send_plan_report.sh")

# Prose `state_source` thật, chép nguyên văn từ plan trên đĩa.
SRC_BARE = "DT5G_macro"
SRC_ANNOTATED = "DT5G_macro (deploy_golive_dt5g_v4/golive_state_today.json, published_at 2026-08-10T19:01:15)"
SRC_PATHY = ("deploy_golive_dt5g_v4/golive_state_today.json "
             "(tav2_bq.vnindex_5state_dt5g_live qua get_gated_state)")

# Mỗi case là dict để thêm trường mới không phải sửa lại mọi dòng cũ.
#   want_block : gate state có ĐƯỢC PHÉP chặn việc gửi plan không
#   want_note  : chuỗi BẮT BUỘC có trong report render ra (None = không kiểm)
#   deny_note  : chuỗi KHÔNG được có trong report
# want_note tồn tại vì arch-review coord-2026-08-11: "fail-open được phép, fail-open CÂM thì
# không" — mọi nhánh bỏ qua gate phải để lại dấu vết ĐỌC ĐƯỢC trong chính report, nếu không
# một RED giả ồn ào bị đổi lấy một GREEN giả câm (lớp lỗi khó phát hiện hơn hẳn).
CASES = [
    dict(name="annotated-source cùng state  -> KHÔNG chặn (bug 08-10/11)",
         p_src=SRC_ANNOTATED, p_state=3, g_src=SRC_BARE, g_state=3, has_golive=True,
         want_block=False, want_note="✅ state=3 (NEUTRAL) khớp"),
    dict(name="pathy-source cùng state      -> KHÔNG chặn (bug 08-07)",
         p_src=SRC_PATHY, p_state=3, g_src=SRC_BARE, g_state=3, has_golive=True,
         want_block=False, want_note="✅ state=3 (NEUTRAL) khớp"),
    dict(name="LỆCH STATE, nhãn source TRÙNG -> PHẢI chặn (bản cũ mù ca này)",
         p_src=SRC_BARE, p_state=1, g_src=SRC_BARE, g_state=3, has_golive=True,
         want_block=True),
    dict(name="plan thiếu field state       -> KHÔNG chặn NHƯNG phải NÓI RA",
         p_src=SRC_PATHY, p_state=None, g_src=SRC_BARE, g_state=3, has_golive=True,
         want_block=False, want_note="⚠️ CHƯA đối chiếu được state plan"),
    dict(name="không có golive_state_today  -> KHÔNG chặn NHƯNG phải NÓI RA",
         p_src=SRC_ANNOTATED, p_state=1, g_src=None, g_state=None, has_golive=False,
         want_block=False, want_note="không có deploy_golive_dt5g_v4/golive_state_today.json"),
    dict(name="golive.state là prose        -> KHÔNG chặn NHƯNG phải NÓI RA",
         p_src=SRC_BARE, p_state=3, g_src=SRC_BARE, g_state="NEUTRAL", has_golive=True,
         want_block=False, want_note="⚠️ CHƯA đối chiếu được state plan"),
    dict(name="golive JSON HỎNG            -> KHÔNG chặn NHƯNG phải NÓI RA (except Exception)",
         p_src=SRC_BARE, p_state=3, g_src=SRC_BARE, g_state=3, has_golive="corrupt",
         want_block=False, want_note="⚠️ CHƯA đối chiếu được state plan"),
    dict(name="state=-1 (PROBE)             -> KHÔNG chặn (sentinel, không phải regime 1-5)",
         p_src=SRC_BARE, p_state=-1, g_src=SRC_BARE, g_state=3, has_golive=True,
         p_state_name="PROBE", want_block=False, want_note="PROBE, không phải regime 1-5"),
    dict(name="state=3 nhưng state_name='BULL' -> KHÔNG chặn, PHẢI cảnh báo mâu thuẫn",
         p_src=SRC_BARE, p_state=3, g_src=SRC_BARE, g_state=3, has_golive=True,
         p_state_name="BULL", want_block=False,
         want_note="hai field trong cùng plan mâu thuẫn"),
]

PLAN_DATE = "2026-08-11"
ACCOUNT = "SpaceX"


def run_case(name, p_src, p_state, g_src, g_state, has_golive, want_block,
             want_note=None, deny_note=None, p_state_name="NEUTRAL"):
    sandbox = tempfile.mkdtemp(prefix="sendplan_selfcheck_")
    try:
        plans = os.path.join(sandbox, "data", "trade_plans")
        os.makedirs(plans)
        plan = {
            "plan_date": PLAN_DATE,
            "account": ACCOUNT,
            "state_source": p_src,
            "state_name": p_state_name,
            "orders": [],
            "summary": {"action": "HOLD", "reasons": ["selfcheck fixture"]},
            "requires_user_approval": False,
        }
        if p_state is not None:
            plan["state"] = p_state
        with open(os.path.join(plans, f"plan_{ACCOUNT}_{PLAN_DATE}.json"), "w") as f:
            json.dump(plan, f)

        if has_golive:
            gdir = os.path.join(sandbox, "deploy_golive_dt5g_v4")
            os.makedirs(gdir)
            gpath = os.path.join(gdir, "golive_state_today.json")
            if has_golive == "corrupt":
                with open(gpath, "w") as f:
                    f.write('{"as_of": "2026-08-10", "state": 3,')   # JSON cụt
            else:
                golive = {"as_of": "2026-08-10", "source": g_src, "bq_publish_ok": True}
                if g_state is not None:
                    golive["state"] = g_state
                with open(gpath, "w") as f:
                    json.dump(golive, f)

        env = dict(os.environ)
        env["SEND_PLAN_WORKDIR_OVERRIDE"] = sandbox
        env["SEND_PLAN_MARKER_DIR"] = os.path.join(sandbox, "markers")
        proc = subprocess.run(
            ["bash", SCRIPT, "--account", ACCOUNT, "--dry-run"],
            capture_output=True, text=True, env=env, timeout=180,
        )
        out = proc.stdout + proc.stderr
        # Chỉ quan tâm gate state — không nhận nhầm escalate của gate khác là "đã chặn đúng".
        blocked = ("plan_state_mismatch" in out) or ("plan_state_source_mismatch" in out)
        ok = blocked == want_block
        why = "" if ok else f"mong đợi chặn={want_block}, thực tế chặn={blocked}"
        # Bỏ qua gate mà KHÔNG để lại dấu vết = fail-open câm ⇒ FAIL, dù hành vi chặn đúng.
        if ok and want_note and want_note not in out:
            ok, why = False, f"thiếu dấu vết trong report: không thấy {want_note!r}"
        if ok and deny_note and deny_note in out:
            ok, why = False, f"report không được chứa {deny_note!r}"
        return ok, blocked, why, out
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def main():
    if not os.path.exists(SCRIPT):
        print(f"FAIL: không thấy {SCRIPT}")
        return 1
    passed = 0
    for case in CASES:
        ok, blocked, why, out = run_case(**case)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {case['name']}")
        if ok:
            passed += 1
        else:
            print(f"        {why}")
            for line in out.strip().splitlines()[:8]:
                print(f"        | {line}")
    total = len(CASES)
    print(f"\n{passed}/{total} PASS")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
