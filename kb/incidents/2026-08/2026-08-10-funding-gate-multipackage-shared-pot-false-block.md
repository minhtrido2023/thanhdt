# 2026-08-10 — FUNDING gate CHẶN OAN plan ZaloPay đã duyệt: cộng tỉ lệ tiêu thụ của 2 gói vay DÙNG CHUNG một hũ tiền

**Hiện tượng.** 09:05 ICT `run_bot.sh --account ZaloPay` (plan 2026-08-10, `approved_by=user (John)`)
thoát rc=3 sau 0 phút, KHÔNG đặt lệnh nào. `check_plan_funding` trả `BLOCK`: "Σ lệnh MUA
92.649.435đ VƯỢT sức mua thật 11.637.708đ … tiêu thụ 105,6%". Bot KHÔNG chết — gate chặn đúng
thiết kế; không có lệnh kẹt, không có autoheal log, journal ZaloPay rỗng (chỉ có `.lock`). SpaceX
cùng phiên chạy bình thường.

**Root cause (đo lại read-only bằng chính `check_plan_funding` lúc 09:1x, không suy đoán).**
4 lệnh mua tách thành 2 nhóm gói vay, và **cả hai nhóm trả về CÙNG một `pp0Buy = 5.818.854đ`**:

| nhóm | gói vay | n_orders | need | pp0Buy | JIT chia | utilization |
|---|---|---|---|---|---|---|
| A | 1258 (`resolved:symbol`, probe DRI) | 2 | 48.936.675 | **5.818.854** | 86.550.576 | **0,5298** |
| B | 1826 (`resolved:symbol`, probe POW) | 2 | 43.712.760 | **5.818.854** | 77.311.435 | **0,5258** |

**KHÔNG nhóm nào vượt sức mua của chính nó** (0,53 và 0,53 đều < 1,0). BLOCK đến 100% từ phép
`measured_util = Σ_g util_g = 1,0556 > 1,0` (`plan_funding_gate.py:262,276`).

Tỉ lệ tiêu thụ THẬT ở cấp plan: `92.649.435 / (5.818.854 + 163.862.011) = **54,6%**`.

ZaloPay là account **cash-only**: `pp0Buy` của MỌI gói vay đều ≈ `availableCash` của cùng một hũ
tiền. Cộng phân số ⇒ hũ 5.818.854đ bị **đếm 2 lần**, và `buying_power_vnd` báo ra
`11.637.708đ = 5.818.854 × 2` cũng là con số đếm đôi, không phải sức mua thật.

**Đây là giả định thiết kế sai, không phải lỗi gõ nhầm.** Docstring §CÔNG THỨC và selfcheck case
`[F]` cố ý chốt ngữ nghĩa "cộng tỉ lệ" để chống che-giấu-vốn (nhóm thừa gánh cho nhóm vượt). Nhưng
stub của `[F]` cho mỗi gói một hũ RIÊNG (100tr vs 50tr) — trong khi thực tế cash-only cho hai gói
CÙNG một hũ. Với k nhóm nhu cầu cân nhau, tổng phình ≈ k× ⇒ chặn oan. Trước 08-10 mọi phiên chỉ có
1 nhóm nên `Σ ≡ max` và lỗi không lộ.

Mục tiêu chống che-giấu-vốn của `[F]`/`[G]` đạt được **nguyên vẹn** bằng `max_g util_g > 1` (case
`[G]`: nhóm A util > 1 ⇒ vẫn CHẶN). Chỉ case `[F]` — đúng hình dạng false-positive — đổi kết quả.

**Thiệt hại thật.** 3/4 lệnh mua (DRI, POW, SCL) là LAG entry-window **ngày 3/3**; SSI ngày 2/3.
Không khớp hôm nay ⇒ cửa sổ ĐÓNG HẲN, không catch-up.

**Chưa sửa — chạm ranh giới cấm.** Winston (job `Winston_20260810_020517`) KHÔNG vá: sửa
`plan_funding_gate.py` là **nới một gate tiền thật** giữa giờ giao dịch, và header file yêu cầu
quant-skeptic; sửa plan cũng nằm trong danh sách cấm. Đã escalate bus `question` + Telegram.

