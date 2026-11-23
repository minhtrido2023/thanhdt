# DD CSV (Hoá chất Cơ bản Miền Nam) · ứng viên LAG_LO · **r3, dựng lại 23/11/2026** · job `Taylor_20261123_001046`

> **r3 thay r2 (`REPORT.md`, 09/11).** Bản r2 bị skeptic DD_GENERAL r1 (22/11) phán **REFUTED** vì đếm hai lần: vốn hoá vĩnh viễn lợi nhuận của nhà máy cũ BH1 đang bị cưỡng chế tháo dỡ, đồng thời tính nhà máy thay thế Nhơn Trạch theo NPV = 0. r3 dựng lại theo cách (b) của errata. Tâm giảm từ **20.717 xuống 11.041 đ/cp** (−46,7%). Nhãn đổi từ **TRONG vùng sang TRÊN vùng**. Toàn bộ thay đổi so với r2 nằm ở **Phụ lục E**. Bản r2, r1 và errata được giữ nguyên.
>
> Chỉ nghiên cứu: không đặt lệnh, không wire, không gửi email, không ghi sổ giá.
>
> **Mù giá.** Giả định được khoá ở `calc/assumptions_r3.json` (md5 `05e886fe1782b273410640d108436e86`). `calc/LOCK_r3_prerun.txt` ghi lúc 2026-11-23T07:17:59+07:00, **trước** khi truy vấn giá mới. Minh bạch: giá 22.600 ngày 06/11 đã biết từ r2 trước khi khoá. Không tham số nào được chỉnh sau khi xem giá.
>
> **Tái lập** (chạy từ thư mục CSV/):
> - `/home/trido/thanhdt/wc_venv/bin/python -I calc/model_r3.py` — mù giá. Hai lần chạy cho `run1_r3.txt` = `run2_r3.txt`, md5 `c974ecfb5d6c0a1bf07404b63fb438a3`.
> - `.../python -I calc/postlock_r3.py` — sau khoá: giá, thanh khoản, nhãn. Đọc `calc/px_csv_r3.csv`, truy vấn ở `calc/px_csv_r3.sql`.
> - File khoá theo schema v1: `calc/lock_v1_r3.json`. Lint `bin/dd_assumptions_lint.py --strict` cho 0 vi phạm.
>
> **Nguồn.** `src/` và các file dữ liệu `calc/` của r2 đã được **khôi phục** từ git `b01861a67^`. Chúng bị xoá bởi đợt TRIM_DD ngày 19/11, và md5 khớp `calc/LOCK_post_md5_r2.txt` (xem E7).

## 1. Kết luận (r3)
| | Tâm | P10 | P25 | P50 | P75 | P90 | Giá 20/11 | Nhãn |
|---|---|---|---|---|---|---|---|---|
| Trước chiết khấu thanh khoản | 11.231 | 6.727 | 8.757 | 11.182 | 13.647 | 15.832 | 20.300 | TRÊN vùng |
| **Sau CK, cỡ 5 tỷ (headline)** | **11.041** | **6.613** | 8.609 | 10.993 | 13.416 | **15.564** | 20.300 | **TRÊN vùng** |
| Sau CK, cỡ 1 tỷ | 11.146 | 6.676 | — | 11.097 | — | 15.712 | 20.300 | TRÊN vùng |
| Sau CK, cỡ 40 tr | 11.214 | 6.717 | — | 11.165 | — | 15.808 | 20.300 | TRÊN vùng |

- **Giá so với vùng.** Giá 20.300 (đóng cửa 20/11, BQ) cao hơn tâm **83,9%** và cao hơn P90 30,4%. **99,8% trọng số** kết cục nằm dưới giá.
- **Luật 4 trượt xa.** Ngưỡng mua là 0,85 × tâm = **9.385**.
- **Giá ngụ ý gì.** Muốn tâm (sau CK 5 tỷ) bằng giá thì cần r ≈ **7,68%**, tức lãi huy động 12T khoảng 1,6%, trong khi hiện nay là 7,40%. Cách đọc khác: ngay cả khi coi Nhơn Trạch **100% là tăng trưởng** (φ = 0, tức cách (a) của r2 cộng thêm các khoản trừ quỹ), giá trị cũng chỉ là **20.027**, vẫn dưới giá. Vậy giá hiện tại ngụ ý thị trường **không trừ đồng capex thay thế nào** và còn kỳ vọng thêm phần thưởng.
- **Điểm yếu lớn nhất của chính r3:** tỷ lệ thay thế φ (phần capex Nhơn Trạch chỉ để thay công suất BH1 cũ) không có số chính xác theo từng sản phẩm. Tôi dùng dải 0,5/0,65/0,8, dựa trên hai mốc độc lập (§4). Mỗi 0,1 của φ làm tâm đổi khoảng **1.406 đ/cp** (trước CK). Kết luận "TRÊN vùng" vẫn đứng ở **mọi φ ≥ 0**: φ = 0,33 cho 15.465, φ = 0 cho 20.027, cả hai đều dưới giá 20.300.
- **Sizing (V8):** đề xuất **0% NAV** tại giá hiện tại. Nếu giá về dưới ngưỡng luật 4 (≤ 9.385) thì mở 2% NAV, trần 4%, và mỗi phiên ≤ 1 tỷ (§7).

