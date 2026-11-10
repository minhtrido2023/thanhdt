# Cổng edge-health THEO THÁNG cho BAL vs chạy "mù" — job `Taylor_20261110_053025`

## Kết luận (5 dòng)
1. **CÓ HẠI về lợi suất, KHÔNG cải thiện rủi ro điều chỉnh.** Luật gốc (tháng âm ⇒ khoá mua mới, dương ⇒ mở) làm ΔCAGR **−2,62pp (pin0%) / −2,76pp (pin1M)**. P(ΔCAGR>0) = **0,01** ở cả hai quy ước; CI90 [−4,8; −0,65]pp nằm trọn dưới 0. IS và OOS cùng âm, bỏ từng năm (LOO) không năm nào lật dấu.
2. **Sharpe xấu đi** (−0,15 / −0,12, P>0 = 0,06 / 0,11). **Calmar KHÔNG PHÂN BIỆT ĐƯỢC** (+0,04 / −0,13, P>0 = 0,26 / 0,30). MaxDD nông hơn (+2,35 / +0,59pp), nhưng 8 lịch khoá NGẪU NHIÊN trên engine thật (cùng 62 tháng khoá, cùng 26 đợt) cho MaxDD tốt hơn với trung vị **+2,76pp**. ⇒ phần DD đỡ hơn là do **giảm exposure**, không phải thông tin.
3. **Tín hiệu không mang thông tin:** P(tháng sau âm | tháng này âm) = 39,5% so với 38,1% khi tháng này dương (Fisher p = 1,0, 101 cặp tháng). Precision của tháng bị khoá = 41,9% so với tỷ lệ nền 39,6%. Lệnh bị chặn có win-rate 55,9%, gần bằng 56,6% của lệnh được giữ. Theo tiền: tránh được 43,7B lỗ nhưng bỏ lỡ 97,7B lãi.
4. **Cả 9 biến thể × 2 quy ước = 18/18 chân đều ΔCAGR < 0.** Lỗ đi theo liều: khoá càng nhiều tháng thì lỗ càng nặng. Trễ 1–2 tháng còn tệ hơn. Biến thể đỡ nhất là G5 (chỉ khoá sau 2 tháng âm liên tiếp): −0,47 / −0,98pp, Sharpe ±0, Calmar +0,34 / +0,13 với P ~0,55, tức không phân biệt được. DSR của biến thể tốt nhất = **0,02 / 0,008**. Sổ LAG đặt cùng luật cũng hại (−3,08 / −3,37pp).
5. ⇒ **Đây KHÔNG phải edge.** Nếu user vẫn muốn bật cổng thì đó là **khẩu vị rủi ro có giá**: khoảng −2,6pp CAGR/năm theo luật gốc (khoảng −0,5…−1pp nếu dùng G5), đổi lấy DD nông hơn mà khoá ngẫu nhiên cũng cho được. Khuyến nghị: không wire như một nguồn cải thiện hiệu suất. Quyết định thuộc về user; quant-skeptic sẽ phản biện.

> **Phạm vi:** chỉ PAPER. Không sửa code live, `trading_rules.json` hay main. Knob nằm trên worktree research
> `wt-balgate-1110` @ `33f005209` (gốc `bb700ab67`). Một Taylor khác đang dựng cổng live: báo cáo này là
> bằng chứng cho quyết định có bật hay không, không phải review code của job đó.

## 1. Thiết lập
- **Engine:** lệnh pin R3 park0 (registry "2026-10-08"), `$DNA_PYEXE`, threads=1, NAV 50B, 2014-01-02→2026-06-19,
  BQ snapshot `bq_cache_asof20260729_postrestate`. Knob `BAL_BUY_BLOCK_FILE` chặn **first fill** của sổ
  `v23audit_BAL` vào các phiên trong tháng bị khoá. Lệnh bị chặn bị bỏ như SLOT_BLOCK. Lệnh đang khớp dở,
  vị thế đang giữ và lệnh thoát giữ nguyên. Khi không đặt knob thì engine trơ.
- **Chân CONTROL (BLIND):** **byte-identical** với 2 pin: `537e349b` (pin0%, 22,12% / 1,93 / −16,2% / 1,36)
  và `a6ba34d8` (pin1M, 25,42% / 2,17 / −13,9% / 1,84). Self-check 0 VND ở BAL+LAG, đủ 30/30 chân, EXIT=0.
