#!/usr/bin/env python3
"""Selfcheck work_tree_server: cổng ngẫu nhiên, state cô lập trong tmp (không đụng state/, kb/, secrets/ thật)."""
import hashlib, io, json, os, re, shutil, subprocess, sys, tempfile, threading, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "bin"))


def snap(p):
    p = Path(p)
    return (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest()) if p.exists() else None


REPO_GUARD = [HERE / "state/work_tree/merged.json", HERE / "kb/work_ledger.jsonl"]
before_repo = [snap(p) for p in REPO_GUARD]

tmp = Path(tempfile.mkdtemp(prefix="wt_selfcheck_"))
(tmp / "state").mkdir()
(tmp / "root/kb").mkdir(parents=True)   # WT_BUILD_ROOT: kb rỗng ⇒ không derived từ repo thật
(tmp / "bus").mkdir()                   # WT_BUS_ROOT rỗng
fr = tmp / "fileroot"                   # gốc giả cho /file (vá S.ROOT bên dưới)
(fr / "kb/projects").mkdir(parents=True)
(fr / "data").mkdir()
(fr / "kb/projects/ok.md").write_text("# ok\n")
(fr / "kb/projects/my_token_notes.md").write_text("x")
(fr / "kb/projects/not_in_links.md").write_text("x")
(fr / "data/dnse_trading_token.json").write_text('{"t":"SECRET"}')
os.symlink(fr / "data/dnse_trading_token.json", fr / "kb/projects/link.md")
os.environ.update(WT_STATE_DIR=str(tmp / "state"), WT_LEDGER=str(tmp / "ledger.jsonl"), WT_SECRETS_DIR=str(tmp / "secrets"),
                  WT_BUILD_ROOT=str(tmp / "root"), WT_BUS_ROOT=str(tmp / "bus"))
import work_ledger as WL  # noqa: E402

# fixture → bản ghi ledger (4 item) ; merged.json ban đầu = fixture
fx = json.loads((HERE / "tests/fixtures/work_tree_merged.json").read_text())
for it in fx["items"]:
    rec = {k: it[k] for k in WL.FIELDS if k in it}
    rec.update(id=it["id"], ts="2026-11-01T00:00:00+07:00", by="fixture", notes=it.get("notes") or [])
    WL.append_record(rec, str(tmp / "ledger.jsonl"))
WL.upsert("proj:files-check", by="fixture", path=str(tmp / "ledger.jsonl"), branch="Research/DD cổ phiếu", title="files",
          links=[{"label": "ok", "path": "kb/projects/ok.md"}, {"label": "sym", "path": "kb/projects/link.md"},
                 {"label": "tok", "path": "kb/projects/my_token_notes.md"},
                 {"label": "out", "path": "data/dnse_trading_token.json"}])
WL.upsert("proj:nav-check", by="fixture", path=str(tmp / "ledger.jsonl"), branch="Research/Tín hiệu & chiến lược", title="Kiểm tra NAV 500 cp")
WL.upsert("busq:wags/test-topic", by="fixture", path=str(tmp / "ledger.jsonl"), branch="Operation/Sự cố & retro", title="busq test")
shutil.copy(HERE / "tests/fixtures/work_tree_merged.json", tmp / "state/merged.json")
N_FX = len(fx["items"])
import work_tree_server as S  # noqa: E402

srv = S.make_server(0, "127.0.0.1")
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
tok = srv.token
B = "http://127.0.0.1:%d" % port
fails = []


class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


op = urllib.request.build_opener(NoRedir)


