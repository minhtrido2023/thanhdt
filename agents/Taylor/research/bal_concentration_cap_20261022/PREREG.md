# PREREG — Trần sizing BAL khi sổ ít mã (job Taylor_20261022_095008)

Ghi TRƯỚC khi chạy bất kỳ số backtest nào của job này. READ-ONLY với production: không sửa code canonical,
không pin registry, không ghi tên file canonical. Engine chạy trong worktree riêng, output vào thư mục này.

## Nguồn
- Control pin0% = ledger `data/pinned_ledgers/2026-09-28__R3-anchor-pin0pct-sexies__4707bcbe.csv.gz`
  (md5 raw `4707bcbeb7e801d49a4a851ffd91d5e7`). Control pin1M = `bcd0469f42c2f76937a6ebb10aae9b40`.
- Lệnh: đúng lệnh pin trong `PINS.jsonl` (env y nguyên, `$DNA_PYEXE`, `BQ_CACHE_THREADS=1`), code từ commit
  `f66dab18` (worktree đã sinh cả 2 md5 trên; có knob `IDLE_CARRY_TIER`). Self-check engine 0 VND bắt buộc.
- Universe: engine pin đã dùng `universe_pit` (tag `_univpit`). Không có code mới đọc nguồn dữ liệu mới.
- Live: `deploy_golive_dt5g_v4/out/golive_v23_recommendations_*.csv`, `data/trade_plans/plan_*.json`.
- Không dùng `profit_*` ở bất kỳ đâu.

## Q2/Q3 — đo trên ledger control (không chạy engine)
- "Lệnh BAL" = holding BAL có play_type ∈ {MEGA, MOMENTUM, DEEP_VALUE_RECOVERY, RE_BACKLOG_BUY} và biến thể
  `_W`. Loại `ETF_PARK`, `CAPITB_*` (sleeve CAPIT có sizing riêng, miễn stop/slot).
- n_bal(d) = số holding BAL mở cuối ngày d. Trọng số %NAV hệ của 1 lệnh =
  Σbuy_amount / nav_bal_ref(ngày vào) × s(ngày vào), với s = cap_bal / combined_nav.
- Q3 cửa sổ: 21 phiên không chồng lấn (bắt đầu từ phiên đầu ledger). P&L sleeve BAL-cổ phiếu =
  Δbal_stocks_ref + Σsell − Σbuy − Σfee của TX cổ phiếu BAL (KHÔNG ETF), quy về hệ × s(a) / combined_nav(a).
  Nhóm theo n_bal(a): **{1-2}** vs **{≥3}**; n_bal(a)=0 loại khỏi so sánh chính.
  Thước đo: tỉ lệ cửa sổ ≤ −0,70% NAV (p05 toàn mẫu job trước) và ≤ −1,07% (SpaceX live); Fisher exact
  2 phía. Phân vị live −1,07% / −0,55% trong nhóm {1-2}.
- Tỉ lệ STOP theo n_bal tại ngày vào (tính cả chính nó): {1-2} vs {≥3}, Fisher exact. Ghi chú: holding chồng
  thời gian không độc lập ⇒ p-value chỉ mang tính mô tả.

## Q4 — overlay trần (chạy engine)
- Knob `BAL_WMAX_NAV=w` (mặc định tắt ⇒ phải byte-identical control). Với lệnh BAL (định nghĩa trên) ở lần
  fill đầu: `target = min(target, (w / s(t−1)) × cur_nav_book)`, s(t−1) = cap_bal/combined_nav phiên trước
  lấy từ ledger control CÙNG quy ước (xấp xỉ 2-pass: s của đường control, không phải của đường bị cap —
  cố định trước, đo độ lệch thực bằng trọng số %NAV thực tế của chân cap).
- Tiền thừa: ở lại BAL book theo luật engine hiện hành của cấu hình pin (park `PARK_STATES=3:0.3`, tiền
  nhàn rỗi 0% ở pin0% / dep1m ở pin1M). Không thêm cơ chế mới.
- **Lưới cố định: w ∈ {3%, 4%, 5%}** × {pin0%, pin1M} = **N trial = 6** (+2 chân control). Không thêm lưới.
- Báo: CAGR, Sharpe, MaxDD, Calmar, worst 21-phiên, p01/p05 cửa sổ 21 phiên của combined, IS 2014-19 / OOS 2020+.

## Luật quyết định (khoá trước)
- "Không phá CAGR": ΔCAGR ≥ −0,46pp (sàn nhiễu W2b) ở CẢ hai quy ước.
- "Cải thiện đuôi": MaxDD tốt hơn ≥ 0,46pp VÀ p01 cửa sổ 21 phiên tốt hơn, ở CẢ hai quy ước, cùng dấu IS và OOS.
- Cả hai đạt ở ≥1 mức w ⇒ "có tín hiệu, cần quant-skeptic trước khi wire". Không thì **NO-GO**.
- Chênh < 0,46pp không đọc là cải thiện/xấu đi.
- Q3 "lệch live-backtest đo được" nếu nhóm {1-2} có tỉ lệ cửa sổ ≤ −0,70% cao hơn {≥3} với Fisher p<0,05;
  ngược lại nói rõ chưa đo được khác biệt.
