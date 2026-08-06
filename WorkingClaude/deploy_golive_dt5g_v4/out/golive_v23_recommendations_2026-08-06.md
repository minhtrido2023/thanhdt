# V2.3 + DT5G — Daily Recommendations — 2026-08-06

*Generated 2026-08-06 19:03. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 49% (as of 2026-08-05) → trong band ±10pp, không rebalance
- **Parking (cả 2 book):** park **80%** cash nhàn rỗi vào **rổ custom30V** (`tav2_bq.custom30v_8l`, yieldcombo, cap-weight namecap≤10%, 30 mã) (NEUTRAL)
    - top: VHM 10% · BID 10% · VCB 10% · CTG 9% · TCB 8% · VPB 7% · MBB 7% · HPG 7% …

## BAL book (50% NAV target) — 0 picks

_No new BAL entries today_ — không có signal đạt chuẩn trong các tier BAL (MEGA/MOMENTUM*/DVR/RE_BACKLOG) sau SV_TIGHT/overheat/AVOID_exbull. **Action: giữ vị thế hiện có (45d) + park cash theo target ở trên.** Đây là hành vi thận trọng bình thường, không phải lỗi.

_Informational (ngoài tier BAL, V2.3 không trade):_ VVS(COMPOUNDER_BUY), KLB(MOMENTUM_S_N), CTR(COMPOUNDER_BUY), FOC(COMPOUNDER_BUY), VTO(COMPOUNDER_BUY), DGW(COMPOUNDER_BUY), PHP(COMPOUNDER_BUY), SCL(MOMENTUM_S_N), DXP(COMPOUNDER_BUY), TLG(COMPOUNDER_BUY), DHC(COMPOUNDER_BUY), GMD(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

**Vào lệnh phiên tới:**
- **PGS** (LAG_HI) — entry T+1 phiên tới (release 2026-07-31, NP_R 56%, pa_HL3 6.9)
- **PHR** (LAG_HI) — entry T+1 phiên tới (release 2026-07-31, NP_R 300%, pa_HL3 5.7)
- **SSI** (LAG_LO) — entry T+1 phiên tới (release 2026-07-31, NP_R 27%, pa_HL3 5.9)
- **TVN** (LAG_HI) — entry T+1 phiên tới (release 2026-07-31, NP_R 66%, pa_HL3 6.3)
- **VNF** (LAG_HI) — entry T+1 phiên tới (release 2026-07-31, NP_R 48%, pa_HL3 6.4)
- **VSI** (LAG_LO) — entry T+1 phiên tới (release 2026-07-31, NP_R 66%, pa_HL3 5.0)

_Cửa sổ entry đã qua trong các phiên gần nhất — đối chiếu vị thế thực, KHÔNG mặc định đã vào lệnh:_ APF(2026-08-04), BSR(2026-08-06), BVB(2026-08-05), DCM(2026-08-05), DGW(2026-08-05), DHD(2026-08-03), DRI(2026-08-06), GVR(2026-08-06), HMH(2026-08-06), MAC(2026-08-04), NVB(2026-08-06), POW(2026-08-06), PRE(2026-08-05), PVT(2026-08-05), SCL(2026-08-06), TV2(2026-08-04), TV3(2026-08-04), VGS(2026-08-06)

_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên kế tiếp thay vì nằm im): 20 mã — ATS, BTW, DNN, DP2, DWS, HDW, HOT, MNB, NAP, PBT, PEN, PXI …_

_Đã loại ở tầng tín hiệu (gate quản trị BANNED/forensic): BFC (forensic), VVS (banned)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **3.6%** vs gate 31%
- Gate chưa kích hoạt — sleeve dormant.

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD APF [LAG] (data 2026-08-05): ⚠ thanh khoản mỏng (ADV3T 1.16 tỷ/phiên < sàn 2 tỷ) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 21.7% · ROE_Min3Y 14.0% · FSCORE 7 · D/E 1.05 · PE 6.82
  🟢 DCF: CHEAP (giá trị hợp lý ~74,126đ vs giá 45,000đ, MoS +39.3%, robust)
