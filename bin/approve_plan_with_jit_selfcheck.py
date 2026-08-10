#!/usr/bin/env python3
"""Selfcheck cho `bin/approve_plan_with_jit.sh` sau khi GỠ đường merge cũ (2026-08-11,
job Taylor_20260810_185646).

Hai thứ phải đúng cùng lúc, và chúng kéo ngược chiều nhau:
  1. script KHÔNG BAO GIỜ tự thêm lệnh vào `orders[]` nữa (đường merge cũ đã gỡ hẳn —
     giữ hai writer trên cùng một vùng là tái lập đúng cấu hình sinh ra sự cố 08-07);
  2. nhưng cũng KHÔNG được duyệt một plan còn đề xuất bán PARK chưa qua
     `merge_park_orders.py` — duyệt lúc đó ra plan có lệnh MUA mà thiếu lệnh BÁN tài trợ,
     đúng hình dạng mất-phiên 08-06. Gỡ (1) mà quên (2) là đổi một lớp lỗi lấy lớp kia.

Cách chạy: dựng CÂY GIẢ trong tmp (`mike/bin/` + `data/trade_plans/`) rồi chạy CHÍNH script
thật ở đó — không mock hàm, không trích khối python. Nhờ vậy nó kiểm luôn cả đường uỷ quyền
sang `approve_plan_simple.sh` (bug ở chỗ nối là thứ test-hàm-thuần không thể thấy).
`append_event.sh` / `notify_thread.sh` bị thay bằng stub ghi log — KHÔNG đụng bus thật
(coding_guidelines §5b: selfcheck không được gây tác dụng phụ ra kênh ngoài).

Chạy: python3 mike/bin/approve_plan_with_jit_selfcheck.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BIN = Path(__file__).resolve().parent
FAILS = []


def check(name, cond, detail=""):
    print(("  ✔ " if cond else "  ✘ ") + name + ("" if cond else f" — {detail}"))
    if not cond:
        FAILS.append(f"{name}: {detail}")


def make_tree():
    """Cây giả: <root>/mike/bin/*.sh + <root>/data/trade_plans/ (khớp WC_ROOT=SCRIPT_DIR/../..)."""
    root = Path(tempfile.mkdtemp(prefix="apjit_sc_"))
    fake_bin = root / "mike" / "bin"
    fake_bin.mkdir(parents=True)
    (root / "data" / "trade_plans").mkdir(parents=True)
    for f in ("approve_plan_with_jit.sh", "approve_plan_simple.sh"):
        shutil.copy(BIN / f, fake_bin / f)
        os.chmod(fake_bin / f, 0o755)
    # stub: ghi lại việc được gọi, KHÔNG chạm bus/Discord thật
    for f in ("append_event.sh", "notify_thread.sh"):
        p = fake_bin / f
        p.write_text(f'#!/usr/bin/env bash\necho "{f} $*" >> "$(dirname "$0")/../../calls.log"\n')
        os.chmod(p, 0o755)
    return root


def write_plan(root, account, date, plan):
    p = root / "data" / "trade_plans" / f"plan_{account}_{date}.json"
    p.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def run(root, account, date, dry=False):
    env = dict(os.environ, DRY_RUN="1" if dry else "0")
    return subprocess.run(
        [str(root / "mike" / "bin" / "approve_plan_with_jit.sh"), account, date, "user (test)"],
        capture_output=True, text=True, env=env)


BUY = {"id": "BUY-DRI-LAG-01", "ticker": "DRI", "side": "buy", "qty": 1800,
       "ref_price": 13100.0, "priority": 1, "total_with_fee_vnd": 23_597_685}
SELL = {"id": "PARKMERGE-SELL-VHM", "ticker": "VHM", "side": "sell", "qty": 400,
        "ref_price": 76500.0, "priority": 0, "book": "PARK",
        "play_type": "PARK_TRIM+JIT_UNPARK", "merge_owner": "park_merge_v1",
        "estimated_proceeds_vnd": 30_600_000, "fee_est_vnd": 22_950}
JIT_ORDERS = [{"ticker": "VHM", "side": "sell", "qty": 100, "ref_price": 76500.0}]


# Dấu CHẠY do chính merge_park_orders.py ghi (bước 6). Đây — KHÔNG phải `_merged_into_orders`
# — là bằng chứng cổng bám vào: script one-off cũ ghi trùng chuỗi "✅ ĐÃ MERGE" nhưng không
# bao giờ ghi khoá này (đã đo trên plan_SpaceX_2026-08-07.json thật).
STAMP = {"owner": "park_merge_v1", "n_generated": 1, "n_dropped_owned": 0}


def base_plan(merged=False, **kw):
    p = {"plan_date": "2026-08-11", "account": "SpaceX", "orders": [dict(SELL), dict(BUY)],
         "approved_by": None, "requires_user_approval": True,
         "nav_basis": {"available_cash_before_vnd": 50_000_000}}
    if merged:
        p["merge_park_orders"] = dict(STAMP)
    p.update(kw)
    return p


print("=== approve_plan_with_jit_selfcheck ===")
print("\n[G] Cổng 'plan đã qua merge_park_orders.py chưa'")

# G1 — đề xuất L2 CÓ lệnh nhưng KHÔNG có dấu merge ⇒ phải TỪ CHỐI, không ghi gì.
root = make_tree()
pp = write_plan(root, "SpaceX", "2026-08-11",
                base_plan(jit_unpark_proposal={"decision": "JIT", "orders": JIT_ORDERS}))
r = run(root, "SpaceX", "2026-08-11")
after = json.loads(pp.read_text())
check("G1 đề xuất bán PARK chưa qua merge ⇒ exit≠0 (từ chối duyệt)", r.returncode != 0,
      f"rc={r.returncode}")
check("G1 KHÔNG ghi approved_by", after.get("approved_by") is None, str(after.get("approved_by")))
check("G1 thông báo chỉ đúng lệnh cần chạy (merge_park_orders.py)",
      "merge_park_orders.py" in r.stderr, r.stderr[-200:])
check("G1 KHÔNG gọi bus/Discord", not (root / "calls.log").exists())

# G2 — cùng plan đó nhưng đã mang dấu ✅ ⇒ qua cổng, duyệt được.
root = make_tree()
pp = write_plan(root, "SpaceX", "2026-08-11",
                base_plan(merged=True,
                          jit_unpark_proposal={"decision": "JIT", "orders": JIT_ORDERS,
                                              "_merged_into_orders": "✅ ĐÃ MERGE vào orders[]"}))
r = run(root, "SpaceX", "2026-08-11")
after = json.loads(pp.read_text())
check("G2 plan đã qua merge ⇒ duyệt thành công", r.returncode == 0,
      f"rc={r.returncode} {r.stderr[-200:]}")
check("G2 đã ghi approved_by", after.get("approved_by") == "user (test)",
      str(after.get("approved_by")))
check("G2 CÓ gọi bus + Discord", (root / "calls.log").exists()
      and "append_event.sh" in (root / "calls.log").read_text()
      and "notify_thread.sh" in (root / "calls.log").read_text())

# G3 — ĐƯỜNG MERGE CŨ ĐÃ GỠ: script không được tự thêm lệnh nào vào orders[].
#      Đề xuất L2 có VHM 100cp; bản CŨ sẽ thêm `SELL-JIT-PARK-VHM-01` (id khác ⇒ dedup mù)
#      ⇒ orders[] nở từ 2 lên 3 và VHM bị bán 400+100=500cp. Đây chính là sự cố 08-07.
check("G3 orders[] KHÔNG nở ra (2 lệnh trước, 2 lệnh sau)", len(after["orders"]) == 2,
      f"{len(after['orders'])} lệnh: {[o['id'] for o in after['orders']]}")
check("G3 tổng bán VHM vẫn 400cp, KHÔNG thành 500cp (không tái lập 08-07)",
      sum(o["qty"] for o in after["orders"]
          if o["side"] == "sell" and o["ticker"] == "VHM") == 400)
check("G3 không có lệnh nào mang id namespace cũ SELL-JIT-PARK-*",
      not any(str(o.get("id", "")).startswith("SELL-JIT-PARK-") for o in after["orders"]))

# G4 — merge ĐÃ chạy nhưng cố ý KHÔNG gộp tầng đó (dán ⛔) ⇒ hợp lệ, chỉ cảnh báo.
root = make_tree()
pp = write_plan(root, "SpaceX", "2026-08-11",
                base_plan(merged=True, jit_unpark_proposal={
                    "decision": "JIT", "orders": JIT_ORDERS,
                    "_merged_into_orders": "⛔ KHÔNG merge vào orders[] — reconcile_ok=False"}))
r = run(root, "SpaceX", "2026-08-11")
check("G4 dấu ⛔ ⇒ vẫn duyệt được (merge ĐÃ chạy, chỉ là không gộp tầng đó)",
      r.returncode == 0, f"rc={r.returncode} {r.stderr[-200:]}")
check("G4 nhưng phải CẢNH BÁO ra stdout, không im lặng",
      "KHÔNG gộp tầng này" in r.stdout, r.stdout[-200:])

# G5 — khối đề xuất tồn tại nhưng 0 lệnh ⇒ không có gì để gộp ⇒ không chặn oan.
root = make_tree()
write_plan(root, "SpaceX", "2026-08-11",
           base_plan(jit_unpark_proposal={"decision": "NO_JIT", "orders": []}))
check("G5 khối đề xuất rỗng ⇒ không chặn oan", run(root, "SpaceX", "2026-08-11").returncode == 0)

# G6 — plan không có khối đề xuất nào (plan chỉ mua) ⇒ không chặn oan.
root = make_tree()
write_plan(root, "SpaceX", "2026-08-11", base_plan(orders=[dict(BUY)]))
check("G6 plan không có đề xuất bán PARK ⇒ không chặn oan",
      run(root, "SpaceX", "2026-08-11").returncode == 0)

# G7 — cổng bắt CẢ tầng L1, không chỉ L2 (park_trim cũng là đề xuất bán PARK).
root = make_tree()
pp = write_plan(root, "SpaceX", "2026-08-11",
                base_plan(park_trim_proposal={"decision": "TRIM", "orders": JIT_ORDERS}))
r = run(root, "SpaceX", "2026-08-11")
check("G7 L1 park_trim chưa gộp cũng bị chặn (không chỉ L2)", r.returncode != 0,
      f"rc={r.returncode}")
check("G7 KHÔNG ghi approved_by", json.loads(pp.read_text()).get("approved_by") is None)

# G8 — DRY_RUN=1: qua cổng nhưng KHÔNG được ghi chữ ký.
root = make_tree()
pp = write_plan(root, "SpaceX", "2026-08-11",
                base_plan(merged=True,
                          jit_unpark_proposal={"decision": "JIT", "orders": JIT_ORDERS,
                                              "_merged_into_orders": "✅ ĐÃ MERGE"}))
r = run(root, "SpaceX", "2026-08-11", dry=True)
check("G8 DRY_RUN=1 ⇒ exit 0 nhưng KHÔNG ghi approved_by",
      r.returncode == 0 and json.loads(pp.read_text()).get("approved_by") is None,
      f"rc={r.returncode} approved={json.loads(pp.read_text()).get('approved_by')}")
check("G8 DRY_RUN=1 ⇒ KHÔNG gọi bus/Discord", not (root / "calls.log").exists())

# G9 — plan ĐÃ duyệt ⇒ không ghi đè (kế thừa từ approve_plan_simple.sh, kiểm lại tại chỗ nối).
root = make_tree()
pp = write_plan(root, "SpaceX", "2026-08-11",
                base_plan(merged=True, approved_by="user (John) truoc do",
                          jit_unpark_proposal={"decision": "JIT", "orders": JIT_ORDERS,
                                              "_merged_into_orders": "✅ ĐÃ MERGE"}))
r = run(root, "SpaceX", "2026-08-11")
check("G9 plan đã có approved_by ⇒ từ chối ghi đè", r.returncode != 0
      and json.loads(pp.read_text()).get("approved_by") == "user (John) truoc do",
      f"rc={r.returncode}")

# G10 — HÌNH DẠNG THẬT của plan gộp bằng script one-off CŨ: khối mang dấu "✅ ĐÃ MERGE…"
#       nhưng KHÔNG có khoá `merge_park_orders`. Đo trên `plan_SpaceX_2026-08-07.json` thật
#       (`_merged_into_orders` = "✅ ĐÃ MERGE vào orders[] của plan này (p…", `merge_park_orders`
#       vắng mặt) — đúng plan của ngày bán trùng 1.200cp. Cổng PHẢI từ chối: dấu ✅ là quy ước
#       DÙNG CHUNG giữa hai writer, không chứng minh được cơ chế đã-verify nào đã chạy.
#       Ca này là lý do cổng bám vào `merge_park_orders.owner` chứ không bám vào dấu ✅.
root = make_tree()
pp = write_plan(root, "SpaceX", "2026-08-11",
                base_plan(jit_unpark_proposal={
                    "decision": "JIT", "orders": JIT_ORDERS,
                    "_merged_into_orders": "✅ ĐÃ MERGE vào orders[] của plan này (park_merge)"}))
r = run(root, "SpaceX", "2026-08-11")
check("G10 hình dạng THẬT 08-07 (dấu ✅ của script cũ, KHÔNG có `merge_park_orders`) ⇒ từ chối",
      r.returncode != 0 and json.loads(pp.read_text()).get("approved_by") is None,
      f"rc={r.returncode}")
check("G10 thông báo nói rõ vì sao dấu ✅ không đủ (tránh người đọc tưởng cổng hỏng)",
      "one-off" in r.stderr, r.stderr[-260:])

# ── G11-G14: bằng chứng phải là ARTIFACT TRÊN ĐĨA, không chỉ khối nhúng trong plan ──────
# quant-skeptic 2026-08-11 (killer objection, đã dựng ca chạy thật): `compute_park_trim.py` /
# `compute_jit_unpark.py` chỉ ghi ra FILE, KHÔNG ghi khối `*_proposal` vào plan — trong chuỗi
# cron đề xuất thì khối đó do chính merge ghi. Nên "plan chưa merge lần nào" = plan KHÔNG có
# khối VÀ KHÔNG có dấu ⇒ cổng bản trước CHO QUA đúng ca cần chặn.
print("\n[G1x] Bằng chứng từ artifact trên đĩa (không chỉ khối trong plan)")


def put_artifact(root, name, orders):
    p = root / "data" / "trade_plans" / name
    p.write_text(json.dumps({"decision": "TRIM", "orders": orders}), encoding="utf-8")


# G11 — ĐÚNG hình dạng reviewer dựng: plan chỉ có lệnh mua, KHÔNG khối, KHÔNG dấu, nhưng
#       artifact L1 CÓ trên đĩa ⇒ merge chưa chạy ⇒ phải TỪ CHỐI.
root = make_tree()
pp = write_plan(root, "SpaceX", "2026-08-11", base_plan(orders=[dict(BUY)]))
put_artifact(root, "park_trim_SpaceX_2026-08-11.json", JIT_ORDERS)
r = run(root, "SpaceX", "2026-08-11")
check("G11 artifact L1 có trên đĩa + plan không khối/không dấu ⇒ TỪ CHỐI (merge bị bỏ qua)",
      r.returncode != 0 and json.loads(pp.read_text()).get("approved_by") is None,
      f"rc={r.returncode}")

# G12 — cùng thế nhưng artifact L2.
root = make_tree()
write_plan(root, "SpaceX", "2026-08-11", base_plan(orders=[dict(BUY)]))
put_artifact(root, "jit_unpark_SpaceX_2026-08-11.json", JIT_ORDERS)
check("G12 artifact L2 trên đĩa cũng bị bắt (không chỉ L1)",
      run(root, "SpaceX", "2026-08-11").returncode != 0)

# G13 — artifact trên đĩa NHƯNG plan đã mang dấu chạy ⇒ merge đã chạy ⇒ cho qua.
#       Không có ca này thì G11/G12 có thể được thoả bằng cách chặn mọi plan có artifact.
root = make_tree()
pp = write_plan(root, "SpaceX", "2026-08-11", base_plan(merged=True))
put_artifact(root, "park_trim_SpaceX_2026-08-11.json", JIT_ORDERS)
r = run(root, "SpaceX", "2026-08-11")
check("G13 artifact trên đĩa + plan ĐÃ có dấu chạy ⇒ vẫn duyệt được (không chặn oan)",
      r.returncode == 0 and json.loads(pp.read_text()).get("approved_by") == "user (test)",
      f"rc={r.returncode} {r.stderr[-160:]}")

# G14 — artifact trên đĩa nhưng 0 lệnh (L1 chạy, kết luận không trim) ⇒ không có gì để gộp.
root = make_tree()
write_plan(root, "SpaceX", "2026-08-11", base_plan(orders=[dict(BUY)]))
put_artifact(root, "park_trim_SpaceX_2026-08-11.json", [])
check("G14 artifact trên đĩa nhưng 0 lệnh ⇒ không chặn oan",
      run(root, "SpaceX", "2026-08-11").returncode == 0)

# ── G15-G16: `approve_plan_simple.sh` không được chặn oan ca S3 (lệnh merge + lệnh ngoài
#    miền cùng mã). Cùng lớp báo động giả với MERGE_STALE_SRC, ở tầng duyệt.
print("\n[G15] Cổng trùng-ticker của approve_plan_simple.sh — thu hẹp theo miền")

FOREIGN_SELL = {"id": "SELL-LAG-VHM-01", "ticker": "VHM", "side": "sell", "qty": 200,
                "ref_price": 76500.0, "priority": 0, "book": "LAG", "play_type": "LAG_EXIT",
                "estimated_proceeds_vnd": 15_300_000, "fee_est_vnd": 11_475}
root = make_tree()
pp = write_plan(root, "SpaceX", "2026-08-11",
                base_plan(merged=True, orders=[dict(SELL), dict(FOREIGN_SELL), dict(BUY)]))
r = run(root, "SpaceX", "2026-08-11")
check("G15 lệnh merge + lệnh bán NGOÀI miền cùng mã ⇒ vẫn duyệt được (ca S3 hợp lệ)",
      r.returncode == 0 and json.loads(pp.read_text()).get("approved_by") == "user (test)",
      f"rc={r.returncode} {r.stderr[-200:]}")

# G16 — chứng minh ngược: HAI lệnh cùng thuộc miền merge ⇒ vẫn phải chặn (merge 2 lần).
root = make_tree()
pp = write_plan(root, "SpaceX", "2026-08-11",
                base_plan(merged=True,
                          orders=[dict(SELL),
                                  dict(SELL, id="SELL-JIT-PARK-VHM-01", qty=100,
                                       merge_owner=None, play_type="JIT_UNPARK"),
                                  dict(BUY)]))
r = run(root, "SpaceX", "2026-08-11")
check("G16 chứng minh ngược: 2 lệnh CÙNG thuộc miền merge ⇒ VẪN chặn (dấu hiệu merge 2 lần)",
      r.returncode != 0 and json.loads(pp.read_text()).get("approved_by") is None,
      f"rc={r.returncode}")

print("\n" + "=" * 70)
if FAILS:
    print(f"FAIL — {len(FAILS)} ca hỏng:")
    for f in FAILS:
        print(f"  · {f}")
    sys.exit(1)
print("PASS — toàn bộ selfcheck approve_plan_with_jit")
