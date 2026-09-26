# BƯỚC 3 — H2: CPI FiinPro thật thay tầng nội suy của `cpi_vn.py`

Job `Taylor_20260926_164113` · Taylor · 2026-09-27 · PAPER-ONLY, **không sửa `cpi_vn.py`**
Nguồn mới: `mike/data/fiinprox_cpi_monthly_20260914.csv` (registry `macro/fiinprox_cpi_monthly.md`)
— 224 tháng **2008-01 → 2026-08**, CPI YoY %.
Consumer đã đo: `macro_confidence_regime.py` (a) và `dcf_valuation.py` (b).
Script: `h2_cpi_swap.py` / `h2_dcf_ab.py`; log `h2_cpi_swap.log` / `h2_dcf_ab.log`.

Tầng mới dùng trong cả hai phép đo: **T1 NSO thật GIỮ NGUYÊN** (13 tháng 2025-06→2026-06),
mọi tháng khác lấy FiinPro nếu có, không có thì giữ proxy ⇒ **thay 211/236 tháng**.
`2007-01..2007-12` FiinPro KHÔNG phủ ⇒ tầng T3 backfill 2007 vẫn phải giữ.

## 1. Hai chuỗi lệch bao nhiêu — và ai đúng

Toàn mẫu (n=224): **MAE 0,441pp**, max **3,01pp**.

| Năm | proxy TB | FiinPro TB | MAE | max |lệch| |
|---|---|---|---|---|
| 2008 | 23,07 | 23,06 | **0,01** | 0,07 |
| 2009 | 6,60 | 6,99 | 0,46 | 3,01 |
| 2011 | 18,57 | 18,64 | 0,66 | 1,78 |
| 2015 | 1,05 | 0,63 | 0,42 | 1,19 |
| 2017 | 2,99 | 3,53 | 0,54 | 1,07 |
| **2019** | **3,90** | **2,80** | **1,11** | **2,51** |
| 2022 | 3,36 | 3,15 | 0,24 | 0,89 |
| 2025 | 3,43 | 3,31 | 0,13 | 0,64 |

**2019 là năm tệ nhất và có thể quy nguyên nhân bằng bằng chứng đang cầm (§29):** docstring
`cpi_vn.py` khai đúng 2 neo cho 2019 — `Jan 2.6, Dec 5.2 [ASF pork spike late]` — rồi **nội suy
tuyến tính** giữa hai neo. Số học khớp khít: tháng 10/2019 = 2,6 + (9/11)×2,6 = **4,73**, đúng giá
trị proxy in ra. Thực tế cú sốc giá thịt lợn chỉ nổ tháng 11-12/2019, nên phép nội suy dựng một
đoạn dốc SUỐT NĂM không hề tồn tại. FiinPro đọc 2,24% cho 10/2019.

**Nguồn thứ ba trong chính KB của fleet xác nhận FiinPro**: `kb/data_registry/market-state/
vn_macro_regime_history.md` (Bobby, CANONICAL) ghi giai đoạn 2016-2019 CPI **2-4%**; trung bình
2019 của FiinPro = **2,80%**, của proxy = 3,90% (ngoài dải). Đây là đối chiếu độc lập, không phải
suy đoán.

Đáng chú ý theo chiều ngược lại: **2008 khớp gần như tuyệt đối (MAE 0,01pp)** — tầng T3 backfill
của Winston cho 2008 là dữ liệu thật, không phải nội suy. Chỗ hỏng là T2 (2011-2025), đúng tầng
dispatch nhắm tới.

## 2. (a) Đổi nhãn regime — **KHÔNG ở episode lạm phát 2011/2022** ⇒ tiêu chí củng cố FAIL

