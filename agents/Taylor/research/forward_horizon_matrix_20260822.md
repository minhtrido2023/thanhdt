# A2 — Ma trận FORWARD-HORIZON (DT5G × Value Radar) + hàng PARKING/CAPIT
job Taylor_20260822_131318

**Câu hỏi:** từ mỗi ô (DT5G × Value Radar), forward 60/120/250 phiên hệ ra sao? Parking/CAPIT
tương ứng ra sao?

**Trả lời ngắn:** Ma trận forward của **hệ (COMB) gần như KHÔNG phân biệt được với base rate vô
điều kiện** — COMB fwd-250 median toàn mẫu là **+27,3% (p_pos 92%)**, và ô hiện tại NEUTRAL+RẺ cho
**+26,9%** sau khi loại chồng lấn (n độc lập = **6**). Nói cách khác: `p_pos = 100%` ở gần như mọi
ô **không phải tín hiệu của ô — đó là hệ số nền của một hệ compound 12 năm.** Ngược lại, radar
**có** giữ được thông tin forward trên **thị trường (VNI)** và trên **rổ parking**, nơi vùng ĐẮT
tụt hẳn về ~0%. Kết luận này khớp với luật hiện hành: **Value Radar DISPLAY-ONLY.**

---

## 0. Khác gì ma trận gốc + 3 bẫy phải mang theo

Ma trận gốc (job Taylor_20260822_101400) đo return **ĐỒNG THỜI** trong ô (điều kiện trên *đang ở
trong* ô). A2 đo return **PHÍA TRƯỚC kể từ phiên BƯỚC VÀO** ô — đây mới là dạng câu hỏi dùng được
cho quyết định.

**Bẫy 1 — BASE RATE. Đọc bảng baseline TRƯỚC bảng ma trận, luôn.**

| horizon | COMB med | p_pos | BAL | LAG | PARK | VNI | VNI p_pos |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 60 | **+5,1%** | 77% | +4,2% | +6,0% | +3,3% | +2,7% | 63% |
| 120 | **+12,5%** | 86% | +9,2% | +11,4% | +6,0% | +5,5% | 67% |
| 250 | **+27,3%** | **92%** | +23,7% | +28,5% | +13,7% | +8,5% | 70% |

Mọi con số trong ma trận phải đọc là **CHÊNH LỆCH so với dòng này**, không đọc mức tuyệt đối.

**Bẫy 2 — CHỒNG LẤN nặng.** Cửa sổ 250 phiên của các lần vào ô liên tiếp chồng lên nhau gần như
toàn bộ: NEUTRAL|RẺ có **14/16 cặp kế tiếp cách nhau <250 phiên** (median gap 71 phiên).
`n_entries=18` **không phải** 18 quan sát độc lập.

**Bẫy 3 — zone ≈ kỷ nguyên** (confound đã ghi ở ma trận gốc): ĐẮT≈2017-21, RẺ≈2022-25 ⇒ n hiệu
dụng ~2-3 chu kỳ. A2 không sửa được confound này, chỉ đo thêm một chiều.

**Nguồn:** `panel_daily.csv` (từ pin R3 CANONICAL, self-check 0 VND đã chạy ở job trước) +
`a1_daily.csv` (rổ custom30V PIT, self-check 0 VND ở A1) + `EVENT_CAPIT` lấy từ **chính file pin
R3** (18 lần fire — cùng backtest nên nhất quán, không phải nguồn thứ hai). Không dùng cột
`profit_*`. Forward return = NAV[t₀+h]/NAV[t₀]−1, ô quan sát tại đóng cửa t₀.

---

## 1. Ma trận forward — COMB (median %, p_pos %, p_beat_VNI %)

131 lần bước vào một ô trên 3.107 phiên. `n_full` = số lần có đủ horizon.

