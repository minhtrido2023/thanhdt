#!/usr/bin/env python3
"""Tách SUE của LAG (hàng hoá vs bất ngờ thật) — sổ nhật ký FORWARD (PAPER-ONLY, không lệnh/plan/trading_rules).

Thiết kế đóng băng ở `agents/Taylor/research/commodity_cycle_te_20261026/PREREG-4.md`. Mỗi lần chạy:
  1. Sự kiện BCTC quý ≥ 2026Q3 của 25 mã tier A (commodity_map_te.csv) ⇒ tính c_yoy/c_ma, sue1/sue2, SUE_hat (OLS
     theo họ, CHỈ sự kiện cùng họ có Release_Date < ngày công bố này), sue_res. Quý 2026Q3 = PRE_FREEZE_BACKFILL
     (counts=False). Sự kiện LAG qualify của mã ngoài danh sách ⇒ group=NO_COMMODITY (loại khỏi H1, ghi lý do).
     APPEND-ONLY `data/commodity_sue_decomp_forward_events.csv`, khoá (family, quarter, ticker): giá trị lúc thấy lần
     đầu được giữ, không tính lại.
  2. Sự kiện đủ 60 phiên ⇒ post60 (vượt trội so với bình quân đều universe_pit) APPEND-ONLY
     `data/commodity_sue_decomp_forward_outcomes.csv`.
Tracker KHÔNG in IC/TB/CI/p hay bất cứ thống kê nào ghép SUE với post60 (PREREG-4 §5); verdict =
`commodity_sue_decomp_forward_review.py` (có cổng ngày).

Chạy: $DNA_PYEXE mike/bin/commodity_sue_decomp_forward_tracker.py [--dry-run] [--data-dir DIR] [--te-parquet P]
Selfcheck: mike/bin/commodity_sue_decomp_forward_tracker_selfcheck.py [--mutants]
"""
import argparse
import datetime as dt
import hashlib
import io
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
LOCK_DIR = os.path.join(HERE, "..", "agents/Taylor/research/commodity_cycle_te_20261026")
PREREG_MD5 = "6c5642c13ea830f464a0fd07b1be2d4c"
MAP_MD5 = "9414e8640baca06a8837813e4280a31b"
LOCKED = {"PREREG-4.md": PREREG_MD5, "commodity_map_te.csv": MAP_MD5}
BANNED = {"HSG", "NKG"}                      # trong danh sách tier A, BANNED giao dịch nhưng vẫn đo (PREREG-4 §2)
BACKFILL_Q, FIRST_Q, LAST_Q = pd.Period("2026Q3", "Q"), pd.Period("2026Q4", "Q"), pd.Period("2031Q1", "Q")
H, LATE_SESSIONS, MIN_OBS_Q = 60, 10, 40
FIT_MIN_N, FIT_MIN_Q = 8, 6
SIG_LAG_DAYS = 2                             # TE cập nhật 23:00 ICT ⇒ giá TB quý biết từ qend+2 ngày
EV_COLS = ["group", "family", "quarter", "ticker", "release_date", "first_seen", "status", "counts", "reason",
           "banned", "lag_qualify", "c_yoy", "c_ma", "sue1", "sue1_a", "sue1_b", "sue1_nfit", "sue1_hat", "sue1_res",
           "sue2", "sue2_a", "sue2_b", "sue2_nfit", "sue2_hat", "sue2_res", "prereg_md5", "map_md5"]
OUT_COLS = ["group", "family", "quarter", "ticker", "t0", "t60", "r_stock", "r_bench", "post60", "note",
            "computed_at"]
KEY = ["family", "quarter", "ticker"]


# ---------------- logic thuần (selfcheck gọi trực tiếp) ----------------
def quarter_avgs(te):
    """te: DataFrame index=ngày, cột=metric_key → TB quý lịch (index = Period Q), NaN khi < MIN_OBS_Q quan sát."""
    g = te.groupby(te.index.to_period("Q"))
    return g.mean().where(g.count() >= MIN_OBS_Q)


