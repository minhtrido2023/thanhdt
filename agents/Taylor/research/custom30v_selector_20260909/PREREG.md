# VÒNG 4 — TIỀN ĐĂNG KÝ (custom30V selector)
job `Taylor_20260909_153631` · viết **TRƯỚC** khi chạy bất kỳ chân treatment nào · **PAPER-ONLY**
· AUDIT_EXP_TAG `c30vsel20260909`

Neo bắt buộc mang theo: **Phần 0** (`PHASE0.md`, đã ghi bus trước khi viết file này) và toàn bộ
tiền lệ đã bị bác ở mục §1. 3 vòng BAL NO-GO liên tiếp **không** tạo áp lực phải tìm ra số dương.

---

## 1. Cái gì ĐÃ BỊ BÁC — không chân nào dưới đây được lặp lại

| đã đo | kết quả | nguồn |
|---|---|---|
| `eyonly` (bỏ hẳn 1/PCF, mọi route) | −0,05pp FULL = no-op | registry A2, 07-14 |
| `eyfin` (bỏ 1/PCF cho financial) | +0,08pp, trái dấu IS/OOS = nhiễu | registry A1, 07-14 |
| `eyrisk` (ey × sàn ROE liên tục) | **NO-GO cả 2 scope** (−0,28 / −0,39pp) | 07-15 |
| `v3comp`/`v3route`/`v3route2`/`v3route3` (rank tham chiếu ngành, dạng composite) | **NO-GO**, fix route thật −2,38pp | 07-14 ×2 |
| `fincap` 0,30 / 0,45 / 0,50 / 0,55 (cắt trọng số tài chính) | −0,64 / −0,84 / −0,74 / −0,32pp, MaxDD ĐỨNG YÊN | 07-14 ×2 |
| accrual-quality gate trong CFO_POOL (3 bản độc lập) | **NO-GO ×3** | 08-30 ×2, 09-06 R3 |
| FSCORE tilt / FSCORE bottom-exclude / MAX5 lottery / EVEB route-swap | negative ở proxy | 06-21 → 07-05 |
| pool THU HẸP 60→30 (liq-tilt) | REFUTED | #19 registry |
| (30, cap 0,15) · permanent-exclude 7 tên · custom30B bull-park · stability floor · SOFT-glide | đã bác | KB |

**Hệ quả với 3 hạt giống của dispatch:** trục (2) *lens ngân hàng* và trục (3) *rank tham chiếu
ngành* đã có câu trả lời đo được ở **dạng composite / dạng cắt trọng số** — vòng này **KHÔNG** lặp
lại các dạng đó. Chỉ mở đúng **một dạng chưa từng đo** của mỗi trục, nêu rõ ở §3.

## 2. Thống kê — N khai thật

| đại lượng | giá trị | dùng cho |
|---|---|---|
| kỳ tái cân bằng ĐỘC LẬP (sự kiện chọn mã) | **48** | LOYO/LOWO, block bootstrap |
| vị thế (tên × kỳ) | 1.440 | thống kê phân phối vị thế |
| phiên | 2.965 | chuỗi NAV |
| năm lịch | 13 (2014-2026) | C4a LOYO theo năm |

Khác hẳn BAL (N=10 cửa sổ regime): **N ở đây là 48 sự kiện chọn mã**, nên block bootstrap dùng
block **63 phiên ≈ 1 quý** (khớp chu kỳ rebal), KHÔNG khai theo số dòng.

**N_trials = 4** (L1a, L1b, L2, L3). Không có chân nào ngoài 4 chân này. Không sweep tham số.

## 3. Bốn chân — mỗi chân một trục, không grid

### L1a / L1b — ĐỘ RỘNG POOL (trục cấu trúc, Phần 0 §6)
`BASKET_CFO_POOL` **60 → 90** (L1a) và **60 → 120** (L1b). Không đổi gì khác.

- **Vì sao:** pool ràng buộc **48/48 kỳ**; trung bình **132 tên đã qua cổng rating≤3 không bao giờ
  được chấm điểm định giá**. Registry chỉ từng đo chiều THU HẸP (60→30, REFUTED).
- **Không phải grid-search:** `BASKET_CFO_POOL` là tham số production sẵn có (mặc định 60); 2 điểm
  tiền đăng ký, không sweep. **Luật đọc kết quả chốt trước:** chỉ tính là bằng chứng khi phản ứng
  **ĐƠN ĐIỆU** theo độ rộng (60→90→120 cùng chiều). Không đơn điệu = nhiễu, NO-GO bất kể dấu.
