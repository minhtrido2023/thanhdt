---
kind: bigquery-table
status: CANONICAL
source: tav2_bq.ticker_financial
group: fundamentals
writer: Ingest theo lịch công bố BCTC (MAX_FIN_LAG=90 trong bq_freshness_check.sh)
---

# tav2_bq.ticker_financial

**Status: CANONICAL**

## Là gì
Báo cáo tài chính quý.

## Ai ghi / cadence
Ingest theo lịch công bố BCTC (~60-85 ngày lệch cho phép, `MAX_FIN_LAG=90` trong
`bq_freshness_check.sh`).

## Bẫy
`OShares` ở đây **vừa trễ quanh ex-date, vừa bị RESTATE về sau** (2.667 dòng/576 mã mang số của
một AIS có hiệu lực SAU đó, tới 2.693 ngày) ⇒ đọc thẳng là look-ahead. Cột này có file riêng,
status **TRAP**: [`ticker_financial_oshares.md`](ticker_financial_oshares.md). Xem thêm
[`../price-volume/shares_outstanding_live.md`](../price-volume/shares_outstanding_live.md).

**`IntCov_P0` (dấu ÂM) KHÔNG đáng tin làm tín hiệu distress một mình — mẫu số là RÒNG, không phải
gộp.** Không có ETL nào trong repo tính lại cột này (vendor nguồn ngoài, khả năng vnstock), và
`ticker_financial` KHÔNG có cột chi phí/doanh thu tài chính riêng để tái lập công thức chính xác.
Bằng chứng (job `Taylor_20260904_075525`, `agents/Taylor/research/adaptive_exclusion_v3_20260904.md`
§Việc 1): trong tập (ticker,quý) vừa đòn bẩy cao (`Debt_Eq_P0>3,5`) vừa `IntCov_P0<0` (n=2.147,
2010→2026), **chỉ 8,1% là net-cash-rich** (`Cash_P0+LtInvest_P0 > StDebt_P0+LtDebt_P0`) — phần
lớn (91,9%) vẫn là NET DEBTOR theo bảng cân đối, nhưng trong nhóm net-debtor đó **82,9% vẫn có
EBIT ước tính dương** (`EBITM_P0×Revenue_P0`) **và 68,1% có cả EBIT lẫn NP_P0 cùng dương** — về
mặt toán học, tử số dương + tỷ lệ âm ⇒ mẫu số PHẢI âm, xác nhận mẫu số là một khoản RÒNG có thể đảo
dấu (không phải "lãi vay gộp, luôn dương" như đọc tên cột theo nghĩa đen). **Nhưng** khoản ròng đó
KHÔNG giải thích được bằng proxy bảng cân đối đơn giản `Cash_P0+LtInvest_P0` (hồi quy toàn universe
R²=0,25, tỷ lệ khớp dấu với `NetDebt` chỉ 53% — gần bằng tung đồng xu) — nhiều khả năng khoản
doanh thu tài chính thật đến từ dòng chảy (lãi JV/công ty liên kết, lãi chênh lệch tỷ giá, lãi bán
khoản đầu tư một lần) chứ không phải tồn kho tiền/đầu tư cuối kỳ trên bảng cân đối.

**Quy tắc tiền xử lý dấu bắt buộc khi dùng `IntCov_P0` trong bất kỳ gate/rule mới nào:**
- `IntCov_P0 < 0` → KHÔNG tự suy ra distress. Chỉ coi là cảnh báo khi ĐI KÈM `EBITDA_P0 < 0` HOẶC
  `NP_P0 < 0` (operating/net level xấu thật) — một mình dấu âm của `IntCov_P0` không đủ.
- `0 <= IntCov_P0 < 1,5` (dương, yếu) → vẫn có false-positive đáng kể (61,4% trong tập kiểm
  n=1.290 vẫn có `NP_P0>0`) — nên đối chiếu thêm `EBITDA_P0`/`NP_P0`, đừng dùng ngưỡng này một mình.
