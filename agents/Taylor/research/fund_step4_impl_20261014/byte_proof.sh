#!/usr/bin/env bash
# Bằng chứng: tỉ suất danh mục / pnl_vnd / mwr_pct giữ nguyên TỪNG BYTE. Chạy CLI master (sandbox
# /tmp/step4_ctl, code master) và nhánh (/tmp/step4_sbx) trên CÙNG bản sao dữ liệu thật; so đầu ra
# nhánh sau khi bỏ khối `benchmark` với đầu ra master (json.dumps indent=2 = định dạng CLI in ra).
set -uo pipefail
OUT=$(dirname "$0")/byte_proof; mkdir -p "$OUT"; : > "$OUT/rc.txt"
for acc in SpaceX ZaloPay; do for d in 2026-07-03 2026-08-31 2026-09-18 2026-09-30 2026-10-09 2026-10-13; do
  for s in ctl sbx; do
    (cd /tmp && WC_ROOT=/tmp/step4_$s TZ=Asia/Ho_Chi_Minh python3 /tmp/step4_$s/mike/bin/nav_period_returns.py \
       --account $acc --report-date $d > "$OUT/${s}_${acc}_$d.json" 2>/dev/null); echo "$s $acc $d rc=$?" >> "$OUT/rc.txt"
  done; done; done
python3 - "$OUT" <<'PY'
import glob, json, os, sys
o = sys.argv[1]; bad = 0; n = 0
for c in sorted(glob.glob(f"{o}/ctl_*.json")):
    a = open(c).read(); b = open(c.replace("/ctl_", "/sbx_")).read()
    if not a or not b:
        same = a == b; print(os.path.basename(c), "cả hai rỗng (rc≠0 cả hai)" if same else "LỆCH rỗng"); bad += not same; continue
    jb = json.loads(b)
    for k in ("inception", "wtd", "mtd", "day"):
        if jb.get(k): jb[k].pop("benchmark", None)
    eq = json.dumps(jb, ensure_ascii=False, indent=2) + "\n" == a
    n += 1; bad += not eq; print(os.path.basename(c), "BẰNG từng byte" if eq else "KHÁC")
print(f"TỔNG {n} cặp có số, {bad} lệch"); sys.exit(1 if bad else 0)
PY
