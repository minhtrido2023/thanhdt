# Lăng kính CƠ BẢN bổ sung cho DT5G — bộ chỉ số định giá chuẩn ngành có dùng được cho VN không?

**Ngày dữ liệu: 2026-07-28** · job `Taylor_20260729_082452` · Taylor (Quant)
**Loại: RESEARCH / trả lời câu hỏi chiến lược — KHÔNG wire gì vào production trong job này.**

> **Bối cảnh & liên kết** (không lặp lại nội dung):
> - Báo cáo gốc: [`market_regime_probability_20260729.md`](market_regime_probability_20260729.md)
>   — §1 PE/PB hiện tại, §2 base rate, §4 kết luận xác suất bear ~20%.
> - **Phụ lục A** (cùng file, §A) — ROE NO-GO vì **đồng nhất thức** ROE = PB/PE.
> - **Phụ lục B** (cùng file, §B) — đính chính P/B: VIC bóp méo chỉ số cap-weighted.
> - Ý tưởng của user (thread 1525112292159651940): DT5G là gate **giá/kỹ thuật** (momentum + macro,
>   không đọc định giá) ⇒ dùng lăng kính **cơ bản** làm góc nhìn thứ hai, khai thác **divergence**.

---

## 0. Trả lời ngắn

| Câu hỏi | Trả lời |
|---|---|
| Có bộ chỉ số định giá chuẩn ngành nào tính được cho VN? | **Có 3**: CAPE (5/7/10 năm), EV/EBITDA, ERP. Buffett Indicator: **không** (thiếu GDP danh nghĩa). |
| Chúng có nói điều gì MỚI so với PE/PB không? | **CAPE: KHÔNG** (85–93% phương sai là PE+PB sau khi khử xu hướng). **EV/EBITDA: mới nhưng vô nghĩa** (trực giao 91%, sức dự báo ~0). **ERP: mới một phần (63%) nhưng yếu hơn PB đơn lẻ.** |
| Composite z-score có đáng xây không? | **KHÔNG.** Các thành phần tương quan 0,79–0,95; composite dự báo **KÉM HƠN** P/B đơn lẻ (ρ −0,443 vs −0,473). |
| Định giá lúc CAPIT fire có tương quan chất lượng kết quả không? | **Có dấu hiệu thật, đúng hướng kinh tế, và — khác hẳn ROE — KHÔNG đa cộng tuyến với thứ hệ thống đã dùng.** Nhưng **0/56 phép thử qua BH**, N = 22–26 sự kiện, và bỏ riêng năm 2022 làm tín hiệu 12M đảo dấu. |
| **Verdict cuối** | **NO-GO wire tilt sizing bây giờ.** ĐỀ XUẤT: **shadow-log** phân vị P/B tại mỗi lần CAPIT fire (§3.2) — rẻ, không đụng tiền, và là cách DUY NHẤT để N lớn dần. |

**Một câu tổng kết ngược với kỳ vọng ban đầu:** thêm lăng kính định giá **không làm bức tranh rõ hơn,
nó thêm một bậc tự do mô hình**. Với 10–19 năm dữ liệu VN, chỉ riêng việc chọn **có khử xu hướng cơ học
hay không** đã làm phân vị của cùng một chỉ số nhảy **30–45 điểm** (§1.3) — biên độ lớn hơn toàn bộ tín
hiệu mà chỉ số đó mang lại.

---

## 1. VIỆC 1 — Khảo sát khả thi bộ chỉ số định giá chuẩn ngành

### 1.1 Bảng khả thi

Rổ chuẩn dùng xuyên suốt = **top-100 vốn hoá mỗi phiên**, và mọi tỷ số đều báo **song song** bản
cap-weighted THÔ và ≥1 bản **bền với outlier** (capped-weight 10%/mã, trung vị equal-weight) — đúng
phương pháp Phụ lục B.4.

| Chỉ số | Công thức chuẩn ngành | Tính được từ BQ? | Ghi chú |
|---|---|---|---|
| **CAPE / Shiller PE** | P / mean(E thực N năm) | **CÓ** — E chỉ số = `VNINDEX / PE`, khử lạm phát bằng CPI | Cửa sổ đủ: 5Y từ **2011-09**, 7Y từ **2013-07**, 10Y từ **2016-03** |
| **EV/EBITDA** | ΣEV / ΣEBITDA | **CÓ** — `ticker.EVEB` × `ticker.EBITDA_P0` | Từ **2009-05** (17,2 năm) |
| **ERP** | earnings yield − lãi suất phi rủi ro | **CÓ (proxy)** — ey − lãi huy động Big4-12M | Từ **2011-01**; xem §1.7 về TPCP |
| **Market Cap / GDP** | mcap thị trường / GDP danh nghĩa | **KHÔNG** | Xem §1.6 |
| **Composite z-score** | trung bình z các chỉ số độc lập | Tính được nhưng **NO-GO** | §1.5 |

**Nguồn khử lạm phát (CAPE)**: `cpi_vn.py` (registry `mike/kb/data_registry/macro/cpi_vn.md`,
status CANONICAL-PROXY) cho 2011-01→2026-06; **bổ sung 4 mốc bình quân năm 2007–2010**
(8,36 / 22,98 / 6,70 / 9,23 %) tra cứu và xác minh bằng WebSearch ngày 2026-07-29 (World Bank
`FP.CPI.TOTL.ZG` / GSO). Không tự chế số. Chỉ số CPI dựng được: 2006=100 → **2026 = 320,4**.

### 1.2 Giá trị hiện tại + phân vị

