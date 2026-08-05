# V2.3 + DT5G — Daily Recommendations — 2026-08-05

*Generated 2026-08-05 19:03. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 50% (as of 2026-08-04) → trong band ±10pp, không rebalance
- **Parking (cả 2 book):** park **80%** cash nhàn rỗi vào **rổ custom30V** (`tav2_bq.custom30v_8l`, yieldcombo, cap-weight namecap≤10%, 30 mã) (NEUTRAL)
    - top: VCB 10% · CTG 10% · BID 10% · VHM 10% · TCB 9% · VPB 8% · MBB 8% · LPB 5% …

## BAL book (50% NAV target) — 1 picks

| ticker | tier | 8L | ta | close_bq_stale (CẤM dùng làm ref_price — giá BQ trễ ≥1 phiên, ref_price phải lấy DNSE live) | sector | weight (of book) |
|---|---|---:|---:|---:|---:|---:|
| VIC | RE_BACKLOG_BUY | 4 | 123 | 220000.0 | 8 | 10% |

_Informational (ngoài tier BAL, V2.3 không trade):_ VVS(COMPOUNDER_BUY), KLB(MOMENTUM_S_N), CTR(COMPOUNDER_BUY), FOC(COMPOUNDER_BUY), VTO(COMPOUNDER_BUY), PHP(COMPOUNDER_BUY), DXP(COMPOUNDER_BUY), TLG(COMPOUNDER_BUY), DHC(COMPOUNDER_BUY), GMD(COMPOUNDER_BUY), VNM(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

**Vào lệnh phiên tới:**
- **BSR** (LAG_HI) — entry T+1 phiên tới (release 2026-07-30, NP_R 782%, pa_HL3 5.8)
- **DRI** (LAG_HI) — entry T+1 phiên tới (release 2026-07-30, NP_R 212%, pa_HL3 8.3)
- **GVR** (LAG_LO) — entry T+1 phiên tới (release 2026-07-30, NP_R 58%, pa_HL3 5.6)
- **HMH** (LAG_LO) — entry T+1 phiên tới (release 2026-07-30, NP_R 263%, pa_HL3 7.4)
- **NVB** (LAG_HI) — entry T+1 phiên tới (release 2026-07-30, NP_R 64%, pa_HL3 6.4)
- **PGS** (LAG_HI) — entry T+2 phiên tới (release 2026-07-31, NP_R 56%, pa_HL3 6.9)
- **PHR** (LAG_HI) — entry T+2 phiên tới (release 2026-07-31, NP_R 300%, pa_HL3 5.7)
- **POW** (LAG_HI) — entry T+1 phiên tới (release 2026-07-30, NP_R 484%, pa_HL3 5.1)
- **SCL** (LAG_HI) — entry T+1 phiên tới (release 2026-07-30, NP_R 141%, pa_HL3 7.5)
- **SSI** (LAG_LO) — entry T+2 phiên tới (release 2026-07-31, NP_R 27%, pa_HL3 5.9)
- **TVN** (LAG_HI) — entry T+2 phiên tới (release 2026-07-31, NP_R 66%, pa_HL3 6.3)
- **VGS** (LAG_LO) — entry T+1 phiên tới (release 2026-07-30, NP_R 66%, pa_HL3 13.4)
- **VNF** (LAG_HI) — entry T+2 phiên tới (release 2026-07-31, NP_R 48%, pa_HL3 6.4)
- **VSI** (LAG_LO) — entry T+2 phiên tới (release 2026-07-31, NP_R 66%, pa_HL3 5.0)

_Cửa sổ entry đã qua trong các phiên gần nhất — đối chiếu vị thế thực, KHÔNG mặc định đã vào lệnh:_ APF(2026-08-04), BVB(2026-08-05), DCM(2026-08-05), DGW(2026-08-05), DHD(2026-08-03), MAC(2026-08-04), PRE(2026-08-05), PVT(2026-08-05), TV2(2026-08-04), TV3(2026-08-04)

_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên kế tiếp thay vì nằm im): 20 mã — ATS, BTW, DNN, DP2, DWS, HDW, HOT, MNB, NAP, PBT, PEN, PXI …_

