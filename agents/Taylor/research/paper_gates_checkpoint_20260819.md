# Checkpoint 2 gate paper-program bằng journal thật — 2026-08-19

**Job**: `Taylor_20260819_110954` (dispatch từ Mike, user đã duyệt)
**Phạm vi**: ĐO và KẾT LUẬN. Không flip live gate, không sửa code/config production, không sửa tay
`kb/paper_programs_charter/` (file tự sinh). Chỉ cập nhật `kb/paper_programs_registry.json`.

**Nguồn**: `data/execution_logs/exec_main_*_journal.csv` (28 file, 2026-07-07→2026-08-19),
`trading_bot/executor.py`, `trading_bot/config.py`, `secrets/trading_bot_accounts.json`,
BigQuery `tav2_bq.ticker`. Mọi số dưới đây tái lập được từ 4 nguồn đó.

---

## PHẦN 1 — EXTREME-regime gate (`id=extreme_regime`)

### 1.1 Phiên EVIDENCE

Định nghĩa dùng nhất quán với checkpoint 2026-08-04 (job `Taylor_20260804_124404`):
**evidence = journal có ≥1 sự kiện `PLACE` THÀNH CÔNG** (executor chạy thật VÀ đặt được lệnh).

| Loại | Số file | Ngày |
|---|---:|---|
| Có `PLACE` thành công → **evidence** | **25** | 07-07, 07-10, 07-13, 07-14, 07-15, 07-16, 07-17, 07-20, 07-21, 07-22, 07-23, 07-24, 07-27, 07-31, 08-04, 08-05, 08-06, 08-07, 08-10, 08-11, 08-12, 08-13, 08-17, 08-18, 08-19 |
| Chỉ `GHOST_ORDER`, 0 lệnh đặt → KHÔNG tính | 2 | 07-08, 07-09 |
| Toàn `PLACE_FAIL`/`ATC_FAIL` (386+45), 0 lệnh đặt → KHÔNG tính | 1 | 07-30 |
| **Tổng file journal** | 28 | |

Kiểm chứng quy tắc đếm: áp đúng quy tắc này tính tới 2026-08-04 cho **15** — khớp TUYỆT ĐỐI con số
15/20 mà checkpoint 08-04 đã pin. Quy tắc không bị đổi giữa chừng.

⇒ **25/20 phiên evidence — ĐẠT ngưỡng.** Phiên thứ 20 rơi vào **2026-08-11**.

Phân rã theo chiều lệnh (quan trọng: `EXTREME_PAUSE` + `EXTREME_FLOOR_GUARD` là marker chiều MUA):

- Phiên có lệnh MUA: **20/25**. 5 phiên chỉ có lệnh BÁN ⇒ buy-path không được đánh giá:
  07-31, 08-04, 08-06, 08-12, 08-19.
- Phiên sạch M5 cho nhánh trigger (ii): **22/25** (loại 07-07, 07-10, 07-13 — đọc `rvol_20d`
  từ monolith `ticker_prune.parquet` đóng băng 06-26). Fix của Winston = commit `16309166`
  `2026-07-13 21:44:33 +0700`, tức SAU phiên 07-13 ⇒ 07-14 trở đi sạch. Đã verify bằng `git show`.

### 1.2 Marker / false-trigger

Quét chuỗi CHÍNH XÁC ở CẢ cột `event` LẪN `note`, cả 28 file:

| Marker (khớp code) | Vị trí trong code | Số phiên | Số dòng |
|---|---|---:|---:|
| `EXTREME_PAUSE` | `executor.py:1660` | 0 | 0 |
| `EXTREME_FLOOR_GUARD` | `executor.py:1666` | 0 | 0 |
| `EXTREME_DOWN sell-to-floor` | `executor.py:1684` | 0 | 0 |
| *(kiểm tra lỏng hơn)* bất kỳ chuỗi `EXTREME` | — | 0 | 0 |

⇒ **0 marker / 25 phiên evidence. ZERO false-trigger.**

### 1.3 Gate có THỰC SỰ được nạp không (chống kết luận rỗng)

"0 marker" chỉ có nghĩa nếu gate đang bật. Nạp config đúng đường `run_bot` dùng:

```
load_config() → load_accounts(cfg):
  main    | mode=paper | extreme_regime_enabled=True  | band=0.03 | move_z=3.0
  ZaloPay | mode=live  | extreme_regime_enabled=False
  SpaceX  | mode=live  | extreme_regime_enabled=False
  RocketX | mode=live  | extreme_regime_enabled=False
  ab_cross/ab_dip | paper | False
```

