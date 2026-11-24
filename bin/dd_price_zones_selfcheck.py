#!/usr/bin/env python3
"""dd_price_zones_selfcheck.py — mỗi số trong kb/dd_price_zones.json phải khớp NGUYÊN VĂN file nguồn.

Kiểm (không mạng, không BQ/DNSE):
  1. Mỗi evidence.quote là chuỗi con NGUYÊN VĂN của evidence.file (đọc từ MIKE_SRC_ROOT — mặc định
     repo mike canonical, vì thư mục research/ của DD mới có thể chưa commit vào nhánh).
  2. Mỗi field số khai trong evidence.fields xuất hiện như một con số trong quote
     (chấp nhận '47.700', '55,0k', '19,4' (nghìn), '~20k').
  3. Mọi field số khác null (zone_low/center/zone_high/price_ref/center_range) đều được ÍT NHẤT một
     evidence phủ; field null phải có null_reason (trừ price_date).
  4. Bất biến: zone_low ≤ zone_high; center_range[0] == center; append-only key (ticker, dd_date, rev) duy nhất.
  5. center_kind ∈ enum; kind ≠ expected_weighted ⇒ phải có no_expected_reason (luật ưu tiên: giá trị kỳ vọng
     trọng số khi nguồn có); center_alt phải có center_alt_kind + evidence phủ.
  6. Đính chính append-only: rev>1 ⇒ supersedes "TICKER@dd_date#N" trỏ đúng entry rev=N đã có (N=rev−1),
     rev liên tục từ 1; rev≥2 bắt buộc correction_reason.
Dùng: python3 bin/dd_price_zones_selfcheck.py [--ledger PATH]   (rc 0 = PASS)
"""
import argparse
import json
import datetime as dt
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.environ.get("MIKE_SRC_ROOT", "/home/trido/thanhdt/WorkingClaude/mike")
NUM_FIELDS = ("zone_low", "center", "zone_high", "price_ref")
CENTER_KINDS = ("expected_weighted", "base_scenario", "blend", "median", "zone_midpoint", "point")
LOCK_REQUIRED_FROM = "2026-11-08"  # entry ghi từ ngày này BẮT BUỘC có assumptions_md5 (user chốt B, 08/11); cũ được miễn
SKEPTIC_FINAL_REQUIRED_FROM = "2026-11-23"  # entry ghi từ ngày này BẮT BUỘC có skeptic_final + audited_fy_missing (A2, 22/11); cũ được miễn
SKEPTIC_PATH_REQUIRED_FROM = "9999-12-31"  # entry ghi từ ngày này BẮT BUỘC có skeptic_verdict_path → file rN.json do bin/dd_skeptic_run.py ghi (A4; Mike đặt ngày bật SAU khi 2 DD kế tiếp có file)
SKEPTIC_FINAL_ENUM = ("CONFIRMED", "FIXED_UNVERIFIED", "REFUTED_OPEN", "NONE")
_TOK = re.compile(r"\d+(?:[.,]\d+)*")


def quote_numbers(q):
    """Tập giá trị (đồng) mà các token số trong quote có thể biểu diễn: 'a.bcd' = nghìn phân cách;
    'a,b' = thập phân. ×1000 (đơn vị k/nghìn) CHỈ cho token có giá trị < 1000 (19,4 / 55,0 / 20 → 19.400…);
    token ≥1000 (vd '9.950', '2026') không bị nhân thành số lớn vô nghĩa."""
    out = set()
    for t in _TOK.findall(q):
        if "." in t and all(len(g) == 3 for g in t.split(".")[1:]) and "," not in t:
            v = float(t.replace(".", ""))
        else:
            v = float(t.replace(".", "").replace(",", ".")) if t.count(",") == 1 else float(t.replace(",", ""))
        out.add(round(v, 3))
        if v < 1000:
            out.add(round(v * 1000, 3))
    return out


