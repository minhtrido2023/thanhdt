#!/usr/bin/env python3
"""Pin họ trial (trial family) của DSR/PBO thành MỘT file manifest bất biến.

Vì sao cần: `dsr_pbo_annex.py::family_paths()` là **glob động** trên
`data/v23_golive_audit_2014_now_*.csv`. Họ trial vì thế nở ra theo mọi backtest R&D chạy sau đó
(đo 2026-09-27: 73 CSV qua bộ lọc ≥2500 obs lúc pin tháng 7 → **486** hôm nay), và PBO — vốn là
hàm của CHÍNH tập cấu hình được so sánh — trôi theo thời gian. Hệ quả: số PBO đã pin trong
`data/results_registry.md` §"DSR / PBO Robustness Annex" **không tái lập được**, và cùng một lệnh
chạy ở 2 worktree khác nhau cho 2 số khác nhau (0,3993 vs 0,5026 — đúng hai bên ngưỡng quyết
định 0,5 của §quant-research/guideline "PBO ≥ 0,5 ⇒ chọn config robust-trung vị").

Ngữ nghĩa ĐÚNG của họ trial (Bailey-Borwein-LdP-Zhu 2017): tập cấu hình **đã được SO SÁNH với
nhau khi chọn** config deploy. Một backtest R&D chạy 2 tháng sau, cho một câu hỏi khác, KHÔNG
thuộc họ đó — glob động cố tình hay không vẫn kéo nó vào.

Dùng:
    python3 dsr_family_manifest.py build --out data/dsr_family_manifest_2026-09-27.json \
        --mtime-before 2026-07-05T08:00 --reason "họ trial phục dựng ..." [--min-obs 2500]
    python3 dsr_family_manifest.py verify data/dsr_family_manifest_2026-09-27.json
    DSR_FAMILY_MANIFEST=data/dsr_family_manifest_2026-09-27.json python3 dsr_pbo_annex.py

`build` KHÔNG tự quyết file nào thuộc họ — nó ghi lại tiêu chí bạn khai (`criterion`) + bằng chứng
đo được cho từng file (md5, size, mtime, n_obs) để người sau audit được. `verify`/annex fail-CLOSED:
thiếu file hoặc md5 lệch ⇒ thoát khác 0, KHÔNG âm thầm bỏ qua file đó (bỏ qua = đúng lại bệnh cũ:
họ trial thay đổi mà số vẫn in ra như thường).
"""
import argparse
import datetime
import glob
import hashlib
import json
import os
import sys
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
DATA = "data"
MANIFEST_ENV = "DSR_FAMILY_MANIFEST"


def md5_of(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def n_obs_of(path):
    """Số ngày NAV dùng được — cùng định nghĩa `dsr_pbo_annex.load_nav()` (collapse theo ngày)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from dsr_pbo_annex import load_nav
    s = load_nav(path)
    return 0 if s is None else int(len(s))


def build(args):
    from dsr_pbo_annex import family_paths
    cand = family_paths(_ignore_manifest=True)
    cut = None
    if args.mtime_before:
        cut = datetime.datetime.fromisoformat(args.mtime_before).replace(tzinfo=ICT).timestamp()
    entries, skipped = [], {"mtime": 0, "short": 0, "unreadable": 0}
    for p in cand:
        mt = os.path.getmtime(p)
        if cut is not None and mt >= cut:
            skipped["mtime"] += 1
            continue
        n = n_obs_of(p)
        if n == 0:
            skipped["unreadable"] += 1
            continue
        if n < args.min_obs:
            skipped["short"] += 1
            continue
        entries.append({
            "path": p, "md5": md5_of(p), "size": os.path.getsize(p),
            "mtime_ict": datetime.datetime.fromtimestamp(mt, ICT).isoformat(),
            "n_obs": n, "reason": args.reason,
        })
    entries.sort(key=lambda e: e["path"])
    man = {
        "_doc": "Họ trial CỐ ĐỊNH cho dsr_pbo_annex.py. Tạo bởi dsr_family_manifest.py build. "
                "KHÔNG sửa tay: sửa md5 mà không sửa file = phá chính cơ chế fail-closed.",
        "manifest_version": 1,
        "created_at_ict": datetime.datetime.now(ICT).isoformat(),
        "criterion": {
            "glob": f"{DATA}/v23_golive_audit_2014_now_*.csv (+ loại navXXB / from20XX như family_paths)",
            "mtime_before_ict": args.mtime_before,
            "min_obs": args.min_obs,
            "reason": args.reason,
        },
        "n_entries": len(entries),
        "n_candidates_globbed": len(cand),
        "skipped": skipped,
        "entries": entries,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1, ensure_ascii=False)
    print(f"Ghi {args.out}: {len(entries)}/{len(cand)} CSV vào họ trial "
          f"(bỏ: mtime {skipped['mtime']}, <{args.min_obs} obs {skipped['short']}, "
          f"không đọc được {skipped['unreadable']})")
    return 0


def load_manifest(path):
    """Trả list path đã VERIFY. Raise nếu thiếu file / md5 lệch (fail-closed)."""
    man = json.load(open(path, encoding="utf-8"))
    missing, mismatch = [], []
    for e in man["entries"]:
        if not os.path.exists(e["path"]):
            missing.append(e["path"])
            continue
        got = md5_of(e["path"])
        if got != e["md5"]:
            mismatch.append(f"{e['path']} (manifest {e['md5'][:12]}… vs trên đĩa {got[:12]}…)")
    if missing or mismatch:
        raise RuntimeError(
            f"manifest {path} KHÔNG khớp đĩa — fail-closed, không tính PBO trên họ khác:\n"
            + "".join(f"  THIẾU: {m}\n" for m in missing)
            + "".join(f"  MD5 LỆCH: {m}\n" for m in mismatch)
            + "  (file backtest bị ghi đè/xoá ⇒ số PBO cũ không còn tái lập được; "
              "dựng manifest MỚI có ngày mới thay vì sửa manifest cũ.)")
    return [e["path"] for e in man["entries"]], man


def verify(args):
    try:
        paths, man = load_manifest(args.manifest)
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    print(f"✅ {args.manifest}: {len(paths)} CSV khớp md5, tạo {man['created_at_ict']}, "
          f"tiêu chí {man['criterion']}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", required=True)
    b.add_argument("--mtime-before", default=None,
                   help="ISO ICT; chỉ nhận CSV có mtime TRƯỚC mốc này (phục dựng họ tại thời điểm pin)")
    b.add_argument("--min-obs", type=int, default=2500)
    b.add_argument("--reason", required=True,
                   help="vì sao những file này thuộc HỌ (đã được so sánh khi chọn config deploy)")
    b.set_defaults(func=build)
    v = sub.add_parser("verify")
    v.add_argument("manifest")
    v.set_defaults(func=verify)
    args = ap.parse_args()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
