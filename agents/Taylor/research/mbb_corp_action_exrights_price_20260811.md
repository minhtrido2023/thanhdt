# MBB corp-action 2026-08-11 + lớp bug giá tham chiếu ex-rights

**Job** `Taylor_20260810_183618` · **Ngày** 2026-08-11 (01:30–02:40 ICT, tiền phiên)
**Commit** `197404ea` (mike) + `d2c117f` (WorkingClaude) · **Trạng thái** XONG, đã đối soát khớp
từng đồng với ảnh chụp app DNSE của user.

---

## 0. Tóm tắt một đoạn

Hai vấn đề Mike giao HÓA RA CÙNG MỘT GỐC: một sự kiện doanh nghiệp có thật (MBB giao dịch không
hưởng quyền 11/08/2026 — cổ tức cổ phiếu 15% **và** chào bán quyền mua 10:1 giá 10.000đ) không
được đăng ký ở đâu cả. Hệ quả tách làm hai nhánh: (a) **số lượng** — broker đã cộng cổ phiếu
thưởng, sổ lô thì chưa ⇒ `reconcile.ok=False` ⇒ L1 park-trim / L2 JIT-unpark `BLOCKED_RECONCILE`;
(b) **giá** — `compute_active_nav.py` đọc giá đóng cửa phiên TRƯỚC (24.250, chưa điều chỉnh) nhân
với số lượng phiên NÀY (đã điều chỉnh) ⇒ thổi phồng NAV 5.013.250đ (≈0,5%).

Nhánh (b) là **một lớp bug tổng quát**, không phải chuyện của riêng MBB: nó bắn mỗi khi bất kỳ mã
nào trong danh mục giao dịch không hưởng quyền, và cũng bắn ở UPCOM/HNX nơi giá tham chiếu vốn dĩ
khác giá đóng cửa. Bản vá không nhắc tới MBB một chữ.

---

## 1. Bằng chứng — ba nguồn ĐỘC LẬP với chính cái lệch số lượng

`corp_actions.json` cấm suy corp action từ việc thấy qty lệch (một fill sót journal / GHOST_ORDER
/ chuyển khoản CK tạo ra ĐÚNG hình dạng lệch đó). Ba nguồn dưới đây không cái nào dùng cái lệch làm
tiền đề.

### Nguồn 1 — công bố sàn / lưu ký
Ngày GDKHQ **11/08/2026**, ngày ĐKCC **12/08/2026**. MB phát hành ~1,21 tỷ cp trả cổ tức 2025 tỉ lệ
**15%**, đồng thời chào bán ~805,5 triệu cp cho cổ đông hiện hữu giá **10.000đ/cp**. Vốn điều lệ dự
kiến vượt 100.600 tỷ. Nguồn: `vsd.vn/vi/ad/185869` (Tổng công ty Lưu ký & Bù trừ — nguồn gốc),
`vietstock.vn/2026/08/...-1476203.htm`, `vneconomy.vn/mbb-tra-co-tuc-bang-tien-va-co-phieu.htm`.
Đây là WebSearch ĐỘC LẬP, khác nguồn (stockbiz) mà vòng điều tra 08-10 đã dùng.

*Kiểm chéo tỉ lệ quyền mua bằng số tuyệt đối, không tin nhãn "10:1":*
1,21 tỷ ÷ 0,15 ≈ **8,07 tỷ** cp đang lưu hành ⇒ 805,5 triệu ÷ 8,07 tỷ ≈ **10,0%** ⇒ đúng 10:1. ✓

### Nguồn 2 — giá tham chiếu chính thức của sàn (trường GIÁ, không phải trường SỐ LƯỢNG)
`secdef` sáng 08-11 trả `basicPrice=20,2` / `ceilingPrice=21,6` / `floorPrice=18,8`, **đồng nhất
trên cả 7 boardId**. Trong khi `close_price` G1 phiên 08-10 = **24,25**, và BQ `tav2_bq.ticker` độc
lập cũng cho `Close=Price=24.250` ngày 08-10 (tỉ số Close/Price = 1,0 liên tục từ 27/07).

Công thức điều chỉnh chuẩn HOSE cho **gộp** cổ tức CP + quyền mua:

