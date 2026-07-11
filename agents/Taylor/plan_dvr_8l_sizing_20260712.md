# PLAN — Rule sizing DVR theo 8L rating + route (nhánh (b) sau CP1 NO-GO momentum-deals)
> Taylor, 2026-07-12 · job Taylor_20260711_232012 · trạng thái: **SCOPE XONG — CHỜ USER DUYỆT, CHƯA CHẠY BACKTEST NÀO**
> Trial MỚI, sổ N riêng (không dùng lại N-ledger 14 test đã đóng của momentum-deals Phase 1).

## 1. Bối cảnh & điểm khởi đầu

Phase 1 momentum-deals (CP1 NO-GO, quant-skeptic CONFIRMED) cho ra 1 insight cấu trúc từ cohort
đối chứng DVR (mô tả, không phải trial): **8L rating + route phân tách RÕ thắng/thua ở kênh
DEEP_VALUE_RECOVERY nhưng KHÔNG phân tách ở MOM**:
- F1 rating (thang 8L 1–5, thấp = tốt): Cliff δ = **−0.127**, p=0.002, FDR-PASS (winners có rating tốt hơn).
- F2 route (lens ngành 8L): Cramér V = **0.259**, p=9e-9, FDR-PASS — effect mạnh nhất trong 13 feature.
- Cũng PASS ở DVR: T1 ta (+0.093), C2 state5 (−0.080), C3 days_since_release (−0.112) — nhỏ, không làm rule.

Breakdown mô tả trên đúng dữ liệu Phase 1 đã đóng (724 episode labeled S/F, kênh DVR, L2 = profit_2M
≥+10% vs ≤0%; KHÔNG phải trial mới — chỉ đọc lại bảng đã build):

| Trục | Nhóm | n | win-rate FULL | win-rate ex-2021 |
|---|---|---|---|---|
| route | SECURITIES | 98 | **76.5%** | 72.1% (n=43) |
| route | REALESTATE / CYCLICAL / BANK / INSURANCE | 274 | 56–61% | 50–67% |
| route | **COMPOUNDER** (48% mẫu!) | 349 | **41.3%** | 36.2% (n=196) |
| route | POWER | 3 | 0% | (n=2, bỏ qua) |
| rating | 1–2 | 222 | 59.5% | 47.8% |
| rating | 3 | 287 | 54.0% | 52.2% |
| rating | **4–5** | 215 | **43.3%** | **37.8%** |
| kết hợp | route≠COMPOUNDER ∧ rating≤3 | 304 | **63.5%** | 57.7% |
| kết hợp | phần còn lại | 420 | 44.5% | 39.7% |

Per-year: hướng phân tách của gate kết hợp GIỮ NGUYÊN mọi năm 2017–2025 (2018: 72% vs 41%; 2021:
68% vs 51%; 2025: 40% vs 21%); chỉ 2026 flip (n=9 — quá nhỏ). Grid route×rating cho thấy 2 trục
độc lập một phần: rating 4–5 làm hại BANK/COMPOUNDER/REALESTATE nhưng không hại SECURITIES/CYCLICAL;
COMPOUNDER tệ ở CẢ 2 nhóm rating (46%/35%).

**Đọc effect size trung thực (điểm 4 của dispatch):** δ=−0.127 của rating là **small** theo convention
Cliff (|δ|<0.147) — p=0.002 chỉ nhờ n lớn, KHÔNG phải effect lớn. Route V=0.259 là **medium**, và
contrast chính (COMPOUNDER 41% vs còn lại 62%) là chênh lệch win-rate ~20pp trên kênh chiếm gần nửa
mẫu — đây mới là trục đáng làm rule. Kết luận scale ở §7.

## 2. DVR đã dùng 8L ở đâu trong hệ thống? (điểm 2 dispatch — audit chống trùng lặp)

Đã tra `mike/kb/data_registry.md` + grep production code. Hiện trạng:

| Chỗ | Dùng 8L thế nào | Có chạm DVR không |
|---|---|---|
| Entry gate DVR (`signal_v11_sql.py:134`) | **KHÔNG** — DVR định nghĩa bằng `fa_tier='C'` (bảng **legacy `fa_ratings`** A–E) + ta≥100 + state5∈(4,5) + np/rev_yoy>20% | Là chính nó — entry hoàn toàn legacy, chưa có 8L |
| `regime_size_overlay.py` (VALIDATED, prod) | Half-size 10%→5% cho tên rating8l≥4, **CHỈ trong state 1–2** (CRISIS/BEAR) | Về danh nghĩa có (DVR nằm trong base_tiers), nhưng **dormant với DVR tại entry**: 912/912 episode DVR entry ở state 4 (773) hoặc 5 (139) — không bao giờ ở state≤2. Chỉ có thể chồng nếu vị thế giữ sang lúc state rơi ≤2 (hiếm, xem rủi ro §8.6) |
| custom30V basket (`custom_basket.rating_asof`) | gate rating≤3 cho rổ parking | Khác sleeve — parking NEUTRAL, không phải kênh deal DVR |
| DC-book double-confirm (paper) | 8L rating≤2 | Khác sleeve (paper) |

