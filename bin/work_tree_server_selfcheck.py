#!/usr/bin/env python3
"""Selfcheck work_tree_server: cổng ngẫu nhiên, state cô lập trong tmp (không đụng state/, kb/, secrets/ thật)."""
import json, os, re, shutil, sys, tempfile, threading, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
tmp = Path(tempfile.mkdtemp(prefix="wt_selfcheck_"))
(tmp / "state").mkdir()
shutil.copy(HERE / "tests/fixtures/work_tree_merged.json", tmp / "state/merged.json")
os.environ.update(WT_STATE_DIR=str(tmp / "state"), WT_LEDGER=str(tmp / "ledger.jsonl"), WT_SECRETS_DIR=str(tmp / "secrets"))
sys.path.insert(0, str(HERE / "bin"))
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
check("200 /api/tree có token", c == 200 and len(json.loads(b)["items"]) == 4)
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
c, b, _ = req("/api/status", "POST", {"id": "paper:p1", "status": "NO-GO", "verdict": {"label": "NO-GO", "text": "x"}})
check("POST status NO-GO → 200", c == 200 and json.loads(b)["status"] == "NO-GO")
check("status rác → 400", req("/api/status", "POST", {"id": "paper:p1", "status": "bậy"})[0] == 400)
c, b, _ = req("/api/new", "POST", {"branch": "Research/Dữ liệu & PIT", "title": "Hướng mới", "summary": "tóm tắt"})
nid = json.loads(b).get("id", "") if c == 200 else ""
n = json.loads(b) if c == 200 else {}
check("POST new → user:<slug>, idea, source=user, ack=false",
      nid.startswith("user:") and n.get("status") == "idea" and n.get("source") == "user" and n.get("ack") is False, (c, b[:200]))
check("new xuất hiện ở khối inbox", nid in json.loads(req("/api/tree")[1])["attention"]["inbox"])
check("body quá lớn → 413", req("/api/note", "POST", {"id": "proj:fpt-dd", "text": "x" * 70000})[0] == 413)
# /file
check("/file whitelist .md trong ROOT → 200", req("/file?p=kb/projects/work-tree-dashboard-spec-20261101.md")[0] == 200)
for p in ("../secrets/x", "secrets/work_tree_token", "../../etc/passwd", "/etc/passwd", "kb/../secrets/work_tree_token",
          "bin/work_tree_server.py", ".git/config", "%2e%2e/secrets/x", "kb/projects/../../secrets/a.md"):
    check("/file chặn %r" % p, req("/file?p=" + p)[0] in (403, 404) and req("/file?p=" + p)[0] != 200)
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
shutil.rmtree(tmp, ignore_errors=True)
print("RESULT: " + ("FAIL %s" % fails if fails else "PASS"))
sys.exit(1 if fails else 0)
