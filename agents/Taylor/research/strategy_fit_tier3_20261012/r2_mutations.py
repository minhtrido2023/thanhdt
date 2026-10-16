#!/usr/bin/env python3
"""Vòng 2 (job Taylor_20261012_044300) — bảng đột biến cho nhánh feat/strategy-fit-tier3-20261012.
Mỗi đột biến: sửa 1 chỗ trong file nguồn (đếm đúng 1 lần khớp), chạy selfcheck, kỳ vọng ĐỎ, trả file về.
Chạy từ gốc worktree:  python3 <file này>   (thoát 0 = mọi đột biến đều bị giết)."""
import subprocess, sys
PY = "/home/trido/thanhdt/wc_venv/bin/python"
D, E = "bin/strategy_fit_dashboard.py", "bin/eod_trading_report.sh"
SD, SE = "bin/strategy_fit_dashboard_selfcheck.py", "bin/strategy_fit_email_attach_selfcheck.py"
M = [
 # ── C1
 ("C1a dòng 25% mất phần trạng thái thực thi", D, SD, " <b>Trạng thái thực thi</b>: {st['cron']}; đầu vào của \"", " Đầu vào của \""),
 ("C1b dòng −5% mất phần trạng thái thực thi", D, SD, "<b>Trạng thái thực thi</b>: {st['lim']}. Ô này", "Ô này"),
 ("C1c dòng episode mất phần trạng thái thực thi", D, SD, "<b>Trạng thái thực \"\n        f\"thi</b>: {st['epi']}; {st['cron']}. Ô này", "\"\n        f\"Ô này"),
 ("C1d kết luận cron đảo điều kiện (n==0 → n!=0)", D, SD, '"(trang không kiểm systemd)" if n == 0 else', '"(trang không kiểm systemd)" if n != 0 else'),
 ("C1e dòng crontab bị # vẫn được đếm", D, SD, ' and not ln.lstrip().startswith("#"))', ')'),
 ("C1f trạng thái crontab viết cứng (không đọc)", D, SD, 'for ln in prov["crontab"]().splitlines()', 'for ln in "".splitlines()'),
 ("C1g trạng thái khoá −5% viết cứng (không quét code)", D, SD,
  'out["lim"] = refs("daily_loss_limit_pct", "<b>chưa có code nào đọc khoá này</b>, luật chưa được thực thi")',
  'out["lim"] = "0 file nhắc tới daily_loss_limit_pct ⇒ <b>chưa có code nào đọc khoá này</b>, luật chưa được thực thi"'),
 ("C1h khôi phục suy diễn «không có episode nào đang được theo dõi»", D, SD,
  " (file vắng KHÔNG cho biết có episode hay không: bộ theo dõi không chạy thì cũng không có file)", " ⇒ không có episode nào đang được theo dõi"),
 ("C1i ghi lại «→ HALT» như phanh đang chạy", D, SD, "'KHÔNG ĐỌC ĐƯỢC'}% thì HALT \"\n        f\"(BOT_STOP) — hằng số", "'KHÔNG ĐỌC ĐƯỢC'}% → HALT \"\n        f\"(BOT_STOP) — hằng số"),
 ("C1j ngày file eod_account viết cứng", D, SD, 'f"file mới nhất mang ngày <b>{esc(eod[-1])}</b>" if eod', 'f"file mới nhất mang ngày <b>20260702</b>" if eod'),
 ("C1k quét code lỗi bị nuốt thành «0 file»", D, SD, "            n_files, hits = prov[\"code_refs\"](needle)\n        except Exception as e:\n            return f\"<b>không xác định được</b>",
  "            n_files, hits = prov[\"code_refs\"](needle)\n        except Exception as e:\n            n_files, hits = 0, []\n        if False:\n            return f\"<b>không xác định được</b>"),
 # ── C2
 ("C2a bỏ đánh giá ΔNAV thô trước cổng", D, SD, 'raw_hit = lim is not None and raw is not None and raw["change_pct"] / 100 <= lim', "raw_hit = False"),
 ("C2b ΔNAV thô so sai đơn vị (% với tỉ lệ)", D, SD, 'raw["change_pct"] / 100 <= lim', 'raw["change_pct"] <= lim'),
 ("C2c ô bị chặn không còn hiện ΔNAV thô", D, SD, "            c.body = (f'<p>ΔNAV <b>thô</b> của dòng mới nhất", "            _ = (f'<p>ΔNAV <b>thô</b> của dòng mới nhất"),
 ("C2d chạm phanh trong ngày theo ΔNAV thô không lên danh sách", D, SD, "            if raw_hit:\n                c.touched.append(", "            if False:\n                c.touched.append("),
 # ── C3 (7 đột biến của reviewer + 3 về data_dir)
 ("C3-1 flows=[] (bỏ sổ dòng tiền)", D, SD, "require_file=True)              # thiếu sổ dòng tiền ⇒ TỪ CHỐI, không đoán []\n", "require_file=True)\n        flows = []\n"),
 ("C3-2 bỏ require_file=True", D, SD, "require_file=True)              # thiếu sổ", "require_file=False)             # thiếu sổ"),
 ("C3-3 NAV luôn lấy của SpaceX", D, SD, 'rows = nul.load_nav_history(account, ', 'rows = nul.load_nav_history("SpaceX", '),
 ("C3-4 mốc khởi điểm luôn lấy của SpaceX", D, SD, 'inception = nul.load_inception(account, ', 'inception = nul.load_inception("SpaceX", '),
 ("C3-5 dòng tiền luôn lấy của SpaceX", D, SD, 'flows = acf.load_flows(account, ', 'flows = acf.load_flows("SpaceX", '),
 ("C3-6 jumps=[] (tắt cổng NAV-jump)", D, SD, "raw_last=raw_last, jumps=acf.unexplained_nav_jumps(rows, flows),", "raw_last=raw_last, jumps=[],"),
 ("C3-7 build_ledger nhận flows=[]", D, SD, "nul.build_ledger(rows, flows, ", "nul.build_ledger(rows, [], "),
 ("C3-8 provider bỏ qua data_dir cho NAV", D, SD, 'nul.load_nav_history(account, os.path.join(data_dir, "execution_logs"))', "nul.load_nav_history(account)"),
 ("C3-9 provider bỏ qua data_dir cho sổ dòng tiền", D, SD, 'acf.load_flows(account, os.path.join(data_dir, "account_cash_flows.json"),', "acf.load_flows(account, None,"),
 ("C3-10 provider bỏ qua data_dir cho mốc khởi điểm", D, SD, 'nul.load_inception(account, os.path.join(data_dir, "account_inception.json"))', "nul.load_inception(account)"),
 ("C3-11 cổng §12 «bộ số giống hệt» bị tắt", D, SD, "len({c.sig for c in ok}) == 1:", "len({c.sig for c in ok}) == 0:"),
 # ── C4b
 ("C4b-1 mốc 19:10 lệch biên (>= → >)", D, SD, "(n.hour, n.minute) >= NAV_SNAPSHOT_ICT", "(n.hour, n.minute) > NAV_SNAPSHOT_ICT"),
 ("C4b-2 mất neo ICT (dùng tz của now)", D, SD, "    n = now.astimezone(ICT)\n", "    n = now\n"),
 ("C4b-3 ô drawdown không bao giờ CŨ", D, SD, "        c.stale = last_date < want\n", "        c.stale = False\n"),
 ("C4b-4 không trừ nghỉ lễ khi lùi phiên", D, SD, "        while not is_session(d):\n            d -= timedelta(days=1)\n    return d", "        while d.weekday() >= 5:\n            d -= timedelta(days=1)\n    return d"),
 ("C4b-5 quay về quy tắc cũ (cho phép thiếu 1 ngày)", D, SD, "        c.stale = last_date < want\n", "        c.stale = bdays_after(last_date, now.date()) > 1\n"),
 # ── N1..N6
 ("N1a bỏ kiểm giờ đóng cửa (chỉ so ngày)", D, SD, 'ok = t.date() == r["date"] and t.time() >= acf.SESSION_CLOSE_ICT', 'ok = t.date() == r["date"]'),
 ("N1b bỏ kiểm ngày (chỉ so giờ)", D, SD, 'ok = t.date() == r["date"] and t.time() >= acf.SESSION_CLOSE_ICT', "ok = t.time() >= acf.SESSION_CLOSE_ICT"),
 ("N1c cặp lệch giờ vẫn gọi là giá chốt", D, SD, '    if any(r.get("snap_off") or r.get("nav_is_estimate") for r in (a, b)):', "    if False:"),
 ("N1d bỏ cỡ sai số của drawdown lớn nhất", D, SD, 'max_dd_err=max((x for r in off for x in around(r)), default=None),', "max_dd_err=None,"),
 ("N2 nguồn mất «ĐÃ KHAI» / số bản ghi", D, SD, "(đã loại nạp/rút ĐÃ KHAI — {flows_txt}; cùng công thức với", "(đã loại nạp/rút; cùng công thức với"),
 ("N3a caveat ZaloPay tụt xuống sau bảng", D, SD, '            head + _table(["Chỉ số", "Giá trị", "Ghi chú"], rows)\n', '            _table(["Chỉ số", "Giá trị", "Ghi chú"], rows) + head\n'),
 ("N3b ô ZaloPay lại mang mốc −25,2%", D, SD, "        else:\n            _, m = ct.find(\"CLAUDE.md\"", "        if True:\n            _, m = ct.find(\"CLAUDE.md\""),
 ("N3c độ lớn DGC viết cứng thay vì trích", D, SD, "bot — DGC khoảng <b>{esc(m.group(1)) if m else \"KHÔNG ĐỌC ĐƯỢC\"}% NAV</b>", "bot — DGC khoảng <b>một phần ba NAV</b>"),
 ("N4 bộ đếm đếm cả lệnh ngoài block", D, SD, ' and "hyb:blk" in str(r.get("note", ""))', ""),
 ("N5a mất câu «không so với ngưỡng +22 bps»", D, SD, "Số PAPER, <b>không so với ngưỡng +", "Số PAPER, <b>ngưỡng +"),
 ("N5b mất khoảng leave-one-out", D, SD, "dương = mua ĐẮT hơn giá mở cửa; {loo_txt}. \"", "dương = mua ĐẮT hơn giá mở cửa. \""),
 ("N6a N đếm cả dòng ngày lễ", D, SD, 'sess = ledger[:1] + [r for r in ledger[1:] if is_session(r["date"])]', "sess = list(ledger)"),
 ("N6b ngày lễ bị coi là phiên thiếu", D, SD, "        if is_session(d) and d not in have:", "        if d.weekday() < 5 and d not in have:"),
 # ── N7
 ("M11a dòng «hiện tại từ đỉnh» hiện tỉ suất từ mốc", D, SD, '["Drawdown hiện tại từ đỉnh", f"<b>{vn(100 * s[\'cur_dd\'], 2)}%</b>"', '["Drawdown hiện tại từ đỉnh", f"<b>{vn(100 * s[\'total\'], 2)}%</b>"'),
 ("M11b drawdown hiện tại tính từ mốc thay vì từ đỉnh", D, SD, 'cur_dd=last["unit_price"] / peak["unit_price"] - 1,', 'cur_dd=last["unit_price"] / sess[0]["unit_price"] - 1,'),
 ("M18 chạm 25% theo drawdown LỚN NHẤT", D, SD, 'if ddt is not None and s["cur_dd"] <= -ddt:', 'if ddt is not None and s["max_dd"] <= -ddt:'),
 ("M19a biên −5% lệch +5 bps", D, SD, 'if lim is not None and s["day_ret"] <= lim:', 'if lim is not None and s["day_ret"] <= lim + 0.0005:'),
 ("M19b biên −5% lệch −5 bps", D, SD, 'if lim is not None and s["day_ret"] <= lim:', 'if lim is not None and s["day_ret"] <= lim - 0.0005:'),
 ("M19c ngưỡng −5% viết cứng thay vì đọc file luật", D, SD, 'if lim is not None and s["day_ret"] <= lim:', 'if lim is not None and s["day_ret"] <= -0.05:'),
 ("M21 chạm theo phiên xấu nhất LỊCH SỬ", D, SD, 'if lim is not None and s["day_ret"] <= lim:', 'if lim is not None and s["worst_day"] <= lim:'),
 ("M35 xoá đoạn giải thích mốc −25,2%", D, SD, "            tail = ('<p class=\"muted\">Mốc tham chiếu là con số của backtest nhiều năm, <b>không phải ngưỡng hành động</b>; '\n                    f'{s[\"n\"]} phiên live chưa đủ để nói drawdown thật «khớp» hay «lệch» mốc đó.</p>') + tail\n", "            pass\n"),
 # ── C4a (script EOD)
 ("C4a-1 khôi phục cửa sổ dùng lại 30 phút", E, SE, "  if [ \"$PLAN_DATE\" = \"$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)\" ]; then\n    # mtime",
  "  if [ -z \"$(find \"$dash\" -newermt '-30 minutes' -size +0c 2>/dev/null)\" ] && [ \"$PLAN_DATE\" = \"$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)\" ]; then\n    # mtime"),
 ("C4a-2 bỏ chốt «file phải được ghi lại ở lượt này»", E, SE, ' || [ "$(stat -c %y "$dash" 2>/dev/null || true)" = "$before" ]; then', "; then"),
 ("C4a-3 nhánh HOLD gửi trước khi chụp NAV", E, SE, "  _nav_section\n  _dt5g_warn_set\n", "  _dt5g_warn_set\n"),
 ("C4a-4 nhánh đầy đủ gửi trước khi chụp NAV", E, SE, "\n_nav_section\n", "\n: no_nav\n"),
 ("C4a-5 lượt sau sinh lỗi vẫn kèm file lượt trước", E, SE, "      STRATEGY_FIT_ARGS=(--attach-note \"Dashboard độ phù hợp chiến lược KHÔNG kèm hôm nay — sinh lỗi: $last\")\n      return 0\n",
  "      STRATEGY_FIT_ARGS=(--attach-note \"Dashboard độ phù hợp chiến lược KHÔNG kèm hôm nay — sinh lỗi: $last\")\n"),
]
only = sys.argv[1:]
alive, dead, broken = [], [], []
for name, path, chk, old, new in M:
    if only and not any(name.startswith(o) for o in only):
        continue
    src = open(path, encoding="utf-8").read()
    if src.count(old) != 1:
        broken.append(f"{name}: neo khớp {src.count(old)} lần"); print(f"??    {name}  (neo khớp {src.count(old)} lần)"); continue
    try:
        open(path, "w", encoding="utf-8").write(src.replace(old, new))
        r = subprocess.run([PY, chk], capture_output=True, text=True)
    finally:
        open(path, "w", encoding="utf-8").write(src)
    fails = [ln.strip()[:110] for ln in r.stdout.splitlines() if ln.strip().startswith(("FAIL", "[FAIL]"))]
    (dead if r.returncode != 0 else alive).append(name)
    print(f"{'CHẾT ' if r.returncode != 0 else 'SỐNG '} {name}  ({len(fails)} ca đỏ" + (f"; đầu: {fails[0]}" if fails else "") + ")")
print(f"\n==> {len(dead)} chết / {len(alive)} sống / {len(broken)} neo hỏng")
for a in alive + broken:
    print("   CÒN:", a)
sys.exit(1 if alive or broken else 0)