| Chỉ số | Hiện tại | Dữ liệu từ | Số năm | Độ dốc/năm | **Phân vị THÔ** | **Phân vị KHỬ XU HƯỚNG** |
|---|---|---|---|---|---|---|
| P/E capped-10% | **11,59** | 2007-03 | 19,4 | −0,002 | **23,1** | 23,3 |
| P/E cap-weighted thô | 12,93 | 2007-03 | 19,4 | −0,035 | 39,0 | 42,8 |
| P/B capped-10% | **1,838** | 2007-03 | 19,4 | −0,039 | **33,6** | *59,2* |
| P/B cap-weighted thô | 2,028 | 2007-03 | 19,4 | −0,046 | 48,3 | *69,6* |
| P/B trung vị EW | 1,511 | 2007-03 | 19,4 | −0,005 | 33,8 | 39,5 |
| **EV/EBITDA capped-10%** | **11,49** | 2009-05 | 17,2 | −0,583 | **24,4** | *56,8* |
| EV/EBITDA cap-weighted | 13,59 | 2009-05 | 17,2 | −1,055 | 45,9 | *72,9* |
| EV/EBITDA trung vị EW | 10,56 | 2009-05 | 17,2 | −0,912 | 28,4 | *58,0* |
| **CAPE-5Y** | **15,63** | 2011-09 | 14,9 | **+0,594** | *59,9* | **12,3** |
| **CAPE-7Y** | **16,98** | 2013-07 | 13,1 | **+0,600** | *60,1* | **18,1** |
| **CAPE-10Y** | **18,84** | 2016-03 | 10,3 | **+0,519** | *70,7* | 43,3 |
| Earnings yield (1/PE cap10) | 8,63% | 2007-03 | 19,4 | −0,082 | 76,9 *(cao=rẻ)* | 84,1 |
| **ERP** (ey − huy động 6,80%) | **+1,83pp** | 2011-01 | 15,6 | +0,203 | 70,1 *(cao=rẻ)* | 43,3 |

*(Chữ nghiêng = con số bị lật bởi lựa chọn khử-xu-hướng; xem §1.3.)*
Biểu đồ: [`valuation_framework_20260729.png`](valuation_framework_20260729.png)

### 1.3 Phát hiện quan trọng nhất: **xu hướng cơ học nuốt trọn tín hiệu**

CAPE **trôi lên +0,59/năm** (R² = 0,35 chỉ với biến thời gian; bình quân đầu kỳ 7,76 → cuối kỳ 17,29).
Đây không phải thị trường đắt dần — đây là **cơ chế của chính công thức**: mẫu số là bình quân lợi nhuận
thực **quá khứ** N năm, mà lợi nhuận thực VN tăng trưởng nhanh, nên mẫu số luôn tụt hậu so với tử số.
Mỹ có 140 năm để xu hướng này trở thành nhiễu nhỏ; **VN có 10–15 năm, xu hướng LỚN HƠN tín hiệu.**

Hệ quả trực tiếp, và đây là câu trả lời cho lo ngại gốc của user ("PE rẻ vì E ở đỉnh chu kỳ"):

- **Đọc CAPE thô** → phân vị 60–71 → "thị trường KHÔNG rẻ, PE rẻ đúng là ảo giác chu kỳ".
- **Đọc CAPE đã khử xu hướng** → phân vị **12,3 / 18,1 / 43,3** → "thị trường RẺ, khớp với PE/PB".
- Hai cách đọc **trái ngược nhau**, và **không có cách nào trong 13 năm dữ liệu để phân xử**.

Điều tương tự xảy ra ngược chiều với EV/EBITDA (trôi **−0,58/năm**): thô 24,4 (rẻ) → khử xu hướng 56,8
(trung tính), và với P/B (33,6 → 59,2). **Chỉ P/E là không trôi** (−0,002/năm, p=0,87 — phân vị 23,1 vs
23,3, gần như đồng nhất). Đây là lý do kỹ thuật khiến P/E là chỉ số cấp-index duy nhất mà phân vị lịch
sử VN đọc được nguyên trạng mà không cần giả định mô hình nào.

> **Kết luận §1.3:** thêm lăng kính định giá **không giảm mơ hồ, nó thêm một tham số ẩn** (khử xu hướng
> hay không) mà dữ liệu VN không đủ để xác định. Bất kỳ ai trích dẫn "CAPE VN ở phân vị X" **phải** nói
> rõ đã khử xu hướng hay chưa, nếu không con số vô nghĩa.

### 1.4 Đa cộng tuyến — áp đúng quy trình Phụ lục A.4.1

Hồi quy log-log chỉ số mới ~ log(PE) + log(PB), **trên chuỗi đã khử xu hướng** (nếu để nguyên xu hướng,
phần "mới" chỉ là xu hướng, không phải thông tin):

| Chỉ số mới | N | R²\|PE | R²\|PB | **R²\|PE+PB** | Thông tin còn MỚI |
|---|---|---|---|---|---|
| CAPE-5Y | 3.710 | 0,764 | 0,934 | **0,935** | **7%** |
| CAPE-7Y | 3.260 | 0,687 | 0,891 | **0,902** | **10%** |
| CAPE-10Y | 2.585 | 0,523 | 0,820 | **0,851** | **15%** |
| EV/EBITDA cap10 | 4.119 | 0,009 | 0,003 | 0,094 | **91%** |
| ERP | 3.882 | 0,195 | 0,333 | 0,369 | **63%** |

**CAPE rơi đúng vào bẫy Phụ lục A**: sau khi khử xu hướng, nó là **biến đổi tuyến tính của P/B**
(R² 0,82–0,93) — cùng dạng vấn đề với ROE = PB/PE, chỉ khác là quan hệ thống kê chứ không phải đồng
nhất thức đại số. **Không phải biến độc lập.**

EV/EBITDA **thật sự trực giao** (91% mới) — nhưng xem sức dự báo:

| Biến | ρ(f6M) | ρ(f12M) | R²hiệu chỉnh (f12M, một mình, đã khử xu hướng) |
|---|---|---|---|
| **P/B capped-10%** | **−0,357** | **−0,587** | **+0,395** |
| P/E capped-10% | −0,249 | −0,439 | +0,324 |
| CAPE-7Y | −0,371 | −0,518 | +0,299 |
| CAPE-10Y | −0,515 | −0,749 | +0,530 *(chỉ 10,3 năm dữ liệu)* |
| ERP | +0,338 | +0,393 | +0,135 |
| **EV/EBITDA cap10** | −0,140 | −0,172 | **+0,017** |

