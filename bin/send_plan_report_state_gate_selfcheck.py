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
# Ca KHỚP state: từ 163714bf (user 2026-09-29 "câu cố định lặp lại vô nghĩa") report CỐ Ý không
# in dòng "✅ state=… khớp" nữa — chỉ in khi có ⚠️. Dấu vết đúng cho ca khớp vì thế là VẮNG ⚠️;
# gate vẫn được chứng minh SỐNG bởi ca "LỆCH STATE … PHẢI chặn" trên cùng đường code.
_NO_STATE_WARN = "⚠️ CHƯA đối chiếu được state plan"
_G_PUB = "2026-08-10T19:01:15"          # published_at của golive fixture
_GATE_LINE_MARK = "Cổng DT5G SUY GIẢM"   # chuỗi nhận diện dòng nguồn cổng trong report
CASES = [
    dict(name="annotated-source cùng state  -> KHÔNG chặn (bug 08-10/11)",
         p_src=SRC_ANNOTATED, p_state=3, g_src=SRC_BARE, g_state=3, has_golive=True,
         want_block=False, deny_note=_NO_STATE_WARN),
    dict(name="pathy-source cùng state      -> KHÔNG chặn (bug 08-07)",
         p_src=SRC_PATHY, p_state=3, g_src=SRC_BARE, g_state=3, has_golive=True,
         want_block=False, deny_note=_NO_STATE_WARN),
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
    # ── Dòng NGUỒN CỔNG (retro 2026-10-11 Pattern I, bin/gate_source_check.py): bản publish plan
    # dựa vào ra nguồn khác DT5G_macro ⇒ đúng MỘT dòng ⚠️ trong report, KHÔNG chặn. Mọi ca ở trên
    # dùng g_src=DT5G_macro nên cũng phải KHÔNG có dòng này (kiểm chung trong run_case).
    dict(name="nguồn cổng DT4_only + bằng chứng đúng lượt -> KHÔNG chặn, dòng ⚠️ trích dòng cổng",
         p_src=SRC_BARE, p_state=3, g_src="DT4_only", g_state=3, has_golive=True, want_block=False,
         gate_marker=dict(source="DT4_only", published_at=_G_PUB,
                          gate_line="[get_gated_state] DT4_only: health report 2903min old (> 1440) -> DT4_only",
                          gate_line_why="", health="status=HEALTHY, ts=2026-10-10T18:37:02+07:00, recommended_state_source=DT5G_macro"),
         want_note="ra nguồn DT4_only, không phải DT5G_macro ⇒ state này KHÔNG áp macro cap (cổng fail-closed về DT4). "
                   "Plan KHÔNG bị chặn — anh cân nhắc khi duyệt. Bằng chứng lượt publish: dòng cổng tự in: "
                   "«[get_gated_state] DT4_only: health report 2903min old (> 1440) -> DT4_only» · "
                   "data/macro_health.json: status=HEALTHY, ts=2026-10-10T18:37:02+07:00",
         want_gate_lines=1),
    dict(name="nguồn cổng DT4_only, KHÔNG có marker    -> dòng ⚠️ nói thẳng không có bằng chứng",
         p_src=SRC_BARE, p_state=3, g_src="DT4_only", g_state=3, has_golive=True, want_block=False,
         want_note="Không có bằng chứng nguyên nhân của đúng lượt publish này", want_gate_lines=1),
    dict(name="nguồn cổng DT4_only, marker của lượt KHÁC -> KHÔNG trích bằng chứng cũ",
         p_src=SRC_BARE, p_state=3, g_src="DT4_only", g_state=3, has_golive=True, want_block=False,
         gate_marker=dict(source="DT4_only", published_at="2026-08-07T19:01:00",
                          gate_line="[get_gated_state] DT4_only: BẰNG CHỨNG CŨ", gate_line_why="", health="status=CU"),
         want_note="Không có bằng chứng nguyên nhân của đúng lượt publish này",
         deny_note="BẰNG CHỨNG CŨ", want_gate_lines=1),
    dict(name="golive THIẾU trường source              -> dòng ⚠️, không khẳng định về macro cap",
         p_src=SRC_BARE, p_state=3, g_src=None, g_state=3, has_golive=True, want_block=False,
         want_note="ra nguồn <thiếu trường source>, không phải DT5G_macro ⇒ KHÔNG xác nhận được state này có áp macro cap",
         deny_note="state này KHÔNG áp macro cap", want_gate_lines=1),
    dict(name="nguồn cổng DT4_STALE                    -> dòng ⚠️",
         p_src=SRC_BARE, p_state=3, g_src="DT4_STALE", g_state=3, has_golive=True, want_block=False,
         want_note="ra nguồn DT4_STALE, không phải DT5G_macro", want_gate_lines=1),
    dict(name="nguồn cổng DT5G_macro dù còn marker cũ   -> KHÔNG có dòng ⚠️ nguồn cổng",
         p_src=SRC_BARE, p_state=3, g_src=SRC_BARE, g_state=3, has_golive=True, want_block=False,
         gate_marker=dict(source="DT4_only", published_at=_G_PUB, gate_line="x", gate_line_why="", health="x")),
    # ── Nhánh LỖI của khối nguồn cổng (send_plan_report.sh, `except Exception as _e`): helper hỏng
    # ⇒ report VẪN render và có ĐÚNG MỘT dòng nói ra là không kiểm được. "lỗi ⇒ sys.exit(1)" làm
    # mất report; "lỗi ⇒ câm" làm mất dòng — cả hai mutation phải làm ca này đỏ.
    dict(name="helper nguồn cổng HỎNG                  -> report vẫn render, đúng 1 dòng 'KHÔNG kiểm được'",
         p_src=SRC_BARE, p_state=3, g_src="DT4_only", g_state=3, has_golive=True, want_block=False,
         broken_helper=True, want_note="🧭 Thị trường:", want_gate_err_lines=1),
]

