#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check: cổng FAIL-SAFE đối soát cơ sở giá lệnh mua LUẬT A tại thời điểm ĐẶT LỆNH.

Job Taylor_20260815_022340 (việc 1). Đóng lỗ hổng quant-skeptic chỉ ra khi CONFIRMED bản wire
luật A: `_limit_price()` tính trần đuổi từ `ref_price`, nên nếu `ref_price`/anchor không còn
mô tả phiên đang chạy thì phần lớn tác dụng luật A bốc hơi mà KHÔNG có gì bắt lỗi.

§5b coding_guidelines: đặt MIKE_BOT_TEST_MODE=1 TRƯỚC khi dựng Executor — 6 call-site
`_publish_bot_event` bắn thẳng lên bus production dưới nhãn Mafee nếu không có guard này.
"""
import os
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")           # ← PHẢI đứng trước mọi import Executor

import datetime as dt
import json
import sys
import tempfile
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_bot.no_chase_ceiling import (                  # noqa: E402
    RULE_A_REF_TOL_DEFAULT, check_ref_vs_live, rule_a_ceiling, rule_a_in_force)
from trading_bot.plan import PlannedOrder, TradePlan, load_plan  # noqa: E402
from trading_bot.executor import Executor                   # noqa: E402
from trading_bot.config import DEFAULTS                     # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
FAIL = []
N = [0]


def check(name, cond, detail=""):
    N[0] += 1
    print(("  ✓ " if cond else "  ✗ ") + name + (f"  — {detail}" if detail else ""))
    if not cond:
        FAIL.append(name)


def mk(ticker="DRI", anchor=13000.0, tau=0.03, ref=None, side="buy", rule="A",
       ceiling=None, anchor_date="2026-08-14"):
    """PlannedOrder luật A hợp lệ theo mặc định; tham số để bẻ từng bất biến một."""
    ceil = ceiling if ceiling is not None else (rule_a_ceiling(anchor, tau)[0] if anchor else None)
    return PlannedOrder(
        id=f"B-{ticker}", ticker=ticker, side=side, qty=1000,
        ref_price=(anchor if ref is None else ref),
        hard_no_chase_ceiling_vnd=ceil, ceiling_rule=rule,
        ceiling_anchor_price=anchor, ceiling_anchor_date=anchor_date, ceiling_tau=tau)


CHASE = DEFAULTS["max_chase_pct_buy"]          # 1,5% — trần đuổi tĩnh thật của production

# ══════════════════════════════════════════════════════════════════════ A. rule_a_in_force
print("\nA. rule_a_in_force — CHỈ chạy cổng khi luật A THẬT SỰ đang hiệu lực")
check("A1 lệnh luật A hợp lệ → True", rule_a_in_force(mk()) is True)
check("A2 lệnh BÁN → False (không có khái niệm mua đuổi)",
      rule_a_in_force(mk(side="sell")) is False)
check("A3 không khai ceiling_rule → False (luật cũ, ngoài phạm vi)",
      rule_a_in_force(mk(rule=None)) is False)
check("A4 khai 'A' nhưng trần KHÔNG tái lập được từ provenance → False",
      rule_a_in_force(mk(ceiling=99999.0)) is False,
      "load_plan đã fail-closed về luật cũ; áp cổng luật A lên nó là chặn oan")
check("A5 khai 'A' nhưng thiếu anchor → False", rule_a_in_force(mk(anchor=None)) is False)
check("A6 nhãn 'a' thường + khoảng trắng vẫn nhận", rule_a_in_force(mk(rule=" a ")) is True)

# ══════════════════════════════════════════════════════════ B. C1 — anchor vs phiên sống
print("\nB. C1 — anchor luật A phải khớp giá đóng phiên ĐÃ HOÀN TẤT trên feed sống")
LIVE = 13000.0
ok, info = check_ref_vs_live(mk(anchor=LIVE), LIVE, CHASE)
check("B1 anchor == live → PASS", ok is True and info["check"] == "OK", info["reason"])

for dev in (0.009, -0.009):
    ok, info = check_ref_vs_live(mk(anchor=LIVE * (1 + dev)), LIVE, CHASE)
    check(f"B2 lệch {dev:+.1%} (trong dung sai 1%) → PASS", ok is True, info["reason"])

for dev in (0.0101, -0.0101, 0.05, -0.05):
    ok, info = check_ref_vs_live(mk(anchor=LIVE * (1 + dev)), LIVE, CHASE)
    check(f"B3 lệch {dev:+.2%} (ngoài dung sai) → CHẶN", ok is False and info["check"] == "C1",
          info["reason"][:90])

# Ca THẬT đo được 2026-08-15: SSI — BQ `Price` 24.500 vs DNSE `ohlc` 19.580 (−20%).
ok, info = check_ref_vs_live(mk("SSI", anchor=24500.0), 19580.0, CHASE)
check("B4 ca THẬT SSI (BQ 24.500 vs DNSE 19.580) → CHẶN", ok is False and info["check"] == "C1",
      f"lệch {info['anchor_dev']:+.1%}")

# Sai đơn vị nghìn↔VND (lỗi đã cắn thật trong chính họ nghiên cứu này).
ok, info = check_ref_vs_live(mk(anchor=13.0), LIVE, CHASE)
check("B5 sai đơn vị (13 thay vì 13.000) → CHẶN", ok is False and info["check"] == "C1")

# Plan trễ 1 phiên trên một mã đi mạnh qua đêm.
ok, info = check_ref_vs_live(mk(anchor=13000.0), 13650.0, CHASE)
check("B6 plan trễ 1 phiên, mã +5% qua đêm → CHẶN", ok is False and info["check"] == "C1",
      info["reason"][:80])

# GIỚI HẠN ĐÃ CÔNG BỐ (không phải bug): plan cũ mà mã đi <1% thì LỌT — nhưng sai số trần
# cũng <1%, tức bị chặn bởi đúng cận trên đã chọn. Test này khoá lời hứa đó lại.
ok, info = check_ref_vs_live(mk(anchor=13000.0), 13060.0, CHASE)
check("B7 GIỚI HẠN: plan cũ nhưng mã chỉ đi +0,46% → LỌT (đúng thiết kế, đã công bố)",
      ok is True, "sai số trần ≤1% ⇒ bị kẹp bởi chính cận trên của dung sai")

# ══════════════════════════════════════════ C. C2 — trần % theo ref_price không thay trần A
print("\nC. C2 — trần đuổi suy từ ref_price KHÔNG được âm thầm thay trần luật A")
ok, info = check_ref_vs_live(mk(anchor=LIVE, ref=LIVE), LIVE, CHASE)
check("C1 ref == anchor == live (đúng ca LAG 08-10 thật) → PASS", ok is True,
      f"cap {info['cap_from_ref_price']:,.0f} ≥ {info['cap_required_at_least']:,.0f}")

# ref_price cũ hơn thị trường: anchor vẫn tươi (đã sửa tay/tái sinh) nhưng ref thì không.
ok, info = check_ref_vs_live(mk(anchor=LIVE, ref=LIVE * 0.90), LIVE, CHASE)
check("C2 ref_price cũ −10% (anchor vẫn tươi) → CHẶN", ok is False and info["check"] == "C2",
      info["reason"][:95])

# Đúng hình dạng book DISCRETIONARY_SPECIAL: resting kéo lên cùng tỉ lệ với trần ⇒ PHẢI lọt.
ok, info = check_ref_vs_live(mk("TV1", anchor=20100.0, ref=20500.0), 20100.0, CHASE)
check("C3 ref_price CAO hơn anchor (resting kéo theo — thiết kế TV1) → PASS", ok is True,
      "một chiều có chủ đích: trần cứng vẫn kẹp phía trên, không có rủi ro mua đắt")

# Ranh giới chính xác của C2: cap_chase vừa đúng bằng min(trần, live).
edge_ref = LIVE / (1 + CHASE)
ok, _ = check_ref_vs_live(mk(anchor=LIVE, ref=edge_ref * 1.0001), LIVE, CHASE)
check("C4 ref ngay TRÊN ngưỡng C2 → PASS", ok is True)
ok, info = check_ref_vs_live(mk(anchor=LIVE, ref=edge_ref * 0.999), LIVE, CHASE)
check("C5 ref ngay DƯỚI ngưỡng C2 → CHẶN", ok is False and info["check"] == "C2")

# chase động (vol-scale) nới cap ⇒ ca biên C2 lật đúng chiều — cổng dùng chase THẬT của lệnh.
ok, _ = check_ref_vs_live(mk(anchor=LIVE, ref=edge_ref * 0.999), LIVE, 0.04)
check("C6 cùng ref nhưng chase động 4% → PASS (cổng dùng chase THẬT, không hằng số)", ok is True)

# ══════════════════════════════════════════════════════════════ D. fail-closed khi thiếu dữ liệu
print("\nD. Thiếu dữ liệu ⇒ FAIL-CLOSED (không có đường nào fail-OPEN)")
for bad in (None, 0, -1, "abc", float("nan")):
    ok, info = check_ref_vs_live(mk(), bad, CHASE)
    check(f"D1 live_prev_close={bad!r} → CHẶN", ok is False and info["check"] == "live_unavailable")
ok, info = check_ref_vs_live(mk(anchor=None), LIVE, CHASE)
check("D2 thiếu anchor → CHẶN", ok is False)
o = mk(); o.ref_price = None
ok, info = check_ref_vs_live(o, LIVE, CHASE)
check("D3 thiếu ref_price → CHẶN", ok is False and info["check"] == "C2")
ok, info = check_ref_vs_live(mk(), LIVE, None)
check("D4 thiếu chase_pct → CHẶN", ok is False and info["check"] == "C2")

# ═══════════════════════════════════════════════ E. _fetch_prev_close — chọn ĐÚNG bar phiên trước
print("\nE. Executor._fetch_prev_close — chỉ nhận bar phiên ĐÃ ĐÓNG, lấy từ DNSE (không BQ)")
TODAY = dt.datetime.now(ICT).date()


def ts_of(d):
    return int(dt.datetime.combine(d, dt.time(9, 0)).replace(tzinfo=ICT).timestamp())


class FakeClient:
    def __init__(self, bars, boom=False):
        self.bars, self.boom, self.calls = bars, boom, 0

    def ohlc(self, symbol, resolution="1D", **kw):
        self.calls += 1
        if self.boom:
            raise RuntimeError("DNSE 503")
        return {"t": [ts_of(d) for d, _ in self.bars], "c": [c for _, c in self.bars]}


d1, d2 = TODAY - dt.timedelta(days=4), TODAY - dt.timedelta(days=1)
px, why = Executor._fetch_prev_close(FakeClient([(d1, 12.9), (d2, 13.3), (TODAY, 13.9)]), "DRI")
check("E1 BỎ nến HÔM NAY đang chạy, lấy phiên đã đóng", px == 13300.0, f"{px} ({why})")
px, _ = Executor._fetch_prev_close(FakeClient([(d1, 12.9), (d2, 13.3)]), "DRI")
check("E2 không có nến hôm nay → vẫn lấy phiên gần nhất", px == 13300.0)
px, why = Executor._fetch_prev_close(FakeClient([(TODAY, 13.9)]), "DRI")
check("E3 CHỈ có nến hôm nay → None (fail-closed, không lấy giá đang đuổi làm mốc)",
      px is None, why)
px, why = Executor._fetch_prev_close(FakeClient([], boom=True), "DRI")
check("E4 ohlc ném lỗi → (None, lý do) chứ không nổ lên trên", px is None, why)


class BadShape:
    def ohlc(self, *a, **k):
        return {"t": [1, 2], "c": [1.0]}


px, why = Executor._fetch_prev_close(BadShape(), "DRI")
check("E5 mảng t↔c lệch độ dài → None", px is None, why)
px, _ = Executor._fetch_prev_close(FakeClient([(d2, 13300.0)]), "DRI")
check("E6 feed trả sẵn đơn vị VND → normalize_price_vnd giữ nguyên", px == 13300.0)

# ══════════════════════════════════════════════════ F. Executor — cache + bỏ qua khi không có feed
print("\nF. Executor._live_prev_close / _rule_a_ref_guard")


class FakeBroker:
    name = "fake"

    def __init__(self, client=None):
        self.client = client

    def get_quote(self, t):
        return None


def mk_exec(orders, client=None, vol_scale=False):
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL", nav_basis={},
                     orders=orders, account="SELFCHECK", created_at="2099-01-01T00:00:00")
    cfg = dict(DEFAULTS)
    # TẤT ĐỊNH hoá: mặc định production bật `chase_cap_vol_scale_enabled` ⇒ `_buy_chase_pct`
    # đọc rvol_20d THẬT từ cache BQ local ⇒ kết quả đổi theo máy/ngày. Tắt cho phần lớn test,
    # và có RIÊNG một test bật lại (F8) để đường vol-scale không bị bỏ trắng.
    cfg["chase_cap_vol_scale_enabled"] = vol_scale
    return Executor(plan, FakeBroker(client), cfg)


cl = FakeClient([(d2, 13.3)])
ex = mk_exec([mk()], cl)
check("F1 gọi 2 lần chỉ tốn 1 lời gọi ohlc (cache theo mã)",
      ex._live_prev_close("DRI")[0] == 13300.0 and ex._live_prev_close("DRI")[0] == 13300.0
      and cl.calls == 1, f"calls={cl.calls}")

ex_nofeed = mk_exec([mk()], None)
check("F2 broker KHÔNG có client ohlc (paper/sim) → cổng BỎ QUA, không chặn",
      ex_nofeed._rule_a_ref_guard(mk()) is None)

ex2 = mk_exec([mk()], FakeClient([(d2, 13.0)]))   # 13.000đ = ĐÚNG anchor mặc định của mk()
check("F3 anchor khớp phiên trước → cổng cho qua", ex2._rule_a_ref_guard(mk()) is None)
bad = ex2._rule_a_ref_guard(mk(anchor=15000.0, ref=15000.0))
check("F4 anchor lệch +15% → cổng CHẶN, trả (reason, info)",
      bad is not None and bad[1]["check"] == "C1", bad[0][:80] if bad else "")
check("F5 lệnh KHÔNG luật A đi qua cổng không đổi gì",
      ex2._rule_a_ref_guard(mk(rule=None)) is None)

ex3 = mk_exec([mk()], FakeClient([], boom=True))
bad = ex3._rule_a_ref_guard(mk())
check("F6 feed lỗi trên broker CÓ ohlc → CHẶN (fail-closed), không phải bỏ qua",
      bad is not None and bad[1]["check"] == "live_unavailable", bad[0][:70] if bad else "")

# Cổng đọc dung sai từ cfg (không hardcode) — hạ về 0,1% thì ca 0,46% phải lật sang CHẶN.
ex4 = mk_exec([mk()], FakeClient([(d2, 13.0)]))
ex4.cfg["rule_a_ref_tol_pct"] = 0.001
check("F7 dung sai lấy từ cfg (hạ 0,1% ⇒ ca lệch 0,46% lật sang CHẶN)",
      ex4._rule_a_ref_guard(mk(anchor=13060.0, ref=13060.0)) is not None)

# Đường vol-scale THẬT của production (`chase_cap_vol_scale_enabled=True`): chase = clamp(
# 2×rvol_20d, 1,5%, 4%), đọc rvol từ cache BQ local. Không assert lên giá trị rvol (nó là
# trạng thái SỐNG — §23 hệ luận 1), chỉ đòi cổng vẫn chạy được và vẫn cho lệnh ĐÚNG đi qua.
ex5 = mk_exec([mk()], FakeClient([(d2, 13.0)]), vol_scale=True)
check("F8 bật vol-scale như production → cổng vẫn cho lệnh anchor-đúng đi qua",
      ex5._rule_a_ref_guard(mk()) is None,
      f"chase thật của DRI trên máy này = {ex5._buy_chase_pct('DRI'):.2%}")

# ═════════════════════════════════════════════ G. §5b — selfcheck KHÔNG được bắn event bus thật
print("\nG. §5b — không rò event lên bus production khi chạy selfcheck")
sink = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False).name
os.environ["MIKE_BOT_TEST_EVENT_SINK"] = sink
from trading_bot.executor import _publish_bot_event                     # noqa: E402
_publish_bot_event("error", "RULE_A_REF_PRICE_MISMATCH", {"probe": True})
os.environ.pop("MIKE_BOT_TEST_EVENT_SINK")
rows = [json.loads(x) for x in open(sink, encoding="utf-8") if x.strip()]
check("G1 event bị chặn khỏi bus và chảy vào sink (MIKE_BOT_TEST_MODE=1)",
      len(rows) == 1 and rows[0]["topic"] == "RULE_A_REF_PRICE_MISMATCH")
os.unlink(sink)

# ══════════════════════════════════ H. HỒI QUY: nạp lại MỌI plan LIVE thật — 0 lệnh bị chặn oan
print("\nH. HỒI QUY trên plan LIVE thật — cổng mới KHÔNG được chặn lệnh nào đang chạy đúng")
import glob                                                              # noqa: E402
from trading_bot.config import PLAN_DIR                                  # noqa: E402
n_plan = n_buy = n_rule_a = n_guard_ran = 0
for path in sorted(glob.glob(os.path.join(PLAN_DIR, "plan_*.json"))):
    base = os.path.basename(path)[len("plan_"):-len(".json")]
    acct, _, pdate = base.rpartition("_")
    try:
        pl = load_plan(pdate, account=acct)      # ← (plan_date, account), KHÔNG phải path
    except Exception:
        continue
    if pl is None or not getattr(pl, "orders", None):
        continue                      # file không phải plan hợp lệ / plan rỗng
    n_plan += 1
    for o in pl.orders:
        if o.side != "buy":
            continue
        n_buy += 1
        if rule_a_in_force(o):
            n_rule_a += 1
        # Cổng chỉ được ĐỘNG tới lệnh luật A: mọi lệnh khác phải trả None kể cả khi feed hỏng.
        e = mk_exec([o], FakeClient([], boom=True))
        if not rule_a_in_force(o) and e._rule_a_ref_guard(o) is not None:
            n_guard_ran += 1
check(f"H1 nạp {n_plan} plan thật, {n_buy} lệnh mua — 0 lệnh NGOÀI luật A bị cổng động tới",
      n_guard_ran == 0, f"lệnh luật A trong kho plan hiện tại: {n_rule_a}")
check("H2 kho plan hiện tại chưa có lệnh luật A nào ⇒ hành vi LIVE hôm nay KHÔNG đổi",
      n_rule_a == 0, "đúng như commit 2db6d37 tuyên bố (chưa áp cho plan thật nào)")

print(f"\n{'='*78}")
if FAIL:
    print(f"❌ {len(FAIL)}/{N[0]} FAIL: {FAIL}")
    sys.exit(1)
print(f"✅ ALL PASS — {N[0]}/{N[0]} — cổng fail-safe cơ sở giá luật A (dung sai "
      f"{RULE_A_REF_TOL_DEFAULT:.2%}, đo N=66 mã 2026-08-15)")