| regime | zone | h | n_full | VNI | **COMB** | p_pos | p_beat | BAL | LAG | **PARK** |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **NEUTRAL** | **RẺ** | 60 | 18 | 6,4 | **8,1** | 67 | 83 | 4,7 | 8,5 | 3,5 |
| | | 120 | 17 | 9,5 | **17,7** | 94 | 94 | 11,9 | 21,4 | 12,3 |
| | | 250 | 17 | 17,9 | **33,9** | 100 | 82 | 33,4 | 37,8 | 30,1 |
| NEUTRAL | TRUNGTINH | 60 | 25 | 3,9 | 5,1 | 68 | 72 | 2,3 | 6,8 | 0,4 |
| | | 120 | 21 | 9,0 | 15,9 | 81 | 76 | 11,5 | 18,5 | 9,4 |
| | | 250 | 19 | 23,3 | **46,1** | 100 | 95 | 41,1 | 38,5 | 34,0 |
| NEUTRAL | ĐẮT | 60 | 11 | 2,7 | 5,5 | 73 | 64 | 3,6 | 4,6 | 2,8 |
| | | 120 | 9 | 5,2 | 19,8 | 89 | 89 | 13,6 | 19,8 | 7,1 |
| | | 250 | 9 | **−0,7** | 26,9 | 100 | 89 | 22,5 | 30,9 | **−2,9** |
| NEUTRAL | *ALL* | 250 | 45 | 17,6 | 33,9 | 100 | 89 | 33,4 | 35,7 | 24,4 |
| CRISIS | RẺ | 250 | 12 | 10,9 | **36,9** | 75 | 92 | 23,4 | 37,0 | 29,1 |
| CRISIS | TRUNGTINH | 250 | 16 | 19,1 | 26,4 | 81 | 100 | 21,2 | 30,2 | 16,6 |
| CRISIS | ĐẮT | 250 | 10 | 18,5 | 23,4 | 90 | 90 | 21,8 | 27,1 | 13,8 |
| CRISIS | *ALL* | 60 | 38 | −0,1 | **−1,8** | 45 | 42 | 0,2 | −4,7 | −3,5 |
| BEAR | *ALL* | 250 | 11 | 8,0 | 22,7 | 91 | 91 | 28,7 | 25,0 | 13,9 |
| BULL | ĐẮT | 250 | 8 | **−2,4** | 32,8 | 100 | 100 | 36,4 | 38,2 | **−1,5** |
| BULL | *ALL* | 250 | 22 | 4,3 | 29,5 | 100 | 100 | 25,8 | 35,1 | 10,9 |
| EXBULL | *ALL* | 250 | 3 | 36,9 | 102,2 | 100 | 100 | 107,4 | 101,1 | 89,3 |

Ma trận đầy đủ (mọi ô × 3 horizon × 5 chuỗi): **`forward_matrix.csv`**.

**Ba điều đọc được:**
1. **CRISIS h=60 là ô duy nhất âm** (COMB −1,8%, p_pos 45%, p_beat 42%) — vào CRISIS thì 3 tháng
   đầu vẫn đau, đến h=250 mới lật (+26,3%, p_beat 95%). Đây là chữ ký "vào sớm" của một hệ
   phòng thủ, không phải lỗi.
2. **PARK là chuỗi DUY NHẤT bị vùng ĐẮT đánh gục**: NEUTRAL|ĐẮT −2,9%, BULL|ĐẮT −1,5% ở h=250,
   trong khi COMB cùng ô vẫn +26,9%/+32,8%. Hệ trung hoà được radar; rổ parking thì không.
3. **EXBULL n=3-4** — liệt kê cho đủ, **không đọc như kết quả**.

---

## 2. Ô hiện tại NEUTRAL+RẺ — phân phối, không chỉ median

| zone | h | strat | n | p0 | p10 | p25 | **p50** | p75 | p90 | p100 | mean | p_pos |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **RẺ** | 60 | COMB | 18 | −10,1 | −2,1 | −0,8 | **8,1** | 12,7 | 27,0 | 29,3 | 8,8 | 67 |
| | 120 | COMB | 17 | −9,9 | 2,8 | 11,1 | **17,7** | 26,2 | 39,0 | 52,0 | 19,1 | 94 |
| | 250 | COMB | 17 | **+9,0** | 12,6 | 24,7 | **33,9** | 55,6 | 74,5 | 98,6 | 41,6 | **100** |
| | 250 | VNI | 17 | −3,3 | 8,8 | 14,4 | 17,9 | 41,2 | 53,6 | 62,1 | 27,4 | 94 |
| | 250 | PARK | 17 | +3,8 | 4,3 | 8,9 | 30,1 | 45,7 | 93,8 | 165,9 | 40,4 | 100 |
| TRUNGTINH | 250 | COMB | 19 | +17,2 | 18,3 | 27,2 | **46,1** | 56,9 | 84,6 | 97,5 | 46,6 | 100 |
| ĐẮT | 250 | COMB | 9 | +3,2 | 6,7 | 16,0 | **26,9** | 37,0 | 61,1 | 83,0 | 31,6 | 100 |
| ĐẮT | 250 | VNI | 9 | −11,6 | −8,7 | −7,1 | **−0,7** | 14,7 | 32,8 | 49,1 | 6,5 | **44** |
| ĐẮT | 250 | PARK | 9 | −17,1 | −9,6 | −5,5 | **−2,9** | 10,2 | 54,0 | 70,1 | 10,7 | **44** |

