#!/usr/bin/env python3
"""Theo dõi lô cổ phiếu QUYỀN MUA MBB (SpaceX 110cp / ZaloPay 20cp, journal MBB-RIGHTS-2026-08-28).

Bối cảnh: user duyệt A1 19/11/2026 22:04 ICT — chờ broker cho BÁN lô này (tradeQuantity == openQuantity)
rồi mới chuyển nhãn CORP_ACTION→PARK (patch ở nhánh session/15727-a, arch-review NEEDS_CHANGES) và đưa
lệnh bán MBB vào plan để user duyệt. READ-ONLY: chỉ đọc dnse_raw, chỉ gửi cảnh báo, không đổi gì.
Báo 1 lần khi bán được (state), và nhắc 1 lần từ 28/11 nếu vẫn kẹt (khai báo lệch hết hạn 30/11).
"""
import datetime as dt
import glob
import json
import os
import subprocess
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ROOT = "/home/trido/thanhdt/WorkingClaude"
STATE = os.path.join(ROOT, "mike", "state", "mbb_rights_watch.json")
THREAD = "trading_daily"  # tên trong kb/discord_channels.json — notify_thread.sh tự resolve (discord-id-gate)
LOCKED = {"SpaceX": 110, "ZaloPay": 20}


def latest_mbb():
    files = sorted(glob.glob(os.path.join(ROOT, "data", "execution_logs", "dnse_raw_*.jsonl")))
    out = {}
    for f in reversed(files):
        last = {}
        for line in open(f, encoding="utf-8"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("kind") != "positions":
                continue
            for p in r["payload"].get("positions", []):
                if p.get("symbol") == "MBB":
                    last[r["account_label"]] = (p["openQuantity"], p.get("tradeQuantity"), r["ts"])
        for a, v in last.items():
            out.setdefault(a, v)
        if len(out) == len(LOCKED):
            break
    return out


def notify(msg):
    subprocess.run(["bash", os.path.join(ROOT, "mike", "bin", "notify_thread.sh"), msg, THREAD], check=False)


def main():
    today = dt.datetime.now(ICT).date()
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    pos = latest_mbb()
    if len(pos) < len(LOCKED):
        print(f"[mbb-watch] thiếu dữ liệu positions: {pos}")
        return 1
    free = {a: v for a, v in pos.items() if v[1] is not None and v[1] >= v[0]}
    desc = "; ".join(f"{a}: mở {v[0]} / bán được {v[1]}" for a, v in pos.items())
    print(f"[mbb-watch] {today} {desc}")
    if len(free) == len(LOCKED) and not st.get("released_alerted"):
        notify("⚠️ MBB quyền mua đã BÁN ĐƯỢC (" + desc + "). Theo quyết định A1 19/11: Mike chuyển nhãn "
               "CORP_ACTION→PARK (patch nhánh session/15727-a cần xử lý NEEDS_CHANGES) và trình plan bán MBB để user duyệt.")
        st["released_alerted"] = today.isoformat()
    elif not free and today >= dt.date(2026, 11, 28) and not st.get("stale_alerted"):
        notify("⏰ MBB quyền mua vẫn chưa bán được (" + desc + "); khai báo lệch known_position_discrepancies "
               "hết hạn 30/11 — cần Mike/user xử lý (hỏi DNSE ngày niêm yết, gia hạn khai báo).")
        st["stale_alerted"] = today.isoformat()
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    json.dump(st, open(tmp, "w"))
    os.replace(tmp, STATE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
