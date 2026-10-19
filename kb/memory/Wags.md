# Working memory — Wags
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Wags.

# Working memory — Wags
> Sổ tay việc ĐANG MỞ. File này bơm vào đầu MỌI phiên/dispatch của Wags ⇒ mỗi dòng thừa là
> context phải trả tiền lại từ đầu, mỗi lần.

## Ghi gì vào đây (đọc 1 lần)
- Chỉ 2 loại: (a) việc CÒN TREO — đang chờ ai, chờ gì; (b) chốt làm ĐỔI CÁCH LÀM về sau.
- KHÔNG ghi "job X XONG, commit Y". git log + bus + `agents/Wags/research/` đã giữ đủ; chép lại
  vào đây chỉ làm mọi phiên sau phải đọc lại một lần nữa.
- Mỗi entry ≤ 2 dòng: KẾT LUẬN trước, bỏ quá trình.
- Việc treo mà xong rồi thì XOÁ dòng đó, đừng ghi đè một dòng "đã xong" lên trên.
- Quy tắc dùng cho CẢ ĐỘI ⇒ đề xuất vào `kb/coding_guidelines.md` (§13: ghi ra `.proposed`),
  không nuôi riêng trong file này.
- Quá 12 entry thì phần cũ tự sang `kb/memory/archive/Wags_history.md` — không mất, không auto-load.

- [2026-10-08T14:42:20Z] [2026-10-08] context-pack-trim R2 DUNG NEEDS_CHANGES: branch chore/context-pack-trim-20261008 @e143a7cb (wt-ctxtrim-1008) CHUA merge. 1 blocker (V2.5 NO-GO mat khoi hot path) + 4 should-fix, bus finding context-pack-trim. Cho user/Mike cho 1 luot sua nho hoac bo; bo thi git worktree remove + xoa branch.
- [2026-10-08T15:00:48Z] [2026-10-08] dispatch-token-telemetry R2 DUNG o NEEDS_CHANGES: branch feat/dispatch-token-telemetry-20261008 @eacd6dfb (wt-tokentel-1008) CHUA merge; con SF1 round_cap selfcheck do (docstring spend_report:244) + nit. Cho Mike/user cho vong 3 hoac bo.
- [2026-10-09T09:59:14Z] [2026-10-09] selfcheck-red sweep#1: 8/10 CLOSED; OPEN annualization (no moi R&D Taylor, chu Taylor) + nav_2account (SCL ban tay 30/09, question can-user). Sweep sau: 2 cau nay OPEN lan 2 => CAN USER + post Architecture.
- [2026-10-09T15:46:30Z] [2026-10-09] instructions-dedup DUNG NEEDS_CHANGES: branch chore/instructions-dedup-20261009 @69b99144 (wt-instrdedup-1009) CHUA merge; bus finding instructions-dedup co 8 required_change. Cho Mike/user cho 1 luot sua hoac bo (bo: git worktree remove + xoa branch).
- [2026-10-09T20:53:18Z] [2026-10-10] selfcheck-red sweep#2: 0/2 dong, ca 2 CAN USER (da post Architecture). annualization: cho Taylor_20261009_205248 bao PASS rc=0 => dong cau. nav_2account: cho user A/B/C (question selfcheck-red-sweep-2026-10-09-can-user).
- [2026-10-09T20:58:33Z] [2026-10-10T03:58:33Z] selfcheck-red sweep#2: annualization CLOSED (Taylor commit c1516450, Wags verified rc=0 PASS doc-lap). CON LAI: nav_2account CAN USER A/B/C (da post Architecture).
- [2026-10-13T03:30:00Z] [2026-10-13] measured_by gate XONG TREN NHANH feat/finding-measured-by-20261013 @3bb3597ac (wt-measuredby-1013) CHUA merge — cho Mike merge sau gio GD. Viec theo sau neu duoc giao: rotate bus/_measured_by_warn.jsonl trong fleet_housekeeping.sh KEM selfcheck; nit reviewer trong bus finding finding-measured-by-gate-20261013.
- [2026-10-15T05:46:24Z] [2026-10-15] Chốt: đóng question thì answer phải GIỮ ĐÚNG topic rollup; answer topic con (plan-t1-not-ready-*) không đóng câu tổng (checker match đúng topic).
- [2026-10-16T09:36:44Z] [2026-10-16] selfcheck-red sweep#3: 2/3 CLOSED; OPEN snapshot_corp_action (public_datetime, DDL cần user — question selfcheck-red-sweep-2026-10-16-can-user). Sweep sau: còn OPEN ⇒ CẦN USER + post Architecture.
- [2026-10-16T20:53:24Z] [2026-10-17] selfcheck-red sweep#4: snapshot_corp_action OPEN lan 2 => CAN USER (da post Architecture). Cho user tra question selfcheck-red-sweep-2026-10-16-can-user (A: HASH_EXCLUDE+ALTER ADD COLUMN); duyet xong => ap + rerun T3.7 + dong cau.
- [2026-10-19T01:21:50Z] [2026-10-19] Cho user tra A/B/C cau Mike/retro-pattern-recurring-fail-closed-gate-without-owned-recovery-path (da post Architecture 08:2x ICT). Tra loi => close_bus_question.py --decided-by-user + mo viec A / merge nhanh carry-forward C.
- [2026-10-19T05:47:58Z] [2026-10-19] Chờ user trả A/B câu Winston/deposit-cctg-weekly-question (đã post trading_daily 12:5x ICT; im lặng = giữ 6,80/7,40). Có trả lời ⇒ close_bus_question.py --decided-by-user (B thì nhờ Winston chạy append_deposit_rate.py).
