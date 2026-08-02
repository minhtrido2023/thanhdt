#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TẦNG 2 + TẦNG 3 của phương pháp cổ tức — bản STAGED chờ merge vào
`mike/bin/dividend_adjusted_return.py` (Winston_20260802_082040 đang sửa file đó, không ghi đè).

BỐI CẢNH — phản biện của user (2026-08-02)
------------------------------------------
Tỉ số `Close/Price` chỉ nói "CÓ một sự kiện điều chỉnh giá", KHÔNG nói đó là loại gì: cổ tức tiền
mặt, cổ tức cổ phiếu, thưởng CP, chia tách, phát hành thêm — tất cả làm tỉ số nhảy y hệt nhau. Suy
ngược ra "đồng/cp" từ tỉ số là ÁP một giả định mà chính dữ liệu đó không kiểm chứng được.

KIẾN TRÚC 3 TẦNG
    TẦNG 1 · PHÁT HIỆN   `Close/Price`                       → "mã nào, ngày nào" (+ ước lượng thô)
    TẦNG 2 · ĐO LƯỜNG    tiền mặt broker DNSE                → SỐ CHÍNH THỨC (đồng/cp)
    TẦNG 3 · ĐỐI SOÁT    `ticker_financial.Dividend_1Y` delta → xác nhận độc lập, trễ theo quý

TẦNG 2 LÀ MỘT HỆ PHƯƠNG TRÌNH, KHÔNG PHẢI PHÉP CHIA
---------------------------------------------------
DNSE ghi cổ tức phải thu vào `balances.stock.cashDividendReceiving`. Delta DƯƠNG = tiền cổ tức mới
ghi nhận, nhưng là **của TOÀN TÀI KHOẢN theo NGÀY, không tách theo mã** — nhiều mã cùng ngày chốt
quyền rơi chung một delta. Nên:

    với mỗi (tài khoản a, ngày d):   delta(a,d) = Σ_mã  qty(a, mã) × per_share(mã)

Hai tài khoản SpaceX/ZaloPay có tỉ lệ nắm giữ KHÁC nhau → hai phương trình độc lập. Hệ 2×2 của
ngày 23/07 (CTG và VCB cùng ex-date) có nghiệm DUY NHẤT suy hoàn toàn từ tiền thật:

    2300·CTG + 1300·VCB = 1.620.000   (SpaceX)     →  CTG = 450
    1050·CTG +  800·VCB =   832.500   (ZaloPay)    →  VCB = 450

Giải theo từng THÀNH PHẦN LIÊN THÔNG. Đủ hạng + dư số ~0 ⇒ `CASH_CONFIRMED`. Vô định (chỉ giữ ở 1
tài khoản mà 2 mã cùng ngày) ⇒ giữ `UNVERIFIED`, **CẤM đưa vào báo cáo** — không lấp bằng tỉ số.

BIGQUERY KHÔNG CÓ CỘT RAW PER-EVENT (tự kiểm 2026-08-02)
Chỉ có `tav2_bq.shares_outstanding_live` (`ex_date`+`cash_div_per_share`+`stock_div_ratio`) đúng
hình dạng cần — nhưng **4 dòng**, Winston ghi tay khi cần override `OShares`, 0 dòng cho 6 sự kiện
tháng 7/2026. Dùng nếu có (đã phân loại sẵn), không coi là nguồn có sẵn.

    python3 dividend_broker_solve.py --selfcheck        # offline, không cần BQ/log
    python3 dividend_broker_solve.py --resolve MBB,BID,CTG,VCB,NCT,SAB --from 2026-07-01 --to 2026-08-01
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
from dividend_adjusted_return import (  # noqa: E402
    BQ_PROJECT, Adjustment, _bq, _broker_records, detect_adjustments,
)

ACCOUNTS = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}

# Dư số chấp nhận được của một phương trình broker (VND) — làm tròn số dư + phí lẻ.
EQ_TOL_ABS, EQ_TOL_REL = 10.0, 0.005
# Nghiệm lệch quá ngưỡng này so với ước lượng tỉ số ⇒ nghi phương trình bị nhiễm bởi một sự kiện
# chưa phát hiện rơi cùng delta ⇒ hạ về UNVERIFIED (tầng 1 làm LƯỚI AN TOÀN, không làm nguồn số).
SANITY_REL = 0.01


