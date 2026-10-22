#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đẳng thức tiền hằng tối — tự phát hiện dòng tiền NGOÀI (nạp/rút) CHƯA KHAI.

Bước 2/4 của chính sách "tài khoản = quỹ mở" (`kb/projects/fund-unit-performance-policy-20261010.md`).
Sổ `data/account_cash_flows.json` do NGƯỜI khai; file rỗng nghĩa là "chưa ai GHI", không phải "chưa
có nạp/rút", và cổng bước nhảy NAV 5%/15% không thấy khoản ≲50tr. Module này là lớp bắt chặt hơn:
với MỖI cửa sổ giữa hai lần chụp NAV liên tiếp, phần biến động tiền KHÔNG giải thích được bằng các
khoản nội bộ đọc được = dòng tiền ngoài NGHI NGỜ. Nó KHÔNG BAO GIỜ ghi vào sổ nào: cửa sổ cần người
xem thì hiện ra kèm bằng chứng đã đọc (§29) cho tới khi người khai dòng tiền hoặc ghi lời xác nhận.

ĐẲNG THỨC (một cửa sổ = từ lần chụp của dòng nav_history trước tới lần chụp của dòng sau):

    ΔK = bán − mua − phí − thuế bán + cổ tức + lãi Trứng vàng − khấu trừ rút Trứng vàng
         + [dòng tiền ngoài] + nhiễu

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
  khấu trừ rút Trứng vàng = số rút ròng × `EGG_WITHDRAW_COST` (đo một lần — xem hằng số).

SỐ LƯỢNG CỔ PHIẾU — kiểm ở MỌI cửa sổ, không chỉ cửa sổ đã bị nghi: số lượng vị thế đổi phải bằng
đúng lệnh đã đọc, cộng cổ phiếu thưởng/cổ tức cổ phiếu ĐÃ KÝ trong `data/corp_actions.json`. Còn dư
⇒ có giao dịch mà module không thấy (lệnh đặt ngoài bot, quyền mua, chuyển khoản chứng khoán): tiền
của nó có thể đang bù trừ đúng một khoản nạp/rút nên phần dư tiền ~0 KHÔNG chứng minh được gì ⇒ cửa
sổ "không kết luận được", nêu mã + số lượng + giá trị ước tính. Không đọc được vị thế ở một đầu cửa
sổ ⇒ KHÔNG đối chiếu được số lượng: cửa sổ vẫn được xét theo phần dư tiền, kèm ghi chú nói rõ điều
đó, và lượt chụp của đúng ngày ấy báo một dòng ở kênh vận hành (thiếu bằng chứng ≠ sạch).

KHÔNG mô hình hoá (nằm trong phần dư, và là lý do có ngưỡng): các khoản DNSE ghi có/ghi nợ DỒN
theo kỳ (lãi vay ký quỹ, phí ứng trước, lãi tiền gửi không kỳ hạn, phí lưu ký cuối tháng), phí
UPCOM thấp hơn HOSE 0,009pp, thuế bán cổ phiếu thưởng, cổ tức chốt quyền và chi trả trong cùng một
cửa sổ. Phần dư vượt ngưỡng mà một trong các khoản đó có thể phủ được thì mang nhãn "cần xác nhận
khoản nội bộ" kèm ước tính, KHÔNG gọi là nạp/rút.

KHÔNG phủ:
  · chuyển CỔ PHIẾU vào/ra không kèm tiền: chỉ thấy ở dạng "số lượng đổi ngoài lệnh" (không biết
    giá trị thật) — lớp bắt chính vẫn là cổng bước nhảy NAV và cổng phần dư số lượng của
    `daily_nav_snapshot.py`;
  · nạp/rút đi kèm lệnh ngoài bot ở mã có sự kiện cổ phiếu thưởng đã ký CÙNG cửa sổ, với số lượng
    trùng đúng số cổ phiếu thưởng;
  · nạp/rút đi kèm lệnh ngoài bot trong cửa sổ KHÔNG đọc được vị thế ở một đầu (lịch sử thật tới
    2026-10-12: 3/135 cửa sổ, đều là dòng chụp lại/chụp giữa phiên) — chỉ có dòng "không đối chiếu
    được số lượng" ở kênh vận hành của đúng lượt chụp đó;
  · cửa sổ từ mốc khởi điểm tới dòng nav_history đầu tiên: không có số dư đầu ⇒ liệt kê là
    "không kiểm được", phải đối chiếu tay với sao kê;
  · trôi chậm đã quá `DRIFT_WINDOWS` cửa sổ mà không ai xử lý: dòng "phần dư trôi" chỉ xét
    `DRIFT_WINDOWS` cửa sổ gần nhất.

NGƯỠNG: xem `THRESHOLD_PCT` bên dưới (đo trên 135 cửa sổ thật của hai tài khoản).

ĐÓNG MỘT CỬA SỔ — hai cách, đều do NGƯỜI ghi kèm bằng chứng:
  · đúng là nạp/rút ⇒ bản ghi deposit/withdraw có ngày + giờ rơi vào cửa sổ đó trong
    `data/account_cash_flows.json`; phần dư sau khi trừ số tiền khai phải về dưới ngưỡng (khai
    thiếu/thừa thì vẫn cảnh báo phần còn lại);
  · đã xem, không phải nạp/rút ⇒ một lời xác nhận trong FILE RIÊNG `data/cash_identity_acks.json`
    (xem `load_acks`): ghi đúng hai mốc chụp của cửa sổ, phần dư ĐÃ XEM (`acked_residual_vnd`), số
    lượng đổi ngoài lệnh đã xem, lý do, bằng chứng, người xác nhận, ngày. Lời xác nhận chỉ có hiệu lực khi
    phần dư đo được lệch số đã xem không quá ngưỡng — lệch hơn thì cửa sổ mở lại và nêu phần chênh.
    Bản ghi `market_only` của sổ dòng tiền KHÔNG đóng được cửa sổ nào ở đây (nó không mang số tiền
    nên từng che được khoản nạp bất kỳ cùng ngày).

AI THẤY GÌ: báo cáo gửi nhà đầu tư chỉ mang MỘT dòng trung tính (`investor_line`), và chỉ khi còn
cửa sổ chưa đóng. Chi tiết đầy đủ đi kênh vận hành: trường `cash_flow_warnings` của
`nav_snapshot_<TK>_<ngày>.json`, CLI dưới đây, và tin nhắn Trading Daily của lượt chụp (chỉ chi
tiết cửa sổ kết thúc ĐÚNG ngày đang chụp; cửa sổ cũ gộp một dòng đếm).

Dùng:
    python3 mike/bin/cash_identity.py --account SpaceX              # bảng phần dư + cửa sổ đang mở
    python3 mike/bin/cash_identity.py --account SpaceX --json
  rc: 0 = không có gì đang mở · 3 = CÓ cửa sổ đang mở / phần dư trôi · 1 = không chạy được.
    python3 mike/bin/cash_identity.py --account SpaceX --notify-snapshot 2026-10-12   # lượt cron gọi
