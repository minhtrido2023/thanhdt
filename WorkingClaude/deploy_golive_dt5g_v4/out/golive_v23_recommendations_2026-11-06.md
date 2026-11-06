# V2.3 + DT5G — Daily Recommendations — 2026-11-06

*Generated 2026-11-06 19:05. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 48% (as of 2026-11-05) → trong band ±10pp, không rebalance
- **Parking:** 0% (state 3 → KHÔNG park, giữ cash phòng thủ)

## BAL book (50% NAV target) — 1 picks

| ticker | tier | 8L | ta | close_bq_stale (CẤM dùng làm ref_price — giá BQ trễ ≥1 phiên, ref_price phải lấy DNSE live) | sector | weight (of book) |
|---|---|---:|---:|---:|---:|---:|
| TCH | RE_BACKLOG_BUY | 4 | 146 | 13500.0 | 8 | 10% |

_Informational (ngoài tier BAL, V2.3 không trade):_ VGS(COMPOUNDER_BUY), CTG(COMPOUNDER_BUY), NAB(COMPOUNDER_BUY), TPB(COMPOUNDER_BUY), DHA(COMPOUNDER_BUY), QTP(COMPOUNDER_BUY), REE(COMPOUNDER_BUY), LHG(COMPOUNDER_BUY), NTP(COMPOUNDER_BUY), BWE(COMPOUNDER_BUY), DPG(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

**Vào lệnh phiên tới:**
- **BSR** (LAG_HI) — entry T+1 phiên tới (release 2026-11-02, NP_R 888%, pa_HL3 9.3)
- **CSV** (LAG_LO) — entry T+1 phiên tới (release 2026-11-02, NP_R 48%, pa_HL3 5.5)
- **GAS** (LAG_LO) — entry T+1 phiên tới (release 2026-11-02, NP_R 80%, pa_HL3 5.1)
- **GVR** (LAG_HI) — entry T+1 phiên tới (release 2026-11-02, NP_R 76%, pa_HL3 6.2)
- **HTN** (LAG_HI) — entry T+1 phiên tới (release 2026-11-02, NP_R 1812%, pa_HL3 7.8)
- **MSB** (LAG_LO) — entry T+1 phiên tới (release 2026-11-02, NP_R 29%, pa_HL3 6.1)
- **MZG** (LAG_HI) — entry T+1 phiên tới (release 2026-11-02, NP_R 101%, pa_HL3 6.2)
- **YEG** (LAG_LO) — entry T+1 phiên tới (release 2026-11-02, NP_R 35%, pa_HL3 5.9)

_Cửa sổ entry đã qua trong các phiên gần nhất — đối chiếu vị thế thực, KHÔNG mặc định đã vào lệnh:_ DCM(2026-11-05), PHP(2026-11-05), PVT(2026-11-05), TV2(2026-11-04)

_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên kế tiếp thay vì nằm im): 114 mã — AAV, ADP, AFX, AGP, AMC, APF, API, BKC, BMS, BTW, C32, C47 …_

_Đã loại ở tầng tín hiệu (gate quản trị BANNED/forensic): VVS (banned)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **5.2%** vs gate 31%
- Gate chưa kích hoạt — sleeve dormant.

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD BSR [LAG] (data 2026-11-05): thanh khoản OK (ADV3T 253.13 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 15.3% · ROE_Min3Y 1.1% · FSCORE 7 · D/E 0.44 · PE 4.75
  🔴 DCF: RICH (giá trị hợp lý ~21,359đ vs giá 26,500đ, MoS -24.1%, robust)
- DD CSV [LAG] (data 2026-11-05): thanh khoản OK (ADV3T 6.10 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 18.3% · ROE_Min3Y 13.7% · FSCORE 7 · D/E 0.32 · PE 8.59
  🟢 DCF: CHEAP (giá trị hợp lý ~29,479đ vs giá 22,900đ, MoS +22.3%, robust)
- DD GAS [LAG] (data 2026-11-05): thanh khoản OK (ADV3T 87.98 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [CEIL2] ngày 2026-08-10
  FA: ROE5Y 19.4% · ROE_Min3Y 16.7% · FSCORE 6 · D/E 0.41 · PE 12.21
  🔴 DCF: RICH (giá trị hợp lý ~67,081đ vs giá 74,600đ, MoS -11.2%, không robust)
- DD GVR [LAG] (data 2026-11-05): thanh khoản OK (ADV3T 60.17 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [CEIL2] ngày 2026-08-10
  FA: ROE5Y 8.0% · ROE_Min3Y 5.3% · FSCORE 7 · D/E 0.37 · PE 14.28
  🔴 DCF: RICH (giá trị hợp lý ~13,888đ vs giá 30,150đ, MoS -117.1%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD HTN [LAG] (data 2026-11-05): thanh khoản OK (ADV3T 2.62 tỷ/phiên) · ⚠ có quý LỖ trong nền 4 quý (P3) — surprise có thể do nền thấp
  FA: ROE5Y 5.9% · ROE_Min3Y 1.2% · FSCORE 6 · D/E 2.56 · PE 36.49
  🔴 DCF: RICH (giá trị hợp lý ~6,841đ vs giá 7,300đ, MoS -6.7%, không robust)
- DD MZG [LAG] (data 2026-11-05): thanh khoản OK (ADV3T 7.44 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 6.6% · ROE_Min3Y 5.4% · FSCORE 5 · D/E 2.81 · PE 8.56
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 11.7% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD PHP [LAG] (data 2026-11-05): thanh khoản OK (ADV3T 10.79 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 13.1% · ROE_Min3Y 11.8% · FSCORE 8 · D/E 0.38 · PE 10.39
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 🔴 EV/EBITDA (cảng/hạ tầng): EV/EBITDA 8.6x (cheap <8x, benchmark mature 4-8x) — RICH [framework (n nhỏ — cần margin/ROIC xác nhận kèm)]
- DD PVT [LAG] (data 2026-11-05): thanh khoản OK (ADV3T 120.55 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-10-29
  FA: ROE5Y 13.6% · ROE_Min3Y 12.7% · FSCORE 7 · D/E 0.84 · PE 6.92
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 🟢 P/B trough (vận tải biển): P/B 0.83 (trough buy <0.9 — chu kỳ sâu, không có moat) — CHEAP [framework (logistics_port_screen)]
- DD TCH [BAL] (data 2026-11-05): thanh khoản OK (ADV3T 61.80 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 5.8% · ROE_Min3Y 3.0% · FSCORE 5 · D/E 0.45 · PE 16.38
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 4/5, earnings yield 6.1% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- ✅ LAG không cờ (4): DCM, MSB, TV2, YEG

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- **Sàn thanh khoản CỨNG cả 2 book hệ thống: ADV3T ≥ 2 tỷ/phiên** (user chốt 2026-08-10 — *hiệu quả vốn*, KHÔNG phải edge: backtest đo phần gia tăng là −0,26pp CAGR / PBO 0,916). Phiên này loại 0 dòng BAL + 93 ứng viên LAG vì dưới sàn.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-11-06.csv` | status: `data/golive_v23_status.json`