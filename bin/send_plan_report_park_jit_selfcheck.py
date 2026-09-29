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

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import wc_paths  # noqa: E402

# `WC` cứng canonical trước đây làm `SENDER` LUÔN trỏ `send_plan_report.sh` của checkout
# CANONICAL: chạy selfcheck này từ worktree vẫn test script MASTER, PASS không chứng minh gì về
# bản đang sửa (lớp lỗi đã vá ở `compute_active_nav_selfcheck.py`, 833abcc5).
# SENDER = sibling theo VỊ TRÍ FILE ⇒ đổi theo worktree. `WC` (cây WorkingClaude: `data/trade_plans`
# đọc thật + `trading_bot` symlink vào sandbox — không nhân bản theo worktree của repo `mike`) tra
# qua marker `wc_paths.find_wc_root`.
WC = wc_paths.find_wc_root(__file__)
SENDER = os.path.join(HERE, "send_plan_report.sh")
REAL_PLANS = os.path.join(WC, "data", "trade_plans")

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + (f"  [{detail}]" if detail else ""))


def expected_date(env=None):
    # Always compute in ICT regardless of TZ env — matches sender's anchored ICT date (§16).
    r = subprocess.run(
        [sys.executable, "-c",
         "import datetime as dt; from zoneinfo import ZoneInfo; "
         "from trading_bot.vn_market import next_trading_day; "
         "print(next_trading_day(dt.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()))"],
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


def _unmerge(plan):
    """Strip _merged_into_orders from proposals so tests see the 'not-yet-merged' state.
    Real plans on disk may have _merged_into_orders set (already processed), which correctly
    suppresses L1/L2 in the renderer. Tests verify rendering of proposals — they need the
    pre-merge state regardless of when the plan file was last saved."""
    p = copy.deepcopy(plan)
    for key in ("park_trim_proposal", "jit_unpark_proposal"):
        if isinstance(p.get(key), dict):
            p[key].pop("_merged_into_orders", None)
    return p


SX = _unmerge(load_real("SpaceX"))
ZP = _unmerge(load_real("ZaloPay"))


# ── Kỳ vọng SUY TỪ ARTIFACT, không ghim số (sửa 2026-08-14, job Taylor_20260814_080528) ──
# Bản cũ ghim chuỗi "12 lệnh BÁN, Σ 71.7tr" / "3 mã PARK tổng 16.0tr"… đo tại một vintage của
# `data/trade_plans/plan_*_2026-08-07.json`. Hai file đó KHÔNG nằm trong git (`.gitignore:12
# *.json`) và bị ghi đè khi re-plan — bản trên đĩa hiện là 11 lệnh/42.0tr, nên 14 ca đỏ dù
# renderer hoàn toàn đúng. Đây đúng ca §23 hệ luận 1 cảnh báo: "đọc thẳng file production
# (data/trade_plans/…) làm assertion ⇒ test tự vô hiệu theo thời gian".
#
# BẤT BIẾN THẬT mà bộ này sinh ra để bảo vệ KHÔNG phải "đúng 12 lệnh" — mà là "report KHÔNG
# ĐƯỢC GIẤU/NÓI SAI đề xuất nằm trong plan" (lỗ hổng 08-05 giấu L1, 08-07 giấu L2). Vì vậy
# kỳ vọng giờ TÍNH TỪ chính artifact rồi đối chiếu với TEXT đã render: artifact đổi bao nhiêu
# lần cũng không sao, giấu một lệnh là đỏ ngay.
def _prop(plan, key):
    """(n_lệnh, Σ tiền) của một proposal — theo ĐÚNG quy ước renderer: `value_vnd`, thiếu thì
    fallback qty × ref_price (chính ca ZaloPay đang phủ)."""
    pr = plan.get(key) or {}
    orders = pr.get("orders") or pr.get("sells") or []
    total = 0.0
    for o in orders:
        v = o.get("value_vnd")
        if v in (None, 0):
            v = (o.get("qty") or 0) * (o.get("ref_price") or o.get("limit_price_vnd") or 0)
        total += float(v or 0)
    return len(orders), total


def _tr(vnd):
    """Định dạng 'tr' y hệt renderer (1 chữ số thập phân) để so được bằng chuỗi."""
    return f"{vnd / 1e6:.1f}tr"


def _main_buy(plan):
    """(ticker, qty) của lệnh MUA chính trong plan — cũng suy từ artifact, vì rổ mã đổi theo
    ngày (bản cũ ghim 'SSI 3100cp'; artifact trên đĩa nay là DRI)."""
    b = next((o for o in plan.get("orders") or []
              if str(o.get("side", "")).lower() == "buy"), {})
    return b.get("ticker"), b.get("qty")


SX_L1_N, SX_L1_V = _prop(SX, "park_trim_proposal")
SX_L2_N, SX_L2_V = _prop(SX, "jit_unpark_proposal")
ZP_L1_N, ZP_L1_V = _prop(ZP, "park_trim_proposal")
ZP_L2_N, ZP_L2_V = _prop(ZP, "jit_unpark_proposal")
SX_TK, SX_QTY = _main_buy(SX)
ZP_TK, ZP_QTY = _main_buy(ZP)
print(f"  (kỳ vọng suy từ artifact — SpaceX L1 {SX_L1_N}/{_tr(SX_L1_V)} "
      f"L2 {SX_L2_N}/{_tr(SX_L2_V)} · ZaloPay L1 {ZP_L1_N}/{_tr(ZP_L1_V)} "
      f"L2 {ZP_L2_N}/{_tr(ZP_L2_V)})")

# ── T1. Plan THẬT 2026-08-07, cả 2 account: đủ 4 mục ─────────────────────────────────────
print("\n[T1] Plan thật 2026-08-07 — 4 mục bắt buộc (orders / funding note / L1 / L2)")
out_sx = run_sender(SX, "SpaceX")
check("SpaceX: lệnh mua chính vẫn hiện", f"MUA {SX_TK} {SX_QTY}cp" in out_sx,
      f"chờ MUA {SX_TK} {SX_QTY}cp")
check("SpaceX: funding note NGAY CẠNH lệnh mua, nói rõ bán N mã PARK tổng X",
      "Tiền đâu ra:" in out_sx
      and f"bán {SX_L2_N} mã PARK tổng {_tr(SX_L2_V)}" in out_sx,
      [l.strip()[:110] for l in out_sx.splitlines() if "Tiền đâu ra" in l][:1])
check("SpaceX: funding note nói mua NGUYÊN lệnh (không để user tưởng thiếu tiền)",
      f"mua NGUYÊN lệnh {SX_QTY}cp" in out_sx)
check("SpaceX: có mục RIÊNG L1 park_trim + số mã + Σ tiền + mục tiêu trần PARK",
      f"ĐỀ XUẤT TRIM PARK (L1) — {SX_L1_N} lệnh BÁN, Σ {_tr(SX_L1_V)}" in out_sx
      and "đưa PARK về trần 80% của pool" in out_sx,
      [l.strip()[:110] for l in out_sx.splitlines() if "TRIM PARK (L1)" in l][:1])
check("SpaceX: L1 nói rõ CẦN DUYỆT RIÊNG + không nằm trong lệnh chính",
      "CẦN DUYỆT RIÊNG" in out_sx and "KHÔNG nằm trong danh sách lệnh chính" in out_sx)
check("SpaceX: có mục RIÊNG L2 jit_unpark + liệt kê mã bán + amendment",
      f"ĐỀ XUẤT BÁN PARK TÀI TRỢ LỆNH MUA (L2/JIT) — {SX_L2_N} lệnh BÁN, "
      f"Σ {_tr(SX_L2_V)}" in out_sx
      and f"MUA {SX_TK}: FUNDED_BY_JIT" in out_sx)
check("SpaceX: heading tổng nêu có thêm N lệnh bán PARK ngoài orders[]",
      f"{SX_L1_N + SX_L2_N} lệnh BÁN PARK đề xuất" in out_sx,
      f"chờ {SX_L1_N + SX_L2_N} = L1 {SX_L1_N} + L2 {SX_L2_N}")
# Mã bị chặn trim phải HIỆN, không im lặng. Bản cũ dựa vào việc artifact 08-07 tình cờ có
# SHS/VND trong `blocked` — nay `blocked == []` nên ca đó không thể xanh và cũng không còn
# kiểm gì. Dựng ca TƯỜNG MINH: bơm blocked vào bản sao ⇒ luôn đi qua đúng nhánh render, độc
# lập với vintage artifact. Kèm ca chứng minh ngược (blocked rỗng ⇒ KHÔNG in dòng thừa).
_pb = copy.deepcopy(SX)
_pb["park_trim_proposal"]["blocked"] = [
    {"ticker": "SHS", "reason": "T+2 chưa về, không bán được"},
    {"ticker": "VND", "reason": "vượt trần %ADV phiên"}]
_out_pb = run_sender(_pb, "SpaceX")
check("SpaceX: mã bị chặn trim (SHS/VND) vẫn hiện, không im lặng",
      "Không trim được" in _out_pb and "SHS" in _out_pb and "VND" in _out_pb
      and "T+2 chưa về" in _out_pb,
      [l.strip()[:110] for l in _out_pb.splitlines() if "Không trim được" in l][:1])
check("SpaceX: CHỨNG MINH NGƯỢC — blocked rỗng ⇒ KHÔNG in dòng 'Không trim được'",
      "Không trim được" not in out_sx,
      f"blocked artifact = {len((SX.get('park_trim_proposal') or {}).get('blocked') or [])}")

out_zp = run_sender(ZP, "ZaloPay")
check(f"ZaloPay: funding note đúng số ({ZP_L2_N} mã PARK, {_tr(ZP_L2_V)})",
      f"bán {ZP_L2_N} mã PARK tổng {_tr(ZP_L2_V)}" in out_zp
      and f"mua NGUYÊN lệnh {ZP_QTY}cp" in out_zp,
      [l.strip()[:110] for l in out_zp.splitlines() if "Tiền đâu ra" in l][:1])
check(f"ZaloPay: L1 ({ZP_L1_N} lệnh, {_tr(ZP_L1_V)}) + L2 ({ZP_L2_N} lệnh, "
      f"{_tr(ZP_L2_V)}) đều có mục riêng",
      f"TRIM PARK (L1) — {ZP_L1_N} lệnh BÁN, Σ {_tr(ZP_L1_V)}" in out_zp
      and f"(L2/JIT) — {ZP_L2_N} lệnh BÁN, Σ {_tr(ZP_L2_V)}" in out_zp)
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
      f"Lệnh bị CO** {SX_QTY}cp → 1200cp" in out and "co còn 1200cp" in out,
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
      "GIỮ NGUYÊN (HOLD)" in out
      and f"ĐỀ XUẤT TRIM PARK (L1) — {SX_L1_N} lệnh BÁN" in out)

