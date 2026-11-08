> **QUY ƯỚC CUỐI (user chốt 08/11/2026 10:50 ICT):** KHÔNG áp luật 3c chặt. Moat chỉ được THÊM vào định giá khi bền; NARROW/NONE = không thưởng nhưng KHÔNG trừ. **Headline = mô hình cơ sở hiện hành (REPORT_r3 08/11: tâm 17.491, P10 7.702, P90 30.677; 15.832/2.726 là r2, đã bị r3 thay thế)**; mọi 'bản chặt-3c / headline mới / chờ duyệt' bên dưới chỉ còn là **độ nhạy rủi ro** ('nếu về trung bình ngành'), KHÔNG phải kết luận định giá. Các sửa lỗi dữ liệu/công thức/peer trong tài liệu này vẫn có hiệu lực. Không mã nào trong 20 mã có moat bền ⇒ không thêm tham số moat.

# TV2 (PECC2) — ADDENDUM bước 3c (5F tầng b + moat trong mô hình) · 07–08/11/2026 · job `Taylor_20261107_172014`; **vòng sửa sau skeptic `Taylor_20261108_024226` (bản trước: `*_r1`)**

> **Đồng bộ r3 (08/11):** các bảng dưới dùng control r2 (15.832/2.726/30.675) làm điểm gốc để so sánh độ nhạy; headline hiện hành là REPORT_r3 (17.491/7.702/30.677).
> Bổ sung cho `REPORT_r2.md` (05/11). Không làm lại DD; mọi phần khác của REPORT_r2 giữ nguyên, kể cả §6 WARNING pháp lý.
> - Số: `calc/moat_5f_tv2.py` → `calc/moat_5f_tv2_out.{txt,json}` (control = tâm r2 15.832, assert khớp; chạy 2 lần md5 trùng `4159c42a…`). Bản WIDE (chỉ đo độ nhạy): `calc/moat_5f_tv2_wide.py` → `_wide_out.{txt,json}`.
> - Dữ liệu peer: `calc/bq_moat_tv1234_20261107.csv` (BQ `ticker_financial`, TV1–TV4, 2010Q1→2026Q3). Đọc **dòng Q4** của mỗi năm: ROE_Trailing = ROE 4 quý; GPM_P0/EBITM_P0 là TTM, nên dòng Q4 = số cả năm (bài học A).
> - Vòng sửa: `calc/moat_5f_tv2_fix.py` → `calc/moat_5f_tv2_fix_out.{txt,json}` (control r2 15.832 assert khớp; chạy 2 lần md5 trùng: json `8e42f383…`, txt `0c65c361…`). Quy ước BQ: GPM/NPM/EBITM/EBITDA_P0 là TTM (dòng Q4 = cả năm); ROIC_xY chỉ cập nhật ở dòng Q4.
> - 5F dựa trên kiến thức LLM, non-point-in-time ⇒ chỉ dùng cho DD sống, không đưa vào backtest.

## 1. Vị thế & lợi thế cạnh tranh (5F) — LÀM MỚI
**Tái dùng hay làm mới:** `data/moat_tags.csv` không có dòng TV2. `kb/projects/tv2-dd-20261028.md`/`-20261101.md` cũng không có audit 5F ⇒ **làm mới**. Phạm vi chỉ gồm dữ liệu đang có trong thư mục + BQ, không nghiên cứu thêm.

**Loại hình DN:** tư vấn thiết kế nguồn/lưới điện + EPC/tổng thầu theo dự án. Ít tài sản, nắm tiền ròng lớn (≈1.951 tỷ; lãi tài chính ≈44% LNTT 9T/26 [REPORT_r2 §7]).
⚠️ ROIC trong BQ của TV2 vô nghĩa: vốn đầu tư ≈ 0 nên ROIC10Y 2018Q4 = 98,9%, ROIC_Trailing 2012Q4 = 333%. ⇒ Chỉ dùng ROE làm chỉ báo; **không trích ROIC ở cả hai phía** (kể cả dòng tag).