```
P_moi = (P_cu + gia_quyen × ty_le_quyen) / (1 + ty_le_co_tuc + ty_le_quyen)
      = (24.250 + 10.000 × 0,10) / (1 + 0,15 + 0,10)
      = 25.250 / 1,25 = 20.200   ← KHỚP CHÍNH XÁC basicPrice
```
Trần/sàn ±7% quanh 20.200 (21.614→21,6; 18.786→18,8) cũng khớp.

**Đây là hệ một phương trình một nghiệm:** chỉ CẶP (15%, 10:1 @10.000đ) mới đưa 24.250 về đúng
20.200. Nguồn 2 vì vậy xác nhận ĐỒNG THỜI cả hai tỉ lệ, bằng dữ liệu giá, không mượn gì từ nguồn 1.

### Nguồn 3 — chữ ký KẾ TOÁN của broker (phân biệt corp action với "fill sót journal")
Một fill bị sót journal sẽ **LÀM TĂNG** tổng giá vốn. Corp action thì **GIỮ NGUYÊN** tổng giá vốn
và hạ giá bình quân. Đo thật:

| Account | costPrice trước | costPrice sau | Kiểm tổng giá vốn |
|---|---|---|---|
| SpaceX | 24.850,0000 | 21.608,6957 | 1.100 × 24.850 = **27.335.000** = 1.265 × 21.608,6957 ✓ |
| ZaloPay | 24.597,9129 | 21.417,1483 | 202 × 24.597,9129 = **4.968.778,4** = 232 × 21.417,1483 ✓ |

Khớp tới đồng ở cả hai. Mốc thời gian đọc thẳng từ `positions.modifiedDate`:
**2026-08-10T12:32:49Z = 19:32:49 ICT** (SpaceX) / 12:32:15Z (ZaloPay) — tức broker credit cổ phiếu
thưởng **tối trước ex-date**, đúng cùng khuôn ca VHM 08-05. Bản đọc cuối còn số cũ ~19:12 ICT
08-10, bản đọc đầu đã số mới 00:41 ICT 08-11 — nhất quán.

---

## 2. Vấn đề 1 — số lượng: làm tròn SAI CHỖ

Ca MBB là ca ĐẦU TIÊN tỉ lệ không chia hết, nên nó lộ ra một giả định sai trong
`corp_action_split`. Bản cũ **fail-closed mọi lô lẻ**: nếu bất kỳ lô nào cho ra số không nguyên thì
không áp gì cả cho mã đó + gắn cờ UNVERIFIED.

ZaloPay giữ 202cp qua **2 lô: 100 + 102**. `100 × 1,15 = 115` nguyên, nhưng `102 × 1,15 = 117,3`
thì không ⇒ bản cũ sẽ đứng im và MBB ở ZaloPay bị chặn vĩnh viễn.

**Broker không làm tròn từng lô.** Nó tính quyền trên TỔNG vị thế rồi làm tròn xuống MỘT LẦN:
`floor(202 × 1,15) = floor(232,3) = 232`, rồi hạ giá vốn theo đúng 232 (kiểm bằng nguồn 3 ở trên,
khớp tuyệt đối). Chính docstring cũ đã chỉ đúng chỗ này — "làm tròn từng lô rồi cộng lại KHÁC làm
tròn ở mức vị thế (chỗ broker làm tròn)" — nhưng kết luận sai chiều: thay vì làm tròn ĐÚNG CHỖ,
nó chọn không làm gì.

**Bản mới:** làm tròn xuống một lần trên tổng vị thế, chia phần dôi về từng lô bằng
**largest-remainder (Hamilton)**, tie-break theo thứ tự lô trong sổ ⇒ hoàn toàn tất định. Giá vốn
mỗi lô đặt lại `= tổng giá vốn CŨ của lô / qty MỚI của lô` ⇒ tổng giá vốn bất biến ở cả mức lô lẫn
mức vị thế, kể cả khi **hệ số hiệu dụng ≠ hệ số khai báo** (ZaloPay: 232/202 = **1,148515** chứ
không phải 1,15 — và broker cũng hạ costPrice theo đúng 1,148515).

Chi tiết float: `202 × 1,15 = 232,29999999999998` nhưng `1100 × 1,15 = 1265,0000000000002` —
không cộng epsilon trước khi `floor` thì có ca tụt mất 1 đơn vị. Đã xử lý (`+1e-9`) và có test riêng.