def comm_signals(qa, key, q, sign=1):
    """→ (c_yoy, c_ma) của quý q; NaN nếu thiếu."""
    if key not in qa.columns:
        return np.nan, np.nan
    s = qa[key]
    get = lambda p: s.get(p, np.nan)  # noqa: E731
    cur = get(q)
    yoy = np.log(cur / get(q - 4))
    ma = np.log(cur / np.nanmean([get(q - k) for k in range(1, 5)])) if all(
        pd.notna(get(q - k)) for k in range(1, 5)) else np.nan
    return float(yoy * sign), float(ma * sign)


def sue1(r):
    """S1 (chính): (NP_P0 − NP_P4)/Revenue_P4, cắt ±0,5."""
    if not (pd.notna(r.Revenue_P4) and r.Revenue_P4 > 0 and pd.notna(r.NP_P0) and pd.notna(r.NP_P4)):
        return np.nan
    return float(np.clip((r.NP_P0 - r.NP_P4) / r.Revenue_P4, -0.5, 0.5))


def sue2(r):
    """S2 (phụ): surprise_B_MA đúng công thức lag_live_schedule.py (FLOOR 1e9, cắt ±5)."""
    v = [r.NP_P1, r.NP_P2, r.NP_P3, r.NP_P4]
    if pd.isna(r.NP_P0) or all(pd.isna(x) for x in v):
        return np.nan
    e = np.nanmean(v)
    return float(np.clip((r.NP_P0 - e) / max(abs(e), 1e9), -5, 5))


def build_hist(fin, cmap, qa):
    """Mọi sự kiện của mã trong danh sách (không lọc universe) với sue1/sue2/c_yoy/c_ma — nguồn fit."""
    m = cmap.set_index("ticker")
    f = fin[fin.ticker.isin(m.index) & fin.Release_Date.notna()].copy()
    rows = []
    for r in f.itertuples():
        mm = m.loc[r.ticker]
        q = pd.Period(r.quarter, "Q")
        cy, cm = comm_signals(qa, mm.te_metric_key, q, int(mm.sign))
        rows.append(dict(family=mm.family, ticker=r.ticker, quarter=r.quarter, release=pd.Timestamp(r.Release_Date),
                         c_yoy=cy, c_ma=cm, sue1=sue1(r), sue2=sue2(r)))
    return pd.DataFrame(rows, columns=["family", "ticker", "quarter", "release", "c_yoy", "c_ma", "sue1", "sue2"])


def fit_hat(hist, family, release, x, y, xval):
    """OLS y=a+b·x trên sự kiện cùng họ có release < `release` (chặt). → (a, b, n, hat) hoặc None nếu thiếu lịch sử."""
    past = hist[(hist.family == family) & (hist.release < pd.Timestamp(release))].dropna(subset=[x, y])
    if len(past) < FIT_MIN_N or past.quarter.nunique() < FIT_MIN_Q or pd.isna(xval):
        return None
    b, a = np.polyfit(past[x].values, past[y].values, 1)
    return float(a), float(b), len(past), float(a + b * xval)


def sessions_between(days, d0, d1):
    """Số phiên trong (d0, d1]; phần sau phiên cuối có trong lịch tính theo ngày làm việc (bảo thủ: nhiều hơn)."""
    d0, d1 = pd.Timestamp(d0), pd.Timestamp(d1)
    n = int(((days > d0) & (days <= d1)).sum())
    last = days[-1] if len(days) else d0
    if d1 > last:
        n += len(pd.bdate_range(max(last, d0) + pd.Timedelta(days=1), d1))
    return n


def classify(quarter, release, first_seen, days):
    """→ (status, counts, reasons[list]) hoặc None nếu ngoài cửa sổ ghi."""
    q = pd.Period(quarter, "Q")
    if q < BACKFILL_Q or q > LAST_Q:
        return None
    if q < FIRST_Q:
        return "PRE_FREEZE_BACKFILL", False, ["PRE_FREEZE"]
    late = sessions_between(days, release, first_seen) > LATE_SESSIONS
    return "FORWARD", (not late), (["LATE"] if late else [])


