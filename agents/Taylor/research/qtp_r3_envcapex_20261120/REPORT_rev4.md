# QTP DD rev4 — xử lý skeptic r1 (DD_GENERAL, INCONCLUSIVE) · 23/11/2026 · job `Taylor_20261123_063644`

> Chỉ NGHIÊN CỨU. Không ghi `dd_price_zones.json`, không email. Thay thế `REPORT_r3c.md` (không đè bản cũ). Sổ: dd_date 2026-11-17, rev mới = 4.
> Mô hình `qtp_model_rev4.py` (md5 `8f14ee33e478f37f173a114b41059b2d`), output `qtp_model_rev4_out.txt` (md5 `793d7ae50c7cb2f9807e0f7caa06801b`, chạy lại trùng từng byte). Mô hình là bản sao r3c, chỉ THÊM: tham số `vol`/`vc_pass`/`fc_end`/`extra_opex`/`extra_eq` và hàm `ktpl_pv`/`val4`/`center4`. Với tham số mặc định, mô hình tái lập đúng r3c 8.557/7.701 và r3 7.836/7.053 (dòng 2 của output).
> Khoá giả định: `assumptions_QTP_rev4.json` (md5 `190b829455f1a6e77b9e15ccac7a3727`). Khoá TRƯỚC khi đọc giá. `dd_assumptions_lint.py` rc=0, chế độ cảnh báo, còn 22 cảnh báo hình dạng schema (tên trường của `projects`/`bonus_esop`/`rate_path`, L14 ngày lãi huy động sau dd_date). Không có vi phạm nội dung số.
> r = 13,5%: `deposit_rate_vn.effective_deposit_rate('2026-11-23')` = 7,40% (CCTG 12M 02/11), bằng mức neo 03/11 ⇒ không điều chỉnh (V1).

## 0. Kết luận

- **Tâm rev4: 6.273 đ/cp sau chiết khấu thanh khoản (6.970 trước CK).** r3c là 7.701, nên tâm giảm 18,5%. Nhãn vẫn **ĐẮT / TRÊN vùng**.
- Tâm giảm do hai thay đổi, cả hai đều có cơ sở độc lập (§1):
  - **Quỹ khen thưởng–phúc lợi (KTPL):** trước CK −896 đ/cp. Nguồn là BCTC kiểm toán 2025: số dư 120,6 tỷ, tỷ lệ trích 11,4% LNST năm trước.
  - **Trọng số P0 trở về 0,50 như r3:** trước CK −691 đ/cp. Skeptic r1 chỉ ra việc hạ xuống 0,40 ở r3b không có dữ kiện mới; legal-vn 23/11 cũng không đưa ra dữ kiện thuận lợi nào.
- **Vùng biến thể đơn lẻ, sau CK: 5.140 … 7.117.** Kết hợp các biến thể: 4.993 … 7.927. Theo trọng số P0 từ 0,6 về 0: 5.652 … 9.380.
- **Cvlp (amoniac đi qua giá biến đổi) là upside có điều kiện, không vào tâm.** Xác suất q=0,25 trong nhánh P0 cho 6.782 (+8,1%); q=1 cho 8.308 (+32,4%).
- **Sau khoá giá:** giá tham chiếu là 10.200 (đóng cửa 20/11/2026, BQ `ticker`), tức 1,63× tâm. Giá này còn cao hơn cả các mức sau:
  - kết hợp thuận lợi nhất 7.927 (1,29×);
  - P0 = 0, tức chắc chắn được bù, 9.380 (1,09×);
  - Cvlp q=1, 8.308 (1,23×).
  Ngưỡng 0,85× tâm là 5.332.
