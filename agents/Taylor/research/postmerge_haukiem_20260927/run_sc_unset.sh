#!/bin/bash
# Hoan tat cac hang TZ=unset cua sweep (job goc bi cat giua chung).
WC=/home/trido/thanhdt/WorkingClaude
OUT=$WC/mike/agents/Taylor/research/postmerge_haukiem_20260927/selfchecks
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export WORKDIR_8L="$WC"
DNA=/home/trido/thanhdt/wc_venv/bin/python
WC_SC="basket_oshares_step_exdate_selfcheck.py basket_return_leg_oshares_selfcheck.py basket_price_basis_selfcheck.py dsr_family_manifest_selfcheck.py"
MK_SC="nav_flow_term_selfcheck.py annualization_basis_selfcheck.py reconcile_equity_egg_selfcheck.py asof_label_selfcheck.py"
SUM="$OUT/SUMMARY_unset.tsv"; : > "$SUM"
for pyspec in "python3|py310" "$DNA|dnapy"; do
  py="${pyspec%%|*}"; pyl="${pyspec##*|}"
  for s in $WC_SC; do
    f="$OUT/${s%.py}__TZ-unset__${pyl}.log"
    ( cd "$WC" && env -u TZ "$py" "$WC/$s" ) > "$f" 2>&1; rc=$?
    printf '%s\t%s\tunset\t%s\n' "$rc" "${s%.py}" "$pyl" >> "$SUM"; echo "RC=$rc ${s%.py} unset $pyl"
  done
  for s in $MK_SC; do
    f="$OUT/${s%.py}__TZ-unset__${pyl}.log"
    ( cd "$WC/mike" && env -u TZ "$py" "$WC/mike/bin/$s" ) > "$f" 2>&1; rc=$?
    printf '%s\t%s\tunset\t%s\n' "$rc" "${s%.py}" "$pyl" >> "$SUM"; echo "RC=$rc ${s%.py} unset $pyl"
  done
done
echo "=== UNSET DONE ==="
