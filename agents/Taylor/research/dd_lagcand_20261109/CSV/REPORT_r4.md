# DD CSV (Hoá chất Cơ bản Miền Nam) · ứng viên LAG_LO · **r4 — 23/11/2026** · job `Taylor_20261123_001046`

> **r4 thay r3 (`REPORT_r3.md`).** Lịch sử phản biện:
> - r2 (`REPORT.md`, 09/11) bị skeptic DD_GENERAL **r1 REFUTED** vì đếm hai lần: vốn hoá vĩnh viễn lợi nhuận của nhà máy BH1 đang bị cưỡng chế tháo dỡ, đồng thời tính nhà máy thay thế Nhơn Trạch theo NPV = 0.
> - r3 sửa lỗi đếm hai lần. Skeptic **r2 cho INCONCLUSIVE**: phép sửa đúng và số khớp, nhưng còn hai thiếu sót ngược chiều (lá chắn thuế khấu hao, lãi suất chiết khấu phần capex vay nợ) cùng vài hạng mục chưa định lượng.
> - r4 đưa hai thiếu sót vào base và thêm độ nhạy cho phần còn lại.
>
> Tâm: r2 20.717 → r3 11.041 → **r4 11.224 đ/cp** (sau chiết khấu thanh khoản ở cỡ 5 tỷ). Nhãn: TRONG vùng (r2) → **TRÊN vùng** (r3, r4). Đính chính chi tiết ở Phụ lục E.
>
> Chỉ nghiên cứu: không đặt lệnh, không wire, không gửi email, không ghi sổ giá.
>
> **Khoá giả định.** Khoá mù giá gốc là `calc/assumptions_r3.json` (md5 `05e886fe…`), ghi trong `calc/LOCK_r3_prerun.txt` lúc 07:17:59, trước khi truy vấn giá lúc 07:18:16. r4 **khoá lại sau khi đã thấy giá**, lý do là skeptic r2:
> - File khoá mới: `calc/assumptions_r4.json`, ghi trong `calc/LOCK_r4.txt`.
> - Chỉ thêm hai tham số. Cả hai có nguồn từ BCTC và chính sách kế toán, không chỉnh theo giá.
> - Mọi tham số của r3 giữ nguyên.
> - Theo schema v1: `calc/lock_v1_r4.json`, lint `--strict` 0 vi phạm.
>
> **Tái lập** (chạy từ thư mục CSV/):
> - `/home/trido/thanhdt/wc_venv/bin/python -I calc/model_r4.py`. Chạy 2 lần cho `run1_r4.txt` = `run2_r4.txt`, md5 `ea0d204c88e32a74d7908ff2e7588991`.
> - `calc/postlock_r4.py` cho giá, thanh khoản và nhãn.
>
> `src/` và các file dữ liệu của r2 được khôi phục từ git `b01861a67^`; md5 khớp `LOCK_post_md5_r2.txt` (xem E7).

## 1. Kết luận (r4)
| | Tâm | P10 | P25 | P50 | P75 | P90 | Giá 20/11 | Nhãn |
|---|---|---|---|---|---|---|---|---|
| Trước chiết khấu thanh khoản | 11.417 | 7.109 | 9.066 | 11.358 | 13.538 | 15.808 | 20.300 | TRÊN vùng |
| **Sau CK, cỡ 5 tỷ (headline)** | **11.224** | **6.989** | 8.913 | 11.166 | 13.309 | **15.541** | 20.300 | **TRÊN vùng** |
| Sau CK, cỡ 1 tỷ | 11.331 | 7.055 | — | 11.272 | — | 15.689 | 20.300 | TRÊN vùng |
| Sau CK, cỡ 40 tr | 11.400 | 7.098 | — | 11.341 | — | 15.784 | 20.300 | TRÊN vùng |

