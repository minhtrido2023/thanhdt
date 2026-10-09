#!/usr/bin/env python3
"""replay.py — REPLAY lịch sử cổng giá trong phiên bằng CHÍNH driver `bin/intraday_price_watch.py`.

PAPER-ONLY (job Taylor_20261009_094633). Không sửa watcher, không gọi broker để đặt lệnh, không chạm
data/intraday_watch/ thật. Cách làm: gọi `ipw.run_tick(now, deps)` MỖI PHÚT 09:00-14:59 như cron, chỉ
thay `deps.market` bằng HistMarket (giá lịch sử) — mọi quyết định (trigger, gộp cả thị trường, mở ca,
hạn phán quyết/hạn trả lời, mặc định theo book, hoãn sau 14:00, bộ máy bán 4 chế độ) là code thật.

Dùng: replay.py --scenario NONE|BROKEN|UNCLEAR [--days FILE] [--depth-mult 0.5] [--out DIR]
  NONE    = không có phán quyết agent (đúng như shadow hiện tại chạy --no-dispatch) ⇒ engine mặc định GIỮ
  BROKEN  = agent kết luận GÃY ngay trước hạn (T0+19' thường / T0+9' rút gọn) ⇒ BÁN toàn bộ
  UNCLEAR = agent kết luận CHƯA RÕ ngay trước hạn ⇒ BÁN 50% (book V2.4), GIỮ (discretionary/UNKNOWN)
User luôn IM LẶNG (không trả lời) ⇒ mặc định áp khi hết hạn trả lời.

GIẢ ĐỊNH (không có dữ liệu lịch sử tương ứng — ghi rõ trong REPORT):
  A1 sổ lệnh mua: KHÔNG có lịch sử ⇒ dựng 3 mức last−1..3 bước giá, mỗi mức = depth_mult × KL khớp
     trung bình/phút 15' gần nhất; tại giá sàn: 1 mức ở sàn nếu phút gần nhất có KL, ngược lại trắng.
  A2 giá trong phiên 2023-09-11..2026-06-19 = bar 15' (data/intraday_full.pkl tới 05-12 + cache/vn15 vnstock/VCI cho mã thiếu & sau 05-12; giá điều
     chỉnh) quy về VND thô bằng hệ số Price_BQ(D)/close_bar_cuối(D); giá trong phút = bậc thang (bar
     15' gán vào phút cuối của nó ⇒ chỉ thấy SAU khi bar đóng, không nhìn trước).
  A3 2026-07-09..2026-10-09 = bar 1' DNSE thật (lịch sử DNSE đã điều chỉnh ⇒ quy về thô bằng Price_BQ(D)).
  A4 sàn = engine.floor_price(TC, sàn) với sàn giao dịch HIỆN TẠI (DNSE secdef) — không point-in-time.
  A5 KL bán được = KL giữ (bỏ qua T+2 của lệnh mua vừa khớp).
  A6 Danh mục 2023-09..2026-06 = ledger R3 pin 4707bcbe (BAL/LAG + custom30V khi park>0), quy về NAV
     1 tỷ; 2026-07..10 = vị thế thật SpaceX/ZaloPay (verified_snapshot ngày trước).
"""
import argparse
import datetime as dt
import json
import os
import shutil
import sys
import time

import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
sys.path.insert(0, os.path.join(WC, "mike", "bin"))
HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, "cache")

import intraday_cutloss_engine as E  # noqa: E402
import intraday_price_watch as ipw  # noqa: E402
import trading_bot.vn_market as vm  # noqa: E402

NAV_SIM = 1_000_000_000
PKL_END = dt.date(2026, 5, 12)
LEDGER_END = dt.date(2026, 6, 19)
LIVE_1M_START = dt.date(2026, 7, 9)
FAKE_BOT_STOP = os.path.join(HERE, "cache", "_no_bot_stop")   # không bao giờ tồn tại

# ---------------------------------------------------------------- lịch giao dịch lịch sử
DAILY = pd.read_parquet(os.path.join(C, "daily.parquet"))
DAILY["d"] = DAILY.time.dt.date
VNI_D = DAILY[DAILY.ticker == "VNINDEX"].set_index("d").sort_index()
TDAYS = set(VNI_D.index)
_orig_is_holiday = vm.is_holiday


