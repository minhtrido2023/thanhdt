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
    walked = _walk_to_marker(start)
    env = os.environ.get("WC_ROOT")
    if env:
        env = os.path.abspath(env)
        if os.path.isfile(os.path.join(env, MARKER)):
            if walked and os.path.realpath(walked) != os.path.realpath(env):
                # Env hợp lệ nhưng trỏ cây KHÁC cây chứa script (vd một `WorkingClaude` anh em
                # có marker nhưng `data/` rỗng). Không đổi hành vi — override tường minh vẫn
                # thắng — nhưng phải nhìn thấy được: rủi ro ở đây là GHI vào nhầm cây
                # (`nav_history_*.csv`), thứ không tự báo lỗi như đọc thiếu dữ liệu.
                print(f"⚠️  WC_ROOT={env!r} khác cây chứa script ({walked!r}) — vẫn dùng "
                      f"WC_ROOT theo override; kiểm tra nếu script này GHI dữ liệu",
                      file=sys.stderr)
            return env
        print(f"⚠️  bỏ qua WC_ROOT={env!r} — không có {MARKER} ở đó (dispatch.sh tính biến này "
              f"bằng đếm cấp, sai khi chạy từ worktree); tự tìm marker thay thế", file=sys.stderr)
    if walked:
        return walked
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(start))))


def _walk_to_marker(start: str):
    """Thư mục gần nhất đi LÊN từ `start` có `wc_env.sh`; None nếu chạm "/" mà không thấy."""
    d = os.path.dirname(os.path.abspath(start))
    while True:
        if os.path.isfile(os.path.join(d, MARKER)):
            return d
        parent = os.path.dirname(d)
        if parent == d:                      # chạm "/" mà không thấy marker
            return None
        d = parent


MIKE_MARKER = "MIKE.md"


def find_mike_canonical_root(start: str) -> str:
    """Gốc CANONICAL của checkout `mike` — cây giữ SỔ dùng chung, không phải cây đang chạy.

    Khác `find_wc_root()` ở mục đích: `find_wc_root` trả về "cây CỦA TÔI" (đúng cho dữ liệu
    đọc-theo-cây như `data/execution_logs`). Hàm này trả về "cây của CẢ FLEET" — dùng cho state
    dùng chung mà `.gitignore` không đồng bộ, cụ thể `state/report_delivery.json`: sổ giao hàng
    báo cáo nhà đầu tư. Sổ phân mảnh = một lần giao hàng từ worktree là VÔ HÌNH với
    `check_report_cadence.sh` ⇒ gửi TRÙNG cho nhà đầu tư (đã xảy ra: monthly 2026-08 gửi
    2026-08-28 từ `mike_paseo` rồi gửi lại 2026-09-02 từ canonical — sổ canonical không hề biết
    lần đầu).

    Quy tắc: `<find_wc_root()>/mike` (có `MIKE.md`). KHÔNG dùng heuristic "`.git` là THƯ MỤC thì
    là canonical, là FILE thì là worktree" — nghe hợp lý nhưng SAI trên chính máy này:
    `WorkingClaude/mike_paseo/.git` là thư mục thật (clone riêng) mà vẫn là cây phụ, và chính nó
    là cây đã ghi 32 entry vào sổ lạc. Neo theo ĐƯỜNG DẪN quy ước thì cả worktree
    (`mike/agents/wt-*`, `WorkingClaude/wt-*`), clone phụ (`mike_paseo`) lẫn bản sao tạm cùng
    độ sâu đều quy về một sổ.

    Cây `WorkingClaude` ANH EM (`thanhdt/wt-*/WorkingClaude/`) vẫn neo vào `mike` của CHÍNH nó —
    cố ý, giống `find_wc_root`: đó là fleet khác, không phải worktree của fleet này.

    KHÔNG nhận override qua biến môi trường — khác `find_wc_root()` một cách có chủ ý. "Cây của
    tôi" thì hợp lý để override; SỔ DÙNG CHUNG thì không: chỉ cần một biến env trỏ cây khác là
    sổ lại phân mảnh đúng như sự cố vừa vá, mà lần này không ai nhìn thấy.
    Fallback khi không dựng được (bản sao rời, không có `wc_env.sh` ở bất kỳ cấp nào): trả về
    hành vi cũ `dirname×2(start)` — không ném lỗi, để test/CI vẫn chạy được.
    """
    # KHÔNG có env override ở đây, và CỐ Ý KHÔNG đi qua `find_wc_root()`: hàm đó nhận env `WC_ROOT`, mà `dispatch.sh` export
    # `WC_ROOT` của CÂY NÓ ĐANG CHẠY vào mọi phiên agent. Sổ giao hàng là SINGLETON của fleet,
    # không phải "cây của tôi": nhận env ở đây nghĩa là một phiên neo ở cây `WorkingClaude` anh
    # em (trên máy này có 2 cây như vậy, mỗi cây một sổ 56KB) sẽ ghi sổ vào đó — tái hiện đúng
    # phân mảnh vừa vá, lần này qua env (arch-review vòng 2, 2026-09-12). Neo THUẦN theo vị trí
    # file: tất định, không phụ thuộc ai gọi mình.
    walked = _walk_to_marker(start)
    canonical = os.path.join(walked, "mike") if walked else ""
    if canonical and os.path.isfile(os.path.join(canonical, MIKE_MARKER)):
        return canonical
    running = os.path.dirname(os.path.dirname(os.path.abspath(start)))
    print(f"⚠️  không tìm thấy checkout mike canonical (thử {canonical!r}) — dùng cây đang chạy "
          f"{running!r}; state dùng chung có thể bị phân mảnh", file=sys.stderr)
    return running


def _cli(argv: list) -> int:
    """CLI cho script BASH tái dùng đúng một định nghĩa gốc cây (đừng chép phép đếm cấp).

        ROOT="$(python3 bin/wc_paths.py --mike-canonical)"   # cây mike canonical
        WC="$(python3 bin/wc_paths.py --wc-root)"            # cây WorkingClaude của tôi
    """
    if len(argv) != 1 or argv[0] not in ("--mike-canonical", "--wc-root"):
        print("usage: wc_paths.py {--mike-canonical|--wc-root}", file=sys.stderr)
        return 2
    print(find_mike_canonical_root(__file__) if argv[0] == "--mike-canonical"
          else find_wc_root(__file__))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
