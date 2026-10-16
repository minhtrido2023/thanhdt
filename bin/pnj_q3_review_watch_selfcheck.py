#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pnj_q3_review_watch_selfcheck.py — self-check cho bin/pnj_q3_review_watch.py.

Offline hoàn toàn (BQ/bus/Discord đều giả lập, state trong thư mục tạm) — KHÔNG post gì thật.
`--live` thêm 1 lượt `--dry-run` chạm BQ thật (chỉ đọc; không post, không ghi state).
`PNJW_TARGET=<đường dẫn bản cần kiểm>` cho mutation test. Nên chạy dưới `env -u TZ` + 1 TZ lạ.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.abspath(os.environ.get("PNJW_TARGET") or os.path.join(HERE, "pnj_q3_review_watch.py"))
_spec = importlib.util.spec_from_file_location("pnj_q3_review_watch_under_test", TARGET)
W = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(W)

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  PASS  {name}")
    else:
        FAIL += 1; print(f"  FAIL  {name}  {detail}")


class World:
    """Thế giới giả: BQ trả `det`, bus + Discord là 2 danh sách đếm được."""
    def __init__(self, n=0, release="2026-10-27"):
        self.dir = tempfile.mkdtemp(prefix="pnjw_")
        self.state = os.path.join(self.dir, "state.json")
        self.det = {"n": n, "release_date": release if n else None, "time": release if n else None}
        self.bus, self.discord, self.queries, self.logs = [], [], 0, []
        self.query_exc = self.bus_has_exc = self.bus_post_exc = self.discord_exc = None
        self.bus_post_lands_then_raises = False

    def query(self):
        self.queries += 1
        if self.query_exc:
            raise self.query_exc
        return self.det

    def bus_has(self):
        if self.bus_has_exc:
            raise self.bus_has_exc
        return len(self.bus) > 0

    def post_bus(self, payload):
        if self.bus_post_exc:
            raise self.bus_post_exc
        self.bus.append(payload)
        if self.bus_post_lands_then_raises:
            raise SystemExit("bị kill ngay sau khi event đã lên bus")

    def post_discord(self, msg):
        if self.discord_exc:
            raise self.discord_exc
        self.discord.append(msg)

    def run(self, **kw):
        return W.run(state_path=self.state, query_fn=self.query, bus_has_fn=self.bus_has,
                     post_bus_fn=self.post_bus, post_discord_fn=self.post_discord,
                     out=self.logs.append, **kw)

    def st(self):
        with open(self.state, encoding="utf-8") as f:
            return json.load(f)

    def leftovers(self):
        return [f for f in os.listdir(self.dir) if f != "state.json"]


print("=" * 78); print("  1. chưa có PNJ Q3 → im lặng"); print("=" * 78)
w = World(n=0)
r = w.run()
check("1a n=0 → not_yet", r == "not_yet", r)
check("1b không post bus, không Discord, không tạo state, không in gì",
      not w.bus and not w.discord and not os.path.exists(w.state) and not w.logs, f"{w.bus} {w.discord} {w.logs}")
for _ in range(3):
    w.run()
check("1c chạy lại 3 lần vẫn im lặng", not w.bus and not w.discord and not os.path.exists(w.state))

print("=" * 78); print("  2. có PNJ Q3 → bắn ĐÚNG 1 lần"); print("=" * 78)
w = World(n=1)
r = w.run()
check("2a n=1 → fired", r == "fired", r)
check("2b đúng 1 bus question + đúng 1 Discord", len(w.bus) == 1 and len(w.discord) == 1, f"{len(w.bus)} {len(w.discord)}")
p = w.bus[0] if w.bus else {}
blob = json.dumps(p, ensure_ascii=False)
check("2c payload: target Mike, nêu current_ops + 09-30 + BCTC Q3 + fundamental-skeptic + KHÔNG tự khôi phục",
      p.get("target") == "Mike" and "kb/current_ops.md" in blob and "2026-09-30" in blob and "2026Q3" in blob
      and "fundamental-skeptic" in blob and "KHÔNG tự khôi phục" in blob and "excluded_tickers" in blob, blob[:300])
check("2d payload mang bằng chứng đo được (ngày công bố, số dòng)",
      p.get("evidence", {}).get("release_date") == "2026-10-27" and p.get("evidence", {}).get("n_rows") == 1, f"{p.get('evidence')}")