# ── T7. Tương thích ngược: plan KHÔNG có 2 field này → không thêm dòng nào ───────────────
print("\n[T7] Plan cũ không có park_trim/jit_unpark — không đổi hành vi")
p = copy.deepcopy(SX)
p.pop("park_trim_proposal", None)
p.pop("jit_unpark_proposal", None)
out = run_sender(p, "SpaceX")
check("không có 2 field → KHÔNG in mục L1/L2 nào, report vẫn render bình thường",
      "TRIM PARK" not in out and "L2/JIT" not in out and "Tiền đâu ra" not in out
      and f"MUA {SX_TK} {SX_QTY}cp" in out)

# ── T8. Artifact méo mó → fail-open, KHÔNG crash report (render_crashed = mất plan) ──────
print("\n[T8] Artifact méo mó (kiểu sai) → fail-open, không crash")
p = copy.deepcopy(SX)
p["park_trim_proposal"] = "TRIM"                       # str thay vì dict
p["jit_unpark_proposal"] = {"decision": "JIT", "orders": "xxx", "buy_amendments": None}
out = run_sender(p, "SpaceX")
check("kiểu sai → vẫn render plan đầy đủ, không ESCALATE render_crashed",
      "Kế hoạch giao dịch ngày mai" in out and f"MUA {SX_TK} {SX_QTY}cp" in out
      and "render_crashed" not in out)