| Lực | Đánh giá (số + nguồn) |
|---|---|
| Cạnh tranh nội ngành | Có 4 PECC nội địa (TV1–TV4) cùng các viện/nhà thầu tư nhân. GPM dòng Q4 2016–25: TV2 trung vị **14,6%**, TV3/TV4 trung vị **27,6%** / TB 27,8%. EBITM 2025: TV2 **3,9%**, TV3 2,6%, TV4 4,2% [CSV]. Chênh GPM là do cơ cấu EPC (EPC biên gộp thấp), không phải bằng chứng yếu thế cạnh tranh: EBITM 2025 của TV2 (3,9%) cao hơn TV3 (2,6%), thấp hơn TV4 (4,2%) — nằm giữa peer. Cạnh tranh cao. |
| Quyền lực người mua | Người mua chính là EVN và các chủ đầu tư nguồn (độc quyền mua, đấu thầu). Tỷ trọng doanh thu đến từ EVN/bên liên quan: *cần kiểm chứng*. Phải thu CMC (liên kết) 657–666 tỷ, thu tiền Q3 ≈ 0 [REPORT_r2 §6.3] ⇒ người mua ép được điều khoản thanh toán. Rất cao. |
| Quyền lực nhà cung cấp | Nhân lực kỹ sư cùng thiết bị/thầu phụ EPC. GPM thấp do cơ cấu EPC (thầu phụ/thiết bị chiếm phần lớn giá vốn); EBITM ngang peer nên chưa kết luận được nhà cung cấp ép biên hơn peer. Trung bình–cao. |
| Đối thủ mới | Rào cản là hồ sơ năng lực (thiết kế nhiệt điện/NLTT/lưới) và quan hệ EVN. Đã gọi tên được cơ chế, nhưng EPC NLTT 2018–21 vẫn đón nhiều nhà thầu tư nhân. Thị phần: *cần kiểm chứng*. Trung bình. |
| Sản phẩm thay thế | Thấp với khâu thiết kế (bắt buộc phải có); EPC thì thay được bằng tổng thầu khác. |
| **Lực thứ 6 (Nhà nước)** | Chiều thuận: QHĐ8. Chiều ngược: chu kỳ ROE 2016–21 (21–50%) trùng cửa sổ giá FIT điện mặt trời/gió. Cửa sổ chính sách đóng ⇒ ROE dòng Q4 2022–25 rơi về **4,0–7,4%** [CSV] = **đồng hồ cắt hào đã chạy**. ⚠️ Nhưng ROE_Trailing đã hồi: 2026Q1 10,4% → Q2 12,8% → **2026Q3 16,3% > Ke 13,5%** [CSV], chủ yếu nhờ lãi tài chính (≈44% LNTT 9T/26) chứ không phải biên EPC/tư vấn ⇒ đó là lợi suất từ tiền ròng, không chứng minh siêu ngạch từ hoạt động. Vụ án EVNNPT/PC1 cùng "13 pháp nhân" đánh vào kênh quan hệ EVN; chỉ để ở mức **WARNING**, không dùng ép biên (bài học E). |

**Ba điều kiện moat BỀN ⇒ KHÔNG BỀN**

| Điều kiện | Kết quả (cả hai phía, BQ dòng Q4) |
|---|---|
| (i) Siêu ngạch nhiều chu kỳ | ✗. **Phía thuận:** ROE5Y 2016–21 là 31,8–41,8%; **ROE_Trailing 2026Q3 = 16,3% > Ke 13,5%** (có lãi tài chính 44% LNTT). **Phía nghịch:** 2025Q4 ROE5Y **8,9%**, ROE_Min5Y **3,9%**, cả hai < Ke; ROE dòng Q4 < Ke **4 năm liền** (2022–25). Siêu ngạch chỉ có trong một cửa sổ chính sách, không lặp lại qua nhiều chu kỳ; số 2026Q3 mới 1 quý-TTM và dựa vào lãi float. |
| (ii) Cơ chế gọi tên được | ? Chưa xác lập: hồ sơ năng lực PECC + quan hệ EVN là giả thuyết, dựa trên hai mục *cần kiểm chứng* (tỷ trọng doanh thu EVN, thị phần). Không tính là ✓. |
| (iii) Không có đồng hồ cắt hào | ✗. Cửa sổ FIT đã hết; kênh EVN đang có WARNING pháp lý. |

