#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho chế độ KHO BẤT BIẾN của sổ đơn vị quỹ (`nav_unit_ledger.py`: manifest md5, cổng
trước khi chốt, hoàn tất lần chốt dở, `--real-data`, `--restate`, lời nhận gắn với dòng, khoá) —
bước 3/4 của chính sách "tài khoản = quỹ mở".

KHÉP KÍN: mọi file nằm ở tempdir; "thư mục dữ liệu thật" trong các ca dưới là một tempdir gán vào
`nul.NAV_HISTORY_DIR`. Không broker, không BigQuery, không đọc/ghi `data/`. Lịch phiên lấy từ
`trading_bot.vn_market` (như `nav_unit_ledger_selfcheck.py`).

Chạy: python3 mike/bin/nav_ledger_vault_selfcheck.py
      env -u TZ python3 … ;  TZ=America/New_York python3 … ;  TZ=Pacific/Kiritimati python3 …
"""
import datetime
import hashlib
import fcntl
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

import nav_unit_ledger as nul                         # noqa: E402

D = datetime.date
N = 0
FAILS = []
TODAY = D(2026, 7, 31)
NAV_FIELDS = ["date", "nav", "mtm_stock", "cash", "margin_debt", "offbook_assets", "egg_assets",
              "balance_ts", "cum_dividend_excl", "nav_is_estimate", "nav_source"]
INC = {"SpaceX": {"inception_date": "2026-07-01", "starting_capital": 1_000_000_000}}
# 2026-07-01 là thứ Tư. Bốn phiên liền nhau sau mốc khởi điểm:
NAV4 = [("2026-07-02", 1_010_000_000.0), ("2026-07-03", 1_020_000_000.0),
        ("2026-07-06", 1_015_000_000.0), ("2026-07-07", 1_030_000_000.0)]


def ok(cond, msg):
    global N
    N += 1
    if not cond:
        FAILS.append(msg)
        print(f"FAIL: {msg}")


def raises(exc_type, fn, msg, needle=None):
    global N
    N += 1
    try:
        fn()
    except exc_type as exc:
        if type(exc) is not exc_type:
            FAILS.append(f"{msg}: phải ném đúng {exc_type.__name__}, được {type(exc).__name__}: {exc}")
            print("FAIL:", FAILS[-1])
            return None
        for part in ([needle] if isinstance(needle, str) else (needle or [])):
            if part not in str(exc):
                FAILS.append(f"{msg}: thông điệp thiếu {part!r}: {exc}")
                print("FAIL:", FAILS[-1])
        return exc
    except Exception as exc:                # noqa: BLE001
        FAILS.append(f"{msg}: phải ném {exc_type.__name__}, được {type(exc).__name__}: {exc}")
        print("FAIL:", FAILS[-1])
        return None
    FAILS.append(f"{msg}: phải ném {exc_type.__name__}, không ném gì")
    print("FAIL:", FAILS[-1])
    return None


def md5(data):
    return hashlib.md5(data).hexdigest()


class Box:
    """nav_history + mốc khởi điểm + sổ dòng tiền + thư mục sổ, tất cả trong tempdir."""

    def __init__(self, tmp, name, nav, flows=()):
        self.dir = Path(tmp) / name
        self.dir.mkdir()
        self.ledger_dir = self.dir / "ledger"
        self.ledger_dir.mkdir()
        self.inc_path = str(self.dir / "account_inception.json")
        self.flows_path = str(self.dir / "account_cash_flows.json")
        Path(self.inc_path).write_text(json.dumps(INC), encoding="utf-8")
        Path(self.flows_path).write_text(json.dumps({"SpaceX": list(flows)}), encoding="utf-8")
        self.write_nav(nav)

    def write_nav(self, nav):
        """nav: [(ngày, nav[, balance_ts])]; balance_ts mặc định <ngày>T19:10:00, "" = ô trống."""
        lines = [",".join(NAV_FIELDS)]
        for rec in nav:
            ts = rec[2] if len(rec) > 2 else f"{rec[0]}T19:10:00"
            lines.append(f"{rec[0]},{rec[1]!r},{rec[1]!r},0,0,0,0,{ts},0,False,live")
        (self.dir / "nav_history_SpaceX.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    @property
    def sealed(self):
        return self.ledger_dir / "nav_unit_ledger_SpaceX.csv"

    @property
    def manifest(self):
        return Path(str(self.sealed) + nul.MANIFEST_SUFFIX)

    def records(self):
        return [json.loads(x) for x in self.manifest.read_text(encoding="utf-8").splitlines()]

    def ledger(self):
        return nul.build_account_ledger("SpaceX", str(self.dir), self.inc_path, self.flows_path)[0]

    def seal(self, **kw):
        kw.setdefault("immutable", True)
        kw.setdefault("today", TODAY)
        kw.setdefault("meta", {"account": "SpaceX"})
        return nul.seal(str(self.sealed), self.ledger(), **kw)

    def verify(self, **kw):
        return nul.seal(str(self.sealed), self.ledger(), write=False, **kw)

    def cli(self, *extra):
        return subprocess.run(
            [sys.executable, str(BIN / "nav_unit_ledger.py"), "--account", "SpaceX",
             "--nav-dir", str(self.dir), "--inception-path", self.inc_path,
             "--flows-path", self.flows_path, "--ledger-dir", str(self.ledger_dir), *extra],
            capture_output=True, text=True)


# ------------------------------------------------------------------ V1. chốt, manifest, md5 trùng
def v1_seal_and_manifest(tmp):
    box = Box(tmp, "v1", NAV4)
    before, added = box.seal()
    data = box.sealed.read_bytes()
    recs = box.records()
    ok(before == [] and len(added) == 5 and len(data.decode().splitlines()) == 6,
       f"V1: lần đầu phải chốt mốc khởi điểm + 4 dòng, được {len(added)}")
    r = recs[0]
    ok(len(recs) == 1 and r["seq"] == 1 and r["kind"] == "seal" and r["md5_before"] is None
       and r["md5"] == md5(data), f"V1: bản ghi manifest đầu phải mang md5 của file vừa ghi: {r}")
    ok(r["rows_total"] == 5 and r["rows_added"] == 5 and r["rows_before"] == 0
       and r["first_date"] == "2026-07-01" and r["last_date"] == "2026-07-07",
       f"V1: số dòng / ngày đầu / ngày cuối trong manifest sai: {r}")
    ok(float(r["last_unit_price"]) == 10_300.0 and r["accepted_preclose"] == {}
       and r["account"] == "SpaceX" and r["sealed_at_ict"].endswith("+07:00"),
       f"V1: giá đơn vị cuối / tài khoản / giờ chốt ICT sai: {r}")
    ok(sorted(x.name for x in box.ledger_dir.iterdir()) == [
        "nav_unit_ledger_SpaceX.csv", "nav_unit_ledger_SpaceX.csv.lock",
        "nav_unit_ledger_SpaceX.csv.manifest.jsonl"], "V1: thư mục sổ chỉ có sổ + khoá + manifest")
    # md5 trùng ⇒ từ chối, không ghi gì, không có lối ép.
    exc = raises(nul.NothingToSeal, box.seal, "V1 chốt lần hai không có dòng mới",
                 [r["md5"], "từ chối", "manifest #1"])
    ok(exc is not None and box.sealed.read_bytes() == data and len(box.records()) == 1,
       "V1: bị từ chối thì file sổ và manifest không đổi byte nào")
    ok(box.verify() == (nul.read_sealed(str(box.sealed)), []),
       "V1: thư mục đã có manifest ⇒ đối chiếu chỉ-đọc tự chạy ở chế độ kho bất biến và khớp")
    raises(nul.NothingToSeal, lambda: nul.seal(str(box.sealed), box.ledger(), today=TODAY),
           "V1: thư mục đã có manifest ⇒ chốt không truyền immutable vẫn là kho bất biến")
    p = box.cli("--seal")
    ok(p.returncode == 2 and "NothingToSeal" in p.stderr and r["md5"] in p.stderr
       and box.sealed.read_bytes() == data,
       f"V1 CLI: chốt lần hai phải rc=2 nêu md5, được rc={p.returncode} {p.stderr[:200]}")
    ok("--force" not in (BIN / "nav_unit_ledger.py").read_text(encoding="utf-8").split('"""', 2)[2],
       "V1: CLI không được có cờ --force nào")
    p = box.cli()
    ok(p.returncode == 0 and f"manifest #1 (seal) md5 {r['md5']}" in p.stdout
       and "giá đơn vị cuối 10300.0000" in p.stdout,
       f"V1 CLI: đối chiếu phải in md5 + giá đơn vị cuối của manifest: {p.stdout[-300:]}")

    # Chốt tiếp: byte cũ giữ nguyên, md5 nối chuỗi.
    box.write_nav(NAV4 + [("2026-07-08", 1_040_000_000.0)])
    before, added = box.seal()
    data2 = box.sealed.read_bytes()
    recs = box.records()
    ok(len(before) == 5 and [x["date"] for x in added] == [D(2026, 7, 8)] and data2.startswith(data),
       "V1: chốt tiếp phải thêm đúng 1 dòng và giữ nguyên từng byte cũ")
    ok(len(recs) == 2 and recs[1]["md5_before"] == recs[0]["md5"] and recs[1]["md5"] == md5(data2)
       and recs[1]["seq"] == 2 and recs[1]["rows_before"] == 5 and recs[1]["rows_total"] == 6,
       f"V1: bản ghi thứ hai phải nối md5 với bản ghi đầu: {recs[1]}")
    # CLI --immutable ở thư mục mới + meta md5 nguồn.
    box2 = Box(tmp, "v1_cli", NAV4)
    p = box2.cli("--immutable", "--seal")
    rec = box2.records()[0] if box2.manifest.exists() else {}
    ok(p.returncode == 0 and "vừa THÊM 5 dòng" in p.stdout and "kho bất biến: manifest #1" in p.stdout,
       f"V1 CLI --immutable --seal: rc={p.returncode} {p.stdout[-200:]} {p.stderr[-200:]}")
    ok(rec.get("nav_history_md5") == md5((box2.dir / "nav_history_SpaceX.csv").read_bytes())
       and rec.get("inception_md5") == md5(Path(box2.inc_path).read_bytes())
       and rec.get("cash_flows_md5") == md5(Path(box2.flows_path).read_bytes())
       and rec.get("tool") == "nav_unit_ledger.py",
       f"V1 CLI: manifest phải ghi md5 của ba file nguồn: {rec}")
    # Chế độ thường (không manifest) không đổi: chốt lại 0 dòng vẫn rc=0, không sinh manifest.
    box3 = Box(tmp, "v1_plain", NAV4)
    p1, p2 = box3.cli("--seal"), box3.cli("--seal")
    ok(p1.returncode == 0 and p2.returncode == 0 and "vừa THÊM 0 dòng" in p2.stdout
       and not box3.manifest.exists(), "V1: thư mục thử không --immutable giữ hành vi cũ, không manifest")


