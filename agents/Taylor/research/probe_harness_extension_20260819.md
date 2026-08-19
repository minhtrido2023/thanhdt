# Harness mở rộng bằng chứng cho gate `extreme_regime` — 2026-08-19

**Job**: `Taylor_20260819_124400` (dispatch từ Mike; user duyệt PHƯƠNG ÁN 2 ngày 2026-08-19,
thread 1521113190405247057)
**Phạm vi**: thay đổi HARNESS (cách chạy/giữ phiên probe + đo tick). **KHÔNG** đổi logic gate,
**KHÔNG** flip `extreme_regime_enabled` ở bất kỳ account nào.
**Tiền đề**: `research/paper_gates_checkpoint_20260819.md` (job `Taylor_20260819_110954`).

---

## 1. Vấn đề cần vá — hai gap CẤU TRÚC, không phải gap thị trường

Checkpoint 08-19 kết luận gate ĐẠT điều kiện định lượng (25/20 phiên evidence, 0 marker) nhưng
bằng chứng **MỘT CHIỀU**, vì hai lý do nằm ở harness chứ không ở thị trường:

| Gap | Số đo (checkpoint 08-19) | Nguyên nhân |
|---|---|---|
| **(A)** trigger (i) cận sàn chưa từng trong tầm với | min headroom **+4,43 %** vs band 3,00 %; **0/242** dòng `PLACE` trong band | 3 phiên (07-15 FPT +2,17 %, 07-20 HPG +0,88 %, 07-22 HDB +1,34 %) giá THỰC SỰ vào band — nhưng executor đã tắt. Kết luận "đã tắt lúc đó" chỉ **suy gián tiếp từ OHLC ngày**, không có dữ liệu tại-thời-điểm. |
| **(B)** trigger (ii) 3-sigma gần như không chạy được | executor sống **trung vị 20 GIÂY**; **20/28** phiên < `dip_window_min` (15′) ⇒ `_r15` = None ⇒ fail-safe False. r15 chỉ đo được **49/242** dòng, âm nhất **−0,90 %** vs ngưỡng lỏng nhất **−2,42 %** | `_r15` cần px_hist tuổi ≥ 0,7 × 15′ ≈ 10,5′. Phiên 20 giây không bao giờ tích đủ. |

Cả hai đều là **giới hạn của dụng cụ đo**, không phải kết luận về gate.

---

## 2. Bản vá

### 2.1 `probe_linger_min` — kéo dài tuổi thọ phiên (vá gap B)

`trading_bot/config.py` DEFAULTS:

```
"probe_linger_min": 30,           # 0 = tắt. 30' > 2,0×dip_window_min ⇒ r15 luôn có mẫu hợp lệ
"probe_linger_live_gate": True,   # True ⇒ chỉ ăn ở account mode == "paper"
"probe_tick_log": True,           # ghi CSV quan sát band-proximity/r15 mỗi chu kỳ sample
```

`trading_bot/executor.py`:

- `Executor.step()` — nhánh `all_done` gọi `_probe_linger_active(now, phase)`. Còn trong cửa sổ ⇒
  lấy mẫu giá rồi **trả `False`** (chưa xong) nên `run_session` lặp tiếp. Nhánh này **KHÔNG gọi**
  `_place_slices` / `_atc_sweep` ⇒ không lệnh nào được đặt thêm.
- `_record_prices()` — khi harness bật, lấy mẫu **cả parent đã `done`** (trước đây `continue`).
  Parent done không bao giờ được `_place_slices` xét tới, nên đây thuần là kéo dài chuỗi quan sát.
- Linger **chỉ chạy trong phiên khớp liên tục** (`MORNING`/`AFTERNOON`). Hai lý do đo được, không
  phải cho gọn: ngoài phiên liên tục giá đứng im ⇒ r15 đọc ra 0 % giả; và cron `pkill` 11:32 dừng
  paper main qua trưa — còn linger lúc đó thì process bị giết giữa chừng và `write_report()`
  không bao giờ chạy.
- Mốc `until` đóng dấu **một lần** vào `state["_probe_linger_until"]` ⇒ không tự gia hạn theo mỗi
  chu kỳ, và bền qua restart giữa phiên.
- Journal ghi `PROBE_LINGER_START` / `PROBE_LINGER_END` để truy được cửa sổ này trong mọi phiên.

### 2.2 `probe_tick_log` — đo band-proximity tại-thời-điểm (vá gap A)

