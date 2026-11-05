# TV1 (EVNPECC1) — DD redo VÒNG 2 · giá 04/11/2026 · job `Taylor_20261105_020018`

> Tài liệu chỉ để nghiên cứu, giữ trung dung. Vụ án nằm ở phần WARNING, không đưa vào tâm (có bản song song).
> - Áp `STANDARD_r2.md`.
> - Số liệu: `calc/model_tv1_r2_out.txt|json`, chạy `$DNA_PYEXE -I calc/model_tv1_r2.py`.
> - LOCK: `calc/LOCK_r2_md5.txt`, gồm `tv1_v2_core.py` và `v2data/bq_tv1_quarterly_2022_2025.csv`.
> - Tất định: `_common_g2r2/selfcheck_r2.sh`.
> - Lõi INTRINSIC_v2 02/11 tái lập byte từ vòng 1. Bản vòng 1 vẫn giữ: `REPORT.md`, `SUMMARY_r1.json`.

## 0. Kết luận
| Sau CK 4,02% @5 tỷ | |
|---|---|
| **Tâm** (kỳ vọng lưới) | **15.379** |
| P50 kết cục | 15.532 |
| Giá trị tại tham số trung tâm (PPA 520, tư vấn 11%, Q187,5, đúng 2027, VLĐ 49%) | 19.165 |
| **P10 / P90 kết cục** | **4.693 / 24.544** (min 0, max 43.306; n = 720) |

- Giá **19.600** cao hơn tâm 27,4%. **71,3% trọng số kết cục nằm dưới giá.** Nhãn **TRONG vùng**, nhưng vùng rất rộng; giá nằm trên tâm và trên P50.
- Nhãn không đổi so với vòng 1, và cũng không do đổi định nghĩa vùng: vòng 1 đã dùng P10–P90; rev5 dùng P20–P80 và cũng ra TRONG.
- Tâm thấp hơn giá trị ở tham số trung tâm 20% vì hai lý do:
  - 520 và biên 11% đều nằm trên kỳ vọng xác suất (PPA kỳ vọng 509; 50% xác suất biên tư vấn ≤ 8%);
  - tâm gồm nhánh truy thu với xác suất 0,10.
- P10 do nhánh PPA 340 chi phối (63% trọng số quanh P10), cộng truy thu (31%). **5,5% trọng số chạm sàn vốn chủ 0.**
- So vòng 1 (tâm 16.348, P10 8.366): tâm −5,9%, P10 −44%. Toàn bộ chênh lệch đến từ trục thời điểm mới.

## 1. Đổi so vòng 1
| Điều | Vòng 1 | Vòng 2 |
|---|---|---|
| 2 đối xứng | Lùi hạ bậc (chiều lên) chỉ nêu ở §9; truy thu (chiều xuống) để ở WARNING ⇒ cả hai nằm ngoài lưới. VLĐ cố định 49% | Trục **thời điểm** hai chiều: truy thu hồi tố 0,10 · đúng 2027 0,70 · lùi 1 năm 0,15 · lùi 2 năm 0,05 [UL]. Trục VLĐ 45/49/53% |
| 1 phân vị | bậc thang | wpct; sàn vốn chủ 0 (trách nhiệm hữu hạn) |
| 5, 6, 9, 10 | — | §5, §6, LOCK, Gordon |

Truy thu là tranh chấp **hợp đồng** với EVN (bậc giá 2018 đã ký), không phải vụ án, nên đưa vào lưới với xác suất [UL]. Bản không có trục này: tâm 16.348, P10 8.420, P90 24.562.

## 5. Thanh khoản
| Cỡ | ADV trung vị | Q/ADV | Số phiên @10% | CK |
|---|---|---|---|---|
| **5 tỷ** | 120 phiên: 0,63 tỷ | 797% | 79,7 | **4,02%** |
| 5 tỷ | 250 phiên: 0,80 tỷ | 624% | 62,4 | 3,59% |
| 5 tỷ | 60 phiên: 0,45 tỷ | 1.115% | 111,5 | 4,69% |
| **Sleeve 10 / 20 / 40 triệu** | 120 phiên | 1,6–6,4% | 0,6 | **0,50% / 0,57% / 0,66%** |

