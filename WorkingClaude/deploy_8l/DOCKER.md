# 8L — Docker deploy (compact, self-contained)

One image (`google/cloud-sdk:slim` + bq + python deps + app), two services:
- **bot** — 24/7 interactive Telegram bot
- **cron** — runs the daily 5-step chain (17:45 ICT Mon–Fri) + quarterly paper-trade

## Prereqs (on the server)
- Docker + docker compose plugin.
- Copy the repo (per `MANIFEST.txt`) to the server. At the **repo root** place:
  - `sa-key.json`  — GCP service-account key (BigQuery Job User + Data Viewer on `lithe-record-440915-m9`)
  - `telegram_config.json` — bot token + chat_id (from the laptop)

## Run (2 commands)
```bash
cd <repo-root>/deploy_8l
docker compose up -d --build
```
That's it. Bot is live 24/7; cron fires the daily/quarterly jobs. Data persists in `../data` (host volume).

## Verify / operate
```bash
docker compose ps                          # both services Up
docker compose logs -f bot                 # bot polling + queries
docker compose logs -f cron                # cron daemon
docker compose exec cron python3 rating_8l.py        # run a step manually
docker compose exec cron bash -lc 'source deploy_8l/env.sh && python3 rank_8l_daily_alert.py --no-telegram'
docker compose down                        # stop
```

## ⚠️ Before starting: only ONE Telegram poller
Stop the laptop bot first (delete `%Startup%\8L_Telegram_Bot.lnk`, kill the process, disable the
`8L_Daily_Alert` Windows task) — else Telegram returns 409 (two getUpdates pollers).

## Notes
- Timezone baked as `Asia/Ho_Chi_Minh` (cron 17:45 = correct close-of-session time).
- vnstock (bank-lens refresh) NOT in the image/cron — keep refreshing `data/bank_lens_v3.csv` on the
  laptop and it syncs via the `../data` volume, OR add a cron line if the server can reach VCI.
- Secrets are **mounted read-only at runtime**, never baked into the image (see .dockerignore).
