# DD REDO VÒNG 3c (vòng cuối) — SZL (Sonadezi Long Thành, HOSE) · job `Taylor_20261108_180625` · 09/11/2026

Đầu vào: `REPORT_r3b.md` + `calc_r3b/`. Skeptic cuối r3b kết luận REFUTED hẹp, chỉ ở **một** điểm số là khung KTPL trên cổ phần SZC/SZB, cộng vài lỗi văn bản. A (RONIC = Ke) giữ nguyên. Số trong file này lấy từ `calc_r3c/model_r3c_out.txt`: chạy 2 lần trùng byte, md5 `6a4cc7cd`. LOCK ghi **trước** lần chạy đầu: `calc_r3c/LOCK_r3c_prerun.txt` (2026-11-09T01:09:21+07:00, chỉ-đọc, đủ md5 upstream gồm r3/r3b, BCTC, file giá, wpct, lãi huy động). Minh bạch: giá 27.700 đã biết từ r3; file giá giữ nguyên của r3, không truy vấn lại.

## 0. Kết luận

| | r3b | **r3c base (khung BÁN)** | r3c song song (khung GIỮ) |
|---|---|---|---|
| Tâm, cỡ 5 tỷ (CK 4,12%) | 24.529 | **25.165** (+635; +2,6%) | 25.241 |
| P10 / P50 / P90, 5 tỷ | 22.301 / 24.372 / 27.074 | **22.936 / 25.008 / 27.710** | 23.013 / 25.085 / 27.786 |
| % trọng số dưới giá, 5 tỷ | 95,3% | **89,4%** | 89,1% |
| Nhãn 5 tỷ (tham chiếu) | TRÊN | **TRONG, ngay ranh giới** (P90 hơn giá 10 đ) | TRONG (P90 +86 đ) |
| Tâm, cỡ sleeve 40 tr (CK 0,37%) | 25.488 | **26.148** | 26.228 |
| P10 / P50 / P90, 40 tr | 23.173 / 25.325 / 28.133 | **23.833 / 25.985 / 28.793** | 23.913 / 26.065 / 28.872 |
| % dưới giá, 40 tr | 87,2% | **76,2%** | 76,1% |
| **Nhãn 40 tr (hành động)** | TRONG sát cạnh trên (−1,5%) | **TRONG** (giá thấp hơn P90 3,8%) | TRONG |
| Giá | 27.700 (06/11, BQ) | 27.700 | 27.700 |

- **Khớp skeptic.** Skeptic dựng lại lưới độc lập và cho các khoảng sau: tâm 5 tỷ 25.165–25.241, P90 5 tỷ 27.710–27.786, tâm 40 tr 26.148–26.228, P90 40 tr 28.793–28.872, ~76% dưới giá. Khung BÁN trùng cận dưới, khung GIỮ trùng cận trên, khớp từng số.
- Nhãn hành động là cỡ 40 tr: **TRONG**, nhưng 76% kết cục nằm dưới giá. Giá cao hơn tâm 5,9% (40 tr) / 10,1% (5 tỷ). Cỡ 5 tỷ ngoài vùng hiệu chỉnh CK (Q/ADV250 1.084%), chỉ để tham chiếu. Ở cỡ này nhãn coi như **đúng ranh giới TRONG/TRÊN**: ngưỡng N0 để chuyển sang TRÊN là 131,0, base là 131,08.
- **Không đủ điều kiện sleeve fear-buy §2.5** (giữ r2).

## 1. Sửa lỗi B — khung KTPL trên thu nhập cổ phần SZC/SZB

Thị giá cổ phần SZC + SZB ngày 06/11 là **486,4 tỷ**. Vốn gốc 284,8 tỷ, lãi vốn 201,6 tỷ, thuế lãi vốn 20% là 40,3 tỷ.

