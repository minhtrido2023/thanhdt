# -*- coding: utf-8 -*-
"""Self-check cho cảnh báo bus `fill_lagging` (executor._check_fill_lagging).

Lỗi gốc (code-review 2026-11-15, cq-2026-11-15-hard-boundary): kiểm tra cộng
`p.get("qty", 0)` trên `state["parents"]`, mà parent state KHÔNG có khoá `qty`
⇒ total_plan=0 ⇒ fill_rate=1.0 ⇒ cảnh báo 11:00 không bao giờ nổ. Fix: lấy khối lượng
kế hoạch từ `plan.orders[].qty`.

Vòng 2 (arch-review 2026-11-16): chỉ tính parent ĐÃ QUA HẾT cửa sổ thực thi của nó
(`Executor._fill_lag_due` — HYBRID LIVE hoãn lệnh mua tới 11:00-13:45, nên ngày chỉ-mua
không được nổ lúc 11:00), theo GIÁ TRỊ (`_parent_fill_value`, chung với write_report), lỗi
của 1 account chỉ ghi journal `FILL_LAG_CHECK_ERROR`.

Không đụng broker/bus thật: MIKE_BOT_TEST_MODE=1 + MIKE_BOT_TEST_EVENT_SINK (file tạm)
để assert event LẼ RA đã bắn. Executor = `object.__new__(Executor)` (không __init__, không
broker) để chạy đúng các method lịch thật; cfg = `config.DEFAULTS` + override cổng.

Mutant: nạp lại executor.py với từng đột biến (lỗi gốc, 0.0/1.0, bỏ lọc state, bỏ cổng
lịch, đếm CP, bỏ try/except, HYBRID due sớm) ⇒ mỗi mutant PHẢI làm hỏng ≥1 ca.

Run: python fill_lagging_selfcheck.py   (exit 0 = all pass)
"""
import datetime as dt
import importlib.util
import json
import os
import sys
import tempfile
from types import SimpleNamespace

os.environ["MIKE_BOT_TEST_MODE"] = "1"   # §5b — trước khi import executor
_SINK = tempfile.NamedTemporaryFile(prefix="fill_lag_sink_", suffix=".jsonl", delete=False).name
os.environ["MIKE_BOT_TEST_EVENT_SINK"] = _SINK
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from trading_bot import executor as EX  # noqa: E402
from trading_bot.config import DEFAULTS as CFG_DEFAULT  # noqa: E402

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def _events():
    with open(_SINK, encoding="utf-8") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def _reset():
    open(_SINK, "w").close()


HYB = {"mode": "live", "fill_timing_enabled": True, "fill_timing_live_gate": False,
       "fill_timing_hybrid_enabled": True, "fill_timing_hybrid_live_gate": False}
UNIFORM = {"mode": "live", "fill_timing_enabled": False}
# HYBRID tắt (cổng LIVE đóng) nhưng fill-timing cơ bản LIVE — lịch cửa sổ buy 10:45-11:15
BASE = {"mode": "live", "fill_timing_enabled": True, "fill_timing_live_gate": False,
        "fill_timing_hybrid_enabled": True, "fill_timing_hybrid_live_gate": True}


def _cfg(over):
    c = dict(CFG_DEFAULT)
    c.update(over)   # block giờ HYBRID/cửa sổ lấy từ DEFAULTS thật (không chép số)
    return c


def _exec(mod, fills, qtys=(1000, 2000), sides=("buy", "buy"), px=(10_000, 10_000),
          label="T", orphan_filled=None, cfg=UNIFORM, missing_state=()):
    """Executor THẬT (`object.__new__`, không __init__/broker) ⇒ chạy đúng `_fill_lag_due`,
    `_hybrid_active`, `_hybrid_sched` của module đang test (fix hoặc mutant)."""
    orders = [SimpleNamespace(id=f"{sd.upper()}-X{i}", qty=q, side=sd, ref_price=p,
                              urgency="normal", value=q * p)
              for i, (q, sd, p) in enumerate(zip(qtys, sides, px))]
    parents = {}
    for o, f in zip(orders, fills):
        if o.id in missing_state:     # có trong plan nhưng CHƯA có trong state
            continue
        parents[o.id] = {"filled": f, "done": False,
                         "children": [{"filled": f, "price": o.ref_price}] if f else []}
    if orphan_filled is not None:   # parent chỉ còn trong state (không còn trong plan)
        parents["ORPHAN"] = {"filled": orphan_filled, "done": True,
                             "children": [{"filled": orphan_filled, "price": 10_000}]}
    e = object.__new__(mod.Executor)
    e.label, e.cfg = label, _cfg(cfg)
    e.state = {"parents": parents}
    e.plan = SimpleNamespace(orders=orders)
    e.journal = []
    e._journal = lambda ev, o=None, **kw: e.journal.append((ev, kw.get("note", "")))
    return e


