#!/usr/bin/env python3
"""diagnosis_evidence_gate.py <file.sh> [...]

Pre-commit gate — CHẶN CỨNG commit khi một đoạn code VỨT BỎ stderr của lệnh vừa hỏng
(`2>/dev/null`) rồi ở CHÍNH nhánh hỏng đó in ra một CHẨN ĐOÁN cho người đọc (`|| die "…"`).
Nghĩa là: bằng chứng về nguyên nhân đang nằm trong tay thì ném đi, rồi đoán thay nó.

WHY (không phải một quy ước nữa — §28 đã có từ 2026-08-13 và ĐÃ THẤT BẠI 3 lần sau đó):
Cùng một khiếm khuyết "checker/guard hardcode chẩn đoán thay vì đọc bằng chứng" nổ ở 3 vị trí
khác nhau trong ~1 tuần:
  1. 2026-08-21 `ops_health_check.sh` §5b — quy CHỤP mọi ca cách ly là shell word-split
     (commit 53c16004).
  2. 2026-08-25 `ops_health_check.sh` check#9 — hardcode "nghi quoting bug 08-01" cho cả ca
     HOST TẮT, cron chưa từng fire (commit 52eb62ea).
  3. 2026-08-28 `append_event.sh` guard JSON — `json.loads` biết chính xác `Extra data: char
     1667` nhưng `2>/dev/null` vứt đi, rồi khẳng định "nhiều khả năng bị cắt cụt"; ops_health
     §5b chép nguyên văn vào dispatch ⇒ người xử lý bị dẫn sai hướng ngay dòng đầu
     (commit 55b3f34c). Escalation: bus question
     `retro-pattern-recurring-checker-hardcode-diagnosis-3`, retro-2026-08-28 Pattern A.
Vá từng call-site 3 lần không ngăn được vị trí thứ 4. Gate này biến "đừng đoán, in bằng chứng"
từ quy ước con-người-phải-nhớ thành ĐIỀU KIỆN CƠ HỌC để commit — cùng khuôn với
bin/shellcheck_gate.sh / bin/discord_id_gate.sh / bin/utc_text_gate.sh.

PHẠM VI CHỈ BẮT ĐƯỢC 1/3 — nói thẳng, đừng để ai tưởng gate này phủ cả họ lỗi:
  - BẮT được ca #3: "bằng chứng có trong tay rồi vứt" là một bit CƠ HỌC (`2>/dev/null` = vứt vs
    `2>&1` = giữ), kiểm được không cần hiểu ngôn ngữ tự nhiên.
  - KHÔNG bắt được ca #1/#2: ở đó không hề có exception nào — chỉ là văn xuôi khẳng định một
    nguyên nhân mà code chưa hề đọc bằng chứng nào để biết. Phát hiện việc đó = đọc hiểu ngôn
    ngữ tự nhiên, không phải việc của một lint rule. Nửa đó thuộc về review checklist —
    kb/coding_guidelines.md §29.

CHỮ KÝ (đã đo trên repo thật TRƯỚC khi chốt, theo đúng kỷ luật của shellcheck_gate.sh):
  cùng MỘT câu lệnh (nối qua `\` xuống dòng) có ĐỦ 3 điều kiện —
    (a) `2>/dev/null` → stderr bị VỨT (dạng ĐÚNG `2>&1 >/dev/null` — bắt lại để in — không
        khớp, nên bản đã vá tự động sạch);
    (b) nhánh `||` gọi một hàm CHẾT (`die`/`fail`/`_die`/`abort`) kèm thông điệp trong nháy.
  Điều kiện (c) là cái tách true-positive khỏi 67 ca `|| echo 0` / `|| echo unknown` hợp lệ
  (default scalar khi thiếu file — không phải chẩn đoán gửi cho người). Mọi điều kiện ở đây
  đều đã bị MUTATION kiểm: phá cái nào thì selfcheck ĐỎ cái đó (2 điều kiện thừa — "không có
  2>&1" và "thông điệp ≥40 ký tự" — sống sót mutation ⇒ là guard giả ⇒ ĐÃ GỠ, không giữ lại
  cho có). Đo thật:
    - rule THÔ (chỉ a+b+`|| die|echo|printf`): 68 hit / 76 script → 1 đúng, 67 sai ⇒ vô dụng,
      đúng cái "một rule bắn 200 lần với 50%" mà shellcheck_gate.sh cảnh báo.
    - rule NÀY: HEAD = **0 hit** trên toàn bộ bin/*.sh + hooks/*.sh; chạy trên
      `git show 55b3f34c^:bin/append_event.sh` (bản ĐÚNG LÚC LỖI) = **1 hit, đúng dòng 108**.
      Fires on the real bug, silent on the real repo.

Escape hatch (cùng khuôn MIKE_CQ_GATE / MIKE_COMMIT_GATE): env MIKE_DIAG_GATE=warn hạ BLOCK
xuống cảnh báo không chặn; =off tắt hẳn.
"""
import os
import re
import sys