- **Sizing (V8):** không đề xuất mua vì giá ở trên mọi biến thể. Nếu có thì vẫn trong khung 2–4% NAV.
- **Cảnh báo (WARNING), không vào base:** ở P0 cơ sở, sau khi trừ KTPL, dòng tiền toàn công ty 2030–39 cộng dồn **−3.168 tỷ**. Tiền ròng xuống **−254 tỷ năm 2039 ngay cả khi không chia cổ tức**; r3c ghi +3 tỷ vì chưa trừ KTPL.

## 1. Đính chính so với r3c — từng hạng mục skeptic r1

| # | Hạng mục skeptic | Xử lý rev4 | Loại | Tác động lên tâm (sau CK) |
|---|---|---|---|---|
| 1 | Chi phí biến đổi 470 tỷ/năm có thể đi qua giá biến đổi của PPA hiện hữu (đòn chính, +30%) | **legal-vn 23/11:** TT12/2025 (VBHN 56/VBHN-BCT) Đ7.3 có cấu phần **Cvlp – chi phí vật liệu phụ** "theo khối lượng và đơn giá các loại vật liệu phụ", nên amoniac **nhiều khả năng** thuộc Cvlp. Nhưng **Đ18**: với PPA đã ký, nhóm "biến động khác" (gồm Cvlp) chỉ trượt **2,5%/năm từ năm cơ sở**, không theo chi phí thực tế ⇒ đưa vật liệu mới vào **phải sửa PPA** (Đ26, Đ27.3). Không tìm được tiền lệ công khai 2020–2026. Bản thân FS gộp 72,33 đ/kWh vào phần **xin** tăng giá, khớp với đọc này. | (b) kịch bản có xác suất, **không vào base** | q=0 (tâm) · q=0,25: +8,1% · q=0,5: +16,2% · q=1: +32,4%. Đối chiếu đúng phép tính của skeptic (VC=0 ở mọi kịch bản): 8.815 (+40,5% so với tâm rev4) |
| 2 | Trọng số r3→r3b (+8,4%) dựa trên đọc lại dữ kiện cũ | **Trở về 0,50 / 0,30 / 0,20 (r3).** Tách dữ kiện mới khỏi dữ kiện cũ ở §3; bỏ mục "(0)" tự mâu thuẫn của r3c. | (a) thay base, có lý do | −691 trước CK (P0 0,4 → 0,5) |
| 3 | Thay xúc tác SCR định kỳ; "tuổi thọ dự án 10 năm" trong FS | FS §3.1.7 (bảng thông số) ghi "Tuổi thọ dự án 10 năm; khấu hao 10 năm". Bảng giải trình thẩm tra (txt dòng 4534–4539) ghi tuổi thọ còn lại 18 năm ⇒ 17 năm, "TVTK đã sửa". Không văn bản nào nêu chu kỳ hay chi phí thay xúc tác, cũng không rõ O&M 102 tỷ đã gồm khoản này hay chưa. | (c) **không kiểm chứng được** ⇒ độ nhạy | Xúc tác 27 tỷ/năm từ 2033: −2,2%; 54 tỷ/năm: −4,3% (**ước lượng**: ~1 m³/MW × 1.200 MW × ~5.000 USD/m³ ≈ 160 tỷ ban đầu, thay một nửa mỗi 3 năm). FC chỉ thu 10 năm (đến 2039): −3,3% |
| 4 | Tỷ giá trên phần EPC 89,76 triệu USD | QĐ 1710: EPC 89.756.813 USD; tỷ giá FS 26.388. VND mất giá 10% ⇒ thêm 237 tỷ vốn chủ (giả định vay cố định 2.787,9). | (b) độ nhạy | −6,0% |
| 5 | Bù theo đ/kWh nhạy với sản lượng huy động | FS: 6.000 h/năm (thương phẩm 6.501,57 GWh). Mô hình cho doanh thu bù (FC+FOM+VC) và chi phí amoniac/điện tự dùng/phần dư cùng tỷ lệ với sản lượng; O&M cố định 102 tỷ không đổi. | (b) độ nhạy | 5.000 h: +2,9% · 6.500 h: −1,5% |
| 6 | Quỹ khen thưởng–phúc lợi trích từ LNST (vắng ở r2/r3c) | **BCTC kiểm toán 2025, TM 19.1:** trích KTPL + thưởng BQL năm 2025 = 71,36 tỷ (trên LNST 2024 619,26 ⇒ 11,52%), năm 2024 = 69,04 tỷ (trên LNST 2023 614,4 ⇒ 11,24%) ⇒ dùng **11,38%**, trả năm sau, chỉ khi LNST toàn công ty > 0. Thêm **số dư quỹ 120,6 tỷ** (BCĐKT 31/12/2025, mã 322), là nợ phải chi cho người lao động mà netcash r2 chưa trừ. Số dư Q3/26 chưa đọc (bản scan) ⇒ dùng số 31/12/2025. | (a) **vào base** (cơ sở độc lập: BCTC kiểm toán) | Dòng trích −1.001 trên nền r2 (trước CK); số dư −268; cộng chung với dự án −896 trước CK (W r3b). Độ nhạy tỷ lệ 8% / 15%: +2,5% / −2,7% |
| 7 | GPMT 517 Phụ lục 2 (SCR có bắt buộc chạy trước 2032 không) | Vẫn **không lấy được văn bản** (r3c đã tra web 20/11; rev4 không có nguồn mới). | (c) không kiểm chứng được | Biến thể opex SCR từ 2032: +13,4% (giữ ngoài tâm, như r3c) |
| 8 | Phần dư 115,3 tỷ/năm trong VC chưa giải thích (skeptic: "đã gắn nhãn") | Giữ trong tâm; FS không thuyết minh. | (c) | Bỏ phần dư: +10,3% |
| 9 | Thời hạn PPA và giá cố định sau khi hết khấu hao (r2 nêu là biến lớn nhất) | legal-vn: **không tìm được** nguồn về thời hạn PPA điển hình; TT57 (Tạp chí Công Thương 03/2021) quy định giá cố định từng năm bám lịch trả nợ; không có quy định giá giảm về chỉ còn O&M. | (c) | Không đổi kịch bản tốt/xấu của r2 |

