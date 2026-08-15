# -*- coding: utf-8 -*-
"""Self-check LUẬT A — trần giá mua `anchor(phiên trước) × (1+τ)` sinh lúc lập plan.

Context: user chốt Rule A ngày 2026-08-15 (bus `ceiling-rule-AB-user-decision-CORRECTED`,
decided_by=user) sau nghiên cứu `ceiling_ab_pacing_20260814`. Đây là **lựa chọn CHÍNH SÁCH**
(trả thêm ~16 bps để cắt rủi ro kẹt hoàn toàn), KHÔNG phải edge — không con số nào ở đây được
trích như "cải tiến có bằng chứng".

BẤT BIẾN của file này:
  A. **"Nothing changed"** — mọi lệnh KHÔNG khai `ceiling_rule="A"` phải cho trần Y HỆT luật cũ,
     kể cả các ca rác đã từng bị quant-skeptic bắt (trần âm/0/không parse được ⇒ rơi về anchor).
     Kiểm bằng cách nạp lại 4 plan LIVE THẬT đã chạy và đòi trần khớp từng đồng.
  B. **Không có đường FAIL-OPEN**: khai Rule A mà provenance hỏng ở BẤT KỲ đâu (thiếu anchor,
     τ ngoài dải, trần không tái lập được, anchor_date ≥ plan_date) ⇒ VỨT con số đã khai, quay
     về luật cũ. Đặc biệt: một plan sửa tay ghi trần to + nhãn "A" KHÔNG được hưởng trần đó.
  C. **Trần chỉ neo vào phiên ĐÃ ĐÓNG trước plan_date** — bất biến chống "trượt trong phiên".
  D. **Phạm vi**: chỉ lệnh MUA có `entry_anchor_price` và book ≠ DISCRETIONARY_SPECIAL.
     BAL/CAPIT/momentum/lệnh BÁN không bao giờ bị đụng.
  E. **Executor không đổi**: `_hard_buy_ceiling()` vẫn chỉ đọc `hard_no_chase_ceiling_vnd`, và
     mọi ca "trần mở khoá lệnh" đều có CA CHỨNG MINH NGƯỢC (bỏ Rule A ra thì `_limit_price`
     trả None = KHÔNG đặt được lệnh nào).

Run: /home/trido/thanhdt/wc_venv/bin/python rule_a_ceiling_selfcheck.py   (exit 0 = pass)
"""
import copy
import glob
import json
import math
import os
import sys

# §5b: selfcheck chạm Executor phải chặn `_publish_bot_event` ghi lên bus THẬT.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from trading_bot.no_chase_ceiling import (  # noqa: E402
    RULE_A, RULE_A_TAU_DEFAULT, RULE_A_TAU_MAX, BOOKS_WITH_OWN_CEILING_ENGINE,
    ANCHOR_BASIS_OFFICIAL_REF, EXCHANGE_BAND_PCT, apply_rule_a, check_reference_snapshot,
    resolve_buy_ceiling, rule_a_ceiling)
from trading_bot.brokers import EXCHANGE_BAND_PCT as BROKER_BANDS
from trading_bot.plan import PlannedOrder, load_plan  # noqa: E402
from trading_bot.config import PLAN_DIR  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


PLAN_DATE = "2026-08-18"
ANCHOR_DATE = "2026-08-17"


def buy(**over):
    """Lệnh LAG entry-window điển hình (khuôn DRI plan 08-10 THẬT)."""
    o = {"id": "BUY-DRI-01", "side": "buy", "ticker": "DRI", "qty": 1000,
         "ref_price": 13000.0, "book": "LAG", "play_type": "LAG_HI",
         "entry_anchor_price": 13000.0}
    o.update(over)
    return o


def rule_a_order(anchor=13400.0, tau=RULE_A_TAU_DEFAULT, **over):
    c = math.floor(anchor * (1 + tau))
    o = buy(hard_no_chase_ceiling_vnd=float(c), ceiling_rule=RULE_A,
            ceiling_anchor_price=anchor, ceiling_anchor_date=ANCHOR_DATE, ceiling_tau=tau,
            ceiling_anchor_basis=ANCHOR_BASIS_OFFICIAL_REF, ceiling_exchange="HOSE")
    o.update(over)
    return o


