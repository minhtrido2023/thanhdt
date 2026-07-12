# Audit dọn dẹp cron paper-trading lạc hậu — 2026-07-12
Job: `Winston_20260712_151206` (dispatch từ Mike, sau audit cron-order `Winston_20260712_142100`)
Phương pháp: đọc crontab thật + code thật từng script, grep consumer từng output (không đoán),
đối chiếu `mike/kb/paper_programs_registry.json` (nguồn chuẩn tắc các chương trình paper) +
`mike/kb/data_registry.md`. READ-ONLY — không sửa gì.

## KẾT LUẬN TỔNG (TL;DR)
**Bề mặt cron đã SẠCH hơn kỳ vọng — chỉ có 1 dòng diff cần áp: xóa dangling comment trong crontab.**
Lý do không có thêm ứng viên xóa:
1. Các dự án vừa đóng (V2.5, Q-sleeve, DVR-8L, momentum-deals, fa8l re-tune) **chưa bao giờ có cron
   riêng** — toàn bộ chạy qua dispatch/backtest ad-hoc. Không có gì để gỡ.
2. Đợt dọn zombie đã làm trước đó 2 lần (2026-06-16 gỡ V121 ensemble; 2026-07-07 commit `94b51a7`
   retire 6 step [15][16][18][23][24][25]) — các block RETIRED còn nguyên đúng pattern.
3. Các sim "trông cũ" (pt_v11/pt_v12/pt_v4/compare) hóa ra là **control arms có chủ đích** của panel
   `engine_room_oos` trong registry (v2, updated 2026-07-07): "V11/V12/V4 giữ chạy làm control arms
   (chi phí ~0)", review date 2026-12-01 — validation liên tục cho lựa chọn V2.4, render hàng ngày
   15:20 vào Trading report. Đây là quyết định đã ghi, không phải rác vô chủ.

## A. Crontab — verdict từng dòng liên quan paper/research

| Dòng cron (ICT) | Verdict | Phân loại | Bằng chứng |
|---|---|---|---|
| 15:30 `papertrade_daily.sh` | **GIỮ** | (a)+(c) | xem mục B từng step |
| 17:45 `pt_8l_daily.sh` | GIỮ | (c) production | 9 step đều là 8L production chain (rating→screener→dna→alerts→sector_lens); không step nào thuộc R&D đã đóng |
| 18:00 `telegram_run_daily.sh` | GIỮ | (c) | Telegram BA-system production |
| 06:00 `newdeals_daily_report.py` | GIỮ | (a)+(c) | AlphaLens paper (active tới 2026-09-30, registry) + Golden/Strong watchlist monitor |
| 15:05 `dc_book_waterfall_paper.py` | GIỮ | (a) | trial mở, event-anchored (registry: trần 2026-10-06) |
| 15:20 `paper_programs_daily_report.sh` | GIỮ | (c) | render registry — kênh duy nhất của ORB sau khi gỡ section Telegram 07-07 |
| Block "Paper main probe harness" (7 dòng: 08:52/09:10/10:46/11:32/13:05 + 2 early-check) | GIỮ | (a) | evidence cho EXTREME (target ~2026-08-03) + vol-scale (~07-20) + fill-timing (~07-31) — cả 3 đều DANG CHẠY theo dispatch |
| Sat 08:30/09:15 `refresh_fa_ratings_8l.sh`/`refresh_fa_ratings.sh` | GIỮ | (c) | production dependency (dispatch ghi rõ không đụng) |
| Feeds: vcb_fx 08:15, hog Mon 09:00, rubber 18:35, WB commodity d5/d10, new_listings 18:10, shares 18:40, SBV Fri | GIỮ | (c) | data-ops feeds, input DT5G macro/corp-action |
| `# V2.4 go-live flip (one-shot 2026-07-01)` | **XÓA** | (d) | dangling comment, không có lệnh theo sau (dòng kế là separator Discord section) — one-shot đã chạy xong từ 07-01 |

