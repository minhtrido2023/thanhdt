# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- Go-live V2.4: 2026-06-30 — **Spyros CONDITIONAL GO ✓ — chờ user approval**

## Đang chờ
- **User**: approve go-live V2.4 (LF config)
- Wendy: legal-severity DGC → Taylor risk/reward

## Corp-action pending — SẠCH (2026-06-24)
- corp_action_pending.json = {} (rỗng)
- Quy tắc: chỉ track ticker có trong ticker_prune (ADV 3M ≥ 1 tỷ VND). Ngoài prune = illiquid, không giao dịch, bỏ qua.
- Quy tắc detect: Cash div → OShares không đổi = expected. Stock bonus → so OShares trước/sau ex_date trong ticker_prune. CẢNH BÁO: Price có thể bị stale (ETL bug, VVS June 2026) → cross-check với ngày trước ex_date thực sự, không phải ngày kề trước.

## Spyros conditions (V2.4 go-live — unchanged)
1. RECOVERY_WMAX=0.95 | 2. DEP_FLOOR=7.5% DORMANT | 3. max_gross=1.0 enforce cứng
4. RECOVERY_PARK trigger không mở rộng | 5. trading_rules v1.6 trước 2026-06-30
6. get_gated_state() duy nhất | 7. Review 90d sau nếu episode 3 fire

## V2.5 building blocks (post-go-live)
- Exp-8 Test A: CAPIT vol-1.7x/3M + MGE=1.3 — Spyros reviewed, MGE sensitivity confirmed sweet spot
- RECOVERY_GRADUAL=1 + RECOVERY_ACCEL=1: genuine improvement vs plain gradual

## Kill-switch (Spyros): SBV>7.5% / pb_z>-0.3 intra-episode / DD>-12% circuit breaker
## PE correction: applied to rating_8l.py (Price/Close adjustment)

## CÁCH GIAO VIỆC ĐÚNG (updated 2026-06-24)
LUÔN dùng: `bin/dispatch.sh <agent> "prompt"` (sync) hoặc `--bg` (>10 min)
KHÔNG dùng: inbox/append_event directive cho task cần kết quả ngay

