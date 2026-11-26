#!/usr/bin/env python3
"""Selfcheck bin/prune_depth_gate.py (arch-review vòng 2 việc B #6 + mutation, 25/11/2026).
Không gọi BQ thật: decide() trực tiếp + main() với `bq` giả trên PATH (đường query_counts).
Mỗi ca ghi rõ mutation nó giết."""
import shutil
import atexit
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = Path(os.environ.get("PDG_TARGET", HERE / "prune_depth_gate.py"))
sys.path.insert(0, str(TARGET.parent))
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("pdg", TARGET)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

FAILS = 0
# 20 phiên THẬT trước 23/11/2026 (BQ ticker_prune, đo 25/11) — trung vị 203 ⇒ ngưỡng 183.
REAL = [205, 205, 205, 204, 204, 204, 204, 203, 203, 203, 203, 203, 202, 202, 202, 202, 201, 201, 201, 197]


def chk(cond, name, out=""):
    global FAILS
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS += 1
        print("   output:", out)


def v(n, prior):
    verdict, info = P.decide(n, prior)
    return verdict, info


FAKE_BQ = r"""#!/usr/bin/env python3
# bq giả: lọc hàng theo ĐÚNG cửa sổ trong SQL (INTERVAL N DAY quanh DATE('x') hoặc MAX) — giết mutant LOOKBACK;
# ghi CLOUDSDK_CONFIG thấy được ra file; CLOUDSDK_CONFIG sai/thiếu ⇒ lỗi y như bq thật (invalid_scope).
import datetime as dt, json, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(here, "cloudsdk_seen"), "a").write(repr(os.environ.get("CLOUDSDK_CONFIG")) + "\n")
want = open(os.path.join(here, "want_cfg")).read().strip() if os.path.exists(os.path.join(here, "want_cfg")) else ""
if want and os.environ.get("CLOUDSDK_CONFIG") != want:
    print("BigQuery error in query operation: invalid_scope: Bad Request", file=sys.stderr); sys.exit(1)
rows = json.load(open(os.path.join(here, "rows.json")))
sql = sys.argv[-1]
m = re.search(r"DATE\('(\d{4}-\d{2}-\d{2})'\)", sql)
tg = dt.date.fromisoformat(m.group(1)) if m else max(dt.date.fromisoformat(d) for d, _ in rows)
lb = int(re.search(r"INTERVAL (\d+) DAY", sql).group(1))
print("dt,n")
for d, n in rows:
    if tg - dt.timedelta(days=lb) <= dt.date.fromisoformat(d) <= tg:
        print(f"{d},{n}")
"""


def run_cli(rows, date_arg=None, reseed=None, envi=False, wc_env=None, want_cfg=None):
    """rows=[(date, n)] ⇒ bq giả (lọc theo cửa sổ SQL); chạy main() thật qua subprocess.
    reseed=dict ⇒ file reseed tạm; None ⇒ file không tồn tại. envi=True ⇒ `env -i` (như cron trần)."""
    td = Path(tempfile.mkdtemp(prefix="pdg_sc_"))
    atexit.register(shutil.rmtree, td, True)  # P3-5: không rò /tmp
    (td / "bq").write_text(FAKE_BQ)
    (td / "bq").chmod(0o755)
    (td / "rows.json").write_text(json.dumps(rows))
    if want_cfg:
        (td / "want_cfg").write_text(want_cfg)
    rf = td / "reseed.json"
    if reseed is not None:
        rf.write_text(reseed if isinstance(reseed, str) else json.dumps(reseed))
    args = ["--date", date_arg] if date_arg else ["--latest"]
    if envi:
        env = {"PATH": f"{td}:/usr/bin:/bin", "PDG_RESEED_FILE": str(rf)}
        if wc_env:
            env["PDG_WC_ENV"] = wc_env
    else:
        env = dict(os.environ, PATH=f"{td}:{os.environ['PATH']}", PDG_RESEED_FILE=str(rf))
    r = subprocess.run([sys.executable, str(TARGET)] + args, capture_output=True, text=True, timeout=60, env=env)
    seen = (td / "cloudsdk_seen").read_text() if (td / "cloudsdk_seen").exists() else ""
    run_cli.seen = seen
    return r.returncode, r.stdout + r.stderr


