# Working memory — Taylor
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Taylor.

> Sổ tay việc ĐANG MỞ. File này bơm vào đầu MỌI phiên/dispatch của Taylor ⇒ mỗi dòng thừa là
> context phải trả tiền lại từ đầu, mỗi lần.

## Ghi gì vào đây (đọc 1 lần)
- Chỉ 2 loại: (a) việc CÒN TREO — đang chờ ai, chờ gì; (b) chốt làm ĐỔI CÁCH LÀM về sau.
- KHÔNG ghi "job X XONG, commit Y". git log + bus + `agents/Taylor/research/` đã giữ đủ; chép lại
  vào đây chỉ làm mọi phiên sau phải đọc lại một lần nữa.
- Mỗi entry ≤ 2 dòng: KẾT LUẬN trước, bỏ quá trình.
- Việc treo mà xong rồi thì XOÁ dòng đó, đừng ghi đè một dòng "đã xong" lên trên.
- Quy tắc dùng cho CẢ ĐỘI ⇒ đề xuất vào `kb/coding_guidelines.md` (§13: ghi ra `.proposed`),
  không nuôi riêng trong file này.
- Quá 12 entry thì phần cũ tự sang `kb/memory/archive/Taylor_history.md` — không mất, không auto-load.

- [2026-11-22T09:45:11Z] ĐANG DỞ: job Taylor_20261122_094500 DD VLB | NEXT: đọc skill+BCTC scan, ghi REPORT.md từng phần
- [2026-11-22T09:50:02Z] ĐANG DỞ: job Taylor_20261122_094949 VCB investor report | NEXT: đọc skill, dựng investor_report/ trong dd_VCB_20261117
- [2026-11-22T09:51:02Z] [PAT r5 22/11] XONG job Taylor_20261122_094714: tam 66.470 trước CK / 59.823 sau CK / cong 50.850; tam phu thuoc cach doc H1/26 (62.578 neu 'nhieu') — CHO Mike goi skeptic r5 + ghi dd_price_zones (chua ghi, khong email)
- [2026-11-22T09:54:25Z] [dd-vlb 22/11] XONG job Taylor_20261122_094500: REPORT tam 61.798 sau CK (md5 f80cd48a…), RE ≤52.500 — CHO Mike goi fundamental-skeptic + ghi dd_price_zones; con thieu BCTC 2025 KT + bang giay phep
- [2026-11-22T09:59:41Z] [vcb-investor 22/11] XONG job Taylor_20261122_094949: investor_report VCB 12 trang dry-run, chưa gửi email — CHỜ Mike kiểm + ghi dd_price_zones + user lệnh gửi
- [2026-11-22T10:06:04Z] [dd-vlb r2 22/11] XONG job Taylor_20261122_100129: tam 51.163 sau CK (r1 61.798), 48.100=0,94 TRUNG TINH (md5 93e0ec77…) — CHO Mike goi skeptic xac nhan lai + ghi dd_price_zones
- [2026-11-22T10:08:03Z] ĐANG DỞ: job Taylor_20261122_100749 VLB investor report | NEXT: copy khuôn VCB investor_report/build_report.py, dựng dd_VLB_20261122/investor_report/
- [2026-11-22T10:19:06Z] [vlb-investor 22/11] XONG job Taylor_20261122_100749: PDF 8 trang dry-run, chưa gửi email; phát hiện cổ tức 2.500đ ex 19/11 -> giá/tâm 0,99 cùng cơ sở (r2 0,94) — CHỜ Mike ghi dd_price_zones + user lệnh gửi
- [2026-11-22T12:51:20Z] [A6 22/11] XONG job Taylor_20261122_124816: lint email DD commit ffeae621e (wt-dd-a6, chưa merge); file skill ngoài git đã sửa, bak_20261122 — CHỜ Mike duyệt, bật DD_LINT_BLOCK=True sau khi có số báo giả
- [2026-11-22T13:00:27Z] ĐANG DỞ: job Taylor_20261122_130006 B1 LAG_DD_REQUIRE_CONFIRMED | NEXT: worktree wt-dd-b1 + wt-dd-b1m, sửa plan.py + prompt
- [2026-11-22T13:05:18Z] [B1 22/11] XONG job Taylor_20261122_130006: outer 096541ed8 (wt-dd-b1) + mike f2cc160d5 (wt-dd-b1m), hằng False, chưa merge — CHỜ arch-reviewer + Mike merge
- [2026-11-22T13:14:18Z] ĐANG DỞ: job Taylor_20261122_131400 B4 assumptions lint | NEXT: đọc SPEC, tạo wt-dd-b4
- [2026-11-22T13:17:22Z] [B2 22/11] XONG job Taylor_20261122_131331: commit 270c0231a (wt-dd-b2, chưa merge) — CHỜ arch-review + Mike merge; PLAN: FULL 4 (TCH DCM PAT VLB), ? 12, MECH 5 (HHH MSB PNJ QTP SCL)
- [2026-11-22T13:24:54Z] [B4 22/11] XONG job Taylor_20261122_131400: lint assumptions v1 commit 41b5d6dd2 (wt-dd-b4, chưa merge), cảnh báo — CHỜ quant-skeptic soát + Mike đặt ENFORCE_FROM sau 2 tuần
