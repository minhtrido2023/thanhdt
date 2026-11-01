#!/usr/bin/env python3
"""work_tree_build.py — gộp sổ cái + nguồn derived → state/work_tree/merged.json (hợp đồng: kb/projects/work-tree-dashboard-spec-20261101.md).

Nguồn derived (chỉ ĐỌC, không ghi ngược): kb/paper_programs_registry.json, kb/dashboard_watchlist.json,
kb/structural_break_watch.json, bus question chưa đóng (bin/bus_question_audit.py --json), parser
kb/projects/INDEX.md (+ quét kb/projects/*.md chưa có trong INDEX), bus/jobs 30 ngày.
Ledger (kb/work_ledger.jsonl) thắng derived theo từng trường. Mọi ngày giờ neo ICT (§16).
`attention.*` = danh sách ID (tra trong `items`). Không hiện số tài khoản/NAV/CAGR: sanitize() che.

Chạy: python3 bin/work_tree_build.py [--out PATH] [--quiet]
Import: build(Cfg()) -> dict ; write_merged(Cfg()) -> dict
"""
import argparse
import difflib
import glob
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import work_ledger as wl  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
HERE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON_MIKE = "/home/trido/thanhdt/WorkingClaude/mike"
OPEN = ("idea", "active", "waiting")
ROOT_ORDER = ("Research", "Operation", "Portfolio", "Watch")
SKELETON = [
    "Research/Tín hiệu & chiến lược", "Research/Thực thi", "Research/Dữ liệu & PIT",
    "Research/Paper programs", "Research/DD cổ phiếu",
    "Operation/Báo cáo & cadence", "Operation/Cron-hạ tầng-KB", "Operation/Corp-action",
    "Operation/Sự cố & retro",
    "Portfolio/Tài khoản live", "Portfolio/Rủi ro & gate", "Portfolio/Sleeve discretionary",
    "Portfolio/Hiệu suất",
    "Watch/Vĩ mô & cấu trúc", "Watch/Mốc định kỳ",
]
ROOT_TYPE = {"Research": "research", "Operation": "ops", "Portfolio": "portfolio", "Watch": "watch"}
SENSITIVE = [(re.compile(r"\b000\d{7}\b"), "[tk]"),
             (re.compile(r"availableCash", re.I), "[ẩn]"),
             (re.compile(r"\b(NAV|CAGR)\b", re.I), "[ẩn]")]
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


class Cfg:
    def __init__(self, root=None, ledger=None, out=None, bus_root=None, wc_root=None, today=None):
        self.root = root or HERE_ROOT
        self.ledger = ledger or os.environ.get("WT_LEDGER") or os.path.join(self.root, "kb", "work_ledger.jsonl")
        self.out = out or os.environ.get("WT_OUT") or os.path.join(self.root, "state", "work_tree", "merged.json")
        br = bus_root or os.environ.get("WT_BUS_ROOT")
        if not br:  # worktree dev: bus/ gitignored → nằm ở cây canonical
            br = self.root if os.path.isdir(os.path.join(self.root, "bus", "inbox")) else CANON_MIKE
        self.bus_root = br
        self.wc_root = wc_root or os.path.dirname(CANON_MIKE)
        self.today = today or datetime.now(ICT).date()
        self.audit = os.path.join(HERE_ROOT, "bin", "bus_question_audit.py")


def sanitize(s):
    if not isinstance(s, str):
        return s
    for rx, rep in SENSITIVE:
        s = rx.sub(rep, s)
    return s


def clean(o):
    if isinstance(o, str):
        return sanitize(o)
    if isinstance(o, list):
        return [clean(x) for x in o]
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    return o


def first_date(*texts):
    for t in texts:
        m = DATE_RE.search(t or "")
        if m:
            try:
                datetime.strptime(m.group(0), "%Y-%m-%d")
                return m.group(0)
            except ValueError:
                pass
    return None


def paths_in(cfg, text):
    """Mọi đường dẫn .md/.json trong chuỗi nguồn; tên trơn → thử kb/projects/."""
    out = []
    for m in re.findall(r"[\w./-]+\.(?:md|json)\b", text or ""):
        if "/" not in m and os.path.exists(os.path.join(cfg.root, "kb", "projects", m)):
            m = "kb/projects/" + m
        if m not in out:
            out.append(m)
    return [{"label": os.path.basename(m), "path": m} for m in out[:4]]


