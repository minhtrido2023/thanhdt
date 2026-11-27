---
kind: coding-guideline-topic
title: "Money, Equity, and Cash Accounting Semantics (§25)"
owner: Mike
status: canonical
updated: 2026-11-27
---

# Money, Equity, and Cash Accounting Semantics (§25)

> Tách nguyên văn từ [`../coding_guidelines_ext.md`](../coding_guidelines_ext.md) (2026-11-27, giữ trần <40 KB).

## 25. "Tiền" KHÔNG Phải Một Con Số — Mỗi Consumer Phải Khai Rõ Đang Hỏi Câu Nào

**Luật:** bất kỳ code nào đọc số dư tiền từ broker PHẢI khai (trong tên biến hoặc comment ngay tại
chỗ đọc) nó đang hỏi câu nào trong hai câu dưới, và lấy đúng field của câu đó. Không có "field tiền
mặc định"; `DNSEBroker.get_cash()` **không** phải mặc định an toàn.

| Câu hỏi | Field ĐÚNG | Dùng ở | Sai thì hỏng kiểu gì |
|---|---|---|---|
| "Tôi **SỞ HỮU** bao nhiêu vốn?" (cơ sở NAV / mẫu số tính tỷ trọng mục tiêu) | **`totalCash − totalDebt` (+ `egg.totalValue` nếu consumer là NAV/pool, xem dưới)** | `daily_nav_snapshot.py:449`, `reconcile_equity.py`, `compute_park_trim.py` (mẫu số pool), `compute_active_nav.py` (§cash) | Khai THIẾU NAV đúng bằng tiền bán chưa settle ⇒ under-deploy, hoặc pool co lại đúng bằng lượng vừa bán ⇒ **vòng lặp tự kích bán tiếp** |
| "Tôi **TIÊU ĐƯỢC NGAY** bao nhiêu?" (sức mua đặt lệnh phiên này) | **`ppse.pp0Buy`/`qmaxBuy`**, hoặc `availableCash` khi không gọi được ppse | `DNSEBroker.get_cash()`, `check_plan_funding()`, `executor.py` · ⚠️ `compute_jit_unpark.py` (L2) là NGOẠI LỆ user duyệt — xem ghi chú ngay dưới bảng | Nới lỏng gate tiền ⇒ đặt lệnh không có tiền; hoặc chặn oan plan tự cấp vốn đủ |

**Chiều thứ BA (thêm 2026-08-19, sau sự cố TRIM giả cùng ngày): Trứng vàng (`egg.totalValue`,
sibling của `stock` trong payload `balances` — xem `kb/data_registry/trading-bot/
dnse_openapi_v2_calling_guideline.md`) KHÔNG nằm trong `totalCash` VÀ KHÔNG nằm trong
`availableCash`.** Nó là vốn CHỦ SỞ HỮU thật (thuộc dòng "SỞ HỮU" ở trên) nhưng cần lệnh rút +
về tài khoản T+1 mới tiêu được (KHÔNG thuộc dòng "TIÊU ĐƯỢC NGAY"). Consumer thuộc dòng "SỞ HỮU"
PHẢI cộng thêm field này (đã làm ở `compute_active_nav.py`/`daily_nav_snapshot.py` từ 08-18,
`compute_park_trim.py` từ 08-19 — sự cố xảy ra vì L1 bị bỏ sót khi 2 file kia đã sửa: tiền
chuyển từ cash sang egg làm pool L1 co lại giả, sinh TRIM oan ~58,7tr cho SpaceX+ZaloPay).
Consumer thuộc dòng "TIÊU ĐƯỢC NGAY" (`check_plan_funding()`, `executor.py`)
**KHÔNG được cộng egg** — đó là nới lỏng gate tiền y hệt lỗi ở dòng trên.

