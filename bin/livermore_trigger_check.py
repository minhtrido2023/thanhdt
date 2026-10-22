#!/usr/bin/env python3
"""Cò kích hoạt Livermore "đọc sống" — chạy T2-T6 SAU 19:01 ICT (DT5G publish xong).

Kích hoạt (đủ MỘT):
  (i)  DT gate candidate (dna_report.get_dt_gate_clock): need=25 với k>=15, hoặc need=10 với k>=5
       (MỌI candidate, kể cả NEUTRAL→BEAR);
  (ii) VNINDEX đóng cửa PHÁ đỉnh/đáy đóng cửa 252 phiên TRƯỚC, hoặc phá biên đóng cửa 60 phiên TRƯỚC.
Dedupe: cùng as-of chạy lại = no-op; khoảng cách tối thiểu TOÀN CỤC 20 phiên giữa mọi lần đọc (mọi loại, đo trên registry).
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
HI_LO_WIN, BREAK_WIN = 252, 60
RUN_TIMEOUT = int(os.environ.get("LIVERMORE_RUN_TIMEOUT") or 1200) if os.environ.get("LIVERMORE_TEST") == "1" else 1200
MIN_GAP = 20          # phiên: khoảng cách tối thiểu TOÀN CỤC giữa mọi lần đọc (chân 20 phiên không chồng)
STATE_FILE = lambda: os.path.join(C.STATE_DIR, "livermore_trigger.json")      # noqa: E731


def dt_kinds(clock):
    """Candidate đang tích luỹ: need==25 (VÀO CRISIS/EX-BULL) với k>=15; need==10 (mọi chuyển khác,
    kể cả NEUTRAL→BEAR) với k>=5."""
    if not clock or not clock.get("active"):
        return []
    cand, k, need, com = clock["cand"], clock["k"], clock["need"], clock.get("committed")
    if need == 25 and k >= ENTER_K:
        return [f"DT_ENTER_{STATE_NAME.get(cand, cand)}"]
    if need == 10 and k >= EXIT_K:
        return [f"DT_MOVE_{STATE_NAME.get(com, com)}_TO_{STATE_NAME.get(cand, cand)}"]
    return []


def price_kinds(closes):
    """closes: list close tăng dần, phần tử cuối = as-of. Đóng cửa PHÁ đỉnh/đáy đóng cửa 252 phiên
    TRƯỚC, hoặc phá biên đóng cửa 60 phiên TRƯỚC."""
    if len(closes) < HI_LO_WIN + 1:
        raise ValueError(f"cần >= {HI_LO_WIN + 1} bar, có {len(closes)}")
    c, out = closes[-1], []
    p252, p60 = closes[-HI_LO_WIN - 1:-1], closes[-BREAK_WIN - 1:-1]
    if c > max(p252):
        out.append("PRICE_BREAK252_UP")
    if c < min(p252):
        out.append("PRICE_BREAK252_DOWN")
    if c > max(p60):
        out.append("PRICE_BREAK60_UP")
    if c < min(p60):
        out.append("PRICE_BREAK60_DOWN")
    return out


def load_state():
    p = STATE_FILE()
    if not os.path.exists(p):
        return {"last_fired": {}, "runs": {}, "alerts": {}}
    with open(p, encoding="utf-8") as fh:
        st = json.load(fh)               # hỏng ⇒ raise (fail loud), không tự reset rồi bắn lặp
    st.setdefault("last_fired", {})
    st.setdefault("runs", {})
    st.setdefault("alerts", {})
    return st


def save_state(st):
    C.atomic_write(STATE_FILE(), json.dumps(st, indent=1, sort_keys=True) + "\n")


def gap_ok(as_of, entries, dates):
    """True nếu as-of cách lần đọc gần nhất TRƯỚC nó (mọi loại, theo registry) >= MIN_GAP phiên."""
    prev = [e["as_of"] for e in entries if e["as_of"] < as_of]
    if not prev:
        return True
    prev = max(prev)
    if prev in dates:
        return dates.index(as_of) - dates.index(prev) >= MIN_GAP
    n, d = 0, prev
    while d < as_of:
        d = C.next_session(d)
        n += 1
    return n >= MIN_GAP


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


def alert(kind, msg, st=None):
    """Báo lỗi kênh livermore, dedupe 1 lần / ngày ICT / loại (state['alerts']). Lỗi hỏng state vẫn báo (không dedupe)."""
    key = f"{C.today_ict()}|{kind}"
    if st is None:
        try:
            st = load_state()
        except Exception as ex:
            print(f"[trigger] WARN state hỏng ({ex}) — báo không dedupe", file=sys.stderr)
    if st is not None and key in st["alerts"]:
        print(f"[trigger] alert {kind} đã báo hôm nay — bỏ qua")
        return False
    if not notify(f"⚠️ Livermore — {msg}"):
        return False
    if st is not None:
        st["alerts"][key] = C.now_ict().isoformat(timespec="seconds")
        for k in [k for k in st["alerts"] if k[:10] < str(C.today_ict() - dt.timedelta(days=7))]:
            del st["alerts"][k]
        save_state(st)
    return True


def entry_summary(as_of):
    for e in C.parse_entries(C.read_registry()):
        if e["as_of"] == as_of:
            return (f"H20_DIR={e['dir']} P_UP={e['p_up']:.2f} LEVEL {e['level']} · đáo hạn {e['due']} "
                    f"(lịch {e['calendar']}) · báo cáo mike/data/livermore/{as_of}.md")
    return None


def run_livermore(as_of, kinds):
    binp = os.environ.get("LIVERMORE_RUN_BIN") or os.path.join(C.ROOT, "bin", "livermore_run.sh")
    try:
        r = subprocess.run([binp, "--as-of", str(as_of), "--triggers", ",".join(kinds)],
                           capture_output=True, text=True, timeout=RUN_TIMEOUT)
    except subprocess.TimeoutExpired:
        return 124, f"TIMEOUT {RUN_TIMEOUT}s — run_livermore không xong"
    return r.returncode, (r.stdout + r.stderr).strip()[-400:]


def run_score():
    """→ rc của scorer (0/20 = ổn); lỗi/timeout trả (rc hoặc 124, chi tiết)."""
    binp = os.environ.get("LIVERMORE_SCORE_BIN") or os.path.join(C.ROOT, "bin", "livermore_score.py")
    try:
        r = subprocess.run([sys.executable, binp, "--notify"], capture_output=True, text=True, timeout=300)
    except Exception as ex:
        print(f"[trigger] WARN score lỗi: {ex}", file=sys.stderr)
        return 124, f"{type(ex).__name__}: {ex}"
    print(f"[trigger] score rc={r.returncode}: " + (r.stdout.strip().splitlines() or [""])[-1][:200])
    if r.returncode not in (0, 20):
        print(f"[trigger] WARN score lỗi: {r.stderr.strip()[:300]}", file=sys.stderr)
    return r.returncode, r.stderr.strip()[-300:]


def evaluate(argv, clock_fn=real_clock):
    dry = "--dry-run" in argv
    today = C.today_ict()
    bars = C.get_bars(today - dt.timedelta(days=700))
    if len(bars) < HI_LO_WIN + 1:
        print(f"[trigger] LỖI chỉ có {len(bars)} bar (<{HI_LO_WIN + 1})", file=sys.stderr)
        alert("DATA", f"LỖI dữ liệu: chỉ có {len(bars)} bar VNINDEX (<{HI_LO_WIN + 1}) — cò không chạy được (rc=2)")
        return 2
    as_of = bars[-1]["time"]
    exp = C.expected_last_session()
    if as_of < exp:
        print(f"[trigger] STALE: bar cuối {as_of} < phiên kỳ vọng {exp} — không kích hoạt")
        alert("STALE", f"dữ liệu VNINDEX cũ: bar cuối {as_of} < phiên kỳ vọng {exp} — cò không kích hoạt (rc=3)")
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
    gap = C.has_entry(C.read_registry(), as_of) or gap_ok(as_of, C.parse_entries(C.read_registry()), dates)
    ok_kinds = kinds if gap else []
    print(f"[trigger] as-of={as_of} kích hoạt thô={kinds} sau khoảng-cách-{MIN_GAP}={ok_kinds} clock_ok={clock_ok}")
    rc = 0 if (clock_ok or ok_kinds) else 4
    if rc == 4 and not dry:
        alert("DTCLOCK", f"DT clock không dùng được cho as-of {as_of} (lỗi/lệch ngày) và không có kích hoạt giá — "
                         "điều kiện DT KHÔNG được kiểm hôm nay (rc=4)", st)
    if not ok_kinds or dry:
        return rc
    has = C.has_entry(C.read_registry(), as_of)
    if not has and run0 and run0.get("status") == "pending":
        alert(f"PENDING_{as_of}", f"{as_of}: lượt đọc trước dừng giữa chừng (state 'pending', chưa có entry) — chạy lại", st)
    if not has:
        st["runs"][str(as_of)] = {"kinds": ok_kinds, "status": "pending", "notified": False,
                                  "ts": C.now_ict().isoformat(timespec="seconds")}
        save_state(st)                       # ghi TRƯỚC khi gọi ngoài (§5)
        rcr, tail = run_livermore(as_of, ok_kinds)
        has = rcr == 0 and C.has_entry(C.read_registry(), as_of)
        if not has:
            st["runs"][str(as_of)]["status"] = "failed"
            save_state(st)
            alert(f"RUN_{as_of}", f"{as_of}: kích hoạt {','.join(ok_kinds)} nhưng đọc LỖI (rc={rcr}): {tail[-250:]}", st)
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
        alert("EXC", f"LỖI cò {type(ex).__name__}: {str(ex)[:250]} (rc=2)")
        rc = 2
    if "--dry-run" not in argv:
        src, tail = run_score()
        if src not in (0, 20):
            alert("SCORE", f"scorer lỗi rc={src}: {tail[-250:]}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
