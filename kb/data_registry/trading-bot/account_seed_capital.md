---
kind: local-file
status: CANONICAL
source: "data/account_seed_capital.json (gitignored *.json — bản sao kiểm toán: agents/Taylor/research/aria_F_20260913/account_seed_capital.json)"
group: trading-bot
role: vốn đầu kỳ + lô legacy + fill broker xác nhận mà dnse_raw thiếu, cho reconcile_equity.py
writer: tay (Taylor, aria-F2 2026-09-13); reader: mike/bin/reconcile_equity.py (khi KHÔNG truyền --starting-capital)
---

# account_seed_capital.json

Mỗi account 1 entry: `nav` = totalCash − totalDebt + Σ qty×giá ngày go-live (dnse_raw balances+positions
lọc `account_no`, giá BQ `ticker.Price` KHÔNG điều chỉnh), `legacy_positions` {qty, price} — giá vốn GIẢ
ĐỊNH = MTM ngày seed, `missing_fills_broker_confirmed` — fill có trong email khớp lệnh/sao kê DNSE nhưng
dnse_raw không có.

Hiện có: **ZaloPay** (07-06, NAV 987.865.567). SpaceX KHÔNG có entry — vẫn truyền `--starting-capital`.

## Bẫy
- Truyền `--starting-capital` ⇒ file bị BỎ QUA hoàn toàn (không nạp legacy) — ZaloPay với placeholder 1B
  sẽ lệch ~95% NAV như trước.
- Thêm fill vào `missing_fills_broker_confirmed` chỉ khi có bằng chứng broker (msg id email / dòng sao kê);
  dnse_raw thiếu fill ⇒ reconcile in "KL replay ≠ broker" — đó là tín hiệu, đừng tắt.
