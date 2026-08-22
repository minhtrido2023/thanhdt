# B2-ext — "Alpha sau khử beta của V2.4 có phụ thuộc breadth-tercile không?"

**Job**: `Taylor_20260822_153901` · **Ngày**: 2026-08-22 · **PAPER-ONLY, không đề xuất wire**
**Prereg**: [`b2_alpha_breadth_prereg_20260822.md`](b2_alpha_breadth_prereg_20260822.md) (viết TRƯỚC khi chạy)
**Script**: `strategy_regime_matrix_20260822_b2ext.py` · **Log**: `strategy_regime_matrix_20260822/b2ext.log`

---

## VERDICT: **REFUTE** — H1 bị bác bỏ

Không có bằng chứng rằng beta-adjusted alpha của V2.4 phụ thuộc breadth-tercile theo hướng đã
prereg. **3/4 tiêu chí CONFIRM trượt**, và 2 trong số đó là điều kiện REFUTE tự động:

| Tiêu chí prereg §5 (COMB) | Kết quả | |
|---|---|---|
| (a) Δ_HIGH−LOW > 5pp/năm | **+3,7pp** | ✗ |
| (b) p<0,05 một đuôi **và** qua BH FDR 10% | **p = 0,349**, BH10 fail | ✗ (p>0,10 ⇒ REFUTE tự động) |
| (c) LOO > 75% năm dương | 100% | ✓ (nhưng xem §5 — đây là niềm tin giả) |
| (d) OOS cùng dấu IS | **IS −7,8% / OOS +13,4%** | ✗ (đổi dấu ⇒ REFUTE tự động) |

**0/9 test chính qua BH FDR 10%.** 2 test có p thô <0,05 (`BAL HIGH−MID` p=0,043;
`COMB HIGH−MID` p=0,043) — nhưng cả hai đều **không phải cặp trong H1**, và cả hai đều fail BH.

**Selfcheck bắt buộc PASS**: COMB full-sample CAGR = **28,86%**, NAV cuối từ 50B = **1.178,01B** —
khớp pin R3 lệch **0,003pp** (ngưỡng 0,1pp).

---

## 1. Kết quả chính — bảng alpha theo tercile

Mẫu hiệu dụng **2015-01-12 → 2026-06-19, n=2.855 phiên, 12 năm** (mất 252 phiên warm-up beta).
Alpha = `mean(r_strat_t − beta_{t-1}·r_vni_t) × 249,28`; nhãn tercile = `btile_{t-1}` (PIT, trễ 1 phiên).

| tercile | phiên | ep | breadth TB | **BAL alpha** | **LAG alpha** | **COMB alpha** | beta COMB | VNI (a.r.) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LOW | 1.160 | 49 | 39,0% | +19,4% | +22,6% | **+20,9%** | 0,53 | +3,7% |
| MID | 802 | 97 | 58,5% | +9,6% | +9,0% | **+9,3%** | 0,55 | +19,6% |
| HIGH | 893 | 49 | 67,7% | +28,6% | +21,5% | **+24,6%** | 0,46 | +15,4% |

### Phát hiện làm hỏng chính hypothesis: quan hệ là **CHỮ U**, không phải gradient

H1 giả định đơn điệu tăng (LOW < MID < HIGH). Thực tế **cả 3 chiến lược đều có MID THẤP NHẤT** —
LOW và HIGH cùng cao, MID sụt. Đây không phải "breadth cao thì alpha cao", mà là "breadth ở giữa
thì alpha thấp" — một hình dạng **không có cơ chế nào trong prereg dự đoán**, và cũng không có câu
chuyện kinh tế nào sẵn (thị trường "nửa khoẻ" không phải một chế độ có nghĩa).

Đúng dạng hình chữ U này là lý do 2 test p<0,05 duy nhất đều là `HIGH−MID`: chúng đo cạnh phải
của chữ U, không đo gradient. Diễn giải chúng là bằng chứng cho H1 sẽ là **HARKing**.

---

## 2. Nguồn gốc con số +11,8pp của B2 — 83% là same-day contamination

Tách từng bước từ phương pháp B2 sang thiết kế prereg (cùng mẫu hiệu dụng 2015+):

