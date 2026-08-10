# fill_timing — vì sao chưa chốt được, và chốt được ngày nào

Job `Taylor_20260810_032034` · 2026-08-10 · Taylor
Câu hỏi user (John): *"khi nào chốt được vấn đề khung giờ tối ưu để vào lệnh? Cho thời gian xử lý cụ thể"*

---

## TL;DR

- **Phát hiện của Mike CHÍNH XÁC** — và nặng hơn Mike nghĩ: không phải "tỉ lệ trúng thấp" mà là
  **xác suất = 0 TUYỆT ĐỐI, do cấu trúc**. Cron BUY-window chạy **đúng 2 ngày (T3/T5) mà cơ chế
  `BUY_VALUE_FACTOR` bảo đảm luôn NET SELL**. Chờ thêm bao lâu cũng không ra bằng chứng.
- **Gate 1 đang 4/5 phiên** (thiếu đúng 1). Cả 4 phiên đó (07-14/16/21/23) **đúng là từ cron 10:46**
  — xác nhận nghi vấn #2 của Mike.
- **Gate 2 đã 10/5 phiên — ĐÃ ĐẠT.** Gate 3 (0 reject) đạt-có-công-bố.
- **Fix = 1 dòng, xoay `BUY_VALUE_FACTOR` đi ĐÚNG 1 NGÀY** trong file paper-only
  `mike/bin/paper_main_probe_plan.py`. Không chạm `trading_bot/`, không chạm crontab.
- **ETA: fix trước 08:52 ICT 11-08 ⇒ phiên thứ 5 gần như chắc chắn 2026-08-11, bảo đảm cứng
  2026-08-13. Chốt (sau quant-skeptic + user sign-off): 2026-08-14.**
  Không fix ⇒ **không bao giờ chốt**.

---

## 1. Xác nhận độc lập phát hiện của Mike

### 1.1 Ngữ nghĩa nhãn `ft:` (đọc code, không đoán từ tên)

`trading_bot/executor.py:922-955` (`_fill_timing_mult`) + `config.py:66-72`:

| side | mult = 1.0 (`ft:in-window`) khi | ngược lại |
|---|---|---|
| buy | `10:45 ≤ t < 11:15` **HOẶC** `t ≥ 13:00` (phiên chiều) **HOẶC** `urgency=high` **HOẶC** gap-adaptive down-gap 09:15-09:45 | `ft:out×4` |
| sell | `09:15 ≤ t < 09:45` | `ft:out×4` |

⚠️ **Cạm bẫy đo lường:** `ft:in-window` **KHÔNG đồng nghĩa** "nằm trong 10:45-11:15".
`execution_quality_review.py:109` đếm tỉ lệ in-window bằng **string-match trên note**, nên nó
**đếm dư**. 9 lệnh BUY dưới đây mang nhãn `ft:in-window` nhưng **ngoài** cửa sổ 10:45-11:15:

- `2026-07-07 14:19:38` × 6 mã — luật "phiên chiều 13:00+", không phải cửa sổ BUY.
- `2026-07-15 09:15:03` × 3 mã (FPT/MBB/HDB) — `GAP_OPEN_OVERRIDE gap_z=-3.39/-2.32/-2.67`.

⇒ Mọi con số dưới đây tôi đếm **STRICT**: `PLACE` + `side=buy` + `ts ∈ [10:45, 11:15)` +
`ft:in-window` + có ít nhất 1 `FILL` cho đúng `child_oid` đó.

### 1.2 Toàn bộ lần cron `46 3 * * 2,4` đã chạy thật

Nguồn: `mike/logs/run_bot_main_<date>.log` (mtime + nội dung) đối chiếu
`data/execution_logs/exec_main_<date>_journal.csv`. Cron này **bắt đầu chạy thật từ 2026-07-14**
(07-07/07-09 tuy là T3/T5 nhưng log ghi 14:19 và 09:10 → chưa có dòng cron này).

