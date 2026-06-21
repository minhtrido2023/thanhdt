# BA-system v11 — Production Deployment Guide

**Version:** 11.0 (2026-05-12 production lock)
**Audience:** Backend developer deploying to fresh server
**Goal:** Reproduce the live recommendation engine + daily Telegram delivery end-to-end

---

## 0. TL;DR (5-minute version)

You're deploying a Vietnamese stock market signal engine that:
1. Pulls daily price + fundamentals data from BigQuery (`tav2_bq.*`)
2. Scores ~470 quality tickers with a 26-component formula (v10) + 5-state market regime
3. Filters via V11 stack (state-conditional Fresh-Q + market-overheat guards)
4. Outputs a 12-position watchlist (BAL book + VN30 book) split 50/50
5. Recommends ETF parking for idle cash (V6: 70% → VN30 ETF in NEUTRAL state)
6. Pushes the watchlist to a Telegram chat at 18:00 Mon-Fri

**Validated performance (2014-2026 backtest, 50B VND NAV):**
- CAGR 19.17% · Sharpe 1.56 · MaxDD -15.9% · Calmar 1.21

**Stack:**
- Python 3.11+ · pandas · numpy · requests
- Google Cloud SDK (`bq` CLI) with read access to `lithe-record-440915-m9.tav2_bq`
- Telegram bot
- cron/systemd (Linux) or Task Scheduler (Windows) for 18:00 daily trigger

**Total deploy time on a clean Linux VM: ~30 minutes** (excluding BQ access provisioning).

---

## 1. System Overview

### 1.1 What it does

The system answers ONE question every weekday at 18:00:
> "Given today's market close, which Vietnamese stocks should I buy at tomorrow's open? And where should idle cash sit?"

It outputs:
- **BAL book**: up to 10 stocks from the broad universe, max 4 in Fin/RE sector (plus 2 RE_BACKLOG exempt)
- **VN30 book**: up to 10 stocks from the 30 most-liquid names
- **ETF allocation**: 70% of idle cash → VN30 ETF if market regime is NEUTRAL
- **F-system overlay** (optional): VN30 futures position based on regime

Each stock position is sized to 5% of total NAV. Hold period 45 trading days, stop loss -20%, re-entry blacklist 20 days after stop.

### 1.2 Performance baseline (12-year backtest with current production config)

| Window | CAGR | Sharpe | MaxDD | Calmar | Win Rate |
|---|---|---|---|---|---|
| Full 2014-2026 (12y) | 19.17% | 1.56 | -15.9% | 1.21 | ~65% |
| OOS 2024-2026 | 28.87% | 2.02 | -9.6% | 3.01 | high |
| Pre-OOS 2014-19 | 8.88% | 1.61 | -7.7% | 1.15 | mid |
| VNINDEX B&H baseline | ~11.5% | 0.69 | -45.3% | 0.26 | — |

Alpha vs VNINDEX: **+7.7pp CAGR, half the drawdown, more than 2x Sharpe.**

### 1.3 Architecture (4 layers)

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 4: Output & Delivery                                  │
│  • recommend_holistic.py → CSV + console                     │
│  • telegram_recommend.py → Telegram HTML message             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│  LAYER 3: Strategy Logic (V11 production)                    │
│  • Tier classification (MEGA, MOMENTUM, MOMENTUM_N, etc.)    │
│  • V11 SV_TIGHT Fresh-Q filter (state-conditional)           │
│  • V11 P3 COMPOSITE overheat filter                          │
│  • Sector cap (Fin/RE max 4, RE_BACKLOG exempt)              │
│  • Book selection (BAL + VN30, 50/50 split)                  │
│  • V6 ETF parking advice (70% NEUTRAL)                       │
│  • F-system overlay (optional)                               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│  LAYER 2: Signal Generation (v10 score + 5-state regime)     │
│  • 26-component TA score (RSI, MA, MACD, PE z-score, etc.)   │
│  • FA tier lookup (point-in-time A/B/C/D/E from fa_ratings)  │
│  • 5-state regime from vnindex_5state                        │
│  • days_since_release computed point-in-time                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│  LAYER 1: Data (BigQuery tav2_bq)                            │
│  • ticker — daily OHLCV + indicators (canonical)             │
│  • ticker_1m — rolling 1-month snapshot (more recent data)   │
│  • ticker_prune — quality universe (449 tickers)             │
│  • fa_ratings — quarterly FA tiers (A-E)                     │
│  • ticker_financial — quarterly fundamentals + Release_Date  │
│  • vnindex_5state — market regime (1=CRISIS..5=EX-BULL)      │
└─────────────────────────────────────────────────────────────┘
```

### 1.4 Key design decisions (do not change without backtest)

1. **No look-ahead bias** — fa_ratings JOINed with point-in-time semantics (use `t.time >= fa.f_time AND t.time < fa.next_f_time`)
2. **Computed VNINDEX_RSI_Max3M** — the column was removed from `ticker` table; system now computes rolling MAX over 60 sessions
3. **Auto-fallback ticker → ticker_1m** — for dates after ticker daily refresh lag (typically T-2 to T-7)
4. **5-state forward-fill** — if `vnindex_5state` doesn't have today's row, use most-recent prior state
5. **Original (smoothed) 5-state, NOT v2g** — v2g was tested and rejected for BA-system (-2.40pp CAGR, see Section 11.4)

---

## 2. Data Layer: BigQuery Setup

### 2.1 Project & dataset

- **Project ID**: `lithe-record-440915-m9`
- **Dataset**: `tav2_bq`
- **Location**: `asia-southeast1`

### 2.2 Tables required (READ access)

| Table | Rows | Size | Update cadence | Schema |
|---|---|---|---|---|
| `tav2_bq.ticker` | ~15.2M | ~16.3 GB | Daily (~T-2 lag) | DAY-partitioned by `time`, clustered by `ticker` |
| `tav2_bq.ticker_1m` | ~26K | ~28 MB | **Daily ~16:00 VN time** | Rolling 1-month snapshot, same schema as ticker |
| `tav2_bq.ticker_prune` | ~711K | ~902 MB | Daily | Quality 449-ticker universe |
| `tav2_bq.fa_ratings` | ~12,400 | ~3 MB | Quarterly (after earnings) | ticker, time, tier (A-E), score_* (7 axes) |
| `tav2_bq.ticker_financial` | ~63.6K | ~54 MB | Quarterly | ticker, time, quarter, Release_Date, NP_P0..7, etc. |
| `tav2_bq.vnindex_5state` | ~6,268 | ~200 KB | When state recomputed (manual) | time, state (1-5) |

### 2.3 Critical columns (must exist on `ticker`)

Required for v10 score:
```
time, ticker, Close, Volume, Volume_3M_P50, Close_T1
MA20, MA50, MA50_T1, MA200, D_RSI, D_MACDdiff, D_RSI_Max1W
PE, PE_MA5Y, PE_SD5Y, FSCORE
NP_P0, NP_P1, NP_P4, ICB_Code
HI_3M_T1, ID_HI_3Y
```

Note: `VNINDEX_RSI_Max3M` is **NOT** in `ticker` anymore. The SQL computes it from rolling D_RSI of `ticker = 'VNINDEX'`.

### 2.4 Service account setup

Create a service account on Google Cloud with:
- **Role**: `BigQuery Data Viewer` on `lithe-record-440915-m9.tav2_bq`
- **Role**: `BigQuery Job User` on project

Download key JSON. Save as `~/.config/gcloud/sa-key.json` (Linux) or `%USERPROFILE%\.config\gcloud\sa-key.json` (Windows).

```bash
# Auth via service account (Linux/macOS/Windows)
gcloud auth activate-service-account --key-file=~/.config/gcloud/sa-key.json
gcloud config set project lithe-record-440915-m9
```

### 2.5 Test BQ connection

```bash
bq query --use_legacy_sql=false \
  'SELECT MAX(time) AS max_time, COUNT(DISTINCT ticker) AS n_tickers
   FROM tav2_bq.ticker_1m WHERE D_RSI IS NOT NULL'
