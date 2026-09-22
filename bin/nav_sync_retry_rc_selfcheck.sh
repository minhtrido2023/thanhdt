#!/usr/bin/env bash
# nav_sync_retry_rc_selfcheck.sh — mutation test (d) cho job Taylor_20260922_111128:
# "rc=5 (corp_action_gate_v2 share_event_block) KHÔNG bị nav_sync_retry.sh retry 2h như rc=4."
#
# rc=5 là mã MỚI (P1, arch-review lần trước: rc=4 bị TÁI SỬ DỤNG sai — nav_sync_retry.sh sẽ
# retry 2h rồi báo "lệch giá >5%" cho một lỗi có thể là gap 0,0%). Thiết kế v2 KHÔNG sửa logic
# nav_sync_retry.sh (nó vẫn chỉ so `[ "$RC" != "4" ]`) mà dựa vào 2 bất biến TĨNH.
#
# ⚠️ PHẠM VI THẬT của test này (sửa 2026-09-22, arch-review vòng 2 mục [7] — header cũ tự khai
# "xác nhận CẢ HAI bằng harness thật", SAI):
#   • Bất biến #1 KHÔNG được harness nào chạy. Nó là khẳng định TĨNH, đọc từ mã nguồn
#     (eod_trading_report.sh: `if [ "$rc" = "4" ]`, so sánh tuyệt đối). Muốn kiểm cơ học thì
#     phải dựng harness riêng cho eod_trading_report.sh — chưa có.
#   • Bất biến #2 CÓ chạy thật: harness dưới đây gọi chính `nav_sync_retry.sh` với rc=5.
#
#   1. [TĨNH, chưa có harness] eod_trading_report.sh CHỈ ghi marker nav_pending_retry cho rc=4
#      (`[ "$rc" = "4" ]` tuyệt đối) — rc=5 không bao giờ có marker để nav_sync_retry.sh nhặt lên.
#   2. [CHẠY THẬT] NẾU giả sử có marker (vd tồn dư/bug tương lai), nav_sync_retry.sh với rc=5 phải XOÁ
#      marker ngay (nhánh "đổi loại lỗi giữa chừng") — KHÔNG rơi vào nhánh "vẫn rc=4" chờ tới
#      cutoff 21:15 rồi mới đổi hậu tố .stuck. rc=4 PHẢI escalate .stuck sau cutoff; rc=5 thì
#      KHÔNG BAO GIỜ được vào nhánh đó (không lệ thuộc giờ chạy).
#
# Chạy:  bash mike/bin/nav_sync_retry_rc_selfcheck.sh
# Phải PASS y hệt: env -u TZ TZ=America/New_York bash mike/bin/nav_sync_retry_rc_selfcheck.sh
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASS=0
FAIL=0

check() {
  local name="$1" cond="$2"
  if [ "$cond" = "0" ]; then
    echo "  ✓ $name"
    PASS=$((PASS + 1))
  else
    echo "  ✗ $name"
    FAIL=$((FAIL + 1))
  fi
}

# Dựng ROOT giả lập: bin/nav_sync_retry.sh thật (copy nguyên văn) + stub cho mọi thứ nó gọi.
run_case() {
  local stub_rc="$1" force_hhmm="$2" label="$3"
  local tmp; tmp="$(mktemp -d)"
  mkdir -p "$tmp/bin" "$tmp/state/nav_pending_retry"
  cp "$HERE/nav_sync_retry.sh" "$tmp/bin/nav_sync_retry.sh"

  cat > "$tmp/bin/daily_nav_snapshot.py" <<EOF
#!/usr/bin/env python3
import sys
print("stub gate output rc=$stub_rc")
sys.exit($stub_rc)
EOF
  chmod +x "$tmp/bin/daily_nav_snapshot.py"

  # Stub python3 trong PATH trỏ về python3 thật (script gọi "python3 \$ROOT/bin/...")
  : > "$tmp/notify_calls.log"
  : > "$tmp/append_event_calls.log"
  cat > "$tmp/bin/notify_thread.sh" <<EOF
#!/usr/bin/env bash
echo "\$1" >> "$tmp/notify_calls.log"
EOF
  chmod +x "$tmp/bin/notify_thread.sh"
  cat > "$tmp/bin/append_event.sh" <<EOF
#!/usr/bin/env bash
echo "\$*" >> "$tmp/append_event_calls.log"
EOF
  chmod +x "$tmp/bin/append_event.sh"

  # Fake `date`: chỉ can thiệp đúng 2 dạng gọi mà nav_sync_retry.sh dùng
  # (TZ=... date +%H%M / +%Y-%m-%d); mọi gọi khác rơi về /usr/bin/date thật.
  mkdir -p "$tmp/fakebin"
  cat > "$tmp/fakebin/date" <<EOF
#!/usr/bin/env bash
for a in "\$@"; do
  case "\$a" in
    +%H%M) echo "$force_hhmm"; exit 0 ;;
    +%Y-%m-%d) echo "2026-09-23"; exit 0 ;;
  esac
