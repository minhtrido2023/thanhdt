#!/usr/bin/env python3
"""Selfcheck cho cầu chì vòng polish (bin/dispatch_round_cap.py + wiring exit 7 trong dispatch.sh).

Sandbox HOÀN TOÀN: bus job GIẢ trong tmpdir (DISPATCH_LOOP_HINT_JOBS_DIR), audit log giả
(MIKE_DISPATCH_ROUND_CAP_LOG). KHÔNG đọc/ghi bus/jobs thật, KHÔNG gọi claude: ca end-to-end gọi
dispatch.sh với agent KHÔNG TỒN TẠI (`RcapProbe`) ⇒ cầu chì đúng thì exit 7; cầu chì hỏng thì
dispatch.sh dừng ở kiểm tra agent-dir (exit 1) — không bao giờ tới bước tạo job/gọi CLI.

  python3 bin/dispatch_round_cap_selfcheck.py              # 1 môi trường
  python3 bin/dispatch_round_cap_selfcheck.py --all-tz     # + env -u TZ, TZ=America/New_York
  python3 bin/dispatch_round_cap_selfcheck.py --mutations  # tự bắn đột biến, mỗi cái phải bị giết
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
AGENT = "RcapProbe"
BR = "feat/roundcap-probe-20261005"


def utc_id(agent, age_s):
    t = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=age_s)
    return f"{agent}_{t.strftime('%Y%m%d_%H%M%S')}"


def seed(d, age_s, summary, to=AGENT, status="done", chain_tokens=None):
    jid = utc_id(to, age_s)
    rec = {"job_id": jid, "to": to, "status": status, "prompt_summary": summary,
           "started_at": str(int(time.time()) - age_s)}
    if chain_tokens is not None:
        rec["chain_tokens"] = chain_tokens
    p = Path(d) / f"{jid}.json"
    p.write_text(json.dumps(rec))
    os.utime(p, (time.time() - age_s, time.time() - age_s))
    return jid


def seed_rounds(d, n, token=BR, to=AGENT, start_age=4 * 3600, gap=1800):
    return [seed(d, start_age - i * gap, f"Vòng {i + 1} branch {token}", to=to) for i in range(n)]


def suite(root):
    """Chạy toàn bộ ca trên cây `root`; trả list tên ca FAIL."""
    root = Path(root)
    cap = root / "bin" / "dispatch_round_cap.py"
    disp = root / "bin" / "dispatch.sh"
    fails = []
    base_env = {k: v for k, v in os.environ.items()
                if k not in ("JOB_ID", "DISPATCH_ROUND_CAP_OVERRIDE", "DISPATCH_ROUND_CAP_REASON",
                             "DISPATCH_ROUND_CAP_PRIOR", "DISPATCH_FROM", "DISCORD_THREAD_ID")}

    def check(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
        if not cond:
            fails.append(name)

    def env_for(jobs, log, **extra):
        e = dict(base_env, DISPATCH_LOOP_HINT_JOBS_DIR=str(jobs), MIKE_DISPATCH_ROUND_CAP_LOG=str(log))
        e.update(extra)
        return e

    def run_cap(prompt, jobs, log, to=AGENT, **extra):
        r = subprocess.run([sys.executable, str(cap), "check", "--to", to], input=prompt,
                           capture_output=True, text=True, env=env_for(jobs, log, **extra), timeout=60)
        return r.returncode, r.stdout, r.stderr

    def run_disp(prompt, jobs, log, **extra):
        r = subprocess.run(["bash", str(disp), AGENT, prompt], capture_output=True, text=True,
                           env=env_for(jobs, log, DISPATCH_CLAUDE_BIN="/bin/false", **extra), timeout=120)
        return r.returncode, r.stdout, r.stderr

    def audit(log):
        return Path(log).read_text() if Path(log).exists() else ""

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # 1-3. Vòng 1, 2, 3 đi qua (0/1/2 vòng trước)
        for n in range(3):
            j = td / f"pass{n}"
            j.mkdir()
            seed_rounds(j, n)
            rc, out, err = run_cap(f"Vòng {n + 1} branch {BR}", j, td / f"pass{n}.log")
            check(f"round{n + 1}_passes", rc == 0 and "ERROR" not in err, f"rc={rc} err={err[-200:]}")
            if n == 0:
                check("chain_tokens_emitted", out.split("\t")[0] == BR, repr(out))

        # 4. Vòng 4 bị chặn (3 vòng trước) + audit + liệt kê job
        j4 = td / "block"
        j4.mkdir()
        ids = seed_rounds(j4, 3)
        log4 = td / "block.log"
        rc, out, err = run_cap(f"Vòng 4 branch {BR}", j4, log4)
        check("round4_blocked_rc7", rc == 7, f"rc={rc}")
        check("round4_msg_lists_prior_jobs", all(i in err for i in ids) and "CHẾ ĐỘ B" in err
              and "DISPATCH_ROUND_CAP_OVERRIDE=1" in err, err[-400:])
        check("round4_audit_block", "\tblock\t" in audit(log4) and f"chain={BR}" in audit(log4), audit(log4))
        check("round4_stdout_note", out.strip().endswith(f"block:{BR}:4"), repr(out))

        # 5. Override env (phiên tương tác — không có JOB_ID) ⇒ qua + audit
        log5 = td / "ov.log"
        rc, out, err = run_cap(f"Vòng 4 branch {BR}", j4, log5, DISPATCH_ROUND_CAP_OVERRIDE="1",
                               DISPATCH_ROUND_CAP_REASON="user duyệt 10:00")
        check("override_passes", rc == 0, f"rc={rc} err={err[-200:]}")
        check("override_audited", "\toverride\t" in audit(log5) and "user duyệt 10:00" in audit(log5), audit(log5))
        check("override_job_field", f"override:{BR}:4" in out, repr(out))

        # 6. Override từ agent headless (JOB_ID kế thừa) ⇒ TỪ CHỐI, vẫn chặn
        log6 = td / "ovr.log"
        rc, out, err = run_cap(f"Vòng 4 branch {BR}", j4, log6, DISPATCH_ROUND_CAP_OVERRIDE="1",
                               JOB_ID="Taylor_20261005_000000")
        check("override_refused_headless", rc == 7 and "TỪ CHỐI" in err
              and "\toverride_refused\t" in audit(log6), f"rc={rc}")

        # 7. Chuỗi khác KHÔNG bị ảnh hưởng; agent khác cùng nhánh KHÔNG bị ảnh hưởng
        rc, _, _ = run_cap("Vòng 1 branch fix/khac-hoan-toan-20261005", j4, td / "o.log")
        check("other_chain_unaffected", rc == 0, f"rc={rc}")
        rc, _, _ = run_cap(f"retro nhắc branch {BR}", j4, td / "o.log", to="Wags")
        check("other_agent_unaffected", rc == 0, f"rc={rc}")

        # 8. [RESUME / [FALLBACK (tự sinh, tiếp nối vòng đã nhận) ⇒ miễn
        rc, _, _ = run_cap(f"[RESUME sau usage-limit #1, job gốc=X] Vòng 4 branch {BR}", j4, td / "o.log")
        check("resume_exempt", rc == 0, f"rc={rc}")
        rc, _, _ = run_cap(f"[FALLBACK provider->claude sau usage-limit, job gốc=X] branch {BR}", j4, td / "o.log")
        check("fallback_exempt", rc == 0, f"rc={rc}")

        # 9. Bản đúp <5 phút của vòng 3 ⇒ vẫn là vòng 3, không chặn
        j9 = td / "dup"
        j9.mkdir()
        seed_rounds(j9, 2, start_age=4 * 3600)
        seed(j9, 60, f"Vòng 3 branch {BR}")
        rc, _, err = run_cap(f"Vòng 3 (gửi lại) branch {BR}", j9, td / "o.log")
        check("dup_within_5min_not_new_round", rc == 0, f"rc={rc} {err[-200:]}")

        # 10. chain_tokens (prompt ĐẦY ĐỦ) được đếm dù prompt_summary 160 byte KHÔNG chứa token
        #     — đúng ca broker-primary r1 (Taylor_20261003_162814).
        j10 = td / "ct"
        j10.mkdir()
        seed(j10, 5 * 3600, "User DUYET: DOI THU TU UU TIEN corp-action (token bị cắt khỏi summary)",
             chain_tokens=BR)
        seed_rounds(j10, 2, start_age=3 * 3600)
        rc, _, _ = run_cap(f"VONG 4 branch {BR}", j10, td / "o.log")
        check("chain_tokens_field_counted", rc == 7, f"rc={rc}")

        # 11. job cancelled / >24h không tính
        j11 = td / "old"
        j11.mkdir()
        seed(j11, 30 * 3600, f"branch {BR}")
        seed(j11, 28 * 3600, f"branch {BR}")
        seed(j11, 3 * 3600, f"branch {BR}", status="cancelled")
        seed(j11, 2 * 3600, f"branch {BR}")
        rc, _, _ = run_cap(f"branch {BR}", j11, td / "o.log")
        check("old_and_cancelled_ignored", rc == 0, f"rc={rc}")

        # 12. Không có token nhánh ⇒ qua, im lặng
        rc, out, err = run_cap("Query PE hiện tại của VNM", j4, td / "o.log")
        check("no_token_silent", rc == 0 and err == "" and out == "\t\n", repr((out, err)))

        # 13. FAIL-OPEN: thư mục job không đọc được ⇒ rc 0 + CẢNH BÁO (không im lặng)
        rc, out, err = run_cap(f"Vòng 4 branch {BR}", td / "khong-ton-tai", td / "fo.log")
        check("unreadable_records_fail_open", rc == 0 and "WARN round-cap" in err and "FAIL-OPEN" in err
              and "failopen" in out,
              f"rc={rc} err={err[-200:]}")

        # 14. Ngưỡng đọc từ env (DISPATCH_ROUND_CAP_PRIOR=4 ⇒ vòng 4 qua)
        rc, _, _ = run_cap(f"Vòng 4 branch {BR}", j4, td / "o.log", DISPATCH_ROUND_CAP_PRIOR="4")
        check("threshold_env_knob", rc == 0, f"rc={rc}")

        # --- END-TO-END qua dispatch.sh thật (agent không tồn tại ⇒ không thể có side-effect) ---
        rc, out, err = run_disp(f"Vòng 4 branch {BR}", j4, td / "e2e.log")
        check("e2e_dispatch_exit7", rc == 7 and "CHẶN" in err, f"rc={rc} err={err[-300:]}")
        rc, out, err = run_disp(f"Vòng 4 branch {BR}", j4, td / "e2e_ov.log", DISPATCH_ROUND_CAP_OVERRIDE="1")
        check("e2e_override_passes_cap", rc == 1 and "not found" in err and "CHẶN" not in err,
              f"rc={rc} err={err[-300:]}")
        rc, out, err = run_disp(f"Vòng 1 branch {BR}", td / "khong-ton-tai", td / "e2e_fo.log")
        check("e2e_fail_open", rc == 1 and "not found" in err and "FAIL-OPEN" in err, f"rc={rc} err={err[-300:]}")
        # script cầu chì CRASH (rc≠0, ≠7) ⇒ dispatch.sh fail-open, không chặn. Giả crash bằng một
        # `python3` bọc trong PATH chỉ hỏng khi gọi dispatch_round_cap.py.
        fake = td / "fakebin"
        fake.mkdir()
        real_py = shutil.which("python3")
        (fake / "python3").write_text("#!/bin/sh\ncase \"$*\" in *dispatch_round_cap.py*) exit 3 ;; esac\n"
                                      f'exec "{real_py}" "$@"\n')
        os.chmod(fake / "python3", 0o755)
        rc, out, err = run_disp(f"Vòng 4 branch {BR}", j4, td / "e2e_cr.log",
                                PATH=f"{fake}:{os.environ.get('PATH', '')}")
        check("e2e_cap_crash_fail_open", rc == 1 and "not found" in err and "FAIL-OPEN" in err,
              f"rc={rc} err={err[-300:]}")
        rc, out, err = run_disp(f"Vòng 2 branch {BR}", td / "pass1", td / "e2e_p.log")
        check("e2e_round2_passes_cap", rc == 1 and "not found" in err, f"rc={rc} err={err[-300:]}")

        # --- E2E ĐẦY ĐỦ trong ROOT giả (khuôn dispatch_discord_topic_selfcheck.sh): bin/ symlink,
        # notify/append_event/consolidate là stub, claude là stub ⇒ dispatch chạy hết tới khi tạo
        # job record; kiểm field chain_tokens/round_cap ghi đúng và override KHÔNG rò xuống agent.
        sb = td / "sb" / "mike"
        for sub in ("bin", "kb", "bus/jobs", "logs", "state/circuit", f"agents/{AGENT}"):
            (sb / sub).mkdir(parents=True, exist_ok=True)
        for f in (root / "bin").iterdir():
            if f.is_file():
                (sb / "bin" / f.name).symlink_to(f.resolve())
        for k in ("cli_providers.json", "discord_channels.json"):
            shutil.copy(root / "kb" / k, sb / "kb" / k)
        for n in ("notify.sh", "notify_thread.sh", "append_event.sh", "consolidate.sh"):
            (sb / "bin" / n).unlink()               # gỡ symlink TRƯỚC, không ghi xuyên qua nó
            (sb / "bin" / n).write_text("#!/usr/bin/env bash\nexit 0\n")
            os.chmod(sb / "bin" / n, 0o755)
            assert not (sb / "bin" / n).is_symlink()
        envdump = td / "child.env"
        stub = td / "claude_stub.sh"
        stub.write_text(f"#!/usr/bin/env bash\necho \"OV=${{DISPATCH_ROUND_CAP_OVERRIDE-<UNSET>}}\" > {envdump}\n"
                        "echo stub-ok\nexit 0\n")
        os.chmod(stub, 0o755)
        seeded = set()
        for jid in seed_rounds(sb / "bus" / "jobs", 3):
            seeded.add(jid + ".json")

        def full_disp(prompt, **extra):
            e = {k: v for k, v in base_env.items() if k != "DISPATCH_LOOP_HINT_JOBS_DIR"}
            e.update(DISPATCH_CLAUDE_BIN=str(stub), MIKE_DISPATCH_ROUND_CAP_LOG=str(td / "full.log"), **extra)
            before = set(os.listdir(sb / "bus" / "jobs"))
            r = subprocess.run(["bash", str(sb / "bin" / "dispatch.sh"), AGENT, prompt, "--timeout", "60"],
                               capture_output=True, text=True, env=e, timeout=300)
            new = sorted(set(os.listdir(sb / "bus" / "jobs")) - before)
            rec = json.loads((sb / "bus" / "jobs" / new[-1]).read_text()) if new else {}
            return r.returncode, rec, r.stderr

        rc, rec, err = full_disp(f"Vòng 4 branch {BR}", DISPATCH_ROUND_CAP_OVERRIDE="1")
        check("full_override_record_fields", rc == 0 and rec.get("chain_tokens") == BR
              and rec.get("round_cap") == f"override:{BR}:4", f"rc={rc} rec={rec} err={err[-300:]}")
        check("full_override_not_leaked_to_agent",
              envdump.exists() and envdump.read_text().strip() == "OV=<UNSET>",
              envdump.read_text() if envdump.exists() else "no dump")
        rc, rec, err = full_disp(f"Vòng 5 branch {BR}")
        check("full_round5_blocked_no_record", rc == 7 and rec == {}, f"rc={rc} rec={rec}")

    # --- wiring tĩnh: override không rò xuống agent con, field job được ghi ---
    sh = disp.read_text()
    i_call = sh.find('bin/dispatch_round_cap.py" check')
    i_unset = sh.find("unset DISPATCH_ROUND_CAP_OVERRIDE")
    i_cli = sh.find('CLI_BIN="$("$ROOT/bin/cli_provider.sh" bin')
    check("wiring_unset_after_call_before_cli", 0 < i_call < i_unset < i_cli, f"{i_call} {i_unset} {i_cli}")
    check("wiring_job_fields", 'chain_tokens="$_chain_tokens" round_cap="$_round_cap_note"' in sh)
    check("wiring_exit7_documented", "7=CẦU CHÌ VÒNG POLISH" in sh)
    return fails


MUTATIONS = [
    # (tên, file, chuỗi gốc, chuỗi thay)
    ("go_check_exit7", "bin/dispatch.sh",
     'if [ "$_rcap_rc" -eq 7 ]; then\n  exit 7', 'if [ "$_rcap_rc" -eq 7 ]; then\n  :'),
    ("doi_nguong_3_thanh_4", "bin/dispatch_round_cap.py",
     '"DISPATCH_ROUND_CAP_PRIOR", "3"', '"DISPATCH_ROUND_CAP_PRIOR", "4"'),
    ("bo_override", "bin/dispatch_round_cap.py",
     'if ov == "1" and not inherited_job:', 'if False:'),
    ("override_khong_chan_headless", "bin/dispatch_round_cap.py",
     'if ov == "1" and not inherited_job:', 'if ov == "1":'),
    ("nuot_fail_open_thanh_chan", "bin/dispatch_round_cap.py",
     '        _audit("failopen", a.to, frm, "", [], reason=f"{type(e).__name__}: {e}")\n        return 0',
     '        _audit("failopen", a.to, frm, "", [], reason=f"{type(e).__name__}: {e}")\n        return BLOCK_RC'),
    ("fail_open_im_lang", "bin/dispatch_round_cap.py",
     'print(f"WARN round-cap: không đếm được vòng', 'print(f"round-cap: không đếm được vòng'),
    ("bash_moi_rc_khac_0_la_chan", "bin/dispatch.sh",
     'if [ "$_rcap_rc" -eq 7 ]; then', 'if [ "$_rcap_rc" -ne 0 ]; then'),
    ("bo_mien_resume", "bin/dispatch_round_cap.py",
     '_AUTO_PREFIX = ("[RESUME", "[FALLBACK")', '_AUTO_PREFIX = ("[KHONG-BAO-GIO",)'),
    ("bo_rang_buoc_agent", "bin/dispatch_loop_hint.py",
     'if agent and d.get("to") != agent:', 'if False:'),
    ("bo_chain_tokens_field", "bin/dispatch_loop_hint.py",
     'if token in [x for x in str(ct).split(",") if x]:', 'if False:'),
    ("ban_dup_tinh_vong_moi", "bin/dispatch_round_cap.py",
     'round_no = len(rounds) if rounds and now - rounds[-1][-1][0] < H.DEDUP_S else len(rounds) + 1',
     'round_no = len(rounds) + 1'),
    ("khong_unset_override", "bin/dispatch.sh",
     "unset DISPATCH_ROUND_CAP_OVERRIDE DISPATCH_ROUND_CAP_REASON", ": no-unset"),
    ("dispatch_time_gio_dia_phuong", "bin/dispatch_loop_hint.py",
     'return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())', 'return int(dt.timestamp())'),
]


def make_mutant_root(tmp, rel, old, new):
    """Cây giả: bin/ là symlink từng file thật, riêng file đột biến là bản sao đã sửa."""
    real = HERE.parent
    root = Path(tmp)
    (root / "bin").mkdir(parents=True)
    for f in (real / "bin").iterdir():
        if f.is_file():
            (root / "bin" / f.name).symlink_to(f)
    for name in ("kb",):
        (root / name).symlink_to(real / name)
    tgt = root / rel
    src = (real / rel).read_text()
    if old not in src:
        raise SystemExit(f"MUTATION TARGET TRÔI: {rel}: {old[:60]!r} — cập nhật MUTATIONS")
    tgt.unlink()
    tgt.write_text(src.replace(old, new, 1))
    os.chmod(tgt, 0o755)
    return root


def main():
    args = sys.argv[1:]
    if "--mutations" in args:
        survived = []
        for name, rel, old, new in MUTATIONS:
            with tempfile.TemporaryDirectory() as tmp:
                root = make_mutant_root(tmp, rel, old, new)
                killed, killers = False, []
                # Chạy dưới 2 TZ: đột biến phụ thuộc giờ địa phương chỉ lộ khi TZ ≠ UTC.
                for tz_env in (dict(os.environ), dict(os.environ, TZ="America/New_York")):
                    r = subprocess.run([sys.executable, str(HERE / "dispatch_round_cap_selfcheck.py"),
                                        "--root", str(root)], capture_output=True, text=True,
                                       timeout=900, env=tz_env)
                    killed = killed or r.returncode != 0
                    killers += [ln[5:].split(" — ")[0] for ln in r.stdout.splitlines()
                                if ln.startswith("FAIL ") and ln[5:].split(" — ")[0] not in killers]
                print(f"{'KILLED ' if killed else 'SURVIVED'} {name}  ← {', '.join(killers[:4])}")
                if not killed:
                    survived.append(name)
        print(f"\n{len(MUTATIONS) - len(survived)}/{len(MUTATIONS)} mutation bị giết")
        return 1 if survived else 0
    if "--all-tz" in args:
        bad = 0
        for label, env in (("hiện tại", dict(os.environ)),
                           ("env -u TZ", {k: v for k, v in os.environ.items() if k != "TZ"}),
                           ("TZ=America/New_York", dict(os.environ, TZ="America/New_York"))):
            r = subprocess.run([sys.executable, __file__], capture_output=True, text=True, env=env, timeout=900)
            print(f"[{label}] {r.stdout.strip().splitlines()[-1]}")
            bad += r.returncode != 0
        return 1 if bad else 0
    root = HERE.parent
    if "--root" in args:
        root = Path(args[args.index("--root") + 1])
    fails = suite(root)
    print(f"\n{'OK' if not fails else 'FAIL'}: {len(fails)} ca hỏng" + (f" ({', '.join(fails)})" if fails else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
