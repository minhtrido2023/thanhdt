#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sổ ĐƠN VỊ QUỸ của một account — chuỗi "giá một đơn vị quỹ" chốt theo ngày. `build_ledger` là
công thức DUY NHẤT cho tỉ suất theo kỳ (`nav_period_returns.py` lấy tỉ suất = tỉ số hai giá đơn vị
của chuỗi dựng trong bộ nhớ); file sổ trên đĩa chỉ là BẢN ĐỐI CHỨNG, chưa có trước bước 3.

Chính sách: `kb/projects/fund-unit-performance-policy-20261010.md` (user duyệt 2026-10-10) —
tài khoản quản lý đo như một quỹ mở. Dựng từ ba nguồn, không nguồn nào khác:
  · `data/execution_logs/nav_history_{account}.csv`  — NAV chốt cuối ngày (+ cờ `nav_is_estimate`)
  · `data/account_cash_flows.json`                   — nạp/rút (người ghi, kèm bằng chứng)
  · `data/account_inception.json`                    — mốc khởi điểm + vốn khởi điểm

QUY TẮC CHỐT (một chỗ duy nhất định nghĩa nó — `build_ledger`):
  · Khởi điểm: giá 10.000 đ/đơn vị tại `inception_date`, số đơn vị = `starting_capital`/10.000.
  · Nạp ⇒ PHÁT HÀNH đơn vị, rút ⇒ HUỶ đơn vị, luôn theo một GIÁ CHỐT; giá đơn vị không đổi vì
    dòng tiền, chỉ đổi vì lãi/lỗ.
  · Quy ước của từng dòng tiền do `account_cash_flows.assign_flow` SUY từ ngày + giờ khai và
    `balance_ts` của nav_history (người khai không chọn): tiền giao dịch ở giá chốt GẦN NHẤT
    TRƯỚC thời điểm tiền vào/ra.
  · "eod" trên dòng R (tiền tới SAU giờ đóng cửa phiên R, trước khi chụp NAV của R):
        giá_R = (nav_R − tiền_eod_R) / đơn_vị_trước ;  đơn_vị += tiền_eod_R / giá_R
    `nav_R` ĐÃ chứa khoản tiền đó nên phải trừ ra trước khi chia.
  · "bod" trên dòng R (tiền tới trước/trong phiên R): giao dịch ở giá chốt của dòng LIỀN TRƯỚC.
        đơn_vị += tiền_bod_R / giá_{R−1} ;  giá_R = nav_R / đơn_vị
  · Cả hai cùng dòng: bod trước, eod sau ⇒ giá_R/giá_{R−1} = (nav_R − eod)/(nav_{R−1} + bod).
  · Bất biến mỗi dòng: đơn_vị × giá = nav (sai số dấu phẩy động, ≪ 1 đồng).
  · nav_history phải tăng NGHIÊM NGẶT theo ngày (trùng ngày ⇒ từ chối).

SỔ TRÊN ĐĨA LÀ CHỈ-GHI-THÊM: `nav_unit_ledger_{account}.csv`. `--seal` chỉ THÊM dòng mới vào
cuối (đọc file MỘT lần dưới khoá `fcntl.flock`, ghi qua file tạm + `os.replace`). Dựng lại mà
một dòng ĐÃ CHỐT khác đi (NAV nguồn bị sửa, dòng tiền khai lùi ngày, dòng bị xoá/chen) ⇒ rc=2,
in từng dòng lệch bao nhiêu, KHÔNG ghi gì.

HAI CHẾ ĐỘ CHỐT (bước 3 của chính sách, 2026-10-14):
  · Thư mục thử/research (`--ledger-dir D`): như trên, không manifest.
  · KHO BẤT BIẾN (coding_guidelines §8c) — BẮT BUỘC với thư mục dữ liệu thật, tự bật khi thư mục
    đã có manifest, hoặc `--immutable`: mỗi lần chốt ghi một bản ghi vào
    `nav_unit_ledger_{account}.csv.manifest.jsonl` (chỉ-thêm; md5 trước/sau nối thành chuỗi).
    Mọi lần đọc/chốt kiểm md5 file == md5 của bản ghi cuối ⇒ cắt bớt dòng cuối, xoá file, sửa tay
    đều bị bắt (rc=2) — thứ mà so từng dòng không thấy. Chốt mà không có dòng mới (md5 trùng) ⇒
    rc=2, không có `--force`. Cổng trước khi chốt: chỉ chốt ngày TRƯỚC hôm nay (ICT — dòng hôm
    nay còn bị `daily_nav_snapshot.py` ghi đè); không thiếu dòng của phiên nào trong đoạn chốt;
    `balance_ts` đọc được; dòng chụp TRƯỚC giờ đóng cửa của chính phiên nó phải được nhận tường
    minh (`--accept-preclose NGÀY=lý do`; manifest ghi {lý do, balance_ts, nav} của ĐÚNG dòng
    được nhận — dòng đó đổi balance_ts hoặc NAV thì lời nhận hết hiệu lực, phải nhận lại); dòng
    chụp SAU khi phiên kế đã đóng cửa ⇒ từ chối (phải đính chính nav_history trước).
    Thứ tự ghi: manifest TRƯỚC, file sổ SAU ⇒ chết giữa chừng thì lần chạy kế thấy md5 file ==
    `md5_before` của bản ghi cuối và HOÀN TẤT đúng lần chốt dở (chỉ khi dựng lại ra đúng md5 đã
    ghi); không đoán, không ghi bản ghi thứ hai.
  · Thư mục dữ liệu thật: phải có `--real-data` (không phải `--force`: mọi cổng trên vẫn chạy);
    thiếu ⇒ rc=3. "Thật" = cây cố định `CANONICAL_REAL_DIR` của máy, HOẶC mọi thư mục có
    `dnse_raw_*.jsonl`, HOẶC NAV_HISTORY_DIR suy từ WC_ROOT (`is_real_data_dir`) — đổi WC_ROOT
    không lách được. Người chạy là Mike sau khi user duyệt — xem `kb/data_registry/trading-bot/
    nav_unit_ledger.md`. Mỗi lần chốt/đính chính in một dòng máy-đọc-được
    `SEAL_MD5 <account> <md5 file sổ> <md5 manifest>` để post lên bus làm mốc NGOÀI kho.
ĐÍNH CHÍNH SỔ ĐÃ CHỐT (`--restate`): lịch sử đổi CÓ CHỦ ĐÍCH (sửa nav_history, backfill, khai dòng
tiền lùi ngày) không bao giờ sửa tại chỗ. Phải có báo cáo tác động của `fund_restatement.py impact`
mang ĐÚNG md5 sổ đang chốt và md5 sổ sau đính chính (báo cáo của một thay đổi khác ⇒ từ chối),
`--reason`, `--approved-by`. Sổ cũ được chép nguyên byte sang
`nav_unit_ledger_{account}.csv.superseded.<seq>.<md5>.csv` rồi mới thay; manifest ghi bản ghi
`restate` (md5 cũ, md5 mới, file lưu, lý do, người duyệt, md5 báo cáo tác động, từng dòng lệch).
`nav_period_returns.py` KHÔNG đọc sổ trên đĩa: tỉ suất luôn tính từ chuỗi dựng trong bộ nhớ.

