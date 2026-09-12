#!/usr/bin/env python3
"""Tìm gốc cây WorkingClaude theo MARKER, không đếm cấp thư mục.

Vì sao tồn tại (sự cố 2026-09-12): `ROOT = dirname×3(__file__)` chỉ đúng cho BẢN GỐC
`mike/bin/`. Mọi bản sao chạy từ worktree `mike/agents/wt-*/bin/` cho ROOT =
`WorkingClaude/mike/agents` ⇒ `data/execution_logs` trỏ thư mục KHÔNG TỒN TẠI ⇒
`report_return_gate.py` fail-closed ⇒ **báo cáo nhà đầu tư không gửi được** (5 ca thật:
2026-07-03, 07-24, 07-31, 08-07 + 1 lần Errno 2). 3/3 worktree kiểm tra đều lệch.

`wc_env.sh` là marker DUY NHẤT của gốc — đã verify bằng `find . -name wc_env.sh` trên cả cây:
đúng 1 kết quả, tại `WorkingClaude/wc_env.sh`. Không thư mục con nào (kể cả worktree) có file
cùng tên, nên đi lên từ `__file__` tới thư mục chứa nó là xác định duy nhất.

Override tường minh bằng biến môi trường `WC_ROOT` — TÁI DÙNG quy ước đã có ở
`forensic_flag_review_check.py`, không đặt tên mới.
"""
from __future__ import annotations

import os

MARKER = "wc_env.sh"


def find_wc_root(start: str) -> str:
    """Gốc WorkingClaude cho script `start` (truyền `__file__`).

    Thứ tự: env `WC_ROOT` > đi lên tìm `wc_env.sh` > (cây bị cắt rời) hành vi cũ dirname×3.
    Fallback cuối KHÔNG ném lỗi ở import-time: script gọi nó vẫn phải chạy được trong môi
    trường test/CI không có cây thật, và lỗi "thiếu dữ liệu" ở dưới dễ đọc hơn ImportError.
    """
    env = os.environ.get("WC_ROOT")
    if env:
        return os.path.abspath(env)
    d = os.path.dirname(os.path.abspath(start))
    while True:
        if os.path.isfile(os.path.join(d, MARKER)):
            return d
        parent = os.path.dirname(d)
        if parent == d:                      # chạm "/" mà không thấy marker
            break
        d = parent
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(start))))
