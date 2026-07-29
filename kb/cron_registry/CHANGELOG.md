---
kind: changelog
group: _rules
title: Log thay đổi Cron Registry
note: >
  Đây là changelog BIÊN TẬP của lịch cron (dòng nào thêm/xoá/đổi giờ, ai làm, job nào, 4 câu hỏi
  §11 đã trả lời) — provenance + audit trail §11, KHÔNG phải narrative sự cố. Sự cố live-workflow
  ghi ở kb/INCIDENTS.md (C1 vintage-mismatch 2026-07-12; send_plan re-dispatch 2026-07-13). Mục cũ
  nhất ở dưới cùng.
authority_note: >
  CURRENT-STATE của mỗi cron = BẢNG CHÍNH (../cron_registry.md), KHÔNG phải changelog này. Đặc biệt
  entry 08:10 ngày 3 (refresh_deposit_rate_vn.sh): 2 mục 2026-07-20 dưới đây kể lại quá trình bật
  cơ chế auto-write; NHƯNG trạng thái HIỆN TẠI (bảng chính) = auto-write ĐÃ BỊ LOẠI BỎ, người thật
  chạy `append_deposit_rate.py --source manual_verify`. Khi mâu thuẫn → tin bảng chính. Full detail
  + review đối kháng deposit-rate: kb/projects/deposit-rate-autocheck.md.
