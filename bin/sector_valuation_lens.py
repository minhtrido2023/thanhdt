#!/usr/bin/env python3
"""FLOOR_FAIL → lăng kính định giá theo ngành: trả lời SẴN "có được SKIP mã này không".

⚠️ CHỈ ĐỌC. Không đặt lệnh, không sửa plan, KHÔNG gọi BQ (điều 6 coding_guidelines: same-day
   phải là DNSE — script này không đụng giá same-day, chỉ đọc chỉ số định giá đã chốt).

VÌ SAO CÓ FILE NÀY (sự cố thật 2026-07-28): `FLOOR_FAIL` KHÔNG phải field do code sinh ra để
chặn — nó là chữ DollarBill tự viết mô tả một mã trượt golden floor (ROE_Min3Y≥0 ∧ CF_OA_3Y>0).
LAG chỉ có ĐÚNG 1 gate cứng: 8L rating≤3 (`lag_filter_low_rating()`, đã chạy ở nguồn). Vì
FLOOR_FAIL không có code backing, 2 phiên dispatch diễn giải khác nhau trên CÙNG 1 CSV
(signal 2026-07-27): `plan_SpaceX_2026-07-28.json` áp lăng kính chứng khoán (P/B<1,8 +
ROE_TTM>8% → CHEAP) rồi giữ EVF/PSI/VCI; `plan_ZaloPay_2026-07-28.json` ghi "FLOOR_FAIL — skip"
cho cả 3.

ĐIỂM MẤU CHỐT — LĂNG KÍNH ĐÃ CÓ SẴN, KHÔNG PHẢI THIẾU CÔNG CỤ: `alt_valuation_lens.py` (tạo
2026-07-20, commit 8136112 — TRƯỚC sự cố 8 ngày) đã tính đúng lăng kính đó, và
`golive_recommend_v23.py` đã IN KẾT QUẢ vào chính cột `due_diligence` của CSV mà cả 2 phiên
đang đọc. Kiểm chứng trên file gốc `golive_v23_recommendations_2026-07-27.csv`: cả 3 mã đều
mang sẵn "🟢 P/B band + ROE (chứng khoán): ... — CHEAP". Nghĩa là phiên ZaloPay đã bỏ qua một
giá trị ĐÃ TÍNH XONG nằm ngay trong ô nó đọc. Vậy script này KHÔNG viết lại lăng kính (§2/§3
coding_guidelines: không nhân bản logic) — nó TRÍCH giá trị đó ra và biến thành 1 quyết định
dứt khoát, để không còn chỗ cho 2 cách hiểu.

NGUỒN (theo thứ tự ưu tiên):
  1. `--from-csv` / `--signal-date` → cột `due_diligence` của CSV khuyến nghị. ĐÚNG POINT-IN-
     TIME (là thứ engine đã tính tại signal_date đó) và tái lập được cho mọi ngày quá khứ.
  2. `alt_valuation_lens.alt_lens()` live — đọc `data/rating_8l.csv` (snapshot HÔM NAY, refresh
     17:45 ICT). Chỉ dùng khi mã không có trong CSV. ⚠ KHÔNG point-in-time, KHÔNG join ngược
     vào backtest (cảnh báo nguyên văn của module gốc).

QUYẾT ĐỊNH (cơ học, 1-1 với luật `kb/context_planning_mini.md` §"FLOOR_FAIL KHÔNG phải gate cứng"):
  CHEAP  → `KHONG_SKIP_VI_FLOOR_FAIL` — lăng kính ngành ỦNG HỘ; FLOOR_FAIL một mình KHÔNG đủ
           để loại. Mã vẫn phải qua các gate CỨNG hiện có (8L rating≤3 đã lọc ở nguồn, %ADV,
           cash-discipline) — script này KHÔNG cấp quyền mua cho ai.
  RICH   → `SKIP_CO_CAN_CU` — lăng kính thay thế CŨNG nói đắt ⇒ skip là có căn cứ, ghi rõ lý do.
  N/A    → `CAN_NGUOI_QUYET` — chỉ có lăng kính THÔ/fallback (8L rộng, P/B thô bảo hiểm), không
           phân định được. KHÔNG được lặng lẽ skip, cũng KHÔNG được lặng lẽ mua.
  không có lăng kính → `CAN_NGUOI_QUYET` (ngành chưa có lăng kính thay thế).

    python3 mike/bin/sector_valuation_lens.py --signal-date 2026-07-27 --floor-fail-only
    python3 mike/bin/sector_valuation_lens.py --ticker VCI --ticker PSI --ticker EVF
"""
import argparse
import csv
import datetime as dt
import glob
import json
import os
import re
import sys

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, WC_ROOT)

