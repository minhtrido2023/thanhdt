#!/usr/bin/env python3
"""Selfcheck arch_noise_gate.py — mẫu thật lấy từ 100 tin Architecture 18-23/10/2026.
Chạy: python3 bin/arch_noise_gate_selfcheck.py   (không chạm Discord, state ở tmpdir)."""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="archgate_")
os.environ["ARCH_GATE_STATE"] = TMP
sys.path.insert(0, HERE)
import arch_noise_gate as g  # noqa: E402

ARCH = g.arch_id()
FAILS = []


def chk(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


# ---- phải CHẶN (thường lệ) ----
BUFFERED = {
    "🔧 **[wags-autofix] Nhận issue điều phối: 'coord-2026-10-21'** — Wags đang chẩn đoán": "wags_lifecycle",
    "✅ **[wags-autofix] HOÀN TẤT issue 'coord-2026-10-21'** — Wags đã sửa, arch-reviewer audit: **CONFIRMED**": "wags_lifecycle",
    "🧪 **Arch-review (ad-hoc)** — finding Wags khớp 'wags-fix: coord-2026-10-21': **CONFIRMED** — ok": "wags_lifecycle",
    "🚀 **Wags** nhận việc (job `Wags_20261021_114111`): VIỆC SỬA…": "job_progress",
    "ℹ️ **Wags** job `Wags_20261021_114111`: đã chạy 180s, qua trung vị": "job_progress",
    "⚠️ **Wags** job `Wags_20261021_114111`: đã chạy 240s, vượt mốc p75": "job_progress",
    "⏰ **Taylor** vẫn đang chạy (job `Taylor_1`)": "job_progress",
    "🌙 KB nightly done (2026-10-22) — ⚠️ oversized memories: Mafee(8KB)": "kb_nightly",
}
for m, cat in BUFFERED.items():
    chk(f"classify {cat}: {m[:45]}", g.classify(m) == cat)

# ---- phải GỬI (cảnh báo thật) — mọi thứ này KHÔNG được bị chặn ----
MUST_PASS = [
    "🧪 **Arch-review (ad-hoc)** — finding Wags khớp 'wags-fix: coord-2026-10-19': **NEEDS_CHANGES** — x",
    "🧪 **Arch-review (ad-hoc)** — finding Wags khớp 'wags-fix: coord-2026-10-19': **REFUTED** — x",
    "✅ **Wags** xong (job `Wags_20261021_114111`): plan T+1 KHÔNG sẵn sàng — CẦN USER QUYẾT",
    "✅ **Mafee** xong (job `Mafee_1`): STEP_FAIL",
    "🔴 **Selfcheck baseline sweep** — 310 file, 299 PASS.\n**2 ca ĐỎ MỚI**",
    "⚠️ **[wags-autofix] Issue 'coord-2026-10-19' CẦN NGƯỜI XEM** — arch-reviewer verdict: **NEEDS_CHANGES**",
    "🔁 [wags-autofix] Vấn đề 'coord-2026-10-21' TÁI DIỄN trong cooldown — fix trước có thể chưa ăn",
    "🔴 **[wags-autofix] 'coord-2026-10-19' — arch-review NEEDS_CHANGES/REFUTED 2+ VÒNG LIÊN TIẾP",
    "🚨 [backup_freshness] 2026-10-22 — BACKUP CÓ VẤN ĐỀ: fleet Mike",
    "⚠️ [ccdb_bridge_drift] claude-code-discord-bridge đang 387 commit(s) behind origin/main",
    "🩺 Wags — câu hỏi cần anh quyết (treo từ 18/10)",
    "❌ **Wags** hết lượt (job `Wags_1`). Xem log: /x",
    "🔴 **Circuit breaker OPEN** cho **Wags** (3 lỗi)",
    "🐤 corp_action_feed_canary 2026-10-19: 1/4 mục WARN",
    "🧪 **Arch-review (ad-hoc)** — finding Taylor khớp 'capit': **REFUTED**",   # không phải wags-fix
    "mọi tin lạ không khớp mẫu nào",
    "",
]
for m in MUST_PASS:
    chk(f"pass-through: {m[:50]!r}", g.classify(m) is None)

# ---- gate(): topic khác không bị đụng; ARCH_GATE=off; buffer ghi đúng ----
OTHER = json.load(open(g.REGISTRY, encoding="utf-8"))["channels"]["trading_daily"]["id"]
rc, _ = g.gate(OTHER, "🌙 KB nightly done (x)")
chk("topic khác (trading_daily) -> rc=1, không ghi buffer", rc == 1 and not os.path.exists(g.BUFFER))
os.environ["ARCH_GATE"] = "off"
rc, _ = g.gate(ARCH, "🌙 KB nightly done (x)")
chk("ARCH_GATE=off -> rc=1", rc == 1)
del os.environ["ARCH_GATE"]
rc, _ = g.gate(ARCH, "🌙 KB nightly done (2026-10-22) — oversized")
chk("routine @architecture -> rc=0 + ghi buffer", rc == 0 and os.path.getsize(g.BUFFER) > 0)
rc, _ = g.gate(ARCH, "🚨 [backup_freshness] BACKUP CÓ VẤN ĐỀ")
chk("alert @architecture -> rc=1", rc == 1)

# ---- fail-open: state dir không ghi được ----
g.STATE, g.BUFFER = "/proc/nonexistent_x", "/proc/nonexistent_x/buffer.jsonl"
rc, _ = g.gate(ARCH, "🌙 KB nightly done (x)")
chk("lỗi đĩa -> fail-open rc=1 (không nuốt tin)", rc == 1)
g.STATE, g.BUFFER = TMP, os.path.join(TMP, "buffer.jsonl")

# ---- cron_health: job lỗi/STALE mới, đổi chữ ký, nhắc lại sau 7 ngày ----
def cron_msg(errs=(), stale=(), sig="boom"):
    body = "".join(f"  [0 1 * * *] /x/{j}.sh\n    2 dòng lỗi gần nhất trong {j}.log: {sig} {j}\n" for j in errs)
    st = "".join(f"  [0 2 * * *] /s/{j}.sh\n    log cũ 3 ngày\n" for j in stale)
    out = "🩺 [cron_health_check] 2026-10-23: 5 job cần chú ý — chi tiết:\n\ncron_health_check — 100 job, 5 cần chú ý\n\n"
    if errs:
        out += f"=== ERRORS_FOUND ({len(errs)}) ===\n{body}\n"
    if stale:
        out += f"=== STALE ({len(stale)}) ===\n{st}\n"
    return out + "=== OK (9) ===\n"
rc, out = g.gate(ARCH, cron_msg(["a", "b"]))
chk("cron lần 1: 2 lỗi mới -> rc=10 + nêu cả 2", rc == 10 and "a.sh" in out and "b.sh" in out and "2 job cần xem" in out)
rc, out = g.gate(ARCH, cron_msg(["a", "b"]))
chk("cron lần 2 y hệt -> rc=0 (chỉ digest)", rc == 0 and out == "")
rc, out = g.gate(ARCH, cron_msg(["a", "b", "c"]))
chk("cron thêm c -> rc=10, CHỈ nêu c", rc == 10 and "c.sh" in out and "a.sh" not in out)
rc, out = g.gate(ARCH, cron_msg(["a", "b", "c"], stale=["nav"]))
chk("STALE mới (job lỗi cũ không đổi) -> rc=10, nêu nav", rc == 10 and "nav.sh" in out and "STALE" in out and "a.sh" not in out)
rc, out = g.gate(ARCH, cron_msg(["a", "b", "c"], stale=["nav"], sig="KeyError"))
chk("cùng job, chữ ký lỗi ĐỔI -> rc=10", rc == 10 and "a.sh" in out)
rc, out = g.gate(ARCH, cron_msg([], stale=["nav2"]))
chk("chỉ có STALE mới (không ERRORS_FOUND) -> rc=10", rc == 10 and "nav2.sh" in out)
rc, out = g.gate(ARCH, cron_msg(["b"]))
rc, out = g.gate(ARCH, cron_msg(["a", "b"]))
chk("a hết lỗi rồi lỗi lại -> MỚI", rc == 10 and "a.sh" in out)
seen = json.load(open(g.CRON_SEEN, encoding="utf-8"))
k = next(x for x in seen if "/x/a.sh" in x)
seen[k]["last_sent"] = "2020-01-01"
json.dump(seen, open(g.CRON_SEEN, "w", encoding="utf-8"))
rc, out = g.gate(ARCH, cron_msg(["a", "b"]))
chk("job còn lỗi > 7 ngày -> nhắc lại (rc=10, 'còn từ')", rc == 10 and "còn từ" in out and "b.sh" not in out)
bad = "🩺 [cron_health_check] x\n=== ERRORS_FOUND (3) ===\n  [0 1 * * *] /x/a.sh\n    e\n"
rc, out = g.gate(ARCH, bad)
chk("đếm mục không khớp parser -> fail-open rc=1", rc == 1)
rc, out = g.gate(ARCH, "🩺 [cron_health_check] 2026-10-23: tất cả OK (0 cần chú ý).")
chk("cron không có mục nào -> rc=0 (digest)", rc == 0)

# ---- digest + con trỏ byte-offset ----
r = subprocess.run([sys.executable, os.path.join(HERE, "arch_noise_gate.py"), "digest", "--dry-run"],
                   capture_output=True, text=True, env=dict(os.environ))
chk("digest dry-run có tiêu đề + dòng cron_health + STALE", "tổng kết" in r.stdout and "cron_health_check" in r.stdout and "STALE: nav" in r.stdout)
chk("digest không đẩy cursor khi dry-run", not os.path.exists(g.CURSOR))
chk("digest rỗng không vỡ", "Không có việc" in g.build_digest([], "23/10/2026"))
chk("digest liệt kê MỌI kb_nightly", g.build_digest([{"cat": "kb_nightly", "text": "🌙 KB nightly done (a) ⚠️ x"},
                                                      {"cat": "kb_nightly", "text": "🌙 KB nightly done (b) ⚠️ y"}], "d").count("KB nightly:") == 2)
STUB = os.path.join(TMP, "stub_ok.sh")
open(STUB, "w").write("#!/bin/bash\necho \"$1\" >> " + os.path.join(TMP, "posted.txt") + "\n")
os.chmod(STUB, 0o755)
FAILSTUB = os.path.join(TMP, "stub_fail.sh")
open(FAILSTUB, "w").write("#!/bin/bash\nexit 3\n")
os.chmod(FAILSTUB, 0o755)
size0 = os.path.getsize(g.BUFFER)
rc = subprocess.run([sys.executable, os.path.join(HERE, "arch_noise_gate.py"), "digest", "--post"],
                    capture_output=True, text=True, env=dict(os.environ, ARCH_DIGEST_NOTIFY=FAILSTUB)).returncode
chk("digest post THẤT BẠI -> rc≠0 và KHÔNG đẩy con trỏ", rc != 0 and not os.path.exists(g.CURSOR))
rc = subprocess.run([sys.executable, os.path.join(HERE, "arch_noise_gate.py"), "digest", "--post"],
                    capture_output=True, text=True, env=dict(os.environ, ARCH_DIGEST_NOTIFY=STUB)).returncode
chk("digest post OK -> con trỏ = kích thước buffer", rc == 0 and int(open(g.CURSOR).read()) == size0)
g.gate(ARCH, "🌙 KB nightly done (sau digest)")
r = subprocess.run([sys.executable, os.path.join(HERE, "arch_noise_gate.py"), "digest", "--dry-run"],
                   capture_output=True, text=True, env=dict(os.environ))
chk("lượt digest sau chỉ thấy bản ghi MỚI (không lặp)", "sau digest" in r.stdout and "cron_health_check" not in r.stdout)

# ---- e2e notify_thread.sh: tin thường lệ -> buffered, KHÔNG gọi API ----
env = dict(os.environ, ARCH_GATE_STATE=TMP)
E2E_MSG = "🌙 KB nightly done (e2e)"
assert g.classify(E2E_MSG) == "kb_nightly", "e2e sẽ POST THẬT lên Discord nếu regex hồi quy — dừng"
n0 = sum(1 for _ in open(g.BUFFER))
r = subprocess.run([os.path.join(HERE, "notify_thread.sh"), E2E_MSG, "architecture"],
                   capture_output=True, text=True, env=env)
chk("notify_thread.sh e2e: rc=0 + buffered", r.returncode == 0 and "buffered" in r.stdout)
chk("notify_thread.sh e2e: buffer +1 dòng", sum(1 for _ in open(g.BUFFER)) == n0 + 1)

shutil.rmtree(TMP, ignore_errors=True)
print("\nTOÀN BỘ PASS" if not FAILS else f"\n{len(FAILS)} FAIL: {FAILS}")
sys.exit(1 if FAILS else 0)
