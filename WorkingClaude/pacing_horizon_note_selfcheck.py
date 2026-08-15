# -*- coding: utf-8 -*-
"""pacing_horizon_note_selfcheck.py — self-check cho trading_bot.plan.annotate_pacing_horizon.

Chú thích "số phiên gom kỳ vọng" cho lệnh lớn so với ADV (README §4b nghiên cứu
ceiling_ab_pacing_20260814, user duyệt 2026-08-15). THUẦN THÔNG TIN ⇒ trọng tâm self-check là
BẤT BIẾN "không đổi gì cả": qty / ref_price / số lệnh / mọi field khác phải y nguyên.

Chạy:  $DNA_PYEXE pacing_horizon_note_selfcheck.py       (offline, ADV giả lập — không chạm BQ)
"""
import copy
import os
import sys

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")   # §5b coding_guidelines

from trading_bot import plan as plan_mod
from trading_bot.plan import (PACING_NOTE_MARK, PlannedOrder, TradePlan,
                              annotate_pacing_horizon, pacing_horizon_for_ratio)

ASOF = "2026-08-15"
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def mk_plan(specs):
    """specs: list (ticker, qty, ref_price, note)."""
    orders = [PlannedOrder(id=f"BUY-{tk}-{i:02d}", ticker=tk, side="buy", qty=q,
                           ref_price=px, book="LAG", note=nt)
              for i, (tk, q, px, nt) in enumerate(specs)]
    return TradePlan(plan_date=ASOF, signal_date=ASOF, strategy="test", strategy_version="0",
                     state=3, state_name="NEUTRAL", nav_basis={}, orders=orders,
                     account="SELFCHECK")


def fake_adv(table):
    """table: {ticker: adv_vnd | None}; None = nguồn ADV hỏng cho mã đó."""
    def _f(ticker, asof):
        adv = table.get(ticker)
        if adv is None:
            return None, None, "selfcheck: không có ADV"
        return float(adv), "2026-08-14", None
    return _f


# ── 1. Bảng ngưỡng — đúng bảng đã đo trong README §4b ────────────────────────────────────
print("\n[1] pacing_horizon_for_ratio — bảng ngưỡng")
check("ratio None → không chú thích", pacing_horizon_for_ratio(None) is None)
check("5% ADV → không chú thích", pacing_horizon_for_ratio(0.05) is None)
check("đúng 10% ADV → không chú thích (biên dưới đóng)", pacing_horizon_for_ratio(0.10) is None)
check("10,1% ADV → 10 phiên", pacing_horizon_for_ratio(0.101)[0] == "10")
check("25% ADV → 10 phiên", pacing_horizon_for_ratio(0.25)[0] == "10")
check("đúng 30% ADV → 10 phiên", pacing_horizon_for_ratio(0.30)[0] == "10")
check("45% ADV → ≥10 phiên (vùng chưa đo, làm tròn lên)",
      pacing_horizon_for_ratio(0.45)[0] == "≥10")
check("60% ADV → ≥10 phiên", pacing_horizon_for_ratio(0.60)[0] == "≥10")
check("60% ADV → nêu rõ 5 phiên bất khả thi",
      "BẤT KHẢ THI" in pacing_horizon_for_ratio(0.60)[1])
check("120% ADV → ≥10 phiên", pacing_horizon_for_ratio(1.20)[0] == "≥10")
# đơn điệu: số phiên không bao giờ giảm khi ratio tăng
rank = {None: 0, "10": 1, "≥10": 2}
seq = [rank[(pacing_horizon_for_ratio(r) or (None,))[0]]
       for r in [0.02, 0.09, 0.11, 0.29, 0.31, 0.59, 0.61, 2.0]]
check("đơn điệu không giảm theo ratio", seq == sorted(seq), seq)

# ── 2. BẤT BIẾN: không đổi sizing / giá / số lệnh ────────────────────────────────────────
print("\n[2] bất biến — thuần thông tin, không đổi gì")
plan_mod._adv_for_gate = fake_adv({"AAA": 1_000_000_000,      # lệnh 300tr = 30% ADV
                                   "BBB": 20_000_000_000,     # lệnh 300tr = 1,5% ADV
                                   "CCC": 400_000_000})       # lệnh 300tr = 75% ADV
specs = [("AAA", 15000, 20000.0, ""), ("BBB", 15000, 20000.0, "ghi chú cũ"),
         ("CCC", 15000, 20000.0, "")]
before = copy.deepcopy(mk_plan(specs))
plan, notes = annotate_pacing_horizon(mk_plan(specs), asof=ASOF)
check("số lệnh không đổi", len(plan.orders) == len(before.orders))
check("qty không đổi", [o.qty for o in plan.orders] == [o.qty for o in before.orders])
check("ref_price không đổi",
      [o.ref_price for o in plan.orders] == [o.ref_price for o in before.orders])
