# PAT — Định giá r3 (mù giá thị trường), 17/11/2026

## KẾT LUẬN ĐẦU
- **Tâm r3 = 66.900 đ/cp** (cây 3.024 lá: 66.864; đường cơ sở với đầu vào kỳ vọng: 66.850).
- **Khoảng:** P25–P75 = **48.900 – 80.000** · P10–P90 = **36.700 – 99.100** · trung vị 67.800.
- **Bắc cầu r2 → r3** (r2 = 64.736, chạy lại khớp; cộng dồn, đ/cp):

| Bước | Giá trị | Đóng góp |
|---|---|---|
| r2 (chạy lại) | 64.736 | |
| (1) TX: P(15% hiệu lực 01/01/2027) 0,90 → 0,97 — dự thảo r2 chưa đọc được nay đã biết là KHÔNG có P4 (A2 §a2) | 63.229 | **−1.507** |
| (2) Điện: mức cắt cho nhóm sản xuất 2% → 1,5% (phân bổ của EVN: nhóm sản xuất ≈ 0,727 × mức bình quân, A3 §1.3) | 62.548 | **−681** |
| (3a) Nút O, phần thời gian: λ chính xác (0,523 thay vì làm tròn 0,55), H2/2027 lấy xác suất tích luỹ tại thời điểm đó thay vì mượn trạng thái 2028, A coi là kết cục pháp lý nhị phân | 61.994 | **−554** |
| (3b) Nút O, phần nhất quán: B (cung quặng nhà nước) giữ hazard hằng cả sau 2028, thay vì cắt tại 01/2028 rồi gán "vĩnh viễn" | 66.864 | **+4.871** |
| **Tổng r2 → r3** | | **+2.128 (+3,3%)** |

  Từng thay đổi gỡ riêng khỏi r3 cho cùng đóng góp: −1.507 / −681 / +4.871 (bước (3a)+(3b) gộp).
- **Điểm kém chắc nhất (theo thứ tự):** (1) **giá DLC trả PAT** (nút T và chiết khấu chuyển giá): 63,7% doanh thu 9T/26 và 85,5% Q3 bán cho DLC, mà nguyên tắc giá thì không tìm được. Riêng biến này đi từ 50.700 (DLC trả thấp hơn netback 5%) tới 83.400 (s_eff 0,135). (2) **Mức giá thực hiện**: ±5% giá ⇒ ±24.800/cp, vì biên mỏng (GPM dài hạn kỳ vọng 12,7–13,7%). Ánh xạ nhánh giữa của nút P là chỗ yếu đã biết: nếu ánh xạ tuyến tính thì còn 60.200. (3) **Lựa chọn hazard cho B**: nếu cắt tại 2028 như r2 thì 62.000; nếu có khối vĩnh viễn 0,25 thì 64.000.
- **Độ tin cậy:** thấp–trung bình. Tâm vững với bằng chứng 17/11: không thay đổi nào vượt ±5.000. Còn khoảng giá trị thì rộng, và độ rộng đó do **2 ẩn số không quan sát được** (giá chuyển nhượng, giá thực hiện/tấn) quyết định, chứ không do quặng hay thuế.

## 1. Khẳng định của user → mô hình làm gì (chỉ phần chạm định giá)
- **#4 "Hàn, Đài, Nhật không bị thuế 15%":** chỉ đúng với Nhật (CPTPP 0% từ 2025), EU thì 0% từ 2027. Hàn và Đài chịu MFN (A2 §b). Bản thân PAT chịu đủ MFN: thuế 10,59% trên doanh thu nước ngoài 9T/26 (A2 §d) ⇒ **không mở thêm kênh giảm thuế nào cho PAT**. Nút T giữ nguyên. Riêng thông tin FTA chỉ nâng CẬN TRÊN: DLC giữ khách Nhật/EU nên có dư địa chia lợi (độ nhạy s_eff 0,785 ⇒ 64.800). Thuế 15% gần chắc chắn (TX 0,97).
- **#2 "Điện giảm 2%":** đúng ở mức bình quân. Với nhóm sản xuất mức giảm ≈ 1,5%, tác động −681/cp so với r2. Nguyên nhân là r2 đã tính dư lợi ích, không phải điện xấu đi. Toàn bộ kỳ vọng điện (cả F5) chỉ đáng khoảng ±3.000/cp.
- **#2 "Chi phí tăng chuyển được cho khách":** truyền dẫn có ở Q2 nhưng không có ở Q1 và Q3 (A3 §3.2). Nút P giữ nguyên ±6,3%. Độ nhạy biên độ ±10% ⇒ 62.800.
- **#3 "Quặng đã thông suốt; chưa có cơ sở nói LN lõi 2027 < 2026":** đến 17/11 chưa mỏ nào mở lại. Nguồn Ai Cập chỉ đảm bảo tới hết Q1/2027, UBND tỉnh ghi nhận PAT thiếu nguyên liệu (A1 §B, §C2, §C5). Base giữ nguyên khối lượng (WARNING; −15%/−30% sản lượng H2/2027 ⇒ −600/−1.200). **Cầu EBIT 9T/26 quy năm → E[EBIT 2027]** (`calc_r3/ebit_2026_2027.py`): 283 (khung mô hình; 2026E thực ≈ 259) → bước thuế 10→15% **−73** → cốc 9T ≈ 1.700 → 2.108 **−35** → quặng (H1/27 vẫn GĐ2, H2 theo xác suất) **−39** → điện −4 → giá kỳ vọng −24 ⇒ **109**. Hai cấu phần lớn nhất (thuế, cốc) có văn bản/dữ liệu và không phụ thuộc chuyện quặng thông hay tắc. Nếu quặng giải ngay đầu 2027, chỉ thu lại được khoảng 39 trong 174. ⇒ Cơ sở cho "LN lõi 2027 thấp hơn 2026" là có, trong khung giả định netback (T_a). Nếu DLC gánh thuế (T_b/T_c) thì bước thuế co lại còn 35%/13,5%.
- **#1 "Đáy Q2–Q3 rồi tốt dần":** với PAT, Q2/26 là quý TỐT NHẤT (GPM 25%), đáy là Q1 (13,6%) và Q3 (14,5%) (A1 §D1). Mô hình không dùng giả thuyết đường phục hồi. Từ H2/2027 trở đi chi phí giảm theo xác suất giải quặng (E[NVL/DT]: 2027 54,8% → 2028 51,5% → 2030 50,8% → dài hạn 50,6%).