# ------------------------------------------------------------------ V2. cổng "trước hôm nay"
def v2_today_gate(tmp):
    box = Box(tmp, "v2", NAV4)
    before, added = box.seal(today=D(2026, 7, 7))
    ok([x["date"] for x in added][-1] == D(2026, 7, 6) and len(added) == 4,
       f"V2: hôm nay 07-07 ⇒ chỉ chốt tới 07-06, được {[str(x['date']) for x in added]}")
    raises(nul.NothingToSeal, lambda: box.seal(today=D(2026, 7, 7)), "V2: dòng hôm nay chưa chốt được")
    raises(nul.SealGateError, lambda: box.seal(today=D(2026, 7, 7), asof=D(2026, 7, 7)),
           "V2: --asof = hôm nay", ["không trước hôm nay", "2026-07-06"])
    raises(nul.SealGateError, lambda: box.seal(today=D(2026, 7, 7), asof=D(2026, 7, 9)),
           "V2: --asof sau hôm nay", "không trước hôm nay")
    ok(len(box.records()) == 1, "V2: các lần bị từ chối không được thêm bản ghi manifest")
    before, added = box.seal(today=D(2026, 7, 8))
    ok([x["date"] for x in added] == [D(2026, 7, 7)], "V2: sang hôm sau thì dòng 07-07 chốt được")
    box = Box(tmp, "v2_asof", NAV4)
    _, added = box.seal(asof=D(2026, 7, 3))
    ok([x["date"] for x in added][-1] == D(2026, 7, 3) and len(added) == 3, "V2: --asof quá khứ được tôn trọng")

    # "Hôm nay" mặc định phải là ngày ICT, không phải ngày theo TZ của máy. 18:30 UTC ngày 07-07 =
    # 01:30 ICT ngày 07-08 ⇒ dòng 07-07 chốt được; lấy giờ máy (UTC/New_York) thì KHÔNG.
    code = (
        "import sys, datetime, types\n"
        f"sys.path.insert(0, {str(BIN)!r})\n"
        "import nav_unit_ledger as nul\n"
        "FIXED = datetime.datetime(2026, 7, 7, 18, 30, tzinfo=datetime.timezone.utc)\n"
        "class FakeDT(datetime.datetime):\n"
        "    @classmethod\n"
        "    def now(cls, tz=None):\n"
        "        return FIXED.astimezone(tz) if tz is not None else FIXED.astimezone().replace(tzinfo=None)\n"
        "class FakeDate(datetime.date):\n"
        "    @classmethod\n"
        "    def today(cls):\n"
        "        return FIXED.astimezone().date()        # ngày theo TZ của MÁY\n"
        "nul.datetime = types.SimpleNamespace(datetime=FakeDT, date=FakeDate,\n"
        "                                     timedelta=datetime.timedelta, time=datetime.time)\n"
        "d, inc, fl, sealed = sys.argv[1:5]\n"
        "ledger = nul.build_account_ledger('SpaceX', d, inc, fl)[0]\n"
        "_, added = nul.seal(sealed, ledger, immutable=True, meta={'account': 'SpaceX'})\n"
        "print(added[-1]['date'], nul.read_manifest(sealed)[-1]['sealed_at_ict'])\n")
    for tz in ("UTC", "America/New_York", "Pacific/Kiritimati", None):
        box = Box(tmp, f"v2_tz_{(tz or 'unset').replace('/', '_')}", NAV4)
        env = {k: v for k, v in os.environ.items() if k != "TZ"}
        if tz:
            env["TZ"] = tz
        p = subprocess.run([sys.executable, "-c", code, str(box.dir), box.inc_path, box.flows_path,
                            str(box.sealed)], capture_output=True, text=True, env=env)
        ok(p.returncode == 0 and p.stdout.split() == ["2026-07-07", "2026-07-08T01:30:00+07:00"],
           f"V2 TZ={tz}: hôm nay phải tính theo ICT (chốt tới 07-07, giờ chốt 01:30+07:00), được "
           f"rc={p.returncode} {p.stdout!r} {p.stderr[-300:]}")


