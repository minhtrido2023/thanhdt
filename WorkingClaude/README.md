# BA-system v11 — Quick Start

Vietnamese stock market signal engine. Daily Telegram delivery of recommended stock picks for tomorrow's open.

## Performance baseline (validated 12-year backtest, 50B VND NAV)

| Window | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|
| **Full 2014-2026** | **19.17%** | **1.56** | **-15.9%** | **1.21** |
| OOS 2024-2026 | 28.87% | 2.02 | -9.6% | 3.01 |
| Pre-OOS 2014-19 | 8.88% | 1.61 | -7.7% | 1.15 |
| VNINDEX B&H baseline | 11.5% | 0.69 | -45% | 0.26 |

Alpha vs VNINDEX: **+7.7pp CAGR, half the drawdown.**

## 5-minute setup

### Linux server (recommended)

```bash
# 1. Install prerequisites
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip cron
curl https://sdk.cloud.google.com | bash && exec -l $SHELL

# 2. Upload code + sa-key
mkdir -p ~/ba-system ~/.config/gcloud
# scp -r ./* server:~/ba-system/
# scp sa-key.json server:~/.config/gcloud/

# 3. Run automated deployment
cd ~/ba-system
chmod +x deploy_linux.sh
./deploy_linux.sh

# 4. Configure Telegram (when prompted)
nano telegram_config.json  # add bot_token + chat_id

# 5. Test
source venv/bin/activate
python telegram_recommend.py --dry-run  # preview
python telegram_recommend.py            # real send
```

### Windows server

```powershell
# 1. Install Python 3.11+ from python.org
# 2. Install Google Cloud SDK from cloud.google.com/sdk
# 3. Run as Administrator:
powershell -ExecutionPolicy Bypass -File deploy_windows.ps1
```

## Documentation

| Document | Audience | Purpose |
|---|---|---|
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Developer deploying to server | Full deployment guide (this is the main doc) |
| [BA_SYSTEM_WORKFLOW.md](BA_SYSTEM_WORKFLOW.md) | Developer / quant | Technical workflow reference |
| [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) | Operator | Telegram bot specifics |

## Critical files

```
recommend_holistic.py          # Main live engine (Layer 4 output)
telegram_recommend.py          # Telegram bot wrapper
simulate_holistic_nav.py       # Backtest engine
signal_v10_sql.py              # Clean SIGNAL_V10 SQL constant
test_state_var_with_p3.py      # V11 backtest validator
fundamental_rating_all.csv     # FA tier cache (quarterly refresh)
telegram_config.json           # SECRET — gitignored
```

## Daily operation

```
15:00 VN    Market close
~16:00      BigQuery ticker_1m refresh
18:00 M-F   cron → telegram_recommend.py → Telegram message
T+1         User executes book picks at market open
```

## Production stack (v11.0 — 2026-05-12 production lock)

- **Score**: v10 (26-component formula + Fin/RE×FA-D bonus)
- **Tier classification**: V11 (adds RE_BACKLOG_BUY for ICB 8633 with advance customer surge)
- **State regime**: 5-state ORIGINAL (smoothed) — v2g rejected, see DEPLOYMENT.md §11.4
- **Position mgmt**: max 12 positions · 10%/pos · hold 45d · stop -20% · BL20 · T+3
- **Filters**:
  - V11 SV_TIGHT Fresh-Q (30d state 1 / 60d state 2-3 / no filter state 4-5)
  - V11 P3 COMPOSITE overheat (block buys when VNI/MA200>1.30 AND late-cycle)
- **Strategy**: 50/50 BAL+Fin/RE-max-4 + VN30_BAL split
- **ETF parking**: V6 (70% idle cash → VN30 ETF in NEUTRAL state)
- **F-system overlay**: Optional 20% capital, state-conditional VN30F

## Validation

```bash
source venv/bin/activate
python test_state_var_with_p3.py  # ~10-15 min, expect V4 CAGR ~19.17%
```

## Support / troubleshooting

See [DEPLOYMENT.md §12](DEPLOYMENT.md#12-troubleshooting) for common issues.

Key gotchas:
1. `tav2_bq.ticker.VNINDEX_RSI_Max3M` column was removed — system computes it via CTE
2. `ticker_1m` uses `'VNI'` not `'VNINDEX'` symbol for the index
3. v2g 5-state hurts BA-system — keep ORIGINAL smoothed version
4. FA tier cache (fundamental_rating_all.csv) needs quarterly refresh