# ── A. rule_a_ceiling — công thức, làm tròn, dải τ ────────────────────────────────────────
print("A. rule_a_ceiling(): công thức + làm tròn CHẶT + dải τ")
c, _ = rule_a_ceiling(13000.0, 0.03)
check("A1 13.000 × 1,03 = 13.390", c == 13390.0, f"{c}")
c, _ = rule_a_ceiling(13333.0, 0.03)
check("A2 làm tròn XUỐNG (floor), không bao giờ nới trần",
      c == float(math.floor(13333.0 * 1.03)) and c == 13732.0, f"{c} (thô {13333.0*1.03:.4f})")
check("A3 τ mặc định = 3% đúng giá trị user chốt 2026-08-12",
      RULE_A_TAU_DEFAULT == 0.03, str(RULE_A_TAU_DEFAULT))
for bad in (0, -0.01, RULE_A_TAU_MAX + 1e-9, 0.5, None, "3%", True):
    c, why = rule_a_ceiling(13000.0, bad)
    check(f"A4 τ={bad!r} bị từ chối", c is None, why)
c, _ = rule_a_ceiling(13000.0, RULE_A_TAU_MAX)
check("A5 τ = trần 10% vẫn hợp lệ (biên đóng)", c == 14300.0, f"{c}")
for bad in (0, -1, None, "rác", float("nan")):
    c, why = rule_a_ceiling(bad, 0.03)
    check(f"A6 anchor={bad!r} bị từ chối", c is None, why)

# ── B. resolve_buy_ceiling — "nothing changed" cho lệnh KHÔNG khai Rule A ─────────────────
print("\nB. NOTHING CHANGED — lệnh không khai Rule A đi đúng luật cũ 2026-08-09")
cases = [
    ("B1 chỉ có entry_anchor_price ⇒ trần = anchor", buy(), 13000.0),
    ("B2 generator ghi trần CHẶT HƠN ⇒ giữ cái chặt hơn",
     buy(hard_no_chase_ceiling_vnd=12500.0), 12500.0),
    ("B3 generator ghi trần RỘNG HƠN ⇒ kẹp về anchor (không nới)",
     buy(hard_no_chase_ceiling_vnd=99000.0), 13000.0),
    ("B4 trần rác ÂM ⇒ rơi về anchor, KHÔNG tắt trần",
     buy(hard_no_chase_ceiling_vnd=-1), 13000.0),
    ("B5 trần rác 0 ⇒ rơi về anchor", buy(hard_no_chase_ceiling_vnd=0), 13000.0),
    ("B6 trần rác chuỗi ⇒ rơi về anchor", buy(hard_no_chase_ceiling_vnd="rác"), 13000.0),
    ("B7 anchor rác ⇒ chỉ còn trần generator", buy(entry_anchor_price="n/a",
                                                  hard_no_chase_ceiling_vnd=12000.0), 12000.0),
    ("B8 không anchor, không trần ⇒ None (hành vi cũ)",
     buy(entry_anchor_price=None), None),
]
for nm, o, want in cases:
    got, info = resolve_buy_ceiling(o, plan_date=PLAN_DATE)
    check(nm, got == want, f"got={got} want={want} mode={info.get('mode')}")
got, info = resolve_buy_ceiling(
    {"side": "sell", "ticker": "DRI", "hard_no_chase_ceiling_vnd": 13000.0}, PLAN_DATE)
check("B9 lệnh BÁN không có khái niệm trần đuổi ⇒ None",
      got is None and info["mode"] == "not_a_buy", f"{got}/{info['mode']}")

# ── C. Rule A hợp lệ ─────────────────────────────────────────────────────────────────────
print("\nC. Rule A hợp lệ — trần NỚI so với entry_anchor_price đóng băng")
o = rule_a_order(anchor=13400.0)
got, info = resolve_buy_ceiling(o, plan_date=PLAN_DATE)
check("C1 trần = floor(13.400 × 1,03) = 13.802", got == 13802.0, f"{got}")
check("C2 mode = rule_a", info["mode"] == "rule_a", info["mode"])
check("C3 entry_anchor_price (13.000) KHÔNG còn kẹp xuống — đúng mục đích Rule A",
      got > o["entry_anchor_price"], f"{got} > {o['entry_anchor_price']}")
