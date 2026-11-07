# ADDENDUM 5F — FPT · 07/11/2026 · **r2** (sau phản biện skeptic cụm 1) · job `Taylor_20261107_122439`

> Bổ sung bước 3c cho `REPORT_r2.md` (05/11). **Không làm lại DD**; mọi phần khác của REPORT_r2 giữ nguyên. Bản r1: `ADDENDUM_5F_r1.md`.
> Tái lập (chạy 2 lần, md5 trùng): `$DNA_PYEXE -I calc/fpt_5f_r2.py` → `fpt_5f_r2_out.txt` md5 bd4ed12d…; `calc/fpt_5f_r2_xau.py` → `fpt_5f_r2_xau_out.txt` md5 88bb0ede…
> (r1 `fpt_5f.py` vẫn tái lập NARROW/SYM/NONE). Chân đối chứng WIDE = mô hình hiện hành ⇒ tâm **54.203** khớp REPORT_r2 (0 đ lệch).
> Số ROIC/ROE/GPM: `bq query tav2_bq.ticker_financial` 07/11/2026, **có 2026Q3** (công bố 29/10). GPM so sánh dùng **TB 4 quý (trung bình giản đơn của GPM_P0..P3, không trọng số doanh thu)**; GPM_P0 là giá trị MỘT quý.
> Non-point-in-time (kiến thức LLM + tag 06/2026) ⇒ CHỈ dùng DD sống, cấm đưa vào backtest.

## 1. Vị thế & lợi thế cạnh tranh (5F) — **TÁI DÙNG**
**Nguồn:** `data/moat_tags.csv` dòng FPT, `asof 2026-06-05`, src `5f_validated_compet` = 5 tháng < 12 ⇒ tái dùng (luật tần suất 06/11); kiểm nhanh từ `dd_FPT_20261101/REPORT.md`, `SKEPTIC_20261101.md`, BQ.

| | Nội dung (tái dùng) |
|---|---|
| Loại hình DN | Dịch vụ CNTT xuất khẩu (chênh lệch chi phí nhân lực + quan hệ khách hàng) + CNTT trong nước + giáo dục; FTEL (45,66%) & FRT (46,54%) là cổ phần, không hợp nhất FTEL từ 01/01/2026 |
| **moat_tier** | **NARROW** |
| **moat_type** | SWITCHING/COST/SCALE (khoá quan hệ KH Nhật + quy mô nhân lực) |
| **Rủi ro số 1** | GenAI coding agent hàng hoá hoá mô hình gia công theo người-tháng (cùng lực đã hạ peer Ấn Độ 2026) |

| Lực | Bằng chứng định lượng · nguồn |
|---|---|
| Cạnh tranh nội ngành | ROIC5Y FPT **17,7%** vs CMG 7,9%, CMT 9,8%, ELC 5,7%, ITD 8,4%. **GPM TB4Q** 2026Q3 **35,1%** (quý Q3 32,9%); 2026Q2 36,2% (quý 34,7%) vs CMG 18,3%, ITD 27,8% (Q3), ELC 19,3% (Q2; Q3 chưa có P0, TB 3 quý 17,6%); CMT không có GPM. Trung vị peer ~19,3%, trung bình ~21,8% ⇒ FPT vượt xa ở cả hai, nhãn không nhạy cách chọn. **Peer CMG/CMT/ELC/ITD đều NỘI ĐỊA ⇒ chỉ chứng minh dẫn đầu nội địa, là bằng chứng YẾU cho hào xuất khẩu**; peer toàn cầu (TCS/Infosys) *cần kiểm chứng* |
| Đối thủ mới | Hợp đồng >1 triệu USD 9T **163 (+29,4%)**, KH >500k USD 367 (+9,6%) [KQKD9T p6]. Số kỹ sư/thị phần xuất khẩu VN *cần kiểm chứng* |
| Quyền lực người mua | Nhật = **46%** DT nước ngoài 9T (13.197 tỷ); top-10 KH *cần kiểm chứng* |
| Quyền lực nhà cung cấp (lao động) | GPM **quý**: 2026Q2 34,7% → 2026Q3 32,9% (−1,8pp); TB4Q 36,2% → 35,1% [BQ]. Phần do thôi hợp nhất FTEL chưa tách được. (Chuỗi 2020Q4/2024Q4 của r1 là GPM_P0 một quý, không phải TTM ⇒ **bỏ**) |
| Sản phẩm thay thế | JPY H1 +22,6% → Q3 **~+15,3%**; DX nước ngoài Q3 **+3,8%**; APAC 9T **−4,6%**; ngược chiều: AI/Data 9T 2.915 tỷ **+55%** [`dd_FPT_20261101/REPORT.md` §0, §5] |
| **Lực thứ 6** | (a) **Đồng hồ GenAI** = cơ chế cắt hào đang chạy; (b) FTEL: Nhà nước (Bộ Công an) ~50,16% ⇒ chân viễn thông (hào WIDE) ra khỏi lõi; (c) ETR 11,1% → 15,2% (*cần kiểm chứng*) |

