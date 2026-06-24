# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên
- Go-live V2.4: 2026-06-30 — **Spyros CONDITIONAL GO ✓ — chờ user approval**
## Đang chờ
- **User**: approve go-live V2.4 — mọi điều kiện Spyros đã rõ ràng
- Wendy: legal-severity DGC → Taylor risk/reward
## Spyros conditions (V2.4 go-live)
1. RECOVERY_WMAX=0.95 giữ nguyên
2. DEP_FLOOR=7.5% DORMANT không hạ
3. max_gross_exposure=1.0 enforce cứng trong Mafee
4. RECOVERY_PARK trigger KHÔNG mở rộng ngoài {CRISIS,BEAR}+pb_z≤-0.5
5. trading_rules v1.6 wire trước 2026-06-30
6. get_gated_state() là nguồn regime duy nhất
7. Review 90 ngày sau go-live nếu episode 3 fire
## Kill-switch (Spyros)
- SBV rate > 7.5% → suspend RECOVERY_PARK
- pb_z median > -0.3 trong khi episode active → forced unwind
- Intra-episode DD > -12% từ entry → circuit breaker
## Real-margin 1.3x (post-go-live, chưa live)
- Cần: paper ≥90 ngày + per-year breakdown từ Taylor + sandbox Mafee test
- MGE=1.5x: BLOCK vĩnh viễn. deposit_eyield gate: BLOCK (DD-31.7% confirmed)
## R&D đã đóng
- Exp-2 hold-neutral: REJECTED
- Exp-3 deposit_eyield: REJECTED BQ-pinned (DD-31.7%)
- fedborrow-dormant (32.22%/DD-15.5%/Cal 2.08): post-go-live candidate, Spyros pending 90d
- PE bug NOT MATERIAL

