#!/usr/bin/env bash
# weekly_ops_audit.sh — Sáng thứ Bảy hàng tuần: audit vận hành sâu, "giống như Mike vừa làm"
# (mandate user 2026-08-01, sau khi Mike tự tay rà soát và bắt được 2 bug quoting âm thầm sống
# 2 tuần trong kb_nightly.sh + 2 đêm trong daily_retro.sh — xem kb/incidents/2026-08/).
#
# KHÁC với kb_nightly.sh's Friday/Saturday editorial dispatch (KB content curation, data
# registry audit, fable-drift): job NÀY tập trung vào "có bug thật đang sống mà không ai biết
# không" — sweep log lỗi, verify các fix tuần qua CÓ THẬT SỰ chạy đúng trong production (không
# chỉ tin commit message), theo đúng nguyên tắc "verify artifact, không tin self-report"
# (MIKE.md §Quy chuẩn bắt buộc mục 2, coding_guidelines.md §6). Tách riêng khỏi kb_nightly.sh
# vì dispatch đó đã khá nặng (11 mục) — dồn thêm việc sâu này vào có rủi ro hết turns trước khi
# xong (đã từng thấy job hết max-turns 50 cho khối lượng việc nhỏ hơn, 2026-07-31).
#
# Lịch: 03:30 ICT Thứ Bảy (SAU kb_nightly.sh 02:00, tránh tranh chấp tài nguyên/git lock).
set -uo pipefail
ROOT="/home/trido/thanhdt/WorkingClaude/mike"
LOG="$ROOT/logs/weekly_ops_audit.log"
# (Không còn biến ARCH_THREAD: nó đã CHẾT từ TRƯỚC refactor 2026-08-02 — prompt bên dưới tự
# ghi topic, không đọc biến này. Một biến giữ tên channel mà không ai đọc chính là dạng lỗi
# của sự cố 2026-07-22 "override thành dead-code": sửa biến, tưởng đã đổi đích, thực tế không.)

log() { echo "[$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%dT%H:%M:%S%z)] $*" | tee -a "$LOG"; }
log "=== weekly_ops_audit START ==="

# Post-condition check của LẦN CHẠY TUẦN TRƯỚC (khảo sát vận hành 2026-08-01, xem
# kb/dispatch_output_contract.md) — job này chạy `&` fire-and-forget từ cron, KHÔNG có "lần
# gọi lại" tự nhiên trong ngày như ops_autofix.sh; điểm đúng để tự kiểm là ĐẦU lần chạy TUẦN
# SAU (cùng nguyên tắc kb_nightly.sh Phase 0b). Cửa sổ 9 ngày (rộng hơn chu kỳ 7 ngày 1 chút,
# chống lệch giờ chạy) — không chặn dispatch tuần này dù tuần trước lỗi, chỉ báo rõ.
SINCE_LAST_WEEK="$(TZ=UTC date -u -d '9 days ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || true)"
if [ -n "$SINCE_LAST_WEEK" ] && ! python3 "$ROOT/bin/mike_json.py" has-event "$ROOT/bus" Mike \
     "$SINCE_LAST_WEEK" "decision:weekly-ops-audit" >/dev/null 2>&1; then
  log "WARNING: không tìm thấy decision 'weekly-ops-audit' nào trong 9 ngày qua — lần chạy tuần trước có thể đã lạc đề/chết im."
  "$ROOT/bin/notify.sh" "🟡 weekly_ops_audit: KHÔNG tìm thấy decision 'weekly-ops-audit' nào trong 9 ngày qua — lần chạy tuần trước có thể đã lạc đề/chết im. Kiểm logs/weekly_ops_audit.log." >/dev/null 2>&1 || true
fi

# Prompt xây bằng heredoc QUOTED ('PROMPT_EOF') — cố tình, để loại hẳn lớp lỗi vừa vá 2 lần
# hôm nay (unescaped " / ` bên trong chuỗi bash double-quoted làm dispatch.sh nhận sai
# argument hoặc bash cố thực thi 1 đoạn text như lệnh). Heredoc quoted không bash-parse bất
# kỳ ký tự nào bên trong (không cần escape " hay `), chỉ cần path là literal (không biến).
PROMPT="$(cat <<'PROMPT_EOF'
WEEKLY OPS AUDIT (automated, sáng thứ Bảy hàng tuần). Bạn đang ở headless mode.

Bối cảnh: user yêu cầu (2026-08-01) lặp lại định kỳ đúng kiểu rà soát Mike vừa tự tay làm hôm đó
— rà soát KHÔNG PHẢI để tìm thấy "mọi thứ ổn" mà để CHỦ ĐỘNG săn bug thật đang sống, verify các
fix gần đây CÓ THỰC SỰ chạy đúng trong production hay không (không chỉ tin commit message/log
"launched"/rc=0). Bài học gốc cùng ngày: 2 script cron (daily_retro.sh, kb_nightly.sh) đều có bug
quoting âm thầm — 1 cái crash 2 đêm liền, 1 cái làm CẢ review Friday/Saturday chết 2 TUẦN LIỀN —
không ai biết vì log "đã dispatch"/"đã launch" không đồng nghĩa "chạy đúng". Xem
kb/incidents/2026-08/2026-08-01-daily-retro-quoting-bug-silent-2day-outage.md và
kb/incidents/2026-08/2026-08-01-kb-nightly-friday-dispatch-silently-broken-2-weeks.md làm mẫu
tinh thần rà soát (đọc log thật, tái hiện lỗi, verify bằng cách CHẠY THỬ chứ không chỉ đọc lại).

