# Mở hard-block anomaly sang BAL/LAG — ĐO LƯỜNG, không phải đề xuất wire

> Taylor (Quant/Algo), job `Taylor_20260814_041116` Việc 4, 2026-08-14.
> **KHÔNG chạm một dòng code chọn mã production nào.** Đây là số liệu để user quyết chính sách,
> đúng như §D.3 report `portfolio_wide_badnews_protection_20260814.md` đã nói.
> Script tái lập: `mike/agents/Taylor/exp_balleg_hardblock/measure_balleg_hardblock.py`
> Dữ liệu từng lệnh: `exp_balleg_hardblock/balleg_hardblock_events.csv` (835 dòng).

---

## 0. Kết luận một câu

**Số liệu KHÔNG ủng hộ mở hard-block sang BAL/LAG.** Trên 835 lệnh mua BAL/LAG thật của backtest
R3 (2014-01→2026-05), những lệnh mà hard-block sẽ chặn lại có kết cục **TỐT HƠN** đối chứng
(+6,17% vs +4,67% trung bình; 56,0% vs 52,4% thắng) — và nhóm cờ đúng-hình-dạng-DGC/PNJ
(FLOOR2/IDIOCRASH, tức mã vừa SẬP) là nhóm tốt nhất trong tất cả: **+7,56%**. Tuy nhiên **không
khoảng tin cậy nào loại trừ 0**, nên phát biểu chặt chẽ là: *không đo được lợi ích, có dấu hiệu
ngược, N quá mỏng để kết luận mạnh theo chiều nào*.

Cái hard-block MUA thật sự làm được, đo được, và không mơ hồ: **cắt bớt đuôi trái** — tỉ lệ lệnh
lỗ ≥20% trong nhóm bị chặn là **11,2%** so với **5,4%** ở đối chứng, tức nó **đúng là gấp đôi mật
độ thảm hoạ**. Nhưng nó gánh theo cả những cú hồi mạnh sau sập, và tổng lại thì **hoà tới hơi âm**.

⚠️ **Phát hiện phụ QUAN TRỌNG HƠN cả câu hỏi gốc, chạm cả rổ CAPIT đang LIVE**:
`anomaly_gate.anomaly_excluded()` **không phân biệt lý do cờ** — nên **CEIL2 (trần 2 phiên = giá
TĂNG mạnh) cũng loại mã khỏi rổ mua**. Trong 125 ca bị chặn ở đây, **56 ca (44,8%) là CEIL2**, tức
gần một nửa số lần "bảo vệ khỏi tin xấu" thực chất là **từ chối mua một cổ phiếu vì nó vừa tăng
giá**. Đây không phải quyết định ai đó đã cân nhắc rồi chọn — nó là hệ quả phụ của việc gộp mọi
reason vào một cờ. Xem §5.

---

## 1. Cách đo

| Thành phần | Nguồn | Ghi chú |
|---|---|---|
| Lệnh mua BAL/LAG thật | `data/v23_golive_audit_2014_now_…cap50b_ideal_univpit.csv` (`record_type=TX`, sổ giao dịch của R3 đã pin 2026-08-03) | **835 lệnh / 369 mã / 2014-01-27→2026-05-25**, đã trừ `ETF_PARK` (parking, không phải chọn mã) và `CAPIT*` (đã bị chặn cứng hôm nay) |
| Cờ anomaly lịch sử | **import `anomaly_scan.compute_signals()`**, chạy trên `data/bq_cache/ticker/*.parquet` | Dùng LẠI luật production, không chép lại — chép lại là tự sinh bản thứ hai lệch dần. `hold=∅` ⇒ nhánh **tier W** (chặt hơn), đúng cho một mã còn là ỨNG VIÊN mua |
| Universe bộ quét PIT | `data/bq_cache/fa_ratings_8l.parquet`, `rating<=2`, bản gần nhất **trước** ngày mua | Hôm nay bộ quét chỉ nhìn `hold ∪ rating<=2` ⇒ mã ngoài đó **không bao giờ có cờ** |
| Kết cục | khớp `holding_id` buy↔sell trong chính sổ đó, gộp bán từng phần, trừ phí | 835/835 lệnh đã đóng vị thế |

**Chống look-ahead**: một cờ chỉ tính là "đã biết" nếu phiên alert **≤ ngày mua − 1**. Đúng chuỗi
production: `anomaly_scan` 08:20 đọc cache T-1 → `golive_recommend_v23` 19:00 cùng ngày → lệnh cho
phiên sau. TTL 30 ngày, bằng `ANOMALY_TTL_DAYS`.

---

## 2. Câu hỏi (1): hard-block sẽ chặn bao nhiêu lệnh?

