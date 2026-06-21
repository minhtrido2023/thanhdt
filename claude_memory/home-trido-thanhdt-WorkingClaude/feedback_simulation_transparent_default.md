---
name: feedback-simulation-transparent-default
description: "Khi user yêu cầu chạy simulation, MẶC ĐỊNH dùng transparent pattern (event_log + reconciliation), không cần hỏi."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 58667b68-fff4-4b9a-abbd-ac6945b7b8b3
---

Mỗi khi user yêu cầu chạy simulation (BA v11 / v12 / v13... bất kỳ phiên bản nào), **default phải chạy theo transparent pattern** giống `sim_v12_transparent.py` / `sim_v11_transparent.py`. Không cần hỏi user xác nhận, không chạy bản tối giản trước.

**Why**: User yêu cầu rõ 2026-05-20 sau khi tôi chạy bản tối giản v12 đầu tiên (chỉ in metrics). User muốn kết quả luôn có thể tái tạo NAV từ giao dịch để đảm bảo đúng đắn — đây là tiêu chuẩn cố định, không phải request một lần.

**How to apply** — mỗi sim phải emit đủ bộ output `analyze_portfolio.py`-compatible:

1. **Truyền `event_log=[]`, `etf_log=[]`, `force_close_eod=False`** vào `simulate()` cho mỗi book stock chính (BAL, VN30, hoặc book khác).
2. **Custom loop** (LAGGED, F-system, etc.) phải tự append event dict với schema chuẩn: `{ymd, ticker, action(buy/sell), buy_amount, sell_amount, fee, adj_price, shares, holding_id, play_type, cash_after, reason, book}`.
   - `buy_amount` = clean share cost (no fee). Cash deducted = `buy_amount + fee`.
   - `sell_amount` = clean gross. Cash received = `sell_amount − fee`.
3. **MTM_UNREALIZED phantom rows** cho mọi open position cuối kỳ (stocks + ETF lots) với cùng `holding_id` như buy → để `analyze_portfolio.py` group đúng cặp.
4. **Save 4 files** vào `data/`:
   - `<name>_logs.csv` — daily NAV + per-book cash/stocks/etf + n_pos + n_tx + state
   - `<name>_transactions.csv` — mọi buy/sell + ETF rebalance + MTM phantoms
   - `<name>_open_positions.csv` — open lots với cost_basis/mark/unrealised
   - `<name>_report.md` — output của `analyze_portfolio.py` + reconciliation block ghi nối thêm
5. **Reconciliation block bắt buộc** trong report, verify 4 gate (mọi delta phải = 0):
   - `init − Σ(buys+fees) + Σ(sells−fees) = end_cash` (từ tx CSV)
   - `cash + cash_etf + stocks_mv = NAV` mỗi ngày
   - `Σ MTM stocks = stocks_mv[−1]`, `Σ MTM ETF = cash_etf[−1]`
   - Mỗi open có buy match holding_id + MTM phantom sell match
6. **Run `analyze_portfolio.py`** sau khi save CSV xong; append reconciliation block sau output của nó.
7. **In tóm tắt cho user** theo style đã thiết lập: bảng metrics + per-leg breakdown + 4-gate reconciliation pass + danh sách files (xem session 2026-05-20).

**Pattern reference**: `sim_v11_transparent.py` (BAL+VN30+ETF), `sim_v12_transparent.py` (BAL+LAGGED+ETF). Khi tạo phiên bản mới (v13 Tam Thế etc.), copy 1 trong 2 file này làm template.

Liên quan: [[v11-transparent-sim-bugs-fixed]], [[ba-v12-am-duong-spec]].
