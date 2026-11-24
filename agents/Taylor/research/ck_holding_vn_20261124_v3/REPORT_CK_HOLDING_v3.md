# CK holding niêm yết VN — v3 (job Taylor_20261124_041821, 24/11/2026)

Chỉ đo tham số (hiển thị / đầu vào DD). KHÔNG dựng rev8 HHS, KHÔNG ghi sổ, KHÔNG wire. Không đọc giá HHS/TCH/CRV.
Nguồn số: `run1.txt` = `run2.txt` = `run_dna.txt` (md5 `b8cf3c781a6ffa9d5b12f8ce9d61c107`; python3/pandas 2.3.3 và
`$DNA_PYEXE`/pandas 3.0.2 cho kết quả GIỐNG HỆT, cả `calc_out_v3.json` `a0ff4f43…` và `panel_v3.csv` `8a06d01b…`).
Khoá: `LOCK_md5.txt`. Pre-registration: `PREREG_v3.md` (md5 `7a7aef59…`, khoá 11:21:44 ICT trước calc v3; chép nguyên văn ở Phụ lục A).

## 0. Kết luận

**Không có dải nào vừa hẹp vừa trung thực.** Theo tiêu chí khai trước (§C), dải tham chiếu trung tâm là
**[−11,9% … 1,5% … +23,0%]**, rộng **34,9pp**. Mức này vượt ngưỡng "có nghĩa" 20pp, nên **KHÔNG ĐẠT**.
Tôi không ép dải hẹp hơn.

- **Đây là dải của TRUNG TÂM** (CK trung vị của holding VN), không phải dải của "một holding bất kỳ".
  - Nó gộp hai nguồn bất định về trung tâm:
    - Theo đặc tả đo: −10,3 … +7,4% (17,8pp).
    - Theo thời gian, trung vị cắt ngang từng tháng: −11,9% (03/2026) → +23,0% (11/2026).
  - Đường tháng tăng gần như đơn điệu: tự tương quan lag-1 0,96, T_eff ≈ 0,2. Tức là 9 tháng chỉ tương đương **≈1 quan sát độc lập**.
  - Dải hẹp 17,8pp của (a) chỉ đúng như **trung bình 03–11/2026**. Nó giấu xu hướng 35pp, nên KHÔNG được dùng riêng.
- **Dải "một holding bất kỳ"** (IQR liên-holding, N = 13) rộng hơn nhiều: **−38,7% … +36,6%** (75pp). Kể cả sau loại cấu trúc theo quy tắc khai trước, vẫn còn 64,5pp (§2b).
- **0% nằm TRONG dải trung tâm, ở phân vị 0,34**, gần trung vị đo được 1,5%. Vị trí so với các mốc:
  - Bỏ KSF (mã BANNED của fleet) thì trung vị là 5,6%.
  - Tháng gần nhất (20/11/2026) là 23,0%.
  - ⇒ Base 0% xấp xỉ trung tâm gộp, **hơi lạc quan** so với bản bỏ KSF, và **lạc quan rõ** so với trạng thái hiện tại.
  - CK càng cao thì giá trị HHS càng thấp.
- **Gợi ý cách dùng cho HHS (phương án A của user):**
  - Base 0%.
  - Độ nhạy ở hai đầu dải trung tâm: **−12% / +23%**.
  - Ghi rõ +23% là mức của tháng gần nhất trong một xu hướng chưa đảo chiều.
  - So với v2 (0 / 6,5 / 23 / 38%): bỏ mốc 38%, vì đó là q75 phân tán liên-holding, không phải trung tâm. Thêm đầu âm −12%.
- **Độ tin: THẤP.** Có ba lý do:
  - N = 13 holding, trong 1 chế độ thị trường.
  - Cắt ngang PIT thật chỉ có 9 tháng.
  - Trung vị đổi dấu theo đặc tả hợp lý.

