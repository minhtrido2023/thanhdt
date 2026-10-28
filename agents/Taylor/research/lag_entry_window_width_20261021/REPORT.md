# Cửa sổ vào lệnh book LAG — độ rộng có phải vấn đề không?

**Job** `Taylor_20261021_102832` · 2026-10-21 · Taylor · READ-ONLY (không sửa production, không pin)
PREREG: `PREREG.md` md5 `728a2104a1a88bd0f6dd61bcf4df182c` (ghi trước khi chạy số).

## 0. Kết luận

**Giả thuyết của Mike đứng vững.** Lỗ hổng nằm ở khâu vận hành phiên chuẩn, không nằm ở độ rộng cửa sổ.

| | Kết quả | Loại |
|---|---|---|
| Live 07-01→10-21: số ca trần giá / hết cửa sổ là nguyên nhân CHÍNH | **0 / 28** slot mục tiêu | ĐO (artifact) |
| Live: vốn mục tiêu LAG không triển khai | **~90%** (1.358tr / 1.516tr, slot ước lượng) | ĐO số ca, số tiền là ƯỚC LƯỢNG |
| Trong số vốn đó, do vận hành (tiền, lịch, plan rỗng, plan bỏ sót) | **100%** nguyên nhân chính. Trần/cửa sổ chỉ là quân domino CUỐI ở 5 ca (~304tr), cả 5 đều đã mất phiên 1 vì vận hành và đều trước Luật A | ĐO |
| Backtest: W1 vs W3 (Luật A, thoát neo) | **−0,06pp** CI95 [−0,13; +0,02] | ĐO (event study) |
| Backtest: W4 hoặc W5 vs W3 | **+0,000pp** và **−0,006pp**; chỉ 0 và 1 sự kiện trong N=5.361 khác kết quả | ĐO |
| Số sự kiện LAG live đi qua cửa sổ kể từ Luật A (08-15) | **0** | ĐO |

→ **Giữ 3 phiên.** Không có cơ sở để nới hay thu hẹp: cả mẫu live (N=0 dưới luật hiện hành) lẫn backtest đều không ủng hộ. Việc cần làm là sửa vận hành ở phiên chuẩn (§5).

---

## A. Kiểm toán live (2026-07-01 → 2026-10-21, SpaceX + ZaloPay) — ĐO

**Nguồn dữ liệu.**
- Ứng viên: các dòng `book=LAG` trong `golive_v23_recommendations_*.csv`. Đây là cùng file mà `filter_lag_entry_window.py` đọc.
- Quyết định: plan JSON từng ngày, gồm `orders[]`, `deferred_orders[]` và `lag_analysis`.
- Fill thật: `dnse_raw_<d>.jsonl` `kind=orders`. Bước đầu tiên luôn là lọc `accountNo` (§12), sau đó lấy `fillQuantity` max theo `id`.
- Kiểm chéo: email khớp lệnh broker `dnse_khoplenh_broker_confirm_*.csv`. Có file cho các ngày 07-08, 10-08, 11-08. Với SCL 08-10 khớp đúng 1500/1000 ở cả 2 nguồn.
- Script: `audit_live.py` → `audit_live_rows.csv`; `classify_live.py` → `audit_live_classified.csv`. Mỗi mã nguyên nhân có kèm trích dẫn artifact trong cột `evidence`.

**Tập ứng viên.** 67 sự kiện × 2 account = 134 dòng. Tất cả có entry chuẩn trong khoảng **07-24 → 08-07** (mùa Q2).
- Không có dòng LAG nào cho 08-13 → 10-19. Đây là ngoài mùa thật: theo BQ `ticker_financial`, tỷ lệ release Q2 sau 08-07 chỉ 0,2–1,2%/năm (2022–2026).
- Mùa Q3 mới bắt đầu. 3 ứng viên (HT1/SCL/VPB) có entry khoảng 10-26, nằm ngoài khoảng kiểm toán.

