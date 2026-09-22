# Working memory — Taylor
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

- [2026-09-14T18:04:21Z] [2026-09-15] A-prime snapshot_corp_action (job _175556): bbbb9b80 tren fix/corp-action-snapshot-schema-aprime (worktree mike/agents/wt-corp-snapshot-aprime), CHUA DDL/merge — CHO user duyet DDL + Mike merge truoc 06:50 ICT theo APPLY_A_PRIME.md; question schema-drift chua dong.
- [2026-09-16T00:44:57Z] [2026-09-16] expvol_pacing checkpoint 09-16 XONG (job _004003, commit mike d2b848ec): gate1+2 PASS, gate3/4 THIEU MAU N=2/25 order-day. CHO user quyet SOM: nhip ~1 order-day/15 phien => can ~370 phien cho 25, nhieu kha nang cham safety_ceiling 2027-02-17 truoc; chap nhan dong trial 'thieu co hoi' hay ha nguong mau? Checkpoint ke 2026-10-13.
- [2026-09-17T15:23:59Z] [2026-09-17] treasury+first_disclosure (job _150848): A report research/treasury_reconcile_20260917 (6ade95ec) CHO Mike/user chon noi luu (bang rieng de xuat) + one-time/recurring + UNSIZED policy truoc khi code oshares_live; B (ae38f4b6) first_disclosure CHUA UNBLOCK prereg, cho Mike quyet mo sprint descriptive.
- [2026-09-17T16:14:14Z] [2026-09-17] treasury window monitor (job _160652): 20d153fb branch feat/treasury-buyback-window-monitor (worktree mike/agents/wt-treasury-window) CHUA merge/CHUA cron - CHO Mike+arch-reviewer; Mike/user chon nguong CLOSE_WINDOW_DAYS (do: 6/29 dong <=45d) + gio cron (de xuat T2 07:10 tuan).
- [2026-09-17T16:25:19Z] [2026-09-17] treasury window monitor: arch B1+B2 vá d25d8b9d (tren 20d153fb, branch feat/treasury-buyback-window-monitor) CHUA merge/cron - CHO arch-reviewer vong 2 + Mike/user chot CLOSE_WINDOW_DAYS (45 vs 90) + gio cron.
- [2026-09-17T16:33:09Z] [2026-09-17] treasury window monitor: arch vong 2 text-fix a8301c27 (tren d25d8b9d) CHUA merge/cron - CHO arch-reviewer vong 3 + Mike/user chot CLOSE_WINDOW_DAYS (45 vs 90) + gio cron.
- [2026-09-18T01:21:32Z] [2026-09-18] fearbuy weekly (job _011034) XONG, commit cf8313fd. MO: GEX = AMBIGUOUS-yeu, 2 cong nhi phan (ket luan dieu tra 500kV mach 3 co neu dich danh phap nhan Gelex? + Q3/2026 CF_OA >= NP?) — cua so gia DA DONG, khong actionable. Caveat dd52 pheu lech sang tuan 3 chua ai fix.
- [2026-09-18T10:49:23Z] [2026-09-18] treasury_share_events table (job _103820): 8b85f833 tren feat/treasury-share-events-table (worktree mike/agents/wt-treasury-table) — CHUA ghi BQ/CHUA tao bang. 577 dong dry-run, 3 tier tach bach, 33 ca suy luan recompute doc lap 33/33 khop. CHO arch-reviewer + Mike/user duyet DDL schema.sql + data_registry_entry.proposed.md.
- [2026-09-18T11:18:41Z] [2026-09-18] treasury_share_events (job _110145): 52d6ab96 tren feat/treasury-share-events-table (worktree mike/agents/wt-treasury-table) — va B1 dedup dem-2-lan (3 cot dup_group_id/is_canonical/duplicate_of, SUM tho phong 3.008.900 CP) + N1 inferred_window_days + 4 file kb/data_registry/*.proposed. 110 PASS, 32/32 mutation. CHUA ghi BQ/CHUA tao bang/CHUA merge — CHO arch-reviewer vong 2 + Mike/user duyet DDL + 4 file .proposed.
- [2026-09-18T11:30:52Z] [2026-09-18] treasury_share_events (job _112831): vong 3 text-only 4e7f51d4 tren feat/treasury-share-events-table (worktree mike/agents/wt-treasury-table) — cam MERGE per-row + muc Nap lai. CHUA ghi BQ/CHUA merge. CHO Mike/user duyet DDL schema.sql + 4 file kb/data_registry/*.proposed.
- [2026-09-22T09:51:32Z] [2026-09-22] nav-corpaction-gate (job _090801): L1 feat/nav-exdate-forecast SAN SANG MERGE (commit ef544b1d, arch-review PASS sau 1 vong sua). L2-L4 feat/nav-corpaction-gate (c5bd6e9b) BI arch-review TU CHOI - L3 verify_cash_div_invariant KHONG BAO GIO reachable tren nhanh is_today (BQ khong the xac nhan ticker cung ngay luc 19:10), L4 se chan NAV that VPB 09-23/09-24 vo co. CAN REDESIGN (gan ticker tu corp-action snapshot thay vi doi BQ; L4 dua tren bang chung credit som that). CHO Mike/user quyet ai lam lai + khi nao - KHONG tu lam tiep duoi ap luc deadline.
- [2026-09-22T10:05:17Z] [2026-09-22] nav-exdate-forecast L1 vong 2 XONG (commit 71d253c2, sua R2-R6 theo arch-review doc lap cua Mike): pipeline-3b doi cho truoc cong abort, R3 notify khi thieu snapshot, R4 day_word theo vi tri phien, R5 test hermetic real schema, R6 guard+wording+unit fixes. 39/39 PASS x3 TZ, tree clean. CHO Mike/user merge feat/nav-exdate-forecast. L2-L4 (feat/nav-corpaction-gate) VAN BI TU CHOI rieng, cho redesign.
