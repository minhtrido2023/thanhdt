# Đặc trưng kỹ thuật cho candidate BAL + LAG: (Q1) timing điểm mua, (Q2) nhóm rủi ro đuôi

**Job** `Taylor_20261022_070208` · 2026-10-22 · Taylor · READ-ONLY (không sửa production, không pin registry, không ghi tên canonical)
PREREG: `PREREG.md` md5 `ba8a81f125b0ceb46cffeb537ebc923f` (khoá trước khi tính bất kỳ đặc trưng nào; md5 kiểm lại cuối job: khớp).
Script → stdout: `nav_overlay.py` → `nav_overlay_stdout.txt` (ledger BAL+LAG, NAV) · `lag_events.py` → `lag_events_stdout.txt` (5.361 sự kiện LAG).
CSV: `positions_features.csv`, `q1_event_ledger.csv`, `q2_event_ledger.csv`, `nav_overlay.csv`, `lag_events_features.csv`, `q1_lag_events.csv`, `q2_lag_events.csv`.

## 0. Kết luận

**Q1 (timing điểm mua): NO-GO.** Không luật nào trong 3 luật làm tốt hơn việc mua Open phiên chuẩn như hiện hành, ở cả hai book.
- **Lệnh giới hạn −2% (R1)** cho giá vào tốt hơn khoảng 150–220 bps trên các lệnh khớp. Nhưng **48–53% lệnh không khớp**, và nó bỏ lỡ mã thắng nhiều hơn mức trung bình: không khớp 53% ở tercile thắng, so với 48% chung (LAG-event).
  - Ròng mỗi giao dịch: **−1,8pp** trên LAG-event, CI [−2,8; −0,9]; **−4,5pp** trên BAL.
  - Cấp NAV tổng: CAGR **−2,2 đến −2,7pp** ở cả pin0% lẫn pin1M.
- **Bỏ lệnh khi gap > 3% (R2)** và **chờ nhịp hồi (R3)**: Δ ≈ 0 hoặc hơi âm. Không có CI nào loại trừ 0 về phía dương.

**Q2 (nhóm rủi ro đuôi): có một nhóm rủi ro thật — biến động 60 phiên cao (G_VOL, top 20% IS). Nhưng giảm 50% tỷ trọng KHÔNG cải thiện NAV/Calmar ổn định ⇒ nhãn theo PREREG = CẢNH BÁO-ONLY, không đổi size.**
- LAG-event (5.361 sự kiện / 51 mùa):
  - P(MAE ≤ −15% trong kỳ giữ): **30,5% so với 12,8%**, Δ +17,7pp, CI [+14,3; +21,6].
  - P5 lợi suất: −23,0% so với −14,3%, ΔP5 −8,7pp, CI [−11,0; −6,0].
  - Ổn định IS/OOS, bỏ-một-năm không năm nào đổi dấu, qua Holm.
  - **Lợi suất TB KHÔNG thấp hơn**: 5,09% so với 4,38%, Δ +0,7pp, CI [−1,4; +3,0]. Tức là rủi ro đuôi cao hơn nhưng được bù bằng lợi suất.
- BAL-ledger: HIT15 43,8% so với 24,7% ở pin0%, CI [+5,0; +32,8]. Nhưng ở ledger pin1M CI chứa 0 ([−3,5; +26,7]) ⇒ **chưa vững** (N=300 vị thế / 40 quý).
- Giảm 50% size nhóm G_VOL ở cấp NAV tổng:

| Biến thể | Pin | ΔCAGR | ΔMaxDD | ΔCalmar |
|---|---|---:|---:|---:|
| LAG | pin0% | −0,01pp | +0,45pp | +0,04 |
| LAG | pin1M | −0,03pp | −0,16pp | −0,02 |
| BAL | pin0% | −0,30pp | +0,13pp | −0,01 |
| BAL | pin1M | −0,58pp | +0,09pp | −0,03 |

  Không đạt tiêu chí (5): phải tốt hơn ở **cả hai** pin. DSR 0,133, PBO 0,616.