→ **Rule mới = BỔ SUNG hoàn toàn mới cho kênh DVR** (entry-time, mọi state DVR fire được), KHÔNG
phải refine logic 8L nào sẵn có trên DVR. Điểm tiếp nối duy nhất: ngưỡng **rating≥4 = fragile** lấy
đúng prior art đã validate của `regime_size_overlay` (fragility là ABSOLUTE rating, không phải
per-group tier — nghiên cứu cũ đã bác bản relative) — tái dùng ngưỡng cũ thay vì tune ngưỡng mới,
vừa có prior độc lập vừa không tốn N.

Nguồn dữ liệu (đã tra registry §9 guidelines): `tav2_bq.fa_ratings_8l` = **CANONICAL** as-of PIT
(ticker, eff_date, route, rating 1–5). Caveat đang mở: cron weekly refresh chưa xác nhận ghi được
(test tay 07-11 fail vì service account read-only; lần cron thật đầu tiên thứ Bảy 07-18) — với
BACKTEST as-of tới 2026-06 thì bảng hiện tại (lastModified 06-20) đủ; wiring LIVE phải chờ cron
xác nhận OK.

## 3. Sizing-tilt hay gate? (điểm 1 dispatch) — CHỌN SIZING-TILT

Cân nhắc 2 hướng:

**(a) Sizing-tilt** (giảm size cho DVR entry có route/rating xấu, giữ full cho tốt) — **CHỌN**:
1. Effect size chỉ small–medium → không đủ mạnh cho quyết định nhị phân loại hẳn; win-rate nhóm xấu
   ~41–44% không phải "chắc chắn thua", chỉ là coin flip kém — half-size đúng bản chất thông tin hơn cut.
2. COMPOUNDER-route chiếm **48% episode DVR** và DVR là kênh episode LỚN NHẤT của BAL (1.077 ep, hơn cả
   toàn bộ MOM family 789) — hard gate cắt gần nửa breadth kênh lớn nhất → deal-scarcity, dồn capital
   về parking/ít tên hơn, đổi cấu trúc book nhiều hơn mức insight cho phép. Tilt giữ breadth, chỉ dịch capital.
3. Nhất quán kiến trúc: `regime_size_overlay` đã thiết lập đúng pattern này (split `<tier>_W`, tier-weight
   riêng) và đã VALIDATED — rule mới tái dùng cơ chế engine sẵn có, không cần plumbing mới.
4. Lý thuyết: DVR là play "hồi phục/beta" — chạy tốt trên route chu kỳ–tài chính (SECURITIES/REALESTATE/
   BANK/CYCLICAL) nơi "rẻ vì chu kỳ" thật sự mean-revert; route COMPOUNDER mà rơi vào fa_tier C thường là
   "business chất lượng đang gãy" — rẻ vì suy giảm cấu trúc, không phải chu kỳ → value-trap. Đúng quan điểm
   user: lens per-route của 8L cho thông tin THẬT mà thang A–E trộn chung không thấy.

**(b) Hard gate** (loại DVR entry route/rating xấu) — KHÔNG chọn làm hướng chính, vì lý do 1–2 trên.
Khai báo rõ: KHÔNG có variant hard-gate trong family lần này (giữ N nhỏ); nếu tilt thắng rõ mà user
muốn đo thêm bản gate thì đó là trial mới cần duyệt N riêng.

## 4. Candidate rules — pre-registered (≤3 variant, không tune ngưỡng)

Mọi ngưỡng lấy sẵn từ prior art / category tự nhiên — KHÔNG có tham số tune trong family:
- Ngưỡng rating: **≥4** (đúng `WEAK_RATING_MIN=4` của regime_size_overlay, đã validated).
- Route xấu: **COMPOUNDER** (+POWER gộp cùng vì n=5 quá nhỏ để đứng riêng và win 0% cùng chiều;
  category, không có ngưỡng số).
- Size giảm: **10% → 5%** (đúng FULL_SIZE/WEAK_SIZE hiện hành, không mở tham số mới).

