# Dự án thay thế `ticker_prune` → `universe_pit` — ĐANG MỞ (checklist G4-G9)

**Quyết định lịch trình (2026-09-06, user, Discord):** không chốt mốc lịch cho toàn dự án.
P5/P6 (CAPIT pool + ADV cap cutover) và G8.1 (executor.py) giữ **event-gated vô thời hạn**
(chờ `capit_fired=false` + quyết định sàn thanh khoản pool riêng; chờ trước khi bật 3 cờ live)
— đúng bản chất, không nên gán ngày lịch cho điều kiện thị trường. Riêng **G7/G8/G9** (không bị
chặn bởi điều kiện gì, chỉ là backlog treo từ 07-22) được đưa vào quét định kỳ hàng tuần —
`bin/kb_nightly.sh` item 12 (commit `852d8d34`): báo tuổi mỗi tuần, escalate hỏi user nếu
"CÒN TREO" liên tục >8 tuần không ai làm.

> Tách ra khỏi `kb/current_ops.md` 2026-08-01 (token-cost review). Fact QUYẾT ĐỊNH đã cutover
> (universe_pit = production cho R3/CAPIT breadth) vẫn giữ tóm tắt trong current_ops.md — file
> này chỉ chứa checklist chi tiết còn lại + lịch sử vintage. Đọc khi cần theo dõi tiến độ G5-G9,
> không cần đọc mỗi phiên.

`ticker_prune` không có quản trị (curation circular-bias, không tái lập được, và **07-29 bị
bq_admin TRUNCATE+rebuild mất 58 mã khỏi toàn lịch sử** — 513→455 mã, -17%, đúng cơ chế "mã vào
bằng daily-append bị xoá ở lần rebuild toàn bộ kế tiếp" — user chốt 07-29 KHÔNG khôi phục từ
backup, giữ `ticker_prune_ttbackup_fresh_20260713` chỉ làm mỏ neo nghiên cứu) → team tự xây
`universe_pit` (point-in-time từ `tav2_bq.ticker`, B3=1,0 tỷ VND/ngày). **Cổng cứng §3.2b/Q9 ĐÃ
MỞ từ 2026-07-22** (user chốt A′+Q-C, không Q-B) — P1-P3 cutover production (custom30V→
`universe_pit_q` commit `ce7d457`, golive_recommend_v23 commit `0bfbdfe`). **CAPIT §4.4 = NỬA XONG
(G4)**: breadth cutover `universe_pit` (`CAPIT_BREADTH_SOURCE=pit`, top-250, washout_gate 0,31,
commit `dcee252`); **pool pbz + ADV cap CỐ Ý còn ghim `ticker_prune`** (đổi rổ đang giải ngân, 2
vòng đo thất bại tìm ngưỡng bảo toàn) — cấm cutover pool khi `capit_fired=true`. **G6 re-pin R3
XONG 2026-07-22** (`results_registry.md:4040`); số bị **re-pin LẠI 07-29 do đổi vintage restate
DT5G, không đổi mô hình** (số liệu ở `kb/canonical.md`). Còn lại thật: G5 shadow
≥10 phiên, G7 N-trial review, G8 data/cron-registry gate, G9 quant-skeptic full review — cộng 3
việc mới phát sinh từ audit 07-29 (Winston_20260729_132257): (1) ~~migrate breadth-decoupling guard
`macro_state_live.py:158` sang `universe_pit`~~ **ĐÃ XONG 2026-07-29**, commit `8f958957`
(`BREADTH_SOURCE = "pit"`, `UNIVERSE_PIT_TABLE = tav2_mike.universe_pit`); quant-skeptic
CONFIRMED confidence cao (`mike/logs/verify_20260729_153007.log`), post-merge self-check trên
module production 6/6 PASS, A/B 3135 phiên: breadth khác 3132 ngày (mean |Δ| 2,4pp), guard flip
229 phiên, macro cap khác 13 phiên, **state DT5G cuối cùng khác 0 phiên**. Ngưỡng giữ nguyên;
rollback = đổi đúng 1 dòng. (Dòng "đang chạy, cần self-check+quant-skeptic trước khi wire" là
trạng thái 07-29 lúc audit, đã lỗi thời ~2 tháng — sửa 2026-09-24.); (2) pin/snapshot BQ hàng tháng cho bảng dễ restate (`ticker`/
`ticker_financial`/`ticker_prune`/`universe_pit`/VNINDEX_PE, dispatch Winston đang chạy); (3)
WASHOUT_GATE đã tự verify KHÔNG cần rà lại (0,31 hiệu chuẩn đúng trên `universe_pit`, không phải
bug). Tài liệu đầy đủ:
`mike/agents/Taylor/research/ticker_prune_replacement_plan.md` +
`mike/agents/Winston/universe_pit_ops_feasibility_20260722.md` +
`mike/agents/Winston/research/ticker_prune_hidden_risk_audit_20260729.md`.

## ✅ G7-G9 ĐÓNG (2026-09-19, dispatch Mike, job `Taylor_20260919_033750`)

Backlog treo 8,4 tuần (escalate qua `kb_nightly.sh` item 12) — user quyết dứt điểm. Cả 3 mục:

