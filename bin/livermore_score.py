#!/usr/bin/env python3
"""Chấm các entry Livermore đã đáo hạn (D+20 phiên) — append-only, idempotent.

Mỗi entry đến hạn + đủ 20 bar sau as-of → ghi 1 dòng `SCORE|...` vào registry (entry KHÔNG bị sửa).
Baseline: đồng xu 50% · "luôn UP" · DT5G-implied (state DT5G TẠI as-of, từ vnindex_5state_dt5g_live).
Cổng giải thể: ≥12 entry đã chấm mà Livermore KHÔNG hơn (hit VÀ Brier, nghiêm ngặt) cả 3 baseline
⇒ in "GIẢI THỂ ĐỀ XUẤT" (rc=20). Chỉ đề xuất — người quyết định.

Quy ước: y=1 nếu close[D+20] > close[D], ngược lại y=0 (bằng nhau = 0). hit = (dir==UP) == (y==1).
Brier = (P_UP − y)². "Luôn UP" = P_UP 1.0. DT5G-implied: P_UP = min(%vốn,100)/100 theo state
(1 CRISIS 0 · 2 BEAR .2 · 3 NEUTRAL .7 · 4 BULL 1 · 5 EX-BULL 1), dir=UP nếu P_UP ≥ .5.
"Hơn" baseline B = hit_L > hit_B VÀ Brier_L < Brier_B.

rc: 0 xong · 20 đề xuất giải thể · 1 lỗi.   Cờ: --notify (báo kênh Livermore khi có dòng chấm mới / giải thể),
--dry-run (không ghi), --today YYYY-MM-DD (chỉ khi LIVERMORE_TEST=1).
"""
import datetime as dt
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import livermore_common as C                                   # noqa: E402

GATE_N = 12
DT5G_P = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.0}


def score_entry(e, bars, dt5g_state):
    """→ dict kết quả, hoặc None nếu chưa đủ bar. Raise nếu as-of lệch dữ liệu."""
    idx = {b["time"]: i for i, b in enumerate(bars)}
    if e["as_of"] not in idx:
        raise RuntimeError(f"{e['as_of']}: không có bar as-of trong dữ liệu chấm")
    i0 = idx[e["as_of"]]
    if abs(bars[i0]["close"] - e["close"]) > 0.01:
        raise RuntimeError(f"{e['as_of']}: close as-of lệch (sổ {e['close']} vs dữ liệu {bars[i0]['close']})")
    if i0 + C.HORIZON >= len(bars):
        return None
    b20 = bars[i0 + C.HORIZON]
    y = 1 if b20["close"] > bars[i0]["close"] else 0
    hit = int((e["dir"] == "UP") == (y == 1))
    r = {"as_of": e["as_of"], "d20": b20["time"], "close0": bars[i0]["close"], "close20": b20["close"],
         "ret": b20["close"] / bars[i0]["close"] - 1, "dir": e["dir"], "p_up": e["p_up"], "y": y,
         "hit": hit, "brier": (e["p_up"] - y) ** 2, "drift": (b20["time"] - e["due"]).days,
         "dt5g_state": dt5g_state}
    r["up_hit"], r["up_brier"] = int(y == 1), (1.0 - y) ** 2
    r["coin_hit"], r["coin_brier"] = 0.5, 0.25
    if dt5g_state in DT5G_P:
        p = DT5G_P[dt5g_state]
        r["dt_hit"], r["dt_brier"] = int((p >= 0.5) == (y == 1)), (p - y) ** 2
    else:
        r["dt_hit"] = r["dt_brier"] = None
    return r


def score_line(r):
    f = lambda v: "NA" if v is None else (f"{v:.4f}" if isinstance(v, float) else str(v))
    return (f"SCORE|{r['as_of']}|d20={r['d20']}|close0={r['close0']}|close20={r['close20']}|ret={r['ret']:.4f}"
            f"|dir={r['dir']}|p_up={r['p_up']:.2f}|y={r['y']}|hit={r['hit']}|brier={r['brier']:.4f}"
            f"|dt5g_state={f(r['dt5g_state'])}|dt5g_hit={f(r['dt_hit'])}|dt5g_brier={f(r['dt_brier'])}"
            f"|due_drift_days={r['drift']}")


def parse_score_line(line):
    kv = dict(p.split("=", 1) for p in line.split("|")[2:])
    num = lambda s: None if s == "NA" else float(s)
    return {"hit": int(kv["hit"]), "brier": float(kv["brier"]), "y": int(kv["y"]),
            "dt_hit": num(kv["dt5g_hit"]), "dt_brier": num(kv["dt5g_brier"])}


