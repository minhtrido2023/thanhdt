# TV1 — Giai đoạn 2: so giá trị nội tại đã khoá với giá thị trường

Viết SAU khi khoá (`LOCK.txt` 21:54:32 ICT, md5 INTRINSIC.md `0e194156…`, kiểm lại `md5sum -c` OK). Không sửa INTRINSIC.md.
Tái lập: `python3 -I phase2/compare.py` (đọc `phase2/dnse_20261102.json`, DNSE fetch 21:54:42 ICT).

## 1. Giá và bội số

| | |
|---|---|
| Giá DNSE latest_trade | **19.500 đ** (khớp 14:34:40 ngày 02/11/2026; trung bình phiên 19.352; đóng cửa 30/10 19.800) |
| Vốn hoá | 520,5 tỷ |
| P/E TTM | **2,76×** (bỏ khoản khác ròng Q3: 3,32×) |
| P/B | 0,91 |
| Lợi suất cổ tức (1.500 đ) | 7,7% |
| Thanh khoản | KL bình quân 20 phiên ~45 nghìn cp ≈ **0,87 tỷ/phiên** (UPCOM) |

**So với giá trị nội tại:**
- Thấp hơn tâm (27.800) **30%**.
- Thấp hơn ô trung vị (25.100) 22%.
- Thấp hơn P20 (22.100) 12%.
- Giá nằm trong toàn lưới (16.200–50.000), ở góc dưới: giữa ô P4×thấp (16.200) và P3×thấp (19.200).

## 2. Thị trường đang ngầm định gì (giữ mọi khối khác ở tâm, giải ra một biến)

| Biến được giải | Ngầm định | Đọc |
|---|---|---|
| Giá PPA ròng 2027+ | **~370 đ/kWh** | Thấp hơn sàn kinh tế (440–540), sát dự thảo 2018 (338) ⇒ thị trường đang định giá bậc 243,66 như sự thật |
| Giá trị tư vấn | **107 tỷ** = 2,2× LNST tư vấn 2027 (kịch bản giữa) | Thấp hơn cả kịch bản thấp (170) ⇒ thị trường chiết khấu mảng tư vấn như thể bị cấm thầu |
| Ke chung | **17,4%** | Vượt phép thử "Ke > ~15% thì không mã nào qua" ⇒ chiết khấu không đến từ chi phí vốn thông thường |
| Rủi ro vụ án | Khoảng cách 8.300 đ/cp ≈ cú sốc cấm thầu EVN 3 năm (−8.600) | Tức P(cấm) ≈ 0,96 nếu chỉ có lý do này |

## 3. Đối chiếu chéo peer (sau khoá; chỉ đối chiếu, không phải mỏ neo)

**Thuỷ điện** (P/E UPCOM 7,9–9,2×, `peer_calib.json`):
- Kịch bản giữ giá 949: 732–854 tỷ, khớp DCF mù 790.
- Ở giá thấp hơn, P/E cho số thấp hơn DCF (P3: 203–237 so với 365). Lý do: khấu hao 38 tỷ/năm là phi tiền mặt,
  lớn hơn nhiều capex duy trì 5 tỷ. P/E trên LNST đánh giá thấp tài sản này, nên DCF là thước đúng.

**Tư vấn** (P/E TV4–TV3 2026 YTD 6,0–9,2×; TV2 bị méo) × LNST lõi 2026E ~45 [UL] = 270–414 tỷ. DCF mù 329 nằm trong khoảng.

**SOTP bằng bội số peer: 21.400–26.800 đ/cp.** Phương pháp độc lập này vẫn cao hơn giá 10–38%. P/E TTM của TV1 (2,8×)
thấp hơn mốc 7,5× của peer khoảng 63%.

## 4. Lý do khả dĩ cho khoảng cách

**Thị trường có thể đã tính điều mình không đưa vào tâm** (theo thứ tự trọng lượng, đánh giá của tôi):
1. **Rủi ro vụ án** (chủ tịch và phó phòng TCKT bị khởi tố; TV1 trong "13 công ty liên quan"; khách hàng chính EVNNPT là
   nơi xảy ra vụ án). Luật user: không đưa vào cơ sở khi chưa có bằng chứng tác động. Nhưng đây là nguồn khả dĩ nhất
   cho chiết khấu 30%.
