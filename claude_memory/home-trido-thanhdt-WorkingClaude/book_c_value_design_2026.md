---
name: book-c-value-design-2026
description: "Book C (VALUE) design — signal, capital, DT5G gating, rebalance day-10 timing finding ([REDACTED]12)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 169175c2-e4bb-43b4-990e-5ab581fd0038
---

> ⛔ **DROPPED [REDACTED]12** — user bỏ kế hoạch 3-book. Lý do: Book C KHÔNG phải grind-hedge tin cậy (grind 2025-26 value+momentum CÙNG rơi −7%; lợi ích chỉ là Sharpe full-cycle, không bõ tradeoff MaxDD −2.7pp/Calmar + phức tạp). pt_book_c.py gỡ khỏi pipeline (giữ tham khảo). PRODUCTION = **V2.3 = V2.2 + capit** (xem [[v4-faithful-reproduction-2026]]). Nghiên cứu dưới đây GIỮ làm tham khảo (signal/timing/rebal đều đúng, chỉ là quyết định không deploy).

## Book C — VALUE (3rd book bên cạnh BAL + LAG trong V2.2 extended)

**Capital (Option A, user chốt)**: 50B tổng = BAL 17.5B + LAG 17.5B + VALUE 15B (thay 30% vốn V2.2, quản lý chung 1 danh mục).

**Signal**: vscore = PB.rank(pct) + PE.rank(pct) trong universe quality-gated; top quintile 20%.
Quality gate V4: ROIC5Y>=8% AND FSCORE>=5 (+PE<100, PB>0, liq Trading_Value_1M_P50>=10B).
Liq-weighted, name cap. SQL: book_c_live_signal.sql; validation: book_c_signal.py + data/book_c_backtest.csv.

**BQ-validated (ticker_prune 2016-2026, profit_1M)**: standalone EW gated 18.4%/Sh0.84/DD-33.9. Anti-phase: 2016/2021/2023 value thắng lớn (2021 +122% vs +61%); corr value-vs-momentum -0.03 (trực giao).

**⚠️ REFINED — vs V2.2 legs THẬT (v22c_compare.py [REDACTED]12, BAL_cap+LAG_cap, KHÔNG phải proxy V5)**: thêm Book C vào V2.2+capit (Band±10pp, 2016-now, apples-to-apples) = TRADE-OFF KHÔNG free-lunch: CAGR 23.6→22.5% (-1.1pp), **Sharpe 1.34→1.56 (+0.23, vol 17→13.6%)**, Sortino +0.22, **NHƯNG MaxDD -18.1→-20.9% (TỆ 2.7pp), Calmar 1.30→1.08 (tệ)**. Lý do: V2.2+capit đã có DD nông nhờ capit cushion; Book C DD-33.9 (value-trap) kéo worst-case sâu hơn tại 2020-COVID (C -11.5pp, value lag V-recovery momentum). Finding CŨ "+0.30Sh/-2.8pp DD tốt hơn" là vs PROXY V5 (DD-19.8 sâu hơn) → ĐẢO DẤU khi so V2.2+capit thật. **KẾT LUẬN: Book C = cải thiện SHARPE/SORTINO (nhất quán, vol giảm mạnh) + đệm GRIND style-divergence (2025-26 +1.4pp, grind window +2.4pp = đúng regime NOW), KHÔNG cải thiện tail/CAGR/Calmar. Quyết định: tối ưu Sharpe→thêm C; tối ưu MaxDD/Calmar→V2.2+capit đã tốt hơn.**

**Vận hành 2 nhịp**: mã rotate THÁNG/lần; exposure theo DT5G đổi NGAY khi state đổi (CRISIS 0% / BEAR 20% / NEUTRAL 70% / BULL 100% / EX-BULL 130% của 15B). CRISIS: Book C về cash đúng lúc capit sleeve fire → bàn giao vốn, không giẫm chân.

## Rebalance timing — CHỐT ANCHOR DAY 10 (book_c_rebal_timing.py, [REDACTED]12)