| Khung | Thuế lãi vốn | KTPL 11,2% trích trên | KTPL | **Tổng trừ** | Ròng |
|---|---|---|---|---|---|
| r3b (lỗi trộn khung) | 40,3 | (thị giá − thuế), **gồm cả vốn gốc** | 50,0 | 90,3 | 396,0 |
| **BÁN (base r3c)** | 40,3 | lãi vốn sau thuế 161,3 | **18,1** | **58,4** | **428,0** |
| GIỮ-NHẬN-CỔ-TỨC (song song) | 0 | PV cổ tức ≈ thị giá 486,4 | 54,5 | 54,5 | 431,8 |

- `model_r3b.py:76` tính `(MKT − TAX) × (1 − k)`, tức trộn hai khung. Thuế lãi vốn bị trừ theo kịch bản BÁN, nhưng KTPL lại trích trên toàn bộ giá trị sau thuế, gồm cả 284,8 tỷ hoàn vốn gốc. Phần hoàn vốn này không phải lợi nhuận nên không thuộc quỹ KTPL. Hệ quả: r3b bi quan **663 đ/cp** (so khung BÁN) / **743 đ/cp** (so khung GIỮ), tính trước CK.
- **Base = khung BÁN**, vì mô hình định giá cổ phần bằng thị giá trừ thuế lãi vốn. Trong khung này, thu nhập từ cổ phần chính là lãi vốn sau thuế. User đã duyệt nguyên tắc "áp KTPL nhất quán trên thu nhập cổ phần".
- **Khung GIỮ**: không có thuế lãi vốn, vì cổ tức nhận từ doanh nghiệp đã nộp TNDN là thu nhập miễn thuế TNDN. Căn cứ nêu theo hiểu biết là Luật TNDN 14/2008/QH12 Điều 4 khoản 6, **chưa tra** văn bản trong phiên này; Luật TNDN 67/2025/QH15 cũng **chưa tra**. KTPL trích trên toàn bộ dòng cổ tức, với PV dòng cổ tức xấp xỉ thị giá. Hai khung chỉ chênh **77 đ** ở tâm và không đổi nhãn.
- Độ nhạy B 50% (khung BÁN): tâm 25.344 (+180), TRONG ở cả hai cỡ.

**Cầu nối r3b → r3c** (control tái lập khớp cả r3 29.257 và r3b 24.529 / 40 tr 25.488):

| Bước | Tâm 5 tỷ | Δ vs r3b | P10–P90 5 tỷ | 5 tỷ | Tâm 40 tr | P10–P90 40 tr | 40 tr |
|---|---|---|---|---|---|---|---|
| r3b (control) | 24.529 | — | 22.301–27.074 | TRÊN | 25.488 | 23.173–28.133 | TRONG |
| **r3c: khung BÁN** | **25.165** | **+635** | 22.936–27.710 | TRONG | **26.148** | 23.833–28.793 | TRONG |
| (song song) khung GIỮ | 25.241 | +712 | 23.013–27.786 | TRONG | 26.228 | 23.913–28.872 | TRONG |

## 2. Độ nhạy (mỗi dòng đổi 1 trục so với base r3c)

