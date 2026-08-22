#!/usr/bin/env bash
# daily_retro.sh — 00:30 ICT (dời từ 22:00, 2026-07-10 — sau khi cập nhật giờ chạy EOD
# pipeline: daily_refresh 18:30 -> bq_freshness_check 19:00 -> send_plan_report 21:00),
# chạy SAU fleet_backup (00:00) + sync_bq_cache_daily (23:45) đêm hôm trước, TRƯỚC
# kb_nightly (02:00) — review được TRỌN VẸN cả ngày vừa qua, không sót job cuối ngày nào.
# Trả lời 3 câu user đặt ra 2026-07-09:
#   1. Lỗi hôm đó là lỗi MỚI hay lỗi CŨ tái diễn?
#   2. Fix đã hoàn chỉnh, tránh được rủi ro lặp lại chưa, hay còn hở?
#   3. Bài học chung nào để KHÔNG lặp lại kiểu lỗi này ngày này qua ngày khác?
# Ghi kết quả thành 1 file entry kb/incidents/retro/retro-<ngày>.md (theo đúng format
# kb/incidents/retro/retro-2026-07-07.md — xem đó làm mẫu; sổ sự cố migrate sang cấu trúc
# OKF 1-sự-cố-1-file ngày 2026-07-30, kb/INCIDENTS.md nay là STUB), rồi dọn working memory
# của Mike + chạy consolidate để ngày mai phiên mới refresh sạch, không mang
# theo rác của hôm nay.
#
# KIẾN TRÚC 3-BƯỚC (2026-07-22, thay cho bản 1-job cũ — xem lý do dưới):
#   1. dispatch Mike ĐỒNG BỘ (draft job) — gom bằng chứng, trả lời 3 câu, viết DRAFT
#      ra state/retro_draft_<ngày>.md (KHÔNG đụng kb/incidents/).
#   2. bash TỰ dispatch Wags ĐỒNG BỘ (không qua Mike) để verify draft — bash chỉ
#      capture nguyên văn output, không parse gì cả.
#   3. dispatch Mike NỀN (finalize job, dùng &) — nhận draft + verdict Wags làm input,
#      tự quyết ghi vào kb/incidents/retro/ thế nào, rồi làm nốt commit/dọn memory/
#      consolidate/đăng Trading Daily.
#
# TẠI SAO ĐỔI (bus question `retro-pattern-recurring-headless-wake-assumption-3`, user
# chọn hướng B 2026-07-22): bản cũ để CHÍNH Mike (trong 1 phiên `claude -p` một lần) tự
# dispatch Wags rồi "chờ lượt sau" đọc kết quả — dù prompt đã ghi rõ ràng "CẤM
# ScheduleWakeup", Mike vẫn 2 lần liên tiếp làm sai (07-17 rồi TÁI DIỄN Y HỆT 07-19: job
# Wags kẹt status=running nhiều ngày, không ai đọc). Nhắc trong prompt (dù mạnh) không
# đủ tin cậy để ngăn 1 phiên LLM dài/phức tạp chọn sai đường. Fix ĐÚNG: bỏ hẳn quyền
# quyết định "gọi Wags rồi chờ" khỏi Mike — để bash (vốn đã biết chờ tuần tự, không có
# khái niệm "turn sau" nào cả) tự làm việc đó bằng chính dispatch.sh đồng bộ có sẵn.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Shared usage-limit phrase list (single source of truth, also used by dispatch.sh).
source "$ROOT/bin/usage_limit_phrases.sh"
# Lỗi TRUYỀN TẢI (API/mạng/TLS bị chặn giữa đường) — lớp thứ BA, khác CẢ usage-limit lẫn
# "Mike trả lạc đề". Sự cố thật 2026-08-20 00:30 ICT: cả 2 lần thử chết sau 16-18 giây với
# "API Error: Unable to connect to API: Self-signed certificate detected" (proxy/ISP chèn
# cert) ⇒ retro 2026-08-19 mất hẳn. Hai hệ quả phải vá, không phải một:
#   1. Retry TỨC THÌ (18 giây sau lần đầu) rơi đúng vào cùng khoảng blip ⇒ vô dụng. Lớp này
#      cần chờ một nhịp; usage-limit thì không (chờ cũng vô nghĩa, đã dừng hẳn).
#   2. Log/notify cũ gán MỌI thất bại không-phải-usage-limit thành "nghi Mike trả nhầm task
#      cũ" ⇒ sáng hôm sau người đọc đi tìm bug quoting/prompt trong khi nguyên nhân nằm ở
#      tầng mạng (đúng ca ops-autofix Winston_20260820_012008 bị dẫn sai hướng).
# Cố ý KHÔNG gộp vào usage_limit_phrases.sh: file đó là hợp đồng dùng chung với dispatch.sh
# (khớp ⇒ auto-resume). Lỗi mạng KHÔNG được kích auto-resume của dispatch.sh.
API_TRANSPORT_ERROR_RE='Unable to connect to API|Self-signed certificate|Connection error|fetch failed|ECONNREFUSED|ECONNRESET|ETIMEDOUT|getaddrinfo|EAI_AGAIN'
# Chờ giữa 2 lần thử khi gặp lỗi truyền tải (giây). Cron 00:30 không có deadline gấp.
API_RETRY_BACKOFF_SEC="${DAILY_RETRO_API_BACKOFF_SEC:-180}"
LOG="$ROOT/logs/daily_retro.log"
# Chạy 00:30 ICT = đã sang ngày lịch MỚI — review NGÀY VỪA KẾT THÚC (hôm qua theo giờ chạy),
# không phải "hôm nay" theo đồng hồ lúc script chạy. Bug tiềm ẩn nếu dùng `date` trực tiếp:
# sẽ tính nhầm sang ngày mới, không tìm thấy incident nào của ngày vừa review (cùng họ lỗi
# off-by-one-day vừa sửa cho DollarBill/DT5G hôm nay).
TODAY="$(TZ='Asia/Ho_Chi_Minh' date -d 'yesterday' +%Y-%m-%d 2>/dev/null \
      || TZ='Asia/Ho_Chi_Minh' date -v-1d +%Y-%m-%d 2>/dev/null \
      || python3 -c "import datetime; print((datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))) - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))")"
