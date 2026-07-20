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

import csv
import datetime as dt
import json
import os
import re
import logging

import pandas as pd

from .config import WORKDIR, DATA_DIR
from .plan import TradePlan, PlannedOrder
from .vn_market import next_trading_day, round_lot, LOT

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------- DCF check (Pha 2, 2026-07-14)

_DCF_SENS_KEYS = ["r-1%", "r+1%", "g-2%", "g+2%"]

DCF_HISTORY_CSV = os.path.join(WORKDIR, "data", "dcf_lens_history.csv")
_DCF_HISTORY_COLS = ["logged_at", "as_of", "ticker", "source", "status",
                     "fair_value_ps", "price", "margin_of_safety", "robust", "conglomerate"]


def _dcf_is_conglomerate(ticker):
    """Cờ đa ngành/holding (chỉ để cảnh báo hiển thị). Fail-safe: import lỗi → False."""
    try:
        import sys as _sys
        if WORKDIR not in _sys.path:
            _sys.path.insert(0, WORKDIR)
        import dcf_valuation as _dcf
        return _dcf.is_conglomerate(ticker)
    except Exception:
        return False


def _dcf_check_for_order(ticker, price, asof):
    """Tính dcf_check dict cho 1 BUY order (non-financial, informational only).

    Đọc từ data/bq_cache/ticker_financial.parquet (local parquet, không gọi BQ live).
    Fail-safe: mọi lỗi đều trả NOT_COMPUTED với reason="dcf_error:...", KHÔNG raise.

    robust = True khi MoS KHÔNG đổi dấu qua toàn bộ sensitivity box
             (±1pp discount rate, ±2pp growth) — ngưỡng thống nhất theo Spyros/họp round-table.
    """
    try:
        import sys as _sys
        if WORKDIR not in _sys.path:
            _sys.path.insert(0, WORKDIR)
        import dcf_valuation as _dcf

        res = _dcf.fair_value(ticker, asof, price=price)

        if not res["ok"]:
            reason = res.get("reason", "unknown")
            if "financial-sector" in reason:
                nc_reason = "financial_sector_excluded"
            elif "positive FCFE" in reason or "FCFE <= 0" in reason:
                nc_reason = "fcfe_negative_buildout"
            elif "insufficient financial" in reason:
                nc_reason = "insufficient_history"
            else:
                nc_reason = reason[:80]
            return {"status": "NOT_COMPUTED", "margin_of_safety": None,
                    "robust": False, "reason": nc_reason,
                    "conglomerate": _dcf.is_conglomerate(ticker), "as_of": str(asof)[:10]}

        mos = res.get("margin_of_safety")
        status = "CHEAP" if (mos is not None and mos > 0) else "RICH"

        # robust: kiểm tra MoS không đổi dấu qua sensitivity box
        sens = res.get("sensitivity", {})
        robust = False
        if mos is not None and price and price > 0:
            mos_positive = mos > 0
            sens_signs = []
            for k in _DCF_SENS_KEYS:
                s = sens.get(k, {})
                fv_s = s.get("fv")
                if fv_s and fv_s > 0:
                    mos_s = (fv_s - price) / fv_s
                    sens_signs.append(mos_s > 0)
            robust = bool(sens_signs) and all(sg == mos_positive for sg in sens_signs)

        # fair_value_ps + price: HIỂN THỊ ONLY (user directive 2026-07-15) — neo số tuyệt đối
        # cho quyết định mua/bán + cho phép so giá dự báo vs giá thị trường sau này. KHÔNG
        # tham gia logic status/robust/gate nào. price = đúng giá MoS được tính trên đó, nên
        # dòng hiển thị luôn tự nhất quán mà không cần caller truyền lại giá.
        fv_ps = res.get("fair_value_ps")
        return {
            "status": status,
            "margin_of_safety": round(float(mos), 4) if mos is not None else None,
            "robust": robust,
            "fair_value_ps": round(float(fv_ps), 0) if fv_ps is not None else None,
            "price": round(float(price), 0) if price is not None else None,
            # đa ngành/holding: CẢNH BÁO hiển thị (user directive 2026-07-15) — DCF 1-dòng-tiền
            # có thể vô nghĩa với cấu trúc nhiều mảng. KHÔNG loại khỏi DCF, không đụng
            # status/robust/gate — y hệt fair_value_ps, thuần hiển thị.
            "conglomerate": _dcf.is_conglomerate(ticker),
            "as_of": str(asof)[:10],
        }

    except Exception as exc:
        _log.warning("DCF check lỗi cho %s: %s", ticker, exc)
        return {"status": "NOT_COMPUTED", "margin_of_safety": None,
                "robust": False, "reason": f"dcf_error: {str(exc)[:80]}",
                "conglomerate": _dcf_is_conglomerate(ticker), "as_of": str(asof)[:10]}

def _format_alt_lens(ticker):
    """Lăng kính định giá thay thế khi DCF NOT_COMPUTED. Fail-safe: import/lỗi → ""."""
    if not ticker:
        return ""
    try:
        import sys as _sys
        if WORKDIR not in _sys.path:
            _sys.path.insert(0, WORKDIR)
        from alt_valuation_lens import format_alt_lens
        return format_alt_lens(ticker)
    except Exception as exc:
        _log.warning("alt lens lỗi cho %s: %s", ticker, exc)
        return ""