Selfcheck: python3 mike/bin/cash_identity_selfcheck.py
"""
import argparse
import csv
import datetime
import json
import math
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from account_cash_flows import SESSION_CLOSE_ICT, flow_moment, load_flows  # noqa: E402
from corp_actions import load_corp_actions  # noqa: E402
from dnse_fee_rates import FEE_RATE_BUY_PCT, FEE_RATE_SELL_PCT, SELL_TAX_RATE  # noqa: E402
from wc_paths import find_wc_root  # noqa: E402

WC_ROOT = find_wc_root(__file__)
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
INCEPTION_PATH = os.path.join(WC_ROOT, "data", "account_inception.json")
SEED_PATH = os.path.join(WC_ROOT, "data", "account_seed_capital.json")
ACKS_PATH = os.path.join(WC_ROOT, "data", "cash_identity_acks.json")
CORP_ACTIONS_PATH = os.path.join(WC_ROOT, "data", "corp_actions.json")
NOTIFY_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notify_thread.sh")
ICT = ZoneInfo("Asia/Ho_Chi_Minh")

# Lãi Trứng vàng theo NGÀY LỊCH. Đo trên 80 cửa sổ không có chuyển tiền ↔ Trứng vàng của cả hai
# tài khoản (2026-08-19 → 2026-10-12): Σ mức tăng / Σ (số dư × số ngày) = 0,023397%/ngày
# (≈8,54%/năm), từng cửa sổ nằm trong 0,02333%–0,02343%. DNSE đổi lãi suất ⇒ sai số = số dư ×
# chênh lãi × số ngày (500tr, lệch 1 điểm %/năm, 1 ngày ≈ 13,7 nghìn đồng ≈ 0,0014% NAV) — nhỏ hơn
# ngưỡng hai bậc ở TỪNG cửa sổ nhưng cộng dồn thì không: dòng "phần dư trôi" (`DRIFT_WINDOWS`) là
# chỗ báo hằng số này đã cũ. Selfcheck ghim nó bằng một cửa sổ THẬT đóng băng.
EGG_DAILY_RATE = 0.00023397
# Thuế TNCN cổ tức tiền mặt, DNSE khấu trừ lúc CHI TRẢ (phải thu ghi gộp) — đo: ZaloPay 2026-09-25
# chi trả 80.000.000 ⇒ totalCash giảm 4.002.556 (5% = 4.000.000).
DIVIDEND_TAX_RATE = 0.05
# Chỉ để ƯỚC LƯỢNG ứng viên "lãi vay ghi dồn" (không vào đẳng thức): 12,5%/năm theo user, chưa đối
# chiếu hợp đồng DNSE — cùng giả định với `reconcile_equity.py --margin-rate-annual`. Đo 5 cửa sổ
# có dư nợ lớn của SpaceX (07-03 → 07-09): 410tr/1 ngày −135k (≈12,0%/năm) nhưng 410tr/3 ngày chỉ
# −142k và 189tr/1 ngày ≈ 0 ⇒ DNSE KHÔNG ghi đều theo ngày, chưa mô hình hoá được.
MARGIN_RATE_ANNUAL_NOTE = 0.125
# Một kỳ ghi dồn lãi vay dài tối đa bao nhiêu ngày khi xét ứng viên nội bộ (một tháng + lề).
MARGIN_POSTING_DAYS = 35

# Rút Trứng vàng trước hạn bị khấu trừ lãi. NẰM TRONG đẳng thức từ vòng 2 (không có nó thì rút từ
# ~231tr ZaloPay / ~245tr SpaceX là vượt ngưỡng). Đo 2 lần rút thật ngày 2026-09-17, cùng gửi 29
# ngày: SpaceX mất 100.576 trên 49,95tr rút (0,2014%), ZaloPay 62.839 trên 31,22tr (0,2013%). Hai
# lần cùng thời gian gửi nên CHƯA phân biệt được "0,2% số rút" với "khấu trừ theo số ngày đã gửi" —
# chưa đối chiếu biểu phí DNSE. Vì thế: khoản khấu trừ ước tính mà TỰ NÓ lớn hơn ngưỡng thì cửa sổ
# được nhắc một lần ở kênh vận hành để người đo lại, và phần lệch khỏi ước tính tới
# `EGG_WITHDRAW_COST_CAP` số rút là ứng viên nội bộ chứ không gọi là rút tiền.
EGG_WITHDRAW_COST = 0.002013
EGG_WITHDRAW_COST_CAP = 0.01
# Trần để coi phần dư DƯƠNG là ứng viên "cổ tức tiền mặt ghi và chi trả trong cùng một cửa sổ"
# (đẳng thức không thấy loại này vì phải thu về 0 ở cả hai đầu): cổ tức gộp ≤ 15% giá trị cổ phiếu
# đầu cửa sổ. CHƯA có ca thật nào để đo — chỉ đổi NHÃN của dòng vận hành, không đóng cửa sổ.
DIVIDEND_SAME_WINDOW_CAP = 0.15

# NGƯỠNG: |phần dư chưa giải thích| > THRESHOLD_PCT % NAV đầu cửa sổ.
# Đo trên TOÀN BỘ lịch sử hai tài khoản tới 2026-10-12 — 135 cửa sổ (SpaceX 69, ZaloPay 66), sổ
# dòng tiền rỗng, |phần dư| theo % NAV: trung vị 0,0000 · p90 0,0066 · p95 0,0115 · p99 0,0543 ·
# max 0,1124; số cửa sổ vượt 0,005/0,01/0,02/0,05/0,1 = 18/11/4/2/1.
# Chọn 0,05 vì đó là cận dưới của dải PHẢI SỬA theo chính sách (điểm 4: lệch < 0,05% NAV thì không
# đính chính) — ngưỡng cao hơn để lại một dải mù mà chính sách buộc sửa. Biên so với nhiễu thật
# là ~1,7 lần, KHÔNG rộng: hai cửa sổ dưới ngưỡng lớn nhất đạt 0,0294% (SpaceX 07-31→08-03) và
# 0,0217% (ZaloPay 08-27→08-28).
# Hai cửa sổ lịch sử vượt ngưỡng đều của SpaceX và đều KHÔNG phải nạp/rút: dòng 07-02 chụp giữa
# loạt lệnh khớp sáng go-live; cửa sổ 08-27→08-28 là tiền đổi thành cổ phiếu (MBB +110 cp, giá vốn
# tăng đúng 110 × 10.000 đ; ZaloPay cùng ngày +20 cp) — chưa xác minh bằng nguồn ngoài rằng đó là
# quyền mua. Chi tiết từng ngày: `agents/Taylor/research/fund_cashflow_detect_20261012/`.
THRESHOLD_PCT = 0.05
THIN_DAYS = 30                    # cửa sổ thiếu bằng chứng còn được nhắc trong dòng đếm hằng tối (ngày)
# Trôi tích luỹ: tổng phần dư (% NAV) của `DRIFT_WINDOWS` cửa sổ gần nhất — chỉ cộng cửa sổ kiểm
# được và không đang mở/đã xác nhận riêng — vượt `THRESHOLD_PCT` ⇒ một dòng "phần dư trôi". Trên
# lịch sử thật tới 2026-10-12 tổng trượt lớn nhất là 0,046% (SpaceX) / 0,025% (ZaloPay): chưa lần
# nào vượt.
DRIFT_WINDOWS = 20
WARNING_MARKER = "DÒNG TIỀN CHỜ KHAI"
DRIFT_MARKER = "phần dư trôi có hệ thống"
INVESTOR_MARKER = "biến động tiền chưa đối chiếu xong"
SENT_PREFIX = "đã gửi"
LABEL_QUANTITY = "không kết luận được"
LABEL_INTERNAL = "cần xác nhận khoản nội bộ"
LABEL_EXTERNAL = "nghi nạp/rút chưa khai"


_ERRNO_RE = re.compile(r"\[Errno -?\d+\] ?")


class CashIdentityError(ValueError):
    """Không dựng được đẳng thức (thiếu/hỏng nguồn) — thông điệp trích đúng thứ đã đọc (§29)."""


def _err(exc):
    """Lỗi → chuỗi cho dòng cảnh báo: tên lớp + thông điệp, bỏ cụm "[Errno N]" và không dùng dạng
    "TênLỗi:" — hai dạng đó khớp `ERROR_RE` của `cron_health_check.py`, mà dòng này đi vào log cron
    mỗi tối cho tới khi có người xử lý (một cảnh báo không được biến thành ERRORS_FOUND hằng ngày)."""
    return f"{type(exc).__name__} ({_ERRNO_RE.sub('', str(exc))})"


def _d(value):
    """1107515.4 → "1.107.515 đ" (viết "đ", không "VND": cụm "VND" đứng trước một phần trăm có dấu
    bị cổng tỉ suất đọc thành tỉ suất của mã VND)."""
    return f"{value:,.0f}".replace(",", ".") + " đ"


def _sd(value):
    return f"{value:+,.0f}".replace(",", ".") + " đ"


def _vn(value, digits=1):
    """12.5 → "12,5" (thập phân dấu phẩy, không dấu)."""
    return f"{abs(value):.{digits}f}".replace(".", ",")


def _pct(value):
    """Phần trăm KHÔNG dấu (chiều đã nằm ở số tiền có dấu đứng trước nó)."""
    return _vn(value, 3) + "% NAV"


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
                       "mtm": _num(rec.get("mtm_stock")),
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
    Mỗi file chỉ đọc một lần; bản ghi không thuộc `account_no` bị loại ngay ở dòng đầu. Mọi giá trị
    được chuẩn hoá về số/thời điểm NGAY lúc đọc: bản ghi sai kiểu không làm hỏng lượt chạy mà được
    ghi lại ở `problems` (số dòng + lỗi) để chỉ những cửa sổ chạm ngày đó thành "không kiểm được"."""

    KINDS = ("balances", "orders", "place_order", "positions")

    def __init__(self, account_no, raw_dir=None):
        self.account_no = str(account_no)
        self.raw_dir = raw_dir or EXEC_DIR
        self._days = {}

    def path(self, date):
        return os.path.join(self.raw_dir, f"dnse_raw_{date.isoformat()}.jsonl")

    def day(self, date):
        """`{"exists", "balances": [(lúc, phải thu cổ tức | None)], "positions": [(lúc, {mã: (KL,
        giá thị trường | None)})], "orders": {mã lệnh: lệnh mới nhất đã chuẩn hoá},
        "n_order_records", "problems": [(số dòng, lỗi)]}` của một ngày."""
        if date in self._days:
            return self._days[date]
        out = {"exists": False, "balances": [], "positions": [], "orders": {}, "n_order_records": 0,
               "problems": []}
        path = self.path(date)
        if os.path.exists(path):
            out["exists"] = True
            with open(path, "r", encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if not any(f'"{kind}"' in line for kind in self.KINDS):
                        continue
                    try:
                        self._ingest(out, json.loads(line))
                    except (ValueError, TypeError, AttributeError, KeyError) as exc:
                        # Không biết bản ghi hỏng là của ai ⇒ tính cho mọi tài khoản (thiếu bằng
                        # chứng ≠ sạch); bản ghi gắn rõ tài khoản KHÁC đã bị loại trước khi chạm payload.
                        out["problems"].append((lineno, _err(exc)))
        self._days[date] = out
        return out

    def _ingest(self, out, rec):
        tag = rec.get("account_no")
        if tag is not None and str(tag) != self.account_no:
            return                                  # §12: bản ghi của tài khoản khác
        kind = rec.get("kind")
        if kind not in self.KINDS:
            return                                  # tên loại chỉ tình cờ nằm trong nội dung dòng
        payload = rec.get("payload") or {}
        if not isinstance(payload, dict):
            raise TypeError(f"payload của bản ghi {kind} là {type(payload).__name__}, không phải object")
        if kind == "balances":
            if tag is None:
                return                              # không gắn tài khoản ⇒ không đoán là của ai
            value = (payload.get("stock") or {}).get("cashDividendReceiving")
            out["balances"].append((_parse_ts(rec.get("ts")), None if value is None else _num(value)))
        elif kind == "positions":
            mine = {}
            for p in payload.get("positions") or []:
                if str(p.get("accountNo")) != self.account_no:
                    continue
                price = p.get("marketPrice")
                qty, old = _num(p.get("openQuantity")), mine.get(p.get("symbol"), (0.0, None))
                mine[p.get("symbol")] = (old[0] + qty, old[1] if price is None else _num(price))
            if tag is not None or mine:
                out["positions"].append((_parse_ts(rec.get("ts")), mine))
        else:
            orders = (payload.get("orders") or [] if kind == "orders" else [payload.get("resp") or {}])
            mine = {}
            for o in orders:
                # Lệnh mang accountNo riêng: bản ghi cũ (trước 2026-07-06) không gắn tài khoản ở
                # ngoài nên phải lọc theo từng lệnh.
                if o.get("id") is None or str(o.get("accountNo")) != self.account_no:
                    continue
                try:
                    moment = _parse_broker_utc(o.get("modifiedDate") or o.get("createdDate"))
                except (TypeError, ValueError):
                    moment = None                   # không đọc được giờ ⇒ `fills_between` gán giờ đóng cửa
                qty = _num(o.get("fillQuantity"))
                mine[o["id"]] = {
                    "symbol": o.get("symbol"), "qty": qty, "moment": moment,
                    "side": "sell" if str(o.get("side") or "").upper().startswith("NS") else "buy",
                    "value": qty * _num(o.get("averagePrice") or o.get("price"))}
            out["orders"].update(mine)              # bản ghi sau (mới hơn) đè bản ghi trước của cùng lệnh
            out["n_order_records"] += 1 if (mine or tag is not None) else 0

    def problems_between(self, date0, date1):
        """Bản ghi không đọc được trong các file từ `date0` tới `date1`: [(đường dẫn, số dòng, lỗi)]."""
        out, day = [], date0
        while day <= date1:
            out.extend((self.path(day), lineno, msg) for lineno, msg in self.day(day)["problems"])
            day += datetime.timedelta(days=1)
        return out

    def receivable_at(self, snap):
        """`cashDividendReceiving` ở bản ghi balances chụp ĐÚNG lúc `snap` (chính bản ghi mà
        `daily_nav_snapshot.py` đã dùng); không có bản đúng giây thì bản mới nhất trước đó trong
        ngày. Không có bản nào, hoặc bản đó thiếu field ⇒ `None` (thiếu bằng chứng, KHÔNG coi là 0)."""
        best = None
        for at, value in self.day(snap.date())["balances"]:
            if at <= snap and (best is None or at >= best[0]):
                best = (at, value)
        return None if best is None else best[1]

    def positions_at(self, snap):
        """{mã: (KL đang giữ, giá thị trường | None)} ở bản ghi positions mới nhất KHÔNG lệch `snap`
        quá 10 phút về cả hai phía (positions và balances được ghi cách nhau vài giây). Không có bản
        nào trong khoảng đó ⇒ `None` (không đối chiếu được) — KHÔNG lấy bản ghi buổi sáng thay cho
        bản buổi tối (arch-review vòng 2, N3: ca mua tay 10:00 kèm nạp tiền báo sạch)."""
        best = None
        gap = datetime.timedelta(minutes=10)
        for at, positions in self.day(snap.date())["positions"]:
            if snap - gap <= at <= snap + gap and (best is None or at >= best[0]):
                best = (at, positions)
        return None if best is None else best[1]

    def fills_between(self, snap0, snap1):
        """Lệnh có khớp với lần cập nhật cuối trong (snap0, snap1]. Trả list dict {moment, symbol,
        side ("buy"/"sell"), qty, value}. Lệnh không đọc được giờ ⇒ coi như khớp lúc đóng cửa của
        ngày file (ngày giao dịch của nó)."""
        out = []
        day = snap0.date()
        while day <= snap1.date():
            for o in self.day(day)["orders"].values():
                if o["qty"] <= 0:
                    continue
                moment = o["moment"] or datetime.datetime.combine(day, SESSION_CLOSE_ICT)
                if snap0 < moment <= snap1:
                    out.append(dict(o, moment=moment))
            day += datetime.timedelta(days=1)
        return out


def load_account(account, inception_path=None):
    """`{"account_no", "inception_date" | None}` từ `data/account_inception.json`."""
    path = inception_path or INCEPTION_PATH
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if not isinstance(cfg, dict) or not isinstance(cfg.get(account), dict) \
            or not cfg[account].get("account_no"):
        raise CashIdentityError(f"{path}: không có account_no cho '{account}'")
    start = cfg[account].get("inception_date")
    return {"account_no": str(cfg[account]["account_no"]),
            "inception_date": datetime.date.fromisoformat(start) if start else None}


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


def load_rights_subscription_fills(account, account_no=None, path=None):
    """N1: CP quyền mua USER đã khai (`rights_subscription.py`) — cùng dạng fill broker xác nhận,
    `fee_free` (nộp tiền mua quyền không chịu phí giao dịch). Sổ hỏng ⇒ raise (fail-closed)."""
    import rights_subscription as rights_sub
    out = []
    for d, evs in rights_sub.fill_events(account, path=path, account_no=account_no).items():
        day = datetime.date.fromisoformat(d)
        for _ts, key, tk, _side, qty, px in evs:
            out.append({"moment": datetime.datetime.combine(day, SESSION_CLOSE_ICT), "symbol": tk,
                        "side": "buy", "qty": qty, "value": qty * px, "fee_free": True, "key": key})
    return out


def _ack_text(rec, key, where):
    value = rec.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}: thiếu `{key}` (chuỗi không rỗng)")
    return value.strip()


