# Funding gate — hũ tiền CHUNG chỉ được đếm một lần (sự cố ZaloPay 2026-08-10)

- **Job**: `Taylor_20260810_024323` · **Commit**: `19e788f` (WorkingClaude), `97a80058` (mike/kb)
- **File chạm**: `trading_bot/plan_funding_gate.py`, `plan_funding_gate_selfcheck.py`
- **quant-skeptic**: **CONFIRMED**, confidence *medium* (log `mike/logs/verify_20260810_025632_2516526.log`)
- **Incident**: `kb/incidents/2026-08/2026-08-10-funding-gate-multipackage-shared-pot-false-block.md`

## 1. Triệu chứng

09:05 ICT `run_bot.sh --account ZaloPay` thoát rc=3 sau 0 phút, **0 lệnh được đặt** trên một plan
đã được user duyệt. `check_plan_funding` trả BLOCK: "Σ mua 92.649.435đ vượt sức mua 11.637.708đ,
tiêu thụ 105,6%". 3/4 lệnh mua (DRI/POW/SCL) là LAG entry-window **ngày 3/3** — không khớp hôm nay
là cửa sổ đóng hẳn.

## 2. Root cause — chính xác hơn chẩn đoán ban đầu

Chẩn đoán ban đầu (Winston): "`buying_power_vnd` cộng `pp0Buy` của 2 nhóm = đếm hũ 2 lần". Đúng
về hiện tượng nhưng **chưa phải cơ chế đẩy 54,6% thành 105,6%**.

Công thức 08-07 đặt **hũ chung ĐẦY ĐỦ vào mẫu số của TỪNG nhóm** rồi mới chia JIT theo tỉ lệ:

```
U_cũ = Σ_g  need_g / (POT + JIT × need_g/Σneed)
```

Thay `POT = 0` để tách riêng phần JIT sẽ thấy ngay bản chất:

```
U_cũ|POT=0 = Σ_g need_g / (JIT × need_g/Σneed) = k × Σneed / JIT      (k = số nhóm)
```

tức **tín dụng JIT bị chia loãng đúng k lần**. Với `POT` nhỏ (cash-only, 5,8tr so với JIT 163,9tr)
thì gần như toàn bộ mẫu số là phần JIT bị chia loãng ⇒ k=2 làm tỉ lệ tiêu thụ **gấp đôi**:
0,5298 + 0,5258 = **1,0556** thay vì 0,546.

Không lộ trước 08-10 vì mọi phiên trước chỉ có **một** nhóm gói vay (khi đó `Σ ≡ max ≡` công thức
đúng). Hôm nay là lần đầu 4 lệnh mua tách 2 nhóm.

## 3. Công thức mới — suy từ mô hình, không thêm tham số

Mô hình tài nguyên đúng: các gói vay **không có tiền riêng**, `pp0Buy_g = POT × λ_g` với
`λ_g = 1/initialRate` của gói (cash-only ⇒ λ=1 ⇒ mọi gói trả về cùng một số). Một lệnh mua
`need_g` tiêu của hũ chung đúng `need_g/λ_g`, nên ràng buộc thật là

```
Σ_g need_g/λ_g ≤ POT + JIT   ⟺   Σ_g need_g/pp0Buy_g ≤ 1 + JIT/POT
```

Cài đặt:

```
U_raw = Σ_g need_g / pp0Buy_g            POT = min_g pp0Buy_g      (đếm MỘT lần)
H     = 1 + JIT_hiệu_lực / POT           U   = U_raw / H           BLOCK khi U > 1
```

`JIT_hiệu_lực = JIT × (Σ need nhóm ĐO ĐƯỢC / Σ need toàn plan)` — nhóm không đo được không nằm
trong `U_raw` nên cũng không được hưởng phần tín dụng của nó.

**Kiểm chứng số trên ca thật**: `U_raw = 92.649.435/5.818.854 = 15,9223`;
`H = 1 + 163.862.011/5.818.854 = 29,1611`; `U = 0,546` — **khớp đúng tỉ lệ cấp plan
92.649.435/(5.818.854+163.862.011) = 54,6%**.

## 4. Vì sao KHÔNG đổi `Σ` sang `max`

Đề xuất ban đầu: "các nhóm cùng `pp0Buy` ⇒ dùng chung hũ ⇒ lấy `max`". Từ chối, có phản ví dụ
số cụ thể (khoá bằng selfcheck `[Q3]`):

> Hai nhóm, mỗi nhóm cần 60% CÙNG một hũ 100tr. `max(0,60; 0,60) = 0,60` ⇒ **OK oan**, trong khi
> plan cần **120%** số tiền đang có.

Nghịch lý biểu kiến "hũ chung nên đừng cộng" tan khi viết ra đơn vị: cái được cộng là **tỉ lệ
tiêu thụ của cùng một hũ**, không phải hai hũ độc lập. Cộng tỉ lệ là đúng; sai lầm 08-07 nằm ở
chỗ **lặp lại hũ trong mẫu số** rồi chia nhỏ JIT.

