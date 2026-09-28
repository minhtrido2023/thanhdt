#!/usr/bin/env bash
# pin_artifact_gate_shim.sh <file> [...] — shim của hook `pin-artifact-gate` cho repo NGOÀI
# (/home/trido/thanhdt). File này do CHÍNH repo ngoài track; gate thật nằm ở repo LỒNG
# WorkingClaude/mike/bin/pin_artifact_gate.py.
#
# VÌ SAO CẦN SHIM: y hệt lý do của `tz_anchor_gate_shim.sh` (arch-review 2026-08-30 F1).
# `/home/trido/thanhdt/.gitignore:107` là `WorkingClaude/mike/` ⇒ repo ngoài KHÔNG track repo
# lồng ⇒ trong MỌI worktree/clone mới, `WorkingClaude/mike/` KHÔNG TỒN TẠI. Trỏ `entry` thẳng
# vào đó thì pre-commit chết cứng ("Executable ... not found") ngay cả trên file SẠCH.
#
# Quy tắc: THIẾU repo lồng = KHÔNG GATE ĐƯỢC, không phải = CHẶN. Báo ra stderr rồi exit 0.
# Fail-open đúng ở đây vì gate này bảo vệ kỷ luật TÀI LIỆU (số pin phải có artifact), không
# phải một lỗi làm mất tiền ngay; nó không được phép khoá đường commit của phiên khác vì một
# repo mà repo này còn không track.
# ⚠️ Hook PHẢI khai `verbose: true` trong .pre-commit-config.yaml — pre-commit chỉ in output
# hook khi rc!=0 hoặc verbose; gate này cố ý fail-open nên thiếu verbose thì fail-open biến
# thành FAIL-SILENT (đúng thứ §16 đã thua một lần).
# Bỏ qua có chủ đích:  SKIP=pin-artifact-gate git commit ...
set -uo pipefail

# Chỉ builtin của bash (parameter expansion + cd/pwd), KHÔNG gọi `dirname`: shim phải chạy
# được cả khi PATH nghèo nàn — `dirname: command not found` sẽ âm thầm làm GATE trỏ sai chỗ.
SELF="${BASH_SOURCE[0]}"
SELF_DIR="${SELF%/*}"
[ "$SELF_DIR" = "$SELF" ] && SELF_DIR="."
SELF_DIR="$(cd "$SELF_DIR" && pwd)"

GATE="$SELF_DIR/mike/bin/pin_artifact_gate.py"
if [ ! -f "$GATE" ]; then
  echo "⚠️  pin-artifact-gate: không thấy $GATE — repo lồng WorkingClaude/mike/ không có mặt" >&2
  echo "    ở checkout này (.gitignore của repo ngoài ẩn nó). KHÔNG GATE ĐƯỢC lần commit này." >&2
  echo "    Luật vẫn áp dụng: mục '## ' mới trong data/results_registry.md phải có" >&2
  echo "    'ledger_md5: <32 hex>' hoặc 'no_ledger: <lý do>'. Tự kiểm bằng tay." >&2
  exit 0
fi

# `python3` trần, KHÔNG $DNA_PYEXE — biến kế thừa có thể trỏ sai trong worktree (cùng lý do
# đã ghi ở tz_anchor_gate_shim.sh). Gate chỉ dùng stdlib (argparse/re/gzip/json/zoneinfo).
PY="$(command -v python3 2>/dev/null || true)"
if [ -z "$PY" ]; then
  echo "⚠️  pin-artifact-gate: không tìm thấy python3 trên PATH — KHÔNG GATE ĐƯỢC." >&2
  exit 0
fi

exec "$PY" "$GATE" "$@"
