#!/usr/bin/env python3
"""Selfcheck cho bin/measured_by_warn_report.py (2026-10-13). Bus tạm sandbox, now cố định bằng --now.
Chạy: python3 bin/measured_by_warn_report_selfcheck.py   (nên chạy dưới cả `env -u TZ`, TZ=America/New_York,
TZ=Pacific/Kiritimati — kết quả KHÔNG được phụ thuộc TZ)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HELPER = os.path.join(ROOT, "bin", "measured_by_warn_report.py")
NOW = "2026-10-13T00:30:00Z"           # = 07:30 ICT 13/10
_fails = []


def check(name, cond, detail=""):
    print(("  PASS  " if cond else "  FAIL  ") + name + ("" if cond else " — " + detail))
    if not cond:
        _fails.append(name)


def run(bus, extra=()):
    p = subprocess.run([sys.executable, HELPER, "--bus", bus, "--now", NOW, *extra],
                       capture_output=True, text=True, timeout=30)
    return p.returncode, p.stdout, p.stderr


def snap(bus):
    out = {}
    for dp, _, fs in os.walk(bus):
        for f in fs:
            fp = os.path.join(dp, f)
            out[fp] = (os.path.getmtime(fp), open(fp, "rb").read())
    return out


def mk():
    d = tempfile.mkdtemp(prefix="mbwr_")
    os.makedirs(os.path.join(d, "inbox"))
    return d


def w(d, name, lines):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        for ln in lines:
            f.write((ln if isinstance(ln, str) else json.dumps(ln)) + "\n")


def warn(ts, agent, topic, trace):
    return {"ts": ts, "warn": "finding_missing_measured_by", "agent_id": agent, "topic": topic,
            "trace_id": trace}


def finding(ts, et="finding"):
    return {"ts": ts, "event_type": et, "agent_id": "x", "topic": "t"}


# --- ca "chưa có dữ liệu" (fail-open, rc=0) ---
d = mk()
rc, out, _ = run(d)
check("file thiếu ⇒ chưa có dữ liệu, rc=0", rc == 0 and "chưa có dữ liệu" in out, out)
w(d, "_measured_by_warn.jsonl", [])
rc, out, _ = run(d)
check("file rỗng ⇒ chưa có dữ liệu, rc=0", rc == 0 and "chưa có dữ liệu" in out, out)
w(d, "_measured_by_warn.jsonl", ["{hỏng", "[1,2]", '"x"', json.dumps({"ts": "không-phải-ngày"}), json.dumps({"no": "ts"})])
rc, out, _ = run(d)
check("toàn dòng hỏng/không ts ⇒ chưa có dữ liệu, rc=0", rc == 0 and "chưa có dữ liệu" in out, out)
rc, out, _ = run(os.path.join(d, "không-có-thư-mục-này"))
check("bus không tồn tại ⇒ rc=0 chưa có dữ liệu", rc == 0 and "chưa có dữ liệu" in out, out)
bad = os.path.join(d, "afile")
open(bad, "w").close()
rc, out, _ = run(bad)
check("bus là FILE ⇒ rc=0 chưa có dữ liệu", rc == 0 and "chưa có dữ liệu" in out, out)
shutil.rmtree(d)

# --- ca đếm ---
d = mk()
w(d, "_measured_by_warn.jsonl", [
    "rác không phải json",
    warn("2026-10-12T23:00:00Z", "Taylor", "A", "Taylor_1"),            # 1.5h trước: trong 24h, có trace
    warn("2026-10-12T23:00:00Z", "Taylor", "A", "Taylor_2"),            # agent trùng, topic trùng
    warn("2026-10-12T05:00:00Z", "Wags", "B", None),                    # 19.5h: trong 24h, null trace
    warn("2026-10-12T05:00:00Z", "Wags", "B", ""),                      # trace rỗng ⇒ script/cron
    warn("2026-10-12T05:00:00Z", "Wags", "B", "   "),                   # trace chỉ khoảng trắng ⇒ cron
    warn("2026-10-12T00:29:59Z", "Winston", "C", "W_1"),                # 24h00m01s: NGOÀI 24h, trong 48h
    warn("2026-10-12T00:30:00Z", "Winston", "C", "W_2"),                # đúng 24h00m00s: TRONG 24h (biên đóng)
    warn("2026-10-11T00:30:00Z", "Mike", "D", None),                    # đúng 48h: trong 7ng, "24h trước" (biên)
    warn("2026-10-06T00:30:01Z", "Mike", "D", None),                    # 6d23h59m59s: trong 7ng
    warn("2026-10-06T00:30:00Z", "Mike", "D", None),                    # đúng 7d: TRONG 7ng (biên đóng)
    warn("2026-09-01T00:00:00Z", "Cũ", "E", "c"),                       # rất cũ
    warn("2026-10-13T00:30:01Z", "Future", "F", "f"),                   # tương lai: loại
])
w(d, "inbox/Taylor.jsonl", [finding("2026-10-12T10:00:00Z"), finding("2026-10-12T10:00:00Z", "status"),
                            finding("2026-10-05T10:00:00Z"), "hỏng", finding("2026-10-13T00:30:01Z"),
                            finding("2026-10-06T00:30:00Z")])
w(d, "inbox/Wags.jsonl", [finding("2026-10-12T11:00:00Z"), finding("2026-10-12T00:30:00Z")])
before = snap(d)
rc, out, err = run(d)
print(out)
check("rc=0", rc == 0)
check("đúng 5 dòng (1 khối ngắn)", len(out.strip().splitlines()) == 5, out)
# 24h: Taylor×2 + Wags×3 + W_2 = 6 ; 24h trước (24h,48h]: W_1 + Mike(đúng 48h) = 2 ; 7ng (tuổi ≤7d, biên đóng) = 6+2+Mike(6d23h)+Mike(đúng 7d) = 10
check("cảnh báo 24h=6, 24h trước=2, 7ng=10", "24h=6 (24h trước đó=2) · 7ng=10" in out, out)
# finding: 24h = Taylor 1 + Wags 2 = 3 ; 7ng = 3 + Taylor(đúng 7d) = 4 (10-05T10 = 7d14h ⇒ ngoài)
check("finding 24h=3, 7ng=4 (status/hỏng/tương lai/7d14h bị loại; đúng 7d tính)", "finding: 24h=3 · 7ng=4" in out, out)
check("tỉ lệ 24h=200.0% 7ng=250.0% (đếm theo code, mẫu số riêng)", "24h=200.0% · 7ng=250.0%" in out, out)
check("nguồn 24h: có trace=3 · không trace=3", "24h: có trace_id (agent dispatch)=3 · không trace_id (script/cron)=3" in out, out)
check("nguồn 7ng: có trace=3 · không trace=6", "7ng: 4 · 6" in out, out)
check("agent top: Mike=3, Wags=3 (hoà ⇒ theo tên), Taylor=2, Winston=2", "Mike=3, Wags=3, Taylor=2, Winston=2" in out, out)
check("topic top: B=3, D=3, A=2, C=2", "B=3, D=3, A=2, C=2" in out, out)
check("không có 'Future'/'Cũ' (ngoài cửa sổ/tương lai)", "Future" not in out and "Cũ" not in out, out)
check("giờ in ra theo ICT: 13/10/2026 07:30", "13/10/2026 07:30 ICT" in out, out)
check("ĐỌC-ONLY: bus không đổi byte/mtime", snap(d) == before)
check("stderr rỗng", err == "", err)
shutil.rmtree(d)

# --- top-8 agent / top-5 topic ---
d = mk()
w(d, "_measured_by_warn.jsonl", [warn("2026-10-12T20:00:00Z", "ag%02d" % i, "tp%02d" % i, "t") for i in range(12)])
rc, out, _ = run(d)
def line(prefix):
    return next((l for l in out.splitlines() if l.strip().startswith(prefix)), ": ").split(": ", 1)[1]
ag, tp = line("agent_id"), line("topic")
check("top 8 agent / top 5 topic", len(ag.split(", ")) == 8 and len(tp.split(", ")) == 5, ag + " | " + tp)
check("không có finding ⇒ tỉ lệ n/a (không chia 0)", "n/a" in out, out)
shutil.rmtree(d)

# --- dòng lồng quá sâu (RecursionError) bị bỏ qua như dòng hỏng, dòng hợp lệ còn lại vẫn đếm ---
d = mk()
w(d, "_measured_by_warn.jsonl", ["[" * 200000, warn("2026-10-12T20:00:00Z", "a", "t", None)])
rc, out, _ = run(d)
check("dòng lồng 200000 tầng: rc=0, bản ghi hợp lệ vẫn đếm", rc == 0 and "24h=1 " in out, out)
shutil.rmtree(d)

# --- lớp bảo vệ CUỐI ở main: build() nổ bất kỳ ngoại lệ nào ⇒ in "chưa có dữ liệu", rc=0 ---
d = mk()
w(d, "_measured_by_warn.jsonl", [warn("2026-10-12T20:00:00Z", "a", "t", None)])
src = open(HELPER, encoding="utf-8").read().replace("def build(", "def _orig_build(") \
    + "\n\ndef build(*a, **k):\n    raise ZeroDivisionError('mô phỏng lỗi bất ngờ')\n"
# `__main__` guard nằm trước def build ⇒ phải đặt guard SAU: tách main-guard ra cuối.
head, _, tail = src.partition('if __name__ == "__main__":')
patched = os.path.join(d, "patched.py")
open(patched, "w", encoding="utf-8").write(head + '\nif __name__ == "__main__":' + tail)
p = subprocess.run([sys.executable, patched, "--bus", d, "--now", NOW], capture_output=True, text=True, timeout=30)
check("build() nổ ZeroDivisionError ⇒ rc=0 và 'chưa có dữ liệu'", p.returncode == 0 and "chưa có dữ liệu" in p.stdout,
      "rc=%s out=%r err=%r" % (p.returncode, p.stdout, p.stderr[-200:]))
shutil.rmtree(d)

# --- topic dài/nhiều dòng bị cắt, không phá khối 5 dòng ---
d = mk()
w(d, "_measured_by_warn.jsonl", [warn("2026-10-12T20:00:00Z", "a", "x\n" + "y" * 500 + "\nz", "t")])
rc, out, _ = run(d)
check("topic nhiều dòng/quá dài không phá khối (vẫn 5 dòng, mỗi dòng ≤300 ký tự)",
      len(out.strip().splitlines()) == 5 and max(len(l) for l in out.splitlines()) < 300, out)
shutil.rmtree(d)

print("\n" + ("OK: toàn bộ assertion PASS" if not _fails else "FAIL: %d assertion: %s" % (len(_fails), _fails)))
sys.exit(1 if _fails else 0)
