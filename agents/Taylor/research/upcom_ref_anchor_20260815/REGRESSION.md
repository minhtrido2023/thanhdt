# PHẦN 3 — Hồi quy: bug này LỚN TỚI ĐÂU trong thực tế

Job `Taylor_20260815_034407` · script `regress_ceiling_old_vs_new.py` · dữ liệu
`regression_ceiling.json`

Chỉ đạo gọi đây là *"con số quan trọng nhất — nó cho biết bug này lớn tới đâu trong thực tế
(không phải lý thuyết)"*. Dưới đây là con số đó, kèm **giới hạn của phép đo** nói trước.

---

## 0. Phép đo này đo cái gì — và vì sao KHÔNG đo thẳng được

`q.ref` **chỉ đọc được SỐNG**; DNSE không có endpoint lịch sử (README §1.7, đã kiểm). Nên **không
thể** dựng lại trần đúng của một phiên quá khứ từ chính nguồn production.

**Vật thay thế**: bình quân gia quyền dựng lại từ **bar 1 phút nguồn VCI** (đường dữ liệu độc lập
hoàn toàn với DNSE). Đây **không phải giả định** — nó đã được đối soát trùng `q.ref` thật **6/7
mã UPCOM TỚI TỪNG TICK** (README §1.4), ca mạnh nhất là SCL tái lập sai lệch −3,36% với sai số
**0,012 điểm phần trăm**.

**Giới hạn phải đọc kèm**: (a) đối soát tick-level chỉ trên **1 phiên** (08-14), 12 tháng còn lại
suy rộng từ đó; (b) bar VCI có thể cắt đuôi phiên (ca SGP dừng 14:50 → lệch đúng 1 tick); (c) đo
trên **trần đã làm tròn về bước giá 100đ** — tức đúng cái giá đặt được trên bảng, nên phần lệch
<100đ bị nuốt và con số dưới đây là **cận DƯỚI** của sai số thật.

---

## 1. Kết quả chính — nhóm mã ĐANG trong phạm vi luật A

**DRI + SCL + TV1**, N = **777 phiên-mã**, τ = 3%:

| Chỉ tiêu | Giá trị |
|---|---:|
| median \|lệch trần\| | **0,553%** |
| p90 | **1,527%** |
| max | **9,868%** |
| % phiên lệch > 1% | **19,82%** |
| **% phiên lệch > CẢ ngân sách τ=3%** | **1,80%** |

**Đọc đúng**: median 0,553% = **18% ngân sách trần** user duyệt bị sai ngay từ cơ sở giá. p90
1,527% = **51% ngân sách**. Và **1,8% số phiên sai số còn LỚN HƠN CẢ ngân sách** — hôm đó trần
luật A hoàn toàn không mô tả thứ user nghĩ mình đã duyệt.

### Chi tiết từng mã (12 tháng)

| mã | trong phạm vi A | N | median | p90 | max | >τ=3% | max lệch VND |
|---|:--:|---:|---:|---:|---:|---:|---:|
| **DRI** | ✅ | 259 | 0,741% | 1,527% | 4,605% | 0,77% | 700đ |
| **SCL** | ✅ | 259 | 0,568% | 1,734% | **9,868%** | **3,86%** | 1.500đ |
| **TV1** | ✅ | 259 | 0,420% | 1,299% | 7,563% | 0,77% | 1.800đ |
| SGP | — | 259 | 0,463% | 1,389% | 3,781% | 0,39% | 900đ |
| ACV | — | 259 | 0,350% | 1,018% | 2,610% | 0,00% | 1.600đ |
| QNS | — | 259 | 0,211% | 0,591% | 1,392% | 0,00% | 600đ |
| TMG | — | 64 | 0,000% | 1,051% | **27,258%** | 6,25% | 16.600đ |
| **GỘP** | | **1.618** | **0,414%** | **1,270%** | 27,258% | **1,17%** | |

**SCL là ca xấu nhất trong phạm vi**: 3,86% số phiên (10/259) sai số vượt cả τ=3%. TMG (ngoài
phạm vi hiện tại, nhưng **đủ điều kiện thành ứng viên tương lai**) chạm 27,3% — thanh khoản mỏng
thì hai định nghĩa giá phân kỳ rất xa.

---

## 2. 🔴 Phát hiện quan trọng: lệch theo **HAI CHIỀU**, không phải thiên lệch một phía

| Chiều | Số phiên | Tỉ lệ | Nghĩa là gì |
|---|---:|---:|---|
| Trần cũ **CAO HƠN** trần đúng | 608 | **37,6%** | Cổng chống-đuổi bị **NỚI** ⇒ mua đắt hơn mức user duyệt — **mất tiền thật** |
| Trần cũ **THẤP HƠN** trần đúng | 527 | **32,6%** | Cổng bị **SIẾT** ⇒ lệnh có thể không đặt được dù giá còn trong ngân sách — **mất cơ hội**, đúng cái rủi ro kẹt mà luật A sinh ra để cắt |
| Bằng nhau (sau làm tròn tick) | 483 | 29,9% | — |

**Mean lệch CÓ DẤU = +0,091%** — gần 0. ⇒ Đây **KHÔNG phải một thiên lệch hệ thống có thể bù
bằng hằng số**; nó là **nhiễu hai chiều**, và cả hai chiều đều hỏng theo cách riêng. Không có
"điều chỉnh τ lên/xuống một chút" nào chữa được — chỉ đổi đúng cơ sở giá mới chữa.

Điều này cũng bác bỏ một cách đọc dễ mắc: *"trần cũ dựa trên giá đóng, mà giá đóng thường cao hơn
bình quân trong phiên tăng, nên bug này chỉ làm ta mua đắt"*. **Sai** — 32,6% số phiên nó làm
ngược lại.

