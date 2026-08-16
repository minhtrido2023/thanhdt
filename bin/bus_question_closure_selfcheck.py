#!/usr/bin/env python3
"""Regression checks for canonical cross-topic bus-question closure."""
from __future__ import annotations

import json
import datetime
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "bin" / "close_bus_question.py"
AUDIT = ROOT / "bin" / "bus_question_audit.py"


def event(agent, etype, topic, ts, payload=None):
    return {"agent_id": agent, "event_type": etype, "topic": topic, "ts": ts,
            "payload": payload or {}}


def write_event(root: Path, agent: str, rec: dict):
    path = root / "bus" / "inbox" / f"{agent}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def audit(root: Path):
    env = {"BUS_AUDIT_ROOT": str(root)}
    run = subprocess.run([sys.executable, str(AUDIT), "--json"], env=env,
                         capture_output=True, text=True)
    return json.loads(run.stdout)["pending"]


with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / "bin").mkdir(parents=True)
    writer = root / "bin" / "append_event.sh"
    writer.write_text("""#!/usr/bin/env python3
import datetime,json,pathlib,sys,uuid
agent,etype,topic,payload=sys.argv[1:5]
p=pathlib.Path(__file__).resolve().parents[1]/'bus'/'inbox'/f'{agent}.jsonl'
p.parent.mkdir(parents=True,exist_ok=True)
r={'event_id':str(uuid.uuid4()),'ts':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'agent_id':agent,'event_type':etype,'topic':topic,'payload':json.loads(payload)}
with p.open('a',encoding='utf-8') as f:f.write(json.dumps(r,ensure_ascii=False)+'\\n')
""", encoding="utf-8")
    writer.chmod(0o755)

    qtopic = "cash-vendor-policy"
    write_event(root, "Taylor", event("Taylor", "question", qtopic,
                                      "2026-08-13T04:43:24+00:00"))
    assert len(audit(root)) == 1

    write_event(root, "Mike", event("Mike", "decision", "ops-backlog-batch",
                                     "2026-08-15T06:00:00+00:00",
                                     {"resolves": [f"Taylor/{qtopic}"], "evidence": "commit abc"}))
    assert audit(root) == [], audit(root)

    # A newer instance remains open: an older resolver cannot pre-resolve a regression.
    # Keep the regression newer than the old resolver but older than the helper event it is
    # about to create. A fixed future timestamp makes this test depend on wall-clock date.
    recent = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=1)).isoformat()
    write_event(root, "Taylor", event("Taylor", "question", qtopic, recent))
    assert len(audit(root)) == 1

    run = subprocess.run([sys.executable, str(HELPER), f"Taylor/{qtopic}",
                          "--resolution", "keep closed", "--evidence", "BQ freshness query",
                          "--source-topic", "ops-backlog-batch", "--decided-by-user",
                          "--root", str(root)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert "CLOSED" in run.stdout and audit(root) == []

    again = subprocess.run([sys.executable, str(HELPER), f"Taylor/{qtopic}",
                            "--resolution", "same", "--evidence", "same",
                            "--root", str(root)], capture_output=True, text=True)
    assert again.returncode == 0 and "ALREADY_CLOSED" in again.stdout

    # ── rollup_of (2026-08-16, arch-review coord-2026-08-14 required_change #1+#4).
    # Trước fix: bus_question_audit.py KHÔNG hiểu `rollup_of` ⇒ báo cáo tuần "danh sách ĐẦY
    # ĐỦ" mâu thuẫn với gate hàng ngày; và check #5 khớp topic con bằng SUBSTRING ⇒ MỘT event
    # đóng được cả escalation TỔNG trong khi câu hỏi con chưa ai quyết.
    def topics(r):
        return {x["topic"] for x in audit(r)}

    q_ts = "2026-08-16T01:00:00+00:00"
    r_ts = "2026-08-16T02:00:00+00:00"
    write_event(root, "Mike", event("Mike", "question", "rollup-du-con", q_ts,
                                    {"rollup_of": ["r-con-1", "r-con-2"]}))
    write_event(root, "Mike", event("Mike", "question", "rollup-mot-event-nuot-hai", q_ts,
                                    {"rollup_of": ["z-alpha", "z-beta"]}))
    write_event(root, "Mike", event("Mike", "question", "rollup-thieu-1-con", q_ts,
                                    {"rollup_of": ["r-con-1", "r-con-chua-dong"]}))
    assert {"rollup-du-con", "rollup-mot-event-nuot-hai", "rollup-thieu-1-con"} <= topics(root)

    write_event(root, "Wags", event("Wags", "decision", "r-con-1", r_ts))
    write_event(root, "Wags", event("Wags", "decision", "r-con-2", r_ts))
    # MỘT decision duy nhất mà topic CHỨA cả 2 chuỗi con — đúng lỗ substring đã tái lập.
    write_event(root, "Wags", event("Wags", "decision", "z-alpha-and-z-beta-summary", r_ts))
    left = topics(root)
    assert "rollup-du-con" not in left, left
    assert "rollup-mot-event-nuot-hai" in left, left
    assert "rollup-thieu-1-con" in left, left

    # ── split_ref/same_ref (2026-08-16 round 4, arch-review round 3 required_change #3).
    # Nhánh này được thêm vào bus_question_audit.py ở 8e9affc3 với ZERO coverage: reviewer
    # gỡ hẳn `same_ref` khỏi bản copy mà selfcheck vẫn 12/12 PASS. Hai bản (gate hàng ngày
    # ở check #5, báo cáo tuần ở đây) được phép trôi khỏi nhau trong im lặng — đúng thứ
    # required_change #4 sinh ra để chống. Ba ca dưới đây phủ đúng 3 nhánh của same_ref.
    write_event(root, "Mike", event("Mike", "question", "rollup-ref-qualified", q_ts,
                                    {"rollup_of": ["r-con-qual"]}))
    write_event(root, "Mike", event("Mike", "question", "rollup-ref-cheo-agent", q_ts,
                                    {"rollup_of": ["r-con-cheo"]}))
    # Topic TỰ NÓ chứa '/' — lớp câu hỏi đông nhất trên bus thật (`selfcheck-red: ...`).
    slashy = "selfcheck-red: mike/bin/job_cancel_guard_selfcheck.py"
    write_event(root, "Mike", event("Mike", "question", "rollup-topic-co-slash", q_ts,
                                    {"rollup_of": [slashy]}))
    # (1) sub TRẦN đóng bằng resolves QUALIFIED đúng agent ⇒ PHẢI đóng.
    write_event(root, "Wags", event("Wags", "decision", "gop-qual", r_ts,
                                    {"resolves": ["Mike/r-con-qual"]}))
    # (2) sub TRẦN của Mike + resolves khai agent KHÁC ⇒ KHÔNG được đóng (false-CLOSED).
    write_event(root, "Taylor", event("Taylor", "decision", "gop-cheo", r_ts,
                                      {"resolves": ["Taylor/r-con-cheo"]}))
    # (3) topic chứa '/' đóng bằng resolver topic trần ⇒ PHẢI đóng (trước fix: kẹt mãi).
    write_event(root, "Wags", event("Wags", "decision", slashy, r_ts))
    left = topics(root)
    assert "rollup-ref-qualified" not in left, left
    assert "rollup-ref-cheo-agent" in left, left
    assert "rollup-topic-co-slash" not in left, left

print("bus_question_closure_selfcheck: 15/15 PASS")
