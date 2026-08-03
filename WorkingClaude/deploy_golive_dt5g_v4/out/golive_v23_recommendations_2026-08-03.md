# V2.3 + DT5G — Daily Recommendations — 2026-08-03

*Generated 2026-08-03 19:03. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 50% (as of 2026-07-31) → trong band ±10pp, không rebalance
- **Parking (cả 2 book):** park **70%** cash nhàn rỗi vào **rổ custom30V** (`tav2_bq.custom30v_8l`, yieldcombo, cap-weight namecap≤10%, 30 mã) (NEUTRAL)
    - top: VCB 10% · CTG 10% · BID 10% · VHM 10% · TCB 9% · VPB 8% · MBB 8% · LPB 5% …

## BAL book (50% NAV target) — 0 picks

_No new BAL entries today_ — không có signal đạt chuẩn trong các tier BAL (MEGA/MOMENTUM*/DVR/RE_BACKLOG) sau SV_TIGHT/overheat/AVOID_exbull. **Action: giữ vị thế hiện có (45d) + park cash theo target ở trên.** Đây là hành vi thận trọng bình thường, không phải lỗi.

_Informational (ngoài tier BAL, V2.3 không trade):_ CTR(COMPOUNDER_BUY), VTO(COMPOUNDER_BUY), DXP(COMPOUNDER_BUY), PHP(COMPOUNDER_BUY), GMD(COMPOUNDER_BUY), SAB(COMPOUNDER_BUY), VNM(COMPOUNDER_BUY), TLG(COMPOUNDER_BUY), POW(COMPOUNDER_BUY), FPT(COMPOUNDER_BUY), DHC(COMPOUNDER_BUY), VVS(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

**Vào lệnh phiên tới:**
- **APF** (LAG_HI) — entry T+1 phiên tới (release 2026-07-28, NP_R 197%, pa_HL3 8.1)
- **BSR** (LAG_HI) — entry T+3 phiên tới (release 2026-07-30, NP_R 782%, pa_HL3 5.8)
- **BVB** (LAG_HI) — entry T+2 phiên tới (release 2026-07-29, NP_R 2462%, pa_HL3 5.2)
- **DCM** (LAG_HI) — entry T+2 phiên tới (release 2026-07-29, NP_R 36%, pa_HL3 6.1)
- **DGW** (LAG_HI) — entry T+2 phiên tới (release 2026-07-29, NP_R 167%, pa_HL3 7.7)
- **DRI** (LAG_HI) — entry T+3 phiên tới (release 2026-07-30, NP_R 212%, pa_HL3 8.3)
- **GVR** (LAG_LO) — entry T+3 phiên tới (release 2026-07-30, NP_R 58%, pa_HL3 5.6)
- **HMH** (LAG_LO) — entry T+3 phiên tới (release 2026-07-30, NP_R 263%, pa_HL3 7.4)
- **MAC** (LAG_HI) — entry T+1 phiên tới (release 2026-07-28, NP_R 116%, pa_HL3 6.2)
- **NVB** (LAG_HI) — entry T+3 phiên tới (release 2026-07-30, NP_R 64%, pa_HL3 6.4)
- **PGS** (LAG_HI) — entry T+4 phiên tới (release 2026-07-31, NP_R 56%, pa_HL3 6.9)
- **POW** (LAG_HI) — entry T+3 phiên tới (release 2026-07-30, NP_R 484%, pa_HL3 5.1)
- **PRE** (LAG_LO) — entry T+2 phiên tới (release 2026-07-29, NP_R 24%, pa_HL3 5.9)
- **PVT** (LAG_HI) — entry T+2 phiên tới (release 2026-07-29, NP_R 88%, pa_HL3 5.0)
- **SCL** (LAG_HI) — entry T+3 phiên tới (release 2026-07-30, NP_R 141%, pa_HL3 7.5)
- **TV2** (LAG_LO) — entry T+1 phiên tới (release 2026-07-28, NP_R 168%, pa_HL3 5.9)
- **TV3** (LAG_LO) — entry T+1 phiên tới (release 2026-07-28, NP_R 30%, pa_HL3 5.8)
- **VGS** (LAG_LO) — entry T+3 phiên tới (release 2026-07-30, NP_R 66%, pa_HL3 13.4)

_Cửa sổ entry đã qua trong các phiên gần nhất — đối chiếu vị thế thực, KHÔNG mặc định đã vào lệnh:_ AMC(2026-07-29), DHD(2026-08-03), MDF(2026-07-29), PCT(2026-07-30), TIN(2026-07-29), VE9(2026-07-29), XPH(2026-07-30)

_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên kế tiếp thay vì nằm im): 20 mã — ATS, BTW, DNN, DP2, DWS, HDW, HOT, L10, NAP, PBT, PEN, PXI …_

