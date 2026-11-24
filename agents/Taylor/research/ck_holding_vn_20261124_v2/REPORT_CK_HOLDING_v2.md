# CK holding niêm yết VN — v2 (job Taylor_20261124_032640, 24/11/2026)

Chỉ đo tham số (hiển thị / đầu vào DD). KHÔNG dựng rev8 HHS, KHÔNG ghi sổ, KHÔNG wire. Không đọc giá HHS/TCH/CRV.
Nguồn số: `run1.txt` = `run2.txt` (md5 `058b2a14c5339e65b66086e873e8d23d`), `calc_out_v2.json`, `panel_v2.csv`; khoá `LOCK_md5.txt`.

## 0. Kết luận
**(a) CK đo được (bản chính = PIT, loại giá con STALE, độ phủ ≥60% trong ≥3 tháng):**
- **N = 12 holding**: APH, CMX, GEX, IPA, LHC, MSN, MVN, OGC, PAN, SNZ, VIC, VSC.
- **Trung vị 6,5%**; IQR **−19,1% … +38,0%**; min…max −167,7% (MVN) … +68,1% (CMX).
- Bootstrap khối (holding có hoàn lại × khối 3 tháng circular, B=5.000): trung vị p5–p95 **−18,7% … +36,2%**.
- **Đường theo tháng** (trung vị cắt ngang, chỉ các tháng có n ≥ 11): **−4,6% (31/03/2026) → +23,0% (20/11/2026)**.
  - Bản tỷ lệ cố định (look-ahead), lùi về 12/2024: trung vị tháng nằm trong khoảng −15,9% … +23,0%. Suốt 2025 nó âm, từ −16% đến 0%.
- **N hiệu dụng = 12 holding × 1 chế độ thị trường** (11/2024–11/2026). Tự tương quan lag-1 của đường tháng là 0,50, nên T_eff ≈ 6,9/21 tháng. Đây là hai năm của một chu kỳ, không phải trung bình nhiều chu kỳ.

**(b) Không đủ mạnh để làm BASE cho HHS.**
- Dấu của trung vị đổi theo lựa chọn hợp lý:
  - Ngưỡng 50/70%: 3,2% / 2,3%.
  - Tỷ lệ cố định: −1,0%.
  - Chỉ tính độ phủ thanh khoản: −12,6%.
- IQR vắt qua 0.
- Nhóm giống HHS chỉ có N = 2 (CMX 68%, OGC −8%). Nhóm tầng chồng có **N = 0**.
- ⇒ **Khuyến nghị: giữ base 0% + dải độ nhạy có nguồn.**
  - Trung vị đo được: 6,5%.
  - Trung vị tháng gần nhất: 23,0%.
  - q75 cắt ngang: 38,0%.
  - ⇒ **dải 0 / 6,5 / 23 / 38%**. Không có số nào đủ tư cách làm điểm base. Mức 26,6% của v1 là sản phẩm của mẫu 6 mã + giá con stale (xem §1).

**(c) Độ tin: THẤP.**
- Nguồn độc lập, truy được, tái lập bit-exact.
- Nhưng phân tán liên holding rất lớn: IQR 57pp.
- Toàn mẫu nằm trong 1 chế độ, và phần trôi của 2026 đến từ giá MẸ giảm (§1.5).

## 1. Đính chính so với v1 (mỗi mục: tác động lên N và trung vị)

v1: N = 6, trung vị 26,6%, 4 ngày đo năm 2026, 17 mã hardcode.

1. **Giá con STALE.**
   - Quy tắc: STALE khi phiên có khối lượng cuối cùng cách D quá 10 phiên, hoặc ADV60 (trung bình 60 phiên, ngày không khớp tính = 0) bằng 0.
   - Phần giá trị STALE được chuyển về nhóm 'theo sổ' (sᵢ·Eᵢ giữ nguyên trong E_mẹ − Σ). Giá MẸ STALE thì bỏ luôn quan sát.
   - CII rớt: LGC dừng dữ liệu từ 18/06/2026, độ phủ trung vị còn 0,00; chỉ có 2 tháng ≥ 60%.
   - PAN vẫn ở lại (độ phủ 0,71 sau khi BBC dừng từ 15/01/2026 chuyển về sổ).
   - **Tác động:** bản v1-giữ-stale cho N = 13, trung vị 9,8% ⇒ loại stale làm trung vị **−3,3pp** (9,8 → 6,5) và N −1.
   - Đường tháng v1-stale nằm cao hơn bản chính 2–8pp từ 06/2026, ví dụ 30/06: 13,0% so với 5,0%.
