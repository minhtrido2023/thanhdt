#!/usr/bin/env python3
"""weekly_orphan_review.py — rà MỒ CÔI hằng tuần: thứ để lâu không tham chiếu, không định hướng ⇒ dọn.

User chỉ đạo 2026-11-19 22:08 ICT: "bất cứ thứ gì để quá lâu không có tham chiếu, không có định hướng thì
dọn dẹp; đưa vào lịch dọn dẹp hàng tuần". Kế hoạch + luật: kb/projects/weekly-orphan-review-plan-20261119.md.

Mặc định DRY-RUN (chỉ báo cáo). `--apply` mới xoá, và CHỈ những mục bên dưới:
  R  research/*  (agents/Taylor/research, trừ dd_* và mục trong kb/cleanup_keep.txt)
     - TRIM: thư mục im > R_IDLE_DAYS, KHÔNG bị code/cron tham chiếu ⇒ xoá file không-.md (tracked: git rm
       + commit theo pathspec, khôi phục được từ lịch sử; untracked: chỉ xoá khi md5 không khớp mục pin/registry/code)
     - REMOVE_DIR: như trên + không .md + không KB nào nhắc + im > R_ORPHAN_DAYS ⇒ xoá cả thư mục
     GRACE: mục phải xuất hiện ở ≥ GRACE_DAYS ngày TRƯỚC (state) mới được xoá — cho người kịp ghi vào cleanup_keep.txt.
  T  /tmp/*  top-level của chính user, im > T_IDLE_DAYS, không tiến trình nào nhắc tới ⇒ rm -rf (không grace).
CHỈ BÁO, KHÔNG BAO GIỜ XOÁ: dd_* (nguồn DD), data/bq_cache_asof*, data/pinned_ledgers, worktree chưa merge,
file ignored lớn trong data/ (liệt kê top để người quyết).
Thoát: 0 luôn (cron). Đầu ra: logs/orphan_review/<ngày>.md + digest 1 tin qua bin/notify.sh khi có việc.
"""
import argparse, datetime as dt, glob, hashlib, json, os, re, subprocess, sys, time

R_IDLE_DAYS = 3
R_ORPHAN_DAYS = 14
T_IDLE_DAYS = 7
GRACE_DAYS = 7
MIN_HEAVY = 1 << 20
BIG_FILE = 50 << 20
BIG_FILE_AGE = 30
NEVER = ("bq_cache", "pinned_ledgers")


def sh(cmd, cwd=None, inp=None):
    return subprocess.run(cmd, cwd=cwd, input=inp, capture_output=True, text=True)


def newest_mtime(path):
    best = 0.0
    for root, _, fs in os.walk(path):
        for f in fs:
            try:
                best = max(best, os.lstat(os.path.join(root, f)).st_mtime)
            except OSError:
                pass
    return best


def corpus(root):
    """Văn bản mà tham chiếu 'sống' có thể nằm: code, cron, registry. Không gồm chính thư mục research."""
    parent = os.path.dirname(root)
    pats = ["bin/*.py", "bin/*.sh", "*.py", "data/*.json", "kb/projects/paper_programs_registry.json",
            os.path.join(parent, "*.py"), os.path.join(parent, "trading_bot", "*.py"),
            os.path.join(parent, "data", "results_registry.md"),
            os.path.join(parent, "data", "pinned_ledgers", "PINS.jsonl")]
    out = []
    for g in pats:
        for f in glob.glob(g if os.path.isabs(g) else os.path.join(root, g)):
            try:
                out.append(open(f, errors="ignore").read())
            except OSError:
                pass
    out.append(sh(["crontab", "-l"]).stdout)
    return "\n".join(out)


def kb_corpus(root):
    out = []
    for f in glob.glob(os.path.join(root, "kb", "projects", "*.md")) + glob.glob(os.path.join(root, "kb", "*.md")):
        if "research-prune" in f or "weekly-orphan" in f:
            continue
        try:
            out.append(open(f, errors="ignore").read())
        except OSError:
            pass
    return "\n".join(out)


def load_keep(root):
    p = os.path.join(root, "kb", "cleanup_keep.txt")
    keep = []
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            l = l.split("#")[0].strip()
            if l:
                keep.append(l.rstrip("/"))
    return keep


