# fill_timing — checkpoint 5/5 gate, đo bằng dữ liệu thật

Job `Taylor_20260811_091002` · 2026-08-11 · Taylor
Dispatch từ Mike: *"checkpoint đã tới hạn nhưng 5/5 tiêu chí vẫn pending — chưa ai thực sự đi kiểm tra"*.

---

## TL;DR

- **Gate 1-4: PASS.** Không phải "coi như đạt" — đo lại từ đầu bằng `data/execution_logs/exec_main_*_journal.csv`
  (23 phiên, 2026-07-07 → 2026-08-11) + `Open` từ `tav2_bq.ticker_1m`.
- **Gate 1 (BUY adherence) vừa đủ ngưỡng ĐÚNG HÔM NAY**: phiên thứ 5 là 2026-08-11 — đúng như ETA
  của job `Taylor_20260810_032034` dự báo. Fix xoay `BUY_VALUE_FACTOR` đã có tác dụng thật.
- **Gate 5: pending — và tôi khuyến nghị GIỮ pending.** Lý do KHÔNG phải thiếu dữ liệu mà là
  **lệch cơ chế**: cái sắp lên live là HYBRID, nhưng 5 phiên bằng chứng của gate 1 gồm 4 phiên
  cơ chế CŨ + 1 phiên hybrid.
- Đề xuất mốc: thêm 4 phiên BUY hybrid (cron T3/T5 → **08-13, 08-18, 08-20, 08-25**) →
  quant-skeptic ~**08-26** → user sign-off. **KHÔNG tự bật live.**

---

## 1. Phương pháp — vì sao không dùng thẳng số của probe

Probe registry (`python3 execution_quality_review.py`) hôm nay in:

```
journal ft-notes: 185 placements | in-window 49% | out-of-window 51%
journal FAIL/ERROR events: 431
C. DIRECTIONAL FILL SANITY ... no completed fills yet
```

Ba con số này **không dùng trực tiếp để chốt gate được**, cả ba đều vì lý do cấu trúc:

1. **"49% in-window" trộn hai chiều.** Cron probe chạy 2 khung: **09:15 (T2/T4/T6)** để thử cửa sổ
   BÁN và **10:46 (T3/T5)** để thử cửa sổ MUA. Trên phiên 09:15, lệnh MUA **buộc phải** ngoài cửa
   sổ (và ngược lại) — đó là cơ chế chạy ĐÚNG, không phải mất adherence. Gate 1 và gate 2 phải đo
   TÁCH theo chiều, trên đúng nhóm phiên của chiều đó.
2. **Nhãn `ft:in-window` ≠ "nằm trong cửa sổ".** Nó là `ft_mult == 1.0`
   (`trading_bot/executor.py:1423`), mà mult=1.0 còn xảy ra ở: phiên chiều ≥13:00 (nhánh buy),
   `urgency=high`, gap-adaptive down-gap, và live-gate. Đếm bằng string-match → **đếm dư 9 lệnh**
   (6× `2026-07-07 14:19` luật phiên chiều, 3× `2026-07-15 09:15` `GAP_OPEN_OVERRIDE`).
   Tái xác nhận độc lập phát hiện của job `Taylor_20260810_032034`. **Mọi số dưới đây đo bằng
   TIMESTAMP thật của event `PLACE`, không bằng nhãn.**
3. **Mục C không bao giờ tính được cho paper.** Nó đọc `data/execution_logs/dnse_raw_*.jsonl` —
   file chỉ do broker DNSE **live** ghi; `main` là `mode=paper` → `PaperBroker` → không có dòng
   nào. "no completed fills yet" là **hạn chế công cụ**, không phải "chưa có fill" (thực tế có
   185 FILL). Gate 4 phải đo từ journal.

---

## 2. Gate 1 — BUY window adherence (10:45-11:15): **PASS**

Chỉ tính phiên probe 10:46 (nhóm thử cửa sổ MUA) có phát sinh lệnh mua:

| Phiên | Lệnh MUA | Trong cửa sổ (timestamp) | Khớp |
|---|---:|---:|---:|
| 2026-07-14 | 6 | 6 | 6 |
| 2026-07-16 | 6 | 6 | 6 |
| 2026-07-21 | 6 | 6 | 6 |
| 2026-07-23 | 6 | 6 | 6 |
| **2026-08-11** | **4** | **4** | **4** |
| **Tổng** | **28** | **28 (100%)** | **28** |