2. **VCSH và số CP quanh đợt phát hành.**
   - E bây giờ lấy thẳng từ CĐKT quý VCI (`owners_equity − minority_interests`), quý có Release_Date BQ ≤ D. Phát hiện: VCI REST trả đủ 2020Q1–2026Q3; giới hạn "4 kỳ" chỉ là cắt phía client của vnstock. ⇒ **Không còn dùng BVPS×OShares** cho mọi holding trong N.
   - Số CP vốn hoá lấy từ `oshares_at` PIT, áp ISS từ ngày ex.
   - Đối chiếu với vốn góp VCI/10.000 (`shares_xcheck` trong calc_out). Chênh lệch chỉ xuất hiện trong khoảng từ ngày ex tới quý báo cáo kế tiếp, và đều đúng chiều sau-sự-kiện:

     | Mã | Từ | Hệ số số CP |
     |---|---|---|
     | GEE | 05/2026 | ×1,75 |
     | GEX | 05/2026 | ×1,45 |
     | IPA | 08/2026 | ×1,15 |
     | VHM | 08/2026 | ×2,00 |
     | VIC | 12/2025 | ×1,99 |

   - **PAN, còn dư:** `oshares_at` từ chối (AIS_UNCERTIFIED) tới 30/06, nên fallback dùng 208,89 tr.
     - 07–09/2026 dùng AIS 258,07 tr; 10–11/2026 dùng BQ 250,67 tr.
     - Chuỗi không đơn điệu vì hai nguồn khác định nghĩa: 258,07 = vốn góp VCI/10.000 (cổ phiếu **phát hành**), còn 250,67 = BQ OShares. Chênh 7,40 tr cũng đúng bằng 216,29 − 208,89 ở quý trước, nên đây **nhiều khả năng là cổ phiếu quỹ** (suy luận từ hai cặp số, chưa đối chiếu thuyết minh BCTC).
     - Hệ quả: MV PAN 07–09 bị đánh giá cao khoảng 2,9%, nên CK PAN lệch xuống khoảng 3pp trong 3 tháng.
     - Nếu đợt phát hành ex trước 30/06 thì MV ngày 30/06 bị đánh giá thấp. **Chưa sửa trong code** (hạn chế §4). Tác động lên trung vị chung ≤ 1 bậc hạng: PAN 3,2% nằm sát dưới trung vị.
   - Câu "tránh bẫy" của v1 đã bị thay bằng quy tắc trên.
3. **VCSH mẹ.**
   - 12/12 holding trong N dùng VCSH mẹ chính xác từ CĐKT VCI.
   - E con cũng là VCSH thuộc cổ đông mẹ của con. Chỉ MVN có 1 con dùng fallback (VCSH tổng BQ).
   - Độ nhạy "chỉ holding có VCSH mẹ + con chính xác": N = 11, trung vị 9,8%.
   - Thiên lệch hai chiều của v1 (E con gồm NCI ⇒ CK lệch xuống; NCI con không niêm yết bị bỏ sót ⇒ lệch lên) **đã bị loại bỏ** cho tập N. Fallback xấp xỉ chỉ còn ở các holding bị loại.