EV/EBITDA = **trực giao nhưng gần như vô thông tin** — nhiễu độc lập, không phải góc nhìn mới.
CAPE-10Y có số đẹp nhất nhưng chỉ có **10,3 năm** (≈10 quan sát độc lập ở horizon 12M) và 85% phương sai
của nó đã nằm trong PE+PB.

### 1.5 Composite z-score — **NO-GO**

Điều kiện tiền đề của dispatch ("chỉ tính nếu ≥2 chỉ số độc lập thật sự sống sót") **không thoả**, nhưng
đã tính để có bằng chứng số thay vì lập luận suông. Composite = trung bình z (đã khử xu hướng) của
{PE cap10, PB cap10, CAPE-7Y, ERP đảo dấu}, N = 3.260 phiên (13,1 năm).

Ma trận tương quan các thành phần (đã khử xu hướng):

|  | PE | PB | CAPE7 | ERP |
|---|---|---|---|---|
| PE | 1,00 | 0,92 | 0,83 | 0,88 |
| PB | 0,92 | 1,00 | **0,95** | 0,85 |
| CAPE7 | 0,83 | 0,95 | 1,00 | 0,79 |
| ERP | 0,88 | 0,85 | 0,79 | 1,00 |

Không có cặp nào dưới 0,79. Sức dự báo: composite ρ(f6M) = **−0,319** / ρ(f12M) = **−0,443**, so với
**P/B đơn lẻ −0,331 / −0,473**. **Composite THUA P/B đơn lẻ ở cả hai horizon** — gộp 4 chỉ số tương quan
0,8–0,95 chỉ pha loãng chỉ số tốt nhất bằng ba bản sao nhiễu hơn của chính nó.

*(Giá trị composite hiện tại, để tham khảo: **−0,74 z, phân vị 26,2** — thành phần PE −1,15 / PB −0,81 /
CAPE7 −0,90 / ERP −0,10. Nghĩa là "hơi rẻ", nhất quán với §1.2 nhưng KHÔNG thêm thông tin.)*

### 1.6 Buffett Indicator (Market Cap / GDP) — **NGOÀI PHẠM VI**

Đã kiểm tra registry và codebase. Thứ hệ thống có là `gdp_growth_vn.py` (`GDP_ANNUAL`,
CANONICAL) = **tốc độ tăng trưởng GDP THỰC hàng năm %** (World Bank `NY.GDP.MKTP.KD.ZG`) —
**không phải mức GDP danh nghĩa tính bằng VND**, là thứ Buffett Indicator cần ở mẫu số.

Về nguyên tắc có thể dựng lại mức GDP danh nghĩa từ 1 mốc neo + tăng trưởng thực + giảm phát GDP, nhưng
(a) chưa có mốc neo nào trong hệ thống, (b) **giảm phát GDP ≠ CPI** (VN chênh nhau đáng kể), nên việc
đó sẽ là **chế số liệu, không phải đo**. ⇒ Cần nguồn dữ liệu mới (World Bank `NY.GDP.MKTP.CN`) trước khi
tính được. **Không tự chế.** Nếu user muốn, đây là 1 lần fetch WB API + 1 entry registry (việc của
Winston, nhỏ) — nhưng xem §3.1 trước khi bỏ công.

### 1.7 Lợi suất TPCP (trái phiếu chính phủ VN) — **KHÔNG có nguồn thật**

Đã tra `mike/kb/data_registry/macro/` (7 nguồn) và grep toàn codebase. Kết quả:

- **Không có** chuỗi lợi suất TPCP VN nào trong registry hay BQ.
- Thứ duy nhất tồn tại là hằng số `VGB_1Y` hardcode trong `sim_dt4g_improve.py` — **26 giá trị bình quân
  năm tự ước lượng bằng tay** ("approx annual avg" theo chính comment của file), **không có trong
  registry**, không có nguồn, không refresh. **Không đủ tư cách làm input ERP chuẩn tắc** (đúng quy tắc
  coding_guidelines §9: nguồn không có trong registry ⇒ không mặc định an toàn).
- ⇒ **Giữ lãi suất huy động Big4-12M-online làm proxy** (`deposit_rate_vn.py`, CANONICAL-PROXY,
  26 mốc neo 2011→2026 + CSV append-only).

**Giới hạn phải nói rõ khi trích ERP**: mẫu số là **hàm bậc thang 26 mốc trong 15,6 năm**, tức ERP thay
đổi phần lớn do earnings yield chứ không do lãi suất; và lãi huy động ≠ lãi phi rủi ro (có phần bù rủi
ro ngân hàng + trần/sàn hành chính SBV thời 2011–2013). Đây là lý do ERP chỉ nên đọc theo **hướng và
mức thô** ("dương mỏng" vs "âm" vs "dương rộng"), không đọc phân vị lẻ.

---

## 2. VIỆC 2 — Định giá lúc CAPIT fire có tương quan chất lượng kết quả không?

### 2.1 Tái lập danh sách sự kiện

Không có artifact nào đủ dài để dùng lại: `data/capit_event_elig_full.csv` chỉ có 12 sự kiện 2014→2026-03
(dừng trước lần fire LIVE 07-20). Nên đã **tái lập đúng luật production** từ
`pt_v23_audit_2014.py:1079-1086`:

```
ngày washout = ≥ WASHOUT_GATE (0,30) tỷ lệ ticker_prune có D_RSI < 0,3
sự kiện      = ngày ĐẦU TIÊN của cụm; các cụm cách nhau ≥ 30 ngày lịch
```

Mở rộng lùi về **2009-05** (ngày đầu tiên `ticker_prune` có ≥100 mã — ngưỡng breadth có nghĩa theo
CLAUDE.md) thay vì chỉ 2014+ như backtest, để tăng N. **Kết quả: 134 phiên washout → 26 sự kiện**
(19 trong cửa sổ 2014+).

