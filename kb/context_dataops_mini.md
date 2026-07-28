# Mike fleet — context data-ops (Winston headless dispatch)
> Phần CHUYÊN BIỆT cho vận hành dữ liệu/pipeline — không lặp lại safety core (đã import
> riêng ở CLAUDE.md), không có chi tiết chiến lược trading (việc của Taylor/DollarBill).
> Cần domain khác (chiến lược/thực thi/pháp lý)? Đọc `kb/context_pack.md` qua Read tool
> nếu tự tin đúng chỗ, hoặc escalate Mike — đừng đoán.

## BigQuery cốt lõi
Project `lithe-record-440915-m9`, dataset `tav2_bq` (region `asia-southeast1`).
```
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 'SQL'
```
Bảng hay chạm: `ticker` (daily OHLCV+indicator), `ticker_prune` (universe chất lượng, dùng cho
freshness/breadth), `ticker_financial` (quý), `ticker_1m` (rolling snapshot live).

## DT5G — bảng production, KHÔNG nhầm với base (bẫy đã gây sự cố thật)
Production = `tav2_bq.vnindex_5state_dt5g_live` (qua `get_gated_state()`). Bare
`tav2_bq.vnindex_5state` = v3.4b BASE (không DT-gate/macro-cap, ~153 transitions) — KHÔNG phải
DT5G (~49 transitions). `publish_gated_state.py` PHẢI đọc live BigQuery, KHÔNG được đi qua
`BQ_LOCAL_CACHE` (env kế thừa từ `wc_env.sh`) — sự cố thật 2026-07-12, publish step đọc cache
T-1 khiến freshness gate `MAX_STATE_LAG=0` fail cứng; fix = `os.environ.pop('BQ_LOCAL_CACHE')`
process-local trước import, KHÔNG sửa `wc_env.sh` (sẽ hỏng mọi script khác cần cache).

## Trước khi wire nguồn dữ liệu mới hoặc sửa cron — TRA REGISTRY TRƯỚC
- `mike/kb/data_registry/` (bắt đầu ở `index.md`) — mọi bảng/file có status CANONICAL/TRAP/DEPRECATED,
  1 nguồn = 1 file (cấu trúc OKF, migrate 2026-07-28). Bẫy đã biết: đọc nhầm bảng regime base thay vì
  DT5G (trên); nguồn không có trong registry → xác minh trước khi coi là an toàn, đừng suy đoán từ tên
  bảng "nghe hợp lý". (`kb/data_registry.md` giờ là stub redirect.)
- `mike/kb/cron_registry.md` — trước khi thêm/sửa lịch cron, trả lời 4 câu hỏi bắt buộc (đọc gì+
  vintage, nguồn tươi lúc nào — ĐO THẬT không tin comment, cần T hay T-1, ai tiêu thụ+deadline).

## BQ local cache sync (`sync_bq_cache_daily.sh`, 23:45 ICT)
Phần lớn incremental/delta theo `WHERE time > max_cached` hoặc year-chunking (`ticker`,
`ticker_prune`). 3 ngoại lệ CỐ Ý full_only: `fa_ratings`/`fa_ratings_8l` (bảng nguồn bị
DELETE+INSERT re-rank mỗi tuần — delta sẽ bỏ sót lần rewrite) và `ticker_1m` (rolling snapshot,
không phải append-only). Đừng "tối ưu" 3 bảng này thành delta mà không hiểu lý do full_only.

## Khi archive 1 file thành canonical (coding_guidelines §10)
Khi xác nhận 1 script là bản canonical cho 1 mục đích, CÙNG lúc: grep toàn repo xác nhận không
còn caller nào dùng bản cũ, `git mv` bản cũ vào `archive/` (không `rm`), cập nhật file nguồn tương ứng
trong `data_registry/` đánh dấu DEPRECATED + trỏ tới bản thay thế.

## Same-day pricing — DNSE API, KHÔNG BigQuery
BQ chỉ sync qua đêm 23:45 ICT — bất kỳ check freshness/giá "hôm nay" chạy TRƯỚC giờ đó đọc BQ sẽ
luôn là dữ liệu hôm qua. Freshness check tự thân dùng BQ (đúng việc của nó — kiểm tra BQ đã sync
chưa), nhưng đừng lẫn với việc cần giá LIVE (đó là việc của DollarBill/Mafee qua DNSE API).
