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
    simulate_holistic_nav.py:1174) thì KHÔNG giữ vốn: mã bị chặn không chiếm chỗ. Lọc ở đây =
    mã đó KHÔNG BAO GIỜ thành mục tiêu ⇒ sổ live không rót vốn vào nhóm mã không mua được,
    đúng như engine mô phỏng. Bộ lọc GIỮ VÔ ĐIỀU KIỆN (không mua được thì đừng đặt mục tiêu) —
    câu đó độc lập với mọi tranh cãi về con số dưới đây.

    ⚠️ CƠ CHẾ ĐÚNG = "KHÔNG RÓT VỐN VÀO RỔ LỖ", **KHÔNG PHẢI** "vốn quay vòng nhanh hơn"
    (đo 2026-08-03, job Taylor_20260803_021414, phép thử T3 = phân rã sổ lệnh của chính 2 CSV
    audit A/B, không chạy backtest mới. Đây là lần đính chính THỨ BA cho cơ chế module này):
      · **Vòng quay vốn CHẬM HƠN** ở chân đã sửa: **5,62x/năm (L1) vs 6,28x/năm (L0)**. ⇒ mọi
        cách diễn đạt kiểu "vốn quay/chảy sang các event LAG kế tiếp (nhanh hơn)" — từng nằm
        đúng chỗ này — là SAI, đã gỡ.
      · Δ đến từ **lợi nhuận mỗi CHU KỲ triển khai vốn**: 3,549% (L0) → 4,582% (L1) = +1,03pp.
      · **81%** của +1,03pp chỉ là do **KHÔNG rót vốn vào 58 mã bị chặn** — nhóm này ở L0 hút
        **1.690B** vốn luỹ kế (106 vị thế) để sinh **−1,77%/chu kỳ**. 19% còn lại mới là
        "chất lượng của vốn thay thế".
      · Ràng buộc cộng đã kiểm: `(1+4,582%)^70 / (1+3,549%)^78 = 1,51x` vs tỷ lệ NAV cuối thực
        đo **1,48x** (khớp trong 2%) ⇒ phân rã giải thích gần trọn Δ, không phải kể chuyện.
      · Nghịch lý biểu kiến đã giải: L1 bỏ dở NHIỀU hơn (63,7% vs 48,5%) mà vẫn lời hơn, vì
        ABANDONED_REFUND hoàn tiền về sổ (P&L nhóm bỏ dở chỉ 4,2B/12,3B) ⇒ tỷ lệ bỏ dở là
        TRIỆU CHỨNG, không phải nguyên nhân của Δ.

    ⚠️ NHÃN CỦA SỐ PIN — ĐỔI 2026-08-03 (job Taylor_20260803_045138 phép thử T5, quant-skeptic
    CONFIRMED cao). Số pin **KHÔNG còn là "CẬN DƯỚI có thiên lệch đã biết"**. Nó là **ƯỚC LƯỢNG
    ĐIỂM CÓ ĐIỀU KIỆN** vào một tham số mô hình **chưa được neo**: trần fill %ADV/phiên
    (`liquidity_volume_pct` = 0,20 = 20%ADV, đo được là **bind ~90% số phiên-fill**). Lý do bỏ
    nhãn cận dưới: tồn tại ĐÚNG HAI thiên lệch đã biết, **NGƯỢC CHIỀU, cùng bậc độ lớn**:
      (A) LÊN — L0 rót vốn vào nhóm mã live không mua được: **+4,08pp** (L0→L1 tại pct=0,20).
      (B) XUỐNG — cả hai chân giả định fill tới 20%ADV/phiên, trong khi fill THẬT của DNSE
          (T4, 07-01→08-03) chỉ xác nhận tới **3,86%ADV/phiên**: L1@0,20 → L1@0,05 = **−4,50pp**.
      Áp CẢ HAI: L1 @ pct=0,05 = **26,82%** vs chân đối chứng L0 @ pct=0,20 = **27,24%** ⇒
      **−0,42pp: hai thiên lệch GẦN TRIỆT TIÊU NHAU.** (Số (A)/(B) trên đo ở cơ sở ADV `close`
      nên chân đối chứng là 27,24%.)
      ĐÃ GHÉP LẠI Ở CƠ SỞ `price` — cơ sở của pin chính thức 28,86% (job Taylor_20260803_052705,
      `T1_PRICE_RESULTS.md`; chân L0@0,20 tái lập ĐÚNG 28,86% và L1@0,20 đúng 32,71%, self-check
      0 VND cả 6 chân): (A) = **+3,85pp**, (B) = **−3,53pp**, áp CẢ HAI ⇒ L1@0,05 = **29,18%** vs
      pin **28,86%** = **+0,32pp**. Tức ở CẢ HAI cơ sở giá, áp đồng thời hai thiên lệch cho một số
      **cách chân pin < 0,5pp**, và **dấu của phần dư ĐỔI CHIỀU** (−0,42 → +0,32) ⇒ phần dư nằm
      trong nhiễu, không phải hiệu ứng có hướng. Hình dạng thang (Δ tăng đơn điệu khi nới capacity)
      giữ nguyên ở cả hai cơ sở ⇒ kết luận CƠ CHẾ không phụ thuộc cơ sở giá.
    ⇒ **ĐỌC SỐ PIN KHÔNG THEO CHIỀU NÀO** — không cận dưới, không cận trên. KHÔNG trích
    +4,08/+4,11pp như edge; KHÔNG re-pin LÊN; cũng KHÔNG re-pin XUỐNG (3,86% là **cận dưới đã
    xác nhận** của khả năng fill, không phải ước lượng khả năng fill thật: mẫu chệch có hệ thống
    vì `cap_lag_orders` CẤM đặt lệnh lớn hơn ⇒ vắng bằng chứng ở 20% KHÔNG PHẢI bằng chứng vắng
    mặt). Khoảng **[~27,2%; 31,3%]** từng ghi ở đây đã **HẾT HIỆU LỰC** và **không có khoảng
    thay thế**. Sổ theo dõi + 2 mốc cứng để đóng câu hỏi MỨC (checkpoint **2026-12-15**, rà soát
    đầy đủ **2027-03-31**): `mike/kb/projects/lag-adv-filter-tracking.md`. Engine giữ
    `LIQ_ZERO_BLOCK=""` (opt-in) cho tới khi MỨC được hiệu chuẩn.

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
        ⚠️ Đọc "nhả vốn cho ứng viên kế tiếp" ĐÚNG NGHĨA HẸP: ràng buộc thường trực là VỐN
        (đúng, đo được), NHƯNG tổng hiệu ứng KHÔNG đến từ vốn quay vòng nhanh hơn — T3 đo
        vòng quay GIẢM (6,28 → 5,62x/năm). Xem khối "CƠ CHẾ ĐÚNG" ở trên.

    ĐÃ TÁCH ĐƯỢC **CƠ CHẾ**, CHƯA HIỆU CHUẨN ĐƯỢC **MỨC** (cập nhật 2026-08-03 sau T1–T5; thay
    cho mục "CHƯA PHÂN RÃ ĐƯỢC +4,11pp" của bản trước):
      · Giả thuyết H_B — "Δ là hiện vật capacity: sổ ở quy mô này đơn giản KHÔNG fill nổi mã LAG"
        — **ĐÃ BỊ BÁC BỎ HAI LẦN bằng hai knob TRỰC GIAO, cả hai lần bằng SAI DẤU đạo hàm**:
        (T1) nới trần %ADV/phiên 20x ⇒ Δ **TĂNG** đơn điệu +2,51 → +4,08 → +5,20pp;
        (T2) hạ NAV 10x (50B→5B) ⇒ Δ đạt **CỰC ĐẠI +5,48pp ở đầu 5B**. H_B đòi Δ teo về ≤+0,5pp
        ở cả hai đầu lỏng. Manipulation check của cả hai thang đơn điệu đúng chiều (abandoned%
        L0 56,8→34,6% theo %ADV; 30,2→54,5% theo NAV) ⇒ can thiệp có ăn, phép thử không vô hiệu.
      · Cộng lập luận thẳng từ code: `liquidity_require_positive` **CHỈ** biến một `daily_max`
        VÔ HẠN thành 0, không bao giờ nới ⇒ L1 là **siết chặt nghiêm ngặt** của L0, và một hiện
        vật kiểu "mô hình fill quá dễ dãi" **không thể** sinh ra từ chân bị siết chặt hơn.
      · **Còn MỞ = MỨC.** Cả hai chân dùng chung một mô hình fill (%ADV/ngày) chưa neo vào fill
        thật; T4 đo được lệnh live chưa bao giờ vượt 3,86%ADV/phiên (cận dưới, mẫu chệch). ⇒
        không con số nào của A/B này được đọc như kỳ vọng live — xem "NHÃN CỦA SỐ PIN" ở trên.
      · Bằng chứng đầy đủ: `mike/agents/Taylor/research/lag_fidelity_decomp_20260803/`
        (README.md, T1/T2/T4_RESULTS.md, T5_DECISION.md).

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
