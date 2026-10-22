#!/usr/bin/env python3
"""Selfcheck bộ Livermore (trigger_check / run.sh / score / common). KHÔNG chạm BQ hay claude thật:
bars qua LIVERMORE_BARS_CSV, DT5G qua LIVERMORE_DT5G_CSV, claude/notify là script giả, đồng hồ giả.

Chạy 3 TZ (env -u TZ, America/New_York, UTC — §16/§19) rồi chạy MUTANT (sửa 1 chỗ trong bản sao mã,
selfcheck PHẢI đỏ). exit 0 = tất cả qua.   Usage: bin/livermore_selfcheck.py [--no-mutants]
"""
import datetime as dt
import os
import random
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.environ.get("LIVERMORE_BIN_DIR") or HERE
FILES = ["livermore_common.py", "livermore_run.sh", "livermore_score.py", "livermore_trigger_check.py"]

FAKE_CLAUDE = r'''#!/usr/bin/env bash
# claude giả: đếm số lần gọi; mode qua FAKE_CLAUDE_MODE
echo x >> "$FAKE_CLAUDE_COUNT"
P="${@: -1}"
D="$(echo "$P" | grep -o 'AS_OF = [0-9-]*' | head -1 | cut -d' ' -f3)"
blk() { printf '<<<FORECAST\n- H20_DIR: %s\n- H20_P_UP: %s\n- LEVEL: 1700 HOLD\n- INVALIDATION: close < 1650\nFORECAST>>>\n' "$1" "$2"; }
echo "# Báo cáo Livermore $D"; echo "phân tích giả..."
case "${FAKE_CLAUDE_MODE:-good}" in
  good)       blk UP 0.62; echo "RESULT|$D|UP|0.62|HOLD" ;;
  down)       blk DOWN 0.30; echo "RESULT|$D|DOWN|0.30|BREAK" ;;
  noresult)   blk UP 0.62 ;;
  badid)      blk UP 0.62; echo "RESULT|1999-01-01|UP|0.62|HOLD" ;;
  badp)       blk UP 1.62; echo "RESULT|$D|UP|1.62|HOLD" ;;
  contradict) blk UP 0.30; echo "RESULT|$D|UP|0.30|HOLD" ;;
  noblock)    echo "RESULT|$D|UP|0.62|HOLD" ;;
  mismatch)   blk DOWN 0.30; echo "RESULT|$D|UP|0.62|HOLD" ;;
  badlevel)   blk UP 0.62; echo "RESULT|$D|UP|0.62|MAYBE" ;;
  exit1)      echo boom >&2; exit 1 ;;
esac
'''
FAKE_NOTIFY = '#!/usr/bin/env bash\necho "$2|$1" >> "$FAKE_NOTIFY_LOG"\n'


