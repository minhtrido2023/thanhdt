#!/usr/bin/env python3
"""Cổng ĐỘ SÂU ticker_prune — NGUỒN DUY NHẤT cho bq_freshness_check.sh và daily_refresh_v34b_linux.sh.

Luật (user duyệt "B" 25/11/2026, sự cố "không ra plan 25/11"):
    FAIL khi n < max(FLOOR, ceil(RATIO × trung vị n của WINDOW phiên liền trước ĐÃ có dữ liệu)).
Ngưỡng cứng 200 cũ chặn oan phiên thật 23/11 (197 mã) vì universe thu hẹp DẦN (trung vị/tháng
2026: T7 219 → T8 215 → T9 212 → T10 205 → T11 202). Ngưỡng tương đối bám theo trôi chậm nhưng
vẫn chặn rớt ĐỘT NGỘT (ghi thiếu/moi ruột, vd sự cố 07-2026 còn 7-10 mã/ngày).

Số đo (BQ ticker_prune 2012-01-03→2026-11-23, 3.695 phiên có đủ 20 phiên trước):
  * tỉ lệ n / trung vị-20 thấp nhất từ 2016: 0,919 (2022-11-15: 251/273) ⇒ RATIO 0,90 không chặn
    oan phiên nào 2016→nay; 16 phiên <0,90 đều ≤2015 (đứt gãy universe 09-10/2015: 156→107).
  * n nhỏ nhất mỗi năm 2017-2026: 170 168 171 171 267 251 239 252 253 197 ⇒ FLOOR 150 ≈ 0,9×168
    (đáy 2017+), thấp hơn 197 hiện tại; universe co dưới 150 = cần người xem lại, không tự qua.
  * ca 23/11 (đo BQ 25/11): 197 vs trung vị 20 phiên trước 203 ⇒ ngưỡng 183 ⇒ QUA.  202→150 ⇒ CHẶN.

Trung vị NEO vào phiên ĐÃ QUA CỔNG (arch-review vòng 2 #6, 25/11): trước đây trung vị lấy 20 phiên trước BẤT KỂ
phiên đó có FAIL không ⇒ một chuỗi ghi thiếu kéo dài tự đầu độc trung vị (202 rồi chuỗi 170: phiên thứ 11 ngưỡng
còn 153 ⇒ cổng tự cho qua). Giờ duyệt lịch sử theo thời gian: WINDOW phiên đầu (≥ sàn) làm hạt giống, mỗi phiên
sau chỉ được NHẬN vào lịch sử nếu chính nó QUA ngưỡng tính trên lịch sử đã nhận trước nó. Hệ quả cố ý: universe co
THẬT >10% một lần sẽ bị chặn tới khi NGƯỜI xác nhận (không tự hợp thức hoá) — LOOKBACK 150 ngày (~100 phiên) để
hạt giống còn sạch kể cả chuỗi ghi thiếu dài ~2-3 tháng.

LỐI THOÁT CỦA NGƯỜI (arch-review vòng cuối #4, 25/11): universe co THẬT >10% một lần ⇒ neo trên chặn ~cả
LOOKBACK. Người đã đối chiếu (team dữ liệu) ghi `config/prune_depth_reseed.json` {"reseed_from": "<phiên đầu tiên
của universe mới>", "source": "<bằng chứng>"} (cùng khuôn config/trading_calendar_confirmed.json) ⇒ với ngày xét
≥ reseed_from, lịch sử TRƯỚC reseed_from bị bỏ; trong lúc chưa đủ WINDOW phiên mới, ngưỡng = max(sàn, ⌈RATIO ×
trung vị các phiên mới đã nhận⌉) (chưa có phiên nào ⇒ chỉ sàn). Thiếu source / ngày sai / JSON hỏng ⇒ BỎ QUA
(vẫn chặn — fail-closed). Sàn 150 KHÔNG bao giờ bị reseed nới.

Env (arch-review vòng cuối #1): cron / `env -i` không source wc_env.sh ⇒ bq thiếu CLOUDSDK_CONFIG ⇒ "invalid_scope:
Bad Request". ensure_wc_env() nạp CLOUDSDK_CONFIG/DNA_PYEXE + nối PATH từ wc_env.sh khi CLOUDSDK_CONFIG chưa có;
vẫn thiếu ⇒ UNMEASURABLE nói rõ lý do env (không gọi bq).

Fail-closed: không đủ WINDOW phiên trước / BQ lỗi / output lạ ⇒ rc=2 (KHÔNG ĐO ĐƯỢC) — caller chặn.

CLI:
  prune_depth_gate.py --latest            # ngày = MAX(time) của bảng (bq_freshness_check.sh)
  prune_depth_gate.py --date YYYY-MM-DD   # ngày cụ thể (daily_refresh step [0]; chưa ingest ⇒ n=0)
  prune_depth_gate.py --counts-json '{"date":"…","n":197,"prior":[…]}'   # selfcheck, không gọi BQ
In đúng 1 dòng `PRUNE_DEPTH <PASS|FAIL|UNMEASURABLE> …`. rc: 0 PASS · 1 FAIL · 2 UNMEASURABLE.
"""
import argparse
import csv
import io
import json
import math
import os
import re
import statistics
import subprocess
import sys

