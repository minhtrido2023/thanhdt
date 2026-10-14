#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chụp bảng sàn HOSE theo thời điểm ⇒ `data/benchmark/hose_membership_<YYYY-MM-DD>.json` + `_latest`.

Rổ của VN-Index có cổ tức (`vnindex_total_return.py`) = mã đang niêm yết HOSE ngày t. Hai nguồn hợp lại
(nguyên mẫu `agents/Taylor/research/fund_step4_20261014/tr_build.py::hose_spells`):
  (1) mã HIỆN ở HOSE theo bảng sàn VNDirect: [listedDate, delistedDate nếu đã huỷ niêm yết).
  (2) mã đã RỜI HOSE (nay ở HNX/UPCOM/biến mất): sự kiện rời HOSE trong `tav2_bq.corporate_action`
      (MOVE/SUSP/NLIS, khớp tiêu đề); ngày vào = sự kiện vào HOSE gần nhất trước đó, không có thì
      ngày đầu tiên mã có dòng trong `tav2_bq.ticker` từ 2013-12-01 (`ca_leave_start_assumed`).
KHÔNG dùng `universe_pit`/`ticker_prune` (rổ lọc thanh khoản, không phải thành phần VN-Index).

Chạy tuần một lần; in DIFF mã vào/ra HOSE so với `_latest` cũ (stdout — wrapper cron đẩy Trading Daily).

  python3 mike/bin/hose_membership_refresh.py [--out-dir DIR] [--from-files DIR --ca-parquet P --panel-parquet P]
