#!/usr/bin/env bash
# 5 selfcheck từng FAIL do sandbox thiếu đầu vào — chạy lại trong sandbox dựng bằng build_sandbox_full.sh.
WC="$1"; OUT="$2"; PYX=/home/trido/thanhdt/wc_venv/bin/python; mkdir -p "$OUT"; : > "$OUT/summary.txt"
run1() { local cwd="$1" label="$2"; shift 2
  ( cd "$cwd" && env -u TZ -u WC_ROOT -u MIKE_ROOT -u BQ_LOCAL_CACHE NO_GCE_CHECK=true PYTHONDONTWRITEBYTECODE=1 MIKE_BOT_TEST_MODE=1 \
      timeout 300 "$@" ) > "$OUT/$(echo "$label" | tr '/' '_').log" 2>&1
  echo "rc=$? $label" >> "$OUT/summary.txt"; }
for f in money_path_freshness_selfcheck.py freshness_ops_selfcheck.py dt5g_chain_freshness_selfcheck.py; do run1 "$WC" "$f" "$PYX" "$f"; done
run1 "$WC/mike" mike/agents/Winston/freshness_warn_selfcheck.py python3 agents/Winston/freshness_warn_selfcheck.py
run1 "$WC/mike" mike/bin/filter_lag_entry_window_selfcheck.py python3 bin/filter_lag_entry_window_selfcheck.py
cat "$OUT/summary.txt"
