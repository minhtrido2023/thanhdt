"""One-time loader (DRY-RUN) cho bang `tav2_mike.treasury_share_events`.

Nap 577 su kien CP quy (buy_done/sell_done) tu `tav2_bq.treasury_news`, gop
`(ticker, public_date, action_type)`, voi size lay tu 3 NGUON KHONG TRON LAN:

  VENDOR_PUBLISHED        128  vendor cong bo thang tren treasury_news        confidence=high
  SIBLING_ROW               3  su kien co CA dong co size LAN dong NULL       confidence=high
                               (size la so vendor cong bo, chi bi dedup che)
  OSHARES_DELTA_INFERRED   33  suy tu lech ticker_financial.OShares           confidence=medium
                               (Winston job _052425; control n=13, 77% khop chinh xac)
  UNSIZED                 413  that su khong co du lieu -> outstanding_delta NULL
                               (KHONG noi suy thanh 0: 62/131 ca control co size that > 0
                                ma OShares bat dong -> NO_MOVE != 0)

Quy uoc dau (do tren toan bo 577 su kien, 0 vi pham):
  treasury_news.shares_delta = Delta luong CP QUY nam giu (buy_done >= 0, sell_done <= 0)
  => outstanding_delta = Delta luong CP LUU HANH = -shares_delta  (mot phep lat dau duy nhat)

SUM(outstanding_delta) KHONG AN TOAN neu khong loc `is_canonical`: mot giao dich that co
the xuat hien o 2 dong (vendor dang 2 ngay khac nhau, hoac 1 dong vendor + 1 dong suy tu
OShares chong nhau) -> cong 2 lan. Xem mark_duplicates(). Query dung:
  SELECT SUM(outstanding_delta) FROM ... WHERE is_canonical

PIT: `confirmed_asof` chi dat cho OSHARES_DELTA_INFERRED = ngay dong BCTC quy SAU thuc su
"biet duoc" so nay (MAX(time, Release_Date) cua dong sau). Join theo `public_date` vao he
rating/sizing ma bo qua cot nay la PIT LEAK cho 33 dong do.

DRY-RUN: KHONG ghi BigQuery, KHONG tao bang. Xuat CSV de review.
Chay:  $DNA_PYEXE build_treasury_share_events.py            # doc BQ that + inputs/resolved.csv
       $DNA_PYEXE build_treasury_share_events.py --help
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import os
import re
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
HERE = os.path.dirname(os.path.abspath(__file__))
LOADER_VERSION = "treasury_share_events_loader/1.0.0"
BQ_TABLE = "lithe-record-440915-m9.tav2_mike.treasury_share_events"

# Dau ky vong cua shares_delta (Delta CP QUY) theo action_type.
VENDOR_SIGN = {"buy_done": +1, "sell_done": -1}
# Dau ky vong cua outstanding_delta (Delta CP LUU HANH) = nguoc lai.
OUTSTANDING_SIGN = {"buy_done": -1, "sell_done": +1}

SOURCE_VENDOR = "VENDOR_PUBLISHED"
SOURCE_SIBLING = "SIBLING_ROW"
SOURCE_INFERRED = "OSHARES_DELTA_INFERRED"
SIZED, UNSIZED = "SIZED", "UNSIZED"

# Dedup: cung mot giao dich that duoc dang 2 lan (xem mark_duplicates).
DUP_MAX_GAP_DAYS = 14
DUP_REL_TOL = 0.05
# Tier nao duoc giu lam canonical khi 2 dong cung mot giao dich (nho hon = tin hon).
TIER_RANK = {SOURCE_VENDOR: 0, SOURCE_SIBLING: 1, SOURCE_INFERRED: 2}

FIELDS = [
    "id", "ticker", "public_date", "action_type", "outstanding_delta",
    "size_status", "source", "confidence", "confirmed_asof",
    "unsized_reason", "inferred_window_days", "dup_group_id", "is_canonical", "duplicate_of",
    "source_news_ids", "first_public_datetime", "loaded_at", "loader_version",
]


# ---------------------------------------------------------------- pure helpers
def event_id(ticker: str, public_date: str, action_type: str) -> str:
    """id deterministic => chay lai / MERGE khong sinh trung."""
    key = f"{ticker}|{public_date}|{action_type}"
    return "TRSY-" + hashlib.sha1(key.encode()).hexdigest()[:16]


def vendor_outstanding_delta(shares_delta, action_type: str):
    """Lat dau mot lan: Delta luu hanh = -Delta CP quy. Sai dau => ValueError (fail loud)."""
    if shares_delta is None:
        return None
    d = int(round(float(shares_delta)))
    if d != 0 and (d > 0) != (VENDOR_SIGN[action_type] > 0):
        raise ValueError(
            f"vi pham quy uoc dau: action_type={action_type} shares_delta={d} "
            f"(ky vong dau {'duong' if VENDOR_SIGN[action_type] > 0 else 'am'})")
    return -d


_WHY_RE = re.compile(r"q(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})")


def parse_quarter_window(why: str):
    """Rut (before_date, after_date) tu chuoi `why` cua Winston. None neu khong khop.

    Gia tri nay LUON phai duoc verify lai bang OShares that (xem verify_inferred)
    truoc khi dung — khong bao gio tin thang chuoi mo ta (§28)."""
    m = _WHY_RE.search(why or "")
    return (m.group(1), m.group(2)) if m else None


def verify_inferred(inferred_delta, before_oshares, after_oshares, action_type: str):
    """Doc lap tinh lai lech OShares va so voi so Winston suy ra.

    Tra (ok, recomputed, reason). Chi khi ok=True dong do moi duoc nap."""
    if before_oshares is None or after_oshares is None:
        return False, None, "THIEU_OSHARES"
    recomputed = int(round(float(after_oshares) - float(before_oshares)))
    if recomputed == 0:
        return False, recomputed, "OSHARES_KHONG_DOI"
    if (recomputed > 0) != (OUTSTANDING_SIGN[action_type] > 0):
        return False, recomputed, "SAI_DAU_KY_VONG"
    if recomputed != int(inferred_delta):
        return False, recomputed, f"LECH_SO_WINSTON(suy={int(inferred_delta)})"
    return True, recomputed, ""


def confirmed_asof_of(fin_time: str, release_date):
    """Ngay som nhat con so suy luan THUC SU biet duoc = MAX(time, Release_Date).

    Release_Date NULL 11,7% va lech `time` 0,7% tren ticker_financial => lay max de
    khong bao gio lac quan hon thuc te."""
    if not release_date:
        return fin_time
    return max(fin_time, release_date)


def same_transaction(a, b):
    """Hai dong CO PHAI la cung mot giao dich that? Luat XAC DINH, khong doan.

    Cung ticker + action_type, |public_date| cach nhau <= DUP_MAX_GAP_DAYS ngay,
    va |outstanding_delta| lech <= DUP_REL_TOL => cung mot giao dich.
    Chi goi tren dong SIZED (delta khong NULL)."""
    if a["ticker"] != b["ticker"] or a["action_type"] != b["action_type"]:
        return False
    gap = abs((date.fromisoformat(b["public_date"])
               - date.fromisoformat(a["public_date"])).days)
    if gap > DUP_MAX_GAP_DAYS:
        return False
    x, y = abs(int(a["outstanding_delta"])), abs(int(b["outstanding_delta"]))
    m = max(x, y)
    if m == 0:
        return True
    return abs(x - y) / m <= DUP_REL_TOL


def mark_duplicates(rows):
    """Gop cac dong la CUNG MOT giao dich thanh nhom, chon DUNG MOT dong canonical.

    VI SAO CAN: khoa gop (ticker, public_date, action_type) KHONG bat duoc truong hop
    vendor dang cung mot dot mua o HAI ngay khac nhau (thong bao chinh thuc + tin bao
    chi), hay mot dong vendor chong mot dong suy tu OShares. Ca 2 deu co that:
      NDN buy_done 2018-05-17 + 2018-05-18, moi dong -1.000.000  => SUM tho -2.000.000
          (+2,5% sai tren ~39,6tr CP luu hanh) cho MOT giao dich 1.000.000 CP.
      CTD buy_done 2021-02-01 (INFERRED -2.008.900) + 2021-02-03 (VENDOR -2.000.000)
          => SUM tho -4.008.900 (+2,7% sai) cho MOT giao dich hon 2tr CP.
    => SUM(outstanding_delta) KHONG an toan neu khong loc `is_canonical`.

    NEO theo dong DAU nhom (khong chain truyen tiep): be rong mot nhom bi chan cung o
    DUP_MAX_GAP_DAYS ngay. Chain se gop nham nhieu dot mua that lien tiep thanh mot —
    mat du lieu, te hon la dem 2 lan.

    Canonical = tier dang tin nhat (VENDOR > SIBLING > INFERRED), roi public_date som
    nhat (cong bo dau tien), roi id nho nhat. Dong con lai O LAI trong bang de audit
    voi is_canonical=False + duplicate_of tro ve id canonical.

    NGUONG do tren 577 dong that, KHONG chon bang cam tinh: 2 cap ung vien nam o gap
    1-2 ngay, cap consecutive-event gan nhat KHAC nam o 53 ngay, va moi cap cung-gia-tri
    (lech <=5%) con lai deu >= 244 ngay (HWS/VND/TW3 mua lai dung lo cu — dot mua THAT
    thu hai, khong duoc gop). => moi N trong [2,52] cho CUNG ket qua; chon 14 (than trong,
    gan dau thap) de 2 dot mua that cach nhau 3 tuan khong bao gio bi gop.

    GIOI HAN: chi phu dong SIZED. 413 dong UNSIZED co delta NULL nen khong so duoc theo
    gia tri (va khong cong vao SUM). Do duoc 6 cap SIZED-UNSIZED + 18 cap UNSIZED-UNSIZED
    trong vong 14 ngay — nghi trung nhung KHONG chung minh duoc => de nguyen
    is_canonical=True; COUNT(*) so su kien co the phong toi da 24, SUM thi khong.
    """
    buckets = collections.defaultdict(list)
    for r in rows:
        if r["outstanding_delta"] is not None:
            buckets[(r["ticker"], r["action_type"])].append(r)

    groups = []
    for key in sorted(buckets):
        opened = []
        for r in sorted(buckets[key], key=lambda x: (x["public_date"], x["id"])):
            for g in opened:
                if same_transaction(g[0], r):
                    g.append(r)
                    break
            else:
                opened.append([r])
        groups.extend(g for g in opened if len(g) > 1)

    for g in groups:
        gid = "TRSYG-" + hashlib.sha1(
            "|".join(sorted(x["id"] for x in g)).encode()).hexdigest()[:16]
        canon = min(g, key=lambda x: (TIER_RANK[x["source"]], x["public_date"], x["id"]))
        for x in g:
            x["dup_group_id"] = gid
            x["is_canonical"] = x is canon
            x["duplicate_of"] = None if x is canon else canon["id"]
    return groups


def build_rows(events, inferred, loaded_at):
    """Dung toan bo dong bang tu 3 nguon. Ham THUAN — selfcheck goi thang, khong can BQ.

    events:   [{ticker, public_date, action_type, shares_delta, n_rows, n_null,
                n_distinct, news_ids, first_public_datetime}]
    inferred: {(ticker, public_date, action_type): {outstanding_delta, confirmed_asof}}
              (chi chua ca DA verify), va {..: {"unsized_reason": str}} cho phan con lai.
    """
    rows, seen = [], set()
    for e in events:
        t, d, at = e["ticker"], e["public_date"], e["action_type"]
        if at not in VENDOR_SIGN:
            raise ValueError(f"action_type ngoai pham vi: {at}")
        key = (t, d, at)
        if key in seen:
            raise ValueError(f"su kien trung sau khi gop: {key}")
        seen.add(key)
        if int(e["n_distinct"]) > 1:
            raise ValueError(f"{key}: {e['n_distinct']} gia tri shares_delta khac nhau — "
                             "chua co luat chon, dung lai thay vi doan")

        delta = vendor_outstanding_delta(e.get("shares_delta"), at)
        inf = inferred.get(key, {})
        if delta is not None:
            # co size vendor: SIBLING_ROW neu su kien con dong NULL bi dedup che
            source = SOURCE_SIBLING if int(e["n_null"]) > 0 else SOURCE_VENDOR
            row = dict(outstanding_delta=delta, size_status=SIZED, source=source,
                       confidence="high", confirmed_asof=None, unsized_reason=None,
                       inferred_window_days=None)
        elif "outstanding_delta" in inf:
            row = dict(outstanding_delta=int(inf["outstanding_delta"]), size_status=SIZED,
                       source=SOURCE_INFERRED, confidence="medium",
                       confirmed_asof=inf["confirmed_asof"], unsized_reason=None,
                       inferred_window_days=inf["window_days"])
        else:
            row = dict(outstanding_delta=None, size_status=UNSIZED, source=None,
                       confidence=None, confirmed_asof=None, inferred_window_days=None,
                       unsized_reason=inf.get("unsized_reason") or "UNKNOWN")
        row.update(id=event_id(t, d, at), ticker=t, public_date=d, action_type=at,
                   dup_group_id=None, is_canonical=True, duplicate_of=None,
                   source_news_ids=e.get("news_ids"),
                   first_public_datetime=e.get("first_public_datetime"),
                   loaded_at=loaded_at, loader_version=LOADER_VERSION)
        rows.append({k: row[k] for k in FIELDS})
    mark_duplicates(rows)
    return rows


# ------------------------------------------------------------------ BQ readers
def _bq():
    sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
    from corp_action_lib import bq
    return bq


def fetch_events():
    bq = _bq()
    raw = bq("""
      SELECT ticker, CAST(public_date AS STRING) public_date, action_type,
             MAX(shares_delta) shares_delta,
             COUNT(*) n_rows, COUNTIF(shares_delta IS NULL) n_null,
             COUNT(DISTINCT shares_delta) n_distinct,
             STRING_AGG(DISTINCT CAST(news_id AS STRING), ',' ORDER BY CAST(news_id AS STRING)) news_ids,
             CAST(MIN(public_datetime) AS STRING) first_public_datetime
      FROM `lithe-record-440915-m9.tav2_bq.treasury_news`
      WHERE action_type IN ('buy_done','sell_done')
      GROUP BY 1,2,3 ORDER BY 1,2,3""")
    out = []
    for r in raw:
        sd = r["shares_delta"]
        out.append({**r, "shares_delta": None if sd in (None, "") else float(sd)})
    return out


def fetch_financials(pairs):
    """pairs: {(ticker, date)} -> {(ticker,date): {OShares, release_date}}"""
    if not pairs:
        return {}
    bq = _bq()
    tickers = sorted({t for t, _ in pairs})
    inlist = ",".join(f"'{t}'" for t in tickers)
    raw = bq(f"""
      SELECT ticker, CAST(time AS STRING) t, OShares, CAST(Release_Date AS STRING) rd
      FROM `lithe-record-440915-m9.tav2_bq.ticker_financial`
      WHERE ticker IN ({inlist}) AND OShares IS NOT NULL AND OShares > 0""")
    return {(r["ticker"], r["t"]): {"oshares": float(r["OShares"]),
                                    "release_date": r["rd"] or None} for r in raw}


def load_winston_resolved(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def load_winston_reasons(path):
    """tier cua cac ca KHONG suy duoc -> unsized_reason."""
    out = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["is_unsized"].strip().lower() == "true" and not (r["inferred"] or "").strip():
                out[(r["ticker"], r["public_date"][:10], r["action_type"])] = {"unsized_reason": r["tier"]}
    return out


def resolve_inferred(resolved_rows, reasons, fin):
    """Verify DOC LAP tung ca suy luan roi moi cho vao. Tra (inferred_map, rejected)."""
    inferred, rejected = dict(reasons), []
    for r in resolved_rows:
        t, d, at = r["ticker"], r["public_date"][:10], r["action_type"]
        key = (t, d, at)
        win = parse_quarter_window(r["why"])
        if not win:
            rejected.append((*key, "KHONG_DOC_DUOC_CUA_SO", r["why"]))
            continue
        before_d, after_d = win
        b, a = fin.get((t, before_d)), fin.get((t, after_d))
        ok, recomputed, why = verify_inferred(
            float(r["inferred"]), b and b["oshares"], a and a["oshares"], at)
        if not ok:
            rejected.append((*key, why, f"{before_d}..{after_d}"))
            continue
        inferred[key] = {
            "outstanding_delta": recomputed,
            "confirmed_asof": confirmed_asof_of(after_d, a["release_date"]),
            # Be rong cua so OShares that su dung. 28/33 ca ~1 quy (76-115 ngay); 5 ca
            # phai noi ra 2 quy (176-188 ngay) vi quy ke tiep bi confounder. Nhom control
            # do do chinh xac (77%/85%/92%) gan nhu chi gom ca 1 quy => 5 dong window dai
            # KHONG duoc nhom control dai dien. Luu SO DO, khong luu nhan k.
            "window_days": (date.fromisoformat(after_d) - date.fromisoformat(before_d)).days,
        }
    return inferred, rejected


# ------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resolved", default=f"{HERE}/inputs/resolved.csv")
    ap.add_argument("--final-inferred", default=f"{HERE}/inputs/final_inferred.csv")
    ap.add_argument("--out", default=f"{HERE}/treasury_share_events_dryrun.csv")
    a = ap.parse_args()

    loaded_at = datetime.now(_ICT).isoformat(timespec="seconds")
    events = fetch_events()
    resolved = load_winston_resolved(a.resolved)
    reasons = load_winston_reasons(a.final_inferred)

    need = set()
    for r in resolved:
        win = parse_quarter_window(r["why"])
        if win:
            need |= {(r["ticker"], win[0]), (r["ticker"], win[1])}
    fin = fetch_financials(need)

    inferred, rejected = resolve_inferred(resolved, reasons, fin)
    rows = build_rows(events, inferred, loaded_at)

    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    Counter = collections.Counter
    by_src = Counter(r["source"] or "(unsized)" for r in rows)
    print(f"DRY-RUN — KHONG ghi BQ. Bang dich (chua ton tai): {BQ_TABLE}")
    print(f"  {len(rows)} dong -> {a.out}")
    for k, v in sorted(by_src.items(), key=lambda x: -x[1]):
        print(f"    {k:<24}{v:>5}")
    print(f"  id duy nhat: {len({r['id'] for r in rows}) == len(rows)}")
    sized = [r for r in rows if r["size_status"] == SIZED]
    print(f"  SIZED {len(sized)} / UNSIZED {len(rows)-len(sized)}"
          f" | outstanding_delta NULL tren UNSIZED: "
          f"{all(r['outstanding_delta'] is None for r in rows if r['size_status'] == UNSIZED)}")
    print(f"  confirmed_asof chi tren {SOURCE_INFERRED}: "
          f"{ {r['source'] for r in rows if r['confirmed_asof']} }")
    if rejected:
        print(f"  !! {len(rejected)} ca suy luan BI TU CHOI khi verify doc lap:")
        for x in rejected:
            print(f"     {x}")
    else:
        print(f"  verify doc lap OShares: {len(resolved)}/{len(resolved)} ca suy luan KHOP")
    print(f"  unsized_reason: {dict(Counter(r['unsized_reason'] for r in rows if r['unsized_reason']))}")

    noncanon = [r for r in rows if not r["is_canonical"]]
    ngroups = len({r["dup_group_id"] for r in rows if r["dup_group_id"]})
    print(f"  dedup (gap<={DUP_MAX_GAP_DAYS}d, |delta| lech<={DUP_REL_TOL:.0%}):"
          f" {ngroups} nhom trung, {len(noncanon)} dong is_canonical=False")
    for r in sorted(noncanon, key=lambda x: (x["ticker"], x["public_date"])):
        canon = next(c for c in rows if c["id"] == r["duplicate_of"])
        print(f"     {r['ticker']:<5}{r['action_type']:<11}{r['public_date']} "
              f"{r['outstanding_delta']:>12} ({r['source']}) -> canonical "
              f"{canon['public_date']} {canon['outstanding_delta']:>12} ({canon['source']})")
    s_all = sum(r["outstanding_delta"] for r in rows if r["outstanding_delta"] is not None)
    s_can = sum(r["outstanding_delta"] for r in rows
                if r["outstanding_delta"] is not None and r["is_canonical"])
    print(f"  SUM(outstanding_delta): tho {s_all:,} | loc is_canonical {s_can:,}"
          f" | chenh {s_all - s_can:,}")


if __name__ == "__main__":
    main()
