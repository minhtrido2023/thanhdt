---
kind: changelog
group: _rules
title: Lịch sử biên tập Data Registry
note: >
  Đây là changelog BIÊN TẬP của chính registry (nguồn nào thêm/sửa/đánh dấu obsolete, ai làm,
  job nào) — provenance, KHÔNG phải narrative sự cố. Sự cố live-workflow ghi ở kb/incidents/.
  Vì không trùng INCIDENTS nên giữ nguyên (không nén-thành-pointer). Mục cũ nhất ở dưới cùng.
---

# Lịch sử biên tập Data Registry

- 2026-07-31 (Winston, job Winston_20260731_014953): cập nhật `market-state/vnindex_5state_dt5g_live.md` — thêm mục **⚠️ HAI WRITER ĐỘC LẬP** (publisher của ta ~18:35/~19:01 + pipeline **kaffa_v2 của team dữ liệu** ~17:12 ICT, implementation DT5G RIÊNG, DELETE+APPEND 5 phiên, từ commit c794dd1 2026-06-08). Ghi rõ **quyết định user 2026-07-31 (phương án B)**: ta CHỈ TIÊU THỤ + GIÁM SÁT + BÁO team dữ liệu, **KHÔNG** yêu cầu họ đổi bảng đích, **KHÔNG** đụng hệ thống của họ. 4 hệ quả kỹ thuật đã đo: (1) `MAX(time)` KHÔNG chứng minh publisher của ta còn sống (gate cũ bị che — đo thật 2026-07-31 09:02: gate cũ `lag=0 OK` trong khi bản công bố của ta vẫn là `as_of=07-30`) ⇒ `bq_freshness_check.sh` chuyển sang gate bằng BẰNG CHỨNG publisher (`golive_state_today.json`); (2) cửa sổ 17:12→18:35 bảng mang giá trị engine kaffa (consumer production chạy sau 19:00 nên không dính); (3) 2 engine lệch **27/3.134 phiên (0,86%)** — trùng khớp hằng ngày là may, không phải bảo đảm; (4) **`asof_date IS NULL` = dấu vân tay writer ngoài** (đo 2026-07-31: đúng 5 dòng đuôi 07-24→07-30 NULL; NULL ở đuôi là BÌNH THƯỜNG trong kiến trúc 2-writer, NULL ở vùng ĐÃ CHỐT mới là báo động). Thêm monitor `mike/bin/dt5g_writer_watch.py` (2 mẫu/ngày, tầng HIGH/WARN/QUIET, không chặn gì) + cập nhật `market-state/golive_state_today.md` (vai trò mới: input của gate BLOCK).
- 2026-07-30 (Taylor, job Taylor_20260730_164533): thêm nguồn MỚI `data/value_radar_series.csv` + module `value_radar.py` → `market-state/value_radar_series.md`, status **CANONICAL (DISPLAY-ONLY)**. Đóng gói Value Radar của Phụ lục C (`market_regime_probability_20260729.md`) thành module tái dùng; user chốt cửa sổ **rolling 10 năm** làm bản chính (07-30 = **25,9 RẺ**; expanding-2008 = 36,0 TRUNG TÍNH — cùng ngày, cùng công thức, khác cửa sổ). Wire vào ĐÚNG 2 chỗ hiển thị: `dna_report.build_value_radar_line()` (khối NOW, cạnh state DT5G) + `mike/bin/eod_trading_report.sh`. **Bẫy quan trọng nhất đã ghi vào entry: CẤM mọi consumer ra quyết định** (0/17 lăng kính qua BH/Bonferroni; đầu RẺ không đơn điệu) — cùng tiền lệ DT4-gate clock. Self-check parity PASS: lệch nhãn 0/4.134 phiên vs `exp_value_radar/radar.csv`, số hôm nay khớp pin §C.4.5.
- 2026-07-29 (Taylor, job Taylor_20260729_015830): thêm nguồn MỚI `tav2_bq.insider_transaction` (giao dịch nội bộ TT96/2020, bq_admin backfill 2026-07-27) → `fundamentals/insider_transaction.md`, status CANONICAL kèm 4 bẫy point-in-time đo được: (1) bảng là SNAPSHOT trạng thái, `public_date` bị GHI ĐÈ khi Đăng ký→Done ⇒ ngày công bố Ý ĐỊNH của 50.934 sự kiện đã hoàn tất ĐÃ MẤT (không backtest được lợi thế công bố-trước của VN nếu không tự snapshot từ nay); (2) `Không thực hiện được` gần như không dùng (2 dòng/11 năm) — non-completion thật đọc ở `share_acquire` (14,7% khớp 0 CP); (3) `share_before/after` không tin được ở dòng Đăng ký; (4) cụm ≥5 người cùng mua 1 ngày = ESOP (15,7% dòng Mua) làm nhiễu tín hiệu "insider mua". Ghi thêm: `role_name` KHÔNG phải chức danh (chứa tên người) — bảng KHÔNG có field chức vụ; `event_code` tách sạch DDIND/DDRP (người) vs DDINS (tổ chức = flow, không phải inside info). CADENCE REFRESH CHƯA XÁC NHẬN (mới 1 lần ingest) — phải hỏi bq_admin trước khi live đọc.
- 2026-07-28 (Winston, job Winston_20260728_104434): migrate `kb/data_registry.md` (single-file, 265 dòng,
  18 mục bảng markdown) → cấu trúc OKF `kb/data_registry/` (1 nguồn = 1 file .md + frontmatter tối thiểu,
  13 thư mục nhóm + index.md điều hướng). File cũ giữ làm STUB REDIRECT. Cảnh báo an toàn (cột "Bẫy")
  chuyển VERBATIM sang prose, không cắt. Cập nhật 3 ref code/prompt sống: `bin/kb_nightly.sh`,
  `kb/coding_guidelines.md §9`, `kb/context_dataops_mini.md`. PILOT dọn-dẹp OKF của đội.
