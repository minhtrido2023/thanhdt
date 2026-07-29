# V2.3 + DT5G — Daily Recommendations — 2026-07-29

*Generated 2026-07-29 19:06. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 49% (as of 2026-07-28) → trong band ±10pp, không rebalance
- **Parking (cả 2 book):** park **70%** cash nhàn rỗi vào **rổ custom30V** (`tav2_bq.custom30v_8l`, yieldcombo, cap-weight namecap≤10%, 30 mã) (NEUTRAL)
    - top: CTG 10% · BID 10% · VHM 10% · VCB 10% · TCB 9% · VPB 8% · MBB 8% · LPB 5% …

## BAL book (50% NAV target) — 0 picks

_No new BAL entries today_ — không có signal đạt chuẩn trong các tier BAL (MEGA/MOMENTUM*/DVR/RE_BACKLOG) sau SV_TIGHT/overheat/AVOID_exbull. **Action: giữ vị thế hiện có (45d) + park cash theo target ở trên.** Đây là hành vi thận trọng bình thường, không phải lỗi.

_Informational (ngoài tier BAL, V2.3 không trade):_ VVS(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

**Vào lệnh phiên tới:**
- **DHD** (LAG_LO) — entry T+3 phiên tới (release 2026-07-27, NP_R 33%, pa_HL3 5.7)
- **MAC** (LAG_HI) — entry T+4 phiên tới (release 2026-07-28, NP_R 116%, pa_HL3 6.2)
- **PCT** (LAG_HI) — entry T+1 phiên tới (release 2026-07-23, NP_R 505%, pa_HL3 7.7)
- **TV3** (LAG_LO) — entry T+4 phiên tới (release 2026-07-28, NP_R 30%, pa_HL3 5.8)
- **VVS** (LAG_HI) — entry T+1 phiên tới (release 2026-07-23, NP_R 342%, pa_HL3 12.7)
- **XPH** (LAG_HI) — entry T+1 phiên tới (release 2026-07-23, NP_R 2837%, pa_HL3 9.7)

_Cửa sổ entry đã qua trong các phiên gần nhất — đối chiếu vị thế thực, KHÔNG mặc định đã vào lệnh:_ AMC(2026-07-29), BMS(2026-07-27), BSI(2026-07-27), CLC(2026-07-27), CSV(2026-07-28), EVF(2026-07-28), FTS(2026-07-27), GEE(2026-07-27), HAR(2026-07-27), HCM(2026-07-27), HT1(2026-07-28), IDV(2026-07-28), KHS(2026-07-27), MDF(2026-07-29), NBC(2026-07-27), SPM(2026-07-27), TIN(2026-07-29), VCI(2026-07-28), VE9(2026-07-29), VND(2026-07-27), VPB(2026-07-27)

_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên kế tiếp thay vì nằm im): 20 mã — ATS, BTW, DNN, DP2, HDW, HOT, L10, MNB, NAP, PBT, PEN, PXI …_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **29.2%** vs gate 31%
- Gate chưa kích hoạt — sleeve dormant.

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD AMC [LAG] (data 2026-07-23): 🔴 thanh khoản ~0 (ADV3T 1 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.8% · ROE_Min3Y 11.9% · FSCORE 8 · D/E 0.96 · PE 5.75
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → chưa có lăng kính định giá cho ngành này
- DD BMS [LAG] (data 2026-07-28): ⚠ thanh khoản mỏng (ADV3T 1.64 tỷ/phiên < sàn 2 tỷ) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 8.2% · ROE_Min3Y 6.9% · FSCORE 2 · D/E 0.31 · PE 17.18
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 P/B band + ROE (chứng khoán): P/B 1.23 (band cheap <1.8), ROE_TTM n/a (cần >8%) — RICH [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD BSI [LAG] (data 2026-07-28): thanh khoản OK (ADV3T 9.01 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 10.3% · ROE_Min3Y 8.5% · FSCORE 2 · D/E 2.42 · PE 13.89
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.27 (band cheap <1.8), ROE_TTM 9.4% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD CLC [LAG] (data 2026-07-28): 🔴 thanh khoản ~0 (ADV3T 28 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 17.6% · ROE_Min3Y 16.3% · FSCORE 8 · D/E 1.04 · PE 6.60
  🔴 DCF: RICH (giá trị hợp lý ~739đ vs giá 50,500đ, MoS -6738.1%, robust) ⚠ cần dcf_override_reason
- DD CSV [LAG] (data 2026-07-28): thanh khoản OK (ADV3T 4.36 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 18.3% · ROE_Min3Y 13.7% · FSCORE 6 · D/E 0.29 · PE 8.60
  🟢 DCF: CHEAP (giá trị hợp lý ~23,623đ vs giá 20,750đ, MoS +12.2%, không robust)
- DD DGC [PARK] (data 2026-07-28): thanh khoản OK (ADV3T 28.64 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE,IDIOCRASH] ngày 2026-07-23
  FA: ROE5Y 37.3% · ROE_Min3Y 21.3% · FSCORE 4 · D/E 0.19 · PE 6.43
  🟢 DCF: CHEAP (giá trị hợp lý ~76,501đ vs giá 36,750đ, MoS +52.0%, robust)
- DD DHD [LAG] (data 2026-07-28): 🔴 thanh khoản ~0 (ADV3T 54 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 8.9% · ROE_Min3Y 7.7% · FSCORE 5 · D/E 0.94 · PE 20.76
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 4.8% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD EVF [LAG] (data 2026-07-28): thanh khoản OK (ADV3T 30.40 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 8.0% · ROE_Min3Y 5.1% · FSCORE 3 · D/E 7.81 · PE 9.27
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.86 (band cheap <1.8), ROE_TTM 9.6% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD EVF [PARK] (data 2026-07-28): thanh khoản OK (ADV3T 30.40 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 8.0% · ROE_Min3Y 5.1% · FSCORE 3 · D/E 7.81 · PE 9.27
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.86 (band cheap <1.8), ROE_TTM 9.6% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD FTS [LAG] (data 2026-07-28): thanh khoản OK (ADV3T 20.06 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 15.7% · ROE_Min3Y 9.3% · FSCORE 4 · D/E 2.28 · PE 18.87
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.79 (band cheap <1.8), ROE_TTM 9.5% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD GEE [LAG] (data 2026-07-28): thanh khoản OK (ADV3T 85.21 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 22.9% · ROE_Min3Y 14.0% · FSCORE 3 · D/E 1.32 · PE 11.42
  🔴 DCF: RICH (giá trị hợp lý ~19,298đ vs giá 63,500đ, MoS -229.1%, robust) ⚠ cần dcf_override_reason
- DD HAR [LAG] (data 2026-07-28): ⚠ thanh khoản mỏng (ADV3T 116 tr/phiên < sàn 2 tỷ) · 🔴 NGOÀI universe_pit (lần cuối 2026-07-13) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 0.7% · ROE_Min3Y 0.9% · FSCORE 5 · D/E 0.00 · PE 21.14
  🔴 DCF: RICH (giá trị hợp lý ~230đ vs giá 2,870đ, MoS -1145.7%, robust) ⚠ cần dcf_override_reason
- DD HCM [LAG] (data 2026-07-28): thanh khoản OK (ADV3T 117.86 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.2% · ROE_Min3Y 8.3% · FSCORE 6 · D/E 1.82 · PE 25.81
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 P/B band + ROE (chứng khoán): P/B 2.33 (band cheap <1.8), ROE_TTM 10.2% (cần >8%) — RICH [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD HT1 [LAG] (data 2026-07-28): ⚠ thanh khoản mỏng (ADV3T 1.78 tỷ/phiên < sàn 2 tỷ) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 4.0% · ROE_Min3Y 0.3% · FSCORE 8 · D/E 0.49 · PE 11.74
  🟢 DCF: CHEAP (giá trị hợp lý ~25,849đ vs giá 11,900đ, MoS +54.0%, robust)
- DD IDV [LAG] (data 2026-07-28): 🔴 thanh khoản ~0 (ADV3T 54 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 22.3% · ROE_Min3Y 14.6% · FSCORE 7 · D/E 1.13 · PE 6.94
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 14.4% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD KHS [LAG] (data 2026-07-28): 🔴 thanh khoản ~0 (ADV3T 38 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 15.3% · ROE_Min3Y -3.7% · FSCORE 6 · D/E 0.41 · PE 4.55
  🟢 DCF: CHEAP (giá trị hợp lý ~65,767đ vs giá 13,400đ, MoS +79.6%, robust)
- DD LPB [PARK] (data 2026-07-28): thanh khoản OK (ADV3T 89.08 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE] ngày 2026-06-24
  FA: ROE5Y 21.9% · ROE_Min3Y 19.2% · FSCORE 4 · D/E 13.30 · PE 14.15
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 3.71 vs hợp lý 2.12 (ROE5Y 21.9%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD MAC [LAG] (data 2026-07-28): 🔴 thanh khoản ~0 (ADV3T 7 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.8% · ROE_Min3Y 14.5% · FSCORE 6 · D/E 0.33 · PE 7.58
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 13.2% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD MBS [PARK] (data 2026-07-28): thanh khoản OK (ADV3T 75.14 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 14.7% · ROE_Min3Y 12.3% · FSCORE 7 · D/E 1.86 · PE 14.45
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 P/B band + ROE (chứng khoán): P/B 1.49 (band cheap <1.8), ROE_TTM n/a (cần >8%) — RICH [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD MDF [LAG] (data 2026-07-28): 🔴 thanh khoản ~0 (ADV3T 2 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 2.0% · ROE_Min3Y -4.9% · FSCORE 7 · D/E 0.63 · PE 18.52
  🟢 DCF: CHEAP (giá trị hợp lý ~16,584đ vs giá 4,400đ, MoS +73.5%, robust)
- DD NBC [LAG] (data 2026-07-28): ⚠ thanh khoản mỏng (ADV3T 305 tr/phiên < sàn 2 tỷ) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 11.1% · ROE_Min3Y 6.7% · FSCORE 8 · D/E 3.50 · PE 5.38
  🟢 DCF: CHEAP (giá trị hợp lý ~172,236đ vs giá 7,800đ, MoS +95.5%, robust)
- DD PC1 [PARK] (data 2026-07-28): thanh khoản OK (ADV3T 84.27 tỷ/phiên) · ⚠ cờ chất lượng BANNED
  FA: ROE5Y 10.0% · ROE_Min3Y 1.7% · FSCORE 4 · D/E 1.74 · PE 7.54
  🟢 DCF: CHEAP (giá trị hợp lý ~37,031đ vs giá 21,400đ, MoS +42.2%, robust)
- DD PCT [LAG] (data 2026-07-24): 🔴 thanh khoản ~0 (ADV3T 1 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 8.0% · ROE_Min3Y 8.1% · FSCORE 6 · D/E 1.94 · PE 8.18
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → chưa có lăng kính định giá cho ngành này
- DD SHS [PARK] (data 2026-07-28): thanh khoản OK (ADV3T 197.28 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-20
  FA: ROE5Y 11.7% · ROE_Min3Y 5.7% · FSCORE 1 · D/E 1.20 · PE 13.42
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.08 (band cheap <1.8), ROE_TTM 8.1% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD SPM [LAG] (data 2026-07-28): 🔴 thanh khoản ~0 (ADV3T 1 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · ⚠ có quý LỖ trong nền 4 quý (P2) — surprise có thể do nền thấp
  FA: ROE5Y 1.4% · ROE_Min3Y -0.2% · FSCORE 7 · D/E 0.15 · PE 19.66
  🟢 DCF: CHEAP (giá trị hợp lý ~43,247đ vs giá 10,200đ, MoS +76.4%, robust)
- DD TIN [LAG] (data 2026-07-28): ⚠ thanh khoản mỏng (ADV3T 1.37 tỷ/phiên < sàn 2 tỷ) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 14.1% · ROE_Min3Y -17.3% · FSCORE 5 · D/E 7.20 · PE 6.33
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 P/B band + ROE (chứng khoán): P/B 3.64 (band cheap <1.8), ROE_TTM 76.4% (cần >8%) — RICH [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD TV3 [LAG] (data 2026-07-28): 🔴 thanh khoản ~0 (ADV3T 2 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 11.3% · ROE_Min3Y 7.7% · FSCORE 5 · D/E 0.85 · PE 8.35
  🔴 DCF: RICH (giá trị hợp lý ~7,709đ vs giá 15,100đ, MoS -95.9%, robust) ⚠ cần dcf_override_reason
- DD VCB [PARK] (data 2026-07-28): thanh khoản OK (ADV3T 245.31 tỷ/phiên)
  FA: ROE5Y 20.4% · ROE_Min3Y 16.7% · FSCORE 4 · D/E 9.90 · PE 12.58
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 1.93 vs hợp lý 1.93 (ROE5Y 20.4%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD VCI [LAG] (data 2026-07-28): thanh khoản OK (ADV3T 131.81 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.9% · ROE_Min3Y 7.1% · FSCORE 2 · D/E 1.32 · PE 15.61
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.32 (band cheap <1.8), ROE_TTM 9.2% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VE9 [LAG] (data 2026-07-28): 🔴 thanh khoản ~0 (ADV3T 2 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · 🔴 surprise PHỒNG CƠ HỌC: nền YoY NP_P4 ≤ 0 (-0.3 tỷ) — %YoY vô nghĩa
  FA: ROE5Y -16.8% · ROE_Min3Y -42.2% · FSCORE 5 · D/E 0.43 · PE 11.80
  🔴 DCF: RICH (giá trị hợp lý ~2,513đ vs giá 2,700đ, MoS -7.4%, không robust)
- DD VGC [PARK] (data 2026-07-28): thanh khoản OK (ADV3T 13.21 tỷ/phiên)
  FA: ROE5Y 16.6% · ROE_Min3Y 13.7% · FSCORE 4 · D/E 1.22 · PE 12.35
  🔴 DCF: RICH (giá trị hợp lý ~15,856đ vs giá 35,750đ, MoS -125.5%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD VIX [PARK] (data 2026-07-28): thanh khoản OK (ADV3T 429.04 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 15.6% · ROE_Min3Y 5.3% · FSCORE 1 · D/E 0.18 · PE 7.63
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.92 (band cheap <1.8), ROE_TTM 19.0% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VND [LAG] (data 2026-07-28): thanh khoản OK (ADV3T 251.59 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 15.3% · ROE_Min3Y 9.5% · FSCORE 6 · D/E 1.33 · PE 9.25
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.16 (band cheap <1.8), ROE_TTM 12.8% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VND [PARK] (data 2026-07-28): thanh khoản OK (ADV3T 251.59 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 15.3% · ROE_Min3Y 9.5% · FSCORE 6 · D/E 1.33 · PE 9.25
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.16 (band cheap <1.8), ROE_TTM 12.8% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VVS [LAG] (data 2026-07-28): thanh khoản OK (ADV3T 11.27 tỷ/phiên) · ⚠ cờ chất lượng BANNED · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 25.9% · ROE_Min3Y 6.4% · FSCORE 5 · D/E 8.35 · PE 6.55
  🟢 DCF: CHEAP (giá trị hợp lý ~173,335đ vs giá 99,000đ, MoS +42.9%, robust)
- DD XPH [LAG] (data 2026-07-28): 🔴 thanh khoản ~0 (ADV3T 16 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · ⚠ có quý LỖ trong nền 4 quý (P1,P2,P3) — surprise có thể do nền thấp
  FA: ROE5Y -4.4% · ROE_Min3Y -11.5% · FSCORE 5 · D/E 0.02 · PE 1.89
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 52.9% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- ✅ LAG không cờ (1): VPB
- ✅ PARK không cờ (20): ACB, BID, CTG, DBC, DCM, HAH, HDB, HHV, IDC, MBB, MSB, PVT, SHB, TCB, TPB, VHC, VHM, VIB, VPB, VRE

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-07-29.csv` | status: `data/golive_v23_status.json`