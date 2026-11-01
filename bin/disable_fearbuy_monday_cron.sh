#!/usr/bin/env bash
# Tắt cron quét thứ Hai fear-buy (user duyệt 2026-11-01). Chạy:  bash mike/bin/disable_fearbuy_monday_cron.sh
# Thử không sửa gì:  bash mike/bin/disable_fearbuy_monday_cron.sh --dry
# Hoàn tác:          crontab ~/crontab_backup_20261101.txt
set -u
BK="$HOME/crontab_backup_20261101.txt"
NEW="$(mktemp)"
trap 'rm -f "$NEW"' EXIT

crontab -l > "$BK" || { echo "LỖI: không đọc được crontab"; exit 1; }
awk '/fearbuy_weekly_scan\.sh --mode monday/ && !/^[[:space:]]*#/ { print "# TAT 2026-11-01 (user: bo quet thu Hai fearbuy) # " $0; next } { print }' "$BK" > "$NEW"

N="$(diff "$BK" "$NEW" | grep -c '^>')"
if [ "$N" -ne 1 ]; then
  echo "DỪNG: kỳ vọng đúng 1 dòng bị comment, thực tế $N. Không sửa crontab."
  diff "$BK" "$NEW"
  exit 1
fi

echo "Dòng sẽ bị comment:"
diff "$BK" "$NEW" | grep '^>' | cut -c1-200

if [ "${1:-}" = "--dry" ]; then
  echo "(--dry: chưa sửa gì. Chạy lại không có --dry để áp dụng.)"
  exit 0
fi

crontab "$NEW" || { echo "LỖI: crontab không nhận file mới. Crontab cũ vẫn nguyên."; exit 1; }
echo "ĐÃ ÁP DỤNG. Kiểm tra:"
crontab -l | grep -n "mode monday" | cut -c1-160
echo "Backup: $BK  (hoàn tác: crontab $BK)"