def _validate_ack(rec, where):
    if not isinstance(rec, dict) or not isinstance(rec.get("window"), dict):
        raise ValueError(f"{where}: phải là object có `window` {{from, to}}")
    residual = rec.get("acked_residual_vnd")
    if isinstance(residual, bool) or not isinstance(residual, (int, float)) or not math.isfinite(residual):
        raise ValueError(f"{where}: `acked_residual_vnd` phải là số hữu hạn, được {residual!r}")
    gaps = rec.get("acked_qty_gaps", {})
    if not isinstance(gaps, dict) or any(
            isinstance(q, bool) or not isinstance(q, (int, float)) or not math.isfinite(q) or not q
            for q in gaps.values()):
        raise ValueError(f"{where}: `acked_qty_gaps` phải là {{mã: số lượng khác 0}}, được {gaps!r}")
    try:
        start, end = _parse_ts(rec["window"].get("from")), _parse_ts(rec["window"].get("to"))
        datetime.date.fromisoformat(_ack_text(rec, "confirmed_date", where))
    except ValueError as exc:
        raise ValueError(f"{where}: mốc `window.from`/`window.to`/`confirmed_date` không đọc được ({exc})") from exc
    return {"from": start, "to": end, "acked_residual_vnd": float(residual),
            "acked_qty_gaps": {str(s): float(q) for s, q in gaps.items()},
            "reason": _ack_text(rec, "reason", where),
            "evidence": _ack_text(rec, "evidence", where),
            "confirmed_by": _ack_text(rec, "confirmed_by", where),
            "confirmed_date": rec["confirmed_date"]}


