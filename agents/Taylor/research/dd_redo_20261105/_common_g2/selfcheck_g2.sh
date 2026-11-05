#!/usr/bin/env bash
# Tự kiểm job Taylor_20261105_014130: chạy lại 4 mô hình + SUMMARY, so md5 trước/sau (tất định), in bảng tổng hợp.
set -euo pipefail
B="$(cd "$(dirname "$0")/.." && pwd)"; PY="${DNA_PYEXE:-/home/trido/thanhdt/wc_venv/bin/python}"
for T in SIP SCL TV1 TV2; do
  t=$(echo "$T" | tr 'A-Z' 'a-z')
  before=$(md5sum "$B/$T/calc/model_${t}_out.json" "$B/$T/SUMMARY.json" | awk '{print $1}' | tr '\n' ' ')
  (cd "$B/$T/calc" && "$PY" -I "model_${t}.py" >/dev/null 2>&1)
  (cd "$B/_common_g2" && "$PY" -I make_summary.py "$T" >/dev/null)
  after=$(md5sum "$B/$T/calc/model_${t}_out.json" "$B/$T/SUMMARY.json" | awk '{print $1}' | tr '\n' ' ')
  [ "$before" = "$after" ] && echo "$T reproducible OK" || { echo "$T MISMATCH $before vs $after"; exit 1; }
done
"$PY" -I - "$B" <<'PY'
import json, sys, os
B = sys.argv[1]; rows = []
for T in ("SIP", "SCL", "TV1", "TV2"):
    S = json.load(open(os.path.join(B, T, "SUMMARY.json")))
    M = json.load(open(os.path.join(B, T, "calc", f"model_{T.lower()}_out.json")))
    assert S["center_post_liq"] == round(M["center_post_liq"]) and S["p10_post"] == round(M["P_post"]["p10"]) and S["p90_post"] == round(M["P_post"]["p90"])
    rows.append(S)
f = lambda x: f"{x:,.0f}".replace(",", ".")
print("| Mã | Giá 04/11 | Tâm sau CK | P10 | P50 | P90 | Giá/tâm | Nhãn | Tâm cũ | Mới/cũ |")
print("|---|---|---|---|---|---|---|---|---|---|")
for S in rows:
    print(f"| {S['ticker']} | {f(S['price'])} | {f(S['center_post_liq'])} | {f(S['p10_post'])} | {f(S['p50_post'])} | {f(S['p90_post'])} | {S['px_vs_center']:+.1%} | {S['label']} | {f(S['zone_old']['center'])} | {S['center_new_vs_old']:+.1%} |")
PY