## 2. Chất lượng lợi nhuận (tái dùng r2 §2, không đổi; số đã được skeptic r1 kiểm khớp)
- LN mẹ Q3/26 85,40 tỷ (+47,9% YoY), Q2 130,03 tỷ (+107,6%), 9T 258,32 tỷ (+49,5%). Nguồn: BCTC Q3 p3 và giải trình 1591, 1020/GT-HCCB.
- Phần vượt đến từ **giá H2SO4 +249%/+289%** và phốt pho vàng của công ty con, cộng thêm hàng hoá thương mại gấp 4 lần (G3).
- Lợi nhuận khác không đáng kể. Tức là lợi nhuận kinh doanh thật nhưng **phụ thuộc giá chu kỳ**. Bobby đánh giá cú sốc lưu huỳnh là TẠM THỜI (độ tin 0,85).
- **Nền so sánh:** LN mẹ năm 2019–2025 (BQ, kiểm lại trong `model_r3_out.json`) lần lượt là 244,02 / 179,66 / 208,93 / 353,21 / 209,18 / 240,78 / 208,95 tỷ. Trung bình **234,96**, TTM 294,49.

## 3. Bảng cân đối và dòng tiền (30/09/2026, BCTC p1–p4, p14, p19)
- **Tiền và tiền gửi:** tiền 154,63 tỷ, tiền gửi trên 3 tháng 630,60 tỷ, vay ngắn hạn 259,62 tỷ, không có vay dài hạn.
- **r3 trừ thêm hai quỹ là nợ phải trả** (đã được cấp bằng tiền):
  - Quỹ khen thưởng phúc lợi (mã 323): **25,92 tỷ**.
  - Quỹ phát triển KH&CN (mã 344): **15,00 tỷ**.
  - ⇒ **Tiền ròng dùng cho định giá: 484,69 tỷ** (r2: 525,61).
- **Trích quỹ từ LNST** (TM17a p19, phân phối LN 2025): quỹ KTPL 2,431 + khen thưởng BĐH 2,656 = 5,087 tỷ trên LN mẹ 209,0 tỷ = **2,43%**. Khoản này không đi qua P&L, nên được trừ khỏi dòng tiền cổ đông: E_core × (1 − 2,43%).
- **CĐKKS:** 49,96 tỷ, trừ theo sổ.
- **Cổ tức 21,14 tỷ trong 9T/26** nằm ở cột "lợi ích CĐKKS" của TM17a, tức là **trả cho cổ đông thiểu số của công ty con**, không phải cổ đông công ty mẹ. G7 đóng. Công ty mẹ không chia cổ tức tiền 2025; 172,85 tỷ được trích vào quỹ ĐTPT.
- **TSCĐ hữu hình gần hết khấu hao:** nguyên giá 1.144,9 tỷ, giá trị còn lại 37,1 tỷ, khấu hao 9T 15,0 tỷ (p15). ⇒ Lợi nhuận lịch sử **chưa gánh chi phí thay nhà máy**. Đây là cốt lõi của lỗi r2.
- **CFO 9T: +197,8 tỷ.** Capex 9T 265,7 tỷ ⇒ FCFE 9T âm.
- **Trả trước người bán 242,4 tỷ** (từ 29,1 tỷ đầu năm; 66,7 tỷ tại 30/06 theo BCTC soát xét 6T). BCTC Q3 **không có thuyết minh chi tiết** khoản này (đã đọc lại p14 ngày 23/11). G2 vẫn không kiểm chứng được, nên chỉ để ở độ nhạy.
- **Sở hữu:** Vinachem 65,0% ⇒ free float ≤ 35%.
- **Số cổ phiếu:** 110.499.910 = vốn góp mã 411 1.104.999.100.000 đ / 10.000 đ (BCĐKT 30/09/2026). Không có cổ phiếu quỹ và không tăng vốn trong 9T (TM17a).

