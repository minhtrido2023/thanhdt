# V2.3 + DT5G — Daily Recommendations — 2026-10-27

*Generated 2026-10-27 19:04. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 48% (as of 2026-10-26) → trong band ±10pp, không rebalance
- **Parking:** 0% (state 3 → KHÔNG park, giữ cash phòng thủ)

## BAL book (50% NAV target) — 0 picks

_No new BAL entries today_ — không có signal đạt chuẩn trong các tier BAL (MEGA/MOMENTUM*/DVR/RE_BACKLOG) sau SV_TIGHT/overheat/AVOID_exbull. **Action: giữ vị thế hiện có (45d) + park cash theo target ở trên.** Đây là hành vi thận trọng bình thường, không phải lỗi.

_Informational (ngoài tier BAL, V2.3 không trade):_ HT1(COMPOUNDER_BUY), NT2(COMPOUNDER_BUY), SCL(MOMENTUM_S_N), VGC(COMPOUNDER_BUY), QTP(COMPOUNDER_BUY), NNC(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

**Vào lệnh phiên tới:**
- **MCH** (LAG_LO) — entry T+2 phiên tới (release 2026-10-22, NP_R 15%, pa_HL3 10.8)
- **MSR** (LAG_HI) — entry T+2 phiên tới (release 2026-10-22, NP_R 41510%, pa_HL3 8.2)

_Cửa sổ entry đã qua trong các phiên gần nhất — đối chiếu vị thế thực, KHÔNG mặc định đã vào lệnh:_ HT1(2026-10-26), SCL(2026-10-26), VPB(2026-10-26)

_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên kế tiếp thay vì nằm im): 93 mã — AAV, ADP, AFX, AGP, AMC, APF, BMS, BTW, C47, CCT, CHS, CKG …_

_Đã loại ở tầng tín hiệu (gate quản trị BANNED/forensic): VVS (banned)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **2.8%** vs gate 31%
- Gate chưa kích hoạt — sleeve dormant.

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD MCH [LAG] (data 2026-10-26): thanh khoản OK (ADV3T 58.42 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y 36.4% · ROE_Min3Y 29.7% · FSCORE 6 · D/E 0.85 · PE 25.20
  🔴 DCF: RICH (giá trị hợp lý ~59,588đ vs giá 139,900đ, MoS -134.8%, robust) ⚠ cần dcf_override_reason
- DD MSR [LAG] (data 2026-10-26): thanh khoản OK (ADV3T 113.40 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · nền YoY dương (surprise không phồng do nền âm)
  FA: ROE5Y -4.7% · ROE_Min3Y -12.8% · FSCORE 6 · D/E 1.64 · PE 15.39
  🔴 DCF: RICH (giá trị hợp lý ~5,011đ vs giá 63,700đ, MoS -1171.2%, robust) ⚠ cần dcf_override_reason
- DD VPB [LAG] (data 2026-10-26): thanh khoản OK (ADV3T 361.93 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-09-18
  FA: ROE5Y 14.8% · ROE_Min3Y 8.4% · FSCORE 4 · D/E 7.05 · PE 7.57
  DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 Gordon P/B (ngân hàng): P/B 1.18 vs hợp lý 1.22 (ROE5Y 14.8%, COE 13%/g 5%) — CHEAP [đã validate (bank_compounder_screen)]
- ✅ LAG không cờ (2): HT1, SCL

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- **Sàn thanh khoản CỨNG cả 2 book hệ thống: ADV3T ≥ 2 tỷ/phiên** (user chốt 2026-08-10 — *hiệu quả vốn*, KHÔNG phải edge: backtest đo phần gia tăng là −0,26pp CAGR / PBO 0,916). Phiên này loại 0 dòng BAL + 75 ứng viên LAG vì dưới sàn.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-10-27.csv` | status: `data/golive_v23_status.json`