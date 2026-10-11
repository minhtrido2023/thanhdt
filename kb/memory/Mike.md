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
- [2026-10-10T21:06:57Z] [10-11 04:20 ICT] QUỸ MỞ BƯỚC 1 XONG: merge master cdb565a6 (+ kb 4ad5c9e3), arch-review lần 3 APPROVED, số nghiệm thu không đổi, 9 selfcheck xanh trên master, 2 worktree đã dọn. Tài liệu + luật gán + danh sách nợ: kb/projects/fund-unit-performance-policy-20261010.md. VIỆC CÓ MỐC: thứ Hai 12/10 sau 19:10 ICT nhìn 2 dòng 💰 NAV của báo cáo EOD (lượt cron thật đầu tiên với code mới; ZaloPay 'Từ go-live' phải ~−4,9% thay −6,06%; nếu dòng in 'tỉ suất KHÔNG tính được' thì đọc lỗi kèm theo). CHỜ USER 3 điểm: (1) xác nhận luật giá cho tiền vào trước giờ mở cửa/cuối tuần (đang = giá chốt phiên liền trước); (2) đính chính 28 báo cáo ngày ZaloPay in sai mốc thế nào; (3) cho giao bước 2 (tự phát hiện dòng tiền bằng đẳng thức tiền + gộp nợ K2/K3/K4/K5 + cổng tỉ suất fail-closed + cảnh báo pending). Việc hạ tầng nên giao Wags: tz_anchor_gate.baseline_key sai với worktree WorkingClaude/wt-*; sandbox hoá nav_scripts_2account_selfcheck (ghi data/ thật). KHÔNG đặt wakeup — không còn job nền.
- [2026-10-11T03:05:31Z] [10-11 10:10 ICT] User DUYỆT (10:04): (2) đính chính 1 dòng kèm báo cáo ngày ZaloPay 12/10, không gửi lại bản cũ; (3) giao bước 2 quỹ mở sau khi cron tối thứ Hai 12/10 chạy sạch. Đã đặt CronCreate one-shot trong phiên lúc 19:47 ICT thứ Hai 12/10 (12:47 UTC) làm cả 3 việc: kiểm 2 dòng NAV, gửi dòng đính chính vào Trading report 1522576692638388364, dispatch Taylor bước 2. CronCreate CHỈ sống trong phiên — nếu phiên restart thì mất, phải làm tay theo mục này. Điểm (1) luật giá tiền vào trước giờ mở cửa/cuối tuần: user hỏi giải thích, CHƯA chốt (đang = giá chốt phiên liền trước).
- [2026-10-11T03:23:50Z] [10-11 10:25 ICT] User CHỐT điểm (1) quỹ mở: GIỮ giá chốt phiên liền trước cho tiền vào trước giờ mở cửa/cuối tuần/ngày nghỉ (decided_by user, kb 41764ffa; code bước 1 đã đúng, không sửa). Cả 3 điểm chờ user nay ĐÃ ĐÓNG. Còn lại duy nhất: việc có mốc thứ Hai 12/10 sau 19:10 ICT (kiểm 2 dòng NAV + gửi dòng đính chính ZaloPay vào Trading report + dispatch Taylor bước 2) — CronCreate one-shot 19:47 ICT trong phiên, mất nếu phiên restart.
- [2026-10-11T03:25:10Z] [10-11 10:35 ICT] ĐÍNH CHÍNH dòng trên: CronCreate one-shot 19:47 thứ Hai ĐÃ MẤT (phiên Discord mỗi lượt là tiến trình mới ⇒ CronCreate vô dụng ở đây, đừng dùng lại). Thay bằng task one-shot BỀN trong bộ lập lịch ccdb: id 2741 'fund-step2-after-eod-20261012-<thread>', bắn Thứ Hai 12/10 19:46 ICT vào topic 1558282936489611354 (kiểm: curl $CCDB_API_URL/api/tasks). BẪY: bất kỳ ScheduleWakeup nào đặt trong topic này trước giờ đó sẽ XOÁ task (ccdb giữ ≤1 one-shot/thread) ⇒ nếu buộc phải đặt wakeup thì tạo lại task sau.
- [2026-10-11T03:37:41Z] [10-11 10:50 ICT] Topic 1558645322085826593: user hỏi phân tích Haiku/Sonnet/Opus 5.5 + routing mới. ĐÃ TRÌNH 6 đề xuất, CHƯA sửa gì, CHỜ USER duyệt: (1) 8 agents/*/.claude/settings.json claude-sonnet-5 -> claude-sonnet-5-5 (omit --model đang chạy Sonnet đời cũ: 1.054 lượt/3 ngày); (2) ghim model cho 10 native agent chưa có frontmatter model (đang thừa hưởng Opus của Mike); (3) thêm tầng Haiku 5.5 (alias haiku -> claude-haiku-5-5 đã probe) cho việc chỉ-đọc kiểm được; (4) thử 2 tuần Opus mặc định effort medium, high chỉ cho phản biện/đường tiền; (5) ops_autofix.sh opus->sonnet (lật 1 phần quyết định 10-06, cần arch-review); (6) bỏ đẩy Q1 sang opencode (offload 0%), giữ opencode cho second_opinion. Số đo: Taylor opus/high = 65% chi phí job có bản ghi cost (42/320 job).