- ⚠️ Cỡ 5 tỷ cần 80–110 phiên để thoát, **nằm xa ngoài vùng hiệu chỉnh của luật căn bậc hai**. CK thực tế có thể cao hơn nhiều.
- Cỡ hợp lý ≤ 1 tỷ. Ở cỡ sleeve, tâm là 15.916 (= 16.023 × (1 − 0,66%)), nhãn không đổi.

## 6. Pháp lý / quản trị — ⚠️ WARNING
Mang theo cờ từ `dd_TV1_20261102/SKEPTIC{,2..5}_20261102.md`, `dd_TV1_blind_20261102/SKEPTIC_BLIND_20261102.md` và REPORT 02/11.

1. **Vụ EVNNPT/PC1:** Chủ tịch HĐQT Nguyễn Hữu Chỉnh và phó phòng TCKT bị khởi tố, tạm giam (05/2026; [nhadautu](https://nhadautu.vn/chu-tich-tv1-nguyen-huu-chinh-bi-bat-d105159.html), [baolaocai](https://baolaocai.vn/vi-sao-ong-nguyen-huu-chinh-chu-tich-hdqt-tv1-bi-khoi-to-post900153.html)).
   - Về pháp nhân, công ty chỉ viết "chưa nhận được thông tin/kết luận chính thức" (H1 TM33). Câu này **không** có nghĩa là "chưa bị khởi tố".
   - Bản song song có cấm thầu 3 năm (DT tư vấn −50%, xác suất 0,35 lấy theo P(M5) của REPORT 02/11): **tâm 12.981, P10 1.431, P90 22.806**, 79,4% trọng số dưới giá.
2. **Mức thiệt hại theo kịch bản pháp lý:** cấm 3 năm ≈ −8.194 đ/cp; cấm 5 năm ≈ −12.983; nộp 20/50/100 tỷ ≈ −660 / −1.650 / −3.301.
3. **Big4 từ chối kiểm toán FY2026** ([vietnamfinance 01/07/2026](https://vietnamfinance.vn/chu-tich-bi-bat-cong-ty-dien-bi-4-cong-ty-tu-choi-kiem-toan-d146988.html)). Đã đóng: An Việt ký ngày 18/08. Rủi ro chất lượng kiểm toán vẫn còn (mốc M4, khoảng 31/03/2027).
4. **Giá PPA SB5 từ 2027 chưa có văn bản:**
   - Lãnh đạo nêu 500–600 qua KBSV, chưa kiểm bản gốc.
   - Bậc 2018 là 243,66 + O&M ≈ 340.
   - Truy thu 2022–26 ≈ 657 tỷ trước thuế, tương đương −17.397 đ/cp. Nay đã thành nhánh lưới.
5. **Cổ đông và cổ tức:**
   - EVN 54,34%.
   - Lê Minh Hà 9,84%, đồng thời là bên cho vay (lãi vay cá nhân phải trả 64,3 tỷ).
   - Không trả cổ tức tiền FY2016–22.
6. **Tra tin 05/11/2026 (WebSearch):** không thấy khởi tố hay kết luận mới liên quan TV1 sau 02/11.
   - Kết quả "NQ ĐHĐCĐ bất thường 2/11 bán đấu giá SB5" thực ra là **02/11/2020** ([vietnamfinance](https://vietnamfinance.vn/evnpecc1-rao-ban-nha-may-thuy-dien-song-bung-5-voi-gia-khoi-diem-1390-ty-d57541.html), [EVN](https://en.evn.com.vn/d6/news/EVNPECC1-agreed-to-sell-Song-Bung-5-Hydropower-Plant-66-163-2038.aspx)). 6 lần rao bán từ 2019 đến 06/2021 đều không thành. Không phải dữ liệu mới.
   - WebSearch không thay được CBTT sàn.

## 7. Định giá
- **Phương pháp:** SOTP gồm PV FCFE thuỷ điện 2027–08/2059 (sau KTPL 20%), DCF tư vấn, và tiền ròng điều chỉnh. r = 13,5%.
- **Trục lưới:**
  - giá PPA 949/600/520/440/340 với xác suất 0,05/0,25/0,30/0,20/0,20;
  - biên tư vấn 5/8/11/14% với xác suất 0,20/0,30/0,40/0,10;
  - Q 175/187,5/200;
  - thời điểm (như §1);
  - VLĐ 45/49/53%.
  - Mọi xác suất là [UL], áp cơ học theo phản biện mù.
- **Loại khỏi lưới:**
  - vụ án (cấm thầu, nộp tiền) ⇒ để ở WARNING + bản song song;
  - điện mặt trời nổi 46 MWp ⇒ NPV 0, chưa đầu tư;
  - tỷ lệ KTPL ⇒ đo được, 20%.
- **`base_adjustments`:** tiền ròng điều chỉnh **−2.412 đ/cp**. Gồm cổ tức phải trả, lãi vay cá nhân phải trả, quỹ KTPL 40,7 tỷ (mã 323), KTPL sẽ trích từ 9T, cộng LNST Q4 50 tỷ [UL]. Tất cả đều là nợ trên sổ hoặc tỷ lệ đã đo.

| Biến thể | Tâm | P10 | P50 | P90 | % dưới giá |
|---|---|---|---|---|---|
| Chính (5 trục) | 15.379 | 4.693 | 15.532 | 24.544 | 71,3% |
| Không trục thời điểm | 16.348 | 8.420 | — | 24.562 | 70,8% |
| Trục vòng 1 (n=60) + wpct | 16.348 | 8.454 | 15.759 | 24.676 | — |
| Có cấm thầu p0,35 | 12.981 | 1.431 | — | 22.806 | 79,4% |

- **Gordon (g 3%, trước CK, LNST 2025 sau KTPL):** có lãi tiền gửi 36.723 · không có lãi tiền gửi 37.198.
  - Con số này **gấp đôi tâm**, vì LNST 2025 chứa giá điện 949 sẽ bị hạ bậc. Đúng điểm mà §1 vòng 1 đã nêu ("P/E thấp là bẫy"). Chỉ dùng để đối chiếu, không phải cận.
- **Độ nhạy r (tâm sau CK, β=1):**

| Lãi suất | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| Tâm | 16.979 (+10,4%) | 16.138 | 15.379 | 14.689 | 14.060 (−8,6%) |

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON
| Mốc | LÊN nếu | XUỐNG nếu |
|---|---|---|
| Văn bản/phụ lục PPA SB5 | giá ròng ≥ 600, hoặc lùi hạ bậc ≥ 2 năm | ≤ 440 hoặc ~340; có văn bản đòi truy thu 2022–26 |
| BCTC Q4/2026 + kiểm toán FY2026 (An Việt) | biên tư vấn ≥ 11%; chấp nhận toàn phần | ngoại trừ; trích lập cho vụ án |
| Vụ án | kết thúc, không cấm thầu/nộp tiền | quyết định cấm thầu EVN (≈ −8.200 trở lên) |
| Lãi huy động | −50bp ⇒ +4,9% | +50bp ⇒ −4,5% |

- Ngưỡng nhãn: DƯỚI vùng khi giá < 4.693; TRÊN vùng khi giá > 24.544.
- **HARD ABANDON:** khởi tố pháp nhân, cấm thầu EVN, có văn bản truy thu, hoặc kiểm toán từ chối/ngoại trừ.
- **Không đủ điều kiện sleeve fear-buy §2.5**: giá đang cao hơn tâm, vụ án chưa kết luận. Nếu xét lại sau này: trần size 2–4% NAV và phải có trigger §3 (SKEPTIC_BLIND N7).
