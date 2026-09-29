# CCS Phase 1 — bản đồ expectancy có điều kiện (H1–H6 + 1 amendment)

> Taylor, job `Taylor_20260905_141801`, 2026-09-05. Đề cương: `mike/reports/research_proposal_conviction_sizing_20260905.md`. Đầu vào: ledger Phase 0 (`Taylor_20260905_135003`, 3/3 gate ĐẠT, pin R3 tái lập byte-identical).
> **Phase 1 = ĐO, không backtest sizing.** Không một dòng logic production nào bị đụng.

## Kết luận một dòng

**Không hypothesis nào được đề cử sang Phase 2.** 5/7 chết ngay ở tiêu chí đã tiền-đăng ký; 2 cái sống qua sàng lọc dấu (H4, H6) đều **hỏng ở chỗ khác nhau nhưng cùng chí mạng**: H4 mất 86% hiệu ứng ra OOS và cận trên khả thi OOS (**0,28pp**) nằm **dưới** sàn nhiễu harness 0,385pp; H6 có phản ứng **không đơn điệu** theo tercile (MID ≥ TOP ở IS và ở BAL) nên chính động tác sizing mà nó hàm ý — "dồn thêm vào TOP" — không được dữ liệu ủng hộ. Với N_trials = 7, p đã hiệu chỉnh tốt nhất là **0,371** (cả Bonferroni lẫn BH) — không cái nào tới gần ngưỡng.

**"Phase 2 không đáng chạy" theo đúng đề cương §5** là kết luận của tôi. Có **một** quan sát HẬU NGHIỆM đủ ổn định để đáng cân nhắc tiền-đăng ký lại thành một nghiên cứu riêng (§6) — nhưng nó không phải một trong 7 hypothesis, và tôi không đề cử nó như thể nó là.

## 0. Sáu quyết định thiết kế đã áp đúng nguyên văn

| | Quyết định | Áp thế nào trong code |
|---|---|---|
| D1 | `ABANDONED_REFUND` loại khỏi thước đo CHÍNH, báo nhánh phụ song song | `PRIMARY` = 1.012 lệnh (loại 1.044), `SENS` = 2.056. Mọi contrast chạy **cả hai** nhánh; `sign_flip_vs_sensitivity` là một tiêu chí loại. **0/7 hypothesis đổi dấu giữa hai nhánh** — D1 không phải chỗ giết ai cả, nhưng nó nén biên độ xuống ~40% ở mọi ô (ABANDONED_REFUND giữ trung vị 4 phiên, expectancy ≈ 0) |
| D2 | H2 định nghĩa lại recovery bằng BREADTH | `recovery_breadth` = tercile breadth ở t−1 thuộc MID/HIGH **và** có ít nhất một phiên LOW trong 21 phiên trước đó. Khai `N_trials = 7`; H2 bản gốc (DT5G-upgrade) vẫn báo cáo dưới nhãn `H2o` để không giấu trial nào |
| D3 | H5 DESCRIPTIVE-ONLY | Gắn cứng `status="DESCRIPTIVE"`; nó tự động vào nhánh DEAD bất kể số đẹp hay xấu |
| D4 | H3 chỉ kết luận ở mức gộp hoặc LAG | Contrast chính chạy scope `BOTH`; bảng tách BAL/LAG in ra dưới nhãn `DESCRIPTIVE (per-book split)` |
| D5 | H6 phải kiểm soát `sig_n_cands` | Phân tầng 4 mức (1-4 / 5-8 / 9-17 / 18+), gộp theo trọng số Mantel-Haenszel, bootstrap phân tầng |
| D6 | `rating_8l` chỉ mô tả | Không xuất hiện trong bất kỳ mask nào; chỉ dùng một lần ở §6 để **bác bỏ** một cách giải thích |

## 1. Bảng expectancy — nhánh CHÍNH (đã loại ABANDONED_REFUND)

N = số **episode độc lập** (cụm entry cùng bucket cách nhau ≤10 phiên — đúng quy ước Phase 0). `exp` = expectancy = trung bình `ret`/lệnh. `R` = `ret / (σ60 × √phiên)`, winsor [1%, 99%] vì 6 dòng có `vol60 ≈ 0` đẩy giá trị thô tới −2,8 triệu.