def load_acks(account, acks_path=None):
    """Lời xác nhận "đã xem, không phải nạp/rút" của `account` → `(list, lỗi | None)`.

    SCHEMA `data/cash_identity_acks.json` — `{"<tài khoản>": [bản ghi, …]}`, mỗi bản ghi:
      - `window`: `{"from": balance_ts dòng trước, "to": balance_ts dòng sau}` — ĐÚNG hai mốc chụp
        của cửa sổ như trong nav_history (dòng bị chụp lại thì lời xác nhận cũ hết hiệu lực);
      - `acked_residual_vnd`: phần dư chưa giải thích mà người xác nhận ĐÃ XEM (có dấu);
      - `acked_qty_gaps`: `{mã: số lượng}` đổi ngoài lệnh đã xem (bỏ trống = không có);
      - `reason`, `evidence`, `confirmed_by`, `confirmed_date` (YYYY-MM-DD): bắt buộc, không rỗng.
    File vắng mặt = chưa có lời xác nhận nào (bình thường). File hỏng hoặc có MỘT bản ghi sai ⇒
    coi như không có lời xác nhận nào và trả lỗi nêu file + thứ đã đọc: xác nhận sai dạng không
    được âm thầm đóng cửa sổ, và cũng không được làm hỏng lượt chụp NAV."""
    path = acks_path or ACKS_PATH
    if not os.path.exists(path):
        return [], None
    try:
        with open(path, "r", encoding="utf-8") as f:
            blob = json.load(f)
        if not isinstance(blob, dict):
            raise ValueError(f"gốc phải là object {{tài khoản: [...]}}, được {type(blob).__name__}")
        recs = blob.get(account, [])
        if not isinstance(recs, list):
            raise ValueError(f"mục '{account}' phải là list, được {type(recs).__name__}")
        return [_validate_ack(rec, f"{account}[{i}]") for i, rec in enumerate(recs)], None
    except (OSError, ValueError) as exc:
        return [], f"{path} không dùng được nên KHÔNG lời xác nhận nào có hiệu lực — {_err(exc)}"


def load_share_credits(corp_actions_path=None):
    """Sự kiện làm TĂNG số lượng đã được ký (`corp_actions.load_corp_actions`) → `(list, lỗi | None)`.
    Sổ hỏng ⇒ coi như không có sự kiện nào (mọi số lượng đổi ngoài lệnh thành "không kết luận
    được") và trả lỗi nêu file — không làm hỏng đẳng thức."""
    path = corp_actions_path or CORP_ACTIONS_PATH
    try:
        return [dict(a, effective=_parse_ts(a["broker_effective_ts"])) for a in load_corp_actions(path)], None
    except Exception as exc:                # noqa: BLE001 — nguồn phụ: lỗi của nó thành một dòng cảnh báo
        return [], (f"{path} không dùng được nên số lượng đổi do cổ phiếu thưởng/cổ tức cổ phiếu "
                    f"KHÔNG được giải thích — {_err(exc)}")


def _reconcile_quantities(raw, snap0, snap1, fills, share_credits, mtm0=0.0, mtm1=0.0):
    """Số lượng vị thế đổi giữa hai lần chụp có bằng đúng lệnh đã đọc + cổ phiếu thưởng đã ký không.
    Trả `(gaps, values, unverified, credited)`: `gaps` = {mã: số lượng dư}, `values` = {mã: giá trị
    ước tính theo giá thị trường của bản ghi vị thế | None}, `unverified` = lý do không đối chiếu
    được (None nếu đối chiếu được), `credited` = ghi chú các khoản dư đã khớp sự kiện đã ký."""
    p0, p1 = raw.positions_at(snap0), raw.positions_at(snap1)
    # Bản ghi vị thế RỖNG trong khi dòng nav_history có cổ phiếu = lỗi đọc của broker (đã thấy thật:
    # dnse_raw_2026-08-20 SpaceX 19:07:16 có 0 vị thế kẹp giữa các bản ghi 27 vị thế), KHÔNG phải
    # "không giữ mã nào" — coi là không đọc được (arch-review vòng 2, N4).
    if p0 == {} and mtm0 > 0:
        p0 = None
    if p1 == {} and mtm1 > 0:
        p1 = None
    if p0 is None or p1 is None:
        return {}, {}, ("không đọc được vị thế ở "
                        + " và ".join(f"lần chụp {s}" for s, p in ((snap0, p0), (snap1, p1)) if p is None)
                        + " (quanh lúc đó dnse_raw không có bản ghi positions, hoặc bản ghi rỗng trong khi NAV có cổ phiếu)"), []
    net = {}
    for fx in fills:
        net[fx["symbol"]] = net.get(fx["symbol"], 0.0) + (fx["qty"] if fx["side"] == "buy" else -fx["qty"])
    gaps, values, credited = {}, {}, []
    for symbol in sorted(set(p0) | set(p1) | set(net), key=str):
        q0 = p0.get(symbol, (0.0, None))[0]
        gap = p1.get(symbol, (0.0, None))[0] - q0 - net.get(symbol, 0.0)
        if abs(gap) < 1e-6:
            continue
        # Cổ phiếu thưởng/cổ tức cổ phiếu ĐÃ KÝ: broker ghi có trong cửa sổ và số tăng bằng đúng
        # KL đầu cửa sổ × (hệ số − 1), bỏ phần lẻ (đo 16/16 lần thật của hai tài khoản).
        event = next((a for a in share_credits
                      if a["ticker"] == symbol and snap0 < a["effective"] <= snap1
                      and 0 <= q0 * (a["qty_multiplier"] - 1) - gap + 1e-6 < 1), None)
        if event is not None:
            credited.append(f"{_gap_text({symbol: gap})} khớp sự kiện đã ký {event['id']}")
            continue
        price = p1.get(symbol, (0.0, None))[1] or p0.get(symbol, (0.0, None))[1]
        gaps[symbol], values[symbol] = gap, (gap * price if price else None)
    return gaps, values, None, credited


def _silent_days(raw, snap0, snap1):
    day, silent = snap0.date(), []
    while day <= snap1.date():
        info = raw.day(day)
        if day.weekday() < 5 and not info["n_order_records"]:
            silent.append(f"{day}" + ("" if info["exists"] else " (không có file)"))
        day += datetime.timedelta(days=1)
    return silent


