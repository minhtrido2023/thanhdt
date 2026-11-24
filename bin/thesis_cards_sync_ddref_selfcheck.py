#!/usr/bin/env python3
"""Selfcheck thesis_cards_sync_ddref.py — chạy trên BẢN SAO sổ thật trong thư mục tạm. Chạy: env -u TZ ... ; TZ=America/New_York ..."""
import copy
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import thesis_cards as T  # noqa: E402
import thesis_cards_sync_ddref as S  # noqa: E402

fails = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


doc = T.read_json(T.CARDS)
led = T.read_json(T.LEDGER)
with tempfile.TemporaryDirectory() as td:
    lp, cp = os.path.join(td, "led.json"), os.path.join(td, "cards.json")

    def setup(led_mut=None):
        L = copy.deepcopy(led)
        if led_mut:
            led_mut(L["entries"])
        json.dump(L, open(lp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        open(cp, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")

    def go(write=False, tickers=None):
        o, e = io.StringIO(), io.StringIO()
        return S.run(cp, lp, write, tickers, out=o, err=e), o.getvalue(), e.getvalue()

    def add_rev(entries, t="FPT", **kw):
        last = T.latest_ledger(entries)[t]
        n = copy.deepcopy(last)
        n.update(rev=last.get("rev", 1) + 1, supersedes="%s@%s#%s" % (t, last["dd_date"], last.get("rev", 1)))
        n.update(kw)
        entries.append(n)

    setup()
    rc, o, _ = go()
    check("sổ thật đang khớp ⇒ rc=0, không có gì để làm", rc == 0 and "không có thẻ nào cần" in o)
    setup(add_rev)
    rc, o, _ = go()
    check("sổ thêm rev (số giữ) ⇒ dry-run rc=0, báo đồng bộ FPT", rc == 0 and "đồng bộ FPT" in o and "dry-run" in o)
    check("dry-run KHÔNG ghi thẻ", len(T.read_json(cp)["cards"]) == len(doc["cards"]))
    rc, o, _ = go(write=True)
    new = T.read_json(cp)
    nc, oc = T.latest_cards(new)["FPT"], T.latest_cards(doc)["FPT"]
    check("--write thêm đúng 1 thẻ FPT rev+1", rc == 0 and len(new["cards"]) == len(doc["cards"]) + 1 and nc["rev"] == oc["rev"] + 1)
    check("thẻ mới chỉ đổi dd_ref/rev/recorded_at/supersedes_note", all(nc[k] == oc[k] for k in oc if k not in ("rev", "dd_ref", "recorded_at", "supersedes_note")))
    check("dd_ref.rev khớp sổ", nc["dd_ref"]["rev"] == T.latest_ledger(T.read_json(lp)["entries"])["FPT"]["rev"])
    check("thẻ các mã khác không đổi", all(T.latest_cards(new)[t] == T.latest_cards(doc)[t] for t in ("NNC", "VGS")))
    check("sau ghi: validate sạch", not T.validate(new, T.read_json(lp)["entries"], None))
    rc, o, _ = go(write=True)
    check("chạy lại = no-op (idempotent)", rc == 0 and len(T.read_json(cp)["cards"]) == len(new["cards"]))
    # số đổi ⇒ không tự đồng bộ
    for k, v in (("center", 99999), ("zone_low", 1), ("zone_high", 999999)):
        setup(lambda E, k=k, v=v: add_rev(E, **{k: v}))
        rc, o, _ = go(write=True)
        check("sổ đổi %s ⇒ CẦN NGƯỜI XEM, rc=4, không ghi" % k, rc == 4 and "CẦN NGƯỜI XEM FPT" in o and len(T.read_json(cp)["cards"]) == len(doc["cards"]))
    # lẫn: FPT đổi số + NNC chỉ đổi rev ⇒ NNC vẫn đồng bộ, rc=4
    setup(lambda E: (add_rev(E, "FPT", center=99999), add_rev(E, "NNC")))
    rc, o, _ = go(write=True)
    check("lẫn FPT đổi số + NNC chỉ rev ⇒ NNC ghi, FPT báo, rc=4", rc == 4 and T.latest_cards(T.read_json(cp))["NNC"]["rev"] == T.latest_cards(doc)["NNC"]["rev"] + 1
          and T.latest_cards(T.read_json(cp))["FPT"]["rev"] == T.latest_cards(doc)["FPT"]["rev"])
    setup(lambda E: (add_rev(E, "FPT"), add_rev(E, "NNC")))
    rc, o, _ = go(write=True, tickers=["NNC"])
    check("--ticker NNC ⇒ chỉ NNC", rc == 0 and T.latest_cards(T.read_json(cp))["FPT"]["rev"] == T.latest_cards(doc)["FPT"]["rev"]
          and T.latest_cards(T.read_json(cp))["NNC"]["rev"] == T.latest_cards(doc)["NNC"]["rev"] + 1)
    # stale_reason / closed ⇒ bỏ qua
    d2 = copy.deepcopy(doc)
    T.latest_cards(d2)["FPT"]["dd_ref"]["stale_reason"] = "test"
    T.latest_cards(d2)["FPT"]["dd_ref"]["rev"] = 1
    check("thẻ có stale_reason ⇒ plan bỏ qua", not S.plan(d2, led["entries"], {"FPT"})[0] and not S.plan(d2, led["entries"], {"FPT"})[1])
    d3 = copy.deepcopy(doc)
    T.latest_cards(d3)["FPT"]["status"] = "closed"
    T.latest_cards(d3)["FPT"]["dd_ref"]["rev"] = 1
    check("thẻ closed ⇒ plan bỏ qua", not S.plan(d3, led["entries"], {"FPT"})[0])
    # định dạng file lệch ⇒ từ chối; đầu vào hỏng ⇒ rc=2
    setup(add_rev)
    open(cp, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=4))
    rc, _, err = go(write=True)
    check("định dạng lệch ⇒ rc=2, không ghi", rc == 2 and "định dạng" in err)
    open(cp, "w", encoding="utf-8").write("{hỏng")
    rc, _, _ = go()
    check("JSON hỏng ⇒ rc=2", rc == 2)
    # validate bản tạm FAIL ⇒ rc=3, không đổi file: làm thẻ cũ hỏng schema
    setup(add_rev)
    bad = copy.deepcopy(doc)
    T.latest_cards(bad)["NNC"]["deal_type"] = "yolo"
    open(cp, "w", encoding="utf-8").write(json.dumps(bad, ensure_ascii=False, indent=2) + "\n")
    before = open(cp, "rb").read()
    rc, _, err = go(write=True)
    check("validate bản tạm FAIL ⇒ rc=3, file nguyên vẹn", rc == 3 and open(cp, "rb").read() == before)

print("ALL PASS" if not fails else "FAILED: %s" % fails)
sys.exit(1 if fails else 0)
