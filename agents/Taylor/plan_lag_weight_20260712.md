# PLAN — Tăng tỷ trọng allocator w_LAG (PEAD) sau khi đóng kênh MOM_N/MOM_S
> Taylor, 2026-07-12 · job Taylor_20260712_070206 · trạng thái: **SCOPE XONG — CHỜ USER DUYỆT, CHƯA CHẠY BACKTEST NÀO**
> Trial MỚI, sổ N riêng. Cấu trúc theo mẫu `plan_dvr_8l_sizing_20260712.md`.

## 0. Tóm tắt cho user (đọc 1 phút)

Câu hỏi user: *"momentum yếu (vừa đóng MOM_N/MOM_S) → có nên nghiêng thêm allocator về LAG vì edge
LAG bền hơn không?"* Sau khi kiểm tra số liệu có sẵn (KHÔNG chạy backtest mới), câu trả lời scope
gồm 3 phần:

1. **Tiền đề "LAG bền hơn" ĐÚNG MỘT NỬA**: edge trade-level của LAG dương ở 11/15 năm (KHÔNG dồn
   2020-21 như MOM) — bền hơn thật về BỀ RỘNG năm. Nhưng nó **có chu kỳ trough rõ**: 2019 ≈ 0,
   2022 ≈ 0, và **2026 hiện ÂM** (mean −0.9%/trade, win 29% — trough sâu nhất mẫu).
2. **Hệ thống ĐÃ CÓ cơ chế adaptive cho đúng việc này**: allocator production là **edge-conditional**
   (w_LAG=0.65 trong state 3/4/5 CHỈ khi edge-health trailing-12M của chính LAG ≥ 4%; nếu không giữ
   0.50). Ngay lúc này gate đang FAIL (2026: 0% số ngày đạt) → config đã-validate nói **0.50, không
   phải 0.65**. Tăng ceiling tĩnh bây giờ là đi NGƯỢC tín hiệu của cơ chế đã có.
3. **Phát hiện phụ QUAN TRỌNG (nên xử lý bất kể quyết định nghiên cứu)**: live recommender
   `golive_recommend_v23.py` **KHÔNG implement edge-conditional gate** — nó in target 65% vô điều
   kiện ở state 3/4/5, trong khi spec pinned của R3 (`v23a … edge`) yêu cầu hiện tại phải là 50%.
   Spec-drift harness-vs-live, chi tiết §4.

**Khuyến nghị của tôi (user quyết)**: ưu tiên **fix spec-drift (§4) trước** — 0 tốn N, chỉ align
live với spec đã validate; còn family tăng-ceiling (§6) đáng chạy NHƯNG kỳ vọng biên nhỏ (+0.0–0.5pp,
prior lệch về null) vì ràng buộc capacity §5. Nếu user muốn đo, plan dưới đây pre-registered đầy đủ.

## 1. Bối cảnh & câu hỏi

- Production V2.4/R3 vừa re-pin sau đóng MOM_N/MOM_S (commit 4fbd492+9df396d): **CAGR 27.84% /
  Sharpe 1.84 / MaxDD −18.2% / Calmar 1.53** @50B; IS 23.15 / OOS 32.30 / OOS Calmar 1.77;
  cửa sổ OOS ex-2021 21.92 / 2022+ 21.30 / 2024+ 30.87 (nguồn: registry section RE-PIN 2026-07-12).
- Allocator hiện hành: `STATE_LAG_WEIGHT = {CRISIS 0.50 / BEAR 0.00 / NEUTRAL·BULL·EXBULL 0.65}`,
  band ±10pp, **edge-conditional** (`pt_v23_audit_2014.py:169-174, 1738-1751`): tilt 0.65 ở state
  3/4/5 CHỈ khi `mean12` (trailing-12M mean post-return các trade LAG, causal, từ
  `data/lag_edge_health.csv`) ≥ `EDGE_THR=4.0%`; else 0.50. BEAR=0 vì PEAD lỗ trong gấu hệ thống
  (−14%/yr, xem `crisis_playbook.md:132`).