def inner():
    tmp = tempfile.mkdtemp(prefix="lvr_sc_")
    reg = os.path.join(tmp, "reg", "livermore_reads.md")
    env = dict(LIVERMORE_TEST="1", LIVERMORE_REGISTRY=reg, LIVERMORE_DATA_DIR=os.path.join(tmp, "data"),
               LIVERMORE_STATE_DIR=os.path.join(tmp, "state"), LIVERMORE_BARS_CSV=os.path.join(tmp, "bars.csv"),
               LIVERMORE_DT5G_CSV=os.path.join(tmp, "dt5g.csv"), LIVERMORE_NOW="2026-10-22T19:30:00",
               FAKE_CLAUDE_COUNT=os.path.join(tmp, "claude.count"), FAKE_NOTIFY_LOG=os.path.join(tmp, "notify.log"),
               LIVERMORE_CLAUDE_BIN=os.path.join(tmp, "claude_fake"), LIVERMORE_NOTIFY_BIN=os.path.join(tmp, "notify_fake"),
               LIVERMORE_PY=sys.executable)
    os.environ.update(env)
    for name, body in (("claude_fake", FAKE_CLAUDE), ("notify_fake", FAKE_NOTIFY)):
        p = os.path.join(tmp, name)
        open(p, "w").write(body)
        os.chmod(p, os.stat(p).st_mode | stat.S_IEXEC)
    sys.path.insert(0, BIN)
    import livermore_common as C
    import livermore_score as S
    import livermore_trigger_check as T
    # trigger gọi run.sh/score theo vị trí BIN (mutant có bản riêng)
    os.environ["LIVERMORE_RUN_BIN"] = os.path.join(BIN, "livermore_run.sh")
    os.environ["LIVERMORE_SCORE_BIN"] = os.path.join(BIN, "livermore_score.py")

    fails, n = [], [0]

    def check(name, cond, detail=""):
        n[0] += 1
        if not cond:
            fails.append(f"{name} {detail}")
            print(f"  FAIL {name} {detail}")

    D = dt.date
    cnt = lambda: len(open(env["FAKE_CLAUDE_COUNT"]).read().split()) if os.path.exists(env["FAKE_CLAUDE_COUNT"]) else 0  # noqa: E731
    nlog = lambda: [x for x in open(env["FAKE_NOTIFY_LOG"]).read().splitlines() if x.startswith("livermore|")] if os.path.exists(env["FAKE_NOTIFY_LOG"]) else []  # noqa: E731

    def reset():
        for p in (reg, reg + ".lock", env["FAKE_CLAUDE_COUNT"], env["FAKE_NOTIFY_LOG"]):
            if os.path.exists(p):
                os.remove(p)
        for d in (env["LIVERMORE_DATA_DIR"], env["LIVERMORE_STATE_DIR"]):
            shutil.rmtree(d, ignore_errors=True)
        os.makedirs(os.path.dirname(reg), exist_ok=True)
        open(reg, "w").write("# header\n## Entries\n(chưa có lần đọc sống)\n")

    def write_bars(closes, last=None):
        days = [last or D(2026, 10, 22)]
        while len(days) < len(closes):
            days.append(C.prev_session(days[-1]))
        days.reverse()
        with open(env["LIVERMORE_BARS_CSV"], "w") as fh:
            fh.write("time,Open,High,Low,Close,Volume\n")
            for d, c in zip(days, closes):
                fh.write(f"{d},{c},{c + 1},{c - 1},{c},1000000\n")
        return days

    def walk(n_, seed=1, lo=1000.0, hi=1200.0):
        rnd = random.Random(seed)
        return [round(lo + (hi - lo) * (0.5 + 0.45 * (rnd.random() - 0.5)), 2) for _ in range(n_)]

    # ── 1. lịch HOSE ──
    d, cal = C.add_sessions(D(2026, 8, 28), 3)
    check("cal-holiday-bù-QK", d == D(2026, 9, 7), str(d))
    d, cal = C.add_sessions(D(2026, 10, 22), 20)
    check("cal-20-phiên", d == D(2026, 11, 19) and cal == "CONFIRMED", f"{d} {cal}")
    d, cal = C.add_sessions(D(2026, 12, 24), 20)
    check("cal-qua-2026-ESTIMATE", cal == "ESTIMATE" and d.weekday() < 5, f"{d} {cal}")
    d, _ = C.add_sessions(D(2027, 1, 29), 3)
    check("cal-Tết-ước-lượng-bỏ-qua", d == D(2027, 2, 17), str(d))
    check("cal-cuối-tuần", C.next_session(D(2026, 10, 23)) == D(2026, 10, 26))
    check("exp-sau-19h", C.expected_last_session(dt.datetime(2026, 10, 22, 19, 30, tzinfo=C.ICT)) == D(2026, 10, 22))
    check("exp-trước-19h", C.expected_last_session(dt.datetime(2026, 10, 22, 18, 59, tzinfo=C.ICT)) == D(2026, 10, 21))
    check("exp-T7", C.expected_last_session(dt.datetime(2026, 10, 24, 20, 0, tzinfo=C.ICT)) == D(2026, 10, 23))
    # TZ ngoài không đổi now_ict thật
    os.environ.pop("LIVERMORE_NOW")
    check("now_ict-neo-ICT", C.now_ict().utcoffset() == dt.timedelta(hours=7))
    os.environ["LIVERMORE_NOW"] = env["LIVERMORE_NOW"]

    # ── 2. điều kiện kích hoạt ──
    base = walk(300)
    check("price-none", T.price_kinds(base) == [], str(T.price_kinds(base)))
    up = base[:-1] + [max(base) * 0.99]
    check("price-near-hi", "PRICE_NEAR_HI252" in T.price_kinds(up))
    check("price-break-up", "PRICE_BREAK60_UP" in T.price_kinds(base[:-1] + [max(base) + 5]))
    check("price-near-lo", "PRICE_NEAR_LO252" in T.price_kinds(base[:-1] + [min(base) * 1.015]))
    check("price-break-down", "PRICE_BREAK60_DOWN" in T.price_kinds(base[:-1] + [min(base) - 5]))
    check("price-2.1%-không-bắn", "PRICE_NEAR_HI252" not in T.price_kinds(base[:-1] + [max(base) * 0.979]))
    clk = lambda **k: dict(active=True, cand=1, k=15, need=25, committed=3, asof="2026-10-22", **k)  # noqa: E731
    check("dt-enter-15", T.dt_kinds(clk()) == ["DT_ENTER_CRISIS"])
    check("dt-enter-14", T.dt_kinds({**clk(), "k": 14}) == [])
    check("dt-enter-exbull", T.dt_kinds({**clk(), "cand": 5, "k": 20}) == ["DT_ENTER_EXBULL"])
    check("dt-need25-BULL-không", T.dt_kinds({**clk(), "cand": 4}) == [])
    check("dt-exit-5", T.dt_kinds(dict(active=True, cand=3, k=5, need=10, committed=1)) == ["DT_EXIT_CRISIS"])
    check("dt-exit-4", T.dt_kinds(dict(active=True, cand=3, k=4, need=10, committed=1)) == [])
    check("dt-neutral→bear-không", T.dt_kinds(dict(active=True, cand=2, k=9, need=10, committed=3)) == [])
    check("dt-inactive", T.dt_kinds(dict(active=False, committed=1)) == [] and T.dt_kinds(None) == [])
    dates = [D(2026, 10, 1)]
    while len(dates) < 12:
        dates.append(C.next_session(dates[-1]))
    check("cooldown-4-phiên", not T.cooled("K", dates[4], {"K": str(dates[0])}, dates))
    check("cooldown-5-phiên", T.cooled("K", dates[5], {"K": str(dates[0])}, dates))
    check("cooldown-chưa-từng", T.cooled("K", dates[5], {}, dates))
    check("cooldown-cùng-ngày", not T.cooled("K", dates[5], {"K": str(dates[5])}, dates))

    # ── 3. parse RESULT (fail-loud) ──
    good = "x\n<<<FORECAST\n- H20_DIR: UP\n- H20_P_UP: 0.62\n- LEVEL: 1700 HOLD\n- INVALIDATION: <1650\nFORECAST>>>\nRESULT|2026-10-22|UP|0.62|HOLD\n"
    a = D(2026, 10, 22)
    check("parse-ok", C.parse_forecast(good, a)["p_up"] == 0.62)
    bads = {"thiếu-RESULT": good.replace("RESULT|2026-10-22|UP|0.62|HOLD", ""),
            "sai-id": good.replace("RESULT|2026-10-22", "RESULT|2026-10-21"),
            "P>1": good.replace("0.62|HOLD", "1.62|HOLD"),
            "UP-p<.5": good.replace("0.62|HOLD", "0.30|HOLD").replace("H20_P_UP: 0.62", "H20_P_UP: 0.30"),
            "thiếu-khối": good.replace("<<<FORECAST", "").replace("FORECAST>>>", ""),
            "dir-lệch": good.replace("H20_DIR: UP", "H20_DIR: DOWN"),
            "p-lệch": good.replace("H20_P_UP: 0.62", "H20_P_UP: 0.55"),
            "level": good.replace("|HOLD", "|MAYBE"),
            "thiếu-INVALIDATION": good.replace("- INVALIDATION: <1650\n", ""),
            "2-RESULT": good + "RESULT|2026-10-22|UP|0.62|HOLD\n"}
    for k, txt in bads.items():
        try:
            C.parse_forecast(txt, a)
            check(f"parse-bad:{k}", False, "không raise")
        except C.ResultError:
            check(f"parse-bad:{k}", True)

    # ── 4. DT5G đọc đúng bảng (SQL) ──
    seen = []
    old_rows, old_env = C.bq_rows, os.environ.pop("LIVERMORE_DT5G_CSV")
    C.bq_rows = lambda sql, max_rows=5000: (seen.append(sql), [{"time": "2026-10-22", "state": "3"}])[1]
    st = C.get_dt5g_state(D(2026, 10, 22))
    C.bq_rows, os.environ["LIVERMORE_DT5G_CSV"] = old_rows, old_env
    check("dt5g-đúng-bảng-live", st == 3 and "vnindex_5state_dt5g_live" in seen[0] and "5state AS" not in seen[0], str(seen))

    # ── 4b. gói dữ liệu không rò bar sau as-of ──
    reset()
    write_bars(walk(520))                                # bars đến 10-22
    pk = os.path.join(tmp, "pkg.csv")
    os.environ["LIVERMORE_ALLOW_PAST"] = "1"
    r = subprocess.run([sys.executable, os.path.join(BIN, "livermore_common.py"), "package", "2026-10-20", pk],
                       capture_output=True, text=True)
    rows = open(pk).read().splitlines() if r.returncode == 0 else []
    check("gói-không-rò-sau-as-of", rows and rows[-1].startswith("2026-10-20,") and "2026-10-21" not in "".join(rows),
          (rows[-1] if rows else r.stderr[-200:]))
    check("gói-500-bar", len(rows) == 501, str(len(rows)))
    del os.environ["LIVERMORE_ALLOW_PAST"]
    r = subprocess.run([sys.executable, os.path.join(BIN, "livermore_common.py"), "package", "2026-10-20", pk],
                       capture_output=True, text=True)
    check("gói-cũ-hơn-kỳ-vọng-bị-từ-chối", r.returncode != 0, r.stdout[-100:])

    # ── 5. chuỗi đầy đủ: trigger → run.sh → claude giả → registry → notify ──
    reset()
    closes = walk(299) + [1300.0]            # phá đỉnh ⇒ PRICE_NEAR_HI252 + PRICE_BREAK60_UP
    write_bars(closes)
    os.environ["FAKE_CLAUDE_MODE"] = "good"
    rc = T.evaluate([], clock_fn=lambda: None)
    txt = C.read_registry()
    check("chain-rc10", rc == 10, f"rc={rc}")
    check("chain-entry", "### LVR-2026-10-22" in txt and "- result: RESULT|2026-10-22|UP|0.62|HOLD" in txt)
    check("chain-due", "- due: 2026-11-19 (calendar=CONFIRMED)" in txt)
    check("chain-outcome-trống", txt.rstrip().endswith("- outcome:"))
    check("chain-report", os.path.exists(os.path.join(env["LIVERMORE_DATA_DIR"], "2026-10-22.md")))
    check("chain-claude-1", cnt() == 1)
    check("chain-notify-1", len(nlog()) == 1 and nlog()[0].startswith("livermore|"), str(nlog()))
    snap = txt
    rc2 = T.evaluate([], clock_fn=lambda: None)          # chạy lại cùng ngày
    check("idem-rc", rc2 == 10)
    check("idem-không-gọi-lại-LLM", cnt() == 1, str(cnt()))
    check("idem-không-báo-lại", len(nlog()) == 1)
    check("idem-registry-nguyên", C.read_registry() == snap)
    # run.sh chạy tay lần 2: EXISTS, không gọi claude
    r = subprocess.run([os.environ["LIVERMORE_RUN_BIN"], "--as-of", "2026-10-22"], capture_output=True, text=True)
    check("run-idem", r.returncode == 0 and cnt() == 1 and C.read_registry() == snap, r.stderr[-200:])
    # kill giữa chừng: entry có, state còn pending, chưa báo
    import json
    stt = json.load(open(os.path.join(env["LIVERMORE_STATE_DIR"], "livermore_trigger.json")))
    stt["runs"]["2026-10-22"].update(status="pending", notified=False)
    stt["last_fired"] = {}
    C.atomic_write(os.path.join(env["LIVERMORE_STATE_DIR"], "livermore_trigger.json"), json.dumps(stt))
    rc3 = T.evaluate([], clock_fn=lambda: None)
    check("kill-resume", rc3 == 10 and cnt() == 1 and len(nlog()) == 2, f"rc={rc3} cnt={cnt()} n={len(nlog())}")
    # kill sau khi state=done nhưng TRƯỚC khi báo ⇒ lượt sau chỉ báo bù, không gọi lại LLM
    stt = json.load(open(os.path.join(env["LIVERMORE_STATE_DIR"], "livermore_trigger.json")))
    stt["runs"]["2026-10-22"].update(status="done", notified=False)
    C.atomic_write(os.path.join(env["LIVERMORE_STATE_DIR"], "livermore_trigger.json"), json.dumps(stt))
    n_before = len(nlog())
    rc3b = T.evaluate([], clock_fn=lambda: None)
    check("kill-sau-done-báo-bù", rc3b == 10 and cnt() == 1 and len(nlog()) == n_before + 1, f"rc={rc3b}")
    # dedupe theo loại: ngày kế (as-of mới) cùng điều kiện < 5 phiên ⇒ không bắn
    write_bars(closes + [1310.0], last=D(2026, 10, 23))
    os.environ["LIVERMORE_NOW"] = "2026-10-23T19:30:00"
    rc4 = T.evaluate([], clock_fn=lambda: dict(active=False, committed=3, asof="2026-10-23"))
    check("dedupe-5-phiên", rc4 == 0 and cnt() == 1, f"rc={rc4} cnt={cnt()}")
    os.environ["LIVERMORE_NOW"] = env["LIVERMORE_NOW"]

    # ── 6. as-of lệch / dữ liệu cũ ──
    reset()
    write_bars(closes, last=D(2026, 10, 21))             # đồng hồ 10-22 19:30 nhưng bar cuối 10-21
    rc = T.evaluate([], clock_fn=lambda: clk())
    check("stale-rc3", rc == 3 and cnt() == 0, f"rc={rc}")
    write_bars(walk(300))                                # bars đúng, clock lệch as-of ⇒ bỏ DT
    rc = T.evaluate([], clock_fn=lambda: {**clk(), "asof": "2026-10-21"})
    check("clock-lệch-bỏ-DT", rc == 4 and cnt() == 0, f"rc={rc}")
    rc = T.evaluate([], clock_fn=lambda: clk())          # clock đúng ⇒ bắn DT
    check("clock-đúng-bắn-DT", rc == 10 and "DT_ENTER_CRISIS" in C.read_registry(), f"rc={rc}")
    reset()
    r = subprocess.run([os.environ["LIVERMORE_RUN_BIN"], "--as-of", "2026-10-25"], capture_output=True, text=True)
    check("run-as-of-không-phải-bar", r.returncode != 0 and cnt() == 0, r.stderr[-200:])

    # ── 7. parse hỏng ⇒ fail-loud, KHÔNG entry nửa vời ──
    for mode in ("noresult", "badid", "badp", "contradict", "noblock", "mismatch", "badlevel", "exit1"):
        reset()
        write_bars(closes)
        os.environ["FAKE_CLAUDE_MODE"] = mode
        rc = T.evaluate([], clock_fn=lambda: None)
        check(f"fail-loud:{mode}", rc == 11 and "### LVR-" not in C.read_registry()
              and os.path.exists(os.path.join(env["LIVERMORE_DATA_DIR"], "2026-10-22.FAILED.md"))
              and any("LỖI" in x for x in nlog()), f"rc={rc} notify={nlog()}")
        if mode == "badid":
            check("fail-không-đặt-last_fired", not json.load(open(os.path.join(env["LIVERMORE_STATE_DIR"], "livermore_trigger.json")))["last_fired"])
    os.environ["FAKE_CLAUDE_MODE"] = "good"

    # ── 8. chấm điểm ──
    def mk_entries(specs):
        """specs: list (as_of, dir, p_up). bars phẳng 1000 trừ close[D+20] theo y."""
        reset()
        days = [D(2026, 1, 5)]
        while len(days) < 400:
            days.append(C.next_session(days[-1]))
        closes_ = {d: 1000.0 for d in days}
        txt_ = ""
        dtrows = []
        for i, (idx, dr, p, y, st_) in enumerate(specs):
            a_ = days[idx]
            closes_[days[idx + 20]] = 1010.0 if y else 990.0
            due, cal = C.add_sessions(a_, 20)
            txt_ += (f"\n### LVR-{a_}\n- as_of: {a_}\n- created: x\n- trigger: T\n- close_asof: 1000.0\n- due: {due} "
                     f"(calendar={cal})\n- report: r\n- forecast:\n    f\n- result: RESULT|{a_}|{dr}|{p}|HOLD\n- outcome:\n")
            if st_:
                dtrows.append(f"{a_},{st_}")
        C.locked_append(reg, txt_)
        with open(env["LIVERMORE_BARS_CSV"], "w") as fh:
            fh.write("time,Open,High,Low,Close,Volume\n")
            for d_ in days:
                c_ = closes_[d_]
                fh.write(f"{d_},{c_},{c_},{c_},{c_},1\n")
        open(env["LIVERMORE_DT5G_CSV"], "w").write("time,state\n" + "\n".join(dtrows) + "\n")
        return days

    days = mk_entries([(0, "UP", 0.7, 1, 3), (1, "UP", 0.6, 0, 3), (2, "DOWN", 0.2, 0, 1)])
    os.environ["LIVERMORE_NOW"] = f"{days[30]}T19:30:00"
    rc = S.main(["--today", str(days[30])])
    sc = C.parse_scores(C.read_registry())
    check("score-3-dòng", len(sc) == 3 and rc == 0, str(len(sc)))
    l0, l1, l2 = (sc[str(days[i])] for i in (0, 1, 2))
    check("score-hit-brier", "|hit=1|brier=0.0900|" in l0 and "|hit=0|brier=0.3600|" in l1 and "|hit=1|brier=0.0400|" in l2, f"{l0}\n{l1}\n{l2}")
    check("score-dt5g-implied", "dt5g_state=3|dt5g_hit=1|dt5g_brier=0.0900" in l0 and "dt5g_state=1|dt5g_hit=1|dt5g_brier=0.0000" in l2, l0 + l2)
    before = C.read_registry()
    S.main(["--today", str(days[30])])
    check("score-idempotent", C.read_registry() == before)
    check("score-entry-không-bị-sửa", before.startswith("# header") and "- outcome:\n\n### LVR-" in before.replace("\n\n###", "\n\n###"))
    S.main(["--today", str(days[30]), "--notify"])
    check("score-không-notify-khi-không-mới", len(nlog()) == 0)
    # chưa đến hạn / chưa đủ bar
    mk_entries([(0, "UP", 0.7, 1, 3)])
    S.main(["--today", str(days[19])])
    check("score-chưa-đến-hạn", not C.parse_scores(C.read_registry()))
    # as-of lệch dữ liệu chấm (close khác sổ) ⇒ lỗi, không ghi
    mk_entries([(0, "UP", 0.7, 1, 3)])
    txt_ = C.read_registry().replace("close_asof: 1000.0", "close_asof: 1234.0")
    C.atomic_write(reg, txt_)
    rc = S.main(["--today", str(days[30])])
    check("score-close-lệch-fail", rc == 1 and not C.parse_scores(C.read_registry()))
    # cổng giải thể
    def gate(n_entries, livermore_right):
        sp = []
        for i in range(n_entries):
            y_ = i % 2
            up_ = bool(y_) == livermore_right
            sp.append((i, "UP" if up_ else "DOWN", 0.9 if up_ else 0.1, y_, 3))
        mk_entries(sp)
        return S.main(["--today", str(days[60]), "--notify"])
    check("gate-11-không", gate(11, False) == 0)
    # 12 entry; Livermore sai hết, DT5G (state 3 ⇒ .7) đúng ⇒ Livermore không hơn gì cả ⇒ giải thể
    rc = gate(12, False)
    check("gate-12-sai-hết-giải-thể", rc == 20 and "GIẢI THỂ" in open(env["FAKE_NOTIFY_LOG"]).read(), f"rc={rc}")
    rc = gate(12, True)
    check("gate-12-đúng-hết-không", rc == 0, f"rc={rc}")
    # 12 entry, y toàn 1: Livermore hơn đồng xu nhưng KHÔNG hơn "luôn UP" ⇒ giải thể (phải hơn CẢ 3)
    c = S.cumulative([{"hit": 1, "brier": .01, "y": 1, "dt_hit": 1.0, "dt_brier": .09}] * 12)
    check("gate-hơn-đồng-xu-nhưng-thua-luôn-UP-thì-giải-thể", c["dissolve"] and c["beats"]["coin"] and not c["beats"]["always_up"])
    # hơn đồng xu + luôn-UP nhưng thua DT5G ⇒ giải thể
    rows_ = [{"hit": 1, "brier": .2, "y": 1, "dt_hit": 1.0, "dt_brier": .01}] * 6 + [{"hit": 1, "brier": .2, "y": 0, "dt_hit": 1.0, "dt_brier": .01}] * 6
    c = S.cumulative(rows_)
    check("gate-thua-DT5G-thì-giải-thể", c["dissolve"] and c["beats"]["coin"] and not c["beats"]["dt5g"], str(c["beats"]))
    # hơn cả 3 ⇒ không giải thể
    rows_ = [{"hit": 1, "brier": .04, "y": 1, "dt_hit": 0.0, "dt_brier": .5}] * 6 + [{"hit": 1, "brier": .04, "y": 0, "dt_hit": 0.0, "dt_brier": .9}] * 6
    c = S.cumulative(rows_)
    check("gate-hơn-cả-3-không-giải-thể", not c["dissolve"] and all(c["beats"].values()), str(c["beats"]))
    c = S.cumulative([{"hit": 0, "brier": .5, "y": 1, "dt_hit": None, "dt_brier": None}] * 12)
    check("gate-dt5g-NA", c["dissolve"] and c["n_dt5g"] == 0)

    # ── 9. append-only an toàn ──
    reset()
    check("append-ghi", C.locked_append(reg, "### LVR-2026-01-01\n", guard=lambda c_: C.has_entry(c_, D(2026, 1, 1))))
    check("append-guard-chặn", not C.locked_append(reg, "### LVR-2026-01-01\n", guard=lambda c_: C.has_entry(c_, D(2026, 1, 1))))

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"[inner] {n[0]} assertion, {len(fails)} fail")
    return 1 if fails else 0


