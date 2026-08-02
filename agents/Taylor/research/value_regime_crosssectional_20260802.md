# Định giá × DT5G ở **tầng cross-sectional (mã-ngày)** — IC của value có đổi theo chế độ thị trường không?

**Job**: `Taylor_20260802_042110` · **Ngày**: 2026-08-02 · **Loại**: RESEARCH, KHÔNG wire production,
KHÔNG sửa code production (đã xác nhận `git diff` sạch cho mọi file production).

**Bối cảnh**: chuỗi nghiên cứu index-timing DT5G × Value Radar đã ĐÓNG ở
[`market_regime_probability_20260729.md`](market_regime_probability_20260729.md) (Phụ lục E: bài toán
định thời điểm chỉ số ở VN chỉ có ~22–26 quan sát độc lập ⇒ 0/110 phép thử sống sót là kết quả **đúng dự
đoán của thiếu N**, không phải xui rủi). File này hỏi một câu **khác hẳn**: không phải "định giá có giúp
định thời điểm mua/bán chỉ số không", mà "**trong một rổ cổ phiếu đã qua cổng, xếp hạng theo độ rẻ có
dự báo lợi suất tương đối tốt hơn ở một số chế độ DT5G không**". Đây là tầng CHỌN MÃ, không phải tầng
định thời điểm — không mở lại phép thử nào đã đóng, không cộng dồn vào sổ 110 phép thử hôm qua.

---

## 0. Trả lời ngắn

| Câu hỏi | Trả lời | Bằng chứng cốt lõi |
|---|---|---|
| **1. IC của value có đổi theo DT5G state?** | **KHÔNG ĐỦ BẰNG CHỨNG** | Ở mức **episode độc lập** (12/20/10 đợt), mọi so sánh cặp p = 0,087–0,82; CI90 phủ 0. Quan trọng hơn: **hai panel độc lập cho DẤU NGƯỢC NHAU** ở CRISIS+BEAR (panel A −0,046 vs panel B +0,121) ⇒ đặc trưng của nhiễu, không phải hiệu ứng thật. |
| **2a. Độ phân tán định giá có liên quan DT5G / Value Radar?** | **Liên quan MẠNH tới Value Radar, KHÔNG liên quan DT5G** | Spearman(IQR, `radar3_roll`) = **−0,709** (p<0,001, N=143 tháng); Spearman(IQR, trung vị 1/PE) = **+0,846**; Spearman(state DT5G, IQR) = **+0,027** (p=0,75). Độ phân tán gần như là **một cách viết lại mức rẻ tổng thể của thị trường** — không phải thông tin mới. |
| **2b. IC value có cao hơn trong những ngày phân tán rộng?** | **KHÔNG ĐỦ BẰNG CHỨNG** | Ở mức tháng p=0,001–0,046 (**trông rất mạnh**) nhưng đó là **pseudo-N**: IQR có autocorr lag-1 = 0,84, 48 tháng "RỘNG" chỉ là **13 khối liên tục**; ở mức khối p=0,35–0,42, CI90 phủ 0. Tercile lại **trùng gần khít với THỜI KỲ** (RỘNG: 45/48 tháng thuộc 2020+; HẸP: 41/48 thuộc 2014–19). Panel B cho **dấu ngược lại** (−0,112). |
| **Có đề xuất đổi production không?** | **KHÔNG** | Không có cơ sở cho quy tắc tăng conviction/tập trung rổ theo state. Kết quả ngược lại **ủng hộ thiết kế hiện tại**: rating = cổng nhị phân, value dùng để xếp thứ tự, KHÔNG phải return-tilt theo chế độ. |
| ~~**Phát hiện phụ (quan trọng, ngoài 2 câu hỏi)**~~ 🛑 **ĐÃ BỊ BÁC BỎ 2026-08-02 — xem banner §5** | ~~Có look-ahead giá điều chỉnh trong mọi nghiên cứu value đọc thẳng `PE`/`PCF` từ `tav2_bq.ticker`~~ **SAI: `PE` vốn đã ở cơ sở `Price` thô PIT đúng** | `PE` lưu theo **Close đã điều chỉnh** ⇒ 1/PE lịch sử bị thổi bởi hệ số điều chỉnh TƯƠNG LAI. Sửa lại: IC +0,125 → **+0,096** (toàn universe); trong cổng production còn **+0,034 (t=1,37, KHÔNG có ý nghĩa)**. `rating_8l.py` **đã** sửa; **`custom_basket.py::_yield_piv` (selector yieldcombo của custom30V) CHƯA sửa** ⇒ backtest custom30V mang bias này (live không, vì hôm nay hệ số ≈1). Xem §5. |

