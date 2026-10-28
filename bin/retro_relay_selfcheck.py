#!/usr/bin/env python3
"""Selfcheck relay retro→Trading Daily (retro_escalate.relay_to_user). Stub notify, KHÔNG gửi Discord thật."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import retro_escalate as R

T = tempfile.mkdtemp()
stub = os.path.join(T, "stub.sh")
open(stub, "w").write(f'#!/bin/bash\necho "$2|$1" >> {T}/sent.log\n[ -f {T}/fail ] && exit 1\nexit 0\n')
os.chmod(stub, 0o755)
os.environ["RETRO_NOTIFY_CMD"] = stub
os.environ["RETRO_RELAY_STATE"] = os.path.join(T, "st.json")
P = {"summary": "s", "options": ["A) a", "B) b", "c"], "recommendation": "A", "recurring_days": 2}
sent = lambda: open(os.path.join(T, "sent.log")).read().count("trading_daily|")
bad = 0
def chk(name, ok):
    global bad
    print(("  PASS  " if ok else "  FAIL  ") + name); bad += not ok

open(os.path.join(T, "fail"), "w").close()
chk("notify lỗi ⇒ False, không raise, không state", R.relay_to_user("e1", "t1", P) is False and not os.path.exists(os.environ["RETRO_RELAY_STATE"]))
os.remove(os.path.join(T, "fail"))
chk("retry sau lỗi ⇒ gửi", R.relay_to_user("e1", "t1", P) is True)
chk("cùng event_id ⇒ không gửi lại", R.relay_to_user("e1", "t1", P) is False)
chk("event mới cùng topic cùng ngày ⇒ không gửi lại", R.relay_to_user("e2", "t1", P) is False)
chk("topic khác ⇒ gửi", R.relay_to_user("e3", "t2", P) is True)
chk("đích = trading_daily (tên, không ID trần)", open(os.path.join(T, "sent.log")).read().splitlines()[0].startswith("trading_daily|"))
m = R.format_relay("retro-pattern-recurring-x", P)
chk("message đủ options A/B/C + đề xuất + cách trả lời", all(s in m for s in ("A) a", "B) b", "C) c", "Đề xuất: A", "Trả lời")))
chk("tổng 3 lần gọi notify (e1 lỗi, e1 ok, e3)", sent() == 3)

# (a) _new_event_id bind offset
import json
os.makedirs(os.path.join(R.ROOT, "bus", "inbox"), exist_ok=True)
AG = "RelaySelfcheck"
ib = R._inbox_path(AG)
try:
    open(ib, "w").write(json.dumps({"event_type": "question", "topic": "tt", "event_id": "OLD"}) + "\n")
    off = R._inbox_size(AG)
    chk("_new_event_id: không ghi mới ⇒ None (không nhặt câu cũ)", R._new_event_id(AG, "tt", off) is None)
    open(ib, "a").write(json.dumps({"event_type": "question", "topic": "tt", "event_id": "NEW"}) + "\n")
    chk("_new_event_id: lấy đúng câu mới", R._new_event_id(AG, "tt", off) == "NEW")
    # (b) main() end-to-end (bus riêng của worktree, bus-root tmp)
    import io, contextlib
    os.makedirs(os.path.join(T, "mike", "bus", "inbox"), exist_ok=True)
    os.environ["RETRO_RELAY_STATE"] = os.path.join(T, "st2.json")
    open(os.path.join(T, "sent.log"), "w").close()
    argv = ["--pattern", "relaysc-pattern", "--days", "2", "--agent", AG, "--bus-root", T, "--payload", json.dumps(P)]
    with contextlib.redirect_stdout(io.StringIO()):
        rc1 = R.main(argv); rc2 = R.main(argv)
    chk("main e2e: rc=0 và rerun cùng ngày chỉ 1 lần notify", rc1 == 0 and rc2 == 0 and sent() == 1)
    # (c) timeout
    open(os.path.join(T, "slow.sh"), "w").write("#!/bin/bash\nsleep 5\n"); os.chmod(os.path.join(T, "slow.sh"), 0o755)
    os.environ["RETRO_NOTIFY_CMD"] = os.path.join(T, "slow.sh"); os.environ["RETRO_NOTIFY_TIMEOUT"] = "1"
    os.environ["RETRO_RELAY_STATE"] = os.path.join(T, "st3.json")
    chk("timeout ⇒ False, không state", R.relay_to_user("e9", "t9", P) is False and not os.path.exists(os.environ["RETRO_RELAY_STATE"]))
    # (d) state hỏng
    os.environ["RETRO_NOTIFY_CMD"] = stub
    open(os.environ["RETRO_RELAY_STATE"], "w").write("{broken")
    ok = R.relay_to_user("e10", "t10", P) is True
    chk("state hỏng ⇒ vẫn gửi + ghi lại JSON hợp lệ", ok and "event:e10" in json.load(open(os.environ["RETRO_RELAY_STATE"])))
finally:
    for f in (ib,):
        try: os.remove(f)
        except OSError: pass
print("✅ PASS" if not bad else f"❌ {bad} FAIL"); sys.exit(1 if bad else 0)
