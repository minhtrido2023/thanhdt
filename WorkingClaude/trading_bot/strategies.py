# -*- coding: utf-8 -*-
"""Strategy layer — mỗi version chiến lược là 1 class, đăng ký trong REGISTRY.

Nâng cấp chiến lược = thêm class mới (vd V24Strategy) + đăng ký + đổi
config "strategy". Plan cũ/journal cũ không bị ảnh hưởng.

V23Strategy (production): MIRROR paper book V2.3 sang tài khoản thật, scale theo
NAV. Target = vị thế paper hiện có (pt_v22_dt5g_open_positions) ∪ khuyến nghị
vào lệnh T+1 (golive_v23_recommendations) ∪ phần park ETF. Lệnh = chênh lệch
target − danh mục thật. Exit của paper ngày T+1 sẽ được sync ở plan T+2
(trễ 1 phiên — chấp nhận ở v1, vì exit V2.3 là hold-expiry/stop không gấp).
"""

import datetime as dt
import json
import os
import re

import pandas as pd

from .config import WORKDIR, DATA_DIR
from .plan import TradePlan, PlannedOrder
from .vn_market import next_trading_day, round_lot, LOT

GOLIVE_OUT = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "out")
STATUS_FILE = os.path.join(DATA_DIR, "golive_v23_status.json")
PT_LOGS = os.path.join(DATA_DIR, "pt_v22_dt5g_logs.csv")
PT_POSITIONS = os.path.join(DATA_DIR, "pt_v22_dt5g_open_positions.csv")
PT_TRANSACTIONS = os.path.join(DATA_DIR, "pt_v22_dt5g_transactions.csv")


class StrategyBase:
    name = "base"
    version = "0"

    def build_plan(self, cfg, broker, signal_date=None):
        """→ TradePlan (chưa save)."""
        raise NotImplementedError


