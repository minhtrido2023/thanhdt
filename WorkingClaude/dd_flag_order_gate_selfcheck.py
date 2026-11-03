# -*- coding: utf-8 -*-
"""dd_flag_order_gate_selfcheck.py — self-check cho trading_bot.plan.filter_dd_flag_orders
(+ due_diligence.dd_flag_verdict): luật user 2026-11-02 "mã có cờ ⇒ loại khỏi candidate mọi book".

Chạy:  $DNA_PYEXE dd_flag_order_gate_selfcheck.py            (unit, offline — DD bị monkeypatch)
       TRADING_BOT_RUNTIME_ROOT=/home/trido/thanhdt/WorkingClaude \\
       $DNA_PYEXE dd_flag_order_gate_selfcheck.py --live     (+ REPLAY DD THẬT trên plan gốc 03/11
           có TCH — bản .bak_20261102_2315 — cả 2 account)
       DDGATE_CODE_ROOT=<dir chứa trading_bot/>               (mutation runner dùng: import code
           từ bản sao đã gây đột biến thay vì cây này)

Không phụ thuộc TZ: mọi asof truyền tường minh (§16). Chạy lại dưới `env -u TZ` + TZ ngoại lai.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_ROOT = os.environ.get("DDGATE_CODE_ROOT") or HERE
sys.path.insert(0, CODE_ROOT)

from trading_bot import plan as plan_mod                       # noqa: E402
from trading_bot import due_diligence as dd                    # noqa: E402
from trading_bot.plan import (PlannedOrder, TradePlan, filter_dd_flag_orders,  # noqa: E402
                              net_offsetting_orders)

ASOF = "2026-11-03"
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def mk_plan(specs, account="SELFCHECK"):
    """specs: (ticker, book, side) hoặc (ticker, book, side, qty)."""
    orders = [PlannedOrder(id=f"{sp[2].upper()}-{sp[0]}-{i:02d}", ticker=sp[0], side=sp[2],
                           qty=(sp[3] if len(sp) > 3 else 1000), ref_price=20000.0, book=sp[1])
              for i, sp in enumerate(specs)]
    return TradePlan(plan_date=ASOF, signal_date=ASOF, strategy="test", strategy_version="0",
                     state=3, state_name="NEUTRAL", nav_basis={}, orders=orders,
                     account=account)


# DD giả: dict đúng shape run_due_diligence(as_dict=True)
def _ok(**kw):
    d = {"red_flags": [], "has_red_flag": False, "in_universe": True,
         "quality_flag": "QUALITY_OK", "data_date": "2026-10-30"}
    d.update(kw)
    return d


FAKE = {
    "TCH": _ok(quality_flag="FLOOR_FAIL"),                       # ca gốc 03/11
    "RTF": _ok(quality_flag="RATING_FAIL"),
    "UNK": _ok(quality_flag="UNKNOWN_FLOOR"),
    "DEAD": _ok(red_flags=["THANH_KHOAN_CHET"], has_red_flag=True),
    "OUT": _ok(red_flags=["NGOAI_UNIVERSE"], has_red_flag=True, in_universe=False,
               quality_flag=None),
    "ERR": {"error": "không có dữ liệu trong bq_cache/ticker", "red_flags": ["DD_KHONG_CHAY_DUOC"],
            "has_red_flag": True},
    "NAU": _ok(in_universe=None, quality_flag=None),             # universe_pit không đọc được
    "NAD": _ok(in_universe=None, quality_flag=None, red_flags=["THANH_KHOAN_CHET"],
               has_red_flag=True),
    "FPT": _ok(),
    "VCB": _ok(quality_flag=None),                                # in universe, flag None = sạch
    "JNK": _ok(red_flags=["KHONG_PHAI_MA_CO"], has_red_flag=True),  # mã lạ ngoài RED_FLAG_CODES
}
CALLS = []


def fake_run_dd(ticker, book, ctx, as_dict=False):
    CALLS.append((ticker, book, dict(ctx), as_dict))
    if ticker == "BOOM":
        raise RuntimeError("bq chết")
    return FAKE[ticker]


_REAL_DEPS = plan_mod._dd_flag_gate_deps


def use_fake():
    plan_mod._dd_flag_gate_deps = lambda: (fake_run_dd, dd.dd_flag_verdict)


def run(specs, account="SELFCHECK"):
    CALLS.clear()
    return filter_dd_flag_orders(mk_plan(specs, account))


def cascade(specs, account="SELFCHECK"):
    """Đúng thứ tự bot_execute: cổng cờ DD → net_offsetting_orders (10b kiểm thứ tự này tĩnh)."""
    CALLS.clear()
    pl, out = filter_dd_flag_orders(mk_plan(specs, account))
    pl, adj = net_offsetting_orders(pl)
    return [(o.ticker, o.side, o.qty, o.book) for o in pl.orders], out, adj


print("=== dd_flag_order_gate self-check ===")
use_fake()

# 1. Ca gốc TCH BAL FLOOR_FAIL
pl, out = run([("TCH", "BAL", "buy")])
check("TCH BAL buy FLOOR_FAIL ⇒ BLOCKED (ca gốc plan 03/11)",
      pl.orders == [] and len(out) == 1 and out[0]["action"] == "BLOCKED"
      and out[0]["codes"] == ["QF:FLOOR_FAIL"] and out[0]["qty_before"] == 1000, out)

# 2. Mọi book mua bị áp
for bk in ("BAL", "LAG", "CAPIT", "DC", None):
    pl, out = run([("TCH", bk, "buy")])
    check(f"book {bk!r} buy có cờ ⇒ BLOCKED", pl.orders == [] and out[0]["action"] == "BLOCKED")

# 3. Mọi loại cờ
for tk, code in (("RTF", "QF:RATING_FAIL"), ("UNK", "QF:UNKNOWN_FLOOR"),
                 ("DEAD", "THANH_KHOAN_CHET"), ("OUT", "NGOAI_UNIVERSE"),
                 ("NAD", "THANH_KHOAN_CHET")):
    pl, out = run([(tk, "LAG", "buy")])
    check(f"{tk} ⇒ BLOCKED codes chứa {code}",
          pl.orders == [] and out and out[0]["action"] == "BLOCKED" and code in out[0]["codes"], out)

# 4. Sạch ⇒ giữ, không bản ghi
pl, out = run([("FPT", "BAL", "buy"), ("VCB", "CAPIT", "buy")])
check("mã sạch (QUALITY_OK / quality_flag None trong universe) ⇒ GIỮ, 0 bản ghi",
      [o.ticker for o in pl.orders] == ["FPT", "VCB"] and out == [], out)
pl, out = run([("JNK", "BAL", "buy")])
check("red_flag lạ ngoài RED_FLAG_CODES KHÔNG tính là cờ", len(pl.orders) == 1 and out == [], out)

# 4b. Book PARK MIỄN (user 2026-11-03) — nhãn THẬT trong plan_*.json: "PARK" (PARK_ADD) và
#     "custom30V_parking" (NEUTRAL_park/PARK_ENTRY). Mã cờ vẫn được mua; không gọi DD, 0 bản ghi.
for bk in ("PARK", "custom30V_parking", "park"):
    pl, out = run([("TCH", bk, "buy")])
    check(f"PARK-1 book {bk!r} buy mã FLOOR_FAIL ⇒ GIỮ, 0 bản ghi, 0 lần gọi DD",
          len(pl.orders) == 1 and out == [] and CALLS == [], (out, CALLS))
for tk in ("DEAD", "OUT", "ERR"):
    pl, out = run([(tk, "PARK", "buy")])
    check(f"PARK-2 {tk} (cờ đỏ/lỗi DD) book PARK ⇒ GIỮ, không FAIL_OPEN", len(pl.orders) == 1 and out == [], out)
pl, out = run([("TCH", "CAPIT", "buy"), ("TCH", "BAL", "buy"), ("TCH", "LAG", "buy"),
               ("TCH", "PARK", "buy"), ("TCH", "custom30V_parking", "buy")])
check("PARK-3 CAPIT/BAL/LAG cùng mã cờ VẪN BLOCKED, 2 chân park giữ",
      sorted(o.book for o in pl.orders) == ["PARK", "custom30V_parking"]
      and sorted(a["book"] for a in out) == ["BAL", "CAPIT", "LAG"]
      and all(a["action"] == "BLOCKED" for a in out), out)
pl, out = run([("TCH", "BAL_PARKING_X", "buy"), ("TCH", "NOTPARK", "buy"), ("TCH", "PARKING", "buy")])
check("PARK-4 khớp TUYỆT ĐỐI: book chứa chữ PARK nhưng không phải 2 nhãn park ⇒ BLOCKED",
      pl.orders == [] and len(out) == 3, out)
# park đi qua netting: BUY PARK mã cờ + SELL LAG cùng mã ⇒ cổng giữ BUY PARK, netting ra 1 lệnh
sent, out, adj = cascade([("TCH", "PARK", "buy", 1000), ("TCH", "LAG", "sell", 300)])
check("PARK-5 gate→net: BUY PARK 1000 (mã cờ) + SELL LAG 300 ⇒ NET BUY 700, không BLOCKED",
      sent == [("TCH", "buy", 700, "PARK")] and out == [], (sent, out, adj))
# PARK + LAG cùng mã cờ: chân LAG chặn, chân PARK sống, không trốn vào lệnh NET
sent, out, adj = cascade([("TCH", "LAG", "buy", 500), ("TCH", "custom30V_parking", "buy", 200)])
check("PARK-6 LAG 500 BLOCKED + PARK 200 giữ ⇒ ra broker chỉ BUY 200 park",
      sent == [("TCH", "buy", 200, "custom30V_parking")]
      and [(a["action"], a["book"]) for a in out] == [("BLOCKED", "LAG")], (sent, out))

# 5. Lệnh BÁN không bao giờ bị chặn (và không gọi DD)
pl, out = run([("TCH", "BAL", "sell"), ("DEAD", "LAG", "sell"), ("ERR", "PARK", "sell")])
check("SELL mã có cờ / lỗi DD ⇒ GIỮ cả 3, 0 bản ghi, 0 lần gọi DD",
      len(pl.orders) == 3 and out == [] and CALLS == [], (out, CALLS))

# 6. DISCRETIONARY* chỉ cảnh báo
pl, out = run([("TCH", "DISCRETIONARY_SPECIAL", "buy"), ("DEAD", "discretionary", "buy")])
check("DISCRETIONARY* buy có cờ ⇒ GIỮ + WARN_DISCRETIONARY (không BLOCKED)",
      len(pl.orders) == 2 and [a["action"] for a in out] == ["WARN_DISCRETIONARY"] * 2, out)
pl, out = run([("ERR", "DISCRETIONARY_SPECIAL", "buy")])
check("DISCRETIONARY lỗi DD ⇒ giữ, KHÔNG FAIL_OPEN (không phải cổng chặn ở đó)",
      len(pl.orders) == 1 and out == [], out)

# 7. PROBE miễn — CHỈ trên account paper `main`
pl, out = run([("TCH", "PROBE", "buy")], account="main")
check("PROBE buy account=main ⇒ GIỮ, không gọi DD",
      len(pl.orders) == 1 and out == [] and CALLS == [])
for acct in ("SpaceX", "ZaloPay", "SELFCHECK", ""):
    pl, out = run([("TCH", "PROBE", "buy")], account=acct)
    check(f"PROBE buy account={acct!r} (không phải main) ⇒ BLOCKED như book thường",
          pl.orders == [] and [a["action"] for a in out] == ["BLOCKED"], out)
pl, out = run([("TCH", "BAL", "buy")], account="main")
check("account=main nhưng book BAL ⇒ vẫn BLOCKED (miễn trừ chỉ cho PROBE)",
      pl.orders == [] and out[0]["action"] == "BLOCKED", out)

# 8. Fail-mode
pl, out = run([("ERR", "BAL", "buy"), ("TCH", "BAL", "buy"), ("FPT", "LAG", "buy")])
acts = [a["action"] for a in out]
check("DD lỗi 1 mã ⇒ mã đó GIỮ + FAIL_OPEN; mã cờ khác vẫn BLOCKED; mã sạch giữ",
      [o.ticker for o in pl.orders] == ["ERR", "FPT"] and acts == ["BLOCKED", "FAIL_OPEN"]
      and "ERR[BAL]" in out[-1]["reason"], out)
pl, out = run([("NAU", "BAL", "buy")])
check("universe_pit không đọc được (in_universe None, không cờ đỏ) ⇒ FAIL_OPEN, KHÔNG im lặng CLEAN",
      len(pl.orders) == 1 and [a["action"] for a in out] == ["FAIL_OPEN"], out)
pl, out = run([("BOOM", "BAL", "buy")])
check("run_dd raise ⇒ GIỮ + FAIL_OPEN", len(pl.orders) == 1 and out[0]["action"] == "FAIL_OPEN")
plan_mod._dd_flag_gate_deps = lambda: (_ for _ in ()).throw(ImportError("no dd"))
pl, out = run([("TCH", "BAL", "buy"), ("FPT", "LAG", "buy")])
check("không nạp được lớp DD ⇒ GIỮ NGUYÊN plan + 1 FAIL_OPEN",
      len(pl.orders) == 2 and len(out) == 1 and out[0]["action"] == "FAIL_OPEN", out)
use_fake()

# 9. Hợp đồng gọi DD
pl, out = run([("FPT", "lag", "buy"), ("FPT", "LAG", "buy"), ("FPT", "BAL", "buy")])
check("DD gọi 1 lần / (mã, book chuẩn hoá hoa), as_dict, skip_dcf+skip_corp_flags, asof=plan_date",
      sorted((c[0], c[1]) for c in CALLS) == [("FPT", "BAL"), ("FPT", "LAG")]
      and all(c[3] and c[2].get("skip_dcf") and c[2].get("skip_corp_flags")
              and c[2]["asof"] == ASOF and "est_value_vnd" not in c[2] for c in CALLS), CALLS)
pl, out = run([])
check("plan rỗng ⇒ không lỗi", pl.orders == [] and out == [])

# 10. dd_flag_verdict trên các nhánh trả sớm THẬT của run_due_diligence (không fake)
plan_mod._dd_flag_gate_deps = _REAL_DEPS
_orig = dd._latest_row
dd._latest_row = lambda t, a: None
st = dd.dd_flag_verdict(dd.run_due_diligence("ZZZZ", "BAL", {"asof": ASOF, "skip_dcf": True},
                                             as_dict=True))
check("run_due_diligence thật, thiếu dòng ⇒ verdict UNKNOWN", st[0] == "UNKNOWN", st)
dd._latest_row = lambda t, a: (_ for _ in ()).throw(OSError("parquet hỏng"))
st = dd.dd_flag_verdict(dd.run_due_diligence("ZZZZ", "BAL", {"asof": ASOF, "skip_dcf": True},
                                             as_dict=True))
check("run_due_diligence thật, raise bên trong ⇒ verdict UNKNOWN", st[0] == "UNKNOWN", st)
dd._latest_row = _orig
check("dd_flag_verdict(None) ⇒ UNKNOWN", dd.dd_flag_verdict(None)[0] == "UNKNOWN")

# 10b. Dây nối cascade: bot_execute gọi cổng SAU signal_holds, TRƯỚC pre_net_refs/netting
# (arch-review vòng 1: cổng sau netting làm mất SELL / lọt MUA qua chuyển nội bộ). Tĩnh —
# bot_execute import broker/OTP nên không chạy main() offline được.
src = open(os.path.join(CODE_ROOT, "bot_execute.py"), encoding="utf-8").read()
i_hold = src.find("plan, holds_blocked = filter_signal_holds(plan)")
i_dd = src.find("plan, dd_blocked = filter_dd_flag_orders(plan)")
i_ref = src.find('pre_net_refs[p["label"]] = {o.ticker: o.ref_price for o in plan.orders}')
i_net = src.find("plan, net_adj = net_offsetting_orders(plan)")
i_lev = src.find("plan, lever_adj = apply_capit_lever(")
check("bot_execute: signal_holds < dd_flag < pre_net_refs < netting < lever trong cascade",
      0 < i_hold < i_dd < i_ref < i_net < i_lev, (i_hold, i_dd, i_ref, i_net, i_lev))
check("bot_execute: FAIL_OPEN của cổng đi qua _notify_failopen (Telegram+Discord)",
      '_notify_failopen(p["label"], "cờ DD' in src)
_blk = src[i_dd:i_ref]
check("bot_execute: BLOCKED/WARN gom 1 tin tóm tắt/account qua _notify_dd_flag_summary",
      "_notify_dd_flag_summary(p[\"label\"], plan_date, _dd_lines)" in _blk
      and _blk.count("_dd_lines.append(") == 2, _blk[-400:])
_i_fn = src.find("def _notify_dd_flag_summary(")
check("_notify_dd_flag_summary gửi qua _notify_trading_daily (Discord+Telegram)",
      _i_fn > 0 and "_notify_trading_daily(" in src[_i_fn:src.find("\ndef ", _i_fn + 10)])

# 10c. Ca NETTING (gate → net đúng thứ tự cascade) — tái hiện probe arch-review vòng 1
use_fake()
sent, out, adj = cascade([("TCH", "BAL", "buy", 1000), ("TCH", "DISCRETIONARY_SPECIAL", "sell", 300)])
check("NET-A: BUY BAL 1000 cờ + SELL DISCRETIONARY 300 ⇒ SELL 300 SỐNG tới broker",
      sent == [("TCH", "sell", 300, "DISCRETIONARY_SPECIAL")]
      and [(a["action"], a["qty_before"]) for a in out] == [("BLOCKED", 1000)], (sent, out))
sent, out, adj = cascade([("TCH", "LAG", "buy", 300), ("TCH", "custom30V_parking", "sell", 1000)])
check("NET-B: BUY LAG 300 cờ + SELL PARK 1000 ⇒ SELL đủ 1000, MUA không đi qua chuyển nội bộ",
      sent == [("TCH", "sell", 1000, "custom30V_parking")] and adj == []
      and [(a["action"], a["book"], a["qty_before"]) for a in out] == [("BLOCKED", "LAG", 300)],
      (sent, out, adj))
sent, out, adj = cascade([("TCH", "LAG", "buy", 500), ("TCH", "DISCRETIONARY_SPECIAL", "buy", 2000),
                          ("TCH", "PARK", "sell", 100)])
check("NET-C: chân LAG 500 cờ KHÔNG trốn vào lệnh NET nhãn DISCRETIONARY (NET = 2000−100)",
      sent == [("TCH", "buy", 1900, "DISCRETIONARY_SPECIAL")]
      and sorted((a["action"], a["book"], a["qty_before"]) for a in out)
      == [("BLOCKED", "LAG", 500), ("WARN_DISCRETIONARY", "DISCRETIONARY_SPECIAL", 2000)],
      (sent, out))

# 11. --live: replay DD THẬT trên plan gốc 03/11 (bản có TCH)
if "--live" in sys.argv:
    from trading_bot.plan import load_plan  # noqa: F401
    wc = os.environ.get("TRADING_BOT_RUNTIME_ROOT", "/home/trido/thanhdt/WorkingClaude")
    for acct in ("SpaceX", "ZaloPay"):
        bak = os.path.join(wc, "data", "trade_plans", f"plan_{acct}_2026-11-03.json.bak_20261102_2315")
        raw = json.load(open(bak))
        tp = TradePlan(plan_date=raw["plan_date"], signal_date=raw.get("signal_date", ""),
                       strategy="replay", strategy_version="0", state=0, state_name="",
                       nav_basis={}, orders=[PlannedOrder(**{k: v for k, v in o.items()
                                                             if k in PlannedOrder.__dataclass_fields__})
                                             for o in raw["orders"]], account=acct)
        before = [(o.ticker, o.book, o.side) for o in tp.orders]
        pl, out = filter_dd_flag_orders(tp)
        after = [(o.ticker, o.book, o.side) for o in pl.orders]
        removed = [x for x in before if x not in after]
        print(f"  [live {acct}] trước {len(before)} lệnh → sau {len(after)}; bỏ {removed}; "
              f"bản ghi {[(a['ticker'], a['action'], a['codes']) for a in out]}")
        check(f"live {acct}: TCH buy bị BLOCKED với QF:FLOOR_FAIL",
              any(a["ticker"] == "TCH" and a["action"] == "BLOCKED" and "QF:FLOOR_FAIL" in a["codes"]
                  for a in out), out)
        check(f"live {acct}: mọi lệnh SELL giữ nguyên",
              [x for x in before if x[2] == "sell"] == [x for x in after if x[2] == "sell"])
        check(f"live {acct}: không FAIL_OPEN (nguồn DD đọc được)",
              not any(a["action"] == "FAIL_OPEN" for a in out), out)
        # Ca TỔNG HỢP có SELL (plan .bak không có lệnh SELL ⇒ check SELL ở trên rỗng): thêm SELL
        # mã cờ TCH + SELL mã sạch đầu tiên, DD THẬT, rồi chạy gate → net như cascade.
        tp2 = TradePlan(plan_date=raw["plan_date"], signal_date="", strategy="replay",
                        strategy_version="0", state=0, state_name="", nav_basis={},
                        orders=[PlannedOrder(**{k: v for k, v in o.items()
                                                if k in PlannedOrder.__dataclass_fields__})
                                for o in raw["orders"]], account=acct)
        clean = next((o.ticker for o in tp2.orders if o.ticker != "TCH"), "FPT")
        tp2.orders += [PlannedOrder(id="SYN-SELL-TCH", ticker="TCH", side="sell", qty=100,
                                    ref_price=20000.0, book="custom30V_parking")]
        if clean:
            tp2.orders += [PlannedOrder(id=f"SYN-SELL-{clean}", ticker=clean, side="sell", qty=100,
                                        ref_price=20000.0, book="custom30V_parking")]
        pl2, out2 = filter_dd_flag_orders(tp2)
        sells2 = [(o.ticker, o.qty) for o in pl2.orders if o.side == "sell"]
        pl2, _ = net_offsetting_orders(pl2)
        sent2 = [(o.ticker, o.side, o.qty) for o in pl2.orders if o.ticker == "TCH"]
        print(f"  [live {acct} +SELL tổng hợp] sell sau cổng {sells2}; TCH ra broker {sent2}")
        check(f"live {acct} +SELL tổng hợp: cả SELL TCH (mã cờ) lẫn SELL {clean} sống qua cổng",
              ("TCH", 100) in sells2 and (clean is None or (clean, 100) in sells2), sells2)
        check(f"live {acct} +SELL tổng hợp: sau gate→net, TCH ra broker = SELL 100 nguyên vẹn",
              sent2 == [("TCH", "sell", 100)], sent2)

print(f"\n=== {PASS} PASS / {FAIL} FAIL ===")
sys.exit(1 if FAIL else 0)
