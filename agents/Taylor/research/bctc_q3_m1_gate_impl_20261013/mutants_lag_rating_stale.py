# -*- coding: utf-8 -*-
"""Mutation test cho lag_rating_stale (job Taylor_20261013_125149). Mỗi mutant = 1 thay thế chuỗi
trên bản sao tạm của 3 file đích; chạy lag_rating_stale_selfcheck.py với LRS_TARGET_DIR=bản sao.
KILLED = selfcheck exit != 0. Dùng: $DNA_PYEXE mutants_lag_rating_stale.py <WC worktree dir>"""
import os, shutil, subprocess, sys, tempfile

WT = os.path.abspath(sys.argv[1])
PY = sys.executable
F, G, T = "lag_rating_filter.py", os.path.join("deploy_golive_dt5g_v4", "golive_recommend_v23.py"), "telegram_recommend.py"
M = [
 # ── hàm cờ ──
 ("F01 so sánh <= (đúng ngày cũng cờ)", F, "if not rating_d < rel_d or", "if not rating_d <= rel_d or"),
 ("F02 so sánh đảo >", F, "if not rating_d < rel_d or", "if not rating_d > rel_d or"),
 ("F03 bỏ guard mã không có rating", F, "if tk not in rmap or pd.isna(rel_ts):", "if pd.isna(rel_ts):"),
 ("F04 lỗi nguồn bị nuốt (trả None)", F, '        return [], f"{type(ex).__name__}: {ex}"\n\n\ndef annotate', '        return [], None\n\n\ndef annotate'),
 ("F05 nhãn gate lệch biên (<=4 là PASS)", F, "float(rt) < rating_max_ok + 1 else", "float(rt) <= rating_max_ok + 1 else"),
 ("F06 hàm cờ sửa cand tại chỗ", F, "        tks = sorted(set(cand[\"ticker\"]))\n        asof_d = pd.Timestamp(asof).date()\n        tl = \",\".join(f\"'{t}'\" for t in tks)\n        a = bq(f\"\"\"SELECT f.ticker, f.rating, f.time\nFROM tav2_bq.fa_ratings_8l AS f\nWHERE f.ticker IN ({tl}) AND f.time <= DATE '{asof_d}'\nQUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) = 1\"\"\")\n        rmap = {r.ticker: (r.rating, r.time)",
  "        tks = sorted(set(cand[\"ticker\"]))\n        cand.drop(cand.index[:1], inplace=True)\n        asof_d = pd.Timestamp(asof).date()\n        tl = \",\".join(f\"'{t}'\" for t in tks)\n        a = bq(f\"\"\"SELECT f.ticker, f.rating, f.time\nFROM tav2_bq.fa_ratings_8l AS f\nWHERE f.ticker IN ({tl}) AND f.time <= DATE '{asof_d}'\nQUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) = 1\"\"\")\n        rmap = {r.ticker: (r.rating, r.time)"),
 ("F07 bỏ điều kiện as-of trong SQL cờ", F, "WHERE f.ticker IN ({tl}) AND f.time <= DATE '{asof_d}'\nQUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) = 1\"\"\")\n        rmap = {r.ticker: (r.rating, r.time)",
  "WHERE f.ticker IN ({tl})\nQUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) = 1\"\"\")\n        rmap = {r.ticker: (r.rating, r.time)"),
 ("F08 bỏ khử trùng", F, " or (tk, rel_d) in seen:", " or False:"),
 ("F09 so theo giờ thay vì ngày", F, "rel_d, rating_d = rel_ts.date(), rtime_ts.date()", "rel_d, rating_d = rel_ts, rtime_ts"),
 ("F10 thiếu cột → im lặng", F, 'return [], "cand thiếu cột ticker/Release_Date — không kiểm được rating cũ"', "return [], None"),
 ("F11 bỏ sắp xếp", F, '        flags.sort(key=lambda f: (f["release_date"], f["ticker"]))\n', ""),
 ("F12 rating không ép int", F, '"rating": int(rt) if has_rt else None,', '"rating": rt if has_rt else None,'),
 ("F13 NaT rating time không bỏ qua", F, "            if pd.isna(rtime_ts):\n                continue\n", ""),
 ("F14 rổ rỗng vẫn truy vấn", F, "    try:\n        if cand is None or not len(cand):\n            return [], None\n        if \"ticker\" not in", "    try:\n        if cand is None:\n            return [], None\n        if \"ticker\" not in"),
 ("F15 rating NULL bị gắn PASS", F, '"gate": "PASS" if has_rt and float(rt)', '"gate": "PASS" if not has_rt or float(rt)'),
 ("F16 đổi ngưỡng cổng thật 3→4", F, "RATING_MAX_OK = 3 ", "RATING_MAX_OK = 4 "),
 ("F17 cổng thật: >= thành >", F, "if float(rt) >= rating_max_ok + 1:", "if float(rt) > rating_max_ok + 1:"),
 ("F18 cổng thật: missing không loại", F, "        if rt is None or pd.isna(rt):\n            dropped.append(", "        if False:\n            dropped.append("),
 # ── annotate / formatter ──
 ("P01 đổi nhãn UPCOMING↔WINDOW_PASSED", F, '(("UPCOMING", lag_up), ("WINDOW_PASSED", lag_recent))', '(("WINDOW_PASSED", lag_up), ("UPCOMING", lag_recent))'),
 ("P02 khớp status chỉ theo ticker", F, 'shown[(it["ticker"], str(it["release"]))] = f"{label} {it[\'entry\']}"', 'shown[(it["ticker"], None)] = f"{label} {it[\'entry\']}"'),
 ("P03 không có cờ vẫn ra dòng", F, "        if not flags:\n            return \"\"\n", ""),
 ("P04 bỏ qua lỗi", F, "        if error:\n", "        if False:\n"),
 ("P05 không escape HTML", F, 'esc = (lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")) if html else str', "esc = str"),
 ("P06 không cắt danh sách", F, "for f in fs[:STALE_LIST_MAX])", "for f in fs)"),
 ("P07 nhóm LOẠI bị bỏ", F, "        if failed:\n            parts.append(", "        if False:\n            parts.append("),
 ("P08 PASS ngoài cửa sổ bị nêu tên", F, 'if f.get("gate") == "PASS" and f.get("status")]', 'if f.get("gate") == "PASS"]'),
 ("P09 html dùng **", F, 'b0, b1 = ("<b>", "</b>") if html else ("**", "**")', 'b0, b1 = ("**", "**")'),
 ("P10 formatter raise khi rác", F, '    except Exception as ex:\n        return f"⚠️ lag_rating_stale: không dựng được dòng cảnh báo ({type(ex).__name__})"', '    except ZeroDivisionError as ex:\n        return ""'),
 ("P11 không đếm sự kiện ngoài cửa sổ", F, "        if other:\n", "        if False:\n"),
 ("P12 annotate sửa lag_up", F, "            for it in items or []:\n", "            for it in items or []:\n                it[\"entry\"] = str(it[\"entry\"]) + \" \"\n"),
 # ── golive ──
 ("G01 cờ làm LOẠI mã cũ (fail-closed lén)", G, "    cand, lag_rating_dropped, lag_rating_error = lag_filter_low_rating(bq, cand, LATEST)\n",
  "    cand = cand[~cand[\"ticker\"].isin({f[\"ticker\"] for f in lag_rating_stale})]\n    cand, lag_rating_dropped, lag_rating_error = lag_filter_low_rating(bq, cand, LATEST)\n"),
 ("G02 cờ đo SAU cổng (mất phía RATING_FAIL)", G, "    lag_rating_stale, lag_rating_stale_error = lag_rating_stale_flags(bq, cand, LATEST)\n    cand, lag_rating_dropped, lag_rating_error = lag_filter_low_rating(bq, cand, LATEST)\n",
  "    cand, lag_rating_dropped, lag_rating_error = lag_filter_low_rating(bq, cand, LATEST)\n    lag_rating_stale, lag_rating_stale_error = lag_rating_stale_flags(bq, cand, LATEST)\n"),
 ("G03 mất khoá status lag_rating_stale", G, '    "lag_rating_stale": lag_rating_stale,\n', ""),
 ("G04 mất khoá lag_rating_stale_error", G, '    "lag_rating_stale_error": lag_rating_stale_error,\n', ""),
 ("G05 mất dòng trong .md", G, 'if _lag_stale_line:\n    L.append("\\n" + _lag_stale_line)\n', ""),
 ("G06 bỏ annotate status", G, "annotate_stale_status(lag_rating_stale, lag_up, lag_recent)\n", ""),
 ("G07 cổng thật bị bỏ gọi (chỉ còn cờ)", G, "    cand, lag_rating_dropped, lag_rating_error = lag_filter_low_rating(bq, cand, LATEST)\n", "    pass\n"),
 ("G08 cờ rating PASS-cũ bị đẩy khỏi lag_up", G, "annotate_stale_status(lag_rating_stale, lag_up, lag_recent)\n",
  "annotate_stale_status(lag_rating_stale, lag_up, lag_recent)\nlag_up = [it for it in lag_up if it[\"ticker\"] not in {f[\"ticker\"] for f in lag_rating_stale}]\n"),
 ("G09 khởi tạo biến cờ trong try", G, "lag_rating_stale, lag_rating_stale_error = [], None\n", ""),
 ("G10 cờ dùng asof khác (END)", G, "lag_rating_stale_flags(bq, cand, LATEST)", "lag_rating_stale_flags(bq, cand, END)"),
 ("G11 annotate đảo tham số", G, "annotate_stale_status(lag_rating_stale, lag_up, lag_recent)", "annotate_stale_status(lag_rating_stale, lag_recent, lag_up)"),
 ("G12 lọc thanh khoản bị bỏ", G, "    cand, lag_liq_dropped, lag_liq_error = lag_filter_illiquid(bq, cand, LATEST)\n", ""),
 ("G13 n_lag_rating_stale sai", G, '"n_lag_rating_stale": len(lag_rating_stale),', '"n_lag_rating_stale": 0,'),
 # ── telegram ──
 ("T01 không nối dòng", T, "    if _stale:\n        lines.append(_stale)\n", ""),
 ("T02 dùng markdown thay HTML", T, 'st.get("lag_rating_stale_error"), html=True)', 'st.get("lag_rating_stale_error"), html=False)'),
 ("T03 bỏ qua lỗi kiểm", T, '                                              st.get("lag_rating_stale_error"), html=True)', "                                              None, html=True)"),
 ("T04 dòng chèn TRƯỚC book LAG", T, "    lines.append(build_lag_section(lag_df, w_tgt))\n    # Cảnh báo-only", "    _lagsec = build_lag_section(lag_df, w_tgt)\n    # Cảnh báo-only"),
]
ONLY = sys.argv[2].split(',') if len(sys.argv) > 2 else None
if ONLY:
    M = [m for m in M if m[0].split(' ')[0] in ONLY]