---

## 1. Phương pháp — chống bẫy pseudo-N

### 1.1 Chọn (a) Fama-MacBeth, KHÔNG dùng OLS gộp dòng
Panel mã-ngày trông có N lớn (hàng chục nghìn dòng) nhưng các mã **cùng ngày** di chuyển tương quan
(thị trường chung). Cách làm ở đây:

1. Mỗi **ngày quan sát** chạy **một** hồi quy cross-sectional riêng `fwd ~ a + b·value` ⇒ một hệ số
   `b_t` và một rank-IC (Spearman) cho ngày đó.
2. Chuỗi `{b_t}`, `{IC_t}` theo thời gian là đơn vị thống kê. **N hiệu dụng = số kỳ quan sát**, không
   phải số dòng panel.
3. Ngày quan sát = **phiên giao dịch cuối mỗi tháng** ⇒ `fwd20` (20 phiên ≈ 1 tháng) **gần như không
   chồng lấn** ⇒ t-stat thường. `fwd60` chồng lấn 3 tháng ⇒ **Newey-West lag 2**.
4. **Bước then chốt, cả 2 câu hỏi**: state DT5G và độ phân tán đều **rất dai dẳng** (một đợt CRISIS kéo
   nhiều tháng liền; autocorr lag-1 của IQR = 0,84). Vì vậy mọi kết luận **được báo ở mức EPISODE** —
   gộp các tháng liên tiếp cùng nhóm thành **một** quan sát. Số tháng chỉ dùng để mô tả.

> Đây chính là bẫy đã bắt 3–4 lần ngày 2026-07-29 (ROE: N=3900 ngày chồng lấn → thật 15 năm; DT5G
> 1-tuần: N=1919 ngày → thật 7 sự kiện). Ở đây nó **tái diễn đúng như dự đoán**: câu hỏi 2 có p=0,001
> ở mức tháng và p=0,42 ở mức episode.

### 1.2 Hai panel độc lập (chống lỗi pipeline một chiều)

| | **Panel A** (tự dựng cho việc này) | **Panel B** (đông cứng, đã pin sẵn) |
|---|---|---|
| Nguồn | `tav2_bq.ticker` × `tav2_mike.universe_pit` (PIT) × `tav2_bq.fa_ratings_8l` (as-of) × `tav2_bq.vnindex_5state_dt5g_live` | `data/value_panel_2014.csv` (PIT, input đông cứng của audit R3) + as-of rating từ `fa_ratings_8l` |
| Kỳ quan sát | phiên cuối **tháng**, 2014-06-30 → 2026-07-31 (145 tháng) | phiên cuối **quý** (49 quý) |
| Forward | `Close_adj(T+20)/Close_adj(T) − 1` và T+60 | cột `profit_2M` (T+40) |
| Universe | `in_universe` ∧ rating≤3 ∧ `Trading_Value_1M_P50` ≥3 tỷ | universe panel ∧ rating≤3 ∧ `turnover` ≥3 tỷ |
| Quy mô | 15.232 dòng, 494 mã, **trung vị 101 mã/tháng** | **trung vị 108 mã/quý** |
| Đo value | `ey_pct` = percentile 1/PE trong route (chính); `vs_proxy` = composite v3_div tái lập | `ey` = 1/PE thô (đúng như bản pin) |

Đã tra `mike/kb/data_registry/` trước khi chọn nguồn: dùng `universe_pit` (CANONICAL, PIT) **chứ không
phải `ticker_prune`**; dùng `vnindex_5state_dt5g_live` (DT5G production) **chứ không phải bare
`vnindex_5state`** (đó là v3.4b base — bẫy đã ghi trong CLAUDE.md).

