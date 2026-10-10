#!/usr/bin/env bash
# VÒNG 2 — kiểm chứng trên DỮ LIỆU THẬT (chỉ ĐỌC data/ và mike/reports; không gửi gì, không gọi
# eod_trading_report.sh). Mọi output vào research/daily_return_gate_20261010/round2/.
#  (1) sinh thử khối danh mục 2 tài khoản × 02/10 + 09/10 bằng code của nhánh rồi chạy cổng;
#  (2) 11 biến thể của reviewer (+ 3 biến thể trôi MỘT dòng) trên bản sinh thử SpaceX 02/10;
#  (3) 2 bản nháp tuần; (4) báo cáo ngày CŨ đã gửi (hồi quy: dây bẫy F6 không được chặn oan).
set -uo pipefail
W=/home/trido/thanhdt/WorkingClaude/wt-dailyreturn-1010
M=/home/trido/thanhdt/WorkingClaude/mike
R=$M/agents/Taylor/research/daily_return_gate_20261010/round2
T=$R/trial; V=$R/variants; G=$R/regress
mkdir -p "$T" "$V" "$G"
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
cd /home/trido/thanhdt/WorkingClaude
SHARED="$(mktemp -d /tmp/taylor_k1_memo.XXXXXX)"
trap 'rm -rf "$SHARED" /tmp/taylor_k1_memo.*' EXIT

gate() { # nhãn, file, thư mục out, memo
  local t0; t0=$(date +%s)
  DAR_BQ_MEMO_DIR="$4" python3 $W/bin/report_return_gate.py --report "$2" > "$3/$1.txt" 2>&1; local rc=$?
  echo "GATE $1 rc=$rc $(( $(date +%s)-t0 ))s | $(grep -m1 'Đã kiểm' "$3/$1.txt" | cut -c1-105) | $(grep -m1 '^❌ CHẶN\|^✅ PASS' "$3/$1.txt" | cut -c1-40) | $(grep -A1 '^❌ CHẶN' "$3/$1.txt" | sed -n 2p | cut -c1-170)"
}

