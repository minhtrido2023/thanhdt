#!/usr/bin/env python3
"""dd_skeptic_run — chạy fundamental-skeptic headless cho 1 báo cáo DD và GHI verdict thành file (script ghi, agent KHÔNG ghi).

  python3 bin/dd_skeptic_run.py --dir agents/Taylor/research/dd_<MÃ>_<ngày> --report <REPORT.md> [--round N] [--dry-run]

Đầu ra: <dir>/skeptic/rN.json (+ rN_raw.md; có cost_usd lấy từ total_cost_usd của claude --output-format json, null nếu thiếu). N mặc định = max(rN.json hiện có)+1; --round trùng file có sẵn ⇒ từ chối.
Brief dựng từ template cố định (mù giá) và PHẢI qua bin/dd_blind_lint.py --mode skeptic: rc≠0 ⇒ không chạy.
rc: 0 ok · 2 lỗi dùng/đầu vào · 3 brief bị lint chặn · 4 claude lỗi/verdict không parse được (KHÔNG ghi rN.json; thô lưu logs/).
Env: DD_SKEPTIC_CLAUDE_BIN (stub test) · DD_SKEPTIC_AGENT_DEF · DD_SKEPTIC_MODEL (mặc định opus) · DD_SKEPTIC_WORKDIR · DD_SKEPTIC_TIMEOUT_S.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICT = dt.timezone(dt.timedelta(hours=7))
ENUM = ("CONFIRMED", "REFUTED", "INCONCLUSIVE")
CLAUDE = os.environ.get("DD_SKEPTIC_CLAUDE_BIN", "/home/trido/.local/bin/claude")
AGENT_DEF = os.environ.get("DD_SKEPTIC_AGENT_DEF", os.path.expanduser("~/.claude/agents/fundamental-skeptic.md"))
MODEL = os.environ.get("DD_SKEPTIC_MODEL", "opus")
WORKDIR = os.environ.get("DD_SKEPTIC_WORKDIR", "/home/trido/thanhdt/WorkingClaude")
TIMEOUT_S = int(os.environ.get("DD_SKEPTIC_TIMEOUT_S", "1500"))
FRAMEWORK = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/calculated_fear_state_backstop.md"

# Template CỐ ĐỊNH — không giá thị trường / PE / sổ giá-tâm. Dòng đường dẫn có blind-ok vì tên thư mục DD chứa mã (bắt buộc để skeptic mở được file).
BRIEF = """Nhiệm vụ: phản biện (bác bỏ) báo cáo due diligence dưới đây. Làm cả hai chiều: tìm chỗ yếu khiến kết luận SAI THEO CHIỀU ĐẮT lẫn chiều RẺ.
Báo cáo cần phản biện: {report}  <!-- blind-ok: đường dẫn báo cáo bắt buộc -->
Khung tiêu chí của fleet (đọc trước): {framework}
Cách làm: đọc phần mô hình của báo cáo, tự tính lại ít nhất một con số then chốt từ nguồn gốc (BCTC, bảng giả định), truy mọi con số về nguồn.
Ràng buộc mù: KHÔNG tra giá thị trường, P/E, P/B, vốn hoá; KHÔNG mở kb/dd_price_zones.json hay bất kỳ sổ vùng giá nào; không tra giá trên mạng. Đánh giá chất lượng mô hình và dữ kiện, không đánh giá "đắt/rẻ so với thị giá".
Kết thúc bằng đúng khối VERDICT_JSON theo định dạng ở định nghĩa vai trò của bạn.
"""


def md5_of(b):
    return hashlib.md5(b).hexdigest()


def atomic_write(path, data):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def rel(p):
    p = os.path.abspath(p)
    return os.path.relpath(p, ROOT) if p.startswith(ROOT + os.sep) else p


def next_round(skdir):
    rs = [int(m.group(1)) for f in (os.listdir(skdir) if os.path.isdir(skdir) else [])
          for m in [re.fullmatch(r"r(\d+)\.json", f)] if m]
    return max(rs, default=0) + 1


def lint_brief(brief):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(brief)
        tmp = f.name
    try:
        p = subprocess.run([sys.executable, os.path.join(ROOT, "bin", "dd_blind_lint.py"), "--mode", "skeptic", tmp],
                           capture_output=True, text=True)
    finally:
        os.unlink(tmp)
    return p.returncode, (p.stdout + p.stderr).strip()


def parse_verdict(txt):
    """(obj, None) hoặc (None, lý_do_thật). Chịu trailing-comma (bài học verify_finding.sh 2026-07-11/08-10); KHÔNG suy đoán."""
    m = re.search(r"<<<VERDICT_JSON>>>(.*?)<<<END_VERDICT>>>", txt, re.S)
    if not m:
        return None, "không thấy khối <<<VERDICT_JSON>>>…<<<END_VERDICT>>> trong output"
    raw = m.group(1).strip()
    try:
        obj = json.loads(raw)
    except ValueError as e1:
        try:
            obj = json.loads(re.sub(r",(\s*[}\]])", r"\1", raw))
        except ValueError:
            return None, "VERDICT_JSON không parse được: %s" % e1
    if not isinstance(obj, dict) or obj.get("verdict") not in ENUM:
        return None, "verdict=%r ngoài enum %s" % (obj.get("verdict") if isinstance(obj, dict) else obj, ENUM)
    return obj, None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--round", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mode", choices=("FEAR_BUY", "DD_GENERAL"), default="DD_GENERAL",
                    help="chế độ skeptic, chèn dòng đầu brief 'MODE: …'. Mặc định DD_GENERAL (user duyệt 22/11/2026 23:28); FEAR_BUY CHỈ khi truyền tường minh")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    ddir = a.dir if os.path.isabs(a.dir) else os.path.join(ROOT, a.dir)
    report = a.report if os.path.isabs(a.report) else os.path.join(ROOT, a.report)
    if not os.path.isdir(ddir):
        print("LỖI: --dir không phải thư mục: %s" % ddir, file=sys.stderr)
        return 2
    try:
        rbytes = open(report, "rb").read()
    except OSError as e:
        print("LỖI: không đọc được báo cáo %s: %s" % (report, e), file=sys.stderr)
        return 2
    skdir = os.path.join(ddir, "skeptic")
    n = a.round or next_round(skdir)
    if n < 1 or os.path.exists(os.path.join(skdir, "r%d.json" % n)):
        print("LỖI: round %d không hợp lệ hoặc r%d.json đã tồn tại (không ghi đè)" % (n, n), file=sys.stderr)
        return 2
    out_json, out_raw = os.path.join(skdir, "r%d.json" % n), os.path.join(skdir, "r%d_raw.md" % n)
    brief = BRIEF.format(report=os.path.abspath(report), framework=FRAMEWORK)
    if a.mode:
        brief = "MODE: %s\n" % a.mode + brief
    rc, msg = lint_brief(brief)
    if rc != 0:
        print("LỖI: brief bị dd_blind_lint chặn (rc=%d), KHÔNG chạy skeptic:\n%s" % (rc, msg), file=sys.stderr)
        return 3
    if a.dry_run:
        print("=== BRIEF ===\n%s=== sẽ ghi ===\n%s\n%s\n[dry-run] không gọi claude." % (brief, out_json, out_raw))
        return 0
    if not os.path.isfile(AGENT_DEF):
        print("LỖI: thiếu định nghĩa agent %s" % AGENT_DEF, file=sys.stderr)
        return 2
    sysdef = re.sub(r"\A---\n.*?\n---\n", "", open(AGENT_DEF, encoding="utf-8").read(), count=1, flags=re.S)
    prompt = sysdef + "\n\n--- NHIỆM VỤ ---\n" + brief
    started = dt.datetime.now(ICT).isoformat(timespec="seconds")
    cmd = [CLAUDE, "-p", prompt, "--model", MODEL, "--permission-mode", "auto",
           "--allowedTools", "Bash Read Grep Glob", "--max-turns", "50", "--output-format", "json"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKDIR if os.path.isdir(WORKDIR) else None, timeout=TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired) as e:
        print("LỖI: gọi claude thất bại: %s" % e, file=sys.stderr)
        return 4
    txt, cost = p.stdout, None
    if p.returncode == 0:  # --output-format json: {"result": "<text>", "total_cost_usd": N}
        try:
            env_ = json.loads(p.stdout)
            if isinstance(env_, dict) and isinstance(env_.get("result"), str):
                txt, cost = env_["result"], env_.get("total_cost_usd")
        except ValueError:
            pass  # không phải JSON envelope ⇒ coi stdout là text thô như trước, cost_usd=null
    obj, why = (None, "claude rc=%d, stderr: %s" % (p.returncode, p.stderr[-300:])) if p.returncode != 0 else parse_verdict(txt)
    if obj is None:
        os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)
        lp = os.path.join(ROOT, "logs", "dd_skeptic_%s_r%d.raw" % (dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S"), n))
        atomic_write(lp, txt)
        print("LỖI: %s\nKHÔNG ghi %s. Thô lưu %s. Đuôi output:\n%s" % (why, rel(out_json), lp, txt[-400:]), file=sys.stderr)
        return 4
    atomic_write(out_raw, txt)
    rec = {"round": n, "verdict": obj["verdict"], "confidence": obj.get("confidence"),
           "report_path": rel(report), "report_md5": md5_of(rbytes), "brief_md5": md5_of(brief.encode("utf-8")),
           "model": MODEL, "cost_usd": cost, "started_at_ict": started, "summary": obj.get("summary"),
           "verdict_raw_path": rel(out_raw)}
    atomic_write(out_json, json.dumps(rec, ensure_ascii=False, indent=2) + "\n")
    print("OK r%d verdict=%s -> %s" % (n, rec["verdict"], rel(out_json)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
