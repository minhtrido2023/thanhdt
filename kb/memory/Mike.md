# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 13/11 → 14/11
- Retro 13/11 ghi xong (kb/incidents/retro/retro-2026-11-13.md). Backup mike-fleet ĐÃ LÊN LẠI (252856b84, rewrite f1e5e9d31); bundle 4,0GB giữ làm đường lùi.
## Đang chờ / mở
- Plan T+1 thứ Hai 16/11 chưa dựng (plan-t1-not-ready SpaceX+ZaloPay, owner Mike→DollarBill): dispatch DollarBill dựng plan trước run_bot 09:05 ICT T2; plan cần user duyệt (mirror topic plan 1521183164364754974).
- Wags/selfcheck-red-sweep-20261113-book-clearing-merge-approval: chờ user duyệt merge fix book_clearing (nhánh fix/book-clearing-lag-dd-zone-gate-20261113, chạm đường sửa qty).
- Escalation classifier-denials-mike đã mở (retro-pattern-recurring-classifier-denials-mike) — không đăng trùng; việc: allowlist headless cho close_bus_question.py.
- Wags/wags-fix-not-confirmed: coord-2026-11-13 — nghi đóng được, kiểm trước khi đóng.
## Quyết định quan trọng 13/11
- User chọn A rewrite master gỡ file >100MB (backup); NEO sizing DD đổi: NAV ≤2 tỷ ⇒ DD5 ≈ −33% (xem kb/projects/bal-lag-live-gap-findings-20261112.md).
## Việc nên làm thêm
- Pre-commit chặn file >95MB cả repo; viết entry kb/incidents/ cho sự cố backup GH001.

- [2026-11-14T01:39:16Z] 14/11 08:5x: dọn bus 19→9 câu mở. Đóng: book_clearing(user duyệt, merge 26b0c29ed), 5 meta-alarm Wags coord-05/06 (expired_unverified), coord-12/13 (đã vá fleet_backup+selfcheck, ac5fc0324). Housekeeping nay tự đóng plan-t1-not-ready khi plan_date khớp + meta-alarm Wags >=3d. CÒN: PNJ Q3 (chờ user A/B), plan 16/11 (vòng CN 19:00 dựng), classifier-denials (chờ user duyệt A), 5 selfcheck-red thật (immutable_publish/universe_pit_p3,p4/basket_price_basis_audit/nav_scripts_2account — phụ thuộc dữ liệu live, chưa triage)
- [2026-11-14T02:57:42Z] 14/11 10:00: DONE — raw ticker restored + cache heal + DT5G refresh 13/11 OK (state 3). PNJ DD: giữ loại, PDF đã đính, ledger+kb commit 6eb8cc663, email CHƯA gửi (chờ user). Còn mở: plan 16/11 (vòng CN 19:00 dựng; user duyệt trước 08:45 T2), 5 selfcheck-red tự đóng khi sweep xanh (kb_nightly 02:00), RCA ETL kaffa_v2 (bq_admin) + dedupe VNH 13/11, đề xuất gate so đếm raw ticker vs ticker_1m (chưa làm), PNJ: lượt định giá mù giá thật chưa làm.
- [2026-11-14T05:53:55Z] [14/11 12:55] NT5 live-gap vòng 5: user hỏi A8 có cần không. Mike đánh giá KHÔNG CẦN lúc này (không code nào đọc neo DD5; park 0, CAPIT lever tắt, nav-loss-brake chỉ cảnh báo ⇒ kết quả A8 không đổi hành động nào). A8 SHELVED, không mở topic mới; đóng chuỗi live-gap. Mở lại nếu: user muốn bật margin/park>0/CAPIT lever, hoặc live DD thật vượt −33% (nav-loss-brake đỏ). Danh sách đo nếu mở lại: pin1M/park0,3 ở NAV nhỏ; gate live rating≤3/governance/dd_zone/allocator; trần ½ ADV 2 account.
- [2026-11-14T06:24:46Z] 14/11 13:30: Livermore training plan xong (kb/projects/livermore-training-plan-20261114.md, job Taylor_20261114_061614). CHỜ user duyệt P0+P1 (5 câu §11) rồi dispatch Taylor Opus medium; chưa dispatch gì thêm.
- [2026-11-14T06:36:04Z] 14/11 13:36: User DUYỆT Livermore plan (P0+P1 ngay; P2 đủ 2 nhánh×3 lần SAU G0/G1; cổng 12=cổng giết; thu hẹp vai nếu G1/G2 fail; đọc theo mã tiếp). Job Taylor_20261114_063556 (opus/high, 4h) làm A-F P1 + gói case κ. TIẾP: khi xong → Mike chạy 60 lượt Livermore (20 case×3) chấm κ → quant-skeptic phản biện P1 → quyết G0/G1 → P2. Artifact agents/Taylor/research/livermore_divergence_20261114/.
