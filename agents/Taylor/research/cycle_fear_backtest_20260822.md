# KẾT QUẢ — backtest nhóm (b) chu kỳ + case sơ bộ (c)/(d), khung "sợ hãi có tính toán"

> Taylor, job `Taylor_20260822_022947`, 2026-08-22. PREREG: `cycle_fear_prereg_20260822.md`,
> **commit `4e36d170` TRƯỚC mọi truy vấn outcome**. Script tái lập: `out/cycle_fear_calc.py`,
> dữ liệu thô `out/cycle_fear_px.csv`, kết quả `out/cycle_fear_results.json`.
> **KHÔNG wire production. Không có khuyến nghị mua/bán nào phát sinh từ file này.**

## 0. VERDICT — **NO-GO**

| Giả thuyết | Ngưỡng prereg | Đo được | Phán quyết |
|---|---|---|---|
| **H1** median trough+12M BHAR > 0% ∧ N ≥ 5 | >0%, N≥5 | **+108,3pp**, N_tickers=14 | ✅ **ĐẠT** |
| **H2** discriminator §2.5 phân biệt được | median(PASS) − median(FAIL) **≥ +20pp** ở BHAR_12M | **−17,0pp** (PASS 102,5 < FAIL 119,5) | ❌ **BÁC BỎ** |
| **GO** = H1 ∧ H2 trên ≥3 ngành | — | H2 trượt | ❌ **NO-GO** |

**Đọc một câu:** trong đáy chu kỳ 2022Q4, **mọi thứ đã rơi đều nảy** — bộ tiêu chí §2.5 KHÔNG tách
được người thắng khỏi kẻ thua ở chân trời 12 tháng. H1 đạt nhưng **vô nghĩa về mặt thông tin**: nó
đạt cả trên nhóm negative control mà tôi đã chỉ định trước là "sẽ thua".

**Bằng chứng sắc nhất cho việc H2 bị bác bỏ:** 2 negative control **HSG (+178,1pp)** và
**NKG (+166,8pp)** — chỉ định trước là "tôn/thép thương mại biên mỏng, KHÔNG phải leader chi phí
thấp, sẽ thua" — **đánh bại HPG (+102,5pp)**, chính là case chuẩn của khung. Dự đoán ex-ante ở
prereg §4 viết ra để có thể sai, và **nó đã sai đúng chiều ngược lại**.

---

## 1. Bảng kết quả đầy đủ

DD_250d = sụt từ đỉnh 250 phiên trước đáy. BHAR = vượt VNINDEX, điểm phần trăm. **T0** = neo tại đáy
(ex-post, CẬN TRÊN không thực thi được); **T20** = neo tại đáy+20 phiên (gần thực tế hơn).

### Nhóm (b) — chu kỳ/hàng hoá

