#!/usr/bin/env python3
"""Work-Tree Dashboard server (Pha 1, phần B). stdlib only, 0 dependency.

Đọc state/work_tree/merged.json (do work_tree_build.py sinh), ghi qua work_ledger.py.
Env: WT_PORT (8610) · WT_BIND (mặc định: "bind" trong kb/work_tree_config.json, không có thì 0.0.0.0) ·
WT_ROOT · WT_STATE_DIR · WT_LEDGER · WT_SECRETS_DIR · WT_BUILD_ROOT · WT_BUS_ROOT (các WT_* trừ PORT/BIND
chỉ để test/selfcheck cô lập). Import work_ledger/work_tree_build lỗi ⇒ server chết lúc khởi động (cố ý).
Auth: token ở secrets/work_tree_token; GET /?k=<token> đặt cookie rồi redirect.
"""
import hmac, json, os, re, secrets as _secrets, sys, threading, time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(os.environ.get("WT_ROOT") or Path(__file__).resolve().parent.parent).resolve()
WC_ROOT = Path(os.environ.get("WT_WC_ROOT") or (ROOT.parent if ROOT.name == "mike" else ROOT.parent / "WorkingClaude")).resolve()
STATE_DIR = Path(os.environ.get("WT_STATE_DIR") or ROOT / "state" / "work_tree")
MERGED = STATE_DIR / "merged.json"
LEDGER = Path(os.environ.get("WT_LEDGER") or ROOT / "kb" / "work_ledger.jsonl")
SECRETS_DIR = Path(os.environ.get("WT_SECRETS_DIR") or ROOT / "secrets")
WEB = ROOT / "webui_work_tree"
STATUSES = {"idea", "active", "waiting", "GO", "NO-GO", "live", "closed"}
VERDICTS = {"NO-GO", "GO", "INCONCLUSIVE", "IMPLEMENTED", "KHÔNG WIRE"}
FILE_EXT = {".md", ".json", ".csv", ".html"}
FILE_DIRS = ("kb/projects/", "kb/paper_programs_charter/")
FILE_DENY = re.compile(r"token|cred|secret|otp|passw", re.I)
STATUS_BLOCKED = ("busq:", "paper:")  # nguồn derived: chỉ note/priority, không đóng từ web
MAX_BODY, MAX_FILE, RATE_MAX, RATE_WIN = 64 * 1024, 2 * 1024 * 1024, 30, 60
STATIC = {"/": ("index.html", "text/html; charset=utf-8"),
          "/app.js": ("app.js", "application/javascript; charset=utf-8"),
          "/style.css": ("style.css", "text/css; charset=utf-8")}

_write_lock = threading.Lock()
_rate = defaultdict(deque)
_rate_lock = threading.Lock()

if str(ROOT / "bin") not in sys.path:
    sys.path.insert(0, str(ROOT / "bin"))
import work_ledger as WL  # noqa: E402  (lỗi import ⇒ chết lúc khởi động, không im lặng)
import work_tree_build as WB  # noqa: E402


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


def _rebuild():
    WB.write_merged(WB.Cfg(root=os.environ.get("WT_BUILD_ROOT") or str(ROOT), ledger=str(LEDGER), out=str(MERGED),
                           bus_root=os.environ.get("WT_BUS_ROOT")))


def op_note(id_, text):
    return WL.add_note(id_, text, by="user")


def op_priority(id_, p):
    return WL.set_priority(id_, p, by="user")


def op_status(id_, status, verdict):
    if status in ("idea", "active", "waiting"):  # mở lại ⇒ xoá kết luận cũ
        return WL.upsert(id_, by="user", status=status, verdict=None)
    return WL.set_status(id_, status, (verdict or {}).get("label"), (verdict or {}).get("text", ""), by="user")


def op_new(branch, title, summary):
    return WL.new_user_item(branch, title, summary, by="user")["id"]


def find_item(id_):
    for i in read_merged().get("items", []):
        if i.get("id") == id_:
            return i
    return None


