# Dự án momentum-deals (đóng kênh MOM_N/MOM_S)
> Dự án đã đóng — tách khỏi context_pack 2026-07-12. Chi tiết gốc từ kb/current_ops.md.
> Status: CLOSED. KHÉP KÍN — production LIVE, re-pin R3 27.84%/1.84/-18.2/1.53 (commit 4fbd492+9df396d).

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

## Đo tác động đóng kênh MOM XONG (Scope A vs B, quant-skeptic CONFIRMED) — user yêu cầu tách MOM_N/MOM_S theo regime trước khi chốt (2026-07-12)

Taylor đo xong Scope A (đóng MOM_N+MOM_S) vs Scope B (đóng cả family MEGA+MOMENTUM+MOM_N+MOM_S) so
control R3 hiện tại (28.82/1.90/-15.7/1.83) — quant-skeptic CONFIRMED high confidence, tự tái lập
khớp chính xác. **Phát hiện quan trọng: Scope B bị số đo BÁC** (kém control mọi cửa sổ kể cả 2024+)
— kênh MOMENTUM/MEGA chung (chỉ chạy BULL/EXB) vẫn đóng góp thật, CP1/CP-DVR1 chỉ đo MOM_N/MOM_S
nên không phủ được kết luận đó. Khuyến nghị ban đầu: Scope A (đóng MOM_N+MOM_S, giữ MOMENTUM/MEGA) —
chi phí lịch sử -0.97pp FULL dồn 2017-2020, nhưng hậu-2021 hoà-tới-dương (+0.11 ex-2021/+1.03
2022+/+0.65 2024+).

**User CHỈ RA khoảng trống quan trọng trước khi duyệt cuối**: `MOM_N` chỉ chạy ở regime NEUTRAL,
`MOM_S` chỉ chạy ở BULL/EXB — 2 tier "sống" ở 2 chế độ thị trường khác nhau, nhưng CP1 đo GỘP CHUNG
cả 2 vào 1 "gia đình" vì MOM_N một mình quá ít mẫu để test riêng (87 episode). Nếu MOM_S có cùng bản
chất "chỉ hiệu quả trong bull" như MOMENTUM/MEGA (vừa được Scope A-vs-B chứng minh còn đóng góp thật),
đóng gộp MOM_S cùng MOM_N trong Scope A hiện tại có thể đang bỏ lỡ 1 kênh còn tốt. Mike đã dispatch
Taylor kiểm tra lại: đo riêng Scope C (chỉ đóng MOM_N, giữ MOM_S+MOMENTUM+MEGA) so với Scope A/B,
CHƯA sửa code sống, chờ kết quả trước khi chốt phạm vi cuối cùng.

## KIỂM TRA TÁCH MOM_N vs MOM_S XONG — cả 2 phần đo ĐỒNG THUẬN: giữ nguyên khuyến nghị SCOPE A (2026-07-12)

Scope C (chỉ đóng MOM_N, giữ MOM_S) kém hơn Scope A ở OOS/2022+ (quant-skeptic CONFIRMED, tự tái
lập khớp chính xác). Phân tích lại đặc điểm tách riêng MOM_S: vẫn 0/13 FDR-pass, còn yếu hơn gộp
chung. Cơ chế: MOM_S là phần lỏng lẻo còn sót lại của điều kiện momentum (không có bộ lọc chặt như
MOMENTUM/MEGA), giữ nó không thêm giá trị mà còn chiếm vốn của kênh tốt hơn (ngay năm 2021 bong
bóng, đóng cả 2 vẫn tốt hơn chỉ đóng MOM_N). **USER DUYỆT CUỐI CÙNG: tiến hành Scope A** — đóng
MOM_N + MOM_S, giữ nguyên MOMENTUM/MEGA generic. Re-pin baseline R3 mới ≈27.84%/1.84/-18.2%/1.53 +
cập nhật KB/CLAUDE.md. Đây là thay đổi production thật (chạm `golive_recommend_v23.py` money-path
+ `pt_v22_dt5g.py` + `pt_v4_dt5g.py`) — dispatch Taylor thực thi + quant-skeptic verify code change
trước khi coi là hoàn tất. Lưu ý: BAL/LAG book hiện đang rỗng (NEUTRAL parking từ ~04/2026) nên thay
đổi này KHÔNG ép thoát vị thế nào đang mở, chỉ ảnh hưởng entry mới từ nay trở đi.

## DỰ ÁN MOMENTUM-DEALS ĐÃ KHÉP KÍN HOÀN TOÀN — production LIVE (2026-07-12, commit 4fbd492 + 9df396d)

Thực thi xong: **`MOMENTUM_N`/`MOMENTUM_S` đã bị bỏ khỏi `TIER_BAL`** ở 3 file production
(`golive_recommend_v23.py` money-path, `pt_v22_dt5g.py`, `pt_v4_dt5g.py`) + harness
`pt_v23_audit_2014.py` cùng commit — `signal_v11_sql.py` giữ nguyên (label MOM chỉ còn làm chẩn
đoán, rollback = revert 1 dòng/file). Baseline R3 chính thức mới: **CAGR 27.84% / Sharpe 1.84 /
MaxDD −18.2% / Calmar 1.53** (re-pin, byte-identical với bản đã quant-skeptic CONFIRMED trước đó).
`kb/canonical.md` đã cập nhật số tham chiếu + ghi lại quyết định đóng kênh. quant-skeptic CONFIRMED
(high confidence) cho CHÍNH việc sửa code — verify 4 file đúng ý, không side-effect, số liệu tái
lập chính xác từ NAV thô.

**Sự cố phụ bắt được + tự sửa trong lúc thực thi**: thiếu `BQ_LOCAL_CACHE` khiến 1 lần chạy rơi về
đọc BQ sống thay vì cache pin — đã root-cause, sửa, ghi `BQ_LOCAL_CACHE=1` thành phần bắt buộc của
lệnh pin từ nay. Phát hiện thêm: lần đo Scope C buổi sáng cùng ngày cũng dính lỗi tương tự (không
ảnh hưởng kết luận chính Scope A) — đã chạy lại sạch, Scope A càng vững hơn ở các cửa sổ hậu-2021.

**Hiệu lực thật**: BAL/LAG hiện đang rỗng (NEUTRAL parking từ ~04/2026) nên KHÔNG ép đóng vị thế nào
đang mở — chỉ ảnh hưởng entry mới từ lần DollarBill lập plan tiếp theo trở đi.

**Việc còn treo (không khẩn)**: dọn file tạm ở repo root (`pt_v23_scopeC_tmp_20260712.py`) khi tiện.

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
