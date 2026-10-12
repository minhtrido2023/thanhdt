#!/usr/bin/env python3
"""Thử mutation cho nav_loss_brake_monitor.py: mỗi mutant = MỘT thay thế chuỗi trên bản sao trong
thư mục tạm, chạy selfcheck trên bản sao đó. Mutant "sống" = selfcheck vẫn 0 FAIL.
Dùng: python3 mutation_run.py   (in bảng; rc=0 luôn — kết quả là bảng)"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "bin"))
SRC = open(os.path.join(BIN, "nav_loss_brake_monitor.py"), encoding="utf-8").read()
WC_ROOT = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); "
                          "from wc_paths import find_wc_root; print(find_wc_root(%r))"
                          % (BIN, os.path.join(BIN, "x.py"))],
                         capture_output=True, text=True).stdout.strip()

M = [
 ("M01 daily: <= → <", 'BREACH if v <= th["daily"] + EPS else OK', 'BREACH if v < th["daily"] - EPS else OK'),
 ("M02 daily: bỏ EPS", 'v <= th["daily"] + EPS', 'v <= th["daily"]'),
 ("M03 drawdown: <= → <", 'BREACH if v <= -DD_THRESHOLD + EPS else OK', 'BREACH if v < -DD_THRESHOLD - EPS else OK'),
 ("M04 episode: <= → <", 'BREACH if v <= th["episode"] + EPS else OK', 'BREACH if v < th["episode"] - EPS else OK'),
 ("M05 DD_THRESHOLD 0.25 → 0.20", "DD_THRESHOLD = 0.25\n# Sau", "DD_THRESHOLD = 0.20\n# Sau"),
 ("M06 bỏ lọc account ở raw_positions", 'if str(rec.get("account_no")) != str(account_no):\n                continue', 'if False:\n                continue'),
 ("M07 daily: bỏ kiểm cờ ước tính", 'elif row["nav_is_estimate"] or prev["nav_is_estimate"]:', 'elif False:'),
 ("M08 drawdown: bỏ kiểm cờ ước tính", '    if row["nav_is_estimate"]:\n        res["drawdown"]', '    if False:\n        res["drawdown"]'),
 ("M09 không ghi dấu đã gửi", "    _write_json_atomic(ctx.sent_path, sent)\n", "    pass\n"),
 ("M10 gửi lỗi vẫn đánh dấu", '    if not ok:\n        out["send_error"] = detail\n        return out', '    if not ok:\n        out["send_error"] = detail'),
 ("M11 dedupe: gửi lại mọi lần", "new = [k for k in keys if k not in sent]", "new = list(keys)"),
 ("M12 basis luôn total", '"managed" if profile["excluded_tickers"] else "total", "ledger": None', '"total", "ledger": None'),
 ("M13 bẫy sleeve: bỏ điều kiện đã khai", "if why and cur not in declared:", "if why:"),
 ("M14 bẫy sleeve: tắt hẳn", "if why and cur not in declared:", "if False:"),
 ("M15 bẫy giá: bỏ số mũ n phiên", "(1 - EXCL_PRICE_BAND) ** n <= ratio <= (1 + EXCL_PRICE_BAND) ** n", "(1 - EXCL_PRICE_BAND) <= ratio <= (1 + EXCL_PRICE_BAND)"),
 ("M16 bẫy KL: tắt", "if abs(qa - qb) > 1e-6:\n                why.append", "if False:\n                why.append"),
 ("M17 bẫy lịch corp-action: tắt", "            for e in events:\n                amt", "            for e in []:\n                amt"),
 ("M18 thiếu phiên liền trước: bỏ kiểm", 'elif prev["date"] < want:', 'elif False:'),
 ("M19 mốc so: luôn dòng liền trước", 'prev = next((r for r in cut[:-1] if r["date"] == want), cut[-2])', 'prev = cut[-2]'),
 ("M20 health: bỏ kiểm phiên", 'if st.get("session") != want.isoformat():', 'if False:'),
 ("M21 bỏ dòng tiền nạp/rút", "total, info = build_ledger(rows, flows, base_date, base_nav)", "total, info = build_ledger(rows, [], base_date, base_nav)"),
 ("M22 sổ dòng tiền thiếu ⇒ coi như rỗng", "flows = load_flows(account, flows_path=ctx.flows_path, require_file=True, today=today)", "flows = load_flows(account, flows_path=ctx.flows_path, require_file=False, today=today)"),
 ("M23 bản duyệt thu hồi vẫn mở", 'if rec.get("revoked"):', 'if False:'),
 ("M24 mở episode không cần vị thế gói vay", "        if not held:\n            notes.append(f\"có bản duyệt margin {d} nhưng broker KHÔNG", "        if False:\n            notes.append(f\"có bản duyệt margin {d} nhưng broker KHÔNG"),
 ("M25 vị thế gói vay không episode: im", "        if held:\n            res[\"episode\"] = _res(\n                UNMEASURABLE", "        if False:\n            res[\"episode\"] = _res(\n                UNMEASURABLE"),
 ("M26 thiếu ngưỡng ⇒ mặc định −5%", '        errors["daily"] = (f"{rules_path}: risk_circuit_breakers.daily_loss_limit_pct phải là số "\n                           f"trong (−1, 0), đọc được {v!r}")', '        th["daily"] = -0.05'),
 ("M27 lý do thiếu dòng: bỏ đọc file chặn", "    if os.path.exists(block):", "    if False:"),
 ("M28 chuỗi mã loại trừ: cho ghi đè", 'merged = sorted(old + [r for r in rows if r["date"] not in have]', 'merged = sorted([r for r in old if r["date"] not in {x["date"] for x in rows}] + [r for r in rows]'),
 ("M29 active_nav sai ngày vẫn dùng", 'if an.get("account") != account or an.get("computed_at") != date.isoformat():', 'if False:'),
 ("M30 không so KL hai nguồn", "if abs(float(p.get(\"qty\") or 0) - qty) > 1e-6:", "if False:"),
 ("M31 từ chối gửi thật khi không live: bỏ", "    if not ctx.is_live:\n        return False,", "    if False:\n        return False,"),
 ("M32 expected_session: dùng ngày UTC", "d = now.astimezone(ICT).date() if now.tzinfo else now.date()", "d = now.astimezone(datetime.timezone.utc).date() if now.tzinfo else now.date()"),
 ("M33 NAV_EXPECTED_AFTER 21:50 → 00:00", "NAV_EXPECTED_AFTER_ICT = datetime.time(21, 50)", "NAV_EXPECTED_AFTER_ICT = datetime.time(0, 0)"),
 ("M34 episode: điểm vào = ngày mở (không phải phiên trước)", "ref = [x for x in dates if x < d]", "ref = [x for x in dates if x <= d]"),
 ("M35 đóng episode không cần lý do", 'if not (closed_by or "").strip() or not (reason or "").strip():', 'if False:'),
 ("M36 episode đã đóng vẫn tính", 'if e.get("closed_date") is None or d < datetime.date.fromisoformat(e["closed_date"]):\n            return e', 'if True:\n            return e'),
 ("M37 dòng tiền treo: bỏ qua", '        if info["pending"]:\n            raise ValueError(f"{len(info[\'pending\'])} dòng tiền TREO trong', '        if False:\n            raise ValueError(f"{len(info[\'pending\'])} dòng tiền TREO trong'),
 ("M38 tin cảnh báo: bỏ lệnh BOT_STOP", "lines.append(f\"`touch {os.path.join(WC_ROOT, 'data', 'BOT_STOP')}`\")", "pass"),
 ("M39 EXCL_PRICE_BAND 7,5% → 30%", "EXCL_PRICE_BAND = 0.075", "EXCL_PRICE_BAND = 0.30"),
 ("M41 bỏ đối chiếu total_nav hai file", "    if abs(gap) > NAV_MATCH_TOL:", "    if False:"),
 ("M42 NAV_MATCH_TOL 0,1% → 0,01%", "NAV_MATCH_TOL = 0.001", "NAV_MATCH_TOL = 0.0001"),
 ("M40 chưa có chuỗi mã loại trừ ⇒ lặng lẽ coi 0", "        if not excl:\n            raise ValueError", "        if False:\n            raise ValueError"),
]
alive = []
for name, a, b in M:
    if SRC.count(a) != 1:
        print(f"{name:<52} LỖI HARNESS: chuỗi gốc xuất hiện {SRC.count(a)} lần")
        alive.append(name + " (harness)")
        continue
    tmp = tempfile.mkdtemp(prefix="lossbrake_mut_")
    tb = os.path.join(tmp, "bin")
    os.makedirs(tb)
    for f in ("account_cash_flows.py", "nav_unit_ledger.py", "wc_paths.py",
              "nav_loss_brake_monitor_selfcheck.py"):
        shutil.copy(os.path.join(BIN, f), tb)
    open(os.path.join(tb, "nav_loss_brake_monitor.py"), "w", encoding="utf-8").write(SRC.replace(a, b))
    env = dict(os.environ, WC_ROOT=WC_ROOT)
    env.pop("MIKE_LOSS_BRAKE_ALERT_SINK", None)
    r = subprocess.run([sys.executable, os.path.join(tb, "nav_loss_brake_monitor_selfcheck.py")],
                       capture_output=True, text=True, env=env, timeout=600)
    last = (r.stdout.strip().splitlines() or ["(không output)"])[-1]
    killed = r.returncode != 0
    fails = [x.strip()[2:28] for x in r.stdout.splitlines() if x.strip().startswith("✗")]
    print(f"{name:<52} {'CHẾT' if killed else 'SỐNG'}  {' | '.join(fails[:4]) if killed else last}")
    if not killed:
        alive.append(name)
    shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{len(M) - len(alive)}/{len(M)} mutant chết. Còn sống: {alive or 'không'}")