done
exec /usr/bin/date "\$@"
EOF
  chmod +x "$tmp/fakebin/date"

  local marker="$tmp/state/nav_pending_retry/SpaceX_2026-09-23.log"
  echo "stale marker content" > "$marker"

  PATH="$tmp/fakebin:$tmp/bin:$PATH" bash "$tmp/bin/nav_sync_retry.sh" >/dev/null 2>&1

  local marker_gone=1 stuck_exists=1
  [ -f "$marker" ] || marker_gone=0
  ls "$tmp/state/nav_pending_retry/"*.stuck_* >/dev/null 2>&1 && stuck_exists=0

  echo "  [$label] marker_gone(0=yes)=$marker_gone stuck_created(0=yes)=$stuck_exists" >&2
  rm -rf "$tmp"
  echo "$marker_gone $stuck_exists"
}

echo "1. rc=4, giờ TRONG cửa sổ (20:00) — im lặng chờ, KHÔNG xoá marker, KHÔNG stuck"
read -r m4_early s4_early <<<"$(run_case 4 2000 rc4-early)"
check "rc=4@20:00: marker vẫn còn (chờ lượt cron kế)" "$([ "$m4_early" = 1 ] && echo 0 || echo 1)"
check "rc=4@20:00: chưa tạo .stuck (chưa tới cutoff)" "$([ "$s4_early" = 1 ] && echo 0 || echo 1)"

echo "2. rc=4, giờ SAU cutoff (21:20) — phải escalate .stuck (hành vi hiện có, KHÔNG đổi)"
read -r m4_late s4_late <<<"$(run_case 4 2120 rc4-late)"
check "rc=4@21:20: marker đổi hậu tố .stuck_ (không còn tên gốc)" "$m4_late"
check "rc=4@21:20: .stuck ĐƯỢC tạo (retry 2h hết hạn → escalate)" "$s4_late"

echo "3. rc=5 (corp_action_gate_v2 share_event_block), giờ SAU cutoff (21:20)"
read -r m5_late s5_late <<<"$(run_case 5 2120 rc5-late)"
check "rc=5@21:20: marker bị XOÁ ngay (nhánh 'đổi loại lỗi', không chờ)" "$m5_late"
check "rc=5@21:20: KHÔNG tạo .stuck (không lẫn với ca PRICE_XCHECK rc=4)" "$([ "$s5_late" = 1 ] && echo 0 || echo 1)"

echo "4. rc=5, giờ TRONG cửa sổ (20:00) — vẫn phải xoá NGAY, không đợi 2h như rc=4"
read -r m5_early s5_early <<<"$(run_case 5 2000 rc5-early)"
check "rc=5@20:00: marker bị XOÁ ngay (khác hẳn rc=4@20:00 ở case 1)" "$m5_early"
check "rc=5@20:00: KHÔNG tạo .stuck" "$([ "$s5_early" = 1 ] && echo 0 || echo 1)"

echo
echo "$PASS PASS, $FAIL FAIL"
[ "$FAIL" -eq 0 ]
