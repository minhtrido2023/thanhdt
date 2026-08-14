#!/usr/bin/env python3
"""Selfcheck cho bin/dispatch_question_hint.py (nhắc đóng vòng bus sau dispatch).

Cái nhắc này có HAI cách hỏng, ngược chiều nhau, và cả hai đều IM LẶNG:
  · Bỏ sót — đúng ca root-cause-A mà nó sinh ra để chặn thì không kêu. Không ai biết, vì
    "không in gì" là trạng thái bình thường của nó.
  · Nhiễu — kêu ở mọi dispatch ⇒ bị phớt lờ ⇒ tệ hơn không có (tạo cảm giác đã có cơ chế).
Nên selfcheck phải pin CẢ HAI phía, đặc biệt là phía ÂM (prompt không liên quan ⇒ im).

Chạy trên bus GIẢ qua BUS_AUDIT_ROOT (bus_question_audit.py hỗ trợ sẵn từ 2026-08-14) —
không đụng bus thật, không phụ thuộc backlog hôm nay.

  python3 bin/dispatch_question_hint_selfcheck.py
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HINT = ROOT / "bin" / "dispatch_question_hint.py"

fails, oks = [], []


def check(name, cond, detail=""):
    (oks if cond else fails).append(name)
    print(("  ✅ " if cond else "  ❌ ") + name + (f" — {detail}" if detail else ""))


def ago(days):
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)) \
        .strftime("%Y-%m-%dT%H:%M:%SZ")


# Bảng câu hỏi treo dùng chung: lấy hình dạng THẬT trên bus 2026-08-14 (4 lớp khác nhau —
# wags-fix, arch-review, selfcheck-red, câu hỏi nghiệp vụ chữ dài).
BOARD = [
    ("Wags", "wags-fix-not-confirmed: coord-2026-08-12", 3),
    ("Wags", "wags-arch-review-inconclusive: coord-2026-08-13", 2),
    ("Wags", "selfcheck-red: plan_cash_commitment_selfcheck.py", 3),
    ("Taylor", "can-user-quyet-mo-cong-CASH_VENDOR-va-kiem-freshness", 1),
    ("Mike", "paper-checkpoint-overdue-fill_timing", 2),
]


def run_hint(prompt, board=None):
    """Chạy hint thật trên một cây bus giả; trả stdout."""
    td = tempfile.mkdtemp(prefix="qhint_")
    try:
        inbox = Path(td) / "bus" / "inbox"
        inbox.mkdir(parents=True)
        by_agent = {}
        for agent, topic, age in (BOARD if board is None else board):
            by_agent.setdefault(agent, []).append(
                {"agent": agent, "event_type": "question", "topic": topic, "ts": ago(age),
                 "payload": {}})
        for agent, evs in by_agent.items():
            (inbox / f"{agent}.jsonl").write_text(
                "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in evs), encoding="utf-8")
        env = dict(os.environ, BUS_AUDIT_ROOT=td)
        r = subprocess.run([sys.executable, str(HINT), "--to", "Taylor"], input=prompt,
                           capture_output=True, text=True, env=env, timeout=60)
        return r.stdout, r.returncode
    finally:
        shutil.rmtree(td, ignore_errors=True)


# ── Phía DƯƠNG: đúng ca nó sinh ra để chặn thì phải kêu ──────────────────────────────────
def case_positive_matches():
    out, _ = run_hint("User đã quyết phương án B cho "
                      "can-user-quyet-mo-cong-CASH_VENDOR-va-kiem-freshness. Triển khai ngay.")
    check("CHẮC: prompt chứa nguyên văn topic ⇒ khớp mức CHẮC",
          "[CHẮC]" in out and "CASH_VENDOR" in out, out[:160])
    check("CHẮC: in kèm lệnh append_event.sh sẵn để copy (nhắc CƠ HỌC, không phải lời khuyên)",
          "append_event.sh Mike decision" in out, out[:200])

    # Ca root-cause-A kinh điển: Mike nghe user quyết qua Discord rồi dispatch thẳng, prompt
    # chỉ nhắc nhãn ngày ĐẦY ĐỦ. Đây là lớp tái diễn nhiều nhất (coord-*).
    out, _ = run_hint("Vòng fix coord-2026-08-12 user đã xem và đồng ý bỏ qua, làm tiếp bước sau.")
    check("ngày ĐẦY ĐỦ tự nó đủ điểm khớp (lớp coord-* chỉ có DUY NHẤT token ngày)",
          "wags-fix-not-confirmed: coord-2026-08-12" in out, out[:200])

    # Dạng viết tắt người hay gõ: "coord-08-13" + tên lớp.
    out, _ = run_hint("Cái arch-review inconclusive của coord-08-13 thì user bảo thôi, khỏi làm.")
    check("viết tắt MM-DD + tên lớp ⇒ đủ điểm khớp",
          "wags-arch-review-inconclusive: coord-2026-08-13" in out, out[:200])


# ── Phía ÂM: im lặng khi không liên quan. Đây mới là vế giữ cho cái nhắc còn được đọc ────
def case_negative_stays_silent():
    out, rc = run_hint("Chạy backtest chiến lược V2.4 trên universe ticker_prune từ 2015, "
                       "xuất CSV kết quả và biểu đồ NAV.")
    check("ÂM: prompt nghiệp vụ không liên quan ⇒ im lặng tuyệt đối", out.strip() == "", out[:200])

    out, _ = run_hint("Giao Taylor rà lại số liệu, Winston kiểm tra corp-action, "
                      "Spyros soát rủi ro. Job này chạy nền, check jobs.sh sau.")
    check("ÂM: prompt đầy TÊN AGENT + từ điều phối ⇒ vẫn im (tên agent là stopword)",
          out.strip() == "", out[:200])

    out, _ = run_hint("Cập nhật plan và kiểm tra cash còn lại của tài khoản SpaceX.")
    check("ÂM: 2 token NGẮN tầm thường ('plan'+'cash') KHÔNG đủ khớp — nếu đủ thì gần như "
          "mọi dispatch giao dịch đều kêu và cái nhắc thành nhiễu nền",
          out.strip() == "", out[:200])

    out, _ = run_hint("Xem lại cam kết tiền mặt: plan_cash_commitment_selfcheck.py đang đỏ.")
    check("ĐỐI CHỨNG cho ca trên: cùng chủ đề nhưng có token ĐẶC THÙ ⇒ PHẢI khớp "
          "(chứng minh ca âm ở trên im vì ngưỡng, không phải vì logic chết)",
          "plan_cash_commitment_selfcheck.py" in out, out[:200])

    out, _ = run_hint("Vòng fix coord-2026-08-99 (ngày không có trên bảng) — làm tiếp.")
    check("ÂM: ngày KHÁC ⇒ không khớp nhầm sang câu hỏi ngày khác", out.strip() == "", out[:200])


# ── Fail-open: cái nhắc hỏng thì dispatch vẫn phải chạy như chưa từng có nó ──────────────
def case_fail_open():
    out, rc = run_hint("")
    check("prompt rỗng ⇒ im lặng, exit 0", out.strip() == "" and rc == 0, f"rc={rc}")

    td = tempfile.mkdtemp(prefix="qhint_bad_")
    try:
        # Bus hỏng: inbox tồn tại nhưng chứa JSON rác ⇒ tuyệt đối KHÔNG được làm dispatch chết.
        inbox = Path(td) / "bus" / "inbox"
        inbox.mkdir(parents=True)
        (inbox / "Mike.jsonl").write_text("{khong-phai-json\n", encoding="utf-8")
        r = subprocess.run([sys.executable, str(HINT)], input="coord-2026-08-12",
                           capture_output=True, text=True,
                           env=dict(os.environ, BUS_AUDIT_ROOT=td), timeout=60)
        check("bus HỎNG ⇒ fail-open: exit 0, không ném traceback ra stderr",
              r.returncode == 0 and "Traceback" not in r.stderr, f"rc={r.returncode} {r.stderr[:120]}")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    r = subprocess.run([sys.executable, str(HINT)], input="coord-2026-08-12",
                       capture_output=True, text=True,
                       env=dict(os.environ, BUS_AUDIT_ROOT="/khong/ton/tai"), timeout=60)
    check("bus KHÔNG TỒN TẠI ⇒ fail-open: exit 0, im lặng",
          r.returncode == 0 and r.stdout.strip() == "", f"rc={r.returncode}")


# ── Trần số dòng: nhắc phải NGẮN, và nếu cắt thì phải NÓI RA (không cắt im lặng) ─────────
def case_capped_and_says_so():
    board = [("Wags", f"wags-fix-not-confirmed: coord-2026-07-{d:02d}", 5) for d in range(10, 20)]
    prompt = " ".join(f"coord-2026-07-{d:02d}" for d in range(10, 20))
    out, _ = run_hint(prompt, board=board)
    shown = out.count("· [")
    check("nhắc bị chặn ở 3 mục (không đổ cả backlog vào output dispatch)", shown == 3,
          f"{shown} mục")
    check("cắt bớt phải NÓI RA số còn lại + trỏ tới danh sách đầy đủ",
          "và 7 câu hỏi treo khác" in out and "bus_question_audit.py" in out, out[-260:])


# ── Ràng buộc TÍCH HỢP: dispatch.sh phải THẬT SỰ gọi hint (cả 2 nhánh bg và đồng bộ) ─────
def case_wired_into_dispatch():
    src = (ROOT / "bin" / "dispatch.sh").read_text(encoding="utf-8")
    calls = [ln for ln in src.splitlines() if "dispatch_question_hint.py" in ln
             and not ln.strip().startswith("#")]
    check("dispatch.sh gọi hint ở CẢ 2 nhánh (--bg và đồng bộ) — sự cố root-cause-A xảy ra "
          "ở cả hai, vá 1 nhánh là bỏ lọt nửa còn lại", len(calls) >= 2,
          f"{len(calls)} lời gọi: {calls}")
    check("mọi lời gọi đều fail-open tại call site (|| true) — hint hỏng không được giết dispatch",
          all("|| true" in c for c in calls), str(calls))


def main():
    print("— selfcheck dispatch_question_hint.py —")
    for fn in (case_positive_matches, case_negative_stays_silent, case_fail_open,
               case_capped_and_says_so, case_wired_into_dispatch):
        print(f"\n[{fn.__name__}]")
        fn()
    total = len(oks) + len(fails)
    print(f"\n{'❌' if fails else '✅'} {len(oks)}/{total} PASS"
          + (f" — FAIL: {fails}" if fails else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