o2 = rule_a_order(anchor=12000.0)
got2, _ = resolve_buy_ceiling(o2, plan_date=PLAN_DATE)
check("C4 anchor ĐI XUỐNG ⇒ trần HẠ theo (luật đối xứng, chỉ mua rẻ hơn)",
      got2 == 12360.0 and got2 < o2["entry_anchor_price"], f"{got2}")
check("C5 không truyền plan_date ⇒ bỏ qua kiểm ngày (chỉ dùng trong test đơn vị)",
      resolve_buy_ceiling(rule_a_order(), plan_date=None)[0] == 13802.0)

# ── D. FAIL-CLOSED — mọi đường hỏng của Rule A ───────────────────────────────────────────
print("\nD. FAIL-CLOSED — provenance hỏng ⇒ VỨT số đã khai, quay về luật cũ")
broken = [
    ("D1 thiếu ceiling_anchor_price", {"ceiling_anchor_price": None}),
    ("D2 anchor ≤ 0", {"ceiling_anchor_price": -13400.0}),
    ("D3 anchor không parse được", {"ceiling_anchor_price": "mười ba nghìn"}),
    ("D4 τ vượt trần cứng 10%", {"ceiling_tau": 0.25,
                                 "hard_no_chase_ceiling_vnd": float(math.floor(13400 * 1.25))}),
    ("D5 τ = 0", {"ceiling_tau": 0, "hard_no_chase_ceiling_vnd": 13400.0}),
    ("D6 τ thiếu", {"ceiling_tau": None}),
    ("D7 trần KHÔNG tái lập được từ anchor (plan sửa tay)",
     {"hard_no_chase_ceiling_vnd": 25000.0}),
    ("D8 trần lệch 1đ so với công thức", {"hard_no_chase_ceiling_vnd": 13803.0}),
    ("D9 thiếu hẳn trần", {"hard_no_chase_ceiling_vnd": None}),
    ("D10 anchor_date = plan_date (giá TRONG PHIÊN — trượt trong phiên)",
     {"ceiling_anchor_date": PLAN_DATE}),
    ("D11 anchor_date SAU plan_date (look-ahead)", {"ceiling_anchor_date": "2026-08-19"}),
    ("D12 anchor_date không parse được", {"ceiling_anchor_date": "hôm qua"}),
    ("D13 anchor_date thiếu", {"ceiling_anchor_date": None}),
]
for nm, over in broken:
    o = rule_a_order(**over)
    got, info = resolve_buy_ceiling(o, plan_date=PLAN_DATE)
    check(f"{nm} ⇒ về luật cũ (13.000)",
          got == 13000.0 and info["mode"] == "rule_a_failsafe",
          f"got={got} mode={info.get('mode')} | {info.get('reason','')[:90]}")

o = rule_a_order(hard_no_chase_ceiling_vnd=99_000.0, entry_anchor_price=None)
got, info = resolve_buy_ceiling(o, plan_date=PLAN_DATE)
check("D14 Rule A hỏng + KHÔNG có entry_anchor_price ⇒ trần khai bị VỨT (None), "
      "tuyệt đối không fail-OPEN sang 99.000",
      got is None and info["mode"] == "rule_a_failsafe", f"got={got}")
o = rule_a_order()
o["ceiling_rule"] = "B"
got, _ = resolve_buy_ceiling(o, plan_date=PLAN_DATE)
check("D15 nhãn rule lạ ('B') KHÔNG kích hoạt Rule A ⇒ kẹp về anchor cũ", got == 13000.0, f"{got}")
o = rule_a_order()
o["ceiling_rule"] = " a "
got, _ = resolve_buy_ceiling(o, plan_date=PLAN_DATE)
check("D16 nhãn ' a ' (thường + khoảng trắng) VẪN nhận đúng là Rule A", got == 13802.0, f"{got}")
got, _ = resolve_buy_ceiling(rule_a_order(), plan_date="không-phải-ngày")
check("D17 plan_date rác ⇒ fail-closed về luật cũ", got == 13000.0, f"{got}")