- G_DEEP (DIST52 ≤ P20, xa đỉnh 52 tuần): qua (1)–(4) trên LAG-event (Δ +10,6pp, CI [+2,2; +19,4]) nhưng KHÔNG qua trên LAG-ledger lẫn BAL-ledger. Giảm size làm LAG mất 0,9pp CAGR ⇒ cũng chỉ CẢNH BÁO-ONLY.
- G_RUN (đã chạy mạnh 20 phiên): không có ý nghĩa ở đâu cả.

→ **Không đề xuất wire gì. Không A/B full-engine.** Nếu cần, có thể hiển thị cờ "biến động cao — đuôi xấu gấp ~2,4 lần" trên candidate (display-only). Cờ này không có giá trị sizing ở cấp book: đo được trên ledger, Calmar không cải thiện ổn định khi cắt size.

| Hạng mục | Kết quả | Nhãn |
|---|---|---|
| LAG-event: N sự kiện / mã / **mùa (N độc lập)** | 5.361 / 789 / **51** | ĐO |
| Ledger R3 park0: vị thế BAL / LAG (pin0%) · cụm quý | 300 / 694 · 40 / 50 | ĐO |
| Control LAG-event Y TB | **4,551%** (= pin nghiên cứu 10-22) | ĐO |
| Control NAV: CAGR/Sharpe/MaxDD/Calmar tính lại từ DAILY | 22,1207% / 1,9329 / −16,2313% / 1,3628 (pin0%); 25,4196% / 2,1708 / −13,8506% / 1,8353 (pin1M) = METRIC pin | ĐO |
| Replay NAV tổng từ 2 book ref × trọng số allocator (Δ=0) | max sai 0,0034 VND (pin0%) / 0,0223 VND (pin1M) | ĐO |
| Trials | 12 (Q1 3×2 book + Q2 3×2 book) | — |
| DSR (Δ ngày, biến thể tốt nhất) / PBO (CSCV S=16, 13 cấu hình) | **0,133 / 0,616** | ĐO |

## 1. Thiết kế (theo PREREG)
- **Tập sự kiện**:
  - LAG-event = `lag_entry_window_width_20261021/exp_window_events.csv`: mua Open e, thoát Close e+25.
  - Cấp NAV dùng 2 ledger kho bất biến R3 park0: `537e349b…` (pin0%, SÀN) và `a6ba34d8…` (pin1M, TRẦN). md5 được kiểm lại trong script.
  - "Vị thế" = `holding_id` có ENTRY_FILL và thoát TIME/STOP/MTM. Lệnh ABANDONED_REFUND giữ nguyên.
- **Đặc trưng** tại Close e−1 (PIT): VOL60, RUN20, DIST52. GAP đo tại Open e, chỉ dùng cho R2 chạy lúc mở cửa. Không dùng `profit_*`.
- **Q1**: R1 giới hạn R×0,98 sống 3 phiên · R2 bỏ lệnh nếu GAP > 3% · R3 mua Open phiên kế sau phiên đầu tiên đóng cửa dưới R, tối đa Open e+2. Thoát giữ nguyên ngày/giá control.
- **Q2**: ngưỡng P80/P20 cắt trên IS (2014–19), riêng từng tập. Hành động = giảm 50% size, phần tiền thừa nằm im (pin0% = 0, pin1M = dep1m PIT).
- **NAV**:
  - Overlay bậc 1 trên book ref: Δ_i(t) = phần biến thể − phần control, đánh dấu Close cache; sau ngày thoát đóng băng ở chênh tiền thu về.
  - NAV tổng = replay lợi suất 2 book × trọng số allocator `cap_*` phiên trước − `rebal_cost`. Δ=0 tái hiện `combined_nav` tới 0,02 VND.
- **Thống kê**: bootstrap cụm (mùa cho LAG-event, quý vào lệnh cho ledger) 2.000 lần, seed 20261022; Holm trong mỗi họ; DSR trên Δ lợi suất ngày; PBO CSCV.

## 2. Q1 — Kết quả