## 4. Nhơn Trạch = thay thế bắt buộc + tăng trưởng (luật V4a + D3) — phần sửa chính của r3
**Dữ kiện (có nguồn):**
- **Tổng vốn và công suất:**
  - Tổng vốn **1.844 tỷ**, gồm vốn chủ 632 và vay 1.212 (cafef 04/08/2026, danchuphapluat 18/08/2026; baodauthau 03/07/2025 ghi khoảng 1.840).
  - Công suất thiết kế **307.900 t sản phẩm/năm, quy đổi 100%** (danchuphapluat 18/08/2026).
  - Nhà máy được mô tả "trên cơ sở hợp nhất 3 nhà máy hiện hữu" (baodauthau). Mục đích là "di dời toàn bộ hoạt động sản xuất tại KCN Biên Hoà 1".
- **Ba nhà máy sản xuất đều ở KCN Biên Hoà 1** (BCTN 2021, PDF trang 13): Biên Hoà (xút–clo), Tân Bình 2 (H2SO4, phèn), Đồng Nai (H3PO4). Chi nhánh Tân Bình ở TP.HCM chỉ kinh doanh. Công ty con phốt pho ở Lào Cai, **không di dời**.
- **Lực ép di dời:**
  - QĐ 2408/QĐ-UBND ngày 07/07/2026 cưỡng chế tháo dỡ; thời gian thực hiện 15/07–31/12/2026, trên ba thửa khoảng 82.300 m² (cafef).
  - QĐ 1122/QĐ-HĐQT ngày 31/07/2026 dừng toàn bộ nhà máy Tân Bình 2 sau 15/08/2026.
  - ⇒ Phần capex để **giữ lại công suất cũ** là chi bắt buộc theo quy định và **không tạo doanh thu mới**. Theo **D3**, đó là **capex tuân thủ = DÒNG TIỀN RA**.
- **Lịch (G4, đóng một phần):**
  - Một số dây chuyền chạy từ cuối 2026 (danchuphapluat).
  - Tháo dỡ và bàn giao BH1 hoàn tất 10/2029; nghiệm thu toàn bộ 12/2031 (cafef 04/08/2026).
  - Dự án kéo dài gần 6 năm (baodauthau).

**Tỷ lệ thay thế φ (phần của 1.844 tỷ chỉ để thay công suất cũ). Cơ sở dữ liệu gồm hai mốc độc lập:**
1. **Xút:** công suất cũ **50.000 t NaOH 100%/năm**, chạy 90–100% (Tạp chí Công Thương 21/05/2025; di dời 3 giai đoạn 20k + 15k + 15k). Mục tiêu Nhơn Trạch là 100.000 t xút và 100.000 t H2SO4 (Đại biểu Nhân dân 26/09/2025; cafef 04/08/2026). ⇒ Với xút, φ ≈ **0,5**.
2. **Tổng sản lượng:** "sản phẩm chủ yếu sản xuất" năm 2021 là **245.949 t** (BCTN 2021, PDF trang 18; `src/bctn_2021_vietstock.pdf`, md5 `4ff91a0a…`). Chia cho 307.900 t ra **0,80**. Đây là **cận trên**, vì đơn vị 2021 không ghi "quy 100%" (tấn thương phẩm thường lớn hơn tấn quy 100%). Mặt khác, công suất thiết kế cũ có thể cao hơn sản lượng thực.

⇒ Trục φ = **0,5 / 0,65 / 0,8**, trọng số 0,25/0,5/0,25 (ước lượng, đối xứng quanh điểm giữa hai mốc). Công suất cũ chính xác theo từng sản phẩm **không kiểm chứng được** (BCTN 2022–2025 chưa lấy được; BCTN 2021 không có bảng công suất). Ảnh hưởng: **±1.406 đ/cp cho mỗi 0,1 φ**.