### Bảng ứng viên dải (khai trước — PREREG §B)
| Ứng viên | Thấp | Giữa | Cao | Rộng (pp) | N | Ổn định | Đo cái gì |
|---|---|---|---|---|---|---|---|
| (a) Lưới 12 đặc tả PIT (độ phủ 50/60/70 × VIC có/không × con mỏng giá/sổ) | −10,3% | 1,5% (chính) | 7,4% | 17,8 | 7–16 | LOO trung vị chính −3,3…5,6% | Bất định TRUNG TÂM theo đặc tả (gộp 03–11/2026) |
| (b) IQR sau loại cấu trúc R1 + R2 | −18,6% | 9,8% | 45,9% | 64,5 | 7 | LOO 5,6…23,2%; trung tâm theo tháng −4,6…29,0% | PHÂN TÁN liên-holding |
| (c1) Kiểm soát & cổ tức con→mẹ < 1% (giống HHS) | 11,0% | 30,0% | 49,1% | 38,1 | **2** | — | **Không đủ N** |
| (c2) Tercile cổ tức con→mẹ thấp nhất (≤ 5,2%/năm) | −166,7% | −101,4% | −8,1% | 158,6 | **5** | — | **Không đủ N** |
| (c3) Kiểm soát | −85,7% | −3,3% | 30,0% | 115,8 | 10 | LOO −8,1…1,5%; theo tháng −26,1…26,9% | Phân tán trong nhóm kiểm soát |
| (d) Trung vị tháng PIT (n ≥ 11) | −11,9% | −0,9% | 23,0% | 34,9 | 9 tháng (n = 11–15) | IQR tháng −8,7…7,9%; LOO: thấp −16,6…−9,7, cao 19,1…26,9 | TRUNG TÂM trôi theo thời gian |
| **Chọn (PREREG §C) = hull (a) ∪ (d)** | **−11,9%** | **1,5%** | **23,0%** | **34,9** | 13 | LOO trong dải: có | **Trung tâm. > 20pp ⇒ KHÔNG ĐẠT "có nghĩa"** |

- Cột "Giữa" của (a) và dòng chọn là trung vị đặc tả chính.
- (c1) N = 2 < 8 nên theo §C không thay được (a).

## 1. Đính chính so với v2 (mỗi lỗi: tác động lên N / trung vị / đường tháng)

Mốc so sánh v2: N = 12, trung vị 6,46%, IQR −19,1…38,0%, đường tháng 03→11/2026 −4,6 → 23,0%.

**1. PAN — thưởng 20% ex 29/05/2026 (sửa); rà toàn bộ mẫu.**
- **Quy tắc chung (cầu nối ISS):** với mọi thưởng / cổ tức CP trong `tav2_bq.corporate_action` (event ISS, method Bonus|DIV):
  - Nếu số CP dùng ở D ≥ ngày ex vẫn ≈ số trước ex, thì dùng S_pre × (1 + Σr), cộng các sự kiện cùng ngày ex. Gắn cờ `ISS_FIX`.
  - Ví dụ cộng cùng ngày: BSR có 0,315 + 0,30; sổ thật cho ×1,615.
- **Cổ phiếu quỹ:** nếu AIS (CP **phát hành**) lớn hơn BQ OShares đã công bố từ 0,5% đến 15%, và không có sự kiện CP nào sau cuối quý BQ, thì dùng BQ (CP **lưu hành**). Gắn cờ `TREASURY_FIX`.
- **PAN:**
  - 29/05 và 30/06: 208,89 tr → **250,67 tr**.
  - 07–09/2026: AIS 258,07 tr → **250,67 tr**.
  - **Bằng chứng cổ phiếu quỹ, kiểm số học:**
    - KL thưởng 41.778.416 = 20% × 208,89 tr lưu hành, chứ không phải × 216,29 tr phát hành.
    - Suy ra 258,07 − 250,67 = **7,40 tr CP quỹ**: không nhận thưởng, không tính vào vốn hoá.
- **CK PAN theo tháng (v2 → v3):**

  | Tháng | v2 | v3 |
  |---|---|---|
  | 05/2026 | 11,3% | −6,5% |
  | 06/2026 | 17,9% | 1,5% |
  | 07/2026 | −3,9% | −0,9% |
  | 08/2026 | 1,4% | 4,3% |
  | 09/2026 | 3,2% | 5,9% |

  Trung vị PAN: 3,2% → **1,5%**.
