#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đẳng thức tiền hằng tối — tự phát hiện dòng tiền NGOÀI (nạp/rút) CHƯA KHAI.

Bước 2/4 của chính sách "tài khoản = quỹ mở" (`kb/projects/fund-unit-performance-policy-20261010.md`).
Sổ `data/account_cash_flows.json` do NGƯỜI khai; file rỗng nghĩa là "chưa ai GHI", không phải "chưa
có nạp/rút", và cổng bước nhảy NAV 5%/15% không thấy khoản ≲50tr. Module này là lớp bắt chặt hơn:
với MỖI cửa sổ giữa hai lần chụp NAV liên tiếp, phần biến động tiền KHÔNG giải thích được bằng các
khoản nội bộ đọc được = dòng tiền ngoài NGHI NGỜ. Nó KHÔNG BAO GIỜ ghi vào sổ dòng tiền: vượt
ngưỡng mà sổ chưa có bản ghi khớp ⇒ "CHỜ KHAI" + cảnh báo nêu ngày, số tiền ước lượng và bằng chứng
đã đọc (§29); người khai kèm bằng chứng thì cảnh báo tự hết.

ĐẲNG THỨC (một cửa sổ = từ lần chụp của dòng nav_history trước tới lần chụp của dòng sau):

    ΔK = bán − mua − phí − thuế bán + cổ tức + lãi Trứng vàng + [dòng tiền ngoài] + nhiễu

  K = "tôi SỞ HỮU bao nhiêu tiền" (§25 — KHÔNG phải sức mua): `totalCash − totalDebt +
      egg.totalValue + off-book khai tay`, đọc từ CHÍNH các cột nav_history mà
      `daily_nav_snapshot.py` đã ghi từ balances của broker:
          K = cash + cum_dividend_excl − margin_debt + offbook_assets + egg_assets
      (`cash` của nav_history đã TRỪ cổ tức phải thu chưa qua ex-date; cộng lại để về totalCash).
      Vay/trả ký quỹ và chuyển tiền ↔ Trứng vàng triệt tiêu ngay trong K, không cần số hạng riêng.
  bán/mua  = Σ fillQuantity × averagePrice của các lệnh trong `dnse_raw_*.jsonl` (bản ghi `orders`
      / `place_order`, bản mới nhất mỗi lệnh) có lần cập nhật cuối nằm TRONG cửa sổ, cộng các
      fill broker xác nhận mà dnse_raw thiếu (`data/account_seed_capital.json` →
      `missing_fills_broker_confirmed`).
  phí/thuế = biểu phí thật `dnse_fee_rates.py` (0,097%/chiều + thuế bán 0,1%).
  cổ tức   = mức TĂNG của `cashDividendReceiving` giữa hai lần chụp (broker ghi GỘP vào totalCash
      lúc chốt quyền); mức GIẢM = đã chi trả ⇒ totalCash giảm đúng thuế TNCN 5% của phần đó.
  lãi Trứng vàng = số dư Trứng vàng đầu cửa sổ × `EGG_DAILY_RATE` × số ngày lịch.

KHÔNG mô hình hoá (nằm trong phần dư, và là lý do có ngưỡng): các khoản DNSE ghi có/ghi nợ DỒN
theo kỳ (lãi vay ký quỹ, phí ứng trước, lãi tiền gửi không kỳ hạn, phí lưu ký cuối tháng), khấu trừ
lãi khi rút Trứng vàng trước hạn, phí UPCOM thấp hơn HOSE 0,009pp, thuế bán cổ phiếu thưởng, cổ tức
chốt quyền và chi trả trong cùng một cửa sổ. Cửa sổ có dư nợ ký quỹ hoặc có rút Trứng vàng được
ghi chú kèm con số ước tính để người đọc tự đối chiếu.

KHÔNG phủ: chuyển CỔ PHIẾU vào/ra (không đi qua tiền) — lớp bắt vẫn là cổng bước nhảy NAV và cổng
phần dư số lượng của `daily_nav_snapshot.py`. Cửa sổ từ mốc khởi điểm tới dòng nav_history đầu tiên
không có số dư đầu ⇒ không kiểm được.

NGƯỠNG: xem `THRESHOLD_PCT` bên dưới (đo trên 135 cửa sổ thật của hai tài khoản).

