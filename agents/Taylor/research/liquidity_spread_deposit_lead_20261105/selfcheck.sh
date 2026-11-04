#!/usr/bin/env bash
# D2 selfcheck: TZ-invariance (byte-identical), Mike's measurement, fail-closed paths.
set -u
cd "$(dirname "$0")"
PY=/home/trido/thanhdt/wc_venv/bin/python
T=$(mktemp -d); fails=0
ok(){ echo "PASS $1"; }; bad(){ echo "FAIL $1"; fails=$((fails+1)); }
env -u TZ $PY analysis.py --asof 2026-11-05 >"$T/a.txt" 2>&1 && cp results.json "$T/a.json" || bad "run env -u TZ"
TZ=America/New_York $PY analysis.py --asof 2026-11-05 >"$T/b.txt" 2>&1 && cp results.json "$T/b.json" || bad "run TZ=NY"
cmp -s "$T/a.txt" "$T/b.txt" && cmp -s "$T/a.json" "$T/b.json" && ok "TZ byte-identical" || bad "TZ output differs"
$PY - "$T/a.json" <<'PY' && ok "mike check +2.33pp / ~93%; verdict+N" || bad "mike check / verdict"
import json,sys; R=json.load(open(sys.argv[1])); m=R["mike_check"]
assert abs(m["S_last"]-2.33)<=0.01, m
assert abs(m["pct_le"]-93)<=1, m
assert R["verdict"]["n_eval"]==3 and R["verdict"]["label"]=="ỦNG HỘ", R["verdict"]
assert R["prereg_md5"]=="2098a999f2daade7dff3c4332996637c", R["prereg_md5"]
PY
# fail-closed: stale asof
$PY analysis.py --asof 2026-12-01 >/dev/null 2>"$T/e1"; rc=$?
[ $rc -eq 2 ] && grep -q "stale" "$T/e1" && ok "stale -> rc2" || bad "stale rc=$rc $(cat "$T/e1")"
# fail-closed: tampered TE snapshot (md5)
sed '5s/[0-9]$/9/' data/te_ib3m_policy.csv >"$T/te.csv"
D2_TE_CSV="$T/te.csv" $PY analysis.py --asof 2026-11-05 >/dev/null 2>"$T/e2"; rc=$?
[ $rc -eq 2 ] && grep -q "md5" "$T/e2" && ok "tampered TE -> rc2" || bad "tamper rc=$rc"
# fail-closed: truncated deposit CSV
head -50 data/fiinprox_deposit_1m_big4_monthly_2019_2026.csv >"$T/dep.csv"
D2_DEP1M_CSV="$T/dep.csv" $PY analysis.py --asof 2026-11-05 >/dev/null 2>"$T/e3"; rc=$?
[ $rc -eq 2 ] && grep -q "CSV 1T" "$T/e3" && ok "truncated dep -> rc2" || bad "dep rc=$rc"
# restore canonical results
$PY analysis.py --asof 2026-11-05 >run_main.txt 2>&1
rm -rf "$T"; echo "fails=$fails"; exit $fails