def _internal_candidates(win, prev, cur):
    """Khoản NỘI BỘ không mô hình hoá mà bằng chứng đã đọc chưa loại trừ được và độ lớn hợp lý
    của nó phủ được phần dư — có ⇒ dòng cảnh báo nói "cần xác nhận khoản nội bộ", không gọi là
    nạp/rút. Chỉ đổi NHÃN: cửa sổ vẫn mở cho tới khi người khai hoặc xác nhận."""
    out, gap = [], win["unexplained"]
    debt = max(prev["debt"], cur["debt"])
    if gap < 0 and debt > 0:
        cap = debt * MARGIN_RATE_ANNUAL_NOTE * MARGIN_POSTING_DAYS / 365
        if -gap <= cap:
            out.append(f"lãi vay ký quỹ DNSE ghi dồn (dư nợ {_d(debt)}; một kỳ {MARGIN_POSTING_DAYS} "
                       f"ngày ở {_vn(MARGIN_RATE_ANNUAL_NOTE * 100)}%/năm tối đa khoảng {_d(cap)})")
    if gap < 0 and win["egg_out"] > 0 and -gap <= win["egg_out"] * EGG_WITHDRAW_COST_CAP:
        out.append(f"khấu trừ rút Trứng vàng lớn hơn mức đã đo (rút {_d(win['egg_out'])}, đã tính "
                   f"{_d(win['egg_cost'])}; hằng số mới đo một lần ở kỳ gửi 29 ngày)")
    if gap > 0 and prev["mtm"] > 0:
        gross = gap / (1 - DIVIDEND_TAX_RATE)
        if gross <= prev["mtm"] * DIVIDEND_SAME_WINDOW_CAP:
            out.append(f"cổ tức tiền mặt ghi và chi trả trong cùng cửa sổ (không đi qua phải thu) — "
                       f"ứng với cổ tức gộp khoảng {_d(gross)}, bằng {_vn(gross / prev['mtm'] * 100)}% "
                       f"giá trị cổ phiếu đầu cửa sổ")
    return out


def build_windows(rows, raw, flows, extra_fills=(), threshold_pct=THRESHOLD_PCT, acks=(),
                  share_credits=()):
    """Đẳng thức tiền cho từng cặp dòng nav_history liên tiếp. Trả list dict, mỗi cửa sổ một dòng:
    date0/date1, snap0/snap1, nav0, delta_k, sell, buy, n_fills, fees, dividend, egg_interest,
    egg_out, egg_cost, residual (= delta_k − các khoản nội bộ), declared (nạp/rút đã khai rơi vào
    cửa sổ), unexplained (= residual − declared), pct_nav, over (vượt ngưỡng), qty_gaps/qty_values/
    qty_unverified (đối chiếu số lượng), kind (nhãn khi cần người xem), acked/ack_mismatch,
    suspect (= ĐANG MỞ: cần người xem và chưa có lời xác nhận khớp), info, notes.
    Cửa sổ có đầu mút không rõ lúc chụp, hoặc chạm một file dnse_raw có bản ghi không đọc được ⇒
    `checkable=False` kèm lý do, không tính số nào."""
    money = [(flow_moment(f)[0], f) for f in flows if f["kind"] != "market_only"]
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
        if not bad:
            broken = raw.problems_between(prev["snap"].date(), cur["snap"].date())
            if broken:
                bad = [f"{len(broken)} bản ghi dnse_raw không đọc được nên lệnh khớp/vị thế/phải thu "
                       f"của cửa sổ này không đủ tin: "
                       + "; ".join(f"{path} dòng {lineno} — {msg}" for path, lineno, msg in broken[:3])
                       + (f"; … và {len(broken) - 3} bản ghi nữa" if len(broken) > 3 else "")]
        if bad:
            win.update(checkable=False, suspect=False, reason="; ".join(bad))
            continue
        snap0, snap1 = prev["snap"], cur["snap"]
        fills = raw.fills_between(snap0, snap1) + [
            fx for fx in extra_fills if snap0 < fx["moment"] <= snap1]
        sell = sum(fx["value"] for fx in fills if fx["side"] == "sell")
        buy = sum(fx["value"] for fx in fills if fx["side"] == "buy")
        buy_fee_base = sum(fx["value"] for fx in fills if fx["side"] == "buy" and not fx.get("fee_free"))
        fees = (buy_fee_base * FEE_RATE_BUY_PCT / 100 + sell * FEE_RATE_SELL_PCT / 100
                + sell * SELL_TAX_RATE)
        recv0, recv1 = raw.receivable_at(snap0), raw.receivable_at(snap1)
        if recv0 is None or recv1 is None:
            dividend = 0.0
            win["notes"].append(
                "không đọc được cashDividendReceiving ở "
                + " và ".join(f"lần chụp {s}" for s, r in ((snap0, recv0), (snap1, recv1)) if r is None)
                + " (dnse_raw không có bản ghi balances gắn tài khoản này mang field đó) ⇒ cổ tức tính 0")
        else:
            delta = recv1 - recv0
            dividend = delta if delta >= 0 else delta * DIVIDEND_TAX_RATE
        days = (snap1.date() - snap0.date()).days
        egg_interest = prev["egg"] * EGG_DAILY_RATE * days
        egg_out = prev["egg"] + egg_interest - cur["egg"]
        if egg_out <= prev["egg"] * EGG_DAILY_RATE * max(days, 1):  # chưa tới mức lãi của chính cửa sổ
            egg_out = 0.0                                            # = sai số lãi suất, không phải rút
        egg_cost = egg_out * EGG_WITHDRAW_COST
        delta_k = cur["k"] - prev["k"]
        residual = delta_k - (sell - buy - fees + dividend + egg_interest - egg_cost)
        declared = [f for at, f in money if snap0 < at <= snap1]
        declared_vnd = sum(f["amount_vnd"] for f in declared)
        unexplained = residual - declared_vnd
        tol = prev["nav"] * threshold_pct / 100
        gaps, values, unverified, credited = _reconcile_quantities(
            raw, snap0, snap1, fills, share_credits, prev["mtm"], cur["mtm"])
        win.update(delta_k=delta_k, sell=sell, buy=buy, n_fills=len(fills), fees=fees,
                   dividend=dividend, egg_interest=egg_interest, egg_out=egg_out, egg_cost=egg_cost,
                   residual=residual, declared=declared_vnd, declared_flows=declared,
                   unexplained=unexplained, pct_nav=unexplained / prev["nav"] * 100,
                   over=abs(unexplained) > tol, qty_gaps=gaps, qty_values=values,
                   qty_unverified=unverified, kind=None, acked=None, ack_mismatch=[], info=None)
        win["notes"].extend(credited)
        if unverified:
            win["notes"].append(f"{unverified} ⇒ KHÔNG đối chiếu được số lượng cổ phiếu với lệnh khớp; "
                                f"lệnh đặt ngoài bot trong cửa sổ này (nếu có) không được thấy")
        debt = max(prev["debt"], cur["debt"])
        if debt > 0:
            win["notes"].append(
                f"có dư nợ ký quỹ ({_d(prev['debt'])} → {_d(cur['debt'])}); lãi vay ước "
                f"{_d(debt * MARGIN_RATE_ANNUAL_NOTE / 365 * max(days, 1))} cho {max(days, 1)} ngày "
                f"KHÔNG nằm trong đẳng thức (DNSE không ghi đều theo ngày)")
        if egg_out:
            win["notes"].append(
                f"Trứng vàng rút ròng {_d(egg_out)} trong cửa sổ; đã tính khấu trừ rút trước hạn "
                f"{_d(egg_cost)} vào đẳng thức (ước tính — hằng số đo một lần ngày 2026-09-17)")
        if prev["offbook"] or cur["offbook"]:
            win["notes"].append(
                f"có tài sản off-book khai tay ({_d(prev['offbook'])} → {_d(cur['offbook'])}) — "
                f"số do người báo, không đọc được từ broker")
        if gaps:
            win["kind"] = LABEL_QUANTITY
        elif win["over"]:
            win["candidates"] = _internal_candidates(win, prev, cur)
            win["kind"] = LABEL_INTERNAL if win["candidates"] else LABEL_EXTERNAL
        elif egg_cost > tol:
            # Đẳng thức khép CHỈ nhờ một ước tính lớn hơn cả ngưỡng mà hằng số mới đo một lần ⇒
            # nhắc một lần ở kênh vận hành (không mở cửa sổ, không vào báo cáo nhà đầu tư).
            win["info"] = (f"{LABEL_INTERNAL}: rút Trứng vàng {_d(egg_out)}, đẳng thức khép nhờ khoản "
                           f"khấu trừ ƯỚC TÍNH {_d(egg_cost)} ({_pct(egg_cost / prev['nav'] * 100)}, "
                           f"lớn hơn ngưỡng) — đối chiếu số thật trên sao kê để đo lại hằng số")
        if win["kind"]:
            silent = _silent_days(raw, snap0, snap1)
            if silent:
                win["notes"].append("dnse_raw KHÔNG có bản ghi orders nào của tài khoản các ngày "
                                    + ", ".join(silent) + " ⇒ lệnh đặt ngoài bot những ngày đó "
                                    "không được thấy ở đây")
            matching = [a for a in acks if a["from"] == snap0 and a["to"] == snap1]
            if len(matching) > 1:
                win["ack_mismatch"].append(f"có {len(matching)} lời xác nhận cho cùng cửa sổ — không biết dùng cái nào")
            elif matching:
                ack = matching[0]
                drift = unexplained - ack["acked_residual_vnd"]
                if abs(drift) > tol:
                    win["ack_mismatch"].append(
                        f"phần dư đo được {_sd(unexplained)} lệch {_sd(drift)} so với số đã xác nhận "
                        f"{_sd(ack['acked_residual_vnd'])} (ngày {ack['confirmed_date']}, {ack['confirmed_by']})")
                if gaps != ack["acked_qty_gaps"]:
                    win["ack_mismatch"].append(
                        f"số lượng đổi ngoài lệnh đo được {_gap_text(gaps) or 'không có'} khác số đã "
                        f"xác nhận {_gap_text(ack['acked_qty_gaps']) or 'không có'}")
                if not win["ack_mismatch"]:
                    win["acked"] = ack
        win["suspect"] = bool(win["kind"]) and win["acked"] is None
    return windows


