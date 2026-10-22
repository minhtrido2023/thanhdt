#!/usr/bin/env python3
"""Chạy mỗi case MỘT lần claude -p opus (không công cụ, cwd /tmp), song song 6. Lỗi kỹ thuật thử lại CÙNG prompt (<=3 lần).
Không đổi prompt. Resumable: bỏ qua case đã có raw/E###.txt hợp lệ. Dừng nếu >50% lần gọi lỗi."""
import json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
D = os.path.dirname(os.path.abspath(__file__))
SYS = open(f"{D}/system_prompt.txt").read().strip(); Q = open(f"{D}/question.txt").read()
cases = [json.loads(l) for l in open(f"{D}/cases.jsonl")]
RE = re.compile(r"P_HIT15:\s*([01](?:\.\d+)?)\s*\n\s*RISK:\s*(LOW|MED|HIGH)\s*\n\s*P_POS:\s*([01](?:\.\d+)?)", re.I)
stat = {"calls": 0, "fail": 0}
def run(c):
    out = f"{D}/raw/{c['id']}.txt"
    if os.path.exists(out) and RE.search(open(out).read()): return True
    prompt = Q + "\n\nDỮ LIỆU:\n" + c["data"]
    for a in range(3):
        stat["calls"] += 1
        try:
            p = subprocess.run(["claude", "-p", "--model", "opus", "--tools", "", "--setting-sources", "", "--disable-slash-commands",
                                "--strict-mcp-config", "--no-session-persistence", "--system-prompt", SYS],
                               input=prompt, capture_output=True, text=True, cwd="/tmp", timeout=300)
            txt = p.stdout
            if p.returncode == 0 and RE.search(txt):
                open(out, "w").write(txt); return True
            err = (p.stderr or txt)[:200]
        except subprocess.TimeoutExpired:
            err = "timeout"
        stat["fail"] += 1
        print(f"[fail] {c['id']} try{a+1}: {err!r}", flush=True)
        if stat["calls"] >= 30 and stat["fail"] / stat["calls"] > 0.5: print("ABORT >50% lỗi", flush=True); os._exit(3)
        time.sleep(5 * (a + 1))
    return False
t0 = time.time(); done = 0
with ThreadPoolExecutor(6) as ex:
    for ok in ex.map(run, cases):
        done += 1
        if done % 20 == 0: print(f"{done}/{len(cases)} {time.time()-t0:.0f}s fail={stat['fail']}/{stat['calls']}", flush=True)
print("FINISHED", sum(os.path.exists(f"{D}/raw/{c['id']}.txt") for c in cases), "ok; fail", stat, flush=True)