def short(s, n=160):
    s = re.sub(r"\s+", " ", (s or "")).strip()
    return s if len(s) <= n else s[:n - 1] + "…"


def load_json(path, warns):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # nguồn hỏng không được làm sập cả cây
        warns.append("không đọc được %s: %s" % (os.path.basename(path), e))
        return None


def guess_branch(text):
    t = text.lower()
    rules = [
        (("due-diligence", "due diligence", "fear-buy", " dd ", "dgc", "tv1"), "Research/DD cổ phiếu"),
        (("universe", "oshares", "cổ tức tiền", "adjfactor", "pit ", "ticker_prune"), "Research/Dữ liệu & PIT"),
        (("corporate_action", "corp-action", "corp action"), "Operation/Corp-action"),
        (("báo cáo", "report", "cadence"), "Operation/Báo cáo & cadence"),
        (("plan-approval", "cron", "selfcheck", "incident", "retro"), "Operation/Cron-hạ tầng-KB"),
        (("zalopay", "spacex", "tài khoản"), "Portfolio/Tài khoản live"),
        (("margin", "capit", "gate", "brake"), "Portfolio/Rủi ro & gate"),
        (("paper",), "Research/Paper programs"),
        (("order_book", "fill", "execution", "opening", "expvol"), "Research/Thực thi"),
    ]
    for keys, br in rules:
        if any(k in t for k in keys):
            return br
    return "Research/Tín hiệu & chiến lược"


def type_of(branch):
    return ROOT_TYPE.get((branch or "").split("/")[0], "research")


# ---------------------------------------------------------------- derived sources
def d_paper(cfg, warns):
    d = load_json(os.path.join(cfg.root, "kb", "paper_programs_registry.json"), warns) or {}
    upd = d.get("updated")
    out = []
    for p in d.get("programs", []):
        pid = p.get("id")
        if not pid:
            continue
        st = str(p.get("status") or "").split(" ")[0].lower()
        status = "live" if st.startswith("graduated") else "closed" if st == "closed" else "active"
        due = first_date(p.get("review_date"), p.get("end")) if status == "active" else None
        name = p.get("name") or pid
        summ = {"live": "Chương trình paper đã tốt nghiệp, đang chạy live.",
                "closed": "Chương trình paper đã đóng."}.get(
            status, "Chương trình paper đang chạy" + (", mốc xem lại %s." % due if due else ", theo sự kiện."))
        detail = "**Mục tiêu:** %s\n\n**Điều kiện kết thúc:** %s" % (
            short(p.get("objective"), 600) or "—", short(p.get("end_or_trigger"), 600) or "—")
        links = []
        ch = "kb/paper_programs_charter/%s.md" % pid
        if os.path.exists(os.path.join(cfg.root, ch)):
            links.append({"label": "Hiến chương", "path": ch})
        out.append({"id": "paper:" + pid, "branch": "Research/Paper programs", "title": name,
                    "summary": summ, "detail": detail, "type": "research", "status": status,
                    "owner": p.get("owner") or "", "opened": p.get("start"), "updated": upd, "due": due,
                    "links": links, "source": "derived:paper_programs_registry"})
    return out


def d_watchlist(cfg, warns):
    d = load_json(os.path.join(cfg.root, "kb", "dashboard_watchlist.json"), warns) or {}
    out = []
    for m in d.get("milestones", []):
        date, label = m.get("date"), m.get("label") or ""
        if not date:
            continue
        slug = wl.slugify("%s-%s" % (date, label), 48)
        src = m.get("source")
        out.append({"id": "wl:" + slug, "branch": "Watch/Mốc định kỳ", "title": short(label, 110),
                    "summary": "Mốc %s: %s" % (date, short(label, 120)), "detail": label, "type": "watch",
                    "status": "waiting", "owner": "Mike", "due": date, "updated": None,
                    "links": paths_in(cfg, src), "source": "derived:dashboard_watchlist"})
    for r in d.get("research_backlog", []):
        rid = r.get("id")
        if not rid:
            continue
        src = r.get("source", "")
        out.append({"id": "wl:" + rid, "branch": guess_branch(r.get("idea", "")), "title": short(r.get("idea"), 100),
                    "summary": short(r.get("idea"), 160), "detail": r.get("idea", "") + "\n\nNguồn: " + src,
                    "type": "research", "status": "idea", "priority": int(r.get("priority") or 3) if str(r.get("priority") or 3) in "123" else 3,
                    "owner": "Mike", "links": paths_in(cfg, src),
                    "source": "derived:dashboard_watchlist"})
    return out