**Kiểm chứng đối chiếu artifact cũ** (`capit_event_elig_v21c.csv`, 14 sự kiện 2014→2026-03):
**14/14 đều có sự kiện tương ứng** trong danh sách này — 8 khớp **đúng ngày**, 5 lệch 1–2 ngày,
1 lệch 5 ngày (2022-06-20 ↔ 2022-06-15). **Lần fire LIVE 2026-07-20 được tái lập chính xác.**
Chiều ngược lại có **4 sự kiện artifact cũ KHÔNG có**: 2015-05-18, 2018-07-05, 2020-02-03,
2020-07-27 — cả 4 đều hợp lệ dưới luật cụm ≥30 ngày (cách sự kiện liền kề 37–38 ngày trở lên).
Nguyên nhân chênh lệch **chưa xác minh**: file `*_elig_*.csv` là artifact **rổ đủ điều kiện** (một
sự kiện không có mã nào qua bộ lọc chất lượng sẽ không sinh dòng nào), không phải danh sách sự kiện
chuẩn tắc; cộng thêm khác vintage gate/universe. Coi 4 sự kiện này là **phần mở rộng chưa được đối
chiếu chéo**, và §2.5 (LOO bỏ từng sự kiện) cho thấy không sự kiện đơn lẻ nào đảo dấu kết luận.

### 2.2 Bảng 26 sự kiện — định giá **nhân quả** tại ngày fire + kết cục forward

Phân vị định giá dùng ở đây là **phân vị mở rộng (expanding), NHÂN QUẢ**: chỉ so với lịch sử **trước**
ngày đó, burn-in 750 phiên (~3 năm) — không nhìn tương lai. `ovs` = % ticker_prune quá bán,
`mdd12M` = sụt sâu nhất của VNINDEX trong 252 phiên sau sự kiện.

| Sự kiện | ovs% | dd52w | P/B cap10 | **%ile P/B** | P/E cap10 | %ile P/E | EV/EB | %ile | r3M | r6M | r12M | mdd12M |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2009-12-10 | 40,7 | −26,5 | 2,2 | *(burn-in)* | 12,4 | — | — | — | +11,4 | +11,4 | +6,8 | −7,6 |
| 2010-08-09 | 41,1 | −24,3 | 2,2 | 31,9 | 11,1 | 29,1 | 25,4 | 0,0 | −3,3 | +8,8 | −18,7 | −18,8 |
| 2010-10-20 | 38,2 | −29,1 | 2,0 | 24,1 | 10,6 | 25,7 | 23,4 | 2,2 | +12,5 | +6,1 | −7,4 | −13,2 |
| 2011-02-21 | 41,9 | −12,0 | 2,0 | 19,4 | 10,2 | 17,5 | 19,8 | 0,0 | −20,1 | −16,1 | −12,4 | −30,4 |
| 2011-04-21 | 31,9 | −16,2 | 1,8 | 15,4 | 9,4 | 12,4 | 17,6 | 0,0 | −10,3 | −12,9 | +1,1 | −26,8 |
| 2011-11-14 | 35,9 | −25,0 | 1,3 | **1,7** | 7,9 | 5,1 | 23,1 | 16,4 | +3,0 | +14,4 | −1,0 | −14,0 |
| 2012-08-23 | 42,9 | −19,5 | 1,6 | 22,6 | 9,1 | 21,2 | 17,4 | 3,9 | −2,3 | +18,6 | +20,5 | −4,5 |
| 2014-05-08 | 52,5 | −13,2 | 1,7 | 32,7 | 12,2 | 59,7 | 7,4 | 13,6 | +15,3 | +13,5 | +2,0 | −2,5 |
| 2015-05-18 | 31,1 | −17,4 | 1,7 | 26,1 | 12,0 | 49,9 | 32,5 | 89,3 | +12,3 | +14,1 | +17,7 | −1,3 |
| 2015-08-24 | 44,7 | −17,8 | 1,6 | 22,8 | 10,8 | 36,0 | 7,5 | 15,1 | +14,7 | +6,8 | +25,4 | −1,0 |
| 2016-01-18 | 44,4 | −17,6 | 1,6 | 18,9 | 10,9 | 35,0 | 30,9 | 86,8 | +12,6 | +23,5 | +29,8 | −0,9 |
| **2018-05-28** | 41,5 | −22,6 | 2,8 | **86,0** | 18,5 | 87,1 | 12,7 | 42,8 | +6,0 | −1,0 | +3,0 | −5,7 |
| **2018-07-05** | 31,2 | −25,3 | 2,5 | **79,1** | 17,4 | 85,5 | 12,3 | 40,9 | +13,5 | −0,9 | +8,3 | −2,4 |
| 2020-02-03 | 35,2 | −9,4 | 2,1 | 55,6 | 14,0 | 57,6 | 11,0 | 27,3 | −17,7 | −14,0 | +18,2 | −29,0 |
| 2020-03-11 | 32,8 | −20,8 | 1,9 | 44,7 | 12,5 | 39,8 | 9,0 | 21,8 | +6,9 | +9,6 | **+45,6** | −18,8 |
| 2020-07-27 | 39,2 | −23,4 | 1,8 | 33,0 | 12,4 | 38,4 | 11,2 | 29,0 | +22,4 | **+48,3** | **+62,6** | 0,0 |
| **2022-04-19** | 38,3 | −8,0 | 2,6 | **78,1** | 15,3 | 61,3 | 15,3 | 56,4 | −16,2 | **−24,4** | **−25,4** | **−35,2** |
| 2022-06-15 | 30,3 | −20,6 | 2,2 | 54,8 | 12,5 | 34,6 | 12,9 | 36,6 | +2,2 | −15,0 | −8,9 | −24,9 |
| 2022-09-28 | 35,5 | −25,2 | 2,0 | 43,8 | 11,5 | 23,7 | 11,6 | 27,0 | −13,9 | −6,9 | +1,0 | −20,3 |
| 2023-10-30 | 31,5 | −16,3 | 1,6 | 11,2 | 11,5 | 25,9 | 11,0 | 25,9 | +12,8 | +19,8 | +20,4 | −1,4 |
| 2024-04-17 | 30,1 | −7,5 | 1,8 | 29,5 | 13,7 | 53,8 | 13,2 | 45,8 | +6,0 | +7,7 | +1,5 | −8,3 |
| 2024-08-05 | 35,6 | −8,7 | 1,8 | 27,5 | 13,4 | 48,6 | 14,2 | 55,1 | +4,8 | +7,3 | +33,4 | −7,9 |
| 2025-04-03 | 52,5 | −8,0 | 1,7 | 18,1 | 12,3 | 34,5 | 13,1 | 42,0 | +14,0 | +37,9 | +41,2 | −11,0 |
| 2025-10-20 | 33,3 | −7,4 | 2,1 | 58,7 | 14,9 | 65,1 | 15,0 | 59,8 | +15,9 | +14,3 | *đang chạy* | −3,4 |
| 2026-03-09 | 43,8 | −13,1 | 2,0 | 53,0 | 13,2 | 44,2 | 13,3 | 42,3 | +8,5 | *đang chạy* | — | −3,7 |
| **2026-07-20** (LIVE) | 45,9 | −9,6 | 1,9 | **43,6** | 12,2 | 30,9 | 11,9 | 29,1 | *đang chạy* | — | — | −4,3 |

