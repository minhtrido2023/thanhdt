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
  --scheduled-quarterly) SCHEDULED_KIND="quarterly" ;;
  *) echo "Usage: $0 [--scheduled-weekly|--scheduled-monthly|--scheduled-quarterly]" >&2; exit 2 ;;
esac
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# ROOT phải là cây CANONICAL, không phải cây đang chạy. Đây là nơi RA QUYẾT ĐỊNH "kỳ này đã có
# báo cáo chưa": chạy từ worktree/clone thì DELIVERY_STATE + reports/ đều trỏ cây phụ ⇒ đọc sổ
# rỗng ⇒ dispatch soạn LẠI ⇒ artifact sha mới ⇒ delivery gate giao như bản hợp lệ ⇒ nhà đầu tư
# nhận báo cáo TRÙNG (ghim hash không cứu được, vì hash khác thật). Cùng một luật "sổ nằm ở
# đâu" với report_delivery_gate.py — vá một đầu là chưa vá (arch-review 2026-09-12).
# Fallback im lặng về cây đang chạy nếu bản sao này chưa có wc_paths.py (worktree tiền-vá):
# giữ nguyên hành vi cũ, không làm script chết.
# KHÔNG `2>/dev/null`: đúng những cảnh báo cần thấy nhất (env lệch cây, không tìm thấy
# canonical, lỗi python thật) đều đi ra stderr.
CANONICAL_ROOT="$(python3 "$ROOT/bin/wc_paths.py" --mike-canonical || true)"
if [ -n "$CANONICAL_ROOT" ] && [ -f "$CANONICAL_ROOT/MIKE.md" ] && [ "$CANONICAL_ROOT" != "$ROOT" ]; then
  echo "ℹ️  check_report_cadence: chạy từ $ROOT nhưng dùng sổ/báo cáo của cây canonical $CANONICAL_ROOT" >&2
  ROOT="$CANONICAL_ROOT"
fi
WC_ROOT="$(cd "$ROOT/.." && pwd)"
if [ -f "$WC_ROOT/wc_env.sh" ]; then
  # shellcheck source=/dev/null
  source "$WC_ROOT/wc_env.sh"
fi
TRADING_REPORT_THREAD="trading_report"
STATE="$ROOT/state/report_cadence_dispatched.json"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"

# ── QGUARD_BEGIN — --scheduled-quarterly chỉ chạy NGÀY CUỐI của tháng 3/6/9/12 (lịch ICT, TODAY đã neo
# TZ='Asia/Ho_Chi_Minh' §16). Cron `0 14 28-31 3,6,9,12 *` bắn cả 28-31 nên ngày khác thoát rc=0 IM LẶNG
# (không sweep, không dispatch, không ghi state). Đặt TRƯỚC delivery sweep NÊN lượt 21:00 ngày khác không
# sweep gì — việc sweep + cứu báo cáo quý là của lượt watchdog 08:30 T2-T6 (không cờ), vòng sweep của nó
# NAY đã gồm *_quarterly_report_*.md (trước vòng 2 thì thiếu ⇒ quý không có lưới giao bù). Chỉ phụ thuộc
# $TODAY (selfcheck trích khối này). §16: `date -d` ghim TZ=UTC — TZ=Asia/Beirut / Atlantic/Azores làm
# `date -d "2030-03-31 +1 day"` LỖI (DST nhảy 00:00) ⇒ _Q_NEXT_DOM rỗng ⇒ guard exit 0 IM LẶNG.
if [ "$SCHEDULED_KIND" = "quarterly" ]; then
  _Q_MONTH="$(TZ=UTC date -d "$TODAY" +%m)"; _Q_NEXT_DOM="$(TZ=UTC date -d "$TODAY +1 day" +%d)"
  case "$_Q_MONTH" in 03|06|09|12) _Q_QMONTH=1 ;; *) _Q_QMONTH=0 ;; esac
  if [ "$_Q_QMONTH" != "1" ] || [ "$_Q_NEXT_DOM" != "01" ]; then
    exit 0
  fi
fi
# ── QGUARD_END

mkdir -p "$ROOT/state"
[ -f "$STATE" ] || echo '{}' > "$STATE"

EMAILED_STATE="$ROOT/state/report_emailed.json"
[ -f "$EMAILED_STATE" ] || echo '{}' > "$EMAILED_STATE"
DELIVERY_STATE="$ROOT/state/report_delivery.json"
# De-dup cho cảnh báo "sweep DELIVERY INCOMPLETE" — 1 lần/file/ngày (mẫu bin/eod_trading_report.sh
# ALERTED_STATE, arch-review coord-2026-08-31 required_changes #1).
SWEEP_ALERTED_STATE="$ROOT/state/report_delivery_incomplete_alerted.json"
[ -f "$SWEEP_ALERTED_STATE" ] || echo '{}' > "$SWEEP_ALERTED_STATE"

# ── NAVCHECK_BEGIN — hàm thuần cho NAVGUARD quý (selfcheck trích + chạy khối này). §16: date -d ghim UTC.
_q_nav_check_date() {   # $1=cuối quý (YYYY-MM-DD) → ngày LÀM VIỆC cuối ≤ nó (T7→-1, CN→-2). Lễ ngày thường: không xử lý ở đây.
  case "$(TZ=UTC date -d "$1" +%u)" in
    6) TZ=UTC date -d "$1 -1 day" +%F ;;
    7) TZ=UTC date -d "$1 -2 days" +%F ;;
    *) printf '%s\n' "$1" ;;
  esac
}
_q_nav_problems() {     # $1=ngày kiểm → stdout " SpaceX(thiếu dòng) ZaloPay(nav_is_estimate=True)" (rỗng = đủ + đã chốt)
  local d="$1" a f v out=""
  for a in SpaceX ZaloPay; do
    f="${NAV_DIR:-$WC_ROOT/data/execution_logs}/nav_history_${a}.csv"
    v="$(awk -F, -v d="$d" '$1==d{r="FOUND:" $10} END{print r}' "$f" 2>/dev/null)"
    case "$v" in
      "") out="${out} ${a}(thiếu dòng ${d})" ;;
      FOUND:True) out="${out} ${a}(nav_is_estimate=True ngày ${d})" ;;
    esac
  done
  printf '%s' "$out"
}
_state_get() {          # $1=key → giá trị trong $STATE (rỗng nếu không có/đọc không được)
  STATE_F="$STATE" KEY="$1" python3 -c "
import json, os
try: print(json.load(open(os.environ['STATE_F'])).get(os.environ['KEY'], ''))
except Exception: print('')
"
}
_state_set() {          # $1=key $2=value — ghi NGUYÊN TỬ (tmp + os.replace, §5)
  STATE_F="$STATE" KEY="$1" VAL="$2" python3 -c "
import json, os, sys, tempfile
path = os.environ['STATE_F']
try:
    state = json.load(open(path))
    if not isinstance(state, dict):
        raise ValueError('state khong phai dict: %r' % type(state).__name__)
except Exception as e:
    print('check_report_cadence: state cu hong (%s: %s) — dung lai tu {}' % (type(e).__name__, e), file=sys.stderr)
    state = {}
state[os.environ['KEY']] = os.environ['VAL']
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix='.report_cadence_dispatched.', suffix='.tmp')
try:
    with os.fdopen(fd, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
except BaseException:
    try:
        os.unlink(tmp)
    except OSError:
        pass
    raise
"
}
# ── NAVCHECK_END

