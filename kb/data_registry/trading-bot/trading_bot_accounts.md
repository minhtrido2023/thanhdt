---
kind: config
status: CANONICAL
source: secrets/trading_bot_accounts.json
group: trading-bot
role: money-path config
writer: con người/Mike khi onboard hoặc đổi config
---

# secrets/trading_bot_accounts.json

**Status: CANONICAL (config)**

## Là gì
Hồ sơ account (enabled/mode/broker, `excluded_tickers`, override paper: extreme_regime, chase_cap).

## Ai ghi / cadence
Con người/Mike khi onboard hoặc đổi config.

## Bẫy
`excluded_tickers` case-sensitive (selfcheck đã cover); account mới `enabled:true/mode:live` TỰ ĐỘNG
được cron dùng-chung nhận — thêm account = kiểm tra lại toàn bộ điểm đọc file này.
