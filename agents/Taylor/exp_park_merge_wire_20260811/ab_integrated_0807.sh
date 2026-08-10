#!/usr/bin/env bash
# A/B TÍCH HỢP trên dữ liệu thật 2026-08-07 — chạy qua ĐƯỜNG THẬT (CLI + script duyệt thật),
# KHÔNG gọi thẳng hàm merge_park_orders() như 10 vòng verify trước.
#
# Vì sao phải làm lại dù 10 vòng trước đã khớp 6.900/2.500: 10 vòng đó verify LÕI HÀM. Bề mặt
# mới của lần wire này là (a) `main()` đọc file/ghi file, (b) cổng mới trong
# approve_plan_with_jit.sh, (c) chỗ nối giữa hai thứ đó. Bug ở chỗ nối là thứ test hàm thuần
# không thể thấy (chính là cách khuyết tật "artifact vắng mặt" lọt qua 10 vòng).
#
# CHỈ ĐỌC dữ liệu thật: mọi thứ chép sang tmp, plan production KHÔNG bị đụng.
# Chạy: bash mike/agents/Taylor/exp_park_merge_wire_20260811/ab_integrated_0807.sh
set -uo pipefail

WC=/home/trido/thanhdt/WorkingClaude
WORK=$(mktemp -d /tmp/ab_wire_XXXX)
trap 'echo "(tmp giữ lại để soi: $WORK)"' EXIT

# ── cây giả cho script duyệt (nó tự suy WC_ROOT = <script>/../..) ────────────────────
mkdir -p "$WORK/mike/bin" "$WORK/data/trade_plans"
cp "$WC/mike/bin/approve_plan_with_jit.sh" "$WC/mike/bin/approve_plan_simple.sh" "$WORK/mike/bin/"
chmod +x "$WORK/mike/bin/"*.sh
for f in append_event.sh notify_thread.sh; do
  printf '#!/usr/bin/env bash\necho "%s $*" >> "$(dirname "$0")/../../calls.log"\n' "$f" \
    > "$WORK/mike/bin/$f"
  chmod +x "$WORK/mike/bin/$f"
done

PD="$WORK/data/trade_plans"
for a in SpaceX ZaloPay; do
  cp "$WC/data/trade_plans/plan_${a}_2026-08-07.json"       "$PD/"
  cp "$WC/data/trade_plans/park_trim_${a}_2026-08-07.json"  "$PD/"
  cp "$WC/data/trade_plans/jit_unpark_${a}_2026-08-07.json" "$PD/"
done

# Bản thật ĐÃ ký duyệt (user John 12:36). Bỏ chữ ký để so CƠ CHẾ chứ không so chữ ký —
# merge cố ý TỪ CHỐI sửa plan đã duyệt, giữ chữ ký thì mọi chân đều REFUSED và A/B vô nghĩa.
python3 - "$PD" <<'PY'
import json, sys, pathlib
for p in pathlib.Path(sys.argv[1]).glob("plan_*.json"):
    d = json.loads(p.read_text(encoding="utf-8"))
    HUMAN = {o["ticker"]: o["qty"] for o in d["orders"] if o.get("side") == "sell"}
    (p.parent / f"human_{p.stem}.json").write_text(json.dumps(HUMAN), encoding="utf-8")
    d["approved_by"] = None
    d["approved_at"] = None
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
PY