FLOOR = 150
RATIO = 0.90
WINDOW = 20
LOOKBACK_DAYS = 150  # ~100 phiên: hạt giống 20 + đủ dài để chuỗi ghi thiếu không chiếm hạt giống — partition-pruned, rẻ
MIKE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WC_ENV = os.environ.get("PDG_WC_ENV") or os.path.join(os.path.dirname(MIKE_ROOT), "wc_env.sh")
RESEED_FILE = os.environ.get("PDG_RESEED_FILE") or os.path.join(MIKE_ROOT, "config", "prune_depth_reseed.json")
RUNBOOK = ("RUNBOOK: universe co THẬT (đã đối chiếu team dữ liệu) ⇒ ghi config/prune_depth_reseed.json "
           "{reseed_from: <phiên đầu của universe mới>, source: <bằng chứng>} rồi chạy lại; ghi thiếu/moi ruột ⇒ "
           "KHÔNG reseed, KHÔNG nới ngưỡng")
PROJECT = os.environ.get("BQ_PROJECT", "lithe-record-440915-m9")
TABLE = f"`{PROJECT}.tav2_bq.ticker_prune`"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def ensure_wc_env(env=None, wc_env=None):
    """CLOUDSDK_CONFIG chưa có ⇒ nạp từ wc_env.sh (CLOUDSDK_CONFIG, DNA_PYEXE; PATH nối thêm). Không ghi đè biến
    đã đặt (TZ/WORKDIR_8L KHÔNG nhập). → None nếu env dùng được, ngược lại chuỗi lý do (caller fail-closed)."""
    env = os.environ if env is None else env
    if env.get("CLOUDSDK_CONFIG"):
        return None
    path = wc_env or WC_ENV
    if not os.path.isfile(path):
        return f"thiếu CLOUDSDK_CONFIG và không thấy {path} để nạp (cron phải source wc_env.sh)"
    try:
        r = subprocess.run(["bash", "-c", '. "$1" >/dev/null 2>&1; env -0', "_", path], capture_output=True,
                           timeout=30, env=dict(env))
        got = dict(x.split("=", 1) for x in r.stdout.decode("utf-8", "replace").split("\0") if "=" in x)
    except Exception as exc:  # noqa: BLE001
        return f"thiếu CLOUDSDK_CONFIG, nạp {path} lỗi: {type(exc).__name__}: {exc}"
    for k in ("CLOUDSDK_CONFIG", "DNA_PYEXE"):
        if got.get(k) and not env.get(k):
            env[k] = got[k]
    cur = [x for x in env.get("PATH", "").split(":") if x]
    env["PATH"] = ":".join(cur + [x for x in got.get("PATH", "").split(":") if x and x not in cur])
    return None if env.get("CLOUDSDK_CONFIG") else f"thiếu CLOUDSDK_CONFIG sau khi nạp {path}"