# ------------------------------------------------------------------ V3. sửa ngoài công cụ
def v3_tamper(tmp):
    def fresh(name):
        box = Box(tmp, name, NAV4)
        box.seal()
        return box, box.sealed.read_bytes(), box.manifest.read_bytes()

    def refused(box, label, needle):
        for fn, how in ((box.seal, "chốt"), (lambda: box.verify(immutable=True), "đối chiếu")):
            raises(nul.SealIntegrityError, fn, f"V3 {label} — {how}", needle)

    # Cắt dòng cuối: so từng dòng KHÔNG thấy (đó là lỗ mà manifest bịt).
    box, data, man = fresh("v3_cut")
    cut = b"".join(data.splitlines(keepends=True)[:-1])
    box.sealed.write_bytes(cut)
    ok(nul.diff_against_sealed(box.ledger(), nul.read_sealed(str(box.sealed))) == [],
       "V3: cắt dòng cuối thì so từng dòng không báo gì (lý do phải có manifest)")
    refused(box, "cắt dòng cuối", ["đã bị đổi NGOÀI công cụ", md5(cut), md5(data)])
    ok(box.sealed.read_bytes() == cut and box.manifest.read_bytes() == man,
       "V3: phát hiện sửa tay thì KHÔNG ghi gì (không tự vá)")
    p = box.cli("--seal")
    ok(p.returncode == 2 and "SealIntegrityError" in p.stderr and box.sealed.read_bytes() == cut,
       f"V3 CLI: cắt dòng cuối phải rc=2, được rc={p.returncode} {p.stderr[:200]}")
    p = box.cli()
    ok(p.returncode == 2 and "SealIntegrityError" in p.stderr,
       f"V3 CLI: đối chiếu cũng phải rc=2, được rc={p.returncode}")

    # Xoá file sổ khi manifest đã có >= 2 bản ghi ⇒ không khớp md5 nào ⇒ từ chối.
    box, data, man = fresh("v3_del")
    box.write_nav(NAV4 + [("2026-07-08", 1_040_000_000.0)])
    box.seal()
    data = box.sealed.read_bytes()
    box.sealed.unlink()
    refused(box, "xoá file sổ", ["KHÔNG có file", md5(data)])
    ok(not box.sealed.exists(), "V3: file bị xoá không được dựng lại âm thầm")
    # Xoá file sổ khi manifest mới có MỘT bản ghi: không phân biệt được với "lần chốt đầu chết
    # trước khi ghi file" ⇒ chỉ được trả lại ĐÚNG nội dung đã ghi md5 (nguồn không đổi), không
    # thêm bản ghi; nguồn đã đổi thì từ chối — xoá file để "dựng lại cho khớp" không qua được.
    box, data, man = fresh("v3_del_first")
    box.sealed.unlink()
    raises(nul.SealIntegrityError, box.verify, "V3 xoá file sổ (1 bản ghi) — đối chiếu", "CHƯA thay file")
    ok(not box.sealed.exists(), "V3: lệnh chỉ-đọc không dựng lại file")
    box.write_nav([("2026-07-02", 1_011_000_000.0)] + NAV4[1:])
    raises(nul.SealIntegrityError, box.seal, "V3: xoá file rồi sửa nguồn để dựng lại", "nguồn đã đổi")
    ok(not box.sealed.exists() and box.manifest.read_bytes() == man, "V3: xoá + sửa nguồn ⇒ không ghi gì")
    box.write_nav(NAV4)
    box.seal()
    ok(box.sealed.read_bytes() == data and box.manifest.read_bytes() == man,
       "V3: nguồn không đổi ⇒ trả lại đúng từng byte đã chốt, manifest không thêm bản ghi")

    box, data, man = fresh("v3_edit")
    edited = data.replace(b"1010000000.0", b"1010000000.5", 1)
    ok(edited != data, "V3: sanity — bản sửa phải khác bản gốc")
    box.sealed.write_bytes(edited)
    p = box.cli("--seal")
    ok(p.returncode == 2 and box.sealed.read_bytes() == edited,
       f"V3: sửa một ô ⇒ rc=2 (lệch sổ hoặc md5), không ghi; được rc={p.returncode}")

    box, data, man = fresh("v3_nomanifest")
    box.manifest.unlink()
    refused(box, "mất manifest", ["không có bản ghi nào", md5(data)])
    box2 = Box(tmp, "v3_legacy_file", NAV4)
    nul.seal(str(box2.sealed), box2.ledger(), immutable=False)           # sổ chế độ thường
    raises(nul.SealIntegrityError, box2.seal, "V3: bật kho bất biến trên sổ chế độ thường có sẵn",
           "không do chế độ kho bất biến chốt")

    # Manifest bị sửa: chuỗi md5/seq đứt, dòng hỏng.
    box, data, man = fresh("v3_chain")
    box.write_nav(NAV4 + [("2026-07-08", 1_040_000_000.0)])
    box.seal()
    lines = box.manifest.read_text(encoding="utf-8").splitlines(keepends=True)
    for label, body, needle in (
            ("xoá bản ghi đầu", lines[1], "chuỗi manifest ĐỨT"),
            ("đảo thứ tự", lines[1] + lines[0], "chuỗi manifest ĐỨT"),
            ("lặp bản ghi", lines[0] + lines[0] + lines[1], "chuỗi manifest ĐỨT"),
            ("seq nhảy cóc (md5 vẫn nối)", lines[0] + json.dumps(dict(json.loads(lines[1]), seq=5)) + "\n",
             "chuỗi manifest ĐỨT"),
            ("dòng không phải JSON", lines[0] + "{hỏng\n", "không đọc được"),
            ("thiếu khoá md5", lines[0] + json.dumps({"seq": 2, "kind": "seal"}) + "\n", "không đọc được"),
            ("dòng trống ở giữa", lines[0] + "\n" + lines[1], "không đọc được")):
        box.manifest.write_text(body, encoding="utf-8")
        refused(box, f"manifest {label}", needle)
    rec = json.loads(lines[1])
    rec["md5"] = "0" * 32
    box.manifest.write_text(lines[0] + json.dumps(rec) + "\n", encoding="utf-8")
    refused(box, "manifest sửa md5 bản ghi cuối", "đã bị đổi NGOÀI công cụ")
    box.manifest.write_text("".join(lines), encoding="utf-8")
    ok(box.verify()[1] == [], "V3: khôi phục manifest ⇒ khớp lại")
    # Lệch NGUỒN (không phải sửa file sổ) vẫn là LedgerDriftError như cũ.
    box.write_nav([("2026-07-02", 1_010_000_001.0)] + NAV4[1:] + [("2026-07-08", 1_040_000_000.0)])
    raises(nul.LedgerDriftError, box.seal, "V3: NAV quá khứ đổi 1 đ", "2026-07-02 nav:")
    raises(nul.LedgerDriftError, box.verify, "V3: đối chiếu CHỈ-ĐỌC cũng phải báo lệch nguồn", "2026-07-02 nav:")
    p = box.cli("--seal")
    ok(p.returncode == 2 and "LỆCH SỔ" in p.stderr and "--restate" in p.stderr,
       f"V3 CLI: lệch nguồn phải rc=2 và chỉ đường đính chính, được rc={p.returncode} {p.stderr[-200:]}")


# ------------------------------------------------------------------ V4. chết giữa chừng
def v4_crash_resume(tmp):
    real_write = nul._atomic_write

    def boom(path, data):
        raise OSError("mất điện (giả lập)")

    for first in (True, False):
        box = Box(tmp, f"v4_{'first' if first else 'append'}", NAV4)
        if not first:
            box.seal(asof=D(2026, 7, 3))
        old = box.sealed.read_bytes() if box.sealed.exists() else None
        n_before = len(box.records()) if box.manifest.exists() else 0
        nul._atomic_write = boom
        try:
            raises(OSError, box.seal, f"V4 ({'lần đầu' if first else 'chốt tiếp'}): chết khi thay file", "mất điện")
        finally:
            nul._atomic_write = real_write
        recs = box.records()
        ok(len(recs) == n_before + 1 and (box.sealed.read_bytes() if box.sealed.exists() else None) == old,
           "V4: manifest đã có bản ghi mới, file sổ CHƯA đổi (manifest ghi TRƯỚC)")
        raises(nul.SealIntegrityError, box.verify, "V4: đối chiếu chỉ-đọc khi còn lần chốt dở",
               ["CHƯA thay file", "Chạy lại"])
        ok((box.sealed.read_bytes() if box.sealed.exists() else None) == old,
           "V4: lệnh chỉ-đọc không được tự hoàn tất lần chốt dở")
        before, added = box.seal()
        ok(md5(box.sealed.read_bytes()) == recs[-1]["md5"] and len(box.records()) == n_before + 1,
           "V4: chạy lại phải hoàn tất ĐÚNG lần chốt dở và KHÔNG thêm bản ghi manifest thứ hai")
        ok(len(added) == recs[-1]["rows_added"] and len(before) == recs[-1]["rows_before"]
           and added[-1]["date"] == D(2026, 7, 7),
           f"V4: kết quả trả về phải là của lần chốt vừa hoàn tất, được {len(before)}+{len(added)}")
        raises(nul.NothingToSeal, box.seal, "V4: sau khi hoàn tất thì chốt lại bị từ chối")
        ok(box.verify()[1] == [], "V4: sau khi hoàn tất sổ khớp")

    # Nguồn đổi giữa lần chốt dở và lần chạy lại ⇒ KHÔNG hoàn tất hộ.
    box = Box(tmp, "v4_changed", NAV4)
    box.seal(asof=D(2026, 7, 3))
    old = box.sealed.read_bytes()
    nul._atomic_write = boom
    try:
        raises(OSError, box.seal, "V4 đổi nguồn: chết khi thay file")
    finally:
        nul._atomic_write = real_write
    box.write_nav(NAV4[:3] + [("2026-07-07", 1_030_000_001.0)])
    raises(nul.SealIntegrityError, box.seal, "V4: nguồn đổi sau lần chốt dở",
           ["nguồn đã đổi", "Không hoàn tất hộ"])
    ok(box.sealed.read_bytes() == old, "V4: nguồn đổi ⇒ file sổ giữ nguyên")


