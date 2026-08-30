#!/usr/bin/env bash
# tz_anchor_gate_shim.sh <file.py> [...] — shim của hook `tz-anchor-gate` cho repo NGOÀI
# (/home/trido/thanhdt). File này do CHÍNH repo ngoài track; gate thật nằm ở repo LỒNG
# WorkingClaude/mike/bin/tz_anchor_gate.py.
#
# VÌ SAO CẦN SHIM (arch-review 2026-08-30 F1 — killer objection, đã repro trong sandbox):
# `/home/trido/thanhdt/.gitignore:107` là `WorkingClaude/mike/`. Repo ngoài KHÔNG track repo
# lồng ⇒ trong MỌI worktree mới và mọi clone mới, `WorkingClaude/mike/` KHÔNG TỒN TẠI. Trỏ
# `entry` thẳng vào đó thì pre-commit chết cứng ngay cả trên file SẠCH:
#     Executable `WorkingClaude/mike/bin/tz_anchor_gate.py` not found   → hook Failed, rc=1
# Phạm vi hook là `^WorkingClaude/.*\.py$`, gồm `bot_execute.py` + 17 file `trading_bot/*.py`
# ⇒ một hotfix chạm tiền thật commit từ worktree sẽ không commit được, và `MIKE_TZ_GATE=off`
# KHÔNG cứu được vì script chưa từng được chạy tới (`MIKE_TZ_GATE=off` chỉ cứu được khi gate
# CHẠY tới — nó là công tắc tắt hẳn bên trong gate, không phải bên ngoài).
# Đo lúc audit: 4/5 worktree ngoài lấy mẫu
# không có đường dẫn đó; cái thứ 5 sống nhờ một symlink làm tay.
#
# Quy tắc: THIẾU repo lồng = KHÔNG GATE ĐƯỢC, không phải = CHẶN. Báo ra stderr rồi exit 0.
# Fail-open ở đây là đúng: gate này chặn một lớp lỗi LATENT (giờ sai), không phải một lỗi làm
# mất tiền ngay; đổi lại nó không bao giờ được phép khoá đường commit của người khác vì một
# repo mà repo này còn không track. Muốn bỏ qua hook có chủ đích:  SKIP=tz-anchor-gate git commit
set -uo pipefail

GATE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/mike/bin/tz_anchor_gate.py"

if [ ! -f "$GATE" ]; then
  echo "⚠️  tz-anchor-gate: không thấy $GATE — repo lồng WorkingClaude/mike/ không có mặt ở" >&2
  echo "    checkout này (.gitignore của repo ngoài ẩn nó). $# file .py KHÔNG ĐƯỢC GATE." >&2
  echo "    coding_guidelines.md §16 vẫn áp dụng — tự kiểm datetime.now()/date.today() bằng tay." >&2
  exit 0
fi

exec "${DNA_PYEXE:-python3}" "$GATE" "$@"
