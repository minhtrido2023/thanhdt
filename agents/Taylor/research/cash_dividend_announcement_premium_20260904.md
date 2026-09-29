# Cash Dividend Announcement Premium — vs Deposit Rate Yield Gap

**Job**: `Taylor_20260904_092935` · **Ngày**: 2026-09-04 · **Verdict: BLOCKED trên dữ liệu — KHÔNG chạy được backtest hệ thống, KHÔNG phải NO-GO trên bằng chứng thống kê**

## Tóm tắt 1 dòng

Không thể xây `announcement_date` đáng tin từ `tav2_bq.corporate_action` — bảng này đã bị
**CẤM cho announcement study từ Sprint `corp_action_program_20260815`** vì cơ chế upsert-tại-chỗ
xoá mất ngày công bố gốc, và cơ chế vá (`corporate_action_snapshots`) mới chạy được **18 ngày**
(2026-08-17→2026-09-04), quá ngắn so với runway ~12 tháng cần thiết. Xác nhận thêm bằng chính ca
DGC 09-03 — bản ingest MỚI NHẤT của bảng nguồn (2026-09-03 15:44 UTC) **còn chưa có** dòng cổ tức
8.000đ vừa công bố, tức là ngay cả proxy tốt nhất hiện có cũng trễ hơn tin thị trường đã biết.

## Bước 0 — Prereg (viết trước khi nhìn outcome, rồi phát hiện Bước 0 tự nó bất khả thi)

- **H1**: Ngày công bố cổ tức tiền mặt, giá tăng mạnh hơn ngày bình thường (announcement premium > 0).
- **H2**: `yield_at_announcement / deposit_rate_12M` là predictor dương của `announcement_premium`.
- **H3** (optional): ngưỡng yield/rate > 1.0 → premium đặc biệt lớn.
- **Definition (dispatch)**: `announcement_day` = ngày đầu tiên `corporate_action.DIV` xuất hiện
  cho event đó trên BQ (KHÔNG phải ex-date).
- **Tiêu chí xác nhận H1**: median announcement_return > +1% với p<0.05 (Wilcoxon vs matched controls).
- **Tiêu chí xác nhận H2**: Spearman(yield_ratio, premium) > 0 với p<0.05.

Prereg này commit trước khi chạy Bước 1 — nhưng Bước 1 (data pull) lộ ra ngay định nghĩa
`announcement_day` ở trên **không thực thi được** trên bảng nguồn được chỉ định. Phần dưới đây là
bằng chứng đo thật, không phải suy đoán.

## Bằng chứng — vì sao Bước 0 bất khả thi

### 1. Đã có lệnh cấm tường minh trong data registry, dựa trên điều tra trước

`mike/kb/data_registry/price-volume/corporate_action_bq.md` Bẫy (2b) + Bẫy (5), và
`mike/agents/Taylor/research/corp_action_snapshot_pipeline_design_20260817.md` dòng 18:

> "Hệ quả đã trả giá: **Sprint 1 (`corp_action_program_20260815`) CẤM mọi announcement study** vì
> thiếu point-in-time provenance (gate CONDITIONAL PASS). Pipeline này là **tiền đề duy nhất** để
> mở lại."

Cơ chế cụ thể: `corporate_action` bị **UPSERT TẠI CHỖ** — khi 1 event chuyển trạng thái
`announced` → `executed`, dòng `announced` (mang ngày công bố Ý ĐỊNH) bị GHI ĐÈ, không giữ lại.
Đo thật 2026-08-17: batch ingest gần nhất rewrite 1.331 dòng, **89% có `public_date` cũ hơn
2026-08-01** (cũ nhất 2024-09-13) — vendor sửa dòng LỊCH SỬ mỗi lần chạy, không chỉ append. Bẫy
(5) của cùng file kết luận thẳng: **"bảng này KHÔNG có cột nào ghi thời điểm thị trường lần đầu
biết tin"** — cả 3 ứng viên cột (`public_date`, `id_created_date`, `listing_date`) đều đã bị loại
bằng đo đạc.

`id_release`/`listing_date` cũng không dùng được: `listing_date` populate 81,8% chỉ ở `ISS`
(không phải `DIV`), và ngay cả khi có thì nó là ngày CP MỚI LÊN SÀN — **hậu sự kiện**, median
+49-91 ngày SAU `exright_date`, không phải ngày công bố.

### 2. Cơ chế vá (`corporate_action_snapshots`) mới sống được 18 ngày — không đủ runway

Query trực tiếp (2026-09-04, `bq` CLI):

```
MIN(snapshot_date) = 2026-08-17
MAX(snapshot_date) = 2026-09-04
COUNT(DISTINCT snapshot_date) = 18
```

File thiết kế pipeline này (`corp_action_snapshot_pipeline_design_20260817.md` §8.5) tự ước tính
runway cần **12-18 tháng** để tích luỹ đủ N sự kiện có ngày ĐĂNG KÝ point-in-time thật (không phải
executed muộn), và mục việc còn treo #5 ghi rõ: **"Quyết định mở lại announcement study — Không
sớm hơn 2027-08"**. 18 ngày = ~4,9% của mốc ngắn nhất (12 tháng). Không đủ để xây dù chỉ một mẫu
descriptive đáng tin.

### 3. Kiểm chứng bằng chính ca động lực của dispatch — DGC 2026-09-03

