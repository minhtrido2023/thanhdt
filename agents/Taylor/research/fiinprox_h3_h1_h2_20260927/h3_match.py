#!/usr/bin/env python3
"""H3 — nghiem thu PIT cho fiinprox_oshares_pit vs tav2_bq.corporate_action (ISS + AIS).

Khong doan nguyen nhan (coding_guidelines §29): moi lop khong khop chi duoc dat nhan tu
BANG CHUNG doc duoc trong chinh du lieu (co/khong co event nao trong cua so, dau cua delta,
co cot ratio hay khong).
"""
import csv, sys, bisect
from collections import defaultdict
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[4]                      # WorkingClaude
PIT = ROOT / "mike/data/fiinprox_oshares_pit_20260926.csv"
WIN = 3                                  # +/- 3 phien

tdays = [r["d"] for r in csv.DictReader(open(D / "tdays.csv"))]
tidx = {d: i for i, d in enumerate(tdays)}

def tpos(d):
    """chi so phien cua ngay d; ngay khong phai phien -> phien ke tiep."""
    if d in tidx:
        return tidx[d]
    i = bisect.bisect_left(tdays, d)
    return i if i < len(tdays) else len(tdays) - 1

# ---------- 1. su kien PIT ----------
pit_rows = list(csv.DictReader(open(PIT)))
events = []
for r in pit_rows:
    if not r["delta"] or "first_obs" in (r["flags"] or ""):
        continue
    sh = float(r["shares"]); dl = float(r["delta"])
    before = sh - dl
    if before <= 0:
        rel = None
    else:
        rel = dl / before
    events.append(dict(ticker=r["ticker"], date=r["date"], shares=sh, delta=dl,
                       before=before, rel=rel, flags=r["flags"] or ""))

big = [e for e in events if e["rel"] is not None and abs(e["rel"]) >= 0.05]
print(f"PIT: {len(pit_rows)} dong | {len(events)} su kien doi so | "
      f"{len(big)} su kien |delta/before| >= 5%")
# doi chieu voi dinh nghia khac (delta/shares_after) de biet con 2.434 tu dau
alt = [e for e in events if abs(e["delta"]) / e["shares"] >= 0.05]
print(f"  (dinh nghia |delta/shares_after| >= 5% -> {len(alt)} su kien)")

# ---------- 2. ung vien corp-action ----------
ca = defaultdict(list)
for r in csv.DictReader(open(D / "ca_iss_ais.csv")):
    dates = [d for d in (r["exright_date"], r["effective_date"], r["issue_date"],
                         r["listing_date"]) if d]
    if not dates:
        continue
    ca[r["ticker"]].append(dict(r, dates=dates))

# ---------- 3. ghep ----------
def match(ev, date_fields, win=WIN):
    p = tpos(ev["date"])
    out = []
    for c in ca.get(ev["ticker"], []):
        for f in date_fields:
            d = c[f]
            if d and abs(tpos(d) - p) <= win:
                out.append((f, c))
                break
    return out

FIELDS_STRICT = ("exright_date", "effective_date")          # theo dispatch
FIELDS_WIDE = ("exright_date", "effective_date", "issue_date")

def rate(evs, fields, win=WIN):
    n = sum(1 for e in evs if match(e, fields, win))
    return n, len(evs), 100.0 * n / max(1, len(evs))

for lbl, fields in (("exright|effective", FIELDS_STRICT), ("+issue_date", FIELDS_WIDE)):
    for w in (0, 1, 3, 5, 10):
        n, tot, pct = rate(big, fields, w)
        print(f"KHOP NGAY  {lbl:20s} win=+/-{w:<2d}  {n}/{tot} = {pct:.1f}%")

# ---------- 4. khop TY LE ----------
def to_f(x):
    try:
        return float(x)
    except Exception:
        return None

ratio_ok = ratio_bad = ratio_na = 0
ratio_detail = []
for e in big:
    ms = match(e, FIELDS_WIDE)
    if not ms:
        continue
    best = None
    for f, c in ms:
        sd = to_f(c["shares_delta"])
        sta = to_f(c["shares_total_after"])
        er = to_f(c["exercise_ratio"])
        cand = []
        if sd:
            cand.append(("shares_delta", abs(e["delta"] - sd) / max(abs(e["delta"]), 1)))
        if sta:
            cand.append(("shares_total_after", abs(e["shares"] - sta) / max(e["shares"], 1)))
        if er and e["rel"]:
            cand.append(("exercise_ratio", abs(abs(e["rel"]) - er / 100.0) /
                         max(abs(e["rel"]), 1e-9) if er > 1.5 else
                         abs(abs(e["rel"]) - er) / max(abs(e["rel"]), 1e-9)))
        for k, err in cand:
            if best is None or err < best[1]:
                best = (k, err, c["event_code"])
    if best is None:
        ratio_na += 1
    elif best[1] <= 0.02:
        ratio_ok += 1
    else:
        ratio_bad += 1
        ratio_detail.append((e["ticker"], e["date"], e["delta"], e["shares"], best))

mtot = sum(1 for e in big if match(e, FIELDS_WIDE))
print(f"\nKHOP TY LE (trong so {mtot} su kien da khop ngay):")
print(f"  khop <=2%: {ratio_ok} ({100.0*ratio_ok/max(1,mtot):.1f}%)  "
      f"lech >2%: {ratio_bad}  khong co cot so sanh: {ratio_na}")

# ---------- 5. lop khong khop ----------
un = [e for e in big if not match(e, FIELDS_WIDE)]
pos = [e for e in un if e["delta"] > 0]
neg = [e for e in un if e["delta"] < 0]
no_ca_at_all = [e for e in un if not ca.get(e["ticker"])]
print(f"\nKHONG KHOP: {len(un)} ({100.0*len(un)/len(big):.1f}%)")
print(f"  delta > 0: {len(pos)} | delta < 0: {len(neg)}")
print(f"  ma KHONG co bat ky dong ISS/AIS nao trong bang CA: {len(no_ca_at_all)} "
      f"({len({e['ticker'] for e in no_ca_at_all})} ma)")
byyear = defaultdict(int)
for e in un:
    byyear[e["date"][:4]] += 1
print("  theo nam: " + " ".join(f"{k}:{v}" for k, v in sorted(byyear.items())))
bysize = defaultdict(int)
for e in un:
    a = abs(e["rel"])
    b = "5-10%" if a < .1 else "10-25%" if a < .25 else "25-50%" if a < .5 else "50-100%" if a < 1 else ">=100%"
    bysize[b] += 1
print("  theo do lon: " + " ".join(f"{k}:{v}" for k, v in bysize.items()))

with open(D / "h3_unmatched.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticker", "date", "shares_before", "shares_after", "delta", "rel_pct",
                "ticker_has_any_ca_row", "n_ca_rows_same_ticker"])
    for e in sorted(un, key=lambda x: -abs(x["rel"])):
        w.writerow([e["ticker"], e["date"], int(e["before"]), int(e["shares"]), int(e["delta"]),
                    round(100 * e["rel"], 3), bool(ca.get(e["ticker"])), len(ca.get(e["ticker"], []))])
with open(D / "h3_ratio_mismatch.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ticker", "date", "delta_pit", "shares_after_pit", "best_field", "rel_err", "ca_event_code"])
    for t, d, dl, sh, b in sorted(ratio_detail, key=lambda x: -x[4][1])[:400]:
        w.writerow([t, d, int(dl), int(sh), b[0], round(b[1], 4), b[2]])
print(f"\n-> {D/'h3_unmatched.csv'} ; {D/'h3_ratio_mismatch.csv'}")
