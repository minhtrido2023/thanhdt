#!/usr/bin/env bash
# daily_refresh_v34b_linux.sh
# ============================================================================
# Linux-native daily refresh of the v3.4b BASE + DT5G live state on the server.
# Replaces the Windows daily_refresh_v3_4b.bat chain (whose deploy step uses
# backticks that /bin/sh mis-parses on Linux). Runs the full rebuild locally,
# loads to BQ tav2_bq.vnindex_5state, SYNCS _v34b_clean (nothing else does),
# then republishes vnindex_5state_dt5g_live.
#
# Auth: sources wc_env.sh -> CLOUDSDK_CONFIG = dtienthanh@gmail.com (read-WRITE).
# Schedule: cron Mon-Fri 18:30 ICT (after market close + ticker ingest; moved from a
# drifted 23:15 ICT slot 2026-07-10 — verified ticker_prune/ticker ingest actually completes
# well before 18:45 on a normal day, matching this script's own long-standing "~18:05" intent
# that the crontab had silently drifted ~5h away from). Step [0] below verifies the day's
# ingest is actually complete before computing, rather than trusting the clock alone.
# Log: data/refresh_v34b_linux_<YYYY-MM-DD>.log  (rolling, 30-day cleanup)
# ============================================================================
set -uo pipefail

source /home/trido/thanhdt/WorkingClaude/wc_env.sh
export STATE_WORKDIR="$WORKDIR_8L"
PY="$DNA_PYEXE"
PJ="lithe-record-440915-m9"
cd "$WORKDIR_8L"

LOG="data/refresh_v34b_linux_$(date +%Y-%m-%d).log"
exec >>"$LOG" 2>&1
echo "==================================================================="
echo "v3.4b/DT5G Linux refresh START $(date)  acct=$(gcloud config get-value account 2>/dev/null)"
echo "==================================================================="

die() { echo "!!! ABORT: $* (at $(date))"; exit 1; }
step() { echo; echo "--- $* ---"; }

# --- 0. freshness precheck: verify TODAY's ticker_prune ingest is actually complete before
# computing on it. Found 2026-07-10 (user asked "does this really need to wait for the full
# BQ sync?"): ticker_prune/ticker were BOTH already complete (normal-range row counts) well
# before this job's old 23:15 ICT slot — the schedule had drifted ~5h later than this script's
# own documented "~18:05 ICT" intent for no discovered reason, silently masked by
# bq_freshness_check.sh's MAX_STATE_LAG=2 tolerance (1-day-stale always passed as "fine").
# Rather than just picking a new fixed clock time and hoping it's always ready, verify the
# real artifact: retry with a bounded wait instead of computing on an incomplete/stale day.
step "[0] freshness precheck: today's ticker_prune ingest complete?"
TODAY_ICT="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
MIN_TICKERS=200   # historical daily count is ~260-270; 200 comfortably excludes a partial trickle
ready=0
for attempt in $(seq 1 6); do
  n="$(bq query --use_legacy_sql=false --project_id="$PJ" --format=csv --quiet \
    "SELECT COUNT(DISTINCT ticker) FROM tav2_bq.ticker_prune WHERE time = DATE('$TODAY_ICT')" \
    2>/dev/null | tail -1)"
  n="${n:-0}"
  if [ "$n" -ge "$MIN_TICKERS" ] 2>/dev/null; then
    echo "  ready: ticker_prune has $n tickers for $TODAY_ICT (attempt $attempt)"
    ready=1; break
  fi
  echo "  not ready yet: ticker_prune has ${n:-0} tickers for $TODAY_ICT (need >=$MIN_TICKERS) — attempt $attempt/6, waiting 15m"
  [ "$attempt" -lt 6 ] && sleep 900
done
[ "$ready" = 1 ] || die "ticker_prune still incomplete for $TODAY_ICT after 6 attempts (~1.5h) — refusing to compute DT5G on a stale/partial day. bq_freshness_check.sh's own gate will BLOCK DollarBill downstream since vnindex_5state_dt5g_live won't advance today."

# --- 1. upstream local rebuild (produces vnindex_5state_tam_quan_v3_4b_full_history.csv) ---
step "[1] clear pkl caches"
rm -f data/_cache_vnindex_2000_now.pkl data/_cache_universe_2013_now.pkl

step "[2] pull_us_market.py"
$PY pull_us_market.py || die "pull_us_market"

step "[3] ew_v1 (BQ ticker pull; retry x3 on flaky failure)"
ok=0
for try in 1 2 3; do
  if $PY vnindex_5state_ew_v1.py; then ok=1; break; fi
  echo "  ew_v1 attempt $try failed; clearing cache + retry"; rm -f _cache_universe_2013_now.pkl; sleep 5
done
[ "$ok" = 1 ] || die "ew_v1 failed after 3 attempts"

