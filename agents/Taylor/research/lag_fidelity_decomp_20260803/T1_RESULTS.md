# T1 — THANG CAPACITY: kết quả + kiểm tra manipulation

**Job:** `Taylor_20260803_021414` · 2026-08-03 · Harness `run_rung.sh` · Engine
`pt_v23_lagcap_research.py` (khác production **đúng 1 dòng đã ghi chú**).
Snapshot `bq_cache_asof20260729_postrestate`, NAV 50B, `LAG_ADV_BASIS=close`, `threads=1`, `$DNA_PYEXE`.

## 1. Điều kiện hợp lệ — ĐẠT

Rung gốc `pct=0.20`, chân L0 in ra:

```
Final NAV 1,006.33B  CAGR 27.24%  Sharpe(252) 1.81  MaxDD -18.4%  Calmar 1.48
```

= **tái lập CHÍNH XÁC pin R3 hiện hành** (27,24 / 1,81 / −18,4 / 1,48 / 1.006,33B).
⇒ bản sao nghiên cứu hợp lệ, A/B đọc được. (Không tái lập ⇒ toàn bộ T1 vô hiệu — điều kiện tiên
quyết đăng ký trước ở README §4.)

## 2. Thang

`liquidity_volume_pct` của sổ LAG = trần mua **mỗi phiên** tính theo %ADV. Nhỏ = capacity **ràng
buộc chặt**; lớn = capacity **gần như không ràng buộc**.

| `%ADV/ngày` | L0 (control) | L1 (`LIQ_ZERO_BLOCK=lag`) | **Δ CAGR** | Δ NAV cuối |
|---|---|---|---|---|
| **0,05** (chặt 4x) | 24,31% (752,49B) | 26,82% (965,07B) | **+2,51pp** | +212,6B |
| **0,20** (gốc = production) | **27,24%** (1.006,33B) | 31,32% (1.490,21B)¹ | **+4,08pp** | +483,9B |
| **1,00** (lỏng 5x) | 28,78% (1.168,93B) | 33,98% (1.914,31B) | **+5,20pp** | +745,4B |

¹ chân L1@0,20 lấy từ A/B 2026-08-02 (**cùng** snapshot, **cùng** config, engine production).
Có thể so trực tiếp vì chân L0@0,20 của bản sao nghiên cứu tái lập số production đến từng chữ số.

**Chỉ số phụ (rung lỏng 1,00):** Sharpe L0 1,85 / L1 1,96 · MaxDD L0 −17,7% / L1 **−20,6%** ·
Calmar 1,62 / 1,65. Rung chặt 0,05: Sharpe 1,69 / 1,77 · MaxDD −19,4% / −17,6% · Calmar 1,26 / 1,53.

## 3. Manipulation check (BẮT BUỘC — đăng ký trước)

Tỷ lệ vị thế LAG bỏ dở (`ABANDONED_REFUND`), đo lại từ chính CSV audit của mỗi chân:

| `%ADV/ngày` | L0 abandoned% | L1 abandoned% |
|---|---|---|
| 0,05 | 56,8% (n=2.394) | 75,4% (n=2.666) |
| 0,20 | 48,5% (n=2.066) | 63,7% (n=2.516) |
| 1,00 | **34,6%** (n=1.614) | **49,3%** (n=2.028) |

**Phán quyết: manipulation CÓ ăn, nhưng CHỈ MỘT PHẦN — phải nói thẳng.**
- ✅ Đơn điệu hoàn hảo theo đúng chiều ở **cả hai** chân (L0 −22,2pp, L1 −26,1pp khi nới 20x) ⇒
  knob tác động **đúng** vào cơ chế định nhắm; phép thử **không vô hiệu**.
- ⚠️ **KHÔNG đạt ngưỡng "<~20%"** đã đăng ký cho trạng thái "capacity hết ràng buộc". Ở rung 1,00
  vẫn còn 34,6%/49,3% bỏ dở — phần dư này do `max_fill_days=5` + `min_fill_pct` và do có những mã
  ADV thật sự bé, **không** phải do trần %ADV. ⇒ rung 1,00 là **"capacity nới mạnh"**, KHÔNG phải
  **"capacity bằng không"**. Mọi kết luận dưới đây chỉ dùng **CHIỀU của đạo hàm**, không dùng giá
  trị tuyệt đối ở đầu lỏng.

## 4. Đối chiếu với dự đoán ĐĂNG KÝ TRƯỚC

`H_B` (hiện vật capacity) dự đoán: **nới capacity ⇒ Δ teo về ~0** (vì Δ *chính là* chênh lệch khả
năng hấp thụ). Vùng kết luận đã đăng ký: Δ(rung lỏng) ≤ +0,5pp ⇒ H_B trội; ≥ +2,0pp ⇒ H_A trội.