- 2026-07-23 (Winston, job Winston_20260723_080716): đánh giá khả thi 5 nguồn foreign flow lịch sử (vnstock đã xác nhận KHÔNG có — foreign_trade/prop_trade là stub NotImplementedError). Kết luận test THẬT bằng curl: **VNDirect finfo `/v4/foreigns` = nguồn tốt nhất** (JSON no-auth, per-stock + INDEX-level VNINDEX/VN30 + phái sinh VN30Fyymm, ~8 năm từ 2018-08-30); cafef ashx chỉ ~3 tháng rolling cash-only; fireant cần token; TCBS/vietstock/HOSE không khả thi qua path đã dò. Thêm 5 row vào bảng "Feeds Winston". CHƯA wire production — chỉ báo cáo khả thi cho Mike/user quyết định bước tiếp (job nghiên cứu tìm tín hiệu báo trước đợt giảm VNI −13,45% từ đỉnh 05-18).
- 2026-07-17 (Winston, job Winston_20260717_072420): triển khai Layer A refresh routine cho `deposit_rate_vn.py` (user approved). Thêm `data/deposit_rate_vn_events.csv` (append-only, 5 cột) + patch `deposit_events_df()` (backward-compatible: CSV rỗng = hành vi cũ y hệt, verified regression `current_deposit_rate()`=6.80%) + `append_deposit_rate.py` (CLI append idempotent + atomic + verify) + `refresh_deposit_rate_vn.sh` (cron nhắc 08:10 ICT ngày 3, best-effort fetch KHÔNG tự ghi) + WARN freshness >45 ngày trong `ops_health_check.sh` §8. Đổi status entry `deposit_rate_vn.py` từ "CHƯA có cron" → đã có refresh routine.
- 2026-07-17 (Taylor, job Taylor_20260717_063638): thêm nguồn mới `gdp_growth_vn.py` (World Bank real GDP annual, CANONICAL single-tier) cho DCF terminal-growth research. Thêm consumer mới cho `deposit_rate_vn.py`: `dcf_refresh_gate.py` (gate refresh có điều kiện theo biên độ 1pp). DCF earning-power/terminal-g study: research, NOT wired production (quant-skeptic CONFIRMED — earning-power NO-GO redundant w/ 1/PE, GDP terminal-g = level/display fix không phải alpha).
- 2026-07-14 (Winston, job Winston_20260714_055051): thêm `dcf_valuation.py` + `dcf_backtest.py` làm consumer mới vào 2 entry đã có — `deposit_rate_vn.py` (dùng `current_deposit_rate()` làm risk-free rate baseline) và `cpi_vn.py` (CPI làm terminal growth rate input). Cả 2 là research tool, NOT wired production (job Taylor_20260714_051643).
- 2026-07-13 (Winston, job Winston_20260713_131255): thêm 2 row thiếu trong mục "Vĩ mô" —
  `deposit_rate_vn.py` (data prerequisite §2 plan Pillar A′, `Taylor_20260713_124803`) và
  `cpi_vn.py` (phát hiện PHỤ trong lúc làm, đã có sẵn từ 2026-07-06 nhưng chưa vào registry). Cả
  2 là proxy hồi tố/fetch-tay-1-lần, KHÔNG có cron refresh — gap vận hành giống nhau, đề xuất
  routine tháng ở `proposal_deposit_rate_monthly_refresh_20260713.md` (chưa duyệt/cài).