# ── E. apply_rule_a — PHẠM VI ────────────────────────────────────────────────────────────
print("\nE. PHẠM VI — chỉ lệnh MUA có entry_anchor_price, book ≠ DISCRETIONARY_SPECIAL")
ANCH = {"DRI": (13400.0, ANCHOR_DATE, "UPCOM"), "VNM": (60000.0, ANCHOR_DATE, "HOSE"),
        "TV1": (20100.0, ANCHOR_DATE, "UPCOM"), "SSI": (24500.0, ANCHOR_DATE, "HOSE")}
orders = [
    buy(),                                                             # LAG có anchor → ÁP
    buy(id="BUY-SSI-02", ticker="SSI", entry_anchor_price=24450.0, play_type="LAG_LO"),
    {"id": "BUY-VNM-03", "side": "buy", "ticker": "VNM", "book": "BAL",  # BAL không anchor
     "play_type": "SIGNAL_V11", "ref_price": 60000.0, "qty": 500},
    {"id": "BUY-VNM-04", "side": "buy", "ticker": "VNM", "book": "CAPIT",
     "play_type": "CAPIT", "ref_price": 60000.0, "qty": 500},
    {"id": "BUY-TV1-05", "side": "buy", "ticker": "TV1", "book": "DISCRETIONARY_SPECIAL",
     "entry_anchor_price": 20000.0, "hard_no_chase_ceiling_vnd": 20661.0, "ref_price": 20000.0},
    {"id": "SELL-DRI-06", "side": "sell", "ticker": "DRI", "book": "LAG",
     "entry_anchor_price": 13000.0, "ref_price": 13000.0, "qty": 100},
]
snapshot = copy.deepcopy(orders)
n, notes = apply_rule_a(orders, ANCH)
check("E1 áp đúng 2 lệnh (LAG DRI + LAG SSI)", n == 2, f"n={n}")
check("E2 DRI có trần Rule A", orders[0].get("ceiling_rule") == RULE_A
      and orders[0]["hard_no_chase_ceiling_vnd"] == 13802.0,
      str(orders[0].get("hard_no_chase_ceiling_vnd")))
check("E3 SSI có trần Rule A", orders[1]["hard_no_chase_ceiling_vnd"] == float(
    math.floor(24500 * 1.03)))
for i, nm in ((2, "BAL"), (3, "CAPIT")):
    check(f"E4 {nm} KHÔNG bị đụng (byte-identical)", orders[i] == snapshot[i], str(orders[i]))
check("E5 DISCRETIONARY_SPECIAL KHÔNG bị đụng — đã có engine trần riêng",
      orders[4] == snapshot[4] and "DISCRETIONARY_SPECIAL" in BOOKS_WITH_OWN_CEILING_ENGINE)
check("E6 lệnh BÁN KHÔNG bị đụng", orders[5] == snapshot[5])
check("E7 mã KHÔNG tra được anchor ⇒ bỏ qua, giữ nguyên luật cũ",
      apply_rule_a([buy(ticker="ZZZ")], {})[0] == 0)
o_stale = buy()
apply_rule_a([o_stale], {"DRI": (13400.0, ANCHOR_DATE, "UPCOM")}, tau=0.5)
check("E8 τ ngoài dải ⇒ apply_rule_a KHÔNG gắn nhãn (không sinh plan hỏng)",
      o_stale.get("ceiling_rule") is None, str(o_stale.get("ceiling_rule")))


# ── G. CƠ SỞ GIÁ ANCHOR (sửa lỗi 2026-08-15) ─────────────────────────────────────────────
print("\nG. Cơ sở giá anchor — giá tham chiếu CHÍNH THỨC, không phải giá đóng cửa")
o = rule_a_order()
o.pop("ceiling_anchor_basis")
got, inf = resolve_buy_ceiling(o, plan_date=PLAN_DATE)
check("G1 plan VINTAGE CŨ (không khai ceiling_anchor_basis) ⇒ FAIL-CLOSED về luật cũ",
      got == 13000.0 and inf["mode"] == "rule_a_failsafe", f"{got} / {inf.get('mode')}")
o = rule_a_order(ceiling_anchor_basis="prev_close")
got, _ = resolve_buy_ceiling(o, plan_date=PLAN_DATE)
check("G2 cơ sở giá SAI ('prev_close') ⇒ FAIL-CLOSED, không được hưởng trần rộng",
      got == 13000.0, f"{got}")
