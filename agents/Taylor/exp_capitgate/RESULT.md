# Nới quality gate của CAPIT basket — **NO-GO 4 biến thể / INCONCLUSIVE 2** (job Taylor_20260720_160852)

Tiếp nối 2 job DCF×CAPIT NO-GO. Giả thuyết: ràng buộc thật không phải metric xếp hạng mà là
**pool quá mỏng** (median 7 tên; 9/14 event pool ≤ K). Câu hỏi: nới gate có mở pool an toàn không?

Pre-register **trước khi chạy**: `PREREG.md` — 6 biến thể gate neo theo percentile thực tế của
universe, horizon quyết định h=60 (đúng holding period CAPIT), 4 tiêu chí GO định trước **nặng về
đuôi trái** (vì CAPIT hold 60 phiên **stop-exempt** → value-trap là rủi ro chính, không phải mean).

## 1. Kết quả chính — đối chiếu 4 tiêu chí

| Gk | nới gì | (i) pool>K | (ii) đuôi trái | (iii) t>−2 | (iv) LOO/IS-OOS | **VERDICT** |
|---|---|---|---|---|---|---|
| G1 | ROE 0,12→0,09 | 7/14 (+2) ❌ | ✓ | ✓ | ❌ | **NO-GO** |
| G2 | ROIC 0,10→0,08 | 5/14 (+0) ❌ | ❌ | ✓ | ✓ | **NO-GO** |
| G3 | FSCORE 6→5 | 9/14 (+4) ✓ | ✓ | ✓ (−0,50) | ❌ IS/OOS đảo dấu | **INCONCLUSIVE** |
| G4 | ADV 2B→1B | 6/14 (+1) ❌ | ✓ | ✓ | ❌ | **NO-GO** |
| G5 | COMBO-mild (3 trục ×1 nấc) | 9/14 (+4) ✓ | ✓ | ✓ (−0,03) | ❌ IS/OOS đảo dấu | **INCONCLUSIVE** |
| G6 | COMBO-p50 (biên trên) | 9/14 (+4) ✓ | ✓ | ✓ (+0,34) | ❌ LOO sign-flip | **NO-GO** (xem §4) |

Baseline G0 = 5/14 event có pool > K.

