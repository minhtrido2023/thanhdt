# -*- coding: utf-8 -*-
"""lag_rating_filter.py — GATE CỨNG chất lượng (8L rating) cho book LAG.

CHÍNH SÁCH (user chốt 2026-07-27, sau 2 case liên tiếp TRC rating=4/D rồi MST rating=4/E):
mọi ứng viên LAG PHẢI có 8L rating ≤ 3 mới được đưa vào danh sách khuyến nghị. Rating ≥ 4
(RATING_FAIL) → TỰ ĐỘNG LOẠI THẬT khỏi output — KHÔNG chỉ gắn cờ, KHÔNG escalate từng ca nữa
(khác quy tắc trước 07-27). DollarBill/Mafee do đó không còn thấy các mã này như "candidate chờ
quyết định".

⚠️ ĐÁNH ĐỔI ĐÃ BIẾT, USER ĐÃ DUYỆT: backtest cùng ngày (job Taylor_20260723_131958) test đúng
biến thể "gate rating≤3 chặn cứng cho LAG" và kết quả NO-GO ở cấp trung bình lịch sử (IS-negative,
Sharpe 0,95→0,80). Đây là quyết định risk-tolerance — đánh đổi hiệu suất đo được trong backtest để
lấy bảo vệ khỏi rủi ro cá biệt (mã chất lượng rất kém dù tín hiệu PEAD kích hoạt). KHÔNG tự ý đảo
ngược bằng backtest cũ — xem context_planning_mini.md "LAG entry — GATE CỨNG rating≤3".

PHẠM VI = CHỈ book LAG (LAG_HI/LAG_LO). BAL/CAPIT/custom30V có gate rating riêng đang chạy đúng,
KHÔNG đụng tới (BAL: "weak" half-size ở BEAR/CRISIS; golden-floor ROE_Min3Y≥0 ∧ CF_OA_3Y>0).

Nguồn: `tav2_bq.fa_ratings_8l` (cột `rating`, 1..8; golden gate ≤3). Point-in-time: lấy dòng
rating MỚI NHẤT có `time ≤ asof` — không look-ahead sang rating gán SAU ngày tín hiệu (bắt buộc
cho replay lịch sử; với run LIVE asof≈hôm nay nên trùng snapshot mới nhất).

FAIL-SAFE:
  · TỪNG MÃ đo được rating ≥ 4 → LOẠI (fail-closed, đúng ý định gate).
  · TỪNG MÃ KHÔNG có rating nào ≤ asof → LOẠI (fail-closed: "PHẢI CÓ rating≤3 mới được vào" ⇒
    không xác nhận được ≤3 thì loại). Thực tế coverage fa_ratings_8l trên universe LAG = 100%
    (đo 2026-07-27: 0/160 mã thiếu rating), nên nhánh này gần như không kích hoạt — giữ cho đúng
    ý định, không phải vì hay gặp.
  · CẢ TRUY VẤN hỏng (BQ lỗi) → GIỮ NGUYÊN danh sách + WARNING (fail-open), trả error string để
    status.json phân biệt "không có mã nào rating≥4" vs "gate không chạy được". Chặn sạch book LAG
    vì một lỗi mạng thiệt hại lớn hơn; và recommender đã nạp thành công `fa_ratings_8l` ở bước BAL
    (regime_size) TRƯỚC khi tới đây, nên một lỗi truy vấn thứ hai trên cùng bảng là hiếm/thoáng
    qua. LƯU Ý: từ 2026-07-29 gate NÀY có lưới an toàn ở executor
    (`trading_bot.plan.filter_lag_rating_orders`, gọi trong cascade bot_execute.py) áp CÙNG hàm
    này lên từng order LAG-buy của plan — nhưng lưới đó fail-OPEN theo đúng nguyên tắc trên, nên
    lag_rating_filter_error != None VẪN phải được người đọc status/plan để ý.

Consumer: deploy_golive_dt5g_v4/golive_recommend_v23.py.
Self-check: lag_rating_filter_selfcheck.py
Cờ CẢNH BÁO-only `lag_rating_stale` (rating cũ hơn BCTC của sự kiện, 2026-10-13) ở cuối file;
self-check: lag_rating_stale_selfcheck.py.
"""
import pandas as pd

RATING_MAX_OK = 3        # 8L rating ≤ 3 = QUALIFY; ≥ 4 = RATING_FAIL (auto-exclude)
POLICY_TAG = "auto-excluded per user policy 2026-07-27"