| Biến thể | Tâm 5 tỷ | Δ | P10–P90 5 tỷ | 5 tỷ | P10–P90 40 tr | % dưới giá 40 tr | 40 tr |
|---|---|---|---|---|---|---|---|
| **HEADLINE r3c (A + B khung BÁN)** | **25.165** | 0 | 22.936–27.710 | TRONG | 23.833–28.793 | 76,2% | TRONG |
| Khung GIỮ-NHẬN-CỔ-TỨC | 25.241 | +77 | 23.013–27.786 | TRONG | 23.913–28.872 | 76,1% | TRONG |
| Chỉ A (B tắt) | 25.524 | +360 | 23.296–28.070 | TRONG | 24.207–29.167 | 74,1% | TRONG |
| Chỉ B (A tắt, RONIC ngầm ∞) | 28.897 | +3.733 | 25.850–32.346 | TRONG | 26.860–33.611 | 20,6% | TRONG |
| B ở 50% | 25.344 | +180 | 23.116–27.890 | TRONG | 24.020–28.980 | 76,1% | TRONG |
| KTPL 5% (lõi + lãi vốn cổ phần) | 26.537 | +1.373 | 24.279–29.283 | TRONG | 25.228–30.428 | 55,6% | TRONG |
| KTPL 8% | 25.875 | +710 | 23.631–28.524 | TRONG | 24.554–29.639 | 69,4% | TRONG |
| N0 = Q3×4 (138,5) | 26.007 | +842 | 23.652–28.696 | TRONG | 24.577–29.817 | 61,4% | TRONG |
| N0 = 2025 năm hoá (115,3) | 23.374 | −1.791 | 21.414–25.612 | TRÊN | 22.251–26.614 | 97,8% | **TRÊN** |
| Chỉ nhánh vĩnh viễn | 25.548 | +384 | 23.077–28.079 | TRONG | 23.979–29.176 | 72,5% | TRONG |
| Chỉ 27 năm | 25.037 | −128 | 22.748–27.564 | TRÊN | 23.637–28.642 | 77,5% | TRONG |
| Thời hạn 1/2–1/2 | 25.292 | +128 | 22.964–27.710 | TRONG | 23.862–28.793 | 75,0% | TRONG |
| Holdco 10% (SZC/SZB) | 24.313 | −851 | 22.085–26.858 | TRÊN | 22.948–27.908 | 89,1% | TRONG |
| Holdco 25% | 23.036 | −2.128 | 20.808–25.581 | TRÊN | 21.621–26.581 | 96,3% | **TRÊN** |
| Holdco ngụ ý P/B SNZ/SZC 45% (cận trên thô) | 21.318 | −3.846 | 19.090–23.863 | TRÊN | 19.836–24.796 | 99,8% | **TRÊN** |
| Capex duy trì 0,5× KH (+45/năm) | 31.647 | +6.482 | 29.254–34.286 | DƯỚI | 30.398–35.626 | 0,0% | **DƯỚI** |
| Capex duy trì 1,5× KH (−45/năm) | 18.682 | −6.482 | 16.459–21.046 | TRÊN | 17.102–21.869 | 100% | **TRÊN** |
| + BĐS đầu tư mới 166,9 theo giá vốn | 28.484 | +3.320 | 26.256–31.029 | TRONG | 27.282–32.242 | 19,4% | TRONG |
| Ký quỹ DH theo PV đến 2053 | 27.991 | +2.827 | 25.746–30.538 | TRONG | 26.752–31.732 | 23,0% | TRONG |

- Ở cỡ 40 tr, nhãn TRONG giữ qua mọi biến thể về khung/tỷ lệ B, KTPL, thời hạn, N0 = Q3×4 và holdco 10%. Nhãn đổi sang TRÊN khi: N0 bằng mức 2025, holdco ≥ 12,4%, hoặc capex duy trì 1,5× KH. Đổi sang DƯỚI chỉ khi capex duy trì 0,5× KH.
- **Đã bỏ** độ nhạy r3b "B cả cổ phần chưa niêm yết" (−253). Phần này ghi theo sổ sách nên không có lãi vốn trong khung BÁN, tức KTPL = 0, và độ nhạy đó không có cơ sở.
- Trục rộng nhất vẫn là capex duy trì (±6.482). BCTC không tách capex duy trì với capex mở rộng.

## 3. Giá ngụ ý và ngưỡng nhãn

Để tâm 5 tỷ = 27.700, chỉ cần **một** điều sau đúng: N0 = 153,4 tỷ (KTPL 11,2%), hoặc 131,5 khi KTPL 0%; hoặc KTPL ≈ 0% (−0,3%); hoặc r = 11,34% (base 13,50%); hoặc thêm +17,6 tỷ/năm dòng tiền.

Ngưỡng đổi nhãn (khung BÁN; khung GIỮ trong ngoặc):

