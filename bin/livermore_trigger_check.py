#!/usr/bin/env python3
"""Cò kích hoạt Livermore "đọc sống" — chạy T2-T6 SAU 19:01 ICT (DT5G publish xong).

Kích hoạt (đủ MỘT):
  (i)  DT gate candidate (dna_report.get_dt_gate_clock): VÀO CRISIS/EX-BULL (need=25) với k>=15,
       hoặc RA CRISIS/EX-BULL (need=10, committed đang là CRISIS/EX-BULL) với k>=5;
  (ii) VNINDEX đóng cửa cách đỉnh/đáy ĐÓNG CỬA 252 phiên <=2%, hoặc đóng cửa phá biên đóng cửa 60 phiên TRƯỚC.
Dedupe: cùng (loại, as-of) chạy lại = no-op; mỗi loại tối đa 1 lần / 5 phiên (cooldown theo bar).
Mỗi as-of tối đa 1 lần gọi livermore_run.sh. WARN-only: lỗi ở đây KHÔNG chặn gì khác (cron độc lập).
Cuối mỗi lượt gọi livermore_score.py --notify (chấm entry đáo hạn).

rc: 0 không kích hoạt · 10 kích hoạt + đọc xong · 11 kích hoạt nhưng run lỗi · 3 dữ liệu cũ/lệch as-of
    · 4 DT clock không dùng được (và không có kích hoạt giá) · 2 lỗi đầu vào (BQ...).
Cờ: --dry-run (không state/run/notify/score).  Hook test: LIVERMORE_RUN_BIN, LIVERMORE_SCORE_BIN,
LIVERMORE_NOTIFY_BIN, LIVERMORE_STATE_DIR, và cho clock: tham số clock_fn của evaluate().
"""
import datetime as dt
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import livermore_common as C                                   # noqa: E402

CRISIS, EXBULL = 1, 5
STATE_NAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
ENTER_K, EXIT_K = 15, 5
NEAR_PCT, HI_LO_WIN, BREAK_WIN = 0.02, 252, 60
COOLDOWN = 5          # phiên
STATE_FILE = lambda: os.path.join(C.STATE_DIR, "livermore_trigger.json")      # noqa: E731


def dt_kinds(clock):
    if not clock or not clock.get("active"):
        return []
    cand, k, need, com = clock["cand"], clock["k"], clock["need"], clock.get("committed")
    if need == 25 and cand in (CRISIS, EXBULL) and k >= ENTER_K:
        return [f"DT_ENTER_{STATE_NAME[cand]}"]
    if need == 10 and com in (CRISIS, EXBULL) and k >= EXIT_K:
        return [f"DT_EXIT_{STATE_NAME[com]}"]
    return []


def price_kinds(closes):
    """closes: list close tăng dần, phần tử cuối = as-of."""
    if len(closes) < HI_LO_WIN + 1:
        raise ValueError(f"cần >= {HI_LO_WIN + 1} bar, có {len(closes)}")
    c, w = closes[-1], closes[-HI_LO_WIN:]
    hi, lo, out = max(w), min(w), []
    if (hi - c) / hi <= NEAR_PCT:
        out.append("PRICE_NEAR_HI252")
    if (c - lo) / lo <= NEAR_PCT:
        out.append("PRICE_NEAR_LO252")
    prior = closes[-BREAK_WIN - 1:-1]
    if c > max(prior):
        out.append("PRICE_BREAK60_UP")
    if c < min(prior):
        out.append("PRICE_BREAK60_DOWN")
    return out


def load_state():
    p = STATE_FILE()
    if not os.path.exists(p):
        return {"last_fired": {}, "runs": {}}
    with open(p, encoding="utf-8") as fh:
        st = json.load(fh)               # hỏng ⇒ raise (fail loud), không tự reset rồi bắn lặp
    st.setdefault("last_fired", {})
    st.setdefault("runs", {})
    return st


def save_state(st):
    C.atomic_write(STATE_FILE(), json.dumps(st, indent=1, sort_keys=True) + "\n")


def cooled(kind, as_of, last_fired, dates):
    """True nếu kind được phép bắn: chưa từng, hoặc cách lần trước >= COOLDOWN phiên (đếm theo bar)."""
    prev = last_fired.get(kind)
    if not prev:
        return True
    prev = dt.date.fromisoformat(prev)
    if prev >= as_of:
        return False
    if prev in dates:
        return dates.index(as_of) - dates.index(prev) >= COOLDOWN
    n, d = 0, prev
    while d < as_of:
        d = C.next_session(d)
        n += 1
    return n >= COOLDOWN


def real_clock():
    sys.path.insert(0, C.WC_ROOT)
    import dna_report
    return dna_report.get_dt_gate_clock()