DRAFT_FILE="$ROOT/state/retro_draft_$TODAY.md"
# Mốc thời gian bắt đầu lần chạy này — dùng ở bước 3 để đọc CƠ KHÍ xem bước 1 đã mở
# escalation nào (sự cố 2026-08-15: bước 1 mở `retro-pattern-recurring-wakeup-miss-2days`,
# 6 phút sau bước 3 mở thêm `wakeup-miss-pattern-escalate-2026-08-15` cho ĐÚNG CÙNG pattern
# → 2 câu hỏi trùng, checker báo 2 lần, user phải quyết 1 việc 2 lần).
RUN_START_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
mkdir -p "$ROOT/state"

log() { echo "[$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%dT%H:%M:%S%z)] $*" | tee -a "$LOG"; }
log "=== daily_retro START (reviewing $TODAY, chạy lúc $(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%dT%H:%M)) ==="

# Leftover-draft staleness check (arch-reviewer finding, 2026-07-22): bước 3 (finalize)
# chạy nền — nếu nó fail, dispatch.sh KHÔNG tự notify (chỉ --bg mode mới có auto-callback
# +notify, sync mode thì im lặng). Dấu hiệu duy nhất của 1 lần finalize fail: draft của
# NGÀY TRƯỚC vẫn còn tồn tại (finalize thành công luôn tự xoá draft ở bước 6 của nó).
# Quét ở ĐÂY (đầu mỗi lần chạy) để không cần thêm cron/job riêng — đúng chu kỳ hàng ngày
# sẵn có, bắt được trong vòng tối đa 1 ngày thay vì "không ai để ý tới khi nào".
for _stale in "$ROOT"/state/retro_draft_*.md; do
  [ -e "$_stale" ] || continue
  [ "$_stale" = "$DRAFT_FILE" ] && continue
  log "WARNING: leftover draft từ lần chạy trước vẫn còn: $_stale — nghĩa là finalize job hôm đó ĐÃ FAIL ÂM THẦM (không tự xoá được draft nếu không xong)."
  "$ROOT/bin/notify.sh" "[daily_retro] Phát hiện draft RETRO cũ chưa dọn: $_stale — dấu hiệu finalize job của lần chạy đó đã fail âm thầm (không notify được vì chạy nền). Cần người kiểm tra kb/incidents/retro/retro-<ngày tương ứng>.md có entry chưa." 2>/dev/null || true
  "$ROOT/bin/append_event.sh" Mike question "daily-retro-stale-draft-$(basename "$_stale" .md)" \
    "{\"reason\":\"leftover draft file phat hien khi chay daily_retro ngay $TODAY, nghia la finalize job truoc do fail am tham\",\"file\":\"$_stale\"}" 2>/dev/null || true
done

# --- Hệ WAKE-UP đã GỠ hoàn toàn 2026-08-21 (commit 541b50f3) --------------------------
# push wake-on-completion + reconciler cron + debounce đã bị loại bỏ. Không còn đo lường.
# logs/wake_thread_errors.log có thể còn dòng fixture từ wake_debounce_selfcheck.sh — không đọc.
echo "$(date -Iseconds) [wake-metrics] REMOVED-2026-08-21 kiến-trúc-wake-up-đã-gỡ" >> "$LOG"