| Trục | Cỡ 40 tr (hành động) | Cỡ 5 tỷ (tham chiếu) |
|---|---|---|
| N0 → TRÊN | < **123,2** (122,6) — base 131,1 cách −6,0% | < **131,0** (130,4) — **cách base 0,06%** |
| N0 → DƯỚI | > **169,6** (168,9) — base cách +29% | > 180,4 (179,7) |
| KTPL → TRÊN | > **15,8%** (15,0%) | — |
| KTPL → DƯỚI | < −6,4% (−1,8%) ⇒ **không đạt được** bằng KTPL | — |
| Dòng tiền thêm/năm (capex duy trì vs KH 90/năm) → DƯỚI | > **+26,9** tỷ (+26,3) ≈ capex duy trì ≤ 0,70× KH | — |
| Dòng tiền → TRÊN | < **−7,3** tỷ (−7,8) ≈ capex duy trì ≥ 1,08× KH | — |
| Holdco trên SZC/SZB → TRÊN | > **12,4%** (13,1%) | — |

So với r3b, các ngưỡng N0 127,9 / 135,8 ghi ở §3 của r3b đã **hết hiệu lực**. Độ nhạy lãi huy động (β = 1): −100bp ⇒ tâm +4,3%; +100bp ⇒ −3,8%.

## 4. Đính chính văn bản r3b

File r3b giữ nguyên (md5 nằm trong `calc_r3b/LOCK_r3b_post_md5.txt`); đính chính ghi ở đây.

1. `REPORT_r3b.md:41`: dòng "B cả cổ phần chưa niêm yết (= skeptic) 24.276" không có cơ sở (xem §2), r3c đã bỏ. Câu ở `REPORT_r3b.md:19` nói "trùng từng số với skeptic" chỉ cho thấy cả hai cùng áp B lên phần chưa niêm yết; trùng số không chứng minh quy ước đúng (skeptic cuối r3b xác nhận phần này KTPL = 0).
2. `REPORT_r3b.md:90` và `ADDENDUM_5F_SYNC_r3b.md:3` viện lý do "md5 nằm trong LOCK của DDV/PVT/NT2/PVP" để không sửa file, nhưng lý do này **SAI**. md5 hiện tại của `ADDENDUM_5F.md` (`83131c3e`) và `SUMMARY_5F.json` (`af090936`) không nằm trong LOCK nào: `grep -rl` trên mọi `LOCK*` dưới `dd_redo_20261105/` trả rỗng, kiểm 09/11. Hai file sync r3b còn liệt kê danh sách mã khác nhau (.md: DDV/PVT/NT2; .json: DDV/PVP/PVT/NT2). ⇒ r3c đã **sửa tại chỗ** `ADDENDUM_5F.md:1` và `SUMMARY_5F.json:32`, đồng thời thêm `headline_centre_current` cạnh `headline_centre_report_of_record`. Hai file sync được viết lại, thống nhất nội dung và ghi rõ đã bị thay. md5 trước khi sửa nằm trong LOCK prerun r3c.
3. `REPORT_r3b.md:91`: `REPORT_r3.md` (`b53be177`) **chỉ** nằm trong LOCK của chính SZL (`SZL/calc_r3/LOCK_md5.txt:20`), không phải "LOCK nhiều mã". File vẫn giữ nguyên, vì nó là bản ghi của r3 và đã được LOCK đó trỏ tới.
4. `model_r3b.py:76`: lỗi khung KTPL, xem §1.

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON — theo ngưỡng r3c

Nhãn hành động là cỡ 40 tr, hiện TRONG. "Lên" nghĩa là sang DƯỚI vùng (rẻ), "xuống" nghĩa là sang TRÊN vùng (đắt).

