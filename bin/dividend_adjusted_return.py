#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tỉ suất lợi nhuận ĐÃ ĐIỀU CHỈNH CỔ TỨC cho một vị thế — BẮT BUỘC dùng trong mọi báo cáo.

VÌ SAO CẦN FILE NÀY
-------------------
`tav2_bq.ticker` có 2 cột giá:
  * `Price` — giá THÔ, đúng giá thật trên bảng điện (báo cáo mark-to-market dùng cột này).
  * `Close` — giá ĐÃ ĐIỀU CHỈNH cổ tức/chia tách, hồi tố từ HÔM NAY về quá khứ.

Tỉ số `Close/Price` là HẰNG SỐ giữa hai ex-date liên tiếp và NHẢY VỀ 1.0 đúng ngày ex-date của
sự kiện gần nhất. Đây là phép NHÂN, không phải phép trừ — hiệu `Close - Price` biến thiên theo
mức giá nên KHÔNG dùng hiệu số để suy ra cổ tức (ví dụ SAB: hiệu chạy −3.110 → −3.000 trong khi
cổ tức thật là đúng 3.000đ/cp).

    div_per_share = P_last_cum × (1 − ratio_last_cum / ratio_ex)

Hai lỗi thật đã xảy ra trong báo cáo tháng 7/2026 (xem `mike/kb/data_registry/price-volume/
ticker_close_vs_price_dividend_adj.md`):
  1. Lấy `(Price_cuối kỳ − giá vốn)/giá vốn` mà QUÊN cộng cổ tức đã nhận → % lãi/lỗ THẤP HƠN
     thực tế (NCT báo −11,6% trong khi thật là −3,1%).
  2. Lấy `Close` (đã điều chỉnh) trừ giá vốn THÔ → phạt cổ tức HAI LẦN.

QUY TẮC
-------
* Giá vốn (`cost`) là giá khớp THẬT đã trả — số THÔ, chưa điều chỉnh.
* Giá cuối kỳ dùng `Price` (thô) — đúng thứ nhà đầu tư thấy trên bảng điện.
* Cổ tức tiền mặt CỘNG VÀO TỬ SỐ, mẫu số giữ nguyên giá vốn gốc:
      total_return = (P_end + D − cost) / cost
  KHÔNG dùng `Close_end/Close_start` để so với giá vốn: chuỗi `Close` được hồi tố từ vintage
  HÔM NAY nên mức giá của nó không cùng hệ quy chiếu với một giá khớp thô. (`Close/Close` chỉ
  đúng khi so hai NGÀY với nhau — ví dụ "mã X tăng bao nhiêu trong tuần" — không phải để so với
  giá vốn.)

⚠️ CỔ TỨC TIỀN MẶT vs CHIA TÁCH/CỔ PHIẾU THƯỞNG: tỉ số `Close/Price` KHÔNG phân biệt được hai
loại. Chia tách làm TĂNG SỐ LƯỢNG cổ phiếu (giá trị không đổi, không có tiền về); cổ tức tiền mặt
giữ nguyên số lượng và trả tiền. Vì vậy mọi sự kiện phát hiện từ BQ mặc định là `UNVERIFIED`, và
`verify_with_broker()` mới nâng lên `CASH_CONFIRMED` (khớp `cashDividendReceiving` của DNSE) hoặc
hạ xuống `STOCK_SUSPECTED` (số lượng cổ phiếu đổi tại ex-date). KHÔNG đưa số `UNVERIFIED` vào báo
cáo gửi nhà đầu tư.

CLI
---
    python3 mike/bin/dividend_adjusted_return.py --ticker NCT --from 2026-07-21 --to 2026-07-31 \
        --cost 94360 --qty 500 --account SpaceX
    python3 mike/bin/dividend_adjusted_return.py --selfcheck
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field

BQ_PROJECT = "lithe-record-440915-m9"
EXEC_LOG_DIR = "/home/trido/thanhdt/WorkingClaude/data/execution_logs"