def _hist_is_holiday(d):
    """Lịch lịch sử: ngày thường không có phiên VNINDEX trong BQ = nghỉ (vn_market chỉ khai lễ 2026)."""
    if d > max(TDAYS):
        return _orig_is_holiday(d)
    return d.weekday() < 5 and d not in TDAYS


os.fsync = lambda fd: None              # replay: ghi state mỗi phút × 690 ngày ⇒ fsync nghẽn jbd2 (chỉ I/O,
                                        # không đổi logic quyết định; file vẫn ghi atomic tmp+replace)
vm.is_holiday = _hist_is_holiday          # next_trading_day/prev_trading_day/session_phase tra global này
PX = {t: g.set_index("d").sort_index() for t, g in DAILY.groupby("ticker")}
EXCH = json.load(open(os.path.join(C, "exchange.json")))
_PKL = None


def pkl():
    global _PKL
    if _PKL is None:
        _PKL = pd.read_pickle(os.path.join(WC, "data", "intraday_full.pkl"))
        for t, x in _PKL.items():
            x["time"] = pd.to_datetime(x["time"])
            x["d"] = x.time.dt.date
    return _PKL


def _prev_td(d):
    i = sorted(TDAYS)
    k = i.index(d) if d in TDAYS else None
    return i[k - 1] if k else None


def raw_ref(tk, day):
    """TC sàn thô của ngày `day` = Price(D) × Close_adj(D−1)/Close_adj(D) (đúng cả ngày GDKHQ)."""
    p = PX.get(tk)
    pd_ = _prev_td(day)
    if p is None or pd_ is None or pd_ not in p.index:
        return None
    if day in p.index and p.loc[day, "Close"] and p.loc[day, "Price"]:
        return float(p.loc[day, "Price"] * p.loc[pd_, "Close"] / p.loc[day, "Close"])
    return float(p.loc[pd_, "Price"])


def _src_rows(tk, day):
    """Bar điều chỉnh (đơn vị nghìn đồng) của 1 ngày từ 1 nguồn: (nguồn, [(t, open, close, vol)])."""
    if day <= LEDGER_END:
        x = pkl().get(tk) if day <= PKL_END else None
        if x is not None and (x.d == day).any():
            g = x[x.d == day]
            return "pkl", [(r.time.to_pydatetime(), r.open, r.close, int(r.volume)) for r in g.itertuples()]
        x = vn15(tk)
        if x is not None and (x.d == day).any():
            g = x[x.d == day]
            return "vn15", [(r.time.to_pydatetime(), r.open, r.close, int(r.volume)) for r in g.itertuples()]
        return None, []
    if day >= LIVE_1M_START:
        f = os.path.join(C, "stk_1m", f"{day}_{tk}.json")
        if not os.path.exists(f):
            fetch_live(tk, day)
        r = json.load(open(f)) if os.path.exists(f) else {}
        return "dnse1m", [(dt.datetime.fromtimestamp(t, ipw._ICT).replace(tzinfo=None), r["o"][i] if r.get("o")
                           else r["c"][i], r["c"][i], r["v"][i]) for i, t in enumerate(r.get("t") or [])]
    return None, []


def _same_src_prev(tk, day, src):
    pd_ = _prev_td(day)
    if pd_ is None:
        return None
    if src == "pkl":
        x = pkl().get(tk)
    elif src == "vn15":
        x = vn15(tk)
    else:
        s2, rows = _src_rows(tk, pd_)
        return rows[-1][2] if s2 == src and rows else None
    g = x[(x.d == pd_) & (x.close > 0)] if x is not None else None
    return float(g.close.iloc[-1]) if g is not None and len(g) else None


SRC_USED = {}