Giới hạn đã đo, không suy diễn: `macro_confidence_regime.py` cần `/tmp/vn_turnover.csv` và
`/tmp/gold_world.csv`, **cả hai không còn tồn tại trên máy này** ⇒ 2 cơ `REG_A`/`REG_A_strict`
(phụ thuộc vàng) KHÔNG tái lập được. Chỉ báo 2 cơ đo được, đúng công thức trong file:
`REG_C = infl_hot | dep_rising` · `REG_B = usd_up126 & REG_C`, với
`infl_hot = (cpi_yoy_chg3 > 0) | (cpi_yoy > 4,0)` — dòng DUY NHẤT CPI chạm vào.
Lưới ngày `data/macro_features.csv` ⇒ cửa sổ khả dụng **2011-01..2026-05 (185 tháng)**, không phủ
được 2008-2010 như dispatch nêu.

| Lát | Đổi nhãn | Tỷ lệ |
|---|---|---|
| `infl_hot` (cờ tháng) | 36/236 | 15,3% |
| `REG_C` | **27/185** | 14,6% |
| `REG_B` | **17/185** | 9,2% |

`REG_C` đổi: 2014-06/07/08 · 2015-04/05/06/12 · 2017-08/11/12 · 2019-07/08/09/10 · 2020-04/07/08 ·
2021-02/07/08 · **2022-01/02** · 2023-08/12 · 2024-01 · 2024-12 · 2025-07.
(danh sách đầy đủ + nhãn cũ/mới + CPI hai chuỗi: `h2_regime_flips.csv`)

**Đối chiếu phase-map / episode registry — kết quả NGƯỢC với kỳ vọng dispatch:**
- **2011 (sóng lạm phát thứ 2, CRISIS): 0 tháng đổi.** Cả hai chuỗi đều đọc CPI 17-23% ⇒ `infl_hot`
  = True theo mọi định nghĩa. Sai số 0,66pp không đủ để đổi nhãn khi cách ngưỡng 4,0 tới ~14pp.
- **2022: chỉ 2022-01 và 2022-02** — tức TRƯỚC `EP-2022-05` (Tân Hoàng Minh/SCB/Fed) gần 3 tháng.
  Không phải "đổi đúng episode".
- **2018 (năm duy nhất Bobby có phase-map chi tiết cùng 2009): 0 tháng đổi regime** (1 tháng đổi
  `infl_hot` nhưng bị `dep_rising` hấp thụ).
- Cụm đổi dày nhất là **2019 (4 tháng REG_C) và 2017 (3 tháng)** — đúng nơi proxy sai nhiều nhất,
  nhưng KHÔNG phải nơi episode vĩ mô nằm.

⇒ Tiêu chí prereg "đổi ở đúng episode lạm phát 2011/2022 là củng cố" **không đạt**. Cách đọc đúng:
CPI thật sửa được **nhiễu giữa chu kỳ** (nơi CPI lảng vảng quanh ngưỡng 4,0 và `chg3` đổi dấu do
đoạn dốc nội suy giả), **không** sửa gì ở các episode lạm phát lớn — ở đó tín hiệu quá mạnh nên
sai số proxy không chạm tới ngưỡng. Đây là lý do đúng để wire (bớt nhiễu), nhưng **không** phải
bằng chứng "CPI thật làm hệ đọc khủng hoảng tốt hơn".

## 3. (b) DCF rổ đang giữ — **Δ = 0,000% trên 7/7 mã tính được, do trần `cap_rf` chặn**

Rổ = 30 mã đang giữ ở SpaceX + ZaloPay, đọc từ `dnse_raw_*.jsonl` mới nhất **có lọc `accountNo`
(§12)**, as-of 2026-09-26.

| | CPI cũ (T2/T3 nội suy) | CPI thật (FiinPro) | Δ |
|---|---|---|---|
| `terminal_growth` (TB CPI 5 năm) | 3,4426% | 3,4147% | **−0,0279pp** |
| `g_term` (mode `cap_rf`) | 6,8000% | 6,8000% | **0,0000pp** |
| Giá trị hợp lý/mã (7 mã) | — | — | **0,000% mọi mã** |