- DD BSR [LAG] (data 2026-08-05): thanh khoản OK (ADV3T 208.07 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 15.3% · ROE_Min3Y 1.1% · FSCORE 6 · D/E 0.42 · PE 6.39
  🔴 DCF: RICH (giá trị hợp lý ~13,839đ vs giá 25,150đ, MoS -81.7%, robust) ⚠ cần dcf_override_reason
- DD BVB [LAG] (data 2026-08-05): thanh khoản OK (ADV3T 17.46 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 5.1% · ROE_Min3Y 1.0% · FSCORE 4 · D/E 16.92 · PE 10.28
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 1.01 vs hợp lý 0.02 (ROE5Y 5.1%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD DGC [PARK] (data 2026-08-05): thanh khoản OK (ADV3T 26.72 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE,IDIOCRASH] ngày 2026-07-23
  FA: ROE5Y 37.3% · ROE_Min3Y 21.3% · FSCORE 4 · D/E 0.19 · PE 7.09
  🟢 DCF: CHEAP (giá trị hợp lý ~76,501đ vs giá 40,550đ, MoS +47.0%, robust)
- DD DGW [LAG] (data 2026-08-05): thanh khoản OK (ADV3T 28.12 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 23.6% · ROE_Min3Y 14.2% · FSCORE 6 · D/E 2.34 · PE 10.37
  🔴 DCF: RICH (giá trị hợp lý ~8,688đ vs giá 39,150đ, MoS -350.6%, robust) ⚠ cần dcf_override_reason
- DD DHD [LAG] (data 2026-08-05): 🔴 thanh khoản ~0 (ADV3T 60 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 8.9% · ROE_Min3Y 7.7% · FSCORE 5 · D/E 0.91 · PE 20.38
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 4.9% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD EVF [PARK] (data 2026-08-05): thanh khoản OK (ADV3T 27.80 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 8.0% · ROE_Min3Y 5.1% · FSCORE 3 · D/E 7.81 · PE 9.86
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.92 (band cheap <1.8), ROE_TTM 9.6% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD GVR [LAG] (data 2026-08-05): thanh khoản OK (ADV3T 52.70 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 8.0% · ROE_Min3Y 5.3% · FSCORE 8 · D/E 0.35 · PE 15.79
  🔴 DCF: RICH (giá trị hợp lý ~14,197đ vs giá 28,150đ, MoS -98.3%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD HMH [LAG] (data 2026-08-03): 🔴 thanh khoản ~0 (ADV3T 2 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 6.4% · ROE_Min3Y 2.1% · FSCORE 6 · D/E 0.16 · PE 8.36
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → chưa có lăng kính định giá cho ngành này
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD LPB [PARK] (data 2026-08-05): thanh khoản OK (ADV3T 89.68 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE] ngày 2026-06-24
  FA: ROE5Y 21.9% · ROE_Min3Y 19.2% · FSCORE 4 · D/E 13.30 · PE 14.02
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 3.68 vs hợp lý 2.12 (ROE5Y 21.9%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD MAC [LAG] (data 2026-08-03): 🔴 thanh khoản ~0 (ADV3T 7 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.8% · ROE_Min3Y 14.5% · FSCORE 8 · D/E 0.17 · PE 7.52
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → chưa có lăng kính định giá cho ngành này
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD NVB [LAG] (data 2026-08-05): thanh khoản OK (ADV3T 5.29 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ có quý LỖ trong nền 4 quý (P2) — surprise có thể do nền thấp
  FA: ROE5Y -20.5% · ROE_Min3Y -91.7% · FSCORE 3 · D/E 12.89 · PE 128.24
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 2.37 vs hợp lý -3.18 (ROE5Y -20.5%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD PGS [LAG] (data 2026-08-05): 🔴 thanh khoản ~0 (ADV3T 6 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 10.4% · ROE_Min3Y 10.5% · FSCORE 9 · D/E 1.66 · PE 23.73
  🟢 DCF: CHEAP (giá trị hợp lý ~71,594đ vs giá 64,500đ, MoS +9.9%, không robust)
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD PHR [LAG] (data 2026-08-05): thanh khoản OK (ADV3T 18.77 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 17.9% · ROE_Min3Y 12.3% · FSCORE 5 · D/E 0.43 · PE 8.43
  🔴 DCF: RICH (giá trị hợp lý ~47,948đ vs giá 58,200đ, MoS -21.4%, robust) ⚠ cần dcf_override_reason
- DD PNJ [PARK] (data 2026-08-05): thanh khoản OK (ADV3T 41.66 tỷ/phiên) · ⚠ cờ bất thường W [CEIL2] ngày 2026-08-05
  FA: ROE5Y 21.5% · ROE_Min3Y 20.1% · FSCORE 1 · D/E 0.51 · PE 6.69
  🔴 DCF: RICH (giá trị hợp lý ~17,873đ vs giá 37,900đ, MoS -112.1%, robust) ⚠ cần dcf_override_reason
- DD PRE [LAG] (data 2026-08-05): ⚠ thanh khoản mỏng (ADV3T 124 tr/phiên < sàn 2 tỷ) · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 14.9% · ROE_Min3Y 11.9% · FSCORE 6 · D/E 3.69 · PE 10.58
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: P/B thô (bảo hiểm): P/B 1.65, ROE5Y 14.9% [THÔ — chưa có lens chuyên biệt (combined-ratio/EV không có trong BQ)]
  🔴 DD cờ đỏ: NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD SCL [LAG] (data 2026-08-05): ⚠ thanh khoản mỏng (ADV3T 1.21 tỷ/phiên < sàn 2 tỷ) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 13.8% · ROE_Min3Y 10.1% · FSCORE 8 · D/E 0.93 · PE 10.02
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 10.0% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD SSI [LAG] (data 2026-08-05): thanh khoản OK (ADV3T 371.72 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 13.0% · ROE_Min3Y 10.1% · FSCORE 5 · D/E 1.37 · PE 12.71
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.50 (band cheap <1.8), ROE_TTM 13.5% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD TV3 [LAG] (data 2026-08-05): 🔴 thanh khoản ~0 (ADV3T 2 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 11.3% · ROE_Min3Y 7.7% · FSCORE 5 · D/E 0.85 · PE 8.74
  🔴 DCF: RICH (giá trị hợp lý ~7,709đ vs giá 15,800đ, MoS -105.0%, robust) ⚠ cần dcf_override_reason
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD TVN [LAG] (data 2026-08-05): thanh khoản OK (ADV3T 5.79 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 1.4% · ROE_Min3Y -4.1% · FSCORE 6 · D/E 1.67 · PE 7.84
  🔴 DCF: RICH (giá trị hợp lý ~1,764đ vs giá 9,100đ, MoS -415.8%, robust) ⚠ cần dcf_override_reason
- DD VCB [PARK] (data 2026-08-05): thanh khoản OK (ADV3T 250.19 tỷ/phiên)
  FA: ROE5Y 20.4% · ROE_Min3Y 16.7% · FSCORE 6 · D/E 9.69 · PE 11.90
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 1.99 vs hợp lý 1.93 (ROE5Y 20.4%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD VGS [LAG] (data 2026-08-05): thanh khoản OK (ADV3T 2.70 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.9% · ROE_Min3Y 6.1% · FSCORE 6 · D/E 1.72 · PE 4.53
  🔴 DCF: RICH (giá trị hợp lý ~10,446đ vs giá 18,000đ, MoS -72.3%, robust) ⚠ cần dcf_override_reason
- DD VIX [PARK] (data 2026-08-05): thanh khoản OK (ADV3T 463.59 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 15.6% · ROE_Min3Y 5.3% · FSCORE 1 · D/E 0.18 · PE 8.68
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.05 (band cheap <1.8), ROE_TTM 19.0% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VND [PARK] (data 2026-08-05): thanh khoản OK (ADV3T 252.85 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 15.3% · ROE_Min3Y 9.5% · FSCORE 6 · D/E 1.33 · PE 9.56
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.20 (band cheap <1.8), ROE_TTM 12.8% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VNF [LAG] (data 2026-08-05): 🔴 thanh khoản ~0 (ADV3T 23 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 7.1% · ROE_Min3Y 1.0% · FSCORE 6 · D/E 0.36 · PE 6.20
  🟢 DCF: CHEAP (giá trị hợp lý ~38,656đ vs giá 13,000đ, MoS +66.4%, robust)
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD VRE [PARK] (data 2026-08-05): thanh khoản OK (ADV3T 133.21 tỷ/phiên) · ⚠ cờ bất thường W [CEIL2] ngày 2026-07-30
  FA: ROE5Y 10.3% · ROE_Min3Y 10.3% · FSCORE 7 · D/E 0.27 · PE 8.29
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 12.1% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD VSI [LAG] (data 2026-08-05): 🔴 thanh khoản ~0 (ADV3T 6 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 14.4% · ROE_Min3Y 13.2% · FSCORE 7 · D/E 1.17 · PE 5.08
  🟢 DCF: CHEAP (giá trị hợp lý ~103,146đ vs giá 17,150đ, MoS +83.4%, robust)
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- ✅ LAG không cờ (5): DCM, DRI, POW, PVT, TV2
- ✅ PARK không cờ (22): ACB, BID, CTG, DCM, DDV, HAH, HDB, HHV, HPG, IDC, MBB, MSB, PVT, SHB, TCB, TCM, TNG, TPB, VHC, VHM, VIB, VPB

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-08-06.csv` | status: `data/golive_v23_status.json`