_Đã loại ở tầng tín hiệu (gate quản trị BANNED/forensic): BFC (forensic), VVS (banned)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **5.2%** vs gate 31%
- Gate chưa kích hoạt — sleeve dormant.

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD AMC [LAG] (data 2026-07-31): 🔴 thanh khoản ~0 (ADV3T 1 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.8% · ROE_Min3Y 11.9% · FSCORE 8 · D/E 1.18 · PE 5.75
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → chưa có lăng kính định giá cho ngành này
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD APF [LAG] (data 2026-07-31): ⚠ thanh khoản mỏng (ADV3T 1.16 tỷ/phiên < sàn 2 tỷ) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 21.7% · ROE_Min3Y 14.0% · FSCORE 7 · D/E 1.96 · PE 7.01
  🟢 DCF: CHEAP (giá trị hợp lý ~74,126đ vs giá 46,300đ, MoS +37.5%, robust)
- DD BSR [LAG] (data 2026-07-31): thanh khoản OK (ADV3T 216.20 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 15.3% · ROE_Min3Y 1.1% · FSCORE 5 · D/E 0.55 · PE 6.45
  🔴 DCF: RICH (giá trị hợp lý ~13,839đ vs giá 25,350đ, MoS -83.2%, robust) ⚠ cần dcf_override_reason
- DD BVB [LAG] (data 2026-07-31): thanh khoản OK (ADV3T 17.66 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 5.1% · ROE_Min3Y 1.0% · FSCORE 4 · D/E 16.92 · PE 10.11
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 1.00 vs hợp lý 0.02 (ROE5Y 5.1%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD DBC [PARK] (data 2026-07-31): thanh khoản OK (ADV3T 23.14 tỷ/phiên) · ⚠ cờ chất lượng RATING_FAIL
  FA: ROE5Y 11.2% · ROE_Min3Y 0.5% · FSCORE 0 · D/E 1.08 · PE 6.08
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 4/5, earnings yield 16.3% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD DGC [PARK] (data 2026-07-31): thanh khoản OK (ADV3T 27.46 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE,IDIOCRASH] ngày 2026-07-23
  FA: ROE5Y 37.3% · ROE_Min3Y 21.3% · FSCORE 4 · D/E 0.19 · PE 6.84
  🟢 DCF: CHEAP (giá trị hợp lý ~76,501đ vs giá 39,100đ, MoS +48.9%, robust)
- DD DGW [LAG] (data 2026-07-31): thanh khoản OK (ADV3T 26.29 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 23.6% · ROE_Min3Y 14.2% · FSCORE 6 · D/E 1.73 · PE 9.69
  🔴 DCF: RICH (giá trị hợp lý ~8,688đ vs giá 36,600đ, MoS -321.3%, robust) ⚠ cần dcf_override_reason
- DD DHD [LAG] (data 2026-07-31): 🔴 thanh khoản ~0 (ADV3T 59 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 8.9% · ROE_Min3Y 7.7% · FSCORE 5 · D/E 0.94 · PE 20.53
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 4.7% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD EVF [PARK] (data 2026-07-31): thanh khoản OK (ADV3T 27.96 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 8.0% · ROE_Min3Y 5.1% · FSCORE 3 · D/E 7.81 · PE 9.58
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.91 (band cheap <1.8), ROE_TTM 9.6% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD GVR [LAG] (data 2026-07-31): thanh khoản OK (ADV3T 54.29 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 8.0% · ROE_Min3Y 5.3% · FSCORE 8 · D/E 0.35 · PE 15.43
  🔴 DCF: RICH (giá trị hợp lý ~14,197đ vs giá 27,500đ, MoS -93.7%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD HMH [LAG] (data 2026-07-31): 🔴 thanh khoản ~0 (ADV3T 2 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 6.4% · ROE_Min3Y 2.1% · FSCORE 6 · D/E 0.13 · PE 8.36
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 4/5, earnings yield 10.5% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD LPB [PARK] (data 2026-07-31): thanh khoản OK (ADV3T 87.65 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE] ngày 2026-06-24
  FA: ROE5Y 21.9% · ROE_Min3Y 19.2% · FSCORE 4 · D/E 13.30 · PE 13.70
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 3.65 vs hợp lý 2.12 (ROE5Y 21.9%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD MAC [LAG] (data 2026-07-30): 🔴 thanh khoản ~0 (ADV3T 7 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.8% · ROE_Min3Y 14.5% · FSCORE 6 · D/E 0.33 · PE 7.58
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 13.2% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD MBS [PARK] (data 2026-07-31): thanh khoản OK (ADV3T 77.77 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 14.7% · ROE_Min3Y 12.3% · FSCORE 7 · D/E 1.86 · PE 14.61
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 P/B band + ROE (chứng khoán): P/B 1.54 (band cheap <1.8), ROE_TTM n/a (cần >8%) — RICH [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD MDF [LAG] (data 2026-07-30): 🔴 thanh khoản ~0 (ADV3T 3 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 2.0% · ROE_Min3Y -4.9% · FSCORE 7 · D/E 0.63 · PE 23.15
  🟢 DCF: CHEAP (giá trị hợp lý ~16,584đ vs giá 5,500đ, MoS +66.8%, robust)
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD NVB [LAG] (data 2026-07-31): thanh khoản OK (ADV3T 4.53 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ có quý LỖ trong nền 4 quý (P2) — surprise có thể do nền thấp
  FA: ROE5Y -20.5% · ROE_Min3Y -91.7% · FSCORE 3 · D/E 12.89 · PE 126.03
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 2.46 vs hợp lý -3.18 (ROE5Y -20.5%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD PC1 [PARK] (data 2026-07-31): thanh khoản OK (ADV3T 73.70 tỷ/phiên) · ⚠ cờ chất lượng BANNED
  FA: ROE5Y 10.0% · ROE_Min3Y 1.7% · FSCORE 4 · D/E 1.74 · PE 7.54
  🟢 DCF: CHEAP (giá trị hợp lý ~37,031đ vs giá 21,400đ, MoS +42.2%, robust)
- DD PCT [LAG] (data 2026-07-30): 🔴 thanh khoản ~0 (ADV3T 1 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 8.0% · ROE_Min3Y 8.1% · FSCORE 6 · D/E 1.94 · PE 8.02
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 12.5% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD PGS [LAG] (data 2026-07-31): 🔴 thanh khoản ~0 (ADV3T 4 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 10.4% · ROE_Min3Y 10.5% · FSCORE 9 · D/E 1.66 · PE 20.86
  🟢 DCF: CHEAP (giá trị hợp lý ~71,594đ vs giá 56,700đ, MoS +20.8%, robust)
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD PRE [LAG] (data 2026-07-31): ⚠ thanh khoản mỏng (ADV3T 128 tr/phiên < sàn 2 tỷ) · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 14.9% · ROE_Min3Y 11.9% · FSCORE 6 · D/E 3.56 · PE 10.36
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: P/B thô (bảo hiểm): P/B 1.62, ROE5Y 14.9% [THÔ — chưa có lens chuyên biệt (combined-ratio/EV không có trong BQ)]
  🔴 DD cờ đỏ: NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD SCL [LAG] (data 2026-07-31): ⚠ thanh khoản mỏng (ADV3T 1.01 tỷ/phiên < sàn 2 tỷ) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 13.8% · ROE_Min3Y 10.1% · FSCORE 8 · D/E 0.86 · PE 9.42
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 8.5% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD SHS [PARK] (data 2026-07-31): thanh khoản OK (ADV3T 195.76 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-20
  FA: ROE5Y 11.7% · ROE_Min3Y 5.7% · FSCORE 1 · D/E 1.20 · PE 13.60
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.12 (band cheap <1.8), ROE_TTM 8.1% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD TIN [LAG] (data 2026-07-31): ⚠ thanh khoản mỏng (ADV3T 1.14 tỷ/phiên < sàn 2 tỷ) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 14.1% · ROE_Min3Y -17.3% · FSCORE 5 · D/E 7.20 · PE 6.28
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 P/B band + ROE (chứng khoán): P/B 3.52 (band cheap <1.8), ROE_TTM 76.4% (cần >8%) — RICH [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD TV3 [LAG] (data 2026-07-30): 🔴 thanh khoản ~0 (ADV3T 2 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 11.3% · ROE_Min3Y 7.7% · FSCORE 5 · D/E 0.85 · PE 8.69
  🔴 DCF: RICH (giá trị hợp lý ~7,709đ vs giá 15,700đ, MoS -103.6%, robust) ⚠ cần dcf_override_reason
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD VCB [PARK] (data 2026-07-31): thanh khoản OK (ADV3T 257.40 tỷ/phiên)
  FA: ROE5Y 20.4% · ROE_Min3Y 16.7% · FSCORE 6 · D/E 9.90 · PE 11.90
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 2.02 vs hợp lý 1.93 (ROE5Y 20.4%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD VE9 [LAG] (data 2026-07-31): 🔴 thanh khoản ~0 (ADV3T 2 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · 🔴 surprise PHỒNG CƠ HỌC: nền YoY NP_P4 ≤ 0 (-0.3 tỷ) — %YoY vô nghĩa
  FA: ROE5Y -16.8% · ROE_Min3Y -42.2% · FSCORE 5 · D/E 0.43 · PE 11.36
  🔴 DCF: RICH (giá trị hợp lý ~2,513đ vs giá 2,600đ, MoS -3.5%, không robust)
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE, SURPRISE_PHONG_CO_HOC ⚠ cần dd_override_reason
- DD VGC [PARK] (data 2026-07-31): thanh khoản OK (ADV3T 13.69 tỷ/phiên)
  FA: ROE5Y 16.6% · ROE_Min3Y 13.7% · FSCORE 5 · D/E 1.22 · PE 11.93
  🔴 DCF: RICH (giá trị hợp lý ~21,658đ vs giá 37,850đ, MoS -74.8%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD VGS [LAG] (data 2026-07-31): thanh khoản OK (ADV3T 2.72 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.9% · ROE_Min3Y 6.1% · FSCORE 6 · D/E 1.34 · PE 4.46
  🔴 DCF: RICH (giá trị hợp lý ~10,446đ vs giá 17,700đ, MoS -69.4%, robust) ⚠ cần dcf_override_reason
- DD VIX [PARK] (data 2026-07-31): thanh khoản OK (ADV3T 430.48 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 15.6% · ROE_Min3Y 5.3% · FSCORE 1 · D/E 0.18 · PE 8.06
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.98 (band cheap <1.8), ROE_TTM 19.0% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VND [PARK] (data 2026-07-31): thanh khoản OK (ADV3T 247.63 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 15.3% · ROE_Min3Y 9.5% · FSCORE 6 · D/E 1.33 · PE 9.36
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.21 (band cheap <1.8), ROE_TTM 12.8% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VRE [PARK] (data 2026-07-31): thanh khoản OK (ADV3T 124.90 tỷ/phiên) · ⚠ cờ bất thường W [CEIL2] ngày 2026-07-30
  FA: ROE5Y 10.3% · ROE_Min3Y 10.3% · FSCORE 7 · D/E 0.27 · PE 7.77
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 13.1% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD XPH [LAG] (data 2026-07-31): 🔴 thanh khoản ~0 (ADV3T 15 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · ⚠ có quý LỖ trong nền 4 quý (P1,P2,P3) — surprise có thể do nền thấp
  FA: ROE5Y -4.4% · ROE_Min3Y -11.5% · FSCORE 5 · D/E 0.02 · PE 1.77
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 56.5% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- ✅ LAG không cờ (5): DCM, DRI, POW, PVT, TV2
- ✅ PARK không cờ (18): ACB, BID, CTG, DCM, HAH, HDB, HHV, IDC, MBB, MSB, PVT, SHB, TCB, TPB, VHC, VHM, VIB, VPB

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-08-03.csv` | status: `data/golive_v23_status.json`