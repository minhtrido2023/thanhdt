#!/usr/bin/env bash
# prefetch_dnse_statement.sh — tải statement khớp lệnh DNSE (email ~16:09 ICT) của HÔM NAY về
# data/execution_logs/dnse_khoplenh_broker_confirm_<DD-MM-YYYY>.csv TRƯỚC các job NAV.
#
# Vì sao (22/10/2026, bán tay DRI 21/10): cổng KL của daily_nav_snapshot / compute_active_nav /
# park_holdings đọc statement bằng `load_broker_fills(allow_fetch=False)` (cố ý — hàm thuần, không
# I/O mạng). Hệ quả: KHÔNG AI tải statement ⇒ ngày chỉ có lệnh bán TAY, journal bot không có fill ⇒
# phần dư KL không giải thích được ⇒ chặn dòng NAV (rc=5) dù email đã về từ 16:09.
#
# Hợp đồng: idempotent (CSV đã có ⇒ không gọi mạng) · KHÔNG BAO GIỜ làm hỏng caller (luôn exit 0) ·
# ngày không khớp lệnh nào DNSE không gửi email ⇒ không có CSV là bình thường (không báo lỗi).
# Gọi bởi: cron 16:40 + 18:40 ICT T2-T6 (log logs/prefetch_dnse_statement.log); nav_snapshot_daily.sh (sau chờ EOD); đầu compute_active_nav_all.sh.
# Test: PREFETCH_WC_ROOT ghi đè gốc repo (selfcheck sandbox).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="${PREFETCH_WC_ROOT:-$(cd "$ROOT/.." && pwd)}"
TIMEOUT_S="${PREFETCH_TIMEOUT_S:-90}"
TODAY_DMY="$(TZ='Asia/Ho_Chi_Minh' date +%d-%m-%Y)"
CSV="$WC_ROOT/data/execution_logs/dnse_khoplenh_broker_confirm_${TODAY_DMY}.csv"

if [ -s "$CSV" ]; then
  echo "[prefetch_dnse_statement] $TODAY_DMY: đã có statement — bỏ qua."
  exit 0
fi
err="$(cd "$WC_ROOT" && timeout -k 10 "$TIMEOUT_S" python3 fetch_dnse_khoplenh_email.py --date "${TODAY_DMY//-//}" 2>&1 >/dev/null)"
rc=$?
if [ -s "$CSV" ]; then
  echo "[prefetch_dnse_statement] $TODAY_DMY: đã tải statement (rc=$rc)."
elif [ "$rc" = 124 ] || [ "$rc" = 137 ]; then
  echo "❌ prefetch_dnse_statement $TODAY_DMY: fetch quá ${TIMEOUT_S}s (rc=$rc) — chưa có statement."
elif printf '%s' "$err" | grep -q "Không tìm thấy email"; then
  echo "[prefetch_dnse_statement] $TODAY_DMY: chưa có email (chưa về, hoặc phiên khớp 0 — DNSE không gửi)."
else
  # Lỗi KHÁC "không có email" (OAuth hết hạn, import, layout…): in bằng chứng thật, dòng ❌ để cron_health bắt.
  echo "❌ prefetch_dnse_statement $TODAY_DMY: fetch lỗi rc=$rc — chưa có statement. Lỗi thật (cuối):"
  printf '%s\n' "$err" | tail -n 3
fi
exit 0