VIỆC CẦN LÀM (mỗi mục xong ghi 1-2 câu kết luận, đừng chỉ nói "đã kiểm tra"):

1. SWEEP LOG LỖI: chạy `python3 bin/cron_health_check.py` (audit CƠ HỌC toàn bộ crontab — mtime +
   quét lỗi có ngày-nhận-biết cho mọi job có log target; đã chạy DAILY qua
   cron_health_check_daily.sh 08:25 T2-T6, nhưng chạy lại ở đây để có bức tranh MỚI NHẤT ngay
   lúc review). Đọc kỹ CẢ 4 nhóm (ERRORS_FOUND/STALE/LOG_MISSING/NO_LOG_REDIRECT) — STALE/
   LOG_MISSING có thể là false positive hợp lệ (job mới cài chưa tới lần chạy đầu, script chỉ
   log khi CÓ việc) nên đừng tự động coi là bug, đối chiếu ngày cài đặt (kb/cron_registry.md)
   trước khi kết luận. Bổ sung thêm: grep mọi file logs/*.log đổi trong 7 ngày qua mà
   cron_health_check.py CHƯA có log-target khai báo cho (dấu hiệu tự viết script mới chưa đăng
   ký vào crontab đúng cách) tìm dấu hiệu crash tương tự (Traceback, "unbound variable", "No such
   file or directory" ngay sau tên script ở đầu dòng, "syntax error", "command not found",
   "Permission denied", "ERROR: unknown argument"). Với MỖI hit: đối chiếu kb/incidents/ xem đã ghi chưa
   còn ảnh hưởng workflow sống → điều tra root cause (đọc script liên quan), nếu nằm trong ranh
   giới tự sửa an toàn (bug code trong script report/check/pipeline/cache — KHÔNG CHẠM trade
   plan/trading_rules.json/logic đặt lệnh/crontab dòng thực thi/xoá dữ liệu/BOT_STOP, giống hệt
   guardrail ops_autofix.sh) → tự sửa, verify bằng cách CHẠY THỬ đoạn code sau khi sửa (không chỉ
   đọc lại), ghi entry kb/incidents/<YYYY-MM>/<ngày>-<topic>.md, commit. Vượt ranh giới → escalate
   bus question + notify, KHÔNG tự sửa.

2. VERIFY CÁC FIX TUẦN QUA THẬT SỰ CHẠY ĐÚNG: liệt kê mọi commit "fix(...)" trong git log 7 ngày
   qua (mike repo) + mọi entry kb/incidents/ status=fixed mới trong 7 ngày. Với MỖI cái: tìm 1
   ARTIFACT THẬT xác nhận nó đang hoạt động đúng trong production (dòng log thật gần nhất khớp
   hành vi mong đợi, file state được ghi đúng, output đúng định dạng) — KHÔNG chỉ tin commit
   message. Không tìm được artifact xác nhận → ghi rõ "CHƯA VERIFY ĐƯỢC (chưa có lần trigger
   thật kể từ khi fix)" thay vì suy đoán là đã ổn.

3. TOKEN/COST TREND: đọc state/spend_history.csv. Báo cáo %fable VÀ %opus tuần mới nhất + so 3
   tuần gần nhất (không chỉ tuần này). %opus tăng ≥20 điểm % trong 3 tuần HOẶC ≥60% tuần mới nhất
   → lấy mẫu 5-8 dispatch opus gần nhất (bus/jobs/*.json), đánh giá có thật sự "task nặng cần
   planning nhiều" theo MIKE.md §Model routing hay không. Không tự sửa thói quen dispatch, chỉ
   đo + báo cáo minh bạch (đây là hành vi con người của Mike, không phải bug code).

4. KÍCH THƯỚC FILE KB QUAN TRỌNG: wc -c cho kb/context_pack.md, kb/current_ops.md, MIKE.md,
   kb/coding_guidelines.md. So với ngưỡng đã biết (context_pack.md 45KB, current_ops.md 28KB).
   Nếu đang tăng, ước lượng tốc độ tăng gần đây (so với git log trước đó ~1-2 tuần, dùng
   `git log --format=%H -- <file>` rồi `git show <commit>:<file> | wc -c` vài điểm) và số ngày
   còn lại trước khi chạm ngưỡng. KHÔNG tự trim ở đây (việc đó thuộc kb_nightly.sh Friday review
   + Mike phiên sống) — chỉ đo + cảnh báo nếu <7 ngày còn lại trước ngưỡng.

5. OKF TREE STALENESS (kb/data_registry/ thôi — kb/incidents/ đã tự động hoá hàng ngày, xem
   dưới): so sánh danh sách file thật (`find kb/data_registry -name '*.md'`) với bảng liệt kê
   trong index.md tương ứng. Lệch (file có nhưng không có trong bảng, hoặc ngược lại) → tự sửa
   index.md (việc tài liệu thuần, không rủi ro) + commit.
   (`kb/incidents/index.md` KHÔNG cần làm ở đây nữa — `bin/incidents_index_sync.py --check/--fix`
   đã chạy hàng ngày qua `cron_health_check_daily.sh` 08:25, tự sửa + commit khi lệch, khảo sát
   vận hành 2026-08-01. Chỉ cần LIỆT KÊ ở báo cáo cuối nếu 7 ngày qua có commit
   "chore(incidents): auto-sync index.md" nào bất thường/lặp lại nhiều lần — dấu hiệu drift tái
   diễn nhanh, đáng điều tra root cause thay vì để tự sửa lặp lại mãi.)

6. BUS QUESTION BACKLOG: chạy `python3 bin/bus_question_audit.py`. Câu nào Mike có đủ thông tin
   tự quyết (không cần thẩm quyền user riêng) → tự quyết + ghi answer. Câu nào thật cần user →
   giữ PENDING, liệt kê rõ trong báo cáo cuối kèm tuổi.

7. daily_retro.sh COVERAGE: liệt kê 7 ngày gần nhất có/thiếu kb/incidents/retro/retro-<ngày>.md.
   Thiếu ngày nào → ghi rõ, đối chiếu logs/daily_retro.log xem có lỗi bash không (đúng check đã
   thêm vào ops_health_check.sh mục 9, đây là lớp xác nhận thêm ở tầng tuần).

8. SELFCHECK BASELINE (khảo sát vận hành 2026-08-01, bin/run_selfchecks.sh — kết quả THẬT của
   lần chạy TRƯỚC dispatch này, nối ở CUỐI prompt bên dưới, không phải bạn tự chạy lại): đọc
   phần "=== SELFCHECK RESULTS ===" ở cuối. Với MỖI FAIL: đọc kỹ, phân biệt (a) regression thật
   (code sản xuất đổi làm selfcheck sai — tự sửa nếu trong ranh giới mục 1, verify lại bằng
   cách CHẠY THẬT không chỉ đọc) vs (b) selfcheck tự nó có giả định sai/lỗi thời (dữ liệu ngày
   cụ thể đổi, ground-truth cần cập nhật — sửa selfcheck, ghi rõ lý do KHÔNG phải bug production)
   vs (c) chưa đủ thông tin để kết luận (ghi rõ "CẦN ĐIỀU TRA SÂU HƠN", đừng đoán). KHÔNG cần
   sửa hết trong 1 lần nếu nhiều — ưu tiên FAIL nào có khả năng chạm surface tiền thật/dữ liệu
   client-facing trước.

BÁO CÁO CUỐI (bắt buộc, dù mọi mục đều sạch — quiet-heartbeat: "không có gì mới" vẫn phải nói rõ
ràng, im lặng hoàn toàn không phân biệt được với job chết): tổng hợp ngắn gọn 7 mục trên, bug nào
tìm thấy + đã tự sửa (kèm commit hash) hay đang escalate, số PENDING bus question, %fable/%opus,
kích thước kb file quan trọng. Post báo cáo này vào Architecture channel bằng:
bash bin/notify_thread.sh "<báo cáo>" architecture
VÀ notify Telegram (bin/notify.sh "<tóm tắt ngắn>"). Sau đó append_event.sh Mike decision
'weekly-ops-audit' "<JSON tóm tắt: bugs_found, bugs_fixed, escalated, pct_fable, pct_opus>".

KHÔNG cần hỏi user trước cho việc 1,5,6 (tài liệu/dọn backlog thuần, đã uỷ quyền). Việc 1 chỉ tự
sửa trong đúng ranh giới đã nêu — vượt ranh giới luôn escalate, không tự quyết.
PROMPT_EOF
)"

# Chạy selfcheck baseline THẬT trước dispatch (khảo sát vận hành 2026-08-01, item #2 đã duyệt)
# — nối kết quả vào PROMPT bằng string concatenation (KHÔNG chèn vào bên trong heredoc quoted
# ở trên, giữ nguyên lý do heredoc quoted ban đầu: tránh lại đúng lớp lỗi quoting đã vá 2 lần).
log "Chạy selfcheck baseline (bin/run_selfchecks.sh, offline tier)..."
SELFCHECK_OUT="$(bash "$ROOT/bin/run_selfchecks.sh" 2>&1 | tail -200)"
PROMPT="$PROMPT

=== SELFCHECK RESULTS (chạy thật trước dispatch này, xem việc 8) ===
$SELFCHECK_OUT"

DISPATCH_FROM=user "$ROOT/bin/dispatch.sh" Mike "$PROMPT" \
    --model opus --effort high --timeout 3600 >> "$LOG" 2>&1 &

log "Weekly ops audit dispatch launched (background)."
log "=== weekly_ops_audit DONE (dispatch chạy nền) ==="