| ID | Rule (áp tại entry DVR, mọi state DVR fire) | Giả thuyết |
|---|---|---|
| **R1 route-tilt** | route ∈ {COMPOUNDER, POWER} → size 5%; còn lại 10% | Trục mạnh nhất (V=0.259) đứng một mình đủ chưa |
| **R2 fragility-tilt** | rating8l ≥ 4 → size 5%; còn lại 10% | Mở rộng nguyên lý regime_size (đã validated ở stress-state) sang entry-time DVR |
| **R3 combined-tilt** | multiplicative: ×0.5 nếu route xấu, ×0.5 nếu rating≥4, floor 2.5% (tức 10/5/2.5%) | 2 trục độc lập một phần (grid §1) → kết hợp bắt được nhiều thông tin nhất |

Thiếu rating/route (không có row as-of tại entry — hiếm, coverage 8L 100% family từ 2014-07): coi như
nhóm TỐT (full size) — fail-open, rule chỉ được phép giảm size khi có bằng chứng xấu, không phạt vì thiếu data.

**Sổ N-ledger "DVR-8L-SIZING" — khai báo đóng tại đây: N = 5**
1–3. R1, R2, R3 qua full harness (3 trial chính).
4. Sensitivity size-giảm cho CONFIG THẮNG duy nhất: 5% → 7.5% (1 trial, kiểm robust, không chọn lại winner bằng nó).
5. Ablation LOO ex-2021 + ex-2020 cho config thắng (đếm 1 trial gộp — chỉ đọc, không đổi lựa chọn).
KHÔNG mở thêm test nào sau khi chạy. Nếu giữa chừng "muốn thử thêm" → dừng, xin user duyệt N mới.

## 5. Harness & tiêu chí GO/NO-GO (CP-DVR1, checkpoint duy nhất)

**Harness**: `pt_v23_audit_2014.py` integrated @50B, threads=1, đúng pinned command + `$DNA_PYEXE`
(guidelines §8) — baseline đối chứng = **R3 re-pinned mới: CAGR 28.82% / Sharpe 1.90 / MaxDD −15.7% /
Calmar 1.83** (sau fix F3 base-leak, KHÔNG dùng số 28.05% cũ). Output đặt tên `_exp_dvr8l_<id>` —
tuyệt đối không đè filename canonical. Self-check 0 VND bắt buộc mỗi run.

Cơ chế cài đặt: tái dùng pattern `regime_size_overlay` — split row DVR thành tier phụ
(`DEEP_VALUE_RECOVERY_X`) với tier-weight riêng; không sửa SIGNAL_V11 SQL, không đổi entry set —
CHỈ đổi weight. Diff dự kiến nhỏ (~30–50 dòng, 1 module riêng + 3 dòng wire trong pt_v23).

| Gate CP-DVR1 | Tiêu chí GO (config thắng phải đạt TẤT CẢ) |
|---|---|
| OOS 2020+ | CAGR **và** Calmar ≥ baseline R3 (không chỉ CAGR) |
| Walk-forward IS 2014–19 | Không tệ hơn baseline quá 0.3pp CAGR (DVR fire ít pre-2020, kỳ vọng ~flat) |
| Per-year LOO | Delta vs baseline KHÔNG âm ở mọi năm bỏ-ra, **đặc biệt ex-2021 và ex-2020** (DVR dồn 2 năm này) |
| Tail | MaxDD không xấu hơn baseline |
| DSR | ≥ 0.95 trên NAV daily của config chọn (N=5 khai báo ở trên đưa vào deflation) |
| PBO | Family 5 < 8 → không bắt buộc theo quy chuẩn; báo cáo CSCV nếu chạy được, không làm gate |
| quant-skeptic | CONFIRMED bắt buộc trước khi trình user |

NO-GO = không config nào đạt đủ → đóng nhánh (b) đúng quy trình (như CP1/CP2 trước), ghi registry, không wire.
GO ≠ wire: GO chỉ = trình user sign-off; thay đổi áp LIVE luôn cần user duyệt riêng (trading_rules/plan flow).

**Kỳ vọng độ lớn đặt trước (chống tự lừa):** rule chỉ dịch chuyển weight bên trong 1 kênh của BAL
(BAL ≈ nửa NAV allocator) — kỳ vọng thực tế cỡ **+0.2 đến +0.8pp CAGR Full**, cùng cỡ DT5G overlay
(+0.43pp) hay coverage-effect fa8l (+0.88pp). Nếu kết quả ra +3–5pp → nghi ngờ bug/leak TRƯỚC KHI mừng.

## 6. Timeline đề xuất

| Bước | Việc | Ước lượng |
|---|---|---|
| 0 | User duyệt plan này (family 3 rule, N=5, gate CP-DVR1) | — |
| 1 | Module tilt + wire pt_v23 + self-check 0 VND + spot-check 20 entry DVR (rating/route as-of đúng PIT, no look-ahead) | 0.5 ngày |
| 2 | 4 run: baseline verify + R1/R2/R3 @50B; per-year extract | 0.5–1 ngày (compute-bound) |
| 3 | Sensitivity + LOO cho winner, DSR; viết kết quả vào plan doc + registry | 0.5 ngày |
| 4 | quant-skeptic verify → trình user | — |

