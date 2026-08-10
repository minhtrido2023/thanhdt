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
