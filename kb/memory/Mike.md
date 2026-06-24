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
## Real-margin R&D — TẤT CẢ GATES ĐÃ THỬ (2026-06-24)
- fedborrow (10%): DEAD — 0 events (eyield 5.7-9.1% < 10% borrow cấu trúc VN)
- deposit_eyield: REJECTED — misfire COVID 2020, DD -31.7% (BQ-pinned)
- conviction (CRISIS+postbull+PillarB): FAIL — Pillar B dormant trong CRISIS (DT5G đã cap trước), -2.01pp vs baseline
- KLUẬN: không có gate khả thi nào tìm được. DT5G đã làm hầu hết việc của conviction gate rồi.
- Next option: unconditional leverage (no gate) cần Spyros riêng, hoặc SHELF real-margin R&D
## R&D notes
- PE correction: applied to rating_8l.py
- Per-year breakdown (V2.4 equivalent): 1 năm âm/13 năm (2022: -4.3%), 2020 MaxDD -31.5% OK

