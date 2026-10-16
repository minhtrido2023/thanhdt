# -*- coding: utf-8 -*-
"""Mutation test cho bin/pnj_q3_review_watch.py. Dùng: python3 mutants_pnj_watch.py <mike worktree>"""
import os, shutil, subprocess, sys, tempfile
WT = os.path.abspath(sys.argv[1]); SRC = os.path.join(WT, "bin", "pnj_q3_review_watch.py")
SC = os.path.join(WT, "bin", "pnj_q3_review_watch_selfcheck.py")
M = [
 ("W01 bỏ chốt already_fired", 'if st.get("bus_posted_at") and st.get("discord_attempted_at"):\n        return "already_fired"', 'if False:\n        return "already_fired"'),
 ("W02 n<=0 vẫn bắn", 'if det["n"] <= 0:', 'if det["n"] < -5:'),
 ("W03 bỏ hỏi lại bus trước khi post", "            on_bus = bool(bus_has_fn())\n", "            on_bus = False\n"),
 ("W04 state hỏng → coi như rỗng (fail-open)", '    except Exception as ex:\n        return None, f"{type(ex).__name__}: {ex}"\n    if not isinstance(st, dict):', '    except Exception as ex:\n        return {}, None\n    if not isinstance(st, dict):'),
 ("W05 dấu Discord ghi SAU khi gửi", '        st["discord_attempted_at"] = stamp()\n        save_state(state_path, st)          # dấu "đã thử" TRƯỚC khi gửi ⇒ tối đa một lần\n        try:\n            post_discord_fn(build_discord(det))\n', '        try:\n            post_discord_fn(build_discord(det))\n            st["discord_attempted_at"] = stamp()\n'),
 ("W06 Discord lỗi → xoá dấu (sẽ gửi lại)", '            st["discord_ok"] = False\n', '            st["discord_ok"] = False\n            st.pop("discord_attempted_at", None)\n'),
 ("W07 post bus lỗi vẫn ghi state", '                return "bus_post_failed"\n', '                pass\n'),
 ("W08 BQ lỗi → coi như đã có", '            return "query_failed"\n        if not isinstance(det, dict)', '            det = {"n": 1, "release_date": None, "time": None}\n        if not isinstance(det, dict)'),
 ("W09 bus không đọc được → vẫn post", '            return "bus_unreadable"\n', '            on_bus = False\n'),
 ("W10 ghi state không nguyên tử", "    os.replace(tmp, path)\n", "    import shutil; shutil.copy(tmp, path); os.remove(tmp)\n"),
 ("W11 dry-run vẫn post", "    if dry_run:\n", "    if False:\n"),
 ("W12 sai quý (2026Q2)", 'QUARTER = "2026Q3"', 'QUARTER = "2026Q2"'),
 ("W13 sai mã", 'TICKER = "PNJ"', 'TICKER = "DGC"'),
 ("W14 sai topic", 'TOPIC = "pnj-bctc-q3-review-trigger"', 'TOPIC = "pnj-review"'),
 ("W15 bus_has khớp chuỗi con", '                if isinstance(ev, dict) and ev.get("topic") == TOPIC and ev.get("event_type") == "question":', '                if True:'),
 ("W16 bus_has không lọc event_type", ' and ev.get("event_type") == "question":', ":"),
 ("W17 bus_has chỉ quét inbox", 'glob.glob(os.path.join(bus_dir, "**", "*.jsonl"), recursive=True)', 'glob.glob(os.path.join(bus_dir, "inbox", "*.jsonl"))'),
 ("W18 thiếu bus dir → False", '        raise RuntimeError(f"không thấy thư mục bus: {bus_dir}")', "        return False"),
 ("W19 giờ UTC thay ICT", "    return datetime.now(_ICT)", "    return datetime.now(ZoneInfo('UTC'))"),
 ("W20 main trả 1 khi lỗi", '        print(f"WARN pnj-q3-watch: lỗi không lường trước — {type(ex).__name__}: {ex}")\n        return 0', '        print(f"WARN pnj-q3-watch: lỗi không lường trước — {type(ex).__name__}: {ex}")\n        return 1'),
 ("W21 payload bỏ target Mike", '        "target": "Mike",\n', ""),
 ("W22 payload bỏ câu KHÔNG tự khôi phục", '"do_not": (f"KHÔNG tự khôi phục {TICKER}; KHÔNG sửa', '"do_not": (f"Có thể khôi phục {TICKER}; KHÔNG sửa'),
 ("W23 state của mã khác vẫn nhận", "    if st and (st.get(\"ticker\") != TICKER or st.get(\"quarter\") != QUARTER):", "    if False:"),
 ("W24 state không-phải-dict vẫn nhận", "    if not isinstance(st, dict):\n        return None,", "    if False:\n        return None,"),
 ("W25 bỏ kiểm hình dạng kết quả truy vấn", '        if not isinstance(det, dict) or not isinstance(det.get("n"), int):', "        if False:"),
 ("W26 đã bắn rồi vẫn truy vấn BQ", '    det = st.get("detected")\n    if not det:', '    det = None\n    if not det:'),
 ("W27 Discord gửi trước bus", '    if not st.get("bus_posted_at"):\n        try:\n            on_bus', '    if False:\n        try:\n            on_bus'),
 ("W28 log lỗi BQ không kèm lỗi thật", 'f"Lỗi thật: {type(ex).__name__}: {ex}")\n            return "query_failed"', 'f"")\n            return "query_failed"'),
 ("W29 Discord lỗi không ghi lỗi thật", '            st["discord_error"] = f"{type(ex).__name__}: {ex}"\n', '            st["discord_error"] = "lỗi"\n'),
 ("W30 không lưu detected vào state", '"detected": det,\n', '"detected": None,\n'),
]
k = s_ = na = 0; surv = []
for name, old, new in M:
    tmp = tempfile.mkdtemp(prefix="pnjmut_"); p = os.path.join(tmp, "pnj_q3_review_watch.py")
    try:
        src = open(SRC, encoding="utf-8").read()
        if src.count(old) != 1:
            na += 1; print(f"NOT-APPLIED ({src.count(old)} khớp)  {name}"); continue
        open(p, "w", encoding="utf-8").write(src.replace(old, new))
        r = subprocess.run([sys.executable, SC], capture_output=True, text=True, env=dict(os.environ, PNJW_TARGET=p), timeout=120)
        fails = [l.strip()[:100] for l in r.stdout.splitlines() if l.startswith("  FAIL")]
        if r.returncode != 0:
            k += 1; print(f"KILLED   {name}  ← {len(fails)} FAIL" + (f" (vd: {fails[0]})" if fails else " (crash)"))
        else:
            s_ += 1; surv.append(name); print(f"SURVIVED {name}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
print(f"\nTỔNG: {k} killed / {s_} survived / {na} not-applied / {len(M)} mutant")
for x in surv: print("  SỐNG:", x)
