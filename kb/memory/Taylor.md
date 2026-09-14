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

- [2026-09-13T06:01:49Z] cq-20260913 follow-up 1258 XONG (job _055125): nguon = injector:116 khong truyen goi, 0 tac dong tien; patch #1 KHONG dong ca nay. CHO Mike/user duyet fix goc brokers._account_default_lp tra profile theo account_id (hoac sua injector:116).
- [2026-09-13T06:27:23Z] cq-20260913 #1: patch v2 (research/cq20260913_batch1_item1_v2.patch, commit 063dd83f) = v1 + fix goc profile-lp, 2 vong arch APPROVE. CHO Mike apply v2 THAY v1 T2 14/09 sau 15:00 + chay selfcheck cuoi patch. Van CHO user quyet co nav_include_egg_offbook (khuyen nghi OFF).
- [2026-09-13T07:10:15Z] [2026-09-13] aria-F XONG (F1 5f8c3ba2, F2 4a02f23a). CHO user: dong bo phi 0,097% vao duong thuc thi (trading_bot/plan_funding_gate.py FEE_RATE + merge_park_orders.py fee_est_vnd + prompt bq_freshness_check.sh) cung luc. CHO Mafee/Winston: dnse_raw+journal ZaloPay 07-10 thieu order VHC 600cp. BAY: commit o mike repo khi co job song song -> index bi git add lan; dung GIT_INDEX_FILE tam + commit-tree voi danh sach file tuong minh.
- [2026-09-13T07:18:46Z] cq-20260913 remove-v23 (job _064725): patch research/cq20260913_remove_v23.patch (+ _mike_docs.patch), commit 2a067741, arch APPROVE. CHO Mike apply T2 14/09 sau 15:00 theo thu tu v2 -> remove (git apply --index) -> mike_docs; co nav_include_egg_offbook bi go => khong con cho user quyet.
- [2026-09-13T08:33:11Z] aria-H (job _075547): A commit 3d6f4265 XONG. CHO Mike apply B research/aria_H_20260913/plan_funding_gate_fee.patch T2 14/09 >=15:00 SAU v2+remove_v23 (commit rieng) + cp plan_funding_gate_fee_sync_selfcheck.py vao mike/bin cung luc (dat som = run_selfchecks do).
- [2026-09-13T10:07:42Z] aria-K (job _091014) patch v2 arch APPROVE, commit mike 430fa526. CHO Mike apply T2 14/09 >=15:00 SAU v2->remove_v23->aria_H (commit rieng). Backfill VHC 07-10 CHUA chay: can ve raw verify_account_snapshot cong missing_fills_broker_confirmed truoc. Question mo: heartbeat --once dependency.
- [2026-09-14T01:08:46Z] [2026-09-14] CHO user/Mike: question zalopay-tv1-200cp-sized-by-dgc-dividend-receivable-0914 — lenh TV1 200cp ZaloPay do co tuc DGC 80tr (excluded) trong active_nav; neu chon C thi sua compute_active_nav (can review). TV1: can xac nhan An Viet kiem toan FY2026 + ban an van ban 17,6 ty.
- [2026-09-14T15:43:10Z] [2026-09-14] oshares forward-absorption (job _151805): branch fix/oshares-finfallback-double-count eded0afe (worktree /home/trido/thanhdt-wt-oshares-finfb-dblcount) CHO Mike+arch-reviewer land; ngay land VIB se publish kem MODEL_REBASE (tac dung phu model_version, khong phai so doi); registry .proposed Bay 3.
- [2026-09-14T16:20:38Z] [2026-09-14] oshares fwd-absorption vong 2 (job _160309): bc86963e tren branch fix/oshares-finfallback-double-count (chua merge), verify xanh ca cong publish that. CHO Mike+arch-reviewer vong 3 land. De xuat viec rieng: ~20 check song BQ san co trong oshares_live selfcheck (cung lop rui ro cong do).
- [2026-09-14T17:09:16Z] [2026-09-15] oshares freeze live selfcheck (job _164512): ce123789 tren test/oshares-freeze-live-selfchecks (worktree thanhdt-wt-oshares-freeze-live) + mike 5c931f08. CHO Mike+arch-reviewer land SAU double-count; 2 viec Mike quyet: docstring gate_selfcheck con noi cham BQ, SC2 do oan theo ten thu muc.
- [2026-09-14T17:46:47Z] [2026-09-15] corp_action_feed_canary (job _173213): 2465a35c tren feat/corp-action-feed-canary (worktree mike/agents/wt-corp-feed-canary), CHUA merge/CHUA cai cron — CHO Mike+arch-reviewer. Question mo: corp-action-snapshot-schema-drift-20260914 (snapshot fail tu 09-14, vendor them 2 cot).
- [2026-09-14T18:04:21Z] [2026-09-15] A-prime snapshot_corp_action (job _175556): bbbb9b80 tren fix/corp-action-snapshot-schema-aprime (worktree mike/agents/wt-corp-snapshot-aprime), CHUA DDL/merge — CHO user duyet DDL + Mike merge truoc 06:50 ICT theo APPLY_A_PRIME.md; question schema-drift chua dong.
