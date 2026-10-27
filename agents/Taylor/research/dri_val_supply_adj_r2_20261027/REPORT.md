# DRI — định giá lại lần 2, sửa các lỗi skeptic chỉ ra (job `Taylor_20261027_093047`, 27/10/2026)

> Chỉ nghiên cứu: không lệnh, không pin. Lưới khai trước trong `PREREG.md` (commit `eb3be59b0`, md5 `6cb5187a…`), commit
> trước khi chạy số. `python3 model.py` → `out.txt` (md5 `6fe09ded…`, giống hệt dưới `env -u TZ` và `TZ=America/New_York`).
> Nguồn mới: BCTN 2025 và BCTN 2024 của DRI (trích nguyên văn ở `src/`), Wendy (legal-vn) về thuế Lào.
> Nhãn: [BCTC3] · [BCTN24]/[BCTN25] · [BQ] · [FEED] · [WENDY] · [UL] giả định chưa có nguồn · [NỀN].
> **Đây là bản để skeptic phản biện tiếp, không phải kết luận chốt.**

## 0. Trả lời thẳng
**Selfcheck:** trong `model.py` mới tái lập đúng **10.878 / 11.031** (model_q3) và **14.301** (bản trước), rồi mới đổi tham số.

**(1) FV theo từng mức RSS3 giữa chu kỳ** (đ/cp, trọng số đường giá 60/40; ngoặc = 14.700 so FV) [out mục 3]:
| | mid 1,865 | mid 1,97 | mid 2,075 | mid 2,18 |
|---|---|---|---|---|
| **Tâm** (k 0,3 · C_ref 32 · sản lượng −2%/năm từ 2035 · phí Lào 10% · haircut 15%) | **11.061** (+33%) | **12.481** (+18%) | **13.901** (+6%) | **15.321** (−4%) |
| Cùng tâm, hàm cũ k = 0 (dốc 248) | 9.540 (+54%) | 11.587 (+27%) | 13.635 (+8%) | 15.682 (−6%) |
| Lưới khai trước, k chọn: P10 – trung vị – P90 | 9.963 – 11.763 – 13.888 | 11.429 – 13.316 – 15.639 | 12.837 – 14.836 – 17.368 | 14.277 – 16.380 – 19.163 |
| Tỷ lệ ô lưới có FV ≥ 14.700 | 4% | 21% | 53% | 84% |
- Lưới mỗi mid: 1.458 ô = r × C_ref {31; 32; 33} × f × sản lượng × phí Lào × haircut × trọng số. P10/P90 là phân vị của lưới, **không phải xác suất**.
- Trọng số đường giá (80/20 ↔ 40/60) nay chỉ làm FV xê dịch **510–589 đ**. Trước đây nó tạo ra 3.183 đ, nhưng phần đó là do phép ghép.

**(2) Khoảng FV tôi cho là đáng tin nhất dưới lưới đã khai: tâm 12,5–13,9k (mid 1,97–2,075); P10–P90 của hai mid đó là 11,4–17,4k.**
Khoảng này dựa trên một phán đoán, không phải số đo:
- Không lấy **1,865** làm tâm: đây là trung vị danh nghĩa, tính bằng đô-la cũ.
- Không lấy **2,18** làm tâm vì hai lý do. Một, giá DRI thực nhận thấp hơn RSS3 và lệch pha (năm 2024 RSS3 2,275 nhưng DRI chỉ bán được 1.788 USD/t). Hai, model giữ chi phí VND phẳng tới 2054, nên đọc mid theo nghĩa "thực" đã là lạc quan.
- Ai tin mid ≈ trung vị 10 năm **thực** (2,185, CPI [NỀN]) thì đọc cột 2,18. Ai tin mid danh nghĩa thì đọc cột 1,865.