check("không sinh trần giá / field giá mới",
      all(o.hard_no_chase_ceiling_vnd is None for o in plan.orders))
check("ticker/side/book/priority không đổi",
      [(o.ticker, o.side, o.book, o.priority) for o in plan.orders] ==
      [(o.ticker, o.side, o.book, o.priority) for o in before.orders])

# ── 3. Nội dung chú thích ────────────────────────────────────────────────────────────────
print("\n[3] nội dung chú thích")
by_tk = {o.ticker: o for o in plan.orders}
check("AAA (30% ADV) CÓ chú thích", PACING_NOTE_MARK in by_tk["AAA"].note)
check("AAA ghi 10 phiên", "10 phiên" in by_tk["AAA"].note)
check("BBB (1,5% ADV) KHÔNG chú thích", PACING_NOTE_MARK not in by_tk["BBB"].note)
check("BBB giữ nguyên note cũ", by_tk["BBB"].note == "ghi chú cũ")
check("CCC (75% ADV) ghi ≥10 phiên", "≥10 phiên" in by_tk["CCC"].note)
check("CCC nêu bất khả thi 5 phiên", "BẤT KHẢ THI" in by_tk["CCC"].note)
check("bản ghi trả về đúng số lệnh được chú thích",
      sum(1 for n in notes if n["action"] == "ANNOTATED") == 2)

# note cũ được GIỮ, chú thích nối sau
plan2, _ = annotate_pacing_horizon(mk_plan([("AAA", 15000, 20000.0, "ghi chú cũ")]), asof=ASOF)
check("giữ note cũ + nối chú thích", plan2.orders[0].note.startswith("ghi chú cũ | "))

# ── 4. Idempotent — gọi 2 lần không nhân đôi ─────────────────────────────────────────────
print("\n[4] idempotent")
p = mk_plan([("AAA", 15000, 20000.0, "ghi chú cũ")])
p, _ = annotate_pacing_horizon(p, asof=ASOF)
n1 = p.orders[0].note
p, _ = annotate_pacing_horizon(p, asof=ASOF)
check("gọi lần 2 cho note y hệt", p.orders[0].note == n1, p.orders[0].note)
check("chỉ 1 dấu [PACING]", p.orders[0].note.count(PACING_NOTE_MARK) == 1)
# ADV đổi ⇒ chú thích được THAY, không nối thêm
plan_mod._adv_for_gate = fake_adv({"AAA": 20_000_000_000})
p, _ = annotate_pacing_horizon(p, asof=ASOF)
check("ADV tăng ⇒ gỡ chú thích cũ, không còn dấu", PACING_NOTE_MARK not in p.orders[0].note)
check("gỡ xong vẫn giữ note gốc", p.orders[0].note == "ghi chú cũ")

# ── 5. Fail-mode nguồn ADV — KHÔNG chặn lệnh ─────────────────────────────────────────────
print("\n[5] fail-mode nguồn ADV")
plan_mod._adv_for_gate = fake_adv({"AAA": None})
p, notes = annotate_pacing_horizon(mk_plan([("AAA", 15000, 20000.0, "")]), asof=ASOF)
check("ADV hỏng: lệnh vẫn còn", len(p.orders) == 1)
check("ADV hỏng: qty nguyên vẹn", p.orders[0].qty == 15000)
check("ADV hỏng: không chú thích", PACING_NOTE_MARK not in p.orders[0].note)
check("ADV hỏng: báo NO_ADV cho caller",
      [n["action"] for n in notes] == ["NO_ADV"])


def _boom(ticker, asof):
    raise RuntimeError("BQ down")


plan_mod._adv_for_gate = _boom
p, notes = annotate_pacing_horizon(mk_plan([("AAA", 15000, 20000.0, "x")]), asof=ASOF)
check("nguồn ADV raise: KHÔNG raise ra ngoài, lệnh nguyên vẹn",
      len(p.orders) == 1 and p.orders[0].qty == 15000)
check("nguồn ADV raise: báo NO_ADV", notes and notes[0]["action"] == "NO_ADV")

# qty=0 / ref_price=0 → bỏ qua, không chia cho 0
plan_mod._adv_for_gate = fake_adv({"AAA": 1_000_000_000})
p, notes = annotate_pacing_horizon(mk_plan([("AAA", 0, 20000.0, ""), ("AAA", 100, 0.0, "")]),
                                   asof=ASOF)
check("qty=0 / ref_price=0 → bỏ qua sạch", notes == [])

print(f"\n{'='*60}\nPASS={PASS}  FAIL={FAIL}")
sys.exit(1 if FAIL else 0)