Mỗi chu kỳ sample ghi 1 dòng vào `data/execution_logs/probe_ticks_<account>_<date>.csv`:

```
ts, account, ticker, last, floor, ceiling, ref, headroom_floor, extreme_band, in_band,
r15, rvol_20d, trig_ii_threshold, trig_ii_would_fire, parent_done, linger
```

`headroom_floor = last/floor − 1`, `in_band = (headroom_floor ≤ extreme_band)`,
`trig_ii_threshold = −extreme_move_z × rvol_20d`. Từ đây câu hỏi "giá có vào band lúc executor
còn sống không?" trả lời được **trực tiếp**, hết phải suy từ OHLC ngày.

**THUẦN QUAN SÁT.** Không field nào trong file này được đọc lại bởi `_extreme_regime`,
`_extreme_regime_raw`, `_floor_guard_buy`, `_extreme_slice_mult` hay bất kỳ đường đặt lệnh nào.
`_probe_tick_log` nuốt mọi exception — một dòng log hỏng không được làm hỏng phiên.

### 2.3 An toàn LIVE — hai chốt độc lập

Cùng khuôn `fill_timing_live_gate` / `expected_volume_pacing_live_gate`:

1. **Cổng cấu hình**: `probe_linger_live_gate` đọc bằng `.get(..., True)` ⇒ cấu hình **thiếu
   khoá = paper-only**, không mở toang.
2. **Chốt cứng trong code**: `cfg["mode"]` phải đúng bằng `"paper"`.

Ngoài ra `probe_linger_min` rác/không parse được ⇒ tắt, không raise.

**Không sửa `secrets/trading_bot_accounts.json`** — mặc định nằm ở `DEFAULTS`, cổng LIVE lo phần
phân biệt. (Cũng tránh luôn xung đột với session GDKHQ/VIX đang chạy song song.)

Config hiệu lực đọc lại qua `load_config()` + `load_accounts()` (không đọc file thô):

| account | mode | probe_linger_min | HARNESS | extreme_regime_enabled |
|---|---|---:|---|---|
| main | paper | 30 | **ON** | True |
| ZaloPay | live | 30 | off | False |
| SpaceX | live | 30 | off | False |
| RocketX | live | 30 | off | False |
| ab_cross / ab_dip | paper | 30 | ON | False |

---

## 3. Selfcheck

`probe_linger_selfcheck.py` (mới, 43 ca) + toàn bộ **20 selfcheck phụ thuộc `executor.py`** tra
bằng `bin/selfcheck_scope_map.sh` (executor.py là module lõi dùng chung ⇒ §23 bắt buộc quét rộng).

| Môi trường | Kết quả |
|---|---|
| TZ mặc định | **21/21 file PASS**, 841 assertion |
| `env -u TZ` | **21/21 PASS**, 841 |
| `TZ=America/New_York` | **21/21 PASS**, 841 |

Nhóm ca đáng chú ý trong bộ mới:

- **A (regression)** — `mode=live` ⇒ harness tắt dù `probe_linger_min=30`; phiên vẫn kết thúc
  ngay khi khớp xong; không sinh file tick log. Thiếu khoá `probe_linger_live_gate` ⇒ vẫn
  paper-only. `probe_linger_min=0`/rác ⇒ tắt. Parent done vẫn KHÔNG được lấy mẫu khi harness tắt.
- **B (cơ chế)** — giữ phiên sống, **0 lệnh đặt trong linger**, mốc không tự gia hạn, kết thúc
  đúng mốc, journal có START/END, không linger ngoài phiên liên tục.
- **B′ (gap B)** — sau ~20 giây r15 = `None` (đúng hiện trạng hôm nay); sau 20′ linger
  **r15 tính được** (−1,20 % trên kịch bản trượt mô phỏng), px_hist ≥ 15 điểm.
- **B″ (gap A)** — headroom tính đúng (7,527 % với last=ref, floor=ref×0,93); giá tụt vào band ⇒
  `in_band=1` đo trực tiếp; quote thiếu `floor` ⇒ không raise, headroom rỗng.
- **C (cách ly gate)** — chuỗi `(_extreme_regime, _floor_guard_buy, _extreme_slice_mult)` qua 4
  poll **GIỐNG HỆT** khi bật/tắt harness, trên kịch bản giá khoá sàn (trace không rỗng: gate có
  thật sự kích ở poll 2).

### 3.1 Một lỗi THẬT bộ selfcheck tự bắt được