def _gap_text(gaps):
    return ", ".join(f"{symbol} {qty:+,.0f} cp".replace(",", ".") for symbol, qty in sorted(gaps.items()))


def drift_of(windows, rows_by_date, threshold_pct=THRESHOLD_PCT):
    """Tổng phần dư của `DRIFT_WINDOWS` cửa sổ gần nhất (chỉ cửa sổ kiểm được, không cần người xem
    riêng) vượt ngưỡng ⇒ dict mô tả; không ⇒ None. Bắt thứ mà ngưỡng từng cửa sổ không thấy: khoản
    nhỏ lặp lại, hoặc một hằng số của đẳng thức đã cũ."""
    recent = [w for w in windows[-DRIFT_WINDOWS:] if w["checkable"] and not w["kind"]]
    total_pct = sum(w["pct_nav"] for w in recent)
    if not recent or abs(total_pct) <= threshold_pct:
        return None
    interest = sum(max(rows_by_date[w["date0"]]["debt"], rows_by_date[w["date1"]]["debt"])
                   * MARGIN_RATE_ANNUAL_NOTE / 365 * max((w["snap1"].date() - w["snap0"].date()).days, 1)
                   for w in recent)
    return {"date0": recent[0]["date0"], "date1": recent[-1]["date1"], "n_windows": len(recent),
            "sum_vnd": sum(w["unexplained"] for w in recent), "sum_pct": total_pct,
            "same_sign": sum(1 for w in recent if w["unexplained"] * total_pct > 0),
            "margin_interest_est": interest}


def check_account(account, asof=None, nav_dir=None, raw_dir=None, flows_path=None,
                  inception_path=None, seed_path=None, acks_path=None, corp_actions_path=None,
                  threshold_pct=THRESHOLD_PCT, today=None):
    """Dựng đẳng thức tiền của `account` trên toàn bộ nav_history tới `asof` (date, gồm cả ngày đó).
    Trả `{"account", "threshold_pct", "windows", "suspects" (cửa sổ ĐANG MỞ), "uncheckable",
    "baseline", "drift", "source_errors"}`. `baseline` = cửa sổ mốc khởi điểm → dòng nav_history
    đầu: luôn "không kiểm được", đứng đầu `uncheckable`, KHÔNG nằm trong `windows` (không có số
    nào để cộng)."""
    rows = load_nav_rows(account, nav_dir)
    if asof is not None:
        rows = [r for r in rows if r["date"] <= asof]
    info = load_account(account, inception_path)
    raw = RawLog(info["account_no"], raw_dir)
    flows = load_flows(account, flows_path=flows_path, require_file=True, today=today)
    acks, ack_error = load_acks(account, acks_path)
    credits, credit_error = load_share_credits(corp_actions_path)
    windows = build_windows(rows, raw, flows,
                            load_confirmed_missing_fills(account, seed_path)
                            + load_rights_subscription_fills(account, info["account_no"]),
                            threshold_pct, acks, credits)
    by_date = {r["date"]: r for r in rows}
    drift = drift_of(windows, by_date, threshold_pct)
    if drift:                               # lượt chụp trước đã thấy chưa (để không nhắc chi tiết mỗi tối)
        drift["new"] = drift_of(windows[:-1], by_date, threshold_pct) is None
    baseline = None
    if rows:
        baseline = {
            "date0": info["inception_date"], "date1": rows[0]["date"], "snap0": None,
            "snap1": rows[0]["snap"], "nav0": None, "checkable": False, "suspect": False,
            "baseline": True, "notes": [],
            "reason": "từ mốc khởi điểm tới dòng nav_history đầu tiên không có lần chụp số dư đầu "
                      "⇒ nạp/rút trong khoảng này phải đối chiếu tay với sao kê"}
    return {"account": account, "threshold_pct": threshold_pct, "windows": windows,
            "suspects": [w for w in windows if w["suspect"]], "baseline": baseline,
            "uncheckable": ([baseline] if baseline else []) + [w for w in windows if not w["checkable"]],
            "drift": drift, "source_errors": [e for e in (ack_error, credit_error) if e]}


def _span(win):
    def end(day, snap):
        return f"{day} ({snap:%d/%m %H:%M})" if snap else f"{day or 'mốc khởi điểm'}"
    return f"{end(win['date0'], win['snap0'])} → {end(win['date1'], win['snap1'])}"


