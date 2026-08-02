# -*- coding: utf-8 -*-
"""lag_liquidity_filter.py — bộ lọc thanh khoản TẦNG TÍN HIỆU cho book LAG.

Module riêng (thay vì hàm nội trong golive_recommend_v23.py) để self-check được mà không
phải chạy cả script recommender; `bq` truyền vào như tham số — cùng mẫu với custom30.current.
Consumer: deploy_golive_dt5g_v4/golive_recommend_v23.py.
Self-check: lag_liq_signal_filter_selfcheck.py
"""
import pandas as pd

LAG_ADV_MAX_STALE_DAYS = 30   # = trading_bot/plan.py::LAG_ADV_MAX_STALE_DAYS (giữ 2 tầng cùng ngưỡng)
LOOKBACK_DAYS = 90            # cửa sổ quét dòng giá gần nhất (>> ngưỡng stale, chỉ để chặn full-scan)


def lag_filter_illiquid(bq, cand, asof, max_stale_days=LAG_ADV_MAX_STALE_DAYS):
    """Loại ứng viên LAG KHÔNG ĐO ĐƯỢC THANH KHOẢN (Volume_3M_P50 ≤ 0 / thiếu / quá cũ).

    VÌ SAO Ở TẦNG TÍN HIỆU, KHÔNG CHỈ Ở EXECUTOR (user quyết 2026-07-21, job
    Taylor_20260721_172103): gate `cap_lag_orders` (trading_bot/plan.py) chặn ĐÚNG các mã này
    ở tầng đặt lệnh, nhưng SỐ MỤC TIÊU của paper book mirror vẫn giữ mã đó ⇒ phần vốn ấy nằm
    im chờ một lệnh không bao giờ khớp. Engine backtest (`liquidity_require_positive`,
    simulate_holistic_nav.py:1174) thì KHÔNG giữ vốn: mã bị chặn không chiếm chỗ, vốn quay
    sang các event LAG kế tiếp — đó là nguồn của +4,11pp trong A/B contemporaneous
    27,22% → 31,33%. Lọc ở đây = mã đó KHÔNG BAO GIỜ thành mục tiêu ⇒ vốn tự chảy sang event
    kế tiếp đúng như engine mô phỏng. Đây là ĐIỀU KIỆN để kỳ vọng nằm ở PHẦN TRÊN của khoảng
    [~27,2%; 31,3%], KHÔNG phải cam kết đạt 31,33% (xem "còn lệch" dưới).
    ⚠️ CẬP NHẬT 2026-08-03 (job Taylor_20260802_175754): khoảng [~27,2%; 31,3%] nay HẾT HIỆU LỰC
    và KHÔNG có khoảng mới thay thế — A/B lại trên đúng vintage bị quant-skeptic chấm INCONCLUSIVE
    đúng vì lý do ghi ở "CHƯA PHÂN RÃ ĐƯỢC" bên dưới (lần thứ BA). Số dùng được duy nhất: pin R3
    27,24%, hiểu như CẬN DƯỚI. Engine để `LIQ_ZERO_BLOCK=""` (opt-in) cho tới khi phân rã xong.

    CƠ CHẾ THAY THẾ = CHỦ YẾU LÀ VỐN, thỉnh thoảng mới thêm slot (bản đo được, 2026-07-21;
    đây là lần đính chính THỨ HAI — cả hai cách diễn đạt trước đều bị quant-skeptic REFUTED:
    bản #1 nói "book LAG không có trần slot", bản #2 nói "trần 12 BIND ⇒ nhả cả slot lẫn vốn
    tức thì". Cả hai đều sai; số dưới đây là ĐO, không suy luận từ code đọc lướt):
      · Book LAG CÓ khai `max_positions=12` + `tier_position_limit={LAG_*: 12}`
        (pt_v23_audit_2014.py:1765/1769, pt_v22_dt5g.py:733).
      · `slot_exempt_tiers` CÓ được truyền trong đường chạy production (merge_extra
        pt_v23_audit_2014.py:1272, gọi ở :1802) nhưng chỉ chứa các tier CAPIT ⇒ LAG_HI/LAG_LO
        vẫn bị đếm. (Kết luận "LAG bị đếm" đúng, nhưng LÝ DO ở bản #2 — "không được truyền" —
        thì sai.)
      · Trần 12 là cổng RÒ: simulate_holistic_nav.py:1032-1037 chỉ kiểm tra tại `is_first_fill`
        và đếm `positions` (vị thế ĐÃ hoàn tất), nên cụm first-fill cùng ngày lọt qua. Đo lại
        vị thế LAG thực trong chính 2 lần chạy A/B (quant-skeptic dựng lại từ 2 CSV audit, loại
        pseudo-holding ABANDONED_REFUND): đỉnh đồng thời 17 (CTRL) / 16 (TREAT), trung bình
        5,85 / 4,89. CHẠM trần (≥12 — đúng ngưỡng cổng `_n_slots >= max_positions`, KHÔNG phải
        ">12", vốn chỉ là 23,5%/15,7%): 31,8% / 19,1% trên TOÀN BỘ 3.107 phiên, nhưng nếu chỉ
        tính phiên book THỰC SỰ có vị thế thì là 56,3% (CTRL) / 33,3% (TREAT).
      ⇒ Ràng buộc thường trực KHÔNG phải slot mà là VỐN (LAG_TW 0,10/0,08) — đo độc lập:
        ở đỉnh 17 vị thế (2016-10-28) book LAG còn 54.569 VND tiền mặt trên 52,8 tỷ cổ phiếu,
        và trung bình 96% đã giải ngân ở mọi phiên chạm ≥12. Một mã bị chặn nhả VỐN cho ứng
        viên kế tiếp; slot chỉ đóng góp thêm ở các phiên đang chạm trần (thiểu số nếu tính
        toàn kỳ, nhưng quá nửa số phiên hoạt động ở CTRL — đừng đọc là "hiếm").

    CHƯA PHÂN RÃ ĐƯỢC +4,11pp (nêu rõ để không ai trích dẫn nhầm): tỷ lệ giữa velocity-vốn /
    thay-slot / né-lỗ-trực-tiếp CHƯA đo. Một con số "~92% substitution, ~8% né lỗ" từng xuất
    hiện ở bản docstring trước — KHÔNG có phép đo nào chống lưng, đã gỡ. Đầu mối mạnh nhất cho
    lần đo sau (quant-skeptic chỉ ra): TREAT vào lệnh nhiều hơn +30,1% (1.652→2.149) nhưng vị
    thế HOÀN TẤT lại ít hơn −16,3% (674→564), tỷ lệ ABANDONED_REFUND 59,2% (CTRL) → 73,8%
    (TREAT). RỦI RO CÒN MỞ, phải nói thẳng: "vốn chảy sang event LAG kế tiếp" và "book đơn giản
    là KHÔNG fill nổi mã LAG ở quy mô 25B" để lại CÙNG một dấu vết trên CSV — chưa tách được.
    Nếu vế sau đúng thì +4,11pp là hiện vật của mô hình fill chứ không phải edge thật, và việc
    mirror bộ lọc sang live sẽ không mang lại gì. Bộ lọc này vẫn ĐÚNG về mặt logic (không mua
    được thì đừng đặt mục tiêu), nhưng ĐỪNG dùng +4,11pp làm cơ sở kỳ vọng cho tới khi tách xong.

    ⚠️ KHE HỞ LIVE CHƯA BỊT (phát hiện cùng lúc, KHÔNG tự sửa — đổi luật sizing production
    phải qua user): đường LIVE (script này + trading_bot/plan.py + strategies.py) KHÔNG có
    trần vị thế nào cho book LAG (`MAX_POS=12` trong golive_recommend_v23.py:346 chỉ áp cho
    BAL qua `select_book`). Backtest thì có trần — nhưng trần RÒ, nên mức thực tế cần mirror
    là ~16-17 vị thế LAG đồng thời, KHÔNG phải 12. Đây là độ lệch fidelity RIÊNG (không phải
    thứ bộ lọc này sinh ra); nếu sau này user duyệt mirror trần sang live thì phải neo vào con
    số đo được ở trên, đừng copy hằng số 12.

    ADV = `Volume_3M_P50 × COALESCE(Price, Close)` trên dòng MỚI NHẤT có time ≤ asof — đúng
    công thức engine (`pt_v23_audit_2014.py` `LAG_ADV_BASIS="price"`) và `cap_lag_orders`.
    ⚠️ CƠ SỞ GIÁ ĐỔI 2026-08-02 (job Taylor_20260802_163657), ĐỒNG THỜI ở cả 3 điểm live +
    engine để KHÔNG phá bất biến parity: `Volume_3M_P50` là số lượng CP THÔ (đo được
    `Trading_Value == Volume × Price` khớp 100% số dòng), nên nhân `Close` (đã điều chỉnh hồi
    tố) vừa sai độ lớn (~−7,4% median) vừa là look-ahead khi replay lịch sử. Ở CHÍNH tầng này
    ADV chỉ dùng cho phép thử `> 0` nên đổi cơ sở KHÔNG đổi kết quả lọc (cả hai giá đều dương
    cùng lúc); tác động thật nằm ở `cap_lag_orders` (độ lớn trần) và engine (tốc độ fill). Live không biết ADV của ngày vào
    lệnh (T+5 ở tương lai) nên dùng dòng gần nhất — nhân quả, và Volume_3M_P50 là trung vị 3
    tháng nên trễ vài phiên không đổi dấu. CÒN LỆCH so với engine (ghi nhận, không tự vá):
    engine tra ADV theo TỪNG NGÀY FILL, tầng này chốt một lần theo ngày tín hiệu.

    PHẠM VI = CHỈ book LAG (đo thật, không suy đoán — job Taylor_20260721_172103):
      · BAL  — SIGNAL_V11 đã có `WHERE liq >= 1e9` cứng (signal_v11_sql.py:143) ⇒ không thể lọt.
      · CAPIT — pool đã lọc `Price×Volume/1e9 >= 2`; đo 2014→2026-06: 0/26.277 dòng pool có
                Volume_3M_P50 ≤ 0. Ngoài ra `capit_adv_caps` đã fail-closed sẵn.
      · PARK (custom30V) — rổ xếp theo liq_rank; rổ hiện tại min ADV 13,1 tỷ/phiên.
    Áp thêm cho 3 book kia chỉ là code chết + rủi ro chặn nhầm ⇒ không áp.

    FAIL-SAFE HAI CHIỀU, CÓ CHỦ Ý:
      · TỪNG MÃ đo được mà ADV ≤ 0 / dòng quá cũ (> max_stale_days) → LOẠI (fail-closed,
        cùng chiều `cap_lag_orders`).
      · CẢ TRUY VẤN hỏng (BQ lỗi) → GIỮ NGUYÊN danh sách + WARNING (fail-open). Chặn sạch book
        LAG vì một lỗi mạng là thiệt hại lớn hơn nhiều, và lưới an toàn thật sự vẫn còn nguyên:
        `cap_lag_orders` ở executor fail-CLOSED nên không mã nào lọt thành lệnh mà ta không đo
        được thanh khoản. Tầng này tối ưu PHÂN BỔ VỐN, không phải tầng an toàn cuối.

    Trả (cand đã lọc, list dict mô tả mã bị loại, lỗi-nguồn|None).
    """
    if cand is None or not len(cand):
        return cand, [], None
    tks = sorted(set(cand["ticker"]))
    asof_d = pd.Timestamp(asof).date()
    try:
        tl = ",".join(f"'{t}'" for t in tks)
        a = bq(f"""SELECT t.ticker, t.time, t.Volume_3M_P50, COALESCE(t.Price, t.Close) AS px,
       t.Volume_3M_P50 * COALESCE(t.Price, t.Close) AS adv_vnd
FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({tl}) AND t.time <= DATE '{asof_d}'
  AND t.time >= DATE_SUB(DATE '{asof_d}', INTERVAL {LOOKBACK_DAYS} DAY)
QUALIFY ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) = 1""")
    except Exception as ex:
        print(f"  WARNING: không đọc được ADV cho ứng viên LAG ({ex}) — GIỮ nguyên danh sách "
              f"(executor cap_lag_orders vẫn fail-closed, không mã nào lọt thành lệnh)")
        return cand, [], f"{type(ex).__name__}: {ex}"
    rows = {r.ticker: r for r in a.itertuples()} if len(a) else {}
    dropped = []
    for tk in tks:
        r = rows.get(tk)
        if r is None:
            dropped.append({"ticker": tk,
                            "reason": f"không có dòng giá nào trong {LOOKBACK_DAYS} ngày gần nhất"})
            continue
        stale = (asof_d - pd.Timestamp(r.time).date()).days
        if stale > max_stale_days:
            dropped.append({"ticker": tk, "reason": f"dữ liệu ADV cũ {stale} ngày "
                            f"(> {max_stale_days}) — có thể ngừng giao dịch/huỷ niêm yết"})
            continue
        if not (pd.notna(r.adv_vnd) and float(r.adv_vnd) > 0):
            dropped.append({"ticker": tk, "reason": f"Volume_3M_P50={r.Volume_3M_P50} → ADV ≤ 0, "
                            f"không mua được (mirror liquidity_require_positive)"})
    if dropped:
        bad = {d["ticker"] for d in dropped}
        cand = cand[~cand["ticker"].isin(bad)].copy()
    return cand, dropped, None