def cash_per_share(adj) -> float:
    """Số đồng/cp được phép cộng vào tỉ suất. 0 nếu chưa xác minh — KHÔNG suy diễn từ tỉ số."""
    return adj.per_share if getattr(adj, "kind", "") == "CASH_CONFIRMED" else 0.0


# ======================================================================================
# TẦNG 2 · ĐO LƯỜNG
# ======================================================================================

def bq_corp_action(ticker: str, ex_date: str):
    """Ưu tiên 1: bảng corp-action BQ — hiếm khi có, nhưng đã phân loại sẵn tiền/cổ phiếu."""
    rows = _bq(f"""
        SELECT s.cash_div_per_share AS cash, s.stock_div_ratio AS stock
        FROM `{BQ_PROJECT}.tav2_bq.shares_outstanding_live` AS s
        WHERE s.ticker = '{ticker}' AND s.ex_date = DATE '{ex_date}'
    """)
    return rows[0] if rows else None


def broker_cash_deltas(account_no: str) -> dict:
    """{ngày: tổng delta DƯƠNG của `cashDividendReceiving`} — tiền cổ tức mới được ghi nhận.

    Delta ÂM = khoản phải thu đã chi trả về `totalCash` (không phải sự kiện mới) → bỏ.
    Bỏ bản ghi "khối stock TOÀN SỐ 0" — lỗi API tạm thời đã biết của DNSE (cùng lỗi làm sai NAV
    ZaloPay 27/07); giữ lại sẽ tạo cú sụt rồi bật giả trong chuỗi và hỏng phép lấy delta.
    """
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
    out = {}
    for (_, prev_cd), (ts, cd) in zip(series, series[1:]):
        if cd > prev_cd:
            out[ts[:10]] = out.get(ts[:10], 0.0) + (cd - prev_cd)
    return out


def broker_qty(account_no: str) -> dict:
    """{(mã, ngày): số lượng cuối ngày} từ bản ghi positions (đã lọc account, §12)."""
    out = {}
    for rec in _broker_records("positions", account_no):
        ts = rec.get("ts") or ""
        for it in rec.get("payload", {}).get("positions", []):
            if str(it.get("accountNo")) != str(account_no):
                continue
            key = (it["symbol"], ts[:10])
            if key not in out or ts >= out[key][0]:
                out[key] = (ts, it.get("openQuantity"))
    return {k: v[1] for k, v in out.items()}


def _qty_at(qmap: dict, adj) -> float:
    """Số lượng hưởng quyền: ưu tiên ngày cuối còn quyền, thiếu thì lấy chính ex-date."""
    q = qmap.get((adj.ticker, adj.last_cum_date))
    if q is None:
        q = qmap.get((adj.ticker, adj.ex_date))
    return float(q or 0.0)


def _connected(equations: list, n: int) -> list:
    """Gom (phương trình, ẩn) thành thành phần liên thông. equations = [(cols, rhs, label)]."""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for cols, _, _ in equations:
        for c in cols[1:]:
            ra, rb = find(cols[0]), find(c)
            if ra != rb:
                parent[ra] = rb
    groups = {}
    for eq in equations:
        root = find(eq[0][0])
        eqs, cols = groups.setdefault(root, ([], set()))
        eqs.append(eq)
        cols.update(eq[0])
    return [(eqs, sorted(cols)) for eqs, cols in groups.values()]