Không có systemd user timer nào (`systemctl --user list-timers` = 0). Không tìm thấy scheduler nào
khác ngoài crontab user `trido`.

## B. papertrade_daily.sh — verdict từng step

| Step | Verdict | Phân loại | Bằng chứng (consumer thật) |
|---|---|---|---|
| [1] pull_us_market | GIỮ | (c) | `us_market_history.csv` = Pillar B (VIX/SPX) của DT5G macro gate — production |
| [2] refresh_lagged_caches | GIỮ | (c) | pkl fresh-daily = nguồn identity/NP_R của `lag_live_schedule.py` (fix R1 CRITICAL hôm nay `f7463e3`) — dừng là giết LAG live |
| [3] snapshot_state_vintage | GIỮ | (c) | vintage PIT snapshot cho audit point-in-time; rẻ |
| [4] macro_healthcheck | GIỮ | (c) | ghi `data/macro_health.json` → `get_gated_state()` fail-safe production |
| [6] custom30_history (blend→`custom30_8l`) | GIỮ | (c) | quyết định "kept for audits" ghi trong chính fix `e02a75b` (07-11); `bq_freshness_check.sh` đang BLOCK content-age + WARN writer-alive trên bảng này (dừng writer = tự gây alert giả); sync_bq_cache mirror; audit scripts đọc. Muốn retire phải là thay đổi phối hợp (Taylor), không phải cron cleanup |
| [6b] custom30v_history (yieldcombo→`custom30v_8l`) | GIỮ | (c) | **PRODUCTION** parking basket writer (revive 07-11); dừng = time-bomb rebal 08-05 |
| [7] pt_v11_tq34b | GIỮ | (a/c) | control arm `engine_room_oos` (registry, review 2026-12-01) |
| [8] pt_v12_macro | GIỮ | (a/c) | control arm `engine_room_oos` |
| [11] pt_v4_dt5g | GIỮ | (a/c) | control arm + vừa được cập nhật trong chính commit đóng MOM `4fbd492` hôm nay (được maintain chủ động) |
| [12] pt_v22_dt5g (V2.3) | GIỮ | **(c) PRODUCTION** | `trading_bot/strategies.py` đọc `pt_v22_dt5g_open_positions.csv` để build plan THẬT; registry ghi "KHÔNG BAO GIỜ retire khi V2.4 còn live" |
| [14] papertrade_compare | GIỮ | (c) | ghi `papertrade_compare5.csv` = data source của probe `engine_room_oos` (report 15:20 hàng ngày). Consumer chết khác (dt4_decision_review/vol_spike/pt_sleeve_allocator) đã unscheduled/retired rồi |
| [17] orb_pt | GIỮ | (a) | trial MỞ theo registry: điều kiện kết thúc là REGIME (≥60 phiên gồm chop/bear), không phải deadline; report 15:20 là kênh duy nhất. Known-flaky (FAIL 07-10 vnstock ConnectionError) — đã có FAIL-alert cuối chain từ 07-11 |
| [19] crisis_alert_push | GIỮ | (c) | còi Telegram washout — alert vận hành, chỉ kêu khi WATCH/STRONG |
| [20] pt_capitulation_shadow | GIỮ | (a) | trial event-driven MỞ + chính là điều kiện tái xét (a) của V2.5 ("tích lũy episode capitulation qua theo dõi S2 trên paper") — V2.5 NO-GO càng cần giữ cái này |
| [21] fetch_bdi_daily | GIỮ | (c) | BDI feed (Winston) |
| [22] edge_health_monitor --refresh | GIỮ | (c) | input cơ chế w_LAG 50/65 vừa fix (`a776a9a`). ⚠️ xem finding F2 dưới |
| [26] phosphorus_dgc_weekly (Fri) | GIỮ | (c) | DGC special-situation monitor — DGC = 47.2% NAV ZaloPay (vị thế legacy excluded), case Taylor còn sống (target 70-75k/12-18 tháng) |
| Block comment RETIRED [15][16][18][23][24][25] | GIỮ NGUYÊN | — | đúng pattern archive-không-xóa |

