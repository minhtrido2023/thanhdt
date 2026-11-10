# V2.3 + DT5G — Daily Recommendations — 2026-11-10

*Generated 2026-11-10 19:06. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 48% (as of 2026-11-09) → trong band ±10pp, không rebalance
- **Parking:** 0% (state 3 → KHÔNG park, giữ cash phòng thủ)

## BAL book (50% NAV target) — 1 picks

| ticker | tier | 8L | ta | close_bq_stale (CẤM dùng làm ref_price — giá BQ trễ ≥1 phiên, ref_price phải lấy DNSE live) | sector | weight (of book) |
|---|---|---:|---:|---:|---:|---:|
| TCH | RE_BACKLOG_BUY | 4 | 141 | 13600.0 | 8 | 10% |

_Informational (ngoài tier BAL, V2.3 không trade):_ NAB(COMPOUNDER_BUY), DHA(COMPOUNDER_BUY), LHG(COMPOUNDER_BUY), HHV(COMPOUNDER_BUY), GMD(COMPOUNDER_BUY), BWE(COMPOUNDER_BUY), NTP(COMPOUNDER_BUY), DPG(COMPOUNDER_BUY), NT2(COMPOUNDER_BUY), SIP(COMPOUNDER_BUY), SAB(COMPOUNDER_BUY), REE(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

_(không có entry PEAD đến hạn phiên tới)_

_Cửa sổ entry đã qua trong các phiên gần nhất — đối chiếu vị thế thực, KHÔNG mặc định đã vào lệnh:_ BSR(2026-11-09), CSV(2026-11-09), DCM(2026-11-05), GAS(2026-11-09), GVR(2026-11-09), HTN(2026-11-09), MSB(2026-11-09), MZG(2026-11-09), PHP(2026-11-05), PVT(2026-11-05), VGS(2026-11-06), YEG(2026-11-09)

_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên kế tiếp thay vì nằm im): 113 mã — AAV, ADP, AFX, AGP, AMC, APF, API, BMS, BTW, C32, C47, CCT …_

_Đã loại ở tầng tín hiệu (gate quản trị BANNED/forensic): VVS (banned)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **5.6%** vs gate 31%
- Gate chưa kích hoạt — sleeve dormant.

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD BSR [LAG] (data 2026-11-09): thanh khoản OK (ADV3T 247.88 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 15.3% · ROE_Min3Y 1.1% · FSCORE 7 · D/E 0.44 · PE 4.65
  🔴 DCF: RICH (giá trị hợp lý ~21,359đ vs giá 25,950đ, MoS -21.5%, robust)
- DD CSV [LAG] (data 2026-11-09): thanh khoản OK (ADV3T 6.28 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 18.3% · ROE_Min3Y 13.7% · FSCORE 7 · D/E 0.32 · PE 8.48
  🟢 DCF: CHEAP (giá trị hợp lý ~29,479đ vs giá 22,600đ, MoS +23.3%, robust)
- DD GAS [LAG] (data 2026-11-09): thanh khoản OK (ADV3T 85.83 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [CEIL2] ngày 2026-08-10
  FA: ROE5Y 19.4% · ROE_Min3Y 16.7% · FSCORE 6 · D/E 0.41 · PE 11.95
  🔴 DCF: RICH (giá trị hợp lý ~67,081đ vs giá 73,000đ, MoS -8.8%, không robust)
- DD GVR [LAG] (data 2026-11-09): thanh khoản OK (ADV3T 56.10 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [CEIL2] ngày 2026-08-10
  FA: ROE5Y 8.0% · ROE_Min3Y 5.3% · FSCORE 7 · D/E 0.37 · PE 13.83
  🔴 DCF: RICH (giá trị hợp lý ~13,888đ vs giá 29,200đ, MoS -110.3%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD HTN [LAG] (data 2026-11-09): thanh khoản OK (ADV3T 2.49 tỷ/phiên) · ⚠ có quý LỖ trong nền 4 quý (P3) — surprise có thể do nền thấp
  FA: ROE5Y 5.9% · ROE_Min3Y 1.2% · FSCORE 6 · D/E 2.56 · PE 36.09
  🔴 DCF: RICH (giá trị hợp lý ~6,841đ vs giá 7,220đ, MoS -5.5%, không robust)
- DD MZG [LAG] (data 2026-11-09): thanh khoản OK (ADV3T 8.16 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 6.6% · ROE_Min3Y 5.4% · FSCORE 5 · D/E 2.81 · PE 8.77
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 11.4% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD PHP [LAG] (data 2026-11-09): thanh khoản OK (ADV3T 10.73 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 13.1% · ROE_Min3Y 11.8% · FSCORE 8 · D/E 0.38 · PE 10.23
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 🔴 EV/EBITDA (cảng/hạ tầng): EV/EBITDA 8.5x (cheap <8x, benchmark mature 4-8x) — RICH [framework (n nhỏ — cần margin/ROIC xác nhận kèm)]
- DD PVT [LAG] (data 2026-11-09): thanh khoản OK (ADV3T 116.74 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-10-29
  FA: ROE5Y 13.6% · ROE_Min3Y 12.7% · FSCORE 7 · D/E 0.84 · PE 6.92
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 🟢 P/B trough (vận tải biển): P/B 0.83 (trough buy <0.9 — chu kỳ sâu, không có moat) — CHEAP [framework (logistics_port_screen)]
- DD TCH [BAL] (data 2026-11-09): thanh khoản OK (ADV3T 64.19 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 5.8% · ROE_Min3Y 3.0% · FSCORE 5 · D/E 0.45 · PE 16.70
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 4/5, earnings yield 6.0% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- DD VGS [LAG] (data 2026-11-09): thanh khoản OK (ADV3T 2.80 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 12.9% · ROE_Min3Y 6.1% · FSCORE 3 · D/E 1.71 · PE 4.25
  🔴 DCF: RICH (giá trị hợp lý ~10,219đ vs giá 19,100đ, MoS -86.9%, robust)
- ✅ LAG không cờ (3): DCM, MSB, YEG

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- **Sàn thanh khoản CỨNG cả 2 book hệ thống: ADV3T ≥ 2 tỷ/phiên** (user chốt 2026-08-10 — *hiệu quả vốn*, KHÔNG phải edge: backtest đo phần gia tăng là −0,26pp CAGR / PBO 0,916). Phiên này loại 0 dòng BAL + 93 ứng viên LAG vì dưới sàn.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-11-10.csv` | status: `data/golive_v23_status.json`