Biểu đồ tán xạ: [`capit_valuation_20260729.png`](capit_valuation_20260729.png)

### 2.3 Kết quả thống kê

**(a) Tương quan hạng Spearman, toàn bộ họ phép thử** (7 chỉ số × 2 cách tính phân vị × 4 kết cục
= **56 phép thử**, khai báo trước khi diễn giải):

| Xếp hạng | Biến | Kết cục | N | ρ | p thô | Qua BH? |
|---|---|---|---|---|---|---|
| 1 | P/B cap-weighted, %ile mở rộng | r6M | 23 | **−0,549** | 0,0066 | ✗ |
| 2 | P/B cap-weighted, %ile 3Y | r12M | 23 | −0,531 | 0,0091 | ✗ |
| 3 | P/B capped-10%, %ile 3Y | r12M | 23 | −0,445 | 0,0332 | ✗ |
| 4 | **P/B capped-10%, %ile mở rộng** | **r6M** | 23 | **−0,424** | 0,0438 | ✗ |
| … | | | | | | |

**0/56 qua Benjamini-Hochberg(0,05). 0/56 qua Bonferroni.** Ngưỡng BH cho phép thử tốt nhất là
0,00089; p thô của nó là 0,0066 — **thiếu 7 lần**.

**(b) Chia đôi rẻ/không-rẻ** (permutation test 20.000 hoán vị, 16 tổ hợp): **0/16 qua BH**. Kết quả gợi ý
mạnh nhất: P/B cap10 → r6M, nhóm rẻ trung vị **+10,9%** vs nhóm không-rẻ **−0,9%** (Δ = 11,8pp,
p thô = 0,069).

**(c) Tercile theo phân vị P/B (nhân quả)** — bảng mô tả, dễ đọc nhất:

| Nhóm | N | %ile P/B trung vị | r3M | r6M | r12M | mdd12M |
|---|---|---|---|---|---|---|
| **RẺ nhất** | 9 | 18,9 | **+12,5** | **+14,4** | **+20,4** | −11,0 |
| giữa | 8 | 32,3 | +6,0 | +8,8 | +2,0 | −6,1 |
| **ĐẮT nhất** | 8 | 57,2 | +6,4 | **−1,0** | +5,6 | −12,2 |

*(r12M nhóm RẺ: trung vị +20,4%, **CI90 bootstrap −1,0% … +25,4%** (N=9) — khoảng tin cậy chạm 0.)*

**(d) Dấu ngược nhau giữa P/B và P/E — và đây là một phát hiện có ý nghĩa kinh tế, không phải nhiễu:**
P/B rẻ → forward tốt (ρ âm), nhưng P/E **cao** → forward tốt (ρ +0,32 với r3M). Cách đọc nhất quán duy
nhất: tại đáy washout, lợi nhuận E đang bị nén, nên **P/E cao chính là dấu hiệu đáy chu kỳ lợi nhuận**,
còn P/B (mẫu số là vốn chủ, ổn định hơn nhiều qua chu kỳ) mới đo được "rẻ" thật. **Đây chính xác là cơ
chế mà Phụ lục A.5 đã cảnh báo, quan sát ở chiều ngược lại.** Hệ quả thực hành: **một composite "định
giá rẻ" gộp PE và PB sẽ TỰ MÂU THUẪN ở đúng thời điểm CAPIT fire** — thêm một lý do độc lập bác §1.5.

### 2.4 Điểm khác biệt CỐT LÕI so với ROE: **không đa cộng tuyến với thứ hệ thống đã dùng**

Luật sizing CAPIT hiện tại đã dùng: DT5G state, `dd52w`, `grind`, breadth `oversold`. Nếu phân vị P/B chỉ
là biến thể của những thứ đó thì không có gì mới (bẫy Phụ lục A.4.1). Kiểm tra:

| Cặp | ρ Spearman | p | N |
|---|---|---|---|
| %ile P/B ~ **dd52w** | **+0,006** | 0,977 | 25 |
| %ile P/B ~ **breadth oversold** | −0,167 | 0,425 | 25 |
| %ile P/E ~ dd52w | +0,300 | 0,145 | 25 |
| %ile EV/EBITDA ~ dd52w | +0,407 | 0,043 | 25 |

