# Phase B — V2.4 cấp cổ phiếu qua cụm cơ cấu 2007-2012: SỐNG SÓT BẰNG TRÁNH NÉ, KHÔNG PHẢI HẤP THỤ

Job Taylor_20260830_114100. **KHÔNG chạy backtest mới** — tái dùng backtest V2.4 full-window
2008-2026 đã có (`agents/Taylor/research/backtest_2008_v24_20260825.md`, job
`Taylor_20260825_055651`+`_074227`, **quant-skeptic CONFIRMED (medium confidence)**,
`mike/bus/inbox/quant-skeptic.jsonl` topic `VERIFY: backtest-2008-v24-full`, 2026-08-25T07:29:46Z),
đào sâu thêm đúng câu hỏi dispatch hôm nay (drawdown/recovery-time/stuck-state trong RIÊNG cụm
2007-2012) từ chính audit CSV đã self-check 0 VND của job đó — không phải số mới chưa kiểm chứng.

## 1. Điểm bắt đầu — đã đúng như đề xuất, không cần chạy lại
Backtest 08-25 đã dùng `AUDIT_START=2008-01-01` (universe `universe_pit`, NAV 50B = 25B BAL +
25B LAG, `capit_margin_lever` f=1.3 production), rất gần khuyến nghị dispatch hôm nay (~2008-2009,
tránh 2007-04 vì phục hồi +130% đó là global-GFC-recovery, không phải VN tự xử lý). Universe_pit
2008 = 204 tên (đo lại hôm nay, đủ lớn theo tiêu chí CLAUDE.md ~105-204 tên tuỳ bảng).

## 2. LAG data coverage đầu giai đoạn — ĐÃ được backtest 08-25 lường trước và ghi rõ
`ticker_financial.Release_Date`: 2009 = 1.225 lượt/362 mã, 2013 = 2.431 lượt/626 mã (~1/2 mật độ).
8L rating composite value-lens PCF/PS coverage ~0% giai đoạn 2008-2012 (chỉ nhánh 1/PE hoạt động
— `backtest_pre2014_feasibility_20260825.md`). Đây là GIỚI HẠN DỮ LIỆU THẬT, không phải giả định
— đã kiểm bằng query BQ trực tiếp, không suy đoán.

## 3. Walk-forward RIÊNG cụm 2007-01→2012-12 (đào mới từ audit CSV đã verify, KHÔNG chạy lại)
Nguồn: `data/v23_golive_audit_2014_now_..._exp_scenarioB_production_univpit_from20080101.csv`
(record_type=DAILY, 1.248 phiên trong cửa sổ; cột `combined_nav`, `(bal|lag)_(stocks|etf)_ref`,
`nav_(bal|lag)_ref`, `state`).

**Invested fraction (tỷ lệ vốn thực sự có vị thế cổ phiếu/ETF, không phải tiền mặt/park):**
- Toàn cụm: chỉ **122/1.248 phiên (9,8%)** có BẤT KỲ book nào >1% invested. TOÀN BỘ tập trung
  đúng **2 cửa sổ**: **2010-08-10 → 2010-11-04** (cả BAL lẫn LAG lên tới ~62-64% sách, trùng
  đúng nhịp NEUTRAL ngắn giữa 2 đợt BEAR sóng 2/3 mà Phase A xác định) và **2012-08-24 →
  2012-11-19** (chỉ LAG, lên ~50%, BAL = 0% suốt). **2008, 2009, 2011 — invested = 0,000 TUYỆT
  ĐỐI cả 2 book, không một phiên nào ngoại lệ** — kể cả 2009 khi VNI +57,9% (đã ghi trong
  backtest 08-25) và kể cả những đoạn state=NEUTRAL trong các năm đó.
- Yearly return hệ thống trong 4/5 năm gần như đúng 0,00% (0% lãi tiền gửi nhàn rỗi theo quy ước
  backtest, KHÔNG phải bug) — trong khi VNI dao động −65,7% (2008) → +57,9% (2009) → −27,7%
  (2011). Hệ thống hoàn toàn ĐỨNG NGOÀI các đợt biến động lớn nhất.

**Drawdown/recovery — chỉ có 1 cửa sổ đủ vị thế để đo:**
- MaxDD combined_nav toàn cụm 2007-2012 = **−7,86%**, xảy ra **2010-08-25** — đúng bên trong cửa
  sổ đầu tư duy nhất có ý nghĩa (Aug-Nov 2010), KHÔNG phải trong đáy GFC (2008 Q4) hay đỉnh lạm
  phát 2011 như trực giác kỳ vọng.
- Recovery: từ đáy 46,07B (2010-08-25) về lại đỉnh cũ 50,00B chỉ mất **12 ngày lịch** (2010-09-06)
  — nhanh, vì bản thân drawdown quá nhỏ để cần "phục hồi" theo nghĩa thông thường.