**Công thức base r3** (tỷ đồng, chia 110,50 triệu cổ phiếu):
`Giá trị = (E·(1+dE) − lãi tiền gửi sau thuế)·(1 − 2,43%)/r + tiền ròng 484,69 − CĐKKS 49,96 + (1−φ)·346,48 − φ·1.497,52/(1+r)^t + npv·(1−φ)·1.844`
- **Phần thay thế** (φ):
  - Phần **đã chi** (φ × 346,48) là chi phí chìm của việc giữ công suất cũ, nên **không cộng lại**. Tiền ròng đã đo sau khi chi.
  - Phần **còn phải chi** (φ × 1.497,52) là dòng tiền ra, chiết khấu về hiện tại theo t ∈ {0,5; 1,75; 3,0} năm (trọng số 0,25/0,5/0,25). Cơ sở là lịch ở trên: chi đều từ Q4/26 tới 2030, trung điểm khoảng 1,75 năm.
- **Phần tăng trưởng** (1 − φ): theo **NPV = 0 giá sổ sách**. Phần đã chi cộng lại theo giá vốn; phần còn chi được đối ứng bằng giá trị tương đương. Trục NPV ±20% chỉ áp lên phần tăng trưởng, đối xứng, kỳ vọng bằng 0.
  - Phía (−): Bobby nêu công suất xút nội địa có thể tăng từ 230 lên 430–500 nghìn t.
  - Phía (+): cầu alumina.
- **Không đếm hai lần:** E_core vốn hoá vĩnh viễn chỉ hợp lệ khi đã trả tiền thay nhà máy. Không trừ thêm khấu hao mới, vì capex đã trừ bằng tiền. Không trừ thêm lãi vay mới, vì capex dùng vốn vay cũng là dòng tiền ra của vốn chủ khi đo bằng tiền ròng.
- **Tại tham số trung tâm** (φ 0,65, t 1,75, kịch bản CƠ SỞ):
  - Phần thay thế còn chi có PV = 779,9 tỷ ≈ **−7.058 đ/cp**.
  - Phần tăng trưởng đã chi 121,3 tỷ ≈ **+1.097 đ/cp**.

**Bồi thường và đất:**
- **Bồi thường BH1:** chỉ có bồi thường cây trồng 195 triệu cộng thưởng 8 triệu (QĐ 1618 ngày 08/09/2025, theo cafef), không trọng yếu. Không có số bồi thường cho nhà xưởng hay máy móc. Đất BH1 thuê lại của Sonadezi. **Base = 0**, độ nhạy +100 tỷ ⇒ **+890 đ/cp**.
- **Đất TP.HCM** (đã đọc TB 610/TB-UBND ngày 15/10/2026, `src/thuhoi_dat_HCM_20261019.pdf` p2): khu 5.845 m² tại 1/180 A1 Đông Hưng Thuận là **đất THUÊ** theo HĐ 5899/HĐ-TĐ 1996. Bị thu hồi theo khoản 2 Điều 82 Luật Đất đai 2024 vì "không còn nhu cầu, **tự nguyện trả lại**"; công ty chỉ phải xử lý tài sản trên đất trong 15 ngày. Thông báo **không có điều khoản bồi thường** ⇒ giá trị 0 là có cơ sở, không phải hạng mục bị bỏ sót.

## 5. Vị thế và lợi thế cạnh tranh (5F tầng b) — TÁI DÙNG (< 12 tháng)
- `data/moat_tags.csv`, asof 2026-06-05: **NARROW · COST/SCALE**, nhà sản xuất xút–clo phía Nam, price-taker.
- Kiểm nhanh: (1) lực hành chính là di dời bắt buộc; (2) đối thủ nội địa đang tăng công suất xút (Bobby); (3) ROE_Min5Y 13,66% ≈ Ke.
- ⇒ Giữ **NARROW, không thưởng**, terminal RONIC = Ke (D4).
- Độ nhạy thưởng moat (RONIC 18,3%, g 4%): tâm 12.492, vẫn TRÊN vùng.
- Đề xuất `risk1`: "di dời bắt buộc BH1 → Nhơn Trạch 1.844 tỷ; phần thay thế công suất (φ ~0,5–0,8) là capex tuân thủ".

## 6. Định giá
- **Chi phí vốn (V1):**
  - r = 13,5% + 1,0 × (7,40% − 7,40%) = **13,50%**. Lãi huy động lấy từ `deposit_rate_vn.effective_deposit_rate('2026-11-23')` = cctg_12m(2026-11-02) 7,40% (Big-4 6,8%), neo 03/11.
  - Độ nhạy theo lãi huy động (tâm sau CK 5 tỷ): −100bp **11.984** (+8,5%), −50bp 11.492 (+4,1%), +50bp 10.624 (−3,8%), +100bp 10.239 (−7,3%).
  - Với β = 0,5: ±100bp cho 11.492 / 10.624.
  - **Hai đầu dải Ke nội địa (D4):** Ke 12,3% cho 12.193; Ke 13,4% cho 11.129.