- **Giá so với vùng.** Giá 20.300 (đóng cửa 20/11, BQ) cao hơn tâm **80,9%** và cao hơn P90 30,6%. 99,8% trọng số kết cục nằm dưới giá.
- **Luật 4 trượt xa.** Ngưỡng mua là 0,85 × tâm = **9.540**.
- **Giá ngụ ý gì.** Để tâm bằng giá thì r phải khoảng **8,05%**, tức lãi huy động 12T khoảng 1,95%, trong khi hiện nay là 7,40%.
- **Kể cả nếu bỏ hết capex thay thế**, tức coi Nhơn Trạch 100% là tăng trưởng (φ = 0, gần cách (a) của r2), giá trị cũng chỉ là **20.027**, vẫn dưới giá. Vậy giá hiện tại ngụ ý thị trường không trừ đồng capex thay thế nào.
- **Điểm yếu lớn nhất của chính r4.** Tỷ lệ thay thế φ được suy từ báo chí và từ số tấn, vì không có bảng công suất cũ theo sản phẩm (§4). Mỗi 0,1 của φ làm tâm đổi khoảng **1.377 đ/cp**.
  - Nhãn "TRÊN vùng" đứng ở **mọi φ ≥ 0**: φ = 0,33 cho 15.558; φ = 0 cho 20.027.
  - Kịch bản TỐT dựa trên cú sốc axit có xung đột với việc nhà máy axit TB2 đã dừng (§6). Bỏ TỐT thì tâm còn 10.267.
- **Sizing (V8): 0% NAV tại giá hiện tại.** Nếu giá ≤ 9.540 thì xét 2% NAV, trần 4%; mỗi phiên ≤ 1 tỷ.

## 2. Chất lượng lợi nhuận (tái dùng r2 §2, đã được skeptic r1 và r2 kiểm khớp)
- **LN mẹ 2026:** Q3 85,40 tỷ (+47,9% YoY), Q2 130,03 tỷ (+107,6%), 9T 258,32 tỷ (+49,5%). Nguồn: BCTC Q3 p3 và giải trình 1591, 1020/GT-HCCB.
- **Nguồn phần vượt:**
  - Giá H2SO4 +249% (Q2) và +289% (Q3).
  - Phốt pho vàng của công ty con.
  - Hàng hoá thương mại tăng gấp 4 (G3).
- **Bản chất:** lợi nhuận kinh doanh thật nhưng phụ thuộc giá chu kỳ. Bobby đánh giá cú sốc lưu huỳnh là tạm thời (độ tin 0,85).
- **LN mẹ 2019–2025 (BQ):** 244,02 / 179,66 / 208,93 / 353,21 / 209,18 / 240,78 / 208,95. Trung bình **234,96**; TTM **294,49**.

## 3. Bảng cân đối và dòng tiền (30/09/2026, BCTC p1–p4, p14–p19)
**Tiền ròng**
- Tiền 154,63; tiền gửi trên 3 tháng 630,60; vay ngắn hạn 259,62 (vay ngân hàng tại công ty mẹ, TM14). Không có vay dài hạn.
- Trừ thêm hai quỹ là nợ phải trả: **quỹ khen thưởng phúc lợi (mã 323) 25,92** và **quỹ KH&CN (mã 344) 15,00**.
- ⇒ **Tiền ròng dùng cho định giá: 484,69 tỷ.**

**Trích quỹ từ LNST:** TM17a p19 ghi trích quỹ KTPL 2,431 cộng khen thưởng BĐH 2,656 tỷ, trên LN mẹ 2025 là 209,0 tỷ, tức **2,43%**. Áp vào mô hình: E_core × (1 − 2,43%).

**CĐKKS:** 49,96 tỷ.
- Cổ tức 21,14 tỷ trả trong 9T/26 là cổ tức cho **CĐKKS** (TM17a, cột lợi ích CĐKKS).
- Công ty mẹ không chia cổ tức tiền năm 2025; 172,85 tỷ được trích vào quỹ ĐTPT.

**TSCĐ hữu hình**
- Nguyên giá 1.144,9; giá trị còn lại 37,1 (p15).
- Chính sách khấu hao (p9): nhà cửa 5–25 năm, máy móc 4–10 năm.
- ⇒ Lợi nhuận lịch sử không gánh chi phí thay nhà máy. Đây là lý do mô hình phải xử lý capex thay thế.

**Lãi vay:** chi phí lãi vay 9T là 9,974 tỷ (p3, mã 24). Dư nợ bình quân (157,8 + 259,6)/2 ⇒ lãi suất hiệu dụng **6,37%/năm**.

**Dòng tiền 9T:** CFO +197,8; capex 265,7.

**Trả trước người bán 242,4 tỷ** (66,7 tỷ tại 30/06). BCTC Q3 không có thuyết minh chi tiết ⇒ **G2 không kiểm chứng được**, để ở độ nhạy.

