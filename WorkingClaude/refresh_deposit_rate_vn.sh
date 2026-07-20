#!/usr/bin/env bash
# refresh_deposit_rate_vn.sh — MONTHLY auto-confirm of the Big-4 12M deposit rate.
#
# Layer A of proposal_deposit_rate_monthly_refresh_20260713.md (§3, user-approved 2026-07-17)
# + auto-crosscheck upgrade (user-approved 2026-07-20, mike/kb/projects/deposit-rate-autocheck.md,
#   quant-skeptic REFUTED 8 rounds, CONFIRMED after fixes — full adversarial history there).
# Briefly reverted to notify-only same day (2026-07-20, mid-review, before round 10 converged),
# then RE-ENABLED same day once the user reviewed the final CONFIRMED design + the real
# current_deposit_rate() bug the review process caught:
#   - best-effort direct scrape (CafeF/VCB, short timeout, known low success) as a cheap first try,
#   - THEN dispatch Winston to WebSearch-crosscheck the Big-4 12M ONLINE rate. append_deposit_rate.py
#     MECHANICALLY enforces (not just agent-self-reported): (a) >=2 sources from >=2 DISTINCT owner
#     groups via --sources JSON (sister-site clusters like VCCorp count as one), (b) a delta guard
#     refusing any write >=1.0pp from EITHER the current value OR the last human-confirmed anchor
#     (bounds cumulative drift), (c) --force/--source/--collected/--effective are all bound to
#     JOB_ID (caller identity), never to a self-declared flag — an agent cannot talk its way past
#     any guard, only a real interactive human can override,
#   - if evidence is ambiguous/stale/too-few-owners, OR any guard refuses the write, Winston
#     escalates (bus `question` topic deposit-rate-refresh-question) instead of retrying/guessing,
#   - POST-CONDITION CHECK (closes "dispatch rc=0 but agent did nothing"): after dispatch, this
#     script greps Winston's own bus inbox for a `deposit-rate-refresh-done` (event_type=status) or
#     `deposit-rate-refresh-question` (event_type=question) event timestamped AFTER this run
#     started. Neither found -> fall back to the plain manual reminder. rc=5 (usage-limit-queued,
#     self-resuming via resume_pending.py) is carved out of this fallback — it is not a failure.
#   - SAME-DAY REPORT, ALWAYS (user directive 2026-07-20, revising the earlier quiet-heartbeat
#     design): every month Winston confirms a result — changed OR unchanged — it posts to Trading
#     Daily the same day, clearly marked as freshly-confirmed data (not just a done-event on the
#     bus). No more "stay quiet if unchanged."
#
# deposit_rate_vn.current_deposit_rate() is a LIVE production input (rating_8l.py NEUTRAL tilt).
#
# Schedule: day 3 of month, 08:10 ICT (before the DCF refresh-gate consumes it around day 11).
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"

MONTH="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m)"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
RUN_START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
LOG="data/refresh_deposit_rate_vn_$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m).log"
echo "===== deposit-rate refresh START ${RUN_START_UTC} (ICT ${TODAY}) =====" >> "$LOG"

# current live value (frozen anchors + any CSV appends)
CUR="$($PY -c 'from deposit_rate_vn import current_deposit_rate; print(f"{current_deposit_rate():.2f}")' 2>>"$LOG")" || CUR="?"
echo "current_deposit_rate() = ${CUR}%" >> "$LOG"

# cheap best-effort direct fetch first (CafeF table is JS-rendered, success EXPECTED to fail —
# kept only in case the page ever changes; feeds Winston's dispatch as a starting hint, not trusted)
HINT="$($PY - <<'PYEOF' 2>>"$LOG"
import re, sys
try:
    import urllib.request
    req = urllib.request.Request(
        "https://cafef.vn/du-lieu/lai-suat-ngan-hang.chn",
        headers={"User-Agent": "Mozilla/5.0 (deposit-rate-refresh best-effort)"})
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
    m = re.search(r"12\s*th[aá]ng.{0,80}?(\d(?:[.,]\d)?)\s*%", html, re.I | re.S)
    if m:
        print(m.group(1).replace(",", "."))
except Exception as e:
    print(f"fetch failed: {e}", file=sys.stderr)
PYEOF
)"
HINT="$(printf '%s' "$HINT" | tr -d '[:space:]')"
echo "direct fetch hint = '${HINT:-<none>}'" >> "$LOG"

