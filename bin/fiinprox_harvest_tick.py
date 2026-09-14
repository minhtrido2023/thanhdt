#!/usr/bin/env python3
"""fiinprox_harvest_tick.py — hàng đợi harvest FiinPro-X tự động (cron 3 lần/giờ).

Mỗi tick lấy ĐÚNG 1 task pending trong `state/fiinprox_harvest/queue.json`, chạy headless
`claude -p --allowedTools mcp__claude_ai_FiinXMCP__execute_api` với đoạn code sandbox cố định,
đọc NGUYÊN VĂN tool_result từ `--output-format stream-json` (model không chép lại số), kiểm tra
rồi ghi file raw atomic. Kế hoạch + nhật ký: kb/projects/fiinprox-trial-harvest-plan-20260914.md.

Chống giới hạn (đo thật 14/09): lô 30 mã get_freefloat → 504; lô 20 mã OK; ~6-7 lô/giờ → 429
"hourly request limit". Nhịp 1 lô/tick × 3 tick/giờ = 60 mã/giờ, dưới ngưỡng.
- 429 / "request limit"  → cooldown 65 phút, task giữ pending (không tính attempt).
- [Errno 28] sandbox đầy → thử lại tick sau (model tự thử tối đa 3 lần/tick); KHÔNG làm task failed.
- 504 / Gateway Timeout   → tách lô làm đôi.
- lỗi khác (validate, ERROR) ≥ 6 lần → failed + báo thread.
- Sau 2026-09-27 23:59 ICT (trial hết 28/09) → không chạy nữa.

Dùng:
  fiinprox_harvest_tick.py init      # dựng hàng đợi (idempotent, bỏ qua task/file đã có)
  fiinprox_harvest_tick.py tick      # cron gọi
  fiinprox_harvest_tick.py status
  fiinprox_harvest_tick.py tick --dry-run   # in prompt, không gọi claude
"""
import argparse
import fcntl
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../mike
STATE = os.path.join(ROOT, "state", "fiinprox_harvest")
QUEUE = os.path.join(STATE, "queue.json")
LOG = os.path.join(STATE, "log.jsonl")
LOCK = os.path.join(STATE, "tick.lock")
COOLDOWN = os.path.join(STATE, "cooldown_until")
DONE_FLAG = os.path.join(STATE, "all_done_notified")
TICKERS = os.path.join(ROOT, "data", "fiinprox_oshares_raw", "tickers.txt")
DEADLINE = datetime(2026, 9, 27, 23, 59, tzinfo=ICT)
MAX_ATTEMPTS = 6
USAGE_SKIP_PCT = 85
OSHARES_START = 70      # 0..69 đã harvest tay 14/09 (b000..b050)
OSHARES_BATCH = 20

CODE_OSHARES = '''TICKERS=__TICKERS__
d=pd.DataFrame(client.PriceStatistics().get_freefloat(tickers=TICKERS, from_date="2013-01-01", to_date="__TO__"))
out=[]
for t in TICKERS:
    g=d[d.ticker==t].sort_values('timestamp') if len(d) else d
    s=g[['timestamp','outstanding_share']].dropna() if len(g) else g
    if len(s)==0:
        out.append(t+"|NA"); continue
    v=s['outstanding_share'].astype('int64').tolist(); ts=s['timestamp'].str[2:10].str.replace('-','').tolist()
    segs=[]
    for i,x in enumerate(v):
        if segs and segs[-1][1]==x: segs[-1][2]+=1
        else: segs.append([ts[i],x,1])
    blips=0; changed=True
    while changed:
        changed=False
        for k in range(1,len(segs)-1):
            if segs[k][2]<=5 and segs[k-1][1]==segs[k+1][1]:
                segs[k-1][2]+=segs[k][2]+segs[k+1][2]; del segs[k:k+2]; blips+=1; changed=True; break
    parts=[f"{segs[0][0]}:{segs[0][1]}"]
    for k in range(1,len(segs)):
        dlt=segs[k][1]-segs[k-1][1]; parts.append(f"{segs[k][0]}:{'+' if dlt>0 else ''}{dlt}")
    out.append(f"{t}|n{len(s)}|b{blips}|"+";".join(parts))
print("\\n".join(out))'''