### 2a. LAG-event (5.361), Δ = Y biến thể − Y control (pp) — ĐO
| Luật | Pin | Δ | CI95 cụm-mùa | ΔIS | ΔOOS | Bỏ-một-năm [min; max] | % không khớp | % không khớp ở tercile thắng | Giá vào tốt hơn (bps, lệnh khớp) |
|---|---|---:|---|---:|---:|---|---:|---:|---:|
| R1 LIMIT2 | pin0% | **−1,79** | [−2,81; −0,88] | −1,09 | −2,16 | [−2,09; −1,18] | 48,0 | 53,1 | +222 |
| R1 LIMIT2 | pin1M | **−1,64** | [−2,65; −0,74] | −0,90 | −2,03 | [−1,93; −1,03] | 48,0 | 53,1 | +222 |
| R2 GAPSKIP3 | pin0% | −0,10 | [−0,32; +0,11] | −0,20 | −0,05 | [−0,15; −0,02] | 6,2 | 5,0 | — |
| R2 GAPSKIP3 | pin1M | −0,08 | [−0,30; +0,14] | −0,18 | −0,03 | [−0,13; +0,01] | 6,2 | 5,0 | — |
| R3 PULLBACK | cả hai | −0,33 | [−0,69; −0,01] | −0,05 | −0,48 | [−0,39; −0,15] | 0 | 0 | **−35** (đắt hơn) |

### 2b. Ledger — Δ lợi suất giao dịch (pp) và cấp NAV tổng — ĐO
| Biến thể | Pin | Δ/giao dịch [CI95 cụm-quý] | % không khớp | ΔCAGR | ΔMaxDD | ΔCalmar | ΔCAGR IS / OOS |
|---|---|---|---:|---:|---:|---:|---|
| R1 · BAL | pin0% | −4,53 [−7,21; −1,84] | 41,7 | −2,20 | −3,01 | −0,33 | −4,95 / +0,50 |
| R1 · LAG | pin0% | −2,37 [−3,55; −1,25] | 51,6 | −2,72 | +0,92 | −0,10 | −4,15 / −1,34 |
| R2 · BAL | pin0% | −0,31 [−0,88; +0,19] | 4,7 | −0,00 | +1,76 | +0,17 | +0,08 / −0,08 |
| R2 · LAG | pin0% | −0,51 [−0,97; −0,12] | 4,9 | −0,35 | −0,51 | −0,06 | −2,02 / +1,26 |
| R3 · BAL | pin0% | −0,35 [−0,97; +0,21] | 0 | −0,08 | −1,10 | −0,09 | −0,34 / +0,17 |
| R3 · LAG | pin0% | +0,09 [−0,34; +0,48] | 0 | −0,06 | +0,68 | +0,06 | +0,69 / −0,77 |
| R1 · BAL | pin1M | −5,43 [−7,85; −2,85] | 42,4 | −2,74 | −1,39 | −0,35 | −4,73 / −0,81 |
| R1 · LAG | pin1M | −2,23 [−3,42; −1,12] | 53,2 | −2,73 | −0,15 | −0,21 | −4,07 / −1,43 |
| R2 · BAL | pin1M | −0,08 [−0,56; +0,39] | 3,6 | +0,06 | +1,07 | +0,16 | +0,11 / +0,02 |
| R2 · LAG | pin1M | −0,45 [−0,91; −0,05] | 5,2 | −0,37 | −0,89 | −0,14 | −2,18 / +1,38 |
| R3 · BAL | pin1M | −0,14 [−0,77; +0,44] | 0 | −0,05 | −0,40 | −0,06 | −0,16 / +0,05 |
| R3 · LAG | pin1M | +0,03 [−0,38; +0,43] | 0 | +0,03 | +0,05 | +0,01 | +0,71 / −0,61 |