**(3) 14.700 so FV:** cao hơn tâm **+33% / +18% / +6%** ở mid 1,865 / 1,97 / 2,075; thấp hơn **−4%** ở mid 2,18. Trong khoảng ở (2), giá **cao hơn FV 6–18%**.

**(4) Trục nhạy nhất** (đổi một trục quanh tâm, mục 5):
| Trục | Biên độ FV (đ/cp) | Đo hay đoán |
|---|---|---|
| **Mid RSS3 1,865 → 2,18** | **4.259** | ĐOÁN (cơ sở từng mức ở PREREG §1) |
| **C_ref 31 → 33** (thêm 34 thì 3.072) | 2.048 | Mức số ĐO (mục 2), lưới do dispatch chọn |
| Sản lượng: 0 / 2 / 3%/năm từ 2035 | 1.983–2.123 | ĐOÁN, chưa có nguồn |
| Tồn kho vượt 0 / 1.717 / 3.370 t | 1.911–1.935 | 1.717 ĐO [SXKD]; 3.370 chưa xác minh |
| k (truyền giá vào chi phí) 0 / 0,3 / 0,6 | 532–1.788 | Chọn bằng backcast, N = 4 năm |
| r 10 / 12 / 13% | 1.266–1.584 | ĐOÁN |
| Phí chuyển LN Lào 0 / 10% | 960–1.116 | Mức 10% có nguồn; việc đã nằm trong thuế hay chưa thì CHƯA RÕ |
| Q4/26 Bear ↔ Bull | 919 | ước lượng |
| Haircut tiền Lào 0 / 15 / 30% | 806 | ĐOÁN |
| f (tỷ trọng giá vốn cố định) | 620–634 | ĐOÁN, dữ liệu 2024 ngược chiều (mục 2) |
| Trọng số đường giá | 510–589 | Phán đoán của Bobby |
| Đời khai thác L0 / L1 / L2 | 11–30 | — |

## 1. Sửa (a): bỏ phép ghép mid ↔ kịch bản
Mid nay là **một** phân phối dùng chung cho cả hai đường giá. Pha 60/40 của Bobby chỉ quyết định 2027–2028. Cơ sở từng mức:
| Mid | Cơ sở |
|---|---|
| 1,865 | Trung vị danh nghĩa 10 năm |
| 1,97 | Bước lưới |
| 2,075 | Trung vị danh nghĩa 5 năm |
| 2,18 | TB 2025 ≈ trung vị 10 năm thực (2,185) và 5 năm thực (2,179), quy về USD 2025 bằng CPI Mỹ [NỀN/UL] [FEED] |

Cầu nối (mục 6): bỏ ghép làm FV **−2.284** nếu đích là mid 1,97 và **+117** nếu đích là 2,075. Điều này khớp với con số skeptic đã chỉ ra.

## 2. Sửa (b): giá vốn/t và hàm LNST — phát hiện quan trọng nhất
**"33,11" của BCTN không cùng định nghĩa với C trong model.** [BCTN24/25, mục 1]:
- GVHB hợp nhất chia tấn cao su bán (định nghĩa model) = **27,85** (2024) · **30,13** (2025) · **31,48** (9T/26).
- "Giá vốn/t" in trong BCTN là 31,98 (2024) và 33,11 (2025).
- Chênh × tấn = **41,8 tỷ ở cả hai năm** ⇒ số BCTN là "giá thành hàng bán" có cộng chi phí bán hàng (BH ~30,5 tỷ/năm). Văn bản BCTN cũng nói "chi phí quản lý bán hàng tăng, dẫn đến giá thành hàng bán…".
- Model trừ BH+QLDN riêng qua SGA. Vì vậy C 33–34 là **đếm BH hai lần**, khoảng 3 tr/t.

