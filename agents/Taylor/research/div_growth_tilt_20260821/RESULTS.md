# KẾT QUẢ — B_signal_v2: div-growth CAGR làm tilt liên tục (industry-relative)

Job `Taylor_20260821_113800` · PREREG khoá trước ở `PREREG.md` (commit `mike@647c9424`)
Panel tái dùng: `../div_growth_signal_20260821/panel_enriched.csv` (universe_pit, cuối tháng,
2014-01-27 → 2026-07-31, 151 tháng, 52.960 dòng, 15.094 dòng `has_cagr`).
Selfcheck độc lập: `selfcheck.py` — **PASS 4/4** (z tính lại bằng vòng lặp tay khớp tới 6,7e-16
trên 941 dòng/200 ô; 1.268/1.268 ô giữ lại thoả `n≥5 ∧ mean(z)=0 ∧ sd(z)=1`; IC tính lại khớp
tuyệt đối; `prox` xác nhận đúng bằng `dep/DY` trên 5 ca thật).

## VERDICT: **WEAK** — KHÔNG WIRE

| Chân | Ngưỡng khoá trước | Đo được | Đạt? |
|---|---|---|---|
| **H1 PRIMARY** `IC(z_cagr_ind_L2, BHAR60)` FULL | `> 0,04` ∧ `t_NW ≥ 2,0` | **0,0367** · t_NW **2,73** | ❌ IC / ✅ t |
| H1 — IS (≤2019-12) | — | **0,0620** · t 2,75 | ✅ đạt cả 2 |
| H1 — OOS (≥2020-01) | — | **0,0130** · t 0,95 | ❌ (dương, dưới ngưỡng) |
| **H2** partial IC control `prox`, FULL | `> 0` | **0,0296** · t_NW 2,23 | ✅ trên FULL |
| H2 — IS / OOS | — | **+0,0685** (t 3,16) / **−0,0067** (t −0,59) | ❌ ĐỔI DẤU ở OOS |
| **H3** sparsity `pct_rows` | `≥ 30%` ⇒ không SPARSE | **80,2%** (ô: 48,5%) | ✅ **KHÔNG SPARSE** |

Khớp đúng định nghĩa WEAK ở PREREG §4: *H1 thoả trọn ở IS (0,062 > 0,04 ∧ t 2,75 ≥ 2,0), OOS
dương nhưng dưới ngưỡng*. **Minh bạch chỗ luật tự chồng nhau:** đọc chữ nghĩa mệnh đề NO-GO
(`IC ≤ 0,04` trên FULL) thì đây là NO-GO. Hai cách đọc dẫn tới **cùng một hành động: không wire**;
tôi báo WEAK vì mệnh đề WEAK cụ thể hơn và mô tả đúng hình dạng dữ liệu.

## 1. Cái ĐÚNG trong giả thuyết: industry-z THẬT SỰ thêm thông tin so với CAGR thô

So sánh trên **ĐÚNG cùng một mẫu con** (H1b — thiết kế để tách "z có ích" khỏi "lọc mẫu làm đẹp số"):

| Scope | `IC(z_cagr_ind_L2)` | `IC(cagr thô, cùng mẫu)` | Δ |
|---|---|---|---|
| FULL | **0,0367** (t_NW **2,73**) | 0,0270 (t_NW **1,73**) | **+0,0097** |
| IS | 0,0620 (t 2,75) | 0,0507 (t 1,88) | +0,0113 |
| OOS | 0,0130 (t 0,95) | 0,0049 (t 0,32) | +0,0081 |

Chuẩn hoá trong ngành nâng IC ở **cả ba** scope và đẩy t_NW từ *không có ý nghĩa* (1,73) sang
*có ý nghĩa* (2,73; p = 0,0063). Kết luận của study cha — "cắt 3 bậc ±5% là cách mất thông tin
nhất" — được xác nhận: dạng liên tục + khử ngành tốt hơn hẳn nhãn GROWING/STABLE/DECLINING
(hiệu nhóm cũ **−0,23pp, ngược hướng**). **Giả thuyết của tôi đúng về hướng.**

Chi tiết phụ: H1c (khử ngành CẢ HAI VẾ) cho IC 0,0367 FULL — y hệt H1 ⇒ toàn bộ tác dụng đến từ
vế X, không phải vế Y. Fallback ICB L1 (`//1000`) yếu hơn L2 (FULL 0,0276 vs 0,0367) ⇒ L2 là mức
chia đúng; không cần dùng fallback (H3 đã không SPARSE).

## 2. Cái SAI: nâng được MỨC, không chữa được ĐÀ SUY GIẢM

