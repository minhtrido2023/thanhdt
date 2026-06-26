# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- Go-live V2.4: 2026-06-30 — **Spyros CONDITIONAL GO ✓ — chờ user approval**

## Đang chờ
- **Taylor (bg)**: viết trading_rules v1.7 (macro kill-switch: SBV/pb_z/DD) — dispatch 2026-06-26
- **User**: approve go-live (flip applies_to→live + approved_by trong trading_rules.json)
- Wendy: legal-severity DGC → advisory, không phải blocker cứng

## Fleet (cập nhật 2026-06-26)
- DollarBill + Mafee: **ĐANG CHẠY** (enabled + serving) — paper mode, dry-run trước go-live
- Mike + Taylor: active, serving

## Spyros conditions (V2.4 go-live)
1. RECOVERY_WMAX=0.95 ✓ | 2. DEP_FLOOR=7.5% DORMANT ✓ | 3. max_gross=1.0 enforce cứng ✓
4. RECOVERY_PARK trigger không mở rộng ✓ | 5. trading_rules v1.6 ✓ (2026-06-23)
6. get_gated_state() duy nhất ✓ | 7. Review 90d sau nếu episode 3 fire
- Gap còn lại: macro kill-switch (Taylor đang làm → v1.7) + user approval

## Trước go-live 30/06
1. trading_rules v1.7 (macro kill-switch) — Taylor đang làm
2. User flip applies_to→"live" + approved_by→"user" trong trading_rules.json
3. DGC legal (Wendy) — advisory

## Corp-action pending — SẠCH (2026-06-24)
- corp_action_pending.json = {} (rỗng)

## Kill-switch (Spyros): SBV>7.5% / pb_z>-0.3 intra-episode / DD>-12% circuit breaker
## PE correction: applied to rating_8l.py (Price/Close adjustment)

