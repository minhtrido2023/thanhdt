# Checkpoint paper-program `extreme_regime` (EXTREME-regime gate) — kiểm bằng dữ liệu thật

- **Job**: `Taylor_20260804_124404` (VIỆC 2) · **Ngày**: 2026-08-04 · **Owner**: Taylor
- **Chương trình**: gate phòng thủ intraday — arm 2-poll · sell-to-floor · buy-pause · cadence ×0.25
- **Kết luận 1 dòng**: **CHƯA đủ điều kiện chuyển bước** — thiếu **5 phiên evidence** (15/20) và
  **3 phiên nữa cần loại** khỏi nhánh trigger (ii) vì lỗi M5. **KHÔNG flip live trong job này.**
- Không đổi production. `git diff` chỉ chạm `mike/kb/paper_programs_registry.json` + file báo cáo này.

---

## 1. Tiến độ evidence — 15/20, CHƯA đủ

Đếm bằng chính hàm production `count_evidence_sessions('main','2026-07-07')`
(`mike/bin/paper_programs_daily_report.py`), không đếm tay:

| | |
|---|---|
| Mục tiêu registry | **20 phiên** evidence, đếm từ 2026-07-07 |
| Thực tế | **15 phiên**: 07-07, 07-10, 07-13→07-17, 07-20→07-24, 07-27, 07-31, 08-04 |
| Còn thiếu | **5 phiên** |

**Chất lượng 15 phiên đó không đồng đều** — chi tiết quan trọng cho việc đọc "zero false-trigger":

| Nhóm | Phiên | Nội dung |
|---|---|---|
| Đầy đủ (BUY+SELL cả rổ 6 mã) | 13 phiên 07-07→07-27 | cả buy-path (PAUSE/FLOOR_GUARD) lẫn sell-path đều được đánh giá |
| **Chỉ SELL** (dư netting) | 07-31 (HPG,VNM), 08-04 (MBB) | **buy-path KHÔNG được đánh giá** — 1-2 lệnh/phiên |
| Không tính (đúng) | 07-08, 07-09 (chỉ GHOST_ORDER), 07-30 | — |

**07-30 là 1 phiên MẤT HẲN**: 386 `PLACE_FAIL` + 45 `ATC_FAIL`, lỗi
`PaperBroker.place_order() got an unexpected keyword argument 'cash_only'`. Đã fix (commit
`2af4abd`), không tái diễn từ 07-31.

**Luồng evidence từng đứng 8 ngày** (07-28→08-04) do bug netting nội bộ của probe harness — **đã
gỡ sáng nay** (job `Taylor_20260804_094514`, commit mike `d59bdf9c` + selfcheck 6/6). Evidence chạy
lại **từ phiên 2026-08-05** ⇒ đủ 20 phiên vào khoảng **2026-08-11** (5 phiên T2-T6, nếu không nghỉ lễ).

## 2. Marker EXTREME đã bắn: **0 / 15 phiên** (quét toàn bộ 18 file journal)

Quét mọi dòng chứa chuỗi `EXTREME` ở CẢ cột `event` lẫn `note`, 18/18 file
`exec_main_*_journal.csv`: **0 hit**. Không có 1 lần arm nào.

### ⚠️ Lỗi thật trong registry: danh sách `probe.markers` KHÔNG khớp code

Registry đang khai `["EXTREME_PAUSE","EXTREME_SELL","EXTREME_DOWN","EXTREME_UP"]`. Đối chiếu
`grep -o '_journal("[A-Z_]*"' trading_bot/executor.py` — **executor chỉ phát ra 2 marker EXTREME**:

| Marker registry | Có thật trong code? |
|---|---|
| `EXTREME_PAUSE` | ✅ `executor.py:1020` (buy-pause) |
| `EXTREME_SELL` | ❌ **không tồn tại** — chỉ có trong fixture `mike/bin/paper_report_render_selfcheck.py` |
| `EXTREME_UP` | ❌ **không tồn tại** ở đâu cả |
| `EXTREME_DOWN` | ❌ không phải tên event; chỉ khớp *tình cờ* qua chuỗi trong `note` |
| **`EXTREME_FLOOR_GUARD`** | ✅ `executor.py:1026` — **THIẾU trong registry** |

Hệ quả cụ thể: `probe_journal_scan` quét bằng `if m in line`, nên nếu
**`EXTREME_FLOOR_GUARD` bắn thật thì báo cáo paper hằng ngày sẽ KHÔNG thấy** (dòng đó không chứa
chuỗi nào trong 4 marker đang khai). Đây đúng là marker được thêm để bịt lỗ hổng PNJ — tức là cái
đáng theo dõi nhất lại đang vô hình. Sell-to-floor thì may mắn vẫn thấy được vì `note` của PLACE
chứa chuỗi `EXTREME_DOWN sell-to-floor` (`executor.py:1032` → `:1109-1112`).