| Mã nguyên nhân (ứng viên × account) | SpaceX | ZaloPay |
|---|---:|---:|
| Lọc ADV/universe ở tầng tín hiệu/DD (`SIG_FILTER_ADV_UNIV`) | 33 | 35 |
| Loại DD/rating/floor/DCF-RICH (`EXCLUDED_DD`) | 13 | 12 |
| Loại tường minh bởi user / banned | 3 | 3 |
| Đã có vị thế (VPB/VND/PVT) | 3 | 1 |
| ZaloPay loại FLOOR_FAIL trong khi SpaceX cùng ngày xếp VALID (EVF/PSI/VCI 07-28) | – | 3 |
| **Mục tiêu thật** (qua lọc của chính fleet) | **13** | **15** |
| ↳ `FILLED_D1` | 0 | 2 (VPB, CSV) |
| ↳ `FILLED_LATE` / `PARTIAL_LATE` (phiên 3) | 1 (SCL 1500/1500) | 1 (SCL 1000/1500) |
| ↳ `WAIT_CASH` (hoãn vì thiếu tiền ở phiên chuẩn) | 7 | 9 |
| ↳ `PLAN_CALENDAR_ERROR` | 4 | 0 |
| ↳ `PLAN_EMPTY_BLOCKED` (park_trim `BLOCKED_RECONCILE` 08-06) | 2 (DRI, POW) | 0 |
| ↳ `PLAN_DECIDED_NOT_ORDERED` (SSI 08-07: `decision=BUY` nhưng không có trong `orders[]`/`deferred`) | 1 | 1 |
| ↳ Trần giá / khoá trần / vendor release muộn là nguyên nhân CHÍNH | **0** | **0** |

Chi tiết các ca vận hành:
- **`PLAN_CALENDAR_ERROR`** (SpaceX AGR/BSI/FTS/HCM):
  - Engine báo "UPCOMING T+3 từ 07-22", tức entry 07-27.
  - Plan SpaceX 07-24 ghi "T+2 entry **07-25**". Ngày đó là **thứ Bảy**.
  - Dispatch tối 07-24 fail do weekly usage limit.
  - Plan SpaceX 07-27 ghi "CỬA SỔ ĐÃ ĐÓNG — 16 mã MISSED". Trong khi đó plan ZaloPay **cùng ngày** coi 07-27 là phiên chuẩn và đã mua VPB.
  - Như vậy hai account diễn giải hai lịch khác nhau cho cùng một tín hiệu.
- **Vendor release muộn = 0.** Mọi ứng viên xuất hiện lần đầu ở CSV dưới dạng `UPCOMING T+2..T+4`, tức engine thấy release trước phiên chuẩn 2–4 phiên. Không ca nào xuất hiện lần đầu dưới dạng `WINDOW_PASSED`.
- **Khoá trần biên độ = 0** trong mẫu live.
- **Ghost-order** không phải mã chính của ca nào. DRI 08-07 SpaceX là `WAIT_CASH` ×94 ("sức mua broker 0 cp"), đúng như journal ghi.

## B. Định lượng — số ca ĐO, số tiền ƯỚC LƯỢNG

Slot mục tiêu lấy từ chính plan: SpaceX `lag_hi/lo_target_vnd` 91,0tr / 72,8tr (plan 07-28); ZaloPay 27,07tr / 21,66tr (plan 08-06). Áp các con số này cho mọi ngày, nên số tiền là **ước lượng**.

| | SpaceX | ZaloPay | Tổng |
|---|---:|---:|---:|
| Giá trị mục tiêu (28 slot) | 1.201,8tr | 314,0tr | 1.515,9tr |
| Không triển khai | 1.110,8tr (92%) | 247,3tr (79%) | **1.358,0tr (90%)** |
| Triển khai trễ (phiên 3) | 91,0tr | 18,0tr | 109,1tr (7%) |

Vốn không triển khai, chia theo mã chính: `WAIT_CASH` 58% · `PLAN_CALENDAR_ERROR` 21% · `PLAN_EMPTY_BLOCKED` 13% · `PLAN_DECIDED_NOT_ORDERED` 7% · partial 1%.