o = rule_a_order(ceiling_exchange="XXX")
got, _ = resolve_buy_ceiling(o, plan_date=PLAN_DATE)
check("G3 sàn không hợp lệ ⇒ FAIL-CLOSED (sàn quyết định công thức tham chiếu)",
      got == 13000.0, f"{got}")
check("G4 EXCHANGE_BAND_PCT khớp bản trong brokers.py (một chính sách, một số)",
      EXCHANGE_BAND_PCT == BROKER_BANDS, f"{EXCHANGE_BAND_PCT} vs {BROKER_BANDS}")
n2, _ = apply_rule_a([buy(ticker="DRI")], {"DRI": (13400.0, ANCHOR_DATE, "XXX")})
check("G5 apply_rule_a KHÔNG gắn nhãn khi sàn không xác định", n2 == 0, f"n={n2}")
o_ok = buy(ticker="DRI")
apply_rule_a([o_ok], {"DRI": (13400.0, ANCHOR_DATE, "upcom")})
check("G6 apply_rule_a ghi provenance cơ sở giá + sàn (chuẩn hoá hoa)",
      o_ok["ceiling_anchor_basis"] == ANCHOR_BASIS_OFFICIAL_REF
      and o_ok["ceiling_exchange"] == "UPCOM", str(o_ok.get("ceiling_exchange")))

print("\nG'. check_reference_snapshot — 3 cổng G1/G2/G3, fail-closed mọi hướng")
ok, i = check_reference_snapshot(20000.0, 23000.0, 17000.0, "UPCOM", True,
                                 prev_low=19500.0, prev_high=20500.0)
check("G'1 snapshot UPCOM hợp lệ (biên ±15%, ref ∈ biên phiên trước) ⇒ NHẬN", ok, i.get("reason"))
ok, i = check_reference_snapshot(20000.0, 23000.0, 17000.0, "HOSE", True)
check("G'2 biên ±15% nhưng khai sàn HOSE (±7%) ⇒ CHẶN — phép kiểm TRỰC GIAO bắt sai sàn",
      not ok and i["gate"] == "G2", str(i.get("gate")))
ok, i = check_reference_snapshot(20000.0, 23000.0, 17000.0, "HOSE", False)
check("G'3 sàn KHÔNG xác định được (exchange_known=False) ⇒ CHẶN, không đoán 'HOSE'",
      not ok and i["gate"] == "G1", str(i.get("gate")))
ok, i = check_reference_snapshot(20000.0, 23000.0, 17000.0, "UPCOM", True,
                                 prev_low=21000.0, prev_high=22000.0)
check("G'4 tham chiếu NGOÀI biên giá phiên trước ⇒ CHẶN (bắt snapshot CŨ)",
      not ok and i["gate"] == "G3", str(i.get("gate")))
for bad in (None, 0, -1, "abc", float("nan")):
    ok, _ = check_reference_snapshot(bad, 23000.0, 17000.0, "UPCOM", True)
    check(f"G'5 ref rác ({bad!r}) ⇒ CHẶN", not ok)
ok, i = check_reference_snapshot(20000.0, None, 17000.0, "UPCOM", True)
check("G'6 thiếu giá trần sống ⇒ CHẶN (không kiểm chéo được biên độ)",
      not ok and i["gate"] == "G2", str(i.get("gate")))
ok, i = check_reference_snapshot(19600.0, 20972.0, 18228.0, "HOSE", True,
                                 prev_low=24000.0, prev_high=25000.0)
check("G'7 ca SSI ex-right 08-17: tham chiếu 19.600 điều chỉnh, ngoài biên phiên trước "
      "[24.000; 25.000] ⇒ CHẶN — caller phải xử lý GDKHQ tường minh, không lặng lẽ nhận",
      not ok and i["gate"] == "G3", str(i.get("gate")))

# ── F. Vòng khép kín qua load_plan() — file plan THẬT trên đĩa ───────────────────────────
print("\nF. load_plan() — vòng khép kín trên file plan thật (ghi tạm, xoá sau)")
tmp_date = "2099-12-31"                     # ngày sentinel, không đụng plan production nào
tmp_path = os.path.join(PLAN_DIR, f"plan_selfcheckRuleA_{tmp_date}.json")