# ── T9. Phụ thuộc môi trường: chạy lại T1 dưới env -u TZ và TZ ngoại lai ─────────────────
print("\n[T9] verify-before-done — chạy lại dưới `env -u TZ` và TZ=America/New_York")
for label, extra in (("env -u TZ", {"TZ": None}),
                     ("TZ=America/New_York", {"TZ": "America/New_York"})):
    o = run_sender(SX, "SpaceX", env_extra=extra)
    check(f"{label}: 4 mục vẫn đủ (khối L1/L2 không phụ thuộc TZ)",
          f"bán {SX_L2_N} mã PARK tổng {_tr(SX_L2_V)}" in o
          and f"ĐỀ XUẤT TRIM PARK (L1) — {SX_L1_N} lệnh BÁN" in o
          and f"(L2/JIT) — {SX_L2_N} lệnh BÁN" in o
          and f"MUA {SX_TK} {SX_QTY}cp" in o)

# ── T10 — "Lý do (áp dụng CHUNG...): tuân thủ trần PARK X%" phải ĐỘNG theo target_park,
# KHÔNG hardcode "80%". Bug gốc 2026-09-28: dòng per-order hardcode "80%" trong khi park
# target đã đổi 0.80→0.30. Sửa gốc: đọc target_park (98a9d633). Sửa kb/plan_report_style_
# guide.md §2 (2026-09-29): N lệnh PARK_TRIM cùng lý do gộp thành 1 DÒNG TỔNG sau vòng lặp
# thay vì lặp theo từng lệnh — bài test này cập nhật để khớp layout mới (1 dòng, không phải
# N dòng), vẫn giữ nguyên tinh thần gốc: giá trị % PHẢI đọc động từ target_park.
# Real plan 08-07 đã có sẵn 3 PARK_TRIM order trong orders[]; ghi đè target_park=0.30 để
# chứng minh dòng render đúng theo config, không phải hardcode.
# ⚠️ CHỈ kiểm dòng "↳ ℹ️ Lý do" do send_plan_report.sh TỰ SINH — các dòng note/notes khác
# trong plan 08-07 là DỮ LIỆU LỊCH SỬ tĩnh (baked-in lúc target thật sự là 80%), không phải
# code-generated, nên hợp lệ khi vẫn còn "80%" — không dùng blanket "80% not in out".
print("\n[T10] Lý do PARK_TRIM phải ĐỘNG theo target_park + gộp 1 dòng (không lặp theo lệnh)")
p = copy.deepcopy(SX)
p["park_trim_proposal"]["target_park"] = 0.30
out = run_sender(p, "SpaceX")
_reason_lines = [l.strip() for l in out.splitlines() if "↳ ℹ️ Lý do" in l]
check("target_park=0.30 → dòng 'Lý do' tổng in đúng 'trần PARK 30%', KHÔNG hardcode 80%",
      len(_reason_lines) > 0
      and all("trần PARK 30%" in l for l in _reason_lines)
      and not any("trần PARK 80%" in l for l in _reason_lines),
      _reason_lines[:1])
