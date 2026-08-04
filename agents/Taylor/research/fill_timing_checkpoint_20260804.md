# Checkpoint paper-program `fill_timing` — 2026-08-04

**Job**: `Taylor_20260804_091703` · **Owner**: Taylor · **Nguồn**: charter
`mike/kb/paper_programs_charter/fill_timing.md` + registry entry `fill_timing`.

**Kết luận 1 dòng**: 2/5 gate PASS. Không đủ điều kiện chuyển bước, và lý do KHÔNG phải "cần thêm
thời gian" — mà là **evidence đã ngừng tích lũy từ 2026-07-28** vì netting triệt tiêu 100% lệnh của
probe harness. Gỡ blocker + 1 phiên BUY-window nữa là đủ mechanics.

---

## 1. Dữ liệu đã đo (không suy đoán)

Nguồn: `data/execution_logs/exec_main_*_journal.csv` (18 file, 2026-07-07 → 2026-08-04),
`data/bq_cache` (day-open), `mike/logs/run_bot_main_*.log`, `trading_bot/executor.py`,
`trading_bot/brokers.py`, crontab.

Tổng journal paper `main`: 906 dòng — 155 PLACE (đều có `ft:` note), 155 FILL, 153 DONE,
386 PLACE_FAIL, 45 ATC_FAIL, 12 GHOST_ORDER.

### Cadence theo thiết kế (crontab)
| Cron | Ngày | Giờ ICT | Mục đích khai báo |
|---|---|---|---|
| `10 2 * * 1,3,5` | T2/T4/T6 | 09:10 | SELL-window evidence (09:15-09:45) |
| `46 3 * * 2,4` | T3/T5 | 10:46 | BUY-window evidence (10:45-11:15) |

⇒ **Mỗi phiên chỉ đo được MỘT phía**. Số gộp "in-window 54%" mà probe in ra hằng ngày trộn cả 2
phía qua mọi phiên nên **vô nghĩa** — phải tách theo phiên × phía.

### Adherence tách đúng theo phiên × phía
| Phía | Phiên đúng thiết kế | Placement | In-window |
|---|---|---|---|
| SELL @09:15 | 9 (07-10,13,15,17,20,22,24,27,31) | 50 | **50/50 = 100%** |
| BUY @10:46 | 4 (07-14,16,21,23) | 24 | **24/24 = 100%** |
| BUY @14:19 (07-07, phiên chiều) | 1 | 6 | 6/6 (rule `t>=13:00 → mult=1.0`, KHÔNG phải cửa sổ 10:45-11:15) |

0 lệnh nào lọt ra ngoài cửa sổ của phiên nó thuộc về mà không giải thích được.

### Lỗi / reject
- 431 sự kiện lỗi (386 PLACE_FAIL + 45 ATC_FAIL) **toàn bộ ngày 2026-07-30**, **1 root cause duy
  nhất**: `PaperBroker.place_order() got an unexpected keyword argument 'cash_only'`. Đã fix +
  verify cùng ngày — `kb/incidents/2026-07/2026-07-30-paper-trading-report-3-root-causes.md`.
- 12 GHOST_ORDER (07-08, 07-09): `PaperBroker.poll_orders()` trả lệnh all-time → ghost guard tưởng
  lệnh hôm qua là ghost. Đã fix bằng day-scope filter (`brokers.py`, comment tại chỗ).
- **0 reject từ broker.**

### Fill vs day-open (154/155 FILL khớp được day-open từ `bq_cache`)
Tính **theo PHIÊN** (sự kiện độc lập), không theo dòng fill — 6 mã cùng phiên tương quan cao,
khai n=80 là sai kỷ luật §18/`quant-research`.

| Phía × cửa sổ | N_phiên | mean bps vs open | t |
|---|---|---|---|
| BUY trong 10:46 | 5 | **+26.1** (TRÊN open — dấu **ngược** giả thuyết) | +0.56 |
| SELL trong 09:15 | 9 | **−8.5** (dưới open) | −4.49 |
| BUY tại 09:15 | 10 | +14.0 | +2.64 |
| SELL tại 10:46 | 4 | −22.2 | −0.46 |

Đọc đúng: cùng phiên 09:15, BUY **+14.0** / SELL **−8.5** ⇒ chênh ~22.5 bps = **spread bid/ask**,
không phải hiệu ứng timing. Cái t=−4.49 của SELL chỉ là "bán ở bid", không phải bằng chứng edge.
BUY trong cửa sổ mục tiêu có dấu **bất lợi** (+26.1 bps đắt hơn open) nhưng t=0.56 ⇒ không phân
biệt được với nhiễu, đúng như charter cảnh báo (std phiên đo được ~100 bps).

---

## 2. Hai vấn đề CẤU TRÚC (quan trọng hơn các con số trên)