# ------------------------------------------------------------------ V5. cổng đoạn chốt
def v5_gates(tmp):
    def gate(name, nav, needle, **kw):
        box = Box(tmp, name, nav)
        exc = raises(nul.SealGateError, lambda: box.seal(**kw), f"V5 {name}", needle)
        ok(not box.sealed.exists() and not box.manifest.exists(),
           f"V5 {name}: bị cổng chặn thì không tạo file sổ lẫn manifest")
        return box, exc

    # Thiếu dòng của một phiên (07-03) giữa hai dòng.
    gate("thieu_phien", [NAV4[0], NAV4[2], NAV4[3]],
         ["2026-07-03: nav_history THIẾU dòng", "--from-raw", "CHƯA đủ điều kiện chốt (1 chỗ)"])
    # Thiếu phiên NGAY SAU mốc khởi điểm (07-02).
    gate("thieu_phien_dau", NAV4[1:], "2026-07-02: nav_history THIẾU dòng")
    # Cuối tuần + nghỉ lễ 31/08–02/09 không phải phiên thiếu; dòng của ngày không phiên chụp giờ nào cũng được.
    hol = Box(tmp, "v5_nghi_le", [("2026-07-02", 1e9)])
    hol_inc = {"SpaceX": {"inception_date": "2026-08-27", "starting_capital": 1_000_000_000}}
    Path(hol.inc_path).write_text(json.dumps(hol_inc), encoding="utf-8")
    hol.write_nav([("2026-08-28", 1.01e9), ("2026-08-31", 1.01e9, "2026-08-31T08:00:00"),
                   ("2026-09-03", 1.02e9)])
    _, added = hol.seal(today=D(2026, 9, 30))
    ok(len(added) == 4, f"V5: nghỉ lễ 31/08–02/09 + cuối tuần không được coi là phiên thiếu, được {len(added)}")

    # Dòng chụp TRƯỚC giờ đóng cửa của chính phiên nó.
    pre = NAV4[:2] + [("2026-07-06", 1_015_000_000.0, "2026-07-06T04:49:59"), NAV4[3]]
    box, exc = gate("chup_truoc_dong_cua", pre,
                    ["2026-07-06: dòng chụp số dư lúc 2026-07-06T04:49:59", "TRƯỚC giờ đóng cửa 14:45",
                     "--accept-preclose 2026-07-06="])
    raises(nul.SealGateError, lambda: box.seal(accept_preclose={"2026-07-07": "gõ nhầm"}),
           "V5: nhận nhầm ngày", ["--accept-preclose 2026-07-07", "gõ nhầm ngày", "(2 chỗ)"])
    _, added = box.seal(accept_preclose={"2026-07-06": "0 lệnh ngày đó; đẳng thức tiền dư 33 đ"})
    rec = box.records()[0]
    ok(len(added) == 5 and rec["accepted_preclose"] == {"2026-07-06": {
        "reason": "0 lệnh ngày đó; đẳng thức tiền dư 33 đ", "balance_ts": "2026-07-06T04:49:59",
        "nav": 1_015_000_000.0}},
       f"V5: nhận tường minh ⇒ chốt được và lý do nằm trong manifest: {rec.get('accepted_preclose')}")
    p = box.cli()
    ok(p.returncode == 0 and "dòng chụp trước đóng cửa đã nhận: 2026-07-06" in p.stdout,
       f"V5 CLI: đối chiếu phải nhắc dòng đã nhận: {p.stdout[-200:]}")
    # Biên: đúng 14:45:00 KHÔNG phải trước đóng cửa; 14:44:59 thì có.
    edge = Box(tmp, "v5_bien", NAV4[:2] + [("2026-07-06", 1_015_000_000.0, "2026-07-06T14:45:00"), NAV4[3]])
    ok(len(edge.seal()[1]) == 5, "V5: chụp đúng 14:45:00 là sau đóng cửa — chốt được")
    gate("bien_1_giay", NAV4[:2] + [("2026-07-06", 1_015_000_000.0, "2026-07-06T14:44:59"), NAV4[3]],
         "TRƯỚC giờ đóng cửa")
    # Chụp sáng hôm sau, trước giờ đóng cửa phiên kế (ZaloPay 07-27 thật) ⇒ vẫn là giá chốt phiên đó.
    late_ok = Box(tmp, "v5_sang_hom_sau", NAV4[:2] + [("2026-07-06", 1_015_000_000.0, "2026-07-07T09:15:15"),
                                                    ("2026-07-07", 1_030_000_000.0)])
    ok(len(late_ok.seal()[1]) == 5, "V5: dòng chụp sáng phiên kế (trước 14:45) vẫn chốt được")
    # K3: dòng mang ngày T chụp SAU khi phiên T+1 đã đóng cửa ⇒ từ chối, KHÔNG có lối nhận.
    k3 = NAV4[:2] + [("2026-07-06", 1_015_000_000.0, "2026-07-07T15:00:00"),
                     ("2026-07-07", 1_030_000_000.0, "2026-07-07T19:10:00")]
    box, _ = gate("k3", k3, ["2026-07-06", "phiên đóng cửa gần nhất là 2026-07-07", "không có lối nhận"])
    raises(nul.SealGateError, lambda: box.seal(accept_preclose={"2026-07-06": "cố nhận"}),
           "V5: K3 không nhận được bằng --accept-preclose", ["không có lối nhận", "(2 chỗ)"])
    # balance_ts thiếu / hỏng.
    gate("thieu_ts", NAV4[:2] + [("2026-07-06", 1_015_000_000.0, "")] + NAV4[3:], "balance_ts không đọc được")
    gate("ts_hong", NAV4[:2] + [("2026-07-06", 1_015_000_000.0, "hôm qua")] + NAV4[3:],
         ["balance_ts không đọc được", "'hôm qua'"])
    # balance_ts có múi giờ: 08:00 UTC = 15:00 ICT ⇒ sau đóng cửa.
    tz_ok = Box(tmp, "v5_ts_utc", NAV4[:2] + [("2026-07-06", 1_015_000_000.0, "2026-07-06T08:00:00+00:00"), NAV4[3]])
    ok(len(tz_ok.seal()[1]) == 5, "V5: balance_ts mang múi giờ phải quy về ICT trước khi so 14:45")
    gate("ts_utc_truoc", NAV4[:2] + [("2026-07-06", 1_015_000_000.0, "2026-07-06T07:00:00+00:00"), NAV4[3]],
         "TRƯỚC giờ đóng cửa")
    # Cổng chỉ xét ĐOẠN SẮP CHỐT: dòng đã chốt (và đã nhận) không bị hỏi lại.
    box = Box(tmp, "v5_chi_doan_moi", pre)
    box.seal(asof=D(2026, 7, 6), accept_preclose={"2026-07-06": "đã rà"})
    _, added = box.seal()
    ok([x["date"] for x in added] == [D(2026, 7, 7)] and box.records()[1]["accepted_preclose"] == {},
       "V5: chốt tiếp không phải nhận lại dòng đã chốt")
    p = box.cli()
    ok("đã nhận: 2026-07-06" in p.stdout, "V5: lời nhận cũ vẫn hiện ở các lần sau")
    # CLI: --accept-preclose sai dạng.
    box = Box(tmp, "v5_cli", pre)
    for bad in ("2026-07-06", "2026-07-06=", "2026-07-06=   "):
        p = box.cli("--immutable", "--seal", "--accept-preclose", bad)
        ok(p.returncode == 2 and "NGÀY=lý do" in p.stderr and not box.sealed.exists(),
           f"V5 CLI: --accept-preclose {bad!r} phải rc=2, được rc={p.returncode} {p.stderr[:160]}")
    p = box.cli("--immutable", "--seal", "--accept-preclose", "2026-07-06=đã rà, 0 lệnh")
    ok(p.returncode == 0 and box.records()[0]["accepted_preclose"]["2026-07-06"]["reason"] == "đã rà, 0 lệnh",
       f"V5 CLI: nhận tường minh phải chốt được, rc={p.returncode} {p.stderr[:200]}")


# ------------------------------------------------------------------ V6. thư mục dữ liệu thật
def v6_real_dir(tmp):
    box = Box(tmp, "v6", NAV4)
    fake_real = Path(tmp) / "v6_fake_real"
    fake_real.mkdir()
    target = str(fake_real / "nav_unit_ledger_SpaceX.csv")
    orig = nul.NAV_HISTORY_DIR
    nul.NAV_HISTORY_DIR = str(fake_real)
    try:
        ledger = box.ledger()
        raises(nul.SealRefused, lambda: nul.seal(target, ledger, today=TODAY),
               "V6: thư mục thật không real_data", ["TỪ CHỐI chốt sổ", "--real-data"])
        raises(nul.SealRefused, lambda: nul.seal(target, ledger, today=TODAY, immutable=True),
               "V6: thư mục thật, immutable mà không real_data")
        ok(list(fake_real.iterdir()) == [], "V6: bị từ chối thì không tạo file nào (kể cả file khoá)")
        ok(nul.seal(target, ledger, write=False) == ([], []) and list(fake_real.iterdir()) == [],
           "V6: đối chiếu chỉ-đọc trên thư mục thật chưa có sổ ⇒ ([], []), không tạo file")
        # real_data=True: kho bất biến LUÔN bật, kể cả khi người gọi truyền immutable=False.
        _, added = nul.seal(target, ledger, today=TODAY, real_data=True, immutable=False,
                            meta={"account": "SpaceX"})
        ok(len(added) == 5 and Path(target + nul.MANIFEST_SUFFIX).is_file(),
           "V6: chốt thư mục thật phải sinh manifest dù immutable=False")
        raises(nul.NothingToSeal, lambda: nul.seal(target, ledger, today=TODAY, real_data=True),
               "V6: thư mục thật, chốt lần hai")
        # Thư mục thật: kho bất biến bật cả khi manifest biến mất (thư mục thử thì phải --immutable).
        kept = Path(target + nul.MANIFEST_SUFFIX).read_bytes()
        Path(target + nul.MANIFEST_SUFFIX).unlink()
        raises(nul.SealIntegrityError, lambda: nul.seal(target, ledger, write=False),
               "V6: thư mục thật mất manifest — đối chiếu chỉ-đọc", "không có bản ghi nào")
        Path(target + nul.MANIFEST_SUFFIX).write_bytes(kept)
        raises(nul.SealRefused, lambda: nul.restate(target, ledger, impact_report="x", reason="r",
                                                    approved_by="a"),
               "V6: đính chính thư mục thật không real_data", "--real-data")
    finally:
        nul.NAV_HISTORY_DIR = orig

    # CLI với NAV_HISTORY_DIR trỏ tempdir (không bao giờ chạm data/ thật).
    real2 = Path(tmp) / "v6_fake_real_cli"
    real2.mkdir()

    def cli(*extra):
        code = ("import sys, nav_unit_ledger as n; n.NAV_HISTORY_DIR = sys.argv.pop(1); "
                "raise SystemExit(n.main())")
        return subprocess.run(
            [sys.executable, "-c", code, str(real2), "--account", "SpaceX", "--nav-dir", str(box.dir),
             "--inception-path", box.inc_path, "--flows-path", box.flows_path, *extra],
            capture_output=True, text=True, cwd=str(BIN))
    p = cli("--seal")
    ok(p.returncode == 3 and "--real-data" in p.stderr and list(real2.iterdir()) == [],
       f"V6 CLI: --seal thư mục thật không --real-data phải rc=3, được rc={p.returncode}")
    p = cli("--seal", "--immutable")
    ok(p.returncode == 3 and list(real2.iterdir()) == [], "V6 CLI: --immutable không thay được --real-data")
    p = cli("--seal", "--real-data")
    ok(p.returncode == 0 and (real2 / "nav_unit_ledger_SpaceX.csv.manifest.jsonl").is_file()
       and "kho bất biến: manifest #1" in p.stdout,
       f"V6 CLI: --seal --real-data phải chốt + sinh manifest, rc={p.returncode} {p.stderr[:200]}")
    p = cli("--seal", "--real-data")
    ok(p.returncode == 2 and "NothingToSeal" in p.stderr, "V6 CLI: chốt lần hai ở thư mục thật rc=2")
    p = cli("--restate", "--impact-report", "x.json", "--reason", "r", "--approved-by", "a")
    ok(p.returncode == 3, f"V6 CLI: --restate thư mục thật không --real-data phải rc=3, được {p.returncode}")


