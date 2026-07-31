---
kind: bigquery-table
status: CANONICAL (lịch sử khuyến nghị/allocator theo ngày)
source: lithe-record-440915-m9.recommend_v23.status + .recommendations
group: market-state
writer: mike/agents/Mafee/push_recommend_v23_to_bq.py — bq_freshness_check.sh [pipeline-3] ~19:00 T2-T6
derived_from: data/golive_v23_status.json + deploy_golive_dt5g_v4/out/golive_v23_recommendations_<date>.csv
role: SỔ LỊCH SỬ của golive_v23 (snapshot trên đĩa bị ghi đè mỗi phiên — xem golive_v23_recommendations.md)
---

# `recommend_v23.status` + `recommend_v23.recommendations` (BQ)

**Status: CANONICAL** — đây là **nguồn lịch sử duy nhất** cho "phiên X hệ thống khuyến nghị gì,
allocator/CAPIT ở trạng thái nào". File `data/golive_v23_status.json` trên đĩa CHỈ có phiên gần
nhất (bị ghi đè), xem [`golive_v23_recommendations.md`](golive_v23_recommendations.md).

## Là gì
- `recommend_v23.status` — 1 dòng/`signal_date`: `state`/`state_name`/`source`, `w_lag_target`/
  `w_lag_current`/`alloc_band`/`band_breach`, `etf_park_frac`, `breadth_oversold`/`washout_gate`/
  `capit_fired`/`capit_size`/`capit_grind`, `dd52w`/`vn_cooling`, các đếm `n_bal`/`n_lag_upcoming`/
  `n_lag_recent`/`n_capit_basket`, cột `extra` (JSON).
- `recommend_v23.recommendations` — 1 dòng/mã/ngày: `book` (BAL/LAG/CAPIT), `ticker`, `play_type`,
  `ta`, `close`, `sector`, `weight_pct`, `status`, `extra` (JSON).
- Cả 2 partition theo `signal_date`. Project `lithe-record-440915-m9`, location `asia-southeast1`.

## Ai ghi / cadence
`mike/agents/Mafee/push_recommend_v23_to_bq.py`, gọi từ `bq_freshness_check.sh` **[pipeline-3]**
(`bq_freshness_check.sh:518`) trong cron 19:00 ICT T2-T6, ngay sau [pipeline-2]
`golive_recommend_v23.py`. **Idempotent**: mỗi lần chạy REPLACE toàn bộ partition của
`signal_date` đó (`--backfill` để push lại mọi CSV có sẵn).

## Bẫy #1 — chuỗi KHÔNG liền mạch, đừng giả định đủ ngày
Đo 2026-07-31: `status` 30 dòng (2026-06-11→07-30), `recommendations` 935 dòng (06-23→07-30).
Trong cùng cửa sổ có **36 phiên VNINDEX** ⇒ **thiếu 7 phiên** (06-12, 06-22, 06-24, 06-25, 06-29,
07-10, 07-14) và **thừa 1 dòng ngày KHÔNG giao dịch** (2026-06-14, Chủ Nhật — di sản đợt backfill
đầu 06-23). Luôn `JOIN` với lịch phiên thật (VNINDEX trong `tav2_bq.ticker`) thay vì đếm dòng.

## Bẫy #2 — cột `capit_fired` là TÊN CŨ và được GIỮ CỐ Ý
`golive` đã đổi field JSON sang `capit_signal_today` (2026-07-31) nhưng **giữ alias `capit_fired`**
chính vì cột BQ này đã có lịch sử và schema map theo đúng tên đó — đổi tên cột = mất/gãy partition
cũ. Ngữ nghĩa vẫn là "gate breadth của RIÊNG ngày đó", **không phải "đang giữ CAPIT"**.

## Bẫy #3 — field mới rơi vào `extra`, không tự thành cột
`STATUS_KNOWN_FIELDS` trong writer là danh sách cứng; mọi key JSON ngoài danh sách bị gom vào cột
`extra` (JSON). Nên `capit_signal_today` và cả cụm `capit_episode_*` (từ 2026-07-31) nằm trong
`extra`, truy vấn bằng `JSON_VALUE(extra, '$.capit_episode_open')`. Muốn lên cột riêng phải sửa
schema + `STATUS_KNOWN_FIELDS` (và backfill), không tự động.

## Bẫy #4 — có đường FALLBACK parse từ MD
Khi status JSON không khớp `signal_date` cần push, writer **parse từ file MD** bằng regex
(`WASHOUT GATE FIRED`, `size = **x**`, `Oversold breadth: **x%**`…) và đánh dấu
`extra._status_source = "parsed_from_md"`. Dòng như vậy nghèo field hơn và phụ thuộc văn bản MD —
kiểm tra `extra` trước khi dùng một ngày cũ làm bằng chứng.

## Bẫy #5 — `n_capit_basket` là RỔ TÍNH LẠI của ngày đó, KHÔNG phải vị thế đang giữ
Chuỗi thật 07-20→07-28: 5 → 5 → 4 → 4 → 3 → 3 → 3, rồi 07-29 về 0 khi gate tắt — trong khi vị thế
THẬT vẫn nguyên 5 mã. Lịch sử BQ trả lời "tín hiệu ngày đó nói gì", **không** trả lời "đang giữ
gì". Câu hỏi đang-giữ ⇒ [`capit_episode.md`](capit_episode.md) hoặc vị thế broker DNSE.

↩ [Nhóm market-state](index.md)