check("2e Discord nêu mã, quý, ngày, 'KHÔNG tự khôi phục', topic bus",
      w.discord and all(k in w.discord[0] for k in ("PNJ", "2026Q3", "2026-10-27", "KHÔNG tự khôi phục", W.TOPIC)), f"{w.discord}")
st = w.st()
check("2f state: 2 mốc thời gian neo ICT (+07:00), discord_ok, đúng mã/quý",
      st.get("ticker") == "PNJ" and st.get("quarter") == "2026Q3" and str(st.get("bus_posted_at", "")).endswith("+07:00")
      and str(st.get("discord_attempted_at", "")).endswith("+07:00") and st.get("discord_ok") is True, f"{st}")
check("2g không để lại file tạm", w.leftovers() == [], f"{w.leftovers()}")
check("2h topic/agent/kênh đúng hằng số", W.TOPIC == "pnj-bctc-q3-review-trigger" and W.TICKER == "PNJ"
      and W.QUARTER == "2026Q3" and W.DISCORD_CHANNEL == "trading_daily")

print("=" * 78); print("  3. chạy lại → KHÔNG lặp"); print("=" * 78)
q0 = w.queries
rs = [w.run() for _ in range(5)]
check("3a 5 lượt sau đều already_fired", rs == ["already_fired"] * 5, f"{rs}")
check("3b vẫn 1 bus + 1 Discord", len(w.bus) == 1 and len(w.discord) == 1, f"{len(w.bus)} {len(w.discord)}")
check("3c đã bắn rồi thì không truy vấn BQ nữa", w.queries == q0, f"{w.queries} vs {q0}")

print("=" * 78); print("  4. lỗi đọc → fail-closed, không spam"); print("=" * 78)
w = World(n=1); w.query_exc = RuntimeError("bq exit=1: quota")
r = w.run()
check("4a BQ lỗi → query_failed, 0 post, 0 state", r == "query_failed" and not w.bus and not w.discord and not os.path.exists(w.state), r)
check("4b … log mang LỖI THẬT (§29)", any("quota" in l for l in w.logs), f"{w.logs}")
for bad in (None, [], {"n": "1"}, {"release_date": "x"}, "1"):
    w = World(n=1); w.det = bad
    r = w.run()
    check(f"4c kết quả truy vấn sai hình dạng {bad!r} → query_failed, 0 post", r == "query_failed" and not w.bus and not w.discord, r)
w = World(n=1); w.det = {"n": -1, "release_date": None, "time": None}
check("4d n âm → not_yet, 0 post", w.run() == "not_yet" and not w.bus)

for nm, content in (("JSON hỏng", "{not json"), ("rỗng", ""), ("mảng", "[1,2]"), ("chuỗi", '"fired"'),
                    ("của mã khác", json.dumps({"ticker": "DGC", "quarter": "2026Q3", "bus_posted_at": "x"})),
                    ("của quý khác", json.dumps({"ticker": "PNJ", "quarter": "2026Q2", "bus_posted_at": "x"}))):
    w = World(n=1)
    with open(w.state, "w", encoding="utf-8") as f:
        f.write(content)
    r = w.run()
    with open(w.state, encoding="utf-8") as f:
        same = f.read() == content
    check(f"4e state {nm} → state_unreadable, 0 post, file giữ nguyên, có log lỗi",
          r == "state_unreadable" and not w.bus and not w.discord and same and w.logs and w.queries == 0, f"{r} {w.logs}")

w = World(n=1); w.bus_has_exc = OSError("bus không đọc được")
r = w.run()
check("4f không quét được bus → bus_unreadable, 0 post, 0 state",
      r == "bus_unreadable" and not w.bus and not w.discord and not os.path.exists(w.state), r)

print("=" * 78); print("  5. bị kill / lỗi giữa chừng → không lặp (§5)"); print("=" * 78)
# 5a — post bus lỗi TRƯỚC khi lên bus: chưa ghi state, lượt sau bắn bình thường đúng 1 lần
w = World(n=1); w.bus_post_exc = RuntimeError("append_event.sh exit=1")
r1 = w.run(); w.bus_post_exc = None; r2 = w.run(); r3 = w.run()
check("5a post bus lỗi → bus_post_failed, rồi fired đúng 1 lần", (r1, r2, r3) == ("bus_post_failed", "fired", "already_fired")
      and len(w.bus) == 1 and len(w.discord) == 1, f"{r1} {r2} {r3} bus={len(w.bus)} dc={len(w.discord)}")
