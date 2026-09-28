#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dòng tiền NGOẠI SINH (nạp/rút vốn) của account — nguồn sự thật cho số hạng flow trong
tỉ suất công bố (`nav_period_returns.py`) và cho cổng chặn ở `report_delivery_gate.py`.

VÌ SAO LÀ FILE THỦ CÔNG — DNSE OpenAPI KHÔNG có nguồn nạp/rút (đã quét, không phải phỏng đoán):
  - `dnse_api.py` (SDK wrapper, 2026-09-27): 20 endpoint, KHÔNG có cash-statement/transaction/
    deposit/withdraw. Chỉ có `balances()` = SỐ DƯ tại một thời điểm, không phải SỔ dòng tiền.
  - `data/execution_logs/dnse_raw_*.jsonl` (86 file): 12 loại record, toàn bộ là
    orders/positions/balances/ppse/quote/place_order/cancel_order/loan_packages/accounts.
    KHÔNG có loại nào ghi nạp/rút.
  - Các field nghe giống dòng tiền trong `balances.stock` đều KHÔNG phải: `depositInterest`
    (lãi tiền gửi), `depositFeeAmount` (phí lưu ký/lãi vay đã post), `withdrawableCash` (hạn mức
    rút KHẢ DỤNG, không phải đã rút), `derivative.pendingDepositWithdraw` (chỉ tài khoản phái
    sinh, luôn 0 với 2 TK hiện tại).
  ⇒ Số nạp/rút chỉ con người biết. File này là nơi ghi, và `report_delivery_gate` là cơ chế
  cưỡng chế không cho quên (§6: verify artifact, đừng tin field nghe hợp lý).

SCHEMA `data/account_cash_flows.json`:
    {
      "_doc": "...",
      "SpaceX": [
        {"date": "2026-10-05", "amount_vnd": 200000000, "kind": "deposit",
         "evidence": "sao kê DNSE 2026-10-05 + email xác nhận chuyển khoản",
         "timing": "bod"}
      ],
      "ZaloPay": []
    }
  - `amount_vnd`: DƯƠNG = nạp vào, ÂM = rút ra. Số VND, không phải nghìn/triệu.
  - `kind`: "deposit" | "withdraw" | "market_only". `market_only` (amount_vnd PHẢI = 0) là lời
    KHẲNG ĐỊNH CÓ BẰNG CHỨNG rằng bước nhảy NAV ngày đó là biến động thị trường, không phải
    nạp/rút — đó là cách duy nhất để mở cổng chặn ở `report_delivery_gate`.
  - `evidence`: bắt buộc, non-empty. Không có bằng chứng ⇒ không được ghi (§6).
  - `timing`: "bod" (mặc định) hoặc "eod" — xem `nav_period_returns.py` § quy ước.
  - File KHÔNG tồn tại = CHƯA có dòng tiền nào được ghi (hợp lệ, không phải lỗi). Nó KHÔNG có
    nghĩa "không có dòng tiền nào xảy ra" — phân biệt 2 điều đó là việc của cổng NAV-jump.

