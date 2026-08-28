#!/usr/bin/env python3
# Docstring là RAW (r"""): nó chứa `\` làm ví dụ cú pháp bash — chuỗi thường sinh
# SyntaxWarning "invalid escape sequence" ra stderr, làm bẩn cả nhánh MIKE_DIAG_GATE=off
# (đáng lẽ im hoàn toàn) và làm đỏ diagnosis_evidence_gate_selfcheck.py.
r"""diagnosis_evidence_gate.py <file.sh> [...]

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
  trong CÙNG một cửa sổ 8 dòng phải có ĐỦ 2 điều kiện —
    (a) stderr bị VỨT, ở BẤT KỲ cách viết nào bash dùng: `2>/dev/null`, `>/dev/null 2>&1`
        (idiom silencing phổ biến NHẤT của bash), `&>/dev/null`, `2>&-`. Cố ý KHÔNG khớp dạng
        ĐÚNG `2>&1 >/dev/null` (bắt stderr lại để in) — nên bản đã vá tự động sạch;
    (b) nhánh `||` gọi một hàm CHẾT (`die`/`_die`/`fail`/`_fail`/`fatal`/`abort`/`bail`, kể cả
        khi bọc trong nhóm ngoặc nhọn `|| { die "…"; }`) kèm thông điệp trong nháy.
  Điều kiện (b) là cái tách true-positive khỏi các ca `|| echo 0` / `|| echo unknown` hợp lệ
  (default scalar khi thiếu file — không phải chẩn đoán gửi cho người). Mọi điều kiện ở đây
  đều đã bị MUTATION kiểm: phá cái nào thì selfcheck ĐỎ cái đó (2 điều kiện thừa — "không có
  2>&1" và "thông điệp ≥40 ký tự" — sống sót mutation ⇒ là guard giả ⇒ ĐÃ GỠ, không giữ lại
  cho có). Đo thật trên corpus HÔM NAY (100 file .sh trong bin/ + hooks/ ở HEAD):
    - rule THÔ (a + `|| die|echo|printf`): **99 hit / 100 script** (33 file) → 1 đúng, còn lại
      sai ⇒ vô dụng, đúng cái "một rule bắn 200 lần với 50%" mà shellcheck_gate.sh cảnh báo.
    - rule NÀY: HEAD = **0 hit** trên toàn bộ bin/*.sh + hooks/*.sh; chạy trên
      `git show 55b3f34c^:bin/append_event.sh` (bản ĐÚNG LÚC LỖI) = **1 hit, đúng dòng 108**;
      im trên bản đã vá `55b3f34c`. Fires on the real bug, silent on the real repo.

BỀ RỘNG VÒNG 2 (2026-08-29, arch-review NEEDS_CHANGES trên 15c27547): bản đầu chỉ nhận ra ĐÚNG
MỘT cách viết (`cmd 2>/dev/null || die`). `>/dev/null 2>&1` (repo đang dùng 84 lần), `|| { die; }`
(41 chỗ `|| {`) và `|| _fail` (hàm có thật ở bin/preflight_check.sh:36) vứt stderr y hệt nhưng đi
qua gate im lặng — trong khi bịt lại đo được VẪN 0 false-positive, tức bề rộng bỏ lại là MIỄN PHÍ
chứ không do sức ép FP. Với một fix mà tiền đề là "vá call-site 3 lần không ngăn được vị trí thứ
4", để vị trí thứ 4 lọt chỉ vì nó viết theo cách repo đang dùng 84 lần là chưa đạt mục tiêu.

CÒN HỞ (ghi ở đây VÀ trên bus/KB, đừng để chỉ nằm trong docstring): dạng PYTHON của cùng khiếm
khuyết (`subprocess.run(..., stderr=subprocess.DEVNULL)` rồi hardcode chẩn đoán) CHƯA được gate
nào canh — scope hiện tại chỉ `^(bin|hooks)/.*\.sh$`, trong khi 2 gate anh em đã dùng `(sh|py)`
và có ≥4 file bin/*.py đang dùng DEVNULL.

Escape hatch (cùng khuôn MIKE_CQ_GATE / MIKE_COMMIT_GATE): env MIKE_DIAG_GATE=warn hạ BLOCK
xuống cảnh báo không chặn; =off tắt hẳn.
"""
import os
import re
import sys

# stderr bị VỨT — MỌI cách viết bash dùng để làm câm stderr. Cố ý KHÔNG khớp `2>&1 >/dev/null`
# (bắt stderr lại để in ra) — đó là cách ĐÚNG và là hình dạng của bản đã vá 55b3f34c. Thứ tự
# quan trọng: `>/dev/null 2>&1` VỨT stderr, `2>&1 >/dev/null` GIỮ — regex phân biệt bằng thứ tự.
DISCARD = re.compile(
    r"2>\s*/dev/null"  # cmd 2>/dev/null
    r"|>\s*/dev/null\s+2>&1"  # cmd >/dev/null 2>&1 — idiom phổ biến nhất, 84 hit trong repo
    r"|&>\s*/dev/null"  # cmd &>/dev/null (bash gộp)
    r"|2>&-"  # đóng hẳn descriptor stderr
)
# Chỉ hàm CHẾT + có thông điệp trong nháy, kể cả khi bọc trong nhóm ngoặc nhọn `|| { die …; }`
# (41 chỗ `|| {` trong repo). Đây là điều kiện tách true-positive khỏi các ca `|| echo 0` /
# `|| echo unknown` hợp lệ (default scalar khi thiếu file, không phải chẩn đoán gửi cho người)
# — đo thật: nới emitter sang echo|printf làm rule bắn 99 hit/100 script. Mutation M2 canh đúng
# nhánh đó. `_fail` có thật ở bin/preflight_check.sh:36.
DIAG = re.compile(
    r"\|\|\s*\{?\s*(_die|_fail|die|fail|fatal|abort|bail)\b[^\n]{0,20}[\"']", re.S
)


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
                    "   Vứt stderr (`2>/dev/null` / `>/dev/null 2>&1` / `&>/dev/null` / `2>&-`)\n"
                    "   ném đi đúng thứ nói cho bạn biết chuyện gì đã xảy ra, rồi\n"
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