# 5b — kill NGAY SAU khi event đã lên bus, trước khi ghi state: lượt sau hỏi bus, không post lần 2
w = World(n=1); w.bus_post_lands_then_raises = True
try:
    w.run(); killed = False
except SystemExit:
    killed = True
check("5b-0 mô phỏng kill sau khi post bus: 1 event trên bus, CHƯA có state", killed and len(w.bus) == 1 and not os.path.exists(w.state))
w.bus_post_lands_then_raises = False
r = w.run()
check("5b lượt sau: KHÔNG post bus lần 2 (hỏi lại bus), Discord gửi 1 lần, state ghi bus_found_existing",
      r == "fired" and len(w.bus) == 1 and len(w.discord) == 1 and w.st().get("bus_found_existing") is True,
      f"{r} bus={len(w.bus)} dc={len(w.discord)}")
# 5c — kill giữa dấu 'đã thử Discord' và lúc gửi: KHÔNG gửi lại (tối đa một lần), bus vẫn còn
w = World(n=1); w.discord_exc = SystemExit("kill khi đang gửi Discord")
try:
    w.run(); killed = False
except SystemExit:
    killed = True
w.discord_exc = None
st_mid = w.st()
r = w.run()
check("5c kill khi gửi Discord → state đã có discord_attempted_at; lượt sau already_fired, 0 Discord, 1 bus",
      killed and st_mid.get("discord_attempted_at") and r == "already_fired" and len(w.discord) == 0 and len(w.bus) == 1,
      f"killed={killed} {st_mid} {r}")
# 5d — Discord lỗi thường: ghi discord_ok=False + lỗi thật, KHÔNG gửi lại
w = World(n=1); w.discord_exc = RuntimeError("notify_thread.sh exit=1: 502")
r1 = w.run(); w.discord_exc = None; r2 = w.run()
st = w.st()
check("5d Discord lỗi → fired (bus có), discord_ok=False + lỗi thật trong state và log; không gửi lại",
      r1 == "fired" and r2 == "already_fired" and len(w.bus) == 1 and len(w.discord) == 0 and st.get("discord_ok") is False
      and "502" in st.get("discord_error", "") and any("502" in l for l in w.logs), f"{r1} {r2} {st}")
# 5e — dòng PNJ biến mất khỏi BQ sau khi đã post bus (restate) vẫn hoàn tất Discord từ `detected` đã lưu
w = World(n=1); w.discord_exc = SystemExit("kill")
try:
    w.run()
except SystemExit:
    pass
st = w.st(); st.pop("discord_attempted_at", None)
W.save_state(w.state, st)          # giả lập: kill sau khi ghi bus_posted_at, TRƯỚC dấu Discord
w.discord_exc = None; w.det = {"n": 0, "release_date": None, "time": None}
r = w.run()
check("5e đã post bus, BQ sau đó trả n=0 → vẫn gửi Discord 1 lần từ `detected` đã lưu, bus không lặp",
      r == "fired" and len(w.discord) == 1 and len(w.bus) == 1 and "2026-10-27" in w.discord[0], f"{r} {w.discord}")

print("=" * 78); print("  6. ghi state nguyên tử"); print("=" * 78)
w = World(n=1)
W.save_state(w.state, {"ticker": "PNJ", "quarter": "2026Q3", "v": 1})
before = open(w.state, encoding="utf-8").read()
_orig_replace = os.replace
def _boom_replace(a, b):
    raise OSError("kill giữa lúc đổi tên")
os.replace = _boom_replace
try:
    W.save_state(w.state, {"ticker": "PNJ", "quarter": "2026Q3", "v": 2}); raised = False
except OSError:
    raised = True
finally:
    os.replace = _orig_replace
check("6a kill trước os.replace → file state CŨ còn nguyên, đọc được", raised and open(w.state, encoding="utf-8").read() == before
      and W.load_state(w.state)[1] is None)