| H | Nhóm conviction | n | ep | win | exp | R (trbình / trung vị) | Nhóm đối chứng | n | ep | win | exp | **Δexp** | 95% CI | p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | dd52 ≤ −20% | 336 | 64 | 57,4% | +7,63% | 0,43 / 0,28 | dd52 > −20% | 676 | 71 | 58,1% | +6,55% | **+1,08pp** | [−3,05; +5,29] | 0,63 |
| H2 | ey CHEAP × breadth-recovery | 49 | **18** | 63,3% | +11,30% | 0,79 / 0,56 | còn lại có ey | 919 | 74 | 59,1% | +7,11% | **+4,19pp** | [−3,10; +12,97] | 0,27 |
| H2o | ey CHEAP × DT5G-recovery | 77 | **17** | 62,3% | +10,33% | 0,56 / 0,39 | còn lại có ey | 891 | 75 | 59,0% | +7,06% | **+3,28pp** | [−7,10; +12,41] | 0,60 |
| H3 | breadth tercile LOW (t−1) | 426 | 39 | 57,0% | +5,13% | 0,31 / 0,23 | MID+HIGH | 586 | 53 | 58,5% | +8,20% | **−3,07pp** | [−7,41; +1,57] | 0,21 |
| H4 | LAG surprise HIGH × ey CHEAP | 98 | 41 | 66,3% | +9,39% | 0,64 / 0,32 | còn lại LAG | 511 | 50 | 54,6% | +4,59% | **+4,80pp** | [−0,07; +9,73] | 0,053 |
| H5 | ≤10 phiên sau DT5G upgrade | 215 | **19** | 59,1% | +7,61% | 0,42 / 0,39 | >10 phiên | 781 | 69 | 57,5% | +6,55% | **+1,06pp** | [−5,26; +7,65] | 0,77 |
| H6 | rank TOP | 535 | 66 | 54,6% | +6,13% | 0,37 / 0,18 | rank BOTTOM | 129 | 48 | 50,4% | +3,17% | **+2,97pp** | [−0,90; +6,82] | 0,14 |

Nhánh `+ABANDONED_REFUND` (sensitivity, D1) giữ **nguyên dấu ở cả 7 ô**, biên độ co lại ~40–60%: H1 +0,43pp · H2 +1,81pp · H2o +2,12pp · H3 −1,13pp · H4 +1,80pp · H5 +0,97pp · H6 +1,55pp. Không hypothesis nào bị D1 giết, và không hypothesis nào được D1 cứu.

**Không có hiệu ứng thời gian nắm giữ nào giả dạng thành edge** — `ret` chưa chuẩn hoá theo thời gian, nên đã kiểm: H4 treat/control đều **26,0 phiên** trung bình; H6 TOP/MID/BOTTOM là 30,3 / 32,0 / 32,6 phiên (nhóm "thắng" giữ *ngắn hơn*, tức là nếu có thiên lệch thì nó đang chống lại kết luận, không đỡ). Cột `R` — đã chuẩn hoá cả biến động lẫn √thời gian — xác nhận cùng chiều cho H4 (ΔR = +0,31, p = 0,073) nhưng yếu hơn hẳn cho H6 (ΔR = +0,17, p = 0,24).

## 2. Sàng lọc sống/chết — tiêu chí tiền-đăng ký

| H | ep nhỏ nhất | IS 2014-19 | OOS 2020+ | cùng dấu | LOO ổn | đổi dấu vs D1 | **Verdict** |
|---|---|---|---|---|---|---|---|
| H1 | 64 | +5,18pp | −1,49pp | ❌ | ✓ | không | **CHẾT** |
| H2 | **18** ❌ | +10,07pp | −0,92pp | ❌ | ✓ | không | **CHẾT** |
| H2o | **17** ❌ | +3,58pp | +2,56pp | ✓ | ❌ | không | **CHẾT** |
| H3 | 39 | +0,70pp | −5,42pp | ❌ | ✓ | không | **CHẾT** |
| H4 | 41 | +8,41pp | **+1,17pp** | ✓ | ✓ | không | sống qua sàng — xem §3 |
| H5 | **19** ❌ | +7,34pp | −1,40pp | ❌ | ✓ | không | **CHẾT** (và D3 đã cấm kết luận) |
| H6 | 48 | +3,03pp | +3,45pp | ✓ | ✓ | không | sống qua sàng — xem §4 |

