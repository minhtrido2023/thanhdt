#!/usr/bin/env bash
# disk_guard_daily.sh — dọn cache TÁI TẠO ĐƯỢC hằng ngày + cảnh báo khi đĩa gần đầy.
# User duyệt 2026-11-16 ("dọn dẹp mỗi ngày, không để rác tích tụ"). Chỉ đụng cache regen được
# (pip/uv/npm/pre-commit-unused); KHÔNG xoá dữ liệu nghiên cứu/snapshot (§8b) — việc đó cần user.
# Đĩa >= DISK_WARN_PCT (mặc định 85) ⇒ gửi cảnh báo kèm top thư mục lớn qua bin/notify.sh.
# --watch (thêm 2026-11-24, user duyệt sau sự cố đĩa 100%): CHỈ đo + cảnh báo, không dọn cache.
# Chạy mỗi 30' (cron). Mức 85/90/95%. Báo khi LÊN mức mới hoặc nhắc lại sau 6h (≥95%: 1h) +
# 1 tin khi hạ về <85%. Kèm danh sách worktree ĐÃ MERGE + SẠCH (ứng viên gỡ, chỉ liệt kê, KHÔNG xoá).
# Lý do: 24/11 03:20 báo 87% đúng 1 lần/ngày, 10h sau đĩa 100% (20 worktree × 2,6–4GB).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WARN="${DISK_WARN_PCT:-85}"
if [ "${1:-}" = "--watch" ]; then
  STATE="${DISK_WATCH_STATE:-$ROOT/state/disk_watch.state}"; mkdir -p "$(dirname "$STATE")"
  pct="${DISK_WATCH_FAKE_PCT:-$(df --output=pcent / | tail -1 | tr -dc 0-9)}"
  lvl=0; [ "$pct" -ge "$WARN" ] && lvl=1; [ "$pct" -ge 90 ] && lvl=2; [ "$pct" -ge 95 ] && lvl=3
  plvl=0; pts=0; [ -f "$STATE" ] && read -r plvl pts < "$STATE"
  now=$(date +%s); gap=21600; [ "$lvl" -ge 3 ] && gap=3600
  if [ "$lvl" -eq 0 ]; then
    [ "${plvl:-0}" -gt 0 ] && "$ROOT/bin/notify.sh" "✅ Đĩa / đã hạ về ${pct}% (<${WARN}%)."
    echo "0 0" > "$STATE"; exit 0
  fi
  if [ "$lvl" -gt "${plvl:-0}" ] || [ $((now - ${pts:-0})) -ge "$gap" ]; then
    free=$(df -BG --output=avail / | tail -1 | tr -dc 0-9)
    cand=""
    for r in "$ROOT:master" "$(dirname "$(dirname "$ROOT")"):main"; do
      repo="${r%:*}"; base="${r##*:}"
      while IFS=$'\t' read -r wp wb; do
        [ -d "$wp" ] && [ "$wp" != "$repo" ] || continue
        git -C "$repo" merge-base --is-ancestor "$wb" "$base" 2>/dev/null || continue
        [ -z "$(git -C "$wp" status --porcelain 2>/dev/null)" ] || continue
        cand="$cand$(du -sm "$wp" 2>/dev/null | cut -f1)MB $(basename "$wp"); "
      done < <(git -C "$repo" worktree list --porcelain 2>/dev/null | awk '/^worktree /{p=$2} /^branch /{b=$2; sub("refs/heads/","",b); print p"\t"b}')
    done
    [ -n "$cand" ] || cand="(không có)"
    icon="⚠️"; [ "$lvl" -ge 2 ] && icon="🔴"
    "$ROOT/bin/notify.sh" "$icon Đĩa / ${pct}% (còn ${free}GB; mức ${WARN}/90/95). Worktree ĐÃ MERGE+SẠCH có thể gỡ (nhờ Mike gỡ, luật user 24/11: merged+sạch+0 process, không --force): ${cand} Cần user quyết: research/snapshot/bq_cache."
    echo "$lvl $now" > "$STATE"
  fi
  exit 0
fi
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