def notify(msg):
    chan = os.environ.get("DISCORD_THREAD_ID_LIVERMORE") or "livermore"
    binp = os.environ.get("LIVERMORE_NOTIFY_BIN") or os.path.join(C.ROOT, "bin", "notify_thread.sh")
    try:
        r = subprocess.run([binp, msg, chan], capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            return True
        print(f"[trigger] WARN notify rc={r.returncode}: {r.stderr.strip()[:200]}", file=sys.stderr)
    except Exception as ex:
        print(f"[trigger] WARN notify lỗi: {ex}", file=sys.stderr)
    return False


def entry_summary(as_of):
    for e in C.parse_entries(C.read_registry()):
        if e["as_of"] == as_of:
            return (f"H20_DIR={e['dir']} P_UP={e['p_up']:.2f} LEVEL {e['level']} · đáo hạn {e['due']} "
                    f"(lịch {e['calendar']}) · báo cáo mike/data/livermore/{as_of}.md")
    return None


def run_livermore(as_of, kinds):
    binp = os.environ.get("LIVERMORE_RUN_BIN") or os.path.join(C.ROOT, "bin", "livermore_run.sh")
    r = subprocess.run([binp, "--as-of", str(as_of), "--triggers", ",".join(kinds)],
                       capture_output=True, text=True, timeout=1200)
    return r.returncode, (r.stdout + r.stderr).strip()[-400:]


def run_score():
    binp = os.environ.get("LIVERMORE_SCORE_BIN") or os.path.join(C.ROOT, "bin", "livermore_score.py")
    try:
        r = subprocess.run([sys.executable, binp, "--notify"], capture_output=True, text=True, timeout=300)
        print(f"[trigger] score rc={r.returncode}: " + (r.stdout.strip().splitlines() or [""])[-1][:200])
        if r.returncode not in (0, 20):
            print(f"[trigger] WARN score lỗi: {r.stderr.strip()[:300]}", file=sys.stderr)
    except Exception as ex:
        print(f"[trigger] WARN score lỗi: {ex}", file=sys.stderr)


def evaluate(argv, clock_fn=real_clock):
    dry = "--dry-run" in argv
    today = C.today_ict()
    bars = C.get_bars(today - dt.timedelta(days=700))
    if len(bars) < HI_LO_WIN + 1:
        print(f"[trigger] LỖI chỉ có {len(bars)} bar (<{HI_LO_WIN + 1})", file=sys.stderr)
        return 2
    as_of = bars[-1]["time"]
    exp = C.expected_last_session()
    if as_of < exp:
        print(f"[trigger] STALE: bar cuối {as_of} < phiên kỳ vọng {exp} — không kích hoạt")
        return 3
    dates = [b["time"] for b in bars]
    kinds = price_kinds([b["close"] for b in bars])
    clock, clock_ok = None, False
    try:
        clock = clock_fn()
    except Exception as ex:
        print(f"[trigger] WARN DT clock lỗi: {ex}", file=sys.stderr)
    if clock is not None and clock.get("asof") == str(as_of):
        clock_ok = True
        kinds = dt_kinds(clock) + kinds
    elif clock is not None:
        print(f"[trigger] WARN DT clock asof={clock.get('asof')} ≠ VNINDEX as-of {as_of} — bỏ điều kiện DT")
    st = load_state()
    run0 = st["runs"].get(str(as_of))
    if run0 and run0.get("status") == "done" and not dry:       # đã đọc rồi: chỉ có thể còn thiếu bước báo
        if not run0.get("notified"):
            summ = entry_summary(as_of) or "(entry có nhưng không parse được — kiểm registry)"
            if notify(f"📈 Livermore đọc {as_of} — kích hoạt: {','.join(run0.get('kinds', []))}\n{summ}"):
                run0["notified"] = True
                save_state(st)
        print(f"[trigger] as-of {as_of} đã đọc xong — no-op")
        return 10
    ok_kinds = [k for k in kinds if cooled(k, as_of, st["last_fired"], dates)]
    print(f"[trigger] as-of={as_of} kích hoạt thô={kinds} sau cooldown={ok_kinds} clock_ok={clock_ok}")
    rc = 0 if (clock_ok or ok_kinds) else 4
    if not ok_kinds or dry:
        return rc
    has = C.has_entry(C.read_registry(), as_of)
    if not has:
        st["runs"][str(as_of)] = {"kinds": ok_kinds, "status": "pending", "notified": False,
                                  "ts": C.now_ict().isoformat(timespec="seconds")}
        save_state(st)                       # ghi TRƯỚC khi gọi ngoài (§5)
        rcr, tail = run_livermore(as_of, ok_kinds)
        has = rcr == 0 and C.has_entry(C.read_registry(), as_of)
        if not has:
            st["runs"][str(as_of)]["status"] = "failed"
            save_state(st)
            notify(f"⚠️ Livermore {as_of}: kích hoạt {','.join(ok_kinds)} nhưng đọc LỖI (rc={rcr}): {tail[-250:]}")
            return 11
    run = st["runs"].get(str(as_of)) or {"kinds": ok_kinds, "notified": False}
    run.update(status="done", kinds=run.get("kinds") or ok_kinds)
    for k in ok_kinds:
        st["last_fired"][k] = str(as_of)
    st["runs"][str(as_of)] = run
    save_state(st)                           # entry đã có ⇒ ghi ngay, rồi mới báo
    summ = entry_summary(as_of) or "(entry có nhưng không parse được — kiểm registry)"
    if notify(f"📈 Livermore đọc {as_of} — kích hoạt: {','.join(ok_kinds)}\n{summ}"):
        run["notified"] = True
        save_state(st)
    return 10


def main(argv):
    try:
        rc = evaluate(argv)
    except Exception as ex:
        print(f"[trigger] LỖI: {type(ex).__name__}: {ex}", file=sys.stderr)
        rc = 2
    if "--dry-run" not in argv:
        run_score()
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
