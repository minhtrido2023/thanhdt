**KẾT LUẬN: KHÔNG TƯƠNG THÍCH** (tiêu chí khoá trước ở `PRELOCK.md`; trượt K3 "không hội tụ"). Mức trung bình thì đúng
(FV/giá trung vị 1,17), nhưng từng mã lệch nhau rất xa và khoảng cách giá–FV không thu hẹp sau 3–5 năm. Khi engine nói
"đắt" (FV<giá), giá chỉ về tới tâm trong 60 tháng ở 32% số ca.

Job Taylor_20261111_032615 · 2026-11-11 · Taylor · CHỈ NGHIÊN CỨU (không sửa engine, skill, zones hay moat_tags).

## 0. Cái gì được kiểm định, cái gì KHÔNG
- **ĐÃ kiểm định:** engine cơ học `dcf_valuation.fair_value` chạy đúng cấu hình production: frame `domestic_v2` (r 12,25%,
  trần g_T 5,5%, cap_rf), shrink 0,5, cơ sở FCFE 3 năm. Số CP lấy theo quý (`fin`, PIT). Tính tại 40 mốc cuối quý,
  2016Q1–2025Q4.
- **KHÔNG kiểm định được theo PIT:** tâm/vùng DD trong `dd_price_zones`. Đó là engine **cộng thêm lớp phán đoán** (comps,
  kịch bản, chiết khấu thanh khoản, moat), không có phiên bản lịch sử để chạy lại. §5 cho thấy lớp này **viết đè engine
  rất mạnh**, nên kết luận ở đây là về NỀN dòng tiền của DD, không phải về từng vùng DD hiện tại.
- Mẫu chính: mã không-tài-chính, `in_universe` (universe_pit) đúng phiên as-of, rating_8l ≤ 3 (merge_asof lùi), engine
  trả FV. Ra **4.451 dòng (mã, as-of) · 437 mã · 40 quý**. Mẫu phụ là toàn bộ universe_pit (6.107 dòng): kết quả gần như
  y hệt (FV/P 1,16 · touch60 0,72 · gap ratio 1,01 · beta 0,055).
- Giá tại as-of = `Price` chưa điều chỉnh, cùng khung với OShares quý. Đường giá sau đó = `Price_t × Close_{t+k}/Close_t`
  (Close đã điều chỉnh, nên gồm cả cổ tức tiền mặt). Vì vậy các tỉ lệ "chạm tâm" bên dưới là **cận dưới**: giá trần
  không gộp cổ tức sẽ chạm sớm hơn một chút.

## 1. Tiêu chí PRELOCK và kết quả
| Tiêu chí | Ngưỡng ⇒ KHÔNG | Đo được | CI95 bootstrap cụm (mã · quý) | Trượt? |
|---|---|---|---|---|
| K1: chạm tâm trong 60 tháng (tính cả t0; chỉ as-of đủ 60 tháng, n=2.234) | < 50% | **72,0%** | [67,1–76,5] · [70,1–73,9] | không |
| K2: trung vị FV/giá tại as-of | ngoài [0,75; 1,25] | **1,168** | [1,05–1,30] · [1,10–1,23] | không (CI theo mã chạm 1,30) |
| K3a: median\|log(P₃₆/FV)\| ÷ median\|log(P₀/FV)\| (n=3.367) | ≥ 1 | **1,009** | [0,94–1,09] · [0,97–1,05] | **CÓ** |
| K3b: β của log(P₃₆/P₀) theo log(FV/P₀) | CI chứa 0 | 0,070 | [0,039–0,102] · [0,043–0,095] | không |

K3b dương và có ý nghĩa thống kê, nhưng rất nhỏ: sau 3 năm giá chỉ đi được khoảng 7% quãng đường log về phía FV. Phần dư
giá-so-với-FV gần như giữ nguyên: median |gap| là 0,69 → 0,70 (36 tháng) → 0,75 (60 tháng). Ngay cả khi so với **FV cập
nhật** tại t+36, tỉ số vẫn là 0,976. Nói cách khác: giá và FV của engine không đi lại gần nhau theo thời gian.

N độc lập: với touch60, N hiệu dụng là **~349 theo cụm mã** (so với 2.234 dòng) và ~2.137 theo cụm quý. Ràng buộc chính là
mã, vì **57% phương sai log(FV/P) nằm giữa các mã** (tự tương quan 4 quý là 0,45).