⚠️ **NGOẠI LỆ DUY NHẤT, user duyệt 2026-08-19: `compute_jit_unpark.py` (L2) CÓ cộng egg.**
Bảng trên xếp L2 vào dòng "TIÊU ĐƯỢC NGAY" và cấm cộng egg; commit `956d8ec5` (2026-08-20)
làm NGƯỢC LẠI, và đó là quyết định có chủ đích chứ không phải vi phạm — 2 vòng làm rõ cùng
ngày + quant-skeptic vòng 2, user chốt. Lý do hợp lệ: **L2 là tầng ĐỀ XUẤT, không phải tầng
GATE.** Gate cứng vẫn là `check_plan_funding()` (P0) và nó vẫn KHÔNG cộng egg — nghĩa là
egg không hề nới lỏng cổng tiền, nó chỉ cho phép L2 đề xuất "mua đủ, có rút egg" thay vì
âm thầm SHRINK lệnh xuống phần cash thật. Bù lại, mỗi `buy_amendments[i]` phải mang
`funded_via` ("cash" | "cash+egg") + `egg_relied_vnd` (CẬN TRÊN, không phải số chính xác)
và in cảnh báo rút egg tường minh; egg không rút kịp ⇒ P0 giữ HOLD, đúng thiết kế.
Ranh giới cứng + vì sao KHÔNG chiết khấu phí: docstring `§pool-egg-L2` trong
`mike/bin/compute_jit_unpark.py` — ĐỌC TRƯỚC khi đổi lại chỗ đó.
Bằng chứng chạy thật (2026-08-19, ZaloPay): `cash đầu 39.17tr (availableCash 0.39tr +
Trứng vàng 38.78tr)` kèm đúng dòng cảnh báo "CẦN RÚT Trứng vàng ... TRƯỚC khi đặt lệnh".
(Ghi lại 2026-08-22 tại weekly ops audit: bảng §25 viết 08-19 còn quyết định L2 chốt 08-19→20,
nên hai nguồn mâu thuẫn nhau đúng 3 ngày. Ai đọc bảng mà không đọc dòng này sẽ "sửa" L2 bỏ
egg đi và lặng lẽ revert một quyết định user đã duyệt.)

**Vì sao là luật chứ không phải trùng hợp — HAI bug cùng loại trong HAI ngày liên tiếp:**
`compute_park_trim.py` (mẫu số pool, 2026-08-09, job `Taylor_20260809_150316`, commit `df7d92b4`)
và `compute_active_nav.py` (cơ sở NAV, 2026-08-10, job `Taylor_20260810_004252`). Cả hai đều lấy
`availableCash` vì nó là field đầu tiên `get_cash()` trả về.

**Số neo (đo thật, SpaceX 2026-08-07 — phiên bán 13 mã PARK ≈189,4tr):**
`availableCash` 11:25 = **4.821.143**; 19:10 sau khi bán = **4.821.143** (Y HỆT); `totalCash`
19:10 = **203.656.265**. ⇒ tiền bán **KHÔNG BAO GIỜ** vào `availableCash` trong ngày bán. Trên
active_nav điều đó = **−198.835.122đ, −20,7% NAV**.
Hằng đẳng thức đối soát: `totalCash == availableCash + cashDividendReceiving + depositInterest`
(ZaloPay 08-07: `5.818.854 + 6.453.500 + 318 = 12.272.672`, khớp tuyệt đối).

**Bốn hệ quả bắt buộc khi viết code loại này:**
1. **Fail-closed, KHÔNG rơi về `availableCash`.** Không đọc được `totalCash`/`totalDebt` ⇒ thoát,
   không ghi file. Rơi về = tái lập đúng bug vừa sửa, lặng lẽ.
2. **Tái dùng 3 guard, đừng viết lại**: `park_holdings._stock_block_all_zero` /
   `_cash_fields_all_zero` / `_cash_fields_inconsistent` (bất biến `totalCash ≥ availableCash`).
   Cả ba đều bắt một cách hỏng mà hai cái kia mù — bỏ bất kỳ cái nào là để hở đúng một lối.
3. **Đối soát chéo bằng nguồn có đường đi KHÁC** trước khi tin: `nav_history_<label>.csv`
   (`daily_nav_snapshot.py`) tính NAV theo path hoàn toàn khác — lệch = một trong hai sai.
4. **Cơ sở tỷ trọng ĐƯỢC PHÉP lớn hơn sức mua trong ngày** (tiền chưa settle T+2, cổ tức phải thu,
   `manual_offbook_assets_vnd`). Đó KHÔNG phải lỗi sizing; chặn overshoot là việc của tầng thực thi
   (gate P0 `check_plan_funding` + L2 JIT-unpark), không phải của tầng NAV. Nhưng phải **công bố**
   khoảng cách đó ra output, đừng để người đọc plan tưởng là lỗi.

**Vì sao prose ở data_registry KHÔNG đủ (bài học riêng):**
`kb/data_registry/trading-bot/dnse_openapi_v2_calling_guideline.md` ĐÃ ghi rõ "3 field cash khác
nhau" từ 2026-08-03 — bug vẫn xảy ra hai lần sau đó. Khác biệt: tài liệu kia nói *các field khác
nhau*, bảng trên nói **script NÀO của mình phải dùng field NÀO**. Thêm consumer tiền mới ⇒ thêm
một dòng vào bảng, đó là cách rule này không mốc.

*→ `agents/Taylor/research/active_nav_cash_basis_fix_20260810.md` (bản vá + 26 selfcheck + đối
soát độc lập khớp từng đồng, quant-skeptic CONFIRMED cao vòng 1).*