def scan_research(root, now, code, kb, keep, min_heavy):
    base = os.path.join(root, "agents", "Taylor", "research")
    items, protected = [], []
    if not os.path.isdir(base):
        return items, protected
    tracked = set(sh(["git", "ls-files", "-z", "agents/Taylor/research"], cwd=root).stdout.split("\0"))
    for d in sorted(os.listdir(base)):
        p = os.path.join(base, d)
        if not os.path.isdir(p):
            continue
        rel = f"agents/Taylor/research/{d}"
        if d.startswith("dd_") or any(rel == k or rel.startswith(k + "/") or d == k for k in keep):
            protected.append((d, "dd/keep"))
            continue
        age = (now - newest_mtime(p)) / 86400
        if age < R_IDLE_DAYS:
            continue
        if d in code:
            protected.append((d, "code/cron tham chiếu"))
            continue
        heavy, has_md = [], False
        for root_, _, fs in os.walk(p):
            for f in fs:
                fp = os.path.join(root_, f)
                if f.lower().endswith(".md"):
                    has_md = True
                    continue
                try:
                    heavy.append((fp, os.lstat(fp).st_size))
                except OSError:
                    pass
        hb = sum(s for _, s in heavy)
        kb_ref = d in kb
        if not kb_ref and not has_md and age > R_ORPHAN_DAYS:
            allb = hb + sum(os.lstat(os.path.join(r, f)).st_size for r, _, fs in os.walk(p) for f in fs if f.lower().endswith(".md"))
            items.append({"key": f"R:{d}:REMOVE_DIR", "kind": "R", "action": "REMOVE_DIR", "name": d, "bytes": allb,
                          "age": round(age), "why": "không .md, không KB nhắc, không code tham chiếu"})
        elif hb >= min_heavy:
            items.append({"key": f"R:{d}:TRIM", "kind": "R", "action": "TRIM", "name": d, "bytes": hb, "age": round(age),
                          "why": f"im {round(age)}d, không code/cron tham chiếu" + ("" if kb_ref else ", KB không nhắc"),
                          "tracked": sum(1 for fp, _ in heavy if os.path.relpath(fp, root) in tracked)})
    return items, protected


def scan_tmp(tmp, now, min_bytes):
    items = []
    if not os.path.isdir(tmp):
        return items
    ps = sh(["ps", "-eo", "args"]).stdout
    for n in sorted(os.listdir(tmp)):
        p = os.path.join(tmp, n)
        if n.startswith((".", "claude", "tmux", "systemd", "snap")):
            continue
        try:
            st = os.lstat(p)
        except OSError:
            continue
        if st.st_uid != os.getuid():
            continue
        m = newest_mtime(p) if os.path.isdir(p) else st.st_mtime
        age = (now - max(m, st.st_mtime)) / 86400
        if age <= T_IDLE_DAYS or p in ps:
            continue
        size = sum(os.lstat(os.path.join(r, f)).st_size for r, _, fs in os.walk(p) for f in fs) if os.path.isdir(p) else st.st_size
        if size >= min_bytes:
            items.append({"key": f"T:{n}", "kind": "T", "action": "RM", "name": p, "bytes": size, "age": round(age),
                          "why": f"/tmp im {round(age)}d, không tiến trình nhắc tới"})
    return items


def scan_report_only(root, now):
    out = []
    parent = os.path.dirname(root)
    for r in {root, parent}:
        res = sh(["git", "worktree", "list", "--porcelain"], cwd=r).stdout.split("\n\n")
        master = "master" if r == root else "main"
        for blk in res:
            m = re.search(r"^worktree (.+)$", blk, re.M)
            b = re.search(r"^branch refs/heads/(.+)$", blk, re.M)
            if not m or m.group(1) == r or not b or not os.path.isdir(m.group(1)):
                continue
            wp, br = m.group(1), b.group(1)
            merged = sh(["git", "merge-base", "--is-ancestor", br, master], cwd=r).returncode == 0
            last = sh(["git", "log", "-1", "--format=%ct", br], cwd=r).stdout.strip()
            age = (now - int(last)) / 86400 if last.isdigit() else 0
            dirty = bool(sh(["git", "status", "--porcelain"], cwd=wp).stdout.strip())
            if not merged and age > 7 and not dirty:
                out.append(f"worktree mồ côi? {wp} (nhánh {br} chưa merge, commit cuối {round(age)}d trước, sạch)")
    big = []
    data = os.path.join(parent, "data")
    for r_, ds, fs in os.walk(data):
        ds[:] = [d for d in ds if not d.startswith(NEVER)]
        for f in fs:
            fp = os.path.join(r_, f)
            try:
                st = os.lstat(fp)
            except OSError:
                continue
            if st.st_size >= BIG_FILE and (now - st.st_mtime) / 86400 > BIG_FILE_AGE:
                big.append((st.st_size, fp, round((now - st.st_mtime) / 86400)))
    for s, fp, a in sorted(big, reverse=True)[:12]:
        out.append(f"file lớn cũ trong data/ (CHỈ BÁO): {s >> 20}MB, {a}d — {os.path.relpath(fp, parent)}")
    return out


def md5_guard(files, text):
    """Trả danh sách file untracked ĐƯỢC PHÉP xoá: md5[:8] không xuất hiện trong code/registry/PINS."""
    ok = []
    for fp in files:
        try:
            md = hashlib.md5(open(fp, "rb").read()).hexdigest()[:8]
        except OSError:
            continue
        if md not in text:
            ok.append(fp)
    return ok