- **Ba kịch bản** (trọng số 0,25/0,5/0,25, ước lượng; dE ±10%). Giá trị/cp trước CK tại tham số trung tâm:
  - XẤU — LN 179,7 (đáy xút 2020): **7.589**
  - CƠ SỞ — LN 235,0 (TB 2019–25): **11.206**
  - TỐT — LN 294,5 (TTM, cú sốc axit duy trì): **15.099**
- **Lưới tính:** 243 kết cục = kịch bản (3) × dE (3) × φ (3) × thời điểm chi (3) × NPV tăng trưởng (3). Phân vị lấy theo trọng số. Kết quả sau CK 5 tỷ: min 2.121, max 21.223.

**Độ nhạy** (tâm sau CK 5 tỷ; không đổi headline):

| Độ nhạy | Tâm | So với base 11.041 |
|---|---|---|
| φ = 1,0 (skeptic: 100% thay thế) | 6.202 | −43,8% |
| φ = 0,8 | 8.968 | −18,8% |
| φ = 0,5 | 13.115 | +18,8% |
| φ = 0,33 | 15.465 | +40,1% |
| φ = 0 (cách a của r2, cộng thêm các khoản trừ quỹ) | 20.027 | +81,4% |
| Không chiết khấu thời gian cho capex còn chi (t = 0) | 9.363 | −15,2% |
| Thay thế lặp lại mỗi 30 năm (vĩnh viễn) | 10.845 | −1,8% |
| Ứng trước ~200 tỷ là của Nhơn Trạch (G2, chưa xác nhận) | 12.596 | +14,1% |
| Bồi thường BH1 +100 tỷ | 11.931 | +8,1% |
| Gián đoạn 0/−25/−50% một năm LN lõi (0,4/0,4/0,2) | 10.688 | −3,2% |
| Gián đoạn như trên + bồi thường 100 tỷ | 11.578 | +4,9% |
| Thưởng moat (RONIC 18,3%, g 4%) | 12.492 | +13,1% |
| Không trừ số dư quỹ KTPL/KH&CN (như r2) | 11.405 | +3,3% |

Không độ nhạy nào, kể cả khi ghép thuận lợi nhất (φ = 0,5 + G2 + bồi thường + moat ≈ 16–17k [ước lượng, chưa chạy cộng gộp]), đưa tâm lên tới giá 20.300.

**V6 — Hai nền giá trị (chỉ hiển thị):**
- V_ngắn (LN trung vị 2023–25 = 209,2 tỷ, g = 0, cùng cầu nối vốn) = **9.359** sau CK.
- V_dài (FCFE): **FCFE ≤ 0** trong giai đoạn capex. CFO 9T 197,8 trừ capex 265,7 ra số âm, và còn khoảng 1.498 tỷ phải chi. ⇒ Theo luật chỉ báo V_ngắn; dòng tiền âm là do đầu tư (thay thế cộng tăng trưởng). Không tính D, không có cờ phân kỳ.
- Không ghi các số này vào sổ.

**Đối chiếu nhanh (sau khoá):**
- P/E giá / LN chuẩn hoá 9,5x; P/E TTM 7,6x; P/B mẹ 1,23x.
- Cờ "DCF auto CHEAP" của hệ là **nhiễu về kết luận**: nó vốn hoá thu nhập gần đỉnh mà không trừ capex thay thế.

## 7. Thanh khoản và sizing (V3, V8) — sau khoá
- **Số liệu:** σ ngày **2,25%**, ADV250 (trung vị Price × Volume, cửa sổ 19/11/2025–20/11/2026) **8,88 tỷ**, ADV60 7,32 tỷ.
- **Chiết khấu thanh khoản = σ × √(Q/ADV250):**
  - 5 tỷ: **1,69%**. Q/ADV = 56%, ngoài vùng hiệu chỉnh của luật căn bậc hai, nên chỉ là chỉ dấu.
  - 1 tỷ: 0,76%. 40 tr: 0,15%.
- **Thời gian thoát lệnh:** 5 tỷ mất 5,6 phiên ở tỷ lệ tham gia 10% (2,8 phiên ở 20%); 1 tỷ mất 1,1 phiên ở 10%.
- Free float ≤ 35%.
- **Nhãn không đổi theo cỡ:** TRÊN vùng ở mọi cỡ.
- **Sizing V8 (chuẩn 2–4% NAV/mã):** **0% tại giá hiện tại.** Nếu giá ≤ 9.385 (luật 4) và không có tin xấu mới thì xét 2% NAV, trần 4%. Khẩu phần ≤ 1 tỷ mỗi phiên.

