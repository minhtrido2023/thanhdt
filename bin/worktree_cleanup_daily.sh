#!/usr/bin/env bash
# worktree_cleanup_daily.sh — dọn worktree/branch session đã merge vào master.
#
# User duyệt 2026-08-18: "Đồng ý dọn worktree và branch. Đưa thành 1 task routine tự
# động chạy hàng ngày cho tôi." Cron đăng ký 03:00 ICT; script này mặc định DRY-RUN,
# chỉ `--apply` mới thực hiện xoá (cron luôn truyền --apply).
#
# Nguyên tắc an toàn (bắt buộc, đừng nới lỏng mà chưa có review):
# 1. DRY-RUN là mặc định. Không có --apply thì không xoá gì.
# 2. Chỉ xoá worktree SẠCH (git status rỗng) và branch có tip là ANCESTOR của master.
#    Không dùng --force, không xoá worktree dirty/unmerged.
# 3. Bỏ qua worktree/branch thuộc session/claim CCDB đang hiện diện (active_ids/active_dirs)
#    để không phá môi trường làm việc của phiên Claude đang chạy.
# 4. Remote branch chỉ ĐƯỢC báo cáo, không xoá mặc định — xoá remote cần quyết định riêng.
set -uo pipefail

DEFAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$DEFAULT_ROOT"
APPLY=0
MASTER_BRANCH="master"
CCDB_URL="${CCDB_API_URL:-http://127.0.0.1:8199}"
LOCK="$ROOT/state/locks/worktree_cleanup.lock"
LOG="$ROOT/logs/worktree_cleanup.log"

usage() {
  cat <<EOF
worktree_cleanup_daily.sh [--apply] [--root=PATH] [--help]

  (không cờ)   DRY-RUN: chỉ in những gì sẽ dọn. MẶC ĐỊNH.
  --apply      Thực thi thật: xoá worktree sạch + branch đã merge.
  --root=PATH  Thay thư mục repo để chạy thử trên production root.
EOF
}

for a in "$@"; do
  case "$a" in
    --apply) APPLY=1 ;;
    --root=*) ROOT="${a#--root=}" ;;
    -h|--help) usage; exit 0 ;;
    *) echo "cờ không hiểu: $a" >&2; usage; exit 2 ;;
  esac
done

ROOT="$(cd "$ROOT" && pwd)"
LOCK="$ROOT/state/locks/worktree_cleanup.lock"
LOG="$ROOT/logs/worktree_cleanup.log"

mkdir -p "$ROOT/state/locks" "$ROOT/logs"
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "worktree_cleanup_daily: lock $LOCK đang được giữ — bỏ qua lượt này" >&2
  exit 0
fi

say() {
  printf '%s\n' "$*"
  # Crontab redirects stdout+stderr tới $LOG; KHÔNG ghi nội bộ nữa để khỏi trùng dòng.
  return 0
}

N_REMOVED=0
N_KEPT_UNMERGED=0
N_KEPT_DIRTY=0
N_KEPT_ACTIVE=0
N_BRANCH_DELETED=0

say "=== worktree_cleanup_daily $( [ "$APPLY" = 1 ] && echo APPLY || echo 'DRY-RUN (mặc định)' ) $(date -u +%FT%TZ) ==="
say "repo: $ROOT | master: $MASTER_BRANCH | ccdb: $CCDB_URL"

# ── Lấy danh sách session/claim CCDB để chặn worktree thuộc phiên/kênh đã biết ──
active_ids=()
active_dirs=()
ccdb_ok=0
active_csv="$(python3 - "$CCDB_URL" <<'PY' 2>/dev/null || true
import json, sys, urllib.request

base = sys.argv[1]

def load(path):
    req = urllib.request.Request(base + path, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.load(r)

try:
    sessions = load("/api/sessions?exclude_thread=0")
    for s in sessions.get("sessions", []):
        if s.get("thread_id"):
            print("id:" + str(s["thread_id"]))
        if s.get("working_dir"):
            print("dir:" + s["working_dir"])
    claims = load("/api/claims")
    for c in claims.get("claims", []):
        if c.get("thread_id"):
            print("id:" + str(c["thread_id"]))
except Exception:
    sys.exit(0)
PY
)"

if [ -n "$active_csv" ]; then
  ccdb_ok=1
  while IFS= read -r line; do
    case "$line" in
      id:*) active_ids+=("${line#id:}") ;;
      dir:*) active_dirs+=("${line#dir:}") ;;
    esac
  done <<< "$active_csv"
  say "CCDB đang hiện diện: ${#active_ids[@]} thread / ${#active_dirs[@]} working_dir"
else
  say "WARNING: không đọc được CCDB ($CCDB_URL) — fail-closed, sẽ không xoá gì ở chế độ --apply"
fi