check("§2 style guide — CHỈ 1 dòng 'Lý do' tổng cho cả nhóm PARK_TRIM, KHÔNG lặp theo từng "
      "lệnh (3 lệnh PARK_TRIM trong plan 08-07 ⇒ đúng 1 dòng, không phải 3)",
      len(_reason_lines) == 1 and "áp dụng CHUNG" in _reason_lines[0],
      _reason_lines)
p2 = copy.deepcopy(SX)  # target_park thiếu/None → fallback "?" (khớp quy ước _tgt_s) thay vì bịa số
p2["park_trim_proposal"].pop("target_park", None)
out2 = run_sender(p2, "SpaceX")
check("target_park thiếu → fallback 'trần PARK ?' (không dấu %, khớp quy ước _tgt_s hiện có), KHÔNG bịa số",
      any("↳ ℹ️ Lý do" in l and "trần PARK ? (park-trim)" in l for l in out2.splitlines()))

# ── T11 — margin_note "khối lượng tính cho X× vốn" (DENIED/sizing branch) phải ĐỘNG theo
# CAPIT_LEVER_APPROVED_F, KHÔNG hardcode "1,3×". Bug cùng lớp với T10 (audit
# plan_report_audit_20260928 §1 #2, dòng ~481-483): trước sửa, literal "1,3×" mô tả lại
# CAPIT_LEVER_APPROVED_F trong khi biến/hằng số thật đã import được cùng scope — đổi gói
# đòn bẩy (vd f=1.5) sẽ lập tức sai mà không ai phát hiện nếu còn hardcode.
# ⚠️ Runtime fixture cho nhánh PLAN_SIZED_LEVERED_BUT_OFF/DENIED của preview_margin_day cần
# dựng toàn bộ envelope CAPIT + apply_capit_lever gating — CHƯA có sẵn ở bất kỳ selfcheck
# nào (kiểm tra 2026-09-29: 0 hit "PLAN_SIZED_LEVERED_BUT_OFF"/"CAPIT_LEVER_APPROVED_F"
# trong mike/bin/*selfcheck*.py). Test này PIN Ở TẦNG SOURCE (đọc chính f-string trong
# send_plan_report.sh) thay vì runtime — vẫn bắt được đúng mutation "hardcode lại 1,3×",
# nhưng KHÔNG chứng minh nhánh DENIED render đúng end-to-end. Ghi rõ đây là gap còn lại,
# không tự nhận là coverage đầy đủ.
print("\n[T11] margin_note '...× vốn' phải đọc CAPIT_LEVER_APPROVED_F (source-level pin)")
_sender_src = open(SENDER, encoding="utf-8").read()
check("f-string 'khối lượng tính cho ...× vốn' dùng {CAPIT_LEVER_APPROVED_F:g}, KHÔNG literal '1,3×'",
      "{CAPIT_LEVER_APPROVED_F:g}× " in _sender_src
      and "khối lượng tính cho 1,3× vốn" not in _sender_src)