## 8. Rủi ro và mốc đổi nhận định CẢ HAI chiều
| Chiều | Mốc (kiểm bằng BCTC/CBTT) | Tác động |
|---|---|---|
| **NÂNG** | Công ty công bố công suất cũ theo sản phẩm, hoặc cơ cấu 307.900 t cho thấy phần tăng trưởng lớn (φ < 0,5) | Mỗi −0,1 φ ⇒ +1.406 đ/cp |
| NÂNG | Thuyết minh xác nhận ~200 tỷ trả trước là thiết bị Nhơn Trạch (G2) | +1.555 đ/cp |
| NÂNG | Công bố bồi thường di dời BH1 | +890 đ/cp mỗi 100 tỷ |
| NÂNG | LN mẹ Q4/26 ≥ 70 tỷ **và** Q1/27 ≥ 60 tỷ sau khi lưu huỳnh đã giảm | Dời trọng số sang TỐT (TỐT tại tham số trung tâm 15.099) |
| NÂNG | Lãi huy động 12T −100bp | +943 đ/cp (11.984) |
| **HẠ** | Vượt dự toán 1.844 tỷ hoặc trễ trên 6 tháng (có tín hiệu cụ thể) | Phần thay thế còn chi tăng; trục NPV (−) |
| HẠ | Biên gộp quý < 20% hoặc LN mẹ quý < 40 tỷ trong giai đoạn di dời | Dời trọng số sang XẤU / kích hoạt độ nhạy gián đoạn |
| HẠ | Công bố cho thấy φ ≈ 1 (Nhơn Trạch chỉ thay thế) | Tâm ≈ 6.202 |
| HẠ | Lưu huỳnh/axit tiếp tục giảm (Bobby forecast `sulfur`) | Xác nhận TTM không bền |

**HARD ABANDON:** kiểm toán ngoại trừ BCTC 2026; dừng sản xuất trên 1 quý mà không có công suất thay thế; vay để chia cổ tức.

## 9. Pháp lý, quản trị, kiểm toán (chỉ WARNING, không đưa vào tâm)
- **Cưỡng chế BH1 / dừng TB2:** đây là thi hành đề án chuyển đổi KCN, không phải xử phạt. Hệ quả kinh tế của nó (capex thay thế) **đã nằm trong base qua D3**. Còn rủi ro gián đoạn chỉ là độ nhạy.
- **Thu hồi đất HCM:** đã đọc, xem §4. Không có bồi thường, giá trị 0.
- **Ý kiến kiểm toán — Taylor tự đọc ngày 23/11** (render trang PDF scan vào `src/png_r3/`):
  - BCTC hợp nhất FY2025: báo cáo kiểm toán độc lập số **041/2025/BCTCHN-FAC** ngày 23/02/2026, **chấp nhận toàn phần, không có đoạn nhấn mạnh** (`fy2025_p5/p6.png`).
  - Soát xét 6T/2026: số **044/2026/BCTCHN-FAC** ngày 27/07/2026, kết luận **chấp nhận toàn phần** (`h1_p5.png`).
  - `audited_fy_missing = false`.
- **Giao dịch bên liên quan:** chủ yếu với các công ty cùng Vinachem; dịch vụ từ Thiết kế CN Hoá chất 17,6 tỷ trong 9T. Các NQ HĐQT chấp thuận giao dịch NCLQ năm 2026 (số 02, 04, 07, 08) **không kiểm chứng được** trong phiên này, vì nội dung NQ không có trong `src/`. Ảnh hưởng ước lượng: giá trị giao dịch 9T nhỏ (dưới 1% doanh thu), tác động lên tâm dưới 1% [ước lượng].
- **Nhân sự:** đổi Chủ tịch ngày 25/04/2026; đổi người phụ trách KTNB ngày 06/07/2026.
- **GAPS còn mở:**
  - G2: trả trước 242,4 tỷ.
  - G3: hàng thương mại 350 tỷ.
  - G4b: lịch chi capex theo năm.
  - G6: nguồn H2SO4.
  - Mới: cơ cấu 307.900 t theo sản phẩm và công suất thiết kế cũ (quyết định φ).