## 2. PHÁT HIỆN QUAN TRỌNG NHẤT — **giả thuyết value-trap KHÔNG được xác nhận**
Đây là câu hỏi cốt lõi user đặt ra (#2 trong dispatch). Đo trên panel 30.476 name-date /
165 ngày quan sát, suy diễn trên 41 ngày **quarterly non-overlapping**, return demeaned trong ngày,
giới hạn pb_z<0 (đúng điều kiện production mua):

| Gk | P(ret60 ≤ −20%) MARGINAL / CORE | 5th-pct M/C | mean worst-decile M/C |
|---|---|---|---|
| G3 | **4,3% / 3,4%** | −17,7 / −18,8 | −20,0 / −20,7 |
| G5 | **4,1% / 4,5%** | −18,8 / −19,5 | −20,4 / −20,5 |
| G6 | **6,0% / 5,1%** | −20,9 / −19,5 | −21,0 / −20,9 |

Các tên **lọt vào nhờ nới gate KHÔNG có đuôi trái xấu hơn** tên đã qua gate cũ — chênh ≤1pp ở
P(≤−20%), 5th-pct thậm chí NHỈNH HƠN ở G3/G5. Nỗi lo "nới gate = rước value-trap giữ chết 60 phiên"
**không có trong dữ liệu 2014-2026**. Đây là kết quả âm có giá trị: nó loại bỏ đúng lý do khiến gate
được giữ chặt.

⚠️ Giới hạn phải nói rõ: mẫu chỉ bao trùm các chế độ đã xảy ra 2014-2026. Kết luận "an toàn đuôi
trái" là **có điều kiện trên lịch sử này**, không phải bảo đảm cấu trúc. Với công cụ stop-exempt,
đây là loại kết luận nên coi là "chưa thấy bằng chứng gây hại", không phải "đã chứng minh vô hại".

## 3. Nhưng nới gate CŨNG KHÔNG giúp gì — và hơi hại ở portfolio level
Tên mới không tệ hơn, nhưng cũng **không tốt hơn**: hiệu demeaned MARGINAL−CORE gần 0 ở mọi biến
thể (G3 −1,06pp t=−0,50 · G5 −0,05pp t=−0,03 · G6 +0,60pp t=+0,34), bootstrap khối-năm cắt qua 0
ở cả 6 (P(>0) từ 0,24 đến 0,74).

Panel C (14 event, K=5, rank pb_z — **N=14 KHÔNG đủ power**, chỉ định hướng):

| h | base | G1 | G2 | G3 | G4 | G5 | G6 |
|---|---|---|---|---|---|---|---|
| 60 | +13,02pp | −1,44 | −0,61 | −1,04 | −0,51 | −0,94 | **−4,02** (t=−1,86) |
| 250 | +20,12pp | −0,54 | +0,38 | −2,58 | −0,83 | −2,54 | **−10,11** |

**6/6 biến thể âm ở h=60**, và biến thể nới mạnh nhất (G6) tệ nhất ở CẢ hai horizon — dose-response
đúng chiều "nới càng nhiều càng đắt". Lưu ý trung thực: 6 biến thể **không phải 6 mẫu độc lập**
(cùng 14 event, rổ chồng lấn nhiều), nên **không** được đọc "6/6 âm" như phép thử dấu p=0,016.

## 4. Vì sao G6 xuống NO-GO còn G3/G5 chỉ INCONCLUSIVE
G6 đạt (i)(ii)(iii) theo đúng chữ nghĩa nhưng: LOO sign-flip, **và** Panel C xấu rõ ở cả 2 horizon
(−4,02 / −10,11pp) — kết hợp lại đủ để kết luận nới tới trung vị là **đắt**, không chỉ vô ích.
G3/G5 chỉ trượt (iv) và trượt theo kiểu dao động quanh 0.

**Tự phê bình về tiêu chí (iv)**: (iv) đòi IS/OOS cùng dấu — đó là công cụ đúng cho một tuyên bố
*có edge*, nhưng job này tuyên bố *non-inferiority* (tên mới không tệ hơn). Một hiệu số dao động
quanh 0 thì đảo dấu IS/OOS là chuyện đương nhiên, không phải bằng chứng bất ổn. Số thật: G3 IS
−6,73 (t=−1,43, chỉ **8 ngày**) / OOS +1,10 (t=+0,50, 21 ngày) — **cả hai đều không có ý nghĩa**.
Tôi **giữ nguyên phán quyết theo tiêu chí đã pre-register** (INCONCLUSIVE, không nâng lên GO) và
ghi nhận khiếm khuyết thiết kế này ra đây thay vì diễn giải lại sau khi thấy số.

## 5. Khác biệt thật so với 2 job DCF: **đòn bẩy này RỘNG, không hiếm**
Job DCF bị chặn bởi structural bound (chỉ chạm 5/14 event × 1-2 tên). Nới gate thì khác hẳn —
số tên rổ thực sự đổi so với baseline:

| Gk | event có ≥1 tên đổi | tổng số tên hoán đổi / 14 event |
|---|---|---|
| G3 | **13/14** | 22 |
| G5 | **14/14** | 35 |
| G6 | **14/14** | 45 |

Nên đúng như dispatch dự đoán: nới gate ảnh hưởng **mọi lần CAPIT fire tương lai**, không phải
1,2 lần/năm hiếm hoi. Vấn đề **không phải** thiếu đòn bẩy — mà là đòn bẩy này đo được và **kết quả
đo là trung tính-đến-hơi-âm**. Đây là lý do NO-GO khác chất so với job trước.

## 6. DSR — **không báo, có chủ ý**
Điều kiện tiên quyết pre-register (đạt cả (i)-(iv)) **không biến thể nào đạt**. Quan trọng hơn:
không biến thể nào có tuyên bố *edge dương* để mà deflate — t tốt nhất là +0,34. DSR trên một giả
thuyết non-inferiority là con số vô nghĩa; báo ra sẽ gây hiểu nhầm đã qua chuẩn multiple-testing.
Không báo (nhất quán với 2 job trước).

## 7. KẾT LUẬN & khuyến nghị
- **Không wire gì.** Giữ nguyên gate production (ROE_Min5Y≥0,12 ∧ ROIC5Y≥0,10 ∧ FSCORE≥6 ∧ ADV≥2B).
- **Không đề xuất paper-first** cho G3/G5, dù chúng an toàn về đuôi trái. Lý do: paper chỉ có ý
  nghĩa khi có giả thuyết dương để xác nhận — ở đây hiệu ứng đo được là ~0 ở name-level và hơi âm ở
  portfolio-level. CAPIT fire ~1,2 lần/năm nên paper 12 tháng tích được ~1 event: không đủ để lật
  kết luận nào. Chờ đợi không tạo ra thông tin.
- **Điều đáng giữ lại cho tương lai**: nếu sau này cần mở pool vì lý do **capacity/sizing** (ví dụ
  rổ neo vào tên thanh khoản mỏng như NCT sau khi loại PNJ — xem `context_pack.md` mục CAPIT), thì
  **G3 (FSCORE 6→5) là lựa chọn rẻ nhất**: +4 event có lựa chọn thật, 13/14 event đổi rổ, đuôi trái
  không xấu đi, chi phí đo được −1,04pp/h60 (t=−0,82, không có ý nghĩa). Đó là quyết định
  *capacity*, phải trả giá bằng return kỳ vọng gần-bằng-0-đến-hơi-âm — **không phải** một cải thiện
  alpha, và cần user quyết định rõ ràng theo khung đó.
- **Gợi ý hướng tiếp**: cả 3 job liên tiếp đều cho thấy trong pool đã lọc chất lượng, **cả pb_z lẫn
  DCF lẫn mức chặt của gate đều gần như không phân biệt được tên tốt/xấu ở h=60**. Nếu còn muốn cải
  thiện CAPIT, nên nghi ngờ khâu *selection* nói chung và chuyển sang trục khác: sizing/timing
  (số slot K, phân bổ theo độ sâu), hoặc cơ chế thoát (điểm yếu cấu trúc thật đã biết:
  stop-exempt 60 phiên). Đề nghị đóng hẳn nhánh "cải thiện CAPIT bằng selection".

## Provenance / audit
- Point-in-time: đọc `ticker_prune` tại đúng ngày quan sát (cột tài chính đã join theo Release_Date)
  → không look-ahead. Forward return từ adjusted Close; quan sát bị cắt cụt ở cuối panel bị loại
  (ngưỡng 0,8·h) thay vì bias.
- Nguồn: `data/bq_cache/ticker_prune/*.parquet` (chunked — đã tra `kb/data_registry.md`, tránh bẫy
  monolith đóng băng 06-26).
- threads=1; stable-sort tie-break `(pbz, ticker)`; bootstrap seed cố định 12345.
- **Không có self-check 0 VND**: đây là selection/forward-return study, không phải NAV sim — không có
  ledger tiền để đối soát. Nói rõ thay vì claim một gate không chạy.
- Scripts: `build_panel.py`, `analyze.py`; data: `panel.csv` (30.476 dòng).
- Production `capit_basket()` (`pt_v23_audit_2014.py` dòng ~1044) **KHÔNG bị sửa**; không chạm
  plan/executor (R&D thuần tuý).