# Chân B: dựng lại trạng thái HỎNG 08-07 — thêm LẠI lệnh JIT gốc ở namespace id CŨ, đúng
# cách `approve_plan_with_jit.sh` (bản cũ) đã ghi. Làm trên bản sao riêng.
mkdir -p "$WORK/legB"; cp "$PD"/*.json "$WORK/legB/"
python3 - "$WORK/legB" <<'PY'
import json, sys, pathlib
d = pathlib.Path(sys.argv[1])
for a in ("SpaceX", "ZaloPay"):
    plan = json.loads((d / f"plan_{a}_2026-08-07.json").read_text(encoding="utf-8"))
    l2   = json.loads((d / f"jit_unpark_{a}_2026-08-07.json").read_text(encoding="utf-8"))
    for jo in l2["orders"]:
        plan["orders"].insert(0, {
            "id": f"SELL-JIT-PARK-{jo['ticker']}-01", "ticker": jo["ticker"], "side": "sell",
            "qty": jo["qty"], "ref_price": jo["ref_price"], "book": "PARK",
            "play_type": "JIT_UNPARK", "priority": 0})
    (d / f"plan_{a}_2026-08-07.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2),
                                                 encoding="utf-8")
PY

echo "════ CỔNG DUYỆT TRƯỚC KHI GỘP (phải TỪ CHỐI) ════"
# Chạy trên BẢN SAO RIÊNG: nếu chạy thẳng trên $PD, cổng (nếu cho qua) sẽ KÝ plan, và mọi
# chân merge sau đó bị từ chối vì "plan đã duyệt" — lỗi của chính harness này ở lần chạy đầu,
# nhìn ra y hệt một kết quả A/B hợp lệ (Σ vẫn khớp vì REFUSED trả plan nguyên vẹn).
mkdir -p "$WORK/gate_pre/mike/bin" "$WORK/gate_pre/data/trade_plans"
cp "$WORK/mike/bin/"*.sh "$WORK/gate_pre/mike/bin/"; chmod +x "$WORK/gate_pre/mike/bin/"*.sh
cp "$PD"/*.json "$WORK/gate_pre/data/trade_plans/"
for a in SpaceX ZaloPay; do
  out=$(DRY_RUN=0 "$WORK/gate_pre/mike/bin/approve_plan_with_jit.sh" "$a" 2026-08-07 \
        "user (test A/B)" 2>&1); rc=$?
  sig=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('approved_by'))" \
        "$WORK/gate_pre/data/trade_plans/plan_${a}_2026-08-07.json")
  echo "  $a: rc=$rc (kỳ vọng ≠0) · approved_by=$sig (kỳ vọng None)"
done

echo
echo "════ CHÂN A (plan người đã sửa đúng) + CHÂN B (dựng lại trạng thái HỎNG) ════"
for leg in A B; do
  dir=$PD; [ "$leg" = B ] && dir=$WORK/legB
  for a in SpaceX ZaloPay; do
    python3 "$WC/mike/bin/merge_park_orders.py" --account "$a" --plan-date 2026-08-07 \
            --plan-dir "$dir" --write > "$WORK/merge_${leg}_${a}.log" 2>&1
    rc=$?
    python3 - "$dir" "$a" "$leg" "$rc" <<'PY'
import json, sys, pathlib
d, a, leg, rc = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
plan = json.loads((d / f"plan_{a}_2026-08-07.json").read_text(encoding="utf-8"))
human = json.loads((d / f"human_plan_{a}_2026-08-07.json").read_text(encoding="utf-8"))
auto = {}
for o in plan["orders"]:
    if o.get("side") == "sell":
        auto[o["ticker"]] = auto.get(o["ticker"], 0) + o["qty"]
stamp = plan.get("merge_park_orders", {})
ran = rc == "0" and stamp.get("owner") == "park_merge_v1"
ok = auto == human and ran
print(f"  chân {leg} {a:8s}: rc={rc} merge THẬT SỰ chạy={ran} khớp người duyệt={auto == human}  "
      f"Σ auto={sum(auto.values())} / Σ người={sum(human.values())}"
      + ("" if ok else f"  LỆCH={ {k: (human.get(k), auto.get(k)) for k in set(human) | set(auto) if human.get(k) != auto.get(k)} }"))
PY
  done
done

echo
echo "════ CỔNG DUYỆT SAU KHI GỘP (phải CHO QUA + ghi chữ ký) ════"
for a in SpaceX ZaloPay; do
  DRY_RUN=0 "$WORK/mike/bin/approve_plan_with_jit.sh" "$a" 2026-08-07 "user (test A/B)" \
    > "$WORK/approve_${a}.log" 2>&1
  rc=$?
  python3 - "$PD" "$a" "$rc" <<'PY'
import json, sys, pathlib
d, a, rc = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
p = json.loads((d / f"plan_{a}_2026-08-07.json").read_text(encoding="utf-8"))
sells = {}
for o in p["orders"]:
    if o.get("side") == "sell":
        sells[o["ticker"]] = sells.get(o["ticker"], 0) + o["qty"]
print(f"  {a:8s}: rc={rc} · approved_by={p.get('approved_by')!r} · "
      f"Σ bán SAU khi duyệt={sum(sells.values())} (phải KHÔNG đổi so với sau merge)")
PY
done