→ **Đã sửa `probe.markers` trong registry** thành 3 chuỗi khớp code thật:
`EXTREME_PAUSE`, `EXTREME_FLOOR_GUARD`, `EXTREME_DOWN sell-to-floor`.
(Kết luận "0 marker" ở trên **không** dựa vào danh sách này — tôi quét thẳng chuỗi `EXTREME`.)

## 3. Câu hỏi M5 (audit `Winston_20260712_142100`) — **giải được, KHÔNG phải loại sạch**

**Sự việc**: `data/bq_cache/ticker_prune.parquet` (monolith) đóng băng **2026-06-26**;
`Executor._load_gap_ref_data` đọc thẳng file này ⇒ `rvol_20d`/`prior_close` tính trên giá cũ.
Winston fix tối **2026-07-13** (commit `1630916`, chuyển sang chunked dir); Taylor xác nhận độc lập
cùng ngày (job `Taylor_20260713_075836`).

**Phân giải theo TỪNG nhánh trigger** (đây là chỗ audit gốc không tách):

| Thành phần | Nguồn dữ liệu | M5 ảnh hưởng? |
|---|---|---|
| Trigger (i) cận sàn — `last ≤ floor×(1+3%)` | **chỉ quote sống** (`q.floor`, `q.last`) | ❌ **KHÔNG** |
| `_floor_guard_buy` (bịt lỗ hổng PNJ) | **chỉ quote sống** | ❌ **KHÔNG** |
| Trigger (ii) 3-sigma — `r15 < −z×rvol_20d` | `_gap_ref.rvol_20d` ← parquet | ✅ **CÓ**, 3 phiên |

Phiên dính: **07-07, 07-10, 07-13** (07-14 trở đi đã đọc dữ liệu tươi).

**Đo mức lệch thật** (dựng lại đúng công thức `_load_gap_ref_data`: `tail(22)` → `pct_change` →
`std` của 20 return; STALE = dữ liệu chốt 06-26):

| Phiên | Ticker-session mà rvol STALE **thấp hơn** thật (⇒ ngưỡng CHẶT hơn, gate **NHẠY hơn**) |
|---|---|
| 07-07 | VNM (−27,9%) |
| 07-10 | MBB (−7,7%), VNM (−26,3%) |
| 07-13 | MBB (−7,5%), VNM (−33,6%) |

→ **5/18 ticker-session** gate nhạy hơn thực tế (ngưỡng VNM −1,78% thay vì −2,69%) — mà **vẫn
không bắn** ⇒ với 5 ca này, bằng chứng "zero false-trigger" **mạnh hơn** thực tế, không yếu đi.
**13/18 ticker-session** còn lại rvol STALE **cao hơn** (tới +58,6% với ACB 07-10) ⇒ ngưỡng LỎNG
hơn ⇒ "không bắn" là bằng chứng **yếu hơn** (rủi ro false-**negative**, không phải false-positive).

**Kết luận M5**: evidence 3 phiên đó **không vô giá trị**, nhưng **không dùng được cho nhánh
trigger (ii)**. Đề nghị đếm bảo thủ:

| Nhánh | Phiên sạch dùng được |
|---|---|
| Trigger (i) cận sàn + `_floor_guard_buy` | **15/20** |
| Trigger (ii) 3-sigma | **12/20** (loại 07-07, 07-10, 07-13) |

⚠️ Không tái dựng được `r15` intraday từ dữ liệu ngày, nên **không** kiểm được "liệu có phiên nào
suýt bắn" — chỉ khẳng định được ngưỡng đã lệch bao nhiêu.

## 4. Quan sát của user về case PNJ — **KHÔNG xác nhận được** (bằng chứng nói ngược lại)

User nêu: *"thấy hiệu quả cho case PNJ"*. Kiểm bằng bằng chứng có sẵn:

1. **PNJ chưa bao giờ nằm trong rổ probe paper main.** 18/18 journal chỉ có
   ACB/FPT/HDB/HPG/MBB/VNM. **0 dòng PNJ**, **0 marker EXTREME**.
2. **Case-study PNJ đã làm rồi** (job `Taylor_20260713_075836`, bus 2026-07-13T08:07:15Z) và kết
   luận **ngược với quan sát của user**: PNJ sàn cứng 3 phiên (07-03 −6,97% / 07-06 −6,98% /
   07-07 −6,96%), nhưng hệ thống **không mua PNJ nhờ VÒNG CHỌN MÃ**, không phải nhờ gate — cả 4
   nguồn đều loại PNJ *trước khi* gate có cơ hội làm gì (BAL ta-score 16-46 << ngưỡng 95/155/140;
   LAG không có earnings event; custom30V rổ 05-05 không có PNJ; DC book 9 mã không có PNJ).
   Grep toàn bộ trade plan 07-06→07-13 cả 3 account: **0 lần PNJ**.