⇒ Gate ARMED đúng 1 account paper `main`, LIVE không đụng. **"0 marker" là kết luận thật, không rỗng.**

### 1.4 ⚠️ HAI PHÁT HIỆN MỚI VỀ PHẠM VI — làm HẸP kết luận, chưa từng đo trước đây

Registry cũ đã cảnh báo bằng văn xuôi ("rổ probe large-cap chưa bao giờ tới gần sàn"). Lần này đo
được thành SỐ, và số nói mạnh hơn văn xuôi.

**(A) Nhánh trigger (i) — cận sàn — CHƯA BAO GIỜ trong tầm với.**

Điều kiện: `last <= floor × (1 + extreme_band)` với `extreme_band = 0.03`.
Đo trên **toàn bộ 242 dòng `PLACE` có giá** mà executor từng phát ra (= đúng những mức giá
executor THỰC SỰ quan sát), so với sàn ước lượng `prev_close × 0,93` (cả 6 mã đều HOSE):

| Chỉ số | Giá trị |
|---|---|
| Headroom trên sàn NHỎ NHẤT từng quan sát | **+4,43 %** (VNM 2026-07-23 10:46) |
| `extreme_band` | 3,00 % |
| Số dòng `PLACE` nằm TRONG band | **0 / 242** |

Có 3 phiên rổ probe THỰC SỰ rơi vào band trong ngày — nhưng executor đã tắt từ lâu:

| Ngày | Mã | Open trên sàn | Low trên sàn | Executor sống |
|---|---|---:|---:|---|
| 2026-07-15 | FPT | +7,68 % | **+2,17 %** | 09:15:03→09:47:27 |
| 2026-07-20 | HPG | +7,03 % | **+0,88 %** | 09:15:04→09:15:24 (20 s) |
| 2026-07-22 | HDB | +7,73 % | **+1,34 %** | 09:15:08→09:15:28 (20 s) |

Tại đúng thời điểm executor đang poll, giá cách sàn **7,03–7,73 %** — hơn gấp đôi band. Cú sập
xuống band xảy ra sau đó, khi không còn gì chạy.
⇒ Trigger (i) **chưa từng được thử một lần nào** trên paper.

**(B) Nhánh trigger (ii) — 3-sigma — phần lớn KHÔNG THỂ với tới về mặt cấu trúc.**

`_r15` (`executor.py:499`) cần mẫu giá tuổi `0,7×15 → 2,0×15` phút, tức px_hist ≥ ~10,5 phút.
Đo tuổi thọ executor mỗi phiên từ timestamp journal:

| Chỉ số | Giá trị |
|---|---|
| Tuổi thọ TRUNG VỊ 1 phiên | **20 giây** |
| Phiên chạy < 15 phút (= `dip_window_min`) | **20 / 28** |

Trong các phiên đó `_r15` trả `None` ⇒ trigger (ii) fail-safe `False` **do cấu trúc**, không phải
do thị trường lành tính. Đếm trực tiếp từ nhãn journal (`no-hist` = `_r15` trả None):

| | Số dòng |
|---|---:|
| `PLACE` tổng | 242 |
| có `r15=` (tức `_r15` tính được) | **49** |
| `no-hist` (`_r15` = None) | 102 |
| nhánh `adp:twap` (note không in r15) | 91 |

Và trên 49 quan sát tính được, r15 âm nhất từng thấy = **−0,90 %** (ACB 2026-08-17 11:00).
Ngưỡng kích là `r15 < −3,0 × rvol_20d`; `rvol_20d` đo từ BQ trên chính 6 mã, cửa sổ 07-07→08-19:

| Mã | rvol_20d min | rvol_20d avg | Ngưỡng LỎNG NHẤT (−3σ tại rvol min) |
|---|---:|---:|---:|
| VNM | 0,807 % | 1,546 % | **−2,42 %** |
| HPG | 0,826 % | 1,636 % | −2,48 % |
| MBB | 0,890 % | 1,612 % | −2,67 % |
| HDB | 0,947 % | 1,538 % | −2,84 % |
| FPT | 1,116 % | 1,939 % | −3,35 % |
| ACB | 1,123 % | 1,353 % | −3,37 % |

⇒ Cú giảm mạnh nhất executor từng đo được (−0,90 %) mới đi được **~37 %** quãng đường tới ngưỡng
LỎNG NHẤT (−2,42 %). Trigger (ii) cũng **chưa từng tới gần**.