def T(h, m):
    return dt.datetime(2026, 11, 16, h, m)


def run_cases(mod):
    """Trả về dict kết quả các ca để so bản fix vs mutant."""
    r = {}
    _reset()
    e = _exec(mod, [300, 0])                         # 300/3000 = 10% < 40%
    mod._check_fill_lagging([e], "MORNING", T(11, 0))
    ev = _events()
    r["slow_fires"] = len(ev) == 1 and ev[0]["topic"] == "fill_lagging" \
        and ev[0]["payload"]["fill_rate_pct"] == 10.0 and ev[0]["payload"]["account"] == "T"
    mod._check_fill_lagging([e], "MORNING", T(11, 0))
    r["once"] = len(_events()) == 1
    _reset()
    mod._check_fill_lagging([_exec(mod, [1000, 2000])], "MORNING", T(11, 0))   # 100%
    r["full_silent"] = len(_events()) == 0
    _reset()
    mod._check_fill_lagging([_exec(mod, [600, 600])], "MORNING", T(11, 0))     # 40% — biên
    r["boundary_silent"] = len(_events()) == 0
    _reset()
    mod._check_fill_lagging([_exec(mod, [0, 0])], "MORNING", T(10, 59))        # trước 11:00
    mod._check_fill_lagging([_exec(mod, [0, 0])], "ATC", T(14, 35))           # sai phase
    r["gate_silent"] = len(_events()) == 0
    _reset()
    # theo GIÁ TRỊ, không theo số CP: 1000 CP rẻ đã khớp đủ (10tr), 1000 CP đắt chưa (90tr)
    # ⇒ 50% số CP nhưng 10% giá trị ⇒ PHẢI nổ.
    mod._check_fill_lagging([_exec(mod, [1000, 0], qtys=(1000, 1000), px=(10_000, 90_000))],
                            "MORNING", T(11, 0))
    ev = _events()
    r["value_weighted"] = len(ev) == 1 and ev[0]["payload"]["fill_rate_pct"] == 10.0
    _reset()
    # parent mồ côi fill lớn không được "che" fill chậm của plan hiện tại
    mod._check_fill_lagging([_exec(mod, [0, 0], orphan_filled=10**6)], "MORNING", T(11, 0))
    r["orphan_ignored"] = len(_events()) == 1
    _reset()
    # CHỈ có parent mồ côi trong state (không parent nào của plan) ⇒ không có gì để đo ⇒ im
    e = _exec(mod, [0, 0], orphan_filled=5, missing_state=("BUY-X0", "BUY-X1"))
    mod._check_fill_lagging([e], "MORNING", T(11, 0))
    r["only_orphan_silent"] = len(_events()) == 0 and not e.journal
    _reset()
    # lệnh có trong plan nhưng CHƯA có trong state: bỏ qua, không lỗi, không journal lỗi
    e = _exec(mod, [3000, 0], qtys=(3000, 1000), missing_state=("BUY-X1",))
    mod._check_fill_lagging([e], "MORNING", T(11, 0))
    r["missing_state_skipped"] = len(_events()) == 0 and not e.journal
    _reset()
    mod._check_fill_lagging([_exec(mod, [0, 0], label="A"), _exec(mod, [3000, 0], label="B")],
                            "MORNING", T(11, 0))
    r["per_account"] = [x["payload"]["account"] for x in _events()] == ["A"]
    # ── HYBRID LIVE: ngày chỉ-mua, 11:00 ⇒ lệnh mua còn block phía trước ⇒ KHÔNG nổ ────────
    _reset()
    e = _exec(mod, [0, 0], cfg=HYB)
    for hm in ((11, 0), (11, 20), (13, 0), (13, 44)):
        mod._check_fill_lagging([e], "MORNING" if hm[0] < 12 else "AFTERNOON", T(*hm))
    r["hybrid_buyonly_silent_until_1345"] = len(_events()) == 0
    mod._check_fill_lagging([e], "AFTERNOON", T(13, 45))     # hết block mua ⇒ đo
    r["hybrid_buy_fires_after_1345"] = len(_events()) == 1
    _reset()
    # HYBRID: bán chậm thật lúc 11:00 (block bán hết 10:15) ⇒ nổ dù lệnh mua chưa due
    e = _exec(mod, [0, 0], sides=("sell", "buy"), cfg=HYB)
    mod._check_fill_lagging([e], "MORNING", T(11, 0))
    ev = _events()
    r["hybrid_slow_sell_fires_1100"] = len(ev) == 1 and ev[0]["payload"]["n_due"] == 1
    _reset()
    # HYBRID: bán đủ, mua 0 lúc 11:00 ⇒ chỉ tính bán (100%) ⇒ im
    mod._check_fill_lagging([_exec(mod, [1000, 0], sides=("sell", "buy"), cfg=HYB)],
                            "MORNING", T(11, 0))
    r["hybrid_sell_done_buy_pending_silent"] = len(_events()) == 0
    # ── fill-timing CƠ BẢN (HYBRID đóng cổng LIVE): mua due sau 11:15 ───────────────────────
    _reset()
    e = _exec(mod, [0, 0], cfg=BASE)
    mod._check_fill_lagging([e], "MORNING", T(11, 0))
    r["base_buy_silent_1100"] = len(_events()) == 0
    mod._check_fill_lagging([e], "MORNING", T(11, 15))
    r["base_buy_fires_1115"] = len(_events()) == 1
    # ── 1 account ném lỗi ⇒ không lan ra ngoài, account khác vẫn được kiểm, journal ghi lỗi ─
    _reset()
    bad = _exec(mod, [0, 0], label="BAD")
    bad.plan = SimpleNamespace(orders=None)                 # iterate None ⇒ TypeError
    good = _exec(mod, [0, 0], label="GOOD")
    try:
        mod._check_fill_lagging([bad, good], "MORNING", T(11, 0))
        raised = False
    except Exception:
        raised = True
    r["error_contained"] = (not raised and [x["payload"]["account"] for x in _events()] == ["GOOD"]
                            and [j[0] for j in bad.journal] == ["FILL_LAG_CHECK_ERROR"])
    return r


