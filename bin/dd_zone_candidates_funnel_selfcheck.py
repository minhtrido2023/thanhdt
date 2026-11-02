#!/usr/bin/env python3
"""Selfcheck khối "E. Ứng viên sleeve từ sổ DD" của discretionary_candidate_funnel.py (quy tắc 4 user
02/11) + HỢP ĐỒNG producer→consumer: file do dd_price_zone_watch.run() ghi phải được print_block() đọc.

Offline (CSV giá giả, --no-bq, --no-positions). Chạy dưới `env -u TZ` + TZ ngoại lai.
  python3 bin/dd_zone_candidates_funnel_selfcheck.py [--mutants]
"""
import argparse
import contextlib
import datetime as dt
import importlib.util
import io
import json
import os
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FSRC = os.path.join(HERE, "discretionary_candidate_funnel.py")
WSRC = os.path.join(HERE, "dd_price_zone_watch.py")
_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
D = dt.date


def load(path, text, name):
    spec = importlib.util.spec_from_loader(name, loader=None)
    m = importlib.util.module_from_spec(spec)
    m.__file__ = path
    exec(compile(text, path, "exec"), m.__dict__)
    return m


def cases(F, W):
    R = []

    def ok(name, cond):
        R.append((name, bool(cond)))

    today = D(2026, 11, 3)                      # T3 — phiên gần nhất = T2 02/11
    base = {"schema": F.DD_ZONE_SCHEMA, "asof": "2026-11-02", "checked": 3, "total": 3, "excluded": [],
            "candidates": [{"ticker": "AAA", "close": 16000.0, "center": 20000, "pct_center": -20.0,
                            "dd_date": "2026-10-30", "new_alert": True,
                            "warnings": ["⚠ cờ DD QF:FLOOR_FAIL (sleeve discretionary: chỉ cảnh báo)"]}]}
    b = F.format_dd_zone_lines(base, today)
    ok("ứng viên: mã + giá có dấu nghìn + % so tâm + 🆕 + cờ cảnh báo",
       "• AAA 16.000 (-20,0% so tâm 20.000; DD 2026-10-30) 🆕" in b and "QF:FLOOR_FAIL" in b)
    ok("tiêu đề nói rõ 'user duyệt từng lần, KHÔNG tự mua'", "user duyệt từng lần, KHÔNG tự mua" in b)
    ok("file thiếu ⇒ nói rõ không kết luận được", "KHÔNG kết luận được" in F.format_dd_zone_lines(None, today))
    ok("sai schema ⇒ không đọc", "sai schema" in F.format_dd_zone_lines(dict(base, schema="x/v0"), today))
    ok("asof cũ hơn phiên gần nhất ⇒ KẾT QUẢ CŨ", "KẾT QUẢ CŨ" in F.format_dd_zone_lines(dict(base, asof="2026-10-30"), today)
       and "KẾT QUẢ CŨ" not in b)
    ok("0 ứng viên, kiểm đủ ⇒ '0 ứng viên (kiểm được 3/3'",
       "0 ứng viên (kiểm được 3/3 mã)" in F.format_dd_zone_lines(dict(base, candidates=[]), today))
    ok("0 ứng viên, kiểm thiếu ⇒ cảnh báo chưa kết luận",
       "chưa kết luận được" in F.format_dd_zone_lines(dict(base, candidates=[], checked=1), today))
    ok("có ứng viên nhưng kiểm thiếu ⇒ cảnh báo n/m", "chỉ kiểm được 2/3" in F.format_dd_zone_lines(dict(base, checked=2), today))
    ok("mã bị loại nêu ở 'Không xét'", "Không xét: TV1 (đã có quyết định không giữ)" in
       F.format_dd_zone_lines(dict(base, excluded=[{"ticker": "TV1", "why": "đã có quyết định không giữ"}]), today))
    ok("schema 2 phía khớp (producer = consumer)", F.DD_ZONE_SCHEMA == W.CAND_SCHEMA)
    ok("tên file 2 phía khớp", os.path.basename(W.CAND_JSON) == F.DD_ZONE_FILE or "DDZ_CANDIDATES" in os.environ)

    # HỢP ĐỒNG end-to-end: watch.run() ghi → funnel.print_block() đọc (cùng thư mục sandbox)
    with tempfile.TemporaryDirectory() as td:
        lp = os.path.join(td, "l.json")
        e = {"ticker": "AAA", "dd_date": "2026-10-30", "bctc_quarter": "2026Q3", "zone_low": 18000, "center": 20000,
             "zone_high": 24000, "expires_on": "2027-02-27"}
        json.dump({"entries": [e, dict(e, ticker="DRI"), dict(e, ticker="BBB")]}, open(lp, "w"))
        cp = os.path.join(td, "p.csv")
        open(cp, "w").write("ticker,date,close\nAAA,2026-11-02,16000\nDRI,2026-11-02,15000\nBBB,2026-11-02,19900\n")
        a = argparse.Namespace(asof="2026-11-02", ledger=lp, state=os.path.join(td, "s.json"), out_dir=td, price_csv=cp,
                               report_block=True, no_bq=True, no_positions=True, no_state=True,
                               candidates_json=os.path.join(td, F.DD_ZONE_FILE))
        with contextlib.redirect_stdout(io.StringIO()):
            W.run(a, now=dt.datetime(2026, 11, 2, 21, 0, tzinfo=_ICT))
        rp = os.path.join(td, "discretionary_funnel_latest.json")     # thiếu kết quả funnel: khối D báo thiếu
        pb = F.print_block(today, rp)
        ok("e2e: print_block có khối E với AAA, DRI ở 'Không xét', BBB không có",
           "E. Ứng viên sleeve từ sổ DD" in pb and "• AAA 16.000" in pb and "Không xét: DRI" in pb and "• BBB" not in pb)
        ok("e2e: ứng viên mang cảnh báo vị thế chưa kiểm (--no-positions)", "có thể đang giữ" in pb.split("• AAA")[1])
        ok("e2e: khối D vẫn in như cũ (đứng trước khối E)", pb.index("D. Funnel 8L") < pb.index("E. Ứng viên"))
        open(os.path.join(td, F.DD_ZONE_FILE), "w").write("{hỏng")
        ok("file hỏng ⇒ báo HỎNG, không crash", "HỎNG" in F.print_block(today, rp))
        os.remove(os.path.join(td, F.DD_ZONE_FILE))
        ok("file không có ⇒ báo không thấy file", "không thấy file" in F.print_block(today, rp))
    src = open(FSRC, encoding="utf-8").read().split("def format_dd_zone_lines")[1].split("def print_block")[0]
    ok("khối E không ghi plan/không gọi lệnh", not any(k in src for k in ("trade_plans", "place_order", "_atomic_write")))
    return R


