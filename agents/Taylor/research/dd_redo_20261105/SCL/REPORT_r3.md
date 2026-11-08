# SCL — DD redo VÒNG 3 · giá đóng cửa 06/11/2026 (CUM-quyền) · job `Taylor_20261108_142022`

Áp đính chính `TOP5_CORRECTIONS_20261108.md` §SCL, sau khi kiểm từng điểm bằng calc. Thay REPORT_r2 (headline 22.769 mang lỗi GPM).
Calc: `calc_r3/model_scl_r3.py` (chạy 2 lần trùng byte: out.json `73a84983…`, out.txt `75145594…`) · `calc_r3/make_summary_r3.py` (`63eff2f8…`) · LOCK `calc_r3/LOCK_r3_md5.txt` (13 file upstream).

## 0. Kết luận

| | Tâm | P10 | P50 | P90 | Giá 06/11 | % trọng số dưới giá | Nhãn |
|---|---|---|---|---|---|---|---|
| **Headline r3** (lõi sửa GPM, E1, CK sleeve 40tr 0,84%) | **23.652** | **18.986** | **23.202** | **28.854** | 29.400 (cum) | 91,7% | **TRÊN vùng (>P90) — SÁT RANH GIỚI** |
| Cùng mô hình, CK 5 tỷ (4,45%, ngoại suy) | 22.791 | 18.295 | 22.357 | 27.803 | 29.400 | 96,7% | TRÊN |
| Sau quyền, CK 40tr (so TERP 27.139) | 22.146 | 18.104 | 21.756 | 26.651 | 27.139 | — | TRÊN |
| r2 (để so) | 22.769 | 17.348 | 23.312 | 27.119 | 30.000 (04/11) | 98,4% | TRÊN |

**Ở cỡ tham chiếu 5 tỷ (CK 4,45%, ngoại suy ngoài vùng hiệu chỉnh √): tâm 22.791 · P10 18.295 · P50 22.357 · P90 27.803 · 96,7% trọng số dưới giá · nhãn TRÊN vùng.** Headline ở trên dùng cỡ sleeve 40 triệu; các mã khác trong đợt DD này báo ở cỡ 5 tỷ, nên so chéo mã phải đọc dòng này.

- Giá cao hơn tâm **+24,3%** và cao hơn P90 chỉ **+1,9%**. Nhãn không đổi so với r2; định nghĩa vùng P10–P90 cũng không đổi qua r1–r3 (nhãn không đổi KHÔNG phải do đổi định nghĩa vùng).
- Tâm tăng **+883 đ/cp (+3,9%)** so với r2. Các bước được tách ở §2.
- n = 108 kết cục. Min 17.044, max 33.261.
- Tâm 23.652 cao hơn P50 23.202 vì đuôi phải do STRUCTURAL kéo. Giá trị tại tham số trung tâm là 24.146.
- P10 hoàn toàn do nhánh CYCLICAL. Vùng quanh P90 gồm STRUCTURAL 0,625 và ADMIN_GATED 0,375.
- **Không đủ điều kiện sleeve fear-buy §2.5:** giá TRÊN vùng, không phải trạng thái sợ hãi.

## 1. Kiểm từng đính chính