### (A) BLOCKER — evidence đã chết từ 2026-07-28
Netting được wire vào production ngày **2026-07-27** (commit `ab20a77`, "Wire netting
(net_offsetting_orders) + post-fill reconciliation LIVE into bot_execute.py").

Probe plan (`mike/bin/paper_main_probe_plan.py`) theo thiết kế là **churn**: bán sạch 6 mã đang giữ
rồi mua lại **đúng 6 mã đó**. Netting nhìn thấy mua = bán trên cùng mã ⇒ gộp thành chuyển nội bộ:

```
[main] ⟲ NET ACB (INTERNAL_ONLY): mua 1,300 = bán 1,300 → 0 lệnh ra broker …
[main] plan 2026-07-28 không có lệnh — bỏ qua
```

Từ 07-28 tới nay **0 lệnh ra broker**, trừ 1 lệnh dư 100cp MBB ngày 08-04 do làm tròn. Journal
07-28 / 07-29 / 08-03 **không tồn tại**; 07-30 là ngày 431 lỗi; 07-31 chỉ 2 lệnh SELL.

⇒ Con số adherence 155 placement hiển thị mỗi ngày là **số đóng băng tới 2026-07-27**, không phải
evidence mới. Cùng harness ⇒ 2 chương trình paper khác (`extreme_regime`, `vol_scale_chase_cap`)
cũng đang đói evidence dù report gắn badge ✅.

### (B) Harness không thể chứng minh cơ chế fill-timing, chỉ chứng minh cron đúng giờ
- `_fill_timing_mult()` (`executor.py:873-906`) **chỉ nhân interval GIỮA các slice**
  (`executor.py:1009`). Nó không chặn/hoãn việc đặt lệnh.
- Ghi nhận thực tế: **151/153 lệnh cha khớp trong 1 slice duy nhất** ⇒ không có slice thứ hai ⇒
  multiplier **không bao giờ ràng buộc**.
- `ft:in-window` / `ft:out×4` (`executor.py:1106-1108`) là hàm **thuần** của wall-clock lúc đặt
  lệnh ⇒ nhãn giờ cron nổ, không phải bằng chứng cơ chế hoạt động.
- `PaperBroker._try_fill()` khớp **100% qty ngay poll đầu tại đúng ask/bid**, 0 slippage / 0 queue
  / 0 market impact (155/155 fill = đúng giá đặt) ⇒ cột "fill vs open" đo **trôi giá theo giờ**,
  không phải chất lượng khớp lệnh.

**Hệ quả cho quyết định**: bằng chứng bps qua harness này là bất khả thi trong thời gian hợp lý.
Để tách edge 17.6 bps khỏi nhiễu phiên ~100 bps ở t=2 cần n ≈ (2×100/17.6)² ≈ **130 phiên
BUY-window** ≈ **65 tuần** ở cadence 2 phiên/tuần — và kể cả đủ n thì vẫn không phải bằng chứng
khớp lệnh vì PaperBroker khớp tại limit. Điều này khớp với decision rule gốc 30-06 ghi ngay trong
`execution_quality_review.py`: *"apply if MECHANICS clean … Edge validates post-go-live."*

---

## 3. Trạng thái 5 gate (đã ghi vào registry)

| # | Tiêu chí | Status | Căn cứ |
|---|---|---|---|
| 1 | BUY window adherence | ⏳ **pending** | 4/5 phiên (review_short yêu cầu ≥5); 24/24 in-window trên 4 phiên đó; accrual đã dừng |
| 2 | SELL window adherence | ✅ **pass** | 9 phiên, 50/50 in-window |
| 3 | 0 reject/fail hoặc giải thích được | ✅ **pass** | 431 lỗi = 1 ngày 1 root cause đã fix; 12 GHOST đã fix; 0 reject broker |
| 4 | Fill không tệ hơn open đáng kể | ⏳ **pending** | N=5 phiên BUY, +26.1 bps t=0.56 — không kết luận được cả 2 chiều |
| 5 | quant-skeptic → user sign-off | ⏳ **pending** | bị chặn bởi #1 và #4 |

---

## 4. Khuyến nghị (KHÔNG tự bật live — chờ user quyết)

1. **Gỡ blocker netting cho probe harness** (việc code, ~1 lần dispatch): sửa
   `paper_main_probe_plan.py` để basket MUA ≠ basket BÁN (vd bán 6 mã đang giữ, mua 6 mã khác
   trong danh sách thanh khoản cao, xoay vòng), **hoặc** miễn netting cho account `mode=paper`.
   Ưu tiên phương án 1 — giữ nguyên đường code production của netting.
   → Việc này cũng khôi phục evidence cho `extreme_regime` + `vol_scale_chase_cap`.
2. **Sau 1 phiên BUY-window (T3 hoặc T5)** → gate #1 đạt 5/5 → **mechanics đủ**. Ước ~1 tuần.
3. **Quyết theo MECHANICS, không chờ bps** — đúng decision rule 30-06. Gate #4 nên đổi cách phát
   biểu: từ "chứng minh không tệ hơn open" (bất khả thi ở N này) sang "không có dấu hiệu tệ hơn
   open vượt nhiễu" — hiện tại đúng là không có.
4. **Rồi mới** quant-skeptic → user sign-off → flip `fill_timing_live_gate=false`.
5. **Sửa số hiển thị hằng ngày**: `execution_quality_review.py` mục A nên tách BUY/SELL theo phiên
   thay vì gộp 1 tỷ lệ 54% — tỷ lệ gộp hiện tại vô nghĩa và dễ đọc nhầm thành "adherence kém".

**Không có thay đổi production nào trong job này.** Chỉ cập nhật registry + charter (tự sinh).
