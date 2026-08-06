#!/usr/bin/env python3
"""Self-check: send_plan_report.sh PHẢI hiện rõ park_trim_proposal (L1) + jit_unpark_proposal (L2).

Lỗ hổng gốc (lặp 2 lần, user John chốt sửa 2026-08-06, job Taylor_20260806_155733):
cả 2 cơ chế đã LIVE và sinh lệnh BÁN thật / quyết định cỡ lệnh MUA thật, nhưng report duyệt
plan KHÔNG hề nhắc tới:
  - 08-05: park_trim_proposal (TRIM) bị giấu ⇒ user không biết có lệnh trim để mà duyệt;
  - 08-07: plan SpaceX hiện "MUA SSI 3100cp = 75,33tr" trong khi cash chỉ 4,82tr ⇒ đọc riêng
    lệnh mua thì tưởng DollarBill mua liều, trong khi thực tế jit_unpark bán 12 mã PARK bù đủ
    (status=FUNDED_BY_JIT, khớp NGUYÊN lệnh).

Chạy script THẬT trong sandbox (SEND_PLAN_WORKDIR_OVERRIDE + SEND_PLAN_MARKER_DIR + --dry-run,
cùng harness đã dùng ở job Taylor_20260731_155814) — không gửi Telegram/Discord, không ghi
marker thật.

Chạy: python3 mike/bin/send_plan_report_park_jit_selfcheck.py
Theo skill verify-before-done: T9 chạy lại T1 dưới `env -u TZ` + TZ ngoại lai để lộ phụ thuộc
môi trường (bẫy §16 — selfcheck thừa hưởng TZ đúng của tác giả thì luôn PASS).
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

WC = "/home/trido/thanhdt/WorkingClaude"
SENDER = os.path.join(WC, "mike", "bin", "send_plan_report.sh")
REAL_PLANS = os.path.join(WC, "data", "trade_plans")

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + (f"  [{detail}]" if detail else ""))


def expected_date(env=None):
    r = subprocess.run(
        [sys.executable, "-c", "import datetime as dt;from trading_bot.vn_market import "
         "next_trading_day;print(next_trading_day(dt.date.today()))"],
        cwd=WC, capture_output=True, text=True, env=env)
    return r.stdout.strip()


def run_sender(plan, account, env_extra=None):
    """Chạy send_plan_report.sh THẬT trong sandbox; trả stdout+stderr."""
    td = tempfile.mkdtemp()
    try:
        for sub in ("data/trade_plans", "state"):
            os.makedirs(os.path.join(td, sub), exist_ok=True)
        os.symlink(os.path.join(WC, "trading_bot"), os.path.join(td, "trading_bot"))
        env = dict(os.environ, SEND_PLAN_WORKDIR_OVERRIDE=td,
                   SEND_PLAN_MARKER_DIR=os.path.join(td, "state", "marker"))
        for k, v in (env_extra or {}).items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = v
        exp = expected_date(env)
        plan = dict(plan, plan_date=exp)
        with open(os.path.join(td, "data", "trade_plans",
                               f"plan_{account}_{exp}.json"), "w", encoding="utf-8") as fh:
            json.dump(plan, fh, ensure_ascii=False)
        r = subprocess.run(["bash", SENDER, "--account", account, "--dry-run"],
                           capture_output=True, text=True, env=env, timeout=600)
        return r.stdout + r.stderr
    finally:
        shutil.rmtree(td, ignore_errors=True)


def load_real(account, date="2026-08-07"):
    with open(os.path.join(REAL_PLANS, f"plan_{account}_{date}.json"), encoding="utf-8") as fh:
        return json.load(fh)


SX = load_real("SpaceX")
ZP = load_real("ZaloPay")

# ── T1. Plan THẬT 2026-08-07, cả 2 account: đủ 4 mục ─────────────────────────────────────
print("\n[T1] Plan thật 2026-08-07 — 4 mục bắt buộc (orders / funding note / L1 / L2)")
out_sx = run_sender(SX, "SpaceX")
check("SpaceX: lệnh mua chính vẫn hiện", "MUA SSI 3100cp" in out_sx)
check("SpaceX: funding note NGAY CẠNH lệnh mua, nói rõ bán N mã PARK tổng X",
      "Tiền đâu ra:" in out_sx and "bán 12 mã PARK tổng 71.7tr" in out_sx,
      [l.strip()[:110] for l in out_sx.splitlines() if "Tiền đâu ra" in l][:1])
check("SpaceX: funding note nói mua NGUYÊN lệnh (không để user tưởng thiếu tiền)",
      "mua NGUYÊN lệnh 3100cp" in out_sx)
check("SpaceX: có mục RIÊNG L1 park_trim + số mã + Σ tiền + mục tiêu trần PARK",
      "ĐỀ XUẤT TRIM PARK (L1) — 13 lệnh BÁN, Σ 92.8tr" in out_sx
      and "đưa PARK về trần 80% của pool" in out_sx,
      [l.strip()[:110] for l in out_sx.splitlines() if "TRIM PARK (L1)" in l][:1])
check("SpaceX: L1 nói rõ CẦN DUYỆT RIÊNG + không nằm trong lệnh chính",
      "CẦN DUYỆT RIÊNG" in out_sx and "KHÔNG nằm trong danh sách lệnh chính" in out_sx)
check("SpaceX: có mục RIÊNG L2 jit_unpark + liệt kê mã bán + amendment",
      "ĐỀ XUẤT BÁN PARK TÀI TRỢ LỆNH MUA (L2/JIT) — 12 lệnh BÁN, Σ 71.7tr" in out_sx
      and "MUA SSI: FUNDED_BY_JIT" in out_sx)
check("SpaceX: heading tổng nêu có thêm 25 lệnh bán PARK ngoài orders[]",
      "25 lệnh BÁN PARK đề xuất" in out_sx)
check("SpaceX: mã bị chặn trim (SHS/VND) vẫn hiện, không im lặng",
      "SHS" in out_sx and "VND" in out_sx and "Không trim được" in out_sx)

out_zp = run_sender(ZP, "ZaloPay")
check("ZaloPay: funding note đúng số (3 mã PARK, 16,0tr)",
      "bán 3 mã PARK tổng 16.0tr" in out_zp and "mua NGUYÊN lệnh 800cp" in out_zp,
      [l.strip()[:110] for l in out_zp.splitlines() if "Tiền đâu ra" in l][:1])
check("ZaloPay: L1 (8 lệnh, 36.1tr) + L2 (3 lệnh, 16.0tr) đều có mục riêng",
      "TRIM PARK (L1) — 8 lệnh BÁN, Σ 36.1tr" in out_zp
      and "(L2/JIT) — 3 lệnh BÁN, Σ 16.0tr" in out_zp)
check("ZaloPay: value_vnd KHÔNG có trong proposal orders → fallback qty×ref_price ra số đúng",
      "VHM 100cp (7.7tr)" in out_zp)

# ── T2/T3. decision BLOCKED_* phải hiện rõ kèm lý do ─────────────────────────────────────
print("\n[T2/T3] decision BLOCKED_* — hiện rõ, kèm lý do, KHÔNG im lặng")
p = copy.deepcopy(SX)
p["park_trim_proposal"] = {"decision": "BLOCKED_RECONCILE", "orders": [],
                           "notes": ["sổ lô LỆCH so với broker ⇒ không sinh đề xuất nào"]}
out = run_sender(p, "SpaceX")
check("L1 BLOCKED_RECONCILE hiện rõ + lý do",
      "TRIM PARK (L1) BỊ CHẶN — BLOCKED_RECONCILE" in out and "sổ lô LỆCH" in out,
      [l.strip()[:110] for l in out.splitlines() if "BỊ CHẶN" in l][:1])

p = copy.deepcopy(SX)
p["jit_unpark_proposal"] = {"decision": "BLOCKED_DAYCAP", "orders": [], "buy_amendments": [],
                            "notes": ["không đo được trần thanh khoản rổ ⇒ fail-closed"]}
out = run_sender(p, "SpaceX")
check("L2 BLOCKED_DAYCAP hiện rõ + cảnh báo lệnh mua có thể thiếu tiền",
      "(L2/JIT) BỊ CHẶN — BLOCKED_DAYCAP" in out and "trần thanh khoản" in out
      and "THIẾU TIỀN" in out,
      [l.strip()[:110] for l in out.splitlines() if "BỊ CHẶN" in l][:1])

# ── T4/T5. status SHRINK / DROP phải nói rõ lệnh bị co / bị bỏ ───────────────────────────
print("\n[T4/T5] buy_amendments status SHRINK / DROP")
p = copy.deepcopy(SX)
a = p["jit_unpark_proposal"]["buy_amendments"][0]
a.update({"status": "SHRINK", "qty_final": 1200, "target_value_final_vnd": 29160000.0,
          "reason": "bán PARK không đủ bù, co còn 1200cp theo sức mua"})
out = run_sender(p, "SpaceX")
check("SHRINK: nói rõ lệnh bị CO từ qty_plan → qty_final + lý do",
      "Lệnh bị CO** 3100cp → 1200cp" in out and "co còn 1200cp" in out,
      [l.strip()[:110] for l in out.splitlines() if "bị CO" in l][:1])

p = copy.deepcopy(SX)
a = p["jit_unpark_proposal"]["buy_amendments"][0]
a.update({"status": "DROP", "qty_final": 0, "target_value_final_vnd": 0.0,
          "reason": "sức mua sau bán PARK < 1 lô"})
out = run_sender(p, "SpaceX")
check("DROP: nói rõ lệnh bị BỎ dù đã cố bán PARK + lý do",
      "Lệnh bị BỎ**" in out and "sức mua sau bán PARK < 1 lô" in out,
      [l.strip()[:110] for l in out.splitlines() if "bị BỎ" in l][:1])

# ── T6. TRIM khi orders[] RỖNG (đúng ca 08-05: HOLD nhưng vẫn có lệnh trim cần duyệt) ────
print("\n[T6] orders[] rỗng + park_trim TRIM (ca 08-05) — mục L1 vẫn phải hiện")
p = copy.deepcopy(SX)
p["orders"] = []
p.pop("jit_unpark_proposal", None)
out = run_sender(p, "SpaceX")
check("HOLD 0 lệnh nhưng vẫn hiện mục TRIM PARK (L1) — đúng lỗ hổng 08-05",
      "GIỮ NGUYÊN (HOLD)" in out and "ĐỀ XUẤT TRIM PARK (L1) — 13 lệnh BÁN" in out)

# ── T7. Tương thích ngược: plan KHÔNG có 2 field này → không thêm dòng nào ───────────────
print("\n[T7] Plan cũ không có park_trim/jit_unpark — không đổi hành vi")
p = copy.deepcopy(SX)
p.pop("park_trim_proposal", None)
p.pop("jit_unpark_proposal", None)
out = run_sender(p, "SpaceX")
check("không có 2 field → KHÔNG in mục L1/L2 nào, report vẫn render bình thường",
      "TRIM PARK" not in out and "L2/JIT" not in out and "Tiền đâu ra" not in out
      and "MUA SSI 3100cp" in out)

# ── T8. Artifact méo mó → fail-open, KHÔNG crash report (render_crashed = mất plan) ──────
print("\n[T8] Artifact méo mó (kiểu sai) → fail-open, không crash")
p = copy.deepcopy(SX)
p["park_trim_proposal"] = "TRIM"                       # str thay vì dict
p["jit_unpark_proposal"] = {"decision": "JIT", "orders": "xxx", "buy_amendments": None}
out = run_sender(p, "SpaceX")
check("kiểu sai → vẫn render plan đầy đủ, không ESCALATE render_crashed",
      "Kế hoạch giao dịch ngày mai" in out and "MUA SSI 3100cp" in out
      and "render_crashed" not in out)

# ── T9. Phụ thuộc môi trường: chạy lại T1 dưới env -u TZ và TZ ngoại lai ─────────────────
print("\n[T9] verify-before-done — chạy lại dưới `env -u TZ` và TZ=America/New_York")
for label, extra in (("env -u TZ", {"TZ": None}),
                     ("TZ=America/New_York", {"TZ": "America/New_York"})):
    o = run_sender(SX, "SpaceX", env_extra=extra)
    check(f"{label}: 4 mục vẫn đủ (khối L1/L2 không phụ thuộc TZ)",
          "bán 12 mã PARK tổng 71.7tr" in o
          and "ĐỀ XUẤT TRIM PARK (L1) — 13 lệnh BÁN" in o
          and "(L2/JIT) — 12 lệnh BÁN" in o
          and "MUA SSI 3100cp" in o)

print(f"\n{'=' * 72}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
for f in FAIL:
    print(f"  ✗ {f}")
sys.exit(1 if FAIL else 0)