Dùng:
    python3 mike/bin/nav_unit_ledger.py --account SpaceX                      # dựng + in
    python3 mike/bin/nav_unit_ledger.py --account SpaceX --ledger-dir D       # + đối chiếu sổ ở D
    python3 mike/bin/nav_unit_ledger.py --account SpaceX --ledger-dir D --seal
    python3 mike/bin/nav_unit_ledger.py --account SpaceX --ledger-dir D --immutable --seal \
        [--accept-preclose 2026-08-24="lý do"]
    python3 mike/bin/nav_unit_ledger.py --account SpaceX --ledger-dir D --restate \
        --impact-report impact.json --reason "..." --approved-by "..."
Selfcheck: python3 mike/bin/nav_unit_ledger_selfcheck.py
"""
import argparse
import csv
import datetime
import fcntl
import hashlib
import json
import math
import os
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import account_cash_flows as _acf  # noqa: E402
from account_cash_flows import (NavRow, attach_flows_to_rows,  # noqa: E402,F401
                                load_flows, require_strictly_increasing)
from wc_paths import find_wc_root  # noqa: E402

WC_ROOT = find_wc_root(__file__)
INCEPTION_PATH = os.path.join(WC_ROOT, "data", "account_inception.json")
NAV_HISTORY_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
MANIFEST_SUFFIX = ".manifest.jsonl"

UNIT_PRICE_0 = 10_000.0
LEDGER_FIELDS = ["date", "nav", "flow_bod_vnd", "flow_eod_vnd", "units_issued", "units",
                 "unit_price", "nav_is_estimate"]
# Cột NGUỒN (nav, dòng tiền, cờ) so ĐÚNG TỪNG GIÁ TRỊ. Cột SUY RA (đơn vị, giá) so tương đối:
# 1e-10 ≈ 0,1 đồng trên NAV 1 tỷ — lớn hơn nhiễu dấu phẩy động (~1e-15) năm bậc, nhỏ hơn thay
# đổi thật nhỏ nhất (NAV lệch 1 đồng = 1e-9) một bậc; mà NAV lệch 1 đồng thì cột `nav` đã bắt.
DERIVED_REL_TOL = 1e-10


class LedgerDriftError(ValueError):
    """Chuỗi dựng lại KHÁC sổ đã chốt. `.diffs` = từng dòng lệch, đã viết sẵn cho người đọc."""

    def __init__(self, path, diffs):
        self.path = path
        self.diffs = diffs
        super().__init__(f"sổ đơn vị đã chốt {path} KHÁC chuỗi dựng lại ở {len(diffs)} chỗ:\n  "
                         + "\n  ".join(diffs))


class SealRefused(ValueError):
    """Từ chối chốt sổ vào thư mục dữ liệu thật khi không có `--real-data` (rc=3)."""


class SealIntegrityError(ValueError):
    """Kho bất biến: file sổ / manifest không còn là thứ công cụ này đã ghi (md5 lệch, chuỗi
    manifest đứt, lần chốt dở không hoàn tất được)."""


class NothingToSeal(ValueError):
    """Kho bất biến: không có dòng mới để chốt / không có gì để đính chính (md5 sẽ trùng)."""


class SealGateError(ValueError):
    """Kho bất biến: đoạn sắp chốt chưa đủ điều kiện (thiếu phiên, dòng chụp trước đóng cửa…)."""


def _parse_date(s: str) -> datetime.date:
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


def load_inception(account: str, inception_path: str = INCEPTION_PATH) -> dict:
    with open(inception_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if account not in cfg:
        raise ValueError(f"account '{account}' không có entry trong {inception_path}")
    return cfg[account]


def load_nav_history(account: str, nav_dir: str = NAV_HISTORY_DIR) -> list:
    """Trả list NavRow (= [(date, nav), ...]) tăng dần theo ngày."""
    path = os.path.join(nav_dir, f"nav_history_{account}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"thiếu {path}")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            if not rec.get("date") or not rec.get("nav"):
                continue
            rows.append(NavRow(_parse_date(rec["date"]), float(rec["nav"]),
                               is_estimate=(rec.get("nav_is_estimate") == "True"),
                               balance_ts=(rec.get("balance_ts") or None)))
    rows.sort(key=lambda r: r[0])
    if not rows:
        raise ValueError(f"{path} rỗng")
    return rows


def _inception_baseline(rows: list, inception: dict):
    """(from_date, nav0) khởi điểm thật: starting_capital nếu có, else dòng đầu tiên."""
    starting_capital = inception.get("starting_capital")
    if starting_capital is not None:
        return _parse_date(inception["inception_date"]), float(starting_capital)
    first_date, first_nav = rows[0]
    return first_date, first_nav


def build_ledger(rows: list, flows: list, inception_from: datetime.date,
                 inception_nav0: float) -> tuple:
    """Dựng sổ đơn vị. Trả `(ledger, info)`.

    `ledger`: list dict tăng dần theo ngày — dòng 0 là mốc khởi điểm (`inception_from`, giá
    10.000), sau đó mỗi dòng nav_history có date > `inception_from` một dòng. Khoá: date, nav,
    flow_bod_vnd, flow_eod_vnd, units_issued, units, unit_price, nav_is_estimate, flows.
    `info`: {"dropped": flow có date <= mốc khởi điểm (đã nằm trong vốn khởi điểm, KHÔNG phải
    dòng tiền), "pending": flow TREO — chưa dòng nav_history nào chụp sau thời điểm tiền vào/ra}.
    ⚠️ "dropped" lọc theo NGÀY, không theo giờ, và mốc khởi điểm được coi là giá CHỐT của
    `inception_date`. ZaloPay: mốc = balances 2026-07-06T21:45:43 (sau đóng cửa 07-06) ⇒ đúng,
    chỉ hở khe 21:45–24:00 ngày 07-06. SpaceX: mốc 1 tỷ là số dư SÁNG 2026-07-01 (09:30, trước
    phiên đầu) ⇒ tiền vào 07-01 sau 09:30 bị loại oan, và tiền vào 07-02 trước lần chụp 09:46
    được phát hành ở 10.000, thiếu biến động phiên 07-01 (~0,5%) mà không lỗi. Cả hai khe nằm
    trong quá khứ, sổ dòng tiền thật rỗng; hiện ở `dropped_flows`, không tự sửa ở đây.
    `flows` của mỗi dòng sổ là bản sao đã gán (`timing` = quy ước suy ra, `session_date`).
    """
    if not (math.isfinite(inception_nav0) and inception_nav0 > 0):
        raise ValueError(f"vốn khởi điểm phải > 0 và hữu hạn, được {inception_nav0}")
    require_strictly_increasing(rows)
    nav_rows = [r for r in rows if r[0] > inception_from]
    dropped = [f for f in flows if f["date"] <= inception_from]
    by_date = attach_flows_to_rows(nav_rows, [f for f in flows if f["date"] > inception_from],
                                   inception_from)
    pending = by_date.pop(None, [])

    base_est = next((getattr(r, "is_estimate", False) for r in rows if r[0] == inception_from),
                    False)
    units = inception_nav0 / UNIT_PRICE_0
    price = UNIT_PRICE_0
    ledger = [{"date": inception_from, "nav": inception_nav0, "flow_bod_vnd": 0.0,
               "flow_eod_vnd": 0.0, "units_issued": 0.0, "units": units, "unit_price": price,
               "nav_is_estimate": base_est, "flows": [], "balance_ts": None}]
    for row in nav_rows:
        d, nav = row[0], row[1]
        if not math.isfinite(nav):
            raise ValueError(f"{d}: nav của nav_history không phải số hữu hạn ({nav!r}) — không "
                             f"tính được giá đơn vị từ dòng này trở đi; sửa nav_history")
        day = by_date.get(d, [])
        f_bod = sum(f["amount_vnd"] for f in day if f["timing"] == "bod")
        f_eod = sum(f["amount_vnd"] for f in day if f["timing"] == "eod")
        before = units
        units += f_bod / price                      # bod: giao dịch ở giá chốt phiên liền trước
        if units <= 0:
            raise ValueError(f"{d}: rút đầu ngày {f_bod:,.0f} VND huỷ hết đơn vị quỹ (còn "
                             f"{units:.6f}) — không còn giá đơn vị; kỳ này phải chia thủ công")
        price = (nav - f_eod) / units               # giá chốt cuối ngày, CHƯA tính dòng tiền eod
        if price <= 0:
            raise ValueError(f"{d}: nav {nav:,.0f} − dòng tiền eod {f_eod:,.0f} <= 0 — không "
                             f"tính được giá đơn vị (số tiền khai có đúng không?)")
        units += f_eod / price                      # eod: giao dịch ở giá vừa chốt
        if units <= 0:
            raise ValueError(f"{d}: rút cuối ngày {f_eod:,.0f} VND huỷ hết đơn vị quỹ (còn "
                             f"{units:.6f}) — không còn giá đơn vị; kỳ này phải chia thủ công")
        ledger.append({"date": d, "nav": nav, "flow_bod_vnd": f_bod, "flow_eod_vnd": f_eod,
                       "units_issued": units - before, "units": units, "unit_price": price,
                       "nav_is_estimate": bool(getattr(row, "is_estimate", False)),
                       "flows": day, "balance_ts": getattr(row, "balance_ts", None)})
    return ledger, {"dropped": dropped, "pending": pending}


# ---------------------------------------------------------------- sổ trên đĩa (chỉ-ghi-thêm)
def ledger_path(account: str, ledger_dir: str) -> str:
    return os.path.join(ledger_dir, f"nav_unit_ledger_{account}.csv")


def _csv_line(row: dict) -> str:
    return ",".join([row["date"].isoformat(), repr(float(row["nav"])),
                     repr(float(row["flow_bod_vnd"])), repr(float(row["flow_eod_vnd"])),
                     repr(float(row["units_issued"])), repr(float(row["units"])),
                     repr(float(row["unit_price"])), str(bool(row["nav_is_estimate"]))]) + "\n"


def _parse_sealed(text: str, path: str) -> list:
    if text and not text.endswith("\n"):
        raise ValueError(f"{path}: dòng cuối không kết thúc bằng xuống dòng (ghi dở?) — không "
                         f"đọc tiếp, kiểm file bằng tay")
    lines = text.splitlines()
    if not lines or lines[0].split(",") != LEDGER_FIELDS:
        raise ValueError(f"{path}: header {lines[:1]} khác schema {LEDGER_FIELDS}")
    out = []
    for n, line in enumerate(lines[1:], start=2):
        parts = line.split(",")
        try:
            if len(parts) != len(LEDGER_FIELDS) or parts[7] not in ("True", "False"):
                raise ValueError("sai số cột hoặc cờ nav_is_estimate")
            rec = {"date": _parse_date(parts[0]), "nav_is_estimate": parts[7] == "True"}
            for key, raw in zip(LEDGER_FIELDS[1:7], parts[1:7]):
                rec[key] = float(raw)
                if not math.isfinite(rec[key]):
                    raise ValueError(f"{key}={raw} không phải số hữu hạn")
        except ValueError as exc:
            raise ValueError(f"{path} dòng {n}: không đọc được ({exc}): {line!r}") from exc
        if out and rec["date"] <= out[-1]["date"]:
            raise ValueError(f"{path} dòng {n}: ngày {rec['date']} không tăng dần")
        out.append(rec)
    return out


def _read_text(path: str):
    """Nội dung file sổ, hoặc None nếu chưa có file."""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def read_sealed(path: str) -> list:
    """Dòng đã chốt, tăng dần. File không tồn tại ⇒ [] (chưa chốt dòng nào). File hỏng ⇒ raise:
    sổ đã chốt mà đọc không ra thì không được coi như chưa có sổ."""
    text = _read_text(path)
    return [] if text is None else _parse_sealed(text, path)


def diff_against_sealed(ledger: list, sealed: list) -> list:
    """Mọi chỗ chuỗi dựng lại KHÁC các dòng đã chốt. [] = khớp."""
    if not sealed:
        return []
    diffs = []
    last = sealed[-1]["date"]
    built = {r["date"]: r for r in ledger if r["date"] <= last}
    have = {r["date"] for r in sealed}
    for d in sorted(set(built) - have):
        diffs.append(f"{d}: dòng CHEN VÀO quá khứ — chuỗi dựng lại có ngày này (nav "
                     f"{built[d]['nav']:,.0f}) nhưng sổ đã chốt tới {last} thì không")
    for old in sealed:
        d = old["date"]
        new = built.get(d)
        if new is None:
            diffs.append(f"{d}: dòng đã chốt (nav {old['nav']:,.0f}, giá {old['unit_price']:.4f}) "
                         f"KHÔNG còn trong chuỗi dựng lại")
            continue
        for key in ("nav", "flow_bod_vnd", "flow_eod_vnd"):
            if new[key] != old[key]:
                diffs.append(f"{d} {key}: đã chốt {old[key]:,.2f} → dựng lại {new[key]:,.2f} "
                             f"(lệch {new[key] - old[key]:+,.2f} VND)")
        if bool(new["nav_is_estimate"]) != old["nav_is_estimate"]:
            diffs.append(f"{d} nav_is_estimate: đã chốt {old['nav_is_estimate']} → dựng lại "
                         f"{bool(new['nav_is_estimate'])}")
        for key in ("units_issued", "units", "unit_price"):
            # nan/inf ở giá trị đã chốt phải tính là LỆCH: `abs(x − nan) > tol` luôn False, và
            # với inf thì dung sai tương đối cũng thành inf — nên kiểm hữu hạn trước, so `<=` sau.
            if not (math.isfinite(old[key])
                    and abs(new[key] - old[key]) <= DERIVED_REL_TOL * max(abs(old[key]), 1.0)):
                rel = (new[key] / old[key] - 1) * 100 if old[key] else float("inf")
                diffs.append(f"{d} {key}: đã chốt {old[key]!r} → dựng lại {new[key]!r} "
                             f"(lệch {new[key] - old[key]:+.6f} = {rel:+.6f}%)")
    return diffs


def _seal_locked(path, ledger, asof, write):
    old_text = _read_text(path)                 # đọc MỘT lần: vừa để đối chiếu, vừa để ghi lại
    sealed = [] if old_text is None else _parse_sealed(old_text, path)
    diffs = diff_against_sealed(ledger, sealed)
    if diffs:
        raise LedgerDriftError(path, diffs)
    last = sealed[-1]["date"] if sealed else None
    new = [r for r in ledger if (last is None or r["date"] > last)
           and (asof is None or r["date"] <= asof)]
    if not write or not new:
        return sealed, []
    if old_text is None:
        old_text = ",".join(LEDGER_FIELDS) + "\n"
    tmp = f"{path}.tmp.{os.getpid()}"
    try:
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(old_text + "".join(_csv_line(r) for r in new))    # byte cũ giữ NGUYÊN
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):                 # ghi dở ⇒ không để lại file tạm, sổ cũ nguyên vẹn
            os.remove(tmp)
    return sealed, new


# ---------------------------------------------------------------- kho bất biến (§8c)
# Cây dữ liệu thật của máy này — CỐ ĐỊNH, không suy từ WC_ROOT: đổi WC_ROOT sang sandbox không
# được làm thư mục thật thôi là "thật".
CANONICAL_REAL_DIR = "/home/trido/thanhdt/WorkingClaude/data/execution_logs"


def is_canonical_dir(directory: str) -> bool:
    """`directory` là CHÍNH thư mục dữ liệu thật: cây cố định của máy, hoặc NAV_HISTORY_DIR (suy
    từ WC_ROOT)."""
    real = os.path.realpath(os.path.abspath(directory))
    return real in (os.path.realpath(CANONICAL_REAL_DIR), os.path.realpath(NAV_HISTORY_DIR))


def is_real_data_dir(directory: str) -> bool:
    """Thư mục phải có `--real-data` mới được ghi: (a) cây cố định của máy, (b) MỌI thư mục chứa
    `dnse_raw_*.jsonl` (bản ghi broker — kể cả bản sao: ghi nhầm lên bản sao của cây thật cũng
    phải gọi tường minh), (c) NAV_HISTORY_DIR suy từ WC_ROOT."""
    if is_canonical_dir(directory):
        return True
    try:
        names = os.listdir(os.path.realpath(os.path.abspath(directory)))
    except OSError:                     # chưa có thư mục ⇒ không thể là nơi chứa bản ghi broker
        return False
    return any(n.startswith("dnse_raw_") and n.endswith(".jsonl") for n in names)


def _is_real_dir(path: str) -> bool:
    return is_real_data_dir(os.path.dirname(os.path.abspath(path)))


def manifest_path(path: str) -> str:
    return path + MANIFEST_SUFFIX


def _md5(data):
    return None if data is None else hashlib.md5(data).hexdigest()


def _read_bytes(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()


def read_manifest(path: str) -> list:
    """Bản ghi manifest của sổ `path`, cũ → mới. Chưa có file ⇒ []. Dòng không đọc được, hoặc
    `md5_before`/`seq` không nối với bản ghi trước ⇒ SealIntegrityError (manifest là chỉ-thêm)."""
    mp = manifest_path(path)
    if not os.path.exists(mp):
        return []
    out = []
    with open(mp, "r", encoding="utf-8") as f:
        for n, line in enumerate(f, start=1):
            try:
                rec = json.loads(line)
                for key in ("seq", "kind", "md5", "md5_before", "rows_total", "last_date"):
                    rec[key]
            except (ValueError, KeyError, TypeError) as exc:
                raise SealIntegrityError(
                    f"{mp} dòng {n}: không đọc được ({type(exc).__name__}: {exc}): "
                    f"{line[:120]!r}") from exc
            prev = out[-1]["md5"] if out else None
            if rec["md5_before"] != prev or rec["seq"] != len(out) + 1:
                raise SealIntegrityError(
                    f"{mp} dòng {n}: chuỗi manifest ĐỨT — bản ghi seq {rec['seq']} có md5_before "
                    f"{rec['md5_before']}, không nối với bản ghi trước (seq {len(out)}, md5 {prev}). "
                    f"Manifest là chỉ-thêm: có dòng bị xoá, sửa hoặc chen.")
            out.append(rec)
    return out


def _content(ledger: list, upto: datetime.date) -> bytes:
    """Nội dung file sổ dựng từ đầu cho mọi dòng có ngày <= `upto`."""
    return (",".join(LEDGER_FIELDS) + "\n"
            + "".join(_csv_line(r) for r in ledger if r["date"] <= upto)).encode("utf-8")


def _atomic_write(path: str, data: bytes) -> None:
    tmp = f"{path}.tmp.{os.getpid()}"
    try:
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _append_manifest(path: str, rec: dict) -> None:
    with open(manifest_path(path), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _pending_content(ledger: list, rec: dict, old: bytes) -> bytes:
    """Nội dung mà lần chốt `rec` (đã ghi manifest, chưa thay file) định ghi, dựng lại từ nguồn."""
    upto = _parse_date(rec["last_date"])
    if rec["kind"] == "restate":
        return _content(ledger, upto)
    if old is None:
        return _content(ledger, upto)
    last = _parse_sealed(old.decode("utf-8"), "sổ trước lần chốt dở")[-1]["date"]
    return old + "".join(_csv_line(r) for r in ledger if last < r["date"] <= upto).encode("utf-8")


def _vault_state(path: str, ledger: list, write: bool) -> tuple:
    """`(byte file sổ | None, dòng đã chốt, manifest, vừa_hoàn_tất_lần_chốt_dở)` của một sổ kho bất biến, SAU khi kiểm md5
    file == md5 bản ghi manifest cuối. md5 file == `md5_before` của bản ghi cuối = lần chốt đó
    đã ghi manifest nhưng chết trước khi thay file: khi `write` thì hoàn tất ĐÚNG lần đó (chỉ khi
    dựng lại ra đúng md5 đã ghi), không thì báo. Mọi lệch khác ⇒ SealIntegrityError."""
    manifest = read_manifest(path)
    old = _read_bytes(path)
    if not manifest:
        if old is not None:
            raise SealIntegrityError(
                f"{path}: có file sổ ({len(old)} byte, md5 {_md5(old)}) nhưng "
                f"{manifest_path(path)} không có bản ghi nào — file này không do chế độ kho bất "
                f"biến chốt. KHÔNG ghi gì; kiểm bằng tay.")
        return None, [], [], False
    last = manifest[-1]
    have = _md5(old)
    resumed = False
    if have != last["md5"]:
        seen = "KHÔNG có file" if old is None else f"{len(old)} byte"
        if have != last["md5_before"]:
            raise SealIntegrityError(
                f"{path}: md5 đọc được {have} ({seen}) khác md5 đã ghi ở manifest #{last['seq']} "
                f"({last['md5']}: {last['rows_total']} dòng tới {last['last_date']}) và khác cả md5 "
                f"trước lần chốt đó ({last['md5_before']}) ⇒ file sổ đã bị đổi NGOÀI công cụ (sửa "
                f"tay, cắt dòng, xoá, chép đè). KHÔNG ghi gì.")
        want = _pending_content(ledger, last, old)
        if _md5(want) != last["md5"]:
            raise SealIntegrityError(
                f"{path}: lần chốt #{last['seq']} ({last['kind']}) đã ghi manifest nhưng chưa thay "
                f"file sổ (md5 file {have} = md5 trước lần chốt); dựng lại bây giờ ra md5 "
                f"{_md5(want)}, khác {last['md5']} đã ghi ⇒ nguồn đã đổi từ lúc đó. Không hoàn tất "
                f"hộ; kiểm bằng tay.")
        if not write:
            raise SealIntegrityError(
                f"{path}: lần chốt #{last['seq']} ({last['kind']}) đã ghi manifest nhưng CHƯA thay "
                f"file sổ (chết giữa chừng). Chạy lại đúng lệnh chốt đó để hoàn tất; lệnh chỉ-đọc "
                f"này không ghi gì.")
        _atomic_write(path, want)
        old, resumed = want, True
    return old, _parse_sealed(old.decode("utf-8"), path), manifest, resumed


def _row_capture(row: dict):
    """(lúc chụp số dư | None, phiên đóng cửa gần nhất lúc chụp | None) của một dòng sổ."""
    ts = row.get("balance_ts")
    if not ts:
        return None, None
    try:
        snap = datetime.datetime.fromisoformat(str(ts))
    except ValueError:
        return None, None
    if snap.tzinfo is not None:
        snap = snap.astimezone(ICT).replace(tzinfo=None)
    return snap, _acf._last_session_closed_by(snap)


def seal_gate(ledger: list, start_date: datetime.date, new_rows: list, accept_preclose: dict,
              carried: dict = None) -> tuple:
    """Cổng của kho bất biến cho đoạn sắp chốt. Trả `(vấn đề chặn, lời nhận)`; lời nhận =
    {ngày ISO: {reason, balance_ts, nav}} — gắn với ĐÚNG dòng được nhận, không chỉ với ngày.
    `start_date`: ngày dòng đã chốt cuối (hoặc mốc khởi điểm) đứng ngay trước `new_rows`.
    `accept_preclose` = {ngày ISO: lý do} người gọi vừa gõ. `carried` = lời nhận của các lần chốt
    trước (dạng lưu trong manifest): chỉ còn hiệu lực khi dòng vẫn mang đúng `balance_ts` và `nav`
    lúc được nhận — dòng đã đổi thì phải nhận lại."""
    problems, accepted = [], {}
    carried = carried or {}
    have = {r["date"] for r in ledger}
    prev = start_date
    for row in new_rows:
        d = row["date"]
        gap = prev + datetime.timedelta(days=1)
        while gap < d:
            if gap not in have and _acf._is_session_day(gap):
                problems.append(
                    f"{gap}: nav_history THIẾU dòng của phiên này (nằm giữa {prev} và {d}) — chốt "
                    f"thì giá đơn vị {d} gộp biến động hai phiên và backfill về sau thành dòng "
                    f"chen. Backfill trước: daily_nav_snapshot.py --account <TK> --date {gap} "
                    f"--from-raw")
            gap += datetime.timedelta(days=1)
        prev = d
        if row["balance_ts"] is None and d == ledger[0]["date"]:
            continue                                    # mốc khởi điểm: không phải lần chụp nào
        snap, seen = _row_capture(row)
        if snap is None:
            problems.append(f"{d}: balance_ts không đọc được (đọc được: {row.get('balance_ts')!r}) "
                            f"— không biết NAV dòng này chụp lúc nào")
            continue
        session = _acf._is_session_day(d)
        want = d if session else _acf._last_session_closed_by(
            datetime.datetime.combine(d, datetime.time(0, 0)))
        if session and snap < datetime.datetime.combine(d, _acf.SESSION_CLOSE_ICT):
            key = d.isoformat()
            ident = {"balance_ts": row["balance_ts"], "nav": row["nav"]}
            old = carried.get(key)
            if key in accept_preclose:
                accepted[key] = dict(ident, reason=accept_preclose[key])
            elif isinstance(old, dict) and {k: old.get(k) for k in ident} == ident:
                accepted[key] = old
            elif old is not None:
                was = (f"balance_ts {old.get('balance_ts')!r}, NAV {old.get('nav')!r}"
                       if isinstance(old, dict) else "bản ghi cũ không ghi balance_ts/NAV")
                problems.append(
                    f"{d}: lời nhận --accept-preclose cũ ({was}) KHÔNG còn là của dòng này — dòng "
                    f"hiện có balance_ts {row['balance_ts']!r}, NAV {row['nav']!r}, vẫn chụp TRƯỚC "
                    f"giờ đóng cửa {_acf.SESSION_CLOSE_ICT:%H:%M}. Lời nhận gắn với đúng một dòng; "
                    f"đã rà dòng MỚI thì nhận lại: --accept-preclose {d}=\"<lý do + bằng chứng>\"")
            else:
                problems.append(
                    f"{d}: dòng chụp số dư lúc {row['balance_ts']} — TRƯỚC giờ đóng cửa "
                    f"{_acf.SESSION_CLOSE_ICT:%H:%M} của chính phiên đó ⇒ NAV có thể không phải "
                    f"giá chốt. Đính chính dòng nav_history, hoặc nếu ĐÃ RÀ và NAV đúng là giá "
                    f"chốt thì nhận tường minh: --accept-preclose {d}=\"<lý do + bằng chứng>\"")
        elif seen != want:
            problems.append(
                f"{d}: dòng chụp số dư lúc {row['balance_ts']} — khi đó phiên đóng cửa gần nhất "
                f"là {seen}, không phải {want} ⇒ NAV dòng này không phải giá chốt phiên {want} "
                f"(chạy lại snapshot ngày cũ theo đường live?). Phải đính chính nav_history; "
                f"không có lối nhận tường minh.")
    for key in sorted(set(accept_preclose) - set(accepted)):
        problems.append(f"--accept-preclose {key}: trong đoạn sắp chốt không có dòng nào của ngày "
                        f"đó chụp trước giờ đóng cửa (gõ nhầm ngày?)")
    return problems, accepted


def _accepted_so_far(manifest: list) -> dict:
    out = {}
    for rec in manifest:
        out.update(rec.get("accepted_preclose") or {})
    return out


def _seal_immutable_locked(path, ledger, asof, today, accept_preclose, meta):
    old, sealed, manifest, resumed = _vault_state(path, ledger, write=True)
    diffs = diff_against_sealed(ledger, sealed)
    if diffs:
        raise LedgerDriftError(path, diffs)
    if resumed and manifest[-1]["kind"] == "seal":
        # Lần chạy này vừa hoàn tất lần chốt dở #seq: đó là kết quả của nó, không chốt gì thêm.
        k = manifest[-1]["rows_added"]
        return sealed[:len(sealed) - k], [r for r in ledger if r["date"] in
                                          {x["date"] for x in sealed[len(sealed) - k:]}]
    cutoff = today - datetime.timedelta(days=1)
    if asof is not None and asof > cutoff:
        raise SealGateError(
            f"--asof {asof} không trước hôm nay ({today}, giờ ICT): dòng nav_history của hôm nay "
            f"còn bị daily_nav_snapshot.py ghi đè khi chạy lại ⇒ chỉ chốt tới {cutoff}.")
    upto = asof or cutoff
    last = sealed[-1]["date"] if sealed else None
    new = [r for r in ledger if (last is None or r["date"] > last) and r["date"] <= upto]
    if not new:
        raise NothingToSeal(
            f"{path}: không có dòng mới để chốt tới {upto}"
            + (f" — sổ đã chốt {len(sealed)} dòng tới {last}, md5 {manifest[-1]['md5']} (manifest "
               f"#{manifest[-1]['seq']}). Chốt lại sẽ ra đúng md5 đó ⇒ từ chối."
               if sealed else " (nav_history chưa có dòng nào trước hôm nay)."))
    problems, accepted = seal_gate(ledger, last if last is not None else new[0]["date"],
                                   new, accept_preclose or {})
    if problems:
        raise SealGateError(f"{path}: đoạn {new[0]['date']} → {new[-1]['date']} CHƯA đủ điều kiện "
                            f"chốt ({len(problems)} chỗ):\n  " + "\n  ".join(problems))
    base = old if old is not None else (",".join(LEDGER_FIELDS) + "\n").encode("utf-8")
    data = base + "".join(_csv_line(r) for r in new).encode("utf-8")
    rec = dict(meta or {}, seq=len(manifest) + 1, kind="seal", md5_before=_md5(old), md5=_md5(data),
               rows_before=len(sealed), rows_added=len(new), rows_total=len(sealed) + len(new),
               first_date=(sealed[0]["date"] if sealed else new[0]["date"]).isoformat(),
               last_date=new[-1]["date"].isoformat(), last_unit_price=repr(float(new[-1]["unit_price"])),
               accepted_preclose=accepted,
               sealed_at_ict=datetime.datetime.now(ICT).isoformat(timespec="seconds"))
    _append_manifest(path, rec)                 # manifest TRƯỚC: chết ở đây ⇒ lần sau hoàn tất
    _atomic_write(path, data)
    return sealed, new


def seal(path: str, ledger: list, asof: datetime.date = None, write: bool = True, *,
         immutable: bool = None, real_data: bool = False, today: datetime.date = None,
         accept_preclose: dict = None, meta: dict = None) -> tuple:
    """Đối chiếu `ledger` với sổ đã chốt rồi (khi `write`) THÊM vào cuối sổ mọi dòng có ngày sau
    dòng đã chốt cuối cùng (và <= `asof`). Trả `(dòng_đã_chốt_trước_đó, dòng_vừa_thêm)`.
    Lệch với dòng đã chốt ⇒ LedgerDriftError, KHÔNG ghi gì. Khi ghi: giữ khoá độc quyền
    `<path>.lock` suốt đọc→ghi, để hai tiến trình chốt cùng lúc không sinh dòng trùng.
    `immutable` (kho bất biến, xem docstring module): None ⇒ tự bật khi thư mục đã có manifest;
    LUÔN bật với thư mục dữ liệu thật, nơi còn cần `real_data=True` (thiếu ⇒ SealRefused)."""
    real = _is_real_dir(path)
    if immutable is None:
        immutable = os.path.exists(manifest_path(path))
    immutable = immutable or real
    if not write:
        if not immutable:
            return _seal_locked(path, ledger, asof, False)
        # Lệnh chỉ-đọc KHÔNG tạo file khoá; nhưng nếu khoá đã có thì chờ (khoá chia sẻ) lần chốt
        # đang chạy xong — không thì đọc đúng lúc "manifest đã ghi, file chưa thay" và báo nhầm
        # "chết giữa chừng". Tiến trình chết thật không còn giữ khoá ⇒ vẫn báo đúng.
        lock_path = f"{path}.lock"
        if not os.path.exists(lock_path):
            _, sealed, _, _ = _vault_state(path, ledger, write=False)
        else:
            with open(lock_path, "r", encoding="utf-8") as lock:
                fcntl.flock(lock, fcntl.LOCK_SH)
                try:
                    _, sealed, _, _ = _vault_state(path, ledger, write=False)
                finally:
                    fcntl.flock(lock, fcntl.LOCK_UN)
        diffs = diff_against_sealed(ledger, sealed)
        if diffs:
            raise LedgerDriftError(path, diffs)
        return sealed, []
    if real and not real_data:
        raise SealRefused(
            f"TỪ CHỐI chốt sổ vào thư mục dữ liệu thật {os.path.dirname(os.path.abspath(path))} "
            f"(cây dữ liệu thật, hoặc thư mục có dnse_raw_*.jsonl): chốt sổ đơn vị thật là "
            f"thao tác ghi-một-lần, phải gọi tường minh với --real-data sau khi user duyệt "
            f"(kb/projects/fund-unit-performance-policy-20261010.md, bước 3). Truyền --ledger-dir "
            f"trỏ thư mục khác nếu đang test/research.")
    if today is None:
        today = datetime.datetime.now(ICT).date()
    with open(f"{path}.lock", "a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            if immutable:
                return _seal_immutable_locked(path, ledger, asof, today, accept_preclose, meta)
            return _seal_locked(path, ledger, asof, True)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def restate(path: str, ledger: list, *, impact_report: str, reason: str, approved_by: str,
            real_data: bool = False, accept_preclose: dict = None, meta: dict = None) -> dict:
    """ĐÍNH CHÍNH một sổ kho bất biến: thay toàn bộ đoạn đã chốt bằng chuỗi dựng lại (cùng ngày
    cuối), SAU KHI chép nguyên byte sổ cũ sang file `.superseded.*` và ghi bản ghi `restate` vào
    manifest. Trả bản ghi manifest vừa thêm. Từ chối khi: chuỗi dựng lại không khác sổ đã chốt;
    báo cáo tác động (`fund_restatement.py impact --out`) không mang đúng md5 sổ đang chốt và md5
    sổ sau đính chính; thiếu lý do / người duyệt; đoạn đính chính không qua `seal_gate`."""
    real = _is_real_dir(path)
    if real and not real_data:
        raise SealRefused(
            f"TỪ CHỐI đính chính sổ ở thư mục dữ liệu thật "
            f"{os.path.dirname(os.path.abspath(path))} khi không có "
            f"--real-data (thao tác của Mike sau khi user duyệt).")
    if not str(reason or "").strip() or not str(approved_by or "").strip():
        raise SealGateError("đính chính sổ đã chốt phải có --reason và --approved-by (không rỗng)")
    with open(f"{path}.lock", "a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            old, sealed, manifest, resumed = _vault_state(path, ledger, write=True)
            if not manifest:
                raise NothingToSeal(f"{path}: chưa có sổ kho bất biến nào để đính chính — chốt lần "
                                    f"đầu bằng --seal.")
            if resumed and manifest[-1]["kind"] == "restate":
                return manifest[-1]             # vừa hoàn tất đúng lần đính chính dở
            diffs = diff_against_sealed(ledger, sealed)
            if not diffs:
                raise NothingToSeal(f"{path}: chuỗi dựng lại KHỚP sổ đã chốt (md5 "
                                    f"{manifest[-1]['md5']}) — không có gì để đính chính.")
            last = sealed[-1]["date"]
            data = _content(ledger, last)
            with open(impact_report, "rb") as f:
                report_bytes = f.read()
            try:
                report = json.loads(report_bytes.decode("utf-8"))
                bind = report["ledger_binding"]
                got = (report["account"], bind["sealed_md5"], bind["restated_md5"])
            except (ValueError, KeyError, TypeError) as exc:
                raise SealGateError(
                    f"báo cáo tác động {impact_report} không đọc được hoặc thiếu account / "
                    f"ledger_binding.sealed_md5 / restated_md5 ({type(exc).__name__}: {exc}) — "
                    f"phải là đầu ra của fund_restatement.py impact --sealed-ledger … --out") from exc
            want = ((meta or {}).get("account"), _md5(old), _md5(data))
            if got != want:
                raise SealGateError(
                    f"báo cáo tác động {impact_report} KHÔNG phải của thay đổi này: nó ghi "
                    f"(tài khoản, md5 sổ đang chốt, md5 sổ sau đính chính) = {got}, thực tế là "
                    f"{want}. Chạy lại fund_restatement.py impact trên đúng dữ liệu hiện tại.")
            rows = [r for r in ledger if r["date"] <= last]
            # Lời nhận cũ chỉ theo sang khi dòng của nó còn nguyên balance_ts + NAV (seal_gate);
            # lời nhận cũ của một ngày nay không còn chụp trước đóng cửa thì tự rơi, không lỗi.
            problems, accepted = seal_gate(ledger, rows[0]["date"], rows, accept_preclose or {},
                                           carried=_accepted_so_far(manifest))
            if problems:
                raise SealGateError(f"{path}: sổ sau đính chính CHƯA đủ điều kiện chốt "
                                    f"({len(problems)} chỗ):\n  " + "\n  ".join(problems))
            seq = len(manifest) + 1
            archive = f"{path}.superseded.{seq}.{_md5(old)[:12]}.csv"
            existing = _read_bytes(archive)
            if existing is not None and existing != old:
                raise SealIntegrityError(f"{archive} đã tồn tại với nội dung KHÁC sổ đang chốt — "
                                         f"file lưu là ghi-một-lần; kiểm bằng tay.")
            if existing is None:
                _atomic_write(archive, old)
            rec = dict(meta or {}, seq=seq, kind="restate", md5_before=_md5(old), md5=_md5(data),
                       rows_before=len(sealed), rows_total=len(rows),
                       rows_added=len(rows) - len(sealed), first_date=rows[0]["date"].isoformat(),
                       last_date=last.isoformat(),
                       last_unit_price=repr(float(rows[-1]["unit_price"])),
                       accepted_preclose=accepted, archived_as=os.path.basename(archive),
                       reason=str(reason).strip(), approved_by=str(approved_by).strip(),
                       impact_report_md5=_md5(report_bytes), n_diffs=len(diffs), diffs=diffs[:200],
                       sealed_at_ict=datetime.datetime.now(ICT).isoformat(timespec="seconds"))
            _append_manifest(path, rec)
            _atomic_write(path, data)
            return rec
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def build_account_ledger(account, nav_dir=NAV_HISTORY_DIR, inception_path=INCEPTION_PATH,
                         flows_path=None) -> tuple:
    rows = load_nav_history(account, nav_dir)
    inception = load_inception(account, inception_path)
    flows = load_flows(account, flows_path=flows_path, require_file=True)
    return build_ledger(rows, flows, *_inception_baseline(rows, inception))


def _file_md5(path):
    return _md5(_read_bytes(path)) if path else None


def _parse_accept(items) -> dict:
    out = {}
    for item in items or []:
        day, sep, why = item.partition("=")
        if not sep or not why.strip():
            raise SealGateError(f"--accept-preclose {item!r}: phải là NGÀY=lý do (lý do không rỗng)")
        out[_parse_date(day.strip()).isoformat()] = why.strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--account", required=True)
    ap.add_argument("--seal", action="store_true",
                    help="THÊM các dòng chưa chốt vào sổ ở --ledger-dir (thư mục dữ liệu thật: "
                         "phải thêm --real-data)")
    ap.add_argument("--asof", help="YYYY-MM-DD — chỉ chốt tới ngày này (mặc định: dòng cuối; kho "
                                   "bất biến: hôm qua, giờ ICT)")
    ap.add_argument("--tail", type=int, default=5, help="số dòng cuối in ra (mặc định 5)")
    ap.add_argument("--ledger-dir", help="thư mục sổ để đối chiếu/chốt; bỏ trống = chỉ dựng + in")
    ap.add_argument("--nav-dir", default=NAV_HISTORY_DIR)
    ap.add_argument("--inception-path", default=INCEPTION_PATH)
    ap.add_argument("--flows-path")
    ap.add_argument("--immutable", action="store_true",
                    help="chốt theo chế độ kho bất biến (manifest + md5 + cổng) ở thư mục thử; "
                         "thư mục dữ liệu thật và thư mục đã có manifest thì LUÔN bật")
    ap.add_argument("--real-data", action="store_true",
                    help="cho phép --seal/--restate ghi vào thư mục dữ liệu thật (mọi cổng vẫn chạy)")
    ap.add_argument("--accept-preclose", action="append", metavar="NGÀY=LÝ DO",
                    help="nhận một dòng chụp trước giờ đóng cửa ĐÃ RÀ là giá chốt (ghi vào manifest)")
    ap.add_argument("--restate", action="store_true",
                    help="ĐÍNH CHÍNH sổ kho bất biến đã chốt bằng chuỗi dựng lại (cần "
                         "--impact-report, --reason, --approved-by)")
    ap.add_argument("--impact-report", help="đầu ra JSON của fund_restatement.py impact")
    ap.add_argument("--reason")
    ap.add_argument("--approved-by")
    args = ap.parse_args()
    if args.seal and args.restate:
        ap.error("--seal và --restate không đi cùng nhau")
    if args.restate and not args.impact_report:
        ap.error("--restate cần --impact-report")

    path = ledger_path(args.account, args.ledger_dir or NAV_HISTORY_DIR)
    flows_path = args.flows_path or _acf.FLOWS_PATH
    sealed = added = restated = None
    try:
        asof = _parse_date(args.asof) if args.asof else None
        accept = _parse_accept(args.accept_preclose)
        ledger, info = build_account_ledger(args.account, args.nav_dir, args.inception_path,
                                            args.flows_path)
        meta = {"account": args.account, "tool": "nav_unit_ledger.py",
                "nav_history_md5": _file_md5(os.path.join(args.nav_dir,
                                                          f"nav_history_{args.account}.csv")),
                "inception_md5": _file_md5(args.inception_path),
                "cash_flows_md5": _file_md5(flows_path)}
        if args.restate:
            restated = restate(path, ledger, impact_report=args.impact_report, reason=args.reason,
                               approved_by=args.approved_by, real_data=args.real_data,
                               accept_preclose=accept, meta=meta)
            sealed, added = seal(path, ledger, write=False)
        elif args.seal or args.ledger_dir:
            sealed, added = seal(path, ledger, asof, write=args.seal,
                                 immutable=True if args.immutable else None,
                                 real_data=args.real_data, accept_preclose=accept, meta=meta)
    except SealRefused as e:
        print(f"nav_unit_ledger ({args.account}): {e}", file=sys.stderr)
        return 3
    except LedgerDriftError as e:
        print(f"LỆCH SỔ nav_unit_ledger ({args.account}): {e}\n  ⇒ KHÔNG ghi gì. Dòng đã chốt "
              f"không được đổi tại chỗ; lịch sử đổi có chủ đích đi đường đính chính: "
              f"fund_restatement.py impact … --out rồi nav_unit_ledger.py --restate.",
              file=sys.stderr)
        return 2
    except (SealIntegrityError, NothingToSeal, SealGateError) as e:
        print(f"TỪ CHỐI nav_unit_ledger ({args.account}) [{type(e).__name__}]: {e}\n  ⇒ KHÔNG ghi "
              f"gì vào sổ.", file=sys.stderr)
        return 2
    except (FileNotFoundError, ValueError, KeyError) as e:      # CashFlowError là ValueError
        print(f"LỖI nav_unit_ledger ({args.account}): {e}", file=sys.stderr)
        return 1

    for f in info["dropped"]:
        print(f"  ℹ️ bỏ flow {f['date']} {f['amount_vnd']:+,.0f} VND: ngày <= mốc khởi điểm "
              f"{ledger[0]['date']} (đã nằm trong vốn khởi điểm)", file=sys.stderr)
    for f in info["pending"]:
        print(f"  ⚠️ flow {f['date']} {f.get('time_ict') or ''} {f['amount_vnd']:+,.0f} VND TREO, "
              f"chưa vào sổ: chưa dòng nav_history nào chụp sau thời điểm đó (dòng cuối "
              f"{ledger[-1]['date']})", file=sys.stderr)
    print(f"nav_unit_ledger {args.account}: {len(ledger)} dòng dựng được "
          f"({ledger[0]['date']} → {ledger[-1]['date']}), "
          f"{sum(1 for r in ledger if r['nav_is_estimate'])} dòng nav_is_estimate, "
          f"{sum(1 for r in ledger if r['flow_bod_vnd'] or r['flow_eod_vnd'])} ngày có dòng tiền")
    if sealed is None:
        print("sổ trên đĩa: KHÔNG đối chiếu (không truyền --ledger-dir)")
    else:
        last_sealed = (added or sealed or [None])[-1]
        print(f"sổ đã chốt: {path} — {len(sealed) + len(added)} dòng"
              + (f", tới {last_sealed['date']}" if last_sealed else " (chưa chốt dòng nào)")
              + (f"; vừa THÊM {len(added)} dòng" if args.seal else "; khớp chuỗi dựng lại"))
        manifest = read_manifest(path)
        if manifest:
            m = manifest[-1]
            print(f"kho bất biến: manifest #{m['seq']} ({m['kind']}) md5 {m['md5']} — "
                  f"{m['rows_total']} dòng tới {m['last_date']}, giá đơn vị cuối "
                  f"{float(m['last_unit_price']):.4f}"
                  + (f"; dòng chụp trước đóng cửa đã nhận: "
                     f"{', '.join(sorted(_accepted_so_far(manifest)))}"
                     if _accepted_so_far(manifest) else ""))
            if args.seal or args.restate:
                # B13 — mốc NGOÀI kho: Mike post dòng này lên bus sau mỗi lần chốt. Hoàn tác
                # đồng thời file sổ + đuôi manifest thì md5 ở đây không còn khớp mốc đã post.
                print(f"SEAL_MD5 {args.account} {_file_md5(path)} {_file_md5(manifest_path(path))}")
        if restated:
            print(f"ĐÃ ĐÍNH CHÍNH: {restated['n_diffs']} chỗ lệch; sổ cũ (md5 "
                  f"{restated['md5_before']}) lưu ở {restated['archived_as']}; người duyệt "
                  f"{restated['approved_by']}")
    print(",".join(LEDGER_FIELDS))
    for r in ledger[-args.tail:] if args.tail > 0 else []:
        print(_csv_line(r), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
