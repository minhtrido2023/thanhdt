# `tav2_bq.ticker_prune` — Điều tra & Giải đáp về Universe

**Ngày điều tra:** 2026-07-22
**Đối tượng:** bảng BigQuery `lithe-record-440915-m9.tav2_bq.ticker_prune`
**Bối cảnh:** Nhóm research đang xây bộ quy tắc quản trị universe dựa trên `ticker_prune`. Trong lúc
điều tra họ phát hiện một số hiện tượng bất thường và soạn 10 câu hỏi gửi người quản trị BigQuery.
Tài liệu này ghi lại nguyên văn các câu hỏi đó, kết quả xác minh trên dữ liệu production, và câu
trả lời cho từng câu.

**Kết luận một dòng:** Cả 3 phép đo trong bản điều tra đều **đúng về số liệu** nhưng **sai về nguyên
nhân**. Không tồn tại hệ thống quản trị universe nào phía sau `ticker_prune` — bảng này là kết quả
chồng lấn của **ba đường ghi độc lập**, và điều đó khiến 8/10 câu hỏi trở thành câu hỏi sai đối tượng.

---

## Phần 0 — Cách bảng `ticker_prune` thực sự được tạo ra

Đây là kiến thức nền cần có trước khi đọc phần trả lời. Bảng bị ghi bởi **3 đường độc lập**, mỗi
đường dùng một danh sách mã khác nhau và một chế độ ghi khác nhau.

| # | Đường ghi | Code | Danh sách mã dùng | Chế độ ghi | Tần suất |
|---|---|---|---|---|---|
| 1 | **Rebuild toàn bộ** | `deeplearning/bigquery.py:535` `run_prune_ticker_pipeline()` (`--mode prune`, và nằm trong `--mode full`) | `hit_ticker_list.csv` (453 mã) | `WRITE_TRUNCATE` — **xóa hẳn bảng** rồi tạo lại từ `gs://tav2-gs/v2_prune/*.csv` | Thủ công |
| 2 | **Append hằng ngày** | `worker/tasks/schedule_tasks.py:467` → `sync_bigquery_table_batch(table_type="ticker_prune")` | `ticker_list.csv` (1.873 mã, cập nhật hằng ngày) | delete + append theo `(ticker, time)`, chỉ **7 ngày gần nhất** (`sync_window_days=7`), tối đa 5 dòng/mã (`latest_rows_per_ticker=5`) | Hằng ngày |
| 3 | **Replace toàn bộ lịch sử 1 mã** | `worker/tasks/bigquery_tasks.py:526` `replace_ticker_data_in_bigquery_table(table_type="ticker_prune")`, được gọi trong chain tại `worker/tasks/data_tasks.py:615-628` | Từng mã riêng lẻ | Xóa sạch mã đó rồi nạp lại **toàn bộ lịch sử** | **Event-driven** — mỗi khi mã có báo cáo tài chính quý mới hoặc sự kiện điều chỉnh giá |

Cả ba đường đều áp **cùng một bộ lọc cấp dòng**:

```python
Volume_3M_P50 * Price / Inflation_7 > 1_000_000_000.0
```
*(`deeplearning/bigquery.py:261-265` và `worker/tasks/bigquery_tasks.py:127-131`)*

- `Volume_3M_P50` — trung vị khối lượng khớp lệnh 3 tháng
- `Price` — giá **chưa điều chỉnh**
- `Inflation_7` — hệ số khử lạm phát 7%/năm
- ⇒ Ý nghĩa: **giá trị giao dịch trung vị 3 tháng > 1 tỷ VND/phiên, quy về mệnh giá gốc**

Điểm mấu chốt: **đây là bộ lọc theo từng dòng (từng ngày), không phải theo mã.** Một mã chỉ xuất
hiện ở đúng những phiên nó đủ thanh khoản, nên chuỗi thời gian trong bảng **có lỗ hổng**. Ví dụ mã
`AAM` chỉ có 304 dòng và dừng hẳn ở 2011-03-10.

Do đó, cái mà nhóm research gọi là "membership" thực chất là tích của ba yếu tố không liên quan
đến nhau:

