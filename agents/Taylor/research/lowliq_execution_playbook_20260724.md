# Chiến lược thực thi cho nhóm cổ phiếu thanh khoản RẤT THẤP (ADV < 1 tỷ VND/ngày)
**Job:** Taylor_20260724_022702 · **Ngày:** 2026-07-24 · **Case sống:** TV1 (PECC1, UPCOM)
**Loại:** RESEARCH — để Mike/user quyết định áp cho tranche 2 (07-27) trở đi. KHÔNG tự sửa code/plan.

---

## 0. TL;DR
- Thiết kế hiện tại của DollarBill (LO no-chase ≤19.900 + 2 tranche cố định 07-24/07-27) **đúng về
  giá (no-chase) nhưng sai về NHỊP** — lịch 2-phiên cố định là tuỳ tiện, mâu thuẫn với chính luận
  điểm giữ 2-3 năm.
- **Dữ liệu thực xác nhận giả thuyết của user**: TV1 **KHÔNG có ngày nào KL=0** trong 59 phiên gần
  nhất (min 3.500 cp — luôn có giao dịch mỗi phiên); volume thấp đi cùng giá giảm (CORR +0,35) ⇒ ngày
  KL thấp = **ít người CHỊU bán ở giá thấp**, KHÔNG phải thị trường đóng băng. Người bán có thật, chỉ
  không xuất hiện đúng lúc mình dò. ⇒ TWAP-theo-%KL-thực-tế-trong-ngày là công cụ SAI cho nhóm này.
- **Đề xuất**: thay lịch tranche cố định bằng **"chương trình gom bằng lệnh chờ kiên nhẫn"
  (patient resting-bid accumulation)** — đặt LO chờ ở/dưới bid mỗi phiên, trải qua NHIỀU tuần, tăng
  participation cơ hội khi thấy bán thật, hết hạn theo CATALYST (không theo lịch), chấp nhận under-fill.
- **Nên** tổng quát hoá thành playbook tái sử dụng cho DGC / sleeve "mua khi sợ hãi" — phác thảo tham
  số ở §4.

---

## 1. Đánh giá thiết kế hiện tại (LO no-chase ≤19.900 + 2 tranche 200cp)

**Điểm MẠNH (giữ nguyên):**
1. **No-chase ceiling 20.000 là đúng bản chất.** Order-book TV1 rất mỏng, nhiều bước giá (best offer
   19,9k×920 rồi 20,0k×880). Với thanh khoản này, market/aggressive-limit sẽ ăn xuyên nhiều bước →
   trả giá tệ. LO ≤ bid là kỷ luật đúng.
2. **Size cực nhỏ so với thanh khoản ⇒ market impact ≈ 0.** Cả vị thế 400 cp × 19.900 = 7,96 tr VND =
   **1,14% của MỘT ngày turnover median gần đây (~701 tr VND)**; mỗi tranche 200 cp = 0,57%. Impact
   KHÔNG phải ràng buộc ở size này — đây là điểm mấu chốt: cái giới hạn thực không phải "% ADV" mà là
   **có bao nhiêu người chịu bán ở giá mình đặt**.
3. Kế toán sạch: cash-only, book=DISCRETIONARY_SPECIAL, tách allocator, tên file non-canonical (đúng
   coding_guidelines §8), không stop-loss theo giá (đúng cho thesis asset-backed).

**Điểm YẾU:**
1. **Lịch 2-phiên cố định (07-24, 07-27) là tuỳ tiện.** Không có cơ sở nào để tin đúng 2 ngày đó có
   người bán ≤19.900. Nếu cả 2 ngày đều mỏng/không ai bán thấp → under-fill; nếu ép cho đủ → cám dỗ
   chase. Bản thân plan đã tự mâu thuẫn: thesis nói "gom 2-3 năm, kiên nhẫn" nhưng execution nén vào
   2 ngày.
2. **Trần cứng 400cp/2 phiên** biến một chương trình tích luỹ dài hạn thành một cửa sổ thực thi 2 ngày.
3. **Không có cơ chế tăng participation cơ hội** khi bỗng xuất hiện một phiên có bán thật (block ra).
   Với tên thanh khoản thấp, ngày có người bán mạnh là **hiếm và không dự báo được** — đó chính là lúc
   nên gom NHIỀU hơn, nhưng lịch cố định không cho.