**Số cổ phiếu:** 110.499.910 (mã 411 / 10.000 đ, tại 30/09/2026). Không có cổ phiếu quỹ, 9T không tăng vốn. Vinachem sở hữu 65,0%.

## 4. Nhơn Trạch = phần thay thế bắt buộc (D3) + phần tăng trưởng (V4a)
**Dữ kiện**
- Tổng vốn **1.844 tỷ**, gồm VCSH 632 và vay 1.212 (vay 10 năm). Nguồn: cafef 04/08/2026, danchuphapluat 18/08/2026, baodauthau 03/07/2025.
- Công suất **307.900 t/năm quy 100%**, "trên cơ sở hợp nhất 3 nhà máy hiện hữu".
- Ba nhà máy sản xuất cũ đều nằm ở KCN Biên Hoà 1 (BCTN 2021, PDF trang 13). Công ty con phốt pho ở Lào Cai, không di dời.
- **Cưỡng chế:**
  - QĐ 2408 cưỡng chế 3 thửa 10.358 + 19.476,9 + 52.474 m², thực hiện 15/07–31/12/2026.
  - Lý do ghi trong QĐ: công ty "không chấp hành việc tháo dỡ, di dời... bàn giao đất".
  - QĐ 1122 (CBTT 1123) dừng nhà máy Tân Bình 2 (H2SO4) sau 15/08/2026.
- **Lịch:**
  - Một số dây chuyền chạy từ cuối 2026.
  - Tháo dỡ BH1 xong 10/2029.
  - Nghiệm thu toàn bộ 12/2031.

**Tỷ lệ thay thế φ: trục 0,5 / 0,65 / 0,8** (trọng số 0,25/0,5/0,25, ước lượng). Hai mốc:
1. **Xút:** công suất cũ 50.000 t NaOH 100% (TCCT 21/05/2025), mục tiêu mới 100.000 t ⇒ 0,5.
2. **Tổng:** sản lượng 2021 là 245.949 t (BCTN 2021, PDF trang 18) so với 307.900 t ⇒ 0,80. Đây là cận trên, vì tấn thương phẩm khác tấn quy 100%.

Skeptic r2 lưu ý thêm (chiều RẺ):
- φ tính theo tấn, không theo capex.
- Xút–clo tốn capex/tấn hơn H2SO4, nên φ tính theo capex có thể thấp hơn 0,65.

Không có dữ liệu capex theo dây chuyền ⇒ **không kiểm chứng được**. Trục giữ nguyên; ảnh hưởng ±1.377 đ/cp cho mỗi 0,1 φ.

**Công thức base r4** (tỷ đồng, chia cho 110,50 triệu cổ phiếu):
```
Giá trị = (E·(1+dE) − 32,65)·(1 − 2,43%)/r + 484,69 − 49,96
          + (1−φ)·346,48                                    [phần tăng trưởng đã chi, giá vốn]
          − φ·[1.212/(1+kd_st)^t + 285,52/(1+r)^t]           [D3: phần thay thế còn chi]
          + φ·1.844·20%/L · niên_kim(r, L)/(1+r)^t            [lá chắn thuế khấu hao phần thay thế]
          + npv·(1−φ)·1.844                                  [trục NPV phần tăng trưởng, kỳ vọng 0]
```

**Hai thay đổi so với r3** (đều đưa vào base, có cơ sở dữ liệu):
- **Chiết khấu phần vay theo lãi vay sau thuế (kd_st).**
  - Phần còn chi 1.497,5 tỷ = vay 1.212 + VCSH còn lại 285,5 (632 − 346,5 đã chi bằng tiền sẵn có).
  - Phần vay là dòng tiền ra kiểu nợ, nên chiết khấu ở kd × (1 − 20%) = 8,0% × 0,8 = **6,4%**. Cách này đã gồm lá chắn thuế lãi vay.
  - kd 8,0% = lãi hiệu dụng thực tế 6,37% (BCTC) + 1,6pp kỳ hạn 10 năm (ước lượng). Độ nhạy kd 6,4% / 9,5%.
  - Phần VCSH vẫn chiết khấu ở Ke.