**Kiểm nhanh từ 05/06:** không đổi tier; rủi ro số 1 hiện thực một phần (Nhật Q3 giảm tốc, GPM quý Q3 −1,8pp) ⇒ củng cố NARROW.

## 2. Ba điều kiện moat BỀN
| ĐK | Kết quả | Bằng chứng (cả hai phía) |
|---|---|---|
| (i) Siêu ngạch nhiều chu kỳ | **TRƯỢT trên ROIC; chỉ qua trên ROE** | **ROIC** (Ke 13,5%): ROIC5Y 2018Q4 **11,8%**, 2019Q4 **12,3%** (< Ke); 2025Q4–2026Q3 17,7% (> Ke); ROIC10Y **15,9%**; ROIC_Min5Y 13,7% ≈ Ke; **ROIC_Min10Y 6,75%** (BQ 2026Q3). **ROE** (riêng, không thay ROIC): ROE_Min10Y 20,2%, ROE_Min5Y 23,0%, ROE TTM 25,5%. Chuỗi gồm FTEL ⇒ ROIC riêng CNTT *cần kiểm chứng* |
| (ii) Cơ chế gọi tên được | ĐẠT | switching cost KH Nhật + quy mô giao hàng (tag) |
| (iii) Không có đồng hồ cắt hào | **TRƯỢT** | GenAI thay thế người-tháng (lực 6) |
⇒ **moat_durable = false**. Không thưởng RONIC > Ke.

## 3. Moat trong mô hình — mô hình hiện hành ĐANG NGẦM thưởng moat kiểu WIDE ⇒ không nhất quán
RONIC ngầm **terminal** = g_T/(1−conv): XẤU 5,0% · CƠ SỞ 16,0% · TỐT 26,7% (Ke 13,5%). RONIC ngầm **5 năm explicit** = g1/(1−conv): XẤU 5,0% · **CƠ SỞ 36%** · **TỐT 93%**. Cả hai CƠ SỞ/TỐT ≫ Ke, và ROE giữa chu kỳ > Ke kéo dài; **tách bạch:**
- **Terminal (luật 3c, RONIC = Ke ĐỐI XỨNG):** conv_T = 1 − g_T/Ke = **0,704** (CƠ SỞ/TỐT) và **0,778** (XẤU, nâng từ 0,40). Cắt một chiều (r1) chỉ gỡ phía trên, giữ XẤU dưới Ke ⇒ không phải luật 3c; nay là **độ nhạy**, không phải headline.
- **Explicit 5 năm:** giữ nguyên r2 (g1 3/9/14%, conv 0,40/0,75/0,85). **Không có cơ sở bên ngoài** để RONIC explicit 36%/93% vượt ROIC5Y 17,7% hay ROE TTM 25,5% ⇒ báo **độ nhạy cap** (§4), không tự chọn cap làm headline (quy ước chờ Mike).
- Bội số premium không dùng (FCFE + cổ phần thị giá). Biên: không có tham số biên riêng (nằm trong g1 × LN lõi TTM); r2 không giữ GPM riêng trên TB ngành.
- Vụ án/pháp lý: không dùng làm lý do ép biên/m_T (chỉ WARNING).