# ------------------------------------------------------------------ V7. đính chính sổ đã chốt
def v7_restate(tmp):
    import fund_restatement as fr

    def impact(box, sealed_path=None, out_name="impact.json"):
        out = str(box.dir / out_name)
        args = ["impact", "--account", "SpaceX", "--old-nav-dir", str(box.dir / "old"),
                "--new-nav-dir", str(box.dir), "--inception-path", box.inc_path,
                "--flows-path", box.flows_path, "--reports-dir", str(box.dir / "reports"),
                "--out", out]
        if sealed_path:
            args += ["--sealed-ledger", sealed_path]
        rc = subprocess.run([sys.executable, str(BIN / "fund_restatement.py"), *args],
                            capture_output=True, text=True)
        return rc, out

    def setup(name, nav_new):
        box = Box(tmp, name, NAV4)
        (box.dir / "old").mkdir()
        (box.dir / "reports").mkdir()
        (box.dir / "old" / "nav_history_SpaceX.csv").write_bytes(
            (box.dir / "nav_history_SpaceX.csv").read_bytes())
        box.seal()
        sealed_bytes = box.sealed.read_bytes()
        box.write_nav(nav_new)
        return box, sealed_bytes

    fixed = [("2026-07-02", 1_005_000_000.0)] + NAV4[1:]
    box, old_bytes = setup("v7", fixed)
    raises(nul.LedgerDriftError, box.seal, "V7: sau khi sửa nguồn, chốt thường phải báo lệch")
    rc, out = impact(box, str(box.sealed))
    report = json.loads(Path(out).read_text(encoding="utf-8")) if rc.returncode == 0 else {}
    bind = report.get("ledger_binding") or {}
    want_new = nul._content(box.ledger(), D(2026, 7, 7))
    ok(rc.returncode == 0 and bind.get("sealed_md5") == md5(old_bytes)
       and bind.get("restated_md5") == md5(want_new) and bind.get("sealed_last_date") == "2026-07-07"
       and bind.get("n_ledger_diffs", 0) >= 1,
       f"V7: báo cáo tác động phải mang md5 sổ đang chốt + md5 sổ sau đính chính: {bind} {rc.stderr[:200]}")

    def do_restate(b, report_path, **kw):
        kw.setdefault("reason", "NAV 07-02 đếm trùng một lô")
        kw.setdefault("approved_by", "user 2026-10-14")
        kw.setdefault("meta", {"account": "SpaceX"})
        return nul.restate(str(b.sealed), b.ledger(), impact_report=report_path, **kw)

    for kw, needle in (({"reason": ""}, "--reason và --approved-by"), ({"reason": "   "}, "--reason"),
                       ({"approved_by": ""}, "--approved-by"), ({"approved_by": None}, "--approved-by")):
        raises(nul.SealGateError, lambda: do_restate(box, out, **kw), f"V7: thiếu {kw}", needle)
    raises(nul.SealGateError, lambda: do_restate(box, out, meta={"account": "ZaloPay"}),
           "V7: báo cáo tác động của tài khoản khác (§12)", "KHÔNG phải của thay đổi này")
    bad = box.dir / "bad.json"
    for label, body in (("không phải JSON", "{"), ("thiếu ledger_binding", json.dumps({"account": "SpaceX"})),
                        ("ledger_binding null", json.dumps({"account": "SpaceX", "ledger_binding": None})),
                        ("là list", "[]")):
        bad.write_text(body, encoding="utf-8")
        raises(nul.SealGateError, lambda: do_restate(box, str(bad)), f"V7: báo cáo {label}",
               "không đọc được hoặc thiếu")
    raises(FileNotFoundError, lambda: do_restate(box, str(box.dir / "khong_co.json")),
           "V7: không có file báo cáo tác động")
    ok(box.sealed.read_bytes() == old_bytes and len(box.records()) == 1
       and not [x for x in box.ledger_dir.iterdir() if ".superseded." in x.name],
       "V7: mọi lần từ chối ở trên không được đổi sổ, manifest, hay sinh file lưu")
    # Báo cáo của MỘT THAY ĐỔI KHÁC (nguồn đổi thêm sau khi đo) ⇒ từ chối.
    box.write_nav([("2026-07-02", 1_004_000_000.0)] + NAV4[1:])
    raises(nul.SealGateError, lambda: do_restate(box, out), "V7: nguồn đổi sau khi đo tác động",
           ["KHÔNG phải của thay đổi này", md5(old_bytes)])
    box.write_nav(fixed)

    rec = do_restate(box, out)
    new_bytes = box.sealed.read_bytes()
    recs = box.records()
    archives = [x for x in box.ledger_dir.iterdir() if ".superseded." in x.name]
    ok(new_bytes == want_new and md5(new_bytes) == rec["md5"] == recs[-1]["md5"],
       "V7: sau đính chính file sổ = chuỗi dựng lại, md5 khớp manifest")
    ok(len(recs) == 2 and rec["kind"] == "restate" and rec["seq"] == 2
       and rec["md5_before"] == md5(old_bytes) == recs[0]["md5"],
       f"V7: bản ghi restate phải nối md5 với lần chốt trước: {rec}")
    ok(len(archives) == 1 and archives[0].read_bytes() == old_bytes
       and archives[0].name == rec["archived_as"]
       == f"nav_unit_ledger_SpaceX.csv.superseded.2.{md5(old_bytes)[:12]}.csv",
       f"V7: sổ cũ phải được lưu NGUYÊN BYTE, tên mang seq + md5: {[x.name for x in archives]}")
    ok(rec["reason"] == "NAV 07-02 đếm trùng một lô" and rec["approved_by"] == "user 2026-10-14"
       and rec["impact_report_md5"] == md5(Path(out).read_bytes()) and rec["n_diffs"] >= 1
       and any("2026-07-02 nav" in d for d in rec["diffs"]) and rec["rows_total"] == 5
       and rec["last_date"] == "2026-07-07" and float(rec["last_unit_price"]) == 10_300.0,
       f"V7: bản ghi restate thiếu lý do/người duyệt/md5 báo cáo/dòng lệch: {rec}")
    ok(box.verify()[1] == [], "V7: sau đính chính sổ khớp chuỗi dựng lại")
    raises(nul.NothingToSeal, lambda: do_restate(box, out), "V7: đính chính lần hai không còn gì để sửa",
           "không có gì để đính chính")
    box.write_nav(fixed + [("2026-07-08", 1_040_000_000.0)])
    _, added = box.seal()
    ok([x["date"] for x in added] == [D(2026, 7, 8)] and box.sealed.read_bytes().startswith(new_bytes)
       and box.records()[-1]["md5_before"] == rec["md5"], "V7: sau đính chính chốt tiếp bình thường")

    # CLI end-to-end + đính chính CHÈN một phiên thiếu vào giữa (số dòng tăng).
    gap = [NAV4[0], NAV4[2], NAV4[3]]
    box = Box(tmp, "v7_cli", gap)
    (box.dir / "old").mkdir()
    (box.dir / "reports").mkdir()
    raises(nul.SealGateError, box.seal, "V7 CLI: có phiên thiếu thì chưa chốt được")
    # dựng tình huống "đã chốt rồi mới backfill": chốt tới 07-02, rồi chốt 07-06.. sau khi backfill là lệch
    box.write_nav([NAV4[0]])
    box.seal()
    box.write_nav(NAV4[:2])
    box.seal()
    (box.dir / "old" / "nav_history_SpaceX.csv").write_bytes((box.dir / "nav_history_SpaceX.csv").read_bytes())
    sealed_before = box.sealed.read_bytes()
    box.write_nav([("2026-07-02", 1_010_000_000.0), ("2026-07-03", 1_021_000_000.0)])
    rc, out = impact(box, str(box.sealed))
    p = box.cli("--restate", "--impact-report", out, "--reason", "sửa 07-03", "--approved-by", "user")
    ok(rc.returncode == 0 and p.returncode == 0 and "ĐÃ ĐÍNH CHÍNH" in p.stdout
       and "manifest #3 (restate)" in p.stdout and box.sealed.read_bytes() != sealed_before,
       f"V7 CLI: --restate phải rc=0, được rc={p.returncode} {p.stdout[-300:]} {p.stderr[-300:]}")
    p = box.cli("--restate", "--impact-report", out, "--reason", "x", "--approved-by", "y")
    ok(p.returncode == 2 and "NothingToSeal" in p.stderr, "V7 CLI: --restate lần hai rc=2")
    p = box.cli("--restate", "--reason", "x", "--approved-by", "y")
    ok(p.returncode == 2 and "--impact-report" in p.stderr, "V7 CLI: --restate thiếu --impact-report bị argparse chặn")
    p = box.cli("--restate", "--seal", "--impact-report", out)
    ok(p.returncode == 2, "V7 CLI: --seal và --restate không đi cùng nhau")

    # Sổ chưa từng chốt ở kho bất biến ⇒ không có gì để đính chính.
    box = Box(tmp, "v7_none", NAV4)
    raises(nul.NothingToSeal, lambda: do_restate(box, out), "V7: chưa có sổ kho bất biến",
           "chốt lần đầu bằng --seal")

    # File lưu đã tồn tại với nội dung khác ⇒ từ chối, sổ giữ nguyên.
    box, old_bytes = setup("v7_archive", fixed)
    rc, out = impact(box, str(box.sealed))
    clash = Path(f"{box.sealed}.superseded.2.{md5(old_bytes)[:12]}.csv")
    clash.write_bytes(b"khac")
    raises(nul.SealIntegrityError, lambda: do_restate(box, out), "V7: file lưu trùng tên khác nội dung",
           "ghi-một-lần")
    ok(box.sealed.read_bytes() == old_bytes and len(box.records()) == 1, "V7: file lưu xung đột ⇒ không đổi gì")
    clash.write_bytes(old_bytes)                 # trùng nội dung (lần trước chết sau khi lưu) ⇒ đi tiếp
    ok(do_restate(box, out)["kind"] == "restate", "V7: file lưu đã có ĐÚNG nội dung thì đính chính đi tiếp")

    # Chết giữa chừng khi đính chính: manifest + file lưu đã có, file sổ chưa thay ⇒ chạy lại hoàn tất.
    box, old_bytes = setup("v7_crash", fixed)
    rc, out = impact(box, str(box.sealed))
    real_write = nul._atomic_write

    def boom_main(path, data):
        if path == str(box.sealed):
            raise OSError("mất điện (giả lập)")
        return real_write(path, data)

    nul._atomic_write = boom_main
    try:
        raises(OSError, lambda: do_restate(box, out), "V7: chết khi thay file sổ")
    finally:
        nul._atomic_write = real_write
    ok(box.sealed.read_bytes() == old_bytes and len(box.records()) == 2,
       "V7 chết giữa chừng: manifest có bản ghi restate, file sổ chưa đổi")
    raises(nul.SealIntegrityError, box.verify, "V7: đối chiếu khi đính chính dở", "CHƯA thay file")
    rec = do_restate(box, out)
    ok(rec["kind"] == "restate" and len(box.records()) == 2
       and md5(box.sealed.read_bytes()) == rec["md5"] and box.verify()[1] == [],
       "V7: chạy lại hoàn tất đúng lần đính chính dở, không thêm bản ghi")

    # Lời nhận dòng chụp-trước-đóng-cửa: đính chính làm dòng đó hết là chụp-trước ⇒ lời nhận cũ
    # không thành lỗi "gõ nhầm"; đính chính tạo dòng chụp-trước MỚI thì vẫn phải nhận.
    pre = NAV4[:2] + [("2026-07-06", 1_015_000_000.0, "2026-07-06T04:49:59"), NAV4[3]]
    box = Box(tmp, "v7_accept", pre)
    (box.dir / "old").mkdir()
    (box.dir / "reports").mkdir()
    (box.dir / "old" / "nav_history_SpaceX.csv").write_bytes((box.dir / "nav_history_SpaceX.csv").read_bytes())
    box.seal(accept_preclose={"2026-07-06": "đã rà"})
    box.write_nav(NAV4[:2] + [("2026-07-06", 1_014_000_000.0, "2026-07-06T14:45:00"), NAV4[3]])
    rc, out = impact(box, str(box.sealed))
    rec = do_restate(box, out)
    ok(rec["accepted_preclose"] == {}, f"V7: dòng đã hết chụp-trước thì không mang lời nhận nữa: {rec['accepted_preclose']}")
    # Đính chính MỘT DÒNG KHÁC trong khi dòng chụp-trước đã nhận vẫn y nguyên ⇒ lời nhận của lần
    # chốt trước phải được mang theo (không bắt nhận lại, không rơi khỏi manifest).
    box = Box(tmp, "v7_carry", pre)
    (box.dir / "old").mkdir()
    (box.dir / "reports").mkdir()
    (box.dir / "old" / "nav_history_SpaceX.csv").write_bytes((box.dir / "nav_history_SpaceX.csv").read_bytes())
    box.seal(accept_preclose={"2026-07-06": "đã rà"})
    box.write_nav([("2026-07-02", 1_005_000_000.0)] + pre[1:])
    rc, out3 = impact(box, str(box.sealed))
    rec = do_restate(box, out3)
    ok(rc.returncode == 0 and rec["accepted_preclose"] == {"2026-07-06": {
        "reason": "đã rà", "balance_ts": "2026-07-06T04:49:59", "nav": 1_015_000_000.0}},
       f"V7: lời nhận của lần chốt trước phải theo sang bản ghi restate: {rec['accepted_preclose']}")
    box2, _ = setup("v7_new_preclose", NAV4[:2] + [("2026-07-06", 1_014_000_000.0, "2026-07-06T09:00:00"), NAV4[3]])
    rc, out2 = impact(box2, str(box2.sealed))
    raises(nul.SealGateError, lambda: do_restate(box2, out2), "V7: đính chính sinh dòng chụp trước đóng cửa",
           "TRƯỚC giờ đóng cửa")
    ok(do_restate(box2, out2, accept_preclose={"2026-07-06": "rà rồi"})["accepted_preclose"]
       == {"2026-07-06": {"reason": "rà rồi", "balance_ts": "2026-07-06T09:00:00", "nav": 1_014_000_000.0}},
       "V7: nhận tường minh khi đính chính")
    ok(fr.TIER_REISSUE_ABOVE == 0.5 and fr.TIER_NOTE_FROM == 0.05, "V7: ngưỡng chính sách điểm 4")


