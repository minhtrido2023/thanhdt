# HHS — DD rev7 (23/11/2026, job Taylor_20261123_120407)

rev7 thay giả định chiết khấu holding (CK holding) của rev6 bằng một số **đo được**. rev6 giữ song song hai mức 0% và 27%, cả hai đều không có nguồn. Số mới lấy từ phép đo CK của các holding niêm yết tại Việt Nam (`agents/Taylor/research/ck_holding_vn_20261123/REPORT_CK_HOLDING.md`).

Mọi phần còn lại giữ nguyên rev6: lưới r3, pha loãng (quyền mua 5:3 @10.000 cộng cổ tức cổ phiếu 7%), tách khối HH1–HH4, PPA, quỹ khen thưởng phúc lợi.

- **Giả định khoá:** `rev7/calc/assumptions.json`, md5 `3afcd113013fad82acfa5ea35c5bce1d`. Lint 0 vi phạm.
- **Calc:** `rev7/calc/calc_rev7.py`, md5 `a098b003…`. Chạy hai lần, `run1.txt` = `run2.txt` = `967960e1…`. Output: `rev7/calc/calc_rev7_out.json` (md5 `b7d912f6…`).
- **LOCK:** `rev7/calc/LOCK_md5.txt`, ghi lúc 19:24 ICT 23/11/2026.
  - rev7 **không truy vấn giá HHS**. Giá so sánh 9.700 (BQ 20/11/2026) kế thừa từ rev5/rev6.
  - Phép đo CK **không dùng giá HHS, TCH hay CRV**. Cặp TCH→HHS bị loại khỏi mẫu.
- **Nguồn CK:** `ck_holding_vn_20261123/calc_out.json`, md5 `e78cc0d9…`. Calc của rev7 assert md5 file này và assert trung vị = 0,2663.

## 0. Kết luận

**Tâm CUM giảm từ 13.969 (rev6) xuống 10.805.** Vùng mới 9.634–12.012. Nhãn đổi từ DƯỚI vùng sang **TRONG vùng** ở giá 9.700. Luật 4 **KHÔNG ĐẠT**: ngưỡng 0,85 × tâm = 9.184 thấp hơn 9.700.

| Cơ sở | CK holding | Tâm | P10 | P50 | P90 | Giá so sánh | Nhãn | Luật 4 (giá ≤ 0,85 × tâm) |
|---|---|---|---|---|---|---|---|---|
| **CUM — BASE rev7** | **26,63% (đo, N = 6)** | **10.805** | **9.634** | 10.765 | **12.012** | 9.700 (BQ 20/11/2026) | **TRONG vùng** | KHÔNG (ngưỡng 9.184) |
| CUM — độ nhạy IQR thấp | 19,98% | 11.595 | 10.324 | 11.558 | 12.879 | 9.700 | DƯỚI vùng | ĐẠT (9.856) |
| CUM — độ nhạy IQR cao | 38,83% | 9.355 | 8.365 | 9.320 | 10.409 | 9.700 | TRONG vùng | KHÔNG (7.952) |
| CUM — nhóm kiểm soát (N = 5) | 24,06% | 11.110 | 9.901 | 11.073 | 12.346 | 9.700 | DƯỚI vùng | KHÔNG (9.444) |
| CUM — bỏ VIC (N = 5) | 29,21% | 10.498 | 9.367 | 10.457 | 11.676 | 9.700 | TRONG vùng | KHÔNG (8.923) |
| CUM — chỉ tính độ phủ thanh khoản (N = 3) | 42,03% | 8.975 | 8.033 | 8.939 | 9.993 | 9.700 | TRONG vùng | KHÔNG (7.629) |
| CUM — đối chiếu: 0% (headline rev6, không nguồn) | 0% | 13.969 | 12.422 | 13.917 | 15.564 | 9.700 | DƯỚI vùng | ĐẠT (11.874) |
| CUM — đối chiếu: trục r2, kỳ vọng 27% (**không nguồn**) | 0/15/25/35/45% | 10.761 | 8.624 | 10.559 | 13.207 | 9.700 | TRONG vùng | KHÔNG (9.147) |
| CUM — độ nhạy: CK 26,63% áp lên **toàn bộ** NAV | 26,63% | 10.249 | 9.114 | 10.211 | 11.419 | 9.700 | TRONG vùng | KHÔNG |
| **EX — BASE** (phát hành đủ 100%, k = 1 − CK = 0,734) | 26,63% | **8.846** | 8.162 | — | 9.551 | TERP sau cổ tức 9.171 | **TRONG vùng** | KHÔNG (7.519) |
| EX — k = 1 (tiền góp vốn không chịu CK) | 26,63% | 9.767 | — | — | — | 9.171 | — | KHÔNG (8.302) |