**Đề xuất (chờ user/Taylor + quant-skeptic).** Đổi `measured_util` từ `Σ` sang **`max`** khi các
nhóm dùng chung hũ tiền (dấu hiệu máy đọc được: `pp0Buy` các nhóm bằng nhau ⇒ một hũ), kèm check
cấp plan `Σneed ≤ Σ(hũ duy nhất) + JIT`; sửa `buying_power_vnd` báo ra để không đếm đôi; thêm case
selfcheck "2 nhóm CÙNG pp0Buy, tổng need 55% hũ chung → OK".

**Lesson.** Một aggregation "thận trọng" chỉ thận trọng khi mô hình tài nguyên đúng. `Σ` phân số
chỉ hợp lệ khi các mẫu số là tài nguyên ĐỘC LẬP CỘNG ĐƯỢC; stub selfcheck cho mỗi nhóm một hũ riêng
đã che mất chính giả định đó suốt 6 ngày.

---

## RESOLUTION (Taylor, job `Taylor_20260810_024323`, commit `19e788f`, 2026-08-10 ~09:50 ICT)

**Root cause chính xác hơn chẩn đoán ban đầu.** Không chỉ là `buying_power_vnd` đếm đôi. Bản
08-07 đặt **hũ chung ĐẦY ĐỦ vào mẫu số của TỪNG nhóm** rồi mới chia JIT theo tỉ lệ:
`U = Σ_g need_g/(POT + JIT×need_g/Σneed)`. Với k nhóm nhu cầu cân nhau, phép đó làm **tín dụng
JIT bị chia loãng đúng k lần** — thay POT=0 vào sẽ thấy ngay: `Σ = k×Σneed/JIT` thay vì
`Σneed/JIT`. Đó mới là thứ đẩy 54,6% thành 105,6%.

**Công thức đã áp** (suy thẳng từ mô hình hũ chung `pp0Buy_g = POT × λ_g`, không thêm tham số):

```
U_raw = Σ_g need_g / pp0Buy_g          POT = min_g pp0Buy_g   (hũ chung, đếm MỘT lần)
H     = 1 + JIT_hiệu_lực / POT         U   = U_raw / H        BLOCK khi U > 1
```

**KHÔNG áp đề xuất `max`.** `max` mở một lỗ hổng thật: hai nhóm mỗi nhóm tiêu 60% CÙNG một hũ ⇒
`max = 0,60` ⇒ "OK" oan dù plan cần 120% số tiền đang có. Selfcheck `[Q3]` khoá đúng ca này.
Tính chống-che-giấu-vốn được giữ nguyên bằng cách **giữ `Σ`** (case `[F]`, `[P6]` vẫn CHẶN);
chỉ sửa chỗ đếm đôi hũ + chia loãng JIT.

**Blast radius hẹp, chứng minh bằng đại số**: nhóm ĐƠN ⇒ `U = need/(bp+JIT)`, đồng nhất TUYỆT
ĐỐI bản cũ (`(need/bp)/((bp+JIT)/bp) = need/(bp+JIT)`); `JIT = 0` ⇒ cũng đồng nhất bản cũ. Chỉ
hình dạng "nhiều nhóm VÀ có tín dụng JIT" đổi hành vi — tức đúng và chỉ đúng hình dạng sự cố.

**Verify.** `plan_funding_gate_selfcheck.py` **97 PASS / 0 FAIL**, byte-identical dưới 4 TZ
(no-TZ/UTC/ICT/NY). Case mới: `[Q1]` replay THẬT (assert util 54,6% và hũ 5.818.854 chứ không
phải 11.637.708), **`[Q1b]` chứng minh ngược** (tính lại công thức CŨ trên chính dữ liệu đó ra
1,0556 > 1 — ca `[Q1]` thật sự khoá bug, không phải khẳng định suông), `[Q2]` bỏ hết lệnh bán ⇒
VẪN BLOCK, `[Q3]` lỗ hổng của `max`, `[Q4]` biên `≤`, `[Q5]` hũ khác nhau (margin 2×), `[Q6]`
nhóm không đo được ⇒ JIT chiết khấu. Sweep phụ thuộc (`bin/selfcheck_scope_map.sh`):
`plan_cash_commitment_selfcheck` 59/0, `loan_package_resolution_selfcheck` ALL PASS.
Live read-only re-probe: `action=OK`, util 55,9%, `shared_pot_vnd` = 1.915.422 (một lần).