Test 7 anchor (1/5/10/15/20/25/EOM), 123 tháng 2016-2026, cùng signal:
- **Day 10-15 plateau THẮNG: CAGR 34-35% vs EOM 27.3%, Sharpe 1.05 vs 0.89** (ungated, no-TC, relative). Day 10 MaxDD tốt nhất (-49.1%).
- BCTC thực tế: 59% ra tháng-1-quý nhưng RẢI: tới ngày 20 mới 32%, ngày 25 = 69%, ngày 28 = 83%; **41% ra tháng 2 của quý**.
- Cơ chế (ma trận anchor × month-of-quarter, ĐƠN ĐIỆU cả 2 chiều):
  - Tháng earnings (1/4/7/10): rotate ĐẦU tháng = TỆ NHẤT (day-1 -0.64%) — chọn mã trên data cũ rồi ôm qua mùa BCTC; EOM tốt nhất +5.60%.
  - Tháng 2 quý: rotate SỚM = TỐT NHẤT (+6.2..+6.9% day 1-10, EOM chỉ +1.3%) — value drift hậu-earnings chạy ~6 tuần, rotate muộn là mua sau khi sóng đã chạy.
  - Tháng 3 quý: timing vô nghĩa (+0.2..+1.4%).
- Day-10 = compromise tối ưu của lịch cố định: chịu 1 tháng data cũ ở tháng earnings (+1.18%), đổi lấy full capture drift tháng 2 (+6.20%).
- Caveat: paired t chỉ 0.4-0.5 (noise tháng lớn) nhưng cấu trúc đơn điệu 7 anchor × 3 MoQ = mechanism thật.

**How to apply**: rebalance Book C vào ngày giao dịch đầu tiên >= ngày 10 dương lịch mỗi tháng. Rebalance "ăn tiền" nhất = day-10 tháng 2/5/8/11 (data quý mới đủ). KHÔNG rotate đầu tháng earnings (1/4/7/10).

## Cross-book rebalance — CHỐT BAND ±10pp (book_rebal_policy.py, [REDACTED]12)

Nhịp rebalance THỨ 3 (ngoài rotate-mã-tháng & exposure-DT5G): khi nào reset tỉ lệ vốn 35/35/30 giữa BAL/LAG/VALUE.
Test trên NAV gated thật (pt_v22_bal_v21 + pt_v22_lag_v21 + book_c_backtest), 2016-2026, TC 0.30%:
- **Corr xác nhận thiết kế: BAL/LAG=0.53 (cùng momentum), VALUE vs momentum=−0.03 (trực giao)** → bonus rebalance đến TỪ trục value-vs-momentum.
- **Diversification (có 3 book) đáng giá HƠN NHIỀU chọn policy: blend Sharpe ~1.5 vs single-book tốt nhất LAG 1.22; vol 21%→14%.**
- Policy: Never(drift) Sh1.49/DD−19.9/Cal1.13; **Band±10pp Sh1.55/DD−19.9/Cal1.18 (chỉ 4 lần reset/10y, OOS Sh1.53 cao nhất)** = THẮNG mọi trục; Monthly Sh1.54 nhưng DD−20.8 (TỆ hơn) + 17.6% turnover/yr (đắt nhất, vô ích).
- **Cơ chế: Monthly bơm vốn lại momentum đúng lúc nó drawdown → hại DD + tốn TC. Never để LAG phình tới 49% = rủi ro tập trung. Band±10pp = cưỡi trend nhưng chặn concentration.**

**How to apply**: KHÔNG rebalance theo lịch tháng. Reset 35/35/30 CHỈ khi một book lệch >10pp khỏi target (đo trên BASE notional từ P&L drift, KHÔNG đo trên exposure tạm thời do DT5G). Quarterly là fallback đơn giản (Sh1.54) nếu muốn lịch cố định. Lưu ý: cash do DT5G gate book xuống (vd VALUE→0% CRISIS) GIỮ làm reserve của book đó, KHÔNG reallocate sang BAL/LAG (chỉ capit sleeve nhận). Khác biệt tuyệt đối nhỏ (Sh 1.49-1.55) — đừng over-tune.

## GO-LIVE paper-trade (pt_book_c.py, [REDACTED]12)
Script forward track Book C 15B: day-10 monthly rebalance, V4 gate, vscore top-quintile, liq-weight name-cap 25%, TC 0.30%, DT5G gating ASYMMETRIC (de-risk NGAY khi state rớt — giao cash cho capit; re-risk chỉ ở rebal kế = chậm). Seed [REDACTED]11 (END 06-08 < START → seed như pt_v22_dt5g). Smoke-test START=2025-09: −2.37%/DD−14.7% qua grind (tốt hơn momentum −19.8%), picks khớp (DBC/VGS/VHC/NT2/PVT). Combined V2.2+C: đọc 2 leg momentum từ pt_v22_dt5g_logs (BAL_*/SECOND_*), scale 0.7→17.5B, +Book C, weight 35/35/30 Band±10pp → data/pt_v22c_combined_logs.csv. Env override PT_BOOK_C_START để smoke-test. **Wired papertrade_daily.bat [4d] SAU [4c] pt_v22_dt5g** (phải sau vì đọc legs). Outputs pt_book_c_{logs,transactions,open_positions,report}. KHÔNG đụng pt_v22_dt5g live (OOS baseline).

