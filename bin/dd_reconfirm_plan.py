#!/usr/bin/env python3
"""dd_reconfirm_plan — CHỈ ĐỌC: lập bảng "mã nào cần phản biện lại / xác nhận cơ học" cho mọi mã trong kb/dd_price_zones.json (B2, 22/11).

  python3 bin/dd_reconfirm_plan.py [--out PLAN.md] [--ledger kb/dd_price_zones.json]

LUẬT (định nghĩa cơ học duy nhất cho khi FIXED_UNVERIFIED được tồn tại):
  Bản "đã được phản biện" = rev mà skeptic THỰC SỰ đọc, suy từ skeptic_status của từng rev theo thứ tự (dd_date, rev):
    · status có CONFIRMED (và không có "CHƯA chạy/qua")  ⇒ skeptic đọc CHÍNH rev đó.
    · status có REFUTED / "sửa theo" / "đã áp" / SKEPTIC_R / "phản biện" ⇒ skeptic đọc rev TRƯỚC đó; rev này là bản đã áp sửa.
    · status mở đầu "CHƯA …" ⇒ rev này chưa ai đọc; đi lùi tiếp.
    Đi lùi từ rev cuối tới khi gặp rev thuộc 2 loại đầu. Không gặp / rev trước không tồn tại / tâm null ⇒ "không xác định" (?).
  skeptic_final=CONFIRMED ⇒ OK.  Δtâm = (tâm rev cuối − tâm rev đã phản biện)/tâm rev đã phản biện.
  Δ>5% HOẶC đổi lớp nhãn (NON/RẺ/DƯỚI/TRONG/TRÊN, suy từ verdict_label) ⇒ FULL (phản biện lại bằng skeptic).
  Δ≤5% và cùng lớp nhãn ⇒ MECH (xác nhận cơ học: tính lại số + checklist đính chính; KHÔNG nâng nhãn; chờ user chốt có chấp nhận CONFIRMED-cơ-học).
  Lớp nhãn không suy được (?) ⇒ "?". CONFIRMED chỉ ghi qua bin/dd_ledger_append_confirmed.py sau bin/dd_skeptic_run.py.
Ưu tiên: P1 = đang giữ (positions trong data/discretionary_exit_rules.json ∪ {FPT,NNC,VGS}) · P2 = giá đóng cửa ngày watch gần nhất
  < zone_low (đọc data/dd_price_zone_watch_state.json, ngày lớn nhất; giá = trường close) · P3 = còn lại.
Env: DD_WC_ROOT (mặc định /home/trido/thanhdt/WorkingClaude) · DDZ_STATE · DD_EXIT_RULES.
"""
import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WC = os.environ.get("DD_WC_ROOT", "/home/trido/thanhdt/WorkingClaude")
EXTRA_HELD = ("FPT", "NNC", "VGS")
DELTA_THR = 0.05
CLASS_ORDER = {"FULL": 0, "?": 1, "MECH": 2, "OK": 3}


def status_kind(s):
    s = s or ""
    if "CONFIRMED" in s and not re.search(r"CHƯA (chạy|qua)", s):
        return "CONFIRMED"
    if re.search(r"REFUTED|sửa theo|đã áp|SKEPTIC_R|phản biện", s):
        return "APPLIED"
    if s.lstrip().startswith("CHƯA") or re.search(r"CHƯA (chạy|qua)", s):
        return "NONE"
    return "NONE"


def label_class(lbl):
    s = lbl or ""
    if re.match(r"\s*NON\b", s):
        return "NON"
    for pat, c in ((r"DƯỚI vùng|DƯỚI dải", "DƯỚI"), (r"TRÊN vùng|ĐẮT|TRÊN dải", "TRÊN"), (r"TRONG vùng|TRONG dải|HỢP LÝ|trung dung — TRONG", "TRONG"),
                   (r"\bRẺ\b", "RẺ"), (r"trung dung — giá DƯỚI", "DƯỚI"), (r"trung dung — giá TRÊN|trung dung — TRÊN", "TRÊN")):
        if re.search(pat, s):
            return c
    m = re.search(r"(dưới|trên|trong)\s+vùng", s, re.I)
    return {"dưới": "DƯỚI", "trên": "TRÊN", "trong": "TRONG"}[m.group(1).lower()] if m else "?"


def reviewed_index(seq):
    """Chỉ số (trong seq đã sắp) của rev skeptic thực sự đọc, hoặc None."""
    for i in range(len(seq) - 1, -1, -1):
        k = status_kind(seq[i].get("skeptic_status"))
        if k == "CONFIRMED":
            return i
        if k == "APPLIED":
            return i - 1 if i >= 1 else None
    return None


