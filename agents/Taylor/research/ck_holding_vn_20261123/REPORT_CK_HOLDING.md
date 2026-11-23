# Chiết khấu holding (CK holding) — holding niêm yết VN, đo 23/11/2026 (job Taylor_20261123_120407)

Tham số định giá cho DD (chỉ hiển thị / đầu vào DD). **Không** wire vào production hay sizing.

## 0. Kết luận
- **N = 6 holding độc lập** đạt độ phủ giá thị trường ≥ 60% SOTP: CII, GEX, IPA, PAN, SNZ, VIC. Đã đo 17 holding; 11 holding còn lại có độ phủ < 60% nên bị loại (§3).
- **CK toàn nhóm (N = 6):**
  - Trung vị **26,6%**, IQR **20,0% – 38,8%**.
  - Khoảng min…max là −245% (VIC giao dịch cao hơn nhiều so với SOTP) … +51% (GEX).
  - Bootstrap theo holding (10.000 lần), khoảng 5–95% của trung vị: **−110% … +42%**. Khoảng này rộng vì N nhỏ và có VIC.
  - Bỏ VIC (N = 5): trung vị **29,2%**.
- **Nhóm giống HHS:**
  - Nhóm (i) *kiểm soát* (≥ 50% giá trị niêm yết đến từ công ty con nắm ≥ 50%): N = 5, trung vị **24,1%**, IQR 18,6–29,2%.
  - Nhóm (i)+(ii) *kiểm soát + cổ tức tiền từ con < 1%/năm*: chỉ có **N = 1** (CII, 24,1%). **Không đủ N** để dùng nhóm này làm base.
  - Nhóm (iii) *tầng chồng* (TCH→HHS→CRV): không có holding nào trong mẫu có công ty mẹ niêm yết nắm ≥ 50% phía trên. GEX→GEE→VGC là tầng chồng **phía dưới**. ⇒ **N = 0** cho đặc điểm này.
- **Kiểm chứng chéo thứ hai:** Spearman giữa CK và tỷ suất cổ tức tiền con→mẹ là **+0,37 (N = 6)**. Dấu này **ngược** giả thuyết "càng nhận nhiều cổ tức tiền thì CK càng thấp" và N quá nhỏ ⇒ **không xác nhận được**. Không làm phép kiểm cặp mẹ–con lịch sử (xem §4: không có lịch sử sở hữu point-in-time).
- **Độ tin: THẤP–TRUNG BÌNH.**
  - Nguồn độc lập và truy được (BCTC qua KBS, giá BQ chưa điều chỉnh, số CP point-in-time).
  - Nhưng N nhỏ.
  - 3/6 holding có độ phủ chủ yếu đến từ giá công ty con **kém thanh khoản**. Lấy theo độ phủ thanh khoản (universe_pit) ≥ 60% thì chỉ còn N = 3, trung vị 42,0%.
  - 4/6 holding dùng VCSH mẹ xấp xỉ (§2).

## 1. Định nghĩa và nguồn
- **Công thức** (`calc_ck.py`, tại mỗi ngày đo D, chỉ dùng dữ liệu đã công bố ≤ D):
  - SOTP = Σ sᵢ·MVᵢ + (E_mẹ − Σ sᵢ·Eᵢ)
  - Độ phủ = Σ sᵢ·MVᵢ / SOTP
  - CK = 1 − MV_mẹ / SOTP
  - Phần trong ngoặc là phần **theo sổ**: công ty không niêm yết, BĐS, tiền và nợ cấp mẹ. Nợ ròng cấp holding đã nằm sẵn trong E_mẹ (VCSH thuộc cổ đông mẹ = tài sản − nợ), nên không trừ lần nữa.
- **Ngày đo:** 31/03, 30/06, 30/09, 20/11/2026. CK của mỗi holding là **trung vị 4 ngày**.
- **Tỷ lệ sở hữu sᵢ:**
  - Lấy tỷ lệ lợi ích theo BCTC năm (KBS `subsidiaries`, `update_date` 31/12/2025). Riêng VIC là 31/12/2024; GVR và PLX là 31/12/2022.
  - Chỉ dùng sᵢ khi `update_date` + 90 ngày ≤ D (hạn nộp BCTC năm).
  - Đối chiếu với VCI (`inputs/stakes.csv` cột `stake_vci`). VCI thiếu nhiều cổ phần lớn và có chỗ lệch, ví dụ CII–NBB 21,9% (VCI) so với 79,8% (KBS). Dùng KBS vì có gắn ngày BCTC.
  - Tên công ty con được khớp với mã niêm yết theo tên chuẩn hoá **khớp tuyệt đối** (`raw/listing_vci_20261123.csv`).
- **MV:** giá **chưa điều chỉnh** (`ticker.Price`, không dùng Close đã điều chỉnh) × số CP point-in-time `oshares_live.oshares_at` (neo AIS). Nếu bị từ chối thì dùng dòng `ticker_financial.OShares` có Release_Date ≤ D, có gắn cờ `FALLBACK_FIN_RELEASED`. Tránh bẫy `ticker_financial_oshares.md` (OShares bị restate).
- **E (VCSH thuộc cổ đông mẹ):**
  - Lấy từ CĐKT quý VCI (`owners_equity − minority_interests`), chọn quý có Release_Date ≤ D. Kiểm tra bằng HHS Q3/2026: 16.880 − 7.727 = 9.153 tỷ, khớp EQ_ME của rev6.
  - ⚠ **Bẫy mới:** `ticker_financial.BVPS × OShares` là VCSH **TỔNG, gồm lợi ích thiểu số**. HHS: 39.075 × 432 tr = 16.880 tỷ.