def d_sbw(cfg, warns):
    d = load_json(os.path.join(cfg.root, "kb", "structural_break_watch.json"), warns) or {}
    out = []
    for e in d.get("events", []):
        eid = e.get("id")
        if not eid:
            continue
        nxt = [x for x in (e.get("next_checks") or []) if DATE_RE.fullmatch(str(x)) and x >= cfg.today.isoformat()]
        due = nxt[0] if nxt else (d.get("next_review") if e.get("status") != "closed" else None)
        trig = e.get("status") == "triggered"
        concl = e.get("conclusion")
        summ = short(concl, 160) if concl else "Theo dõi: %s." % short(e.get("label"), 120)
        out.append({"id": "sbw:" + eid, "branch": "Watch/Vĩ mô & cấu trúc", "title": e.get("label") or eid,
                    "summary": summ, "detail": "Trạng thái: %s\n\nKết luận: %s\n\nNguồn phát hiện: %s" % (
                        e.get("status"), concl or "—", e.get("detection_source") or "—"),
                    "type": "watch", "status": "active" if trig else "waiting", "owner": d.get("owner") or "Mike",
                    "opened": d.get("opened"), "updated": None, "due": due,
                    "links": [{"label": "Giao thức", "path": "kb/projects/amh-structural-break-protocol-20260910.md"}],
                    "source": "derived:structural_break_watch"})
    return out


def d_busq(cfg, warns):
    if not os.path.exists(cfg.audit):
        warns.append("thiếu bus_question_audit.py")
        return []
    env = dict(os.environ, BUS_AUDIT_ROOT=cfg.bus_root)
    try:
        p = subprocess.run([sys.executable, cfg.audit, "--json"], env=env, capture_output=True, text=True, timeout=90)
        data = json.loads(p.stdout)
    except Exception as e:
        warns.append("bus_question_audit lỗi: %s" % e)
        return []
    out = []
    for q in data.get("pending", []):
        ag, tp = q.get("agent") or "?", q.get("topic") or "?"
        ts = (q.get("ts") or "")[:10] or None
        auto = tp.startswith("selfcheck-red") or tp.startswith("wake")
        low = tp.lower()
        br = ("Portfolio/Rủi ro & gate" if any(k in low for k in ("plan-", "nav", "gate")) and not auto
              else "Operation/Sự cố & retro")
        age = int(q.get("age_days") or 0)
        out.append({"id": "busq:%s/%s" % (ag, tp), "branch": br, "title": tp,
                    "summary": "Câu hỏi bus của %s chưa được đóng (%d ngày)." % (ag, age),
                    "detail": "Agent hỏi: %s\nTopic: %s\nGửi lúc: %s (UTC)\n\nĐóng bằng answer/decision trên bus "
                              "(skill bus-question-closure)." % (ag, tp, q.get("ts")),
                    "type": "ops", "status": "waiting", "priority": 2 if age >= 3 else 3, "owner": ag,
                    "opened": ts, "updated": ts, "needs_user": not auto,
                    "waiting_on": {"who": "user" if not auto else ag, "what": "đóng câu hỏi bus", "since": ts},
                    "source": "derived:bus_question"})
    return out


VERDICTS = [("NO-GO", r"NO-GO"), ("KHÔNG WIRE", r"KHÔNG WIRE"), ("IMPLEMENTED", r"IMPLEMENTED"),
            ("INCONCLUSIVE", r"INCONCLUSIVE"), ("GO", r"(?<![\w-])GO(?![\w-])")]
VERDICT_STATUS = {"NO-GO": "NO-GO", "GO": "GO", "IMPLEMENTED": "live", "KHÔNG WIRE": "closed", "INCONCLUSIVE": "closed"}


