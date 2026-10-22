#!/usr/bin/env bash
# livermore_run.sh [--as-of YYYY-MM-DD] [--triggers KIND1,KIND2]
# Dựng gói OHLCV VNINDEX as-of (500 phiên, KHÔNG DT5G, KHÔNG bar sau as-of) → chạy headless agent
# `livermore` ĐỌC MÙ → parse FORECAST/RESULT → ghi 1 entry append-only vào
# kb/data_registry/market-state/livermore_reads.md + báo cáo data/livermore/<as_of>.md.
# rc: 0 ghi xong (hoặc entry đã có — idempotent) · 1 lỗi (parse hỏng / as-of lệch / claude lỗi) — KHÔNG ghi entry nửa vời.
# Hook kiểm thử: LIVERMORE_CLAUDE_BIN (claude giả), LIVERMORE_BARS_CSV, LIVERMORE_REGISTRY, LIVERMORE_DATA_DIR.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" >/dev/null 2>&1 || true
export TZ=Asia/Ho_Chi_Minh
PY="${LIVERMORE_PY:-python3}"
CLAUDE_BIN="${LIVERMORE_CLAUDE_BIN:-claude}"
COMMON="$ROOT/bin/livermore_common.py"
AS_OF="-"; TRIGGERS="MANUAL"
while [ $# -gt 0 ]; do
  case "$1" in
    --as-of) AS_OF="${2:?--as-of cần giá trị}"; shift 2 ;;
    --triggers) TRIGGERS="${2:?--triggers cần giá trị}"; shift 2 ;;
    *) echo "usage: livermore_run.sh [--as-of D] [--triggers K1,K2]" >&2; exit 2 ;;
  esac
done
die() { echo "LIVERMORE-RUN-FAIL: $*" >&2; exit 1; }

# Thư mục làm việc NGOÀI repo: claude không nạp CLAUDE.md của repo (chứa DT5G) vào phiên đọc mù.
WORK="$(mktemp -d /tmp/livermore_run.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

_out="$("$PY" "$COMMON" package "$AS_OF" "$WORK/pkg.csv" 2>&1)" || die "dựng gói dữ liệu: $_out"
AS_OF="${_out%% *}"
echo "[livermore_run] package: $_out"

# Idempotent (§5): đã có entry as-of này thì không gọi LLM lần nữa.
REG="${LIVERMORE_REGISTRY:-$ROOT/kb/data_registry/market-state/livermore_reads.md}"
if [ -f "$REG" ] && grep -q "^### LVR-$AS_OF\$" "$REG"; then
  echo "[livermore_run] EXISTS LVR-$AS_OF — bỏ qua"; exit 0
fi

PROMPT="$("$PY" "$COMMON" prompt "$AS_OF" "$WORK/pkg.csv")"
set +e
( cd "$WORK" && timeout "${LIVERMORE_TIMEOUT:-900}" "$CLAUDE_BIN" -p --agent livermore \
    --tools "Read" --setting-sources user --no-session-persistence \
    --disallowedTools "Read(//home/trido/thanhdt/**)" "Read(//home/trido/.claude/projects/**)" \
    -- "$PROMPT" ) >"$WORK/report.md" 2>"$WORK/claude.err"
rc=$?
set -e
if [ $rc -ne 0 ]; then
  mkdir -p "${LIVERMORE_DATA_DIR:-$ROOT/data/livermore}"
  cp "$WORK/report.md" "${LIVERMORE_DATA_DIR:-$ROOT/data/livermore}/$AS_OF.FAILED.md" 2>/dev/null || true
  die "claude rc=$rc: $(head -c 400 "$WORK/claude.err")"
fi

if ! _fin="$("$PY" "$COMMON" finalize "$AS_OF" "$WORK/report.md" "$TRIGGERS" 2>&1)"; then
  mkdir -p "${LIVERMORE_DATA_DIR:-$ROOT/data/livermore}"
  cp "$WORK/report.md" "${LIVERMORE_DATA_DIR:-$ROOT/data/livermore}/$AS_OF.FAILED.md" 2>/dev/null || true
  die "parse/ghi entry: $_fin (báo cáo thô: data/livermore/$AS_OF.FAILED.md)"
fi
echo "[livermore_run] $_fin"