**Phần do cửa sổ so với phần do vận hành.**
- Do cửa sổ (ca có lệnh hợp lệ, đủ tiền ở phiên 1 mà vẫn không khớp trong 3 phiên): **0tr**.
- Do vận hành: **100%** nguyên nhân chính.
- Trần `≤ anchor` cũ là quân domino cuối ở DRI/POW/SSI (khoảng 304tr). Chỉ xảy ra **sau khi** phiên 1 đã mất vì tiền hoặc plan, và đều trước Luật A. Dưới Luật A, ca kiểu này trong backtest là 0,1% (§C).

**Chi phí** (ƯỚC LƯỢNG: áp đường cong lịch sử vào ca live).
- Lợi nhuận kỳ vọng/slot ở baseline live W3·A·ANCH là **4,61%** CI [3,44; 5,89] cho 25 phiên nắm.
- **Cận trên** chi phí bỏ lỡ: 1.358tr × 4,61% ≈ **62,6tr** [46,7; 80,0]. Con số này giả định tiền đó lẽ ra nằm im ở 0%.
- **Cận thực tế hơn:** tổng slot vượt sức chứa book. LAG book SpaceX 455,2tr (plan 07-28 `NAV_book_LAG`), ZaloPay 238,9tr (plan 07-27 `lag_book_vnd`), tổng 694tr so với 1.516tr slot.
  - Ngay cả khi vận hành hoàn hảo, chỉ khoảng **694tr** triển khai được. Thực tế đã triển khai khoảng 158tr, tức khoảng 23% sức chứa.
  - Phần lỡ triển khai được: khoảng 536tr × 4,61% ≈ **24,7tr** [18,4; 31,6]. Đây là ƯỚC LƯỢNG và chưa trừ lợi nhuận tiền đang nằm ở CAPIT/park.
- Chi phí trễ: 109tr × 2 phiên × 0,35pp/phiên (đo 08-10) ≈ **0,8tr**. Không đáng kể.

⚠️ Một phần `WAIT_CASH` là **cấu trúc** chứ không phải lỗi: book LAG oversubscribe, tiền đang nằm ở CAPIT/park. Riêng đợt 08-06 là lỗi vận hành thật: `BLOCKED_RECONCILE` do lệch sổ VHM, và PARK sell ZaloPay bị `HTTP 400 deal not found` ×944 (nghiên cứu 08-10). Với dữ liệu hiện có tôi **không tách được hai phần này cho từng ca**. Đó là SUY LUẬN, không phải số đo.

## C. Backtest độ rộng cửa sổ — ĐO (event study, KHÔNG phải NAV)

**Thiết lập** (`window_design_bt.py`).
- Tập sự kiện sao y luật engine (`NP_R≥15 ∧ prior_n_good≥4 ∧ pa_HL3≥5`, forensic ON), entry = Release+5.
- N = **5.361 sự kiện**, 789 mã, **572 cụm ngày công bố**. Bootstrap cụm 2.000 lần, seed 20261021.
- So với nghiên cứu 08-10 (4.618 sự kiện), số sự kiện nhiều hơn vì dữ liệu dài thêm.
- Giá lấy từ `data/bq_cache` qua `simulate_holistic_nav.bq`. Vintage của cache chưa kiểm.

**Mô phỏng Luật A.**
- Trần = ref × 1,03, với ref = `Price` thô phiên trước. Đây là XẤP XỈ: đúng HOSE/HNX ngày thường; sai với UPCOM (giá tham chiếu là bình quân gia quyền) và ngày GDKHQ.
- Khoá trần: High = Low và tăng ≥ 6,5% thì không khớp.
- Khớp toàn phần hoặc không khớp. Không mô hình volume.

**Lệch PREREG (khai thật).**
- Mô hình giá khớp theo PREREG ("min(Close, trần)") cho Luật A giá **thấp hơn Close đúng vào những ngày tăng giá**, nên Luật A được lợi một cách cơ học (+0,26pp so với NONE).
- Đã sửa thành **cơ sở khớp chung = Open thô** cho mọi biến thể:
  - Open ≤ trần thì khớp ở Open.
  - Open > trần ≥ Low thì khớp ở trần.
  - Low > trần thì không khớp.