# Nhiễu làm tròn: `Close` được làm tròn tới 10 VND nên tỉ số dao động ~10/Price.
# Ngưỡng 0,3% đủ rộng để bỏ qua nhiễu, đủ hẹp để bắt cổ tức nhỏ nhất đã gặp (450đ/34.000 = 1,3%).
RATIO_JUMP_MIN = 0.003


@dataclass
class Adjustment:
    """Một sự kiện điều chỉnh giá (cổ tức tiền mặt HOẶC chia tách — chưa phân biệt)."""

    ticker: str
    ex_date: str
    last_cum_date: str
    last_cum_price: float
    per_share: float
    kind: str = "UNVERIFIED"  # UNVERIFIED | CASH_CONFIRMED | STOCK_SUSPECTED
    note: str = ""


@dataclass
class PositionReturn:
    ticker: str
    qty: int
    cost_per_share: float
    end_price: float
    dividend_per_share: float
    adjustments: list = field(default_factory=list)

    @property
    def cost_total(self) -> float:
        return self.qty * self.cost_per_share

    @property
    def pl_price(self) -> float:
        """Lãi/lỗ do GIÁ (chưa gồm cổ tức) — vẫn là 'lãi/lỗ chưa thực hiện' đúng nghĩa."""
        return self.qty * (self.end_price - self.cost_per_share)

    @property
    def dividend_total(self) -> float:
        return self.qty * self.dividend_per_share

    @property
    def pl_total(self) -> float:
        return self.pl_price + self.dividend_total

    @property
    def pct_price_only(self) -> float:
        return self.pl_price / self.cost_total * 100.0

    @property
    def pct_total_return(self) -> float:
        return self.pl_total / self.cost_total * 100.0

    @property
    def unverified(self) -> list:
        return [a for a in self.adjustments if a.kind != "CASH_CONFIRMED"]


def _bq(sql: str) -> list:
    """Chạy BQ, trả về list[dict]. Không dùng cache env (§11) — đây là tra cứu lịch sử thuần."""
    out = subprocess.run(
        ["bq", "query", "--use_legacy_sql=false", f"--project_id={BQ_PROJECT}", "--format=json", sql],
        capture_output=True, text=True, timeout=300,
    )
    if out.returncode != 0:
        raise RuntimeError(f"bq query failed: {out.stderr.strip()[:500]}")
    body = out.stdout.strip()
    # bq đôi khi in dòng cảnh báo trước JSON
    start = body.find("[")
    return json.loads(body[start:]) if start >= 0 else []


def detect_adjustments(ticker: str, start: str, end: str) -> list:
    """Mọi sự kiện điều chỉnh giá có ex-date trong (start, end]. Mặc định kind=UNVERIFIED."""
    rows = _bq(f"""
        SELECT t.time AS d, t.Price AS price, t.Close AS close
        FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
        WHERE t.ticker = '{ticker}'
          AND t.time BETWEEN DATE_SUB(DATE '{start}', INTERVAL 10 DAY) AND DATE '{end}'
          AND t.Price > 0 AND t.Close > 0
        ORDER BY t.time
    """)
    events, prev = [], None
    for r in rows:
        d = str(r["d"])[:10]
        price, close = float(r["price"]), float(r["close"])
        ratio = close / price
        if prev is not None:
            pd_, pprice, pratio = prev
            # ex-date phải nằm SAU 'start' (sự kiện trước khi mua vị thế không liên quan)
            if ratio / pratio - 1.0 > RATIO_JUMP_MIN and d > start:
                events.append(Adjustment(
                    ticker=ticker, ex_date=d, last_cum_date=pd_, last_cum_price=pprice,
                    per_share=round(pprice * (1.0 - pratio / ratio), 2),
                ))
        prev = (d, price, ratio)
    return events