Histogram COMB fwd-250 trong NEUTRAL:
```
RE         n=17   0..10:2  10..20:1  20..40:7  40..80:5  >80:2
TRUNGTINH  n=19            10..20:3  20..40:6  40..80:7  >80:3
DAT        n= 9   0..10:2  10..20:1  20..40:4  40..80:1  >80:1
```

**Đuôi trái của COMB ở h=250 là +9,0% (RẺ), +17,2% (TRUNGTINH), +3,2% (ĐẮT)** — tức trong mẫu này
KHÔNG có lần nào hệ lỗ sau 250 phiên kể từ bất kỳ điểm vào NEUTRAL nào. Đó là dấu hiệu mẫu quá
thuận (12 năm bull ròng), **không phải bằng chứng hệ không thể lỗ**. Đừng dùng con số này làm
kỳ vọng downside — bootstrap 5th-pct của V2.4 vẫn là DD ~−29% (KNOWLEDGE.md).

---

## 3. De-overlap: N độc lập thật, và radar có value gì không

Greedy: giữ 1 entry, bỏ mọi entry cách nó <h phiên.

| zone | h | n_all | **n_indep** | COMB (all) | **COMB (indep)** | VNI (indep) | PARK (indep) |
|---|---:|---:|---:|---:|---:|---:|---:|
| RẺ | 60 | 18 | 12 | 8,1 | **8,2** | 8,8 | 6,5 |
| RẺ | 120 | 17 | 8 | 17,7 | **17,2** | 9,2 | 9,3 |
| **RẺ** | **250** | 17 | **6** | 33,9 | **26,9** | 16,1 | 19,8 |
| TRUNGTINH | 60 | 25 | 13 | 5,1 | **0,4** | 3,5 | 0,4 |
| TRUNGTINH | 120 | 21 | 8 | 15,9 | **10,6** | 5,8 | −4,8 |
| TRUNGTINH | 250 | 19 | **5** | 46,1 | **33,9** | 9,7 | 20,1 |
| ĐẮT | 60 | 11 | 9 | 5,5 | **5,5** | 2,7 | 2,8 |
| ĐẮT | 120 | 9 | 6 | 19,8 | **16,8** | 5,9 | 4,5 |
| ĐẮT | 250 | 9 | **4** | 26,9 | **23,3** | 3,3 | 6,3 |

### Đây là kết quả chính của A2

**So với baseline vô điều kiện (COMB fwd-250 = +27,3%):**

| | COMB indep | Δ vs baseline | VNI indep | Δ vs baseline (8,5) | PARK indep | Δ vs baseline (13,7) |
|---|---:|---:|---:|---:|---:|---:|
| NEUTRAL+RẺ | 26,9 (n=6) | **−0,4pp** | 16,1 | **+7,6pp** | 19,8 | +6,1pp |
| NEUTRAL+TRUNGTINH | 33,9 (n=5) | +6,6pp | 9,7 | +1,2pp | 20,1 | +6,4pp |
| NEUTRAL+ĐẮT | 23,3 (n=4) | −4,0pp | 3,3 | **−5,2pp** | 6,3 | **−7,4pp** |

1. **Với HỆ (COMB): radar không cho thông tin forward dùng được.** Chênh lệch RẺ−ĐẮT sau
   de-overlap là +3,6pp trên n=6 vs n=4, và ô RẺ còn thấp hơn base rate 0,4pp. Thứ tự cũng không
   đơn điệu (TRUNGTINH cao nhất). Với n≤6 độc lập, đây là nhiễu.
