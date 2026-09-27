# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Retro 2026-09-26 XONG (commit a9b294de): 2 sự cố, Wags GAPS FOUND (minor, đã sửa — đếm
  event 153→163). Escalation: KHÔNG mở mới. 2 carry-over vẫn treo (xem dưới).
- **CARRY-OVER quan trọng nhất — `retro-pattern-recurring-ack-topic-counter-structural-3retros`**
  (mở 09-25T20:59:54Z): Mike đã quyết dispatch Wags 1 task hẹp sửa `daily_retro.sh:195` vs
  `ops_health_check.sh` (bug ack-topic-counter, arch-reviewer chỉ đúng 2 lần 09-23/09-25) —
  **CHƯA THỰC THI** qua 2 retro liên tiếp (~20h tính đến 09-26). Nếu vẫn chưa làm khi có
  instance mới (report/coordination chạy lại từ Thứ Hai 28/09) → lần tái diễn thứ 4, cần làm
  ngay đầu tuần.
- Carry-over: `retro-pattern-recurring-fpt-vendor-backfill-2days` — BQ FPT corp-action hệ số
  vẫn thiếu, chờ user chọn A/B/C. 0 report cuối tuần nên chưa verify lại được.
- `selfcheck-baseline-checker-no-tier-orb-vnstock-daily` (mở 09-25, low urgency) — treo, chưa
  tới ngưỡng escalate lại.

## Việc đang mở / cần theo dõi
1. **FiinPro harvest**: 74/74 lô XONG (26/09). 2 job song song đang chạy: JOB A
   Taylor_20260926_164113 (H3 PIT→H1 bank 8L→H2 CPI), JOB B Taylor_20260926_164143 (H4 foreign
   matched 2018→H5 retail ecology), timeout 3h, opus/high. Sau khi cả 2 xong: dispatch H6
   (Bobby/macro-strategist, lead-indicator credit/M2/fx) + H7 (GDP, thấp ưu tiên). Wakeup poll:
   claim-reply từng job trước khi post kết quả.
2. **excluded_dividend_receivable[DGC]** (ZaloPay) — dọn config khi tiền DGC về thật, đã qua hạn
   dự kiến ~09-25, kiểm lại khi có cập nhật.
3. Đối soát panel-vs-live gap (job Taylor_20260926_042824) đã XONG 04-44 26/09: 2 việc phụ còn
   mở không khẩn — `audit_lib.py` nhãn park sai E1VFVN30 vs CUSTOM_VN30G; 8-9 mã live ngoài rổ
   recommend chưa truy nguồn.
4. Opening-window l2-poll A/B (order_book_execution_shadow ext, commit 4d863548) DEPLOYED, cron
   09:13 ICT T2-T6 từ 28/09 — checkpoint sơ bộ 21/10, mốc quyết định cứng 25/01/2027.

## ĐÃ XÁC NHẬN KHÔNG CÒN TREO
- Chuỗi audit corp-action 4 call-site + vendor-mismatch + ex-date price-frame — ĐÓNG HOÀN TOÀN
  2026-09-24, tất cả LIVE trên master.
- context_pack.md 47.6KB đã vượt ngưỡng 45KB (ghi nhận 09-25, chưa xử — theo dõi nếu tiếp tục
  phình).