MUTANTS = [
    ("F1 bỏ cảnh báo KẾT QUẢ CŨ", "    if asof < prev_trading_day(today):\n        lines.append(f\"⚠️ KẾT QUẢ CŨ",
     "    if False:\n        lines.append(f\"⚠️ KẾT QUẢ CŨ"),
    ("F2 bỏ cờ cảnh báo của ứng viên", "w = f\" · {'; '.join(c['warnings'])}\" if c.get(\"warnings\") else \"\"", "w = \"\""),
    ("F3 0 ứng viên luôn nói 'kiểm đủ'", "if n == m and m else", "if True else"),
    ("F4 bỏ kiểm schema", "if payload.get(\"schema\") != DD_ZONE_SCHEMA:", "if False:"),
    ("F5 bỏ dòng Không xét", "    if payload.get(\"excluded\"):\n", "    if False:\n"),
    ("F6 print_block không nối khối E", "pick_base_dir=base) + \"\\n\" + format_dd_zone_lines(zpay, today)",
     "pick_base_dir=base)"),
    ("F7 file hỏng ⇒ coi như thiếu", "zpay = {\"schema\": f\"HỎNG ({type(e).__name__})\"}", "zpay = None"),
    ("F8 đọc file ở DATA_DIR thật thay vì base", "os.path.join(base, DD_ZONE_FILE)", "os.path.join(DATA_DIR, DD_ZONE_FILE)"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutants", action="store_true")
    a = ap.parse_args()
    ftxt = open(FSRC, encoding="utf-8").read()
    W = load(WSRC, open(WSRC, encoding="utf-8").read(), "ddz_w")
    R = cases(load(FSRC, ftxt, "funnel_f"), W)
    for n, r in R:
        print(("PASS " if r else "FAIL ") + n)
    allok = all(r for _, r in R)
    print(f"-- {sum(r for _, r in R)}/{len(R)} PASS (TZ={os.environ.get('TZ', '<unset>')})")
    if a.mutants:
        killed = 0
        for name, old, new in MUTANTS:
            if ftxt.count(old) != 1:
                print(f"MUTANT-SKIP? '{name}': chuỗi gốc không duy nhất ({ftxt.count(old)})")
                allok = False
                continue
            try:
                dead = not all(r for _, r in cases(load(FSRC, ftxt.replace(old, new), "funnel_mut"), W))
            except Exception:  # noqa: BLE001 — mutant làm vỡ module cũng tính là bị bắt
                dead = True
            killed += dead
            print(("KILLED " if dead else "SURVIVED ") + name)
        print(f"-- mutants killed {killed}/{len(MUTANTS)}")
        allok = allok and killed == len(MUTANTS)
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