**ρ = +0,006 với dd52w là gần như trực giao hoàn hảo.** Phân vị P/B tại ngày fire **KHÔNG** phải cách nói
khác của "washout sâu hay nông" — nó đo chiều thật sự mới. Kiểm chứng bằng tương quan riêng phần (khử
dd52w + oversold): ρ(P/B, r6M) từ −0,424 thô → **−0,392 riêng phần** (p = 0,064), tức tín hiệu **không bị
hấp thụ** bởi các biến hệ thống đã có. Hồi quy tăng dần: R²hiệu chỉnh cho r6M từ +0,054 (dd52w+ovs) →
**+0,165** khi thêm %ile P/B.

**Đây là khác biệt then chốt so với kết luận ROE (Phụ lục A.4.1), nơi biến mới là đồng nhất thức của biến
cũ. Ở đây biến mới thật sự mới — vấn đề duy nhất là cỡ mẫu.**

### 2.5 Độ bền — **năm 2022 gánh phần lớn**

| Mẫu | Kết cục | N | ρ | LOO bỏ 1 sự kiện (min…max) | Bỏ nguyên năm xấu nhất |
|---|---|---|---|---|---|
| 2009+ | r6M | 23 | −0,424 | −0,528 … −0,356 | bỏ 2022 → **−0,289** |
| 2009+ | r12M | 22 | −0,118 | −0,206 … −0,013 | bỏ 2022 → **+0,107** *(đảo dấu)* |
| 2009+ | mdd12M | 25 | −0,101 | −0,184 … −0,011 | bỏ 2022 → **+0,099** *(đảo dấu)* |
| **2014+ (production)** | r6M | 17 | **−0,625** *(p=0,007)* | −0,715 … −0,576 | bỏ 2022 → −0,543 |
| 2014+ | r12M | 16 | −0,462 *(p=0,072)* | −0,571 … −0,386 | bỏ 2022 → −0,280 |
| 2014+ | mdd12M | 19 | −0,435 *(p=0,063)* | −0,538 … −0,370 | bỏ 2022 → −0,300 |

Đọc đúng: **bỏ bất kỳ MỘT sự kiện nào cũng không đảo dấu** (tốt); nhưng **bỏ nguyên năm 2022 làm r12M và
mdd12M của mẫu đầy đủ đảo dấu** (xấu) — đúng pattern "1–2 năm gánh hết edge" mà chuẩn multiple-testing của
đội (KNOWLEDGE §Quy chuẩn 5) yêu cầu kiểm và coi là cờ đỏ. Trong cửa sổ production 2014+, dấu giữ nguyên
sau khi bỏ 2022 nhưng yếu đi ~35–50%.

Sự kiện **2022-04-19** là quan sát có đòn bẩy lớn nhất: %ile P/B 78,1 (đắt nhất nhóm), r12M **−25,4%**,
mdd12M **−35,2%** — đúng một lần "washout kỹ thuật khi định giá chưa rẻ" và nó là thảm hoạ. Hai sự kiện
2018 (%ile 86,0 và 79,1) cùng dấu nhưng biên độ nhỏ (r6M −1,0 / −0,9). Nói cách khác **giả thuyết được
chống đỡ bởi 3 quan sát đắt-tiền, mà 1 trong 3 chiếm phần lớn hiệu ứng.**

### 2.6 Cỡ mẫu — nói thẳng như dispatch yêu cầu

**N = 26 sự kiện tổng, 19 trong cửa sổ production, 16–23 có kết cục đầy đủ.** Ở cỡ này, sức mạnh thống kê
để phát hiện |ρ| = 0,4 ở α = 0,05 (hai phía) là **~50%** — tức ngay cả khi hiệu ứng CÓ THẬT đúng độ lớn
đó, một nửa số lần chạy sẽ không phát hiện được. Và vì đây là phép thử thứ 56 trong một họ, chuẩn đúng
không phải α = 0,05 mà là **~0,0009**, cần |ρ| ≈ 0,63 ở N = 23 mới đạt. **Chưa có cách nào để 26 sự kiện
trong 17 năm trả lời dứt khoát câu hỏi này** — và điều đó **không** sẽ thay đổi bằng cách phân tích khéo
hơn; chỉ thay đổi bằng cách chờ thêm sự kiện (~1,5 sự kiện/năm ⇒ cần ~15 năm nữa để N gấp đôi).

**Đây là kết quả có giá trị**: biết trước rằng câu hỏi này không thể trả lời bằng dữ liệu quá khứ VN
tốt hơn không biết. Nó chuyển bài toán từ "tìm bằng chứng" sang "quyết định dưới bất định đã đo".

### 2.7 Sự kiện đang sống: CAPIT fire 2026-07-20

Chỉ mô tả, **không phải khuyến nghị** (xem §3.3): lần fire hiện tại có %ile P/B **43,6** — thuộc nhóm
**"giữa"**, không phải nhóm rẻ (≤~29) cũng không phải nhóm đắt (≥~55). %ile P/E 30,9 và EV/EBITDA 29,1
nằm ở nửa dưới. Nhóm "giữa" lịch sử có r6M trung vị +8,8% / r12M +2,0% (N = 8). Với các con số ở §2.5–2.6,
**không có cơ sở thống kê để đề xuất thay đổi size của lần fire này**, và §3.3 giải thích tại sao dù có
cũng không nên làm giữa chừng một đợt đang giải ngân.

---

## 3. VIỆC 3 — Đề xuất: có nên xây gì tiếp, và xây ở đâu

### 3.1 Việc 1 — chỉ giữ giá trị MÔ TẢ, không xây gì

Giống hệt kết luận đã chốt cho ROE ở Phụ lục A.6:

- **KHÔNG** wire CAPE — sau khử xu hướng nó là biến đổi của P/B (R² 0,82–0,93), và phân vị của nó phụ
  thuộc hoàn toàn vào lựa chọn khử-xu-hướng (§1.3).
