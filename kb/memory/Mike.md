# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- Go-live V2.4: 2026-06-30 — **Spyros CONDITIONAL GO ✓ — chờ user approval**

## Đang chờ
- **DollarBill (bg)**: đang tạo plan paper 2026-06-27
- **User**: (1) số tiểu khoản DNSE của SpaceX để wire vào config; (2) approve go-live (flip applies_to→live)
- Wendy: legal-severity DGC → advisory

## Fleet (cập nhật 2026-06-26)
- DollarBill + Mafee: **ĐANG CHẠY** — paper mode, dry-run
- Mike + Taylor: active, serving

## Go-live account
- **SpaceX** = tiểu khoản DNSE mới, user đã nạp **1B VND tiền thật**
- Bill + Mafee go-live SẼ CHẠY TRÊN SpaceX (không phải dnse_main 0001743768)
- CẦN: account_id (số TK DNSE SpaceX) → thêm vào trading_bot_accounts.json

## Spyros conditions (V2.4 go-live)
1. RECOVERY_WMAX=0.95 ✓ | 2. DEP_FLOOR=7.5% DORMANT ✓ | 3. max_gross=1.0 ✓
4. RECOVERY_PARK trigger ✓ | 5. trading_rules v1.7 ✓ | 6. get_gated_state() ✓ | 7. Review 90d ✓
- Gap còn lại: account_id SpaceX + user approval flip

## Trước go-live 30/06
1. User cung cấp account_id SpaceX DNSE → wire config
2. User flip applies_to→"live" + approved_by→"user" trong trading_rules.json

## Corp-action pending — SẠCH (2026-06-24)
## Kill-switch (trading_rules v1.7): SBV/pb_z/DD ✓