```

Expected: `max_time` within last 2 business days, `n_tickers` ~450-500.

---

## 3. Code Structure

### 3.1 Production files (critical — must deploy)

| File | Purpose | Lines |
|---|---|---|
| `recommend_holistic.py` | **Main live engine** — daily watchlist generator | ~650 |
| `telegram_recommend.py` | Telegram bot wrapper | ~300 |
| `simulate_holistic_nav.py` | Backtest engine (used for validation, not daily run) | ~700 |
| `signal_v10_sql.py` | Clean SIGNAL_V10 SQL constant (no side effects) | ~90 |
| `fundamental_rating_all.csv` | **Local cache** of FA tiers (refreshed quarterly) | ~12k rows |

### 3.2 Configuration

| File | Purpose | Secret? |
|---|---|---|
| `telegram_config.json` | Bot token + chat ID | **YES — do not commit** |
| `.gitignore` | Excludes secrets + logs | No |

### 3.3 Validation / backtest scripts (optional, useful for sanity checks)

| File | Purpose |
|---|---|
| `test_state_var_with_p3.py` | V11 production backtest (7 variants × 3 periods) |
| `export_journal_v6_extended.py` | Trade journal export for any date range |
| `quarterly_walkforward.py` | Quarterly forward validation + traffic light status |
| `test_fresh_q_filter.py` | Validate Fresh-Q filter |
| `test_etf_parking.py` | Validate V6 ETF parking |

### 3.4 Operational files

| File | Purpose |
|---|---|
| `telegram_run_daily.bat` (Windows) | Scheduler wrapper |
| `telegram_run_daily.sh` (Linux — create as per Section 6) | Cron wrapper |
| `telegram_register_task.ps1` (Windows) | Task Scheduler registration |
| `telegram_run_YYYY-MM-DD.log` | Per-day output log (auto-rotated 30 days) |

### 3.5 Documentation (this repo)

| File | Purpose |
|---|---|
| `DEPLOYMENT.md` | **This file** — full deploy guide |
| `BA_SYSTEM_WORKFLOW.md` | Technical workflow reference |
| `TELEGRAM_SETUP.md` | Telegram-specific setup |
| `README.md` | Quick-start (5-minute version) |
| `requirements.txt` | Python dependencies |

---

## 4. Server Setup (Linux Ubuntu/Debian — recommended)

### 4.1 System requirements

- **OS**: Ubuntu 22.04 LTS or Debian 12 (any modern Linux works)
- **RAM**: 2 GB minimum, 4 GB recommended
- **CPU**: 1 vCPU sufficient (jobs are ~30s-2min)
- **Disk**: 5 GB free (for code + logs + caches)
- **Network**: Outbound HTTPS to googleapis.com, api.telegram.org

### 4.2 Install dependencies

```bash
# Update + base tools
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git curl wget tzdata

# Set timezone to Vietnam
sudo timedatectl set-timezone Asia/Ho_Chi_Minh

# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
# OR (if curl install fails)
# sudo apt install -y google-cloud-cli

# Verify
python3.11 --version  # expect 3.11.x
bq --version          # expect any recent version
```

### 4.3 Create deployment user

```bash
sudo useradd -m -s /bin/bash basystem
sudo usermod -aG sudo basystem  # optional: only if user needs sudo
sudo su - basystem
```

### 4.4 Clone repository

```bash
cd ~
git clone <your-repo-url> ba-system
# OR if no git: scp files from existing Windows machine
# scp -r /c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/* basystem@server:~/ba-system/

cd ~/ba-system
```

### 4.5 Python environment

```bash
python3.11 -m venv venv
source venv/bin/activate

# Install Python deps (see requirements.txt)
pip install --upgrade pip
pip install -r requirements.txt

