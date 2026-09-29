#!/usr/bin/env python3
"""Gộp sổ giao hàng báo cáo LẠC (worktree/clone phụ) về sổ CANONICAL — mặc định chỉ IN DIFF.

Vì sao tồn tại: trước bản vá 2026-09-12, `report_delivery_gate.py` lấy ROOT = cây đang chạy,
mà `state/` bị gitignore ⇒ mỗi worktree/clone giữ một sổ riêng. Bản vá chặn sổ MỚI phân mảnh;
file này dọn phần ĐÃ lạc (và phát hiện sổ lạc mới nếu một cây chạy bản tiền-vá).

Kỷ luật nhập, theo hướng AN TOÀN MỘT CHIỀU — thà giao lại một lần thừa còn hơn nuốt mất một
lần giao thật:
  * KHÔNG BAO GIỜ đè entry đã có trong sổ canonical (kể cả khi sổ lạc "đầy đủ hơn").
  * Chỉ nhập entry đã giao ĐỦ hai kênh (discord + email) — entry mới validate chưa gửi thì nhập
    vào chẳng đổi gì, vì `complete()` vẫn False.
  * Chỉ nhập khi `reports/<tên>` trong cây canonical TỒN TẠI và sha256 khớp đúng entry. Cùng
    tên mà khác nội dung là artifact KHÁC (đã gặp: `SpaceX_daily_report_2026-08-21.md` hai sha)
    — nhập vào sẽ đánh dấu "đã gửi" cho một file chưa từng được gửi, tức NUỐT một lần giao hàng
    thật. Đây là lý do khoá nhập theo hash chứ không theo tên.

    python3 mike/bin/report_delivery_ledger_merge.py            # dry-run: liệt kê + diff
    python3 mike/bin/report_delivery_ledger_merge.py --apply    # ghi (có backup .bak-<ts>)
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
import tempfile
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wc_paths import find_mike_canonical_root, find_wc_root  # noqa: E402

CANONICAL_ROOT = Path(find_mike_canonical_root(__file__))
CANONICAL_STATE = CANONICAL_ROOT / "state" / "report_delivery.json"
LEDGER_REL = Path("state") / "report_delivery.json"


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def find_stray_ledgers(wc_root: Path) -> list[Path]:
    """Mọi `*/state/report_delivery.json` dưới cây WorkingClaude, trừ sổ canonical.

    Quét 2 tầng đủ cho mọi hình dạng đã biết: `WorkingClaude/<cây>/state/` (clone phụ +
    worktree ngoài) và `WorkingClaude/mike/agents/<wt>/state/` (worktree trong).
    """
    found = []
    for base in [wc_root, CANONICAL_ROOT / "agents"]:
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if not child.is_dir():
                continue
            cand = child / LEDGER_REL
            if cand.is_file() and cand.resolve() != CANONICAL_STATE.resolve():
                found.append(cand)
    return found


def load_reports(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    reports = data.get("reports", {})
    return reports if isinstance(reports, dict) else {}


def classify(name: str, entry: dict, canonical: dict) -> tuple[str, str]:
    if not isinstance(entry, dict):
        return "SKIP", "entry không phải object"
    sha = entry.get("sha256")
    if name in canonical and canonical[name].get("sha256") == sha:
        return "ALREADY", "sổ canonical đã có đúng hash này"
    # Bằng chứng giao hàng xét TRƯỚC trùng-tên: bản ghi chỉ-validate (chạy thử) trùng tên một
    # báo cáo thật KHÔNG phải "cần người xem" — nó không bao giờ đủ điều kiện nhập. Gắn CLASH
    # cho nó làm loãng đúng cái cần người đọc (arch-review 2026-09-12 required_changes #6).
    delivered = (isinstance(entry.get("discord"), dict) and isinstance(entry.get("email"), dict)
                 and entry["discord"].get("status") == "delivered"
                 and entry["email"].get("status") == "delivered")
    if not delivered:
        return "SKIP", "chưa giao đủ 2 kênh — chỉ là bản ghi validate, nhập vào không đổi gì"
    if name in canonical:
        return "CLASH", (f"ĐÃ GIAO THẬT nhưng canonical giữ sha="
                         f"{str(canonical[name].get('sha256'))[:12]} ≠ sổ lạc "
                         f"{str(sha)[:12]} — KHÔNG đè, cần người xem")
    disk = sha256_file(CANONICAL_ROOT / "reports" / name)
    if disk is None:
        return "SKIP", "không có file tương ứng trong reports/ canonical"
    if disk != sha:
        return "SKIP", f"file canonical sha={disk[:12]} ≠ entry sha={str(sha)[:12]} (artifact khác)"
    return "IMPORT", "đã giao đủ 2 kênh + hash khớp file canonical"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="thực sự ghi vào sổ canonical")
    args = ap.parse_args()

    wc_root = Path(find_wc_root(__file__))
    canonical_doc = json.loads(CANONICAL_STATE.read_text(encoding="utf-8")) if (
        CANONICAL_STATE.is_file()) else {"version": 1, "reports": {}}
    canonical = canonical_doc.setdefault("reports", {})
    strays = find_stray_ledgers(wc_root)
    print(f"sổ canonical: {CANONICAL_STATE} ({len(canonical)} entry)")
    print(f"sổ lạc tìm thấy: {len(strays)}")

    to_import: dict = {}
    clashes = 0
    for stray in strays:
        print(f"\n--- {stray}")
        try:
            entries = load_reports(stray)
        except Exception as exc:                                  # sổ hỏng: báo, không chặn
            print(f"    ⚠️  không đọc được: {exc}")
            continue
        already = 0
        for name, entry in sorted(entries.items()):
            verdict, why = classify(name, entry, canonical)
            if verdict == "IMPORT" and name not in to_import:
                to_import[name] = entry
            elif verdict == "CLASH":
                clashes += 1
            elif verdict == "ALREADY":
                already += 1
                continue
            print(f"    [{verdict}] {name} — {why}")
        print(f"    ({len(entries)} entry, {already} đã có trong canonical)")

    print(f"\nSẼ NHẬP: {len(to_import)} entry" + (f" · CLASH cần người xem: {clashes}" if clashes else ""))
    for name in sorted(to_import):
        print(f"  + {name}  sha={to_import[name]['sha256'][:12]}")
    if not to_import:
        print("Không có gì để gộp — sổ canonical đã đủ.")
        return 0
    if not args.apply:
        print("\n(dry-run — chạy lại với --apply để ghi)")
        return 0

    # Ghi dưới ĐÚNG lock mà report_delivery_gate.py dùng, và ghi ATOMIC. Công cụ dọn sổ mà
    # write_text trần thì một lần bị kill giữa chừng = sổ canonical hỏng ⇒ load_json raise ⇒
    # CHẶN TOÀN BỘ giao hàng cho tới khi người khôi phục .bak (arch-review 2026-09-12 #2).
    # Đọc lại sổ BÊN TRONG lock: bản đọc lúc dry-run có thể đã cũ nếu một delivery vừa chạy.
    lock_path = CANONICAL_STATE.with_suffix(CANONICAL_STATE.suffix + ".lock")
    stamp = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y%m%dT%H%M%S-ICT")
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        doc = json.loads(CANONICAL_STATE.read_text(encoding="utf-8")) if (
            CANONICAL_STATE.is_file()) else {"version": 1, "reports": {}}
        fresh = doc.setdefault("reports", {})
        backup = CANONICAL_STATE.with_suffix(CANONICAL_STATE.suffix + f".bak-{stamp}")
        backup.write_text(json.dumps(doc, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                          encoding="utf-8")
        written = 0
        for name, entry in to_import.items():
            if name in fresh:                      # delivery chen vào giữa dry-run và --apply
                print(f"  ! bỏ qua {name} — sổ canonical vừa có entry này (không đè)")
                continue
            merged = dict(entry)
            merged["merged_from_stray_ledger_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
            fresh[name] = merged
            written += 1
        fd, tmp = tempfile.mkstemp(prefix=CANONICAL_STATE.name + ".", dir=CANONICAL_STATE.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(doc, fh, indent=2, ensure_ascii=False, sort_keys=True)
                fh.write("\n")
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, CANONICAL_STATE)
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(tmp)
    print(f"đã ghi {written} entry · backup: {backup}")
    print("Dọn backup khi đã yên tâm: rm mike/state/report_delivery.json.bak-*")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