- **Tín hiệu:** lợi suất tháng lịch của sổ BAL MÙ (`nav_bal_ref`, ledger pin0% mù; là shadow, ngoại sinh với
  chân treatment). Tháng có exposure cổ phiếu trung bình <5% hoặc ret = 0 coi là "thiếu mẫu" ⇒ giữ trạng thái.
  Dùng cùng lịch khoá cho cả 2 quy ước tiền nhàn rỗi, để mỗi lần chỉ đổi 1 trục.
- **Nhân quả:** tín hiệu tháng M quyết định các phiên của tháng M+1+trễ. Lệnh xếp hàng ở phiên cuối tháng M
  khớp T+1, tức phiên đầu tháng M+1. Trễ 1 và 2 tháng mô phỏng chuỗi live chậm hơn (dựng theo exit-month).
- **N độc lập:** luật gốc có **26 đợt khoá / 51 lần chuyển trạng thái / 62 trong 150 tháng bị khoá** và 101 cặp
  tháng-có-mẫu liên tiếp. Đây là N nhỏ, nên công cụ chính là paired block bootstrap (L=21, B=4000, 1 chuỗi index
  chung) + LOO theo năm + placebo. IS/OOS chỉ để kiểm cùng dấu.
- **Pre-flight** (`preflight.txt`, per-episode, N=26, 9 trial): chỉ phát hiện được nếu Sharpe gia tăng ≥0,96/năm.
  Kịch bản lạc quan (1,0) là GO, kịch bản bảo thủ (0,5) là NO-GO. Vẫn chạy vì user yêu cầu rõ ràng.
- **N_trials = 9** (khai trong `PREREG.md` trước khi chạy chân treatment): G1_L0/L1/L2, G2_3m, G3_x2 (khoá khi < −2%),
  G4_hu2 (mở cần 2 tháng dương), G5_hl2 (khoá cần 2 tháng âm), G6_n3 (mẫu cần ≥3 mã mua hoặc expo ≥30%),
  G1_L0capx (miễn CAPIT). Chân LAG chỉ để đo, không tính là trial.

## 2. Kết quả engine (Δ = cổng − mù, R3 gộp)
| Biến thể | %tháng khoá | ΔCAGR pin0% / pin1M | ΔSharpe | ΔMaxDD (pp, + = nông hơn) | ΔCalmar | P(ΔCal>0) | IS / OOS ΔCAGR (pin0%) |
|---|---:|---|---|---|---|---|---|
| **G1_L0 (luật user)** | 41% | **−2,62 / −2,76** | −0,150 / −0,117 | +2,35 / +0,59 | +0,04 / −0,13 | 0,26 / 0,30 | −1,73 / −3,46 |
| G1_L1 (trễ 1T) | 41% | −2,83 / −3,72 | −0,185 / −0,203 | −2,62 / −1,37 | −0,34 / −0,41 | 0,10 / 0,10 | −1,10 / −4,37 |
| G1_L2 (trễ 2T) | 40% | −3,26 / −3,63 | −0,171 / −0,139 | −3,68 / −2,57 | −0,42 / −0,51 | 0,09 / 0,12 | −2,56 / −3,83 |
| G2_3m | 33% | −1,21 / −2,76 | −0,038 / −0,128 | +3,19 / +1,39 | +0,24 / −0,02 | 0,47 / 0,27 | −1,74 / −0,71 |
| G3_x2 | 15% | −0,74 / −2,13 | −0,047 / −0,122 | +0,46 / +0,43 | −0,01 / −0,10 | 0,33 / 0,08 | +0,17 / −1,60 |
| G4_hu2 | 59% | −4,46 / −5,02 | −0,244 / −0,245 | −3,03 / −1,92 | −0,45 / −0,54 | 0,12 / 0,16 | −2,73 / −5,99 |
| G5_hl2 | 21% | −0,47 / −0,98 | +0,013 / −0,006 | +3,52 / +1,42 | +0,34 / +0,13 | 0,56 / 0,54 | −0,42 / −0,52 |
| G6_n3 | 32% | −2,77 / −3,38 | −0,186 / −0,201 | +2,16 / −1,15 | +0,01 / −0,37 | 0,23 / 0,17 | −1,26 / −4,19 |
| G1_L0capx | 41% | −1,96 / −2,05 | −0,118 / −0,086 | +2,82 / +0,45 | +0,14 / −0,09 | 0,34 / 0,39 | −2,06 / −1,86 |
| *LAG book, G1_L0 (đo)* | 35% | −3,08 / −3,37 | −0,163 / −0,172 | +0,95 / +1,35 | −0,12 / −0,07 | 0,19 / 0,17 | −2,82 / −3,34 |