## 10. Cờ tự động của hệ
| Cờ | Đánh giá |
|---|---|
| W IDIOCRASH 2026-07-27 | NHIỄU về cơ bản. Giá chạm sàn −6,98% trong khi VNINDEX −1,01%; CTS/MBS/VND cũng bị cờ cùng ngày (r2 E6, không đổi) |
| ROE5Y 18,3% | Thật nhưng dễ hiểu sai: gồm đỉnh 2022, và **chưa gánh khấu hao/capex thay thế** (TSCĐ còn lại chỉ 37,1 tỷ) |
| DCF auto CHEAP ~29.479 | **Nhiễu về kết luận**: thu nhập gần đỉnh và không có capex thay thế |
| moat NARROW | Thật, tái dùng |
| ADV3T ~6 tỷ | Thật; ADV250 8,88 tỷ |

## 11. Giả định [ước lượng] / tự đặt (đầy đủ ở `calc/assumptions_r3.json`)
- Trọng số kịch bản 0,25/0,5/0,25; dE ±10%.
- **φ 0,5/0,65/0,8** (0,25/0,5/0,25). Hai mốc nguồn ở §4; điểm giữa là ước lượng.
- **Thời điểm chi 0,5/1,75/3,0 năm** (0,25/0,5/0,25).
- NPV phần tăng trưởng ±20% (0,2/0,6/0,2), kỳ vọng 0.
- Lãi tiền gửi sau thuế 32,65 tỷ/năm (9T × 4/3 × 0,8).
- Trích quỹ 2,43% LNST (số đọc trên TM17a, không phải giả định).
- Bồi thường = 0; RONIC = Ke.

## 12. File (r3)
- `REPORT_r3.md` (bản này).
- `calc/assumptions_r3.json`, `calc/LOCK_r3_prerun.txt`, `calc/model_r3.py`, `calc/run1_r3.txt` / `run2_r3.txt`, `calc/model_r3_out.json`.
- `calc/postlock_r3.py` / `_out.json` / `_out.txt`, `calc/px_csv_r3.csv` / `.sql`, `calc/lock_v1_r3.json`, `calc/LOCK_r3_post.txt`.
- `src/bctn_2021_vietstock.pdf` / `.txt` (mới), `src/png_r3/` (trang kiểm toán, soát xét).
- Bản cũ giữ nguyên: `REPORT.md` (r2), `REPORT_r1.md`, `ERRATA_r1_skeptic.md`, `calc/model.py`, `calc/assumptions.json`.