def d_projects(cfg, warns):
    pdir = os.path.join(cfg.root, "kb", "projects")
    idx = os.path.join(pdir, "INDEX.md")
    items, covered = {}, set()
    if os.path.exists(idx):
        section, cur, entries = None, None, []
        for line in open(idx, encoding="utf-8"):
            line = line.rstrip("\n")
            if line.startswith("## "):
                section = "closed" if "đã đóng" in line else "open" if "ĐANG MỞ" in line else None
                cur = None
            elif section and line.startswith("- "):
                cur = {"section": section, "text": line[2:]}
                entries.append(cur)
            elif cur and line.startswith(" ") and line.strip() and not line.strip().startswith("<!--"):
                cur["text"] += " " + line.strip()
        for e in entries:
            t = e["text"]
            m = re.search(r"`([^`]+\.md)`", t) or re.search(r"\]\(([^)]+\.md)\)", t)
            if not m:
                continue
            ref = m.group(1)
            path = ref if "/" in ref else "kb/projects/" + ref
            stem = os.path.splitext(os.path.basename(ref))[0]
            if stem in ("REPORT", "FINDINGS", "README"):
                stem = os.path.basename(os.path.dirname(ref)) or stem
            if "/" not in ref:
                covered.add(stem)
            iid = "proj:" + stem
            if iid in items:
                continue
            dm = re.match(r"(\d{4}-\d{2}-\d{2})", t)
            date = dm.group(1) if dm else None
            lm = re.match(r"\[([^\]]+)\]", t)
            if lm:
                title = lm.group(1)
            else:
                title = re.sub(r"^\d{4}-\d{2}-\d{2}(→[\d-]+)?\s*", "", t.split("→")[0].split(" — ")[0])
            title = short(re.sub(r"[`*]", "", title), 100)
            after = re.split(r"`[^`]+\.md`\)?|\]\([^)]+\.md\)", t, 1)[-1].lstrip(" —-:")
            after = re.sub(r"[`*]", "", after)
            label = None
            if e["section"] == "closed":
                for lab, rx in VERDICTS:
                    if re.search(rx, t):
                        label = lab
                        break
            status = VERDICT_STATUS[label] if label else ("closed" if e["section"] == "closed" else "active")
            br = guess_branch(t)
            items[iid] = {"id": iid, "branch": br, "title": title, "summary": short(after or title),
                          "detail": re.sub(r"[`*]", "", t), "type": type_of(br), "status": status,
                          "owner": "", "opened": date, "updated": date,
                          "verdict": {"label": label, "text": short(after, 240)} if label else None,
                          "links": [{"label": "Tài liệu", "path": path}], "confidence": "med",
                          "source": "derived:projects_index"}
    for f in sorted(glob.glob(os.path.join(pdir, "*.md"))):
        stem = os.path.splitext(os.path.basename(f))[0]
        if stem == "INDEX" or stem in covered or "proj:" + stem in items:
            continue
        try:
            head = open(f, encoding="utf-8").read(3000)
        except OSError:
            continue
        hm = re.search(r"^#\s+(.+)$", head, re.M)
        title = short(re.sub(r"[`*]", "", hm.group(1)) if hm else stem, 100)
        dm = re.search(r"(\d{8})(?!\d)", stem)
        date = None
        if dm:
            try:
                date = datetime.strptime(dm.group(1), "%Y%m%d").date().isoformat()
            except ValueError:
                pass
        label = "NO-GO" if re.search(r"NO-GO", head[:1500]) else None
        closed = re.search(r"ĐÓNG|XONG|KHÉP|HOÀN TẤT|DONE", head[:1500])
        status = "NO-GO" if label else "closed" if closed else "active"
        br = guess_branch(stem + " " + title)
        items["proj:" + stem] = {
            "id": "proj:" + stem, "branch": br, "title": title,
            "summary": "Chưa phân loại — cần backfill đọc tài liệu.", "detail": short(head.split("\n", 2)[-1], 500),
            "type": type_of(br), "status": status, "owner": "", "opened": date, "updated": date,
            "verdict": {"label": label, "text": ""} if label else None,
            "links": [{"label": "Tài liệu", "path": "kb/projects/%s.md" % stem}], "confidence": "low",
            "source": "derived:projects_scan"}
    return list(items.values())


