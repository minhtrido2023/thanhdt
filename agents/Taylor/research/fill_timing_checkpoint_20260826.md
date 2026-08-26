# Checkpoint `fill_timing` — 5 phiên hybrid ĐÃ ĐỦ (thực đo 2026-08-26)

**Job**: `Taylor_20260826_004005` (dispatch từ Mike qua `paper_checkpoint_escalation.sh`, `end=2026-08-25 < today`)
**Phạm vi**: ĐO + KẾT LUẬN + chuẩn bị đề xuất. KHÔNG flip `fill_timing_live_gate`, không sửa code/config
production, không sửa tay `kb/paper_programs_charter/` (file tự sinh). Chỉ cập nhật
`kb/paper_programs_registry.json`.
**Nguồn**: `data/execution_logs/exec_main_*_journal.csv`, `logs/run_bot_main_2026-08-25*.log`,
`data/trade_plans/plan_main_*.json`, `trading_bot/config.py`, `crontab -l`, BigQuery `tav2_bq.ticker`
+ `tav2_bq.ticker_1m`. Mọi số dưới đây tái lập được từ các nguồn đó.

---

## 1. Thước đo — giữ nguyên phương pháp đã chốt 2026-08-19

- Đếm bằng **TIMESTAMP journal**, KHÔNG string-match nhãn `ft:in-window` (nhãn = `mult==1.0`, không
  phải "nằm trong cửa sổ").
- Thước cho HYBRID = **5 block × 15′** `["11:00","11:15","13:00","13:15","13:30"]` (`config.py:167`),
  KHÔNG phải cửa sổ `10:45-11:15` (đó là cơ chế gom-cửa-sổ tiền-hybrid, `config.py:137-138`).
- Tiêu chí 1 phiên hybrid BUY = hybrid bật (`hyb:` trong note hoặc event `HYBRID_DEFER`) **và**
  ≥1 lệnh MUA `PLACE` rơi trong block đã lên lịch.

**Kiểm chứng phép đo (control leg)**: chạy lại nhánh pre-hybrid `10:45-11:15` trên 4 phiên
07-14/07-16/07-21/07-23 cho **−1,6 bps, sd 97,9, t=−0,03** — tái lập số đã pin ở checkpoint 08-11
(**−1,7 bps, sd 97,8, t=−0,03**). Pipeline đo không bị đổi giữa chừng.

## 2. Bộ đếm phiên hybrid BUY — **6/5, ĐÃ ĐỦ**

| Ngày | Thứ | hybrid | BUY đặt | trong block | số block | trong 10:45-11:15 | BUY khớp | FAIL | Chi tiết |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 2026-08-10 | T2 | no | 6 | 0 | 0 | 0 | 6 | 0 | tiền-hybrid (09:15) — không tính |
| **2026-08-11** | T3 | YES | 4 | **4** | 1 | 4 | 4 | 0 | 11:00×4 |
| 2026-08-12 | T4 | YES | 0 | 0 | 0 | 0 | 0 | 0 | phiên chỉ-BÁN — không tính |
| **2026-08-13** | T5 | YES | 10 | **10** | **2** | 6 | 10 | 0 | 11:00×6 + 11:15×4 |
| **2026-08-17** | T2 | YES | 5 | **5** | 1 | 5 | 5 | 0 | 11:00×5 |
| **2026-08-18** | T3 | YES | 5 | **5** | 1 | 5 | 5 | 0 | 11:00×5 |
| 2026-08-19 | T4 | YES | 0 | 0 | 0 | 0 | 0 | 0 | phiên chỉ-BÁN — không tính |
| **2026-08-20** | T5 | YES | 11 | **11** | **3** | 6 | 11 | 0 | 11:00×6 + 11:15×4 + 13:00×1 |
| 2026-08-21 | T6 | YES | 0 | 0 | 0 | 0 | 0 | 0 | phiên chỉ-BÁN — không tính |
| **2026-08-24** | T2 | YES | 8 | **8** | **2** | 6 | 8 | 0 | 11:00×6 + 11:15×2 |