| Kịch bản | Số lệnh bị chặn | Tỉ lệ |
|---|---:|---:|
| **CẬN TRÊN** — giả định bộ quét phủ MỌI ứng viên mua | **125 / 835** | **15,0%** |
| **THỰC TẾ HÔM NAY** — chỉ mã nằm trong universe quét (`rating<=2`) tại thời điểm đó | **36 / 835** | **4,3%** |

Khoảng cách 125 vs 36 là một sự thật hạ tầng đáng chú ý tự nó: **~71% số ca mà hard-block "đáng
lẽ" bắt được thì bộ quét hôm nay còn không nhìn tới**, vì ứng viên LAG/PEAD phần lớn không phải
mã `rating<=2`. Muốn hard-block BAL/LAG có tác dụng như hình dung thì phải **mở universe quét
trước**, và đó là một thay đổi riêng, tốn kém riêng, chưa ai đo.

---

## 3. Câu hỏi (2): chặn đúng hay chặn oan?

| Nhóm | n | Thắng | Lỗ ≥20% | Ret trung vị | Ret trung bình | Tổng P&L |
|---|---:|---:|---:|---:|---:|---:|
| **Đối chứng — KHÔNG bị chặn** | 710 | 52,4% | **5,4%** | +0,79% | **+4,67%** | +230,14 tỷ |
| Bị chặn — **cận trên** | 125 | 56,0% | **11,2%** | +1,78% | **+6,17%** | +26,31 tỷ |
| Bị chặn — **thực tế** (`rating<=2`) | 36 | 47,2% | **16,7%** | −0,72% | +3,07% | −5,21 tỷ |

Bootstrap 4.000 lần, chênh lệch trung bình so với đối chứng:

| Nhóm | Δ trung bình | CI95 | Đọc là |
|---|---:|---|---|
| Cận trên (n=125) | **+1,50pp** | [−2,62; +5,72] | **chưa loại trừ 0** |
| Thực tế (n=36) | −1,60pp | [−9,11; +6,30] | **chưa loại trừ 0** |
| Chỉ nhóm SẬP (n=68) | **+2,88pp** | [−2,37; +8,69] | **chưa loại trừ 0** |

⇒ Không có bằng chứng thống kê cho chiều nào. Nhưng **cả ba điểm ước lượng của nhóm "đúng hình
dạng DGC/PNJ" đều nghiêng về phía CHẶN LÀ MẤT TIỀN**, không phải phía chặn là bảo vệ.

**Vì sao ngược trực giác — và vì sao nó nhất quán với hệ đang chạy**: một mã vừa sập riêng lẻ
rồi được BAL/LAG chọn mua là **đúng định nghĩa của sleeve "mua khi sợ hãi có tính toán"**.
`DEEP_VALUE_RECOVERY` và `RE_BACKLOG_BUY` được thiết kế để làm chính việc đó. Hard-block sẽ tắt
một phần cơ chế mà hệ đang cố ý bật.

Con số **KHÔNG mơ hồ** là đuôi trái: **11,2% vs 5,4%** lệnh lỗ ≥20%. Nhóm bị cờ **thật sự** dày
thảm hoạ gấp đôi. Nhưng phần hồi phục của những cú sập khác bù lại đủ, nên tổng thì hoà.

---

## 4. Năm nào gánh kết quả?

Nhóm bị chặn (cận trên), P&L theo năm (tỷ VND): 2014 +0,74 · 2015 +1,11 · 2016 +0,30 · 2017 +1,82
· 2018 +2,69 · 2019 +5,46 · 2020 +5,29 · 2021 +7,90 · 2022 +7,50 · 2023 −0,71 · 2024 +10,97
· 2025 +1,12 · **2026 −17,89**.

**11/13 năm dương** ⇒ kết luận "chặn thì mất tiền" KHÔNG phải do một năm may mắn.

Ngược lại, con số âm **−5,21 tỷ** của nhóm "thực tế" thì **hoàn toàn** do 3 lệnh gần đây: bỏ 2026
ra, nhóm này về gần bằng 0 (−0,29 tỷ trên 35 lệnh, +3,57% trung bình). Riêng năm 2026 chỉ có
**1 lệnh** (KSF, cờ **CEIL2**, −14,3%). **Không được trích "hard-block cứu −5,21 tỷ"** — đó là
n=1 đội lốt xu hướng.

---

## 5. Phát hiện phụ — chạm rổ CAPIT đang LIVE, đề nghị xử lý riêng

`anomaly_gate.anomaly_excluded()` trả về mọi ticker có `last_alert` trong TTL, **bất kể `reasons`**.
Mà `anomaly_scan` ghi cờ cho cả **CEIL2** (trần 2 phiên) và **VOLSPIKE**, không chỉ FLOOR2/IDIOCRASH.
Chính docstring `anomaly_scan.py` gọi CEIL2 là *"đối xứng, severity thấp — watch note"* — tức là
nó chưa bao giờ được thiết kế để chặn lệnh mua.