- Tổng lợi nhuận cả cụm 2007-01→2012-12 (5 năm): **+1,49%** — bảo toàn vốn gần như tuyệt đối,
  KHÔNG tăng trưởng.

## 4. Trả lời trực tiếp câu hỏi "hệ có sống sót/thích nghi qua khủng hoảng cơ cấu không"

**Có sống sót — nhưng bằng cơ chế TRÁNH NÉ (avoidance), không phải HẤP THỤ (absorption).**
V2.4 không hề "chịu đòn rồi phục hồi" qua cụm 2007-2012 — nó gần như không có mặt trên thị
trường 90,2% số phiên trong 6 năm đó, nên không có tổn thất thật để đo khả năng phục hồi. Đây
CHÍNH LÀ cơ chế bảo vệ được xác nhận ở Phase A (DT4 chưa từng đạt state 4/5 BULL/EXBULL trong cả
2008-2013, và `signal_v11_sql.py` gate cứng các tier momentum mạnh nhất vào state∈{4,5} —
`backtest_2008_v24_20260825.md` mục "PHÁT HIỆN QUAN TRỌNG NHẤT"). Không có "stuck ở trạng thái
xấu quá lâu" theo nghĩa thua lỗ kéo dài — có "stuck ở CASH quá lâu" theo nghĩa cơ hội (bỏ lỡ toàn
bộ nhịp hồi 2009 +57,9%), đánh đổi được ghi nhận, không phải bug.

**Hệ quả cho câu hỏi ban đầu (survivorship bias risk từ Phase B context):** vì hệ hầu như không
tham gia thị trường trong đúng giai đoạn có rủi ro huỷ niêm yết cao nhất (2008-2012), golden-floor
gate của 8L (ROE_Min3Y≥0 ∧ CF_OA_3Y>0) gần như KHÔNG có cơ hội thể hiện tác dụng lọc mã sắp huỷ
niêm yết trong cụm này — không phải vì gate sai, mà vì SIGNAL_V11/LAG chưa từng chọn đủ mã để gate
đó phát huy. Điều này làm giả định "gate lọc mã sắp huỷ niêm yết trước khi huỷ" gần như KHÔNG
kiểm chứng được bằng chính cửa sổ 2007-2012 — nhất quán với hạn chế đã nêu trong dispatch (BQ
không giữ dữ liệu cơ bản mã đã huỷ niêm yết nên không thể kiểm ngược).

## 5. Trung thực về giới hạn dữ liệu (không tự nhận "đại diện" khi dữ liệu mỏng)
- 8L composite 2008-2012 chỉ có nhánh 1/PE hoạt động (PCF/PS coverage ~0%) — bất kỳ mã nào lọt
  qua gate trong cửa sổ HIẾM HOI có vị thế (Aug-Nov 2010/2012) được chọn bởi 1 nhánh giá trị
  không đầy đủ như production hiện tại.
- LAG (PEAD) density ~50% của mức 2013 trong 2009 — số lượng ứng viên PEAD giai đoạn đầu THỰC SỰ
  mỏng, không chỉ do gate `prior_n_good>=4` nghiêm mà còn do nguồn Release_Date thưa.
- Universe_pit 204 tên (2008) đủ tiêu chí "đủ lớn" theo CLAUDE.md nhưng vẫn ~1/2 quy mô 2014
  (203 → 427 tên đến 2010) — kết luận rút ra từ cụm 2007-2012 có N hiệu dụng RẤT NHỎ (chỉ 2 cửa
  sổ đầu tư thật trong 6 năm) và KHÔNG nên coi là đại diện thống kê cho hành vi V2.4 nói chung.

## Không đề xuất thay đổi production
Đúng phạm vi dispatch — audit hành vi độ bền, không tuning tham số, không claim CAGR đẹp/xấu.
Nếu kết luận này sau này được dùng làm cơ sở cho quyết định wire/thay đổi bất kỳ gì → cần
quant-skeptic pass RIÊNG cho phần phân tích drawdown/invested-fraction mới này (backtest gốc đã
verified, nhưng lát cắt drill-down này là phái sinh mới, chưa được review độc lập).

## File liên quan
- Backtest gốc (đã verify): `agents/Taylor/research/backtest_2008_v24_20260825.md` +
  `agents/Taylor/research/backtest_2008_v24_20260825/engine_2008.py`.
- Audit CSV nguồn cho drill-down này:
  `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_scenarioB_production_univpit_from20080101.csv`
  (record_type=DAILY, cột combined_nav/nav_bal_ref/nav_lag_ref/bal_*_ref/lag_*_ref/state).
- Phase A (cùng job hôm nay): `research/crisis_stress_dt5g_2007_2012_20260830.md`.