- `2026-07-30` (10:46) và `2026-08-04`/`2026-08-06` (10:46) không có lệnh mua → không tính:
  07-30 là ngày sự cố PLACE_FAIL, 08-04/08-06 là ngày net-SELL của `BUY_VALUE_FACTOR` cũ.
- **08-11 là phiên hybrid**: 4 lệnh mua bị `HYBRID_DEFER` lúc 10:46:03 ("ngoài block, còn 5 block
  phía trước"), đặt lại **11:00:06** với nhãn `ft:in-window hyb:blk left=5` → vẫn trong 10:45-11:15.
  Cơ chế hoãn-theo-lịch chạy đúng.

⇒ Đạt ngưỡng `review_short` **"≥5 phiên có BUY fill trong cửa sổ"** đúng ngày hôm nay.

## 3. Gate 2 — SELL window adherence (09:15-09:45): **PASS** (vượt xa)

10 phiên probe 09:15 có lệnh bán: 07-13, 07-15, 07-17, 07-20, 07-22, 07-24, 07-27, 07-31, 08-05
(và 07-10, ngoài phạm vi có `Open` trong `ticker_1m`) — **50/50 lệnh trong cửa sổ, 50/50 khớp**.
Không có phiên nào lệch.

## 4. Gate 3 — 0 rejects/fails: **PASS (có công bố)**

Kiểm kê toàn bộ event của `exec_main_*` từ 2026-06-26:

| | PLACE | FILL | DONE | PLACE_FAIL | ATC_FAIL | GHOST_ORDER | HYBRID_DEFER |
|---|---:|---:|---:|---:|---:|---:|---:|
| Ngoài 07-30 | 185 | 185 | 183 | **0** | **0** | 18 | 4 |
| Riêng 07-30 | 0 | 0 | 0 | **386** | **45** | 0 | 0 |

- **431 lỗi = 100% thuộc 1 ngày 2026-07-30**, một root cause duy nhất
  (`PaperBroker.place_order` thiếu tham số `cash_only`), fix + verify cùng ngày —
  `mike/kb/incidents/2026-07/2026-07-30-paper-trading-report-3-root-causes.md`.
  **9 phiên kể từ 07-31: 0 lỗi.** Con số 431 còn hiện trong probe vì cửa sổ `--since 2026-06-26`
  chưa trượt qua, không phải lỗi đang tái diễn.
- **18 `GHOST_ORDER`** (07-08 ×6, 07-09 ×6, 08-07 ×6): guard idempotency (`_ghost_tickers`) phát
  hiện lệnh có ở sổ broker mà không có trong state — xảy ra khi chạy LẠI harness trong cùng ngày
  giao dịch với state mới (07-08/07-09 02:10; 08-07 13:05). **Đúng thiết kế** (§5 coding_guidelines:
  không đoán-rồi-gộp, dừng lại chờ người), không phải reject của broker. Ghi nhận là *watch*, không
  chặn gate.

## 5. Gate 4 — fill vs day-open: **PASS ở mức SANITY** (không phải bằng chứng edge)

Đo thủ công: giá `FILL` trong journal ÷ `Open` cùng mã/ngày (`tav2_bq.ticker_1m`, cửa sổ có dữ liệu
từ 2026-07-13). Đơn vị thống kê = **NGÀY** (không phải lệnh — 6 lệnh cùng phiên không độc lập).

| Chiều | Vị trí | n ngày | Trung bình ngày (bps vs open) | sd ngày | se | t |
|---|---|---:|---:|---:|---:|---:|
| BUY | **trong** cửa sổ | 4 | **−1,7** (thấp hơn = tốt) | 97,8 | 48,9 | −0,03 |
| BUY | ngoài (09:15) | 10 | +12,3 | 9,1 | 2,9 | +4,29 |
| SELL | **trong** cửa sổ | 9 | **−9,1** (cao hơn = tốt) | 6,1 | 2,0 | −4,45 |
| SELL | ngoài (10:46) | 6 | −14,2 | 80,3 | 32,8 | −0,43 |

Đọc đúng:

- **Tiêu chí gate là SANITY** ("không tệ hơn open **đáng kể**"), và nó đạt: BUY trong cửa sổ
  −1,7 bps — không có dấu hiệu bị đánh dấu giá lên hệ thống. SELL trong cửa sổ −9,1 bps là
  **dưới một bước giá** (tick 50đ trên giá 22.600 = 22 bps), tức nhiễu làm tròn, không phải bán rẻ.
- **KHÔNG được đọc thành edge.** Edge kỳ vọng 17,6 bps trong khi **se ngày của nhánh BUY
  in-window = 48,9 bps** → power ≈ 0. Xem chuỗi ngày: `07-14 +37 · 07-16 +9 · 07-21 +88 ·
  07-23 −140` — đó là **biến động cả ngày của thị trường**, không phải chất lượng khớp. Bằng chứng
  đối chứng: cùng ngày 07-23, nhánh SELL ngoài cửa sổ cũng −160 bps.
- Nhánh "ngoài cửa sổ" có t lớn nhưng **không phải phản chứng**: +12,3 bps của BUY 09:15 chỉ là
  chi phí cross ngay tại mở cửa (~1 tick), đo trên mẫu đồng nhất nên sd nhỏ.
- **Caveat thực thi**: `PaperBroker` khớp trọn tại giá đặt (cross quote sống), **không mô hình hàng
  đợi/slippage** — số vs-open phản ánh đường đi của giá tại thời điểm đặt, không phản ánh độ khó khớp.
- 2026-08-11 chưa vào được bảng (BQ chưa sync phiên T; §6: same-day không đọc BQ). Sẽ có sau
  `sync_bq_cache_daily.sh` 23:45 hôm nay.

## 6. Gate 5 — quant-skeptic → user sign-off: **pending, và nên giữ pending**

Vướng mắc **không còn là dữ liệu** (4/4 gate cơ học đã đạt) mà là **lệch cơ chế**:

1. **Cái sắp lên live là HYBRID, nhưng hybrid mới có 1 phiên paper.** `fill_timing_hybrid_enabled`
   bật trên paper 2026-08-10; phiên đầu tiên là 08-11 (hôm nay). 5 phiên bằng chứng gate 1 =
   4 phiên cơ chế gom-cửa-sổ CŨ + 1 phiên hybrid. Gate viết cho cơ chế cũ; flip live bây giờ là
   deploy một cơ chế có n=1.
2. **Chính hybrid vừa có 3 vòng REFUTED tìm ra lỗi thật** (giao thoa EXTREME, deadlock arm,
   deadlock qua quote lỗi — job `Taylor_20260810_034544`/`_051847`). Code mới sửa hôm qua, burn-in
   1 phiên là quá mỏng cho tiền thật.
3. **Cơ chế TRẢI BLOCK của hybrid chưa từng được thực chứng trên paper.** Probe đặt qty=100 cp/mã
   → khớp trọn ngay block đầu (`hyb:blk left=5` rồi DONE). Tức 08-11 chỉ chứng minh phần *hoãn tới
   block đúng giờ*, chưa chứng minh phần *chia nhỏ nhiều block*.

**Đề xuất (user quyết, tôi không tự bật):**

- **A — khuyến nghị:** chờ đủ **5 phiên BUY hybrid**. Cron BUY-probe chạy T3/T5 ⇒ 08-13, 08-18,
  08-20, 08-25 → đủ **2026-08-25**; quant-skeptic ~**08-26**; user sign-off ~**08-27**.
- **B — nếu user coi gate cơ học là bất biến theo cơ chế** (adherence là "đặt đúng khung giờ", cả
  2 cơ chế đều đạt): chạy quant-skeptic ngay tuần này, sign-off ~**08-14** như ETA cũ.
- Kèm theo (rẻ, nên làm dù chọn A hay B): **nâng qty probe** trong
  `mike/bin/paper_main_probe_plan.py` để một mã cần >1 block, lấy bằng chứng cho phần trải block.
  Đánh đổi: gãy tính so sánh với 5 phiên đã đo → nếu làm thì nên đếm lại từ phiên đầu tiên sau khi đổi.

**`fill_timing_live_gate` vẫn `True`** (`trading_bot/config.py:67`) — không account live nào bị
ảnh hưởng bởi bất cứ điều gì trong báo cáo này.

---

## 7. Việc kèm theo cho công cụ đo (không chặn gate)

- `execution_quality_review.py` mục A nên tách theo **chiều × nhóm phiên** và đếm theo timestamp;
  hiện tại "49% in-window" là con số không diễn giải được.
- Mục C nên nói thẳng "paper không ghi `dnse_raw`, dùng journal" thay vì "no completed fills yet" —
  hiện tại nó im lặng đúng vào gate mà nó được lập ra để đo.
- Cả hai đều là sửa **công cụ báo cáo**, không chạm `trading_bot/`. Chưa làm trong job này (ngoài
  phạm vi dispatch: dispatch yêu cầu *kiểm tra bằng dữ liệu thật*, tôi đã đo trực tiếp thay vì tin
  probe).