# Verify imports work
python -c "import pandas, numpy, requests; print('OK')"
```

### 4.6 Google Cloud authentication

```bash
# Place service account key
mkdir -p ~/.config/gcloud
# Upload sa-key.json via scp or secrets manager
chmod 600 ~/.config/gcloud/sa-key.json

# Authenticate
gcloud auth activate-service-account --key-file=~/.config/gcloud/sa-key.json
gcloud config set project lithe-record-440915-m9

# Test
bq query --use_legacy_sql=false \
  --format=csv \
  'SELECT MAX(time) FROM `lithe-record-440915-m9.tav2_bq.ticker_1m` WHERE D_RSI IS NOT NULL'
# Expected output: a recent date (within 2-3 business days)
```

### 4.7 Path adjustments

**The current code uses Windows-style paths in some places.** Update the following:

In `recommend_holistic.py`, change:
```python
# OLD (Windows):
WORKDIR = r"C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude"
BQ_BIN = r"C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"

# NEW (Linux):
WORKDIR = "/home/basystem/ba-system"
BQ_BIN = "bq"   # assumes bq is on PATH
```

The `bq()` function builds a shell command that pipes a SQL file into `bq query`. The pipe `<` syntax works on both bash and cmd. Verify it works:

```bash
cd ~/ba-system
echo 'SELECT 1' > /tmp/test.sql
bq query --use_legacy_sql=false --format=csv < /tmp/test.sql
```

If you get authentication errors, set `GOOGLE_APPLICATION_CREDENTIALS`:
```bash
echo 'export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcloud/sa-key.json' >> ~/.bashrc
source ~/.bashrc
```

### 4.8 Smoke test

```bash
cd ~/ba-system
source venv/bin/activate
python recommend_holistic.py
```

Expected output:
```
========================================================================================
  🏆 BA-SYSTEM LIVE ENGINE — 2026-05-15
     Strategy: 50% BAL+Fin/RE-max-4 + 50% VN30_BAL  (D1+slot12: RE_BACKLOG exempt)
     PM: max=12pos, 10%/pos cap, hold=45d, stop=-20%, BL20, T+3 min hold
========================================================================================

[1/4] Loading TA v10 scoring + 5-state regime …
      474 tickers scored
[2/4] Loading FA 7-axis breakdown …
      653 tickers with FA snapshot
...
```

If you see this output, **Layers 1-3 work end-to-end.** Layer 4 (Telegram) covered next.

---

## 5. Telegram Bot Setup

### 5.1 Create Telegram bot

1. Open Telegram, search **@BotFather**
2. Type `/newbot`, choose name (e.g., "BA System Notifier")
3. BotFather returns `bot_token` like `1234567890:ABCdef...` — save this securely

### 5.2 Get chat ID

1. Open the bot you just created and send `/start`
2. In a browser, visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Look for `"chat":{"id":123456789,...}` — this is your `chat_id`
4. For group chats, `id` will be negative starting with `-100`

### 5.3 Configure credentials

```bash
cd ~/ba-system
cp telegram_config.template.json telegram_config.json
nano telegram_config.json
```

Fill in:
```json
{
  "bot_token": "1234567890:ABCdef...",
  "chat_id": "987654321",
  "send_charts": false,
  "include_universe_stats": true,
  "include_f_overlay": true
}
```

```bash
chmod 600 telegram_config.json  # secret — restrict access
```

### 5.4 Test send

```bash
cd ~/ba-system
source venv/bin/activate

# Dry-run first (no actual send)
python telegram_recommend.py --dry-run

# Real send
python telegram_recommend.py
```

You should see in Telegram:
- HTML-formatted message with regime + book picks
- (If signals exist) Two CSV attachments

---

## 6. Daily Scheduling

### 6.1 Linux cron (recommended)

Create wrapper script:

```bash
cat > ~/ba-system/telegram_run_daily.sh << 'EOF'
#!/bin/bash
# Daily BA-system Telegram notifier — runs Mon-Fri 18:00 VN time

cd "$HOME/ba-system"

# Activate venv
source venv/bin/activate

# Ensure BQ creds set
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcloud/sa-key.json

# Log file (per day)
LOGFILE="telegram_run_$(date +%Y-%m-%d).log"

echo "===== BA-system Telegram run started $(date) =====" >> "$LOGFILE"

# Run the notifier
python telegram_recommend.py >> "$LOGFILE" 2>&1
EXITCODE=$?

echo "===== Exit code: $EXITCODE at $(date) =====" >> "$LOGFILE"

# Cleanup logs older than 30 days
find . -name 'telegram_run_*.log' -mtime +30 -delete

exit $EXITCODE
EOF

chmod +x ~/ba-system/telegram_run_daily.sh
```

Add to cron:
```bash
crontab -e
```

Add the line (18:00 Mon-Fri, Vietnam time):
```
0 18 * * 1-5 /home/basystem/ba-system/telegram_run_daily.sh
```

Verify:
```bash
crontab -l
```

### 6.2 Alternative: systemd timer (more control)

Create unit files:

```bash
sudo nano /etc/systemd/system/ba-telegram.service
```

```ini
[Unit]
Description=BA-system Telegram daily notifier
After=network-online.target

[Service]
Type=oneshot
User=basystem
WorkingDirectory=/home/basystem/ba-system
ExecStart=/home/basystem/ba-system/telegram_run_daily.sh
StandardOutput=append:/home/basystem/ba-system/systemd_run.log
StandardError=append:/home/basystem/ba-system/systemd_run.log

[Install]
WantedBy=multi-user.target
```

```bash
sudo nano /etc/systemd/system/ba-telegram.timer
```

```ini
[Unit]
Description=BA-system Telegram daily — Mon-Fri 18:00 VN

[Timer]
OnCalendar=Mon..Fri 18:00:00 Asia/Ho_Chi_Minh
Persistent=true
RandomizedDelaySec=30s

[Install]
WantedBy=timers.target
```

Enable + start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ba-telegram.timer

# Verify
sudo systemctl list-timers | grep ba-telegram
sudo systemctl status ba-telegram.timer
```