- **Tác động:**
  - N không đổi.
  - Trung vị mẫu 12 mã của v2 (tính theo luật v3): 6,46% → **5,63%**. Khớp số skeptic.
  - Đường tháng của mẫu v2 ở 05/2026: +1,4% → **−6,5%** (đổi dấu).
- **Rà toàn mẫu:**
  - Trên tập N, chỉ còn 2 sửa khác:
    - SZL 20/11/2026: `TREASURY_FIX` 1,6%.
    - MCH 01/2025: trước cửa sổ PIT, không ảnh hưởng.
  - Ngoài tập N có thêm `ISS_FIX` ở GCF, GLT, LAI, PSD, SHB (đầy đủ ở `share_fixes`).
  - Lệch còn lại trên tập N sau sửa (`share_audit_N`, |gap| > 2%) chỉ là ESOP (AAA 3%, VSC 5%). ESOP không phải sự kiện ex-giá, nên KHÔNG sửa.
  - Quyền mua và phát hành riêng lẻ (DXG, SCI, VTD…): giá ex trước khi CP mới niêm yết. Tôi KHÔNG sửa (hạn chế 4). Chúng không thuộc tập N, trừ con của DXG.

**2. T_eff / tự tương quan.**
- Chỉ tính trên 9 tháng có n ≥ 11 (03–11/2026): **ρ = 0,96, T_eff ≈ 0,20**.
- Bản kiểu v2 (21 tháng, gồm 12 tháng chỉ có VIC) cho ρ = 0,51. Con số T_eff ≈ 6,9 của v2 là sai.
- ⇒ Về thời gian, mẫu ≈ **1 quan sát độc lập**. Skeptic đo trên dữ liệu v2 được ρ 0,80 / T_eff ≈ 1,0; v3 còn thấp hơn.

**3. Tiền lọc — bỏ hẳn.**
- v3 đưa **cả 116 holding** đủ tiêu chí vào calc:
  - Tải thêm CĐKT VCI cho 69 mẹ + 221 con. 2 mã VCI không có dữ liệu: TAC, DPD.
  - Tải giá / số CP PIT cho 451 mã.
- Độ phủ được lọc **PIT theo từng tháng**, bằng **VCSH thuộc cổ đông mẹ** (VCI `owners_equity − minority_interests`).
- Không còn ảnh chụp 1 ngày 30/10/2026. `inputs/prescreen.csv` chỉ giữ để đối chiếu, calc không đọc.
- **Kết quả:**
  - **N 12 → 13.** Mã mới vào: **KSF**. Không mã nào ra.
  - Trung vị **5,63% → 1,49%**. Mã thứ 7/13 giờ là PAN, vì KSF −101% chen vào đuôi dưới.
- Các mã skeptic nghi bị loại oan đều không đạt độ phủ 60% ở tháng nào. Độ phủ cao nhất theo tháng: PVI 0,31; PPC 0,33; VLC 0,49; C32 0,29; PET 0,29; AAA 0,32; VSF 0,29.
- Các mã sát ngưỡng nhưng < 3 tháng ≥ 60%: DVN (1 tháng), FPT (1 tháng), CII (2 tháng).
- ⚠️ **KSF nằm trong danh sách BANNED vĩnh viễn của fleet.**
  - Con duy nhất là SSH 99,96%, mỏng: tại 30/10/2026 ADV60 ≈ 0,002 tỷ, khớp 5/60 phiên.
  - SSH dừng khớp từ 07/09/2026, nên KSF chỉ có 5 tháng.
  - Đặc tả chính vẫn giữ KSF, vì quy tắc khai trước không có ngoại lệ. Bỏ KSF thì trung vị 5,63%; bỏ cả con mỏng thì KSF tự rớt khỏi mẫu.
- Hạn chế còn lại: tiêu chí giữ holding (≥ 3 tháng đạt 60%) vẫn xét trên cả cửa sổ. Chỉ đường tháng (d) là PIT chặt.