**Đọc bảng:**
- Ở giá 9.700, nhãn nằm sát đáy vùng: P10 = 9.634, giá chỉ cao hơn P10 0,7%.
- Nhãn đổi theo mức CK trong khoảng IQR:
  - CK ≤ ~25% (IQR thấp hoặc nhóm kiểm soát): DƯỚI vùng.
  - CK ≥ 26,6%: TRONG vùng.
- **Không có mức CK nào trong khoảng đo được cho nhãn TRÊN vùng.**

**Giữ nguyên từ rev6:**
- HHS nằm trong `forensic_flags` EXCLUDE ⇒ không vào candidate plan, bất kể nhãn nào.
- Sizing V8 không áp dụng.

**Độ tin của tham số CK: THẤP–TRUNG BÌNH.** Lý do nằm ở §2. Nếu user không chấp nhận phép đo này làm base, dòng đối chiếu 0% (13.969, DƯỚI vùng) vẫn còn nguyên trong bảng. rev7 không xoá bản nào.

## 1. Đính chính so với rev6

| # | Hạng mục | rev6 | rev7 | Nguồn | Ảnh hưởng tâm CUM |
|---|---|---|---|---|---|
| 1 | CK holding trong base | 0%. Song song 27%. **Cả hai đều không có dữ liệu** | **26,63%** = trung vị N = 6 holding niêm yết VN có độ phủ giá thị trường ≥ 60% (CII, GEX, IPA, PAN, SNZ, VIC). IQR 19,98–38,83% làm độ nhạy | `ck_holding_vn_20261123/REPORT_CK_HOLDING.md` | 13.969 → **10.805** (−22,6%) |
| 2 | Nhóm "giống HHS" (kiểm soát + ít cổ tức tiền từ con + tầng chồng) | — | Nhóm này chỉ có N = 1 (CII, 24,06%). Không có holding nào có tầng chồng phía trên như TCH→HHS ⇒ **không đủ N**. Theo luật brief, dùng **trung vị toàn bộ**. Nhóm kiểm soát (N = 5, 24,06%) đưa vào độ nhạy | như trên | — |
| 3 | CK quản trị | Trục r2 là độ nhạy | Giữ **0** trong base. CK đo từ giá thị trường là chiết khấu **tổng hợp**, đã bao gồm phần quản trị; cộng thêm sẽ trừ hai lần | — | 0 |
| 4 | Skeptic r4: PPA được mô tả là "nguồn độc lập duy nhất" | Sai cách gọi | **Sửa lại:** PPA là giá trị hợp lý nội bộ nhóm, được kiểm toán chấp nhận, nhưng **không phải** định giá độc lập. Chỉ dùng PPA để kiểm tra nhất quán ở cấp tổng, như rev6 §2.1 vẫn làm (không dùng để nâng tâm) | skeptic `r4_raw.md` | 0 |
| 5 | Skeptic r4: neo w theo tỷ lệ **diện tích đất** (3,75%) là thấp | — | Ghi nhận. Khoảng w hợp lý là 10–30%, tương ứng −2,3% đến −9,0% (bảng rev6 §2.2). Vẫn là **kịch bản**, không vào base (V4). Ở CK 26,63%, lấy rev6 hh_split nhân tỷ lệ 10.805/13.969 thì tâm ở w 10–30% ≈ 10.550–9.830 (**ước lượng**), vẫn ≥ P10 9.634 ở w ≤ 15% | rev6 `calc_rev6_out.json` hh_split | 0 (kịch bản) |
| 6 | Skeptic r4: hai kết luận thanh tra bị rơi khỏi danh sách WARNING | Thiếu | **Khôi phục** TB 2124/TB-TTCP (CRV, 7,87 tỷ thu tạm) và KL 08/KL-TTTP (NƠXH Pruksa, chưa có số liệu) vào §4 | `dd_HHS_20261101/BRIEF_v2_investor.md` | 0 |

## 2. Áp CK holding: công thức, phạm vi và các trục không trùng

- **Công thức** (lõi `hhs_r3.make`, tham số `hd_fix = h`):
  - V = [ HHS × c × (1 − h) + OTHER + LNST ô tô × P/E + bds × BDS_SURP × HHS × (1 − h) − kq × KQ ] / 431,99 tr cp, sau đó trừ CK thanh khoản d5 = 1,41%.
  - HHS = 51,15% là lợi ích kinh tế của HHS tại CRV. c là giá trị CRV trong mô hình (giá gốc + thặng dư HTK × pv(y) + backlog).
- **Phần chịu CK:**
  - **Chịu CK:** chỉ phần HHS × CRV, gồm cả thặng dư BĐSĐT quy về HHS. Phần này chiếm **85,06%** NAV trước CK, ở lưới trung tâm.
  - **Không chịu CK, phần lợi ích thiểu số 48,85% của CRV:** phần này đã bị loại khỏi NAV HHS từ đầu, nên áp CK lên nó sẽ là trừ hai lần.
  - **Không chịu CK, OTHER (tài sản ròng riêng của HHS ngoài CRV) và mảng ô tô:** đây là tài sản HHS nắm trực tiếp, không đi qua tầng holding.