def check(ledger_path, src_root=SRC_ROOT):
    errs = []
    d = json.load(open(ledger_path, encoding="utf-8"))
    seen = set()
    cache = {}
    for i, e in enumerate(d["entries"]):
        tag = f"#{i} {e.get('ticker')} {e.get('dd_date')}"
        rev = int(e.get("rev", 1))
        key = (e["ticker"], e["dd_date"], rev)
        if key in seen:
            errs.append(f"{tag}: trùng khoá (ticker, dd_date, rev) — sổ append-only: DD mới khác ngày; đính chính = rev cao hơn")
        errs += _rev_errs(tag, e, rev, d["entries"][:i])
        seen.add(key)
        ck = e.get("center_kind")
        if e.get("center") is not None:
            if ck not in CENTER_KINDS:
                errs.append(f"{tag}: center_kind={ck!r} ngoài enum {CENTER_KINDS}")
            elif ck != "expected_weighted" and not e.get("no_expected_reason") and not any(
                    x.get("supersedes") == f"{e['ticker']}@{e['dd_date']}#{rev}" for x in d["entries"]):
                errs.append(f"{tag}: center_kind={ck} nhưng thiếu no_expected_reason (luật ưu tiên: kỳ vọng trọng số khi nguồn có)")
        elif ck is not None:
            errs.append(f"{tag}: center=null nhưng center_kind={ck!r}")
        if e.get("center_alt") is not None and e.get("center_alt_kind") not in CENTER_KINDS:
            errs.append(f"{tag}: center_alt thiếu/sai center_alt_kind")
        covered = set()
        for ev in e.get("evidence") or []:
            p = os.path.join(src_root, ev["file"])
            if p not in cache:
                try:
                    cache[p] = open(p, encoding="utf-8").read()
                except OSError as x:
                    cache[p] = None
                    errs.append(f"{tag}: không đọc được nguồn {ev['file']}: {x}")
            txt = cache[p]
            if txt is not None and ev["quote"] not in txt:
                errs.append(f"{tag}: trích dẫn KHÔNG có nguyên văn trong {ev['file']}: {ev['quote'][:80]!r}")
            nums = quote_numbers(ev["quote"])
            for fld in ev.get("fields", []):
                vals = e.get(fld)
                vals = vals if isinstance(vals, list) else [vals]
                for v in vals:
                    if v is None or round(float(v), 3) not in nums:
                        errs.append(f"{tag}: {fld}={v} KHÔNG có trong trích dẫn {ev['quote'][:80]!r}")
                covered.add(fld)
        for fld in NUM_FIELDS + ("center_range", "center_alt"):
            if e.get(fld) is not None and fld not in covered:
                errs.append(f"{tag}: {fld}={e[fld]} không có evidence nào phủ")
        for fld in NUM_FIELDS:
            if e.get(fld) is None and not e.get("null_reason"):
                errs.append(f"{tag}: {fld}=null nhưng thiếu null_reason")
        if e.get("zone_low") is not None and e.get("zone_high") is not None and e["zone_low"] > e["zone_high"]:
            errs.append(f"{tag}: zone_low > zone_high")
        cr = e.get("center_range")
        if cr is not None and (len(cr) != 2 or cr[0] != e.get("center") or cr[0] > cr[1]):
            errs.append(f"{tag}: center_range phải [center, hi] tăng dần")
        errs += _expiry_errs(tag, e)
        errs += _lock_errs(tag, e, src_root)
        errs += _skeptic_final_errs(tag, e, src_root)
        errs += _center_adj_errs(tag, e, src_root)
        errs += _skeptic_path_errs(tag, e, src_root)
        for fld in ("source_file",):
            if not os.path.exists(os.path.join(src_root, e[fld])):
                errs.append(f"{tag}: source_file không tồn tại {e[fld]}")
    return d, errs


