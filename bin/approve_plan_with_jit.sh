#!/usr/bin/env bash
# Duyệt 1 plan giao dịch có lệnh bán PARK (L1 park_trim / L2 jit_unpark) tài trợ lệnh mua.
#
# ⚠️ SCRIPT NÀY KHÔNG CÒN MERGE GÌ (đổi 2026-08-11, job Taylor_20260810_185646).
#
# Trước đây nó tự gộp `jit_unpark_proposal` vào `orders[]` bằng dedup theo `id`. Cơ chế đó
# hỏng theo cả hai hướng và đã gây sự cố thật:
#   · 2026-08-07 — `merge_three_in_one_20260807.py` và script này dùng HAI namespace id khác
#     nhau (`SELL-{TK}-PARK-{i:02d}` vs `SELL-JIT-PARK-{TK}-01`) ⇒ dedup theo id mù hoàn toàn
#     ⇒ bán TRÙNG lô: thừa 1.200cp (SpaceX) + 400cp (ZaloPay);
#   · dedup `if oid in existing_ids: continue` là "thêm nếu chưa có" — nó KHÔNG BAO GIỜ sửa
#     được một lệnh đã sai khi artifact tính lại ra qty mới.
#
# Việc gộp nay do **`mike/bin/merge_park_orders.py`** làm, theo cơ chế SỞ HỮU-MỘT-VÙNG +
# DỰNG-LẠI (danh tính = `(ticker, side, nguồn)`, không phải `id`), có bất biến hậu kiểm và
# 120 ca selfcheck. Giữ hai writer trên cùng một vùng = tái lập đúng cấu hình sinh ra 08-07,
# nên đường merge cũ ở đây bị GỠ HẲN chứ không phải tắt bằng cờ.
#
# Script này giờ làm ĐÚNG hai việc:
#   1. CỔNG: từ chối duyệt nếu plan còn đề xuất bán PARK **chưa đi qua** merge_park_orders.py
#      (nếu không, duyệt xong sẽ ra một plan có lệnh mua mà KHÔNG có lệnh bán tài trợ — đúng
#      hình dạng mất-phiên 2026-08-06);
#   2. uỷ quyền phần duyệt thật cho `approve_plan_simple.sh` — script đó đã có sẵn kiểm trùng
#      ticker, kiểm Σ nguồn tài trợ ≥ Σ mua, atomic write, bus event và Discord notify. Nhân
#      bản logic duyệt ra hai chỗ là đúng cái bẫy `kb/coding_guidelines.md` §10 cảnh báo.
#
# DÙNG (không đổi):
#   bin/approve_plan_with_jit.sh SpaceX 2026-08-11 "user (John) - Discord, duyet mua DRI + ban PARK"
#   DRY_RUN=1 bin/approve_plan_with_jit.sh SpaceX 2026-08-11 "..."

set -euo pipefail

ACCOUNT="${1:?usage: approve_plan_with_jit.sh <account> <date YYYY-MM-DD> <approved-by-text>}"
PLAN_DATE="${2:?usage: approve_plan_with_jit.sh <account> <date YYYY-MM-DD> <approved-by-text>}"
APPROVED_BY="${3:?usage: approve_plan_with_jit.sh <account> <date YYYY-MM-DD> <approved-by-text>}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WC_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PLAN_PATH="$WC_ROOT/data/trade_plans/plan_${ACCOUNT}_${PLAN_DATE}.json"

if [[ ! -f "$PLAN_PATH" ]]; then
  echo "❌ không tìm thấy plan: $PLAN_PATH" >&2
  exit 2
fi

# ── CỔNG: plan đã đi qua merge_park_orders.py chưa? ──────────────────────────────────
# Bằng chứng = khoá cấp plan `merge_park_orders.owner == "park_merge_v1"` (bước 6 của merge).
#
# ⚠️ CỐ Ý KHÔNG dùng `_merged_into_orders` làm bằng chứng, dù nhìn thì hợp lý hơn: script
# one-off cũ `agents/DollarBill/merge_three_in_one_20260807.py` ghi Y HỆT chuỗi "✅ ĐÃ MERGE
# vào orders[]…" vào cùng khoá đó. Đã ĐO trên `plan_SpaceX_2026-08-07.json`: khối mang dấu ✅
# nhưng KHÔNG có `merge_park_orders` ⇒ nếu bám vào dấu ✅ thì cổng này công nhận một plan
# gộp bằng ĐÚNG cơ chế đã gây sự cố 08-07. Dấu ✅ là QUY ƯỚC dùng chung giữa hai writer;
# khoá `merge_park_orders.owner` là thứ chỉ cơ chế mới ghi ra. (Cùng bài học "quy ước ≠ bất
# biến" đã làm quant-skeptic REFUTED vòng 5 của chính dự án này.)
#
# KHÔNG suy ra bằng cách đếm lệnh bán trong orders[]: merge được phép cắt một mã về 0cp theo
# trần sellable, lúc đó "không có lệnh bán" là kết quả ĐÚNG chứ không phải dấu hiệu chưa chạy.
python3 - "$PLAN_PATH" "$ACCOUNT" "$PLAN_DATE" <<'PYEOF'
import json, os, sys

