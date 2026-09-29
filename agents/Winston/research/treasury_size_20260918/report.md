# Tìm size cho sự kiện treasury_news thiếu `shares_delta` (job Winston_20260918_052425)

READ-ONLY. Không ghi BigQuery, không tạo `tav2_mike.treasury_share_events`.
Tái lập: `$DNA_PYEXE mike/agents/Winston/research/treasury_size_20260918/final3.py` từ `WorkingClaude/`.

## Kết luận một dòng
Trong 446 sự kiện thiếu size, **36 xác định được** (33 suy từ OShares + 3 thu hồi miễn phí),
**410 thật sự KHÔNG có dữ liệu**. Hai trong ba nguồn dispatch đề xuất là **ngõ cụt cấu trúc**,
không phải "chưa thử kỹ".

## 0 — Ba tiền đề trong dispatch cần sửa trước khi đọc số
1. **446 chứ không phải 449.** Dedup `(ticker, public_date, action_type)` lấy `MAX(shares_delta)`:
   131 sized / 446 unsized (Taylor: 128/449). Chênh đúng 3 sự kiện có **cả dòng có size lẫn dòng NULL**
   — CTD 2018-02-06 (−448.500), HVG 2020-01-13 (−5.000.000), KHW 2018-02-22 (−24.000). Đây là size
   **thu hồi miễn phí**, không cần suy luận gì: chỉ là hệ quả của cách gộp trùng.
2. **`source_news_id` / `first_disclosure_datetime` KHÔNG nằm trên `treasury_news`** — chúng là cột của
   `tav2_bq.corporate_action`. `treasury_news` có `news_id`, `public_datetime`, `first_ingested_at`.
3. **Quy ước dấu nhất quán hơn Taylor mô tả**: `shares_delta` là Δ **lượng CP quỹ nắm giữ**
   — buy_done 78 dương / 0 âm, sell_done 0 dương / 50 âm. ⇒ Δ **lưu hành** = **−shares_delta**, một
   phép lật dấu duy nhất cho cả hai chiều. (3 dòng có `shares_delta = 0`: đăng ký nhưng không khớp gì.)

## 1 — Nguồn 2 (parse text) và nguồn 3 (link chéo): CHẾT CẤU TRÚC, yield = 0

| Cột | Non-NULL / 2.377 dòng |
|---|---|
| `short_content` | **0** |
| `source` | **0** |
| `source_link` | **0** |

Chỉ còn `title`. Và parser hiện tại **đã vét cạn `title`**, đo được:

| action_type | sized | sized có số lớn trong title | **unsized có số lớn trong title** |
|---|---|---|---|
| buy_done | 80 | 66 | **1** |
| sell_done | 51 | 46 | **1** |

Hai ca "unsized có số lớn" đó khi đọc ra là **số hiệu văn bản**, không phải lượng CP:
`KBC121020: Báo cáo kết quả giao dịch bán cổ phiếu quỹ` và
`GLT: ...số 01.2024-BC ngày 16/10/2024`. Trong 446 sự kiện, chỉ 26 có BẤT KỲ chữ số nào trong title;
các số đó là tiền (`thu về 61 tỷ đồng`), phần trăm (`đã bán 88% lượng đăng ký`) hoặc số đợt
(`lần 2 năm 2019`) — **không ca nào cho ra số lượng cổ phiếu**. Title của nhóm thiếu size gần như
đều là tiêu đề công bố thông tin thuần: *"X: Báo cáo kết quả giao dịch mua lại cổ phiếu quỹ"*.

**Nguồn 3**: join `treasury_news.news_id` → `corporate_action.source_news_id` khớp **2/585 dòng**,
và **cả 2 đều không mang `shares_delta` lẫn `shares_total_after`**. Yield = 0.

## 2 — Nguồn 1 (lệch OShares): cách duy nhất còn lại, và nó hẹp

Thuật toán: với mỗi sự kiện lấy 2 dòng `ticker_financial` bao quanh `public_date`,
Δ = OShares(sau) − OShares(trước), đối chiếu dấu kỳ vọng (buy_done ⇒ lưu hành giảm).

**Độ chính xác KHÔNG ước lượng — đo bằng control**: chạy đúng thuật toán đó trên 131 sự kiện
**đã biết size**, so với giá trị thật.

| | v1 (lỏng) | v3 (chốt) |
|---|---|---|
| suy được / 131 | 24 | **13** |
| khớp CHÍNH XÁC | 18 (75%) | **10 (76,9%)** |
| sai ≤5% | 21 (87,5%) | **11 (84,6%)** |
| sai ≤20% | — | **12 (92,3%)** |

Hai ca trượt còn lại: GIL 2015-10-23 (thật −12.000, suy −8.000) và HIG 2018-12-17 (thật 964.000,
suy 1.092.614) — đều là quý có thêm biến động nhỏ mà `corporate_action` không ghi.

### Ba hàng rào phải thêm, mỗi cái vá một lỗi ĐÃ tạo ra kết quả sai
- **Tầng MEDIUM (trừ bù corporate_action) bị loại hẳn**: đo trên control được **0/4 đúng**,
  sai trung vị 116%, ca tệ nhất 29.520% (FOC). Không có bằng chứng nó hoạt động.
