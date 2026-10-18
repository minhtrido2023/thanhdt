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

- [2026-10-14T09:29:47Z] ĐANG DỞ job Taylor_20261014_091148 attempt2: commit B2/B1/B3/B4/N-b có sẵn (10e84dd2c) | NEXT: N-a,N-c,N-d,N-e + verify (TZ, §23, harness reviewer, byte master vs nhánh) + bus
- [2026-10-14T09:34:30Z] ĐANG DỞ job 091148 attempt2: TẤT CẢ B1-B4 + N-a..e đã commit (HEAD 8d39846be) | NEXT: verify (harness /tmp/archrev_s4/mut/run.py, TZ, §23, byte proof) + bus finding
- [2026-10-14T09:46:34Z] [Quỹ bước 4 vòng 2, 10-14] XONG nhánh @246f3ba53 (B1-B4 + N-a..e), finding fund-step4-round2-20261014 trace 091148; CHỜ Mike arch-review hẹp vòng 2. Merge PHẢI kèm data/account_inception.json. Sự cố: dòng sót nav_history_ZaloPay 10-14 16:38 (cron 19:10 tự thay) — kiểm sau 19:10. (Thay dòng ĐANG DỞ job 091148.)
- [2026-10-14T13:53:08Z] ĐANG DỞ job Taylor_20261014_135258 (đổi nhãn rate_source cctg_6m→cctg_12m, worktree riêng, KHÔNG merge): bắt đầu | NEXT: grep + tạo worktree
- [2026-10-14T14:35:49Z] [rate-source-label-12m 10-14] XONG chờ arch-review: nhánh fix/rate-source-label-12m-20261014 ở CẢ 2 repo (WC ea82525f, mike 53fd6909b), CHƯA merge. (Thay dòng ĐANG DỞ job 135258.)
- [2026-10-16T03:36:03Z] ĐANG DỞ job Taylor_20261016_033549 (cron chốt sổ đơn vị quỹ tuần, wrapper bin/ledger_seal_weekly.py, nhánh feat/ledger-seal-weekly-20261016 wt riêng, KHÔNG merge/cron/data thật): bắt đầu | NEXT: đọc nav_unit_ledger.py + ledger_anchor_check.py + sandbox mẫu
- [2026-10-16T03:53:05Z] [ledger-seal-weekly 10-16] XONG chờ Mike arch-review+merge+cài cron: nhánh feat/ledger-seal-weekly-20261016 @256bfcca6 (wt đã gỡ), finding ledger-seal-weekly-20261016 trace Taylor_20261016_033549. Theo dõi: vn_market thiếu Tết 2027. (Thay dòng ĐANG DỞ job 033549.)
- [2026-10-16T04:02:25Z] ĐANG DỞ job Taylor_20261016_040211 (ledger-seal-weekly VÒNG 2: B1 NothingToSeal last>=asof, B2 so mốc, N1 N2 N4; wt agents/Taylor/wt-seal-r2, KHÔNG merge/cron/data) | NEXT: tạo wt, sửa
- [2026-10-16T04:09:32Z] [ledger-seal-weekly vòng 2 10-16] XONG chờ Mike arch-review hẹp+merge+cron: nhánh feat/ledger-seal-weekly-20261016 @9900c56e5 (wt gỡ), finding ledger-seal-weekly-round2-20261016 trace Taylor_20261016_040211. (Thay dòng ĐANG DỞ job 040211 + dòng XONG vòng 1.)
- [2026-10-17T02:18:27Z] [weekly 10-12→10-16] 2 file md + 6 chart XONG, delivery gate BLOCK G4 (cột VN-Index có cổ tức). CHỜ Mike/bq_admin gỡ G4 rồi chạy lại report_delivery_gate cho 2 file (sha trong bus finding weekly-...BLOCKED-G4).
- [2026-10-18T03:16:52Z] ĐANG DỞ job Taylor_20261018_030925 (cq-2026-10-18 autodispatch, 7 finding): sửa xong 6 + F7 chỉ docstring, working tree CHƯA commit (9 file ở WorkingClaude/); arch-reviewer ae94d13e chạy nền | NEXT: nhận verdict, commit CHỈ 9 file (cấm git add -A), bus finding topic cq-2026-10-18-taylor-autodispatch, notify_thread.sh architecture
- [2026-10-18T03:22:49Z] [cq-2026-10-18 autodispatch] XONG commit 3147ce873 (9 file), chờ Mike/arch-review vòng 2 nếu muốn; chưa merge/push. (Thay dòng ĐANG DỞ job 030925.)