def member_at(umembers, ticker, d):
    """Thành viên universe_pit ở phiên cuối ≤ d."""
    idx = umembers.index[umembers.index <= pd.Timestamp(d)]
    return bool(len(idx)) and ticker in umembers[idx[-1]]


class Market:
    def __init__(self, close, umembers):
        self.close, self.umembers = close, umembers
        self.days = close.index
        r = close.pct_change(fill_method=None)
        e = umembers.explode().dropna().rename("ticker").rename_axis("time").reset_index()
        mem = (e.assign(v=1).pivot_table(index="time", columns="ticker", values="v", aggfunc="first")
               .reindex(index=close.index, columns=close.columns).notna())     # = common.bench: thiếu ngày ⇒ False
        self.bc = (1 + r.where(mem.shift(1, fill_value=False)).mean(axis=1).fillna(0)).cumprod()

    def post(self, ticker, release, h=H, asof=None):
        """→ dict(t0, t60, r_stock, r_bench, post60) | 'pending' | None (không có giá). t60 phải ≤ asof (ngày chạy)."""
        i = self.days.searchsorted(pd.Timestamp(release) + pd.Timedelta(days=1), side="left")
        if i + h > len(self.days) - 1 or (asof is not None and self.days[i + h] > pd.Timestamp(asof)):
            return "pending"
        t0, t1 = self.days[i], self.days[i + h]
        if ticker not in self.close.columns:
            return None
        a, b = self.close.at[t0, ticker], self.close.at[t1, ticker]
        if not (pd.notna(a) and pd.notna(b) and a > 0 and b > 0):
            return None
        rs, rb = b / a - 1, self.bc[t1] / self.bc[t0] - 1
        return dict(t0=t0.strftime("%Y-%m-%d"), t60=t1.strftime("%Y-%m-%d"), r_stock=rs, r_bench=rb, post60=rs - rb)


def new_event_rows(fin, cmap, qa, lagq, mk, ledger_keys, first_seen):
    hist = build_hist(fin, cmap, qa)
    m = cmap.set_index("ticker")
    qual = set(zip(lagq.ticker, lagq.quarter)) if lagq is not None else set()
    rows = []
    for r in fin[fin.Release_Date.notna()].itertuples():
        tier = r.ticker in m.index
        fam = m.loc[r.ticker].family if tier else "NONE"
        if (fam, r.quarter, r.ticker) in ledger_keys:
            continue
        if not tier and (r.ticker, r.quarter) not in qual:
            continue
        c = classify(r.quarter, r.Release_Date, first_seen, mk.days)
        if c is None:
            continue
        st, counts, reasons = c
        base = dict(family=fam, quarter=r.quarter, ticker=r.ticker,
                    release_date=pd.Timestamp(r.Release_Date).strftime("%Y-%m-%d"), first_seen=first_seen,
                    status=st, banned=int(r.ticker in BANNED), lag_qualify=int((r.ticker, r.quarter) in qual),
                    sue1=sue1(r), sue2=sue2(r), prereg_md5=PREREG_MD5, map_md5=MAP_MD5)
        if not tier:
            rows.append({**base, "group": "NO_COMMODITY", "counts": False, "reason": "EXCLUDED_NO_COMMODITY"})
            continue
        q = pd.Period(r.quarter, "Q")
        cy, cm = comm_signals(qa, m.loc[r.ticker].te_metric_key, q, int(m.loc[r.ticker].sign))
        if pd.Timestamp(r.Release_Date) <= q.end_time.normalize() + pd.Timedelta(days=SIG_LAG_DAYS):
            reasons.append("SIGNAL_NOT_BEFORE_RELEASE")
        if not member_at(mk.umembers, r.ticker, r.Release_Date):
            reasons.append("NOT_IN_UNIVERSE")
        if pd.isna(cy) and pd.isna(cm):
            reasons.append("NO_COMMODITY_DATA")
        row = {**base, "group": "TIER_A", "c_yoy": cy, "c_ma": cm}
        for s, x, xv in [("sue1", "c_yoy", cy), ("sue2", "c_ma", cm)]:
            f = fit_hat(hist, fam, r.Release_Date, x, s, xv)
            if f is None:
                reasons.append(f"NO_FIT_HISTORY_{s.upper()}")
                continue
            a, b, n, hat = f
            row.update({f"{s}_a": a, f"{s}_b": b, f"{s}_nfit": n, f"{s}_hat": hat, f"{s}_res": row[s] - hat})
        hard = {"SIGNAL_NOT_BEFORE_RELEASE", "NOT_IN_UNIVERSE", "NO_COMMODITY_DATA"}
        row["counts"] = bool(counts and not hard.intersection(reasons) and "NO_FIT_HISTORY_SUE1" not in reasons)
        row["reason"] = ";".join(reasons)
        rows.append(row)
    return pd.DataFrame(rows, columns=EV_COLS)


