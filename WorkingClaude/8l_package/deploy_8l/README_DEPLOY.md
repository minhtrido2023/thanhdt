# 8L Services — Deployment Handover (Linux server, 24/7)

Move the 8L Telegram bot + daily-alert + quarterly paper-trade off the laptop onto an always-on Linux server.
Code is already made **portable** (reads paths from env vars; Windows defaults preserved). The dev only needs
to: copy files, set env vars, configure BigQuery auth, install deps, enable systemd + cron.

## What runs
| Service | What | Cadence | How |
|---|---|---|---|
| `telegram_8l_bot.py` | Interactive bot — user texts a ticker ("BMP", "BMP 8L") → replies 8L ranking/read | 24/7 long-poll | **systemd** (`8l-bot.service`) |
| `run_daily.sh` (5-step) | rating_8l → unified_screener → rank_8l → daily-alert (top-30 surprise) → cheap_pb_floor (buy-now). 2 Telegram alerts. | EOD ~17:45 ICT, Mon–Fri | **cron** |
| `pt_8l_quarterly.py` | Paper-trade: snapshot top-20 each quarter; review vs VNINDEX at quarter end | quarterly | **cron** |
| `power_lens.py` | Refresh power-sector lens (BQ-only, safe on server) | weekly | **cron** (optional) |

Daily chain detail: **`rating_8l.py`** = credit-style quality rating 1–5 across 7 routes (→ rating_8l.csv + top30 + buynow); **`cheap_pb_floor.py`** = rating × PB-floor × Ngũ Hành (DT5G market state from BQ `vnindex_5state_dt5g_live`) → buy-now Telegram alert. Both BQ-only for market data (rating_8l also reads cached bank_lens_v3.csv + power_lens.csv).

## Prerequisites
- Linux (Debian/Ubuntu assumed). Python 3.10+.
- **Google Cloud SDK** (`bq` CLI) installed — https://cloud.google.com/sdk/docs/install
- A **GCP service account** with roles `BigQuery Job User` + `BigQuery Data Viewer` on project
  `lithe-record-440915-m9`; download its JSON key → place as `<APP_DIR>/sa-key.json`.
- Telegram bot token + chat_id already in `telegram_config.json` (copy from laptop).

## Install (one-time)
```bash
sudo mkdir -p /opt/8l && sudo chown $USER /opt/8l
# 1) copy files per MANIFEST.txt into /opt/8l (keep the data/ subfolder structure)
# 2) deps + Cloud SDK
cd /opt/8l && bash deploy_8l/setup.sh
# 3) BigQuery auth (service account; no metadata server since not a GCP VM)
gcloud auth activate-service-account --key-file=/opt/8l/sa-key.json
gcloud config set project lithe-record-440915-m9
#    (and set GOOGLE_APPLICATION_CREDENTIALS in env.sh for the SDK path)
# 4) timezone (so cron 15:30 = trading close ICT). Either set server TZ:
sudo timedatectl set-timezone Asia/Ho_Chi_Minh
#    OR keep server UTC and use CRON_TZ in crontab (provided).
# 5) smoke test (rating_8l + power_lens have no Telegram; cheap_pb_floor DOES send → test last)
source /opt/8l/env.sh && source venv/bin/activate
python power_lens.py && python rating_8l.py && python unified_screener.py && python rank_8l.py
python rank_8l_daily_alert.py --no-telegram     # baseline, no send
# cheap_pb_floor.py sends Telegram on run — run once to confirm end-to-end (expected: 1 buy-now message)
```

## Enable services
```bash
# bot (systemd) — edit User=/paths in 8l-bot.service first
sudo cp deploy_8l/8l-bot.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now 8l-bot
sudo systemctl status 8l-bot      # should be active (running)
journalctl -u 8l-bot -f           # live logs

# cron (daily alert + quarterly) — review crontab.txt, then:
crontab deploy_8l/crontab.txt
crontab -l
```

## ⚠️ IMPORTANT — only ONE bot poller
Telegram allows a single getUpdates poller. **Stop the laptop bot before starting the server bot**
(else HTTP 409 conflict): on the laptop, delete `%Startup%\8L_Telegram_Bot.lnk`, stop the `8L_Telegram_Bot`
process, and disable the `8L_Daily_Alert` Windows task (the server takes over both).

## ⚠️ vnstock (bank lens refresh) — egress caveat
`bank_lens_v3.py` (refreshes `data/bank_lens_v3.csv`) uses **vnstock** (VN market data, VCI source).
From a non-VN server IP it may be blocked / DNS-flaky. Options:
- (a) Server in a VN-friendly region → test `python bank_lens_v3.py`; if OK, add to a weekly cron.
- (b) Keep bank refresh on the laptop; push `data/bank_lens_v3.csv` to the server (scp/rsync) periodically.
Everything else (power/cyclical/compounder/rank/bot/alert) is **BQ-only → works anywhere**.

## Files: see MANIFEST.txt.  Env vars: see env.sh.  Tunables: thresholds in rank_8l_daily_alert.py.
