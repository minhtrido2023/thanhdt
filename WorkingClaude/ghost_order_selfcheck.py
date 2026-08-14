# -*- coding: utf-8 -*-
"""Regression self-check for the ghost-order idempotency guard (2nd independent defense
beyond fcntl.flock — see concurrent_lock_selfcheck.py for the 1st).

Incident 2026-07-02 root cause was TWO CONCURRENT bot_execute.py processes; flock now
blocks that (concurrent_lock_selfcheck.py). The residual gap flagged by quant-skeptic
(2026-07-02T05:29 VERIFY) is SEQUENTIAL: if a process is killed AFTER broker.place_order()
succeeds but BEFORE _save_state() persists that fact (crash/OOM/reboot), the order exists
for real at the broker but state.json doesn't know it — a later run (even holding the lock
correctly) would place ANOTHER order for the "missing" qty. DNSE's API has no client-supplied
idempotency key, so the broker itself can't dedupe.

Fix (Executor._ghost_tickers, executor.py): every step() cross-checks the broker's live
order list (already fetched for _sync_fills) against state's known child oids. Any broker
order for a plan ticker that isn't in state AND has filled_qty>0 or is still open is a
"ghost" — _place_slices/_atc_sweep then SKIP that ticker (fail-safe pause, same class as
WAIT_CASH/WAIT_QUOTA) instead of guessing how to merge it into state. A human investigates.
Also: _save_state() now runs immediately after each successful place_order (not just once at
the end of step()), shrinking the crash window itself.

Two review rounds since: quant-skeptic (verify_finding.sh, checks A-H below cover its
killer objection on poll_orders() failing open). A second, independent third-party review
(2026-07-02) verified the mechanism against real DNSE data and found 2 more gaps, both
fixed same round (checks I-J): _save_state() wasn't atomic (tmp+os.replace added), and
PaperBroker.poll_orders() built OrderUpdate with raw=None so paper trading could never
rehearse the guard (now passes raw={"symbol": ...} matching the real broker's shape).

Run: python ghost_order_selfcheck.py   (exit 0 = all pass)
"""
import glob
import os
import sys

# Test-mode: KHÔNG cho Executor._publish_bot_event ghi event GIẢ vào bus production
# (retro-2026-08-07 Pattern 1 — 4 lần tái diễn 08-03/04/05/07). Xem coding_guidelines §5.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot.brokers import OrderUpdate  # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan  # noqa: E402
from trading_bot.executor import Executor  # noqa: E402
from trading_bot.config import load_config, EXEC_DIR  # noqa: E402

# Executor.__init__ eagerly loads state.json from the DEFAULT (account, plan_date) path
# BEFORE make_executor() below gets a chance to redirect state_file to a tmpdir — so a
# stale file left by an EARLIER run of this (or any other) selfcheck sharing the same
# account tag corrupts this run's starting state. Found 2026-07-06 while adding the
# excluded_tickers feature: several selfchecks failed with KeyError after repeated runs.
# Fix: unique per-file tag + wipe any leftover fixture before each run (same pattern as
# concurrent_lock_selfcheck.py's TAG cleanup).
TAG = "selfcheck-ghost"
for f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(f)

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


class _NullBroker:
    """Never actually called in this self-check; place_order raises loudly if the
    ghost guard fails to skip (that IS the assertion)."""
    name = "null"

    def get_quote(self, *a, **k):
        raise AssertionError("get_quote should not be reached — ghost guard must skip first")

    def place_order(self, *a, **k):
        raise AssertionError("place_order called on a GHOSTED ticker — guard failed!")

    def cancel_order(self, *a, **k):
        return None

    def get_cash(self):
        return 10**12

    def poll_orders(self):
        return {}