def lag_filter_low_rating(bq, cand, asof, rating_max_ok=RATING_MAX_OK):
    """Loại ứng viên LAG có 8L rating ≥ rating_max_ok+1 (mặc định ≥4), point-in-time ≤ asof.

    Trả (cand đã lọc, list dict mô tả mã bị loại, lỗi-nguồn|None). Mỗi dict mã bị loại có
    {"ticker", "rating" (int|None), "reason"}.
    """
    if cand is None or not len(cand):
        return cand, [], None
    tks = sorted(set(cand["ticker"]))
    asof_d = pd.Timestamp(asof).date()
    try:
        tl = ",".join(f"'{t}'" for t in tks)
        a = bq(f"""SELECT f.ticker, f.rating, f.time
FROM tav2_bq.fa_ratings_8l AS f
WHERE f.ticker IN ({tl}) AND f.time <= DATE '{asof_d}'
QUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) = 1""")
    except Exception as ex:
        print(f"  WARNING: không đọc được 8L rating cho ứng viên LAG ({ex}) — GIỮ nguyên danh "
              f"sách (fail-open). LƯU Ý: lưới executor (filter_lag_rating_orders) cũng fail-open "
              f"khi nguồn hỏng, xem lag_rating_filter_error trong status.json")
        return cand, [], f"{type(ex).__name__}: {ex}"
    rmap = {r.ticker: r.rating for r in a.itertuples()} if len(a) else {}
    dropped = []
    for tk in tks:
        rt = rmap.get(tk)
        if rt is None or pd.isna(rt):
            dropped.append({"ticker": tk, "rating": None,
                            "reason": f"RATING_FAIL — không có 8L rating ≤ {asof_d}, không xác "
                                      f"nhận được rating≤{rating_max_ok} ({POLICY_TAG})"})
            continue
        if float(rt) >= rating_max_ok + 1:
            dropped.append({"ticker": tk, "rating": int(rt),
                            "reason": f"RATING_FAIL 8L={int(rt)} (≥{rating_max_ok+1}) ({POLICY_TAG})"})
    if dropped:
        bad = {d["ticker"] for d in dropped}
        cand = cand[~cand["ticker"].isin(bad)].copy()
    return cand, dropped, None


# ─────────────────────────────────────────────────────────────────────────────────────────────
# CỜ CẢNH BÁO `lag_rating_stale` (user duyệt 2026-10-13, job Taylor_20261013_125149, finding M1(b)
# của audit sẵn sàng BCTC Q3). CHỈ CẢNH BÁO — KHÔNG lọc, KHÔNG đổi `cand`, KHÔNG đổi quyết định
# của cổng 8L ≤ 3 ở trên (user chốt 07-27, giữ nguyên). Siết thành fail-closed = việc của user sau
# khi đo thêm 1 mùa.
#
# Vấn đề: `fa_ratings_8l.time` = eff_date = Release_Date của BCTC mà dòng rating được dựng từ đó
# (rating_8l_history.py). Cổng ở trên lấy dòng rating MỚI NHẤT ≤ asof mà không kiểm dòng đó có
# được dựng từ BCTC của CHÍNH sự kiện LAG đang xét hay không. Lúc lập plan, nếu re-rate chưa chạy
# sau khi mã công bố thì dòng mới nhất là của QUÝ TRƯỚC ⇒ time < Release_Date của sự kiện ⇒ cổng
# đang chấm bằng rating cũ (mùa Q2/2026: 28/117 sự kiện qualify, 5 ca đổi phía cổng, ca thật TVN).
#
# ⚠️ Cờ này CHỈ có nghĩa ở lượt chạy LIVE. Replay lịch sử KHÔNG tái hiện được: dòng rating của quý
# mới được đóng dấu time = Release_Date dù được ghi vào bảng muộn hơn nhiều ngày, nên bảng hôm nay
# trông như lúc nào cũng tươi.
# ⚠️ Truy vấn riêng (lặp lại đúng SQL của cổng) thay vì dùng chung kết quả: để `lag_filter_low_rating`
# không bị sửa một dòng nào. Giá = 1 truy vấn nhỏ/lượt chạy.
# ─────────────────────────────────────────────────────────────────────────────────────────────
STALE_LIST_MAX = 12      # số mã tối đa in ra trong 1 dòng cảnh báo (phần còn lại gộp "…")


