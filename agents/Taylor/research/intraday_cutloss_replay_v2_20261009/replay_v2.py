#!/usr/bin/env python3
"""replay_v2.py — replay v2 (job Taylor_20261009_110243). Dùng LẠI replay.py v1 (HistMarket, nguồn bar, tiêm
phán quyết, run_tick THẬT) nhưng: (1) chọn code watcher `--code new|old` (new = master 9a1eeede sau PHẦN 1,
old = 5050f6fa trước sửa; bản chụp ở new_bin/ old_bin/ — không đọc mike/bin sống để kết quả tái lập được);
(2) universe v2 (PREREG): ledger R3 lọc ADV20 ≥ 1 tỷ ∪ tập mã SpaceX/ZaloPay đang giữ (09/10/2026), NAV 50 tỷ;
`--universe v1` = ledger R3 nguyên như v1 (NAV 1 tỷ) để so; (3) độ nhạy sổ lệnh `--ticks 1|3` × `--depth-mult`;
(4) ghi thêm `bar_t` (thời điểm bar mới nhất nhìn thấy) vào quote để lọc quote cũ.
PAPER-ONLY. Ngày giao dịch [start, end] của shard + `--tail` ngày đuôi (cho ca carryover); chấm chỉ lấy t0
thuộc khối của shard."""
import argparse
import datetime as dt
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "intraday_cutloss_replay_20261009")
ap = argparse.ArgumentParser()
ap.add_argument("--code", choices=("new", "old"), default="new")
ap.add_argument("--universe", choices=("v1", "v2"), default="v2")
ap.add_argument("--scenario", default="BROKEN", choices=("NONE", "BROKEN", "UNCLEAR"))
ap.add_argument("--depth-mult", type=float, default=0.5)
ap.add_argument("--ticks", type=int, default=3, choices=(1, 3))
ap.add_argument("--days", required=True, help="file ngày (khối của shard)")
ap.add_argument("--tail", type=int, default=2)
ap.add_argument("--out", required=True)
A = ap.parse_args()
A.days, A.out = os.path.abspath(A.days), os.path.abspath(A.out)

sys.path.insert(0, os.path.join(HERE, f"{A.code}_bin"))
import intraday_cutloss_engine as E  # noqa: E402,F401
import intraday_price_watch as ipw  # noqa: E402,F401
assert os.path.dirname(ipw.__file__) == os.path.join(HERE, f"{A.code}_bin"), ipw.__file__
sys.path.insert(0, V1)
os.chdir(V1)
import replay as R  # noqa: E402  (tái dùng module đã import ở trên — sys.modules)
assert R.ipw is ipw and R.E is E

import pandas as pd  # noqa: E402

NAV_V2 = 50_000_000_000
LIVESET = ["PVT", "DRI", "SCL", "SIP", "VPB", "MSB", "VIB", "TPB", "MBB", "VNM", "TV1", "SAB", "NCT", "VPI"]
LIVESET_BOOK = {"TV1": E.DISCRETIONARY}          # TV1 = sleeve discretionary thật
D = R.DAILY.copy()
D["val"] = D.Price * D.Volume
D = D.sort_values(["ticker", "d"])
D["adv20"] = D.groupby("ticker").val.transform(lambda s: s.rolling(20, min_periods=10).median().shift(1))
ADV = {(t, d): v for t, d, v in zip(D.ticker, D.d, D.adv20)}


def universe_v2(day):
    g = R.HL[R.HL.d == day]
    hold, uni = {}, {}
    for _, r in g.iterrows():
        ref = R.raw_ref(r.ticker, day)
        adv = ADV.get((r.ticker, day))
        if not ref or not r.weight or r.weight <= 0 or not (adv and adv >= 1e9):
            continue
        qty = max(100, int(r.weight * NAV_V2 / ref // 100) * 100)
        hold[r.ticker] = {"qty": qty, "sellable": qty, "cost": None}
        uni[r.ticker] = {"holdings": {"HIST": {"qty": qty, "sellable": qty, "cost": None, "book": r.book,
                                               "account_id": "HIST", "no_auto_sell": None}},
                         "buys": [], "watch": False}
    for t in LIVESET:
        if t in uni:
            continue
        ref = R.raw_ref(t, day)
        if not ref:
            continue
        qty = max(100, int(0.05 * NAV_V2 / ref // 100) * 100)
        hold[t] = {"qty": qty, "sellable": qty, "cost": None}
        uni[t] = {"holdings": {"HIST": {"qty": qty, "sellable": qty, "cost": None,
                                        "book": LIVESET_BOOK.get(t, "LIVESET"), "account_id": "HIST",
                                        "no_auto_sell": None}}, "buys": [], "watch": False}
    return uni, {"HIST": hold}


class HM(R.HistMarket):
    def quote(self, sym):
        q = super().quote(sym)
        if q.get("bids") and A.ticks == 1:
            q["bids"] = q["bids"][:1]
        s = self._s(sym)
        av = self._avail(s[1]) if s else []
        q["bar_t"] = av[-1][0].isoformat() if av else None
        return q


R.HistMarket = HM
if A.universe == "v2":
    R.ledger_universe = universe_v2


def main():
    out = A.out
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    block = [dt.date.fromisoformat(x.strip()) for x in open(A.days) if x.strip()]
    td = sorted(R.TDAYS | {dt.date(2026, 10, 9)})
    i = td.index(block[-1]) if block[-1] in td else None
    days = block + (td[i + 1:i + 1 + A.tail] if i is not None else [])
    t0 = time.time()
    for k, day in enumerate(days):
        live = day >= R.LIVE_1M_START
        if not live and day > R.LEDGER_END:
            continue
        if not live and A.universe == "v1" and not (R.HL.d == day).any():
            continue
        R.run_day(day, A.scenario, out, A.depth_mult, live)
        if k % 25 == 0:
            print(f"{k}/{len(days)} {day} {time.time()-t0:.0f}s", flush=True)
    with open(os.path.join(out, "block.txt"), "w") as f:
        f.write("\n".join(d.isoformat() for d in block))
    print("done", out, f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