# --- Time-claim audit (§S4, discord_time_reasoning_by_construction_plan_20260821.md) --
# Đo loại lỗi C ("LLM suy luận giờ sai") thay vì chờ user chụp màn hình — scan trong bash
# (không bảo Mike tự grep, cùng triết lý với khối wake-metrics phía trên). KHÔNG
# --dry-run: script tự ghi bus + Discord Architecture nếu có mismatch — daily_retro chỉ cần
# đếm số dòng để đưa vào draft, không tự ghi lại lần hai.
_time_claim_out="$(python3 "$ROOT/bin/time_claim_audit.py" --days 1 2>&1 || true)"
_time_claim_count="$(echo "$_time_claim_out" | head -1 | grep -oE '[0-9]+ mismatch' | grep -oE '^[0-9]+' || true)"
[ -n "$_time_claim_count" ] || _time_claim_count=0
echo "$(date -Iseconds) [time-claim-audit] $TODAY count=$_time_claim_count" >> "$LOG"

# --- Bước 1: Mike viết DRAFT (đồng bộ — bash CHỜ THẬT, không dùng &) ------------------
# DISPATCH_FROM=user bắt buộc — xem fix 2026-07-09 kb_nightly.sh (Friday editorial
# dispatch bị self-dispatch guard chặn âm thầm nhiều tuần vì thiếu dòng này).
rm -f "$DRAFT_FILE"
# Prompt viết DRAFT — đặt vào biến để có thể RETRY 1 lần mà không lặp lại text.
# Mitigation (Wags coord-2026-07-28): phiên Mike `claude -p` thỉnh thoảng trả lời NHẦM
# task cũ còn trong context thay vì viết draft (07-26 trả tóm tắt research "đi đêm lãi
# suất", 07-27 trả status job Taylor) → draft rỗng dù rc=0 → đẻ question vô ích 2 ngày
# liên tiếp. Lần trượt này mang tính nhất thời; 1 lần retry với prompt sạch thường bắt
# được. KHÔNG retry khi draft rỗng do usage-limit (transient quota — retry chỉ phí quota).
draft_prompt=\
"DAILY RETRO — BƯỚC 1/3: VIẾT DRAFT (tự động, ngày $TODAY). Mỗi ngày review lại TẤT CẢ
lỗi/sự cố xảy ra trong ngày, trả lời rõ 3 câu, rút bài học tránh lặp lại 'hết ngày này
đến ngày khác' (user yêu cầu 2026-07-09).

⚠️ NHIỆM VỤ CỦA BẠN Ở BƯỚC NÀY CHỈ LÀ VIẾT DRAFT ra file '$DRAFT_FILE' — KHÔNG đụng
sổ sự cố kb/incidents/, KHÔNG tự dispatch Wags, KHÔNG commit gì cả. 1 script bash khác
(ngoài phiên này) sẽ tự lo phần verify + tạo file entry trong kb/incidents/retro/ + commit
sau khi bạn xong. Viết xong draft là DỪNG, không làm gì thêm.

(Sổ sự cố migrate sang cấu trúc OKF 2026-07-30: 1 sự cố = 1 file trong kb/incidents/<tháng>/,
RETRO hằng ngày = kb/incidents/retro/retro-<ngày>.md, điều hướng ở kb/incidents/index.md.
kb/INCIDENTS.md giờ chỉ là STUB REDIRECT — đừng đọc/ghi nó nữa.)

QUY TRÌNH BẮT BUỘC (đọc bằng chứng thật, không suy đoán):
1. Liệt kê MỌI entry sự cố đã ghi cho ngày $TODAY: 'ls kb/incidents/*/$TODAY-*.md' (sự cố)
   và 'kb/incidents/retro/retro-$TODAY.md' (retro, thường chưa có).
