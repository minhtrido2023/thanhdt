# -*- coding: utf-8 -*-
"""lag_liq_ledger.py — sổ APPEND-ONLY ghi lại ứng viên LAG bị loại ở tầng tín hiệu.

VÌ SAO CẦN (job Taylor_20260803_035250, việc 3 — user: "dùng hệ thống để đánh giá, không thể
đánh giá tay mãi"):
Câu hỏi còn treo là con số +3,85pp/+4,11pp CAGR gán cho `lag_filter_illiquid()` — quant-skeptic
đã chấm INCONCLUSIVE BA LẦN vì chưa tách được EDGE THẬT (vốn chảy sang event LAG kế tiếp) khỏi
HIỆN VẬT MÔ HÌNH FILL (book đơn giản không fill nổi mã LAG ở quy mô 25B). Hai giả thuyết để lại
CÙNG một dấu vết trên CSV backtest ⇒ chạy lại backtest bao nhiêu lần cũng không tách được.
Thứ tách được là DỮ LIỆU LIVE kể từ khi bộ lọc sống (2026-07-21).

KHE HỞ THẬT (đo, không suy đoán — 2026-08-03):
  · Nhánh BỊ LOẠI: `data/golive_v23_status.json` CÓ ghi `lag_liq_excluded` mỗi phiên (07-31: 21
    mã) nhưng file này bị GHI ĐÈ mỗi lần chạy VÀ nằm trong .gitignore (`git log` = 0 commit)
    ⇒ KHÔNG có một ngày lịch sử nào. Đây là dữ liệu KHÔNG tái tạo được về sau: bộ lọc chốt theo
    dòng ADV *gần nhất tại thời điểm chạy*, mà `Volume_3M_P50` là trung vị trượt 3 tháng nên
    replay hôm nay KHÔNG cho lại đúng tập mã đã bị loại hôm đó.
  · Nhánh ĐƯỢC GIỮ: đã có sẵn lịch sử — `deploy_golive_dt5g_v4/out/golive_v23_recommendations_
    <date>.csv` (38 file có ngày tại thời điểm viết). KHÔNG cần log thêm.
  · Kết cục (return) của CẢ HAI nhánh: luôn truy hồi được từ BQ về sau (giá lịch sử không đổi)
    ⇒ CỐ Ý không log ở đây. Fill thật của book live: đã nằm ở `data/execution_logs/
    dnse_raw_*.jsonl`. CỐ Ý không log lại.
⇒ Mở rộng TỐI THIỂU = chỉ vá đúng một lỗ hổng duy nhất: giữ lại nhánh BỊ LOẠI theo ngày.

CÁI NÀY KHÔNG LÀM (đọc kỹ trước khi trích dẫn):
Sổ này KHÔNG kết luận gì, KHÔNG chấm điểm bộ lọc, KHÔNG feed vào bất kỳ gate production nào.
Nó chỉ tích luỹ nguyên liệu để tới mốc rà soát (xem `mike/kb/projects/lag-adv-filter-tracking.md`)
có dữ liệu THẬT mà phân rã, thay vì chạy lại backtest lần thứ tư.

QUAN HỆ VỚI `data/lag_edge_health.csv` (KHÁC HẲN, đừng lẫn):
`edge_health_monitor.py::lag_edge_health()` dựng lại cohort e3 nghiên cứu (NP_R>=15,
prior_n_good>=4, pa_HL3>=5) rồi đo mean/win trượt 12 tháng, và file đó là INPUT SỐNG của
production (`golive_recommend_v23.py:287` chọn w_LAG). Nó KHÔNG tách được đóng góp của
`lag_filter_illiquid()` — ba lý do cơ chế: (a) hàng ghi ra chỉ có {entry, ret}, KHÔNG có ticker
nên không quy chiếu ngược được mã nào; (b) không có cột thanh khoản/ADV nào; (c) nghiêm trọng
nhất — nó đo p0/p1 close-to-close với giả định fill lý tưởng, TRÙNG ĐÚNG giả định đang bị nghi
ngờ, nên về nguyên tắc không thể dùng nó để bác chính giả định đó. ⇒ Vì vậy ledger này là FILE
RIÊNG. TUYỆT ĐỐI không thêm cột vào `lag_edge_health.csv` (schema đó là hợp đồng với production).

Chạy:  python3 lag_liq_ledger.py              # append phiên hiện tại (idempotent)
       python3 lag_liq_ledger.py --selfcheck  # test, không đụng file thật
"""
import csv
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATUS = os.path.join(WORKDIR, "data", "golive_v23_status.json")
LEDGER = os.path.join(WORKDIR, "data", "lag_liq_ledger.csv")

