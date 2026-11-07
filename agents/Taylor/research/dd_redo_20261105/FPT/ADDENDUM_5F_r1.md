# ADDENDUM 5F — FPT · 07/11/2026 · job `Taylor_20261107_120553`

> Bổ sung bước 3c cho `REPORT_r2.md` (05/11). **Không làm lại DD**; mọi phần khác của REPORT_r2 giữ nguyên.
> Tái lập: `$DNA_PYEXE -I calc/fpt_5f.py > calc/fpt_5f_out.txt` (exec nguyên phần mô hình của `fpt_r2.py`, không ghi file nào của r2;
> md5 `fpt_5f.py` 9c70197b…, `fpt_5f_out.txt` 7bb0c9de…). Chân đối chứng WIDE = mô hình hiện hành ⇒ tâm **54.203** khớp REPORT_r2 (0 đ lệch).
> Số ROIC/ROE/GPM: `bq query` `tav2_bq.ticker_financial` 07/11/2026 (FPT, CMG, CMT, ELC, ITD; quý Q4 2018–2025 + 2026Q2).
> Non-point-in-time (kiến thức LLM + tag 06/2026) ⇒ CHỈ dùng DD sống, cấm đưa vào backtest.

## 1. Vị thế & lợi thế cạnh tranh (5F) — **TÁI DÙNG**
**Nguồn:** `data/moat_tags.csv` dòng FPT, `asof 2026-06-05`, src `5f_validated_compet` = **5 tháng < 12 tháng ⇒ tái dùng** (luật tần suất 06/11). Chỉ kiểm nhanh từ dữ liệu đang có trong thư mục (`dd_FPT_20261101/REPORT.md`, `SKEPTIC_20261101.md`, BQ).

| | Nội dung (tái dùng) |
|---|---|
| Loại hình DN | Dịch vụ CNTT xuất khẩu (chênh lệch chi phí nhân lực + quan hệ khách hàng) + CNTT trong nước + giáo dục; FTEL (45,66%) & FRT (46,54%) là cổ phần, không còn hợp nhất FTEL từ 01/01/2026 |
| **moat_tier** | **NARROW** |
| **moat_type** | SWITCHING/COST/SCALE (khoá quan hệ khách hàng Nhật + quy mô nhân lực) |
| **Rủi ro số 1** | GenAI coding agent làm hàng hoá hoá mô hình gia công theo người-tháng (cùng lực đã hạ peer Ấn Độ 2026) |

| Lực | Bằng chứng định lượng · nguồn |
|---|---|
| Cạnh tranh nội ngành | FPT ROIC5Y **17,7%** vs CMG 7,9%, CMT 9,8%, ELC 5,7%; GPM TTM **34,7%** (2026Q2) vs CMG 18,1%, ELC 17,5% [BQ]. Peer toàn cầu (TCS/Infosys) — biên so sánh *cần kiểm chứng* |
| Đối thủ mới | Quy mô + quan hệ: hợp đồng >1 triệu USD 9T **163 (+29,4%)**, KH >500k USD 367 (+9,6%) [KQKD9T p6]. Số kỹ sư/thị phần xuất khẩu VN *cần kiểm chứng* |
| Quyền lực người mua | Nhật = **46%** DT nước ngoài 9T (13.197 tỷ) — tập trung theo thị trường; top-10 khách hàng *cần kiểm chứng* |
| Quyền lực nhà cung cấp (lao động) | Lương kỹ sư tăng thu hẹp chênh lệch (tag); GPM TTM 39,6% (2020Q4) → 37,7% (2024Q4) → 34,7% (2026Q2) [BQ] — một phần do thôi hợp nhất FTEL biên cao, chưa tách được |
| Sản phẩm thay thế | GenAI: JPY H1 +22,6% → Q3 **~+15,3%**; DX nước ngoài Q3 **+3,8%**; USD Q3 +5,8%; APAC 9T **−4,6%**. Chiều ngược: AI/Data 9T 2.915 tỷ **+55%** [`dd_FPT_20261101/REPORT.md` §0, §5] |
| **Lực thứ 6** | (a) **Đồng hồ GenAI** = cơ chế cắt hào đang chạy; (b) FTEL: Nhà nước (Bộ Công an) kiểm soát ~50,16% ⇒ chân viễn thông (hào WIDE) đã ra khỏi lõi; (c) ETR 11,1% → 15,2% (thuế tối thiểu toàn cầu? *cần kiểm chứng*) |

**Kiểm nhanh "có gì đổi hào từ 05/06":** không đổi tier. Rủi ro số 1 đang **hiện thực một phần** (Nhật giảm tốc Q3, DX nước ngoài Q3 +3,8%) — củng cố NARROW, không có cơ sở nâng. Chiều tích cực (mega deal +29%, AI +55%) chưa đủ đảo.

## 2. Ba điều kiện moat BỀN
| ĐK | Kết quả | Bằng chứng |
|---|---|---|
| (i) Siêu ngạch nhiều chu kỳ | **ĐẠT một phần** | ROE_Min10Y **20,2%**, ROE_Min5Y 23,0%, ROIC5Y 17,7% > Ke 13,5%; nhưng **ROIC_Min5Y 13,7% ≈ Ke** và chuỗi 2018–2025 **gồm FTEL** (chân WIDE đã tách) ⇒ ROIC riêng CNTT *cần kiểm chứng* |
| (ii) Cơ chế gọi tên được | ĐẠT | switching cost quan hệ Nhật + quy mô giao hàng (tag) |
| (iii) Không có đồng hồ cắt hào | **TRƯỢT** | GenAI thay thế người-tháng (lực 6) |
⇒ **moat_durable = false** (cho mục đích thưởng terminal). Không thưởng RONIC > Ke.

