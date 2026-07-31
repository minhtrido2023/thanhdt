# V2.3 + DT5G — Daily Recommendations — 2026-07-30

*Generated 2026-07-30 19:07. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 49% (as of 2026-07-29) → trong band ±10pp, không rebalance
- **Parking (cả 2 book):** park **70%** cash nhàn rỗi vào **rổ custom30V** (`tav2_bq.custom30v_8l`, yieldcombo, cap-weight namecap≤10%, 30 mã) (NEUTRAL)
    - top: CTG 10% · BID 10% · VHM 10% · VCB 10% · TCB 9% · VPB 8% · MBB 8% · LPB 5% …

## BAL book (50% NAV target) — 1 picks

| ticker | tier | 8L | ta | close_bq_stale (CẤM dùng làm ref_price — giá BQ trễ ≥1 phiên, ref_price phải lấy DNSE live) | sector | weight (of book) |
|---|---|---:|---:|---:|---:|---:|
| AGG | RE_BACKLOG_BUY | 3 | 121 | 11750.0 | 8 | 10% |

_Informational (ngoài tier BAL, V2.3 không trade):_ VTO(COMPOUNDER_BUY), PHP(COMPOUNDER_BUY), VVS(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

_(không có entry PEAD đến hạn phiên tới)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **10.0%** vs gate 31%
- Gate chưa kích hoạt — sleeve dormant.

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD AGG [BAL] (data 2026-07-29): thanh khoản OK (ADV3T 2.28 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 9.6% · ROE_Min3Y 6.8% · FSCORE 3 · D/E 0.53 · PE 4.87
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 20.5% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD DGC [PARK] (data 2026-07-29): thanh khoản OK (ADV3T 27.09 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE,IDIOCRASH] ngày 2026-07-23
  FA: ROE5Y 37.3% · ROE_Min3Y 21.3% · FSCORE 4 · D/E 0.19 · PE 6.62
  🟢 DCF: CHEAP (giá trị hợp lý ~76,501đ vs giá 37,850đ, MoS +50.5%, robust)
- DD EVF [PARK] (data 2026-07-29): thanh khoản OK (ADV3T 29.84 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 8.0% · ROE_Min3Y 5.1% · FSCORE 3 · D/E 7.81 · PE 9.39
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.87 (band cheap <1.8), ROE_TTM 9.6% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD LPB [PARK] (data 2026-07-29): thanh khoản OK (ADV3T 88.36 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE] ngày 2026-06-24
  FA: ROE5Y 21.9% · ROE_Min3Y 19.2% · FSCORE 4 · D/E 13.30 · PE 13.91
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 3.65 vs hợp lý 2.12 (ROE5Y 21.9%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD MBS [PARK] (data 2026-07-29): thanh khoản OK (ADV3T 71.76 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 14.7% · ROE_Min3Y 12.3% · FSCORE 7 · D/E 1.86 · PE 14.37
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 P/B band + ROE (chứng khoán): P/B 1.48 (band cheap <1.8), ROE_TTM n/a (cần >8%) — RICH [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD PC1 [PARK] (data 2026-07-29): thanh khoản OK (ADV3T 78.19 tỷ/phiên) · ⚠ cờ chất lượng BANNED
  FA: ROE5Y 10.0% · ROE_Min3Y 1.7% · FSCORE 4 · D/E 1.74 · PE 7.58
  🟢 DCF: CHEAP (giá trị hợp lý ~37,031đ vs giá 21,500đ, MoS +41.9%, robust)
- DD SHS [PARK] (data 2026-07-29): thanh khoản OK (ADV3T 193.19 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-20
  FA: ROE5Y 11.7% · ROE_Min3Y 5.7% · FSCORE 1 · D/E 1.20 · PE 13.42
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.08 (band cheap <1.8), ROE_TTM 8.1% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VCB [PARK] (data 2026-07-29): thanh khoản OK (ADV3T 237.00 tỷ/phiên)
  FA: ROE5Y 20.4% · ROE_Min3Y 16.7% · FSCORE 4 · D/E 9.90 · PE 12.69
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 1.95 vs hợp lý 1.93 (ROE5Y 20.4%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD VGC [PARK] (data 2026-07-29): thanh khoản OK (ADV3T 13.49 tỷ/phiên)
  FA: ROE5Y 16.6% · ROE_Min3Y 13.7% · FSCORE 5 · D/E 1.22 · PE 11.50
  🔴 DCF: RICH (giá trị hợp lý ~21,658đ vs giá 36,500đ, MoS -68.5%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD VIX [PARK] (data 2026-07-29): thanh khoản OK (ADV3T 403.99 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 15.6% · ROE_Min3Y 5.3% · FSCORE 1 · D/E 0.18 · PE 7.57
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.91 (band cheap <1.8), ROE_TTM 19.0% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VND [PARK] (data 2026-07-29): thanh khoản OK (ADV3T 244.64 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 15.3% · ROE_Min3Y 9.5% · FSCORE 6 · D/E 1.33 · PE 9.25
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.16 (band cheap <1.8), ROE_TTM 12.8% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- ✅ PARK không cờ (20): ACB, BID, CTG, DBC, DCM, HAH, HDB, HHV, IDC, MBB, MSB, PVT, SHB, TCB, TPB, VHC, VHM, VIB, VPB, VRE

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-07-30.csv` | status: `data/golive_v23_status.json`