def suspect_line(account, win):
    """Một dòng VẬN HÀNH tự đủ nghĩa cho một cửa sổ đang mở: nhãn, ngày, số tiền, bằng chứng đã
    đọc, cách đóng. KHÔNG dùng cho báo cáo gửi nhà đầu tư (xem `investor_line`)."""
    gap = win["unexplained"]
    if win["kind"] == LABEL_QUANTITY:
        parts, effect = [], 0.0
        for symbol, qty in sorted(win["qty_gaps"].items()):
            value = win["qty_values"][symbol]
            parts.append(f"{symbol} {qty:+,.0f} cp".replace(",", ".")
                         + (f" (khoảng {_d(abs(value))} theo giá thị trường)" if value is not None
                            else " (bản ghi vị thế không có giá ⇒ không ước được giá trị)"))
            if value is not None:                   # tiền của một lệnh mua (−) / bán (+) cỡ đó
                effect -= value * ((1 + FEE_RATE_BUY_PCT / 100) if qty > 0
                                   else (1 - FEE_RATE_SELL_PCT / 100 - SELL_TAX_RATE))
        what = ("số lượng cổ phiếu đổi mà lệnh đã đọc và sự kiện cổ phiếu đã ký không giải thích: "
                + ", ".join(parts))
        if all(v is not None for v in win["qty_values"].values()):
            what += (f"; nếu đó là lệnh đặt ngoài bot ở giá thị trường thì còn {_sd(gap - effect)} "
                     f"tiền vào/ra chưa giải thích")
        what += (f". Phần dư tiền {_sd(gap)} ({_pct(win['pct_nav'])}) vì thế KHÔNG chứng minh được là "
                 f"không có nạp/rút")
    elif win["kind"] == LABEL_INTERNAL:
        what = (f"phần dư {_sd(gap)} ({_pct(win['pct_nav'])}) chưa giải thích, nhưng chưa loại trừ "
                f"được: " + "; ".join(win["candidates"]) + ". Nếu không phải thì là tiền "
                + ("nạp vào" if gap > 0 else "rút ra") + " chưa khai")
    else:
        what = (f"phần dư {_sd(gap)} ({_pct(win['pct_nav'])}) không có khoản nội bộ nào đã đọc giải "
                f"thích được ⇒ nghi tiền " + ("NẠP vào" if gap > 0 else "RÚT ra")
                + " mà sổ dòng tiền chưa có bản ghi khớp")
    declared = f"; đã trừ {_sd(win['declared'])} dòng tiền đã khai trong cửa sổ" if win["declared"] else ""
    mismatch = ("; LỜI XÁC NHẬN KHÔNG CÒN KHỚP — " + "; ".join(win["ack_mismatch"])
                if win["ack_mismatch"] else "")
    return (f"⚠️ {WARNING_MARKER} ({account}) — {win['kind']}: cửa sổ {_span(win)}: {what}{mismatch}. "
            f"Đã đọc: tiền sở hữu đổi {_sd(win['delta_k'])}; {win['n_fills']} lệnh khớp (bán "
            f"{_d(win['sell'])}, mua {_d(win['buy'])}, phí+thuế {_d(win['fees'])}); cổ tức "
            f"{_sd(win['dividend'])}; lãi Trứng vàng {_sd(win['egg_interest'])}{declared}"
            + "".join(f"; {note}" for note in win["notes"])
            + ". Cách đóng: khai deposit/withdraw có giờ vào data/account_cash_flows.json, hoặc ghi "
              "lời xác nhận kèm bằng chứng vào data/cash_identity_acks.json với window = "
              f"{win['snap0'].isoformat()} → {win['snap1'].isoformat()}, acked_residual_vnd = {gap:.0f}"
            + (f", acked_qty_gaps = {json.dumps({s: q for s, q in sorted(win['qty_gaps'].items())})}"
               if win["qty_gaps"] else "")
            + ".")


def drift_line(account, drift):
    interest = (f"; trong đó có cửa sổ mang dư nợ ký quỹ — lãi vay ước {_d(drift['margin_interest_est'])} "
                f"KHÔNG nằm trong đẳng thức, có thể là nguyên nhân" if drift["margin_interest_est"] >= 1 else "")
    return (f"⚠️ {WARNING_MARKER} ({account}) — {DRIFT_MARKER}: {drift['n_windows']} cửa sổ gần nhất "
            f"({drift['date0']} → {drift['date1']}) cộng lại {_sd(drift['sum_vnd'])} "
            f"({_pct(drift['sum_pct'])}), {drift['same_sign']}/{drift['n_windows']} cửa sổ cùng chiều, "
            f"dù không cửa sổ nào tự vượt ngưỡng{interest}. Đo lại hằng số của đẳng thức (lãi Trứng "
            f"vàng, khấu trừ rút Trứng vàng, biểu phí) hoặc tìm khoản nhỏ lặp lại (nạp/rút nhỏ giọt, "
            f"phí định kỳ) trên sao kê.")


def uncheckable_line(account, win):
    return f"⚠️ Đẳng thức tiền ({account}) không kiểm được cửa sổ {_span(win)}: {win['reason']}"


def investor_line(result):
    """MỘT dòng trung tính cho báo cáo gửi nhà đầu tư, chỉ khi còn CỬA SỔ chưa đóng; không có ⇒
    None. Không tên file/field nội bộ, không khẳng định nạp/rút, không phần trăm có dấu. Dòng
    "phần dư trôi" KHÔNG vào đây: nó không gắn với cửa sổ nào nên không ai đóng được bằng một lời
    xác nhận — để nó ở báo cáo là tái lập dòng cảnh báo lặp vô hạn; nó đi kênh vận hành."""
    amounts = []
    for w in result["suspects"]:
        values = [abs(v) for v in w["qty_values"].values() if v is not None]
        amounts.append(max([abs(w["unexplained"])] + values))
    if not amounts:
        return None
    return (f"ℹ️ Có {len(amounts)} khoản {INVESTOR_MARKER} (lớn nhất {_d(max(amounts))}); tỉ suất kỳ "
            f"chứa ngày đó có thể được điều chỉnh.")


def report(account, asof=None, **paths):
    """Mọi thứ consumer hiển thị cần, KHÔNG BAO GIỜ ném:
      `investor_line` — dòng cho báo cáo gửi nhà đầu tư (None nếu không có gì đang mở);
      `ops_lines`     — chi tiết đầy đủ mọi cửa sổ đang mở / không kiểm được / trôi / nguồn hỏng;
      `ops_today`     — phần gửi kênh vận hành của lượt chụp ngày `asof`: chi tiết CHỈ của cửa sổ
                        kết thúc đúng ngày đó, cửa sổ cũ gộp một dòng đếm;
      `error`         — đẳng thức không chạy được (một dòng nêu đúng lỗi đã gặp), ngược lại None."""
    try:
        result = check_account(account, asof=asof, **paths)
    except Exception as exc:                # noqa: BLE001 — đường hiển thị: lỗi phải hiện ra, không được làm gãy caller
        line = (f"⚠️ Đẳng thức tiền ({account}) KHÔNG chạy được nên chưa kiểm được dòng tiền chưa "
                f"khai — {_err(exc)}")
        return {"investor_line": None, "ops_lines": [line], "ops_today": [line], "error": line}
    every = ([result["baseline"]] if result["baseline"] else []) + result["windows"]
    day = asof or (every[-1]["date1"] if every else None)
    ops, today, older, thin = [], [], [], []
    for w in every:
        ends_today = w["date1"] == day
        # Cửa sổ THIẾU BẰNG CHỨNG (không kiểm được / không đối chiếu được số lượng) đã kết thúc trong
        # THIN_DAYS ngày qua: chỉ được nhắc đúng một tối ở chi tiết, nên gộp vào dòng đếm hằng tối
        # để thiếu bằng chứng không bị đối xử như sạch (arch-review vòng 2, N8). Cửa sổ mốc khởi
        # điểm luôn không kiểm được (cấu trúc, không đổi) ⇒ không đếm.
        if (not ends_today and not w.get("baseline") and day and (day - w["date1"]).days <= THIN_DAYS
                and not w["suspect"] and (not w["checkable"] or (w.get("qty_unverified") and not w["acked"]))):
            thin.append(w)
        if w["suspect"]:
            ops.append(suspect_line(account, w))
            (today if ends_today else older).append(ops[-1] if ends_today else w)
        elif not w["checkable"] and (ends_today or not w.get("baseline")):
            ops.append(uncheckable_line(account, w))
            if ends_today:
                today.append(ops[-1])
        elif ends_today and (w.get("info") or (w.get("qty_unverified") and not w["acked"])):
            ops.append(f"ℹ️ Đẳng thức tiền ({account}) cửa sổ {_span(w)} — "
                       + (w["info"] or f"phần dư tiền {_sd(w['unexplained'])} dưới ngưỡng nhưng "
                                       f"{w['qty_unverified']} ⇒ KHÔNG đối chiếu được số lượng cổ "
                                       f"phiếu với lệnh khớp (thiếu bằng chứng, không phải sạch)"))
            today.append(ops[-1])
    drift = result["drift"]
    errors = [f"⚠️ Đẳng thức tiền ({account}): {e}" for e in result["source_errors"]]
    if drift and drift["new"]:
        today.append(drift_line(account, drift))
    stale = ([f"{len(older)} cửa sổ cũ chưa đóng (kết thúc "
              + ", ".join(str(w["date1"]) for w in older[:6]) + ("…" if len(older) > 6 else "") + ")"]
             if older else [])
    stale += [f"{len(thin)} cửa sổ trong {THIN_DAYS} ngày qua chưa kiểm được hoặc chưa đối chiếu được số "
              f"lượng cổ phiếu (kết thúc " + ", ".join(str(w["date1"]) for w in thin[:6])
              + ("…" if len(thin) > 6 else "") + ")"] if thin else []
    stale += ["phần dư trôi có hệ thống đã báo từ lượt trước"] if drift and not drift["new"] else []
    if stale:
        today.append(f"⚠️ {WARNING_MARKER} ({account}): còn " + " và ".join(stale)
                     + f" — chi tiết: python3 mike/bin/cash_identity.py --account {account}")
    return {"investor_line": investor_line(result),
            "ops_lines": ops + ([drift_line(account, drift)] if drift else []) + errors,
            "ops_today": today + errors, "error": None}


