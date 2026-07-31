#!/usr/bin/env python3
"""Self-check cho fix "CAPIT nhân capit_size hai lần" (job Taylor_20260731_155814).

Sự cố gốc (finding Taylor_20260731_154624): plan SpaceX 2026-07-21 lấy `weight_pct`=15,0 của
dòng CAPIT trong CSV recommendations — con số ĐÃ = capit_size/n_basket — rồi nhân nó lên
`capit_total_target_vnd` (vốn ĐÃ = NAV_book_LAG × capit_size) ⇒ hiệu lực capit_size².
Deploy 254,4tr thay vì 348,4tr: thiếu 93,9tr, trong đó 87,1tr do nhân đôi và 6,8tr do làm
tròn lô. Cùng ngày, cùng CSV, plan ZaloPay chia đúng /n ⇒ lỗi ĐỌC CỘT ĐA NGHĨA.

Fix kiểm ở đây:
  (A) producer `golive_recommend_v23.py` publish sẵn VND/slot (`status.capit_slot_targets`)
      — số học đúng, đã gồm capit_size ĐÚNG MỘT LẦN;
  (B) CSV thêm cột `weight_base` nói rõ mẫu số từng book (và không phá BQ pusher);
  (C) consumer `send_plan_report.sh` đối chiếu Σ lệnh CAPIT vs mục tiêu, WARN trước khi duyệt.

Chạy: /home/trido/thanhdt/wc_venv/bin/python <file này>
"""
import ast
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

WC = "/home/trido/thanhdt/WorkingClaude"
GOLIVE = os.path.join(WC, "deploy_golive_dt5g_v4", "golive_recommend_v23.py")
SENDER = os.path.join(WC, "mike", "bin", "send_plan_report.sh")

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + (f"  [{detail}]" if detail else ""))


# ── T1. Tái lập số thật 07-21: chứng minh chẩn đoán "nhân capit_size hai lần" ─────────────
print("\n[T1] Tái lập sự cố 07-21 từ plan thật trên đĩa")
p_sx = json.load(open(os.path.join(WC, "data", "trade_plans", "plan_SpaceX_2026-07-21.json")))
ca = p_sx["capit_allocation"]
n_slots = ca["capit_slots"]
correct_slot = ca["capit_total_target_vnd"] / n_slots
plan_slot = ca["capit_per_slot_target_vnd"]
check("SpaceX 07-21: per-slot thực tế = per-slot đúng × capit_size (thừa đúng 1 lần capit_size)",
      abs(plan_slot - correct_slot * ca["capit_size"]) < 1.0,
      f"plan {plan_slot:,.0f} vs đúng {correct_slot:,.0f} × {ca['capit_size']}")
check("SpaceX 07-21: thiếu do nhân đôi ≈ 87,1tr (KHÔNG phải làm tròn lô)",
      abs((correct_slot - plan_slot) * n_slots - 87_091_046) < 1_000,
      f"{(correct_slot - plan_slot) * n_slots:,.0f} VND")

p_zp = json.load(open(os.path.join(WC, "data", "trade_plans", "plan_ZaloPay_2026-07-21.json")))
zp_txt = json.dumps(p_zp, ensure_ascii=False)
check("ZaloPay 07-21 (đối chứng): cùng CSV, chia đúng /n ⇒ lỗi là đọc cột, không phải số học",
      "175997313" in zp_txt.replace(",", "") or "35199463" in zp_txt.replace(",", ""),
      "target 175.997.313 / slot 35.199.463 xuất hiện trong plan")

# ── T2. Số học của producer — exec ĐÚNG khối code thật trong golive_recommend_v23.py ──────
print("\n[T2] Số học capit_slot_targets — trích khối code THẬT bằng AST, không chép lại")
src = open(GOLIVE, encoding="utf-8").read()
tree = ast.parse(src)
block = None
for node in ast.walk(tree):
    if (isinstance(node, ast.For) and isinstance(node.target, ast.Name)
            and node.target.id == "_a"
            and "capit_shares" in ast.dump(node.iter)):
        block = node
        break
check("tìm thấy khối tính capit_targets trong golive_recommend_v23.py", block is not None)

