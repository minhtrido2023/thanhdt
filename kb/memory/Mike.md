# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- **Go-live V2.4: 2026-07-01 08:00 ICT** — cron tự động flip SpaceX enabled=true + restart Bill+Mafee

## Fleet (2026-07-01)
- DollarBill + Mafee: ĐANG CHẠY paper mode — dry-run đến 30/06
- Mike + Taylor: active

## Go-live — ĐÃ SETUP HOÀN TOÀN
- SpaceX / 0002023347 / DNSE: 1B VND, enabled=false (cron flip 01/07 08:00 ICT)
- trading_rules v1.7: applies_to=live, approved_by=user, live_effective=2026-07-01 ✓
- Cron: `0 1 1 7 * golive_01jul.sh` — tự flip + restart + Telegram notify
- Script: mike/bin/golive_01jul.sh

## Telegram report (Taylor đang dọn)
- Xoá: VOL-SPIKE V5, F-SYSTEM, ORB, AMH Cockpit V6, V2.3 NAV-only
- Thêm: V2.4 paper-trade section với buy/sell detail từ plan files

## Paper dry-run (nay đến 30/06)
- Plan 2026-06-27 đã tạo (state NEUTRAL, custom30V basket)
- Bill tạo plan T+1 mỗi EOD; Mafee paper-execute; Telegram report daily 18:00 ICT

## Advisory
- DGC trong custom30V rank 21 — Wendy legal check (không phải blocker)

- [2026-06-27T10:59:55Z] ## Đang chờ
- Taylor job Taylor_20260627_105942: validate IC của 4 delta signals (ΔFSCORE, ΔNP_R acceleration, ΔCashCycle, ΔRevenue) cho 8L screener — IS/OOS walk-forward. Khi xong: quyết định wire delta nào vào screener (tiebreaker hay value_score adjustment).
- [2026-06-27T11:09:17Z] ## Đang chờ
- (Cleared: Taylor_20260627_105942 đã xong)

## Findings 8L delta-momentum (2026-06-27)
- ΔNP_R IC=0.083/OOS=0.104: WIRE ✅ (strongest)
- ΔFSCORE IC=0.057/OOS=0.073: WIRE ✅
- ΔRevenue: optional (redundant w/ ΔNP_R)
- ΔCashCycle: REJECT ❌
- Cách wire: tiebreaker sort TRONG rating tier, KHÔNG fold vào value_score
- Chờ user quyết định: wire vào rating_8l.py hay chỉ expose cột mới?
- [2026-06-27T11:16:47Z] ## Đang chờ
- Taylor job Taylor_20260627_111639: backtest delta_momentum tilt vào custom30V IS/OOS. Verdict cần: OOS CAGR + Calmar cả hai tốt hơn mới WIRE. Kết quả sẽ về qua Telegram.