## 2. Tâm và bước cầu nối

| Bước | Trước CK | Sau CK |
|---|---|---|
| r3c (W 0,4/0,36/0,24) | 8.557 | 7.701 |
| + KTPL (trích 11,38% + số dư 120,6) | 7.661 | 6.895 |
| + trọng số về 0,5/0,3/0,2 = **tâm rev4** | **6.970** | **6.273** |

Kết quả thuần theo kịch bản (W_R2 trên nền r2), trước / sau CK:
- P0: 3.519 / 3.167
- P50: 8.726 / 7.854
- P100: 12.966 / 11.669

## 3. Trọng số — dữ kiện MỚI tách khỏi dữ kiện cũ (sửa §4 r3c)

Chốt **0,50 / 0,30 / 0,20** trước khi chạy lưới. Đây là ước lượng, N = 0 tiền lệ.

- **Dữ kiện đã có từ r3, nên không phải lý do để dời trọng số:**
  - EVN kiến nghị 29/12/2025 (`REPORT_r3.md:98`);
  - FS dẫn TT57 Đ20.3;
  - 9 năm chưa được bù;
  - 0 tiền lệ;
  - bên mua và chủ chi phối cùng thuộc EVN.
- **Dữ kiện mới sau r3, chiều thuận lợi:** Luật Điện lực 61/2024 Đ52.4 (còn tranh cãi; legal-vn 23/11 không tìm được nguyên văn).
- **Dữ kiện mới sau r3, chiều bất lợi:**
  - không có Đ14.6;
  - TT07 đã bị TT12 bãi bỏ và TT12 không có điều tương đương;
  - PPA mẫu theo TT12 không có điều khoản "thay đổi pháp luật" (legal-vn 23/11);
  - chỉ thị EVN 12/2025 yêu cầu nâng cấp xử lý khí thải nhưng không nói cơ chế thanh toán.