- **6 phiên hybrid BUY**: 08-11, 08-13, 08-17, 08-18, **08-20 (phiên thứ 5)**, **08-24 (thứ 6)**.
- **Adherence: 43/43 lệnh MUA trong block đã lên lịch (100 %), 43/43 khớp, 0 lệnh ngoài block, 0 FAIL.**
- Cột `trong 10:45-11:15` cho thấy vì sao thước cũ SAI: chỉ 30/43 lệnh nằm trong cửa sổ đó.

### 2.1 `2026-08-25` — vì sao không có phiên (không phải lỗi fill-timing)

`logs/run_bot_main_2026-08-25.log` (cả sáng lẫn chiều): *"[main] không có plan cho 2026-08-25 — bỏ qua"*.
Không có `data/trade_plans/plan_main_2026-08-25.json`; `logs/paper_main_probe_plan.log` mtime dừng ở
**2026-08-24 08:52**. Cron sinh plan chạy 08:52 ICT (`52 1 * * 1-5`, host chạy UTC) rơi trọn vào
**host downtime 2026-08-24 15:30 → 2026-08-25 09:45 ICT**, đã ghi nhận độc lập ở
`kb/incidents/2026-08/2026-08-25-host-downtime-missed-nightly-crons.md` (commit `52eb62ea`).
⇒ 08-25 là **casualty của sự cố hạ tầng đã đóng**, không phải tín hiệu gì về hybrid. Bộ đếm không
phụ thuộc vào nó (đã đủ 5 từ 08-20).

### 2.2 Danh sách ngày "phương án A" vs tiêu chí đo được

Danh sách dự báo (08-11/08-13/08-18/08-20/08-25) có 4/5 ngày thành hiện thực (08-25 mất vì downtime).
Nhưng danh sách ngày là **dự báo lịch cron**, không phải định nghĩa gate — điều này đã được chốt ở
checkpoint 08-19 khi 08-17 (ngoài dự báo) đạt cùng tiêu chí. Theo **tiêu chí thực chất** mà phương án A
nói tới ("chờ đủ 5 phiên hybrid"), bộ đếm là **6/5 — vượt**.

## 3. Block-spreading — n=3 phiên, không còn n=1

Ghi chú 08-19 nói trải block mới thực chứng n=1 (08-13). Nay:

| Ngày | Mã trải nhiều block | Bằng chứng |
|---|---|---|
| 08-13 | ACB/HDB/HPG/MBB (4 mã × 2 block) | `11:00:05` → `11:15:08`, `filled_total=100` mang sang, note `hyb:blk left=4` |
| 08-20 | ACB/HDB/HPG/MBB × 2 block + **MBB × 3 block** | `11:00:09` → `11:15:13` → `13:05:04`, `filled_total` 0→100→200, `left=5→4→3` |
| 08-24 | HPG/MBB × 2 block | `11:00:11` → `11:15:15`, `filled_total=100` |

Bộ đếm block giảm đơn điệu đúng thiết kế; `filled_total` mang sang đúng; không có lệnh nào rơi ngoài
lịch block. **08-20 là ca ĐẦU TIÊN chạm block phiên chiều (13:00)** — trước đó chỉ 2 block sáng.

## 4. Gate 4 (fill vs open) — đo lại RIÊNG cho hybrid

Giá khớp từ journal; `Open` từ BQ. Kiểm `Price/Close` để bắt hệ số điều chỉnh: **tháng 8 = 1,0000
cho cả 6 mã** (so sánh thẳng được); tháng 7 MBB = **1,2003** (cổ tức cổ phiếu) nên nhánh control đã
quy `Open` về giá thô trước khi so — không quy sẽ sai ~2.000 bps cho riêng MBB.

| Ngày | n_fill | day-mean (bps vs open) |
|---|---:|---:|
| 08-11 | 4 | −1,9 |
| 08-13 | 10 | +4,4 |
| 08-17 | 5 | +14,2 |
| 08-18 | 5 | +35,6 |
| 08-20 | 11 | +66,0 |
| 08-24 | 8 | −37,7 |