Test trigger:
```bash
sudo systemctl start ba-telegram.service
# Check logs
journalctl -u ba-telegram.service --since "5 minutes ago"
```

### 6.3 Windows alternative (Task Scheduler)

If deploying to Windows server, use the existing scripts:
```cmd
cd C:\path\to\ba-system
powershell -ExecutionPolicy Bypass -File telegram_register_task.ps1
```

See `TELEGRAM_SETUP.md` for Windows-specific instructions including wake-from-sleep handling.

---

## 7. Production Logic Specification

This section is the **canonical reference** for the trading logic. The code implements this spec exactly.

### 7.1 v10 Score Formula (Layer 2 TA score)

Sum 26 boolean conditions. Max possible ≈ 194.

#### Momentum (max 113 pt)
| Condition | Points |
|---|---|
| `D_RSI > 0.50` | +25 |
| `Close > MA50 AND MA50 > MA200` | +25 |
| `Volume ≥ Vol_3M_P50 × 1.3 AND Close > Close_T1` | +20 |
| `D_MACDdiff > 0` | +15 |
| `Close > MA20` | +15 |
| `D_RSI > 0.75` | +5 |
| `D_RSI_Max1W > 0.65` | +5 |
| `ID_HI_3Y ≤ 5` (fresh 3Y high) | +8 |
| `D_RSI < 0.30` | **-10** |

#### Valuation
| Condition | Points |
|---|---|
| `PE < PE_MA5Y - 0.5×PE_SD5Y` (cheap) | +15 |
| `PE > PE_MA5Y + 1.0×PE_SD5Y` (expensive) | **-15** |

#### VNINDEX Context
| Condition | Points |
|---|---|
| `vni_max3m.rsi_max3m > 0.65` (computed from VNINDEX D_RSI rolling MAX 60 sessions) | +10 |

#### FA Quality
| Condition | Points |
|---|---|
| `FSCORE >= 8` (Piotroski) | +10 |
| `NP_P0 > 1.5 × NP_P4` (YoY strong) | +8 |
| `NP_P0 < 0.7 × NP_P4` (YoY decline) | **-8** |
| `NP_P0 > 1.2 × NP_P1` (QoQ accel) | +8 |

#### Sector tilt
| Condition | Points |
|---|---|
| `ICB_Code/1000 IN (8, 9)` (Fin/RE or Tech) | +5 |
| `ICB_Code/1000 IN (4, 7)` (Health or Utilities) | **-5** |

#### Trend confirmation (MA50 slope)
| Condition | Points |
|---|---|
| `MA50 > MA50_T1` | +5 |
| `MA50 > MA50_T1 × 1.005` | +5 |
| `MA50 < MA50_T1` | **-5** |
| `Close/HI_3M_T1 < 0.85` (deep drawdown) | **-10** |

#### v10 breakthrough (Fin/RE × FA interaction)
| Condition | Points |
|---|---|
| `sector=8 AND fa_tier='D'` | **+10** |
| `sector=8 AND fa_tier='A'` | **-10** |

### 7.2 Tier Classification (Layer 3)

After computing `ta_score`, classify into `play_type`. The CASE WHEN order matters:

```sql
CASE
  -- 1. Block: bear market or junk FA
  WHEN state5 IN (1, 2) THEN 'AVOID_bear'
  WHEN fa_tier = 'E' THEN 'AVOID_faE'

  -- 2. V11 D1 RE_BACKLOG_BUY (sector exempt)
  -- ICB 8633 + adv_yoy > 0.5 + FA C/D + ta ≥ 120 + state 3-5 + NP/Rev YoY > 0
  -- [Handled in Python classify_play_type, not SQL]

  -- 3. BA-core tiers
  WHEN ta ≥ 170 AND state5 IN (4,5) AND fa_tier IN ('C','D')       THEN 'MEGA'
  WHEN ta ≥ 170 AND state5 IN (4,5)                                THEN 'S_PRO'
  WHEN ta ≥ 155 AND state5 IN (4,5) AND fa_tier IN ('C','D')       THEN 'MOMENTUM'
  WHEN ta ≥ 155 AND state5 IN (4,5) AND fa_tier IN ('A','B')       THEN 'MOMENTUM_QUALITY'
  WHEN ta ≥ 155 AND state5 = 3   AND fa_tier IN ('C','D')         THEN 'MOMENTUM_N'
  WHEN fa_tier IN ('A','B') AND pe_z < -0.5 AND ta ≥ 95
       AND state5 IN (3,4,5) AND NOT warn_ext                       THEN 'COMPOUNDER_BUY'
  WHEN fa_tier = 'C' AND ta ≥ 100 AND state5 IN (4,5)
       AND (np_yoy > 0.20 OR rev_yoy > 0.20)                        THEN 'DEEP_VALUE_RECOVERY'
  WHEN ta ≥ 140 AND state5 IN (4,5)                                 THEN 'MOMENTUM_S'
  WHEN ta ≥ 125 AND state5 IN (4,5)                                 THEN 'MOMENTUM_A'
  WHEN ta ≥ 140 AND state5 = 3                                      THEN 'MOMENTUM_S_N'
  WHEN fa_tier IN ('A','B') AND ta ≥ 70 AND ta < 130                THEN 'COMPOUNDER_HOLD'
  WHEN fa_tier IN ('A','B')                                         THEN 'WAIT'
  ELSE 'PASS'
END
```

**BA_CORE_TIERS** = {MEGA, MOMENTUM, MOMENTUM_N, MOMENTUM_S, DEEP_VALUE_RECOVERY, RE_BACKLOG_BUY}

These are the only tiers eligible for new buy orders. Other tiers are watchlist-only.

### 7.3 V11 Production Filter Stack

After getting the candidate set (BA_CORE_TIERS), apply 3 sequential filters:

