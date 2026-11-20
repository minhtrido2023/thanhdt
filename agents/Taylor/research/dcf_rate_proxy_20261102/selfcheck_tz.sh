#!/usr/bin/env bash
# Chạy analysis.py dưới 3 môi trường TZ, so md5 out/*.csv (trừ file của extra.py)
set -euo pipefail
H="$(cd "$(dirname "$0")" && pwd)"; PY=/home/trido/thanhdt/wc_venv/bin/python
source /home/trido/thanhdt/WorkingClaude/wc_env.sh >/dev/null 2>&1 || true
cd "$H"
run() { local tag="$1"; shift; "$@" "$PY" analysis.py > "out/run_tz_${tag}.txt" 2>&1; (cd out && md5sum monthly_series.csv episodes.csv episodes_avg3_ngoai_prereg.csv leadlag.csv leadlag_ci.csv d3m_corr.csv selection.csv scen_*.csv) > "out/md5_${tag}.txt"; }
run default env
run noTZ env -u TZ
run NY env TZ=America/New_York
diff out/md5_default.txt out/md5_noTZ.txt && diff out/md5_default.txt out/md5_NY.txt && echo "TZ md5 IDENTICAL (default / env -u TZ / America/New_York)"
"$PY" selfcheck.py
env -u TZ "$PY" selfcheck.py | tail -1
