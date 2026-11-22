#!/usr/bin/env bash
# lag_require_confirmed_prompt_selfcheck.sh — selfcheck cho khối LAG_ZONE_NOTE + LAG_DD_REQUIRE_CONFIRMED
# (B1, user duyệt D1+D5 22/11/2026) trong bin/bq_freshness_check.sh. Cắt khối THẬT từ file cạnh script
# này (không chép lại), chạy trong sandbox với các biến thể trading_bot/plan.py:
#   False / chưa có hằng ⇒ LAG_ZONE_NOTE giống TỪNG BYTE bản trước B1 (chỉ dòng LAG_ZONE_NOTE= gốc);
#   True ⇒ có câu luật 22/11; mơ hồ (2 dòng, giá trị lạ, thiếu file) ⇒ [WARN] kèm bằng chứng + câu nhắc kiểm tay.
# Mutation: 3 đột biến của khối phải bị bắt. Không phụ thuộc TZ. Chạy: bash bin/lag_require_confirmed_prompt_selfcheck.sh
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REAL="$HERE/bq_freshness_check.sh"
PASS=0; FAIL=0
check() { if [ "$2" = 0 ]; then PASS=$((PASS+1)); echo "  PASS  $1"; else FAIL=$((FAIL+1)); echo "  FAIL  $1  ${3:-}"; fi; }

SB="$(mktemp -d)"; trap 'rm -rf "$SB"' EXIT
# Khối = từ dòng 'LAG_ZONE_NOTE=' tới 'fi' đầu tiên sau '_lagcf_file='.
awk '/^LAG_ZONE_NOTE="/{on=1} on{print} on&&/^_lagcf_file=/{seen=1} on&&seen&&/^fi$/{exit}' "$REAL" > "$SB/block.sh"
grep -m1 '^LAG_ZONE_NOTE="' "$REAL" > "$SB/orig.sh"
check "cắt được khối (có dòng gốc + _lagcf_file + fi)" \
  "$( grep -q '^_lagcf_file=' "$SB/block.sh" && tail -1 "$SB/block.sh" | grep -qx 'fi' && [ -s "$SB/orig.sh" ]; echo $?)"

mkwd() {  # $1 = tên, $2 = nội dung plan.py ("__NOFILE__" ⇒ không tạo file)
  mkdir -p "$SB/$1/trading_bot"
  [ "$2" = "__NOFILE__" ] || printf '%s\n' "$2" > "$SB/$1/trading_bot/plan.py"
}
render() {  # $1 = file khối, $2 = WORKDIR ⇒ in LAG_ZONE_NOTE (stdout) ; log → $SB/log
  WORKDIR="$2" bash -c 'set -uo pipefail; source "$1" >"$3" 2>&1; printf "%s" "$LAG_ZONE_NOTE"' _ "$1" "$2" "$SB/log"
}
mkwd F  $'X = 1\nLAG_DD_REQUIRE_CONFIRMED = False\nY = 2'
mkwd FC $'LAG_DD_REQUIRE_CONFIRMED = False   # tắt'
mkwd T  $'X = 1\nLAG_DD_REQUIRE_CONFIRMED = True\nY = 2'
mkwd N  $'X = 1\nLAG_DD_ZONE_GATE_ENABLED = True'
mkwd D  $'LAG_DD_REQUIRE_CONFIRMED = False\nLAG_DD_REQUIRE_CONFIRMED = True'
mkwd V  $'LAG_DD_REQUIRE_CONFIRMED = 1'
mkwd D3 $'LAG_DD_REQUIRE_CONFIRMED = True  # bật\nLAG_DD_REQUIRE_CONFIRMED = False'   # python lấy dòng SAU ⇒ False
mkwd M  "__NOFILE__"
ORIG="$(WORKDIR=/nonexistent bash -c 'source "$1"; printf "%s" "$LAG_ZONE_NOTE"' _ "$SB/orig.sh")"
SENT="BỔ SUNG LUẬT USER 22/11/2026"
WARN_S="KHÔNG đọc được trạng thái cổng LAG_DD_REQUIRE_CONFIRMED"

NF=0
run_cases() {  # $1 = file khối, $2=verbose ⇒ gọi check; luôn đặt biến toàn cục NF = số ca FAIL (KHÔNG gọi trong \$(...))
  local blk="$1" v="${2:-}" out
  NF=0
  _c() { if [ "$2" = 0 ]; then if [ -n "$v" ]; then check "$1" 0; fi; else NF=$((NF+1)); if [ -n "$v" ]; then check "$1" 1 "${3:-}"; fi; fi; }
  out="$(render "$blk" "$SB/F")";  _c "hằng False ⇒ LAG_ZONE_NOTE giống từng byte bản trước B1" "$([ "$out" = "$ORIG" ]; echo $?)" "len ${#out} vs ${#ORIG}"
  _c "hằng False ⇒ không in WARN" "$([ ! -s "$SB/log" ]; echo $?)" "$(cat "$SB/log")"
  out="$(render "$blk" "$SB/FC")"; _c "hằng False + comment cuối dòng ⇒ giống từng byte" "$([ "$out" = "$ORIG" ]; echo $?)"
  out="$(render "$blk" "$SB/N")";  _c "chưa có hằng (main chưa merge) ⇒ giống từng byte, không WARN" "$([ "$out" = "$ORIG" ] && [ ! -s "$SB/log" ]; echo $?)"
  out="$(render "$blk" "$SB/T")";  _c "hằng True ⇒ có câu luật 22/11 nối SAU bản gốc" "$([ "${out#"$ORIG"}" != "$out" ] && [[ "$out" == *"$SENT"* ]] && [[ "$out" == *"skeptic_final == 'CONFIRMED'"* ]] && [[ "$out" == *"audited_fy_missing"* ]]; echo $?)"
  _c "hằng True ⇒ không có câu nhắc 'không đọc được'" "$([[ "$out" != *"$WARN_S"* ]]; echo $?)"
  for k in D D3 V M; do
    out="$(render "$blk" "$SB/$k")"
    _c "mơ hồ ($k) ⇒ [WARN] có bằng chứng + câu nhắc kiểm tay, KHÔNG có câu bật" \
      "$(grep -q '\[WARN\].*grep rc=' "$SB/log" && [[ "$out" == *"$WARN_S"* ]] && [[ "$out" != *"$SENT"* ]]; echo $?)" "$(cat "$SB/log")"
  done
}

echo "== khối thật =="
run_cases "$SB/block.sh" verbose

echo "== mutation (mỗi đột biến phải làm ≥1 ca FAIL) =="
mut() {  # $1 tên, $2 biểu thức sed
  sed -E "$2" "$SB/block.sh" > "$SB/mut.sh"
  if cmp -s "$SB/mut.sh" "$SB/block.sh"; then check "$1: điểm đột biến tồn tại" 1 "sed không đổi gì"; return; fi
  run_cases "$SB/mut.sh"
  check "$1: KILLED ($NF ca FAIL)" "$([ "$NF" -gt 0 ]; echo $?)"
}
mut "X1 nhánh True không nối câu"      '/BỔ SUNG LUẬT USER 22\/11/s/^  LAG_ZONE_NOTE=.*/  :/'
mut "X2 nhánh False cũng nối câu"      's/^  :   # tắt.*/  LAG_ZONE_NOTE="${LAG_ZONE_NOTE} BỔ SUNG LUẬT USER 22\/11\/2026"/'
mut "X3 bỏ kiểm số dòng khớp"          's/\[ "\$_lagcf_n" -eq 1 \] && //g'

echo; echo "$PASS PASS / $FAIL FAIL"
[ "$FAIL" = 0 ]