| Bước | LOW | MID | HIGH | **HIGH−LOW** |
|---|---:|---:|---:|---:|
| B2 nguyên bản (alpha hình học từ CAGR + nhãn **cùng phiên**) | +15,0% | +14,1% | +28,9% | **+13,8pp** |
| → đổi sang nhãn **trễ 1 phiên** (giữ nguyên mọi thứ khác) | +24,5% | +8,7% | +26,9% | **+2,4pp** |
| → đổi tiếp sang alpha **số học ngày** | +21,9% | +8,0% | +22,5% | **+0,6pp** |
| BASE prereg (rolling beta_{t-1}, alpha ngày) | +20,9% | +9,3% | +24,6% | **+3,7pp** |

**Một dòng duy nhất — trễ nhãn 1 phiên — xoá 11,4/13,8 = 83% hiệu ứng.**

Cơ chế: `breadth_t` tính từ `Close_t`, cùng phiên với `r_vni_t`. B2 tự đo
`corr(breadth_t, r_vni_t) = +0,109`. Nhãn "HIGH breadth hôm nay" một phần chính là nhãn "hôm nay
VNINDEX xanh" ⇒ danh mục beta-dương tự động trông tốt hơn ở HIGH. Sau khi trễ 1 phiên, tương quan
này rơi từ **+0,109 → +0,014** và hiệu ứng biến mất cùng nó.

Phần dư (2,4 → 0,6pp) đến từ chênh lệch **hình học vs số học**: LOW là vùng vol cao, CAGR gộp
phạt vol nặng hơn mean ngày — nên đo bằng CAGR đẩy LOW xuống một cách giả tạo.

> **Lưu ý số**: B2 báo LOW +16,3 / MID +20,2 / HIGH +28,1 (Δ=+11,8pp) trên toàn panel 2014+;
> tái tạo ở đây cho +15,0 / +14,1 / +28,9 (Δ=+13,8pp) vì mẫu bắt đầu 2015 (warm-up beta). Khác
> biệt mẫu, cùng kết luận.

---

## 3. Conditional on DT5G — dấu ĐẢO NGƯỢC, phần dương còn lại là composition

Breadth **không** phải alias của regime: `corr(breadth_{t-1}, DT5G ordinal)` Spearman **+0,398**
(< 0,5, ngưỡng prereg). Nhưng phân bố lệch mạnh:

| DT5G | n | LOW | MID | HIGH |
|---|---:|---:|---:|---:|
| CRISIS | 443 | 57,8% | 35,0% | 7,2% |
| BEAR | 241 | 63,1% | 18,3% | 18,7% |
| NEUTRAL | 1.689 | 37,7% | 25,8% | 36,5% |
| BULL | 422 | 27,3% | 39,6% | 33,2% |
| EXBULL | 60 | 0,0% | 0,0% | **100,0%** |

Trong **cùng một** DT5G state, Δ_HIGH−LOW của COMB **đổi dấu**:

| state | n_HIGH | n_LOW | alpha HIGH | alpha LOW | **Δ** | p |
|---|---:|---:|---:|---:|---:|---:|
| NEUTRAL | 616 | 637 | +19,8% | +26,6% | **−6,8pp** | 0,711 |
| BULL | 140 | 115 | +41,2% | +43,6% | **−2,4pp** | 0,541 |
| CRISIS / BEAR / EXBULL | — | — | — | — | mẫu quá nhỏ | — |

⇒ **+3,7pp ở mức tổng là hiệu ứng cấu thành (Simpson), không phải hiệu ứng breadth.** Tercile HIGH
gánh 100% EXBULL và tỷ trọng BULL cao — những state alpha vốn đã cao — trong khi tercile LOW gánh
phần lớn CRISIS/BEAR. Bỏ kênh cấu thành đi, dấu quay về âm ở cả 2 state đủ mẫu.

---

## 4. Robustness — không biến thể nào cứu được kết luận

Δ alpha COMB (HIGH−LOW):

| Biến thể | Δ | p (1 đuôi) |
|---|---:|---:|
| **BASE (prereg)** | +3,7pp | 0,349 |
| beta toàn mẫu (look-ahead, β=0,489) | +2,7pp | 0,388 |
| beta riêng theo tercile (đúng cách B2: 0,42/0,57/0,61) | **+0,6pp** | 0,475 |
| rolling beta cửa sổ 126 phiên | +2,9pp | 0,383 |
| rolling beta cửa sổ 504 phiên | +1,8pp | 0,431 |
| tercile toàn mẫu (**non-PIT, có look-ahead**) | +17,3pp | 0,053 |
| tercile **cùng phiên** (như B2) | +9,9pp | 0,146 |
| excess THÔ (không khử beta) | **−3,3pp** | 0,610 |

