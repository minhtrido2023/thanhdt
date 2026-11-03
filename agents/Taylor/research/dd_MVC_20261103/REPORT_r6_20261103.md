# DD — MVC (CTCP Vật liệu và Xây dựng Bình Dương, UPCOM) · bản r6 (nội bộ) · as-of 03/11/2026 · job `Taylor_20261103_103341`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua/bán. User quyết. Email: **CHƯA gửi** (dry-run OK).
> r6 = SỬA ĐỐI XỨNG sau `SKEPTIC4_20261103.md` (12 đính chính): nguyên tắc user 03/11 17:06 (dự án mới base = sổ sách/NPV 0; lệch chỉ khi có cơ sở độc lập) áp cho CẢ khoản cộng lẫn khoản trừ (r5 chỉ áp cho khoản trừ).
> Phần BCTC/ngành/quản trị: `REPORT_r2_20261103.md` §1–§6 vẫn hiệu lực. r5: `REPORT_r5_20261103.md`; r3/r4: `REPORT_r4_20261103.md` (lịch sử).
> Đơn vị tỷ đồng; đ/cp = tỷ × 10. Giả định tự đặt gắn (ước lượng).

## 0. Mù giá — thứ tự (ICT, `r6/calc/`) — GHI TRUNG THỰC
| Bước | Giờ |
|---|---|
| Brief r6 KHÔNG nêu giá. Dựng `model_r6.py` (tái dùng `model_r5.py` + `valuation_base.py` KHÔNG SỬA, md5 trùng r5) → `model_r6_out.{txt,json}`, `grid_r6.csv`; ngưỡng ĐĂNG KÝ TRƯỚC trong docstring | trước 17:37 |
| BQ chỉ truy vấn `GPM_P0`, `ROE_Trailing` (MVC, NNC) — không cột giá/PE/PB | ~17:35 |
| **KHOÁ** `LOCK_md5_r6.txt` 6 file | 17:37:37 |
| So giá `compare_r6.py`: 03/11 close 13.300 (DNSE `close_price` MVC G1 15:00:01; KL cả phiên 1.430 cp) | sau khoá |
**Giới hạn:** r1–r5 đã biết giá 13.700 (02/11) và 13.300 (03/11) ⇒ khoá md5 chỉ chứng minh THỨ TỰ CHẠY, không chứng minh "chưa từng thấy giá". Ngoài ra khi grep tìm lý do SL NNC (bước dựng), output vô tình hiện giá MVC/NNC cũ trong `dd_NNC_20261030/calc/valuation_v2.py:10` và `dd_NNC_20261030/REPORT.md:8,178` — không dùng làm đầu vào.

## 1. Kết luận r6
- **Tâm 23.093 đ/cp** (W 25/50/20/5 × g2031/thực 50:50; r 13%; holding 0; mỏ mới sổ sách 438,4 MỌI kịch bản − trễ GP kỳ vọng; đất ở sổ sách 30) · **Base cơ sở 22.942** (g2031 21.227 / thực 24.657).
- Stress: biên đá cụm về TB chu kỳ từ 2028 = **16.622** (×0,5: 19.858) · giá phẳng danh nghĩa 19.010.
- Đối chiếu mỏ mới hai phía có trọng số (upside tốt + NPV xấu/rất xấu): **22.170**.
- **Thang (lưới 2.187 bộ, đăng ký trước):** RẺ ≤15.586 (P10) · RẺ CÓ ĐIỀU KIỆN 15.586–17.345 · HỢP LÝ 17.345–22.540 · NGHIÊNG ĐẮT 22.540–25.132 · ĐẮT ≥25.132. P50 **19.755**, min 12.857. Tâm nằm ở vùng nghiêng đắt của chính lưới: tâm giả định biên cơ sở (≈73% biên đỉnh dài hạn), lưới cho 1/3 trọng số mỗi mức stress.
- **Sau khoá:** 13.300 = 0,58× tâm, 0,67× P50, P/B 0,86×; 0,3% bộ < giá ⇒ **RẺ (dưới P10). Biên an toàn CÓ ĐIỀU KIỆN: giá đá cụm giữ ≥~70% biên đỉnh** (P10 lưới con stress 0 = 19.786). Hoà vốn tâm = giá khi biên đơn vị dài hạn ≈37% đỉnh (stress s 1,54) [`compare_r6_out.txt`].
- ROE bền hàm ý của GIÁ (Gordon r13 g3): 11,6% > ROE TB 2017–25 của MVC 7,4% (BQ; skeptic nêu 10 năm 8,1% — khác cửa sổ). Chu kỳ ở ĐỈNH: GPM MVC 35,2% (Q3/26 TTM) vs 6,9–25,0% 2016–2025; NNC 53,3% vs TB 34,2%.
- So tham chiếu skeptic (đất 30 + mỏ mới sổ sách, lưới giữ): tâm 23.093 = khớp; base 22.942 = khớp; phẳng 19.010 = khớp; hai phía 22.170 = khớp. Lưới r6 KHÁC lưới skeptic (P10 20.313) vì thêm 2 trục stress biên + hạn GP theo brief (bỏ trục capex — vô hiệu khi up=False).

