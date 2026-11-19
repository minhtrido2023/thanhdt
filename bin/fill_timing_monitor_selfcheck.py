#!/usr/bin/env python3
"""Selfcheck fill_timing_monitor. Chạy: env -u TZ python3 ...; TZ=Asia/Tokyo ...; TZ=America/New_York ...
Cần dữ liệu thật (dnse_raw + journal) + CSV open của job 052911 để tái lập số; phần còn lại dùng fixture tổng hợp.
"""
import hashlib, json, os, subprocess, sys, tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd
import fill_timing_monitor as f

HERE = Path(__file__).resolve().parent
RES = Path(os.environ.get("FTM_RESEARCH_DIR", "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/fill_timing_real_fills_20261119"))
PREREG = HERE.parent / "agents/Taylor/research/fill_timing_monitor_20261119/PREREG.md"
n_pass = 0


def ok(cond, msg):
    global n_pass
    if not cond:
        print("FAIL:", msg); sys.exit(1)
    n_pass += 1; print("PASS:", msg)


def fixture(tmp, buy_bps, n_weeks=9, per_week=4, other_account=False, dup=False, side_bps=0.0, journals=True):
    """n_weeks tuần × per_week mã (thứ Ba mỗi tuần từ 2026-09-08). Open=Close=Price=10000."""
    tmp = Path(tmp); log = tmp / "logs"; log.mkdir(parents=True, exist_ok=True)
    recs, jr, opens = [], [], []
    oid = 1
    for w in range(n_weeks):
        d = (datetime(2026, 9, 8) + timedelta(weeks=w)).strftime("%Y-%m-%d")
        for k in range(per_week):
            sym = "S%02d" % k
            opens.append((sym, d, 10000, 10000, 10000))
            for side, bps in (("NB", buy_bps), ("NS", side_bps)):
                o = dict(id=oid, accountNo="0002023347", fillQuantity=100, transDate=d, symbol=sym, side=side,
                         averagePrice=10000 * (1 + bps / 1e4), orderType="LO")
                recs.append(o)
                if dup: recs.append(dict(o))
                jr.append(dict(event="PLACE", parent_id="p%d" % oid, child_oid=str(oid), ts=d, note="adp; hyb:blk"))
                oid += 1
    if other_account:
        for k in range(50):
            recs.append(dict(id=900000 + k, accountNo="0009999999", fillQuantity=100000, transDate="2026-09-08", symbol="ZZZ", side="NB", averagePrice=99999))
    (log / "dnse_raw_2026-09-30.jsonl").write_text("\n".join(json.dumps({"kind": "orders", "payload": {"orders": [r]}}) for r in recs) + "\n")
    if journals:
        pd.DataFrame(jr).to_csv(log / "exec_SpaceX_2026-09-30_journal.csv", index=False)
    pd.DataFrame(opens, columns=["ticker", "d", "Open", "Close", "Price"]).drop_duplicates(["ticker", "d"]).to_csv(tmp / "open.csv", index=False)
    fake = tmp / "fake_notify.sh"; out = tmp / "notify_out.txt"
    fake.write_text('#!/bin/bash\nprintf "%s|%s\\n" "$2" "$1" >> ' + str(out) + "\n"); fake.chmod(0o755)
    return log, tmp / "open.csv", str(fake), out, tmp / "state.json"


def run(tmp, today, **kw):
    log, oc, fake, out, state = fixture(tmp, **kw) if not (Path(tmp) / "open.csv").exists() else (Path(tmp) / "logs", Path(tmp) / "open.csv", str(Path(tmp) / "fake_notify.sh"), Path(tmp) / "notify_out.txt", Path(tmp) / "state.json")
    argv = ["--log-dir", str(log), "--open-csv", str(oc), "--notify-cmd", fake, "--state", str(state)]
    if today: argv += ["--today", today]
    rc = f.main(argv)
    msgs = out.read_text().splitlines() if out.exists() else []
    return rc, msgs, state