Nguồn: `results.json` (md5 `8e32f1e4…`), sinh bởi `analyze.py`. Ledger pin: G1_L0 pin0% md5 `d8c68175…`,
pin1M md5 `8ae049ac…`.

**G1_L0 tuyệt đối:** pin0% 19,50% / 1,78 / −13,9% / 1,40 · pin1M 22,66% / 2,05 / −13,3% / 1,71. **Neo DD (sàn) không đổi**:
cổng không phải lý do để nới neo −25,2%, vì phần cải thiện DD là do giảm exposure (§3).
**Bootstrap G1_L0 pin0%:** ΔCAGR CI90 [−4,76; −0,65]pp, P>0 = 0,01 · ΔSharpe [−0,31; +0,01], P = 0,06 ·
ΔMaxDD [−2,4; +4,1]pp, P = 0,59 · ΔCalmar [−0,52; +0,22], P = 0,26.
**LOO năm (G1_L0):** ΔCAGR nằm trong [−2,89; −1,79]pp (pin0%) và [−3,10; −2,15]pp (pin1M). Không năm nào làm
lật dấu, kể cả bỏ 2021 là năm hại nặng nhất (−17,7pp riêng năm đó ở pin0%). Δ lợi suất từng năm âm ở 11/12 năm
có hoạt động 2015–2026 (pin0%). Chỉ 2020 dương (+0,6pp); 2014 = 0.

## 3. Placebo — thông tin hay chỉ là giảm exposure?
- **Engine thật, 8 lịch khoá ngẫu nhiên** (cùng 62 tháng khoá, cùng 26 đợt, pin0%). Trung vị placebo: ΔCAGR −2,35pp,
  ΔSharpe −0,08, ΔMaxDD **+2,76pp**, ΔCalmar +0,13. Cổng thật: −2,62 / −0,150 / +2,35 / +0,04. Xếp cổng thật chung với 8
  placebo (9 chuỗi, 1 = tốt nhất): hạng 6/9 ở CAGR/Sharpe/Calmar, 5/9 ở MaxDD ⇒ **không tốt hơn khoá ngẫu nhiên**. 8 mẫu là ít; con số ≥1000 nằm ở dòng dưới.
- **Bộ xấp xỉ "trừ lệnh", 2000 placebo/biến thể** (`placebo.py`). Kiểm hợp lệ trước khi dùng: không trừ gì thì tái lập
  NAV BAL mù (residual cuối 0 VND; trung vị theo phiên 2e-5 VND; có 5 phiên 07/2025 lệch tới 12B do giá MTM) và tái
  lập R3 gộp 22,12% / 1,93 / −16,2%. So với engine, bộ xấp xỉ khớp **CAGR** (G1_L0 −2,22 so với −2,62pp) nhưng **sai
  chiều MaxDD** (−4,5 so với +2,35pp), vì nó không mô hình hoá việc tiền/slot được giải phóng rồi tái dùng. ⇒ chỉ đọc
  placebo xấp xỉ cho CAGR/Sharpe. Phân vị của cổng thật: G1_L0 ΔCAGR **31%**, ΔSharpe **35%**. Mọi biến thể nằm trong
  khoảng 12–49%, không biến thể nào gần 95%.
- **Tiêu chí placebo không đạt; đây không phải lời khẳng định placebo cao hơn về mặt thống kê.** Tiêu chí PREREG là thắng
  ≥95% placebo; cổng thật ở phân vị 31%. 8 placebo engine có MaxDD trung vị tốt hơn cổng thật, nhưng phân tán rất rộng
  (−2,0…+6,5pp). Điều đo được chỉ là: cổng thật không phân biệt được với khoá ngẫu nhiên.

## 4. Phân rã (G1_L0, bộ xấp xỉ trên ledger mù pin0%)
- Bị chặn **152/396** holding. Tránh được **43,7B lỗ** nhưng bỏ lỡ **97,7B lãi**, ròng **−54,0B** (theo VND của sổ mù).
  Win-rate lệnh bị chặn 55,9% so với 56,6% lệnh giữ. Lãi trung bình/lệnh 355M so với 423M.