- 2026-07-13 (Winston, job Winston_20260713_103213): cập nhật 3 row lỗi thời sau khi refresh
  fa_ratings/fa_ratings_8l sống lại 07-12 (identity fix `a9716f6`, test ghi thật OK, quant-skeptic
  CONFIRMED): row `fa_ratings` hết "STATIC/chờ duyệt cron/lastModified 05-10", row `fa_ratings_8l`
  hết "cron chưa xác nhận ghi được/đứng 06-20", row `bq_cache` hết "fa_ratings chết 05-10". Kèm
  cùng commit: `sync_bq_cache.py` chuyển 2 bảng này sang `full_only` (delta-append không tương
  thích refresh DELETE+INSERT/re-rank) + cron tạm T3 mùa BCTC đến 2026-08-04 (xem
  `cron_registry.md`).
- 2026-07-11: tạo lần đầu, seed từ sự cố SIGNAL_V11 base-leak + các gotcha đã biết trong
  CLAUDE.md/coding_guidelines.md.
- 2026-07-11 (Taylor sweep, job Taylor_20260711_080014): rà toàn codebase (grep mọi `tav2_bq.*`,
  file `data/*` dùng chung, crontab thật, `bq show` lastModified thật, mtime thật). Thêm 8 section
  mới (~35 nguồn): 8L rating, custom30 baskets, bq_cache, LAG caches, research caches, trading
  bot/execution, paper harness, feeds Winston, config/meta, quy tắc universe. TRAP/rủi ro mới phát
  hiện: `custom30_8l` vs `custom30v_8l` (mislabel bug thật 07-11, bảng sai lại TƯƠI hàng ngày);
  `tav2_bq.fa_ratings` STATIC không writer nhưng vẫn là input production SIGNAL_V11;
  `vnindex_5state_dt_4gate` BQ chết 06-02 nhưng CSV local sống (cache mirror bản chết);
  `data/vnindex_5state.csv` twin local của bảng trap; cache DuckDB mirror nguyên tên cả bảng trap.
