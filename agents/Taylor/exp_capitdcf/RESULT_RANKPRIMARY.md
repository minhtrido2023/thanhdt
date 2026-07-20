# DCF MoS làm RANK CHÍNH cho CAPIT basket — **NO-GO** (job Taylor_20260720_155015)

**Câu hỏi (user 2026-07-20):** thay pb_z bằng DCF margin-of-safety làm metric xếp hạng **cốt lõi**
chọn rổ CAPIT (khác job trước: lần trước DCF chỉ là filter/tiebreaker phụ).

Thiết kế **pre-register trước khi chạy**: `PREREG.md` (N_trials=3 trục rank; horizon chính h=60;
4 tiêu chí GO định trước). Kết quả dưới đây đọc thẳng vào 4 tiêu chí đó.

## 1. Giải quyết vấn đề POWER — mở rộng mẫu 8,4× so với job trước
Job trước bí ở N=14 fire event. Lần này test name-level trên **toàn bộ universe đạt quality gate**
(ROE_Min5Y≥12%, ROIC5Y≥10%, FSCORE≥6, ADV≥2B) tại **mọi đầu tháng 2014-2026**, KHÔNG giới hạn ở
ngày fire — 2 trục thi đấu trên cùng tập tên.

- Panel: **1.176 name-date · 146 ngày quan sát** (job trước: 141 holdings / 13 event).
- Chống N-inflation: ngày quan sát chính lấy **quarterly non-overlapping** (cách nhau ≥ h=60 phiên)
  → 50 ngày độc lập. Bản monthly (chồng lấn) chỉ dùng làm robustness, và suy diễn qua
  **cluster bootstrap theo khối NĂM** (13 block), không dùng t-stat chồng lấn.

## 2. Kết quả PANEL A — test chính (h=60, quarterly non-overlapping, 41 ngày có IC)
| trục | IC | t | hit>0 |
|---|---|---|---|
| **DCF MoS** | +0,047 | **0,72** | 0,56 |
| pb_z (baseline) | −0,008 | −0,12 | 0,46 |
| COMBO 50/50 | −0,013 | −0,18 | 0,51 |

**Paired DCF−PBZ: +0,055, t=+0,76** (P(diff>0 theo ngày) = 0,51 — đúng bằng tung đồng xu).

### Đối chiếu 4 tiêu chí GO (định trước, không sửa sau khi thấy số)
| # | Tiêu chí | Ngưỡng | Thực tế | |
|---|---|---|---|---|
| (i) | IC(DCF) > 0, t ≥ 2,0 | t≥2,0 | t=**0,72** | ❌ TRƯỢT |
| (ii) | paired DCF−PBZ, t ≥ 2,0 | t≥2,0 | t=**0,76** | ❌ TRƯỢT |
| (iii) | LOO theo năm đều dương | mọi năm >0 | **bỏ 2020 → −0,024** (âm) | ❌ TRƯỢT |
| (iv) | IS/OOS cùng dấu | cùng dấu | IS **−0,066** / OOS **+0,141** | ❌ TRƯỢT |

**Trượt cả 4.** Theo luật pre-register: (i) hoặc (ii) trượt ⇒ **NO-GO**.

### Điểm quan trọng nhất: lại vẫn là 2020
LOO theo năm cho thấy **bỏ đúng 1 năm 2020 là hiệu số đảo âm** (+0,055 → −0,024); 12 năm còn lại
bỏ năm nào cũng gần như không đổi. Đây **cùng một failure mode** với job trước (toàn bộ edge nằm ở
event COVID 2020-03-12, swap SAB→CVT). Mở rộng mẫu 8,4× **không tạo ra bằng chứng mới** — chỉ cho
thấy rõ hơn rằng cái "edge" ban đầu (IC +0,187, t=1,40) là **một cú sốc định giá 2020 duy nhất**,
không phải pattern lặp lại. Dấu IS âm / OOS dương củng cố: không ổn định theo thời gian.

### Robustness (đều cùng hướng, không cứu được kết luận)
| bản | paired DCF−PBZ | ghi chú |
|---|---|---|
| h=250, annual non-overlap (11 ngày) | +0,042, t=+0,26 | ns |
| h=60, monthly chồng lấn (123 ngày) | +0,078, t=+1,66 | t **thổi phồng do chồng lấn** — xem bootstrap |
| year-block cluster bootstrap | +0,078, **CI95 [−0,081, +0,233]**, P(>0)=0,82 | **cắt qua 0** |
| N/A bị loại khỏi phép đo (sensitivity) | +0,125, t=+1,50 | vẫn ns |

## 3. Quan sát phụ đáng lưu (KHÔNG phải kết luận test)
Trên panel sạch, **pb_z IC = −0,008 (t=−0,12) ≈ đúng bằng 0**. Tức trong cái pool đã lọc chất
lượng này, pb_z gần như **không có giá trị chọn tên** — nó hoạt động như một *bộ lọc rẻ*, không
phải một *thước xếp hạng*. (Trên bản monthly chồng lấn pb_z ra −0,087 t=−2,32, nhưng t đó bị
chồng lấn thổi lên — **không** đọc là "pb_z có hại có ý nghĩa".) Hàm ý: đừng kỳ vọng đổi metric
rank cứu được gì, kể cả metric khác DCF.