**quant-skeptic CONFIRMED** (confidence **medium**) — tự re-run cả 3 suite, tự suy lại bất đẳng
thức `min(pots) ≥ POT_thật ⇒ H_tính ≤ H_thật ⇒ U_tính ≥ U_thật` (chỉ chặn thừa, không bao giờ
bỏ lọt). **Rủi ro tồn dư nó nêu, giữ nguyên không giấu**: mô hình "hũ chung × đòn bẩy" mới chỉ
được kiểm chứng SỐNG ở ca cash-only — mà ca đó **suy biến** (λ=1 với mọi gói) nên không phân biệt
được mô hình này với mô hình khác. Ca nhiều gói vay ĐÒN BẨY khác λ hiện chỉ có stub `[Q5]`, chưa
có live probe. Không phải regression (bản 08-07 đứng trên cùng axiom). **Việc còn nợ**: (1) live
probe read-only trên account đòn bẩy có 2 gói khác `initialRate`; (2) thay `[Q5]` bằng số DNSE
thật khi có; (3) `plan_cash_commitment.py` chưa có selfcheck nào cho plan nhiều nhóm.

**Kết quả LIVE.** Autoheal khởi động lại bot lúc **09:50**; gate cho qua; ZaloPay **đặt được lệnh
mua thật** (DRI, SCL). Sự cố chặn oan CHẤM DỨT.

## ⚠️ SỰ CỐ THỨ HAI lộ ra ngay sau đó — `deal not found` chặn toàn bộ lệnh BÁN

Gate thông rồi thì lộ tầng dưới: **8/8 lệnh BÁN PARK** (BID/CTG/HDB/MBB/TCB/VCB/VHM/VPB)
`PLACE_FAIL` **`HTTP 400: deal not found`**, lặp 376 lần từ 09:50. Không bán được ⇒ không có tiền
JIT ⇒ POW/SSI `WAIT_CASH`, DRI mới khớp 300/1900, SCL 200/1000.

**Root cause (đã xác minh bằng `git show`, không đoán)**: commit **`c22bd1c` (2026-08-07)** đổi
`DNSEBroker.place_order` từ `elif cash_only: lp = _resolve_loan_package_id(symbol) / else: lp =
None` thành `lp = _resolve_loan_package_id(symbol)` **vô điều kiện**. Lệnh BÁN PARK không đặt
`cash_only` nên TRƯỚC 08-07 đi ra với `lp=None`; NAY mang `loanPackageId` giải theo MÃ ⇒ DNSE
không tìm thấy deal khớp gói đó ⇒ 400. **Tiêu đề chính commit đó ghi "cho MỌI lệnh MUA"** — ý
định là buy-only, code lại áp cả hai chiều (thiếu điều kiện `side`).

**Bằng chứng lịch sử**: ZaloPay `PLACE` sell thành công 07-17/07-20/07-21/07-22/07-23/07-27
(0 fail); **08-10 là ngày ĐẦU TIÊN có lệnh bán kể từ `c22bd1c`** ⇒ 376 fail, 0 thành công.
Không phải thiếu hàng: live positions BID 900≥600, CTG 1050≥600, HDB 659≥200, MBB 1102≥900,
TCB 956≥600, VCB 800≥700, VHM sellable 300≥300, VPB 1800≥500.

**Xử lý**: sửa nằm trong **logic đặt lệnh = ranh giới CỨNG** của Taylor ⇒ không tự vá. Đã dispatch
**Mafee** (chủ sở hữu execution, tác giả `c22bd1c`) kèm chẩn đoán đầy đủ — job
`Mafee_20260810_031058` — yêu cầu quant-skeptic trước khi áp, và **cấm khởi động tiến trình bot
thứ 2** (bot đang chạy tự retry ~20s nên code mới trên đĩa sẽ được vòng sau dùng).

**Bài học (cùng họ với chính sự cố trên)**: một thay đổi được chứng minh cho *một chiều lệnh* đã
được áp cho *cả hai chiều* mà không có case nào phủ chiều còn lại — y hệt cách stub `[F]` cho mỗi
gói một hũ riêng đã che mất giả định tài nguyên suốt 6 ngày. Cả hai đều là **giả định phạm vi
không được viết ra thành test**.
