#!/usr/bin/env bash
# custom30v_rebalance_watch.sh — xác nhận tav2_bq.custom30v_8l ĐÃ rebalance đúng lịch quý
# (q2m5: phiên giao dịch đầu tiên từ ngày 5 tháng {2,5,8,11}), thay vì im lặng chờ ai đó
# hỏi. Writer (custom30_history.py, papertrade_daily.sh step [6b], 15:30 ICT hàng ngày) từng
# mồ côi lặng lẽ 2026-06-18→07-11 (3,5 tuần không ai biết, xem
# mike/kb/data_registry/custom30/custom30v_8l.md). Bảng này là "role: production parking
# (money-path)" — rebalance trễ = custom30V (30% idle-pool parking) giữ mã cũ quá hạn.
#
# Cơ chế: hôm nay >= ngày trigger quý này (05 của tháng 2/5/8/11, dịch tới phiên giao dịch
# đầu tiên) → kỳ vọng MAX(rebal_date) trong bảng đã nhích lên >= ngày đó. Chưa nhích ngày đầu
# = ⚠️ WARN (đủ để thấy, chưa đủ để báo động — writer đo được hoàn tất ~15:33 ICT, cron này
# chạy 16:05 ICT nên hiếm khi false-positive do timing); chưa nhích SANG NGÀY THỨ 2 = 🔴 RED.
set -uo pipefail
export PATH="/home/trido/google-cloud-sdk/bin:$PATH"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# CLOUDSDK_CONFIG: cron KHÔNG có nó => gcloud rơi về ~/.config/gcloud (scope hỏng) và `bq` fail
# auth. wc_env.sh là nguồn chuẩn tắc của biến này — đừng hardcode lại đường dẫn.
# shellcheck source=/dev/null
[ -f "$ROOT/../wc_env.sh" ] && . "$ROOT/../wc_env.sh" >/dev/null 2>&1
TRADING_DAILY_THREAD="trading_daily"
TODAY="$(TZ=Asia/Ho_Chi_Minh date +%Y-%m-%d)"
STATE="$ROOT/state/custom30v_rebalance_streak.json"
mkdir -p "$ROOT/state"
[ -f "$STATE" ] || echo '{"streak": 0, "last_bad_date": null, "last_expected_trigger": null}' > "$STATE"

_notify() {
  "$ROOT/bin/notify_thread.sh" "$1" "$TRADING_DAILY_THREAD" 2>/dev/null || true
}

# Ngày trigger q2m5 GẦN NHẤT đã qua (tháng {2,5,8,11}, ngày 5) tính tới hôm nay — không cần
# lịch giao dịch chính xác tuyệt đối (holiday hiếm quanh các mốc này): nếu ngày 5 rơi cuối
# tuần thì +1..+2 ngày là đủ margin, cron chạy hàng ngày nên tự bắt kịp hôm sau. Theo cách
# tính này EXPECTED_TRIGGER luôn <= TODAY (là trigger GẦN NHẤT trong quá khứ), nên bảng phải
# LUÔN phản ánh ít nhất tới ngày đó.
EXPECTED_TRIGGER="$(python3 -c "
import datetime as dt
today = dt.date.fromisoformat('$TODAY')
months = [2, 5, 8, 11]
candidates = []
for y in (today.year - 1, today.year):
    for m in months:
        d = dt.date(y, m, 5)
        if d <= today:
            candidates.append(d)
print(max(candidates).isoformat())
")"

# ⚠️ `bq` in lỗi ra STDOUT (không phải stderr) — xem kb/incidents/2026-08/2026-08-29-bq-error-
# on-stdout-empty-diagnosis.md. Nên `2>/dev/null | tail -1` cũ trả về DÒNG CUỐI CỦA THÔNG ĐIỆP
# LỖI ("to select an already authenticated account to use.") — chuỗi KHÔNG rỗng, lọt qua guard
# `-z`, rồi so `"to select…" < "2026-08-05"` sai (lexical "t" > "2") ⇒ nhánh "Healthy, im lặng".
# Watchdog money-path báo KHỎE khi thực ra nó mù. Vì vậy: giữ nguyên output (cả 2 kênh), kiểm rc,
# và bắt buộc MAX_REBAL khớp ĐÚNG dạng ngày trước khi đem đi so sánh.
BQ_OUT="$(bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --quiet \
  'SELECT MAX(rebal_date) FROM tav2_bq.custom30v_8l' 2>&1)"
BQ_RC=$?
MAX_REBAL="$(printf '%s\n' "$BQ_OUT" | tail -1)"

if [ "$BQ_RC" -ne 0 ] || ! printf '%s' "$MAX_REBAL" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
  _notify "🔴 **custom30v_rebalance_watch ($TODAY)** — không đọc được MAX(rebal_date) từ tav2_bq.custom30v_8l (bq rc=$BQ_RC). Output thật của bq: $(printf '%s' "$BQ_OUT" | tr '\n' ' ' | cut -c1-400)"
  exit 1
fi

if [ "$MAX_REBAL" \< "$EXPECTED_TRIGGER" ]; then
  STREAK="$(python3 -c "
import json
p = '$STATE'
s = json.load(open(p))
if s.get('last_expected_trigger') != '$EXPECTED_TRIGGER':
    s['streak'] = 0  # trigger quý mới -> reset đếm từ đầu
if s.get('last_bad_date') != '$TODAY':
    s['streak'] = s.get('streak', 0) + 1
    s['last_bad_date'] = '$TODAY'
    s['last_expected_trigger'] = '$EXPECTED_TRIGGER'
    json.dump(s, open(p, 'w'), indent=1)
print(s['streak'])
")"
  if [ "$STREAK" -ge 2 ]; then
    _notify "🔴 **custom30v_rebalance_watch ($TODAY)** — ${STREAK} ngày liên tiếp MAX(rebal_date) trong tav2_bq.custom30v_8l vẫn = ${MAX_REBAL}, CHƯA nhích lên ngày trigger quý này (${EXPECTED_TRIGGER}). custom30_history.py (papertrade_daily.sh step [6b]) có thể đã mồ côi lại (đúng dạng sự cố 06-18→07-11). Đây là bảng money-path (30% idle-pool parking) — cần kiểm tra ngay."
  else
    _notify "⚠️ **custom30v_rebalance_watch ($TODAY)** — MAX(rebal_date) trong tav2_bq.custom30v_8l vẫn = ${MAX_REBAL}, chưa nhích lên ngày trigger quý này (${EXPECTED_TRIGGER}). Ngày đầu tiên trong streak — sẽ báo RED nếu vẫn chưa cập nhật ngày mai."
  fi
  exit 1
fi

# Healthy — reset streak, im lặng.
echo '{"streak": 0, "last_bad_date": null, "last_expected_trigger": null}' > "$STATE"
exit 0