MUTANTS = [
    ("livermore_trigger_check.py", "COOLDOWN = 5", "COOLDOWN = 1", "bỏ dedupe 5 phiên"),
    ("livermore_trigger_check.py", "ENTER_K, EXIT_K = 15, 5", "ENTER_K, EXIT_K = 25, 5", "ngưỡng vào 15→25"),
    ("livermore_trigger_check.py", "NEAR_PCT, HI_LO_WIN, BREAK_WIN = 0.02,", "NEAR_PCT, HI_LO_WIN, BREAK_WIN = 0.05,", "biên 2%→5%"),
    ("livermore_trigger_check.py", "    if as_of < exp:", "    if False:", "bỏ kiểm as-of lệch"),
    ("livermore_trigger_check.py", 'if run0 and run0.get("status") == "done" and not dry:', "if False:", "bỏ idempotent/resume báo"),
    ("livermore_trigger_check.py", "if clock is not None and clock.get(\"asof\") == str(as_of):", "if clock is not None:", "bỏ kiểm asof của clock"),
    ("livermore_common.py", "    if rid != str(as_of):", "    if False:", "bỏ kiểm id RESULT"),
    ("livermore_common.py", 'if (d == "UP" and pu < 0.5) or (d == "DOWN" and pu > 0.5):', "if False:", "bỏ kiểm mâu thuẫn dir/P_UP"),
    ("livermore_common.py", "d.weekday() < 5 and not _vm().is_holiday(d) and", "d.weekday() < 5 and", "lịch bỏ ngày lễ"),
    ("livermore_common.py", "    bars = [b for b in get_bars(start, as_of) if b[\"time\"] <= as_of]", "    bars = get_bars(start)", "gói dữ liệu rò bar sau as-of"),
    ("livermore_common.py", "FROM tav2_bq.vnindex_5state_dt5g_live AS t", "FROM tav2_bq.vnindex_5state AS t", "đọc nhầm bảng không hậu tố"),
    ("livermore_score.py", "y = 1 if b20[\"close\"] > bars[i0][\"close\"] else 0", "y = 1 if b20[\"close\"] < bars[i0][\"close\"] else 0", "đảo dấu hit"),
    ("livermore_score.py", "return 20 if c.get(\"dissolve\") else 0", "return 0", "bỏ rc giải thể"),
    ("livermore_score.py", "dissolve\": n >= GATE_N and", "dissolve\": n >= 1 and", "cổng giải thể không chờ 12"),
    ("livermore_score.py", "not all(beats.values())", "not any(beats.values())", "giải thể chỉ khi thua cả 3 (sai luật)"),
    ("livermore_run.sh", "grep -q \"^### LVR-$AS_OF\\$\" \"$REG\"", "false", "run.sh mất idempotent"),
]


