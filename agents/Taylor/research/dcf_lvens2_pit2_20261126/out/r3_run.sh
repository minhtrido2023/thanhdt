#!/usr/bin/env bash
# dựng lại + selfcheck vòng 3, tuần tự một luồng
set -u
cd "$(dirname "$0")/.."
export LVENS2_FROZEN=/home/trido/thanhdt/WorkingClaude/data/research_frozen/dcf_v31_inputs/out LVENS2_CA=out/ca/ca_extract_202611.csv LVENS2_CA_MD5=28418e9d4d91abfa8965ac756bb3d9c4 PYTHONHASHSEED=0
PY=/home/trido/thanhdt/wc_venv/bin/python; D=out/r3_logs; mkdir -p $D
for ym in 2026-05 2026-06 2026-07 2026-08 2026-09 2026-10; do /usr/bin/time -v $PY calc/lvens2_pit2.py --asof-ym $ym --mc-pit all --out-dir out/r3_final >> $D/rebuild.txt 2>> $D/rebuild_time.txt; echo "$ym rc=$?" >> $D/rebuild.txt; done
( cd out/final && md5sum ./*.parquet ) > $D/md5_final_ref.txt; ( cd out/r3_final && md5sum ./*.parquet ) > $D/md5_final_r3.txt
diff $D/md5_final_ref.txt $D/md5_final_r3.txt > $D/md5_diff.txt; echo "diff rc=$? n=$(wc -l < $D/md5_final_r3.txt)" >> $D/md5_diff.txt
rm -rf out/r3_regress; $PY calc/lvens2_pit2.py --asof-ym 2026-10 --mc-pit strict --no-eguard --out-dir out/r3_regress > $D/regress.txt 2>&1
$PY - >> $D/regress.txt 2>&1 <<'PY'
import glob, pandas as pd
a = pd.read_parquet(glob.glob("out/r3_regress/*.parquet")[0]); old = pd.read_parquet(glob.glob("out/regress/*2026-10*noeguard*.parquet")[0])
print("vs out/regress (bản đã đối chiếu merge):", a.shape, a.equals(old))
m = glob.glob("../dcf_lvens2_incremental_20261125/out/**/lvens2_2026-10*.parquet", recursive=True); print("merged candidates", m)
for f in m:
    b = pd.read_parquet(f); cols = [c for c in b.columns if c in a.columns]
    j = a.set_index("ticker")[[c for c in cols if c != "ticker"]]; k = b.set_index("ticker")[[c for c in cols if c != "ticker"]]
    print(f, len(a), len(b), "equal_on_common_cols", j.sort_index().equals(k.sort_index()))
PY
for tz in unset America/New_York Asia/Ho_Chi_Minh; do
  tag=${tz//\//_}; if [ $tz = unset ]; then pre="env -u TZ"; else pre="env TZ=$tz"; fi
  F=out/r3_final $pre bash calc/selfcheck_paper_cell_pit2.sh out/sc_ledger_r3_$tag > $D/scl_$tag.txt 2>&1; echo "rc=$?" >> $D/scl_$tag.txt
  for ym in 2026-10 2026-05; do $pre $PY calc/selfcheck_pit2.py $ym stepcar out/sc_r3_${tag}_$ym > $D/scp_${ym}_$tag.txt 2>&1; echo "rc=$?" >> $D/scp_${ym}_$tag.txt; done
done
touch $D/DONE
