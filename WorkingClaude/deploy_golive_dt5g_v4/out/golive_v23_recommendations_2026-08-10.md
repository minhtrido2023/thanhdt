# V2.3 + DT5G — Daily Recommendations — 2026-08-10

*Generated 2026-08-10 19:03. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 50% (as of 2026-08-07) → trong band ±10pp, không rebalance
- **Parking (cả 2 book):** park **80%** cash nhàn rỗi vào **rổ custom30V** (`tav2_bq.custom30v_8l`, yieldcombo, cap-weight namecap≤10%, 30 mã) (NEUTRAL)
    - top: VHM 10% · BID 10% · VCB 10% · CTG 9% · TCB 8% · VPB 7% · MBB 7% · HPG 7% …

## BAL book (50% NAV target) — 0 picks

_No new BAL entries today_ — không có signal đạt chuẩn trong các tier BAL (MEGA/MOMENTUM*/DVR/RE_BACKLOG) sau SV_TIGHT/overheat/AVOID_exbull. **Action: giữ vị thế hiện có (45d) + park cash theo target ở trên.** Đây là hành vi thận trọng bình thường, không phải lỗi.

_Informational (ngoài tier BAL, V2.3 không trade):_ SCL(COMPOUNDER_BUY), HII(MOMENTUM_S_N), DXP(COMPOUNDER_BUY), TTA(COMPOUNDER_BUY), PVP(COMPOUNDER_BUY), HT1(COMPOUNDER_BUY), PHP(COMPOUNDER_BUY), GMD(COMPOUNDER_BUY), VGC(COMPOUNDER_BUY), SAB(COMPOUNDER_BUY), BVH(COMPOUNDER_BUY), VNM(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

_(không có entry PEAD đến hạn phiên tới)_

_Cửa sổ entry đã qua trong các phiên gần nhất — đối chiếu vị thế thực, KHÔNG mặc định đã vào lệnh:_ BSR(2026-08-06), BVB(2026-08-05), DCM(2026-08-05), DGW(2026-08-05), DRI(2026-08-06), GVR(2026-08-06), NVB(2026-08-06), PHR(2026-08-07), POW(2026-08-06), PVT(2026-08-05), SSI(2026-08-07), VGS(2026-08-06)

_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên kế tiếp thay vì nằm im): 119 mã — ABC, AFX, AGP, AMC, APF, ATS, BCA, BCE, BMC, BMS, BTH, BTW …_

