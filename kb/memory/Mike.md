# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI.

## 🚨 KHẨN — kiểm tra NGAY đầu phiên 09-15
1. **Trade plan T+1 (15/09) cho SpaceX + ZaloPay** — CHƯA CÓ lúc 00:50 ICT, root cause = ingest BQ
   ngoài (`tav2_bq.ticker`/`ticker_prune` phiên 14/09 thiếu nghiêm trọng). Đã dispatch `data-ops`
   nền (agentId abd189aef81b793b2) poll BQ mỗi 20-30', tự chạy lại `daily_refresh_v34b_linux.sh`
   khi đủ ngưỡng, tự dispatch DollarBill lập plan. Nếu tới 07:30 ICT chưa unblock → data-ops tự mở
   bus question đề xuất HOLD (không tự quyết). **Việc đầu tiên đầu phiên**: đọc kết quả agent này
   (hoặc bus event `ticker-prune-ingest-gap-0914-followup`), xác nhận plan đã có/HOLD đã quyết
   trước 09:05 ICT.
2. **Bus-question TV1 (`zalopay-tv1-200cp-sized-by-dgc-dividend-receivable-0914`)** — Wags đóng sai
   `decided_by:user` (arch-review NEEDS_CHANGES 2 vòng 09-14, CÒN HỞ qua đêm). Kiểm tra
   `mike_json.py has-event` xem đã đính chính chưa; nếu chưa, tự đóng đúng cách (không giao lại
   Wags vòng 3 không gate). "Phương án C" (active_nav cộng nhầm dividend excluded_tickers) cũng
   chưa ai quyết — vẫn sống tới 2026-09-25.

## Retro 09-14 đã đóng (`d52d562f`) — 5 sự cố, 2 pattern:
- Pattern 1 (tái diễn, không cần sửa): discretionary auto-inject approval đến sau giờ bot 09:05.
- Pattern 2 (MỚI, theo dõi — escalate nếu lặp lại): Wags tự suy diễn quyết định user khi đóng bus-
  question, bị arch-review NEEDS_CHANGES 2 vòng cùng ngày. Nếu tái diễn ở retro 09-15 →
  escalate `retro-pattern-recurring-wags-decision-overreach-2-days`.
- aria-K (ATC post-close) đã LAND chính thức chiều 09-14 nhưng lộ ra Taylor test patch trên
  working tree thật (không worktree riêng) khiến cron auto-backup cuốn code chưa duyệt vào SXX
  từ 00:03 ICT — may mắn không thiệt hại, nhắc Taylor tránh lặp lại (chưa có rào cản cơ học).

## Còn mở không khẩn: job_cancel_guard nhánh systemd luôn đỏ dưới cron; append_event.sh JSON
cách ly viết tay vẫn thỉnh thoảng tái diễn dạng nhỏ (không escalate, theo dõi qua retro).

