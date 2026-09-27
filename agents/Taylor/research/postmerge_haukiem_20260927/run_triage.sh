#!/bin/bash
# Triage 2 selfcheck FAIL sau merge ticket 1: gia thuyet = control leg (module tien-sua)
# khong co buoc OShares tai EX-DATE, nen phai ep BASKET_OSHARES_STEP=quarter cho ban HIEN TAI.
WC=/home/trido/thanhdt/WorkingClaude
OUT=$WC/mike/agents/Taylor/research/postmerge_haukiem_20260927/selfchecks
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
export WORKDIR_8L="$WC"
DNA=/home/trido/thanhdt/wc_venv/bin/python
cd "$WC" || exit 9

TZ=Asia/Ho_Chi_Minh BASKET_OSHARES_STEP=quarter "$DNA" "$WC/basket_price_basis_selfcheck.py" \
  > "$OUT/basket_price_basis_selfcheck__STEPQUARTER2__TZ-ICT__dnapy.log" 2>&1
echo "RC_pricebasis_quarter=$?"

TZ=Asia/Ho_Chi_Minh BASKET_OSHARES_STEP=quarter BASKET_RETLEG_PREREF=2c098c1a \
  "$DNA" "$WC/basket_return_leg_oshares_selfcheck.py" \
  > "$OUT/basket_return_leg_oshares_selfcheck__PREREF2c_STEPQUARTER__TZ-ICT__dnapy.log" 2>&1
echo "RC_retleg_preref_quarter=$?"

TZ=Asia/Ho_Chi_Minh BASKET_RETLEG_PREREF=2c098c1a \
  "$DNA" "$WC/basket_return_leg_oshares_selfcheck.py" \
  > "$OUT/basket_return_leg_oshares_selfcheck__PREREF2c_EXDATE__TZ-ICT__dnapy.log" 2>&1
echo "RC_retleg_preref_exdate=$?"
echo "=== TRIAGE DONE ==="
