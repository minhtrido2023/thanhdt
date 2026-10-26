#!/usr/bin/env python3
"""Giám sát độ tươi THEO MÃ cho `tav2_bq.commodity_prices` (bq_admin nạp 23:00 ICT).

Không có cadence chung (TE có mã ngày, mã tuần; WB tháng; GDT ~2 tuần) ⇒ mỗi khoá
(metric_key, source, cadence) tự học nhịp của chính nó từ lịch sử:

- gaps = khoảng cách NGÀY LỊCH giữa 2 quan sát liên tiếp, trong 365 ngày tính ngược từ
  quan sát cuối (cuối tuần/lễ tự nằm trong phân phối gap của mã — không dùng lịch VN).
- age = ref_date − last_obs. STALE khi age > max(K×median_gap, p90_gap + PAD).
- Lễ theo mùa (Tết, Quốc khánh TQ…) không có trong p90: nếu ĐÚNG mã đó năm trước có một
  gap phủ ref−364 ± SEASON_WINDOW ngày, ngưỡng nâng lên bằng gap đó (không quá gap đó).
- FROZEN_VALUE: số quan sát cuối liên tiếp CÙNG giá ≥ max(FROZEN_MIN_RUN, run dài nhất đã
  hoàn tất trong cửa sổ học + 1) — bắt kiểu TE mang giá cũ sang nhiều ngày.
- LOW_SAMPLE: < MIN_GAPS gap trong cửa sổ học ⇒ không báo động.

ref_date mặc định = hôm nay ICT; chạy sau lượt nạp 23:00 (đề xuất 07:30 ICT). Ghi
data/commodity_freshness_state.json (atomic) và CHỈ in báo cáo khi trạng thái đổi so với lần
trước. Không gửi Telegram/Discord. `--backtest START END` replay từng ngày trên lịch sử.
"""
import argparse
import bisect
import io
import json
import os
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc_paths  # noqa: E402

WC_ROOT = wc_paths.find_wc_root(__file__)
_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
STATE_PATH = os.path.join(WC_ROOT, "data", "commodity_freshness_state.json")
WC_ENV = os.path.join(WC_ROOT, "wc_env.sh")
PROJECT = "lithe-record-440915-m9"

# Ngưỡng chốt sau backtest 12 tháng (2025-10-27→2026-10-26) — xem
# kb/projects/commodity-freshness-monitor-20261026.md trước khi đổi.
DEFAULTS = dict(learn_days=365, min_gaps=8, k_median=3.0, p90_pad=2,
                season_window=25, frozen_min_run=3, frozen_mult=2.0)
# Chỉ dùng cho backtest: ngày một quan sát thực sự có trong bảng. WB CMO ra số tháng M vào
# đầu tháng M+1 (obs_date = mùng 1 tháng M) ⇒ ~35 ngày. Các nguồn khác: có ngay ngày quan sát.
AVAIL_LAG_DAYS = {"worldbank_cmo": 35}
ALERT = ("STALE", "FROZEN_VALUE")


def today_ict():
    return datetime.now(_ICT).date()


def series_key(metric_key, source, cadence):
    return f"{metric_key}|{source}|{cadence}"


def load_history_bq(since):
    """1 query gom lịch sử. Lỗi ⇒ in nguyên văn stdout+stderr của bq (bq đặt lỗi SQL ở stdout)."""
    sql = ("SELECT c.metric_key, c.source, c.cadence, c.observation_date, c.value "
           "FROM `lithe-record-440915-m9.tav2_bq.commodity_prices` AS c "
           f"WHERE c.observation_date >= DATE '{since.isoformat()}'")
    cmd = (f"source {WC_ENV} >/dev/null 2>&1; bq query --use_legacy_sql=false "
           f"--project_id={PROJECT} --format=csv --max_rows=100000000 \"$Q\"")
    r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True,
                       env={**os.environ, "Q": sql})
    if r.returncode != 0 or not r.stdout.startswith("metric_key"):
        raise RuntimeError(f"bq query lỗi rc={r.returncode}\nstdout: {r.stdout[:2000]}\n"
                           f"stderr: {r.stderr[:2000]}")
    return pd.read_csv(io.StringIO(r.stdout))


def prepare(df, backtest_lag=False):
    """→ {key: (obs_dates: list[date], values: np.ndarray, avail: list[date])}, đã sort.
    backtest_lag=True: avail = ngày dòng thực sự có trong bảng (AVAIL_LAG_DAYS). Live: dòng
    nào đã ở trong bảng là đã biết ⇒ lag 0."""
    df = df.copy()
    df["observation_date"] = pd.to_datetime(df["observation_date"]).dt.date
    out = {}
    for (m, s, c), g in df.groupby(["metric_key", "source", "cadence"], sort=True):
        g = g.sort_values("observation_date")
        dates = g["observation_date"].tolist()
        lag = timedelta(days=AVAIL_LAG_DAYS.get(s, 0) if backtest_lag else 0)
        out[series_key(m, s, c)] = (dates, g["value"].to_numpy(float), [d + lag for d in dates])
    return out


