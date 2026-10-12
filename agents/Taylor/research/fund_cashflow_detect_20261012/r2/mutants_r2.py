"""Mutant vòng 2 (Taylor, job Taylor_20261012_162001).

`suite(name)` trả list (id, file, old, new, note) — `old` phải xuất hiện ĐÚNG 1 lần:
  rev   = 72 mutant của arch-reviewer (arch_review_ea9d6969a/mutants.py); cái nào chuỗi `old` không
          còn trong code vòng 2 thì được CHUYỂN sang đúng chỗ tương ứng của code mới (PORT_REV),
          giữ nguyên id + ý nghĩa đột biến.
  step2 = 86 mutant vòng 1 của tác giả (mut/mutants_step2.py), chuyển tương tự (PORT_STEP2).
  ar3   = 76 mutant arch-review bước 1 (ar3_mut/mutants.py), nguyên văn.
  new   = mutant MỚI cho logic vòng 2 (lời xác nhận, đối chiếu số lượng, trôi, nhãn, S4-S7, gửi).
`OBSOLETE` = id mà đột biến không còn chỗ áp (code bị bỏ theo quyết định thiết kế) + lý do.
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A = "account_cash_flows.py"; DN = "daily_nav_snapshot.py"; NU = "nav_unit_ledger.py"
RG = "report_delivery_gate.py"; CI = "cash_identity.py"; NP = "nav_period_returns.py"
EOD = "eod_trading_report.sh"; RETRY = "nav_sync_retry.sh"

RESID = "residual = delta_k - (sell - buy - fees + dividend + egg_interest - egg_cost)"
SIDE = '"side": "sell" if str(o.get("side") or "").upper().startswith("NS") else "buy",'
RECV = "            if at <= snap and (best is None or at >= best[0]):\n                best = (at, value)"
MATCH = 'matching = [a for a in acks if a["from"] == snap0 and a["to"] == snap1]'
FILLWIN = "                if snap0 < moment <= snap1:\n                    out.append(dict(o, moment=moment))"
TOL = 'tol = prev["nav"] * threshold_pct / 100'

# id -> (file, old, new) ở code vòng 2
PORT_REV = {
    "N01": (CI, "over=abs(unexplained) > tol,", "over=abs(unexplained) >= tol,"),
    "N02": (CI, SIDE, SIDE.replace(".upper()", "")),
    "N03": (CI, 'qty * _num(o.get("averagePrice") or o.get("price"))}', 'qty * _num(o.get("price") or o.get("averagePrice"))}'),
    "N04": (CI, '                if o["qty"] <= 0:\n                    continue', '                if o["qty"] < 0:\n                    continue'),
    "N05": (CI, 'moment = o["moment"] or datetime.datetime.combine(day, SESSION_CLOSE_ICT)',
            'moment = o["moment"] or datetime.datetime.combine(day, datetime.time(0, 0))'),
    "N07": (CI, RECV, RECV.replace("at <= snap", "at < snap")),
    "N08": (CI, RECV, RECV.replace("at >= best[0]", "at <= best[0]")),
    "N10": (CI, "None if value is None else _num(value)))", "0.0 if value is None else _num(value)))"),
    "N11": (CI, "                best = (at, value)\n        return None if best is None else best[1]",
            "                best = (at, value)\n        return 0.0 if best is None else best[1]"),
    "N19": (CI, 'return 3 if result["suspects"] or result["drift"] else 0', "return 0"),
    "N22": (CI, 'out["orders"].update(mine)  ', 'out["orders"] = dict(mine, **out["orders"])  '),
    "N23": (CI, '                if str(p.get("accountNo")) != self.account_no:\n                    continue\n                price = p.get("marketPrice")',
            '                price = p.get("marketPrice")'),
    "N31": (CI, 'for at, value in self.day(snap.date())["balances"]:', 'for at, value in self.day(snap.date())["balances"][:1]:'),
    "N32": (CI, '        if egg_out:\n            win["notes"].append(', '        if egg_out > 1e18:\n            win["notes"].append('),
    "N37": (CI, "            if tag is None:\n                return                              # không gắn tài khoản ⇒ không đoán là của ai\n", ""),
    "N38": (CI, "            if silent:\n", "            if False:\n"),
    "N40": (CI, 'out["n_order_records"] += 1 if (mine or tag is not None) else 0', 'out["n_order_records"] += 1'),
    "N41": (CI, MATCH, "matching = list(acks)[:1]"),
    "G07": (RG, '            ops.append(f"⚠️ {PENDING_FLOW_MARKER} ({account}): KHÔNG kiểm được dòng tiền treo — "\n                       f"{type(exc).__name__} ({exc})")',
            "            pass"),
    "G09": (RG, "        if investor and INVESTOR_FLOW_MARKER not in text:\n", '        if investor and INVESTOR_FLOW_MARKER not in text:\n            raise RuntimeError("cash-flow BLOCK")\n'),
    "G10": (RG, "if investor and INVESTOR_FLOW_MARKER not in text:", "if investor and INVESTOR_FLOW_MARKER in text:"),
    "G11": (RG, "    if cell is None:\n        print(", '    if cell is None:\n        raise RuntimeError("period-return BLOCK thiếu dòng")\n        print('),
    "G13": (RG, "identity = cash_identity_report(account, asof=end, **paths)", "identity = cash_identity_report(accounts[0], asof=end, **paths)"),
    "S01": (DN, "    except Exception as exc:                # noqa: BLE001 — đường hiển thị (xem docstring)\n        line = (f\"⚠️ Đẳng thức tiền",
            "    except ValueError as exc:                # noqa: BLE001 — đường hiển thị (xem docstring)\n        line = (f\"⚠️ Đẳng thức tiền"),
    "S02": (DN, "identity = cash_identity_report(args.account, args.date, nav_dir=EXEC_DIR, raw_dir=EXEC_DIR)",
            "identity = cash_identity_report(args.account, args.date)"),
    "S03": (DN, 'lines.append("   " + identity["investor_line"])', 'lines.append("   ")'),
    "P03": (NP, 'result["cash_flow_warnings"] = identity["ops_lines"]', 'result["cash_flow_warnings"] = identity["ops_lines"][:1]'),
}
PORT_STEP2 = {
    "C07": (CI, RESID, RESID.replace("- fees", "+ fees")),
    "C08": (CI, RESID, RESID.replace(" + dividend", "")),
    "C09": (CI, RESID, RESID.replace(" + egg_interest", "")),
    "C10": (CI, RESID, RESID.replace("sell - buy", "buy - sell")),
    "C20": (CI, MATCH, 'matching = [a for a in acks if a["to"] == snap1]'),
    "C21": (CI, MATCH, 'matching = [a for a in acks if a["from"] == snap0]'),
    "C22": (CI, MATCH, "matching = list(acks)"),
    "C23": (CI, 'win["suspect"] = bool(win["kind"]) and win["acked"] is None', 'win["suspect"] = bool(win["kind"])'),
    "C24": (CI, "over=abs(unexplained) > tol,", "over=unexplained > tol,"),
    "C25": (CI, TOL, TOL + " * 2"),
    "C26": (CI, TOL, TOL + " / 2"),
    "C27": (CI, 'pct_nav=unexplained / prev["nav"] * 100,', 'pct_nav=unexplained / cur["nav"] * 100,'),
    "C30": (CI, "        if tag is not None and str(tag) != self.account_no:\n            return                                  # §12: bản ghi của tài khoản khác\n", ""),
    "C31": (CI, "            if tag is None:\n                return                              # không gắn tài khoản ⇒ không đoán là của ai\n", ""),
    "C33": (CI, RECV, RECV.replace("at <= snap and ", "")),
    "C34": (CI, FILLWIN, FILLWIN.replace("snap0 < moment <= snap1", "snap0.date() <= moment.date() <= snap1.date()")),
    "C35": (CI, FILLWIN, FILLWIN.replace("snap0 < moment <= snap1", "snap0 <= moment < snap1")),
    "C36": (CI, SIDE, '"side": "buy",'),
    "C38": (CI, '                if o["qty"] <= 0:\n                    continue\n', ""),
    "C55": (CI, "            ops.append(uncheckable_line(account, w))\n            if ends_today:\n                today.append(ops[-1])", "            pass"),
    "C56": (CI, '("NẠP vào" if gap > 0 else "RÚT ra")', '("NẠP vào" if gap < 0 else "RÚT ra")'),
    "C57": (CI, "        if gaps:\n            win[\"kind\"] = LABEL_QUANTITY", "        if False:\n            win[\"kind\"] = LABEL_QUANTITY"),
    "C59": (CI, '        if egg_out:\n            win["notes"].append(', '        if egg_out > 1e18:\n            win["notes"].append('),
    "D40": (DN, "return report(account, asof=datetime.date.fromisoformat(date), **paths)", "return report(account, asof=None, **paths)"),
    "D41": (DN, 'lines.append("   " + identity["investor_line"])', 'lines.append(identity["investor_line"])'),
    "D42": (DN, '    if identity["investor_line"]:\n        lines.append(', '    if False:\n        lines.append('),
    "D43": (DN, '"cash_flow_investor_line": identity["investor_line"],', '"cash_flow_investor_line": None,'),
    "D44": (DN, '"cash_flow_warnings": identity["ops_lines"],', '"cash_flow_warnings": [],'),
    "P60": (NP, 'result["cash_flow_warnings"] = identity["ops_lines"]', 'result["cash_flow_warnings"] = []'),
    "P61": (NP, "identity = cash_identity_report(args.account, asof=report_date)", "identity = cash_identity_report(args.account)"),
    "R06": (RG, "identity = cash_identity_report(account, asof=end, **paths)", "identity = cash_identity_report(account, **paths)"),
    "R07": (RG, '            ops.extend(identity["ops_lines"])', "            pass"),
    "R09": (RG, "if investor and INVESTOR_FLOW_MARKER not in text:", "if False:"),
}
OBSOLETE = {
    "N42": "placeholder của reviewer (chưa bao giờ áp)",
}

NEW = [
    # ---- lời xác nhận ở file riêng (S1)
    ("X01", CI, "                if abs(drift) > tol:", "                if abs(drift) > tol * 1000:", "lời xác nhận không bao giờ lệch số tiền (S1 quay lại)"),
    ("X02", CI, 'drift = unexplained - ack["acked_residual_vnd"]', "drift = 0.0", "bỏ so phần dư với số đã xác nhận (S1 quay lại)"),
    ("X03", CI, '                if gaps != ack["acked_qty_gaps"]:', "                if False:", "bỏ so số lượng đã xác nhận"),
    ("X04", CI, "            if len(matching) > 1:", "            if False:", "hai lời xác nhận cùng cửa sổ ⇒ dùng cái đầu"),
    ("X05", CI, '"evidence": _ack_text(rec, "evidence", where),', '"evidence": str(rec.get("evidence")),', "lời xác nhận không cần bằng chứng"),
    ("X06", CI, "isinstance(residual, bool) or not isinstance(residual, (int, float)) or not math.isfinite(residual):",
     "isinstance(residual, bool) or not isinstance(residual, (int, float)):", "acked_residual_vnd NaN lọt (so với NaN luôn False ⇒ đóng mọi cửa sổ)"),
    ("X07", CI, "        recs = blob.get(account, [])", "        recs = [r for v in blob.values() if isinstance(v, list) for r in v]", "lời xác nhận của tài khoản khác cũng dùng (§12)"),
    ("X08", CI, '        return [], f"{path} không dùng được nên KHÔNG lời xác nhận nào có hiệu lực — {_err(exc)}"', "        return [], None", "file lời xác nhận hỏng ⇒ im lặng"),
    ("X09", CI, "isinstance(residual, bool) or not isinstance(residual, (int, float)) or not math.isfinite(residual):",
     "not isinstance(residual, (int, float)) or not math.isfinite(residual):", "acked_residual_vnd = true được nhận như 1"),
    ("X10", CI, 'money = [(flow_moment(f)[0], f) for f in flows if f["kind"] != "market_only"]\n',
     'money = [(flow_moment(f)[0], f) for f in flows if f["kind"] != "market_only"]\n    acks = list(acks) + [{"from": None, "to": None}] * 0\n', "tương đương có chủ đích (kiểm bộ chạy): không đổi hành vi"),
    # ---- đối chiếu số lượng ở mọi cửa sổ (C1)
    ("X11", CI, "from corp_actions import load_corp_actions  # noqa: E402", "from corp_actions import load_all as load_corp_actions  # noqa: E402", "sự kiện cổ phiếu CHƯA KÝ cũng giải thích số lượng"),
    ("X12", CI, "                      and 0 <= q0 * (a[\"qty_multiplier\"] - 1) - gap + 1e-6 < 1), None)", "                      ), None)", "sự kiện đã ký giải thích MỌI số lượng lệch của mã đó"),
    ("X13", CI, 'if a["ticker"] == symbol and snap0 < a["effective"] <= snap1', 'if a["ticker"] == symbol', "sự kiện ngoài cửa sổ cũng giải thích"),
    ("X14", CI, 'net[fx["symbol"]] = net.get(fx["symbol"], 0.0) + (fx["qty"] if fx["side"] == "buy" else -fx["qty"])',
     'net[fx["symbol"]] = net.get(fx["symbol"], 0.0) + fx["qty"]', "lệnh bán tính như mua khi đối chiếu số lượng"),
    ("X15", CI, "    if p0 is None or p1 is None:\n        return {}, {}, (", "    if p0 is None and p1 is None:\n        return {}, {}, (", "thiếu vị thế MỘT đầu vẫn đối chiếu"),
    ("X16", CI, "        if unverified:\n            win[\"notes\"].append(", "        if False:\n            win[\"notes\"].append(", "bỏ ghi chú không đối chiếu được số lượng"),
    ("X17", CI, 'elif ends_today and (w.get("info") or (w.get("qty_unverified") and not w["acked"])):', 'elif ends_today and w.get("info"):', "lượt chụp thiếu vị thế không báo kênh vận hành"),
    ("X18", CI, "        gaps[symbol], values[symbol] = gap, (gap * price if price else None)", "        gaps[symbol], values[symbol] = gap, None", "không ước giá trị số lượng lệch"),
    ("X19", CI, "        if abs(gap) < 1e-6:\n            continue", "        if abs(gap) < 1e9:\n            continue", "không bao giờ thấy số lượng lệch (C1 quay lại)"),
    # ---- nhãn + khấu trừ Trứng vàng (S2)
    ("X21", CI, "        elif egg_cost > tol:", "        elif False:", "bỏ dòng nhắc khi đẳng thức khép nhờ ước tính lớn (R5)"),
    ("X22", CI, "        egg_cost = egg_out * EGG_WITHDRAW_COST\n", "        egg_cost = 0.0\n", "bỏ khấu trừ rút Trứng vàng khỏi đẳng thức (S2 quay lại)"),
    ("X23", CI, "EGG_WITHDRAW_COST = 0.002013", "EGG_WITHDRAW_COST = 0.0015", "hằng số khấu trừ rút Trứng vàng lệch"),
    ("X24", CI, "    if gap < 0 and debt > 0:\n        cap = debt *", "    if False:\n        cap = debt *", "bỏ ứng viên lãi vay (R6 thành nghi rút)"),
    ("X25", CI, "        if -gap <= cap:", "        if True:", "ứng viên lãi vay không có trần"),
    ("X26", CI, '        if gross <= prev["mtm"] * DIVIDEND_SAME_WINDOW_CAP:', "        if True:", "ứng viên cổ tức không có trần"),
    ("X27", CI, ' and -gap <= win["egg_out"] * EGG_WITHDRAW_COST_CAP:', ":", "ứng viên khấu trừ Trứng vàng không có trần"),
    ("X28", CI, 'win["kind"] = LABEL_INTERNAL if win["candidates"] else LABEL_EXTERNAL', 'win["kind"] = LABEL_EXTERNAL', "luôn gọi là nghi nạp/rút (S2 quay lại)"),
    ("X29", CI, "EGG_WITHDRAW_COST_CAP = 0.01", "EGG_WITHDRAW_COST_CAP = 0.03", "trần khấu trừ Trứng vàng nới 3 lần"),
    ("X30", CI, "max(days, 1):  # chưa tới mức lãi của chính cửa sổ", "0:  # chưa tới mức lãi của chính cửa sổ", "sai số lãi suất Trứng vàng bị coi là RÚT Trứng vàng"),
    # ---- trôi (S3)
    ("X31", CI, 'recent = [w for w in windows[-DRIFT_WINDOWS:] if w["checkable"] and not w["kind"]]', 'recent = [w for w in windows[-DRIFT_WINDOWS:] if w["checkable"]]', "cửa sổ đang mở bị cộng lần nữa vào tổng trôi"),
    ("X32", CI, "    if not recent or abs(total_pct) <= threshold_pct:", "    if not recent or total_pct <= threshold_pct:", "chỉ thấy trôi chiều dương (rút nhỏ giọt lọt)"),
    ("X33", CI, 'drift["new"] = drift_of(windows[:-1], by_date, threshold_pct) is None', 'drift["new"] = True', "dòng trôi gửi chi tiết MỌI tối"),
    ("X34", CI, "    if drift and drift[\"new\"]:\n        today.append(drift_line(account, drift))", "    if False:\n        today.append(drift_line(account, drift))", "lượt đầu tiên thấy trôi không gửi chi tiết"),
    ("X35", CI, '"ops_lines": ops + ([drift_line(account, drift)] if drift else []) + errors,', '"ops_lines": ops + errors,', "dòng trôi biến mất khỏi chi tiết vận hành"),
    ("X36", CI, "    if not amounts:\n        return None", "    if result[\"drift\"]:\n        amounts.append(abs(result[\"drift\"][\"sum_vnd\"]))\n    if not amounts:\n        return None", "dòng trôi (không ai đóng được) vào báo cáo nhà đầu tư"),
    # ---- S6 / G8 / S7
    ("X41", CI, 'broken = raw.problems_between(prev["snap"].date(), cur["snap"].date())', "broken = []", "bản ghi dnse_raw hỏng bị bỏ qua im lặng (S6)"),
    ("X42", CI, "                    except (ValueError, TypeError, AttributeError, KeyError) as exc:", "                    except ValueError as exc:", "bản ghi sai KIỂU làm chết cả tài khoản (S6)"),
    ("X43", CI, "return f\"{type(exc).__name__} ({_ERRNO_RE.sub('', str(exc))})\"", 'return f"{type(exc).__name__}: {exc}"', "dòng lỗi khớp bộ dò của cron_health_check (G8)"),
    ("X44", CI, 'return f"{value:,.0f}".replace(",", ".") + " đ"', 'return f"{value:,.0f}".replace(",", ".") + " VND"', "viết VND (S7)"),
    ("X45", CI, 'return _vn(value, 3) + "% NAV"', 'return f"{value:+.3f}% NAV"', "phần trăm mang dấu (S7)"),
    ("X46", CI, '+ (f"; … và {len(broken) - 3} bản ghi nữa" if len(broken) > 3 else "")]', "]", "không in số bản ghi hỏng còn lại (S6)"),
    # ---- kênh: nhà đầu tư vs vận hành (C2)
    ("X51", CI, "(today if ends_today else older).append(ops[-1] if ends_today else w)", "today.append(ops[-1])", "chi tiết cửa sổ cũ lặp lại mỗi tối (C2)"),
    ("X52", CI, '        ends_today = w["date1"] == day', "        ends_today = True", "mọi cửa sổ coi như kết thúc hôm nay"),
    ("X53", CI, "    if str(ops.get(\"status\", \"\")).startswith(SENT_PREFIX):\n        return 0,", "    if False:\n        return 0,", "bước gửi không idempotent (§5)"),
    ("X54", CI, 'if os.environ.get("MIKE_BOT_TEST_MODE") == "1" or os.environ.get("PYTEST_CURRENT_TEST"):', "if False:", "bỏ chốt chế độ test (§5b)"),
    ("X55", CI, "failure = (None if proc.returncode == 0 else", "failure = (None if True else", "gửi hỏng vẫn ghi 'đã gửi'"),
    ("X56", CI, "    os.replace(tmp, path)\n    if failure:", "    if failure:", "không ghi trạng thái gửi vào nav_snapshot"),
    ("X57", CI, '[notify_script or NOTIFY_SCRIPT, "\\n".join(lines), channel]', '[notify_script or NOTIFY_SCRIPT, lines[0], channel]', "chỉ gửi dòng đầu"),
    ("X58", DN, "            and str(previous.get(\"status\", \"\")).startswith(\"đã gửi\"):\n        return {\"lines\": lines, \"status\": previous[\"status\"]}",
     "            and False:\n        return {\"lines\": lines, \"status\": previous[\"status\"]}", "chụp lại cùng ngày ⇒ gửi lại (§5)"),
    ("X59", DN, 'if isinstance(previous, dict) and previous.get("lines") == lines \\', "if isinstance(previous, dict) and True \\", "nội dung ĐỔI vẫn giữ 'đã gửi' (không gửi cái mới)"),
    ("X60", DN, '"cash_flow_ops": cash_flow_ops_record(snapshot_path, identity["ops_today"]),', '"cash_flow_ops": cash_flow_ops_record(snapshot_path, identity["ops_lines"]),', "kênh vận hành nhận chi tiết MỌI cửa sổ mỗi tối"),
    ("X61", DN, '    if identity["investor_line"]:\n        lines.append("   " + identity["investor_line"])', '    lines += ["   " + x for x in identity["ops_lines"]]', "chi tiết vận hành vào thân báo cáo ngày (C2 quay lại)"),
    ("X62", EOD, '  if [ "$rc" = "0" ]; then\n    python3 "$ROOT/bin/cash_identity.py"', '  if [ "$rc" != "9" ]; then\n    python3 "$ROOT/bin/cash_identity.py"', "gọi bước gửi cả khi NAV chưa ghi"),
    ("X63", EOD, "      --channel trading_daily >&2 || true\n  fi\n}", "      --channel trading_daily || true\n  fi\n}", "đầu ra bước gửi không sang stderr (vẫn không vào NAV_SECTION — tương đương về thân báo cáo)"),
    ("X64", EOD, '--notify-snapshot "$PLAN_DATE" \\\n      --channel trading_daily >&2 || true\n  fi\n}', '--notify-snapshot "$PLAN_DATE" \\\n      --channel trading_report >&2 || true\n  fi\n}', "chi tiết vận hành gửi nhầm kênh báo cáo"),
    ("X65", RETRY, '--notify-snapshot "$PLAN_DATE"', '--notify-snapshot "$TODAY"', "nav_sync_retry gọi sai tham số ngày (TODAY == PLAN_DATE ở nhánh này ⇒ tương đương)"),
    ("X66", RG, "        if OPS_FLOW_MARKER in text:", "        if False:", "cổng không nhắc khi báo cáo mang dòng vận hành"),
    ("X67", RG, "            if identity[\"investor_line\"]:\n                investor.append(identity[\"investor_line\"])", "            pass", "cổng không lấy dòng nhà đầu tư"),
    # ---- S4 / S5
    ("X71", RG, "    if reported_pct is None:\n        raise RuntimeError(\n            f\"period-return BLOCK ({report.name}): dòng 'Từ khi bắt đầu hoạt động' có mặt",
     "    if reported_pct is None:\n        return\n        raise RuntimeError(\n            f\"period-return BLOCK ({report.name}): dòng 'Từ khi bắt đầu hoạt động' có mặt", "ô số hỏng ⇒ bỏ qua (S4 quay lại)"),
    ("X72", RG, "            return cells[1] if len(cells) >= 2 else \"\"", "            return cells[1] if len(cells) >= 2 else None", "dòng thiếu cột số ⇒ coi như không có dòng"),
    ("X73", RG, "    return value if math.isfinite(value) else None", "    return value", "bỏ kiểm hữu hạn ở ô số (regex đã chặn nan/inf ⇒ tương đương)"),
    ("X74", RG, "    except Exception as exc:                           # noqa: BLE001 — xem docstring", "    except OSError as exc:                           # noqa: BLE001 — xem docstring", "đường cảnh báo ném lỗi ra deliver() (S5 quay lại)"),
    ("X75", RG, "        except Exception as exc:                       # noqa: BLE001 — cảnh báo, không chặn\n            ops.append(f\"⚠️ Đẳng thức tiền",
     "        except ValueError as exc:                       # noqa: BLE001 — cảnh báo, không chặn\n            ops.append(f\"⚠️ Đẳng thức tiền", "import cash_identity hỏng không còn ra dòng lỗi riêng (S5)"),
    ("X76", RG, "                    _warn_cash_flows(report)\n", "", "deliver() không gọi cảnh báo dòng tiền"),
    # ---- G3
    ("X81", CI, '"uncheckable": ([baseline] if baseline else []) + [w for w in windows if not w["checkable"]],', '"uncheckable": [w for w in windows if not w["checkable"]],', "không liệt kê cửa sổ mốc khởi điểm (G3)"),
    ("X82", CI, 'elif not w["checkable"] and (ends_today or not w.get("baseline")):', 'elif not w["checkable"] and not w.get("baseline"):', "lượt chụp đầu của tài khoản mới không báo cửa sổ mốc khởi điểm (G3)"),
]


def _load(dirname, modname):
    path = os.path.join(HERE, "..", dirname)
    sys.path.insert(0, path)
    sys.modules.pop(modname, None)
    try:
        return list(importlib.import_module(modname).M)
    finally:
        sys.path.pop(0)
        sys.modules.pop(modname, None)


def _ported(mutants, ports):
    out = []
    for mid, fname, old, new, note in mutants:
        if mid in OBSOLETE:
            continue
        if mid in ports:
            fname, old, new = ports[mid]
            note = note + " [chuyển sang code vòng 2]"
        out.append((mid, fname, old, new, note))
    return out


def suite(name):
    if name == "rev":
        return _ported(_load("arch_review_ea9d6969a", "mutants"), PORT_REV)
    if name == "step2":
        return _ported(_load("mut", "mutants_step2"), PORT_STEP2)
    if name == "ar3":
        return _load("ar3_mut", "mutants")
    if name == "new":
        return list(NEW)
    raise SystemExit(f"không có bộ '{name}'")