- **Lá chắn thuế khấu hao** cho phần thay thế.
  - L = **12 năm**. Cơ sở: chính sách khấu hao p9 (máy 4–10 năm, nhà 5–25 năm), gia quyền theo cơ cấu nguyên giá cũ p15 (máy 79%, nhà 16%) = 12,4 năm.
  - Bắt đầu tính từ thời điểm t, chiết khấu ở Ke. Độ nhạy L = 8 / 20.
  - Phần tăng trưởng (NPV = 0) đã gồm hiệu ứng thuế của nó, nên không cộng thêm.

**Tại tham số trung tâm** (φ 0,65, t 1,75, kịch bản CƠ SỞ):
- Phần thay thế còn chi: −855,4 tỷ ≈ −7.741 đ/cp.
- Lá chắn thuế: +92,6 tỷ ≈ +838 đ/cp.
- Phần tăng trưởng đã chi: +121,3 tỷ ≈ +1.097 đ/cp.
- Giá trị CƠ SỞ: **11.361** (trước CK).

**Bồi thường, tháo dỡ, đất**
- **Bồi thường BH1:**
  - QĐ 2408 Điều 2.4 dẫn Điều 27 NĐ 88/2024 (bồi thường, hỗ trợ, tái định cư khi Nhà nước thu hồi đất). QĐ cũng căn cứ VB 719/TTPTQĐ-BT ngày 03/07/2026 về "hồ sơ bồi thường".
  - ⇒ Có cơ sở để bồi thường > 0, nhưng **không có số tiền**. Báo chí chỉ nêu 195 triệu cây trồng.
  - Xử lý: **base = 0**; độ nhạy +100 tỷ ⇒ **+890 đ/cp**.
- **Kinh phí cưỡng chế phá dỡ:** do Nhà nước bố trí (Điều 2.4).
- **Chi phí hoàn nguyên môi trường** khu hoá chất cũ: **không kiểm chứng được**, không có số liệu. Chiều tác động ngược với bồi thường. Xử lý: WARNING kèm độ nhạy −100 tỷ ⇒ **−890 đ/cp**.
- **Đất TP.HCM** (TB 610/TB-UBND, đã đọc): đất **thuê**, tự nguyện trả lại theo k2 Đ82 Luật Đất đai 2024, thông báo không có điều khoản bồi thường ⇒ 0, có cơ sở.

## 5. 5F tầng (b) — TÁI DÙNG (< 12 tháng)
- `data/moat_tags.csv` (2026-06-05) xếp **NARROW · COST/SCALE**. ROE_Min5Y 13,66% ≈ Ke.
- Lực hành chính (di dời bắt buộc) đã làm đổi lớn dòng tiền, và tác động này đã nằm trong base qua D3.
- Không thưởng moat. Terminal RONIC = Ke (D4).
- Độ nhạy nếu thưởng moat: 12.675, vẫn TRÊN vùng.

## 6. Định giá
**Chi phí vốn (V1)**
- r = 13,5% + 1,0 × (7,40% − 7,40%) = **13,50%**. Lãi huy động lấy từ `deposit_rate_vn.effective_deposit_rate('2026-11-23')` = cctg_12m(2026-11-02) 7,40% (Big-4 6,8%), neo ngày 03/11.
- **Độ nhạy theo lãi huy động** (tâm sau CK 5 tỷ):

  | Thay đổi lãi | Tâm | So với base |
  |---|---|---|
  | −100bp | 12.301 | +9,6% |
  | −50bp | 11.742 | +4,6% |
  | +50bp | 10.742 | −4,3% |
  | +100bp | 10.294 | −8,3% |

- Với β = 0,5: ±100bp cho 11.742 / 10.742.
- **Hai đầu dải Ke nội địa (D4):** Ke 12,3% ⇒ 12.537; Ke 13,4% ⇒ 11.324.

**Kịch bản** (trọng số 0,25/0,5/0,25, ước lượng; dE ±10%), giá trị tại tham số trung tâm, trước CK:

| Kịch bản | LN mẹ (tỷ) | Cơ sở | Giá trị (đ/cp) |
|---|---|---|---|
| XẤU | 179,7 | Đáy xút 2020 | 7.744 |
| CƠ SỞ | 235,0 | Trung bình 2019–25 | 11.361 |
| TỐT | 294,5 | TTM | 15.254 |

**Lưới:** 243 kết cục = 3 kịch bản × 3 dE × 3 φ × 3 thời điểm × 3 NPV. Sau CK 5 tỷ: min 3.043, max 20.976.