echo "== (1) sinh thử + cổng"
for D in 2026-10-02 2026-10-09; do
  for A in ZaloPay SpaceX; do
    MEMO="$(mktemp -d /tmp/taylor_k1_memo.XXXXXX)"      # như cron: mỗi lượt tài khoản một sổ nhớ riêng
    F="$T/${A}_daily_report_${D}.md"
    t0=$(date +%s)
    DAR_BQ_MEMO_DIR="$MEMO" python3 $W/bin/portfolio_status.py --account "$A" --date "$D" > "$T/ps_${A}_${D}.out" 2> "$T/ps_${A}_${D}.err"; rc=$?
    t1=$(date +%s)
    { printf '📊 **EOD Trading Report — %s (%s)**\n\n' "$A" "$D"; cat "$T/ps_${A}_${D}.out"; printf '\n(bản SINH THỬ — chỉ khối danh mục; phần lệnh/NAV không đổi trong nhánh này)\n'; } > "$F"
    echo "TRIAL $A $D portfolio_status rc=$rc $((t1-t0))s | mục chi tiết: $(grep -c '^\*\*Chi tiết' "$F") | dòng 'chưa có tỉ suất': $(grep -o '(chưa có tỉ suất)' "$F" | wc -l) | memo files=$(ls "$MEMO" | wc -l)"
    gate "gate_${A}_${D}" "$F" "$T" "$MEMO"
    cp -n "$MEMO"/* "$SHARED"/ 2>/dev/null
    rm -rf "$MEMO"
  done
done

echo "== (2) biến thể trên SpaceX 02/10"
python3 - "$T" "$V" <<'PY'
import re, sys
T, V = sys.argv[1], sys.argv[2]
sx = open(f"{T}/SpaceX_daily_report_2026-10-02.md", encoding="utf-8").read()
zp = open(f"{T}/ZaloPay_daily_report_2026-10-02.md", encoding="utf-8").read()
BIT = re.compile(r"([A-Z][A-Z0-9]{2}) (\d[\d.,]*M), ([+-]\d+\.\d\d)%")
bits = list(BIT.finditer(sx))
neg = next(m for m in bits if m.group(3).startswith("-"))
first = bits[0]
def sub(m, new):                      # thay ĐÚNG một dòng vị thế
    return sx[:m.start()] + new + sx[m.end():]
tk, val, pct = neg.group(1), neg.group(2), neg.group(3)
out = {
 "t01_one_pct_plus0.3": sub(neg, f"{tk} {val}, {float(pct) + 0.3:+.2f}%"),
 "t02_unicode_minus_comma": sub(neg, f"{tk} {val}, " + pct.replace("-", "−").replace(".", ",") + "%"),
 "t03_format_drift_colon_ALL": BIT.sub(lambda m: f"{m.group(1)} {m.group(2)}: {m.group(3)}%", sx),
 "t04_format_drift_trieu_ALL": BIT.sub(lambda m: f"{m.group(1)} {m.group(2)[:-1]} triệu, {m.group(3)}%", sx),
 "t05_format_drift_paren_ALL": BIT.sub(lambda m: f"{m.group(1)} {m.group(2)} ({m.group(3)}%)", sx),
 "t03s_format_drift_colon_ONE": sub(neg, f"{tk} {val}: {pct}%"),
 "t04s_format_drift_trieu_ONE": sub(neg, f"{tk} {val[:-1]} triệu, {pct}%"),
 "t05s_format_drift_paren_ONE": sub(neg, f"{tk} {val} ({pct}%)"),
 "t06_zalopay_block_in_spacex_file": zp.replace("ZaloPay", "SpaceX"),
 "t08_sleeve_total_tampered": re.sub(r"(\| [^|\n]*\(\d+ mã\) \|[^|\n]*\|[^|\n]*\| )([+-]\d+\.\d)%", lambda m: f"{m.group(1)}{float(m.group(2)) + 10:+.1f}%", sx, count=1),
 "t09_bold_pct_wrong": sub(neg, f"{tk} {val}, **{float(pct) + 1.73:+.2f}%**"),
 "t09b_bold_pct_right": sub(neg, f"{tk} {val}, **{pct}%**"),
 "t10_value_B_unit": sub(first, f"{first.group(1)} 0.08B, +9.99%"),
}
dri = next((m for m in bits if m.group(1) == "DRI"), None)
if dri:
    out["t07_dri_costprice_number"] = sub(dri, f"DRI {dri.group(2)}, {float(dri.group(3)) + 2.18:+.2f}%")
flag = re.search(r"🔴 ([A-Z][A-Z0-9]{2}) ([+-]\d+\.\d\d)% \(", sx)
if flag:
    out["t11_flag_line_wrong"] = sx[:flag.start(2)] + f"{float(flag.group(2)) + 4.7:+.2f}" + sx[flag.end(2):]
for name, text in out.items():
    assert text != sx or name.startswith("t06"), name
    open(f"{V}/{name}__SpaceX_daily_report_2026-10-02.md", "w", encoding="utf-8").write(text)
print("VARIANTS", len(out), "| dòng bị sửa:", tk, val, pct, "| cờ:", flag.group(0) if flag else None, "| DRI:", bool(dri))
PY
for F in "$V"/t*__SpaceX_daily_report_2026-10-02.md; do
  n="$(basename "$F" .md)"; gate "${n%%__*}" "$F" "$V" "$SHARED"
done

echo "== (3) 2 bản nháp tuần"
for F in /home/trido/thanhdt/WorkingClaude/wt-1558282936489611354/reports/*_weekly_report_2026-10-05_to_2026-10-09.md; do
  gate "weekly_$(basename "$F" .md)" "$F" "$G" "$SHARED"
done

echo "== (4) báo cáo ngày CŨ đã gửi (hồi quy)"
for D in 2026-10-01 2026-10-02 2026-10-06 2026-10-07 2026-10-08 2026-10-09; do
  for A in SpaceX ZaloPay; do
    F="$M/reports/${A}_daily_report_${D}.md"
    [ -f "$F" ] && gate "old_${A}_${D}" "$F" "$G" "$SHARED"
  done
done
echo ALLDONE
