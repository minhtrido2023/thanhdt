#!/usr/bin/env bash
# Selfcheck sổ trên BẢN TẠM (không chạm kb/dd_price_zones.json): kịch bản A và B, mỗi kịch bản 3 TZ.
set -u
ROOT="$1"; OUT="$2"; F=agents/Taylor/research/dd_HHS_PAT_followup_20261125; W3=agents/Taylor/research/dd_recheck_20261125w3/HHS
for SC in A B; do
  TMP=$(mktemp /tmp/ddpz_${SC}_XXXX.json)
  if [ "$SC" = A ]; then HP=$W3/LEDGER_PROPOSAL_HHS.json; HA=$W3/adj.json; else HP=$F/HHS/LEDGER_PROPOSAL_HHS_B.json; HA=$F/HHS/adj_B.json; fi
  python3 - "$ROOT" "$TMP" "$HP" <<'PY'
import json, sys, datetime as dt
root, tmp, hp = sys.argv[1:4]
led = json.load(open(f"{root}/kb/dd_price_zones.json"))
now = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(timespec="seconds")
for p in (hp, "agents/Taylor/research/dd_HHS_PAT_followup_20261125/PAT/LEDGER_PROPOSAL_PAT_rev6_text.json"):
    e = json.load(open(f"{root}/{p}"))["entry"]; e["recorded_at"] = now; led["entries"].append(e)
json.dump(led, open(tmp, "w"), ensure_ascii=False, indent=1)
print("entries", len(led["entries"]))
PY
  python3 "$ROOT/bin/dd_ledger_append_center_adj.py" --ledger "$TMP" --root "$ROOT" --adj HHS="$HA" --write 2>&1 | tail -3
  for TZV in UTC Asia/Ho_Chi_Minh America/New_York; do
    TZ=$TZV MIKE_SRC_ROOT="$ROOT" python3 "$ROOT/bin/dd_price_zones_selfcheck.py" --ledger "$TMP" > "$OUT/selfcheck_${SC}_${TZV//\//_}.txt" 2>&1
    echo "SC=$SC TZ=$TZV rc=$? $(tail -1 "$OUT/selfcheck_${SC}_${TZV//\//_}.txt")"
  done
  python3 -c "import json;d=json.load(open('$TMP'));print('final entries',len(d['entries']))"
  rm -f "$TMP"
done