RECS_DIR = os.path.join(WC_ROOT, "deploy_golive_dt5g_v4", "out")

# Khớp ĐÚNG chuỗi `alt_valuation_lens.format_alt_lens()` phát ra. Đổi câu chữ bên đó mà không
# đổi ở đây → `_parse_lens` trả None → script rơi về nhánh live, KHÔNG bịa verdict.
_RE_LENS = re.compile(
    r"→ thay thế:\s*(?:🟢\s*|🔴\s*)?(?P<lens>.+?):\s*"
    r"(?P<detail>.*?)(?:\s+—\s+(?P<verdict>CHEAP|RICH))?\s*\[(?P<conf>[^\]]+)\]")
_RE_NO_LENS = re.compile(r"→ chưa có lăng kính định giá cho ngành này")
_RE_DCF = re.compile(r"(?:🟢|🔴)?\s*DCF:\s*(?P<v>CHEAP|RICH|NOT_COMPUTED)(?:\s*\((?P<why>[^)]*)\))?")

DECISIONS = {
    "CHEAP": ("KHONG_SKIP_VI_FLOOR_FAIL",
              "lăng kính ngành ỦNG HỘ — FLOOR_FAIL một mình KHÔNG đủ để loại mã LAG"),
    "RICH": ("SKIP_CO_CAN_CU",
             "lăng kính thay thế CŨNG nói đắt — skip là có căn cứ, ghi rõ lý do trong plan"),
    "N/A": ("CAN_NGUOI_QUYET",
            "chỉ có lăng kính THÔ/fallback — không phân định được, KHÔNG lặng lẽ skip"),
    None: ("CAN_NGUOI_QUYET", "ngành này chưa có lăng kính định giá thay thế"),
}


def _d(x):
    if isinstance(x, dt.datetime):
        return x.date()
    if isinstance(x, dt.date):
        return x
    return dt.date.fromisoformat(str(x)[:10])


def _parse_lens(dd_text):
    """Trích {lens, verdict, detail, confidence} từ cột due_diligence. None nếu không có."""
    t = dd_text or ""
    m = _RE_LENS.search(t)
    if m:
        return {"lens": m.group("lens").strip(), "verdict": m.group("verdict") or "N/A",
                "detail": m.group("detail").strip(), "confidence": m.group("conf").strip()}
    if _RE_NO_LENS.search(t):
        return None
    return None


def _parse_dcf(dd_text):
    m = _RE_DCF.search(dd_text or "")
    if not m:
        return None
    return {"verdict": m.group("v"), "reason": (m.group("why") or "").strip() or None}


def _decide(verdict):
    code, why = DECISIONS.get(verdict, DECISIONS[None])
    return code, why


def _row(ticker, floor_fail, lens, dcf, source, book=None, status=None):
    # Lăng kính thay thế CHỈ có nghĩa khi DCF không tính được. DCF chạy được thì nó mới là trục
    # định giá chính — không lấy fallback đè lên nó.
    dcf_v = (dcf or {}).get("verdict")
    if dcf_v in ("CHEAP", "RICH"):
        code, why = _decide(dcf_v)
        why = f"DCF chạy được ({dcf_v}) — dùng thẳng DCF, không cần lăng kính thay thế"
        used = "DCF"
        verdict = dcf_v
        lens_name = "DCF (dcf_valuation)"
        detail = (dcf or {}).get("reason")
        conf = "DCF chính quy"
    else:
        verdict = (lens or {}).get("verdict") if lens else None
        code, why = _decide(verdict)
        used = "alt_lens"
        lens_name = (lens or {}).get("lens")
        detail = (lens or {}).get("detail")
        conf = (lens or {}).get("confidence")
    return {
        "ticker": ticker, "book": book, "status": status,
        "floor_fail": floor_fail,
        "valuation_axis_used": used, "lens": lens_name, "verdict": verdict,
        "detail": detail, "confidence": conf,
        "dcf": dcf, "decision": code, "decision_why": why, "source": source,
    }


def _live_lens(ticker):
    """alt_valuation_lens.alt_lens() — snapshot HÔM NAY. Mọi lỗi → None (fail-safe như bản gốc)."""
    try:
        import alt_valuation_lens
        return alt_valuation_lens.alt_lens(ticker)
    except Exception:
        return None