**Thực đo: Δ = +2,51 → +4,08 → +5,20pp — TĂNG đơn điệu khi capacity được nới.**

⇒ **H_B bị BÁC BỎ, và bị bác theo cách mạnh nhất có thể: sai DẤU của đạo hàm.** Không phải "Δ vẫn
lớn hơn ngưỡng" mà là **Δ đi ngược hẳn chiều H_B đòi hỏi**. Manipulation chỉ đạt một phần không
làm suy yếu kết luận này — để xác định **dấu** của `dΔ/d(capacity)` thì một can thiệp ăn một phần
là đủ, và dấu đó là dương ở **cả hai** khoảng (0,05→0,20 và 0,20→1,00).

**Nhất quán với cơ chế T3:** nhóm mã bị chặn ở L0 fill **KHÔNG bị trần** (`daily_max = remaining_value`)
nên **bất biến** với `pct`; nới `pct` chỉ giúp **vốn được giải phóng ở L1** triển khai được nhiều hơn.
Nới capacity ⇒ L1 khai thác được nhiều hơn ⇒ Δ **phải** tăng. Thang này chính là dấu vân tay của cơ
chế "tránh bẫy lỗ + tái triển khai", không phải của "sổ không fill nổi".

## 5. Kết luận T1 — và ranh giới của nó

**ĐƯỢC PHÉP kết luận:**
1. **Δ KHÔNG phải hiện vật do sổ 25B không hấp thụ nổi size.** Giả thuyết đó đòi Δ teo khi nới
   capacity; thực tế Δ tăng đơn điệu. Đây là câu hỏi đã treo 3 vòng — **nay đã tách được**.
2. **Δ nhạy MẠNH với độ chặt của mô hình fill** (+2,51 … +5,20pp trên dải 20x). ⇒ **con số +4,08pp
   không phải hằng số**, nó là hàm của một tham số mô hình chưa được neo vào thực tế.
3. **Cảnh báo vận hành quan trọng:** ở rung chặt (0,05), chân "đã sửa" L1 = **26,82%**, tức **THẤP
   HƠN pin hiện hành 27,24%**. Nếu fill thật ngoài đời chặt hơn giả định engine, thì cả hai chân
   đều lạc quan và **không có cơ sở nào để re-pin LÊN**.

**KHÔNG được phép kết luận:**
- ❌ Không kết luận 31,32% (hay 33,98%) là kỳ vọng/pin mới. T1 tách **cơ chế**, không hiệu chuẩn
  **mức**. Việc đó cần **T4 (neo ngoài mô phỏng)** — đối chiếu `%ADV/ngày` giả định với fill THẬT
  của DNSE — vì cả 3 rung vẫn là **mô phỏng**.
- ❌ Không suy ra gì từ mức tuyệt đối ở rung 1,00 (manipulation chỉ đạt một phần, §3).
- ❌ Không đề xuất bật `LIQ_ZERO_BLOCK` mặc định trong job này (bộ lọc **live** đã bật sẵn từ
  07-21/07-22 vì lý do độc lập; đây thuần là câu hỏi **con số backtest**).

## 6. Bước tiếp theo (thứ tự)

| | Việc | Vì sao bây giờ | Effort |
|---|---|---|---|
| **T4** | Neo `%ADV/ngày` vào fill THẬT (DNSE 07-01→nay, lọc `accountNo`) | T1 vừa chứng minh Δ **nhạy** với chính tham số này ⇒ nó thành tham số quan trọng nhất chưa được neo | ~1h |
| **T2** | Thang NAV {5,10,25,50,100}B | knob **trực giao**; hai knob cùng kết luận = bằng chứng mạnh hơn nhiều | ~30' |
| **T5** | Cập nhật docstring `lag_liquidity_filter.py` (bỏ diễn giải "capital velocity") | file production ⇒ cần duyệt, **không tự sửa** | — |

**Kiến nghị gate:** T1+T3 là kết luận **cơ chế** (không đề xuất đổi production, không đề xuất
re-pin) ⇒ theo skill §15 chưa bắt buộc quant-skeptic. Nhưng vì kết luận này **sẽ bị trích dẫn** như
giấy phép để re-pin, **nên** đưa qua `bin/verify_finding.sh` trước khi bất kỳ ai dùng nó làm căn cứ.

---
**Bổ sung 2026-08-03 (sau review quant-skeptic):** bảng walk-forward IS/OOS cho mọi rung của thang này nằm ở `T5_DECISION.md` §3b. Tóm tắt: Δ **dương ở cả hai nửa trên cả 10 chân** (không phải hiện vật in-sample), **nhưng độ lớn tập trung gần hết ở OOS** (rung gốc: IS +0,86pp vs OOS +7,28pp) ⇒ thêm một lý do không trích Δ như hằng số.