### Nới fail-closed có làm mất an toàn không? KHÔNG — và đã chứng minh, không phải lập luận suông
Cái fail-closed thật sự bảo vệ ta là (a) cổng `_status: CONFIRMED` + ≥2 nguồn độc lập, và (b) cổng
đối soát `Σ lô == openQuantity`. Quy tắc làm tròn sai **lộ ra ngay ở (b)**. Mutation test:

| Hệ số | SpaceX sổ / broker | ZaloPay sổ / broker | reconcile |
|---|---|---|---|
| **1,15 (đúng)** | 1265 / 1265 | 232 / 232 | ✅ ok |
| 1,16 | 1276 / 1265 (+11) | 234 / 232 (+2) | ❌ BLOCKED |
| 1,14 | 1254 / 1265 (−11) | 230 / 232 (−2) | ❌ BLOCKED |
| 1,20 | 1320 / 1265 (+55) | 242 / 232 (+10) | ❌ BLOCKED |

**6/6 đột biến bị giết** trên cả hai account. Không hệ số sai nào trôi im lặng được.

---

## 3. Vấn đề 2 — giá: LỚP BUG TỔNG QUÁT, không phải chuyện của MBB

### Cơ chế
`dnse_close_prices()` đọc `close_price` boardId=G1 — **giá đóng cửa của PHIÊN GẦN NHẤT ĐÃ XONG**.
Chạy hàm này TRƯỚC khi phiên hôm nay đóng (tiền phiên 01:30, hay giữa phiên 10:00) thì giá đó thuộc
phiên **TRƯỚC**. Với một mã đang GDKHQ hôm nay, giá phiên trước là giá **chưa điều chỉnh**, trong
khi `openQuantity` của broker thì **đã điều chỉnh**. Nhân giá cũ × số lượng mới = thổi phồng NAV.

Đây là **cái bẫy thứ hai, ngược chiều cái bẫy 2026-07-06**. Lần đó: BQ sync đêm nên đọc BQ lúc
15:00 ra giá hôm qua ⇒ đã sửa bằng cách chuyển sang `close_price` G1. Lần này: chính `close_price`
G1 cũng "hôm qua" khi phiên chưa đóng. Cùng một họ lỗi — **giá và số lượng đến từ hai thời điểm
khác nhau**.

### Bản vá — tổng quát, không biết MBB là gì
Nếu giá G1 **không thuộc phiên hôm nay** (so `time` của chính entry G1 với ngày ICT, §16), lấy
`secdef.basicPrice` — giá tham chiếu **chính thức của sàn cho phiên hiện tại**, đã bao gồm mọi điều
chỉnh corp action, và là con số app DNSE hiển thị. Không cần biết mã nào có sự kiện gì, chỉ cần
biết *"giá đang cầm thuộc phiên nào"*.

**KHÔNG đổi hành vi đường chạy chính** (EOD 17:30, báo cáo 15:00): lúc đó G1 close đã thuộc phiên
hôm nay ⇒ nhánh mới không kích hoạt, `secdef` thậm chí không được gọi. Đã có test khẳng định điều
này (`secdef_calls == []`).

**Fail-safe:** `secdef` lỗi mạng / trả rỗng / `time` thiếu ⇒ giữ nguyên giá G1 (hành vi cũ). Nhánh
mới chỉ được phép LÀM TỐT HƠN, không được phép làm hỏng đường đang chạy.

### Nó vá nhiều hơn MBB
Chạy thật sáng 08-11 trên danh mục SpaceX, hàm thay **3** mã chứ không phải 1:

| Mã | G1 close (phiên 08-10) | basicPrice (phiên 08-11) | Δ × qty |
|---|---|---|---|
| MBB | 24.250 | **20.200** (ex-rights) | −5.123.250 |
| SCL | 23.300 | **23.400** (HNX) | +150.000 |
| TV1 | 19.800 | **19.700** (UPCOM: tham chiếu = giá BÌNH QUÂN phiên trước, không phải giá đóng cửa) | −40.000 |
| | | **Tổng** | **−5.013.250** |

**−5.013.250 = ĐÚNG BẰNG khoảng lệch user báo.** Không dư một đồng, không có phần "chưa giải thích
được". SCL/TV1 cho thấy lỗi này âm ỉ ở UPCOM/HNX **mỗi phiên**, không đợi corp action.

