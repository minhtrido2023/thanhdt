#!/usr/bin/env python3
"""Selfcheck dòng 'Plan phiên kế tiếp' của daily_decision_topic.py (hạng mục 5, 2026-11-25).
WC giả (account SpaceX+ZaloPay, file plan, golive_state_today.json) + lịch THẬT vn_market (WORKDIR_8L_NEW)."""
import inspect
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ["WORKDIR_8L"] = os.environ.get("WORKDIR_8L_NEW", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, str(HERE))
import daily_decision_topic as D  # noqa: E402

FAILS = 0
TMP = []


def chk(cond, name, out=""):
    global FAILS
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS += 1
        print("   output:", out)


def wc(plans=(), asof="2026-11-23", broken=False):
    d = Path(tempfile.mkdtemp(prefix="ddps_")); TMP.append(d)
    (d / "trading_bot").mkdir()
    (d / "trading_bot" / "__init__.py").write_text("")
    (d / "trading_bot" / "config.py").write_text(
        "raise ImportError('conflict marker')\n" if broken else "def live_dnse_labels():\n    return ['SpaceX', 'ZaloPay']\n")
    (d / "data" / "trade_plans").mkdir(parents=True)
    for acct, date, appr in plans:
        (d / "data" / "trade_plans" / f"plan_{acct}_{date}.json").write_text(
            json.dumps({"plan_date": date, "orders": [], "approved_by": appr}))
    (d / "deploy_golive_dt5g_v4").mkdir()
    (d / "deploy_golive_dt5g_v4" / "golive_state_today.json").write_text(json.dumps({"as_of": asof}))
    return str(d)


try:
    out = D.plan_status_line(datetime(2026, 11, 25, 8, 0), wc(plans=[("SpaceX", "2026-11-25", "user")]))
    chk("Plan phiên kế tiếp (T4 25/11): SpaceX có (đã duyệt) · ZaloPay ❌ KHÔNG · DT5G as_of 2026-11-23 ✅" in out,
        "S1 25/11 08:00: SpaceX có (đã duyệt), ZaloPay KHÔNG, DT5G as_of 23/11 đúng phiên trước", out)
    out = D.plan_status_line(datetime(2026, 11, 24, 8, 0), wc(plans=[("SpaceX", "2026-11-25", None)]))
    chk("(T4 25/11): SpaceX có (chưa duyệt)" in out, "S2 24/11 (lễ) ⇒ phiên kế tiếp = 25/11, không phải 24/11", out)
    out = D.plan_status_line(datetime(2026, 11, 23, 8, 0), wc(asof="2026-11-20"))
    chk("(T2 23/11)" in out and "ngày nghỉ sắp tới: T3 24/11" in out and "as_of 2026-11-20 ✅" in out,
        "S3 23/11 08:00: nêu ngày nghỉ sắp tới T3 24/11; as_of 20/11 = phiên trước 23/11 ⇒ ✅", out)
    out = D.plan_status_line(datetime(2026, 11, 25, 8, 0), wc(asof="2026-11-20"))
    chk("as_of 2026-11-20 ⚠️ (cần 2026-11-23)" in out, "S4 25/11 as_of 20/11 cũ ⇒ ⚠️ cần 23/11 (bỏ qua lễ 24/11)", out)
    out = D.plan_status_line(datetime(2026, 11, 25, 8, 0), wc(plans=[("SpaceX", "2026-11-24", None)]))
    chk("SpaceX ❌ KHÔNG" in out, "S5 chỉ có plan 24/11 (ngày sai) ⇒ 25/11 vẫn KHÔNG", out)
    out = D.plan_status_line(datetime(2026, 11, 25, 8, 0), wc(broken=True))
    chk("KHÔNG đọc được trạng thái" in out and "conflict marker" in out, "S6 config lỗi ⇒ nói rõ lỗi thật, không im lặng", out)
    src = inspect.getsource(D.plan_status_line)
    chk("pending_questions" not in src and "bus" not in src.split('"""')[2],
        "S7 đọc từ ARTIFACT (file plan/golive_state), không từ bus question", "")
    src_b = inspect.getsource(D.build)
    chk("plan_status_line(now)" in src_b.split("\n")[13] or "plan_status_line(now)" in src_b,
        "S8 build() chèn dòng ngay dưới tiêu đề 'Việc cần anh quyết'", "")
finally:
    for d in TMP:
        shutil.rmtree(d, ignore_errors=True)
print(f"daily_decision_plan_status_selfcheck: {'PASS' if FAILS == 0 else f'FAIL ({FAILS})'}")
sys.exit(1 if FAILS else 0)
