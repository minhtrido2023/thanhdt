# Sleeve discretionary — FPT + NNC (user duyệt 05/11/2026 22:11 + chốt chi tiết 22:17 ICT, `decided_by: user`)

Nguyên văn 22:11: "Đồng ý Duyệt mua fpt và nnc cho sleeve discretionary. Các mã này được phép giữ trong vòng 25 phiên. Nếu đạt target 10% thì bán. Còn không sẽ thoái khi quá 25 phiên giao dịch."
Nguyên văn 22:17: "1. Size 5% Nav. 2. Target 10% so với giá vốn. Trước khi bán cần ý kiến của livermore. Nếu đồng thuận thì bán. Còn không cứ giữ cho đến khi có ý kiến đồng thuận bán phiên kế tiếp từ Livermore. Như vậy 25 phiên vẫn có thể kéo dài nếu còn trend, tức là ý kiến chưa bán. Chỉ bán khi livermore quyết bán. 3. Cắt lỗ ở mốc 10%. Và cắt lỗ theo quy trình cắt lỗ đã có"

## Luật (SUPERSEDES bản 22:11 "thoái cứng quá 25 phiên")
- Mua: FPT, NNC, book DISCRETIONARY_SPECIAL, **5% NAV mỗi mã**. Account: user không nêu ⇒ Mike áp CẢ SpaceX + ZaloPay như tiền lệ TV1; ZaloPay tính 5% trên `active_nav` (DGC excluded), KHÔNG tổng NAV (§7/§25).
- **Exit = Livermore quyết, không phải đồng hồ/giá.** Hai mốc KÍCH HOẠT hỏi Livermore: (a) giá ≥ +10% so giá vốn; (b) đủ 25 phiên giao dịch kể từ ngày vào. Tại mốc: hỏi Livermore (đọc mù, theo mã). Đồng thuận BÁN ⇒ đưa lệnh bán vào plan (vẫn qua user duyệt plan). Chưa bán ⇒ GIỮ, hỏi lại MỖI phiên kế tiếp cho tới khi Livermore nói bán. 25 phiên là mốc xem xét, KHÔNG phải hạn cứng.
- **[CHỐT LẠI 22:35, thay mục này] Cắt lỗ −10% so giá vốn ⇒ LÊN PLAN dưới dạng ĐỀ XUẤT SELL; user XÁC NHẬN (duyệt plan); được duyệt rồi mới vào quy trình cutloss/thực thi đã có.** Không tự bán. (Bản cũ ở ngay dưới giữ để audit.)
- ~~**Cắt lỗ −10% so giá vốn** ⇒ vào "quy trình cắt lỗ đã có" = cổng giá + hồ sơ DD khủng hoảng 7 ngày, user quyết bán, mặc định GIỮ, hệ thống KHÔNG tự bán (`bin/intraday_cutloss_engine.py`, quyết định user 01/11). Cổng sẵn có −5% ∧ idio −4% vẫn chạy. GIẢ ĐỊNH của Mike: −10% giá vốn là MỐC KÍCH HOẠT thêm vào quy trình đó, không phải lệnh bán tự động. Nếu user muốn bán tự động ở −10% phải nói rõ (đảo quyết định 01/11).~~
- Livermore trước giờ DISPLAY-ONLY và chỉ đọc VNINDEX (thử mù 22/10: chưa hơn "luôn UP"); đây là lần đầu nó giữ cửa quyết bán cho cổ phiếu riêng — Mike gọi theo mã, ghi `kb/data_registry/market-state/livermore_reads.md`, chấm sau.

## DD tham chiếu (r2 05/11, giá 04/11)
- FPT: giá 53.900 vs tâm 54.203 (−0,6%), P10 32.389 / P90 74.557.
- NNC: giá 46.900 vs tâm 57.589 (−18,6%), P10 30.219 / P90 93.649.
- Cờ NNC/FPT: cổng cờ tầng lệnh MUA (03/11) có thể chặn; user duyệt tay thì xử theo DD-flag rule 4, KHÔNG lách cổng.

## Trạng thái
- 22:2x: dispatch DollarBill chèn BUY vào plan 06/11 (chưa duyệt, user duyệt plan như thường).
- Việc còn: theo dõi hằng ngày sau khi có fill (ngày vào, giá vốn broker, số phiên, +10%/−10%) → báo để Mike gọi Livermore. Chưa có cron — dựng sau khi biết fill thật.

## Cập nhật 06/11/2026 00:09 ICT (`decided_by: user`)
- User DUYỆT cho Livermore giữ cửa quyết bán FPT/NNC (dù bài thử 100 chuỗi trượt PREREG 0,0007 — xem `agents/Mike/research/livermore_stock_battery_20261105/REPORT.md`). Bán vẫn đi qua plan + user duyệt.
- User DUYỆT 2 plan 06/11 rev2 (SpaceX: SELL TV1 400 + BUY FPT 800/NNC 900; ZaloPay: BUY FPT 500/NNC 600). approved_by ghi qua approve_plan_simple.sh (chuỗi mang "00:0x ICT" = 00:09 ICT).
- User yêu cầu thêm: model kỹ thuật định lượng bổ trợ Livermore (thanh khoản cao; mua → bán được từ chiều T+2; chốt +5% / cắt lỗ −5%).