- Hai chiều mới gần cân nhau, chiều bất lợi nhiều hơn ⇒ không có cơ sở để hạ P0. Giữ đúng mức r3.
- Mục "(0)" của r3c (EVN bị ép biên) làm TĂNG P0 nhưng lại nằm dưới tiêu đề "giảm P0". Đó là lỗi trình bày; rev4 xếp nó vào nhóm "dữ kiện cũ".

**Độ nhạy trọng số** (P50:P100 = 60:40, đã có KTPL; trước / sau CK):

| P0 | trước | sau |
|---|---|---|
| 0 | 10.422 | 9.380 |
| 0,2 | 9.041 | 8.137 |
| 0,3 | 8.351 | 7.516 |
| 0,4 | 7.661 | 6.895 |
| **0,5 (chốt)** | **6.970** | **6.273** |
| 0,6 | 6.280 | 5.652 |

## 4. Biến thể (W_R4, có KTPL; trước / sau CK)

| Biến thể | Trước | Sau | Δ |
|---|---|---|---|
| **Tâm rev4** | 6.970 | **6.273** | – |
| Bỏ phần dư 115 của VC | 7.688 | 6.919 | +10,3% |
| Opex SCR từ 2032 (QCVN 19) | 7.908 | 7.117 | +13,4% |
| Sản lượng 5.000 h | 7.174 | 6.456 | +2,9% |
| Sản lượng 6.500 h | 6.868 | 6.181 | −1,5% |
| Tỷ giá EPC USD, VND −10% | 6.554 | 5.899 | −6,0% |
| Xúc tác SCR 27 tỷ/năm từ 2033 (ước lượng) | 6.819 | 6.137 | −2,2% |
| Xúc tác SCR 54 tỷ/năm từ 2033 (ước lượng) | 6.668 | 6.001 | −4,3% |
| FC chỉ bù 10 năm (đến 2039) | 6.740 | 6.066 | −3,3% |
| Bù chậm từ 2033 | 5.711 | 5.140 | −18,1% |
| Khấu hao 18 năm | 6.844 | 6.160 | −1,8% |
| Lãi vay 7% / 11% (ước lượng 9%) | 7.366 / 6.570 | 6.629 / 5.913 | +5,7% / −5,7% |
| KTPL 8% / 15% | 7.148 / 6.780 | 6.433 / 6.102 | +2,5% / −2,7% |
| Kết hợp thuận lợi (bỏ dư 115 + opex 2032 + lãi 7%) | 8.808 | 7.927 | +26,4% |
| Kết hợp bất lợi (bù chậm 2033 + xúc tác 27 + 5.000 h + lãi 11%) | 5.547 | 4.993 | −20,4% |

Lưu ý về chiều của biến thể sản lượng 5.000 h: biến thể này làm tăng tâm vì ở P0 chi phí amoniac giảm theo sản lượng. Hiệu ứng của sản lượng thấp lên LNST nền r2 **không** được mô hình hoá ở đây, vì nó thuộc kịch bản xấu của r2. Không đọc biến thể này như "huy động ít thì tốt".

## 5. V1 chi phí vốn · V2 dải Ke · V3 thanh khoản · V5 5F · V6 hai nền

- **V1:** r = 13,5% (neo 03/11/2026; lãi huy động hiệu dụng 7,40% tại 23/11 = neo).
  - Độ nhạy β=1, r và lãi vay cùng dịch: ±50bp ⇒ +2,7% / −2,6%; ±100bp ⇒ +5,6% / −5,1%.
  - β = 0,5, ±100bp: +4,2% / −4,0%.
