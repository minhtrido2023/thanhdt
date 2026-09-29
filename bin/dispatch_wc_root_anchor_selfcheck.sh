#!/usr/bin/env bash
# dispatch_wc_root_anchor_selfcheck.sh — khối neo WC_ROOT theo marker wc_env.sh của bin/dispatch.sh.
#
# Bug gốc (sự cố 2026-09-12 + code-quality 2026-09-13, vá ở 136a90d0): bản sao dispatch.sh trong
# worktree mike/agents/wt-*/bin/ đếm cấp "$ROOT/.." = mike/agents — gốc SAI ⇒ không source được
# wc_env.sh, preflight_bq_cache.py luôn fail. arch-reviewer 2026-09-17 (job Wags_20260917_152645):
# vá chỉ được kiểm bằng tay 1 lần ⇒ selfcheck bền này.
#
# CÁCH KIỂM: trích NGUYÊN khối từ dispatch.sh thật (không chép tay) rồi chạy với ROOT giả trong
# thư mục tạm — không side-effect, không chạy dispatch. Có ca MUTATION (khối chỉ đếm cấp) để chứng
# minh selfcheck đỏ được khi vá bị revert.
set -uo pipefail
ROOT_REAL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
D="$ROOT_REAL/bin/dispatch.sh"
TMPD="$(mktemp -d)"; trap 'rm -rf "$TMPD"' EXIT
pass=0; fail=0
ok()  { echo "  PASS $1"; pass=$((pass+1)); }
bad() { echo "  FAIL $1"; fail=$((fail+1)); }

# Khối = từ dòng gán WC_ROOT đếm cấp tới `fi` đầu tiên ở cột 0 sau nó.
BLOCK="$(awk '/^WC_ROOT="\$\(cd "\$ROOT\/\.\." && pwd\)"$/{on=1} on{print} on&&/^fi$/{exit}' "$D")"
if [ -z "$BLOCK" ] || ! grep -q '_wc_probe' <<<"$BLOCK"; then
  bad "không trích được khối neo WC_ROOT từ dispatch.sh (đổi cấu trúc? cập nhật awk)"
  echo "KẾT QUẢ: $pass PASS / $fail FAIL"; exit 1
fi
echo "$BLOCK" > "$TMPD/block.sh"
# Mutation: khối cũ tiền-vá, chỉ đếm cấp.
echo 'WC_ROOT="$(cd "$ROOT/.." && pwd)"' > "$TMPD/mutant.sh"

resolve() {  # $1=file khối, $2=ROOT giả → in WC_ROOT
  ROOT="$2" bash -c 'set -euo pipefail; source "$1"; printf %s "$WC_ROOT"' _ "$1"
}

# Cây giả có marker: $TMPD/WC/wc_env.sh, mike/, mike/agents/wt-x/
WC="$TMPD/WC"; mkdir -p "$WC/mike/agents/wt-x/bin"; : > "$WC/wc_env.sh"
# Cây giả KHÔNG marker (tmp không nằm dưới cây nào có wc_env.sh — kiểm trước)
NM="$TMPD/NM"; mkdir -p "$NM/mike/agents/wt-x/bin"
_p="$TMPD"; _has=0; while [ "$_p" != "/" ]; do [ -f "$_p/wc_env.sh" ] && _has=1; _p="$(dirname "$_p")"; done
[ -f /wc_env.sh ] && _has=1

echo "A. Khối thật"
r="$(resolve "$TMPD/block.sh" "$WC/mike")";           [ "$r" = "$WC" ] && ok "A1 cây chính ⇒ WC" || bad "A1 cây chính ⇒ '$r' (muốn $WC)"
r="$(resolve "$TMPD/block.sh" "$WC/mike/agents/wt-x")"; [ "$r" = "$WC" ] && ok "A2 worktree ⇒ WC (đi lên theo marker)" || bad "A2 worktree ⇒ '$r' (muốn $WC)"
if [ "$_has" = 0 ]; then
  r="$(resolve "$TMPD/block.sh" "$NM/mike/agents/wt-x")"; [ "$r" = "$NM/mike/agents" ] && ok "A3 không marker ⇒ giữ \$ROOT/.." || bad "A3 không marker ⇒ '$r' (muốn $NM/mike/agents)"
else
  bad "A3 không chạy được: có wc_env.sh ở tổ tiên của $TMPD"
fi
r="$(resolve "$TMPD/block.sh" "$ROOT_REAL")"; [ -f "$r/wc_env.sh" ] && [ -f "$r/preflight_bq_cache.py" ] && ok "A4 repo thật ⇒ $r có wc_env.sh + preflight_bq_cache.py" || bad "A4 repo thật ⇒ '$r' thiếu marker/preflight"

echo "B. Mutation (khối tiền-vá chỉ đếm cấp) phải làm A2 đỏ"
r="$(resolve "$TMPD/mutant.sh" "$WC/mike/agents/wt-x")"; [ "$r" != "$WC" ] && ok "B1 mutant worktree ⇒ '$r' ≠ WC (selfcheck bắt được revert)" || bad "B1 mutant cũng ra WC — A2 không phân biệt được"

echo "C. Nơi dùng phải qua \$WC_ROOT, không \"\$ROOT/..\""
grep -qE '^\[ -f "\$WC_ROOT/wc_env\.sh" \] && source "\$WC_ROOT/wc_env\.sh"' "$D" && ok "C1 source wc_env.sh qua \$WC_ROOT" || bad "C1 dòng source wc_env.sh không dùng \$WC_ROOT"
grep -qE 'python3 "\$WC_ROOT/preflight_bq_cache\.py"' "$D" && ok "C2 preflight_bq_cache.py qua \$WC_ROOT" || bad "C2 preflight_bq_cache.py không dùng \$WC_ROOT"
n="$(grep -nE '"\$ROOT/\.\."' "$D" | grep -vE '^[0-9]+:\s*#' | grep -vc 'WC_ROOT="\$(cd "\$ROOT/\.\." && pwd)"')"
[ "$n" = 0 ] && ok "C3 không còn \"\$ROOT/..\" ngoài dòng khởi tạo WC_ROOT" || bad "C3 còn $n chỗ dùng \"\$ROOT/..\" trực tiếp"

echo "KẾT QUẢ: $pass PASS / $fail FAIL"
[ "$fail" = 0 ]
