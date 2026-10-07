#!/usr/bin/env bash
# refresh_deposit_cctg_weekly.sh — WEEKLY cross-check of BOTH the Big-4 12M term-deposit rate AND
# the Big-4 CCTG 6M rate, built so a decline shows up within a week instead of waiting for the
# existing monthly Big-4-only refresh (refresh_deposit_rate_vn.sh, still runs separately as its own
# cron job -- NOT replaced by this file, though append_deposit_rate.py itself is a SHARED writer,
# see note below). User directive (2026-10-01, job Taylor_20261001_054108):
#   "Lãi suất huy động tháng sau giảm so với tháng trước. Hoặc chứng chỉ tiền gửi phát hành đợt
#    sau thấp hơn đợt trước. Cần bạn xây dựng cơ chế lấy dữ liệu hàng tuần... gắn vào cron tự động."
#
# Deliberately reuses the EXACT architecture refresh_deposit_rate_vn.sh's auto-write mechanism
# earned through 8 rounds of adversarial review (mike/kb/projects/deposit-rate-autocheck.md) rather
# than inventing a new HTML scraper: a dispatched agent (Winston) WebSearches, cites >=2 structured
# sources, and the MECHANICAL guards live in the writer scripts (append_deposit_rate.py and the
# new append_cctg_rate.py), never in agent self-report. append_deposit_rate.py is NOT a private
# copy of this mechanism -- it is the SAME writer the monthly script calls, so a guard change here
# (round 2: reused-URL sidecar + optional per-source rate check; round 3/B2-1/B2-2, coord job
# Taylor_20261001_064913: URL normalization fix + per-source rate now MANDATORY for any dispatched
# agent) applies to BOTH cadences at once -- refresh_deposit_rate_vn.sh's own prompt has been
# updated alongside each of these to keep citing what its writer now requires. See
# append_cctg_rate.py's docstring for the one genuine CCTG-only enhancement: its --sources entries
# must each carry their own cited rate UNCONDITIONALLY (not just when JOB_ID is set), cross-checked
# to agree within 0.1pp before a write is allowed.
#
# Fail-closed by construction, same as the monthly script: no evidence / disagreement / stale
# source / owner-group collision -> the writer script refuses the write outright (rc!=0, no CSV
# change) and this wrapper's post-condition check falls back to a plain manual-review reminder.
#
# Trend detection (the actual point of doing this WEEKLY, not just monthly): regardless of whether
# this week's dispatch wrote anything, ALWAYS run deposit_cctg_trend_check.py at the end — it reads
# whatever is currently on disk (frozen anchors + CSV, from ANY source: this script, the monthly
# Big-4 refresh, or a manual append) and raises a WARNING-ONLY alert if the latest anchor is below
# the prior one for either series. It NEVER writes to a series CSV and NEVER touches park/sizing —
# park 0% reversal is a user-only decision (CLAUDE.md macro-killswitch section).
#
# Schedule: Monday 08:00 ICT (= 01:00 UTC same day; host crontab is Etc/UTC, see
# kb/cron_registry.md's note on CRON_TZ vs the TZ= env line) — before run_bot 09:05.
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"

# --dry-run: skip the real Winston dispatch (no WebSearch session spawned, no bus event written
# under its name) and run trend_check in --dry-run too (no notify/bus/state write) — lets a human
# verify the mechanical pieces (env, CUR_DEP/CUR_CCTG extraction, log path, trend check logic)
# before installing the cron line, without burning a real dispatch.
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
RUN_START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
LOG="data/refresh_deposit_cctg_weekly_$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m).log"
echo "===== deposit+CCTG weekly refresh START ${RUN_START_UTC} (ICT ${TODAY}) =====" >> "$LOG"

CUR_DEP="$($PY -c 'from deposit_rate_vn import current_deposit_rate; print(f"{current_deposit_rate():.2f}")' 2>>"$LOG")" || CUR_DEP="?"
CUR_CCTG="$($PY -c 'from cctg_rate_vn import current_cctg_rate; r,_=current_cctg_rate(); print(f"{r:.2f}" if r is not None else "none")' 2>>"$LOG")" || CUR_CCTG="?"
echo "current_deposit_rate() = ${CUR_DEP}% | current_cctg_rate() = ${CUR_CCTG}%" >> "$LOG"

