#!/usr/bin/env python3
"""Selfcheck arch_noise_gate.py — mẫu thật lấy từ 100 tin Architecture 18-23/10/2026.
Chạy: python3 bin/arch_noise_gate_selfcheck.py   (không chạm Discord, state ở tmpdir)."""
import json, os, subprocess, sys, tempfile

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
    "🧪 **Arch-review (ad-hoc)** — finding Wags khớp 'wags-fix: coord-2026-10-19': **NEEDS_CHANGES** — x": "wags_lifecycle",
    "🚀 **Wags** nhận việc (job `Wags_20261021_114111`): VIỆC SỬA…": "job_progress",
    "ℹ️ **Wags** job `Wags_20261021_114111`: đã chạy 180s, qua trung vị": "job_progress",
    "⚠️ **Wags** job `Wags_20261021_114111`: đã chạy 240s, vượt mốc p75": "job_progress",
    "⏰ **Taylor** vẫn đang chạy (job `Taylor_1`)": "job_progress",
    "✅ **Wags** xong (job `Wags_20261021_114111`): kết quả…": "job_done",
    "🌙 KB nightly done (2026-10-22) — ⚠️ oversized memories: Mafee(8KB)": "kb_nightly",
    "🔴 **Selfcheck baseline sweep** — 310 file, 299 PASS.": "selfcheck_sweep",
}
for m, cat in BUFFERED.items():
    chk(f"classify {cat}: {m[:45]}", g.classify(m) == cat)

# ---- phải GỬI (cảnh báo thật) — mọi thứ này KHÔNG được bị chặn ----
MUST_PASS = [
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

# ---- cron_health: chỉ lỗi MỚI mới gửi ----
def cron_msg(jobs):
    body = "".join(f"  [0 1 * * *] /x/{j}.sh\n    2 dòng lỗi gần nhất trong {j}.log: boom {j}\n" for j in jobs)
    return (f"🩺 [cron_health_check] 2026-10-23: 5 job cần chú ý — chi tiết:\n\ncron_health_check — 100 job, 5 cần chú ý\n\n"
            f"=== ERRORS_FOUND ({len(jobs)}) ===\n{body}\n=== STALE (1) ===\n  [x] /y\n")
rc, out = g.gate(ARCH, cron_msg(["a", "b"]))
chk("cron lần 1: 2 lỗi mới -> rc=10 + nêu cả 2", rc == 10 and "a.sh" in out and "b.sh" in out and "2 job lỗi MỚI" in out)
rc, out = g.gate(ARCH, cron_msg(["a", "b"]))
chk("cron lần 2 y hệt -> rc=0 (chỉ digest)", rc == 0 and out == "")
rc, out = g.gate(ARCH, cron_msg(["a", "b", "c"]))
chk("cron lần 3 thêm c -> rc=10, CHỈ nêu c", rc == 10 and "c.sh" in out and "a.sh" not in out and "1 job lỗi MỚI" in out)
rc, out = g.gate(ARCH, cron_msg(["b"]))
rc, out = g.gate(ARCH, cron_msg(["a", "b"]))
chk("a hết lỗi rồi lỗi lại -> tính là MỚI", rc == 10 and "a.sh" in out)
bad = "🩺 [cron_health_check] x\n=== ERRORS_FOUND (3) ===\n  [0 1 * * *] /x/a.sh\n    e\n"
rc, out = g.gate(ARCH, bad)
chk("đếm ERRORS_FOUND không khớp parser -> fail-open rc=1", rc == 1)
rc, out = g.gate(ARCH, "🩺 [cron_health_check] 2026-10-23: tất cả OK (0 cần chú ý).")
chk("cron không có mục lỗi -> rc=0 (digest)", rc == 0)

# ---- digest ----
r = subprocess.run([sys.executable, os.path.join(HERE, "arch_noise_gate.py"), "digest", "--dry-run"],
                   capture_output=True, text=True, env=dict(os.environ))
chk("digest dry-run có tiêu đề + dòng cron_health", "tổng kết" in r.stdout and "cron_health_check" in r.stdout)
chk("digest không đẩy cursor khi dry-run", not os.path.exists(g.CURSOR))
chk("digest rỗng không vỡ", "Không có việc" in g.build_digest([], "23/10/2026"))

# ---- e2e notify_thread.sh: tin thường lệ -> buffered, KHÔNG gọi API ----
env = dict(os.environ, ARCH_GATE_STATE=TMP)
n0 = sum(1 for _ in open(g.BUFFER))
r = subprocess.run([os.path.join(HERE, "notify_thread.sh"), "🌙 KB nightly done (e2e)", "architecture"],
                   capture_output=True, text=True, env=env)
chk("notify_thread.sh e2e: rc=0 + buffered", r.returncode == 0 and "buffered" in r.stdout)
chk("notify_thread.sh e2e: buffer +1 dòng", sum(1 for _ in open(g.BUFFER)) == n0 + 1)

print("\nTOÀN BỘ PASS" if not FAILS else f"\n{len(FAILS)} FAIL: {FAILS}")
sys.exit(1 if FAILS else 0)
