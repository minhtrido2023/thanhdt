# A2 — Race condition tiền mặt giữa hai bộ sinh lệnh (DollarBill 19:0x vs injector 20:30)

**Job** `Taylor_20260804_155443` · 2026-08-04 · **BUILD XONG + SELFCHECK XONG, CHƯA WIRE**

---

## 0. Tóm tắt

| | |
|---|---|
| Đã build | `trading_bot/plan_cash_commitment.py` (module, read-only) |
| Selfcheck | `plan_cash_commitment_selfcheck.py` — **59/59 PASS**, byte-identical ở 4 cấu hình TZ |
| E2E đường dây thật | `mike/agents/Taylor/research/inject_cash_gate_e2e_test.py` — **12/12 PASS** |
| Patch đề xuất | `mike/agents/Taylor/research/discretionary_inject_cash_gate.patch` — `git apply --check` sạch, **CHƯA áp** |
| Production đụng tới | **0 file** (`git diff` xác nhận `mike/bin/discretionary_accumulation_inject.py` nguyên vẹn) |

---

## 1. Đọc hai luồng — trả lời dứt điểm câu "chiều nào chạy trước"

**Injector KHÔNG THỂ chạy trước.** `discretionary_accumulation_inject.py:141-144`: chưa có
file plan thì `return 0` no-op. Trật tự luôn là **plan trước, injector sau** ⇒ chỉ có MỘT
chiều cần kiểm tra. Không cần cơ chế hai chiều, không cần lock, không cần cron mới.

**Injector hiện KHÔNG hề đọc tiền.** `grep -n "cash|available|ppse"` trên file đó → 0 kết
quả. `compute_session_order()` (`trading_bot/discretionary_accumulation.py:52`) không nhận
tham số tiền nào; nó size thuần `min(remaining, cap%ADV)`. Vế trái (plan V2.4 đã dự chi)
chưa từng xuất hiện trong phép tính của nó.

**Sự cố 07-24 thoát bằng gì.** Không phải cơ chế: `plan_SpaceX_2026-07-24.json` field
`cash_planning.tv1_reserve_first` cho thấy DollarBill làm phép trừ đó **bằng tay trong REV2**
(job `DollarBill_20260723_125357`) sau khi được nhắc. Cùng khuôn thất bại 3 lần của A1.

**Số học sự cố, neo lại chính xác** (selfcheck case C giữ cả hai cơ sở để không ai đọc lệch):
V2.4 45,9M + TV1 3,98M = 49.880.000đ vs cash 49.125.163đ → vượt **754.837đ** trước phí,
**792.247đ** sau phí 0,075%. Báo cáo gốc ghi "~0,78M" = con số trước phí.

**Trạng thái hôm nay**: `state_TV1_SpaceX.json` = `completed` (2026-07-29, gom đủ 400/400) ⇒
**0 state active**, injector đang no-op mỗi phiên. Lỗ hổng là **kiến trúc, chưa nổ lại** —
sẽ nổ ở case gom kế tiếp. Đây là lý do nên vá lúc rảnh, không phải lúc đang chạy.

---

## 2. Cơ chế đã build

### 2.1 Vế trái — plan đã dự chi bao nhiêu
`commitment_summary()` cộng Σ lệnh MUA × giá × (1+0,075%), tách theo `book`, và **liệt kê
riêng lệnh không tính được chi phí** (`unpriced`). Lệnh thiếu giá KHÔNG được coi là chi phí 0
— đó là cách một lệnh tàng hình lọt qua phép cộng; gặp là trả headroom `None` và caller
fail-safe không chèn (selfcheck case L).

### 2.2 Vế phải — dùng lại nguyên mô hình A1, không nhân bản logic
Gọi thẳng `plan_funding_gate.check_plan_funding()` (A1, đã LIVE, quant-skeptic CONFIRMED) để
lấy `utilization` U, rồi:

```
headroom = (1 − U) × pp0Buy(gói vay của CHÍNH lệnh sắp chèn)
```

Gói vay giải bằng **đúng hàm `place_order` dùng** (`_resolve_loan_package_id` cho `cash_only`)
— tránh lặp lại bẫy TV1 07-29 (hỏi bằng gói default 1841 → `pp0Buy=0` giả, gói đúng là 1122).
Selfcheck case O neo đúng ca đó.

### 2.3 Khi không đo được `pp0Buy` — fail-safe NGƯỢC CHIỀU với A1, có lý do
A1 (gate lúc thực thi) không đo được thì **không chặn**, vì chặn oan làm lỡ deadline vào lệnh
LAG T+1 (phí thật). Ở đây ngược lại: **không đo được ⇒ không chèn thêm**. Căn cứ là tính chất
của chính chương trình gom, không phải sở thích: `accept_underfill: true`, `no_chase: true`,
resting-bid **re-đặt mỗi phiên** trong cửa sổ mềm 20 phiên — bỏ một phiên gần như không tốn
gì, còn chèn lệnh không có tiền đằng sau sẽ đẩy **cả plan** vào diện bị A1 chặn TOÀN BỘ lúc
09:05 (A1 chặn cấp plan, không chặn từng lệnh).

