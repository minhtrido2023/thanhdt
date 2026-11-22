#!/usr/bin/env python3
"""dd_ledger_append_confirmed — sau khi bin/dd_skeptic_run.py ghi skeptic/rN.json với verdict CONFIRMED, THÊM 1 entry rev+1
vào kb/dd_price_zones.json (số GIỮ NGUYÊN; chỉ đổi nhãn skeptic). Đây là đường DUY NHẤT để ghi skeptic_final="CONFIRMED" (B2, 22/11).

  python3 bin/dd_ledger_append_confirmed.py --ticker VLB --verdict agents/Taylor/research/dd_VLB_20261122/skeptic/r1.json [--write]

Mặc định --dry-run (in entry sẽ thêm). --write mới ghi (selfcheck sổ trên bản tạm TRƯỚC, rồi os.replace nguyên tử).
Từ chối (rc=2, nói lý do thật) nếu: rN.json không đọc được / verdict ≠ CONFIRMED · mã không có trong sổ · entry cuối ĐÃ CONFIRMED ·
source_file không đọc được · md5(source_file) ≠ report_md5 trong rN.json (báo cáo đã đổi sau lúc phản biện) · selfcheck sổ bản tạm FAIL.
Diff chỉ là dòng thêm: chèn văn bản trước mảng entries kết thúc, KHÔNG dump lại cả file (có kiểm: kết quả == json.dumps toàn bộ).
rc: 0 ok (hoặc dry-run) · 2 từ chối / lỗi đầu vào · 3 selfcheck sổ bản tạm FAIL.
"""
import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICT = dt.timezone(dt.timedelta(hours=7))
sys.path.insert(0, HERE)
TAIL = '\n ],\n "center_kinds"'


def latest(entries, ticker):
    cand = [e for e in entries if e["ticker"].upper() == ticker.upper()]
    return max(cand, key=lambda e: (e["dd_date"], int(e.get("rev", 1)))) if cand else None


def build_entry(last, verdict_rel, now):
    e = copy.deepcopy(last)
    rev = int(last.get("rev", 1))
    day = now.strftime("%d/%m/%Y")
    e["rev"] = rev + 1
    e["supersedes"] = "%s@%s#%d" % (last["ticker"], last["dd_date"], rev)
    e["correction_reason"] = "phản biện lại %s: CONFIRMED" % day
    e["skeptic_final"] = "CONFIRMED"
    e["skeptic_final_basis"] = "skeptic_run"
    e["skeptic_verdict_path"] = verdict_rel
    e["skeptic_status"] = "CONFIRMED (phản biện lại %s, %s); lịch sử: %s" % (day, verdict_rel, last.get("skeptic_status") or "")
    e["recorded_at"] = now.isoformat(timespec="seconds")
    return e


def render(text, entry):
    """Chèn entry vào cuối mảng entries bằng văn bản; trả (text_mới, lỗi)."""
    if text.count(TAIL) != 1:
        return None, "không tìm thấy đúng 1 điểm chèn cuối mảng entries (định dạng sổ đã đổi?)"
    body = json.dumps(entry, ensure_ascii=False, indent=1).replace("\n", "\n  ")
    new = text.replace(TAIL, ",\n  " + body + TAIL)
    want = json.loads(text)
    want["entries"].append(entry)
    if json.dumps(want, ensure_ascii=False, indent=1) != new:
        return None, "chèn văn bản không khớp json.dumps toàn bộ (định dạng sổ lệch)"
    return new, None


def run(ledger, verdict, ticker, write, root=ROOT, now=None, out=sys.stdout, err=sys.stderr):
    now = now or dt.datetime.now(ICT)

    def no(msg, rc=2):
        print("TỪ CHỐI: " + msg, file=err)
        return rc

    vabs = verdict if os.path.isabs(verdict) else os.path.join(root, verdict)
    try:
        v = json.load(open(vabs, encoding="utf-8"))
    except (OSError, ValueError) as ex:
        return no("không đọc được %s: %s" % (vabs, ex))
    if v.get("verdict") != "CONFIRMED":
        return no("verdict trong %s là %r, không phải CONFIRMED" % (verdict, v.get("verdict")))
    text = open(ledger, encoding="utf-8").read()
    last = latest(json.loads(text)["entries"], ticker)
    if last is None:
        return no("mã %s không có trong sổ" % ticker)
    if last.get("skeptic_final") == "CONFIRMED":
        return no("entry cuối %s@%s#%s đã CONFIRMED — không thêm lần nữa" % (last["ticker"], last["dd_date"], last.get("rev", 1)))
    src = last.get("source_file") or ""
    sabs = src if os.path.isabs(src) else os.path.join(root, src)
    try:
        md5 = hashlib.md5(open(sabs, "rb").read()).hexdigest()
    except OSError as ex:
        return no("không đọc được source_file %r của entry cuối: %s" % (src, ex))
    if md5 != v.get("report_md5"):
        return no("md5(source_file)=%s ≠ report_md5 trong %s=%s — báo cáo của entry cuối KHÔNG phải bản skeptic đã đọc" % (md5, verdict, v.get("report_md5")))
    vrel = os.path.relpath(vabs, root) if vabs.startswith(root + os.sep) else vabs
    entry = build_entry(last, vrel, now)
    new, why = render(text, entry)
    if new is None:
        return no(why)
    import dd_price_zones_selfcheck as sc
    d_ = os.path.dirname(os.path.abspath(ledger))
    fd, tmp = tempfile.mkstemp(dir=d_, prefix=".tmp_dd_zones_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new)
            f.flush()
            os.fsync(f.fileno())
        _, errs = sc.check(tmp, root)
        if errs:
            for x in errs[:10]:
                print("selfcheck sổ FAIL: " + x, file=err)
            return no("selfcheck sổ trên bản tạm có %d lỗi — KHÔNG ghi" % len(errs), 3)
        print("entry thêm: %s@%s rev %s→%s, skeptic_final %s→CONFIRMED, verdict=%s" % (
            last["ticker"], last["dd_date"], last.get("rev", 1), entry["rev"], last.get("skeptic_final"), vrel), file=out)
        if not write:
            print("[dry-run] không ghi; thêm --write để ghi.", file=out)
            return 0
        os.replace(tmp, ledger)
        tmp = None
        print("ĐÃ GHI %s" % ledger, file=out)
        return 0
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--verdict", required=True, help="đường dẫn skeptic/rN.json (tương đối so với --root)")
    ap.add_argument("--ledger", default=os.path.join(ROOT, "kb", "dd_price_zones.json"))
    ap.add_argument("--root", default=ROOT, help="gốc để phân giải source_file/verdict (mặc định repo của script)")
    ap.add_argument("--write", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    return run(a.ledger, a.verdict, a.ticker, a.write, a.root)


if __name__ == "__main__":
    sys.exit(main())
