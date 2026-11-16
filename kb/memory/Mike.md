# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 15/11 → 16/11
- Retro 15/11 ghi (kb/incidents/retro/retro-2026-11-15.md). Pattern 1 (BQ raw thủng) lặp 2 retro: retro 16/11 PHẢI kiểm wire [0b] ticker_integrity_precheck (nhánh fix/ticker-integrity-precheck-20261115) đã merge chưa; chưa ⇒ escalate.
## Đang chờ / mở
- Plan T+1 T2 16/11 đã dựng (2 account); user duyệt trước 08:45 (mirror topic plan 1521183164364754974). Hỏi user: cứu hộ plan ngày thường (late_plan_catchup MISSING).
- Weekly report 09–13/11: chưa xác nhận COMPLETE — chạy report_delivery_gate (cần user/classifier cho phép).
- sunday_plan_round/bq_freshness chạy tay từ phiên Mike phải đặt MIKE_WAKEUP_GATE=off (hoặc env -u CLAUDECODE); cân nhắc cho wrapper tự đặt.
- AI-momentum P1 (topic Momentum Lab 1571541823615406201): Taylor_20261115_170852 sửa 6 BLOCKER ⇒ arch-review vòng 2 (Opus) ⇒ merge (gồm nhánh Wags M2 0ab039b5f) ⇒ smoke test ⇒ USER cài cron 19:35 T2-T6 (Mike không tự cài).
- bus question code-reviewer/cq-2026-11-15-hard-boundary treo: chưa xử.
- Còn chờ user: PNJ Q3 A/B; classifier-denials-mike duyệt A; worktree dirty, bq_cache_asof 2x2G, book_regime_fit 943M (CHƯA xoá); DD PAT đã gửi email, mở: tờ trình DLC, BCTC Q4/26.
- 5 selfcheck-red thật chưa triage; RCA ETL kaffa_v2 (bq_admin); selfcheck_red_owner_sweep.sh hardcode opus/high — đề xuất hạ.
## Quyết định gần đây
- Livermore thu hẹp vai; chấm TAY LVR-STK FPT/NNC 03/12, VGS/NNC 10/12; LVR-2026-10-21 scorer tự chấm 18/11.
- NEO sizing DD: NAV ≤2 tỷ ⇒ DD5 ≈ −33%. 4 quy tắc DD-flag 02/11 giữ nguyên.

- [2026-11-15T18:01:38Z] [16/11 01:0x] arch-review vòng 2 = NEEDS_CHANGES: freshness 95% từ chối mọi thứ Hai (mất ~25% sự kiện) + max-turns rc≠0 bị xếp InfraError. Đã DỪNG polish theo cầu chì, hỏi user 'sửa tiếp (1 lượt nhỏ + review vòng 3 chỉ diff)' hay 'dừng'. Nhánh research/ai-momentum-p1-20261115 HEAD 17d1f7e1f chưa merge. Cron KHÔNG trước tối T3 17/11; cần smoke test live (ledger tạm, --max-turns 1 để kiểm rc) trước.
- [2026-11-16T01:11:59Z] [16/11 08:2x] User: mở topic mới + chạy đề xuất 'sửa tiếp'. Topic MỚI AI-Momentum Lab #2 = 1571694105111691406 (topic cũ 1571541823615406201 ĐÓNG, không poll). Dispatch Taylor_20261116_011145 (override round-cap, user duyệt) sửa hẹp freshness+max-turns+alert rc4+12 mutant. Phiên topic mới theo dõi (wake_thread). Sau: arch-review vòng 3 chỉ diff → merge → smoke test live sau 19:00 T2 → user cài cron (UTC 13:00/14:30/16:00).
- [2026-11-16T01:21:55Z] [16/11 08:4x] Mục H xong (xoá clone rw_20261113b.git; bundle 4GB đã mất từ trước; mike-fleet remote 6e313fc là tổ tiên HEAD). Weekly 09-13/11 SpaceX+ZaloPay vẫn INCOMPLETE do Q9 (cột VN-Index có cổ tức thiếu số, G5 lệch +0.52>0.5 ngày 11/11) — chờ user: sửa ETL rồi gửi lại HOẶC miễn Q9 tuần này. code-reviewer 6 finding hard-boundary + Winston SBV: chờ user quyết.
- [2026-11-16T01:25:28Z] [16/11 08:3x] Dọn rác xong: gỡ 11 worktree >3 ngày (backup dirty ~/worktree_dirty_backups_20261116), thêm cron disk_guard_daily 03:20 ICT (cache + cảnh báo ≥85%) + cron worktree outer 03:10. Đĩa 77%. GIỮ: bq_cache_asof (§8b, 0728=marker), book_regime_fit 943M; journal cần sudo; /tmp/wt-m2wrap (Wags).
- [2026-11-16T01:26:35Z] [16/11 08:3x] User duyệt B: (1) A=chờ ETL G5 rồi gửi lại 2 weekly; (2) sửa 2 lỗi medium (executor.py:2687 fill_lagging, bull_div_boost.py:45), 4 lỗi thấp để sau; (3) chấp nhận nguồn EAF 06/10 sau re-verify. Dispatch: Taylor_20261116_012626 (opus, KHÔNG merge, báo nhánh→Mike arch-review đường tiền→merge), Winston_20261116_012628 (RCA G5 11/11), Winston_20261116_012630 (SBV re-verify + đóng bus question). Sau G5 xong: chạy lại report_delivery_gate 2 weekly (SpaceX gửi nhà đầu tư ngoài). Đóng bus code-reviewer question khi merge xong.
- [2026-11-16T01:31:42Z] [16/11 08:3x] Taylor R3 xong 2ec32179e; đang arch-review vòng 3 (cầu chì: lỗi MỚI ⇒ dừng báo user). APPROVED→merge→smoke live sau 19:00→user cài cron.
- [2026-11-16T01:32:50Z] [16/11 08:4x] User duyệt A2 (waiver Q9 riêng 2 weekly 09-13/11, giữ ô 'chưa có số'+ghi chú G5) + SBV không cần nguồn 2 (ĐÃ ĐÓNG bus question). Dispatch Taylor waiver Q9 (opus). Sau: arch-review → merge → chạy report_delivery_gate thật 2 weekly (--topic trading_report). Song song Taylor_20261116_012626 (executor/bull_div) đang arch-review vòng 3?
- [2026-11-16T01:42:12Z] [16/11 08:5x] arch-review fix executor/bull_div = NEEDS_CHANGES cả 2 (A: fill_lagging nổ sai do HYBRID hoãn mua tới 11:00, 22/46 ngày-account; B: tracker.py _bq cũng shell=True). Đã dispatch Taylor vòng 2 (1 lượt, opus). Cầu chì: vòng 2 xong → arch-review CHỈ DIFF → merge; nếu lỗi MỚI → dừng báo user. Waiver Q9 job Taylor_20261116_013249 còn chạy; Taylor event: Livermore NOT_VERBATIM cả 2 weekly (cổng livermore-block có thể chặn tiếp — kiểm khi chạy gate).
- [2026-11-16T01:50:12Z] [16/11 09:0x] Waiver Q9 merged (23f286b50, arch-review APPROVED); 2 weekly 09-13/11 COMPLETE (Discord+email). Còn: Taylor_20261116_014210 vòng 2 executor/bull_div → arch-review chỉ diff → merge → đóng bus code-reviewer question. Non-blocking waiver: G5 bất kỳ qua, TypeError khi waivers không phải list (gom sau).
