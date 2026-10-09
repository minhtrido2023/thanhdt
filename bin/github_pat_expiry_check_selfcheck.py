#!/usr/bin/env python3
"""github_pat_expiry_check_selfcheck.py — bin/github_pat_expiry_check.sh với header giả lập
(GITHUB_PAT_HEADERS_CMD) + stub git/curl cho đường fetch THẬT + đồng hồ giả (GITHUB_PAT_NOW) + sandbox state/log + notify stub.
Ca: 20/10/3/âm ngày, không header, lỗi mạng, HTTP 401, stamp 1 lần/ngày, token không lộ,
QUIET, và `env -u TZ`. Gọi thật không dùng Discord: BIN_DIR của script được trỏ vào bản copy
có notify_thread.sh giả."""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path

REAL = Path(__file__).resolve().parent / "github_pat_expiry_check.sh"
NOW = 1_791_000_000                      # epoch cố định
SECRET = "ghp_SUPERSECRETTOKEN123"
PASS = FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"PASS {name}")
    else: FAIL += 1; print(f"FAIL {name} {detail}")

def hdr(days, status=200):
    exp = NOW + int(days * 86400) + 3600
    d = subprocess.check_output(["date", "-u", "-d", f"@{exp}", "+%Y-%m-%d %H:%M:%S UTC"], text=True).strip()
    return f"printf 'HTTP/2 {status} \\r\\ncontent-type: x\\r\\ngithub-authentication-token-expiration: {d}\\r\\n\\r\\n'"

