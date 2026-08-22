# PREREG — Nhóm (b) chu kỳ/hàng hoá + case sơ bộ (c)/(d) của khung "sợ hãi có tính toán"

> Taylor, job `Taylor_20260822_022947`, 2026-08-22. **File này commit TRƯỚC khi chạy bất kỳ truy vấn
> outcome nào trên BQ.** Kết quả đi vào `cycle_fear_backtest_20260822.md` (file riêng, commit sau).

## 0. Câu hỏi

Khung `calculated_fear_state_backstop.md` §2.5 (discriminator "chu kỳ vs cấu trúc") hiện chỉ có **1
case verify đầy đủ cho nhóm (b): HPG 2022**. Câu hỏi: mở rộng mẫu ra nhiều ngành/nhiều đáy thì
discriminator còn phân biệt được không, và lợi suất trough+12M có dương không.

## 1. Giả thuyết (đúng nguyên văn dispatch)

- **H1**: nhóm chu kỳ (b) có **median trough+12M BHAR > 0%** và **N ≥ 5 case**.
- **H2**: discriminator "chu kỳ sẽ qua" vs "cấu trúc hỏng" **áp dụng được** — mỗi case ra được một
  phán quyết pass/fail rõ ràng theo checklist §2.5.
- **GO**: H1 ∧ H2 trên **≥3 ngành**, có **OOS check** (case sau 2020).
- **NO-GO**: median BHAR ≤ 0%, **hoặc** N < 5, **hoặc** discriminator không phân biệt được.

### 1.1 Định nghĩa thao tác của "discriminator không phân biệt được" (bổ sung — dispatch không định nghĩa)

Không định nghĩa trước thì mệnh đề H2 không thể sai, tức không phải giả thuyết. Chốt:

> Discriminator **PHÂN BIỆT ĐƯỢC** ⟺ (i) median BHAR_12M của nhóm **PASS** (đủ cả 4 tiêu chí §2.5)
> **cao hơn** median của nhóm **FAIL** (trượt ≥1 tiêu chí) **ít nhất 20 điểm phần trăm**, VÀ (ii)
> **cả 3 negative control** đã chỉ định trước ở §3.3 rơi vào nhóm FAIL đúng như phân loại ex-ante.
>
> Ngược lại (gap < 20pp, hoặc negative control lại thắng) ⟹ **H2 BÁC BỎ** ⟹ NO-GO.

## 2. Đo lường — cố định trước

- **Nguồn**: BQ `tav2_bq.ticker` (partition `time`, cluster `ticker`), cột **`Close`** (adjusted).
  **KHÔNG dùng `Price`** (raw, không điều chỉnh cổ tức/chia tách) — đây là bẫy hệ quy chiếu đã cắn
  thật ở job corp-action 2026-08-21 (lệch −6,83pp thuần kế toán khi cửa sổ bắc qua ex-date).
- **Benchmark**: VNINDEX, cùng nguồn, cùng ngày, cùng phép tính.
- **Đáy (trough)**: `MIN(Close)` trong **cửa sổ khủng hoảng đã khai báo trước ở §3** cho từng case.
  Cửa sổ được chọn TRƯỚC khi query, dựa trên mốc lịch sử đã biết công khai (không phải chọn theo giá).
- **BHAR_H** = `Close(trough + H)/Close(trough) − 1` **−** `VNINDEX(trough + H)/VNINDEX(trough) − 1`,
  với H ∈ {6M, 12M, 24M} tính theo **ngày lịch** (126/252/504 phiên là xấp xỉ; dùng ngày lịch để nhất
  quán với quy ước metric của repo). Nếu thiếu phiên đúng ngày, lấy phiên giao dịch **gần nhất ≤** mốc.
- **Metric chính cho H1**: **median BHAR_12M**.

### 2.1 Hai neo entry — bắt buộc báo CẢ HAI