- `|IntCov_P0|` gần 0 (< ~0,05) → vùng chia gần-0 bất ổn định (implied denominator nổ), coi là
  low-confidence/bỏ qua, đừng lọc trực tiếp trên khoảng này.
- Gate production hiện tại (custom30V dynamic-exclusion nghiên cứu, chưa wire) đã áp đúng nguyên
  tắc này: dùng `EBITDA_P0<0` (operating-level) thay `IntCov_P0<1,5` cho điều kiện "đang lỗ thật",
  giảm flag rate từ 5,97%→1,62% trên đúng tập `Debt_Eq_P0>3,5`.
- Muốn công thức chính xác: hỏi thẳng nguồn dữ liệu (bq_admin/ai quản lý ETL `ticker_financial`),
  đừng tiếp tục suy diễn từ tương quan — độ tin cậy hiện tại là CAO nhưng KHÔNG xác nhận trực tiếp.

**CẬP NHẬT 2026-09-05 — trả lời từ bq_admin, xác nhận trực tiếp, ĐÍNH CHÍNH giả thuyết "mẫu số
ròng" ở trên (chỉ đúng cho một nhánh, không phải bản chất chung của cột):**
`IntCov_P0` = **pass-through trực tiếp giá trị VCI trả về trong báo cáo ratio của VCI** (công thức
nội bộ VCI, KHÔNG công khai, không suy ngược được). **CHỈ khi VCI trả `null`** thì mới rơi vào
nhánh tự tính, công thức đã xác nhận: `profit_before_tax / abs(interest_expense) + 1`.

**Hệ quả — vì sao KHÔNG tự tính lại được để thay thế nguồn BQ hiện tại, kể cả khi muốn:**
1. **Chứng minh được bằng toán học rằng ca SBA đến từ nhánh VCI-opaque, không phải nhánh fallback**
   đã biết công thức: `PBT/|IntExp| + 1` có mẫu số LUÔN dương tuyệt đối ⇒ nếu PBT dương thì kết
   quả LUÔN ≥ 1, không bao giờ âm. SBA có PBT dương và TĂNG DẦN suốt 2013→2024 trong khi IntCov
   thực tế càng ÂM SÂU hơn (−1,47→−24,26) — không thể sinh ra từ công thức này. Vậy giá trị SBA
   chắc chắn đến từ số VCI tự trả (nhánh 1), phương pháp tính của VCI KHÔNG biết được, không phải
   thiếu dữ liệu để tính lại mà là KHÔNG BIẾT công thức để tính lại.
2. **Ngay cả nhánh fallback ĐÃ BIẾT công thức cũng không tái lập được từ BQ**: đã kiểm schema
   `ticker_financial` trực tiếp (`INFORMATION_SCHEMA.COLUMNS`) — KHÔNG có cột `interest_expense`
   hay `profit_before_tax`. Chỉ có `EBITM_P0` (biên EBIT, một cột KHÁC, đã dùng để ước tính EBIT
   ở mục audit trên) — không đủ nguyên liệu để tự tính kể cả công thức đơn giản đã biết.
3. **Kết luận thực hành**: `IntCov_P0` là con số HỘP ĐEN của vendor cho đa số dòng (khi VCI có trả
   giá trị) — không phải lỗi pipeline, không phải điều tự tính lại được từ dữ liệu sẵn có trong
   `tav2_bq`. Muốn dùng đúng công thức fallback cũng phải kéo báo cáo tài chính thô (interest
   expense, profit before tax) từ vnstock/VCI trực tiếp, NGOÀI phạm vi `ticker_financial`.
   **Quy tắc tiền xử lý dấu ở trên VẪN ĐÚNG và VẪN LÀ CÁCH DÙNG AN TOÀN** (dùng `EBITDA_P0`/`NP_P0`
   đối chiếu thay vì tin `IntCov_P0` một mình) — phát hiện này xác nhận lý do gốc rễ, không đổi
   khuyến nghị.