def load_series(tk, day):
    """→ (ref_raw, bars[(t_avail_label, close_raw, vol)], ato) hoặc None.

    Mọi nguồn intraday lịch sử (pkl/vnstock/DNSE) là giá ĐIỀU CHỈNH theo corp-action về sau ⇒ quy về
    giá thô ngày D bằng f = Price_BQ(D)/close_bar_cuối(D); TC = close bar cuối phiên TRƯỚC của CÙNG nguồn × f
    (cùng gốc điều chỉnh ⇒ đúng cả ngày GDKHQ). Không dùng tỉ lệ Close_adj của BQ cho TC: BQ áp điều chỉnh
    lệch ngày (HDB: Close 05..08/10/2026 đã điều chỉnh, GDKHQ thật 09/10) ⇒ kích hoạt giả."""
    src, rows = _src_rows(tk, day)
    rows = [(t, o if o == o else c, c, int(v) if v == v else 0) for t, o, c, v in rows if c == c and c > 0]
    p = PX.get(tk)
    if not rows or p is None or day not in p.index or not p.loc[day, "Price"]:
        return None
    f = float(p.loc[day, "Price"]) / (float(rows[-1][2]) * 1000)
    prev = _same_src_prev(tk, day, src)
    if prev:
        ref = prev * 1000 * f
    else:
        ref = raw_ref(tk, day)
        src += "+bqref"
    if not ref:
        return None
    SRC_USED[(tk, day)] = src
    bars, ato = [], None
    for t, o, c, v in rows:
        if src.startswith("dnse1m"):
            bars.append((t, c * 1000 * f, v))
            continue
        if t.time() == dt.time(9, 15):
            ato = (o * 1000 * f, 0)
            bars.append((t, o * 1000 * f, 0))                         # giá ATO, thấy từ 09:16
        if t.time() == dt.time(14, 45):
            bars.append((t, c * 1000 * f, int(v)))                    # ATC
        else:
            bars.append((t + dt.timedelta(minutes=14), c * 1000 * f, int(v)))   # bar 15' thấy khi đóng
    bars.sort()
    return ref, bars, ato


_RO = None
_VN15 = {}


def vn15(tk):
    if tk not in _VN15:
        p = os.path.join(C, "vn15", f"{tk}.parquet")
        x = pd.read_parquet(p) if os.path.exists(p) else None
        if x is not None:
            x["time"] = pd.to_datetime(x["time"])
            x["d"] = x.time.dt.date
        _VN15[tk] = x
    return _VN15[tk]


def fetch_live(tk, day):
    global _RO
    import build_inputs as B
    if _RO is None:
        _RO = B.dnse()
    B.fetch_bars(_RO, tk, day, False, os.path.join(C, "stk_1m", f"{day}_{tk}.json"))


def vni_series(day):
    f = os.path.join(C, "vni_1m", f"{day}.json")
    if not os.path.exists(f):
        return []
    r = json.load(open(f))
    return [(dt.datetime.fromtimestamp(t, ipw._ICT).replace(tzinfo=None), r["c"][i], r["v"][i])
            for i, t in enumerate(r.get("t") or [])]


