#!/bin/bash
cd /home/trido/thanhdt/WorkingClaude || exit 9
OUT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_hau_kiem_20260927
export PATH="$PATH:/home/trido/google-cloud-sdk/bin" CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh
DNA=/home/trido/thanhdt/wc_venv/bin/python
for tzspec in "UTC" "America/New_York"; do
  lbl=$(echo "$tzspec" | tr '/' '_')
  env TZ=$tzspec BQ_LOCAL_CACHE=data/bq_cache $DNA basket_price_basis_selfcheck.py > "$OUT/sc_pricebasis_main_TZ_$lbl.log" 2>&1
  echo "pricebasis TZ=$tzspec rc=$?" >> "$OUT/run_pb.done"
done
