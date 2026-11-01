#!/usr/bin/env python3
"""Selfcheck work_tree_section() của daily_decision_topic: ca đủ dữ liệu + ca thiếu file (không được làm hỏng bản tin)."""
import importlib.util, json, sys, tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ddt", HERE / "daily_decision_topic.py")
ddt = importlib.util.module_from_spec(spec); spec.loader.exec_module(ddt)
now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
fails = []


def check(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name + (" — %s" % (info,) if info and not ok else ""))
    if not ok:
        fails.append(name)


def mk(merged=True, token=True, cfg=None, raw=None):
    r = Path(tempfile.mkdtemp(prefix="ddt_wt_"))
    (r / "state/work_tree").mkdir(parents=True); (r / "secrets").mkdir(); (r / "kb").mkdir()
    if merged:
        (r / "state/work_tree/merged.json").write_text(raw if raw is not None else json.dumps(
            {"counts": {"need_user": 3, "overdue": 5, "recent": 7, "inbox": 2}}))
    if token:
        (r / "secrets/work_tree_token").write_text("tok/en+1\n")
    if cfg:
        (r / "kb/work_tree_config.json").write_text(json.dumps(cfg))
    return str(r)


t = ddt.work_tree_section(now, mk())
check("đủ dữ liệu: 4 số + link mặc định", t and all(x in t for x in ("**3**", "**5**", "**7**", "**2**"))
      and "http://192.168.100.7:8610/?k=tok%2Fen%2B1" in t, t)
t = ddt.work_tree_section(now, mk(cfg={"base_url": "http://x:1/"}))
check("base_url lấy từ kb/work_tree_config.json", t and "http://x:1/?k=" in t, t)
check("thiếu merged.json → None", ddt.work_tree_section(now, mk(merged=False)) is None)
check("thiếu token → None", ddt.work_tree_section(now, mk(token=False)) is None)
check("merged.json hỏng → None", ddt.work_tree_section(now, mk(raw="{không phải json")) is None)
check("thiếu key counts → None", ddt.work_tree_section(now, mk(raw="{}")) is None)
# build() không vỡ khi thiếu file: thay các nguồn nặng bằng stub
ddt.pending_questions = lambda: []; ddt.user_wait_section = lambda: []
ddt.funnel_section = lambda: "F"; ddt.dashboard_section = lambda n: "D"
ddt.ROOT = mk(merged=False)
txt = ddt.build(now)
check("build() vẫn chạy, không có dòng Cây việc khi thiếu merged.json", "Việc cần anh quyết" in txt and "Cây việc" not in txt)
ddt.ROOT = mk()
check("build() có dòng Cây việc khi đủ dữ liệu", "Cây việc" in ddt.build(now))
print("RESULT: " + ("FAIL %s" % fails if fails else "PASS"))
sys.exit(1 if fails else 0)
