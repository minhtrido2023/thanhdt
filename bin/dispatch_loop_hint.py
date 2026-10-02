#!/usr/bin/env python3
"""dispatch_loop_hint.py — nhắc CƠ HỌC: dispatch này có đang rơi vào chuỗi polish nhiều vòng?

VẤN ĐỀ (audit token 2026-10-02). Chi phí Taylor vọt ở 27/9 và 01/10 vì các chuỗi vòng nối đuôi
nhau trên CÙNG một nhánh (lag-exit 6 vòng, ATC UPCOM 4 vòng, price-frame 2 vòng): mỗi vòng = 1
dispatch + 1 arch-review, mỗi vòng vá đúng chỗ reviewer vừa chỉ rồi lộ chỗ kế. Chính sách đã có
trong kb/mike_model_routing.md § "Hai chế độ theo ĐỘ KHÓ + cầu chì" — nhưng nằm trong tài liệu
không nạp tự động nên lúc nhớ lúc quên. Đây là chốt cơ học tại đúng khoảnh khắc dispatch.

NHẮC, KHÔNG CHẶN (cùng tinh thần nudge fable/effort trong dispatch.sh). Hai tín hiệu:
  · VÒNG ≥3: ≥2 job trước (≤24h) đã nhắc cùng token nhánh/worktree ⇒ nhắc cầu chì (Opus high
    review TOÀN BỘ rồi sửa một lượt, hoặc nếu test-only thì hỏi user).
  · TIẾP NỐI mà effort=high: có job trước cùng nhánh + prompt có từ khoá tiếp nối ("tiếp tục",
    "vòng N", "test-only", "hoàn tất"...) mà KHÔNG có từ khoá việc mới ("thiết kế", "giả thuyết
    mới", "tại sao"...) ⇒ nhắc medium (Sonnet) đủ.

Token nhánh = `fix|feat|wire|session/<tên>` hoặc `wt-<tên>`. Nguồn "job trước" = bus/jobs/*.json
(`prompt_summary` 160 ký tự đầu — token đặt muộn hơn thì đếm hụt, thiên về IM thay vì kêu oan).
Job tự sinh `[RESUME ...` bị loại (đó là auto-resume sau usage-limit, không phải vòng polish).

FAIL-OPEN TUYỆT ĐỐI: mọi lỗi ⇒ im lặng, exit 0. Dispatch không bao giờ được hỏng vì cái nhắc.

  echo "<prompt>" | dispatch_loop_hint.py --to <agent> [--effort E] [--model M]
Selfcheck: python3 bin/dispatch_loop_hint_selfcheck.py
"""
import argparse
import glob
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS_DIR = os.environ.get("DISPATCH_LOOP_HINT_JOBS_DIR") or os.path.join(ROOT, "bus", "jobs")
WINDOW_S = 24 * 3600
LOOP_THRESHOLD = 2          # đã có ≥2 job trước ⇒ lần này là vòng ≥3

_BRANCH = re.compile(r"\b((?:fix|feat|wire|session)/[A-Za-z0-9_.-]+|wt-[A-Za-z0-9_.-]+)")
_CONTINUE = re.compile(r"tiếp tục|tiep tuc|vòng\s*\d|vong\s*\d|test-only|hoàn tất|hoan tat|"
                       r"redispatch|dọn scope|apply verdict|polish", re.I)
_NEWWORK = re.compile(r"thiết kế|thiet ke|giả thuyết mới|gia thuyet moi|tại sao|tai sao|"
                      r"chưa hiểu|chua hieu|chưa rõ nguyên nhân|điều tra|dieu tra", re.I)


def branch_tokens(prompt):
    seen = []
    for m in _BRANCH.findall(prompt):
        m = m.rstrip(".,;:)")
        if m not in seen:
            seen.append(m)
    return seen[:3]


def prior_counts(tokens, now=None, jobs_dir=None):
    """{token: số job ≤24h có prompt_summary chứa token}, bỏ job [RESUME."""
    now = now or time.time()
    jobs_dir = jobs_dir or JOBS_DIR
    counts = {t: 0 for t in tokens}
    for f in glob.glob(os.path.join(jobs_dir, "*.json")):
        try:
            if now - os.path.getmtime(f) > WINDOW_S * 2:   # lọc nhanh, đệm 2× cho mtime lệch
                continue
            d = json.load(open(f))
            if now - int(d.get("started_at", 0)) > WINDOW_S:
                continue
            s = d.get("prompt_summary", "") or ""
        except Exception:
            continue
        if s.lstrip().startswith("[RESUME"):
            continue
        for t in tokens:
            if t in s:
                counts[t] += 1
    return counts


def build_hint(prompt, to, effort, model, now=None, jobs_dir=None):
    tokens = branch_tokens(prompt)
    if not tokens:
        return []
    counts = prior_counts(tokens, now=now, jobs_dir=jobs_dir)
    n = max(counts.values())
    tok = max(counts, key=counts.get)
    out = []
    if n >= LOOP_THRESHOLD:
        out.append(f"NOTE: '{tok}' đã được dispatch {n} lần trong 24h — đây là vòng {n + 1}. Hỏi:")
        out.append("  lỗi lần này CÙNG loại với vòng trước (reviewer chỉ rõ chỗ) hay KHÁC loại/ngày càng")
        out.append("  nhiều? Khác loại ⇒ DỪNG vá cuốn chiếu: Opus high review TOÀN BỘ nhánh rồi sửa một")
        out.append("  lượt. Test-only quá 2 vòng ⇒ hỏi user trước (kb/mike_model_routing.md § cầu chì).")
    head = prompt[:400]
    if n >= 1 and effort == "high" and _CONTINUE.search(head) and not _NEWWORK.search(head):
        out.append(f"NOTE: dispatch tiếp nối trên '{tok}' mà --effort high — việc đã rõ hướng/apply")
        out.append("  verdict thì Sonnet --effort medium là đủ (kb/mike_model_routing.md Chế độ A).")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", default="")
    ap.add_argument("--effort", default="")
    ap.add_argument("--model", default="")
    a = ap.parse_args()
    try:
        prompt = sys.stdin.read()
        for line in build_hint(prompt, a.to, a.effort, a.model):
            print(line)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