| Ngày | Thứ | Có journal? | BUY placed | BUY in-window + FILL | Vì sao |
|---|---|---|---|---|---|
| 2026-07-14 | T3 | ✅ | 6 | **✅ 6/6** | trước netting: plan gửi cả SELL-all + BUY-all |
| 2026-07-16 | T5 | ✅ | 6 | **✅ 6/6** | " |
| 2026-07-21 | T3 | ✅ | 6 | **✅ 6/6** | " |
| 2026-07-23 | T5 | ✅ | 6 | **✅ 6/6** | " |
| 2026-07-28 | T3 | ❌ (0 lệnh) | 0 | ❌ | `net_offsetting_orders()` LIVE từ 07-27 → net 0 cả 6 mã (log: `INTERNAL_ONLY` ×6) |
| 2026-07-30 | T5 | ✅ nhưng 386 `PLACE_FAIL` + 45 `ATC_FAIL` | 0 | ❌ | sự cố `PaperBroker.place_order` thiếu `cash_only` |
| 2026-08-04 | T3 | ✅ | 0 | ❌ | **sau fix netting**: rotation ⇒ NET SELL (1 lệnh MBB sell) |
| 2026-08-06 | T5 | ✅ | 0 | ❌ | rotation ⇒ NET SELL 6 mã |

**Tỉ lệ thô 4/8 = 50%.** Nhưng chia theo cơ chế thì con số đó vô nghĩa:

| Thời kỳ | Cơ chế | Tỉ lệ |
|---|---|---|
| 07-14 → 07-23 (trước netting) | plan luôn có BUY thật | **4/4 = 100%** |
| 07-28, 07-30 | netting nuốt hết / crash paper broker | 0/2 |
| 08-04 → nay (sau fix netting) | rotation `BUY_VALUE_FACTOR` | **0/2, và = 0% VĨNH VIỄN** |

### 1.3 Vì sao là 0% *tuyệt đối*, không phải "xui"

`mike/bin/paper_main_probe_plan.py:78` — chính comment trong code đã nói ra mâu thuẫn:

```python
# Chuỗi chọn sao cho có 3 ngày net BUY (T2/T4/T6) + 2 ngày net SELL (T3/T5) mỗi tuần
BUY_VALUE_FACTOR = {0: 1.00, 1: 0.75, 2: 0.90, 3: 0.70, 4: 0.85}   # 0=T2 … 4=T6
```

Đối chiếu crontab:

| cron | ngày | mục đích ghi trong comment | rotation cho ra |
|---|---|---|---|
| `46 3 * * 2,4` → 10:46 | **T3, T5** | "BUY-window evidence (10:45-11:15)" | **NET SELL** |
| `10 2 * * 1,3,5` → 09:10 | **T2, T4, T6** | "SELL-window evidence (09:15-09:45)" | **NET BUY** |

**Hai lịch bị đảo ngược đúng 100% so với rotation.** Không phải xác suất thấp:
`qty = round(30M × f / px / 100) × 100`; T2→T3 hệ số giảm **25%**, T4→T5 giảm **22%**. Để một mã
lật thành net BUY thì giá phải **giảm >22% trong 1 phiên** — vượt xa biên độ HOSE ±7%. ⇒ **P = 0
theo đúng nghĩa đen, cho cả 6 mã, mọi phiên T3/T5.**

Điều tương tự đúng ở chiều kia: cron SELL-window (T2/T4/T6) luôn rơi vào ngày NET BUY nên
**cũng không sinh được SELL-window evidence mới** kể từ 08-04 (phiên 08-05 có SELL in-window là do
netting để lại phần dư sell trên 4 mã trong ngày chuyển tiếp, không phải thiết kế).

---

## 2. Trạng thái 5 gate (đo lại hôm nay, STRICT)