def apply_item(root, it, text, now):
    freed = 0
    if it["kind"] == "T":
        sh(["rm", "-rf", "--", it["name"]])
        return it["bytes"]
    d = os.path.join(root, "agents", "Taylor", "research", it["name"])
    rel = os.path.relpath(d, root)
    if it["action"] == "REMOVE_DIR":
        files = [os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs]
    else:
        files = [os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs if not f.lower().endswith(".md")]
    tracked = set(sh(["git", "ls-files", "-z", rel], cwd=root).stdout.split("\0"))
    trk = [f for f in files if os.path.relpath(f, root) in tracked]
    unt = md5_guard([f for f in files if os.path.relpath(f, root) not in tracked], text)
    if trk:
        for i in range(0, len(trk), 2000):
            sh(["git", "rm", "-q", "--ignore-unmatch", "--"] + [os.path.relpath(f, root) for f in trk[i:i + 2000]], cwd=root)
        sh(["git", "commit", "-q", "--only", "-m",
            f"chore(weekly-orphan-review): {it['action']} {rel} ({len(trk)} file tracked; user duyệt luật 2026-11-19)\n\n"
            "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>", "--", rel], cwd=root)
    for f in unt:
        try:
            freed += os.lstat(f).st_size
            os.remove(f)
        except OSError:
            pass
    if it["action"] == "REMOVE_DIR":
        sh(["rm", "-rf", "--", d])
    for r, ds, fs in os.walk(d, topdown=False):
        if not os.listdir(r):
            try:
                os.rmdir(r)
            except OSError:
                pass
    return it["bytes"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    ap.add_argument("--tmp", default="/tmp")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--state")
    ap.add_argument("--now", type=float, default=None, help="epoch (selfcheck)")
    ap.add_argument("--min-heavy", type=int, default=MIN_HEAVY)
    ap.add_argument("--min-tmp", type=int, default=MIN_HEAVY)
    ap.add_argument("--no-notify", action="store_true")
    ap.add_argument("--no-report-only", action="store_true")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    now = a.now if a.now is not None else time.time()
    today = dt.datetime.fromtimestamp(now).date()
    sp = a.state or os.path.join(root, "state", "orphan_review_state.json")
    try:
        state = json.load(open(sp))
    except (OSError, ValueError):
        state = {}
    code, kb, keep = corpus(root), kb_corpus(root), load_keep(root)
    items, protected = scan_research(root, now, code, kb, keep, a.min_heavy)
    items += scan_tmp(a.tmp, now, a.min_tmp)
    info = [] if a.no_report_only else scan_report_only(root, now)
    new_state, applied, pending = {}, [], []
    for it in items:
        first = state.get(it["key"], today.isoformat())
        new_state[it["key"]] = first
        it["first_seen"] = first
        grace_ok = it["kind"] == "T" or (today - dt.date.fromisoformat(first)).days >= GRACE_DAYS
        if a.apply and grace_ok:
            it["freed"] = apply_item(root, it, code, now)
            applied.append(it)
            new_state.pop(it["key"], None)
        else:
            pending.append(it)
    os.makedirs(os.path.dirname(sp), exist_ok=True)
    tmp = sp + ".tmp"
    json.dump(new_state, open(tmp, "w"), indent=1)
    os.replace(tmp, sp)
    mb = lambda b: f"{b / 2**20:.0f}MB"
    L = [f"# Orphan review {today} ({'APPLY' if a.apply else 'DRY-RUN'})", ""]
    L.append(f"## Đã xoá ({len(applied)}, {mb(sum(i['bytes'] for i in applied))})")
    L += [f"- {i['action']} {i['name']} — {mb(i['bytes'])} — {i['why']}" for i in applied] or ["- (không)"]
    L.append(f"\n## Ứng viên chờ grace {GRACE_DAYS} ngày ({len(pending)}, {mb(sum(i['bytes'] for i in pending))})")
    L += [f"- {i['action']} {i['name']} — {mb(i['bytes'])} — {i['why']} — thấy lần đầu {i['first_seen']}" for i in pending] or ["- (không)"]
    L.append("\n## Chỉ báo (không tự xoá)")
    L += [f"- {x}" for x in info] or ["- (không)"]
    L.append(f"\n## Được bảo vệ (không xoá): {len(protected)} thư mục (dd_*/keep/có code tham chiếu)")
    rep = "\n".join(L)
    od = os.path.join(root, "logs", "orphan_review")
    os.makedirs(od, exist_ok=True)
    open(os.path.join(od, f"{today}.md"), "w", encoding="utf-8").write(rep + "\n")
    print(rep)
    if (applied or pending or info) and not a.no_notify:
        n = os.path.join(root, "bin", "notify.sh")
        if os.path.exists(n):
            msg = (f"🧹 Rà mồ côi tuần {today}: đã xoá {len(applied)} ({mb(sum(i['bytes'] for i in applied))}), "
                   f"chờ grace {len(pending)} ({mb(sum(i['bytes'] for i in pending))}), chỉ báo {len(info)}. "
                   f"Muốn GIỮ mục nào ⇒ ghi vào kb/cleanup_keep.txt trước khi hết grace. Chi tiết: logs/orphan_review/{today}.md")
            sh([n, msg])
    return 0


if __name__ == "__main__":
    sys.exit(main())