def weekdays(n, start="2026-04-01"):
    d, out = dt.date.fromisoformat(start), []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(str(d))
        d += dt.timedelta(days=1)
    return out


def days(n, start="2026-08-01"):
    d0 = dt.date.fromisoformat(start)
    return [str(d0 + dt.timedelta(days=i)) for i in range(n)]


def main():
    vd, info = v(197, REAL)
    chk(vd == "PASS" and info["threshold"] == 183, "T1 ca thật 23/11: 197 vs trung vị 203 ⇒ ngưỡng 183, QUA", info)
    vd, info = v(183, REAL)
    chk(vd == "PASS", "T2 biên n == ngưỡng (183) ⇒ QUA  [giết: >= → >]", info)
    vd, info = v(182, REAL)
    chk(vd == "FAIL", "T2b 182 = ngưỡng−1 ⇒ CHẶN", info)
    # T3 (#6): universe 202 rồi chuỗi ghi thiếu 170 kéo dài — MỌI phiên trong chuỗi 1..40 PHẢI vẫn chặn
    base = [202] * 30
    bad = [k for k in range(1, 41) if v(170, base + [170] * (k - 1))[0] != "FAIL"]
    chk(not bad, "T3 chuỗi ghi thiếu 170 sau universe 202: phiên thứ 1..40 của chuỗi ĐỀU chặn (trước: phiên 11 tự qua)",
        f"phiên tự qua: {bad[:5]}")
    vd, info = v(170, base + [170] * 14)
    chk(vd == "FAIL" and info["threshold"] == 182 and info["dropped"] == 14,
        "T3b phiên thứ 15: ngưỡng vẫn 182 (trung vị 202), 14 phiên FAIL bị loại khỏi trung vị, dòng in nêu rõ", info)
    chk("loại_khỏi_trung_vị=14" in P.fmt(vd, "x", info), "T3c fmt nêu số phiên bị loại", P.fmt(vd, "x", info))
    vd, info = v(201, base + [170] * 14)
    chk(vd == "PASS", "T3d hết chuỗi, số mã về 201 ⇒ QUA (không kẹt vĩnh viễn khi dữ liệu hồi)", info)
    # T4 phân bố lệch: 15×200 + 5×400 ⇒ trung vị 200 (ngưỡng 180) ≠ trung bình 250 (ngưỡng 225)
    vd, info = v(200, [200] * 8 + [400] * 5 + [200] * 7)
    chk(vd == "PASS" and info["threshold"] == 180, "T4 phân bố lệch: trung vị (không phải trung bình)  [giết: median → mean]", info)
    # T5 >20 phiên lịch sử, trôi chậm: 20×260 rồi 20×240 ⇒ cửa sổ = 20 phiên GẦN NHẤT (ngưỡng 216), không phải 20 đầu (234)
    vd, info = v(220, [260] * 20 + [240] * 20)
    chk(vd == "PASS" and info["threshold"] == 216, "T5 cửa sổ = 20 phiên mới nhất  [giết: [-window:] → [:window]]", info)
    # T6 lọc sàn hạt giống (thay lọc >0): 12 phiên 0/thiếu + 19 phiên thật ⇒ chỉ 19 hợp lệ ⇒ KHÔNG ĐO ĐƯỢC
    vd, info = v(200, [0] * 12 + [200] * 19)
    chk(vd == "UNMEASURABLE", "T6 phiên 0 mã không tính là lịch sử  [giết: bỏ lọc sàn/>0 hạt giống]", info)
    vd, info = v(200, [0] * 12 + [200] * 20)
    chk(vd == "PASS", "T6b đủ 20 phiên thật ⇒ đo được", info)
    # T7 đường query_counts: 19 phiên trước + chính ngày xét ⇒ ngày xét KHÔNG được tính vào lịch sử
    ds = days(20)
    rc, out = run_cli([(d, 200) for d in ds[:19]] + [(ds[19], 200)])
    chk(rc == 2 and "UNMEASURABLE" in out and "19/20" in out,
        "T7 --latest: 19 phiên trước + ngày xét ⇒ KHÔNG ĐO ĐƯỢC (ngày xét không vào prior)  [giết: d < date → <=]", out)
    rc, out = run_cli([(d, 203) for d in days(21)[:20]] + [(days(21)[20], 183)])
    chk(rc == 0 and "PRUNE_DEPTH PASS" in out and "threshold=183" in out, "T7b --latest 20 phiên trước ⇒ QUA rc=0", out)
    rc, out = run_cli([(d, 203) for d in days(20)], date_arg="2026-08-21")
    chk(rc == 1 and "n=0" in out, "T7c --date ngày CHƯA ingest ⇒ n=0 ⇒ CHẶN rc=1", out)
    rc, out = run_cli([(d, 202) for d in days(30)] + [(d, 170) for d in days(45)[30:]])
    chk(rc == 1 and "PRUNE_DEPTH FAIL" in out and "n=170" in out,
        "T7d --latest chuỗi 15 phiên ghi thiếu qua đường BQ ⇒ vẫn CHẶN rc=1", out)
    # T8 (vòng cuối #5a): phiên ĐÚNG BẰNG ngưỡng PHẢI vào lịch sử  [giết: accepted_history >= → >]
    vd, info = v(200, [200] * 20 + [180])
    chk(vd == "PASS" and info["dropped"] == 0, "T8 phiên trước = ngưỡng (180) được NHẬN vào lịch sử (dropped=0)  [giết: >= → >]", info)
    vd, info = v(150, [150] * 20)
    chk(vd == "PASS", "T8b hạt giống đúng bằng sàn 150 được nhận  [giết: x >= floor → >]", info)
    # T9 (vòng cuối #5b): qua ĐƯỜNG QUERY (bq giả lọc theo INTERVAL của SQL): 25 phiên 202 rồi 45 phiên ghi thiếu
    # 170 (≈98 ngày lịch) ⇒ LOOKBACK 150 còn hạt giống sạch ⇒ CHẶN; LOOKBACK 75 chỉ còn ~8 phiên 202 ⇒ tự qua.
    ds = weekdays(70)
    rows = [(d, 202) for d in ds[:25]] + [(d, 170) for d in ds[25:]]
    rc, out = run_cli(rows)
    chk(rc == 1 and "n=170" in out and "threshold=182" in out,
        "T9 --latest chuỗi ghi thiếu 45 phiên (≥40) qua đường query ⇒ vẫn CHẶN  [giết: LOOKBACK 150 → 75]", out)
    rc, out = run_cli(rows, date_arg=ds[-1])
    chk(rc == 1 and "threshold=182" in out, "T9b --date cùng chuỗi ⇒ CHẶN", out)
    # T10 (vòng cuối #1): `env -i` (cron trần, không source wc_env.sh) ⇒ tự nạp CLOUDSDK_CONFIG ĐÚNG từ wc_env.sh
    wc_env = Path(P.WC_ENV)
    want = next((l.split("=", 1)[1].split()[0] for l in wc_env.read_text().splitlines()
                 if l.startswith("export CLOUDSDK_CONFIG=")), None) if wc_env.is_file() else None
    ok_rows = [(d, 203) for d in weekdays(21)]
    rc, out = run_cli(ok_rows, envi=True, want_cfg=want or "x")
    chk(want and rc == 0 and "PRUNE_DEPTH PASS" in out and run_cli.seen.strip() == repr(want),
        f"T10 env -i ⇒ bq thấy CLOUDSDK_CONFIG={want} (nạp từ {wc_env}), PASS", out + " seen=" + run_cli.seen)
    rc, out = run_cli(ok_rows, envi=True, wc_env="/nonexistent/wc_env.sh", want_cfg=want or "x")
    chk(rc == 2 and "UNMEASURABLE" in out and "CLOUDSDK_CONFIG" in out and not run_cli.seen,
        "T10b env -i + không có wc_env.sh ⇒ UNMEASURABLE nêu rõ thiếu CLOUDSDK_CONFIG, KHÔNG gọi bq", out)
    rc, out = run_cli(ok_rows, want_cfg="/wrong/cfg")
    chk(rc == 2 and "invalid_scope" in out, "T10c bq lỗi auth ⇒ UNMEASURABLE trích lỗi thật (invalid_scope)", out)
    # T11 (vòng cuối #4): universe co THẬT −12% (202 → 178) — lối thoát của người qua file reseed
    ds = weekdays(34)
    rows = [(d, 202) for d in ds[:30]] + [(ds[30], 178)]
    rc, out = run_cli(rows)
    chk(rc == 1 and "RUNBOOK" in out and "prune_depth_reseed.json" in out,
        "T11 co −12% một lần, không có reseed ⇒ CHẶN, dòng FAIL kèm RUNBOOK lối thoát", out)
    good = {"reseed_from": ds[30], "source": "team dữ liệu xác nhận universe co (ticket X)"}
    rc, out = run_cli(rows, reseed=good)
    chk(rc == 0 and "RESEED_FROM=" + ds[30] in out and "threshold=150" in out,
        "T11b file reseed hợp lệ (reseed_from = phiên co) ⇒ QUA (chưa có phiên mới ⇒ chỉ sàn)", out)
    rows3 = rows + [(ds[31], 178), (ds[32], 177), (ds[33], 178)]
    rc, out = run_cli(rows3, reseed=good)
    chk(rc == 0 and "threshold=161" in out, "T11c 3 phiên sau reseed ⇒ ngưỡng theo trung vị universe MỚI (161), QUA", out)
    rc, out = run_cli(rows3[:-1] + [(ds[33], 120)], reseed=good)
    chk(rc == 1 and "n=120" in out, "T11d sau reseed vẫn chặn rớt đột ngột (120 < 161) — reseed không phải tắt cổng", out)
    rc, out = run_cli(rows, reseed={"reseed_from": ds[30], "source": ""})
    chk(rc == 1 and "thiếu source" in out, "T11e reseed THIẾU source ⇒ bỏ qua, vẫn CHẶN (fail-closed)", out)
    rc, out = run_cli(rows, reseed="{hỏng")
    chk(rc == 1 and "file hỏng" in out, "T11f file reseed hỏng ⇒ bỏ qua, vẫn CHẶN", out)
    rc, out = run_cli(rows, reseed={"reseed_from": "25/11/2026", "source": "x"})
    chk(rc == 1 and "sai định dạng" in out, "T11g reseed_from sai định dạng ⇒ bỏ qua, vẫn CHẶN", out)
    rc, out = run_cli(rows[:-1] + [(ds[30], 7)], reseed=good)
    chk(rc == 1 and "threshold=150" in out, "T11h reseed KHÔNG nới sàn: 7 mã ⇒ CHẶN", out)
    rows_j = rows + [(ds[31], 155), (ds[32], 155)]
    rc, out = run_cli(rows_j, reseed=good)
    chk(rc == 1 and "n=155" in out and "threshold=161" in out,
        "T11j reseed 178 → 155 (FAIL) → 155: phiên FAIL KHÔNG vào trung vị pha hạt giống ⇒ vẫn CHẶN (reviewer P2)", out)
    shipped = json.loads((HERE.parent / "config" / "prune_depth_reseed.json").read_text())
    rf, src = shipped.get("reseed_from"), str(shipped.get("source") or "").strip()
    chk((rf is None and not src) or (bool(src) and bool(P.DATE_RE.match(str(rf)))),
        "T11i file thật: reseed TẮT, hoặc reseed_from YYYY-MM-DD kèm source (người bật hợp lệ không làm đỏ test)", shipped)


if __name__ == "__main__":
    main()
    print(f"prune_depth_gate_selfcheck: {'PASS' if FAILS == 0 else f'FAIL ({FAILS})'}")
    sys.exit(1 if FAILS else 0)