- Lý do câu hỏi nảy sinh: MOM_N/MOM_S đóng vì thành công lịch sử = dồn mẫu 2020-21. User hỏi tự
  nhiên: vậy có nghiêng thêm về LAG không?
- **Ràng buộc tiền lệ phải khai báo**: `deploy_golive_dt5g_v4/README.md:83` ghi rõ về allocator:
  *"`{1:.50, 2:0, 3:.65, 4:.65, 5:.65}` — do NOT retune to history"*. Dự án này chính là retune —
  nếu user duyệt đo, tức là chấp nhận lật chỉ dẫn đứng đó một cách CÓ Ý THỨC, và vì thế gate phải
  chặt (LOO/DSR cứng, §7), không nới.

## 2. Kiểm tra tiền đề "edge LAG bền hơn" — số liệu CÓ SẴN (descriptive, không phải trial)

Nguồn: `data/lag_edge_health.csv` (5.387 trade LAG 2012→2026, cột `ret` = post-return/trade, file
causal đã dùng cho chính edge-conditional allocator). Per-year:

| Năm | n | mean ret/trade | win% | | Năm | n | mean | win% |
|---|---|---|---|---|---|---|---|---|
| 2012 | 9 | −3.8% | 44% | | 2020 | 307 | +6.1% | 54% |
| 2013 | 61 | +4.7% | 61% | | **2021** | **581** | **+12.5%** | **71%** |
| 2014 | 194 | +8.4% | 63% | | 2022 | 650 | +0.0% | 44% |
| 2015 | 381 | +2.8% | 52% | | 2023 | 408 | +5.2% | 58% |
| 2016 | 371 | +3.5% | 54% | | 2024 | 563 | +4.9% | 63% |
| 2017 | 310 | +4.0% | 54% | | 2025 | 643 | +3.9% | 55% |
| 2018 | 320 | +2.3% | 53% | | **2026** | **285** | **−0.9%** | **29%** |
| 2019 | 304 | +0.8% | 42% | | FULL | 5.387 | +4.2% | 54% |

**Đọc trung thực:**
- **Ủng hộ user**: edge dương 11/15 năm, trải rộng 2013-18 + 2020-25 — KHÁC hẳn chữ ký MOM_N/MOM_S
  (dồn 2020-21). "LAG bền hơn MOM" = ĐÚNG về bề rộng.
- **Chống lại việc tăng ceiling NGAY**: (a) 2021 vẫn là năm lớn nhất (mean 12.5%, n=581 — LOO
  ex-2021 bắt buộc); (b) edge có trough chu kỳ (2019/2022 ≈ 0) và **2026 là trough sâu nhất mẫu**
  (âm cả mean lẫn win-rate); (c) % ngày pass gate edge-health ≥4%: 2026 = **0%** → cơ chế
  adaptive hiện hành đang chủ động GIỮ 0.50. Realized `w_lag_tgt` mean cả mẫu ≈ 0.50 (từ CSV
  pinned R3) — tức ceiling 0.65 vốn chỉ có hiệu lực ~nửa thời gian.

## 3. Hiệu lực live hiện tại = 0 (quan trọng cho kỳ vọng của user)

BAL/LAG book đang RỖNG (NEUTRAL parking từ ~04/2026). Bất kể kết quả nghiên cứu, đổi w_LAG **không
ép thoát/vào vị thế nào ngay**; hiệu lực chỉ bắt đầu khi LAG refill (dự kiến ~cuối 07 theo job
Taylor_20260704_033932). Và vì gate edge-health đang fail, một ceiling cao hơn (nếu GO + wire) sẽ
**dormant cho tới khi edge LAG hồi ≥4%** — đây là tính năng, không phải nhược điểm: không ai muốn
tăng tỷ trọng vào một book đang win 29%.

## 4. PHÁT HIỆN PHỤ — spec-drift live vs harness (đề xuất xử lý TRƯỚC, không tốn N)