#### Filter 1: P3 COMPOSITE Overheat
**Block buys when:**
```
VNI_Close / VNI_MA200 > 1.30  AND  (state5 == 5  OR  VNI_D_RSI > 0.75)
```
- Anchor: `1.30` (validated robust over 12y)
- Regime confirmation: state5=5 (EX-BULL) OR VNI overbought (D_RSI > 0.75 on 0-1 scale)
- When triggered, demote all buy candidates to `AVOID_overheated`

#### Filter 2: SV_TIGHT State-Conditional Fresh-Q
Different `days_since_release` thresholds per state:
- State 1 (CRISIS): ≤ 30 days
- State 2 (BEAR): ≤ 60 days
- State 3 (NEUTRAL): ≤ 60 days
- State 4 (BULL): no filter
- State 5 (EX-BULL): no filter

Tickers exceeding threshold are skipped.

#### Filter 3: Sector Cap
- `Fin/RE (sector 8) max 4 positions`
- **Exempt**: `RE_BACKLOG_BUY` tier can slot beyond this cap

### 7.4 Book Selection

Sort candidates by `(priority desc, ta_score desc)` then fill up to `max_positions=12` total:

```
PRIORITY = {
    MEGA: 100, MOMENTUM: 88, MOMENTUM_N: 80,
    MOMENTUM_S: 72, DEEP_VALUE_RECOVERY: 70,
    RE_BACKLOG_BUY: 55
}
```

- **BAL book**: pick from full ticker_prune universe (with Fin/RE cap)
- **VN30 book**: pick from top-30 most-liquid tickers (no sector cap)
- 50/50 capital split between books (each gets 50% of total NAV)
- Within each book, each position sized to ~5% of total NAV (= 10% of book NAV)

### 7.5 V6 ETF Parking

Daily logic:
- Compute total cash = `NAV - sum(position_market_values)`
- If state5 == 3 (NEUTRAL): **target_etf = 70% × cash** in VN30 ETF (E1VFVN30)
- Otherwise: target_etf = 0% (all cash defensive)
- Rebalance only if drift > 0.5% of cash pool
- ETF earns VN30 daily return; minus 0.65%/yr management fee + 0.30%/yr tracking error
- Friction: 0.15% per side on rebalance

### 7.6 Position Management

- **Hold**: 45 trading days (TIME exit)
- **Stop loss**: -20% from entry (STOP exit)
- **T+3 min hold**: cannot sell before T+2 closes (2 sessions after entry)
- **Re-entry blacklist (BL20)**: 20 sessions after STOP exit
- **Multi-day fill**: max 5 days to complete fill; abandon if <30% filled
- **Liquidity cap**: 20% of daily ADV per session
- **Tiered exit slippage**: +0.1%/0.3%/0.5% extra if position > 5/10/20% of ADV
- **Friction**: TC 0.1% per side, capital gains tax 0.1% on sell

### 7.7 F-system Overlay (Optional 20% capital)

`F_HADAPTED_MAP` position by state:
- State 1 (CRISIS): -1.00 × VN30F (max short)
- State 2 (BEAR): -0.20 × VN30F (light short)
- State 3 (NEUTRAL): +0.70 × VN30F (long)
- State 4 (BULL): +1.00 × VN30F
- State 5 (EX-BULL): +1.30 × VN30F (leveraged long)

Net NAV exposure = position × 0.20 (20% capital). System OUTPUTS recommendation; user manually manages VN30F account.

---

## 8. Operational Procedures

### 8.1 Daily flow (automated)

```
15:00 VN     VN market close
~16:00       BigQuery ticker_1m refresh (data lag ~30-60min)
18:00 Mon-F  cron triggers telegram_run_daily.sh
             └→ python telegram_recommend.py
                ├─ [1/4] Load TA v10 + 5-state from BQ
                ├─ [2/4] Load FA 7-axis from fundamental_rating_all.csv
                ├─ [3/4] Load VN30 universe
                ├─ [4/4] Apply V11 filters + book selection
                ├─ Format HTML message
                ├─ POST to Telegram
                └─ Attach CSV files
             ├─ Log: telegram_run_YYYY-MM-DD.log
             └─ Output: holistic_YYYY-MM-DD.csv, ba_book_bal_*.csv, ba_book_vn30_*.csv

T+1 next     User executes book picks
session      - Buy each pick at 5% NAV
             - Park 70% of idle cash in VN30 ETF if NEUTRAL
             - Set stop -20%, hold 45d
```

### 8.2 Monitoring

#### Daily checks (automated alerts recommended)

Create `~/ba-system/monitor.sh`:
```bash
#!/bin/bash
# Verify last run was successful

LATEST_LOG=$(ls -t telegram_run_*.log 2>/dev/null | head -1)
if [ -z "$LATEST_LOG" ]; then
    echo "ALERT: No log file found"
    exit 1
fi

LAST_LINE=$(tail -1 "$LATEST_LOG")
if echo "$LAST_LINE" | grep -q "Exit code: 0"; then
    echo "OK: Last run succeeded"
else
    echo "ALERT: Last run failed → $LAST_LINE"
    exit 1
fi
```

Run on a separate schedule (e.g., daily 19:00) and pipe failure to alerting (PagerDuty/email/webhook).

#### Weekly: review log file

```bash
tail -100 telegram_run_$(date +%Y-%m-%d).log
```

Look for:
- BQ query errors
- Telegram API errors (rate limit, token revoked)
- Python tracebacks

#### Quarterly: walk-forward validation

Run quarterly walk-forward to detect performance drift:
```bash
python quarterly_walkforward.py 2026-06-30  # use latest quarter end
```

Check output:
- Trailing 3Y CAGR vs baseline 17.15%
- Trailing 5Y Sharpe vs baseline 1.21
- If RED on 2+ consecutive snapshots, investigate

### 8.3 Data refresh procedures

#### FA tier refresh (quarterly, manual)

After Q reports release (typically Apr 30, Jul 30, Oct 30, Jan 30):

