# V2.3 + DT5G — Daily Recommendations — 2026-11-02

*Generated 2026-11-02 19:06. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 48% (as of 2026-10-30) → trong band ±10pp, không rebalance
- **Parking:** 0% (state 3 → KHÔNG park, giữ cash phòng thủ)

## BAL book (50% NAV target) — 1 picks

| ticker | tier | 8L | ta | close_bq_stale (CẤM dùng làm ref_price — giá BQ trễ ≥1 phiên, ref_price phải lấy DNSE live) | sector | weight (of book) |
|---|---|---:|---:|---:|---:|---:|
| TCH | RE_BACKLOG_BUY | 4 | 121 | 11850.0 | 8 | 10% |

_Informational (ngoài tier BAL, V2.3 không trade):_ VGS(COMPOUNDER_BUY), NAB(COMPOUNDER_BUY), TPB(COMPOUNDER_BUY), NTP(COMPOUNDER_BUY), DPG(COMPOUNDER_BUY), DHA(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

**Vào lệnh phiên tới:**
- **BSR** (LAG_HI) — entry T+5 phiên tới (release 2026-11-02, NP_R 888%, pa_HL3 9.3)
- **CSV** (LAG_LO) — entry T+5 phiên tới (release 2026-11-02, NP_R 48%, pa_HL3 5.5)
- **DCM** (LAG_LO) — entry T+3 phiên tới (release 2026-10-29, NP_R 31%, pa_HL3 6.0)
- **GAS** (LAG_LO) — entry T+5 phiên tới (release 2026-11-02, NP_R 80%, pa_HL3 5.1)
- **GVR** (LAG_HI) — entry T+5 phiên tới (release 2026-11-02, NP_R 76%, pa_HL3 6.2)
- **MSB** (LAG_LO) — entry T+5 phiên tới (release 2026-11-02, NP_R 29%, pa_HL3 6.1)
- **PHP** (LAG_LO) — entry T+3 phiên tới (release 2026-10-29, NP_R 56%, pa_HL3 5.3)
- **PVT** (LAG_LO) — entry T+3 phiên tới (release 2026-10-29, NP_R 42%, pa_HL3 6.9)
- **TV2** (LAG_LO) — entry T+2 phiên tới (release 2026-10-28, NP_R 360%, pa_HL3 5.0)
- **YEG** (LAG_LO) — entry T+5 phiên tới (release 2026-11-02, NP_R 35%, pa_HL3 5.9)

_Cửa sổ entry đã qua trong các phiên gần nhất — đối chiếu vị thế thực, KHÔNG mặc định đã vào lệnh:_ MCH(2026-10-29), MSR(2026-10-29)

_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên kế tiếp thay vì nằm im): 108 mã — AAV, ADP, AFX, AGP, AMC, APF, BKC, BMS, BTW, C32, C47, CCT …_

_Đã loại ở tầng tín hiệu (gate quản trị BANNED/forensic): VVS (banned)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **14.0%** vs gate 31%
- Gate chưa kích hoạt — sleeve dormant.

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD BSR [LAG] (data 2026-10-30): thanh khoản OK (ADV3T 271.59 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 15.3% · ROE_Min3Y 1.1% · FSCORE 6 · D/E 0.42 · PE 6.94
  🔴 DCF: RICH (giá trị hợp lý ~13,522đ vs giá 27,600đ, MoS -104.1%, robust) ⚠ cần dcf_override_reason
- DD CSV [LAG] (data 2026-10-30): thanh khoản OK (ADV3T 5.95 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-07-27
  FA: ROE5Y 18.3% · ROE_Min3Y 13.7% · FSCORE 6 · D/E 0.29 · PE 9.42
  🟢 DCF: CHEAP (giá trị hợp lý ~23,099đ vs giá 22,750đ, MoS +1.5%, không robust)
- DD GAS [LAG] (data 2026-10-30): thanh khoản OK (ADV3T 101.48 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [CEIL2] ngày 2026-08-10
  FA: ROE5Y 19.4% · ROE_Min3Y 16.7% · FSCORE 7 · D/E 0.46 · PE 14.80
  🔴 DCF: RICH (giá trị hợp lý ~57,816đ vs giá 78,000đ, MoS -34.9%, robust)
- DD GVR [LAG] (data 2026-10-30): thanh khoản OK (ADV3T 64.26 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [CEIL2] ngày 2026-08-10
  FA: ROE5Y 8.0% · ROE_Min3Y 5.3% · FSCORE 8 · D/E 0.35 · PE 17.84
  🔴 DCF: RICH (giá trị hợp lý ~13,888đ vs giá 31,250đ, MoS -125.0%, robust) ⚠ cần dcf_override_reason ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- DD MCH [LAG] (data 2026-10-30): thanh khoản OK (ADV3T 42.44 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 36.4% · ROE_Min3Y 29.7% · FSCORE 6 · D/E 0.85 · PE 24.32
  🔴 DCF: RICH (giá trị hợp lý ~58,628đ vs giá 135,000đ, MoS -130.3%, robust) ⚠ cần dcf_override_reason
- DD MSR [LAG] (data 2026-10-30): thanh khoản OK (ADV3T 115.82 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y -4.7% · ROE_Min3Y -12.8% · FSCORE 6 · D/E 1.64 · PE 14.79
  🔴 DCF: RICH (giá trị hợp lý ~4,740đ vs giá 61,200đ, MoS -1191.1%, robust) ⚠ cần dcf_override_reason
- DD PHP [LAG] (data 2026-10-30): thanh khoản OK (ADV3T 10.59 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 13.1% · ROE_Min3Y 11.8% · FSCORE 8 · D/E 0.38 · PE 10.20
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 🔴 EV/EBITDA (cảng/hạ tầng): EV/EBITDA 8.5x (cheap <8x, benchmark mature 4-8x) — RICH [framework (n nhỏ — cần margin/ROIC xác nhận kèm)]
- DD PVT [LAG] (data 2026-10-30): thanh khoản OK (ADV3T 124.36 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường W [IDIOCRASH] ngày 2026-10-29
  FA: ROE5Y 13.6% · ROE_Min3Y 12.7% · FSCORE 7 · D/E 0.84 · PE 7.14
  DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 🟢 P/B trough (vận tải biển): P/B 0.85 (trough buy <0.9 — chu kỳ sâu, không có moat) — CHEAP [framework (logistics_port_screen)]
- DD TCH [BAL] (data 2026-10-30): thanh khoản OK (ADV3T 54.74 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL
  FA: ROE5Y 5.8% · ROE_Min3Y 3.0% · FSCORE 3 · D/E 0.53 · PE 39.82
  DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 3/5, earnings yield 2.5% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
- ✅ LAG không cờ (4): DCM, MSB, TV2, YEG

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- **Sàn thanh khoản CỨNG cả 2 book hệ thống: ADV3T ≥ 2 tỷ/phiên** (user chốt 2026-08-10 — *hiệu quả vốn*, KHÔNG phải edge: backtest đo phần gia tăng là −0,26pp CAGR / PBO 0,916). Phiên này loại 0 dòng BAL + 88 ứng viên LAG vì dưới sàn.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-11-02.csv` | status: `data/golive_v23_status.json`