**4. Con mỏng** (cờ `thin`: ADV60 < 0,1 tỷ HOẶC < 20 phiên khớp/60).
- **Đã dùng.** Độ nhạy:

  | Cách xử lý con mỏng | N | Trung vị |
  |---|---|---|
  | Tính theo giá (chính) | 13 | 1,5% |
  | Trọng 50% (½ giá + ½ sổ) | 11 | 1,2% |
  | Về sổ | 10 | −5,5% |
  | Loại holding có ≥ 50% giá trị niêm yết ở con mỏng | 11 | 1,5% |

- Đường tháng khi con mỏng về sổ: −21,2% (03/2026) → 9,8% (11/2026), n = 8–11.
- **CMX:** con duy nhất là CMM (lợi ích 74%, ADV60 0,045 tỷ, mỏng). CK 68,1% ở bản chính. Ở bản ½ và bản sổ, CMX còn 0 tháng đạt độ phủ ≥ 60% ⇒ **rớt khỏi N**.
  - ⇒ Đuôi trên +68% chỉ tồn tại nếu tin giá CMM.
  - Nhóm "giống HHS" (c1) chỉ có CMX và OGC, nên chính nó tựa vào một giá mỏng.
- Holding có tỷ trọng con mỏng đáng kể: KSF 100%, CMX 100%, SNZ 34%, PAN 30%, MVN 10%.

**5. pandas 2.x / 3.**
- `isinstance(r.nested_via, str)`, và `nested_via` mặc định là `''`.
- Chạy cả `python3` (pandas 2.3.3) lẫn `$DNA_PYEXE` (pandas 3.0.2): stdout, `calc_out_v3.json` và `panel_v3.csv` giống hệt md5.
- Bẫy N = 0 im lặng của v2 đã được loại.

## 2. Chi tiết ứng viên dải

**(a) Lưới đặc tả** (trung vị holding, PIT):

| Độ phủ | VIC | Con mỏng | N | Trung vị |
|---|---|---|---|---|
| 50% | có | giá | 16 | −2,1% |
| 50% | có | sổ | 13 | −0,8% |
| 50% | không | giá | 15 | 1,5% |
| 50% | không | sổ | 12 | 1,2% |
| **60%** | **có** | **giá** | **13** | **1,5%** |
| 60% | có | sổ | 10 | −5,5% |
| 60% | không | giá | 12 | 5,6% |
| 60% | không | sổ | 9 | −2,9% |
| 70% | có | giá | 11 | 5,1% |
| 70% | có | sổ | 8 | −10,3% |
| 70% | không | giá | 10 | 7,4% |
| 70% | không | sổ | 7 | −8,1% |

- Ngoài lưới:
  - Tỷ lệ cố định (look-ahead): −4,0% (N = 15).
  - Giữ giá stale: 7,7% (N = 14).
  - Chỉ độ phủ thanh khoản ≥ 60%: −12,6% (N = 7).
  - Bỏ VIC + MVN: 9,8% (N = 11).
- Bootstrap khối (holding × 3 tháng, B = 5.000): trung vị p5–p95 **−26,9 … +36,2%**. Mô hình này không có cú sốc chung, nên dải thật còn rộng hơn.

**(b) Loại cấu trúc theo quy tắc khai trước:**
- R1 (cổ đông lớn ≥ 85%) loại MVN (99,47%) và SNZ (99,54%).
- R2 (phần theo sổ âm) loại VIC (−54.282 tỷ), IPA (−728), APH (−134), OGC (−121).
- ⚠️ **Thiết kế R2 bắt rộng hơn ý định.**
  - Ý định là bắt VIC, nơi VinFast có vốn chủ âm.
  - Nhưng R2 cũng loại IPA/APH/OGC, những holdco có nợ ròng ở cấp mẹ. Ở các mã này, phần sổ âm là hợp lệ về kinh tế.
  - Tôi giữ đúng kết quả khai trước, không chọn lại.
- Để tham khảo, **POST-HOC, không dùng để chọn dải**:
  - Chỉ R1: N = 11, IQR −25,6 … 1,5 … 39,4%.
  - R1 + bỏ VIC: N = 10, IQR −11,5 … 5,6 … 40,8% (52pp).
