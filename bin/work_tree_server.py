#!/usr/bin/env python3
"""Work-Tree Dashboard server (Pha 1, phần B). stdlib only, 0 dependency.

Đọc state/work_tree/merged.json (do work_tree_build.py sinh), ghi qua work_ledger.py.
Env: WT_PORT (8610) · WT_BIND (0.0.0.0) · WT_ROOT · WT_STATE_DIR · WT_LEDGER · WT_SECRETS_DIR
(các WT_* trừ PORT/BIND chỉ để test/selfcheck cô lập).
Auth: token ở secrets/work_tree_token; GET /?k=<token> đặt cookie rồi redirect.
"""
import hmac, json, os, re, secrets as _secrets, subprocess, sys, threading, time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(os.environ.get("WT_ROOT") or Path(__file__).resolve().parent.parent).resolve()
WC_ROOT = Path(os.environ.get("WT_WC_ROOT") or ROOT.parent / "WorkingClaude").resolve()
STATE_DIR = Path(os.environ.get("WT_STATE_DIR") or ROOT / "state" / "work_tree")
MERGED = STATE_DIR / "merged.json"
LEDGER = Path(os.environ.get("WT_LEDGER") or ROOT / "kb" / "work_ledger.jsonl")
SECRETS_DIR = Path(os.environ.get("WT_SECRETS_DIR") or ROOT / "secrets")
WEB = ROOT / "webui_work_tree"
STATUSES = {"idea", "active", "waiting", "GO", "NO-GO", "live", "closed"}
VERDICTS = {"NO-GO", "GO", "INCONCLUSIVE", "IMPLEMENTED", "KHÔNG WIRE"}
FILE_EXT = {".md", ".json", ".csv", ".html"}
MAX_BODY, MAX_FILE, RATE_MAX, RATE_WIN = 64 * 1024, 2 * 1024 * 1024, 30, 60
STATIC = {"/": ("index.html", "text/html; charset=utf-8"),
          "/app.js": ("app.js", "application/javascript; charset=utf-8"),
          "/style.css": ("style.css", "text/css; charset=utf-8")}

_write_lock = threading.Lock()
_rate = defaultdict(deque)
_rate_lock = threading.Lock()

if str(ROOT / "bin") not in sys.path:
    sys.path.insert(0, str(ROOT / "bin"))
try:
    import work_ledger as WL  # Phần A (job khác); thiếu thì dùng adapter
except Exception:
    WL = None
try:
    import work_tree_build as WB
except Exception:
    WB = None


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_token():
    f = SECRETS_DIR / "work_tree_token"
    if f.exists():
        t = f.read_text().strip()
        if t:
            return t
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    t = _secrets.token_urlsafe(24)
    fd = os.open(f, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(t + "\n")
    os.chmod(f, 0o600)
    return t


# ---------------------------------------------------------------- data / adapter
def read_merged():
    try:
        return json.loads(MERGED.read_text(encoding="utf-8"))
    except Exception:
        return {"generated_at": None, "counts": {}, "attention": {"need_user": [], "overdue": [],
                "recent": [], "ideas": [], "inbox": []}, "items": [], "branches": []}


def _ledger_append(rec):
    import fcntl
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        fh.flush(); os.fsync(fh.fileno())


def _fallback_rebuild():
    """Adapter tối thiểu khi chưa có work_tree_build: gấp ledger lên merged.json cũ."""
    m = read_merged()
    items = {i["id"]: i for i in m.get("items", [])}
    if LEDGER.exists():
        for ln in LEDGER.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(ln)
            except Exception:
                continue
            cur = items.setdefault(r["id"], {"id": r["id"], "notes": [], "priority": 3,
                                             "status": "idea", "needs_user": False})
            for k, v in r.items():
                if k in ("ts", "by"):
                    continue
                if k == "notes":
                    for n in v:
                        if n not in cur["notes"]:
                            cur["notes"].append(n)
                else:
                    cur[k] = v
    today = datetime.now().date().isoformat()
    week = (datetime.now() - timedelta(days=7)).date().isoformat()
    L = list(items.values())
    ids = lambda f: [i["id"] for i in L if f(i)]
    m["items"] = L
    m["attention"] = {
        "need_user": ids(lambda i: i.get("needs_user") and i.get("status") != "closed"),
        "overdue": ids(lambda i: i.get("stale") or (i.get("due") and i["due"] < today and i.get("status") != "closed")),
        "recent": ids(lambda i: (i.get("updated") or "")[:10] >= week),
        "ideas": ids(lambda i: i.get("status") == "idea"),
        "inbox": ids(lambda i: i.get("source") == "user" and not i.get("ack")),
    }
    m["branches"] = sorted({i["branch"] for i in L if i.get("branch")})
    m["generated_at"] = now_iso()
    m["counts"] = {k: len(v) for k, v in m["attention"].items()}
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = MERGED.with_suffix(".tmp")
    tmp.write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, MERGED)