if [ "$DRY_RUN" -eq 0 ] && [ -x "$WORKDIR_8L/mike/bin/append_event.sh" ]; then
  "$WORKDIR_8L/mike/bin/append_event.sh" Winston status "deposit-cctg-weekly-dispatch" \
    "{\"date\":\"${TODAY}\",\"current_deposit\":\"${CUR_DEP}\",\"current_cctg\":\"${CUR_CCTG}\"}" >> "$LOG" 2>&1 || true
fi

PROMPT="Xác nhận lãi suất HÀNG TUẦN cho 2 chuỗi — Big-4 12 tháng (tiết kiệm, kênh ONLINE) và Big-4 CCTG 12 tháng cao nhất (chứng chỉ tiền gửi). Ngày ${TODAY}. Giá trị hiện đang dùng: Big-4 12M = ${CUR_DEP}%, CCTG (12M cao nhất; 6M trước 05/10) = ${CUR_CCTG}%.

=== CHUỖI 1: Big-4 12 THÁNG (tiết kiệm, kênh online) ===
TIÊU CHUẨN (CÙNG owner-group/recency guard cơ chế THÁNG hiện có — nhưng chuỗi TUẦN này THÊM yêu
cầu per-source rate citation giống hệt chuỗi 2, vì chạy 4 lần/tháng thay vì 1 lần nên phơi nhiễm
cao hơn; cơ chế THÁNG (refresh_deposit_rate_vn.sh) giữ nguyên KHÔNG đổi, prompt riêng của nó):
1. WebSearch nguồn có NGÀY CỤ THỂ (trong ~25 ngày) nêu lãi suất tiết kiệm 12 tháng Big-4 (Agribank/Vietcombank/BIDV/VietinBank). KÊNH (user chốt 2026-10-05): nguồn nêu cả ONLINE lẫn TẠI QUẦY khác nhau cho cùng ngân hàng ⇒ lấy số CAO NHẤT trong hai kênh làm số của ngân hàng đó (số quầy thấp hơn/lẻ tẻ KHÔNG phải lý do escalate).
2. Cần >=2 nguồn ĐỘC LẬP (khác nhóm sở hữu — vd cafef/kenh14/soha đều VCCorp tính là 1). append_deposit_rate.py tự soi domain, từ chối nếu không đủ.
3. MỖI nguồn PHẢI ghi RÕ con số % nó báo (field 'rate' trong --sources bên dưới) — append_deposit_rate.py sẽ TỰ SO các số này, từ chối ghi nếu lệch nhau >0,1 điểm %. Nếu các nguồn cho số khác nhau quá 0,1pp, đó LÀ escalate, không tự chọn 1 số.
4. --rate bạn truyền PHẢI khớp (gần như tuyệt đối) với MỘT trong các số đã cite trong --sources — không được tự tổng hợp/làm tròn thành số không nguồn nào nói.
5. 1/4 ngân hàng lệch so với 3 còn lại -> dùng MODE (đa số 3/4), KHÔNG escalate riêng trường hợp này (áp dụng ở bước CHỌN ngân hàng để cite, không phải ở bước so 2 nguồn CÙNG 1 ngân hàng).
6. Chỉ escalate khi: không đủ 3/4 đồng thuận, HOẶC 1 ngân hàng có 2 nguồn báo 2 số khác nhau >0,1pp, HOẶC không tìm được nguồn đủ mới.
Ghi (nếu có số xác nhận): python3 append_deposit_rate.py --rate <X> --effective ${TODAY} --source web_crosscheck_auto --collected ${TODAY} --note \"<tóm tắt>\" --sources '[{\"publisher\":\"<tên>\",\"url\":\"<url>\",\"date\":\"<YYYY-MM-DD>\",\"rate\":<X>}, ...]'