## 4. Kết quả & độ nhạy (sau CK thanh khoản 5 tỷ 0,187%; r 13,5%; lưới 540 kết cục; giá 53.900; nhãn TRONG/TRÊN theo `r2common`)
| Phương án | Tâm | P10 | P50 | P90 | Trung tâm | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|---|
| WIDE (= REPORT_r2) | 54.203 | 32.389 | 55.182 | 74.557 | 58.579 | 47,5% | TRONG |
| **HEADLINE — NARROW_SYM (luật 3c: RONIC_T=Ke đối xứng)** *(quy ước chờ Mike duyệt)* | **55.051** | **42.312** | 56.446 | **68.242** | 57.110 | 38,5% | **TRONG** |
| Downside có dữ liệu: SYM cho CƠ SỞ/TỐT, XẤU terminal giữ conv 0,40 (RONIC 5% < Ke) | 52.238 | 34.507 | 56.446 | 68.242 | — | 38,5% | TRONG |
| Cắt một chiều (r1) | 51.525 | 32.389 | 54.908 | 68.242 | 57.110 | 47,7% | TRONG |
| NONE (RONIC ≤ Ke cả 5 năm + terminal; cận trên) | 45.517 | 32.389 | 49.023 | 53.360 | 50.550 | 94,1% | TRÊN |

Độ nhạy **cap RONIC explicit** (conv_explicit = min(conv, 1 − g1/cap)):
| Terminal \ cap | không cap | **25,5%** (ROE TTM) | **17,7%** (ROIC5Y) |
|---|---|---|---|
| WIDE | 54.203 | 51.902 (P90 68.258) | 50.067 (P90 64.677) |
| Một chiều | 51.525 | 49.224 (P90 60.616) | 47.389 (P90 56.436, 67,9% dưới giá) |
| **SYM** | **55.051** | 52.749 (P10 42.312, P90 61.067) | 50.915 (P90 56.997, 58,5% dưới giá) |
Mọi ô đều **TRONG vùng** (kể cả cap 17,7%).

Tách thay đổi của headline so với WIDE (đo bằng 2 phương án trên): gỡ thưởng WIDE ở CƠ SỞ/TỐT = **−2.678**; nâng XẤU lên Ke = **+3.526**; ròng **+848**. **Phần dương đến từ giả định XẤU RONIC=Ke (đối xứng), không từ dữ liệu** — dữ liệu (conv 9T/26 −0,12; FY25 0,60) ủng hộ XẤU dưới Ke ⇒ phương án downside 52.238. Cap explicit −2.3k…−4.1k tuỳ cap.

## 5. Thay đổi so với báo cáo hiện hành
**Có đổi giá trị, KHÔNG đổi nhãn (TRONG vùng ở mọi phương án).** Theo luật 3c (headline NARROW_SYM): tâm 54.203 → **55.051 (+848; +1,6%)**, P10 32.389 → **42.312**, P50 55.182 → 56.446, P90 74.557 → **68.242 (−6.315)**; giá trị tại tham số trung tâm 58.579 → 57.110. Vùng bị **thu hẹp cả hai phía**; ngưỡng TRÊN vùng 74.557 → 68.242. Phương án downside XẤU<Ke: 52.238 (P10 34.507); cắt một chiều 51.525 chỉ là độ nhạy. Không ghi `dd_price_zones.json`, không sửa REPORT_r2/SUMMARY.json — Mike quyết quy ước (đối xứng vs downside) và cap explicit.

## 6. Đề xuất `data/moat_tags.csv`
**Không cần dòng mới** (tag 05/06/2026 còn hiệu lực; tier không đổi). Nếu muốn ghi vết, nối vào `risk1` (human-curated): `"; 2026-11-07 check: Q3/26 JPY ~+15% (H1 +22,6%), DX NN Q3 +3,8%, GPM quý Q3 32,9% (−1,8pp) = risk1 đang hiện thực một phần; ROIC_Min5Y 13,7% ≈ Ke, ROIC_Min10Y 6,75%, ROIC5Y 2018-19 11,8-12,3% < Ke (gồm FTEL)"`.

## 7. Cần kiểm chứng
ROIC riêng mảng CNTT (bỏ FTEL) 5–10 năm; top-10 KH; số kỹ sư/thị phần xuất khẩu; GPM peer toàn cầu cùng định nghĩa; cơ sở RONIC explicit 36%/93%; nguyên nhân ETR tăng; GPM TB4Q chưa trọng số doanh thu.