- **Đánh đổi biết trước:** nới pool kéo tên thanh khoản thấp hơn vào ⇒ cap 20%-ADV của parking sẽ
  siết hơn. Báo cáo phải in ADV rổ để không nhầm alpha với ảo giác thanh khoản.

### L2 — CHÂN DÒNG TIỀN BỀN thay chân `1/PCF` (trục user (1))
Chế độ mới `BASKET_SELECT=eycfq`:
```
score(t) = 2·rank_pct(1/PE)                          nếu t ∈ {BANK, INSURANCE, SECURITIES}
score(t) = rank_pct(1/PE) + rank_pct(cfy3(t))        ngược lại
cfy3(t) = (CF_OA_3Y as-of Release_Date / 3) / (giá THÔ tại ngày rebal × OShares)
```
- **Khác gì với cái đã bác:** `eyonly` **bỏ** chân 2; accrual-gate dùng chất lượng dòng tiền làm
  **CỔNG/SÀN**. Đây là **THAY THẾ chân định giá**: đổi lợi suất dòng tiền **1 kỳ** (1/PCF) thành
  lợi suất dòng tiền **3 năm**. Chưa ai đo dạng này.
- **Bằng chứng nó là thước đo KHÁC (đo trước, `cov_check.py`):** Spearman(1/PCF, cfy3) = **0,319**
  (Pearson 0,138) trên 854 cặp phi-tài-chính ⇒ không phải biến thể của cùng một con số.
- **Độ phủ đã kiểm tra thật (yêu cầu dispatch):** CF_OA_3Y phủ **100,0%** trên tên phi-tài-chính
  (962 cặp), 99,6% trên tài chính; theo kỳ min 93% / trung vị 100%; **0/48 kỳ dưới 80%**. ⇒ chân
  này ĐƯỢC chạy. (Nếu phủ đã dưới 80% ở bất kỳ kỳ nào thì theo dispatch phải bỏ chân, không lấp giả định.)
- **Tài chính bị loại khỏi chân cfy3 BẰNG CẤU TRÚC**, không phải hậu kiểm: `CF_OA` vô nghĩa với
  ngân hàng (`kb/data_registry/fundamentals/roe_roic_fscore_quality.md` + banking framework). Dùng
  đúng khuôn `2·ey` của `eyfin` để **giữ nguyên thang [0,2]** — chính lớp lỗi thang-đo đã giết `v3route`.
- Thiếu dữ liệu → `fillna(0.5)`, y hệt mọi chân khác (fail-open, không phạt sự vắng mặt).

### L3 — GHIM SỐ LƯỢNG NGÂN HÀNG, ĐỔI *TÊN* NGÂN HÀNG (trục user (2)+(3), dạng duy nhất chưa đo)
- Registry 07-14 đã ghi tường minh: *"hướng route-aware duy nhất còn logic … percentile TRONG
  route (ghim ~0,5, chỉ đổi 'bank nào' không đổi 'bao nhiêu bank')"* và **Taylor KHÔNG tự mở** —
  cần user/Mike. **Dispatch vòng 4 chính là uỷ quyền đó.**
- Cơ chế: chấm `yieldcombo` như production, cắt top-30, **đếm** `n_bank` tên BANK trong top-30, rồi
  **thay đúng `n_bank` slot đó** bằng `n_bank` ngân hàng tốt nhất trong pool theo **lens ngân hàng
  đã validate**. Slot phi-ngân-hàng **không đụng tới**. ⇒ tỷ trọng ngành **bất biến theo thiết kế**.
- Lens dùng **nguyên văn** `banking_valuation_framework.md` (đã backtest, "REAL signal, holds OOS"),
  **không hằng số mới**: sàn chất lượng `ROE_Min3Y ≥ 0,08`; Gordon `justified_PB = (ROE5Y−0,05)/0,08`;
  điểm `z(justified_PB − PB) + z(ROE5Y) + z(NP_YoY)`. Ngân hàng trượt sàn ROE bị đẩy xuống cuối
  hàng ngân hàng (không bị loại khỏi rổ — loại sẽ đổi số lượng, phá đúng thứ chân này ghim).
- **Prior THẤP, khai trước:** cùng framework đó kết luận tín hiệu "**largely already owned** …
  already captured by custom30V", và `pb_z` trong route bank chỉ IC +0,065 (t=1,17). Kỳ vọng nền
  là **không có gì để thu hoạch**; chân này chạy để ĐÓNG trục, không để kỳ vọng dương.

