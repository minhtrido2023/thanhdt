# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-08 (cuối ngày, sau daily retro bước 3/3)

## Daily retro 08-08 — XONG
1 sự cố mới (`selfcheck-weekly-new-red` báo động giả do chạy tay sai interpreter, cùng họ lỗi
07-31), 1 pattern ĐÓNG (test-bus-pollution — Taylor vá `_publish_bot_event()` guard
`MIKE_BOT_TEST_MODE`, escalate→fix→verify trong ~11h, mẫu tốt), 1 pattern quy trình MỚI formal
hoá: backlog "chưa ghi file kb/incidents/" đã lặp 4 retro liên tiếp (08-05→08-08) mà chưa ai đề
xuất Prevention — 2 hướng nêu ra (stub tự động vs chấp nhận retro-là-đủ), CẦN USER QUYẾT hướng
nào, chưa tự chọn. Wags verify: GAPS FOUND (đếm sai "2 sự cố mới" trong tiêu đề, đã sửa) → file
`kb/incidents/retro/retro-2026-08-08.md`, commit `0ebe1699`.

## Việc treo sang 08-09 (ưu tiên)
1. **Pattern 2 (backlog ghi file kb/incidents/) cần USER quyết** — hướng (a) stub tự động mỗi
   khi finding/error event vượt ngưỡng, hay (b) chấp nhận retro backfill là đủ, sửa quy tắc thay
   vì sửa quy trình. Nêu rõ khi có dịp nói chuyện với user.
2. **9 sự cố 08-07 vẫn 0/9 có file `kb/incidents/` riêng** (đặc biệt funding-gate saga #3 đã fix
   + quant-skeptic CONFIRMED, chỉ thiếu file ghi) — nếu retro 08-09/08-10 vẫn = 0 thì ĐẠT ngưỡng
   escalate cho Pattern 2 theo mục 6.
3. **`selfcheck_weekly_baseline_check.sh`** — 2 việc kỹ thuật nhỏ: (a) thêm run-id vào tên
   `RESULT_JSON` (chống ghi đè bằng chứng lần chạy sai); (b) guard cứng chặn interpreter sai
   `$DNA_PYEXE` (fail loud thay vì chạy sai âm thầm).
4. **`plan_state_source_mismatch`** (`bin/send_plan_report.sh` ~168-176) — so sai chuỗi mô tả
   thay vì giá trị `state` thật, CHƯA sửa, sẽ lộ lại tối nay khi gửi plan T+1.
5. **SpaceX/DRI ghost order 07-07 07:06:49Z** — vẫn CHƯA ai xác nhận liên hệ bug funding-gate
   #3(a) (Taylor/Mafee cần đối chiếu timeline).
6. Theo dõi: wakeup compliance 08-08 = 0% MISS (n=4, mẫu nhỏ) — tín hiệu tốt, chưa kết luận xu hướng.

## Kế thừa lâu hơn (theo dõi định kỳ, không cần hành động ngay)
- Verify độc lập fix VHM (NAV-report + LotBook corp-action) — vẫn chưa có ai verify ngoài Taylor.
- lag-sizing-basis-lech-2-account (SpaceX %active_nav sai mẫu số) — cần xác nhận.
- Paper-main netting fix (Taylor_20260804_094514): cần xác nhận LIVE end-to-end.
- Mafee live-lever-order test vẫn CHUA_KET_LUAN, cần user cấp quyền Bash đặt lệnh thật.
- PNJ TTL anomaly_flags (~08-23 review).
- coord-2026-08-07 saga bị arch-reviewer bounce 2 vòng, im lặng từ đó — theo dõi có lặp không.