- [2026-09-26T17:48:06Z] 27/09 00:5x — FiinPro 7 HƯỚNG XONG (commit kb v: kết quả ở kb/projects/fiinprox-data-usage-proposal-20260926.md §6). Không wire gì. CHỜ USER QUYẾT: (1) bus question Taylor/custom30v-index-artifact-pham-vi-re-pin — R3 28,86%→24,38% (−4,48pp) khi bỏ bước nhảy số CP khỏi chuỗi return custom30V (custom_basket.py:220/:1125), quant-skeptic CONFIRMED high — A sửa+re-pin toàn bộ / B chỉ R3 / C TRAP; Taylor khuyên A + kiểm kê park LIVE có mua 30 mã thật không; (2) đóng B.1 production_mechanism_2009_2018 + G4 amh-review; (3) câu hỏi trục breadth-tercile 08-22 trượt 4/4 trên panel H5; (4) H1/H2 wire vệ sinh (giá trị 0/thấp) — có làm không. Đã lưu h5_retail_*.csv + artifact trong git (8acb69d4, aff8940e). Trial FiinPro hết 28/09 — KHÔNG mua.
- [2026-09-27T02:24:04Z] 27/09 09:2x — USER QUYẾT (Discord 09:20): custom30V option A + kiểm kê park LIVE; đóng B.1+G4 (đã commit); breadth-tercile 08-22 nghiên cứu lại; H1/H2 wire vệ sinh. Đã đóng bus question custom30v-index-artifact-pham-vi-re-pin (decided_by=user, A). Dispatch 3 job song song opus/high, ĐỀU LÀM TRONG WORKTREE, KHÔNG tự merge master: JOB C Taylor_20260927_022253 (custom30V: bước 0 kiểm kê park LIVE → sửa custom_basket.py chân return → re-pin R3 + kiểm kê mọi pin qua custom_basket → quant-skeptic, timeout 4h); JOB D Taylor_20260927_022319 (H1 rate_bank AQ vào rating_8l_history + vá override_current_bank_aq fail-open; H2 tầng T1.5 cpi_vn + freshness §14; quant-skeptic; timeout 3h); JOB E Taylor_20260927_022338 (breadth-tercile recheck, paper-only, 3h). Khi xong: claim-reply từng job, post kết quả, xin user sign-off merge C và D. Overdue verify job quant-skeptic_20260926_173015: artifact CONFIRMED có trên bus → đã xử lý status.
- [2026-09-27T02:40:16Z] 27/09 09:4x — JOB E XONG (claimed): verdict A — quy ước breadth-tercile 08-22 ĐỨNG (giữ trục), nhưng ranh giới: 0/27 ô 08-22 + 0/4 job E trên 12,6 năm ⇒ chỉ MÔ TẢ, đừng suy tín hiệu từ nhãn ô; 3 trục cùng khuôn 0/12. Đã duyệt 2 .proposed (canonical.md + bq_cache_parquet.md bẫy MA200 NULL 2015-2017). CẦN WINSTON (data-ops): MA200 NULL là khuyết cache hay có thật ở tav2_bq.ticker — chưa làm. JOB C bước 0 xong: park LIVE CÓ mua rổ thật (SpaceX 19 mã 387tr, ZaloPay 17 mã 157tr; không đủ 30 tên do lot 100cp), custom_basket chỉ trên đường sống ở chân WEIGHT (custom30_history.py → custom30v_8l_publish.csv) ⇒ sửa chân return không đổi byte nào đường tiền; fake return đo trên cửa sổ live 01/07→25/09 = +0,9751pp (ACB +13% 22/07, HPG +10% 30/07). JOB C bước 1 đang chạy worktree wt-c30v-retfix. JOB D đang chạy.
- [2026-09-27T03:09:08Z] 27/09 10:1x — JOB D XONG (claimed): H1+H2 WIRED trên branch wire/fiinprox-h1-h2-ve-sinh (worktree /home/trido/thanhdt/wt-fiinprox-h1h2-wire, commit repo ngoài f4b081b7 + 9f0b2bf3; mike 727d99a1), quant-skeptic CONFIRMED medium, selfcheck 33/33 + 33/33 (3 TZ). CHỜ USER SIGN-OFF MERGE. 2 Δ live: BVB mất QUALITY_OK (rating 3→4, điểm 3 cũ là bịa do fail-open bank-nodata; không nắm giữ), ABB vào watchlist tier W anomaly_scan (3→2). Hậu kiểm bắt buộc sau merge: build_universe_pit_quality BVB→RATING_FAIL, ABB giữ OK; chạy rating_8l_history.py canonical refresh fa_ratings_8l. Đã duyệt 2 registry .proposed (commit). JOB C custom30V còn chạy (bước 2 re-pin). Sau C xong: data-ops xác minh MA200 NULL 2015-2017.
- [2026-09-27T03:30:17Z] 27/09 10:3x — USER KÝ MERGE H1/H2: đã merge --no-ff vào main repo ngoài (1546895a), 4 file (cpi_vn.py, rating_8l_history.py + 2 selfcheck). Dispatch hậu kiểm bắt buộc (job xem output dispatch): selfcheck trên main, rating_8l_history canonical refresh fa_ratings_8l, build_universe_pit_quality (BVB→RATING_FAIL, chỉ BVB), anomaly tier W chỉ +ABB, md5 custom30v_8l_publish.csv/rating_8l.csv không đổi, registry → LIVE. JOB C custom30V còn chạy (wakeup 10:30 poll).
- [2026-09-27T03:30:41Z] 27/09 10:3x — USER KÝ MERGE H1/H2: đã merge --no-ff vào main WorkingClaude commit 1546895a. Dispatch hậu kiểm bắt buộc  (Taylor, main canonical): selfcheck trên main, rating_8l_history.py canonical refresh fa_ratings_8l (kỳ vọng 360/981 đổi, 0 đổi cổng ≤3 lịch sử, 6 dòng mới nhất đổi), build_universe_pit_quality BVB→RATING_FAIL/ABB OK, park byte-identical, cập nhật registry+current_ops. JOB C custom30V Taylor_20260927_022253 vẫn chạy (64 phút, re-pin R3 trong wt-c30v-retfix, thư mục c30v_retleg_repin_20260927). Sau khi C xong: data-ops xác minh MA200 NULL 2015-2017.
- [2026-09-27T03:31:01Z] 27/09 10:3x — job hậu kiểm H1/H2 sau merge = Taylor_20260927_033050 (đã tạo, running). Poll cùng JOB C Taylor_20260927_022253.
- [2026-09-27T03:31:02Z] 27/09 10:3x — hậu kiểm H1/H2 sau merge: job Taylor_20260927_033050 (opus/medium, 2h). Lần dispatch đầu bị chặn bởi NOTE effort-high (không tạo job) — đã dispatch lại effort medium. Wakeup gộp poll C (Taylor_20260927_022253) + F (033050).
- [2026-09-27T03:37:00Z] 27/09 10:3x — User hỏi 'còn việc treo?': đã đóng 3 bus question resolved-nhưng-chưa-close (loan_package_multi_account_selfcheck stale, wags-fix-not-confirmed coord-2026-09-25 no-code-change, fiinprox-H1-H2-wire-merge-hay-khong đã merge). Dispatch 2 việc mới: Wags_20260927_033622 (fix DỨT ĐIỂM ack-topic-counter bug, đã quyết 09-25 nhưng 2 retro chưa thực thi — lần 3 escalate, bắt buộc arch-review), Taylor_20260927_033642 (triage lag_forensic_filter_selfcheck.py red 2 ngày chưa ai xem, banned-ticker safety filter). Còn treo cần user quyết: (1) FPT vendor backfill A/B/C (3 ngày, xem context_pack); (2) code-reviewer/cq-2026-09-27-hard-boundary — 11 finding money/order-adjacent code-reviewer CỐ Ý không cho Wags autofix, nổi bật: discretionary_margin_gate.py:195 current_price() unpack 3 từ tuple 2 phần tử → crash check-exits nếu có margin arm sống (hiện 0 arm, latent nhưng HIGH severity) — chưa dispatch fix, cần quyết có làm ngay không. 4 job Taylor/Wags đang chạy song song: C (custom30V repin, worktree wt-c30v-retfix), F/hậu kiểm H1H2 (Taylor_20260927_033050), Wags ack-topic-counter (033622), Taylor lag_forensic triage (033642).
- [2026-09-27T03:42:48Z] 27/09 10:4x — JOB F hậu kiểm H1/H2 sau merge: PASS sạch (claimed). fa_ratings_8l refresh 360/981 BANK đổi, 0 cổng ≤3 đổi lịch sử, 6 dòng mới nhất đổi đúng chủ đích (BAB/BVB/PGB 3→4, NVB/SGB 3→5, KLB 4→3); BVB→RATING_FAIL (hiệu lực từ build kế tiếp, bảng append-only), tier W +ABB; md5 custom30v_8l_publish.csv/rating_8l.csv không đổi; registry LIVE (ae77b515). Lưu ý selfcheck cpi_vn_tier15 cần CPI_OLD_ROOT trỏ bản pre-merge — không phải regression. Còn JOB C custom30V (running ~80'), sau đó data-ops MA200 NULL.
- [2026-09-27T03:50:30Z] 27/09 10:4x — User: (1) đề xuất FPT tự tính hệ số corp-action thay vì phụ thuộc vendor VCI (giải thích root cause: VCI rate-limit hôm đó); (2) duyệt xử lý TẤT CẢ 11 finding code-quality hard-boundary. Đã dispatch 2 job mới: Taylor_20260927_034929 (prototype self-computed adjusted-Close cross-check dùng tav2_bq.corporate_action, test trên case FPT, KHÔNG wire production, R&D only), Taylor_20260927_035010 (sửa 11 finding theo 3 mức ưu tiên — HIGH: discretionary_margin_gate.py:195 crash; MEDIUM: daily_nav_snapshot.py §25 guard, brokers.py get_cash fallback, compute_active_nav.py silent drop, dividend_adjusted_return.py hardcode accounts; LOW: TZ bare-datetime x2, dead-code x2 — worktree riêng, arch-review bắt buộc, KHÔNG tự merge). Đã đóng bus code-reviewer/cq-2026-09-27-hard-boundary (decided_by=user). Đã đóng bus FPT vendor backfill? KHÔNG — vẫn treo, chỉ mới dispatch prototype, sẽ đóng khi Taylor có kết quả. Tổng 6 job Taylor/Wags đang chạy song song: C custom30V, F hậu kiểm (PASS rồi), Wags ack-topic-counter, Taylor lag_forensic triage, Taylor FPT prototype, Taylor code-quality fix 11 finding.
- [2026-09-27T04:06:53Z] 27/09 11:0x — data-ops xác minh MA200 NULL 2015-2017: CÓ THẬT ở nguồn tav2_bq.ticker (không phải khuyết cache), luật lọc mẫu số giữ nguyên; đã commit registry. JOB C custom30V còn chạy (~100', heartbeat sống, timeout 4h) — wakeup 11:27 poll.