CODE_FX = '''d=pd.DataFrame(client.economy.currency.list_exchange_rates(time_frequency="Monthly", from_date="__Y__-01-01", to_date="__Y__-12-31"))
d=d[d.currency_code=='USD']; d['m']=d.trading_date_id.str[:7]
g=d.sort_values('trading_date_id').groupby(['m','organization_short_name']).last()
def col(org,c):
    try: return g.xs(org,level=1)[c]
    except KeyError: return pd.Series(dtype=float)
o=pd.DataFrame({'central':col('Tỷ giá trung tâm (USD)','ask_rate'),'vcb_bid_tf':col('Vietcombank','bid_rate_transfer'),'vcb_ask':col('Vietcombank','ask_rate'),'free_ask':col('Thị trường tự do (USD)','ask_rate'),'sbv_ask':col('Ngân Hàng Nhà Nước Việt Nam','ask_rate')})
print("#fx __Y__",len(o))
for m,r in o.sort_index().iterrows():
    print(m+","+",".join("" if pd.isna(x) else str(int(round(x))) for x in r.tolist()))'''


def now():
    return datetime.now(ICT)


def log(event, **kw):
    os.makedirs(STATE, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps({"ts": now().isoformat(timespec="seconds"), "event": event, **kw}, ensure_ascii=False) + "\n")


def atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def load_queue():
    if not os.path.exists(QUEUE):
        return []
    with open(QUEUE) as f:
        return json.load(f)


def save_queue(q):
    atomic_write(QUEUE, json.dumps(q, ensure_ascii=False, indent=1))


def notify(msg):
    sh = os.path.join(ROOT, "bin", "notify_thread.sh")
    subprocess.run([sh, msg, "vn_macro_watch"], check=False)


def cmd_init():
    q = load_queue()
    ids = {t["id"] for t in q}
    tickers = open(TICKERS).read().split()
    added = 0
    for i in range(OSHARES_START, len(tickers), OSHARES_BATCH):
        tid = f"oshares_b{i:03d}"
        out = f"data/fiinprox_oshares_raw/b{i:03d}.txt"
        if tid in ids or os.path.exists(os.path.join(ROOT, out)):
            continue
        q.append({"id": tid, "kind": "oshares", "tickers": tickers[i:i + OSHARES_BATCH], "out": out,
                  "status": "pending", "attempts": 0, "last_error": None, "done_at": None})
        added += 1
    for y in range(2012, 2027):
        tid = f"fx_{y}"
        out = f"data/fiinprox_fx_raw/usd_{y}.txt"
        if tid in ids or os.path.exists(os.path.join(ROOT, out)):
            continue
        q.append({"id": tid, "kind": "fx", "year": y, "out": out,
                  "status": "pending", "attempts": 0, "last_error": None, "done_at": None})
        added += 1
    save_queue(q)
    print(f"queue: +{added} task, tổng {len(q)}")


def build_code(task):
    if task["kind"] == "oshares":
        return CODE_OSHARES.replace("__TICKERS__", repr(task["tickers"])).replace("__TO__", now().strftime("%Y-%m-%d"))
    return CODE_FX.replace("__Y__", str(task["year"]))


def build_prompt(code):
    return (
        "Bạn là bước tải dữ liệu tự động. Gọi tool mcp__claude_ai_FiinXMCP__execute_api với tham số `code` "
        "CHÍNH XÁC là đoạn giữa hai dòng <<<CODE và CODE>>> (không sửa, không thêm bớt ký tự nào).\n"
        "- Nếu kết quả tool chứa 'No space left on device' hoặc '504' hoặc 'Gateway Timeout': gọi lại y hệt, "
        "tối đa 3 lần gọi tổng cộng.\n"
        "- Nếu kết quả chứa '429' hoặc 'request limit': DỪNG ngay, không gọi lại.\n"
        "- Không gọi tool nào khác. Không tóm tắt dữ liệu. Cuối cùng chỉ trả lời một chữ: DONE.\n"
        "<<<CODE\n" + code + "\nCODE>>>"
    )