def write_tmp(orders_):
    os.makedirs(PLAN_DIR, exist_ok=True)
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump({"plan_date": tmp_date, "signal_date": "2099-12-30", "strategy": "selfcheck",
                   "strategy_version": "0", "state": 3, "state_name": "NEUTRAL",
                   "nav_basis": {"account_nav": 1e9, "paper_nav": 1e9, "scale": 1.0},
                   "account": "selfcheckRuleA", "orders": orders_}, f, ensure_ascii=False)


try:
    ok_o = rule_a_order(anchor=13400.0, ceiling_anchor_date="2099-12-30")
    bad_o = rule_a_order(anchor=13400.0, ceiling_anchor_date="2099-12-30",
                         id="BUY-POW-02", ticker="POW", entry_anchor_price=13400.0,
                         hard_no_chase_ceiling_vnd=25000.0)      # trần bịa, nhãn A
    old_o = buy(id="BUY-SCL-03", ticker="SCL", entry_anchor_price=24200.0, ref_price=24200.0)
    write_tmp([ok_o, bad_o, old_o])
    p = load_plan(tmp_date, account="selfcheckRuleA")
    by = {o.id: o for o in p.orders}
    check("F1 Rule A hợp lệ ⇒ PlannedOrder mang trần 13.802",
          by["BUY-DRI-01"].hard_no_chase_ceiling_vnd == 13802.0,
          str(by["BUY-DRI-01"].hard_no_chase_ceiling_vnd))
    check("F2 provenance sống sót qua load_plan (audit trail)",
          by["BUY-DRI-01"].ceiling_rule == RULE_A
          and by["BUY-DRI-01"].ceiling_anchor_price == 13400.0
          and by["BUY-DRI-01"].ceiling_tau == RULE_A_TAU_DEFAULT)
    check("F3 plan sửa tay (trần 25.000 + nhãn A) ⇒ kẹp về entry_anchor_price 13.400",
          by["BUY-POW-02"].hard_no_chase_ceiling_vnd == 13400.0,
          str(by["BUY-POW-02"].hard_no_chase_ceiling_vnd))
    check("F4 lệnh luật cũ ⇒ trần = anchor 24.200 (không đổi)",
          by["BUY-SCL-03"].hard_no_chase_ceiling_vnd == 24200.0,
          str(by["BUY-SCL-03"].hard_no_chase_ceiling_vnd))

    # anchor_date == plan_date của CHÍNH file plan → phải fail-closed dù ngày hợp lệ về cú pháp
    write_tmp([rule_a_order(anchor=13400.0, ceiling_anchor_date=tmp_date)])
    p = load_plan(tmp_date, account="selfcheckRuleA")
    check("F5 anchor_date = plan_date của file ⇒ fail-closed (chống trượt trong phiên)",
          p.orders[0].hard_no_chase_ceiling_vnd == 13000.0,
          str(p.orders[0].hard_no_chase_ceiling_vnd))
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

# ── G. Hồi quy trên 4 plan LIVE THẬT — trần phải KHÔNG ĐỔI ───────────────────────────────
print("\nG. HỒI QUY — nạp lại plan LIVE thật, trần phải y hệt luật cũ")
real = sorted(glob.glob(os.path.join(PLAN_DIR, "plan_*.json")))
n_seen = n_ceiled = 0
for path in real:
    base = os.path.basename(path)[len("plan_"):-len(".json")]
    acct, _, pdate = base.rpartition("_")
    try:
        raw = json.load(open(path, encoding="utf-8"))
    except Exception:
        continue
    if any(o.get("ceiling_rule") for o in raw.get("orders", [])):
        continue                          # plan đã dùng Rule A ⇒ không phải ca "không đổi"
    try:
        p = load_plan(pdate, account=acct)
    except Exception as exc:              # plan schema cũ/hỏng — không phải phạm vi file này
        print(f"    (bỏ qua {base}: {type(exc).__name__})")
        continue
    if p is None:
        continue
    n_seen += 1
    for po, ro in zip(p.orders, raw["orders"]):
        if po.side != "buy":
            continue
        anchor = ro.get("entry_anchor_price")
        cur = ro.get("hard_no_chase_ceiling_vnd")
        try:
            cur = float(cur or 0)
        except (TypeError, ValueError):
            cur = 0.0
        if anchor:
            want = min(cur, float(anchor)) if cur > 0 else float(anchor)
        else:
            want = cur if cur > 0 else None
        got = po.hard_no_chase_ceiling_vnd
        if want is not None:
            n_ceiled += 1
        if (got or None) != (want or None):
            check(f"G {base}/{po.id} trần không đổi", False, f"got={got} want={want}")