**Xung đột TỐT và TB2 (skeptic r2).**
- TB2 là nhà máy H2SO4, đã dừng sau 15/08/2026.
- Tuy vậy, Q3 gồm khoảng 6 tuần sau khi dừng mà DT axit vẫn tăng. Phải trả người bán có Kompass và Marubeni, cho thấy axit có thể đến từ thương mại (G6).
- Chưa đủ cơ sở để bỏ TỐT khỏi base ⇒ giữ, kèm độ nhạy "TỐT = CƠ SỞ": **10.267 (−8,5%)**.
- Q4/26 là phép thử.

**Độ nhạy** (tâm sau CK 5 tỷ; base 11.224):

| Độ nhạy | Tâm | Δ |
|---|---|---|
| φ = 1,0 | 6.484 | −42,2% |
| φ = 0,8 | 9.193 | −18,1% |
| φ = 0,5 | 13.255 | +18,1% |
| φ = 0,33 | 15.558 | +38,6% |
| φ = 0 (≈ cách a của r2 + trừ quỹ) | 20.027 | +78,4% |
| TỐT thay bằng CƠ SỞ (TB2 dừng) | 10.267 | −8,5% |
| Hoàn nguyên môi trường −100 tỷ | 10.334 | −7,9% |
| Không lá chắn thuế khấu hao | 10.394 | −7,4% |
| Không chiết khấu thời gian capex còn chi (t = 0) | 10.391 | −7,4% |
| Đời khấu hao 20 năm / 8 năm | 10.981 / 11.409 | −2,2% / +1,6% |
| kd 6,4% / 9,5% | 11.092 / 11.343 | −1,2% / +1,1% |
| Chiết khấu toàn bộ ở Ke, không lá chắn (= r3) | 11.041 | −1,6% |
| Thay thế lặp lại mỗi 30 năm | 11.027 | −1,8% |
| Gián đoạn 0/−25/−50% (0,4/0,4/0,2) | 10.871 | −3,1% |
| Gián đoạn + bồi thường 100 tỷ | 11.761 | +4,8% |
| Bồi thường BH1 +100 tỷ | 12.114 | +7,9% |
| Ứng trước 200 tỷ là của Nhơn Trạch (G2) | 12.779 | +13,9% |
| Thưởng moat (RONIC 18,3%, g 4%) | 12.675 | +12,9% |
| Không trừ số dư quỹ KTPL/KH&CN | 11.588 | +3,2% |

**V6 (chỉ hiển thị)**
- V_ngắn (LN trung vị 2023–25 = 209,2 tỷ, g = 0) = **9.510** sau CK.
- V_dài: **FCFE ≤ 0** trong giai đoạn capex (CFO 9T 197,8 − capex 265,7; còn ~1.498 tỷ phải chi) ⇒ chỉ báo V_ngắn. FCFE âm là do đầu tư.
- Không tính D, không cờ phân kỳ, không ghi vào sổ.

**Đối chiếu nhanh:** P/E trên LN chuẩn hoá 9,5x; P/E TTM 7,6x; P/B mẹ 1,23x. Cờ "DCF auto CHEAP" là nhiễu: dùng thu nhập đỉnh và không có capex thay thế.

## 7. Thanh khoản và sizing (V3, V8)
- **Số liệu:** σ ngày 2,25%; ADV250 **8,88 tỷ** (cửa sổ 19/11/2025–20/11/2026); ADV60 7,32 tỷ.
- **Chiết khấu thanh khoản:**

  | Cỡ vị thế | CK | Ghi chú |
  |---|---|---|
  | 5 tỷ | **1,69%** | Q/ADV 56%, ngoài vùng hiệu chỉnh |
  | 1 tỷ | 0,76% | |
  | 40 tr | 0,15% | |

- **Số phiên thoát lệnh:** 5 tỷ cần 5,6 phiên ở tỷ lệ tham gia 10% (2,8 phiên ở 20%); 1 tỷ cần 1,1 phiên.
- Free float ≤ 35%. Nhãn TRÊN vùng ở mọi cỡ.
- **Sizing V8:** 0% NAV tại giá hiện tại. Nếu giá ≤ 9.540 thì xét 2%, trần 4%, mỗi phiên ≤ 1 tỷ.