def tool_results(stream_text):
    """Trả list chuỗi tool_result của execute_api, theo thứ tự."""
    res = []
    for line in stream_text.splitlines():
        try:
            j = json.loads(line)
        except ValueError:
            continue
        if j.get("type") != "user":
            continue
        for c in j.get("message", {}).get("content", []) or []:
            if not isinstance(c, dict) or c.get("type") != "tool_result":
                continue
            content = c.get("content")
            if isinstance(content, list):
                texts = [x.get("text", "") for x in content if isinstance(x, dict) and x.get("type") == "text"]
                if not texts:
                    continue  # tool_reference (ToolSearch), bỏ qua
                content = "\n".join(texts)
            if isinstance(content, str):
                res.append(content)
    return res


def classify(raw):
    """→ (kind, stdout_or_error)."""
    txt = raw
    try:
        j = json.loads(raw)
        if isinstance(j, dict) and "result" in j:
            txt = j["result"]
    except ValueError:
        pass
    low = txt.lower()
    if "429" in txt or "request limit" in low:
        return "RATE_LIMIT", txt[-300:]
    if "no space left on device" in low:
        return "DISK", txt[-200:]
    if "504" in txt or "gateway timeout" in low:
        return "TIMEOUT", txt[-200:]
    if "Success: True" in txt and "Stdout:" in txt:
        out = txt.split("Stdout:", 1)[1]
        out = out.split("\n\nStderr:", 1)[0]
        return "OK", out.strip("\n")
    return "ERROR", txt[-400:]


def validate(task, out):
    lines = [l for l in out.splitlines() if l.strip()]
    if task["kind"] == "oshares":
        got = [l.split("|", 1)[0] for l in lines if "|" in l]
        if got != task["tickers"]:
            return f"ticker lệch: cần {len(task['tickers'])}, nhận {len(got)}"
        return None
    data = [l for l in lines if not l.startswith("#")]
    if not lines or not lines[0].startswith(f"#fx {task['year']}"):
        return "thiếu header #fx"
    if any(l.count(",") != 5 for l in data):
        return "dòng fx sai số cột"
    return None


def usage_pct():
    try:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "bin", "usage_watch.py"), "--oneline"],
                           capture_output=True, text=True, timeout=60)
        return int(r.stdout.split()[0])
    except (ValueError, IndexError, subprocess.SubprocessError, OSError):
        return None


def cmd_status():
    q = load_queue()
    from collections import Counter
    c = Counter((t["kind"], t["status"]) for t in q)
    for k in sorted(c):
        print(k, c[k])
    if os.path.exists(COOLDOWN):
        print("cooldown_until", open(COOLDOWN).read().strip())


