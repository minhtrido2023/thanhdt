# T2 — THANG NAV (knob TRỰC GIAO): kết quả + kiểm tra manipulation

**Job:** `Taylor_20260803_045138` · 2026-08-03 · Harness `run_nav.sh` · Engine
`pt_v23_lagcap_research.py` (khác production **đúng 1 dòng đã ghi chú**).
Snapshot `bq_cache_asof20260729_postrestate`, `LAG_LIQ_PCT=0.20` (gốc), `LAG_ADV_BASIS=close`,
`threads=1`, `$DNA_PYEXE`. **Chỉ đổi `NAV_TOTAL_B`.**

## 1. Vì sao knob này bổ sung được cho T1

T1 nới trực tiếp **trần mô hình** (`%ADV/ngày`). T2 giữ nguyên trần, đổi **kích cỡ sổ**: NAV nhỏ ⇒
mỗi slot nhỏ hơn so với ADV ⇒ ràng buộc capacity **lỏng hơn** mà **không** đụng vào tham số mô hình.
Hai đường vào **khác nhau** cho **cùng** một cơ chế. Cảnh báo C3 (README §3.2) vẫn đúng — NAV làm
nhiễu nhiều thứ cùng lúc — nên T2 là **kiểm chứng chéo**, không phải phép thử sạch hơn T1.

## 2. Thang

| NAV | L0 (control) | L1 (`LIQ_ZERO_BLOCK=lag`) | **Δ CAGR** | Δ NAV cuối |
|---|---|---|---|---|
| **5B** (lỏng nhất) | 29,24% (122,23B) | 34,72% (204,95B) | **+5,48pp** | +82,7B |
| **10B** | 28,64% (230,52B) | 33,80% (376,44B) | **+5,16pp** | +145,9B |
| **25B** | 28,18% (551,42B) | 31,87% (785,01B) | **+3,69pp** | +233,6B |
| **50B** (gốc = pin) | **27,24%** (1.006,33B) | 31,32% (1.490,21B)¹ | **+4,08pp** | +483,9B |
| **100B** (chặt nhất) | 25,18% (1.642,14B) | 28,83% (2.349,19B) | **+3,65pp** | +707,1B |

¹ cặp 50B lấy từ T1/A-B 08-02 (**cùng** snapshot, **cùng** config); chân L0@50B của bản sao nghiên
cứu tái lập pin R3 đến từng chữ số nên so trực tiếp được.

**Chỉ số phụ:** Sharpe L0 1,84 / 1,83 / 1,85 / 1,81 / 1,72 · L1 1,99 / 1,94 / 1,88 / — / 1,82.
MaxDD L1 xấu hơn L0 ở 4/5 rung (vd 10B: −20,6% vs −17,2%). Calmar L0 1,63 / 1,67 / 1,52 / 1,48 /
1,25 · L1 1,79 / 1,64 / 1,52 / — / 1,51.

## 3. Manipulation check (BẮT BUỘC, đăng ký trước — cùng bộ tiêu chí T1)

Tỷ lệ vị thế LAG bỏ dở (`ABANDONED_REFUND`), đếm lại từ chính CSV audit của mỗi chân:

| NAV | n vị thế L0 | L0 abandoned% | n vị thế L1 | L1 abandoned% |
|---|---|---|---|---|
| 5B | 1.444 | **30,2%** | 1.768 | **41,1%** |
| 10B | 1.594 | 34,4% | 2.007 | 49,2% |
| 25B | 1.830 | 42,1% | 2.296 | 56,1% |
| 50B | 2.066 | 48,5% | 2.516 | 63,7% |
| 100B | 2.245 | **54,5%** | 2.715 | **70,1%** |

**Phán quyết: manipulation CÓ ăn — đơn điệu HOÀN HẢO trên cả 5 rung, cả hai chân**
(L0 −24,3pp, L1 −29,0pp khi đi từ 100B xuống 5B). ⇒ knob NAV tác động **đúng** vào ràng buộc
capacity; phép thử **không vô hiệu**.

