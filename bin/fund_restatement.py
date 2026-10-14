#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CƠ CHẾ ĐÍNH CHÍNH số hiệu suất đã công bố (chính sách "tài khoản = quỹ mở", điểm 4 — user
duyệt 2026-10-10; `kb/projects/fund-unit-performance-policy-20261010.md`).

Khi lịch sử NAV đổi CÓ CHỦ ĐÍCH (sửa một dòng nav_history, backfill phiên thiếu, khai dòng tiền
lùi ngày), công cụ này đo — cho TỪNG báo cáo đã gửi — TÁC ĐỘNG CỦA THAY ĐỔI NÀY: số tính lại trên
dữ liệu CŨ so với số tính lại trên dữ liệu MỚI, xếp bậc theo ngưỡng của chính sách, và nêu hành
động bắt buộc.
⚠️ Nó KHÔNG đo sai số của số ĐÃ IN: nếu số in trong báo cáo vốn đã khác số tính lại trên dữ liệu cũ
(phương pháp lúc in khác, dữ liệu lúc in khác — vd biến động tháng 8 ZaloPay in 25,58% trong khi dữ
liệu cũ tính lại ra 21,35%) thì độ lệch đó NẰM NGOÀI phép đo này và phải rà riêng bằng mắt.
⚠️ Phạm vi quét (ghi vào `scan_scope` của đầu ra): (1) file trong `--reports-dir` (kể cả bản
`*.md.bak_sent_*` = đúng bản đã gửi) — báo cáo NGÀY có file từ 2026-08-17 (trước đó chỉ trên Discord); (2) tin EOD đã lên Discord,
đọc lại từ log `eod_trading_report.log*` (cả `.gz`; mặc định thư mục `logs/` cạnh `--reports-dir`):
mỗi dòng `NAV <ngày>: <số> VND (… <±x>% so với hôm trước)` dưới dấu hiệu tài khoản của khối
là một "báo cáo" loại `eod` (số chính: NAV + so với hôm trước), và vì số in đọc được chính xác, nó
còn được so với SỐ ĐÃ IN (`printed_dev`). Log xoay vòng: tin cũ hơn log còn giữ KHÔNG quét được; tin
Discord không đi qua hai kênh trên cũng không.

    độ lệch < 0,05        ⇒ bậc 1: sửa từ nay, không đính chính
    0,05 <= độ lệch <= 0,5 ⇒ bậc 2: sửa sổ + một dòng ghi chú ở báo cáo kế tiếp
    độ lệch > 0,5         ⇒ bậc 3: phát hành lại báo cáo — LUÔN cần user duyệt

"Độ lệch" của một báo cáo = số lớn nhất trong: |NAV cuối kỳ mới / cũ − 1| (%), và |tỉ suất mới −
cũ| (điểm %) của các kỳ báo cáo đó in (ngày: so với hôm trước, WTD, MTD, từ đầu; tuần: WTD, MTD,
từ đầu; tháng: MTD, QTD, YTD, từ đầu — §6 bắt báo cáo tháng in đủ). Đó là SỐ CHÍNH (`headline`).
Riêng các số THEO NGÀY nằm trong kỳ của báo cáo (bảng NAV từng ngày, và mọi chỉ số suy từ chuỗi
ngày như độ biến động) được đo thành `window`: |NAV ngày mới / cũ − 1| và |tỉ suất ngày mới − cũ|
lớn nhất trong kỳ. Công cụ KHÔNG biết báo cáo có in các số ngày đó không ⇒ khi `window` từ bậc 2
trở lên và cao hơn `headline`, hoặc kỳ có dòng NAV thêm/bỏ, hoặc một dòng trong kỳ đổi cột TIỀN /
CỔ PHIẾU / NỢ mà NAV giữ nguyên, báo cáo vào danh sách CẦN NGƯỜI XEM (kèm số dòng trích nguyên NAV
cũ của dòng bị sửa và NAV mới của dòng chèn, tìm bằng so chuỗi) — không tự hạ thành "không cần làm
gì".

