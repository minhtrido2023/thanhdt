"""send_plan_report.sh --dry-run: bản MASTER vs bản nhánh trên CÙNG fixture. Nguồn DT5G_macro ⇒
output phải y hệt từng byte; DT4_only ⇒ khác nhau đúng 1 dòng (dòng nguồn cổng)."""
import difflib, hashlib, json, os, subprocess, sys, tempfile
master, new = sys.argv[1], sys.argv[2]
def run(script, src):
    with tempfile.TemporaryDirectory(prefix="spr_proof_") as sb:
        os.makedirs(f"{sb}/data/trade_plans"); os.makedirs(f"{sb}/deploy_golive_dt5g_v4")
        json.dump({"plan_date": "2026-08-11", "account": "SpaceX", "state_source": "DT5G_macro", "state": 3,
                   "state_name": "NEUTRAL", "orders": [], "summary": {"action": "HOLD", "reasons": ["fixture"]},
                   "requires_user_approval": False}, open(f"{sb}/data/trade_plans/plan_SpaceX_2026-08-11.json", "w"))
        json.dump({"as_of": "2026-08-10", "source": src, "state": 3, "bq_publish_ok": True,
                   "published_at": "2026-08-10T19:01:15"}, open(f"{sb}/deploy_golive_dt5g_v4/golive_state_today.json", "w"))
        env = dict(os.environ, SEND_PLAN_WORKDIR_OVERRIDE=sb, SEND_PLAN_MARKER_DIR=f"{sb}/markers")
        r = subprocess.run(["bash", script, "--account", "SpaceX", "--dry-run"], capture_output=True, text=True, env=env, timeout=180)
        # đường dẫn sandbox + giờ gửi là thứ duy nhất đổi giữa 2 lượt — chuẩn hoá để so nội dung
        return r.returncode, (r.stdout + "\n--STDERR--\n" + r.stderr).replace(sb, "<SB>")
import re
norm = lambda t: re.sub(r"\d{2}:\d{2} ICT", "HH:MM ICT", t)
for src in ("DT5G_macro", "DT4_only"):
    (ra, a), (rb, b) = run(master, src), run(new, src)
    a, b = norm(a), norm(b)
    d = [l for l in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]
    print(f"{src}: rc master={ra} nhánh={rb} · md5 master={hashlib.md5(a.encode()).hexdigest()} nhánh={hashlib.md5(b.encode()).hexdigest()} · bytes={len(a.encode())}/{len(b.encode())} · GIỐNG HỆT={a == b} · số dòng khác={len(d)}")
    for l in d: print("   ", l[:260])