| # | Gate | Trạng thái | Bằng chứng |
|---|---|---|---|
| 1 | BUY window adherence | **4/5 — THIẾU ĐÚNG 1 PHIÊN** | 07-14, 07-16, 07-21, 07-23 (6/6 lệnh khớp mỗi phiên) |
| 2 | SELL window adherence | ✅ **10/5 — ĐẠT** | 07-10/13/15/17/20/22/24/27/31, 08-05 |
| 3 | 0 rejects (hoặc được giải thích) | ✅ **ĐẠT-CÓ-CÔNG-BỐ** | Toàn bộ 431 lỗi thuộc **duy nhất 2026-07-30** (`PaperBroker.place_order` thiếu `cash_only`), đã fix+verify cùng ngày; **0 lỗi mọi phiên khác** từ 07-01 |
| 4 | BUY fill không tệ hơn open đáng kể (bps) | ⏳ **KHÔNG gate sớm** — đúng theo `notes` của registry | xem §5 |
| 5 | quant-skeptic → user sign-off | ⏳ chờ gate 1 | |

`review_short` của chương trình = **"≥5 phiên có BUY fill trong cửa sổ + 0 reject → quant-skeptic →
user sign-off"** ⇒ **điều kiện chốt thực tế chỉ còn ĐÚNG 1 PHIÊN của gate 1.**

---

## 3. ETA dưới cơ chế HIỆN TẠI (không sửa gì)

**KHÔNG BAO GIỜ.** Không phải "vài tuần nữa" — cron BUY-window chỉ chạy T3/T5, và T3/T5 được
rotation bảo đảm 100% là ngày NET SELL. Mô phỏng 6 phiên tới bằng chính `build_plan()` thật
(held thật từ `secrets/bot_paper_account.json`, giá thật từ BQ cache):

```
08-11 T3 f=0.75 cron=10:46 BUY-win  ->  0 buy / 6 sell   <== 0 BUY
08-12 T4 f=0.90 cron=09:10 SELL-win ->  6 buy / 0 sell
08-13 T5 f=0.70 cron=10:46 BUY-win  ->  0 buy / 6 sell   <== 0 BUY
08-14 T6 f=0.85 cron=09:10 SELL-win ->  6 buy / 0 sell
08-17 T2 f=1.00 cron=09:10 SELL-win ->  6 buy / 0 sell
08-18 T3 f=0.75 cron=10:46 BUY-win  ->  0 buy / 6 sell   <== 0 BUY
```

---

## 4. FIX ĐỀ XUẤT (kế hoạch — CHƯA áp dụng)

### 4.1 Nội dung: xoay `BUY_VALUE_FACTOR` đi **đúng 1 ngày trong tuần**

`mike/bin/paper_main_probe_plan.py:79` (file **paper-only**, không phải `trading_bot/`):

```python
# HIỆN TẠI — up-day = T2/T4/T6 (lệch pha với cron BUY-window T3/T5)
BUY_VALUE_FACTOR = {0: 1.00, 1: 0.75, 2: 0.90, 3: 0.70, 4: 0.85}

# ĐỀ XUẤT — cùng TẬP giá trị, dịch phải 1 ngày: up-day = T2/T3/T5
BUY_VALUE_FACTOR = {0: 0.85, 1: 1.00, 2: 0.75, 3: 0.90, 4: 0.70}
```

Bất biến thiết kế gốc **giữ nguyên tuyệt đối** — cùng 5 giá trị, vẫn đôi một khác nhau, và bước
nhảy giữa 2 phiên liên tiếp (kể cả vòng T6→T2) vẫn **≥0,15**:

| bước | T6→T2 | T2→T3 | T3→T4 | T4→T5 | T5→T6 |
|---|---|---|---|---|---|
| Δ | +0,15 | +0,15 | −0,25 | +0,15 | −0,20 |
| ⇒ | NET BUY | **NET BUY (T3 = cron 10:46)** | NET SELL | **NET BUY (T5 = cron 10:46)** | NET SELL |

- Cron BUY-window (T3, T5) → **cả 2 đều NET BUY** ✅
- Cron SELL-window (T2, T4, T6) → T4 và T6 NET SELL ✅ (gate 2 vẫn tích luỹ tiếp; T2 thành ngày
  BUY nhưng gate 2 đã 10/5 nên không mất gì)