Hai biến thể duy nhất cho Δ lớn (+17,3 và +9,9) đều là **hai biến thể có look-ahead** — non-PIT
tercile và nhãn cùng phiên. Đó chính là chữ ký của artefact, không phải của tín hiệu: hiệu ứng chỉ
sống khi được phép nhìn trước.

Kết luận về phương pháp beta: **không nhạy cảm**. Bốn cách ước lượng beta khác nhau (rolling
126/252/504, toàn mẫu, theo tercile) đều cho Δ trong khoảng +0,6 đến +3,7pp, không cách nào
p<0,10.

### Phân rã tỷ trọng đầu tư — vì sao excess thô và alpha nói ngược nhau

| tercile | inv_BAL | inv_LAG | r_COMB (a.r.) | r_VNI (a.r.) | excess thô | alpha |
|---|---:|---:|---:|---:|---:|---:|
| LOW | 56,9% | 67,8% | +23,5% | +3,7% | **+19,8pp** | +20,9% |
| MID | 66,4% | 63,2% | +19,3% | +19,6% | −0,4pp | +9,3% |
| HIGH | 75,8% | 69,6% | +31,9% | +15,4% | +16,5pp | +24,6% |

Cơ chế B2 mô tả là ĐÚNG về chất ở phần "hệ đầu tư nhẹ hơn": ở LOW breadth tỷ trọng cổ phiếu của
sổ BAL chỉ 56,9% so với 75,8% ở HIGH, và VNINDEX ở LOW gần như đứng yên (+3,7%/năm) nên excess thô
phồng lên mà không cần alpha nào. (Phần "beta thấp hơn" thì KHÔNG đúng theo rolling beta PIT: beta
LOW = 0,53 > beta HIGH = 0,46 — chỉ beta OLS trong-ô mới cho thứ tự ngược lại; xem §8 caveat.) Nhưng sau khi trễ nhãn đúng cách, **excess thô
LOW−HIGH chỉ còn +3,3pp** (không phải khoảng cách lớn B2 thấy), và alpha thì không phân biệt được
với nhau. Cả hai mặt của câu chuyện B2 đều teo lại cùng lúc.

---

## 5. Vì sao LOO 100% dương KHÔNG phải bằng chứng ủng hộ

Đây là điểm dễ đọc nhầm nhất trong báo cáo này, nên nói rõ:

- LOO bỏ **1 năm trên 12** ⇒ mỗi replicate vẫn giữ ~92% mẫu. Với một hiệu ứng nhỏ và ổn định về
  mặt số học (+3,7pp), LOO gần như **không thể** đổi dấu — nó đo độ nhạy với outlier năm, không đo
  tính khái quát hoá.
- Split IS/OOS là test sắc hơn cho cùng câu hỏi, và nó **đổi dấu ở cả 3 chiến lược**:
  BAL −6,6% → +22,6%; LAG −7,8% → +4,6%; COMB −7,8% → +13,4%.
- Hai kết quả không mâu thuẫn: toàn bộ Δ dương nằm ở nửa OOS 2020+ (đúng cửa sổ có COVID crash +
  bull 2021 + bear 2022), nửa IS 2015-2019 cho dấu ÂM. LOO chỉ đang phản ánh rằng nửa OOS đủ nặng
  để kéo tổng thể dương dù bỏ bất kỳ năm đơn lẻ nào.

**Bài học chung để ghi sổ**: khi n_năm nhỏ (≤15), LOO-theo-năm và walk-forward split KHÔNG thay
thế được nhau. LOO qua mà split trượt ⇒ tin split.

---

## 6. Kết luận & ghi sổ

**Ghi sổ đúng như dispatch quy định cho nhánh REFUTE**: *"excess sau khử beta là artefact của
interval chọn"* — cụ thể hoá được thành 3 câu có số:

1. **83% hiệu ứng B2 là same-day contamination** của nhãn breadth (`corr` +0,109 → +0,014 sau khi
   trễ 1 phiên; Δ +13,8pp → +2,4pp).
2. **Phần còn lại là composition theo DT5G state**, không phải breadth: conditional-on-state cho
   Δ ÂM ở cả NEUTRAL (−6,8pp) và BULL (−2,4pp).
