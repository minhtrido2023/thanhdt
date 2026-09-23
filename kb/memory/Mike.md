# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Retro 2026-09-23 XONG (6 sự cố, 3 pattern, Wags GAPS FOUND→đã sửa, commit `6d320fad`).
  Pattern 1 (approval-gate trễ) CHỐT sau 3 lần tái diễn — cron `plan_approval_reminder.sh`
  08:50 ICT go-live hôm nay, chưa qua chu kỳ nhiều ngày, theo dõi tuần tới.
- NAV corp-action gate v2 (L2-L4) LANDED master `4dcc3643`. Runbook rc=5 mới **CHỜ MIKE DUYỆT
  ĐƯA LIVE** — `kb/ops_runbook.md.proposed` §13.
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải
  chạy approve_margin_day.py TRƯỚC bot.

## Việc đang mở / cần theo dõi
1. **`test_trading_bot.py:353`** (raw `p["broker"]`/`p["mode"]`) — CHƯA sửa, quá hạn 2 ngày liên
   tiếp (deadline gốc "trước retro 09-22"). Cần dispatch cụ thể ai sửa.
2. **`question wags-fix-not-confirmed: coord-2026-09-23`** vẫn TREO cuối ngày 09-23 — arch-reviewer
   NEEDS_CHANGES cho finding `wags-fix: coord-2026-09-23`, chưa có finding/answer sửa theo sau.
   Root cause: root_cause sai + mô tả hành vi hệ thống sai vẫn đứng nguyên trên bus.
3. **Pattern 2 CHƯA sửa gốc** (retro-2026-09-23): `daily_retro.sh:195` sinh topic escalate nhúng
   bộ đếm ngày (`retro-pattern-recurring-<n>-days`) khiến ack theo topic khớp tuyệt đối không
   phủ được khi topic đổi số — ≥6 lần cùng gốc. Hướng sửa: tách `recurrence_count` ra payload
   riêng, topic ổn định theo tên pattern. Chưa đủ ngưỡng "2 retro liên tiếp" để bắt buộc — nếu
   lặp ở retro 09-24 phải escalate ngay.
4. **NAV corp-action gate v2 rc=5 runbook** — chờ Mike duyệt đưa live.
5. **universe-pit-migration G7/G8/G9** — ~9 tuần treo, chờ user chọn A (dispatch Taylor làm dứt
   điểm) hay B (đóng hẳn). G8.1 đã đóng 09-20.
6. **excluded_dividend_receivable[DGC]** (ZaloPay) cần dọn config sau khi tiền DGC về thật
   (~2026-09-25).
7. Treasury buyback/corp_action mở rộng (Taylor branch feat/treasury-share-events-table) — chờ
   user duyệt chính thức.
8. FiinPro/OShares harvest dừng 09-15 ở 4/59 lô — chưa có selfcheck/commit xác nhận.

- [2026-09-23T17:52:24Z] 24/09 00:5x — exdate price-frame ĐÃ LAND: mike master 508bb607, arch-review APPROVED sau 3 VÒNG. current_ops đã ghi (1656990a). Selfcheck từ master 59/59 qua 5 TZ + corp_action 85/0.
SỐ ĐÃ ĐÚNG cả 2 account (Mike chạy lại lúc 00:5x): SpaceX VPB 1.386 × 22.050 = 30.561.300, active_nav 982.294.013; ZaloPay VPB 1.512 × 22.050 = 33.339.600, active_nav 520.678.926; computed_at 2026-09-24.
Dispatch DollarBill_20260923_175136 LẬP LẠI plan 24/09 cả 2 account trên số mới (plan cũ BÁN VPB 200cp/100cp ref_price 27.800, CHƯA duyệt nên không có lệnh nào chạy).
ĐÃ ĐẾM 5 CALL-SITE CÙNG LỚP CHƯA VÁ — thứ tự ưu tiên: (1) dividend_adjusted_return.py:473-478 chạm SỐ CÔNG BỐ nhà đầu tư §21; (2) discretionary_margin_gate.py:335 sleeve margin tiền thật, latent; (3) report_return_gate.py lỗ hổng phủ im lặng; (4) discretionary_accumulation_inject.py:124 baseline hỏng vĩnh viễn; (5) due_diligence.py adv_vnd() chiều an toàn không gấp.
NỢ VỆ SINH: compute_active_nav.py:616 chưa atomic (§5, đóng luôn lỗ hardlink); bản CŨ mike/.claude/worktrees/wags-fix-coord-08-19/bin/compute_active_nav.py ghi thẳng canonical với bug gốc (grep exdate_frame = 0); runbook rc=6/rc=7.
⚠️ arch-reviewer KHÔNG khẳng định đã quét hết lớp lỗi này — không tuyên bố đã đóng.
