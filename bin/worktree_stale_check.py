#!/usr/bin/env python3
"""Worktree/clone nào đang chạy bản TIỀN-VÁ của script giao hàng báo cáo, và sổ lạc nào có
entry ĐÃ GIAO — hai thứ không checker nào phát hiện trước 2026-09-12.

Bối cảnh (kb/incidents/2026-09/2026-09-12-report-return-gate-worktree-root.md, mục "Còn treo"
#1): 14+ bản sao worktree giữ `report_return_gate.py`/`report_delivery_gate.py` bản tiền-vá.
Bản vá 2026-09-12 đã ghim delivery về script canonical nên rủi ro CHÍNH đã đóng; phần còn lại
là các đường chạy TRỰC TIẾP từ worktree (agent chạy tay `bin/report_return_gate.py`). Chỉ CẢNH
BÁO — KHÔNG tự rebase: worktree thuộc phiên/agent khác, kéo master vào giữa chừng là phá việc
đang dở của người khác.

    python3 mike/bin/worktree_stale_check.py          # in dòng cảnh báo (rỗng nếu sạch)
    python3 mike/bin/worktree_stale_check.py --json
Exit 0 luôn (checker, không phải gate).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wc_paths import find_mike_canonical_root  # noqa: E402

CANONICAL = Path(find_mike_canonical_root(__file__))
WATCHED = ("report_return_gate.py", "report_delivery_gate.py", "wc_paths.py")


def sha(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def candidate_trees() -> list:
    """Mọi cây có `bin/` cạnh cây canonical: `WorkingClaude/*` và `mike/agents/*`."""
    out = []
    for base in (CANONICAL.parent, CANONICAL / "agents"):
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.resolve() == CANONICAL.resolve() or not (child / "bin").is_dir():
                continue
            out.append(child)
    return out


def active_since(tree: Path, days: int) -> bool:
    """Cây có file nào được sửa trong `days` ngày gần đây (quét nông: gốc + 1 cấp).

    Vì sao lọc: 18/18 worktree hiện tại đều TIỀN-VÁ và đều nằm im. In cảnh báo cho cả 18 mỗi
    lượt cron = đúng cái WARN-rác mà chính `ops_health_check.sh` (header §7) ghi là đã lặp ~20
    lần trong 5 ngày mà không ai hành động. Cây nằm im thì rebase cũng vô nghĩa: rủi ro chỉ
    hiện thực khi có người ĐANG làm việc trong đó.
    """
    cutoff = time.time() - days * 86400
    for base in (tree, *(d for d in tree.iterdir() if d.is_dir())) if tree.is_dir() else ():
        try:
            for entry in base.iterdir():
                if entry.stat().st_mtime > cutoff:
                    return True
        except OSError:
            continue
    return False


def unmerged_deliveries(led: Path, canonical_reports: dict) -> list:
    """Entry ĐÃ GIAO trong sổ lạc mà sổ canonical chưa có VÀ artifact khớp hash — tức đúng thứ
    `report_delivery_ledger_merge.py` sẽ nhập. Cùng một khoá (hash, không phải tên) để hai công
    cụ không bao giờ nói khác nhau."""
    try:
        reports = json.loads(led.read_text(encoding="utf-8")).get("reports", {})
    except (OSError, ValueError):
        return []
    out = []
    for name, rec in reports.items():
        if not isinstance(rec, dict) or name in canonical_reports:
            continue
        if not (isinstance(rec.get("email"), dict) and rec["email"].get("status") == "delivered"):
            continue
        if sha(CANONICAL / "reports" / name) == rec.get("sha256"):
            out.append(name)
    return sorted(out)


def scan(days: int = 14) -> dict:
    want = {name: sha(CANONICAL / "bin" / name) for name in WATCHED}
    try:
        canonical_reports = json.loads(
            (CANONICAL / "state" / "report_delivery.json").read_text(encoding="utf-8")
        ).get("reports", {})
    except (OSError, ValueError):
        canonical_reports = {}
    stale, ledgers, dormant = [], [], 0
    for tree in candidate_trees():
        drift = [name for name in WATCHED
                 if (tree / "bin" / name).is_file() and sha(tree / "bin" / name) != want[name]]
        # Thiếu hẳn wc_paths.py = chắc chắn tiền-vá (bản vá thêm file này), tính là drift.
        if not (tree / "bin" / "wc_paths.py").is_file() and (
                tree / "bin" / "report_return_gate.py").is_file():
            drift.append("wc_paths.py (THIẾU)")
        if drift:
            if active_since(tree, days):
                stale.append({"tree": str(tree), "files": sorted(set(drift))})
            else:
                dormant += 1
        led = tree / "state" / "report_delivery.json"
        if led.is_file():
            missing = unmerged_deliveries(led, canonical_reports)
            if missing:
                ledgers.append({"ledger": str(led), "delivered": missing})
    return {"canonical": str(CANONICAL), "stale_trees": stale, "stray_ledgers": ledgers,
            "stale_dormant_count": dormant, "active_window_days": days}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--days", type=int, default=14,
                    help="cây không có file nào sửa trong N ngày coi như nằm im (mặc định 14)")
    args = ap.parse_args()
    res = scan(args.days)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0
    # [WARN-ONLY]: Wags/Winston KHÔNG rebase hộ được (worktree thuộc phiên khác) ⇒ auto-dispatch
    # chỉ đốt token. Marker này là thứ ops_health_check.sh dùng để loại khỏi routing autofix.
    if res["stale_trees"]:
        names = ", ".join(os.path.basename(t["tree"]) for t in res["stale_trees"][:6])
        more = f" (+{len(res['stale_trees']) - 6} cây nữa)" if len(res["stale_trees"]) > 6 else ""
        print(f"⚠️ [WARN-ONLY] {len(res['stale_trees'])} worktree ĐANG ĐƯỢC DÙNG "
              f"(<{res['active_window_days']} ngày) chạy bản TIỀN-VÁ script giao hàng báo cáo: "
              f"{names}{more}. Delivery tự động đã ghim về bản canonical nên an toàn; chạy TAY "
              f"bin/report_return_gate.py trong các cây đó thì vẫn dính sự cố 2026-09-12 — "
              f"rebase/merge master. (Thêm {res['stale_dormant_count']} cây tiền-vá nhưng nằm "
              f"im, không tính.)")
    for item in res["stray_ledgers"]:
        print(f"⚠️ [WARN-ONLY] sổ giao hàng LẠC có {len(item['delivered'])} báo cáo ĐÃ GỬI mà sổ "
              f"canonical KHÔNG biết: {item['ledger']} — nguy cơ gửi TRÙNG, gộp bằng "
              f"bin/report_delivery_ledger_merge.py (dry-run trước, --apply sau).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