3. **Quan hệ không đơn điệu** (chữ U, MID thấp nhất ở cả 3 chiến lược) ⇒ ngay cả nếu có ý nghĩa
   thống kê, nó cũng không phải hình dạng mà bất kỳ cơ chế sizing nào khai thác được.

**Hệ quả với hướng nghiên cứu**: **ĐÓNG** hướng "tăng allocation/sizing khi HIGH breadth". Không
prereg tiếp. Kết quả này nhất quán với B2 (0/27 ô qua BH FDR 10% trên excess thô) và với chuỗi
B1/B2/B3 hôm nay — không hướng nào trong nhóm "gắn thêm một trục điều kiện vào hệ" tạo ra edge đo
được.

**KHÔNG đề xuất wire.** Không có gì để đưa qua quant-skeptic vì không có claim dương nào.

---

## 7. SAI LỆCH SO VỚI PREREG

**Không có sai lệch về thiết kế, tiêu chí, hay hướng test.** Ba bổ sung, tất cả đều là phân tích
THÊM sau khi verdict đã xác định, không dùng để đổi verdict:

1. **§11 Attribution** (bảng ở §2 báo cáo này): tách +13,8pp của B2 thành từng bước. Không có
   trong prereg; thêm vì verdict REFUTE đòi giải thích *tại sao* B2 thấy hiệu ứng.
2. **Robustness cửa sổ beta 126/504 phiên**: prereg §7.2 chỉ nêu "beta toàn mẫu" và "beta theo
   tercile"; thêm 2 cửa sổ rolling để chứng minh kết luận không nhạy với lựa chọn cửa sổ.
3. **Kiểm tra hình dạng đơn điệu** (chữ U): prereg giả định gradient nhưng không viết test hình
   dạng tường minh. Ghi lại vì nó vô hiệu hoá cách diễn giải 2 p-value `HIGH−MID` <0,05.

Tiêu chí CONFIRM/REFUTE giữ **nguyên văn** như prereg §5; verdict tính bằng code
(`[VERDICT_MACHINE] REFUTE diff=0.037063 p=0.349400 loo_pos=1.0000 is=-0.077792 oos=0.134226`).

## 8. Caveat

- Backtest **gross**: chưa trừ phí/slippage/thuế (quy đổi thực tế CAGR ≈ backtest − 1,5%). Hiệu
  giữa 2 tercile ít nhạy hơn mức tuyệt đối nhưng không bằng 0.
- Alpha ở đây **mô tả**, không phải tín hiệu giao dịch.
- `beta_COMB` trung bình theo rolling (LOW 0,53 / MID 0,55 / HIGH 0,46) khác beta OLS trong-ô
  (0,42/0,57/0,61) vì rolling beta ước lượng trên cửa sổ 252 phiên **bắc qua nhiều tercile**. Đây
  là hạn chế đã biết của thiết kế PIT: beta_{t-1} là beta *pha trộn*, không phải beta điều kiện của
  tercile. Cả hai cách đều đã chạy (§4) và cho cùng kết luận, nên hạn chế này không đổi verdict.
- Mẫu hiệu dụng mất 252 phiên đầu (2014) do warm-up beta ⇒ IS chỉ còn 2015-2019.

## 9. Artifact

| File | Nội dung |
|---|---|
| `b2_alpha_breadth_prereg_20260822.md` | prereg (viết trước) |
| `strategy_regime_matrix_20260822_b2ext.py` | script |
| `strategy_regime_matrix_20260822/b2ext.log` | log chạy đầy đủ |
| `strategy_regime_matrix_20260822/b2ext_alpha_tercile.csv` | **kết quả chính** — alpha/beta/return theo tercile |
| `strategy_regime_matrix_20260822/b2ext_tests.csv` | 9 test chính + BH FDR |
| `strategy_regime_matrix_20260822/b2ext_walkforward.csv` | IS/OOS |
| `strategy_regime_matrix_20260822/b2ext_loo.csv` | LOO theo năm |
| `strategy_regime_matrix_20260822/b2ext_conditional.csv` | conditional-on-DT5G |
| `strategy_regime_matrix_20260822/b2ext_robustness.csv` | 8 biến thể robustness |
| `strategy_regime_matrix_20260822/b2ext_attribution.csv` | tách +13,8pp → +0,6pp |