_Đã loại ở tầng tín hiệu (gate quản trị BANNED/forensic): BFC (forensic), VVS (banned)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **4.0%** vs gate 31%
- Gate chưa kích hoạt — sleeve dormant.

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD APF [LAG] (data 2026-08-04): ⚠ thanh khoản mỏng (ADV3T 1.17 tỷ/phiên < sàn 2 tỷ) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 21.7% · ROE_Min3Y 14.0% · FSCORE 7 · D/E 1.05 · PE 6.94
  🟢 DCF: CHEAP (giá trị hợp lý ~74,126đ vs giá 45,800đ, MoS +38.2%, robust)
- DD BSR [LAG] (data 2026-08-04): thanh khoản OK (ADV3T 206.82 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 15.3% · ROE_Min3Y 1.1% · FSCORE 6 · D/E 0.42 · PE 6.36
  🔴 DCF: RICH (giá trị hợp lý ~13,839đ vs giá 25,000đ, MoS -80.7%, robust) ⚠ cần dcf_override_reason
- DD BVB [LAG] (data 2026-08-04): thanh khoản OK (ADV3T 17.53 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 5.1% · ROE_Min3Y 1.0% · FSCORE 4 · D/E 16.92 · PE 10.32
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 1.02 vs hợp lý 0.02 (ROE5Y 5.1%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD DBC [PARK] (data 2026-08-04): thanh khoản OK (ADV3T 24.08 tỷ/phiên) · ⚠ cờ chất lượng RATING_FAIL
  FA: ROE5Y 11.2% · ROE_Min3Y 0.5% · FSCORE 0 · D/E 1.08 · PE 6.20
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 4/5, earnings yield 16.1% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD DGC [PARK] (data 2026-08-04): thanh khoản OK (ADV3T 26.09 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE,IDIOCRASH] ngày 2026-07-23
  FA: ROE5Y 37.3% · ROE_Min3Y 21.3% · FSCORE 4 · D/E 0.19 · PE 6.93
  🟢 DCF: CHEAP (giá trị hợp lý ~76,501đ vs giá 39,600đ, MoS +48.2%, robust)
- DD DGW [LAG] (data 2026-08-04): thanh khoản OK (ADV3T 28.45 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 23.6% · ROE_Min3Y 14.2% · FSCORE 6 · D/E 2.34 · PE 10.49
  🔴 DCF: RICH (giá trị hợp lý ~8,688đ vs giá 39,600đ, MoS -355.8%, robust) ⚠ cần dcf_override_reason
- DD DHD [LAG] (data 2026-08-04): 🔴 thanh khoản ~0 (ADV3T 60 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 8.9% · ROE_Min3Y 7.7% · FSCORE 5 · D/E 0.91 · PE 20.53
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 4.9% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD EVF [PARK] (data 2026-08-04): thanh khoản OK (ADV3T 28.08 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 8.0% · ROE_Min3Y 5.1% · FSCORE 3 · D/E 7.81 · PE 9.82
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 0.91 (band cheap <1.8), ROE_TTM 9.6% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD GVR [LAG] (data 2026-08-04): thanh khoản OK (ADV3T 55.64 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 8.0% · ROE_Min3Y 5.3% · FSCORE 8 · D/E 0.35 · PE 15.99
  🔴 DCF: RICH (giá trị hợp lý ~14,197đ vs giá 28,500đ, MoS -100.8%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD HMH [LAG] (data 2026-08-03): 🔴 thanh khoản ~0 (ADV3T 2 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 6.4% · ROE_Min3Y 2.1% · FSCORE 6 · D/E 0.16 · PE 8.36
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → chưa có lăng kính định giá cho ngành này
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD LPB [PARK] (data 2026-08-04): thanh khoản OK (ADV3T 91.03 tỷ/phiên) · ⚠ cờ bất thường H [VOLSPIKE] ngày 2026-06-24
  FA: ROE5Y 21.9% · ROE_Min3Y 19.2% · FSCORE 4 · D/E 13.30 · PE 14.23
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 3.73 vs hợp lý 2.12 (ROE5Y 21.9%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD MAC [LAG] (data 2026-08-03): 🔴 thanh khoản ~0 (ADV3T 7 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.8% · ROE_Min3Y 14.5% · FSCORE 8 · D/E 0.17 · PE 7.52
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → chưa có lăng kính định giá cho ngành này
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD MBS [PARK] (data 2026-08-04): thanh khoản OK (ADV3T 88.36 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 14.7% · ROE_Min3Y 12.3% · FSCORE 7 · D/E 1.86 · PE 15.10
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 P/B band + ROE (chứng khoán): P/B 1.56 (band cheap <1.8), ROE_TTM n/a (cần >8%) — RICH [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD NVB [LAG] (data 2026-08-04): thanh khoản OK (ADV3T 5.19 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ có quý LỖ trong nền 4 quý (P2) — surprise có thể do nền thấp
  FA: ROE5Y -20.5% · ROE_Min3Y -91.7% · FSCORE 3 · D/E 12.89 · PE 129.34
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 2.39 vs hợp lý -3.18 (ROE5Y -20.5%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD PC1 [PARK] (data 2026-08-04): thanh khoản OK (ADV3T 69.12 tỷ/phiên) · ⚠ cờ chất lượng BANNED
  FA: ROE5Y 10.0% · ROE_Min3Y 1.7% · FSCORE 4 · D/E 1.74 · PE 7.51
  🟢 DCF: CHEAP (giá trị hợp lý ~37,031đ vs giá 21,500đ, MoS +41.9%, robust)
- DD PGS [LAG] (data 2026-08-04): 🔴 thanh khoản ~0 (ADV3T 6 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 10.4% · ROE_Min3Y 10.5% · FSCORE 9 · D/E 1.66 · PE 22.44
  🟢 DCF: CHEAP (giá trị hợp lý ~71,594đ vs giá 61,000đ, MoS +14.8%, robust)
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD PHR [LAG] (data 2026-08-04): thanh khoản OK (ADV3T 19.28 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 17.9% · ROE_Min3Y 12.3% · FSCORE 5 · D/E 0.43 · PE 8.67
  🔴 DCF: RICH (giá trị hợp lý ~47,948đ vs giá 59,800đ, MoS -24.7%, robust) ⚠ cần dcf_override_reason
- DD PRE [LAG] (data 2026-08-04): ⚠ thanh khoản mỏng (ADV3T 125 tr/phiên < sàn 2 tỷ) · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 14.9% · ROE_Min3Y 11.9% · FSCORE 6 · D/E 3.69 · PE 10.51
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: P/B thô (bảo hiểm): P/B 1.64, ROE5Y 14.9% [THÔ — chưa có lens chuyên biệt (combined-ratio/EV không có trong BQ)]
  🔴 DD cờ đỏ: NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD SCL [LAG] (data 2026-08-04): ⚠ thanh khoản mỏng (ADV3T 1.19 tỷ/phiên < sàn 2 tỷ) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 13.8% · ROE_Min3Y 10.1% · FSCORE 8 · D/E 0.93 · PE 9.66
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 10.3% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD SHS [PARK] (data 2026-08-04): thanh khoản OK (ADV3T 197.38 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-20
  FA: ROE5Y 11.7% · ROE_Min3Y 5.7% · FSCORE 1 · D/E 1.20 · PE 14.14
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.13 (band cheap <1.8), ROE_TTM 8.1% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD SSI [LAG] (data 2026-08-04): thanh khoản OK (ADV3T 374.01 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 13.0% · ROE_Min3Y 10.1% · FSCORE 5 · D/E 1.37 · PE 12.79
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.51 (band cheap <1.8), ROE_TTM 13.5% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD TV3 [LAG] (data 2026-07-30): 🔴 thanh khoản ~0 (ADV3T 2 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 11.3% · ROE_Min3Y 7.7% · FSCORE 5 · D/E 0.85 · PE 8.69
  🔴 DCF: RICH (giá trị hợp lý ~7,709đ vs giá 15,700đ, MoS -103.6%, robust) ⚠ cần dcf_override_reason
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD TVN [LAG] (data 2026-08-04): thanh khoản OK (ADV3T 5.79 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 1.4% · ROE_Min3Y -4.1% · FSCORE 6 · D/E 1.67 · PE 7.84
  🔴 DCF: RICH (giá trị hợp lý ~1,764đ vs giá 9,100đ, MoS -415.8%, robust) ⚠ cần dcf_override_reason
- DD VCB [PARK] (data 2026-08-04): thanh khoản OK (ADV3T 260.44 tỷ/phiên)
  FA: ROE5Y 20.4% · ROE_Min3Y 16.7% · FSCORE 6 · D/E 9.69 · PE 12.04
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🔴 Gordon P/B (ngân hàng): P/B 2.02 vs hợp lý 1.93 (ROE5Y 20.4%, COE 13%/g 5%) — RICH [đã validate (bank_compounder_screen)]
- DD VGC [PARK] (data 2026-08-04): thanh khoản OK (ADV3T 13.85 tỷ/phiên)
  FA: ROE5Y 16.6% · ROE_Min3Y 13.7% · FSCORE 5 · D/E 1.36 · PE 12.07
  🔴 DCF: RICH (giá trị hợp lý ~21,658đ vs giá 38,300đ, MoS -76.8%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD VGS [LAG] (data 2026-08-04): thanh khoản OK (ADV3T 2.75 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.9% · ROE_Min3Y 6.1% · FSCORE 6 · D/E 1.72 · PE 4.58
  🔴 DCF: RICH (giá trị hợp lý ~10,446đ vs giá 18,200đ, MoS -74.2%, robust) ⚠ cần dcf_override_reason
- DD VIC [BAL] (data 2026-08-04): thanh khoản OK (ADV3T 744.21 tỷ/phiên) · ⚠ cờ chất lượng RATING_FAIL
  FA: ROE5Y 5.2% · ROE_Min3Y 1.9% · FSCORE 7 · D/E 6.24 · PE 74.90
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 4/5, earnings yield 1.3% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD VIX [PARK] (data 2026-08-04): thanh khoản OK (ADV3T 460.28 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 15.6% · ROE_Min3Y 5.3% · FSCORE 1 · D/E 0.18 · PE 8.62
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.04 (band cheap <1.8), ROE_TTM 19.0% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VND [PARK] (data 2026-08-04): thanh khoản OK (ADV3T 252.85 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 15.3% · ROE_Min3Y 9.5% · FSCORE 6 · D/E 1.33 · PE 9.56
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 P/B band + ROE (chứng khoán): P/B 1.20 (band cheap <1.8), ROE_TTM 12.8% (cần >8%) — CHEAP [framework (screen gate, KHÔNG phải giá trị hợp lý)]
- DD VNF [LAG] (data 2026-08-04): 🔴 thanh khoản ~0 (ADV3T 23 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 7.1% · ROE_Min3Y 1.0% · FSCORE 6 · D/E 0.36 · PE 6.20
  🟢 DCF: CHEAP (giá trị hợp lý ~38,656đ vs giá 13,000đ, MoS +66.4%, robust)
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- DD VRE [PARK] (data 2026-08-04): thanh khoản OK (ADV3T 132.96 tỷ/phiên) · ⚠ cờ bất thường W [CEIL2] ngày 2026-07-30
  FA: ROE5Y 10.3% · ROE_Min3Y 10.3% · FSCORE 7 · D/E 0.27 · PE 8.27
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 12.1% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD VSI [LAG] (data 2026-08-04): 🔴 thanh khoản ~0 (ADV3T 9 tr/phiên) — NGOÀI mô hình backtest · 🔴 NGOÀI universe_pit · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 14.4% · ROE_Min3Y 13.2% · FSCORE 7 · D/E 1.17 · PE 5.30
  🟢 DCF: CHEAP (giá trị hợp lý ~103,146đ vs giá 17,900đ, MoS +82.7%, robust)
  🔴 DD cờ đỏ: THANH_KHOAN_CHET, NGOAI_UNIVERSE ⚠ cần dd_override_reason
- ✅ LAG không cờ (5): DCM, DRI, POW, PVT, TV2
- ✅ PARK không cờ (18): ACB, BID, CTG, DCM, HAH, HDB, HHV, IDC, MBB, MSB, PVT, SHB, TCB, TPB, VHC, VHM, VIB, VPB

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-08-05.csv` | status: `data/golive_v23_status.json`