| | n (ngày = đơn vị độc lập) | mean | sd | se | t |
|---|---:|---:|---:|---:|---:|
| **HYBRID (block)** | 6 | **+13,4 bps** | 35,2 | 14,4 | +0,94 |
| Control: pre-hybrid (10:45-11:15) | 4 | −1,6 bps | 97,9 | 49,0 | −0,03 |
| Hiệu (hybrid − pre) | — | +15,0 bps | — | 51,1 | +0,29 |

**Đọc đúng 3 điều:**
1. **Gate 4 vẫn PASS theo đúng chữ của nó** ("BUY fill không tệ hơn open đáng kể"): +13,4 bps với
   se 14,4 ⇒ không phân biệt được với 0, và **nhỏ hơn 1 bước giá** (tick 50/22.600 = 22 bps).
2. ⚠️ **DẤU NGƯỢC với edge backtest.** Backtest tuyên bố BUY 11:15 **rẻ hơn** open 17,6 bps; hybrid đo
   được **đắt hơn** 13,4 bps. Không có bằng chứng nào ủng hộ edge 17,6 bps trên fill thật; điểm ước lượng
   cách −17,6 bps đúng 2,16 se. **⚠️ CON SỐ ~2σ NÀY MỎNG Ở n=6 — đừng trích riêng nó** (quant-skeptic
   2026-08-26 nêu, Taylor tự tái lập): leave-one-out cho σ chạy từ **1,59** (bỏ 08-18) tới **3,34**
   (bỏ 08-24), mean chạy +2,9…+23,7 bps. Cái BỀN qua mọi tập con là **dấu và độ lớn**: mọi tập con
   leave-one-out đều cho mean DƯƠNG và cách xa −17,6 — không tập con nào đưa edge backtest vào tầm với.
   Cái KHÔNG bền là mức tin cậy chính xác. Kết luận đúng: *"không thấy edge, và dữ liệu nghiêng về
   loại trừ nó"*, KHÔNG phải *"đã loại trừ ở 2σ"*.
   Đây vẫn là **thay đổi so với checkpoint 08-11** (khi se ngày 48,9 bps ⇒ hoàn toàn "không đo được"). Nguyên nhân cơ học
   nhiều khả năng: **31/43** lệnh đi nhánh `adp:dip → cross` (12 lệnh `→passive`) (vượt spread lấy giá chào bán), tức trả nửa
   spread — backtest so mức giá, không mô hình hoá chi phí vượt spread.
3. **Cái hybrid CẢI THIỆN được là PHƯƠNG SAI, không phải trung bình**: sd ngày 35,2 vs 97,9
   (F=7,74, df 3/5 — gợi ý, chưa kết luận ở n này). Đây đúng là điều lý thuyết trải-block hứa hẹn.

## 5. Trạng thái 5 gate

| # | Gate | Trước | Sau | Căn cứ |
|---|---|---|---|---|
| 1 | BUY window adherence | pass | **pass** (mở rộng) | +43/43 lệnh hybrid trong block trên 6 phiên |
| 2 | SELL window adherence | pass | pass | không có dữ liệu lật ngược |
| 3 | 0 rejects/fails | pass | **pass** (mở rộng) | 0 FAIL/ERROR trên **15/15** file journal 07-31→08-24 |
| 4 | fill không tệ hơn open đáng kể | pass | **pass, kèm caveat mới** | +13,4 bps (se 14,4) < 1 tick; nhưng DẤU NGƯỢC edge |
| 5 | quant-skeptic → user sign-off | pending | **điều kiện dữ liệu ĐỦ — chờ quant-skeptic + chữ ký user** | 6/5 phiên; block-spreading n=3 |

## 6. Khuyến nghị

**Điều kiện dữ liệu của phương án A đã thoả.** Bước tiếp theo đúng như next-action đã ghi:
`verify_finding.sh` → quant-skeptic → nếu CONFIRMED thì trình user xin chữ ký.

**Nhưng khuyến nghị của Taylor về NỘI DUNG chữ ký đã đổi so với 08-11**, vì mục 4.2 là dữ liệu mới:

- Cái đã chứng minh được là **CƠ HỌC**: lệnh vào đúng block, khớp 100 %, trải block hoạt động, 0 lỗi.
  Bật live theo nghĩa "cơ chế chạy đúng như thiết kế" là có căn cứ.