def make_executor(tmpdir, orders, cfg_over=None, broker=None):
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=orders,
                     account=TAG, created_at="2099-01-01T00:00:00")
    cfg = load_config()
    # HYBRID fill-timing GHIM TẮT làm nền (cfg_over vẫn bật lại được — nhóm K dùng).
    # Vì sao: bộ này đo LƯỚI GHOST (idempotency, chống mua đúp), mà từ 2026-08-10
    # `fill_timing_hybrid_enabled` mặc định True (bật trên paper, commit 717307f). F1/G1
    # chạy mode="paper" ở NOW=09:20 — NGOÀI block MUA của HYBRID (11:00-13:45) ⇒ lệnh MUA
    # bị hoãn theo LỊCH trước khi tới chỗ kiểm lưới ghost.
    # ĐO THẬT (không suy luận), mutation gỡ `if o.ticker in ghost_tickers: continue` ở
    # `_place_slices` rồi A/B đúng MỘT cờ: hybrid=True ⇒ broker KHÔNG bị gọi ⇒ F1 VẪN PASS;
    # hybrid=False ⇒ get_quote bị gọi ⇒ F1 FAIL đúng như phải thế. Nghĩa là trước bản vá này
    # F1 PASS KỂ CẢ KHI lưới ghost bị gỡ sạch — nó không đo được gì nữa. Nguy hiểm hơn màu
    # đỏ: "không gọi broker" không phân biệt được lưới AN TOÀN (ghost, chống mua đúp thật)
    # với lịch CHI PHÍ (HYBRID_DEFER, chỉ hoãn). §23 hệ luận 1: selfcheck không assert lên
    # trạng thái SỐNG (ở đây là một cờ config toàn cục đang trôi). Ca KẾT HỢP đo ở nhóm K.
    cfg["fill_timing_hybrid_enabled"] = False
    cfg.update(cfg_over or {})
    cfg["mode"] = "paper"
    ex = Executor(plan, broker or _NullBroker(), cfg, shared={})
    ex.state_file = os.path.join(tmpdir, "state.json")
    ex.journal_file = os.path.join(tmpdir, "journal.csv")
    return ex


import tempfile

