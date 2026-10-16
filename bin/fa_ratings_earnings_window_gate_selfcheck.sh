#!/usr/bin/env bash
# fa_ratings_earnings_window_gate_selfcheck.sh — bộ test GATE của
# fa_ratings_earnings_window_daily.sh (chỉ gọi `--check YYYY-MM-DD`; KHÔNG chạy refresh nào,
# không chạm BQ, không ghi file).
#
# Cửa sổ đang kiểm (nới cả hai đầu 2026-10-13, user duyệt, job Taylor_20261013_125149):
#   ĐẦU  = tháng {1,4,7,10} ∧ ngày ≥ 10      ĐUÔI = tháng {2,5,8,11} ∧ ngày ≤ 10
#   trừ lễ VN (vn_market.is_holiday), KỂ CẢ cuối tuần.
#
# Dùng:  bin/fa_ratings_earnings_window_gate_selfcheck.sh
#        GATE_SCRIPT=/đường/dẫn/bản-đột-biến.sh bin/fa_ratings_earnings_window_gate_selfcheck.sh
# Exit 0 = mọi ca PASS; 1 = có ca FAIL (in từng ca lệch).
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE_SCRIPT="${GATE_SCRIPT:-$HERE/fa_ratings_earnings_window_daily.sh}"

# "ngày|kỳ vọng|từ khoá phải có trong lý do SKIP (rỗng = không kiểm)|ghi chú"
CASES=(
  # ── biên ĐẦU (ngày 10 tháng đầu quý) ──
  "2026-10-09|SKIP|day=9|sát trước biên đầu"
  "2026-10-10|RUN||đúng biên đầu (cũ: SKIP vì <15)"
  "2026-10-14|RUN||trong đoạn mới nới 10..14"
  "2026-10-15|RUN||biên cũ, vẫn RUN"
  "2026-10-31|RUN||cuối tháng đầu quý"
  "2026-01-09|SKIP|day=9|tháng 1 sát trước biên"
  "2026-01-10|RUN||tháng 1 đúng biên"
  "2026-01-31|RUN||cuối tháng 1"
  "2026-04-09|SKIP|day=9|tháng 4 sát trước biên"
  "2026-04-10|RUN||tháng 4 đúng biên"
  "2026-04-29|RUN||trước lễ 30/04"
  "2026-07-09|SKIP|day=9|tháng 7 sát trước biên"
  "2026-07-10|RUN||tháng 7 đúng biên"
  "2026-07-31|RUN||cuối tháng 7"
  # ── biên ĐUÔI (ngày 10 tháng thứ hai quý) ──
  "2026-11-01|RUN||liền mạch 31/10 → 01/11"
  "2026-11-05|RUN||ngày rebalance custom30V"
  "2026-11-10|RUN||đúng biên đuôi"
  "2026-11-11|SKIP|day=11|sát sau biên đuôi"
  "2026-11-30|SKIP|day=30|cuối tháng 11"
  "2026-02-01|RUN||liền mạch 31/01 → 01/02"
  "2026-02-10|RUN||tháng 2 đúng biên đuôi"
  "2026-02-11|SKIP|day=11|tháng 2 sát sau biên"
  "2026-02-28|SKIP|day=28|cuối tháng 2"
  "2028-02-29|SKIP|day=29|năm nhuận"
  "2026-05-02|RUN||sau lễ 01/05"
  "2026-05-10|RUN||tháng 5 đúng biên đuôi"
  "2026-05-11|SKIP|day=11|tháng 5 sát sau biên"
  "2026-08-01|RUN||liền mạch 31/07 → 01/08"
  "2026-08-10|RUN||tháng 8 đúng biên đuôi (ca TVN 08-05 nằm trong)"
  "2026-08-11|SKIP|day=11|tháng 8 sát sau biên"
  # ── tháng KHÔNG thuộc nhóm (3,6,9,12) — kể cả ngày 10 và ngày nằm trong cả hai nhánh ──
  "2026-03-05|SKIP|month=3|tháng 3 ngày ≤10"
  "2026-03-10|SKIP|month=3|tháng 3 ngày 10"
  "2026-03-20|SKIP|month=3|tháng 3 ngày ≥10"
  "2026-06-10|SKIP|month=6|tháng 6"
  "2026-06-30|SKIP|month=6|tháng 6 cuối"
  "2026-09-10|SKIP|month=9|tháng 9"
  "2026-12-10|SKIP|month=12|tháng 12"
  "2026-12-31|SKIP|month=12|tháng 12 cuối"
  # ── lễ VN (fixed-list) ──
  "2026-01-01|SKIP|le VN|01/01 (cũng <10)"
  "2026-04-30|SKIP|le VN|30/04 trong nhánh đầu"
  "2026-05-01|SKIP|le VN|01/05 trong nhánh đuôi"
  "2026-09-02|SKIP|le VN|02/09 (cũng ngoài tháng)"
  # ── cuối tuần vẫn RUN ──
  "2026-10-17|RUN||Thứ Bảy"
  "2026-10-18|RUN||Chủ Nhật"
  "2026-11-07|RUN||Thứ Bảy nhánh đuôi"
  "2026-11-08|RUN||Chủ Nhật nhánh đuôi"
)

