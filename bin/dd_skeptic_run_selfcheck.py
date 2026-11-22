#!/usr/bin/env python3
"""Selfcheck dd_skeptic_run.py bằng claude GIẢ (DD_SKEPTIC_CLAUDE_BIN). Chạy dưới env -u TZ và TZ lạ."""
import json, os, stat, subprocess, sys, tempfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "dd_skeptic_run.py")
res = []


def chk(name, ok):
    res.append(ok)
    print(("PASS " if ok else "FAIL ") + name)


def stub(td, name, body):
    p = os.path.join(td, name)
    open(p, "w").write("#!/usr/bin/env bash\n" + body)
    os.chmod(p, os.stat(p).st_mode | stat.S_IEXEC)
    return p


def run(args, bin_, extra=None):
    env = dict(os.environ, DD_SKEPTIC_CLAUDE_BIN=bin_, DD_SKEPTIC_AGENT_DEF=AGDEF, DD_SKEPTIC_WORKDIR="/tmp")
    env.update(extra or {})
    return subprocess.run([sys.executable, RUN] + args, capture_output=True, text=True, env=env)


GOOD = 'cat <<\'X\'\n{"type":"result","result":"phan tich...\\n<<<VERDICT_JSON>>>\\n{\\"case_topic\\":\\"T\\",\\"verdict\\":\\"REFUTED\\",\\"confidence\\":\\"medium\\",\\"summary\\":\\"ket luan thu\\",}\\n<<<END_VERDICT>>>","total_cost_usd":0.12}\nX\n'
with tempfile.TemporaryDirectory() as td:
    AGDEF = os.path.join(td, "agent.md")
    open(AGDEF, "w").write("---\nname: x\n---\nVai tro skeptic.\n")
    d = os.path.join(td, "dd_T"); os.makedirs(d)
    rep = os.path.join(d, "REPORT.md"); open(rep, "w").write("# bao cao\n")
    good = stub(td, "good.sh", GOOD)
    r = run(["--dir", d, "--report", rep], good)
    j1 = os.path.join(d, "skeptic", "r1.json")
    chk("rc=0 + ghi r1.json + r1_raw.md (trailing-comma được chịu)", r.returncode == 0 and os.path.isfile(j1) and os.path.isfile(os.path.join(d, "skeptic", "r1_raw.md")))
    rec = json.load(open(j1)) if os.path.isfile(j1) else {}
    chk("verdict/round/md5 đúng", rec.get("verdict") == "REFUTED" and rec.get("round") == 1
        and rec.get("report_md5") == hashlib.md5(b"# bao cao\n").hexdigest() and len(rec.get("brief_md5", "")) == 32
        and rec.get("started_at_ict", "").endswith("+07:00") and rec.get("verdict_raw_path", "").endswith("r1_raw.md"))
    chk("cost_usd=0.12 lấy từ total_cost_usd của JSON envelope", rec.get("cost_usd") == 0.12)
    chk("không còn file .tmp_ sót", not [f for f in os.listdir(os.path.join(d, "skeptic")) if f.startswith(".tmp_")])
    r = run(["--dir", d, "--report", rep], good)
    chk("lần 2 ⇒ round tăng r2.json", r.returncode == 0 and os.path.isfile(os.path.join(d, "skeptic", "r2.json")))
    plain = stub(td, "plain.sh", "cat <<'X'\n<<<VERDICT_JSON>>>\n{\"verdict\":\"CONFIRMED\"}\n<<<END_VERDICT>>>\nX\n")
    r = run(["--dir", d, "--report", rep, "--round", "7"], plain)
    rp = json.load(open(os.path.join(d, "skeptic", "r7.json"))) if r.returncode == 0 else {}
    chk("stdout text thô (không envelope) vẫn parse, cost_usd=null", rp.get("verdict") == "CONFIRMED" and rp.get("cost_usd") is None and "cost_usd" in rp)
    os.remove(os.path.join(d, "skeptic", "r7.json")); os.remove(os.path.join(d, "skeptic", "r7_raw.md"))
    r = run(["--dir", d, "--report", rep, "--round", "1"], good)
    chk("--round trùng file có sẵn bị từ chối (rc=2), không ghi đè", r.returncode == 2)
    before = sorted(os.listdir(os.path.join(d, "skeptic")))
    for nm, body in (("noblock", "echo hi\n"), ("badjson", "echo '<<<VERDICT_JSON>>>{\"verdict\": oops}<<<END_VERDICT>>>'\n"),
                     ("badenum", "echo '<<<VERDICT_JSON>>>{\"verdict\":\"MAYBE\"}<<<END_VERDICT>>>'\n"), ("clauderc", "echo boom >&2\nexit 7\n")):
        r = run(["--dir", d, "--report", rep], stub(td, nm + ".sh", body))
        chk("%s ⇒ rc=4, không ghi file, có lý do thật" % nm, r.returncode == 4 and sorted(os.listdir(os.path.join(d, "skeptic"))) == before and "LỖI" in r.stderr)
    r = run(["--dir", d, "--report", rep, "--dry-run"], os.path.join(td, "khong_ton_tai"))
    chk("--dry-run không gọi claude (bin không tồn tại vẫn rc=0), không ghi", r.returncode == 0 and "BRIEF" in r.stdout and sorted(os.listdir(os.path.join(d, "skeptic"))) == before)
    # brief chứa giá ⇒ lint chặn
    sys.path.insert(0, HERE)
    import importlib; m = importlib.import_module("dd_skeptic_run")
    m.BRIEF = m.BRIEF + "Giá cổ phiếu hiện tại 71.000đ, P/E 8.\n"
    m.CLAUDE = os.path.join(td, "khong_ton_tai")
    rc = m.main(["--dir", d, "--report", rep])
    chk("brief chứa giá ⇒ lint chặn rc=3, không ghi", rc == 3 and sorted(os.listdir(os.path.join(d, "skeptic"))) == before)
    m.BRIEF = m.BRIEF.split("Giá cổ phiếu")[0]
    chk("--dir không tồn tại ⇒ rc=2", run(["--dir", os.path.join(td, "nope"), "--report", rep], good).returncode == 2)
print("-- %d/%d PASS" % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
