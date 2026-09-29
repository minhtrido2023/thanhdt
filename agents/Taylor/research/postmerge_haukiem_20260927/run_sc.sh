#!/bin/bash
# Hoi quy selfcheck tren MAIN canonical sau merge dot audit 27/09 (job Taylor_20260927_064745).
# 3 TZ (ICT / UTC / env -u TZ) x 2 interpreter (python3 = 3.10, $DNA_PYEXE = 3.12), §16 + §19.
WC=/home/trido/thanhdt/WorkingClaude
OUT=$WC/mike/agents/Taylor/research/postmerge_haukiem_20260927/selfchecks
mkdir -p "$OUT"
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export WORKDIR_8L="$WC"
DNA=/home/trido/thanhdt/wc_venv/bin/python
WC_SC="basket_oshares_step_exdate_selfcheck.py basket_return_leg_oshares_selfcheck.py basket_price_basis_selfcheck.py dsr_family_manifest_selfcheck.py"
MK_SC="nav_flow_term_selfcheck.py annualization_basis_selfcheck.py reconcile_equity_egg_selfcheck.py asof_label_selfcheck.py"
SUM="$OUT/SUMMARY.tsv"
: > "$SUM"

run_one() {  # $1=script $2=cwd $3=label $4=pyexe $5=tzspec $6=tzlabel $7=pylabel
  local s="$1" cw="$2" lab="$3" py="$4" tz="$5" tzl="$6" pyl="$7" rc
  local f="$OUT/${lab}__TZ-${tzl}__${pyl}.log"
  ( cd "$cw" || exit 9
    if [ "$tzl" = "unset" ]; then env -u TZ "$py" "$s"; else TZ="$tz" "$py" "$s"; fi ) > "$f" 2>&1
  rc=$?
  printf '%s\t%s\t%s\t%s\n' "$rc" "$lab" "$tzl" "$pyl" >> "$SUM"
  echo "RC=$rc $lab TZ=$tzl $pyl"
}

for spec in "Asia/Ho_Chi_Minh|ICT" "UTC|UTC" "|unset"; do
  tz="${spec%%|*}"; tzl="${spec##*|}"
  for pyspec in "python3|py310" "$DNA|dnapy"; do
    py="${pyspec%%|*}"; pyl="${pyspec##*|}"
    for s in $WC_SC; do
      [ -f "$WC/$s" ] || { echo "MISSING $WC/$s"; continue; }
      run_one "$WC/$s" "$WC" "${s%.py}" "$py" "$tz" "$tzl" "$pyl"
    done
    for s in $MK_SC; do
      [ -f "$WC/mike/bin/$s" ] || { echo "MISSING mike/bin/$s"; continue; }
      run_one "$WC/mike/bin/$s" "$WC/mike" "${s%.py}" "$py" "$tz" "$tzl" "$pyl"
    done
  done
done
echo "=== ALL DONE ==="