fail=0; n=0
_one() {  # $1=nhãn môi trường; phần còn lại = tiền tố lệnh (env ...)
  local label="$1"; shift
  local c d want kw note got
  for c in "${CASES[@]}"; do
    IFS='|' read -r d want kw note <<<"$c"
    got="$("$@" "$GATE_SCRIPT" --check "$d" 2>&1)"
    n=$((n + 1))
    if [ "$want" = "RUN" ]; then
      [ "$got" = "RUN" ] || { echo "FAIL [$label] $d ($note): muon RUN, nhan '$got'"; fail=$((fail + 1)); }
    else
      case "$got" in
        "SKIP: "*) ;;
        *) echo "FAIL [$label] $d ($note): muon SKIP, nhan '$got'"; fail=$((fail + 1)); continue ;;
      esac
      if [ -n "$kw" ] && [[ "$got" != *"$kw"* ]]; then
        echo "FAIL [$label] $d ($note): ly do SKIP thieu '$kw' — nhan '$got'"; fail=$((fail + 1))
      fi
    fi
  done
}

# §16: kết quả không được phụ thuộc TZ của tiến trình gọi.
_one "TZ-unset" env -u TZ
_one "TZ=America/Los_Angeles" env TZ=America/Los_Angeles
_one "TZ=Pacific/Kiritimati" env TZ=Pacific/Kiritimati

# Nhánh KHÔNG tham số (= hôm nay ICT) phải trùng nhánh có tham số với ngày ICT, ở mọi TZ.
TODAY_ICT="$(TZ='Asia/Ho_Chi_Minh' date +%F)"
want_today="$("$GATE_SCRIPT" --check "$TODAY_ICT" 2>&1)"
for tz in "" "America/Los_Angeles" "Pacific/Kiritimati"; do
  if [ -z "$tz" ]; then got="$(env -u TZ "$GATE_SCRIPT" --check 2>&1)"; else got="$(env TZ="$tz" "$GATE_SCRIPT" --check 2>&1)"; fi
  n=$((n + 1))
  [ "$got" = "$want_today" ] || { echo "FAIL [today TZ='${tz:-unset}'] muon '$want_today', nhan '$got'"; fail=$((fail + 1)); }
done

# Chốt tĩnh: nhánh "hôm nay" phải lấy ngày qua today_ict() — phép so ở trên KHÔNG bắt được việc đổi
# sang date.today() vào những ngày mà hôm nay và ngày kề có cùng kết quả gate (đo 2026-10-13).
n=$((n + 1))
if grep -qE 'date\.today\(\)|datetime\.now\(\)' "$GATE_SCRIPT" || ! grep -q 'else today_ict()' "$GATE_SCRIPT"; then
  echo "FAIL [static] nhanh hom-nay khong con neo today_ict()"; fail=$((fail + 1))
fi

echo "fa_ratings_earnings_window gate selfcheck: $((n - fail))/$n PASS (${#CASES[@]} ca x 3 TZ + 3 ca hom-nay + 1 chot tinh; script=$GATE_SCRIPT)"
[ "$fail" -eq 0 ]
