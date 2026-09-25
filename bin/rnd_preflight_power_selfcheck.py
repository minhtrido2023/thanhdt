#!/usr/bin/env python3
"""Selfcheck cho bin/rnd_preflight_power.py. Chạy: $DNA_PYEXE bin/rnd_preflight_power_selfcheck.py"""
import io, os, sys, json, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rnd_preflight_power as M

OK = FAIL = 0
def chk(cond, msg):
    global OK, FAIL
    if cond: OK += 1
    else: FAIL += 1; print(f"  FAIL: {msg}")

def run(*args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        M.main(list(args) + ["--json"])
    return json.loads(buf.getvalue())

print("== 1. Tái lập con số đã PIN của ORB (job Taylor_20260925_120926) ==")
r = run("--mean-bps","6.16","--sd-bps","110.22","--obs-per-year","252",
        "--n-available","1129","--n-trials","20","--n-rule","per-day","--max-history-years","9.13")
chk(abs(r["dsr_now"]-0.4914) < 0.01, f"DSR@1129 pin 0.4914, được {r['dsr_now']:.4f}")
chk(abs(r["n_for_target_dsr"]-4075) < 80, f"N cho DSR0.95 pin 4075, được {r['n_for_target_dsr']}")
chk(abs(r["n_for_power80_2sided"]-2510) < 30, f"power80 pin 2510, được {r['n_for_power80_2sided']:.0f}")
chk(abs(r["dsr_at_max_history"]-0.779) < 0.01, f"DSR tại trần 9.13y pin 0.779, được {r['dsr_at_max_history']:.4f}")
chk(r["verdict"]=="NO-GO", f"phải NO-GO (N cần > trần), được {r['verdict']}")

print("== 2. Trần dữ liệu THẬT SỰ đổi phán (không phải cờ trang trí) ==")
r2 = run("--mean-bps","6.16","--sd-bps","110.22","--obs-per-year","252",
         "--n-available","1129","--n-trials","20","--n-rule","per-day")
chk(r2["verdict"]=="MARGINAL", f"không có trần -> MARGINAL, được {r2['verdict']}")
chk(r["verdict"]!=r2["verdict"], "bỏ --max-history-years phải đổi phán")

print("== 3. Edge đủ mạnh + đủ dữ liệu -> GO ==")
r3 = run("--sharpe-ann","1.9","--obs-per-year","252","--n-available","3000",
         "--n-trials","20","--n-rule","per-day")
chk(r3["verdict"]=="GO", f"Sharpe 1.9 n=3000 phải GO, được {r3['verdict']}")
chk(r3["n_for_target_dsr"] <= 3000, "N cần phải <= N có sẵn khi GO")

print("== 4. N_trials cao làm ngưỡng KHẮT KHE hơn (deflate thật sự hoạt động) ==")
a = run("--sharpe-ann","1.2","--obs-per-year","252","--n-available","3000","--n-trials","5","--n-rule","per-day")
b = run("--sharpe-ann","1.2","--obs-per-year","252","--n-available","3000","--n-trials","100","--n-rule","per-day")
chk(b["dsr_now"] < a["dsr_now"], f"N_trials 100 phải cho DSR thấp hơn 5: {b['dsr_now']:.4f} vs {a['dsr_now']:.4f}")
chk(b["n_for_target_dsr"] > a["n_for_target_dsr"], "N_trials cao phải cần N lớn hơn")

print("== 5. Market-timing đếm per-episode: 13 episode KHÔNG BAO GIỜ đủ ==")
r5 = run("--sharpe-ann","1.5","--obs-per-year","4","--n-available","13","--n-trials","10","--n-rule","per-episode")
chk(r5["verdict"]!="GO", f"13 episode không được GO, được {r5['verdict']}")
chk(r5["n_for_target_dsr"] is None or r5["n_for_target_dsr"] > 13, "N cần phải > 13")
chk(r5["effect_multiple_needed"] > 1.0, "phải đòi effect lớn hơn giả định")

print("== 6. --n-rule là BẮT BUỘC (không cho chạy mà không khai cách đếm N) ==")
try:
    with contextlib.redirect_stderr(io.StringIO()):
        M.main(["--sharpe-ann","1.0","--obs-per-year","252","--n-available","1000"])
    chk(False, "thiếu --n-rule phải lỗi")
except SystemExit as e:
    chk(e.code != 0, "thiếu --n-rule phải exit != 0")

print("== 7. Tính đơn điệu: N càng lớn DSR càng cao, cùng effect ==")
prev = -1
for n in (500, 1000, 2000, 4000):
    v = run("--sharpe-ann","1.0","--obs-per-year","252","--n-available",str(n),
            "--n-trials","20","--n-rule","per-day")["dsr_now"]
    chk(v > prev, f"DSR phải tăng theo N tại n={n}"); prev = v

print("== 8. Sharpe = 0 -> không bao giờ đạt ==")
r8 = run("--mean-bps","0","--sd-bps","100","--obs-per-year","252","--n-available","5000",
         "--n-trials","20","--n-rule","per-day")
chk(r8["n_for_target_dsr"] is None, "Sharpe 0 phải trả None (không bao giờ đạt)")
chk(r8["verdict"]=="NO-GO", f"Sharpe 0 phải NO-GO, được {r8['verdict']}")

print(f"\n{OK} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