- **KHÔNG** wire EV/EBITDA — trực giao nhưng R²hiệu chỉnh +0,017, tức trực giao với cả kết cục.
- **KHÔNG** wire composite — thua P/B đơn lẻ, và tự mâu thuẫn tại washout (§2.3d).
- **KHÔNG** bỏ công fetch GDP danh nghĩa cho Buffett Indicator **trừ khi user muốn riêng cho mục đích
  mô tả/truyền thông**: nó là một tỷ số cấp-index nữa với cùng vấn đề mẫu ngắn + xu hướng cơ học mạnh
  (mcap/GDP của một thị trường đang chứng khoán-hoá luôn trôi lên) — gần như chắc chắn lặp lại §1.3.
- **CÓ**, dùng để **mô tả trong báo cáo**: câu đáng đưa vào báo cáo định kỳ là *"CAPE-5/7Y thô ở phân vị
  60 nhưng gần như toàn bộ mức đó là trôi cơ học; khử xu hướng còn 12–18, nhất quán với P/E 23 và P/B
  robust 34"* — nghĩa là **lăng kính cơ bản KHÔNG mâu thuẫn với kết luận "rẻ" của Phụ lục B**, và lo ngại
  gốc của user (PE rẻ giả vì E đỉnh chu kỳ) **không được số liệu CAPE xác nhận** ở bất kỳ cách đọc nào
  ngoài cách đọc thô đã biết là chệch.

**Về ý tưởng "khai thác divergence giữa lăng kính kỹ thuật và cơ bản"**: dữ liệu nói rằng ở thời điểm này
**không có divergence để khai thác** — DT5G (kỹ thuật/momentum) đang thận trọng, còn lăng kính cơ bản, khi
đo cho đúng, cũng nói "rẻ vừa phải, không phải cơ hội thế hệ". Divergence THẬT trong mẫu 17 năm chỉ xuất
hiện ở đúng 3 lần (2018×2, 2022-04: kỹ thuật báo washout ⟷ định giá vẫn đắt) — và §2.5 cho thấy 3 quan
sát không đủ để xây luật.

### 3.2 Việc 2 — **ĐỀ XUẤT DUY NHẤT: shadow-log, không phải tilt**

**KHÔNG đề xuất tilt sizing bây giờ.** Lý do gộp lại: 0/56 qua BH; 2022 gánh phần lớn r12M/mdd; N = 26 và
không thể tăng nhanh. Wire một tilt bây giờ sẽ vi phạm chính chuẩn DSR/PBO của đội (KNOWLEDGE §Quy chuẩn 5)
ngay ở bước khai báo N trials.

**Nhưng cũng không nên vứt bỏ**, vì §2.4: biến này **trực giao với mọi thứ luật CAPIT đang dùng** — đây là
điều mà ROE, và cả CAPE/EVEB/composite ở Việc 1, đều không đạt. Đề xuất tương xứng với bằng chứng:

> **Ghi shadow-log phân vị định giá tại MỖI lần CAPIT fire** — 1 dòng CSV, `WARN_ONLY`, không chặn,
> không đổi size, không đụng tiền. Ghi: ngày fire, `pb_cap10` + %ile mở rộng nhân quả, `pe_cap10` + %ile,
> `eveb_cap10` + %ile, `oversold`, `dd52w`, state DT5G, size thực tế đã dùng. Đúng khuôn mẫu **P0
> buying-power shadow** đã chạy từ 2026-07-29 (`data/plan_buying_power_shadow_log.csv`) — cơ chế đã có,
> đã được user chấp nhận về hình thức, chi phí gần bằng 0.

Vị trí trong kiến trúc: nơi `pt_v23_audit_2014.py:1122` / `golive_recommend_v23.py` đã tính xong
`capit_events` — thêm một lần ghi, **không** thêm điều kiện. Không cần `constraints.py`/registry (đúng
quyết định user 2026-07-29: chỉ đáng xây khi có ≥3 rule tường minh cùng lúc).

**Điều kiện để bàn lại chuyện tilt** (pre-register ngay bây giờ để tránh chọn ngưỡng sau khi thấy dữ liệu):
- N ≥ 35 sự kiện có kết cục 12M đầy đủ (hiện 22 ⇒ cần ~8–10 năm nữa), **HOẶC**
- ≥ 5 sự kiện MỚI (post-2026-07) rơi vào nhóm %ile P/B > 55 để mẫu "đắt" có N ≥ 8 độc lập với 2018/2022.
- Khi đó: chạy lại đúng 56 phép thử này (không mở rộng họ), yêu cầu qua BH, **kèm** LOO theo năm không đảo
  dấu, **kèm** DSR ≥ 0,95 trên NAV của config có tilt, rồi mới route qua quant-skeptic.

Nếu đến lúc đó tín hiệu đứng vững, hình dạng tilt hợp lý nhất — ghi lại để khỏi phải nghĩ lại, **KHÔNG
phải đề xuất triển khai**: *khi CAPIT fire mà %ile P/B nhân quả > ~55, nhân size với ~0,5* (dạng SHRINK
phòng thủ, giống `EW2D_SHRINK`/`postbull_mult` đã có sẵn trong `capit_base` — không cần cơ chế mới), và
**không** tăng size khi rẻ (bất đối xứng: bằng chứng ở phía "đắt thì tệ" mạnh hơn phía "rẻ thì tuyệt", và
tăng size là hành động không thể đảo ngược bằng tiền thật).

### 3.3 Ranh giới rõ ràng của job này

- **Không code, không wire, không đụng `trading_rules.json`.** Toàn bộ là research.
- **Không đổi gì cho đợt CAPIT đang giải ngân (fire 07-20)** — kể cả nếu tilt được duyệt sau này, áp một
  luật sizing mới vào giữa một đợt đang chạy dở là đúng loại thay-đổi-giữa-chừng mà đội đã cấm.
- Báo cáo này **không cần quant-skeptic** (chỉ mô tả + NO-GO). **Cần** quant-skeptic nếu sau này ai muốn
  lật NO-GO này thành GO.

---

## 4. Giới hạn phương pháp (đọc trước khi trích dẫn)

