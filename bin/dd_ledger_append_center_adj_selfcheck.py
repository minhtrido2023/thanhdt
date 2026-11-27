#!/usr/bin/env python3
"""Selfcheck dd_ledger_append_center_adj.py — chạy trên BẢN SAO sổ thật trong thư mục tạm (không đụng sổ thật)."""
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import dd_ledger_append_center_adj as t  # noqa: E402

SRC_ADJ = "agents/Taylor/research/dd_adjcenter_20261124/DGC/adj.json"


def main():
    r = []
    with tempfile.TemporaryDirectory() as td:
        led = os.path.join(td, "led.json")
        base = os.path.join(ROOT, "kb", "dd_price_zones.json")
        txt = json.load(open(base, encoding="utf-8"))
        # bản sao sổ chưa có entry center_adj nào (nếu sổ thật đã ghi) để test lặp lại được: cắt CẢ ĐUÔI từng mã
        # từ entry center_adj đầu tiên — bỏ riêng entry đó làm rev đứt quãng khi sau nó còn rev khác (MBB rev5→6)
        cut, keep_ = set(), []
        for e in txt["entries"]:
            if e.get("center_adj") is not None:
                cut.add(e["ticker"])
            if e["ticker"] not in cut:
                keep_.append(e)
        txt["entries"] = keep_
        open(led, "w", encoding="utf-8").write(json.dumps(txt, ensure_ascii=False, indent=1))
        n0 = len(txt["entries"])

        def go(adjs, write=False, ledger=led):
            o, e = io.StringIO(), io.StringIO()
            rc = t.run(ledger, adjs, write, ROOT, out=o, err=e)
            return rc, o.getvalue(), e.getvalue()

        rc, _, _ = go(["DGC=" + SRC_ADJ])
        r.append(("dry-run rc=0", rc == 0))
        r.append(("dry-run không ghi sổ", len(json.load(open(led))["entries"]) == n0))
        rc, _, _ = go(["DGC=" + SRC_ADJ], write=True)
        L = json.load(open(led, encoding="utf-8"))["entries"]
        new, old = L[-1], [e for e in L[:-1] if e["ticker"] == "DGC"][-1]
        r.append(("write rc=0, thêm đúng 1 entry", rc == 0 and len(L) == n0 + 1))
        r.append(("rev+1 + supersedes đúng", new["rev"] == int(old["rev"]) + 1 and new["supersedes"] == "DGC@%s#%s" % (old["dd_date"], old["rev"])))
        keep = ("center", "zone_low", "zone_high", "skeptic_final", "price_ref", "verdict_label", "expires_on", "assumptions_md5", "report_md5")
        r.append(("số/nhãn cũ giữ nguyên", all(new.get(k) == old.get(k) for k in keep)))
        r.append(("center_adj/low/high/basis/md5 có đủ", all(new.get(k) is not None for k in ("center_adj", "center_adj_low", "center_adj_high", "center_adj_basis", "center_adj_md5"))))
        rc, _, err = go(["DGC=" + SRC_ADJ], write=True)
        r.append(("ghi lần 2 (đã có center_adj) bị từ chối", rc == 2 and "ĐÃ có center_adj" in err))
        rc, _, _ = go(["ZZZ=" + SRC_ADJ])
        r.append(("ticker adj.json ≠ mã bị từ chối", rc == 2))
        rc, _, _ = go(["FPT=" + SRC_ADJ])
        r.append(("adj.json của mã khác bị từ chối", rc == 2))
        rc, _, _ = go(["DGC=" + os.path.join(ROOT, SRC_ADJ)])
        r.append(("đường dẫn tuyệt đối bị từ chối", rc == 2))
        rc, _, _ = go(["DGC=../x.json"])
        r.append(("đường dẫn thoát gốc bị từ chối", rc == 2))
        rc, _, _ = go(["DGC=" + SRC_ADJ, "DGC=" + SRC_ADJ])
        r.append(("mã khai 2 lần bị từ chối", rc == 2))
        rc, _, _ = go(["FPT=agents/Taylor/research/dd_adjcenter_20261124/FPT/adj.json", "DRI=agents/Taylor/research/dd_adjcenter_20261124/DRI/adj.json"])
        r.append(("lô 2 mã dry-run qua", rc == 0))
        # adj.json lệch rev / dd_date / thiếu số: bản sao trong tmpdir (root=td) — không đụng cây research thật
        def go_td(mut):
            jj = json.load(open(os.path.join(ROOT, SRC_ADJ), encoding="utf-8"))
            mut(jj)
            rel = "adj_bad.json"
            json.dump(jj, open(os.path.join(td, rel), "w", encoding="utf-8"))
            led2 = os.path.join(td, "led2.json")
            open(led2, "w", encoding="utf-8").write(json.dumps(txt, ensure_ascii=False, indent=1))
            o, e = io.StringIO(), io.StringIO()
            return t.run(led2, ["DGC=" + rel], False, td, out=o, err=e), e.getvalue()
        rc, err = go_td(lambda jj: jj.update(rev=99))
        r.append(("adj.json lệch rev entry cuối bị từ chối", rc == 2 and "rev khác" in err))
        rc, err = go_td(lambda jj: jj.update(dd_date="2026-01-01"))
        r.append(("adj.json lệch dd_date bị từ chối", rc == 2 and "rev khác" in err))
        rc, err = go_td(lambda jj: jj.pop("center_adj"))
        r.append(("adj.json thiếu center_adj bị từ chối", rc == 2 and "center_adj" in err))
        # rc=3: sổ bản sao có entry cũ hỏng (zone_low > zone_high) ⇒ selfcheck bản tạm FAIL ⇒ KHÔNG ghi, sổ nguyên vẹn
        bad_led = os.path.join(td, "led_bad.json")
        bt = json.loads(json.dumps(txt))
        for e_ in bt["entries"]:
            if e_["ticker"] == "DGC":
                e_["zone_low"], e_["zone_high"] = 9e9, 1
        open(bad_led, "w", encoding="utf-8").write(json.dumps(bt, ensure_ascii=False, indent=1))
        before = open(bad_led, "rb").read()
        rc, _, err = go(["DGC=" + SRC_ADJ], write=True, ledger=bad_led)
        r.append(("selfcheck bản tạm FAIL ⇒ rc=3, sổ không đổi", rc == 3 and open(bad_led, "rb").read() == before))
    bad = [n for n, ok in r if not ok]
    for n, ok in r:
        print(("PASS " if ok else "FAIL ") + n)
    print("-- %d ca, lỗi %d" % (len(r), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
