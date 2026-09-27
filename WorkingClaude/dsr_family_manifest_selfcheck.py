#!/usr/bin/env python3
"""Selfcheck cơ chế `family_manifest` của `dsr_pbo_annex.py` (2026-09-27).

Chạy trong một thư mục CÔ LẬP (`tmp/data/` chứa symlink tới CSV thật) nên KHÔNG ghi gì vào
`data/` canonical và không cần copy 1,5GB. 4 assertion, mỗi cái ứng đúng một cách hỏng:

  1. Manifest hợp lệ ⇒ annex chạy, N = số entry của manifest (không phải số file trong thư mục).
  2. **Thêm CSV LẠ vào thư mục ⇒ PBO KHÔNG ĐỔI** (đây là bệnh gốc: glob động làm PBO trôi —
     đo thật cùng ngày 2026-09-27: 477 file lúc sáng PBO 0,3993 → 486 file lúc 12:47 PBO 0,5013,
     vượt ngưỡng quyết định 0,5). Đối chứng: cùng thư mục đó, KHÔNG set manifest ⇒ PBO PHẢI đổi.
  3. Manifest thiếu file ⇒ **fail-CLOSED** (exit≠0, không in PBO trên họ đã bị thu nhỏ).
  4. md5 lệch (file bị ghi lại) ⇒ fail-CLOSED.

    $DNA_PYEXE dsr_family_manifest_selfcheck.py [--n-configs 8]
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ANNEX = os.path.join(HERE, "dsr_pbo_annex.py")
BUILDER = os.path.join(HERE, "dsr_family_manifest.py")
REAL_DATA = os.path.join("/home/trido/thanhdt/WorkingClaude", "data")


def run_annex(cwd, manifest=None, r3=None):
    env = dict(os.environ)
    env.pop("DSR_FAMILY_MANIFEST", None)
    if manifest:
        env["DSR_FAMILY_MANIFEST"] = manifest
    env["DSR_R3_CSV"] = r3
    p = subprocess.run([sys.executable, ANNEX], cwd=cwd, env=env,
                       capture_output=True, text=True)
    pbo = re.search(r"PBO = ([0-9.]+)", p.stdout)
    ncfg = re.search(r"x (\d+) configs", p.stdout)
    return {"rc": p.returncode, "pbo": float(pbo.group(1)) if pbo else None,
            "ncfg": int(ncfg.group(1)) if ncfg else None,
            "out": p.stdout, "err": p.stderr}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-configs", type=int, default=8)
    args = ap.parse_args()

    pool = sorted(glob.glob(os.path.join(REAL_DATA, "v23_golive_audit_2014_now_*.csv")))
    pool = [p for p in pool if "from20" not in p and not re.search(r"nav\d+B", p)]
    if len(pool) < args.n_configs + 1:
        print(f"❌ chỉ có {len(pool)} CSV, cần ≥{args.n_configs+1}", file=sys.stderr)
        return 2
    picked, stray = pool[:args.n_configs], pool[args.n_configs]

    fails, n = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "data")
        os.makedirs(d)
        for p in picked:
            os.symlink(p, os.path.join(d, os.path.basename(p)))
        r3 = os.path.join("data", os.path.basename(picked[0]))
        man = os.path.join(tmp, "manifest.json")
        b = subprocess.run([sys.executable, BUILDER, "build", "--out", man,
                            "--reason", "selfcheck", "--min-obs", "2500"],
                           cwd=tmp, capture_output=True, text=True)
        if b.returncode != 0:
            print(f"❌ build manifest lỗi:\n{b.stdout}\n{b.stderr}", file=sys.stderr)
            return 2

        # 1. manifest hợp lệ
        base = run_annex(tmp, manifest=man, r3=r3)
        n += 1
        if base["rc"] != 0 or base["pbo"] is None:
            fails.append(f"1: annex với manifest hợp lệ FAIL rc={base['rc']}\n{base['err'][-400:]}")
        n += 1
        if base["ncfg"] != args.n_configs:
            fails.append(f"1: N={base['ncfg']} != số entry manifest {args.n_configs}")

        # 2. thêm CSV lạ vào thư mục
        os.symlink(stray, os.path.join(d, os.path.basename(stray)))
        with_man = run_annex(tmp, manifest=man, r3=r3)
        n += 1
        if with_man["pbo"] != base["pbo"] or with_man["ncfg"] != base["ncfg"]:
            fails.append(f"2: CSV lạ ĐÃ ĐỔI kết quả dù có manifest — PBO {base['pbo']}→"
                         f"{with_man['pbo']}, N {base['ncfg']}→{with_man['ncfg']}")
        no_man = run_annex(tmp, manifest=None, r3=r3)   # đối chứng: glob động PHẢI đổi
        n += 1
        if no_man["ncfg"] == base["ncfg"]:
            fails.append(f"2-đối chứng: KHÔNG manifest mà N vẫn {no_man['ncfg']} — test không đo "
                         f"cái nó tuyên bố đo (CSV lạ phải nhập họ khi glob động)")

        # 3. manifest thiếu file
        os.remove(os.path.join(d, os.path.basename(picked[-1])))
        miss = run_annex(tmp, manifest=man, r3=r3)
        n += 1
        if miss["rc"] == 0 or miss["pbo"] is not None:
            fails.append(f"3: thiếu file mà annex vẫn chạy (rc={miss['rc']}, PBO={miss['pbo']}) — "
                         f"KHÔNG fail-closed")
        n += 1
        if "THIẾU" not in miss["err"]:
            fails.append(f"3: thông điệp lỗi không nêu file THIẾU (§29 — phải trích bằng chứng): "
                         f"{miss['err'][-200:]}")
        os.symlink(picked[-1], os.path.join(d, os.path.basename(picked[-1])))

        # 4. md5 lệch
        tgt = os.path.join(d, os.path.basename(picked[1]))
        os.remove(tgt)
        shutil.copy(picked[2], tgt)      # nội dung KHÁC, tên giữ nguyên
        bad = run_annex(tmp, manifest=man, r3=r3)
        n += 1
        if bad["rc"] == 0 or bad["pbo"] is not None:
            fails.append(f"4: md5 lệch mà annex vẫn chạy (rc={bad['rc']}, PBO={bad['pbo']})")
        n += 1
        if "MD5 LỆCH" not in bad["err"]:
            fails.append(f"4: thông điệp lỗi không nêu MD5 LỆCH: {bad['err'][-200:]}")

        print(f"  [1] manifest hợp lệ: N={base['ncfg']}, PBO={base['pbo']}")
        print(f"  [2] +1 CSV lạ, CÓ manifest: N={with_man['ncfg']}, PBO={with_man['pbo']}  "
              f"(đối chứng KHÔNG manifest: N={no_man['ncfg']}, PBO={no_man['pbo']})")
        print(f"  [3] thiếu file: rc={miss['rc']}  [4] md5 lệch: rc={bad['rc']}")
    print(f"{'✅' if not fails else '❌'} {n - len(fails)}/{n} assertion PASS")
    for f in fails:
        print(f"   ❌ {f}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