# ---------------------------------------------------------------- thị trường lịch sử (chỉ I/O)
class HistMarket:
    def __init__(self, day, holdings_by_acc, depth_mult):
        self.day, self.hold, self.depth_mult = day, holdings_by_acc, depth_mult
        self.now = None
        self._ser = {}
        self._vni = vni_series(day)
        pd_ = _prev_td(day)
        self._vni_ref = float(VNI_D.loc[pd_, "Close"]) if pd_ in VNI_D.index else None
        self.vni_pending_open, self.vni_note = False, None

    def set_now(self, now):
        self.now = now.replace(tzinfo=None)

    def _s(self, tk):
        if tk not in self._ser:
            self._ser[tk] = load_series(tk, self.day)
        return self._ser[tk]

    def _avail(self, bars):
        # bar nhãn t (phút) chỉ có SAU khi phút đó đóng (DNSE phát bar sau 1 phút)
        return [b for b in bars if b[0] + dt.timedelta(minutes=1) <= self.now]

    def quote(self, sym):
        s = self._s(sym)
        if s is None:
            return {"error": "không có dữ liệu lịch sử"}
        ref, bars, _ = s
        av = self._avail(bars)
        ex = (EXCH.get(sym) or "HOSE").upper()
        floor = E.floor_price(ref, ex)
        last = av[-1][1] if av else None
        if last is not None:
            last = max(last, floor)             # bar điều chỉnh lệch vài đồng dưới sàn ⇒ kẹp về sàn
        recent = [v for _, _, v in av[-15:]]
        per_min = (sum(recent) / max(1, len(recent))) if recent else 0
        bids = []
        if last:
            if last <= floor + E.EPS:
                if av and av[-1][2] > 0:
                    bids = [(floor, int(self.depth_mult * per_min))]
            else:
                tk_ = E.tick_of(last, ex)
                p0 = int(last // tk_) * tk_
                bids = [(max(floor, p0 - k * tk_), int(self.depth_mult * per_min)) for k in (1, 2, 3)]
                bids = [b for b in bids if b[1] > 0]
        return {"last": last, "ref": ref, "floor": floor, "ceiling": None,
                "bid": bids[0][0] if bids else None, "bids": bids, "exchange": ex,
                "exchange_known": sym in EXCH and EXCH[sym] is not None,
                "day_volume": int(sum(v for _, _, v in av))}

    def bars(self, sym, day, index=False):
        s = self._s(sym)
        return self._avail(s[1]) if s else []

    def vni(self, now):
        """Bắt chước LiveMarket.vni (bar 1' + kiểm tra bar cũ) trên dữ liệu lịch sử."""
        bars = self._avail(self._vni)
        last = bars[-1][1] if bars else None
        n = self.now
        grace = dt.timedelta(minutes=ipw.OPEN_GRACE_MIN)
        self.vni_pending_open = not bars and \
            dt.timedelta(0) <= n - n.replace(hour=9, minute=15, second=0, microsecond=0) < grace
        self.vni_note = None if bars else "không có bar 1 phút nào"
        if bars:
            ref_t = n
            if dt.time(11, 30) <= n.time() < (dt.datetime.combine(n.date(), dt.time(13)) + grace).time():
                ref_t = n.replace(hour=11, minute=30, second=0, microsecond=0)
            elif n.time() >= dt.time(14, 30):
                ref_t = n.replace(hour=14, minute=30, second=0, microsecond=0)
            if bars[-1][0] < ref_t - dt.timedelta(minutes=ipw.VNI_MAX_AGE_MIN):
                self.vni_note = f"bar cuối {bars[-1][0]:%H:%M} quá cũ"
                last = None
        return last, self._vni_ref

    def positions(self, account_id):
        return self.hold.get(account_id, {})

    def open_buys(self, account_id, sym):
        return []


class DryNotifier:
    def send(self, msg, channels=("discord",), subject=None, mention=False):
        return {ch: (True, "replay-dry") for ch in channels}


# ---------------------------------------------------------------- danh mục theo ngày
HL = pd.read_parquet(os.path.join(C, "holdings_ledger.parquet"))
HL["d"] = HL.date.dt.date
LV = pd.read_parquet(os.path.join(C, "holdings_live.parquet"))


def ledger_universe(day):
    g = HL[HL.d == day]
    hold, uni = {}, {}
    for _, r in g.iterrows():
        ref = raw_ref(r.ticker, day)
        if not ref or not r.weight or r.weight <= 0:
            continue
        qty = max(100, int(r.weight * NAV_SIM / ref // 100) * 100)
        hold[r.ticker] = {"qty": qty, "sellable": qty, "cost": None}
        uni[r.ticker] = {"holdings": {"HIST": {"qty": qty, "sellable": qty, "cost": None, "book": r.book,
                                               "account_id": "HIST", "no_auto_sell": None}},
                         "buys": [], "watch": False}
    return uni, {"HIST": hold}


def live_positions(day):
    out = {}
    accs = {a["label"]: a for a in ipw.load_accounts()}
    for lab, g in LV[LV.snap_date < day].groupby("account"):
        last = g[g.snap_date == g.snap_date.max()]
        aid = accs[lab]["account_id"] if lab in accs else lab
        out[aid] = {r.ticker: {"qty": int(r.qty), "sellable": int(r.qty), "cost": r.cost}
                    for _, r in last.iterrows()}
    return out


# ---------------------------------------------------------------- vòng replay
def minutes(day):
    t = dt.datetime.combine(day, dt.time(9, 0))          # driver dùng giờ ICT naive (vn_market.now_ict)
    end = dt.datetime.combine(day, dt.time(14, 59))
    while t <= end:
        yield t
        t += dt.timedelta(minutes=1)


def inject_verdicts(state_dir, day, now, scenario):
    if scenario == "NONE":
        return
    st = ipw._read_json(ipw.state_path(state_dir, day)) or {}
    for tk, c in (st.get("cases") or {}).items():
        if c.get("verdict"):
            continue
        t0 = ipw._p(c["t0"])
        lat = (E.INVEST_MIN_COMPRESSED if c.get("compressed") else E.INVEST_MIN) - 1
        if now >= t0 + dt.timedelta(minutes=lat):
            p = ipw.verdict_path(state_dir, t0.date(), tk)
            if not os.path.exists(p):
                ipw._atomic_json(p, {"ticker": tk, "label": scenario,
                                     "summary": f"REPLAY giả định phán quyết {scenario}", "at": ipw._iso(now)})


def run_day(day, scenario, state_dir, depth_mult, live):
    if live:
        pos = live_positions(day)
        market = HistMarket(day, pos, depth_mult)
        deps = ipw.Deps(market, DryNotifier(), state_dir, dispatch=None, messages=lambda: [],
                        bot_stop_path=FAKE_BOT_STOP, nav=lambda lab: (None, None), budget_s=1e9)
        deps.universe = None                     # build_universe THẬT (plan/book/excluded lịch sử)
    else:
        uni, pos = ledger_universe(day)
        market = HistMarket(day, pos, depth_mult)
        deps = ipw.Deps(market, DryNotifier(), state_dir, dispatch=None, messages=lambda: [],
                        accounts=[], bot_stop_path=FAKE_BOT_STOP, universe=uni,
                        nav=lambda lab: (None, None), budget_s=1e9)
    for now in minutes(day):
        market.set_now(now)
        ipw.run_tick(now, deps)
        inject_verdicts(state_dir, day, now, scenario)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="NONE", choices=("NONE", "BROKEN", "UNCLEAR"))
    ap.add_argument("--days", help="file danh sách ngày (mặc định: mọi ngày có dữ liệu)")
    ap.add_argument("--depth-mult", type=float, default=0.5)
    ap.add_argument("--out", default=None)
    ap.add_argument("--resume", action="store_true",
                    help="tiếp lượt dở: xoá ngày cuối (đang chạy dở) rồi chạy tiếp từ đó, giữ carryover")
    a = ap.parse_args()
    out = a.out or os.path.join(HERE, "runs", f"{a.scenario}_d{a.depth_mult}")
    resume_from = None
    if a.resume and os.path.isdir(out):
        done = sorted(f[6:16] for f in os.listdir(out) if f.startswith("state_") and f.endswith(".json"))
        if done:
            resume_from = dt.date.fromisoformat(done[-1])
            for f in (f"state_{done[-1]}.json", f"shadow_{done[-1]}.jsonl"):
                if os.path.exists(os.path.join(out, f)):
                    os.remove(os.path.join(out, f))
            vd = os.path.join(out, "verdicts")
            for f in (os.listdir(vd) if os.path.isdir(vd) else []):
                if f.startswith(done[-1]):
                    os.remove(os.path.join(vd, f))
    else:
        if os.path.exists(out):
            shutil.rmtree(out)
        os.makedirs(out)
    if a.days:
        days = [dt.date.fromisoformat(x.strip()) for x in open(a.days) if x.strip()]
    else:
        days = sorted(d for d in TDAYS if dt.date(2023, 9, 12) <= d <= LEDGER_END or d >= LIVE_1M_START)
        days += [d for d in (dt.date(2026, 10, 9),) if d not in days]
    t0 = time.time()
    for i, day in enumerate(sorted(days)):
        live = day >= LIVE_1M_START
        if not live and not (HL.d == day).any():
            continue
        if resume_from and day < resume_from:
            continue
        run_day(day, a.scenario, out, a.depth_mult, live)
        if i % 50 == 0:
            print(f"{a.scenario} {i}/{len(days)} {day} {time.time()-t0:.0f}s", flush=True)
    print("done", out, f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
