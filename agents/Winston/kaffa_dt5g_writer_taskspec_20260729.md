# kaffa_v2 ghi `vnindex_5state_dt5g_live` — điều tra code thật + task-spec đề xuất (2026-07-29)

Job: `Winston_20260729_114625` · Nối tiếp `Winston_20260729_110410`
(`dt5g_live_second_writer_20260729.md`). **Chỉ ĐỀ XUẤT — không chạm codebase của team dữ liệu.**

---

## TL;DR — 3 giả định đầu vào đều SAI, cần đính chính trước khi gửi cho hainguyen

| Giả định | Thực tế (đã đọc code + đo dữ liệu) |
|---|---|
| "Họ dùng Celery + **Claude** → tốn token, cần thay bằng SQL cho rẻ" | **KHÔNG có LLM ở bất kỳ đâu trong đường tính market-state.** Toàn bộ là numpy/pandas thuần. Chi phí LLM cần tiết kiệm = **0**. |
| "Họ **dựa trên bản DT5G của mình** rồi cập nhật thêm" | **KHÔNG.** Họ **tự tính lại toàn bộ chuỗi DT5G từ đầu** bằng bản port riêng, đọc dữ liệu **local `ticker_v1a/`** + yfinance + file SBV của họ. Không hề đọc `tav2_bq.vnindex_5state_dt5g_live` hay bảng base của mình. |
| "2 engine không bit-identical (27/3134 phiên lệch)" | **Sai — đó là lệch VINTAGE, không phải lệch engine.** So cùng vintage: **0 lệch trên 3.135 phiên, ở MỌI tầng** (v3.4b base, DT4-gate, macro, final, state_raw). Xem §3. |

Vấn đề còn lại **không phải chi phí, mà là quyền sở hữu bảng production** (2 writer / split-brain
+ che gate fail-safe của mình). Cách sửa rẻ nhất: **đổi 1 biến môi trường** phía họ, không sửa code.

---

## 1. Có gọi Claude/LLM không? → KHÔNG (đã đọc hết đường gọi)

Đường thực thi: Celery `pipeline` → `schedule_tasks.update_market_state:610` →
`market_state_tasks.update_market_regime_state:246` → `dt5g_chain.pipeline.build_state_history`.

Toàn bộ package `core_utils/market_state_engines/dt5g_chain/` (11 file, 1.332 dòng) chỉ import
`numpy`, `pandas`, `json`, `pathlib` + `yfinance` (feed US). `grep -rniE 'anthropic|claude|openai|
langchain|llm|gpt-|gemini'` trên toàn repo: các hit đều **ngoài** đường này (`agent/agent_main.py`,
`tools/`, `tuning/`, `.claude/skills/`, `CLAUDE.md`) — không file nào được `market_state_tasks.py`
hay `dt5g_chain/` import. `requirements.txt` **không có** `anthropic`/`openai`.

→ (a) Không có bước nào gọi LLM. (b) Không áp dụng. Giả định "tốn token Claude" **SAI hoàn toàn**;
nếu gửi thông điệp "chuyển sang SQL cho đỡ tốn token" họ sẽ thấy mình chưa đọc code của họ.

Cần nói rõ: **Celery ≠ Claude.** Celery chỉ là task queue Python; task này là recompute pandas
(vài chục giây), chi phí duy nhất là CPU.

## 2. Họ lấy dữ liệu gốc từ đâu? → dữ liệu LOCAL của chính họ, không phải bảng của mình

`market_state_tasks.py:258-277`:
- VNINDEX: `ticker_v1a/VNINDEX.csv` (local, 23 cột chỉ báo họ tự tính) — `_load_local_vni()`.
- Universe: `load_all_ticker_panel()` từ `ticker_v1a/` local, lọc `Close>0`, `time>='2013-01-01'`,
  loại `VNINDEX/VN30/VN30F*/E1VFVN30*/FUE*`.
- US: `preprocess/market_state/us_market_history.csv` (yfinance SPX+VIX, task riêng).
- SBV: `core_utils/data/sbv_refi_events.json` (bản copy của họ).
- Breadth: `get_stock_list(typ="hit")` — họ tự dựng lại tiêu chí `ticker_prune`
  (`Volume_3M_P50*Price/Inflation_7 > 1e9`) trên panel local (`pipeline.py:31-73`).

Docstring đầu file ghi thẳng: *"No BigQuery: the VNINDEX row and the universe panel are read from
local ticker_v1a/"*. BigQuery chỉ xuất hiện ở **bước cuối cùng**, là ghi ra
(`_sync_market_state_to_bigquery`, DELETE `time>=min_time` + APPEND 5 phiên).