- Chi phí đứng ngoài: exposure cổ phiếu trung bình của BAL **34,7% → 27,4%** NAV sổ. CAGR riêng sổ BAL 17,3% → 12,0%
  (pin0%) và 21,7% → 16,1% (pin1M). Carry 1M **không** cứu được (ΔCAGR pin1M −2,76pp, sâu hơn pin0%), vì tiền nhàn
  rỗi ~3,5%/năm thua xa kỳ vọng của lệnh BAL.
- Cơ chế: tháng âm của BAL thường là pha điều chỉnh trong xu hướng. Tháng kế tiếp trung bình vẫn +1,45% (tháng bị
  khoá) so với +2,30% (tháng mở). Khoá đúng lúc giá rẻ là bỏ lỡ phục hồi (2021: −17,7pp). DT5G đã lo phần
  khủng hoảng thật, nên cổng tháng lặp lại cùng việc nhưng bằng một tín hiệu nhiễu hơn.

## 5. Đa kiểm định
- **DSR** (chuỗi excess daily so với mù; họ 9 trial; biến thể tốt nhất G5): **0,021 (pin0%) / 0,008 (pin1M)**. SR excess
  năm của mọi biến thể đều âm (−0,19 … −0,93).
- **PBO** (CSCV S=16, 12.870 split, họ 9 + BLIND): 0,107 / 0,169. PBO thấp ở đây chỉ nói rằng việc chọn theo IS khá ổn
  định; nó KHÔNG cứu được kết luận, vì cấu hình tốt nhất vẫn có excess âm.
- Liều–tác dụng: thứ tự theo %tháng khoá là G3 15% (−0,74), G5 21% (−0,47), G6 32% (−2,77), G2 33% (−1,21),
  G1 41% (−2,62), G4 59% (−4,46). Gần đơn điệu: khoá càng nhiều thì lỗ càng nặng. Trễ 0→1→2 tháng thì lỗ
  −2,62 → −2,83 → −3,26. Đây là chữ ký của "giảm exposure trên một sổ kỳ vọng dương", không phải chữ ký của timing.

## 6. Đối chiếu với kết luận cũ
- Giống trường hợp **park 0 vs 0,3**: hiệu ứng rủi ro nằm trong nhiễu. Khác ở chỗ chiều lợi suất của cổng này có
  ý nghĩa thống kê là **âm**. Vì vậy đây không trung tính như park mà là chi phí thật.
- Phù hợp với kết luận "DT5G là bảo hiểm, không phải edge". Cổng tháng là lớp bảo hiểm thứ hai mà phí bảo hiểm
  (−2,6pp/năm) vượt xa phần chi trả (DD đỡ ~2pp, ngẫu nhiên cũng cho được).
- Cổng LAG hiện hành (neg_streak ≥3 trên trailing-12M, ngưỡng đã cam kết trước từ nghiên cứu edge-cycle) dùng tín
  hiệu khác hẳn (mean12 của cohort sự kiện, chậm). Báo cáo này chỉ đo luật TRẢ VỀ THEO THÁNG áp lên LAG (−3,1pp), **không**
  đánh giá và không đề xuất đổi cổng LAG hiện hành.

## 7. Caveat
- Tín hiệu lấy NAV sổ mù trong backtest. Chuỗi live có thể khác: dựng theo exit-month thì chậm hơn, và kết quả trễ
  1–2 tháng là tệ hơn.
- N = 26 đợt khoá: không thể chứng minh "vô hại". Chỉ chứng minh được "hại về CAGR" (P = 0,99) và "không cải thiện
  Sharpe/Calmar".
- Cùng caveat capacity của pin R3 (LAG không ràng buộc khối lượng). CAGR thật ≈ backtest − 1,5pp. Proxy `pin1M` có
  53/150 tháng dựng lại.
- Placebo engine chỉ có 8 mẫu. Placebo ≥1000 chạy trên bộ xấp xỉ, và bộ này chỉ hợp lệ cho CAGR/Sharpe.

## 8. Tái lập
`run_leg.sh <TAG> BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER=off|dep1m BAL_BUY_BLOCK_FILE=blocks/<V>.txt`
(code `wt-balgate-1110` @ `33f005209`). `build_blocks.py <ledger mù> blocks [bal|lag]` · `analyze.py` · `placebo.py`.
Danh sách chân: `queue.txt` và `queue_plac.txt`. Log: `logs/`.