def _broker_records(kind: str, account_no: str):
    """Duyệt bản ghi dnse_raw theo `kind`, ĐÃ LỌC account (coding_guidelines §12)."""
    for path in sorted(glob.glob(os.path.join(EXEC_LOG_DIR, "dnse_raw_*.jsonl"))):
        for line in open(path):
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("kind") != kind:
                continue
            if str(rec.get("account_no")) != str(account_no):
                continue
            yield rec


def verify_with_broker(adjustments: list, account_no: str, qty: int) -> list:
    """Nâng UNVERIFIED → CASH_CONFIRMED / STOCK_SUSPECTED bằng dữ liệu broker DNSE.

    CASH_CONFIRMED  : `cashDividendReceiving` tăng đúng qty × per_share quanh ex-date.
    STOCK_SUSPECTED : số lượng cổ phiếu (`openQuantity`) đổi tại ex-date → nghi chia tách.
    """
    # Chuỗi cashDividendReceiving theo thời gian.
    # Bỏ qua bản ghi "khối stock TOÀN SỐ 0" — lỗi API tạm thời đã biết của DNSE (cùng lỗi đã làm
    # sai NAV ZaloPay 27/07, xem daily_nav_snapshot.py). Nếu giữ lại, nó tạo ra một cú sụt rồi
    # bật giả trong chuỗi và làm hỏng phép đối soát delta.
    series = []
    for rec in _broker_records("balances", account_no):
        stock = rec.get("payload", {}).get("stock") or {}
        cd = stock.get("cashDividendReceiving")
        if cd is None:
            continue
        if all((stock.get(k) or 0) == 0 for k in
               ("totalCash", "availableCash", "depositInterest", "cashDividendReceiving")):
            continue
        series.append((rec.get("ts") or "", cd))
    series.sort()
    deltas = [(ts, cd - prev[1]) for prev, (ts, cd) in zip(series, series[1:]) if cd != prev[1]]

    # Số lượng cổ phiếu cuối mỗi ngày
    qty_by_day = {}
    for rec in _broker_records("positions", account_no):
        ts = rec.get("ts") or ""
        for it in rec.get("payload", {}).get("positions", []):
            if str(it.get("accountNo")) != str(account_no):
                continue
            key = (it["symbol"], ts[:10])
            if key not in qty_by_day or ts >= qty_by_day[key][0]:
                qty_by_day[key] = (ts, it.get("openQuantity"))

    for adj in adjustments:
        expected = round(qty * adj.per_share)
        # DNSE ghi khoản phải thu vào TỐI ngày cuối còn hưởng quyền (T-1 của ex-date),
        # đôi khi trượt sang chính ex-date → chấp nhận cửa sổ 2 ngày.
        window = {adj.last_cum_date, adj.ex_date}
        tol = max(10.0, expected * 0.005)
        same_day = [d for ts, d in deltas if ts[:10] in window and d > 0]
        exact = [d for d in same_day if abs(d - expected) <= tol]
        # Nhiều mã cùng ex-date (VD CTG và VCB đều 23/07) được broker ghi CHUNG một khoản —
        # khi đó delta của ngày là TỔNG, phải chấp nhận "chứa" thay vì "bằng".
        combined = [d for d in same_day if d > expected + tol]
        q0 = qty_by_day.get((adj.ticker, adj.last_cum_date), (None, None))[1]
        q1 = qty_by_day.get((adj.ticker, adj.ex_date), (None, None))[1]
        if q0 is not None and q1 is not None and q0 != q1:
            adj.kind = "STOCK_SUSPECTED"
            adj.note = f"số lượng đổi {q0} → {q1} tại ex-date — nghi chia tách/thưởng, KHÔNG cộng như tiền"
        elif exact:
            adj.kind = "CASH_CONFIRMED"
            adj.note = f"khớp cashDividendReceiving +{exact[0]:,.0f} (kỳ vọng {expected:,.0f})"
        elif combined:
            adj.kind = "CASH_CONFIRMED"
            adj.note = (f"nằm trong khoản ghi chung +{combined[0]:,.0f} của ngày (kỳ vọng riêng "
                        f"{expected:,.0f}; nhiều mã cùng ngày chốt quyền), số lượng cp không đổi")
        else:
            adj.note = ("không tìm thấy bản ghi broker khớp — có thể chưa nắm giữ tại ngày chốt quyền, "
                        "hoặc log không phủ ngày đó")
    return adjustments


