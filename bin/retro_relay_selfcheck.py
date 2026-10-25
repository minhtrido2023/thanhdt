#!/usr/bin/env python3
"""Selfcheck relay retro→Trading Daily (retro_escalate.relay_to_user). Stub notify, KHÔNG gửi Discord thật."""
import os, stat, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import retro_escalate as R

T = tempfile.mkdtemp()
stub = os.path.join(T, "stub.sh")
open(stub, "w").write(f'#!/bin/bash\necho "$2|$1" >> {T}/sent.log\n[ -f {T}/fail ] && exit 1\nexit 0\n')
os.chmod(stub, 0o755)
os.environ["RETRO_NOTIFY_CMD"] = stub
os.environ["RETRO_RELAY_STATE"] = os.path.join(T, "st.json")
P = {"summary": "s", "options": ["A) a", "B) b", "c"], "recommendation": "A", "recurring_days": 2}
sent = lambda: open(os.path.join(T, "sent.log")).read().count("\n") if os.path.exists(os.path.join(T, "sent.log")) else 0
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
chk("tổng đúng 2 lần gửi", sent() == 3)  # e1(lỗi)+e1(ok)+e3
print("✅ PASS" if not bad else f"❌ {bad} FAIL"); sys.exit(1 if bad else 0)