FIELDS = ["signal_date", "gate", "ticker", "reason_kind", "metric", "reason", "first_seen_ts"]

# gate -> key trong status json. Cả 3 cổng loại-ứng-viên-LAG ở tầng tín hiệu đều ghi cùng một
# sổ: câu hỏi cần trả lời là "vốn chảy đi đâu khi một mã bị chặn", mà cả 3 cổng đều chặn theo
# đúng cơ chế đó — tách file theo cổng chỉ làm khó việc nối lại sau này.
GATES = {
    "liq": "lag_liq_excluded",
    "rating": "lag_rating_excluded",
    "forensic": "lag_forensic_excluded",
}

_RE_STALE = re.compile(r"ADV cũ (\d+) ngày")
_RE_VOL = re.compile(r"Volume_3M_P50=([0-9.eE+-]+)")


def parse_liq_reason(reason):
    """Tách chuỗi reason của lag_filter_illiquid() thành (kind, metric).

    CỐ Ý parse chuỗi thay vì sửa `lag_liquidity_filter.py` cho nó trả thêm field: file đó là
    code production đang chạy live, một sổ theo dõi KHÔNG đáng để chạm vào. Ba template dưới
    đây khớp nguyên văn 3 nhánh `dropped.append` của hàm đó; template đổi thì rơi về
    kind='other' (giữ nguyên `reason` thô) chứ không mất dòng.
    """
    m = _RE_STALE.search(reason)
    if m:
        return "stale_adv", float(m.group(1))
    m = _RE_VOL.search(reason)
    if m:
        return "adv_zero", float(m.group(1))
    if "không có dòng giá nào" in reason:
        return "no_price_row", ""
    return "other", ""


def rows_from_status(st):
    """status dict -> list dòng ledger (chưa khử trùng lặp)."""
    sd = st.get("signal_date") or st.get("date")
    if not sd:
        return []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    for gate, key in GATES.items():
        for d in st.get(key) or []:
            tk = d.get("ticker")
            if not tk:
                continue
            reason = d.get("reason", "")
            if gate == "liq":
                kind, metric = parse_liq_reason(reason)
            elif gate == "rating":
                kind, metric = "rating_fail", d.get("rating", "")
            else:
                kind, metric = d.get("kind", "forensic"), d.get("flag_date") or ""
            out.append({
                "signal_date": str(sd), "gate": gate, "ticker": tk,
                "reason_kind": kind, "metric": "" if metric is None else metric,
                "reason": reason, "first_seen_ts": ts,
            })
    return out


