#!/usr/bin/env python3
"""Rà báo cáo ĐÃ GỬI bằng cổng mới (nhánh fix/total-return-gips-20261010): số công bố vs số đúng chuẩn.
Chỉ ĐỌC. Chạy:  python3 sent_reports_audit.py > sent_reports_audit.out 2> sent_reports_audit.err
Lưu ý: giá phiên lịch sử lấy `Price` thô khi `Close` đã bị điều chỉnh hồi tố (xem `pick_raw_price`);
trên UPCOM `Price` là giá bình quân, có thể lệch 1 bước giá so với giá khớp cuối đã dùng lúc soạn."""
import glob, json, os, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/wt-totalreturn-1010/bin")
import dividend_adjusted_return as dar
import report_return_gate as g

_cache, _real_bq = {}, dar._bq
def _bq(sql):
    if sql not in _cache:
        _cache[sql] = _real_bq(sql)
    return _cache[sql]
dar._bq = _bq
dar.crosscheck_dividend_1y = lambda adjs: adjs          # tầng 3 không đổi số nào — bỏ để nhanh
# Phát hiện tầng 1: MỘT truy vấn/mã cho cả cửa sổ rồi lọc theo ex-date ≤ end — cùng kết quả với
# gọi riêng từng `end` (cú nhảy là thuộc tính cục bộ của chuỗi), nhưng dùng lại được giữa các kỳ.
_det = {}
_TODAY = "2026-10-09"
def _detect(tk, start, end):
    key = (tk, start)
    if key not in _det:
        _det[key] = dar._price_ratio_rows([tk], start, _TODAY)
    rows = [r for r in _det[key] if str(r["d"])[:10] <= end]
    return dar._scan_jumps(tk, rows, start)
dar.detect_adjustments = _detect
_series, _qty = {}, {}
_rs, _rq = dar.broker_cost_series, dar.broker_qty
dar.broker_cost_series = lambda a: _series.setdefault(a, _rs(a))
dar.broker_qty = lambda a: _qty.setdefault(a, _rq(a))

REPORTS = "/home/trido/thanhdt/WorkingClaude/mike/reports"
files = sorted(f for f in glob.glob(os.path.join(REPORTS, "*_report_*.md"))
               if os.path.basename(f).split("_")[0] in ("SpaceX", "ZaloPay")
               and ("_weekly_" in f or "_monthly_" in f))
out = []
for path in files:
    name = os.path.basename(path)
    try:
        labels, asof = g.accounts_asof_from_name(path)
        rows = g.parse_report_rows(path)
        for lb in labels:
            acct = dar.ACCOUNTS[lb]
            pos = g.broker_positions(acct, asof)
            gross, mism, extra = g.entitled_gross(pos.keys(), acct, asof)
            for tk, qty, pct in rows:
                if tk not in pos or abs(pos[tk][0] - qty) > 1e-6:
                    continue
                q, cp, mkt = pos[tk]
                rec = {"report": name, "acct": lb, "asof": asof, "tk": tk, "qty": qty,
                       "published": pct, "cp": round(cp, 2), "mkt": mkt}
                if tk in extra["blockers"]:
                    rec.update(correct=None, why=extra["blockers"][tk])
                else:
                    gr = gross.get(tk, 0.0)
                    exp, _pl, raw = g.expected_pct(q, cp, mkt, gr, addback_ps=extra["addback"].get(tk))
                    rec.update(correct=round(exp, 2), diff=round(pct - exp, 2), raw=round(raw, 2),
                               gross=round(gr, 2))
                out.append(rec)
                print(json.dumps(rec, ensure_ascii=False), flush=True)
    except Exception as e:
        print(json.dumps({"report": name, "error": f"{type(e).__name__}: {e}"}, ensure_ascii=False), flush=True)