1. **Rổ top-100 vốn hoá**, không phải toàn thị trường — khớp Phụ lục B để so sánh được. Rổ toàn bộ cho
   mức khác vài %, không đổi kết luận.
2. **Tái lập P/B khớp Phụ lục B tới sai số tuyệt đối TB 0,0007** (max 0,021 trên 4.631 phiên chồng lấn);
   `pb_cap10` 0,0006; trung vị EW 0,0017. **P/E lệch 0,106 TB (0,8%)** vì rổ P/E ở đây = top-100 có PE>0,
   còn Phụ lục B lấy top-100 có PB>0 rồi mới lọc PE — định nghĩa ở đây sạch hơn, chênh lệch không đổi
   kết luận nào.
3. **CAPE phụ thuộc chuỗi CPI**: 2011+ dùng `cpi_vn.py` (Tier-2 proxy nội suy cho 2011→2025-05, Tier-1
   NSO thật chỉ 2025-06→2026-06); 2007–2010 dùng 4 mốc bình quân năm tra WebSearch. Sai số vài phần mười
   %/năm không đổi kết luận §1.3 (xu hướng +0,59/năm lớn hơn nhiều bậc), nhưng **không** dùng CAPE ở đây
   cho bất kỳ so sánh cấp lẻ nào.
4. **`EBITDA_P0` là số quý hiện tại**, gộp EV/EBITDA chỉ số bằng ΣEV/ΣEBITDA giả định `EVEB` của vendor
   dùng cùng định nghĩa EBITDA — chưa kiểm chứng độc lập. Đây là lý do phụ để không tin EV/EBITDA cấp-index
   quá mức (lý do chính vẫn là R²hiệu chỉnh +0,017).
5. **Phân vị mở rộng có burn-in không đều**: sự kiện 2009-12 bị loại (chưa đủ 750 phiên), các sự kiện
   2010–2012 so với lịch sử chỉ 3–5 năm. Đã báo song song bản `%ile 3Y` trượt; kết luận không đổi
   (bảng §2.3a có cả hai).
6. **Forward return đo trên VNINDEX**, không phải trên NAV rổ CAPIT thật. Rổ CAPIT là 15 mã chất lượng
   xếp theo PB z-score, không phải chỉ số — quan hệ định giá-index → kết quả-rổ có thể khác. Đo trên NAV
   rổ thật là việc lớn hơn (cần replay 26 sự kiện qua `pt_v23_audit_2014.py`), **chỉ đáng làm nếu tín hiệu
   qua được cổng ở §3.2** — làm bây giờ là tăng số phép thử trên cùng 26 quan sát.
7. **`ticker_prune` cho breadth**: cố ý giữ nguyên nguồn mà luật CAPIT production đang dùng (pool + ADV cap
   vẫn ghim `ticker_prune`, chỉ breadth đã cutover sang `universe_pit` với gate 0,31). Danh sách sự kiện ở
   đây tái lập luật gate 0,30/`ticker_prune`; đối chiếu artifact cũ khớp 14/14 (8 đúng ngày, 6 lệch 1–5
   ngày) **và** tái lập đúng lần fire live 07-20 — xem §2.1 về 4 sự kiện mở rộng chưa đối chiếu chéo được.
   **Đã đo độ nhạy gate 0,30 → 0,31** (không chỉ suy luận): **vẫn đúng 26 sự kiện**, chỉ 2 sự kiện dịch
   2 ngày (2022-06-15→06-17, 2024-04-17→04-19; cả hai dịch về **gần hơn** với artifact cũ). Chưa chạy
   lại trên mẫu số `universe_pit` (breadth production hiện tại) — đó là thay đổi mẫu số chứ không chỉ
   ngưỡng, và §4.4-KQ của dự án `universe_pit` đã ghi nhận không tồn tại gate bảo toàn hành vi.
8. Không có lợi suất TPCP thật ⇒ ERP là proxy lãi huy động, **hàm bậc thang 26 mốc** (§1.7).

---

## 5. Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude && source wc_env.sh
E=mike/agents/Taylor/exp_valframe
$DNA_PYEXE $E/fetch.py            # BQ: panel top-150 mcap 2007+, breadth ticker_prune, VNINDEX
$DNA_PYEXE $E/build_metrics.py    # chuoi dinh gia cap-index + tu kiem chung voi Phu luc B
$DNA_PYEXE $E/viec1.py            # CAPE/ERP/EVEB + phan vi + da cong tuyen tho
$DNA_PYEXE $E/viec1b.py           # troi co hoc + suc du bao tang them
$DNA_PYEXE $E/viec1c.py           # khu xu huong
$DNA_PYEXE $E/viec1d.py           # da cong tuyen sau khu xu huong + composite
$DNA_PYEXE $E/capit_events.py     # 26 su kien CAPIT + dinh gia nhan qua + forward
$DNA_PYEXE $E/capit_stats.py      # 56 phep thu Spearman + BH/Bonferroni + chia doi permutation
$DNA_PYEXE $E/capit_incr.py       # da cong tuyen voi dd52/breadth + tuong quan rieng phan
$DNA_PYEXE $E/capit_loo.py        # LOO su kien / LOO nam
$DNA_PYEXE $E/final_numbers.py    # bang tom tat + 2 chart
```

Dữ liệu trung gian: `exp_valframe/{metrics_daily,metrics_full,capit_events_gate0.3,viec1_summary,
viec1_percentiles,capit_stats_spearman,capit_stats_split,composite}.csv`.
Chart: `research/valuation_framework_20260729.png`, `research/capit_valuation_20260729.png`.

*Ghi chú dictionary*: `CLAUDE.md` liệt kê `EPS` và `PS` trong nhóm cột financial của `tav2_bq.ticker` —
**hai cột này KHÔNG tồn tại** trong schema thật (đã kiểm bằng `bq show --schema`). Có `PB, PE, PCF, EVEB,
BVPS, OShares`. Nên sửa dictionary khi tiện.
