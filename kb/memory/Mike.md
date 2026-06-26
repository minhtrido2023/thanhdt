# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- Go-live V2.4: 2026-06-30 — **Spyros CONDITIONAL GO ✓ — chờ user approval**

## Fleet (2026-06-26)
- DollarBill + Mafee: ĐANG CHẠY, paper mode — cả 2 đã nhận SpaceX account info
- Mike + Taylor: active, serving

## Go-live account — WIRED ✓
- **SpaceX** = tiểu khoản DNSE **0002023347**, NAV 1B VND tiền thật
- `enabled=false` trong trading_bot_accounts.json — bật khi user flip trading_rules
- dnse_main (0001743768) = TK riêng, KHÔNG phải go-live V2.4

## Chỉ còn 2 bước để go-live (30/06)
1. User flip `applies_to → "live"` + `approved_by → "user"` trong `/home/trido/thanhdt/WorkingClaude/data/trading_rules.json`
2. Set `enabled=true` cho SpaceX trong `secrets/trading_bot_accounts.json`

## Paper dry-run đang chạy
- Plan 2026-06-27 đã tạo (DollarBill) — state NEUTRAL, custom30V basket

## Spyros conditions — TẤT CẢ ĐÃ ĐỦ ✓
1. RECOVERY_WMAX=0.95 ✓ | 2. DEP_FLOOR=7.5% DORMANT ✓ | 3. max_gross=1.0 ✓
4. RECOVERY_PARK trigger ✓ | 5. trading_rules v1.7 ✓ | 6. get_gated_state() ✓ | 7. Review 90d ✓

## Advisory (không phải blocker)
- Wendy: legal-severity DGC (trong custom30V rank 21, HOSE audit ngoại trừ)