- Mọi cách loại cấu trúc đều để lại phân tán ≥ 50pp. Phân tán liên-holding là thật, không phải do 2 ngoại lai.

**(c) Có điều kiện:**
- Chỉ "kiểm soát" đủ N (10). Nhóm này rộng 116pp, vì chứa VIC, MVN, KSF.
- Nhóm giống HHS (c1) N = 2. Kiểm soát sau loại cấu trúc N = 6.
- ⇒ **Không đủ** để làm dải có điều kiện.

**(d) Đường tháng PIT n ≥ 11** (CK trung vị cắt ngang, đặc tả chính):

| Tháng | 03/2026 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11/2026 |
|---|---|---|---|---|---|---|---|---|---|
| Trung vị | −11,9% | −9,8% | −8,7% | −2,6% | −0,9% | 0,5% | 7,9% | 19,7% | 23,0% |
| n | 15 | 13 | 12 | 12 | 11 | 12 | 12 | 12 | 12 |

- Mẫu 12 mã v2 theo luật v3: −4,6 / −9,8 / −6,5 / 1,5 / −0,9 / 4,3 / 7,9 / 19,7 / 23,0%.
- **Phần trôi:** ở 8/11 holding (không tính VIC, KSF), Δln giá MẸ thấp hơn Δln SOTP. Ví dụ:
  - PAN: −0,50 so với −0,09.
  - SNZ: −0,41 so với −0,17.
  - VSC: −0,60 so với +0,18.
  - CMX: −0,32 so với −0,14.
  - OGC: −0,41 so với +0,97.
- ⇒ CK tăng vì mẹ giảm giá nhanh hơn rổ con, như v2 đã thấy. Hiện chưa có bằng chứng nào cho thấy xu hướng này sẽ hồi về trung bình.

## 3. Bảng theo holding (bản chính: PIT, loại stale, độ phủ ≥ 60% ở ≥ 3 tháng)
| Holding | CK trung vị | min…max tháng | Tháng | Độ phủ | Độ phủ thanh khoản | Tỷ trọng con mỏng | Kiểm soát | Cổ tức con→mẹ/năm | Cờ |
|---|---|---|---|---|---|---|---|---|---|
| CMX | 68,1% | 62,2…72,4 | 7 | 0,75 | 0,00 | 1,00 | có | 0,0% | mỏng |
| VSC | 55,3% | 15,3…62,9 | 6 | 0,66 | 0,28 | 0,05 | có | 6,6% | |
| IPA | 42,2% | 34,9…46,2 | 9 | 1,13 | 1,13 | 0,00 | không | 9,9% | R2 |
| GEX | 36,6% | 23,4…49,9 | 9 | 0,73 | 0,73 | 0,00 | có | 9,6% | |
| SNZ | 10,3% | 6,4…26,9 | 9 | 0,82 | 0,23 | 0,34 | có | 16,2% | R1 |
| MSN | 9,8% | 0,6…14,1 | 9 | 0,97 | 0,97 | 0,00 | không | 18,9% | |
| PAN | 1,5% | −21,2…19,1 | 9 | 0,71 | 0,31 | 0,30 | có | 19,6% | ISS/TREASURY_FIX |
| OGC | −8,1% | −101,6…49,2 | 9 | 1,20 | 0,00 | 0,00 | có | 0,0% | R2 |
| APH | −12,6% | −33,7…−3,5 | 9 | 1,11 | 1,11 | 0,00 | không | 8,5% | R2 |
| LHC | −38,7% | −63,3…−15,3 | 9 | 1,00 | 1,00 | 0,00 | có | 17,7% | |
| KSF | −101,4% | −170,2…−85,1 | 5 | 0,67 | 0,00 | 1,00 | có | 1,2% | BANNED, mỏng |
| VIC | −166,7% | −308,1…−4,6 | 21 | 1,15 | 1,13 | 0,00 | có | 3,2% | R2 |
| MVN | −167,7% | −201,4…−141,8 | 9 | 0,78 | 0,63 | 0,10 | có | 5,3% | R1 |

