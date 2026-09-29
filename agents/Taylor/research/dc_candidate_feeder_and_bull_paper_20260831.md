# DC candidate feeder + waterfall paper BULL/EXBULL — Việc #2 + #3

Job `Taylor_20260831_014244` (dispatch Mike, user duyệt 2026-08-31 08:41 ICT, decided_by user).
2 việc nhỏ, KHÔNG phải backtest, tiếp theo `dc_3book_factor_neutral_20260830.md`. Cả 2 vẫn
paper/tham khảo — không đụng `plan.py`/`executor.py`/`trading_rules.json`.

## Việc #2 — DC candidate feeder cho pipeline due-diligence/discretionary

**Kiến trúc chọn: registry RIÊNG, không nhét vào `bin/discretionary_candidate_funnel.py`.**

Lý do: funnel fear-buy là 1 pipeline BQ CHẤM ĐIỂM/RANK toàn bộ `universe_pit` mỗi lần chạy
(washout+dd52+PB adaptive threshold) — mỗi lần chạy là 1 bảng rank MỚI, KHÔNG có khái niệm "đã
thấy mã này chưa" (stateless-by-design). DC ngược lại: universe CỐ ĐỊNH 16 mã
(`sector_lens_monitor.NAMES`), tín hiệu là MEMBERSHIP nhị phân (sector-lens BUY ∩ 8L≤2 — đúng
logic `dc_book_waterfall_paper.py::load_double_confirm()`, KHÔNG viết lại). Câu hỏi cần trả lời
("mã nào MỚI thoả DC hôm nay mà hôm qua chưa") là bài toán DIFF-THEO-THỜI-GIAN (stateful), không
phải bài toán rank — nhét vào funnel PB-adaptive vừa tái tạo sai logic threshold (dispatch cấm
rõ) vừa phá tính "1 lần chạy = 1 bảng rank sạch" của funnel đó.

**Script mới**: `mike/bin/dc_candidate_feeder.py`. Cùng QUY ƯỚC OUTPUT với funnel fear-buy
(RECON-only, KHÔNG auto-arm, `--print-block` để nhúng prompt LLM khác) nhưng có state riêng để
diff theo ngày:
- `data/dc_candidate_state.json` — `active_members` (DC set lần chạy trước) + `last_run_date`,
  atomic write (tmp+`os.replace`, coding_guidelines §5).
- `data/dc_candidate_registry.csv` — append-only, 1 dòng/candidate mới: `event_date, ticker,
  event(new_entry|re_entry), sector, buy_mode, rating, primary, value, reference, reason,
  logged_at_ict`.
- Idempotent theo ngày (asof không đổi → không ghi trùng, chỉ update state).
- Mã "mới" = trong DC set hôm nay mà KHÔNG có trong `active_members` lần chạy trước — bao gồm cả
  lần đầu tiên chưa từng thấy (`new_entry`) lẫn tái xuất hiện sau khi đã rời DC set
  (`re_entry` — vẫn là tín hiệu DD mới, không phải noise, vì rating/sector-lens status đã đổi).

**Test chạy thật (2026-08-31, cache sống)**: 9 mã đang thoả DC — ACB, CTR, DHG, FPT, HAH, MBB,
PVT, SSI, TCB (tất cả `new_entry` vì registry lần đầu chạy). Re-run cùng ngày → `status=unchanged`,
0 dòng mới, registry không đổi (idempotent xác nhận bằng test thật, không chỉ đọc code).