def new_outcome_rows(events, done_keys, mk, now_s, asof=None):
    rows, n_pending = [], 0
    for e in events.itertuples():
        if (e.family, e.quarter, e.ticker) in done_keys:
            continue
        p = mk.post(e.ticker, e.release_date, asof=asof)
        if p == "pending":
            n_pending += 1
            continue
        base = dict(group=e.group, family=e.family, quarter=e.quarter, ticker=e.ticker, computed_at=now_s)
        rows.append({**base, **p, "note": ""} if p else {**base, "note": "NO_PRICE"})
    return pd.DataFrame(rows, columns=OUT_COLS), n_pending


def check_locks(lock_dir=None, locked=None):
    bad = []
    for n, md5 in (locked or LOCKED).items():
        p = os.path.join(lock_dir or LOCK_DIR, n)
        got = hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"
        if got != md5:
            bad.append(f"{n}: {got} != {md5}")
    return bad


def _append(path, new, cols):
    """APPEND-ONLY + nguyên tử: dòng cũ giữ nguyên byte-giá-trị, chỉ nối thêm dòng có khoá mới."""
    old = pd.read_csv(path, dtype=str) if os.path.exists(path) else pd.DataFrame(columns=cols)
    if len(new):
        keys = set(zip(*(old[k] for k in KEY)))
        new = new[[k not in keys for k in zip(*(new[c].astype(str) for c in KEY))]]
    out = pd.concat([old, new.astype(object)], ignore_index=True)[cols] if len(new) else old
    tmp = path + ".tmp"
    out.to_csv(tmp, index=False)
    os.replace(tmp, path)


# ---------------- nạp dữ liệu thật ----------------
def load_cmap():
    m = pd.read_csv(os.path.join(LOCK_DIR, "commodity_map_te.csv"))
    return m[(m.tier == "A") & (m.ticker != "-")][["ticker", "family", "te_metric_key", "sign"]]


def load_te(keys, parquet=None):
    if parquet:
        d = pd.read_parquet(parquet)
    else:
        sql = ("SELECT c.metric_key, c.observation_date, c.value FROM `lithe-record-440915-m9.tav2_bq.commodity_prices` AS c "
               "WHERE c.source='trading_economics' AND c.cadence='daily' AND c.observation_date >= DATE '2016-10-01' "
               "AND c.metric_key IN (" + ",".join(f"'{k}'" for k in sorted(keys)) + ")")
        cmd = (f"source {WC_ROOT}/wc_env.sh >/dev/null 2>&1; bq query --use_legacy_sql=false "
               "--project_id=lithe-record-440915-m9 --format=csv --max_rows=10000000 \"$Q\"")
        r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, env={**os.environ, "Q": sql})
        if r.returncode != 0 or not r.stdout.startswith("metric_key"):
            raise RuntimeError(f"bq query lỗi rc={r.returncode}\nstdout: {r.stdout[:1500]}\nstderr: {r.stderr[:1500]}")
        d = pd.read_csv(io.StringIO(r.stdout))
    d["observation_date"] = pd.to_datetime(d.observation_date)
    d = d[d.metric_key.isin(keys)]
    return d.pivot(index="observation_date", columns="metric_key", values="value").sort_index()


