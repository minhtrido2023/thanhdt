#!/usr/bin/env bash
# check_report_cadence.sh — kiểm tra + TỰ SỬA báo cáo tuần/tháng quá hạn.
#
# Thay thế mục §7 cũ trong ops_health_check.sh (đã bug thật 2026-08-01, xem
# kb/incidents/2026-08/2026-08-01-weekly-monthly-report-dead.md): WARN cũ chỉ IN RA 1 dòng,
# CHÔN trong message ops_health_check chạy 4 lần/ngày (2 khung giờ x 2 account) — không có
# forcing function nào khiến ai đó thực sự hành động. Kết quả: WARN "tuần 2026-07-20→2026-07-24
# quá hạn" lặp lại 4 lần/ngày suốt từ 2026-07-27 đến 2026-08-01 (5 ngày, ~20 lần) mà KHÔNG có
# báo cáo nào được soạn — báo cáo tháng 07 cũng chưa từng được soạn dù tháng đã đóng.
#
# Cơ chế mới (cron 1 lần/ngày, KHÔNG lặp theo account):
#   1. Overdue → dispatch Taylor --bg TỰ SOẠN + TỰ GỬI báo cáo (đúng pipeline §6
#      coding_guidelines.md: verify_account_snapshot.py --account-no, nav_history CSV thật).
#   2. ĐỒNG THỜI post escalation rõ ràng vào Trading report topic (KHÔNG chôn ở Trading Daily)
#      + bus event `question` — người có thể thấy NGAY, không cần đợi Mike đọc log.
#   3. Idempotency: mỗi (period, ngày) chỉ dispatch 1 lần — state/report_cadence_dispatched.json.
#      Nếu qua ngày mà báo cáo vẫn chưa xuất hiện (dispatch trước thất bại âm thầm) → tự dispatch
#      lại ngày sau (retry tự nhiên, không cần người nhắc).
#   4. Email (thêm 2026-08-01, user yêu cầu): mỗi lần chạy, quét MỌI file weekly/monthly report
#      đã có trên đĩa (không riêng report vừa được dispatch trong lần chạy này) và gửi qua
#      send_report_email.py bất kỳ file nào chưa từng gửi (state/report_emailed.json) — tự
#      chữa lành nếu Taylor quên gọi bước gửi email trong prompt (cùng bài học attempt-1-crash
#      của check_report_cadence chính nó: đừng chỉ tin 1 agent nhớ làm đủ bước, có lớp quét lại).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
TRADING_REPORT_THREAD="trading_report"
STATE="$ROOT/state/report_cadence_dispatched.json"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"

mkdir -p "$ROOT/state"
[ -f "$STATE" ] || echo '{}' > "$STATE"

EMAILED_STATE="$ROOT/state/report_emailed.json"
[ -f "$EMAILED_STATE" ] || echo '{}' > "$EMAILED_STATE"

