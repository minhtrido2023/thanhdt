#!/usr/bin/env python3
"""dd_ledger_append_center_adj — E17 (user duyệt 24/11/2026 19:10): THÊM entry rev+1 gắn tâm kỳ vọng điều chỉnh vào kb/dd_price_zones.json.
Mọi số/nhãn cũ GIỮ NGUYÊN (kể cả skeptic_final); chỉ thêm center_adj, center_adj_low/high, center_adj_basis (đường dẫn TƯƠNG ĐỐI từ
gốc mike tới adj.json), center_adj_md5, + rev/supersedes/correction_reason/recorded_at. Tâm adj KHÔNG thay tâm base (luật 0,85×tâm/luật 4).

  python3 bin/dd_ledger_append_center_adj.py --adj FPT=agents/Taylor/research/dd_adjcenter_20261124/FPT/adj.json [--adj ...] [--write]

Mặc định dry-run. Từ chối (rc=2) nếu: adj.json không đọc được / ticker lệch / dd_date,rev ≠ entry cuối của mã / mã không có trong sổ /
entry cuối ĐÃ có center_adj / thiếu center_base|center_adj|range_low|range_high. rc=3 nếu selfcheck sổ bản tạm FAIL (cả lô không ghi).
Ghi 1 lần cho cả lô (os.replace nguyên tử), diff chỉ là dòng thêm (cùng cơ chế dd_ledger_append_confirmed).
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
from dd_ledger_append_confirmed import latest, render  # noqa: E402


def build_entry(last, adj, rel, md5, now):
    e = copy.deepcopy(last)
    rev = int(last.get("rev", 1))
    e["rev"] = rev + 1
    e["supersedes"] = "%s@%s#%d" % (last["ticker"], last["dd_date"], rev)
    e["correction_reason"] = ("thêm tâm kỳ vọng điều chỉnh E17 (user duyệt 24/11/2026 19:10): %s đ/cp, dải %s–%s; tâm base/vùng/nhãn/skeptic_final "
                              "GIỮ NGUYÊN, tâm adj KHÔNG thay tâm base trong luật 0,85×tâm/luật 4" % (adj["center_adj"], adj["range_low"], adj["range_high"]))
    e["center_adj"] = adj["center_adj"]
    e["center_adj_low"] = adj["range_low"]
    e["center_adj_high"] = adj["range_high"]
    e["center_adj_basis"] = rel
    e["center_adj_md5"] = md5
    e["recorded_at"] = now.isoformat(timespec="seconds")
    return e


def run(ledger, adjs, write, root=ROOT, now=None, out=sys.stdout, err=sys.stderr):
    now = now or dt.datetime.now(ICT)

    def no(msg, rc=2):
        print("TỪ CHỐI: " + msg, file=err)
        return rc

    text = open(ledger, encoding="utf-8").read()
    entries = json.loads(text)["entries"]
    new_entries, seen = [], set()
    for spec in adjs:
        if "=" not in spec:
            return no("--adj phải dạng MÃ=đường_dẫn, nhận %r" % spec)
        tk, rel = spec.split("=", 1)
        tk = tk.strip().upper()
        if tk in seen:
            return no("mã %s khai 2 lần trong cùng lô" % tk)
        seen.add(tk)
        if os.path.isabs(rel):
            return no("%s: đường dẫn adj.json phải TƯƠNG ĐỐI so với gốc mike" % tk)
        pth = os.path.realpath(os.path.join(root, rel))
        if not pth.startswith(os.path.realpath(root) + os.sep):
            return no("%s: đường dẫn thoát khỏi gốc" % tk)
        try:
            raw = open(pth, "rb").read()
            adj = json.loads(raw)
        except (OSError, ValueError) as ex:
            return no("%s: không đọc được %s: %s" % (tk, rel, ex))
        if not isinstance(adj, dict) or adj.get("ticker") != tk:
            return no("%s: adj.json ticker=%r" % (tk, adj.get("ticker") if isinstance(adj, dict) else adj))
        for k in ("center_base", "center_adj", "range_low", "range_high"):
            if not isinstance(adj.get(k), (int, float)) or isinstance(adj.get(k), bool):
                return no("%s: adj.json thiếu/không phải số: %s" % (tk, k))
        last = latest(entries + new_entries, tk)
        if last is None:
            return no("mã %s không có trong sổ" % tk)
        if last.get("center_adj") is not None:
            return no("%s: entry cuối %s@%s#%s ĐÃ có center_adj — không thêm lần nữa" % (tk, last["ticker"], last["dd_date"], last.get("rev", 1)))
        if str(adj.get("dd_date")) != str(last["dd_date"]) or str(adj.get("rev")) != str(last.get("rev", 1)):
            return no("%s: adj.json (dd_date=%s rev=%s) ≠ entry cuối (%s rev %s) — adj dựng trên rev khác" % (
                tk, adj.get("dd_date"), adj.get("rev"), last["dd_date"], last.get("rev", 1)))
        new_entries.append(build_entry(last, adj, rel.replace(os.sep, "/"), hashlib.md5(raw).hexdigest(), now))
    new = text
    for e in new_entries:
        new, why = render(new, e)
        if new is None:
            return no(why)
    import dd_price_zones_selfcheck as sc
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(ledger)), prefix=".tmp_dd_zones_", suffix=".json")
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
        for e in new_entries:
            print("entry thêm: %s@%s rev→%s center_adj=%s [%s–%s] basis=%s" % (
                e["ticker"], e["dd_date"], e["rev"], e["center_adj"], e["center_adj_low"], e["center_adj_high"], e["center_adj_basis"]), file=out)
        if not write:
            print("[dry-run] không ghi; thêm --write để ghi.", file=out)
            return 0
        os.replace(tmp, ledger)
        tmp = None
        print("ĐÃ GHI %s (%d entry)" % (ledger, len(new_entries)), file=out)
        return 0
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--adj", action="append", required=True, help="MÃ=đường_dẫn_adj.json (tương đối gốc mike); lặp được")
    ap.add_argument("--ledger", default=os.path.join(ROOT, "kb", "dd_price_zones.json"))
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--write", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    return run(a.ledger, a.adj, a.write, a.root)


if __name__ == "__main__":
    sys.exit(main())