# 1) Tái lập số job 052911 trên dữ liệu thật
M = f.load_orders(f.DEFAULT_LOG_DIR, "2026-11-17")
U, pend = f.build_units(M, pd.read_csv(RES / "bq_open.csv"))
res = f.evaluate(U)
ok(pend == 0, "0 lệnh thiếu open (đúng job 052911)")
ok((res["BUY"]["n_orders"], res["BUY"]["n_units"]) == (70, 22), "BUY HYB_IN_BLOCK 70 lệnh / 22 mã-ngày")
ok((res["SELL"]["n_orders"], res["SELL"]["n_units"]) == (250, 115), "SELL HYB_IN_BLOCK 250 lệnh / 115 mã-ngày")
R = pd.read_csv(RES / "results_bps.csv")
rb = R[(R.side == "BUY") & (R.group == "HYB_IN_BLOCK")].iloc[0]; rs = R[(R.side == "SELL") & (R.group == "HYB_IN_BLOCK")].iloc[0]
ok(abs(U[U.side == "BUY"].bps.mean() - rb.mean_bps) < 1e-6 and abs(round(U[U.side == "BUY"].bps.mean(), 1) + 56.1) < 1e-9, "BUY mean = results_bps.csv = -56,1")
ok(abs(res["SELL"]["mean_bps"] - rs.mean_bps) < 1e-6 and round(res["SELL"]["mean_bps"], 1) == -6.1, "SELL mean = results_bps.csv = -6,1")
ok(abs(res["SELL"]["ci_lo"] - rs.ci_lo) < 1e-6 and abs(res["SELL"]["ci_hi"] - rs.ci_hi) < 1e-6, "SELL CI95 bootstrap khối tuần trùng analyze.py")
ok(not res["BUY"]["enough_N"] and "mean_bps" not in res["BUY"] and not res["alert"], "BUY chưa đủ N (22/4) => không mean/kết luận/alert")

# 2) Nguồn ngày bật cờ + PREREG
g = subprocess.run(["git", "-C", str(HERE), "show", "-s", "--format=%cs", f.HYBRID_FLAG_COMMIT], capture_output=True, text=True)
ok(g.returncode == 0 and g.stdout.strip() == f.HYBRID_ON_DATE, f"HYBRID_ON_DATE khớp ngày commit {f.HYBRID_FLAG_COMMIT} ({g.stdout.strip()})")
txt = PREREG.read_text()
ok(hashlib.md5(txt.encode()).hexdigest() == (PREREG.parent / "PREREG.md5").read_text().strip(), "PREREG md5 khớp file .md5")
ok(all(s in txt for s in (f.HYBRID_ON_DATE, f.HYBRID_FLAG_COMMIT, ">=30", ">=8", "+22", str(f.BOOT_SEED), str(f.BOOT_N))), "hằng số trong code đều có trong PREREG")

# 3) Chưa đủ N không kết luận / ngưỡng +22 với dữ liệu tổng hợp (E2E)
with tempfile.TemporaryDirectory() as t:
    rc, msgs, _ = run(t, "2026-11-17", buy_bps=100.0, n_weeks=7, per_week=4)  # 28 đơn vị, 7 tuần
    ok(rc == 0 and msgs == [], "28 đơn vị/7 tuần BUY +100bps => không alert, im lặng (thứ Ba)")
with tempfile.TemporaryDirectory() as t:
    rc, msgs, _ = run(t, "2026-11-17", buy_bps=100.0, n_weeks=7, per_week=5)  # 35 đơn vị, 7 tuần
    ok(rc == 0 and msgs == [], "35 đơn vị nhưng 7 tuần (<8) => vẫn chưa đủ N, không alert")
with tempfile.TemporaryDirectory() as t:
    rc, msgs, _ = run(t, "2026-11-16", buy_bps=100.0, n_weeks=8, per_week=3)  # 24 đơn vị, 8 tuần, thứ Hai
    ok(rc == 0 and len(msgs) == 1 and "chưa đủ N" in msgs[0] and "N=24/30" in msgs[0] and "mean" not in msgs[0], "24 đơn vị/8 tuần thứ Hai: 1 dòng tiến độ, không mean")