def warning_lines(account, asof=None, **paths):
    """Các dòng VẬN HÀNH đầy đủ (CLI tỉ suất, cổng giao báo cáo). Không dựng được đẳng thức ⇒ MỘT
    dòng nói đúng lỗi đã gặp — không im lặng, không đoán."""
    return report(account, asof=asof, **paths)["ops_lines"]


def notify_snapshot(account, date, channel, exec_dir=None, notify_script=None):
    """Gửi chi tiết vận hành của lượt chụp `date` (khối `cash_flow_ops` trong
    `nav_snapshot_<TK>_<ngày>.json`) tới kênh `channel` qua `notify_thread.sh` (truyền TÊN kênh),
    rồi ghi trạng thái vào chính file đó. Trả `(rc, thông điệp)`; rc=1 chỉ khi có thứ phải gửi mà
    không gửi được. Tách khỏi `daily_nav_snapshot.py` có chủ đích: script đó được hàng chục
    selfcheck chạy lại, còn hàm này chỉ do lượt cron gọi SAU khi NAV đã ghi xong.
    Bị giết giữa lúc gửi xong và lúc ghi trạng thái ⇒ lượt sau gửi lặp MỘT tin vận hành (không có
    nguồn sự thật phía Discord để hỏi lại) — chấp nhận, vì đây không phải hành động chạm tiền."""
    path = os.path.join(exec_dir or EXEC_DIR, f"nav_snapshot_{account}_{date}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            blob = json.load(f)
        ops = blob.get("cash_flow_ops") or {}
        lines = [str(line) for line in ops.get("lines") or []]
    except (OSError, ValueError, AttributeError) as exc:
        return 1, f"không đọc được {path} nên không biết có gì phải gửi — {_err(exc)}"
    if not lines:
        return 0, f"{account} {date}: không có chi tiết đẳng thức tiền nào phải gửi"
    if str(ops.get("status", "")).startswith(SENT_PREFIX):
        return 0, f"{account} {date}: {ops['status']} — không gửi lại"
    if os.environ.get("MIKE_BOT_TEST_MODE") == "1" or os.environ.get("PYTEST_CURRENT_TEST"):
        return 0, f"{account} {date}: KHÔNG gửi {len(lines)} dòng (đang ở chế độ test)"
    try:
        proc = subprocess.run([notify_script or NOTIFY_SCRIPT, "\n".join(lines), channel],
                              capture_output=True, text=True, timeout=120)
        failure = (None if proc.returncode == 0 else
                   f"notify_thread.sh rc={proc.returncode}, in ra: "
                   f"{(proc.stderr or proc.stdout).strip()[-300:] or '(không in gì)'}")
    except (OSError, subprocess.SubprocessError) as exc:
        failure = _err(exc)
    stamp = datetime.datetime.now(ICT).strftime("%Y-%m-%d %H:%M:%S")
    blob["cash_flow_ops"] = dict(ops, lines=lines, status=(
        f"GỬI HỎNG lúc {stamp} — {failure}" if failure else f"{SENT_PREFIX} {channel} lúc {stamp}"))
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(blob, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)
    if failure:
        return 1, f"{account} {date}: KHÔNG gửi được {len(lines)} dòng tới {channel} — {failure}"
    return 0, f"{account} {date}: đã gửi {len(lines)} dòng tới {channel}"


def _table(result):
    head = (f"{'cửa sổ':<23}{'ΔK':>15}{'bán−mua':>15}{'phí+thuế':>11}{'cổ tức':>12}"
            f"{'lãi egg':>10}{'đã khai':>13}{'phần dư':>13}{'%NAV':>9}")
    lines = [head]
    for w in ([result["baseline"]] if result["baseline"] else []) + result["windows"]:
        label = f"{w['date0'] or 'khởi điểm'} → {w['date1']:%m-%d}"
        if not w["checkable"]:
            lines.append(f"{label:<23}KHÔNG KIỂM ĐƯỢC — {w['reason']}")
            continue
        flag = (f"  ◀ ĐANG MỞ ({w['kind']})" if w["suspect"]
                else "  (đã có lời xác nhận khớp)" if w["acked"]
                else "  (không đối chiếu được số lượng)" if w["qty_unverified"] else "")
        lines.append(f"{label:<23}{w['delta_k']:>15,.0f}{w['sell'] - w['buy']:>15,.0f}"
                     f"{w['fees'] + w['egg_cost']:>11,.0f}{w['dividend']:>12,.0f}{w['egg_interest']:>10,.0f}"
                     f"{w['declared']:>13,.0f}{w['unexplained']:>13,.0f}{w['pct_nav']:>9.4f}{flag}")
    return "\n".join(lines)


def _jsonable(result):
    def clean(value):
        if isinstance(value, (datetime.date, datetime.datetime)):
            return value.isoformat()
        if isinstance(value, dict):
            return {key: clean(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [clean(item) for item in value]
        return value
    return {"account": result["account"], "threshold_pct": result["threshold_pct"],
            "n_windows": len(result["windows"]), "baseline": clean(result["baseline"]),
            "suspects": clean(result["suspects"]), "uncheckable": clean(result["uncheckable"]),
            "drift": clean(result["drift"]), "source_errors": result["source_errors"],
            "windows": clean(result["windows"])}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--account", required=True)
    ap.add_argument("--asof", help="YYYY-MM-DD: chỉ xét nav_history tới ngày này")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--nav-dir")
    ap.add_argument("--raw-dir")
    ap.add_argument("--flows-path")
    ap.add_argument("--inception-path")
    ap.add_argument("--seed-path")
    ap.add_argument("--acks-path")
    ap.add_argument("--corp-actions-path")
    ap.add_argument("--threshold-pct", type=float, default=THRESHOLD_PCT)
    ap.add_argument("--notify-snapshot", metavar="YYYY-MM-DD",
                    help="gửi chi tiết vận hành của lượt chụp NAV ngày này tới --channel rồi thoát")
    ap.add_argument("--channel", default="trading_daily",
                    help="TÊN kênh trong kb/discord_channels.json (không truyền ID trần)")
    args = ap.parse_args()
    if args.notify_snapshot:
        rc, message = notify_snapshot(args.account, args.notify_snapshot, args.channel,
                                      exec_dir=args.nav_dir)
        # NOTIFY_FAILED = chuỗi cron_health_check.py bắt; thiếu nó thì gửi hỏng chỉ nằm trong log cron
        # và các tối sau không gửi bù (arch-review vòng 2, N1).
        print(f"{'NOTIFY_FAILED: ' if rc else ''}cash_identity: {message}",
              file=sys.stderr if rc else sys.stdout)
        return rc
    try:
        result = check_account(
            args.account, asof=datetime.date.fromisoformat(args.asof) if args.asof else None,
            nav_dir=args.nav_dir, raw_dir=args.raw_dir, flows_path=args.flows_path,
            inception_path=args.inception_path, seed_path=args.seed_path, acks_path=args.acks_path,
            corp_actions_path=args.corp_actions_path, threshold_pct=args.threshold_pct)
    except (ValueError, OSError, KeyError) as exc:
        print(f"cash_identity: KHÔNG chạy được — {_err(exc)}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(_jsonable(result), ensure_ascii=False, indent=2))
    else:
        print(f"== Đẳng thức tiền {args.account} — ngưỡng ±{result['threshold_pct']}% NAV, "
              f"{len(result['windows'])} cửa sổ")
        print(_table(result))
        for w in result["suspects"]:
            print(suspect_line(args.account, w))
        if result["drift"]:
            print(drift_line(args.account, result["drift"]))
        for w in result["uncheckable"]:
            print(uncheckable_line(args.account, w))
        for e in result["source_errors"]:
            print(f"⚠️ {e}")
    return 3 if result["suspects"] or result["drift"] else 0


if __name__ == "__main__":
    sys.exit(main())