- **Tách khỏi các trục khác:**
  - **CK thanh khoản d5 (1,41%):** là chi phí tác động khi bán một vị thế 5 tỷ, áp sau cùng. Đây là khái niệm khác với chiết khấu thị trường của holding.
  - **Thời gian thực hiện y:** nằm trong pv(y) của c.
  - **CK quản trị:** = 0 vì đã nằm trong CK tổng hợp (#3).
- **Độ nhạy định nghĩa:** CK đo được là 1 − MV / SOTP **toàn bộ**. Áp lên toàn bộ NAV HHS thì tâm là 10.249 (−5,1% so với base). Base giữ cách áp theo phần CRV như brief yêu cầu.
- **EX:** dùng công thức rev5 §3 với k = 1 − h, nhất quán với bản song song 27% của rev5/rev6 (khi đó k = 0,73). Lý do: tiền quyền mua chảy vào NĐL/CRV và cũng nằm sau tầng holding. Với k = 1, tâm EX là 9.767.
- **Hạn chế của tham số** (chi tiết ở REPORT_CK_HOLDING §4):
  - N = 6, không có chuỗi 2019–2026. Đây là ảnh chụp năm 2026.
  - 3/6 holding có độ phủ phụ thuộc giá công ty con kém thanh khoản (CII, SNZ, PAN).
  - 4/6 holding dùng VCSH mẹ xấp xỉ, khiến CK bị đẩy **lên**.
  - Kiểm chứng chéo bằng cổ tức tiền con→mẹ cho kết quả ngược dấu giả thuyết (ρ = +0,37). **Không xác nhận được.**
  - HHS không có dòng cổ tức tiền từ CRV về, và nằm ở **tầng chồng phía dưới** (TCH → HHS → CRV). Cả hai đặc điểm thường gắn với CK cao hơn trung vị. Nhưng mẫu không có N để đo hai đặc điểm này ⇒ **không điều chỉnh**, chỉ ghi nhận.

## 3. Luật định giá (giữ rev6 §4, chỉ đổi phần CK holding)
- **V1:** r = 13,50%. Độ nhạy ±50/±100bp ≈ 0 đ/cp (NAV quỹ đất).
- **V3:** CK thanh khoản 1,41% kế thừa.
- **V4:**
  - CK holding giờ có dòng dữ liệu độc lập và nguồn, nên được vào base.
  - Phần cao tầng HH1–HH4 vẫn là kịch bản.
  - Chi phí hoàn thiện G10 = NPV0.
- **V5:** 5F 07–09/11/2026 tái dùng.
  - Moat NONE / LOCATION.
  - Rủi ro số 1: dòng tiền đi qua hai tầng holding. Rủi ro này nay đã được định giá một phần qua CK 26,63%.
- **V6:** V_ngắn 4.466 đ/cp chỉ hiển thị.
- **V8:** không áp vì EXCLUDE.

## 4. WARNING (giữ rev6, bổ sung theo skeptic r4)
- Tăng vốn 60% (quyền mua 5:3 @10.000) + cổ tức cổ phiếu 7%.
- NQ 10/NQ-HĐQT 20/11/2026: lấy ý kiến cổ đông bằng văn bản 14–25/12/2026, **nội dung chưa công bố**. Đây là mốc phải làm lại bản pha loãng.
- Chuyển nhượng hợp đồng tiền gửi 852,0 tỷ giữa TCH và CRV/NĐL.
- **(khôi phục)** TB 2124/TB-TTCP: CRV bị thu tạm 7,87 tỷ (không trọng yếu).
- **(khôi phục)** KL 08/KL-TTTP: NƠXH Pruksa, chưa có số liệu.

## 5. Mốc hai chiều (bổ sung rev6 §5)
- **Lên:** cổ tức tiền CRV chuyển về HHS. Khi có, HHS sẽ ra khỏi nhóm "không có dòng tiền con→mẹ", và có cơ sở để dùng đầu thấp IQR (~20%).
- **Xuống:** tầng chồng TCH→HHS (58,31%) cộng với việc không có cổ tức tiền đều nghiêng về đầu cao IQR (~39%). Nếu sau này có dữ liệu đo nhóm tầng chồng, chạy lại.
- Các mốc khác giữ rev6 §5.

## 6. Còn mở
1. **User chấp nhận hay không** dùng CK đo được (26,63%, độ tin thấp–trung bình) làm base, thay cho 0%.
2. Chuỗi CK 2019–2026 cần lịch sử tỷ lệ sở hữu theo thời điểm (BCTC năm từng holding). Hiện chưa có.
3. Nội dung phiên lấy ý kiến cổ đông 14–25/12/2026.
4. Cơ cấu HTK NC-II giữa thấp tầng và cao tầng HH1–HH4.
5. BV NĐL chưa kiểm toán.