2. **Với THỊ TRƯỜNG (VNI) và ROI PARKING: radar CÓ tách được**, và tách đúng chiều đơn điệu —
   VNI: RẺ 16,1 > TRUNGTINH 9,7 > ĐẮT 3,3; PARK: RẺ 19,8 ≈ TRUNGTINH 20,1 ≫ ĐẮT 6,3. Vùng ĐẮT
   là vùng duy nhất cả VNI lẫn PARK tụt dưới base rate rõ rệt.
3. **Hàm ý cơ chế:** V2.4 **hấp thụ** thông tin định giá vĩ mô mà radar mang — nhờ DT5G cap +
   allocator + chọn mã theo yieldcombo. Cái radar nói thêm cho *thị trường* thì hệ đã tính vào
   rồi. **Đây là lập luận ỦNG HỘ giữ Value Radar ở trạng thái DISPLAY-ONLY**, không phải lập luận
   để wire nó vào sizing.
4. Nhất quán với §C.5 `market_regime_probability_20260729.md` (hiệu RẺ−ĐẮT p=0,049 thô, chưa qua
   BH/Bonferroni, đầu RẺ không đơn điệu) — A2 tái xác nhận bằng một góc đo khác (forward thay vì
   đồng thời).

---

## 4. CAPIT theo ô — 18 lần fire (LIỆT KÊ, không p-value)

| ngày | size | regime | zone | COMB60 | COMB120 | COMB250 | VNI60 | VNI120 | VNI250 |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|
| 2014-05-08 | 1,000 | CRISIS | TRUNGTINH | 17,9 | 33,7 | 47,9 | 13,1 | 10,2 | 3,0 |
| 2015-05-18 | 0,750 | NEUTRAL | RẺ | 24,8 | 27,7 | 43,0 | 16,2 | 15,6 | 16,4 |
| 2015-08-24 | 0,375 | NEUTRAL | RẺ | 14,1 | 10,5 | 30,3 | 14,8 | 3,8 | 24,8 |
| 2016-01-18 | 0,750 | NEUTRAL | RẺ | 15,4 | 25,3 | 22,1 | 8,0 | 26,7 | 28,8 |
| 2018-05-28 | 1,000 | CRISIS | ĐẮT | 17,2 | 21,5 | 31,4 | 4,1 | −2,6 | 4,3 |
| 2018-07-05 | 0,375 | NEUTRAL | ĐẮT | 38,1 | 31,2 | 40,0 | 13,1 | 1,4 | 7,4 |
| 2020-02-03 | 0,750 | NEUTRAL | TRUNGTINH | −2,9 | −6,0 | 33,8 | −17,3 | −7,7 | 25,6 |
| 2020-03-11 | 0,250 | BEAR | TRUNGTINH | 2,1 | 0,6 | 58,0 | 10,9 | 8,7 | 44,2 |
| 2020-07-27 | 0,375 | NEUTRAL | RẺ | 28,0 | 51,6 | **98,6** | 20,3 | 51,1 | 62,1 |
| **2022-04-19** | **0,000** | CRISIS | TRUNGTINH | 0,4 | −2,5 | **−7,9** | −15,9 | −25,9 | −25,0 |
| 2022-06-15 | 0,250 | BEAR | RẺ | 1,6 | −7,4 | **−3,9** | 2,9 | −11,0 | −8,0 |
| **2022-09-28** | **0,000** | BEAR | RẺ | −4,4 | −4,4 | 14,7 | −10,9 | −8,6 | 0,8 |
| 2023-10-30 | 1,000 | CRISIS | RẺ | 16,9 | 16,2 | 33,3 | 13,0 | 15,7 | 20,7 |
| 2024-04-17 | 0,500 | BULL | RẺ | 14,5 | 18,8 | 31,9 | 7,4 | 7,8 | 1,2 |
| 2024-08-05 | 0,500 | CRISIS | RẺ | 3,9 | 7,9 | 58,9 | 5,9 | 6,0 | 32,5 |
| 2025-04-03 | 0,500 | BULL | RẺ | 20,2 | 45,3 | 40,0 | 12,6 | 35,0 | 36,4 |
| 2025-10-20 | 0,750 | NEUTRAL | TRUNGTINH | 6,3 | 1,3 | — | 15,8 | 10,0 | — |
| 2026-03-09 | 0,750 | NEUTRAL | TRUNGTINH | −3,2 | — | — | 10,8 | — | — |

