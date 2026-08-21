#!/usr/bin/env bash
# utc_text_gate.sh <file.sh|file.py> [...]
#
# Pre-commit gate — CHẶN CỨNG commit nếu code thực thi (bin/, hooks/) tạo ra GIỜ-TRONG-NGÀY
# theo UTC ở dạng dễ lọt vào văn bản gửi người (Discord/Telegram/email).
#
# WHY (sự cố thật, 2 lần trong cùng ngày 2026-08-21):
#   Lần 1: LLM tự viết "03:25 sáng" khi thật là 17:26 ICT → đã sửa bằng header stamp ở tầng
#          transport ccdb (outbound_format.py).
#   Lần 2 (ngay sau khi deploy lần 1): thân tin vẫn có "12:14 UTC (~435s)" — do chính
#          dispatch.sh sinh bằng `date -u ... '+%H:%M UTC'`, không phải LLM. Header đúng, thân sai.
#   Hai lần, hai producer khác nhau (LLM / script), cùng một triệu chứng với người đọc. Văn
#   bản hướng dẫn "luôn dùng TZ=Asia/Ho_Chi_Minh" đã có trong coding_guidelines §16 từ lâu —
#   vẫn lọt. Gate này biến §16 từ lời dặn thành điều kiện CƠ HỌC để commit được (chính sách
#   enforcement 2026-08-01: "đẩy bài học cũ ra công cụ/linter thay vì văn xuôi").
#
# PATTERN chặn (per-line, chỉ code thực thi):
#   (a) `date -u` kèm định dạng giờ-trong-ngày `%H` / `%T` / `%R`       → người đọc sẽ thấy giờ UTC
#   (b) chuỗi định dạng chứa ` UTC'` / ` UTC"` / `%H:%M UTC`              → gắn nhãn UTC vào text
#   (c) Python: `utcnow()` hoặc `timezone.utc` đi cùng `strftime(... %H`  → cùng ý (a)
# KHÔNG chặn: `date -u +%Y-%m-%d` / `%Y%m%d_%H%M%S` dùng cho TÊN FILE LOG / cutoff (giờ trong
# tên file log không đi tới người); ISO `%Y-%m-%dT%H:%M:%SZ` cho bus event (máy đọc, có Z).
# Thoát có chủ đích (hiếm — phải ghi lý do cùng dòng): thêm `# utc-ok: <lý do>` cuối dòng.
#
# Đã đo trên repo thật trước khi bật (2026-08-21): 1 hit thật (dispatch.sh:1584 — đúng ca sự
# cố, đã sửa), 0 false-positive trong bin/ + hooks/. Cùng kỷ luật với bin/discord_id_gate.sh.
set -uo pipefail

[ "$#" -eq 0 ] && exit 0

# (a) date -u + time-of-day format; (b) literal UTC label inside a format string;
# (c) python utcnow/timezone.utc + strftime with %H on the same line.
PAT_A='date -u[^|;&]*\+[^|;&]*%(H|T|R)\b'
# Machine-readable shapes (log filenames, ISO-8601 with explicit Z for bus/JSON) are NOT
# human-facing clock text — excluded for all three patterns.
PAT_EXCL='%Y%m%d_%H%M%S|%Y%m%d%H%M|%H:%M:%SZ|%H:%MZ|%FT%TZ|%TZ'
PAT_B='%(H:%M|R|T)[^'"'"'"]*[[:space:]](UTC|GMT)\b'
PAT_C='(utcnow\(\)|timezone\.utc|time\.gmtime)[^#]*strftime\([^)]*%H'

BLOCKED=0
for f in "$@"; do
  [ -f "$f" ] || continue
  case "$f" in *_selfcheck.sh|*_selfcheck.py|*/tests/*) continue;; esac
  while IFS= read -r line; do
    ln="${line%%:*}"; body="${line#*:}"
    [[ "$body" =~ \#[[:space:]]*utc-ok: ]] && continue
    # Skip pure comment lines.
    [[ "$body" =~ ^[[:space:]]*# ]] && continue
    echo "  🔴 $f:$ln: $(printf '%s' "$body" | head -c 140)  ← giờ UTC trong text gửi người [HARD-BLOCK] (utc_text_gate.sh)"
    BLOCKED=$((BLOCKED + 1))
  done < <(
    { grep -nE "$PAT_A" "$f" ; grep -nE "$PAT_B" "$f" ; grep -nE "$PAT_C" "$f" ; } 2>/dev/null \
      | grep -vE "$PAT_EXCL" | sort -t: -k1,1n -u
  )
done

if [ "$BLOCKED" -gt 0 ]; then
  echo
  echo "utc_text_gate: $BLOCKED dòng tạo giờ-trong-ngày theo UTC. Giờ cho NGƯỜI đọc phải là ICT:"
  echo "  bash:   TZ='Asia/Ho_Chi_Minh' date '+%H:%M ICT'        python: datetime.now(ZoneInfo('Asia/Ho_Chi_Minh'))"
  echo "  Khoảng thời gian ước lượng: ghi PHÚT (~7 phút), không giây (~435s)."
  echo "  Thoát có chủ đích (phải ghi lý do): thêm  # utc-ok: <lý do>  cuối dòng.  (kb/coding_guidelines.md §16)"
  exit 1
fi
exit 0
