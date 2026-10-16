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

- [2026-10-14T06:06:57Z] ĐANG DỞ job Taylor_20261014_060642 (quỹ bước 4 phần 2: CÀI ĐẶT theo research/fund_step4_20261014/SPEC.md, wt riêng nhánh feat/fund-step4-benchmark-20261014, KHÔNG merge/cron/data thật): bắt đầu | NEXT: đọc README+SPEC, tạo worktree
- [2026-10-14T06:37:49Z] ĐANG DỞ job Taylor_20261014_060642 (quỹ bước 4 phần 2, wt-step4-1014): bước 1-3 COMMIT (b58064f4f A, a51b7cb18 B, 7aeae5999 nav_period_returns benchmark+--sleeve); byte-proof research/fund_step4_impl_20261014/byte_proof.sh 11/11 | NEXT: bước 4 bảng 3.2 + report_delivery_gate (cổng ô chỉ số = CLI, chặn weekly/monthly khi cột cổ tức chưa có số), bước 5 registry+cron (chỉ soạn), bus finding
- [2026-10-14T06:53:21Z] [Quỹ mở bước 4 phần 2, 10-14] XONG: nhánh feat/fund-step4-benchmark-20261014 @6a60a0bbc (5 commit, wt-step4-1014), CHƯA merge/cron; finding fund-step4-impl-20261014 trace Taylor_20261014_060642; README research/fund_step4_impl_20261014/. CHỜ Mike arch-review + user (merge, sleeve_*.json thật, cron, bq_admin Q10). Sau merge: weekly bảng 3.2 cũ bị chặn khi chuỗi TR đã dựng. (Thay dòng ĐANG DỞ job 060642.)
- [2026-10-14T09:12:03Z] ĐANG DỞ job Taylor_20261014_091148 (Quỹ mở bước 4 VÒNG 2: B1-B4 + N-a..e, nhánh feat/fund-step4-benchmark-20261014 wt agents/Taylor/wt-step4-1014, KHÔNG merge/cron/data thật) | NEXT: đọc diff nhánh + review a9c014c85c30499ef + /tmp/archrev_s4
- [2026-10-14T09:26:36Z] ĐANG DỞ job Taylor_20261014_091148: B2 94804b24a, B1 131ea7abf, B3 xong | NEXT: B4 4 mutant (N1 N6 N9 N11) + N-a..e + verify sweep
- [2026-10-14T09:29:47Z] ĐANG DỞ job Taylor_20261014_091148 attempt2: commit B2/B1/B3/B4/N-b có sẵn (10e84dd2c) | NEXT: N-a,N-c,N-d,N-e + verify (TZ, §23, harness reviewer, byte master vs nhánh) + bus
- [2026-10-14T09:34:30Z] ĐANG DỞ job 091148 attempt2: TẤT CẢ B1-B4 + N-a..e đã commit (HEAD 8d39846be) | NEXT: verify (harness /tmp/archrev_s4/mut/run.py, TZ, §23, byte proof) + bus finding
- [2026-10-14T09:46:34Z] [Quỹ bước 4 vòng 2, 10-14] XONG nhánh @246f3ba53 (B1-B4 + N-a..e), finding fund-step4-round2-20261014 trace 091148; CHỜ Mike arch-review hẹp vòng 2. Merge PHẢI kèm data/account_inception.json. Sự cố: dòng sót nav_history_ZaloPay 10-14 16:38 (cron 19:10 tự thay) — kiểm sau 19:10. (Thay dòng ĐANG DỞ job 091148.)
- [2026-10-14T13:53:08Z] ĐANG DỞ job Taylor_20261014_135258 (đổi nhãn rate_source cctg_6m→cctg_12m, worktree riêng, KHÔNG merge): bắt đầu | NEXT: grep + tạo worktree
- [2026-10-14T14:35:49Z] [rate-source-label-12m 10-14] XONG chờ arch-review: nhánh fix/rate-source-label-12m-20261014 ở CẢ 2 repo (WC ea82525f, mike 53fd6909b), CHƯA merge. (Thay dòng ĐANG DỞ job 135258.)
- [2026-10-16T03:36:03Z] ĐANG DỞ job Taylor_20261016_033549 (cron chốt sổ đơn vị quỹ tuần, wrapper bin/ledger_seal_weekly.py, nhánh feat/ledger-seal-weekly-20261016 wt riêng, KHÔNG merge/cron/data thật): bắt đầu | NEXT: đọc nav_unit_ledger.py + ledger_anchor_check.py + sandbox mẫu
- [2026-10-16T03:53:05Z] [ledger-seal-weekly 10-16] XONG chờ Mike arch-review+merge+cài cron: nhánh feat/ledger-seal-weekly-20261016 @256bfcca6 (wt đã gỡ), finding ledger-seal-weekly-20261016 trace Taylor_20261016_033549. Theo dõi: vn_market thiếu Tết 2027. (Thay dòng ĐANG DỞ job 033549.)
