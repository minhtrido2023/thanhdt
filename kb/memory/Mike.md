# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- Retro 2026-09-22 XONG (3 sự cố, Wags CONFIRMED, commit `7b7798d1`).
  **ESCALATE mở**: `retro-pattern-recurring-plan-approval-gate-3days` — Pattern 1 (approval gate
  trễ ngay trước giờ bot chạy) tái diễn 3 lần (09-14 trễ 38' → 09-21 trễ 5' → 09-22 trễ 3'), 2
  retro liên tiếp cùng pattern. Cần user quyết: thêm lớp nhắc-duyệt sát giờ mở cửa (~08:45 ICT)
  hay chấp nhận nguyên trạng (gate an toàn, chỉ mất vài phút thực thi mỗi lần).
- NAV corp-action gate v2 (L2-L4) LANDED master `4dcc3643` (5 vòng arch-review, selfcheck
  38/0+64/0+8/0 qua 3 TZ). Runbook rc=5 mới **CHỜ MIKE DUYỆT ĐƯA LIVE** — `kb/ops_runbook.md.proposed` §13.
- `nav-price-xcheck-stuck` DRI (09-21) ĐÃ ĐÓNG 09-22 13:31Z — không còn theo dõi riêng.

## Việc đang mở / cần theo dõi
1. **`test_trading_bot.py:353`** (raw `p["broker"]`/`p["mode"]`) — CHƯA sửa, đã QUÁ HẠN (deadline
   "trước retro 09-22" đã trôi qua). Cần dispatch cụ thể ai sửa — chưa làm.
2. **Escalate approval-gate 3-day pattern** (xem trên) — chờ user trả lời.
3. **NAV corp-action gate v2 rc=5 runbook** — chờ Mike duyệt đưa live.
4. **universe-pit-migration G7/G8/G9** — ~9 tuần treo, chờ user chọn A (dispatch Taylor làm dứt
   điểm) hay B (đóng hẳn). G8.1 đã đóng 09-20.
5. **excluded_dividend_receivable[DGC]** (ZaloPay) cần dọn config sau khi tiền DGC về thật
   (~2026-09-25).
6. Treasury buyback/corp_action mở rộng (Taylor branch feat/treasury-share-events-table) — chờ
   user duyệt chính thức.
7. FiinPro/OShares harvest dừng 09-15 ở 4/59 lô — chưa có selfcheck/commit xác nhận.

