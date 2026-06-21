# secrets/ — credentials (NOT committed)

This folder holds all live credentials and is **gitignored**. Values live only
on the server. When resuming on a fresh machine, recreate these files here:

| File | Purpose | Source / template |
|------|---------|-------------------|
| `phs_secret.json` | PHS API client_id / client_secret | keys: `PHS_CLIENT_ID`, `PHS_CLIENT_SECRET` |
| `phs_credentials.json` | PHS login (username/password/client pair) | broker |
| `dnse_credentials.json` | DNSE API key/secret | broker |
| `telegram_config.json` | Telegram bot_token + chat_id | `telegram_config.template.json` |
| `trading_bot_accounts.json` | trading bot account list | `trading_bot/` |
| `trading_bot_config.json` | trading bot config | `trading_bot/` |
| `bot_paper_account.json`, `bot_paper_dnsetest.json` | paper-trading state | auto |
| `sa-key.json`, `gcp_credentials.json` | GCP service-account / OAuth (BQ) | Google Cloud |

Notes:
- BigQuery auth for cron jobs uses `CLOUDSDK_CONFIG=../gcloud_dtienthanh` (ADC),
  not `sa-key.json` — see `wc_env.sh`.
- Code reads these via `os.path.join(WORKDIR, "secrets", "<file>")`. PHS secrets
  can alternatively be supplied via env vars (`PHS_CLIENT_ID`, `PHS_CLIENT_SECRET`).
- Token caches (`dnse_trading_token.json`, `phs_flex_token.json`) are regenerated
  at login and live in `data/`, not here.