Vòng chạy dưới `env -u TZ` **FAIL ngay lần đầu** — và hoá ra không phải lỗi TZ: glob dọn state ở
đầu file dùng `exec_{TAG}_*` trong khi mọi ca dùng tag **có hậu tố** (`selfcheck-probe-r15`…), nên
state cũ sống sót; `px_hist` cũ (mốc 09:50) làm `_record_prices` thấy mẫu "mới hơn `now`" ⇒ bỏ qua
mọi chu kỳ ⇒ không dòng tick log nào. Đã sửa glob thành `{TAG}*`; chạy **hai lần liên tiếp** vẫn
PASS (đúng cái bẫy `extreme_regime_selfcheck.py` đã cảnh báo trong comment TAG của nó).

---

## 4. Deadline + chính sách go-live đã chốt trong registry

`kb/paper_programs_registry.json` → `extreme_regime`, charter regen bằng `sync_charter()`
(không sửa tay `kb/paper_programs_charter/extreme_regime.md`).

- **DEADLINE REVIEW: 2026-08-25 16:00 ICT** — thay hẳn kiểu kết thúc mở/event-anchored.
- Field `end` = **2026-08-24** cố ý: `bin/paper_checkpoint_escalation.sh` so `end < today`, nên
  08-24 làm checker tự fire **đúng ngày 2026-08-25** (cron 16:10 ICT). Đặt 08-25 sẽ fire 08-26 =
  trễ deadline 1 ngày. Verify bằng mô phỏng 3 ngày: 08-19 → không fire; **08-25 → fire
  `extreme_regime`**; 08-26 → fire thêm `fill_timing` (mốc riêng của nó).
- **Chính sách go-live (user chốt)**: gate là **BẢO HIỂM, không phải alpha** ⇒ **không cần chờ sự
  kiện sập THẬT**; thiếu sự kiện sập thật **không phải blocker**. Tại deadline, khuyến nghị
  go-live nếu đủ **6** điều kiện: (1) gate ARMED paper main; (2) ZERO false-trigger trên tổng
  phiên evidence **tính cả các phiên probe dài mới**; (3) stress-injection 24/24 PASS; (4) **cả
  hai** trigger structural reachable **và đo được** (r15 có dữ liệu thật; band-proximity đo trực
  tiếp); (5) selfcheck pass; (6) quant-skeptic sign-off.
- Gate 4 vẫn **pending** — Taylor không tự bật live.

---

## 5. Cái này KHÔNG làm được (nói rõ thay vì đoán)

1. **Không tạo ra sự kiện sập.** Harness chỉ đảm bảo *nếu* giá vào band / r15 thủng ngưỡng trong
   giờ probe thì ta **đo được**; nó không làm điều đó xảy ra. Xác suất quan sát tăng vì cửa sổ
   sống dài hơn ~90× (20 giây → 30 phút), không vì thị trường đổi.
2. **Vẫn chỉ 6 mã large-cap** trong rổ probe (`paper_main_probe_plan.py`) — nhóm ít khi chạm sàn
   nhất. Mở rộng rổ sang mã biến động cao là thay đổi KHÁC, chưa làm, chưa xin.
3. **T3/T5 linger bị cắt bởi `pkill` 11:32** nếu phiên khớp xong sát trưa (lịch HYBRID đặt lệnh
   11:00/11:15). Ngày đó cửa sổ linger ngắn hơn 30′ — không mất dữ liệu đã ghi, chỉ ngắn hơn.
4. **`_r15` trên nhánh `adp:twap`** vẫn không in vào note journal (hạn chế cũ, ngoài phạm vi) —
   nhưng từ nay `probe_ticks_*.csv` ghi r15 **mọi chu kỳ sample**, độc lập với nhánh đặt lệnh, nên
   con số 49/242 cũ hết là cận dưới mù.

---

## 6. File thay đổi

| File | Thay đổi |
|---|---|
| `trading_bot/config.py` | +3 khoá DEFAULTS + khối comment lý do (số đo gap A/B) |
| `trading_bot/executor.py` | `probe_tick_file` trong `__init__`; `_record_prices` honour linger + gọi tick log; 3 hàm mới `_probe_linger_on` / `_probe_linger_active` / `_probe_tick_log`; nhánh linger trong `step()` |
| `probe_linger_selfcheck.py` | MỚI — 43 ca |
| `mike/kb/paper_programs_registry.json` | `extreme_regime`: end/end_or_trigger/gate 4/notes/review_short/data_sources |
| `mike/kb/paper_programs_charter/extreme_regime.md` | regen bằng `sync_charter()` |