## 4. Chân ĐỐI CHỨNG + bẫy `sys.path` vòng 2

`ctrl` = **đúng lệnh pin R3**:
```bash
NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" \
AUDIT_END=2026-06-19 $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
```
chạy qua **bản copy nghiên cứu** của `custom_basket.py` + engine. `pt_v23_audit_2014.py` tự
`sys.path.insert(0, WORKDIR)` ⇒ bản copy bị che (bẫy vòng 2). Xử lý y hệt vòng 3: **re-insert thư
mục nghiên cứu lên đầu `sys.path` ngay sau dòng đó**, và control phải đi qua **cùng đường** ấy.

**Điều kiện tiên quyết, kiểm TRƯỚC khi tin bất kỳ chân treatment nào:** md5 CSV control phải bằng
**`7d053e6201c9d107685ff4d1dd9d2d2a`** (pin R3, vòng 3 tái lập byte-identical). Lệch = harness bẩn,
DỪNG, không đọc số treatment.

Ràng buộc chung mọi chân: `universe_pit`, `LAG_ADV_BASIS=price`, `BQ_CACHE_THREADS=1`,
IS 2014-19 / OOS 2020+, cấm cột forward-looking (`profit_*`, `_center_*`, `PC1W..PC2M`, `Open_1D`,
`O*`, `Pattern_*`), không sửa file production (`filter.json`, `simulate_holistic_nav.py`,
`pt_v23_audit_2014.py`, `custom_basket.py`, `trading_rules.json`), `EXP_TAG` trên MỌI arm kể cả
control (§8 coding_guidelines — không ghi đè tên canonical).

## 5. Bảy tiêu chí GO — chốt trước, không sửa sau khi thấy số

| # | tiêu chí | ngưỡng | nguồn ngưỡng |
|---|---|---|---|
| **C1** | ΔCAGR vs ctrl | **> +0,385pp** | sàn nhiễu vòng 2/3 |
| **C2** | Calmar | **≥ Calmar(ctrl)** | quy ước |
| **C3** | IS **và** OOS | **cùng dương** | chữ ký robust (KB) |
| **C4a** | LOYO theo năm (13) | max \|đóng góp 1 năm\| < **50%** tổng delta | vòng 2/3 |
| **C4b** | per-window (10 cửa sổ regime) | max \|đóng góp\| < **50%** | vòng 2/3 |
| **C5a** | DSR vs SR_ctrl, N_trials=**4** | **> 0,95** | KB "DSR<0.95 = RED FLAG" |
| **C5b** | PBO (CSCV, S=16, toàn họ 5 config) | **< 0,5** | KB |
| **C6** | block bootstrap CI95 ΔCAGR (block 63 phiên) | **loại trừ 0** | vòng 2/3 |
| **C7** | self-check | **0 VND** (BAL+LAG) mọi chân **và** md5 control = pin | §4 |

**Trượt bất kỳ tiêu chí nào = NO-GO.** Không có "gần đạt".

## 6. Đối chứng bắt buộc nếu có chân thắng (không bỏ qua như vòng 3 §3)

Chân nào qua C1 phải in thêm, TRƯỚC khi được gọi là edge:
1. **Tỷ trọng cổ phần trung bình trong NEUTRAL** (`w_equity`) — lệch > 2pp so với ctrl ⇒ delta đến
   từ đổi mức rủi ro, không phải chọn mã; phải quy delta cho beta trước khi báo.
2. **Tỷ trọng tài chính theo ngày** — chân nào đổi tỷ trọng ngành > 5pp thì đó là **cú cược ngành**,
   phải báo như cược ngành (đúng cảnh báo 07-14), không phải "selector tốt hơn".
3. **ADV rổ + số ngày cap 20%-ADV ràng buộc** — riêng L1a/L1b (nới pool kéo tên mỏng hơn vào).
4. **Turnover** — chân nào tăng turnover > 1,5× ctrl phải trừ chi phí thật trước khi so C1.

## 7. Ghi trước điều sẽ KHÔNG làm
- Không đổi mức park 80% (config F1, user chốt 2026-08-04).
- Không đổi `N_MEMBERS=30`, `name_cap=0.10`, `gate_rating=3`, `rebal=q2m5`.
- Không thêm chân sau khi thấy số. Không tách/gộp chân để cứu một kết quả.
- Không wire gì vào production trong vòng này, kể cả nếu cả 7 tiêu chí đều đạt: theo KB, wire cần
  **quant-skeptic CONFIRMED** + user duyệt.
