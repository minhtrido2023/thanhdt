# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 21/10 (dọn 00:40 ICT 22/10)
## Chờ USER
- Retro-pattern fail-closed gate (2 câu bus: `...-owned-recovery-path` 18/10 + `...-recovery-path-recurring` 19/10; trả lời xong đóng CẢ HAI).
- Lãi CCTG A/B (6,8% vs 5,9%; mặc định giữ 6,80/7,40).
- Patch chạm NAV/lệnh của nhánh lag-rights-audit (N1-N4, X1-X3) KHÔNG áp, chờ user; rights_issue_alert.py chưa wire.
## Việc theo dõi (Mike)
- Sáng 22/10: Trading Daily có 🔒 seal_blocked (VNINDEX TR, 14/10 n=334) không; dọn `vnindex_tr_daily.csv.bak_pre_restate_20261021` sau báo cáo tuần 24/10; dọn worktree/nhánh fix/vnindex-tr-*.
- Cổng DD-trước-plan LAG: Taylor_20261021_151302 (thí điểm HT1/SCL/VPB, hạn 12:00 22/10; cổng plan hạn 24/10 trưa) → claim-reply, đọc 3 gói, skeptic mã FLAG, arch-review rồi merge trước plan CN 25/10 19:00. SCL đã user ACK PROCEED (LAG_LO 8%, vào ~26/10, hủy nếu VinCons chậm trả).
- Đọc TAY báo cáo plan 25-26/10 (hợp đồng LAG mới lần đầu chạy thật). NON-BLOCKING còn lại của 4 việc LAG: xem current_ops/memory cũ (✅ rỗng, int(entry_window_day) crash, selfcheck Wags phụ thuộc vị trí). Chạy lại audit_live.py sau 15/11.
- Xác nhận `tav2_bq.ticker` phục hồi đủ ~1294 mã (đo 14→21/10 chỉ 794–864 mã/ngày) — bq_admin/Winston; mã niêm yết mới (DMX) + 230/447 mã delisted thiếu dữ liệu.
- 2 question Wags treo (`wags-fix-not-confirmed: coord-2026-10-19/20`); watchdog "no enabled mike@ units" lặp.
- Prevention đề xuất (chưa làm): dispatch.sh cảnh báo --bg thiếu wakeup; script apply-restate tự chạy lại delivery gate; seal benchmark kiểm số mã ticker; memcap/mem_slots (container 40GB).
- FPT Q3: chờ BCTC (~28/10); đã đính chính 2.723 (không phải 2.273). DRI: giữ, hard trigger BCTC Q3 ~30/10 (LNST<22 tỷ→bán 50%), vùng mua ≤13.000 chưa trước BCTC.
## Đã chốt hôm nay
- DRI bán tay 21/10 @15.400 (SpaceX 2.500cp còn, ZaloPay 1.300) — decided_by user; cổng KL active-NAV hợp nhất fill+statement merged f0e293c30.
- VNINDEX TR: G1 rechain + restate-sealed merged 3fa8ec1f7. LAG 4 việc vận hành merged 4ef6ef771.
- Retro 21/10 logged (3 sự cố, Pattern A đóng vòng; Wags GAPS đã sửa). Plan 22/10 KHÔNG được có SELL DRI.
## Mốc
- nav-loss-brake 11-09; review BĐS 11-26; LAG checkpoint 12-15; measurement audit ~12-27; monitor treasury_buyback 26/10; retro 10-23 xét escalate wakeup.

