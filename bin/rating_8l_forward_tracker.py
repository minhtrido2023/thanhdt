#!/usr/bin/env python3
"""Rating 8L — tracker tích luỹ OOS đi tới (PAPER-ONLY, read-only BQ).

Thiết kế khoá ở `agents/Taylor/research/rating_8l_forward_bt_20261020/PREREG_FORWARD.md` (md5 PREREG_MD5 dưới).
Mỗi lần chạy:
  1. Quét `tav2_bq.fa_ratings_8l` + `ticker_financial` tìm dòng rating có eff_date > 2026-07-31, xếp G0/G1/G2/G3 theo
     rating dòng liền trước cùng mã, gắn cờ loại ca (giữ nguyên luật event study vòng 2) ⇒ APPEND-ONLY vào
     `data/rating_8l_forward_events.csv`. Khoá (ticker, quarter): đã có thì KHÔNG ghi lại (giá trị lần đầu thấy = PIT).
  2. CAR[2,20]/[2,40] vs B3 (EW in_universe loại chính mã) cho sự kiện đủ 42 phiên sau eff ⇒ APPEND-ONLY vào
     `data/rating_8l_forward_car.csv`. CHỈ khi nguồn giá qua cổng độ phủ (fail-closed): live `tav2_bq.ticker`, nếu
     trượt thì pin `tav2_pin.ticker_pin_YYYYMM` mới nhất; cả hai trượt ⇒ KHÔNG tính CAR, in BLOCKED.
Tracker KHÔNG ra verdict (verdict = `event_study_v2_frozen.py` lúc review, PREREG §1/§3).

Chạy: $DNA_PYEXE mike/bin/rating_8l_forward_tracker.py [--dry-run]
Selfcheck: mike/bin/rating_8l_forward_tracker_selfcheck.py
"""
import argparse
import datetime as dt
import hashlib
import os
import sys
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
EVENTS_CSV = os.path.join(WC_ROOT, "data/rating_8l_forward_events.csv")
CAR_CSV = os.path.join(WC_ROOT, "data/rating_8l_forward_car.csv")
HERE = os.path.dirname(os.path.abspath(__file__))
LOCK_DIR = os.path.join(HERE, "..", "agents/Taylor/research/rating_8l_forward_bt_20261020")
PREREG_MD5 = "4ad20803a74b046af74a9b128085019c"
LOCKED = {                                      # file khoá → md5; lệch ⇒ dừng, KHÔNG ghi ledger (NB2)
    "PREREG_FORWARD.md": PREREG_MD5,
    "event_study_v2_frozen.py": "a857d81bfc95be8b7dac507f6cf9dbad",
    "PREREG_FORWARD_ADDENDUM_20261020.md": "aace4e50089c28518550019846cfe1d8",
}
EFF_AFTER = pd.Timestamp("2026-07-31")          # sự kiện phải có eff > mốc này (PREREG §1)
WPRE, WPOST, NEED_AFTER = 60, 40, 42            # CAR cần đủ 42 phiên sau phiên 0
MIN_TICKERS, MIN_UNIV_COVER, MIN_UNIV_N = 1200, 0.98, 300        # cổng độ phủ (PREREG §2; n = mã TOÀN BẢNG, xem price_source)
WIN = {"[2,20]": (2, 20), "[2,40]": (2, 40)}
EV_COLS = ["ticker", "quarter", "eff_date", "route", "rating_prev", "rating_new", "grp",
           "x_null", "x_definite", "x_early7", "excl", "first_seen", "prereg_md5"]
CAR_COLS = ["ticker", "quarter", "eff_date", "grp", "excl", "session0", "in_univ0", "car[2,20]", "car[2,40]",
            "n_obs_win", "px_source", "px_n_tickers", "px_univ_cover", "computed_at", "prereg_md5"]


