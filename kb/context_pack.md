# Mike fleet — context pack (v941)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-07-11T17:19:43] quant-skeptic/verification — ✅ CONFIRMED VERIFY: PLAN momentum-deals pattern discovery — scope xong, chờ user duyệt trước Phase 0: {"finding_topic": "PLAN momentum-deals pattern discovery — scope xong, chờ user duyệt trước Phase 0", "verdict": "CONFIRMED", "confidence": "high", "checks": {" …
- [2026-07-11T22:59:12] Taylor/finding — momdeal Phase 1 HOÀN TẤT — CP1 = NO-GO (0/13 feature qua gate pre-registered): thành công lịch sử kênh MOM chủ yếu là dồn mẫu regime 2020-21, không phải pattern lặp lại được — khuyến nghị đóng/thu hẹp kênh MOM, Phase 2 KHÔNG chạy: {"job": "Taylor_20260711_225135", "status": "PHASE1_DONE_CP1_NOGO", "plan_doc": "mike/agents/Taylor/plan_momentum_deals_20260711.md (section CP1 moi)", "script" …
- [2026-07-11T23:06:29] quant-skeptic/verification — ✅ CONFIRMED VERIFY: momdeal Phase 1 HOÀN TẤT — CP1 = NO-GO (0/13 feature qua gate pre-registered): thành công lịch sử kênh MOM chủ yếu là dồn mẫu regime 2020-21, không phải pattern lặp lại được — khuyến nghị đóng/thu hẹp kênh MOM, Phase 2 KHÔNG chạy: {"finding_topic": "momdeal Phase 1 CP1 = NO-GO (0/13 features pass pre-registered gate); historical MOM success is regime-concentrated 2020-21, not a repeatable …
- [2026-07-11T23:28:09] Taylor/finding — PLAN DVR-8L sizing (nhánh b) — scope xong, chờ user duyệt, chưa chạy backtest: {"job": "Taylor_20260711_232012", "status": "PLAN_DONE_PENDING_USER_APPROVAL", "plan_doc": "mike/agents/Taylor/plan_dvr_8l_sizing_20260712.md", "huong_chon": "S …
- [2026-07-12T01:10:13] Taylor/finding — CP-DVR1 KẾT QUẢ CHÍNH THỨC = NO-GO cả 3 rule — nhánh (b) đóng, toàn chuỗi momentum-deals ĐÓNG: {"job": "Taylor_20260712_010527", "status": "CPDVR1_CLOSED_NOGO", "plan_doc": "mike/agents/Taylor/plan_dvr_8l_sizing_20260712.md (section CP-DVR1 KET QUA)", "re …
- [2026-07-12T01:14:26] quant-skeptic/verification — ✅ CONFIRMED VERIFY: CP-DVR1 KẾT QUẢ CHÍNH THỨC = NO-GO cả 3 rule — nhánh (b) đóng, toàn chuỗi momentum-deals ĐÓNG: {"finding_topic": "CP-DVR1 KẾT QUẢ CHÍNH THỨC = NO-GO cả 3 rule — nhánh (b) đóng, toàn chuỗi momentum-deals ĐÓNG", "verdict": "CONFIRMED", "confidence": "high", …
- [2026-07-12T02:09:54] Taylor/finding — ĐO XONG tác động đóng kênh MOM (production scoping) — Scope A (−MOM_N,−MOM_S) = khuyến nghị ĐÓNG (governance, giá −0.97pp FULL nhưng hậu-2021 hoà-tới-dương); Scope B (đóng cả family) = BÁC bởi số đo, âm mọi cửa sổ — CHƯA sửa code sống, chờ user duyệt phạm vi: {"job": "Taylor_20260712_012515", "status": "MEASURE_DONE_PENDING_USER_SCOPE_APPROVAL", "plan_doc": "mike/agents/Taylor/plan_close_mom_20260712.md", "headline": …
- [2026-07-12T02:16:38] quant-skeptic/verification — ✅ CONFIRMED VERIFY: ĐO XONG tác động đóng kênh MOM (production scoping) — Scope A (−MOM_N,−MOM_S) = khuyến nghị ĐÓNG (governance, giá −0.97pp FULL nhưng hậu-2021 hoà-tới-dương); Scope B (đóng cả family) = BÁC bởi số đo, âm mọi cửa sổ — CHƯA sửa code sống, chờ user duyệt phạm vi: {"finding_topic": "ĐO XONG tác động đóng kênh MOM (production scoping) — Scope A (−MOM_N,−MOM_S) khuyến nghị ĐÓNG (governance, −0.97pp FULL / hậu-2021 hoà-tới-d …
<!--RECENT-END-->

# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-07-11

## Dự án momentum-deals ĐÓNG, user duyệt đóng kênh MOM — production change đang scope (2026-07-11/12)

Toàn chuỗi R&D đã đóng (Phase 1 CP1 NO-GO + nhánh (b) CP-DVR1 NO-GO, cả 2 quant-skeptic CONFIRMED —
xem `plan_momentum_deals_20260711.md` + `plan_dvr_8l_sizing_20260712.md`). **User duyệt đóng/thu hẹp
kênh MOM_N/MOM_S trong SIGNAL_V11 (production V2.4/R3)** — đây là thay đổi chạm production thật
(SpaceX/ZaloPay live), KHÔNG phải chỉ R&D nữa, phải qua đúng quy trình: Taylor thiết kế + đo tác
động đầy đủ (không chỉ tin kết luận R&D cũ, cần backtest riêng cho chính THAY ĐỔI XÓA BỎ momentum
khỏi allocator, IS/OOS/LOO/DSR/PBO) → quant-skeptic verify → user sign-off cuối cùng → mới sửa
`signal_v11_sql.py` thật. Dispatch scoping+backtest đã gửi.

**User cũng nêu ý tưởng riêng (CHƯA quyết, cần đo riêng nếu muốn theo đuổi)**: có nên tăng tỷ trọng
allocator sang LAG (PEAD) vì edge bền hơn không — Mike đã tách rõ đây là quyết định KHÁC, lớn hơn
(đổi w_LAG allocator, không chỉ xóa bucket momentum), chưa làm gì, chờ user quyết có muốn đo riêng
không sau khi việc đóng kênh MOM xong.

## Dự án momentum-deals — user duyệt plan, Phase 0 bắt đầu (2026-07-11)

User duyệt `mike/agents/Taylor/plan_momentum_deals_20260711.md` nguyên trạng (label +10%/0%, 13
feature pre-registered dùng 8L, khung CP0-CP3, chấp nhận trước CP1-NO-GO là kết luận hợp lệ).
Câu hỏi trọng tâm dự án đúng như user hỏi: "sự thành công của MOM_N cũ có thực không" — CP1 sẽ trả
lời trực tiếp (nếu chỉ do dồn 2021 → thành công cũ là ảo giác mẫu nhỏ, không phải pattern thật).
User hỏi về việc dùng 1 Discord topic riêng cho dự án này — Mike không tự tạo topic được, đã đề
nghị user dùng lại topic nghiên cứu Taylor có sẵn hoặc tạo topic mới rồi báo lại. User tạo topic
mới **1525112292159651940**, đã lưu memory (`project-momentum-deals-topic-routing`) — dispatch
tiếp theo dùng `DISCORD_THREAD_ID=1525112292159651940` override để route đúng kết quả.

**Phase 0 XONG — CP0 = GO** (cả 3 gate PASS): dataset sạch, 8L coverage 100% family, N khớp khảo sát
CHÍNH XÁC 0% lệch like-for-like; xác nhận pkl cũ đúng là base-leak pre-F3, rebuild DT5G verified
1085/1085; bắt+sửa 1 bug label (profit_2M đơn vị %). quant-skeptic CONFIRMED high confidence.

**Phase 1 XONG — CP1 = NO-GO** (quant-skeptic CONFIRMED high confidence, tự tái lập khớp chính xác):
0/13 feature qua gate pre-registered (FDR10% + sign-stable IS/OOS/ex2021 + |Cliff δ|≥0.15). 2
near-miss (ROIC_Trailing δ=+0.116, Revenue_YoY δ=+0.129 — FDR-pass + sign-stable nhưng effect size
dưới ngưỡng). Multivariate AUC 0.472 (không có predictability). **Trả lời trực tiếp câu hỏi trung
tâm của user**: thành công lịch sử MOM_N/MOM_S chủ yếu do dồn mẫu regime 2020-21 (57.2% tổng mẫu có
nhãn) — không phải pattern lặp lại được, khớp kết luận fa8l CP2 nhưng đo trực tiếp trên deal/episode
lần này. **Insight**: 8L rating+route phân tách RÕ ở DVR (đối chứng) nhưng KHÔNG ở MOM — xác nhận
đúng quan điểm user "8L không kém, chỉ là momentum không có trục chất lượng để bám".

**Khuyến nghị Taylor (chờ user quyết)**: đóng/thu hẹp kênh MOM_N/MOM_S, tái phân bổ vốn về DVR/
RE_BACKLOG. 2 nhánh mở nếu muốn tiếp tục (đều là trial MỚI, cần duyệt N-budget riêng): (a) Revenue_YoY
làm golden floor chung, (b) khai thác insight 8L-DVR thành rule sizing riêng. Phase 2 harness KHÔNG
chạy (không có candidate rule hợp lệ). Dự án dừng đúng quy trình tại CP1, chờ user quyết bước tiếp.

**User CHỌN nhánh (b)** (2026-07-11): khai thác insight "8L rating+route phân tách rõ ở DVR" thành
rule sizing riêng cho kênh DVR. Đây là trial MỚI, ngoài phạm vi N-ledger 14 test đã đóng ở Phase 1 —
Taylor cần scope/plan trước khi đo (đúng kỷ luật), không nhảy thẳng vào backtest. Dispatch scoping
đã gửi, route qua Discord topic 1525112292159651940 (dự án này có topic riêng, tách khỏi vận hành
chung — user tự nhận ra và yêu cầu tách, Mike xác nhận không tự chuyển phiên sống sang topic khác
được, chỉ dispatch việc nền route đúng topic).

**Plan DVR-8L sizing DUYỆT, backtest bắt đầu (2026-07-12)**: `plan_dvr_8l_sizing_20260712.md` —
hướng size-tilt (không hard-gate), 3 rule pre-registered (R1 route-tilt, R2 fragility-tilt, R3
combined), N=5 đóng sổ, gate CP-DVR1 chặt (OOS CAGR+Calmar ≥ baseline, LOO không âm mọi năm kể cả
ex-2021/ex-2020, tail không xấu hơn, DSR≥0.95, quant-skeptic CONFIRMED bắt buộc). Kỳ vọng khai báo
trước: +0.2-0.8pp CAGR — nếu ra +3-5pp phải nghi bug trước khi mừng. User duyệt nguyên trạng, Taylor
tiến hành backtest (module tilt + 4 run + sensitivity/LOO).

## fa_ratings → fa_ratings_8l: user CHỐT hướng (c) — dự án re-tune SIGNAL_V11 bucket trên 8L (2026-07-11)

**Quyết định user (không phải quyết định thay user)**: sau khi backtest drop-in swap bị bác (cả 2
mapping tier8l/rating8l đều kém baseline R3, OOS -3.55pp/-2.20pp, LOO âm mọi năm — xem finding
Taylor_20260711_094714, quant-skeptic CONFIRMED), user chọn **hướng (c): re-tune bucket logic
SIGNAL_V11 trên nền thang rating gốc của 8L (1-5), coi đây là ứng viên THAY THẾ CORE thật sự nếu
kết quả tốt** — KHÔNG chọn (a) giữ static vá tạm, KHÔNG chọn (b) hybrid fallback chắp vá. Lý do user
nêu rõ: "return phải dựa trên dữ liệu thật và đầy đủ... không né tránh... không dùng bất kỳ hình
thức nào chỉ để chữa cháy mà không giải quyết vấn đề tận gốc."

**Đây là dự án R&D đầy đủ, không phải patch nhanh** — 3 giai đoạn user yêu cầu: (1) team bàn luận
cẩn thận lên plan, (2) chuẩn bị dữ liệu tốt, (3) cập nhật lại model. Đang ở giai đoạn 1+2 song song:
- Taylor (fable, dispatch async): thiết kế phương pháp re-tune bucket (C/D momentum vs A/B
  compounder vs E avoid) trên thang rating 8L gốc — không map cưỡng ép sang A-E như thử nghiệm vừa
  bác. Phải theo đúng multiple-testing discipline (N trials khai báo, DSR/PBO, walk-forward IS/OOS,
  per-year LOO) trước khi coi là ứng viên production.
- data-ops/Winston (dispatch song song): chuẩn bị dữ liệu — fix cadence refresh `fa_ratings_8l`
  hiện đang THỦ CÔNG (lần cuối 06-20), đây là rủi ro đã bị nhắc lại nhiều lần (mọi finding trước đều
  flag "nếu migrate mà không wire refresh tự động = đổi bảng đóng băng lấy bảng đóng-băng-chậm-hơn").
  Đề xuất cron + freshness-check, KHÔNG tự cài crontab — trình diff cho user duyệt trước.

**Deadline nghiệp vụ thật vẫn còn nguyên**: `fa_ratings` đóng băng 05-10, sẽ sai dần khi BCTC
Q2/2026 về (~cuối tháng 7) — dự án này cần có tiến độ rõ trước đó, dù không cần vội đổi ngay hôm nay.

**Trước khi wire production**: bắt buộc qua đủ walk-forward IS/OOS + DSR/PBO + LOO + quant-skeptic
CONFIRMED + user sign-off cuối cùng — không khác gì mọi thay đổi signal khác trong hệ thống.

**Tiến độ (2026-07-11, cùng ngày, làm nhanh theo yêu cầu ưu tiên của user):**
- Cron weekly refresh `fa_ratings_8l` (Winston đề xuất) → **user duyệt + đã cài** (commit dd7feb9,
  thứ Bảy 08:30 ICT). Test tay thất bại vì phiên interactive Mike dùng service account read-only
  (`bq-reader-8l`) — CHƯA rõ cron thật (crontab) chạy identity nào, xác nhận quanh lần chạy đầu
  tiên **thứ Bảy 07-18**.
- **Phase 0 XONG — CP0 = GO** (quant-skeptic CONFIRMED, high confidence): attribution ladder tách
  được degradation của lần drop-in trước = do THANG ĐO (−2.29pp FULL/−4.34pp OOS), còn coverage
  rộng hơn của 8L thực ra DƯƠNG (+0.88pp FULL/+1.34pp OOS) → giữ full coverage, dồn thiết kế vào
  bucket rating=GATE theo ngữ cảnh. Lưu ý cần mang sang Phase 2: hiệu ứng coverage dương tập trung
  nhiều ở năm 2021 — cần LOO loại bỏ năm đó trước khi tin hẳn.
- **Phase 1 XONG — CP1 = PASS**: family 12 config đo bằng proxy BQ thật, 12/12 vượt baseline OOS.
  **User đã chọn 3 finalist đưa vào Phase 2: F12_dvr_23, F1_gate_lean, F6_n_strict** (N-ledger đã
  đóng 16/16 — Phase 2 chỉ kiểm chứng lại, không mở thêm trial mới).
- **Chỉ đạo user cho Phase 2 (quan trọng)**: đánh giá phải nhìn TỔNG THỂ — cách 3 finalist phối hợp
  với nhau và với framework hiện có, không chỉ so OOS đơn lẻ. Làm tuần tự, kiểm chứng chắc chắn từng
  bước trước khi qua bước sau — tránh làm ẩu phải sửa lại sau.
- **Phase 2 XONG — CP2 = NO-GO CẢ 3 FINALIST** (quant-skeptic CONFIRMED, high confidence, tự tái
  lập khớp chính xác). F1/F6/F12 đều fail tiêu chí OOS + LOO (âm mọi năm kể cả ex-2021) + tail. Root
  cause: trục MOMENTUM_N (kênh entry chính của BAL dưới NEUTRAL — state phổ biến nhất DT5G) gãy vì
  thang rating 1-5 không tái tạo được "quality filter ngầm" mà tier C/D cũ vô tình tạo ra (loại được
  junk nhỏ mà rating không loại được). F12 kết quả full-năm đẹp thực ra bị kéo bởi 1 năm outlier 2021
  (+20.95pp riêng năm đó) — đúng lo ngại quant-skeptic nêu từ Phase 0.
- **KẾT LUẬN DỰ ÁN hướng (c)**: đã đo trung thực và bị bác — re-tune bucket trên thang 8L gốc (theo
  đúng pre-registered family, N=16/16, không mở thêm trial) KHÔNG cho ra ứng viên thay core khả thi.
  Quy trình hoạt động ĐÚNG như thiết kế (bắt được hướng không khả thi trước khi wire production, không
  phải thất bại của quy trình).
- **3 fallback chờ user chọn** (không quyết thay user):
  (i) giữ `fa_ratings` static, xử staleness riêng — caveat: edge control đo trên bảng lúc còn fresh,
      không bảo chứng cho bảng đóng băng sau BCTC Q2/2026;
  (ii) hybrid E-gate-only (chỉ thay T1 avoid bằng rating=5, giữ nguyên phần còn lại) — CHƯA ĐO, đây
      LÀ trial mới cần user duyệt mở N-budget riêng nếu muốn thử;
  (iii) rebuild legacy builder `fa_ratings` (builder gốc không còn trong repo) — giải quyết tận gốc
      staleness, giữ nguyên semantics đã tune.
  Deadline nghiệp vụ không đổi: BCTC Q2/2026 về ~cuối tháng 7, rebal quý ~08-05.

**User CHỐT (iii) — rebuild legacy `fa_ratings` builder (2026-07-11).** Kèm chỉ đạo chiến lược lớn
hơn, QUAN TRỌNG cho hướng nghiên cứu sắp tới:
- Bản thân **book Momentum (MOM_N) hiện tại đã KHÔNG hiệu quả** (không riêng gì việc không tái tạo
  được trên 8L) — cần làm lại chiến lược này, không chỉ vá cho hợp với nguồn dữ liệu mới.
- User KHÔNG đồng ý với khung "8L kém hơn vì mất quality-filter ngầm" — quan điểm user: 8L áp dụng
  lens riêng cho từng route/ngành nên rating PHẢI chính xác hơn, không phải kém đi. Nếu momentum
  không tái tạo được trên nền 8L, đó là dấu hiệu bản thân pattern momentum cũ dễ vỡ/overfit
  (dựa vào 1 "quality filter ngầm" tình cờ của tier cũ), KHÔNG phải lỗi của 8L.
- **Hướng nghiên cứu tiếp theo (sau khi (iii) xong và verified)**: quay lại phân tích các deal
  THÀNH CÔNG trong lịch sử của book — soi kỹ đặc điểm fundamentals + technical thật để tìm 1 pattern
  hiệu quả, KHÔNG cố giữ momentum chỉ vì nó từng "vô tình" chạy được. Đây là dự án R&D riêng, MỚI,
  không phải phần của việc rebuild fa_ratings.
- **Thứ tự làm việc user yêu cầu**: tuần tự, "phần nào làm tốt phần đó trước" — (iii) rebuild
  fa_ratings builder trước, verify xong mới bắt đầu dự án phân tích momentum/deals.
- Nguyên tắc chốt cho cả 2 việc: dùng dữ liệu tươi, đánh giá đúng chuẩn mực (walk-forward IS/OOS,
  DSR/PBO, LOO, quant-skeptic) — "không nên thấy pattern dễ overfit như momentum mà bị lay động"
  (không giữ 1 pattern chỉ vì quen thuộc/lịch sử nếu số liệu thật không ủng hộ).

**Tiến độ (iii) rebuild fa_ratings builder (2026-07-11, cùng ngày):**
- Feasibility XONG (Taylor job Taylor_20260711_145129, quant-skeptic CONFIRMED high confidence):
  builder gốc **chưa hề mất** — là `fundamental_rating.py` (repo root), registry ghi nhầm "không có
  writer" (đã sửa). Lineage 100% khớp 12.367/12.367 rows lịch sử; reproduction test chạy lại hôm nay
  = 82.3% khớp tier chính xác / 99.9% trong ±1 bậc; phủ tới 2026-07-08 gồm cả 2026Q2.
- **Root cause phần lệch 18% (user xác nhận, 2026-07-11)**: BQ admin có điều chỉnh nhỏ tỉ lệ chia cổ
  tức tiền mặt → giá điều chỉnh (adjusted Close) đổi nhẹ hồi tố → percentile trôi nhẹ gần ranh giới
  tier. Đây là hiện tượng bình thường của nguồn dữ liệu, không phải lỗi công thức.
- **User CHỐT mức độ an toàn cho quý cũ (nới so với đề xuất ban đầu của quant-skeptic)**: KHÔNG cần
  đòi khớp tuyệt đối/byte-identical cho các quý đã đóng băng — "quý cũ nếu có thay đổi nhẹ vẫn đạt
  tỉ lệ thống kê thì cũng không vấn đề gì". Nghĩa là: thiết kế append-only vẫn giữ nguyên hướng
  (không chủ động re-rank lại quý cũ), nhưng nếu do dữ liệu giá gốc tự nhiên trôi (như trên) làm quý
  cũ lệch nhẹ khi build lại, đó là chấp nhận được miễn còn đạt ngưỡng thống kê tương đương đã đo
  (~82%/99.9%), KHÔNG cần chặn cứng bằng diff byte-để-byte như quant-skeptic đề xuất ban đầu.
- **User duyệt: cho Taylor tiến hành bước tiếp theo** — xây cơ chế refresh append-only + cron weekly
  (giống mẫu `fa_ratings_8l`) + wire freshness-check. Vẫn cần: (a) fix lỗi pandas-3 nhỏ ở khối cảnh
  báo cuối script trước khi wire cron; (b) quyền ghi BQ vẫn là vấn đề mở giống fa_ratings_8l — chờ
  kết quả cron 8L thật thứ Bảy 07-18 để áp dụng chung lời giải, không cần giải riêng.

## DT5G BULL-giả bug → audit freshness toàn hệ thống → CRITICAL basket fix → re-pin baseline R3
### CHUỖI ĐÃ KHÉP KÍN HOÀN TOÀN (2026-07-11), chỉ còn 3 mục chờ xác nhận qua cron thứ Hai 07-13

**Khởi nguồn**: user nghi ngờ candidate BULL sắp commit của DT5G (breadth/thanh khoản yếu, không
giống bull thật). Điều tra ra: reorg 06-21 (`10ae395`) làm writer `vnindex_5state_ew_v1.py:519` ghi
lệch path, EW-leg đóng băng từ 06-22 → base v3.4b rơi về chấm điểm index-only → BULL GIẢ (streak
9/10, thiếu 1 phiên mới commit). **Live KHÔNG bị ảnh hưởng sai** — `dt5g_live` chưa từng commit
BULL. Fix 1 dòng (`498c3a6`) + quant-skeptic CONFIRMED.

**Mở rộng audit** (theo yêu cầu user "rà soát freshness toàn hệ thống 8L/production, không chỉ
DT5G") phát hiện thêm, TẤT CẢ đã fix + verify (mỗi bước đều quant-skeptic CONFIRMED):
- **CRITICAL**: rổ "custom30V" production thực ra là rổ BLEND (env-default sai), lệch 14/30 mã so
  với rổ yieldcombo đã backtest — writer bảng thật `custom30v_8l` chết từ 06-18. Fix: hồi sinh
  writer + trỏ advisory đúng bảng (`e02a75b`).
- **HIGH**: `compute_active_nav.py` dùng giá BQ không gate cho sizing ZaloPay; `bq_freshness_check.sh`
  có bug `-le`/`MAX_STATE_LAG` khiến báo FRESH giả (lý do bug gốc sống 3 tuần không ai biết).
- **MEDIUM**: field `close` (BQ stale) rò vào context DollarBill không code-enforce; `risk_monitor.py`
  HALT không check provenance; freshness-check chỉ phủ 3/8 bảng cần thiết; chuỗi 8L/papertrade
  FAIL im lặng không alert.
- **F3 (phát hiện lớn nhất)**: `signal_v11_sql.py` (dùng chung, entry gate BAL book) đọc bảng BASE
  thay vì `dt5g_live` — sổ tín hiệu production (pt_v4/pt_v22, paper) đã mua theo BULL giả
  (PVD/TVN/VCG/TLD/TPB/ASP). Fix tracker (`0537514`) — sổ **tự sửa sạch qua full-replay**, xác nhận
  thực nghiệm, không cần can thiệp tay (`9149c0f`). Baseline R3 đã pin cũng dùng bảng base → **re-pin
  lại** (`09724bc`): **CAGR 28.05%→28.82%, Sharpe 1.86→1.90, MaxDD -17.5%→-15.7%, Calmar 1.60→1.83**
  — cải thiện toàn diện, DSR=1.0000/PBO=0.209 không suy giảm. Backup CSV cũ + banner SUPERSEDED
  trong `data/results_registry.md`. `pt_v12_live.py` xác nhận KHÔNG phải production consumer (chết
  từ 05-19), không cần vá.

**⚠️ Số tham chiếu V2.4 chính thức đã đổi** — CLAUDE.md/canonical.md ghi "R3 NEUTRAL-only @50B:
CAGR 28.05%..." **ĐÃ LỖI THỜI**, cần cập nhật thành 28.82%/1.90/-15.7%/1.83 ở lần sửa KB tiếp theo.

**Còn treo, chờ cron thứ Hai 07-13 18:30 ICT (Mike tự kiểm tra, đừng quên qua restart):**
1. Query lại `tav2_bq.vnindex_5state_dt5g_live` xác nhận 06-24→07-13 = NEUTRAL(3), có dòng 07-10/07-13.
2. `bq show tav2_bq.custom30v_8l` xác nhận writer đã hồi sinh (lastModified qua 06-18).
3. `19:00 ICT freshness-check 8 bảng` chạy thật lần đầu — kỳ vọng 2 WARN hợp lệ, 0 false-block
   (Winston đã test kỹ case này để không chặn nhầm publish quan trọng).

## `mike@Mike.service` (remote-control daemon) đã TẮT HẲN (2026-07-07, user quyết định)
User giờ chỉ dùng Discord để nói chuyện với Mike (tách nhiều topic tiện phân việc hơn hẳn so với
ClaudeCode desktop app), gần như không dùng desktop app trực tiếp nữa (chỉ dự phòng lúc bất
thường, vd lỗi version model không xử lý được qua Discord). Đã xác nhận qua điều tra process/
systemd: **`mike@Mike.service`** ("Claude agent Mike, remote-control") và **`ccdb-mike.service`**
(bridge Discord thật, nhận tin nhắn + spawn `claude -p --resume <thread-uuid>` cho MỖI topic) là
**2 service độc lập hoàn toàn** — `ccdb-mike.service` KHÔNG phụ thuộc `mike@Mike.service` (xác
nhận `systemctl --user show ccdb-mike.service` không có Requires/After/PartOf/BindsTo nào trỏ tới
service kia). Đã `systemctl --user disable --now mike@Mike.service` — verify: service này
`inactive (dead)`, còn `ccdb-mike.service` vẫn `active (running)` bình thường, Discord không hề
gián đoạn. **Không cần sửa `bin/watchdog.sh`/`bin/fleet_health.sh`** — cả 2 script tự động iterate
qua unit đang `enabled` (không hardcode tên `mike@Mike.service`), nên tự động bỏ qua unit đã tắt,
không báo cảnh báo giả "DOWN"/"PERSISTENT DOWN" nữa.

**Nếu cần bật lại** (vd muốn dùng lại tính năng remote-control của desktop app):
`systemctl --user enable --now mike@Mike.service`.

## Model mặc định của chính Mike — SỬA LẠI về Sonnet 5 (2026-07-07, user yêu cầu, đảo ngược quyết
định 2026-07-06 đổi sang Fable 5)
Đã đồng bộ **3 nơi** (phát hiện có 2 tầng cấu hình song song trong bridge, không chỉ 1 chỗ — xem
[[reference-ccdb-model-config-layers]]):
1. `agents/Mike/.claude/settings.json` → `"model": "claude-sonnet-5"`.
2. `/workspace/ccdb-mike/.env` → `CCDB_MODEL=claude-sonnet-5` (đây là fallback thấp nhất, KHÔNG
   phải nguồn quyết định thật nếu DB đã có row).
3. **`/workspace/ccdb-mike/data/sessions.db` bảng `settings`** — đây mới là nguồn ưu tiên CAO NHẤT
   (thread override > global > `.env`). Phát hiện 4 dòng rác sai format từ các lần `/model` trước
   đó (`"Sonnet 5"`, `"sonnet 5"` có dấu cách — CLI từ chối, đây chính là lỗi user gặp ở 1 topic
   khác). Đã dọn: xóa hết override riêng theo thread, chỉ giữ 1 giá trị global
   `model.global.claude = "claude-sonnet-5"` (+ đồng bộ key legacy `claude_model` cho nhất quán
   hiển thị). Không cần restart `ccdb-mike.service` — bridge tự đọc lại nguồn này mỗi lần spawn
   session mới.

## Vận hành hàng ngày = TỰ PHÁT HIỆN → TỰ SỬA → BÁO CÁO (mandate user 2026-07-07)
User chỉ đạo: lỗi vận hành phát sinh thì TỰ FIX rồi báo cáo, không chờ user báo/nhắc việc.
Tài liệu chuẩn tắc: **`kb/ops_runbook.md`** (timeline ngày, mỗi bước check gì, ranh giới tự
sửa). Cơ chế: `bin/ops_autofix.sh` — checker phát hiện lỗi → dispatch Winston (fable) chẩn
đoán + sửa + verify + báo Trading Daily; đã wire vào `ops_health_check.sh` (08:20/12:45) và
`sync_bq_cache_daily.sh` (23:45). Cooldown 1h/vấn đề chống bão dispatch. **Ranh giới cứng
(không bao giờ tự sửa, escalate question + Telegram):** trade plan, trading_rules.json,
logic đặt lệnh, crontab dòng thực thi, xoá dữ liệu, BOT_STOP. Mike trong phiên sống thấy
lỗi ops → tự sửa trực tiếp cùng ranh giới đó, không cần chờ checker.

## Onboarding account mới cho team Mike (thêm 2026-07-06, user yêu cầu chuẩn hoá quy trình)
Khi user nói "giao quyền quản lý tài khoản X cho team Mike" → làm theo
`kb/account_onboarding_runbook.md` theo đúng thứ tự, không tự bịa quy trình. Tóm tắt: cron
dùng-chung (preflight/ops-health-check/send-plan-report/eod-report/dispatch-DollarBill) đã
tổng quát hoá qua `trading_bot.config.live_dnse_labels()` + `bin/for_each_live_account.sh` —
account mới `enabled:true/mode:live/broker:dnse` trong `trading_bot_accounts.json` tự động
được các bước này nhận, KHÔNG cần sửa cron. Riêng 4 dòng cron THỰC THI THẬT (`run_bot.sh`,
`bot_heartbeat.sh`, lunch-pkill) KHÔNG tự động — luôn hỏi user xác nhận trước khi thêm (điểm
không thể đảo ngược: bot tự đặt lệnh thật lần đầu, không người duyệt giữa chừng).

## Đang trading (LIVE)
- **SpaceX** (DNSE 0002023347): V2.4 LIVE từ 2026-07-01. **Trim 07-06 ĐÃ HOÀN TẤT** (23/23 lệnh bán,
  710,5tr/710,1tr kế hoạch = 100%, không lệch đối soát broker) — exposure 141,4%→~70% NEUTRAL target
  như kế hoạch, 8 mã basket-drift đã thoát hết (LPB/MSB/VHC/HAH/VIB/VGC/DCM/MBS). **Nợ margin thật
  VẪN CÒN 409,86tr VND** (chưa trả — lần đọc API giữa chiều báo debt=0 là do balance CHƯA cập nhật
  xong, không phải nợ đã được trả; xác nhận bằng ảnh chụp app DNSE thật của user + đọc lại API lúc
  16:12 ICT, xem `kb/INCIDENTS.md` 2026-07-06 "CORRECTION"). **NAV xác nhận đúng: 983.002.349 VND**
  (khớp chính xác ảnh chụp app: Tiền 709.276.086 + Cổ phiếu 683.590.000 − Nợ 409.863.737). Nợ margin
  sẽ giảm khi tiền bán thật sự settle T+2 (08/07). 15 vị thế còn lại. run_bot.sh 09:05 ICT mỗi T2-T6.
  **Cập nhật cùng ngày:** `verify_account_snapshot.py` từng dùng BQ Close (sync đêm 23:45) cho MTM
  cùng ngày → NAV đã post lúc 15:00 dùng nhầm giá 07-03 (688,38tr thay vì 683,59tr thật). Đã vá: dùng
  `close_price()`/`latest_trade()` DNSE boardId=G1 khi `--asof`=hôm nay (verified khớp app tới đồng),
  BQ vẫn dùng cho ngày quá khứ. `nav_history_SpaceX.csv` dòng 07-06 đã sửa lại đúng. Chi tiết:
  `kb/INCIDENTS.md` 2026-07-06 "Two wrong end-of-day market price sources".
  **Đã duyệt (2026-07-03, event Mike/decision `plan-07-06-v2-trim-70pct`): trim GỘP về đúng 70% NEUTRAL
  target** (không chỉ khôi phục 1x như plan v1 cũ) — `data/trade_plans/plan_SpaceX_2026-07-06_v2.json`,
  bán tổng ~710M VND (71.8% NAV) trong 1 phiên 07-06 09:00-10:30, Mafee đã authorized, không cần duyệt
  lại. Sau thực thi kỳ vọng: exposure 141.4%→69.6%, dọn sạch 8 mã basket drift (LPB/MSB/VHC/HAH/VIB/
  VGC/DCM/MBS), margin debt→0 sau T+2 settle 07-08. **Lý do 70% (không phải 93.8-94.7% go-live gốc):**
  DollarBill từng tự đặt target_equity_pct=93.8% lúc go-live KHÔNG qua backtest — user chất vấn trực
  tiếp, Taylor backtest full 2-book NAV thật xác nhận 70% thắng tuyệt đối mọi metric risk-adjusted
  (Sharpe 1.78 vs 1.66, Calmar 1.63 vs 1.49, DD -16.5% vs -18.8%, job `Taylor_20260703_130720`, quant-
  skeptic CONFIRMED). Đã chính thức hoá thành `trading_rules.json` v2.1 section `neutral_parking`
  (default 0.70 của phần idle cash khi BAL/LAG rỗng, KHÔNG phải trần tổng cổ phiếu — khi 2 book có deal
  thật tổng cổ phiếu có thể vượt xa 70%, đúng thiết kế) + cơ chế `risk_dial_override` (muốn park≠0.70
  bắt buộc field `risk_dial_confirmed_by_user`+`risk_dial_warning_acknowledged`, thiếu 1 trong 2 →
  Mafee tự block plan).
  **Cập nhật 2026-07-06 08:5x ICT (trước giờ mở cửa):** phát hiện `plan_SpaceX_2026-07-06.json`
  (tên file executor thật sự đọc) vẫn là bản v1 cũ (11 lệnh, 94.7%) — v2 (23 lệnh, 70%, bản đã
  duyệt) nằm ở tên file `_v2` mà `trading_bot/plan.py` KHÔNG hề nhận diện. Nếu không phát hiện,
  09:05 sẽ chạy nhầm v1. Đã sửa (user duyệt): đổi tên v1→`..._v1_superseded_11name.json` (giữ audit),
  copy v2 đè vào tên file chính thức — xác nhận qua preflight 08:58 ICT: "23 lệnh, ~0.710B VND,
  approved=user" đúng như kỳ vọng. Tiện thể vá 2 lỗi hiển thị trong `preflight_check.sh` (field
  `approved_by`/`mafee_authorized` thiếu ở plan gốc gây báo NOT_APPROVED giả; field `est_value_vnd`
  vs `est_value` sai tên gây hiển thị `0.000B` giả). Chi tiết đầy đủ: `kb/INCIDENTS.md` 2026-07-06.
  **Cập nhật 2026-07-06 giữa phiên sáng:** phát hiện bot lặp ~2000 lần `HTTP 400: Trade quantity
  not enough` từ 09:12 ICT trên đúng 11 mã mua 02/07 (chưa qua T+2 — DNSE chỉ nhả sellable từ
  **phiên chiều** của ngày T+2, không phải từ đầu phiên sáng). Đã vá `trading_bot/executor.py`
  (commit `2cee603`): `step()` gọi `get_positions()` 1 lần/chu kỳ, cap qty bán theo `sellable`
  thật hoặc bỏ qua (`WAIT_T2_SETTLEMENT`) thay vì để broker tự từ chối. Fix này CHỈ có hiệu lực
  từ lần restart tự nhiên tiếp theo (nghỉ trưa 11:30 → resume 13:00), không restart tay giữa
  chừng. Cũng commit luôn fix `trading_bot/plan.py` (id/ref_price normalize cho schema v2, commit
  `7a2a145`) đã hotfix trên đĩa từ sáng nhưng chưa commit. Chi tiết: `kb/INCIDENTS.md` 2026-07-06
  (entry thứ 2 cùng ngày).
- **ZaloPay** (DNSE 0001743768, tên cũ `dnse_main`, đổi tên 2026-07-06): V2.4 LIVE từ 2026-07-06
  (user quyết định). **CASH-ONLY** (không margin, package "ZaloPay" id=1258 type N) — cơ hội so
  sánh V2.4 có-margin (SpaceX) vs không-margin. Tài khoản có 7 vị thế CŨ (giữ từ trước khi bot
  quản lý, không có lịch sử FILL trong journal nội bộ): DGC/MSH/TCM/TLG/VHC/VIB/VPB. **DGC (47,2%
  NAV) EXCLUDED khỏi rebalancing** qua field mới `excluded_tickers` trong
  `secrets/trading_bot_accounts.json` (enforce cứng ở `bot_execute.py` qua
  `trading_bot.plan.filter_excluded_tickers()`, không phụ thuộc plan generator nhớ đúng) — lý do:
  đang bị HOSE hạn chế giao dịch (QĐ 448, chỉ khớp định kỳ, cắt margin) + cảnh báo (QĐ 544, kiểm
  toán ngoại trừ) do lãnh đạo bị khởi tố hình sự 17/03/2026, ước gỡ hạn chế ~11-12/2026 (xem
  legal-vn/Wendy research 2026-06-21/26/29 — Điều 42 QĐ 22 cần đủ 2 điều kiện: khắc phục nguyên
  nhân + 6 tháng sạch CBTT liên tục). Taylor giữ DGC vì lý do đầu tư (target 70-75k/12-18 tháng,
  +37% EV, 65% xác suất, briefing 2026-06-29), KHÔNG phải vì kẹt thanh khoản.
  NAV thật go-live (xác nhận API 2026-07-06T07:42): **tổng NAV 1.011.470.378đ, active NAV (loại
  DGC, dùng làm cơ sở target V2.4) 534.470.378đ** — dùng `bin/compute_active_nav.py --account
  ZaloPay` để tính lại khi cần (không phụ thuộc lịch sử journal, đọc trực tiếp balance/positions
  thật + giá BQ). **Known gap:** `daily_nav_snapshot.py` chưa tính đúng P&L cho vị thế legacy này
  (cần lịch sử FILL nội bộ mà account không có) — NAV/active_nav đã đúng, phần P&L breakdown cho
  báo cáo cần việc riêng sau. Cơ chế `excluded_tickers` viết TỔNG QUÁT (không riêng ZaloPay) để
  dùng cho account tương lai có vị thế legacy tương tự — xem `kb/coding_guidelines.md` §7. Chi
  tiết đầy đủ + 10 selfcheck: `kb/INCIDENTS.md` không có entry riêng (không phải sự cố, là setup
  bình thường) — xem commit `87392be` (WorkingClaude repo).
  **Cập nhật 2026-07-06 tối (user xác nhận 2 lần):** đã thêm 4 dòng cron thực thi thật
  (`run_bot.sh --account ZaloPay` sáng/chiều, `bot_heartbeat.sh ZaloPay`, lunch-pkill) —
  ZaloPay giờ tự động y hệt SpaceX. **Plan 07-07 hiện tại vẫn là HOLD/0 lệnh** (bản nháp
  transition Option A — bán dần VIB/VHC/TCM/TLG/MSH, mua custom30V thay thế, user đã chọn
  hướng A — dispatch DollarBill 2 lần đều timeout/treo, KHÔNG ghi được file cập nhật, cần
  dispatch lại + điều tra nguyên nhân treo) → phiên chạy tự động ĐẦU TIÊN sáng mai
  (2026-07-07) sẽ không làm gì (an toàn). `approved_by` vẫn null → preflight 08:45 mai sẽ
  báo RED cho ZaloPay (NOT_APPROVED) — ĐÃ BIẾT TRƯỚC, vô hại vì 0 lệnh. **Bug nghiêm trọng
  phát hiện + đã vá cùng tối:** `dnse_raw_{date}.jsonl` dùng chung cho MỌI account theo
  ngày, bản ghi "balances" không gắn account → NAV SpaceX báo sai 688,5tr (lẫn balance
  ZaloPay) khi tính lại báo cáo EOD hôm nay. Đã vá tận gốc (`trading_bot/brokers.py` gắn
  account_no/label mọi bản ghi log, `daily_nav_snapshot.py` lọc đúng account) + verify lại
  đúng 982.867.365đ + gửi đính chính (Telegram — Discord "Trading report" lỗi HTTP 500,
  không phải do nội dung). Chi tiết: `kb/INCIDENTS.md` 2026-07-06. **Topic Trading report đã
  THÔNG lại ~23:45 cùng tối**: root cause = private thread, bot rớt membership khi archive —
  unarchive KHÔNG đủ, user phải @mention bot trong topic để thêm lại. Report EOD chính thức
  đã gửi vào topic. eod_trading_report.sh giờ có fallback Telegram+Trading Daily khi post fail
  (không bao giờ rơi im lặng nữa).
- **AlphaLens Paper**: FPT/ACB/MBB/HDB, tracking vs VNINDEX đến 2026-09-30. DollarBill phụ trách.

## Đang R&D
- **Taylor · EXTREME-regime gate PAPER-TRADING** (bắt đầu 2026-07-01, user duyệt trực tiếp): `extreme_regime_enabled=True` CHỈ trên account paper `main` (override trong `trading_bot_accounts.json`); global default + SpaceX/live GIỮ `False`. Week-1 stress-injection PASS 24/24 (`stress_extreme_regime.py`: arm 2-poll · sell-to-floor · buy-pause · cadence ×0.25 + negative controls). **Target kết thúc ~2026-07-28 (~20 phiên).** 3 điều kiện còn lại trước LIVE: (a) ZERO false-trigger qua ~4 tuần benign, (b) không can thiệp NORMAL-path, (c) user sign-off. **KHÔNG bật gì ở live.**
- **Taylor · vol-scale buy chase-cap (patch#3) PAPER-TRADING** (bắt đầu 2026-07-01, user duyệt trực tiếp): `chase_cap_vol_scale_enabled=True` CHỈ trên account paper `main` (override trong `trading_bot_accounts.json`, k=2.0/ceil=0.04); global default + SpaceX/live GIỮ `False`. Executor-path stress PASS 15/15 (`stress_vol_scale_chase_cap.py`: wiring · WIDEN clamp-to-ceil · MONOTONE · fail-safe rvol absent/0/<0 · paper limit > static + NEG-control live→static). **Target kết thúc ~2026-07-14 (~10 phiên — ngắn hơn EXTREME vì fire trên gap-up thường, tích event nhanh).** Điều kiện trước LIVE: (a) paper sạch (wiring đúng trên quote thật + fail-safe khi thiếu rvol cache), (b) không can thiệp NORMAL-path ngày non-gap, (c) skeptic rerun REAL-fill vs `min(open,L)` proxy trên correlated gap-up @NAV target, (d) user sign-off. **KHÔNG bật gì ở live.**
- **Taylor**: sector sweep #10+ (chờ Mike dispatch)
- **Taylor · fill-timing khung giờ (BUY 10:45-11:15 / SELL 09:15-09:45)**: ĐÃ xử lý xong 2026-07-02 (job Taylor_20260702_031608, note cũ ở dòng này lỗi thời). Edge THẬT & IS/OOS-stable (BUY tại 11:15 rẻ hơn open +17.6bps/lệnh, t=12.0; SELL tại open đúng, +11.8bps vs ATC) nhưng **KHÔNG flip `fill_timing_live_gate` ngay** — cần paper tích lũy ~3-4 tuần fill (từ go-live 2026-07-01, mới ~3-4 phiên) để `execution_quality_review.py` xác nhận NET-of-noise capture (noise 110-220bps >> edge 17bps) → quant-skeptic → user sign-off mới flip. Checkpoint tự nhiên: ~cuối tháng 7.
- **V2.5**: R&D-complete, DISABLED. Reminder: 2026-07-07 Mike hỏi user go-ahead integration.
- **Taylor · DC-book (ConvergePort) NEUTRAL idle-cash waterfall PAPER-TRADING** (bắt đầu 2026-07-06,
  user duyệt trực tiếp, job `Taylor_20260706_125540` + `Taylor_20260706_131247`): khi NEUTRAL và
  BAL/LAG rỗng (đúng tình trạng SpaceX từ ~04/2026), thứ tự ưu tiên giải ngân phần tiền rảnh:
  **BAL/LAG (full trước, không đổi) → DC book/ConvergePort (double-confirm sector-lens BUY ∧ 8L
  rating≤2, capacity ~10-15B ex-DHG) → custom30V (phần còn lại)**. Khi BAL/LAG có deal trở lại → rút
  ưu tiên ngược lại, bán custom30V trước rồi mới đến DC book (reverse-unwind). Backtest xác nhận: DC
  làm top-priority (thay BAL/LAG) = REFUTE mạnh (12.05% CAGR/DD-38.4% vs R3 28.05%/DD-18.8%); DC làm
  lớp giữa (đúng thứ tự trên) = +5.0pp trên sleeve parking, ước tính +3.5pp/năm cho SpaceX-now. **Caveat
  quan trọng: DSR phần excess này chỉ 0.775 (<0.95 ngưỡng an toàn) — bảo hiểm hợp lý, CHƯA phải alpha
  tin cậy cao** → lý do bắt buộc phải paper trước, không wire live ngay. Chạy CHỈ trên account paper
  `main` (override trong `trading_bot_accounts.json`), global default + SpaceX/live GIỮ nguyên (không
  đổi gì). **Đã thêm vào EOD daily report** (theo yêu cầu user 2026-07-06) — xem section paper sleeve
  trong `eod_trading_report.sh` output.
  **Review = EVENT-ANCHORED, KHÔNG PHẢI ngày cố định** (user quyết định 2026-07-06, sau khi Taylor tự
  đính chính lý do "3 tháng" không phải vì DSR mà vì chu-kỳ cơ chế): mốc review = khi chu kỳ
  reverse-unwind ĐẦU TIÊN (LAG dự kiến refill cuối 07, job `Taylor_20260704_033932`) hoàn tất + settle
  4-6 tuần sau đó. Sàn ~2 tháng (đủ thấy trọn unwind+settle), trần ~2026-10-06 (tránh mùa BCTC Q3).
  Nếu LAG refill trượt lịch → mốc review trượt theo, KHÔNG giữ cứng 10-06. **Mike + Taylor cùng theo
  sát diễn biến portfolio để đề xuất ngày review cụ thể khi đủ điều kiện** — không tự động, không
  phải 1 con số đã chốt sẵn.

## Chờ user quyết định
- V2.5 live-recommend integration: **2026-07-07** (trigger tự động)

## Reliability hardening (2026-07-02, theo yêu cầu user — 4 việc AgentOps)
Đã triển khai đủ 4 mục theo thứ tự ưu tiên, chi tiết + self-check trong `kb/INCIDENTS.md` và
`MIKE.md` §Quy chuẩn bắt buộc:
1. **Circuit breaker** per-agent trong `dispatch.sh` (`state/circuit/<id>.json`).
2. **Idempotency guard** (`Executor._ghost_tickers`, `trading_bot/executor.py`) — lớp phòng thủ
   THỨ HAI cho double-buy, đóng residual gap quant-skeptic tìm thấy sau flock fix (503aa2f).
   quant-skeptic CONFIRMED (verify_finding.sh 2026-07-02T13:48). Review vòng 2 (bên thứ ba, xem
   dưới) thêm 2 fix nữa. **Đã commit** repo WorkingClaude/thanhdt commit `e1d9b7c` (user duyệt
   2026-07-02T15:30).
3. **trace_id** trong bus event (`append_event.sh`, fallback tự động qua `$JOB_ID`).
4. **`kb/INCIDENTS.md`** — backfill 5 sự cố đã biết (double-buy, job chết theo session, callback
   ping-pong, Mafee zombie, go-live day-1 5 bugs).

**Review vòng 2 (2026-07-02, bên thứ ba độc lập)** — verify lại cơ chế bằng dữ liệu DNSE thật
(6.338 lệnh `dnse_raw_2026-07-02.jsonl`), xác nhận cơ chế đúng, tìm thêm 2 gap không-chặn +
1 note vận hành, cả 3 đã fix/ghi ngay trong lượt: (a) `_save_state()` không atomic → giờ
tmp+`os.replace()`; (b) `PaperBroker.poll_orders()` trả `raw=None` → guard là no-op trên paper,
giờ trả `raw={"symbol":...}` giống broker thật, paper trading diễn tập được; (c) không có quy
trình "unpause" chính thức — đã ghi rõ trong docstring `_ghost_tickers()` (executor.py) + KB
(chấp nhận theo thiết kế: unpause thủ công, không auto-reconcile). `ghost_order_selfcheck.py`
giờ 12/12 (thêm I/J cho 2 fix trên, verify catch-regression bằng cách revert-tạm rồi phục hồi).
**Đã commit** cùng lần với vòng 1 — commit `e1d9b7c` gộp cả 2 vòng review.

## Usage-limit auto-resume (2026-07-03, theo yêu cầu user)
User gặp vấn đề: task tự động research bị dừng giữa chừng khi tài khoản hết usage limit 5h
(`bin/usage_watch.py`), phải tự quay lại nhắc "tiếp tục". Đã tự động hóa cho **mọi agent qua
`dispatch.sh`** (không riêng agent nào — Taylor/DollarBill/Mafee/... đều được):
- `dispatch.sh` phát hiện dispatch fail vì usage-limit (log khớp cụm từ HOẶC
  `usage_watch.py` PCT≥95%) → KHÔNG coi là fail thật (không trip circuit breaker) → ghi
  `bus/pending_resumes/<job_id>.json` (resume_at = reset-time ước tính + buffer 10').
- **`bin/resume_pending.py`** (cron mới, `*/10 * * * *`) tự fire record đến hạn, dispatch lại
  đúng agent với prompt "đọc working memory, tiếp tục — đừng làm lại từ đầu".
- Chặn lặp vô hạn: tối đa 3 lần auto-resume liên tiếp (`DISPATCH_MAX_USAGE_RESUMES`), quá trần
  → rơi về xử lý fail thật (có trip circuit breaker) — phòng trường hợp đây là bug thật chứ
  không phải usage limit thật.
- Test end-to-end đầy đủ (fake usage-limit CLI, sync + `--bg`, cap boundary n=2/n=3, resume
  chain thật qua `resume_pending.py`) — tất cả đúng như thiết kế.
- **Giới hạn đã biết:** chỉ cứu headless dispatch, KHÔNG cứu được phiên tương tác trực tiếp
  của chính Mike (nếu turn hiện tại của Mike bị rate-limit thì turn đó chết hẳn, không tự
  lên lịch resume chính nó được). Chi tiết: `MIKE.md` §Quy chuẩn bắt buộc mục 6.

## Workflow ngày trading (SpaceX, T2-T6, giờ ICT)
1. **17:30** — `bq_freshness_check.sh`: BQ fresh → dispatch DollarBill lập plan T+1
2. **19:30** — `send_plan_report.sh`: gửi plan T+1 vào Trading Daily thread (duyệt trước 08:45 sáng mai)
3. **08:20** — `ops_health_check.sh --label "Trước phiên sáng"` (thêm 2026-07-06, theo yêu cầu user) —
   kiểm tra vận hành tự động TRƯỚC preflight: xung đột file plan (bài học sự cố 07-06), lỗi lặp lại
   bất thường trong journal (loại trừ WAIT_T2_SETTLEMENT/mẫu T+2 đã biết), circuit breaker, câu hỏi
   (question) chưa trả lời trong 48h — post tóm tắt vào **Trading Daily** (vận hành sống, không phải
   Trading report). Script: `bin/ops_health_check.sh`.
4. **08:45** — `preflight_check.sh`: kiểm tra sẵn sàng trước giờ mở cửa (GREEN/RED)
5. **09:05** — `run_bot.sh --auto-otp`: thực thi plan (phiên sáng)
6. **09:00-14:55** — `bot_heartbeat.sh` mỗi 5': giám sát liveness + digest fill mới
7. **11:30** — dừng bot giờ nghỉ trưa (`pkill -f "[b]ot_execute.py --account SpaceX"`, sửa 2026-07-06
   tối — pattern cũ tự khớp luôn dòng lệnh gọi chính nó qua `sh -c`, xem `kb/INCIDENTS.md`; vô hại
   vì `session_phase()` đã tự idle đúng qua trưa dù pkill không hiệu quả, nhưng vẫn cần fix cho đúng)
8. **12:45** — `ops_health_check.sh --label "Trước phiên chiều"` (thêm 2026-07-06) — kiểm tra lại toàn
   bộ khâu vận hành sau phiên sáng, trước khi resume phiên chiều — cùng nội dung kiểm tra như bước 3,
   chạy lại để bắt vấn đề phát sinh trong phiên sáng trước khi vào phiên chiều.
9. **13:00** — `run_bot.sh --auto-otp`: resume phiên chiều
10. **~14:50** — phiên đóng (ATC), bot tự cancel lệnh treo, ghi `exec_*_report.md`
11. **15:00** — `eod_trading_report.sh`: **báo cáo tổng kết EOD** (thêm 2026-07-01) — đọc `state.json`
   (giá khớp thực từng lệnh), tính tổng lệnh/mua-bán/khớp đủ-một phần-chưa khớp/tổng giá trị VND,
   post vào **Trading report topic** (đổi từ Trading Daily 2026-07-03, xem dưới). **Thêm 2026-07-03**:
   gọi `bin/daily_nav_snapshot.py` để in kèm NAV thật cuối ngày + biến động so hôm trước (MTM cổ phiếu
   từ BQ, cash/nợ margin từ balances API thật) — ghi vào `data/execution_logs/nav_history_SpaceX.csv`,
   nguồn duy nhất mọi báo cáo ngày/tuần/tháng dùng chung. Xem `kb/coding_guidelines.md` §6 "Standing
   pipeline" cho quy trình xác minh bắt buộc + phân biệt độ sâu nội dung theo từng loại báo cáo.

**3 Discord topic tách biệt (cập nhật 2026-07-03 — thêm Trading report):**
- **Trading Daily (1521470705563340910)** — nội dung VẬN HÀNH SỐNG trong ngày: preflight, run_bot,
  heartbeat, BQ freshness, `ops_health_check.sh` (08:20 + 12:45, thêm 2026-07-06). (EOD report đã
  CHUYỂN sang Trading report — xem dưới.)
- **DollarBill plan channel (1521183164364754974)** — riêng cho việc LẬP KẾ HOẠCH của DollarBill
  (`send_plan_report.sh`, và mọi `dispatch.sh DollarBill ...` khác dù cron hay ad-hoc). Root cause
  thread-leak (dispatch notify theo thread Mike đang active) đã fix ở tầng `dispatch.sh` qua hàm
  `_agent_thread_override` — route CỐ ĐỊNH cho DollarBill bất kể Mike gọi từ topic nào.
- **Per-job thread routing tổng quát (thêm 2026-07-06)** — `_agent_thread_override` chỉ đúng cho
  agent LUÔN thuộc 1 topic cố định (DollarBill). Nhưng Taylor phục vụ NHIỀU topic song song (vd
  user tách riêng "nghiên cứu 8L" và "nghiên cứu vĩ mô", cả 2 đều dispatch Taylor) — báo cáo hoàn
  thành từng job phải về ĐÚNG topic đã yêu cầu job đó, không phải topic Mike đang hoạt động lúc
  job xong. Fix: `dispatch.sh` giờ ghi `discord_thread_id` NGAY vào job record lúc dispatch (chụp
  1 lần, không đổi), mọi thông báo (nhận việc/xong/fail/circuit-breaker/usage-limit) đọc lại field
  này qua `_job_thread_id <job_id>` thay vì suy ra "topic hiện tại". Xem `kb/INCIDENTS.md`.
- **Trading report (1522576692638388364, thêm 2026-07-03, user chỉ đạo)** — kênh DUY NHẤT cho
  **báo cáo tổng hợp** trading ngày/tuần/tháng (khác với alert vận hành sống ở Trading Daily). Đã
  chuyển đích `eod_trading_report.sh` (báo cáo EOD + cảnh báo đối soát mismatch) sang topic này.
  Báo cáo tuần/tháng (khi Mike tự soạn thủ công theo yêu cầu user, vd báo cáo tuần go-live SpaceX
  2026-07-03) cũng đích đến topic này. User cũng dùng topic này để giao các yêu cầu vận hành liên
  quan đến báo cáo trading.

**Duyệt plan — LUÔN mirror vào DollarBill plan channel (thêm 2026-07-02, user chỉ đạo):** khi
user duyệt/thảo luận duyệt plan trực tiếp với Mike ở BẤT KỲ topic Discord nào khác (không riêng
plan channel), Mike vẫn xử lý ngay tại chỗ (không ép user đổi topic), NHƯNG phải
`notify_thread.sh` xác nhận vào **1521183164364754974** ngay sau đó — channel này luôn là bản ghi
đầy đủ mọi lần duyệt, dù hội thoại thật diễn ra ở đâu. Lý do: tránh rải rác/loãng topic khác.

**Escalation khi plan T+1 không sẵn sàng (thêm 2026-07-01, sau sự cố DollarBill "timeout" nhưng
plan thực ra đã ghi xong — dispatch.sh job status không đáng tin 100%):** `send_plan_report.sh`
19:30 ICT giờ verify ARTIFACT thật (file `plan_<account>_<T+1 date>.json` đúng ngày kỳ vọng qua
`next_trading_day()`, có field `orders`) — KHÔNG tin job status. Nếu thiếu/sai ngày/hỏng schema →
**ESCALATE thật**: Telegram + Discord (như cũ) VÀ ghi bus event `question` (`plan-t1-not-ready`) để
Mike tự đọc được ở phiên sau, không chỉ trông chờ user thấy Telegram rồi tới hỏi. KHÔNG tự động
retry/re-dispatch (an toàn hơn — con người quyết định bước tiếp theo, đúng nguyên tắc human-in-the-loop
của toàn hệ thống).

## Cron quan trọng khác (ICT)
| Giờ | Lịch | Việc |
|---|---|---|
| 23:45 | T2-T6 | sync_bq_cache_daily.sh |
| 02:00 | Daily | kb_nightly.sh — archive events, trim memory |
| 02:00 | Thứ 6 | kb_nightly.sh → dispatch Mike editorial KB review |
| 00:00 | Daily | backup.sh → GitHub |

## Kill-switches
- `data/BOT_STOP`: tạo file = dừng mọi giao dịch tức thì
- `state/NOTIFY_OFF`: tắt Telegram push tạm thời
- V2.5: `trading_rules.json v1.7` → v25_leverage STATUS=DISABLED

## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-01. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`). **Live từ 2026-07-01.**

### Mục tiêu
Vận hành chiến lược **production V2.4**, **go-live 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- **R3 NEUTRAL-only @50B: CAGR 28.05% / Sharpe 1.87 / DD −18.8% / Calmar 1.50** (pin threads=1).
- Bootstrap 5th-pct: CAGR 18.6%, DD −28.6% (anchor DD ~−29%, KHÔNG phải −18%).
- **NEUTRAL parking custom30V = phần tin cậy nhất: +7.4pp Full.** (30 mã, cap 0.10)
- Bull parking: NAV ≥150B. **(30, 0.15) = OVERFIT**, walk-forward bác.
- **V2.5** (future) = V2.4 + lever MGE=1.5, account sẵn sàng, DISABLED, reminder 2026-07-07.

### Đã thử, BỊ LOẠI — không wire
custom30V permanent-exclude 7 tên (−1.0pp); LAG SUE-tilt 3 tầng (−0.66pp); hold-neutral exit (−47B);
stability floor ROE_Min<0 (−0.45pp); liq-tilt custom30 (REFUTED); deep-discount sleeve (PARKED);
pbcombo dual-vehicle (Calmar 1.48→1.37); gq_score growth gate (−IC); composite v3 as entry-selector (NO).

### DT5G — market regime gate
- Production: `tav2_bq.vnindex_5state_dt5g_live` qua `get_gated_state()`.
- **KHÔNG đọc** `vnindex_5state` — đó là v3.4b BASE (153 transitions ≠ DT5G 49 transitions).
- Gate phòng thủ (insurance), KHÔNG phải return-enhancer.
- State hiện tại 2026-07-01: **NEUTRAL(3)**, DT5G_macro HEALTHY.

### 8L Rating & Composite
- Composite v3 LIVE (`rating_8l.py`): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS). Golden floor: ROE_Min3Y≥0 ∧ CF_OA_3Y>0.
- **1/PE dominant factor** (IC +0.125, 94% hit). Rating = binary gate ≤3, KHÔNG phải return-tilt.
- Value dominates ALL regimes kể cả BULL. Moat governance: chỉ WIDE (đã audit 5F) mới notch.

### Hạ tầng giao dịch
- `bot_execute.py --auto-otp`: execution deterministic (Python, không phải LLM headless).
- `bin/run_bot.sh`: wrapper gọi bot_execute.py, Discord notify, publish bus event.
- **`data/BOT_STOP`** = kill-switch tức thì.
- BQ Local Cache (DuckDB, threads=1): `data/bq_cache/`, ~100ms vs 5-15s BQ. Sync 23:45 ICT.
- Auto-OTP Gmail: `gmail_otp_reader.py` dùng `internalDate` filter (KHÔNG `newer_than`).
- PHS: **BLOCKED** (lỗi -700003, chờ credential) → paper only.
- **Workflow ngày trading đầy đủ** (T2-T6): BQ freshness(17:30) → plan T+1(19:30) → preflight(08:45)
  → execute sáng(09:05) → resume chiều(13:00) → **EOD report(15:00, `eod_trading_report.sh`, thêm
  2026-07-01)**. Toàn bộ post vào 1 Discord thread — Trading Daily (1521470705563340910).

### Kiến trúc fleet
- Companion daemon: **CHỈ Mike**. Mọi agent khác (Taylor, Bill, Mafee, v.v.) headless/native on-demand.
- Winston/Spyros/Wendy = native subagent `Agent(subagent_type=...)`, không còn daemon.
- Dispatch đúng: `bin/dispatch.sh`. Directive = mandate dài hạn only (deprecated cho task).
- Self-dispatch chặn. Agent → Mike phải escalate (event `question`), KHÔNG spawn Mike headless.
- **quant-skeptic**: REFUTED/INCONCLUSIVE = KHÔNG wire. Bắt buộc trước mọi thay đổi production.
- **Execution**: bot_execute.py (Python) cho đặt lệnh thật. LLM headless bị classifier block khi thao tác tiền.

### Quy chuẩn làm việc
1. Backtest: self-check 0 VND + walk-forward IS(2014–19)/OOS(2020+) + threads=1. Edge rớt OOS = loại.
2. No look-ahead: `profit_*` chỉ train, KHÔNG filter live.
3. Pin kết quả: `data/results_registry.md`. Ghi bus ngay (`append_event.sh`).
4. Human-in-the-loop: Taylor (rules) → Bill (plan, user duyệt) → Mafee (plan-bound only).
5. **Multiple-testing discipline (chốt 2026-07-05, R&D Q3 program H2, Bailey-López de Prado):** mọi
   wire production khai báo **N trials** (số config đã so sánh để tới đó) + **DSR** (Deflated Sharpe
   Ratio) trên NAV daily của config sắp deploy. **DSR < 0.95 → RED FLAG**, không wire nếu chưa có
   sign-off rõ ràng (bổ sung cho, không thay thế, gate quant-skeptic + walk-forward IS/OOS hiện có).
   Khi wire được chọn từ 1 họ ≥~8 biến thể (parking/lever/basket sweep): báo thêm **PBO** (Probability
   of Backtest Overfitting, CSCV) — PBO≥0.5 = ưu tiên config robust-trung vị thay vì IS-best. Kèm
   **per-year leave-one-out** khi edge OOS mỏng năm — 1-2 năm carry hết edge = reshuffle-luck, không
   phải signal bền (bài học Wave1/H8a-tiebreaker 2026-07-05: OOS CAGR/Calmar tăng đúng luật nhưng
   toàn bộ đến từ 2021+2023, LOO rớt → route qua skeptic trước khi wire). V2.4/R3 đã qua chuẩn DSR/PBO
   (DSR≈1.0, PBO≈0.20 — xem `data/results_registry.md` mục "DSR / PBO Robustness Annex", script
   `dsr_pbo_annex.py`).

### Cổ phiếu — quy tắc nhanh
- **BANNED vĩnh viễn**: PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC/IMP/TRA, TOS, VTP.
- Banking (MBB/ACB/HDB): Tier 1. FPT: Tier 1. CTR: Tier 2. Pharma: buy-and-hold only (timing phá alpha).
- DGC: 2 nhánh tách biệt — compounder-screen (exclude) ≠ special-situation case.
- Sector sweeps #1–9 xong: tất cả = lens/tilt, không phải standalone book (banking có OOS edge nhưng 74% trong custom30V).

### Backup / DR
`~/thanhdt/backup.sh` → GitHub `minhtrido2023/thanhdt` (private). Daily 00:00 ICT.

## Nguồn chuẩn tắc đầy đủ
Chi tiết: kb/KNOWLEDGE.md (§1-9). Events: kb/events_buffer.md. Fleet: kb/fleet_status.md.