## 8. Mốc đổi nhận định CẢ HAI chiều
| Chiều | Mốc (kiểm bằng BCTC/CBTT) | Tác động |
|---|---|---|
| **NÂNG** | Công bố cơ cấu 307.900 t / công suất cũ / capex theo dây chuyền cho thấy φ < 0,5 | +1.377 đ/cp mỗi −0,1 φ |
| NÂNG | Công bố số bồi thường BH1 (NĐ 88/2024, VB 719) | +890 đ/cp mỗi 100 tỷ |
| NÂNG | Thuyết minh xác nhận ~200 tỷ trả trước là của Nhơn Trạch (G2) | +1.555 đ/cp |
| NÂNG | LN mẹ Q4/26 ≥ 70 tỷ **và** Q1/27 ≥ 60 tỷ, kèm doanh thu axit vẫn cao sau khi TB2 dừng | Xác nhận TỐT (15.254 tại tham số trung tâm) |
| NÂNG | Lãi huy động 12T −100bp | +1.077 đ/cp |
| **HẠ** | Q4/26 cho thấy doanh thu/biên H2SO4 sụt sau khi TB2 dừng | Bỏ TỐT ⇒ ~10.267 |
| HẠ | Vượt dự toán 1.844 tỷ hoặc trễ trên 6 tháng (có tín hiệu cụ thể) | Phần thay thế còn chi tăng; trục NPV (−) |
| HẠ | Chi phí hoàn nguyên môi trường BH1 do công ty chịu, có số liệu | −890 đ/cp mỗi 100 tỷ |
| HẠ | Biên gộp quý < 20% hoặc LN mẹ quý < 40 tỷ trong giai đoạn di dời | Trọng số dồn về XẤU; độ nhạy gián đoạn |

**HARD ABANDON:** kiểm toán ngoại trừ BCTC 2026; dừng sản xuất trên 1 quý mà không có công suất thay thế; vay để chia cổ tức.

## 9. Pháp lý, quản trị, kiểm toán (chỉ WARNING, không vào tâm)
- **Cưỡng chế BH1 / dừng TB2:** thi hành đề án chuyển đổi KCN, không phải xử phạt. Hệ quả kinh tế (capex thay thế) đã nằm trong base qua D3.
- QĐ 2408 ghi lý do là công ty "không chấp hành việc tháo dỡ, di dời". Đây là cờ quản trị (chậm di dời), không phải hình sự.
- **Kiểm toán** (Taylor tự đọc ngày 23/11, ảnh trong `src/png_r3/`):
  - BCTC FY2025: 041/2025/BCTCHN-FAC ngày 23/02/2026, **chấp nhận toàn phần, không có đoạn nhấn mạnh**.
  - Soát xét 6T/2026: 044/2026 ngày 27/07/2026, **chấp nhận toàn phần**.
  - `audited_fy_missing = false`.
- **Giao dịch bên liên quan:** chủ yếu với các đơn vị cùng Vinachem (giá trị nhỏ). Nội dung các NQ HĐQT 2026 (02, 04, 07, 08) và NQ phê duyệt tổng vốn Nhơn Trạch **không kiểm chứng được** (không có trong `src/`). Ước lượng tác động dưới 1% lên tâm. Tổng vốn 1.844 chỉ có nguồn báo chí; một nguồn 2025 khác ghi khoảng 1.840.
- **Nhân sự:** đổi Chủ tịch 25/04/2026; đổi người phụ trách KTNB 06/07/2026.
- **GAPS còn mở:**
  - G2: trả trước 242,4 tỷ.
  - G3: hàng thương mại 350 tỷ.
  - G4b: lịch chi capex theo năm.
  - G6: nguồn H2SO4 sau khi TB2 dừng.
  - Cơ cấu capex/công suất theo dây chuyền (quyết định φ).
  - Chi phí hoàn nguyên môi trường.
  - Số bồi thường.

## 10. Cờ tự động của hệ
| Cờ | Đánh giá |
|---|---|
| W IDIOCRASH 27/07 | Nhiễu về cơ bản. Ngày đó giá chạm sàn −6,98%, VNINDEX −1,01%, CTS/MBS/VND cùng bị cờ |
| ROE5Y 18,3% | Thật nhưng gồm đỉnh 2022 và chưa gánh capex thay thế |
| DCF auto CHEAP | Nhiễu về kết luận |
| moat NARROW | Thật, tái dùng |
| ADV3T ~6 tỷ | Thật; ADV250 8,88 tỷ |

