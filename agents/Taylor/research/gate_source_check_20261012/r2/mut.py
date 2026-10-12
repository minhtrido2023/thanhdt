import shutil, subprocess, sys, os, re
from pathlib import Path
WT = Path("/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-gatesrc-1012")
M = Path("/tmp/gs_r2/mut")
def fresh():
    shutil.rmtree(M, ignore_errors=True); M.mkdir(parents=True)
    shutil.copytree(WT/"bin", M/"bin", symlinks=True); shutil.copytree(WT/"kb", M/"kb", symlinks=True)
def sub(rel, old, new):
    p = M/rel; s = p.read_text(); assert s.count(old) == 1, (rel, old[:50], s.count(old)); p.write_text(s.replace(old, new))
def run(sc, env=None):
    r = subprocess.run([sys.executable, str(M/"bin"/sc)], capture_output=True, text=True, timeout=900, env=dict(os.environ, **(env or {})))
    out = r.stdout + r.stderr
    fails = [l[:150] for l in out.splitlines() if l.startswith("FAIL") or l.startswith("[FAIL")]
    tail = [l for l in out.splitlines() if "PASS" in l][-1:] 
    return r.returncode, fails, tail
BQ, SP, ND = "bq_freshness_check_selfcheck.py", "send_plan_report_state_gate_selfcheck.py", "notify_discord_selfcheck.py"
G = "bin/gate_source_check.py"
PUB = '_run_pipeline "[pipeline-1] publish_gated_state"      deploy_golive_dt5g_v4/publish_gated_state.py'
MUTS = [
 ("M0 không mutation (đối chứng bản sao)", None, [BQ, SP, ND]),
 ("M1 B1: quay lại `| tee`", lambda: sub("bin/bq_freshness_check.sh", f'  {PUB} > "$GATE_PUB_OUT"\n  cat "$GATE_PUB_OUT"\n', f'  {PUB} | tee "$GATE_PUB_OUT"\n'), [BQ]),
 ("M2 N1: save_marker hỏng ⇒ ném lỗi (nuốt Discord+bus)", lambda: sub(G, "    except OSError as exc:\n        return _err(exc)\n\n\ndef _run", "    except OSError:\n        raise\n\n\ndef _run"), [BQ]),
 ("M3 N2: fromtimestamp trần", lambda: sub(G, "dt.datetime.fromtimestamp(mtime, ICT)", "dt.datetime.fromtimestamp(mtime)"), [BQ]),
 ("M4 N2: fromtimestamp(utc)", lambda: sub(G, "dt.datetime.fromtimestamp(mtime, ICT)", "dt.datetime.fromtimestamp(mtime, dt.timezone.utc)"), [BQ]),
 ("M5 N3: bỏ timeout của helper", lambda: sub(G, "text=True, timeout=SEND_TIMEOUT_S)", "text=True)"), [BQ]),
 ("M6 N5: khoá một-ô (chỉ giữ cặp hiện tại)", lambda: sub(G, 'if k.startswith(publish_date + "|") and isinstance(v, dict)}', 'if k == key and isinstance(v, dict)}'), [BQ]),
 ("M7 N5: câu WARN cũ 'lượt chạy lại sẽ thử lại'", lambda: sub(G, "Chưa đánh dấu; \"\n                  f\"KHÔNG có lượt tự chạy lại cùng ngày", "Chưa đánh dấu, lượt chạy lại sẽ thử lại; \"\n                  f\"(không có lượt tự chạy lại cùng ngày)"), [BQ]),
 ("M8 N4: lỗi helper ⇒ sys.exit(1)", lambda: sub("bin/send_plan_report.sh", '    _gs_line = (f"⚠️ KHÔNG kiểm được nguồn cổng DT5G của bản publish hôm nay ({type(_e).__name__}: "\n                f"{_e}) — không chặn plan, tự xem trường source trong golive_state_today.json")', '    sys.exit(1)'), [SP]),
 ("M9 N4: lỗi helper ⇒ câm", lambda: sub("bin/send_plan_report.sh", '    _gs_line = (f"⚠️ KHÔNG kiểm được nguồn cổng DT5G của bản publish hôm nay ({type(_e).__name__}: "\n                f"{_e}) — không chặn plan, tự xem trường source trong golive_state_today.json")', '    _gs_line = ""'), [SP]),
 ("M10 R0: bỏ --max-time của curl", lambda: sub("bin/notify_discord.sh", ' --max-time "${MIKE_DISCORD_MAX_TIME:-15}"', ''), [ND]),
 ("M11 N1: bỏ lệnh gọi sau khi ghi dấu hỏng (return sớm)", lambda: sub(G, "    _mark()                              # bằng chứng", "    if save_marker(a.workdir, marker):\n        return 0\n    _mark()                              # bằng chứng"), [BQ]),
]
only = sys.argv[1:]
for name, fn, scs in MUTS:
    if only and not any(name.startswith(o) for o in only): continue
    fresh()
    if fn: fn()
    for sc in scs:
        rc, fails, tail = run(sc)
        print(f"== {name} | {sc}: rc={rc} {'ĐỎ' if rc else 'XANH'} {tail}")
        for f in fails[:6]: print("     ", f)
    sys.stdout.flush()