## 2. Phân phối FV/giá — đúng ở mức trung bình, sai ở từng mã
- FV/P: trung vị 1,17, IQR **0,56 → 2,20** (IQR log 1,37). 44% số ca có FV < giá, 31,5% có FV < 0,7×giá.
- Theo mã (291 mã có ≥ 4 quý): **31%** mã có FV/P trung vị < 0,75 ("luôn đắt"), **46%** > 1,33 ("luôn rẻ"). 23% mã có
  FV < giá ở ≥ 80% số quý. Đây đúng là hiện tượng user lo ngại: một nhóm lớn mã mà giá và định giá không gặp nhau. Lỗi
  không nằm ở mức chung mà ở chỗ engine xếp sai từng mã.
- Ổn định theo năm: bỏ lần lượt từng năm, trung vị FV/P vẫn nằm trong 1,12–1,19 và touch60 trong 0,71–0,73. Không có năm
  nào chi phối kết quả.

| as-of | n | mã | FV/P trung vị | %FV<P | chạm36 | chạm36 khi FV<P | chạm60 khi FV<P | gap ratio 36 | β36 |
|---|---|---|---|---|---|---|---|---|---|
| 2016 | 357 | 125 | 1,22 | 42% | 73% | 36% | 46% | 0,98 | 0,09 |
| 2017 | 330 | 109 | 1,17 | 43% | 70% | 30% | 30% | 1,21 | −0,01 |
| 2018 | 341 | 119 | 1,05 | 49% | 65% | 29% | 29% | 1,07 | 0,12 |
| 2019 | 371 | 119 | 1,28 | 42% | 71% | 31% | 33% | 0,95 | 0,12 |
| 2020 | 393 | 121 | 1,55 | 29% | 76% | 19% | 21% | 0,80 | 0,11 |
| 2021 | 634 | 216 | 1,15 | 45% | 72% | 37% | 33% | 1,05 | 0,04 |
| 2022 | 617 | 212 | 1,20 | 42% | 76% | 42% | – | 0,99 | 0,05 |
| 2023 | 437 | 143 | 1,02 | 49% | 58% | 11% | – | 1,16 | 0,03 |
| 2024 | 460 | 139 | 0,95 | 52% | – | – | – | – | – |
| 2025 | 511 | 166 | 1,15 | 45% | – | – | – | – | – |

Theo DT5G tại as-of (state 1 = CRISIS … 5 = EX-BULL), FV/P lần lượt là 1,10 / 1,30 / 1,16 / 1,16 / 1,20 và gap ratio
36 tháng là 1,02 / 0,99 / 1,01 / 1,03 / 0,89. Không có chế độ nào hội tụ rõ, nên đây không phải hiện tượng riêng của một
chế độ thị trường.

## 3. Chạm tâm / vùng (c-ii, c-v)
| Chân trời | chạm ≤ tâm | chạm ≤ 0,85×tâm | khi FV<P | khi FV<0,7P (v) | từng vào vùng ±độ nhạy | % phiên trong vùng |
|---|---|---|---|---|---|---|
| 12 tháng | 64,6% | 59,1% | 19,4% | 6,6% (n=1.362) | 30,8% | 11,4% |
| 24 tháng | 67,9% | 62,7% | 26,2% | 12,0% | 40,5% | 11,8% |
| 36 tháng | 70,8% | 65,7% | 31,2% | 16,0% (n=1.018) | 47,6% | 11,9% |
| 60 tháng | 72,0% | 67,6% | 32,5% | **16,6%** (n=676) | 56,7% | 11,4% |

Tỉ lệ chạm tổng (72%) trông ổn chỉ vì 56% số ca có FV > giá, tức là "chạm" ngay tại t0. **Ở những ca giá phải giảm mới
chạm tâm thì 2/3 không bao giờ chạm trong 5 năm. Với ca FV < 0,7×giá thì 83% không chạm.** Vùng engine (min–max của các
biến thể r±1đ, g±2đ) quá hẹp so với độ phân tán: giá chỉ nằm trong vùng ~11% số phiên.

## 4. Rule mua "giá ≤ 0,85×tâm" (f)
FV của từng quý được giữ nguyên cho các phiên tới quý kế tiếp (PIT), trên 277.705 cặp mã-phiên và 437 mã. Rule **kích
hoạt ở 49,6% số phiên** và 60% số mã-năm (theo năm dao động 48–74%). Vậy rule KHÔNG vô dụng vì hiếm; vấn đề ngược lại.
Rule kích hoạt **theo danh tính mã chứ không theo thời điểm**: 26% mã chưa bao giờ kích hoạt, 29% kích hoạt < 5% số
phiên, trong khi nhóm "luôn rẻ" thì gần như kích hoạt suốt. Lý do là mức chênh nằm giữa các mã (57% phương sai) và bền
qua thời gian, nên rule chủ yếu đang chọn những mã có cấu trúc dòng tiền khiến FCFE 3 năm cao so với lợi nhuận.