"""
import argparse
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vnindex_total_return as VTR  # noqa: E402

FAR = "2100-01-01"
FLOORS = ("HOSE", "HNX", "UPCOM")
VND_URL = "https://api-finfo.vndirect.com.vn/v4/stocks?q=type:STOCK~floor:{fl}&size=3000"
COUNT_TOL = 0.05          # N-d vòng 2: số mã HOSE đổi > 5% so với _latest ⇒ không ghi đè (nghi nguồn hỏng)
STALE_TMP_S = 3600        # file .tmp.<pid> cũ hơn 1 giờ = lần chạy bị giết giữa chừng ⇒ dọn
LEAVE_RE = r"từ HOSE sang|Hủy niêm yết.*HOSE|GDCC trên HOSE"
ENTER_RE = r"niêm yết.*trên (?:sàn )?HOSE|sang HOSE|giao dịch trên sàn HOSE"


def hose_spells(floor_lists: dict, ca, first_seen: dict) -> list:
    """[(ticker, start, end, src)] — khoảng [start, end) trên HOSE. `floor_lists[fl]` = bản ghi
    VNDirect; `ca` = DataFrame sự kiện MOVE/SUSP/NLIS (ticker, event_code, effective_date,
    event_title_vi); `first_seen[ticker]` = date."""
    import pandas as pd
    rows, cur = [], {}
    for fl in FLOORS:
        for r in floor_lists.get(fl, []):
            cur[r["code"]] = (fl, r.get("status"), r.get("listedDate"), r.get("delistedDate"))
    for code, (fl, st, ld, dd) in cur.items():
        if fl != "HOSE" or not ld:
            continue
        end = dd if (st == "delisted" and dd and dd > ld) else FAR
        rows.append((code, ld[:10], end[:10], "vnd_master"))
    t = ca[ca.event_code.isin(["MOVE", "SUSP", "NLIS"])].copy()
    t["title"] = t.event_title_vi.fillna("")
    t["effective_date"] = pd.to_datetime(t["effective_date"])
    leave = t[t.title.str.contains(LEAVE_RE, regex=True)]
    enter = t[t.title.str.contains(ENTER_RE, regex=True) & ~t.title.str.contains("Hủy")]
    have = {r[0] for r in rows}
    for code, g in leave.groupby("ticker"):
        end = g.effective_date.max()
        if code in have:
            if end >= pd.Timestamp(cur[code][2]):
                continue
        e = enter[(enter.ticker == code) & (enter.effective_date < end)]
        if len(e):
            start, src = e.effective_date.min().date().isoformat(), "ca_leave"
        elif code in first_seen:
            start, src = str(first_seen[code])[:10], "ca_leave_start_assumed"
        else:
            continue
        rows.append((code, start, end.date().isoformat(), src))
    return rows


def snapshot(floor_lists: dict, ca, first_seen: dict, vintage: str, sources: dict) -> dict:
    spells = {}
    for code, a, b, src in sorted(hose_spells(floor_lists, ca, first_seen)):
        spells.setdefault(code, []).append([a, b, src])
    now_hose = sorted(r["code"] for r in floor_lists.get("HOSE", [])
                      if r.get("status") != "delisted")
    return {"vintage": vintage, "built_at_ict": VTR.now_ict().isoformat(timespec="seconds"),
            "sources": sources, "n_tickers": len(spells), "hose_now": now_hose, "spells": spells}


def diff(old: dict, new: dict) -> dict:
    a, b = set(old.get("hose_now", [])), set(new.get("hose_now", []))
    return {"added": sorted(b - a), "removed": sorted(a - b), "old_vintage": old.get("vintage")}


def implausible(old: dict, new: dict, tol: float = COUNT_TOL):
    """Lý do (chuỗi) nếu số mã HOSE hiện tại đổi quá `tol` so với `_latest` cũ, ngược lại None. Bảng sàn
    thật đổi vài mã/tuần; nhảy > 5% gần như chắc là nguồn trả thiếu/thừa (cắt trang, đổi API)."""
    n0, n1 = len(old.get("hose_now") or []), len(new.get("hose_now") or [])
    if n0 and abs(n1 - n0) > tol * n0:
        return (f"số mã HOSE {old.get('vintage')} = {n0} → {new.get('vintage')} = {n1} "
                f"({n1 - n0:+d}, > {tol:.0%} của {n0})")
    return None


def sweep_stale_tmp(out_dir: str, now: float = None) -> list:
    """Xoá `hose_membership_*.json.tmp.*` cũ hơn STALE_TMP_S (lần chạy bị giết sau khi mở file tạm)."""
    now = time.time() if now is None else now
    gone = []
    for f in glob.glob(os.path.join(out_dir, "hose_membership_*.json.tmp.*")):
        if now - os.path.getmtime(f) > STALE_TMP_S:
            os.remove(f)
            gone.append(os.path.basename(f))
    return gone


def _atomic_json(path: str, obj) -> None:
    tmp = f"{path}.tmp.{os.getpid()}"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=0, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def fetch_live():
    import urllib.request
    import pandas as pd
    lists = {}
    for fl in FLOORS:
        with urllib.request.urlopen(VND_URL.format(fl=fl), timeout=60) as r:
            j = json.loads(r.read().decode("utf-8"))
        if j.get("totalElements", 0) > len(j.get("data", [])):
            raise RuntimeError(f"VNDirect {fl}: totalElements {j.get('totalElements')} > "
                               f"{len(j.get('data', []))} bản ghi nhận được — bị cắt trang")
        lists[fl] = j["data"]
    if VTR.WC_ROOT not in sys.path:
        sys.path.insert(0, VTR.WC_ROOT)
    from corp_action_lib import TABLE, bq
    proj = TABLE.split(".")[0]
    ca = pd.DataFrame(bq(f"SELECT c.ticker, c.event_code, CAST(c.effective_date AS STRING) effective_date, "
                         f"c.event_title_vi FROM `{TABLE}` AS c "
                         f"WHERE c.event_code IN ('MOVE','SUSP','NLIS')"))
    fs = {r["ticker"]: r["d"] for r in bq(
        f"SELECT t.ticker, CAST(MIN(t.time) AS STRING) d FROM `{proj}.tav2_bq.ticker` AS t "
        f"WHERE t.time >= '2013-12-01' GROUP BY t.ticker")}
    return lists, ca, fs, {"floors": VND_URL, "corporate_action": TABLE}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", default=VTR.BENCH_DIR)
    ap.add_argument("--vintage", help="mặc định hôm nay ICT")
    ap.add_argument("--from-files", help="thư mục có vndirect_stocks_{HOSE,HNX,UPCOM}.json (offline)")
    ap.add_argument("--ca-parquet")
    ap.add_argument("--panel-parquet")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--accept-count-change", action="store_true",
                    help=f"ghi dù số mã HOSE đổi > {COUNT_TOL:.0%} (đã kiểm bằng mắt là thật)")
    a = ap.parse_args(argv)
    vintage = a.vintage or VTR.now_ict().date().isoformat()
    if a.from_files:
        import pandas as pd
        try:
            import db_dtypes  # noqa: F401 — cột DATE của BQ trong parquet
        except ImportError:
            pass
        lists = {fl: json.load(open(os.path.join(a.from_files, f"vndirect_stocks_{fl}.json")))["data"]
                 for fl in FLOORS}
        ca = pd.read_parquet(a.ca_parquet)
        p = pd.read_parquet(a.panel_parquet, columns=["time", "ticker"])
        fs = {k: str(v)[:10] for k, v in p.groupby("ticker").time.min().items()}
        sources = {"floors": os.path.abspath(a.from_files), "corporate_action": a.ca_parquet}
    else:
        lists, ca, fs, sources = fetch_live()
    snap = snapshot(lists, ca, fs, vintage, sources)
    latest = os.path.join(a.out_dir, "hose_membership_latest.json")
    old = json.load(open(latest, encoding="utf-8")) if os.path.exists(latest) else {}
    d = diff(old, snap)
    print(json.dumps({"vintage": vintage, "n_tickers": snap["n_tickers"],
                      "n_hose_now": len(snap["hose_now"]), "diff": d}, ensure_ascii=False))
    if d["old_vintage"] and (d["added"] or d["removed"]):
        print(f"📋 Bảng sàn HOSE {d['old_vintage']} → {vintage}: vào {d['added'] or '—'}; "
              f"ra {d['removed'] or '—'}")
    bad = implausible(old, snap)
    if bad and not a.accept_count_change:
        print(f"🔴 hose_membership_refresh: KHÔNG ghi — {bad}. Kiểm nguồn {sources.get('floors')}; thật thì "
              f"chạy lại với --accept-count-change.", file=sys.stderr)
        return 2
    if not a.dry_run:
        os.makedirs(a.out_dir, exist_ok=True)
        for g in sweep_stale_tmp(a.out_dir):
            print(f"hose_membership_refresh: dọn file tạm cũ {g}", file=sys.stderr)
        _atomic_json(os.path.join(a.out_dir, f"hose_membership_{vintage}.json"), snap)
        _atomic_json(latest, snap)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