**Hệ quả:**
- C_ref tương đương số đo: 30,45 (hiệu chỉnh khớp LNST 2025) và 30,09 (9T/26 quy về giá 47,24 theo k 0,3).
- Lưới dispatch {31; 32; 33} nằm **cao hơn số đo 0,5–2,9 tr/t**. Mỗi 1 tr/t ≈ 1.024 đ/cp.
- Đối chứng C_cal 30,45 (mục 4): **14.072** ở mid 1,97 và **15.491** ở mid 2,075.
- Tôi **không** chuyển tâm sang 30,45 vì lưới đã khai trước. Có hai lý do khiến C cao hơn số đo vẫn hợp lý:
  1. Riêng Q3/26 là 36,54 ở sản lượng thấp, và Q4 Base giả định 35.
  2. Chi phí VND/LAK sẽ trôi lên theo lạm phát tới 2054, trong khi model giữ phẳng.
- Skeptic nên tấn công điểm này.

**Hàm LNST — luật chọn k (khai trước): RMSE backcast 2021–2024 nhỏ nhất, mức hiệu chỉnh khớp 2025** (mục 2):
| Năm | RSS3 | LNST thật [BQ] | k 0 (sai số) | **k 0,3** | k 0,6 |
|---|---|---|---|---|---|
| 2021 | 2,072 | 76,8 | 68,7 (−8,1) | 95,3 (+18,5) | 121,8 (+45,0) |
| 2022 | 1,810 | 59,9 | 20,1 (−39,8) | 61,3 (+1,3) | 102,4 (+42,5) |
| 2023 | 1,576 | 74,1 | −19,8 (−93,9) | 35,9 (−38,2) | 91,6 (+17,5) |
| 2024 | 2,275 | 108,8 | 56,9 (−51,8) | 56,4 (−52,4) | 55,8 (−53,0) |
| 2025 | 2,183 | 157,4 | 157,4 (0) | 157,4 (0) | 157,4 (0) |
| **RMSE 21–24** | | | 57,4 | **33,7** | 41,7 |
- **Chọn k = 0,3**, dốc **173 tỷ/($/kg)**, so với 248 của hàm cũ và 99 nếu biên gộp không đổi.
- Hạn chế:
  - N = 4 năm.
  - Sản lượng 2021–22 giả định 14.000 t [UL].
  - Năm 2024 lệch −52 với mọi k, vì giá DRI thực nhận lệch khỏi RSS3 và vì f = 0,5 đẩy giá vốn/t lên khi sản lượng giảm.
- POST-HOC (mục 8, không đổi lưới): với f = 0, RMSE còn 23,4 và vẫn chọn k 0,3. Thực tế 2024 sản lượng −28% nhưng GVHB/t **thấp hơn** 2025. Vậy dữ liệu **không ủng hộ** f cao. f là trục ít nhạy (~600 đ), nên không đổi kết luận.
- Bằng chứng truyền giá: biên gộp hợp nhất 36–43% suốt 2021–25 [BQ GPM_P0] dù RSS3 dao động 1,58–2,27. Chi phí chạy theo giá, nhiều khả năng do lương cạo mủ, LAK và chi phí xuất kho. Đây là lý do hàm cố định (k 0) dốc quá mức.

## 3. Sửa (c): sản lượng theo tuổi vườn
- **Không tìm thấy bảng năm trồng/diện tích theo tuổi** trong BCTN 2025, BCTN 2024, BCTC Q3 hay `dd_*`.
- Số có nguồn [BCTN25]:
  - 8.592,3 ha cao su.
  - "2015: 80% diện tích đã đưa vào khai thác" ⇒ trồng chủ yếu ~2005–2010 [UL].
  - "Diện tích cao su đang dần bước vào chu kỳ thanh lý".
  - Thu mua tiểu điền ~2.000 t năm 2026 "bù đắp sản lượng thiếu hụt khi vườn cây đi vào lộ trình thanh lý".
  - Tái canh 37,77 ha năm 2026.
  - Cam kết khoanh nuôi phần đất rừng bảo tồn khi hết chu kỳ 1.
