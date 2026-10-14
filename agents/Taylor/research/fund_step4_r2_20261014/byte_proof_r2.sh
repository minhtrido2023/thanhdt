#!/usr/bin/env bash
# Vòng 2: (a) tỉ suất danh mục/pnl/mwr nhánh HEAD = master TỪNG BYTE (bỏ khối benchmark) trên CÙNG bản sao dữ
# liệu thật; (b) SpaceX inception tới 09-30 = −4,913% (mốc 30/06); (c) thiếu index_anchor_date ⇒ rc≠0 + lý do.
# Sandbox /tmp: ctl = code master canonical; sbx = code nhánh + account_inception.json.proposed + chuỗi TR bản sao.
set -uo pipefail
R=/home/trido/thanhdt/WorkingClaude; WT=$R/mike/agents/Taylor/wt-step4-1014
H=$WT/agents/Taylor/research/fund_step4_r2_20261014; MK=$WT/agents/Taylor/research/fund_step4_impl_20261014/mk_sandbox.sh
OUT=$H/byte_proof_r2; rm -rf "$OUT"; mkdir -p "$OUT"
bash "$MK" /tmp/s4r2_ctl "$R/mike" >/dev/null; bash "$MK" /tmp/s4r2_sbx "$WT" >/dev/null; bash "$MK" /tmp/s4r2_nof "$WT" >/dev/null
cp "$H/account_inception.json.proposed" /tmp/s4r2_sbx/data/account_inception.json
for s in sbx nof; do mkdir -p /tmp/s4r2_$s/data/benchmark; cp /tmp/tr2_sbx/data/benchmark/* /tmp/s4r2_$s/data/benchmark/; done
md5sum /tmp/s4r2_sbx/data/benchmark/vnindex_tr_daily.csv "$R/data/account_inception.json" > "$OUT/inputs_md5.txt"
git -C "$R/mike" rev-parse --short HEAD > "$OUT/ctl_rev.txt"; git -C "$WT" rev-parse --short HEAD > "$OUT/sbx_rev.txt"
for acc in SpaceX ZaloPay; do for d in 2026-07-03 2026-07-31 2026-08-31 2026-09-18 2026-09-25 2026-09-30 2026-10-02 2026-10-09 2026-10-13; do
  for s in ctl sbx nof; do
    (cd /tmp && env -u TZ WC_ROOT=/tmp/s4r2_$s python3 /tmp/s4r2_$s/mike/bin/nav_period_returns.py \
       --account $acc --report-date $d > "$OUT/${s}_${acc}_$d.json" 2> "$OUT/${s}_${acc}_$d.err"); echo "$s $acc $d rc=$?" >> "$OUT/rc.txt"
  done; done; done
python3 - "$OUT" <<'PY'
import glob, json, os, sys
o = sys.argv[1]; bad = n = 0
for c in sorted(glob.glob(f"{o}/ctl_*.json")):
    a = open(c).read(); b = open(c.replace("/ctl_", "/sbx_")).read()
    if not a or not b:
        same = a == b; print(os.path.basename(c), "cả hai rỗng" if same else "LỆCH rỗng"); bad += not same; continue
    jb = json.loads(b)
    for k in ("inception", "wtd", "mtd", "day"):
        if jb.get(k): jb[k].pop("benchmark", None)
    eq = json.dumps(jb, ensure_ascii=False, indent=2) + "\n" == a
    n += 1; bad += not eq; print(os.path.basename(c), "BẰNG từng byte" if eq else "KHÁC")
print(f"(a) TỔNG {n} cặp có số, {bad} lệch")
j = json.load(open(f"{o}/sbx_SpaceX_2026-09-30.json"))["inception"]["benchmark"]
print("(b) SpaceX inception→09-30:", j.get("index_anchor_date"), "giá", j.get("vnindex_price_pct"), "TR", j.get("vnindex_tr_pct"))
for acc in ("SpaceX", "ZaloPay"):
    for d in ("2026-09-30", "2026-10-09"):
        b = json.load(open(f"{o}/sbx_{acc}_{d}.json"))["inception"]["benchmark"]
        print(f"    {acc} {d}: mốc {b.get('index_anchor_date')} giá {b.get('vnindex_price_pct')} TR {b.get('vnindex_tr_pct')} chênh {b.get('excess_vs_price_pp')}")
print("(c) thiếu index_anchor_date:", open(f"{o}/nof_SpaceX_2026-09-30.err").read().strip().splitlines()[-1:] )
sys.exit(1 if bad else 0)
PY
echo "proof rc=$?"; grep -c "rc=0" "$OUT/rc.txt"; grep -v "rc=0" "$OUT/rc.txt" | head