> *(mã có nằm trong danh sách mà pipeline đang chạy lặp qua không)*
> × *(dòng ngày đó có vượt ngưỡng thanh khoản không)*
> × *(mã đó có sống sót qua lần `TRUNCATE` gần nhất không)*

---

## Phần 1 — Bằng chứng quyết định

```
$ bq show --format=prettyjson tav2_bq.ticker_prune

  creationTime     = 2026-07-12 01:08:23    ← bảng bị DROP rồi tạo lại tại đây
  lastModifiedTime = 2026-07-21 16:36:06
  numRows          = 930,245
```

Vì `import_gcs_to_bigquery` khi gặp `WRITE_TRUNCATE` sẽ gọi `delete_table()` rồi `create_table()`
(`deeplearning/bigquery.py:208-216`), nên **`creationTime` chính là dấu thời gian của lần rebuild
toàn bộ gần nhất: 2026-07-12 01:08**.

Toàn bộ các hiện tượng "bất thường" mà nhóm research đo được đều là hệ quả trực tiếp của mốc này.

**Số liệu bổ sung (đo ngày 2026-07-21/22):**

```
tav2_bq.ticker_prune : 543 mã / 930.245 dòng / 2000-12-15 → 2026-07-21
hit_ticker_list.csv  : 453 mã  (GCS, sửa lần cuối 2026-04-14)
ticker_list.csv      : 1.873 mã (GCS, cập nhật hằng ngày, 2026-07-21)
tav2_bq.ticker       : 1.291 mã

→ 91 mã có trong bảng nhưng KHÔNG có trong hit list (51 mã vẫn cập nhật tới 07-21)
→ 1 mã (HLC) có trong hit list nhưng KHÔNG có dòng nào trong bảng
→ 146/543 mã có MAX(time) < 2025 (mã đã chết / mất thanh khoản, lịch sử vẫn nằm lại)
```

---

## Phần 2 — Phán quyết cho 3 nhận định của bản điều tra

| Nhận định gốc | Số liệu | Diễn giải nguyên nhân |
|---|---|---|
| Pool ticker bị đóng băng 2026-03-13 → 2026-07-06, rồi mở băng bằng 1 lô 41 mã | ✅ **Đúng** | ❌ **Sai — không tồn tại khái niệm "pool"** |
| VPL chờ 419 ngày, SBG chờ 948 ngày; 24 mã niêm yết 2023-2026 chưa từng xuất hiện | ✅ **Đúng** | ❌ **Sai — không có "hàng đợi"; con số trộn lẫn 2 nguyên nhân khác hẳn nhau** |
| 10.850 dòng lịch sử 2014-2025 xuất hiện trong 8 ngày | ✅ **Đúng** | ⚠️ **Đúng một nửa — có backfill thật, nhưng là event-driven per-ticker, không có lịch, và không bao giờ kết thúc** |

### 2.1 — "Lô 41 mã ngày 2026-07-06"

Kiểm tra 41 mã này:

- Cả 41 mã có **đúng 12 dòng**, trải từ 2026-07-06 đến 2026-07-21.
- **Cả 41 mã đều KHÔNG nằm trong `hit_ticker_list.csv`.**

