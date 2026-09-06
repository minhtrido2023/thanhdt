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
việc mới phát sinh từ audit 07-29 (Winston_20260729_132257): (1) migrate breadth-decoupling guard
`macro_state_live.py:158` sang `universe_pit` (đang chạy, cần self-check+quant-skeptic trước khi
wire — input DT5G production); (2) pin/snapshot BQ hàng tháng cho bảng dễ restate (`ticker`/
`ticker_financial`/`ticker_prune`/`universe_pit`/VNINDEX_PE, dispatch Winston đang chạy); (3)
WASHOUT_GATE đã tự verify KHÔNG cần rà lại (0,31 hiệu chuẩn đúng trên `universe_pit`, không phải
bug). Tài liệu đầy đủ:
`mike/agents/Taylor/research/ticker_prune_replacement_plan.md` +
`mike/agents/Winston/universe_pit_ops_feasibility_20260722.md` +
`mike/agents/Winston/research/ticker_prune_hidden_risk_audit_20260729.md`.