| # | Đính chính skeptic | Kết quả kiểm | Bằng chứng |
|---|---|---|---|
| 1 | Headline phải dùng lõi sửa GPM (21.813) | **ĐÚNG** — đã áp | `bigquery_dictionary.json`: GPM_P0 là TTM. Chân đối chứng S1 tái lập **21.813 / P90 26.672**, trùng skeptic đến từng đồng |
| 2a | Bội số áp lên E0 thay vì E1 (~−880) | **ĐÚNG** — áp vào headline | (1−g/ROE)/(r−g) là P/E kỳ tới (V0 = D1/(r−g)). E0 = TTM tới 30/09. Hiệu ứng **+881** |
| 2b | CK 4,5% ở cỡ 5 tỷ là ngoại suy (~+840) | **ĐÚNG** — headline dùng sleeve 40tr, 5 tỷ báo song song | Cỡ 5 tỷ = 213% ADV120 (2,35 tỷ), ngoài vùng √. 40tr = 1,7% ADV, trong vùng. Hiệu ứng **+861** (ADV cập nhật tới 06/11) |
| 2c | Trục lỗ phải thu [UL] đang nằm trong base (~−90) | **ĐÚNG** — chuyển sang độ nhạy | BCTC V.3: Vincons 67,892 tỷ, dự phòng 0, kiểm toán 2025 chấp nhận toàn phần, nên base = sổ sách. Hiệu ứng **+86** |
| 2 | Gộp 3 khoản ⇒ P90 ~28.800 | **ĐÚNG** | P90 **28.854** |
| 2 | Có IRR Phả Lại ⇒ P90 ~29.350 | **KHÔNG tái lập được** — giữ số của tôi | Cùng headline, thêm trục IRR 10/13,5/17% (0,25/0,5/0,25): P90 **28.902** < giá. Tôi cộng 262,9×(IRR/r−1) và không nhân (1+g); skeptic có lẽ dùng quy ước khác. Hai số đều < 29.400 nên **không đổi nhãn** |
| 2 | Nhánh TROUGH + khung nợ mệnh giá kéo tâm xuống ~1.100–1.200 | **ĐÚNG hướng, chưa khớp độ lớn** | Khung r3 (E1, CK 40tr): TROUGH −1.527, nợ mệnh giá −1.160, gộp −2.688 (tâm 20.964). Ở khung r2, TROUGH là −1.121. Mức gộp −2.688 gấp ~2,3 lần ước tính của skeptic (~1.100–1.200); **chênh lệch này chưa được giải thích hết** (chưa đối chiếu khung/quy ước của skeptic với khung r3). Hướng và nhãn không đổi |
| 3 | Câu 5F §5 'không sát ranh giới' | **ĐÚNG** — đã sửa `ADDENDUM_5F.md` | Giá/P90 headline +1,9% |
| 4 | So cùng cơ sở; lịch quyền | **ĐÚNG**; lịch đã xác nhận | So giá cum với giá trị trước quyền, TERP với giá trị sau quyền (§0). NQ **1363/NQ-HĐQT 26/10/2026** (PDF gốc của công ty, `dd_SCL_20261029/src`): ĐKCC 10/11; chuyển nhượng quyền 17/11–03/12; đăng ký + nộp tiền 17/11–08/12. Hai mốc báo chí là **hai hạn khác nhau**, không mâu thuẫn. NQ không có cổ phiếu thưởng. Cổ tức cổ phiếu ĐKCC 10/06/2026 (HNX) đã nằm trong vốn góp 388,4 tỷ |
| 5 | Bảng cân đối chỉ truy về PDF scan | **ĐÃ KIỂM** bằng `fitz` render trang + đọc ảnh (không có OCR) | BCTC HN Q3/2026 trang 1–2, 17, 19: VCSH 533,638 (CĐKKS 2,022); vay NH 259,737 + DH 156,724; tiền 95,103; phải thu KH 115,970; **Vincons 67,892 (58,54%)**; XDCB 206,627 (Phả Lại 177,999 + 12,652; tách tro GĐ2 14,817). Khớp hằng số lõi. **LCTT (CFO 9T 9,9) chưa đọc lại ở r3** |

## 2. Bridge r2 → r3 (tâm sau CK, đ/cp cum)

Mỗi bước chỉ đổi một yếu tố, theo đúng thứ tự dưới.

| Bước | Tâm | Δ | P10 | P90 | Lý do |
|---|---|---|---|---|---|
| S0 r2 headline | 22.769 | — | 17.348 | 27.119 | Đối chứng, tái lập byte |
| S1 sửa GPM | 21.813 | −956 | 17.348 | 26.672 | GPM_P0 là TTM nên GPM năm = Q4 |
| S2 giá + ADV tới 06/11 | 21.824 | +11 | 17.357 | 26.685 | CK 5 tỷ 4,50% → 4,45% |
| S2b phải thu theo số BCTC | 21.824 | 0 | | | 67,892 thay cho 116,0×58,5% |
| S3 bỏ trục phải thu [UL] | 21.910 | +86 | 17.541 | 26.704 | Không có dữ liệu cho xác suất lỗ |
| S4 E1 = E0×(1+g) | 22.791 | +881 | 18.295 | 27.803 | Quy ước P/E kỳ tới |
| **S5 CK sleeve 40tr** | **23.652** | +861 | 18.986 | 28.854 | 5 tỷ nằm ngoài vùng √ |

Tâm đổi qua ba vòng (22.855 → 22.769 → 23.652; giảm nhẹ ở r1→r2, tăng ở r2→r3) mà không có thông tin kinh doanh mới. Toàn bộ thay đổi đến từ sửa lỗi dữ liệu và quy ước, như bảng trên.

## 3. Biến thể song song

