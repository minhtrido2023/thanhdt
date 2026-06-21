#!/usr/bin/env bash
# run_8l_daily.sh — 8L daily EOD pipeline (Linux equivalent of pt_8l_daily.bat).
# Schedule via cron on trading days, ~17:45 ICT (before any 18:00 report consumer).
# Requires: WORKDIR_8L set, python on PATH (pandas/numpy/requests), `bq` CLI authenticated.
set -euo pipefail
export WORKDIR_8L="${WORKDIR_8L:?set WORKDIR_8L to the 8L install dir}"
cd "$WORKDIR_8L"
PY="${DNA_PYEXE:-python3}"
LOG="$WORKDIR_8L/data/pt_8l_daily_$(date +%F).log"
mkdir -p "$WORKDIR_8L/data"

echo "==== 8L daily $(date) ====" >"$LOG"
# Daily chain (light): rating -> screener -> rank -> dna -> vn30 basket -> alert -> buy-now
"$PY" rating_8l.py            >>"$LOG" 2>&1   # quality rating 1-5 + top30 + buynow
"$PY" unified_screener.py     >>"$LOG" 2>&1   # route + valuation + 8 lenses -> unified_screener.csv
"$PY" rank_8l.py              >>"$LOG" 2>&1   # composite route-aware score -> rank_8l.csv
"$PY" dna_card.py             >>"$LOG" 2>&1   # full-universe DNA cards -> dna_cards.csv
"$PY" vn30_8l.py              >>"$LOG" 2>&1   # deployable 8L-VN30 basket -> vn30_8l.csv
"$PY" rank_8l_daily_alert.py  >>"$LOG" 2>&1   # top-30 surprise-jump Telegram alert
"$PY" cheap_pb_floor.py       >>"$LOG" 2>&1   # rating x PB-floor buy-now Telegram alert
"$PY" -c "import bot_8l_commands as b; b.snapshot_today()" >>"$LOG" 2>&1  # dated rank snapshot (bot 'new')
echo "Done $(date)" >>"$LOG"

# ── PERIODIC FEEDER REFRESH (run weekly/after quarterly results or monthly-commodity update) ──
# These build the intermediate CSVs that unified_screener/rank_8l/dna_card consume. NOT in the daily
# chain because they depend on quarterly fundamentals + manually-updated monthly commodity files.
#   python bank_lens_v3.py          # bank NPL/CAR/coverage (uses vnstock) -> bank_lens_v3.csv
#   python power_lens.py            # ICB-7535 debt-lifecycle           -> power_lens.csv
#   python cash_machine_screen.py   # engine class (ROIC x runway)      -> cash_machine_screen.csv, engine_class.csv
#   python margin_cycle_detector.py # gross-margin cycle peak/bottom    -> margin_cycle_detector.csv
#   python saturation_detector.py   # TAM/runway saturation             -> saturation_detector.csv
#   python cyclical_structural.py   # commodity percentile x Brent      -> cyclical_structural.csv   (needs data/brent_monthly.csv)
#   python oil_transmission.py      # oil-chain transmission            -> uses data/oil_transmission_map.csv
#   python freight_map.py           # shipping freight cycle            -> freight_map.csv
#   python asset_play_detector.py   # NAV/SOTP asset-plays              -> asset_play.csv