3. **Replay giả định còn lộ ra gate THẤT BẠI ở case này**: nếu PNJ có lọt danh sách mua thì
   2-poll confirm khiến **slice đầu vẫn khớp tại giá sàn** trước khi gate arm — và ở NAV ~1B, lệnh
   điển hình 30-100tr < `max_child_value` 200tr nên slice đầu = **toàn bộ lệnh**.
4. **Điều PNJ thực sự mang lại**: nó **phát hiện lỗ hổng poll-1** → sinh ra `_floor_guard_buy`
   (stateless, chặn chiều MUA ngay poll 1, commit `74f5daa`, stress 40/40 PASS,
   job `Taylor_20260713_082159`).

**Nói thẳng**: PNJ **không phải bằng chứng gate hiệu quả** — nó là bằng chứng **vòng chọn mã** hiệu
quả, cộng với một **lỗ hổng của gate** được PNJ phơi ra rồi mới vá. Giá trị của case là có thật,
nhưng nằm ở chỗ khác với chỗ user nghĩ, và phần vá đó **chưa từng được kiểm chứng trên thị trường
thật** (0 lần `EXTREME_FLOOR_GUARD` bắn trong 15 phiên, vì rổ probe toàn large-cap không bao giờ
lại gần sàn).

## 5. Trạng thái 4 gate

| # | Tiêu chí | Trạng thái | Căn cứ |
|---|---|---|---|
| 1 | Stress-injection 24/24 (nay 40/40) | **PASS** | `stress_extreme_regime.py`, đã đính chính số đếm 07-13 |
| 2 | ZERO false-trigger qua ~4 tuần benign | **PENDING** | 0/15 marker nhưng **15/20** phiên (trigger ii chỉ **12/20**) |
| 3 | Không can thiệp NORMAL-path | **PASS** | 0 marker/15 phiên ⇒ 0 lần can thiệp; gate + guard đều nằm sau `extreme_regime_enabled`; section 6g của stress resolve cfg THẬT của SpaceX/ZaloPay chứng minh live không kích |
| 4 | User sign-off | **PENDING** | chờ user + Mike đọc báo cáo này |

## 6. Còn thiếu gì cụ thể để chuyển bước

1. **5 phiên evidence nữa** — từ 08-05, ước đủ ~**2026-08-11**.
2. **3 phiên bù cho trigger (ii)** nếu muốn giữ chuẩn 20 phiên sạch cho CẢ 2 nhánh → ước
   **~2026-08-14**.
3. **Thừa nhận giới hạn phạm vi, không vá được bằng cách chờ**: rổ probe là 6 large-cap thanh
   khoản cao, **chưa bao giờ tới gần sàn**. "Zero false-trigger" ở đây = *gate không kêu bậy trong
   điều kiện lành tính trên large-cap*, **không phải** *gate xử lý đúng khi thị trường sập* — nhánh
   sau chỉ có bằng chứng từ stress harness + backtest, giống hệt tình huống gate 4 của
   `vol_scale_chase_cap`. Nếu user muốn bằng chứng cho nhánh sau thì chờ thêm trên paper **không**
   giải quyết được; phải thêm 1 mã biến động mạnh vào rổ probe (đổi thiết kế probe) hoặc chấp nhận
   re-scope như đã làm với chase-cap.

## 7. Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude
# đếm phiên evidence bằng hàm production
/home/trido/thanhdt/wc_venv/bin/python -c "import sys;sys.path.insert(0,'mike/bin');\
from paper_programs_daily_report import count_evidence_sessions as c;print(c('main','2026-07-07'))"
# quét marker EXTREME toàn bộ journal
grep -c EXTREME data/execution_logs/exec_main_*_journal.csv
# marker nào executor THỰC SỰ phát ra
grep -o '_journal("[A-Z_]*"' trading_bot/executor.py | sort -u
```

Nguồn: `data/execution_logs/exec_main_*_journal.csv` (18 file) · `trading_bot/executor.py:908-1035,
1109-1112` · `data/bq_cache/ticker_prune/*.parquet` · `mike/bin/paper_programs_daily_report.py:67-83,
195-226` · bus `Taylor_20260713_075836` / `Taylor_20260713_082159` / `Winston_20260713_143546` /
`Taylor_20260804_094514`.
