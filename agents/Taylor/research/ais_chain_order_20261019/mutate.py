"""Mutation harness: mỗi mutant sửa ĐÚNG 1 nhánh của luật chuỗi; selfcheck phải đỏ (rc!=0)."""
import os, shutil, subprocess, sys, tempfile
WT = sys.argv[1] if len(sys.argv) > 1 else "/home/trido/thanhdt/wt-Taylor_20261019_052148/WorkingClaude"
src = open(f"{WT}/oshares_live.py").read()
M = {
 "M1 bỏ chặn nhóm trùng-total": ("        if len({r[\"effective_date\"] for r in grp}) != 1 or \\", "        if False and len({r[\"effective_date\"] for r in grp}) != 1 or \\"),
 "M2 bỏ đòi delta>0": ("if d is None or float(d) <= 0 or abs(", "if d is None or abs("),
 "M3 nới dung sai mắt xích": ("abs(t0 + float(d) - t1) / t1 > EXPLAIN_TOL:", "abs(t0 + float(d) - t1) / t1 > 1.0:"),
 "M4 bỏ đòi có dòng sai ngày": ("    if not late:\n        return ais_rows, []", "    if False:\n        return ais_rows, []"),
 "M5 bỏ đòi có public_date": ("        if not pub:\n            return ais_rows, []", "        if not pub:\n            pub = dates[i]"),
 "M6 tăng không ngặt": ("if any(a >= b for a, b in zip(new, new[1:])):", "if any(a > b for a, b in zip(new, new[1:])):"),
 "M7 bỏ kiểm tăng dọc chuỗi": ("if any(a >= b for a, b in zip(new, new[1:])):", "if False:"),
 "M8 bỏ đường tắt chain_certified": ("    if rows and all(r.get(\"chain_certified\") for r in rows):", "    if False:"),
 "M9 _ais_verdicts không qua luật": ("    ais_rows, _redated = _visible_ais(corp, ticker, asof)", "    ais_rows = [c for c in corp if c['ticker'] == ticker and c['event_code'] == 'AIS' and c['effective_date'] and c['effective_date'] <= asof and c['shares_total_after']]"),
 "M10 oshares_at không qua luật": ("        ais, redated = _visible_ais(corp, tk, asof)", "        ais, redated = [c for c in corp if c['ticker'] == tk and c['event_code'] == 'AIS' and c['effective_date'] and c['effective_date'] <= asof and c['shares_total_after']], []"),
 "M11 sửa dict caller tại chỗ": ("            out.append({**r, \"effective_date\": new[i], \"vendor_effective_date\": dates[i],\n                        \"chain_certified\": True})", "            r.update({\"effective_date\": new[i], \"vendor_effective_date\": dates[i], \"chain_certified\": True}); out.append(r)"),
 "M12 dời ngày MỌI dòng về public": ("    for i in late:\n", "    for i in range(len(dates)):\n"),
 "M13 dòng sai ngày = quá SỚM thay vì quá muộn": ("late = [i for i in range(len(dates) - 1) if dates[i] > min(dates[i + 1:])]", "late = [i for i in range(1, len(dates)) if dates[i] < max(dates[:i])]"),
 "M14 không gắn chain_certified": ("                        \"chain_certified\": True})", "                        \"chain_certified\": False})"),
}
killed, alive = [], []
for name, (a, b) in M.items():
    assert src.count(a) == 1, f"{name}: mẫu không duy nhất ({src.count(a)})"
    d = tempfile.mkdtemp(prefix="osl_mut_")
    try:
        open(f"{d}/oshares_live.py", "w").write(src.replace(a, b))
        env = dict(os.environ, PYTHONPATH=WT)
        r = subprocess.run([sys.executable, f"{d}/oshares_live.py", "--selfcheck"], cwd=d, env=env,
                           capture_output=True, text=True, timeout=600)
        fails = [l.strip()[:70] for l in r.stdout.splitlines() if l.strip().startswith("FAIL ")]
        (killed if r.returncode != 0 else alive).append(name)
        print(("KILLED" if r.returncode != 0 else "ALIVE "), name, "|", fails[:3] or r.stderr.strip()[-120:])
    finally:
        shutil.rmtree(d)
print(f"mutants {len(M)}: killed {len(killed)} alive {len(alive)} {alive}")