## GRIND MONITOR (v22_grind_monitor.py, [REDACTED]12) — trả lời "V2.2+capit suy giảm 2025→now?"
Leg NAV THẬT (BAL_cap+LAG_cap sum/drift, đến [REDACTED]09):
- **2025 KHÔNG suy giảm — cả năm +30.8%** (nhưng lag VNI +40.5%, bull VIC-megacap). Đỉnh ATH 980B ngày **2025-08-19**.
- **Từ đỉnh đến nay: −11.8% DD, 294 ngày dưới nước, trong khi VNINDEX +8.4% = STYLE-DIVERGENCE** (book chảy máu khi index giữ/tăng, đúng pattern 8L/momentum lag megacap). 2026 YTD −2.8%. Trailing: 1M −2.2%, 3M +5.3%, 12M +12.1%.
- **⚠️ CORRECTION quan trọng về Book C trong grind**: KHÔNG phải hedge đáng tin. Cửa sổ đỉnh→now (2025-08..2026-03): mom −7.9%, **Book C alone CŨNG −7.2%** (value cũng rơi grind này), blend 35/35/30 = −9.3% (TỆ −1.4pp). Dấu ĐẢO theo cửa sổ: v22c_compare bắt đầu 2025-09 cho +2.4pp (vì bỏ tháng đỉnh Aug +8.1% mom). → **lợi ích Book C là Sharpe/vol FULL-CYCLE, KHÔNG phải cứu grind cụ thể này**; 2025-26 value & momentum CÙNG rơi (không nghịch pha như 2021). Đừng bán Book C như "grind hedge".

**GRIND LENS wired papertrade_compare.py**: stats() thêm cur_dd (DD từ đỉnh chạy), underwater_days, peak_date, ret_1m (~21d), ret_3m (~63d); thêm section "Grind lens" trong report. Theo dõi V22 vs V22C trailing-3M forward để xem value sleeve có đệm grind đang diễn ra không.

**WIRING [REDACTED]12**: (1) thêm V22 + V22C vào papertrade_compare.py SYSTEMS (trước đó CHƯA có cả V2.2) → hiện trong báo cáo so sánh hệ; seed/missing xử lý graceful. (2) pt_book_c.py thêm live_picks_md() — screen ticker_1m TƯƠI (book_c_live_signal.sql logic) + DT5G state hiện tại → data/book_c_live_picks.csv + bảng "Book C nên giữ gì hôm nay" trong report, LUÔN chạy kể cả khi seed. Picks NOW ([REDACTED]10, NEUTRAL 70%): PVP/NT2/VHC/PVT/IJC tổng 10.5B. KHÔNG đụng dna_report.py (per-ticker bot, sai chỗ cho NAV combined).

Liên quan: [[capit-stock-optimizer-2026]] (capit nhận cash từ Book C trong CRISIS).

**SWAP TEST: Book C THAY BAL — REJECTED at faithful grade ([REDACTED]11, user Q "BAL có quan trọng thật không hay overfit, Book C thay được không?")**. Built faithful daily ledger for Book C (`workspace/bookc_faithful_sim.py` → `data/bookc_faithful_nav.csv`): monthly picks from book_c_backtest.csv, T+1 Open, slip 0.1%+TC 0.1%/side+CGT 0.1%, liq cap 20% ADV/5d, delta-only rebalance (continuing names not churned), idle cash 0%. **Research→faithful haircut −5.5pp** (gated ~19.3%→13.84%/Sh0.80). Swap test (band±10pp allocator, w_LAG .65, partner=BAL vs BookC, 2016→2026): **BAL partner 24.29%/−18.3/Sh1.66/Cal1.32 >> BookC partner 21.60%/−21.6/1.47/1.00**. The earlier monthly-grade result (BookC 26.16 > BAL 23.29) was grade-mismatch illusion. **BAL's role confirmed: real alpha (18.06% vs VNINDEX ~11%, half the DD), NOT pure overfit, earns its 35%-good/100%-BEAR seat; not replaceable by Book C.** Caveat: sim slightly harsh on BookC (no ETF parking, worth ~+1-1.5pp) — doesn't close the 4.2pp standalone gap. Silver lining: BookC partner wins 2025+ only (18.40 vs 16.43) = confirms cyclical/energy value catches the current regime → future role = small COMPLEMENT sleeve (must pass faithful), never a BAL replacement.
