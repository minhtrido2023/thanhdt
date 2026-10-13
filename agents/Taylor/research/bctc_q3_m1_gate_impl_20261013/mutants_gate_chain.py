#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutation test cho 2 selfcheck CHƯA có artifact mutation lưu lại ở lượt 1:
  G* = fa_ratings_earnings_window_daily.sh  (qua GATE_SCRIPT=)   · C* = bq_freshness_check.sh (qua CHAIN_TARGET=)
Mỗi mutant = 1 phép thay chuỗi trên BẢN SAO trong /tmp; KILLED = selfcheck exit≠0. File thật không bị sửa.
Chạy: python3 mutants_gate_chain.py <worktree mike>"""
import os, subprocess, sys, tempfile
WT = sys.argv[1]
GATE, CHAIN = os.path.join(WT, "bin/fa_ratings_earnings_window_daily.sh"), os.path.join(WT, "bin/bq_freshness_check.sh")
G = [
 ("G01 biên đầu 10→15 (luật cũ)", "EDGE_DAY = (1, 4, 7, 10), (2, 5, 8, 11), 10", "EDGE_DAY = (1, 4, 7, 10), (2, 5, 8, 11), 15"),
 ("G02 biên 10→9", "(2, 5, 8, 11), 10", "(2, 5, 8, 11), 9"),
 ("G03 biên 10→11", "(2, 5, 8, 11), 10", "(2, 5, 8, 11), 11"),
 ("G04 đầu: < thành <=", "if d.day < EDGE_DAY:", "if d.day <= EDGE_DAY:"),
 ("G05 đuôi: > thành >=", "if d.day > EDGE_DAY:", "if d.day >= EDGE_DAY:"),
 ("G06 bỏ nhánh đuôi (luật cũ)", "elif d.month in TAIL_MONTHS:", "elif False:"),
 ("G07 đuôi không giới hạn ngày", "    if d.day > EDGE_DAY:", "    if False:"),
 ("G08 đầu không giới hạn ngày", "    if d.day < EDGE_DAY:", "    if False:"),
 ("G09 thiếu tháng 1", "HEAD_MONTHS, TAIL_MONTHS, EDGE_DAY = (1, 4, 7, 10)", "HEAD_MONTHS, TAIL_MONTHS, EDGE_DAY = (4, 7, 10)"),
 ("G10 thiếu tháng 10", "= (1, 4, 7, 10), (2", "= (1, 4, 7), (2"),
 ("G11 thiếu tháng 2", "(2, 5, 8, 11), 10", "(5, 8, 11), 10"),
 ("G12 thiếu tháng 11", "(2, 5, 8, 11), 10", "(2, 5, 8), 10"),
 ("G13 đuôi lệch sang tháng 3/6/9/12", "(2, 5, 8, 11), 10", "(3, 6, 9, 12), 10"),
 ("G14 tháng ngoài cửa sổ vẫn RUN", '    reasons.append(f"month={d.month} ngoai cua so mua BCTC")', "    pass"),
 ("G15 bỏ check lễ", "if is_holiday(d):", "if False:"),
 ("G16 loại lại cuối tuần", "if is_holiday(d):", "if is_holiday(d) or d.weekday() >= 5:"),
 ("G17 hoán đổi đầu/đuôi", "if d.month in HEAD_MONTHS:", "if d.month in TAIL_MONTHS and False or d.month in (1, 4, 7, 10) and d.day < 0:"),
 ("G18 --check không in gì", '  _gate "$CHECK_DATE"\n  exit 0', "  exit 0"),
]
C = [
 ("C01 pkl: bỏ timeout", 'timeout "$LAG_PKL_REFRESH_TIMEOUT_S" $PY refresh_earnings_surprise_pkl.py', '$PY refresh_earnings_surprise_pkl.py'),
 ("C02 pkl: python3 thay $PY", 'timeout "$LAG_PKL_REFRESH_TIMEOUT_S" $PY refresh', 'timeout "$LAG_PKL_REFRESH_TIMEOUT_S" python3 refresh'),
 ("C03 pkl: timeout mặc định 300→3000", '"${LAG_PKL_REFRESH_TIMEOUT_S:-300}"', '"${LAG_PKL_REFRESH_TIMEOUT_S:-3000}"'),
 ("C04 pkl: lỗi thì exit 1 (chặn plan)", '  _pkl_rc=$?\n', '  _pkl_rc=$?\n  exit 1\n'),
 ("C05 pkl: lỗi không notify", '  "$ROOT/bin/notify_thread.sh" "🟡 LAG PKL REFRESH WARN', '  : "🟡 LAG PKL REFRESH WARN'),
 ("C06 pkl: notify bỏ lý do thật", "Lý do thật: ${_pkl_why:-<không có output>}", "Lý do thật: xem log"),
 ("C07 pkl: timeout không được nêu tên", '[ "$_pkl_rc" -eq 124 ] && _pkl_why=', '[ "$_pkl_rc" -eq 999 ] && _pkl_why='),
 ("C08 pkl: lỗi tăng FAILED", '  _pkl_rc=$?\n', '  _pkl_rc=$?\n  FAILED=$((FAILED+1))\n'),
 ("C09 pkl: thành công cũng notify", '  echo "  [ok] [pipeline-1d] refresh_earnings_surprise_pkl', '  "$ROOT/bin/notify_thread.sh" "x" "$DISCORD_STALE_CHANNEL"; echo "  [ok] [pipeline-1d] refresh_earnings_surprise_pkl'),
 ("C10 pkl: nuốt output khi thành công", '  echo "$_pkl_out" | tail -3\n', ''),
 ("C11 pkl: notify sai kênh", 'Không chặn plan." "$DISCORD_STALE_CHANNEL"', 'Không chặn plan." "architecture"'),
 ("C12 pkl: chạy SAU golive", None, None),
 ("C13 pnj: bỏ timeout", "timeout 300 python3 bin/pnj_q3_review_watch.py", "python3 bin/pnj_q3_review_watch.py"),
 ("C14 pnj: không truyền --quiet", "bin/pnj_q3_review_watch.py ${QUIET:+--quiet}", "bin/pnj_q3_review_watch.py"),
 ("C15 pnj: lỗi tăng WARNED", '  echo "  [WARN] pnj_q3_review_watch.py exit=$?', '  WARNED=$((WARNED+1)); echo "  [WARN] pnj_q3_review_watch.py exit=$?'),
 ("C16 pnj: lỗi nuốt output thật", "Output thật: ${_pnj_out:-<rỗng>}", "Output thật: (ẩn)"),
 ("C17 pnj: nuốt output khi OK", '  [ -n "$_pnj_out" ] && echo "$_pnj_out"\n', '  :\n'),
 ("C18 pnj: lỗi thì exit 1", '  echo "  [WARN] pnj_q3_review_watch.py exit=$?', '  exit 1; echo "  [WARN] pnj_q3_review_watch.py exit=$?'),
 ("C19 pnj: dời xuống SAU cổng FAILED", None, None),
]
def special(name, src):
    if name.startswith("C12"):
        a = src.find("# [pipeline-1d] làm mới data/earnings_surprise_data.pkl"); b = src.find('_run_pipeline "[pipeline-2] golive_recommend_v23"')
        e = src.find("\n", b) + 1
        return src[:a] + src[b:e] + src[a:b] + src[e:]
    a = src.find("# --- PNJ BCTC Q3 review-trigger watch"); b = src.find('[ "$WARNED" -gt 0 ] && echo "NOTE:')
    blk = src[a:b]; rest = src[:a] + src[b:]
    k = rest.find('echo "=== ALL FRESH — chạy EOD pipeline ==="')
    return rest[:k] + blk + rest[k:]
def run(group, path, envk, cmd):
    src = open(path, encoding="utf-8").read(); kill = live = na = 0
    for name, a, b in group:
        if a is None: mut = special(name, src)
        elif a not in src: na += 1; print(f"NOT-APPLIED {name}"); continue
        else: mut = src.replace(a, b, 1)
        if mut == src: na += 1; print(f"NOT-APPLIED {name}"); continue
        with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False, encoding="utf-8") as f: f.write(mut); p = f.name
        os.chmod(p, 0o755)
        env = dict(os.environ, **{envk: p}); env.pop("TZ", None)
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=WT, timeout=600)
        fails = [l.strip() for l in (r.stdout + r.stderr).splitlines() if "FAIL" in l and "PASS /" not in l and "0 FAIL" not in l]
        if r.returncode != 0: kill += 1; print(f"KILLED   {name}  ← rc={r.returncode}, {len(fails)} dòng FAIL (vd: {fails[0][:110] if fails else '-'})")
        else: live += 1; print(f"SURVIVED {name}")
        os.unlink(p)
    print(f"TỔNG {envk}: {kill} killed / {live} survived / {na} not-applied / {len(group)} mutant\n"); return live + na
bad = run(G, GATE, "GATE_SCRIPT", ["bash", "bin/fa_ratings_earnings_window_gate_selfcheck.sh"])
bad += run(C, CHAIN, "CHAIN_TARGET", ["python3", "bin/bctc_q3_chain_wiring_selfcheck.py"])
sys.exit(1 if bad else 0)
