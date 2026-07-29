#!/usr/bin/env python3
"""In "dau van tay" vintage cua mot thu muc BQ local cache, de dan kem so pin
trong data/results_registry.md (Viec 2, job Taylor_20260729_155142).

Ly do ton tai: BQ time-travel da tat va `ticker`/`ticker_prune` bi TRUNCATE+rebuild
moi ngay => khong the tra lai "du lieu ngay X" tu BQ. Dau van tay (md5 + rows +
max_time) la thu duy nhat chung minh mot so pin duoc do tren vintage nao.

Dung: python3 cache_vintage_stamp.py <cache_dir> [--md]
"""
import hashlib
import json
import os
import sys

KEY_TABLES = [
    "vnindex_5state_dt5g_live",
    "vnindex_5state_tam_quan_v34b_clean",
    "ticker",
    "ticker_prune",
    "universe_pit_q",
    "ticker_financial",
    "fa_ratings_8l",
]


def md5_of(path):
    h = hashlib.md5()
    if os.path.isdir(path):  # partitioned table -> hash file names + contents in sorted order
        for root, dirs, files in os.walk(path):
            dirs.sort()
            for f in sorted(files):
                fp = os.path.join(root, f)
                h.update(os.path.relpath(fp, path).encode())
                with open(fp, "rb") as fh:
                    for chunk in iter(lambda: fh.read(1 << 20), b""):
                        h.update(chunk)
    else:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    return h.hexdigest()


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cache = sys.argv[1].rstrip("/")
    as_md = "--md" in sys.argv
    man = json.load(open(os.path.join(cache, "manifest.json")))

    rows = []
    for name in KEY_TABLES:
        info = man["tables"].get(name)
        if not info:
            rows.append((name, "-", "-", "MISSING"))
            continue
        path = os.path.join(cache, info["file"].rstrip("/"))
        rows.append((name, f"{info['rows']:,}", info.get("max_time", "n/a"),
                     md5_of(path)[:16] if os.path.exists(path) else "MISSING"))

    if as_md:
        print(f"- `cache_dir`: `{cache}`")
        print(f"- `manifest.verified`: **{man.get('verified')}** · `verified_at`: {man.get('verified_at')}")
        if man.get("verified_note"):
            print(f"- `verified_note`: {man['verified_note']}")
        print()
        print("| bang | rows | max_time | md5 (16 ky tu dau) |")
        print("|---|---|---|---|")
        for r in rows:
            print(f"| `{r[0]}` | {r[1]} | {r[2]} | `{r[3]}` |")
    else:
        print(f"cache={cache} verified={man.get('verified')} at={man.get('verified_at')}")
        for r in rows:
            print(f"  {r[0]:38s} rows={r[1]:>12s} max_time={r[2]:12s} md5={r[3]}")


if __name__ == "__main__":
    main()