Công cụ KHÔNG gửi, KHÔNG sửa, KHÔNG phát hành lại báo cáo nào. `impact` chỉ đọc. `apply` chỉ ghi
nav_history (và nhật ký `nav_history_corrections.jsonl`) ở thư mục được chỉ định, sau khi kiểm báo
cáo tác động đúng là của bản đính chính đó; ghi vào thư mục dữ liệu thật cần `--real-data` ("thật"
= `nav_unit_ledger.is_real_data_dir`: cây cố định của máy, mọi thư mục có `dnse_raw_*.jsonl`, hoặc
NAV_HISTORY_DIR suy từ WC_ROOT).
`apply` chỉ chạy trong khung 09:00–18:30 ICT: nav_history thật bị `daily_nav_snapshot.py` ghi lại
lúc 19:00–21:45 (`nav_sync_retry` mỗi 15'), 19:10 (EOD), 19:50 (+2 retry) và KHÔNG có khoá chung
với đường ghi đó ⇒ áp trong khung ấy có thể bị ghi đè mất. md5 nav_history được đọc lại NGAY TRƯỚC
`os.replace`; đổi giữa chừng ⇒ không ghi, nhật ký thêm bản ghi `aborted`.
Trước khi ghi, byte nav_history hiện có được chép sang
`<nav_dir>/restatement_backups/<account>_<giờ ICT>_<md5>.csv` (chỉ-thêm, không ghi đè). ĐƯỜNG LUI:
trước khi chốt sổ = chép bản sao lưu đó về lại + áp một đính chính NGƯỢC (để nhật ký ghi nhận);
sau khi chốt sổ = chỉ còn đường đính chính (`nav_unit_ledger.py --restate`).

Dùng:
    # (sổ cũ, sổ mới) — hai thư mục nav_history
    fund_restatement.py impact --account SpaceX --new-nav-dir /tmp/x/execution_logs [--out J]
    # (dòng bị sửa) — file đính chính, áp trong bộ nhớ
    fund_restatement.py impact --account SpaceX --correction C.json [--out J]
    # gắn với một sổ đơn vị đã chốt (để `nav_unit_ledger.py --restate` nhận báo cáo này)
    fund_restatement.py impact --account SpaceX --correction C.json --sealed-ledger L.csv --out J
    fund_restatement.py apply  --account SpaceX --nav-dir D --correction C.json \\
        --impact-report J --approved-by "user 2026-10-14"

File đính chính (`--correction`):
    {"account": "SpaceX", "corrections": [
       {"op": "replace", "date": "2026-07-02", "expect": {"nav": "994733747"},
        "set": {"nav": "990304455", "cash": "-409315545"}, "reason": "...", "evidence": "..."},
       {"op": "insert", "date": "2026-08-06", "row": {<đủ mọi cột>}, "reason": "...", "evidence": "..."},
       {"op": "delete", "date": "...", "expect": {"nav": "..."}, "reason": "...", "evidence": "..."}]}
  `expect` (bắt buộc với replace/delete) = giá trị HIỆN CÓ của dòng: lệch ⇒ từ chối (file đính
  chính viết cho một trạng thái khác). Dòng sau khi sửa/chèn phải giữ bất biến
  nav = mtm_stock + cash − margin_debt + offbook_assets + egg_assets (lệch <= 1 đ).

Selfcheck: python3 mike/bin/fund_restatement_selfcheck.py
"""
import argparse
import calendar
import csv
import datetime
import glob
import gzip
import hashlib
import io
import json
import math
import os
import re
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import account_cash_flows as acf  # noqa: E402
import nav_period_returns as npr  # noqa: E402
import nav_unit_ledger as nul  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")

# Ngưỡng của chính sách điểm 4 — đơn vị: % NAV hoặc điểm % tỉ suất.
TIER_NOTE_FROM = 0.05          # >= ⇒ bậc 2
TIER_REISSUE_ABOVE = 0.5       # >  ⇒ bậc 3
TIER_ACTION = {
    0: "không đổi",
    1: "sửa từ nay, không đính chính",
    2: "sửa sổ + một dòng ghi chú ở báo cáo kế tiếp",
    3: "PHÁT HÀNH LẠI báo cáo — cần user duyệt",
}
HEADLINE_KEYS = {"eod": ("day",),
                 "daily": ("day", "wtd", "mtd", "inception"),
                 "weekly": ("wtd", "mtd", "inception"),
                 "monthly": ("mtd", "qtd", "ytd", "inception")}
NAV_INVARIANT_TOL = 1.0        # đồng
AUDIT_LOG = "nav_history_corrections.jsonl"
BACKUP_DIR = "restatement_backups"
# Cột tiền của một dòng nav_history ngoài `nav`: báo cáo có thể in riêng từng cột này.
MONEY_COLUMNS = ("mtm_stock", "cash", "margin_debt", "offbook_assets", "egg_assets",
                 "cum_dividend_excl")
# Khung được phép `apply` (giờ ICT, hai đầu tính cả): ngoài khung ghi nav_history của
# daily_nav_snapshot.py (19:00–21:45) và cách nó một quãng.
APPLY_WINDOW_ICT = (datetime.time(9, 0), datetime.time(18, 30))
# CHỈ cho selfcheck: giờ ICT giả (ISO). Bị từ chối khi --nav-dir là chính thư mục dữ liệu thật.
TEST_NOW_ENV = "FUND_RESTATEMENT_TEST_NOW_ICT"

# `<…>.md.bak_sent_<nhãn>` = bản ĐÃ GỬI được giữ lại khi báo cáo bị soạn lại ⇒ cũng phải đo.
REPORT_RE = re.compile(r"^(?P<who>[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*)_(?P<kind>daily|weekly|monthly)"
                       r"_report_(?P<rest>.+?)\.md(?:\.bak_sent_(?P<bak>.+))?$")
EOD_LOG_GLOB = "eod_trading_report.log*"
# Dấu hiệu tài khoản của một khối trong log EOD — đổi dạng theo thời gian, nhận CẢ BA: dòng lệnh
# `=== …eod_trading_report.sh --account X ===`, tiêu đề cũ `EOD Trading Report — X (ngày)`, tiêu đề
# mới (SpaceX từ 09-2026) `Báo cáo giao dịch ngày — X (ngày)`.
_EOD_HEADER_RE = re.compile(r"(?:--account (?P<acct1>[A-Za-z0-9_]+) ===|(?:EOD Trading Report|Báo cáo giao "
                            r"dịch ngày) — (?P<acct2>[A-Za-z0-9_]+) \(\d{4}-\d{2}-\d{2}\))")
_EOD_NAV_RE = re.compile(r"NAV (?P<date>\d{4}-\d{2}-\d{2}): (?P<nav>[\d,]+) VND\*{0,2} \((?P<vnd>[+-]?[\d,]+) VND, "
                         r"(?P<pct>[+-]?\d+(?:\.\d+)?)% so với hôm trước\)")
_RANGE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_to_(\d{4}-\d{2}-\d{2})(?:_(.+))?$")
_DAY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:_(.+))?$")
_MONTH_RE = re.compile(r"^(\d{4})-(\d{2})(?:_(.+))?$")


class RestatementError(ValueError):
    """Đầu vào của công cụ đính chính không dùng được — thông điệp nêu đúng thứ đã đọc."""


class ApplyRefused(ValueError):
    """Từ chối ghi vào thư mục dữ liệu thật khi không có --real-data (rc=3)."""


def tier(dev: float) -> int:
    """Bậc của một độ lệch (đã lấy trị tuyệt đối). 0 = không lệch."""
    if not math.isfinite(dev):
        return 3                    # không đo được thì không được tự xếp là "nhỏ"
    if dev == 0:
        return 0
    if dev < TIER_NOTE_FROM:
        return 1
    if dev <= TIER_REISSUE_ABOVE:
        return 2
    return 3


def _md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


# ---------------------------------------------------------------- nav_history + file đính chính
def nav_history_path(account: str, nav_dir: str) -> str:
    return os.path.join(nav_dir, f"nav_history_{account}.csv")


def read_nav_table(data: bytes, where: str) -> tuple:
    """(fieldnames, [dict]) của một file nav_history, giữ nguyên chuỗi từng ô."""
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    fields = reader.fieldnames or []
    if "date" not in fields or "nav" not in fields:
        raise RestatementError(f"{where}: header {fields} thiếu cột date/nav")
    rows = list(reader)
    dates = [r["date"] for r in rows]
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise RestatementError(f"{where}: cột date không tăng nghiêm ngặt")
    return fields, rows


def line_terminator(data: bytes) -> str:
    """Dấu xuống dòng của file gốc (`daily_nav_snapshot.py` ghi CRLF) — ghi lại phải giữ đúng nó,
    không thì MỌI dòng đổi byte dù chỉ sửa một dòng."""
    return "\r\n" if b"\r\n" in data else "\n"


def write_nav_table(fields: list, rows: list, terminator: str) -> bytes:
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator=terminator)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _num(row: dict, key: str) -> float:
    raw = row.get(key)
    return float(raw) if raw not in (None, "") else 0.0


def _check_row(row: dict, fields: list, where: str) -> None:
    missing = [k for k in fields if k not in row]
    extra = [k for k in row if k not in fields]
    if missing or extra:
        raise RestatementError(f"{where}: dòng thiếu cột {missing} / thừa cột {extra}")
    try:
        datetime.date.fromisoformat(row["date"])
        parts = {k: _num(row, k) for k in ("nav", "mtm_stock", "cash", "margin_debt",
                                           "offbook_assets", "egg_assets")}
    except ValueError as exc:
        raise RestatementError(f"{where}: ô không phải số/ngày ({exc})") from exc
    if not all(math.isfinite(v) for v in parts.values()):
        raise RestatementError(f"{where}: có ô không hữu hạn: {parts}")
    want = (parts["mtm_stock"] + parts["cash"] - parts["margin_debt"] + parts["offbook_assets"]
            + parts["egg_assets"])
    if abs(parts["nav"] - want) > NAV_INVARIANT_TOL:
        raise RestatementError(
            f"{where}: vỡ bất biến nav = mtm_stock + cash − margin_debt + offbook_assets + "
            f"egg_assets: nav {parts['nav']:,.0f} nhưng các cột cộng lại {want:,.0f} (lệch "
            f"{parts['nav'] - want:+,.0f} đ)")
    if not row.get("balance_ts"):
        raise RestatementError(f"{where}: thiếu balance_ts")
    try:
        datetime.datetime.fromisoformat(row["balance_ts"])
    except ValueError as exc:
        raise RestatementError(f"{where}: balance_ts {row['balance_ts']!r} không đọc được") from exc


def load_correction(path: str, account: str) -> tuple:
    """(danh sách đính chính đã kiểm hình dạng, md5 file)."""
    data = _read_bytes(path)
    try:
        doc = json.loads(data.decode("utf-8"))
        items = doc["corrections"]
        who = doc["account"]
    except (ValueError, KeyError, TypeError) as exc:
        raise RestatementError(f"{path}: không đọc được file đính chính ({type(exc).__name__}: "
                               f"{exc}) — cần {{account, corrections: [...]}}") from exc
    if who != account:
        raise RestatementError(f"{path}: file đính chính của tài khoản {who!r}, đang chạy cho "
                               f"{account!r} (§12 — không áp chéo tài khoản)")
    if not isinstance(items, list) or not items:
        raise RestatementError(f"{path}: corrections phải là list không rỗng")
    seen = set()
    for n, item in enumerate(items):
        where = f"{path} corrections[{n}]"
        if not isinstance(item, dict) or item.get("op") not in ("replace", "insert", "delete"):
            raise RestatementError(f"{where}: op phải là replace | insert | delete, được "
                                   f"{item.get('op') if isinstance(item, dict) else item!r}")
        for key in ("date", "reason", "evidence"):
            if not str(item.get(key) or "").strip():
                raise RestatementError(f"{where}: thiếu {key} (không có lý do + bằng chứng thì "
                                       f"không được sửa lịch sử)")
        try:
            datetime.date.fromisoformat(item["date"])
        except ValueError as exc:
            raise RestatementError(f"{where}: date {item['date']!r} không phải YYYY-MM-DD") from exc
        if item["date"] in seen:
            raise RestatementError(f"{where}: ngày {item['date']} xuất hiện hai lần trong file")
        seen.add(item["date"])
        if item["op"] in ("replace", "delete") and not isinstance(item.get("expect"), dict):
            raise RestatementError(f"{where}: {item['op']} cần expect = giá trị hiện có của dòng")
        if item["op"] == "replace" and not (isinstance(item.get("set"), dict) and item["set"]):
            raise RestatementError(f"{where}: replace cần set = {{cột: giá trị mới}}")
        if item["op"] == "insert" and not isinstance(item.get("row"), dict):
            raise RestatementError(f"{where}: insert cần row = đủ mọi cột")
    return items, _md5(data)


def apply_corrections(fields: list, rows: list, items: list) -> tuple:
    """Áp `items` lên bản sao của `rows`. Trả `(rows mới, [thay đổi])`; mỗi thay đổi =
    {op, date, old, new}. Dòng đã mang SẴN giá trị sau đính chính ⇒ ghi nhận `already`, không lỗi
    (chạy lại không được sửa lần hai)."""
    out = [dict(r) for r in rows]
    changes = []
    for n, item in enumerate(items):
        where = f"corrections[{n}] {item['op']} {item['date']}"
        idx = next((i for i, r in enumerate(out) if r["date"] == item["date"]), None)
        if item["op"] == "insert":
            row = {k: str(v) for k, v in item["row"].items()}
            if row.get("date") != item["date"]:
                raise RestatementError(f"{where}: row.date {row.get('date')!r} khác date")
            _check_row(row, fields, where)
            if idx is not None:
                if out[idx] == row:
                    changes.append({"op": "insert", "date": item["date"], "old": None,
                                    "new": row, "already": True})
                    continue
                raise RestatementError(f"{where}: nav_history ĐÃ có dòng ngày này với giá trị "
                                       f"khác (nav {out[idx]['nav']}) — dùng replace")
            out.append(row)
            out.sort(key=lambda r: r["date"])
            changes.append({"op": "insert", "date": item["date"], "old": None, "new": row})
            continue
        if idx is None:
            if item["op"] == "delete":
                changes.append({"op": "delete", "date": item["date"], "old": None, "new": None,
                                "already": True})
                continue
            raise RestatementError(f"{where}: nav_history không có dòng ngày này")
        cur = out[idx]
        if not isinstance(item.get("expect"), dict):
            raise RestatementError(f"{where}: thiếu expect — {item['op']} phải khai giá trị HIỆN CÓ "
                                   f"của dòng (đọc được nav {cur.get('nav')!r})")
        if item["op"] == "replace":
            new = dict(cur, **{k: str(v) for k, v in item["set"].items()})
            unknown = [k for k in item["set"] if k not in fields]
            if unknown or "date" in item["set"]:
                raise RestatementError(f"{where}: set có cột lạ {unknown} hoặc đổi cột date")
            if cur == new:
                changes.append({"op": "replace", "date": item["date"], "old": dict(cur),
                                "new": new, "already": True})
                continue
        bad = {k: (cur.get(k), str(v)) for k, v in item["expect"].items() if cur.get(k) != str(v)}
        if bad:
            raise RestatementError(
                f"{where}: dòng hiện có KHÁC expect ở " + "; ".join(
                    f"{k}: đọc được {a!r}, expect {b!r}" for k, (a, b) in sorted(bad.items()))
                + " — file đính chính viết cho một trạng thái khác của nav_history")
        if item["op"] == "delete":
            changes.append({"op": "delete", "date": item["date"], "old": dict(cur), "new": None})
            del out[idx]
            continue
        _check_row(new, fields, where)
        changes.append({"op": "replace", "date": item["date"], "old": dict(cur), "new": new})
        out[idx] = new
    return out, changes


# ---------------------------------------------------------------- hai phía cũ / mới
def _nav_rows(table: list) -> list:
    rows = [acf.NavRow(datetime.date.fromisoformat(r["date"]), float(r["nav"]),
                       is_estimate=(r.get("nav_is_estimate") == "True"),
                       balance_ts=(r.get("balance_ts") or None))
            for r in table if r.get("date") and r.get("nav")]
    if not rows:
        raise RestatementError("nav_history không có dòng nào")
    return rows


class Side:
    """Một phía (cũ hoặc mới): nav_history + mốc khởi điểm + sổ dòng tiền ⇒ sổ đơn vị."""

    def __init__(self, account, table, inception, flows):
        self.account, self.table, self.inception, self.flows = account, table, inception, flows
        self.rows = _nav_rows(table)
        base = npr._inception_baseline(self.rows, inception)
        self.ledger, self.info = nul.build_ledger(self.rows, flows, *base)
        self.by_date = {r["date"]: r for r in self.ledger}
        self.day_ret = {}
        for prev, cur in zip(self.ledger, self.ledger[1:]):
            self.day_ret[cur["date"]] = (cur["unit_price"] / prev["unit_price"] - 1) * 100

    def numbers(self, asof: datetime.date):
        """Số công bố asof (không làm tròn): {kỳ: tỉ suất %} + nav + ngày dòng cuối; None nếu
        chưa có dòng nào <= asof."""
        if asof < self.ledger[0]["date"] or not any(r[0] <= asof for r in self.rows):
            return None
        res = npr.compute_period_returns(self.account, asof, self.rows, self.inception, self.flows)
        out = {"nav": res["inception"]["nav1"], "asof_row": res["inception"]["to_date"]}
        for key in ("inception", "wtd", "mtd", "day"):
            block = res[key]
            out[key] = None if block is None else (block["unit_price_ratio"] - 1) * 100
        # QTD/YTD: cùng quy ước mốc của nav_period_returns._period (dòng sổ cuối TRƯỚC đầu kỳ; kỳ
        # mở trước mốc khởi điểm thì lùi về chính mốc khởi điểm).
        i1 = max(i for i, r in enumerate(self.ledger) if r["date"] <= asof)
        quarter = datetime.date(asof.year, 3 * ((asof.month - 1) // 3) + 1, 1)
        for key, start in (("qtd", quarter), ("ytd", datetime.date(asof.year, 1, 1))):
            out[key] = (npr._period(self.ledger, start, i1)["unit_price_ratio"] - 1) * 100
        return out


# ---------------------------------------------------------------- báo cáo đã gửi
def parse_report_name(name: str):
    """{who: [tài khoản], kind, start, end, suffix} của một tên file báo cáo; None nếu tên không
    phải báo cáo ngày/tuần/tháng; ném RestatementError nếu ĐÚNG là báo cáo mà không đọc được kỳ."""
    m = REPORT_RE.match(name)
    if not m:
        return None
    kind, rest = m.group("kind"), m.group("rest")
    try:
        r = _RANGE_RE.match(rest)
        if r:
            start, end, suffix = (datetime.date.fromisoformat(r.group(1)),
                                  datetime.date.fromisoformat(r.group(2)), r.group(3))
        elif _DAY_RE.match(rest):
            d = _DAY_RE.match(rest)
            end, suffix = datetime.date.fromisoformat(d.group(1)), d.group(2)
            start = end
            if kind == "weekly":
                start = end - datetime.timedelta(days=end.weekday())
            elif kind == "monthly":
                start = end.replace(day=1)
        elif _MONTH_RE.match(rest):
            mm = _MONTH_RE.match(rest)
            year, month, suffix = int(mm.group(1)), int(mm.group(2)), mm.group(3)
            start = datetime.date(year, month, 1)
            end = datetime.date(year, month, calendar.monthrange(year, month)[1])
        else:
            raise ValueError(f"phần kỳ {rest!r} không phải NGÀY, NGÀY_to_NGÀY hay THÁNG")
        if start > end:
            raise ValueError(f"kỳ ngược: {start} > {end}")
    except ValueError as exc:
        raise RestatementError(f"{name}: tên báo cáo không đọc được kỳ ({exc})") from exc
    return {"who": m.group("who").split("_"), "kind": kind, "start": start, "end": end,
            "suffix": suffix, "bak_sent": m.group("bak")}


def list_reports(reports_dir: str, account: str) -> tuple:
    """(báo cáo của `account` — cả bản `.md.bak_sent_*`, tên không đọc được kỳ, file trông như
    báo cáo nhưng không phải .md)."""
    found, unparsed, skipped = [], [], []
    for name in sorted(os.listdir(reports_dir)):
        if not os.path.isfile(os.path.join(reports_dir, name)):
            continue
        if not (name.endswith(".md") or ".md.bak_sent_" in name):
            if re.search(r"_(daily|weekly|monthly)_report_", name) and account in name.split("_"):
                skipped.append(name)
            continue
        try:
            meta = parse_report_name(name)
        except RestatementError as exc:
            if account in name.split("_"):
                unparsed.append(str(exc))
            continue
        if meta and account in meta["who"]:
            found.append(dict(meta, name=name))
    return found, unparsed, skipped


def _read_log_text(path: str) -> str:
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as f:
        return f.read()


def list_eod_messages(pattern: str, account: str) -> tuple:
    """(tin EOD của `account` đọc từ log khớp `pattern`, [file đã quét]). Mỗi tin = một "báo cáo"
    loại `eod`: {name, kind, start=end=ngày NAV, printed: {nav, day_pct}, text}. Gán tài khoản theo
    dấu hiệu tài khoản gần nhất phía trên (`_EOD_HEADER_RE`, §12); dòng NAV trước mọi dấu hiệu bị bỏ."""
    files = sorted(glob.glob(pattern))
    out = []
    for path in files:
        who = None
        for n, line in enumerate(_read_log_text(path).splitlines(), start=1):
            h = _EOD_HEADER_RE.search(line)
            if h:
                who = h.group("acct1") or h.group("acct2")
                continue
            m = _EOD_NAV_RE.search(line)
            if not m or who != account:
                continue
            day = datetime.date.fromisoformat(m.group("date"))
            out.append({"name": f"{os.path.basename(path)}:{n}", "kind": "eod", "who": [account],
                        "start": day, "end": day, "suffix": None, "bak_sent": None,
                        "printed": {"nav": float(m.group("nav").replace(",", "")),
                                    "day_pct": float(m.group("pct"))},
                        "text": line})
    return out, files


def _nav_literals(nav: float) -> list:
    whole = f"{nav:,.0f}"
    return [whole.replace(",", "."), whole, whole.replace(",", "")]


def assess_report(meta: dict, old: Side, new: Side, changed_dates: dict, text: str) -> dict:
    """Độ lệch của MỘT báo cáo đã gửi. `changed_dates` = {ngày: {nav_old, nav_new, columns}} của
    các dòng nav_history bị sửa/chèn/xoá (`_changed_dates`)."""
    kind, start, end = meta["kind"], meta["start"], meta["end"]
    a, b = old.numbers(end), new.numbers(end)
    out = {"report": meta["name"], "kind": kind, "period": [start.isoformat(), end.isoformat()],
           "headline": {}, "window": {}, "literal_hits": [], "literal_hits_new": [],
           "component_changes": []}
    devs = []
    if a is None and b is None:
        out["status"] = "kỳ báo cáo đứng trước mọi dòng nav_history ở cả hai phía"
    elif a is None or b is None:
        out["status"] = ("phía CŨ chưa có dòng nào tới cuối kỳ" if a is None
                         else "phía MỚI không còn dòng nào tới cuối kỳ")
        devs.append(float("inf"))
    else:
        out["asof_row"] = {"old": a["asof_row"], "new": b["asof_row"]}
        nav_dev = (b["nav"] / a["nav"] - 1) * 100
        out["headline"]["nav"] = {"old": a["nav"], "new": b["nav"], "dev_pct": nav_dev}
        devs.append(abs(nav_dev))
        for key in HEADLINE_KEYS[kind]:
            if a[key] is None and b[key] is None:
                continue
            if a[key] is None or b[key] is None:
                out["headline"][key] = {"old": a[key], "new": b[key], "dev_pp": None}
                devs.append(float("inf"))
                continue
            out["headline"][key] = {"old": a[key], "new": b[key], "dev_pp": b[key] - a[key]}
            devs.append(abs(b[key] - a[key]))
    out["headline_dev"] = max(devs) if devs else 0.0
    out["tier_headline"] = tier(out["headline_dev"])

    # Số THEO NGÀY trong kỳ (không tính mốc khởi điểm — nó không phải dòng NAV nào được in).
    wdevs, days = [], []
    span = sorted(d for d in set(old.by_date) | set(new.by_date)
                  if start <= d <= end and d != old.ledger[0]["date"])
    for d in span:
        ro, rn = old.by_date.get(d), new.by_date.get(d)
        if ro is None or rn is None:
            days.append({"date": d.isoformat(), "change": "thêm dòng" if ro is None else "bỏ dòng",
                         "nav_old": ro and ro["nav"], "nav_new": rn and rn["nav"]})
            continue
        nav_dev = (rn["nav"] / ro["nav"] - 1) * 100
        ret_dev = new.day_ret.get(d, 0.0) - old.day_ret.get(d, 0.0)
        if nav_dev or ret_dev:
            days.append({"date": d.isoformat(), "change": "đổi số", "nav_old": ro["nav"],
                         "nav_new": rn["nav"], "nav_dev_pct": nav_dev, "day_return_dev_pp": ret_dev})
            wdevs += [abs(nav_dev), abs(ret_dev)]
    # Báo cáo trích nguyên NAV cũ của một dòng bị sửa (kể cả ngoài kỳ của nó) ⇒ tính vào window.
    lines = text.splitlines()

    def find(nav):
        return [n for n, line in enumerate(lines, start=1)
                if any(lit in line for lit in _nav_literals(nav))]

    for d, ch in sorted(changed_dates.items()):
        nav_old, nav_new = ch["nav_old"], ch["nav_new"]
        if nav_old is None:
            # Dòng CHÈN: không có NAV cũ để tìm; tìm NAV MỚI — báo cáo in đúng số đó thì người
            # xem biết nó khớp, không thấy thì (nếu ngày nằm trong kỳ) báo cáo đã in số khác/không in.
            hits = find(nav_new) if nav_new is not None else []
            if hits:
                out["literal_hits_new"].append({"date": d.isoformat(), "nav_new": nav_new,
                                                "lines": hits})
            continue
        hits = find(nav_old)
        if hits and nav_new != nav_old:
            out["literal_hits"].append({"date": d.isoformat(), "nav_old": nav_old, "lines": hits})
            rn = new.by_date.get(d)
            wdevs.append(abs(rn["nav"] / nav_old - 1) * 100 if rn else float("inf"))
        # NAV giữ nguyên nhưng cột tiền/cổ phiếu/nợ của dòng đổi: không số nào ở trên thấy, mà
        # báo cáo có thể in riêng từng cột ⇒ người xem.
        money = [c for c in ch["columns"] if c in MONEY_COLUMNS]
        if start <= d <= end and nav_new == nav_old and money:
            out["component_changes"].append({"date": d.isoformat(), "columns": money})
    structural = [x for x in days if x["change"] != "đổi số"]
    out["window"] = {"days": days, "rows_added_or_removed": len(structural)}
    out["window_dev"] = max(wdevs) if wdevs else 0.0
    out["tier_window"] = tier(out["window_dev"])
    out["affected"] = bool(out["headline_dev"] or out["window_dev"] or structural
                           or out["component_changes"])
    printed = meta.get("printed")
    if printed is not None:
        # Tin EOD: số in đọc được chính xác ⇒ đo THÊM lệch so với SỐ ĐÃ IN (không chỉ so với dữ liệu
        # cũ tính lại). In 2 chữ số thập phân ⇒ sai số làm tròn ≤ 0,005 (bậc 1) là nền, không phải lỗi.
        pdevs = []
        if b is not None:
            pdevs.append(abs(b["nav"] / printed["nav"] - 1) * 100)
            if b["day"] is not None:
                pdevs.append(abs(b["day"] - printed["day_pct"]))
        out["printed"] = dict(printed, new_nav=b and b["nav"], new_day_pct=b and b["day"])
        out["printed_dev"] = max(pdevs) if pdevs else float("inf")
        out["tier_printed"] = tier(out["printed_dev"])
    out["action"] = TIER_ACTION[out["tier_headline"]]
    # Bậc 1 theo chính sách là "sửa từ nay, không đính chính" ⇒ số ngày lệch dưới 0,05 không
    # đáng gọi người; từ bậc 2 trở lên mà số chính của báo cáo không phản ánh thì phải có người xem.
    out["needs_human_look"] = (
        (out["tier_window"] >= 2 and out["tier_window"] > out["tier_headline"])
        or (bool(structural) and out["tier_headline"] < 2)
        or bool(out["component_changes"]))
    return out


def _look_reason(r: dict) -> str:
    parts = []
    if r["tier_window"] > r["tier_headline"]:
        parts.append(f"số theo NGÀY trong kỳ lệch bậc {r['tier_window']} ({r['window_dev']:.4f}) "
                     f"cao hơn số chính (bậc {r['tier_headline']})")
    if r["window"]["rows_added_or_removed"]:
        parts.append(f"kỳ báo cáo có {r['window']['rows_added_or_removed']} dòng NAV thêm/bỏ")
    for c in r["component_changes"]:
        parts.append(f"ngày {c['date']} đổi cột {', '.join(c['columns'])} mà NAV giữ nguyên")
    return ("; ".join(parts)
            + f"; {sum(len(h['lines']) for h in r['literal_hits'])} dòng trích nguyên NAV cũ, "
              f"{sum(len(h['lines']) for h in r['literal_hits_new'])} dòng in đúng NAV của dòng "
              f"chèn — người phải xem báo cáo có in số ngày đó không")


def build_impact(account, old: Side, new: Side, changed_dates: dict, reports_dir: str,
                 eod_glob: str = None) -> dict:
    reports, unparsed, skipped = list_reports(reports_dir, account)
    rows = []
    for meta in reports:
        with open(os.path.join(reports_dir, meta["name"]), "r", encoding="utf-8") as f:
            text = f.read()
        rows.append(assess_report(meta, old, new, changed_dates, text))
    eod, eod_files = list_eod_messages(eod_glob, account) if eod_glob else ([], [])
    for meta in eod:
        rows.append(assess_report(meta, old, new, changed_dates, meta["text"]))
    affected = [r for r in rows if r["affected"]]
    reissue = [r for r in affected if max(r["tier_headline"], r.get("tier_printed", 0)) == 3]
    look = [r for r in affected if r["needs_human_look"] and r not in reissue]
    return {
        "account": account,
        "thresholds": {"tier2_from": TIER_NOTE_FROM, "tier3_above": TIER_REISSUE_ABOVE},
        "n_reports_scanned": len(rows), "n_reports_affected": len(affected),
        "reports": affected,
        "unaffected_reports": [r["report"] for r in rows if not r["affected"]],
        "unparsed_report_names": unparsed, "skipped_non_md": skipped,
        "scan_scope": {
            "reports_dir": reports_dir,
            "n_report_files": sum(1 for r in rows if r["kind"] != "eod"),
            "eod_log_glob": eod_glob, "eod_log_files": [os.path.basename(x) for x in eod_files],
            "n_eod_messages": len(eod),
            "eod_dates": ([min(m["end"] for m in eod).isoformat(), max(m["end"] for m in eod).isoformat()]
                          if eod else None),
            "note": "file .md: báo cáo ngày có từ 2026-08-17 (trước đó chỉ trên Discord); tin EOD Discord: chỉ những tin còn trong "
                    "log eod_trading_report.log* (log xoay vòng); kênh khác KHÔNG quét"},
        # Hàng đợi: công cụ không tự gửi/phát hành lại gì.
        "queue_user_decision": (
            [{"report": r["report"], "why": f"bậc 3 — số chính lệch {r['headline_dev']:.4f}"
              + (f", so với số ĐÃ IN lệch {r['printed_dev']:.4f}" if "printed_dev" in r else "")
              + f" (ngưỡng > {TIER_REISSUE_ABOVE}): phát hành lại / đính chính cần user duyệt"}
             for r in reissue]
            + [{"report": r["report"], "why": _look_reason(r)} for r in look]),
        "note_next_report": [r["report"] for r in affected
                             if max(r["tier_headline"], r.get("tier_printed", 0)) == 2],
        "fix_forward_only": [r["report"] for r in affected
                             if max(r["tier_headline"], r.get("tier_printed", 0)) <= 1],
    }


# ---------------------------------------------------------------- CLI
def _load_side(account, nav_bytes, where, inception_path, flows_path):
    fields, table = read_nav_table(nav_bytes, where)
    inception = nul.load_inception(account, inception_path)
    flows = acf.load_flows(account, flows_path=flows_path, require_file=True)
    return fields, table, Side(account, table, inception, flows)


def _changed_dates(old_table: list, new_table: list) -> dict:
    """{ngày: {nav_old | None, nav_new | None, columns}}: mọi dòng nav_history khác nhau giữa
    hai phía (theo từng ô); `columns` = các cột khác nhau (rỗng khi dòng chỉ có ở một phía)."""
    a = {r["date"]: r for r in old_table}
    b = {r["date"]: r for r in new_table}
    out = {}
    for d in sorted(set(a) | set(b)):
        ra, rb = a.get(d), b.get(d)
        if ra != rb:
            out[datetime.date.fromisoformat(d)] = {
                "nav_old": float(ra["nav"]) if ra else None,
                "nav_new": float(rb["nav"]) if rb else None,
                "columns": sorted(k for k in set(ra) | set(rb) if ra.get(k) != rb.get(k))
                if ra and rb else []}
    return out


def _print_table(impact: dict, show_all: bool) -> None:
    acct = impact["account"]
    print(f"== Tác động đính chính — {acct}: {impact['n_reports_affected']}/"
          f"{impact['n_reports_scanned']} báo cáo đã gửi bị ảnh hưởng "
          f"(ngưỡng: <{TIER_NOTE_FROM} bậc 1 · {TIER_NOTE_FROM}–{TIER_REISSUE_ABOVE} bậc 2 · "
          f">{TIER_REISSUE_ABOVE} bậc 3)")
    print(f"{'báo cáo':58s} {'số chính':>9s} bậc {'theo ngày':>9s} bậc  hành động")
    for r in impact["reports"]:
        mark = "  ⚠ CẦN NGƯỜI XEM" if r["needs_human_look"] else ""
        if "printed" in r:
            p = r["printed"]
            mark += (f"  [tin EOD đã in NAV {p['nav']:,.0f} ({p['day_pct']:+.2f}%); tính lại "
                     + ("—" if p["new_day_pct"] is None else f"{p['new_day_pct']:+.3f}%")
                     + f" ⇒ lệch số in {r['printed_dev']:.4f} bậc {r['tier_printed']}]")
        print(f"{r['report'][:58]:58s} {r['headline_dev']:9.4f}  {r['tier_headline']}  "
              f"{r['window_dev']:9.4f}  {r['tier_window']}   {r['action']}{mark}")
        for key, v in r["headline"].items():
            if key == "nav":
                if v["dev_pct"]:
                    print(f"      NAV cuối kỳ {v['old']:,.0f} → {v['new']:,.0f} ({v['dev_pct']:+.4f}%)")
            elif v["dev_pp"] is None or v["dev_pp"]:
                old = "—" if v["old"] is None else f"{v['old']:+.3f}%"
                new = "—" if v["new"] is None else f"{v['new']:+.3f}%"
                print(f"      {key}: {old} → {new}"
                      + ("" if v["dev_pp"] is None else f" ({v['dev_pp']:+.4f} điểm %)"))
        for x in r["window"]["days"]:
            if x["change"] == "đổi số":
                print(f"      ngày {x['date']}: NAV {x['nav_old']:,.0f} → {x['nav_new']:,.0f} "
                      f"({x['nav_dev_pct']:+.4f}%), tỉ suất ngày {x['day_return_dev_pp']:+.4f} điểm %")
            else:
                nav = x["nav_new"] if x["nav_new"] is not None else x["nav_old"]
                print(f"      ngày {x['date']}: {x['change']} (NAV {nav:,.0f})")
        for h in r["literal_hits"]:
            print(f"      trích nguyên NAV cũ của {h['date']} ({h['nav_old']:,.0f}) ở dòng {h['lines']}")
        for h in r["literal_hits_new"]:
            print(f"      in ĐÚNG NAV của dòng chèn {h['date']} ({h['nav_new']:,.0f}) ở dòng {h['lines']}")
        for c in r["component_changes"]:
            print(f"      ngày {c['date']}: đổi cột {', '.join(c['columns'])}, NAV giữ nguyên")
    if show_all and impact["unaffected_reports"]:
        print("không đổi: " + ", ".join(impact["unaffected_reports"]))
    for label, key in (("CẦN USER QUYẾT", "queue_user_decision"),):
        print(f"-- {label}: {len(impact[key])}")
        for item in impact[key]:
            print(f"   {item['report']}: {item['why']}")
    print(f"-- ghi chú ở báo cáo kế tiếp (bậc 2): {len(impact['note_next_report'])}"
          + (": " + ", ".join(impact["note_next_report"]) if impact["note_next_report"] else ""))
    print(f"-- chỉ sửa từ nay (bậc 0–1): {len(impact['fix_forward_only'])}")
    sc = impact["scan_scope"]
    print(f"-- phạm vi quét: {sc['n_report_files']} file báo cáo trong {sc['reports_dir']}; "
          f"{sc['n_eod_messages']} tin EOD từ {len(sc['eod_log_files'])} log ({sc['eod_log_glob']}"
          + (f", ngày {sc['eod_dates'][0]} → {sc['eod_dates'][1]}" if sc["eod_dates"] else "") + ")")
    for msg in impact["unparsed_report_names"]:
        print(f"⚠️ KHÔNG đọc được kỳ của báo cáo (chưa đo): {msg}")
    if impact["skipped_non_md"]:
        print(f"ℹ️ bỏ qua {len(impact['skipped_non_md'])} file không phải .md: "
              + ", ".join(impact["skipped_non_md"]))
    print("Phép đo = tác động của THAY ĐỔI này (dữ liệu cũ tính lại → dữ liệu mới tính lại); KHÔNG "
          "đo sai số của số đã in (trừ tin EOD: có so thêm với số in). Báo cáo ngày trước 2026-08-17 chỉ có "
          "trên Discord: chỉ quét được phần còn trong log EOD.")
    print("Công cụ này KHÔNG gửi, KHÔNG sửa, KHÔNG phát hành lại báo cáo nào.")


def cmd_impact(args) -> int:
    old_path = nav_history_path(args.account, args.old_nav_dir)
    old_bytes = _read_bytes(old_path)
    fields, old_table, old = _load_side(args.account, old_bytes, old_path, args.inception_path,
                                        args.flows_path)
    correction_md5 = None
    if args.correction:
        items, correction_md5 = load_correction(args.correction, args.account)
        new_table, changes = apply_corrections(fields, old_table, items)
        new_bytes = write_nav_table(fields, new_table, line_terminator(old_bytes))
    else:
        new_path = nav_history_path(args.account, args.new_nav_dir)
        new_bytes = _read_bytes(new_path)
        _, new_table = read_nav_table(new_bytes, new_path)
        changes = None
    new = Side(args.account, new_table,
               nul.load_inception(args.account, args.new_inception_path or args.inception_path),
               acf.load_flows(args.account, flows_path=args.new_flows_path or args.flows_path,
                              require_file=True))
    changed = _changed_dates(old_table, new_table)
    eod_glob = (args.eod_logs if args.eod_logs is not None else os.path.join(
        os.path.dirname(os.path.abspath(args.reports_dir)), "logs", EOD_LOG_GLOB))
    impact = build_impact(args.account, old, new, changed, args.reports_dir, eod_glob or None)
    impact.update({
        "generated_at_ict": datetime.datetime.now(ICT).isoformat(timespec="seconds"),
        "old_nav_history_md5": _md5(old_bytes), "new_nav_history_md5": _md5(new_bytes),
        "correction_md5": correction_md5,
        "changed_rows": [dict(v, date=d.isoformat()) for d, v in sorted(changed.items())],
        "corrections_applied": changes,
        "ledger_binding": None,
    })
    if args.sealed_ledger:
        sealed_bytes = _read_bytes(args.sealed_ledger)
        sealed = nul._parse_sealed(sealed_bytes.decode("utf-8"), args.sealed_ledger)
        if not sealed:
            raise RestatementError(f"{args.sealed_ledger}: sổ đã chốt không có dòng nào")
        impact["ledger_binding"] = {
            "sealed_ledger": os.path.basename(args.sealed_ledger), "sealed_md5": _md5(sealed_bytes),
            "sealed_last_date": sealed[-1]["date"].isoformat(),
            "restated_md5": _md5(nul._content(new.ledger, sealed[-1]["date"])),
            "n_ledger_diffs": len(nul.diff_against_sealed(new.ledger, sealed))}
    _print_table(impact, args.all)
    if args.out:
        tmp = f"{args.out}.tmp.{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(impact, f, ensure_ascii=False, indent=1, default=str)
        os.replace(tmp, args.out)
        print(f"báo cáo tác động: {args.out} (md5 {_md5(_read_bytes(args.out))})")
    return 0


def _clock() -> datetime.datetime:
    return datetime.datetime.now(ICT)


def _now_ict(nav_dir: str) -> datetime.datetime:
    """Giờ ICT dùng cho khung `apply`. `TEST_NOW_ENV` (chỉ selfcheck) thay được giờ, TRỪ KHI
    `nav_dir` là chính thư mục dữ liệu thật — ở đó biến này làm lệnh bị từ chối."""
    raw = os.environ.get(TEST_NOW_ENV)
    if raw is None:
        return _clock().astimezone(ICT)         # so khung theo giờ ICT, kể cả khi đồng hồ trả UTC
    if nul.is_canonical_dir(nav_dir):
        raise RestatementError(
            f"biến môi trường {TEST_NOW_ENV}={raw!r} đang đặt trong khi --nav-dir {nav_dir} là thư "
            f"mục dữ liệu thật — biến này chỉ dành cho selfcheck. Gỡ biến rồi chạy lại.")
    try:
        fake = datetime.datetime.fromisoformat(raw)
    except ValueError as exc:
        raise RestatementError(f"{TEST_NOW_ENV}={raw!r} không phải giờ ISO ({exc})") from exc
    print(f"⚠️ ĐANG DÙNG GIỜ GIẢ {TEST_NOW_ENV}={raw} (chỉ selfcheck)", file=sys.stderr)
    return fake.replace(tzinfo=ICT) if fake.tzinfo is None else fake.astimezone(ICT)


def _backup_nav_history(nav_dir: str, account: str, data: bytes, now: datetime.datetime) -> str:
    """Chép `data` (byte nav_history TRƯỚC khi áp) vào kho sao lưu chỉ-thêm; trả đường dẫn. Đã có
    bản sao lưu của đúng byte này (lần áp trước chết giữa chừng) ⇒ dùng lại, không chép bản hai."""
    folder = os.path.join(nav_dir, BACKUP_DIR)
    os.makedirs(folder, exist_ok=True)
    digest = _md5(data)
    for name in sorted(os.listdir(folder)):
        if (name.startswith(f"{account}_") and name.endswith(f"_{digest}.csv")
                and _read_bytes(os.path.join(folder, name)) == data):
            return os.path.join(folder, name)
    path = os.path.join(folder, f"{account}_{now:%Y%m%dT%H%M%S}_{digest}.csv")
    try:
        with open(path, "xb") as f:                 # "x": không bao giờ ghi đè bản sao lưu cũ
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
    except FileExistsError as exc:
        raise RestatementError(
            f"{path} đã tồn tại với nội dung KHÁC byte nav_history đang đọc (md5 {digest}) — kho "
            f"sao lưu là chỉ-thêm; kiểm bằng tay, không ghi đè.") from exc
    return path


def _append_log(log: str, record: dict) -> None:
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def cmd_apply(args) -> int:
    path = nav_history_path(args.account, args.nav_dir)
    if nul.is_real_data_dir(args.nav_dir) and not args.real_data:
        raise ApplyRefused(
            f"TỪ CHỐI ghi đính chính vào thư mục dữ liệu thật {args.nav_dir} (cây dữ liệu thật của "
            f"máy, hoặc thư mục có dnse_raw_*.jsonl) khi không có --real-data (thao tác của Mike "
            f"sau khi user duyệt).")
    if not str(args.approved_by or "").strip():
        raise RestatementError("apply cần --approved-by (không rỗng)")
    items, correction_md5 = load_correction(args.correction, args.account)
    report_bytes = _read_bytes(args.impact_report)
    try:
        report = json.loads(report_bytes.decode("utf-8"))
        bound = (report["account"], report["correction_md5"], report["old_nav_history_md5"],
                 report["new_nav_history_md5"])
    except (ValueError, KeyError, TypeError) as exc:
        raise RestatementError(f"{args.impact_report}: không phải báo cáo tác động của công cụ "
                               f"này ({type(exc).__name__}: {exc})") from exc
    cur_bytes = _read_bytes(path)
    fields, table = read_nav_table(cur_bytes, path)
    new_table, changes = apply_corrections(fields, table, items)
    new_bytes = write_nav_table(fields, new_table, line_terminator(cur_bytes))
    if (bound[0], bound[1]) != (args.account, correction_md5):
        raise RestatementError(
            f"{args.impact_report} là báo cáo tác động của (tài khoản, md5 file đính chính) = "
            f"{bound[:2]}, không phải của {(args.account, correction_md5)} — đo lại tác động cho "
            f"đúng file đính chính này.")
    if _md5(cur_bytes) == bound[3] and all(c.get("already") for c in changes):
        print(f"ĐÃ ÁP từ trước: {path} đang mang md5 sau đính chính {bound[3]} — không ghi gì.")
        return 0
    if (_md5(cur_bytes), _md5(new_bytes)) != (bound[2], bound[3]):
        raise RestatementError(
            f"{path}: md5 hiện có {_md5(cur_bytes)} / sau khi áp {_md5(new_bytes)} khác cặp "
            f"({bound[2]} → {bound[3]}) mà báo cáo tác động đã đo ⇒ nav_history đã đổi từ lúc đo. "
            f"Chạy lại impact rồi trình duyệt lại.")
    now = _now_ict(args.nav_dir)
    lo, hi = APPLY_WINDOW_ICT
    if not lo <= now.time().replace(tzinfo=None) <= hi:
        raise RestatementError(
            f"TỪ CHỐI áp lúc {now:%Y-%m-%d %H:%M:%S} ICT: chỉ áp đính chính trong khung "
            f"{lo:%H:%M}–{hi:%H:%M} ICT. nav_history bị daily_nav_snapshot.py ghi lại lúc "
            f"19:00–21:45 (nav_sync_retry mỗi 15'), 19:10 (EOD), 19:50 (+2 retry) và không có khoá "
            f"chung với đường ghi đó ⇒ áp ngoài khung có thể bị ghi đè mất. KHÔNG ghi gì.")
    backup = _backup_nav_history(args.nav_dir, args.account, cur_bytes, now)
    record = {"account": args.account,
              "applied_at_ict": now.isoformat(timespec="seconds"),
              "approved_by": args.approved_by.strip(), "correction_md5": correction_md5,
              "impact_report_md5": _md5(report_bytes), "md5_before": bound[2],
              "md5_after": bound[3], "backup": os.path.relpath(backup, args.nav_dir),
              "changes": [dict(c, reason=i["reason"], evidence=i["evidence"])
                          for c, i in zip(changes, items)]}
    log = os.path.join(args.nav_dir, AUDIT_LOG)
    # Nhật ký TRƯỚC, nav_history SAU. Chết giữa hai bước ⇒ lần chạy lại thấy đúng bản ghi này đã
    # có (cùng tài khoản, cùng file đính chính, cùng cặp md5, chưa bị huỷ) và chỉ ghi nốt file,
    # không ghi bản ghi thứ hai.
    key = ("account", "correction_md5", "md5_before", "md5_after")
    pending = False
    if os.path.exists(log):
        with open(log, "r", encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        if lines:
            try:
                last = json.loads(lines[-1])
            except ValueError as exc:
                raise RestatementError(f"{log}: dòng cuối không đọc được ({exc}) — nhật ký đính "
                                       f"chính hỏng, kiểm bằng tay trước khi ghi tiếp") from exc
            pending = (all(last.get(k) == record[k] for k in key)
                       and last.get("status") != "aborted")
    if not pending:
        _append_log(log, record)
    tmp = f"{path}.tmp.{os.getpid()}"
    try:
        with open(tmp, "wb") as f:
            f.write(new_bytes)
            f.flush()
            os.fsync(f.fileno())
        # Không có khoá chung với daily_nav_snapshot._write_nav_history ⇒ đọc lại NGAY trước khi
        # thay: file đổi từ lúc đọc thì bỏ, không đè lên bản ghi mới của snapshot.
        seen = _md5(_read_bytes(path))
        if seen != bound[2]:
            _append_log(log, {k: record[k] for k in key} | {
                "status": "aborted", "aborted_at_ict": _now_ict(args.nav_dir).isoformat(
                    timespec="seconds"), "md5_seen": seen})
            raise RestatementError(
                f"{path}: md5 đọc lại ngay trước khi ghi là {seen}, khác {bound[2]} lúc bắt đầu ⇒ "
                f"có tiến trình khác vừa ghi nav_history. KHÔNG ghi; nhật ký đã thêm bản ghi "
                f"'aborted'. Chạy lại impact trên file hiện tại rồi trình duyệt lại.")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    print(f"ĐÃ ÁP {len(changes)} đính chính vào {path}: md5 {bound[2]} → {bound[3]}; nhật ký {log}")
    for c in changes:
        old_nav = c["old"]["nav"] if c["old"] else "—"
        new_nav = c["new"]["nav"] if c["new"] else "—"
        print(f"   {c['op']} {c['date']}: nav {old_nav} → {new_nav}")
    print(f"sao lưu trước khi áp: {backup} (md5 {bound[2]})\n"
          f"ĐƯỜNG LUI — TRƯỚC khi chốt sổ: cp {backup} {path} rồi áp một đính chính NGƯỢC để nhật "
          f"ký ghi nhận; SAU khi chốt sổ: chỉ còn đường đính chính (nav_unit_ledger.py --restate).")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    imp = sub.add_parser("impact", help="đo tác động lên báo cáo đã gửi (chỉ đọc)")
    imp.add_argument("--account", required=True)
    imp.add_argument("--old-nav-dir", default=nul.NAV_HISTORY_DIR)
    imp.add_argument("--new-nav-dir")
    imp.add_argument("--correction")
    imp.add_argument("--inception-path", default=nul.INCEPTION_PATH)
    imp.add_argument("--new-inception-path")
    imp.add_argument("--flows-path", default=acf.FLOWS_PATH)
    imp.add_argument("--new-flows-path")
    imp.add_argument("--reports-dir", default=REPORTS_DIR)
    imp.add_argument("--sealed-ledger", help="sổ đơn vị đã chốt mà bản đính chính này sẽ thay")
    imp.add_argument("--eod-logs", help="glob log tin EOD Discord (mặc định <thư mục cha của "
                                        "--reports-dir>/logs/eod_trading_report.log*; '' = không quét)")
    imp.add_argument("--out")
    imp.add_argument("--all", action="store_true", help="in cả báo cáo không đổi")
    app = sub.add_parser("apply", help="ghi đính chính vào nav_history của --nav-dir")
    app.add_argument("--account", required=True)
    app.add_argument("--nav-dir", required=True)
    app.add_argument("--correction", required=True)
    app.add_argument("--impact-report", required=True)
    app.add_argument("--approved-by", required=True)
    app.add_argument("--real-data", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "impact":
            if bool(args.correction) == bool(args.new_nav_dir):
                ap.error("impact cần ĐÚNG MỘT trong --correction (dòng bị sửa) hoặc --new-nav-dir "
                         "(sổ mới)")
            return cmd_impact(args)
        return cmd_apply(args)
    except ApplyRefused as e:
        print(f"fund_restatement: {e}", file=sys.stderr)
        return 3
    except (RestatementError, FileNotFoundError, ValueError, KeyError) as e:
        print(f"LỖI fund_restatement [{type(e).__name__}]: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
