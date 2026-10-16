import os, shutil, subprocess, sys, tempfile
WT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-step4-1014/bin"
VT, VS = "vnindex_total_return.py", "vnindex_total_return_selfcheck.py"
NS, NSS = "nav_sleeve.py", "nav_sleeve_selfcheck.py"
NP, NPS = "nav_period_returns.py", "nav_period_benchmark_selfcheck.py"
PT, PTS = "period_table_32.py", "period_table_32_selfcheck.py"
M = [
 ("N1", VT, 'u.loc[u.dy_i > DY_CORRUPT, "divcash"] = 0.0', 'pass', "không loại cổ tức hỏng >50%", (VS,)),
 ("N2", VT, 'for i, r in enumerate(rows):\n        # G2', 'for i, r in list(enumerate(rows))[1:]:\n        # G2', "G2 bỏ dòng mốc", (VS, NPS)),
 ("N4", NS, 'and r["ex_date"] <= d and', 'and r["ex_date"] < d and', "recv không tính ngày GDKHQ", (NSS,)),
 ("N5", VT, 'price_errs = [e for e in errs if e.startswith(("G1", "G2"))]', 'price_errs = list(errs)', "ô giá cũng mất khi G3-G8 hỏng", (VS, NPS, PTS)),
 ("N6", VT, 'if not (e.get("confirmed_by") and e.get("date") and e.get("ticker")):', 'if not (e.get("date") and e.get("ticker")):', "ack G6 không cần người xác nhận", (VS,)),
 ("N7", VT, 'g = d.groupby(["ticker", "exright_date"], as_index=False).value_per_share.sum()', 'g = d.groupby(["ticker", "exright_date"], as_index=False).value_per_share.max()', "đợt cùng ngày lấy max", (VS,)),
 ("N8", VT, 'u["dy_i"] = u["div"] / u.P1', 'u["dy_i"] = u["div"] / u.Price', "dy theo giá phiên t (G6)", (VS,)),
 ("N9", NS, 'if str(rec.get("account_no")) != str(account_no):\n                    continue\n                k = rec.get("kind")', 'k = rec.get("kind")', "div_recv/fills không lọc account (§12)", (NSS,)),
 ("N10", PT, 'if kw in label:', 'if kw.lower() in label.lower():', "khớp nhãn kỳ (đối chứng, kỳ vọng sống)", (PTS,)),
 ("N11", VT, 'if p["n_members"] is not None and r["n_members"] is not None:', 'if p["n_members"] is not None and r["n_members"] is not None and i > 1:', "G4 bỏ phiên đầu kỳ", (VS,)),
]
only = sys.argv[1:] 
for mid, f, a, b, why, checks in M:
    if only and mid not in only: continue
    root = tempfile.mkdtemp(prefix=f"arm_{mid}_"); os.makedirs(root+"/mike"); shutil.copytree(WT, root + "/mike/bin"); open(root+"/wc_env.sh","w").close(); os.symlink("/home/trido/thanhdt/WorkingClaude/trading_bot", root+"/trading_bot"); os.symlink("/home/trido/thanhdt/WorkingClaude/corp_action_lib.py", root+"/corp_action_lib.py"); d = root + "/mike"
    p = d + "/bin/" + f; s = open(p, encoding="utf-8").read()
    n = s.count(a)
    if n != 1: print(mid, "SKIP chuỗi xuất hiện", n, "lần"); continue
    open(p, "w", encoding="utf-8").write(s.replace(a, b))
    res = []
    for c in checks:
        env = {k: v for k, v in os.environ.items() if k not in ("TZ","WC_ROOT")}; env["WC_ROOT"]=root
        r = subprocess.run([sys.executable, d + "/bin/" + c], cwd="/tmp", capture_output=True, text=True, env=env, timeout=900)
        res.append((c, r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1][:110] if (r.stdout + r.stderr).strip() else ""))
    dead = any(rc != 0 for _, rc, _ in res)
    print(mid, "CHẾT" if dead else "SỐNG", "-", why, res)
    shutil.rmtree(root)