## 11. Giả định [ước lượng] (đầy đủ ở `calc/assumptions_r4.json`)
- Trọng số kịch bản 0,25/0,5/0,25; dE ±10%.
- φ 0,5/0,65/0,8; thời điểm chi 0,5/1,75/3,0 năm; NPV phần tăng trưởng ±20%.
- kd 8,0% (6,37% đo + 1,6pp ước lượng).
- Đời khấu hao 12 năm (gia quyền theo chính sách khấu hao).
- Lãi tiền gửi sau thuế 32,65 tỷ/năm.
- Trích quỹ 2,43% (số đọc từ TM17a).
- Bồi thường = 0; hoàn nguyên = 0 (cả hai chỉ ở độ nhạy).
- RONIC = Ke.

## 12. File
- `REPORT_r4.md` (bản này); `REPORT_r3.md` (r3, đã qua skeptic r2).
- `calc/assumptions_r4.json`, `calc/LOCK_r4.txt`, `calc/model_r4.py`, `calc/run1_r4.txt` / `run2_r4.txt`, `calc/model_r4_out.json`, `calc/postlock_r4.py` / `_out.json`, `calc/lock_v1_r4.json`.
- Bản r3: `calc/assumptions_r3.json`, `LOCK_r3_prerun.txt`, `model_r3.py`, `postlock_r3.py`, `px_csv_r3.csv`.
- `src/bctn_2021_vietstock.pdf`, `src/png_r3/`.
- Bản cũ giữ nguyên.