4. **Mẫu tái lập.** Quy trình nằm ở `fetch_inputs_v2.py`, docstring.
   - **Bước 1 — U0:** in_universe trong `universe_pit` tại ≥ 1 ngày cuối tháng 12/2024–11/2026, hợp với 17 mã v1 và GEL. U0 = 497 mã.
   - **Bước 2 — KBS profile:** subsidiaries + cổ đông lớn của U0, gọi thẳng endpoint vì wrapper vnstock bị giới hạn 20 req/phút.
     - Khớp tên chuẩn hoá chính xác với listing.
     - Bổ sung VCI subs (mã 3 ký tự), gắn cờ `VCI_NODATE`.
     - Tầng 2: con không niêm yết nắm ≥ 50% × cổ đông lớn KBS của mã niêm yết.
     - Bỏ con niêm yết nằm lồng trong một con niêm yết khác.
     - Bỏ "con" thực chất là cổ đông mẹ (KBS ghi nhầm, ví dụ CQN ← T&T 77,77%).
   - **Bước 3 — tiêu chí nhận:** ≥ 1 con/liên kết NIÊM YẾT có lợi ích ≥ 20% ⇒ 116 holding.
   - **Bước 4 — tiền lọc:** độ phủ xấp xỉ ≥ 30% (BQ, không gọi VCI), cộng các mã ép đo theo brief ⇒ 26 mã được tải CĐKT VCI + giá.
   - **Bước 5 — giữ:** độ phủ ≥ 60% ở ≥ 3 tháng ⇒ N = 12.
   - Toàn bộ 104 mã bị loại kèm lý do: `calc_out_v2.json` → `excluded`.
     - 90 mã rớt tiền lọc (độ phủ xấp xỉ ở `inputs/prescreen.csv`). Trong `excluded` chúng hiện là "không có giá/VCSH/số CP", vì dữ liệu giá không được tải cho chúng.
   - Các ca brief nêu tên:
     - **MSN — VÀO N** (9,8%; không kiểm soát theo dữ liệu). MCH chỉ có 42,3% = VCI 60% (Masan Consumer Holdings, không ngày) × KBS 70,44%. MSR ("Tầm nhìn Masan") và MML không khớp được qua con trung gian ⇒ nằm ở phần sổ. Tỷ lệ MSN–MCH thật có thể cao hơn: cờ `VCI_NODATE`.
     - **HAG — loại:** không có con niêm yết ≥ 20% (HNG đã bán).
     - **GEE — loại:** độ phủ ≈ 0. CAV/THI/HEM không có giá trong BQ 2026, chỉ TBD 47% có giá. GEE CK −296% tại 20/11 chỉ phản ánh sổ, KHÔNG phải CK.
     - **Tầng chồng:** dữ liệu KBS cho thấy VGC 50,21% thuộc **GEL** (Hạ tầng GELEX), không phải GEE. Chuỗi đúng là GEX→GEL→VGC. GEL đã được thêm vào mẫu nhưng không có giá/số CP trong BQ ⇒ loại.
     - **VIC:** VinFast (Nasdaq) không có giá VND ⇒ nằm ở phần sổ, theo đúng quy tắc chung "chỉ giá niêm yết VN".
     - **CII:** loại vì LGC stale (mục 1).
   - **Tác động:** N 6 → 12. Trung vị 26,6% → 6,5%. Các mã mới vào: APH, CMX, LHC, MSN, MVN, OGC, VSC.
5. **Thời gian.** 24 ngày cuối tháng, 31/12/2024 → 20/11/2026.
   - PIT: tỷ lệ được dùng khi update_date + 90 ≤ D. KBS chỉ cho ảnh chụp BCTC gần nhất (31/12/2025, riêng VIC là 31/12/2024) ⇒ bản PIT chỉ có cắt ngang thật từ **31/03/2026** (n = 11–14). Trước đó chỉ còn VIC.
   - Bản "fixed" (áp ngược tỷ lệ hiện tại) có đủ 24 tháng, n = 11–14, nhưng là **look-ahead**, chỉ để đối chiếu.
   - Đường tháng PIT 2026: −4,6 → −4,6 → 1,4 → 5,0 → −3,5 → 1,4 → 6,5 → 19,7 → 23,0%. Phần lớn mức tăng dồn vào 10–11/2026.
   - **Phân tách phần trôi** (đầu → cuối cửa sổ, Δln):
     - Ở 7/11 holding không phải VIC, giá MẸ giảm mạnh hơn SOTP: PAN −0,50 vs −0,09; SNZ −0,41 vs −0,16; VSC −0,60 vs +0,18; CMX −0,32 vs −0,14; IPA −0,15 vs −0,09; OGC; MSN.
     - Tỷ trọng giá trị niêm yết ở con "đứng im" (|Δln giá| < 2%) = 0 ở 11/12 holding, MVN 1,6%.
     - ⇒ Sau khi loại stale, phần trôi **do giá mẹ giảm**, không phải do giá con đứng im.
   - **Tác động:** trung vị v1 (26,6%) tương ứng mức cuối 2026. Bình quân 2026 thấp hơn nhiều.
