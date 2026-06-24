# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- Go-live V2.4: 2026-06-30 — **Spyros CONDITIONAL GO ✓ — chờ user approval**

## Đang chờ
- **User**: approve go-live V2.4 (LF config)
- **Spyros**: exp8-risk-review — dispatched bg, đang review MGE=1.3 CAPIT-ONLY
- **Taylor**: exp8-mge-sensitivity — dispatched bg, test MGE 1.2/1.3/1.4/1.5
- Wendy: legal-severity DGC → Taylor risk/reward
- **BQ admin**: OShares cho 3 ticker còn pending (VVS lần 2, LHC, LBE)

## Corp-action pending (còn lại — 2026-06-24)
- VVS|2026-06-23: bonus lần 2 (~48%), OShares chưa update (43.05M → ~63.7M)
- LHC|2026-06-24: bonus ~108%, không có trong ticker_prune (illiquid) → cần shares_outstanding_live
- LBE|2026-06-24: bonus ~78%, không có trong ticker_prune (illiquid) → cần shares_outstanding_live

## Quy tắc daily corp-action check
- So sánh OShares trước/sau ex_date trong ticker_prune
- Cash div → OShares không đổi = EXPECTED, xóa khỏi pending (VCS, LCG, AMS đã làm mẫu)
- Stock bonus → OShares phải tăng tương ứng gross_adj_pct; nếu chưa → giữ pending
- Illiquid (không có trong prune) → cần Winston add vào shares_outstanding_live thủ công

## Spyros conditions (V2.4 go-live — unchanged)
1. RECOVERY_WMAX=0.95 | 2. DEP_FLOOR=7.5% DORMANT | 3. max_gross=1.0 enforce cứng
4. RECOVERY_PARK trigger không mở rộng | 5. trading_rules v1.6 trước 2026-06-30
6. get_gated_state() duy nhất | 7. Review 90d sau nếu episode 3 fire

## R&D real-margin — ĐÃ ĐÓNG (2026-06-24)
## V2.5 building blocks (post-go-live)
- Exp-8 Test A: CAPIT vol-1.7x/3M + MGE=1.3 — awaiting Spyros + MGE sensitivity
- RECOVERY_GRADUAL=1 + RECOVERY_ACCEL=1: genuine improvement vs plain gradual

## Kill-switch (Spyros): SBV>7.5% / pb_z>-0.3 intra-episode / DD>-12% circuit breaker
## PE correction: applied to rating_8l.py (Price/Close adjustment)

## CÁCH GIAO VIỆC ĐÚNG (updated 2026-06-24)
LUÔN dùng: `bin/dispatch.sh <agent> "prompt"` (sync) hoặc `--bg` (>10 min)
KHÔNG dùng: inbox/append_event directive cho task cần kết quả ngay

