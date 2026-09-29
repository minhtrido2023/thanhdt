#!/usr/bin/env python3
"""B0 — kiểm kê: mọi md5 mà `results_registry.md` trích dẫn còn dò được file không?

VÌ SAO: một con số pin mà artifact của nó đã mất thì **không còn tái lập được**,
nhưng registry vẫn im lặng để nó làm neo kỳ vọng. Đây đúng là lớp lỗi user nêu
2026-09-28: *"kết quả tốt nhưng là số ảo; hỏi đến thật thì lại là số khác."*

Script CHỈ ĐỌC. Nó không sửa registry, không xoá file, không pin gì.
Đầu ra: báo cáo markdown + rc.

PHÂN LOẠI (3 mức, KHÔNG gộp — mỗi mức cần một hành động khác nhau):
  RESOLVED_STORE  md5 nằm trong kho bất biến `data/pinned_ledgers/`  → an toàn
  RESOLVED_LOOSE  chỉ dò được một file rời trên đĩa (có thể bị ghi đè bất cứ lúc
                  nào, hoặc nằm trong worktree TẠM)                  → nên pin vào kho
  LOST            không file nào trên máy có md5 đó                  → KHÔNG còn tái lập được

`--fail-on-lost` ⇒ rc=1 khi còn LOST (dùng cho cron/audit định kỳ, KHÔNG dùng làm
pre-commit: nợ cũ không phải trả trong một commit).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pin_ledger  # noqa: E402
from wc_paths import find_wc_root  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
REGISTRY_REL = os.path.join("data", "results_registry.md")

RE_FULL = re.compile(r"\b([0-9a-f]{32})\b")
# Dạng rút gọn registry hay dùng: `4707bcbe…` / `4707bcbe...`
RE_SHORT = re.compile(r"`([0-9a-f]{8})(?:…|\.\.\.)`")

SKIP_DIR_PARTS = (".git", "__pycache__", "node_modules", ".pre-commit")


def iter_files(roots, max_bytes: int):
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_PARTS]
            for fn in filenames:
                p = os.path.join(dirpath, fn)
                try:
                    if os.path.islink(p) or os.path.getsize(p) > max_bytes:
                        continue
                except OSError:
                    continue
                yield p


def is_temp_worktree(rel: str) -> bool:
    """Đường dẫn chứa một thư mục dạng `wt-*` = worktree tạm, xoá là mất."""
    return any(part.startswith("wt-") for part in rel.split(os.sep))


def build_index(wc_root: str, max_bytes: int) -> dict:
    roots = [
        os.path.join(wc_root, "data"),
        os.path.join(wc_root, "mike", "research"),
        os.path.join(wc_root, "mike", "agents"),
        os.path.join(wc_root, "mike", "kb"),
    ]
    idx = {}
    for p in iter_files(roots, max_bytes):
        try:
            h = hashlib.md5(open(p, "rb").read()).hexdigest()
        except OSError:
            continue
        idx.setdefault(h, []).append(os.path.relpath(p, wc_root))
    return idx


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=None, help="ghi báo cáo markdown ra file")
    ap.add_argument("--max-bytes", type=int, default=200_000_000)
    ap.add_argument("--fail-on-lost", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    wc_root = os.environ.get("PIN_STORE_WC_ROOT") or find_wc_root(__file__)
    reg = os.path.join(wc_root, REGISTRY_REL)
    if not os.path.exists(reg):
        raise SystemExit(f"Không thấy registry: {reg}")
    text = open(reg, encoding="utf-8").read()

    full = sorted(set(RE_FULL.findall(text)))
    short = sorted(set(RE_SHORT.findall(text)) - {f[:8] for f in full})

    idx = build_index(wc_root, args.max_bytes)
    pref = {}
    for h, paths in idx.items():
        pref.setdefault(h[:8], []).extend(paths)

    store = {r["md5"] for r in pin_ledger.read_manifest(wc_root)
             if r.get("record") != "annotation" and "md5" in r}

    rows = []
    for d in full:
        paths = idx.get(d, [])
        rows.append(_classify(d, "full", paths, store))
    for d8 in short:
        paths = pref.get(d8, [])
        rows.append(_classify(d8, "short", paths, store))

    n_store = sum(1 for r in rows if r["status"] == "RESOLVED_STORE")
    n_loose = sum(1 for r in rows if r["status"] == "RESOLVED_LOOSE")
    n_lost = sum(1 for r in rows if r["status"] == "LOST")
    n_tmp = sum(1 for r in rows if r.get("only_in_temp_worktree"))

    if args.json:
        print(json.dumps({"rows": rows, "summary": {
            "total": len(rows), "in_store": n_store, "loose": n_loose,
            "lost": n_lost, "only_temp_worktree": n_tmp}}, ensure_ascii=False, indent=1))
    else:
        print(f"Tham chiếu md5 trong registry: {len(rows)}  "
              f"(đầy đủ {len(full)} · rút gọn {len(short)})")
        print(f"  ✅ trong kho bất biến : {n_store}")
        print(f"  🟡 chỉ có file RỜI    : {n_loose}   (trong đó {n_tmp} chỉ sống ở worktree TẠM)")
        print(f"  ❌ MẤT DẤU            : {n_lost}")
        for r in rows:
            if r["status"] == "LOST":
                print(f"     MẤT  {r['md5']}  ({r['form']})")
            elif r.get("only_in_temp_worktree"):
                print(f"     TẠM  {r['md5']}  → {r['paths'][0]}")

    if args.out:
        _write_report(args.out, wc_root, rows, n_store, n_loose, n_lost, n_tmp)
        print(f"→ báo cáo: {args.out}")

    return 1 if (args.fail_on_lost and n_lost) else 0


def _classify(digest: str, form: str, paths: list, store: set) -> dict:
    in_store = digest in store or any(p.startswith(os.path.join("data", "pinned_ledgers"))
                                      for p in paths)
    if in_store:
        status = "RESOLVED_STORE"
    elif paths:
        status = "RESOLVED_LOOSE"
    else:
        status = "LOST"
    return {
        "md5": digest,
        "form": form,
        "status": status,
        "paths": paths[:4],
        "n_paths": len(paths),
        "only_in_temp_worktree": bool(paths) and all(is_temp_worktree(p) for p in paths),
    }


def _write_report(out, wc_root, rows, n_store, n_loose, n_lost, n_tmp):
    now = datetime.now(ICT).strftime("%Y-%m-%d %H:%M ICT")
    L = []
    L.append("# B0 — Kiểm kê artifact của mọi số đã pin\n")
    L.append(f"*Sinh tự động bởi `bin/pin_artifact_inventory.py` lúc {now}. Script CHỈ ĐỌC.*\n")
    L.append(f"Nguồn: `{REGISTRY_REL}` · cây quét: `data/`, `mike/research/`, "
             f"`mike/agents/`, `mike/kb/`\n")
    L.append("| | số lượng | nghĩa |")
    L.append("|---|---|---|")
    L.append(f"| ✅ trong kho bất biến | {n_store} | an toàn, không ghi đè được |")
    L.append(f"| 🟡 chỉ có file rời | {n_loose} | có thể bị ghi đè bất cứ lúc nào |")
    L.append(f"| ⚠️ trong đó chỉ ở worktree TẠM | {n_tmp} | xoá worktree là mất |")
    L.append(f"| ❌ MẤT DẤU | {n_lost} | **không còn tái lập được** |")
    L.append(f"| **tổng** | **{len(rows)}** | |\n")

    lost = [r for r in rows if r["status"] == "LOST"]
    if lost:
        L.append("## ❌ Mất dấu — số nào trích các md5 này là số KHÔNG tái lập được\n")
        for r in lost:
            L.append(f"- `{r['md5']}` ({'32 hex' if r['form'] == 'full' else 'rút gọn 8'})")
        L.append("")
    tmp = [r for r in rows if r.get("only_in_temp_worktree")]
    if tmp:
        L.append("## ⚠️ Chỉ còn sống trong worktree TẠM — copy vào kho TRƯỚC khi dọn worktree\n")
        for r in tmp:
            L.append(f"- `{r['md5']}` → `{r['paths'][0]}`")
        L.append("")
    loose = [r for r in rows if r["status"] == "RESOLVED_LOOSE" and not r["only_in_temp_worktree"]]
    if loose:
        L.append("## 🟡 File rời (nên pin vào kho)\n")
        for r in loose:
            extra = f" (+{r['n_paths']-1} bản trùng)" if r["n_paths"] > 1 else ""
            L.append(f"- `{r['md5']}` → `{r['paths'][0]}`{extra}")
        L.append("")
    L.append("---\n")
    L.append("Pin một artifact vào kho:\n")
    L.append("```bash\nmike/bin/pin_ledger.py add <file.csv> --label <nhãn> \\\n"
             "    --command \"<lệnh chạy đầy đủ>\" --audit-end <YYYY-MM-DD>\n```\n")
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