| Mốc | Ngày chấm | Lên (→ DƯỚI) | Xuống (→ TRÊN) |
|---|---|---|---|
| BCTC Q4/2026 | 31/01/2027 | LN lõi chạy ≥ 169,6 tỷ/năm (≈ 42,4/quý; +29% so base), một quý không đủ, cần Long Phước | LN lõi cả năm 2026 < **123,2** ⇔ Q4/2026 lõi < **24,9** tỷ (9T lõi 98,3) |
| NQ ĐHĐCĐ 2027 (KTPL trên LN 2026) | ~04/2027 | KTPL không đủ sức tự đưa sang DƯỚI (ngưỡng < 0%); bỏ mốc "KTPL ≤ 8% ⇒ DƯỚI" của r3 | KTPL > **15,8%** |
| LCTT 2026 + thuyết minh TSCĐ/BĐS đầu tư | 31/03/2027 (BCTC kiểm toán) | Capex duy trì ≤ **0,70× KH** có số (≈ +26,9 tỷ/năm) | Capex duy trì ≥ **1,08× KH** (≈ −7,3 tỷ/năm) |
| Long Phước cho thuê | 30/06/2027 | Hợp đồng thuê/đặt cọc có giá ⇒ NPV dương có cơ sở (BĐS mới theo giá vốn: +3.320, vẫn TRONG; cần thêm trục khác mới sang DƯỚI) | Đội vốn > 920 có số / chậm sau 2027 / D/E vay > 0,8 |
| Cổ tức SZC/SZB 2026 + thị giá | 2027 | giữ/tăng | Cắt cổ tức, hoặc thị trường áp holdco > **12,4%** lên cổ phần SZC/SZB |
| Quyết toán tiền thuê đất KCN Long Thành | khi có | hoàn nhập 44,3 | truy thu > 44,3 |
| Lãi huy động 12T (β = 1) | hằng tháng | −100bp ⇒ tâm +4,3% | +100bp ⇒ −3,8% |
| Thanh tra SNZ | — | — | kết luận nêu tên SZL ⇒ nâng WARNING |

**HARD ABANDON** (giữ r2, không đổi): (a) kết luận thanh tra/khởi tố chạm pháp nhân SZL hoặc tài sản KCN; (b) SZL cho bên liên quan vay/trả trước không bảo đảm > 100 tỷ; (c) Long Phước bị thu hồi/đình chỉ. Sleeve 10–40 tr ⇒ không tranche (chia ≥ 2 phiên vì 8,7% ADV250).

**Không đủ điều kiện sleeve fear-buy §2.5.**

## 9. Mở

- Điều luật miễn TNDN cổ tức giữa doanh nghiệp (khung GIỮ): **chưa tra**. Khung này không đổi nhãn (+77 đ).
- Chưa có NQ ĐHĐCĐ 2026 về tỷ lệ KTPL. Chưa tách capex duy trì/mở rộng, chưa tách doanh thu theo KCN (đồng hồ 2053), mốc 2053 chưa đối chiếu giấy phép.
- Pháp lý SNZ/Đồng Nai: chỉ **WARNING**, không vào base, chưa tra lại sau 05/11.
- Đây là vòng cuối (circuit-breaker), Mike kiểm cơ học. Không đặt lệnh, không sửa `kb/dd_price_zones.json`, không email.

## Tái lập

```bash
cd SZL/calc_r3c
$DNA_PYEXE -I model_r3c.py > model_r3c_out.txt     # 2 lần, cmp trùng byte (md5 6a4cc7cd); control in r3 29.257 + r3b 24.529
$DNA_PYEXE -I make_summary_r3c.py                  # SUMMARY.json (backup r3b: SUMMARY_r3b.json md5 cc861ebf); chạy 2 lần trùng byte
md5sum -c <(grep -v '^#' LOCK_r3c_prerun.txt | sed 's#  SZL/#  ../#; s#  _shared/#  ../../_shared/#; s#  TOP5C#  ../../TOP5C#; s#  STANDARD#  ../../STANDARD#')
# FAILED có chủ đích: SUMMARY.json (thay r3c), ADDENDUM_5F.md, SUMMARY_5F.json, ADDENDUM_5F_SYNC_r3b.md, SUMMARY_5F_SYNC_r3b.json (sửa tại chỗ, §4)
```
