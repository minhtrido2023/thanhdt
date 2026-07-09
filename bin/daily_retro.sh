#!/usr/bin/env bash
# daily_retro.sh — cuối ngày (22:00 ICT), TRƯỚC các job batch đêm (23:15 refresh,
# 23:45 BQ sync, 02:00 kb_nightly). Trả lời 3 câu user đặt ra 2026-07-09:
#   1. Lỗi hôm nay là lỗi MỚI hay lỗi CŨ tái diễn?
#   2. Fix đã hoàn chỉnh, tránh được rủi ro lặp lại chưa, hay còn hở?
#   3. Bài học chung nào để KHÔNG lặp lại kiểu lỗi này ngày này qua ngày khác?
# Ghi kết quả thành 1 entry "RETRO — <ngày>" trong kb/INCIDENTS.md (theo đúng
# format entry RETRO 2026-07-07 đã có — xem đó làm mẫu), rồi dọn working memory
# của Mike + chạy consolidate để ngày mai phiên mới refresh sạch, không mang
# theo rác của hôm nay.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="$ROOT/logs/daily_retro.log"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"

log() { echo "[$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%dT%H:%M:%S%z)] $*" | tee -a "$LOG"; }
log "=== daily_retro START ($TODAY) ==="

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
3. Với MỖI sự cố tìm thấy, trả lời chính xác 3 câu bằng cách đọc lịch sử INCIDENTS.md
   (grep root-cause tương tự các ngày trước, KHÔNG đoán từ trí nhớ):
   a. MỚI hoàn toàn hay TÁI DIỄN (cùng dạng lỗi đã xảy ra ngày nào trước — trích dẫn
      entry cũ nếu có)?
   b. Fix đã HOÀN CHỈNH (verify được, đóng hết đường tái phát) hay còn HỞ (nêu rõ residual
      risk, điều kiện nào sẽ khiến nó tái diễn)?
   c. Đây là lỗi ĐƠN LẺ hay thuộc 1 PATTERN xuyên suốt nhiều sự cố trong ngày/nhiều ngày
      (vd: 'luôn là do đọc nguồn dữ liệu trễ/cache thay vì live', 'luôn là do job chết
      lặng lẽ khi tiến trình cha bị giết mà không ai cập nhật trạng thái', v.v.)?
4. Viết 1 entry MỚI '## RETRO — $TODAY: <n> sự cố, <m> pattern xuyên suốt' vào cuối
   kb/INCIDENTS.md, theo ĐÚNG format entry 'RETRO — 2026-07-07' đã có sẵn trong file
   (đọc nó làm mẫu cấu trúc: Pattern N — mô tả, ví dụ cụ thể, Lesson, Prevention). Đừng
   lặp lại nội dung entry chi tiết từng sự cố đã có sẵn (những cái đó đã ghi rồi) — entry
   RETRO này là TỔNG HỢP + PHÂN LOẠI + BÀI HỌC XUYÊN SUỐT, không phải chép lại.
5. Nếu phát hiện 1 pattern đã xuất hiện ở RETRO ngày trước đó (vd cùng dạng với RETRO
   2026-07-07) VẪN tái diễn hôm nay dù đã có 'Prevention' — đây là tín hiệu QUAN TRỌNG
   NHẤT cần nêu bật: prevention cũ chưa đủ mạnh, cần đề xuất prevention MẠNH HƠN (không
   chỉ lặp lại lời khuyên cũ).
6. Commit thay đổi kb/INCIDENTS.md với message rõ ràng.
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
