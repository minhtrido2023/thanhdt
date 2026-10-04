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

- [2026-10-03T08:45:36Z] ĐANG DỞ: job Taylor_20261003_082621 broker-CA r4, wt-brokerca-r4-1003 branch fix/broker-ca-r4-20261003 @c187bc94 (12 mục sửa, 132/132 mutant, 102/102 matrix, replay 7/7) | NEXT: arch-reviewer 1 lần → bus finding broker-corp-action-source-r4-20261003; KHÔNG merge (Mike merge trước 19:25 T2 05/10)
- [2026-10-03T09:02:00Z] [broker-CA r4] DỪNG (lỗi mới khác loại M-A) job Taylor_20261003_082621: fix/broker-ca-r4-20261003 @c187bc94 (wt-brokerca-r4-1003), 12/12 mục sửa, reviewer không chặn merge-shadow. CHỜ Mike merge trước 19:25 T2 05/10 + user chốt ngữ nghĩa _FAILED feed_dead (M-A) trước live.
- [2026-10-03T10:45:05Z] [2026-10-03 ICT] [broker-CA r5] XONG job Taylor_20261003_091511: fix/broker-ca-r5-20261003@e38c808e (wt-brokerca-r5-1003), 161/161 mutant, matrix 102/102. CHỜ Mike merge trước 19:25 T2 05/10.
- [2026-10-03T16:28:34Z] ĐANG DỞ: job Taylor_20261003_162814 broker-PRIMARY (đảo thứ tự vendor→broker), wt agents/Taylor/wt-brokerprimary-1003 branch feat/broker-primary-20261003 từ 2c2abc63 | NEXT: đọc code auto_confirm+broker_detect, thiết kế đảo thứ tự
- [2026-10-03T16:43:48Z] ĐANG DỞ: job Taylor_20261003_162814 broker-PRIMARY, wt agents/Taylor/wt-brokerprimary-1003 (feat/broker-primary-20261003 từ 2c2abc63), design /tmp/brokerprim/design.md, mục 5+6 xong /tmp/brokerprim/q56.md | NEXT: code broker_detect (vendor_crosscheck, price-only) + auto_confirm (live order) + selfcheck
- [2026-10-03T17:07:59Z] ĐANG DỞ: job Taylor_20261003_162814 broker-PRIMARY, wt agents/Taylor/wt-brokerprimary-1003 WIP commit (selfcheck 338/0 kèm replay) | NEXT: mutation (sửa mẫu cũ + thêm mẫu mới), matrix 17 selfcheck x2 interp x3 TZ, arch-reviewer 1 lần, bus finding broker-primary-20261003
- [2026-10-03T17:34:35Z] ĐANG DỞ: job Taylor_20261003_162814 broker-PRIMARY @311c917a (wt-brokerprimary-1003), mutation 230/230, matrix 102/102, replay OK; scratch wt-archrev-bp-1004 (xoá sau) | NEXT: arch-reviewer 1 lần → bus finding broker-primary-20261003
- [2026-10-03T17:55:37Z] [broker-PRIMARY] DỪNG (lỗi mới khác loại) job Taylor_20261003_162814: feat/broker-primary-20261003@a1e1923e (wt-brokerprimary-1003), arch-review NEEDS_CHANGES: MAJOR-1 registry-có-sẵn im lặng, MAJOR-3 không re-verify sau ex, MAJOR-4 price-only trước ghi; note agents/Taylor/research/broker-primary-20261004.md. CHỜ Mike/user quyết vòng sửa trước live.
- [2026-10-04T02:42:51Z] ĐANG DỞ: job Taylor_20261004_024239 broker-primary r2 (5 RC), wt agents/Taylor/wt-brokerprimary-1003 @a1e1923e | NEXT: đọc note research/broker-primary-20261004.md, sửa RC1-RC5
- [2026-10-04T02:42:51Z] ĐANG DỞ: job Taylor_20261004_024243 plan-position-drift-flag (HƯỚNG NHẸ) | NEXT: worktree feat/plan-position-drift-flag-20261004, script bin/plan_position_drift_check.py
- [2026-10-04T02:47:47Z] ĐANG DỞ: job Taylor_20261004_024239 broker-primary r2, wt-brokerprimary-1003 @a1e1923e, design /tmp/brokerprim/r2_design.md | NEXT: code RC1-RC5 + test + mutants
- [2026-10-04T03:03:29Z] ĐANG DỞ: job Taylor_20261004_024243 drift-flag Q5, wt agents/Taylor/wt-driftflag-1004 @140874f3 (selfcheck 76, mut 34/34) | NEXT: arch-reviewer 1 lần → sửa → bus finding plan-position-drift-flag-20261004