# ---------------- logic thuần (selfcheck gọi trực tiếp) ----------------
def detect_events(fa, tf, known_keys, first_seen):
    """fa: ticker,time,route,rating (mọi dòng, có cả quý trước) · tf: ticker,quarter,time,Release_Date.
    Trả DataFrame EV_COLS các sự kiện eff > EFF_AFTER chưa có trong known_keys {(ticker, quarter)}."""
    fa = fa.sort_values(["ticker", "time"]).copy()
    fa["rating_prev"] = fa.groupby("ticker").rating.shift()
    ev = fa[fa.rating_prev.notna()].copy()
    ev["grp"] = np.select([ev.rating == ev.rating_prev,
                           (ev.rating_prev >= 4) & (ev.rating <= 3),
                           (ev.rating_prev <= 3) & (ev.rating >= 4)], ["G0", "G1", "G2"], "G3")
    tf = tf.copy()
    tf["qend"] = pd.PeriodIndex(tf.quarter, freq="Q").end_time.normalize()
    tf = tf.sort_values(["ticker", "qend"])
    tf["prev_rd"] = tf.groupby("ticker").Release_Date.shift()
    lag = (tf.Release_Date - tf.qend).dt.days
    tf["x_null"] = tf.Release_Date.isna()
    tf["x_definite"] = (lag < 0) | (tf.Release_Date.notna() & tf.prev_rd.notna() & (tf.Release_Date <= tf.prev_rd))
    tf["x_early7"] = lag.between(0, 7)
    tf["eff"] = tf.Release_Date.fillna(tf.time)
    tf = tf.sort_values("qend").drop_duplicates(["ticker", "eff"], keep="last")
    ev = ev.merge(tf[["ticker", "eff", "quarter", "x_null", "x_definite", "x_early7"]],
                  left_on=["ticker", "time"], right_on=["ticker", "eff"], how="inner")
    ev = ev[ev.time > EFF_AFTER]
    if known_keys:
        ev = ev[~pd.Series(list(zip(ev.ticker, ev.quarter)), index=ev.index).isin(known_keys)]
    ev = ev.drop_duplicates(["ticker", "quarter"], keep="first")
    out = pd.DataFrame({
        "ticker": ev.ticker, "quarter": ev.quarter, "eff_date": ev.time.dt.strftime("%Y-%m-%d"),
        "route": ev.route, "rating_prev": ev.rating_prev.astype(int), "rating_new": ev.rating.astype(int),
        "grp": ev.grp, "x_null": ev.x_null.astype(bool), "x_definite": ev.x_definite.astype(bool),
        "x_early7": ev.x_early7.astype(bool)})
    out["excl"] = out.x_null | out.x_definite | out.x_early7
    out["first_seen"] = first_seen
    out["prereg_md5"] = PREREG_MD5
    return out[EV_COLS].sort_values(["eff_date", "ticker"]).reset_index(drop=True)


def coverage_gate(n_tickers_latest, n_univ_latest, n_univ_covered):
    """(ok, cover, lý do). Fail-closed: thiếu số liệu ⇒ không ok."""
    if not n_univ_latest or n_tickers_latest is None or n_univ_covered is None:
        return False, float("nan"), "thiếu số liệu độ phủ"
    cover = n_univ_covered / n_univ_latest
    if n_univ_latest < MIN_UNIV_N:
        return False, cover, f"mẫu số universe {n_univ_latest} < {MIN_UNIV_N}"
    if n_tickers_latest < MIN_TICKERS:
        return False, cover, f"số mã {n_tickers_latest} < {MIN_TICKERS}"
    if cover < MIN_UNIV_COVER:
        return False, cover, f"phủ universe {cover:.3f} < {MIN_UNIV_COVER}"
    return True, cover, "ok"


def compute_cars(events, close, univ, src_meta, computed_at):
    """events: EV_COLS · close: DataFrame (index phiên tăng dần, cột ticker, NaN = không giao dịch)
    · univ: DataFrame bool cùng shape (in_universe). Chỉ tính sự kiện có ≥ NEED_AFTER phiên sau phiên 0."""
    cal = close.index
    observed = close.notna()
    ret = close.ffill().pct_change(fill_method=None)
    U = univ.reindex(index=cal, columns=close.columns).fillna(False).astype(bool)
    inb = (U & observed & ret.notna()).values
    R = ret.values
    S_b, C_b = np.where(inb, R, 0.0).sum(1), inb.sum(1)
    tix = {t: j for j, t in enumerate(close.columns)}
    rows = []
    for e in events.itertuples(index=False):
        i0 = int(cal.searchsorted(pd.Timestamp(e.eff_date)))
        j = tix.get(e.ticker)
        if j is None or i0 - WPRE - 1 < 0 or i0 + NEED_AFTER >= len(cal):
            continue
        sl = slice(i0 - WPRE, i0 + WPOST + 1)
        r = R[sl, j]
        own = inb[sl, j]
        b3 = np.where(own, (S_b[sl] - np.where(own, R[sl, j], 0)) / np.maximum(C_b[sl] - 1, 1),
                      S_b[sl] / np.maximum(C_b[sl], 1))
        ar = np.where(np.isnan(r), 0.0, r - b3)
        cum = np.cumsum(ar)
        row = dict(ticker=e.ticker, quarter=e.quarter, eff_date=e.eff_date, grp=e.grp, excl=e.excl,
                   session0=cal[i0].strftime("%Y-%m-%d"), in_univ0=bool(U.values[i0, j]),
                   n_obs_win=int(observed.values[sl, j].sum()), computed_at=computed_at, prereg_md5=PREREG_MD5, **src_meta)
        for w, (lo, hi) in WIN.items():
            row[f"car{w}"] = float(cum[hi + WPRE] - cum[lo - 1 + WPRE])
        rows.append(row)
    return pd.DataFrame(rows, columns=CAR_COLS)


