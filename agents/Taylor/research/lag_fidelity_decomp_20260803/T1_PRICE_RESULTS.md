# T1-price — THANG CAPACITY chạy lại ở `LAG_ADV_BASIS=price` (ghép số cho pin chính thức 28,86%)

**Job:** `Taylor_20260803_052705` · 2026-08-03 · Harness `run_rung_price.sh` · Engine
`pt_v23_lagcap_research.py` (khác production **đúng 1 dòng đã ghi chú**).
Snapshot `bq_cache_asof20260729_postrestate`, NAV 50B, `threads=1`, `$DNA_PYEXE`.
**Khác T1 gốc ĐÚNG MỘT biến:** `LAG_ADV_BASIS` `close` → `price`.

> **Phạm vi (đọc trước):** đây **KHÔNG** phải phép thử mới, **KHÔNG** đề xuất re-pin, **KHÔNG**
> tuyên bố CONFIRMED gì mới. Toàn bộ T1/T2/T3 + bridge chạy ở cơ sở ADV `close` nên chân đối chứng
> của chúng là **27,24%**, trong khi pin chính thức từ 2026-08-03 là **28,86%** (cơ sở `price` =
> mặc định production từ commit `0062aa0`). Kết luận về **HƯỚNG** không phụ thuộc cơ sở giá; **số
> tuyệt đối** thì có. Việc duy nhất ở đây là ghép lại thang cho đúng cơ sở của số pin.

## 1. Điều kiện hợp lệ — ĐẠT (chặt hơn T1 gốc: khớp ở CẢ HAI chân)

| Chân | Kỳ vọng (A/B 08-02, engine **production**) | Thực đo (bản sao nghiên cứu) | Khớp |
|---|---|---|---|
| `pct=0,20` / **L0** = pin R3 hiện hành | 28,86% · 1,90 · −17,8% · 1,62 · **1.178,01B** | 28,86% · 1,90 · −17,8% · 1,62 · **1.178,01B** | ✅ từng chữ số |
| `pct=0,20` / **L1** (= `L3_both`) | 32,71% · 1,95 · −19,1% · 1,71 · **1.699,09B** | 32,71% · 1,95 · −19,1% · 1,71 · **1.699,09B** | ✅ từng chữ số |

⇒ bản sao nghiên cứu tái lập **cả chân control lẫn chân treat** của A/B production ⇒ thang đọc được.
Không tái lập ⇒ toàn bộ bảng dưới vô hiệu (điều kiện đăng ký trước trong header `run_rung_price.sh`).

**Self-check 0 VND:** cả 6 chân in `[selfcheck BAL]` và `[selfcheck LAG]`
`cash-flow identity max err = 0 VND; final NAV identity err = 0 VND`. `EXIT=0` cả 6.

## 2. Thang — cơ sở `price` (số ghép được với pin 28,86%)

| `%ADV/ngày` | L0 (control) | L1 (`LIQ_ZERO_BLOCK=lag`) | **Δ CAGR** | Δ NAV cuối |
|---|---|---|---|---|
| **0,05** (chặt 4x) | 26,51% (936,26B) | 29,18% (1.214,61B) | **+2,67pp** | +278,4B |
| **0,20** (gốc = production) | **28,86%** (1.178,01B) | 32,71% (1.699,09B) | **+3,85pp** | +521,1B |
| **1,00** (lỏng 5x) | 28,68% (1.157,88B) | 34,24% (1.960,73B) | **+5,56pp** | +802,9B |

**Chỉ số phụ:** Sharpe L0 1,80 / 1,90 / 1,83 — L1 1,85 / 1,95 / 1,98 · MaxDD L0 −18,1% / −17,8% /
−18,0% — L1 −18,2% / **−19,1%** / **−20,0%** · Calmar L0 1,47 / 1,62 / 1,60 — L1 1,61 / 1,71 / 1,71.

**Đối chiếu với thang cơ sở `close` (T1 gốc):**

| `%ADV/ngày` | Δ ở cơ sở `close` | Δ ở cơ sở `price` | Lệch |
|---|---|---|---|
| 0,05 | +2,51pp | +2,67pp | +0,16 |
| 0,20 | +4,08pp | +3,85pp | −0,23 |
| 1,00 | +5,20pp | +5,56pp | +0,36 |

⇒ **HƯỚNG và HÌNH DẠNG thang giữ nguyên hoàn toàn** (Δ tăng đơn điệu khi nới capacity, ở cả hai cơ
sở giá). Kết luận T1 — **H_B bị bác bởi sai DẤU đạo hàm** — **không** phụ thuộc cơ sở giá. Đúng như
T5 đã dự báo trước khi chạy.

## 3. Manipulation check (bắt buộc, đăng ký trước)

Tỷ lệ vị thế LAG bỏ dở (`ABANDONED_REFUND`), đếm lại từ chính CSV audit của mỗi chân
(`record_type=TX`, `book=LAG`, gộp theo `holding_id`):

| `%ADV/ngày` | L0 abandoned% (n vị thế) | L1 abandoned% (n) |
|---|---|---|
| 0,05 | 54,9% (2.324) | 71,4% (2.687) |
| 0,20 | 44,9% (1.901) | 58,8% (2.390) |
| 1,00 | **31,0%** (1.478) | **42,8%** (1.864) |

**Phán quyết: CÓ ăn, nhưng CHỈ MỘT PHẦN — y hệt cơ sở `close`.**
- ✅ Đơn điệu hoàn hảo đúng chiều ở **cả hai** chân (L0 −23,9pp, L1 −28,6pp khi nới 20x) ⇒ knob tác
  động đúng vào ràng buộc capacity ⇒ **phép thử không vô hiệu**.