def lens_report(tickers=None, signal_date=None, csv_path=None, floor_fail_only=False,
                books=("LAG",)):
    """Báo cáo lăng kính cho danh sách mã (hoặc mọi mã FLOOR_FAIL trong CSV)."""
    out = {
        "script": "mike/bin/sector_valuation_lens.py",
        "signal_date": None, "csv": None, "results": [], "counts": {}, "notes": [],
    }
    rows_by_tk = {}
    if csv_path is None and signal_date is not None:
        csv_path = os.path.join(RECS_DIR, f"golive_v23_recommendations_{_d(signal_date)}.csv")
    if csv_path is None and not tickers:
        cands = sorted(glob.glob(os.path.join(RECS_DIR, "golive_v23_recommendations_*.csv")))
        csv_path = cands[-1] if cands else None
    if csv_path and os.path.exists(csv_path):
        out["csv"] = os.path.relpath(csv_path, WC_ROOT)
        out["signal_date"] = os.path.basename(csv_path)[
            len("golive_v23_recommendations_"):-len(".csv")]
        with open(csv_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if books and (r.get("book") or "").strip() not in books:
                    continue
                rows_by_tk.setdefault((r.get("ticker") or "").strip(), r)
    elif csv_path:
        out["notes"].append(f"⚠ không thấy CSV {csv_path} — chỉ dùng được lăng kính LIVE")

    if tickers:
        want = [t.strip().upper() for t in tickers]
    else:
        want = [t for t, r in rows_by_tk.items()
                if (not floor_fail_only) or "FLOOR_FAIL" in (r.get("due_diligence") or "")]
    want = sorted(set(want))

    for tk in want:
        r = rows_by_tk.get(tk)
        if r is not None:
            dd = r.get("due_diligence") or ""
            out["results"].append(_row(
                tk, "FLOOR_FAIL" in dd, _parse_lens(dd), _parse_dcf(dd),
                source=f"csv:{out['csv']}", book=(r.get("book") or "").strip(),
                status=(r.get("status") or "").strip()))
        else:
            d = _live_lens(tk)
            lens = ({"lens": d["lens"], "verdict": d["verdict"], "detail": d["detail"],
                     "confidence": d["confidence"]} if d else None)
            res = _row(tk, None, lens, None, source="live:data/rating_8l.csv")
            res["caveat"] = ("mã không có trong CSV signal_date → dùng snapshot rating_8l.csv "
                             "HÔM NAY (không point-in-time); FLOOR_FAIL không xác định được ở đây")
            out["results"].append(res)

    for res in out["results"]:
        out["counts"][res["decision"]] = out["counts"].get(res["decision"], 0) + 1
    out["notes"].append(
        "FLOOR_FAIL/golden-floor KHÔNG phải gate cứng cho LAG. Gate cứng DUY NHẤT của LAG là 8L "
        "rating≤3, đã chạy ở nguồn (lag_filter_low_rating). Script này KHÔNG cấp quyền mua: mọi "
        "lệnh vẫn qua DD/%ADV/cash-discipline như cũ.")
    out["notes"].append(
        "Áp NHẤT QUÁN cả 2 account: cùng CSV, cùng mã ⇒ cùng decision. Lệch = một bên bỏ qua "
        "giá trị đã tính sẵn, không phải khác khẩu vị.")
    return out


def _print_human(res):
    print(f"Lăng kính định giá theo ngành — signal {res.get('signal_date')} "
          f"(CSV: {res.get('csv')})")
    if not res["results"]:
        print("  (không có mã nào)")
    for r in res["results"]:
        ff = {True: "FLOOR_FAIL", False: "floor OK", None: "floor ?"}[r["floor_fail"]]
        print(f"\n  {r['ticker']:<5} [{r.get('book') or '-'}] {ff}  · trục: {r['valuation_axis_used']}")
        print(f"    lăng kính : {r['lens'] or '(không có)'}")
        print(f"    kết luận  : {r['verdict'] or 'n/a'} — {r['detail'] or ''}")
        if r.get("confidence"):
            print(f"    độ tin cậy: {r['confidence']}")
        print(f"    QUYẾT ĐỊNH: {r['decision']} — {r['decision_why']}")
        if r.get("caveat"):
            print(f"    ⚠ {r['caveat']}")
        print(f"    nguồn     : {r['source']}")
    print()
    for n in res.get("notes") or []:
        print(f"  · {n}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ticker", action="append", default=None, help="lặp lại được")
    ap.add_argument("--signal-date", default=None)
    ap.add_argument("--csv", default=None)
    ap.add_argument("--floor-fail-only", action="store_true",
                    help="không truyền --ticker: chỉ lấy mã có cờ FLOOR_FAIL trong CSV")
    ap.add_argument("--book", action="append", default=None, help="mặc định LAG")
    ap.add_argument("--out", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    res = lens_report(a.ticker, a.signal_date, a.csv, a.floor_fail_only,
                      books=tuple(a.book) if a.book else ("LAG",))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        if not a.json:
            print(f"→ {a.out}")
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        _print_human(res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