check("import CAPIT_LEVER_APPROVED_F từ trading_bot.plan (cùng nguồn apply_capit_lever dùng)",
      "from trading_bot.plan import preview_margin_day, margin_day_approval, "
      "CAPIT_LEVER_APPROVED_F" in _sender_src)

# ── T12 — dòng tổng "Lý do (áp dụng CHUNG cho N lệnh)" trong orders[] loop (send_plan_report.sh
# ~L693/796, biến _pt_trim_tickers) phải lọc play_type == "PARK_TRIM" TUYỆT ĐỐI, KHÔNG được gộp
# nhầm 11 lệnh "PARK_TRIM+JIT_UNPARK" (đã dùng để TÀI TRỢ lệnh mua) vào nhóm "KHÔNG liên quan
# tới việc tài trợ lệnh mua" — arch-review vòng 1 mutation M4 (đổi == thành .startswith) tái tạo
# ĐÚNG sự cố 2026-09-17 (đọc 2 dòng liền nhau tưởng mâu thuẫn) theo chiều ngược lại. Logic sản
# xuất hiện == đã ĐÚNG; test này chỉ PIN để lỡ ai đổi == → startswith/in thì selfcheck phải ĐỎ ngay.
print("\n[T12] Dòng tổng 'Lý do PARK_TRIM' (orders loop) phải lọc play_type == 'PARK_TRIM' tuyệt đối")


def _n_pure_park_trim(plan):
    orders = plan.get("orders") or []
    sells = [o for o in orders if str(o.get("side", "")).lower() in ("sell", "ban", "s")]
    return len([o for o in sells if str(o.get("play_type", "")).upper() == "PARK_TRIM"])


def _n_sells(plan):
    orders = plan.get("orders") or []
    return len([o for o in orders if str(o.get("side", "")).lower() in ("sell", "ban", "s")])


