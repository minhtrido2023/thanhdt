# V2.3 + DT5G — Daily Recommendations — 2026-11-26

*Generated 2026-11-26 19:04. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **50%** | current 49% (as of 2026-11-25) → trong band ±10pp, không rebalance
- **Parking:** 0% (state 3 → KHÔNG park, giữ cash phòng thủ)

## BAL book (50% NAV target) — 0 picks

_No new BAL entries today_ — không có signal đạt chuẩn trong các tier BAL (MEGA/MOMENTUM*/DVR/RE_BACKLOG) sau SV_TIGHT/overheat/AVOID_exbull. **Action: giữ vị thế hiện có (45d) + park cash theo target ở trên.** Đây là hành vi thận trọng bình thường, không phải lỗi.

_Informational (ngoài tier BAL, V2.3 không trade):_ PTB(COMPOUNDER_BUY), POW(COMPOUNDER_BUY)

## LAG book (50% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

_(không có entry PEAD đến hạn phiên tới)_

_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên kế tiếp thay vì nằm im): 86 mã — AAV, ADP, API, BSP, C32, CCT, CKG, CLC, CTP, CTW, DDN, DHD …_

_Đã loại ở tầng tín hiệu (gate quản trị BANNED/forensic): VVS (banned)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, top-250 thanh khoản universe_pit): **34.0%** vs gate 31%
- 🚨 **WASHOUT GATE FIRED** — state routing size = **0.38** (grind=True, dd52w=-15.5%, vn_cooling=False)
- ⚙️ Đòn bẩy margin CAPIT: **TẮT** (enabled=False, cổng dd52<=-20.0% chưa đạt @dd52=-15.5%) — chính sách TẮT (enabled=false) — cần user xác nhận riêng mới bật
- **Vốn triển khai = NAV_book_LAG × capit_size** = (active_nav × w_lag_target 50%) × 0.38 — công thức user chốt 2026-07-20. Hold 60td, stop-exempt, slot-exempt.
- Basket quality-golden (4 mã): GAS, QNS, VGC, VNM
- 💰 **VND MỤC TIÊU/mã — DÙNG THẲNG SỐ NÀY, KHÔNG TỰ NHÂN LẠI** (= status `capit_slot_targets`). Cột `weight_pct`=9.38 của dòng CAPIT trong CSV ĐÃ gồm capit_size — nhân nó lên tổng vốn CAPIT là ra capit_size² (lỗi thật 07-21, SpaceX thiếu 87,1tr):
    · SpaceX — book LAG 470tr × 0.38 = tổng 176tr ⇒ **44.0tr/mã** × 4 mã
    · ZaloPay — book LAG 297tr × 0.38 = tổng 111tr ⇒ **27.9tr/mã** × 4 mã
  Lệnh thật = min(mục tiêu ở trên, trần %ADV bên dưới), rồi mới làm tròn lô.
- Trần %ADV/tên — TỔNG cả fleet (10%·ADV20·2 phiên, VND tuyệt đối; phần dư để CASH, không dồn sang tên khác): GAS 10,579tr, QNS 1,017tr, VGC 2,126tr, VNM 28,125tr
  Thanh khoản một mã là nguồn lực THỊ TRƯỜNG dùng chung — trần TỔNG này được CHIA cho 2 account live (pro-rata-nav), executor mỗi account enforce cứng phần của mình:
    · SpaceX — 61.3% (NAV 939,504,730đ, active_nav @2026-11-25): GAS 6,480tr, QNS 623tr, VGC 1,302tr, VNM 17,227tr
    · ZaloPay — 38.7% (NAV 594,311,834đ, active_nav @2026-11-25): GAS 4,099tr, QNS 394tr, VGC 824tr, VNM 10,898tr

## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)

- DD GAS [CAPIT] (data 2026-11-25): thanh khoản OK (ADV3T 69.15 tỷ/phiên) · ⚠ cờ bất thường W [CEIL2] ngày 2026-08-10
  FA: ROE5Y 19.4% · ROE_Min3Y 16.7% · FSCORE 6 · D/E 0.41 · PE 11.38
  🔴 DCF: RICH (giá trị hợp lý ~67,081đ vs giá 69,500đ, MoS -3.6%, không robust)
- DD VGC [CAPIT] (data 2026-11-25): thanh khoản OK (ADV3T 14.89 tỷ/phiên)
  FA: ROE5Y 16.6% · ROE_Min3Y 13.7% · FSCORE 8 · D/E 1.20 · PE 9.51
  🔴 DCF: RICH (giá trị hợp lý ~22,632đ vs giá 38,050đ, MoS -68.1%, robust) ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng
- ✅ CAPIT không cờ (2): QNS, VNM

_Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 50% NAV, LAG book = 50% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- **Sàn thanh khoản CỨNG cả 2 book hệ thống: ADV3T ≥ 2 tỷ/phiên** (user chốt 2026-08-10 — *hiệu quả vốn*, KHÔNG phải edge: backtest đo phần gia tăng là −0,26pp CAGR / PBO 0,916). Phiên này loại 0 dòng BAL + 72 ứng viên LAG vì dưới sàn.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-11-26.csv` | status: `data/golive_v23_status.json`