### 4.2 Mô phỏng bằng `build_plan()` thật với map mới

```
08-11 T3 f=1.00 cron=10:46 BUY-win  ->  4 buy / 2 sell   <== GATE-1 EVIDENCE
08-12 T4 f=0.75 cron=09:10 SELL-win ->  0 buy / 6 sell
08-13 T5 f=0.90 cron=10:46 BUY-win  ->  6 buy / 0 sell   <== GATE-1 EVIDENCE (sạch)
08-14 T6 f=0.70 cron=09:10 SELL-win ->  0 buy / 6 sell
08-17 T2 f=0.85 cron=09:10 SELL-win ->  6 buy / 0 sell
08-18 T3 f=1.00 cron=10:46 BUY-win  ->  6 buy / 0 sell   <== GATE-1 EVIDENCE
```

**Độ tin cậy 2 mốc:**
- **08-11 (T3): RẤT CÓ KHẢ NĂNG, không bảo đảm.** Đây là ngày chuyển tiếp — 08-10 đã chạy với hệ
  số cũ 1,00 và hệ số mới của T3 cũng là 1,00 ⇒ qty mục tiêu ≈ qty đang giữ, phần net đến từ
  **backstop `if qty == held: qty += 100`** (backstop LUÔN đẩy về phía BUY) và từ sai số làm tròn
  lô. Mô phỏng ở giá cache 08-07 cho 4/6 mã net BUY. Giá thật ngày 11 có thể xê dịch kết quả.
- **08-13 (T5): BẢO ĐẢM CỨNG.** Bước +0,15 (0,75→0,90 = target tăng 20%) — muốn lật thành SELL thì
  giá phải tăng >20% trong 1 phiên, bất khả với biên độ ±7%.

### 4.3 Vì sao chọn cách này thay vì đổi crontab

Phương án thay thế là hoán đổi ngày 2 dòng cron (`46 3 * * 2,4` → `1,3,5` và ngược lại). Tôi
**không đề xuất** vì: (a) đó là 2 dòng cron **thực thi lệnh** (`bot_execute.py`) — theo
`kb/account_onboarding_runbook.md` loại dòng này phải hỏi user trước, trong khi việc cần làm chỉ là
sửa 1 hằng số của một script probe paper-only; (b) đổi cron sẽ **phá gate 2** (đẩy SELL-window sang
đúng ngày NET BUY), trong khi cách xoay hệ số giữ được cả hai; (c) `paper_main_early_check.sh` cũng
bám 2 khung giờ đó, đổi cron phải sửa kéo theo 4 dòng thay vì 1 hằng số.

### 4.4 Checklist khi áp dụng (chưa làm — chờ user duyệt qua Mike)

1. Sửa `BUY_VALUE_FACTOR` + cập nhật comment mô tả up-day (`T2/T3/T5`) và ghi rõ lý do đồng bộ với
   cron 10:46 — tránh người sau "sửa lại cho đẹp" rồi tái lập lỗi lệch pha.
2. Chạy `paper_main_window_selfcheck.py` (bộ selfcheck sở hữu chính hành vi này, case C/D) +
   selfcheck của netting. Theo §23 coding_guidelines: `paper_main_probe_plan.py` **không** thuộc
   nhóm module lõi ⇒ chạy đúng phạm vi, không quét cả bộ.
3. Chạy `python3 mike/bin/paper_main_probe_plan.py --date 2026-08-11 --dry` xác nhận có lệnh BUY.
4. **Phải xong trước 08:52 ICT** ngày áp dụng (giờ cron sinh plan `52 1 * * 1-5`); nếu trễ, plan đã
   ghi thì cần `--force` mới ghi đè.
5. Sau phiên: verify bằng chính script STRICT ở §1.1, **không** tin `execution_quality_review.py`
   (nó đếm dư — xem cạm bẫy đo lường).

### 4.5 Việc phụ nên làm kèm (không chặn)

