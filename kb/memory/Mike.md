# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- Go-live V2.4: 2026-06-30 — **Spyros CONDITIONAL GO ✓ — chờ user approval**
## Đang chờ
- **User**: approve go-live V2.4
- Wendy: legal-severity DGC → Taylor risk/reward
## Spyros conditions (V2.4 go-live — unchanged)
1. RECOVERY_WMAX=0.95 | 2. DEP_FLOOR=7.5% DORMANT | 3. max_gross=1.0 enforce cứng
4. RECOVERY_PARK trigger không mở rộng | 5. trading_rules v1.6 trước 2026-06-30
6. get_gated_state() duy nhất | 7. Review 90d sau nếu episode 3 fire
## Kill-switch (Spyros): SBV>7.5% / pb_z>-0.3 intra-episode / DD>-12% circuit breaker
## Real-margin R&D — PIVOT (quyết định 2026-06-24)
- fedborrow gate: DEAD (cấu trúc) — VN PE 10-17x, eyield 5.7-9.1% < 10% borrow, 0 events fired
- deposit_eyield gate: REJECTED (DD-31.7%)
- → Spyros đề xuất PIVOT sang "signal-conviction gate": CAPIT + CRISIS/BEAR + postbull clear + Pillar B off
- Per-year breakdown (MGE=1.3 fedborrow ≡ unleveraged): chỉ 1 năm âm (2022: -4.3%), 2020 DD -31.5% OK, 2025 lag OK
- V2.4 CONDITIONAL GO không bị ảnh hưởng
## R&D đã đóng
- Exp-2 hold-neutral: REJECTED | Exp-3 deposit_eyield: REJECTED | fedborrow gate: DEAD cấu trúc
- PE correction: applied to rating_8l.py (PE * Price/Close)