def _ict_date(e):
    """Ngày ghi sổ theo ICT (UTC+7). recorded_at thiếu ⇒ dùng dd_date; không parse được / cũng thiếu dd_date ⇒ '9999-12-31'
    (fail-closed: coi là entry mới, phải đủ trường)."""
    ra = e.get("recorded_at")
    if not ra:
        return str(e.get("dd_date") or "9999-12-31")[:10]
    try:
        t = dt.datetime.fromisoformat(str(ra).replace("Z", "+00:00"))
    except ValueError:
        return "9999-12-31"
    if t.tzinfo is None:
        return t.date().isoformat()  # naive = đã là giờ ICT (quy ước sổ)
    return t.astimezone(dt.timezone(dt.timedelta(hours=7))).date().isoformat()


def _lock_errs(tag, e, src_root):
    """Khoá giả định: md5 nguồn phải khớp; entry mới (recorded_at ≥ LOCK_REQUIRED_FROM) bắt buộc có khoá."""
    want = e.get("assumptions_md5")
    if not want:
        if _ict_date(e) >= LOCK_REQUIRED_FROM:
            return [f"{tag}: thiếu assumptions_md5 (entry ghi từ {LOCK_REQUIRED_FROM} bắt buộc khoá giả định)"]
        return []
    try:
        got = hashlib.md5(open(os.path.join(src_root, e.get("assumptions_file") or e["source_file"]), "rb").read()).hexdigest()
    except OSError as x:
        return [f"{tag}: không đọc được nguồn khoá giả định: {x}"]
    return [] if got == want else [f"{tag}: md5 nguồn lệch khoá giả định ({got[:8]}≠{want[:8]}) — nguồn bị sửa sau khi ghi sổ, thêm rev mới"]


SKEPTIC_BASIS_ENUM = ("rule_backfill_20261122", "ambiguous_backfill", "skeptic_run", "user_confirmed")
_RE_NOT_CONFIRMED = re.compile(r"REFUTED|INCONCLUSIVE|CHƯA (?:qua|chạy)", re.I)


def _center_adj_errs(tag, e, src_root):
    """E17 (user 24/11): tâm kỳ vọng điều chỉnh — TUỲ CHỌN, nhưng đã có trường nào thì phải đủ bộ: center_adj (số >0),
    center_adj_basis (adj.json thật, md5 = center_adj_md5, ticker khớp, center_adj khớp) và center_adj_low ≤ center_adj ≤ center_adj_high."""
    keys = ("center_adj", "center_adj_basis", "center_adj_md5", "center_adj_low", "center_adj_high")
    if not any(k in e for k in keys):
        return []
    errs = [f"{tag}: có trường tâm điều chỉnh nhưng thiếu {k}" for k in keys if e.get(k) is None]
    if errs:
        return errs
    ca, lo, hi = e["center_adj"], e["center_adj_low"], e["center_adj_high"]
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in (ca, lo, hi)) or not (0 < lo <= ca <= hi):
        errs.append(f"{tag}: center_adj phải số, 0 < low ≤ adj ≤ high (low={lo!r} adj={ca!r} high={hi!r})")
    if e.get("skeptic_final") == "NONE":
        errs.append(f"{tag}: center_adj nhưng skeptic_final=NONE (tâm điều chỉnh dựng SAU phản biện)")
    pth = os.path.join(src_root, str(e["center_adj_basis"]))
    try:
        raw = open(pth, "rb").read()
    except OSError as x:
        return errs + [f"{tag}: center_adj_basis không đọc được {e['center_adj_basis']}: {x}"]
    if hashlib.md5(raw).hexdigest() != e["center_adj_md5"]:
        errs.append(f"{tag}: center_adj_md5 KHÔNG khớp {e['center_adj_basis']} (file đổi sau khi ghi sổ)")
    try:
        j = json.loads(raw)
    except ValueError as x:
        return errs + [f"{tag}: center_adj_basis không phải JSON: {x}"]
    if j.get("ticker") != e.get("ticker") or abs(float(j.get("center_adj", -1)) - float(ca)) > 0.5:
        errs.append(f"{tag}: adj.json (ticker={j.get('ticker')!r}, center_adj={j.get('center_adj')!r}) không khớp entry")
    return errs