step "[4] build_concentration_history.py"; $PY build_concentration_history.py || die "concentration"
step "[5] vnindex_5state_dual_v3.py";      $PY vnindex_5state_dual_v3.py      || die "dual_v3"
step "[6] build_v3_1_clean.py";            $PY deploy_v3_4b_package/build_v3_1_clean.py || die "v3_1_clean"
cp data/vnindex_5state_tam_quan_v3_1_clean.csv data/vnindex_5state_tam_quan_v3_1_full_history.csv || die "cp v3_1"
step "[7] build_v3_4_bull_aware.py";       $PY deploy_v3_4b_package/build_v3_4_bull_aware.py || die "v3_4b"
step "[8] build_dt_4gate.py (local, non-fatal)"; $PY build_dt_4gate.py || echo "  WARN: dt_4gate failed (non-fatal)"

CSV="vnindex_5state_tam_quan_v3_4b_full_history.csv"  # build_v3_4_bull_aware.py saves to WORKDIR root (not data/)
LOCAL_MAX="$(tail -1 "$CSV" | cut -d, -f1)"
echo "local v3.4b CSV max date = $LOCAL_MAX"
[ -n "$LOCAL_MAX" ] || die "v3.4b CSV empty"

# --- 2. backup (dated, keep last 5) ---
step "[9] backup vnindex_5state + _v34b_clean (dated)"
TS="$(date +%Y%m%d_%H%M%S)"
bq query --use_legacy_sql=false --project_id="$PJ" \
  "CREATE TABLE \`$PJ.tav2_bq.vnindex_5state_archive_predeploy_$TS\` AS SELECT * FROM \`$PJ.tav2_bq.vnindex_5state\`" || die "backup bare"
# prune: keep newest 5 predeploy backups of the bare table
for old in $(bq ls --max_results=1000 tav2_bq 2>/dev/null | grep -oE 'vnindex_5state_archive_predeploy_[0-9_]+' | sort | head -n -5); do
  echo "  prune old backup $old"; bq rm -f -t "$PJ:tav2_bq.$old"
done

# --- 3. deploy: load bare, sync _v34b_clean ---
step "[10] bq load --replace vnindex_5state"
bq load --replace --source_format=CSV --skip_leading_rows=1 --location=asia-southeast1 \
  --schema=time:DATE,state:INT64,state_raw:INT64 \
  "$PJ:tav2_bq.vnindex_5state" "$WORKDIR_8L/$CSV" || die "bq load bare"

step "[11] sync _v34b_clean <- vnindex_5state"
bq query --use_legacy_sql=false --project_id="$PJ" \
  'CREATE OR REPLACE TABLE tav2_bq.vnindex_5state_tam_quan_v34b_clean AS SELECT * FROM tav2_bq.vnindex_5state' || die "sync _v34b_clean"

# --- 4. republish DT5G live ---
step "[12] publish_gated_state.py -> dt5g_live"
$PY deploy_golive_dt5g_v4/publish_gated_state.py || die "publish_gated_state"

# --- 5. verify ---
step "[13] verify freshness (base should match local CSV max=$LOCAL_MAX)"
BASE_MAX="$(bq query --use_legacy_sql=false --format=csv --project_id="$PJ" \
  'SELECT MAX(time) FROM tav2_bq.vnindex_5state_tam_quan_v34b_clean' 2>/dev/null | tail -1)"
LIVE_MAX="$(bq query --use_legacy_sql=false --format=csv --project_id="$PJ" \
  'SELECT MAX(time) FROM tav2_bq.vnindex_5state_dt5g_live' 2>/dev/null | tail -1)"
echo "  _v34b_clean max=$BASE_MAX   dt5g_live max=$LIVE_MAX   (local=$LOCAL_MAX)"
[ "$BASE_MAX" = "$LOCAL_MAX" ] || echo "  WARN: base BQ ($BASE_MAX) != local ($LOCAL_MAX)"

# --- 6. update macro_health ---
step "[14] macro_healthcheck.py (update macro_health.json)"
$PY macro_healthcheck.py || echo "  WARN: macro_healthcheck failed (non-fatal)"

# --- 7. local BQ snapshot (cache for Taylor experiments) ---
step "[15] Building local BQ snapshot..."
cd "$WORKDIR_8L" && $PY scripts/build_snapshot.py >> data/daily_refresh.log 2>&1 \
  && echo "  snapshot OK" || echo "  WARN: build_snapshot failed (non-fatal)"

# rolling 30-day log cleanup
find data -name 'refresh_v34b_linux_*.log' -mtime +30 -delete 2>/dev/null

echo; echo "==================================================================="
echo "v3.4b/DT5G Linux refresh DONE $(date)  base=$BASE_MAX live=$LIVE_MAX"
echo "==================================================================="