**Sàn thời gian = 2014-06, KHÔNG phải 2008** như dispatch nêu: `vnindex_5state_dt5g_live` bắt đầu
2014-01-02 và `fa_ratings_8l` bắt đầu 2014-07-09. Trước 2014 không tồn tại state DT5G ⇒ câu hỏi
"IC theo state" không định nghĩa được.

### 1.3 Sai lệch có chủ đích của `vs_proxy` so với `value_score_v3` production
Tái lập từ `rating_8l.py` (VALUE_VERSION=`v3_div`): percentile trong route của các lăng kính, hợp nhất
coverage-aware theo đúng bộ trọng số `VR_W`, cộng golden-cell +0,10 và track-bonus, PB<0 → 0. Khác:
(i) **thiếu lăng kính `ps`** (`tav2_bq.ticker` không có Revenue/PS) ⇒ trọng số còn lại được chuẩn hoá
lại; (ii) `cfo_normy` dùng chuẩn 5Y/5 thay vì 3Y/3; (iii) **bỏ peak-earnings guard** (cần `ROE_Trailing`);
(iv) không áp registry forensic/moat (chúng là cap **rating**, không phải value). Vì các sai lệch này,
**panel B (bản pin, không do tôi dựng) là bản đối chứng chính** — và nó cho cùng kết luận định tính.

### 1.4 Self-check (`selfcheck.py`, PASS 5/5)
`[1]` cổng rating≤3 & liq≥3 tỷ không hở · `[2]` IC tổng thể tính lại từ panel khớp CSV hệ số tới 1e-9 ·
`[3]` `fwd20` dựng lại từ `panel_raw.csv` sai số 1,1e-16 · `[4]` hệ số điều chỉnh giá đơn điệu giảm theo
thời gian (2,31 năm 2014 → 1,00 năm 2026), chỉ 0,37% dòng <0,99 (Price thô lẻ ở vài mã UPCOM) ·
`[5]` state trong panel khớp `dt5g_live` 0/145 ngày lệch.

---

## 2. Câu hỏi 1 — IC của value theo DT5G state

### 2.1 Panel A (tự dựng) — mức **episode**, `value = ey_pct`

| nhóm | N episode | N tháng | IC trung bình | t | CI90 |
|---|---|---|---|---|---|
| **fwd20 (T+20)** | | | | | |
| CRISIS+BEAR | 12 | 34 | **−0,046** | −1,80 | [−0,091; −0,000] |
| NEUTRAL | 20 | 85 | +0,009 | +0,42 | [−0,030; +0,049] |
| BULL+EXBULL | 10 | 24 | +0,031 | +0,92 | [−0,031; +0,093] |
| **fwd60 (T+60, NW lag2)** | | | | | |
| CRISIS+BEAR | 12 | 34 | −0,069 | −1,25 | [−0,167; +0,030] |
| NEUTRAL | 20 | 83 | −0,029 | −1,10 | [−0,074; +0,016] |
| BULL+EXBULL | 10 | 24 | +0,026 | +1,12 | [−0,016; +0,068] |

So sánh cặp (Welch trên trung bình episode): CRISIS+BEAR − NEUTRAL p=0,117 (fwd20) / 0,522 (fwd60);
BULL+EXBULL − NEUTRAL p=0,602 / 0,129; CRISIS+BEAR − BULL+EXBULL p=**0,087** / 0,135. Với `vs_proxy`
mọi p ≥ 0,44. **EXBULL chỉ 3 tháng (1–2 episode) ⇒ không kiểm định được, chỉ ghi nhận mô tả.**

### 2.2 Panel B (bản pin, quý, `profit_2M`) — trong cổng production, đã sửa giá

| nhóm | N episode | N quý | IC | t (episode) | CI90 (episode) |
|---|---|---|---|---|---|
| TẤT CẢ | 18 | 42 | +0,057 | +2,24 | [+0,013; +0,101] |
| CRISIS+BEAR | 4 | 10 | **+0,121** | +2,20 | [−0,009; +0,250] |
| NEUTRAL | 9 | 24 | +0,002 | +0,06 | [−0,053; +0,056] |
| BULL+EXBULL | 5 | 8 | +0,104 | +2,27 | [+0,006; +0,202] |