# ------------------------------------------------------------------ V8. thư mục thật theo nội dung (B2)
def v8_real_dir_by_content(tmp):
    box = Box(tmp, "v8", NAV4)
    (box.ledger_dir / "dnse_raw_2026-07-02.jsonl").write_text("{}\n", encoding="utf-8")
    sandbox_a = Path(tmp) / "v8_wc_root_a"
    sandbox_a.mkdir()
    (sandbox_a / "wc_env.sh").write_text("", encoding="utf-8")
    import trading_bot.vn_market                      # lịch phiên: sandbox A trỏ đúng gói đang dùng
    os.symlink(Path(trading_bot.vn_market.__file__).resolve().parent, sandbox_a / "trading_bot")
    env = dict(os.environ, WC_ROOT=str(sandbox_a))

    def cli(*extra):
        return subprocess.run(
            [sys.executable, str(BIN / "nav_unit_ledger.py"), "--account", "SpaceX",
             "--nav-dir", str(box.dir), "--inception-path", box.inc_path, "--flows-path", box.flows_path,
             "--ledger-dir", str(box.ledger_dir), *extra], capture_output=True, text=True, env=env)
    p = cli("--seal")
    ok(p.returncode == 3 and "--real-data" in p.stderr and "dnse_raw_*.jsonl" in p.stderr
       and sorted(x.name for x in box.ledger_dir.iterdir()) == ["dnse_raw_2026-07-02.jsonl"],
       f"V8 B2: WC_ROOT khác + --ledger-dir có dnse_raw ⇒ --seal rc=3, không tạo file; rc={p.returncode} {p.stderr[-200:]}")
    p = cli("--seal", "--immutable")
    ok(p.returncode == 3 and not box.sealed.exists(), "V8 B2: --immutable không thay được --real-data")
    raises(nul.SealRefused, lambda: nul.restate(str(box.sealed), box.ledger(), impact_report="x",
                                                reason="r", approved_by="a"),
           "V8 B2: đính chính thư mục có dnse_raw không real_data", "--real-data")
    p = cli("--seal", "--real-data")
    ok(p.returncode == 0 and box.manifest.is_file() and "kho bất biến: manifest #1" in p.stdout,
       f"V8 B2: có --real-data ⇒ chốt ở chế độ kho bất biến (không cần --immutable): rc={p.returncode} {p.stderr[-200:]}")
    ok(nul.is_real_data_dir(str(box.ledger_dir)) and not nul.is_real_data_dir(str(box.dir)),
       "V8 B2: chỉ thư mục có dnse_raw mới là thật")


