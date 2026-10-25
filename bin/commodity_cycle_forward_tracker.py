#!/usr/bin/env python3
"""Commodity early-cycle — sổ nhật ký FORWARD (PAPER-ONLY, không lệnh/plan/trading_rules).

Thiết kế đóng băng ở `agents/Taylor/research/commodity_cycle_prereg2_20261025/PREREG-2.md`.
Ô duy nhất: R=P/MA12 cắt lên 1,05, chân trời 63 phiên. Mỗi lần chạy:
  1. Dò sự kiện từ WB CMO. Tháng tín hiệu 2026-03..2026-09 ⇒ PRE_FREEZE_BACKFILL (counts=False); 2026-10..2030-09 và đã
     qua ngày 11 tháng m+1 ⇒ FORWARD (counts=False nếu LATE). APPEND-ONLY `data/commodity_cycle_forward_events.csv`,
     khoá (family, signal_month).
  2. Sự kiện đủ 63 phiên ⇒ X = r_exp − r_ctrl, APPEND-ONLY `data/commodity_cycle_forward_outcomes.csv`.
Tracker KHÔNG in TB/CI/p (PREREG §7); verdict = `commodity_cycle_forward_review.py`.

Chạy: $DNA_PYEXE mike/bin/commodity_cycle_forward_tracker.py [--dry-run] [--data-dir DIR]
Selfcheck: mike/bin/commodity_cycle_forward_tracker_selfcheck.py
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
HERE = os.path.dirname(os.path.abspath(__file__))
LOCK_DIR = os.path.join(HERE, "..", "agents/Taylor/research/commodity_cycle_prereg2_20261025")
PREREG_MD5 = "2962d12f206b542c58e472a58521f18c"
MAP_MD5 = "cf4bef531aba172309e433113261b957"
LOCKED = {"PREREG-2.md": PREREG_MD5, "commodity_map.csv": MAP_MD5}
CMO = os.path.join(WC_ROOT, "data/_wb_cache/CMO-Historical-Data-Monthly.xlsx")
SERIES = {"rubber": "Rubber, RSS3", "crude oil": "Crude oil, average", "urea": "Urea ",
          "DAP": "DAP", "sugar": "Sugar, world"}
TH, H = 1.05, 63
BACKFILL_FROM, FWD_FROM, FWD_TO = pd.Period("2026-03", "M"), pd.Period("2026-10", "M"), pd.Period("2030-09", "M")
LATE_SESSIONS = 10
EV_COLS = ["family", "signal_month", "R", "status", "counts", "reason", "entry_floor", "first_seen",
           "prereg_md5", "map_md5"]
OUT_COLS = ["family", "signal_month", "entry_date", "counts", "n_exp", "n_ctrl", "r_exp", "r_ctrl", "X",
            "fallback", "exp", "note", "computed_at"]


# ---------------- logic thuần (selfcheck gọi trực tiếp) ----------------
def load_wb(path=CMO):
    raw = pd.read_excel(path, "Monthly Prices", header=4).iloc[1:]
    raw = raw.rename(columns={raw.columns[0]: "m"})
    raw["month"] = pd.PeriodIndex(raw.m.str.replace("M", "-"), freq="M")
    return {f: pd.to_numeric(raw.set_index("month")[c], errors="coerce").dropna() for f, c in SERIES.items()}


def find_events(s, th=TH):
    """[(month, R)] — R_m ≥ th, R_{m-1} < th, thời gian chết 12 tháng trên TOÀN lịch sử (như run.py của job 061240)."""
    R = s / s.rolling(12).mean()
    out, last = [], None
    for m in R.index[13:]:
        if R[m] >= th and R[m - 1] < th and (last is None or (m - last).n > 12):
            last = m
            out.append((m, float(R[m])))
    return out


def day11(month):
    return (month + 1).to_timestamp() + pd.Timedelta(days=10)


def entry_session(days, floor):
    i = days.searchsorted(pd.Timestamp(floor), side="left")
    return days[i] if i < len(days) else None


def classify(month, today, days, first_seen=None):
    """→ (status, counts, reason, entry_floor) hoặc None nếu chưa ghi (ngoài cửa sổ / chưa tới ngày 11)."""
    d11 = day11(month)
    if BACKFILL_FROM <= month < FWD_FROM:
        return "PRE_FREEZE_BACKFILL", False, "PRE_FREEZE", d11
    if not (FWD_FROM <= month <= FWD_TO) or today < d11:
        return None
    fs = pd.Timestamp(first_seen or today)
    floor = max(d11, fs + pd.Timedelta(days=1))
    late = days.searchsorted(fs, side="right") - days.searchsorted(d11, side="left") - 1 > LATE_SESSIONS
    return "FORWARD", (not late), ("LATE" if late else ""), floor


class Market:
    def __init__(self, close, icb, umembers, all_mapped, fam_tickers):
        self.close, self.icb, self.umembers = close, icb, umembers
        self.all_mapped, self.fam_tickers = all_mapped, fam_tickers
        self.days = close.index

    def fwd(self, t, tickers, h):
        i = self.days.get_loc(t)
        j = min(i + h, len(self.days) - 1)
        sub = self.close.loc[:, [x for x in tickers if x in self.close.columns]]
        return (sub.iloc[j] / sub.iloc[i] - 1).dropna()

    def measure(self, fam, t, h=H):
        uni = self.umembers.get(t, set())
        exp = [x for x in self.fam_tickers[fam] if x in uni]
        if not exp:
            return None
        ss = {self.icb.get(x, "")[:2] for x in self.fam_tickers[fam]} - {""}
        ctrl = [x for x in uni if x not in self.all_mapped and self.icb.get(x, "")[:2] in ss]
        fb = len(ctrl) < 5
        if fb:
            ctrl = [x for x in uni if x not in self.all_mapped]
        re, rc = self.fwd(t, exp, h), self.fwd(t, ctrl, h)
        if re.empty or rc.empty:
            return None
        return dict(n_exp=len(re), n_ctrl=len(rc), r_exp=re.mean(), r_ctrl=rc.mean(), X=re.mean() - rc.mean(),
                    fallback=fb, exp=",".join(sorted(re.index)))


def load_market(map_csv=None):
    import duckdb
    cmap = pd.read_csv(map_csv or os.path.join(LOCK_DIR, "commodity_map.csv"))
    prim = cmap[cmap.in_primary == "Y"]
    con = duckdb.connect()
    P = con.sql(f"""select time, ticker, Close, ICB_Code from read_parquet('{WC_ROOT}/data/bq_cache/ticker/*.parquet')
                   where time >= '2013-06-01' and Close > 0""").df()
    P["time"] = pd.to_datetime(P.time)
    close = P.pivot_table(index="time", columns="ticker", values="Close").sort_index().ffill()
    icb = P.dropna(subset=["ICB_Code"]).groupby("ticker").ICB_Code.last().astype(int).astype(str).str.zfill(4)
    U = con.sql(f"""select time, ticker from read_parquet('{WC_ROOT}/data/bq_cache/universe_pit/*.parquet')
                   where in_universe""").df()
    U["time"] = pd.to_datetime(U.time)
    return Market(close, icb, U.groupby("time").ticker.apply(set), set(cmap.ticker),
                  prim.groupby("commodity").ticker.apply(list).to_dict())


def new_event_rows(wb, ledger_keys, today, days, first_seen_ts):
    rows = []
    for fam, s in wb.items():
        for m, r in find_events(s):
            if (fam, str(m)) in ledger_keys:
                continue
            c = classify(m, today, days, first_seen_ts)
            if c is None:
                continue
            st, counts, reason, floor = c
            rows.append(dict(family=fam, signal_month=str(m), R=round(r, 4), status=st, counts=counts,
                             reason=reason, entry_floor=floor.strftime("%Y-%m-%d"),
                             first_seen=first_seen_ts, prereg_md5=PREREG_MD5, map_md5=MAP_MD5))
    return pd.DataFrame(rows, columns=EV_COLS)


def new_outcome_rows(events, done_keys, mk, now_s):
    rows, log = [], []
    for _, e in events.iterrows():
        key = (e.family, e.signal_month)
        if key in done_keys:
            continue
        t = entry_session(mk.days, e.entry_floor)
        if t is None or mk.days.get_loc(t) + H > len(mk.days) - 1:
            log.append(f"pending {key}: chưa đủ {H} phiên sau {e.entry_floor}")
            continue
        if t not in mk.umembers.index:
            log.append(f"BLOCKED {key}: universe_pit không có ngày {t.date()}")
            continue
        r = mk.measure(e.family, t)
        base = dict(family=e.family, signal_month=e.signal_month, entry_date=t.strftime("%Y-%m-%d"),
                    counts=bool(e.counts), computed_at=now_s)
        if r is None:
            rows.append({**base, "n_exp": 0, "n_ctrl": 0, "r_exp": np.nan, "r_ctrl": np.nan, "X": np.nan,
                         "fallback": False, "exp": "", "note": "NO_EXPOSED"})
        else:
            rows.append({**base, **r, "note": ""})
    return pd.DataFrame(rows, columns=OUT_COLS), log


def check_locks(lock_dir=None, locked=None):
    bad = []
    for n, md5 in (locked or LOCKED).items():
        p = os.path.join(lock_dir or LOCK_DIR, n)
        got = hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"
        if got != md5:
            bad.append(f"{n}: {got} != {md5}")
    return bad


def _append(path, new, cols):
    old = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame(columns=cols)
    out = pd.concat([old, new], ignore_index=True)[cols] if len(new) else old
    tmp = path + ".tmp"
    out.to_csv(tmp, index=False)
    os.replace(tmp, path)


def main(argv=None, wb=None, mk=None, now=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--data-dir", default=os.path.join(WC_ROOT, "data"))
    a = ap.parse_args(argv)
    bad = check_locks()
    if bad:
        print("LOCK MISMATCH — dừng, không ghi sổ:\n  " + "\n  ".join(bad))
        return 2
    now = now or dt.datetime.now(ICT)
    today, fs = pd.Timestamp(now.date()), now.strftime("%Y-%m-%d")
    wb = wb if wb is not None else load_wb()
    mk = mk if mk is not None else load_market()
    evp = os.path.join(a.data_dir, "commodity_cycle_forward_events.csv")
    outp = os.path.join(a.data_dir, "commodity_cycle_forward_outcomes.csv")
    ev_old = pd.read_csv(evp) if os.path.exists(evp) else pd.DataFrame(columns=EV_COLS)
    ev_new = new_event_rows(wb, set(zip(ev_old.family, ev_old.signal_month)), today, mk.days, fs)
    ev_all = pd.concat([ev_old, ev_new], ignore_index=True)
    out_old = pd.read_csv(outp) if os.path.exists(outp) else pd.DataFrame(columns=OUT_COLS)
    out_new, log = new_outcome_rows(ev_all, set(zip(out_old.family, out_old.signal_month)), mk,
                                    now.strftime("%Y-%m-%d %H:%M %z"))
    print(f"[{fs} ICT] sự kiện mới {len(ev_new)} · kết quả mới {len(out_new)} · sổ sự kiện {len(ev_all)} dòng "
          f"(counts=True: {int(ev_all.counts.astype(str).eq('True').sum())})")
    for ln in log:
        print("  " + ln)
    print("  R hiện tại (mô tả): " + " · ".join(
        f"{f} {s.index[-1]} R={float((s / s.rolling(12).mean()).iloc[-1]):.3f}" for f, s in wb.items()))
    if a.dry_run:
        print("  --dry-run: không ghi")
        return 0
    os.makedirs(a.data_dir, exist_ok=True)
    _append(evp, ev_new, EV_COLS)
    _append(outp, out_new, OUT_COLS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