| Mã | Ngành | Đáy | Close | DD_250d | PB | Debt_Eq | Phân loại §2.5 | T0_b6 | **T0_b12** | T0_b24 | T20_b12 | T20_b24 |
|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| HPG | Thép | 2022-11-10 | 8.180 | −71,1% | 0,72 | 0,87 | **PASS** | +67,5 | **+102,5** | +113,1 | +39,5 | +39,8 |
| HSG | Thép | 2022-11-15 | 5.190 | −79,8% | 0,40 | 0,56 | FAIL (#3) ⚠️neg-ctrl | +99,5 | **+178,1** | +130,9 | +64,6 | +32,5 |
| NKG | Thép | 2022-11-15 | 5.240 | −82,2% | 0,34 | 1,77 | FAIL (#3) ⚠️neg-ctrl | +85,8 | **+166,8** | +124,6 | +68,2 | +25,6 |
| SSI | Chứng khoán | 2022-11-10 | 7.410 | −72,5% | 0,93 | 1,05 | **PASS** ¹ | +50,2 | **+114,1** | +117,8 | +57,8 | +49,8 |
| VCI | Chứng khoán | 2022-11-15 | 9.280 | −71,0% | 1,17 | 1,38 | FAIL (#3,#4) | +74,5 | **+119,5** | +116,9 | +55,5 | +57,0 |
| HCM | Chứng khoán | 2022-11-15 | 6.450 | −68,3% | 0,88 | 1,59 | FAIL (#3) | +53,2 | **+75,8** | +134,4 | +38,5 | +85,6 |
| DIG | BĐS | 2022-11-15 | 8.740 | −89,7% | 0,82 | 1,10 | FAIL (#3) | +83,1 | **+122,9** | +64,4 | +33,5 | −9,1 |
| PDR | BĐS | 2023-02-28 | 8.440 | −85,4% | 0,73 | 1,47 | FAIL (#2,#3) | +105,6 | **+161,9** | +90,9 | +135,5 | +46,7 |
| NVL | BĐS | 2023-03-01 | 9.530 | −88,3% | 0,44 | **4,73** | FAIL (#1,#2,#3) ⚠️neg-ctrl | +81,9 | **+47,9** | **−22,0** | +16,0 | **−43,1** |
| DBC | Chăn nuôi | 2022-11-15 | 6.950 | −72,2% | 0,52 | 1,33 | **PASS** | +32,1 | **+94,0** | +154,0 | +49,7 | +69,0 |
| BAF | Chăn nuôi | 2022-11-15 | 9.320 | −58,6% | 1,31 | 1,94 | FAIL (#3,#4) | +23,9 | **+39,8** | +74,7 | +41,4 | +86,4 |
| DCM | Phân bón | 2023-04-26 | 17.850 | −43,4% | 1,13 | 0,35 | FAIL (#4) ² | +31,0 | **+29,5** | +41,2 | +57,1 | +38,7 |
| DPM | Phân bón | 2023-05-25 | 14.170 | −44,7% | 0,96 | 0,24 | **PASS** | +10,7 | **+4,6** | −0,6 | +3,6 | +7,5 |
| DGC | Hoá chất | 2020-03-31 | 5.450 | −44,1% | 0,73 | 0,37 | **PASS** | +119,2 | **+238,1** | +1.406,5 | +152,9 | +1.075,1 |

¹ **Sửa phân loại có công bố (prereg §4 cho phép, bắt buộc nói rõ sửa vì số nào):** ex-ante tôi
chấm SSI **FAIL #4** với lý do "PB công ty chứng khoán hiếm khi <1". Dữ liệu PIT bác lại:
**PB SSI tại đáy = 0,93** (và HCM = 0,88) — chứng khoán VN **có** giao dịch dưới book ở đáy 2022.
SSI đạt cả 4 tiêu chí ⟹ chuyển sang PASS. HCM vẫn FAIL vì trượt #3 (không dẫn đầu thị phần).
² DCM: PB 1,13 > 1 ⟹ trượt #4 **đúng theo chữ của luật**, dù bảng cân đối là tiền mặt ròng
(Debt_Eq 0,35 — thấp nhất mẫu). Áp luật như đã viết, không nới sau khi thấy số.

### Nhóm (c) — vĩ mô (lợi suất TUYỆT ĐỐI cho chỉ số, BHAR cho cổ phiếu)

| Mã | Đáy | DD_250d | r12M / BHAR_12M | BHAR_24M | Đọc |
|---|---|---:|---:|---:|---|
| **VNINDEX** COVID | 2020-03-24 (659) | −35,7% | **+76,2%** (tuyệt đối) | — | Mua **chỉ số** trong panic vĩ mô: hiệu quả, không cần chọn mã |
| **VNINDEX** 2022 | 2022-11-15 (912) | −40,3% | **+23,1%** (tuyệt đối) | — | ⚠️ **ĐÍNH CHÍNH DISPATCH**: đáy 2022 rơi vào **Q4/2022**, KHÔNG phải Q1 (Nga-Ukraine). Q1/2022 là vùng **ĐỈNH** |
| FPT | 2020-03-30 | −33,7% | +49,1pp | +143,2pp | Lõi khoẻ ⟹ vượt thị trường mạnh |
| MWG | 2020-03-31 | −54,0% | +43,5pp | +152,5pp | Như trên |
| **VNM** | 2020-03-23 | −37,5% | **−28,3pp** | **−106,7pp** | ★ **Case phản chứng quý nhất cả job**: large-cap "rẻ", cùng panic, cùng đáy — nhưng **lõi đang xấu đi thật** (cạnh tranh + biên) ⟹ thua thị trường 107pp sau 24 tháng |

### Nhóm (d) — gián đoạn vận hành

| Mã | Sự kiện | Đáy | DD_250d | BHAR_12M | BHAR_24M | Có phải "case sợ hãi" không |
|---|---|---|---:|---:|---:|---|
| **RAL** | Cháy nhà máy + nhiễm thuỷ ngân 28/08/2019 | 2019-11-28 | **−19,9%** | +92,6pp | +135,5pp | **KHÔNG** — DD chỉ −19,9% |
| MSH | "3 tại chỗ" Q3/2021 | 2021-07-12 | −14,6% | +34,8pp | +26,7pp | **KHÔNG** |
| TNG | như trên | 2021-07-19 | −28,9% | +74,2pp | +54,8pp | **KHÔNG** |
| VHC | như trên | 2021-07-19 | −22,1% | +139,5pp | +115,3pp | **KHÔNG** |
| FMC | như trên | 2021-07-12 | −18,7% | +84,6pp | +69,2pp | **KHÔNG** |

**Kết luận (d): KHÔNG tìm được case đủ hình dạng, đúng như prereg §3.4 đã cảnh báo trước.** Cả 5 ứng
viên có DD **−14,6% đến −28,9%**, trong khi nhóm (b) có DD **−43% đến −90%**. Thị trường **chưa bao
giờ định giá đây là khủng hoảng** ⟹ không có "nỗi sợ" nào để mua. BHAR dương của chúng là lợi suất
của doanh nghiệp tốt trong thị trường tăng, **không phải bằng chứng cho khung này**. Báo đúng như
prereg đã cam kết: **không ép case cho đủ số**.

---

## 2. Vì sao H2 bị bác bỏ — tách theo TỪNG tiêu chí §2.5

Đây là phần có giá trị nhất của job, hơn cả verdict: **không phải cả 4 tiêu chí đều hỏng — chỉ một
tiêu chí thật sự làm việc, và nó chỉ làm việc ở chân trời dài hơn.**

| Tiêu chí §2.5 | Nhóm | n | BHAR_12M | BHAR_24M | T20_BHAR_24M | Phán quyết |
|---|---|---:|---:|---:|---:|---|
| **#3 leader chi phí thấp** | ✅ leader | 6 | **+98,2** | +115,4 | +44,8 | ❌ **KHÔNG phân biệt** — 12M **ngược chiều** |
| | ❌ không leader | 8 | **+121,2** | +103,9 | +39,6 | |
| **#2 sống sót qua đáy** | ⚠️ nghi ngờ (PDR, NVL) | 2 | +104,9 | **+34,5** | **+1,8** | ✅ **PHÂN BIỆT MẠNH — nhưng chỉ ở 24M** |
| | ✅ ổn | 12 | +108,3 | **+117,3** | **+44,8** | gap 24M = **−82,8pp** |
| **#4 sàn tài sản PB≤1** | PB ≤ 1,0 | 11 | **+114,1** | +117,8 | +39,8 | ⚠️ mạnh ở 12M (+74,3pp), **đảo chiều** ở T20_24M — n=3 quá nhỏ để tin |
| | PB > 1,0 | 3 | **+39,8** | +74,7 | +57,0 | |

**Ba hệ quả rút ra:**

1. **#3 (leader chi phí thấp) ANTI-phân biệt ở 12M.** Ngay trong CÙNG ngành CÙNG đáy: HSG/NKG (biên
   mỏng, DD −80%/−82%) nảy **+178/+167pp** so với HPG (leader, DD −71%) **+103pp**. Cơ chế: **độ nảy
   tỉ lệ với độ rơi, không tỉ lệ với chất lượng**. Kiểm chứng thô: `corr(DD_250d, BHAR_12M) = −0,263`
   trên 14 case (rơi sâu hơn ⟹ nảy mạnh hơn) — quan hệ có đúng chiều nhưng **yếu**, nên độ sâu không
   giải thích được hết; điều chắc chắn là chất lượng KHÔNG giải thích được.
2. **#2 (sống sót) là tiêu chí DUY NHẤT làm việc — và chỉ lộ ra ở 24M.** Ở 12M gap ≈ 0 (+104,9 vs
   +108,3): **thiệt hại cấu trúc chưa kịp cắn**. Ở 24M gap = **−82,8pp**, ở T20_24M nhóm nghi ngờ về
   gần **0 (+1,8pp)**. NVL — case chỉ định trước là structural — là mã **DUY NHẤT âm ở 24M**
   (−22,0pp) và âm nặng nhất ở neo thực tế (T20_24M **−43,1pp**). **Discriminator đã đúng, nhưng
   đúng ở đúng một chiều và đúng một chân trời.**
3. **Chân trời đo là quyết định, không phải chi tiết kỹ thuật.** Prereg khoá H2 ở **12M** — đó là
   lựa chọn của tôi từ dispatch, và nó **quá ngắn** để phân biệt "chu kỳ sẽ qua" khỏi "cấu trúc
   hỏng". Ở 24M, gap PASS−FAIL = **+26,9pp** (đạt ngưỡng 20pp). **Nhưng đây là quan sát HẬU NGHIỆM,
   KHÔNG được tính là GO** — đổi metric sau khi thấy số là đúng thứ prereg tồn tại để chặn. Ghi lại
   như **giả thuyết cho một prereg SAU**, không phải kết quả của job này.
   Thêm nữa gap 24M co còn **+11,1pp** khi dùng neo thực tế T20 ⟹ ngay cả giả thuyết đó cũng mong manh.

---

## 3. Đọc H1 cho đúng — "median +108pp" KHÔNG phải edge

| Chỉ số | T0 (ex-post) | T20 (thực tế hơn) |
|---|---:|---:|
| median BHAR_12M | +108,3pp | **+52,6pp** |
| median BHAR_24M | +115,0pp | **+43,2pp** |

Ba lý do con số này **không được đọc là edge**, cả ba đã khai trước ở prereg §5:

1. **N_eff = 6 episode độc lập** (Thép/CK/BĐS/Chăn nuôi/Phân bón 2022Q4 + Hoá chất 2020Q1), **không
   phải 14**. Mà 5/6 episode là **CÙNG MỘT cú sốc vĩ mô 2022Q4** ⟹ thực chất **~2 cú sốc độc lập**.
   Không chạy p-value trên N=14 (giả độc lập), đúng cam kết prereg §2.2.
2. **Trough là ex-post.** VNINDEX từ chính đáy 2022-11-15 đã +23,1% trong 12M — một phần lớn "alpha"
   ở đây là **mua đúng đáy của thị trường**, không phải chọn đúng mã.
3. **Mâu thuẫn có hệ thống với screen N-lớn §9** (`fearbuy_systematic_screen_20260723.md`, N=237
   episode 2008–2026): non-commodity median **+47,5%** vs commodity **+12,5%** — kết luận ở đó là
   **hàng hoá KHÔNG phải động lực**. Job này soi đúng cái subset median-thấp ấy và ra số đẹp hơn,
   nên **phải đọc là bằng chứng cho "2022Q4 là một đáy tốt"**, chứ không phải bằng chứng cho "nhóm
   chu kỳ có edge". §9 có N lớn hơn 17 lần và phủ 8 regime — **khi hai kết quả đá nhau, tin §9**.

**Survivorship: đã kiểm tra tường minh, KHÔNG có.** Cả 14/14 mã (b) có chuỗi giá liên tục tới
2026-06-15, gồm cả NVL và PDR. Không mã nào biến mất khỏi mẫu.

**Self-check (bắt buộc, §18 quant-research):** HPG T0_bhar12 pipeline = **+102,5pp**; tính tay từ 2
điểm giá thô (Close 8.180 @2022-11-10 → 17.900 @2023-11-10; VNINDEX 947,2 → 1.101,7) = **+102,5pp**
⟹ **PASS**. Đối chiếu độc lập: đáy/giá/lợi suất khớp **từng chữ số** với case HPG đã pin ở §8
(`đáy 2022-11-10, Close 8.180, PB 0,72, +12m +118,8%`) — pipeline job này tái hiện đúng số đã pin
từ một đường tính hoàn toàn khác.

---

## 4. Điều DUY NHẤT đủ tư cách đưa vào khung

**KHÔNG đề xuất đổi §2.5.** Với N_eff ≈ 2 cú sốc độc lập, sửa bộ tiêu chí theo kết quả này là
overfit đúng nghĩa. Ba thứ đề xuất **thêm dưới dạng CẢNH BÁO ĐỌC**, không đụng tiêu chí:

1. **Chân trời đánh giá của nhóm (b) phải là 24M, không phải 12M.** Ở 12M, mọi thứ rơi sâu đều nảy —
   không phân biệt được gì. Nhất quán với §8 đã ghi ("recovery của (b) CHẬM hơn nhưng BỀN"), nay có
   thêm số cho chiều ngược lại: **12M không đủ dài để phát hiện cái hỏng**.
2. **Tiêu chí #3 (leader chi phí thấp) KHÔNG phải bộ lọc chọn người thắng trong 1–2 năm đầu.** Nó
   có thể vẫn đúng như bộ lọc **rủi ro phá sản dài hạn** — nhưng bằng chứng ở đây nói: đừng dùng nó
   để kỳ vọng "leader nảy mạnh hơn". Kẻ biên mỏng nảy mạnh hơn, vì đã rơi sâu hơn.
3. **Tiêu chí #2 (sống sót qua đáy) là tiêu chí đáng đặt cược nhất** — và cách nó thể hiện là **tránh
   được thảm hoạ ở 24M** (NVL −43,1pp trên neo thực tế), **không phải** thắng đậm ở 12M. Đây là bộ
   lọc **phòng thủ**, đúng tinh thần "golden floor cắt blow-up" của §9 phát hiện #2.

---

## 5. Giới hạn (khai trước ở prereg, giữ nguyên sau khi có số)

1. **Pre-registered nhưng KHÔNG blind** — HPG/DGC đã documented, NVL là chuyện ai cũng biết. Tuyên bố
   mạnh nhất cho phép: **nhất quán nội bộ**, KHÔNG phải dự báo out-of-sample.
2. **"OOS" của dispatch chỉ là cái nhãn** — gần như toàn mẫu là 2022 (tức "sau 2020"), IS chỉ có
   DGC 2020 + RAL 2019. Đây **không phải walk-forward thật**.
3. **Không có test thống kê** — cố ý, vì N_eff quá nhỏ (§3 mục 1).
4. **Ngành ≠ episode độc lập** — 2022Q4 chi phối 5/6 episode.
5. **Nhóm (c)/(d) là quan sát, không phải test** — n quá nhỏ theo đúng thiết kế prereg.