6. **Ngưỡng / tập so sánh / nhóm giống HHS.**
   - Ngưỡng độ phủ 50 / 60 / 70%: N 15 / 12 / 11, trung vị **3,2 / 6,5 / 2,3%**.
   - Leave-one-holding-out: **3,2% … 9,8%**.
   - Bỏ VIC: 9,8%. Chỉ mẹ trong universe_pit: 3,2% (N = 11). Độ phủ thanh khoản ≥ 60%: −12,6% (N = 7).
   - Kiểm soát (N = 9): 3,2%. Không kiểm soát (N = 3): 9,8%.
   - **Kiểm soát + cổ tức tiền con→mẹ < 1%/năm (giống HHS): N = 2** (CMX 68,1%, OGC −8,1%).
   - **Tầng chồng: N = 0.**
   - ⇒ **N không đủ để làm base.**

## 2. Bảng theo holding (bản chính)
| Holding | CK trung vị | min…max tháng | Số tháng | Độ phủ | Độ phủ thanh khoản | Kiểm soát | Cổ tức tiền con→mẹ / năm |
|---|---|---|---|---|---|---|---|
| CMX | 68,1% | 62,2…72,4 | 7 | 0,75 | 0,00 | có | 0,0% |
| VSC | 55,3% | 15,3…62,9 | 6 | 0,66 | 0,28 | có | 6,6% |
| IPA | 42,2% | 34,9…46,2 | 9 | 1,13 | 1,13 | không | 9,9% |
| GEX | 36,6% | 23,4…49,9 | 9 | 0,73 | 0,73 | có | 9,6% |
| SNZ | 10,3% | 6,4…27,0 | 9 | 0,82 | 0,23 | có | 16,2% |
| MSN | 9,8% | 0,6…14,1 | 9 | 0,97 | 0,97 | không* | 19,0% |
| PAN | 3,2% | −21,2…19,1 | 9 | 0,71 | 0,31 | có | 19,6% |
| OGC | −8,1% | −101,6…49,2 | 9 | 1,20 | 0,00 | có | 0,0% |
| APH | −12,6% | −33,7…−3,5 | 9 | 1,11 | 1,11 | không | 8,5% |
| LHC | −38,7% | −63,3…−15,3 | 9 | 1,00 | 1,00 | có | 17,7% |
| VIC | −166,7% | −308,1…−4,6 | 21 | 1,15 | 1,13 | có | 3,2% |
| MVN | −167,7% | −201,4…−141,8 | 9 | 0,78 | 0,63 | có | 5,3% |

\* MSN–MCH 42,3% là tích qua trung gian (VCI không có ngày). Cột cổ tức là trung bình qua các tháng; tử số tính trên giá trị niêm yết của các con không lồng nhau.

CK âm (VIC, MVN, LHC, APH) = mẹ giao dịch trên SOTP:
- VIC: vốn hoá mẹ ×8,5 trong cửa sổ (Δln 2,14; gồm thưởng 1:1 12/2025).
- MVN: free-float nhỏ.

Đây là dữ liệu thật, không phải lỗi, nhưng nó làm trung vị nhạy với việc chọn mẫu.

## 3. Hạn chế
1. Tỷ lệ sở hữu PIT chỉ có từ ảnh chụp BCTC năm gần nhất. Cắt ngang PIT thật chỉ có từ 03/2026. Bản 24 tháng là tỷ lệ cố định (look-ahead).
2. PAN, số CP 06–09/2026: AIS_UNCERTIFIED/AIS_EXACT gồm cả cổ phiếu quỹ (mục 1.2). Chưa sửa.
3. Tầng 2 khớp theo tên cổ đông lớn KBS (top holders). Chuỗi nhiều tầng hơn (MSR/MML) bị bỏ sót ⇒ nằm ở phần sổ.
4. Tiền lọc 30% dùng VCSH tổng BQ (gồm NCI) ⇒ có thể đã loại nhầm một holding sát ngưỡng. Danh sách để soát: `inputs/prescreen.csv`.
5. Survivorship: chỉ gồm mã còn niêm yết. Nhiều con UPCOM mỏng (cov_liq < 0,3 ở CMX, OGC, PAN, SNZ, VSC).
6. CK là chiết khấu tổng hợp (quản trị, thuế hai lần, thanh khoản, cảm tính), không tách được từng thành phần.

## 4. Tái lập
- Lệnh chạy: `cd WorkingClaude && source wc_env.sh && python3 .../fetch_inputs_v2.py universe kbs match prescreen vci market` (cần mạng; có cache trong `raw/`), rồi `python3 calc_ck_v2.py > run1.txt` (tất định, không cần mạng).
- `raw/kbs_subs`, `raw/kbs_sh` (497 + 364 json), `raw/vci_bs` (CĐKT quý 2020–2026), tổng 12 MB.