⚠️ **Cùng một hạn chế như T1, phải nói thẳng:** ngay ở rung lỏng nhất (5B) abandoned% vẫn là
30,2%/41,1%, **không** đạt ngưỡng "<~20%" đã đăng ký cho trạng thái "capacity hết ràng buộc" — phần
dư do `max_fill_days=5` + `min_fill_pct` + các mã ADV thật sự bé. ⇒ mọi kết luận chỉ dùng **CHIỀU
của đạo hàm**, không dùng giá trị tuyệt đối ở đầu lỏng.

## 4. Đối chiếu với dự đoán ĐĂNG KÝ TRƯỚC

`H_B` (hiện vật capacity) dự đoán: **gỡ ràng buộc capacity ⇒ Δ teo về ~0**. Vùng đã đăng ký:
Δ(rung lỏng) ≤ +0,5pp ⇒ H_B trội; ≥ +2,0pp ⇒ H_A trội.

**Thực đo Δ tại rung lỏng nhất (5B) = +5,48pp** — lớn nhất toàn thang, gấp **11×** ngưỡng H_B.

⇒ **H_B bị BÁC BỎ lần thứ hai, bởi một knob TRỰC GIAO, và lại theo cách mạnh nhất: sai DẤU của
đạo hàm.** Nới capacity theo đường NAV cho **cùng chiều** với nới capacity theo đường `%ADV`.

**Đơn điệu (skill §10) — trung thực về chỗ chưa đẹp:**
- Nửa lỏng (5B → 25B): Δ giảm đơn điệu chặt **+5,48 → +5,16 → +3,69pp**. Đúng hình dạng dự đoán.
- Nửa chặt (25B → 100B): **+3,69 → +4,08 → +3,65pp** — **phẳng và có một nghịch đảo nhỏ ở 50B**.
  Theo kỷ luật đã đăng ký ở T1 ("thang không đơn điệu ⇒ hạ độ tin cậy một bậc"), **hạ một bậc** cho
  vùng 25–100B. Không ảnh hưởng kết luận về **dấu**: cả 5 rung đều ≫ +2,0pp, và cực đại nằm đúng ở
  đầu lỏng.
- Ghi chú provenance: cặp 50B là cặp DUY NHẤT ghép từ hai lần chạy khác nhau (L0 batch T1, L1 batch
  A/B 08-02). Nghịch đảo nhỏ rơi đúng vào cặp đó — **không** loại trừ được đây là nhiễu ghép batch.

## 5. Kết luận T2

1. **Hai knob độc lập cho CÙNG một kết luận.** T1 (`%ADV` ×20) và T2 (NAV ×20) đều cho
   `dΔ/d(capacity) > 0`. H_B đòi hỏi **dấu âm** ở cả hai. ⇒ Δ **không** phải hiện vật hấp thụ vốn.
   Đây là điều kiện "hai knob cùng kết luận" mà README §4.2 đặt ra làm bằng chứng mạnh.
2. **Δ không phải hằng số, nhưng cũng không teo.** Trên dải NAV 20× nó nằm trong **+3,65 … +5,48pp**
   — chưa bao giờ gần 0. Ở NAV **thật đang giao dịch (~1B)**, ngoại suy từ đầu lỏng cho Δ **lớn
   hơn**, không nhỏ hơn, +5,48pp.
3. **Cảnh báo vận hành mới (khác T1):** L1 có **MaxDD xấu hơn** L0 ở 4/5 rung. Lợi ích của bộ lọc
   đến kèm rủi ro rút vốn cao hơn, không phải bữa trưa miễn phí. Calmar chỉ hơn ở 3/5 rung.
4. **KHÔNG được kết luận:** không rung nào ở đây cấp phép pin một con số. T2 vẫn là **mô phỏng-với-
   mô phỏng** (khiếm khuyết D3); nó tách **cơ chế**, không hiệu chuẩn **mức**. Xem T4.

---
**Bổ sung 2026-08-03 (sau review quant-skeptic):** bảng walk-forward IS/OOS cho mọi rung của thang này nằm ở `T5_DECISION.md` §3b. Tóm tắt: Δ **dương ở cả hai nửa trên cả 10 chân** (không phải hiện vật in-sample), **nhưng độ lớn tập trung gần hết ở OOS** (rung gốc: IS +0,86pp vs OOS +7,28pp) ⇒ thêm một lý do không trích Δ như hằng số.
