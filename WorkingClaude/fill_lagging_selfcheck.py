# -*- coding: utf-8 -*-
"""Self-check cho cảnh báo bus `fill_lagging` (executor._check_fill_lagging).

Lỗi gốc (code-review 2026-11-15, cq-2026-11-15-hard-boundary): kiểm tra cộng
`p.get("qty", 0)` trên `state["parents"]`, mà parent state KHÔNG có khoá `qty`
⇒ total_plan=0 ⇒ fill_rate=1.0 ⇒ cảnh báo 11:00 không bao giờ nổ. Fix: lấy khối lượng
kế hoạch từ `plan.orders[].qty`.

Không đụng broker/bus thật: MIKE_BOT_TEST_MODE=1 + MIKE_BOT_TEST_EVENT_SINK (file tạm)
để assert event LẼ RA đã bắn. Executor giả = SimpleNamespace (hàm chỉ đọc
`.state`, `.plan.orders`, `.label`).

Mutant: nạp lại executor.py với dòng tính total_plan bị đổi về bản lỗi ⇒ ca "fill chậm"
PHẢI hết nổ (chứng minh check bắt được đúng lỗi này).

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


def _exec(fills, qtys=(1000, 2000), label="T", orphan_filled=None):
    orders = [SimpleNamespace(id=f"BUY-X{i}", qty=q) for i, q in enumerate(qtys)]
    parents = {o.id: {"filled": f, "done": False, "children": []} for o, f in zip(orders, fills)}
    if orphan_filled is not None:   # parent chỉ còn trong state (không còn trong plan)
        parents["ORPHAN"] = {"filled": orphan_filled, "done": True, "children": []}
    return SimpleNamespace(label=label, state={"parents": parents},
                           plan=SimpleNamespace(orders=orders))


T1100 = dt.datetime(2026, 11, 16, 11, 0)
T1059 = dt.datetime(2026, 11, 16, 10, 59)


def run_cases(mod, tag):
    """Trả về dict kết quả các ca để so bản fix vs mutant."""
    r = {}
    _reset()
    e = _exec([300, 0])                      # 300/3000 = 10% < 40%
    mod._check_fill_lagging([e], "MORNING", T1100)
    ev = _events()
    r["slow_fires"] = len(ev) == 1 and ev[0]["topic"] == "fill_lagging" \
        and ev[0]["payload"]["fill_rate_pct"] == 10.0 and ev[0]["payload"]["account"] == "T"
    # chỉ nổ 1 lần
    mod._check_fill_lagging([e], "MORNING", T1100)
    r["once"] = len(_events()) == 1
    _reset()
    mod._check_fill_lagging([_exec([1000, 2000])], "MORNING", T1100)   # đủ 100%
    r["full_silent"] = len(_events()) == 0
    _reset()
    mod._check_fill_lagging([_exec([600, 600])], "MORNING", T1100)     # 40% — biên, không nổ
    r["boundary_silent"] = len(_events()) == 0
    _reset()
    mod._check_fill_lagging([_exec([0, 0])], "MORNING", T1059)         # trước 11:00
    mod._check_fill_lagging([_exec([0, 0])], "AFTERNOON", T1100)       # sai phase
    r["gate_silent"] = len(_events()) == 0
    _reset()
    # parent mồ côi fill lớn không được "che" fill chậm của plan hiện tại
    mod._check_fill_lagging([_exec([0, 0], orphan_filled=10**6)], "MORNING", T1100)
    r["orphan_ignored"] = len(_events()) == 1
    _reset()
    mod._check_fill_lagging([_exec([0, 0], label="A"), _exec([3000, 0], label="B")],
                            "MORNING", T1100)
    r["per_account"] = [x["payload"]["account"] for x in _events()] == ["A"]
    return r


real = run_cases(EX, "fix")
for k, v in real.items():
    check(f"fix: {k}", v)

# ── Mutant: khôi phục biểu thức lỗi ────────────────────────────────────────────
src = open(EX.__file__, encoding="utf-8").read()
GOOD = "total_plan = sum(plan_qty.values())"
BAD = 'total_plan = sum(ps[pid].get("qty", 0) for pid in plan_qty)'
check("mutant: dòng fix tồn tại đúng 1 lần", src.count(GOOD) == 1)
spec = importlib.util.spec_from_loader("trading_bot.executor_mutant", loader=None)
mut = importlib.util.module_from_spec(spec)
mut.__dict__.update(__file__=EX.__file__, __package__="trading_bot")
exec(compile(src.replace(GOOD, BAD), EX.__file__, "exec"), mut.__dict__)
m = run_cases(mut, "mutant")
check("mutant: ca fill chậm KHÔNG còn nổ (lỗi gốc tái hiện)", m["slow_fires"] is False)
check("mutant: ca đủ fill vẫn im (mutant không đổi nhánh im)", m["full_silent"] is True)

# bus thật không bị chạm: event chỉ vào sink
check("test-mode guard bật", os.environ.get("MIKE_BOT_TEST_MODE") == "1")
os.unlink(_SINK)
print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAIL'}")
sys.exit(1 if FAILS else 0)