if block is not None:
    ns = {  # đúng số thật SpaceX/ZaloPay ngày 07-20 (nguồn: 2 plan file 07-21)
        "capit_shares": {"SpaceX": 0.66, "ZaloPay": 0.34, "NoNav": 0.0},
        "capit_share_detail": {
            "SpaceX": {"nav": 928971136.0, "source": "active_nav @2026-07-20"},
            "ZaloPay": {"nav": 469326169.0, "source": "active_nav @2026-07-20"},
            "NoNav": {"nav": None, "source": "unavailable"},
        },
        "w_tgt": 0.5, "capit_size": 0.75, "basket": ["NCT", "PVT", "SAB", "SIP", "VNM"],
        "capit_targets": {},
    }
    exec(compile(ast.Module(body=[block], type_ignores=[]), "<capit_targets>", "exec"), ns)
    tg = ns["capit_targets"]
    check("SpaceX: slot = 69.672.835đ (= 928.971.136 × 0,5 × 0,75 / 5) — capit_size ĐÚNG 1 lần",
          tg["SpaceX"]["capit_slot_target_vnd"] == 69_672_835,
          f"{tg['SpaceX']['capit_slot_target_vnd']:,}")
    check("SpaceX: tổng = 348.364.176đ, khớp capit_total_target_vnd plan thật đã ghi",
          tg["SpaceX"]["capit_total_target_vnd"] == ca["capit_total_target_vnd"],
          f"{tg['SpaceX']['capit_total_target_vnd']:,}")
    check("ZaloPay: tổng = 175.997.313đ, khớp con số plan ZaloPay THẬT đã deploy đúng",
          tg["ZaloPay"]["capit_total_target_vnd"] == 175_997_313,
          f"{tg['ZaloPay']['capit_total_target_vnd']:,}")
    check("ZaloPay: slot = 35.199.463đ, khớp per_ticker plan thật",
          tg["ZaloPay"]["capit_slot_target_vnd"] == 35_199_463)
    check("KHÔNG bao giờ bằng con số sai 52.254.626 (bẫy capit_size²)",
          tg["SpaceX"]["capit_slot_target_vnd"] != 52_254_626)
    check("account thiếu NAV → ghi error, KHÔNG bịa số (fail-safe)",
          tg.get("NoNav", {}).get("capit_slot_target_vnd") is None
          and tg.get("NoNav", {}).get("error"),
          str(tg.get("NoNav")))
    # bất biến: nhân weight_pct (=capit_size/n×100) lên tổng đúng là ra ĐÚNG con số sai lịch sử
    wp = ca["capit_slot_weight_pct"] / 100.0
    check("bất biến chẩn đoán: tổng_đúng × weight_pct = 52.254.626 (con số plan sai đã dùng)",
          round(tg["SpaceX"]["capit_total_target_vnd"] * wp) == 52_254_626)

# ── T3. CSV weight_base — có mặt, đúng nghĩa, và KHÔNG phá BQ pusher ──────────────────────
print("\n[T3] Cột weight_base trong CSV + tương thích BQ pusher")
check("rec_df khai báo cột weight_base", '"weight_pct","weight_base","status"' in src)
check("dòng CAPIT gắn nhãn cảnh báo không-nhân-lại",
      "NAV_book_LAG__DA_GOM_capit_size__KHONG_NHAN_LAI" in src)
for book, base in [("BAL", "BAL_book"), ("LAG", "LAG_book"), ("PARK", "parking_basket")]:
    check(f"book {book} có weight_base={base}", f'"weight_base": "{base}"' in src)
check("nhãn SAI 'size × free cash' đã bị xoá khỏi MD", "size × free cash" not in src)

pusher = os.path.join(WC, "mike", "agents", "Mafee", "push_recommend_v23_to_bq.py")
psrc = open(pusher, encoding="utf-8").read()
check("BQ pusher: weight_base KHÔNG nằm trong known_csv ⇒ tự vào cột `extra`, không đổi schema",
      "weight_base" not in psrc.split("known_csv")[1].split("}")[0])

