#!/usr/bin/env python3
"""Tìm gốc cây WorkingClaude theo MARKER, không đếm cấp thư mục.

Vì sao tồn tại (sự cố 2026-09-12): `ROOT = dirname×3(__file__)` chỉ đúng cho BẢN GỐC
`mike/bin/`. Mọi bản sao chạy từ worktree `mike/agents/wt-*/bin/` cho ROOT =
`WorkingClaude/mike/agents` ⇒ `data/execution_logs` trỏ thư mục KHÔNG TỒN TẠI ⇒
`report_return_gate.py` fail-closed ⇒ **báo cáo nhà đầu tư không gửi được** (5 ca thật:
2026-07-03, 07-24, 07-31, 08-07 + 1 lần Errno 2). 3/3 worktree kiểm tra đều lệch.

`wc_env.sh` là marker DUY NHẤT **bên trong cây `WorkingClaude/`** (`find WorkingClaude -name
wc_env.sh` = đúng 1 kết quả, ở chính gốc) — đủ để đi lên từ `__file__` là xác định. KHÔNG phải
duy nhất trên máy: `/home/trido/thanhdt` còn ~12 bản, mỗi worktree của repo NGOÀI mang nguyên
một cây `WorkingClaude/` riêng (vd `thanhdt/wt-<id>/WorkingClaude/wc_env.sh`). Script chạy từ
bên trong một cây anh em như vậy sẽ neo vào ĐÚNG cây anh em đó — đúng theo nghĩa "gốc của tôi",
nhưng dữ liệu ở đó có thể rỗng/cũ. Đi lên gặp marker GẦN NHẤT là hành vi cố ý.

Override tường minh bằng biến môi trường `WC_ROOT` — TÁI DÙNG quy ước đã có ở
`forensic_flag_review_check.py`, không đặt tên mới. **Env được KIỂM CHỨNG, không tin mù**:
`bin/dispatch.sh` tự tính `WC_ROOT="$(cd "$ROOT/.." && pwd)"` — ĐÚNG PHÉP ĐẾM CẤP vừa bị kết
luận là sai — rồi export vào mọi phiên agent; bản sao dispatch.sh trong worktree export
`WC_ROOT=.../mike/agents` và sẽ tái hiện y nguyên sự cố nếu ta tin nó. Nên env chỉ được chấp
nhận khi thư mục đó THẬT SỰ có `wc_env.sh` (cùng cách `check_report_cadence.sh` kiểm).
"""
from __future__ import annotations

import os
import sys

MARKER = "wc_env.sh"


def find_wc_root(start: str) -> str:
    """Gốc WorkingClaude cho script `start` (truyền `__file__`).

    Thứ tự: env `WC_ROOT` **nếu thư mục đó có `wc_env.sh`** > đi lên tìm `wc_env.sh` >
    (cây bị cắt rời) hành vi cũ dirname×3.
    Fallback cuối KHÔNG ném lỗi ở import-time: script gọi nó vẫn phải chạy được trong môi
    trường test/CI không có cây thật, và lỗi "thiếu dữ liệu" ở dưới dễ đọc hơn ImportError.
    """
    env = os.environ.get("WC_ROOT")
    if env:
        env = os.path.abspath(env)
        if os.path.isfile(os.path.join(env, MARKER)):
            return env
        print(f"⚠️  bỏ qua WC_ROOT={env!r} — không có {MARKER} ở đó (dispatch.sh tính biến này "
              f"bằng đếm cấp, sai khi chạy từ worktree); tự tìm marker thay thế", file=sys.stderr)
    d = os.path.dirname(os.path.abspath(start))
    while True:
        if os.path.isfile(os.path.join(d, MARKER)):
            return d
        parent = os.path.dirname(d)
        if parent == d:                      # chạm "/" mà không thấy marker
            break
        d = parent
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(start))))