def d_jobs(cfg, warns):
    cutoff = time.time() - 30 * 86400
    jobs = []
    for f in glob.glob(os.path.join(cfg.bus_root, "bus", "jobs", "*.json")):
        try:
            j = json.load(open(f, encoding="utf-8"))
            ts = float(j.get("started_at") or 0)
        except Exception:
            continue
        if ts < cutoff:
            continue
        jobs.append({"job_id": j.get("job_id"), "to": j.get("to"), "from": j.get("from"),
                     "status": j.get("status"), "ts": datetime.fromtimestamp(ts, ICT).isoformat(timespec="minutes"),
                     "summary": short(sanitize(j.get("prompt_summary") or ""), 100)})
    jobs.sort(key=lambda j: j["ts"], reverse=True)
    return jobs


# ---------------------------------------------------------------- merge
def finalize(it, ledger_it):
    for k, v in ledger_it.items():
        if k in wl.FIELDS and k != "aliases":
            it[k] = v
    it["notes"] = ledger_it.get("notes", [])
    it["aliases"] = ledger_it.get("aliases", [])
    it.setdefault("branch", "Chưa phân loại")
    it.setdefault("title", it["id"])
    it.setdefault("summary", "")
    it.setdefault("detail", "")
    it.setdefault("type", type_of(it["branch"]))
    it.setdefault("status", "active")
    it.setdefault("priority", 3)
    it.setdefault("owner", "")
    it.setdefault("opened", None)
    it.setdefault("updated", it.get("opened"))
    it.setdefault("due", None)
    it.setdefault("verdict", None)
    it.setdefault("waiting_on", None)
    it.setdefault("needs_user", False)
    it.setdefault("links", [])
    it.setdefault("depends_on", [])
    it.setdefault("source", "curated")
    it["priority"] = it["priority"] if it["priority"] in (1, 2, 3) else 3
    if it["source"] == "user":
        it["ack"] = bool(it.get("ack", False))
    return it


def check_links(cfg, items, warns):
    roots = [cfg.root, cfg.wc_root, CANON_MIKE]
    for it in items:
        for ln in it["links"]:
            p = os.path.normpath(ln.get("path") or "")
            ok = bool(p) and not p.startswith(("..", "/")) and any(os.path.exists(os.path.join(r, p)) for r in roots)
            ln["missing"] = not ok
            if not ok:
                warns.append("link thiếu: %s → %s" % (it["id"], ln.get("path")))