with tempfile.TemporaryDirectory() as tmp:
    o1 = PlannedOrder(id="BUY-01", ticker="GHOST1", side="buy", qty=1000, ref_price=20000)
    o2 = PlannedOrder(id="BUY-02", ticker="CLEAN1", side="buy", qty=1000, ref_price=20000)
    ex = make_executor(tmp, [o1, o2])

    # A. Known oid (already tracked as a child) must NEVER be flagged as a ghost, even
    #    with a large filled qty — this is the expected/normal fill-sync path.
    ex.state["parents"]["BUY-01"]["children"].append(
        {"oid": "100", "qty": 500, "price": 20000, "filled": 0, "status": "open",
         "ts": "2099-01-01T09:15:00"})
    updates_known = {"100": OrderUpdate("100", "PartiallyFilled", 500, 20000,
                                        raw={"symbol": "GHOST1", "quantity": 500})}
    ghosts = ex._ghost_tickers(updates_known)
    check("A1 known oid is never a ghost", ghosts == set(), detail=str(ghosts))

    # B. Unknown oid, filled>0, symbol IN plan -> ghost (this is the exact incident
    #    signature: broker shows a real filled order state.json never recorded).
    updates_ghost = {"999": OrderUpdate("999", "Filled", 1000, 20500,
                                        raw={"symbol": "GHOST1", "quantity": 1000})}
    ghosts = ex._ghost_tickers(updates_ghost)
    check("B1 unknown filled order on a plan ticker -> ghost", ghosts == {"GHOST1"},
          detail=str(ghosts))

    # C. Unknown oid, filled=0, DEAD (cancelled/rejected, never touched money) -> safe
    #    to ignore, no double-buy risk.
    updates_dead_empty = {"888": OrderUpdate("888", "Cancelled", 0, None,
                                             raw={"symbol": "GHOST1", "quantity": 1000})}
    ghosts = ex._ghost_tickers(updates_dead_empty)
    check("C1 unknown dead order with 0 fill is NOT a ghost", ghosts == set(),
          detail=str(ghosts))

    # D. Unknown oid, still OPEN (not dead), filled=0 -> still a ghost (could fill any
    #    moment; placing a second order now would double the eventual position).
    updates_open_empty = {"777": OrderUpdate("777", "New", 0, None,
                                             raw={"symbol": "GHOST1", "quantity": 1000})}
    ghosts = ex._ghost_tickers(updates_open_empty)
    check("D1 unknown OPEN order with 0 fill IS a ghost (pending risk)", ghosts == {"GHOST1"},
          detail=str(ghosts))

    # E. Unknown oid for a ticker NOT in today's plan -> irrelevant, not a ghost
    #    (e.g. a manual trade by the user on an unrelated symbol).
    updates_other = {"666": OrderUpdate("666", "Filled", 100, 30000,
                                        raw={"symbol": "NOTINPLAN", "quantity": 100})}
    ghosts = ex._ghost_tickers(updates_other)
    check("E1 order on a non-plan ticker is not a ghost", ghosts == set(), detail=str(ghosts))

    # F. Integration: _place_slices must SKIP a ghosted ticker without ever calling
    #    broker.place_order (NullBroker.place_order raises if reached).
    try:
        ex._place_slices(__import__("datetime").datetime(2099, 1, 1, 9, 20), "MORNING",
                         ghost_tickers={"GHOST1", "CLEAN1"})
        check("F1 _place_slices skips ALL ghosted tickers without calling broker",
              True)
    except AssertionError as e:
        check("F1 _place_slices skips ALL ghosted tickers without calling broker",
              False, detail=str(e))

    # G. Integration: _atc_sweep must also skip a ghosted ticker.
    ex.state["parents"]["BUY-01"]["children"] = []  # reset from test A's mutation
    try:
        ex._atc_sweep(ghost_tickers={"GHOST1", "CLEAN1"})
        check("G1 _atc_sweep skips ALL ghosted tickers without calling broker", True)
    except AssertionError as e:
        check("G1 _atc_sweep skips ALL ghosted tickers without calling broker", False,
              detail=str(e))

    # H. quant-skeptic killer objection (verify_finding.sh 2026-07-02): if poll_orders()
    #    itself raises, step() must fail-safe-pause EVERY plan ticker this cycle, not
    #    silently proceed with an empty (falsely "no ghosts") set. Full step() through a
    #    broker whose poll_orders() always raises — place_order must never be reached.
    import datetime as _dt

    class _RaisingPollBroker(_NullBroker):
        def poll_orders(self):
            raise RuntimeError("simulated broker outage")

    ex2 = make_executor(tmp, [PlannedOrder(id="BUY-03", ticker="POLLFAIL1", side="buy",
                                           qty=1000, ref_price=20000)])
    ex2.broker = _RaisingPollBroker()
    # Spy on the two placement entry points instead of relying on get_quote/place_order
    # exceptions (those get silently swallowed by pre-existing broad except-blocks a few
    # frames up — _record_prices' PX_HIST_FAIL / _place_slices' PLACE_FAIL retry path —
    # so an AssertionError from a fake broker wouldn't reliably propagate to this test).
    # Instead directly capture what ghost_tickers step() computed and handed down, which
    # IS the exact code path the killer objection targeted.
    seen = {}
    real_place_slices = ex2._place_slices
    real_atc_sweep = ex2._atc_sweep
    ex2._place_slices = lambda now, phase, ghost_tickers=(), positions=None: seen.update(place_slices=set(ghost_tickers))
    ex2._atc_sweep = lambda ghost_tickers=(), positions=None: seen.update(atc_sweep=set(ghost_tickers))
    ex2.step(_dt.datetime(2099, 1, 1, 9, 20), "MORNING", True)
    check("H1 step() passes ALL plan tickers as ghosted when poll_orders() raises",
          seen.get("place_slices") == {"POLLFAIL1"}, detail=str(seen))

    # I. Third-party review (2026-07-02) fix #1: _save_state() must be atomic (tmp +
    #    os.replace), since it now runs after every place_order — a bare overwrite risks
    #    a truncated/corrupt state.json if killed mid-write. Verify: no leftover .tmp file
    #    after a normal save, and the saved file round-trips to valid, matching JSON.
    import json as _json
    ex._save_state()
    tmp_leftover = os.path.exists(ex.state_file + ".tmp")
    check("I1 _save_state leaves no .tmp file behind on success", not tmp_leftover)
    with open(ex.state_file, encoding="utf-8") as f:
        reloaded = _json.load(f)
    check("I2 saved state.json round-trips to the in-memory state",
          reloaded["plan_date"] == ex.state["plan_date"])

    # J. Third-party review fix #2: PaperBroker.poll_orders() was building OrderUpdate
    #    with raw=None, so _ghost_tickers() could never resolve a symbol in paper mode —
    #    paper trading could never rehearse this guard. Verify the fix: a paper order
    #    NOT tracked in state (synthetic — status != "open" so _try_fill/get_quote are
    #    never touched, no live quote source needed) is now correctly seen as a ghost.
    #    ts must be TODAY: poll_orders() day-scopes like the real DNSE order book since
    #    2026-07-09 (a cross-day paper order is yesterday's history, not a ghost — see
    #    paper_main_window_selfcheck.py), and the ghost this check rehearses is the
    #    same-day crash-between-place-and-save signature.
    import datetime as _dt

    from trading_bot.brokers import PaperBroker

    pb = PaperBroker(label="selfcheck-ghost")
    pb.state_file = os.path.join(tmp, "paper_state.json")
    pb.state = {"cash": 0, "positions": {}, "open_orders": {
        "P000001": {"symbol": "PAPERGHOST", "qty": 100, "side": "buy", "price": 20000,
                    "type": "LO", "filled": 100, "status": "Filled",
                    "ts": f"{_dt.date.today().isoformat()}T09:15:00"}},
        "fills": [], "next_id": 2}
    ex3 = make_executor(tmp, [PlannedOrder(id="BUY-04", ticker="PAPERGHOST", side="buy",
                                           qty=1000, ref_price=20000)])
    paper_updates = pb.poll_orders()
    ghosts = ex3._ghost_tickers(paper_updates)
    # Asserts the PROPERTY the guard depends on (a resolvable symbol), not an exact dict:
    # the raw row is deliberately grown over time to mirror the real DNSEBroker row, and an
    # equality assertion turns every such addition into a false failure. It already did once
    # — 2026-08-03 added raw["loanPackageId"] so Executor._lever_package_audit (CAPIT margin
    # leverage) could be rehearsed on paper, and this check failed while the guard worked fine.
    check("J1 PaperBroker order carries a resolvable raw.symbol (not None)",
          (paper_updates["P000001"].raw or {}).get("symbol") == "PAPERGHOST",
          detail=str(paper_updates["P000001"].raw))
    check("J1b …and raw carries loanPackageId, so the CAPIT-leverage guard is rehearsable",
          "loanPackageId" in (paper_updates["P000001"].raw or {}),
          detail=str(paper_updates["P000001"].raw))
    check("J2 untracked paper order is correctly detected as a ghost",
          ghosts == {"PAPERGHOST"}, detail=str(ghosts))

    # ─────────── K. LƯỚI GHOST × HYBRID (đúng cấu hình paper THẬT từ 2026-08-10) ───────────
    # Vì sao nhóm này phải tồn tại: nhóm A-J cố ý ghim HYBRID tắt để cô lập lưới ghost. Nếu
    # chỉ ghim mà không bù, bộ test sẽ mô tả một cấu hình KHÔNG ai chạy (paper thật đang bật
    # HYBRID) và lần đổi cờ tiếp theo lại đi qua không ai thấy. Điểm mấu chốt: khi HYBRID bật,
    # "broker không bị gọi" có HAI nguyên nhân khác hẳn nhau — lưới GHOST (an toàn, chặn mua
    # đúp một vị thế đã tồn tại thật ở broker) và HYBRID_DEFER (lịch chi phí, chỉ hoãn). Đếm
    # số lệnh KHÔNG phân biệt được chúng, nên phân biệt bằng JOURNAL + một ca CHỨNG MINH
    # NGƯỢC: tên sự kiện và việc broker CÓ bị chạm tới mới là bằng chứng nguyên nhân.
    print()
    NOW_K = _dt.datetime(2099, 1, 1, 11, 5)    # TRONG block MUA đầu tiên (11:00-11:15)
    NOW_K_OUT = _dt.datetime(2099, 1, 1, 9, 20)  # NGOÀI block MUA — đúng giờ F1 đang dùng
    HYB_ON = {"fill_timing_hybrid_enabled": True}

    class _ReachedBroker(_NullBroker):
        """Ghi lại việc luồng ĐI TỚI được tầng broker, thay vì ném AssertionError. Trả quote
        None ⇒ `_place_slices` ghi NO_QUOTE rồi `continue`: quan sát được mà không đặt lệnh
        thật, không cần nguồn giá sống."""

        def __init__(self):
            self.quote_calls = []

        def get_quote(self, ticker, *a, **k):
            self.quote_calls.append(ticker)
            return None

    def _events(ex):
        import csv as _csv
        if not os.path.exists(ex.journal_file):
            return set()
        with open(ex.journal_file, encoding="utf-8") as f:
            return {row[1] for row in _csv.reader(f) if len(row) > 1}

    def _mk_k(tag_dir, ghosted, now, cfg_over=HYB_ON):
        """1 ca K = 1 thư mục riêng ⇒ journal/state không lẫn giữa các ca."""
        d = os.path.join(tmp, tag_dir)
        os.makedirs(d, exist_ok=True)
        br = _ReachedBroker()
        exk = make_executor(d, [PlannedOrder(id="BUY-K", ticker="GHOSTK", side="buy",
                                             qty=1000, ref_price=20000)],
                            cfg_over=cfg_over, broker=br)
        exk.state_file = os.path.join(d, "state.json")
        exk.journal_file = os.path.join(d, "journal.csv")
        exk._place_slices(now, "MORNING", ghost_tickers=({"GHOSTK"} if ghosted else set()))
        return exk, br

    # K1 — TRONG block MUA nên HYBRID KHÔNG hoãn; mã bị ghost ⇒ thứ duy nhất còn có thể chặn
    # là lưới ghost. Lưới ghost `continue` LẶNG (không ghi journal), nên bằng chứng "không
    # phải HYBRID" là: journal KHÔNG có HYBRID_DEFER, và broker chưa hề bị chạm.
    ex_k1, br_k1 = _mk_k("k1", ghosted=True, now=NOW_K)
    ev_k1 = _events(ex_k1)
    check("K1 HYBRID bật, TRONG block MUA, mã bị GHOST ⇒ chặn bởi lưới ghost, KHÔNG phải "
          "HYBRID_DEFER (broker chưa bị chạm)",
          "HYBRID_DEFER" not in ev_k1 and br_k1.quote_calls == [],
          detail=f"events={sorted(ev_k1)} quote_calls={br_k1.quote_calls}")

    # K2 — CHỨNG MINH NGƯỢC cho K1: cùng cấu hình HYBRID, cùng giờ trong block, đổi ĐÚNG MỘT
    # biến (bỏ cờ ghost). Nếu K1 chỉ phản ánh "thứ gì đó nuốt lệnh" thì ca này cũng phải im.
    ex_k2, br_k2 = _mk_k("k2", ghosted=False, now=NOW_K)
    check("K2 CHỨNG MINH NGƯỢC: cùng cấu hình/giờ, BỎ cờ ghost ⇒ luồng ĐI TỚI broker "
          "(lưới ghost mới là thứ chặn K1)",
          br_k2.quote_calls == ["GHOSTK"] and "NO_QUOTE" in _events(ex_k2),
          detail=f"quote_calls={br_k2.quote_calls} events={sorted(_events(ex_k2))}")

    # K3 — chốt rằng ghim TẮT ở nhóm A-J là cần thiết chứ không tuỳ tiện, và ghi lại ĐÚNG cơ
    # chế đã che mất F1: cùng lệnh KHÔNG bị ghost, chỉ dời ra ngoài block (09:20 = giờ F1).
    ex_k3, br_k3 = _mk_k("k3", ghosted=False, now=NOW_K_OUT)
    check("K3 HYBRID bật, NGOÀI block ⇒ HYBRID_DEFER và broker KHÔNG bị chạm (đây chính là "
          "thứ làm F1 pass kể cả khi lưới ghost bị gỡ sạch)",
          "HYBRID_DEFER" in _events(ex_k3) and br_k3.quote_calls == [],
          detail=f"events={sorted(_events(ex_k3))} quote_calls={br_k3.quote_calls}")

print()
if fails:
    print(f"FAILED {len(fails)} check(s): {fails}")
    sys.exit(1)
print("ALL CHECKS PASSED — ghost (broker-side, state-unknown) orders are detected and "
      "both _place_slices/_atc_sweep fail-safe-pause on them instead of double-buying.")
sys.exit(0)
