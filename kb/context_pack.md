# Mike fleet — context pack (v1031)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-07-13T11:11:18] Winston/finding — new-listings-daily: {"date": "2026-07-13", "lookback_days": 90, "total_new": 1, "needs_manual_rating": 0, "fresh_ipo": 0, "research_queue": [], "snapshot": "/home/trido/thanhdt/Wor …
- [2026-07-13T12:12:41] DollarBill/decision — plan-2026-07-14: {"account": "SpaceX", "plan_date": "2026-07-14", "plan_file": "data/trade_plans/plan_SpaceX_2026-07-14.json", "state": "NEUTRAL(3)", "action": "BASKET_SWAP", "o …
- [2026-07-13T12:27:40] Taylor/finding — World Cup effect + deposit-rate signal scope: A=mức NĂM khớp số nhưng KHÔNG có cơ chế (cửa sổ giải đấu 2/4 dương, N=4 không làm rule); B=dữ liệu ĐÃ CÓ SẴN (deposit_rate_vn.py Big-4 proxy) — Pillar A đang mù đúng chu kỳ 2025-26 deposit +2.0pp/refi bất động, corr 6m-change chỉ 0.63: {"job": "Taylor_20260713_122053", "status": "DONE — scope/descriptive only, KHÔNG sửa production, KHÔNG backtest đầy đủ (đúng đề bài)", "phan_A_worldcup": {"nga …
- [2026-07-13T12:56:52] Taylor/finding — Plan pre-registered deposit-rate signal (Pillar A′) XONG — family N=5 đóng sổ, gate GO/NO-GO định nghĩa trước, khuyến nghị cứng shadow-first vì episode incremental STRONG chỉ N=1 (chính chu kỳ 2025-26 đang diễn ra, chuỗi lại hindsight-anchored): {"job": "Taylor_20260713_124803", "status": "DONE — plan only, KHÔNG backtest, KHÔNG sửa production (đúng đề bài)", "artifact": "mike/agents/Taylor/plan_deposit …
- [2026-07-13T13:20:58] Winston/finding — deposit-rate-signal-data-prereq-xong: {"job": "Winston_20260713_131255", "status": "DONE — 3 viec plan §2 xong, KHONG sua production, KHONG tu cai cron", "viec1_registry": {"fix": "them 2 row muc Vi …
- [2026-07-13T14:45:15] Winston/finding — ticker_prune monolith stale FIX XONG: 28 file doi sang chunked dir, monolith archived, executor stress PASS: {"job": "Winston_20260713_143546", "status": "DONE_COMMITTED_TESTED — het file nao doc du lieu chet 06-26", "scope": "28 file .py (dispatch noi 27, grep ra du 2 …
- [2026-07-13T14:48:40] Taylor/finding — Audit stale-monolith ticker_prune (06-26→07-13): LIVE + mọi backtest pinned KHÔNG ảnh hưởng; chase-cap trial (review MAI 07-14) nhiễm input rvol stale +3..59% ở 100% phiên nhưng ZERO khác biệt hành vi thực tế (đối chiếu từng lệnh); ~20 finding R&D qua 27 script đều đứng vững, không cần re-run: {"job": "Taylor_20260713_143629", "status": "DONE — audit-only, không sửa gì (Winston đã fix + commit 1630916 trong lúc job chạy, kèm stress re-run PASS)", "art …
- [2026-07-13T14:54:13] Taylor/finding — Backtest D0 real-premium (deposit−CPI) XONG: NO-GO đúng kỳ vọng pre-registered — N2 auto-NO-GO + G1/G2 fail, delta FULL −5.06pp, fire ngược dấu 2017/2019/2020-21/2025 và im lặng toàn bộ 2022; đóng dứt điểm hướng real-premium: {"job": "Taylor_20260713_141712", "status": "DONE — D0 only (D1/D2/D3 thuộc job song song), production/paper KHÔNG đụng, plan §10 + registry đã pin", "verdict": …
<!--RECENT-END-->

# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-07-12

## Sẵn sàng mùa BCTC Q2/2026 — audit + fix CRITICAL/MEDIUM đã khép kín trong ngày (2026-07-12)
User yêu cầu rà soát sau khi phát hiện MBS đã công bố BCTC Q2 (08/07) — xác nhận mùa Q2 đã bắt đầu
thật (n=1 hiện tại). Dispatch song song Taylor (góc tín hiệu) + Winston (góc hạ tầng), cả 2 audit
độc lập không trùng việc.

**CRITICAL (Taylor) — ĐÃ FIX, CONFIRMED cả kỹ thuật (quant-skeptic) lẫn rủi ro vận hành (Spyros/
risk-auditor)**: sổ LAG (PEAD, 50-65% NAV khi active) bị mù với sự kiện BCTC mới <30 phiên trong khi
entry là T+5 — 100% entry LAG mùa Q2 sẽ bị bỏ lỡ trong im lặng nếu không sửa. Fix: module mới
`lag_live_schedule.py` (commit `f7463e3`) tách nguồn — identity/NP_R từ pkl fresh-daily (biết ngay
tại ngày release), điều kiện phụ vẫn từ CSV cũ (luôn đủ dữ liệu vì nhìn về quá khứ). Backtest pin R3
byte-identical (không đổi số 27.84/1.84/-18.2/1.53). Bonus: fix còn dọn thêm 1 look-ahead 30-phiên
ẩn khác trong logic cũ (sibling cùng ngày dùng giá trị tương lai) mà không ai từng phát hiện.

**MEDIUM (Winston) — ĐÃ FIX, CONFIRMED**: freshness-check `ticker_financial` đo bằng MAX(time) toàn
bảng, 1 mã early-filer (MBS) đủ để cả check báo "xanh" dù 1254/1255 mã còn lại chưa công bố — nguy
cơ vendor stall giữa mùa im lặng tới 90 ngày. Fix: breadth-probe WARN-only theo mùa BCTC (commit
`1b2fd13`), có guard chống false-positive đầu/cuối mùa.

**3 mục nhỏ Spyros phát hiện thêm — ĐÃ XỬ LÝ HẾT TRONG NGÀY, quant-skeptic CONFIRMED (2026-07-12)**:
- **M1 (MEDIUM) — ĐÃ FIX**: field `lag_source_error` mới trong `golive_v23_status.json` (commit
  `a5f3810`) phân biệt "0 upcoming vì thật sự không có gì" vs "0 vì pkl lỗi". Kèm probe `lag-pkl`
  WARN-only (commit `f84b995`) — dùng "stateful catch-up" (so pkl với chính lịch sử của nó, không so
  tức thời với BQ) để tránh báo giả khi lệch giờ refresh bình thường (15:30 pkl → 19:00 check).
- **L2 (LOW) — ĐÃ FIX** (commit `853080d`): nhãn `ENTERED`/"Đã vào" đổi thành `WINDOW_PASSED`/"Cửa sổ
  entry đã qua — đối chiếu vị thế thực" ở cả 2 bề mặt hiển thị, tránh DollarBill hiểu nhầm là đã có
  vị thế. Xác nhận không code nào parse chuỗi cũ trong pipeline sống.
- **L1 (LOW) — không cần code**, đã document. quant-skeptic **tự tái hiện được đúng** tình huống lỗi
  này (pandas hệ thống không đọc được pkl format mới) khi verify, xác nhận cảnh báo là có căn cứ
  thật, không phải lý thuyết suông.

**KẾT LUẬN: toàn bộ chuỗi audit sẵn sàng mùa BCTC Q2/2026 đã khép kín 100%** — CRITICAL + MEDIUM +
3 mục nhỏ, tất cả đã fix và verify (quant-skeptic + risk-auditor độc lập). Không còn issue nào tồn
đọng trước tuần giao dịch tới. Chi tiết đầy đủ: trace bus `Taylor_20260712_121642` (audit gốc) →
`Taylor_20260712_124834` (fix CRITICAL) → `Spyros_20260712_131501` (phản biện) →
`Taylor_20260712_135148` (fix 3 mục nhỏ); song song `Winston_20260712_122313` →
`Winston_20260712_124928` (fix MEDIUM).

Chi tiết đầy đủ: bus trace `Taylor_20260712_121642` → `Taylor_20260712_124834` (fix) và
`Winston_20260712_122313` → `Winston_20260712_124928` (fix), phản biện `Spyros_20260712_131501`.

## LAG-weight (tăng tỷ trọng PEAD trong allocator) — ĐÓNG, chấp nhận câu trả lời mô tả (2026-07-12)
User chấp nhận kết luận mô tả của Taylor (`plan_lag_weight_20260712.md`) là đủ — KHÔNG chạy family
backtest N=5. Tóm tắt: "LAG bền hơn MOM" đúng một nửa (bền hơn về bề rộng lịch sử, nhưng 2026 hiện
là đáy sâu nhất mẫu); allocator adaptive sẵn có đang nói nên hạ về 50% chứ không phải tăng; capacity
LAG book giới hạn bởi deal-flow (chỉ deploy ~42% vốn) nên tăng trần phần lớn không có tác dụng thật.
Phần fix bug đi kèm (spec-drift w_LAG trong `golive_recommend_v23.py`) đã xong + quant-skeptic
CONFIRMED riêng (commit `a776a9a`). Không mở N-budget mới cho hướng này trừ khi có dữ liệu mới.

## `lag_edge_health.csv` staleness — KHÔNG PHẢI BUG, đã đóng hoàn toàn (2026-07-12, đính chính lần 3)
Chuỗi tiền đề sai liên tiếp, mỗi lần đào sâu hơn lại lộ ra tiền đề TRƯỚC đó cũng sai:
1. Ban đầu: "KHÔNG có lịch refresh tự động" — SAI, `Winston_20260712_114800`/`_121456` xác nhận cron có.
2. Sau đó: "cron có nhưng `--refresh` không catch-up chuỗi LAG edge, bug nằm trong script" — CŨNG SAI.
   Dispatch `Taylor_20260712_155038` (yêu cầu fix logic) trả về: **premise sai, không có bug, KHÔNG
   sửa code** (đúng kỷ luật báo cáo lại thay vì tự mở rộng khi thực tế khác dự kiến). Bằng chứng:
   `lag_edge_health()` chạy VÔ ĐIỀU KIỆN mỗi lần invoke (không phụ thuộc flag `--refresh`), rebuild
   toàn bộ series từ cache daily mỗi lần. Input tươi (`earnings_px.pkl` tới 07-10, `earnings_events_
   classified.csv` rebuild daily). BQ live xác nhận **zero** sự kiện NP_R từ 05-05→07-07 (khoảng trống
   giữa 2 mùa BCTC — có thật, không phải lỗi). Sự kiện kế tiếp (MBS Q2, rel 07-08) cần hold 25 phiên
   mới đủ điều kiện vào series, hoàn tất **~08-19**. Pattern mùa vụ 2012-2025 xác nhận: mọi năm series
   đều dừng ~05-09..05-11 rồi nhảy tiếp ~07-15..07-26 — dừng ở 05-11 ngày 07-12 là ĐÚNG lịch sử. Chạy
   thử thật: CSV ghi đè (mtime advance) nhưng md5 byte-identical — đây chính là "mtime tươi/content cũ"
   bị 2 lần trước đọc nhầm thành staleness.
3. **Kết luận cuối cùng: verdict TROUGH hiện tại (mean12 +0.45%, n=631) là số đúng và tươi nhất có thể
   có — w_LAG gate đọc đúng dữ liệu, KHÔNG có gap production.** Probe WARN-only mtime-check (commit
   `f67e09a`) vẫn giữ nguyên, vô hại (chỉ cảnh báo khi mtime quá cũ so ngưỡng, không liên quan gì tới
   nhầm lẫn content này). Không cần action nào thêm.
4. **Falsifiable check cho tương lai** (Taylor đề xuất, chưa cần làm gì bây giờ): nếu đến ~2026-08-25
   mà `lag_edge_health.csv` VẪN dừng ở 05-11 trong khi `earnings_events_classified.csv` đã có sự kiện
   Q2 đủ điều kiện hold-window — LÚC ĐÓ mới là bug thật, cần dispatch lại kiểm tra.

## Dự án "Q-sleeve" (rổ nhỏ chất lượng cao, cảm hứng AlphaLens) — ĐÓNG, NO-GO cả 2 trục (2026-07-12)
User đề xuất thêm 1 sleeve buy-and-hold rổ nhỏ chất lượng cao (lấy cảm hứng AlphaLens) bổ sung cạnh
BAL/LAG. Scope xong (`plan_quality_sleeve_20260712.md`), family N=5 pre-registered đã duyệt và
chạy: Q8-NEU/Q12-NEU/QF8-NEU (rổ nhỏ thay custom30V) + Q12-BULLEXT (mở rộng giữ cả lúc BULL) + LOO.

**VERDICT: NO-GO cả 2 trục, quant-skeptic CONFIRMED (không có phản bác).**
- **Trục rổ nhỏ thay custom30V**: cả 3 cách chọn đều kém control 2.9-6.8pp IS, LOO âm mọi năm bỏ-ra,
  phần "thắng" ở OOS chỉ là carry thuần từ năm 2021 (+20-24pp riêng năm đó) — đúng chữ ký lỗi đã bác
  ở MOM/fa8l trước đây. Cơ chế: rổ 30 mã hiện tại thắng nhờ breadth/diversification, cô đặc còn 8-12
  mã mất phần đó mà không có gì bù lại.
- **Trục mở rộng BULL/EXBULL**: NO-GO lần thứ 5 liên tiếp (tiền lệ: bull-park, custom30B vehicle, R5,
  DC-book CÂU 1, giờ thêm Q-sleeve) — chết đúng năm tiền lệ hay chết (2025 −19.5pp).
- Diagnostic phụ: excess vốn-điều-chỉnh ÂM so custom30V, 1 mã chiếm 13.24% NAV vượt namecap 10%.

Không đụng production/canonical/trading_rules. Registry đã ghi mục "2026-07-12 — Q-SLEEVE". N-ledger
5/5 đóng sổ, không mở thêm trial.

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
  (giống mẫu `fa_ratings_8l`) + wire freshness-check. (a) fix pandas-3 nhỏ: XONG (commit `7d89c28`).

**VẤN ĐỀ (b) BQ-write-identity ĐÃ GIẢI QUYẾT XONG (2026-07-12, sớm 6 ngày so với kế hoạch chờ cron
07-18)** — user duyệt trực tiếp cho test ghi thật ngay hôm nay thay vì chờ thụ động. Root cause xác
nhận: cả 2 wrapper `refresh_fa_ratings_8l.sh`/`refresh_fa_ratings.sh` thiếu dòng `source wc_env.sh`
(mọi script ghi-BQ-thành-công khác trong repo đều có dòng này để đặt `CLOUDSDK_CONFIG` sang tài
khoản read-write `dtienthanh@gmail.com`; thiếu nó → rơi về default read-only `bq-reader-8l`). Fix 1
dòng mỗi script (commit `a9716f6`, repo mike). **Test ghi THẬT (không phải dry-run) thành công cả 2
bảng**, verify bằng `bq show` độc lập: `fa_ratings_8l` lastModified 06-20→**07-12**, rows
52.433→52.449; `fa_ratings` lastModified 05-10→**07-12**, rows 12.367→12.406, invariant 48/48 quý
đóng băng giữ nguyên (net delta +39 = đúng tổng 2 quý mở re-rank, số học khớp chính xác). quant-
skeptic CONFIRMED độ tin cậy cao (tự tái hiện toàn bộ số liệu). Cron thứ Bảy 07-18 giờ chỉ là lần
chạy scheduled đầu tiên bình thường (kỳ vọng OK), không còn câu hỏi identity treo — **dự án fa_ratings
rebuild coi như hoàn tất**, chỉ còn theo dõi thụ động qua các lần chạy tự động.

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

**✅ XÁC NHẬN XONG (2026-07-13, sau cron 18:30 ICT) — mục 1-2 đã kiểm chứng trực tiếp bằng BQ:**
1. ✅ `vnindex_5state_dt5g_live` + bảng gốc: NEUTRAL(3) liên tục 07-06→07-13, có đủ dòng 07-10/07-13
   mới, episode BULL giả đã biến mất hoàn toàn — khớp chính xác counterfactual đã verify trước đó.
   User tự phát hiện report vẫn hiện "9/10→BULL" lúc 16:00 ICT (TRƯỚC giờ cron) — đã giải thích rõ
   đó là dữ liệu cũ do report được xem trước khi cron chạy, không phải fix thất bại.
2. ✅ `custom30v_8l` writer đã hồi sinh, republish đúng lịch (lastModified 15:32 ICT hôm nay, qua
   cron papertrade riêng — khác giờ cron DT5G).
3. **Còn lại**: `19:00 ICT freshness-check 8 bảng` chạy thật lần đầu — CHƯA tới giờ kiểm tra (hiện
   18:37 ICT), Mike cần tự kiểm tra sau 19:00 xem có 2 WARN hợp lệ, 0 false-block không.

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

  **⚠️ AGENDA SỬA tại mốc review (thêm 2026-07-13, job `Taylor_20260713_100550`, user xác nhận CHƯA
  sửa ngay — để tự nhiên chạy sai thêm một thời gian nhằm quan sát whipsaw thật qua đúng đợt LAG
  refill, rồi sửa gộp 1 lần tại mốc review).** Phát hiện quan trọng: **paper sleeve ĐANG CHẠY SAI so
  với chính spec đã backtest/pin** — dùng trigger NHỊ PHÂN (BAL/LAG có deal → tắt hẳn DC book) thay vì
  spec đúng là DC book chạy LIÊN TỤC trên phần tiền dư (residual). Hậu quả đo được: 57.8% ngày
  NEUTRAL-có-✓✓ vẫn có deal BAL/LAG mới trong khi tiền park còn ~38% NAV → bản nhị phân đang chạy hiện
  tại **TỆ HƠN CẢ baseline không có DC book** (CAGR 27.26% / DD −17.8% / Calmar 1.53 / turnover 20.7×,
  so với spec đúng 27.56% / −15.5% / 1.77 / 3.18× và baseline R3 27.35% / −17.6% / 1.55). 4 việc cần
  làm tại mốc review, theo đúng thứ tự ưu tiên:
  1. **Đổi trigger sang continuous-residual** (quan trọng nhất — đây là bug thực chất, không phải tối ưu thêm).
  2. Đồng bộ lịch rebalance DC book vào q2m5 (giống custom30V) — tự giảm whipsaw ~4 lần, đã backtest (job `Taylor_20260706_173317`).
  3. Cap gộp 0.15/tên (chống trùng mã DC↔custom30V vượt trần name_cap 10% NAV khi sleeve lớn — job `Taylor_20260707_042827`).
  4. Liquidity floor 3B thay hard-exclude DHG đơn thuần (job `Taylor_20260707_042827`).
  Đã kiểm tra kỹ 4 góc còn lại (sizing/depth-weight, ✓✓ làm tiebreaker BAL/LAG, mở rộng CRISIS/BEAR,
  sector-lens đứng riêng) — **không còn không gian cải thiện thật**, không cần backtest thêm cho các
  góc đó khi tới review, chỉ cần làm đúng 4 việc trên.

## V2.5 leverage — VERDICT: NO-GO, giữ DISABLED (2026-07-12, quant-skeptic CONFIRMED)
User hỏi "V2.5 đã đủ tự tin chuyển production chưa" (mốc nhắc 2026-07-07 đã treo quá hạn) — Mike tự
đọc lại toàn bộ lịch sử research, phát hiện edge +0.92pp trước đây có dấu hiệu thiếu vững (mẫu
mỏng, OOS-only, mâu thuẫn nhãn "Spyros-approved" MGE 1.3 vs 1.5). User duyệt làm 1 vòng kiểm tra bổ
sung: giải quyết mâu thuẫn approval + LOO theo episode + DSR/PBO riêng cho lever.

**Kết quả:**
1. **Mâu thuẫn MGE giải quyết**: nhãn "Spyros-approved" MGE 1.5 trong `trading_rules.json` là ĐÚNG
   — Spyros REJECT 2.0/APPROVE 1.5 có điều kiện (06-27), điều kiện còn hiệu lực: "bất kỳ S4 fire nào
   ở 1.5x trong 6 tháng đầu → dừng+review".
2. **LOO + DSR (quant-skeptic tự tái hiện độc lập, kể cả bằng md5 checksum)**: edge +0.92pp FULL
   thực ra là **IS-artifact** (IS +1.88pp, **OOS −0.05pp** — fail thẳng quy chuẩn "rớt OOS = loại").
   Cơ chế tách khỏi baseline từ **2014** (6 năm trước lần lever đầu tiên) = path-divergence, không
   phải alpha thật. LOO: 2 trong 3 episode (2022/2023) bị trần NAV 100B vô hiệu hoàn toàn (CSV
   byte-identical, xác nhận bằng md5); chỉ COVID-2020 thực sự lever, đóng góp ròng **+0.04pp**. DSR
   trên excess series = 0.18-0.56 (RED FLAG mọi N, ngưỡng an toàn ≥0.95). LEVnocap (proxy đúng cho
   NAV live ~1B, trần không bind) → OOS **âm** (-0.19pp).
3. **VERDICT: NO-GO, giữ V2.5 DISABLED.** quant-skeptic CONFIRMED độ tin cậy cao — không tìm được
   lỗ hổng, đồng ý đây là kết luận thận trọng đúng đắn (n=1 episode hiệu dụng không đủ CHỨNG MINH
   lever xấu, nhưng cũng không đủ để tin nó tốt — mặc định DISABLED là đúng cho hệ thống đang live).

**Điều kiện tái xét sau này** (không tự động, cần user quyết lại khi đủ điều kiện):
(a) tích lũy thêm episode capitulation qua theo dõi S2 trigger trên paper (không bật gì ở live);
(b) nếu đo lại: đổi phương pháp sang episode-windowed sim (±60 ngày quanh từng episode, cùng path
nền) thay vì diff 2 full-run — tránh lẫn path-divergence noise; gate = DSR excess ≥0.95 + OOS-dương.

Chi tiết đầy đủ: `data/results_registry.md` mục "V2.5 LEVERAGE VERIFICATION" (2026-07-12), trace bus
`Taylor_20260712_054553` → `Taylor_20260712_063143`.

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

## Audit cron toàn hệ thống XONG (Winston_20260712_142100) — 2 fix đang dispatch (2026-07-12)
User yêu cầu review thứ tự cron. Kết quả: **thứ tự ĐÚNG**, nhưng lộ 2 bug nội dung khẩn:
- **C1 CRITICAL** (tự verify độc lập bằng code+BQ live, xác nhận đúng 100%): `publish_gated_state.py`
  đọc DT5G qua `BQ_LOCAL_CACHE` (T-1) thay vì live — với `MAX_STATE_LAG=0` (siết 07-11), thứ Hai
  07-13 19:00 sẽ FAIL, không dispatch DollarBill. Dispatch Taylor (fable) fix ngay hôm nay: job
  `Taylor_20260712_151135`.
- **H2 HIGH**: check `shares_outstanding_live` calibrate sai giả định → false-BLOCK ~thứ Tư 07-15.
  Đề xuất hạ BLOCK→WARN — CHƯA dispatch, chờ quyết sau khi C1 xong.
- Phụ: M5 (executor.py đọc ticker_prune.parquet monolith chết từ 06-26, ảnh hưởng 2 paper trial
  evidence), M4 (sync_bq_cache thiếu `|| true`), M3 (optional reorder pt_8l/telegram sau 19:00).
- Bản thảo quy tắc "thêm cron mới đặt giờ nào" ở Phần 5 `mike/agents/Winston/audit_cron_order_20260712.md`
  — CHƯA chính thức hoá thành `kb/cron_registry.md`/coding_guidelines, còn nợ.

User đồng thời yêu cầu dọn crontab paper-trading lạc hậu (dựa production hiện tại V2.4 + version
numbering + research đã đóng: V2.5 lever NO-GO, Q-sleeve NO-GO, DVR-8L NO-GO, momentum-deals NO-GO
đã production-thực-thi-rồi, fa8l CP2 NO-GO). Dispatch Winston (fable) research + đề xuất diff (KHÔNG
tự sửa crontab thật): job `Winston_20260712_151206`. Việc còn đang chạy: EXTREME (~07-28), chase-cap
(~07-14), fill-timing (~cuối tháng 7), DC-book (event-anchored) — KHÔNG được đụng.

**Còn nợ sau khi 2 job trên xong**: verify C1 fix (quant-skeptic), quyết H2, formalize cron_registry.md,
áp dụng diff dọn crontab (sau khi tôi review), dispatch Taylor xem lại M5 (2 paper trial evidence).

## C1 CRITICAL (publish DT5G qua BQ_LOCAL_CACHE) — FIX + COMMIT + VERIFY XONG (2026-07-12)
Fix: `deploy_golive_dt5g_v4/publish_gated_state.py` — `os.environ.pop('BQ_LOCAL_CACHE', None)` process-
local trước import `macro_state_live` (commit `4995262`, repo WorkingClaude). Cả 2 attempt dispatch
Taylor đều timeout (tự mở rộng phạm vi sang backfill C1b không cần thiết — Monday's daily_refresh tự
recompute full window nên không cần backfill riêng); Mike tự verify code + tự commit + dispatch
quant-skeptic bằng `--claim` (không có finding event chính thức từ Taylor do timeout).
**quant-skeptic CONFIRMED (high confidence)**: độc lập tái lập cơ chế bằng Python replica thật (pop
env → cache branch bypass → live path), xác nhận process-local (mỗi step trong daily_refresh/
bq_freshness_check chạy subprocess riêng, không leak sang sibling), không side-effect logic khác.
1 ghi chú tùy chọn (pop thêm `LOCAL_SNAPSHOT_DIR`) — hiện vô hại vì biến chưa được export ở đâu.
**Xong, không còn gì treo cho C1.** H2 (shares_outstanding_live false-BLOCK ~07-15) vẫn CHƯA quyết.

## Plan ZaloPay 07-13 (transition day 5/5 FINAL) — user duyệt trực tiếp (2026-07-13, 08:45 ICT)
User duyệt qua Mike sau khi được trình bày chi tiết: bán VIB 9.200cp (~146,7M) + mua BID 900cp
(~36,9M, bù miss ngày 4). `approved_by=user`/`mafee_authorized=true` đã ghi vào
`data/trade_plans/plan_ZaloPay_2026-07-13.json` lúc 08:45 ICT (~20' trước giờ chạy 09:05). Mirror
vào DollarBill plan channel + trả lời bus question `zalopay-plan-0713-chua-duyet-bot-van-chay`
(option A). Đây là ngày cuối transition 5 ngày (07-07→07-13), 4 ngày trước đã thực thi đúng.

**User chỉ đạo quy trình quan trọng cùng lúc**: yêu cầu duyệt plan phải đến tay user TRƯỚC ngày
giao dịch 1 ngày, không được để tái diễn tình huống sáng nay (plan sửa lỗi ngày lúc 22:17 tối
07-10 không ai gửi lại cho duyệt, nằm im tới sáng 07-13 08:20 mới bị ops_health_check phát hiện
CRITICAL — đã ghi đầy đủ `kb/INCIDENTS.md`). Dispatch Winston (fable) thiết kế + implement "second
chance" re-check muộn hơn trong đêm (đề xuất 23:00 ICT, trước sync_bq_cache 23:45) — chạy lại
`send_plan_report.sh` idempotent (không gửi trùng nếu 21:00 đã gửi thành công, có gửi nếu file
plan được sửa/tạo lại sau 21:00): job `Winston_20260713_014816`. KHÔNG đụng bot_execute.py/executor
(vùng cấm riêng, code-gate approval là quyết định khác, cần user sign-off riêng — chưa làm).

## Second-chance re-send cron ĐÃ CÀI + code-gate approval đang thiết kế (2026-07-13)
User duyệt cron backup (`0 16 * * 1-5 ... send_plan_report.sh --second-chance`, 23:00 ICT) —
đã cài + verify (crontab -l xác nhận, dry-run thật trên production path OK). quant-skeptic
CONFIRMED (high) commit `4216295` trước khi cài.

User đồng thời duyệt luôn root-cause 2 (code-gate cứng trong `bot_execute.py`, vùng cấm executor,
cần sign-off riêng — đã có). Dispatch Taylor (fable) job `Taylor_20260713_021202`: BẮT BUỘC điều
tra hành vi thực tế requires_user_approval/approved_by trên plan 2 tuần gần đây của cả SpaceX lẫn
ZaloPay TRƯỚC khi viết code — rủi ro lớn nhất là nếu TOÀN BỘ plan hàng ngày đều đặt
requires_user_approval=true theo triết lý canonical.md nhưng chưa ai set approved_by (vì trước
giờ không gate nên không ai cần) → bật gate sẽ chặn oan giao dịch thường lệ SpaceX sáng mai. Đã
dặn Taylor DỪNG báo cáo lại nếu phát hiện rủi ro này, không tự quyết cách xử lý.

## Code-gate approval trong bot_execute.py XONG (commit 27e1282) — quant-skeptic CONFIRMED, 1 hardening nhỏ đang vá (2026-07-13)
Taylor điều tra kỹ trước khi code (yêu cầu quan trọng nhất): 24 plan thật 06-30→07-13 xác nhận
SpaceX thường lệ dùng `requires_user_approval=false/approved_by="auto"` — gate KHÔNG chặn giao
dịch thường lệ. Paper `main` thiếu field hoàn toàn → backward-compat default=False (an toàn, không
chặn 3 paper trial đang chạy). Bonus: phát hiện `load_plan()` từng ÂM THẦM LỌC MẤT field approval
khỏi dataclass — gate không thể hoạt động nếu không fix cả chỗ này. Gate wire trước lock/broker
connect, fail-safe exit 2 + alert Discord/Telegram/bus khi chặn, HOLD (0 lệnh) không bao giờ bị
chặn. Selfcheck mới 16/16 PASS + regression 6/6 PASS + E2E 2 chiều PASS + audit 20 plan thật (chỉ
đúng 1 plan lịch sử từng là lỗ hổng thật bị chặn, 0 false-block).

**quant-skeptic CONFIRMED (high)** — tự tái lập toàn bộ selfcheck + audit. Tìm 1 lỗ hổng residual
thật: `approved_by` không chuẩn hoá string như `requires_user_approval` — plan ghi `"approved_by":
"None"` (chuỗi literal) sẽ KHÔNG bị chặn (false-negative). Chưa xảy ra trong luồng hiện tại nhưng
là lỗ hổng thật trong lớp an toàn. Dispatch Taylor vá ngay (job `Taylor_20260713_023002`): normalize
approved_by giống requires_user_approval, thêm 2 selfcheck case, verify lại.

**Gate có hiệu lực từ cron 09:05 sáng 07-14** — từ nay plan `req=true` phải có `approved_by` thật
trước giờ chạy, không thì bot tự chối + alert (đúng ý user yêu cầu, khớp cron second-chance 23:00).

## Hardening approval gate: normalize approved_by string 'None'/'null'/'nil'/'nan' = chưa duyệt XONG (commit 54d488c, 2026-07-13)
Vá lỗ hổng residual quant-skeptic tìm thấy — `approval_block_reason()` giờ coi các chuỗi
lowercase `{none,null,nil,nan}` là approved_by trống → BLOCK. Selfcheck 19/19 PASS (file gốc 17
check chứ không phải 16 như dự kiến, đính chính) + regression 6/6 PASS. quant-skeptic CONFIRMED
(high) — tự tái lập false-negative pre-fix, xác nhận không false-block approver thật.

**Chuỗi việc hôm nay đã khép kín hoàn toàn (đều quant-skeptic CONFIRMED):**
1. Plan ZaloPay 07-13 duyệt + thực thi đúng giờ.
2. Cron `send_plan_report.sh --second-chance` 23:00 ICT — đã cài, chống tái diễn "plan sửa sau
   21:00 không được gửi lại duyệt" (commit `4216295`).
3. Code-gate approval cứng trong `bot_execute.py` (commit `27e1282`) + hardening residual
   (commit `54d488c`) — có hiệu lực từ cron 09:05 sáng mai 07-14.

## Báo cáo tuần 07-06→07-10 đã gửi + cơ chế chống tái diễn đã cài (2026-07-13)
User phát hiện báo cáo tuần bị bỏ sót (không có cron tự động, phụ thuộc Mike tự nhớ). Đã xử lý:
1. Soạn báo cáo tuần đầy đủ (Taylor, dùng đúng pipeline verify_account_snapshot.py/nav_history) —
   Mike tự đối chiếu mọi số NAV/% với CSV thật trước khi gửi, khớp chính xác tuyệt đối. File:
   `mike/reports/SpaceX_ZaloPay_weekly_report_2026-07-06_to_2026-07-10.md`. Đã gửi Trading report
   topic (1522576692638388364), user duyệt trước khi gửi.
2. Thêm check WARN vào `ops_health_check.sh` (commit `7147ac3`): tự cảnh báo khi báo cáo tuần
   (thứ Hai, >7 ngày) hoặc tháng (từ ngày 5, chưa có báo cáo tháng trước) quá hạn — chống tái diễn.

## Audit dữ liệu 8L XONG (Winston_20260713_100733) — 3 fix đang dispatch (2026-07-13)
User lo ngại dữ liệu 8L có phản ánh đầy đủ thông tin hệ thống hay không (mùa BCTC Q2 đang bắt đầu).
Audit xác nhận: **hôm nay dữ liệu 8L ĐẦY ĐỦ** — chỉ 1 mã (MBS) đã công bố Q2, đã có mặt đúng ở cả
3 lớp rating. Phát hiện 2 vấn đề kỹ thuật:
- Cron `fa_ratings_8l` thứ Bảy 07-11 chưa từng chạy tự động (bảng tươi nhờ ghi tay 07-12); lần
  scheduled đầu tiên = thứ Bảy 07-18, cần để mắt xác nhận.
- Cache local (research/backtest, KHÔNG phải đường tiền thật) lệch do sync mode `--delta` không
  tương thích cách refresh mới → tối nay 23:45 sẽ tự bắn 1 cảnh báo ĐÚNG NHƯNG không phải sự cố
  thật (by design), sẽ lặp mỗi tuần nếu không sửa.
- Điểm cần lưu ý: rebalance quý ~08-05, mã công bố 08-02..08-04 sẽ chưa kịp có rating Q2.

User duyệt cả 3 đề xuất Winston: (1) sửa cache sync sang full-download cho 2 bảng rating; (2) tăng
tần suất refresh 2x/tuần trong mùa BCTC cao điểm (~4-6 tuần, tới ~08-05); (3) cập nhật 3 chỗ tài
liệu lỗi thời trong `data_registry.md`. Dispatch job `Winston_20260713_103213`.

## User tự phát hiện BQ local cache stale — vấn đề LỚN HƠN dự kiến (2026-07-13)
User hỏi lại "BQ local đang stale, trễ mấy ngày" sau khi tôi báo cáo đã fix xong 8L cache (chỉ
verify fa_ratings/fa_ratings_8l, KHÔNG kiểm tra toàn bộ bq_cache). Tự kiểm tra phát hiện:
`data/bq_cache/ticker_prune.parquet` (monolith) đứng yên từ **06-26** (17 ngày) trong khi thư mục
chunked thay thế (`ticker_prune/<year>.parquet`) vẫn đồng bộ đúng — sync_bq_cache.py đã migrate
sang chunked quanh 06-26 nhưng monolith cũ không ai xoá/cập nhật.

**Blast radius LỚN**: grep xác nhận **27 file** vẫn đọc thẳng monolith cũ — không chỉ
`trading_bot/executor.py:507` (đã biết từ audit M5 hôm qua), mà còn 17 sector-screener script +
9 script backtest/research khác (gap_fairvalue_*, gq_score_gate, neutral_glide_backtest,
converge_union_test, lag_dnpr_event_study, gap_adaptive_proxy, gap_ev_by_liquidity).

Dispatch song song: `Winston_20260713_143546` (fix đường dẫn đọc cho cả 27 file, archive
monolith cũ theo coding_guidelines §10) + `Taylor_20260713_143629` (đánh giá tác động — finding
nào từ 06-26 tới nay đã dùng dữ liệu đông băng, ưu tiên cao nhất: chase-cap vol-scale review dự
kiến MAI 07-14 có bị ảnh hưởng rvol_20d/prior_close không).

## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-01. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`). **Live từ 2026-07-01.**

### Mục tiêu
Vận hành chiến lược **production V2.4**, **go-live 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- **R3 NEUTRAL-only @50B: CAGR 27.84% / Sharpe 1.84 / DD −18.2% / Calmar 1.53** (pin threads=1,
  re-pin 2026-07-12 sau khi đóng kênh MOM_N/MOM_S trong TIER_BAL — commit `4fbd492`, quant-skeptic
  CONFIRMED; xem `data/results_registry.md` + `plan_close_mom_20260712.md`). Số cũ 28.05%/28.82% đã
  lỗi thời qua 2 lần re-pin (DT5G swap 07-11, rồi MOM closure 07-12).
- Bootstrap 5th-pct: CAGR 18.6%, DD −28.6% (anchor DD ~−29%, KHÔNG phải −18%).
- **NEUTRAL parking custom30V = phần tin cậy nhất: +7.4pp Full.** (30 mã, cap 0.10)
- Bull parking: NAV ≥150B. **(30, 0.15) = OVERFIT**, walk-forward bác.
- **V2.5** (future) = V2.4 + lever MGE=1.5, account sẵn sàng, DISABLED, reminder 2026-07-07.

### Đã thử, BỊ LOẠI — không wire
custom30V permanent-exclude 7 tên (−1.0pp); LAG SUE-tilt 3 tầng (−0.66pp); hold-neutral exit (−47B);
stability floor ROE_Min<0 (−0.45pp); liq-tilt custom30 (REFUTED); deep-discount sleeve (PARKED);
pbcombo dual-vehicle (Calmar 1.48→1.37); gq_score growth gate (−IC); composite v3 as entry-selector (NO).

### MOM_N/MOM_S ĐÃ ĐÓNG (2026-07-12) — không phải "thử bị loại", là thay đổi production chính thức
Sau chuỗi R&D đầy đủ (momdeal Phase 1 CP1 NO-GO 0/13 feature → nhánh DVR-8L-sizing CP-DVR1 NO-GO →
đo tác động Scope A/B → kiểm tra tách MOM_N-vs-MOM_S, tất cả quant-skeptic CONFIRMED), user duyệt
đóng `MOMENTUM_N`+`MOMENTUM_S` khỏi `TIER_BAL` (giữ nguyên `MOMENTUM`/`MEGA` generic — Scope B đóng
cả họ bị số đo bác, generic vẫn đóng góp thật). Lý do: thành công lịch sử của 2 tier này chủ yếu do
dồn mẫu regime 2020-21, không phải pattern lặp lại được; hậu-2021 gần như hoà vốn. Chi tiết đầy đủ:
`plan_close_mom_20260712.md`, `plan_dvr_8l_sizing_20260712.md`, `plan_momentum_deals_20260711.md`.

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