# breadcrumb: dispatch is starting this month's autocheck
if [ -x "$WORKDIR_8L/mike/bin/append_event.sh" ]; then
  "$WORKDIR_8L/mike/bin/append_event.sh" Winston status "deposit-rate-refresh-dispatch" \
    "{\"month\":\"${MONTH}\",\"current\":\"${CUR}\",\"direct_fetch_hint\":\"${HINT:-none}\"}" >> "$LOG" 2>&1 || true
fi

PROMPT="Xác nhận lãi suất tiết kiệm 12 tháng Big-4 (Agribank/Vietcombank/BIDV/VietinBank), KÊNH ONLINE, cho tháng ${MONTH}. Giá trị hiện đang dùng (live, input rating_8l NEUTRAL tilt): ${CUR}%.

TIÊU CHUẨN BẮT BUỘC trước khi ghi (KHÔNG được đoán, sai 1 lần là ảnh hưởng production):
1. WebSearch tìm nguồn có NGÀY CỤ THỂ (trong vòng ~25 ngày gần đây) nêu lãi suất tiết kiệm 12 tháng Big-4.
2. Số phải RÕ RÀNG là kỳ hạn 12 tháng, KÊNH ONLINE/trực tuyến (không phải quầy, không phải kỳ hạn khác 6/24 tháng) — nếu nguồn không ghi rõ kênh/kỳ hạn, KHÔNG dùng số đó.
3. Cần ít nhất 2 nguồn mà bạn tin là độc lập (khác toà soạn). LƯU Ý: bạn KHÔNG phải là bên quyết định độ độc lập cuối cùng — append_deposit_rate.py sẽ TỰ KIỂM lại domain của --sources bạn cung cấp và từ chối ghi nếu chúng cùng 1 nhóm sở hữu (vd cafef.vn/kenh14.vn/soha.vn/genk.vn đều là VCCorp, KHÔNG tính là 2 nguồn dù khác domain) — đây là cơ chế script tự chặn, không phải bạn tự phán đoán, nên cứ liệt kê --sources trung thực, script sẽ báo lỗi rõ nếu không đủ.
4. Nếu các nguồn MÂU THUẪN nhau, hoặc không tìm được nguồn đủ mới/đủ rõ — TUYỆT ĐỐI KHÔNG ghi. Escalate: gọi 'mike/bin/append_event.sh Winston question deposit-rate-refresh-question \"<JSON tóm tắt các số/nguồn mâu thuẫn tìm được>\"' rồi notify.sh báo Trading Daily.

Chạy: python3 append_deposit_rate.py --rate <X> --effective ${TODAY} --source web_crosscheck_auto --collected ${TODAY} --note \"<tóm tắt ngắn>\" --sources '[{\"publisher\":\"<tên>\",\"url\":\"<url đầy đủ>\",\"date\":\"<YYYY-MM-DD>\"}, ...]' (liệt kê MỌI nguồn bạn dùng, tối thiểu 2 phần tử, url phải đầy đủ để script tự soi domain).

Lệnh này tự động từ chối ghi (KHÔNG PHẢI bạn tự quyết định) trong các trường hợp sau — nếu gặp bất kỳ lỗi nào trong 3 trường hợp này, ĐỪNG thử flag khác/số khác, hãy escalate ngay theo mục 4 kèm nguyên văn lỗi script trả về:
  a. --sources không đủ 2 nhóm sở hữu độc lập (script tự soi domain, xem mục 3),
  b. --note rỗng,
  c. số lệch >= 1.0 điểm %% so với ${CUR}%% hiện tại — --force KHÔNG dùng được trong phiên headless của bạn (script tự chặn theo JOB_ID môi trường, không phải theo --source), nên lệch >=1.0pp LUÔN cần escalate, không có cách nào khác để ghi được.

Lệnh idempotent — nếu hôm nay đã có người ghi rồi (effective_date trùng), lệnh tự SKIP rc=0, không lỗi — đây KHÔNG phải escalation, coi là hoàn thành bình thường.

BẮT BUỘC HÀNH ĐỘNG CUỐI CÙNG (để Mike xác minh được job này đã thực sự xử lý, không phải treo giữa chừng) — chọn ĐÚNG MỘT trong 2, không được bỏ qua bước này dù kết quả là gì ở trên:
  - Nếu append_deposit_rate.py chạy thành công (kể cả SKIP idempotent): gọi 'mike/bin/append_event.sh Winston status deposit-rate-refresh-done \"<JSON: rate, changed true/false, note ngắn>\"'.
  - Nếu escalate (mục 4, hoặc script từ chối vì a/b/c ở trên): gọi 'mike/bin/append_event.sh Winston question deposit-rate-refresh-question \"<JSON tóm tắt>\"' (chỉ 1 trong 2, không gọi cả hai).