### Xác nhận chéo từ một đoạn code người khác viết
`daily_nav_snapshot.py` (dựng sau ca VHM 08-05) có cổng `PRICE_XCHECK_TOLERANCE_PCT = 5.0`: nếu
`|close_price − positions.marketPrice| > 5%` thì **từ chối tính NAV**. Với MBB hôm nay lệch **20,0%**
⇒ **NAV 08-11 sẽ bị chặn hẳn**. Sau bản vá, hai nguồn khớp 0,0% ⇒ cổng thông và NAV tính được.

Nghĩa là: một đường code hoàn toàn độc lập, viết bởi người khác, đã chọn `positions.marketPrice`
làm chân lý cho đúng tình huống này. Bản vá làm `dnse_close_prices` đồng ý với nó — **và cổng 5%
vẫn nguyên vẹn** (có test khẳng định), giờ nó canh phân kỳ thật sự bất thường thay vì bắn mỗi
ex-date.

---

## 4. Kết quả đối soát — khớp từng đồng

| | app DNSE (user chụp) | `compute_active_nav.py` sau vá | Trước vá |
|---|---|---|---|
| Cổ phiếu | 663.638.000 | **663.638.000** ✓ | 668.651.250 |
| Tiền | 305.627.008 | **305.627.008** ✓ | — |
| **Tài sản ròng** | **969.265.008** | **969.265.008** ✓ | 974.278.258 |

Đối soát độc lập thứ hai (đường đi khác hẳn): `Σ openQuantity × marketPrice` tính thẳng từ
`dnse_raw_2026-08-11.jsonl` = **663.638.000** (SpaceX) và **797.280.850** (ZaloPay) — khớp tuyệt đối
cả hai account với output của script.

Sổ lô sau vá: **SpaceX 21/21 mã KHỚP**, **ZaloPay 17/17 mã KHỚP**, 0 ticker UNVERIFIED.

---

## 5. `BLOCKED_RECONCILE` — đã gỡ (tự động, không có cờ tay nào)

Cổng chặn đọc `reconcile.ok` tính LIVE mỗi lần chạy, không phải một flag lưu đâu đó. Sổ khớp broker
⇒ chặn tự tan. Xác nhận bằng cách chạy thật cả 4 tổ hợp:

| Account | L1 `compute_park_trim` | L2 `compute_jit_unpark` |
|---|---|---|
| SpaceX | `NO_TRIM` | `NO_TRIGGER` |
| ZaloPay | `NO_TRIM` | `NO_TRIGGER` |

(trước: `BLOCKED_RECONCILE`). `NO_TRIGGER` ở L2 là đúng thiết kế — plan hôm nay chỉ có lệnh
DISCRETIONARY_SPECIAL (TV1/DRI), không có lệnh mua book BAL/LAG, nên L2 no-op.

**Không đụng vào `plan_SpaceX_2026-08-11.json` / `plan_ZaloPay_2026-08-11.json`** (yêu cầu mục 7).
Cả hai script L1/L2 là CHỈ ĐỌC; output ghi ra `/tmp` khi kiểm.

### Lưu ý an toàn đã kiểm, không phải giả định
`tradeQuantity` (bán được) vẫn giữ số **CŨ** (SpaceX 1.100, ZaloPay 202) trong khi `openQuantity` đã
là 1.265/232 — cổ phiếu thưởng chưa về tài khoản giao dịch, giống hệt ca VHM. Đã kiểm:
`compute_park_trim.py:499` và `compute_jit_unpark.py:216` đều `min(..., sellable)` ⇒ **không thể**
sinh lệnh bán vượt phần bán được. Không cần vá gì thêm.

---

## 6. Kiểm chứng

**12/12 file selfcheck PASS trên 3 môi trường TZ** (`Asia/Ho_Chi_Minh` / `env -u TZ` /
`America/New_York`) — §16 + skill `verify-before-done`:

`corp_action_selfcheck` 70/70 (từ 56, +14 ca mới) · `exrights_price_basis_selfcheck` **29/29
(MỚI)** · `verify_account_snapshot_corp_action` 12/12 · `compute_active_nav` ALL PASS ·
`compute_park_trim` 63/63 · `compute_jit_unpark` ALL PASS (ma trận TZ) · `nav_scripts_2account`
PASS · `nav_cum_dividend` 38/38 · `money_path_freshness` ALL PASS ·
`verify_account_snapshot_lot_reset` 25/25 · `preflight_order_invariants` 9/9 ·
`excluded_tickers` PASS.

Phạm vi quét (§23): `verify_account_snapshot.py` là **module lõi dùng chung của money path**
(3 consumer: `compute_active_nav`, `daily_nav_snapshot`, chính nó) nên quét rộng là bắt buộc, không
phải phản xạ.