4. **`directive_arithmetic_flag` trong plan đã tự phát hiện lệch số** (chỉ đạo "~375-500cp/phiên"
   ≈ cả vị thế, không phải per-session) — dấu hiệu bản thân khung "chia phiên cố định" không khớp
   quy mô thực.

**Kết luận §1:** thiết kế hiện tại đủ AN TOÀN để chạy tranche 1 (200cp @ ≤19.900, đúng no-chase),
nhưng **khung lịch nên thay** từ tranche 2 trở đi.

---

## 2. Dữ liệu thực TV1 — kiểm tra giả thuyết của user

Nguồn: `tav2_bq.ticker` TV1, 2026-03-02 → 2026-07-22 (98 phiên; recent-20 = 24/06→22/07).

| Cửa sổ | n | median KL (cp) | mean turnover | median turnover | ngày KL<20k | ngày TV<400tr |
|---|---|---|---|---|---|---|
| Tháng 3 (older) | 39 | 132.400 | 5,38 tỷ | 4,49 tỷ | 0 | 0 |
| cuối 4→6 (prev40) | 40 | 70.900 | 2,08 tỷ | 1,69 tỷ | 0 | 0 |
| **recent-20** | 22 | **30.900** | **713 tr** | **701 tr** | **4** | **4** |

**Suy giảm thanh khoản có cấu trúc**, đi cùng giá rơi 33k(T3)→20k(T7): turnover median co từ 4,5 tỷ →
0,7 tỷ. ADV median 39-phiên trong plan (762 tr) là **trung bình động đang GIẢM** — thực tế recent-20
chỉ ~700 tr và còn xu hướng thấp hơn.

**Kiểm tra trực tiếp giả thuyết user ("ngày KL thấp = ít người bán giá thấp, không phải đóng băng"):**
- **0 ngày KL=0 trong 59 phiên gần nhất; min = 3.500 cp (35 lô).** → thị trường **KHÔNG bao giờ đóng
  băng**; mỗi phiên đều có giao dịch. ✅ Giả thuyết đúng vế 1.
- **CORR(Volume, giá) = +0,35** (May-Jul) + giá grind đều đi xuống → khi giá xuống thấp, KL **co lại**
  vì người nắm giữ **không chịu bán rẻ hơn** (chưa capitulation), KHÔNG phải vì hết người. ✅ Giả
  thuyết đúng vế 2: người bán có thật, chỉ không lộ diện ở giá thấp đúng lúc mình dò.
- Hệ quả then chốt: **cái mình đang chờ không phải "khối lượng thị trường" mà là "người bán chịu cắt ở
  giá mình đặt".** Dòng đó nhỏ, cục, không lịch trình. Công cụ đúng = **lệnh chờ dai dẳng nhiều phiên**
  bắt được dòng tích luỹ; công cụ SAI = TWAP %-KL-ngày (trên phiên 3.500cp thì 15% = 525cp, và nếu dòng
  hôm đó khớp ở vùng giá mình không chờ thì mình = 0).

---

## 3. Chiến lược đề xuất cho ADV < 1 tỷ VND/ngày — "Patient Resting-Bid Accumulation"

Nguyên tắc cốt lõi: **kỷ luật là GIÁ (price-band) và SỰ KIÊN NHẪN (nhiều phiên), không phải LỊCH
(calendar) hay %-KL-thực-tế-trong-ngày.**

**Cơ chế:**
1. **Lệnh chờ dai dẳng (persistent resting LO):** mỗi phiên đặt LO mua tại/dưới bid, ≤ no-chase
   ceiling, để nằm chờ trong sổ. Được khớp cơ hội khi người bán bước qua — **không đuổi giá bao giờ**.
   Re-đặt lại mỗi phiên cho tới khi đủ target HOẶC catalyst hết hiệu lực.