| | IS | OOS | Suy giảm |
|---|---|---|---|
| `cagr` thô (study cha, toàn universe) | 0,037 | 0,012 | −67% |
| `z_cagr_ind_L2` (study này) | 0,062 | 0,013 | **−79%** |

Industry-z kéo IS lên gần gấp đôi nhưng OOS gần như đứng yên (0,012 → 0,013). Đây đúng chữ ký của
một cải tiến **chỉ nở ra ở giai đoạn IS**, không phải một cải tiến cấu trúc — dù phép biến đổi này
đã được PREREG (không tune hậu nghiệm), nên nó không phải overfit theo nghĩa quy trình, mà là bằng
chứng thật rằng tín hiệu div-growth đã **tắt sau 2020**.

## 3. H2 — tương tác với yield-floor: "đạt" trên FULL nhưng rỗng ở OOS

Partial Spearman (control `prox = lãi_gửi/DY`, đúng công thức production `_yield_floor()`,
loại ngân hàng ICB 8355; mẫu 12.086 dòng):
- FULL **+0,0296** (t 2,23) — thoả `> 0`, tức tilt CAGR có thông tin NGOÀI yield proximity.
- Nhưng IS **+0,0685** (t 3,16) vs OOS **−0,0067** (t −0,59) ⇒ **đổi dấu**. Toàn bộ phần "gia
  tăng" nằm ở IS. Đọc H2 "đạt" mà bỏ tách giai đoạn là đọc sai.

Double sort (hiệu `hi_z − lo_z` trên BHAR60, tercile `prox`):

| prox tercile | FULL | IS | OOS |
|---|---|---|---|
| T1 thấp nhất (BELOW_FLOOR, DY > lãi gửi) | +0,50pp (p 0,32) | **+1,69pp (p 0,022)** | −0,35pp (p 0,61) |
| T2 | +0,44pp (p 0,44) | **+2,19pp (p 0,011)** | −0,62pp (p 0,40) |
| T3 cao nhất (ABOVE_FLOOR) | −0,14pp (p 0,82) | −0,77pp (p 0,40) | +0,25pp (p 0,77) |

Có hình dạng đơn điệu hợp lý ở IS (tilt CAGR mạnh nhất đúng ở nhóm gần/dưới sàn lợi suất, tắt ở
nhóm đắt) — nhưng **biến mất sạch ở OOS**, và 2 p-value IS chưa qua hiệu chỉnh 6 ô đồng thời.

## 4. Ghi chú thống kê phải mang theo khi trích số này
- `se_NW = 0,0134` ⇒ **CI95 của IC FULL = [0,0103; 0,0630]**. Ngưỡng 0,04 **nằm TRONG** khoảng này:
  dữ liệu **không phân biệt được** "IC = 0,0367" với "IC = 0,04". Trượt ngưỡng ở đây là *trượt theo
  luật đã khoá*, không phải bằng chứng mạnh rằng IC thật < 0,04. Điều này cắt **cả hai chiều** —
  cũng không được dùng để nói "gần đạt nên coi như đạt".
- N thật = **149 tháng** (đơn vị độc lập là tháng, không phải 12.101 dòng); trung bình 80 mã/tháng.
- Test PRIMARY là **1** test duy nhất (khai báo trước). Mọi con số khác (H1b/H1c/H2/L1/bhar20/
  bhar60_price) là mô tả, không được đọc như test độc lập.

## 5. Hàm ý
1. **KHÔNG wire.** `div_growth_signal` giữ nguyên `DISPLAY_ONLY` như study cha đã chốt.
2. **Đóng hướng này lại.** Đây là lần thử thứ hai trên cùng một tín hiệu gốc, với dạng hàm tốt hơn
   hẳn về mặt đo lường (t 1,73 → 2,73) mà vẫn không qua được ngưỡng, và OOS vẫn ~0. Thử tiếp biến
   thể thứ ba trên cùng dữ liệu là fishing, không phải nghiên cứu.
3. **Tri thức mang đi (dùng được cho factor KHÁC):** trước khi kết luận một factor liên tục là vô
   dụng, hãy thử **z-score trong ngành ICB L2** — ở đây nó nâng IC +0,0097 và t_NW +1,0 trên đúng
   cùng mẫu, thuần bằng việc bỏ thành phần ngành. Với universe_pit của VN, mức L2 phủ **80,2%** số
   dòng ở ngưỡng ≥5 payer (L1 phủ 91,9% nhưng IC yếu hơn) ⇒ L2 là điểm cân bằng đúng.
