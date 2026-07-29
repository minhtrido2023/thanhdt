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
