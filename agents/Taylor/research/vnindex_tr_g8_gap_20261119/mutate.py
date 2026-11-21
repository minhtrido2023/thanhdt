"""Mutation test: mỗi mutant tắt một phần của bản vá (sao chép bin/ của WORKTREE vào thư mục tạm, sửa,
chạy selfcheck bản sao). Selfcheck PHẢI đỏ ở mọi mutant. Đường dẫn worktree truyền qua argv[1]."""
import os, shutil, subprocess, sys, tempfile
BIN = os.path.join(os.path.abspath(sys.argv[1]), "bin")
MUT = {
    "M1 bỏ token osh": ('        tok.setdefault(t, []).append(f"{tk}:osh:{int(n)}")', "        pass"),
    "M2 bỏ token row": ('                tok.setdefault(t, []).append(f"{code}:row:{st.isoformat()}")', "                pass"),
    "M3 cổng bỏ qua g8_new": ('    for tk, cause, val in r.get("g8_new") or []:\n        if g8_new_acked', '    for tk, cause, val in []:\n        if g8_new_acked'),
    "M4 bỏ ngưỡng N phiên (osh)": ("s.npx.ge(G8_NEW_MIN_SESSIONS)", "s.npx.ge(0)"),
    "M5 bỏ first_seen (row dùng cửa sổ)": ("        if first_seen and first_seen.get(code) is not None:", "        if False:"),
    "M6 bỏ ack G8_NEW": ('        if g8_new_acked(acks, r["date"], tk, cause):\n            continue\n        why', '        if False:\n            continue\n        why'),
    "M7 bỏ cảnh báo sealed drift": ("            if drift and warn is not None:", "            if False:"),
    "MB f<=t -> f<t (dòng đầu đúng ngày t)": ("            if f is not None and f <= t:", "            if f is not None and f < t:"),
    "MD ~S1_ff -> ~S1 (thiếu OShares 1 ngày)": ("nosh = s[base & ~s.S1_ff.gt(0)", "nosh = s[base & ~s.S1.gt(0)"),
    "M8 G8_NEW không vào seal_blockers": ("+ _g8_new_errs(r, acks, restating)\n", "\n"),
    "M9 bỏ lookback panel": ("    return since - dt.timedelta(days=G8_NEW_LOOKBACK_DAYS)", "    return since"),
    "M10 fetch_bq không dùng bq_panel_start": ("WHERE t.time >= '{bq_panel_start(since).isoformat()}'", "WHERE t.time >= '{since.isoformat()}'"),
    "M11 ack khoảng ngày bỏ cận date_to": ("and k[3] <= d <= k[4] for k in acks)", "and k[3] <= d for k in acks)"),
    "M12 ack khoảng ngày bỏ decided_by": ('        if e.get("decided_by") != "user":', "        if False:"),
    "M13 drift n tol thành mc-only": ("        if abs(dev) >= tol if col == \"n_members\" else abs(dev) > tol:", "        if col == \"mc_members_vnd\" and abs(dev) > tol:"),
    "M15 ffill OShares không giới hạn K (từ đầu panel)": ("osh_w.ffill(limit=G8_NEW_K).shift(1)", "osh_w.ffill().shift(1)"),
    "M16 npx cộng dồn từ đầu panel (không cửa sổ K)": ("px_w.astype(float).rolling(G8_NEW_K, min_periods=1).sum()", "px_w.astype(float).cumsum()"),
    "M17 vị trí phiên từ idx cắt ở mốc dựng": ('''                          sess_full=panel[panel.ticker == "VNINDEX"].set_index("time").Price)''', '''                          sess_full=None)'''),
    "M18 thông báo restate không phân biệt ngữ cảnh": ("               if restating else\n", "               if False else\n"),
    "M14 g8_new_open không xuất": ("    if opn:                         # báo động", "    if False:                       # báo động"),
}
fails = 0
for name, (a, b) in MUT.items():
    with tempfile.TemporaryDirectory(prefix="vtr_mut_") as tmp:
        for f in ("vnindex_total_return.py", "vnindex_total_return_selfcheck.py", "wc_paths.py"):
            shutil.copy(os.path.join(BIN, f), tmp)
        p = os.path.join(tmp, "vnindex_total_return.py")
        s = open(p, encoding="utf-8").read()
        assert s.count(a) == 1, (name, s.count(a))
        open(p, "w", encoding="utf-8").write(s.replace(a, b))
        env = {**os.environ, "WC_ROOT": "/home/trido/thanhdt/WorkingClaude"}
        cp = subprocess.run([sys.executable, os.path.join(tmp, "vnindex_total_return_selfcheck.py")],
                            capture_output=True, text=True, env=env, timeout=900)
        red = cp.returncode != 0
        fails += not red
        last = (cp.stderr.strip().splitlines() or cp.stdout.strip().splitlines() or [""])[-1][:160]
        print(f"{'ĐỎ (tốt)' if red else 'XANH (HỎNG!)'} rc={cp.returncode} {name}: {last}")
print("mutant sống sót:", fails)
sys.exit(1 if fails else 0)