- **Không luật nào qua tiêu chí (1)** của Q1 (Δ/giao dịch > 0 với CI loại trừ 0) ⇒ NO-GO, không cần xét tiếp.
- R2·BAL có ΔMaxDD +1,1…+1,8pp và ΔCalmar +0,16 ở cả 2 pin. Nhưng ΔCAGR ≈ 0, Δ/giao dịch âm, chỉ 47–48 vị thế bị bỏ, và chỉ số Calmar phụ thuộc đường đi của vài lệnh. **Không phải tín hiệu**: không qua (1), (3), (6). Ghi lại để không ai "phát hiện lại" nó như một edge.
- Cơ chế của R1 thua (định tính): mã LAG/BAL tốt thường không quay lại dưới giá tham chiếu −2%. Lệnh giới hạn vì vậy chọn lọc ngược: chỉ khớp những mã đang yếu, và bỏ lỡ mã chạy. Điều này nhất quán với nghiên cứu 08-10, nơi nhóm bị trần `≤anchor` chặn lại tốt hơn +2,29pp.

## 3. Q2 — Kết quả

### 3a. LAG-event (5.361 / 51 mùa) — ĐO
| Nhóm | n | HIT15 nhóm / còn lại | ΔHIT15 [CI95 cụm-mùa] | ΔIS / ΔOOS | Bỏ-một-năm min | MAE TB nhóm / còn lại | P5 nhóm / còn lại | Y TB nhóm / còn lại (Δ [CI]) | Holm |
|---|---:|---|---|---|---:|---|---|---|:-:|
| **G_VOL** (VOL60 ≥ 0,593) | 1.266 | 30,5% / 12,8% | **+17,7 [+14,3; +21,6]** | +19,4 / +16,8 | +17,0 | −11,9% / −7,5% | −23,0% / −14,3% | 5,09 / 4,38 (+0,71 [−1,42; +3,01]) | ✓ |
| G_RUN (RUN20 ≥ 9,3%) | 1.081 | 20,9% / 16,0% | +4,9 [−1,0; +10,3] | +5,6 / +4,6 | +3,5 | −9,5% / −8,3% | −19,1% / −15,0% | 4,66 / 4,52 | ✗ |
| **G_DEEP** (DIST52 ≤ −30,4%) | 1.466 | 24,7% / 14,1% | **+10,6 [+2,2; +19,4]** | +6,3 / +12,1 | +3,4 | −10,6% / −7,8% | −17,9% / −14,8% | 4,91 / 4,42 (+0,49 [−2,06; +3,24]) | ✓ |

G_VOL ΔP5 = −8,69pp, CI95 cụm [−10,96; −6,00].

### 3b. Ledger (vị thế thật của sổ R3) — ĐO
| Book · nhóm | Pin | n nhóm | HIT15 nhóm / còn lại | ΔHIT15 [CI95 cụm-quý] | ΔIS / ΔOOS | Lợi suất TB nhóm / còn lại | Qua (1)–(4)? |
|---|---|---:|---|---|---|---|:-:|
| BAL · G_VOL | pin0% | 73 | 43,8 / 24,7 | +19,2 [+5,0; +32,8] | +8,0 / +22,8 | 9,6 / 9,7 | ✓ |
| BAL · G_VOL | pin1M | 69 | 37,7 / 25,8 | +11,9 [−3,5; +26,7] | +3,6 / +14,1 | 14,1 / 8,9 | ✗ (CI) |
| BAL · G_RUN | pin0% / pin1M | 81 / 89 | 34,6 / 27,4 · 32,6 / 26,8 | +7,2 [−3,7; +20,7] · +5,8 [−7,0; +18,5] | | | ✗ |
| BAL · G_DEEP | pin0% / pin1M | 61 / 59 | 31,2 / 28,9 · 28,8 / 28,4 | +2,3 · +0,4 (CI chứa 0) | đổi dấu | | ✗ |
| LAG · G_VOL | pin0% | 149 | 30,2 / 14,7 | +15,5 [+7,6; +23,5] | +10,9 / +18,9 | 4,9 / 6,4 | ✓ |
| LAG · G_VOL | pin1M | 151 | 29,1 / 14,7 | +14,5 [+6,8; +22,1] | +9,7 / +17,8 | 5,4 / 6,3 | ✓ |
| LAG · G_RUN | cả hai | 122 / 117 | ≈ 18 / 18 | ≈ 0 | | | ✗ |
| LAG · G_DEEP | pin0% / pin1M | 172 | 19,2 / 17,6 · 20,9 / 16,8 | +1,6 · +4,1 (CI chứa 0) | | | ✗ |