```bash
cd ~/ba-system
source venv/bin/activate

# Refresh FA CSV cache (regenerate fundamental_rating_all.csv)
python fundamental_rating.py  # exact name TBD per upstream pipeline

# Verify tier counts
python -c "
import pandas as pd
df = pd.read_csv('fundamental_rating_all.csv')
df['time'] = pd.to_datetime(df['time'])
latest = df[df['time'] == df['time'].max()]
print(latest['tier'].value_counts())
"
```

#### 5-state refresh

The `vnindex_5state` table is recomputed manually after each session (or batched). Verify freshness:

```bash
bq query --use_legacy_sql=false --format=csv \
  'SELECT MAX(time) FROM tav2_bq.vnindex_5state'
```

If stale (>2 weeks), run the canonical state script:
```bash
python vnindex_5state_system.py
# Then upload to BQ (script TBD per upstream pipeline)
```

### 8.4 Pause / disable

To temporarily disable daily Telegram:
```bash
# Disable cron entry
crontab -e
# Comment out the 0 18 * * 1-5 line with #

# OR disable systemd timer
sudo systemctl disable --now ba-telegram.timer
```

---

## 9. Backtest Reproduction

To verify the deployment produces correct numbers, reproduce the V11 backtest:

```bash
cd ~/ba-system
source venv/bin/activate

# This will take ~10-15 minutes (caches signals on first run)
python test_state_var_with_p3.py
```

Expected output (FULL 2014-2026 window):
```
V4 SV_TIGHT(30/60/60)+P3                 19.17    1.56    -15.9   1.21     271
```

Tolerance: ±0.5pp CAGR, ±0.05 Sharpe — within data refresh and float-precision noise.

If results differ significantly:
- Confirm `vnindex_5state` table contains the SMOOTHED (original) state, not v2g
- Confirm `signal_v10_sql.py` uses the `vni_max3m` CTE (computed from VNINDEX D_RSI)
- Confirm `fundamental_rating_all.csv` is up-to-date

### 9.1 Other validation backtests

| Script | Period | Expected metric |
|---|---|---|
| `test_etf_parking.py` | 2014-2026 | V6 (70% NEU) CAGR 18.34%, Sharpe 1.11 |
| `test_fresh_q_filter.py` | 2014-2026 | F1 60d CAGR 16.55%, Sharpe 1.14 |
| `export_journal_v6_extended.py` | 2025-06 → 2026-04 | CAGR 25.82%, NAV end ~60.71B |

---

## 10. Configuration Reference

### 10.1 Hardcoded constants (in code)

These should NOT change without backtest re-validation:

| Constant | File | Value |
|---|---|---|
| `TC_BUY`, `TC_SELL` | simulate_holistic_nav.py | 0.001 (0.1%) |
| `CG_TAX` | simulate_holistic_nav.py | 0.001 (capital gain tax 0.1% on sell) |
| `MIN_HOLD` | simulate_holistic_nav.py | 2 sessions (T+3 rule) |
| `HOLD_DAYS` | simulate_holistic_nav.py | 45 days (default) |
| `STOP_LOSS` | simulate_holistic_nav.py | -0.20 (-20%) |
| `BL20 (blacklist days)` | simulate_holistic_nav.py | 20 sessions |
| `DEPOSIT_R` | simulate_holistic_nav.py | 0.01/252 (1%/yr realistic) |
| `LIQ_FLOOR` | recommend_holistic.py | 1.0 B VND/day |
| `liquidity_volume_pct` | recommend_holistic.py | 0.20 (20% ADV cap) |
| `max_fill_days` | recommend_holistic.py | 5 |
| `MAX_POSITIONS` | recommend_holistic.py | 12 (BAL: 10 base + 2 RE_BACKLOG exempt) |
| `FIN_RE_CAP` | recommend_holistic.py | 4 |
| `FRESH_Q_BY_STATE` | recommend_holistic.py | {1: 30, 2: 60, 3: 60} |
| `P3_VNI_MA200_THRESHOLD` | recommend_holistic.py | 1.30 |
| `P3_VNI_RSI_THRESHOLD` | recommend_holistic.py | 0.75 |
| ETF rebalance friction | simulate_holistic_nav.py | 0.0015 per side |
| ETF mgmt fee | simulate_holistic_nav.py | 0.0065/yr |
| ETF tracking drag | simulate_holistic_nav.py | 0.003/yr |

### 10.2 User configuration

`telegram_config.json`:
```json
{
  "bot_token": "...",
  "chat_id": "...",
  "send_charts": false,
  "include_universe_stats": true,
  "include_f_overlay": true
}
```

`telegram_run_daily.sh` (path adjustments only).

---

## 11. Known Issues & Lessons

### 11.1 ticker.VNINDEX_RSI_Max3M removed from schema
Previously, `tav2_bq.ticker` had a column `VNINDEX_RSI_Max3M` joined per-row. This was removed pre-2026-05. All current SQL files compute it via a CTE:
```sql
vni_history AS (SELECT time, D_RSI FROM tav2_bq.ticker WHERE ticker='VNINDEX' AND D_RSI IS NOT NULL),
vni_max3m AS (SELECT time, MAX(D_RSI) OVER (ORDER BY time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS rsi_max3m FROM vni_history)
```
If a developer pulls a backup containing the old SQL referencing `t.VNINDEX_RSI_Max3M`, the query will fail. Use the SIGNAL_V10 from `signal_v10_sql.py`.

### 11.2 ticker_1m doesn't have all columns
`ticker_1m` lacks some VNINDEX-joined columns. Auto-fallback logic in `recommend_holistic.py` handles this via:
- `latest_vni_max3m` CTE — freezes the last known value from `ticker`
- 5-state forward-fill from latest available `vnindex_5state` row

### 11.3 ticker_1m uses 'VNI' not 'VNINDEX'
The market-index symbol differs between tables:
- `ticker` table: `'VNINDEX'`
- `ticker_1m` table: `'VNI'`

UNION queries must handle both. See `export_journal_v6_extended.py:VNI_QUERY_UNIFIED`.

