# -*- coding: utf-8 -*-
"""
dt4_decision_review.py
======================
End-of-June reminder: surface the V12 DT 4-gate vs TQ34b paper-trade A/B
decision. Triggered once by a Windows scheduled task (DT4DecisionReview)
on 2026-06-29 09:00 local.

Steps:
  1. Refresh the comparison (runs papertrade_compare.py so the report is current).
  2. Extract the A/B decision section + headline standings from
     data/papertrade_compare5.md.
  3. Write a prominent reminder file data/DT4_DECISION_REVIEW.md.
  4. Best-effort Windows popup so the reminder is noticed.
"""
import os, sys, io, subprocess, datetime as dt

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)

CMP_MD = os.path.join(WORKDIR, "data", "papertrade_compare5.md")
OUT_MD = os.path.join(WORKDIR, "data", "DT4_DECISION_REVIEW.md")

# 1. Refresh the comparison report (best-effort)
try:
    subprocess.run([sys.executable, "papertrade_compare.py"], timeout=600,
                   cwd=WORKDIR, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
except Exception as e:
    print(f"  (compare refresh failed: {e}; using existing report)")

# 2. Extract sections from the comparison report
ab, headline = "", ""
if os.path.exists(CMP_MD):
    md = open(CMP_MD, encoding="utf-8").read()
    # A/B decision block
    if "V12_DT4 vs V12_TQ34b" in md:
        seg = md.split("## V12_DT4 vs V12_TQ34b", 1)[1]
        ab = "## V12_DT4 vs V12_TQ34b" + seg.split("\n##", 1)[0]
    # Headline metrics table
    if "## Headline metrics" in md:
        seg = md.split("## Headline metrics", 1)[1]
        headline = "## Headline metrics" + seg.split("\n##", 1)[0]
else:
    ab = "⚠️ data/papertrade_compare5.md not found — run papertrade_daily.bat first."

now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
banner = f"""# ⭐ DECISION DUE — DT 4-gate vs TQ34b (V12 paper-trade A/B)

*Reminder fired: {now}*

You set this checkpoint to decide whether to switch the V12 paper-trade system
from TQ34b to the DT 4-gate state. Below is the latest A/B from ~3 months of
live paper-trade (Apr 1 → end June 2026).

**How to decide:**
- 🟢 SWITCH  → DT 4-gate held its backtested edge (+1.06pp). To promote: point
  pt_v12_tq34b.py's state source to DT (or retire it for pt_v12_dt4.py), and
  consider promoting `tav2_bq.vnindex_5state_dt_4gate` to LIVE `vnindex_5state`.
- 🟡 HOLD    → keep both arms running, revisit later.
- 🔴 KEEP TQ → DT underperformed live; stay on TQ34b.

Full report: `data/papertrade_compare5.md`

---

{ab}

---

{headline}
"""

try:
    open(OUT_MD, "w", encoding="utf-8").write(banner)
    print(f"Wrote {OUT_MD}")
except PermissionError:
    OUT_MD2 = OUT_MD.replace(".md", ".new.md")
    open(OUT_MD2, "w", encoding="utf-8").write(banner)
    print(f"(locked) wrote {OUT_MD2}")

# 4. Best-effort Windows popup (works when task runs in an interactive session)
try:
    import ctypes
    verdict = ""
    for line in ab.splitlines():
        if "Verdict" in line:
            verdict = line.replace("*", "").strip()
            break
    ctypes.windll.user32.MessageBoxW(
        0,
        f"DT 4-gate vs TQ34b — decision due.\n\n{verdict}\n\n"
        f"See data/DT4_DECISION_REVIEW.md",
        "Paper-trade A/B Decision (V12)", 0x40)  # MB_ICONINFORMATION
except Exception as e:
    print(f"  (popup skipped: {e})")

print("DT4 decision review complete.")