`execution_quality_review.py:109` nên đếm in-window theo **timestamp thật** thay vì string-match
`ft:in-window`, và tách riêng "trong cửa sổ BUY 10:45-11:15" với "được miễn vì phiên chiều /
gap-override". Hiện tại nó báo lạc quan hơn thực tế 9 lệnh (§1.1). Đây là công cụ review, không
phải đường chặn lệnh ⇒ ưu tiên thấp, nhưng phải sửa **trước khi** dùng số của nó trong báo cáo
sign-off.

---

## 5. Trả lời thẳng câu hỏi của user

> **"Với cơ chế hiện tại: KHÔNG BAO GIỜ chốt được."** Không phải chậm — cron thu thập bằng chứng
> BUY chạy đúng vào 2 ngày trong tuần mà cơ chế probe bảo đảm không bao giờ có lệnh mua. Đã đứng
> im ở 4/5 phiên từ **2026-07-23**, tức 18 ngày, và sẽ đứng im vô hạn.
>
> **Cần sửa 1 dòng (xoay hệ số theo thứ trong `mike/bin/paper_main_probe_plan.py`, paper-only).
> Sau khi sửa:**
>
> | Mốc | Ngày | Ghi chú |
> |---|---|---|
> | Áp fix + selfcheck | **2026-08-10 (T2)**, xong trước 08:52 ICT 08-11 | 1 hằng số, ~30 phút gồm selfcheck |
> | Phiên thứ 5 (khả năng cao) | **2026-08-11 (T3)** | ngày chuyển tiếp, phụ thuộc làm tròn lô |
> | Phiên thứ 5 (bảo đảm cứng) | **2026-08-13 (T5)** | bước hệ số +20%, không thể lật |
> | quant-skeptic + user sign-off | **2026-08-14 (T6)** | |
> | **CHỐT** | **2026-08-14**, chậm nhất **2026-08-17 (T2)** | |

### Chốt cái gì — nói rõ để không hiểu nhầm

Chốt ở đây = **xác nhận CƠ CHẾ chạy đúng** (lệnh mua thật sự dồn vào 10:45-11:15, lệnh bán vào
09:15-09:45, không reject) ⇒ đủ căn cứ bật `fill_timing_live_gate` cho tiền thật.

**KHÔNG phải** chốt "edge 17,6bps là thật trên fill sống". Con số 17,6bps đến từ backtest riêng
(16 mã, 9670 ticker-day, t=12,0 — `config.py:62-65`), còn nhiễu fill trong ngày là 110–220bps.
Để đo lại edge đó bằng chính paper main: với σ ~100bps mức phiên và Δ=17,6bps, cần
n ≈ (2×100/17,6)² ≈ **130 phiên có BUY fill** ≈ **65 tuần ở nhịp 2 phiên/tuần**. ⇒ **đừng đợi
bps** — chính `notes` của registry đã chốt "EDGE bps cần nhiều tuần — không gate sớm trên bps".
Nếu user muốn số bps làm điều kiện, câu trả lời trung thực là **>1 năm**, và nên bác phương án đó
thay vì hứa.

---

## Nguồn đã đọc trực tiếp (không suy từ tên/comment)

- `crontab -l` dòng 79-86
- `mike/logs/run_bot_main_2026-07-*.log`, `run_bot_main_2026-08-0*.log` (mtime + nội dung)
- `data/execution_logs/exec_main_2026-07-*_journal.csv`, `exec_main_2026-08-*_journal.csv` (22 file)
- `trading_bot/executor.py:922-955, 1162-1166`; `trading_bot/config.py:60-72`
- `mike/bin/paper_main_probe_plan.py` (toàn file)
- `mike/kb/paper_programs_registry.json` → program `fill_timing`
- `secrets/bot_paper_account.json` (held), `data/bq_cache/ticker_1m.parquet` (px)
- `execution_quality_review.py:89-110`

Script kiểm chứng: `/tmp/ft_scan.py`, `/tmp/ft_fill.py`, `/tmp/strict.py`, `/tmp/gates.py`,
`/tmp/sim.py` (mô phỏng gọi thẳng `build_plan()` thật, không sửa file production).