Cặp: CRISIS+BEAR − NEUTRAL p=0,117; BULL+EXBULL − NEUTRAL p=0,099; CRISIS+BEAR − BULL+EXBULL p=0,823.

### 2.3 Vì sao trả lời **KHÔNG ĐỦ BẰNG CHỨNG**, không phải "KHÔNG"

1. **Hai panel cho dấu ngược nhau ở đúng nhóm quan trọng nhất.** Panel A: value **âm** trong
   CRISIS+BEAR (−0,046). Panel B: value **dương mạnh nhất** trong CRISIS+BEAR (+0,121). Cả hai đều
   dùng cùng cổng rating/liq, cùng nguồn state. Hai cách dựng hợp lệ cho hai câu chuyện trái ngược ⇒
   thứ đang đo là **nhiễu ở tầng episode**, không phải cấu trúc.
2. **Không phép so sánh nào qua nổi ngưỡng đa kiểm định.** Với N_trials=16 (§7), ngưỡng Bonferroni
   ≈0,003; p tốt nhất ở mức episode = 0,087.
3. **N cấu trúc quá mỏng đúng như bài học 07-29.** 12 năm DT5G chỉ chứa ~4–12 đợt bear/crisis độc lập
   tuỳ cách gộp. Kể cả nếu hiệu ứng thật tồn tại ở mức |ΔIC| ≈ 0,05, N này không thể phân biệt nó với 0.
4. **Đối chiếu kết quả cũ**: bản pin `data/results_registry.md` — "THREAD (c) ĐÓNG — value thắng MỌI
   regime, không có edge regime-SELECTION" (ey IC: DOWN +0,148 / NEUTRAL +0,107 / BULL +0,156) — được
   **tái lập chính xác** ở đây (§5.2) và kết luận định tính của nó **được củng cố**: khác biệt giữa các
   state không có ý nghĩa thống kê ở mức episode (p=0,38–0,82). Việc làm mới ở đây là (i) đo trong
   **cổng production** thay vì toàn universe, và (ii) đếm N theo **episode** thay vì theo quý.

---

## 3. Câu hỏi 2 — độ phân tán định giá cross-sectional

Độ phân tán đo trên **1/PE thô đã sửa giá** (IQR trong pool mỗi ngày). *Không* đo trên percentile:
phân phối percentile luôn đều nên "độ phân tán của percentile" là hằng số vô nghĩa.

### 3.1 (a) Quan hệ với DT5G và Value Radar — mô tả

| state | N tháng | IQR trung bình | IQR trung vị | trung vị 1/PE |
|---|---|---|---|---|
| CRISIS | 21 | 0,0405 | 0,0356 | 0,0415 |
| BEAR | 13 | 0,0529 | 0,0510 | 0,0642 |
| NEUTRAL | 86 | 0,0439 | 0,0405 | 0,0426 |
| BULL | 21 | 0,0423 | 0,0400 | 0,0443 |
| EXBULL | 3 | 0,0424 | 0,0408 | 0,0465 |

- **Spearman(state DT5G, IQR) = +0,027 (p=0,75)** ⇒ độ phân tán **không** là hàm của chế độ DT5G.
- **Spearman(IQR, `radar3_roll`) = −0,709 (p<0,001, N=143)** ⇒ thị trường càng RẺ theo Value Radar,
  độ phân tán định giá càng RỘNG.
- **Spearman(IQR, trung vị 1/PE) = +0,846** ⇒ và chính đó là lý do: IQR gần như là **cách viết lại
  mức rẻ tổng thể**, không phải chiều thông tin thứ hai. Một chỉ báo tương quan 0,85 với thứ ta đã có
  thì không thêm được gì cho quyết định.

### 3.2 (b) IC value theo tercile độ phân tán — **ví dụ mẫu về bẫy pseudo-N**