**Kết luận: moat_tier = NONE · moat_type = REGULATORY/AFFILIATION** (cơ chế có thật nhưng không tạo ra siêu ngạch).
- Rủi ro số 1: không có HĐ EPC thay thế sau 2028 ⇒ ROE kẹt ở 4–7% (< Ke) như 2022–25 (ROE_Trailing 2026Q3 16,3% > Ke nhờ lãi tài chính, không nhờ EPC). Rủi ro này chính là trục "độ bền LN" của r2.
- Ghi chú tier: NARROW hay NONE cũng không đổi cách xử lý trong mô hình (đều không thưởng). Bảng §3 có cả hai.

## 2. Moat trong mô hình — KHÔNG thưởng; r2 KHÔNG nhất quán 3c (bài học C)
r2 dùng P/E nội tại (1 − g/ROE)/(r − g), với ROE = LNST kịch bản / VCSH ⇒ **RONIC ngầm = ROE kịch bản, vĩnh viễn**.
- Nhánh ROE > Ke được thưởng (tích cực 250/1.330,8 = 18,8%), nhánh ROE < Ke bị phạt (sập 70% ⇒ ROE ≈ 3–6%).
- Mức LN terminal = E × persist của riêng TV2, không neo ngành. ROE terminal kỳ vọng r2 = **12,09%**.
- ⇒ Không ghi "nhất quán". Dưới đây là **BẢN CHẶT-3C** chạy song song.

**Tham số chặt-3c** (cơ sở: moat NONE, bằng chứng (i)✗/(iii)✗ ở §1):
- RONIC = Ke **đối xứng** ở mọi nhánh (P/E terminal = 1/r; g không tạo giá trị). Không cắt một chiều.
- LNST terminal = ROE TB chu kỳ **ngành** × VCSH 1.330,8 tỷ, từ 2029 (NONE). NARROW: giữ E×persist 2029–30, fade tuyến tính 2031–32.
- Neo ngành = ROE dòng Q4 2012–25 của **TV3+TV4** (đối thủ PECC nội địa trực tiếp, n=28): **trung vị 14,76% / TB 14,15%**. Biến thể có TV1 (n=42): 13,82% / 12,95%. TV1 bị loại khỏi neo chính vì ROE 2023–25 do thuỷ điện kéo lên, không phải từ tư vấn [TV1 ADDENDUM §1]. **Neo NHẠY theo cửa sổ:** TV3+TV4 2016–25 14,76/13,96%, 2020–25 14,99/13,86%, nhưng **2022–25 (n=8) trung vị 12,16% / TB 12,43%** — đúng cửa sổ mà TV2 đang ở (bất đối xứng của NONE). Vì vậy không chọn một neo duy nhất: báo khoảng theo 3 neo (§2 bảng dưới).
- Kiểm hợp lý: ROE ngành ≈ Ke ⇒ giá trị terminal ≈ 1,05–1,09× VCSH = "không moat, giá trị ≈ sổ sách". Neo peer cũng chứa lãi float, giống ROE của TV2 ⇒ so được với nhau.
- Giữ nguyên ở mọi bản: 2 năm đầu E (t=1 = 2027, chiết khấu (1+r)^t, Gordon tại T chiết khấu (1+r)^T — **cùng quy ước năm của r2**, bài học H), trục CMC, trục kịch bản/×mult. Không đếm hai lần: pháp lý vẫn ngoài lưới như r2.