MỞ CẢNH BÁO — hai cách, đều do NGƯỜI ghi vào `data/account_cash_flows.json` kèm bằng chứng:
  · đúng là nạp/rút ⇒ bản ghi deposit/withdraw có ngày + giờ rơi vào cửa sổ đó; phần dư sau khi
    trừ số tiền khai phải về dưới ngưỡng (khai thiếu/thừa thì vẫn cảnh báo phần còn lại);
  · không phải nạp/rút (lãi vay post dồn, lệnh đặt tay chưa có log…) ⇒ bản ghi `market_only`
    (amount_vnd = 0) có ngày thuộc cửa sổ = lời khẳng định có bằng chứng "ngày này KHÔNG có nạp/rút".

Dùng:
    python3 mike/bin/cash_identity.py --account SpaceX              # bảng phần dư + khoản chờ khai
    python3 mike/bin/cash_identity.py --account SpaceX --json
  rc: 0 = không có khoản chờ khai · 3 = CÓ khoản chờ khai · 1 = không chạy được.
Selfcheck: python3 mike/bin/cash_identity_selfcheck.py
"""
import argparse
import csv
import datetime
import json
import math
import os
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from account_cash_flows import SESSION_CLOSE_ICT, flow_moment, load_flows  # noqa: E402
from dnse_fee_rates import FEE_RATE_BUY_PCT, FEE_RATE_SELL_PCT, SELL_TAX_RATE  # noqa: E402
from wc_paths import find_wc_root  # noqa: E402

WC_ROOT = find_wc_root(__file__)
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
INCEPTION_PATH = os.path.join(WC_ROOT, "data", "account_inception.json")
SEED_PATH = os.path.join(WC_ROOT, "data", "account_seed_capital.json")
ICT = ZoneInfo("Asia/Ho_Chi_Minh")

# Lãi Trứng vàng theo NGÀY LỊCH. Đo trên 80 cửa sổ không có chuyển tiền ↔ Trứng vàng của cả hai
# tài khoản (2026-08-19 → 2026-10-12): Σ mức tăng / Σ (số dư × số ngày) = 0,023397%/ngày
# (≈8,54%/năm), từng cửa sổ nằm trong 0,02333%–0,02343%. DNSE đổi lãi suất ⇒ sai số = số dư ×
# chênh lãi × số ngày (500tr, lệch 1 điểm %/năm, 1 ngày ≈ 13,7 nghìn đồng ≈ 0,0014% NAV) — nhỏ hơn
# ngưỡng hai bậc; đo lại hằng số này khi phần dư của các ngày yên tĩnh lệch khỏi 0 một cách có hệ thống.
EGG_DAILY_RATE = 0.00023397
# Thuế TNCN cổ tức tiền mặt, DNSE khấu trừ lúc CHI TRẢ (phải thu ghi gộp) — đo: ZaloPay 2026-09-25
# chi trả 80.000.000 ⇒ totalCash giảm 4.002.556 (5% = 4.000.000).
DIVIDEND_TAX_RATE = 0.05
# Chỉ để GHI CHÚ lãi vay ước tính ở cửa sổ có dư nợ (không vào đẳng thức): 12,5%/năm theo user,
# chưa đối chiếu hợp đồng DNSE — cùng giả định với `reconcile_equity.py --margin-rate-annual`.
MARGIN_RATE_ANNUAL_NOTE = 0.125

# Rút Trứng vàng trước hạn bị khấu trừ lãi — chỉ để GHI CHÚ (không vào đẳng thức): đo 2 lần rút
# thật ngày 2026-09-17, cùng gửi 29 ngày: SpaceX mất 100.576 trên 49,95tr rút (0,2014%), ZaloPay
# 62.839 trên 31,22tr (0,2013%). Hai lần cùng thời gian gửi nên CHƯA phân biệt được "0,2% số rút"
# với "khấu trừ theo số ngày đã gửi" — chưa đối chiếu biểu phí DNSE.
EGG_WITHDRAW_COST_NOTE = 0.002013

# NGƯỠNG CHỜ KHAI: |phần dư chưa giải thích| > THRESHOLD_PCT % NAV đầu cửa sổ.
# Đo trên TOÀN BỘ lịch sử hai tài khoản tới 2026-10-12 — 135 cửa sổ (SpaceX 69, ZaloPay 66), sổ
# dòng tiền rỗng, |phần dư| theo % NAV: trung vị 0,0000 · p90 0,0066 · p95 0,0115 · p99 0,0543 ·
# max 0,1124; số cửa sổ vượt 0,005/0,01/0,02/0,05/0,1 = 18/11/4/2/1. 131/135 cửa sổ ≤ 0,0152%.
# Chọn 0,05 vì hai lý do độc lập: (1) đó là cận dưới của dải PHẢI SỬA theo chính sách (điểm 4:
# lệch < 0,05% NAV thì không đính chính) — ngưỡng cao hơn để lại một dải mù mà chính sách buộc
# sửa; (2) gấp 3,3 lần nhiễu thường nhật lớn nhất (0,0152%) nên không báo động vì phí/lãi lẻ.
# Hai cửa sổ lịch sử vượt ngưỡng đều của SpaceX và đều KHÔNG phải nạp/rút (dòng 07-02 chụp giữa
# loạt lệnh khớp sáng go-live; DNSE trừ dồn một khoản trên CẢ HAI tài khoản ngày 28/08) — chi
# tiết từng ngày + lệnh tái lập: `agents/Taylor/research/fund_cashflow_detect_20261012/`.
THRESHOLD_PCT = 0.05
WARNING_MARKER = "DÒNG TIỀN CHỜ KHAI"


class CashIdentityError(ValueError):
    """Không dựng được đẳng thức (thiếu/hỏng nguồn) — thông điệp trích đúng thứ đã đọc (§29)."""


def _num(text):
    """Ô số của nav_history: rỗng = 0 (cột chưa tồn tại ở giai đoạn đó), còn lại phải hữu hạn."""
    if text is None or str(text).strip() == "":
        return 0.0
    value = float(text)
    if not math.isfinite(value):
        raise ValueError(f"không phải số hữu hạn ({text!r})")
    return value


def _parse_ts(text):
    """Chuỗi ISO → datetime ICT naive (cùng hệ với `balance_ts` và `ts` của dnse_raw)."""
    stamp = datetime.datetime.fromisoformat(str(text))
    if stamp.tzinfo is not None:
        stamp = stamp.astimezone(ICT).replace(tzinfo=None)
    return stamp


def _parse_broker_utc(text):
    """`modifiedDate` của DNSE ("2026-07-01T03:14:59.722820993Z", UTC, 9 chữ số lẻ) → ICT naive."""
    raw = str(text).rstrip("Z")
    head, _, frac = raw.partition(".")
    stamp = datetime.datetime.fromisoformat(head).replace(
        microsecond=int((frac[:6] or "0").ljust(6, "0")), tzinfo=datetime.timezone.utc)
    return stamp.astimezone(ICT).replace(tzinfo=None)


def load_nav_rows(account, nav_dir=None):
    """nav_history của `account` → list dict tăng theo ngày, mỗi dòng có `k` (xem docstring module)
    và `snap` (lúc chụp số dư, ICT naive; `None` + `snap_error` nếu `balance_ts` thiếu/hỏng)."""
    path = os.path.join(nav_dir or EXEC_DIR, f"nav_history_{account}.csv")
    if not os.path.exists(path):
        raise CashIdentityError(f"thiếu {path}")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            if not rec.get("date") or not rec.get("nav"):
                continue
            try:
                row = {"date": datetime.date.fromisoformat(rec["date"]), "nav": _num(rec["nav"]),
                       "cash": _num(rec.get("cash")), "debt": _num(rec.get("margin_debt")),
                       "offbook": _num(rec.get("offbook_assets")),
                       "egg": _num(rec.get("egg_assets")),
                       "cum_div_excl": _num(rec.get("cum_dividend_excl"))}
            except ValueError as exc:
                raise CashIdentityError(f"{path}: dòng {rec.get('date')!r} không đọc được ({exc})") from exc
            # "Tôi SỞ HỮU bao nhiêu tiền" (§25): totalCash − totalDebt + egg + off-book khai tay.
            row["k"] = row["cash"] + row["cum_div_excl"] - row["debt"] + row["offbook"] + row["egg"]
            ts = rec.get("balance_ts")
            try:
                row["snap"], row["snap_error"] = (_parse_ts(ts), None) if ts else (None, f"balance_ts rỗng ({ts!r})")
            except ValueError as exc:
                row["snap"], row["snap_error"] = None, f"balance_ts không đọc được ({ts!r}: {exc})"
            rows.append(row)
    rows.sort(key=lambda r: r["date"])
    return rows


class RawLog:
    """Đọc `dnse_raw_<ngày>.jsonl` (file DÙNG CHUNG mọi tài khoản — §12) cho MỘT tài khoản.
    Mỗi file chỉ đọc một lần; bản ghi không thuộc `account_no` bị loại ngay ở dòng đầu."""

    KINDS = ("balances", "orders", "place_order", "positions")

    def __init__(self, account_no, raw_dir=None):
        self.account_no = str(account_no)
        self.raw_dir = raw_dir or EXEC_DIR
        self._days = {}

    def day(self, date):
        """`{"exists", "balances": [(ts, payload)], "positions": [(ts, [vị thế])], "orders":
        {mã lệnh: lệnh mới nhất}, "n_order_records"}` của một ngày."""
        if date in self._days:
            return self._days[date]
        out = {"exists": False, "balances": [], "positions": [], "orders": {}, "n_order_records": 0}
        path = os.path.join(self.raw_dir, f"dnse_raw_{date.isoformat()}.jsonl")
        if os.path.exists(path):
            out["exists"] = True
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if not any(f'"{kind}"' in line for kind in self.KINDS):
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    tag = rec.get("account_no")
                    if tag is not None and str(tag) != self.account_no:
                        continue                    # §12: bản ghi của tài khoản khác
                    kind, payload = rec.get("kind"), rec.get("payload") or {}
                    if kind == "balances":
                        if tag is None:
                            continue                # không gắn tài khoản ⇒ không đoán là của ai
                        out["balances"].append((rec.get("ts") or "", payload))
                    elif kind == "positions":
                        mine = [p for p in payload.get("positions") or []
                                if str(p.get("accountNo")) == self.account_no]
                        if tag is not None or mine:
                            out["positions"].append((rec.get("ts") or "", mine))
                    elif kind in ("orders", "place_order"):
                        orders = (payload.get("orders") or [] if kind == "orders"
                                  else [payload.get("resp") or {}])
                        seen = False
                        for o in orders:
                            # Lệnh mang accountNo riêng: bản ghi cũ (trước 2026-07-06) không gắn
                            # tài khoản ở ngoài nên phải lọc theo từng lệnh.
                            if o.get("id") is None or str(o.get("accountNo")) != self.account_no:
                                continue
                            out["orders"][o["id"]] = o
                            seen = True
                        out["n_order_records"] += 1 if (seen or tag is not None) else 0
        self._days[date] = out
        return out

    def receivable_at(self, snap):
        """`cashDividendReceiving` ở bản ghi balances chụp ĐÚNG lúc `snap` (chính bản ghi mà
        `daily_nav_snapshot.py` đã dùng); không có bản đúng giây thì bản mới nhất trước đó trong
        ngày. Không có bản nào ⇒ `None` (thiếu bằng chứng, KHÔNG coi là 0)."""
        best = None
        for ts, payload in self.day(snap.date())["balances"]:
            try:
                at = _parse_ts(ts)
            except ValueError:
                continue
            if at <= snap and (best is None or at >= best[0]):
                best = (at, payload)
        if best is None:
            return None
        value = (best[1].get("stock") or {}).get("cashDividendReceiving")
        return None if value is None else float(value)

    def quantities_at(self, snap):
        """{mã: KL đang giữ} ở bản ghi positions mới nhất không muộn hơn `snap` quá 10 phút
        (positions và balances được ghi cách nhau vài giây). Không có ⇒ `None`."""
        best = None
        limit = snap + datetime.timedelta(minutes=10)
        for ts, positions in self.day(snap.date())["positions"]:
            try:
                at = _parse_ts(ts)
            except ValueError:
                continue
            if at <= limit and (best is None or at >= best[0]):
                best = (at, positions)
        if best is None:
            return None
        out = {}
        for p in best[1]:
            qty = float(p.get("openQuantity") or 0)
            if qty:
                out[p.get("symbol")] = out.get(p.get("symbol"), 0.0) + qty
        return out

    def fills_between(self, snap0, snap1):
        """Lệnh có khớp với lần cập nhật cuối trong (snap0, snap1]. Trả list dict {moment, symbol,
        side ("buy"/"sell"), qty, value}. Lệnh không đọc được giờ ⇒ coi như khớp lúc đóng cửa của
        ngày file (ngày giao dịch của nó)."""
        out = []
        day = snap0.date()
        while day <= snap1.date():
            for o in self.day(day)["orders"].values():
                qty = float(o.get("fillQuantity") or 0)
                if qty <= 0:
                    continue
                try:
                    moment = _parse_broker_utc(o.get("modifiedDate") or o.get("createdDate"))
                except (TypeError, ValueError):
                    moment = datetime.datetime.combine(day, SESSION_CLOSE_ICT)
                if not snap0 < moment <= snap1:
                    continue
                side = "sell" if str(o.get("side") or "").upper().startswith("NS") else "buy"
                out.append({"moment": moment, "symbol": o.get("symbol"), "side": side, "qty": qty,
                            "value": qty * float(o.get("averagePrice") or o.get("price") or 0)})
            day += datetime.timedelta(days=1)
        return out


def load_account_no(account, inception_path=None):
    path = inception_path or INCEPTION_PATH
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if not isinstance(cfg, dict) or not isinstance(cfg.get(account), dict) \
            or not cfg[account].get("account_no"):
        raise CashIdentityError(f"{path}: không có account_no cho '{account}'")
    return str(cfg[account]["account_no"])


def load_confirmed_missing_fills(account, seed_path=None):
    """Fill broker xác nhận (email/sao kê) mà dnse_raw thiếu — cùng nguồn `reconcile_equity.py`
    dùng. Thiếu file/không có entry = không có fill nào như vậy."""
    path = seed_path or SEED_PATH
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    out = []
    for fx in ((cfg.get(account) or {}) if isinstance(cfg, dict) else {}).get(
            "missing_fills_broker_confirmed", []):
        day = datetime.date.fromisoformat(fx["date"])
        qty = float(fx["qty"])
        out.append({"moment": datetime.datetime.combine(day, SESSION_CLOSE_ICT),
                    "symbol": fx["ticker"], "side": "sell" if fx["side"] == "sell" else "buy",
                    "qty": qty, "value": qty * float(fx["price"])})
    return out


def build_windows(rows, raw, flows, extra_fills=(), threshold_pct=THRESHOLD_PCT):
    """Đẳng thức tiền cho từng cặp dòng nav_history liên tiếp. Trả list dict, mỗi cửa sổ một dòng:
    date0/date1, snap0/snap1, nav0, delta_k, sell, buy, n_fills, fees, dividend, egg_interest,
    residual (= delta_k − các khoản nội bộ), declared (nạp/rút đã khai rơi vào cửa sổ),
    unexplained (= residual − declared), pct_nav, acked (có bản ghi market_only), suspect, notes.
    Cửa sổ có đầu mút không rõ lúc chụp ⇒ `checkable=False` kèm lý do, không tính số nào."""
    money = [(flow_moment(f)[0], f) for f in flows if f["kind"] != "market_only"]
    acks = [f for f in flows if f["kind"] == "market_only"]
    windows = []
    for prev, cur in zip(rows, rows[1:]):
        win = {"date0": prev["date"], "date1": cur["date"], "snap0": prev["snap"],
               "snap1": cur["snap"], "nav0": prev["nav"], "checkable": True, "notes": []}
        windows.append(win)
        bad = [f"dòng {r['date']}: {r['snap_error']}" for r in (prev, cur) if r["snap"] is None]
        if not bad and cur["snap"] <= prev["snap"]:
            bad = [f"dòng {cur['date']} chụp lúc {cur['snap']}, không sau dòng {prev['date']} "
                   f"({prev['snap']})"]
        if not bad and prev["nav"] <= 0:
            bad = [f"NAV dòng {prev['date']} = {prev['nav']:,.0f}"]
        if bad:
            win.update(checkable=False, suspect=False, reason="; ".join(bad))
            continue
        snap0, snap1 = prev["snap"], cur["snap"]
        fills = raw.fills_between(snap0, snap1) + [
            fx for fx in extra_fills if snap0 < fx["moment"] <= snap1]
        sell = sum(fx["value"] for fx in fills if fx["side"] == "sell")
        buy = sum(fx["value"] for fx in fills if fx["side"] == "buy")
        fees = (buy * FEE_RATE_BUY_PCT / 100 + sell * FEE_RATE_SELL_PCT / 100
                + sell * SELL_TAX_RATE)
        recv0, recv1 = raw.receivable_at(snap0), raw.receivable_at(snap1)
        if recv0 is None or recv1 is None:
            dividend = 0.0
            win["notes"].append(
                "không đọc được cashDividendReceiving ở "
                + " và ".join(f"lần chụp {s}" for s, r in ((snap0, recv0), (snap1, recv1)) if r is None)
                + " (dnse_raw không có bản ghi balances gắn tài khoản này) ⇒ cổ tức tính 0")
        else:
            delta = recv1 - recv0
            dividend = delta if delta >= 0 else delta * DIVIDEND_TAX_RATE
        days = (snap1.date() - snap0.date()).days
        egg_interest = prev["egg"] * EGG_DAILY_RATE * days
        delta_k = cur["k"] - prev["k"]
        residual = delta_k - (sell - buy - fees + dividend + egg_interest)
        declared = [f for at, f in money if snap0 < at <= snap1]
        declared_vnd = sum(f["amount_vnd"] for f in declared)
        unexplained = residual - declared_vnd
        acked = [f for f in acks if prev["date"] < f["date"] <= cur["date"]]
        win.update(delta_k=delta_k, sell=sell, buy=buy, n_fills=len(fills), fees=fees,
                   dividend=dividend, egg_interest=egg_interest, residual=residual,
                   declared=declared_vnd, declared_flows=declared, unexplained=unexplained,
                   pct_nav=unexplained / prev["nav"] * 100, acked=acked)
        win["suspect"] = abs(win["pct_nav"]) > threshold_pct and not acked
        debt = max(prev["debt"], cur["debt"])
        if debt > 0:
            win["notes"].append(
                f"có dư nợ ký quỹ ({prev['debt']:,.0f} → {cur['debt']:,.0f}); lãi vay ước "
                f"{debt * MARGIN_RATE_ANNUAL_NOTE / 365 * max(days, 1):,.0f} VND cho "
                f"{max(days, 1)} ngày trên dư nợ {debt:,.0f} KHÔNG nằm trong đẳng thức (DNSE post "
                f"dồn, không theo ngày)")
        egg_out = prev["egg"] + egg_interest - cur["egg"]
        if egg_out > prev["egg"] * EGG_DAILY_RATE:      # nhỏ hơn một ngày lãi = sai số lãi suất
            win["notes"].append(
                f"Trứng vàng giảm {egg_out:,.0f} VND trong cửa sổ; rút trước hạn bị khấu trừ lãi — "
                f"lần đo 2026-09-17 mất {EGG_WITHDRAW_COST_NOTE * 100:.4f}% số rút, tức cỡ "
                f"{egg_out * EGG_WITHDRAW_COST_NOTE:,.0f} VND ở đây (ước tính, KHÔNG nằm trong đẳng thức)")
        if prev["offbook"] or cur["offbook"]:
            win["notes"].append(
                f"có tài sản off-book khai tay ({prev['offbook']:,.0f} → {cur['offbook']:,.0f}) — "
                f"số do người báo, không đọc được từ broker")
        if win["suspect"]:
            win["notes"].extend(_fill_evidence(raw, snap0, snap1, fills))
    return windows


def _fill_evidence(raw, snap0, snap1, fills):
    """Bằng chứng phân biệt "lệnh khớp chưa có log" với "nạp/rút": dnse_raw có bản ghi orders của
    tài khoản trong cửa sổ không, và số lượng vị thế đổi có khớp với lệnh đã đọc không."""
    notes = []
    day, silent = snap0.date(), []
    while day <= snap1.date():
        info = raw.day(day)
        if day.weekday() < 5 and not info["n_order_records"]:
            silent.append(f"{day}" + ("" if info["exists"] else " (không có file)"))
        day += datetime.timedelta(days=1)
    if silent:
        notes.append("dnse_raw KHÔNG có bản ghi orders nào của tài khoản các ngày "
                     + ", ".join(silent) + " ⇒ lệnh đặt ngoài bot những ngày đó không được thấy ở đây")
    q0, q1 = raw.quantities_at(snap0), raw.quantities_at(snap1)
    if q0 is None or q1 is None:
        notes.append("không đọc được vị thế ở "
                     + " và ".join(f"lần chụp {s}" for s, q in ((snap0, q0), (snap1, q1)) if q is None)
                     + " ⇒ không đối chiếu được số lượng với lệnh khớp")
        return notes
    net = {}
    for fx in fills:
        net[fx["symbol"]] = net.get(fx["symbol"], 0.0) + (fx["qty"] if fx["side"] == "buy" else -fx["qty"])
    gaps = []
    for symbol in sorted(set(q0) | set(q1) | set(net)):
        gap = q1.get(symbol, 0.0) - q0.get(symbol, 0.0) - net.get(symbol, 0.0)
        if abs(gap) > 1e-6:
            gaps.append(f"{symbol} {gap:+,.0f}")
    if gaps:
        notes.append("số lượng vị thế đổi KHÔNG khớp lệnh đã đọc: " + ", ".join(gaps)
                     + " ⇒ phần dư có thể là lệnh khớp chưa có log hoặc cổ phiếu thưởng/chuyển "
                       "khoản chứng khoán, chưa chắc là nạp/rút")
    else:
        notes.append("số lượng vị thế khớp đúng với lệnh đã đọc ⇒ phần dư KHÔNG đến từ lệnh khớp "
                     "thiếu log")
    return notes


def check_account(account, asof=None, nav_dir=None, raw_dir=None, flows_path=None,
                  inception_path=None, seed_path=None, threshold_pct=THRESHOLD_PCT, today=None):
    """Dựng đẳng thức tiền của `account` trên toàn bộ nav_history tới `asof` (date, gồm cả ngày đó).
    Trả `{"account", "threshold_pct", "windows", "suspects", "uncheckable"}`."""
    rows = load_nav_rows(account, nav_dir)
    if asof is not None:
        rows = [r for r in rows if r["date"] <= asof]
    raw = RawLog(load_account_no(account, inception_path), raw_dir)
    flows = load_flows(account, flows_path=flows_path, require_file=True, today=today)
    windows = build_windows(rows, raw, flows, load_confirmed_missing_fills(account, seed_path),
                            threshold_pct)
    return {"account": account, "threshold_pct": threshold_pct, "windows": windows,
            "suspects": [w for w in windows if w["suspect"]],
            "uncheckable": [w for w in windows if not w["checkable"]]}


def suspect_line(account, win):
    """Một dòng cảnh báo tự đủ nghĩa cho một cửa sổ chờ khai: ngày, số tiền ước lượng, bằng chứng."""
    direction = "NẠP vào" if win["unexplained"] > 0 else "RÚT ra"
    declared = (f"; đã trừ {win['declared']:+,.0f} VND dòng tiền đã khai trong cửa sổ"
                if win["declared"] else "")
    return (f"⚠️ {WARNING_MARKER} ({account}): giữa lần chụp NAV {win['date0']} "
            f"({win['snap0']:%d/%m %H:%M}) và {win['date1']} ({win['snap1']:%d/%m %H:%M}) có "
            f"{abs(win['unexplained']):,.0f} VND ({win['pct_nav']:+.3f}% NAV) nghi {direction} mà "
            f"sổ dòng tiền chưa có bản ghi khớp. Đã đọc: tiền sở hữu đổi {win['delta_k']:+,.0f}; "
            f"{win['n_fills']} lệnh khớp (bán {win['sell']:,.0f}, mua {win['buy']:,.0f}, phí+thuế "
            f"{win['fees']:,.0f}); cổ tức {win['dividend']:+,.0f}; lãi Trứng vàng "
            f"{win['egg_interest']:+,.0f}{declared}"
            + "".join(f"; {note}" for note in win["notes"])
            + ". Tỉ suất các kỳ chứa ngày này CHƯA khử khoản đó — khai vào "
              "data/account_cash_flows.json kèm bằng chứng (deposit/withdraw có giờ; hoặc "
              "market_only nếu đã xác minh không phải nạp/rút).")


def warning_lines(account, asof=None, **paths):
    """Các dòng cảnh báo cho mọi consumer hiển thị (dòng 💰 NAV, CLI tỉ suất, cổng giao báo cáo).
    Không dựng được đẳng thức ⇒ MỘT dòng nói đúng lỗi đã gặp — không im lặng, không đoán."""
    try:
        result = check_account(account, asof=asof, **paths)
    except Exception as exc:                # noqa: BLE001 — đường hiển thị: lỗi phải hiện ra, không được làm gãy caller
        return [f"⚠️ Đẳng thức tiền ({account}) KHÔNG chạy được nên chưa kiểm được dòng tiền chưa "
                f"khai — {type(exc).__name__}: {exc}"]
    lines = [suspect_line(account, w) for w in result["suspects"]]
    for w in result["uncheckable"]:
        lines.append(f"⚠️ Đẳng thức tiền ({account}) không kiểm được cửa sổ {w['date0']} → "
                     f"{w['date1']}: {w['reason']}")
    return lines


def _table(result):
    head = (f"{'cửa sổ':<23}{'ΔK':>15}{'bán−mua':>15}{'phí+thuế':>11}{'cổ tức':>12}"
            f"{'lãi egg':>10}{'đã khai':>13}{'phần dư':>13}{'%NAV':>9}")
    lines = [head]
    for w in result["windows"]:
        label = f"{w['date0']} → {w['date1']:%m-%d}"
        if not w["checkable"]:
            lines.append(f"{label:<23}KHÔNG KIỂM ĐƯỢC — {w['reason']}")
            continue
        flag = "  ◀ CHỜ KHAI" if w["suspect"] else ("  (đã khẳng định không nạp/rút)" if w["acked"]
                                                   and abs(w["pct_nav"]) > result["threshold_pct"] else "")
        lines.append(f"{label:<23}{w['delta_k']:>15,.0f}{w['sell'] - w['buy']:>15,.0f}"
                     f"{w['fees']:>11,.0f}{w['dividend']:>12,.0f}{w['egg_interest']:>10,.0f}"
                     f"{w['declared']:>13,.0f}{w['unexplained']:>13,.0f}{w['pct_nav']:>9.4f}{flag}")
    return "\n".join(lines)


def _jsonable(result):
    def clean(win):
        out = {}
        for key, value in win.items():
            if isinstance(value, (datetime.date, datetime.datetime)):
                out[key] = value.isoformat()
            elif key in ("declared_flows", "acked"):
                out[key] = [dict(f, date=f["date"].isoformat()) for f in value]
            else:
                out[key] = value
        return out
    return {"account": result["account"], "threshold_pct": result["threshold_pct"],
            "n_windows": len(result["windows"]),
            "suspects": [clean(w) for w in result["suspects"]],
            "uncheckable": [clean(w) for w in result["uncheckable"]],
            "windows": [clean(w) for w in result["windows"]]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--account", required=True)
    ap.add_argument("--asof", help="YYYY-MM-DD: chỉ xét nav_history tới ngày này")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--nav-dir")
    ap.add_argument("--raw-dir")
    ap.add_argument("--flows-path")
    ap.add_argument("--threshold-pct", type=float, default=THRESHOLD_PCT)
    args = ap.parse_args()
    try:
        result = check_account(
            args.account, asof=datetime.date.fromisoformat(args.asof) if args.asof else None,
            nav_dir=args.nav_dir, raw_dir=args.raw_dir, flows_path=args.flows_path,
            threshold_pct=args.threshold_pct)
    except (ValueError, OSError, KeyError) as exc:
        print(f"cash_identity: KHÔNG chạy được — {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(_jsonable(result), ensure_ascii=False, indent=2))
    else:
        print(f"== Đẳng thức tiền {args.account} — ngưỡng ±{result['threshold_pct']}% NAV, "
              f"{len(result['windows'])} cửa sổ")
        print(_table(result))
        for w in result["suspects"]:
            print(suspect_line(args.account, w))
        for w in result["uncheckable"]:
            print(f"⚠️ không kiểm được {w['date0']} → {w['date1']}: {w['reason']}")
    return 3 if result["suspects"] else 0


if __name__ == "__main__":
    sys.exit(main())