## 2. Phân phối và các nút (cây r3)
| Nút | Nhánh: xác suất → giá trị có điều kiện (đ/cp) |
|---|---|
| T | T_a 0,65 → 59.500 · T_b 0,25 → 77.600 · T_c 0,10 → 87.900 |
| P | 0,937: 0,32 → 42.200 · 1,0: 0,58 → 73.800 · 1,063: 0,10 → 105.500 |
| TX | 15%: 0,97 → 66.200 · 10%: 0,03 → 87.800 |
| A (mỏ DGC) | giải H2/2027: 0,5 → 74.000 · không bao giờ: 0,5 → 59.800 |
| D (nguyên nhân quyết định chi phí) | A: 0,5 → 62.500 · B: 0,5 → 71.200 |
| Thời điểm B | trước giữa 2027: 0,337 → 68.100 · H2/27: 0,186 → 67.800 · 2028: 0,230 → 66.900 · 2029–30: 0,181 → 65.200 · 2031+: 0,066 → 62.500 |

Cơ sở (đầu vào kỳ vọng): EBIT 2027 = 108,9 · EBIT 2028 = 169,4 (GPM 12,7%) · EBIT dài hạn (2045, giá 2028) = 185,8 (GPM 13,7%) · tiền ròng 357,4 · PV dòng tiền 2027–2045 = 1.149,9 · PV terminal = 164,0. Tỷ trọng terminal chỉ 9,8% vì chuỗi tường minh đã kéo tới 2045, nên không so trực tiếp được với con số 34% của r2. Ở khung cũ (Gordon tại 2033) phép tính tương đương toán học; kiểm bằng bước 0'.

**Đối chiếu chu kỳ biên gộp 15 kỳ (kiểm, không phải đầu vào):** quy GPM lịch sử về nền thuế 15% theo netback, GPM15 = 1 − (1 − GPM)·(1 − thuế cũ)/0,85. Trung vị 15 kỳ là 14,7%; các kỳ 2023–Q3/26 có trung vị 12,7%, TB 12,6%. GPM dài hạn kỳ vọng của r3 (12,7% năm 2028 → 13,7% dài hạn) nằm giữa hai mốc này. Dài hạn hơi cao hơn chế độ 2023+ do nền giá 9T/26 cao hơn 2023–25, phần này nút P đã xử lý.