**Hiệu chỉnh đa kiểm định, N_trials = 7:** p thô nhỏ nhất là H4 (0,053) ⇒ Bonferroni 0,371, BH 0,371. Cái thứ hai là H6 (0,136) ⇒ BH 0,477. Không cái nào tới gần 0,05, chứ chưa nói tới ngưỡng DSR ≥ 0,95 mà đề cương đòi trước khi wire. Riêng con số này đã đủ để nói: **những gì đo được ở đây tương thích với nhiễu.**

Ba cái chết vì **IS/OOS ngược dấu** (H1, H2, H3) đều có chung một chữ ký: hiệu ứng nằm ở nửa đầu mẫu rồi biến mất hoặc đảo chiều. H1 là ví dụ sạch nhất — 2014-2018 dương gần như liên tục (+3,0 / +6,5 / −5,6 / +7,9 / +10,9pp), rồi 2020 trở đi lặng hẳn (2020 +0,0 · 2022 −3,6 · 2024 −2,5pp). Đây đúng là thứ mà tiêu chí IS/OOS được đặt ra để bắt.

**H3 còn sai cả chiều giả thuyết.** Đề cương đặt "breadth tercile đáy → quay đầu" là nhóm *conviction*; đo ra breadth LOW **kém hơn** MID/HIGH 3,07pp. Ô phái sinh "LOW & đang quay đầu" thì Phase 0 đã đếm được 12–20 episode, tức dưới sàn ngay từ đầu — không chạy, đúng như D-ràng buộc.

## 3. H4 — sống qua sàng lọc dấu, chết ở sàn ý nghĩa thực tế

H4 là ô sạch nhất về mặt hình thức: 41 vs 50 episode (trên sàn 30), IS và OOS cùng dấu, LOO ổn định trong dải hẹp [+4,12; +5,66pp], không nhạy với việc bỏ mã hay bỏ ngành (bỏ ngành lớn nhất → Δ còn *tăng* lên +5,45pp; bỏ mã có return tốt nhất → +3,98pp), 74 mã khác nhau, top-3 mã chỉ chiếm 12,2% số lệnh. Không phải hiện vật tập trung.

Ba lý do vẫn **không đề cử**:

1. **Suy giảm OOS 86%.** IS +8,41pp → OOS **+1,17pp**, CI OOS [−5,30; +7,44] ôm trọn số 0. Tiêu chí tiền-đăng ký chỉ đòi *cùng dấu*, và H4 qua — nhưng Phase 2 sẽ phải sizing theo hiện thực OOS chứ không theo con số IS.
2. **Cận trên khả thi OOS = 0,28pp < sàn nhiễu 0,385pp.** Ước lượng bậc nhất, k = 1,5, đã chặn không cho dịch chuyển nhiều vốn hơn nhóm cấp vốn thực có: toàn mẫu +0,53pp, IS +1,48pp, **OOS +0,28pp**. Nghĩa là: kể cả nếu hiệu ứng OOS là thật, ở quy mô vốn mà nhóm này thực sự hấp thụ được thì nó **không đủ lớn để phân biệt với nhiễu harness**. Đây chính là câu "kể cả đúng cũng không đủ lớn để dùng" mà dispatch yêu cầu tôi nói thẳng khi gặp.
3. **87/98 lệnh của H4 (88,7%) nằm luôn trong nhóm TOP của H6.** H4 và H6 **không phải hai ứng viên độc lập** — chúng gần như cùng một tập lệnh nhìn từ hai phía (ranking của LAG vốn được lái bởi chính surprise). Đề cử cả hai sang Phase 2 sẽ là đếm một hiệu ứng hai lần.

Thêm một điều Phase 2 sẽ phải nuốt nếu ai đó vẫn muốn chạy: nhóm conviction của H4 **mỏng thanh khoản hơn** phần còn lại (ADV trung vị **3,56 tỷ** vs 5,86 tỷ). Upsize đúng vào chỗ mỏng hơn là hướng sai của rủi ro capacity, và caveat mô hình fill 20% ADV (`lag-adv-filter`, mốc 2026-12-15) vẫn đang mở.

