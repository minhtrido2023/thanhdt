# DRI — DD redo VÒNG 2 (05/11/2026, job Taylor_20261105_020023)

**Kết luận (số từ `calc/dri_redo_r2_out.txt`, MỨC KẾT CỤC, 36 kết cục = 18 ô × 2 đường giá):**
tâm **14.092 đ/cp sau CK** (14.379 trước) · **P10 12.006 · P50 14.235 · P90 16.146** sau CK (min 9.737).
Giá 04/11/2026 **13.500** ⇒ −4,2% so tâm ⇒ **TRONG vùng**; **35,2% trọng số kết cục nằm dưới giá**. Luật 4 (giá ≤ 0,85 × tâm): **không đạt**. Hồ sơ crisis-DD DRI đang mở (ngày 4: GIỮ), nhưng ở giá 04/11 **không đủ điều kiện vào thêm theo fear-buy §2.5**.
Nhãn giữ "TRONG vùng". So với sổ mức giá cũ (P25–P75 lưới base, 13.300/14.360/16.490), vùng đổi chủ yếu vì **định nghĩa** (P10–P90 ở mức kết cục), không phải vì cơ bản.

Engine `dri_val_supply_adj_r4_20261027/model.py` exec nguyên văn (tự exec tiếp `dri_val_supply_adj_r3_20261027/model.py`); dữ liệu snapshot 03/11; **LOCK đã bổ sung** r3/model.py và `dri_val_supply_adj_20261027/data/dri_peers_fin.csv` (`calc/LOCK_r2_md5.txt`; danh sách file thực đọc lưu trong `files_read` của out.json). Chân đối chứng cấu hình vòng 1: 15.860 / 11.924 (khớp pin). Chạy 2 lần trùng byte.

## 1. Đã sửa gì (theo E_CORRECTIONS, kiểm bằng calc)
Cầu nối giá trị tại điểm (mid TB, L27, trước CK, đ/cp):

| Bước | Giá trị |
|---|---|
| Base vòng 1 (giữ vườn tới L27; cắt 50% khoản vay Dakruco; giữ 15% tiền Lào; gỗ 20,87 tr/ha) | 15.860 |
| + bỏ haircut khoản vay Dakruco 40 tỷ (đang trả đúng hạn 80→40 tỷ H1, lãi ~9%) | 16.134 |
| + bỏ "giữ lại 15% tiền Lào" (vòng 1 tự ghi là ĐOÁN, không có cơ sở đo) | 16.537 |
| + giá gỗ thanh lý = giá khởi điểm NQ15: 36 tr LAK/ha × 1,1404 = **41,05 tr VND/ha** (thay ước 20,87 từ ~54 ha) | 17.044 |
| + **đọc NQ15 Điều 4**: thanh lý 1.975,23 ha đều 2027–2030, tái canh = dự án mới NPV0 | **14.924** |
| Nhánh NQ15-KINH TẾ: cùng lịch, tái canh theo kinh tế engine (capex m7, năng suất mở cạo) | 13.952 |
| (đối chiếu) nhánh "bị buộc" cũ: 3.949 ha 2029–36 | 13.414 |

Hai khoản sửa base (+677) bị bù trừ bởi dữ liệu NQ15 (−2.120 tại điểm): thanh lý sớm 1.975 ha (≈24% diện tích cạo) làm mất sản lượng mủ từ 2027–30 tới hết đời, chỉ thu ≈81 tỷ tiền đấu giá. Base vòng 1 (R_on=False, cạo tới L27) **mâu thuẫn với NQ15** ⇒ bỏ khỏi base, báo song song (mục 3).

## 2. Lưới (mức kết cục) — trục và giả định tự đặt [UL]
| Trục | Mức | Trọng số | Ghi chú |
|---|---|---|---|
| Đọc NQ15 | NPV0 / KINH TẾ | 0,80 / 0,20 **[UL]** | 0,20 = trọng số nhánh "bị buộc" cũ (nhận định). Luật 20 ủng hộ NPV0; nhánh KINH TẾ là kịch bản có xác suất |
| mid RSS3 thực 2014-01..2026-09 | P25 1,924 / TB 2,221 / P75 2,432 USD2025/kg | .25/.5/.25 | đối xứng (skeptic R4) |
| Đời cạo L | 22 / 27 / 32 | .25/.5/.25 | **giả định**, không có định mức nguồn |
| Trong ô: đường giá 2027–28 | PEAK / MID | 0,6 / 0,4 **[UL]** | |
| FCF = 90% LN lõi | — | — | **[UL]** |

Tách bạch (§4): tâm = kỳ vọng lưới **14.379** (trước CK) · giá trị tại tham số trung tâm **14.730** · P50 kết cục **14.525**. Đuôi dưới do nhánh KINH TẾ: nhánh này một mình có tâm 13.307, P10 10.789 (sau CK), 56,2% dưới giá.

Độ nhạy (tâm sau CK; gốc 14.092):
- Trọng số nhánh KINH TẾ: 0 → 14.288 · 0,1 → 14.190 · 0,3 → 13.994 · 0,5 → 13.798.
- wp PEAK: 0 → 14.532 · 0,5 → 14.165 · 1 → 13.799.
- FCF/LN lõi 80% → 13.219 · 100% → 14.965.
- Khôi phục haircut Dakruco 50% −268 · giữ 15% tiền Lào −395 · cả hai −663 · **khoản vay Dakruco mất trắng −536** · giá gỗ cũ 20,87 −791.
- Lãi huy động (β=1): −100bp +2,6% · −50bp +1,3% · +50bp −1,2% · +100bp −2,4%.