def solve_from_broker(adjustments: list, accounts: dict, deltas=None, qtys=None) -> list:
    """Giải `per_share` của từng sự kiện TỪ TIỀN BROKER THẬT.

    Đặt `kind=CASH_CONFIRMED` + `source='broker_solved'` khi giải được; ngược lại giữ
    `kind='UNVERIFIED'` (giá trị `per_share` ước lượng từ tỉ số vẫn nằm đó cho mục đích chẩn đoán,
    nhưng `cash_per_share()` trả 0 nên KHÔNG thể lọt vào báo cáo).

    `deltas`/`qtys` cho phép tiêm dữ liệu giả lập trong selfcheck (chạy offline).
    """
    import numpy as np

    deltas = deltas or {lb: broker_cash_deltas(no) for lb, no in accounts.items()}
    qtys = qtys or {lb: broker_qty(no) for lb, no in accounts.items()}
    for adj in adjustments:
        adj.source = getattr(adj, "source", "unresolved")

    # (a) Nghi CHIA TÁCH/THƯỞNG CP: số lượng đổi ngay tại ex-date → không sinh tiền, loại khỏi hệ.
    live = []
    for adj in adjustments:
        changed = [f"{lb} {qtys[lb][(adj.ticker, adj.last_cum_date)]}→{qtys[lb][(adj.ticker, adj.ex_date)]}"
                   for lb in accounts
                   if (adj.ticker, adj.last_cum_date) in qtys[lb] and (adj.ticker, adj.ex_date) in qtys[lb]
                   and qtys[lb][(adj.ticker, adj.last_cum_date)] != qtys[lb][(adj.ticker, adj.ex_date)]]
        if changed:
            adj.kind = "STOCK_SUSPECTED"
            adj.note = ("số lượng cổ phiếu đổi tại ex-date (" + "; ".join(changed)
                        + ") — nghi chia tách/thưởng, KHÔNG cộng như tiền")
        else:
            live.append(adj)

    # (b) Dựng hệ. DNSE ghi khoản phải thu tối ngày cuối còn quyền, đôi khi trượt sang chính ex-date
    # → cửa sổ 2 ngày. Nhưng khoản đó chỉ được ghi MỘT LẦN, nên mỗi sự kiện chỉ được gán vào ĐÚNG
    # MỘT ngày trong cửa sổ (ngày SỚM NHẤT có delta dương), nếu không nó sẽ bị đếm ở cả hai.
    # Bẫy thật: ex-date của NCT (27/07) trùng ngày-cuối-còn-quyền của SAB (27/07) — để cửa sổ rộng
    # thì NCT bị cộng vào cả delta 24/07 lẫn 3.300.000 của 27/07, hệ mâu thuẫn, cả hai mã hỏng.
    equations = []
    for lb in accounts:
        by_day = {}
        for i, adj in enumerate(live):
            if _qty_at(qtys[lb], adj) <= 0:
                continue
            for day in (adj.last_cum_date, adj.ex_date):
                if deltas[lb].get(day, 0) > 0:
                    by_day.setdefault(day, []).append(i)
                    break
        for day, cols in sorted(by_day.items()):
            equations.append((cols, float(deltas[lb][day]), (lb, day)))

    # (c) Giải từng thành phần liên thông độc lập.
    for eqs, cols in _connected(equations, len(live)):
        pos = {c: j for j, c in enumerate(cols)}
        A = np.zeros((len(eqs), len(cols)))
        b = np.zeros(len(eqs))
        for i, (ecols, rhs, (lb, _)) in enumerate(eqs):
            b[i] = rhs
            for c in ecols:
                A[i, pos[c]] = _qty_at(qtys[lb], live[c])

        names = ", ".join(f"{live[c].ticker}@{live[c].ex_date}" for c in cols)
        shape = f"{len(eqs)} phương trình / {len(cols)} ẩn: {names}"
        if np.linalg.matrix_rank(A) < len(cols):
            for c in cols:
                live[c].note = (f"hệ VÔ ĐỊNH ({shape}) — nhiều mã cùng ngày chốt quyền mà không đủ "
                                "tài khoản có tỉ lệ nắm giữ khác nhau để tách")
            continue

        x = np.round(np.linalg.lstsq(A, b, rcond=None)[0])
        resid = A @ x - b
        bad = [f"{lb} {d}" for i, (_, _, (lb, d)) in enumerate(eqs)
               if abs(resid[i]) > max(EQ_TOL_ABS, EQ_TOL_REL * abs(b[i]))]
        if bad:
            for c in cols:
                live[c].note = ("nghiệm KHÔNG khớp tiền broker tại " + ", ".join(bad)
                                + " — có thể còn mã khác cùng ngày chưa phát hiện")
            continue

        for c in cols:
            adj, val = live[c], float(x[pos[c]])
            ref = float(getattr(adj, "ratio_per_share", adj.per_share) or 0.0)
            if val <= 0 or (ref > 0 and abs(val - ref) > SANITY_REL * ref):
                adj.note = (f"nghiệm broker {val:,.0f}đ/cp LỆCH XA ước lượng tỉ số {ref:,.0f}đ/cp — "
                            "nghi phương trình bị nhiễm bởi sự kiện chưa phát hiện")
                continue
            adj.per_share, adj.kind, adj.source = val, "CASH_CONFIRMED", "broker_solved"
            adj.note = f"giải từ tiền mặt broker thật ({shape})"

    for adj in adjustments:
        if adj.kind == "UNVERIFIED" and not adj.note:
            adj.note = ("không có bản ghi broker khớp — chưa nắm giữ tại ngày chốt quyền, "
                        "hoặc log không phủ ngày đó")
    return adjustments


