#!/usr/bin/env python3
"""Thử mutation cho nav_loss_brake_monitor.py: mỗi mutant = MỘT thay thế chuỗi trên bản sao trong
thư mục tạm, chạy selfcheck trên bản sao đó. Mutant "sống" = selfcheck vẫn 0 FAIL.
Nhãn Xnn = mutant arch-reviewer vòng 1 báo còn sống (dựng lại theo mô tả); Bn/Nn = mutant phủ
mục sửa vòng 2. Dùng: python3 mutation_run.py   (in bảng; rc=0 luôn — kết quả là bảng)"""
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
 ("M02/X43/X44 bỏ EPS", 'hit = v <= th + EPS', 'hit = v <= th'),
 ("M03 episode dùng nhầm ngưỡng daily", 'res["episode"] = _measured(v, th["episode"], probs, **extra)', 'res["episode"] = _measured(v, th["daily"], probs, **extra)'),
 ("M05 DD_THRESHOLD 0.25 → 0.20", "DD_THRESHOLD = 0.25\n# Sau", "DD_THRESHOLD = 0.20\n# Sau"),
 ("M06 positions: lấy bản ghi account nào cũng được", 'latest, ts = by_acc[str(account_no)]', 'latest, ts = list(by_acc.values())[-1]'),
 ("M07 bỏ kiểm cờ ước tính (mọi phanh)", 'if r["nav_is_estimate"]:\n            out.append', 'if False:\n            out.append'),
 ("M07b daily: bỏ kiểm MỐC SO", 'probs + row_flaws + flaws(prev))', 'probs + row_flaws)'),
 ("M07c daily: bỏ kiểm dòng của phiên", 'probs + row_flaws + flaws(prev))', 'probs + flaws(prev))'),
 ("M08 drawdown: bỏ kiểm dòng của phiên", '_measured(v, -DD_THRESHOLD, late + row_flaws,', '_measured(v, -DD_THRESHOLD, late,'),
 ("X02 episode: bỏ kiểm dòng của phiên (cờ ước tính)", 'probs = late + row_flaws\n    if held is None:', 'probs = list(late)\n    if held is None:'),
 ("M09 không ghi dấu đã gửi", "        _write_json_atomic(ctx.sent_path, sent)\n", "        pass\n"),
 ("M10 gửi lỗi vẫn đánh dấu", '    if not ok:\n        out["send_error"] = detail\n        return out', '    if not ok:\n        out["send_error"] = detail'),
 ("M11 dedupe: gửi lại mọi lần", 'out["new"] = [k for k in keys if k not in sent]', 'out["new"] = list(keys)'),
 ("M12 basis luôn total", '"managed" if profile["excluded_tickers"] else "total", "ledger": None', '"total", "ledger": None'),
 ("M13 bẫy sleeve: bỏ điều kiện đã khai", "if why and cur not in declared:", "if why:"),
 ("M14 bẫy sleeve: tắt hẳn", "if why and cur not in declared:", "if False:"),
 ("X05 bẫy chỉ chặn đúng một ngày", 'bad = {k: v for k, v in chain["unexplained"].items() if k <= d}', 'bad = {k: v for k, v in chain["unexplained"].items() if k == d}'),
 ("M15 bẫy giá: bỏ số mũ n phiên", "(1 - band) ** n <= ratio <= (1 + band) ** n", "(1 - band) <= ratio <= (1 + band)"),
 ("X21a bẫy giá: bỏ cận TRÊN", "if not (1 - band) ** n <= ratio <= (1 + band) ** n:", "if not (1 - band) ** n <= ratio:"),
 ("X21b bẫy giá: bỏ cận DƯỚI", "if not (1 - band) ** n <= ratio <= (1 + band) ** n:", "if not ratio <= (1 + band) ** n:"),
 ("M39 biên HOSE 7% → 30%", 'EXCHANGE_BAND = {"HOSE": 0.07,', 'EXCHANGE_BAND = {"HOSE": 0.30,'),
 ("N8a sàn lạ/chưa khai ⇒ biên RỘNG nhất", 'DEFAULT_EXCHANGE = "HOSE"', 'DEFAULT_EXCHANGE = "UPCOM"'),
 ("N8b bỏ qua sàn đã khai", "    if ex in EXCHANGE_BAND:\n        return", "    if False:\n        return"),
 ("M16 bẫy KL: tắt", "if abs(qa - qb) > 1e-6:\n                why.append", "if False:\n                why.append"),
 ("M17 bẫy lịch corp-action: bỏ sự kiện", "            for e in events:\n                amt", "            for e in []:\n                amt"),
 ("B2a thiếu snapshot corp-action ⇒ coi là sạch", 'return None, f"không có {os.path.basename(path)}"', 'return [], f"không có {os.path.basename(path)}"'),
 ("X08 dùng snapshot usable=False", 'if snap.get("asof") != s.isoformat() or snap.get("usable") is not True:', 'if snap.get("asof") != s.isoformat():'),
 ("X07 bỏ lọc ngày sự kiện", 'if e.get("ticker") in tickers and e.get("date") == s.isoformat()], None', 'if e.get("ticker") in tickers], None'),
 ("X07b bỏ lọc mã sự kiện", 'if e.get("ticker") in tickers and e.get("date") == s.isoformat()], None', 'if e.get("date") == s.isoformat()], None'),
 ("B2b chỉ quét lịch của ngày dòng hiện tại", "for s in sessions if held else []:", "for s in sessions[-1:] if held else []:"),
 ("B2c không giữ mã loại trừ vẫn đòi lịch", "for s in sessions if held else []:", "for s in sessions:"),
 ("M18 thiếu phiên liền trước: bỏ kiểm", 'if prev["date"] < want:', 'if False:'),
 ("M19 mốc so: luôn dòng liền trước", 'prev = next((r for r in cut[:-1] if r["date"] == want), cut[-2])', 'prev = cut[-2]'),
 ("M20 health: bỏ kiểm phiên", 'if st.get("session") != want.isoformat():', 'if False:'),
 ("M21 bỏ dòng tiền nạp/rút (NAV tổng)", "total, info = build_ledger(rows, flows, base_date, base_nav)", "total, info = build_ledger(rows, [], base_date, base_nav)"),
 ("M22 sổ dòng tiền thiếu ⇒ coi như rỗng", "flows = load_flows(account, flows_path=ctx.flows_path, require_file=True, today=today)", "flows = load_flows(account, flows_path=ctx.flows_path, require_file=False, today=today)"),
 ("X28 bỏ nạp/rút ngoài khỏi chuỗi quản lý", "ledger, info = build_ledger(m_rows, flows + sleeve, *m_base)", "ledger, info = build_ledger(m_rows, sleeve, *m_base)"),
 ("X28b bỏ kiểm dòng tiền treo ở chuỗi quản lý", '        if info["pending"]:\n            raise ValueError(f"{len(info[\'pending\'])} dòng tiền TREO (account_cash_flows', '        if False:\n            raise ValueError(f"{len(info[\'pending\'])} dòng tiền TREO (account_cash_flows'),
 ("M37 dòng tiền treo (NAV tổng): bỏ qua", '        if info["pending"]:\n            raise ValueError(f"{len(info[\'pending\'])} dòng tiền TREO trong', '        if False:\n            raise ValueError(f"{len(info[\'pending\'])} dòng tiền TREO trong'),
 ("X29 thiếu managed_sleeve_flows.json coi như rỗng", "sleeve = load_flows(account, flows_path=ctx.sleeve_flows_path, require_file=True,", "sleeve = load_flows(account, flows_path=ctx.sleeve_flows_path, require_file=False,"),
 ("X33 nuốt lỗi khi ghi chuỗi mã loại trừ", '            extra_block = f"không ghi được chuỗi giá trị mã loại trừ: {type(exc).__name__}: {exc}"', '            extra_block = None'),
 ("X46 account nổ ⇒ overall OK", '"warnings": [], "notes": [], "overall": UNMEASURABLE, "monitor_error": True}', '"warnings": [], "notes": [], "overall": OK, "monitor_error": True}'),
 ("X50 active_nav thiếu giá mã loại trừ coi là 0", 'if not p or not float(p.get("price") or 0) > 0:', 'if not p:'),
 ("X09 health: rc bỏ qua send_error", 'broken = a.get("monitor_error") or st.get("error") or alert.get("send_error")', 'broken = a.get("monitor_error") or st.get("error")'),
 ("X54 health: không in lỗi gửi", '    if alert.get("send_error"):\n        body +=', '    if False:\n        body +='),
 ("N11 health: monitor lỗi vẫn ra rc như phanh", 'rc = 3 if broken else (0 if a["overall"] == OK else 1)', 'rc = 0 if a["overall"] == OK else 1'),
 ("X18 không lọc openQuantity>0", 'return [p for p in latest if float(p.get("openQuantity") or 0) > 0], ts, None', 'return list(latest), ts, None'),
 ("X19 lấy positions ĐẦU thay vì cuối", 'out[str(rec.get("account_no"))] = ((rec.get("payload") or {}).get("positions") or [],\n                                               rec.get("ts"))', 'out.setdefault(str(rec.get("account_no")), ((rec.get("payload") or {}).get("positions") or [], rec.get("ts")))'),
 ("X20 bỏ kiểm account của active_nav", 'if an.get("account") != account or an.get("computed_at") != date.isoformat():', 'if an.get("computed_at") != date.isoformat():'),
 ("M29 active_nav sai ngày vẫn dùng", 'if an.get("account") != account or an.get("computed_at") != date.isoformat():', 'if an.get("account") != account:'),
 ("M30 không so KL hai nguồn", "if abs(float(p.get(\"qty\") or 0) - qty) > 1e-6:", "if False:"),
 ("M41 bỏ đối chiếu total_nav hai file", "    if abs(gap) > NAV_MATCH_TOL:", "    if False:"),
 ("M42 NAV_MATCH_TOL 0,1% → 0,01%", "NAV_MATCH_TOL = 0.001", "NAV_MATCH_TOL = 0.0001"),
 ("M40 chưa có chuỗi mã loại trừ ⇒ lặng lẽ coi 0", "        if not excl:\n            raise ValueError", "        if False:\n            raise ValueError"),
 ("M28 chuỗi mã loại trừ: cho ghi đè", 'merged = sorted(old + [r for r in rows if r["date"] not in have]', 'merged = sorted([r for r in old if r["date"] not in {x["date"] for x in rows}] + [r for r in rows]'),
 ("N4 không áp bản đính chính", "    out.update(corrections or {})", "    pass"),
 ("X45a tắt cảnh báo mốc muộn", '            out["warnings"].append(out["late_start"])', '            pass'),
 ("X45b tắt cảnh báo ngày thiếu", "        if gaps:\n            out[\"warnings\"].append", "        if False:\n            out[\"warnings\"].append"),
 ("B3 chuỗi bắt đầu muộn vẫn đo đỉnh như thường", 'late = [chain["late_start"]] if chain.get("late_start") else []', 'late = []'),
 ("B1a bỏ kiểm giờ chụp", 'p = close_capture_problem(r["date"], chain["ts"].get(r["date"]))', 'p = None'),
 ("B1b bỏ cận dưới (chụp trước đóng cửa)", "    if t < lo:\n        return (f\"dòng NAV {d} chụp số dư lúc {ts} — TRƯỚC", "    if False:\n        return (f\"dòng NAV {d} chụp số dư lúc {ts} — TRƯỚC"),
 ("B1c bỏ cận trên (chụp sau mở cửa phiên kế)", "    if t >= hi:\n        return (f\"dòng NAV {d} chụp số dư lúc {ts} — SAU", "    if False:\n        return (f\"dòng NAV {d} chụp số dư lúc {ts} — SAU"),
 ("B1d cận dưới lệch biên", "    if t < lo:\n        return (f\"dòng NAV", "    if t <= lo:\n        return (f\"dòng NAV"),
 ("B1e cận trên lệch biên", "    if t >= hi:\n        return (f\"dòng NAV", "    if t > hi:\n        return (f\"dòng NAV"),
 ("B1f cửa sổ đóng ở 09:00 của NGÀY LỊCH kế (không phải phiên kế)", "hi = datetime.datetime.combine(next_session(d), SESSION_OPEN_ICT)", "hi = datetime.datetime.combine(d + datetime.timedelta(days=1), SESSION_OPEN_ICT)"),
 ("B6a tạm tính vượt ngưỡng vẫn là KHÔNG ĐO ĐƯỢC", "return _res(BREACH_PROV if hit else UNMEASURABLE, v, th, provisional=True,", "return _res(UNMEASURABLE, v, th, provisional=True,"),
 ("B6b tin tạm tính vượt ngưỡng không có lệnh BOT_STOP", "    if BREACH in statuses or BREACH_PROV in statuses:", "    if BREACH in statuses:"),
 ("B6c tạm tính vượt ngưỡng không gửi", "ALERTING = (BREACH, BREACH_PROV, UNMEASURABLE)", "ALERTING = (BREACH, UNMEASURABLE)"),
 ("B6d đầu tin tạm tính vượt ngưỡng vẫn vàng", "    elif BREACH_PROV in statuses:\n        head =", "    elif False:\n        head ="),
 ("B4a episode mở mà hết vị thế vay: im", "    elif not held:\n        probs.append(f\"episode {ep['id']} đang mở nhưng broker KHÔNG còn", "    elif False:\n        probs.append(f\"episode {ep['id']} đang mở nhưng broker KHÔNG còn"),
 ("B4b bản duyệt mới trong episode: không nêu", 'for a in guard["new_approvals"]:', 'for a in []:'),
 ("B4c bản duyệt mới: không lấy số xấu nhất", "            v = min(v, v_alt)", "            pass"),
 ("B4d --ack-approval không có tác dụng", "and a.isoformat() not in acked", "and True"),
 ("B5a không đọc được positions ⇒ 'không có episode'", '        if held is None:\n            res["episode"] = _res(\n                UNMEASURABLE, threshold=th["episode"],\n                reason=(f"không có episode nào đang mở, nhưng KHÔNG kiểm được', '        if False:\n            res["episode"] = _res(\n                UNMEASURABLE, threshold=th["episode"],\n                reason=(f"không có episode nào đang mở, nhưng KHÔNG kiểm được'),
 ("B5b positions chụp trước phiên vẫn dùng", "    if is_session(date) and (t is None or t < datetime.datetime.combine(date, SESSION_CLOSE_ICT)):", "    if False:"),
 ("B5c không khớp vị thế ở phiên kế", "        if cands and next_session(cands[0]) <= upto:", "        if False:"),
 ("B5d episode đang mở mà không đọc được positions: im", '    if held is None:\n        probs.append(f"không kiểm được vị thế gói vay', '    if False:\n        probs.append(f"không kiểm được vị thế gói vay'),
 ("M25 vị thế gói vay không episode: im", "        elif held:\n            # vị thế gói vay có thật", "        elif False:\n            # vị thế gói vay có thật"),
 ("M23 bản duyệt thu hồi vẫn mở", "        if is_revoked(rec):\n            notes.append", "        if False:\n            notes.append"),
 ("N5 revoked: chuỗi 'false' coi là đã thu hồi", 'return "revoked" in rec and rec.get("revoked") not in NOT_REVOKED', 'return bool(rec.get("revoked"))'),
 ("N5b revoked: chỉ nhận đúng True", 'return "revoked" in rec and rec.get("revoked") not in NOT_REVOKED', 'return rec.get("revoked") is True'),
 ("M24 mở episode không cần vị thế gói vay", "            if held:\n                opened = (c, held, ts)", "            if True:\n                opened = (c, held, ts)"),
 ("M34 episode: điểm vào = ngày mở", "ref = [x for x in dates if x < c]", "ref = [x for x in dates if x <= c]"),
 ("M36 episode đã đóng vẫn tính", 'if e.get("closed_date") is None or d < datetime.date.fromisoformat(e["closed_date"]):\n            return e', 'if True:\n            return e'),
 ("X14 ngày đóng dùng <=", 'if e.get("closed_date") is None or d < datetime.date.fromisoformat(e["closed_date"]):\n            return e', 'if e.get("closed_date") is None or d <= datetime.date.fromisoformat(e["closed_date"]):\n            return e'),
 ("X15 bỏ kiểm account trong bản duyệt", '        if rec.get("account") != account:\n            notes.append(f"{name} ghi account=', '        if False:\n            notes.append(f"{name} ghi account='),
 ("X16 bản duyệt tương lai vẫn mở", "        if d > upto:\n            continue", "        if False:\n            continue"),
 ("X17 bản duyệt cũ hơn episode đã đóng vẫn mở", "               for e in mine):\n            continue                      # bản duyệt cũ hơn một episode đã đóng", "               for e in mine) and False:\n            continue                      # bản duyệt cũ hơn một episode đã đóng"),
 ("M35 đóng/mở/đính chính không cần người + lý do", 'missing = [k for k, v in fields.items() if not (v or "").strip()]', 'missing = []'),
 ("B5e --open-episode cho phép mở chồng", '    if any(e["account"] == account and e.get("closed_date") is None for e in data["episodes"]):\n        print(f"❌ {account}: đang có một episode mở', '    if False:\n        print(f"❌ {account}: đang có một episode mở'),
 ("B5f --open-episode nhận ngày tương lai", "    if opened > today or (ref is not None and ref >= opened):", "    if (ref is not None and ref >= opened):"),
 ("M26 thiếu ngưỡng ⇒ mặc định −5%", '        errors["daily"] = (f"{rules_path}: risk_circuit_breakers.daily_loss_limit_pct phải là số "\n                           f"trong (−1, 0), đọc được {v!r}")', '        th["daily"] = -0.05'),
 ("X51 nhận ngưỡng daily dương", "not isinstance(v, (int, float)) or not -1 < v < 0:", "not isinstance(v, (int, float)) or not -1 < v < 1:"),
 ("N6a bỏ kiểm khoảng ngưỡng episode (trigger)", "    if not lo <= v <= hi:\n        return None, f\"{where}.trigger", "    if False:\n        return None, f\"{where}.trigger"),
 ("N6b regex lỏng như cũ", 'r"(?<![\\d.])-0\\.\\d\\d(?!\\d)"', 'r"-0\\.\\d+"'),
 ("N6c bỏ qua khoá số", "    if EPISODE_NUMERIC_KEY in node:", "    if False:"),
 ("N6d khoá số: bỏ kiểm khoảng", "not isinstance(v, (int, float)) or not lo <= v <= hi:", "not isinstance(v, (int, float)):"),
 ("N6e bỏ đối chiếu (-NN%) trong trigger", "    if stated and any(", "    if False and any("),
 ("M27 lý do thiếu dòng: bỏ đọc file chặn", "    if os.path.exists(block):", "    if False:"),
 ("N10 lý do sai khi phiên là dòng đầu chuỗi", '        if cut and cut[-1]["date"] == d:\n            block = (f"phiên {d} là dòng ĐẦU TIÊN', '        if False:\n            block = (f"phiên {d} là dòng ĐẦU TIÊN'),
 ("M31 từ chối gửi thật khi không live: bỏ", "    if not ctx.is_live:\n        return False,", "    if False:\n        return False,"),
 ("M32 expected_session: dùng ngày UTC", "d = now.astimezone(ICT).date() if now.tzinfo else now.date()", "d = now.astimezone(datetime.timezone.utc).date() if now.tzinfo else now.date()"),
 ("M33 NAV_EXPECTED_AFTER 21:50 → 00:00", "NAV_EXPECTED_AFTER_ICT = datetime.time(21, 50)", "NAV_EXPECTED_AFTER_ICT = datetime.time(0, 0)"),
 ("M38 tin cảnh báo: bỏ lệnh BOT_STOP", "lines.append(f\"`touch {os.path.join(WC_ROOT, 'data', 'BOT_STOP')}`\")", "pass"),
 ("B7a monitor nổ: không gửi tin", 'alert = send_once(ctx, [f"monitor|{d}|{type(exc).__name__}"], lambda: text)', 'alert = {"send_error": None, "sent_now": False}'),
 ("B7b monitor nổ: không ghi status", "    try:\n        _write_json_atomic(ctx.status_path, status)\n    except OSError as exc3:", "    try:\n        pass\n    except OSError as exc3:"),
 ("B7c sổ đã-gửi hỏng ⇒ nổ như cũ", "    except (OSError, ValueError) as exc:\n        sent = {}\n        out[\"ledger_error\"]", "    except (KeyError,) as exc:\n        sent = {}\n        out[\"ledger_error\"]"),
 ("B7d sổ episode hỏng ⇒ nổ cả lượt", "    except (OSError, ValueError) as exc:   # sổ episode hỏng", "    except (KeyError,) as exc:   # sổ episode hỏng"),
 ("B7e monitor nổ: không bắt ở main", "            except Exception as exc:\n                return crashed(ctx, args, d, exc)", "            except KeyError as exc:\n                return crashed(ctx, args, d, exc)"),
 ("B7f sổ đã-gửi hỏng: không cất bản hỏng", "            os.replace(ctx.sent_path, f\"{ctx.sent_path}.corrupt.{stamp:%Y%m%dT%H%M%S}\")", "            pass"),
 ("B9 không ghi nhật ký lượt chạy", "    _write_json_atomic(ctx.status_path, status)\n    _log_run(ctx, d, rc, status)\n    return rc", "    _write_json_atomic(ctx.status_path, status)\n    return rc"),
 ("N1 --date phiên cũ vẫn ghi/gửi", "        if d != expected_session(ctx.now) and not args.write_backdated:", "        if False:"),
 ("N1b chạy khô vẫn ghi chuỗi/episode", "                             record=not dry)", "                             record=True)"),
 ("N2 không khoá", "                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)\n                break", "                break"),
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
              "nav_loss_brake_backfill_excluded.py", "nav_loss_brake_monitor_selfcheck.py"):
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