check(f"G1 nạp lại {n_seen} plan thật, {n_ceiled} lệnh mua có trần — 0 lệnh đổi giá trị",
      n_seen >= 10 and n_ceiled >= 12, f"n_plan={n_seen} n_ceiled={n_ceiled}")

# ── H. Executor CHỈ ĐỌC field — và ca chứng minh ngược ───────────────────────────────────
print("\nH. executor._limit_price() — chỉ đọc field, có ca chứng minh ngược")
from trading_bot.executor import Executor  # noqa: E402
from trading_bot.brokers import Quote      # noqa: E402


def _po(**kw):
    d = {"id": "BUY-DRI-01", "side": "buy", "ticker": "DRI", "qty": 1000,
         "ref_price": 13802.0, "book": "LAG", "play_type": "LAG_HI"}
    d.update(kw)
    return PlannedOrder(**d)


ex = Executor.__new__(Executor)
ex.cfg = {"chase_ticks": 1, "max_chase_pct_sell": 0.03, "chase_cap_vol_static": 0.04,
          "chase_cap_vol_k": 2.0, "chase_cap_vol_ceil": 0.04}
ex.state = {}
ex._buy_chase_pct = lambda tk: 0.04          # cố định để test tất định, không đụng rvol thật


def _q(floor_px):
    """Quote dựng từ payload THÔ (Quote.__init__ nhận raw dict, không nhận kwargs)."""
    return Quote({"symbol": "DRI", "exchange": "HOSE", "lastPrice": 13750.0,
                  "refPrice": 13400.0, "ceiling": 14300.0, "floor": floor_px,
                  "bestOffer1Price": 13750.0, "bestBid1Price": 13700.0})


q = _q(12500.0)

px_a = ex._limit_price(_po(hard_no_chase_ceiling_vnd=13802.0), q)
check("H1 Rule A (trần 13.802) ⇒ đặt được lệnh ở giá chào 13.750",
      px_a is not None and px_a <= 13802.0, str(px_a))
px_old = ex._limit_price(_po(ref_price=13000.0, hard_no_chase_ceiling_vnd=13000.0), q)
check("H2 CA CHỨNG MINH NGƯỢC: luật cũ (trần 13.000 < giá SÀN 12.500? không) — "
      "giá bị kẹp về đúng trần, KHÔNG vượt", px_old is not None and px_old <= 13000.0,
      str(px_old))
q_gap = _q(13500.0)
px_none = ex._limit_price(_po(ref_price=13000.0, hard_no_chase_ceiling_vnd=13000.0), q_gap)
check("H3 CA CHỨNG MINH NGƯỢC THẬT: giá SÀN 13.500 > trần cũ 13.000 ⇒ KHÔNG đặt lệnh (None) — "
      "đây đúng là ca Rule A sinh ra để chữa", px_none is None, str(px_none))
px_fix = ex._limit_price(_po(hard_no_chase_ceiling_vnd=13802.0), q_gap)
check("H4 … cùng quote đó, Rule A ĐẶT ĐƯỢC lệnh", px_fix is not None and px_fix <= 13802.0,
      str(px_fix))
check("H5 executor không tự suy trần — bỏ field ⇒ _hard_buy_ceiling None (§24)",
      Executor._hard_buy_ceiling(_po()) is None)
check("H6 lệnh BÁN không bao giờ có trần mua",
      Executor._hard_buy_ceiling(_po(side="sell", hard_no_chase_ceiling_vnd=13802.0)) is None)

print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ tất cả PASS — Rule A mặc định KHÔNG đổi hành vi lệnh nào; mọi đường hỏng fail-CLOSED "
      "về luật cũ; phạm vi chỉ LAG entry-window; executor không đổi.")