def _skeptic_final_errs(tag, e, src_root):
    """A2: skeptic_final ∈ enum (bắt buộc từ SKEPTIC_FINAL_REQUIRED_FROM; entry cũ chỉ bị kiểm nếu CÓ trường);
    audited_fy_missing phải bool; skeptic_verdict_path null được, khác null thì file phải tồn tại."""
    new = _ict_date(e) >= SKEPTIC_FINAL_REQUIRED_FROM
    errs = []
    if "skeptic_final" in e or new:
        if e.get("skeptic_final") not in SKEPTIC_FINAL_ENUM:
            errs.append(f"{tag}: skeptic_final={e.get('skeptic_final')!r} ngoài enum {SKEPTIC_FINAL_ENUM}"
                        + (f" (entry ghi từ {SKEPTIC_FINAL_REQUIRED_FROM} bắt buộc)" if new else ""))
    if "audited_fy_missing" in e or new:
        if not isinstance(e.get("audited_fy_missing"), bool):
            errs.append(f"{tag}: audited_fy_missing={e.get('audited_fy_missing')!r} phải là bool")
    vp = e.get("skeptic_verdict_path")
    if vp is not None and not os.path.isfile(os.path.join(src_root, str(vp))):
        errs.append(f"{tag}: skeptic_verdict_path không tồn tại {vp}")
    if "skeptic_final_basis" in e and e["skeptic_final_basis"] not in SKEPTIC_BASIS_ENUM:
        errs.append(f"{tag}: skeptic_final_basis={e['skeptic_final_basis']!r} ngoài enum {SKEPTIC_BASIS_ENUM}")
    # entry mới: nhãn CONFIRMED không được tự khai mâu thuẫn skeptic_status — hoặc có file verdict chứa chữ CONFIRMED
    if new and e.get("skeptic_final") == "CONFIRMED" and _RE_NOT_CONFIRMED.search(e.get("skeptic_status") or ""):
        ok = False
        if vp is not None:
            try:
                ok = "CONFIRMED" in open(os.path.join(src_root, str(vp)), encoding="utf-8", errors="replace").read()
            except OSError:
                ok = False
        if not ok:
            errs.append(f"{tag}: skeptic_final=CONFIRMED mâu thuẫn skeptic_status (có REFUTED/INCONCLUSIVE/CHƯA) và không có skeptic_verdict_path tới file chứa CONFIRMED")
    return errs


def _skeptic_path_errs(tag, e, src_root, required_from=None):
    """A4: entry ghi từ SKEPTIC_PATH_REQUIRED_FROM (ICT) bắt buộc skeptic_verdict_path ≠ null, file tồn tại, JSON hợp lệ,
    verdict ∈ enum, và skeptic_final==CONFIRMED ⇔ verdict==CONFIRMED."""
    if _ict_date(e) < (required_from or SKEPTIC_PATH_REQUIRED_FROM):
        return []
    vp = e.get("skeptic_verdict_path")
    if vp is None:
        return [f"{tag}: skeptic_verdict_path=null — entry ghi từ {required_from or SKEPTIC_PATH_REQUIRED_FROM} bắt buộc có file verdict (chạy bin/dd_skeptic_run.py)"]
    fp = os.path.join(src_root, str(vp))
    if not os.path.isfile(fp):
        return []  # _skeptic_final_errs đã báo "không tồn tại"
    try:
        with open(fp, encoding="utf-8") as f:
            v = json.load(f).get("verdict")
    except (OSError, ValueError, AttributeError) as ex:
        return [f"{tag}: skeptic_verdict_path {vp} không phải JSON hợp lệ ({ex})"]
    if v not in ("CONFIRMED", "REFUTED", "INCONCLUSIVE"):
        return [f"{tag}: verdict={v!r} trong {vp} ngoài enum CONFIRMED/REFUTED/INCONCLUSIVE"]
    if (e.get("skeptic_final") == "CONFIRMED") != (v == "CONFIRMED"):
        return [f"{tag}: skeptic_final={e.get('skeptic_final')!r} không khớp verdict={v} trong {vp}"]
    return []