def lag_rating_stale_flags(bq, cand, asof, rating_max_ok=RATING_MAX_OK):
    """Liệt kê sự kiện LAG mà dòng 8L rating mới nhất ≤ asof có `time` < Release_Date của sự kiện.

    Gọi trên `cand` TRƯỚC cổng 8L để thấy cả hai phía: mã cổng cho qua bằng rating cũ ("PASS") và
    mã cổng loại bằng rating cũ ("RATING_FAIL"). Mã KHÔNG có dòng rating nào thì không gắn cờ ở
    đây (cổng đã loại fail-closed với lý do riêng, "cũ" không có nghĩa).

    Trả (list dict, lỗi|None). Mỗi dict: {"ticker", "rating" (int|None), "rating_date",
    "release_date", "gate" ("PASS"|"RATING_FAIL")}. KHÔNG bao giờ raise và KHÔNG đụng `cand`:
    lỗi bất kỳ ⇒ ([], chuỗi lỗi) để status.json phân biệt "không có mã nào cũ" với "không kiểm được".
    """
    try:
        if cand is None or not len(cand):
            return [], None
        if "ticker" not in cand.columns or "Release_Date" not in cand.columns:
            return [], "cand thiếu cột ticker/Release_Date — không kiểm được rating cũ"
        tks = sorted(set(cand["ticker"]))
        asof_d = pd.Timestamp(asof).date()
        tl = ",".join(f"'{t}'" for t in tks)
        a = bq(f"""SELECT f.ticker, f.rating, f.time
FROM tav2_bq.fa_ratings_8l AS f
WHERE f.ticker IN ({tl}) AND f.time <= DATE '{asof_d}'
QUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) = 1""")
        rmap = {r.ticker: (r.rating, r.time) for r in a.itertuples()} if len(a) else {}
        flags, seen = [], set()
        for tk, rel in zip(cand["ticker"], cand["Release_Date"]):
            rel_ts = pd.to_datetime(rel, errors="coerce")
            if tk not in rmap or pd.isna(rel_ts):
                continue
            rt, rtime = rmap[tk]
            rtime_ts = pd.to_datetime(rtime, errors="coerce")
            if pd.isna(rtime_ts):
                continue
            rel_d, rating_d = rel_ts.date(), rtime_ts.date()
            if not rating_d < rel_d or (tk, rel_d) in seen:
                continue
            seen.add((tk, rel_d))
            has_rt = rt is not None and not pd.isna(rt)
            flags.append({"ticker": tk, "rating": int(rt) if has_rt else None,
                          "rating_date": str(rating_d), "release_date": str(rel_d),
                          "gate": "PASS" if has_rt and float(rt) < rating_max_ok + 1 else "RATING_FAIL"})
        flags.sort(key=lambda f: (f["release_date"], f["ticker"]))
        return flags, None
    except Exception as ex:
        return [], f"{type(ex).__name__}: {ex}"


def annotate_stale_status(flags, lag_up, lag_recent):
    """Gắn `status` (UPCOMING …/WINDOW_PASSED …/None) cho từng cờ theo đúng 2 danh sách mà plan
    hiển thị. Khớp theo (ticker, release). Chỉ ghi thêm khoá vào dict cờ; không đụng lag_up/lag_recent.
    """
    try:
        shown = {}
        for label, items in (("UPCOMING", lag_up), ("WINDOW_PASSED", lag_recent)):
            for it in items or []:
                shown[(it["ticker"], str(it["release"]))] = f"{label} {it['entry']}"
        for f in flags or []:
            f["status"] = shown.get((f["ticker"], f["release_date"]))
    except Exception:
        for f in (flags if isinstance(flags, list) else []):
            if isinstance(f, dict):
                f.setdefault("status", None)
    return flags


def format_lag_rating_stale_line(flags, error=None, html=False):
    """MỘT dòng cảnh báo cho plan/recommend; "" khi không có gì để báo. Không bao giờ raise."""
    try:
        b0, b1 = ("<b>", "</b>") if html else ("**", "**")
        esc = (lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")) if html else str
        if error:
            return (f"⚠️ {b0}lag_rating_stale KHÔNG kiểm được{b1} ({esc(error)}) — không biết cổng 8L≤3 có "
                    f"đang chấm bằng rating quý trước hay không; quyết định lọc KHÔNG đổi.")
        flags = list(flags or [])
        if not flags:
            return ""

        def _fmt(fs):
            head = ", ".join(
                f"{esc(f['ticker'])} (8L={f['rating'] if f.get('rating') is not None else '?'} chấm "
                f"{esc(f['rating_date'])}, trước BCTC {esc(f['release_date'])}"
                + (f", {esc(f['status'])}" if f.get("status") else "") + ")"
                for f in fs[:STALE_LIST_MAX])
            return head + (f" … (+{len(fs) - STALE_LIST_MAX})" if len(fs) > STALE_LIST_MAX else "")

        shown = [f for f in flags if f.get("gate") == "PASS" and f.get("status")]
        failed = [f for f in flags if f.get("gate") != "PASS"]
        other = len(flags) - len(shown) - len(failed)
        parts = []
        if shown:
            parts.append(f"cổng CHO QUA bằng rating quý trước: {_fmt(shown)}")
        if failed:
            parts.append(f"cổng LOẠI bằng rating quý trước: {_fmt(failed)}")
        if other:
            parts.append(f"+{other} sự kiện ngoài cửa sổ entry")
        return (f"⚠️ {b0}lag_rating_stale{b1} — rating 8L CŨ hơn BCTC của sự kiện (CHỈ CẢNH BÁO, không "
                f"loại/thêm lệnh nào; cổng 8L≤3 giữ nguyên): " + " · ".join(parts)
                + ". Kiểm lại sau lượt re-rate 20:00 trước khi duyệt.")
    except Exception as ex:
        return f"⚠️ lag_rating_stale: không dựng được dòng cảnh báo ({type(ex).__name__})"
