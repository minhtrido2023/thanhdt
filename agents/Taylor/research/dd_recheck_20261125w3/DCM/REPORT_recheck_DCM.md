# DCM — Rà lại DD theo luật B5 + E15/E16/E17 (đợt 3, 25/11/2026, job Taylor_20261125_032448)

Bản rà lại **REPORT_rev9** (`agents/Taylor/research/dd_DCM_20261104/REPORT_rev9.md`, md5 `01ef1894…`, 23/11). **Không làm lại mô hình**: `calc/model_r9.py` (md5 `615c950a…`, khoá `calc/LOCK_r9_md5.txt`) + `assumptions_r9.json` (md5 `a12917ea454b449b000bf660af2f929c`) còn nguyên trong git (không bị TRIM). **CONTROL:** lưới 2.430 kết cục × (1 − CK 0,585% đã khoá) = 27.392,5 ⇒ 27.393, trùng rev9 (`calc/run1.txt`).
Mù giá: không đọc giá mới. Giá 30.400 (DNSE 20/11/2026) kế thừa rev9, chỉ cho nhãn.

## 0. Kết luận

**TÂM (base, r 13,5% ±100bp trong lưới, sau chiết khấu thanh khoản 0,585%): 27.393 đ/cp — vùng P25–P75 24.385–30.479. KHÔNG ĐỔI so với rev9.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 28.941 đ/cp (+5,65% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): DCM: so với lịch sử 10 năm của chính mã — **RẺ** — phân vị [fade 30, hold 1], 120 tháng, N hiệu dụng ≈ 4.4 (thước cơ học RI-ROE5Y của chính mã, KHÔNG dùng tâm DD; chỉ hiển thị)
Tâm kỳ vọng điều chỉnh: 26.303 đ/cp (dải 24.470–27.236; −3,98% so với tâm base); căn cứ 2 hạng mục bậc B (`ADJ_CENTER.md`)

- E15: lưới có trục r 5 điểm (r ±100bp quanh 13,5%); dòng trên = dịch cả trục về tâm 12,3% (giữ độ rộng ±100bp). r cố định 12,3% không trục: 28.881 (+5,43%).
- **Nhãn** (giá 30.400, DNSE 20/11/2026, kế thừa rev9): TRONG vùng P10–P90 (22.065–32.564), +11,0% so tâm; luật 4 (0,85 × 27.393 = 23.284) KHÔNG đạt. Không đổi so với rev9.
- Điểm tham số trung tâm trước CK (center_alt, kế thừa rev9): 27.387 đ/cp.
- **Tâm đổi 0%, nhãn không đổi** ⇒ phần luật mới là cơ học (MECH).
- **Bước 0 (tham số nền bị phủ?): KHÔNG.** (i) CK holding: không có tầng holding. (ii) r: neo 03/11 7,40%; `effective_deposit_rate('2026-11-25')` = 7,40% (`cctg_12m(2026-11-02)`) ⇒ Δ = 0, r 13,5% (tâm trục). (iii) RONIC terminal = Ke, g thực = 0 (rev9 §7, NARROW). (iv) Độ nhạy r tính từ mô hình (rev9 §4), tái lập cùng cơ sở sổ ở §2.
- **Phản biện:** KHÔNG chạy vòng mới. skeptic r4 (23/11, `dd_DCM_20261104/skeptic/r4.json`, **DD_GENERAL**, INCONCLUSIVE medium, report_md5 `01ef1894…` khớp) đã chấm đúng mô hình/tâm này, là vòng 3 cuối (user duyệt 17:03 23/11) ⇒ §E14 DỪNG, giữ REFUTED_OPEN; hạng mục r4 xử lý bằng E17.

