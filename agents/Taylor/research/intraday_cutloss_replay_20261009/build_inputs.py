#!/usr/bin/env python3
"""build_inputs.py — dựng đầu vào cho replay lịch sử cổng giá trong phiên (job Taylor_20261009_094633).

PAPER-ONLY, chỉ ĐỌC. Ghi vào ./cache/:
  holdings_ledger.parquet  — danh mục point-in-time từ ledger R3 pin (BAL/LAG TX + custom30V members khi park>0)
  holdings_live.parquet    — vị thế thật SpaceX/ZaloPay từ verified_snapshot_<TK>_<ngày>.json (asof ngày trước)
  daily.parquet            — BQ tav2_bq.ticker daily (Open/High/Low/Close adj, Price raw, Volume) cho mọi mã liên quan + VNINDEX
  vni_1m/<ngày>.json       — VNINDEX bar 1 phút DNSE (ReadOnlyDNSE, chỉ inquiry)
  stk_1m/<ngày>_<MÃ>.json  — bar 1 phút cổ phiếu DNSE (chỉ có ~3 tháng gần nhất: từ 2026-07-09)
  exchange.json            — sàn hiện tại theo DNSE secdef (GIỚI HẠN: sàn HIỆN TẠI, không point-in-time)
Không dùng cột profit_* ở bất kỳ đâu.
"""
import datetime as dt
import glob
import json
import os
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
sys.path.insert(0, os.path.join(WC, "mike", "bin"))
HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, "cache")
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
LEDGER = os.path.join(WC, "data/pinned_ledgers/2026-09-28__R3-anchor-pin0pct-sexies__4707bcbe.csv.gz")
PKL = os.path.join(WC, "data/intraday_full.pkl")
WIN_START = dt.date(2023, 9, 11)          # đầu độ phủ intraday_full.pkl
LIVE_1M_START = dt.date(2026, 7, 9)       # DNSE chỉ giữ bar 1 phút cổ phiếu ~3 tháng
DAILY_START = "2013-12-01"


BASKET = "CUSTOM_VN30EXVIC_PITG"


def ledger_holdings():
    """Số dư cổ phiếu theo (mã, book) đầu ngày D từ TX (mua +, bán −; TX ngày D chỉ có hiệu lực từ D+1,
    bán trong ngày D ⇒ vẫn giữ lúc mở cửa D). Tỉ trọng = số dư × giá TX gần nhất / combined_nav(D−1).
    Rổ custom30V (TX ticker CUSTOM_VN30EXVIC_PITG) bung thành members quý hiện hành, chia đều."""
    d = pd.read_csv(LEDGER, low_memory=False)
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce", format="mixed")
    daily = d[d.record_type == "DAILY"].set_index("ymd").sort_index()
    days = daily.index
    nav_prev = daily.combined_nav.shift(1)
    tx = d[(d.record_type == "TX") & (d.reason != "MTM_UNREALIZED")].copy()
    tx["sh"] = tx.shares.where(tx.action == "buy", -tx.shares)
    rows = []
    for (tk, book), g in tx.groupby(["ticker", "book"]):
        g = g.sort_values("ymd")
        bal = g.groupby("ymd").sh.sum().cumsum()
        px = g.groupby("ymd").adj_price.last()
        # số dư đầu ngày D = cumsum tới ngày < D
        idx = days[days > bal.index.min()]
        b_prev = bal.reindex(days).ffill().shift(1).reindex(idx)
        p_prev = px.reindex(days).ffill().shift(1).reindex(idx)
        for D, sh in b_prev.items():
            if sh and sh > 1e-6 and nav_prev.get(D):
                rows.append((D, tk, book, sh * p_prev[D] / nav_prev[D]))
    h = pd.DataFrame(rows, columns=["date", "ticker", "book", "weight"])
    mem = d[d.record_type == "CUSTOM_MEMBERS"][["ymd", "ticker"]]
    mdates = sorted(mem.ymd.unique())
    bk = h[h.ticker == BASKET]
    h = h[h.ticker != BASKET]
    crow = []
    for D, w in bk.groupby("date").weight.sum().items():
        md = [m for m in mdates if m <= D]
        if not md:
            continue
        names = mem[mem.ymd == md[-1]].ticker.tolist()
        for t in names:
            crow.append((D, t, "CUSTOM30V", w / len(names)))
    h = pd.concat([h, pd.DataFrame(crow, columns=h.columns)], ignore_index=True)
    h = (h.sort_values("weight", ascending=False).groupby(["date", "ticker"], as_index=False)
         .agg(book=("book", "first"), weight=("weight", "sum")))
    h["state"] = h.date.map(daily.state)
    return h


def live_holdings():
    rows = []
    for lab in ("SpaceX", "ZaloPay"):
        snaps = sorted(glob.glob(os.path.join(WC, f"data/execution_logs/verified_snapshot_{lab}_*.json")))
        for f in snaps:
            asof = dt.date.fromisoformat(os.path.basename(f)[-15:-5])
            for p in json.load(open(f)).get("positions") or []:
                if p.get("qty"):
                    rows.append((asof, lab, p["ticker"].upper(), int(p["qty"]), p.get("true_avg_cost")))
    return pd.DataFrame(rows, columns=["snap_date", "account", "ticker", "qty", "cost"])


