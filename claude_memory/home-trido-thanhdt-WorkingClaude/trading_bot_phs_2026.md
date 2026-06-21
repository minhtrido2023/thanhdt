---
name: trading-bot-phs-2026
description: "trading_bot/ package — bot 2 bước (bot_prepare_plan.py EOD → bot_execute.py trong phiên) mirror paper book V2.3 qua PHS FLEX, paper mode mặc định"
metadata: 
  node_type: memory
  type: project
  originSessionId: e2e7a996-fece-4ef4-860e-4337f05692c2
---

**trading_bot (built [REDACTED]12)** — bot giao dịch tự động trên [[phs_flex_api_wrapper_2026]], plan từ V2.3 ([[version_naming_v23_2026]]).

- **2 bước**: `bot_prepare_plan.py` (EOD, sau golive_recommend_v23 + pt_v22_dt5g) → `data/trade_plans/plan_<T+1>.json`; `bot_execute.py` (chạy xuyên phiên T+1) → journal/state/report trong `data/execution_logs/`.
- **Strategy versioning**: `trading_bot/strategies.py` REGISTRY; V23Strategy = mirror paper book scale theo NAV (`scale = NAV_thật/NAV_paper`); target = paper positions ∪ recs T+1 (BAL FULL/HALF, LAG "UPCOMING T+1", CAPIT nếu fired) ∪ ETF park; lệnh = diff vs danh mục thật; exit paper sync trễ 1 phiên (chấp nhận v1).
- **Executor slicing**: 1 lệnh con sống/parent; qty ≤ min(200M, 10% KL ngày); mua chase trần ref×1.015, bán sàn ref×0.97; treo quá 8' → hủy đặt lại; ATC sweep phần bán sót; resume từ state; kill = file `data/BOT_STOP`.
- **Mode paper (mặc định)**: quote THẬT PHS datafeed (quote-only, không cần login), khớp mô phỏng, tiền ảo `data/bot_paper_account.json`. **Live blocked** chờ PHS cấp client_id/secret (-700003); khi có: `bot_execute.py --mode live --otp <SmartOTP>`.
- **PHS quote mapping đã verify live**: last=closePrice, ref=reference, bid/ask=bidPrice1/offerPrice1, ce/fl=ceiling/floor, KL ngày=totalTrading. Payload thô log vào `phs_raw_<date>.jsonl`. Giá <500 tự ×1000 (normalize_price_vnd).
- **Multi-account ([REDACTED]12)**: profiles trong `data/trading_bot_accounts.json` (label/mode/credentials_file/account_id/overrides); hỗ trợ (a) nhiều tiểu khoản 1 login (FlexClient pool theo credentials file, chung token+OTP) + (b) nhiều login (token cache riêng). Mọi file namespace theo label (`plan_<label>_<date>.json`, `bot_paper_<label>.json`, `exec_<label>_*`). `run_session()` chạy mọi account 1 process, **quota participation gộp fleet** (sổ shared = đã khớp + đang treo/reservation, nhả khi hủy — fix bug test bắt được: thiếu reservation → 2 account vượt quota 2×). CLI: `--account <label>` lặp lại, `--otp label=123456`.
- Config: `data/trading_bot_config.json`. Test offline: `test_trading_bot.py` (fixture giả + multi-account + fleet quota, PASS). Docs: `trading_bot/README.md`.
- ⚠ Windows console cp1252: entry scripts phải `sys.stdout.reconfigure(encoding="utf-8")` (cả stderr) trước khi in tiếng Việt.
- **KẾ HOẠCH THỨ HAI [REDACTED]15 ~10:00 (user chốt, KHÔNG cần reminder)**: test đặt/hủy lệnh thật CẢ 2 BROKER trong phiên — `python dnse_order_test.py --send-otp` → `--otp <mã>` (DNSE, sẵn sàng) và `python phs_order_test.py --otp <SmartOTP>` (PHS — chỉ chạy được nếu PHS đã cấp client_id/secret, không thì vẫn -700003). Cả 2 script: LO mua 100 HPG giá SÀN → poll → hủy → confirm; có guard chặn ngoài giờ. Sau khi PASS: bật `[REDACTED]` enabled=true trong trading_bot_accounts.json để go-live (plan đầu SELL 5 vị thế cũ dọn về book V2.3 — user đã đồng ý).