def position_total_return(ticker, qty, cost_per_share, start, end, end_price=None,
                          account_no=None) -> PositionReturn:
    """Tỉ suất TỔNG (giá + cổ tức tiền mặt) của một vị thế giữ từ `start` tới `end`.

    `start` = ngày mua (chỉ tính cổ tức có ex-date SAU ngày này).
    `end_price` bỏ trống → tự lấy `Price` (thô) phiên `end`.
    `account_no` có truyền → xác minh cổ tức tiền mặt với broker (bắt buộc cho báo cáo gửi NĐT).
    """
    if end_price is None:
        rows = _bq(f"""SELECT t.Price AS price FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
                       WHERE t.ticker='{ticker}' AND t.time = DATE '{end}'""")
        if not rows:
            raise RuntimeError(f"{ticker}: không có giá phiên {end} trong tav2_bq.ticker")
        end_price = float(rows[0]["price"])

    adjs = detect_adjustments(ticker, start, end)
    if account_no:
        adjs = verify_with_broker(adjs, account_no, qty)
    div = sum(a.per_share for a in adjs if a.kind != "STOCK_SUSPECTED")
    return PositionReturn(ticker, qty, float(cost_per_share), float(end_price), div, adjs)


# --------------------------------------------------------------------------------------
# Selfcheck — số liệu thật đã đối soát ba chiều (BQ ↔ cashDividendReceiving ↔ costPrice broker)
# trong `mike/agents/Taylor/research/dividend_adjusted_returns_20260802.md`.
# --------------------------------------------------------------------------------------
_SELFCHECK_CASES = [
    # ticker, last_cum_price, last_cum_ratio, ex_ratio, expected div/share
    ("MBB", 26000.0, 25000.0 / 26000.0, 1.0, 1000.0),
    ("BID", 39300.0, 0.9885496183206107, 1.0, 450.0),
    ("CTG", 29700.0, 29250.0 / 29700.0, 1.0, 450.0),
    ("NCT", 92800.0, 84800.0 / 92800.0, 1.0, 8000.0),
    ("SAB", 46600.0, 43600.0 / 46600.0, 1.0, 3000.0),
]


