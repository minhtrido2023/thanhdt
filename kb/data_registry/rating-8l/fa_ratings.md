---
kind: bigquery-table
status: CANONICAL
source: tav2_bq.fa_ratings
group: rating-8l
note: ĐANG REFRESH ĐỊNH KỲ (hết static từ 2026-07-12)
builder: fundamental_rating.py (repo root); refresh refresh_fa_ratings.py qua mike/bin/refresh_fa_ratings.sh
writer: cron weekly thứ Bảy 09:15 ICT + cron TẠM T3 20:45 ICT đến hết 2026-08-04
---

# tav2_bq.fa_ratings

**Status: CANONICAL, ĐANG REFRESH ĐỊNH KỲ** (hết static từ 2026-07-12)

## Là gì
Panel tier A–E legacy (thang cũ, per-quarter percentile, 7 trục
Quality/Stability/Cash/Shareholder/Growth/Health/Valuation, weights 18/18/18/15/13/8/10) — vẫn là
input PRODUCTION: `SIGNAL_V11.sql` (`fa_tier` của book BAL), `pt_v22_dt5g.py`, `pt_v23_audit_2014.py`
+ ~50 script research.

## Ai ghi / cadence
**Builder = `fundamental_rating.py`** (repo root, KHÔNG mất — sửa lại 2026-07-11, ghi nhầm trước đó vì
tên không theo pattern `build_fa_ratings_*`). Refresh = **`refresh_fa_ratings.py` (append-only: frozen
quarters không đụng, 2 quý mở re-rank, quý mới append khi cohort ≥30) qua wrapper
`mike/bin/refresh_fa_ratings.sh`**, cron **weekly thứ Bảy 09:15 ICT ĐÃ CÀI + identity fix `a9716f6`
(source `wc_env.sh`) + test ghi THẬT 2026-07-12 OK: lastModified 07-12, 12.406 rows, invariant 48/48
quý đóng băng giữ nguyên** (quant-skeptic CONFIRMED — hết câu hỏi treo, lần scheduled đầu 07-18 chỉ là
chạy bình thường). Mùa BCTC Q2: thêm cron TẠM T3 20:45 ICT đến hết 2026-08-04 (job
Winston_20260713_103213, xem `cron_registry.md`).

## Bẫy
2 bẫy: (1) **name-alike với `fa_ratings_8l`** nhưng KHÁC thang đo (A–E vs rating 1–5/tier) và khác
spec — đổi lẫn nhau làm lệch mọi as-of join; (2) quý mới chỉ vào khi cohort ≥30 mã (đầu mùa BCTC,
as-of join "kéo dài tier cuối" của quý trước cho tới lúc đó — đúng thiết kế, không phải staleness).
**2026-07-11 feasibility (Taylor job Taylor_20260711_145129)**: lineage 100% khớp (12.367/12.367 rows
đối chứng `data/fundamental_rating_all.csv`), reproduction test chạy lại builder hôm nay = 82.3% exact
tier / 99.9% ±1 bậc (18% lệch do adjusted-Close hồi tố, không phải lỗi formula), phủ tới 2026-07-08
(gồm 2026Q2) → rebuild + append-only refresh KHẢ THI. **2026-07-11 cơ chế refresh ĐÃ XÂY + dry-run
verified (job Taylor_20260711_153405)**: frozen match 82.51% exact / 99.98% ±1 (floor abort 70%/99%),
publish = DELETE 2 quý mở + INSERT trong 1 transaction (frozen rows không bị rewrite byte nào), quý
mới cohort <30 chưa append (chặn tier-A giả từ cohort 1 dòng); staging table
`tav2_bq.fa_ratings_refresh_staging` (chỉ refresh dùng, đừng đọc). Freshness WARN-only đã wire vào
`bq_freshness_check.sh` + `data_registry_audit.sh`.