path, account, plan_date = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path, encoding="utf-8") as f:
    plan = json.load(f)

stamp = plan.get("merge_park_orders")
merged_ran = isinstance(stamp, dict) and stamp.get("owner") == "park_merge_v1"

# Nguồn bằng chứng phải là ARTIFACT TRÊN ĐĨA, không chỉ khối nhúng trong plan.
# (quant-skeptic 2026-08-11, killer objection — đã tự dựng ca và chạy thật để xác nhận.)
# `compute_park_trim.py`/`compute_jit_unpark.py` ghi ra FILE (`--out`), chúng KHÔNG bao giờ
# ghi khối `*_proposal` vào plan; trong chuỗi cron đề xuất, khối đó do chính merge ghi ở
# bước 6. ⇒ nếu chỉ nhìn khối trong plan thì một plan "có lệnh mua, chưa merge lần nào" là
# plan KHÔNG có khối, KHÔNG có dấu ⇒ cổng cho qua ⇒ đúng ca cần chặn lại lọt.
# Nhìn file trên đĩa thì bằng chứng độc lập với việc merge đã chạy hay chưa.
plan_dir = os.path.dirname(os.path.abspath(path))
SOURCES = (("park_trim_proposal", f"park_trim_{account}_{plan_date}.json", "L1 park_trim"),
           ("jit_unpark_proposal", f"jit_unpark_{account}_{plan_date}.json", "L2 jit_unpark"))

problems, warns = [], []
for key, artifact_name, layer in SOURCES:
    block = plan.get(key)
    n = 0
    if isinstance(block, dict):
        n = len([o for o in (block.get("orders") or []) if (o.get("qty") or 0) > 0])
    # artifact trên đĩa — nguồn độc lập, dùng khi plan chưa mang khối nào
    art_path = os.path.join(plan_dir, artifact_name)
    if os.path.exists(art_path):
        try:
            with open(art_path, encoding="utf-8") as f:
                art = json.load(f)
            n = max(n, len([o for o in (art.get("orders") or []) if (o.get("qty") or 0) > 0]))
        except (OSError, ValueError) as e:
            problems.append(f"{artifact_name}: có trên đĩa nhưng KHÔNG đọc được ({e}) — "
                            f"không thể khẳng định plan đã gộp đủ. Fail-closed.")
            continue
    if n == 0:
        continue
    mark = block.get("_merged_into_orders") if isinstance(block, dict) else None
    if not merged_ran:
        problems.append(
            f"{key}: có {n} đề xuất bán {layer} nhưng plan KHÔNG mang dấu chạy "
            f"`merge_park_orders.owner=park_merge_v1`"
            + (f" (khối có `_merged_into_orders`={str(mark)[:40]!r} — dấu này script one-off "
               f"CŨ cũng ghi, KHÔNG chứng minh được cơ chế mới đã chạy)" if mark else "")
            + ".")
    elif mark and not str(mark).startswith("✅"):
        warns.append(f"{key}: merge đã chạy nhưng KHÔNG gộp tầng này — {mark}")

for w in warns:
    print(f"⚠  {w}")

if problems:
    print("❌ TỪ CHỐI DUYỆT — plan chưa qua bước gộp lệnh bán PARK:", file=sys.stderr)
    for p in problems:
        print(f"   · {p}", file=sys.stderr)
    print("\n   Duyệt lúc này sẽ ra plan có lệnh MUA mà thiếu lệnh BÁN tài trợ (hình dạng\n"
          "   mất-phiên 2026-08-06). Chạy bước gộp trước, xem báo cáo, rồi duyệt lại:\n",
          file=sys.stderr)
    print(f"     python3 mike/bin/merge_park_orders.py --account {plan.get('account','<acct>')} "
          f"--plan-date {plan.get('plan_date','<date>')}            # dry-run, chỉ in báo cáo",
          file=sys.stderr)
    print("     …rồi thêm --write để ghi thật.\n", file=sys.stderr)
    sys.exit(2)

print("✅ cổng gộp: plan đã đi qua merge_park_orders.py (hoặc không có đề xuất bán PARK nào).")
PYEOF

# ── duyệt thật — một implementation duy nhất ─────────────────────────────────────────
exec "$SCRIPT_DIR/approve_plan_simple.sh" "$ACCOUNT" "$PLAN_DATE" "$APPROVED_BY"