| | mức **THÁNG** (sai) | mức **EPISODE** (đúng) |
|---|---|---|
| ey_pct / fwd20 | RỘNG−HẸP = +0,060, t=+2,03, **p=0,046** | +0,044, t=+0,81, **p=0,424** (13 vs 13 khối) |
| ey_pct / fwd60 | +0,089, t=+2,81, **p=0,006** | +0,062, t=+0,97, **p=0,346** |
| vs_proxy / fwd20 | +0,069, t=+2,47, **p=0,015** | +0,043, t=+0,89, **p=0,384** |
| vs_proxy / fwd60 | +0,102, t=+3,32, **p=0,001** | +0,061, t=+0,93, **p=0,364** |

CI90 bootstrap theo khối (20.000 lần lấy mẫu lại các khối) phủ 0 ở cả 4 biến thể, ví dụ
vs_proxy/fwd60: [−0,047; +0,160].

**Hai lý do nữa để không tin con số mức tháng:**

1. **Trùng thời kỳ gần như hoàn toàn.** Tercile RỘNG: 45/48 tháng thuộc 2020+; tercile HẸP: 41/48
   thuộc 2014–19. Tách theo thời kỳ: IC (ey_pct/fwd20) = **−0,065 giai đoạn 2014–19** vs **+0,029
   giai đoạn 2020–26**. Nói cách khác cái ta gọi là "hiệu ứng phân tán" phần lớn là "IC của value đổi
   dấu giữa hai thời kỳ". Trong nội bộ 2014–19 **không kiểm định được** (chỉ 2 tháng thuộc tercile
   RỘNG); trong nội bộ 2020–26 nhóm đối chứng HẸP chỉ có 7 tháng = **2 khối liên tục** ⇒ N=2.
2. **Panel B cho dấu ngược lại**: RỘNG−HẸP = −0,053 (mức quý, p=0,341) / **−0,112** (mức episode,
   4 vs 6 khối, p=0,170).

⇒ **KHÔNG ĐỦ BẰNG CHỨNG.** Và ngay cả nếu tin con số mức tháng thì §3.1 đã cho thấy nó **không phải
tín hiệu mới** — nó gần trùng với mức rẻ tổng thể mà Value Radar đã hiển thị.

---

## 4. Bảng mô tả tương tác 2 chiều (state × phân tán) — chỉ để tham khảo

IC trung bình (ey_pct/fwd20, panel A), **số tháng** trong ngoặc — mọi ô đều dưới ngưỡng N cần thiết,
đưa vào để người đọc sau không phải chạy lại rồi tưởng tìm ra điều gì mới:

| | HẸP | GIỮA | RỘNG |
|---|---|---|---|
| CRISIS+BEAR | −0,063 (14) | +0,032 (10) | −0,007 (10) |
| NEUTRAL | −0,019 (28) | −0,062 (27) | +0,015 (30) |
| BULL+EXBULL | −0,065 (6) | +0,017 (11) | +0,093 (7) |

Không ô nào có ≥3 episode độc lập. Không kiểm định.

---

## 5. ~~Phát hiện phụ — look-ahead giá điều chỉnh trong dữ liệu định giá lịch sử~~ **[ĐÃ BỊ BÁC BỎ]**

