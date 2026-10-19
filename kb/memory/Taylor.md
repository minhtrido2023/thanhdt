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

- [2026-10-17T02:18:27Z] [weekly 10-12→10-16] 2 file md + 6 chart XONG, delivery gate BLOCK G4 (cột VN-Index có cổ tức). CHỜ Mike/bq_admin gỡ G4 rồi chạy lại report_delivery_gate cho 2 file (sha trong bus finding weekly-...BLOCKED-G4).
- [2026-10-18T03:16:52Z] ĐANG DỞ job Taylor_20261018_030925 (cq-2026-10-18 autodispatch, 7 finding): sửa xong 6 + F7 chỉ docstring, working tree CHƯA commit (9 file ở WorkingClaude/); arch-reviewer ae94d13e chạy nền | NEXT: nhận verdict, commit CHỈ 9 file (cấm git add -A), bus finding topic cq-2026-10-18-taylor-autodispatch, notify_thread.sh architecture
- [2026-10-18T03:22:49Z] [cq-2026-10-18 autodispatch] XONG commit 3147ce873 (9 file), chờ Mike/arch-review vòng 2 nếu muốn; chưa merge/push. (Thay dòng ĐANG DỞ job 030925.)
- [2026-10-18T17:25:58Z] ĐANG DỞ job Taylor_20261018_172548 (VN-Index TR carry-forward v2, wt riêng, KHÔNG merge/data thật) | NEXT: đọc bin/vnindex_total_return.py + registry
- [2026-10-18T17:38:45Z] [vnindex-tr carry-forward v2 10-19] XONG chờ Mike gọi quant-skeptic rồi trình user: nhánh research/vnindex-tr-carry-forward-20261019 @37aa83657 (wt WorkingClaude/wt-Taylor_20261018_172548), finding vnindex-tr-carry-forward-v2-20261019. Mở: 1 ô ZaloPay -6,85→-6,86 nếu weekly 12-16/10 đã gửi bằng v1. (Thay dòng ĐANG DỞ job 172548.)
- [2026-10-18T17:45:16Z] [sunday-plan-round 10-19] XONG chờ Mike arch-review+merge+cài cron: nhánh feat/sunday-plan-round-20261019 @d570de2c9 (wt-Taylor_20261018_173105). Thêm 1 dòng: cổng macro_health CN.
- [2026-10-18T18:53:56Z] [sunday-plan-round vòng 2 10-19] XONG chờ Mike arch-review+merge+cài cron: nhánh feat/sunday-plan-round-20261019 @bc6f53eab (wt-Taylor_20261018_173105). (Thay dòng XONG @d570de2c9.)
- [2026-10-19T02:41:32Z] [sunday-plan-round vòng 3 10-19] XONG chờ Mike merge+cài cron: nhánh feat/sunday-plan-round-20261019 @6501e3011. (Thay dòng @bc6f53eab.)
- [2026-10-19T05:21:56Z] ĐANG DỞ job Taylor_20261019_052148 (AIS chain-order rule oshares_live, wt ../wt-Taylor_20261019_052148 nhánh feat/ais-chain-order-20261019, KHÔNG merge) | NEXT: đọc oshares_live + selfcheck + registry
- [2026-10-19T05:40:07Z] [ais-chain-order 10-19] XONG chờ Mike arch-review+quant-skeptic+merge: nhánh feat/ais-chain-order-20261019 @c22ce4c60 (wt /home/trido/thanhdt/wt-Taylor_20261019_052148), finding ais-chain-order-20261019. (Thay dòng ĐANG DỞ job 052148.)
- [2026-10-19T16:01:43Z] ĐANG DỞ job Taylor_20261019_160133 (DT gate candidate BEAR/CRISIS recount, read-only) | NEXT: đọc get_dt_gate_clock + DT gate trong macro_state_live.py, tái dựng chuỗi 29/09-19/10
- [2026-10-19T16:04:07Z] [dt-gate-badzone 10-19] XONG job Taylor_20261019_160133: khuyến nghị A giữ nguyên; REPORT research/dt_badzone_count_20261019/. Mốc: CRISIS 25/25 sớm nhất ~10/11 nếu không đứt. (Thay dòng ĐANG DỞ job 160133.)