def locked_mismatches(base, locked):
    """Danh sách mô tả file khoá bị thiếu/lệch md5 (rỗng = sạch)."""
    bad = []
    for name, want in locked.items():
        p = os.path.join(base, name)
        if not os.path.exists(p):
            bad.append(f"{name}: thiếu file")
            continue
        got = hashlib.md5(open(p, "rb").read()).hexdigest()
        if got != want:
            bad.append(f"{name}: md5 {got} != khai báo {want}")
    return bad


def append_only(path, new, cols, key=("ticker", "quarter")):
    """Ghi thêm dòng có khoá chưa tồn tại; tmp + os.replace. Trả số dòng đã thêm. Không bao giờ sửa dòng cũ."""
    old = pd.read_csv(path, dtype=str, keep_default_na=False) if os.path.exists(path) else pd.DataFrame(columns=cols)
    if list(old.columns) != cols:
        raise SystemExit(f"❌ {path}: header lệch schema {list(old.columns)} != {cols} — dừng, không ghi")
    have = set(zip(*[old[k] for k in key])) if len(old) else set()
    new = new[[tuple(str(v) for v in t) not in have for t in zip(*[new[k] for k in key])]] if len(new) else new
    if not len(new):
        return 0
    out = pd.concat([old, new.astype(str)[cols]], ignore_index=True)
    assert out.iloc[:len(old)].equals(old), "append-only bị vi phạm"
    tmp = f"{path}.tmp.{os.getpid()}"
    out.to_csv(tmp, index=False)
    os.replace(tmp, path)
    return len(new)


# ---------------- BQ (chỉ đọc) ----------------
def _bq():
    from google.cloud import bigquery
    return bigquery.Client(project="lithe-record-440915-m9")


def _q(c, sql):
    df = c.query(sql).to_dataframe()
    for col in ("time", "Release_Date"):
        if col in df:
            df[col] = pd.to_datetime(df[col].astype(str), errors="coerce")
    return df