- 2026-07-11 (họp team, job Taylor_20260711_084145, quant-skeptic CONFIRMED): `custom30v_8l` đóng
  gap (root cause = lịch thứ Bảy, không phải writer hỏng — xem file Custom30). `fa_ratings` →
  khuyến nghị migrate sang `fa_ratings_8l` NHƯNG qua full validation (66% tier khác nhau = đổi
  signal), CHƯA đánh dấu DEPRECATED — đang ở bước backtest song song (job Taylor_20260711_094714,
  user duyệt hướng validate 2026-07-11). Xem "Nguyên tắc bắt buộc" mục 5 (index.md) cho quy trình
  obsolete đầy đủ, thêm cùng ngày theo yêu cầu user ("quản lý phần này phải thật sự cẩn trọng").
- 2026-07-12 (Taylor, job Taylor_20260711_165407, momdeal Phase 0): sửa row `ba_v11_unified_12y_sig.pkl`
  — builder ghi nhầm (`build_state_free_signals.py` → thật ra là `build_pkl_v11_current.py`); pkl rebuilt
  trên `dt5g_live` (bản cũ base-leak pre-F3), backup `.bak_predt5g_20260711`. Phát hiện thêm:
  `bigquery_dictionary.json` THIẾU định nghĩa họ cột `profit_*` (forward return, đơn vị **PHẦN TRĂM** —
  verify thực nghiệm = `LEAD(Close,40)/Close−1 ×100` cho profit_2M) — Winston nên bổ sung dictionary.
- 2026-07-11: xây `bin/data_registry_audit.sh` (regression-guard cơ học cho 2 sự cố base-leak +
  custom30-mislabel, freshness re-check 3 nguồn rủi ro cao nhất, reference-count snapshot cho
  nguồn deprecated/dead) — wire vào Friday KB editorial review (`kb_nightly.sh` Phase 5). Chạy
  thật lần đầu: FAIL=0/WARN=0, xác nhận cả regression-guard lẫn freshness đều đúng thực tế.
- 2026-07-29 (Winston, job `Winston_20260729_132257`, audit sâu theo dispatch Mike): **sửa
  `price-volume/ticker_prune.md` — entry cũ ĐẾM THIẾU consumer LIVE.** Câu "2 consumer LIVE còn
  lại có chủ đích" là SAI: rà cron thật ra thêm **4 chỗ không chủ đích**, sót lại từ trước
  migration — `macro_state_live.py:158` (**breadth-decoupling guard của DT5G, đường regime
  PRODUCTION**), `dna_report.py:91,129`, `update_shares_live.py:49`, `ta_score_daily.py:142`.
  Thêm mục ⚠️ 2026-07-29 ghi sự kiện **TRUNCATE+rebuild `--mode prune` (creation_time 07:27)**:
  distinct ticker **513 → 455** (58 mã biến mất khỏi TOÀN BỘ lịch sử, thêm mới 0), lịch sử viết
  lại ở **20/27 năm cả hai chiều**, hố corruption 07-08→07-14 lành về độ sâu nhưng membership
  07-13 rơi **265 → 220** và là tập con nghiêm ngặt. Cơ chế = đúng Câu 8 QA doc bq_admin
  (`hit_ticker_list.csv` không đổi từ 04-14) ⇒ **sẽ lặp lại mọi rebuild sau**. Blast radius đo
  được vào DT5G: guard lật 79/3135 phiên nhưng chỉ 2 trùng Pillar B, cả 2 singleton →
  `cap_commit=7` nuốt → **0 phiên state đổi** (KHÔNG phải nguyên nhân thứ 3 của vụ restate 71
  phiên). Xác minh **upstream sạch** (`ticker_1m`/`risk_rating` KHÔNG bị prune-lọc; prune là đầu
  ra chứ không phải đầu vào của bq_admin) — có ghi giới hạn: `INFORMATION_SCHEMA.JOBS` Access
  Denied nên không đọc được SQL họ. Phụ: cột `Pattern_*` của `ticker_1m` NULL 100% = cột chết.
  Báo cáo: `mike/agents/Winston/research/ticker_prune_hidden_risk_audit_20260729.md`.
