#!/usr/bin/env python3
"""aria-K — backfill 1 lần: fill ATC ZaloPay 2026-07-10 VHC oid 502431 (600cp @57.500) mà bot không
thấy vì tắt trước khi kết quả ATC công bố (Winston aria-I; bản vá executor_atc_postclose.patch).

KHÔNG sửa dòng nào có sẵn: chỉ NỐI THÊM 1 dòng FILL có cờ `backfill=true` vào
`data/execution_logs/exec_ZaloPay_2026-07-10_journal.csv` (layout 10 cột cũ của file đó), sau khi
sao lưu nguyên file thành `<file>.pre_aria_K`. Không chạm dnse_raw (bản ghi API broker — không bịa
record broker), không chạm state.json, không chạm account_seed_capital.json.

Bằng chứng kiểm LẠI trước khi ghi (thiếu/không khớp ⇒ dừng, rc=2, in giá trị thật đọc được):
  1. Email khớp lệnh DNSE msg 19f4b4977cc2786e (CSV đã parse, aria-F): tiểu khoản 0001743768,
     VHC BÁN tổng 1.800cp, trong đó đúng 600cp @57.500 (100+500).
  2. dnse_raw_2026-07-10.jsonl lọc accountNo 0001743768 (§12): VHC bán fillQuantity = 1.200cp;
     oid 502431 có orderType ATC và fillQuantity 0 (poll cuối 14:45:05).
  3. Journal: FILL (max qty theo child_oid) VHC = 1.200cp; chưa có dòng FILL nào cho oid 502431.
Idempotent: đã có dòng FILL backfill cho 502431 ⇒ in "đã backfill", rc=0, không ghi.

⚠ ĐẾM 2 LẦN / TÁC DỤNG PHỤ — đọc trước khi --apply (đo sandbox, xem README.md cùng thư mục):
  · reconcile_equity.py đọc fill từ dnse_raw + `missing_fills_broker_confirmed` (seed), KHÔNG đọc
    journal ⇒ dòng này không đổi reconcile, KHÔNG đếm 2 lần. Tuyệt đối không nạp thêm 600cp vào
    dnse_raw (khi đó seed + raw mới là đếm 2 lần).
  · verify_account_snapshot.py so dnse_raw vs journal: sau backfill journal −1.800 vs raw −1.200 ⇒
    `WARN qty mismatch VHC` ⇒ `verified=false`, rc=1 cho MỌI lần chạy ZaloPay có 2026-07-10 trong
    --dates (lệch này vĩnh viễn vì dnse_raw là lịch sử). Xem README.md cho khuyến nghị.

Chạy:  $DNA_PYEXE backfill_vhc_0710.py            # dry-run: kiểm bằng chứng + in dòng sẽ ghi
       $DNA_PYEXE backfill_vhc_0710.py --apply    # ghi thật
Sandbox: BACKFILL_EXEC_DIR=<thư mục bản sao execution_logs>.
"""
import argparse
import csv
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
EXEC_DIR = os.environ.get("BACKFILL_EXEC_DIR", os.path.join(WC_ROOT, "data", "execution_logs"))
EMAIL_CSV = os.path.join(HERE, "..", "aria_F_20260913", "emails",
                         "khoplenh_10-07-2026_19f4b4977cc2786e.csv")
ACCOUNT, ACCOUNT_NO, DATE = "ZaloPay", "0001743768", "2026-07-10"
OID, TICKER, PARENT, QTY, PRICE = "502431", "VHC", "SELL-VHC-01", 600, 57500
HEADER10 = ["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty", "price",
            "filled_total", "note"]
NOTE = ("backfill=true source=broker_email msg=19f4b4977cc2786e aria-K: ATC khớp sau khi bot tắt "
        "(poll cuối 14:45:05 còn New); dnse_raw không có fill này; giờ khớp email không ghi")


def die(msg):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(2)