## 2. Sửa đối xứng (12 điểm SKEPTIC4)
| # | Điểm | r6 | Hiệu ứng đ/cp (vs tâm r6) |
|---|---|---|---|
| 1 | Đất ở 150 tỷ kỳ vọng (không IRR, chưa chủ trương) | Sổ sách 30 tỷ (ước lượng, skeptic 23,5–30; chưa đối chiếu thuyết minh từng lô); giá trị phát triển = option NGOÀI tâm; NĐT bỏ "thị trường chưa tính 23,5 ha" | option r5 +1.257; sổ sách 23,5: −68 |
| 2 | Mỏ mới bất đối xứng (+1.375 trong tâm, −2.299 ngoài) | Sổ sách mọi kịch bản; trễ GP giữ (Bobby F6, có cơ sở) | upside +1.375 · downside −2.299 · hai phía −924 (22.170) · bỏ trễ +510 |
| 3 | Chi phí vốn hỗn hợp 5,98%/Kd 4,55% | BỎ khỏi REPORT + NĐT. NPV cơ sở r11/13/15: g2031 −230/−346/−440; thực 105/−55/−185; tốt g2031 562/338/156 | — |
| 4 | Gordon vòng tròn (ROE 18,5%) | ROE 9/12/13,5% → 9.276/13.914/16.233; ROE TB 2017–25 7,4% → 6.785; 18,5% (tham chiếu) → 23.963. Tâm hàm ý ROE 17,9%. Thêm trục stress biên vào lưới (giá chu kỳ 270k NNC = 380×(1−0,533)/(1−0,342), chi phí giữ; biên đơn vị = 50% đỉnh) | stress 0,5 −3.236 · 1,0 −6.471 |
| 4b | Hạn GP Tân Lập 2035 vào lưới | Trục đối xứng 2035 / W / 2045 | 2035 −1.792 · 2045 +1.426 |
| 5 | "Không có dữ liệu cung" | Sửa: cung mới định lượng ~2,1 tr m³/năm thành phẩm MVC (1,5 tr nguyên khối ×1,42) + Tam Lập 1 khu II NNC cùng cụm 2028–30: có CHIỀU, chưa có ĐỘ LỚN ⇒ vách 300 ở độ nhạy | vách −658 |
| 6 | Holding 15% | Độ nhạy, nêu lý do NNC: cổ tức về tiền 15% (10,6/69,6), quỹ ĐTPT NNC 87→353 | 15% −1.264 · 30% −2.511 |
| 7 | SL NNC 1,10 vs Tân Lập 1,30 | GIỮ NNC 1,10 = NNC-DD công bố (cơ sở: FPTS base 0,8 tr m³ từ 2028 riêng NNC — lý do GP/trữ lượng CHƯA RÀ); Tân Lập 1,30 (hiệu chỉnh 2026). Độ nhạy cả hai chiều | NNC 1,20 +97 · NNC 1,30 cả kỳ +380 · Tân Lập 1,10 (2028–30) −303 |
| 8 | Nợ ròng >600 tỷ tuyệt đối | Lộ trình capex base (ước lượng, chưa khấu hao/VLĐ; mỏ mới chưa có dòng tiền 2028): cuối 2026 67 · 2027 589 · 2028 924. Cảnh báo = vượt lộ trình >150 (2027 >739; 2028 >1.074) | — |
| 9 | Phụ thuộc V_NNC | Tâm dùng V_NNC nhất quán 83.887 (r6). V_NNC cố định 77.656 (NNC-DD công bố): 22.491 (−602). Độ dốc +966 đ/cp MVC mỗi +10.000 V_NNC. Tham chiếu skeptic V_NNC 48.000 (giá TT NNC theo skeptic — Taylor KHÔNG truy vấn): 19.627. **CHƯA dựng lại NNC — chờ user.** | |
| 10 | "60% LNTT từ liên kết" | Artifact ~30% (15% về tiền); NĐT ghi ≈30% | — |
| 11 | Nhãn | "RẺ (dưới P10); biên an toàn CÓ ĐIỀU KIỆN: giá đá cụm giữ ≥~70% biên đỉnh"; ROE hàm ý của giá chỉ ở §7 NĐT (sau khoá); chu kỳ ở đỉnh nêu ở kết luận | — |
| 12 | Mù giá | Ghi trung thực §0 | — |

