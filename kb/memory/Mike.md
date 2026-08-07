# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-07 (cuối ngày, sau daily retro bước 3/3)

## Daily retro 08-07 — XONG
11 sự cố, 4 pattern. Wags verify GAPS FOUND (2 gap: SpaceX/DRI ghost order tiền thật bị bỏ sót +
tính lộn khung giờ #9) → đã sửa, ghi `kb/incidents/retro/retro-2026-08-07.md`. Escalate 1 pattern
mới lên bus question `retro-pattern-recurring-test-bus-pollution` (test-code
`_publish_bot_event()` ghi bus production, formal hoá 08-05, tái diễn 08-07, 2 hướng Prevention
có sẵn nhưng chưa ai nhận việc sửa).

## Việc treo sang 08-08 (ưu tiên)
1. **`retro-pattern-recurring-test-bus-pollution`** (mới escalate tối nay) — cần dispatch 1 job
   sửa `_publish_bot_event()` (`trading_bot/executor.py:40-55`) thêm guard môi trường, hoặc user
   quyết hướng khác.
2. **SpaceX/DRI ghost order 07:06:49Z** (phát hiện qua Wags verify retro) — cần Taylor/Mafee xác
   nhận có phải hệ quả trực tiếp bug DRI loan-package (#3, đã fix commit `c22bd1c`) không, đối
   chiếu timeline đặt lệnh vs giờ deploy fix.
3. **`plan_state_source_mismatch` false-positive** (`bin/send_plan_report.sh` ~dòng 168-176) — so
   sai chuỗi mô tả `state_source` giữa 2 generator thay vì so giá trị `state` thật. Sẽ báo giả lại
   ở lần gửi plan T+1 kế tiếp nếu chưa sửa.
4. **9/11 sự cố hôm 08-07 chưa có file `kb/incidents/2026-08/`** riêng (đặc biệt funding-gate
   saga #3 — đã fix + quant-skeptic CONFIRMED, chỉ thiếu file ghi).
5. **Sự cố paper-main ghost/netting (6 mã)** — vẫn chưa xác nhận có phải phần chưa đóng của fix
   08-04 (`Taylor_20260804_094514`, "cần verify LIVE end-to-end") hay không.
6. **coord-2026-08-07 saga** bị arch-reviewer bounce 2 vòng liên tiếp rồi im lặng, không ai theo
   dõi tiếp — theo dõi xem có lặp lại ngày mai không (Pattern 3, chưa escalate).
7. Theo dõi: wakeup compliance (14.3% miss 08-07, tăng nhẹ từ 10% 08-06 — chưa escalate).

## Từ tối 08-07 — 2 fix funding gate ĐÃ ĐÓNG (không cần theo dõi thêm, trừ #2 ở trên)
- Mafee commit `c22bd1c` (UPCOM loan-package routing) + Taylor commit `087a3d0` (JIT-unpark
  credit theo tỉ lệ nhu cầu) + doc fix Mike `00ffd2e`. Cả 2 quant-skeptic CONFIRMED. Domain P0
  gate ACTIVE (hard block) từ 08-04 — cập nhật `kb/current_ops.md` đã phản ánh đúng.
- Bài học quy trình: dispatch 2 agent sửa CÙNG file không cách ly → lần sau tách file/chạy tuần tự.

## Kế thừa lâu hơn (theo dõi định kỳ, không cần hành động ngay)
- Verify độc lập fix VHM (NAV-report + LotBook corp-action) — vẫn chưa có ai verify ngoài Taylor.
- lag-sizing-basis-lech-2-account (SpaceX %active_nav sai mẫu số, phải %LAG_book) — cần xác nhận.
- Paper-main netting fix (Taylor_20260804_094514): cần xác nhận LIVE end-to-end.
- Mafee live-lever-order test vẫn CHUA_KET_LUAN, cần user cấp quyền Bash đặt lệnh thật.
- PNJ TTL anomaly_flags (~08-23 review); coding_guidelines.md gần ngưỡng dung lượng.

