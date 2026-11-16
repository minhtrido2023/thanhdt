#!/usr/bin/env bash
# disk_guard_daily.sh — dọn cache TÁI TẠO ĐƯỢC hằng ngày + cảnh báo khi đĩa gần đầy.
# User duyệt 2026-11-16 ("dọn dẹp mỗi ngày, không để rác tích tụ"). Chỉ đụng cache regen được
# (pip/uv/npm/pre-commit-unused); KHÔNG xoá dữ liệu nghiên cứu/snapshot (§8b) — việc đó cần user.
# Đĩa >= DISK_WARN_PCT (mặc định 85) ⇒ gửi cảnh báo kèm top thư mục lớn qua bin/notify.sh.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WARN="${DISK_WARN_PCT:-85}"
before=$(df --output=used -BM / | tail -1 | tr -dc 0-9)
rm -rf "$HOME/.cache/pip" "$HOME/.cache/uv" 2>/dev/null
command -v npm >/dev/null && npm cache clean --force >/dev/null 2>&1
python3 -m pre_commit gc >/dev/null 2>&1
after=$(df --output=used -BM / | tail -1 | tr -dc 0-9)
pct=$(df --output=pcent / | tail -1 | tr -dc 0-9)
echo "$(TZ=Asia/Ho_Chi_Minh date '+%F %H:%M') disk=${pct}% freed=$((before-after))MB"
if [ "$pct" -ge "$WARN" ]; then
  top=$(du -xsh "$HOME/thanhdt/WorkingClaude/mike/agents/Taylor/research" "$HOME/thanhdt/WorkingClaude/data" "$HOME/thanhdt/WorkingClaude/mike/agents/Taylor" /var/log/journal 2>/dev/null | sort -rh | head -4 | tr '\n' ';')
  "$ROOT/bin/notify.sh" "Đĩa / đạt ${pct}% (ngưỡng ${WARN}%). Lớn nhất: ${top} Cần dọn tay (worktree/research/journal)."
fi