Độ nhạy khác (vs tâm): chi phí Tân Lập ±15% −1.689/+1.735 · r 15%/11% −1.527/+1.810 · PW 70/30 / 30/70 ∓671 [`model_r6_out.txt` §5].

## 3. Cầu nối base (co_so) [`model_r6_out.txt` §1]
| tỷ | g2031 | thực |
|---|---|---|
| Tân Lập | 798,0 | 1.016,3 |
| Mỏ mới (sổ sách 438,4 − trễ 48,7) | 389,7 | 389,7 |
| BOT 93,7 · gạch/xăng 41,5 · đất ở sổ sách 30,0 · LK nhỏ+ICD 99,9 · Q4 50,0 | 315,1 | 315,1 |
| Nợ ròng 30/09 | −116,6 | −116,6 |
| Phần trực tiếp | 1.386,2 | 1.604,5 |
| Phần NNC (44,07%, vòng chéo) | 736,5 | 861,2 |
| **TỔNG** | **2.122,7 (21.227)** | **2.465,7 (24.657)** |

## 4. Điều kiện đổi nhận định (cả hai chiều)
Xuống: biên gộp quý <28% (stress biên), giá Sở XD Q2/27 < −7%, GP mỏ mới bị từ chối, nợ ròng vượt lộ trình >150 tỷ. Lên: hạn GP Tân Lập ≥2045 (+1.426), biên ≥35% giữ qua Q4/26, mỏ mới có GP trước 30/06/2027 (+510).

## 5. Việc mở
1. Chưa chạy fundamental-skeptic trên r6.
2. NNC-DD chưa dựng lại (V_NNC 77.656 công bố vs 83.887 nhất quán; vách SL NNC 1,10 chưa rà lý do) — chờ user.
3. Giá trị sổ sách đất ở 30 tỷ chưa đối chiếu thuyết minh từng lô.
4. Hình 11 NĐT: nhãn đường stress bị đẩy ra ngoài khung (đường chấm vẫn hiện, chú thích hình ghi đủ) — thẩm mỹ, không đổi số.

## Tệp
`r6/calc/`: valuation_base.py · model_r5.py (không sửa) · model_r6.py · model_r6_out.{txt,json} · grid_r6.csv · LOCK_md5_r6.txt · compare_r6.py/_out.txt.
NĐT (đè): `investor_report/MVC_DD_investor_report_20261103.{md,pdf,html}`, `EMAIL_SUBJECT.txt`, `SELFCHECK.md`, `figs/`. Bản NĐT r5 lưu: `archive_internal/MVC_DD_investor_report_20261103_rev4_r5.md`; build r5: `archive_internal/build_report_r5.py`.