def _expiry_errs(tag, e):
    """expires_on BẮT BUỘC là chuỗi ngày ISO hợp lệ — dd_price_zone_watch.expiry_of() đọc thẳng trường này;
    null ⇒ TypeError ⇒ cả lượt làm mới ứng viên sleeve chết (sự cố 16–19/11/2026, 11 entry null)."""
    v = e.get("expires_on")
    if not isinstance(v, str):
        return [f"{tag}: expires_on={v!r} phải là chuỗi ngày YYYY-MM-DD (null làm sập dd_price_zone_watch)"]
    try:
        dt.date.fromisoformat(v)
    except ValueError:
        return [f"{tag}: expires_on={v!r} không phải ngày ISO hợp lệ"]
    return []


def _rev_errs(tag, e, rev, prior):
    """Luật đính chính append-only (rev/supersedes)."""
    errs = []
    have = {int(x.get("rev", 1)) for x in prior if (x["ticker"], x["dd_date"]) == (e["ticker"], e["dd_date"])}
    if rev == 1:
        if e.get("supersedes"):
            errs.append(f"{tag}: rev=1 không được có supersedes")
        return errs
    want = f"{e['ticker']}@{e['dd_date']}#{rev - 1}"
    if e.get("supersedes") != want:
        errs.append(f"{tag}: rev={rev} cần supersedes={want!r}, có {e.get('supersedes')!r}")
    if (rev - 1) not in have:
        errs.append(f"{tag}: rev={rev} nhưng chưa có rev={rev - 1} đứng trước trong sổ (rev phải liên tục, ghi sau)")
    if not e.get("correction_reason"):
        errs.append(f"{tag}: rev={rev} thiếu correction_reason")
    return errs


