# HHS — Tâm kỳ vọng điều chỉnh, DẠNG HIỂN THỊ (24/11/2026, job Taylor_20261124_110052, nhóm g2)

> **Display-only.** Dựng theo dải CK holding **0 … +20%** user đã chốt ngày 24/11 (`kb/projects/ck-hhs-reference-range-20261124.md`). Đây KHÔNG phải rev mới. Không ghi `dd_price_zones.json`, không email, không wire.

- Phương pháp: `../PREREG_adj.md` (md5 `ef5157cb…`) + `../PREREG_adj_v2.md` (md5 `835dfc1e…`), cả hai assert trong `calc_adj.py`.
- Chạy 2 lần: run1 = run2 (md5 `764be80d…`).
- Lõi tính: dùng lại `hhs_r3.py` + `dilution_out.json` + assumptions rev7, đều khoá md5, giống `dd_recheck_20261124/HHS/calc/calc_recheck.py`.
- **CONTROL:** ở CK 26,63% tái lập đúng tâm sổ rev8 là 10.805, và EX 9.767 / 8.846.
- Mù giá: lưới không đọc giá. Bỏ qua mọi nhãn và mọi mức giá trong báo cáo gốc.

## Kết luận
| Dòng | CK +20% (mốc hiện tại, **tâm adj**) | CK 0% (đầu lạc quan, **cận trên**) | Sổ rev8 (CK 26,63%, N = 6) |
|---|---|---|---|
| **CUM (có quyền)** | **11.593** (P10 10.322 – P90 12.876) | 13.969 (P10 12.422 – P90 15.564) | 10.805 |
| **EX (sau quyền 5:3 @10.000 + CP 7%, k = 1)** | **10.227** | 11.615 | 9.767 |
| EX, k = 1 − CK (cách rev7, chỉ để đối chiếu) | 9.536 | 11.615 | 8.846 |

**Tâm kỳ vọng điều chỉnh (CUM): 11.593 đ/cp (+7,29% so với 10.805). Dải hiển thị: 11.593 – 13.969.**
- Còn quyền: lấy ý kiến cổ đông theo NQ 10/NQ-HĐQT từ 14 đến 25/12/2026. Sau GDKHQ dùng dòng EX: **10.227**.
- Toàn bộ thay đổi so với sổ đến từ **tham số CK do user chốt**: 26,63% → +20%. Đây là đổi nền tính, không phải hạng mục bằng chứng.
- **Σ p × m = 0.** Không có hạng mục nào đạt bậc A/B/C+. Lý do cho từng hạng mục ở §2.
- Tâm adj đặt ở mốc **+20%**, vì đây là số đo hiện tại (khoảng đo 15–23%). Mốc **0%** là đầu lạc quan, user ghi rõ "không phải tâm đo được". Đặt tâm ở giữa dải sẽ là thưởng cho đầu lạc quan mà không có số đo nào đứng sau.
- Mỗi +1pp CK làm tâm thay đổi −119 đ/cp. Quan hệ tuyến tính trong dải.

## 1. Hạng mục vào tâm (A/B/C+)
Không có hạng mục nào. Σ = 0.

**Sửa cơ học EX: k = 1.** File giả định khoá ghi `k_base = 1,0`, nhưng rev7 dùng 0,734; skeptic r5 và r1 đã chỉ ra điểm lệch này. Sửa lại chỉ ảnh hưởng dòng EX. Dòng CUM không đổi, và Σ cũng không đổi.