def bq_daily(tickers):
    tl = ",".join(f"'{t}'" for t in sorted(set(tickers) | {"VNINDEX"}))
    sql = (f"SELECT t.time, t.ticker, t.Open, t.High, t.Low, t.Close, t.Price, t.Volume "
           f"FROM tav2_bq.ticker AS t WHERE t.time >= '{DAILY_START}' AND t.ticker IN ({tl})")
    env = "source /home/trido/thanhdt/WorkingClaude/wc_env.sh && "
    out = os.path.join(C, "daily.csv")
    cmd = (env + "bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv "
           f"--max_rows=5000000 \"{sql}\" > {out}")
    subprocess.run(["bash", "-c", cmd], check=True)
    df = pd.read_csv(out)
    df["time"] = pd.to_datetime(df["time"])
    df.to_parquet(os.path.join(C, "daily.parquet"))
    os.remove(out)
    return df


def dnse():
    from intraday_price_watch import ReadOnlyDNSE
    from trading_bot.brokers import get_dnse_client
    return ReadOnlyDNSE(get_dnse_client())


def fetch_bars(ro, sym, day, index, out):
    if os.path.exists(out):
        return
    a = dt.datetime.combine(day, dt.time(8, 30), ICT)
    b = dt.datetime.combine(day, dt.time(15, 30), ICT)
    for k in range(3):
        try:
            r = ro.ohlc(sym, resolution="1", bar_type="index" if index else "stock",
                        **{"from": int(a.timestamp()), "to": int(b.timestamp())})
            json.dump({"t": r.get("t") or [], "c": r.get("c") or [], "o": r.get("o") or [],
                       "l": r.get("l") or [], "v": r.get("v") or []}, open(out, "w"))
            return
        except Exception as e:     # noqa: BLE001
            print(f"  ⚠ {sym} {day} lần {k+1}: {e}")
            time.sleep(2)


def main_holdings_only():
    hl = ledger_holdings()
    hl.to_parquet(os.path.join(C, "holdings_ledger.parquet"))
    print(hl.shape, hl.groupby("book").size().to_dict(), hl.groupby("date").size().describe().to_dict())


def main():
    os.makedirs(C, exist_ok=True)
    os.makedirs(os.path.join(C, "vni_1m"), exist_ok=True)
    os.makedirs(os.path.join(C, "stk_1m"), exist_ok=True)
    hl = ledger_holdings()
    hl.to_parquet(os.path.join(C, "holdings_ledger.parquet"))
    print("ledger holdings", hl.shape, hl.date.min(), hl.date.max())
    lv = live_holdings()
    lv.to_parquet(os.path.join(C, "holdings_live.parquet"))
    print("live holdings", lv.shape, lv.snap_date.min(), lv.snap_date.max())
    pk = pd.read_pickle(PKL)
    names = set(hl.ticker) | set(lv.ticker)
    daily = bq_daily(names)
    print("daily", daily.shape, daily.time.max())
    ro = dnse()
    vdays = sorted(d.date() for d in daily[(daily.ticker == "VNINDEX") & (daily.time.dt.date >= WIN_START)].time)
    today = dt.datetime.now(ICT).date()
    vdays = [d for d in vdays if d <= today]
    # BQ có thể trễ: bổ sung ngày giao dịch gần nhất từ lịch
    from trading_bot.vn_market import is_holiday
    d = vdays[-1] + dt.timedelta(days=1)
    while d <= today:
        if d.weekday() < 5 and not is_holiday(d):
            vdays.append(d)
        d += dt.timedelta(days=1)
    for i, day in enumerate(vdays):
        fetch_bars(ro, "VNINDEX", day, True, os.path.join(C, "vni_1m", f"{day}.json"))
        if i % 100 == 0:
            print("vni", i, day)
    for day in [x for x in vdays if x >= LIVE_1M_START]:
        held = lv[lv.snap_date < day]
        if held.empty:
            continue
        tks = set()
        for lab, g in held.groupby("account"):
            tks |= set(g[g.snap_date == g.snap_date.max()].ticker)
        for t in sorted(tks):
            fetch_bars(ro, t, day, False, os.path.join(C, "stk_1m", f"{day}_{t}.json"))
    ex = {}
    allt = sorted(names | set(pk))
    for t in allt:
        try:
            sd = ro.secdef(t)
            from trading_bot.brokers import DNSEBroker, Quote
            q = Quote({"symbol": t, **DNSEBroker._pick_board(sd, "secdefs")})
            ex[t] = q.exchange if q.exchange_known else None
        except Exception as e:     # noqa: BLE001
            ex[t] = None
    json.dump(ex, open(os.path.join(C, "exchange.json"), "w"), indent=0)
    print("exchange", sum(1 for v in ex.values() if v), "/", len(ex))


if __name__ == "__main__":
    main_holdings_only() if "--holdings-only" in sys.argv else main()