- Vì vậy đường sản lượng là **giả định chưa có nguồn**: 14.000 t, rồi giảm 0 / 2 / 3%/năm từ 2035 (tâm 2%). Tâm 2% làm FV **−1.537 / −1.646** (gồm cả f).
- Stress ngoài lưới, giảm 3%/năm từ 2030: **9.893** (mid 1,97) / **11.129** (mid 2,075).
- **Sầu riêng (238 ha tới 2030), tái canh, gỗ thanh lý, thu mua tiểu điền: loại khỏi FV.** Không có số dòng tiền. Chỉ giữ "khác 10 tỷ/năm" như bản trước. Đây là phần có thể làm FV tăng mà model không tính.

## 4. Sửa (c tiếp): rò rỉ khi chuyển lợi nhuận từ Lào
- **Phí/thuế chuyển LN 10%**, có hai nguồn:
  - BCTN24 viết nguyên văn: "Lào đang áp dụng phí chuyển lợi nhuận về nước 10%/tổng lợi nhuận chuyển về".
  - Wendy: thuế cổ tức 10% theo Luật thuế thu nhập Lào 67/NA (2019) [nguồn thứ cấp, trung bình–cao]. Hiệp định VN–Lào 1996 Điều 10 đặt trần 10% [ĐÃ XÁC MINH văn bản].
  - VN không thu thêm nếu Lào đã thu đủ 20% CIT. Phần khấu trừ gián tiếp và ưu đãi miễn thuế ở Lào thì chưa rõ.
- **CHƯA RÕ** khoản 10% đã nằm trong thuế hiệu dụng hợp nhất (Q3/26 18,3%) hay chưa. H1/26 có khấu trừ thuế 11,17 tỷ [dd_DRI].
  - Nếu đã nằm trong thì đúng là w = 0, và FV tâm **+960 / +1.116**.
  - Cần đọc thuyết minh thuế TNDN hợp nhất để chốt.
- **Haircut tiền ở Lào** áp lên 196,7 tỷ tiền gửi tại ngân hàng Lào [BCTC3]: 15% ⇒ −403 đ. Ngoài lưới, nếu haircut 30% áp cả lên FCF: 9.486 / 10.484.

## 5. Tồn kho và PB (sửa nhãn)
- Cách tính giữ nguyên bản trước, X = 1.717 t. Tồn kho 30/09/26 **183,9 tỷ là [BCTC3]** (snapshot BQ chỉ tới Q2/26); 30/09/25 124,2 [BQ].
- **BVPS thống nhất 9.971 đ** (VCSH mẹ 729,86 tỷ 30/09, đã ghi cổ tức phải trả [BCTC3]) ⇒ PB ở 14.700 = **1,47x**. PB trung vị theo pha, lấy từ bản trước [BQ]:
  | Pha | PB trung vị DRI |
  |---|---|
  | PEAK | 1,49 |
  | MID | 1,25 |
  | TROUGH | 0,65 |

