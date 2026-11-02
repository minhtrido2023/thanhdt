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
from trading_bot.plan import PlannedOrder, TradePlan, filter_dd_flag_orders  # noqa: E402

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


def mk_plan(specs):
    orders = [PlannedOrder(id=f"{sd.upper()}-{tk}-{i:02d}", ticker=tk, side=sd, qty=1000,
                           ref_price=20000.0, book=bk)
              for i, (tk, bk, sd) in enumerate(specs)]
    return TradePlan(plan_date=ASOF, signal_date=ASOF, strategy="test", strategy_version="0",
                     state=3, state_name="NEUTRAL", nav_basis={}, orders=orders,
                     account="SELFCHECK")


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


def run(specs):
    CALLS.clear()
    return filter_dd_flag_orders(mk_plan(specs))


print("=== dd_flag_order_gate self-check ===")
use_fake()

# 1. Ca gốc TCH BAL FLOOR_FAIL
pl, out = run([("TCH", "BAL", "buy")])
check("TCH BAL buy FLOOR_FAIL ⇒ BLOCKED (ca gốc plan 03/11)",
      pl.orders == [] and len(out) == 1 and out[0]["action"] == "BLOCKED"
      and out[0]["codes"] == ["QF:FLOOR_FAIL"] and out[0]["qty_before"] == 1000, out)

# 2. Mọi book mua bị áp
for bk in ("BAL", "LAG", "CAPIT", "PARK", "DC", None):
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
pl, out = run([("FPT", "BAL", "buy"), ("VCB", "PARK", "buy")])
check("mã sạch (QUALITY_OK / quality_flag None trong universe) ⇒ GIỮ, 0 bản ghi",
      [o.ticker for o in pl.orders] == ["FPT", "VCB"] and out == [], out)
pl, out = run([("JNK", "BAL", "buy")])
check("red_flag lạ ngoài RED_FLAG_CODES KHÔNG tính là cờ", len(pl.orders) == 1 and out == [], out)

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

# 7. PROBE miễn hẳn
pl, out = run([("TCH", "PROBE", "buy")])
check("PROBE buy ⇒ GIỮ, không gọi DD", len(pl.orders) == 1 and out == [] and CALLS == [])

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

# 10b. Dây nối cascade: bot_execute gọi cổng SAU governance, TRƯỚC lever (tĩnh — bot_execute
# import broker/OTP nên không chạy main() offline được)
src = open(os.path.join(CODE_ROOT, "bot_execute.py"), encoding="utf-8").read()
i_gov = src.find("plan, gov_blocked = filter_lag_governance_orders(plan)")
i_dd = src.find("plan, dd_blocked = filter_dd_flag_orders(plan)")
i_lev = src.find("plan, lever_adj = apply_capit_lever(")
check("bot_execute: governance < dd_flag < lever trong cascade",
      0 < i_gov < i_dd < i_lev, (i_gov, i_dd, i_lev))
check("bot_execute: FAIL_OPEN của cổng đi qua _notify_failopen (Telegram+Discord)",
      '_notify_failopen(p["label"], "cờ DD' in src)

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

print(f"\n=== {PASS} PASS / {FAIL} FAIL ===")
sys.exit(1 if FAIL else 0)
