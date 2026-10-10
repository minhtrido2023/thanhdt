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
⚠️ CHƯA CHỐT SỔ THẬT TRƯỚC BƯỚC 3 của chính sách (rà các ngày `nav_is_estimate`, có đường đính
chính): `--seal` TỪ CHỐI ghi vào thư mục dữ liệu mặc định (rc=3) — chỉ ghi khi truyền
`--ledger-dir` trỏ nơi khác (test/research). `nav_period_returns.py` KHÔNG đọc sổ trên đĩa.

Dùng:
    python3 mike/bin/nav_unit_ledger.py --account SpaceX                      # dựng + in
    python3 mike/bin/nav_unit_ledger.py --account SpaceX --ledger-dir D       # + đối chiếu sổ ở D
    python3 mike/bin/nav_unit_ledger.py --account SpaceX --ledger-dir D --seal
Selfcheck: python3 mike/bin/nav_unit_ledger_selfcheck.py
"""
import argparse
import csv
import datetime
import fcntl
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from account_cash_flows import (NavRow, attach_flows_to_rows,  # noqa: E402,F401
                                load_flows, require_strictly_increasing)
from wc_paths import find_wc_root  # noqa: E402

WC_ROOT = find_wc_root(__file__)
INCEPTION_PATH = os.path.join(WC_ROOT, "data", "account_inception.json")
NAV_HISTORY_DIR = os.path.join(WC_ROOT, "data", "execution_logs")

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
    """Từ chối chốt sổ vào thư mục dữ liệu thật — chưa được phép trước bước 3 của chính sách."""


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
    ⚠️ "dropped" lọc theo NGÀY, không theo giờ: mốc khởi điểm ZaloPay là NAV đêm TRƯỚC phiên
    2026-07-06, nên tiền vào trong/tối 07-06 KHÔNG nằm trong vốn khởi điểm mà vẫn bị loại — nó
    hiện ở `dropped_flows` của mọi consumer để người đọc thấy, không tự sửa ở đây.
    `flows` của mỗi dòng sổ là bản sao đã gán (`timing` = quy ước suy ra, `session_date`).
    """
    if inception_nav0 <= 0:
        raise ValueError(f"vốn khởi điểm phải > 0, được {inception_nav0}")
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
               "nav_is_estimate": base_est, "flows": []}]
    for row in nav_rows:
        d, nav = row[0], row[1]
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
                       "flows": day})
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


def seal(path: str, ledger: list, asof: datetime.date = None, write: bool = True) -> tuple:
    """Đối chiếu `ledger` với sổ đã chốt rồi (khi `write`) THÊM vào cuối sổ mọi dòng có ngày sau
    dòng đã chốt cuối cùng (và <= `asof`). Trả `(dòng_đã_chốt_trước_đó, dòng_vừa_thêm)`.
    Lệch với dòng đã chốt ⇒ LedgerDriftError, KHÔNG ghi gì. Ghi vào thư mục dữ liệu thật ⇒
    SealRefused (chưa chốt sổ thật trước bước 3). Khi ghi: giữ khoá độc quyền `<path>.lock`
    suốt đọc→ghi, để hai tiến trình chốt cùng lúc không sinh dòng trùng."""
    if not write:
        return _seal_locked(path, ledger, asof, False)
    if os.path.realpath(os.path.dirname(os.path.abspath(path))) == os.path.realpath(NAV_HISTORY_DIR):
        raise SealRefused(
            f"TỪ CHỐI chốt sổ vào thư mục dữ liệu thật {NAV_HISTORY_DIR}: chưa chốt sổ đơn vị thật "
            f"trước bước 3 của chính sách (kb/projects/fund-unit-performance-policy-20261010.md). "
            f"Truyền --ledger-dir trỏ thư mục khác nếu đang test/research.")
    with open(f"{path}.lock", "a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            return _seal_locked(path, ledger, asof, True)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def build_account_ledger(account, nav_dir=NAV_HISTORY_DIR, inception_path=INCEPTION_PATH,
                         flows_path=None) -> tuple:
    rows = load_nav_history(account, nav_dir)
    inception = load_inception(account, inception_path)
    flows = load_flows(account, flows_path=flows_path, require_file=True)
    return build_ledger(rows, flows, *_inception_baseline(rows, inception))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--account", required=True)
    ap.add_argument("--seal", action="store_true",
                    help="THÊM các dòng chưa chốt vào sổ ở --ledger-dir (KHÔNG phải thư mục dữ "
                         "liệu thật — bị từ chối trước bước 3)")
    ap.add_argument("--asof", help="YYYY-MM-DD — chỉ chốt tới ngày này (mặc định: dòng cuối)")
    ap.add_argument("--tail", type=int, default=5, help="số dòng cuối in ra (mặc định 5)")
    ap.add_argument("--ledger-dir", help="thư mục sổ để đối chiếu/chốt; bỏ trống = chỉ dựng + in")
    ap.add_argument("--nav-dir", default=NAV_HISTORY_DIR)
    ap.add_argument("--inception-path", default=INCEPTION_PATH)
    ap.add_argument("--flows-path")
    args = ap.parse_args()

    path = ledger_path(args.account, args.ledger_dir or NAV_HISTORY_DIR)
    sealed = added = None
    try:
        asof = _parse_date(args.asof) if args.asof else None
        ledger, info = build_account_ledger(args.account, args.nav_dir, args.inception_path,
                                            args.flows_path)
        if args.seal or args.ledger_dir:
            sealed, added = seal(path, ledger, asof, write=args.seal)
    except SealRefused as e:
        print(f"nav_unit_ledger ({args.account}): {e}", file=sys.stderr)
        return 3
    except LedgerDriftError as e:
        print(f"LỆCH SỔ nav_unit_ledger ({args.account}): {e}\n  ⇒ KHÔNG ghi gì. Dòng đã chốt "
              f"không được đổi; tính lại lịch sử có chủ đích là đường riêng (chưa có).",
              file=sys.stderr)
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
        print("sổ trên đĩa: KHÔNG đối chiếu (không truyền --ledger-dir; sổ thật chưa chốt trước "
              "bước 3)")
    else:
        last_sealed = (added or sealed or [None])[-1]
        print(f"sổ đã chốt: {path} — {len(sealed) + len(added)} dòng"
              + (f", tới {last_sealed['date']}" if last_sealed else " (chưa chốt dòng nào)")
              + (f"; vừa THÊM {len(added)} dòng" if args.seal else "; khớp chuỗi dựng lại"))
    print(",".join(LEDGER_FIELDS))
    for r in ledger[-args.tail:] if args.tail > 0 else []:
        print(_csv_line(r), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
