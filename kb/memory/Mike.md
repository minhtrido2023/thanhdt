# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (dọn cuối ngày 2026-10-10, sau retro)
- **Retro 2026-10-10 ghi xong**: kb/incidents/retro/retro-2026-10-10.md (commit 3b1cbe16).
  2 sự cố: (1) disk `/` đầy 100% lúc 04:40 ICT (worktree Taylor), tự hồi phục trong ngày không
  rõ ai dọn — error mở, không có event đóng. (2) công cụ tỉ suất §21 (`dividend_adjusted_return.py`)
  lỗi tính GIPS/tax-lot, lan ra 2 báo cáo tuần 05-09/10 đã gửi (sửa + gửi lại, user duyệt 22:03
  ICT 10/10). Pattern H MỚI: lỗi đo lường client-facing được Taylor tự phát hiện-vá-đóng gọn
  trong 1 phiên nhưng KHÔNG đi qua bus dưới dạng `error` (chỉ `finding`) — thiếu tín hiệu nghiêm
  trọng đầu vào; sự cố #1 thiếu tín hiệu đóng đầu ra. Prevention: Taylor post `error` TRƯỚC khi
  vá khi phát hiện lỗi đo lường chạm báo cáo đã gửi; mọi `error` có `action_needed` chỉ người
  phải có event đóng khi giải quyết (kể cả "tự hồi phục, không rõ nguyên nhân"). Wags verify
  GAPS FOUND nhỏ (đếm event 516/7/529→524/9/539), đã sửa.
- **Chính sách "tài khoản = quỹ mở" ĐÃ DUYỆT** (f75457cf, 5 điểm). Bước 1 (sổ đơn vị quỹ) giao
  Taylor job `Taylor_20261010_170004` (opus/high, --bg) — ĐÃ XONG (branch feat/fund-unit-ledger-
  20261011 @feaa33b5, 65/65 mutant chết, control 3.900 giá trị 0 lệch), CHƯA merge, chưa chốt sổ
  thật. Next: kiểm artifact → arch-reviewer 1 lần (dặn liệt kê trọn bộ lỗi) → merge → bước 2 (tự
  phát hiện dòng tiền). Bước 3-4 chưa giao.
- 5 nhánh R&D hậu re-pin park0 (hôm trước) — ĐÃ ĐÓNG hết, không còn gì chờ.
- Instructions-dedup, cutloss intraday shadow v2, corp-action broker-primary SHADOW, SBV
  source-B, Pattern F PAT expiry — không đổi, xem retro-10-09 nếu cần chi tiết.

## Đang chờ
- `selfcheck-red-sweep-2026-10-09-can-user` (Wags/bus question, SCL SpaceX) — còn mở, theo dõi
  sweep Thứ Sáu 16/10.
- `annualization_basis_selfcheck.py` RED (Taylor) — theo dõi sweep tiếp.
- send_plan_report.sh retry drift-check riêng — đề xuất chưa làm, chưa cần gấp.
- Taylor job `Taylor_20261010_170004` (fund-unit-ledger bước 1) — chờ arch-review + merge.

## Next
- Prevention Pattern H: nhắc Taylor post `error` trước khi vá khi gặp lỗi đo lường client-facing
  trong dispatch prompt tiếp theo chạm §21/§31.
- Mỗi `error` có `action_needed` chỉ người — kiểm có event đóng chưa trước khi coi "đã xong"
  (retro mai áp lại, giống Prevention #2 Pattern G đã làm hôm nay).
- Thứ Hai 12/10 08:05 ICT: kiểm cron SBV/CCTG tuần chạy đúng + finalize nhắc STALE nếu cần.
- arch-review fund-unit-ledger bước 1 → merge → giao Taylor bước 2.
- Theo dõi `git worktree list` — nếu đĩa chạm ngưỡng cao lại vài ngày tới, nâng từ "quan sát"
  lên "pattern cần vá" (dọn worktree định kỳ / cảnh báo % dùng).
- KHÔNG đặt wakeup thăm dò khi không có job nền đang chờ kết quả (user 10-05).

- [2026-10-10T18:21:41Z] [10-11 01:25 ICT] Quỹ mở bước 1: vòng 1 (feaa33b5) arch-review NEEDS_CHANGES — K1 (eod mặc định không khai giờ ⇒ giá đơn vị sai vĩnh viễn, lãi ảo ngày rút), K2 (sổ lệch làm cổng tỉ suất fail-open), N1-N11, 30 mutant sống. Review chép ở agents/Taylor/research/fund_unit_ledger_20261011/arch_review_feaa33b5/REVIEW.md. Vòng 2 giao Taylor job Taylor_20261010_182122 (opus/high) với D1 (khai ngày+giờ, code tự suy quy ước: giá chốt gần nhất TRƯỚC khi tiền vào), D2 (chưa nối sổ chốt vào CLI, --seal từ chối data/ tới bước 3), D4 (commit riêng sửa 'Từ go-live' báo cáo ngày: ZaloPay in −6,06% thay vì −4,907% do mốc 1 tỷ mặc định). Xong ⇒ kiểm artifact ⇒ arch-review lần 2 (chỉ xác nhận) ⇒ merge. CHỜ USER: (1) xác nhận luật D1 cho tiền vào trước giờ mở cửa/cuối tuần; (2) có đính chính báo cáo ngày ZaloPay cũ không (lệch 1,15 điểm > ngưỡng 0,5%).
- [2026-10-10T20:14:42Z] [10-11 03:20 ICT] Quỹ mở bước 1: vòng 2 (@75060709) arch-review lần 2 NEEDS_CHANGES — K1 K2 N1-N10 đã đóng; còn B1 (nav_history thiếu dòng phiên ⇒ giá đơn vị sai im lặng; dữ liệu thật thiếu dòng 2026-08-06 cả 2 TK) + L1-L10 nhỏ + 24 mutant sống. Review chép ở agents/Taylor/research/fund_unit_ledger_20261011/arch_review2_75060709/REVIEW2.md (có fix/b1_prototype.patch). Vòng 3 giao Taylor job Taylor_20261010_201420 (opus/medium, áp required_change, 1 commit). Xong ⇒ Mike tự kiểm bằng probe của reviewer (b1.py, fuzz_fix.py) + selfcheck + số nghiệm thu; chỉ gọi review HẸP xác nhận B1/L1-L3, KHÔNG review toàn nhánh lần 3; còn lỗi chặn MỚI ⇒ DỪNG, hỏi user (vòng 4 bị cầu chì chặn). Sau merge: nhìn 2 dòng NAV của cron thật 19:10 ICT thứ Hai 12/10; sửa riêng tz_anchor_gate.baseline_key (worktree WorkingClaude/wt-*); backfill dòng nav_history 2026-08-06; nav_scripts_2account_selfcheck ghi vào data/ thật khi chạy từ worktree (cần sandbox hoá). CHỜ USER: (1) luật D1 tiền vào trước giờ mở cửa/cuối tuần; (2) đính chính 28 báo cáo ngày ZaloPay in sai mốc (thấp hơn 1,13–1,22 điểm %).