2. **Mức bậc giá PPA chưa có văn bản.** Thị trường có thể đọc dự thảo 2018 (243,66) như mức thật. Mình có luận cứ kinh tế
   (sàn ≥440, IRR thực 7,7–8% < trần) nhưng chưa có hợp đồng.
3. **Chất lượng số liệu:** hoàn nhập dự phòng Q3 chưa soát xét; thuyết minh Q3 lệch BCTC kiểm toán 26,7 tỷ; điều chỉnh
   VCSH +8,9.
4. **Cấu trúc cổ đông và thanh khoản:** EVN 54%, UPCOM, ~0,9 tỷ/phiên, payout 27%, KTPL 20%. Đây là chiết khấu thiểu số
   mà INTRINSIC cố ý không áp tuỳ ý. Peer yield thuỷ điện 7–9% (lợi suất 7,7% hiện tại nằm trong dải) cho thấy thị trường
   định giá TV1 như cổ phiếu cổ tức thuần, bỏ qua tăng trưởng tư vấn.

**Mình thấy điều thị trường có thể chưa thấy** (INTRINSIC §E):
- Không có căn cứ quy định để cắt sâu giá PPA; sàn kinh tế 440–540.
- Hợp đồng ký mới 2025 là 835 tỷ (1,87× doanh thu tư vấn), doanh thu 9T +29%, trả trước +33%.
- Đòn bẩy hoạt động: EBIT tư vấn 5% → 10% → 11–17%.
- Vị thế thiết kế gốc ở thuỷ điện mở rộng miền Bắc (Tuyên Quang MR 81,7 tỷ, là bên duy nhất dự thầu).

## 5. Điều làm đổi nhận định — hai chiều, có mốc

| Mốc (ngày dự kiến) | Tích cực hơn nếu | Tiêu cực hơn nếu |
|---|---|---|
| BCTC Q4/2026 (~30/01/2027) | Giá ròng thuỷ điện Q4 vẫn ~949; doanh thu tư vấn cả năm ≥500 tỷ, biên EBIT lõi ≥11% | Doanh thu tư vấn Q4 < Q4/25 (195); xuất hiện trích lập liên quan vụ án |
| CBTT/BCTN về phụ lục PPA SB5 (bất kỳ; ĐHĐCĐ ~04/2027) | Bậc 2 ≥ 520 hoặc lùi mốc sau 2027 (mỗi năm +1.500–1.850 đ/cp) | Bậc 2 = 243,66 + O&M (~340): tâm còn ~18.200 (tư vấn giữa) |
| Giá ròng/kWh thuỷ điện Q1–Q2/2027 (BCTC ~04 và ~08/2027) | ≥600 | ≤400 |
| BCTC kiểm toán FY2026 (~03/2027) | Chấp nhận toàn phần; khoản hoàn nhập Q3 được giải thích | Ý kiến ngoại trừ; điều chỉnh hồi tố |
| Tiến độ vụ án (cáo trạng; NĐ 214/2025 Đ.133) | Cáo trạng chỉ nêu cá nhân; TV1 tiếp tục trúng gói EVNNPT (muasamcong) | Quyết định cấm thầu pháp nhân trong hệ thống EVN (−8.600 đến −13.700 đ/cp) |
| Capex EVN 2026 / kế hoạch 2027 (~01/2027; Bobby F1) | ≥123k và KH 2027 >130k | <115k hoặc KH 2027 ≤ 2026 |
| Gói Sơn La/Lai Châu MR, NT1 (muasamcong, 2027) | TV1 trúng phần thiết kế | Trao cho đơn vị khác |

## 6. Kết luận giai đoạn 2

Giá 19.500 thấp hơn giá trị nội tại dựng mù 22–30% (so trung vị/tâm). Ngay cả SOTP bằng bội số peer cũng cao hơn giá.
Để biện minh cho giá hiện tại, cần **hoặc** giá PPA ~370 (dưới sàn kinh tế), **hoặc** coi mảng tư vấn gần như chắc bị cấm thầu
EVN 3 năm, **hoặc** Ke 17%.

Cả ba đều là những điều **chưa có bằng chứng** trong KQKD (9T/26 tư vấn +29%; thuỷ điện vẫn ở giá cũ). Vì vậy khoảng cách
chủ yếu là **chiết khấu rủi ro sự kiện (vụ án + văn bản PPA) và chiết khấu thiểu số/thanh khoản**, không phải do nền tảng.

Đây là đọc nội bộ, chưa qua phản biện; xác suất kịch bản [UL] là điểm yếu nhất.