> 🛑 **CẢNH BÁO — TOÀN BỘ §5 SAI, ĐỪNG HÀNH ĐỘNG THEO.** Job `Taylor_20260802_054825` (2026-08-02)
> đã bác bỏ tiền đề của mục này. `tav2_bq.ticker.PE/PB/PCF` **KHÔNG** ở cơ sở `Close` đã điều chỉnh —
> chúng ở cơ sở **`Price` thô của chính ngày đó, point-in-time ĐÚNG**. Verify quy mô universe
> (2014–2021, 1.419.351 dòng / 23.067 cặp ticker×kỳ báo cáo): `PE/Price` hằng số trong kỳ ở **93,1%**
> số kỳ vs `PE/Close` **11,0%** (PB 94,6/12,6; PCF 86,9/20,3); đối chiếu tay VNM & FPT 2015-06-30 tái
> lập `NP_ttm/OShares` **chỉ từ `Price` thô**.
>
> Hệ quả, đảo ngược từng điểm dưới đây:
> - **`1/PE` đọc thẳng từ bảng vốn đã đúng.** Nhân `Price/Close` là **ĐƯA look-ahead VÀO**.
> - **IC +0,125 là số ĐÚNG** — hai con số "đã sửa" +0,096 / +0,034 ở §5.2 là số **ĐÃ NHIỄM**, bỏ đi.
>   Trong cổng production con số đúng là **+0,088 (t=3,62)** (cột "chưa sửa"), **có** ý nghĩa.
> - **`custom_basket.py::_yield_piv` KHÔNG có lỗi** — đừng "sửa". A/B NAV đã chạy (cùng vintage,
>   snapshot `bq_cache_asof20260729_postrestate`, self-check 0 VND cả 2 chân): áp "phép sửa" làm R3
>   **XẤU đi −1,70pp CAGR** (27,60→25,90), Calmar 1,58→1,39, 11/13 năm xấu hơn.
> - **`rating_8l.py:521-524` mới là chỗ có lỗi** (nó đang nhân `Price/Close`) — live ≈0, nhưng là
>   lỗi MỞ. §5.1 khen nhầm dòng code này là "đã sửa đúng".
> - Câu hỏi 1 & 2 (§2–§4, kết luận "KHÔNG ĐỦ BẰNG CHỨNG") **KHÔNG bị ảnh hưởng** bởi việc bác bỏ này
>   — chúng dựa trên `ey_pct` (percentile) và panel B dùng `ey` thô; xếp hạng percentile trong ngày
>   không đổi khi bỏ phép nhân sai. Riêng dòng "đã sửa **đảo dấu** kết quả" ở §5.2 nay đọc là: bản
>   **chưa** nhân (tức bản ĐÚNG) cho IC dương +0,039/+0,059, còn bản nhân sai mới ra ≈0/âm.
>
> Bằng chứng + A/B đầy đủ: [`pe_priceadj_refutation_ab_20260802.md`](pe_priceadj_refutation_ab_20260802.md) ·
> `mike/kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md` "Bẫy (4)" ·
> `data/results_registry.md` mục "2026-08-02 — BÁC BỎ...".

### (nguyên văn mục đã bị bác bỏ, giữ lại để tra cứu lịch sử)

Đây là kết quả ngoài 2 câu hỏi được giao, phát hiện khi chẩn đoán vì sao IC panel A ≈ 0. Nó **quan
trọng hơn** cả hai câu trả lời trên vì chạm vào một con số đã pin và một selector đang dùng trong backtest.

### 5.1 Cơ chế
`tav2_bq.ticker.PE` được tính trên **Close đã điều chỉnh**, còn `Price` là giá thô. Hệ số
`F = Price/Close` đo được **chính xác là hệ số điều chỉnh tích luỹ từ ngày đó tới HÔM NAY**:

| năm | 2014 | 2016 | 2018 | 2020 | 2022 | 2024 | 2026 |
|---|---|---|---|---|---|---|---|
| F trung vị | 2,31 | 2,13 | 1,83 | 1,57 | 1,23 | 1,10 | 1,00 |

(VNM: 4,31 → 1,00; FPT: 6,69 → 1,00.) Vì `earn_yield_lưu = F × earn_yield_thật`, xếp hạng "rẻ" theo
số lưu **thiên vị mã sẽ chia cổ tức/thưởng nhiều trong TƯƠNG LAI** — thông tin không có ở thời điểm t
(live hôm nay F≈1, nên bảng xếp hạng live nhìn thấy số khác hẳn backtest cho cùng một ngày lịch sử).
`rating_8l.py` đã sửa đúng (`_pe_adj_factor`, dòng ~519) và ghi rõ "fixes historical inflate of
earn_yield pre-2016". Đây là script **duy nhất** trong repo có phép sửa này (`grep`).

### 5.2 Đo lường (panel B, quý, `profit_2M`, N=42–49 quý)