`deploy_golive_dt5g_v4/golive_recommend_v23.py:53,206` (money-path SpaceX/ZaloPay) dùng
`STATE_LAG_WEIGHT` **thô, không có edge-conditional gate** → đang in "target w_LAG 65%" mọi ngày
NEUTRAL (thấy trong `out/golive_v23_recommendations_2026-07-*.md`), trong khi baseline R3 pinned
chạy `v23a none postbull 0 edge` — spec production yêu cầu target hiện tại = **50%** (edge-health
2026 < 4%). Hệ quả nếu không sửa: khi LAG refill cuối 07, DollarBill sẽ lập plan theo tilt 65%
KHÔNG được backtest bảo chứng cho trạng thái edge hiện tại.

**Đề xuất (việc riêng, tách khỏi family §6):** port hàm `w_lag_target(state)` edge-conditional
(đọc `lag_edge_health.csv`, thr 4%, fallback 0.50) sang `golive_recommend_v23.py` cho khớp spec
pinned. Đây là **bug-fix align theo spec đã validate, không phải thay đổi chiến lược** — nhưng vì
chạm money-path nên vẫn cần user duyệt + quant-skeptic verify code change (đúng quy trình Scope A
vừa làm). Rollback 1 hàm. Cần thêm 1 việc con: xác nhận `lag_edge_health.csv` có writer refresh
định kỳ hay là file đông cứng (nếu đông cứng → phải wire refresh trước khi live tin nó; sẽ nhờ
Winston xác minh — đúng guidelines §9).

## 5. Ràng buộc CAPACITY (điểm 3 dispatch) — vì sao kỳ vọng biên NHỎ

Đo descriptive từ CSV pinned R3 hiện hành (artifact đông cứng, không phải run mới):

- **LAG book chỉ deploy trung bình ~42% vốn vào cổ phiếu PEAD** (`lag_stocks_ref/lag_total` mean
  0.424, ổn định 40-48% mọi năm); chỉ **31% số ngày** book >90% deployed. Phần còn lại là
  cash/ETF-parking nội bộ book.
- Cơ chế: LAG có **12 slot** × tier-weight 8-9%/slot (`pt_v23_audit_2014.py:1684-1692`, hold ~25
  phiên) — ràng buộc binding phần lớn thời gian là **SỐ DEAL PEAD hợp lệ**, không phải vốn được
  cấp. Tăng w_LAG khi slot không đầy chỉ chuyển parking từ book BAL sang parking của book LAG
  (gần như zero-sum, cùng vehicle custom30V/ETF).
- Phần có tác dụng thật: ~31% ngày full-slot, mỗi slot to hơn theo vốn book. @50B: w 0.65 → slot
  ~2.8-2.9B VND; w 0.80 → ~3.6B. Với fill-model 20%ADV/5-ngày, slot 3.6B cần ADV ≥ ~3.6B/ngày —
  universe PEAD có đuôi mid-cap sẽ bắt đầu bị **fill-shortfall / impact**. → harness phải báo cáo
  diagnostic fill-shortfall per-config (khai báo trước ở §7).
- Chiều ngược lại (chi phí): vốn rời BAL là vốn của DVR + MOMENTUM/MEGA generic — Scope A vừa đo
  xong cho thấy phần generic BULL-only **vẫn đóng góp thật** (Scope B bị bác vì cắt nó). Tăng
  w_LAG ở state 4/5 = cắt bớt đúng phần đang còn edge đó.

**Hệ quả cho kỳ vọng (điểm 5 dispatch): +0.0 đến +0.5pp CAGR Full, prior lệch về NULL** (nhỏ hơn
kỳ vọng DVR-8L +0.2-0.8 vì cơ chế ở đây gián tiếp hơn — dịch vốn giữa 2 book mà phần lớn phần dịch
là parking-for-parking). Nếu kết quả ra +2pp trở lên → **nghi bug/leak trước khi mừng** (chuẩn V2.5/
DVR-8L). Nếu mọi config ≤ +0.1pp → kết luận trung thực là "allocator hiện tại đã đủ, đóng nhánh".