- **G7 (rà soát N-trial, đặc biệt `lag_filter_illiquid` chồng lớp B3/B4)** — **đã có câu trả lời
  đầy đủ hơn phạm vi gốc**, không cần chạy lại: `kb/projects/lag-adv-filter-tracking.md` mục
  2026-08-25 (Biến thể B) đo chính xác câu hỏi này — sàn 2B tĩnh ≈ percentile 43,1 của
  `universe_pit`, KHÔNG redundant với B3/B4 (B3/B4 là cổng ELIGIBILITY thô, sàn 2B là cổng
  KHẢ-THI-THI-HÀNH của riêng book LAG) — **NO-GO cả 3 biến thể động, giữ 2B tĩnh**. TMG/IVS (ứng
  viên thứ hai §5.3) đã đóng từ 2026-07-28 (`kb/projects/lag-0724-ivs-tmg-trc.md`). Phần theo dõi
  dài hạn còn lại (fill LAG thật N≥30, mốc **2026-12-15** / **2027-03-31**) là quan sát TÍCH LUỸ
  THEO LỊCH, không phải việc backlog — giữ nguyên lịch, KHÔNG rút ngắn.
- **G8 (data_registry + cron_registry + coding_guidelines + universe_ruleset.md v1)** —
  `data_registry.md` đã xong từ 2026-07-22; **`cron_registry.md` hoá ra ĐÃ XONG cùng ngày**
  (commit `072dfbd6`, Winston — tracker này chỉ chưa cập nhật) — dòng 19:00 đã ghi rõ
  `build_universe_pit.py --date $TODAY` + `build_universe_pit_quality.py`; **`universe_ruleset.md`
  v1 cũng ĐÃ XONG từ G1** (`mike/kb/universe_ruleset.md`, commit `0551adbd`, cùng lúc builder được
  tạo — bị liệt kê nhầm "chưa làm" trong bảng §9 cũ). Việc thật sự còn thiếu = rule
  `coding_guidelines.md` cấm dạng `IN (SELECT DISTINCT ticker FROM ticker_prune)` không điều kiện
  `time` — **đã thêm §9b** (2026-09-19), trỏ về TRAP entry đã có sẵn chi tiết đầy đủ.
- **G9 (quant-skeptic full review toàn dự án)** — chạy xong 2026-09-19, verdict **REFUTED** (medium
  confidence) cho mệnh đề gộp "migration đã đóng hoàn toàn, không còn rủi ro live nào" — nhưng
  **CONFIRMED vững** cho kiến trúc lõi (B1-B8 point-in-time đúng, B8 integrity gate đã FIRE thật
  trong log production 08-31/09-01/09-02 chứ không chỉ unit test, threshold không bị tune ngầm,
  P1-P4 cutover byte-identical). Phát hiện MỚI, thật, mà review từng-mảnh không bắt được: **gate
  cứng G8.1 (cấm bật cờ executor.py trước khi migrate khỏi `ticker_prune`) đã bị VI PHẠM trong thực
  tế** — `chase_cap_vol_scale_enabled` lên LIVE 2026-08-04 trong khi
  `executor.py::_load_gap_ref_data()` vẫn đọc cache `ticker_prune`, vì review go-live tính năng đó
  không đối chiếu tracker migration. Mức độ THẤP (tra giá thuần, fail-safe về hướng chặt hơn,
  không phải look-ahead/rủi ro vốn) nhưng là vi phạm thật — đã cập nhật vào
  `kb/data_registry/price-volume/ticker_prune.md` (mục "VI PHẠM ĐÃ XẢY RA THẬT") + escalate bus
  `question` riêng (`Taylor/executor-chase-cap-still-reads-ticker-prune-20260919`) — **ĐÃ SỬA VÀ ĐÓNG
  2026-09-20** (user chốt Option A trên bus 03:46Z; commit `fd3f5597`:
  `_load_gap_ref_data()` đọc cache `tav2_bq.ticker` superset thay `ticker_prune`, kèm guard
  recency ≤10 ngày + contiguity ≤40 ngày do arch-reviewer yêu cầu; answer đóng bus 04:03Z).
  A/B đo lại 2026-09-24 trên cache thật (job `Taylor_20260923_235320`): 638 mã có gap-ref ở
  nguồn LIVE vs 204 ở nguồn cũ, **0 mã mất gap-ref** (không regression), 2 mã (C4G, PVI) đổi
  `prior_close` — nguyên nhân là tail per-ticker của `ticker_prune` dừng ở ngày mã đó RỜI
  universe (238/450 mã chung có tail cũ hơn; chỉ 2 mã rời trong vòng 10 ngày nên lọt qua guard
  recency), không phải bất đồng giá trị. Bổ sung `churn_guard_selfcheck.py` **section G** ghim
  NGUỒN dữ liệu bằng decoy fixture (section F không kill được mutation đổi nguồn). Hai điểm còn mở khác
  G9 xác nhận (không phải mới, nhưng vẫn treo thật): G7's câu hỏi liquidity-overlap (nay đã đóng ở
  trên) và khoảng hở fidelity R&D (`universe_pit` raw không nằm trong `sync_bq_cache.py`, backtest
  chạy dưới `BQ_LOCAL_CACHE` không bao giờ chạm breadth-decoupling guard — đã có bus event
  2026-09-17, không phải phát hiện mới của job này).

**Kết luận đóng backlog**: G7-G9 hoàn tất theo đúng định nghĩa gốc. G9 sinh ra **một** action item
mới (executor.py chase-cap) — đã tách thành câu hỏi bus riêng, không giữ G7-G9 mở vì nó.