| universe | 1/PE **chưa sửa** | 1/PE **đã sửa** |
|---|---|---|
| toàn universe | **+0,1254 (t=10,88, hit 94%)** ← đúng bằng số đã pin "+0,125, t=11,0, hit 94%" | **+0,0955 (t=8,25, hit 88%)** |
| rating≤3 | +0,1037 (t=9,38) | +0,0748 (t=6,39) |
| liq ≥3 tỷ | +0,0978 (t=4,75) | +0,0455 (t=2,06) |
| **rating≤3 ∧ liq ≥3 tỷ (= cổng production)** | +0,0878 (t=3,62) | **+0,0336 (t=1,37, hit 62%)** |

Trên panel A (tháng, universe rộng chỉ lọc thanh khoản): chưa sửa +0,039 (t=3,59) / +0,059 (t=5,48);
**đã sửa −0,006 (t=−0,50) / −0,015 (t=−1,18)** — tức ở panel này phép sửa **đảo dấu** kết quả.

### 5.3 Ba hàm ý (đề xuất, **không** tự thực hiện)

1. **`custom_basket.py::_yield_piv`** (dòng ~338) tính `AVG(1/PE)`, `AVG(1/PCF)` thẳng từ
   `tav2_bq.ticker` **không sửa hệ số giá**. Đây là selector `yieldcombo` = rank(1/PE)+rank(1/PCF) của
   **custom30V** — cấu phần được KB mô tả là "phần tin cậy nhất, +7,4pp Full". **Live không bị ảnh hưởng**
   (hôm nay F≈1 cho mọi mã) nhưng **backtest thì có**: mọi kỳ tái cân bằng lịch sử xếp hạng trên một
   đại lượng chứa thông tin tương lai. ⇒ **Đề xuất một A/B đo NAV**: chạy lại custom30V với
   `1/(PE×Price/Close)` và so CAGR/Sharpe với bản pin. **Chưa đo được biên độ tác động NAV — không
   được suy ra R3 sai.** Đây là việc riêng, cần quant-skeptic nếu dẫn tới thay đổi thật.
2. **Chú thích lại số đã pin** trong `data/results_registry.md` (mục "IC PANEL 8L", dòng ~159) và
   `kb/KNOWLEDGE.md` §"8L Rating & Composite": "1/PE IC +0,125" nên đọc là **+0,096 sau khi khử bias
   giá điều chỉnh**, và **+0,034 (t=1,37, không có ý nghĩa) bên trong cổng production rating≤3 ∧
   liq≥3 tỷ**. Kết luận định tính "1/PE là lăng kính value mạnh nhất" **không đổi** — nó vẫn là lăng
   kính đứng đầu ở mọi biến thể; chỉ là biên độ nhỏ hơn và **phần lớn biên độ nằm ở đuôi kém thanh
   khoản mà V2.4 cố ý không giao dịch**.
3. **Thêm một dòng cảnh báo vào `mike/kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md`**:
   `PE/PCF/PS/EVEB` trong `tav2_bq.ticker`/`ticker_prune` ở **cơ sở giá điều chỉnh**; mọi nghiên cứu
   lịch sử phải nhân `Price/Close` trước khi xếp hạng cross-sectional. (Tôi **không** tự sửa file KB —
   theo §13 coding_guidelines, nếu Mike muốn thì tôi ghi ra `.proposed`.)

---

## 6. Hàm ý cho quyết định (kết luận nghiệp vụ)

- **Không có cơ sở** cho quy tắc kiểu "tăng conviction/tập trung rổ LAG/BAL khi DT5G không thuận vì IC
  value cao hơn". Bằng chứng cho tiền đề ("IC value cao hơn khi DT5G không thuận") **không tồn tại ở
  mức episode**, và hai panel còn cho dấu ngược nhau.
- **Không có cơ sở** cho một cổng/tilt dựa trên độ phân tán định giá. Ngay cả bản đọc lạc quan nhất
  thì nó cũng gần trùng (ρ=−0,71) với Value Radar đang hiển thị — thêm chỉ báo mà không thêm thông tin.
- **Kết quả củng cố thiết kế hiện hành**: rating 8L = **cổng nhị phân ≤3**, value dùng để **xếp thứ tự**
  trong cổng, KHÔNG phải return-tilt điều kiện theo chế độ. Đúng như bản pin đã kết luận từ 2026-06-21
  ("Rating = RISK-GATE, không phải return-tilt") — nay có thêm bằng chứng ở tầng cross-sectional rằng
  **cũng không có tilt theo chế độ nào bỏ quên**.