- **Giá HHS / TCH / CRV:** **không đọc** (luật mù giá). Cặp TCH→HHS bị loại khỏi mẫu.

## 2. Bảng theo holding (`calc_out.json` md5 `e78cc0d9…`)
| Holding | CK trung vị | CK min…max (4 ngày) | Độ phủ | Độ phủ thanh khoản | Kiểm soát | Cổ tức tiền con→mẹ / giá trị niêm yết / năm | VCSH mẹ | Cấu trúc |
|---|---|---|---|---|---|---|---|---|
| GEX | 51,3% | 35,4…56,5% | 0,65 | 0,65 | có | 7,9% | xấp xỉ (BQ − NCI con niêm yết) | GEX→GEE 75,95% (→VGC: tầng chồng phía dưới) |
| IPA | 42,0% | 28,1…48,1% | 1,09 | 1,09 | không (VND 25,84% liên kết) | 3,4% | xấp xỉ | holding tài chính |
| SNZ | 29,2% | 20,5…40,4% | 0,69 | 0,20 | có (65%) | 7,3% | xấp xỉ | PDN, DNW, SZC, SZG, SZL, D2D… (UPCOM kém thanh khoản) |
| CII | 24,1% | 1,2…40,6% | 0,66 | 0,10 | có | 0,8% | chính xác (VCI) | LGC 54,84% (kém thanh khoản) + NBB 79,79% |
| PAN | 18,6% | 3,0…36,2% | 0,86 | 0,28 | có | 5,6% | xấp xỉ | FMC, VFG, NSC, BBC, ABT, LAF |
| VIC | −245% | −309…−168% | 1,15 | 1,15 | có | 4,5% | chính xác | VHM 73,5%, VPL 85,55% (tỷ lệ theo BCTC 2024) |

**VCSH mẹ xấp xỉ** (khi không có CĐKT VCI vì API trả HTTP 418): E_mẹ ≈ VCSH tổng BQ − Σ (1 − sᵢ)·Eᵢ của các con niêm yết nắm ≥ 50%.
- Phần NCI tầng chồng phía dưới tự triệt tiêu, vì nó vừa nằm trong E_mẹ vừa nằm trong sᵢ·Eᵢ.
- Phần NCI của **con không niêm yết** nắm trực tiếp thì bị bỏ sót. Khi đó E_mẹ bị đánh giá **cao**, nên CK bị đánh giá **cao**. Đây là thiên lệch một chiều cho GEX, IPA, PAN, SNZ.
- Độ nhạy "chỉ holding có VCSH mẹ chính xác" chỉ còn N = 2 (CII, VIC). Không đọc được thông tin gì từ đó.

## 3. Loại vì độ phủ < 60%
BCM 0,16 · DXG 0,42 · FIT 0,49 · GVR 0,25 · KDC 0,20 · PLX 0,09 · REE 0,48 · SJG 0,16 · TVN 0,16 · VEA 0,00 · VGT 0,24.
- CK của nhóm này phần lớn phản ánh **giá sổ** của phần không niêm yết, không phải CK holding.
- Ví dụ: BCM −133%, GVR −98% (quỹ đất ghi theo giá gốc); FIT +71%, TVN +35%.
- Độ nhạy theo ngưỡng độ phủ: ở ngưỡng 50%, N = 6, trung vị 26,6% (không đổi). Ở ngưỡng 70%, N = 3, trung vị 18,6%.

## 4. Hạn chế (nói thẳng)
1. **Không có chuỗi 2019–2026.**
   - Lịch sử tỷ lệ sở hữu point-in-time không có ở dạng máy đọc: KBS và VCI chỉ cho ảnh chụp BCTC gần nhất. Giữ tỷ lệ hiện tại cho các năm trước là look-ahead, đúng loại lỗi mà `holdco_sotp_screen.py` (07/2026) đã ghi là hạn chế.
   - API VCI chặn (HTTP 418) sau khoảng 57 mã, nên không lấy được thêm CĐKT.
   - ⇒ Chỉ đo được 4 ngày trong năm 2026. Vì vậy CK này là **ảnh chụp năm 2026, không phải trung bình chu kỳ**.
2. **Survivorship:** mẫu chỉ gồm holding còn niêm yết đến 11/2026. Các holding đã huỷ niêm yết hoặc đã bán con (HAG→HNG 2021, GTN…) không có trong mẫu.
3. **Giá công ty con kém thanh khoản:** LGC (CII), PDN/DNW/SZG (SNZ), BBC/NSC/VFG (PAN) đều nằm ngoài universe_pit. Giá UPCOM mỏng có thể lệch xa giá trị khớp được.
4. **Tỷ lệ sở hữu cũ:** VIC dùng BCTC 2024 (VPL niêm yết 05/2025). GVR và PLX dùng BCTC 2022 nhưng đều đã bị loại vì độ phủ thấp.
5. **Giá trị sổ của con trong E_mẹ** có thể khác sᵢ·Eᵢ do lợi thế thương mại, PPA và giao dịch nội bộ. Phần chênh rơi vào mục "theo sổ".
6. CK đo được là chiết khấu thị trường **tổng hợp** (gồm quản trị, thuế hai lần, thanh khoản của chính holding, cảm tính). Nó **không** tách riêng được từng thành phần.

## 5. Tái lập
- `fetch_inputs.py`: gom dữ liệu vào `inputs/*.csv`, cần mạng và BQ.
- `calc_ck.py`: tất định, chạy 2 lần cho `run1.txt` = `run2.txt` = md5 `4585c248…`.
- Các khoá md5 ở `LOCK_md5.txt`. Snapshot nguồn thô ở `raw/` (KBS, VCI, listing, CĐKT).