with tempfile.TemporaryDirectory() as td:
    cp = os.path.join(td, "c.csv")
    with open(cp, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["book", "ticker", "play_type", "ta",
                    "close_bq_stale_DO_NOT_USE_AS_REFPRICE", "sector", "weight_pct",
                    "weight_base", "status"])
        w.writerow(["CAPIT", "VNM", "CAPIT_GOLDEN", "", "", "3.0", "15.0",
                    "NAV_book_LAG__DA_GOM_capit_size__KHONG_NHAN_LAI", "WASHOUT"])
    rows = []
    with open(cp, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            known = {"book", "ticker", "play_type", "ta", "close", "sector", "weight_pct",
                     "status", "close_bq_stale_DO_NOT_USE_AS_REFPRICE"}
            rows.append({k: v for k, v in r.items() if k not in known and v not in (None, "")})
    check("CSV có weight_base parse được, rơi vào extra (mô phỏng đúng logic pusher)",
          rows and rows[0].get("weight_base"), str(rows[0] if rows else None))

# ── T4. Consumer: send_plan_report.sh đối chiếu Σ CAPIT vs mục tiêu ───────────────────────
print("\n[T4] send_plan_report.sh — đối chiếu cỡ deploy CAPIT (dry-run, sandbox)")
EXPECTED = subprocess.run(
    [sys.executable, "-c", "import datetime as dt;from trading_bot.vn_market import "
     "next_trading_day;print(next_trading_day(dt.date.today()))"],
    cwd=WC, capture_output=True, text=True).stdout.strip()


def run_sender(plan, status, account):
    """Chạy script THẬT trong sandbox; trả stdout."""
    td = tempfile.mkdtemp()
    try:
        for sub in ("data/trade_plans", "data/execution_logs", "trading_bot", "state"):
            os.makedirs(os.path.join(td, sub), exist_ok=True)
        # trading_bot cần import được (next_trading_day) → symlink cây thật
        os.rmdir(os.path.join(td, "trading_bot"))
        os.symlink(os.path.join(WC, "trading_bot"), os.path.join(td, "trading_bot"))
        plan = dict(plan, plan_date=EXPECTED)
        json.dump(plan, open(os.path.join(
            td, "data", "trade_plans", f"plan_{account}_{EXPECTED}.json"), "w"), ensure_ascii=False)
        json.dump(status, open(os.path.join(td, "data", "golive_v23_status.json"), "w"),
                  ensure_ascii=False)
        env = dict(os.environ, SEND_PLAN_WORKDIR_OVERRIDE=td,
                   SEND_PLAN_MARKER_DIR=os.path.join(td, "state", "marker"))
        r = subprocess.run(["bash", SENDER, "--account", account, "--dry-run"],
                           capture_output=True, text=True, env=env, timeout=300)
        return r.stdout + r.stderr
    finally:
        shutil.rmtree(td, ignore_errors=True)


def status_with(slot, account):
    return {"date": EXPECTED, "capit_signal_today": True, "capit_size": 0.75,
            "capit_slot_targets": ({account: {"capit_slot_target_vnd": slot, "n_slots": 5}}
                                   if slot else {})}


# T4a — plan SAI như thật 07-21 (52,25tr/slot) vs mục tiêu đúng 69,67tr ⇒ phải WARN
out = run_sender(p_sx, status_with(69_672_835, "SpaceX"), "SpaceX")
check("plan SAI (đúng cỡ deploy 07-21) → CẢNH BÁO lệch", "⚠️ CAPIT" in out and "lệch -" in out,
      [l.strip() for l in out.splitlines() if "CAPIT:" in l][:1])
check("cảnh báo nêu đúng nghi vấn nhân capit_size hai lần", "capit_size hai lần" in out)

# T4b — cùng plan đó nhưng mục tiêu = đúng cái nó đã dùng ⇒ KHÔNG WARN (không báo động giả)
out_ok = run_sender(p_sx, status_with(52_254_626, "SpaceX"), "SpaceX")
check("plan khớp mục tiêu → KHÔNG cảnh báo (không báo động giả)",
      "✅ CAPIT" in out_ok and "⚠️ CAPIT" not in out_ok,
      [l.strip() for l in out_ok.splitlines() if "CAPIT:" in l][:1])

# T4c — status chưa publish targets ⇒ nói rõ không đối chiếu được, KHÔNG chặn plan
out_no = run_sender(p_sx, status_with(None, "SpaceX"), "SpaceX")
check("thiếu capit_slot_targets → báo rõ 'không đối chiếu được', vẫn render plan",
      "chưa publish" in out_no and "Kế hoạch giao dịch ngày mai" in out_no)

# T4d — plan không có lệnh CAPIT ⇒ im lặng hoàn toàn
p_nocapit = dict(p_sx, orders=[dict(o, book="BAL") for o in p_sx["orders"]])
out_nc = run_sender(p_nocapit, status_with(69_672_835, "SpaceX"), "SpaceX")
check("plan không có lệnh CAPIT → không thêm dòng nào", "CAPIT:" not in out_nc)

print(f"\n{'=' * 70}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    for f in FAIL:
        print(f"  ✗ {f}")
sys.exit(1 if FAIL else 0)
