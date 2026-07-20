#!/usr/bin/env bash
# daily_retro.sh — 00:30 ICT (dời từ 22:00, 2026-07-10 — sau khi cập nhật giờ chạy EOD
# pipeline: daily_refresh 18:30 -> bq_freshness_check 19:00 -> send_plan_report 21:00),
# chạy SAU fleet_backup (00:00) + sync_bq_cache_daily (23:45) đêm hôm trước, TRƯỚC
# kb_nightly (02:00) — review được TRỌN VẸN cả ngày vừa qua, không sót job cuối ngày nào.
# Trả lời 3 câu user đặt ra 2026-07-09:
#   1. Lỗi hôm đó là lỗi MỚI hay lỗi CŨ tái diễn?
#   2. Fix đã hoàn chỉnh, tránh được rủi ro lặp lại chưa, hay còn hở?
#   3. Bài học chung nào để KHÔNG lặp lại kiểu lỗi này ngày này qua ngày khác?
# Ghi kết quả thành 1 entry "RETRO — <ngày>" trong kb/INCIDENTS.md (theo đúng
# format entry RETRO 2026-07-07 đã có — xem đó làm mẫu), rồi dọn working memory
# của Mike + chạy consolidate để ngày mai phiên mới refresh sạch, không mang
# theo rác của hôm nay.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="$ROOT/logs/daily_retro.log"
# Chạy 00:30 ICT = đã sang ngày lịch MỚI — review NGÀY VỪA KẾT THÚC (hôm qua theo giờ chạy),
# không phải "hôm nay" theo đồng hồ lúc script chạy. Bug tiềm ẩn nếu dùng `date` trực tiếp:
# sẽ tính nhầm sang ngày mới, không tìm thấy incident nào của ngày vừa review (cùng họ lỗi
# off-by-one-day vừa sửa cho DollarBill/DT5G hôm nay).
TODAY="$(TZ='Asia/Ho_Chi_Minh' date -d 'yesterday' +%Y-%m-%d 2>/dev/null \
      || TZ='Asia/Ho_Chi_Minh' date -v-1d +%Y-%m-%d 2>/dev/null \
      || python3 -c "import datetime; print((datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))) - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))")"

log() { echo "[$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%dT%H:%M:%S%z)] $*" | tee -a "$LOG"; }
log "=== daily_retro START (reviewing $TODAY, chạy lúc $(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%dT%H:%M)) ==="

# DISPATCH_FROM=user bắt buộc — xem fix 2026-07-09 kb_nightly.sh (Friday editorial
# dispatch bị self-dispatch guard chặn âm thầm nhiều tuần vì thiếu dòng này).
DISPATCH_FROM=user "$ROOT/bin/dispatch.sh" Mike \
"DAILY RETRO (tự động, 22:00 ICT, ngày $TODAY) — user yêu cầu 2026-07-09: mỗi ngày review
lại TẤT CẢ lỗi/sự cố xảy ra trong ngày, trả lời rõ 3 câu, rút bài học tránh lặp lại
'hết ngày này đến ngày khác'.