- Thêm biến thể LEGACY (phiên 2/3 trần = anchor, tức luật trước 08-15).
- **Tổng đã chạy: 49 cấu hình** (20 theo prereg, 28 ở bảng hiệu chỉnh, 1 độ nhạy engine). Cả hai bảng có trong `window_design_stdout.txt`. Kết luận về độ rộng **giống nhau ở cả hai cơ sở giá**.

**Bảng chính** (cơ sở Open; Δ so với baseline live **W3·A·ANCH** = 4,61%):

| Cấu hình | fill% | trên vốn | Δ vs W3·A·ANCH | CI95 cụm Δ | ΔIS / ΔOOS | LOYO Δ |
|---|---:|---:|---:|---|---|---|
| W1·A·ANCH | 97,4% | 4,55% | −0,06pp | [−0,13; +0,02] | −0,11 / −0,03 | −0,09…−0,04 |
| **W3·A·ANCH (live)** | 99,9% | **4,61%** | — | — | — | — |
| W4·A·ANCH | 99,9% | 4,61% | +0,00pp | [0; 0] | 0 / 0 | 0 |
| W5·A·ANCH | 99,9% | 4,60% | −0,01pp | [−0,02; 0] | −0,02 / 0 | −0,01…0 |
| W3·A·SHIFT (thoát dời) | 99,9% | 4,60% | −0,01pp | [−0,04; +0,01] | +0,02 / −0,03 | −0,02…−0,01 |
| W5·A·SHIFT | 99,9% | 4,59% | −0,02pp | [−0,05; +0,01] | 0 / −0,03 | −0,03…−0,01 |
| W3·LEGACY·ANCH (≤anchor) | 99,9% | 4,52% | −0,09pp | [−0,12; −0,07] | −0,10 / −0,09 | −0,10…−0,09 |
| W5·NONE·SHIFT (≈ engine pin) | 100% | 4,50% | −0,11pp | [−0,15; −0,08] | −0,10 / −0,12 | −0,12…−0,11 |

Phiên khớp đầu tiên, với W3·A: phiên 1 = 5.219, phiên 2 = 127, phiên 3 = 11. Mở rộng lên W5 chỉ thêm **1** sự kiện, và sự kiện đó lãi −34%.
- Phiên 2 và 3 cứu 138 sự kiện (2,6% N), lãi TB 2,24%.
- Phiên 4 và 5 gần như không còn gì để cứu.
- Tỷ lệ Luật A không khớp mỗi phiên là 2,4–3,0%. Khoá trần biên độ là 1,0–1,2%/phiên.

**Quy tắc quyết định trong PREREG:** chỉ đổi nếu CI Δ loại trừ 0, cùng dấu IS/OOS và LOYO không đổi dấu.
- W1: CI chứa 0 → không đổi.
- W4/W5: Δ ≈ 0 → không đổi.
- ⇒ **Giữ W3.**
- Thoát neo hay thoát dời: khác nhau ≤ 0,02pp. Không có lý do đổi luật thoát.

**Hạn chế.** Mô phỏng khớp ở trần khi Open > trần ≥ Low là hơi lạc quan: giả định lệnh chờ ở trần có ưu tiên hàng đợi. Không mô hình ràng buộc vốn, nên đây là event study chứ không phải NAV. Không mô hình thanh khoản theo phiên.

## D. Độ trung thực của engine pin — ĐO một phần + SUY LUẬN

Engine `pt_v23_audit_2014.py` / `simulate_holistic_nav.py`:
- `max_fill_days=5`, khớp ở **Open**, 20% ADV mỗi phiên.
- Hold tính từ **lần khớp đầu** (thoát dời).
- Không trần giá, không khoá trần, và **luôn có tiền ở phiên chuẩn** (không có WAIT_CASH/plan rỗng/lỗi lịch).