def run_inner_in(env_extra, bindir=None):
    env = dict(os.environ, **env_extra)
    env.pop("LIVERMORE_NOW", None)
    if bindir:
        env["LIVERMORE_BIN_DIR"] = bindir
    return subprocess.run([sys.executable, os.path.join(HERE, "livermore_selfcheck.py"), "--inner"],
                          capture_output=True, text=True, env=env)


def main():
    rc = 0
    for label, extra, unset in (("TZ-unset", {}, True), ("TZ=America/New_York", {"TZ": "America/New_York"}, False),
                                ("TZ=UTC", {"TZ": "UTC"}, False)):
        env = dict(os.environ, **extra)
        if unset:
            env.pop("TZ", None)
        env.pop("LIVERMORE_BIN_DIR", None) if not os.environ.get("LIVERMORE_BIN_DIR") else None
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"], capture_output=True, text=True, env=env)
        last = (r.stdout.strip().splitlines() or ["?"])[-1]
        print(f"{label}: rc={r.returncode} {last}")
        if r.returncode:
            print(r.stdout[-1500:], r.stderr[-800:])
            rc = 1
    if rc or "--no-mutants" in sys.argv or os.environ.get("LIVERMORE_BIN_DIR"):
        return rc
    survived = []
    for fn, old, new, why in MUTANTS:
        tmp = tempfile.mkdtemp(prefix="lvr_mut_")
        bd = os.path.join(tmp, "mike", "bin")
        os.makedirs(bd)
        os.symlink(os.path.join(os.path.dirname(os.path.dirname(HERE)), "trading_bot"), os.path.join(tmp, "trading_bot"))
        for f in FILES:
            shutil.copy(os.path.join(HERE, f), bd)
        p = os.path.join(bd, fn)
        s = open(p).read()
        if old not in s:
            print(f"MUTANT {why}: mẫu không tìm thấy trong {fn} — selfcheck cũ kỹ")
            survived.append(why)
            continue
        open(p, "w").write(s.replace(old, new, 1))
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"], capture_output=True, text=True,
                           env=dict(os.environ, LIVERMORE_BIN_DIR=bd))
        killed = r.returncode != 0
        print(f"MUTANT {'chết' if killed else 'SỐNG'}: {why}")
        if not killed:
            survived.append(why)
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"{len(MUTANTS) - len(survived)}/{len(MUTANTS)} mutant chết")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(inner() if "--inner" in sys.argv else main())