**Kiến trúc của họ vs của mình khác nhau thật:**

| | Mình (`macro_state_live.py`) | kaffa (`dt5g_chain/`) |
|---|---|---|
| Tầng 1-5 (ew_base→conc→dual→us_overlay→v3.4b) | **KHÔNG tính live** — đọc bảng đã publish `tav2_bq.vnindex_5state_tam_quan_v34b_clean:105` | **Tính lại toàn bộ** từ panel local |
| Tầng 6 DT 4-gate | `_dt_4gate(10,25,25)` | `four_gate.asym_dir_commit` |
| Tầng 7 macro | `get_macro_state` | `macro.compute_macro_state` |
| Tầng 8 fail-safe | `get_gated_state` + `macro_health.json` | `healthcheck.assess_macro_health` inline |

Bản port của họ là **port chính xác** (họ ghi rõ trong docstring: *"port of
experiment_4/macro_state_live.py"*), kể cả chi tiết mình đổi 2026-06-03: dòng
`macro.py:172` — easing FLOOR **đã bị comment out**, khớp `EASING_FLOOR_ENABLED=False` của mình.

## 3. Cơ chế 27 phiên lệch — đã xác định DỨT ĐIỂM: **lệch vintage, KHÔNG phải lệch engine**

Dùng BigQuery time-travel để lấy đúng ảnh chụp bảng trước mọi lượt ghi hôm nay
(`FOR SYSTEM_TIME AS OF '2026-07-29T09:00:00Z'` = 16:00 ICT) rồi so 3 chiều:

```
rows: 3134  (2014-01-02 → 2026-07-28)
PREV (bản publish 07-28 của mình)  vs KAFFA (artifact 17:12 hôm nay) : 27 lệch
PREV (bản publish 07-28 của mình)  vs NOW  (bản publish 18:36 hôm nay): 27 lệch   ← CÙNG 27 NGÀY ĐÓ
NOW  (bản publish 18:36 của mình)  vs KAFFA                          :  0 lệch
```

Và so từng tầng, cùng vintage (3.135 phiên, script `/tmp/attrib.py`):

```
L5 v3.4b base   mình vs kaffa : 0 lệch
L6 DT4 gate     mình vs kaffa : 0 lệch
L7 final state  mình vs kaffa : 0 lệch
state_raw       mình vs kaffa : 0 lệch
```

→ **Hai engine cho kết quả GIỐNG HỆT NHAU khi ăn cùng vintage dữ liệu.** 27 "phiên lệch" mà job
trước quan sát lúc 18:04 ICT là do so **bản CSV publish 07-28 của mình** với **artifact tính lại
lúc 17:12 hôm 07-29** — lệch 1 ngày dữ liệu, không phải lệch thuật toán. Đính chính kết luận
"2 engine KHÔNG bit-identical" trong `dt5g_live_second_writer_20260729.md`.

### 3b. NHƯNG lòi ra 1 vấn đề THẬT của mình: lịch sử DT5G bị viết lại mỗi đêm

Chính 27 phiên đó là **series của MÌNH tự đổi** giữa publish 07-28 và publish 07-29. Truy ngược
lên bảng base `vnindex_5state_tam_quan_v34b_clean` (time-travel từng ngày):

```
2026-07-25 → 07-27 :  0 phiên lịch sử bị đổi
2026-07-27 → 07-28 :  1
2026-07-28 → 07-29 (trước refresh tối) :  1
refresh tối 07-29 (18:30) : 71 phiên lịch sử bị đổi   ← bất thường
```

71 phiên base bị viết lại (2,3% lịch sử; hầu hết dịch **+1 bậc**: 4→5, 2→3, 3→4), DT-gate hấp thụ
bớt còn **27 phiên final + 28 phiên `state_raw`** đổi giá trị. Đã loại trừ 2 nguyên nhân:
- **Không phải** backfill `VNINDEX_PE`: hàng VNINDEX trong `tav2_bq.ticker` trước/sau hôm nay giống
  nhau (AVG PE 15.0252 vs 15.0244 — chênh đúng do thêm 1 phiên hôm nay).
- **Không phải** đổi thành phần universe: `ticker_prune` 450 mã trước và sau; `ticker` 1.291 mã
  trước và sau (chỉ thêm vài dòng lịch sử: `ticker` +5 dòng, `ticker_prune` +215 dòng, `time` cũ).

Nghi vấn còn lại (**chưa xác minh**, cần job riêng): vài trăm dòng lịch sử được restate trong
`ticker`/`ticker_prune` hôm nay đủ để làm lệch **expanding percentile rank** của tầng EW/breadth —
mà expanding rank thì một thay đổi nhỏ ở quá khứ lan ra toàn chuỗi. Kaffa "đi theo" cùng 71 phiên
đó chính vì họ ăn cùng dữ liệu thị trường gốc.

**Ý nghĩa:** lịch sử DT5G **không tái lập được** giữa các ngày. Mọi audit/backtest trích DT5G lịch
sử đang chạy trên chuỗi động. Đây là việc RIÊNG của mình, không liên quan kaffa → đề nghị mở job
riêng (xem §5).

---

## 4. PHẦN 2 — Task-spec đề xuất cho hainguyen/bq_admin

### 4.1 Vì sao KHÔNG đề xuất "thay recompute bằng 1 câu SQL mirror"

Artifact GCS của họ có **26 cột** (`state`, `allocation`, `raw_state`, `override_state`,
`gate_status`, `r_score`, `pe`, `drawdown`, `breadth`, `state_sessions`, …) và facade
`dt5g.Dt5gEngine` **bắt buộc đủ `_MARKET_STATE_HISTORY_COLUMNS`**, thiếu cột là rơi xuống fallback
`raw_v1` (regime DEGRADED, `dt5g.py:90-108`). Bảng `vnindex_5state_dt5g_live` của mình chỉ có
**3 cột** (`time,state,state_raw`) → **không đủ** để thay artifact. Việc recompute của họ có giá trị
thật cho report/webui của họ, và **không** tốn token LLM.

→ Chỉ **bước ghi BigQuery** (`_sync_market_state_to_bigquery`) là thừa/gây hại, vì nó ghi đè bảng
production của mình. Đó mới là thứ cần đổi — và đổi được **bằng 1 biến môi trường, 0 dòng code.**

### 4.2 Phương án A (khuyến nghị) — đổi đích ghi, không sửa code

`market_state_tasks.py:31` đã env-backed sẵn:

```python
MARKET_STATE_BQ_TABLE = os.environ.get("MARKET_STATE_BQ_TABLE", "vnindex_5state_dt5g_live")
```

Chỉ cần thêm vào env của Celery worker (docker-compose / `.env` / systemd unit của họ):

```bash
MARKET_STATE_BQ_TABLE=vnindex_5state_dt5g_kaffa
```

Rồi tạo bảng đích 1 lần (chạy bằng tài khoản có quyền ghi `tav2_bq`):

```sql
CREATE TABLE IF NOT EXISTS `lithe-record-440915-m9.tav2_bq.vnindex_5state_dt5g_kaffa` (
  time      DATE    NOT NULL,
  state     INT64,
  state_raw INT64
)
PARTITION BY time
OPTIONS (description = 'DT5G mirror do pipeline kaffa_v2 tu tinh (worker/tasks/market_state_tasks.py). Bang PRODUCTION cua trido la tav2_bq.vnindex_5state_dt5g_live - KHONG ghi vao do.');
```

Backfill 1 lần từ artifact hiện có: chạy task ops có sẵn của họ
`tasks.market_state_tasks.sync_market_state_bigquery(min_time="2014-01-01")` — hàm này đã
WRITE_TRUNCATE nguyên bảng từ artifact GCS, không cần code mới.

**Ưu:** 0 dòng code, giữ nguyên toàn bộ pipeline của họ, họ vẫn có bảng BQ riêng để query.
**Nhược:** không có.

### 4.3 Phương án B (nếu họ muốn dùng ĐÚNG con số production của mình, không phải bản tự tính)

Scheduled query trong BigQuery, chạy **19:15 ICT (12:15 UTC) T2–T6** — sau khi publisher của mình
xong lúc ~19:01–19:03 (cron `bq_freshness_check.sh` 19:00 ICT, bước pipeline-1
`publish_gated_state.py`), có ~12 phút đệm:

```sql
-- Scheduled query: "kaffa DT5G mirror"  | 12:15 UTC, Mon-Fri | dest: (none, DML)
-- Gương 30 phiên gần nhất tu bang production cua trido sang bang cua kaffa.
-- Idempotent: chay lai bao nhieu lan cung ra 1 ket qua.
MERGE `lithe-record-440915-m9.tav2_bq.vnindex_5state_dt5g_kaffa` AS dst
USING (
  SELECT s.time, s.state, s.state_raw
  FROM `lithe-record-440915-m9.tav2_bq.vnindex_5state_dt5g_live` AS s
  WHERE s.time >= DATE_SUB(CURRENT_DATE('Asia/Ho_Chi_Minh'), INTERVAL 45 DAY)
) AS src
ON dst.time = src.time
WHEN MATCHED AND (dst.state != src.state OR dst.state_raw != src.state_raw)
  THEN UPDATE SET state = src.state, state_raw = src.state_raw
WHEN NOT MATCHED THEN INSERT (time, state, state_raw) VALUES (src.time, src.state, src.state_raw);
```

Kèm **gate tươi** (khuyến nghị bật `Notify on failure`): thêm ở đầu để job tự fail nếu bảng nguồn
chưa cập nhật hôm nay, thay vì âm thầm gương lại số cũ:

```sql
ASSERT (
  SELECT MAX(s.time) FROM `lithe-record-440915-m9.tav2_bq.vnindex_5state_dt5g_live` AS s
) = CURRENT_DATE('Asia/Ho_Chi_Minh')
AS 'dt5g_live chua publish cho hom nay - dung mirror';
```

**Lưu ý phải nói với họ:** vì lịch sử DT5G của mình có thể được viết lại (§3b), cửa sổ 45 ngày
của MERGE sẽ cuốn theo các chỉnh sửa gần đây, nhưng **không** đồng bộ các chỉnh sửa cũ hơn 45 ngày.
Nếu họ cần lịch sử khớp tuyệt đối thì thay MERGE bằng `CREATE OR REPLACE TABLE ... AS SELECT *`
(bảng chỉ ~3.100 dòng, chi phí không đáng kể).

**Ưu:** 1 nguồn sự thật duy nhất, hết mọi rủi ro lệch. **Nhược:** phụ thuộc lịch chạy của mình
(nếu mình fail thì `ASSERT` chặn, họ mất mirror ngày đó) — nên Phương án A vẫn là mặc định an toàn
hơn cho họ, B chỉ dùng nếu họ chủ động muốn con số canonical.

### 4.4 Phương án C (bổ sung, khuyến nghị chạy song song với A) — reconcile thay vì im lặng

Vì 2 engine hiện **khớp 100%**, giá trị lớn nhất không phải gộp lại mà là **phát hiện lúc chúng
tách nhau** (một bên đổi tham số, một bên restate dữ liệu). 1 scheduled query/ngày, 19:20 ICT:

```sql
SELECT k.time, k.state AS kaffa_state, t.state AS trido_state
FROM `lithe-record-440915-m9.tav2_bq.vnindex_5state_dt5g_kaffa` AS k
JOIN `lithe-record-440915-m9.tav2_bq.vnindex_5state_dt5g_live`  AS t USING (time)
WHERE k.state != t.state
ORDER BY k.time DESC
LIMIT 50;
```

Có dòng trả về = 2 engine đã tách → cảnh báo cho cả 2 bên.

---

## 5. Việc của MÌNH, không gửi cho họ (đề nghị Mike mở job riêng)

1. **[CAO] Lịch sử DT5G bị viết lại 71 phiên trong 1 đêm** (§3b) — truy nguyên nhân restate ở
   `ticker`/`ticker_prune` hôm 2026-07-29; cân nhắc "đóng băng" (freeze) lịch sử DT5G trước ngày T-N
   để chuỗi production tái lập được. Ảnh hưởng mọi audit/backtest trích DT5G lịch sử.
2. **[CAO] Gate fail-safe bị che** — `bq_freshness_check.sh:207` (`MAX_STATE_LAG=0`) vẫn PASS nhờ
   writer của kaffa lúc 17:12 dù publisher của mình chết. Vá bằng bằng chứng publisher-của-ta đã
   chạy (`golive_state_today.json.as_of == hôm nay`). Đã đề xuất ở job trước, **chưa duyệt**.
3. **[TB] Giám sát writer lạ** — cảnh báo khi `lastModifiedTime` của `dt5g_live` rơi ngoài
   18:30–19:05 ICT.
4. **[TB] Ghi `dt5g_live` vào `kb/data_registry/`** kèm cảnh báo 2-writer cho tới khi §4.2 xong.

---

## 6. Draft tin nhắn gửi hainguyen/bq_admin (tiếng Việt, gửi thẳng được)

> Chào anh/em team dữ liệu,
>
> Bên mình vừa phát hiện bảng `tav2_bq.vnindex_5state_dt5g_live` đang có **2 nơi ghi**: publisher
> production của bên mình (chạy ~19:01 ICT hằng ngày) và task Celery
> `tasks.market_state_tasks.update_market_regime_state` của pipeline kaffa_v2 (ghi ~17:12 ICT,
> DELETE `time >= min_time` + APPEND 5 phiên).
>
> Trước hết xin nói rõ: **code bên mình đọc đúng, không có lỗi gì ở phía các bạn** — bọn mình đã đọc
> `worker/tasks/market_state_tasks.py` + `core_utils/market_state_engines/dt5g_chain/` và đối chiếu
> số liệu: bản port DT5G của các bạn cho ra **kết quả giống hệt** bản production của bọn mình
> (0/3.135 phiên lệch, ở cả tầng base v3.4b, DT4-gate lẫn state cuối). Port rất chuẩn, kể cả chi
> tiết bọn mình tắt "easing floor" hồi 03/06.
>
> Vấn đề duy nhất là **quyền sở hữu bảng**: `vnindex_5state_dt5g_live` là bảng production mà các
> hệ thống giao dịch của bọn mình đọc, và bọn mình có một cổng an toàn kiểm tra "bảng đã cập nhật
> tới hôm nay chưa" để chặn giao dịch khi pipeline chết. Khi có writer thứ hai đẩy `MAX(time)` lên
> sớm lúc 17:12, cổng đó **luôn PASS kể cả khi publisher của bọn mình chết hoàn toàn** — tức bọn
> mình mất lớp bảo vệ. Ngoài ra trong khung 17:12–19:01 bảng mang giá trị của engine bên các bạn,
> nên nếu 2 engine có lúc nào đó lệch nhau thì rất khó truy.
>
> **Đề nghị (không cần sửa dòng code nào):** biến `MARKET_STATE_BQ_TABLE` ở
> `market_state_tasks.py:31` đã đọc từ env sẵn rồi, nên chỉ cần set trong env của Celery worker:
>
> ```
> MARKET_STATE_BQ_TABLE=vnindex_5state_dt5g_kaffa
> ```
>
> rồi tạo bảng đích 1 lần (DDL bọn mình gửi kèm bên dưới) và chạy task ops có sẵn của chính các bạn
> `sync_market_state_bigquery(min_time="2014-01-01")` để backfill. Các bạn giữ nguyên toàn bộ
> pipeline + bảng BQ riêng để query, bọn mình lấy lại quyền ghi độc nhất bảng production.
>
> ```sql
> CREATE TABLE IF NOT EXISTS `lithe-record-440915-m9.tav2_bq.vnindex_5state_dt5g_kaffa` (
>   time DATE NOT NULL, state INT64, state_raw INT64
> ) PARTITION BY time
> OPTIONS (description = 'DT5G mirror cua pipeline kaffa_v2. Ban production cua trido: tav2_bq.vnindex_5state_dt5g_live');
> ```
>
> Nếu các bạn muốn dùng **đúng con số production** của bọn mình thay vì bản tự tính, bọn mình có
> sẵn 1 scheduled query gương bảng (chạy 19:15 ICT, sau khi bọn mình publish xong ~19:03, có kèm
> `ASSERT` chặn khi bảng nguồn chưa tươi) — nói một tiếng bọn mình gửi.
>
> **Câu hỏi ngược lại:** có lý do nào bên các bạn *cần* tự tính và ghi thẳng vào đúng bảng đó không
> (ví dụ tool/report nào đang hardcode tên bảng `vnindex_5state_dt5g_live`, hoặc cần state sẵn sàng
> từ 17:12 chứ không chờ được tới 19:01)? Nếu có, cho bọn mình biết để tìm phương án khác — bọn
> mình không muốn áp đặt khi chưa nắm hết nhu cầu bên các bạn.
>
> Cảm ơn các bạn.

---

## Phụ lục — cách tái lập kiểm chứng §3

```bash
# 1. Ảnh chụp bảng production TRƯỚC mọi lượt ghi hôm nay (time-travel, tối đa 7 ngày)
bq query --use_legacy_sql=false --format=csv --max_rows=10000 \
 "SELECT * FROM (SELECT * FROM tav2_bq.vnindex_5state_dt5g_live
   FOR SYSTEM_TIME AS OF TIMESTAMP('2026-07-29T09:00:00Z')) ORDER BY time" > /tmp/snap.csv
# 2. So 3 chiều snap / bản publish hiện tại / artifact kaffa
#    /workspace/kaffa_v2/worker/gcloud_storage/preprocess/market_state/vnindex_5state_dt5g.csv
#    (cột state_id=final, base_state_dt4=DT4, override_state_id=v3.4b, gate_state_id=macro)
# 3. So tầng base: tav2_bq.vnindex_5state_tam_quan_v34b_clean + macro_state_live._dt_4gate()
```
