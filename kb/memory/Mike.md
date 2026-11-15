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