## 1. Thay đổi so với rev9
| # | Luật | rev9 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | E15 | Ke 12,3% chỉ ở điểm trước CK (+1.535) | Dòng E15 ở §0 trên lưới sau CK | 0 |
| 2 | E16 | Chưa có | Dòng E16 nguyên văn (asof 2026-11-20; `calc/dd_history_label_DCM_2026-11-20.*`) | 0 |
| 3 | E17 | Chưa có | `ADJ_CENTER.md` (tâm adj 26.303) | 0 (không thay tâm base) |
| 4 | Đính chính công bố mù giá (skeptic r4) | "giá biết từ pha rev7" | Giá đã biết từ r5 (33.000) / r6 (32.100) — sửa câu công bố, không đổi số | 0 |

## 2. Soát luật B5 (D3/D4/V1–V8)
- **D4:** RONIC = Ke, g thực 0 — đạt. **D3:** quỹ KH&CN không phải capex tuân thủ thuần (DN chọn trích; không chi thì bị thu hồi kèm thuế + lãi — đúng quy tắc v của rev9); phần chi bắt buộc cho KH&CN không thành TSCĐ là rủi ro "chi không tạo doanh thu" ⇒ xử lý ở E17 D1 (bậc B, số TM25). Capex duy trì M 342/401/540 trong base. **V1:** r 13,5% (trục ±100bp), Δ 0; cùng cơ sở sổ (lưới sau CK, dịch trục r theo lãi huy động β1): −100bp 28.661 (+4,63%) · −50bp 28.001 (+2,22%) · +50bp 26.830 (−2,06%) · +100bp 26.307 (−3,96%); dải Ke 12,3–13,4% (rev9 §4). **V3:** CK 0,585% @5 tỷ (ADV 89 tỷ). **V5:** NARROW · COST/LOCATION (ADDENDUM_5F 07–08/11). **V6:** D = 2,53 > ln3 "phân kỳ mạnh" (vốn lưu động 2025 + capex tăng trưởng), đã giải thích, luật 0,85×tâm không tự kích hoạt. **V8:** hiện 0%; nếu giá ≤ 23.284 xét tranche 2% NAV chờ user. ⇒ **đã đủ** ở rev9, chỉ thiếu E15/E16/E17.

## 3. Hạng mục skeptic r4 — trạng thái
| Hạng mục r4 | Hướng | Xử lý |
|---|---|---|
| Quỹ KH&CN: hoàn nhập cho DN không phải DNNN chưa kiểm; chi bắt buộc = dòng tiền ra (tới −8,7%) | ↓ | E17 D1 bậc B: phần chi KH&CN không thành TSCĐ (38,7% số trích 2024–25, TM25) giá trị 0; phần "mất trắng cả quỹ" (rev7, −8,70%) = độ nhạy C |
| Hồi quy đoán cao 2024–25 (skeptic ước −4,5%) | ↓ | E17 D2 bậc B: chạy mô hình, dịch tung độ gốc mỗi cửa sổ bằng phần dư TB 2024–25 ⇒ −6,72% |
| Hạn thuê đất Cà Mau chưa kiểm (−3,6…−6,8%) | ↓ | C — độ nhạy |
| Giá khí 2035+ 100% công thức Đ9.1 (biến thể có trọng số −17,59%) | ↓ | C — trọng số trục là giả định, không có dữ liệu xác suất; độ nhạy |
| 332 tỷ phong toả MBV (−2,3%) | ↓ | C — độ nhạy |
| 4 cửa sổ hồi quy (+7,34%), thuế XK 0% P=0,55 (+3,76%) | ↑ | độ nhạy (lựa chọn đặc tả / chính sách chưa có dữ liệu xác suất); 4 cửa sổ còn ngược chiều với D2 |

## 4. WARNING (giữ rev9 §9)
HĐ khí bên liên quan khép kín PVN → PV GAS → DCM; SĐBS 12 dự thảo; 332 tỷ hạn chế tại MBV; phải thu PVN tăng; sau 24/4/2032 không còn khối lượng cam kết. Pháp lý chỉ WARNING.