Query `tav2_bq.corporate_action` cho `DGC`, sort theo `ingested_at DESC`: dòng `DIV` gần nhất vẫn
là cổ tức **3.000đ công bố 2025-12-11** (kỳ trước). Cổ tức **8.000đ (5.000+3.000 tạm ứng 2026)**
công bố 2026-09-03 — **KHÔNG xuất hiện** trong bảng nguồn dù bản ingest mới nhất có timestamp
2026-09-03 15:44:46 UTC. Đây chính là bằng chứng trực tiếp: dù dùng "ngày đầu tiên DIV xuất hiện
trên BQ" làm proxy, độ trễ vendor đủ lớn để bỏ lỡ đúng case mà user quan sát bằng mắt thường ngày
hôm sau (+8%). Dùng proxy này để đo announcement premium sẽ **hệ thống đo SAI ngày** (muộn hơn
ngày thị trường thực sự phản ứng), làm hỏng chính hypothesis đang muốn test — không phải noise
ngẫu nhiên mà là lệch có hướng (chỉ bắt được case nào vendor xử lý nhanh).

### 4. Kiểm tra thêm — trạng thái `announced` (127 dòng hiện tại) có cứu được không?

`event_status='announced'` (127/17.131 dòng DIV, tách khỏi `executed`) có `public_date` gần ngày
hiện tại hơn nhiều (vd BIC `public_date=2026-08-28`, `exright_date=2026-10-07` — đúng lead-time
~1,5 tháng dispatch mô tả). Về lý thuyết đây là ứng viên tốt nhất cho announcement date THẬT —
nhưng 2 vấn đề chặn dùng ngay: (a) **chưa verify độ trễ ingest** của chính trạng thái `announced`
này (case DGC ở mục 3 cho thấy vendor có thể trễ nhiều ngày ngay cả để tạo dòng `announced`); (b)
theo đúng Bẫy (2b), MỘT KHI dòng này chuyển `executed`, `public_date` gốc bị ghi đè — nên **không
tích luỹ được lịch sử** trừ khi đọc qua `corporate_action_snapshots` (mới có 18 ngày, mục 2).
Kết luận: `announced`-status là hướng ĐÚNG cho tương lai (khi snapshot đủ dài), không phải lối tắt
cho backtest hôm nay.

## Vì sao KHÔNG tự ý đổi definition rồi chạy bừa (vd dùng `exright_date` làm proxy)

Dispatch đã tự cảnh báo đúng rủi ro này: "Nếu announcement_date không có trong BQ... dùng ex_date
làm proxy sẽ sai signal timing" — vì announcement thường đi trước ex_date 2-4 tuần (đo thật ở đây:
median RIGHTS/STOCK_DIVIDEND/BONUS ex_date→listing_date đã là +49-91 ngày, và announcement→
exright_date theo `ISS` case FPT là ~7 tuần). Đo "return quanh exright_date" là đo một câu hỏi
KHÁC (giá điều chỉnh cơ học ngày chốt quyền, đã có literature ex-date-drop riêng, không phải
premium theo tin công bố) — trộn 2 khái niệm sẽ cho ra một con số trông giống câu trả lời nhưng
sai câu hỏi, đúng loại lỗi luật §6/§9 coding_guidelines cấm.

## Kết luận & khuyến nghị

**KHÔNG GO / KHÔNG NO-GO — BLOCKED trên độ sẵn sàng dữ liệu.** Không có bằng chứng nào (thống kê
hay ngược lại) được sinh ra ở đây vì Bước 0 không thực thi được với nguồn dữ liệu được chỉ định
đủ point-in-time integrity. Đây KHÔNG phải kết luận "hypothesis sai" — chỉ là "chưa đo được".

**3 hướng đi tiếp, không hướng nào chạy hôm nay:**

1. **Chờ runway** — `corp_action_snapshot_pipeline_design_20260817.md` đã ghi rõ mốc **không sớm
   hơn 2027-08** để mở lại announcement study nói chung; sprint này thuộc đúng nhóm bị cấm đó,
   không phải trường hợp ngoại lệ.
2. **Case study minh hoạ nhỏ, KHÔNG hệ thống** — dùng WebSearch xác nhận ngày công bố thật cho
   5-10 case cụ thể (bao gồm DGC) thay vì BQ, đo return quanh ngày đó thủ công. Cho định hướng
   định tính, **không đủ N để kiểm định thống kê**, phải khai rõ là illustrative khi báo cáo.
3. **Theo dõi `announced`-status sống** — từ hôm nay, mỗi lần snapshot chạy, ghi lại các dòng
   DIV mới xuất hiện ở trạng thái `announced` (chưa `executed`) — đây chính là hạt giống cho một
   PIT announcement dataset thật, nhưng cần tích luỹ hàng tháng trước khi có N dùng được.

**Không có claim GO/NO-GO nào về H1/H2/H3 — chưa đo được, không phải đo rồi bác bỏ.**

## Self-check

- N_eff = **0** (không có event nào được đo qua pipeline hệ thống — đúng như kết luận ở trên).
- Không có model dự đoán nào được train → không áp dụng 0 VND self-check.
- Case DGC được dùng làm bằng chứng PHỦ ĐỊNH (chứng minh proxy không hoạt động), không phải làm
  training/illustrative case cho hypothesis — đúng lưu ý "KHÔNG phải training case" trong dispatch.
