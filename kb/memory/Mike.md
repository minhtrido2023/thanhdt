# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (cập nhật 2026-10-06 00:40 ICT)
- Broker corp-action PRIMARY: branch feat/broker-primary-20261003 CHƯA merge; chờ log shadow T3 06/10 19:25 ICT, rồi user quyết r5 hay merge có điều kiện (r5 cần DISPATCH_ROUND_CAP_OVERRIDE=1 — user quyết).
- Feed vendor corp_action_daily: 05/10 FRESH, 02/10 FAILED; 03/10–04/10 CHƯA xác minh (retro 10-06 phải đọc logs/corp_action_daily.log).
## Đang chờ
- 2 question selfcheck-red Wags (05:08 ICT 05/10: plan_position_drift_check_selfcheck, phs_flash_api_selfcheck) suppress 14 ngày, chưa có answer — đọc nguyên nhân.
- User: plan funnel 8L discretionary (kb/projects/discretionary-8l-candidate-funnel-plan-20261006.md) 4 câu quyết định.
- Plan 06/10 HOLD BAL/LAG chờ duyệt (DollarBill).
## Đã xong 05/10
- Retro 10-05 ghi kb/incidents/retro/retro-2026-10-05.md (commit), draft đã xoá. Fearbuy thứ Sáu đã tắt (backup state/crontab_backup_20261005T172634Z_fearbuy_off.txt).
- Deposit: CCTG chuẩn = 12M cao nhất Big-4, anchor 7,4% (05/10); cron tuần 12/10 08:05 ICT chạy prompt mới lần đầu — kiểm Winston ghi đúng.
## Next
- Retro 10-06: đóng feed corp-action 03/10–04/10; đếm exit 7 dispatch.sh; đọc selfcheck-red.
- KHÔNG đặt wakeup thăm dò khi không có job nền (user 10-05).

- [2026-10-05T17:46:53Z] 06/10 01:0x: user chốt size 5%/mã, nhãn NGÀNH→Bobby trước Taylor; tôi đề xuất rating<=3 + làn B (1/PE top-3/route) + cổng giá trong phiên thay quét thứ Hai (bot 0 lệnh BUY trước 11:00 từ 26/08). Chờ user: duyệt dựng + PVT hấp dẫn vì đâu + tuỳ chọn tự hoãn lệnh mua.
- [2026-10-05T18:02:51Z] 06/10 01:15: dispatch Taylor_20261005_180152 (dựng funnel A+B, branch, KHÔNG merge) + Taylor_20261005_180155 (nghiên cứu làn C/PVT). Cutloss trong phiên: đề xuất ghi trong plan (mặc định theo phán quyết GÃY=bán/CHƯA RÕ=50%/NHIỄU=giữ; loại custom30V; discretionary chỉ bán khi GÃY; shadow 5 phiên) — CHỜ user duyệt. Sau Taylor: review funnel, arch-review, cài cron 19:35.
- [2026-10-05T18:14:23Z] 06/10 01:20: user DUYỆT cutloss theo phán quyết, custom30V cũng theo quy trình, discretionary chỉ bán khi GÃY, trả lời qua Discord. Kịch bản 4 chế độ (bình thường/nhanh/khẩn/kẹt sàn) ghi trong plan, chờ user duyệt chi tiết. Funnel 180152 xong (branch feat/discretionary-8l-funnel-20261006 7750213f, selfcheck 53/53 tôi chạy lại OK) — arch-review bị ngắt, CHƯA chạy xong; chưa merge, chưa cài cron.