- **`shares_delta` NULL 100% trên ISS (11.747 dòng) và DIV (17.189 dòng)** — chỉ `issue_volumn` được
  điền cho ISS. Bộ lọc confounder v1 vì thế **mù trước mọi đợt phát hành**. Hậu quả thật:
  VPB 2023 bị quy **1.190.500.000 CP** thành "bán CP quỹ", trong khi đó đúng bằng
  `issue_volumn` của ISS record_date 2023-10-20 (phát hành riêng lẻ cho SMBC).
- **Lọc theo CỬA SỔ NGÀY vẫn rò**, vì ngày ISS/AIS trễ hơn lúc số CP thật sự đổi: TPB nhảy đúng
  100.000.000 CP trong quý 2021Q2 nhưng ISS tương ứng có record_date 2021-09-14 — **ngoài** cửa sổ.
  ⇒ thêm **value-match**: |ΔOShares| trùng (sai <0,5%) với bất kỳ `issue_volumn`/`shares_delta` nào
  của chính mã đó ở **bất kỳ ngày nào** → từ chối.
- **Trần quy mô 10% OShares**: size CP quỹ THẬT có p95 = 9,3% (n=112). Trên 10% nhiều khả năng là
  phát hành. Đánh đổi đo được: bỏ sót ~5/112 (4,5%) sự kiện thật sự lớn.

### ⚠️ `NO_MOVE` KHÔNG có nghĩa "size = 0"
Trong control có **62 sự kiện với size THẬT > 0 mà OShares không nhúc nhích một cổ phiếu nào** —
trung vị 110.976 CP, **14 ca ≥ 1 triệu CP**, lớn nhất PVI 2020-05-06 = 7.590.400 CP.
`ticker_financial.OShares` của vendor **thường không phản ánh giao dịch CP quỹ**. Đây là lý do gốc
khiến trần trên của phương pháp này thấp, và là lý do 134 ca `NO_MOVE` phải xếp vào "không có dữ
liệu" chứ tuyệt đối không được nội suy thành 0.

## 3 — Kết quả cuối trên 446 sự kiện

| Nguồn | Số sự kiện | Độ tin cậy |
|---|---|---|
| **Dòng anh em cùng sự kiện** (dedup artifact) | **3** | **Chắc chắn** — là số vendor công bố, không suy luận |
| **Nguồn 1 — lệch OShares** (v3, tier HIGH) | **33** | **77% khớp chính xác, 85% sai ≤5%, 92% sai ≤20%** (đo trên control n=13) |
| Nguồn 2 — parse title | **0** | `short_content` NULL 100%; parser đã vét cạn title |
| Nguồn 3 — link `news_id` → corporate_action | **0** | khớp 2/585, không dòng nào mang size |
| **KHÔNG CÓ DỮ LIỆU** | **410** | — |
| | **446** | |

Phân rã 413 ca không suy được (gồm 410 + 3 đã thu hồi theo đường khác):

| Lý do | n | % |
|---|---|---|
| `CA_CONFOUNDED` — có ISS/DIV/AIS/MA trong cửa sổ | 143 | 32,1% |
| `NO_MOVE` — OShares bất động qua 2 quý kế tiếp | 134 | 30,0% |
| `MULTI_EVENT` — ≥2 sự kiện treasury cùng cửa sổ | 94 | 21,1% |
| `NO_DATA` — thiếu dãy BCTC bao quanh | 26 | 5,8% |
| `ISSUANCE_MATCH` — Δ trùng lượng phát hành đã biết | 8 | 1,8% |
| `SIGN_MISMATCH` — Δ ngược dấu kỳ vọng | 6 | 1,3% |
| `OVER_CAP` — >10% OShares | 2 | 0,4% |

33 ca suy được nằm trên **25 mã**; 410 ca không có dữ liệu nằm trên **175 mã**.
Size suy được đều nhỏ và hợp lý cho CP quỹ: lớn nhất ACB 2019-11-01 sell_done 6.222.000 (0,38%),
VND 2021-11-26 5.914.995 (1,38%), CTD 2021-02-01 buy_done −2.008.900 (2,63%).

## 4 — Khuyến nghị (không tự quyết)
- **Không thể "xử lý dứt điểm" 446 ca.** 410/446 (92%) thiếu size là giới hạn **của nguồn dữ liệu**,
  không phải của nỗ lực: text không tồn tại, link chéo không tồn tại, và OShares của vendor
  chứng minh được là không theo dõi CP quỹ một cách đáng tin.
- Nếu vẫn dựng bảng: nạp 36 ca có size (3 chắc chắn + 33 suy luận, **gắn cờ nguồn + độ tin cậy riêng**,
  đừng trộn lẫn với size vendor công bố), 410 ca còn lại giữ `UNSIZED`.
  Đúng hướng thiết kế `TREASURY_UNSIZED` mà Taylor đã đề xuất — nhóm này **không** thu nhỏ đủ để
  bỏ cơ chế cờ đó đi.
- 33 ca suy luận **chưa qua kiểm định độc lập**; nếu chúng sẽ chạm số liệu dùng cho quyết định
  đầu tư, nên để quant-skeptic soi trước khi nạp. Rủi ro đã biết: 2 lần trong quá trình làm việc này,
  một cấu hình trông hợp lý đã sinh ra quy kết sai cỡ hàng trăm triệu cổ phiếu (VPB, TPB).

## Artifact
`events.csv` (577) · `fin.csv` · `ca.csv` — dữ liệu thô ·
`infer_size.py` → `diag.py` → `final.py` → `final2.py` → **`final3.py` (chốt)** ·
`resolved.csv` (33 ca suy được) · `still_unsized.csv` (413) · `final_inferred.csv` (577, đủ cột lý do)