- **V2 (báo kèm):** Ke 12,3% ⇒ 6.476 (+3,2%); 13,4% ⇒ 6.289 (+0,2%). Dòng tiền hữu hạn đến 2047, không có terminal vô hạn.
- **V3:** chiết khấu 10%, dùng lại r2 §6: ADV trung vị và free float đã đọc sau khoá ở r2; vị thế 1 tỷ thoát khoảng 5,5 phiên, 3 tỷ khoảng 16 phiên ở mức tham gia 15% ADV. Nhãn tính trên giá trị sau CK.
- **V5:** dữ liệu 5F < 12 tháng ⇒ tái dùng. `data/moat_tags.csv`: QTP = NARROW, REGULATORY/COST, asof 2026-06-05. Kiểm nhanh: hào của QTP là PPA có điều tiết. Đúng ca này cho thấy hào "điều tiết" không bảo vệ được chi phí tuân thủ mới. Không thưởng, không trừ.
- **V6 (chỉ hiển thị):** V_ngắn = **−579** đ/cp. Lý do: LNST nền chuẩn hoá 565 tỷ cộng delta trung bình 2030–39 (−605 tỷ, theo trọng số) là số âm. V_dài (cơ sở) = 7.541. **D không xác định** ⇒ theo luật V6, chỉ báo V_ngắn kèm giải thích dòng tiền âm: chi phí vận hành SCR/FGD chưa được bù, cộng lãi và gốc vay dự án trong 2030–39. Luật 0,85×tâm không tự kích hoạt; cần Mike/user phán đoán.

## 6. Dòng tiền toàn công ty (P0, cơ sở, sau KTPL) — WARNING

- Cộng dồn 2030–39: −3.168 tỷ.
- Tiền ròng thấp nhất: **−254 tỷ năm 2039, khi chưa chia cổ tức** (r3c ghi +3 tỷ do chưa trừ KTPL). Như vậy ở P0, công ty phải vay thêm hoặc cắt cổ tức xuống 0 kể cả trong kịch bản cơ sở.
- Điều kiện huỷ r3c §6 (a)–(e) giữ nguyên. Quan trọng nhất là **(d)**: chưa ký thoả thuận bổ sung giá PPA (FC, và Cvlp amoniac) trước COD (~12/2029). Thêm **(f)**: phụ lục PPA đưa Cvlp amoniac vào giá biến đổi. Nếu ký được (f) thì đó là dữ kiện thuận lợi ⇒ chạy lại với q=1 (+32%).

## 7. Mốc đổi nhận định (cả hai chiều)

- **Lên:**
  - Văn bản EVN/BCT chấp nhận bù FC và/hoặc phụ lục PPA về Cvlp (amoniac) ⇒ P0 → 0 hoặc q → 1, tâm 8.300–9.400.
  - GPMT 517 cho SCR chạy từ 2032 ⇒ +13%.
- **Xuống:**
  - EVN/BCT từ chối bằng văn bản ⇒ P0 → 1, tâm khoảng 3.200 sau CK;
  - TMĐT hoặc tỷ giá EPC vượt;
  - BCTC cho thấy số dư KTPL hoặc tỷ lệ trích tăng.

## 8. Giới hạn

- Lãi vay 9%, kỳ hạn 10 năm, tiến độ giải ngân và COD 2030 vẫn là **(ước lượng)**: không có trong văn bản đọc được.
- Chi phí thay xúc tác SCR là **ước lượng ngành**, không có nguồn của công ty.
- KTPL dùng số dư 31/12/2025 (Q3/26 là bản scan, chưa đọc). Tỷ lệ trích lấy từ 2 năm.
- legal-vn là thông tin tham khảo, không phải ý kiến của luật sư hành nghề. Chưa đọc nguyên văn TT57 và Đ52.4 Luật 61/2024.
- Giá tham chiếu 10.200 lấy từ BQ (đóng cửa 20/11/2026). Đây là phiên BQ gần nhất, không phải giá trong phiên; chỉ dùng để gắn nhãn.
- Lint giả định còn 22 cảnh báo về hình dạng schema (chế độ cảnh báo, rc=0).
