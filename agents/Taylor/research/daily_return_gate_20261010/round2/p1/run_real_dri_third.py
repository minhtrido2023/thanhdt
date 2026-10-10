"""Chạy probe DRI THẬT + tài khoản thứ ba của reviewer (real_dri_third.py) SAU rồi TRƯỚC (53b48b76),
dùng chung một sổ nhớ BQ tạm (tự xoá). Chỉ đọc dữ liệu."""
import os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
W = "/home/trido/thanhdt/WorkingClaude/wt-dailyreturn-1010/bin"
OLD = "/tmp/taylor_r2_old_bin"
src = open("/tmp/archrev_k1_evidence/real_dri_third.py", encoding="utf-8").read()
memo = tempfile.mkdtemp(prefix="taylor_k1_memo.")
try:
    for tag, extra in (("after", ""), ("before_53b48b76", f'; sys.path.insert(0, "{OLD}")')):
        code = src.replace("/tmp/archrev_k1/memo_all", memo).replace(
            f'sys.path.insert(0, "{W}")', f'sys.path.insert(0, "{W}"){extra}')
        assert memo in code and (not extra or OLD in code)
        p = os.path.join(HERE, f"real_dri_third_{tag}.py")
        open(p, "w", encoding="utf-8").write(code)
        env = dict(os.environ, WC_ROOT="/home/trido/thanhdt/WorkingClaude"); env.pop("TZ", None)
        with open(os.path.join(HERE, f"real_dri_third_{tag}.txt"), "w", encoding="utf-8") as out:
            rc = subprocess.run([sys.executable, p], stdout=out, stderr=subprocess.STDOUT, env=env).returncode
            out.write(f"\n[rc={rc}]\n")
finally:
    shutil.rmtree(memo, ignore_errors=True)