## 4. H6 — sống qua sàng lọc dấu, chết vì phản ứng KHÔNG ĐƠN ĐIỆU

Sau khi kiểm soát `sig_n_cands` đúng như D5 đòi, hiệu ứng TOP−BOTTOM **không biến mất** — nó còn hơi mạnh lên và ổn định qua cả 4 tầng:

| tầng `sig_n_cands` | n TOP | n BOT | ep TOP | ep BOT | exp TOP | exp BOT | Δ |
|---|---|---|---|---|---|---|---|
| 1-4 | 181 | 12 | 60 | 9 | +4,51% | −1,07% | +5,58pp |
| 5-8 | 80 | 34 | 33 | 26 | +6,89% | +5,77% | +1,12pp |
| 9-17 | 94 | 57 | 31 | 25 | +6,80% | +2,70% | +4,10pp |
| 18+ | 180 | 26 | 36 | 12 | +7,08% | +2,76% | +4,33pp |

Gộp có kiểm soát: **+3,57pp**, CI [−0,21; +7,28], p = 0,065 (thô +2,97pp) ⇒ D5 xác nhận đây **không** phải hiện vật cấu tạo. Tách IS/OOS thì +1,38pp (p = 0,45) và +5,08pp (p = 0,065) — cùng dấu, OOS mạnh hơn.

**Nhưng ba tercile không đơn điệu, và đó là điều giết H6 với tư cách một luật sizing:**

| | n | exp (đều) | exp (theo vốn) | win |
|---|---|---|---|---|
| TOP | 535 | +6,13% | +5,68% | 54,6% |
| **MID** | 254 | **+6,54%** | +3,87% | **60,6%** |
| BOTTOM | 129 | +3,17% | +1,56% | 50,4% |

MID **cao hơn** TOP ở trung bình đều, và cách biệt hẳn ở IS (**+8,18% vs +3,57%**) lẫn ở riêng sổ BAL (+9,69% vs +9,20%); chỉ ở OOS thì TOP mới vượt. Hệ quả cụ thể, không phải chuyện học thuật: overlay mà H6 hàm ý là "dồn thêm vào TOP, rút từ phần còn lại", mà phần còn lại **gồm MID** — tức là rút tiền khỏi nhóm có expectancy ngang hoặc cao hơn. Tính đúng phía cấp vốn thì cận trên khả thi **đổi dấu giữa hai nửa mẫu: IS −2,51pp, OOS +1,42pp** (toàn mẫu +0,73pp). Một luật sizing mà chiều tác động lật giữa IS và OOS thì không phải luật.

Đối chiếu D4: hiệu ứng gần như toàn bộ nằm ở BAL (+6,47pp) chứ không phải LAG (+1,65pp), mà nhánh BOTTOM của BAL chỉ có **20 episode** — dưới sàn. Mức gộp thì đủ N nhưng lại bị pha bởi LAG gần như không có hiệu ứng.

## 5. H2 và H5 — hai ràng buộc N là THẬT, không phải xui

- **H2 sau amendment D2 vẫn không đủ N**: định nghĩa recovery theo breadth cho 49 lệnh / **18 episode**, chỉ nhỉnh hơn bản DT5G-upgrade (77 lệnh / 17 episode). Đổi trục không cứu được — điều kiện "rẻ nhất **và** vừa thoát đáy breadth" bản thân nó hiếm. Và ngay cả ở N đó, IS +10,07pp / OOS −0,92pp đã ngược dấu. Amendment là đúng đắn về mặt thiết kế (nó gỡ trùng lặp với H5) nhưng nó **không** mở ra được cỡ mẫu, và tôi khai nó như trial thứ 7 dù nó không sống.
- **H5 xác nhận đúng trần cấu trúc Phase 0 đã cảnh báo**: 19 episode ở nhánh ≤10 phiên sau upgrade. Theo D3 tôi không kết luận gì; ghi lại con số cho đầy đủ: Δ = +1,06pp, CI [−5,26; +7,65], IS +7,34 / OOS −1,40 ngược dấu, cận khả thi **âm** (−0,59pp). Không có gì để tiếc.