def format_dcf_check(dcf, side="buy", has_override=False, ticker=None):
    """1 dòng hiển thị chuẩn cho dcf_check dict (Pha 2) — dùng chung mọi report echo
    (send_plan_report / eod_trading_report / paper sleeve). Informational only.
    Trả "" khi dcf rỗng/None — caller bỏ dòng, không hiện gì.

    ticker: khi có, NOT_COMPUTED được nối thêm LĂNG KÍNH ĐỊNH GIÁ THAY THẾ theo ngành
    (job Taylor_20260720_101638) thay vì để trống. Bỏ trống ticker → dòng cũ nguyên vẹn."""
    if not dcf or not isinstance(dcf, dict):
        return ""
    status = dcf.get("status")
    # đa ngành/holding: cảnh báo NGAY trên dòng có con số, không giấu trong footnote
    cong_s = " ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng" \
        if dcf.get("conglomerate") else ""
    if status == "NOT_COMPUTED":
        return (f"DCF: NOT_COMPUTED ({dcf.get('reason', '?')})"
                + _format_alt_lens(ticker or dcf.get("ticker")))
    mos = dcf.get("margin_of_safety")
    mos_s = f"{mos * 100:+.1f}%" if isinstance(mos, (int, float)) else "n/a"
    robust_s = "robust" if dcf.get("robust") else "không robust"
    icon = "🟢" if status == "CHEAP" else "🔴"
    # giá trị hợp lý tuyệt đối — bỏ qua khi dcf cũ (plan trước 2026-07-15) không có field
    fv, px = dcf.get("fair_value_ps"), dcf.get("price")
    fv_s = ""
    if isinstance(fv, (int, float)):
        fv_s = f"giá trị hợp lý ~{fv:,.0f}đ"
        if isinstance(px, (int, float)):
            fv_s += f" vs giá {px:,.0f}đ"
        fv_s += ", "
    out = f"{icon} DCF: {status} ({fv_s}MoS {mos_s}, {robust_s})"
    if status == "RICH" and dcf.get("robust") and str(side).lower() == "buy":
        out += " ⚠" if has_override else " ⚠ cần dcf_override_reason"
    return out + cong_s


def log_dcf_history(ticker, dcf, source, asof=None):
    """Ghi 1 dòng vào data/dcf_lens_history.csv (append-only) mỗi lần một report tính dcf_check.

    Mục đích (user directive 2026-07-15): tích luỹ fair_value_ps đã dự báo + giá thị trường lúc
    tính, để SAU NÀY đối chiếu với giá thật tại T+1M/3M/6M và đánh giá lăng kính DCF có hữu ích
    không. Đây thuần là BƯỚC GHI DỮ LIỆU — không phân tích, không quyết định gì.

    Chỉ gọi từ đường REPORT (send_plan_report / eod_trading_report / dc_book_waterfall_paper),
    KHÔNG từ V23Strategy: plan đã duyệt không được ghi ngược (rủi ro, theo dispatch).
    Fail-safe: mọi lỗi → bỏ qua im lặng (log warning), report không bao giờ vì dòng này mà hỏng.
    """
    try:
        if not dcf or not isinstance(dcf, dict):
            return
        row = {
            "logged_at": dt.datetime.now().isoformat(timespec="seconds"),
            "as_of": dcf.get("as_of") or (str(asof)[:10] if asof else ""),
            "ticker": ticker,
            "source": source,
            "status": dcf.get("status"),
            "fair_value_ps": dcf.get("fair_value_ps"),
            "price": dcf.get("price"),
            "margin_of_safety": dcf.get("margin_of_safety"),
            "robust": dcf.get("robust"),
            "conglomerate": dcf.get("conglomerate"),
        }
        os.makedirs(os.path.dirname(DCF_HISTORY_CSV), exist_ok=True)
        write_header = not os.path.exists(DCF_HISTORY_CSV)
        with open(DCF_HISTORY_CSV, "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=_DCF_HISTORY_COLS)
            if write_header:
                w.writeheader()
            w.writerow(row)
    except Exception as exc:
        _log.warning("log_dcf_history lỗi cho %s: %s", ticker, exc)


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
            recs = pd.DataFrame(columns=["book", "ticker", "play_type", "ta",
                                         "close_bq_stale_DO_NOT_USE_AS_REFPRICE",
                                         "sector", "weight_pct", "status"])
        paper = self._load_paper_book()
        if str(paper["ymd"])[:10] != str(signal_date)[:10]:
            notes.append(f"paper logs ymd={paper['ymd']} ≠ signal_date={signal_date} "
                         f"(pt_v22 chưa chạy hôm nay?)")

        # NAV thật & scale
        account_nav = broker.get_nav()
        real_pos = broker.get_positions()
        scale = account_nav / paper["nav"] if paper["nav"] > 0 else 0.0
        # Field CSV đổi tên 2026-07-11 (audit Taylor_20260711_031821 F2): giá BQ của ngày
        # signal — ở ĐÂY dùng hợp lệ vì chỉ là fallback bậc 2 SAU quote live trong _price()
        # (paper-mirror), không phải ref_price plan live. Fallback tên cũ cho CSV cũ.
        _cl = "close_bq_stale_DO_NOT_USE_AS_REFPRICE"
        recs_close = {str(r["ticker"]): (r.get(_cl) if pd.notna(r.get(_cl)) else r.get("close"))
                      for _, r in recs.iterrows()
                      if pd.notna(r.get(_cl)) or pd.notna(r.get("close"))}

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
                    dcf = _dcf_check_for_order(t, px, str(signal_date)[:10])
                    dcf_warn = (
                        dcf.get("status") == "RICH" and dcf.get("robust")
                    )
                    if dcf_warn:
                        notes.append(
                            f"⚠ DCF: {t} RICH & robust (MoS={dcf.get('margin_of_safety',0):.1%}) "
                            f"— ghi dcf_override_reason nếu vẫn mua"
                        )
                    orders.append(PlannedOrder(
                        id="", ticker=t, side="buy", qty=qty, ref_price=px,
                        book=book, play_type=play, dcf_check=dcf))
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