**Chưa làm** (ngoài phạm vi Việc #2, để user/Mike quyết định riêng): wire cron chạy hàng ngày —
funnel hiện chỉ chạy on-demand giống `discretionary_candidate_funnel.py` (không có cron mặc định
nào cho funnel đó). Registry sẽ nằm im nếu không ai gọi script — khuyến nghị nếu muốn tự động,
gọi từ `eod_trading_report.sh` hoặc 1 cron riêng như `discretionary_candidate_funnel.py`.

## Việc #3 — Mở waterfall paper sang BULL/EXBULL

**File sửa**: `dc_book_waterfall_paper.py` (production PAPER mechanism — không phải file mới,
nhưng đúng như dispatch nói, đây là cơ chế paper từ đầu, không đặt lệnh thật).

**Thay đổi**: thêm hằng `BULL=4, EXBULL=5, LOG_STATES=(NEUTRAL,BULL,EXBULL)`. Gate ở đầu
`compute_waterfall_targets()` đổi từ `if state != NEUTRAL: return {}...` thành
`if state not in LOG_STATES: return {}...`. `want_deployed` trong `advance()` đổi từ
`state == NEUTRAL` sang `state in LOG_STATES` (để regime-flip detection đúng khi vào/ra khỏi
tập 3 state). Reason string tổng quát hoá từ hardcode `"NEUTRAL"` sang `state_tag` theo state
thật. Text report (`generate_section()`) sửa tương tự — không còn nói "≠NEUTRAL → flat" khi thực
ra flat chỉ xảy ra ngoài 3 state.

**KHÔNG đụng**: `dc_membership()`/`dc_weights()`/`apply_overlap_cap()`/trigger continuous-residual
(v2 fix#1)/cadence q2m5 (v2 fix#2)/overlap cap 0.15 (v2 fix#3)/liquidity floor 3B (v2 fix#4)/
PER_NAME_CAP (v2.1) — mọi cơ chế deploy/weight nguyên vẹn, đúng chỉ đạo dispatch. `SLEEVE_VERSION`
giữ `"v2"` (không phải đổi mechanism, chỉ mở phạm vi state được ghi — không cần NAV archival,
27 phiên lịch sử NEUTRAL-only vẫn hợp lệ nguyên vẹn, chỉ là sample chưa từng gặp BULL).

**KHÔNG đụng bug trigger nhị phân đã biết** (`kb/projects/rnd-pipeline-tracker.md` mục DC-book) —
đây là quyết định TÁCH BIỆT, chỉ mở phạm vi state được log, không chạm cơ chế trigger/cadence.
Giữ nguyên tới mốc review ~06/10 theo chỉ đạo user 07-13.

⚠️ Lưu ý phụ (không sửa, chỉ ghi nhận): `rnd-pipeline-tracker.md` mục DC-book mô tả 4 việc "cần
sửa tại mốc review" (continuous-residual/cadence/overlap-cap/liq-floor) — đọc code hiện tại
(`dc_book_waterfall_paper.py` docstring v2, 2026-07-20) thì cả 4 việc này **đã được áp dụng rồi**
(SLEEVE_VERSION="v2"). Tracker có vẻ chưa cập nhật theo thực tế code — không nằm trong phạm vi
job này để sửa (KB cần Mike duyệt, §13), chỉ nêu ra để ai xử lý mốc review 06/10 biết trước.

**Selfcheck**: `dc_book_waterfall_selfcheck.py` — thêm group F (11 test mới): BULL/EXBULL giờ
deploy đúng cơ chế 0.15-cap giống NEUTRAL, CRISIS/BEAR vẫn flat (gate không mở quá phạm vi định),
`LOG_STATES` đúng đúng 3 giá trị, và test end-to-end qua `advance()`: chuyển từ NEUTRAL sang BULL
KHÔNG flatten/reverse-unwind (đúng ý đồ — trước đây sẽ bị coi là rời NEUTRAL nên unwind).
**78/78 PASS** (67 cũ + 11 mới). Mutation-test xác nhận test mới THẬT SỰ bắt được lỗi: revert gate
về `state != NEUTRAL` → `F1` fail ngay (KeyError vì `tgt_bull` rỗng) — không phải test giả no-op.

## Files

- Mới: `mike/bin/dc_candidate_feeder.py`
- Data mới: `data/dc_candidate_state.json`, `data/dc_candidate_registry.csv` (9 dòng test thật)
- Sửa: `dc_book_waterfall_paper.py` (gate + reason strings + report text + docstring v2.2 note)
- Sửa: `dc_book_waterfall_selfcheck.py` (+group F, 11 test)