def _self_tests():
    """Mutation nhỏ trên chính bộ so số: số sai 1 chữ số phải bị bắt."""
    r = []
    q = "nằm TRONG vùng ≈7.600–13.000 đ, tâm ≈9.950–10.250 đ; FV ≈ 19,4–21,2k; ~20k; **55,0–66,7k**"
    n = quote_numbers(q)
    r.append(("số chuẩn có mặt", all(x in n for x in (7600, 13000, 9950, 10250, 19400, 21200, 20000, 55000, 66700))))
    r.append(("số lệch bị bắt (7.700/9.960/19.500)", not any(x in n for x in (7700, 9960, 19500))))
    # rev / supersedes / enum — mutation nhỏ trên sổ giả
    base = {"ticker": "AAA", "dd_date": "2026-01-01"}
    r1 = dict(base, rev=1)
    r.append(("rev=2 hợp lệ", not _rev_errs("t", dict(base, rev=2, supersedes="AAA@2026-01-01#1", correction_reason="x"), 2, [r1])))
    r.append(("rev=2 thiếu supersedes bị bắt", bool(_rev_errs("t", dict(base, rev=2, correction_reason="x"), 2, [r1]))))
    r.append(("rev=2 supersedes sai bị bắt", bool(_rev_errs("t", dict(base, rev=2, supersedes="AAA@2026-01-01#2", correction_reason="x"), 2, [r1]))))
    r.append(("rev=3 nhảy cóc bị bắt", bool(_rev_errs("t", dict(base, rev=3, supersedes="AAA@2026-01-01#2", correction_reason="x"), 3, [r1]))))
    r.append(("rev=2 thiếu correction_reason bị bắt", bool(_rev_errs("t", dict(base, rev=2, supersedes="AAA@2026-01-01#1"), 2, [r1]))))
    r.append(("quote_numbers: token ≥1000 không bị ×1000", 9950000 not in quote_numbers("tâm 9.950") and 9950 in quote_numbers("tâm 9.950")))
    r.append(("expires_on hợp lệ → sạch", not _expiry_errs("t", {"expires_on": "2027-03-19"})))
    r.append(("expires_on null bị bắt", bool(_expiry_errs("t", {"expires_on": None}))))
    r.append(("expires_on thiếu bị bắt", bool(_expiry_errs("t", {}))))
    r.append(("expires_on sai định dạng bị bắt", bool(_expiry_errs("t", {"expires_on": "19/03/2027"}))))
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        open(os.path.join(td, "s.md"), "w").write("giả định A")
        m = hashlib.md5(b"gi\xe1\xba\xa3 \xc4\x91\xe1\xbb\x8bnh A").hexdigest()
        ok_e = {"ticker": "AAA", "source_file": "s.md", "assumptions_md5": m, "recorded_at": "2026-11-09T00:00:00+07:00"}
        r.append(("khoá khớp → sạch", not _lock_errs("t", ok_e, td)))
        r.append(("khoá lệch bị bắt", bool(_lock_errs("t", dict(ok_e, assumptions_md5="0" * 32), td))))
        open(os.path.join(td, "s.md"), "w").write("giả định B")
        r.append(("nguồn bị sửa sau ghi sổ bị bắt", bool(_lock_errs("t", ok_e, td))))
        nolock = {k: v for k, v in ok_e.items() if k != "assumptions_md5"}
        r.append(("entry mới thiếu khoá bị bắt", bool(_lock_errs("t", nolock, td))))
        r.append(("entry cũ (trước 08/11) thiếu khoá được miễn", not _lock_errs("t", dict(nolock, recorded_at="2026-11-02T00:00:00+07:00"), td)))
    # E17: tâm kỳ vọng điều chỉnh — đủ bộ, md5 khớp adj.json, ticker/center_adj khớp, low ≤ adj ≤ high
    with tempfile.TemporaryDirectory() as td2:
        aj = json.dumps({"ticker": "AAA", "center_adj": 19000.0}).encode()
        open(os.path.join(td2, "adj.json"), "wb").write(aj)
        ca_e = {"ticker": "AAA", "skeptic_final": "REFUTED_OPEN", "center_adj": 19000.0, "center_adj_low": 18000.0,
                "center_adj_high": 21000.0, "center_adj_basis": "adj.json", "center_adj_md5": hashlib.md5(aj).hexdigest()}
        r.append(("center_adj: bộ đủ → sạch", not _center_adj_errs("t", ca_e, td2)))
        r.append(("center_adj: không có trường nào → bỏ qua", not _center_adj_errs("t", {"ticker": "AAA"}, td2)))
        r.append(("center_adj: thiếu 1 trường bị bắt", bool(_center_adj_errs("t", {k: v for k, v in ca_e.items() if k != "center_adj_md5"}, td2))))
        r.append(("center_adj: md5 lệch bị bắt", bool(_center_adj_errs("t", dict(ca_e, center_adj_md5="0" * 32), td2))))
        r.append(("center_adj: file adj.json mất bị bắt", bool(_center_adj_errs("t", dict(ca_e, center_adj_basis="nope.json"), td2))))
        r.append(("center_adj: ticker lệch bị bắt", bool(_center_adj_errs("t", dict(ca_e, ticker="BBB"), td2))))
        r.append(("center_adj: giá trị lệch adj.json bị bắt", bool(_center_adj_errs("t", dict(ca_e, center_adj=19500.0, center_adj_high=21000.0), td2))))
        r.append(("center_adj: adj ngoài [low,high] bị bắt", bool(_center_adj_errs("t", dict(ca_e, center_adj_high=18500.0), td2))))
        r.append(("center_adj: bool bị bắt", bool(_center_adj_errs("t", dict(ca_e, center_adj=True), td2))))
        r.append(("center_adj: skeptic_final=NONE bị bắt", bool(_center_adj_errs("t", dict(ca_e, skeptic_final="NONE"), td2))))
    ne = {"ticker": "AAA", "recorded_at": "2026-11-23T09:00:00+07:00", "skeptic_final": "NONE", "audited_fy_missing": False}
    r.append(("skeptic_final: entry mới đủ trường → sạch", not _skeptic_final_errs("t", ne, SRC_ROOT)))
    r.append(("skeptic_final: entry mới thiếu skeptic_final bị bắt", bool(_skeptic_final_errs("t", {k: v for k, v in ne.items() if k != "skeptic_final"}, SRC_ROOT))))
    r.append(("skeptic_final: enum sai bị bắt", bool(_skeptic_final_errs("t", dict(ne, skeptic_final="DONE"), SRC_ROOT))))
    old = {"ticker": "AAA", "recorded_at": "2026-11-20T09:00:00+07:00"}
    nr = {k: v for k, v in ne.items() if k != "recorded_at"}
    r.append(("skeptic_final: thiếu recorded_at, dd_date ≥23/11 ⇒ bị bắt", bool(_skeptic_final_errs("t", dict({k: v for k, v in nr.items() if k != "skeptic_final"}, dd_date="2026-11-23"), SRC_ROOT))))
    r.append(("skeptic_final: thiếu recorded_at + thiếu dd_date ⇒ fail-closed bị bắt", bool(_skeptic_final_errs("t", {"ticker": "AAA"}, SRC_ROOT))))
    r.append(("skeptic_final: thiếu recorded_at, dd_date 18/11 (DBC/POW/LLM) được miễn", not _skeptic_final_errs("t", {"ticker": "AAA", "dd_date": "2026-11-18"}, SRC_ROOT)))
    bad = {"ticker": "AAA", "recorded_at": "2026-11-23T09:00:00+07:00", "skeptic_final": "CONFIRMED", "audited_fy_missing": False, "skeptic_status": "vòng 1 REFUTED; chưa chạy lại"}
    r.append(("skeptic_final: CONFIRMED mâu thuẫn skeptic_status (entry mới) bị bắt", bool(_skeptic_final_errs("t", bad, SRC_ROOT))))
    r.append(("skeptic_final: CONFIRMED khớp skeptic_status sạch (entry mới) qua", not _skeptic_final_errs("t", dict(bad, skeptic_status="vòng 2 CONFIRMED (medium)"), SRC_ROOT)))
    r.append(("skeptic_final_basis ngoài enum bị bắt", bool(_skeptic_final_errs("t", {"ticker": "AAA", "recorded_at": "2026-11-20T09:00:00+07:00", "skeptic_final": "NONE", "skeptic_final_basis": "tự_bịa"}, SRC_ROOT))))
    utc = {"ticker": "AAA", "recorded_at": "2026-11-22T18:00:00Z"}  # = 23/11 01:00 ICT
    r.append(("skeptic_final: recorded_at UTC sang ngày 23 ICT bị bắt", bool(_skeptic_final_errs("t", utc, SRC_ROOT))))
    r.append(("skeptic_final: recorded_at UTC 22/11 16:59Z (=23:59 ICT 22/11) được miễn", not _skeptic_final_errs("t", dict(utc, recorded_at="2026-11-22T16:59:00Z"), SRC_ROOT)))
    r.append(("lock: recorded_at UTC sang ngày ≥08/11 ICT thiếu khoá bị bắt", bool(_lock_errs("t", {"ticker": "A", "source_file": "x", "recorded_at": "2026-11-07T18:00:00Z"}, SRC_ROOT))))
    r.append(("skeptic_final: entry cũ thiếu trường được miễn", not _skeptic_final_errs("t", old, SRC_ROOT)))
    r.append(("skeptic_final: entry cũ có enum sai vẫn bị bắt", bool(_skeptic_final_errs("t", dict(old, skeptic_final="X"), SRC_ROOT))))
    r.append(("audited_fy_missing không phải bool bị bắt", bool(_skeptic_final_errs("t", dict(ne, audited_fy_missing="false"), SRC_ROOT))))
    r.append(("skeptic_verdict_path null được phép", not _skeptic_final_errs("t", dict(ne, skeptic_verdict_path=None), SRC_ROOT)))
    r.append(("skeptic_verdict_path trỏ THƯ MỤC bị bắt", bool(_skeptic_final_errs("t", dict(ne, skeptic_verdict_path="agents"), SRC_ROOT))))
    r.append(("skeptic_verdict_path trỏ file không tồn tại bị bắt", bool(_skeptic_final_errs("t", dict(ne, skeptic_verdict_path="no/such/SKEPTIC.md"), SRC_ROOT))))
    # A4: cổng skeptic_verdict_path (đặt ngày bật thấp để test đột biến)
    with tempfile.TemporaryDirectory() as td2:
        def _w(name, obj):
            with open(os.path.join(td2, name), "w", encoding="utf-8") as f:
                f.write(obj if isinstance(obj, str) else json.dumps(obj))
        _w("ok.json", {"verdict": "CONFIRMED"}); _w("ref.json", {"verdict": "REFUTED"})
        _w("bad.json", "{not json"); _w("enum.json", {"verdict": "MAYBE"})
        pe = {"ticker": "AAA", "recorded_at": "2026-11-23T09:00:00+07:00", "skeptic_final": "CONFIRMED", "skeptic_verdict_path": "ok.json"}
        F = "2026-11-01"
        r.append(("A4: entry mới, path hợp lệ + CONFIRMED khớp ⇒ sạch", not _skeptic_path_errs("t", pe, td2, F)))
        r.append(("A4: entry mới path=null bị bắt", bool(_skeptic_path_errs("t", dict(pe, skeptic_verdict_path=None), td2, F))))
        r.append(("A4: JSON hỏng bị bắt", bool(_skeptic_path_errs("t", dict(pe, skeptic_verdict_path="bad.json"), td2, F))))
        r.append(("A4: verdict ngoài enum bị bắt", bool(_skeptic_path_errs("t", dict(pe, skeptic_verdict_path="enum.json"), td2, F))))
        r.append(("A4: skeptic_final=CONFIRMED nhưng verdict REFUTED bị bắt", bool(_skeptic_path_errs("t", dict(pe, skeptic_verdict_path="ref.json"), td2, F))))
        r.append(("A4: verdict CONFIRMED nhưng skeptic_final=NONE bị bắt", bool(_skeptic_path_errs("t", dict(pe, skeptic_final="NONE"), td2, F))))
        r.append(("A4: REFUTED + skeptic_final=REFUTED_OPEN sạch", not _skeptic_path_errs("t", dict(pe, skeptic_final="REFUTED_OPEN", skeptic_verdict_path="ref.json"), td2, F)))
        r.append(("A4: entry cũ (trước ngày bật) path=null được miễn", not _skeptic_path_errs("t", dict(pe, recorded_at="2026-10-30T09:00:00+07:00", skeptic_verdict_path=None), td2, F)))
        r.append(("A4: mặc định 9999-12-31 ⇒ chưa bật, path=null qua", not _skeptic_path_errs("t", dict(pe, skeptic_verdict_path=None), td2)))
    return r


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=os.path.join(os.path.dirname(HERE), "kb", "dd_price_zones.json"))
    a = ap.parse_args()
    ok = True
    for name, res in _self_tests():
        print(("PASS " if res else "FAIL ") + name)
        ok &= res
    d, errs = check(a.ledger)
    for x in errs:
        print("FAIL " + x)
    n = len(d["entries"])
    print(f"-- sổ {n} entry / {len({e['ticker'] for e in d['entries']})} mã; lỗi {len(errs)}")
    sys.exit(0 if ok and not errs else 1)