Tất cả dùng E1 và cùng lõi.

| Biến thể | Tâm 40tr | P10 | P90 | % dưới giá | Tâm 5 tỷ | P90 5 tỷ |
|---|---|---|---|---|---|---|
| **Headline** | **23.652** | 18.986 | 28.854 | 91,7% | 22.791 | 27.803 |
| E0 thay E1 | 22.738 | 18.204 | 27.713 | 96,7% | 21.910 | 26.704 |
| + trục phải thu 0/20/50% (0,75/0,2/0,05 [UL]) | 23.562 | 18.915 | 28.822 | 92,2% | 22.704 | 27.772 |
| + IRR Phả Lại 10/13,5/17% | 23.652 | 18.901 | 28.902 | 91,0% | 22.791 | 27.849 |
| Đối xứng (+TROUGH 0,2) | 22.125 | 17.408 | 28.146 | 94,4% | 21.319 | 27.121 |
| Nợ theo mệnh giá | 22.492 | 17.866 | 27.717 | 96,7% | 21.673 | 26.708 |
| TROUGH + nợ mệnh giá | 20.964 | 16.166 | 26.893 | 97,8% | 20.201 | 25.914 |

Nhãn **TRÊN ở mọi biến thể và cả hai cỡ CK**. Khoảng tâm của các biến thể: 20.201–23.652.

**Lý do chọn headline:**
- E1 là đúng công thức, không phải lựa chọn tuỳ ý.
- Con số 4,45% ở cỡ 5 tỷ là ngoại suy ngoài vùng hiệu chỉnh, không có cơ sở dữ liệu.
- Trục phải thu, TROUGH và nợ mệnh giá chưa có dữ liệu hoặc lớp sector read làm cơ sở, nên chỉ để ở độ nhạy.

**Độ nhạy: phần cộng lại lãi dự án (nằm trong lõi headline, chưa có cơ sở dữ liệu vững):**
- Lõi tính dự án dở dang (Phả Lại + Vĩnh Hảo GĐ2) = giá vốn − nợ tài trợ = 0, rồi cộng lại lãi vay của nợ dự án vào E với lãi suất **4,96%** (= chi phí lãi Q3 5,167 tỷ ×4 / nợ cuối kỳ 416,5 tỷ).
- Thuyết minh chi phí đi vay được vốn hoá **chưa đọc**, nên 4,96% là lãi P&L trung bình, chưa tách phần vốn hoá vào dự án.
- Giả định 'nợ tài trợ dự án = giá vốn dự án' **trái dữ liệu**: nợ 330 → 417 tỷ (+87) trong khi XDCB 11 → 207 tỷ (+196) và tiền 188 → 95 tỷ (−93). Dự án được tài trợ cả bằng nợ lẫn tiền sẵn có, nên nợ dự án không bằng giá vốn.
- **Bỏ hẳn phần cộng lại này thì tâm 21.901, P90 27.150** (số từ skeptic độc lập; chưa chạy lại trong calc_r3). Nhãn vẫn TRÊN. Headline giữ nguyên 23.652 vì đây là cấu phần hiện hành của lõi; người đọc nên coi 21.901 là cận dưới của cấu phần này.

## 4. Giá ngụ ý

Để ra 29.400 (cum, CK 40tr, g 4%, ROE 17,5%, r 13,5%), cần **LN chuẩn hoá ~136,4 tỷ/năm vĩnh viễn**.
- So sánh: NP TTM 117,7; E TTM sau khi cộng lại lãi dự án 125,9; NP 2020–25 lần lượt 25/20/16/45/27/64 tỷ.
- Một cách đọc khác: biên TTM (đỉnh 7 năm) giữ vĩnh viễn kèm **r 12,77%**, tức lãi huy động ~6,67%.
- Skeptic ra 140,6 tỷ / r 11,1% theo quy ước E0 + CK 5 tỷ. Khác quy ước nhưng cùng hướng.
- Phản chứng: CFO 9T chỉ 9,9 tỷ so với LNST 94,4 tỷ.

## 5. Thanh khoản

| Cỡ | ADV | Q/ADV | CK |
|---|---|---|---|
| Sleeve 10 / 20 / 40 tr | ADV120 2,35 tỷ | 0,4–1,7% | 0,67% / 0,74% / **0,84%** |
| 5 tỷ | ADV120 2,35 / ADV250 1,32 / ADV60 3,35 tỷ | 213% / — / — | 4,45% / 5,78% / 3,81% (ngoài vùng √) |