## 6. Family pre-registered (nếu user duyệt đo) — sổ N-ledger "LAG-WEIGHT": **N = 5, đóng tại đây**

Câu hỏi nghiên cứu chính xác: *"Nâng CEILING w_LAG trong good states (3/4/5) từ 0.65 lên X — giữ
nguyên edge-conditional gate (thr 4%, fallback 0.50), giữ nguyên CRISIS 0.50 / BEAR 0.00, giữ
band ±10pp — có cải thiện OOS robust không?"*

Khai báo TRƯỚC những gì KHÔNG đo (giữ N nhỏ, mỗi cái nếu muốn là trial mới xin duyệt riêng):
- KHÔNG đổi CRISIS/BEAR (BEAR=0 có cơ sở riêng: PEAD −14%/yr trong gấu; CRISIS 0.50 là tail-risk
  territory, đổi nó là quyết định risk khác hẳn).
- KHÔNG tune EDGE_THR (4%), band (±10pp), fallback (0.50), số slot (12), tier-weight LAG.
- KHÔNG có variant bỏ-gate chạy độc lập trong ladder (chỉ 1 ablation cho winner, xem trial 4).

| # | Trial | Config | Giả thuyết |
|---|---|---|---|
| 1 | **W70** | good-state ceiling 0.65→**0.70** | liều tối thiểu, sát production |
| 2 | **W75** | ceiling **0.75** | mức "tăng đáng kể" tự nhiên |
| 3 | **W80** | ceiling **0.80** | cận trên hợp lý — quá mức này slot-size @50B vượt ADV đuôi PEAD (§5) |
| 4 | **Ablation gate** cho WINNER duy nhất | winner chạy flat (edge-conditional OFF) | tách phần gain do ceiling vs do adaptive gate — nếu flat ≥ gated → gain là beta-tilt thô, đáng ngờ |
| 5 | **LOO gộp** cho winner (per-year 13 phép + ex-2021/ex-2020) | chỉ đọc, không đổi lựa chọn |

Control (baseline R3 re-pin) chạy lại để verify tái lập pin — control không tính N (chuẩn cũ).
Ceiling ladder là 3 điểm cách đều → winner tự có neighbor làm sensitivity, không cần trial riêng.
KHÔNG mở thêm test sau khi chạy; muốn thêm → dừng, xin user duyệt N mới.

**Harness**: `pt_v23_audit_2014.py` @50B, đúng lệnh pin + **`BQ_LOCAL_CACHE=1 BQ_CACHE_THREADS=1`**
(bài học re-pin 07-12 — cache pin là PHẦN CỦA lệnh), knob mới qua env (vd `LAG_W_GOOD=0.70`, unset
= byte-identical baseline — pattern `BAL_DROP_TIERS` đã dùng), output tag **`_exp_lagw*`** (không
thể đè canonical, guidelines §8). Self-check 0 VND bắt buộc mỗi run. Diff dự kiến ~5-10 dòng
(1 env đọc vào `STATE_LAG_WEIGHT`/`w_lag_target`).

## 7. Gate GO/NO-GO (CP-LAGW1, checkpoint duy nhất)

Winner phải đạt TẤT CẢ (so control cùng cache-vintage, không so số pin cũ nếu data trôi):

| Gate | Tiêu chí |
|---|---|
| OOS 2020+ | CAGR **và** Calmar ≥ control (≈32.30 / 1.77) |
| IS 2014-19 | Không tệ hơn control quá 0.3pp CAGR (≈23.15) |
| Per-year LOO | Delta vs control KHÔNG âm mọi năm bỏ-ra, **đặc biệt ex-2021** (năm LAG lớn nhất, §2) và ex-2020 |
| Tail | MaxDD không xấu hơn control (≈−18.2%) |
| Capacity diagnostic | Fill-shortfall/impact LAG không tăng vật chất (báo số cụ thể; tăng >20% số entry bị scale → FAIL) |
| Ablation gate (trial 4) | Winner-gated ≥ winner-flat trên OOS — gain phải ĐI QUA cơ chế adaptive; nếu flat thắng → NO-GO (beta-tilt thô, ngược thiết kế đã validate) |
| DSR | ≥ 0.95 trên NAV daily winner, N=5 khai báo (footnote trung thực: ceiling 0.65 gốc có lịch sử tuning riêng trước 2026-06-13 — deflation N=5 là cận DƯỚI, vì vậy LOO mang trọng số quyết định) |
| PBO | Family 5 < 8 → không bắt buộc; LOO thay thế |
| quant-skeptic | CONFIRMED bắt buộc trước khi trình user |

