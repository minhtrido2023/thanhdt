#!/usr/bin/env bash
# adjfactor_drift_daily.sh [--dry-run]    — runner HẰNG NGÀY của LAYER 1 (detect-only)
#
# ⚠️ CHƯA CÀI CRON. Dòng crontab đề xuất (chờ user sign-off, §11 phải ghi `kb/cron_registry.md`
# TRƯỚC khi thêm):
#     10 0 * * 2-6  cd /home/trido/thanhdt/WorkingClaude/mike && bin/adjfactor_drift_daily.sh \
#                     >> logs/adjfactor_drift_$(date +\%Y\%m).log 2>&1
# 00:10 ICT T3-T7 = SAU khi `sync_bq_cache_daily.sh` (23:45 ICT) đã chạy — detector đọc LỊCH SỬ
# từ BQ nên đây là đúng ca §6 cho phép dùng BQ, nhưng chạy TRƯỚC sync thì phiên mới nhất chưa có.
# Detector tự neo `asof` vào `MAX(time)` của bảng, KHÔNG vào đồng hồ host, nên chạy sớm chỉ làm
# cửa sổ cũ đi một phiên — không bao giờ đọc ra một ngày không tồn tại.
#
# Vì sao là một runner chứ không phải `detector | alert` thẳng trong crontab: pipe làm MẤT rc của
# detector (chỉ rc của alert ra ngoài) ⇒ **rc=1 "BQ chết, không kết luận được gì" sẽ bị đọc thành
# "không có cảnh báo nào"** — đúng lớp lỗi §29/§14 (im lặng không phân biệt được với khoẻ).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# TÊN kênh trong `kb/discord_channels.json`, KHÔNG phải ID trần (gate `bin/discord_id_gate.sh`;
# `notify_thread.sh` tự resolve tên). `trading_daily` = alert vận hành sống, khác `trading_report`.
TOPIC="${ADJFACTOR_ALERT_TOPIC:-trading_daily}"

# `--dry-run` là cờ của ALERT, không phải của detector — tách ra trước khi gọi. Nếu chuyển thẳng
# "$@" vào detector thì argparse của nó TỪ CHỐI (rc=2) ⇒ rơi vào nhánh "lỗi hạ tầng" và GỬI
# DISCORD THẬT ngay trong một lượt mà người chạy tưởng là thử khan.
DRY=()
DET_ARGS=()
for a in "$@"; do
  if [ "$a" = "--dry-run" ]; then
    DRY=(--dry-run)
  else
    DET_ARGS+=("$a")
  fi
done

OUT="$("$ROOT/bin/adjfactor_drift_detect.py" "${DET_ARGS[@]}" 2>&1)"
DET_RC=$?
printf '%s\n' "$OUT"

if [ "$DET_RC" -eq 1 ] || [ "$DET_RC" -eq 2 ]; then
  # KHÔNG gọi alert: không có kết luận nào để cảnh báo, và im lặng ở đây là SAI — nói thẳng ra
  # rằng lượt quét KHÔNG chạy được, kèm LỖI THẬT mà detector đã in (§29).
  echo "adjfactor_drift_daily: detector rc=$DET_RC -> KHONG ket luan gi, KHONG goi alert." >&2
  MSG="⚠️ **Layer 1 adjfactor: LƯỢT QUÉT KHÔNG CHẠY ĐƯỢC** (rc=${DET_RC})
Không có kết luận nào cho hôm nay — **đây KHÔNG phải \"không có lệch\"**.
\`\`\`
$(printf '%s\n' "$OUT" | tail -12)
\`\`\`"
  if [ "${#DRY[@]}" -gt 0 ]; then
    echo "[dry-run] KHONG gui Discord. Noi dung se gui:" >&2
    printf '%s\n' "$MSG" >&2
  elif ! NOTIFY_ERR="$("$ROOT/bin/notify_thread.sh" "$MSG" "$TOPIC" 2>&1 >/dev/null)"; then
    echo "adjfactor_drift_daily: notify_thread.sh THAT BAI khi bao loi ha tang. Loi that: ${NOTIFY_ERR}" >&2
  fi
  exit "$DET_RC"
fi

printf '%s\n' "$OUT" | "$ROOT/bin/adjfactor_drift_alert.sh" "$TOPIC" "${DRY[@]}"
ALERT_RC=$?
echo "adjfactor_drift_daily: detector rc=$DET_RC alert rc=$ALERT_RC" >&2
exit "$ALERT_RC"