Selfcheck: `python3 mike/bin/nav_flow_term_selfcheck.py`
"""
import datetime
import json
import os
import sys

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FLOWS_PATH = os.path.join(WC_ROOT, "data", "account_cash_flows.json")

VALID_KINDS = ("deposit", "withdraw", "market_only")
VALID_TIMING = ("bod", "eod")

# Ngưỡng cổng NAV-jump: |Δnav ngày| vượt ngưỡng mà KHÔNG có bản ghi dòng tiền nào cho ngày đó
# ⇒ BLOCK. Đo thật trên toàn bộ lịch sử 2 TK ngày 2026-09-27 (N=113 cặp phiên liên tiếp:
# SpaceX 58 từ 2026-07-02, ZaloPay 55 từ 2026-07-07):
#     max|Δ| = 4,148% (ZaloPay 2026-08-07) · p95 = 3,105% · median = 0,826% · mean 1,09% sd 0,93%
# Chọn 5,0%: cao hơn max quan sát 0,85pp (0 false-positive trên cả 113 quan sát lịch sử —
# `nav_flow_term_selfcheck.py` kiểm lại con số này mỗi lần chạy), và thấp hơn nhiều mức nạp/rút
# đáng kể (200tr/1B = 20%). ĐÂY LÀ CỔNG THÔ, KHÔNG PHẢI CỔNG CHÍNH XÁC: dòng tiền nhỏ hơn ~5% NAV
# (≲50tr trên 1B) KHÔNG bị nó bắt — lớp bắt chặt hơn là residual "CHƯA GIẢI THÍCH ĐƯỢC" 0,3% NAV
# của `reconcile_equity.py` (§6 pipeline bước 3). Nói thẳng giới hạn thay vì để người dùng tưởng
# cổng này phủ mọi dòng tiền.
NAV_JUMP_BLOCK_PCT = 5.0


class CashFlowError(ValueError):
    """Bản ghi dòng tiền sai schema — fail-closed, không được bỏ qua im lặng."""


def _parse_date(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


def load_flows(account, flows_path=None, require_file=False):
    """Trả list [{date, amount_vnd, kind, evidence, timing}, ...] tăng dần theo ngày.

    Bản ghi sai schema ⇒ raise CashFlowError (KHÔNG bỏ qua: một bản ghi hỏng nghĩa là dòng tiền
    có xảy ra mà ta không đọc đúng, đúng lớp lỗi §28 "suy từ sự vắng mặt").

    **File THIẾU — hai chế độ, phân biệt theo người gọi (siết 2026-09-28, user duyệt):**
      · `require_file=True` ⇒ **raise CashFlowError**. Dùng cho đường CÔNG BỐ SỐ (§21/§31:
        `nav_period_returns.py`). Lý do: thiếu file thì "không có dòng tiền nào" và "đã mất sổ
        dòng tiền" LÀ HAI VIỆC KHÁC NHAU mà hàm này không phân biệt được — và nếu đoán sai theo
        hướng `[]` thì một lần NẠP tiền thật bị công bố thành LÃI, tức sai theo hướng có lợi cho
        mình, hướng tệ nhất để sai.
      · `require_file=False` (mặc định, giữ nguyên hành vi cũ) ⇒ trả `[]` **nhưng IN cảnh báo ra
        stderr** thay vì im lặng. Dùng cho đường không công bố (`daily_nav_snapshot.py`, vốn còn
        cổng NAV-jump 5% riêng).
    Bản ghi RỖNG khi file CÓ (account chưa từng có dòng tiền) là `[]` hợp lệ ở CẢ HAI chế độ —
    đó là "đã đọc và xác nhận không có", khác hẳn "không đọc được".
    """
    path = flows_path or os.environ.get("ACCOUNT_CASH_FLOWS_PATH") or FLOWS_PATH
    if not os.path.exists(path):
        if require_file:
            raise CashFlowError(
                f"KHÔNG có sổ dòng tiền {path} — người gọi yêu cầu bắt buộc (require_file=True)."
                " Thiếu file thì không phân biệt được 'chưa từng nạp/rút' với 'mất sổ', và đoán"
                " theo hướng rỗng sẽ công bố một lần NẠP thành LÃI. Tạo file (có thể là"
                ' {"<account>": []} nếu thật sự chưa có dòng tiền nào) rồi chạy lại.')
        print(f"[account_cash_flows] CẢNH BÁO: không có {path} ⇒ coi như KHÔNG có dòng tiền"
              f" nào cho '{account}'. Nếu account này ĐÃ từng nạp/rút, mọi tỉ suất tính từ đây"
              f" đều SAI (nạp bị tính thành lãi).", file=sys.stderr)
        return []
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    raw = cfg.get(account, [])
    if not isinstance(raw, list):
        raise CashFlowError(f"{path}: entry của '{account}' phải là list, được {type(raw).__name__}")
    out = []
    for i, rec in enumerate(raw):
        where = f"{path}[{account}][{i}]"
        if not isinstance(rec, dict):
            raise CashFlowError(f"{where}: phải là object")
        for key in ("date", "amount_vnd", "kind", "evidence"):
            if key not in rec:
                raise CashFlowError(f"{where}: thiếu field bắt buộc '{key}'")
        try:
            d = _parse_date(rec["date"])
        except ValueError as exc:
            raise CashFlowError(f"{where}: date không phải YYYY-MM-DD ({exc})") from exc
        kind = rec["kind"]
        if kind not in VALID_KINDS:
            raise CashFlowError(f"{where}: kind='{kind}' không thuộc {VALID_KINDS}")
        try:
            amount = float(rec["amount_vnd"])
        except (TypeError, ValueError) as exc:
            raise CashFlowError(f"{where}: amount_vnd không phải số ({rec['amount_vnd']!r})") from exc
        if not str(rec["evidence"]).strip():
            raise CashFlowError(f"{where}: evidence rỗng — không có bằng chứng thì không được ghi")
        if kind == "market_only" and amount != 0:
            raise CashFlowError(f"{where}: kind='market_only' phải có amount_vnd=0, được {amount:.0f}")
        if kind == "deposit" and amount <= 0:
            raise CashFlowError(f"{where}: kind='deposit' phải có amount_vnd>0, được {amount:.0f}")
        if kind == "withdraw" and amount >= 0:
            raise CashFlowError(f"{where}: kind='withdraw' phải có amount_vnd<0 (rút = số âm), "
                                f"được {amount:.0f}")
        timing = rec.get("timing", "bod")
        if timing not in VALID_TIMING:
            raise CashFlowError(f"{where}: timing='{timing}' không thuộc {VALID_TIMING}")
        out.append({"date": d, "amount_vnd": amount, "kind": kind,
                    "evidence": str(rec["evidence"]), "timing": timing})
    out.sort(key=lambda r: r["date"])
    return out


def flow_dates(flows):
    """Set mọi ngày CÓ bản ghi (kể cả market_only amount=0) — dùng cho cổng NAV-jump."""
    return {f["date"] for f in flows}


def attach_flows_to_rows(rows, flows):
    """Gán mỗi bản ghi dòng tiền vào ĐÚNG MỘT mốc quan sát NAV.

    `rows`: [(date, nav), ...] tăng dần (nav_history). Quy tắc gán:
      - timing="bod": ngày quan sát NAV ĐẦU TIÊN có date >= flow.date. Tiền đã vào tài khoản
        trước khi chốt NAV ngày đó ⇒ nav ngày đó ĐÃ chứa tiền nạp. Nạp cuối tuần (không có dòng
        nav_history) vì vậy rơi đúng vào phiên kế tiếp.
      - timing="eod": phải có dòng nav_history ĐÚNG ngày đó (tiền vào/ra sau khi NAV ngày đó đã
        được chốt theo giá đóng cửa); không có ⇒ CashFlowError (nạp/rút EOD của một ngày không
        có snapshot thực chất là BOD của phiên sau — ghi lại cho đúng, đừng để script đoán).
    Trả dict {row_date: [flow, ...]}. Flow sau dòng NAV cuối cùng bị BỎ (ngoài kỳ đo) và trả
    riêng ở key None để caller báo nếu cần.
    """
    dates = [d for d, _ in rows]
    mapped = {}
    for f in flows:
        if f["timing"] == "eod":
            if f["date"] not in dates:
                raise CashFlowError(
                    f"flow {f['date']} timing='eod' nhưng nav_history không có dòng ngày đó — "
                    f"ghi lại thành timing='bod' của phiên kế tiếp")
            key = f["date"]
        else:
            key = next((d for d in dates if d >= f["date"]), None)
        mapped.setdefault(key, []).append(f)
    return mapped


def unexplained_nav_jumps(rows, flows, threshold_pct=NAV_JUMP_BLOCK_PCT,
                          start=None, end=None):
    """Bước nhảy NAV ngày vượt `threshold_pct` mà KHÔNG có bản ghi dòng tiền nào cho ngày đó.

    Trả list dict {date, prev_date, nav0, nav1, change_pct}. `start`/`end` (date) giới hạn theo
    ngày ĐẾN của bước nhảy; None = không giới hạn.
    """
    have = flow_dates(flows)
    out = []
    for (d0, n0), (d1, n1) in zip(rows, rows[1:]):
        if start is not None and d1 < start:
            continue
        if end is not None and d1 > end:
            continue
        if not n0:
            continue
        chg = (n1 / n0 - 1) * 100
        if abs(chg) > threshold_pct and d1 not in have:
            out.append({"date": d1, "prev_date": d0, "nav0": n0, "nav1": n1, "change_pct": chg})
    return out
