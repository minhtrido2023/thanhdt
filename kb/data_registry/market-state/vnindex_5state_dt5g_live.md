---
kind: bigquery-table
status: CANONICAL
source: tav2_bq.vnindex_5state_dt5g_live
group: market-state
aka: DT5G production
writer: macro_state_live.py → publish_gated_state.py → state_publish_immutable.py (daily_refresh_v34b_linux.sh, cron 18:30 ICT)
writer_2: pipeline kaffa_v2 của TEAM DỮ LIỆU (~17:12 ICT) — writer ĐỘC LẬP, KHÔNG phải của ta, KHÔNG can thiệp
write_contract: APPEND-ONLY + recompute đuôi 25 phiên (BẤT BIẾN, từ 2026-07-30)
columns: time, state, state_raw, asof_date
monitor: mike/bin/dt5g_writer_watch.py (2 mẫu/ngày: daily_refresh [0-pre] 18:30 + bq_freshness_check 19:00)
---

# tav2_bq.vnindex_5state_dt5g_live

**Status: CANONICAL**

## Là gì
Trạng thái thị trường PRODUCTION (DT-gate + macro gate, 49 transitions).

## Ai ghi / cadence
`macro_state_live.py` → `deploy_golive_dt5g_v4/publish_gated_state.py` →
`state_publish_immutable.py`, trong `daily_refresh_v34b_linux.sh` step [12], cron 18:30 ICT
(dời từ 23:15, 2026-07-10).

## HỢP ĐỒNG GHI — BẤT BIẾN (từ 2026-07-30, job `Taylor_20260730_013951`)
**State của một phiên ĐÃ CÔNG BỐ là SỰ KIỆN ĐÃ XẢY RA, không phải ước lượng được cập nhật.**
Publisher chỉ được: (a) append phiên mới; (b) recompute đuôi **25 phiên giao dịch** chưa chốt;
(c) **KHÔNG BAO GIỜ** ghi đè phiên đã chốt (`time <= cutoff`, cutoff = phiên thứ 26 từ cuối).
Bảo đảm là CẤU TRÚC: MERGE có cả 3 nhánh bị chặn bởi `time > cutoff`, + checksum MD5 vùng đã
chốt so trước/sau mỗi lần ghi (lệch ⇒ abort + alert). Trước 2026-07-30 là `bq load --replace`
(đè toàn bộ mỗi đêm) — nguyên nhân 101 phiên lịch sử bị viết lại im lặng ngày 2026-07-29.

- **Cột `asof_date`** = ngày GIÁ TRỊ của dòng đó được ghi/đổi lần cuối (không phải ngày chạm gần
  nhất). Dòng đã chốt giữ `asof_date` vĩnh viễn. Toàn bộ lịch sử hiện có được backfill
  `asof_date = 2026-07-30` = baseline đóng băng tại thời điểm triển khai.
- **Muốn bản tính mới của lịch sử** (sau backfill/restate upstream): chụp **vintage** riêng
  (`snapshot_vintage()` → `vnindex_5state_dt5g_live_vintage_<YYYYMMDD>`), **đừng đè bảng công bố**.
- Telemetry `n_sealed_diff` (số phiên đã chốt mà bản tính mới KHÁC bản công bố — tức số phiên
  `--replace` cũ SẼ âm thầm viết lại) được ĐẾM + alert, KHÔNG áp dụng:
  `data/immutable_publish_history.jsonl`.

## ⚠️ HAI WRITER ĐỘC LẬP — ta CHỈ TIÊU THỤ + GIÁM SÁT (user quyết 2026-07-31)
Bảng này **không do một mình ta ghi**:

| Writer | Là ai | Khi nào | Ghi gì |
|---|---|---|---|
| **Của ta** | `publish_gated_state.py` → `state_publish_immutable.py` | ~18:35 (daily_refresh step [12]) **và** ~19:01 (bq_freshness [pipeline-1]) | MERGE bất biến: append phiên mới + recompute đuôi 25 phiên |
| **kaffa_v2** (TEAM DỮ LIỆU) | `/workspace/kaffa_v2/worker/tasks/market_state_tasks.py`, task `update_market_regime_state` | ~17:12 ICT trong EOD pipeline của họ | DELETE `time >= min_time` + APPEND **5 phiên gần nhất**, tính bằng **implementation DT5G RIÊNG của họ** |

kaffa_v2 wire auto-sync từ commit `c794dd1` (2026-06-08) vì họ tưởng bảng không có owner tự
động ("the table is manually maintained and is stale"); họ **không biết** ta có publisher.
Truy vết đầy đủ: `mike/agents/Winston/dt5g_live_second_writer_20260729.md`.