_Đã loại ở tầng tín hiệu (gate quản trị BANNED/forensic): BFC (forensic), L40 (forensic), VVS (banned)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **1.6%** vs gate 31%
- Gate chưa kích hoạt — sleeve dormant.

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD BSR [LAG] (data 2026-08-07): thanh khoản OK (ADV3T 213.66 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 15.3% · ROE_Min3Y 1.1% · FSCORE 6 · D/E 0.42 · PE 6.66
  🔴 DCF: RICH (giá trị hợp lý ~13,839đ vs giá 26,200đ, MoS -89.3%, robust) ⚠ cần dcf_override_reason
- DD BVB [LAG] (data 2026-08-07): thanh khoản OK (ADV3T 17.32 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 5.1% · ROE_Min3Y 1.0% · FSCORE 4 · D/E 16.92 · PE 10.19
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 1.00 vs hợp lý 0.02 (ROE5Y 5.1%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD DGC [PARK] (data 2026-08-07): thanh khoản OK (ADV3T 28.78 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE,IDIOCRASH] ngày 2026-07-23
  FA: ROE5Y 37.3% · ROE_Min3Y 21.3% · FSCORE 4 · D/E 0.19 · PE 7.73
  🟢 DCF: CHEAP (giá trị hợp lý ~76,501đ vs giá 44,200đ, MoS +42.2%, robust)
- DD DGW [LAG] (data 2026-08-07): thanh khoản OK (ADV3T 28.30 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 23.6% · ROE_Min3Y 14.2% · FSCORE 6 · D/E 2.34 · PE 10.43
  🔴 DCF: RICH (giá trị hợp lý ~8,688đ vs giá 39,400đ, MoS -353.5%, robust) ⚠ cần dcf_override_reason
- DD EVF [PARK] (data 2026-08-07): thanh khoản OK (ADV3T 26.30 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 8.0% · ROE_Min3Y 5.1% · FSCORE 3 · D/E 7.81 · PE 9.70
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.90 (band cheap <1.8), ROE_TTM 9.6% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD GVR [LAG] (data 2026-08-07): thanh khoản OK (ADV3T 53.14 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 8.0% · ROE_Min3Y 5.3% · FSCORE 8 · D/E 0.35 · PE 16.69
  🔴 DCF: RICH (giá trị hợp lý ~14,197đ vs giá 29,750đ, MoS -109.5%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD HHV [PARK] (data 2026-08-07): thanh khoản OK (ADV3T 25.91 tỷ/phiên) · ⚠ cờ chất lượng RATING_FAIL
  FA: ROE5Y 4.6% · ROE_Min3Y 4.4% · FSCORE 7 · D/E 2.21 · PE 9.18
  🟢 DCF: CHEAP (giá trị hợp lý ~36,254đ vs giá 10,050đ, MoS +72.3%, robust)
- DD LPB [PARK] (data 2026-08-07): thanh khoản OK (ADV3T 90.48 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE] ngày 2026-06-24
  FA: ROE5Y 21.9% · ROE_Min3Y 19.2% · FSCORE 4 · D/E 13.30 · PE 13.99
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 3.67 vs hợp lý 2.12 (ROE5Y 21.9%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD NVB [LAG] (data 2026-08-07): thanh khoản OK (ADV3T 5.34 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ có quý LỖ trong nền 4 quý (P2) — surprise có thể do nền thấp
  FA: ROE5Y -20.5% · ROE_Min3Y -91.7% · FSCORE 3 · D/E 12.89 · PE 123.82
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 2.29 vs hợp lý -3.18 (ROE5Y -20.5%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD PHR [LAG] (data 2026-08-07): thanh khoản OK (ADV3T 18.90 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 17.9% · ROE_Min3Y 12.3% · FSCORE 5 · D/E 0.43 · PE 8.49
  🔴 DCF: RICH (giá trị hợp lý ~47,948đ vs giá 58,600đ, MoS -22.2%, robust) ⚠ cần dcf_override_reason
- DD PNJ [PARK] (data 2026-08-07): thanh khoản OK (ADV3T 41.13 tỷ/phiên) · ⚠ cờ bất thường W [CEIL2] ngày 2026-08-05
  FA: ROE5Y 21.5% · ROE_Min3Y 20.1% · FSCORE 1 · D/E 0.51 · PE 6.36
  🔴 DCF: RICH (giá trị hợp lý ~17,873đ vs giá 36,000đ, MoS -101.4%, robust) ⚠ cần dcf_override_reason
- DD SSI [LAG] (data 2026-08-07): thanh khoản OK (ADV3T 372.48 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 13.0% · ROE_Min3Y 10.1% · FSCORE 5 · D/E 1.37 · PE 12.74
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.50 (band cheap <1.8), ROE_TTM 13.5% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD TNG [PARK] (data 2026-08-07): thanh khoản OK (ADV3T 7.58 tỷ/phiên) · ⚠ cờ chất lượng RATING_FAIL
  FA: ROE5Y 17.3% · ROE_Min3Y 12.9% · FSCORE 3 · D/E 3.03 · PE 5.01
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 4/5, earnings yield 20.0% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD VCB [PARK] (data 2026-08-07): thanh khoản OK (ADV3T 250.18 tỷ/phiên)
  FA: ROE5Y 20.4% · ROE_Min3Y 16.7% · FSCORE 6 · D/E 9.69 · PE 11.98
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 2.01 vs hợp lý 1.93 (ROE5Y 20.4%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD VGS [LAG] (data 2026-08-07): thanh khoản OK (ADV3T 2.57 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.9% · ROE_Min3Y 6.1% · FSCORE 6 · D/E 1.72 · PE 4.48
  🔴 DCF: RICH (giá trị hợp lý ~10,446đ vs giá 17,800đ, MoS -70.4%, robust) ⚠ cần dcf_override_reason
- DD VIX [PARK] (data 2026-08-07): thanh khoản OK (ADV3T 474.39 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 15.6% · ROE_Min3Y 5.3% · FSCORE 1 · D/E 0.18 · PE 8.44
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.02 (band cheap <1.8), ROE_TTM 19.0% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VND [PARK] (data 2026-08-07): thanh khoản OK (ADV3T 248.37 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 15.3% · ROE_Min3Y 9.5% · FSCORE 6 · D/E 1.33 · PE 9.39
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.18 (band cheap <1.8), ROE_TTM 12.8% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VRE [PARK] (data 2026-08-07): thanh khoản OK (ADV3T 125.66 tỷ/phiên) · ⚠ cờ bất thường W [CEIL2] ngày 2026-07-30
  FA: ROE5Y 10.3% · ROE_Min3Y 10.3% · FSCORE 7 · D/E 0.27 · PE 7.82
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 12.8% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- ✅ LAG không cờ (4): DCM, DRI, POW, PVT
- ✅ PARK không cờ (20): ACB, BID, CTG, DCM, DDV, HAH, HDB, HPG, IDC, MBB, MSB, PVT, SHB, TCB, TCM, TPB, VHC, VHM, VIB, VPB

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- **Sàn thanh khoản CỨNG cả 2 book hệ thống: ADV3T ≥ 2 tỷ/phiên** (user chốt 2026-08-10 — *hiệu quả vốn*, KHÔNG phải edge: backtest đo phần gia tăng là −0,26pp CAGR / PBO 0,916). Phiên này loại 0 dòng BAL + 98 ứng viên LAG vì dưới sàn.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-08-10.csv` | status: `data/golive_v23_status.json`