SX_N_PURE_PT = _n_pure_park_trim(SX)
SX_N_SELLS = _n_sells(SX)
out_t12 = run_sender(SX, "SpaceX")
_pt_reason_lines = [l.strip() for l in out_t12.splitlines()
                    if "Lý do (áp dụng CHUNG cho" in l and "PARK_TRIM" in l]
check(f"plan 08-07: dòng tổng ghi ĐÚNG N={SX_N_PURE_PT} lệnh PARK_TRIM thuần (đếm từ artifact, "
      f"KHÔNG hardcode) — KHÔNG được là {SX_N_SELLS} (tổng mọi lệnh bán) hay gộp cả PARK_TRIM+JIT_UNPARK",
      SX_N_PURE_PT > 0
      and len(_pt_reason_lines) == 1
      and f"cho {SX_N_PURE_PT} lệnh BÁN PARK_TRIM" in _pt_reason_lines[0]
      and f"cho {SX_N_SELLS} lệnh" not in _pt_reason_lines[0],
      _pt_reason_lines[:1] or [f"(kỳ vọng N={SX_N_PURE_PT})"])

# Biến thể: đổi 1 lệnh PARK_TRIM+JIT_UNPARK → PARK_TRIM thuần ⇒ N phải TĂNG đúng 1, chứng minh
# số N phản ánh lọc play_type thật, không phải hằng số cố định trong test.
p_t12b = copy.deepcopy(SX)
_flipped = False
for o in p_t12b.get("orders") or []:
    if str(o.get("side", "")).lower() in ("sell", "ban", "s") and \
       str(o.get("play_type", "")) == "PARK_TRIM+JIT_UNPARK":
        o["play_type"] = "PARK_TRIM"
        _flipped = True
        break
assert _flipped, "fixture 08-07 phải có ít nhất 1 lệnh PARK_TRIM+JIT_UNPARK để flip — kiểm tra lại artifact"
N_EXPECTED_B = SX_N_PURE_PT + 1
out_t12b = run_sender(p_t12b, "SpaceX")
_pt_reason_lines_b = [l.strip() for l in out_t12b.splitlines()
                      if "Lý do (áp dụng CHUNG cho" in l and "PARK_TRIM" in l]
check(f"flip 1 lệnh PARK_TRIM+JIT_UNPARK→PARK_TRIM: N tăng đúng {SX_N_PURE_PT}→{N_EXPECTED_B}",
      len(_pt_reason_lines_b) == 1
      and f"cho {N_EXPECTED_B} lệnh BÁN PARK_TRIM" in _pt_reason_lines_b[0],
      _pt_reason_lines_b[:1] or [f"(kỳ vọng N={N_EXPECTED_B})"])

# ── T13 — cắt boilerplate 2026-09-29 (arch-review NEEDS_CHANGES → sửa → pin lại 5 hành vi) ──
print("\n[T13] Cắt boilerplate: chỉ suppress khi THẬT SỰ bình thường, không nuốt cảnh báo đi kèm")

# T13a: NO_TRIM_STRUCTURE (PARK vượt trần nhưng KHÔNG mã nào trim được — cùng bản chất
# BLOCKED_ALL_NAMES) KHÔNG được nằm trong tuple suppress — arch-review bắt bản đầu gộp nhầm.
p13a = copy.deepcopy(SX)
p13a["park_trim_proposal"]["decision"] = "NO_TRIM_STRUCTURE"
p13a["park_trim_proposal"]["notes"] = ["phần vượt trần nằm ở các mã CHƯA MUA, cần đường MUA P2"]
out_13a = run_sender(p13a, "SpaceX")
check("NO_TRIM_STRUCTURE vẫn in dòng L1 (không phải ngày yên ổn, cùng lớp BLOCKED_ALL_NAMES)",
      "L1 trim PARK: NO_TRIM_STRUCTURE" in out_13a)