## C. Các mục Mike hỏi đích danh

1. **`pt_v12_live.py`** — XÁC NHẬN không nằm trong bất kỳ cron/script sống nào trên Linux:
   không có trong crontab, không có trong `papertrade_daily.sh` (đã gỡ từ thời `.bat`, ghi chú
   "Removed pt_v12_live" trong cả `papertrade_daily.bat` lẫn `papertrade_compare.py`). Chỉ còn
   được đọc bởi `papertrade_weekly_report.py`/`papertrade_milestone_report.py` — 2 script này
   cũng KHÔNG được schedule trên Linux (chỉ có wrapper trong `server_cron/` legacy + `.bat`
   Windows-era, cả 2 không được crontab gọi). Output frozen mtime 2026-05-27.
   → **Không có dòng cron nào để xóa cho nó** — nó đã chết đúng như current_ops ghi, không cần action.
2. **Dangling comment go-live flip** — xác nhận, xóa an toàn (diff duy nhất).
3. **`server_cron/`** (20 file wrapper) — legacy migration-era, không được crontab hay script sống
   nào gọi (chỉ tự tham chiếu nội bộ). Archive-in-place theo guidelines §10, không action.

## D. Finding phụ (ngoài scope diff, chuyển đúng chỗ)

- **F1 — Sự kiện retire tương lai (event-anchored, ĐỪNG làm bây giờ):** khi cả vol-scale
  (~07-20), fill-timing (~07-31) và EXTREME (~08-03) đóng sổ + user sign-off, block "Paper main
  probe harness" (7 dòng cron) + cron 08:52 plan generator trở thành ứng viên retire nguyên khối.
  Đề nghị Mike ghi mốc theo dõi thay vì đụng bây giờ (EXTREME cần harness chạy tới cùng).
- **F2 — Bằng chứng cho job lag_edge_health đang mở (dispatch riêng của Mike):** step [22]
  `edge_health_monitor.py --refresh` ĐÃ nằm trong lịch daily (papertrade 15:30, tồn tại từ trước
  baseline 06-21) và chạy `[ok]` ngày 07-10 — nhưng `data/lag_edge_health.csv` content vẫn dừng
  2026-05-11 (mtime 07-12 tươi). Tức mệnh đề "không có lịch refresh tự động" trong current_ops
  KHÔNG chính xác về mặt cron — **cron có rồi; bug nằm TRONG script** (`--refresh` chỉ re-pull
  panel IC hàng tháng, không catch-up chuỗi LAG edge). Việc "wire cron" của dispatch kia là thừa;
  việc thật là sửa logic refresh. Cross-ref cho agent nhận job đó.
- **F3 — Comment lỗi thời:** `sync_bq_cache.py:180` vẫn ghi "custom30_8l = the production table
  golive_recommend_v23.py reads" — sai từ fix `e02a75b` 07-11 (production đọc `custom30v_8l`).
  Doc-only, 1 dòng, sửa lúc nào tiện.
- **F4 — orb_pt flaky:** FAIL exit 1 ngày 07-10 (pattern vnstock ConnectionError đã biết, 4/8 phiên
  trước audit 07-11). FAIL-alert cuối chain đã hoạt động — không cần action mới, chỉ ghi nhận tần suất.

## E. DIFF ĐỀ XUẤT (duy nhất, chờ Mike áp)

**Crontab** — xóa 1 dòng comment (không có lệnh nào bị ảnh hưởng):
```diff
-# V2.4 go-live flip (one-shot 2026-07-01)
```
(nằm ngay sau dòng `sync_bq_cache_daily.sh`, trước separator "Discord<->Claude bot supervisor")

**papertrade_daily.sh** — KHÔNG sửa gì. Mọi step còn lại đều map về production dependency hoặc
trial đang mở theo registry.
