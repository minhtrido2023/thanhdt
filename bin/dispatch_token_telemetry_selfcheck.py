#!/usr/bin/env python3
"""dispatch_token_telemetry_selfcheck.py — telemetry token THEO JOB (2026-10-08, vong 2).

Kiem 3 lop:
  U. Unit bin/job_telemetry.py (parse cost-state; fallback cong usage tung message, dedupe
     message.id, turn chi luong chinh, token gom ca sidechain; tong qua nhieu session; whitelist
     key + kiem kieu; fail-open) va spend_report._top_chains (union-find theo TUNG token, noi
     resume/fallback/auto-callback/TIEP TUC vao job goc).
  I. Tich hop dispatch.sh THAT (ROOT gia, bin/ symlink file that, CLI = STUB python ghi
     transcript gia vao $CLAUDE_CONFIG_DIR/projects/*/<session-id>.jsonl):
       - field len record, $logfile GIU NGUYEN tung byte stdout cua CLI, result_summary/exit
         code khong doi (done / failed rc=3 / max-turns => exit 5 resume).
       - fail-open: transcript rac; job_telemetry.py CRASH; in rac => CHI dong whitelist len record.
       - TREO: job_telemetry.py ngu 60s => timeout cung, job van done, exit 0, xong nhanh.
       - KILL trong luc telemetry (sync): SIGTERM => record GIU done/exit_code=0, dispatch exit 0.
       - provider opencode: KHONG co field nao.
       - --bg + retry: tong 2 attempt + retry_causes=khac.
       - dispatch.sh KHONG con goi spend_report.py.
Chay: env -u TZ python3 bin/dispatch_token_telemetry_selfcheck.py   (exit 0 = PASS)
Mutation (bat buoc): MUTATE=off => _record_job_telemetry thanh no-op: ca co field PHAI FAIL.
                     MUTATE=trap => bo trap exit-code-goc: ca KILL PHAI FAIL.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

REAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REAL, "bin"))
import job_telemetry as JT  # noqa: E402
import spend_report as SR  # noqa: E402

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {detail}")


SID1 = "11111111-1111-4111-8111-111111111111"
SID2 = "22222222-2222-4222-8222-222222222222"


def _asst(mid, inp, cr, cc, out, side=False):
    return {"type": "assistant", "isSidechain": side, "timestamp": "2026-10-08T00:00:00Z",
            "message": {"id": mid, "usage": {"input_tokens": inp, "cache_read_input_tokens": cr,
                                             "cache_creation_input_tokens": cc, "output_tokens": out}}}


def _cost_state(sid, cost, models):
    return {"type": "cost-state", "sessionId": sid, "totalCostUSD": cost, "modelUsage": models}


def write_transcript(projects, sid, events, garbage=False):
    d = os.path.join(projects, "-fake-agent-dir")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, sid + ".jsonl"), "w", encoding="utf-8") as f:
        if garbage:
            f.write('{"usage": not json\n\x00\x01 rac "cost-state"\n[1,2,"usage"]\n')
        for e in events:
            f.write(json.dumps(e) + "\n")


def unit_tests(tmp):
    print("== U. unit")
    proj = os.path.join(tmp, "projects")
    # U1 cost-state uu tien, 2 model cong lai
    write_transcript(proj, SID1, [
        {"type": "user", "message": {"content": "x"}},
        _asst("m1", 3, 100, 10, 5), _asst("m1", 3, 100, 10, 5), _asst("m2", 1, 200, 0, 7),
        _asst("s1", 9, 999, 9, 9, side=True),
        _cost_state(SID1, 1.25, {"claude-opus-5-5": {"inputTokens": 4, "outputTokens": 12,
                                                     "cacheReadInputTokens": 300, "cacheCreationInputTokens": 10},
                                 "claude-haiku-4-5": {"inputTokens": 6, "outputTokens": 3,
                                                      "cacheReadInputTokens": 50, "cacheCreationInputTokens": 0}}),
    ])
    t = JT.session_telemetry(SID1, proj)
    check("U1 cost-state: cost", t.get("total_cost_usd") == 1.25, t)
    check("U1 cost-state: token = tong modelUsage",
          (t.get("input_tokens"), t.get("cache_read_tokens"), t.get("cache_creation_tokens"),
           t.get("output_tokens")) == (10, 350, 10, 15), t)
    check("U1 num_turns = 2 message id luong chinh (bo dup + sidechain)", t.get("num_turns") == 2, t)
    # U2 khong cost-state => cong message (CA sidechain cho token), khong cost; dong rac bi bo qua
    write_transcript(proj, SID2, [_asst("a", 1, 10, 2, 3), _asst("a", 1, 10, 2, 3),
                                  _asst("b", 4, 20, 0, 6), _asst("z", 50, 50, 50, 50, side=True)],
                     garbage=True)
    t2 = JT.session_telemetry(SID2, proj)
    check("U2 fallback messages: token gom sidechain, turn chi luong chinh",
          (t2.get("input_tokens"), t2.get("cache_read_tokens"), t2.get("cache_creation_tokens"),
           t2.get("output_tokens"), t2.get("num_turns")) == (55, 80, 52, 59, 2), t2)
    check("U2 fallback: KHONG co cost", "total_cost_usd" not in t2, t2)
    # U3 fail-open + kiem kieu
    check("U3 uuid sai => {}", JT.session_telemetry("../../etc/passwd", proj) == {})
    check("U3 uuid sai (job) => {}", JT.job_telemetry(["*", "../x"], proj) == {})
    miss = JT.job_telemetry(["33333333-3333-4333-8333-333333333333"], proj)
    check("U3 thieu transcript => chi session_id", miss == {"session_id": "33333333-3333-4333-8333-333333333333"}, miss)
    sid4 = "44444444-4444-4444-8444-444444444444"
    write_transcript(proj, sid4, [
        {"type": "assistant", "message": {"id": "q", "usage": {"input_tokens": -5, "output_tokens": True,
                                                              "cache_read_input_tokens": "x", "cache_creation_input_tokens": 3}}},
        _cost_state(sid4, float("nan"), {"m": {"inputTokens": 1}})])
    t4 = JT.job_telemetry([sid4], proj)
    check("U3 kieu: so am/bool/chuoi => 0, cost NaN => bo (fallback)",
          t4.get("input_tokens") == 0 and t4.get("output_tokens") == 0 and t4.get("cache_read_tokens") == 0
          and t4.get("cache_creation_tokens") == 3 and "total_cost_usd" not in t4, t4)
    # U4 tong qua session + idempotent + whitelist
    f = JT.job_telemetry([SID1, SID2, SID1], proj)
    check("U4 tong token 2 session", f.get("cache_read_tokens") == 350 + 80 and f.get("num_turns") == 4, f)
    check("U4 cost = tong phien CO cost-state (can duoi)", f.get("total_cost_usd") == 1.25, f)
    check("U4 session_id = ca 2, dedupe, dung thu tu", f.get("session_id") == f"{SID1},{SID2}", f)
    check("U4 idempotent", JT.job_telemetry([SID1, SID2], proj) == f)
    check("U4 CHI key whitelist", set(f) <= set(JT.OUT_KEYS), sorted(f))
    # U5 CLI: in key=value, sai so doi so => rong, rc=0
    env = {**os.environ, "CLAUDE_CONFIG_DIR": tmp}
    jt = os.path.join(REAL, "bin", "job_telemetry.py")
    r = subprocess.run([sys.executable, jt, f"{SID1},{SID2}"], capture_output=True, text=True, env=env)
    kv = dict(line.split("=", 1) for line in r.stdout.splitlines())
    check("U5 CLI ra field, rc=0", r.returncode == 0 and kv.get("total_cost_usd") == "1.25"
          and kv.get("num_turns") == "4", r)
    r = subprocess.run([sys.executable, jt], capture_output=True, text=True, env=env)
    check("U5 CLI thieu doi so => rong, rc=0", r.returncode == 0 and r.stdout == "", r)
    # U6 chuoi: union-find theo TUNG token + noi job goc
    by_id = {"J0": {"job_id": "J0", "chain_tokens": "fix/abc-20261008", "prompt_summary": "goc"}}
    jobs = [
        {"job_id": "A1", "to": "Taylor", "prompt_summary": "lam viec o wt-pfm-1008", "total_cost_usd": "1"},
        {"job_id": "A2", "to": "Taylor", "chain_tokens": "feat/adjfactor-price-field-mismatch-20261008,wt-pfm-1008",
         "total_cost_usd": "2"},
        {"job_id": "A3", "to": "Taylor", "chain_tokens": "feat/adjfactor-price-field-mismatch-20261008",
         "total_cost_usd": "0.5"},
        {"job_id": "R1", "to": "Taylor", "prompt_summary": "[RESUME sau usage-limit #1, job gốc=J0] Task", "total_cost_usd": "1"},
        {"job_id": "C1", "to": "Mike", "prompt_summary": "[AUTO-CALLBACK job=J0] Taylor HOÀN THÀNH", "input_tokens": "5"},
        {"job_id": "T1", "to": "Taylor", "prompt_summary": "TIẾP TỤC job A3 (timeout) lam not", "total_cost_usd": "0.25"},
        {"job_id": "X1", "to": "Winston", "prompt_summary": "re", "input_tokens": "999"},
    ]
    ranked, n = SR._top_chains(jobs, by_id)
    top = dict(ranked)
    pfm = top.get("feat/adjfactor-price-field-mismatch-20261008") or top.get("wt-pfm-1008")
    check("U6 3 chuoi (pfm gop 4 job qua token chung + TIEP TUC; J0; re)", n == 3, [(k, c["jobs"]) for k, c in ranked])
    check("U6 chuoi pfm: 4 job, cost 3.75, dung dau", pfm and pfm["jobs"] == 4 and pfm["cost"] == 3.75
          and ranked[0][1] is pfm, ranked)
    check("U6 resume + auto-callback -> chuoi job goc", top.get("fix/abc-20261008", {}).get("jobs") == 2, ranked)
    check("U6 khong token -> 40 ky tu dau", top.get("re", {}).get("tokens") == 999, ranked)
    check("U6 nguyen nhan resume", (SR._resume_cause("[RESUME sau max-turns #1, job gốc=X] a"),
                                    SR._resume_cause("TIẾP TỤC job X (timeout)"),
                                    SR._resume_cause("[FALLBACK provider->claude sau usage-limit, job gốc=X] a"))
          == ("max_turns", "tiep_tuc_timeout", "fallback_provider"))

STUB = r'''#!/usr/bin/env python3
import json, os, sys
sb = os.environ["TT_SB"]
sid = ""
for i, a in enumerate(sys.argv):
    if a == "--session-id" and i + 1 < len(sys.argv):
        sid = sys.argv[i + 1]
with open(os.path.join(sb, "calls.txt"), "a") as f:
    f.write(sid + "\n")
n = sum(1 for _ in open(os.path.join(sb, "calls.txt")))
mode = open(os.path.join(sb, "mode")).read().strip()
proj = os.path.join(os.environ["CLAUDE_CONFIG_DIR"], "projects", "-fake-agent-dir")
os.makedirs(proj, exist_ok=True)
def asst(mid, cr):
    return {"type": "assistant", "message": {"id": mid, "usage": {"input_tokens": 1,
            "cache_read_input_tokens": cr, "cache_creation_input_tokens": 2, "output_tokens": 3}}}
if sid:
    with open(os.path.join(proj, sid + ".jsonl"), "w") as f:
        if mode == "garbage":
            f.write('{"usage": rac\n"cost-state" {{{\n')
        else:
            for k in range(3):
                f.write(json.dumps(asst(f"m{n}-{k}", 100)) + "\n")
            if mode != "nocost":
                f.write(json.dumps({"type": "cost-state", "totalCostUSD": 0.5 if n == 1 else 0.25,
                    "modelUsage": {"claude-sonnet-5-5": {"inputTokens": 3, "outputTokens": 9,
                    "cacheReadInputTokens": 300, "cacheCreationInputTokens": 6}}}) + "\n")
if mode == "maxturns":
    sys.stdout.write("Error: Reached max turns (50)\n"); sys.exit(1)
if mode == "fail3":
    sys.stdout.write("STUB-FAIL dong 1\n"); sys.exit(3)
if mode == "retry" and n == 1:
    sys.stdout.write("STUB attempt 1 loi\n"); sys.exit(1)
sys.stdout.write("STUB-OK dong 1\tket luan: telemetry test OK\n")
sys.exit(0)
'''


class Sandbox:
    def __init__(self, mutate=False):
        self.sb = tempfile.mkdtemp(prefix="tt-selfcheck-")
        self.mk = os.path.join(self.sb, "mike")
        for d in ("bin", "kb", "bus/jobs", "logs", "state/circuit", "agents/Taylor"):
            os.makedirs(os.path.join(self.mk, d), exist_ok=True)
        for f in os.listdir(os.path.join(REAL, "bin")):
            src = os.path.join(REAL, "bin", f)
            if os.path.isfile(src):
                os.symlink(src, os.path.join(self.mk, "bin", f))
        for f in ("discord_channels.json", "cli_providers.json"):
            shutil.copy(os.path.join(REAL, "kb", f), os.path.join(self.mk, "kb", f))
        open(os.path.join(self.mk, "agents/Taylor/CLAUDE.md"), "w").write("# Taylor test\n")
        for name, body in (("notify.sh", "exit 0"), ("notify_thread.sh", "exit 0"),
                           ("consolidate.sh", "exit 0"), ("append_event.sh", "exit 0"),
                           ("discord_channel.sh", "exit 1")):
            self.stub(name, "#!/usr/bin/env bash\n" + body + "\n")
        if mutate:
            real = open(os.path.join(REAL, "bin", "dispatch.sh"), encoding="utf-8").read()
            if mutate == "off":
                mut = real.replace('  [ -n "${_TELE_SIDS:-}" ] || return 0\n', "  return 0\n", 1)
            else:  # trap
                mut = real.replace("""  [ -n "${1:-}" ] && trap "rm -f '$_tf'; exit $1" TERM INT HUP\n""", "", 1)
            assert mut != real, "mutation khong ap duoc"
            self.stub("dispatch.sh", mut)
        self.cfg = os.path.join(self.sb, "claude_cfg")
        os.makedirs(self.cfg)
        self.cli = os.path.join(self.sb, "cli_stub.py")
        open(self.cli, "w").write(STUB)
        os.chmod(self.cli, 0o755)

    def stub(self, name, body):  # rm symlink TRUOC — ghi qua symlink se cat file that
        p = os.path.join(self.mk, "bin", name)
        os.remove(p) if os.path.lexists(p) else None
        open(p, "w").write(body)
        os.chmod(p, 0o755)

    def _env(self, mode):
        open(os.path.join(self.sb, "mode"), "w").write(mode)
        p = os.path.join(self.sb, "calls.txt")
        os.remove(p) if os.path.exists(p) else None
        env = {k: v for k, v in os.environ.items() if k not in ("DISCORD_THREAD_ID", "TZ", "JOB_ID")}
        env.update(DISPATCH_CGROUP_DETACH="0", DISPATCH_CLAUDE_BIN=self.cli, DISPATCH_OPENCODE_BIN=self.cli,
                   DISPATCH_FROM="Mike", CLAUDE_CONFIG_DIR=self.cfg, TT_SB=self.sb)
        return env

    def cmd(self, *args):
        return ["bash", os.path.join(self.mk, "bin", "dispatch.sh"), "Taylor", "viec test", *args]

    def run(self, mode, *args, extra_env=None):
        env = self._env(mode)
        env.update(extra_env or {})
        return subprocess.run(self.cmd(*args), cwd=self.mk, env=env, capture_output=True, text=True, timeout=300)

    def last_job(self):
        jd = os.path.join(self.mk, "bus", "jobs")
        recs = []
        for f in os.listdir(jd):
            if f.endswith(".json"):
                recs.append(json.load(open(os.path.join(jd, f))))
        recs.sort(key=lambda r: os.path.getmtime(os.path.join(jd, r["job_id"] + ".json")))
        return recs[-1] if recs else {}

    def clear_jobs(self):
        jd = os.path.join(self.mk, "bus", "jobs")
        for f in os.listdir(jd):
            os.remove(os.path.join(jd, f))
        time.sleep(1.1)  # job_id theo giay — tranh trung ten giua cac ca


def integration_tests(mutate):
    print("== I. tich hop dispatch.sh" + (f" [MUTATION {mutate}]" if mutate else ""))
    s = Sandbox(mutate)
    try:
        # I1 sync done + cost-state
        r = s.run("ok")
        j = s.last_job()
        log = open(j.get("logfile", "/dev/null"), "rb").read() if j.get("logfile") else b""
        check("I1 exit 0 + status done", r.returncode == 0 and j.get("status") == "done", (r.returncode, r.stderr[-400:]))
        check("I1 $logfile = stdout CLI tung byte", log == b"STUB-OK dong 1\tket luan: telemetry test OK\n", log)
        check("I1 result_summary khong doi", j.get("result_summary") == "STUB-OK dong 1 ket luan: telemetry test OK ",
              repr(j.get("result_summary")))
        check("I1 du 7 field", all(k in j for k in ("num_turns", "total_cost_usd", "input_tokens", "cache_read_tokens",
                                                    "cache_creation_tokens", "output_tokens", "session_id")), sorted(j))
        check("I1 gia tri", (j.get("total_cost_usd"), j.get("cache_read_tokens"), j.get("num_turns")) == ("0.5", "300", "3"),
              {k: j.get(k) for k in ("total_cost_usd", "cache_read_tokens", "num_turns")})
        calls = open(os.path.join(s.sb, "calls.txt")).read().split()
        check("I1 session_id tren record = --session-id da truyen", calls == [j.get("session_id")], (calls, j.get("session_id")))
        s.clear_jobs()
        # I2 sync fail rc=3: exit code + status giu nguyen, telemetry van ghi (khong cost)
        r = s.run("fail3")
        j = s.last_job()
        check("I2 rc=3 giu nguyen", r.returncode == 3 and j.get("status") == "failed" and j.get("exit_code") == "3",
              (r.returncode, j.get("status"), j.get("exit_code")))
        check("I2 telemetry co tren job fail", j.get("cache_read_tokens") == "300", j.get("cache_read_tokens"))
        s.clear_jobs()
        # I3 max-turns detection van chay (log khong doi) => exit 5
        r = s.run("maxturns")
        j = s.last_job()
        check("I3 max-turns van duoc nhan ra (exit 5)", r.returncode == 5, (r.returncode, r.stderr[-300:]))
        check("I3 telemetry co tren job max-turns", j.get("num_turns") == "3", j.get("num_turns"))
        s.clear_jobs()
        if not mutate:
            # I4 transcript rac => job van done, khong field token
            r = s.run("garbage")
            j = s.last_job()
            check("I4 transcript rac: van done rc=0", r.returncode == 0 and j.get("status") == "done", r.stderr[-300:])
            check("I4 transcript rac: chi session_id, khong token",
                  j.get("session_id") and not any(k in j for k in SR.TELEMETRY_INT_FIELDS), sorted(j))
            s.clear_jobs()
            # I5 job_telemetry.py CRASH / in rac => job van done rc=0; CHI dong whitelist len record
            for label, body in (("crash", "#!/usr/bin/env python3\nraise SystemExit(7)\n"),
                                ("rac", "#!/usr/bin/env python3\nprint('khongphaikv')\nprint('status=failed')\n"
                                        "print('exit_code=9')\nprint('num_turns=abc')\nprint('num_turns=-1')\n"
                                        "print('session_id=../../etc')\nprint('total_cost_usd=1e9')\n"
                                        "print('foo=1')\nprint('num_turns=7')\n")):
                s.stub("job_telemetry.py", body)
                r = s.run("ok")
                j = s.last_job()
                check(f"I5 job_telemetry {label}: van done rc=0, exit_code=0",
                      r.returncode == 0 and j.get("status") == "done" and j.get("exit_code") == "0",
                      (r.returncode, j.get("status"), j.get("exit_code"), r.stderr[-300:]))
                if label == "rac":
                    check("I5 rac: chi num_turns=7 lot qua whitelist",
                          j.get("num_turns") == "7" and "foo" not in j and "total_cost_usd" not in j
                          and "session_id" not in j, {k: j.get(k) for k in ("num_turns", "foo", "session_id")})
                s.clear_jobs()
            # I8 TREO: job_telemetry.py ngu 60s => timeout cung (JOB_TELEMETRY_TIMEOUT=2), job done, nhanh
            s.stub("job_telemetry.py", "#!/usr/bin/env python3\nimport time\ntime.sleep(60)\nprint('num_turns=1')\n")
            t0 = time.time()
            r = s.run("ok", extra_env={"JOB_TELEMETRY_TIMEOUT": "2"})
            dt = time.time() - t0
            j = s.last_job()
            check("I8 telemetry treo: done, exit 0, khong field, <30s",
                  r.returncode == 0 and j.get("status") == "done" and j.get("exit_code") == "0"
                  and "num_turns" not in j and dt < 30, (r.returncode, j.get("status"), round(dt, 1)))
            s.clear_jobs()
            os.remove(os.path.join(s.mk, "bin", "job_telemetry.py"))
            os.symlink(os.path.join(REAL, "bin", "job_telemetry.py"), os.path.join(s.mk, "bin", "job_telemetry.py"))
            # I6 opencode: khong field nao, khong crash
            r = s.run("ok", "--provider", "opencode", "--model", "opencode/deepseek-v4-flash-free")
            j = s.last_job()
            check("I6 opencode: done, KHONG co telemetry",
                  r.returncode == 0 and j.get("status") == "done"
                  and not any(k in j for k in SR.TELEMETRY_INT_FIELDS + ("session_id", "total_cost_usd")),
                  (r.returncode, sorted(j), r.stderr[-300:]))
            s.clear_jobs()
        if mutate in (None, "trap"):
            # I9 KILL trong cua so telemetry (sync): SIGTERM => record giu done/0, dispatch exit 0
            mark = os.path.join(s.sb, "tele_started")
            s.stub("job_telemetry.py", "#!/usr/bin/env python3\nimport time\nopen(%r, 'w').close()\n"
                                       "time.sleep(30)\nprint('num_turns=1')\n" % mark)
            p = subprocess.Popen(s.cmd(), cwd=s.mk, env=s._env("ok"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            t0 = time.time()
            while not os.path.exists(mark) and time.time() - t0 < 60 and p.poll() is None:
                time.sleep(0.1)
            started = os.path.exists(mark)
            p.terminate()
            try:
                rc = p.wait(timeout=20)
            except subprocess.TimeoutExpired:
                p.kill()
                rc = "hang"
            j = s.last_job()
            check("I9 kill trong telemetry: telemetry da chay", started)
            check("I9 kill trong telemetry: record GIU done/exit_code=0", j.get("status") == "done"
                  and j.get("exit_code") == "0", (j.get("status"), j.get("exit_code"), j.get("result_summary")))
            check("I9 kill trong telemetry: dispatch exit GOC 0 (khong 143), nhanh",
                  rc == 0 and time.time() - t0 < 25, (rc, round(time.time() - t0, 1)))
            os.remove(mark) if os.path.exists(mark) else None
            s.clear_jobs()
            os.remove(os.path.join(s.mk, "bin", "job_telemetry.py"))
            os.symlink(os.path.join(REAL, "bin", "job_telemetry.py"), os.path.join(s.mk, "bin", "job_telemetry.py"))
            if mutate == "trap":
                return
        # I7 --bg + retry: cong don 2 attempt + retry_causes
        r = s.run("retry", "--bg", "--retries", "1")
        deadline = time.time() + 120
        j = {}
        while time.time() < deadline:
            j = s.last_job()
            if j.get("status") in ("done", "failed", "timeout"):
                break
            time.sleep(1)
        check("I7 bg done sau retry", j.get("status") == "done" and j.get("attempt") == "2", (j.get("status"), j.get("attempt")))
        check("I7 retry_causes=khac", j.get("retry_causes") == "khac", j.get("retry_causes"))
        calls = open(os.path.join(s.sb, "calls.txt")).read().split()
        check("I7 tong cost 0.5+0.25 & session_id = 2 uuid da truyen",
              j.get("total_cost_usd") == "0.75" and str(j.get("session_id", "")).split(",") == calls
              and len(calls) == 2 and j.get("num_turns") == "6",
              {k: j.get(k) for k in ("total_cost_usd", "session_id", "num_turns")})
        check("I7 khong con key ngoai whitelist", "telemetry_sessions" not in j and "telemetry_src" not in j, sorted(j))
        log = open(j.get("logfile", "/dev/null"), "rb").read() if j.get("logfile") else b""
        check("I7 $logfile bat dau bang stdout CLI attempt cuoi",
              log.startswith(b"STUB-OK dong 1\tket luan: telemetry test OK\n"), log[:120])
    finally:
        shutil.rmtree(s.sb, ignore_errors=True)


def main():
    mutate = os.environ.get("MUTATE") or None
    if mutate == "1":
        mutate = "off"
    src = open(os.path.join(REAL, "bin", "dispatch.sh"), encoding="utf-8").read()
    if not mutate:
        print("== S. tinh")
        import re
        calls = [ln for ln in src.splitlines() if re.search(r"spend_report\.py", ln) and not ln.lstrip().startswith("#")]
        check("S1 dispatch.sh KHONG con goi spend_report.py", not calls, calls)
    if not mutate:
        tmp = tempfile.mkdtemp(prefix="tt-unit-")
        try:
            unit_tests(tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    integration_tests(mutate)
    print()
    if mutate:
        ok = FAIL > 0
        print(("✅ MUTATION: %d ca FAIL nhu mong doi (test that su canh telemetry)" if ok
               else "❌ MUTATION: KHONG ca nao FAIL — test khong canh gi ca") % FAIL)
        return 0 if ok else 1
    print(("PASS — %d/%d" if FAIL == 0 else "FAIL — %d/%d") % (PASS if FAIL == 0 else FAIL, PASS + FAIL))
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