# ------------------------------------------------------------------ V9. lời nhận gắn với dòng (B6)
def v9_accept_identity(tmp):
    pre = NAV4[:2] + [("2026-07-06", 1_015_000_000.0, "2026-07-06T04:49:59"), NAV4[3]]
    ident = {"reason": "đã rà", "balance_ts": "2026-07-06T04:49:59", "nav": 1_015_000_000.0}

    def setup(name):
        box = Box(tmp, name, pre)
        (box.dir / "old").mkdir()
        (box.dir / "reports").mkdir()
        (box.dir / "old" / "nav_history_SpaceX.csv").write_bytes((box.dir / "nav_history_SpaceX.csv").read_bytes())
        box.seal(accept_preclose={"2026-07-06": "đã rà"})
        return box

    def impact(box, name):
        out = str(box.dir / name)
        p = subprocess.run([sys.executable, str(BIN / "fund_restatement.py"), "impact", "--account", "SpaceX",
                            "--old-nav-dir", str(box.dir / "old"), "--new-nav-dir", str(box.dir),
                            "--inception-path", box.inc_path, "--flows-path", box.flows_path,
                            "--reports-dir", str(box.dir / "reports"), "--sealed-ledger", str(box.sealed),
                            "--out", out], capture_output=True, text=True)
        ok(p.returncode == 0, f"V9: impact {name} rc={p.returncode} {p.stderr[-200:]}")
        return out

    def restate(box, out, **kw):
        return nul.restate(str(box.sealed), box.ledger(), impact_report=out, reason="sửa", approved_by="user",
                           meta={"account": "SpaceX"}, **kw)

    box = setup("v9_demo")
    ok(box.records()[0]["accepted_preclose"] == {"2026-07-06": ident},
       f"V9: manifest lưu lời nhận kèm balance_ts + NAV của dòng: {box.records()[0]['accepted_preclose']}")
    # Demo của reviewer: lời nhận cho "NAV 1015 lúc 04:49" KHÔNG được tự áp cho "NAV 1005 lúc 11:00".
    box.write_nav(NAV4[:2] + [("2026-07-06", 1_005_000_000.0, "2026-07-06T11:00:00"), NAV4[3]])
    out = impact(box, "i1.json")
    sealed_bytes = box.sealed.read_bytes()
    raises(nul.SealGateError, lambda: restate(box, out), "V9 B6: dòng đã đổi NAV + giờ chụp",
           ["KHÔNG còn là của dòng này", "'2026-07-06T04:49:59'", "1015000000.0", "'2026-07-06T11:00:00'",
            "--accept-preclose 2026-07-06="])
    ok(box.sealed.read_bytes() == sealed_bytes and len(box.records()) == 1, "V9 B6: bị chặn thì sổ/manifest không đổi")
    rec = restate(box, out, accept_preclose={"2026-07-06": "rà lại: 1005 lúc 11:00"})
    ok(rec["accepted_preclose"] == {"2026-07-06": {"reason": "rà lại: 1005 lúc 11:00",
                                                   "balance_ts": "2026-07-06T11:00:00", "nav": 1_005_000_000.0}},
       f"V9 B6: nhận lại thì lời nhận mới mang danh tính dòng mới: {rec['accepted_preclose']}")
    p = box.cli()
    ok(p.returncode == 0 and "đã nhận: 2026-07-06" in p.stdout, "V9: CLI vẫn in ngày đã nhận")

    # Chỉ đổi giờ chụp (NAV giữ) — kèm một dòng khác đổi để có gì đính chính ⇒ vẫn phải nhận lại.
    box = setup("v9_ts")
    box.write_nav([("2026-07-02", 1_005_000_000.0), NAV4[1],
                   ("2026-07-06", 1_015_000_000.0, "2026-07-06T10:00:00"), NAV4[3]])
    raises(nul.SealGateError, lambda: restate(box, impact(box, "i2.json")), "V9 B6: chỉ đổi balance_ts",
           "KHÔNG còn là của dòng này")
    # Chỉ đổi NAV (giờ chụp giữ) ⇒ phải nhận lại.
    box = setup("v9_nav")
    box.write_nav(NAV4[:2] + [("2026-07-06", 1_014_000_000.0, "2026-07-06T04:49:59"), NAV4[3]])
    raises(nul.SealGateError, lambda: restate(box, impact(box, "i3.json")), "V9 B6: chỉ đổi NAV",
           "KHÔNG còn là của dòng này")
    # Dòng giữ nguyên ⇒ lời nhận cũ theo sang NGUYÊN (lý do cũ, danh tính cũ).
    box = setup("v9_keep")
    box.write_nav([("2026-07-02", 1_005_000_000.0)] + pre[1:])
    ok(restate(box, impact(box, "i4.json"))["accepted_preclose"] == {"2026-07-06": ident},
       "V9 B6: dòng không đổi ⇒ lời nhận cũ theo sang nguyên vẹn")
    # Lời nhận dạng cũ (chỉ là chuỗi, không danh tính) không được mang sang.
    ledger = Box(tmp, "v9_legacy", pre).ledger()
    problems, accepted = nul.seal_gate(ledger, ledger[0]["date"], ledger, {},
                                       carried={"2026-07-06": "lý do kiểu cũ"})
    ok(accepted == {} and len(problems) == 1 and "bản ghi cũ không ghi balance_ts/NAV" in problems[0],
       f"V9 B6: lời nhận kiểu cũ (chuỗi) không có danh tính ⇒ không mang sang: {problems}")
    problems, accepted = nul.seal_gate(ledger, ledger[0]["date"], ledger, {}, carried={"2026-07-06": ident})
    ok(problems == [] and accepted == {"2026-07-06": ident}, "V9 B6: seal_gate mang lời nhận khớp danh tính")
    problems, _ = nul.seal_gate(ledger, ledger[0]["date"], ledger, {},
                                carried={"2026-07-06": dict(ident, nav=1_015_000_001.0)})
    ok(len(problems) == 1 and "KHÔNG còn là của dòng này" in problems[0], "V9 B6: lệch 1 đồng NAV cũng phải nhận lại")


