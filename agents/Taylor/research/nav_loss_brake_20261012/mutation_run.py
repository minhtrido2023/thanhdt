#!/usr/bin/env python3
"""Thử mutation cho nav_loss_brake_monitor.py: mỗi mutant = MỘT thay thế chuỗi trên bản sao trong
thư mục tạm, chạy selfcheck trên bản sao đó. Mutant "sống" = selfcheck vẫn 0 FAIL.
VÒNG 3 (đo NAV toàn tài khoản): mọi mutant của bộ máy "phần quản lý" (M12–M17, X05–X08, X21, X28,
X29, N8, B2, R29/R31/R39…) BIẾN MẤT cùng đoạn code đó. Qn = luật giảm tin; Kn/B5/R3/R56 = mục vòng 3.
⚠️ KHÔNG thêm mutant gỡ `if not ctx.is_live` trong send_alert: mutant đó sẽ gọi notify_thread.sh THẬT. Dùng: python3 mutation_run.py   (in bảng; rc=0 luôn — kết quả là bảng)"""
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
 ("M01 so ngưỡng: <= → <", 'hit = v <= th + EPS', 'hit = v < th - EPS'),
 ("M02 bỏ EPS khi so ngưỡng", 'hit = v <= th + EPS', 'hit = v <= th'),
 ("M03 episode dùng nhầm ngưỡng daily", 'res["episode"] = _measured(v, th["episode"], probs, **extra)', 'res["episode"] = _measured(v, th["daily"], probs, **extra)'),
 ("M05 DD_THRESHOLD 0.25 → 0.20", "DD_THRESHOLD = 0.25\n# Sau", "DD_THRESHOLD = 0.20\n# Sau"),
 ("M06 positions: lấy bản ghi account nào cũng được (§12)", 'latest, ts, seen = by_acc[str(account_no)]', 'latest, ts, seen = list(by_acc.values())[-1]'),
 ("M07 bỏ kiểm cờ ước tính", 'if r["nav_is_estimate"]:\n            out.append', 'if False:\n            out.append'),
 ("M07b daily: bỏ kiểm MỐC SO", 'probs + base + flaws(prev))', 'probs + base)'),
 ("M07c bỏ kiểm dòng của phiên (cả ba phanh)", 'base = chain["problems"] + flaws(row)', 'base = list(chain["problems"])'),
 ("B1a giờ chụp: bỏ cận dưới (trước đóng cửa)", "    if t < lo:\n        return (f\"dòng NAV", "    if False:\n        return (f\"dòng NAV"),
 ("B1b giờ chụp: bỏ cận trên (sau mở cửa phiên kế)", "    if t >= hi:", "    if False:"),
 ("M09 không ghi dấu đã gửi", "        _write_json_atomic(ctx.sent_path, sent)\n", "        pass\n"),
 ("M10 gửi lỗi vẫn đánh dấu", '    if not ok:\n        out["send_error"] = detail\n        return out', '    if not ok:\n        out["send_error"] = detail'),
 ("M11 dedupe: gửi lại mọi lần", 'out["new"] = [k for k in keys if k not in sent]', 'out["new"] = list(keys)'),
 ("B6 tạm tính vượt ngưỡng không còn là trạng thái riêng", '_res(BREACH_PROV if hit else UNMEASURABLE, v, th, provisional=True,', '_res(UNMEASURABLE, v, th, provisional=True,'),
 ("M18 thiếu phiên liền trước: bỏ kiểm", 'if prev["date"] < want:', 'if False:'),
 ("M19 mốc so: luôn dòng liền trước", 'prev = next((r for r in cut[:-1] if r["date"] == want), cut[-2])', 'prev = cut[-2]'),
 ("M20 health: bỏ kiểm phiên", 'if st.get("session") != want.isoformat():', 'if False:'),
 ("N2 expected_session: bỏ mốc 21:50", 'if is_session(d) and t >= NAV_EXPECTED_AFTER_ICT:', 'if is_session(d):'),
 ("N10 --date phiên cũ không còn chạy khô", 'if d != expected_session(ctx.now) and not args.write_backdated:', 'if False:'),
 ("M21 bỏ dòng tiền nạp/rút", "ledger, info = build_ledger(rows, flows, base_date, base_nav)", "ledger, info = build_ledger(rows, [], base_date, base_nav)"),
 ("M22 sổ dòng tiền thiếu/lỗi ⇒ im lặng coi như rỗng", '            out["problems"].append(("flows", why + " ⇒ số tạm tính KHÔNG trừ nạp/rút nào"))', '            pass'),
 ("M37 dòng tiền treo: bỏ qua", '        if info["pending"]:\n            out["problems"]', '        if False:\n            out["problems"]'),
 ("K1a thiếu ngưỡng: không kèm số tạm tính", 'res["daily"] = _no_threshold(v, th_err["daily"])', 'res["daily"] = _no_threshold(None, th_err["daily"])'),
 ("Q1 luật giảm tin: bỏ điều kiện 'chỉ cờ ước tính'", '{k for k, _ in problems} == {"estimate"}', 'bool(problems)'),
 ("Q2 luật giảm tin: biên 2,0 → 1,0", "QUIET_ESTIMATE_MARGIN_PP = 2.0\n", "QUIET_ESTIMATE_MARGIN_PP = 1.0\n"),
 ("Q3 luật giảm tin: bỏ EPS ở biên", '> QUIET_ESTIMATE_MARGIN_PP + EPS * 100', '> QUIET_ESTIMATE_MARGIN_PP'),
 ("Q6 phanh quiet vẫn đẩy tin (luật tắt)", 'if res[b]["status"] in ALERTING and not res[b].get("quiet")]', 'if res[b]["status"] in ALERTING]'),
 ("Q8 dòng chụp lệch giờ bị coi là 'ước tính'", 'out.append(("capture", p))', 'out.append(("estimate", p))'),
 ("Q9 thiếu phiên liền trước bị coi là 'ước tính'", 'probs.append(("gap", f"thiếu', 'probs.append(("estimate", f"thiếu'),
 ("Q10 sổ dòng tiền lỗi bị coi là 'ước tính'", 'out["problems"].append(("flows", why', 'out["problems"].append(("estimate", why'),
 ("Q10b dòng tiền treo bị coi là 'ước tính'", 'out["problems"].append(("flows", f"{len(info', 'out["problems"].append(("estimate", f"{len(info'),
 ("Q11 không đọc được vị thế vay bị coi là 'ước tính'", 'probs.append(("broker", f"không kiểm được', 'probs.append(("estimate", f"không kiểm được'),
 ("Q12 episode mở mà hết vị thế bị coi là 'ước tính'", "probs.append((\"broker\", f\"episode {ep['id']} đang mở", "probs.append((\"estimate\", f\"episode {ep['id']} đang mở"),
 ("Q13 bản duyệt mới chưa ack bị coi là 'ước tính'", 'probs.append(("approval",', 'probs.append(("estimate",'),
 ("R56 active_episode bỏ lọc account (§12)", 'if e["account"] == account and covers(e, d):', 'if covers(e, d):'),
 ("K2a phiên của ngày đóng không còn đo với episode", 'or d <= datetime.date.fromisoformat(e["closed_date"])))', 'or d < datetime.date.fromisoformat(e["closed_date"])))'),
 ("K2a2 ngày đóng: hết vị thế vay lại thành 'không đo được'", 'elif not held and ep.get("closed_date") != d.isoformat():', 'elif not held:'),
 ("K2b ack: bỏ kiểm ngày tương lai", '    if d > today:\n        print(f"❌ --ack-approval', '    if False:\n        print(f"❌ --ack-approval'),
 ("K2c ack: bỏ kiểm bản duyệt tồn tại", '    if d not in [a for a, _, _ in approvals]:', '    if False:'),
 ("K2d lệnh tay không gửi dòng báo", 'ok, detail, _sink = send_alert(ctx, text)', 'ok, detail, _sink = True, "", None'),
 ("K2e lượt đo kế không nêu lệnh tay", 'notes = recent_actions(ctx, account, d)', 'notes = []'),
 ("K2f lệnh tay: bỏ lọc account (§12)", 'if rec.get("account") == account and at is not None and at > since:', 'if at is not None and at > since:'),
 ("K2g lệnh tay: nhắc lại mãi (bỏ mốc thời gian)", 'if rec.get("account") == account and at is not None and at > since:', 'if rec.get("account") == account and at is not None:'),
 ("K3 --now trên state sống không bị từ chối", '    if args.now and ctx.state_is_live:', '    if False:'),
 ("K4 OSError ở state-dir không còn đi đường crashed", '    except OSError as exc:\n        # không mở', '    except ZeroDivisionError as exc:\n        # không mở'),
 ("K5 sink trên state sống vẫn tính đã gửi", '        if ctx.is_live:\n            return False, (f"tin CHỈ', '        if False:\n            return False, (f"tin CHỈ'),
 ("K6 health-line: phanh chạm vẫn rc=1", 'rc = HEALTH_RC_BREACH', 'rc = 1'),
 ("K11a so mã gói vay theo kiểu (chuỗi '1840' trượt)", 'if _pkg_id(p.get("loanPackageId")) == pkg:', 'if p.get("loanPackageId") == pkg:'),
 ("K11b positions thiếu khoá ⇒ coi là rỗng", 'out[str(rec.get("account_no"))] = (pos if isinstance(pos, list) else None,', 'out[str(rec.get("account_no"))] = (pos if isinstance(pos, list) else [],'),
 ("K11c không kiểm giờ chụp dòng điểm vào", '        probs += flaws(e)', '        pass'),
 ("K11d không in ghi chú (đỉnh chưa phải giá chốt)", "note = f\" · ⚠ {r['note']}\" if r.get(\"note\") else \"\"", 'note = ""'),
 ("B5a ngày duyệt không đọc được ⇒ không thử phiên kế", '                unreadable.append((c, why))\n', '                unreadable.append((c, why))\n                break\n'),
 ("B5b không lấy điểm vào XẤU hơn", 'v = min(row["unit_price"] / e["unit_price"] - 1 for e in entries)', 'v = row["unit_price"] / entries[0]["unit_price"] - 1'),
 ("B5c câu lý do không đọc danh sách bản duyệt", '            seen = guard["approvals"]', '            seen = []'),
 ("R3 khoá số lệch câu chữ vẫn nhận", '        if any(abs(x - v) > EPS for x in in_text):\n            return None, (f"{where}: khoá số', '        if False:\n            return None, (f"{where}: khoá số'),
 ("G8 positions chụp trước đóng cửa vẫn nhận", 'if is_session(date) and (t is None or t < datetime.datetime.combine(date, SESSION_CLOSE_ICT)):', 'if False:'),
 ("D14 bản duyệt thu hồi vẫn mở episode", 'return "revoked" in rec and rec.get("revoked") not in NOT_REVOKED', 'return False'),
 ("G2 bản duyệt mới: không lấy số xấu nhất", '            v = min(v, v_alt)             # số đem so ngưỡng', '            pass             # số đem so ngưỡng'),
 ("G24 openQuantity=0 vẫn là vị thế", 'return [p for p in latest if float(p.get("openQuantity") or 0) > 0], ts, None', 'return [p for p in latest if float(p.get("openQuantity") or 0) >= 0], ts, None'),
 ("X5 sổ episode hỏng làm hỏng cả lượt", '    except (OSError, ValueError) as exc:   # sổ episode hỏng', '    except ZeroDivisionError as exc:   # sổ episode hỏng'),
]
alive = []
for name, a, b in M:
    if SRC.count(a) != 1:
        print(f"{name:<58} LỖI HARNESS: chuỗi gốc xuất hiện {SRC.count(a)} lần")
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
    try:
        r = subprocess.run([sys.executable, os.path.join(tb, "nav_loss_brake_monitor_selfcheck.py")],
                           capture_output=True, text=True, env=env, timeout=300)
        rc, stdout = r.returncode, r.stdout
    except subprocess.TimeoutExpired:
        rc, stdout = 124, "  ✗ (selfcheck treo quá 300s)"
    last = (stdout.strip().splitlines() or ["(không output)"])[-1]
    killed = rc != 0
    fails = [x.strip()[2:28] for x in stdout.splitlines() if x.strip().startswith("✗")]
    how = " | ".join(fails[:4]) or f"(nổ rc={rc}, không assertion nào kịp chạy)"
    print(f"{name:<58} {'CHẾT' if killed else 'SỐNG'}  {how if killed else last}")
    if not killed:
        alive.append(name)
    shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{len(M) - len(alive)}/{len(M)} mutant chết. Còn sống: {alive or 'không'}")