### 11.4 v2g 5-state — REJECTED for BA-system
A "v2g" version of the 5-state system was tested 2026-05-17. While it improved STANDALONE state-machine performance (+1.28pp CAGR), it HURT BA-system stack (-2.40pp CAGR, -6.9pp DD). Reverted via BQ table swap.

**For BA-system, ALWAYS use ORIGINAL (smoothed) 5-state.** Verify:
```sql
SELECT COUNT(*) FROM tav2_bq.vnindex_5state  -- expect 6268
SELECT MAX(time) FROM tav2_bq.vnindex_5state -- expect ~2026-04-28
```

If counts/dates differ, you may be on v2g. To restore:
```sql
CREATE OR REPLACE TABLE tav2_bq.vnindex_5state AS
SELECT * FROM tav2_bq.vnindex_5state_baseline_pre_v2g_20260517_144254;
```

### 11.5 Quarterly drift expected
The system has a known phenomenon: Trailing 3Y Sharpe and Calmar can flicker into "YELLOW/RED" status when a 3Y window happens to contain unusual periods (e.g., 2022 chop + missed 2025-Q4 rally). This is NOT system breakage — it's window variance.

Use Trailing 5Y as the more reliable health metric.

### 11.6 Earnings season (Apr-May, Jan-Feb)
During Q1 (Apr-May) and Q4 (Jan-Feb) earnings season, the SV_TIGHT Fresh-Q filter naturally defers entries until companies publish their latest report. This is by design — the filter avoids buying on stale fundamentals. Expect lower entry counts during earnings windows.

---

## 12. Troubleshooting

### 12.1 BQ query errors

**Error**: `Name VNINDEX_RSI_Max3M not found inside t`
**Fix**: SQL is using deprecated column. Replace with `vmax.rsi_max3m` after JOINing with the `vni_max3m` CTE. Use `signal_v10_sql.py:SIGNAL_V10` as reference.

**Error**: `Access Denied: BigQuery Permission ...`
**Fix**: Service account missing `BigQuery Data Viewer` role. Re-provision via Google Cloud Console.

**Error**: `bq: command not found`
**Fix**: Google Cloud SDK not on PATH. Run `source ~/.bashrc` or full path to `bq`.

### 12.2 Telegram errors

**Error**: `Bad Request: chat not found`
**Fix**: User has not started conversation with bot. Open bot in Telegram, send `/start`, then retry.

**Error**: `Unauthorized`
**Fix**: Bot token invalid or revoked. Generate new via @BotFather and update `telegram_config.json`.

**Error**: Message split into many chunks
**Cause**: Universe has many BA-core picks. Normal behavior; chunks send with 0.5s delay to avoid rate limit.

### 12.3 Sched task issues

**No log files appearing**
- Linux: `crontab -l` to verify cron entry. Check `/var/log/cron` for errors.
- Linux: Cron uses minimal env. Wrapper script must set `cd` + env vars + venv activation explicitly.
- Windows: Verify task is "Run only when user is logged on" matches deployment context.

**Task runs but no Telegram message**
- Check `telegram_run_YYYY-MM-DD.log` for Python errors
- Verify `telegram_config.json` exists and is readable by the task user

### 12.4 Stale state data

If `vnindex_5state.MAX(time)` is more than 2 weeks behind current:
- System uses forward-fill (uses latest available state for all newer dates)
- This is acceptable short-term but should be addressed: regenerate state table from latest VNI data

---

## 13. Disaster Recovery

### 13.1 BQ table corruption / accidental swap

Restore procedures:

```bash
# Check archive tables
bq ls --max_results=100 lithe-record-440915-m9:tav2_bq | grep -i "archive\|baseline\|backup"

# Restore vnindex_5state from baseline
bq query --use_legacy_sql=false \
  'CREATE OR REPLACE TABLE tav2_bq.vnindex_5state AS
   SELECT * FROM tav2_bq.vnindex_5state_baseline_pre_v2g_20260517_144254'

# Restore from v2g archive (if needed)
bq query --use_legacy_sql=false \
  'CREATE OR REPLACE TABLE tav2_bq.vnindex_5state AS
   SELECT * FROM tav2_bq.vnindex_5state_v2g_archive_20260512'
```

### 13.2 Code repository rollback

Maintain a git tag for known-good production state:
```bash
git tag -a v11-production-20260512 -m "BA v11 deployed with V6 ETF + F1 SV_TIGHT + original state"
git push origin v11-production-20260512

# Rollback if needed
git checkout v11-production-20260512
```

### 13.3 Config rotation

If `telegram_config.json` leaks:
1. `@BotFather` → `/revoke` to invalidate the bot token
2. `/newbot` to create a fresh one
3. Update `telegram_config.json` on server
4. `chmod 600 telegram_config.json`
5. Test send

---

## 14. Future Maintenance

### 14.1 Quarterly QWF check (mandatory)

End of each calendar quarter, run:
```bash
python quarterly_walkforward.py $(date +%Y-%m-%d)
```

Look at:
- `qwf_tracking_log.csv` for trend across quarters
- Latest snapshot status (GREEN/YELLOW/RED)

If 2+ consecutive YELLOW on Trailing 5Y: deeper investigation.

### 14.2 Annual FA tier audit

Once a year (around year-end), verify FA tier distribution hasn't drifted:
```sql
SELECT tier, COUNT(DISTINCT ticker) AS n
FROM tav2_bq.fa_ratings
WHERE time = (SELECT MAX(time) FROM tav2_bq.fa_ratings)
GROUP BY tier;
```

Expected: A ~30-50, B ~70-90, C ~90-110, D ~70-90, E ~30-50 per quarter.

### 14.3 Universe rotation (manual review every 1-2 years)

The `ticker_prune` universe is curated. Periodically review:
- Delisted tickers (drop)
- New listings with adequate history (consider adding)
- Quality threshold adjustments

This happens in the upstream data pipeline, not in this code.

---

## 15. Appendix

### 15.1 Glossary