2. **KHÔNG có hạn mức thời gian cứng.** Thay "2 phiên" bằng **cửa sổ mềm** (kỳ vọng ~15-25 phiên ≈
   4-6 tuần cho TV1) + **hạn cứng = theo CATALYST** (2 exit-trigger phi-giá đã có trong plan). "Gom
   đến khi đủ target hoặc hết catalyst", không phải "gom xong trong X ngày".
3. **Trần participation/phiên (bảo vệ, thường KHÔNG bind ở size nhỏ):** ≤10-15% của `adv_ref`
   (recent-20 median turnover). TV1: 10%×701tr = 70tr ≈ 350cp/phiên — cao hơn nhiều so nhu cầu 200cp
   ⇒ trần này gần như không chạm; nó chỉ là bảo hiểm cho tên/size lớn hơn.
4. **Tăng participation CƠ HỘI (opportunistic, cơ học — không tuỳ nghi):** phiên nào KL thực >
   k×`adv_ref` (k≈2, "block bán ra") VÀ giá ≤ limit → cho phép per-session cap × m (m≈2-3) để hốt
   phần bán thật. Đây là điểm đảo ngược đúng logic: gom NHIỀU khi người bán XUẤT HIỆN, gom ÍT/không khi
   họ vắng — thay vì rải đều bất kể.
5. **Price-band là ràng buộc bind:** định nghĩa dải giá tích luỹ neo theo thesis. Trên ceiling → ngừng
   đặt (no-chase). Dưới sàn (giá càng rẻ) → giữ hoặc TĂNG (deep-value: rẻ hơn = tốt hơn, không phải rủi
   ro hơn — trừ khi vi phạm exit-trigger phi-giá). Với TV1: ceiling 20.000; không có sàn "cắt lỗ" vì
   downside đã che bởi tài sản hydro.
6. **Chấp nhận under-fill.** Under-fill ở giá tốt >> full-fill do chase. Nếu hết catalyst window mà chỉ
   gom được 60% target → dừng, đó là kết quả chấp nhận được, không phải thất bại thực thi.

**So sánh với engine CAPIT/LAG hiện có** (`executor.py::_child_qty`): CAPIT dùng ADV20-floor +
realized-ceiling, non-CAPIT dùng `max_participation × day_volume` — **cả hai đều là guard TRONG-MỘT-
PHIÊN**, giả định sẽ fill trong ngày và plan tái sinh mỗi tối. Cho nhóm ADV<1tỷ, cái thiếu không phải
guard chặt hơn mà là **chiều THỜI GIAN đa-phiên**: một lệnh chờ sống qua nhiều tuần, tự re-đặt, hết hạn
theo catalyst. Đây là khác biệt kiến trúc, không phải tinh chỉnh tham số.

---

## 4. Playbook tái sử dụng — "Low-Liquidity Discretionary Accumulation" (đề xuất CÓ)

**Nên tổng quát hoá.** Sleeve "mua khi sợ hãi có tính toán" (mandate tuần, 2026-07-23) sẽ liên tục sinh
ra các tên đặc-tình-huống thanh khoản thấp (DGC bản special-situation, TV1, và các case tương lai). Một
playbook chung tránh mỗi lần lại thiết kế thủ công một lịch tranche tuỳ tiện.

**Điều kiện áp dụng (gate):**
- Book = DISCRETIONARY_SPECIAL (ngoài V2.4), đã qua due-diligence thủ công.
- ADV recent-20 median turnover < ~1-2 tỷ VND/ngày.
- Chân trời buy-and-hold ≥ 1 năm (thesis giá trị/tài sản, KHÔNG momentum/timing).
- Size mục tiêu ≤ vài % NAV VÀ ≤ ~vài ngày turnover cộng dồn (nếu vượt → cần chương trình dài hơn/
  re-đánh giá khả năng thoát).