preserve_verbatim: >
  Cố ý KHÔNG nén-semantic các mục dưới (theo tiền lệ data_registry/CHANGELOG.md + guardrail "đừng
  cắt cảnh báo an toàn nào"): mỗi mục chứa audit-trail §11 (4 câu hỏi/job) + buffer đo thật + gate
  formula — load-bearing, không phải fluff. Chỉ thêm pointer INCIDENTS.md, giữ nguyên nội dung.
---

# Log thay đổi Cron Registry

- 2026-07-29 (Winston, job `Winston_20260729_103816` — user yêu cầu "dời TẤT CẢ paper report/pipeline
  sang 19:00 để có dữ liệu cuối ngày"): **CÀI MỚI `mike/bin/paper_late_feeds.sh` 20:05 ICT** (`5 13 * * 1-5`),
  tách `[19] crisis_alert_push` ra khỏi `papertrade_daily.sh` 15:30 và chạy LẠI `[21] fetch_bdi_daily`.
  **KHÔNG dời chuỗi 15:30** — yêu cầu gốc đã kiểm chứng và bác bỏ một phần: đo thật cho thấy 11/15 step
  active đọc `BQ_LOCAL_CACHE` (`data/bq_cache/*.parquet`, chỉ sync 23:45) nên thấy T-1 dù chạy 15:30 hay
  19:00 — dời chỉ làm báo cáo muộn hơn mà không tươi hơn. Bảng phân loại A/B/C từng step + sơ đồ thứ tự:
  [papertrade_daily_steps.md](papertrade_daily_steps.md).
  4 câu hỏi §11 cho dòng mới:
  (1) *Đọc gì + vintage*: `[19]` query BQ **LIVE** (`ticker_prune` JOIN `dt5g_live` qua `dna_report._bq`
  subprocess, KHÔNG qua cache) → asof = min(2 bảng); `[21]` scrape handybulk.com, lấy ngày mới nhất trên trang.
  (2) *Nguồn tươi lúc nào — ĐO THẬT 2026-07-29*: ingest tav2 ghi xong `ticker` 17:23 / `ticker_prune` 17:17 /
  `ticker_financial` 17:21 / `ticker_1m` 16:02 ICT; `dt5g_live` có phiên T sau `publish_gated_state`
  19:00-19:03 (log: `EOD PIPELINE DONE — 19:03 ICT`). Baltic công bố ~13:00 London ≈ 19-20:00 ICT — kiểm
  chứng: chạy thử lúc 17:47 ICT vẫn chỉ lấy được 07-28.
  (3) *Cần T hay T-1*: cần **T** — `[19]` là cảnh báo capitulation cho người đọc; cảnh báo theo regime hôm qua
  là vô nghĩa đúng vào ngày cần nó nhất.
  (4) *Ai tiêu thụ + deadline*: `[19]` → user qua Telegram, cần trước `send_plan_report` 21:00 (thấy cảnh báo
  trước khi duyệt plan); `[21]` → `freight_map.py` ad-hoc, không deadline. Chọn 20:05 = sau publish 19:03
  (buffer 1h), sau `telegram_run_daily` 19:35, trước 20:30 inject + 21:00 send_plan.
  **Giữ `[21]` ở CẢ 15:30 lẫn 20:05** (không phải dư thừa): script chỉ lấy ngày MỚI NHẤT trên trang → nếu chỉ
  chạy 1 lần muộn mà hôm đó trang chưa cập nhật thì ngày đó mất vĩnh viễn; 2 lần/ngày + dedup theo `date`
  (`drop_duplicates keep=last`) = idempotent, không bao giờ thủng chuỗi.
  **KHÔNG đổi** (có lý do, đừng "tối ưu" lại): `[20] pt_capitulation_shadow` giữ ở 15:30 vì `bq_freshness_check`
  19:00 đọc `pt_capitulation_state.json` cho note CAPIT_FIRED của dispatch DollarBill (đường plan tiền thật) —
  đề xuất chuyển `[20]` vào chính chuỗi 19:00 (sau pipeline-1, trước pipeline-2) đang **chờ user duyệt**;
  `[17] orb_pt` đã asof T sẵn (vnstock live, VN đóng cửa 14:45); `[22]` panel theo THÁNG + bị 19:00 check tuổi
  file `lag_edge_health.csv`; `[1] pull_us_market` phiên US chưa mở ở mọi giờ ICT trong ngày; `[26]` dữ liệu
  theo quý. Test: chạy thật `paper_late_feeds.sh` 17:47 → rc=0, cả 2 step `[ok]`, không side-effect (DORMANT
  → không push, BDI dedup no-op). Backup crontab `/tmp/cron_bak_20260729.txt`, diff xác nhận chỉ THÊM 1 dòng.

- 2026-07-29 (Winston, job `Winston_20260729_084600` — user phát hiện report hiển thị dữ liệu cũ):
  **ĐỔI GIỜ `paper_programs_daily_report.sh --post` 15:20 → 16:00 ICT** (`20 8` → `0 9`, T2-T6).
  *Triệu chứng:* report ngày 07-29 hiển thị mục (7) Capitulation + (8) Engine-room asof **07-27**
  (trễ 2 phiên) trong khi mục (6) ORB asof 07-28 (trễ 1 phiên) — cùng nguồn `papertrade_daily.sh`.
  *Root cause = HAI lag ĐỘC LẬP cộng dồn, không phải một:* **(A)** report chạy 15:20 = **TRƯỚC**
  chain 15:30 cùng ngày → luôn đọc artifact do chain **hôm trước** ghi (+1 phiên, áp dụng cho MỌI
  mục — đây là phần đã sửa); **(B)** riêng mục 7/8, bản thân artifact được gắn nhãn T-1 vì
  `pt_capitulation_shadow.py` query BQ LIVE (`ticker_prune`/`dt5g_live`) và các sim sinh
  `papertrade_compare5.csv` chạy trên giá tới T-1 — BQ chưa có close phiên T lúc 15:30 (ingest
  ~17:30 / sync 23:45) → **sàn cấu trúc**, không sửa được nếu giữ report trong khung 15-16h. Mục 6
  KHÔNG dính (B) vì `orb_pt.py` kéo bar 1m VN30F **LIVE từ vnstock**, phiên đã đóng 14:30 → nhãn T.
  Vậy 2+1 = đúng chênh lệch quan sát được. *Sau fix:* ORB asof **T**, Capitulation/Engine-room asof
  **T-1** (sàn). Ghi chú cũ ở dòng 15:30 ("consumer = 15:20 report **hôm sau**") mô tả đúng hậu quả
  nhưng KHÔNG phải thiết kế có chủ đích — chain idempotent, không có lý do data-integrity nào bắt
  phải đọc artifact hôm trước; đã sửa thành "report 16:00 CÙNG NGÀY".
  **4 câu hỏi §11:** (1) *Đọc gì/vintage?* file artifact local do chain 15:30 ghi — `orb_pt_status.json`
  (T), `pt_capitulation_state.json` + `papertrade_compare5.csv` (T-1); không đọc BQ/cache trực tiếp.
  (2) *Nguồn tươi lúc nào?* đo thật 10 log `papertrade_run_*.log`: chain START 15:30 → DONE **15:38-15:42**
  (worst 15:42, 12'). (3) *Cần T hay T-1?* report EOD paper — cần bản MỚI NHẤT chain vừa sinh; asof=T
  chỉ khả thi cho ORB, mục BQ chấp nhận T-1 (muốn T phải dời sang sau 23:45 = đổi bản chất báo cáo).
  (4) *Ai tiêu thụ/deadline?* user đọc Discord "Trading report", không có job downstream → không
  deadline cứng. **Buffer** 15:30+12'+18' = 16:00 (policy đòi runtime + ≥10'). **Xung đột:** không có
  cron nào trong khe 15:35-16:15 ICT. **Degrade an toàn:** chain chậm bất thường → report đọc artifact
  hôm trước = đúng hành vi cũ, không tạo failure mode mới; mỗi mục tự in `asof` nên đọc ra ngay.
  Kèm theo (cùng commit): nhãn header report đổi `Data as-of: <giờ chạy>` → `Render lúc: … — vintage
  dữ liệu xem asof từng mục` (nhãn cũ dễ khiến người đọc tưởng mọi số là của hôm nay); thêm trường
  `notes` VINTAGE vào registry entry `capitulation_shadow` + `engine_room_oos` giải thích sàn T-1.
  Cron đổi giữa ngày lúc 15:49 ICT → 16:00 hôm nay VẪN nổ (không nhảy khe), report 07-29 chạy 2 lần
  (15:20 bản cũ trễ + 16:00 bản đúng) — cố ý, để xác minh fix ngay trong ngày.

- 2026-07-20 (Mike, user approved trực tiếp): sau entry gốc bên dưới, cơ chế trải qua thêm 7 vòng
  quant-skeptic REFUTED→fix (tổng 10 vòng, chi tiết `kb/projects/deposit-rate-autocheck.md`) — luật
  "1 bài liệt kê đủ 4 ngân hàng = đối chiếu chéo" ở entry gốc đã bị loại bỏ (lỗ hổng N=1), thay bằng
  kiểm tra domain cơ học (`--sources` JSON, ≥2 nhóm sở hữu độc lập). Giữa chừng bị 1 phiên song song
  revert về chỉ-nhắc (lo ngại chi phí review), rồi user xem lại thiết kế CONFIRMED cuối + bug thật
  tìm được (`current_deposit_rate()` ghim sai khi có ngày tương lai/gõ nhầm) → quyết định bật lại
  (commit `49481e7`), kèm yêu cầu MỚI: Winston giờ LUÔN báo Trading Daily cùng ngày có kết quả (đổi
  hay không đổi), có dòng 🆕 highlight rõ đây là số mới — không còn quiet-heartbeat cho mục này.
  (⚠️ current-state bảng chính: auto-write sau đó lại bị loại bỏ, xem `authority_note` frontmatter.)
- 2026-07-20 (Mike, user approved trực tiếp — "để bạn tự động cập nhật thông tin mà không phụ
  thuộc tôi"): nâng cấp `refresh_deposit_rate_vn.sh` từ CHỈ-NHẮC sang tự-xác-nhận-và-ghi. Không
  còn dừng ở "nhắc con người chạy `append_deposit_rate.py`" — giờ tự dispatch Winston mỗi tháng để
  WebSearch-crosscheck lãi suất Big-4 12M kênh online qua ≥2 nguồn độc lập (hoặc 1 bài báo liệt kê
  đủ 4 ngân hàng cùng ngày, tự nó là đối chiếu chéo), CHỈ ghi khi đủ bằng chứng — nếu mâu thuẫn/thiếu
  bằng chứng thì escalate y hệt luồng cũ, không tự đoán. Thêm `--source web_crosscheck_auto` vào
  `append_deposit_rate.py` (bắt buộc `--note` non-empty, tách biệt khỏi `manual_verify` để giữ đúng
  provenance — không phải người trực tiếp xác nhận). Test end-to-end thật ngay trong phiên (không
  đợi cron ngày 3): Winston tìm được 3 nguồn (CafeF 18/7, Kenh14 16/7, CafeF 13/7) đều xác nhận
  6.8% — khớp record đã có sẵn cùng ngày (do Mike tự tay append trước đó) nên tự SKIP đúng
  (idempotent), không ghi trùng. 4 câu hỏi §11 không đổi so với entry gốc bên dưới (vẫn đọc
  `current_deposit_rate()` KHÔNG BQ/cache, vẫn chạy ngày 3 trước DCF gate ngày 11, vẫn KHÔNG cần T
  chính xác, vẫn consumer = `rating_8l.py` NEUTRAL tilt + `dcf_refresh_gate.py`) — chỉ đổi CƠ CHẾ
  ghi (agent-driven crosscheck thay vì chờ người), không đổi lịch/nguồn/consumer. Chi tiết đầy đủ +
  review đối kháng: `kb/projects/deposit-rate-autocheck.md`.
- 2026-07-17 (Taylor, job `Taylor_20260717_074106`, **user approved trực tiếp**): thêm 1 dòng cron
  `10 1 11 * *` (08:10 ICT ngày 11 hàng tháng) gọi `dcf_refresh_gate.py` — cổng refresh có điều kiện:
  recompute DCF **chỉ khi** lãi suất Big-4 12M dịch ≥1.0pp so lần dùng trước (boundary =1.0pp
  **INCLUSIVE** — CHỐT, flag `THRESHOLD_INCLUSIVE=True`, không còn "chờ user"); else giữ số cũ (SKIP).
  Gate chỉ QUYẾT ĐỊNH + PERSIST, không tự chạy recompute. 4 câu hỏi §11: (1) đọc
  `deposit_rate_vn.current_deposit_rate()` (as-of, step series) + prior state JSON — **KHÔNG BQ/cache**,
  granularity tháng nên không vintage-sensitive; (2) nguồn tươi phụ thuộc deposit-rate ngày 3 đã cập
  nhật (con người xác nhận số) → chạy ngày 11 để nằm SAU ngày 3; (3) KHÔNG cần T chính xác
  (`_now_ict_date` dùng UTC date, monthly-granularity vô hại); (4) consumer = whoever tái tạo số DCF
  cho report/dashboard, gọi `run_gate()` trước rồi chỉ recompute fair value khi `refresh=True` —
  reference tool, KHÔNG deadline pipeline hàng ngày. **Fail-safe:** mọi lỗi → `refresh=True` (recompute
  thay vì phục vụ stale trên gate hỏng). Ngày 11 > ngày 3 deposit; cùng phút 08:10 nhưng khác ngày →
  không trùng thực thi. First-run/no-state → REFRESH init. Selfcheck `dcf_refresh_gate_selfcheck.py`
  24/24 PASS. Đi kèm Việc A cùng job: default terminal-growth DISPLAY của `dcf_valuation.py` đổi
  CPI→`cap_rf` (level fix, không alpha — DCF non-decisional trong prod).
- 2026-07-17 (Winston, job `Winston_20260717_072420`, **user approved trực tiếp**): thêm 1 dòng cron
  `10 1 3 * *` (08:10 ICT ngày 3 hàng tháng) gọi `refresh_deposit_rate_vn.sh` — Layer A của
  `proposal_deposit_rate_monthly_refresh_20260713.md`. Script chỉ NHẮC (best-effort fetch CafeF/VCB
  timeout 15s hay fail, KHÔNG tự ghi) + post Discord + status bus; con người xác nhận số rồi chạy
  `append_deposit_rate.py` append vào `data/deposit_rate_vn_events.csv` (append-only, chỉ mốc
  effective_date > 2026-06-01 mới có hiệu lực). 4 câu hỏi §11: (1) đọc web external best-effort
  (CafeF/VCB, có thể fail) + `current_deposit_rate()` — **KHÔNG BQ/cache**; (2) nguồn Big-4 posted
  rate đổi bất thường, thường đầu tháng → chạy ngày 3 hợp lý, không cần T thật trong ngày; (3)
  KHÔNG cần T chính xác (tilt tần suất tháng, sai vài ngày vô hại); (4) consumer = `rating_8l.py`
  NEUTRAL tilt LIVE (đọc bất kỳ lúc nào có, không deadline cứng) + `dcf_refresh_gate.py` (dùng
  quanh ngày 11 → ngày 3 nằm trước). Không trùng phút với cron nào (08:00 commodity ngày 5/10 khác
  phút+ngày; 08:15 vcb_fx T2-T6). Freshness WARN >45 ngày ở `ops_health_check.sh` §8.
- 2026-07-15 (Winston, job `Winston_20260715_061920`, user duyệt dispatch): đổi giờ 3 cron đọc `dt5g_live` để luôn đọc regime HÔM NAY thay vì hôm qua (fix M3 audit `Winston_20260712_142100`): (1) `eod_trading_report.sh` 15:00→19:10 ICT (`0 8` → `10 12` UTC); (2) `pt_8l_daily.sh` 17:45→19:20 ICT (`45 10` → `20 12` UTC); (3) `telegram_run_daily.sh` 18:00→19:35 ICT (`0 11` → `35 12` UTC). Buffer sau publish DT5G ~19:01: eod 9', pt_8l 19', telegram 34'. Không trùng phút với nhau hoặc với bq_freshness 19:00. sector_lens_monitor.py step [9] vẫn đọc cache T-1 — user xác nhận KHÔNG CẦN SỬA, known limitation, chỉ ảnh hưởng công cụ nghiên cứu nội bộ, không chạm trading production.
- 2026-07-14 (Winston, job `Winston_20260714_160739`, **user directive trực tiếp — quy tắc vĩnh
  viễn mỗi quý**; **SỬA 2026-07-23, user directive trực tiếp**): thay 2 dòng T3 tạm thời (hết hạn
  08-04) bằng **1 dòng cron DAILY 20:00 ICT** gọi `mike/bin/fa_ratings_earnings_window_daily.sh`
  — wrapper tự gate: chỉ chạy thật khi **tháng ∈ {1,4,7,10} ∧ ngày ≥ 15 ∧ không lễ VN** (đã BỎ
  điều kiện T2-T6 ngày 2026-07-23 — user xác nhận qua bq_admin rằng `ticker_financial` vẫn được
  cập nhật kể cả Thứ Bảy/Chủ Nhật trong mùa BCTC, nên loại cuối tuần chỉ làm cohort chậm oan; công
  thức cửa sổ = từ 15 của tháng đầu quý đến hết tháng đó; điều kiện "ngày ≥ 15" là đủ vì date hợp
  lệ không vượt số ngày thật của tháng — không cần bảng số-ngày-từng-tháng/năm nhuận; lễ VN =
  `vn_market.is_holiday` fixed-list, lễ biến động Tết ÂL chưa encode → best-effort, ngày Tết chạy
  thừa vô hại). Trong cửa sổ: `refresh_fa_ratings_8l.sh` 20:00 → `refresh_fa_ratings.sh` 20:45
  (spacing 45' giữ nguyên mẫu Sat/T3-tạm). Ngoài cửa sổ: no-op im lặng (log skip-reason). Dòng Sat
  08:30/09:15 GIỮ NGUYÊN (baseline quanh năm) — **từ 2026-07-23, trong cửa sổ mùa BCTC, Thứ Bảy
  sẽ chạy CẢ 2 lần trong ngày (08:30/09:15 baseline + 20:00/20:45 window-run)**, vô hại (idempotent
  DELETE+INSERT/re-rank, khác giờ nên không trùng phút) chỉ tốn thêm 1 lượt BQ query/tuần trong
  cửa sổ; Chủ Nhật chỉ có window-run (20:00/20:45), không có baseline. Cửa sổ đầu tiên áp dụng đủ
  cuối tuần: **2026-07-23 → 2026-07-31** (07-15→07-22 đã chạy dưới gate cũ, bỏ lỡ 2 cuối tuần
  07-18/19). Gate test lại 2026-07-23 qua `--check YYYY-MM-DD`: 07-18/07-19/07-25/07-26 (cuối
  tuần trong cửa sổ) = RUN đúng; 07-14 (<15)/08-01 (ngoài quý)/04-30 (lễ VN) = SKIP đúng.
  4 câu hỏi §11: (1) đọc `ticker_financial` BQ live qua 2 wrapper con đã source `wc_env.sh`
  (identity fix `a9716f6`), ghi BQ `fa_ratings_8l`+`fa_ratings`; (2) nguồn tươi same-day ~17:30
  ICT → 20:00 bắt được filings trong ngày; (3) cần T same-day trong mùa cao điểm BCTC; (4)
  consumer = custom30 builder/DC-book/golive sizing/as-of joins, deadline = rebalance quý +
  cohort đầy dần từng ngày; trước sync cache 23:45 nên cache vớt bản mới ngay đêm đó.
- 2026-07-13 (Winston, job `Winston_20260713_103213`, user approved): thêm 2 dòng cron **TẠM THỜI
  mùa BCTC Q2** — refresh `fa_ratings_8l` (T3 20:00 ICT) + `fa_ratings` (T3 20:45 ICT), guard
  `[ $(date +%Y%m%d) -le 20260804 ]` ngay trong dòng cron → **tự no-op sau 2026-08-04**, xoá dòng
  chết khi tiện. Lịch chạy: 07-14, 07-21, 07-28, 08-04 — lần cuối đúng tối trước rebalance quý
  ~08-05 (đóng điểm nóng audit `Winston_20260713_100733` q6: mã công bố 08-02..08-04 sẽ kịp có Q2
  rating tại rebalance). 4 câu hỏi: (1) đọc `ticker_financial` BQ live, ghi BQ qua wrapper đã
  source `wc_env.sh` (identity fix `a9716f6`); (2) nguồn tươi same-day ~17:30 ICT → 20:00 bắt được
  filings trong ngày (hơn hẳn 08:30 sáng); (3) cần T same-day trong mùa cao điểm; (4) consumer =
  custom30 builder/DC-book/as-of joins, deadline rebalance ~08-05 15:30. Slot 20:00 trống (giữ chỗ
  cũ), tránh hẳn khung giao dịch sáng, trước sync cache 23:45 → cache (giờ full_only, cùng commit)
  vớt bản mới ngay đêm đó. Kèm cùng commit: `sync_bq_cache.py` chuyển `fa_ratings`/`fa_ratings_8l`
  sang `full_only` (delta-append không tương thích refresh DELETE+INSERT/re-rank — hết alert
  count-mismatch giả mỗi thứ Bảy).
- 2026-07-13: thêm second-chance 23:00 cho `send_plan_report.sh` (sự cố kb/INCIDENTS.md 2026-07-13
  root-cause 1: plan sửa/re-dispatch sau 21:00 không bao giờ được gửi lại duyệt). Script đã hỗ trợ
  `--second-chance`/`--dry-run` + marker idempotent `state/plan_report_sent/` (Winston, job
  `Winston_20260713_014816`). 4 câu hỏi §11: (1) đọc file plan local + marker, không BQ/cache;
  (2) plan tươi sau pipeline 19:00, re-dispatch muộn đo thật 22:17 (07-13); (3) cần bản mới nhất
  trên đĩa lúc chạy; (4) consumer = user duyệt qua đêm, deadline preflight 08:45. Dòng cron đề xuất
  (CHƯA cài, chờ Mike): `0 16 * * 1-5 /home/trido/thanhdt/WorkingClaude/mike/bin/for_each_live_account.sh /home/trido/thanhdt/WorkingClaude/mike/bin/send_plan_report.sh --second-chance >> /home/trido/thanhdt/WorkingClaude/mike/logs/send_plan_report.log 2>&1   # 23:00 ICT — second-chance gui lai plan T+1 bi sua sau 21:00 (idempotent, su co 2026-07-13)`
- 2026-07-12: seed v1 từ audit `Winston_20260712_142100` + `Winston_20260712_151206`. Xoá 1 dòng
  crontab dangling comment (`# V2.4 go-live flip`). Fix C1 (publish DT5G đọc live, commit `4995262`,
  quant-skeptic CONFIRMED — chi tiết sự cố: kb/INCIDENTS.md 2026-07-12 C1). Fix H2 (shares_outstanding_live BLOCK→WARN, commit `6459b6d`). Điều tra
  `lag_edge_health.csv` "staleness" → kết luận KHÔNG phải bug (job `Taylor_20260712_155038`, xem
  `kb/current_ops.md`).

↩ [Về cron_registry (bảng chính)](../cron_registry.md) · [index nhóm _rules](index.md)