=== CHUỖI 2: Big-4 CCTG 12 THÁNG, lấy CAO NHẤT các ngân hàng Big-4 (chứng chỉ tiền gửi) ===
TIÊU CHUẨN (KHÁC chuỗi 1 — chuỗi này MỚI, guard CHẶT HƠN):
1. WebSearch nguồn có NGÀY CỤ THỂ (trong ~25 ngày) nêu lãi suất CCTG kỳ hạn 12 THÁNG của nhóm Big-4 (Agribank/Vietcombank/BIDV/VietinBank). QUY TẮC (user chốt 2026-10-05): ngân hàng Big-4 nào CÓ CCTG 12 tháng thì lấy số của nó; trong các ngân hàng đó lấy lãi suất CAO NHẤT làm chuẩn (KHÔNG cần đủ 4/4 ngân hàng, KHÔNG dùng mode/đồng thuận). Ngân hàng chỉ có kỳ hạn khác (vd VCB chỉ phát 6 tháng) thì KHÔNG tính; bảng nào điền sẵn 12 tháng cho NH mà các nguồn khác nói NH đó không phát 12 tháng thì coi là KHÔNG đáng tin và bỏ số đó. CHỈ khi KHÔNG Big-4 nào có CCTG 12 tháng mới được rơi về 6 tháng cao nhất — và phải ghi rõ trong --note là rơi về 6 tháng. KHÔNG lấy ngân hàng cổ phần khác. --note luôn nêu: ngân hàng nào, kỳ hạn nào, vì sao là cao nhất.
2. Cần >=2 nguồn ĐỘC LẬP khác nhóm sở hữu — GIỐNG chuỗi 1.
3. MỖI nguồn PHẢI ghi RÕ con số % nó báo (field 'rate' trong --sources bên dưới) — append_cctg_rate.py sẽ TỰ SO 2 số này, từ chối ghi nếu lệch nhau >0,1 điểm %. Nếu 2 nguồn cho 2 số khác nhau quá 0,1pp, đó LÀ escalate, không tự chọn 1 số.
4. --rate bạn truyền PHẢI khớp (gần như tuyệt đối) với MỘT trong các số đã cite trong --sources — không được tự tổng hợp/làm tròn thành số không nguồn nào nói.
Ghi (nếu có số xác nhận): python3 append_cctg_rate.py --rate <X> --effective ${TODAY} --source web_crosscheck_auto --collected ${TODAY} --note \"<tóm tắt>\" --sources '[{\"publisher\":\"<tên>\",\"url\":\"<url>\",\"date\":\"<YYYY-MM-DD>\",\"rate\":<X>}, ...]'