## 6. Quan sát HẬU NGHIỆM — không phải đề cử, phải tiền-đăng ký lại nếu muốn đi tiếp

Tính không đơn điệu ở §4 để lộ một thứ ổn định hơn hẳn mọi thứ trong 7 hypothesis: **không phải TOP tốt, mà BOTTOM xấu.**

| | n | ep | win | exp |
|---|---|---|---|---|
| rank BOTTOM | 129 | 48 | 50,4% | +3,17% |
| tất cả phần trên (TOP+MID) | 789 | 68 | 56,5% | +6,26% |

Δ = **+3,09pp**, CI [−0,64; +6,66], p = 0,10. Quan trọng hơn con số p: **IS +4,45pp / OOS +2,59pp** (cùng dấu, giữ 58% biên độ — suy giảm ôn hoà nhất trong toàn bộ bản đồ), LOO ổn định trong dải rất hẹp **[+2,47; +3,81pp]**, không đổi dấu ở nhánh `+ABANDONED` (+1,63pp, p = 0,087). Cận trên khả thi của động tác "cắt tỷ trọng nhóm đáy, chia lại lên trên": **+0,85pp** nếu cắt 50%, **+1,69pp** nếu cắt hết — và ổn định **IS +1,67 / OOS +1,71**, khác hẳn kiểu lật dấu của H6.

Đã loại được một cách giải thích tầm thường: BOTTOM nạp nặng `rating_8l = 4` (49,2% vs 24,0%), nhưng **chỉ xét trong rating ≤ 3 thì khoảng cách giữ nguyên (+3,11pp)** ⇒ nó không phải cổng rating hiện có đội lốt.

**Ba lý do tôi KHÔNG đề cử nó sang Phase 2 dù số đẹp nhất bảng:**
1. **Nó là hậu nghiệm.** Tôi tìm ra nó *sau khi* nhìn thấy MID ≥ TOP. Đưa nó vào Phase 2 dưới vỏ "H6" là gian lận tiền-đăng ký. Muốn đi tiếp thì phải khai thành trial thứ 8, tiền-đăng ký riêng, và mọi ngưỡng DSR/PBO tính lại theo N_trials = 8.
2. **Con số +1,69pp giả định vốn cắt ra ĐI ĐƯỢC lên trên — chưa chứng minh được từ ledger.** Engine mua từ đầu bảng xuống, nên khi nó chạm tercile đáy thì mọi tên trên đã mua rồi; tiền cắt ra chỉ có thể **tăng tỷ trọng tên đang nắm**, và điều đó bị chặn bởi trần trọng số/tên. Kiểm được từ ledger: sổ nắm tối đa 33 (BAL) / 36 (LAG) vị thế đồng thời và chỉ **2,6–3,8%** lệnh BOTTOM rơi vào lúc sổ gần trần vị thế ⇒ chỗ trống *về số lượng* thì có. Nhưng trần **trọng số/tên** thì ledger không trả lời được — chỉ Phase 2 chạy harness thật mới biết. Nếu trần đó bị chạm, tiền cắt ra nằm im ở tiền mặt (0%/năm theo quy ước chi phí), và toàn bộ +1,69pp bốc hơi. **Đây là ẩn số quyết định, không phải chi tiết kỹ thuật.**
3. **Cắt 100% tercile đáy trên thực tế là đổi bộ chọn tín hiệu**, mà đề cương §7 loại khỏi phạm vi. Chỉ biến thể cắt một phần (50% → +0,85pp) mới đúng là overlay sizing. Biên an toàn so với sàn 0,385pp lúc đó là hơn hai lần — mỏng, và chưa trừ phần rủi ro ở điểm 2.

Một điều nữa cần biết trước khi ai đó phấn khích: tỷ trọng lệnh rơi vào tercile đáy **tăng theo thời gian** (2,7% năm 2014 → ~20% năm 2025-26). Nghĩa là giá trị của việc cắt nhóm này phần lớn đến từ giai đoạn gần đây — không phải chữ ký reshuffle-luck (LOO đã bác), nhưng nó khiến ước lượng phụ thuộc nhiều vào chế độ hiện tại hơn là vào 13 năm mẫu.

## 7. Trả lời thẳng câu hỏi cổng ra