def req(path, method="GET", body=None, cookie=True, hdr=True):
    h = {}
    if cookie:
        h["Cookie"] = "wt=" + tok
    if hdr and method == "POST":
        h["X-WT"] = "1"
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(B + path, data=json.dumps(body).encode() if body is not None else None, headers=h, method=method)
    try:
        with op.open(r, timeout=5) as x:
            return x.status, x.read(), dict(x.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def check(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name + (" — " + str(info) if info and not ok else ""))
    if not ok:
        fails.append(name)


check("401 không token (/)", req("/", cookie=False)[0] == 401)
check("401 không token (/api/tree)", req("/api/tree", cookie=False)[0] == 401)
c, _, h = req("/?k=" + tok, cookie=False)
check("?k=token → 302 + cookie HttpOnly", c == 302 and "HttpOnly" in h.get("Set-Cookie", ""), (c, h))
check("?k sai → 401", req("/?k=sai", cookie=False)[0] == 401)
c, b, _ = req("/api/tree")
check("200 /api/tree có token", c == 200 and len(json.loads(b)["items"]) == N_FX)
check("200 index.html", req("/")[0] == 200)
c, b, _ = req("/api/item?id=proj:fpt-dd")
check("/api/item 200 + history[]", c == 200 and "history" in json.loads(b))
check("/api/item id lạ → 404", req("/api/item?id=zzz")[0] == 404)
check("POST thiếu X-WT → 403", req("/api/note", "POST", {"id": "proj:fpt-dd", "text": "x"}, hdr=False)[0] == 403)
check("POST không cookie → 401", req("/api/note", "POST", {"id": "proj:fpt-dd", "text": "x"}, cookie=False)[0] == 401)
c, b, _ = req("/api/note", "POST", {"id": "proj:fpt-dd", "text": "ghi chú thử"})
it = json.loads(b) if c == 200 else {}
check("POST note → 200, hiện trong item", c == 200 and any(n["text"] == "ghi chú thử" for n in it.get("notes", [])), (c, b[:200]))
check("note vào ledger", "ghi chú thử" in (tmp / "ledger.jsonl").read_text())
check("note vào merged.json", "ghi chú thử" in (tmp / "state/merged.json").read_text())
c, b, _ = req("/api/priority", "POST", {"id": "proj:fpt-dd", "priority": 2})
check("POST priority → 200 & =2", c == 200 and json.loads(b)["priority"] == 2)
check("priority=9 → 400", req("/api/priority", "POST", {"id": "proj:fpt-dd", "priority": 9})[0] == 400)
c, b, _ = req("/api/status", "POST", {"id": "proj:fpt-dd", "status": "NO-GO", "verdict": {"label": "NO-GO", "text": "x"}})
check("POST status NO-GO → 200", c == 200 and json.loads(b)["status"] == "NO-GO" and json.loads(b)["verdict"]["label"] == "NO-GO", (c, b[:200]))
c, b, _ = req("/api/status", "POST", {"id": "proj:fpt-dd", "status": "active"})
check("mở lại (active) → xoá verdict", c == 200 and json.loads(b)["status"] == "active" and json.loads(b)["verdict"] is None, (c, b[:200]))
check("status rác → 400", req("/api/status", "POST", {"id": "proj:fpt-dd", "status": "bậy"})[0] == 400)
for bid in ("paper:p1", "busq:wags/test-topic"):
    c, b, _ = req("/api/status", "POST", {"id": bid, "status": "closed"})
    check("status %s bị chặn 400 + thông báo tiếng Việt" % bid, c == 400 and "không đóng được" in json.loads(b)["error"], (c, b[:200]))
    check("note/priority %s vẫn được" % bid, req("/api/note", "POST", {"id": bid, "text": "n"})[0] == 200
          and req("/api/priority", "POST", {"id": bid, "priority": 1})[0] == 200)
c, b, _ = req("/api/new", "POST", {"branch": "Research/Dữ liệu & PIT", "title": "Hướng mới", "summary": "tóm tắt"})
nid = json.loads(b).get("id", "") if c == 200 else ""
n = json.loads(b) if c == 200 else {}
check("POST new → user:<slug>, idea, source=user, ack=false",
      nid.startswith("user:") and n.get("status") == "idea" and n.get("source") == "user" and n.get("ack") is False, (c, b[:200]))
check("new xuất hiện ở khối inbox", nid in json.loads(req("/api/tree")[1])["attention"]["inbox"])
check("body quá lớn → 413", req("/api/note", "POST", {"id": "proj:fpt-dd", "text": "x" * 70000})[0] == 413)
# /file — allowlist theo links[] + thư mục + symlink + denylist (vá S.ROOT sang gốc giả)
S.ROOT, S.WC_ROOT = fr.resolve(), (tmp / "nowhere")
c, b, _ = req("/file?p=kb/projects/ok.md")
check("/file path hợp lệ trong links → 200", c == 200 and b.startswith(b"# ok"), c)
check("/file data/dnse_trading_token.json (có trong links nhưng ngoài thư mục) → 403", req("/file?p=data/dnse_trading_token.json")[0] == 403)
check("/file symlink trong base trỏ file nhạy cảm → 403", req("/file?p=kb/projects/link.md")[0] == 403)
check("/file tên chứa 'token' → 403", req("/file?p=kb/projects/my_token_notes.md")[0] == 403)
check("/file không nằm trong links → 403", req("/file?p=kb/projects/not_in_links.md")[0] == 403)
check("/file normpath khớp links ('kb/projects/./ok.md') → 200", req("/file?p=kb/projects/./ok.md")[0] == 200)
for p in ("../secrets/x", "secrets/work_tree_token", "../../etc/passwd", "/etc/passwd", "kb/../secrets/work_tree_token",
          "bin/work_tree_server.py", ".git/config", "%2e%2e/secrets/x", "kb/projects/../../secrets/a.md"):
    check("/file chặn %r" % p, req("/file?p=" + p)[0] in (403, 404) and req("/file?p=" + p)[0] != 200)
S.ROOT, S.WC_ROOT = HERE.resolve(), HERE.resolve().parent
# id chứa 'nav' đi vòng POST note → build → đúng item gốc, không id trùng/mồ côi
c, b, _ = req("/api/note", "POST", {"id": "proj:nav-check", "text": "ghi chú kiểm tra"})
tree = json.loads(req("/api/tree")[1])
ids = [i["id"] for i in tree["items"]]
nav = next((i for i in tree["items"] if i["id"] == "proj:nav-check"), {})
check("id 'nav' giữ nguyên + note đúng item gốc", c == 200 and any(n["text"] == "ghi chú kiểm tra" for n in nav.get("notes", [])), (c, ids))
check("không id trùng / mồ côi (attention ⊂ items)", len(ids) == len(set(ids)) and not [x for v in tree["attention"].values() for x in v if x not in ids]
      and not [x for x in ids if "[" in x], ids)
check("trường hiển thị bị che (NAV, 500 cp), id không", "NAV" not in nav.get("title", "") and "500" not in nav.get("title", ""), nav.get("title"))
c, b, _ = req("/api/new", "POST", {"branch": "Research", "title": "NAV audit", "summary": "s"})
nid2 = json.loads(b).get("id", "")
c2, b2, _ = req("/api/note", "POST", {"id": nid2, "text": "n2"})
check("POST new 'NAV audit' → id user:nav-audit & note đúng item", nid2 == "user:nav-audit" and c2 == 200 and json.loads(b2)["notes"], (nid2, c2))
h = json.loads(req("/api/item?id=proj:nav-check")[1]).get("history", [])
check("history dựng từ ledger (có ts + trường đổi)", bool(h) and all(x["ts"] and x["text"] for x in h) and any("ghi chú" in x["text"] for x in h), h)
# new_user_item đồng thời → id duy nhất
res = []
ts_ = [threading.Thread(target=lambda: res.append(WL.new_user_item("Research", "Song song", path=str(tmp / "ledger.jsonl"))["id"])) for _ in range(8)]
[t.start() for t in ts_]; [t.join() for t in ts_]
check("new_user_item song song: 8 id duy nhất", len(set(res)) == 8, res)
# header / log / non-ASCII
_, _, hh = req("/api/tree")
check("CSP + X-Frame-Options", "frame-ancestors 'none'" in hh.get("Content-Security-Policy", "") and hh.get("X-Frame-Options") == "DENY", hh)
old_err, sys.stderr = sys.stderr, io.StringIO()
req("/?k=" + tok, cookie=False); req("/?k=sai-" + tok, cookie=False)
logged, sys.stderr = sys.stderr.getvalue(), old_err
check("access log che query (không lộ token)", tok not in logged and "?***" in logged, logged)
check("?k non-ASCII → 401 không crash", req("/?k=%C3%A9", cookie=False)[0] == 401)
rq = urllib.request.Request(B + "/api/tree", headers={"Cookie": "wt=\xe9"})
try:
    code = op.open(rq, timeout=5).status
except urllib.error.HTTPError as e:
    code = e.code
check("cookie non-ASCII → 401 không crash", code == 401, code)
check("H.timeout = 15", S.H.timeout == 15)
# import lỗi ⇒ server chết lúc khởi động
solo = tmp / "solo"; (solo / "bin").mkdir(parents=True); shutil.copy(HERE / "bin/work_tree_server.py", solo / "bin/")
r = subprocess.run([sys.executable, str(solo / "bin/work_tree_server.py")], capture_output=True, text=True, timeout=20,
                   env=dict(os.environ, WT_ROOT=str(solo), WT_PORT="0"))
check("thiếu work_ledger/work_tree_build ⇒ chết lúc khởi động (rc≠0)", r.returncode != 0 and "ModuleNotFoundError" in r.stderr, (r.returncode, r.stderr[-200:]))
# secret grep
SECRET = re.compile(r"0002023347|0002023348|0001743768|availableCash|\bNAV\b|\bCAGR\b")
blob = b"".join(req(p)[1] for p in ("/", "/app.js", "/style.css", "/api/tree")).decode()
check("secret-grep HTML/JS/CSS/tree sạch", not SECRET.search(blob), SECRET.findall(blob))
check("token file 0600", oct((tmp / "secrets/work_tree_token").stat().st_mode & 0o777) == "0o600")
# rate-limit (cuối cùng)
S._rate.clear()
codes = [req("/api/note", "POST", {"id": "proj:fpt-dd", "text": "r%d" % i})[0] for i in range(33)]
check("rate-limit: 30 đầu 200, sau đó 429", codes[:30].count(200) == 30 and 429 in codes[30:], codes)
srv.shutdown()
after_repo = [snap(p) for p in REPO_GUARD]
check("merged.json + work_ledger.jsonl của repo KHÔNG đổi (mtime+nội dung)", before_repo == after_repo, (before_repo, after_repo))
shutil.rmtree(tmp, ignore_errors=True)
print("RESULT: " + ("FAIL %s" % fails if fails else "PASS"))
sys.exit(1 if fails else 0)