PLAN_DATE = "2026-08-11"
ACCOUNT = "SpaceX"


def run_case(name, p_src, p_state, g_src, g_state, has_golive, want_block,
             want_note=None, deny_note=None, p_state_name="NEUTRAL",
             gate_marker=None, want_gate_lines=0, broken_helper=False, want_gate_err_lines=0):
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
                golive = {"as_of": "2026-08-10", "source": g_src, "bq_publish_ok": True,
                          "published_at": _G_PUB}
                if g_src is None:
                    del golive["source"]
                if g_state is not None:
                    golive["state"] = g_state
                with open(gpath, "w") as f:
                    json.dump(golive, f)

        if gate_marker is not None:
            os.makedirs(os.path.join(sandbox, "data"), exist_ok=True)
            with open(os.path.join(sandbox, "data", "gate_source_alert.json"), "w") as f:
                json.dump(gate_marker, f)

        if broken_helper:
            # Khối python của report chạy `python3 -` với cwd = WORKDIR ⇒ sys.path[0] là WORKDIR,
            # đứng TRƯỚC mike/bin: file này che helper thật và ném lỗi ngay lúc import.
            with open(os.path.join(sandbox, "gate_source_check.py"), "w") as f:
                f.write('raise RuntimeError("selfcheck: helper hỏng")\n')

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
        # Dòng nguồn cổng: đúng số lần mong đợi ở MỌI ca (0 khi nguồn là DT5G_macro / không đọc
        # được golive — ca sau đã có dòng "CHƯA đối chiếu được state plan", không in hai dòng).
        n_gate = out.count(_GATE_LINE_MARK)
        if ok and n_gate != want_gate_lines:
            ok, why = False, f"dòng nguồn cổng xuất hiện {n_gate} lần, mong đợi {want_gate_lines}"
        n_err = out.count("KHÔNG kiểm được nguồn cổng DT5G")
        if ok and n_err != want_gate_err_lines:
            ok, why = False, (f"dòng 'KHÔNG kiểm được nguồn cổng DT5G' xuất hiện {n_err} lần, mong đợi "
                              f"{want_gate_err_lines} (0 = helper phải import/chạy được; 1 = ca helper hỏng)")
        if ok and broken_helper and "RuntimeError: selfcheck: helper hỏng" not in out:
            ok, why = False, "dòng lỗi không trích lỗi thật của helper (§29)"
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
