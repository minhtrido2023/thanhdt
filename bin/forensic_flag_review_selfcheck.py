#!/usr/bin/env python3
"""forensic_flag_review_selfcheck.py — selfcheck cho bin/forensic_flag_review_check.py.

Chạy trên CSV giả trong thư mục tạm (không đụng data/forensic_flags.csv thật) + bus giả.
Kiểm 3 nhánh thời gian, nhánh đóng-bằng-bus-event, nhánh dữ liệu hỏng, và §16 TZ.

    python3 bin/forensic_flag_review_selfcheck.py
    env -u TZ TZ=America/New_York python3 bin/forensic_flag_review_selfcheck.py   # §16/§19
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "forensic_flag_review_check.py")
WC_ROOT = os.path.dirname(os.path.dirname(HERE))

HDR = "ticker,flag_type,severity,date,source,note,review_by\n"
ROWS = [
    "AAA,related_party,exclude,2026-06-20,t,n,2027-06-20\n",
    "BBB,pump_no_moat,watch,2026-06-20,t,n,2027-06-20\n",
    "CCC,fraud_confirmed,exclude,2026-01-10,t,n,2027-01-10\n",
]

_pass = _fail = 0


def check(name, cond, detail=""):
    global _pass, _fail
    if cond:
        _pass += 1
        print(f"  PASS  {name}")
    else:
        _fail += 1
        print(f"  FAIL  {name}  {detail}")


def run(csv_path, today, bus_dir=None, json_out=None):
    """Chạy target với BUS_DIR ghi đè (bus giả) — không đụng bus thật."""
    src = open(TARGET, encoding="utf-8").read()
    if bus_dir:
        src = src.replace('BUS_DIR = os.path.join(MIKE_ROOT, "bus")', f"BUS_DIR = {bus_dir!r}")
    tmp = os.path.join(tempfile.mkdtemp(), "t.py")
    open(tmp, "w", encoding="utf-8").write(src)
    cmd = [sys.executable, tmp, "--csv", csv_path, "--today", today]
    if json_out:
        cmd += ["--json", json_out]
    r = subprocess.run(
        cmd, capture_output=True, text=True, env={**os.environ, "WC_ROOT": WC_ROOT}
    )
    return r.returncode, r.stdout


def main():
    d = tempfile.mkdtemp()
    csv_ok = os.path.join(d, "ok.csv")
    open(csv_ok, "w", encoding="utf-8").write(HDR + "".join(ROWS))

    # 1. Còn xa hạn → không cảnh báo
    rc, out = run(csv_ok, "2026-09-04")
    check("còn xa hạn → exit 0 + dòng ✅", rc == 0 and "✅" in out, f"rc={rc} out={out!r}")

    # 2. Sắp tới hạn (≤14d) → FYI, KHÔNG phải overdue, vẫn exit 0.
    #    Dùng CSV chỉ gồm AAA/BBB: ở mốc 2027-06-10 thì CCC (hạn 2027-01-10) ĐÃ quá hạn thật,
    #    nên trộn nó vào đây sẽ kiểm nhầm 2 nhánh cùng lúc.
    csv_soon = os.path.join(d, "soon.csv")
    open(csv_soon, "w", encoding="utf-8").write(HDR + ROWS[0] + ROWS[1])
    rc, out = run(csv_soon, "2027-06-10")
    check("sắp hạn → FYI, exit 0", rc == 0 and "sắp tới hạn" in out and "QUÁ HẠN" not in out,
          f"rc={rc} out={out!r}")

    # 3. Quá hạn, chưa ai đóng → exit 1 + fail-closed
    rc, out = run(csv_ok, "2027-07-01")
    check("quá hạn → exit 1", rc == 1 and "QUÁ HẠN" in out, f"rc={rc} out={out!r}")
    check("quá hạn → nói rõ FAIL-CLOSED (không tự gỡ)", "không tự gỡ" in out, out[:200])

    # 4. CCC quá hạn SỚM HƠN (2027-01-10) → chỉ mình nó bị nêu ở mốc 2027-02-01
    rc, out = run(csv_ok, "2027-02-01")
    check("chỉ mã đã quá hạn bị nêu", rc == 1 and "CCC" in out and "AAA" not in out,
          f"rc={rc} out={out!r}")

    # 5. Có bus event đóng → mã đó RỜI danh sách quá hạn (nhánh dễ hỏng nhất: has-event-prefix
    #    báo qua EXIT CODE, không phải stdout — bản nháp đầu sai đúng chỗ này).
    bus = os.path.join(d, "bus")
    os.makedirs(os.path.join(bus, "inbox"))
    with open(os.path.join(bus, "inbox", "Mike.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": "2027-01-20T03:00:00Z", "agent": "Mike", "event_type": "decision",
            "topic": "forensic-flag-review: CCC — giu exclude", "payload": {},
        }) + "\n")
    rc, out = run(csv_ok, "2027-02-01", bus_dir=bus)
    check("bus event đóng → mã rời danh sách quá hạn", rc == 0 and "CCC" not in out,
          f"rc={rc} out={out!r}")

    # 6. Thiếu review_by → nêu ra, KHÔNG im lặng bỏ qua
    csv_missing = os.path.join(d, "missing.csv")
    open(csv_missing, "w", encoding="utf-8").write(HDR + "DDD,x,exclude,2026-06-20,t,n,\n")
    rc, out = run(csv_missing, "2026-09-04")
    check("thiếu review_by → cảnh báo + exit 1", rc == 1 and "thiếu/hỏng" in out and "DDD" in out,
          f"rc={rc} out={out!r}")

    # 7. review_by hỏng định dạng → cùng nhánh 'thiếu/hỏng', không crash
    csv_bad = os.path.join(d, "bad.csv")
    open(csv_bad, "w", encoding="utf-8").write(HDR + "EEE,x,exclude,2026-06-20,t,n,20/06/2027\n")
    rc, out = run(csv_bad, "2026-09-04")
    check("review_by hỏng định dạng → không crash, báo rõ", rc == 1 and "EEE" in out,
          f"rc={rc} out={out!r}")

    # 8. Thiếu FILE → KHÔNG được kết luận "không có cờ nào"
    rc, out = run(os.path.join(d, "khong-ton-tai.csv"), "2026-09-04")
    check("thiếu file → exit 1 + nói không kết luận được",
          rc == 1 and "không kết luận được" in out, f"rc={rc} out={out!r}")

    # 9. --json phản ánh đúng nội dung
    jout = os.path.join(d, "o.json")
    rc, _ = run(csv_ok, "2027-07-01", json_out=jout)
    data = json.load(open(jout, encoding="utf-8"))
    check("--json: 3 mã quá hạn, total=3",
          len(data["overdue"]) == 3 and data["total"] == 3, json.dumps(data)[:200])

    # 10. §16 — kết quả KHÔNG phụ thuộc TZ của tiến trình gọi (mốc sát nửa đêm ICT)
    src = open(TARGET, encoding="utf-8").read()
    check("§16: neo ZoneInfo('Asia/Ho_Chi_Minh'), không dùng datetime.now() trần",
          'ZoneInfo("Asia/Ho_Chi_Minh")' in src and "datetime.now(_ICT)" in src)

    # ---- GỠ SỚM (user chốt 2026-09-04) ----
    # 11. Event đóng ghi TRƯỚC hạn → mã rời hàng đợi ngay, không nằm trong "sắp tới hạn"
    bus2 = os.path.join(d, "bus2")
    os.makedirs(os.path.join(bus2, "inbox"))
    with open(os.path.join(bus2, "inbox", "Taylor.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": "2027-06-01T02:00:00Z", "agent": "Taylor", "event_type": "finding",
            "topic": "forensic-flag-review: AAA — da go, CFO duong 4 quy lien tiep",
            "payload": {},
        }) + "\n")
    rc, out = run(csv_soon, "2027-06-10", bus_dir=bus2)
    check("gỡ sớm: mã đã xử lý trước hạn rời hàng đợi",
          rc == 0 and "đã xử lý TRƯỚC hạn" in out and "AAA" in out.split("↩️")[-1],
          f"rc={rc} out={out!r}")
    check("gỡ sớm: mã CHƯA xử lý vẫn nằm trong FYI sắp hạn",
          "sắp tới hạn" in out and "BBB" in out, out[:250])

    # 12. Event đóng CŨ HƠN ngày gắn cờ → KHÔNG được tính (nói về lần flag trước đó)
    bus3 = os.path.join(d, "bus3")
    os.makedirs(os.path.join(bus3, "inbox"))
    with open(os.path.join(bus3, "inbox", "Mike.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": "2026-01-01T00:00:00Z", "agent": "Mike", "event_type": "decision",
            "topic": "forensic-flag-review: AAA — lan flag cu", "payload": {},
        }) + "\n")
    rc, out = run(csv_soon, "2027-06-10", bus_dir=bus3)
    check("event cũ hơn ngày gắn cờ KHÔNG đóng được cờ hiện tại",
          rc == 0 and "đã xử lý TRƯỚC hạn" not in out and "AAA" in out,
          f"rc={rc} out={out!r}")

    # 13. Đọc được event trong ARCHIVE .jsonl.gz (bỏ sót archive = báo sai "chưa xử lý")
    import gzip as _gz
    bus4 = os.path.join(d, "bus4")
    os.makedirs(os.path.join(bus4, "inbox", "archive"))
    with _gz.open(os.path.join(bus4, "inbox", "archive", "Mike_2027-06.jsonl.gz"),
                  "wt", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": "2027-06-02T00:00:00Z", "agent": "Mike", "event_type": "decision",
            "topic": "forensic-flag-review: AAA — go, da sach", "payload": {},
        }) + "\n")
    rc, out = run(csv_soon, "2027-06-10", bus_dir=bus4)
    check("đọc được event trong archive .jsonl.gz",
          "đã xử lý TRƯỚC hạn" in out, f"rc={rc} out={out!r}")

    # 14. Giãn nhóm: 3 mốc khác nhau → mỗi mốc tới hạn riêng, không nổ cùng lúc
    csv_stag = os.path.join(d, "stagger.csv")
    open(csv_stag, "w", encoding="utf-8").write(
        HDR
        + "G1,related_party,exclude,2026-06-20,t,n,2027-06-06\n"
        + "G2,pump_no_moat,exclude,2026-06-20,t,n,2027-06-13\n"
        + "G3,distress_cashburn,watch,2026-06-20,t,n,2027-06-20\n"
    )
    rc, out = run(csv_stag, "2027-06-07")
    check("giãn nhóm: ở 2027-06-07 chỉ G1 quá hạn, G2/G3 chưa",
          rc == 1 and "G1(exclude" in out and "G2(exclude" not in out
          and "G3(watch" not in out, f"rc={rc} out={out!r}")

    print(f"\n{_pass} PASS, {_fail} FAIL")
    return 1 if _fail else 0


if __name__ == "__main__":
    sys.exit(main())