## 3. Độ nhạy (danh sách khoá §4; đường cơ sở 66.850 trừ khi ghi "cây")
| Trục | Giá trị (đ/cp) |
|---|---|
| r 12,5 / 13,0 / 13,5 / 14,0 / 14,5% (g = 2%) | 71.500 / 69.100 / 66.850 / 64.800 / 62.900 |
| g 0 / 1 / 2 / 3% (r = 13,5%) | 60.100 / 63.200 / 66.850 / 71.200 |
| EBIT dài hạn ×0,8 / 0,9 / 1,1 / 1,2 | 57.400 / 62.100 / 71.600 / 76.300 |
| giá ×0,90 / 0,95 / 1,05 / 1,10 | 17.300 / 42.100 / 91.600 / 116.400 |
| s_eff 0,135 / 0,35 / 0,75 / 0,785 / 1,0 | 83.400 / 77.300 / 65.800 / 64.800 / 58.700 |
| DLC trả dưới netback −5% trên 65% DT | 50.700 |
| thuế giữ 10% chắc chắn / TX về 0,90 (cây) | 87.300 / 68.400 |
| P biên độ ±10% (cây) / nhánh giữa 0,977 (cây) | 62.800 / 60.200 |
| O: B cắt 2028 vĩnh viễn (= r2) / khối vĩnh viễn q_B 0,25 (cây) | 62.000 / 64.000 |
| P(A) 0,3 / 0,7 (cây); A giải muộn 01/2029 (cây) | 64.000 / 69.700; 66.000 |
| O cố định: chưa giải mãi / O2 từ H2/27 / O1 từ 2028 | 50.300 / 71.400 / 79.900 |
| điện cắt 0,98 (cây) / 0,985 bỏ F5 | 67.500 / 69.900 |
| sản lượng H2/2027 −15% / −30% | 66.200 / 65.600 |
| một lần −50 / mất cầm cố −42,6 / 70 tỷ theo mệnh giá | 64.900 / 65.100 / 68.700 |

## 4. Điều cần theo dõi và mốc xác minh
1. **Nguyên tắc giá DLC ↔ PAT** (biến số 1): tờ trình GD bên liên quan ĐHĐCĐ 2027 của PAT; tỷ trọng bán DLC và GPM Q4/26 so với Q3. Tín hiệu bất lợi: GPM tiếp tục ≤ 15% trong khi P4 sunsirs ≥ 28.000 ⇒ nghiêng về "dưới netback".
2. **Tỷ lệ thuế XNK/DT nước ngoài 2027** (BCTC Q1/2027): ≈ 15% ⇒ khớp không-ưu-đãi; thấp hơn đáng kể ⇒ PAT có khách Nhật/EU (nâng s thực).
3. **Văn bản thuế XK P4 trước/đúng 01/01/2027** (TX).
4. **Quặng:** quyết định cho phép KT25/19B hoặc thu hồi/không gia hạn giấy phép KT25 (mốc ~31/12/2026 – đầu 2027) ⇒ đổi nút A. **Bobby F7 ngày 31/05/2027** (3 nhà máy tuyển ≥80%; quyết định dùng 3,53 tr t) ⇒ chấm hazard B. Hợp đồng quặng nhập sau Q1/2027 ⇒ rủi ro khối lượng.
5. **BCTC Q4/2026:** KH ngụ ý LNST Q4 ≈ 64 (≈ Q3). Thấp hơn rõ ⇒ xem lại Q4 FCFE và cơ sở 2027.
6. Giá điện sau 31/03/2027 (F5); P4 sunsirs so với F2 (trung vị 25.000 ngày 12/11/2027).

## 5. Phương pháp và kiểm tra
- Giả định khoá trước khi chạy: `assumptions_objective_r3.md` md5 `f312ad6cac2f495beac38505c1ab0a39`, khoá 2026-11-17T11:23:17Z (`lock_r3.txt`).
- `calc_r3/model_r2_copy.py`: chạy lại r2 ⇒ 64.736,0 (khớp `model_out_r2.json`). `bridge_sens.py`, bước 0': khung r3 + tham số r2 ⇒ 64.736,0, lệch 0,0000% (khung mới tương đương khung cũ).
- **Self-check** `selfcheck_r3.py`: tính lại tâm bằng đường độc lập (dạng đóng E[NVL], EBIT kỳ vọng tuyến tính, chiết khấu viết riêng, không import mô hình) ⇒ 66.864,9 so với cây 66.864,5, **lệch +0,0007% (ĐẠT, ngưỡng < 0,5%)**. Kết quả giống hệt khi chạy dưới TZ khác. Tổng xác suất lá = 1,0000000000.
- **Lệch so với giả định khoá:** không có lệch về giả định. Có một lỗi cài đặt đã sửa: độ nhạy "sản lượng H2/2027" ban đầu áp hệ số 2·vol−1 thay vì vol. Đã sửa trước khi báo; tâm/cây không bị ảnh hưởng.
- Tệp: `assumptions_objective_r3.md`, `lock_r3.txt`, `calc_r3/{model_r3.py, model_out_r3.json, bridge_sens.py, bridge_sens_out.json, selfcheck_r3.py, ebit_2026_2027.py, model_r2_copy.py, model_out_r2_rerun.json, attrib_r2_copy.py}`.

## WARNING (không bake vào base)
Vụ án hình sự lãnh đạo nhóm DGC/PAT (khởi tố 03/2026, mở rộng 07/2026); kiểm toán ngoại trừ. Bảo đảm chéo trong nhóm (40 tỷ + 100.000 USD cầm cố cho "Công ty và các công ty thành viên"). Rủi ro thiếu quặng ảnh hưởng KHỐI LƯỢNG sau Q1/2027. Thanh khoản cổ phiếu không đánh giá ở đây.