## 3. Moat trong mô hình — **phát hiện: mô hình hiện hành ĐANG NGẦM thưởng moat kiểu WIDE**
Terminal `tv = E·(1+g_T)·conv/(Ke−g_T)` ⇒ RONIC ngầm định = g_T/(1−conv): **XẤU 5,0% · CƠ SỞ 16,0% · TỐT 26,7%** (Ke 13,5%) — chính `dd_FPT_20261101/REPORT.md` bảng §8 đã ghi cột này. CƠ SỞ/TỐT > Ke **vĩnh viễn** = thưởng WIDE, trái tag NARROW ⇒ không phải "đã ngầm, nhất quán", mà **không nhất quán** ⇒ sửa.

| Tham số (đề xuất) | Giá trị | Cơ sở |
|---|---|---|
| Thời gian siêu ngạch (fade) | **N = 5 năm** tường minh (g1 3/9/14%, conv theo kịch bản, giữ nguyên) | moat NARROW switching-cost Nhật; ROIC5Y 17,7%, ROE_Min10Y 20,2% [BQ] |
| RONIC terminal | **≤ Ke**: conv_T = min(conv, 1 − g_T/Ke) ⇒ CƠ SỞ 0,75 → **0,704**, TỐT 0,85 → **0,704** | NARROW + lực 6 GenAI ⇒ không thưởng (luật 3c) |
| XẤU (RONIC 5% < Ke) | **giữ nguyên** | là phạt có dữ liệu (conv 9T/26 −0,12, FY25 0,60), không phải thưởng moat; bản đối xứng nâng lên Ke ở §4 |
| Bội số premium | **không dùng** | mô hình FCFE + cổ phần thị giá ⇒ không đếm hai lần |
| Biên trung hạn | không có tham số biên riêng (nằm trong g1 × LN lõi TTM) | — |

## 4. Độ nhạy WIDE / NARROW / NONE (sau CK thanh khoản 5 tỷ 0,187%; r 13,5%; lưới 540 kết cục `wpct`)
| Moat | Cách đưa vào | Tâm | P10 | P50 | P90 | Trung tâm | % dưới giá | Nhãn @53.900 |
|---|---|---|---|---|---|---|---|---|
| **WIDE** (= REPORT_r2) | RONIC_T ngầm 16/26,7% | 54.203 | 32.389 | 55.182 | 74.557 | 58.579 | 47,5% | TRONG vùng |
| **NARROW (đề xuất)** | RONIC_T ≤ Ke | **51.525** | **32.389** | **54.908** | **68.242** | 57.110 | 47,7% | **TRONG vùng** |
| NARROW đối xứng | RONIC_T = Ke cả XẤU | 55.051 | 42.312 | 56.446 | 68.242 | 57.110 | 38,5% | TRONG vùng |
| NONE | RONIC ≤ Ke cả 5 năm + terminal (cận trên: không fade ROIC vốn hiện hữu) | 45.517 | 32.389 | 49.023 | 53.360 | 50.550 | 94,1% | TRÊN vùng |

Đọc: moat sai một bậc (WIDE thật) ⇒ tâm +2.678 (+5,2%), P90 +6.315; sai xuống NONE ⇒ tâm −6.008 (−11,7%), giá vượt P90. P10 không đổi ở 3/4 bản vì do nhánh XẤU quyết định (REPORT_r2 §2), và XẤU vốn đã RONIC < Ke.

## 5. Thay đổi so với báo cáo hiện hành
**Có đổi giá trị, KHÔNG đổi nhãn.** Áp NARROW (RONIC terminal ≤ Ke): tâm **54.203 → 51.525 (−2.678; −4,9%)**, P10 32.389 → 32.389, P50 55.182 → 54.908 (−274), P90 **74.557 → 68.242 (−6.315; −8,5%)**; giá trị tại tham số trung tâm 58.579 → 57.110. Giá 53.900 = tâm +4,6% (trước −0,6%) — vẫn **TRONG vùng**, nhưng vùng hẹp phía trên (ngưỡng TRÊN vùng 74.557 → **68.242**). Lý do duy nhất: gỡ thưởng moat WIDE ngầm ở terminal. Bản đối xứng (nâng XẤU lên Ke) cho tâm 55.051 — Mike chọn quy ước; đề xuất của tôi là bản bất đối xứng (chỉ gỡ thưởng, giữ phạt có dữ liệu). Không ghi `dd_price_zones.json`, không sửa REPORT_r2/SUMMARY.json — Mike quyết.

## 6. Đề xuất `data/moat_tags.csv`
**Không cần dòng mới** (tag 05/06/2026 còn hiệu lực đến 05/06/2027; kiểm nhanh không đổi tier). Nếu muốn ghi nhận dấu vết kiểm nhanh, đề xuất giữ nguyên tier/type, chỉ nối vào `risk1`: `"; 2026-11-07 check: Q3/26 JPY ~+15% (H1 +22,6%), DX NN Q3 +3,8% = risk1 đang hiện thực một phần; ROIC_Min5Y 13,7% ≈ Ke (gồm FTEL)"` — human-curated, không tự sửa.

## 7. Cần kiểm chứng
ROIC riêng mảng CNTT (bỏ FTEL) 5–10 năm; top-10 khách hàng; số kỹ sư/thị phần xuất khẩu; GPM peer toàn cầu cùng định nghĩa; nguyên nhân ETR tăng.