> Hệ quả: caveat M5 (3 phiên rvol stale) hoá ra là mối lo NHỎ. Vấn đề lớn hơn là **harness probe
> sống trung vị 20 giây** nên nhánh 3-sigma gần như không được cấp dữ liệu để chạy. Muốn evidence
> của trigger (ii) có nghĩa thì phải kéo dài tuổi thọ executor (≥20-30 phút) — đây là thay đổi
> harness, KHÔNG phải thay đổi gate, và nằm ngoài phạm vi job này.

### 1.5 Kết luận Phần 1

| Gate | Trước | Sau | Căn cứ |
|---|---|---|---|
| 1. Stress-injection 24/24 | pass | pass | không đổi |
| 2. ZERO false-trigger ~4 tuần benign | **pending** | **pass (kèm caveat phạm vi)** | 25/20 phiên evidence, 0/25 marker, gate verified ARMED |
| 3. Không can thiệp NORMAL-path | pass | pass | 0 marker ⇒ 0 lần can thiệp |
| 4. User sign-off | pending | **pending — KHUYẾN NGHỊ xin chữ ký** | không tự bật |

**Điều kiện định lượng đã đạt đủ.** Nhưng bằng chứng là **MỘT CHIỀU**: nó chứng minh gate
KHÔNG kêu bậy trong điều kiện lành tính; nó KHÔNG chứng minh gate xử lý đúng khi thị trường sập,
vì **cả hai** nhánh trigger đều chưa từng tới gần ngưỡng (4,43 % vs band 3,00 %; −0,90 % vs
−2,42 %). Phần "xử lý đúng khi sập" hiện CHỈ được bảo chứng bởi stress-injection 24/24 (gate 1),
tức bằng chứng tổng hợp, không phải bằng chứng thị trường thật.

**KHÔNG flip live gate.** Trình user quyết định, kèm nguyên văn caveat trên.

---

## PHẦN 2 — Fill-timing window (`id=fill_timing`)

### 2.1 Phương pháp — đo bằng TIMESTAMP, không string-match

Nhãn `ft:in-window` nghĩa là `mult == 1.0`, KHÔNG phải "nằm trong cửa sổ". Tái lập lại đúng
**9 ca đếm dư** đã biết để chứng minh phép đo dưới đây độc lập với nhãn:

- 6 × `2026-07-07T14:19:38` (FPT/MBB/ACB/HDB/VNM/HPG) — luật phiên chiều `t >= 13:00 → 1.0`
- 3 × `2026-07-15T09:15:03` (FPT/MBB/HDB) — `GAP_OPEN_OVERRIDE` (gap_z −3,39 / −2,32 / −2,67)

Khớp chính xác 9/9 ca registry đã ghi ⇒ phép đo bằng timestamp là đúng công cụ.

### 2.2 ⚠️ ĐÍNH CHÍNH THƯỚC ĐO — HYBRID không dùng cửa sổ 10:45-11:15

`config.py:167` — lịch HYBRID chiều MUA là **5 block × 15 phút**:
`["11:00", "11:15", "13:00", "13:15", "13:30"]` (phủ 11:00-11:30 và 13:00-13:45).
Cửa sổ `10:45-11:15` (`config.py:137-138`) là cơ chế **gom-cửa-sổ TIỀN-hybrid**, chỉ còn hiệu lực
khi `_hybrid_active()` = False (`executor.py:1460-1470`).

Đo hybrid bằng `10:45-11:15` là **sai thước**: ngày 08-13 có 4 lệnh đặt lúc `11:15:08` — NGOÀI
`10:45-11:15` nhưng nằm ĐÚNG trong block 2 (11:15-11:30). Bảng dưới báo cả hai thước.

### 2.3 Phiên HYBRID BUY thực đo

| Ngày | Thứ | hybrid | BUY đặt | trong block | số block | trong 10:45-11:15 | BUY khớp | Chi tiết |
|---|---|---|---:|---:|---:|---:|---:|---|
| 2026-08-10 | Mon | no | 6 | 0 | 0 | 0 | 6 | (tiền-hybrid, 09:15) |
| **2026-08-11** | Tue | YES | 4 | **4** | 1 | 4 | 4 | blk1(11:00)×4 |
| 2026-08-12 | Wed | YES | **0** | 0 | 0 | 0 | 0 | phiên chỉ-BÁN ⇒ không tính |
| **2026-08-13** | Thu | YES | 10 | **10** | **2** | 6 | 10 | blk1(11:00)×6 + blk2(11:15)×4 |
| **2026-08-17** | Mon | YES | 5 | **5** | 1 | 5 | 5 | blk1(11:00)×5 |
| **2026-08-18** | Tue | YES | 5 | **5** | 1 | 5 | 5 | blk1(11:00)×5 |
| 2026-08-19 | Wed | YES | **0** | 0 | 0 | 0 | 0 | phiên chỉ-BÁN ⇒ không tính |