def load_reseed(path=None):
    """→ (reseed_from: date|None, note). Thiếu file/null ⇒ (None, ""). Có mà thiếu source/ngày sai/hỏng ⇒ (None, lý do)."""
    path = path or RESEED_FILE
    try:
        with open(path, encoding="utf-8") as f:
            j = json.load(f)
    except FileNotFoundError:
        return None, ""
    except (OSError, ValueError) as exc:
        return None, f"reseed_bỏ_qua=file hỏng ({type(exc).__name__})"
    if not isinstance(j, dict) or not j.get("reseed_from"):
        return None, ""
    src = str(j.get("source") or "").strip()
    if not src:
        return None, "reseed_bỏ_qua=thiếu source (không nhận reseed không có bằng chứng)"
    if not DATE_RE.match(str(j["reseed_from"])):
        return None, f"reseed_bỏ_qua=reseed_from sai định dạng {j['reseed_from']!r}"
    return str(j["reseed_from"]), f"source={src[:80]}"


def threshold(hist, floor=FLOOR, ratio=RATIO, window=WINDOW):
    med = statistics.median(hist[-window:])
    return med, max(floor, math.ceil(ratio * med))


def accepted_history(prior, floor=FLOOR, ratio=RATIO, window=WINDOW, gate_seed=False):
    """prior (cũ→mới) → (đã nhận, số phiên bị loại). Hạt giống = WINDOW phiên đầu có n ≥ sàn; sau đó chỉ nhận
    phiên QUA ngưỡng tính trên lịch sử ĐÃ NHẬN trước nó (phiên FAIL không đầu độc trung vị).
    gate_seed=True (pha reseed): phiên đầu sau reseed do người xác nhận ⇒ nhận theo sàn; các phiên kế tiếp phải
    qua ngưỡng của lịch sử đã nhận ngay cả khi chưa đủ WINDOW (phiên FAIL không lọt vào trung vị)."""
    acc, dropped = [], 0
    for x in (int(v) for v in prior):
        seeding = len(acc) < window and not (gate_seed and acc)
        if x >= (floor if seeding else threshold(acc, floor, ratio, window)[1]):
            acc.append(x)
        else:
            dropped += 1
    return acc, dropped


def decide(n, prior, floor=FLOOR, ratio=RATIO, window=WINDOW, reseeded=False):
    """→ (verdict, info). prior = list số mã của các phiên TRƯỚC ngày xét (cũ→mới). reseeded=True: prior đã cắt
    từ reseed_from (người xác nhận) ⇒ chưa đủ WINDOW vẫn đo được: trung vị phiên mới đã nhận, rỗng ⇒ chỉ sàn."""
    acc, dropped = accepted_history(prior, floor, ratio, window, gate_seed=reseeded)
    if reseeded and len(acc) < window:
        med, thr = (threshold(acc, floor, ratio, window) if acc else (None, floor))
        info = {"n": n, "median": med, "threshold": thr, "floor": floor, "ratio": ratio, "window": len(acc),
                "dropped": dropped, "reseeded": True}
        return ("PASS" if n >= thr else "FAIL"), info
    if len(acc) < window:
        return "UNMEASURABLE", {"n": n, "reason": f"chỉ có {len(acc)}/{window} phiên trước hợp lệ (≥ sàn {floor}) — "
                                                  "không tính được trung vị"}
    med, thr = threshold(acc, floor, ratio, window)
    info = {"n": n, "median": med, "threshold": thr, "floor": floor, "ratio": ratio, "window": window,
            "dropped": dropped}
    return ("PASS" if n >= thr else "FAIL"), info