Tổng ~2–3 ngày làm việc. Không có deadline nghiệp vụ cứng riêng (khác fa_ratings staleness).

## 7. Đáng mở dự án riêng hay gộp maintenance? (trả lời thẳng điểm 4 dispatch)

**Khuyến nghị: chạy như 1 trial gọn maintenance-scale (1 checkpoint, N=5, 2–3 ngày), KHÔNG mở
chương trình nhiều-phase.** Lý do hai chiều:
- Đủ đáng làm: route effect medium (V=0.259) + contrast 20pp win-rate + DVR là kênh episode lớn nhất
  BAL + per-year direction giữ 2017–2025 → không phải noise p-value thuần túy; cài đặt rẻ (tái dùng
  cơ chế validated sẵn).
- Không đáng phóng đại: rating δ small; kênh DVR đang cold (2025 win 26%, 2026 17% — rule chỉ cải
  thiện RELATIVE trong kênh, không cứu kênh); kỳ vọng NAV impact <1pp. Nếu CP-DVR1 NO-GO thì dừng
  hẳn, không "thử thêm ngưỡng khác".

## 8. Rủi ro / caveat khai báo trước

1. **Data-snooping cấu trúc**: insight sinh ra từ chính dữ liệu sẽ backtest (DVR cohort Phase 1).
   Giảm nhẹ: (i) không tune ngưỡng nào — rating≥4 và size 5% lấy từ prior art độc lập đã validated,
   route là category; (ii) gate quyết định trên metric KHÁC (NAV CAGR/Calmar/DD walk-forward, không
   phải win-rate đã nhìn); (iii) LOO ex-2021/ex-2020 cứng; (iv) DSR với N khai báo. Vẫn phải nói
   thật: đây là in-sample-informed hypothesis — kể cả GO, confidence thấp hơn 1 hypothesis tiên nghiệm.
2. **2021 dominance**: 48% mẫu labeled DVR là 2021 (443/912 episode). LOO ex-2021 + ex-2020 là gate
   cứng, không phải tùy chọn.
3. **Kênh cold 2025–26**: win-rate IN-gate 2025 chỉ 39.5%, 2026 11% (n=9) — nếu chế độ thị trường
   hiện tại kéo dài, rule đúng vẫn không tạo lợi nhuận tuyệt đối từ DVR. Kỳ vọng đúng: bớt lỗ/bớt
   kẹt capital ở nhóm xấu.
4. **fa_ratings_8l cron chưa xác nhận ghi được** (thứ Bảy 07-18 mới rõ) — backtest không bị chặn,
   nhưng wiring live phụ thuộc bảng này refresh đúng. Nếu cron fail kéo dài → rule live sẽ chạy trên
   rating đóng băng (đúng vấn đề staleness đã biết của họ fa_ratings).
5. **Route n nhỏ**: INSURANCE 15, POWER 3 — gộp POWER vào nhóm xấu là judgment call khai báo trước
   (0/3 + cùng logic non-recovery), không phải kết quả thống kê. Nếu skeptic muốn, variant R1 có thể
   đọc kết quả cả 2 cách gộp/không gộp từ CÙNG run (không tốn N thêm vì không đổi lựa chọn config).
6. **Chồng với regime_size_overlay khi state rơi**: entry-tilt là weight cố định của deal; nếu vị
   thế còn giữ khi state rơi ≤2, _W-halving nhân thêm → tối đa 2.5%×0.5=1.25% (R3, tên vừa
   COMPOUNDER vừa rating≥4 trong CRISIS). Chấp nhận theo thiết kế (cả 2 lớp đều là phòng thủ, cùng
   chiều); ghi nhận để không ngạc nhiên khi audit weight.
7. **Quyết định đóng/thu hẹp MOM đang chờ user** (khuyến nghị CP1): nếu user đóng MOM, BAL phụ
   thuộc DVR nặng hơn → dự án này càng liên quan, NHƯNG baseline sẽ đổi — nếu quyết định đó đến
   trước bước 2, phải re-pin baseline trước rồi mới chạy family (tránh so với baseline lỗi thời).

## 9. User cần quyết

1. Duyệt hướng **sizing-tilt** (không hard-gate) — §3.
2. Duyệt family 3 rule + ngưỡng pre-registered (rating≥4, route {COMPOUNDER,POWER}, size 10/5/2.5%) — §4.
3. Duyệt sổ N=5 đóng + gate CP-DVR1 (§5), chấp nhận trước NO-GO = đóng nhánh (b).
4. Xác nhận scale: trial gọn maintenance (không mở chương trình nhiều phase) — §7.