So với live (3 phiên + Luật A + plan/vốn thật):
1. **Về độ rộng cửa sổ và trần: engine BI QUAN rất nhẹ.** Proxy W5·NONE·SHIFT kém live W3·A·ANCH **−0,11pp/sự kiện** CI [−0,15; −0,08] (ĐO). Nguyên nhân: Luật A mua được ở trần những ngày gap-up rồi giảm lại. Lệch 5 phiên so với 3 phiên đóng góp khoảng 0.
2. **Về triển khai vốn: engine LẠC QUAN rất mạnh.** Engine giả định vốn LAG có mặt ở phiên chuẩn. Live chỉ triển khai khoảng 10% slot mục tiêu, hoặc khoảng 23% sức chứa book (ĐO số ca / ƯỚC LƯỢNG tiền).
   - Tôi **không lượng hoá được** tác động lên CAGR pin nếu không chạy NAV với chính kênh lỗi này. Đây là SUY LUẬN về chiều: lạc quan.
   - Mẫu live (2 tuần, 1 mùa, 28 slot) quá nhỏ để ngoại suy ra một tỷ lệ triển khai dài hạn.
3. Pin **không sửa** (đúng ràng buộc). Ai trích CAGR pin của LAG nên kèm caveat: "giả định triển khai đầy đủ ở phiên chuẩn".

## 5. Khuyến nghị

**Giữ cửa sổ 3 phiên**: nới ra 4–5 phiên không cứu thêm sự kiện nào đáng kể (backtest); thu về 1 phiên mất khoảng 0,06pp (không có ý nghĩa thống kê). Toàn bộ vốn lỡ ở live là do vận hành phiên chuẩn, không phải do độ rộng cửa sổ.

**Việc vận hành cụ thể** (mỗi mục đều có artifact ở §A):
1. **Lịch entry do code tính, không để LLM tự diễn giải.** DollarBill phải lấy `entry_date`/`entry_window_day` từ `filter_lag_entry_window.py --json`, cấm tự cộng T+n. Ca 07-24/27 cho thấy hai account diễn giải hai lịch khác nhau cho cùng một tín hiệu, có một lịch rơi vào thứ Bảy, và SpaceX mất 4 slot. → DollarBill/Mike.
2. **Cảnh báo cứng khi ứng viên LAG hợp lệ bị `deferred` ĐÚNG ở phiên chuẩn** (WAIT_CASH / BLOCKED_RECONCILE). Đây đã là việc #3 của nghiên cứu 08-10 và đến nay vẫn chưa có cơ chế; 58% vốn lỡ là WAIT_CASH. Cần kèm phương án cấp vốn JIT (unpark) có hạn chót trước phiên chuẩn, không chờ phiên 2/3. → Mike/Wags.
3. **Cổng nhất quán plan:** `lag_analysis.decision == BUY` thì phải có mặt trong `orders[]` hoặc `deferred_orders[]` kèm lý do. Ca SSI 08-07 bị rơi im lặng ở cả 2 account. Đây là kiểm tra cơ học, nên viết thành checker. → Wags.
4. **Một nguồn DD chung cho cả 2 account.** EVF/PSI/VCI 07-28: ZaloPay loại FLOOR_FAIL, SpaceX xếp VALID. Cùng tín hiệu, cùng ngày, khác quyết định. → DollarBill.
5. Theo dõi mùa Q3 (entry từ khoảng 10-26) như mẫu đầu tiên dưới Luật A, rồi chạy lại `audit_live.py` sau 11-15. Đến lúc đó mới có N live > 0 dưới luật hiện hành.

## Tái lập
```bash
cd /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/lag_entry_window_width_20261021
python3 audit_live.py && python3 classify_live.py
/home/trido/thanhdt/wc_venv/bin/python window_design_bt.py
```
Artifact: `audit_live_rows.csv`, `audit_live_classified.csv`, `exp_window_events.csv`, `exp_window_grid*.csv`, `*_stdout.txt`. Tên `exp_*` không canonical, không pin.
