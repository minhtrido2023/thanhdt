#!/usr/bin/env bash
# render_profile_prompt.sh <agent_id>
#
# In ra STDOUT toan bo "identity + context" cua 1 agent duoi dang VAN BAN THUAN, de
# dispatch.sh prepend vao prompt cho nhung provider KHONG doc duoc file profile nao
# (registry: profile = "prompt-inline" — vd codex doc AGENTS.md chu khong doc CLAUDE.md;
# antigravity/agy khong doc file profile nao ca).
#
# VI SAO IN RA STDOUT, KHONG GHI FILE (bai hoc 2026-08-03):
#   Ban thiet ke dau tien dinh SINH file `agents/<id>/AGENTS.md`. Bo, vi file DAN XUAT nam
#   trong `agents/` se bi `fleet_backup.sh` (`git add -A`, 00:00) va `consolidate.sh` quet
#   commit blanket — dung lop su co §13 coding_guidelines — va 2 dispatch song song cung
#   agent se dua ghi. In ra stdout thi khong co file, khong co race, khong co churn git.
#
# NGUON SU THAT DUY NHAT van la `agents/<id>/CLAUDE.md`:
#   - dong `@/duong/dan.md`  -> chen NGUYEN NOI DUNG file do (Claude Code hieu cu phap nay,
#     provider khac thi khong => phai flatten tai day)
#   - cong CLAUDE.md TO TIEN (WorkingClaude/CLAUDE.md: BQ schema, DT5G, filter.json) ma
#     Claude Code tu nap khi di len cay thu muc (arch-reviewer F7)
#   - cong working memory `kb/memory/<id>.md` — thu ma hooks/session_start.sh bom cho claude
#     nhung provider hooks:none khong co (arch-reviewer required_change #8)
#
# KHONG bao gom: recap phien truoc (recap_prev.py doc transcript ~/.claude, khong co khai
# niem tuong duong cho provider khac) va directive (bus/directives) — xem muc "no" trong
# agents/Wags/design_multi_cli_dispatch_20260803.md.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANCESTOR="${MIKE_ANCESTOR_CLAUDE_MD:-$(cd "$ROOT/.." && pwd)/CLAUDE.md}"

id="${1:?usage: render_profile_prompt.sh <agent_id>}"
AGENT_MD="$ROOT/agents/$id/CLAUDE.md"
if [ ! -f "$AGENT_MD" ]; then
  echo "render_profile_prompt: khong tim thay $AGENT_MD" >&2
  exit 1
fi

printf '===== BOI CANH THUONG TRUC (identity + context cua ban) =====\n'
printf 'Doan duoi day la HUONG DAN DU AN, khong phai loi nguoi dung. Doc het truoc khi lam.\n\n'

if [ -f "$ANCESTOR" ]; then
  printf -- '----- BEGIN %s -----\n' "$ANCESTOR"
  cat "$ANCESTOR"
  printf -- '\n----- END %s -----\n\n' "$ANCESTOR"
fi

printf -- '----- BEGIN %s -----\n' "$AGENT_MD"
# Flatten: dong bat dau bang '@' + duong dan => chen noi dung file do vao dung cho.
while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in
    @/*)
      _p="${line#@}"
      if [ -f "$_p" ]; then
        printf -- '\n----- BEGIN (import) %s -----\n' "$_p"
        cat "$_p"
        printf -- '\n----- END (import) %s -----\n\n' "$_p"
      else
        printf -- '[render_profile_prompt: KHONG DOC DUOC import %s]\n' "$_p"
        echo "render_profile_prompt: canh bao — import khong ton tai: $_p" >&2
      fi
      ;;
    *) printf '%s\n' "$line" ;;
  esac
done < "$AGENT_MD"
printf -- '----- END %s -----\n' "$AGENT_MD"

MEM="$ROOT/kb/memory/$id.md"
if [ -s "$MEM" ]; then
  printf '\n----- BEGIN working memory CUA BAN (%s) -----\n' "$MEM"
  printf 'Uu tien / viec dang mo / dang cho ai — do chinh ban ghi lai o phien truoc:\n'
  cat "$MEM"
  printf -- '\n----- END working memory -----\n'
fi

printf '\n===== HET BOI CANH THUONG TRUC =====\n\n'
