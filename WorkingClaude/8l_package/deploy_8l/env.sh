# Source before running any 8L script:  source env.sh
# Uses already-set env if present (Docker/systemd), else sensible defaults. venv-optional.
export WORKDIR_8L="${WORKDIR_8L:-/opt/8l}"
export BQ_BIN="${BQ_BIN:-bq}"
export CLOUDSDK_PYTHON="${CLOUDSDK_PYTHON:-python3}"
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$WORKDIR_8L/sa-key.json}"
# python for dna_card subprocess: venv if present (bare-metal), else system python3 (container)
if [ -x "$WORKDIR_8L/venv/bin/python" ]; then export DNA_PYEXE="${DNA_PYEXE:-$WORKDIR_8L/venv/bin/python}"; else export DNA_PYEXE="${DNA_PYEXE:-python3}"; fi