**Adherence: 24/24 lệnh MUA hybrid nằm trong block đã lên lịch (100 %), 24/24 khớp, 0 lệnh
đặt ngoài block.**

### 2.4 Bộ đếm — 4, không phải 3

- Theo **tiêu chí đo được** (hybrid bật + ≥1 lệnh MUA đặt trong block): **4 phiên** —
  08-11, 08-13, **08-17**, 08-18.
- Theo **danh sách ngày phương án A** (08-11 / 08-13 / 08-18 / 08-20 / 08-25): **3 phiên**.

Chênh lệch = **2026-08-17 (Thứ Hai)**. Đây là phiên KHÔNG có trong danh sách dự báo — danh sách đó
suy từ cadence cron T3/T5, mà 08-17 executor chạy dài (09:15:05→11:00:29, 6.324 s) nên HYBRID hoãn
5 lệnh MUA (`HYBRID_DEFER` lúc 09:15:05) rồi đặt đúng block 11:00. Tức 08-17 đạt CÙNG một tiêu chí
thực chất với 3 phiên kia — danh sách ngày là **dự báo lịch**, không phải định nghĩa gate.

**Cả hai cách đọc đều CHƯA tới 5.** Không dispatch quant-skeptic ở checkpoint này.

### 2.5 Block-spreading — đã được thực chứng (cập nhật ghi chú cũ)

Registry ghi "cơ chế TRẢI BLOCK chưa từng được thực chứng trên paper (probe qty=100 khớp trọn
block đầu)". **Điều này đã hết đúng từ 2026-08-13**: 4 mã (ACB/HDB/HPG/MBB) mỗi mã đặt 2 block —
block 1 lúc `11:00:05` rồi block 2 lúc `11:15:08` với `filled_total=100` mang sang, note
`hyb:blk left=4`. Trải block chạy thật.
⚠️ Mới **n=1 phiên** ⇒ giảm mức độ lo, KHÔNG xoá được nó khỏi danh sách cần theo dõi.

### 2.6 Kết luận Phần 2

- Gate 1-4 (cơ học): giữ **pass**, không có dữ liệu nào lật ngược.
- Gate 5 (quant-skeptic → user sign-off): giữ **pending**. Bộ đếm **4/5** (đo được) hoặc **3/5**
  (danh sách phương án A). Còn thiếu: **2026-08-20 (T5)** và, nếu theo danh sách gốc, **2026-08-25 (T3)**.
- NEXT ACTION khi đủ 5 (sớm nhất 08-20 theo cách đọc đo được; 08-25 theo danh sách gốc):
  (1) đo lại 5 phiên bằng timestamp + thước BLOCK như mục 2.2-2.3;
  (2) `verify_finding.sh` → quant-skeptic;
  (3) CONFIRMED ⇒ escalate user xin chữ ký flip `fill_timing_live_gate`. Phương án A đã chốt
  2026-08-14, KHÔNG hỏi lại A/B/C.
- **KHÔNG flip live gate ở checkpoint này.**

---

## Việc KHÔNG đo được (nói rõ thay vì đoán)

1. **Thời điểm chính xác trong ngày mà giá chạm band** — BQ chỉ có OHLC ngày. Kết luận "executor
   đã tắt khi giá vào band" suy từ (a) giờ sống của executor trong journal và (b) Open cách sàn
   7,03-7,73 %; KHÔNG có tick data để chứng minh trực tiếp.
2. **r15 trên 91 dòng nhánh `adp:twap`** — nhánh này không in `r15=` vào note.
   `_extreme_regime_raw` vẫn gọi `_r15` độc lập (`executor.py:1516`) nhưng không ghi nhật ký khi
   không kích. Con số 49/242 vì vậy là **cận dưới** của số lần trigger (ii) được cấp dữ liệu thật.
3. **Edge bps của fill-timing** — không thuộc phạm vi checkpoint này; hạn chế cũ vẫn nguyên
   (mục C của `execution_quality_review.py` đọc `dnse_raw_*.jsonl` mà PaperBroker không bao giờ ghi).