## 6. Định giá — khung

Khung giữ nguyên lõi r3 (`calc/scl_r3_core_5Ffix.py`):
- LN chuẩn hoá chu kỳ × (1 − g/ROE)/(r − g) × (1 + g).
- Dự án dở dang tính theo giá vốn trừ nợ tài trợ, ròng bằng 0.
- Cộng lại lãi vay của nợ dự án (lãi P&L thực 4,96%).
- **r = 13,5%** = 13,5% + 1,0×(7,40% − 7,40%), lấy cctg_12m ngày 02/11, hiệu lực tại 06/11.

Các giả định khoá và cơ sở từng cái nằm ở `SUMMARY.json → assumptions`. Ba giả định là nhận định hoặc [UL]:
- trọng số chế độ ngành 0,5/0,3/0,2 (Bobby);
- mức quay về trung bình 1/0,5/0;
- g và ROE dài hạn.

**Độ nhạy r** (tâm, CK 40tr, β = 1):

| Δ lãi huy động | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| Tâm | 26.470 (+11,9%) | 24.981 | 22.459 | 21.380 (−9,6%) |

Gordon E1 (g 4%, ROE TTM 22,1%) cho 27.189 trước CK. Chỉ có một biến thể vì SCL không có lãi tiền gửi đáng kể.

## 7. ⚠️ WARNING pháp lý / quản trị

Mang theo đủ các cờ từ r2:
1. **Pha loãng:** 17,3 triệu cp (2023) → 44,84 triệu sau quyền, cộng ESOP 0,92 triệu.
2. **Vay bên liên quan:** 26 tỷ từ cổ đông lớn, lãi 10%.
3. **Phải thu tập trung:** Vincons chiếm 58,5% phải thu KH và chưa được dự phòng.
4. **Dòng tiền và đòn bẩy:** CFO yếu, nợ ròng 321 tỷ.
5. **Chưa thấy tin xử phạt/khởi tố SCL.** Đã WebSearch ngày 05/11 và 08/11/2026 trên [stockbiz](https://stockbiz.vn/tin-tuc/scl-ngay-dang-ky-cuoi-cung-tra-co-tuc-bang-co-phieu-cho-co-dong-hien-huu/40247189), [cafef](https://cafef.vn/song-da-cao-cuong-chao-ban-6-trieu-co-phieu-188261027151900881.chn) và [baophapluat](https://doanhnhan.baophapluat.vn/song-da-cao-cuong-scl-chao-ban-6-trieu-co-phieu-du-thu-75-ty-dong-de-tai-co-cau-nguon-von.html). WebSearch không thay được CBTT sàn.

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON

| Mốc | LÊN nếu | XUỐNG nếu |
|---|---|---|
| Quyền mua 17/11–08/12/2026 | Phát hành đủ, nợ ròng giảm 75 tỷ | Không phát hành hết |
| BCTC Q4/2026 (~20/01/2027) | LNST ≥ 38 tỷ, CFO ≥ LNST, phải thu giảm | Biên gộp TTM < 36%, phải thu tăng tiếp |
| Phả Lại vận hành (2027) | Có HĐ/sản lượng/giá ⇒ đưa IRR vào lưới | Trễ, vượt dự toán |
| Kiểm toán 2026 | Chấp nhận toàn phần | Ngoại trừ |

**Ngưỡng nhãn:** về TRONG vùng khi giá cum ≤ **28.854** (CK 40tr) hoặc ≤ 27.803 (CK 5 tỷ). Sau quyền: TERP ≤ 26.651.

**HARD ABANDON** khi có một trong các sự kiện:
- kiểm toán ngoại trừ về phải thu;
- lỗ phải thu Vincons > 50%;
- quyền mua bị huỷ hoặc đổi điều khoản.

## 9. Còn mở

- Không tái lập được P90 29.350 (bản có IRR) của skeptic; số của tôi là 28.902.
- Chưa đọc lại LCTT từ PDF.
- Chưa đọc thuyết minh chi phí đi vay vốn hoá; giả định nợ tài trợ dự án = giá vốn trái dữ liệu (xem §3, độ nhạy lãi dự án).
- Chênh lệch độ lớn nhánh TROUGH + nợ mệnh giá so với skeptic (−2.688 vs ~−1.150) chưa giải thích hết.
- Chưa có DT theo mảng, backlog, HĐ tro/thạch cao.

Không ghi `kb/dd_price_zones.json`, không email, không PDF, không lệnh.