def _rebuild():
    if WB is not None:
        for name in ("build_and_write", "build_merged", "build"):
            fn = getattr(WB, name, None)
            if callable(fn):
                try:
                    fn()
                    return
                except TypeError:
                    continue
    _fallback_rebuild()


def op_note(id_, text):
    if WL is not None:
        return WL.add_note(id_, text, by="user")
    _ledger_append({"id": id_, "updated": now_iso(), "notes": [{"ts": now_iso(), "by": "user", "text": text}]})


def op_priority(id_, p):
    if WL is not None:
        return WL.set_priority(id_, p, by="user")
    _ledger_append({"id": id_, "priority": p, "updated": now_iso()})


def op_status(id_, status, verdict):
    if WL is not None:
        return WL.set_status(id_, status, (verdict or {}).get("label"), (verdict or {}).get("text", ""), by="user")
    rec = {"id": id_, "status": status, "updated": now_iso()}
    if verdict:
        rec["verdict"] = verdict
    _ledger_append(rec)


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower().encode("ascii", "ignore").decode()).strip("-")
    return s[:40] or "y-tuong"


def op_new(branch, title, summary):
    if WL is not None:
        return WL.new_user_item(branch, title, summary, by="user")["id"]
    id_ = "user:%s-%s" % (slugify(title), datetime.now().strftime("%m%d%H%M%S"))
    _ledger_append({"id": id_, "branch": branch, "title": title, "summary": summary, "status": "idea",
                    "priority": 3, "type": "research", "source": "user", "ack": False,
                    "owner": "user", "opened": now_iso()[:10], "updated": now_iso(), "needs_user": False,
                    "notes": []})
    return id_


def find_item(id_):
    for i in read_merged().get("items", []):
        if i.get("id") == id_:
            return i
    return None


def history(id_):
    out = []
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "log", "-n", "30", "--format=%cI|%s", "-S" + id_,
                            "--", "kb/work_ledger.jsonl"], capture_output=True, text=True, timeout=5)
        for ln in r.stdout.splitlines():
            ts, _, s = ln.partition("|")
            out.append({"ts": ts, "text": s[:200]})
    except Exception:
        pass
    return out


# ---------------------------------------------------------------- file whitelist
def resolve_file(p):
    if not p or "\0" in p or len(p) > 400:
        return None
    rel = Path(p)
    if rel.is_absolute() or ".." in rel.parts:
        return None
    for base in (ROOT, WC_ROOT):
        try:
            f = (base / rel).resolve()
            f.relative_to(base)
        except Exception:
            continue
        parts = f.relative_to(base).parts
        if "secrets" in parts or any(x.startswith(".") for x in parts):
            return None
        if f.suffix.lower() in FILE_EXT and f.is_file() and f.stat().st_size <= MAX_FILE:
            return f
    return None