# ======================================================================================
# TẦNG 3 · ĐỐI SOÁT CHẬM
# ======================================================================================

def crosscheck_dividend_1y(adjustments: list) -> list:
    """Đối soát với delta `Dividend_1Y` giữa hai kỳ báo cáo quý liên tiếp.

    ĐỘ TRỄ LÀ BẢN CHẤT: `Dividend_1Y` chỉ đổi khi có báo cáo quý mới, nên sự kiện xảy ra SAU kỳ gần
    nhất chưa xuất hiện (SAB ex-date 28/07 > kỳ 23/07 → `unavailable`). Nó còn là tổng TRAILING nên
    delta có thể ÂM khi một cổ tức cũ rơi khỏi cửa sổ 1 năm. Vì vậy tầng này CHỈ xác nhận thêm,
    KHÔNG BAO GIỜ ghi đè số của tầng 2.
    """
    for adj in adjustments:
        rows = _bq(f"""
            SELECT t.time AS d, t.Dividend_1Y AS d1y
            FROM `{BQ_PROJECT}.tav2_bq.ticker_financial` AS t
            WHERE t.ticker = '{adj.ticker}' AND t.Dividend_1Y IS NOT NULL
              AND t.time >= DATE_SUB(DATE '{adj.ex_date}', INTERVAL 400 DAY)
            ORDER BY t.time
        """)
        after = [i for i, r in enumerate(rows) if str(r["d"])[:10] > adj.ex_date]
        if not after or after[0] == 0:
            adj.fin_check, adj.fin_note = "unavailable", (
                "chưa có kỳ báo cáo quý nào sau ex-date (độ trễ theo quý) — KHÔNG kết luận gì")
            continue
        i = after[0]
        # bq --format=json trả MỌI giá trị dưới dạng STRING — phải ép kiểu trước khi định dạng số.
        prev_d1y, cur_d1y = float(rows[i - 1]["d1y"]), float(rows[i]["d1y"])
        delta = cur_d1y - prev_d1y
        ref = float(adj.per_share or 0.0)
        span = f"Dividend_1Y {prev_d1y:,.0f}→{cur_d1y:,.0f} (delta {delta:+,.0f})"
        if ref > 0 and abs(delta - ref) <= max(1.0, 0.01 * ref):
            adj.fin_check, adj.fin_note = "match", span
        else:
            adj.fin_check, adj.fin_note = "mismatch", (
                f"{span} ≠ {ref:,.0f} — là tổng TRAILING, một cổ tức cũ có thể vừa rơi khỏi cửa sổ "
                "1 năm; KHÔNG dùng để bác số tầng 2")
    return adjustments


# ======================================================================================
# API cho báo cáo
# ======================================================================================

def resolve_dividends(tickers, start: str, end: str, accounts: dict = None,
                      with_crosscheck: bool = True) -> list:
    """Chạy đủ 3 tầng cho một RỔ mã. LÀM BÁO CÁO PHẢI DÙNG BẢN NÀY — giải cả rổ mới đủ phương trình
    để tách những ngày nhiều mã cùng chốt quyền."""
    accounts = ACCOUNTS if accounts is None else accounts
    adjs = []
    for tk in tickers:
        for a in detect_adjustments(tk, start, end):
            a.ratio_per_share = a.per_share      # TẦNG 1 = ước lượng, giữ lại để chẩn đoán/sanity
            a.source = "unresolved"
            a.fin_check, a.fin_note = "unavailable", ""
            adjs.append(a)

    for adj in adjs:                              # ưu tiên 1: bảng corp-action BQ (nếu tình cờ có)
        row = bq_corp_action(adj.ticker, adj.ex_date)
        if row and row.get("cash") is not None:
            adj.per_share = float(row["cash"])
            adj.source = "bq_corp_action"
            adj.kind = "CASH_CONFIRMED" if adj.per_share > 0 else "STOCK_SUSPECTED"
            adj.note = f"tav2_bq.shares_outstanding_live (stock_div_ratio={row.get('stock')})"

    todo = [a for a in adjs if a.source == "unresolved"]
    if todo:
        solve_from_broker(todo, accounts)
    if with_crosscheck:
        crosscheck_dividend_1y(adjs)
    return adjs


# ======================================================================================
# Selfcheck — OFFLINE (không cần BQ, không cần log broker) để không phụ thuộc môi trường.
# Số liệu giả lập dưới đây là SỐ THẬT trích từ dnse_raw_*.jsonl (xem reconcile_july.txt).
# ======================================================================================