src = open(TARGET, encoding="utf-8").read()
check("6b nguồn: ghi qua tmp + os.replace, chỉ MỘT chỗ mở file để ghi, không xoá file nào",
      src.count('open(tmp, "w"') == 1 and src.count(', "w"') == 1 and "os.replace(tmp, path)" in src
      and "os.remove" not in src and "unlink" not in src)
check("6c nguồn: không import/ghi gì vào cấu hình account (excluded_tickers chỉ xuất hiện trong văn bản)",
      "trading_bot" not in src.replace("secrets/trading_bot_accounts.json", "") and "load_accounts" not in src)

print("=" * 78); print("  7. dry-run"); print("=" * 78)
w = World(n=1)
r = w.run(dry_run=True)
check("7a có PNJ Q3 + dry-run → would_fire, 0 post, 0 state", r == "would_fire" and not w.bus and not w.discord and not os.path.exists(w.state), r)
w = World(n=0)
check("7b chưa có + dry-run → not_yet", w.run(dry_run=True) == "not_yet" and not w.bus)

print("=" * 78); print("  8. bus_has_question (quét bus thật trên thư mục tạm)"); print("=" * 78)
def _bus(files):
    d = tempfile.mkdtemp(prefix="pnjbus_")
    for rel, lines in files.items():
        p = os.path.join(d, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    return d
Q = json.dumps({"agent_id": "Taylor", "event_type": "question", "topic": W.TOPIC, "payload": {}})
F = json.dumps({"agent_id": "Taylor", "event_type": "finding", "topic": "bctc-q3-m1-gate-impl-20261013",
                "payload": {"note": f"watcher bắn topic {W.TOPIC}"}})
A = json.dumps({"agent_id": "Mike", "event_type": "answer", "topic": W.TOPIC, "payload": {}})
O = json.dumps({"agent_id": "Taylor", "event_type": "question", "topic": "pnj-khac", "payload": W.TOPIC})
check("8a question đúng topic trong inbox → True", W.bus_has_question(_bus({"inbox/Taylor.jsonl": [F, Q]})) is True)
check("8b chỉ có finding NHẮC tên topic trong payload → False", W.bus_has_question(_bus({"inbox/Taylor.jsonl": [F, O]})) is False)
check("8c chỉ có answer cùng topic (không phải question) → False", W.bus_has_question(_bus({"inbox/Mike.jsonl": [A]})) is False)
check("8d question nằm ở tầng lưu trữ sâu (batches/archive) → True (§17)",
      W.bus_has_question(_bus({"inbox/Taylor.jsonl": [F], "batches/archive/2026-10/Taylor.jsonl": [Q]})) is True)
check("8e dòng hỏng chứa tên topic bị bỏ qua, không nổ", W.bus_has_question(_bus({"inbox/x.jsonl": ['{"topic": "' + W.TOPIC + '", hỏng', F]})) is False)
check("8f bus rỗng → False", W.bus_has_question(_bus({"inbox/Taylor.jsonl": []})) is False)
try:
    W.bus_has_question("/nonexistent/bus-dir"); ok = False
except Exception:
    ok = True
check("8g không có thư mục bus → raise (caller fail-closed), không trả False giả", ok)

# 8h (arch-review N1): question nằm trong tầng NÉN inbox/archive/*.jsonl.gz → True
import gzip as _gz
_d = _bus({"inbox/Taylor.jsonl": [F]})
os.makedirs(os.path.join(_d, "inbox", "archive"), exist_ok=True)
with _gz.open(os.path.join(_d, "inbox", "archive", "Taylor_2026-09.jsonl.gz"), "wt", encoding="utf-8") as _f:
    _f.write(Q + "\n")
check("8h question nằm trong .jsonl.gz lưu trữ → True (§17)", W.bus_has_question(_d) is True)

print("=" * 78); print("  8x. SQL tĩnh (arch-review R1: mutant bỏ lọc ticker từng sống 52/52)"); print("=" * 78)
_sql = W.build_sql()
check("8x-a SQL lọc đúng ticker", "t.ticker = 'PNJ'" in _sql, _sql)
check("8x-b SQL lọc đúng quý", "t.quarter = '2026Q3'" in _sql, _sql)
check("8x-c SQL loại dòng giữ chỗ (Release_Date IS NOT NULL)", "t.Release_Date IS NOT NULL" in _sql, _sql)
check("8x-d SQL loại dòng giữ chỗ (NP_P0 IS NOT NULL)", "t.NP_P0 IS NOT NULL" in _sql, _sql)
check("8x-e query_bq dùng chính build_sql() (không còn SQL nội tuyến)", "sql = build_sql()" in open(TARGET, encoding="utf-8").read())

print("=" * 78); print("  8y. ALERT cho 3 mã lỗi cần người (arch-review R2)"); print("=" * 78)
import io, contextlib
for _code in ("state_unreadable", "bus_unreadable", "bus_post_failed", "query_failed", "not_yet"):
    _o, _orig_run, _argv0 = io.StringIO(), W.run, sys.argv
    try:
        sys.argv = ["pnj_q3_review_watch.py", "--quiet"]
        W.run = lambda _c=_code, **k: _c
        with contextlib.redirect_stdout(_o):
            _rc = W.main()
    finally:
        W.run, sys.argv = _orig_run, _argv0
    _want = _code in ("state_unreadable", "bus_unreadable", "bus_post_failed")
    check(f"8y {_code}: ALERT {'CÓ' if _want else 'KHÔNG'} in, exit 0", ("ALERT pnj-q3-watch" in _o.getvalue()) == _want and _rc == 0, _o.getvalue()[:120])

print("=" * 78); print("  9. main(): WARN-only, luôn exit 0"); print("=" * 78)
_orig_run, _argv = W.run, sys.argv
try:
    sys.argv = ["pnj_q3_review_watch.py", "--quiet"]
    W.run = lambda **k: (_ for _ in ()).throw(OSError("đĩa đầy khi ghi state"))
    rc = W.main()
    check("9a run() raise (vd lỗi ghi state) → main vẫn trả 0", rc == 0, f"{rc}")
    W.run = lambda **k: "not_yet"
    check("9b not_yet → 0", W.main() == 0)
finally:
    W.run, sys.argv = _orig_run, _argv

if "--live" in sys.argv:
    print("=" * 78); print("  10. LIVE: --dry-run chạm BQ thật (chỉ đọc)"); print("=" * 78)
    st_before = os.path.exists(W.STATE_PATH)
    r = subprocess.run([sys.executable, TARGET, "--dry-run"], capture_output=True, text=True, timeout=180)
    print("   ", (r.stdout + r.stderr).strip()[:300])
    check("10a exit 0", r.returncode == 0, f"{r.returncode}")
    check("10b in ra đúng 1 trong 2 trạng thái đọc được (not_yet | DRY-RUN … sẽ post), không WARN",
          ("OK   pnj-q3-watch: not_yet" in r.stdout or "DRY-RUN pnj-q3-watch" in r.stdout
           or "OK   pnj-q3-watch: already_fired" in r.stdout) and "WARN" not in r.stdout, r.stdout[:200])
    check("10c dry-run không tạo/sửa state thật", os.path.exists(W.STATE_PATH) == st_before)
    # 10d (arch-review R1): đối chiếu ĐỘC LẬP — đếm dòng PNJ 2026Q3 thật bằng truy vấn khác, trong Python
    _r = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={W.PROJECT}", "--format=json", "--quiet",
                         f"SELECT t.ticker, t.quarter, CAST(t.Release_Date AS STRING) AS rd, t.NP_P0 AS np "
                         f"FROM `{W.PROJECT}.tav2_bq.ticker_financial` AS t WHERE t.ticker = '{W.TICKER}' AND t.quarter = '{W.QUARTER}'"],
                        capture_output=True, text=True, timeout=180)
    _rows = json.loads(_r.stdout) if _r.returncode == 0 else None
    _real = None if _rows is None else sum(1 for x in _rows if x.get("rd") and x.get("np") not in (None, ""))
    _got = W.query_bq()["n"]
    check("10d n của query_bq() == số dòng PNJ-Q3 thật (rd & NP khác NULL) đếm độc lập", _real is not None and _got == _real, f"watcher={_got} độc lập={_real}")

print("=" * 78)
print(f"  TỔNG: {PASS} PASS / {FAIL} FAIL   (target={TARGET})")
sys.exit(1 if FAIL else 0)