Cận dùng khi không đo được: `availableCash + Σ lệnh BÁN × (1−phí)`. **Không nhân hệ số đòn
bẩy nào** — đúng thiết kế: lệnh `DISCRETIONARY_SPECIAL` là `cash_only` ("CASH — KHÔNG dùng
margin", master plan TV1). Khác có chủ ý với `FALLBACK_LEVERAGE_MULT=3.0` của A1.

### 2.4 Hành động: THU NHỎ trước, bỏ phiên sau — và luôn để lại vết
- headroom ≥ 1 lô → **SHRINK** về bội số lô mua nổi (phần còn lại re-đặt phiên sau).
- headroom < 1 lô → **bỏ phiên**, nhưng ghi `cash_gate_notes` vào **plan** để **báo cáo 21:00
  hiện lý do**. Đây là điểm thiết kế quan trọng nhất: cron KHÔNG được tự quyết "V2.4 hay
  tranche quan trọng hơn". Nó biến một race im lặng thành **một câu cho người đọc** — muốn ưu
  tiên tranche hơn V2.4 thì user re-plan, quyết định vẫn nằm ở human gate 21:00 đã có sẵn.

---

## 3. Lỗi thứ hai tìm được khi đọc code — re-plan nuốt mất tranche

Không nằm trong mô tả dispatch nhưng cùng cặp luồng, và là lỗi **im lặng**:

Nếu plan bị **ghi lại sau khi injector đã chèn** (re-plan 21:3x/22:1x — chính ca sinh ra cron
`send_plan_report --second-chance` 23:00), file plan bị ghi đè toàn bộ ⇒ lệnh đã chèn biến
mất. Lần chạy sau, **dedup-2 của injector** (`ledger` đã có bản ghi cho `plan_date` → skip)
**từ chối chèn lại** ⇒ tranche của phiên rơi mất, không ai báo.

`replan_dropped_injection()` phát hiện đúng trạng thái đó (ledger có / order không có).
An toàn với §5 idempotency: `filled_qty` luôn đọc lại từ broker chứ không từ ledger, và order
id là tất định (`BUY-<TICKER>-DISC-<plan_date>`) nên dedup-1 vẫn chặn trùng trong cùng plan.
Selfcheck case Q phủ cả 4 tổ hợp.

---

## 4. Selfcheck — cái nó BẮT ĐƯỢC, không chỉ cái nó pass

Chạy dưới `env -u TZ`; ba lần chạy đầu **FAIL và mỗi lần là một lỗi thật**:

1. **Lỗi module thật.** `check_plan_funding` trả `SKIPPED`/`utilization=None` khi plan **chưa
   có lệnh mua nào** — ca thường gặp nhất, không phải ngoại lệ. Bản đầu chỉ chấp nhận
   `action=="OK"` nên rơi im lặng về cận tiền mặt: headroom 5M thay vì 40M ⇒ **bỏ phiên oan**.
   Đã sửa (U = 0 khi chưa dự chi gì).
2. **Selfcheck PASS nhầm lý do.** Case B ban đầu đặt `cash == pp0Buy == 50M` nên hai công thức
   ra **cùng một số** — test không phân biệt được nhánh nào chạy. Đã tách (`cash=8M`,
   `pp0Buy=50M`) + thêm assert `basis`. Cùng lúc sửa stub `get_buying_power`: `ppse` thật với
   `loan_package_id=None` trả số của **gói mặc định account**, không phải rỗng.
3. **Assert sai cơ sở.** Băng `775k–785k` không khớp 792.247đ vì tôi so số **sau phí** với con
   số **trước phí** của báo cáo. Đã neo cả hai, ghi rõ cơ sở.

E2E còn bắt thêm một cái nữa, thuộc loại "chạy xong ≠ có tác dụng": `git apply --directory
<abs path>` trả **rc=0 nhưng file đích không hề đổi** — ba scenario đầu "chạy sạch" trên bản
CHƯA vá. Test giờ kiểm chứng nội dung file sau khi áp, không tin mã thoát.

**Phụ thuộc môi trường** (khai theo `verify-before-done`): không mạng, không broker thật,
không credential, không đọc/ghi `data/` production (tmpdir); module không gọi
`datetime`/`date` ở bất kỳ nhánh nào ⇒ không phụ thuộc TZ, và điều đó được chứng minh bằng
cách chạy lại chính selfcheck dưới 4 cấu hình TZ, output byte-identical.

---

## 5. Đề nghị Mike duyệt

1. Merge `trading_bot/plan_cash_commitment.py` (module mới, chưa ai gọi ⇒ merge một mình
   **không đổi hành vi production**).
2. Áp `discretionary_inject_cash_gate.patch` vào `mike/bin/discretionary_accumulation_inject.py`.
3. Gửi quant-skeptic verify trước khi áp bước 2.

**Rủi ro tồn dư đã biết, nói rõ để không ai tưởng đã đóng:** gate này cho V2.4 quyền ưu tiên
mặc định (injector chạy sau nên nó nhường). Doctrine gốc là **ngược lại** — "TV1 reserve
first". Nếu quan sát thấy chương trình gom bị đói kinh niên (nhiều phiên liên tiếp
`SKIP_NO_CASH`), cách sửa đúng là bước dự-trữ **trước** khi DollarBill viết plan, không phải
nới gate này. Chưa build vì hôm nay chưa có state active nào để đo, và xây trước khi có bằng
chứng đói là đoán. `cash_gate_notes` + `history_noninject` chính là dữ liệu để quyết định đó
sau này.
