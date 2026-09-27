#!/usr/bin/env python3
"""Selfcheck cơ chế `family_manifest` của `dsr_pbo_annex.py` (2026-09-27).

Chạy trong một thư mục CÔ LẬP (`tmp/data/` chứa symlink tới CSV thật) nên KHÔNG ghi gì vào
`data/` canonical và không cần copy 1,5GB. 4 assertion, mỗi cái ứng đúng một cách hỏng:

  1. Manifest hợp lệ ⇒ annex chạy, N = số entry của manifest (không phải số file trong thư mục).
  2. **Thêm CSV LẠ vào thư mục ⇒ PBO KHÔNG ĐỔI** (đây là bệnh gốc: glob động làm PBO trôi —
     đo thật cùng ngày 2026-09-27: 477 file lúc sáng PBO 0,3993 → 486 file lúc 12:47 PBO 0,5013,
     vượt ngưỡng quyết định 0,5).
  3. Manifest thiếu file ⇒ **fail-CLOSED** (exit≠0, không in PBO trên họ đã bị thu nhỏ).
  4. md5 lệch (file bị ghi lại) ⇒ fail-CLOSED.
  5. **`DSR_FAMILY_MANIFEST` KHÔNG set ⇒ fail-CLOSED rc=2** (bắt buộc từ 2026-09-27, user duyệt).
     Trước đó đường này IN cảnh báo rồi vẫn trả PBO — một con số không tái lập được nhưng trông y
     như số pin. Đây cũng là chân ĐỐI CHỨNG của test 2 (đổi nghĩa 2026-09-27: trước là "glob động
     PHẢI đổi N", nay là "đường glob không còn tồn tại trong annex").
  6. Set nhưng RỖNG (`DSR_FAMILY_MANIFEST=""`) ⇒ cũng fail-CLOSED rc=2 — biến rỗng không được coi
     là "đã set" (nếu không, một `export DSR_FAMILY_MANIFEST=$UNSET_VAR` biến gate thành no-op).
  7. **Glob VẪN sống cho `dsr_family_manifest.py build`** — nó cần candidate để dựng manifest. Test
     này là chân đối xứng của 5/6: nếu ai "sửa" gate bằng cách xoá luôn nhánh glob thì builder chết
     và không còn cách nào dựng manifest mới.

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


UNSET = object()   # phân biệt "biến KHÔNG có trong env" với "có nhưng rỗng" (test 5 vs 6)


def run_annex(cwd, manifest=UNSET, r3=None):
    env = dict(os.environ)
    env.pop("DSR_FAMILY_MANIFEST", None)
    if manifest is not UNSET:
        env["DSR_FAMILY_MANIFEST"] = manifest   # có thể là "" — đó chính là test 6
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
        # 5. KHÔNG set DSR_FAMILY_MANIFEST ⇒ fail-closed rc=2 (thay chân đối chứng glob cũ:
        #    từ 2026-09-27 đường glob không còn tồn tại trong annex, nên "N phải đổi" vô nghĩa).
        no_man = run_annex(tmp, r3=r3)
        n += 1
        if no_man["rc"] != 2:
            fails.append(f"5: KHÔNG set DSR_FAMILY_MANIFEST mà rc={no_man['rc']} (phải là 2) — "
                         f"annex không fail-closed")
        n += 1
        if no_man["pbo"] is not None or no_man["ncfg"] is not None:
            fails.append(f"5: fail-closed mà VẪN in số — PBO={no_man['pbo']}, N={no_man['ncfg']}; "
                         f"chính con số không tái lập được mà gate này tồn tại để chặn")
        n += 1
        msg = no_man["err"] + no_man["out"]
        missing_bits = [b for b in ("DSR_FAMILY_MANIFEST", "dsr_family_manifest.py build")
                        if b not in msg]
        if missing_bits:
            fails.append(f"5: thông điệp lỗi thiếu {missing_bits} — người chạy không biết phải làm "
                         f"gì tiếp (§29 phải trích bằng chứng + cách sửa): {msg[-300:]}")

        # 6. set nhưng RỖNG ⇒ cũng fail-closed (biến rỗng không phải "đã set")
        empty_man = run_annex(tmp, manifest="", r3=r3)
        n += 1
        if empty_man["rc"] != 2 or empty_man["pbo"] is not None:
            fails.append(f"6: DSR_FAMILY_MANIFEST=\"\" mà rc={empty_man['rc']}, "
                         f"PBO={empty_man['pbo']} — biến rỗng bị coi là đã set ⇒ gate thành no-op")

        # 7. glob VẪN sống cho builder: dựng lại manifest SAU khi thêm CSV lạ ⇒ phải thấy nó
        man2 = os.path.join(tmp, "manifest2.json")
        b2 = subprocess.run([sys.executable, BUILDER, "build", "--out", man2,
                             "--reason", "selfcheck-glob-alive", "--min-obs", "2500"],
                            cwd=tmp, capture_output=True, text=True)
        n += 1
        if b2.returncode != 0:
            fails.append(f"7: builder FAIL sau khi gate bắt buộc manifest (rc={b2.returncode}) — "
                         f"nhánh glob candidate bị xoá mất ⇒ không còn cách dựng manifest mới:\n"
                         f"{b2.stderr[-300:]}")
            n2_entries = None
        else:
            n2_entries = json.load(open(man2, encoding="utf-8"))["n_entries"]
            n += 1
            if n2_entries != args.n_configs + 1:
                fails.append(f"7: builder thấy {n2_entries} entry, mong {args.n_configs + 1} "
                             f"(8 gốc + 1 CSV lạ) — glob candidate không còn quét đúng thư mục")

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
        print(f"  [2] +1 CSV lạ, CÓ manifest: N={with_man['ncfg']}, PBO={with_man['pbo']}")
        print(f"  [3] thiếu file: rc={miss['rc']}  [4] md5 lệch: rc={bad['rc']}")
        print(f"  [5] manifest KHÔNG set: rc={no_man['rc']}, PBO={no_man['pbo']}, N={no_man['ncfg']}")
        print(f"  [6] manifest rỗng: rc={empty_man['rc']}, PBO={empty_man['pbo']}")
        print(f"  [7] builder glob còn sống: rc={b2.returncode}, n_entries={n2_entries}")
    print(f"{'✅' if not fails else '❌'} {n - len(fails)}/{n} assertion PASS")
    for f in fails:
        print(f"   ❌ {f}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