## 4. STRUCTURAL BOUND — trần tác động, độc lập với mọi thống kê
Đây là phát hiện bền nhất của job này. Universe đạt quality gate rất mỏng: **median 7 tên/phiên**
(3.127 phiên). Tại 14 washout event, rổ production sau cascade pb_z chỉ có **3-7 tên**, mà K=5:

| | |
|---|---|
| event mà metric rank **đổi được bất cứ thứ gì** | **5/14** |
| 9/14 event còn lại | pool ≤ K ⇒ **lấy trọn pool bất kể metric nào** |
| tối đa số tên hoán đổi khi có chọn | **1-2 tên** |

➡️ Ngay cả khi DCF là metric hoàn hảo, nó chỉ chạm được 5/14 event và đổi tối đa 1-2 tên. **Trần
lợi ích quá thấp để biện minh cho việc thay một trục production đã hiểu rõ.** Đây là lý do NO-GO
độc lập với việc thống kê mạnh hay yếu.

## 5. PANEL B — portfolio-level 14 event (tham khảo định hướng, KHÔNG đủ power)
Nêu rõ theo yêu cầu: N=14 **không đủ power**, không dùng làm căn cứ quyết định.

| horizon | dcf_pool − base | dcf_full − base |
|---|---|---|
| h=60 | −0,77pp (t=−1,69) | −0,93pp (t=−0,65) |
| h=120 | −0,50pp (t=−1,25) | −0,56pp (t=−0,26) |
| h=250 | +3,23pp (t=+1,13) | +2,93pp (t=+0,88) |

**Dấu đảo theo horizon** (âm ở 60/120, dương ở 250) = đặc trưng nhiễu. Và LOO: **bỏ 2020-03-12**
→ h250 sụp **+3,23pp → +0,39pp** (dcf_pool) và **+2,93pp → +0,07pp** (dcf_full). Y hệt job trước.

## 6. DSR — **không báo, có chủ ý**
Điều kiện tiên quyết đã pre-register (đạt (i)+(ii)+(iii)) **trượt cả ba**, và edge lại sụp về ~0
khi bỏ 2020. DSR trên một chuỗi mà toàn bộ edge nằm ở 1 năm là **con số trang trí** — báo ra sẽ
gây hiểu nhầm là đã qua chuẩn multiple-testing. Không báo, đúng như lần trước.

## 7. KẾT LUẬN: **NO-GO** — giữ nguyên pb_z làm rank chính
- Trượt **cả 4** tiêu chí GO đã định trước; hiệu paired t=0,76 (cần ≥2,0).
- Edge biến mất khi bỏ 1 năm (2020) — reshuffle-luck, đúng mẫu mà chuẩn 2026-07-05 yêu cầu bác.
- Structural bound: trần tác động chỉ 5/14 event × 1-2 tên ⇒ dù có edge cũng không đáng thay trục.
- **Không đề xuất paper-first**: CAPIT fire ~1,2 lần/năm → paper 6-12 tháng tích được 0-1 event.
  Không có độ dài paper nào tạo ra mẫu để kết luận. Vấn đề là mẫu, không phải thời gian chờ.

### Hướng này nên ĐÓNG
Đã test DCF cho CAPIT ở **cả hai vai** — phụ (filter/tiebreaker, job `Taylor_20260720_153114`) và
chính (rank cốt lõi, job này) — **NO-GO cả hai**, cùng một nguyên nhân gốc: edge chỉ tồn tại ở
event COVID 2020. Đề xuất đóng hướng "DCF × CAPIT selection", không mở biến thể thứ ba.

Nếu muốn cải thiện CAPIT thật, ràng buộc thực sự **không phải metric xếp hạng** mà là **pool quá
mỏng** (median 7 tên; 9/14 event không có gì để chọn). Đòn bẩy nằm ở việc nới/định nghĩa lại
quality gate để có pool đủ rộng cho *bất kỳ* metric nào phát huy — đó là câu hỏi khác, cần user
quyết có mở không.

## Provenance / audit
- Point-in-time: `dcf_valuation.fair_value()` chỉ đọc `ticker_financial.time <= asof` (= Release_Date)
  → không look-ahead. Forward return từ adjusted Close, cắt bỏ quan sát bị truncate ở cuối panel.
- Nguồn: `data/bq_cache/ticker_prune/*.parquet` (chunked — đã tra `kb/data_registry.md`, tránh bẫy
  monolith đóng băng 06-26), `dcf_valuation.py`.
- threads=1; stable-sort tie-break `(metric, ticker)` theo chuẩn determinism 2026-07-13.
- **Không có self-check 0 VND**: đây là selection-study rank/forward-return, không phải NAV sim —
  không có ledger tiền để đối soát. Nói rõ thay vì claim một gate không chạy.
- Scripts: `build_panel.py`, `panelA_ic.py`, `panelB_events.py`; data: `panelA.csv`, `panelB_events.csv`.
- Production `capit_basket()` **KHÔNG bị sửa**; không chạm plan/executor (R&D thuần tuý).