def email_vhc():
    tot = at_px = 0
    with open(EMAIL_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["tieu_khoan"] == ACCOUNT_NO and r["ma"] == TICKER and r["loai_lenh"] == "BÁN" \
                    and r["ngay_gd"] == "10/07/2026":
                tot += int(r["khoi_luong"])
                if int(r["gia_khop"]) == PRICE:
                    at_px += int(r["khoi_luong"])
    return tot, at_px


def raw_vhc():
    latest = {}
    with open(os.path.join(EXEC_DIR, f"dnse_raw_{DATE}.jsonl"), encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("kind") != "orders":
                continue
            for o in (rec.get("payload") or {}).get("orders") or []:
                if str(o.get("accountNo")) != ACCOUNT_NO:      # §12 — file dùng chung
                    continue
                latest[str(o.get("id"))] = o
    sold = sum(o.get("fillQuantity") or 0 for o in latest.values()
               if o.get("symbol") == TICKER and str(o.get("side", "")).upper().startswith("NS"))
    return sold, latest.get(OID)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    jpath = os.path.join(EXEC_DIR, f"exec_{ACCOUNT}_{DATE}_journal.csv")
    with open(jpath, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if rows[0] != HEADER10:
        die(f"header journal khác layout 10 cột mong đợi: {rows[0]}")
    recs = [dict(zip(HEADER10, r)) for r in rows[1:]]
    mine = [r for r in recs if r["event"] == "FILL" and r["child_oid"] == OID]
    if any("backfill=true" in r["note"] for r in mine):
        print(f"ℹ️ đã backfill oid {OID} trước đó — không ghi gì. {jpath}")
        return 0
    if mine:
        die(f"journal ĐÃ có FILL thật cho oid {OID}: {mine} — không backfill")

    e_tot, e_px = email_vhc()
    if (e_tot, e_px) != (1800, QTY):
        die(f"email msg 19f4b4977cc2786e: VHC bán {e_tot}cp, @{PRICE:,} {e_px}cp — mong đợi 1800/600")
    r_sold, r_oid = raw_vhc()
    if r_sold != 1200 or not r_oid or r_oid.get("orderType") != "ATC" or (r_oid.get("fillQuantity") or 0):
        die(f"dnse_raw {DATE} {ACCOUNT_NO}: VHC bán fill {r_sold}cp, oid {OID}="
            f"{ {k: (r_oid or {}).get(k) for k in ('orderType', 'orderStatus', 'fillQuantity')} }"
            f" — mong đợi 1200 và ATC/0")
    by_child = {}
    for r in recs:
        if r["event"] == "FILL" and r["ticker"] == TICKER and r["side"] == "sell":
            by_child[r["child_oid"]] = max(by_child.get(r["child_oid"], 0), int(float(r["qty"])))
    j_sold = sum(by_child.values())
    if j_sold != 1200:
        die(f"journal: VHC bán (max qty theo child) = {j_sold}cp — mong đợi 1200")
    atc = [r for r in recs if r["event"] == "ATC" and r["child_oid"] == OID]
    if len(atc) != 1 or atc[0]["qty"] != str(QTY):
        die(f"journal: dòng ATC oid {OID} = {atc} — mong đợi đúng 1 dòng qty {QTY}")

    row = [f"{DATE}T14:45:00", "FILL", PARENT, TICKER, "sell", OID, str(QTY), str(PRICE),
           str(j_sold + QTY), NOTE]
    print(f"Bằng chứng khớp: email {e_tot}cp (600 @{PRICE:,}) · dnse_raw {r_sold}cp · journal {j_sold}cp")
    print("Dòng sẽ nối:", row)
    if not args.apply:
        print("(dry-run — thêm --apply để ghi)")
        return 0
    bak = jpath + ".pre_aria_K"
    if not os.path.exists(bak):
        shutil.copy2(jpath, bak)
    tmp = jpath + ".tmp_aria_K"
    shutil.copy2(jpath, tmp)
    with open(tmp, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)
    os.replace(tmp, jpath)                        # §5 atomic
    print(f"✅ đã nối 1 dòng FILL backfill → {jpath} (bản gốc: {bak})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