### 3c. Hành động "giảm 50% size" — cấp NAV tổng — ĐO
| Biến thể | Pin | ΔCAGR | ΔMaxDD | ΔCalmar | ΔCalmar IS / OOS | Book: ΔCAGR / ΔMaxDD |
|---|---|---:|---:|---:|---|---|
| G_VOL · LAG | pin0% | −0,01 | +0,45 | +0,04 | −0,09 / +0,07 | +0,13 / +0,20 |
| G_VOL · LAG | pin1M | −0,03 | **−0,16** | **−0,02** | −0,09 / +0,07 | +0,09 / −1,33 |
| G_VOL · BAL | pin0% | −0,30 | +0,13 | −0,01 | +0,08 / +0,01 | −0,94 / −2,06 |
| G_VOL · BAL | pin1M | −0,58 | +0,09 | −0,03 | +0,10 / −0,03 | −1,66 / −3,06 |
| G_DEEP · LAG | pin0% / pin1M | −0,92 / −0,96 | +0,02 / −0,03 | −0,06 / −0,07 | | |
| G_RUN · LAG | pin0% / pin1M | −0,65 / −0,65 | +0,52 / −0,09 | +0,00 / −0,06 | | |
| *(G_DEEP · BAL)* | pin0% / pin1M | −0,24 / −0,27 | +3,36 / +0,73 | +0,34 / +0,08 | −0,08 / +0,42 | |

- **Không biến thể nào đạt (5)–(7)**. G_VOL·LAG gần nhất, nhưng ở pin1M MaxDD và Calmar xấu đi; Calmar IS âm ở cả hai pin.
- *G_DEEP·BAL* có ΔCalmar dương ở cả 2 pin, nhưng nhóm này **không** qua bước xác nhận rủi ro (ΔHIT15 ≈ 0, đổi dấu IS/OOS). Cải thiện MaxDD +3,4pp ở pin0% chỉ còn +0,7pp ở pin1M, tức là phụ thuộc đường đi. Theo PREREG không được cứu bằng biến thể này.
- **Vì sao đuôi xấu ở cấp mã không thành DD ở cấp book** (giả thuyết, CHƯA đo):
  - MaxDD của book do thị trường chung quyết định, không do vài mã biến động cao.
  - G_VOL chiếm ~20% vị thế, lợi suất TB không thấp hơn, nên cắt size chủ yếu là cắt exposure.

## 4. Kiểm định đa trial
- **DSR** = 0,133 ≪ 0,95. Tính trên chuỗi Δ lợi suất ngày (biến thể − control, NAV tổng pin0%), N=12. Biến thể có SR Δ cao nhất là R2·BAL, với SR/ngày −0,0007: không biến thể nào có Δ Sharpe dương.
- **PBO** = 0,616 ≥ 0,5. CSCV S=16, 12.870 tổ hợp, 13 cấu hình gồm cả control, metric Sharpe. Cấu hình IS-best thường dưới trung vị OOS.
- Holm: Q1 các dòng "qua Holm" đều là R1 với Δ **âm**, tức có ý nghĩa theo hướng XẤU. Q2 G_VOL qua ở cả LAG-event và LAG-ledger.

## 5. Giới hạn
- **Overlay bậc 1**, không phải full-engine. Không mô hình hoá:
  - tái đầu tư phần chênh;
  - allocator phản ứng với NAV biến thể (giữ trọng số `cap_*` của control);
  - slot/vốn được giải phóng dồn sang candidate khác.
  Với Q1-R1 (~50% không khớp), chi phí cơ hội ở đây là **cận dưới**: tiền nằm im thay vì vào mã khác. Live đang thiếu triển khai vốn LAG, nên đây là giả định sát thực tế (nghiên cứu 10-21).