=== CHUỖI 3: Big-4 CCTG 6 THÁNG, lấy CAO NHẤT các ngân hàng Big-4 (chuỗi PHỤ, user duyệt 2026-10-07) ===
Mục đích: Bobby đọc đa-proxy chi phí vốn (CCTG 6M vs 12M vs tiết kiệm). Chuỗi này ghi FILE RIÊNG, KHÔNG vào effective rate / kill-switch A / DCF.
TIÊU CHUẨN: y hệt chuỗi 2 (>=2 nguồn khác chủ, mỗi nguồn ghi rõ số, lệch <=0,1pp, --rate khớp 1 số đã cite) nhưng kỳ hạn 6 THÁNG: trong các ngân hàng Big-4 CÓ phát CCTG 6 tháng (vd VCB 6 tháng), lấy lãi suất CAO NHẤT. Nếu ngân hàng niêm yết theo dải kỳ hạn (vd \"6-11 tháng\"), dải đó tính là có 6 tháng. --note nêu ngân hàng nào, vì sao cao nhất, và liệt kê số 6 tháng của các Big-4 khác nếu nguồn có.
Ghi (nếu có số xác nhận): python3 append_cctg_rate.py --series 6m --rate <X> --effective ${TODAY} --source web_crosscheck_auto --collected ${TODAY} --note \"<tóm tắt>\" --sources '[{\"publisher\":\"<tên>\",\"url\":\"<url>\",\"date\":\"<YYYY-MM-DD>\",\"rate\":<X>}, ...]'
⚠️ Nguồn đã dùng cho chuỗi 2 dùng lại được cho chuỗi 3 (sidecar URL hai chuỗi tách riêng).

CẢ 3 LỆNH TRÊN tự chặn (KHÔNG PHẢI bạn tự quyết định) nếu: thiếu nguồn, nguồn cùng nhóm sở hữu, nguồn quá cũ, lệch quá ngưỡng so với giá trị hiện tại (1,0pp), hoặc 2 nguồn lệch nhau >0,1pp (MỌI chuỗi — chuỗi 1 có guard này KHÁC cơ chế tháng). Gặp bất kỳ lỗi nào trong các trường hợp này — ĐỪNG thử flag khác, escalate ngay kèm nguyên văn lỗi script. --force KHÔNG dùng được trong phiên headless của bạn.

Idempotent — nếu hôm nay đã ghi rồi (effective_date trùng), lệnh tự SKIP rc=0, không lỗi, coi là hoàn thành bình thường. Có thể 1 chuỗi ghi được, chuỗi kia escalate — xử lý ĐỘC LẬP, không phải tất-cả-hoặc-không-gì.

BẮT BUỘC HÀNH ĐỘNG CUỐI (để Mike xác minh job này đã xử lý, không treo giữa chừng) — với MỖI chuỗi (1, 2 và 3), chọn ĐÚNG MỘT:
  - Chạy thành công (kể cả SKIP idempotent): 'mike/bin/append_event.sh Winston status deposit-cctg-weekly-done \"<JSON: series, rate, changed true/false, note>\"'.
  - Escalate: 'mike/bin/append_event.sh Winston question deposit-cctg-weekly-question \"<JSON tóm tắt chuỗi nào, số nào mâu thuẫn>\"'.
(Dù các chuỗi đều escalate hoặc đều done, vẫn gọi riêng mỗi chuỗi 1 event — field series = big4_12m / cctg_12m / cctg_6m — để Mike tách được chuỗi nào ổn, chuỗi nào cần xem.)

BÁO CÁO NGAY TRONG NGÀY vào Discord Trading Daily (notify.sh) — dù ĐỔI hay KHÔNG ĐỔI cho mỗi chuỗi, nêu rõ 2 loại ngày (ngày xác nhận ${TODAY} vs ngày nguồn công bố thật trong --sources), báo CẢ CCTG 6 tháng (chuỗi 3) cạnh CCTG 12 tháng, và với CCTG luôn ghi rõ ngân hàng + kỳ hạn của số được chọn (chuẩn 12 THÁNG cao nhất Big-4 từ 2026-10-05; trước đó chuỗi là 6 tháng — đừng gộp lẫn khi báo cáo)."

if [ "$DRY_RUN" -eq 1 ]; then
  echo "[--dry-run] skipping real dispatch.sh call; prompt length=${#PROMPT} chars" >> "$LOG"
  echo "[--dry-run] skipping real dispatch.sh call; prompt length=${#PROMPT} chars"
  DISPATCH_RC=0
else
  DISCORD_THREAD_ID="1521470705563340910" "$WORKDIR_8L/mike/bin/dispatch.sh" Winston "$PROMPT" >> "$LOG" 2>&1
  DISPATCH_RC=$?
fi
echo "dispatch.sh Winston exit_code=${DISPATCH_RC} (dry_run=${DRY_RUN})" >> "$LOG"

# --- post-condition check: did Winston actually signal an outcome for this run? ---
# (meaningless in --dry-run since nothing was dispatched; skip straight to "no" without reading
# the real inbox, so a dry run never gets mistaken for yesterday's unrelated Winston activity)
if [ "$DRY_RUN" -eq 1 ]; then
  CONFIRMED="no"
else
CONFIRMED="$($PY - "$RUN_START_UTC" <<'PYEOF' 2>>"$LOG"
import json, sys
from datetime import datetime
start = datetime.strptime(sys.argv[1], "%Y-%m-%dT%H:%M:%SZ")
path = "mike/bus/inbox/Winston.jsonl"
allowed = {"deposit-cctg-weekly-done": "status", "deposit-cctg-weekly-question": "question"}
found = False
try:
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            topic = rec.get("topic")
            if topic not in allowed or rec.get("event_type") != allowed[topic]:
                continue
            ts = rec.get("ts", "")
            try:
                rts = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                continue
            if rts >= start:
                found = True
    print("yes" if found else "no")
except FileNotFoundError:
    print("no")
PYEOF
)"
fi
echo "post-condition check (deposit-cctg-weekly-done/question found after run start): ${CONFIRMED:-no} (dry_run=${DRY_RUN})" >> "$LOG"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "[--dry-run] skipping fallback-notify branch" >> "$LOG"
elif [ "$DISPATCH_RC" -eq 5 ]; then
  echo "dispatch queued for usage-limit auto-resume (rc=5) — no fallback" >> "$LOG"
