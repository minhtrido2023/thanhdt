# TV1 (EVNPECC1) — rà luật "đầu tư dự án mới" 03/11/2026

## 1. Tâm/vùng hiện hành + nguồn
- Sổ `kb/dd_price_zones.json` không đọc trực tiếp được từ cwd; dùng dòng sổ trích trong `close_20261103.md`: dd_date 2026-11-02, **tâm 18.100 (expected_weighted), vùng 11.400–24.200** (P20–P80 lưới có trọng số, toàn lưới 4.600–44.900), ghi "rev5 (Mike 02/11 ~22:55): tâm = kỳ vọng 5 kịch bản giá PPA x 4 kịch bản tư vấn (INTRINSIC_v2)".
- **Tâm HIỆN HÀNH = bản MÙ v2**: `research/dd_TV1_blind_20261102/INTRINSIC_v2.md` (+ `valuation_blind_v2.py`, `valuation_blind_v2_out.txt/.json`).
- `research/dd_TV1_20261102/REPORT.md` (vòng 8, tâm ~18.000, vùng 15.800–20.600, P/E+DDM, `calc/valuation.py`) là báo cáo có-giá, KHÔNG phải tâm sổ; hai tâm gần nhau (18.000 vs 18.100) nhưng khác phương pháp và khác vùng.

## 2. Dự án/cam kết vốn trong báo cáo
- **Điện mặt trời nổi/lòng hồ SB5 46 MWp + 5 MW BESS, ~800 tỷ vốn, ~90 tỷ DT/năm** (baodauthau 27/06/2025; ĐHĐCĐ 30/04/2026 "vướng thủ tục"). Chưa vào quy hoạch Đà Nẵng mới, chưa có cơ chế giá, chưa có quyết định chủ trương. Bằng chứng: `dd_TV1_blind_20261102/valuation_blind.py:144-149`, `INTRINSIC.md:128-130`, `INTRINSIC_v2.md` §5 (mục "đã phản ánh" số 6); `dd_TV1_20261102/REPORT.md:318` (M8), `:90`, `:414`.
- Nhà máy điện hiện hữu SB5 (57 MW, TMĐT 1.372 tỷ, vận hành từ 2013) KHÔNG phải dự án mới: bậc giá PPA 2027+ (949/600/520/440/340) là giá của tài sản hiện hữu, không phải cung mới. Không có nhà máy/mỏ/M&A mới khác. Mảng tư vấn: đường ống theo capex EVN (không phải cam kết vốn của TV1); Tuyên Quang MR (hợp đồng tư vấn 81,7 tỷ, là doanh thu).
- Không có WACC/Ke riêng cho dự án; Ke chung 12,85% (`valuation_blind_v2.py:11-12`).

## 3. Mô hình có TRỪ ở base không
- **Không trừ, không cộng.** ĐMT nổi bị loại khỏi tâm ("KHÔNG TÍNH", `valuation_blind.py:148-149`); tính riêng chỉ để diễn giải: IRR ~6,8% < Ke, NPV@Ke ~ -296 tỷ ở vốn công bố, và nêu rõ "ai tính nó như động lực là tính quá tay" (`INTRINSIC.md:258`). Cấu phần tâm (thuỷ điện 12.500 + tư vấn 8.000 + tiền ròng -2.400) không chứa vốn ĐMT; `valuation_blind_v2_out.txt:51` tiền ròng -64,4 tỷ gồm quỹ KTPL -40,7 (B2) và nợ tranh chấp, không liên quan ĐMT. REPORT.md cũng chỉ để ĐMT làm trigger M8 (`:318`), không đưa vào SOTP.
- Bản chất = tương đương NPV 0/sổ sách (không giá trị cộng, không trừ). Không có khoản CỘNG thiếu cơ sở từ dự án.
- Các trừ khác KHÔNG phải dự án mới nên nằm ngoài luật này, nhưng nêu để minh bạch: (i) phân bố giá PPA có 0,20 ở 340 đ/kWh và 0,20 ở 440 (kỳ vọng 509 vs 949 hiện hành) — căn cứ độc lập có: văn bản 2018 duy nhất EVN NQ 286/NQ-HĐTV + Cục ĐTĐL 1374/ĐTĐL-GP (bậc 243,66 + O&M ~95 = 338), BCTN 2025 tr.38 "giá điện sụt giảm", lời lãnh đạo 500-600 qua KBSV (bản gốc chưa kiểm); là rủi ro hợp đồng cụ thể quan sát được, không phải "nguồn cung dự án làm sập giá"; (ii) Ke 12,85% áp lên thuỷ điện hiện hữu (cao hơn lãi vay TMĐT), độ nhạy Ke 10%: 25.300, 12%: 19.800 — không phải NPV âm của dự án mới.

## 4. Phân loại
**KHÔNG_VẤN_ĐỀ** (với luật dự án mới). Ghi chú: tâm vẫn nhạy với Ke/giá PPA (ngoài phạm vi luật này).

## 5. Hiệu ứng khi đặt dự án ở sổ sách/NPV 0
**0 đ/cp, 0%.** Không cần chạy lại: dự án ĐMT chưa nằm trong tâm nên NPV 0 = trạng thái hiện tại (đo từ `valuation_blind.py:144-149` và cấu phần ở `valuation_blind_v2_out.txt:66`; không chạy lại, ước lượng theo cấu trúc). Nếu trước đây từng tính ĐMT vào tâm thì bằng chứng cho thấy ngược lại. Tham chiếu: -296 tỷ NPV là kịch bản diễn giải, nếu vô tình trừ sẽ là khoảng -11.000 đ/cp (ước lượng: 296 tỷ / 27 tr cp, vốn ~27 tr cp suy từ 2.412 đ/cp = 64,4 tỷ -> ~26,7 tr cp) — nhưng KHÔNG được trừ trong tâm.

## 6. Giá 03/11 vs tâm (riêng)
- Giá đóng 03/11 = 19.600 (`close_20261103.md`): +8,3% so tâm gốc 18.100, +71,9% so đáy vùng.
- Tâm điều chỉnh = tâm gốc 18.100 (không đổi). Ngưỡng ứng viên tâm x 0,85 = 15.385; giá 19.600 > 15.385 -> **nhãn KHÔNG đổi** ("TRONG vùng" 11.400–24.200, không phải ứng viên).