# ---------------------------------------------------------------- handler
class H(BaseHTTPRequestHandler):
    server_version = "wt/1"
    protocol_version = "HTTP/1.0"

    def log_message(self, fmt, *a):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % a))

    def _send(self, code, body=b"", ctype="application/json; charset=utf-8", extra=()):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        for k, v in extra:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _authed(self):
        ck = self.headers.get("Cookie", "")
        for part in ck.split(";"):
            k, _, v = part.strip().partition("=")
            if k == "wt" and hmac.compare_digest(v, self.server.token):
                return True
        return False

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        k = (q.get("k") or [""])[0]
        if k and u.path == "/":
            if hmac.compare_digest(k, self.server.token):
                return self._send(302, b"", extra=[("Location", "/"), (
                    "Set-Cookie", "wt=%s; HttpOnly; SameSite=Strict; Path=/; Max-Age=31536000" % self.server.token)])
            return self._send(401, {"error": "unauthorized"})
        if not self._authed():
            return self._send(401, {"error": "unauthorized"})
        if u.path in STATIC:
            name, ct = STATIC[u.path]
            try:
                return self._send(200, (WEB / name).read_bytes(), ct)
            except OSError:
                return self._send(404, {"error": "missing asset"})
        if u.path == "/api/tree":
            return self._send(200, read_merged())
        if u.path == "/api/item":
            it = find_item((q.get("id") or [""])[0])
            if not it:
                return self._send(404, {"error": "not found"})
            return self._send(200, dict(it, history=history(it["id"])))
        if u.path == "/file":
            f = resolve_file((q.get("p") or [""])[0])
            if not f:
                return self._send(403, {"error": "forbidden"})
            return self._send(200, f.read_bytes(), "text/plain; charset=utf-8")
        return self._send(404, {"error": "not found"})

    def _rate_ok(self):
        ip, t = self.client_address[0], time.time()
        with _rate_lock:
            d = _rate[ip]
            while d and t - d[0] > RATE_WIN:
                d.popleft()
            if len(d) >= RATE_MAX:
                return False
            d.append(t)
            return True

    def do_POST(self):
        u = urlparse(self.path)
        if not self._authed():
            return self._send(401, {"error": "unauthorized"})
        if self.headers.get("X-WT") != "1":
            return self._send(403, {"error": "missing X-WT"})
        if not self._rate_ok():
            return self._send(429, {"error": "rate limit"})
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            n = -1
        if n < 0 or n > MAX_BODY:
            return self._send(413, {"error": "body too large"})
        try:
            d = json.loads(self.rfile.read(n) or b"{}")
            assert isinstance(d, dict)
        except Exception:
            return self._send(400, {"error": "bad json"})
        s = lambda k, m: str(d.get(k, "")).strip()[:m]
        try:
            with _write_lock:
                if u.path == "/api/new":
                    b, t, sm = s("branch", 80), s("title", 200), s("summary", 160)
                    if not b or not t:
                        return self._send(400, {"error": "branch+title bắt buộc"})
                    new_id = op_new(b, t, sm)
                else:
                    new_id = s("id", 200)
                    if not find_item(new_id):
                        return self._send(404, {"error": "id không tồn tại"})
                    if u.path == "/api/note":
                        t = s("text", 2000)
                        if not t:
                            return self._send(400, {"error": "text rỗng"})
                        op_note(new_id, t)
                    elif u.path == "/api/priority":
                        p = d.get("priority")
                        if p not in (1, 2, 3):
                            return self._send(400, {"error": "priority ∈ 1|2|3"})
                        op_priority(new_id, p)
                    elif u.path == "/api/status":
                        st, v = s("status", 20), d.get("verdict")
                        if st not in STATUSES:
                            return self._send(400, {"error": "status không hợp lệ"})
                        if v is not None:
                            if not isinstance(v, dict) or v.get("label") not in VERDICTS:
                                return self._send(400, {"error": "verdict.label không hợp lệ"})
                            v = {"label": v["label"], "text": str(v.get("text", ""))[:500]}
                        op_status(new_id, st, v)
                    else:
                        return self._send(404, {"error": "not found"})
                _rebuild()
        except ValueError as e:
            return self._send(400, {"error": str(e)[:200]})
        except Exception as e:
            sys.stderr.write("POST error: %r\n" % e)
            return self._send(500, {"error": "server error"})
        return self._send(200, find_item(new_id) or {"id": new_id})


def make_server(port, bind="0.0.0.0"):
    srv = ThreadingHTTPServer((bind, port), H)
    srv.daemon_threads = True
    srv.token = load_token()
    return srv


def main():
    port = int(os.environ.get("WT_PORT", "8610"))
    srv = make_server(port, os.environ.get("WT_BIND", "0.0.0.0"))
    sys.stderr.write("work-tree dashboard :%d (root=%s, ledger-adapter=%s)\n" % (
        port, ROOT, "work_ledger" if WL else "fallback"))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