def fmt(verdict, date, info):
    if verdict == "UNMEASURABLE":
        return f"PRUNE_DEPTH UNMEASURABLE date={date} n={info.get('n')} reason={info['reason']}"
    med = info["median"]
    med_s = "—" if med is None else (str(int(med)) if float(med).is_integer() else f"{med:.1f}")
    drop = f" loại_khỏi_trung_vị={info['dropped']} phiên FAIL trước đó" if info.get("dropped") else ""
    rs = f" {info['reseed']}" if info.get("reseed") else ""
    rb = f" | {RUNBOOK}" if verdict == "FAIL" else ""
    return (f"PRUNE_DEPTH {verdict} date={date} n={info['n']} threshold={info['threshold']} "
            f"median{info['window']}={med_s} (=max(sàn {info['floor']}, ⌈{info['ratio']:.2f}×trung vị phiên đã qua cổng⌉))"
            + drop + rs + rb)


def query_counts(date_arg):
    """→ (date, n, prior_pairs[(date, n)]). date_arg=None ⇒ MAX(time)."""
    env_err = ensure_wc_env()
    if env_err:
        raise RuntimeError(f"env: {env_err}")
    target = f"DATE('{date_arg}')" if date_arg else f"(SELECT MAX(x.time) FROM {TABLE} AS x)"
    sql = (f"WITH tg AS (SELECT {target} AS d) "
           f"SELECT t.time AS dt, COUNT(DISTINCT t.ticker) AS n FROM {TABLE} AS t, tg "
           f"WHERE t.time BETWEEN DATE_SUB(tg.d, INTERVAL {LOOKBACK_DAYS} DAY) AND tg.d "
           f"GROUP BY dt ORDER BY dt")
    r = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
                        "--format=csv", "--quiet", "--max_rows=1000", sql],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError(f"bq rc={r.returncode}: {' '.join((r.stderr or r.stdout).split())[:200]}")
    rows = list(csv.DictReader(io.StringIO(r.stdout)))
    try:
        pairs = [(row["dt"], int(row["n"])) for row in rows]
    except (KeyError, ValueError, TypeError) as exc:
        raise RuntimeError(f"bq trả output lạ ({type(exc).__name__}): {' '.join(r.stdout.split())[:200]}")
    if not pairs:
        raise RuntimeError("bq không trả phiên nào trong cửa sổ — bảng rỗng/ngày sai")
    date = date_arg or pairs[-1][0]
    n = next((c for d, c in pairs if d == date), 0)
    prior = [(d, c) for d, c in pairs if d < date]
    return date, n, prior


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--latest", action="store_true")
    g.add_argument("--date")
    g.add_argument("--counts-json")
    a = ap.parse_args(argv)
    try:
        if a.counts_json:
            j = json.loads(a.counts_json)
            date, n = j["date"], int(j["n"])
            prior = [tuple(x) if isinstance(x, (list, tuple)) else (None, x) for x in j["prior"]]
        else:
            if a.date and not DATE_RE.match(a.date):
                raise RuntimeError(f"--date sai định dạng: {a.date!r}")
            date, n, prior = query_counts(a.date)
    except Exception as exc:  # noqa: BLE001 — mọi lỗi đo ⇒ fail-closed, nói rõ nguyên nhân
        print(f"PRUNE_DEPTH UNMEASURABLE date={a.date or 'latest'} reason={type(exc).__name__}: {exc}")
        return 2
    rfrom, rnote = load_reseed()
    active = bool(rfrom) and str(date) >= rfrom and all(d is not None for d, _ in prior)
    counts = [int(c) for d, c in prior if not active or str(d) >= rfrom]
    verdict, info = decide(n, counts, reseeded=active)
    if active:
        info["reseed"] = f"RESEED_FROM={rfrom} ({rnote}; lịch sử trước mốc bị bỏ theo xác nhận của người)"
    elif rnote or rfrom:
        info["reseed"] = rnote or f"reseed_from={rfrom} chưa hiệu lực cho ngày {date}"
    print(fmt(verdict, date, info))
    return {"PASS": 0, "FAIL": 1}.get(verdict, 2)


if __name__ == "__main__":
    sys.exit(main())