> *"Tối đa 2-3 hypothesis được đề cử sang Phase 2. Nếu KHÔNG cái nào qua, kết luận 'Phase 2 không đáng chạy' là kết quả HỢP LỆ."*

**Đề cử: 0 trên 7.** Phase 2 như đề cương đặc tả (overlay ×k cho một nhóm conviction tiền-đăng ký) **không đáng chạy** — không có nhóm nào vừa đủ N, vừa cùng dấu IS/OOS, vừa đơn điệu theo liều, vừa có cận khả thi OOS vượt sàn nhiễu.

Nếu user/Mike muốn tiêu tiếp một dispatch vào trục này, hình dạng **duy nhất** tôi thấy có cơ sở là câu hỏi hẹp và ngược chiều: *"cắt 50% tỷ trọng tercile đáy có cải thiện NAV không, và vốn cắt ra có thực sự đi được lên trên hay nằm im ở tiền mặt?"* — tiền-đăng ký lại, N_trials = 8, và câu hỏi về trần trọng số ở §6.2 phải là thứ **đo đầu tiên**, không phải thứ khám phá dọc đường. Nếu vốn không đi được, câu trả lời là không và chỉ tốn một lần chạy để biết.

## 8. File

Thư mục `mike/agents/Taylor/research/ccs_phase1_Taylor_20260905_141801/`:

| File | Nội dung |
|---|---|
| `ccs_phase1_expectancy.py` | script chính — 7 contrast × 2 nhánh D1, bootstrap cụm theo episode (B=10.000, seed 20260905), IS/OOS, LOO, H6 phân tầng D5, sàng lọc sống/chết |
| `diag_candidates.py` | chẩn đoán tập trung mã/ngành, capacity %ADV, thời gian nắm giữ, chồng lấn H4∩H6, khả thi tách IS/OOS |
| `trim_variant.py` | định giá quan sát hậu nghiệm §6 (cắt tercile đáy) |
| `ccs_phase1_contrasts_exp.csv` | bảng expectancy đầy đủ, cả hai nhánh D1 |
| `ccs_phase1_perbook_exp.csv` | tách BAL/LAG cho mọi hypothesis (D4) |
| `ccs_phase1_h6_stratified_exp.csv` | H6 theo 4 tầng `sig_n_cands` (D5) |
| `ccs_phase1_survival_exp.csv` | sàng lọc sống/chết + p Bonferroni/BH |
| `ccs_phase1_report_exp.json` · `ccs_phase1_candidate_diag_exp.json` · `ccs_phase1_trim_variant_exp.json` | số thô để tái lập |

Không file canonical nào bị đụng; mọi output mang hậu tố `_exp`. Ledger Phase 0 chỉ được ĐỌC.

## 9. Ghi chú kỹ thuật đáng mang đi

**`r_multiple_vol` thô không dùng thẳng được.** 6/1.012 dòng có `vol60 ≈ 0` (phân vị 0,5% của `vol60` đúng bằng 0), đẩy R xuống tới **−2,8 triệu**; trung bình R của nhóm đối chứng khi đó ra **−4.196**, một con số vô nghĩa mà vẫn hữu hạn nên **không lọt lưới `isfinite`**. Phải winsor [1%, 99%] trước mọi thống kê R. Bẫy chung: `isfinite` bắt được inf, không bắt được "hữu hạn nhưng vô lý" — kiểm phân vị trước khi lấy trung bình bất kỳ đại lượng nào có mẫu số là biến động.

**Ước lượng khả thi phải chặn theo vốn nhóm cấp, không chỉ nhân (k−1) vào nhóm nhận.** Bản đầu của tôi tính `(k−1) × vốn_nhóm_conviction × Δe` và cho H6 ra **+3,04pp** — sai vì với k = 1,5, lượng vốn cần rút vượt cả những gì nhóm đáy thực sự có. Sau khi chặn `moved = min((k−1)·C_treat, C_funding)` **và** đổi phía cấp vốn từ "nhánh đối chứng" sang "toàn bộ phần còn lại trong scope", H6 rơi về +0,73pp và mới lộ ra chuyện lật dấu IS/OOS ở §4. Con số sai lệch gấp 4 lần và nó lệch về phía *ủng hộ* kết luận — đúng hướng nguy hiểm.
