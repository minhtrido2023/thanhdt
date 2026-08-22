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
#   4. Delivery closure: artifact != delivery. Report chưa gửi đi qua report_delivery_gate.py;
#      chỉ COMPLETE khi validation + Discord + email đều có bằng chứng gắn với SHA-256.
set -uo pipefail
SCHEDULED_KIND=""
case "${1:-}" in
  "") ;;
  --scheduled-weekly) SCHEDULED_KIND="weekly" ;;
  --scheduled-monthly) SCHEDULED_KIND="monthly" ;;
  *) echo "Usage: $0 [--scheduled-weekly|--scheduled-monthly]" >&2; exit 2 ;;
esac
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
TRADING_REPORT_THREAD="trading_report"
STATE="$ROOT/state/report_cadence_dispatched.json"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"

mkdir -p "$ROOT/state"
[ -f "$STATE" ] || echo '{}' > "$STATE"

EMAILED_STATE="$ROOT/state/report_emailed.json"
[ -f "$EMAILED_STATE" ] || echo '{}' > "$EMAILED_STATE"
DELIVERY_STATE="$ROOT/state/report_delivery.json"

# --- Catch-up DELIVERY sweep: cứu report đã tạo nhưng agent dừng/max-turn trước lúc gửi.
#     Chỉ chọn file chưa có legacy email proof để không phát lại kho lịch sử khi rollout;
#     gate mới giữ ledger hai kênh và retry riêng kênh còn thiếu.
#     Mở rộng *_daily_report_*.md 2026-08-11 (coding_guidelines.md §6 mục 5, user yêu cầu):
#     trước đó chỉ quét weekly/monthly — daily report (vd SpaceX_ZaloPay_daily_report_*.md) hoàn
#     toàn không có lưới an toàn nào, chỉ tin dispatch prompt nhớ gọi send_report_email.py.
for f in "$ROOT"/reports/*_daily_report_*.md "$ROOT"/reports/*_weekly_report_*.md "$ROOT"/reports/*_monthly_report_*.md; do
  [ -e "$f" ] || continue
  FNAME="$(basename "$f")"
  # paper_programs_daily_report_*.md đã có cron+state EMAIL riêng (paper_programs_daily_report.sh
  # --email, state/paper_programs_report_emailed.json) — bỏ qua ở đây để KHÔNG gửi trùng 2 email.
  case "$FNAME" in paper_programs_daily_report_*.md) continue ;; esac
  ALREADY="$(python3 -c "
import json
state = json.load(open('$EMAILED_STATE'))
print('yes' if state.get('$FNAME') else 'no')
")"
  if [ "$ALREADY" = "no" ]; then
    python3 "$ROOT/bin/report_delivery_gate.py" "$f" --topic "$TRADING_REPORT_THREAD" ||
      echo "check_report_cadence: DELIVERY INCOMPLETE cho $FNAME — giữ việc mở và tự retry lần sau." >&2
  fi
done

# --- Auto-close các bus question `report-cadence-overdue-*` mà kỳ báo cáo ĐÃ được phủ.
#     Đây là question do CHÍNH script này sinh ra (máy hỏi, không có chủ sở hữu là người) —
#     khi Taylor soạn xong file thì việc đã xong THẬT, nhưng không ai post `answer` giữ nguyên
#     topic, nên ops_health_check §5 (fail-closed, đúng) cứ báo pending mãi → COORD_WARN
#     dispatch wags_autofix 2 lần/ngày cho việc đã xong (ca thật 2026-08-10:
#     report-cadence-overdue-weekly_2026-08-03_2026-08-07 pending trong khi file 59KB đã nằm
#     trên đĩa từ 11:49 ICT). Máy hỏi thì máy tự đóng — bằng chứng đóng là ARTIFACT tồn tại,
#     không phải self-report của agent nào.
#
#     HAI SỬA sau arch-review coord-2026-08-10 (verdict NEEDS_CHANGES) — cả hai đều là lỗi
#     "closer dùng phép kiểm KHÁC detector", tức đúng lớp sự cố mà chính nó định vá:
#     (1) DANH SÁCH CÂU HỎI CÒN TREO không tự dò lại bằng matcher thứ BA nữa (bản cũ: exact
#         topic-match, phi thời gian, không quét archive .jsonl.gz) mà hỏi thẳng
#         bin/bus_question_audit.py — matcher CHÍNH THỐNG, port đúng thuật toán của
#         ops_health_check §5 (cross-agent, substring+timestamp r_ts>=q_ts, quét archive).
#         Hệ quả trực tiếp: hỏi LẠI cùng topic sau một answer cũ thì lại đóng được (bản cũ
#         chết vĩnh viễn ở ca này), và không còn 3 bản matcher lệch nhau.
#     (2) BẰNG CHỨNG ĐÓNG dùng CÙNG phép kiểm với detector sinh ra question (most_recent_weekly
#         theo ngày trong TÊN của bất kỳ *_weekly_report_*.md nào), KHÔNG phải os.path.exists
#         trên đúng chuỗi target_file. Tên biến thể (SpaceX_weekly_report_2026-08-07.md, có
#         thật trong repo) làm detector im nhưng closer không đóng được ⇒ question treo vĩnh
#         viễn — đúng ca sự cố này nhắm tới thì lại không có đường thoát nào cả.
#     Quyết định phủ nằm CÙNG khối python với detector (dưới đây, biến `closable`) để hai bên
#     không thể trôi ra khỏi nhau.
RC_PENDING_TOPICS="$(python3 "$ROOT/bin/bus_question_audit.py" --json 2>/dev/null | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
P = "report-cadence-overdue-"
for q in d.get("pending", []):
    t = str(q.get("topic") or "")
    if t.startswith(P):
        print(t)
')"
export RC_PENDING_TOPICS
export REPORT_SCHEDULED_KIND="$SCHEDULED_KIND"

PLAN="$(python3 - "$WC_ROOT" "$TODAY" "$STATE" "$DELIVERY_STATE" << 'PYEOF'
import glob, hashlib, json, os, re, sys
from datetime import date, timedelta

wc_root, today_s, state_path, delivery_state_path = sys.argv[1:5]
today = date.fromisoformat(today_s)
reports_dir = os.path.join(wc_root, "mike", "reports")
state = json.load(open(state_path))
scheduled_kind = os.environ.get("REPORT_SCHEDULED_KIND", "")
try:
    delivery_state = json.load(open(delivery_state_path))
except FileNotFoundError:
    delivery_state = {"reports": {}}

def delivered(fname):
    path = os.path.join(reports_dir, fname)
    rec = delivery_state.get("reports", {}).get(fname, {})
    if not os.path.isfile(path) or not isinstance(rec, dict):
        return False
    with open(path, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    def ok(channel):
        val = rec.get(channel, {})
        return (isinstance(val, dict) and val.get("status") == "delivered"
                and val.get("sha256") == sha and val.get("delivered_at"))
    return rec.get("sha256") == sha and rec.get("artifact_validated_at") and ok("discord") and ok("email")

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
delivered_weekly = [f for f in weekly_files if delivered(os.path.basename(f))]
delivered_weekly_dates = [max(dates_from(f)) for f in delivered_weekly if dates_from(f)]
most_recent_delivered_weekly = max(delivered_weekly_dates) if delivered_weekly_dates else None

this_monday = today - timedelta(days=today.weekday())
if scheduled_kind == "weekly":
    # Lượt chính thức sáng thứ Bảy: tuần T2→T6 vừa đóng, không chờ watchdog +3 ngày.
    candidate_mondays = [this_monday]
else:
    candidate_mondays = []
if most_recent_weekly is None:
    # chưa từng có báo cáo tuần nào — chỉ backfill 1 tuần gần nhất (tránh dispatch runaway lịch sử)
    start_monday = this_monday - timedelta(days=7)
else:
    start_monday = most_recent_weekly + timedelta(days=3)  # thứ Sáu cũ -> thứ Hai tuần kế

# Liệt kê MỌI tuần đã ĐÓNG ĐỦ (qua hết thứ Sáu + buffer 3 ngày) kể từ start_monday — KHÔNG
# giới hạn bởi "tuần hiện tại" theo weekday(), vì hôm nay có thể là T7/CN và tuần T2-T6 vừa
# rồi đã đóng xong dù cùng "tuần lịch" với hôm nay theo cách tính weekday-anchor.
if scheduled_kind not in ("weekly", "monthly"):
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
monthly_files = glob.glob(os.path.join(reports_dir, "*_monthly_report_*.md"))
if today.day >= 5 or scheduled_kind == "monthly":
    if today.month == 1:
        lm_year, lm_num = today.year - 1, 12
    else:
        lm_year, lm_num = today.year, today.month - 1
    if (lm_year, lm_num) >= GO_LIVE_MONTH and scheduled_kind != "weekly":
        last_month_str = f"{lm_year}-{lm_num:02d}"
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

# ── RC_CLOSE_BEGIN — quyết định "kỳ này ĐÃ ĐƯỢC PHỦ, đóng được question" ────────────────
# Marker ỔN ĐỊNH: bin/check_report_cadence_selfcheck.py trích ĐÚNG khối python trên rồi chạy
# nó trên reports_dir giả để khoá hồi quy. Khối này CỐ TÌNH nằm cùng scope với detector và
# dùng lại NGUYÊN các biến của nó (most_recent_weekly, monthly_files) — không được viết lại
# phép kiểm, vì "closer kiểm khác detector" chính là bug arch-review coord-2026-08-10 bắt.
PREFIX = "report-cadence-overdue-"
pending_keys = [t[len(PREFIX):].strip()
                for t in os.environ.get("RC_PENDING_TOPICS", "").splitlines()
                if t.strip().startswith(PREFIX)]
closable = []
for pk in pending_keys:
    mw = re.match(r"^weekly_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})$", pk)
    if mw:
        # Y HỆT điều kiện của nhánh weekly: candidate_mondays bắt đầu từ most_recent_weekly+3,
        # nên mọi tuần có thứ Hai TRƯỚC mốc đó đã được detector coi là có báo cáo.
        mon = date.fromisoformat(mw.group(1))
        if (most_recent_delivered_weekly is not None
                and mon < most_recent_delivered_weekly + timedelta(days=3)):
            closable.append([pk, f"delivery ledger COMPLETE through {most_recent_delivered_weekly.isoformat()} "
                                 f"(artifact validated + Discord + email, hash-bound)"])
        continue
    mm = re.match(r"^monthly_(\d{4}-\d{2})$", pk)
    if mm:
        # Y HỆT `has_last_month` của nhánh monthly.
        hit = [os.path.basename(f) for f in monthly_files
               if mm.group(1) in os.path.basename(f) and delivered(os.path.basename(f))]
        if hit:
            closable.append([pk, f"co bao cao thang {mm.group(1)}: {sorted(hit)[0]}"])
    # period_key lạ (schema đổi) ⇒ KHÔNG đóng — fail về phía để người xem, không tự dọn.

print(json.dumps({"actions": actions, "closable": closable}))
# ── RC_CLOSE_END ────────────────────────────────────────────────────────────────────────
PYEOF
)"

# ── RC_BASH_CLOSE_BEGIN — ghi answer đóng question (marker cho selfcheck) ────────────────
# KHÔNG nuốt lỗi: chỉ in "auto-closed" khi append_event.sh THẬT SỰ exit 0. Bản cũ dùng
# `>/dev/null 2>&1 || true` rồi echo vô điều kiện ⇒ log nói đã đóng trong khi bus không có
# answer nào (arch-review coord-2026-08-10, đúng pattern đã bị bác ở coord-2026-07-30).
echo "$PLAN" | python3 -c "
import json, sys
for pk, evid in json.load(sys.stdin).get('closable', []):
    print(f'{pk}\t{evid}')
" | while IFS=$'\t' read -r PKEY EVID; do
  [ -n "$PKEY" ] || continue
  TOPIC="report-cadence-overdue-${PKEY}"
  if "$ROOT/bin/append_event.sh" Mike answer "$TOPIC" \
       "{\"closed_by\":\"check_report_cadence.sh (auto)\",\"evidence\":\"${EVID}\"}" >/dev/null; then
    echo "check_report_cadence: auto-closed bus question '${TOPIC}' (${EVID})."
  else
    echo "check_report_cadence: KHÔNG ghi được answer đóng '${TOPIC}' (append_event.sh lỗi) — question VẪN TREO, sẽ thử lại lần chạy sau." >&2
  fi
done
# ── RC_BASH_CLOSE_END ───────────────────────────────────────────────────────────────────

N=$(echo "$PLAN" | python3 -c "import json,sys; print(len(json.load(sys.stdin)['actions']))")
if [ "$N" -eq 0 ]; then
  echo "check_report_cadence: OK — không có báo cáo tuần/tháng nào quá hạn."
  exit 0
fi

echo "$PLAN" | python3 -c "
import json, sys
for a in json.load(sys.stdin)['actions']:
    print(f\"{a['kind']}\t{a['period_key']}\t{a['desc']}\t{a['target_file']}\t{a['most_recent']}\")
" | while IFS=$'\t' read -r KIND PKEY DESC TFILE MOSTRECENT; do
  MSG="🔴 **Báo cáo ${KIND} quá hạn — ${DESC}** — chưa có file, đang TỰ ĐỘNG dispatch Taylor soạn + gửi (báo cáo gần nhất: ${MOSTRECENT}). File dự kiến: \`${TFILE}\`. Đây là auto-dispatch từ check_report_cadence.sh (cron), không phải người theo dõi thủ công — nếu 24h sau vẫn chưa thấy báo cáo, đó là dấu hiệu dispatch thất bại, cần Mike kiểm tra bin/jobs.sh."
  echo "$MSG"
  "$ROOT/bin/notify_thread.sh" "$MSG" "$TRADING_REPORT_THREAD" 2>/dev/null || true
  "$ROOT/bin/append_event.sh" Mike question "report-cadence-overdue-${PKEY}" \
    "{\"kind\":\"${KIND}\",\"period\":\"${DESC}\",\"target_file\":\"${TFILE}\",\"question\":\"Bao cao ${KIND} qua han, da auto-dispatch Taylor. Xac nhan/theo doi.\"}" \
    2>/dev/null || true

  EMAIL_STEP="Sau khi tạo artifact, BẮT BUỘC chạy: python3 mike/bin/report_delivery_gate.py ${TFILE} --topic ${TRADING_REPORT_THREAD}. File tồn tại, maxturns_pending hay gửi một kênh đều CHƯA hoàn tất; chỉ báo xong khi gate in COMPLETE."

  # Delegate step (thêm 2026-08-04, user mandate — tiết kiệm chi phí): phần NGHĨ/VIẾT văn xuôi
  # (narrative/nhận định, không cần chạy script/broker data) có thể peer-dispatch cho Winston
  # qua opencode/deepseek (rẻ hơn, xem kb/cli_providers.json). Toàn bộ phần LẤY SỐ LIỆU
  # (verify_account_snapshot.py, nav_history CSV), GHI FILE, gửi Discord/email vẫn PHẢI ở Taylor
  # trên claude — opencode không có Bash/Write (xác nhận 2026-08-03). Chỉ là gợi ý tối ưu chi
  # phí, không bắt buộc — Taylor tự viết thẳng nếu delegate quá chậm/lỗi, không chờ mãi.
  DELEGATE_STEP="Gợi ý tiết kiệm chi phí (không bắt buộc): sau khi đã LẤY ĐỦ số liệu đã verify (bằng Bash trên chính bạn), có thể soạn phần văn xuôi/nhận định (không phải số liệu) bằng cách peer-dispatch: bin/dispatch.sh Winston \"Viết phần narrative/nhận định cho báo cáo trading kỳ ${DESC}, dựa CHÍNH XÁC trên số liệu sau (đừng tự bịa số khác): <dán số liệu đã verify vào đây>\" --provider opencode --timeout 300 — rồi lấy kết quả về, TỰ đối chiếu lại số liệu trước khi ghép vào file cuối (đừng tin mù). Nếu lệnh đó treo/lỗi/quá 3 phút, TỰ viết luôn phần đó, đừng chờ."

  if [ "$KIND" = "weekly" ]; then
    MODEL="sonnet"
    EFFORT="medium"
    PROMPT="Soạn và GỬI báo cáo TUẦN trading cho 2 tài khoản SpaceX + ZaloPay, kỳ ${DESC} (thứ Hai-thứ Sáu, dữ liệu đã đầy đủ). File: ${TFILE}. Đây là auto-dispatch từ check_report_cadence.sh (báo cáo tuần bị bỏ sót, phát hiện tự động). Dùng đúng pipeline mike/kb/coding_guidelines.md §6 (verify_account_snapshot.py --account-no cho CẢ 2 account, đối chiếu nav_history_{account}.csv thật, không tự bịa số). Format/văn phong theo mẫu mike/reports/SpaceX_ZaloPay_weekly_report_2026-07-13_to_2026-07-17.md — nhưng TUYỆT ĐỐI không copy nội dung hạn chế/limitation từ mẫu cũ nếu chưa kiểm tra còn đúng không. CỤ THỂ: Trứng vàng (egg.totalValue) ĐÃ đọc tự động từ DNSE API từ 2026-08-18 (field egg.totalValue trong payload.egg của balances, daily_nav_snapshot.py dòng ~450, cột egg_assets_auto=True trong nav_history CSV) — KHÔNG còn là 'không đọc được qua API DNSE' hay 'off-book manual'. Nếu template mẫu có dòng đó (mục 7.2 hay inline), phải bỏ hoặc viết lại thành 'tự động từ API'. Breadth (%mã > MA50): dùng tav2_mike.universe_pit (PIT thật, không dùng ticker_prune) JOIN với tav2_bq.ticker lấy MA50/Close tại ngày giao dịch mới nhất; ghi rõ số mã trong rổ ngày đó. Sau khi có đủ số liệu, chạy: python3 /home/trido/thanhdt/WorkingClaude/mike/bin/value_radar_chart.py --out /tmp/value_radar_chart_\$(date +%Y%m%d).png và lưu path ra biến. Đính kèm file PNG đó vào cùng Discord message với báo cáo (bin/notify_thread.sh có thể gửi attachment). Trong phần 4.2 của báo cáo, thay bảng text bằng: [xem chart Value Radar đính kèm] và giữ lại các số liệu quan trọng (score, label, từng phân vị) làm text backup cho reader không thấy ảnh. Có gap/lỗi/residual chưa giải thích được thì NÓI RÕ trong báo cáo, đừng làm tròn. Gửi vào Discord Trading report topic (channel ${TRADING_REPORT_THREAD}). ${EMAIL_STEP} ${DELEGATE_STEP} Ghi bus finding khi xong: file path, NAV cuối kỳ 2 account, % biến động, gap/lỗi nếu có."
  else
    MODEL="opus"
    EFFORT="high"
    PROMPT="Soạn và GỬI báo cáo THÁNG trading cho 2 tài khoản SpaceX + ZaloPay, kỳ ${DESC} (cả tháng). File: ${TFILE}. Đây là auto-dispatch từ check_report_cadence.sh (báo cáo tháng bị bỏ sót, phát hiện tự động). Áp dụng chuẩn mực báo cáo THÁNG theo mike/kb/coding_guidelines.md §6 (MTD/QTD/YTD, so với VNINDEX, attribution sector/mã, risk metrics DD/vol, phí/chi phí, outlook) — không chỉ lặp báo cáo tuần. BẮT BUỘC thêm mục 'Paper signals chạy nền — kiểm tra suy giảm theo tháng' cho extreme_regime và fill_timing (hai mục không còn in daily): đọc mike/kb/paper_programs_registry.json, journal data/execution_logs/exec_main_*_journal.csv và output probe/charter liên quan; so sánh tháng này với tháng trước về số phiên evidence/lệnh, marker hoặc false-trigger, reject/fail, adherence cửa sổ và fill-vs-open khi đo được, cùng trạng thái gate. Kết luận chỉ là ổn định / chưa đủ dữ liệu / có dấu hiệu suy giảm cần điều tra, nêu số liệu và giới hạn; TUYỆT ĐỐI không coi ít quan sát hay không có trigger là bằng chứng alpha. Dùng đúng pipeline verify_account_snapshot.py --account-no + nav_history_{account}.csv thật. Có gap/lỗi/residual chưa giải thích được thì NÓI RÕ, đừng làm tròn. Gửi vào Discord Trading report topic (channel ${TRADING_REPORT_THREAD}). ${EMAIL_STEP} ${DELEGATE_STEP} Ghi bus finding khi xong, gồm kết luận monthly review của 2 paper signal."
  fi
  # `--thread "$TRADING_REPORT_THREAD"` tường minh — xem chú thích cùng ngày trong
  # daily_retro.sh (B1). Đúng topic mà chính PROMPT đã yêu cầu gửi báo cáo vào.
  # MODEL: tuần=sonnet (templated, không cần Opus), tháng=opus (attribution/outlook phức tạp
  # hơn) — chốt 2026-08-04 theo yêu cầu user tiết kiệm chi phí, xem thảo luận Discord cùng ngày.
  # EFFORT (thêm 2026-08-10, token-usage audit item #3): tách theo nhánh — trước đây cả 2 nhánh
  # cùng --effort high dù comment ngay trên nói rõ nhánh tuần "templated, không cần Opus" (hạ
  # model rồi nhưng quên xét lại effort, cùng dạng lệch đã tìm thấy ở Taylor interactive
  # dispatch). Tuần=medium (templated), tháng=high (attribution/outlook thật sự phức tạp hơn).
  "$ROOT/bin/dispatch.sh" Taylor "$PROMPT" --thread "$TRADING_REPORT_THREAD" --bg --model "$MODEL" --effort "$EFFORT" --timeout 3600 2>&1 | tail -5

  python3 -c "
import json
state = json.load(open('$STATE'))
state['$PKEY'] = '$TODAY'
json.dump(state, open('$STATE', 'w'), indent=2, ensure_ascii=False)
"
done