QUY TRÌNH BẮT BUỘC (đọc bằng chứng thật, không suy đoán):
1. Liệt kê MỌI entry trong kb/INCIDENTS.md có ngày = $TODAY (grep '^## $TODAY').
2. Liệt kê MỌI bus event event_type=error/finding trong bus/inbox/*.jsonl có ts bắt đầu
   bằng '$TODAY' — đối chiếu xem có sự cố nào CHƯA được ghi vào INCIDENTS.md không (nếu
   có, đây là gap báo cáo cần ghi luôn bổ sung, không bỏ sót).
2c. CHẠY bin/wakeup_audit.py --since \$TODAY (script chỉ hỗ trợ --since, không có --until —
   chấp nhận nó quét luôn phần đầu hôm nay khi retro chạy, đọc kỹ output để CHỈ tính các
   lượt có timestamp thuộc \$TODAY, đừng gộp nhầm). Thêm 2026-07-20 sau sự cố missed-wakeup-
   after-bg-dispatch, job Wags_20260720_121120 — đo tuân thủ MIKE.md §8: mọi lượt dispatch
   --bg có ScheduleWakeup theo sau không. Nếu có lượt vi phạm trong \$TODAY, đưa vào danh
   sách sự cố ở bước 3 (category=dispatch-orchestration), trích số lượt vi phạm/tổng lượt
   --bg trong ngày.

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
3. Với MỖI sự cố tìm thấy, trả lời chính xác 3 câu bằng cách đọc lịch sử INCIDENTS.md
   (grep root-cause tương tự các ngày trước, KHÔNG đoán từ trí nhớ):
   a. MỚI hoàn toàn hay TÁI DIỄN (cùng dạng lỗi đã xảy ra ngày nào trước — trích dẫn
      entry cũ nếu có)?
   b. Fix đã HOÀN CHỈNH (verify được, đóng hết đường tái phát) hay còn HỞ (nêu rõ residual
      risk, điều kiện nào sẽ khiến nó tái diễn)?
   c. Đây là lỗi ĐƠN LẺ hay thuộc 1 PATTERN xuyên suốt nhiều sự cố trong ngày/nhiều ngày
      (vd: 'luôn là do đọc nguồn dữ liệu trễ/cache thay vì live', 'luôn là do job chết
      lặng lẽ khi tiến trình cha bị giết mà không ai cập nhật trạng thái', v.v.)?
3b. THÊM (user yêu cầu 2026-07-11) — mỗi sự cố phải có ĐỦ 3 trường trách nhiệm sau, viết
   thành bảng (không phải văn xuôi rời rạc), tinh thần BLAMELESS (mục đích là biết sửa ở
   BƯỚC/QUY TRÌNH nào, không phải quy tội cá nhân/agent):
   - **Phân loại** (category): chọn 1 trong nhóm đã dùng trước đó nếu khớp, hoặc thêm nhóm
     mới nếu thật sự không khớp nhóm nào — data-registry-accuracy, dispatch-orchestration,
     job-monitoring/lifecycle, execution-money-path, permission-credential, scheduling-
     timing, report-data-provenance, khác (ghi rõ). Mục đích: gộp sự cố theo NHÓM NGUYÊN
     NHÂN qua nhiều ngày, không chỉ theo 'loại triệu chứng' bề mặt.
   - **Nguồn gốc** (origin — bước/quy trình nào tạo ra lỗi, không phải 'ai đáng trách'):
     ví dụ cụ thể đã xảy ra 2026-07-11 — data_registry.md ghi sai 'fa_ratings không có
     writer' vì bước sweep ban đầu (job Taylor_20260711_080014) chỉ tìm file theo pattern
     tên \`build_fa_ratings_*\`, bỏ sót \`fundamental_rating.py\` không theo pattern đó → gốc
     lỗi là QUY TRÌNH SWEEP thiếu (grep theo tên, không theo nội dung/writer thật), không
     phải 'Taylor sai'. Luôn viết theo khuôn 'quy trình/bước X thiếu Y', không viết 'agent
     Z làm sai'.
   - **Người ghi chép** (recorder): ai/tiến trình nào đã ghi entry chi tiết gốc của sự cố
     này vào kb/INCIDENTS.md lúc phát hiện (thường là agent tự append_event.sh khi xong việc,
     hoặc Mike ghi tay trong phiên sống) — trích dẫn job_id/trace_id nếu có. Nếu sự cố CHƯA
     từng được ghi trước khi retro này chạy (phát hiện qua bước 2 ở trên) → ghi rõ 'chưa ai
     ghi trước retro này, retro tự bổ sung' — đây tự nó là 1 dấu hiệu process gap cần nêu.
4. Viết 1 entry MỚI '## RETRO — $TODAY: <n> sự cố, <m> pattern xuyên suốt' vào cuối
   kb/INCIDENTS.md, theo ĐÚNG format entry 'RETRO — 2026-07-07' đã có sẵn trong file
   (đọc nó làm mẫu cấu trúc: Pattern N — mô tả, ví dụ cụ thể, Lesson, Prevention), MỞ RỘNG
   bảng liệt kê sự cố để có thêm 2 cột 'Phân loại' và 'Nguồn gốc' theo mục 3b ở trên. Đừng
   lặp lại nội dung entry chi tiết từng sự cố đã có sẵn (những cái đó đã ghi rồi) — entry
   RETRO này là TỔNG HỢP + PHÂN LOẠI + BÀI HỌC XUYÊN SUỐT, không phải chép lại.
4b. XÁC MINH ĐỘC LẬP bản nháp RETRO (user yêu cầu 2026-07-11: 'ai đảm bảo những ghi chép
   này đã chính xác' — đây là câu trả lời). SAU KHI viết xong bản nháp (bước 4) nhưng
   TRƯỚC KHI commit: gọi bin/dispatch.sh (đồng bộ, KHÔNG dùng --bg vì cần kết quả ngay
   trong dispatch này) tới agent Wags (Fleet Ops Coordinator, đã có sẵn trong fleet, đúng
   vai trò audit độ tin cậy vận hành), với nội dung yêu cầu Wags làm 3 việc: (1) tự grep
   lại bus/inbox/*.jsonl (event error/finding) ngày $TODAY và đối chiếu xem bản nháp RETRO
   có bỏ sót sự cố nào không — đừng tin danh sách bản nháp đã liệt kê, tự tìm lại; (2) xác
   nhận mọi commit hash/job_id/số liệu trích dẫn trong bản nháp có thật và khớp (dùng git
   show, jobs.sh status nếu job_id còn trong bus/jobs/); (3) xác nhận cột Nguồn gốc viết
   đúng tinh thần blameless (mô tả bước/quy trình, không quy tội cá nhân/agent cụ thể).
   Yêu cầu Wags trả lời CONFIRMED (không tìm ra sai sót) hoặc GAPS FOUND kèm danh sách cụ
   thể — Wags KHÔNG tự sửa file, chỉ báo cáo lại.
   Đọc kết quả Wags trả về, rồi:
   - CONFIRMED → thêm dòng 'Verified by: Wags — CONFIRMED' vào cuối entry, commit luôn.
   - GAPS FOUND → SỬA bản nháp theo đúng gaps Wags chỉ ra trước, rồi mới thêm dòng
     'Verified by: Wags — gaps found and fixed: <tóm tắt>' và commit (không commit bản
     nháp còn gap đã biết).
5. Nếu phát hiện 1 pattern đã xuất hiện ở RETRO ngày trước đó (vd cùng dạng với RETRO
   2026-07-07) VẪN tái diễn hôm nay dù đã có 'Prevention' — đây là tín hiệu QUAN TRỌNG
   NHẤT cần nêu bật: prevention cũ chưa đủ mạnh, cần đề xuất prevention MẠNH HƠN (không
   chỉ lặp lại lời khuyên cũ).
6. Commit thay đổi kb/INCIDENTS.md với message rõ ràng (sau khi đã qua bước 4b).
7. DỌN WORKING MEMORY cuối ngày (user yêu cầu 'trước khi vào dreaming, dọn dẹp bộ nhớ'):
   viết lại kb/memory/Mike.md (bin/remember.sh Mike --set) thành bản GỌN, sạch, phản ánh
   đúng trạng thái THẬT cuối ngày $TODAY: việc đang dở/đang chờ ai, quyết định quan trọng
   hôm nay, KHÔNG chép nguyên văn transcript — chỉ giữ thứ ngày mai cần biết ngay để tiếp
   tục mạch việc, xoá bỏ chi tiết đã xong/không còn liên quan.
8. Chạy bin/consolidate.sh để gộp bus→KB, đảm bảo context_pack.md tươi cho phiên ngày mai.
9. Đăng tóm tắt ngắn (5-8 dòng, tiếng người, không jargon) vào Trading Daily
   (1521470705563340910): số sự cố hôm nay, bao nhiêu mới/bao nhiêu tái diễn, pattern
   xuyên suốt quan trọng nhất, có cái nào fix chưa hoàn chỉnh cần theo dõi tiếp.
10. Nếu SAU 2 lần RETRO liên tiếp mà CÙNG 1 pattern vẫn tái diễn (kiểm tra RETRO entry
    liền trước) → escalate bus question 'retro-pattern-recurring-<n>-days' cho Mike/user
    biết prevention hiện tại không hiệu quả, cần thay đổi cách tiếp cận (không chỉ viết
    thêm 1 dòng 'prevention' nữa)." \
    --timeout 1800 >> "$LOG" 2>&1 &

log "Daily retro dispatch launched (background)."
log "=== daily_retro DONE ==="
