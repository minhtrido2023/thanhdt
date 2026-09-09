#!/usr/bin/env bash
# backup_freshness_check.sh — kiểm tra ĐỘC LẬP: bản backup trên GitHub có thật sự tươi không.
#
# Vì sao tồn tại (bus question Mike/retro-2026-09-08-backup-silent-failure-recurring-3rd,
# option B — Wags trả lời 2026-09-09): backup GitHub hỏng 3 lần trong 5 tuần (08-01, 08-12,
# 09-08) và CẢ BA lần đều do người đọc tình cờ phát hiện, không có alert nào. Mỗi lần lại vá
# đúng nguyên nhân kỹ thuật của lần đó (path sai → `|| true` nuốt exit → gitlink treo →
# 2026-09-09 lại thêm: "nothing to commit" thoát 0 mà không push commit tồn). Bốn nguyên nhân
# khác nhau, cùng một hậu quả. Script này KHÔNG kiểm tra nguyên nhân — nó kiểm tra KẾT QUẢ
# (ref trên remote), nên bắt được cả nguyên nhân thứ 5 chưa từng gặp.
#
# Hai bất biến, cả hai đều tính trên remote thật (`git ls-remote`, không tin ref local đã cũ):
#   1. HEAD trên remote không được già hơn MAX_AGE_H giờ  → không đêm nào bị bỏ.
#   2. Không được có commit local nào cũ hơn MAX_AGE_H giờ mà chưa push → backup không tụt hậu.
# Quiet-heartbeat: sạch cũng vẫn báo 1 dòng (im lặng hoàn toàn không phân biệt được với chết).
# BACKUP_FRESHNESS_QUIET=1 ⇒ chỉ in ra stdout, không gửi Discord/bus (dùng khi test tay).
set -uo pipefail
ROOT="/home/trido/thanhdt/WorkingClaude/mike"
MAX_AGE_H="${BACKUP_MAX_AGE_H:-30}"     # 24h chu kỳ + 6h nới cho job chạy trễ
NOW="$(date -u +%s)"
PROBLEMS=""
LINES=""

check_repo() {   # <nhãn> <đường dẫn repo> <remote> <branch>
  local label="$1" repo="$2" remote="$3" branch="$4"
  local rsha lsha age_h behind_h
  rsha="$(timeout 60 git -C "$repo" ls-remote "$remote" "$branch" 2>/dev/null | awk 'NR==1{print $1}')"
  if [ -z "$rsha" ]; then
    PROBLEMS="${PROBLEMS}- $label: KHÔNG đọc được remote ($remote/$branch) — PAT hết hạn hoặc mất mạng\n"
    return
  fi
  # Tuổi bản trên remote. Nếu object chưa có local (remote đi trước) thì fetch nông đúng 1 ref.
  if ! git -C "$repo" cat-file -e "$rsha^{commit}" 2>/dev/null; then
    timeout 120 git -C "$repo" fetch -q "$remote" "$branch" 2>/dev/null || true
  fi
  if git -C "$repo" cat-file -e "$rsha^{commit}" 2>/dev/null; then
    age_h=$(( (NOW - $(git -C "$repo" log -1 --format=%ct "$rsha")) / 3600 ))
    if [ "$age_h" -gt "$MAX_AGE_H" ]; then
      PROBLEMS="${PROBLEMS}- $label: bản trên GitHub đã ${age_h}h tuổi (> ${MAX_AGE_H}h) — backup KHÔNG chạy/không lên\n"
    fi
    LINES="${LINES}  $label: remote ${rsha:0:8}, ${age_h}h tuổi\n"
  else
    LINES="${LINES}  $label: remote ${rsha:0:8} (không đọc được tuổi)\n"
  fi
  # Commit local cũ mà chưa push.
  lsha="$(git -C "$repo" rev-parse HEAD 2>/dev/null)" || return
  if [ "$lsha" != "$rsha" ]; then
    if git -C "$repo" merge-base --is-ancestor "$rsha" "$lsha" 2>/dev/null; then
      behind_h=$(( (NOW - $(git -C "$repo" log -1 --format=%ct "$lsha")) / 3600 ))
      if [ "$behind_h" -gt "$MAX_AGE_H" ]; then
        PROBLEMS="${PROBLEMS}- $label: commit local ${lsha:0:8} chưa push, đã ${behind_h}h — remote thiếu $(git -C "$repo" rev-list --count "$rsha..$lsha") commit\n"
      fi
    else
      PROBLEMS="${PROBLEMS}- $label: local ${lsha:0:8} và remote ${rsha:0:8} ĐÃ PHÂN NHÁNH — push sẽ không bao giờ tự khớp lại\n"
    fi
  fi
}

check_repo "workspace chính (thanhdt/main)" "/home/trido/thanhdt" origin main
check_repo "fleet Mike (mike-fleet)"        "$ROOT"               github mike-fleet

DATE="$(date -u +%Y-%m-%d)"
if [ -z "$PROBLEMS" ]; then
  printf '💾 [backup_freshness] %s: backup GitHub TƯƠI.\n%b' "$DATE" "$LINES"
  [ "${BACKUP_FRESHNESS_QUIET:-0}" = 1 ] \
    || "$ROOT/bin/notify.sh" "💾 [backup_freshness] $DATE: backup GitHub tươi, cả 2 nhánh OK." 2>/dev/null || true
  exit 0
fi
MSG="$(printf '🚨 [backup_freshness] %s — BACKUP CÓ VẤN ĐỀ:\n%b\nTrạng thái đọc được:\n%b' "$DATE" "$PROBLEMS" "$LINES")"
printf '%s\n' "$MSG"
if [ "${BACKUP_FRESHNESS_QUIET:-0}" != 1 ]; then
"$ROOT/bin/notify_thread.sh" "$MSG" architecture 2>/dev/null \
  || "$ROOT/bin/notify_thread.sh" "$MSG" trading_daily 2>/dev/null || true
"$ROOT/bin/append_event.sh" Wags error "backup-freshness-$DATE" \
  "$(python3 -c 'import json,sys;print(json.dumps({"summary":sys.stdin.read()}))' <<< "$MSG")" 2>/dev/null || true
fi
exit 1
