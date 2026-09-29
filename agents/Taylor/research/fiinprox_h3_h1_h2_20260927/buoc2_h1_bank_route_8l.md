# BƯỚC 2 — H1: NPL/LLR FiinPro vào route BANK của 8L

Job `Taylor_20260926_164113` · Taylor · 2026-09-27
Nguồn: `mike/data/fiinprox_bank_ratios_quarterly_20260914.csv` (1.392 dòng, 27 mã ICB 8355,
2010Q1→2026Q2) · registry `fundamentals/fiinprox_bank_ratios_quarterly.md` (DERIVED).
ROE: `tav2_bq.ticker_financial` (`ROE_Trailing` → `ROE5Y` → `ROE3Y`, đúng thứ tự fallback của
`rating_8l_history.py::rate_bank_proxy`), 1.118 dòng mã-quý.

## 0. Sửa lại tiền đề của dispatch — `rate_bank()` KHÔNG phải cái đang chấm lịch sử

Dispatch viết "A/B `rate_bank()` hiện trạng (NaN 9/18 mã)". Đọc code (§1 skill quant-research):

- `rating_8l.py::rate_bank()` (AQ-aware) chỉ chạy trên **snapshot HÔM NAY**, đọc
  `data/bank_lens_v3.csv` — file **một dòng/mã**, không có chiều thời gian.
- Chuỗi rating lịch sử 2014-2026 mà V2.4 thật sự đọc (`tav2_bq.fa_ratings_8l`, 53.660 dòng,
  1.291 ngày, 2014-07-09→2026-10-11) do `rating_8l_history.py` sinh, và ở đó route BANK dùng
  **`rate_bank_proxy()` — ROE-only**, có chú thích rõ lý do: "no NPL/coverage history".
- `override_current_bank_aq()` áp `rate_bank` **chỉ cho dòng mới nhất mỗi mã**, lịch sử giữ proxy.

⇒ A/B đúng là **`rate_bank_proxy` (ROE-only, đang dùng cho backtest) vs `rate_bank` (AQ-aware) với
NPL/LLR FiinPro**. Đó là cái đã chạy dưới đây.

## 1. PREREG (khoá trước khi chạy)
- NPL/LLR chỉ dùng cho **thứ hạng / cổng nhị phân**; KHÔNG đặt ngưỡng tuyệt đối mới.
- Trễ công bố PIT: tại ngày hiệu lực dòng rating, chỉ dùng quý FiinPro **mới nhất đã qua
  ≥45 ngày sau ngày kết thúc quý (Q4: ≥90 ngày)**.
- GO/NO-GO quyết bởi (b): số quyết định V2.4 đổi.

## 2. Kết quả (b) — QUAN TRỌNG NHẤT: **0 quyết định V2.4 đổi, và KHÔNG THỂ đổi**

**Chứng minh bằng ngưỡng, không phải bằng backtest.** Hai hàm có cùng phân hoạch:

| | `rate_bank_proxy(ROE)` | `rate_bank(ROE, NPL, cov)` |
|---|---|---|
| ROE < 8% | 5 | 5 |
| 8% ≤ ROE < 12% | 4 | 4 |
| ROE ≥ 12% | 1 / 2 / 3 theo ROE | 1 / 2 / 3 theo ROE **và** AQ |

`rate_bank` chỉ dùng NPL/coverage ở hai nhánh đầu (`pristine` → 1, `strong` → 2); mọi trường hợp
còn lại có ROE ≥ 12% rơi vào `return 3`. ⇒ **rating ≤ 3 ⟺ ROE ≥ 12% ở CẢ HAI hàm**, độc lập hoàn
toàn với NPL/coverage.

Quét vét cạn **45.090 tổ hợp** (ROE 0→50% bước 0,1pp × 10 giá trị NPL gồm `None`/`NaN`/hai bên mỗi
ngưỡng × 9 giá trị coverage): **0 tổ hợp làm cổng nhị phân `rating ≤ 3` đổi dấu.**

**Thực nghiệm trên dữ liệu thật** (1.118 dòng mã-quý; 1.090 dòng = **97,5%** có NPL/LLR FiinPro dùng
được sau trễ công bố):

| proxy → AQ-aware | n |
|---|---|
| 1 → 3 | 187 |
| 2 → 3 | 138 |
| 1 → 2 | 91 |
| 2 → 1 | 11 |
| **Tổng rating đổi** | **427 (38,2%)** |
| **Cổng nhị phân ≤3 đổi** | **0** |

Chi tiết từng dòng: `h1_rating_changes.csv`. 20 mã có ≥1 quý đổi; nhiều nhất MBB(37) HDB(36)
SHB(34) VIB(34) ACB(27) BID(27) VPB(26) TPB(25) VCB(24) CTG(21).

Cả hai chiều đều xuất hiện (11 dòng **nâng** 2→1 khi AQ tinh khiết) ⇒ không phải một phép hạ bậc
một chiều do thiếu dữ liệu.

## 3. (c) R3 A/B — **KHÔNG CHẠY, có chủ đích**