def classify(seq):
    last = seq[-1]
    ri = reviewed_index(seq)
    base = {"ticker": last["ticker"], "last": "%s#%s" % (last["dd_date"], last.get("rev", 1)),
            "skeptic_final": last.get("skeptic_final"), "center": last.get("center"), "zone_low": last.get("zone_low")}
    if last.get("skeptic_final") == "CONFIRMED":
        return dict(base, reviewed="—", delta=None, label_changed=None, cls="OK")
    if ri is None:
        return dict(base, reviewed="không xác định", delta=None, label_changed=None, cls="?")
    rv = seq[ri]
    rtag = "%s#%s" % (rv["dd_date"], rv.get("rev", 1))
    c0, c1 = rv.get("center"), last.get("center")
    l0, l1 = label_class(rv.get("verdict_label")), label_class(last.get("verdict_label"))
    delta = None if not c0 or c1 is None else (c1 - c0) / c0
    changed = None if "?" in (l0, l1) else (l0 != l1)
    if ri == len(seq) - 1:
        # bản cuối chính là bản đã phản biện (status CONFIRMED nhưng skeptic_final chưa nâng): không còn gì sửa ⇒ MECH
        return dict(base, reviewed=rtag, delta=0.0, label_changed=False, cls="MECH")
    if delta is None:
        cls = "?"
    elif abs(delta) > DELTA_THR or changed:
        cls = "FULL"
    elif changed is None:
        cls = "?"
    else:
        cls = "MECH"
    return dict(base, reviewed=rtag, delta=delta, label_changed=changed, cls=cls)


def held_set(rules_path):
    held = set(EXTRA_HELD)
    try:
        for p in json.load(open(rules_path, encoding="utf-8")).get("positions", []):
            held.add(p["ticker"].upper())
    except (OSError, ValueError, KeyError):
        pass
    return held


def watch_close(state_path):
    """(ngày, {mã: close}) của ngày lớn nhất trong state; ({}, None) nếu không đọc được."""
    try:
        days = json.load(open(state_path, encoding="utf-8"))["days"]
        d = max(days)
        return d, {t: v.get("close") for t, v in days[d].items()}
    except (OSError, ValueError, KeyError):
        return None, {}


def build(ledger, held, wday, closes):
    by = collections.defaultdict(list)
    for e in ledger["entries"]:
        by[e["ticker"].upper()].append(e)
    rows = []
    for t, seq in by.items():
        seq.sort(key=lambda e: (e["dd_date"], int(e.get("rev", 1))))
        r = classify(seq)
        c = closes.get(t)
        r["close"] = c
        r["below"] = bool(c is not None and r["zone_low"] is not None and c < r["zone_low"])
        r["prio"] = 1 if t in held else (2 if r["below"] else 3)
        rows.append(r)
    rows.sort(key=lambda r: (r["prio"], CLASS_ORDER[r["cls"]], r["ticker"]))
    return rows


def render(rows, wday, src):
    cnt = collections.Counter(r["cls"] for r in rows)
    L = ["# B2 — Kế hoạch xác nhận lại DD (CHỈ ĐỌC, sinh bởi bin/dd_reconfirm_plan.py)", "",
         "Tổng %d mã · %s" % (len(rows), " · ".join("%s %d" % (k, cnt[k]) for k in ("FULL", "?", "MECH", "OK"))),
         "Nguồn giá/đáy vùng: %s, ngày watch gần nhất = %s (giá = close; \"dưới đáy\" = close < zone_low của entry cuối)." % (src, wday),
         "Luật: xem docstring bin/dd_reconfirm_plan.py. MECH = xác nhận cơ học, KHÔNG tự nâng nhãn CONFIRMED (chờ user chốt).", "",
         "| P | Mã | Rev cuối | skeptic_final | Rev đã phản biện | Δtâm | Đổi nhãn | Lớp | Giá<đáy | close / zone_low |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        d = "—" if r["delta"] is None else "%+.1f%%" % (100 * r["delta"])
        lc = "?" if r["label_changed"] is None and r["cls"] != "OK" else ("—" if r["label_changed"] is None else ("có" if r["label_changed"] else "không"))
        L.append("| P%d | %s | %s | %s | %s | %s | %s | **%s** | %s | %s / %s |" % (
            r["prio"], r["ticker"], r["last"], r["skeptic_final"], r["reviewed"], d, lc, r["cls"],
            "có" if r["below"] else "không", r["close"] if r["close"] is not None else "—", r["zone_low"] if r["zone_low"] is not None else "—"))
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", default=os.path.join(ROOT, "kb", "dd_price_zones.json"))
    ap.add_argument("--out")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    state = os.environ.get("DDZ_STATE") or os.path.join(WC, "data", "dd_price_zone_watch_state.json")
    rules = os.environ.get("DD_EXIT_RULES") or os.path.join(WC, "data", "discretionary_exit_rules.json")
    try:
        ledger = json.load(open(a.ledger, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print("LỖI: không đọc được sổ %s: %s" % (a.ledger, e), file=sys.stderr)
        return 2
    wday, closes = watch_close(state)
    if not closes:
        print("CẢNH BÁO: không đọc được giá watch từ %s ⇒ P2 trống" % state, file=sys.stderr)
    txt = render(build(ledger, held_set(rules), wday, closes), wday, state)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(txt)
        print("ghi %s" % a.out)
    else:
        print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