2. Liệt kê MỌI bus event event_type=error/finding trong bus/inbox/*.jsonl có ts bắt đầu
   bằng '$TODAY' — đối chiếu xem có sự cố nào CHƯA được ghi vào kb/incidents/ không (nếu
   có, đây là gap báo cáo cần ghi luôn bổ sung, không bỏ sót).
2d. HỆ WAKE-UP ĐÃ GỠ 2026-08-21 (MIKE.md §8): push wake-on-completion + reconciler cron không
   còn chạy — đây là TRẠNG THÁI MONG ĐỢI. KHÔNG mở sự cố cho push=0/reconciler=0.
   Chỉ còn kiểm soát ScheduleWakeup theo mục 2c khi Mike có bước kế tiếp phụ thuộc.
2c. CHẠY bin/wakeup_audit.py --since \$TODAY (script chỉ hỗ trợ --since, không có --until —
   chấp nhận nó quét luôn phần đầu hôm nay khi retro chạy, đọc kỹ output để CHỈ tính các
   lượt có timestamp thuộc \$TODAY, đừng gộp nhầm). Đo tuân thủ MIKE.md §8: mọi lượt dispatch
   --bg có ScheduleWakeup theo sau không. Nếu có lượt vi phạm trong \$TODAY, đưa vào danh
   sách sự cố ở bước 3 (category=dispatch-orchestration), trích số lượt vi phạm/tổng lượt
   --bg trong ngày.
2e. TIME-CLAIM AUDIT (§S4, bin/time_claim_audit.py — đã chạy sẵn bằng bash, ĐỪNG tự chạy
   lại): số mệnh đề giờ tương đối ('còn ~N phút', 'mở lúc HH:MM') KHÔNG khớp thời điểm gửi
   thật trong 24h qua = $_time_claim_count (xem dòng '[time-claim-audit]' trong
   logs/daily_retro.log để lấy đúng số). Script tự ghi bus (agent quant-skeptic, topic
   'time-claim-audit-<ngày>') + Discord Architecture khi count>0 nên KHÔNG cần bạn tự ghi
   lại — chỉ cần: nếu count>0, đưa vào danh sách sự cố ở bước 3 (category=data-registry-
   accuracy), trích chi tiết từ bus event vừa nêu (grep bus/inbox/*.jsonl). Mục tiêu S4 là
   0 mismatch/tuần; count=0 KHÔNG cần nêu gì thêm (không phải regression, không mở sự cố).
2b. VERIFY ARTIFACT THẬT trước khi báo bất kỳ vấn đề nào là 'chưa xử lý'/'còn treo' — đây
   là quy tắc BẮT BUỘC (bài học 2026-07-10: chính retro lần đầu đã sai — báo 1 câu hỏi
   'crontab paper-main chưa cài' là còn mở CHỈ vì bus event question chưa có answer, trong
   khi thực tế đã cài xong 3.5 tiếng trước đó, verify được ngay bằng \`crontab -l\`; đây
   đúng là Pattern B mà chính retro đang đi bắt — tin trạng thái CŨ/GIÁN TIẾP thay vì đọc
   THỰC TẾ HIỆN TẠI). Với MỖI câu hỏi/vấn đề đang định liệt là 'còn mở': nếu có artifact
   kiểm chứng được trực tiếp (crontab -l, file tồn tại, nội dung code/config, giá trị API
   thật), PHẢI đọc artifact đó ngay trước khi kết luận — KHÔNG suy ra tình trạng chỉ từ
   việc có/không có event 'answer' khớp trên bus (bus có thể trễ, thiếu, hoặc người xử lý
   quên ghi answer dù đã làm xong thật).
3. Với MỖI sự cố tìm thấy, trả lời chính xác 3 câu bằng cách đọc lịch sử sổ sự cố
   ('grep -rn <từ khoá> kb/incidents/' tìm root-cause tương tự các ngày trước, hoặc
   'python3 bin/incident_lookup.py \"<label>\" \"<chi tiết>\"' — KHÔNG đoán từ trí nhớ):
   a. MỚI hoàn toàn hay TÁI DIỄN (cùng dạng lỗi đã xảy ra ngày nào trước — trích dẫn
      entry cũ nếu có)?
   b. Fix đã HOÀN CHỈNH (verify được, đóng hết đường tái phát) hay còn HỞ (nêu rõ residual
      risk, điều kiện nào sẽ khiến nó tái diễn)?
   c. Đây là lỗi ĐƠN LẺ hay thuộc 1 PATTERN xuyên suốt nhiều sự cố trong ngày/nhiều ngày
      (vd: 'luôn là do đọc nguồn dữ liệu trễ/cache thay vì live', 'luôn là do job chết
      lặng lẽ khi tiến trình cha bị giết mà không ai cập nhật trạng thái', v.v.)?
3b. Mỗi sự cố phải có ĐỦ 3 trường trách nhiệm sau, viết thành bảng (không phải văn xuôi
   rời rạc), tinh thần BLAMELESS (mục đích là biết sửa ở BƯỚC/QUY TRÌNH nào, không phải
   quy tội cá nhân/agent):
   - **Phân loại** (category): chọn 1 trong nhóm đã dùng trước đó nếu khớp, hoặc thêm nhóm
     mới nếu thật sự không khớp nhóm nào — data-registry-accuracy, dispatch-orchestration,
     job-monitoring/lifecycle, execution-money-path, permission-credential, scheduling-
     timing, report-data-provenance, khác (ghi rõ).
   - **Nguồn gốc** (origin — bước/quy trình nào tạo ra lỗi, không phải 'ai đáng trách'):
     luôn viết theo khuôn 'quy trình/bước X thiếu Y', không viết 'agent Z làm sai'.
   - **Người ghi chép** (recorder): ai/tiến trình nào đã ghi entry chi tiết gốc của sự cố
     này vào kb/incidents/ lúc phát hiện — trích dẫn job_id/trace_id nếu có. Nếu sự cố
     CHƯA từng được ghi trước khi retro này chạy → ghi rõ 'chưa ai ghi trước retro này,
     retro tự bổ sung' — đây tự nó là 1 dấu hiệu process gap cần nêu.
4. Viết DRAFT entry '# RETRO — $TODAY: <n> sự cố, <m> pattern xuyên suốt' ra file
   '$DRAFT_FILE' (tạo mới, KHÔNG động vào kb/incidents/), theo ĐÚNG format entry
   kb/incidents/retro/retro-2026-07-07.md (đọc nó làm mẫu cấu trúc:
   Pattern N — mô tả, ví dụ cụ thể, Lesson, Prevention), MỞ RỘNG bảng liệt kê sự cố để
   có thêm 2 cột 'Phân loại' và 'Nguồn gốc' theo mục 3b ở trên. Đừng lặp lại nội dung
   entry chi tiết từng sự cố đã có sẵn — entry RETRO này là TỔNG HỢP + PHÂN LOẠI + BÀI
   HỌC XUYÊN SUỐT, không phải chép lại.
5. Nếu phát hiện 1 pattern đã xuất hiện ở RETRO ngày trước đó VẪN tái diễn hôm nay dù đã
   có 'Prevention' — đây là tín hiệu QUAN TRỌNG NHẤT cần nêu bật trong draft: prevention
   cũ chưa đủ mạnh, cần đề xuất prevention MẠNH HƠN (không chỉ lặp lại lời khuyên cũ).
6. Nếu SAU 2 lần RETRO liên tiếp mà CÙNG 1 pattern vẫn tái diễn (kiểm tra RETRO entry
   liền trước) → escalate NGAY bus question 'retro-pattern-recurring-<n>-days' (dùng
   append_event.sh trực tiếp, không cần đợi ai) cho Mike/user biết prevention hiện tại
   không hiệu quả, cần thay đổi cách tiếp cận (không chỉ viết thêm 1 dòng 'prevention').

XONG bước 4-6 ở trên là DỪNG. Không viết gì vào kb/incidents/, không dispatch Wags,
không commit, không dọn memory — tất cả phần đó thuộc bước 2/3 của pipeline, KHÔNG phải
việc của phiên này."

# Content-shape gate (thêm 2026-07-29, sau khi bắt được job Mike_20260729_173001 trả rc=0
# nhưng nội dung là chuyện lạc đề — session_start.sh đã vá root cause session-collision ở
# trên, nhưng vẫn cần lớp phòng thủ THỨ HAI độc lập ở đây: non-empty KHÔNG đủ để coi là
# draft thật, vì bất kỳ output lạc đề nào cũng có thể non-empty. Gate cơ khí rẻ: draft phải
# có đúng dòng header mà chính prompt trên đã ra lệnh viết — 1 câu trả lời lạc đề gần như
# chắc chắn không tình cờ khớp định dạng này.
_draft_valid() {
  local f="$1"
  [ -s "$f" ] || return 1
  # Chấp nhận CẢ '# RETRO —' lẫn '## RETRO —': prompt bước 1 (mục 4) ra lệnh viết 1 dấu #,
  # các entry đã finalize trong kb/incidents/retro/ cũng dùng 1 dấu #. Bản gate đầu tiên
  # chỉ khớp '##' → sẽ loại đúng cái draft ĐÚNG ĐỊNH DẠNG. Gate chưa từng chạy thật trước
  # 2026-08-01 (thêm 07-30 00:48 ICT, sau lần chạy thành công cuối; 2 đêm sau đó script
  # chết ở bug quoting 77cfe4ab trước khi tới đây) nên mismatch này chưa lộ ra.
  # Vẫn giữ nguyên tính chất chống-lạc-đề: output lạc đề không tình cờ khớp header + ngày.
  grep -qE "^#{1,2} RETRO — $TODAY" "$f"
}

rc1=0
for _attempt in 1 2; do
  draft_log="$ROOT/logs/daily_retro_draft_$(date -u +%Y%m%d_%H%M%S)_a${_attempt}.log"
  # `--thread architecture` TƯỜNG MINH (2026-08-02, arch-reviewer vòng 4 B1): dispatch.sh
  # không còn đoán topic từ con trỏ toàn cục, nên cron muốn báo vào topic nào phải nêu đích danh
  # (retro fleet = nội dung ops/kiến trúc). Không nêu ⇒ pin rỗng ⇒ im lặng phía Discord.
  DISPATCH_FROM=user "$ROOT/bin/dispatch.sh" Mike "$draft_prompt" \
      --thread architecture --timeout 1500 > "$draft_log" 2>&1
  rc1=$?
  log "Draft attempt $_attempt exit code: $rc1 (log: $draft_log)"
  _draft_valid "$DRAFT_FILE" && break
  if [ -s "$DRAFT_FILE" ]; then
    _bad="$ROOT/state/retro_rejected_${TODAY}_a${_attempt}.md"
    mv "$DRAFT_FILE" "$_bad"
    log "WARNING: draft attempt $_attempt viết ra file nhưng SAI ĐỊNH DẠNG (thiếu header '# RETRO — $TODAY' — nghi lạc đề/trả nhầm task cũ). Giữ lại để chẩn đoán: $_bad (đầu file: $(head -c 200 "$_bad" | tr '\n' ' '))"
  fi
  # Draft rỗng/sai định dạng: nếu do usage-limit thì DỪNG (transient quota, retry vô nghĩa) —
  # để block phân loại phía dưới xử lý calm-skip. Nếu KHÔNG phải usage-limit thì retry 1 lần
  # cuối với prompt sạch.
  if tail -c 4000 "$draft_log" 2>/dev/null | grep -qiE "$USAGE_LIMIT_PHRASE_RE"; then
    log "Draft rỗng/sai định dạng vì usage-limit — không retry."
    break
  fi
  if tail -c 4000 "$draft_log" 2>/dev/null | grep -qiE "$API_TRANSPORT_ERROR_RE"; then
    [ "$_attempt" -lt 2 ] && {
      log "Draft thất bại vì LỖI TRUYỀN TẢI API/mạng (không phải usage-limit, không phải lạc đề) — chờ ${API_RETRY_BACKOFF_SEC}s rồi retry lần cuối."
      sleep "$API_RETRY_BACKOFF_SEC"
    }
  else
    [ "$_attempt" -lt 2 ] && log "Draft rỗng/sai định dạng (không phải usage-limit) — nghi Mike trả nhầm task cũ; retry lần cuối với prompt sạch."
  fi
done
log "Draft dispatch xong sau $_attempt lần thử (exit $rc1, log: $draft_log)"

# Verify ARTIFACT thật — không tin exit code của dispatch.sh, kiểm tra NỘI DUNG file thật
# đã ghi đúng định dạng draft (không chỉ non-empty).
if ! _draft_valid "$DRAFT_FILE"; then
  # Phân loại LÝ DO draft rỗng trước khi báo động (Wags coord-2026-07-27):
  #   - usage-limit: tài khoản Mike hết quota lúc chạy (00:30 ICT) — TRANSIENT, không cần
  #     user quyết. Chỉ báo calm status, KHÔNG đẻ event `question` (question chưa trả lời sẽ
  #     chất đống → ops_health_check §5 spawn job Wags vô ích; đúng ca 2026-07-25 khi phrase
  #     CLI "weekly limit · resets 5pm" evade _looks_like_usage_limit của dispatch.sh).
  #   - lỗi thật (Mike trả sai/treo/exit0-nhưng-không-viết-draft, đúng ca 2026-07-26): giữ
  #     nguyên event `question` để người/Mike xem — đây là bất thường thật.
  if tail -c 4000 "$draft_log" 2>/dev/null | grep -qiE "$USAGE_LIMIT_PHRASE_RE"; then
    log "SKIP: draft RETRO $TODAY không chạy vì tài khoản Mike hết usage-limit (rc=$rc1) — transient, không cần user quyết."
    "$ROOT/bin/notify.sh" "[daily_retro] RETRO $TODAY bỏ qua: tài khoản Mike hết usage-limit lúc chạy (00:30 ICT). Transient — sẽ tự chạy lại kỳ sau. Không cần làm gì trừ khi lặp nhiều ngày liên tiếp." 2>/dev/null || true
    "$ROOT/bin/append_event.sh" Mike status "daily-retro-skipped-usagelimit-$TODAY" \
      "{\"reason\":\"tai khoan Mike het usage-limit luc chay retro (00:30 ICT), draft khong tao duoc — transient khong can user quyet\",\"rc\":$rc1,\"log\":\"$draft_log\"}" 2>/dev/null || true
    log "=== daily_retro SKIPPED (usage-limit, transient) ==="
    exit 0
  fi
  # Nêu ĐÚNG lớp nguyên nhân trong log/notify/bus — người đọc sáng hôm sau không phải
  # đoán giữa "bug prompt" và "mạng chết" (xem chú thích API_TRANSPORT_ERROR_RE ở đầu file).
  if tail -c 4000 "$draft_log" 2>/dev/null | grep -qiE "$API_TRANSPORT_ERROR_RE"; then
    _fail_cause="loi truyen tai API/mang (vd TLS bi proxy chen cert) — KHONG phai bug prompt/quoting"
  else
    _fail_cause="draft rong hoac sai dinh dang (thieu header RETRO) — nghi Mike tra lac de"
  fi
  log "ERROR: draft job không tạo được '$DRAFT_FILE' hợp lệ sau 2 lần thử (rc=$rc1, nguyên nhân: $_fail_cause) — DỪNG pipeline, không dispatch Wags. Xem state/retro_rejected_${TODAY}_a*.md nếu có (draft lạc đề đã bị gate chặn)."
  "$ROOT/bin/notify.sh" "[daily_retro] LỖI: draft RETRO $TODAY không hợp lệ sau 2 lần thử (job Mike rc=$rc1). Nguyên nhân: $_fail_cause. Xem $draft_log và state/retro_rejected_${TODAY}_a*.md. Retro hôm nay KHÔNG chạy — cần người kiểm tra." 2>/dev/null || true
  "$ROOT/bin/append_event.sh" Mike question "daily-retro-draft-failed-$TODAY" \
    "{\"reason\":\"$_fail_cause (sau 2 lan thu), rc=$rc1\",\"log\":\"$draft_log\",\"rejected_glob\":\"state/retro_rejected_${TODAY}_a*.md\"}" 2>/dev/null || true
  log "=== daily_retro ABORTED ==="
  exit 1
fi
log "Draft OK ($(wc -c < "$DRAFT_FILE") bytes) → dispatching Wags to verify."

# --- Bước 2: bash TỰ dispatch Wags (đồng bộ, KHÔNG qua Mike) --------------------------
# Đây là bước cơ học thuần (gửi draft đi kiểm), không cần phán đoán của Mike — để bash
# gọi trực tiếp loại bỏ hẳn điểm quyết định có thể chọn sai (xem lý do đổi kiến trúc ở
# đầu file). Đồng bộ (không --bg): dispatch.sh tự block tới khi Wags xong hoặc timeout,
# kết quả có ngay trong biến, không cần jobs.sh wait/poll gì thêm.
wags_out="$(DISPATCH_FROM=user "$ROOT/bin/dispatch.sh" Wags \
"XÁC MINH ĐỘC LẬP bản nháp RETRO ngày $TODAY (user yêu cầu 2026-07-11: 'ai đảm bảo những
ghi chép này đã chính xác'). Bản nháp ở file '$DRAFT_FILE' — đọc file đó (KHÔNG sửa gì
vào nó, bạn chỉ đọc-only). Làm 3 việc:
1. Tự grep lại bus/inbox/*.jsonl (event error/finding) ngày $TODAY và đối chiếu xem bản
   nháp có bỏ sót sự cố nào không — đừng tin danh sách bản nháp đã liệt kê, tự tìm lại.
2. Xác nhận mọi commit hash/job_id/số liệu trích dẫn trong bản nháp có thật và khớp
   (dùng git show, jobs.sh status nếu job_id còn trong bus/jobs/).
3. Xác nhận cột 'Nguồn gốc' viết đúng tinh thần blameless (mô tả bước/quy trình, không
   quy tội cá nhân/agent cụ thể).
Trả lời rõ ràng ngay đầu câu trả lời: 'CONFIRMED' (không tìm ra sai sót) hoặc
'GAPS FOUND' kèm danh sách cụ thể từng gap. Bạn KHÔNG tự sửa file draft — chỉ báo cáo." \
    --timeout 900 2>&1)"
rc2=$?
log "Wags verify exit code: $rc2"
if [ "$rc2" -ne 0 ] || [ -z "${wags_out//[[:space:]]/}" ]; then
  wags_out="[VERIFICATION KHÔNG CHẠY ĐƯỢC — dispatch Wags rc=$rc2, output rỗng hoặc lỗi. Xem $LOG.]"
  log "WARNING: Wags verify unavailable — finalize job sẽ tự đánh dấu 'Verified by: CHƯA'."
fi

# Escalation đã mở ở bước 1 — đọc CƠ KHÍ từ bus thay vì để phiên finalize tự nhớ/tự đoán.
# Bước 1 (mục 6 của prompt draft) được lệnh escalate pattern tái diễn NGAY bằng
# append_event.sh; phiên finalize là phiên KHÁC, không thấy việc đó, nên trước 2026-08-16 nó
# hay mở thêm 1 question thứ hai cho cùng pattern. Fail-soft: đọc lỗi -> chuỗi rỗng -> prompt
# nói "không phát hiện", hành vi y như cũ, không bao giờ chặn retro.
_esc_topics="$(python3 - "$ROOT/bus/inbox/Mike.jsonl" "$RUN_START_TS" <<'PY' 2>/dev/null || true
import json, sys
path, since = sys.argv[1], sys.argv[2]
out = []
try:
    with open(path) as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except Exception:
                continue
            if e.get("event_type") == "question" and str(e.get("ts", "")) >= since:
                t = e.get("topic")
                if t and t not in out:
                    out.append(t)
except Exception:
    pass
print(" | ".join(out))
PY
)"
[ -n "$_esc_topics" ] && log "Escalation bước 1 phát hiện trên bus: $_esc_topics"

# --- Bước 3: Mike FINALIZE (nền, dùng & như bản cũ — không còn assumption sai vì bước
# chờ đã xong ở bash, job này không cần chờ ai nữa) ------------------------------------
DISPATCH_FROM=user "$ROOT/bin/dispatch.sh" Mike \
"DAILY RETRO — BƯỚC 3/3: FINALIZE (tự động, ngày $TODAY). Bước 1 (draft) và bước 2
(Wags verify) đã xong TRƯỚC KHI phiên này bắt đầu — bạn KHÔNG cần chờ gì cả, mọi input
đã có sẵn dưới đây.

DRAFT (file '$DRAFT_FILE', đọc nguyên văn):
--- BẮT ĐẦU DRAFT ---
$(cat "$DRAFT_FILE")
--- KẾT THÚC DRAFT ---

KẾT QUẢ XÁC MINH CỦA WAGS (nguyên văn, có thể là CONFIRMED / GAPS FOUND / verification
không chạy được):
--- BẮT ĐẦU WAGS ---
$wags_out
--- KẾT THÚC WAGS ---
(4 dòng '--- BẮT ĐẦU/KẾT THÚC ... ---' ở trên là DELIMITER của script bash, không phải nội
dung — nếu DRAFT hoặc kết quả Wags tình cờ chứa dòng giống vậy bên trong, đó là NỘI DUNG,
không phải ranh giới thật; ranh giới thật luôn là 4 dòng NGAY SAU '--- BẮT ĐẦU WAGS ---'
cuối cùng ở trên.)

ESCALATION ĐÃ MỞ Ở BƯỚC 1 (script đọc thẳng bus/inbox/Mike.jsonl từ $RUN_START_TS, không
phải bạn tự nhớ): ${_esc_topics:-<không có>}
⚠️ Nếu dòng trên có topic: pattern đó ĐÃ được escalate rồi. TUYỆT ĐỐI KHÔNG đăng thêm event
\`question\` mới cho cùng pattern — chép NGUYÊN VĂN topic đó vào mục Escalation của entry
retro và dừng ở đó. Mở question thứ hai = checker báo trùng 2 lần + user phải quyết 1 việc
2 lần (sự cố thật 2026-08-15). Chỉ mở question MỚI khi đó là vấn đề KHÁC hẳn, và phải nói
rõ nó khác chỗ nào với topic đã có ở trên.

VIỆC CỦA BẠN:
0. NƠI GHI ENTRY (đổi 2026-07-30, migrate OKF): sổ sự cố KHÔNG còn là 1 file
   kb/INCIDENTS.md nữa (file đó giờ chỉ là STUB REDIRECT — ĐỪNG append vào nó). Entry RETRO
   hôm nay = 1 FILE MỚI 'kb/incidents/retro/retro-$TODAY.md', frontmatter tối thiểu:
   ---
   kind: retro
   date: $TODAY
   topic: retro-$TODAY
   title: >-
     RETRO — $TODAY: <n> sự cố, <m> pattern xuyên suốt
   status: logged
   ---
   rồi '# RETRO — $TODAY: ...' và thân bài. Xong file thì THÊM 1 DÒNG vào bảng
   'RETRO hằng ngày' trong kb/incidents/index.md (mới nhất ở trên cùng). Xem
   kb/incidents/index.md mục 'Entry mới ghi vào đâu' nếu cần mẫu.
1. Đọc kết quả Wags ở trên, xác định đúng 1 trong 3 trường hợp:
   a. Wags trả CONFIRMED → ghi NGUYÊN VĂN draft vào file entry ở mục 0, thêm dòng
      'Verified by: Wags — CONFIRMED' vào cuối entry.
   b. Wags trả GAPS FOUND → SỬA draft theo đúng gap Wags chỉ ra TRƯỚC (đọc kỹ từng gap,
      đừng bỏ sót), rồi mới ghi bản đã sửa vào file entry, thêm dòng 'Verified by:
      Wags — gaps found and fixed: <tóm tắt ngắn các gap đã sửa>'.
   c. Verification không chạy được (Wags timeout/lỗi/rỗng) → ghi NGUYÊN VĂN draft vào
      file entry, thêm dòng 'Verified by: CHƯA — verification không chạy được vì
      <lý do cụ thể từ log trên>', VÀ ghi 1 bus event question
      'daily-retro-unverified-$TODAY' để có người nhặt lại xác minh sau — KHÔNG im lặng
      bỏ qua việc chưa verify được.
2. Commit file entry mới + kb/incidents/index.md với message rõ ràng.
3. DỌN WORKING MEMORY cuối ngày (user yêu cầu 'trước khi vào dreaming, dọn dẹp bộ nhớ'):
   viết lại kb/memory/Mike.md (bin/remember.sh Mike --set) thành bản GỌN, sạch, phản ánh
   đúng trạng thái THẬT cuối ngày $TODAY: việc đang dở/đang chờ ai, quyết định quan trọng
   hôm nay, KHÔNG chép nguyên văn transcript — chỉ giữ thứ ngày mai cần biết ngay để tiếp
   tục mạch việc, xoá bỏ chi tiết đã xong/không còn liên quan.
4. Chạy bin/consolidate.sh để gộp bus→KB, đảm bảo context_pack.md tươi cho phiên ngày mai.
5. Đăng tóm tắt ngắn (5-8 dòng, tiếng người, không jargon) vào Trading Daily
   (topic trading_daily): số sự cố hôm nay, bao nhiêu mới/bao nhiêu tái diễn, pattern
   xuyên suốt quan trọng nhất, có cái nào fix chưa hoàn chỉnh cần theo dõi tiếp.
6. Xoá file '$DRAFT_FILE' (đã gắn xong vào kb/incidents/, không cần giữ nữa)." \
    --timeout 1200 >> "$LOG" 2>&1 &

log "Finalize job dispatched (background)."
log "=== daily_retro DONE (draft+verify đồng bộ xong, finalize đang chạy nền) ==="