def cumulative(rows):
    """rows: list dict có hit,brier,y,dt_hit,dt_brier → bảng lũy kế + verdict từng baseline."""
    n = len(rows)
    if n == 0:
        return {"n": 0}
    m = lambda k: sum(r[k] for r in rows) / n
    L = (m("hit"), m("brier"))
    up = (sum(r["y"] for r in rows) / n, sum((1 - r["y"]) ** 2 for r in rows) / n)
    coin = (0.5, 0.25)
    dtr = [r for r in rows if r["dt_hit"] is not None]
    dtb = (sum(r["dt_hit"] for r in dtr) / len(dtr), sum(r["dt_brier"] for r in dtr) / len(dtr)) if dtr else None
    # so Livermore với DT5G chỉ trên các entry có state DT5G
    L_dt = (sum(r["hit"] for r in dtr) / len(dtr), sum(r["brier"] for r in dtr) / len(dtr)) if dtr else None
    beats = {"coin": L[0] > coin[0] and L[1] < coin[1], "always_up": L[0] > up[0] and L[1] < up[1],
             "dt5g": bool(dtb and L_dt[0] > dtb[0] and L_dt[1] < dtb[1])}
    return {"n": n, "L": L, "coin": coin, "up": up, "dt5g": dtb, "L_vs_dt5g": L_dt, "n_dt5g": len(dtr),
            "beats": beats, "dissolve": n >= GATE_N and not any(beats.values())}


def render(c):
    if c["n"] == 0:
        return "Chưa có entry nào được chấm."
    t = lambda x: "NA" if x is None else f"hit {x[0]:.1%} · Brier {x[1]:.3f}"
    out = [f"Lũy kế {c['n']} entry đã chấm (cổng giải thể cần ≥{GATE_N}):",
           f"  Livermore      : {t(c['L'])}",
           f"  Đồng xu 50%    : {t(c['coin'])}   → hơn? {'CÓ' if c['beats']['coin'] else 'KHÔNG'}",
           f"  Luôn UP        : {t(c['up'])}   → hơn? {'CÓ' if c['beats']['always_up'] else 'KHÔNG'}",
           f"  DT5G-implied   : {t(c['dt5g'])} (n={c['n_dt5g']}; Livermore cùng tập: {t(c['L_vs_dt5g'])})"
           f"   → hơn? {'CÓ' if c['beats']['dt5g'] else 'KHÔNG'}"]
    if c["dissolve"]:
        out.append(f"GIẢI THỂ ĐỀ XUẤT: sau {c['n']} entry, Livermore không hơn cả 3 baseline (hit VÀ Brier).")
    elif c["n"] < GATE_N:
        out.append(f"Cổng giải thể: chưa đánh giá (còn {GATE_N - c['n']} entry).")
    else:
        out.append("Cổng giải thể: không đề xuất (hơn ít nhất 1 baseline).")
    return "\n".join(out)


def notify(msg):
    chan = os.environ.get("DISCORD_THREAD_ID_LIVERMORE") or "livermore"
    binp = os.environ.get("LIVERMORE_NOTIFY_BIN") or os.path.join(C.ROOT, "bin", "notify_thread.sh")
    try:
        r = subprocess.run([binp, msg, chan], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            print(f"[score] WARN notify rc={r.returncode}: {r.stderr.strip()[:200]}", file=sys.stderr)
    except Exception as ex:                                     # WARN-only
        print(f"[score] WARN notify lỗi: {ex}", file=sys.stderr)


def main(argv):
    dry = "--dry-run" in argv
    today = C.today_ict()
    if "--today" in argv and os.environ.get("LIVERMORE_TEST") == "1":
        today = dt.date.fromisoformat(argv[argv.index("--today") + 1])
    text = C.read_registry()
    entries = C.parse_entries(text)
    done = C.parse_scores(text)
    new, pending = [], []
    for e in entries:
        if str(e["as_of"]) in done:
            continue
        if today < e["due"]:
            pending.append(e)
            continue
        bars = C.get_bars(e["as_of"], e["due"] + dt.timedelta(days=14))
        try:
            r = score_entry(e, bars, C.get_dt5g_state(e["as_of"]))
        except RuntimeError as ex:
            print(f"[score] LỖI {ex}", file=sys.stderr)
            return 1
        if r is None:
            print(f"[score] {e['as_of']}: đến hạn {e['due']} nhưng chưa đủ {C.HORIZON} bar sau as-of — chờ dữ liệu")
            pending.append(e)
            continue
        line = score_line(r)
        if not dry:
            C.locked_append(C.REGISTRY, line + "\n",
                            guard=lambda c, a=str(e["as_of"]): f"SCORE|{a}|" in c)
        new.append(line)
        print(f"[score] {line}")
    rows = [parse_score_line(l) for l in C.parse_scores(C.read_registry() if not dry else text).values()]
    rows += [parse_score_line(l) for l in new] if dry else []
    c = cumulative(rows)
    table = render(c)
    print(table)
    print(f"[score] chờ đáo hạn/dữ liệu: {len(pending)} entry")
    if not dry:
        C.atomic_write(os.path.join(C.DATA_DIR, "scoreboard.md"),
                       f"# Livermore scoreboard (sinh tự động {C.now_ict().isoformat(timespec='seconds')})\n\n```\n{table}\n```\n")
    if "--notify" in argv and not dry and (new or c.get("dissolve")):
        notify("Livermore — chấm " + (f"{len(new)} entry mới.\n" if new else "") + table)
    return 20 if c.get("dissolve") else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