class V23Strategy(StrategyBase):
    name = "v23"
    version = "2.3"

    # ----- data loading -----

    def _load_status(self):
        with open(STATUS_FILE, encoding="utf-8") as f:
            return json.load(f)

    def _load_recs(self, signal_date):
        path = os.path.join(GOLIVE_OUT, f"golive_v23_recommendations_{signal_date}.csv")
        if not os.path.exists(path):
            return None, path
        return pd.read_csv(path), path

    def _load_paper_book(self):
        logs = pd.read_csv(PT_LOGS)
        last = logs.iloc[-1]
        nav = float(last["nav"])
        bal_nav = float(last["BAL_cash"] + last["BAL_stocks"] + last["BAL_etf"])
        lag_nav = float(last["SECOND_cash"] + last["SECOND_stocks"] + last["SECOND_etf"])
        etf_value = float(last["BAL_etf"] + last["SECOND_etf"])
        pos = pd.DataFrame(columns=["ticker", "shares"])
        if os.path.exists(PT_POSITIONS):
            p = pd.read_csv(PT_POSITIONS)
            if len(p):
                pos = p.groupby("ticker", as_index=False)["shares"].sum()
        return {"nav": nav, "bal_nav": bal_nav, "lag_nav": lag_nav,
                "etf_value": etf_value, "ymd": str(last["ymd"]), "positions": pos}

    def _last_tx_price(self, ticker):
        """Giá gần nhất của ticker trong transactions paper (fallback cuối)."""
        if not os.path.exists(PT_TRANSACTIONS):
            return None
        try:
            tx = pd.read_csv(PT_TRANSACTIONS)
            rows = tx[tx["ticker"] == ticker]
            if len(rows):
                return float(rows.iloc[-1]["adj_price"])
        except Exception:
            pass
        return None

    def _price(self, broker, ticker, recs_close=None, notes=None):
        """Chuỗi fallback giá: quote PHS → close trong recs → transactions paper."""
        q = broker.get_quote(ticker)
        if q is not None and q.ok():
            return q.last or q.ref
        if recs_close and recs_close > 0:
            return float(recs_close)
        p = self._last_tx_price(ticker)
        if p:
            return p
        if notes is not None:
            notes.append(f"không có giá cho {ticker} — bỏ qua")
        return None

    # ----- plan building -----

    def build_plan(self, cfg, broker, signal_date=None):
        notes = []
        status = self._load_status()
        signal_date = signal_date or status.get("signal_date") or status.get("date")
        recs, recs_path = self._load_recs(signal_date)
        if recs is None:
            notes.append(f"KHÔNG thấy file khuyến nghị {recs_path} — plan chỉ sync mirror")
            recs = pd.DataFrame(columns=["book", "ticker", "play_type", "ta", "close",
                                         "sector", "weight_pct", "status"])
        paper = self._load_paper_book()
        if str(paper["ymd"])[:10] != str(signal_date)[:10]:
            notes.append(f"paper logs ymd={paper['ymd']} ≠ signal_date={signal_date} "
                         f"(pt_v22 chưa chạy hôm nay?)")

        # NAV thật & scale
        account_nav = broker.get_nav()
        real_pos = broker.get_positions()
        scale = account_nav / paper["nav"] if paper["nav"] > 0 else 0.0
        recs_close = {str(r["ticker"]): r.get("close")
                      for _, r in recs.iterrows() if pd.notna(r.get("close"))}

        # ---------- target portfolio (số CP, đã scale) ----------
        target = {}      # ticker -> qty
        ref_px = {}      # ticker -> giá dùng để tính/đặt lệnh
        meta = {}        # ticker -> (book, play_type)

        # 1) mirror vị thế paper hiện có
        for _, r in paper["positions"].iterrows():
            t = str(r["ticker"])
            px = self._price(broker, t, recs_close.get(t), notes)
            if px is None:
                continue
            target[t] = target.get(t, 0) + float(r["shares"]) * scale
            ref_px[t] = px
            meta.setdefault(t, ("MIRROR", ""))

        # 2) khuyến nghị vào lệnh T+1 (BAL FULL/HALF, LAG sắp đến hạn, CAPIT nếu fired)
        for _, r in recs.iterrows():
            t, book = str(r["ticker"]), str(r["book"])
            st = str(r.get("status", ""))
            w = float(r.get("weight_pct", 0) or 0) / 100.0
            if w <= 0:
                continue
            if book == "BAL":
                if st not in ("FULL", "HALF_SIZE"):
                    continue
                book_nav = paper["bal_nav"] * scale
                if st == "HALF_SIZE":
                    w *= 0.5
            elif book == "LAG":
                m = re.search(r"T\+(\d+)", st)
                if not (m and int(m.group(1)) <= 1):
                    continue           # chỉ vào lệnh LAG đến hạn phiên tới
                book_nav = paper["lag_nav"] * scale
            elif book == "CAPIT":
                if not status.get("capit_fired"):
                    continue
                book_nav = paper["lag_nav"] * scale * float(status.get("capit_size", 0))
                w = w if w > 0 else 1.0 / max(1, int(status.get("n_capit_basket", 1)))
            else:
                continue
            px = self._price(broker, t, recs_close.get(t), notes)
            if px is None:
                continue
            qty_rec = book_nav * w / px
            # tránh double-count khi mã vừa có trong paper positions vừa trong recs
            target[t] = max(target.get(t, 0), qty_rec)
            ref_px[t] = px
            meta[t] = (book, str(r.get("play_type", "")))

        # 3) ETF park (giá trị ETF của 2 book trong logs)
        etf = cfg["etf_symbol"]
        if cfg["include_etf_park"] and etf not in target:
            etf_val = paper["etf_value"] * scale
            if etf_val > cfg["min_order_value"]:
                px = self._price(broker, etf, None, notes)
                if px:
                    target[etf] = etf_val / px
                    ref_px[etf] = px
                    meta[etf] = ("ETF", "ETF_PARK")

        # ---------- diff target vs danh mục thật → orders ----------
        orders = []
        tol = cfg["qty_tolerance_pct"]
        all_syms = sorted(set(target) | set(real_pos))
        for t in all_syms:
            tgt = target.get(t, 0.0)
            have = real_pos.get(t, {}).get("total", 0)
            sellable = real_pos.get(t, {}).get("sellable", have)
            px = ref_px.get(t) or self._price(broker, t, recs_close.get(t), notes)
            if px is None:
                continue
            diff = tgt - have
            if tgt > 0 and abs(diff) < tol * tgt:
                continue
            if abs(diff) * px < cfg["min_order_value"]:
                continue
            book, play = meta.get(t, ("SYNC", ""))
            if diff > 0:
                qty = round_lot(diff)
                if qty >= LOT:
                    orders.append(PlannedOrder(
                        id="", ticker=t, side="buy", qty=qty, ref_price=px,
                        book=book, play_type=play))
            else:
                qty = min(round_lot(-diff), sellable)
                if qty >= LOT:
                    note = "" if tgt > 0 else "không còn trong book paper"
                    orders.append(PlannedOrder(
                        id="", ticker=t, side="sell", qty=qty, ref_price=px,
                        book=book, play_type=play, urgency="high", note=note))

        # priority: sell trước (giải phóng tiền), buy theo giá trị giảm dần
        sells = sorted([o for o in orders if o.side == "sell"],
                       key=lambda o: -o.value)
        buys = sorted([o for o in orders if o.side == "buy"],
                      key=lambda o: -o.value)
        for i, o in enumerate(sells):
            o.priority, o.id = 1, f"SELL-{o.ticker}-{i+1:02d}"
        for i, o in enumerate(buys):
            o.priority, o.id = 2 + i, f"BUY-{o.ticker}-{i+1:02d}"
        orders = sells + buys

        if len(orders) > cfg["max_orders_per_day"]:
            notes.append(f"cắt bớt {len(orders) - cfg['max_orders_per_day']} lệnh "
                         f"(max_orders_per_day={cfg['max_orders_per_day']})")
            orders = orders[:cfg["max_orders_per_day"]]
        gross = sum(o.value for o in orders)
        if gross > cfg["max_daily_gross_value"]:
            notes.append(f"⚠ gross {gross/1e9:.1f}B vượt trần "
                         f"{cfg['max_daily_gross_value']/1e9:.1f}B — KIỂM TRA plan!")

        sig = dt.datetime.strptime(str(signal_date)[:10], "%Y-%m-%d").date()
        return TradePlan(
            plan_date=next_trading_day(sig).strftime("%Y-%m-%d"),
            signal_date=str(signal_date)[:10],
            strategy=self.name, strategy_version=self.version,
            state=int(status.get("state", 0)),
            state_name=str(status.get("state_name", "?")),
            nav_basis={"account_nav": round(account_nav),
                       "paper_nav": round(paper["nav"]),
                       "scale": scale},
            orders=orders, notes=notes)


REGISTRY = {
    V23Strategy.name: V23Strategy,
}


def get_strategy(name):
    if name not in REGISTRY:
        raise KeyError(f"strategy '{name}' chưa đăng ký — có: {sorted(REGISTRY)}")
    return REGISTRY[name]()