# --- Catch-up email sweep: gửi MỌI report chưa từng gửi qua email, bất kể vừa tạo lần này
#     hay đã có từ trước (backfill). Idempotent qua $EMAILED_STATE, không phụ thuộc Taylor
#     có nhớ gọi bước gửi email trong prompt của lần dispatch hay không.
for f in "$ROOT"/reports/*_weekly_report_*.md "$ROOT"/reports/*_monthly_report_*.md; do
  [ -e "$f" ] || continue
  FNAME="$(basename "$f")"
  ALREADY="$(python3 -c "
import json
state = json.load(open('$EMAILED_STATE'))
print('yes' if state.get('$FNAME') else 'no')
")"
  if [ "$ALREADY" = "no" ]; then
    if python3 "$ROOT/bin/send_report_email.py" "$f"; then
      python3 -c "
import json
state = json.load(open('$EMAILED_STATE'))
state['$FNAME'] = '$TODAY'
json.dump(state, open('$EMAILED_STATE', 'w'), indent=2, ensure_ascii=False)
"
    else
      echo "check_report_cadence: gửi email THẤT BẠI cho $FNAME (xem stderr ở trên) — sẽ tự thử lại lần chạy cron sau." >&2
    fi
  fi
done

PLAN="$(python3 - "$WC_ROOT" "$TODAY" "$STATE" << 'PYEOF'
import glob, json, os, re, sys
from datetime import date, timedelta

wc_root, today_s, state_path = sys.argv[1], sys.argv[2], sys.argv[3]
today = date.fromisoformat(today_s)
reports_dir = os.path.join(wc_root, "mike", "reports")
state = json.load(open(state_path))

def dates_from(fname):
    return [date.fromisoformat(m) for m in re.findall(r"\d{4}-\d{2}-\d{2}", os.path.basename(fname))]

actions = []

# --- Weekly: liệt kê MỌI tuần đã hoàn thành (thứ Hai->thứ Sáu) còn thiếu báo cáo kể từ
#     most_recent_weekly, KHÔNG chỉ tuần gần nhất — bài học 2026-08-01: bản cũ chỉ nhìn
#     "tuần liền trước hôm nay" nên nếu lỡ backfill 1 tuần, tuần cũ hơn nữa sẽ KHÔNG bao giờ
#     được đề cập lại (period_key tính từ today, không phải từ most_recent_weekly). Cap 8 tuần
#     backfill/lần chạy (phòng runaway nếu dữ liệu nav_history/reports thất lạc bất thường).
weekly_files = glob.glob(os.path.join(reports_dir, "*_weekly_report_*.md"))
weekly_dates = [max(dates_from(f)) for f in weekly_files if dates_from(f)]
most_recent_weekly = max(weekly_dates) if weekly_dates else None

this_monday = today - timedelta(days=today.weekday())
if most_recent_weekly is None:
    # chưa từng có báo cáo tuần nào — chỉ backfill 1 tuần gần nhất (tránh dispatch runaway lịch sử)
    start_monday = this_monday - timedelta(days=7)
else:
    start_monday = most_recent_weekly + timedelta(days=3)  # thứ Sáu cũ -> thứ Hai tuần kế

# Liệt kê MỌI tuần đã ĐÓNG ĐỦ (qua hết thứ Sáu + buffer 3 ngày) kể từ start_monday — KHÔNG
# giới hạn bởi "tuần hiện tại" theo weekday(), vì hôm nay có thể là T7/CN và tuần T2-T6 vừa
# rồi đã đóng xong dù cùng "tuần lịch" với hôm nay theo cách tính weekday-anchor.
candidate_mondays = []
m = start_monday
while len(candidate_mondays) < 8:
    last_friday = m + timedelta(days=4)
    if (today - last_friday).days < 3:
        break  # tuần này (và mọi tuần sau) chưa đóng đủ — dừng, không cần xét tiếp
    candidate_mondays.append(m)
    m += timedelta(days=7)

for last_monday in candidate_mondays:
    last_friday = last_monday + timedelta(days=4)
    period_key = f"weekly_{last_monday.isoformat()}_{last_friday.isoformat()}"
    if state.get(period_key) != today_s:
        actions.append({
            "kind": "weekly", "period_key": period_key,
            "desc": f"tuần {last_monday.isoformat()} → {last_friday.isoformat()}",
            "target_file": f"mike/reports/SpaceX_ZaloPay_weekly_report_{last_monday.isoformat()}_to_{last_friday.isoformat()}.md",
            "most_recent": most_recent_weekly.isoformat() if most_recent_weekly else "CHƯA CÓ",
        })

# --- Monthly: từ ngày 5, tháng trước phải có báo cáo (bỏ qua trước go-live 2026-07) ---
GO_LIVE_MONTH = (2026, 7)
if today.day >= 5:
    if today.month == 1:
        lm_year, lm_num = today.year - 1, 12
    else:
        lm_year, lm_num = today.year, today.month - 1
    if (lm_year, lm_num) >= GO_LIVE_MONTH:
        last_month_str = f"{lm_year}-{lm_num:02d}"
        monthly_files = glob.glob(os.path.join(reports_dir, "*_monthly_report_*.md"))
        has_last_month = any(last_month_str in os.path.basename(f) for f in monthly_files)
        if not has_last_month:
            period_key = f"monthly_{last_month_str}"
            if state.get(period_key) != today_s:
                actions.append({
                    "kind": "monthly", "period_key": period_key,
                    "desc": f"tháng {last_month_str}",
                    "target_file": f"mike/reports/SpaceX_ZaloPay_monthly_report_{last_month_str}.md",
                    "most_recent": "CHƯA CÓ" if not monthly_files else "có tháng khác, thiếu tháng này",
                })

print(json.dumps(actions))
PYEOF
)"

N=$(echo "$PLAN" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
if [ "$N" -eq 0 ]; then
  echo "check_report_cadence: OK — không có báo cáo tuần/tháng nào quá hạn."
  exit 0
fi

echo "$PLAN" | python3 -c "
import json, sys
for a in json.load(sys.stdin):
    print(f\"{a['kind']}\t{a['period_key']}\t{a['desc']}\t{a['target_file']}\t{a['most_recent']}\")
" | while IFS=$'\t' read -r KIND PKEY DESC TFILE MOSTRECENT; do
  MSG="🔴 **Báo cáo ${KIND} quá hạn — ${DESC}** — chưa có file, đang TỰ ĐỘNG dispatch Taylor soạn + gửi (báo cáo gần nhất: ${MOSTRECENT}). File dự kiến: \`${TFILE}\`. Đây là auto-dispatch từ check_report_cadence.sh (cron), không phải người theo dõi thủ công — nếu 24h sau vẫn chưa thấy báo cáo, đó là dấu hiệu dispatch thất bại, cần Mike kiểm tra bin/jobs.sh."
  echo "$MSG"
  "$ROOT/bin/notify_thread.sh" "$MSG" "$TRADING_REPORT_THREAD" 2>/dev/null || true
  "$ROOT/bin/append_event.sh" Mike question "report-cadence-overdue-${PKEY}" \
    "{\"kind\":\"${KIND}\",\"period\":\"${DESC}\",\"target_file\":\"${TFILE}\",\"question\":\"Bao cao ${KIND} qua han, da auto-dispatch Taylor. Xac nhan/theo doi.\"}" \
    2>/dev/null || true

  EMAIL_STEP="Sau khi gửi Discord xong, CŨNG chạy: python3 mike/bin/send_report_email.py ${TFILE} — gửi email báo cáo này cho user. Nếu lệnh đó exit khác 0 (vd thiếu credential), NÓI RÕ trong phần trả lời cuối, đừng bỏ qua im lặng."

  if [ "$KIND" = "weekly" ]; then
    PROMPT="Soạn và GỬI báo cáo TUẦN trading cho 2 tài khoản SpaceX + ZaloPay, kỳ ${DESC} (thứ Hai-thứ Sáu, dữ liệu đã đầy đủ). File: ${TFILE}. Đây là auto-dispatch từ check_report_cadence.sh (báo cáo tuần bị bỏ sót, phát hiện tự động). Dùng đúng pipeline mike/kb/coding_guidelines.md §6 (verify_account_snapshot.py --account-no cho CẢ 2 account, đối chiếu nav_history_{account}.csv thật, không tự bịa số). Format/văn phong theo mẫu mike/reports/SpaceX_ZaloPay_weekly_report_2026-07-13_to_2026-07-17.md. Có gap/lỗi/residual chưa giải thích được thì NÓI RÕ trong báo cáo, đừng làm tròn. Gửi vào Discord Trading report topic (channel ${TRADING_REPORT_THREAD}). ${EMAIL_STEP} Ghi bus finding khi xong: file path, NAV cuối kỳ 2 account, % biến động, gap/lỗi nếu có."
  else
    PROMPT="Soạn và GỬI báo cáo THÁNG trading cho 2 tài khoản SpaceX + ZaloPay, kỳ ${DESC} (cả tháng). File: ${TFILE}. Đây là auto-dispatch từ check_report_cadence.sh (báo cáo tháng bị bỏ sót, phát hiện tự động). Áp dụng chuẩn mực báo cáo THÁNG theo mike/kb/coding_guidelines.md §6 (MTD/QTD/YTD, so với VNINDEX, attribution sector/mã, risk metrics DD/vol, phí/chi phí, outlook) — không chỉ lặp báo cáo tuần. Dùng đúng pipeline verify_account_snapshot.py --account-no + nav_history_{account}.csv thật. Có gap/lỗi/residual chưa giải thích được thì NÓI RÕ, đừng làm tròn. Gửi vào Discord Trading report topic (channel ${TRADING_REPORT_THREAD}). ${EMAIL_STEP} Ghi bus finding khi xong."
  fi
  "$ROOT/bin/dispatch.sh" Taylor "$PROMPT" --bg --model opus --effort high --timeout 3600 2>&1 | tail -5

  python3 -c "
import json
state = json.load(open('$STATE'))
state['$PKEY'] = '$TODAY'
json.dump(state, open('$STATE', 'w'), indent=2, ensure_ascii=False)
"
done