is_active() {
  local wt="$1" branch="$2" id dir
  for id in "${active_ids[@]}"; do
    case "$branch" in
      "session/$id"|"session/$id-"*) return 0 ;;
    esac
    case "$wt" in
      *"$id"*) return 0 ;;
    esac
  done
  for dir in "${active_dirs[@]}"; do
    [ "$dir" = "$wt" ] && return 0
    case "$dir" in
      "$wt"/*) return 0 ;;
    esac
  done
  return 1
}

# ── Duyệt worktree: chặn active/dirty/unmerged, còn lại thì remove + branch -d ──
declare -A wt_branch_by_path
current_wt=""
while IFS= read -r line; do
  case "$line" in
    "worktree "*) current_wt="${line#worktree }"; wt_branch_by_path["$current_wt"]="" ;;
    "branch refs/heads/"*) wt_branch_by_path["$current_wt"]="${line#branch refs/heads/}" ;;
    "detached"*) wt_branch_by_path["$current_wt"]="__detached__" ;;
  esac
done < <(git -C "$ROOT" worktree list --porcelain)

for wt in "${!wt_branch_by_path[@]}"; do
  branch="${wt_branch_by_path[$wt]}"
  [ "$wt" = "$ROOT" ] && continue
  if [ -z "$branch" ] || [ "$branch" = "__detached__" ]; then
    say "KEEP detached worktree (không theo branch để xoá an toàn): $wt"
    continue
  fi
  if is_active "$wt" "$branch"; then
    say "KEEP active (CCDB): $wt [$branch]"
    N_KEPT_ACTIVE=$((N_KEPT_ACTIVE+1))
    continue
  fi
  if ! git -C "$ROOT" merge-base --is-ancestor "$branch" "$MASTER_BRANCH" 2>/dev/null; then
    say "KEEP unmerged: $wt [$branch]"
    N_KEPT_UNMERGED=$((N_KEPT_UNMERGED+1))
    continue
  fi
  if [ -n "$(git -C "$wt" status --porcelain --untracked-files=normal 2>/dev/null || true)" ]; then
    say "KEEP dirty: $wt [$branch]"
    N_KEPT_DIRTY=$((N_KEPT_DIRTY+1))
    continue
  fi

  if [ "$APPLY" = "1" ]; then
    if git -C "$ROOT" worktree remove "$wt" 2>>"$LOG"; then
      say "REMOVED worktree: $wt [$branch]"
      N_REMOVED=$((N_REMOVED+1))
      if git -C "$ROOT" branch -d "$branch" >>"$LOG" 2>&1; then
        say "DELETED branch: $branch"
        N_BRANCH_DELETED=$((N_BRANCH_DELETED+1))
      else
        say "WARN branch $branch không tự xoá được (xem log)"
      fi
    else
      say "WARN worktree remove thất bại: $wt [$branch] (xem log)"
    fi
  else
    say "[dry] REMOVE worktree + DELETE branch: $wt [$branch]"
    N_REMOVED=$((N_REMOVED+1))
  fi
done

# ── Branch session không còn worktree: chỉ xoá local, merged, không active ──
while IFS= read -r branch; do
  [ -n "$branch" ] || continue
  case "$branch" in session/*) ;; *) continue ;; esac

  # Nếu branch vẫn đang được 1 worktree còn lại dùng thì để nhánh worktree xử lý.
  still_checked_out=0
  for wt in "${!wt_branch_by_path[@]}"; do
    if [ "${wt_branch_by_path[$wt]}" = "$branch" ]; then
      still_checked_out=1
      break
    fi
  done
  [ "$still_checked_out" = "1" ] && continue

  if is_active "no-worktree" "$branch"; then
    say "KEEP active branch: $branch"
    N_KEPT_ACTIVE=$((N_KEPT_ACTIVE+1))
    continue
  fi
  if ! git -C "$ROOT" merge-base --is-ancestor "$branch" "$MASTER_BRANCH" 2>/dev/null; then
    say "KEEP unmerged branch: $branch"
    N_KEPT_UNMERGED=$((N_KEPT_UNMERGED+1))
    continue
  fi

  if [ "$APPLY" = "1" ]; then
    if git -C "$ROOT" branch -d "$branch" >>"$LOG" 2>&1; then
      say "DELETED orphan branch: $branch"
      N_BRANCH_DELETED=$((N_BRANCH_DELETED+1))
    else
      say "WARN orphan branch $branch không tự xoá được (xem log)"
    fi
  else
    say "[dry] DELETE orphan branch: $branch"
    N_BRANCH_DELETED=$((N_BRANCH_DELETED+1))
  fi
done < <(git -C "$ROOT" for-each-ref --format='%(refname:short)' 'refs/heads/session/*')

# ── Báo remote stale, không xoá ────────────────────────────────────────────────
say "--- Remote session branches (chỉ báo cáo, không xoá mặc định) ---"
while IFS= read -r ref; do
  say "remote session branch (not deleted): $ref"
done < <(git -C "$ROOT" for-each-ref --format='%(refname:short)' 'refs/remotes/github/session/*')

say "--- Kết quả: removed_worktrees=$N_REMOVED deleted_branches=$N_BRANCH_DELETED kept_active=$N_KEPT_ACTIVE kept_unmerged=$N_KEPT_UNMERGED kept_dirty=$N_KEPT_DIRTY ccdb_ok=$ccdb_ok ---"