## 6. Vùng mua dưới lưới mới (biên an toàn = FV/ngưỡng − 1, tâm 60/40; mục 7)
| Ngưỡng (PB) | mid 1,865 | mid 1,97 | mid 2,075 | mid 2,18 | Tỷ lệ ô lưới FV ≥ ngưỡng (1,865 / 1,97 / 2,075 / 2,18) |
|---|---|---|---|---|---|
| ≤ 13.000 (1,30x) | −15% | −4% | +7% | +18% | 22% / 58% / 88% / 99% |
| ≤ 11.500 (1,15x) | −4% | +9% | +21% | +33% | 57% / 88% / 100% / 100% |
| PB ≤ 1 ≈ 9.971 | +11% | +25% | +39% | +54% | 90% / 100% / 100% / 100% |
- **13.000 chỉ có biên an toàn dương nếu mid ≥ 2,075.** Ở mid 1,97 biên âm nhẹ. Vùng này yếu hơn bản trước, vì bản trước đếm phép ghép.
- **11.500 dương nếu mid ≥ 1,97** (+9%). Biên mỏng ở khoảng đáng tin nhất.
- **PB ≤ 1 dương ở mọi mid**, kể cả 1,865 (+11%). Đây là vùng duy nhất bền với cả trục mid.
- **Điều kiện pha khi coi PB ≤ 1 là fear-buy:**
  - Lịch sử, PB ≤ 1 gần như chỉ xuất hiện ở pha TROUGH (trung vị 0,65).
  - Lưới hiện tại không có đường giá đáy cho 2027–28 (chỉ PEAK/MID), nên biên +11…+54% **bị phóng đại** nếu PB ≤ 1 đến cùng một đợt đáy RSS3.
  - Mua khi đó cần kèm điều kiện pha đã khai: Bobby → TROUGH thì xem lại bảng tiêu chí THOÁT trong `../dd_DRI_20261027/REPORT.md`, và kiểm tra sự kiện Lào (thuế, đất, chuyển tiền).

## 7. Đo được và đoán (đọc trước khi dùng số)
- **ĐO** (có nguồn):
  - Selfcheck 10.878 / 11.031 / 14.301.
  - GVHB/t 27,85 / 30,13 / 31,48 và định nghĩa "33,11".
  - Tấn bán và giá USD 2024/25; LNST 2021–25; GPM 2021–25; tiền ở Lào 196,7; BVPS 9.971; phí Lào 10% (có văn bản, chưa rõ cách hạch toán); trung vị RSS3 danh nghĩa.
  - Backcast và sai số từng năm.
- **ĐOÁN / phán đoán:**
  - Mid giữa chu kỳ (trục lớn nhất); trọng số 60/40; đường sản lượng sau 2035; f; r.
  - Haircut LAK; w đã gồm trong thuế hay chưa; FCF = 90% LN; quyền đất tới 2054; CPI Mỹ.
  - Việc loại sầu riêng/tái canh khỏi FV.
- **Lệch thực/danh nghĩa chưa xử lý:** dòng tiền "tiền 2025" (chi phí và tỷ giá phẳng) nhưng chiết khấu bằng r danh nghĩa 10–13%. Hai sai lệch ngược chiều nhau: (i) r danh nghĩa làm FV thấp đi; (ii) chi phí không trôi theo lạm phát làm FV cao lên. Không tách được nếu thiếu chuỗi giá vốn dài.

## 8. Còn mở cho skeptic
1. Lưới C_ref 31–33 cao hơn số đo cùng định nghĩa (~30,1–30,5). Nên giữ (chi phí sẽ trôi lên) hay hạ?
2. Khoản 10% Lào đã trong thuế hiệu dụng hay chưa: cần thuyết minh thuế BCTC năm.
3. Backcast N = 4, sản lượng 2021–22 giả định, 2024 không khớp với mọi k.
4. Không có bảng tuổi vườn. Đường sản lượng hoàn toàn là giả định.
5. Không dùng giá hay dữ liệu sau 27/10. Mục 8 của `out.txt` là POST-HOC, không đổi tâm/lưới.

**Hàm ý (không phải khuyến nghị lệnh):** ở khoảng mid tôi cho là đáng tin nhất, 14.700 **cao hơn FV 6–18%**, gần với báo cáo Q3 hơn là với bản 14.301. Bản này không đảo, cũng không xác nhận, quyết định giảm 50%.

Nguồn: `PREREG.md`, `model.py`, `out.txt`, `src/bctn2025_excerpt.txt`, `src/bctn2024_excerpt.txt` (md5 PDF ở `src/pdf_md5.txt`) · `../dri_val_supply_adj_20261027/data/` (snapshot BQ) · `../dd_DRI_20261027/` · `data/rubber_monthly.csv`, `data/macro_usdvnd.csv`.