elif [ "$DISPATCH_RC" -ne 0 ] || [ "${CONFIRMED:-no}" != "yes" ]; then
  MSG="⚠️ Tự động xác nhận lãi suất huy động + CCTG tuần này (${TODAY}) KHÔNG có kết quả xác nhận được (dispatch exit=${DISPATCH_RC}, post-condition=${CONFIRMED:-no}) — rơi về nhắc thủ công.
Giá trị đang dùng: Big-4 12M = ${CUR_DEP}%, CCTG (12M cao nhất; 6M trước 05/10) = ${CUR_CCTG}%.
Nếu đã đổi, chạy (số phải xác nhận thật):
  python3 append_deposit_rate.py --rate <X> --effective ${TODAY} --source manual_verify
  python3 append_cctg_rate.py --rate <X> --effective ${TODAY} --source manual_verify"
  if [ -x "$WORKDIR_8L/mike/bin/notify_thread.sh" ]; then
    "$WORKDIR_8L/mike/bin/notify_thread.sh" "$MSG" trading_daily >> "$LOG" 2>&1 || true
  fi
fi

# --- trend check: ALWAYS runs, independent of dispatch outcome above (reads whatever is on disk
# right now — catches a decline that entered via the monthly Big-4 refresh or a manual append too,
# not just this script's own writes) ---
echo "--- trend check ---" >> "$LOG"
if [ "$DRY_RUN" -eq 1 ]; then
  "$PY" deposit_cctg_trend_check.py --dry-run >> "$LOG" 2>&1
else
  "$PY" deposit_cctg_trend_check.py >> "$LOG" 2>&1
fi
TREND_RC=$?
echo "trend check exit_code=${TREND_RC}" >> "$LOG"

# TREND_RC != 0 (real crash, e.g. corrupt CSV -- OR the trend check's own internal notify/bus
# channel failed for some declines/staleness it found -- see deposit_cctg_trend_check.py's
# any_failed) used to be silently absorbed by this wrapper's unconditional `exit 0`: the log got
# one line nobody reads on a cadence, and the user received NOTHING (coord job
# Taylor_20261001_061238 item B1 fix). Surface it loudly instead, and make the wrapper's own exit
# code reflect it so cron's own failure handling (if any) sees it too.
if [ "$TREND_RC" -ne 0 ]; then
  if [ "$DRY_RUN" -eq 0 ] && [ -x "$WORKDIR_8L/mike/bin/notify_thread.sh" ]; then
    TREND_TAIL="$(tail -c 1500 "$LOG")"
    "$WORKDIR_8L/mike/bin/notify_thread.sh" \
      "🔴 deposit_cctg_trend_check.py LỖI (exit=${TREND_RC}, ${TODAY}) — cảnh báo xu hướng hạ lãi suất/CCTG tuần này CÓ THỂ ĐÃ KHÔNG được gửi đầy đủ. Log: ${LOG}
Cuối log:
${TREND_TAIL}" \
      trading_daily >> "$LOG" 2>&1 || true
  else
    echo "[--dry-run or notify_thread.sh missing] trend check failed (exit=${TREND_RC}) — skipping live notify" >> "$LOG"
  fi
fi

echo "===== deposit+CCTG weekly refresh DONE (dispatch_rc=${DISPATCH_RC}, confirmed=${CONFIRMED:-no}, trend_rc=${TREND_RC}, dry_run=${DRY_RUN}) =====" >> "$LOG"
[ "$TREND_RC" -eq 0 ] || exit 1
exit 0
