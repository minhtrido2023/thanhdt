# V2.3 + DT5G — Daily Recommendations — 2026-09-25

*Generated 2026-09-25 19:06. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 48% (as of 2026-09-24) → trong band ±10pp, không rebalance
- **Parking (cả 2 book):** park **80%** cash nhàn rỗi vào **rổ custom30V** (`tav2_bq.custom30v_8l`, yieldcombo, cap-weight namecap≤10%, 30 mã) (NEUTRAL)
    - top: BID 10% · VCB 10% · VHM 10% · CTG 9% · TCB 8% · VPB 7% · MBB 7% · HPG 7% …

## BAL book (50% NAV target) — 0 picks

_No new BAL entries today_ — không có signal đạt chuẩn trong các tier BAL (MEGA/MOMENTUM*/DVR/RE_BACKLOG) sau SV_TIGHT/overheat/AVOID_exbull. **Action: giữ vị thế hiện có (45d) + park cash theo target ở trên.** Đây là hành vi thận trọng bình thường, không phải lỗi.

_Informational (ngoài tier BAL, V2.3 không trade):_ DRI(COMPOUNDER_BUY), GVR(COMPOUNDER_BUY), DCM(COMPOUNDER_BUY), DHC(COMPOUNDER_BUY), DHA(COMPOUNDER_BUY), SCL(COMPOUNDER_BUY), VGC(COMPOUNDER_BUY), VEA(COMPOUNDER_BUY), GMD(COMPOUNDER_BUY), NAB(COMPOUNDER_BUY), BVH(COMPOUNDER_BUY), IDC(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

_(không có entry PEAD đến hạn phiên tới)_

_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên kế tiếp thay vì nằm im): 78 mã — AAV, AFX, AGP, AMC, APF, BMS, BTW, C47, CHS, CKG, CLC, DDN …_

_Đã loại ở tầng tín hiệu (gate quản trị BANNED/forensic): VVS (banned)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **8.4%** vs gate 31%
- Gate chưa kích hoạt — sleeve dormant.

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD DGC [PARK] (data 2026-09-24): thanh khoản OK (ADV3T 21.42 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE,IDIOCRASH] ngày 2026-07-23
  FA: ROE5Y 37.3% · ROE_Min3Y 21.3% · FSCORE 4 · D/E 0.19 · PE 6.20
  🟢 DCF: CHEAP (giá trị hợp lý ~76,501đ vs giá 35,300đ, MoS +53.9%, robust)
- DD EVF [PARK] (data 2026-09-24): thanh khoản OK (ADV3T 16.07 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 8.0% · ROE_Min3Y 5.1% · FSCORE 3 · D/E 7.81 · PE 9.15
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.85 (band cheap <1.8), ROE_TTM 9.6% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD LPB [PARK] (data 2026-09-24): thanh khoản OK (ADV3T 115.67 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE] ngày 2026-06-24
  FA: ROE5Y 21.9% · ROE_Min3Y 19.2% · FSCORE 4 · D/E 13.30 · PE 12.27
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 3.22 vs hợp lý 2.12 (ROE5Y 21.9%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD PNJ [PARK] (data 2026-09-24): thanh khoản OK (ADV3T 171.98 tỷ/phiên) · ⚠ cờ bất thường W [CEIL2] ngày 2026-08-24
  FA: ROE5Y 21.5% · ROE_Min3Y 20.1% · FSCORE 0 · D/E 0.60 · PE 6.98
  🔴 DCF: RICH (giá trị hợp lý ~17,873đ vs giá 33,300đ, MoS -86.3%, robust) ⚠ cần dcf_override_reason
- DD PVT [PARK] (data 2026-09-24): thanh khoản OK (ADV3T 84.22 tỷ/phiên)
  FA: ROE5Y 13.6% · ROE_Min3Y 12.7% · FSCORE 5 · D/E 0.86 · PE 8.08
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 🔴 P/B trough (vận tải biển): P/B 0.93 (trough buy <0.9 — chu kỳ sâu, không có moat) — RICH [framework (logistics_port_screen)]
- DD VCB [PARK] (data 2026-09-24): thanh khoản OK (ADV3T 240.04 tỷ/phiên)
  FA: ROE5Y 20.4% · ROE_Min3Y 16.7% · FSCORE 6 · D/E 9.69 · PE 11.66
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 1.95 vs hợp lý 1.93 (ROE5Y 20.4%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD VGC [PARK] (data 2026-09-24): thanh khoản OK (ADV3T 14.63 tỷ/phiên)
  FA: ROE5Y 16.6% · ROE_Min3Y 13.7% · FSCORE 6 · D/E 1.36 · PE 13.36
  🔴 DCF: RICH (giá trị hợp lý ~21,658đ vs giá 42,400đ, MoS -95.8%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD VIX [PARK] (data 2026-09-24): thanh khoản OK (ADV3T 516.84 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 15.6% · ROE_Min3Y 5.3% · FSCORE 1 · D/E 0.18 · PE 8.30
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.00 (band cheap <1.8), ROE_TTM 19.0% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VND [PARK] (data 2026-09-24): thanh khoản OK (ADV3T 160.49 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 15.3% · ROE_Min3Y 9.5% · FSCORE 6 · D/E 1.33 · PE 8.18
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.03 (band cheap <1.8), ROE_TTM 12.8% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VPB [PARK] (data 2026-09-24): thanh khoản OK (ADV3T 315.60 tỷ/phiên) · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-09-18
  FA: ROE5Y 14.8% · ROE_Min3Y 8.4% · FSCORE 5 · D/E 6.86 · PE 5.88
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 Gordon P/B (ngân hàng): P/B 0.92 vs hợp lý 1.22 (ROE5Y 14.8%, COE 13%/g 5%) — CHEAP [đã validate (bank_compounder_screen)]
- DD VRE [PARK] (data 2026-09-24): thanh khoản OK (ADV3T 119.92 tỷ/phiên) · ⚠ cờ bất thường W [CEIL2] ngày 2026-07-30
  FA: ROE5Y 10.3% · ROE_Min3Y 10.3% · FSCORE 7 · D/E 0.27 · PE 7.57
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 13.2% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- ✅ PARK không cờ (19): ACB, BID, CTG, DCM, DDV, HAH, HDB, HPG, IDC, MBB, MSB, PAN, SHB, TCB, TCM, TPB, VHC, VHM, VIB

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- **Sàn thanh khoản CỨNG cả 2 book hệ thống: ADV3T ≥ 2 tỷ/phiên** (user chốt 2026-08-10 — *hiệu quả vốn*, KHÔNG phải edge: backtest đo phần gia tăng là −0,26pp CAGR / PBO 0,916). Phiên này loại 0 dòng BAL + 67 ứng viên LAG vì dưới sàn.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-09-25.csv` | status: `data/golive_v23_status.json`