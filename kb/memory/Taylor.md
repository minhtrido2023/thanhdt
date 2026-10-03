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

- [2026-10-03T04:44:10Z] ĐANG DỞ: job Taylor_20261003_033512 broker-corp-action, wt-brokerca-1003 branch feat/broker-corp-action-source-20261003 @07706719; arch-review v1 NEEDS_CHANGES (B1 gia-khong-roi/modifiedDate refresh dem; B2 selfcheck cu ghi ledger prod - DA XOA file) | NEXT: sua tron bo required_changes roi arch-review v2 (tran 3 vong)
- [2026-10-03T04:45:25Z] ĐANG DỞ: job Taylor_20261003_033512 attempt2, wt-brokerca-1003 @07706719 + diff dở account_evidence; arch-review v1 full ở /tmp/brokerca/archrev_v1.md (B1,B2,M1-M6,minor) | NEXT: sửa hết required_changes → selfcheck → arch-review v2
- [2026-10-03T05:01:27Z] ĐANG DỞ: job Taylor_20261003_033512 attempt2, wt-brokerca-1003 @bb457b9c (sửa trọn arch-review v1, review v1 lưu /tmp/brokerca/archrev_v1.md) | NEXT: arch-review v2 → nếu APPROVE ghi bus finding broker-corp-action-source-20261003
- [2026-10-03T05:29:46Z] [broker-corp-action] DỪNG ở cầu chì vòng 3 (job Taylor_20261003_033512): branch feat/broker-corp-action-source-20261003 @9ab1cf5f (wt-brokerca-1003), shadow an toàn để merge; TRƯỚC live còn MAJOR N9 (_broker_record_near không xét _status) + 11 đột biến sống — CHỜ Mike quyết dispatch chế độ A. 4 dòng rác quote_unmapped trong dnse_raw_2026-10-03.jsonl do mình, chưa xoá.
- [2026-10-03T07:01:44Z] [2026-10-03T14:0X ICT] [broker-corp-action FIX] XONG job Taylor_20261003_064854: commit 846dfcd6 trên feat/broker-corp-action-source-20261003 (N9 + 19 đột biến, 105/105). CHỜ user: merge, bật live, exdate fallback, cron 21:00.
- [2026-10-03T08:45:36Z] ĐANG DỞ: job Taylor_20261003_082621 broker-CA r4, wt-brokerca-r4-1003 branch fix/broker-ca-r4-20261003 @c187bc94 (12 mục sửa, 132/132 mutant, 102/102 matrix, replay 7/7) | NEXT: arch-reviewer 1 lần → bus finding broker-corp-action-source-r4-20261003; KHÔNG merge (Mike merge trước 19:25 T2 05/10)
- [2026-10-03T09:02:00Z] [broker-CA r4] DỪNG (lỗi mới khác loại M-A) job Taylor_20261003_082621: fix/broker-ca-r4-20261003 @c187bc94 (wt-brokerca-r4-1003), 12/12 mục sửa, reviewer không chặn merge-shadow. CHỜ Mike merge trước 19:25 T2 05/10 + user chốt ngữ nghĩa _FAILED feed_dead (M-A) trước live.
- [2026-10-03T10:45:05Z] [2026-10-03 ICT] [broker-CA r5] XONG job Taylor_20261003_091511: fix/broker-ca-r5-20261003@e38c808e (wt-brokerca-r5-1003), 161/161 mutant, matrix 102/102. CHỜ Mike merge trước 19:25 T2 05/10.
- [2026-10-03T16:28:34Z] ĐANG DỞ: job Taylor_20261003_162814 broker-PRIMARY (đảo thứ tự vendor→broker), wt agents/Taylor/wt-brokerprimary-1003 branch feat/broker-primary-20261003 từ 2c2abc63 | NEXT: đọc code auto_confirm+broker_detect, thiết kế đảo thứ tự
- [2026-10-03T16:43:48Z] ĐANG DỞ: job Taylor_20261003_162814 broker-PRIMARY, wt agents/Taylor/wt-brokerprimary-1003 (feat/broker-primary-20261003 từ 2c2abc63), design /tmp/brokerprim/design.md, mục 5+6 xong /tmp/brokerprim/q56.md | NEXT: code broker_detect (vendor_crosscheck, price-only) + auto_confirm (live order) + selfcheck
- [2026-10-03T17:07:59Z] ĐANG DỞ: job Taylor_20261003_162814 broker-PRIMARY, wt agents/Taylor/wt-brokerprimary-1003 WIP commit (selfcheck 338/0 kèm replay) | NEXT: mutation (sửa mẫu cũ + thêm mẫu mới), matrix 17 selfcheck x2 interp x3 TZ, arch-reviewer 1 lần, bus finding broker-primary-20261003
- [2026-10-03T17:34:35Z] ĐANG DỞ: job Taylor_20261003_162814 broker-PRIMARY @311c917a (wt-brokerprimary-1003), mutation 230/230, matrix 102/102, replay OK; scratch wt-archrev-bp-1004 (xoá sau) | NEXT: arch-reviewer 1 lần → bus finding broker-primary-20261003
- [2026-10-03T17:55:37Z] [broker-PRIMARY] DỪNG (lỗi mới khác loại) job Taylor_20261003_162814: feat/broker-primary-20261003@a1e1923e (wt-brokerprimary-1003), arch-review NEEDS_CHANGES: MAJOR-1 registry-có-sẵn im lặng, MAJOR-3 không re-verify sau ex, MAJOR-4 price-only trước ghi; note agents/Taylor/research/broker-primary-20261004.md. CHỜ Mike/user quyết vòng sửa trước live.
