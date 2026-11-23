# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 23/11 → 24/11
- 🔴 MỞ: plan T+1 24/11 (SpaceX+ZaloPay) CHƯA tồn tại (WorkingClaude/data/trade_plans chỉ có park_trim). Nguyên nhân: bq_freshness 19:00 FAIL (ticker_prune 197<200 + DT5G golive_state as_of=20/11) ⇒ không dispatch DollarBill. Bus question plan-t1-not-ready-2026-11-24-{SpaceX,ZaloPay} chưa answer. Cần dựng plan trước run_bot 09:05 ICT 24/11 (việc Mike/user sáng nay); chưa điều tra 3 mã thiếu ticker_prune và vì sao DT5G không publish 23/11.
- Retro 23/11 đã ghi: kb/incidents/retro/retro-2026-11-23.md (Pattern 1: dữ liệu nền thiếu ⇒ chuỗi plan dừng, không tự khôi phục). Đề xuất prevention chờ user: retry freshness + auto-dispatch DollarBill; cổng ticker_prune phân biệt thiếu đuôi; late_plan_catchup dựng plan thật. Nếu 24/11 plan vẫn thiếu sau 09:00 ⇒ cân nhắc retro_escalate.
- Còn chờ user: prevention retro 22/11 (fleet_backup alert, ack-trước G5, kiểm weekly T6); cq-hard-boundary mục 4; Winston/deposit-cctg-weekly-question chưa answer.
- Giữ nguyên: DD chỉ email khi user báo; DRI bán hết/TV1 không giữ trong plan 03/11; park 0%.