def history(id_):
    """Lịch sử dựng từ bản ghi ledger của item (mới nhất trước): thời điểm, ai, trường đổi."""
    skip = {"id", "ts", "by", "updated"}
    out = []
    for r in WL.read_records(str(LEDGER)):
        if r.get("id") != id_:
            continue
        if r.get("merged_into"):
            txt = "gộp vào " + str(r["merged_into"])
        else:
            ch = ["ghi chú" if k == "notes" else k for k in r if k not in skip]
            txt = "%s đổi: %s" % (r.get("by", "?"), ", ".join(ch) or "—")
        out.append({"ts": r.get("ts") or "", "text": txt[:200]})
    return out[::-1][:30]


# ---------------------------------------------------------------- file allowlist
def resolve_file(p):
    """Chỉ serve path KHỚP CHÍNH XÁC một links[].path trong merged.json (sau normpath), trong FILE_DIRS,
    không symlink (realpath == path chưa resolve), tên không chứa token|cred|secret|otp|passw."""
    if not p or "\0" in p or len(p) > 400 or p.startswith("/"):
        return None
    rel = os.path.normpath(p)
    if rel.startswith("..") or not rel.startswith(FILE_DIRS) or FILE_DENY.search(rel):
        return None
    allowed = {os.path.normpath(l.get("path") or "") for it in read_merged().get("items", [])
               for l in it.get("links") or [] if isinstance(l, dict)}
    if rel not in allowed or Path(rel).suffix.lower() not in FILE_EXT:
        return None
    for base in (ROOT, WC_ROOT):
        cand = os.path.join(str(base), rel)
        if os.path.realpath(cand) != cand:  # symlink ở bất kỳ cấp nào ⇒ từ chối
            continue
        f = Path(cand)
        if f.is_file() and f.stat().st_size <= MAX_FILE:
            return f
    return None


# ---------------------------------------------------------------- handler
class H(BaseHTTPRequestHandler):
    server_version = "wt/1"
    protocol_version = "HTTP/1.0"
    timeout = 15

    def log_message(self, fmt, *a):
        msg = re.sub(r"\?[^\s\"]*", "?***", fmt % a)  # che query (?k=token) khỏi access log
        sys.stderr.write("%s %s\n" % (self.address_string(), msg))

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
        self.send_header("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'")
        self.send_header("X-Frame-Options", "DENY")
        for k, v in extra:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _authed(self):
        ck = self.headers.get("Cookie", "")
        for part in ck.split(";"):
            k, _, v = part.strip().partition("=")
            if k == "wt" and hmac.compare_digest(v.encode(), self.server.token.encode()):
                return True
        return False

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        k = (q.get("k") or [""])[0]
        if k and u.path == "/":
            if hmac.compare_digest(k.encode(), self.server.token.encode()):
                return self._send(302, b"", extra=[("Location", "/"), (
                    "Set-Cookie", "wt=%s; HttpOnly; SameSite=Strict; Path=/; Max-Age=31536000%s" % (
                        self.server.token,
                        "; Secure" if self.headers.get("X-Forwarded-Proto") == "https" else ""))])
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
        if ip in ("127.0.0.1", "::1"):  # sau tunnel cloudflared: IP thật nằm ở CF-Connecting-IP
            ip = (self.headers.get("CF-Connecting-IP") or ip)[:64]
        with _rate_lock:
            if len(_rate) > 64:  # dọn IP đã im quá cửa sổ
                for key in [x for x, q in _rate.items() if not q or t - q[-1] > RATE_WIN]:
                    del _rate[key]
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
                        if new_id.startswith(STATUS_BLOCKED):
                            return self._send(400, {"error": "Mục này lấy từ nguồn tự động (câu hỏi bus / paper program) "
                                                             "nên không đóng được từ web — chỉ ghi chú hoặc đổi ưu tiên."})
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
    bind = os.environ.get("WT_BIND")
    if not bind:
        try:
            bind = json.loads((ROOT / "kb" / "work_tree_config.json").read_text(encoding="utf-8")).get("bind")
        except Exception:
            bind = None
    bind = bind or "0.0.0.0"
    srv = make_server(port, bind)
    sys.stderr.write("work-tree dashboard %s:%d (root=%s)\n" % (bind, port, ROOT))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