Đúng một dòng phân biệt: `Σ` giữ nguyên tính chống-che-giấu-vốn (`[F]`, `[P6]`: nhóm A vượt sức
mua vẫn CHẶN dù nhóm B thừa), `max` thì không.

## 5. Blast radius — chứng minh bằng đại số, không phải bằng cảm giác

| Hình dạng plan | Hành vi |
|---|---|
| Nhóm ĐƠN (mọi phiên thường lệ) | `U = (need/bp)/((bp+JIT)/bp) = need/(bp+JIT)` — **đồng nhất tuyệt đối** bản cũ |
| `JIT = 0` (không có lệnh bán chạy trước) | `U = Σ need_g/pp0Buy_g` — **đồng nhất tuyệt đối** bản cũ |
| Nhiều nhóm **VÀ** có JIT | **Duy nhất** hình dạng đổi hành vi = đúng hình dạng sự cố |

`POT = min` là **cận thận trọng**, không phải xấp xỉ tuỳ tiện: `pp0Buy ≥ tiền mặt` luôn đúng
(λ ≥ 1) ⇒ `min(pots) ≥ POT_thật` ⇒ `H_tính ≤ H_thật` ⇒ `U_tính ≥ U_thật` ⇒ gate **chỉ chặn
thừa, không bao giờ bỏ lọt**. (quant-skeptic tự suy lại bất đẳng thức này độc lập.)

## 6. Verify

- `plan_funding_gate_selfcheck.py` **97 PASS / 0 FAIL**, output **byte-identical** dưới 4 TZ
  (no-TZ / UTC / Asia-Ho_Chi_Minh / America-New_York).
- Case mới: `[Q1]` replay THẬT · **`[Q1b]` chứng minh ngược** (tính lại công thức CŨ trên chính
  dữ liệu đó ra 1,0556 > 1 — ca `[Q1]` thật sự khoá bug chứ không phải khẳng định suông) ·
  `[Q2]` bỏ hết lệnh bán ⇒ VẪN BLOCK · `[Q3]` lỗ hổng của `max` · `[Q4]` biên `≤` · `[Q5]` hũ
  khác λ · `[Q6]` JIT chiết khấu khi có nhóm không đo được.
- Sweep phụ thuộc (`bin/selfcheck_scope_map.sh trading_bot/plan_funding_gate.py`):
  `plan_cash_commitment_selfcheck` **59/0**, `loan_package_resolution_selfcheck` **ALL PASS**.
- Live read-only re-probe trên broker sống: `action=OK`, util 55,9%, `shared_pot_vnd` = 1.915.422
  (một lần, không phải 3.830.844).
- **Kết quả LIVE**: autoheal restart bot 09:50 ⇒ gate cho qua ⇒ ZaloPay **đặt được lệnh mua thật**.

## 7. Rủi ro tồn dư — công bố nguyên văn, không giấu

quant-skeptic CONFIRMED nhưng chỉ **medium**, vì: mô hình "hũ chung × đòn bẩy" mới chỉ được kiểm
chứng SỐNG ở ca cash-only, mà ca đó **suy biến** (λ=1 với mọi gói) nên **không phân biệt được** mô
hình này với bất kỳ mô hình nào khác trùng kết quả khi λ=1. Ca nhiều gói vay **đòn bẩy khác λ**
hiện chỉ có stub `[Q5]`, chưa có live probe. **Không phải regression** (bản 08-07 đứng trên cùng
axiom), và backstop tầng 3 (`executor` `get_cash() < need` → `WAIT_CASH`) không đổi.

**Việc còn nợ**:
1. Live read-only probe trên account đòn bẩy có 2 gói khác `initialRate` — xác nhận `pp0Buy_g` tỉ
   lệ với một hũ chung chứ không phải hạn mức riêng từng gói.
2. Thay `[Q5]` bằng số `pp0Buy` DNSE thật khi có probe trên.
3. `plan_cash_commitment.py` tiêu thụ `utilization` nhưng **không có selfcheck nào cho plan nhiều
   nhóm** — cần bổ sung.

## 8. Bài học

Một phép gộp "thận trọng" chỉ thận trọng khi **mô hình tài nguyên đúng**. `Σ` phân số hợp lệ khi
các mẫu số là tài nguyên độc lập cộng được; lặp lại cùng một mẫu số ở mọi số hạng thì không. Stub
selfcheck `[F]` cho mỗi nhóm một hũ RIÊNG (100tr vs 50tr) đã **che mất chính giả định đó suốt
6 ngày** — một giả định phạm vi không được viết thành test.

Cùng ngày, cùng họ lỗi, ở tầng dưới: `c22bd1c` (08-07) áp `_resolve_loan_package_id` **vô điều
kiện** cho cả lệnh BÁN dù tiêu đề commit ghi "cho MỌI lệnh **MUA**" ⇒ 8/8 lệnh bán PARK bị DNSE
từ chối `HTTP 400: deal not found`. Cũng là **giả định phạm vi không có case phủ chiều còn lại**.
Đã giao Mafee (`Mafee_20260810_031058`) — logic đặt lệnh là ranh giới cứng của Taylor.