`frac_real = 0,22` ⇒ 78% cửa sổ 5 năm vẫn là proxy, nên chuỗi CPI **thực sự đổi** — nhưng
`cap_rf = min(CPI_5y + GDP_thực_15y, r_f)` đang bị **trần r_f = 6,80%** ràng buộc
(CPI+GDP ≈ 3,44 + ~6,2 = ~9,6% ≫ 6,80%) ⇒ `g_term` bất biến ⇒ FV bất biến **đúng bằng 0**, không
phải "xấp xỉ 0". 7/30 mã tính được; 23 mã bị gate loại trước khi chạm CPI (19 tài chính +
5 FCFE≤0 + 1 `CF_OA_3Y≤0` — `h2_dcf_delta.csv`).

**Điều kiện để kết luận này hết đúng** (phải mang theo, không được rút gọn thành "CPI không ảnh
hưởng DCF"): trần chỉ nhả khi `CPI_5y + GDP < r_f`, tức CPI trung bình 5 năm tụt xuống dưới
≈ 0,6% với GDP/r_f hiện tại. Nếu ai đổi `DCF_TERMINAL_MODE` sang `cpi` (default cũ) thì Δ
−0,0279pp đi thẳng vào `g_term` và FV đổi thật.

## 4. (c) Đề xuất wire tối thiểu — GO cho `macro_confidence_regime`, NO-OP cho DCF

**Đề xuất, CHƯA wire (job này chỉ finding):**
1. `cpi_vn.py`: thêm tầng **T1.5 = file FiinPro** đặt GIỮA T1 và T2 — T1 NSO live thắng tuyệt đối
   (nó là nguồn chính thức và tươi hơn), FiinPro thắng T2/T3 cho 2008-01..2026-08, T3 chỉ còn
   phục vụ **2007** (FiinPro không phủ). Không xoá T2: nó là fallback khi file mất.
2. Giữ nguyên MỌI công thức/ngưỡng của `macro_confidence_regime.py` — chỉ đổi nguồn, đúng tinh
   thần prereg (không đặt ngưỡng tuyệt đối mới trên dữ liệu mới).
3. Không cần chạm `dcf_valuation.py`: tác động đo được **đúng 0** với mode mặc định `cap_rf`.
4. **Đổi tên `NSO_CPI_YOY_AVG_REAL` → `NSO_CPI_CORE_YOY_REAL`** (`cpi_vn.py:77`). Tên + comment
   hiện nói "average/cumulative YoY (bình quân/YTD)", nhưng registry
   `macro/fiinprox_cpi_monthly.md` bẫy #1 đã đo: nó khớp **13/13 tháng với `core_yoy_pct`**
   (lạm phát **cơ bản**), không phải CPI bình quân. Rủi ro đổi tên = 0: grep toàn repo
   2026-09-27 xác nhận hằng số này **chỉ được ĐỊNH NGHĨA (dòng 77), không có một lần đọc nào**
   — `cpi_monthly_df()` dùng `NSO_CPI_YOY_REAL` (dòng 144). Phải sửa cả comment, vì trích nó
   là "CPI bình quân" ở bất kỳ báo cáo nào là sai số liệu.
5. Bản ghi provenance: file FiinPro là **snapshot 2026-09-14, không tự cập nhật**. Wire nó vào
   một module production đang đọc CPI tới tháng hiện tại ⇒ phải có freshness-check thật (§14),
   nếu không tháng 2026-09 trở đi sẽ âm thầm rơi về T2 proxy mà không ai biết.

**Cái KHÔNG được bán kèm:** không có bằng chứng nào trong job này nói việc thay CPI làm tăng
lợi nhuận hay cải thiện chất lượng tín hiệu. 27/185 tháng đổi nhãn là **thay đổi**, chưa được
đo là **tốt hơn** — muốn nói "tốt hơn" thì phải chạy chính chiến lược dùng `REG_*` với N = số
episode độc lập, mà số đó (≈13 episode 2011-2026) đã được chứng minh không đủ power cho bất kỳ
claim timing nào (job `Taylor_20260926_164143`, ngưỡng nền 33,5%).
