# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-17T07:57Z (sau merge selfcheck E5/F1/G1)

## Việc vừa xong (08-17)
- **Order-book Pha 0 telemetry**: commit `d6346efd` (main), 29/29 selfcheck PASS. `_order_book_shadow()` ghi `orderbook_shadow_<acct>_<date>.jsonl` tại mỗi child order. Trial bắt đầu 08-18 — kiểm probe `N>0 valid>0` sáng 08-18 sau phiên.
- **P2 expvol_pacing**: EXPVOL_SHADOW đã ghi trong journal 08-17 (TV1 buy, P2 OFF đúng trên live).
- **TV1 tranche cuối**: 500cp @ 20,100 FILL 09:15 ICT SpaceX. Vị thế hoàn tất.
- **Selfcheck isolation E5/F1/G1**: commit `d73e673d` (main) — merge từ session/1521735922066919515-sweep, user duyệt 08-17. capit_lever E5, ghost_order F1/G1 giờ đo đúng tầng guard (không bị HYBRID che). Verified PASS env -u TZ.

## Theo dõi ngày mai 08-18
- Sau phiên sáng: chạy `python3 mike/bin/order_book_shadow_probe.py` — kiểm N>0 và valid>0.
  Nếu valid=0 trong khi N>0 → đọc `source_time_status` trong record (DNSE timestamp format "YYYY-MM-DD HH:MM:SS.mmm" đã pin vào selfcheck).
- EXPVOL_SHADOW tiếp tục log trên mọi lệnh CAPIT/DISCRETIONARY.
- plan-dd-check-string fix (commit 9a9dbb1 trên main) — cần ngày có LAG/BAL để verify đường code thật chạy đúng.

## Quy trình tương tác Discord — user yêu cầu 2026-08-17
Đã wire vào MIKE.md + agents/Mike/CLAUDE.md: interactive turn phải báo nhận việc ngay, post progress 1-2 phút/lần, tự ScheduleWakeup khi chưa xong trong lượt. Không im lặng chờ user hỏi.

## Bối cảnh còn hiệu lực
- dispatch-prompt-heredoc skill — dùng cho MỌI prompt dispatch có backtick/code snippet.
- CASH_VENDOR gate: giữ ĐÓNG (user duyệt 08-15), mở lại chỉ khi >=1 sự kiện ISS/hỗn hợp VÀ qua 2026-09-13.
- corp-action: VN long-only = due-diligence/chi phí, KHÔNG alpha. Quyết định còn chờ user: (A) snapshot pipeline bật thêm inside_transaction NGAY (time-sensitive); (B) wire cờ insider-net-sell-left-tail vào due_diligence.py.