killed = survived = notapplied = 0
surv = []
for name, rel, old, new in M:
    tmp = tempfile.mkdtemp(prefix="lrsmut_")
    try:
        os.makedirs(os.path.join(tmp, "deploy_golive_dt5g_v4"))
        for r in (F, G, T):
            shutil.copy(os.path.join(WT, r), os.path.join(tmp, r))
        p = os.path.join(tmp, rel); s = open(p, encoding="utf-8").read()
        if s.count(old) != 1:
            notapplied += 1; print(f"NOT-APPLIED ({s.count(old)} khớp)  {name}"); continue
        open(p, "w", encoding="utf-8").write(s.replace(old, new))
        if name.startswith("T04"):
            s2 = open(p, encoding="utf-8").read().replace("    if _stale:\n        lines.append(_stale)\n", "    if _stale:\n        lines.append(_stale)\n    lines.append(_lagsec)\n")
            open(p, "w", encoding="utf-8").write(s2)
        r = subprocess.run([PY, os.path.join(WT, "lag_rating_stale_selfcheck.py")], capture_output=True, text=True,
                           env=dict(os.environ, LRS_TARGET_DIR=tmp), timeout=300)
        fails = [l.strip()[:110] for l in r.stdout.splitlines() if l.startswith("  FAIL")]
        if r.returncode != 0:
            killed += 1; print(f"KILLED   {name}  ← {len(fails)} FAIL" + (f" (vd: {fails[0]})" if fails else f" (crash: {r.stderr.strip().splitlines()[-1][:100] if r.stderr.strip() else ''})"))
        else:
            survived += 1; surv.append(name); print(f"SURVIVED {name}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
print(f"\nTỔNG: {killed} killed / {survived} survived / {notapplied} not-applied / {len(M)} mutant")
for s in surv: print("  SỐNG:", s)
