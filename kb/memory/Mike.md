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