def _selfcheck() -> int:
    passed = failed = 0

    def check(name, got, want, tol=0.51):
        nonlocal passed, failed
        ok = abs(got - want) <= tol
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got:,.2f} want={want:,.2f}")
        passed, failed = passed + ok, failed + (not ok)

    print("1) Công thức nhân (KHÔNG phải hiệu số) suy đúng cổ tức/cp:")
    for tk, p, r0, r1, want in _SELFCHECK_CASES:
        check(f"{tk} div/share", p * (1.0 - r0 / r1), want)

    print("2) Hiệu số Close−Price KHÔNG bằng cổ tức (chứng minh vì sao phải dùng tỉ số):")
    # SAB phiên 24/07: Price 46.500, Close 43.510 → hiệu 2.990 ≠ cổ tức thật 3.000
    check("SAB hiệu số tại 24/07 lệch so với 3.000", 46500.0 - 43510.0, 2990.0, tol=0.5)

    print("3) Tỉ suất tổng của vị thế (số thật SpaceX 31/07):")
    for tk, qty, cost, px, div, want_old, want_new in [
        ("NCT", 500, 94360, 83400, 8000, -11.61, -3.14),
        ("SAB", 1100, 47368, 43550, 3000, -8.06, -1.73),
        ("MBB", 2400, 25850, 22500, 1000, -12.96, -9.09),
    ]:
        pr = PositionReturn(tk, qty, cost, px, div)
        check(f"{tk} % chỉ-giá", pr.pct_price_only, want_old, tol=0.01)
        check(f"{tk} % tổng (gồm cổ tức)", pr.pct_total_return, want_new, tol=0.01)

    print("4) Tổng danh mục SpaceX 31/07 (giá vốn 986.725.443):")
    check("lãi/lỗ gồm cổ tức", -62_610_443 + 12_175_000, -50_435_443, tol=1)
    check("% tổng", (-62_610_443 + 12_175_000) / 986_725_443 * 100, -5.11, tol=0.01)

    print("5) Vị thế KHÔNG có cổ tức thì hai con số phải trùng khít:")
    pr = PositionReturn("PVT", 3500, 17100, 18300, 0)
    check("PVT % chỉ-giá == % tổng", pr.pct_total_return - pr.pct_price_only, 0.0, tol=1e-9)

    print("6) Cờ chưa-xác-minh phải nổi khi thiếu đối soát broker:")
    pr = PositionReturn("XXX", 100, 10000, 9000, 500,
                        [Adjustment("XXX", "2026-07-01", "2026-06-30", 10000, 500)])
    check("số sự kiện UNVERIFIED", len(pr.unverified), 1, tol=0)

    print(f"\n=== SELFCHECK: {passed} PASS / {failed} FAIL ===")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ticker")
    ap.add_argument("--qty", type=int, default=1)
    ap.add_argument("--cost", type=float, help="giá vốn THÔ/cp (giá khớp thật đã trả)")
    ap.add_argument("--from", dest="start", help="ngày mua / đầu kỳ YYYY-MM-DD")
    ap.add_argument("--to", dest="end", help="cuối kỳ YYYY-MM-DD")
    ap.add_argument("--end-price", type=float, help="ghi đè giá cuối kỳ (mặc định lấy Price thô từ BQ)")
    ap.add_argument("--account-no", help="số tài khoản DNSE để xác minh cổ tức với broker")
    ap.add_argument("--account", help="nhãn tài khoản (SpaceX/ZaloPay) — tự tra số hiệu")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()

    if a.selfcheck:
        return _selfcheck()
    if not (a.ticker and a.cost and a.start and a.end):
        ap.error("cần --ticker --cost --from --to (hoặc --selfcheck)")

    acc = a.account_no or {"SpaceX": "0002023347", "ZaloPay": "0001743768"}.get(a.account or "")
    pr = position_total_return(a.ticker, a.qty, a.cost, a.start, a.end, a.end_price, acc)

    print(f"{pr.ticker}  {pr.qty:,}cp · giá vốn {pr.cost_per_share:,.0f} · giá {a.end} {pr.end_price:,.0f}")
    for adj in pr.adjustments:
        print(f"  · ex-date {adj.ex_date}: {adj.per_share:,.0f}đ/cp  [{adj.kind}] {adj.note}")
    if not pr.adjustments:
        print("  · không có sự kiện điều chỉnh giá trong kỳ")
    print(f"  Lãi/lỗ do GIÁ      : {pr.pl_price:>15,.0f}  ({pr.pct_price_only:+.2f}%)")
    print(f"  Cổ tức tiền mặt    : {pr.dividend_total:>15,.0f}  ({pr.dividend_per_share:,.0f}đ/cp)")
    print(f"  TỔNG (dùng báo cáo): {pr.pl_total:>15,.0f}  ({pr.pct_total_return:+.2f}%)")
    if pr.unverified:
        print("\n  ⚠️ CÓ SỰ KIỆN CHƯA XÁC MINH VỚI BROKER — không đưa số này vào báo cáo gửi nhà đầu tư"
              " trước khi đối soát cashDividendReceiving / số lượng cổ phiếu.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