## 5. Cầu nối: tâm DD hiện tại so với engine (sổ Mike trích 11/11, 25 mã)
Engine trả FV cho 17/25 mã. 8 mã còn lại: 5 mã FCFE ≤ 0 (HPG, SIP, PVT, SCL, DCM), 2 ngân hàng, 1 mã trượt cổng CFO (TCH).
- Tâm DD ÷ FV engine: trung vị **0,75**, dải 0,13 (TV1) → 18,9 (SZL).
- Độ phân tán so với giá: IQR log của **engine/giá là 1,06**, của **DD/giá chỉ 0,36**. Tâm DD bám giá (trung vị 1,05).
- Như vậy lớp phán đoán DD đang **sửa rất mạnh** cái engine xếp sai. Điều đó giải thích vì sao test mô tả của Mike pass.
  Nhưng chính độ "bám giá" này là triệu chứng mà mối lo (3) nói tới (neo ngầm vào giá). Không kiểm định PIT được, vì lớp
  DD không có lịch sử để chạy lại.

## 6. Chẩn đoán thành phần (e): thay từng tham số, giữ nguyên các tham số còn lại
Tính lại FV từ các thành phần đã lưu, bằng đúng hàm `D._fv_per_share`. Chân đối chứng production khớp engine với độ lệch
tối đa 0,0. **N trials = 144**: 72 tổ hợp khai trong prelock, cộng 72 tổ hợp cơ sở earning-power khai thêm sau đó. Bảng
dưới là số đo IS (as-of 2016–19) / OOS (2020+).

| Thay | FV/P trung vị | IQR log | gap ratio 36 | β36 | chạm60 khi FV<P |
|---|---|---|---|---|---|
| production | 1,17 / 1,17 | 1,40 / 1,37 | 1,03 / 0,98 | 0,074 / 0,067 | 34% / 29% |
| r 10,25 → 13,25% | 1,67 → 1,02 | ~1,40 (không đổi) | 0,96 → 1,03 | 0,074 (không đổi) | 37% → 33% |
| trần g_T 4,5 → 6,5% | 1,03 → 1,36 | ~1,40 | 1,03 → 1,02 | 0,074 | 34% → 36% |
| shrink 0,25 → 0,75 | 1,09 → 1,24 | 1,41 → 1,43 | 1,04 → 1,04 | 0,074 | 32% → 36% |
| cơ sở FCFE 5 năm | 1,17 / 1,04 | 1,23 / 1,18 | 1,01 / 1,04 | 0,086 / 0,075 | 40% / 38% |
| cơ sở **LNST TTM** | 2,01 / 1,51 | **0,74 / 0,84** | **0,80 / 0,88** | **0,101 / 0,158** | **61% / 45%** |
| cơ sở 50% FCFE3y + 50% LNST | 1,77 / 1,44 | 0,82 / 0,91 | 0,91 / 0,92 | 0,157 / 0,174 | 53% / 55% |

**Đọc bảng:**
1. **r, g_T và shrink chỉ dịch MỨC.** Chúng gần như không đổi độ phân tán (IQR log ~1,40) hay tốc độ hội tụ (β 0,074).
   Thay đổi chúng chỉ dời trung vị FV/P, tức là "khớp cho đẹp" ở mức trung bình mà không sửa được lỗi thật. Vì vậy **không
   đề xuất đổi r/g_T/shrink**. Mức hiện tại (1,17) đã nằm trong ngưỡng K2.
2. **Lỗi nằm ở cơ sở dòng tiền.** FCFE 3 năm (CFO − capex) quá nhiễu và không phải thứ thị trường VN định giá. Đổi sang
   cơ sở lợi nhuận thì **độ phân tán giảm một nửa**, β hội tụ tăng 1,4–2,4 lần, và tỉ lệ chạm khi FV<P tăng từ 34% lên
   61% (IS), từ 29% lên 45% (OOS). Cải thiện giữ được qua OOS.
3. Nhưng LNST thì **vượt mức** (FV/P trung vị 2,0 IS / 1,5 OOS). Lý do: LNST chưa trừ phần tái đầu tư nên không phải tiền
   chia được. Chọn tổ hợp tốt nhất trên IS theo prelock (qua K3, mức gần 1 nhất) thì không có biến thể earning-power nào qua
   đồng thời K2 và K3 trong lưới. Kéo mức xuống bằng cách nâng r là tune theo giá, nên **dừng ở đây, không chọn tham số từ
   lưới này**.