- Cái **KHÔNG** chứng minh được, và nay có bằng chứng NGƯỢC, là **LỢI ÍCH GIÁ**: không những không thấy
  edge −17,6 bps, mà khoảng tin cậy hiện tại đã đủ hẹp để loại trừ nó ở ~2σ.
- ⇒ Nếu flip `fill_timing_live_gate`, nên flip với lý do **giảm phương sai thực thi + kỷ luật giờ đặt
  lệnh**, KHÔNG phải "thu edge 17,6 bps". Và nên kèm điều kiện theo dõi: đo lại fill-vs-open sau ~10
  phiên live đầu; nếu mean vượt +22 bps (1 tick) một cách bền thì rollback.
- Nhắc ranh giới đã biết: quy mô probe là 100 cp/mã trên 6 large-cap. Book thật lớn hơn nhiều bậc ⇒
  bằng chứng adherence chuyển giao được, bằng chứng **impact/giá thì KHÔNG**.

**KHÔNG flip live gate ở checkpoint này.**

## 7. Việc KHÔNG đo được (nói rõ thay vì đoán)

1. **Fill vs giá tại đúng thời điểm đặt lệnh** — chỉ có OHLC ngày từ BQ; `probe_ticks_main_*.csv` có
   tick nhưng chưa được dùng làm nguồn chuẩn cho phép đo này (sẽ là thay đổi phương pháp giữa chừng,
   phá control leg mục 1). Vì vậy "+13,4 bps" là vs **open**, không phải vs mid tại thời điểm khớp.
2. **Edge bps mức có ý nghĩa thống kê** — n=6 ngày; se 14,4 bps đủ để loại trừ −17,6 nhưng KHÔNG đủ
   để khẳng định giá trị thật của mean.
3. **Hành vi ở quy mô book thật** — probe 100 cp không tạo impact; không suy ra được gì về
   slippage khi lệnh đủ lớn để ăn nhiều mức giá.
4. **Loại trừ market-direction làm giải thích thay thế cho sign flip** — chưa đo drift trong ngày ở
   cấp từng mã (quant-skeptic đã kiểm sơ ở cấp chỉ số, chưa đủ). Nằm trong danh sách rerun.

---

## 8. Kết quả quant-skeptic (2026-08-26)

**VERDICT: CONFIRMED, confidence MEDIUM** (log `mike/logs/verify_20260826_004642_796886.log`).
Reviewer tự tái lập từ raw journal + BQ pull mới: day-mean `−1,87/+4,4/+14,2/+35,6/+66,0/−37,66`,
`mean=13,44 sd=35,16 se=14,35 t=0,937` — khớp số báo cáo; 43/43 in-block, 0 FAIL trên 15/15 journal,
31/43 `cross` vs 12/43 `passive`, 08-12/08-19/08-21 đúng là phiên chỉ-BÁN (không cherry-pick),
08-10 đúng là tiền-hybrid, 08-25 vắng đúng do host downtime.

**Killer objection (ĐÃ TIẾP THU, xem mục 4.2):** framing "~2,15σ loại trừ edge" mỏng ở n=6.
Taylor tự chạy lại leave-one-out: σ ∈ [1,59; 3,34] (reviewer báo [1,72; 3,34] — min thật là 1,59 khi
bỏ 08-18, tức objection còn mạnh hơn reviewer nêu). Đã sửa cả research doc lẫn `review_short` registry
để không ai trích riêng con số 2σ.

**3 rerun được khuyến nghị** (ghi lại để không rơi):
1. Theo dõi fill-vs-open hàng tuần khi live — báo **khoảng leave-one-out** kèm điểm ước lượng, không chỉ se/t.
2. Kiểm confound market-direction ở **cấp từng mã** (không chỉ cấp chỉ số) cho 6 ngày T8 vs 4 ngày T7.
3. Tái verify độc lập control-leg tháng 7 (−1,6/97,9/−0,03) từ raw journal — reviewer chỉ xác nhận theo
   pin của registry, mà con số này nay gánh vai trò "pipeline không đổi". *(Ghi chú: job này ĐÃ tính lại
   từ raw journal ở mục 1 — nhánh còn thiếu là một người thứ ba làm độc lập.)*