| Neo | Định nghĩa | Tính chất |
|---|---|---|
| **T0 = trough** | đáy thật trong cửa sổ | **EX-POST, KHÔNG thực thi được live** — là **CẬN TRÊN** của lợi suất khả thi. Dùng để so sánh được với case HPG §8 đã có |
| **T20 = trough + 20 phiên** | 20 phiên sau đáy | Proxy thô cho "không ai nhận ra đáy ngay lúc đó". Bi quan hơn, gần thực tế hơn |

**Phán quyết H1 đọc trên T0** (để so được với HPG). **Nếu T0 dương nhưng T20 âm ⟹ hạ verdict xuống
WEAK và nói rõ**: edge chỉ tồn tại nếu bắt đúng đáy, tức không thực thi được.

### 2.2 Khai N trung thực

Các mã cùng ngành, cùng một đáy **KHÔNG độc lập** (SSI/VCI/HCM 2022Q4 là MỘT sự kiện; DIG/PDR/NVL là
MỘT sự kiện). Báo cả hai:
- **N_tickers** = số cặp (mã × đáy).
- **N_eff** = số **episode độc lập** = số cặp (ngành × đáy).

Ngưỡng "N ≥ 5" của H1 áp trên **N_tickers** (đúng nguyên văn dispatch), nhưng **mọi phát biểu về độ
tin cậy phải trích N_eff** — với N_eff cỡ 4–6 thì đây là **playbook, không phải edge thống kê**, và
sẽ nói đúng như vậy. **Không chạy t-test/p-value trên N_tickers** (giả độc lập).

### 2.3 Điều KHÔNG được làm

- Không đổi cửa sổ khủng hoảng sau khi thấy giá.
- Không thêm/bớt case sau khi thấy outcome. Case nào thiếu dữ liệu ⟹ báo "thiếu dữ liệu", không thay thế.
- Không đổi định nghĩa BHAR/H sau khi thấy kết quả.
- Không suy ra khuyến nghị wire production dưới bất kỳ verdict nào (dispatch cấm rõ).

## 3. Case universe — CHỐT, không sửa sau

### 3.1 Nhóm (b) — chu kỳ/hàng hoá

| # | Mã | Ngành | Cửa sổ khủng hoảng (chốt trước) | Bối cảnh |
|---|---|---|---|---|
| 1 | **HPG** | Thép | 2022-06-01 → 2023-01-31 | Đáy chu kỳ thép + BĐS đóng băng. **Case đối chứng đã documented §8** |
| 2 | **HSG** | Tôn/thép thương mại | 2022-06-01 → 2023-01-31 | **NEGATIVE CONTROL** — cùng ngành cùng đáy, không phải leader chi phí thấp |
| 3 | **NKG** | Tôn/thép thương mại | 2022-06-01 → 2023-01-31 | **NEGATIVE CONTROL** — như trên |
| 4 | **SSI** | Chứng khoán | 2022-09-01 → 2023-01-31 | Đáy VN-Index ~874 (11/2022), thanh khoản sập |
| 5 | **VCI** | Chứng khoán | 2022-09-01 → 2023-01-31 | — |
| 6 | **HCM** | Chứng khoán | 2022-09-01 → 2023-01-31 | — |
| 7 | **DIG** | BĐS | 2022-09-01 → 2023-03-31 | Siết trái phiếu BĐS |
| 8 | **PDR** | BĐS | 2022-09-01 → 2023-03-31 | Bị bán giải chấp hàng loạt |
| 9 | **NVL** | BĐS | 2022-09-01 → 2023-03-31 | **NEGATIVE CONTROL** — khủng hoảng rollover trái phiếu = nghi CẤU TRÚC |
| 10 | **DBC** | Chăn nuôi heo | 2022-10-01 → 2023-06-30 | Đáy biên chăn nuôi (giá heo thấp/giá cám cao) |
| 11 | **BAF** | Chăn nuôi heo | 2022-10-01 → 2023-06-30 | — |
| 12 | **DCM** | Phân bón/urê | 2022-09-01 → 2023-06-30 | Đáy chu kỳ urê sau siêu chu kỳ 2021-22 |
| 13 | **DPM** | Phân bón/urê | 2022-09-01 → 2023-06-30 | — |
| 14 | **DGC** | Hoá chất/photpho | 2020-02-15 → 2020-05-31 | **Case đối chứng đã documented §9** (IS, trước 2020 cut) |