⚠️ **2 dòng size = 0,000** (2022-04-19, 2022-09-28) là **đánh giá gate ra size bằng 0, KHÔNG phải
lần fire thật** ⇒ số lần fire thật = **16**. Cả hai đều rơi vào 2022, và đó cũng là 2 trong 3 cửa
sổ forward âm — **gate đã đúng khi từ chối cấp size**, chi tiết dễ bị bỏ sót nếu chỉ đọc cột ngày.

**Gộp theo ô** (mọi ô n ≤ 4 ⇒ chỉ liệt kê):

| ô | n | fwd60 COMB/VNI | fwd120 | fwd250 |
|---|---:|---|---|---|
| NEUTRAL\|RẺ | 4 | +20,1 / +15,5 | +26,5 / +21,2 | +36,6 / +26,8 |
| NEUTRAL\|TRUNGTINH | 3 | −2,9 / +10,8 | −2,4 / +1,2 | +33,8 / +25,6 |
| CRISIS\|RẺ | 2 | +10,4 / +9,4 | +12,1 / +10,8 | +46,1 / +26,6 |
| CRISIS\|TRUNGTINH | 2 | +9,2 / −1,4 | +15,6 / −7,8 | +20,0 / −11,0 |
| BULL\|RẺ | 2 | +17,4 / +10,0 | +32,1 / +21,4 | +36,0 / +18,8 |
| BEAR\|RẺ | 2 | −1,4 / −4,0 | −5,9 / −9,8 | +5,4 / −3,6 |
| CRISIS\|ĐẮT · NEUTRAL\|ĐẮT · BEAR\|TRUNGTINH | 1 mỗi ô | — | — | — |

**Không tính p-value cho bất kỳ ô CAPIT nào** (n≤4, cửa sổ chồng lấn, và CAPIT không phải một
chuỗi return tách rời — nó là sự kiện *sizing* bên trong COMB; cái đo được là "hệ đi thế nào SAU
khi CAPIT fire", không phải "CAPIT lãi bao nhiêu").

---

## 5. Kết luận

1. **Ma trận forward của hệ bị BASE RATE chi phối.** `p_pos = 100%` ở gần mọi ô 250 phiên là hệ
   số nền (+27,3%, 92%), không phải tín hiệu. Bảng baseline phải đi kèm mọi lần trích dẫn ma trận
   forward — nếu không, mọi ô đều "trông tuyệt vời".
2. **Ô hiện tại NEUTRAL+RẺ: +26,9% fwd-250 sau de-overlap (n=6) ≈ base rate (+27,3%).** Không có
   lợi thế forward đo được so với việc đơn giản là đang ở trong hệ. Ở h=120 có nhỉnh hơn
   (+17,2% vs +12,5%) nhưng n=8.
3. **Radar KHÔNG thêm thông tin forward cho HỆ, nhưng CÓ cho THỊ TRƯỜNG và ROI PARKING** — vùng
   ĐẮT kéo VNI về +3,3% và PARK về +6,3% (baseline 8,5/13,7). Đây là bằng chứng ủng hộ **giữ
   DISPLAY-ONLY**, và trùng hướng với kết quả A1 (parking phụ thuộc bối cảnh, không phải hằng số).
4. **CRISIS h=60 âm, h=250 dương mạnh** — nếu có một hàm ý vận hành nào từ A2 thì là ở đây: đừng
   đánh giá một lần vào CRISIS bằng cửa sổ 3 tháng.
5. **Không đề xuất thay đổi production nào từ A2.** N độc lập 4-6 episode/ô là quá mỏng để wire
   bất cứ thứ gì; mọi thay đổi phải qua quant-skeptic CONFIRMED (§18).

**Artifacts:** `forward_matrix.csv` (ma trận đầy đủ) · `a2_entries.csv` (131 lần vào ô × 3 horizon
× 5 chuỗi) · `a2_baseline.csv` · `a2_nonoverlap.csv` · `a2_neutral_distribution.csv` ·
`a2_capit_events.csv` · `a2.log` · script `strategy_regime_matrix_20260822_a2.py`.
