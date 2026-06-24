# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- Go-live V2.4: 2026-06-30 — **Spyros CONDITIONAL GO ✓ — chờ user approval**
## Đang chờ
- **User**: approve go-live V2.4 (LF config)
- **Spyros**: exp8-risk-review — dispatched 2026-06-24T15:21 (pid 801284, bg), đang review MGE=1.3 CAPIT-ONLY
  - Q1: approve MGE=1.3 cho go-live promotion không?
  - Q2: slow-grind early-fire risk + guard?
  - Q3: Signal B giữ/bỏ?
  - Q4: trading_rules v1.6 cần update gì?
  - Log: mike/logs/dispatch_Spyros_20260624_152135.log
- Wendy: legal-severity DGC → Taylor risk/reward
## Spyros conditions (V2.4 go-live — unchanged)
1. RECOVERY_WMAX=0.95 | 2. DEP_FLOOR=7.5% DORMANT | 3. max_gross=1.0 enforce cứng
4. RECOVERY_PARK trigger không mở rộng | 5. trading_rules v1.6 trước 2026-06-30
6. get_gated_state() duy nhất | 7. Review 90d sau nếu episode 3 fire
## R&D real-margin — ĐÃ ĐÓNG (2026-06-24)
Tất cả 6+ hướng không beat V2.4-LF về Calmar. V2.4 (30.63%/DD-17.5%/Cal 1.75) vẫn là best.
## V2.5 building blocks (post-go-live)
- Exp-8 Test A: CAPIT vol-1.7x/3M + MGE=1.3. +3.03pp CAGR/+11pp MaxDD/+0.63 Cal vs same-snapshot baseline.
  Awaiting Spyros risk review → nếu approve = candidate V2.5.
- RECOVERY_GRADUAL=1 + RECOVERY_ACCEL=1: accel filter genuine improvement vs plain gradual.
## Kill-switch (Spyros): SBV>7.5% / pb_z>-0.3 intra-episode / DD>-12% circuit breaker
## PE correction: applied to rating_8l.py (Price/Close adjustment)

