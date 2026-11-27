#!/usr/bin/env python3
"""Selfcheck dd_ledger_append_confirmed.py trên BẢN SAO sổ thật (tmp) + verdict giả. Không đụng sổ thật.
Evidence/source_file phân giải từ MIKE_SRC_ROOT (mặc định mike canonical — nơi có research/ chưa commit). Chạy dưới env -u TZ và TZ lạ."""
import datetime as dt, hashlib, io, json, os, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dd_ledger_append_confirmed as m
import dd_price_zones_selfcheck as sc

ROOT = os.environ.get("MIKE_SRC_ROOT", "/home/trido/thanhdt/WorkingClaude/mike")
LEDGER = os.path.join(os.path.dirname(HERE), "kb", "dd_price_zones.json")
NOW = dt.datetime(2026, 11, 24, 10, 0, tzinfo=m.ICT)
res = []


def chk(name, ok):
    res.append(ok)
    print(("PASS " if ok else "FAIL ") + name)


def call(led, vp, t, write=False):
    o, e = io.StringIO(), io.StringIO()
    rc = m.run(led, vp, t, write, root=ROOT, now=NOW, out=o, err=e)
    return rc, o.getvalue(), e.getvalue()


d0 = json.load(open(LEDGER, encoding="utf-8"))
# Sổ sống có lúc KHÔNG còn mã FIXED_UNVERIFIED nào ⇒ dựng fixture từ 1 entry cuối REFUTED_OPEN (đổi nhãn trên bản sao)
pick = next(e for e in reversed(d0["entries"]) if e.get("skeptic_final") in ("FIXED_UNVERIFIED", "REFUTED_OPEN")
            and e.get("center_adj") is None and e.get("source_file") and os.path.isfile(os.path.join(ROOT, e["source_file"]))
            and m.latest(d0["entries"], e["ticker"]) is e)
T = pick["ticker"]
md5 = hashlib.md5(open(os.path.join(ROOT, pick["source_file"]), "rb").read()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    led = os.path.join(td, "z.json")
    shutil.copy(LEDGER, led)
    base = open(led, "rb").read()

    def vf(name, verdict="CONFIRMED", rmd5=md5):
        p = os.path.join(td, name)
        json.dump({"round": 1, "verdict": verdict, "report_md5": rmd5}, open(p, "w"))
        return p

    ok_v = vf("r1.json")
    chk("sổ bản sao qua selfcheck TRƯỚC khi thêm (baseline sạch)", not sc.check(led, ROOT)[1])
    rc, out, err = call(led, ok_v, T)
    chk("dry-run mặc định rc=0, KHÔNG ghi (byte y nguyên)", rc == 0 and "dry-run" in out and open(led, "rb").read() == base)
    for nm, v, t_, why in (("verdict REFUTED", vf("r2.json", "REFUTED"), T, "không phải CONFIRMED"),
                           ("md5 lệch", vf("r3.json", rmd5="0" * 32), T, "md5(source_file)"),
                           ("mã lạ", ok_v, "ZZZ", "không có trong sổ"),
                           ("file verdict không có", os.path.join(td, "nope.json"), T, "không đọc được")):
        rc, out, err = call(led, v, t_, write=True)
        chk("từ chối: %s ⇒ rc=2, lý do thật, sổ y nguyên" % nm, rc == 2 and why in err and open(led, "rb").read() == base)
    rc, out, err = call(led, ok_v, T, write=True)
    new = open(led, "rb").read()
    chk("--write rc=0, không sót file .tmp_", rc == 0 and new != base and not [f for f in os.listdir(td) if f.startswith(".tmp_")])
    chk("diff CHỈ là dòng thêm (không dòng nào bị xoá/sửa ngoài dấu phẩy nối)",
        new.startswith(base[:base.index(m.TAIL.encode())]) and new.endswith(m.TAIL.encode() + base.split(m.TAIL.encode())[1]))
    d1 = json.load(open(led, encoding="utf-8"))
    e1 = d1["entries"][-1]
    chk("entry mới: rev+1, supersedes, CONFIRMED/skeptic_run, số giữ nguyên, recorded_at ICT",
        len(d1["entries"]) == len(d0["entries"]) + 1 and e1["rev"] == int(pick.get("rev", 1)) + 1
        and e1["supersedes"] == "%s@%s#%d" % (T, pick["dd_date"], int(pick.get("rev", 1)))
        and e1["skeptic_final"] == "CONFIRMED" and e1["skeptic_final_basis"] == "skeptic_run"
        and e1["skeptic_verdict_path"] == ok_v and e1["correction_reason"] == "phản biện lại 24/11/2026: CONFIRMED"
        and all(e1[k] == pick[k] for k in ("zone_low", "center", "zone_high", "price_ref", "source_file", "evidence"))
        and e1["recorded_at"] == "2026-11-24T10:00:00+07:00")
    chk("sổ sau khi ghi qua selfcheck đầy đủ", not sc.check(led, ROOT)[1])
    after = open(led, "rb").read()
    rc, out, err = call(led, ok_v, T, write=True)
    chk("chạy lại ⇒ từ chối vì entry cuối đã CONFIRMED, sổ y nguyên", rc == 2 and "đã CONFIRMED" in err and open(led, "rb").read() == after)
    # selfcheck sổ bản tạm FAIL ⇒ rc=3, không ghi: làm hỏng sổ (quote không còn trong nguồn)
    bad = json.loads(base.decode())
    bad["entries"][[i for i, e in enumerate(bad["entries"]) if e is not None and e["ticker"] == T and e["dd_date"] == pick["dd_date"]][-1]]["evidence"][0]["quote"] = "KHÔNG-CÓ-TRONG-NGUỒN-xyz"
    led2 = os.path.join(td, "bad.json")
    open(led2, "w", encoding="utf-8").write(json.dumps(bad, ensure_ascii=False, indent=1))
    b2 = open(led2, "rb").read()
    rc, out, err = call(led2, ok_v, T, write=True)
    chk("selfcheck sổ bản tạm FAIL ⇒ rc=3, KHÔNG ghi", rc == 3 and open(led2, "rb").read() == b2 and not [f for f in os.listdir(td) if f.startswith(".tmp_")])
print("-- %d/%d PASS" % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