# --- Catch-up DELIVERY sweep: cứu report đã tạo nhưng agent dừng/max-turn trước lúc gửi.
#     Chỉ chọn file chưa có legacy email proof để không phát lại kho lịch sử khi rollout;
#     gate mới giữ ledger hai kênh và retry riêng kênh còn thiếu.
#     Mở rộng *_daily_report_*.md 2026-08-11 (coding_guidelines.md §6 mục 5, user yêu cầu):
#     trước đó chỉ quét weekly/monthly — daily report (vd SpaceX_ZaloPay_daily_report_*.md) hoàn
#     toàn không có lưới an toàn nào, chỉ tin dispatch prompt nhớ gọi send_report_email.py.
for f in "$ROOT"/reports/*_daily_report_*.md "$ROOT"/reports/*_weekly_report_*.md "$ROOT"/reports/*_monthly_report_*.md "$ROOT"/reports/*_quarterly_report_*.md; do
  [ -e "$f" ] || continue
  FNAME="$(basename "$f")"
  # paper_programs_daily_report_*.md đã có cron+state EMAIL riêng (paper_programs_daily_report.sh
  # --email, state/paper_programs_report_emailed.json) — bỏ qua ở đây để KHÔNG gửi trùng 2 email.
  case "$FNAME" in paper_programs_daily_report_*.md) continue ;; esac
  # State hỏng/cụt KHÔNG được làm câm sweep: coi như CHƯA gửi (fail-open về phía sweep/kiểm tra)
  # và in lỗi thật ra stderr — cùng khuôn vendor_mismatch_alert.sh (§29, arch-review coord-2026-09-27).
  # Giá trị đi qua ENV chứ không nội suy vào nguồn python: tên file là dữ liệu ngoài.
  ALREADY="$(EMAILED_STATE="$EMAILED_STATE" FNAME="$FNAME" python3 -c "
import json, os, sys
try:
    state = json.load(open(os.environ['EMAILED_STATE']))
    print('yes' if state.get(os.environ['FNAME']) else 'no')
except Exception as e:
    print('no')
    sys.stderr.write('check_report_cadence: KHONG doc duoc %s — coi nhu CHUA gui, VAN sweep. Loi that: %s: %s\n'
                     % (os.environ['EMAILED_STATE'], type(e).__name__, e))
")"
  if [ "$ALREADY" = "no" ]; then
    # Capture thay vì để chảy thẳng ra log: khối "⚠️ LỆCH NGUỒN VENDOR" mà report_return_gate in
    # ra đi qua stdout của delivery gate ⇒ chôn trong logs/check_report_cadence.log, user không
    # thấy. Bắt lấy ở đây rồi bắn Discord/bus với ĐÚNG nguyên nhân + ĐÚNG người (Winston).
    # Chạy cho CẢ hai nhánh rc: ca "mã lệch nguồn nhưng báo cáo không công bố tỉ suất" cho rc=0,
    # tức cổng KHÔNG chặn — đó chính là ca không kênh nào khác kêu lên.
    # Gửi bù báo cáo DAILY: kèm dashboard "độ phù hợp chiến lược" CỦA ĐÚNG NGÀY ĐÓ nếu file còn
    # trên đĩa; không có thì gửi không kèm. KHÔNG sinh lại ở đây — dashboard đọc dữ liệu "hiện
    # tại", sinh cho ngày cũ ra số sai ngày. Weekly/monthly không khớp mẫu tên ⇒ không bao giờ kèm.
    # SWEEP_ATTACH_BEGIN — trích bởi strategy_fit_email_attach_selfcheck.py. Đổi marker ⇒ FATAL.
    ATTACH_ARGS=()
    # Kiểm weekly/monthly TRƯỚC: `=~` thứ hai sẽ ghi đè BASH_REMATCH của mẫu ngày.
    if [[ ! "${FNAME,,}" =~ (weekly|monthly) ]] \
       && [[ "$FNAME" =~ _daily_report_([0-9]{4}-[0-9]{2}-[0-9]{2})\.md$ ]] \
       && [ -s "$ROOT/reports/dashboard/strategy_fit_${BASH_REMATCH[1]}.html" ]; then
      ATTACH_ARGS=(--attach "$ROOT/reports/dashboard/strategy_fit_${BASH_REMATCH[1]}.html")
    fi
    # SWEEP_ATTACH_END
    GATE_OUT="$(python3 "$ROOT/bin/report_delivery_gate.py" "$f" --topic "$TRADING_REPORT_THREAD" "${ATTACH_ARGS[@]}" 2>&1)"
    GATE_RC=$?
    _RC_WHY=""   # đặt lại mỗi file: biến sống qua vòng lặp, khối GATE_BLOCK_DELIVERY không được đọc lý do của file trước
    printf '%s\n' "$GATE_OUT"
    VENDOR_RC=0
    printf '%s\n' "$GATE_OUT" | "$ROOT/bin/vendor_mismatch_alert.sh" \
      "$FNAME" "$TRADING_REPORT_THREAD" || VENDOR_RC=$?
    if [ "$GATE_RC" -ne 0 ]; then
      echo "check_report_cadence: DELIVERY INCOMPLETE cho $FNAME — giữ việc mở và tự retry lần sau." >&2
      # arch-review coord-2026-08-31 (required_changes #1): trước đây CHỈ có dòng >&2 ở trên —
      # chết trong logs/check_report_cadence.log, không ai thấy trừ khi tự đi đọc log. Cùng khuôn
      # bin/eod_trading_report.sh:70-73 (append_event.sh error + notify_thread.sh), có de-dup
      # 1 lần/file/ngày để không spam mỗi lượt cron cho cùng 1 file kẹt.
      # Cùng lý do fail-open + lỗi thật ra stderr như ALREADY ở trên (§29).
      ALREADY_ALERTED="$(SWEEP_ALERTED_STATE="$SWEEP_ALERTED_STATE" FNAME="$FNAME" TODAY="$TODAY" python3 -c "
import json, os, sys
try:
    state = json.load(open(os.environ['SWEEP_ALERTED_STATE']))
    print('yes' if state.get(os.environ['FNAME']) == os.environ['TODAY'] else 'no')
except Exception as e:
    print('no')
    sys.stderr.write('check_report_cadence: KHONG doc duoc %s — coi nhu CHUA canh bao, VAN gui. Loi that: %s: %s\n'
                     % (os.environ['SWEEP_ALERTED_STATE'], type(e).__name__, e))
")"
      if [ "$ALREADY_ALERTED" = "no" ]; then
        "$ROOT/bin/append_event.sh" Mike error "report-delivery-incomplete-${FNAME}" \
          "{\"artifact\":\"${FNAME}\",\"retry\":\"check_report_cadence sweep (hằng ngày)\"}" \
          2>/dev/null || true
        # Nguyên nhân/người xử lý suy từ BẰNG CHỨNG cổng vừa in ra, không phát một câu cố định
        # (§29). VENDOR_RC=10 chỉ nói "có vendor-lệch-nguồn HOẶC lookup_failed", KHÔNG nói được
        # loại nào — phải grep TAG THẬT trong $GATE_OUT (arch-review vòng 5, R1-C), ĐỪNG suy từ
        # rc=10 (bug gốc: cả 3 nơi từng khẳng định "hai nguồn bất đồng" ngay cả khi chỉ có
        # lookup_failed thuần — SAI, vì lookup_failed nghĩa là CHƯA có nguồn thứ hai để bất đồng).
        # RC_VENDOR_REASON_BEGIN — trích bởi check_report_cadence_selfcheck.py, extract-and-test
        # 3 tổ hợp $GATE_OUT (mismatch-only / lookup_failed-only / cả hai). Đổi tên/di chuyển
        # marker ⇒ selfcheck FATAL, không im lặng pass.
        if printf '%s\n' "$GATE_OUT" | grep -q '^VENDOR_MISMATCH_ALERT|'; then
          INCOMPLETE_MSG="🔴 **Delivery INCOMPLETE — ${FNAME}** — bị CHẶN vì **LỆCH NGUỒN CỔ TỨC** (tiền broker ≠ \`tav2_bq.corporate_action\`), KHÔNG phải lỗi soạn báo cáo. Cần **Winston (data-ops)** đối soát nguồn vendor — chi tiết ở cảnh báo ngay trên. Sweep tự retry mỗi ngày."
        elif printf '%s\n' "$GATE_OUT" | grep -q '^VENDOR_LOOKUP_FAILED|'; then
          INCOMPLETE_MSG="🔴 **Delivery INCOMPLETE — ${FNAME}** — bị CHẶN vì KHÔNG TRA ĐƯỢC nguồn vendor \`tav2_bq.corporate_action\` (lỗi hạ tầng BQ), KHÔNG PHẢI hai nguồn bất đồng số và KHÔNG phải lỗi soạn báo cáo. Thử lại khi BQ khoẻ — không cần Winston đối soát số trừ khi lỗi lặp lại nhiều lượt. Sweep tự retry mỗi ngày."
        else
          # Bản trước in MỘT câu cố định "chưa giao đủ (Discord+email, hash-bound)" cho mọi ca còn
          # lại — kể cả khi cổng tỉ suất CHẶN vì số sai hay cổng SẬP (arch-review 53b48b76 F7):
          # sai hướng người xử lý, lặp mỗi ngày. Lý do đọc từ CHÍNH $GATE_OUT (§29), cùng cách
          # trích với khối EOD_GATE_REASON của eod_trading_report.sh: khối "❌ CHẶN" ⇒ tiêu đề + mục
          # đầu; không có ⇒ dòng cuối cổng in ra (dòng bọc "returned non-zero exit status" thì lấy
          # dòng lỗi thật đứng trước nó); cổng không in gì ⇒ nói đúng là không xác định được.
          _RC_BLK="$(printf '%s\n' "$GATE_OUT" | grep -m1 '^❌ CHẶN' || true)"
          if [ -n "$_RC_BLK" ]; then
            _RC_WHY="cổng tỉ suất CHẶN — ${_RC_BLK#❌ CHẶN — } $(printf '%s\n' "$GATE_OUT" | grep -m1 -A1 '^❌ CHẶN' | sed -n '2p' | sed -E 's/^ *• *//')"
          else
            _RC_WHY="$(printf '%s\n' "$GATE_OUT" | grep -v '^[[:space:]]*$' | grep -v 'returned non-zero exit status' | tail -n 1 || true)"
            [ -n "$_RC_WHY" ] || _RC_WHY="$(printf '%s\n' "$GATE_OUT" | grep -v '^[[:space:]]*$' | tail -n 1 || true)"
            [ -n "$_RC_WHY" ] && _RC_WHY="dòng cuối cổng in ra: $_RC_WHY"
          fi
          [ -n "$_RC_WHY" ] || _RC_WHY="cổng không in dòng nào — không xác định được nguyên nhân từ output"
          _RC_WHY="$(printf '%s' "$_RC_WHY" | python3 -c 'import sys; s = sys.stdin.read(); print(" ".join(s.replace(chr(34), "").replace(chr(92), "").replace(chr(96), "").split())[:300], end="")')"
          INCOMPLETE_MSG="🔴 **Delivery INCOMPLETE — ${FNAME}** — ${_RC_WHY}. Sweep tự retry mỗi ngày; chi tiết: logs/check_report_cadence.log, hoặc bin/report_delivery_gate.py --status ${FNAME}."
        fi
        # RC_VENDOR_REASON_END
        "$ROOT/bin/notify_thread.sh" "$INCOMPLETE_MSG" \
          "$TRADING_REPORT_THREAD" 2>/dev/null || true
        # Ghi NGUYÊN TỬ (tmp + os.replace, §5) — cùng khuôn vendor_mismatch_alert.sh: kill giữa
        # lúc ghi không được để lại JSON cụt cho lượt sau vấp (đây chính là nguyên nhân state
        # hỏng mà nhánh đọc ALREADY_ALERTED ở trên vừa phải phòng thủ).
        SWEEP_ALERTED_STATE="$SWEEP_ALERTED_STATE" FNAME="$FNAME" TODAY="$TODAY" python3 -c "
import json, os, sys, tempfile
path = os.environ['SWEEP_ALERTED_STATE']
try:
    state = json.load(open(path))
    if not isinstance(state, dict):
        raise ValueError('state khong phai dict: %r' % type(state).__name__)
except Exception as e:
    print('check_report_cadence: state cu hong (%s: %s) — dung lai tu {}' % (type(e).__name__, e), file=sys.stderr)
    state = {}