## 3. Báo song song — bản bỏ qua NQ15 (giữ vườn tới L27, nhánh "bị buộc" theo lịch engine cũ, base đã sửa)
Tâm **15.577** · P10 12.548 · P50 15.852 · P90 18.582 · 17,8% dưới giá (sau CK). Nếu NQ15 Điều 4 không thực hiện (không ai mua, HĐQT huỷ) thì giá trị nghiêng về bản này.

## 4. Thanh khoản
ADV trung vị 250 phiên **8,33 tỷ**, 60 phiên **13,82 tỷ**; σ 2,58%.
- Cỡ tham chiếu **5 tỷ** (quy ước fleet; Q/ADV250 0,6× — trong vùng hiệu chỉnh): CK **2,00%** (ADV60: 1,55%). **Nhãn tính ở cỡ này.** Cỡ 5 tỷ ≈65× vị thế thật 75 triệu (đã đóng).
- Cỡ sleeve thật 10–40 triệu: CK **0,09–0,18%** (ADV60 0,07–0,14%) — không đáng kể.

## 5. WARNING pháp lý / quản trị (đầy đủ)
- **Vụ án Dakruco** (cổ đông ~45%, mã **DRG**): 2 cựu TGĐ bị khởi tố; 5 bị can bị truy tố 02/2025. Rủi ro lan sang DRI qua giao dịch bên liên quan.
- **ĐHĐCĐ 22/10/2026 nâng ngưỡng giao dịch bên liên quan cần ĐHĐCĐ duyệt từ 10% lên 30% tổng tài sản**, cùng ngày với Tờ trình 40 (Dakruwood). Cần đối chiếu LDN Đ167 k2 và NĐ155 Đ293 k4b — **cần legal-vn**.
- **NQ HĐQT 15**: nghiên cứu mua Dakruwood từ Dakruco (HĐQT xét 12/2026).
- **Đấu giá 1.975,23 ha**: bán một lô, giá cố định 4 năm, **không cấm bên liên quan mua** ⇒ theo dõi danh tính bên trúng (nếu là Dakruco/Dakruwood thì thành giao dịch bên liên quan).
- Cho Dakruco vay còn 40 tỷ (TSĐB 6 triệu cp DRI), đang trả đúng hạn — trong base theo sổ sách; mất trắng = −536.
- Tiền gửi Quỹ TDND Cao su ĐL 70 tỷ + góp vốn 3 tỷ (soát xét chưa xác định giá trị thu hồi khoản góp). ~197 tỷ tại Lào không thuyết minh nguyên tệ/lãi/kỳ hạn; văn bản tô nhượng chưa công khai; một phần đất thuộc quy hoạch rừng bảo tồn.
- Liên hệ framework §3 **HARD ABANDON #4** (giao dịch bên liên quan chuyển giá trị ra cổ đông lớn).
- "Chưa thấy xử phạt/khởi tố DRI 2026": WebSearch **05/11/2026** — không thấy vụ mới gắn với DRI; chỉ có bài Báo Thanh tra về khởi tố lãnh đạo Dakruco (vụ cũ).
- Ngoài redo (Mike xử lý): broker `openQuantity` DRI = 0 ở cả 2 account.

## 6. Mốc đổi nhận định (hai chiều) + HARD ABANDON
| Mốc | Thời điểm | Tích cực hơn nếu | Tiêu cực hơn nếu |
|---|---|---|---|
| SXKD tháng 10 | ~10/11/2026 | Bán ≥ ~1.390 t/tháng | < 1.000 t |
| Kết quả đấu giá 1.975 ha | Q4/2026 | Giá trúng > khởi điểm, bên thứ ba | Bên trúng = Dakruco/Dakruwood; hoặc huỷ |
| HĐQT xét Dakruwood | 12/2026 | Không mua / giá ≤ sổ sách có thẩm định | Mua giá cao từ cổ đông lớn |
| BCTC Q4/2026 | ~20/01/2027 | Tồn kho giảm, CFO ≥ LNST | Tồn kho không giảm |
| Chuyển sàn HOSE | Q4/2026 | Được chấp thuận | Chậm |
| Giá cổ phiếu | — | < P10 12.006 ⇒ DƯỚI vùng | > P90 16.146 ⇒ TRÊN vùng |

**HARD ABANDON** (đề xuất, chờ user duyệt): (1) DRI mua Dakruwood/tài sản Dakruco giá > sổ sách hoặc không có thẩm định độc lập; (2) khoản vay Dakruco quá hạn / gia hạn không lãi; (3) bên trúng đấu giá là bên liên quan với giá ≈ khởi điểm; (4) vụ án Dakruco mở rộng sang nhân sự/giao dịch DRI. Vị thế thật đã đóng ⇒ không cần tranche.

## Phụ lục — đổi gì so với vòng 1
| | Vòng 1 | **Vòng 2** | Lý do |
|---|---|---|---|
| Tâm sau CK | 14.329 | **14.092** | base sửa (+) và NQ15 (−) bù trừ (mục 1) |
| P10 / P50 / P90 sau CK | 11.255 / 14.296 / 17.422 | **12.006 / 14.235 / 16.146** | nhánh "bị buộc" cũ (3.949 ha) thay bằng hai cách đọc NQ15 (1.975 ha); mức kết cục |
| % trọng số dưới giá | 43,8% (ô) | **35,2%** (kết cục) | |
| Nhãn | TRONG vùng | **TRONG vùng** | không đổi |

Không sửa `kb/dd_price_zones.json`. Chưa qua fundamental-skeptic vòng 2 (Mike chạy).