Nguồn web: [cafef 04/08/2026](https://cafef.vn/sau-cuong-che-cong-ty-hoa-chat-2400-ty-tren-san-phai-dung-nha-may-sau-ngay-15-8-188260804081236249.chn) · [danchuphapluat 18/08/2026](https://danchuphapluat.vn/hoa-chat-co-ban-mien-nam-loi-nhuan-6-thang-but-pha-nha-may-hoa-chat-nhon-trach-tang-toc-ve-dich-10156.html) · [baodauthau 03/07/2025](https://baodauthau.vn/cong-ty-cp-hoa-chat-co-ban-mien-nam-du-kien-dau-tu-1840-ty-dong-xay-nha-may-tai-nhon-trach-post181151.html) · [Đại biểu Nhân dân 26/09/2025](https://daibieunhandan.vn/khoi-cong-nha-may-hoa-chat-nhon-trach-buoc-ngoat-phat-trien-cua-hoa-chat-co-ban-mien-nam-10388014.html) · [Tạp chí Công Thương 24/09/2025](https://tapchicongthuong.vn/hoa-chat-co-ban-mien-nam--khang-dinh-vi-the-voi-du-an-nha-may-hoa-chat-nhon-trach-239793.htm) · [Tạp chí Công Thương 21/05/2025 (xút 50.000 t)](https://tapchicongthuong.vn/gia-xut-thiet-lap-nen-gia-moi--hoa-chat-co-ban-mien-nam--csv--huong-loi-lon-140693.htm) · [BCTN 2021 (vietstock)](https://static2.vietstock.vn/vietstock/2022/3/30/20220330_20220330___csv___bctn_2021.pdf)

## Phụ lục E · Đính chính so với r2 (từng hạng mục skeptic DD_GENERAL r1, 22/11)
| # | Hạng mục skeptic | Xử lý trong r3 | Loại |
|---|---|---|---|
| E1 | **Đếm hai lần**: E_core của BH1 bị vốn hoá vĩnh viễn, cùng lúc Nhơn Trạch được tính NPV = 0 cộng phần đã chi | Dựng theo cách (b). Phần thay thế φ: đã chi không cộng lại, còn chi là dòng tiền ra (PV). Phần tăng trưởng: NPV = 0 giá sổ sách. Tâm 20.717 → **11.041** | (a) đưa vào base, có nguồn |
| E2 | Thiếu công suất BH1 cũ | Có 2 mốc độc lập: xút 50k t (TCCT 21/05/2025) và tổng SX 2021 245.949 t (BCTN 2021 p18) ⇒ trục φ 0,5/0,65/0,8. Công suất cũ chính xác theo sản phẩm: **không kiểm chứng được**, ảnh hưởng ±1.406 đ/cp mỗi 0,1 φ | (a) dải + (c) |
| E3 | Thiếu lịch đóng BH1 / chạy Nhơn Trạch (G4) | Dùng lịch từ cafef và danchuphapluat ⇒ trục thời điểm chi 0,5/1,75/3,0 năm. Lịch chi theo năm vẫn thiếu | (a) + (b) |
| E4 | Bồi thường BH1 = 0 và đất HCM chưa đọc | Đất HCM đã đọc: đất thuê, tự nguyện trả lại, không bồi thường ⇒ 0 có cơ sở. Bồi thường BH1 chỉ có 195 triệu cây trồng ⇒ base 0, độ nhạy +100 tỷ (+890 đ/cp) | (a) / (b) |
| E5 | Quỹ khen thưởng phúc lợi | Trừ số dư quỹ KTPL 25,92 + KH&CN 15,00 khỏi tiền ròng; trừ trích 2,43% LNST khỏi dòng tiền (TM17a). Tác động khoảng −690 đ/cp | (a) có nguồn |
| E6 | NQ giao dịch NCLQ chưa đọc | **Không kiểm chứng được**; ảnh hưởng ước lượng dưới 1% | (c) |
| E7 | Nguồn: `src/` và file dữ liệu mất; mtime của assumptions.json | Khôi phục từ git `b01861a67^` (TRIM_DD ngày 19/11, commit b01861a67): `fin_csv_bq.csv` md5 ff723f56…, `assumptions.json` f27491d7…, `model.py` 12808ac0… đều **khớp `LOCK_post_md5_r2.txt`**. Như vậy nội dung không đổi; mtime 20/11 là do checkout lại, không phải do sửa. Thêm BCTN 2021 vào `src/` | đã đóng |
| E8 | Ý kiến kiểm toán FY2025 ghi theo errata, chưa tự kiểm | Đã tự đọc FY2025 (041/2025, chấp nhận toàn phần, không nhấn mạnh) và soát xét 6T (044/2026, chấp nhận toàn phần) | đã đóng |
| E9 | 110.499.910 cổ phiếu không ghi ngày/nguồn | Mã 411 BCĐKT 30/09/2026 / 10.000 đ | đã đóng |
| E10 | r2 chưa từng được phản biện lại | r3 chạy `dd_skeptic_run.py` (verdict ở `skeptic/r2.json`) | quy trình |
| E11 | Chiều ngược: phần công suất tăng thêm, nền Q4 thấp | Phần tăng trưởng (1−φ) được tính NPV = 0 và cộng lại phần đã chi. Nền Q4 thấp nằm trong mốc NÂNG ở §8. Kịch bản TỐT giữ nguyên | (a)/(b) |
| E12 | G7: cổ tức 21,17 tỷ | TM17a: 21,14 tỷ là cổ tức của **CĐKKS** ⇒ đóng | đã đóng |

**Cầu nối tâm r2 → r3** (sau CK 5 tỷ):
- r2: 20.717 (giá 06/11, CK 1,69%).
- Thêm trừ quỹ KTPL/KH&CN và trích 2,43% LNST, với φ = 0: **20.027**.
- Thêm D3 (φ 0,5/0,65/0,8, PV capex thay thế còn chi), chỉ cộng lại phần tăng trưởng của khoản đã chi: **11.041**.

**Phải phản biện lại (B2):** tâm dịch −46,7% (> 5%) và nhãn đổi từ TRONG sang TRÊN vùng.

**Định giá vẫn mù giá:** khoá lúc 07:17:59, rồi mới truy vấn giá lúc 07:18:16. Thứ tự tạo file có thể kiểm bằng mtime `LOCK_r3_prerun.txt` < `px_csv_r3.csv`. `lock_v1_r3.json` được viết sau khi đọc giá, nhưng chỉ là bản sao theo schema của `assumptions_r3.json` (không thêm tham số giá; số trong `projects` là φ tâm × số đã khoá).
