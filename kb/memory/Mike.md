# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái fleet hiện tại (2026-06-30)
- **Taylor**: active (companion R&D)
- **DollarBill**: active, plan SpaceX 2026-07-01 đã tạo (state NEUTRAL)
- **Mafee**: running (paper mode cho đến go-live)
- **Winston/Spyros/Wendy**: native on-demand (daemon đã tắt 2026-06-25)

## Go-live 2026-07-01
- Cron `0 1 1 7 * golive_01jul.sh` — tự flip SpaceX/DNSE + Telegram notify lúc 08:00 ICT
- trading_rules v1.7: applies_to=live, approved_by=user, live_effective=2026-07-01 ✓
- Account SpaceX / 0002023347 / DNSE: 1B VND, enabled=false → flip ngày mai

## Research đã đóng (custom30V sweep 2026-06-30)
- Permanent Exclude × custom30V: không overlap (tất cả 7 tên nằm ngoài top-30)
- Backtest re-run excluding 7 tên: DO NOT WIRE (OOS đi ngang, IS -0.2pp)
- custom30V production giữ nguyên (30 mã, cap 0.10)
- Sector sweep 15 ngành: sector_watchlist_framework.md đã ghi (Taylor)

## Không có gì pending hiện tại