**QUYẾT ĐỊNH CỦA USER (2026-07-31, phương án B — job `Winston_20260731_014953`):** team dữ liệu
tự quản writer của họ theo cách của họ. Ta **KHÔNG** yêu cầu họ đổi bảng đích, **KHÔNG** sửa gì
trong hệ thống của họ, **KHÔNG** tự tắt job của họ. Ta chỉ **ĐỌC/DÙNG bảng + kiểm tra kết quả +
BÁO team dữ liệu khi có sự cố**.

Hệ quả kỹ thuật phải nhớ:
1. **MAX(time) của bảng KHÔNG chứng minh publisher của ta còn sống.** kaffa đẩy
   `MAX(time)=hôm nay` lúc 17:12, nên mọi gate freshness kiểu `MAX(time)` đều PASS kể cả khi
   chuỗi của ta chết sạch. `bq_freshness_check.sh` từ 2026-07-31 gate bằng **BẰNG CHỨNG
   publisher của ta** (`golive_state_today.json`: `as_of` == phiên gần nhất + `bq_publish_ok` +
   mtime hôm nay) — file local đó writer ngoài không ghi được.
2. **Cửa sổ 17:12 → 18:35 bảng mang giá trị của engine kaffa.** Consumer production thật
   (`golive_recommend`, `pt_v4_dt5g`, `dna_report`, `recommend_tomorrow`, plan T+1) đều chạy
   **sau 19:00** nên không bị ảnh hưởng — nhưng script chạy tay trong cửa sổ đó thì có.
3. **Hai engine KHÔNG bit-identical**: đo 2026-07-29 trên 3.134 phiên chung → **27 phiên lệch
   `state` (0,86%)** (2017-12-05→12-25 là cụm dài nhất, 15 phiên) + 1 phiên lệch riêng
   `state_raw`. Trùng khớp hằng ngày là **may**, không có bảo đảm cấu trúc.
4. **Dấu vân tay writer ngoài = `asof_date IS NULL`.** Publisher của ta luôn ghi `asof_date`, và
   MERGE chỉ cập nhật nó khi GIÁ TRỊ đổi (`state IS DISTINCT FROM`) — nên dòng do kaffa INSERT mà
   giá trị trùng ta sẽ giữ `asof_date = NULL` vĩnh viễn. Đo 2026-07-31: đúng **5 dòng cuối
   (07-24→07-30) NULL** = đúng 5 phiên kaffa append. ⇒ Ai đọc `asof_date` để suy ra provenance
   phải biết NULL ở đuôi là **bình thường** trong kiến trúc 2-writer này; NULL ở vùng **đã chốt**
   mới là báo động (lịch sử bị viết lại).

**Giám sát (không chặn gì):** `mike/bin/dt5g_writer_watch.py`, chạy 2 lần/ngày — `pre-publish-1830`
(đầu `daily_refresh_v34b_linux.sh`, mẫu DUY NHẤT còn thấy dấu vết kaffa vì `lastModifiedTime`
chỉ giữ lần ghi cuối) và `bq-freshness-19h`. Đo: lớp writer theo cửa sổ giờ · `asof_date` NULL ·
dòng trùng `time` · **diff giá trị bảng vs `data/vnindex_5state_dt5g_live.csv` (bản ta công bố)**.
Tầng báo: HIGH (Telegram+Discord+bus `error`) khi ≥1 phiên lệch `state` / dòng đôi / NULL vùng đã
chốt; WARN (Discord+bus) khi ghi ngoài mọi cửa sổ đã biết hoặc lệch `state_raw`; QUIET (chỉ log
`data/dt5g_writer_watch.csv`) cho kaffa ghi đúng giờ + giá trị khớp — cố ý KHÔNG ping mỗi ngày.
**HIGH = báo team dữ liệu, không tự sửa.**

## Bẫy
Đây là nguồn ĐÚNG duy nhất cho production state. Hai điểm cần biết:
1. **Vùng đuôi 25 phiên VẪN đổi được** (đúng thiết kế — state chưa chốt vì DT-gate cần `enC/enX`
   = 25 phiên mới commit). Đừng coi giá trị của 25 phiên gần nhất là bất biến.
2. Cột `asof_date` thêm 2026-07-30 ⇒ `SELECT *` giờ trả 4 cột (`sync_bq_cache.py` cache cả 4).
   Consumer nên nêu tên cột tường minh.