| Bản (CK 2,52% @5 tỷ) | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn @5 tỷ / sleeve 10–40tr |
|---|---|---|---|---|---|---|
| r2 hiện hành (control) | 15.832 | 2.726 | 15.843 | 30.675 | 84,1% | TRONG / TRONG |
| Chỉ RONIC=Ke (terminal vẫn E×persist) | 16.248 | 6.319 | 15.980 | 26.733 | 91,1% | TRÊN / TRÊN (P90 27,3k: **ranh giới**) |
| Chặt-3c NONE, neo Ke 13,5% (**tâm headline**) | **17.807** | 14.761 | 17.808 | 20.296 | 100% | **TRÊN / TRÊN** |
| Chặt-3c NONE, TV3+TV4 trung vị 2022–25 (12,16%) | 16.329 | 13.283 | 16.330 | 18.818 | 100% | TRÊN / TRÊN |
| Chặt-3c NONE, ROE riêng TV2 2022–25 (5,29%) | 8.740 | 5.693 | 8.740 | 11.228 | 100% | TRÊN / TRÊN |
| Chặt-3c NONE, TV3+TV4 trung vị 2012–25 (14,76%; cửa sổ thuận lợi nhất) | 19.201 | 16.154 | 19.201 | 21.689 | 100% | TRÊN / TRÊN |
| Chặt-3c NONE, TV3+TV4 TB | 18.528 | 15.481 | 18.528 | 21.017 | 100% | TRÊN / TRÊN |
| Chặt-3c NONE, +TV1 trung vị / TB | 18.165 / 17.200 | 15.118 / 14.153 | — | 20.654 / 19.688 | 100% | TRÊN / TRÊN |
| Chặt-3c NARROW, TV3+TV4 trung vị / TB | 18.278 / 17.815 | 14.240 / 13.777 | 17.985 / 17.522 | 22.672 / 22.210 | 100% | TRÊN / TRÊN |
| NARROW, giữ trục persist trên neo | 17.157 | 7.032 | 18.581 | 24.806 | 95,6% | TRÊN / TRÊN |

**Headline = KHOẢNG ~16,3k–19,2k** (neo 12,16% → 14,76%), **tâm theo neo Ke 13,5% = 17.807** (P90 20.296) — "giá trị ≈ sổ sách" ở cận Ke. Cận trên 19.201 là cửa sổ thuận lợi nhất và xoá rủi ro backlog EPC (rủi ro số 1) nên **không** đặt làm headline. ROE riêng TV2 2022–25 (8.740) là kịch bản nghịch, ghi để đo độ nhạy, không phải tâm. **Nhãn TRÊN ở mọi neo** (P90 cao nhất 21.689 < giá 27.400). Quy ước chờ Mike/user duyệt; SUMMARY.json và REPORT_r2 không bị sửa.

**Phần chênh do đâu** (từ control 15.832):
- RONIC=Ke: **+416** (+2,6%). Ở tâm, ROE ≈ 13,3% ≈ Ke, nên hai chiều thưởng/phạt gần triệt tiêu nhau; tác động chủ yếu là P90 giảm 30,7k → 26,7k.
- Neo ROE ngành: so với 16.248 là **+1.559** (neo Ke 13,5% → 17.807), **+81** (neo 12,16% → 16.329), **+2.952** (neo 14,76% → 19.201), **−7.508** (ROE riêng 5,29% → 8.740). Nhánh "sập 70%" bị thay bằng neo.
- Phân tán co lại mạnh (P10 2,7k → 14,8k; P90 30,7k → 20,3k, theo neo Ke) vì terminal không còn phụ thuộc kịch bản.
- ⚠️ Chặt-3c **xoá rủi ro riêng của TV2** (backlog EPC cạn, ROE 4–7% bốn năm liền). Bản "giữ persist trên neo" (17.157, P10 7.032) và neo 2022–25 (16.329) là cận dưới. ⇒ Khoảng chặt-3c: **~16,3k–19,2k**, tâm 17.807; kịch bản nghịch ROE riêng 8.740.