**Tham số/ngưỡng (per-name, điền lúc khởi tạo):**
| Tham số | Ý nghĩa | Gợi ý mặc định | TV1 |
|---|---|---|---|
| `adv_ref` | recent-20 median turnover (VND) | đo từ BQ mỗi lần khởi tạo | ~701 tr |
| `target_qty` / `min_acceptable_qty` | mục tiêu & sàn chấp nhận under-fill | từ size cap NAV | 400 / 200 cp |
| `price_band` = [floor, ceiling] | dải tích luỹ neo thesis | ceiling = no-chase; floor = "rẻ hơn thì tốt" | [—, 20.000] |
| `resting_limit` | giá đặt LO chờ | tại/dưới bid, ≤ ceiling | 19.900 |
| `per_session_cap_pct_adv` | trần participation/phiên | 10-15% × adv_ref | 10% (≈350cp, non-bind) |
| `opportunistic_k` | ngưỡng "phiên có bán thật" | KL_ngày > k × adv_ref, k≈2 | 2 |
| `opportunistic_m` | hệ số nhân cap khi trigger | 2-3× | 2 |
| `soft_window_sessions` | kỳ vọng gom xong (mềm) | ~15-25 phiên | ~20 |
| `hard_expiry` | hạn CỨNG | = exit-trigger phi-giá (catalyst), KHÔNG phải ngày | 2 trigger đã có |
| `no_chase` | tuyệt đối không đặt > ceiling | luôn true | true |
| `accept_underfill` | dừng ở min_acceptable khi hết window | luôn true | true |

**Doctrine (bất biến, không tuỳ nghi):**
1. Giá & kiên nhẫn là kỷ luật; lịch & %-KL-ngày KHÔNG phải.
2. Gom NHIỀU khi người bán xuất hiện (opportunistic), ÍT/không khi họ vắng.
3. Under-fill giá tốt > full-fill do chase.
4. Hết hạn theo catalyst, không theo calendar.
5. Đây là **tối thiểu-hoá chi phí thực thi**, KHÔNG phải alpha claim — không có edge backtest-able để
   quant-skeptic gate; kiểm định là kỷ luật thực thi + audit fill giá vs no-chase ceiling sau khi xong.

**Triển khai (nếu user duyệt — CHƯA làm):** cần cơ chế re-chèn lệnh chờ TV1 vào
`plan_SpaceX_<date>.json` (book=DISCRETIONARY_SPECIAL) MỖI phiên tự động cho tới khi đủ target/hết
catalyst, thay vì 2 mục tranche cố định — hiện đang thủ công. Đây là thay đổi execution-handoff, cần
Mike/user quyết + có thể cần DollarBill/Mafee phối hợp. **KHÔNG tự wire trong job này.**

---

## 5. Khuyến nghị cho tranche 2 (07-27) trở đi
1. **Giữ tranche 1 (07-24) như plan** — 200cp LO ≤19.900, đúng no-chase. An toàn.
2. **Từ tranche 2: đổi từ "lịch 2-phiên cố định" sang "lệnh chờ dai dẳng"** — đặt LO ≤19.900 (hoặc =
   bid nếu bid < 19.900) mỗi phiên T2-T6, để nằm chờ, cho tới khi đủ 400cp cộng dồn HOẶC chạm 1 trong 2
   exit-trigger phi-giá. Không ép vào đúng ngày 07-27.
3. **Thêm rule opportunistic**: phiên nào KL > ~1,4 tr VND turnover (≈2×adv_ref) và giá ≤19.900 → cho
   phép gom tới hết phần còn thiếu trong phiên đó (vẫn ≤400 tổng, vẫn no-chase).
4. **CẦN USER/MIKE QUYẾT** có tổng quát hoá thành playbook §4 + wire cơ chế re-chèn tự động hay không.

---

## 6. TRIỂN KHAI (job Taylor_20260724_024201 — user duyệt 2 việc ở §5)

Đã code THẬT (không chỉ đề xuất) + selfcheck 33/33 PASS. **CHƯA kích hoạt cron live** — chờ
quant-skeptic verify + user duyệt trước tranche 2 (thứ Hai 07-27), theo đúng chỉ đạo dispatch.