Nguồn web: [cafef 04/08/2026](https://cafef.vn/sau-cuong-che-cong-ty-hoa-chat-2400-ty-tren-san-phai-dung-nha-may-sau-ngay-15-8-188260804081236249.chn) · [danchuphapluat 18/08/2026](https://danchuphapluat.vn/hoa-chat-co-ban-mien-nam-loi-nhuan-6-thang-but-pha-nha-may-hoa-chat-nhon-trach-tang-toc-ve-dich-10156.html) · [baodauthau 03/07/2025](https://baodauthau.vn/cong-ty-cp-hoa-chat-co-ban-mien-nam-du-kien-dau-tu-1840-ty-dong-xay-nha-may-tai-nhon-trach-post181151.html) · [Đại biểu Nhân dân 26/09/2025](https://daibieunhandan.vn/khoi-cong-nha-may-hoa-chat-nhon-trach-buoc-ngoat-phat-trien-cua-hoa-chat-co-ban-mien-nam-10388014.html) · [TCCT 24/09/2025](https://tapchicongthuong.vn/hoa-chat-co-ban-mien-nam--khang-dinh-vi-the-voi-du-an-nha-may-hoa-chat-nhon-trach-239793.htm) · [TCCT 21/05/2025](https://tapchicongthuong.vn/gia-xut-thiet-lap-nen-gia-moi--hoa-chat-co-ban-mien-nam--csv--huong-loi-lon-140693.htm) · [BCTN 2021](https://static2.vietstock.vn/vietstock/2022/3/30/20220330_20220330___csv___bctn_2021.pdf)

## Phụ lục E · Đính chính
**E-A. Từ r2 sang r3** (skeptic r1 REFUTED; chi tiết ở `REPORT_r3.md`, Phụ lục E)

| # | Hạng mục | Xử lý |
|---|---|---|
| E1 | Đếm hai lần E_core BH1 và Nhơn Trạch NPV = 0 | Cách (b): phần thay thế φ, phần đã chi không cộng lại, phần còn chi là dòng tiền ra; phần tăng trưởng NPV = 0. Tâm 20.717 → 11.041 |
| E2 | Thiếu công suất BH1 cũ | Hai mốc: xút 50k t; tổng sản lượng 2021 245.949 t ⇒ φ 0,5/0,65/0,8. Theo sản phẩm: không kiểm chứng được |
| E3 | Thiếu lịch G4 | Lịch từ cafef/danchuphapluat ⇒ trục thời điểm chi |
| E4 | Đất HCM, bồi thường BH1 | Đất HCM: đất thuê, tự nguyện trả lại ⇒ 0. Bồi thường: base 0, độ nhạy |
| E5 | Quỹ khen thưởng phúc lợi | Trừ số dư 25,92 + 15,00 khỏi tiền ròng; trích 2,43% LNST |
| E6 | NQ giao dịch NCLQ | Không kiểm chứng được (ảnh hưởng dưới 1%, ước lượng) |
| E7 | `src/` và dữ liệu mất; mtime | Khôi phục từ git `b01861a67^` (TRIM_DD 19/11); md5 khớp `LOCK_post_md5_r2.txt` (fin_csv_bq ff723f56, assumptions f27491d7, model 12808ac0) |
| E8 | Kiểm toán ghi theo errata | Đã tự đọc FY2025 và soát xét 6T: đều chấp nhận toàn phần |
| E9 | Nguồn số cổ phiếu | Mã 411, 30/09/2026 |
| E10 | r2 chưa từng qua phản biện | r3 đã chạy skeptic r2; r4 chạy skeptic r3 |
| E11 | Chiều ngược: phần tăng trưởng, nền Q4 | (1−φ) NPV = 0 và cộng lại phần đã chi; mốc NÂNG ở §8 |
| E12 | G7 cổ tức 21,17 tỷ | Là cổ tức CĐKKS (TM17a) ⇒ đóng |

**E-B. Từ r3 sang r4** (skeptic r2 INCONCLUSIVE, `skeptic/r2.json`)

| # | Hạng mục skeptic r2 | Xử lý trong r4 | Tâm |
|---|---|---|---|
| F1 | Thiếu lá chắn thuế khấu hao phần thay thế (+~5,4% với đời 20 năm) | **Đưa vào base:** L = 12 năm (chính sách khấu hao p9, gia quyền theo nguyên giá p15), thuế 20%, chiết khấu ở Ke từ thời điểm t. Độ nhạy L = 8 / 20 | +838 đ/cp (CƠ SỞ) |
| F2 | Capex còn chi phần lớn là vay, nhưng chiết khấu ở Ke (−641 ở kd 8%) | **Đưa vào base:** phần vay 1.212 chiết khấu ở kd sau thuế 6,4% (kd 8,0% = 6,37% đo + 1,6pp); phần VCSH 285,5 ở Ke. Độ nhạy kd 6,4% / 9,5% | khoảng −650 đ/cp |
| F3 | Thiếu chi phí tháo dỡ / hoàn nguyên BH1 | Đã đọc QĐ 2408 Điều 2.4: kinh phí cưỡng chế phá dỡ theo NĐ 88/2024 Điều 27 (nhà nước). Hoàn nguyên môi trường: **không kiểm chứng được** ⇒ độ nhạy −100 tỷ (−890 đ/cp), WARNING | độ nhạy |
| F4 | Kịch bản TỐT xung đột với việc TB2 dừng (G6) | Chưa có cơ sở để hạ (Q3 gồm 6 tuần sau khi dừng mà axit vẫn tăng; có thể là axit thương mại). Giữ base; độ nhạy "TỐT = CƠ SỞ" 10.267 (−8,5%); mốc Q4/26 ở §8 | độ nhạy |
| F5 | φ theo tấn, không theo capex; mốc 0,80 yếu | Ghi rõ chiều (φ theo capex có thể < 0,65 ⇒ tâm cao hơn). Không có dữ liệu capex theo dây chuyền ⇒ **không kiểm chứng được**; trục giữ nguyên | ±1.377 / 0,1 φ |
| F6 | NQ tổng vốn Nhơn Trạch không có trong `src/` | Không kiểm chứng được; nguồn báo chí 1.840–1.844 nhất quán | — |
| F7 | Bồi thường (chiều tăng) | Đọc thêm QĐ 2408: dẫn NĐ 88/2024 và VB 719 "hồ sơ bồi thường" ⇒ có cơ sở > 0 nhưng không có số ⇒ giữ độ nhạy +890 / 100 tỷ | độ nhạy |

**Cầu nối tâm** (sau CK 5 tỷ):
- r2: 20.717.
- Trừ quỹ, φ = 0: 20.027.
- r3 (thêm D3): 11.041.
- Thêm F2 (kd sau thuế): 10.394.
- Thêm F1 (lá chắn thuế): **11.224**.

Tâm r4 dịch +1,7% so với r3 (≤ 5%) và không đổi nhãn. Tuy vậy, r4 vẫn chạy skeptic vòng cuối, vì r3 chưa từng được CONFIRMED.