## 2. Chỉ độ nhạy (C / luật / pháp lý) — KHÔNG vào tâm
| Hạng mục | Hướng | Độ nhạy | Vì sao không vào tâm |
|---|---|---|---|
| Chi phí hoàn thiện NC-II (G10), phần không sinh biên | ↓ | rev5 ở CK 0%: −351 / −702 / −1.403 (5% / 10% / 20% giá gốc HTK). Quy về CK 20% (×0,8, ước lượng): −281 / −562 / −1.122 | Chi phí phải trả 30/9 chỉ 28,1 tỷ. Errata r3: nếu biên 52% tính trên tổng chi phí thì phần hoàn thiện vẫn sinh biên ⇒ chưa chắc dấu ⇒ C |
| Nghĩa vụ NƠXH / quỹ đất NC-II, I.14 + KL 08/KL-TTTP | ↓ | chưa có số | Thường đã nằm trong tổng mức đầu tư ⇒ cận = 0 ⇒ C |
| Cơ cấu cao tầng HH1–HH4 | ↓ | −2,3 … −9,0% | Đã nằm trong trục ds ±15pp của lưới; đưa thêm vào là đếm hai lần |
| CK thanh khoản 1,41% @ 5 tỷ (= 48% ADV60) | ↓ | có thể thấp | Tham số luật V3 |
| [LUẬT] r vs dải Ke (E15), tính ở CK 20% | ↑ | Ke 12,3%: 11.821 (+1,97%); 13,4%: 11.611 | Tham số luật V1 |
| [LUẬT] P/E ô tô 6 < 1/Ke = 7,4 | ↑ | ≈ +1% (skeptic) | Luật RONIC = Ke |
| TB 2124/TB-TTCP (thu hồi 7,87 tỷ); KL 08 | ↓ | ≤ 0,2% | Pháp lý chỉ là WARNING |
| Rò dòng tiền qua 2 tầng holding | ↓ | — | Đã nằm trong CK holding; tính riêng là đếm hai lần |

## 3. Không đếm hai lần
- CK holding đã gồm phần rò dòng tiền qua holding. Không trừ thêm.
- HH1–HH4 đã nằm trong trục ds.
- r, dải Ke và E15 gộp thành một dòng luật.
- Pha loãng (quyền mua + cổ tức CP) xử lý cơ học ở dòng EX, không vào Σ.

## 4. BẢNG ĐIỀU KIỆN ĐỔI SỐ
Δ tính trên tâm adj 11.593.

| Sự kiện / dữ kiện | Khi nào | Đổi gì | Δ (đ/cp) | Δ % |
|---|---|---|---|---|
| Lấy ý kiến cổ đông NQ 10 (14–25/12/2026) giữ quyền 5:3 @10.000 + CP 7% | cuối 12/2026 | Sau GDKHQ dùng dòng EX (k = 1). Nếu đổi giá chào hoặc quy mô ⇒ tính lại EX | −1.366 (pha loãng cơ học/cp) | −11,78 |
| NQ 10 huỷ hoặc hoãn phát hành | cuối 12/2026 | Giữ dòng CUM | 0 | 0 |
| Đo lại CK holding (quét v5 định kỳ) | hằng quý | Chỉ hiển thị; dải chỉ đổi khi user chốt lại | −119 mỗi +1pp | −1,10 mỗi pp |
| HHS nhận cổ tức tiền từ CRV | khi công bố | Bằng chứng chống CK cao ⇒ nghiêng về đầu 0% | tối đa +2.376 | tối đa +20,5 |
| Công bố dự toán hoàn thiện NC-II/HH1–HH4 (G10) | BCTN 2026 / CBTT | C → A | −562 mỗi 10% giá gốc HTK không sinh biên (ước lượng) | −5,2 |
| BCTC kiểm toán NĐL cho thấy BV < 10.000 | ước lượng 03/2027 | Dòng EX dùng k đo được (k < 1) | k = 0,8 ⇒ EX 9.536 | −6,8 (so EX k = 1) |
| Có số liệu NƠXH / KL 08 thu hồi | khi có | C → A, trừ theo đ/cp; phần pháp lý chỉ WARNING | theo số | — |
| Lãi huy động 12T ±50bp (V1) | liên tục | r | +50bp: −92 / −50bp: +94 | ∓0,8 |

Kịch bản gộp (chỉ minh hoạ, KHÔNG phải tâm):
- Có pha loãng + G10 10% không sinh biên ⇒ EX ≈ 10.227 − 562 × (EX/CUM ≈ 0,88) ≈ 9.73x.
- Chiều lên: CRV chi cổ tức tiền + CK về 0% ⇒ CUM 13.969 / EX 11.615.