def cmd_tick(dry_run=False, model="sonnet"):
    os.makedirs(STATE, exist_ok=True)
    lockf = open(LOCK, "w")
    try:
        fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("tick khác đang chạy — bỏ qua")
        return 0
    if now() > DEADLINE:
        print("quá hạn trial — không chạy")
        return 0
    if os.path.exists(COOLDOWN):
        until = datetime.fromisoformat(open(COOLDOWN).read().strip())
        if now() < until:
            print(f"cooldown tới {until.isoformat(timespec='minutes')}")
            return 0
        os.remove(COOLDOWN)
    q = load_queue()
    pending = [t for t in q if t["status"] == "pending"]
    if not pending:
        if q and not os.path.exists(DONE_FLAG):
            done = sum(t["status"] == "done" for t in q)
            failed = [t["id"] for t in q if t["status"] == "failed"]
            notify(f"FiinPro harvest tự động: hàng đợi xong — {done} task done, {len(failed)} failed {failed[:10]}. "
                   "Chờ Mike dựng CSV + đối chiếu + registry.")
            atomic_write(DONE_FLAG, now().isoformat())
        print("hàng đợi trống")
        return 0
    pct = usage_pct()
    if pct is not None and pct >= USAGE_SKIP_PCT:
        log("skip_usage", pct=pct)
        print(f"usage {pct}% ≥ {USAGE_SKIP_PCT}% — nhường quota cho fleet")
        return 0
    task = pending[0]
    code = build_code(task)
    prompt = build_prompt(code)
    if dry_run:
        print(prompt)
        return 0
    try:
        r = subprocess.run(
            ["claude", "-p", prompt, "--model", model,
             "--allowedTools", "mcp__claude_ai_FiinXMCP__execute_api",
             "--output-format", "stream-json", "--verbose"],
            capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL, cwd=STATE)
        stream = r.stdout
    except subprocess.TimeoutExpired as e:
        stream = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        log("claude_timeout", task=task["id"])
    atomic_write(os.path.join(STATE, "last_stream.jsonl"), stream)
    results = tool_results(stream)
    if not results:
        kind, detail = "ERROR", f"không có tool_result (claude rc/stderr: {stream[-300:]!r})"
    else:
        # ưu tiên kết quả OK nếu có trong các lần thử
        classified = [classify(x) for x in results]
        ok = [c for c in classified if c[0] == "OK"]
        kind, detail = ok[-1] if ok else classified[-1]
    if kind == "OK":
        err = validate(task, detail)
        if err:
            kind, detail = "ERROR", f"validate: {err}"
        else:
            atomic_write(os.path.join(ROOT, task["out"]), detail + "\n")
            task.update(status="done", done_at=now().isoformat(timespec="seconds"), last_error=None)
            save_queue(q)
            log("done", task=task["id"], lines=len(detail.splitlines()), calls=len(results))
            left = sum(t["status"] == "pending" for t in q)
            same_kind_left = sum(t["status"] == "pending" and t["kind"] == task["kind"] for t in q)
            if same_kind_left == 0:
                notify(f"FiinPro harvest tự động: xong toàn bộ nhóm `{task['kind']}` (task cuối {task['id']}). "
                       f"Còn {left} task nhóm khác.")
            print(f"OK {task['id']}")
            return 0
    if kind == "RATE_LIMIT":
        until = now() + timedelta(minutes=65)
        atomic_write(COOLDOWN, until.isoformat(timespec="seconds"))
        log("rate_limit", task=task["id"], until=until.isoformat(timespec="minutes"), detail=detail)
        print(f"429 — cooldown tới {until.isoformat(timespec='minutes')}")
        return 0
    if kind == "TIMEOUT" and task["kind"] == "oshares" and len(task["tickers"]) > 5:
        half = len(task["tickers"]) // 2
        base = task["id"]
        a = dict(task, id=base + "a", tickers=task["tickers"][:half], out=task["out"].replace(".txt", "a.txt"),
                 attempts=0, last_error=None)
        b = dict(task, id=base + "b", tickers=task["tickers"][half:], out=task["out"].replace(".txt", "b.txt"),
                 attempts=0, last_error=None)
        idx = q.index(task)
        q[idx:idx + 1] = [a, b]
        save_queue(q)
        log("split", task=base)
        print(f"504 — tách {base} thành 2 lô")
        return 0
    task["attempts"] += 1
    task["last_error"] = f"{kind}: {detail}"[:500]
    # [Errno 28] là lỗi hạ tầng phía FiinX, không phải lỗi của task ⇒ không đẩy task sang failed.
    if kind != "DISK" and task["attempts"] >= MAX_ATTEMPTS:
        task["status"] = "failed"
        notify(f"FiinPro harvest tự động: task `{task['id']}` FAILED sau {MAX_ATTEMPTS} lần — {kind}: {detail[:200]}")
    save_queue(q)
    log("fail", task=task["id"], kind=kind, attempts=task["attempts"], calls=len(results), detail=detail[:300])
    print(f"{kind} {task['id']} attempt {task['attempts']}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init", "tick", "status"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--model", default="sonnet")
    a = ap.parse_args()
    if a.cmd == "init":
        cmd_init()
    elif a.cmd == "status":
        cmd_status()
    else:
        return cmd_tick(a.dry_run, a.model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