Nguồn: `calc_out_v3.json` → `holdings`. Toàn bộ 103 mã bị loại kèm lý do: `excluded`.

## 4. Hạn chế còn lại
1. **Tỷ lệ sở hữu PIT chỉ từ ảnh chụp BCTC năm gần nhất** (KBS). Cắt ngang PIT thật chỉ có 03–11/2026 (9 tháng, T_eff ≈ 0,2). Mọi kết luận đều thuộc **1 chế độ thị trường** đang có xu hướng.
2. Tiêu chí giữ holding (≥ 3 tháng đạt 60%) dùng cả cửa sổ. Chỉ đường tháng (d) chọn PIT chặt từng tháng.
3. **KSF (BANNED) và CMX** tựa hoàn toàn vào giá con mỏng (SSH, CMM). Kết quả nhạy với cách xử lý con mỏng: trung vị 1,5% → −5,5% khi về sổ.
4. Quyền mua / phát hành riêng lẻ: giá ex trước khi CP mới niêm yết. Vốn hoá giai đoạn đó bị đánh giá thấp một phần, chưa sửa. Trên tập N không có ca nào, trừ con của các holding (DXG ngoài N).
5. Cầu nối ISS dựa vào `corporate_action` (sự kiện có `exercise_ratio`). Quy tắc cổ phiếu quỹ là suy luận từ AIS so với BQ, không đối chiếu thuyết minh BCTC, trừ PAN đã kiểm số học. MCH, SP2, SZL, GLT được sửa theo quy tắc chung.
6. Tầng 2 chỉ khớp theo tên cổ đông lớn KBS. Chuỗi sâu hơn (MSN → MSR/MML) nằm ở phần sổ. MSN–MCH 42,3% thiếu ngày (`VCI_NODATE`).
7. **R2 khai trước bắt rộng hơn ý định**, loại cả holdco nợ ròng (§2b). Đây là lỗi thiết kế quy tắc của tôi. Bản post-hoc chỉ để tham khảo.
8. Survivorship: chỉ gồm mã còn niêm yết. Chưa có premium / CK của holding đã huỷ niêm yết.
9. CK là chiết khấu tổng hợp (quản trị, thuế hai lần, thanh khoản, cảm tính), không tách được từng thành phần. Bootstrap không mô hình cú sốc chung.
10. Nit: PREREG ghi giờ "11:22", trong khi md5 khoá lúc 11:21:44. File không sửa sau khoá.
11. Chưa qua quant-skeptic vòng v3.

## 5. Tái lập
- Đầu vào: `cd WorkingClaude && source wc_env.sh && python3 .../fetch_inputs_v3.py universe kbs match vci market vcilong capevents`. Các stage có cache trong `raw/`. Bản này chạy lại `vci market vcilong capevents`; universe/kbs/match tái dùng nguyên của v2.
- Tính: `python3 calc_ck_v3.py > run1.txt` (tất định, không cần mạng). Chạy cùng kết quả với `$DNA_PYEXE`.

## Phụ lục A — PREREG_v3.md (nguyên văn)
# PRE-REGISTRATION — CK holding VN v3 (job Taylor_20261124_041821)

Ghi lúc **2026-11-24 11:22 ICT**, TRƯỚC khi chạy calc v3 (chưa có bất kỳ số v3 nào; số v2 đã biết — xem REPORT v2).
File này khoá md5 trong LOCK_md5.txt và được chép nguyên văn vào đầu REPORT_CK_HOLDING_v3.md. Không sửa sau khi chạy.

## A. Đặc tả chính (thay v2)
- Mẫu: TOÀN BỘ 116 holding qualify (≥1 con niêm yết lợi ích ≥20%); KHÔNG tiền lọc 1 ngày. Lọc độ phủ làm PIT
  theo từng tháng D trong calc, độ phủ tính bằng VCSH thuộc cổ đông MẸ (VCI CĐKT; thiếu VCI ⇒ fallback BQ có cờ).