- Đánh dấu trong kỳ giữ dùng Close cache. Engine đánh dấu theo nguồn khác ở khoảng 20% số ngày (xem Deviation 3). Δ cuối kỳ dùng đúng giá thoát ledger, nên lệch chỉ ảnh hưởng đường đi (MaxDD), không ảnh hưởng CAGR cuối.
- BAL: 300 vị thế / 40 quý là mẫu nhỏ, CI rộng. Kết luận BAL yếu hơn LAG.
- R3 và R1 dùng Low/Close ngày để quyết khớp. Giả định lệnh giới hạn khớp khi Low ≤ giá, bỏ qua hàng đợi, nên **lạc quan** cho R1. R1 vẫn thua.
- 2 ledger pin1M/pin0% có tập vị thế khác nhau (khoảng 2 vị thế), nên không phải mẫu độc lập.

## 6. Deviations so với PREREG
1. **Phí**: PREREG ghi "0,1%/chiều (cost factor engine)". Thực tế cost factor của engine pin là mua ≈0,25%, bán 0,35–0,65% (gồm thuế/slippage), đo từ `fee/buy_amount` và `fee/sell_amount` của ledger. Overlay dùng **đúng cost factor từng giao dịch của ledger** để nhất quán với control. Cách này bảo thủ hơn 0,1%. LAG-event Y là lợi suất gộp (không phí), như 2 nghiên cứu trước.
2. **Cache LAG-event** = `data/bq_cache` (đêm 10-21), không phải `postrestate` như PREREG §1 ghi chung. Lý do: để control tái hiện đúng Y 4,551% của tập đã pin. Kết quả: Open khớp `buyO0` 100%, Close e+25 khớp `exA0` 99,94%. Ledger dùng `postrestate` đúng như PREREG. Script ép env vì phiên đặt sẵn `BQ_LOCAL_CACHE=data/bq_cache`.
3. **Self-check (c)** (dựng lại giá trị cổ phiếu từ TX × Close cache) **KHÔNG ra 0 VND**: lệch ở 19–24% số ngày, max 10–17 tỷ (chủ yếu 2025-07). Lệnh mua/bán của ledger khớp Open cache 100%, nên phần lệch là do engine mark-to-market trong kỳ giữ bằng nguồn giá khác. Cổng 0 VND thay thế đã đạt:
   - (a) metric tính lại khớp METRIC pin tới 4 chữ số;
   - (b) overlay rỗng = 0,0 VND;
   - replay NAV tổng ≤ 0,02 VND.
4. **Fill nhiều phiên** (43–44% vị thế có giá vốn ≠ Open e): luật áp cho TOÀN BỘ ngân sách B tại phiên khớp mới. Control giữ đúng dòng tiền nhiều phiên của ledger.
5. 2 `holding_id` `VCR_20200427_?` có lệnh bán mà không có lệnh mua: bỏ qua. Số lệnh khớp sau ngày thoát (`NOFILL_LATE`) = 0.
6. Ngưỡng Q2 ledger cắt trên ledger **pin0%** IS và áp nguyên cho ledger pin1M. PREREG không nói rõ, chọn để 2 pin dùng cùng ngưỡng.
7. Cụm ledger LAG = quý dương lịch của ngày vào lệnh, không phải mùa Release (ledger không mang Release_Date). Đúng như PREREG §1.
8. `nav_overlay_stats.py` là bản sao nguyên văn `cluster_boot`/`holm` của `nav_overlay.py`. `lag_events.py` import nó để không phải chạy overlay khi import.

## 7. Không lặp nghiên cứu cũ
- 10-22 (`lag_price_reaction_class`): đó là lọc loại theo drift. Ở đây không loại mã nào. Q2 đo đuôi chứ không đo trung bình, và lợi suất TB của G_VOL **không** thấp hơn, nhất quán với NO-GO sáng nay.
- 08-09/08-10/10-21 (cửa sổ, anchor): R1 xác nhận lại theo hướng khác cùng một điều. Chặn giá vào thấp hơn tham chiếu sẽ chọn lọc ngược và tốn tiền.