def price_source(c):
    """Chọn nguồn giá qua cổng: live trước, rồi pin mới nhất. Trả (bảng, meta) hoặc (None, meta lỗi)."""
    pins = _q(c, "SELECT table_name FROM tav2_pin.INFORMATION_SCHEMA.TABLES "
                 "WHERE REGEXP_CONTAINS(table_name, r'^ticker_pin_[0-9]{6}$') ORDER BY table_name DESC LIMIT 1")
    cands = ["tav2_bq.ticker"] + [f"tav2_pin.{t}" for t in pins.table_name]
    tried = []
    for tbl in cands:
        # n_px = số mã TOÀN BẢNG (đếm theo phiên dao động 650-1.260 kể cả bảng lành ⇒ không dùng được);
        # phủ = mã in_universe ở phiên universe mới nhất có ≥1 giá trong 30 ngày cuối của bảng.
        s = _q(c, f"""WITH mx AS (SELECT MAX(time) d FROM {tbl} WHERE time >= DATE_SUB(CURRENT_DATE('Asia/Ho_Chi_Minh'), INTERVAL 60 DAY)),
            px AS (SELECT DISTINCT p.ticker FROM {tbl} AS p, mx WHERE p.time BETWEEN DATE_SUB(mx.d, INTERVAL 30 DAY) AND mx.d),
            ud AS (SELECT MAX(u.time) d FROM tav2_mike.universe_pit AS u, mx WHERE u.time <= mx.d),
            un AS (SELECT DISTINCT u.ticker FROM tav2_mike.universe_pit AS u, ud WHERE u.time = ud.d AND u.in_universe)
            SELECT (SELECT d FROM mx) AS d, (SELECT COUNT(DISTINCT a.ticker) FROM {tbl} AS a) AS n_px,
                   (SELECT COUNT(*) FROM un) AS n_un, (SELECT COUNT(*) FROM un JOIN px USING (ticker)) AS n_cov""").iloc[0]
        ok, cover, why = coverage_gate(int(s.n_px), int(s.n_un), int(s.n_cov))
        tried.append(f"{tbl}: {why} (n_px={s.n_px}, phủ={cover:.3f}, d={s.d})")
        if ok:
            return tbl, dict(px_source=f"{tbl}@{s.d}", px_n_tickers=int(s.n_px), px_univ_cover=round(cover, 4)), tried
    return None, None, tried


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="in kết quả, không ghi CSV")
    a = ap.parse_args()
    now = dt.datetime.now(ICT).strftime("%Y-%m-%dT%H:%M:%S%z")
    print(f"[rating_8l_forward_tracker] bắt đầu {now} (ICT)")
    bad = locked_mismatches(LOCK_DIR, LOCKED)
    if bad:
        print("❌ file khoá lệch md5 — dừng, KHÔNG ghi ledger: " + "; ".join(bad))
        return 2
    c = _bq()
    fa = _q(c, "SELECT f.ticker, f.time, f.route, f.rating FROM tav2_bq.fa_ratings_8l AS f WHERE f.time >= '2025-06-01'")
    tf = _q(c, "SELECT t.ticker, t.quarter, t.time, t.Release_Date FROM tav2_bq.ticker_financial AS t WHERE t.time >= '2025-01-01'")
    known = set()
    if os.path.exists(EVENTS_CSV):
        k = pd.read_csv(EVENTS_CSV, dtype=str)
        known = set(zip(k.ticker, k.quarter))
    new_ev = detect_events(fa, tf, known, now)
    print(f"[events] mới {len(new_ev)} {new_ev.grp.value_counts().to_dict()} | loại ca {int(new_ev.excl.sum())}")
    if not a.dry_run:
        print(f"[events] ghi thêm {append_only(EVENTS_CSV, new_ev, EV_COLS)} dòng → {EVENTS_CSV}")
    all_ev = pd.read_csv(EVENTS_CSV, dtype=str) if os.path.exists(EVENTS_CSV) else new_ev.astype(str)
    all_ev["excl"] = all_ev.excl.astype(str).eq("True")
    done = set()
    if os.path.exists(CAR_CSV):
        k = pd.read_csv(CAR_CSV, dtype=str)
        done = set(zip(k.ticker, k.quarter))
    todo = all_ev[[t not in done for t in zip(all_ev.ticker, all_ev.quarter)]]
    if not len(todo):
        print("[car] không có sự kiện chờ CAR"); return 0
    tbl, meta, tried = price_source(c)
    for t in tried:
        print(f"[car] cổng nguồn giá: {t}")
    if tbl is None:
        print(f"❌ BLOCKED — không nguồn giá nào qua cổng độ phủ; KHÔNG tính CAR ({len(todo)} sự kiện chờ)")
        return 0
    lo = (pd.to_datetime(todo.eff_date).min() - pd.Timedelta(days=130)).strftime("%Y-%m-%d")
    px = _q(c, f"SELECT p.ticker, p.time, p.Close FROM {tbl} AS p WHERE p.time >= '{lo}' AND p.ticker IN "
               f"(SELECT DISTINCT u.ticker FROM tav2_mike.universe_pit AS u WHERE u.in_universe AND u.time >= '{lo}')")
    un = _q(c, f"SELECT u.ticker, u.time FROM tav2_mike.universe_pit AS u WHERE u.in_universe AND u.time >= '{lo}'")
    close = px.pivot(index="time", columns="ticker", values="Close").sort_index()
    close = close[close.notna().sum(axis=1) >= 100]          # lịch = phiên có ≥100 mã có giá
    univ = un.assign(v=True).pivot(index="time", columns="ticker", values="v")
    cars = compute_cars(todo, close, univ, meta, now)
    print(f"[car] tính được {len(cars)} / {len(todo)} (phần còn lại chưa đủ {NEED_AFTER} phiên sau eff hoặc thiếu giá)")
    if not a.dry_run and len(cars):
        print(f"[car] ghi thêm {append_only(CAR_CSV, cars, CAR_COLS)} dòng → {CAR_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