# ------------------------------------------------------------------ V10. khoá, phiên thiếu, SEAL_MD5
def _blocked_while_locked(lock_path, cmd, during=None):
    """Giữ khoá độc quyền `lock_path`, chạy `cmd`: trả (có bị chặn không, tiến trình đã xong)."""
    with open(lock_path, "a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        deadline = time.monotonic() + 1.5
        while time.monotonic() < deadline and proc.poll() is None:
            time.sleep(0.05)
        blocked = proc.poll() is None
        if during:
            during()
        fcntl.flock(lock, fcntl.LOCK_UN)
    out, err = proc.communicate(timeout=60)
    return blocked, proc.returncode, out, err


def v10_lock_gap_md5(tmp):
    # N21: thiếu phiên NGAY SAU dòng đã chốt cuối.
    box = Box(tmp, "v10_gap", NAV4)
    box.seal(asof=D(2026, 7, 2))
    box.write_nav([NAV4[0], NAV4[2], NAV4[3]])
    raises(nul.SealGateError, box.seal, "V10 N21: thiếu 07-03 ngay sau dòng đã chốt cuối 07-02",
           ["2026-07-03: nav_history THIẾU dòng", "giữa 2026-07-02 và 2026-07-06"])
    ok(len(box.records()) == 1, "V10 N21: bị chặn thì manifest không thêm bản ghi")

    # B13: mỗi lần chốt / đính chính in SEAL_MD5 <account> <md5 sổ> <md5 manifest>; đối chiếu thì không.
    box = Box(tmp, "v10_md5", NAV4)
    p = box.cli("--immutable", "--seal")
    line = f"SEAL_MD5 SpaceX {md5(box.sealed.read_bytes())} {md5(box.manifest.read_bytes())}"
    ok(p.returncode == 0 and line in p.stdout.splitlines(), f"V10 B13: --seal phải in đúng dòng {line!r}: {p.stdout[-300:]}")
    p = box.cli()
    ok(p.returncode == 0 and "SEAL_MD5" not in p.stdout, "V10 B13: đối chiếu chỉ-đọc không in SEAL_MD5")
    p = box.cli("--seal")
    ok(p.returncode == 2 and "SEAL_MD5" not in p.stdout, "V10 B13: chốt bị từ chối không in SEAL_MD5")

    # N2: --restate phải giữ khoá độc quyền.
    box = Box(tmp, "v10_restate_lock", NAV4)
    (box.dir / "old").mkdir()
    (box.dir / "reports").mkdir()
    (box.dir / "old" / "nav_history_SpaceX.csv").write_bytes((box.dir / "nav_history_SpaceX.csv").read_bytes())
    box.seal()
    box.write_nav([("2026-07-02", 1_005_000_000.0)] + NAV4[1:])
    out = str(box.dir / "impact.json")
    subprocess.run([sys.executable, str(BIN / "fund_restatement.py"), "impact", "--account", "SpaceX",
                    "--old-nav-dir", str(box.dir / "old"), "--new-nav-dir", str(box.dir), "--inception-path",
                    box.inc_path, "--flows-path", box.flows_path, "--reports-dir", str(box.dir / "reports"),
                    "--sealed-ledger", str(box.sealed), "--out", out], capture_output=True, text=True)
    cmd = [sys.executable, str(BIN / "nav_unit_ledger.py"), "--account", "SpaceX", "--nav-dir", str(box.dir),
           "--inception-path", box.inc_path, "--flows-path", box.flows_path, "--ledger-dir", str(box.ledger_dir),
           "--restate", "--impact-report", out, "--reason", "sửa 07-02", "--approved-by", "user"]
    sealed_before, seen = box.sealed.read_bytes(), {}
    blocked, rc, so, se = _blocked_while_locked(
        str(box.sealed) + ".lock", cmd,
        during=lambda: seen.update(same=box.sealed.read_bytes() == sealed_before, n=len(box.records())))
    ok(blocked and seen == {"same": True, "n": 1},
       f"V10 N2: --restate phải CHỜ (không đụng sổ/manifest) khi tiến trình khác giữ khoá: {seen} rc={rc} {se[-200:]}")
    line = f"SEAL_MD5 SpaceX {md5(box.sealed.read_bytes())} {md5(box.manifest.read_bytes())}"
    ok(rc == 0 and "ĐÃ ĐÍNH CHÍNH" in so and box.records()[-1]["kind"] == "restate" and line in so.splitlines(),
       f"V10 N2/B13: nhả khoá ⇒ đính chính xong, in SEAL_MD5: rc={rc} {so[-300:]} {se[-200:]}")

    # B12: lệnh chỉ-đọc chạy SONG SONG lần chốt đang giữ khoá (manifest đã ghi, file chưa thay) phải
    # CHỜ rồi báo khớp — không báo nhầm "chết giữa chừng".
    box = Box(tmp, "v10_ro", NAV4)
    box.seal(asof=D(2026, 7, 3))
    real_write = nul._atomic_write

    def boom(path, data):
        raise OSError("đang ghi (giả lập)")
    nul._atomic_write = boom
    try:
        raises(OSError, box.seal, "V10 B12: tạo trạng thái 'manifest đã ghi, file chưa thay'")
    finally:
        nul._atomic_write = real_write
    ledger = box.ledger()
    cmd = [sys.executable, str(BIN / "nav_unit_ledger.py"), "--account", "SpaceX", "--nav-dir", str(box.dir),
           "--inception-path", box.inc_path, "--flows-path", box.flows_path, "--ledger-dir", str(box.ledger_dir)]
    blocked, rc, so, se = _blocked_while_locked(
        str(box.sealed) + ".lock", cmd,
        during=lambda: nul._vault_state(str(box.sealed), ledger, write=True))   # "người chốt" ghi xong
    ok(blocked and rc == 0 and "khớp chuỗi dựng lại" in so and "CHƯA thay file" not in se,
       f"V10 B12: đối chiếu chỉ-đọc phải chờ khoá rồi báo khớp: blocked={blocked} rc={rc} {se[-200:]}")
    # Tiến trình chốt CHẾT thật (không ai giữ khoá) ⇒ vẫn báo đúng "chết giữa chừng".
    nul._atomic_write = boom
    try:
        box.write_nav(NAV4 + [("2026-07-08", 1_040_000_000.0)])
        raises(OSError, box.seal, "V10 B12: chết thật")
    finally:
        nul._atomic_write = real_write
    p = box.cli()
    ok(p.returncode == 2 and "CHƯA thay file" in p.stderr, "V10 B12: không ai giữ khoá ⇒ báo chết giữa chừng")

# ------------------------------------------------------------------ V11. mốc ngoài kho (arch-review lần 2, R1)
def v11_external_anchor(tmp):
    box = Box(tmp, "v11", NAV4)
    p = box.cli("--immutable", "--seal", "--asof", "2026-07-03")
    a1 = next(x for x in p.stdout.splitlines() if x.startswith("SEAL_MD5 "))
    box.write_nav(NAV4)
    p = box.cli("--seal")
    a2 = next(x for x in p.stdout.splitlines() if x.startswith("SEAL_MD5 "))
    p = box.cli("--verify-anchor", a1, "--verify-anchor", a2)
    ok(p.returncode == 0 and "mốc ngoài kho KHỚP" in p.stdout and "manifest #1" in p.stdout and "manifest #2" in p.stdout,
       f"V11: mốc cũ (phần đầu manifest) và mốc mới đều khớp: rc={p.returncode} {p.stdout[-300:]} {p.stderr[-200:]}")
    ok(nul.verify_anchor(str(box.sealed), "SpaceX", a1) == {"seq": 1, "md5": a1.split()[2]},
       "V11: verify_anchor trả đúng bản ghi ứng với mốc")
    # Hoàn tác ĐỒNG THỜI file sổ + đuôi manifest về lần chốt #1 ⇒ đối chiếu thường KHỚP, mốc #2 bắt được.
    data1 = box.sealed.read_bytes()[: len(box.sealed.read_bytes())]
    lines = box.manifest.read_bytes().splitlines(keepends=True)
    keep_ledger, keep_manifest = box.sealed.read_bytes(), box.manifest.read_bytes()
    box.manifest.write_bytes(lines[0])
    first = nul._content(box.ledger(), D(2026, 7, 3))
    box.sealed.write_bytes(first)
    box.write_nav(NAV4[:2])
    p = box.cli()
    ok(p.returncode == 0 and "khớp chuỗi dựng lại" in p.stdout,
       "V11: (giới hạn đã biết) hoàn tác đồng thời file + đuôi manifest thì đối chiếu thường KHÔNG thấy")
    p = box.cli("--verify-anchor", a2)
    ok(p.returncode == 2 and "AnchorError" in p.stderr and "KHÔNG còn chứa nguyên vẹn" in p.stderr,
       f"V11: mốc ngoài kho phải bắt được hoàn tác đồng thời: rc={p.returncode} {p.stderr[-300:]}")
    ok(box.cli("--verify-anchor", a1).returncode == 0, "V11: mốc #1 vẫn khớp sau khi hoàn tác về #1")
    box.sealed.write_bytes(keep_ledger)
    box.manifest.write_bytes(keep_manifest)
    box.write_nav(NAV4)
    # Xoá CẢ file sổ + manifest ⇒ đối chiếu thường thấy "0 dòng" (rc=0), mốc ngoài kho rc=2.
    box.sealed.unlink()
    box.manifest.unlink()
    p = box.cli()
    ok(p.returncode == 0, "V11: (giới hạn đã biết) xoá cả sổ lẫn manifest ⇒ đối chiếu thường không thấy")
    p = box.cli("--verify-anchor", a2)
    ok(p.returncode == 2 and "KHÔNG tồn tại" in p.stderr and "ĐÃ chốt" in p.stderr,
       f"V11: xoá cả sổ + manifest ⇒ mốc ngoài kho rc=2: {p.stderr[-300:]}")
    box.manifest.write_bytes(b"")
    p = box.cli("--verify-anchor", a2)
    ok(p.returncode == 2 and "rỗng" in p.stderr, "V11: manifest rỗng ⇒ rc=2")
    box.manifest.unlink()
    # Mốc sai dạng / tài khoản khác / mốc tự mâu thuẫn / dùng sai cờ.
    box.sealed.write_bytes(keep_ledger)
    box.manifest.write_bytes(keep_manifest)
    for bad, needle in (("SEAL_MD5 SpaceX abc", "không đúng dạng"), ("MD5 SpaceX a b", "không đúng dạng"),
                        (a2.replace("SpaceX", "ZaloPay"), "§12"),
                        (" ".join(a2.split()[:2] + ["0" * 32, a2.split()[3]]), "tự mâu thuẫn")):
        p = box.cli("--verify-anchor", bad)
        ok(p.returncode == 2 and needle in p.stderr, f"V11: mốc {bad!r} ⇒ rc=2 nêu {needle!r}: {p.stderr[-200:]}")
    p = box.cli("--verify-anchor", a2, "--seal")
    ok(p.returncode == 2 and "--verify-anchor chỉ đi với" in p.stderr, "V11: --verify-anchor không đi cùng --seal")
    p = subprocess.run([sys.executable, str(BIN / "nav_unit_ledger.py"), "--account", "SpaceX", "--nav-dir",
                        str(box.dir), "--inception-path", box.inc_path, "--flows-path", box.flows_path,
                        "--verify-anchor", a2], capture_output=True, text=True)
    ok(p.returncode == 2 and "--ledger-dir" in p.stderr, "V11: --verify-anchor cần --ledger-dir")
    doc = nul.__doc__
    ok("Xoá CẢ file sổ lẫn manifest" in doc and "--verify-anchor" in doc,
       "V11: docstring không được hứa bắt 'xoá file' khi xoá cả hai")
    del data1


def main():
    with tempfile.TemporaryDirectory(prefix="nav_vault_selfcheck_") as tmp:
        v1_seal_and_manifest(tmp)
        v2_today_gate(tmp)
        v3_tamper(tmp)
        v4_crash_resume(tmp)
        v5_gates(tmp)
        v6_real_dir(tmp)
        v7_restate(tmp)
        v8_real_dir_by_content(tmp)
        v9_accept_identity(tmp)
        v10_lock_gap_md5(tmp)
        v11_external_anchor(tmp)
    if FAILS:
        print(f"FAIL — {len(FAILS)}/{N} assertion hỏng (nav_ledger_vault_selfcheck.py)")
        return 1
    print(f"OK — {N} assertion PASS (nav_ledger_vault_selfcheck.py)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