---

## 3. Tác động lên 8 lệnh THẬT trong phạm vi (plan `2026-08-10`, cả 2 account)

Toàn bộ 8 lệnh có `entry_anchor_price` trong 124 plan lịch sử đều thuộc plan **08-10**:
DRI ×2, POW ×2, SCL ×2, SSI ×2. Anchor lấy từ phiên liền trước (**08-07**):

| mã | sàn | giá đóng 08-07 | tham chiếu ĐÚNG | trần CŨ | trần ĐÚNG | lệch |
|---|---|---:|---:|---:|---:|---:|
| **DRI** | UPCOM | 13.200 | 13.218 | 13.500 | 13.600 | **−100đ (−0,74%)** ⇒ siết oan |
| **SCL** | UPCOM | 24.200 | 24.275 | 24.900 | 25.000 | **−100đ (−0,40%)** ⇒ siết oan |
| POW | HOSE | — | = giá đóng | — | — | **0đ** (HOSE không ảnh hưởng) |
| SSI | HOSE | — | = giá đóng | — | — | **0đ** ngày đó |

⚠️ **Nhưng luật A CHƯA từng áp cho plan thật nào** (commit `2db6d37` tuyên bố vậy, và selfcheck
`H2` xác nhận lại bằng máy: 0 lệnh luật A trong kho plan hiện tại). ⇒ **Bug này chưa gây thiệt
hại tiền thật.** Nó được bắt **trước** khi cơ chế đi vào LIVE — đó là kết quả tốt nhất có thể của
chuỗi việc này, và là lý do con số ở §1 mới là con số đáng lo, không phải §3.

### Ca đáng chú ý nhất: SCL phiên 08-14
| | |
|---|---:|
| giá đóng | 23.700đ |
| tham chiếu ĐÚNG | 22.903đ |
| trần CŨ | 24.400đ |
| trần ĐÚNG | 23.500đ |
| **lệch** | **+900đ (+3,83%)** |

Một plan lập cho phiên kế tiếp dùng anchor 08-14 sẽ có trần **cao hơn 3,83%** — **vượt CẢ ngân
sách τ=3%**. Toàn bộ tác dụng chống-đuổi của luật A bốc hơi trong đúng phiên đó, im lặng.

---

## 4. 🔴 Ca SSI ex-right 2026-08-17 — lỗi lớn hơn, KHÔNG giới hạn UPCOM

Không đo được bằng phân bố (n=1, sự kiện rời rạc) nên báo riêng bằng số học:

| | |
|---|---:|
| giá đóng phiên trước | 24.500đ |
| tham chiếu chính thức (thưởng CP 20% + cổ tức 1.000đ) | **19.600đ** |
| trần luật A theo cơ sở CŨ | 25.235đ |
| **GIÁ TRẦN hợp lệ của phiên (19.600 × 1,07)** | **20.972đ** |

Trần luật A nằm **cao hơn cả giá trần sàn cho phép 20,3%** ⇒ `min()` không bao giờ chạm tới nó ⇒
**luật A không tồn tại trong phiên đó**, và không log nào nói điều đó.

Ba nguồn độc lập khớp số học tuyệt đối: `tav2_bq.corporate_action`, tính tay theo công thức điều
chỉnh, và DNSE `q.ref` sống — cả ba ra **19.600**.

**Cắn mọi sàn, và cắn ngay thứ Hai tới.** Bản vá xử lý bằng cách BỎ QUA luật A đúng ngày GDKHQ
(`fetch_exright_on`) — giới hạn phạm vi có chủ đích, xem `FIX.md` §5 mục 1.

---

## 5. Hồi quy an toàn — bản vá KHÔNG làm hỏng cái đang chạy

| Phép kiểm | Kết quả |
|---|---|
| 96 plan LIVE nạp lại, 23 lệnh mua có trần | **0 lệnh đổi giá trị** |
| 68 plan LIVE, 312 lệnh mua — lệnh NGOÀI luật A bị cổng mới động tới | **0** |
| Lệnh luật A trong kho plan hiện tại | **0** ⇒ hành vi LIVE hôm nay KHÔNG đổi |
| Selfcheck trong scope map (§23, quét rộng vì chạm module lõi) | **25/25 PASS** |
| 4 bộ nhạy ngày × 4 môi trường TZ đối kháng | **PASS đồng nhất** |

---

## 6. Kết luận

1. **Đây là BUG THẬT, không phải trade-off chính sách.** Khác hẳn phần "Rule A vs Rule B" trước
   đó (đánh đổi chính sách, không có bằng chứng thống kê): ở đây anchor **không phải đại lượng
   user đã chỉ định**, và sai đó đo được — median **0,553%**, p90 **1,527%**, **1,8%** số phiên
   vượt cả ngân sách τ.
2. **Chưa gây thiệt hại tiền thật** — luật A chưa từng áp cho plan LIVE nào. Bắt được trước khi
   đi vào production.
3. **Sai theo HAI chiều** (37,6% nới / 32,6% siết, mean có dấu ≈ 0) ⇒ không bù được bằng hằng số,
   phải sửa đúng cơ sở giá.
4. **Lỗi GDKHQ nghiêm trọng hơn lỗi UPCOM** về độ lớn (SSI: 25,0% chênh cơ sở giá, đủ để vô hiệu
   hoá luật A hoàn toàn) và **không giới hạn ở UPCOM**.
5. **Việc còn lại đã công bố** (`FIX.md` §5): đường sizing ngày GDKHQ, bước giá theo `market_id`,
   và xác nhận trên phiên LIVE thật.
