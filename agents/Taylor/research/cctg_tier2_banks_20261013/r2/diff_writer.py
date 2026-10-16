#!/usr/bin/env python3
"""Vi sai writer: `main` vs nhánh, chuỗi 12m + 6m (+ các đường từ chối). Mỗi writer chạy trong thư mục tạm riêng với
cùng fixture; so rc / stdout / stderr / md5 mọi file data/. Dùng: diff_writer.py <WorkingClaude của nhánh>"""
import hashlib, json, os, shutil, subprocess, sys, tempfile
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
BR = os.path.abspath(sys.argv[1])
PY = "/home/trido/thanhdt/wc_venv/bin/python"
TODAY_D = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
T = TODAY_D.isoformat()
def srcs(*u):
    return json.dumps([{"publisher": p, "url": url, "date": T, "rate": 7.4} for p, url in u])
GOOD = srcs(("VietnamNet", "https://vietnamnet.vn/a1"), ("Nghe An", "https://baonghean.vn/a1"))
SAME_OWNER = srcs(("CafeF", "https://cafef.vn/x"), ("Kenh14", "https://kenh14.vn/y"))
CMDS = [  # (nhãn, argv, JOB_ID?)
 ("12m manual ok", ["--rate", "7.4", "--effective", "2026-10-06", "--source", "manual_verify", "--note", "n"], None),
 ("12m SKIP lặp", ["--rate", "7.4", "--effective", "2026-10-06", "--source", "manual_verify"], None),
 ("12m lệch >=1pp", ["--rate", "9.0", "--effective", "2026-10-07", "--source", "manual_verify"], None),
 ("12m không mới hơn", ["--rate", "7.4", "--effective", "2026-09-01", "--source", "manual_verify"], None),
 ("12m --force sửa dòng cũ", ["--rate", "7.5", "--effective", "2026-10-06", "--source", "manual_verify", "--force"], None),
 ("12m rate 0", ["--rate", "0", "--effective", "2026-10-08", "--source", "manual_verify"], None),
 ("12m --source sai", ["--rate", "7.4", "--effective", "2026-10-08", "--source", "zzz"], None),
 ("12m --bank lọt vào", ["--rate", "7.4", "--effective", "2026-10-08", "--source", "manual_verify", "--bank", "VPB"], None),
 ("6m manual ok", ["--series", "6m", "--rate", "7.6", "--effective", "2026-10-02", "--source", "manual_verify"], None),
 ("6m SKIP lặp", ["--series", "6m", "--rate", "7.6", "--effective", "2026-10-02", "--source", "manual_verify"], None),
 ("6m lệch >=1pp", ["--series", "6m", "--rate", "9.5", "--effective", "2026-10-03", "--source", "manual_verify"], None),
 ("6m không mới hơn", ["--series", "6m", "--rate", "7.6", "--effective", "2026-09-01", "--source", "manual_verify"], None),
 ("6m --force sửa dòng cũ", ["--series", "6m", "--rate", "7.7", "--effective", "2026-10-02", "--source", "manual_verify", "--force"], None),
 ("12m agent auto ok", ["--rate", "7.4", "--effective", T, "--source", "web_crosscheck_auto", "--collected", T, "--note", "x", "--sources", GOOD], "j1"),
 ("12m agent dùng lại URL", ["--rate", "7.4", "--effective", (TODAY_D + timedelta(days=1)).isoformat(), "--source", "web_crosscheck_auto", "--collected", T, "--note", "x", "--sources", GOOD], "j1"),
 ("12m agent --force", ["--rate", "7.4", "--effective", T, "--source", "web_crosscheck_auto", "--note", "x", "--force"], "j1"),
 ("12m agent manual", ["--rate", "7.4", "--effective", T, "--source", "manual_verify"], "j1"),
 ("12m agent cùng chủ", ["--rate", "7.4", "--effective", (TODAY_D + timedelta(days=2)).isoformat(), "--source", "web_crosscheck_auto", "--collected", T, "--note", "x", "--sources", SAME_OWNER], "j1"),
 ("6m agent auto ok", ["--series", "6m", "--rate", "7.4", "--effective", T, "--source", "web_crosscheck_auto", "--collected", T, "--note", "x", "--sources", GOOD], "j2"),
]
def build(writer_src_bytes):
    d = tempfile.mkdtemp(prefix="cctg_diffw_")
    for n in ("append_deposit_rate.py", "cctg_rate_vn.py"):
        shutil.copy2(os.path.join(BR, n), d)
    open(os.path.join(d, "append_cctg_rate.py"), "wb").write(writer_src_bytes)
    os.makedirs(os.path.join(d, "data"))
    open(os.path.join(d, "data", "cctg_rate_vn_events.csv"), "w").write(
        "effective_date,cctg_rate,collected_date,source,note\n2026-10-05,7.4,2026-10-05,manual_verify,seed\n")
    return d
def run_all(d):
    out = []
    for label, argv, job in CMDS:
        env = {k: v for k, v in os.environ.items() if k != "JOB_ID"}
        env["TZ"] = "Asia/Ho_Chi_Minh"
        if job:
            env["JOB_ID"] = job
        r = subprocess.run([PY, "append_cctg_rate.py"] + argv, cwd=d, capture_output=True, text=True, env=env)
        out.append((label, r.returncode, r.stdout, r.stderr))
    md5 = {}
    for root, _, fs in os.walk(os.path.join(d, "data")):
        for f in sorted(fs):
            md5[f] = hashlib.md5(open(os.path.join(root, f), "rb").read()).hexdigest()
    return out, md5
main_src = subprocess.run(["git", "show", "main:WorkingClaude/append_cctg_rate.py"], cwd=BR, capture_output=True, check=True).stdout
br_src = open(os.path.join(BR, "append_cctg_rate.py"), "rb").read()
dm, db = build(main_src), build(br_src)
om, mm = run_all(dm); ob, mb = run_all(db)
# thư mục tạm khác nhau -> chuẩn hoá đường dẫn trong stdout/stderr
norm = lambda s, d: s.replace(d, "<D>")
ident = 0
for (l, rc1, o1, e1), (_, rc2, o2, e2) in zip(om, ob):
    o1, e1, o2, e2 = norm(o1, dm), norm(e1, dm), norm(o2, db), norm(e2, db)
    same = (rc1, o1, e1) == (rc2, o2, e2)
    ident += same
    print(f"{'GIỐNG ' if same else 'KHÁC  '} rc {rc1}/{rc2} | {l}")
    if not same:
        print("   main  :", repr((o1 + e1)[:300]))
        print("   nhánh :", repr((o2 + e2)[:300]))
print(f"\n{ident}/{len(om)} lệnh giống hệt (rc+stdout+stderr)")
print("md5 data/ main :", mm)
print("md5 data/ nhánh:", mb)
print("md5 GIỐNG HỆT" if mm == mb else "md5 KHÁC")
shutil.rmtree(dm); shutil.rmtree(db)