## 3. Độ nhạy WIDE / NARROW / NONE (nếu moat sai)

| Tier giả định | Cách đưa vào mô hình | Tâm | P10–P90 | Nhãn @5 tỷ / 10–40tr |
|---|---|---|---|---|
| WIDE (không có cơ sở, chỉ đo) | terminal = ROE riêng TV2 trung vị 2012–25 **22,79%**, RONIC = ROE đó | 27.046 | 22.659–31.945 | TRONG / TRONG (dưới giá 56,4%) |
| NARROW | §2, giữ 2 + fade 2 năm, TV3+TV4 | 17.815–18.278 | 13.777–22.672 | TRÊN / TRÊN |
| NONE | §2, neo từ 2029 (Ke / 2022–25 / 2012–25 / TB) | 16.329–19.201 (Ke: 17.807) | 13.283–21.689 | TRÊN / TRÊN |

- Ghi chú (không dùng để suy moat từ giá): giá 27.400 ≈ tâm bản WIDE ⇒ giá đang ngầm giả định ROE của cửa sổ FIT quay lại vĩnh viễn.
- Mức WIDE→NONE (tâm Ke 17.807): **−34%** tâm.

## 4. Thay đổi so với báo cáo hiện hành
**Có đổi, theo quy ước chặt-3c (chờ duyệt).**
- Tâm 15.832 → **17.807** (+12,5%; khoảng ~16,3k–19,2k).
- P10/P50/P90 2.726/15.843/30.675 → 14.761/17.808/20.296 (neo Ke).
- Nhãn **TRONG → TRÊN vùng**, ở cả cỡ 5 tỷ lẫn sleeve 10/20/40 triệu. Không ở ranh giới: giá cao hơn P90 lớn nhất trong mọi bản chặt-3c (25.327 @40tr, bản persist-trên-neo) 8,2%; với neo Ke P90 @40tr = 20.722.
- Nhãn TRÊN khớp với định nghĩa v3 ngày 01/11 và phản biện 01/11 [REPORT_r2 §0 Điều 7]. Riêng bản "chỉ RONIC=Ke" thì nhãn TRÊN nằm ở ranh giới.
- Tâm TĂNG nhưng nhãn XẤU đi: r2 có nhãn TRONG là nhờ đuôi phải (nhánh tích cực, RONIC = 18,8% vĩnh viễn); luật 3c cắt đuôi đó.
- Không đụng `dd_price_zones`, SUMMARY.json, REPORT_r2. Mike quyết.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi)
```
TV2,NONE,REGULATORY/AFFILIATION,L,"PECC2 = design consultancy + EPC; ROE 21-50% 2016-21 was FIT renewables policy window (clock already run), ROE Q4 4.0-7.4% 2022-25 < Ke 13.5% but ROE_Trailing 2026Q3 16.3% > Ke on financial income 44% of PBT; ROE_Min5Y 3.9% (2025Q4); GPM gap vs TV3/TV4 is EPC mix (EBITM 2025 3.9% vs 2.6%/4.2%); EVN buyer-concentration UNVERIFIED (revenue share not checked); CMC receivable 657-666 bn; LIVE scandal (ex-chair indicted, WARNING only)",2026-11-07,5f_dd_taylor_3c,N
```
- entry = **L** theo bài học G: cấu trúc ngành kém hấp dẫn (người mua độc quyền, ROE peer ≈ Ke). Ghi chú (chỉ ghi chú, không sửa): dòng TV1 hiện ghi entry=M cho cùng ngành ⇒ Mike rà cho thống nhất.
- ⚠️ Cần kiểm chứng (TV1 ADDENDUM, không thuộc TV2): chuỗi EBITM_P0 TV1 2022Q3→2022Q4→2023Q1 = 11,0%→30,2%→14,3% bất thường cho số TTM (TTM không nên nhảy rồi rơi lại ngay); chưa đối chiếu nguồn. moat_upgrade = N.
