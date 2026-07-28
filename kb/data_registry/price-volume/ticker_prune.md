---
kind: bigquery-table
status: TRAP
source: tav2_bq.ticker_prune
group: price-volume
issue: đã thay bằng universe_pit cho mọi cổng quyết định (cutover 2026-07-22)
risk_type: silent drift (trôi dần), KHÔNG phải frozen
writer: bq_admin (3 đường ghi độc lập, ngoài tầm kiểm soát team Mike)
---

# tav2_bq.ticker_prune

**Status: ⚠️ TRAP cho code MỚI — đã thay bằng `universe_pit` cho mọi cổng quyết định** (cutover chính thức 2026-07-22, xem [`universe_pit.md`](universe_pit.md) / [`universe_pit_quality.md`](universe_pit_quality.md))

## Là gì
Universe cũ cho backtest + chọn rổ, **KHÔNG còn là nguồn khuyến nghị**. bq_admin xác nhận (QA
`agents/Taylor/research/ticker_prune_universe_QA_bq_admin_20260722.md`): không tồn tại hệ quản trị
universe — bảng bị ghi bởi 3 đường độc lập (rebuild `WRITE_TRUNCATE` từ `hit_ticker_list.csv` 453 mã
thủ công / daily append cửa sổ 7 ngày từ `ticker_list.csv` / per-ticker replace toàn lịch sử
event-driven theo BCTC). Bộ lọc thật = `Volume_3M_P50*Price/Inflation_7 > 1e9`.

## Ai ghi / cadence
3 đường ghi trên vẫn ĐANG CHẠY (bq_admin, ngoài tầm kiểm soát team Mike) — bảng KHÔNG đứng yên.

## Bẫy
⚠️ **RỦI RO KHÁC với file đông cứng đã gặp trước đây (vụ `ticker_prune.parquet` monolith đóng băng
06-26): đây là "trôi dần" (silent drift), không phải "chết đứng" (frozen).** Một file đông cứng dễ
bắt (mtime cũ, staleness-check báo ngay). `ticker_prune` thì NGƯỢC LẠI — vẫn được ghi liên tục,
`mtime`/freshness-check vẫn "xanh" mỗi ngày, nên KHÔNG có tín hiệu nào tự động báo "bảng này đang
lệch dần khỏi `universe_pit`". Nó chỉ càng ngày càng khác `universe_pit` vì: circular-selection-bias
(`hit_ticker_list` suy từ chính kết quả backtest cũ), lịch sử bị ghi đè âm thầm (đo được +10.630 dòng
2014-2025 trong 8 ngày), và không tái lập point-in-time (`n_union` một mốc lịch sử đã tự trôi 459→381
chỉ trong vài ngày quan sát). **Code còn đọc bảng này sẽ không báo lỗi gì cả — chỉ lặng lẽ cho số
khác `universe_pit` ngày càng nhiều, đúng kiểu lỗi khó phát hiện nhất.** 496 chỗ trong repo từng viết
`IN (SELECT DISTINCT ticker FROM ticker_prune)` KHÔNG có điều kiện time (look-ahead 1,6-2,6×) — hầu
hết là research/backtest có TRƯỚC dự án migrate, KHÔNG bắt buộc sửa hết ngay, nhưng auto-cảnh giác:
**bất kỳ code MỚI nào cần universe/liquidity filter → PHẢI dùng `universe_pit`/`universe_pit_quality`,
KHÔNG viết mới tham chiếu `ticker_prune`.** **2 consumer LIVE còn lại có chủ đích, đã ghi rõ điều kiện
gỡ** (audit đầy đủ 2026-07-22, dispatch job Mike): (a) `golive_recommend_v23.py:215` (CAPIT pool
selection) + `:354` (CAPIT ADV cap) — ghim chờ (i) `capit_fired` về false VÀ (ii) quyết định riêng về
sàn thanh khoản pool (ADV thay vì turnover-1-ngày); (b) `trading_bot/executor.py:588-603` đọc cache
`ticker_prune` cho 3 tính năng R&D (`gap_adaptive_enabled`/`extreme_regime_enabled`/
`chase_cap_vol_scale_enabled`) — **hiện TẮT trên cả SpaceX/ZaloPay** (chỉ bật ở account paper), nhưng
đang trên lộ trình lên live — **PHẢI migrate executor.py sang `universe_pit` TRƯỚC KHI bật bất kỳ cờ
nào trong 3 cờ này cho live**, đây là gap MỚI phát hiện, chưa nằm trong 4 phase P1-P4 migration gốc.
Vẫn cần giữ freshness-monitoring của `ticker_prune` (`preflight_check.sh`/`bq_freshness_check.sh`)
chừng nào 2 consumer live trên còn tồn tại.