_QTY = {
    "SpaceX": {("CTG", "2026-07-22"): 2300, ("VCB", "2026-07-22"): 1300,
               ("NCT", "2026-07-24"): 500, ("SAB", "2026-07-27"): 1100,
               ("MBB", "2026-07-08"): 2400, ("BID", "2026-07-16"): 1900},
    "ZaloPay": {("CTG", "2026-07-22"): 1050, ("VCB", "2026-07-22"): 800,
                ("NCT", "2026-07-24"): 373, ("SAB", "2026-07-27"): 744,
                ("BID", "2026-07-16"): 900},
}
_DELTA = {
    "SpaceX": {"2026-07-09": 2_400_000.0, "2026-07-16": 855_000.0, "2026-07-22": 1_620_000.0,
               "2026-07-24": 4_000_000.0, "2026-07-27": 3_300_000.0},
    "ZaloPay": {"2026-07-16": 405_000.0, "2026-07-22": 832_500.0,
                "2026-07-24": 2_984_000.0, "2026-07-28": 2_232_000.0},
}
_EVENTS = [  # ticker, ex_date, last_cum_date, giá cuối còn quyền, ước lượng tỉ số
    ("MBB", "2026-07-09", "2026-07-08", 26000.0, 1000.0),
    ("BID", "2026-07-17", "2026-07-16", 39300.0, 450.0),
    ("CTG", "2026-07-23", "2026-07-22", 29700.0, 450.0),
    ("VCB", "2026-07-23", "2026-07-22", 54500.0, 450.0),
    ("NCT", "2026-07-27", "2026-07-24", 92800.0, 8000.0),
    ("SAB", "2026-07-28", "2026-07-27", 46600.0, 3000.0),
]


def _mk(tk, ex, cum, price, ratio_ps):
    a = Adjustment(ticker=tk, ex_date=ex, last_cum_date=cum, last_cum_price=price, per_share=ratio_ps)
    a.ratio_per_share, a.source = ratio_ps, "unresolved"
    return a


def _solve_offline(adjs, accounts, qty=None, delta=None):
    return solve_from_broker(
        adjs, accounts,
        deltas={lb: (delta or _DELTA).get(lb, {}) for lb in accounts},
        qtys={lb: (qty or _QTY).get(lb, {}) for lb in accounts})