## 7. Đề xuất (Mike + user duyệt; chưa đề xuất wire, nên chưa tính DSR/PBO)
- **P1 (sửa cấu trúc, cần duyệt để làm pha 2):** đổi cơ sở dòng tiền của engine sang **FCFE cơ bản = LNST chuẩn hoá ×
  (1 − g/ROE)**. Đây là tỉ lệ tái đầu tư bền vững kiểu Damodaran, suy từ kinh tế học doanh nghiệp chứ không lấy giá làm
  đầu vào. Có thể giữ FCFE 3 năm làm "sàn tiền mặt" hoặc trọng số. Prelock mới: K1–K3 như trên, IS 2016–19 / OOS 2020+,
  khai N trials, rồi qua quant-skeptic. Ghi chú: NO-GO earning-power trước đây (`dcf_earning_power_upgrade.md`, Việc 1) là
  câu hỏi về **IC/alpha**, khác câu hỏi tương thích ở đây.
- **P2 (quy trình DD, không cần code):** khi FCFE-engine lệch tâm DD quá ×2 (FV/P < 0,5 hoặc > 2) thì gắn cờ "nền dòng
  tiền không đại diện" và bắt buộc trình bày phương pháp thay thế (P/E chuẩn hoá, EV/EBITDA, SOTP), thay vì để lớp phán
  đoán âm thầm sửa. Hai luật user giữ nguyên: moat chỉ thưởng (11-08), dự án mới NPV=0 (11-03).
- **P3 (đo được về sau):** `dd_price_zones` đã có ngày và rev. Cứ 12/24/36 tháng chấm lại tâm DD theo PIT với chính các
  chỉ số K1–K3 ở đây. Đó là cách duy nhất kiểm được lớp phán đoán DD, kể cả nghi vấn neo vào giá.
- **Rule 0,85×tâm:** giữ, nhưng chỉ có nghĩa sau P1/P2. Với nền FCFE hiện tại, nó chủ yếu lọc theo loại hình dòng tiền
  của mã.

## 8. Hạn chế
- Chỉ kiểm định engine, không kiểm định lớp phán đoán DD (§0, §5). Kết luận "KHÔNG TƯƠNG THÍCH" áp cho nền FCFE.
- Tham số `domestic_v2` (r 12,25, g_T 5,5) được hiệu chỉnh năm 2026 bằng dữ liệu tới 2026, tức là có look-ahead nhẹ ở
  tham số. Không ảnh hưởng kết luận, vì r/g_T không đổi độ phân tán hay β.
- CPI trong cửa sổ g_T lấy tháng ≤ as-of, trong khi số in thật trễ khoảng 1 tháng (không đáng kể vì trần 5,5% thường
  ràng buộc). GDP chỉ dùng năm ≤ as-of−1.
- `ticker_financial.time` = ngày vendor nạp. Nếu vendor sửa ngược dữ liệu thì vẫn còn rủi ro PIT nhỏ. Kiểm tra PIT:
  cắt fin tại as-of rồi tính lại 80 dòng ngẫu nhiên cho độ lệch 0,0.
- Mã huỷ niêm yết: nếu chưa chạm thì bị coi là thiếu dữ liệu (không tính vào mẫu); nếu đã chạm trước đó thì vẫn tính
  "chạm" ⇒ thiên lệch nhẹ về phía chạm.
- Một số FV cực trị (SJS, DMC: FV/P ≈ 0,003; NBC, VC7: FV/P ≈ 20) là do dữ liệu CF/OShares. Các số liệu dùng trung vị nên
  bền với nhiễu này.

## 9. Tái lập
```
cd agents/Taylor/research/dd_vn_calib_20261111/calc ; PY=/home/trido/thanhdt/wc_venv/bin/python
$PY build_panel.py        # -> out/panel.parquet (~3 phút, cache local, không gọi BQ)
$PY analyze.py            # -> out/summary_primary.json  (seed 20261111, B=2000)
$PY analyze.py --sample pit_all --tag pit_all
$PY trigger_freq.py ; $PY variants.py ; $PY checks.py ; $PY ticker_persistence.py
```
Kiểm tra tái lập: chạy `analyze.py` hai lần cho cùng md5 `2b7c6f645aad2ff76d41d0c5fd39ed11`. Kiểm tra PIT (`checks.py`):
độ lệch tối đa 0,0 trên 80 mẫu; `build_panel.py` có assert `fin_time ≤ asof` cho mọi dòng.
