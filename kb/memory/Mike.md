# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI. Plan T+1 2026-09-14 đã HOLD_ALL đúng.
- T2 14/09 = ex-date DGC cổ tức tiền 8.000đ (ZaloPay). xcheck NAV tối 14/09 có thể CHẶN (tự nhận diện KHÔNG
  ship, user chốt (a) GIỮ TAY 09-12) → xử lý TAY theo kb/ops_runbook.md § PRICE_XCHECK (kiểm bất biến §21
  trước khi bỏ qua cổng). KHÔNG hỏi lại user.

## 12/09 — TOÀN BỘ việc user chốt đã XONG, bus 0 pending (verify 15:20 ICT)
5 việc 12:18 + 3 việc treo 14:22 + (a) giữ tay xcheck. Chi tiết commit: incident
kb/incidents/2026-09/2026-09-12-report-return-gate-worktree-root.md (mục Còn treo cập nhật 15:13).
- Sổ giao hàng báo cáo ghim về cây canonical (wc_paths.find_mike_canonical_root, KHÔNG nhận env override;
  fallback warn stderr + dirname×2). Mike verify: gate selfcheck 7/7, ledger selfcheck (chạy 15:20),
  ledger canonical 66 entry nguyên vẹn, checker #14 worktree_stale_check WARN-ONLY sống (4 cây đang dùng
  tiền-vá: mike_paseo, wt-1522576692638388364, wt-1536246356098814022, wt-wags-selfcheck-batch).
- ⚠️ SỰ THẬT CLIENT-FACING: monthly report 2026-08 ĐÃ GỬI 2 LẦN cho nhà đầu tư (28/08 từ mike_paseo sha
  0eb03df4, 02/09 từ canonical sha 9464d365) — sổ canonical không biết lần đầu. Ledger KHÔNG ghi lần 28/08
  (CLASH, merge tool từ chối đè — đúng); ghi bền ở incident. Không có lần gửi trùng nào khác.
- arch-review VIỆC A dừng vòng 2 NEEDS_CHANGES (luật 2 vòng); commit cuối 781a36b3 KHÔNG được review lại —
  Mike spot-review: bỏ env override cho canonical root = đúng hướng; selfcheck phủ. Chấp nhận.
- Selfcheck cần source wc_env.sh + $DNA_PYEXE + đường dẫn TUYỆT ĐỐI (wc_env cd sang WorkingClaude); chạy
  trần python3 FAIL giả (gcloud auth).

## Còn mở có chủ đích (không khẩn, làm khi đụng tới)
- ~28 file bin/*.py cùng lớp dirname-x3 ngoài đường báo cáo (incident mục 5).
- bus_question_housekeeping.py:22 đọc sổ theo cây đang chạy (fail-safe, chỉ ảnh hưởng đóng question).
- find_stray_ledgers chưa quét cây WorkingClaude anh em; dọn state/*.bak-*.
- 4 worktree đang dùng chưa rebase (thuộc session khác — chỉ WARN).
- Pattern 2 tái diễn 09-12: 2 job Wags song song đụng daily_nav_snapshot.py ngoài --write-scope; consolidator
  git add -A quét nhầm 15 file KB vào commit job. Cân nhắc đưa vào retro tuần.

## R&D đã ĐÓNG HẲN tuần 09-05→09-11: AMH · CCS Phase 0-2 · BAL 5 vòng · custom30V 5 vòng · CCS/8L accruals.
## append_event.sh JSON isolation — pattern đã biết, không escalate (18+ lần, 0 mất dữ liệu).
## Sát ngưỡng OKF: kb/coding_guidelines.md 39,5KB/40KB — §-mới PHẢI tách _ext.md.