# `2>/dev/null` = stderr bị VỨT. Cố ý KHÔNG khớp `2>&1 >/dev/null` — đó chính là cách ĐÚNG
# (bắt stderr lại để in ra), và là hình dạng của bản đã vá 55b3f34c.
DISCARD = re.compile(r"2>\s*/dev/null")
# Chỉ hàm CHẾT + có thông điệp trong nháy. Đây là điều kiện tách 1 true-positive khỏi 67 ca
# `|| echo 0` / `|| echo unknown` hợp lệ (default scalar khi thiếu file, không phải chẩn đoán
# gửi cho người) — đo thật trên repo, xem docstring. Mutation M2 (thêm echo|printf vào đây)
# làm selfcheck ĐỎ với 67 false-positive ⇒ điều kiện này có canh thật.
DIAG = re.compile(r"\|\|\s*(die|fail|_die|abort)\b[^\n]{0,20}[\"']", re.S)


def scan(text):
    """Trả [(lineno, dòng)] cho mỗi chỗ khớp chữ ký.

    Quét theo DÒNG + cửa sổ 8 dòng, KHÔNG nối câu lệnh qua `\\`: bản đầu có vòng nối câu lệnh,
    nhưng mutation "bỏ vòng nối" SỐNG SÓT toàn bộ selfcheck (kể cả ca thật 2026-08-28 trải 2
    dòng vật lý) — cửa sổ 8 dòng đã phủ đúng phần đó rồi. Guard không assertion nào giết được
    là guard giả; gỡ thay vì giữ cho có (retro-2026-08-28 Pattern B).
    """
    hits = []
    lines = text.split("\n")
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("#") or not DISCARD.search(line):
            continue
        # `die "…"` hầu như luôn nằm ở dòng SAU lệnh bị `2>/dev/null` (nối bằng `\\` hoặc
        # không), và bản thân thông điệp trải nhiều dòng — nên phải nhìn qua cửa sổ, không chỉ
        # dòng hiện tại. 8 dòng: đủ cho ca thật, mutation thu về 1 dòng làm selfcheck ĐỎ.
        if DIAG.search("\n".join(lines[idx : idx + 8])):
            hits.append((idx + 1, line.strip()))
    return hits


def main(argv):
    mode = os.environ.get("MIKE_DIAG_GATE", "block")
    if mode == "off":
        return 0
    blocked = 0
    for path in argv:
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            for lineno, stmt in scan(fh.read()):
                blocked += 1
                sys.stderr.write(
                    f"\n⛔ {path}:{lineno} — vứt stderr rồi ĐOÁN nguyên nhân\n"
                    f"   {stmt[:160]}\n"
                    "   `2>/dev/null` ném đi đúng thứ nói cho bạn biết chuyện gì đã xảy ra, rồi\n"
                    "   nhánh `|| die` khẳng định một nguyên nhân code chưa hề đọc. Ba lần đã cắn\n"
                    "   thật (08-21, 08-25, 08-28) — xem đầu bin/diagnosis_evidence_gate.py.\n"
                    "   SỬA: bắt stderr lại rồi in ra, đừng vứt:\n"
                    "     _err=\"$(cmd ... 2>&1 >/dev/null)\" || die \"…\n  Lỗi thật: $_err\"\n"
                )
    if blocked and mode != "warn":
        sys.stderr.write(
            f"\n⛔ diagnosis-evidence gate: {blocked} chỗ. Bỏ qua có chủ đích: "
            "MIKE_DIAG_GATE=warn (cảnh báo) / =off (tắt).\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