for bps, expect in ((30.0, True), (22.5, True), (22.0, False), (21.0, False), (-50.0, False)):
    with tempfile.TemporaryDirectory() as t:
        rc, msgs, _ = run(t, "2026-11-17", buy_bps=bps, n_weeks=9, per_week=4)  # 36 đơn vị, 9 tuần
        al = [m for m in msgs if "đề xuất rollback" in m.lower() or "ĐỀ XUẤT rollback" in m]
        ok((rc == 2) == expect and bool(al) == expect, f"đủ N, BUY {bps:+.1f} bps => alert={expect} (rc={rc})")
        if expect:
            ok("user quyết" in al[0] and "KHÔNG tự đổi" in al[0] and "ngày giảm" in al[0] and "không dùng làm bộ lọc live" in al[0], "alert nêu 'user quyết' + ex-post mô tả")

# 4) Idempotent (cùng ngày thứ Hai, alert + weekly)
with tempfile.TemporaryDirectory() as t:
    rc1, m1, st = run(t, "2026-11-16", buy_bps=40.0, n_weeks=9, per_week=4)
    rc2, m2, _ = run(t, "2026-11-16", buy_bps=40.0, n_weeks=9, per_week=4)
    ok(len(m1) == 2 and m1 == m2 and rc1 == rc2 == 2, "chạy lại cùng ngày không post trùng (2 tin: alert + weekly)")
    ok(not [p for p in Path(st).parent.iterdir() if p.name.startswith(".ftm_")], "state ghi nguyên tử, không để file tmp")
    rc3, m3, _ = run(t, "2026-11-23", buy_bps=40.0, n_weeks=9, per_week=4)
    ok(len(m3) == 4, "tuần ISO kế tiếp: alert + weekly mới (4 tin tích luỹ)")

# 5) Lọc account + dedupe
with tempfile.TemporaryDirectory() as t:
    log, oc, fake, out, state = fixture(t, buy_bps=0.0, other_account=True, dup=True)
    M2 = f.load_orders(log, "2026-11-17")
    ok(set(M2.account) == {"SpaceX"} and len(M2) == 9 * 4 * 2, "account lạ bị loại; bản ghi trùng (account,id) dedupe")

# 6) Fail-closed
with tempfile.TemporaryDirectory() as t:
    (Path(t) / "logs").mkdir()
    fake = Path(t) / "fn.sh"; fake.write_text('#!/bin/bash\nprintf "%s\\n" "$1" >> ' + t + "/o.txt\n"); fake.chmod(0o755)
    rc = f.main(["--log-dir", t + "/logs", "--open-csv", "/nonexistent", "--notify-cmd", str(fake), "--state", t + "/s.json", "--today", "2026-11-17"])
    o = (Path(t) / "o.txt").read_text()
    ok(rc == 1 and "monitor không chạy được vì" in o and "dnse_raw" in o, "thiếu dnse_raw => rc=1 + post lý do thật")
with tempfile.TemporaryDirectory() as t:
    log, oc, fake, out, state = fixture(t, buy_bps=0.0, journals=False)
    rc = f.main(["--log-dir", str(log), "--open-csv", str(oc), "--notify-cmd", fake, "--state", str(state), "--today", "2026-11-17"])
    o = out.read_text()
    ok(rc == 1 and "journal" in o and "không chạy được vì" in o, "thiếu journal => rc=1 + lý do nêu journal")
    rc = f.main(["--log-dir", str(log), "--open-csv", str(oc), "--notify-cmd", fake, "--state", str(state), "--today", "2026-11-17"])
    ok(len(out.read_text().splitlines()) == 1, "thông báo lỗi cũng idempotent (cùng ngày+lý do)")

# 7) Ngày anchor ICT, không theo TZ host
with tempfile.TemporaryDirectory() as t:
    log, oc, fake, out, state = fixture(t, buy_bps=0.0)
    # không truyền --today: ngày chạy phải = ngày ICT tính độc lập từ UTC
    exp = (datetime.now(timezone.utc) + timedelta(hours=7)).strftime("%Y-%m-%d")
    f.main(["--log-dir", str(log), "--open-csv", str(oc), "--notify-cmd", fake, "--state", str(state)])
    ok(json.load(open(state))["last_run"]["today"] == exp, f"ngày chạy = ICT ({exp}) với TZ={os.environ.get('TZ', '<unset>')}")

print(f"ALL PASS ({n_pass})")