`exrights_price_basis_selfcheck.py` cố ý viết theo lối **có ca chứng minh ngược**: mỗi khẳng định
"vá chặn được" đi kèm một ca "bỏ vá thì thật sự hỏng" (mục [9]: cổng 5% chặn NAV khi không vá).
Fixture đóng băng từ bản đọc thật 08-11, **không assert lên trạng thái sống** (§23 hệ luận 1).

---

## 7. Việc còn mở

1. **`verify_against_bq` cho MBB sẽ báo MISMATCH và ĐÓ LÀ ĐÚNG.** Hàm đó suy hệ số SỐ LƯỢNG từ cú
   nhảy tỉ số GIÁ — chỉ hợp lệ khi sự kiện thuần cổ tức CP/chia tách. MBB có quyền mua đi kèm nên
   hệ số giá (24.250/20.200 = **1,2005**) ≠ hệ số số lượng (**1,15**). Chạy sau BQ sync đêm 08-11
   để có số, nhưng **đọc MISMATCH là "công cụ không áp dụng được", không phải "sự kiện sai"**. Đã
   ghi rõ trong `verify_against_bq` của record. *Việc nên làm về sau: cho record khai thêm
   `price_adj_factor` để hàm verify so đúng thứ nó đo được.*

2. **Quyền mua 10:1 @10.000đ — QUYẾT ĐỊNH VỐN, cần user.** Không thuộc `corp_actions.json` (file
   đó chỉ mô tả sự kiện TỰ ĐỘNG tăng số lượng). Thời gian chuyển nhượng quyền **18–26/08/2026**.
   Quy mô: SpaceX ~126 quyền ≈ **1,26tr đồng**, ZaloPay ~23 quyền ≈ **0,23tr đồng** — nhỏ, nhưng
   không thực hiện thì bị pha loãng. **Cần user quyết trước 26/08.**

3. **`_status` mới `CONFIRMED` bởi agent, CHƯA có chữ ký user** (`decided_by: "agent"`, §20) — khác
   ca VHM (user ký qua Discord). Phát hiện lúc 01:30 ICT, ngoài giờ. Bằng chứng đủ mạnh và tự nhất
   quán, nhưng **nên xin user xác nhận hậu kiểm**. Thu hồi = đổi `_status` thành `REVOKED ...`, sổ
   lô lập tức quay về số cũ.

4. **`send_plan_report_park_jit_selfcheck.py` FAIL 14/20 — CÓ TRƯỚC job này, không liên quan.** Đã
   chạy baseline trước khi sửa gì: fail y hệt. Nguyên nhân là **§23 hệ luận 1**: test assert lên
   các con số SỐNG (số mã PARK, tổng tiền) đọc từ plan/artifact thật, mà những số đó đã đổi từ khi
   viết test — ví dụ nó chờ "11 mã PARK tổng 42,0tr" nhưng artifact hiện tại là số khác. Report vẫn
   render đủ các mục. **Cần đóng băng fixture**; không nằm trong phạm vi job này nên tôi không sửa.

---

## 8. Bài học đáng đẩy lên `coding_guidelines`

**Giá và số lượng phải đến từ CÙNG MỘT THỜI ĐIỂM.** §6 hiện lo "số này lấy từ nguồn có thẩm quyền
chưa" và §25 lo "'tiền' là câu hỏi nào" — chưa có mục nào lo "hai vế của một phép nhân có cùng
vintage không". Cả hai bug trong job này, và cả bug 2026-07-06, đều là cùng một hình dạng: mỗi vế
đúng riêng lẻ, tích thì sai.

Quy tắc đề xuất: *bất kỳ chỗ nào nhân `qty × price`, phải khai được cả hai vế thuộc phiên nào; nếu
không khai được thì đó là dấu hiệu thiếu tham số, không phải lý do bỏ qua.* Cơ chế cưỡng chế đã có
sẵn và rẻ — cổng `PRICE_XCHECK_TOLERANCE_PCT` của `daily_nav_snapshot.py` chính là hình mẫu: đối
chiếu chéo với `positions.marketPrice` (nguồn duy nhất broker công bố mà qty và price luôn cùng
vintage theo định nghĩa).

Chưa ghi vào `coding_guidelines.md` — theo §13 sẽ ra `.proposed` nếu Mike thấy đáng.
