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

- [2026-11-02T15:27:06Z] ĐANG DỞ job Taylor_20261102_152306: v2 xong (valuation_blind_v2.py tâm 18.116, P20-80 11.386-24.177) | NEXT: INTRINSIC_v2.md → investor_report/ mới (figs, md, pdf, html, SELFCHECK) → commit → bus tv1-dd-final-20261102
- [2026-11-02T15:35:50Z] [tv1-final 02/11] XONG job Taylor_20261102_152306 commit a2a067cb8 — tam v2 18.100 (P20-80 11.400-24.200), gia 19.500 trong dai; cho Mike gui email + sua dd_price_zones
- [2026-11-02T16:08:19Z] ĐANG DỞ: job Taylor_20261102_160806 dd-flag gate (V1 bot_execute) + DD zone candidates (V2) | NEXT: đọc kb/projects/dd-flag-rules-20261102.md
- [2026-11-02T16:19:33Z] ĐANG DỞ job Taylor_20261102_160806: V1 XONG 8cb89c7da (feat/dd-flag-gate-20261102). NEXT V2: dd_price_zone_watch -> ung vien sleeve, nhanh rieng mike repo
- [2026-11-02T16:26:55Z] [dd-flag-rules 02/11] XONG job Taylor_20261102_160806: V1 8cb89c7da feat/dd-flag-gate-20261102 (repo ngoai) + V2 fd9ea4acf feat/dd-zone-candidates-20261102 (mike) — cho Mike arch-review + merge (V1 truoc V2); PROBE mien cong can xac nhan
- [2026-11-02T16:47:58Z] ĐANG DỞ: job Taylor_20261102_164745 vòng2 dd-flag-gate (V1 netting order) + dd-zone (V2 vặt) | NEXT: sửa bot_execute thứ tự cổng
- [2026-11-02T17:10:53Z] [dd-flag r2 03/11] XONG job Taylor_20261102_164745: V1 55c6883f6 + V2 2fd8ebd1d (chua merge) — cho Mike arch-review r2 + merge V1 truoc V2
- [2026-11-03T01:30:18Z] ĐANG DỞ: crisis-DD DRI ngày2 job Taylor_20261103_013001 | NEXT: legal-vn + web tin mới + giá đóng 02/11, viết dd-note
- [2026-11-03T01:34:33Z] [crisis-dd DRI 03/11] XONG ngày2 (không cờ, GIỮ) — mở: NQ ĐHĐCĐ BT 26/10 + giải trình Q3 PDF chưa đọc, SXKD T10 ~10/11
- [2026-11-03T02:41:31Z] ĐANG DỞ: job Taylor_20261103_024121 research CAPIT flag gate A/B — research/capit_flag_gate_20261103/ | NEXT: tìm engine CAPIT + pin trong results_registry
- [2026-11-03T02:49:52Z] ĐANG DỞ job Taylor_20261103_024121: 6 chân chạy, logs ở research/capit_flag_gate_20261103/logs | NEXT: analyze_exp_.py → REPORT_exp_.md → bus finding
- [2026-11-03T02:50:12Z] [dd-flag r3 03/11] XONG job Taylor_20261103_024119: 1bca09394 PARK mien cong (chua merge) — cho Mike arch-review + merge; KB dd-flag-rules chua commit
