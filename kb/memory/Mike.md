# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI. Plan T+1 2026-09-14 đã HOLD_ALL đúng.
- T2 14/09 = ex-date DGC cổ tức tiền 8.000đ (ZaloPay). xcheck NAV tối 14/09 có thể vẫn CHẶN (cơ chế tự
  nhận diện KHÔNG ship) → xử lý TAY theo kb/ops_runbook.md § PRICE_XCHECK (kiểm bất biến §21 trước khi
  bỏ qua cổng). KHÔNG escalate hỏi user lại — quy tắc đã chốt 09-12.

## 5 việc user chốt 12/09 12:18 — XONG HẾT (verify artifact thật 13:35 ICT)
1. report_return_gate worktree ROOT: FIXED (dd2c0d28/e67e2abf/f28008ed, bin/wc_paths.py marker wc_env.sh,
   arch-review 2 vòng CONFIRMED). Selfcheck 11/11 — CHỈ pass khi source wc_env.sh (chạm BQ, cần
   CLOUDSDK_CONFIG); chạy trần python3 sẽ FAIL giả 1 test (gcloud auth). Runner cron có source nên OK.
2. DGC NAV gap = ex-date adj: đóng, quy tắc trong kb/canonical.md (bản SỬA tách cash vs stock dividend).
3. commit_collision_gate selfcheck: fixture tự chứa (ac5b636f), 49/49.
4. hit_details cron 19:05→19:12 + bin/wait_for_artifact.sh (fe6b0ccc, 19/19) + luật §14b ext + registry
   ghi INPUT/PRODUCER.
5. bq pin 202608 nhãn lệch: (a) giữ + cảnh báo registry (d02bb546).
- VIỆC 3 (xcheck tự nhận ex-date): DỪNG đúng luật 2 vòng — KHÔNG ship. Bản nháp cất
  agents/Wags/research/nav_exdate_xcheck_wip_20260912.patch. Lý do: cổng kiểm proxy không kiểm bất biến
  §21, nhánh delta<=0 im lặng ⇒ có thể đếm 2 lần 80tr (+8,15% NAV lọt sanity ±15%).

## Bus question đang mở (1) — CHỜ USER
- Wags/nav-xcheck-exdate-tu-dong-hoa-vong-3-hay-giu-tay-2026-09-12 — Wags + Mike khuyến nghị (a) GIỮ TAY.

## Việc treo mới từ job 052043 (ghi kb/incidents/2026-09/2026-09-12-report-return-gate-worktree-root.md)
1. 17 worktree vẫn chạy bản tiền-vá của report_return_gate.
2. ⚠️ state/report_delivery.json fork theo worktree ⇒ giao hàng từ worktree vô hình với check_report_cadence
   ⇒ NGUY CƠ GỬI TRÙNG báo cáo nhà đầu tư (cổng cũ vô tình chặn, vá xong thì thông). Cần việc riêng.
3. dispatch.sh --add-dir sandbox codex rộng hơn khi dispatch từ worktree.
4. ~28 file bin/*.py cùng lớp dirname-x3 (chỉ liệt kê, chưa sửa — chỉ cắn khi chạy từ worktree).
5. Pattern 2 tái diễn: 2 job Wags song song đụng daily_nav_snapshot.py ngoài --write-scope; job A nuốt hunk
   của B rồi tự trả lại. Consolidator git add -A làm commit quét nhầm 15 file KB (đã reset).

## R&D đã ĐÓNG HẲN tuần 09-05→09-11: AMH · CCS Phase 0-2 · BAL 5 vòng · custom30V 5 vòng · CCS/8L accruals.
## append_event.sh JSON isolation — pattern đã biết, không escalate (18+ lần, 0 mất dữ liệu).
## Sát ngưỡng OKF: kb/coding_guidelines.md 39,5KB/40KB — §-mới PHẢI tách _ext.md.

- [2026-09-12T07:24:18Z] 12/09 14:25: user chốt (a) GIỮ TAY xcheck ex-date (question đã đóng decided_by=user) + duyệt giải quyết 3 việc treo incident report-return-gate. Dispatch Wags 1 job gộp: A=pin report_delivery.json+lock về canonical (wc_paths.find_mike_canonical_root) + gộp 2 sổ lạc + selfcheck, arch-review max 2 vòng; B=checker worktree chạy bản tiền-vá (WARN, không tự rebase); C=xác nhận --add-dir là khôi phục ngữ nghĩa 08-10, chỉ sửa comment. Bus pending hiện = 0.
