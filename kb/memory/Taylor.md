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

- [2026-09-14T15:43:10Z] [2026-09-14] oshares forward-absorption (job _151805): branch fix/oshares-finfallback-double-count eded0afe (worktree /home/trido/thanhdt-wt-oshares-finfb-dblcount) CHO Mike+arch-reviewer land; ngay land VIB se publish kem MODEL_REBASE (tac dung phu model_version, khong phai so doi); registry .proposed Bay 3.
- [2026-09-14T16:20:38Z] [2026-09-14] oshares fwd-absorption vong 2 (job _160309): bc86963e tren branch fix/oshares-finfallback-double-count (chua merge), verify xanh ca cong publish that. CHO Mike+arch-reviewer vong 3 land. De xuat viec rieng: ~20 check song BQ san co trong oshares_live selfcheck (cung lop rui ro cong do).
- [2026-09-14T17:09:16Z] [2026-09-15] oshares freeze live selfcheck (job _164512): ce123789 tren test/oshares-freeze-live-selfchecks (worktree thanhdt-wt-oshares-freeze-live) + mike 5c931f08. CHO Mike+arch-reviewer land SAU double-count; 2 viec Mike quyet: docstring gate_selfcheck con noi cham BQ, SC2 do oan theo ten thu muc.
- [2026-09-14T17:46:47Z] [2026-09-15] corp_action_feed_canary (job _173213): 2465a35c tren feat/corp-action-feed-canary (worktree mike/agents/wt-corp-feed-canary), CHUA merge/CHUA cai cron — CHO Mike+arch-reviewer. Question mo: corp-action-snapshot-schema-drift-20260914 (snapshot fail tu 09-14, vendor them 2 cot).
- [2026-09-14T18:04:21Z] [2026-09-15] A-prime snapshot_corp_action (job _175556): bbbb9b80 tren fix/corp-action-snapshot-schema-aprime (worktree mike/agents/wt-corp-snapshot-aprime), CHUA DDL/merge — CHO user duyet DDL + Mike merge truoc 06:50 ICT theo APPLY_A_PRIME.md; question schema-drift chua dong.
- [2026-09-16T00:44:57Z] [2026-09-16] expvol_pacing checkpoint 09-16 XONG (job _004003, commit mike d2b848ec): gate1+2 PASS, gate3/4 THIEU MAU N=2/25 order-day. CHO user quyet SOM: nhip ~1 order-day/15 phien => can ~370 phien cho 25, nhieu kha nang cham safety_ceiling 2027-02-17 truoc; chap nhan dong trial 'thieu co hoi' hay ha nguong mau? Checkpoint ke 2026-10-13.
- [2026-09-17T15:23:59Z] [2026-09-17] treasury+first_disclosure (job _150848): A report research/treasury_reconcile_20260917 (6ade95ec) CHO Mike/user chon noi luu (bang rieng de xuat) + one-time/recurring + UNSIZED policy truoc khi code oshares_live; B (ae38f4b6) first_disclosure CHUA UNBLOCK prereg, cho Mike quyet mo sprint descriptive.
- [2026-09-17T16:14:14Z] [2026-09-17] treasury window monitor (job _160652): 20d153fb branch feat/treasury-buyback-window-monitor (worktree mike/agents/wt-treasury-window) CHUA merge/CHUA cron - CHO Mike+arch-reviewer; Mike/user chon nguong CLOSE_WINDOW_DAYS (do: 6/29 dong <=45d) + gio cron (de xuat T2 07:10 tuan).
- [2026-09-17T16:25:19Z] [2026-09-17] treasury window monitor: arch B1+B2 vá d25d8b9d (tren 20d153fb, branch feat/treasury-buyback-window-monitor) CHUA merge/cron - CHO arch-reviewer vong 2 + Mike/user chot CLOSE_WINDOW_DAYS (45 vs 90) + gio cron.
- [2026-09-17T16:33:09Z] [2026-09-17] treasury window monitor: arch vong 2 text-fix a8301c27 (tren d25d8b9d) CHUA merge/cron - CHO arch-reviewer vong 3 + Mike/user chot CLOSE_WINDOW_DAYS (45 vs 90) + gio cron.
- [2026-09-18T01:21:32Z] [2026-09-18] fearbuy weekly (job _011034) XONG, commit cf8313fd. MO: GEX = AMBIGUOUS-yeu, 2 cong nhi phan (ket luan dieu tra 500kV mach 3 co neu dich danh phap nhan Gelex? + Q3/2026 CF_OA >= NP?) — cua so gia DA DONG, khong actionable. Caveat dd52 pheu lech sang tuan 3 chua ai fix.
- [2026-09-18T10:49:23Z] [2026-09-18] treasury_share_events table (job _103820): 8b85f833 tren feat/treasury-share-events-table (worktree mike/agents/wt-treasury-table) — CHUA ghi BQ/CHUA tao bang. 577 dong dry-run, 3 tier tach bach, 33 ca suy luan recompute doc lap 33/33 khop. CHO arch-reviewer + Mike/user duyet DDL schema.sql + data_registry_entry.proposed.md.