# T13b: NO_TRIM là quiescent thật — nhưng nếu notes[] có cảnh báo ⚠️ thật (vd ENGINE CHƯA ĐỒNG BỘ,
# cổ tức QUÁ HẠN) thì KHÔNG được nuốt theo decision.
p13b = copy.deepcopy(SX)
p13b["park_trim_proposal"]["decision"] = "NO_TRIM"
p13b["park_trim_proposal"]["notes"] = ["⚠️ ENGINE CHƯA ĐỒNG BỘ — rail MUA park tới 30% nhưng rail "
                                        "TRIM chỉ kích khi vượt 80%, chép dòng này vào notes plan"]
out_13b = run_sender(p13b, "SpaceX")
check("NO_TRIM + notes có ⚠️ thật → vẫn in dòng L1 (không nuốt cảnh báo theo decision)",
      "L1 trim PARK: NO_TRIM" in out_13b and "ENGINE CHƯA ĐỒNG BỘ" in out_13b)

# T13c: NO_TRIM + notes benign (không ⚠️) → ĐÚNG là ngày yên ổn, suppress thật.
p13c = copy.deepcopy(SX)
p13c["park_trim_proposal"]["decision"] = "NO_TRIM"
p13c["park_trim_proposal"]["notes"] = ["PARK trong trần, không cần trim"]
out_13c = run_sender(p13c, "SpaceX")
check("NO_TRIM + notes benign → KHÔNG in dòng L1 (đúng ngày yên ổn, suppress)",
      "L1 trim PARK: NO_TRIM" not in out_13c)

# T13d: NO_TRIGGER (L2) benign → suppress (đối xứng T13c, mã thật SpaceX 2026-09-30 0 lệnh).
p13d = copy.deepcopy(SX)
p13d["jit_unpark_proposal"]["decision"] = "NO_TRIGGER"
p13d["jit_unpark_proposal"]["notes"] = ["không có lệnh MUA book BAL/LAG trong plan ⇒ L2 no-op "
                                        "(đúng thiết kế: L2 chỉ chạy khi có lệnh mua thật)"]
out_13d = run_sender(p13d, "SpaceX")
check("NO_TRIGGER + notes benign → KHÔNG in dòng L2 (đúng ngày yên ổn, suppress)",
      "L2 JIT unpark: NO_TRIGGER" not in out_13d)

# T13e (source-pin): điều kiện suppress price-verify phải dựa trên BẤT BIẾN THẬT
# (verified_n < tổng), KHÔNG được quay lại dùng sự hiện diện của "⚠️" trong text làm proxy —
# đúng lỗi arch-review 2026-09-29 bắt được (PARTIAL verified_n>=1 rơi vào nhánh ✅, "⚠️" in text
# luôn False nên bị suppress sai, giống hệt 0/N).
check('price-verify suppress dùng bất biến "verified_n < len(buy_sell_orders)", KHÔNG dùng "⚠️" in text',
      'verified_n < len(buy_sell_orders)' in _sender_src
      and 'if price_verify_note and "⚠️" in price_verify_note' not in _sender_src)

# T13f (source-pin): DCF/DD disclaimer footer + đoạn giải thích cơ chế pt_merged/jit_merged
# không còn được IN ra report (nội dung vẫn có thể còn trong comment giải thích — chỉ pin là
# KHÔNG có lệnh lines.append() nào phát các đoạn này nữa).
check("DCF_DISCLAIMER/DD_DISCLAIMER không còn được lines.append() vào report",
      "lines.append(f\"ℹ️ _{DCF_DISCLAIMER}_\")" not in _sender_src
      and "lines.append(f\"ℹ️ _{DD_DISCLAIMER}_\")" not in _sender_src)
check('Đoạn giải thích "LỆNH THẬT, đã gộp vào N lệnh ở trên" (cơ chế pt_merged/jit_merged) '
      "không còn bị lines.append() — chỉ còn trong COMMENT giải thích lý do bỏ (không render)",
      'lines.append(f"   ✅ Lệnh BÁN PARK {_which} là LỆNH THẬT, đã gộp' not in _sender_src)

print(f"\n{'=' * 72}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
for f in FAIL:
    print(f"  ✗ {f}")
sys.exit(1 if FAIL else 0)