def run(sb, cmd, quiet=False, drop_tz=False, extra=None):
    env = dict(os.environ)
    if drop_tz: env.pop("TZ", None)
    env.update(GITHUB_PAT_HEADERS_CMD=cmd, GITHUB_PAT_NOW=str(NOW),
               GITHUB_PAT_STATE_DIR=str(sb / "state"), GITHUB_PAT_LOG_DIR=str(sb / "logs"))
    env["BACKUP_FRESHNESS_QUIET"] = "1" if quiet else "0"
    if extra: env.update(extra)
    p = subprocess.run(["bash", str(sb / "bin" / "github_pat_expiry_check.sh")], env=env, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def mk(notify_ok=True):
    sb = Path(tempfile.mkdtemp(prefix="patexp_"))
    (sb / "bin").mkdir()
    shutil.copy(REAL, sb / "bin" / REAL.name)
    (sb / "bin" / "notify_thread.sh").write_text(
        f'#!/usr/bin/env bash\necho "$2|$1" >> "{sb}/sent.txt"\n' + ("" if notify_ok else "exit 1\n"))
    (sb / "bin" / "notify_thread.sh").chmod(0o755)
    return sb

def sent(sb):
    f = sb / "sent.txt"
    return f.read_text() if f.exists() else ""

def logtxt(sb):
    f = sb / "logs" / "github_pat_expiry.log"
    return f.read_text() if f.exists() else ""

# 20 ngày → im lặng, rc 0
sb = mk(); rc, out, err = run(sb, hdr(20)); check("20d: rc0, không gửi", rc == 0 and sent(sb) == "" and "còn 20 ngày" in out, out)
# giờ:phút:giây trong header không bị cắt tại dấu ':' (bug awk -F': *' 2026-10-09)
sb = mk(); rc, out, err = run(sb, "printf 'HTTP/2 200 \\r\\ngithub-authentication-token-expiration: 2026-11-15 00:17:45 UTC\\r\\n\\r\\n'", quiet=True)
check("parse giờ đầy đủ", "hết hạn 2026-11-15 07:17 ICT" in out, out)
# 10 ngày → vàng, gửi architecture 1 lần, stamp
sb = mk(); rc, out, err = run(sb, hdr(10))
s = sent(sb); check("10d: gửi architecture 🟡", rc == 0 and s.startswith("architecture|🟡") and "~/.git-credentials" in s, s)
check("10d: có stamp", (sb / "state" / "github_pat_expiry_alerted.txt").exists())
run(sb, hdr(10)); check("10d: lần 2 cùng ngày không gửi lại", sent(sb).count("architecture|") == 1)
# qua ngày (NOW+1d) → gửi lại
rc, out, err = run(sb, hdr(10), extra={"GITHUB_PAT_NOW": str(NOW + 86400)})
check("10d: ngày sau gửi lại", sent(sb).count("architecture|") == 2)
# 3 ngày → đỏ đậm
sb = mk(); run(sb, hdr(3)); s = sent(sb); check("3d: 🔴 đậm", s.startswith("architecture|🔴") and "**" in s, s)
sb = mk(); run(sb, hdr(2)); check("2d: 🔴", sent(sb).startswith("architecture|🔴"))
# đã quá hạn → đỏ, số ngày âm
sb = mk(); rc, out, err = run(sb, hdr(-2)); check("quá hạn: 🔴 + âm", sent(sb).startswith("architecture|🔴") and "còn -" in out, out)
# QUIET: in nhưng không gửi, không stamp
sb = mk(); rc, out, err = run(sb, hdr(5), quiet=True)
check("QUIET: in, không gửi, không stamp", "🟡" in out and sent(sb) == "" and not (sb / "state" / "github_pat_expiry_alerted.txt").exists())
# không header → im lặng, không log lỗi
sb = mk(); rc, out, err = run(sb, "printf 'HTTP/2 200 \\r\\ncontent-type: x\\r\\n\\r\\n'")
check("không header: im lặng", rc == 0 and sent(sb) == "" and logtxt(sb) == "" and "không có hạn" in out, out)
# lỗi mạng (rc≠0) → log lỗi, rc 0, KHÔNG cảnh báo
sb = mk(); rc, out, err = run(sb, "echo 'curl: (6) Could not resolve host' ; exit 6")
check("lỗi mạng: log thật, không cảnh báo, rc0", rc == 0 and sent(sb) == "" and "rc=6" in logtxt(sb) and "ERROR" in err, logtxt(sb))
# HTTP 401 → log lỗi, không cảnh báo
sb = mk(); rc, out, err = run(sb, hdr(5, status=401))
check("HTTP401: log lỗi, không cảnh báo", rc == 0 and sent(sb) == "" and "HTTP '401'" in logtxt(sb), logtxt(sb))
# header rác → log lỗi
sb = mk(); rc, out, err = run(sb, "printf 'HTTP/2 200 \\r\\ngithub-authentication-token-expiration: garbage\\r\\n\\r\\n'")
check("header rác: log lỗi, không cảnh báo", rc == 0 and sent(sb) == "" and "không parse" in logtxt(sb), logtxt(sb))
# notify hỏng → log lỗi, không stamp (lần sau thử lại), rc 0
sb = mk(notify_ok=False); rc, out, err = run(sb, hdr(5))
check("notify hỏng: log, không stamp, rc0", rc == 0 and "KHÔNG tới Discord" in logtxt(sb) and not (sb / "state" / "github_pat_expiry_alerted.txt").exists())
# token không lộ: lệnh header giả có in token ra stderr/stdout → log lỗi phải che
sb = mk(); rc, out, err = run(sb, f"echo 'Authorization: Bearer {SECRET}'; exit 7")
check("token bị che trong log lỗi", SECRET not in logtxt(sb) and SECRET not in err, logtxt(sb))
# env -u TZ
sb = mk(); rc, out, err = run(sb, hdr(10), drop_tz=True); check("env -u TZ: vẫn đúng", rc == 0 and sent(sb).startswith("architecture|🟡"))
# --- đường fetch THẬT (không GITHUB_PAT_HEADERS_CMD), stub git/curl đầu PATH, cwd KHÔNG phải repo ---
def real_path_run(sb, curl_out, git_ok_only_with_C=True):
    stubs = sb / "stubs"; stubs.mkdir(exist_ok=True)
    (stubs / "git").write_text(f"""#!/usr/bin/env bash
# chỉ trả credential khi được gọi với -C <thư mục repo> (giống thực tế: helper nằm trong .git/config)
if [ "$1" = "-C" ] && [ "$3" = "credential" ] && [ "$4" = "fill" ]; then cat >/dev/null; printf 'username=u\\npassword={SECRET}\\n'; exit 0; fi
exit 128
""")
    (stubs / "curl").write_text(f"""#!/usr/bin/env bash
printf '%s\\n' "$@" > "{sb}/curl_argv.txt"; cat > "{sb}/curl_stdin.txt"
{curl_out}
""")
    for f in stubs.iterdir(): f.chmod(0o755)
    env = dict(os.environ); env.pop("GITHUB_PAT_HEADERS_CMD", None)
    env.update(PATH=f"{stubs}:{os.environ['PATH']}", GITHUB_PAT_NOW=str(NOW), BACKUP_FRESHNESS_QUIET="0",
               GITHUB_PAT_STATE_DIR=str(sb / "state"), GITHUB_PAT_LOG_DIR=str(sb / "logs"))
    p = subprocess.run(["bash", str(sb / "bin" / "github_pat_expiry_check.sh")], env=env, cwd="/", capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

H10 = hdr(10)
sb = mk(); rc, out, err = real_path_run(sb, H10)
argv = (sb / "curl_argv.txt").read_text(); stdin = (sb / "curl_stdin.txt").read_text()
check("real path từ cwd=/: gửi cảnh báo", rc == 0 and sent(sb).startswith("architecture|🟡"), out + err + logtxt(sb))
check("real path: token chỉ ở stdin curl, không ở argv/stdout/stderr/log/Discord",
      SECRET in stdin and SECRET not in argv and SECRET not in out + err + logtxt(sb) + sent(sb), argv)
sb = mk(); rc, out, err = real_path_run(sb, "printf 'HTTP/1.1 200\\r\\nGitHub-Authentication-Token-Expiration: 2026-11-15 00:17:45 UTC\\r\\n\\r\\n'")
check("real path: HTTP/1.1 200 không reason + tên header viết hoa vẫn parse", "ICT" in out and "ngày" in out, out + logtxt(sb))
sb = mk(); rc, out, err = real_path_run(sb, "exit 6")
check("real path: curl lỗi → log có rc, không cảnh báo", rc == 0 and sent(sb) == "" and "rc=3" in logtxt(sb), logtxt(sb))
sb = mk()
stubs_bad = sb / "stubs"; stubs_bad.mkdir()
(stubs_bad / "git").write_text("#!/usr/bin/env bash\nexit 128\n"); (stubs_bad / "git").chmod(0o755)
env = dict(os.environ); env.update(PATH=f"{stubs_bad}:{os.environ['PATH']}", GITHUB_PAT_NOW=str(NOW), GITHUB_PAT_STATE_DIR=str(sb / "state"), GITHUB_PAT_LOG_DIR=str(sb / "logs"))
env.pop("GITHUB_PAT_HEADERS_CMD", None)
p = subprocess.run(["bash", str(sb / "bin" / "github_pat_expiry_check.sh")], env=env, cwd="/", capture_output=True, text=True)
check("không có credential: log nêu LÝ DO, không cảnh báo, rc0", p.returncode == 0 and sent(sb) == "" and "credential" in logtxt(sb), logtxt(sb))

print(f"\n{PASS} pass, {FAIL} fail"); sys.exit(1 if FAIL else 0)