### Files
| File | Vai trò |
|---|---|
| `trading_bot/discretionary_accumulation.py` | Engine THUẦN (no I/O): `compute_session_order(state, filled_qty, prev_turnover_vnd, prev_price_vnd, plan_date, now_iso)` → (order|None, decision). `validate_state()` bảo vệ bất biến no-chase. |
| `mike/bin/discretionary_accumulation_inject.py` | Driver I/O: đọc broker positions LIVE (filled thật) + DNSE quote LIVE (giá/KL phiên gần nhất, KHÔNG BQ §6) → chèn order `book=DISCRETIONARY_SPECIAL` vào `plan_<acct>_<date>.json` (atomic tmp+os.replace) + cập nhật ledger. Idempotent + fail-safe. |
| `mike/bin/inject_discretionary_orders.sh` | Wrapper cron: lặp `live_dnse_labels()`, gọi injector từng account. |
| `data/trade_plans/discretionary/state_TV1_SpaceX.json` | State TV1: target 400 / min 200 / resting_limit 19.900 / ceiling 20.000 / cap 10%ADV / opp k=2,m=2 / soft 20 phiên / hard_expiry = 2 catalyst phi-giá (MANUAL). |
| `discretionary_accumulation_selfcheck.py` | 33 test (engine + injector). |

### Schema state per-position (formalize — task item 1)
`target_qty · min_acceptable_qty · baseline_qty_before_program · lot_size · price_band{resting_limit,
no_chase_ceiling, floor} · adv_ref_vnd · per_session_cap_pct_adv · opportunistic{k,m} ·
soft_window_sessions/start_date · hard_expiry{manual_only, halted, halted_reason, conditions[]} ·
no_chase · accept_underfill · ledger[] · status(active|completed|halted)`.

### Idempotency (3 lớp)
1. dedup order-id `BUY-<T>-DISC-<plan_date>` đã có trong plan → skip.
2. dedup ticker+book=DISCRETIONARY_SPECIAL đã có trong plan → skip (bắt cả tranche chèn tay).
3. dedup ledger đã có bản ghi `plan_date` → skip.
`filled_qty` LUÔN tính lại từ **broker positions** (chân lý), KHÔNG cộng dồn ledger → chạy lại
không đếm 2 lần (selfcheck b′ chứng minh: mất ledger vẫn ra remaining đúng từ broker).

### Wiring (task item 4) — điểm chèn
DollarBill dispatch trong `bq_freshness_check.sh` là **`--bg` (async)** ⇒ plan file được ghi SAU
đó vài phút bởi headless session khác. KHÔNG thể chèn ngay trong vòng lặp dispatch (plan chưa tồn
tại). ⇒ chọn **1 bước cron RIÊNG lúc 20:30 ICT** (sau DollarBill ghi plan ~19:0x, trước
send_plan_report 21:00) để user duyệt plan đã có sẵn lệnh gom. Plan vẫn `requires_user_approval`
⇒ Mafee chỉ execute sau khi user duyệt (human gate GIỮ NGUYÊN).

**Crontab line để KÍCH HOẠT (sau verify + user duyệt):**
```
30 13 * * 1-5 /home/trido/thanhdt/WorkingClaude/mike/bin/inject_discretionary_orders.sh >> /home/trido/thanhdt/WorkingClaude/mike/logs/inject_discretionary.log 2>&1   # 20:30 ICT - auto-chen lenh gom DISCRETIONARY_SPECIAL
```
(20:30 ICT = 13:30 UTC. Đã đăng ký `mike/kb/cron_registry.md`, đánh dấu CHƯA CÀI.)

### Còn cần NGƯỜI (task item 6)
- **hard_expiry (catalyst kiểm toán FY2026 / đình chỉ giao dịch): KHÔNG tự động hoá được.** Cả 2 là
  tin pháp lý/kiểm toán tương lai, không có feed đọc-máy đáng tin. Cơ chế: NGƯỜI (Winston theo dõi
  corp-action/tin → escalate) set `hard_expiry.halted=true` + `halted_reason` trong state file; engine
  tự dừng gom ngay phiên kế (selfcheck xác nhận). Đây là điểm human-in-the-loop CÒN LẠI của cơ chế.
- **Kích hoạt cron**: cần user duyệt (chạm lệnh thật) + quant-skeptic PASS.
- Mọi bước KHÁC (tính qty/giá, chèn plan, dừng khi đủ target, fail-safe) đã tự động + auditable.