state[os.environ['FNAME']] = os.environ['TODAY']
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix='.report_delivery_incomplete_alerted.', suffix='.tmp')
try:
    with os.fdopen(fd, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
except BaseException:
    try:
        os.unlink(tmp)
    except OSError:
        pass
    raise
"
      fi
      # GATE_BLOCK_DELIVERY_BEGIN — question CÓ CHỦ + HẠN + LỆNH RECOVER cho file kẹt, sweep nhắc
      # tới khi `report_delivery_gate.py --status` (sổ hash-bound của chính cổng) báo COMPLETE
      # (retro 10-16→10-19 Pattern 1, phương án A 2026-10-20). Ngoài khối de-dup trên vì helper
      # tự idempotent theo TÊN FILE (một câu cho cả vòng đời file kẹt, kể cả qua nhiều ngày).
      # Chủ suy từ TAG THẬT cổng vừa in (§29), không đoán: VENDOR_* ⇒ Winston; còn lại ⇒ Taylor.
      # Điểm dừng: 3 ngày / 20 lần nhắc ⇒ EXPIRED (1 tin cuối, câu hỏi bus vẫn mở cho người đóng tay).
      if printf '%s\n' "$GATE_OUT" | grep -qE '^VENDOR_(MISMATCH_ALERT|LOOKUP_FAILED)\|'; then
        _GB_OWNER="Winston (data-ops: nguồn cổ tức vendor)"
      else
        _GB_OWNER="Taylor (soạn/sửa báo cáo theo dòng CHẶN của cổng)"
      fi
      timeout 60 python3 "$ROOT/bin/gate_block_question.py" open --gate delivery \
        --key "$FNAME" --owner "$_GB_OWNER" \
        --deadline "$(TZ='Asia/Ho_Chi_Minh' date -d 'tomorrow' +%Y-%m-%d)T08:30" \
        --recover "python3 $ROOT/bin/report_delivery_gate.py $f --topic $TRADING_REPORT_THREAD" \
        --probe "python3 $ROOT/bin/report_delivery_gate.py $f --status" \
        --reason "report_delivery_gate rc=$GATE_RC: ${_RC_WHY:-không xác định (đã báo INCOMPLETE trong ngày — xem logs/check_report_cadence.log hoặc report_delivery_gate.py --status)}" \
        --thread "$TRADING_REPORT_THREAD" --remind-every-min 240 \
        --expires-in-days 3 --max-reminders 20 \
        --extra "{\"artifact\":\"${FNAME}\"}" || true
      # GATE_BLOCK_DELIVERY_END
    fi
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
export RC_BIN_DIR="$ROOT/bin"   # heredoc detector import report_return_gate từ đây

PLAN="$(python3 - "$WC_ROOT" "$TODAY" "$STATE" "$DELIVERY_STATE" << 'PYEOF'
import glob, hashlib, json, os, re, sys
from datetime import date, timedelta

wc_root, today_s, state_path, delivery_state_path = sys.argv[1:5]
today = date.fromisoformat(today_s)
reports_dir = os.path.join(wc_root, "mike", "reports")
try:
    state = json.load(open(state_path))
    if not isinstance(state, dict):
        raise ValueError("state khong phai dict: %r" % type(state).__name__)
except FileNotFoundError:
    state = {}
except Exception as e:
    # state hỏng KHÔNG được giết cả bộ phát hiện quá hạn + auto-close (writer ở cuối file đã
    # dựng lại từ {} khi gặp state hỏng — reader phải cùng chịu được).
    print("check_report_cadence: state cu hong (%s: %s) — doc nhu {}" % (type(e).__name__, e),
          file=sys.stderr)
    state = {}
scheduled_kind = os.environ.get("REPORT_SCHEDULED_KIND", "")
try:
    delivery_state = json.load(open(delivery_state_path))
except FileNotFoundError:
    delivery_state = {"reports": {}}

# Content-completeness (thêm 2026-09-02, sau vụ báo cáo tháng 08: template tạo 25/08 với 5/10
# mục còn "[TBD" được delivery gate coi là COMPLETE và giao thật 28/08, TRƯỚC CẢ KHI tháng đóng
# — vì report_return_gate.py cũ không có phép kiểm nội dung nào, chỉ kiểm tỉ suất NẾU có bảng để
# kiểm. Marker khớp NGUYÊN VĂN quy ước đang dùng trong reports/*.md — mở rộng nếu thấy quy ước
# khác, đừng đoán. Danh sách nằm ở report_return_gate.py (nguồn duy nhất) — import, không chép tay.
sys.path.insert(0, os.environ["RC_BIN_DIR"])
from report_return_gate import INCOMPLETE_MARKERS  # noqa: E402

def content_complete(path):
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return False
    return not any(m in text for m in INCOMPLETE_MARKERS)

def delivered(fname):
    path = os.path.join(reports_dir, fname)
    rec = delivery_state.get("reports", {}).get(fname, {})
    if not os.path.isfile(path) or not isinstance(rec, dict):
        return False
    if not content_complete(path):
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

# Per-account split (user mandate 2026-09-02, coord job Taylor_20260902_161159): từ kỳ 08/2026,
# MỖI kỳ báo cáo (tuần/tháng) là 2 file RIÊNG — SpaceX (client-facing, sanitized) + ZaloPay (đầy
# đủ, nội bộ) — không còn 1 file gộp `SpaceX_ZaloPay_*`. Một kỳ chỉ coi là ĐÃ XONG khi CẢ HAI file
# đều delivered() — nếu chỉ kiểm 1 trong 2 (hoặc kiểu "có file nào khớp ngày là đủ" như logic cũ),
# account còn lại sẽ không bao giờ được cron dispatch lại một khi account kia đã xong.
#
# Tương thích ngược: các kỳ TRƯỚC mốc tách (< 2026-08-24, dùng 1 file `SpaceX_ZaloPay_*` gộp) vẫn
# phải tiếp tục được coi là ĐÃ XONG như trước — nếu không, script sẽ nghĩ hàng chục tuần/tháng cũ
# đột nhiên "quá hạn" theo chuẩn mới và dispatch backfill tràn lan. Vì vậy period_done() chấp nhận
# HOẶC (a) cả 2 file per-account đã delivered [chuẩn MỚI], HOẶC (b) file gộp cũ đã delivered
# [chuẩn CŨ, chỉ còn khớp với các kỳ lịch sử — không script nào còn TẠO MỚI file gộp nữa nên
# nhánh (b) tự nhiên không còn áp dụng được cho các kỳ từ 2026-08-24 trở đi].
ACCOUNTS = ("SpaceX", "ZaloPay")


def _delivered_any(files, predicate):
    """True nếu có ÍT NHẤT 1 file trong `files` khớp `predicate(basename)` và đã delivered() —
    khớp theo tiền tố+ngày (không phải tên tuyệt đối) để chịu được hậu tố biến thể
    (vd `_CORRECTION_VIB`, đã có thật trong repo — arch-review coord-2026-08-10 case #2)."""
    return any(predicate(os.path.basename(f)) and delivered(os.path.basename(f)) for f in files)


def weekly_period_done(files, mon, fri):
    mon_s, fri_s = mon.isoformat(), fri.isoformat()
    split_done = all(
        _delivered_any(files, lambda bn, acct=acct: bn.startswith(acct + "_weekly_report_")
                       and mon_s in bn and fri_s in bn)
        for acct in ACCOUNTS)
    if split_done:
        return True
    return delivered(f"SpaceX_ZaloPay_weekly_report_{mon_s}_to_{fri_s}.md")


def monthly_period_done(files, ym):
    split_done = all(
        _delivered_any(files, lambda bn, acct=acct: bn.startswith(acct + "_monthly_report_") and ym in bn)
        for acct in ACCOUNTS)
    if split_done:
        return True
    return delivered(f"SpaceX_ZaloPay_monthly_report_{ym}.md")


def weekly_filenames(mon, fri):
    """Tên CANONICAL cho kỳ mới (dùng khi cần đề xuất target_file cho dispatch — không phải để
    kiểm tra đã xong hay chưa, xem weekly_period_done())."""
    return [f"{acct}_weekly_report_{mon.isoformat()}_to_{fri.isoformat()}.md" for acct in ACCOUNTS]


def monthly_filenames(ym):
    return [f"{acct}_monthly_report_{ym}.md" for acct in ACCOUNTS]


actions = []

# --- Weekly: liệt kê MỌI tuần đã hoàn thành (thứ Hai->thứ Sáu) còn thiếu báo cáo kể từ
#     most_recent_weekly, KHÔNG chỉ tuần gần nhất — bài học 2026-08-01: bản cũ chỉ nhìn
#     "tuần liền trước hôm nay" nên nếu lỡ backfill 1 tuần, tuần cũ hơn nữa sẽ KHÔNG bao giờ
#     được đề cập lại (period_key tính từ today, không phải từ most_recent_weekly). Cap 8 tuần
#     backfill/lần chạy (phòng runaway nếu dữ liệu nav_history/reports thất lạc bất thường).
weekly_files = glob.glob(os.path.join(reports_dir, "*_weekly_report_*.md"))
weekly_dates = [max(dates_from(f)) for f in weekly_files if dates_from(f)]
most_recent_weekly = max(weekly_dates) if weekly_dates else None
# Suy period (mon,fri) từ MỌI file tuần đang có (cả 2 account, kể cả file gộp lịch sử
# `SpaceX_ZaloPay_weekly_report_*` — dates_from() vẫn đọc được 2 ngày từ tên đó), rồi lọc period
# nào ĐÃ XONG THẬT bằng weekly_period_done() (cả 2 file account riêng đều delivered()). File gộp
# lịch sử không tự khớp weekly_period_done() (nó không có tên `SpaceX_weekly_report_...`/
# `ZaloPay_weekly_report_...`) — đúng ý: các kỳ TRƯỚC ngày tách (< 2026-08-24) coi như CHƯA XONG
# theo nghĩa mới, nhưng candidate_mondays/start_monday dưới đây chỉ backfill từ kỳ tách trở đi
# (mốc most_recent_delivered_weekly sẽ tự nhảy tới tuần 24-28/08 vừa giao lại — không backfill
# runaway về các tuần gộp cũ vì start_monday cách today quá xa sẽ bị cap 8 tuần ở vòng lặp dưới).
weekly_periods = sorted({tuple(sorted(dates_from(f))[:2]) for f in weekly_files if len(dates_from(f)) >= 2})
delivered_weekly_dates = [fri for mon, fri in weekly_periods if weekly_period_done(weekly_files, mon, fri)]
most_recent_delivered_weekly = max(delivered_weekly_dates) if delivered_weekly_dates else None

this_monday = today - timedelta(days=today.weekday())
if scheduled_kind == "weekly":
    # Lượt chính thức sáng thứ Bảy: tuần T2→T6 vừa đóng, không chờ watchdog +3 ngày.
    candidate_mondays = [this_monday]
else:
    candidate_mondays = []
if most_recent_delivered_weekly is None:
    # chưa từng có báo cáo tuần nào ĐÃ GIAO XONG — chỉ backfill 1 tuần gần nhất (tránh dispatch
    # runaway lịch sử)
    start_monday = this_monday - timedelta(days=7)
else:
    # arch-review coord-2026-08-31 (required_changes #2): mốc PHẢI là tuần đã GIAO xong
    # (delivered — sha khớp + Discord + email + không marker TBD), không phải "có file đúng
    # tên" (most_recent_weekly) — một file tồn tại nhưng bị report_return_gate chặn/chưa gửi sẽ
    # không còn sinh cảnh báo nào cho các tuần SAU đó nếu neo theo most_recent_weekly.
    start_monday = most_recent_delivered_weekly + timedelta(days=3)  # thứ Sáu cũ -> thứ Hai tuần kế

# Liệt kê MỌI tuần đã ĐÓNG ĐỦ (qua hết thứ Sáu + buffer 3 ngày) kể từ start_monday — KHÔNG
# giới hạn bởi "tuần hiện tại" theo weekday(), vì hôm nay có thể là T7/CN và tuần T2-T6 vừa
# rồi đã đóng xong dù cùng "tuần lịch" với hôm nay theo cách tính weekday-anchor.
if scheduled_kind not in ("weekly", "monthly", "quarterly"):
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
        # Đường TUYỆT ĐỐI canonical: nửa còn lại của cùng một luật "sổ nằm ở đâu". Sổ đã ghim
        # nhưng nếu agent soạn artifact vào `mike/reports/` TƯƠNG ĐỐI với cwd của nó (worktree)
        # thì sweep không thấy file/hash ⇒ vẫn coi là quá hạn ⇒ dispatch lại ⇒ gửi trùng.
        sx_f, zp_f = weekly_filenames(last_monday, last_friday)
        actions.append({
            "kind": "weekly", "period_key": period_key,
            "desc": f"tuần {last_monday.isoformat()} → {last_friday.isoformat()}",
            "target_file_spacex": os.path.join(reports_dir, sx_f),
            "target_file_zalopay": os.path.join(reports_dir, zp_f),
            "most_recent": most_recent_weekly.isoformat() if most_recent_weekly else "CHƯA CÓ",
            # scheduled_kind=="weekly" -> lượt cron 09:00 T7 ĐÚNG LỊCH (this_monday luôn là tuần
            # vừa đóng), không phải watchdog phát hiện quá hạn -> không được gắn nhãn "overdue".
            "overdue": scheduled_kind == "",
        })

# --- Monthly: từ ngày 5, tháng trước phải có báo cáo (bỏ qua trước go-live 2026-07) ---
GO_LIVE_MONTH = (2026, 7)
monthly_files = glob.glob(os.path.join(reports_dir, "*_monthly_report_*.md"))
if scheduled_kind != "quarterly" and (today.day >= 5 or scheduled_kind == "monthly"):
    if today.month == 1:
        lm_year, lm_num = today.year - 1, 12
    else:
        lm_year, lm_num = today.year, today.month - 1
    if (lm_year, lm_num) >= GO_LIVE_MONTH and scheduled_kind not in ("weekly", "quarterly"):
        last_month_str = f"{lm_year}-{lm_num:02d}"
        # arch-review coord-2026-08-31 (required_changes #2, gộp với monthly cùng lỗi 2026-09-02):
        # "đã xong" = CẢ HAI file account (SpaceX + ZaloPay) đúng tên VÀ delivered() (sha khớp +
        # Discord + email + KHÔNG còn marker TBD) — không phải chỉ SỰ TỒN TẠI FILE, và không phải
        # 1 file gộp như trước 2026-09 nữa (monthly_period_done() ở trên).
        has_last_month = monthly_period_done(monthly_files, last_month_str)
        if not has_last_month:
            period_key = f"monthly_{last_month_str}"
            if state.get(period_key) != today_s:
                sx_f, zp_f = monthly_filenames(last_month_str)
                actions.append({
                    "kind": "monthly", "period_key": period_key,
                    "desc": f"tháng {last_month_str}",
                    "target_file_spacex": os.path.join(reports_dir, sx_f),
                    "target_file_zalopay": os.path.join(reports_dir, zp_f),
                    "most_recent": "CHƯA CÓ" if not monthly_files else "có tháng khác, thiếu tháng này",
                    "overdue": scheduled_kind == "",
                })

# --- Quarterly (user duyệt 02/11/2026; kỳ đầu 2026-Q4): lượt --scheduled-quarterly chạy 21:00 ICT ĐÚNG
#     NGÀY CUỐI QUÝ (31/03, 30/06, 30/09, 31/12) cho CHÍNH quý đó. Watchdog (không cờ, 08:30 hằng ngày)
#     bắt quý VỪA ĐÓNG còn thiếu/chưa giao (rescue nếu lượt 21:00 hỏng hoặc thiếu NAV ngày cuối quý).
#     Cuối quý rơi T7/CN ⇒ không đổi lịch: builder lấy phiên nav_history cuối cùng ≤ cuối quý
#     (S.last_trading_on_or_before / nav_row_on_or_before), nên T7/CN vẫn ra báo cáo, đóng ở phiên T6.
GO_LIVE_QUARTER = (2026, 4)
quarterly_files = glob.glob(os.path.join(reports_dir, "*_quarterly_report_*.md"))

def quarterly_period_done(files, qk):
    return all(
        _delivered_any(files, lambda bn, acct=acct: bn.startswith(acct + "_quarterly_report_") and qk in bn)
        for acct in ACCOUNTS)

def quarterly_filenames(qk):
    return [f"{acct}_quarterly_report_{qk}.md" for acct in ACCOUNTS]

def is_quarter_last_day(d):
    return d.month in (3, 6, 9, 12) and (d + timedelta(days=1)).month != d.month

def recently_dispatched(pk, min_age_days=2):
    """Chống DOUBLE-DISPATCH quý: lượt 21:00 ngày D ghi state[pk]=D; watchdog 08:30 D+1 (~11,5h sau) mà
    `!= today` thì dispatch lần 2 khi job 1 còn chạy/pending-resume ⇒ 2 bản build khác sha ⇒ email trùng.
    Nên chỉ cứu khi KHÔNG có state hoặc state cũ ≥ min_age_days ngày. State hỏng ⇒ coi là mới (fail-safe
    chống trùng: trùng email nhà đầu tư tệ hơn cứu muộn 1 ngày)."""
    v = state.get(pk)
    if not v:
        return False
    try:
        return (today - date.fromisoformat(v)).days < min_age_days
    except (ValueError, TypeError):
        return True

target_q = None   # (year, quarter)
if scheduled_kind == "quarterly":
    if is_quarter_last_day(today):
        target_q = (today.year, today.month // 3)
elif scheduled_kind == "":
    qn_prev = (today.month - 1) // 3          # quý đã đóng gần nhất; 0 ⇒ Q4 năm trước
    target_q = (today.year - 1, 4) if qn_prev == 0 else (today.year, qn_prev)
if target_q is not None and (target_q[0], target_q[1]) >= GO_LIVE_QUARTER:
    qk = f"{target_q[0]}-Q{target_q[1]}"
    if not quarterly_period_done(quarterly_files, qk):
        period_key = f"quarterly_{qk}"
        if not recently_dispatched(period_key):
            sx_f, zp_f = quarterly_filenames(qk)
            actions.append({
                "kind": "quarterly", "period_key": period_key,
                "desc": f"quý {qk}",
                "target_file_spacex": os.path.join(reports_dir, sx_f),
                "target_file_zalopay": os.path.join(reports_dir, zp_f),
                "most_recent": "CHƯA CÓ" if not quarterly_files else "có quý khác, thiếu quý này",
                "overdue": scheduled_kind == "",
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
        # Y HỆT `has_last_month` của nhánh monthly — CẢ HAI file account phải delivered().
        if monthly_period_done(monthly_files, mm.group(1)):
            closable.append([pk, f"co bao cao thang {mm.group(1)}: {', '.join(monthly_filenames(mm.group(1)))}"])
    mq = re.match(r"^quarterly_(\d{4}-Q[1-4])$", pk)
    if mq:
        if quarterly_period_done(quarterly_files, mq.group(1)):
            closable.append([pk, f"co bao cao quy {mq.group(1)}: {', '.join(quarterly_filenames(mq.group(1)))}"])
        continue
    # period_key lạ (schema đổi) ⇒ KHÔNG đóng — fail về phía để người xem, không tự dọn.

print(json.dumps({"actions": actions, "closable": closable}))
# ── RC_CLOSE_END ────────────────────────────────────────────────────────────────────────
PYEOF
)"

# Heredoc chết (traceback/import hỏng) ⇒ PLAN rỗng: trước đây `[ "$N" -eq 0 ]` lỗi, vòng while
# không có input rồi script thoát rc=0 — cron báo xanh trong khi bộ phát hiện quá hạn đã chết.
if ! printf '%s' "$PLAN" | python3 -c "import json,sys; json.load(sys.stdin)['actions']" 2>/dev/null; then
  echo "❌ check_report_cadence: LỖI — bộ phát hiện không trả PLAN JSON hợp lệ (xem traceback phía trên); KHÔNG thể kết luận có/không báo cáo quá hạn." >&2
  exit 1
fi

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
  echo "check_report_cadence: OK — không có báo cáo tuần/tháng/quý nào quá hạn."
  exit 0
fi

echo "$PLAN" | python3 -c "
import json, sys
for a in json.load(sys.stdin)['actions']:
    print(f\"{a['kind']}\t{a['period_key']}\t{a['desc']}\t{a['target_file_spacex']}\t{a['target_file_zalopay']}\t{a['most_recent']}\t{int(a.get('overdue', True))}\")
" | while IFS=$'\t' read -r KIND PKEY DESC TFILE_SX TFILE_ZP MOSTRECENT OVERDUE; do
  # ── NAVGUARD_BEGIN — báo cáo QUÝ: NAV của NGÀY LÀM VIỆC CUỐI ≤ cuối quý phải có + đã chốt, cho CẢ 2 account.
  # Vì sao: build.py lấy dòng nav_history gần nhất ≤ cuối quý (S.nav_row_on_or_before) — thiếu dòng thì NÓ LẶNG
  # LẼ LÙI về phiên trước và ra báo cáo "đóng quý" thiếu 1 phiên, không báo lỗi. Kiểm ngày làm việc cuối ≤
  # PERIOD_END (KHÔNG phải $TODAY: quý kết thúc T7/CN thì là thứ Sáu) và kiểm nav_is_estimate=True (số ước
  # lượng chưa chốt). CHẠY CẢ TRÊN watchdog (OVERDUE=1) — trước đây bỏ qua nên rescue sáng hôm sau soạn báo
  # cáo từ NAV thiếu/ước lượng.
  #  · 21:00 (OVERDUE=0): thiếu ⇒ HOÃN (không dispatch, KHÔNG ghi state dispatch) + status + ghi dấu
  #    deferred_<PKEY> để watchdog sáng mai biết đây là hoãn CÓ CHỦ ĐÍCH (không gửi cảnh báo đỏ "quá hạn").
  #  · watchdog (OVERDUE=1): thiếu ⇒ HOÃN + bus `question` (topic report-cadence-overdue-<PKEY> để bộ đóng
  #    câu hỏi tự đóng khi báo cáo giao xong; lời lẽ "chờ NAV", không phải "quá hạn"). Trần: quá
  #    _Q_DEFER_MAX_DAYS ngày kể từ cuối quý mà NAV vẫn thiếu/ước lượng ⇒ KHÔNG tự dispatch, chuyển sang HỎI NGƯỜI (bus question nhắc mỗi lượt watchdog tới khi giao xong; ngày lễ trùng phiên làm việc cuối quý cũng chặn tới khi có người quyết — hướng fail-safe).
  _Q_DEFER_MAX_DAYS=4
  _RESUMED_NOTE=""
  if [ "$KIND" = "quarterly" ]; then
    _qk0="${PKEY#quarterly_}"
    _QPE="$(TZ=UTC date -d "${_qk0%-Q*}-$(printf '%02d' $((3 * ${_qk0#*-Q})))-01 +1 month -1 day" +%F)"
    _QCHK=""; [ -n "$_QPE" ] && _QCHK="$(_q_nav_check_date "$_QPE")"
    if [ -z "$_QCHK" ]; then
      echo "❌ check_report_cadence: KHÔNG tính được ngày cuối quý/ngày kiểm NAV từ PKEY=${PKEY} — dừng, không dispatch." >&2
      exit 1
    fi
    _NAV_MISSING="$(_q_nav_problems "$_QCHK")"
    _QAGE=$(( ( $(TZ=UTC date -d "$TODAY" +%s) - $(TZ=UTC date -d "$_QPE" +%s) ) / 86400 ))
    if [ -n "$_NAV_MISSING" ] && [ "$_QAGE" -le "$_Q_DEFER_MAX_DAYS" ]; then
      if [ "$OVERDUE" = "0" ]; then
        _NM="⏸️ **Báo cáo quý ${DESC} HOÃN** — NAV phiên ${_QCHK} chưa đủ/chưa chốt:${_NAV_MISSING}. Không dispatch (tránh báo cáo đóng quý thiếu 1 phiên). Watchdog 08:30 sáng mai sẽ tự soạn khi NAV đã có; nếu NAV là ước lượng (backfill, không tự chốt) thì sau ${_Q_DEFER_MAX_DAYS} ngày sẽ hỏi anh thay vì tự phát hành."
        _state_set "deferred_${PKEY}" "$TODAY"
        _EVT=status; _ETOPIC="report-cadence-quarterly-deferred-${PKEY}"
      else
        _NM="⏸️ **Báo cáo quý ${DESC} vẫn CHỜ NAV** (hoãn có chủ đích, không phải quá hạn) — NAV phiên ${_QCHK} chưa đủ/chưa chốt:${_NAV_MISSING}. Watchdog sẽ thử lại sáng mai (tối đa ${_Q_DEFER_MAX_DAYS} ngày sau cuối quý)."
        _EVT=question; _ETOPIC="report-cadence-overdue-${PKEY}"
      fi
      echo "$_NM"
      "$ROOT/bin/notify_thread.sh" "$_NM" "$TRADING_REPORT_THREAD" 2>/dev/null || true
      "$ROOT/bin/append_event.sh" Mike "$_EVT" "$_ETOPIC" \
        "{\"period\":\"${DESC}\",\"missing_nav\":\"${_NAV_MISSING# }\",\"nav_date\":\"${_QCHK}\",\"asof\":\"${TODAY}\",\"question\":\"Cho NAV phien ${_QCHK} truoc khi soan bao cao quy (hoan co chu dich).\"}" 2>/dev/null || true
      continue
    fi
    # Quá trần hoãn mà NAV VẪN thiếu/ước lượng ⇒ FAIL-SAFE: KHÔNG tự dispatch (arch-review vòng 2, 02/11). Dòng
    # nav_is_estimate=True do backfill --from-raw KHÔNG BAO GIỜ được chốt lại (daily_nav_snapshot.py), nên chờ thêm
    # vô nghĩa; tự phát hành sẽ đưa số ước lượng tới nhà đầu tư dưới nhãn "NAV đã đủ". Giữ cảnh báo + hỏi người quyết.
    if [ -n "$_NAV_MISSING" ]; then
      # §29: câu nguyên nhân rẽ theo bit THẬT trong _NAV_MISSING (thiếu dòng ≠ dòng ước lượng), không viết cứng.
      _WHY=""
      case "$_NAV_MISSING" in *nav_is_estimate=True*) _WHY=" Dòng NAV ước lượng (backfill) không tự chốt lại nên chờ thêm vô ích." ;; esac
      case "$_NAV_MISSING" in *"thiếu dòng"*) _WHY="${_WHY} Có dòng THIẾU hẳn (có thể do ngày lễ hoặc snapshot hỏng) — cần kiểm nguyên nhân." ;; esac
      _NM="🔴 **Báo cáo quý ${DESC} KHÔNG tự soạn** — đã quá ${_Q_DEFER_MAX_DAYS} ngày sau cuối quý mà NAV phiên ${_QCHK} vẫn chưa đủ/chưa chốt:${_NAV_MISSING}.${_WHY} Cần anh quyết: chốt NAV phiên đó rồi báo tôi soạn, hoặc cho soạn với phiên cuối đã chốt kèm công bố rõ."
      echo "$_NM"
      "$ROOT/bin/notify_thread.sh" "$_NM" "$TRADING_REPORT_THREAD" 2>/dev/null || true
      "$ROOT/bin/append_event.sh" Mike question "report-cadence-overdue-${PKEY}" \
        "{\"period\":\"${DESC}\",\"missing_nav\":\"${_NAV_MISSING# }\",\"nav_date\":\"${_QCHK}\",\"asof\":\"${TODAY}\",\"question\":\"NAV phien ${_QCHK} van thieu/uoc luong sau ${_Q_DEFER_MAX_DAYS} ngay; khong tu soan bao cao quy. Can nguoi quyet.\"}" 2>/dev/null || true
      continue
    fi
    if [ "$OVERDUE" = "1" ]; then
      _DEFERRED="$(_state_get "deferred_${PKEY}")"
      if [ -n "$_DEFERRED" ]; then OVERDUE=0; _RESUMED_NOTE=" (hoãn từ ${_DEFERRED} do chờ NAV, nay NAV đã đủ)"; fi
    fi
  fi
  # ── NAVGUARD_END
  # OVERDUE=1: watchdog (không cờ, cron 08:30 T2-T6) phát hiện kỳ THẬT SỰ bị bỏ sót — cảnh báo
  # đỏ + bus `question` cần người theo dõi là đúng. OVERDUE=0: lượt --scheduled-weekly/monthly
  # (09:00 T7 / ngày 1) chạy ĐÚNG LỊCH, không phải sự cố — trước đây dùng chung message "quá
  # hạn" + `question` cho cả 2 trường hợp nên MỌI báo cáo tuần/tháng đều bị gắn cảnh báo lỗi dù
  # đúng giờ (user báo cáo 2026-08-29). Tách message + loại event theo OVERDUE để chỉ ca thật
  # sự trễ mới lên cảnh báo.
  if [ "$OVERDUE" = "1" ]; then
    MSG="🔴 **Báo cáo ${KIND} quá hạn — ${DESC}** — chưa có đủ file, đang TỰ ĐỘNG dispatch Taylor soạn + gửi (báo cáo gần nhất: ${MOSTRECENT}). File dự kiến: \`${TFILE_SX}\` + \`${TFILE_ZP}\`. Đây là auto-dispatch từ check_report_cadence.sh (cron watchdog 08:30 T2-T6), không phải người theo dõi thủ công — nếu 24h sau vẫn chưa thấy CẢ HAI báo cáo, đó là dấu hiệu dispatch thất bại, cần Mike kiểm tra bin/jobs.sh."
    EVENT_TYPE="question"
    TOPIC_PREFIX="report-cadence-overdue-"
    EVENT_PAYLOAD="{\"kind\":\"${KIND}\",\"period\":\"${DESC}\",\"target_file_spacex\":\"${TFILE_SX}\",\"target_file_zalopay\":\"${TFILE_ZP}\",\"question\":\"Bao cao ${KIND} qua han, da auto-dispatch Taylor. Xac nhan/theo doi.\"}"
  else
    MSG="📊 **Đang tạo báo cáo ${KIND} theo lịch — ${DESC}** — lượt chạy đúng lịch (Thứ Bảy 09:00 / ngày 1 09:00 / 21:00 ngày cuối quý), không phải lỗi hay quá hạn${_RESUMED_NOTE}. Đang dispatch Taylor soạn + gửi. File dự kiến: \`${TFILE_SX}\` + \`${TFILE_ZP}\`."
    EVENT_TYPE="finding"
    TOPIC_PREFIX="report-cadence-scheduled-"
    EVENT_PAYLOAD="{\"kind\":\"${KIND}\",\"period\":\"${DESC}\",\"target_file_spacex\":\"${TFILE_SX}\",\"target_file_zalopay\":\"${TFILE_ZP}\"}"
  fi
  echo "$MSG"
  "$ROOT/bin/notify_thread.sh" "$MSG" "$TRADING_REPORT_THREAD" 2>/dev/null || true
  "$ROOT/bin/append_event.sh" Mike "$EVENT_TYPE" "${TOPIC_PREFIX}${PKEY}" "$EVENT_PAYLOAD" \
    2>/dev/null || true

  EMAIL_STEP="Sau khi tạo CẢ HAI artifact, BẮT BUỘC chạy return gate rồi delivery gate cho TỪNG file riêng (không phải 1 lệnh gộp): python3 $ROOT/bin/report_delivery_gate.py ${TFILE_SX} --topic ${TRADING_REPORT_THREAD} VÀ python3 $ROOT/bin/report_delivery_gate.py ${TFILE_ZP} --topic ${TRADING_REPORT_THREAD}. File tồn tại, maxturns_pending hay gửi một kênh đều CHƯA hoàn tất; chỉ báo xong khi CẢ HAI lệnh in COMPLETE."

  # Delegate step (thêm 2026-08-04, user mandate — tiết kiệm chi phí): phần NGHĨ/VIẾT văn xuôi
  # (narrative/nhận định, không cần chạy script/broker data) có thể peer-dispatch cho Winston
  # qua opencode/deepseek (rẻ hơn, xem kb/cli_providers.json). Toàn bộ phần LẤY SỐ LIỆU
  # (verify_account_snapshot.py, nav_history CSV), GHI FILE, gửi Discord/email vẫn PHẢI ở Taylor
  # trên claude — opencode không có Bash/Write (xác nhận 2026-08-03). Chỉ là gợi ý tối ưu chi
  # phí, không bắt buộc — Taylor tự viết thẳng nếu delegate quá chậm/lỗi, không chờ mãi.
  DELEGATE_STEP="Gợi ý tiết kiệm chi phí (không bắt buộc): sau khi đã LẤY ĐỦ số liệu đã verify (bằng Bash trên chính bạn), có thể soạn phần văn xuôi/nhận định (không phải số liệu) bằng cách peer-dispatch: bin/dispatch.sh Winston \"Viết phần narrative/nhận định cho báo cáo trading kỳ ${DESC}, dựa CHÍNH XÁC trên số liệu sau (đừng tự bịa số khác): <dán số liệu đã verify vào đây>\" --provider opencode --timeout 300 — rồi lấy kết quả về, TỰ đối chiếu lại số liệu trước khi ghép vào file cuối (đừng tin mù). Nếu lệnh đó treo/lỗi/quá 3 phút, TỰ viết luôn phần đó, đừng chờ."

  # CHUẨN MỚI bắt buộc từ kỳ 08/2026 (user mandate 2026-09-02, coord job Taylor_20260902_161159,
  # 4 file mẫu đã giao: {SpaceX,ZaloPay}_{weekly_report_2026-08-24_to_2026-08-28,monthly_report_2026-08}.md):
  SPLIT_STEP="BẮT BUỘC tạo 2 FILE RIÊNG, không còn 1 file gộp SpaceX_ZaloPay_*: \`${TFILE_SX}\` và \`${TFILE_ZP}\`. (1) File SpaceX = CLIENT-FACING, gửi nhà đầu tư ngoài: TUYỆT ĐỐI không có nội dung lỗi nội bộ/vận hành/sự cố hệ thống (không mục 'công bố sự cố', không nhắc 'job'/'dispatch'/'gate'/'circuit breaker'/'bug'/'lỗi hệ thống'/'bot chết'/'cron' — rà lại toàn văn bản trước khi gửi); chỉ trình bày số liệu hiệu suất thật (MTD/QTD/YTD so VNINDEX), attribution, rủi ro (DD/vol), phí, danh mục cuối kỳ, triển vọng thị trường — văn phong chuyên nghiệp kiểu báo cáo quản lý tài sản gửi nhà đầu tư (tường thuật khách quan, đơn vị tiền tệ/% nhất quán, không viết tắt kỹ thuật nội bộ, không dịch thô từ code/log), các sự kiện quyền lợi cổ đông (cổ tức/quyền mua) vẫn giữ lại nhưng viết lại bằng ngôn ngữ tài chính chuẩn, không kể lể quá trình debug/vá lỗi. (2) File ZaloPay = giữ ĐẦY ĐỦ như chuẩn cũ (kể cả mục công bố sự cố/vận hành, coding_guidelines.md §6) — đây là kênh nội bộ, KHÔNG gửi nhà đầu tư ngoài."
  CHART_STEP="BẮT BUỘC có biểu đồ minh hoạ, dùng công cụ có sẵn mike/bin/report_charts.py (matplotlib PNG tĩnh, KHÔNG phải HTML/SVG tương tác — kênh giao là email HTML + Discord text) — xem --help hoặc đọc source để biết đúng tham số (--account, --label, --title-suffix, --dates/--nav/--vnindex JSON lấy từ đúng pipeline verify đã dùng cho báo cáo — KHÔNG đọc data/VNINDEX.csv cục bộ, file đó đã dừng cập nhật từ 2026-05, phải lấy VNINDEX Close từ BQ/DNSE cùng nguồn đã verify; --allocation JSON top ~7-8 mã theo %NAV + gộp phần còn lại vào 'Cổ phiếu khác'/'Tiền mặt & tiền gửi'). Sinh đủ 3 chart mỗi account (NAV theo thời gian, lợi nhuận lũy kế indexed=100 so VNINDEX 1 trục duy nhất, phân bổ danh mục cuối kỳ) ra mike/reports/assets/, rồi nhúng vào từng .md bằng cú pháp markdown thường \![...](assets/<tên_file>.png) (render_report_html.py tự inline base64 khi gửi email — không cần tự encode base64 tay). Giữ 1 màu chính nhất quán cho đường NAV/lợi nhuận xuyên suốt các kỳ báo cáo (đã định nghĩa sẵn trong report_charts.py, đừng đổi màu tuỳ hứng), không dùng rainbow, có legend khi ≥2 chuỗi. GIỚI HẠN CÓ THẬT cần biết: Discord (notify_thread.sh) KHÔNG đính kèm được file — bản Discord CHỈ là text, thêm 1 dòng 'Xem biểu đồ minh hoạ đính kèm trong email' ở gần đầu báo cáo; chart CHỈ hiện trong bản email. Đừng cố lách giới hạn hạ tầng này."
  # 2026-10-10 (user yêu cầu sau weekly 05-09/10): bảng danh mục phải có khối tổng theo lớp tài sản,
  # và 5 'điểm chưa xác minh' của kỳ đó đều tra được từ nguồn có sẵn — nêu nguồn để kỳ sau tự tra.
  PORTFOLIO_STEP="Bảng 'Danh mục cuối kỳ' (CẢ 2 file) BẮT BUỘC có khối tổng hợp ngay sau các dòng mã, theo đúng thứ tự: dòng in đậm 'Cổ phiếu — tổng (N mã)' (giá trị thị trường, %NAV, lãi/lỗ % = tổng lãi/lỗ đã cộng cổ tức ròng chia tổng giá vốn thô), rồi 'Tiền mặt', 'Tiền gửi Trứng vàng', 'Nợ ký quỹ' (không có nợ vẫn GHI dòng với số 0, không bỏ dòng), cuối cùng 'Tổng NAV' — bốn khối cộng lại phải đúng bằng Tổng NAV và 100%. File ZaloPay thêm 2 dòng con in nghiêng dưới dòng tổng cổ phiếu: 'trong đó DGC' và 'trong đó các mã còn lại'. TRƯỚC KHI ghi bất kỳ điểm nào là 'chưa xác minh/chưa giải thích', phải tra hết các nguồn sau và nêu đã tra gì: (a) giá vốn broker thấp hơn giá khớp thật là KỲ VỌNG — DNSE tự trừ cổ tức tiền mặt GỘP khỏi costPrice tối trước ex-date, kiểm bằng bước nhảy costPrice trong bản ghi positions của dnse_raw; bảng dùng giá vốn THÔ (đã cộng lại cổ tức) và cộng cổ tức ròng vào tỉ suất, không lấy costPrice đã trừ đem so với giá thị trường; (b) cashDividendReceiving tăng nghĩa là có mã vừa qua ex-date và khoản đó ĐÃ nằm trong totalCash — tra tav2_bq.corporate_action theo exright_date và lấy khối lượng nhân value_per_share để gọi đúng mã, không đoán; (c) phần thay đổi NAV ngoài biến động giá phải phân rã tới đồng: cổ tức phải thu, lãi Trứng vàng (mức tăng egg trừ số tiền chuyển vào), lãi tiền mặt, trừ phí và thuế lấy từ data/execution_logs/dnse_khoplenh_broker_confirm_*.csv (cột thue gồm cả thuế TNCN 500đ/cp khi bán cổ phiếu nhận từ cổ tức cổ phiếu); (d) bot không có đường code nào nạp/rút Trứng vàng — mọi chuyển tiền sang Trứng vàng là thao tác tay của chủ tài khoản; (e) tỷ trọng cổ phiếu thấp hơn trần phân bổ của trạng thái thị trường là bình thường khi parking tắt và thiếu tín hiệu — đọc data/golive_v23_status.json (n_bal, n_lag_upcoming, n_lag_recent, etf_park_frac, capit_episode_basket) rồi giải thích bằng số đó; (f) lệnh bán tay ngoài giờ bot có thể thiếu trong orders của dnse_raw — đối chiếu journal và lịch sử lệnh DNSE (orders/history) trước khi coi là lệch."
  # 2026-10-14 (quỹ bước 4, user duyệt): bảng 3.2 "Hiệu suất lũy kế" KHÔNG tự gõ — dán đầu ra period_table_32.py.
  # Cổng report_delivery_gate._check_benchmark_table CHẶN bảng 1 cột VN-Index cũ khi chuỗi data/benchmark/vnindex_tr_daily.csv tồn tại.
  BENCH_STEP="Bảng 3.2 'Hiệu suất lũy kế' (CẢ weekly lẫn monthly, CẢ 2 file) KHÔNG được tự gõ hay tự tính: chạy \`python3 $ROOT/bin/period_table_32.py --account SpaceX --report-date <thứ Sáu cuối kỳ hoặc ngày cuối tháng>\` cho file SpaceX và \`python3 $ROOT/bin/period_table_32.py --account ZaloPay --report-date <cùng ngày> --with-sleeve\` cho file ZaloPay, rồi DÁN NGUYÊN đầu ra (6 cột Giai đoạn | tài khoản | VN-Index (giá) | VN-Index có cổ tức | Chênh so giá | Chênh so có cổ tức, kèm chú thích cố định 'sau thuế TNCN 5% trên cổ tức'). Bảng này chỉ có các dòng Tuần/MTD/Từ khi bắt đầu — KHÔNG thêm dòng QTD/YTD vào bảng 3.2 (báo cáo tháng vẫn có bảng 3.2 như trên; QTD/YTD nếu cần nêu ở phần khác, lấy từ nav_period_returns.py). Ô nào CLI ghi 'chưa có số' thì GIỮ NGUYÊN, không thay bằng số tự tính, không in chỉ số giá vào cột có cổ tức. Cột có cổ tức 'chưa có số' ở chuỗi chính sẽ bị cổng giao báo cáo CHẶN — khi đó báo gap trong bus finding thay vì tìm cách lách."
  # 2026-10-25 (user duyệt, job Taylor_20261025_092234): khối Kỹ thuật của 'Toàn cảnh thị trường' do
  # Livermore viết (bin/livermore_report_block.py: số do SCRIPT tính, Livermore chỉ diễn giải, kiểm số lạ
  # cơ học, fail-closed). Phần Cơ bản/định giá (Value Radar, DT gate §6b) GIỮ NGUYÊN — Livermore mù DT5G.
  case "$PKEY" in
    weekly_*) PERIOD_END="${PKEY##*_}" ;;
    monthly_*) PERIOD_END="$(TZ=UTC date -d "${PKEY#monthly_}-01 +1 month -1 day" +%F)" ;;
    quarterly_*) _qk="${PKEY#quarterly_}"; PERIOD_END="$(TZ=UTC date -d "${_qk%-Q*}-$(printf '%02d' $((3 * ${_qk#*-Q})))-01 +1 month -1 day" +%F)" ;;
    *) PERIOD_END="" ;;
  esac
  LIVERMORE_STEP="Khối '**Kỹ thuật (VN-Index ...)**' trong mục 'Toàn cảnh thị trường' (CẢ 2 file) KHÔNG tự viết nữa — do Livermore (chuyên viên kỹ thuật độc lập của đội) viết: TRƯỚC khi soạn, chạy \`python3 $ROOT/bin/livermore_report_block.py ensure --kind ${KIND} --period-end ${PERIOD_END}\` (thường 1-5 phút, tới ~45 phút nếu đến hạn lập dự báo mới ⇒ chạy NỀN bằng Bash run_in_background, soạn các mục khác trong lúc chờ, rồi đọc JSON nó in ra; idempotent + có khoá — chạy lại trả ngay khối đã có). (a) rc=0 (status PASS): DÁN NGUYÊN VĂN toàn bộ nội dung file .md mà JSON in ra trỏ tới (trường md) vào chỗ khối Kỹ thuật, KHÔNG sửa chữ/số/dòng nguồn/dòng dự báo đang mở, không thêm số kỹ thuật nào khác vào khối; sau khi ghi file chạy \`python3 $ROOT/bin/livermore_report_block.py verify-report <file> --kind ${KIND} --period-end ${PERIOD_END}\` cho TỪNG file, phải ra VERBATIM. (b) rc≠0 (FAIL): tự viết khối Kỹ thuật như trước (chỉ số liệu đã verify, nêu as-of) và KHÔNG ghi Livermore là nguồn; trong file ZaloPay thêm ngay dưới khối dòng '⚠️ Khối kỹ thuật Livermore không qua kiểm tra cơ học — khối trên do người soạn báo cáo viết. Lý do: <reason trong JSON>'; file SpaceX không nhắc sự cố; ghi reason vào bus finding. Mục 'Cơ bản / định giá' (Value Radar, DT gate) giữ nguyên cách làm hiện tại. Phần Outlook Kỹ thuật vẫn do bạn viết nhưng KHÔNG được trình bày như dự báo của Livermore, không cam kết độ chính xác."
  # 2026-10-31 (user duyệt khung báo cáo v2, job Taylor_20261031_042009 — kb/projects/report-style-v2-20261031.md):
  # agent KHÔNG viết markdown tự do nữa — số do bin/report_v2/build.py lấy thẳng từ pipeline, agent chỉ viết
  # narrative.json (builder TỪ CHỐI vượt trần / tự viết số). Prompt cũ giữ nguyên bên dưới làm QUY TRÌNH DỰ
  # PHÒNG khi builder lỗi (rc 1/3) — báo cáo không bao giờ bị bỏ im lặng.
  case "$PKEY" in
    weekly_*) _w="${PKEY#weekly_}"; V2_PERIOD="${_w%_*}_to_${_w#*_}" ;;
    monthly_*) V2_PERIOD="${PKEY#monthly_}" ;;
    quarterly_*) V2_PERIOD="${PKEY#quarterly_}" ;;
    *) V2_PERIOD="" ;;
  esac
  V2_NAR="$ROOT/reports/v2/narrative_${KIND}_${V2_PERIOD}"
  V2_LV="(1) Chạy \`python3 $ROOT/bin/livermore_report_block.py ensure --kind ${KIND} --period-end ${PERIOD_END}\` (nền nếu lâu) để builder có khối thị trường PASS của kỳ. "
  if [ "$KIND" = "quarterly" ]; then
    V2_LV="(1) Báo cáo QUÝ: builder quarterly KHÔNG đọc khối Livermore (livermore_report_block chỉ có kind weekly/monthly) — BỎ QUA bước này, đi thẳng bước (2). "
  fi
  V2_STEP="QUY TRÌNH CHUẨN v2 (user duyệt 31/10/2026 — BẮT BUỘC, thay cho việc tự viết markdown): ${V2_LV}(2) Dựng nháp CHO TỪNG account: \`python3 $ROOT/bin/report_v2/build.py ${KIND} --account SpaceX --period ${V2_PERIOD} --out-dir $ROOT/reports\` và tương tự --account ZaloPay — builder tự lấy MỌI số từ pipeline (nav_period_returns §31, period_table_32, report_return_gate §21 cộng cổ tức, dnse_raw lọc account_no §12) và ghi bản NHÁP vào $ROOT/reports/v2/draft/ (.md TÓM TẮT \`$ROOT/reports/v2/draft/<tên>.md\` + PDF A4 + HTML email ảnh cid ở $ROOT/reports/v2/draft/v2/<tên>/) — nháp KHÔNG nằm ở tên chuẩn nên không ai giao nhầm. Bạn KHÔNG được sửa tay file .md/PDF/HTML đó (cổng kiểm sha256 manifest — sửa tay = bị CHẶN). (3) Đọc .md + manifest.json (khối numbers, recon) + PDF NHÁP trong $ROOT/reports/v2/draft/, rồi viết ${V2_NAR}_SpaceX.json và ${V2_NAR}_ZaloPay.json theo lược đồ: {\"headline\": tiêu đề-kết luận ≤25 từ, \"key_points\": ≤3 gạch, \"sections\": {mục ∈ bridge/performance/risk/attribution/trades/portfolio/market/costs: ≤3 gạch}, \"outlook\": ≤4 hàng {scenario, condition, invalidation, prob(chữ: thấp/trung bình/cao)}, \"internal\": CHỈ ZaloPay, ≤6 khối {title, bullets ≤5 gạch ≤40 từ}}. Mỗi gạch ≤25 từ. KHÔNG tự viết số: mọi con số trong narrative phải CHÉP NGUYÊN VĂN từ số builder đã in; file SpaceX cấm tên nội bộ và từ vận hành (job/dispatch/gate/cron/bug/lỗi hệ thống). Mọi mục CHỈ-ZaloPay của quy trình cũ (công bố sự cố/gap/residual chưa giải thích; với tháng: 'Paper signals chạy nền' và 'Shadow intraday cutloss — tích luỹ OOS' chép số từ intraday_oos_monthly.py) ⇒ đưa vào narrative.internal của ZaloPay, KHÔNG vào SpaceX. (4) Dựng lại với \`--narrative ${V2_NAR}_<Account>.json --promote\` — CHỈ lần này có \`--promote\`: builder chạy artifact lint trên nháp rồi mới đưa về đúng tên chuẩn \`${TFILE_SX}\` / \`${TFILE_ZP}\` (+ $ROOT/reports/v2/<tên>/). rc=4 = nháp không qua artifact lint (thông điệp liệt kê) ⇒ sửa narrative nếu lỗi nằm ở chữ của bạn, nếu không thì xử lý như rc=1. rc=5 = bản chuẩn ĐÃ GIAO trước đó (phiên chạy lại/resume) ⇒ KHÔNG dựng/ghi đè nữa, chỉ chạy cổng giao bước (5) (idempotent COMPLETE) và ghi bus. rc=2 = narrative bị TỪ CHỐI (thông điệp liệt kê từng vi phạm) ⇒ SỬA narrative rồi chạy lại, KHÔNG nới luật, KHÔNG sửa builder. (5) Xem PDF (ít nhất trang 1) rồi chạy cổng giao cho TỪNG file như dưới — cổng chạy return gate §21, period-return §31, bảng benchmark, khối thị trường, artifact lint (repr/markdown thô/None/nan/tên nội bộ/font), nav-flow; email = HTML builder + PDF đính kèm; Discord nhận bản .md tóm tắt (notify_thread.sh không đính kèm file được — PDF chỉ ở email). DỰ PHÒNG: build.py rc=1 (lỗi code) hoặc rc=3 (thiếu nguồn số bắt buộc) cho account nào ⇒ NGAY LẬP TỨC ghi \`$ROOT/bin/append_event.sh Taylor error report-v2-build-fail-${PKEY} '{\"account\":\"<acct>\",\"rc\":<rc>,\"stderr\":\"<dòng lỗi thật>\"}'\`, XOÁ file .md nháp hỏng của account đó nếu có, rồi soạn account đó theo QUY TRÌNH CŨ (dự phòng) bên dưới — không được bỏ báo cáo. Account kia vẫn đi đường v2. Các ràng buộc về số liệu/cổng/gửi của quy trình cũ vẫn áp cho CẢ HAI đường. ——— QUY TRÌNH CŨ (CHỈ dùng khi dự phòng): "
  # N10 (r3, 31/10): tháng = livermore ensure (tới ~45') + 2 account × 2 lần dựng + cổng giao (BQ) ⇒
  # 3600s từng sát trần; tháng 5400s. NGÂN SÁCH nêu thẳng trong prompt để agent biết cắt ở đâu.
  if [ "$KIND" = "weekly" ]; then
    DISPATCH_TIMEOUT=3600
    MODEL="sonnet"
    EFFORT="medium"
    PROMPT="${V2_STEP}Soạn và GỬI báo cáo TUẦN trading cho 2 tài khoản SpaceX + ZaloPay, kỳ ${DESC} (thứ Hai-thứ Sáu, dữ liệu đã đầy đủ). ${SPLIT_STEP} Đây là auto-dispatch từ check_report_cadence.sh (báo cáo tuần bị bỏ sót, phát hiện tự động). Dùng đúng pipeline mike/kb/coding_guidelines.md §6 (verify_account_snapshot.py --account-no cho CẢ 2 account, đối chiếu nav_history_{account}.csv thật, không tự bịa số). Nguồn/as-of của mỗi số và mỗi biểu đồ ghi ở caption markdown ngay dưới ảnh (report_charts.py chỉ có --title-suffix, không vẽ nguồn lên PNG). Trong file SpaceX (client-facing) nguồn ghi bằng tên công khai (HOSE/HNX, dữ liệu môi giới, tính toán nội bộ), TUYỆT ĐỐI không nêu tên bảng/hệ thống nội bộ (tav2_*, BigQuery, DNSE API, universe_pit...), và 'rủi ro/giới hạn' là giới hạn thị trường/phương pháp, không phải sự cố vận hành. Văn phong cô đọng, chuyên nghiệp theo thông lệ thư nhà đầu tư của các nhà quản lý tài sản lớn (rõ luận điểm, dữ liệu, rủi ro và giới hạn), không sao chép hoặc gán nhận định cho BlackRock/Bill Ackman. BẮT BUỘC (cả 2 file): (1) Executive summary; (2) ngay đầu báo cáo có 'Toàn cảnh thị trường' tách rõ Technical (VNINDEX: xu hướng, hỗ trợ/kháng cự, breadth/thanh khoản/momentum nếu dữ liệu chứng minh được) và Fundamental (định giá, tăng trưởng lợi nhuận, lãi suất/vĩ mô, dòng tiền — nêu as-of/nguồn); (3) hiệu quả, attribution, exposure/risk của account; (4) biểu đồ theo chỉ dẫn biểu đồ bên dưới — mọi biểu đồ có tiêu đề, đơn vị, kỳ dữ liệu và nguồn, tạo từ dữ liệu thật; không có dữ liệu đáng tin thì nêu rõ thay vì vẽ; (5) kết luận 'Outlook kỳ tới' tách Technical/Fundamental, dạng kịch bản xác suất/điều kiện làm sai, không phải khuyến nghị chắc chắn. Format/văn phong tham khảo mẫu ĐÃ TÁCH gần nhất mike/reports/SpaceX_weekly_report_2026-08-24_to_2026-08-28.md (client-facing) và mike/reports/ZaloPay_weekly_report_2026-08-24_to_2026-08-28.md (đầy đủ) — KHÔNG dùng mẫu gộp cũ SpaceX_ZaloPay_weekly_report_*.md nữa (deprecated, chỉ còn trên đĩa làm lịch sử). TUYỆT ĐỐI không copy nội dung hạn chế/limitation từ mẫu cũ nếu chưa kiểm tra còn đúng không. CỤ THỂ: Trứng vàng (egg.totalValue) ĐÃ đọc tự động từ DNSE API từ 2026-08-18 (field egg.totalValue trong payload.egg của balances, daily_nav_snapshot.py dòng ~450, cột egg_assets_auto=True trong nav_history CSV) — KHÔNG còn là 'không đọc được qua API DNSE' hay 'off-book manual'. Breadth (%mã > MA50): dùng tav2_mike.universe_pit (PIT thật, không dùng ticker_prune) JOIN với tav2_bq.ticker lấy MA50/Close tại ngày giao dịch mới nhất; ghi rõ số mã trong rổ ngày đó (mục này thuộc bối cảnh thị trường, có thể giữ ở CẢ 2 file vì không phải nội dung nội bộ). Phần Fundamental của 'Toàn cảnh thị trường' lấy dòng DT gate (candidate/streak) từ dna_report.build_dt_gate_line() và Value Radar từ dna_report.build_value_radar_line() (chạy từ WC_ROOT, mike/kb/coding_guidelines.md §6b), KHÔNG tự tính phân vị P/E ad-hoc. ${LIVERMORE_STEP} ${PORTFOLIO_STEP} ${BENCH_STEP} ${CHART_STEP} Value Radar (dna_report.build_value_radar_line()) vẫn giữ ở dạng text/số liệu trong báo cáo như trước, không bắt buộc render thành chart riêng. Có gap/lỗi/residual chưa giải thích được thì NÓI RÕ trong file ZaloPay (đầy đủ); với file SpaceX thì trình bày số liệu cuối cùng đã verify, không kể lể quá trình. Gửi vào Discord Trading report topic (channel ${TRADING_REPORT_THREAD}). ${EMAIL_STEP} ${DELEGATE_STEP} Ghi bus finding khi xong: 2 file path (SpaceX + ZaloPay), NAV cuối kỳ 2 account, % biến động, kết luận market outlook, gap/lỗi nếu có, sha256 + trạng thái delivery gate của TỪNG file."
  elif [ "$KIND" = "quarterly" ]; then
    # QUÝ (user duyệt 02/11/2026, kỳ đầu 2026-Q4 chạy 21:00 ICT 31/12/2026): Sonnet/medium như tuần/tháng.
    # Không có LIVERMORE_STEP/PORTFOLIO_STEP/BENCH_STEP/CHART_STEP: builder quarterly tự dựng biểu đồ, bảng
    # danh mục và bảng hiệu suất từ pipeline (build_quarterly không đọc khối Livermore).
    DISPATCH_TIMEOUT=5400
    MODEL="sonnet"
    EFFORT="medium"
    PROMPT="${V2_STEP}Soạn và GỬI báo cáo QUÝ trading cho 2 tài khoản SpaceX + ZaloPay, kỳ ${DESC} (dữ liệu tới hết ${PERIOD_END}; nếu ngày đó là T7/CN thì builder tự lấy phiên nav_history cuối cùng ≤ ngày đó — KHÔNG tự sửa mốc). ${SPLIT_STEP} Đây là báo cáo QUÝ chạy ĐÚNG LỊCH 21:00 ICT ngày cuối quý (hoặc watchdog 08:30 bắt quý quá hạn). Cadence quarterly dùng cùng quy trình v2 như tuần/tháng: lệnh dựng là \`build.py quarterly --account X --period ${V2_PERIOD}\`. Script lịch đã kiểm trước khi dispatch: nav_history của phiên làm việc cuối ≤ ${PERIOD_END} có đủ + không phải nav_is_estimate; builder LÙI IM LẶNG về dòng gần nhất ≤ ngày đó nếu thiếu (không báo lỗi) — nên nếu \`build.py\` in phiên chốt KHÁC phiên làm việc cuối ≤ ${PERIOD_END}, KHÔNG phát hành: ghi bus error rồi dừng. Quý chứa ngày khởi điểm của account: builder đã xử lý ('không có' cho đóng góp theo mã) — nếu không vỡ thì giữ nguyên. Mọi mục CHỈ-ZaloPay (sự cố/gap/residual chưa giải thích) vào narrative.internal của ZaloPay, KHÔNG vào SpaceX. Gửi vào Discord Trading report topic (channel ${TRADING_REPORT_THREAD}). ${EMAIL_STEP} Ghi bus finding khi xong: 2 file path, NAV cuối kỳ 2 account, % QTD, sha256 + trạng thái delivery gate của TỪNG file."
  else
    # Báo cáo = việc thường ngày ⇒ Sonnet/medium cho CẢ tuần lẫn tháng (user chốt 2026-10-06;
    # trước đó tháng ghim opus/high). Nghiên cứu/coding khó mới lên Opus — kb/mike_model_routing.md.
    DISPATCH_TIMEOUT=5400
    MODEL="sonnet"
    EFFORT="medium"
    PROMPT="${V2_STEP}Soạn và GỬI báo cáo THÁNG trading cho 2 tài khoản SpaceX + ZaloPay, kỳ ${DESC} (cả tháng). ${SPLIT_STEP} Đây là auto-dispatch từ check_report_cadence.sh (báo cáo tháng bị bỏ sót, phát hiện tự động). Áp dụng chuẩn mực báo cáo THÁNG theo mike/kb/coding_guidelines.md §6 (MTD/QTD/YTD, so với VNINDEX, attribution sector/mã, risk metrics DD/vol, phí/chi phí, outlook) — không chỉ lặp báo cáo tuần. Nguồn/as-of của mỗi số và mỗi biểu đồ ghi ở caption markdown ngay dưới ảnh (report_charts.py chỉ có --title-suffix, không vẽ nguồn lên PNG). Trong file SpaceX (client-facing) nguồn ghi bằng tên công khai (HOSE/HNX, dữ liệu môi giới, tính toán nội bộ), TUYỆT ĐỐI không nêu tên bảng/hệ thống nội bộ (tav2_*, BigQuery, DNSE API, universe_pit...), và 'rủi ro/giới hạn' là giới hạn thị trường/phương pháp, không phải sự cố vận hành. Văn phong theo thông lệ thư nhà đầu tư chuyên nghiệp: luận điểm trước, bằng chứng sau, nêu rủi ro/giới hạn; không sao chép hay gán nhận định cho BlackRock/Bill Ackman. BẮT BUỘC ngay đầu (cả 2 file): 'Toàn cảnh thị trường' tách Technical (xu hướng, hỗ trợ/kháng cự, breadth/thanh khoản/momentum) và Fundamental (định giá, earnings, lãi suất/vĩ mô/dòng tiền), mọi số có as-of/nguồn. Biểu đồ theo chỉ dẫn biểu đồ bên dưới, mỗi biểu đồ có tiêu đề/đơn vị/kỳ/nguồn đầy đủ; thiếu dữ liệu thì nói rõ. Kết thúc bằng 'Outlook tháng tới' tách Technical/Fundamental, trình bày kịch bản, điều kiện xác nhận/bác bỏ và rủi ro, không khẳng định chắc chắn. Format/văn phong tham khảo mẫu ĐÃ TÁCH gần nhất mike/reports/SpaceX_monthly_report_2026-08.md (client-facing) và mike/reports/ZaloPay_monthly_report_2026-08.md (đầy đủ) — KHÔNG dùng mẫu gộp cũ SpaceX_ZaloPay_monthly_report_*.md nữa (deprecated, chỉ còn trên đĩa làm lịch sử). BẮT BUỘC thêm mục 'Paper signals chạy nền — kiểm tra suy giảm theo tháng' cho extreme_regime và fill_timing (hai mục không còn in daily) TRONG FILE ZALOPAY (nội bộ) — mục này là theo dõi R&D nội bộ, KHÔNG đưa vào file SpaceX client-facing: đọc mike/kb/paper_programs_registry.json, journal data/execution_logs/exec_main_*_journal.csv và output probe/charter liên quan; so sánh tháng này với tháng trước về số phiên evidence/lệnh, marker hoặc false-trigger, reject/fail, adherence cửa sổ và fill-vs-open khi đo được, cùng trạng thái gate. Kết luận chỉ là ổn định / chưa đủ dữ liệu / có dấu hiệu suy giảm cần điều tra, nêu số liệu và giới hạn; TUYỆT ĐỐI không coi ít quan sát hay không có trigger là bằng chứng alpha. BẮT BUỘC thêm TIỂU MỤC 'Shadow intraday cutloss — tích luỹ OOS' ngay dưới mục paper signals, CŨNG CHỈ trong FILE ZALOPAY (nội bộ, KHÔNG đưa vào file SpaceX client-facing): chạy lệnh python3 mike/bin/intraday_oos_monthly.py --month <YYYY-MM của kỳ báo cáo> từ WC_ROOT và chép nguyên số của nó (số phiên có log, lượt quét, crash, lỗi giá, phiên thiếu EOD_OOS, ngày có ca live, luỹ kế X/30 ngày có ca). Chỉ báo CÁC SỐ ĐẾM (cổng giá trong phiên vẫn chạy, ghi dữ liệu). LƯU Ý: từ 01/11/2026 (user chốt) cutloss KHÔNG còn tự bán — cổng giá chỉ báo + mở hồ sơ DD khủng hoảng 7 ngày, user tự quyết bán, mặc định GIỮ ⇒ mốc 30 ngày/H1 OOS đã HẾT HIỆU LỰC (không còn gì để chấm): KHÔNG chấm H1, KHÔNG kết luận cutloss tốt/xấu, KHÔNG đề xuất bật tự bán; số ngày có ca chỉ là số đếm thô. Có crash/phiên thiếu EOD_OOS thì nêu rõ. Script lỗi hoặc không có log tháng đó thì ghi 'không đọc được' kèm lý do thật, đừng tự ước lượng. Dùng đúng pipeline verify_account_snapshot.py --account-no + nav_history_{account}.csv thật. Phần Fundamental của 'Toàn cảnh thị trường' lấy dòng DT gate (candidate/streak) từ dna_report.build_dt_gate_line() và Value Radar từ dna_report.build_value_radar_line() (chạy từ WC_ROOT, mike/kb/coding_guidelines.md §6b), KHÔNG tự tính phân vị P/E ad-hoc. ${LIVERMORE_STEP} ${PORTFOLIO_STEP} ${BENCH_STEP} ${CHART_STEP} Có gap/lỗi/residual chưa giải thích được thì NÓI RÕ trong file ZaloPay; với file SpaceX thì trình bày số liệu cuối cùng đã verify, không kể lể quá trình vận hành. Gửi vào Discord Trading report topic (channel ${TRADING_REPORT_THREAD}). ${EMAIL_STEP} ${DELEGATE_STEP} Ghi bus finding khi xong, gồm kết luận market outlook và kết luận monthly review của 2 paper signal (trong file ZaloPay) và sha256 + trạng thái delivery gate của TỪNG file."
  fi
  # `--thread "$TRADING_REPORT_THREAD"` tường minh — xem chú thích cùng ngày trong
  # daily_retro.sh (B1). Đúng topic mà chính PROMPT đã yêu cầu gửi báo cáo vào.
  # MODEL: tuần=sonnet (templated, không cần Opus), tháng=opus (attribution/outlook phức tạp
  # hơn) — chốt 2026-08-04 theo yêu cầu user tiết kiệm chi phí, xem thảo luận Discord cùng ngày.
  # EFFORT (thêm 2026-08-10, token-usage audit item #3): tách theo nhánh — trước đây cả 2 nhánh
  # cùng --effort high dù comment ngay trên nói rõ nhánh tuần "templated, không cần Opus" (hạ
  # model rồi nhưng quên xét lại effort, cùng dạng lệch đã tìm thấy ở Taylor interactive
  # dispatch). Tuần=medium (templated), tháng=high (attribution/outlook thật sự phức tạp hơn).
  PROMPT="NGÂN SÁCH THỜI GIAN: phiên này bị dừng cứng sau ${DISPATCH_TIMEOUT}s. Thứ tự ưu tiên khi thiếu giờ: SpaceX trước ZaloPay; narrative ngắn (headline + key_points) thay vì bỏ báo cáo; KHÔNG chạy lại build khi đã rc=0 chỉ để trau chuốt chữ. ${PROMPT}"
  # Quý: --write-scope 2 file đích ⇒ dispatch.sh từ chối (exit 6) nếu job khác còn sống đang giữ cùng file
  # (watchdog 08:30 hôm sau lúc job 21:00 còn chạy/pending-resume ⇒ không soạn lần 2 ⇒ không email trùng).
  WS_ARGS=(); [ "$KIND" = "quarterly" ] && WS_ARGS=(--write-scope "${TFILE_SX},${TFILE_ZP}")
  "$ROOT/bin/dispatch.sh" Taylor "$PROMPT" --thread "$TRADING_REPORT_THREAD" --bg --model "$MODEL" --effort "$EFFORT" --timeout "$DISPATCH_TIMEOUT" ${WS_ARGS[@]+"${WS_ARGS[@]}"} 2>&1 | tail -5

  # Ghi NGUYÊN TỬ (tmp + os.replace, §5) — cùng khuôn 2 chỗ trên: state cụt do bị kill giữa
  # chừng từng làm ALREADY/ALREADY_ALERTED phía trên vấp; STATE này bị đọc lại bởi mọi lượt
  # cron sau nên cùng rủi ro, sửa đồng bộ.
  STATE="$STATE" PKEY="$PKEY" TODAY="$TODAY" python3 -c "
import json, os, sys, tempfile
path = os.environ['STATE']
try:
    state = json.load(open(path))
    if not isinstance(state, dict):
        raise ValueError('state khong phai dict: %r' % type(state).__name__)
except Exception as e:
    print('check_report_cadence: state cu hong (%s: %s) — dung lai tu {}' % (type(e).__name__, e), file=sys.stderr)
    state = {}
state[os.environ['PKEY']] = os.environ['TODAY']
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix='.report_cadence_dispatched.', suffix='.tmp')
try:
    with os.fdopen(fd, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
except BaseException:
    try:
        os.unlink(tmp)
    except OSError:
        pass
    raise
"
done