def _load_mutant(old, new):
    src = open(EX.__file__, encoding="utf-8").read()
    if src.count(old) != 1:
        return None
    spec = importlib.util.spec_from_loader("trading_bot.executor_mutant", loader=None)
    mut = importlib.util.module_from_spec(spec)
    mut.__dict__.update(__file__=EX.__file__, __package__="trading_bot")
    exec(compile(src.replace(old, new), EX.__file__, "exec"), mut.__dict__)
    return mut


real = run_cases(EX)
for k, v in real.items():
    check(f"fix: {k}", v)

# ── Mutant: mỗi mutant PHẢI làm hỏng ít nhất 1 ca (mutant sống = test thiếu) ─────────────
MUTANTS = [
    ("lỗi gốc: qty từ parent state",
     "total_plan = sum(o.value for o in due)",
     'total_plan = sum(ps[o.id].get("qty", 0) for o in due)'),
    ("không có gì due ⇒ 0.0 thay vì 1.0",
     "fill_rate = total_fill / total_plan if total_plan else 1.0",
     "fill_rate = total_fill / total_plan if total_plan else 0.0"),
    ("bỏ lọc 'o.id in ps'",
     "if o.id in ps and e._fill_lag_due(o, now)]",
     "if e._fill_lag_due(o, now)]"),
    ("bỏ cổng lịch (kiểm mọi parent lúc 11:00 — lỗi vòng 1)",
     "if o.id in ps and e._fill_lag_due(o, now)]",
     "if o.id in ps]"),
    ("theo số CP thay vì giá trị",
     "total_plan = sum(o.value for o in due)",
     "total_plan = sum(o.qty for o in due) or 0; total_fill = sum(ps[o.id]['filled'] for o in due)"),
    ("bỏ try/except",
     "        except Exception as ex:\n            try:\n                e._journal(\"FILL_LAG_CHECK_ERROR\"",
     "        except ZeroDivisionError as ex:\n            try:\n                e._journal(\"FILL_LAG_CHECK_ERROR\""),
    ("HYBRID: due ngay cả khi còn block",
     "return self._hybrid_sched(o, now)[1] == 0",
     "return True"),
]
for name, old, new in MUTANTS:
    mut = _load_mutant(old, new)
    if mut is None:
        check(f"mutant [{name}]: điểm đột biến tồn tại đúng 1 lần", False)
        continue
    try:
        m = run_cases(mut)
        killed = [k for k, v in m.items() if v != real[k]]
    except Exception as ex:          # ném lỗi ra ngoài cũng là bị giết
        killed = [f"raised {type(ex).__name__}"]
    check(f"mutant [{name}] bị giết ({', '.join(killed[:3]) or 'SỐNG'})", bool(killed))

# bus thật không bị chạm: event chỉ vào sink
check("test-mode guard bật", os.environ.get("MIKE_BOT_TEST_MODE") == "1")
os.unlink(_SINK)
print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAIL'}")
sys.exit(1 if FAILS else 0)