### 3.2 Nhóm (c) — vĩ mô

| # | Mã/Chỉ số | Cửa sổ | Ghi chú |
|---|---|---|---|
| 15 | **VNINDEX** | 2020-02-15 → 2020-05-31 | COVID crash. BHAR của chỉ số vs chính nó = 0 theo định nghĩa ⟹ với (c) báo **lợi suất TUYỆT ĐỐI**, không phải BHAR |
| 16 | **VNINDEX** | 2022-01-01 → 2022-12-31 | ⚠️ **ĐÍNH CHÍNH DISPATCH**: dispatch ghi "bán tháo 2022Q1 (Nga-Ukraine)". VN-Index đạt **đỉnh** đầu 2022 và đáy thật rơi vào **Q4/2022** (siết trái phiếu + margin call), không phải Q1. Cửa sổ mở rộng cả năm để đáy tự lộ ra, không ép theo mô tả sai |
| 17 | **VNM, FPT, MWG** | 2020-02-15 → 2020-05-31 | 3 large-cap phi-hàng-hoá: test "cả thị trường về giá trị" vs "lõi xấu" |

### 3.3 Negative control chỉ định trước (dùng cho §1.1 điều kiện (ii))

**HSG, NKG** (không phải leader chi phí thấp — trượt §2.5 #3) và **NVL** (nghi cấu trúc: rollover trái
phiếu, trượt §2.5 #2). Cả 3 phải rơi vào nhóm FAIL, nếu không thì H2 bác bỏ.

### 3.4 Nhóm (d) — gián đoạn vận hành

| # | Mã | Sự kiện | Cửa sổ | Ghi chú |
|---|---|---|---|---|
| 18 | **RAL** | Cháy nhà máy Rạng Đông + nhiễm thuỷ ngân, 28/08/2019 | 2019-08-28 → 2020-01-31 | Ứng viên (d) **rõ nhất** tìm được ở VN: sự cố vận hành thuần, không pháp lý cá nhân, có thời hạn khắc phục |
| 19 | **MSH, TNG, VHC, FMC** | Đóng cửa nhà máy "3 tại chỗ" phía Nam Q3/2021 | 2021-07-01 → 2021-12-31 | Gián đoạn có thời hạn rõ. **Rủi ro biết trước**: thị trường 2021 đang bull ⇒ có thể KHÔNG có đợt bán tháo nào để đo. Nếu vậy báo "không thành case", KHÔNG ép |

**Nhóm (d) là THĂM DÒ, không phán quyết.** N quá nhỏ để test gì; mục đích là xem có tìm được case đủ
hình dạng để đưa vào khung không.

## 4. Phân loại §2.5 — CHỐT TRƯỚC KHI THẤY OUTCOME

Bốn tiêu chí §2.5: **#1** chu kỳ (không cấu trúc) · **#2** sống sót qua đáy (bảng cân đối) · **#3**
leader chi phí thấp · **#4** sàn tài sản thực (PB ≲1 trên tài sản hữu hình).

Phân loại dưới đây dựa trên **hiểu biết ngành + logic §2.5**, chốt trước khi query outcome. Tiêu chí
**#2 và #4 sẽ được XÁC MINH bằng dữ liệu PIT** (`ticker_financial` tại quý đã công bố trước ngày đáy);
nếu dữ liệu bác lại phán đoán ex-ante, **ghi rõ là đã sửa và sửa vì số nào** — không lặng lẽ đổi.

| Mã | #1 chu kỳ | #2 sống sót | #3 leader | #4 sàn TS | **Phán quyết ex-ante** |
|---|---|---|---|---|---|
| HPG | ✅ | ✅ | ✅ | ✅ | **PASS** |
| HSG | ✅ | ? | ❌ biên mỏng, thương mại | ? | **FAIL** (#3) |
| NKG | ✅ | ? | ❌ biên mỏng, thương mại | ? | **FAIL** (#3) |
| SSI | ✅ chu kỳ thanh khoản TT | ✅ vốn lớn nhất ngành | ✅ #1 thị phần môi giới | ❌ PB CK hiếm khi <1 | **FAIL** (#4) |
| VCI | ✅ | ✅ | ⚠️ top nhưng không dẫn đầu | ❌ | **FAIL** (#4) |
| HCM | ✅ | ✅ | ⚠️ | ❌ | **FAIL** (#4) |
| DIG | ✅ siết tín dụng tạm | ⚠️ đòn bẩy cao | ❌ không leader | ? | **FAIL** (#3) |
| PDR | ✅ | ❌ bị giải chấp ở đáy | ❌ | ? | **FAIL** (#2,#3) |
| NVL | ❌ rollover TP = cấu trúc | ❌ | ❌ | ? | **FAIL** (#1,#2,#3) |
| DBC | ✅ chu kỳ heo kinh điển | ⚠️ | ✅ leader quy mô 3F | ? | **PASS nếu #2,#4 xác nhận** |
| BAF | ✅ | ⚠️ mới, đòn bẩy | ❌ theo sau | ? | **FAIL** (#3) |
| DCM | ✅ chu kỳ urê | ✅ tiền mặt ròng | ✅ chi phí khí ưu đãi | ? | **PASS nếu #4 xác nhận** |
| DPM | ✅ | ✅ tiền mặt ròng lớn | ✅ | ? | **PASS nếu #4 xác nhận** |
| DGC | ✅ | ✅ | ✅ | ✅ PB 0,73 (đã đo §9) | **PASS** |
| RAL | ✅ (d) có thời hạn | ? | ⚠️ | ? | **chưa phân loại — chờ PIT** |

**Dự đoán ex-ante viết ra để có thể SAI:** nhóm PASS (HPG, DGC, + DCM/DPM/DBC nếu xác nhận) có median
BHAR_12M cao hơn nhóm FAIL ≥20pp; NVL là case tệ nhất tuyệt đối.

## 5. Thiên lệch đã biết — khai trước, không bào chữa sau

1. **KHÔNG BLIND.** HPG (§8) và DGC (§9) đã documented với outcome đã biết; NVL là chuyện công khai
   ai cũng biết. Đây là **pre-registered nhưng không blind** ⟹ điều mạnh nhất có thể tuyên bố là
   **nhất quán nội bộ**, KHÔNG phải "dự báo out-of-sample". Nói đúng như vậy trong kết quả.
2. **Trough là ex-post** (§2.1) — đã xử bằng neo T20 song song.
3. **Survivorship**: mã huỷ niêm yết/ngừng giao dịch sau đáy sẽ thiếu dữ liệu ⟹ tự động bị loại khỏi
   `ticker`, đẩy kết quả LÊN. Phải kiểm tra tường minh mã nào thiếu chuỗi giá và báo ra.
4. **2022Q4 chi phối mẫu**: 9/14 case nhóm (b) cùng đáy 2022Q4 ⟹ phần lớn "N" là **một** cú sốc vĩ mô.
   Đây chính là lý do phải khai N_eff (§2.2). BHAR vs VNINDEX khử phần chung, nhưng không khử được
   tương quan chéo còn lại.
5. **Mâu thuẫn đã biết với screen N-lớn §9**: `fearbuy_systematic_screen_20260723.md` (N=237 episode)
   đã kết luận **commodity KHÔNG phải động lực** — non-commodity median +47,5% vs commodity +12,5%.
   Job này nhìn **đúng cái subset median-thấp đó**. Nếu ra kết quả đẹp cho nhóm chu kỳ, phải đối chiếu
   lại với §9 chứ không được công bố như phát hiện độc lập.
6. **OOS yếu**: dispatch định nghĩa OOS = "case sau 2020", nhưng gần như toàn bộ mẫu là 2022 (sau 2020)
   còn IS chỉ có DGC 2020 + RAL 2019. Đây **không phải walk-forward thật** — chỉ là nhãn. Báo đúng bản chất.