| Term | Meaning |
|---|---|
| **BA-system** | Buy & Accumulate system — the production engine described in this doc |
| **5-state regime** | VNINDEX classification: 1=CRISIS, 2=BEAR, 3=NEUTRAL, 4=BULL, 5=EX-BULL |
| **BA-core tier** | A play_type eligible for new buy entries (vs informational tiers) |
| **TA score** | Technical analysis score (0-194), v10 formula |
| **FA tier** | Fundamental analysis tier A-E from `fa_ratings` table |
| **Fresh-Q filter** | Skip entries when latest quarterly report is too stale |
| **V11 SV_TIGHT** | State-conditional Fresh-Q thresholds (30d/60d/no-filter) |
| **V11 P3 COMPOSITE** | Market-overheat filter blocking buys in late-cycle |
| **V6 ETF parking** | Park idle cash in VN30 ETF during NEUTRAL state |
| **F-system overlay** | Optional VN30F position based on regime |
| **BAL book** | The first 50% of NAV allocated to the broad universe |
| **VN30 book** | The second 50% allocated to top-30 liquid tickers |
| **BL20** | 20-session blacklist after STOP/TRAIL exit |
| **T+3** | Vietnamese settlement: cannot sell within 2 sessions of buy close |

### 15.2 File index

```
ba-system/
├── DEPLOYMENT.md                       # This file
├── BA_SYSTEM_WORKFLOW.md               # Technical workflow detail
├── TELEGRAM_SETUP.md                   # Telegram setup specifics
├── README.md                           # Quick-start
├── requirements.txt                    # Python deps
├── .gitignore                          # Excludes secrets
│
├── recommend_holistic.py               # Live engine (Layer 4 main)
├── telegram_recommend.py               # Telegram wrapper
├── simulate_holistic_nav.py            # Backtest engine
├── signal_v10_sql.py                   # Clean SIGNAL_V10 import
│
├── telegram_config.json                # SECRET (gitignored)
├── telegram_config.template.json       # Template (commitable)
├── telegram_run_daily.sh               # Linux scheduler wrapper
├── telegram_run_daily.bat              # Windows scheduler wrapper
├── telegram_register_task.ps1          # Windows Task Scheduler register
│
├── fundamental_rating_all.csv          # FA tier cache (quarterly refresh)
│
├── test_state_var_with_p3.py           # V11 backtest validator
├── export_journal_v6_extended.py       # Trade journal export
├── quarterly_walkforward.py            # Quarterly forward validation
├── test_etf_parking.py                 # V6 ETF parking validation
├── test_fresh_q_filter.py              # Fresh-Q filter validation
│
├── deploy_linux.sh                     # Linux deploy automation
├── deploy_windows.ps1                  # Windows deploy automation
│
└── telegram_run_YYYY-MM-DD.log        # Daily log (auto-rotated)
```

### 15.3 Critical SQL: SIGNAL_V10

See `signal_v10_sql.py` for the full constant. Key structure:

```
WITH fa_dated AS (...),                    -- FA tier point-in-time
     fin_dated AS (...),                   -- ticker_financial point-in-time
     vni_history AS (...),                 -- VNINDEX D_RSI series
     vni_max3m AS (...),                   -- 60-session rolling MAX
     classified AS (
       SELECT t.ticker, t.time, t.Close,
         (...26 boolean conditions...) AS ta,
         s5.state AS state5,
         fa.fa_tier,
         ...
       FROM tav2_bq.ticker AS t
       LEFT JOIN tav2_bq.vnindex_5state AS s5 ON s5.time = t.time
       LEFT JOIN vni_max3m AS vmax ON vmax.time = t.time
       LEFT JOIN fa_dated AS fa ON ...
       LEFT JOIN fin_dated AS fin ON ...
       WHERE t.time BETWEEN '{start}' AND '{end}'
         AND t.ticker IN (SELECT ticker FROM ticker_prune)
     )
SELECT ticker, time, Close,
  CASE ... END AS play_type, ta, liq, sec
FROM classified WHERE liq >= 1e9
```

### 15.4 Sample Telegram message (NEUTRAL state)

```
🏆 BA-SYSTEM v11 LIVE — 2026-05-15
Sent: 2026-05-15 18:00 (next session T+1 entry)

Market regime: 🟡 NEUTRAL (state=3)

Strategy: 50% BAL+Fin/RE-max-4 + 50% VN30_BAL (RE_BACKLOG exempt)
PM: max=12pos · 10%/pos · hold=45d · stop -20% · BL20 · T+3 min hold
ETF parking V6: 70% idle cash → VN30 ETF (NEUTRAL only)
Fresh-Q SV_TIGHT: ≤30d state 1 / ≤60d state 2-3 / no filter state 4-5
Overheat P3: block buys when VNI/MA200>1.30 AND (state 5 OR D_RSI>0.75)

📋 BOOK A — BAL+Fin/RE-max-4 (50% NAV) (1 mã)

Ticker  Tier      Close   Sc  FA   RSI  Days
-----------------------------------------------
KBC     RE_BACKLOG  37,200  125   C  0.62    8d

📋 BOOK B — VN30_BAL (50% NAV)
   Không có signal — giữ cash cho book này.

🔄 F-system overlay (optional 20% capital)
   F_HAdapted target: +0.70x VN30 (LONG)
   Net VN30F exposure: +14.0% of total NAV

📊 Universe distribution
   BA-core: 1 mã | Compounder/info: 7 mã

💡 Execution checklist (T+1 next session)
   • BAL: 1 pos × 5% NAV = 5% deployed
   • VN30: 0 pos × 5% NAV = 0% deployed
   • Cash dư → 70% VN30 ETF (E1VFVN30)
   • Stop -20%, hold 45d, BL20 after stop
```

---

## 16. Contact / Handover

Once deployed and verified:
1. Save `git tag v11-production-deployed-YYYYMMDD`
2. Document any local config deviations in a `LOCAL_DEPLOY_NOTES.md`
3. Ensure scheduled task health-check is in monitoring (PagerDuty/email)
4. Schedule a 7-day post-deploy review to verify daily delivery + log health

End of document.