- Giữ holding: độ phủ ≥60% ở ≥3 tháng (như v2). Giá con STALE ⇒ về sổ (như v2).
- Số CP: cầu nối ISS — với mỗi sự kiện thưởng / cổ tức CP (corporate_action ISS, method Bonus|DIV, tỷ lệ r) ex E:
  với mọi D ≥ E (tới trước sự kiện CP kế tiếp khác loại), số CP kỳ vọng = S_pre × Π(1+r) với S_pre = số CP dùng ở
  tháng cuối trước E. Lệch > 2% ⇒ dùng số kỳ vọng, gắn cờ ISS_FIX, liệt kê toàn bộ. (PIT: tỷ lệ thưởng công bố trước ex.)
- Con mỏng (thin) = ADV60 < 0,1 tỷ VND HOẶC số phiên khớp trong 60 phiên < 20. Đặc tả chính: giữ giá thị trường
  (như v2); độ nhạy: thin → sổ, thin trọng 50% (½ giá + ½ sổ).
- T_eff / tự tương quan: chỉ trên tháng có n ≥ 11.

## B. Ứng viên dải (khai trước)
(a) **Bất định trung tâm qua đặc tả**: lưới PIT = độ phủ {50,60,70%} × VIC {có, không} × con mỏng {giá, sổ}
    (12 đặc tả). Dải = [min … đặc tả chính … max] của trung vị holding. Đo: "trung tâm" nhạy thế nào với lựa chọn
    hợp lý. Bản tỷ lệ cố định (look-ahead) báo riêng, KHÔNG vào lưới.
(b) **IQR sau loại cấu trúc** — quy tắc chung, không theo kết quả:
    R1 free-float: tổng cổ đông lớn (KBS, mỗi cổ đông ≥5%) của MẸ ≥ 85% ⇒ loại (giá mẹ không phản ánh thị trường).
    R2 phần theo sổ âm: trung vị tháng của (E_mẹ − Σ s_i E_i) < 0 ⇒ loại (sổ âm của mảng không niêm yết lỗ
       không phải proxy giá trị hợp lý; SOTP mất nghĩa). Áp như nhau cho mọi holding.
    Dải = [q25 … trung vị … q75] cắt ngang holding còn lại. Đo: PHÂN TÁN liên-holding (một holding bất kỳ).
(c) **Có điều kiện giống HHS**: (c1) kiểm soát & cổ tức tiền con→mẹ < 1%/năm; (c2) tercile thấp nhất cổ tức
    con→mẹ; (c3) kiểm soát. Dải = [q25 … trung vị … q75]. N < 8 ⇒ ghi "không đủ", không dùng.
(d) **Theo thời gian**: trung vị cắt ngang mỗi tháng PIT có n ≥ 11 (đặc tả chính). Dải = [min … trung vị các tháng
    … max], kèm IQR của đường tháng. Đo: trung tâm trôi theo thời gian trong 1 chế độ.
Mỗi ứng viên báo: thấp/giữa/cao, độ rộng (pp), N, LOO-holding (min…max trung vị), ổn định theo tháng.

## C. Tiêu chí chọn dải tham chiếu cho HHS (khai trước, theo MỤC ĐÍCH không theo độ rộng)
1. Câu hỏi của HHS là "CK base hợp lý cho một holding kiểu HHS" ⇒ đại lượng cần là TRUNG TÂM, không phải phân tán.
   Ứng viên đo trung tâm: (a), (d), và (c) nếu N ≥ 8.
2. Dải tham chiếu = **bao (hull) của (a) và (d)** — vì cả bất định đặc tả lẫn trôi thời gian đều là bất định về
   trung tâm; chọn một trong hai sẽ giấu phần kia. Nếu (c) đạt N ≥ 8 thì dùng (c) thay cho (a) và ghi rõ.
3. Điều kiện "có nghĩa": độ rộng ≤ 20pp VÀ LOO-holding của trung vị chính nằm trong dải. Không đạt ⇒ nói thẳng
   "không có dải vừa hẹp vừa trung thực", báo dải trung thực rộng.
4. (b) LUÔN báo kèm như dải phân tán "một holding bất kỳ" — không dùng làm tham chiếu trung tâm.
5. Báo 0% nằm đâu trong dải được chọn (dưới / trong / trên; phân vị nếu trong).