BÁO CÁO NGAY TRONG NGÀY, LUÔN LUÔN (user chỉ đạo 2026-07-20 — KHÔNG áp dụng quiet-heartbeat cho mục này nữa, khác với các cron khác của team): dù rate ĐỔI hay KHÔNG ĐỔI, bạn PHẢI tự gọi notify.sh để báo Trading Daily NGAY hôm nay, mở đầu tin nhắn bằng dòng highlight rõ ràng đây là dữ liệu MỚI vừa xác nhận hôm nay, không phải số cũ còn hiệu lực — dùng đúng mẫu:
  - Nếu KHÔNG đổi: '🆕 XÁC NHẬN LÃI SUẤT ${MONTH} (mới cập nhật hôm nay ${TODAY}): Big-4 12 tháng online VẪN GIỮ ${CUR}%/năm — đã kiểm chứng qua N nguồn độc lập.' + liệt kê ngắn gọn nguồn.
  - Nếu ĐÃ GHI một số MỚI: '🆕 LÃI SUẤT THAY ĐỔI (mới cập nhật hôm nay ${TODAY}): ${CUR}%→X%/năm.' + lý do/nguồn ngắn gọn.
  - Nếu escalate (mục 4): tin nhắn 'question' đã tự đủ rõ, không cần thêm dòng highlight riêng.

Gợi ý tham khảo (KHÔNG tin tưởng, chỉ là điểm khởi đầu — nguồn CafeF JS-render nên fetch trực tiếp thường fail): direct fetch hint = '${HINT:-không có}'."

DISCORD_THREAD_ID="1521470705563340910" "$WORKDIR_8L/mike/bin/dispatch.sh" Winston "$PROMPT" >> "$LOG" 2>&1
DISPATCH_RC=$?
echo "dispatch.sh Winston exit_code=${DISPATCH_RC}" >> "$LOG"

# --- post-condition check: did Winston actually signal an outcome, not just "session ended"? ---
# Checks BOTH topic AND event_type match the documented contract (status/done, question/question).
CONFIRMED="$($PY - "$RUN_START_UTC" <<'PYEOF' 2>>"$LOG"
import json, sys
from datetime import datetime
start = datetime.strptime(sys.argv[1], "%Y-%m-%dT%H:%M:%SZ")
path = "mike/bus/inbox/Winston.jsonl"
allowed = {"deposit-rate-refresh-done": "status", "deposit-rate-refresh-question": "question"}
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
echo "post-condition check (deposit-rate-refresh-done[status]/question[question] found after run start): ${CONFIRMED:-no}" >> "$LOG"

# fallback logic:
#   rc=5 (usage-limit-queued) -> NOT a failure, resume_pending.py will retry automatically later;
#     never fire the fallback for this case regardless of CONFIRMED (it hasn't run yet).
#   any other non-zero rc, OR rc=0 with no matching post-condition event -> silently-skipped month
#     unless we post the old plain reminder ourselves.
if [ "$DISPATCH_RC" -eq 5 ]; then
  echo "dispatch queued for usage-limit auto-resume (rc=5) — no fallback, resume_pending.py will retry" >> "$LOG"
elif [ "$DISPATCH_RC" -ne 0 ] || [ "${CONFIRMED:-no}" != "yes" ]; then
  MSG="⚠️ Tự động xác nhận lãi suất tiết kiệm tháng ${MONTH} KHÔNG có kết quả xác nhận được (dispatch exit=${DISPATCH_RC}, post-condition=${CONFIRMED:-no}) — rơi về nhắc thủ công.
Giá trị đang dùng (live, input rating_8l NEUTRAL tilt): ${CUR}%.
Nếu lãi suất đã đổi, chạy (số phải xác nhận thật):
  python3 append_deposit_rate.py --rate <X> --effective ${TODAY} --source manual_verify"
  if [ -x "$WORKDIR_8L/mike/bin/notify.sh" ]; then
    "$WORKDIR_8L/mike/bin/notify.sh" "$MSG" >> "$LOG" 2>&1 || true
  fi
fi

echo "===== deposit-rate refresh DONE (dispatch_rc=${DISPATCH_RC}, confirmed=${CONFIRMED:-no}, current_before=${CUR}%) =====" >> "$LOG"
exit 0