def build(cfg=None):
    cfg = cfg or Cfg()
    t0 = time.time()
    warns = []
    today = cfg.today
    led = wl.fold(path=cfg.ledger)
    derived = {}
    for fn in (d_projects, d_paper, d_watchlist, d_sbw, d_busq):
        for it in fn(cfg, warns):
            derived.setdefault(it["id"], it)
    # alias gộp (ledger merge): derived trùng alias bị loại, canonical nhận
    alias_map = {a: i["id"] for i in led.values() for a in i.get("aliases", [])}
    for a in list(derived):
        if a in alias_map:
            derived.pop(a)
    items = {}
    for iid in set(derived) | set(led):
        items[iid] = finalize(dict(derived.get(iid, {"id": iid})), led.get(iid, {}))
    items = list(items.values())

    jobs = d_jobs(cfg, warns)
    kw = {}
    for it in items:
        key = it["id"].split(":", 1)[1].split("/")[-1].lower()
        if len(key) >= 6:
            kw[key] = it["id"]
        for a in it["aliases"]:
            kw[a.split(":", 1)[-1].lower()] = it["id"]
    byid = {it["id"]: it for it in items}
    for it in items:
        it["recent_jobs"] = []
    for j in jobs:
        text = (j["summary"] or "").lower()
        for k, iid in kw.items():
            if k in text and len(byid[iid]["recent_jobs"]) < 5:
                byid[iid]["recent_jobs"].append({x: j[x] for x in ("job_id", "to", "status", "ts", "summary")})

    check_links(cfg, items, warns)

    cut7 = (today - timedelta(days=7)).isoformat()
    for it in items:
        is_open = it["status"] in OPEN
        age = None
        if it.get("updated"):
            try:
                age = (today - datetime.strptime(it["updated"][:10], "%Y-%m-%d").date()).days
            except ValueError:
                pass
        it["overdue"] = bool(is_open and it.get("due") and it["due"] < today.isoformat())
        lim = {"research": 30, "ops": 14}.get(it["type"])
        it["stale"] = bool(is_open and (it["overdue"] or (lim and age is not None and age > lim)))

    def pr(it):
        return (it["priority"], it.get("due") or "9999", it["title"])
    opn = [i for i in items if i["status"] in OPEN]
    attention = {
        "need_user": [i["id"] for i in sorted((i for i in opn if i["needs_user"]), key=pr)],
        "overdue": [i["id"] for i in sorted((i for i in opn if i["stale"]), key=pr)],
        "recent": [i["id"] for i in sorted((i for i in items if (i.get("updated") or "") >= cut7),
                                           key=lambda i: i["updated"], reverse=True)][:30],
        "ideas": [i["id"] for i in sorted((i for i in items if i["status"] == "idea"), key=pr)],
        "inbox": [i["id"] for i in sorted((i for i in items if i["source"] == "user" and not i.get("ack")),
                                          key=lambda i: i.get("opened") or "")],
    }

    # dedup cảnh báo (≥0,85) — bỏ cặp đã là alias của nhau
    titled = [(i["id"], i["title"].lower()) for i in items if len(i["title"]) > 12]
    dups = []
    for a in range(len(titled)):
        for b in range(a + 1, len(titled)):
            ia, ta = titled[a]
            ib, tb = titled[b]
            if ib in byid[ia]["aliases"] or ia in byid[ib]["aliases"]:
                continue
            sm = difflib.SequenceMatcher(None, ta, tb)
            if sm.real_quick_ratio() >= .85 and sm.quick_ratio() >= .85 and sm.ratio() >= .85:
                dups.append({"a": ia, "b": ib, "ratio": round(sm.ratio(), 2)})

    bc = {}
    for i in items:
        c = bc.setdefault(i["branch"], [0, 0])
        c[0] += 1
        c[1] += i["status"] in OPEN
    names = list(SKELETON) + sorted(b for b in bc if b not in SKELETON)
    def border(b):
        r = b.split("/")[0]
        return (ROOT_ORDER.index(r) if r in ROOT_ORDER else 99, names.index(b))
    branches = [{"branch": b, "root": b.split("/")[0], "sub": b.split("/", 1)[1] if "/" in b else "",
                 "count": bc.get(b, [0, 0])[0], "open_count": bc.get(b, [0, 0])[1]}
                for b in sorted(names, key=border)]

    items.sort(key=lambda i: (border(i["branch"]), i["priority"], i["title"]))
    by_status = {}
    for i in items:
        by_status[i["status"]] = by_status.get(i["status"], 0) + 1
    by_src = {}
    for i in items:
        s = i["source"].split(":")[0] + (":" + i["source"].split(":")[1] if ":" in i["source"] else "")
        by_src[s] = by_src.get(s, 0) + 1
    counts = {"total": len(items), "by_status": by_status, "by_source": by_src,
              "need_user": len(attention["need_user"]), "overdue": len(attention["overdue"]),
              "recent": len(attention["recent"]), "ideas": len(attention["ideas"]), "inbox": len(attention["inbox"]),
              "jobs_30d": len(jobs)}
    out = {"generated_at": datetime.now(ICT).isoformat(timespec="seconds"), "attention_format": "ids",
           "counts": counts, "attention": attention, "items": items, "branches": branches,
           "warnings": {"dups": dups, "other": sorted(set(warns))},
           "build_seconds": round(time.time() - t0, 2)}
    return clean(out)


def write_merged(cfg=None):
    cfg = cfg or Cfg()
    out = build(cfg)
    os.makedirs(os.path.dirname(cfg.out), exist_ok=True)
    tmp = cfg.out + ".tmp.%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, cfg.out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    cfg = Cfg(out=a.out)
    o = write_merged(cfg)
    if not a.quiet:
        c = o["counts"]
        print("work_tree_build: %d item | chờ quyết %d · quá hạn %d · mới %d · ý tưởng %d · chờ xử lý %d | jobs30d %d | "
              "dup %d · cảnh báo %d | %.2fs → %s" % (c["total"], c["need_user"], c["overdue"], c["recent"], c["ideas"],
                                                    c["inbox"], c["jobs_30d"], len(o["warnings"]["dups"]),
                                                    len(o["warnings"]["other"]), o["build_seconds"], cfg.out))
        print("by_status:", json.dumps(c["by_status"], ensure_ascii=False), "by_source:", json.dumps(c["by_source"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
