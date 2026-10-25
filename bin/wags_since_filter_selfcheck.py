#!/usr/bin/env python3
"""wags_since_filter_selfcheck.py — khoá bộ lọc mốc `since` (DISPATCH_START_ISO) của pipeline wags_autofix.

Sự cố gốc (code-quality 2026-10-25): label `coord-<ngày>` lặp nhiều vòng/ngày; vòng mà Wags KHÔNG ghi
finding mới vẫn khớp finding CŨ ⇒ risk-tier/arch-review chấm finding cũ ⇒ ✅ HOÀN TẤT giả.

Kiểm 2 nơi: wags_risk_tier.py (chạy thật trên inbox giả) và selector python của _arch_review trong
wags_autofix.sh (trích nguyên văn từ file thật, không chép lại).
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []


def chk(name, ok, extra=""):
    print(("PASS: " if ok else "FAIL: ") + name + ("" if ok else f"  {extra}"))
    if not ok:
        FAILS.append(name)


def tier(inbox, *extra):
    r = subprocess.run([sys.executable, os.path.join(HERE, "wags_risk_tier.py"), inbox, "wags-fix: coord-X", *extra],
                       capture_output=True, text=True)
    return r.stdout.strip()


with tempfile.TemporaryDirectory() as td:
    inbox = os.path.join(td, "Wags.jsonl")
    old = {"ts": "2026-10-25T01:00:00Z", "event_type": "finding", "topic": "wags-fix: coord-X lần 1",
           "payload": {"files_changed": ["kb/a.md"]}}
    new = {"ts": "2026-10-25T05:00:00Z", "event_type": "finding", "topic": "wags-fix: coord-X lần 2",
           "payload": {"files_changed": ["bin/dispatch.sh"]}}
    with open(inbox, "w", encoding="utf-8") as f:
        f.write(json.dumps(old) + "\n")
    chk("không có mốc: hành vi cũ (finding cũ low-risk => low)", tier(inbox) == "low")
    chk("mốc SAU finding cũ: finding cũ bị bỏ => high (fail-safe)", tier(inbox, "2026-10-25T02:00:00Z") == "high")
    chk("mốc TRƯỚC finding: nhận => low", tier(inbox, "2026-10-25T00:00:00Z") == "low")
    chk("mốc trùng đúng giây: nhận (>=)", tier(inbox, "2026-10-25T01:00:00Z") == "low")
    with open(inbox, "a", encoding="utf-8") as f:
        f.write(json.dumps(new) + "\n")
    chk("có finding mới sau mốc: phân loại theo finding MỚI (dispatch.sh => high), không theo cái cũ",
        tier(inbox, "2026-10-25T02:00:00Z") == "high")

# Selector _arch_review: trích đúng heredoc python từ wags_autofix.sh và chạy (KHÔNG chạy --review-topic:
# mode đó post Discord). Mốc sau finding cuối ⇒ không chọn gì (exit 3) ⇒ shell trả INCONCLUSIVE, không gọi claude.
import re
src = open(os.path.join(HERE, "wags_autofix.sh"), encoding="utf-8").read()
m = re.search(r"python3 - \"\$inbox\" \"\$substr\" \"\$since\" <<'PY'\n(.*?)\nPY\n", src, re.S)
chk("trích được selector python từ _arch_review", bool(m))
if m:
    with tempfile.TemporaryDirectory() as td:
        inbox = os.path.join(td, "Wags.jsonl")
        sel = os.path.join(td, "sel.py")
        open(sel, "w", encoding="utf-8").write(m.group(1))
        with open(inbox, "w", encoding="utf-8") as f:
            f.write(json.dumps({"ts": "2026-10-25T01:00:00Z", "event_type": "finding",
                                "topic": "wags-fix: coord-X", "payload": {}}) + "\n")

        def pick(since):
            return subprocess.run([sys.executable, sel, inbox, "wags-fix: coord-X", since],
                                  capture_output=True, text=True)
        chk("selector: không mốc => nhận finding", pick("").returncode == 0)
        chk("selector: mốc trước finding => nhận", pick("2026-10-25T00:00:00Z").returncode == 0)
        r = pick("2026-10-25T02:00:00Z")
        chk("selector: mốc SAU finding => exit 3 (không chọn finding cũ)", r.returncode == 3, r.stdout)

print("\nTOÀN BỘ PASS" if not FAILS else f"\n{len(FAILS)} FAIL: {FAILS}")
sys.exit(1 if FAILS else 0)