- **Việc đáng làm tiếp** (theo thứ tự giá trị): (1) A/B look-ahead của `_yield_piv` ở §5.3.1 — đây là
  câu hỏi có N đủ lớn và ảnh hưởng trực tiếp tới độ tin cậy của con số backtest đang dùng để ra quyết
  định; (2) chú thích lại số pin §5.3.2; (3) cảnh báo data_registry §5.3.3. Cả 3 đều **chờ Mike/user
  quyết**, không tự làm.

---

## 7. Kỷ luật thống kê — N_trials và hạn chế

**N_trials của riêng việc này = 16 đặc tả kiểm định** (không cộng vào sổ 110 phép thử của chuỗi
index-timing đã đóng):
Câu 1 — panel A: 2 định nghĩa value × 2 horizon = 4; panel B: 3 cấu hình universe = 3. Câu 2 — panel A:
4 (2×2) + 4 (tách thời kỳ) = 8; panel B: 1. **Tổng 16.** Ngoài ra 11 lần chạy chẩn đoán/đối chiếu
(bảng IC theo lăng kính, biến thể universe, tái lập số pin) — **không** phải kiểm định giả thuyết, ghi
ra đây để không ai đếm sót. Ngưỡng Bonferroni cho 16 phép ≈ 0,003; **p tốt nhất ở mức episode = 0,087**
⇒ không phép nào sống sót. Không tính DSR/PBO vì **không có** đề xuất wire nào.

**Hạn chế đã biết:**
1. Sàn 2014-06 (DT5G không tồn tại trước 2014), không phải 2008.
2. `vs_proxy` ≠ `value_score_v3` production (thiếu lens `ps`, chuẩn cashflow 5Y thay 3Y, bỏ peak-earn
   guard) — §1.3. Panel B là bản đối chứng cho điểm này.
3. `DA_HEAVY_SET` dùng danh sách **hôm nay** áp cho lịch sử (look-ahead nhẹ ở gán `val_route`; chỉ ảnh
   hưởng trọng số lăng kính, không ảnh hưởng cổng).
4. EXBULL 3 tháng / 1–2 episode ⇒ không kiểm định được, chỉ mô tả.
5. Hai panel còn lệch ở mức tổng thể (A: ≈0 tới −0,04; B: +0,034) — chênh nằm trong dải nhiễu của hai
   thiết kế (universe, horizon T+40 vs T+20/T+60, `turnover` ngày vs `Trading_Value_1M_P50`), nhưng
   **tôi không khép được chênh này**; nó là lý do nữa để không tuyên bố mạnh theo chiều nào.
6. Sửa hệ số giá áp cho `EVEB` chỉ đúng gần đúng (F nhân vào phần vốn hoá, không vào nợ ròng).

**Tái lập** (thư mục `mike/agents/Taylor/exp_value_xsec/`, interpreter `/home/trido/thanhdt/wc_venv/bin/python`):
```bash
cd mike/agents/Taylor/exp_value_xsec
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv \
   --max_rows=500000 < pull_panel.sql > panel_raw.csv       # panel A thô
$PY build_panel.py      # -> panel.csv.gz          (self-check coverage/route/lens)
$PY fm_analysis.py      # câu 1 + câu 2, mức tháng  -> fm_*.csv, dispersion.csv
$PY episodes.py         # câu 2, mức khối + bootstrap khối
$PY q1_blocks.py        # câu 1, mức episode + kiểm tra trùng thời kỳ
$PY reconcile.py        # tái lập số pin +0,125 và phân rã bias giá
$PY q1_pinnedpanel.py   # câu 1 trên panel B
$PY q2_pinnedpanel.py   # câu 2 trên panel B
$PY selfcheck.py        # 5/5 PASS
```
Log đầy đủ của mỗi lần chạy: `log_<tên script>.txt` cùng thư mục.

**Production không bị đụng**: mọi thứ ghi trong `exp_value_xsec/` (theo §8 coding_guidelines — tên
non-canonical, không trùng bất kỳ CSV nào được pin).