Phân rã 125 ca bị chặn:

| Loại cờ | n | Thắng | Lỗ ≥20% | Ret trung bình |
|---|---:|---:|---:|---:|
| **SẬP** (FLOOR2/IDIOCRASH) — đúng hình dạng DGC/PNJ | 68 | 57,4% | 10,3% | **+7,56%** |
| **TĂNG TRẦN** (CEIL2) — **không phải tin xấu** | **56** | 55,4% | 12,5% | +4,77% |
| VOLSPIKE đơn thuần | 1 | 0% | 0% | −9,16% |

**44,8% số lần "bảo vệ khỏi tin xấu" thực chất là từ chối mua vì cổ phiếu vừa tăng giá.** Điều này
đang có hiệu lực THẬT trên rổ CAPIT hôm nay, không phải giả thuyết. Nó không nhất thiết sai (mua
đuổi sau 2 phiên trần là rủi ro riêng), nhưng nếu nó là ý định thì phải là một luật được nói ra,
có tên, có lý do — chứ không phải hệ quả phụ của việc gộp reason.

**Đề nghị**: tách thành job riêng — đo tác động của việc lọc `anomaly_excluded()` theo reason
(chỉ FLOOR2/IDIOCRASH) trên rổ CAPIT. Đó là thay đổi production, cần backtest + quant-skeptic.
Không tự làm trong vòng này.

---

## 6. Giới hạn — đọc trước khi trích số

1. **Đây là counterfactual NGÂY THƠ**: "bỏ lệnh bị chặn" ≠ "hệ chạy như thế". Vốn không mua mã đó
   sẽ đi đâu (mã kế trong hàng đợi? cash? parking?) — mô hình này không trả lời. Con số P&L phải
   đọc là **quy mô của cái bị đụng tới**, KHÔNG phải "CAGR sẽ đổi bấy nhiêu".
2. **Ngưỡng anomaly được tinh chỉnh trên 2024-2026** (backtest FP gốc), áp ngược về 2014 là ngoại
   suy. Số 15,0% có thể lệch theo cả hai chiều ở thời kỳ đầu mẫu.
3. **N thật = 125 (và 36) VỊ THẾ, không phải 835 dòng** — và chúng cụm theo mã/năm. Mọi CI ở trên
   đã dùng đúng n vị thế, và **không CI nào loại trừ 0**. Không có DSR/PBO ở đây vì **không có
   config nào được chọn** — đây là đo lường 1 kịch bản, không phải sweep tham số.
4. **Sổ giao dịch là của backtest R3, không phải fill thật.** Kế thừa mọi caveat của R3 (giả định
   fill 20% ADV/phiên chưa neo — xem `kb/projects/lag-adv-filter-tracking.md`).
5. **Không đo được cái user thực sự lo**: DGC/PNJ là rủi ro **pháp lý/quản trị**, mà cờ ở đây
   thuần **giá/khối lượng**. Một hard-block dựa trên tín hiệu giá không phải là cái chặn được một
   vụ khởi tố; nó chỉ chặn được *hệ quả giá* của vụ đó, sau khi giá đã phản ứng.
6. **Kênh phát hiện vẫn giữ nguyên giá trị.** Kết luận "đừng chặn cứng" KHÔNG phải "đừng theo dõi"
   — `due_diligence.py::_anomaly_note()` vẫn hiện cờ ở cả 4 choke-point cho người duyệt, và đó
   đang là thiết kế đúng: **người nhìn cờ rồi quyết**, thay vì máy loại mù.

---

## 7. Cần user quyết

1. **Mở hard-block cho BAL/LAG?** — khuyến nghị **KHÔNG**. Không đo được lợi ích, điểm ước lượng
   nghiêng ngược, và 71% ca "đáng lẽ bắt được" nằm ngoài tầm bộ quét hôm nay nên hiệu lực thật sẽ
   nhỏ hơn nhiều so với hình dung. Giữ nguyên: BAL/LAG **hiện cờ cho người duyệt**, CAPIT chặn cứng.
2. **Có mở job riêng cho phát hiện §5** (CEIL2 đang chặn mua trong rổ CAPIT) không? — khuyến nghị
   **CÓ**. Đây là hành vi LIVE hôm nay mà chưa ai chủ ý chọn.
3. Nếu vẫn muốn một lớp chặn phía mua: hướng **rẻ hơn và đúng đích hơn** là mở rộng **universe
   quét** (để cờ tồn tại cho ứng viên LAG/PEAD) rồi vẫn để **người duyệt** quyết — thay vì chặn mù.