def read_ledger(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def append_rows(new_rows, path=LEDGER):
    """Ghi thêm, IDEMPOTENT theo khoá (signal_date, gate, ticker).

    Chạy lại cùng một phiên bao nhiêu lần cũng ra cùng một file — §5 coding_guidelines: script
    này treo vào chuỗi cron EOD, bị giết giữa chừng rồi chạy lại là chuyện bình thường.
    `first_seen_ts` của dòng đã có được GIỮ NGUYÊN (không refresh) để còn truy được lần đầu
    nhìn thấy. Ghi tmp + os.replace: chết giữa chừng không để lại file nửa vời.
    """
    existing = read_ledger(path)
    seen = {(r["signal_date"], r["gate"], r["ticker"]) for r in existing}
    added = [r for r in new_rows if (r["signal_date"], r["gate"], r["ticker"]) not in seen]
    if not added:
        return existing, 0
    allrows = existing + added
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(allrows)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return allrows, len(added)


def main():
    try:
        with open(STATUS, "r", encoding="utf-8") as f:
            st = json.load(f)
    except Exception as e:
        # Fail-soft có chủ ý: script này treo vào chuỗi EOD live (bq_freshness_check.sh). Một
        # sổ theo dõi KHÔNG bao giờ được phép làm hỏng chuỗi lập plan T+1.
        print(f"[lag-liq-ledger] skipped: không đọc được {STATUS} ({e})")
        return 0
    rows = rows_from_status(st)
    if not rows:
        print(f"[lag-liq-ledger] phiên {st.get('signal_date')}: không có mã nào bị loại — bỏ qua")
        return 0
    allrows, n_added = append_rows(rows)
    sd = rows[0]["signal_date"]
    by = {}
    for r in rows:
        by[r["gate"]] = by.get(r["gate"], 0) + 1
    detail = ", ".join(f"{g}={n}" for g, n in sorted(by.items()))
    print(f"[lag-liq-ledger] phiên {sd}: +{n_added} dòng mới ({detail}); "
          f"tổng {len(allrows)} dòng / {len({r['signal_date'] for r in allrows})} phiên")
    return 0


# ---------------------------------------------------------------- selfcheck
def _selfcheck():
    import shutil
    tmpd = tempfile.mkdtemp(prefix="lagledger_sc_")
    path = os.path.join(tmpd, "ledger.csv")
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + name)
        if not cond:
            ok = False

    st1 = {"signal_date": "2026-07-31", "lag_liq_excluded": [
        {"ticker": "ATS", "reason": "dữ liệu ADV cũ 31 ngày (> 30) — có thể ngừng giao dịch/huỷ niêm yết"},
        {"ticker": "BTW", "reason": "Volume_3M_P50=0.0 → ADV ≤ 0, không mua được (mirror liquidity_require_positive)"},
        {"ticker": "ZZZ", "reason": "không có dòng giá nào trong 90 ngày gần nhất"},
    ], "lag_rating_excluded": [{"ticker": "AAV", "rating": 5, "reason": "RATING_FAIL 8L=5"}],
        "lag_forensic_excluded": [{"ticker": "VVS", "kind": "banned", "flag_date": None, "reason": "BANNED"}]}

    r1 = rows_from_status(st1)
    chk("rows_from_status: 5 dòng / 3 cổng", len(r1) == 5)
    kinds = {r["ticker"]: (r["reason_kind"], r["metric"]) for r in r1}
    chk("parse stale_adv -> 31", kinds["ATS"] == ("stale_adv", 31.0))
    chk("parse adv_zero -> 0.0", kinds["BTW"] == ("adv_zero", 0.0))
    chk("parse no_price_row", kinds["ZZZ"][0] == "no_price_row")
    chk("rating giữ nguyên hạng 5", kinds["AAV"] == ("rating_fail", 5))
    chk("forensic kind=banned", kinds["VVS"][0] == "banned")

    _, n1 = append_rows(r1, path)
    chk("lần ghi đầu: +5", n1 == 5)
    # IDEMPOTENCY — điểm quan trọng nhất: cron chạy lại/bị giết rồi chạy lại không được nhân đôi
    all2, n2 = append_rows(rows_from_status(st1), path)
    chk("chạy lại cùng phiên: +0 (idempotent)", n2 == 0 and len(all2) == 5)
    first_ts = {r["ticker"]: r["first_seen_ts"] for r in all2}
    chk("first_seen_ts của dòng cũ KHÔNG bị ghi đè",
        first_ts["ATS"] == [r for r in r1 if r["ticker"] == "ATS"][0]["first_seen_ts"])

    # Phiên mới: CÙNG ticker, ngày khác -> phải là dòng mới (khoá gồm signal_date)
    st2 = dict(st1, signal_date="2026-08-03")
    all3, n3 = append_rows(rows_from_status(st2), path)
    chk("phiên mới cùng mã: +5 (khoá gồm signal_date)", n3 == 5 and len(all3) == 10)

    # Cùng ticker bị 2 cổng khác nhau chặn -> 2 dòng riêng, không nuốt mất
    st3 = {"signal_date": "2026-08-04",
           "lag_liq_excluded": [{"ticker": "QQQ", "reason": "Volume_3M_P50=0.0 → ADV ≤ 0"}],
           "lag_rating_excluded": [{"ticker": "QQQ", "rating": 4, "reason": "RATING_FAIL 8L=4"}]}
    all4, n4 = append_rows(rows_from_status(st3), path)
    chk("cùng mã 2 cổng khác nhau -> 2 dòng", n4 == 2)

    # Không có signal_date -> không sinh dòng rác
    chk("thiếu signal_date -> 0 dòng", rows_from_status({"lag_liq_excluded": [{"ticker": "X", "reason": "r"}]}) == [])
    # Danh sách rỗng / thiếu key -> 0 dòng (phiên sạch là bình thường)
    chk("phiên không loại mã nào -> 0 dòng", rows_from_status({"signal_date": "2026-08-05"}) == [])

    # Đọc lại từ đĩa: header + số dòng đúng
    back = read_ledger(path)
    chk("đọc lại từ đĩa khớp", len(back) == 12 and set(back[0].keys()) == set(FIELDS))

    # main() fail-soft khi status không tồn tại
    global STATUS
    _save = STATUS
    STATUS = os.path.join(tmpd, "khong_ton_tai.json")
    try:
        chk("main() fail-soft khi thiếu status (return 0, không raise)", main() == 0)
    finally:
        STATUS = _save

    shutil.rmtree(tmpd, ignore_errors=True)
    print("SELFCHECK:", "ALL PASS" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_selfcheck() if "--selfcheck" in sys.argv else main())
