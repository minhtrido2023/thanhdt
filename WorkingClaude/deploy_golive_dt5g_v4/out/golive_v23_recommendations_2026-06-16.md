# V2.3 + DT5G — Daily Recommendations — 2026-06-16

*Generated 2026-06-16 15:38. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*

## Regime, allocator & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro)
- **Allocator w_LAG:** target **65%** | current 50% (as of 2026-06-15) → **REBALANCE (band ±10pp breached)**
- **Parking (cả 2 book):** park **70%** cash nhàn rỗi vào **rổ 8L custom30** (`tav2_bq.custom30_8l`, cap-weight namecap≤10%, 30 mã) (NEUTRAL)
    - top: VHM 10% · VCB 10% · BID 8% · CTG 7% · TCB 6% · VPB 6% · MBB 6% · GAS 5% …

## BAL book (35% NAV target) — 0 picks

_No new BAL entries today_ — không có signal đạt chuẩn trong các tier BAL (MEGA/MOMENTUM*/DVR/RE_BACKLOG) sau SV_TIGHT/overheat/AVOID_exbull. **Action: giữ vị thế hiện có (45d) + park cash theo target ở trên.** Đây là hành vi thận trọng bình thường, không phải lỗi.

_Informational (ngoài tier BAL, V2.3 không trade):_ AAA(COMPOUNDER_BUY), PSI(MOMENTUM_S_N), POW(COMPOUNDER_BUY), DRI(COMPOUNDER_BUY), KLB(COMPOUNDER_BUY)

## LAG book (65% NAV target, always-on PEAD)

Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.

_(không có entry PEAD đến hạn phiên tới)_

## CAPIT v2 monitor

- Oversold breadth (D_RSI<0.3, ticker_prune): **4.7%** vs gate 30%
- Gate chưa kích hoạt — sleeve dormant.

## Notes
- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = 35% NAV, LAG book = 65% NAV theo allocator).
- BAL: max 12 pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.
- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).
- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.
- CSV: `out/golive_v23_recommendations_2026-06-16.csv` | status: `data/golive_v23_status.json`