def _runs(values):
    """Độ dài các run giá bằng nhau liên tiếp (theo thứ tự)."""
    runs, n = [], 1
    for a, b in zip(values[:-1], values[1:]):
        if abs(a - b) <= 1e-9 * abs(b):
            n += 1
        else:
            runs.append(n)
            n = 1
    runs.append(n)
    return runs


def score_series(dates, values, ref, p):
    """dates/values = các quan sát đã BIẾT tại ref (sorted). Trả dict trạng thái."""
    last = dates[-1]
    age = (ref - last).days
    lo = last - timedelta(days=p["learn_days"])
    i0 = bisect.bisect_left(dates, lo)
    win_d, win_v = dates[i0:], values[i0:].tolist()
    gaps = np.array([(b - a).days for a, b in zip(win_d[:-1], win_d[1:])], dtype=float)
    res = {"last_obs": last.isoformat(), "last_value": float(values[-1]), "age": age,
           "n_gaps": int(len(gaps)), "median_gap": None, "p90_gap": None,
           "threshold": None, "seasonal_allow": None, "tail_run": None,
           "frozen_threshold": None, "status": "LOW_SAMPLE"}
    if len(gaps) < p["min_gaps"]:
        return res
    med, p90 = float(np.median(gaps)), float(np.percentile(gaps, 90))
    thr = max(p["k_median"] * med, p90 + p["p90_pad"])
    # Lễ theo mùa: gap của chính mã này năm trước, phủ ref−364 ± window.
    anchor = ref - timedelta(days=364)
    w = timedelta(days=p["season_window"])
    allow = 0
    j = max(bisect.bisect_left(dates, anchor - w) - 1, 0)
    for a, b in zip(dates[j:-1], dates[j + 1:]):
        if a >= anchor + w:
            break
        if b > anchor - w:
            allow = max(allow, (b - a).days)
    eff = max(thr, allow + p["p90_pad"]) if allow > thr else thr
    runs = _runs(win_v)
    tail = runs[-1]
    done = runs[:-1]
    fthr = max(p["frozen_min_run"], int(p["frozen_mult"] * (max(done) if done else 1)) + 1)
    res.update(median_gap=med, p90_gap=p90, threshold=round(thr, 2),
               seasonal_allow=allow if allow > thr else None, tail_run=int(tail),
               frozen_threshold=int(fthr))
    if age > eff:
        res["status"] = "STALE"
    elif tail >= fthr:
        res["status"] = "FROZEN_VALUE"
    else:
        res["status"] = "OK"
    return res


def score_all(series, ref, p):
    out = {}
    cutoff = ref - timedelta(days=1)  # chạy sáng ref ⇒ thấy dữ liệu nạp tới 23:00 hôm trước
    for k, (dates, vals, avail) in series.items():
        n = bisect.bisect_right(avail, cutoff)
        if n == 0:
            continue
        # avail đơn điệu theo dates (lag hằng số/nguồn) ⇒ prefix là tập đã biết
        out[k] = score_series(dates[:n], vals[:n], ref, p)
    return out


def diff_states(prev, cur):
    """→ list dòng báo cáo khi trạng thái đổi (mã mới cảnh báo / hồi phục / mã mới / mất)."""
    lines = []
    for k in sorted(set(prev) | set(cur)):
        a = prev.get(k, {}).get("status")
        b = cur.get(k, {}).get("status")
        if a == b:
            continue
        c = cur.get(k, {})
        if b in ALERT:
            lines.append(f"🔴 {k}: {a or 'mới'} → {b} (last_obs {c['last_obs']}, age {c['age']}d,"
                         f" ngưỡng {c['threshold']}d, tail_run {c['tail_run']})")
        elif a in ALERT and b is not None:
            lines.append(f"🟢 {k}: {a} → {b} (last_obs {c['last_obs']})")
        elif b is None:
            lines.append(f"⚪ {k}: biến mất khỏi bảng (trước đó {a})")
        elif a is not None:
            lines.append(f"⚪ {k}: {a} → {b}")
    return lines


def write_state_atomic(path, payload):
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".cfm_", suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, path)


def run_live(series, ref, p, state_path, write=True):
    cur = score_all(series, ref, p)
    prev = {}
    if os.path.exists(state_path):
        with open(state_path) as f:
            prev = json.load(f).get("series", {})
    lines = diff_states(prev, cur)
    counts = defaultdict(int)
    for v in cur.values():
        counts[v["status"]] += 1
    payload = {"generated_at": datetime.now(_ICT).isoformat(timespec="seconds"),
               "ref_date": ref.isoformat(), "params": p, "counts": dict(counts),
               "series": cur}
    if write:
        write_state_atomic(state_path, payload)
    return cur, lines, dict(counts)