def load_fin():
    f = pd.read_parquet(f"{WC_ROOT}/data/bq_cache/ticker_financial.parquet",
                        columns=["ticker", "quarter", "Release_Date", "NP_P0", "NP_P1", "NP_P2", "NP_P3", "NP_P4",
                                 "Revenue_P4"])
    f["Release_Date"] = pd.to_datetime(f.Release_Date)
    return f[f.quarter >= "2016Q1"]


def load_lagq():
    sys.path.insert(0, WC_ROOT)
    from lag_live_schedule import live_lag_candidates
    L = live_lag_candidates(start="2026-07-01")
    return L[L.qualify][["ticker", "quarter"]]


def load_market():
    import duckdb
    con = duckdb.connect()
    P = con.sql(f"""select time, ticker, Close from read_parquet('{WC_ROOT}/data/bq_cache/ticker/*.parquet')
                   where time >= '2016-01-01' and Close > 0""").df()
    P["time"] = pd.to_datetime(P.time)
    close = P.pivot_table(index="time", columns="ticker", values="Close").sort_index()
    U = con.sql(f"""select time, ticker from read_parquet('{WC_ROOT}/data/bq_cache/universe_pit/*.parquet')
                   where in_universe and time >= '2016-01-01'""").df()
    U["time"] = pd.to_datetime(U.time)
    return Market(close, U.groupby("time").ticker.apply(set))


def main(argv=None, data=None, now=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--data-dir", default=os.path.join(WC_ROOT, "data"))
    ap.add_argument("--te-parquet", default=None, help="đọc TE từ parquet thay vì BQ (selfcheck/offline)")
    a = ap.parse_args(argv)
    bad = check_locks()
    if bad:
        print("LOCK MISMATCH — dừng, không ghi sổ:\n  " + "\n  ".join(bad))
        return 2
    now = now or dt.datetime.now(ICT)
    fs = now.strftime("%Y-%m-%d")
    if data is None:
        cmap = load_cmap()
        data = dict(cmap=cmap, te=load_te(set(cmap.te_metric_key), a.te_parquet), fin=load_fin(), lagq=load_lagq(),
                    mk=load_market())
    qa = quarter_avgs(data["te"])
    evp = os.path.join(a.data_dir, "commodity_sue_decomp_forward_events.csv")
    outp = os.path.join(a.data_dir, "commodity_sue_decomp_forward_outcomes.csv")
    ev_old = pd.read_csv(evp, dtype=str) if os.path.exists(evp) else pd.DataFrame(columns=EV_COLS)
    ev_new = new_event_rows(data["fin"], data["cmap"], qa, data["lagq"], data["mk"],
                            set(zip(*(ev_old[k] for k in KEY))), fs)
    ev_all = pd.concat([ev_old, ev_new.astype(object)], ignore_index=True)
    out_old = pd.read_csv(outp, dtype=str) if os.path.exists(outp) else pd.DataFrame(columns=OUT_COLS)
    out_new, n_pending = new_outcome_rows(ev_all, set(zip(*(out_old[k] for k in KEY))), data["mk"],
                                          now.strftime("%Y-%m-%d %H:%M %z"), pd.Timestamp(now.date()))
    g = ev_new.groupby(["group", "status"]).size().to_dict() if len(ev_new) else {}
    msg = (f"[{fs} ICT] sự kiện mới {len(ev_new)} {g} · kết quả mới {len(out_new)} · chờ đủ {H} phiên {n_pending} · "
           f"sổ sự kiện {len(ev_all)} dòng")
    print(msg)
    if a.dry_run:
        print("  --dry-run: không ghi")
        return 0
    os.makedirs(a.data_dir, exist_ok=True)
    _append(evp, ev_new, EV_COLS)
    _append(outp, out_new, OUT_COLS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