Giải thích: sau lần `TRUNCATE` ngày 2026-07-12, bảng chỉ còn các mã thuộc hit list. Job append
hằng ngày (đường ghi #2) dùng `ticker_list.csv` đầy đủ nên lập tức đưa các mã ngoài hit list trở
lại — nhưng chỉ trong cửa sổ 7 ngày:

```python
sync_min_date = today - (sync_window_days - 1)   # schedule_tasks.py:448-453
# chạy ngày 2026-07-12  →  min_sync_date = 2026-07-06
```

Và 12 dòng = đúng số phiên giao dịch từ 07-06 đến 07-21 (trừ cuối tuần).

**Kết luận: 2026-07-06 là sàn cửa sổ append, không phải "ngày mã được thêm vào universe".**
Đây không phải sửa lỗi thủ công và cũng không phải thay đổi rule.

### 2.2 — "Thời gian chờ để vào bảng"

Chạy lại bộ lọc thanh khoản trực tiếp trên dữ liệu thô `ticker_v1a/`:

```
SBG : 512/612 dòng vượt ngưỡng, phiên đầu tiên = 2024-03-01
      → nhưng trong BQ chỉ có từ 2026-07-06
DKG : 0/252 dòng vượt ngưỡng
      → vắng mặt vì THANH KHOẢN, không phải vì "đang chờ"
IVS : 1.622 dòng vượt ngưỡng, 2012-03-20 → 2025-12-15
      → khớp CHÍNH XÁC 1.622 dòng vừa xuất hiện trong BQ
TIS : 682 dòng vượt ngưỡng
      → khớp CHÍNH XÁC 682 dòng trong BQ
```

Vậy con số "thời gian chờ" thực ra gộp hai nhóm nguyên nhân hoàn toàn khác nhau:

1. **Đủ thanh khoản từ lâu nhưng lịch sử bị `TRUNCATE` xóa mất** (SBG đủ điều kiện từ 2024-03
   nhưng không thuộc hit list nên bị xóa, và chưa được đường ghi #3 phục hồi).
2. **Chưa bao giờ đủ thanh khoản** (DKG — 0 phiên vượt ngưỡng).

Không có nhóm nào liên quan tới quy tắc theo tuổi niêm yết.

Còn hiện tượng "~85 ngày kể từ ngày niêm yết" ở ABW/GDA/TCX/VPX: đó đơn giản là thời gian cần để
tích lũy đủ dữ liệu cho `Volume_3M_P50` (~3 tháng phiên giao dịch).

### 2.3 — "10.850 dòng lịch sử xuất hiện trong 8 ngày"

Hiện tượng có thật, nhưng cơ chế là đường ghi **#3**: `replace_ticker_data_in_bigquery_table` —
xóa sạch một mã rồi nạp lại **toàn bộ lịch sử** của mã đó
(`worker/tasks/bigquery_tasks.py:526`, docstring: *"Delete one ticker from BigQuery and append its
full recalculated local history"*).

Nó được kích hoạt trong chain tại `worker/tasks/data_tasks.py:615-628`, tức là **mỗi khi một mã có
báo cáo tài chính quý mới hoặc sự kiện điều chỉnh giá** → recompute giá → recompute chỉ báo → đẩy
lại toàn bộ lịch sử lên BigQuery.

- Không có lịch trình.
- Không có điểm kết thúc.
- Sẽ bùng lên mỗi mùa công bố báo cáo quý.

Con số 1.622 dòng của IVS khớp chính xác với số dòng vượt ngưỡng trong dữ liệu thô — nên đây là
một lần replay trung thực bộ lọc, không phải một chiến dịch backfill có chủ đích.

---

## Phần 3 — Trả lời 10 câu hỏi

### Câu 1 — Rule chính xác để một mã được đưa vào / loại khỏi bảng là gì? Ngưỡng thanh khoản nào, cửa sổ bao nhiêu phiên, tần suất đánh giá lại?

**Không tồn tại rule ở cấp mã.** Chỉ có một bộ lọc cấp dòng duy nhất, áp giống hệt nhau ở cả 3
đường ghi:

```python
Volume_3M_P50 * Price / Inflation_7 > 1e9
```

- **Ngưỡng:** ≈ 1 tỷ VND giá trị giao dịch/phiên, quy về mệnh giá gốc (đã khử lạm phát 7%/năm)
- **Cửa sổ:** trung vị 3 tháng (`Volume_3M_P50`)
- **Tần suất đánh giá lại:** **mỗi dòng, mỗi ngày** — không phải định kỳ theo tháng/quý

Hệ quả quan trọng: vì lọc theo dòng chứ không theo mã, **chuỗi thời gian của một mã bị đứt quãng**.
Bất kỳ tính toán nào giả định chuỗi liên tục (MA, breadth, rolling stats) đều cần xử lý lỗ hổng này.

### Câu 2 — Có danh sách curated thủ công ("legacy product selection") nằm trên rule tự động không?

**Có — xác nhận.** Đó là `gs://tav2-gs/rawdata/stock_meta/latest/hit_ticker_list.csv`, dùng bởi
đường rebuild toàn bộ (`get_active_tickers(type="prune")`, `deeplearning/bigquery.py:468`).

- **Ai sinh ra:** `webui/simulation_bot.py:893-899` — lấy `ticker` unique từ `profile_hit.csv`, tức
  là **danh sách các mã từng phát sinh deal trong backtest pattern**.
- **Đưa lên GCS bằng cách nào:** thủ công. Không có Celery task nào ghi file này.
- **Sửa lần cuối:** **2026-04-14** (đối chiếu: `ticker_list.csv` được worker cập nhật hằng ngày,
  bản mới nhất 2026-07-21).
- **Trigger:** không có.

### Câu 3 — Có đúng pool bị đóng băng 2026-03-13 → 2026-07-06 không? Lô 41 mã ngày 07-06 là sửa lỗi hay đổi rule?

**Không phải cả hai.** Xem mục 2.1. Bảng bị `TRUNCATE` lúc 2026-07-12 01:08; 2026-07-06 là sàn cửa
sổ append 7 ngày của lần chạy đầu tiên sau đó. Không có ai can thiệp thủ công, không có rule nào
thay đổi.

Lý do "khoảng đóng băng" xuất hiện: `MIN(time)` **không phải** ngày mã được thêm vào universe. Với
các mã thuộc hit list, `MIN(time)` là phiên đầu tiên trong lịch sử chúng vượt ngưỡng thanh khoản
(thường rất xa trong quá khứ). Với các mã ngoài hit list, `MIN(time)` là sàn cửa sổ append. Trộn
hai loại này vào một biểu đồ sẽ tạo ra ảo giác về một "pool" có lúc mở lúc đóng.

### Câu 4 — ETL có ghi đè / bổ sung dòng lịch sử không? Đang chạy dở hay đã xong? Bao giờ bảng ổn định lại?

**Có, liên tục.** Cơ chế: đường ghi #3 (`replace_ticker_data_in_bigquery_table`), event-driven theo
báo cáo tài chính quý và sự kiện điều chỉnh giá — chi tiết ở mục 2.3.

**Bảng sẽ không bao giờ "ổn định lại".** Không có lịch trình nào để công bố, vì hoạt động ghi đè
này gắn với luồng dữ liệu tài chính chứ không gắn với một chiến dịch có điểm kết thúc.

### Câu 5 — Khi một mã mới được thêm, lịch sử có được backfill toàn bộ không? Vì sao FRT đầy đủ mà 41 mã ngày 07-06 thì không?

**Không đồng nhất, và sự khác biệt không liên quan gì tới việc mã "mới" hay "cũ".** Độ sâu lịch sử
phụ thuộc vào **đường ghi nào chạm vào mã đó gần nhất**:

| Trường hợp | Kết quả |
|---|---|
| Nằm trong `hit_ticker_list` | Có đủ lịch sử từ lần rebuild GCS (đường #1) |
| Được `replace_ticker_data_*` chạm vào (đường #3) | Có đủ lịch sử — VD: IVS, PXL, TIS, MZG, FRT |
| Chỉ được daily append chạm vào (đường #2) | Chỉ có từ sàn cửa sổ — VD: 41 mã ngày 07-06 |

Nói gọn: **độ sâu lịch sử là hàm của "lần cuối mã đó được rebuild", không phải hàm của bất kỳ rule
universe nào.**

### Câu 6 — Membership quá khứ là point-in-time hay áp tiêu chí hiện tại ngược về quá khứ? *(câu quan trọng nhất)*

Cần tách làm ba tầng, vì mỗi tầng có câu trả lời khác nhau:

**Tầng 1 — Bộ lọc cấp dòng: CÓ tính causal (an toàn).**
`Volume_3M_P50` và `Price` tại mỗi dòng đều là dữ liệu quá khứ tính đến đúng ngày đó. Bản thân phép
lọc không nhìn về tương lai.

**Tầng 2 — Universe: KHÔNG point-in-time (có bias thật).**
`hit_ticker_list` được suy ra từ **kết quả backtest** (mã nào từng sinh deal) rồi áp ngược cho toàn
bộ lịch sử. Đây đúng là **selection / survivorship bias** mà nhóm research lo ngại. Mối lo là chính
đáng.

**Tầng 3 — Khả năng tái lập: KHÔNG reproducible (vấn đề nghiêm trọng hơn cả tầng 2).**
Membership của một ngày trong quá khứ **thay đổi theo thời gian**. Chính nhóm research đã đo được
điều này: IVS có 0 dòng ở bản backup ngày 2026-07-13, và 1.622 dòng cho giai đoạn 2012-2025 ở bản
ngày 2026-07-21. Nghĩa là **cùng một backtest, cùng một khoảng thời gian, chạy hôm nay và chạy tuần
sau sẽ cho universe khác nhau.**

> ⚠️ **Cảnh báo thêm:** bảng có sẵn các cột nhãn forward-looking `profit_2W`, `profit_1M`,
> `profit_2M`, `profit_3M` cùng toàn bộ biến thể `_center_*` (sinh bởi `calc_profits_v1`,
> `deeplearning/bigquery.py:57`). Đây là **nhãn để train model**, tuyệt đối không được đưa vào
> feature hoặc điều kiện lọc khi backtest.

### Câu 7 — Có versioning / changelog cho tiêu chí lựa chọn không? Đang chạy phiên bản rule nào?

**Không có.** Không có bảng rule, không có version, không có audit log. Thứ gần nhất với khái niệm
"phiên bản hiện hành" là ba dấu vết rời rạc:

- Ngưỡng hardcode `1_000_000_000.0` tại 2 vị trí trong code
- Timestamp file `hit_ticker_list.csv` trên GCS: **2026-04-14**
- `creationTime` của bảng (= lần rebuild gần nhất): **2026-07-12 01:08**

### Câu 8 — Mã niêm yết mới có "đường tự động" để vào bảng không? Vì sao mã này vào được, mã kia không?

**Có, nhưng nó bị vô hiệu hóa định kỳ.** Đường tự động = daily append (#2), dùng `ticker_list.csv`
đầy đủ. Tuy nhiên **mọi mã đưa vào bằng đường này đều bị xóa sạch ở lần rebuild toàn bộ tiếp theo**,
vì rebuild chỉ nạp lại các mã thuộc hit list.

Bằng chứng cho sự lệch pha này:

- **91/543** mã trong bảng không có trong hit list (51 mã vẫn đang cập nhật tới 2026-07-21)
- Ngược lại, **HLC** nằm trong hit list nhưng **không có dòng nào** trong bảng (chưa bao giờ vượt
  ngưỡng thanh khoản)

Còn khoảng "~85 ngày" ở ABW/GDA/TCX/VPX là thời gian tích đủ dữ liệu cho `Volume_3M_P50`, không
phải quy tắc theo tuổi niêm yết. Các mã như DKG "chưa từng vào" đơn giản vì chưa có phiên nào vượt
ngưỡng.

### Câu 9 — Có thể cung cấp snapshot dạng "as-of" (membership bất biến theo ngày) không?

**Hiện không có, và nên tự xây ở phía research.** Bảng chỉ lưu một trạng thái hiện tại, lại bị ghi
đè bởi 3 đường độc lập, nên không thể dùng làm nguồn as-of.

**Khuyến nghị kỹ thuật:** dựng snapshot `(as_of_date, ticker)` hằng ngày, tính trực tiếp điều kiện
thanh khoản trên `tav2_bq.ticker` (bảng đầy đủ 1.291 mã) thay vì đọc `ticker_prune`. Cách này giải
quyết đồng thời hai vấn đề:

- Có point-in-time thật và bất biến (giải quyết tầng 3 của câu 6)
- Bỏ được hoàn toàn bias từ `hit_ticker_list` (giải quyết tầng 2 của câu 6)

### Câu 10 — Khi một mã bị hủy niêm yết, lịch sử giao dịch có được giữ không?

**Được giữ — nhưng chỉ cho tới lần `TRUNCATE` kế tiếp.**

Hiện tại có **146/543** mã với `MAX(time) < 2025` (mã cũ nhất kết thúc từ 2008-02), lịch sử vẫn còn
nguyên. Tuy nhiên nếu mã đó không nằm trong hit list thì lần chạy `--mode prune` tới sẽ xóa sạch nó.
Và vì mã đã delist nên không còn báo cáo tài chính hay sự kiện giá nào để kích hoạt đường ghi #3
phục hồi lại → **mất vĩnh viễn**.

---

## Phần 4 — Khuyến nghị

**Không nên gửi 10 câu hỏi này đi.** Chúng giả định tồn tại một hệ thống quản trị universe mà thực
tế không có: không có rule membership, không có pool, không có hàng đợi, không có versioning.

Câu hỏi duy nhất thực sự cần được trả lời là:

> **`ticker_prune` nên là "hit universe cố định" hay "universe thanh khoản động"?**

Hiện tại nó là **cả hai cùng lúc**, và kết quả phụ thuộc vào việc pipeline nào chạy sau cùng. Ba
đường ghi cần được thống nhất về một nguồn universe duy nhất **trước khi** xây bất kỳ lớp quản trị
nào lên trên.

Các việc cần làm kèm theo, theo thứ tự ưu tiên:

1. **Thống nhất nguồn universe** giữa 3 đường ghi (rebuild / daily append / per-ticker replace).
2. **Xây lớp snapshot as-of** ở phía research, độc lập với `ticker_prune` (xem câu 9).
3. **Bật lại việc dọn prefix GCS** — `delete_gcs_files(...)` đang bị comment tại
   `deeplearning/bigquery.py:538`, nên file CSV cũ trong `gs://tav2-gs/v2_prune/` không bao giờ bị
   xóa và vẫn được nạp lại ở mỗi lần `TRUNCATE`. Hiện tại chưa gây lệch (455 file ≈ khớp hit list)
   nhưng đây là bug tiềm ẩn.
4. **Rà soát cờ `is_skip`** — đường `deeplearning/bigquery.py` không tôn trọng cờ này, trong khi
   worker có (`schedule_tasks.py:441`).
5. **Lưu ý `max_bad_records=10`** trong cấu hình load job: mỗi lần nạp có thể âm thầm bỏ qua tối đa
   10 dòng lỗi mà không báo.

---

## Phụ lục — Lệnh kiểm chứng

```bash
# Dấu thời gian rebuild toàn bộ gần nhất
bq show --format=prettyjson tav2_bq.ticker_prune | grep -E '"(creationTime|lastModifiedTime|numRows)"'

# Membership hiện tại: mã, phiên đầu, phiên cuối, số dòng
bq query --use_legacy_sql=false --max_rows=10000 --format=csv \
  'SELECT ticker, MIN(time) mn, MAX(time) mx, COUNT(*) c
   FROM tav2_bq.ticker_prune GROUP BY ticker ORDER BY ticker'

# Hai danh sách mã nguồn
gsutil cat gs://tav2-gs/rawdata/stock_meta/latest/hit_ticker_list.csv   # 453 mã, sửa 2026-04-14
gsutil cat gs://tav2-gs/rawdata/stock_meta/latest/ticker_list.csv       # 1.873 mã, cập nhật hằng ngày
gsutil ls -l gs://tav2-gs/rawdata/stock_meta/latest/

# Replay bộ lọc thanh khoản trên dữ liệu thô để đối chiếu
python - <<'PY'
import pandas as pd, numpy as np
d = pd.read_csv("ticker_v1a/IVS.csv", dtype={'time': str})
v = pd.to_numeric(d['Volume_3M_P50'], errors='coerce')
p = pd.to_numeric(d['Price'], errors='coerce')
inf = pd.to_numeric(d['Inflation_7'], errors='coerce').replace(0, np.nan)
m = (v * p / inf) > 1e9
print(m.sum(), d.loc[m, 'time'].iloc[0], d.loc[m, 'time'].iloc[-1])
PY
```

**Lưu ý về độ tin cậy:** toàn bộ metadata BigQuery, số dòng và membership trong tài liệu này lấy
trực tiếp từ production ngày 2026-07-21/22. Riêng các con số replay bộ lọc ở cấp mã được tính trên
bản mirror `ticker_v1a/` của máy dev (dữ liệu tới 2026-05-22, thiếu một số mã như VPL/VNZ/QNP), nên
chỉ kiểm chứng được cho các mã có sẵn local.