def backtest(series, start, end, p):
    """Replay từng ngày. → (daily_status {key:{date:status}}, episodes list)."""
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    hist = defaultdict(dict)
    for d in days:
        for k, v in score_all(series, d, p).items():
            hist[k][d] = v
    eps = []
    for k, byday in hist.items():
        dates = series[k][0]
        cur = None
        for d in days:
            v = byday.get(d)
            st = v["status"] if v else None
            if st in ALERT and (cur is None or cur["status"] != st):
                if cur:
                    eps.append(cur)
                cur = {"key": k, "status": st, "start": d, "end": d, "last_obs": v["last_obs"],
                       "age0": v["age"], "threshold": v["threshold"], "resolved": False}
            elif st in ALERT:
                cur["end"] = d
            elif cur:
                cur["resolved"] = True
                eps.append(cur)
                cur = None
        if cur:
            eps.append(cur)
        for e in eps:
            if e["key"] != k or "gap_total" in e:
                continue
            lo = date.fromisoformat(e["last_obs"])
            nxt = next((x for x in dates if x > lo), None)
            e["gap_total"] = (nxt - lo).days if nxt else None
            prior = [x for x in dates if lo - timedelta(days=p["learn_days"]) <= x <= lo]
            e["hist_max_gap"] = max(((b - a).days for a, b in zip(prior[:-1], prior[1:])),
                                    default=None)
    return hist, eps


FALSE_HEAL_DAYS = 7


def classify(e):
    """Hindsight. STALE: báo GIẢ = mã tự có quan sát mới trong ≤7 ngày kể từ lúc báo (trễ ngắn
    tự lành, không cần ai làm gì — vd Tết dài hơn năm trước); còn lại = THẬT. FROZEN: không có
    ca dương tính nào đã biết ⇒ mọi episode đã tự hết đều tính GIẢ; còn treo cuối kỳ = ONGOING."""
    if e["status"] == "STALE":
        if e["gap_total"] is None:
            return "TRUE_ONGOING"
        healed = date.fromisoformat(e["last_obs"]) + timedelta(days=e["gap_total"])
        return "FALSE" if (healed - e["start"]).days <= FALSE_HEAL_DAYS else "TRUE"
    return "FALSE" if e["resolved"] else "ONGOING"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ref-date", type=date.fromisoformat, default=None)
    ap.add_argument("--state-path", default=STATE_PATH)
    ap.add_argument("--hist-csv", help="đọc lịch sử từ CSV thay vì BQ (selfcheck/backtest)")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--verbose", action="store_true", help="in tóm tắt cả khi không đổi")
    ap.add_argument("--backtest", nargs=2, type=date.fromisoformat, metavar=("START", "END"))
    ap.add_argument("--set", action="append", default=[], metavar="PARAM=VAL",
                    help="ghi đè tham số (chỉ dùng thử nghiệm/backtest)")
    a = ap.parse_args()
    p = dict(DEFAULTS)
    for kv in a.set:
        k, v = kv.split("=", 1)
        p[k] = type(DEFAULTS[k])(float(v)) if k in DEFAULTS else v
    ref = a.ref_date or today_ict()
    first = a.backtest[0] if a.backtest else ref
    since = first - timedelta(days=p["learn_days"] + 400)
    raw = pd.read_csv(a.hist_csv) if a.hist_csv else load_history_bq(since)
    if a.backtest:
        end = a.backtest[1]
        raw = raw[pd.to_datetime(raw["observation_date"]).dt.date < end]
        series = prepare(raw, backtest_lag=True)
        _, eps = backtest(series, a.backtest[0], end, p)
        for e in eps:
            e["class"] = classify(e)
        weeks = ((end - a.backtest[0]).days + 1) / 7
        by = defaultdict(lambda: defaultdict(int))
        for e in eps:
            by[e["status"]][e["class"]] += 1
        print(json.dumps({"params": p, "weeks": round(weeks, 1),
                          "episodes": {s: dict(c) for s, c in by.items()},
                          "false_per_week": round(sum(1 for e in eps if e["class"] == "FALSE")
                                                  / weeks, 2)}, ensure_ascii=False))
        for e in sorted(eps, key=lambda e: (e["start"], e["key"])):
            print(f"{e['start']}..{e['end']} {e['status']:12s} {e['class']:12s} {e['key']} "
                  f"last={e['last_obs']} age0={e['age0']} thr={e['threshold']} "
                  f"gap_total={e['gap_total']} hist_max_gap={e['hist_max_gap']}")
        return 0
    series = prepare(raw)
    cur, lines, counts = run_live(series, ref, p, a.state_path, write=not a.no_write)
    if lines or a.verbose:
        print(f"commodity_freshness {ref} — {counts}")
        for ln in lines:
            print(ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