Dispatch nói "nếu có đổi, chạy R3 A/B, kỳ vọng ≈0". Điều kiện đó **không thoả**: cái vào engine là
cổng nhị phân, và cổng đổi **0 lần**. Δ không phải "kỳ vọng ≈0" mà là **0 chính xác, theo cấu trúc**
— đốt ~20 phút engine để in lại đúng md5 `7d053e6201c9d107685ff4d1dd9d2d2a` không thêm bằng chứng gì.

Đã xác nhận rating vào R3 **chỉ** qua cổng: `ETF_LIQ=custompitg` → `_PIT_PARAMS["custompitg"] =
("none", "q2m5", 3)` ⇒ `quality="none"` ⇒ `QTILT` (1,50/1,25/1,00/0,70/0,40 — hàm CÓ phân biệt 1/2/3)
**không hoạt động**. Nếu R3 dùng `custompitgq` (`quality="tilt"`) thì 427 dòng đổi rating SẼ đổi
trọng số và kết luận này KHÔNG còn đúng — đó là điều kiện phải kiểm lại trước bất kỳ lần đổi
`ETF_LIQ` nào.

Cổng LAG (user chốt 2026-07-27, `rating ≤ 3` auto-exclude ≥4) cũng nhị phân ⇒ cùng kết luận.

## 4. Kết luận: **GO cho wire "thay NaN, không đổi công thức" — nhưng nó KHÔNG mang lại gì cho NAV**

- **Cái được**: chuỗi rating NH hiển thị đúng chất lượng tài sản 2010-2026 thay vì ROE-only; 9/18 mã
  hết NaN ở snapshot live; `override_current_bank_aq` không còn là ngoại lệ một-dòng.
- **Cái KHÔNG được**: 0 quyết định V2.4 đổi, ΔCAGR = 0 theo cấu trúc. Đây là **vệ sinh dữ liệu +
  chẩn đoán**, không phải nguồn lợi nhuận. Đừng trích nó như một cải thiện hiệu suất.
- **Rủi ro nếu wire**: bơm AQ vào chuỗi lịch sử làm rating NH **đổi 38,2% số dòng mã-quý**. Bất kỳ
  consumer nào dùng rating NH như BIẾN LIÊN TỤC (không phải cổng ≤3) sẽ đổi kết quả — đã kiểm
  `QTILT` (không hoạt động ở R3) nhưng **chưa** kiểm `regime_size_overlay.py` (dùng tier D/E) và các
  `*_screen.py`. Phải quét trước khi wire.
- **Sống sau 28/09**: OCR BCTC quý cho mã đang giữ, quy trình `bank_npl_coverage_primary` đã có.
  Bộ FiinPro chỉ cần cho LỊCH SỬ ⇒ hết trial không làm chết gì.

**Bẫy registry đã mang theo**: NPL FiinPro cao hơn OCR +1-2% tương đối (khác mẫu số) ⇒ chỉ dùng thứ
hạng/cổng, đúng như prereg; NIM luỹ kế quy năm (không dùng trong `rate_bank`); nhảy NPL thật
(SHB 2012Q3, STB 2015-17, NVB 2022-24) giữ nguyên, không lọc.

## Nghiệm thu quant-skeptic — **CONFIRMED (high)**, mở rộng phạm vi chứng minh + 1 lỗ hổng LIVE

`bus/inbox/quant-skeptic.jsonl` 2026-09-26T17:35:21Z · log `logs/verify_20260926_173015_1698566.log`.
Reviewer tái lập `h1_bank_ab.py` khớp từng số + md5 CSV, khớp BQ 53.660 dòng `fa_ratings_8l`, và
join độc lập xác nhận 962/962 dòng không-mới-nhất đúng bằng proxy ROE-only (18 lệch đều là dòng
mới nhất bị override) ⇒ **tiền đề của tôi đúng**.

Reviewer **lấp luôn 2 consumer tôi khai là CHƯA KIỂM**: mọi consumer V2.4 đều nhị phân ở biên 3/4 —
`custom_basket.py:945` gate ≤3 (QTILT chỉ khi `quality=='tilt'`, dòng 1085; `custompitg` =
`('none','q2m5',3)`), `regime_size_overlay.py:28 WEAK_RATING_MIN=4`, `golive_recommend_v23.py:683
rating>=4`, `CAPIT_QEXIT r8l >3`, `build_universe_pit_quality QUALITY_OK<=3`. Không runner production
nào đặt `BASKET_GATE_RATING=2` hay `custompitgq`.

**Lỗ hổng reviewer tìm ra, nằm NGOÀI claim của tôi nhưng chạm LIVE — phải giải quyết trước khi wire:**
dòng MỚI NHẤT mỗi NH do `override_current_bank_aq()` sinh từ `bank_lens_v3.csv` (nguồn ROE KHÁC) +
fail-open `bank-nodata -> 3`. Hiện tại nó **đã** làm lệch gate hôm nay cho BAB/BVB/PGB (4→3),
NVB/SGB (5→3), KLB (1→4). Không mã nào trong số đó thuộc custom30V ⇒ tác động live hôm nay = 0,
nhưng bản wire **phải khai rõ nguồn ROE nào thắng ở dòng mới nhất**, và fail-open "không có dữ liệu
⇒ rating 3" là vấn đề CÓ SẴN, độc lập với job này — NVB/SGB đang được chấm 3 live trong khi proxy
nói 5.
