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
## Real-margin R&D — tổng kết (đã đóng 2026-06-24)
- fedborrow gate: DEAD (cấu trúc VN)
- deposit_eyield: REJECTED (DD-31.7%)
- conviction gate: FAIL (PillarB redundant với DT5G)
- MGE_GATE=none: không cải thiện (postbull size=0 × leverage = 0)
- deep-value override: hypothesis sai (2022-04 pb_z=+1.72, không rẻ)
- Gradual+capit Test B (BQ-pinned): REJECT — CAGR +0.05pp vs V2.4-LF nhưng MaxDD -30% vs -17.5% (12pp tệ hơn). Leverage 2022 multi-event cluster amplify dips không tỷ lệ.
- INSIGHT: Tier-1 vs BQ discrepancy đã mislead — Tier-1 baseline cũng xấu (-31.6%) nên Test B trông better, nhưng BQ V2.4-LF baseline thực ra tốt hơn (-17.5%).
## Gradual entry (Test A, no leverage) — chưa BQ verify
- Tier-1: +0.46pp CAGR, better DD. Cần BQ Tier-3 để biết thực có additive không.
- Nếu pass BQ: có thể wire vào V2.4 như "smoother entry" upgrade (không cần Spyros vì no leverage)
## R&D notes: PE correction applied to rating_8l.py