- ⚠️ **KHÔNG đạt ngưỡng "<~20%"** đã đăng ký cho trạng thái "capacity hết ràng buộc" (còn
  31,0%/42,8% ở rung lỏng) — phần dư do `max_fill_days=5` + `min_fill_pct` + mã ADV thật sự bé. ⇒
  chỉ dùng **CHIỀU của đạo hàm**, không dùng giá trị tuyệt đối ở đầu lỏng.

## 4. Phải nói thẳng — một nghịch đảo MỚI ở chân L0 (không có ở cơ sở `close`)

Chân **L0** ở cơ sở `price` **không đơn điệu**: 26,51% → **28,86%** → 28,68% (rung lỏng 1,00 **thấp
hơn** rung gốc 0,20 đúng **−0,18pp**). Ở cơ sở `close` chân L0 đơn điệu tăng (24,31 → 27,24 →
28,78).

- **Không** ảnh hưởng kết luận về DẤU: Δ (L1−L0) vẫn **đơn điệu tăng trên cả ba rung ở cả hai cơ
  sở**, và ở đây nghịch đảo L0 còn *làm Δ tăng*, tức đi ngược hướng có lợi cho H_B.
- **Nhưng** nó là chỉ báo nhiễu ở đầu lỏng: nới trần fill 5x mà tổng thể *xấu đi* một chút nghĩa là
  fill nhanh hơn không đơn thuần tốt (vào lệnh sớm hơn ở giá xấu hơn). Theo kỷ luật đăng ký trước
  (skill §10, "thang không đơn điệu ⇒ hạ độ tin cậy một bậc"), **hạ một bậc độ tin cậy cho giá trị
  tuyệt đối ở rung 1,00** — vốn đã không được dùng để kết luận gì.
- **Cảnh báo vận hành lặp lại:** MaxDD của L1 **xấu hơn** L0 ở rung 0,20 (−19,1% vs −17,8%) và
  1,00 (−20,0% vs −18,0%). Đồng nhất với cảnh báo T2. Lợi ích của bộ lọc **đi kèm rủi ro rút vốn
  cao hơn**, không phải bữa trưa miễn phí.

## 5. Ghép hai thiên lệch ngược chiều — ở đúng cơ sở của pin

Lặp lại phép ghép của T5 §3, thay toàn bộ số bằng cơ sở `price`:

| | Cơ sở `close` (T5 gốc) | Cơ sở `price` (ở đây) |
|---|---|---|
| (A) LÊN — chặn nhóm mã live không mua được: L0@0,20 → L1@0,20 | **+4,08pp** | **+3,85pp** |
| (B) XUỐNG — hạ trần fill 20%→5%ADV (T4 chỉ xác nhận tới 3,86%): L1@0,20 → L1@0,05 | **−4,50pp** | **−3,53pp** |
| **Áp CẢ HAI**: L1@0,05 vs chân pin L0@0,20 | 26,82% vs 27,24% = **−0,42pp** | 29,18% vs 28,86% = **+0,32pp** |

**Kết luận ghép số — mạnh hơn bản `close` một chút, theo hướng ngược lại về dấu:**
1. Ở **cả hai** cơ sở giá, áp đồng thời hai thiên lệch cho ra một số **cách chân pin dưới 0,5pp**
   (−0,42pp ở `close`, +0,32pp ở `price`). **Hai thiên lệch gần triệt tiêu nhau — kết luận trung
   tâm của T5 được tái lập ở cơ sở giá của pin.**
2. **Dấu của phần dư ĐỔI CHIỀU giữa hai cơ sở** (−0,42 → +0,32). Đây là bằng chứng bổ sung rằng
   phần dư ấy **nằm trong nhiễu**, không phải một hiệu ứng có hướng. ⇒ củng cố nhãn mới: **đọc số
   pin KHÔNG theo chiều nào** — không cận dưới, không cận trên.
3. **Không** có cơ sở re-pin lên 32,71%/34,24%, cũng **không** có cơ sở re-pin xuống 29,18%.
   Pin giữ nguyên **28,86%**.

## 6. Ranh giới — cái báo cáo này KHÔNG làm

- ❌ Không đề xuất re-pin (theo cả hai chiều), không đề xuất bật `LIQ_ZERO_BLOCK` mặc định.
- ❌ Không tuyên bố CONFIRMED gì mới. Kết luận cơ chế (H_B bị bác) đã CONFIRMED ở job
  `Taylor_20260803_045138`; đây chỉ là **ghép lại cùng kết luận đó ở đúng cơ sở giá**.
- ❌ Vẫn là **mô phỏng-với-mô phỏng** ở tầng MỨC: trần 20%ADV/phiên vẫn chưa được neo (T4 chỉ cho
  cận dưới 3,86%). Câu hỏi MỨC đóng bằng sổ `lag_liq_ledger.py`, mốc **2026-12-15** /
  **2027-03-31** (`mike/kb/projects/lag-adv-filter-tracking.md`).
- ✅ Production **không bị đụng**: `git status` chỉ có `lag_liquidity_filter.py` (docstring-only,
  chứng minh bằng AST-identity — việc 1 của job này) + 2 file bản sao nghiên cứu untracked.
- ✅ **§8 tên file:** mọi chân gắn `EXP_TAG=pcap_pXXX_LY` ⇒ không chân nào ghi đè CSV canonical.

**Files:** `run_rung_price.sh` · log `pcap_p{005,020,100}_{L0,L1}.log` ·
CSV `data/v23_..._exp_pcap_p*_L*_univpit.csv`.