NO-GO = đóng nhánh, ghi registry, không wire, không thử thêm ceiling khác. GO ≠ wire: GO chỉ =
trình user sign-off; wire live cần duyệt riêng (đổi `STATE_LAG_WEIGHT` ở 4 file production, cùng
pattern Scope A) + re-pin baseline.

## 8. Rủi ro / caveat khai báo trước

1. **Lật chỉ dẫn đứng "do NOT retune to history"** (§1) — phải là quyết định có ý thức của user,
   không phải mặc định. Đây là lý do prior của tôi lệch về null và gate không nới.
2. **2021 dominance**: năm LAG mạnh nhất (mean 12.5%, n=581). Mọi gain dồn 2021 = chữ ký R2/F12
   → LOO ex-2021 là án tử, đã cài làm gate cứng.
3. **Regime hiện tại ngược đề xuất**: LAG 2026 âm (win 29%). Tăng ceiling là bet vào chu kỳ edge
   NEXT, không phải hiện tại — wire xong cũng dormant tới khi edge-health hồi (§3). User cần hiểu
   trước: dự án này KHÔNG đổi hành vi live ngắn hạn.
4. **Đường phụ thuộc lịch sử của 0.65**: giá trị gốc được chọn từ nghiên cứu allocator trước
   2026-06-13 mà registry không còn ghi chi tiết sweep — số trial lịch sử thực không truy được đầy
   đủ → DSR N=5 là under-count có khai báo (footnote gate DSR).
5. **Path-divergence noise**: đổi w_LAG đổi path cả 2 book từ 2014 (bài học V2.5: diff 2 full-run
   nhiễm butterfly noise ±5-12pp/năm). Giảm nhẹ: đọc kết quả ở mức cửa sổ + LOO như Scope A đã làm,
   không đọc 1 số FULL đơn lẻ; nếu tín hiệu mảnh, cân nhắc episode-windowed read (không thêm N).
6. **R1/R2 bull-park chưa re-run sau 2 lần re-pin** — mọi so sánh trong dự án này chỉ trên R3
   NEUTRAL-only config (đúng config live <150B), không suy ra cho bull-park.
7. **`lag_edge_health.csv` freshness chưa xác minh** (§4) — nếu file không có writer định kỳ, cả
   edge-conditional live lẫn nghiên cứu này đứng trên input tĩnh. Việc con cho Winston trước khi
   wire bất cứ gì.

## 9. User cần quyết (3 câu riêng biệt)

1. **Fix spec-drift `golive_recommend_v23.py`** (§4 — port edge-conditional gate cho khớp spec
   pinned; bug-fix, không phải chiến lược mới): duyệt làm ngay? **Khuyến nghị: CÓ**, bất kể câu 2.
2. **Chạy family LAG-WEIGHT** (§6, N=5, gate §7): duyệt đo, hay chấp nhận kết luận descriptive
   (§2+§5: edge LAG bền về bề rộng nhưng đang trough + capacity hạn chế + cơ chế adaptive đã có →
   giữ nguyên allocator) và đóng câu hỏi không tốn compute? **Khuyến nghị: câu trả lời descriptive
   đã khá đủ; chỉ đo nếu user vẫn muốn con số cứng** — kỳ vọng khai báo +0.0-0.5pp, prior null.
3. Nếu duyệt câu 2: xác nhận scale **maintenance trial gọn** (1 checkpoint, ~2-3 ngày, không mở
   chương trình nhiều phase), và chấp nhận trước NO-GO = đóng nhánh.