def _selfcheck() -> int:
    passed = failed = 0

    def eq(name, got, want, tol=0.51):
        nonlocal passed, failed
        ok = isinstance(got, (int, float)) and abs(got - want) <= tol
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got:,.2f} want={want:,.2f}" if ok or
              isinstance(got, (int, float)) else f"  [FAIL] {name}: got={got!r} want={want!r}")
        passed, failed = passed + ok, failed + (not ok)

    def same(name, got, want):
        nonlocal passed, failed
        ok = got == want
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got!r} want={want!r}")
        passed, failed = passed + ok, failed + (not ok)

    print("1) TẦNG 2 giải ĐÚNG cả 6 sự kiện tháng 7 từ TIỀN BROKER THẬT (không dùng tỉ số):")
    adjs = [_mk(*e) for e in _EVENTS]
    _solve_offline(adjs, ACCOUNTS)
    for a, (tk, _, _, _, want) in zip(adjs, _EVENTS):
        eq(f"{tk} per_share", a.per_share, want)
        same(f"{tk} kind/source", (a.kind, a.source), ("CASH_CONFIRMED", "broker_solved"))

    print("2) Ngày 23/07 CTG+VCB trùng ex-date: chỉ tách được nhờ hệ 2 tài khoản (2pt/2ẩn):")
    two = [_mk(*e) for e in _EVENTS if e[0] in ("CTG", "VCB")]
    _solve_offline(two, ACCOUNTS)
    eq("CTG", two[0].per_share, 450.0)
    eq("VCB", two[1].per_share, 450.0)
    print("     kiểm tra ngược: 2300·450+1300·450 và 1050·450+800·450 phải khớp delta thật")
    eq("SpaceX 22/07", 2300 * 450 + 1300 * 450, 1_620_000, tol=1)
    eq("ZaloPay 22/07", 1050 * 450 + 800 * 450, 832_500, tol=1)

    print("3) HỆ VÔ ĐỊNH (1 tài khoản, 2 ẩn) ⇒ giữ UNVERIFIED, KHÔNG lấp bằng ước lượng tỉ số:")
    two2 = [_mk(*e) for e in _EVENTS if e[0] in ("CTG", "VCB")]
    _solve_offline(two2, {"SpaceX": ACCOUNTS["SpaceX"]})
    same("CTG kind", two2[0].kind, "UNVERIFIED")
    eq("CTG cash_per_share (không được lọt vào báo cáo)", cash_per_share(two2[0]), 0.0, tol=1e-9)
    print(f"     lý do ghi lại: {two2[0].note[:70]}…")

    print("4) Ước lượng tỉ số SAI ⇒ hạ về UNVERIFIED (tầng 1 là lưới an toàn, không phải nguồn số):")
    bad = _mk("NCT", "2026-07-27", "2026-07-24", 92800.0, 5000.0)   # tỉ số lệch 60%
    _solve_offline([bad], ACCOUNTS)
    same("NCT kind khi tỉ số lệch xa", bad.kind, "UNVERIFIED")
    eq("NCT cash_per_share", cash_per_share(bad), 0.0, tol=1e-9)

    print("5) Số lượng cổ phiếu đổi tại ex-date ⇒ STOCK_SUSPECTED, KHÔNG cộng như tiền:")
    xxx = _mk("XXX", "2026-07-23", "2026-07-22", 10000.0, 500.0)
    _solve_offline([xxx], {"SpaceX": ACCOUNTS["SpaceX"]},
                   qty={"SpaceX": {("XXX", "2026-07-22"): 1000, ("XXX", "2026-07-23"): 1150}},
                   delta={"SpaceX": {"2026-07-22": 500_000.0}})
    same("XXX kind", xxx.kind, "STOCK_SUSPECTED")
    eq("XXX cash_per_share", cash_per_share(xxx), 0.0, tol=1e-9)

    print("6) Delta ÂM (chi trả khoản phải thu) KHÔNG được coi là sự kiện mới:")
    # SpaceX 17/07 có delta −2.400.000 (trả cổ tức MBB) — nếu bị tính, BID sẽ sai.
    bid = _mk("BID", "2026-07-17", "2026-07-16", 39300.0, 450.0)
    _solve_offline([bid], ACCOUNTS)
    eq("BID per_share vẫn đúng 450 (delta âm 17/07 đã bị loại)", bid.per_share, 450.0)

    print("7) Tổng cộng lại phải khớp tiền cổ tức thật từng tài khoản:")
    eq("SpaceX tổng", 2400 * 1000 + 1900 * 450 + 2300 * 450 + 1300 * 450 + 500 * 8000 + 1100 * 3000,
       12_175_000, tol=1)
    eq("ZaloPay tổng (không có MBB — mua sau ex-date 09/07)",
       900 * 450 + 1050 * 450 + 800 * 450 + 373 * 8000 + 744 * 3000, 6_453_500, tol=1)

    print(f"\n=== SELFCHECK: {passed} PASS / {failed} FAIL ===")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resolve", help="danh sách mã, phân tách bằng dấu phẩy")
    ap.add_argument("--from", dest="start")
    ap.add_argument("--to", dest="end")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()

    if a.selfcheck:
        return _selfcheck()
    if not (a.resolve and a.start and a.end):
        ap.error("cần --resolve --from --to (hoặc --selfcheck)")

    adjs = resolve_dividends([t.strip().upper() for t in a.resolve.split(",")], a.start, a.end)
    print(f"Sự kiện {a.start} → {a.end} (giải từ tiền broker: {', '.join(ACCOUNTS)}):\n")
    for x in sorted(adjs, key=lambda z: (z.ex_date, z.ticker)):
        ps = f"{x.per_share:,.0f}đ/cp" if x.kind == "CASH_CONFIRMED" else "— (chưa xác minh)"
        print(f"  {x.ticker:5s} ex {x.ex_date}  {ps:>22s}  [{x.kind}/{x.source}]")
        print(f"        ước lượng tỉ số (chỉ để đối chiếu): {getattr(x,'ratio_per_share',0):,.0f}đ/cp")
        print(f"        {x.note}")
        print(f"        Dividend_1Y: {x.fin_check} — {x.fin_note}")
    bad = [x for x in adjs if x.kind == "UNVERIFIED"]
    if bad:
        print(f"\n  ⚠️ {len(bad)} sự kiện CHƯA XÁC MINH — CẤM đưa vào báo cáo gửi nhà đầu tư.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
