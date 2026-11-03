# V2.3 + DT5G — Daily Recommendations — 2026-11-03

*Generated 2026-11-03 19:06. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 48% (as of 2026-11-02) → trong band ±10pp, không rebalance
- **Parking:** 0% (state 3 → KHÔNG park, giữ cash phòng thủ)

## BAL book (50% NAV target) — 1 picks

| ticker | tier | 8L | ta | close_bq_stale (CẤM dùng làm ref_price — giá BQ trễ ≥1 phiên, ref_price phải lấy DNSE live) | sector | weight (of book) |
|---|---|---:|---:|---:|---:|---:|
| TCH | RE_BACKLOG_BUY | 4 | 121 | 11950.0 | 8 | 10% |

_Informational (ngoài tier BAL, V2.3 không trade):_ VGS(COMPOUNDER_BUY), VEA(COMPOUNDER_BUY), DHA(COMPOUNDER_BUY), NTP(COMPOUNDER_BUY), QTP(COMPOUNDER_BUY), TPB(COMPOUNDER_BUY), NAB(COMPOUNDER_BUY), MSH(COMPOUNDER_BUY), DPG(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

**Vào lệnh phiên tới:**
- **BSR** (LAG_HI) — entry T+4 phiên tới (release 2026-11-02, NP_R 888%, pa_HL3 9.3)
- **CSV** (LAG_LO) — entry T+4 phiên tới (release 2026-11-02, NP_R 48%, pa_HL3 5.5)
- **DCM** (LAG_LO) — entry T+2 phiên tới (release 2026-10-29, NP_R 31%, pa_HL3 6.0)
- **GAS** (LAG_LO) — entry T+4 phiên tới (release 2026-11-02, NP_R 80%, pa_HL3 5.1)
- **GVR** (LAG_HI) — entry T+4 phiên tới (release 2026-11-02, NP_R 76%, pa_HL3 6.2)
- **MSB** (LAG_LO) — entry T+4 phiên tới (release 2026-11-02, NP_R 29%, pa_HL3 6.1)
- **PHP** (LAG_LO) — entry T+2 phiên tới (release 2026-10-29, NP_R 56%, pa_HL3 5.3)
- **PVT** (LAG_LO) — entry T+2 phiên tới (release 2026-10-29, NP_R 42%, pa_HL3 6.9)
- **TV2** (LAG_LO) — entry T+1 phiên tới (release 2026-10-28, NP_R 360%, pa_HL3 5.0)
- **YEG** (LAG_LO) — entry T+4 phiên tới (release 2026-11-02, NP_R 35%, pa_HL3 5.9)

_Cửa sổ entry đã qua trong các phiên gần nhất — đối chiếu vị thế thực, KHÔNG mặc định đã vào lệnh:_ MCH(2026-10-29), MSR(2026-10-29)

_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên kế tiếp thay vì nằm im): 110 mã — AAV, ADP, AFX, AGP, AMC, APF, BKC, BMS, BTW, C32, C47, CCT …_

_Đã loại ở tầng tín hiệu (gate quản trị BANNED/forensic): VVS (banned)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **16.4%** vs gate 31%
- Gate chưa kích hoạt — sleeve dormant.

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD BSR [LAG] (data 2026-11-02): thanh khoản OK (ADV3T 264.42 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 15.3% · ROE_Min3Y 1.1% · FSCORE 5 · D/E 0.42 · PE 4.85
  🔴 DCF: RICH (giá trị hợp lý ~21,359đ vs giá 27,100đ, MoS -26.9%, robust)
- DD CSV [LAG] (data 2026-11-02): thanh khoản OK (ADV3T 5.68 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 18.3% · ROE_Min3Y 13.7% · FSCORE 7 · D/E 0.32 · PE 8.14
  🟢 DCF: CHEAP (giá trị hợp lý ~29,479đ vs giá 21,700đ, MoS +26.4%, robust)
- DD GAS [LAG] (data 2026-11-02): thanh khoản OK (ADV3T 100.18 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [CEIL2] ngày 2026-08-10
  FA: ROE5Y 19.4% · ROE_Min3Y 16.7% · FSCORE 3 · D/E 0.46 · PE 12.60
  🔴 DCF: RICH (giá trị hợp lý ~67,081đ vs giá 77,000đ, MoS -14.8%, không robust)
- DD GVR [LAG] (data 2026-11-02): thanh khoản OK (ADV3T 60.91 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [CEIL2] ngày 2026-08-10
  FA: ROE5Y 8.0% · ROE_Min3Y 5.3% · FSCORE 6 · D/E 0.35 · PE 13.78
  🔴 DCF: RICH (giá trị hợp lý ~13,888đ vs giá 29,100đ, MoS -109.5%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD MCH [LAG] (data 2026-11-02): thanh khoản OK (ADV3T 41.97 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 36.4% · ROE_Min3Y 29.7% · FSCORE 6 · D/E 0.85 · PE 24.05
  🔴 DCF: RICH (giá trị hợp lý ~58,628đ vs giá 133,500đ, MoS -127.7%, robust) ⚠ cần dcf_override_reason
- DD MSR [LAG] (data 2026-11-02): thanh khoản OK (ADV3T 110.77 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y -4.7% · ROE_Min3Y -12.8% · FSCORE 6 · D/E 1.64 · PE 13.97
  🔴 DCF: RICH (giá trị hợp lý ~4,740đ vs giá 57,800đ, MoS -1119.4%, robust) ⚠ cần dcf_override_reason
- DD PHP [LAG] (data 2026-11-02): thanh khoản OK (ADV3T 10.52 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 13.1% · ROE_Min3Y 11.8% · FSCORE 8 · D/E 0.38 · PE 10.13
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 🔴 EV/EBITDA (cảng/hạ tầng): EV/EBITDA 8.4x (cheap <8x, benchmark mature 4-8x) — RICH [framework (n nhỏ — cần margin/ROIC xác nhận kèm)]
- DD PVT [LAG] (data 2026-11-02): thanh khoản OK (ADV3T 125.91 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-10-29
  FA: ROE5Y 13.6% · ROE_Min3Y 12.7% · FSCORE 7 · D/E 0.84 · PE 6.92
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 🟢 P/B trough (vận tải biển): P/B 0.83 (trough buy <0.9 — chu kỳ sâu, không có moat) — CHEAP [framework (logistics_port_screen)]
- DD TCH [BAL] (data 2026-11-02): thanh khoản OK (ADV3T 54.74 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 5.8% · ROE_Min3Y 3.0% · FSCORE 5 · D/E 0.45 · PE 14.93
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 4/5, earnings yield 6.7% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- ✅ LAG không cờ (4): DCM, MSB, TV2, YEG

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- **Sàn thanh khoản CỨNG cả 2 book hệ thống: ADV3T ≥ 2 tỷ/phiên** (user chốt 2026-08-10 — *hiệu quả vốn*, KHÔNG phải edge: backtest đo phần gia tăng là −0,26pp CAGR / PBO 0,916). Phiên này loại 0 dòng BAL + 90 ứng viên LAG vì dưới sàn.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-11-03.csv` | status: `data/golive_v23_status.json`