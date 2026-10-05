#!/usr/bin/env python3
"""dispatch_loop_hint.py — nhắc CƠ HỌC: dispatch này có đang rơi vào chuỗi polish nhiều vòng?

VẤN ĐỀ (audit token 2026-10-02). Chi phí Taylor vọt ở 27/9 và 01/10 vì các chuỗi vòng nối đuôi
nhau trên CÙNG một nhánh (lag-exit 6 vòng, ATC UPCOM 4 vòng, price-frame 2 vòng): mỗi vòng = 1
dispatch + 1 arch-review, mỗi vòng vá đúng chỗ reviewer vừa chỉ rồi lộ chỗ kế. Chính sách đã có
trong kb/mike_model_routing.md § "Hai chế độ theo ĐỘ KHÓ + cầu chì" — nhưng nằm trong tài liệu
không nạp tự động nên lúc nhớ lúc quên. Đây là chốt cơ học tại đúng khoảnh khắc dispatch.

NHẮC, KHÔNG CHẶN (cùng tinh thần nudge fable/effort trong dispatch.sh). Phần CHẶN CỨNG vòng ≥4
nằm ở bin/dispatch_round_cap.py (exit 7) — dùng lại đúng các hàm chuỗi ở file này. Hai tín hiệu:
  · VÒNG ≥3: ≥2 job trước (≤24h) đã nhắc cùng token nhánh/worktree ⇒ nhắc cầu chì (Opus high
    review TOÀN BỘ rồi sửa một lượt, hoặc nếu test-only thì hỏi user).
  · TIẾP NỐI mà effort=high: có job trước cùng nhánh + prompt có từ khoá tiếp nối ("tiếp tục",
    "vòng N", "test-only", "hoàn tất"...) mà KHÔNG có từ khoá việc mới ("thiết kế", "giả thuyết
    mới", "tại sao"...) ⇒ nhắc medium (Sonnet) đủ.

Token nhánh = `fix|feat|wire|session/<tên>` hoặc `wt-<tên>`. Nguồn "job trước" = bus/jobs/*.json
(`prompt_summary` 160 BYTE đầu (dispatch.sh `head -c 160`; tiếng Việt chiếm nhiều byte) — token đặt muộn hơn thì đếm hụt, thiên về IM thay vì kêu oan).
Record có field `chain_tokens` (dispatch.sh ghi từ PROMPT ĐẦY ĐỦ, từ 2026-10-05) thì khớp tuyệt đối
trên field đó. Job tự sinh `[RESUME`/`[FALLBACK`/`[AUTO-CALLBACK ...` và job `cancelled` bị loại; các dispatch cách nhau <5 phút gộp thành 1
(bản đúp usage-limit/redispatch cùng vòng). Lời nhắc chỉ nêu SỐ DISPATCH đếm được, không khẳng
định số vòng (§29: không đoán điều chưa đọc).

FAIL-OPEN TUYỆT ĐỐI: mọi lỗi ⇒ im lặng, exit 0. Dispatch không bao giờ được hỏng vì cái nhắc.

  echo "<prompt>" | dispatch_loop_hint.py --to <agent> [--effort E] [--model M]
Selfcheck: python3 bin/dispatch_loop_hint_selfcheck.py
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS_DIR = os.environ.get("DISPATCH_LOOP_HINT_JOBS_DIR") or os.path.join(ROOT, "bus", "jobs")
WINDOW_S = 24 * 3600
LOOP_THRESHOLD = 2          # đã có ≥2 dispatch trước ⇒ cầu chì
DEDUP_S = 300               # dispatch cách nhau <5 phút = cùng một vòng

# Neo (arch-review 2026-10-05, killer): `fix|feat|wire|session/` KHÔNG được đứng sau `/` hay ký tự
# từ, VÀ tên phải có ít nhất 1 dấu `-` — chuỗi tĩnh "root_cause/fix/verify/commit" của
# wags_autofix.sh từng khớp `fix/verify` ⇒ mọi dispatch wags_autofix thành 1 chuỗi giả; daily retro
# khớp `fix/commit`. Tên nhánh thật của fleet luôn có `-` (đo 30 ngày). `wt-<tên>` thì ĐƯỢC đứng sau
# đường dẫn (agents/Taylor/wt-abc-1001) nên chỉ neo `\b`.
_BRANCH = re.compile(r"(?<![\w/])(?:fix|feat|wire|session)/[A-Za-z0-9_.]*-[A-Za-z0-9_.-]+"
                     r"|\bwt-[A-Za-z0-9][A-Za-z0-9_.-]*")   # wt- phải theo sau bởi chữ/số (regex `wt-.*` không tính)
_AUTO_PREFIX = ("[RESUME", "[FALLBACK", "[AUTO-CALLBACK")   # tự sinh: không phải vòng mới
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


_JOBID_TS = re.compile(r"_(\d{8}_\d{6})$")


def dispatch_time(d):
    """Giây epoch lúc DISPATCH. Ưu tiên dấu thời gian UTC trong job_id (bất biến) — `started_at`
    bị GHI LẠI ở attempt 2 (đo thật Taylor_20261004_120510: id 12:05Z, started_at 13:26Z).
    job_id không đúng khuôn ⇒ rơi về started_at."""
    m = _JOBID_TS.search(str(d.get("job_id", "")))
    if m:
        try:
            dt = datetime.datetime.strptime(m.group(1), "%Y%m%d_%H%M%S")
            return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())
        except ValueError:
            pass
    return int(d.get("started_at", 0))


def job_matches(d, token):
    """Job thuộc chuỗi `token`? `chain_tokens` (dispatch.sh ghi từ PROMPT ĐẦY ĐỦ, 2026-10-05) khớp
    tuyệt đối; record cũ không có field đó ⇒ tìm chuỗi con trong `prompt_summary` 160 byte."""
    ct = d.get("chain_tokens") or ""
    if token in [x for x in str(ct).split(",") if x]:
        return True
    return token in (d.get("prompt_summary", "") or "")


def prior_jobs(tokens, now=None, jobs_dir=None, mtime_prefilter=True, agent=None):
    """{token: [(dispatch_time, job_id), ...] đã sắp} — job trong cửa sổ WINDOW_S trước `now`.

    `agent` (chỉ round-cap dùng): chỉ đếm job gửi tới ĐÚNG agent đó — để retro/audit tự động
    gửi Mike/Wags mà NHẮC tên nhánh không bị tính thành vòng polish của chuỗi Taylor.

    Bỏ job cancelled, job tự sinh `[RESUME`/`[FALLBACK`/`[AUTO-CALLBACK` (không phải vòng mới). Ném OSError nếu
    thư mục job không đọc được — caller tự quyết fail-open (hint im lặng, round-cap cảnh báo)."""
    now = now or time.time()
    jobs_dir = jobs_dir or JOBS_DIR
    if not os.path.isdir(jobs_dir):
        raise OSError(f"không đọc được thư mục job: {jobs_dir}")
    out = {t: [] for t in tokens}
    for f in glob.glob(os.path.join(jobs_dir, "*.json")):
        try:
            if mtime_prefilter and now - os.path.getmtime(f) > WINDOW_S * 2:   # lọc nhanh, đệm 2×
                continue
            d = json.load(open(f))
            t0 = dispatch_time(d)
            if not (0 <= now - t0 <= WINDOW_S):
                continue
            if d.get("status") == "cancelled":
                continue
            if agent and d.get("to") != agent:
                continue
            s = d.get("prompt_summary", "") or ""
        except Exception:
            continue
        if s.lstrip().startswith(_AUTO_PREFIX):
            continue
        for t in tokens:
            if job_matches(d, t):
                out[t].append((t0, d.get("job_id") or os.path.basename(f)[:-5]))
    for t in out:
        out[t].sort()
    return out


def dedup_rounds(entries):
    """[(t, job_id)] đã sắp ⇒ danh sách VÒNG; dispatch cách nhau <DEDUP_S gộp vào 1 vòng."""
    rounds, last = [], None
    for t, jid in entries:
        if last is None or t - last >= DEDUP_S:
            rounds.append([])
        rounds[-1].append((t, jid))
        last = t
    return rounds


def prior_counts(tokens, now=None, jobs_dir=None):
    """{token: số dispatch ≤24h thuộc chuỗi} — bỏ huỷ/resume/fallback, gộp bản đúp <DEDUP_S."""
    try:
        pj = prior_jobs(tokens, now=now, jobs_dir=jobs_dir)
    except OSError:
        return {t: 0 for t in tokens}
    return {t: len(dedup_rounds(e)) for t, e in pj.items()}


def build_hint(prompt, to, effort, model, now=None, jobs_dir=None):
    tokens = branch_tokens(prompt)
    if not tokens:
        return []
    counts = prior_counts(tokens, now=now, jobs_dir=jobs_dir)
    n = max(counts.values())
    tok = max(counts, key=counts.get)
    out = []
    if n >= LOOP_THRESHOLD:
        out.append(f"NOTE: '{tok}' đã có {n} dispatch trước trong 24h (loại huỷ/resume/bản đúp). Hỏi:")
        out.append("  lỗi lần này CÙNG loại với vòng trước (reviewer chỉ rõ chỗ) hay KHÁC loại/ngày càng")
        out.append("  nhiều? Khác loại ⇒ DỪNG vá cuốn chiếu: Opus high review TOÀN BỘ nhánh rồi sửa một")
        out.append("  lượt. Test-only quá 2 vòng ⇒ hỏi user trước (kb/mike_model_routing.md § cầu chì).")
    head = prompt[:400]
    # Chỉ nhắc "medium" khi CHƯA chạm cầu chì — tránh 2 lời khuyên ngược nhau (B rồi A) cùng lúc.
    if 1 <= n < LOOP_THRESHOLD and effort == "high" and _CONTINUE.search(head) \
            and not _NEWWORK.search(head):
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
