# DD SZL (Sonadezi Long Thành, HOSE) — REV4 · 23/11/2026 · job `Taylor_20261123_003503` (resume `Taylor_20261123_050009`)

Bản này xử lý verdict skeptic DD_GENERAL r1 (22/11, INCONCLUSIVE) trên `REPORT_r3c.md`. File cũ giữ nguyên.

**Nguồn và tái lập.** Các tệp nguồn đã bị TRIM ngày 19/11 (commit `14ad1c925`). Rev4 khôi phục chúng từ git `fc5bd02d9` vào `rev4/restored/`:
- `src/Q3_2026_hopnhat.pdf`, md5 `6ef6a005…`
- `src/H1_2026_soatxet.pdf`, md5 `c36ddb57…`
- `calc*/`

Ảnh trang dùng để đọc thuyết minh nằm ở `rev4/png/`. Mô hình ở `rev4/calc/model_rev4.py`; giả định khoá ở `rev4/calc/assumptions_rev4.json`. Toàn bộ md5 upstream nằm trong `rev4/calc/LOCK_rev4_prerun.txt`, ghi **trước** lần chạy đầu.

**Định giá mù giá.** Giá 27.700 (06/11) đã biết từ r3/r3c. Rev4 **không truy vấn giá mới**: file giá cũ chỉ dùng để tính chiết khấu thanh khoản và gán nhãn. Không có giả định nào được chọn theo giá.

## 0. Kết luận

| | r3c | **rev4 base** |
|---|---|---|
| Tâm, cỡ 5 tỷ (CK 4,12%) | 25.165 | **27.397** (+2.232; +8,9%) |
| P10 / P50 / P90, 5 tỷ | 22.936 / 25.008 / 27.710 | **23.812 / 27.335 / 31.145** |
| Tâm, cỡ 40 tr (CK 0,37%) | 26.148 | **28.468** |
| P10 / P50 / P90, 40 tr | 23.833 / 25.985 / 28.793 | **24.742 / 28.404 / 32.362** |
| % trọng số kết cục dưới giá 27.700 (5 tỷ / 40 tr) | 89,4% / 76,2% | 54,9% / 40,0% |
| Nhãn (5 tỷ tham chiếu / 40 tr hành động) | TRONG / TRONG | **TRONG / TRONG**. Giá cao hơn tâm 1,1% ở cỡ 5 tỷ và thấp hơn tâm 2,7% ở cỡ 40 tr. |

- **Tâm tăng +2.232**, gồm bốn bước: CP tài chính đối xứng +131; BĐS đầu tư mới +1.707; ký quỹ dài hạn theo PV +1.956; N0 chuẩn hoá về biên chu kỳ −1.562.
- **Vùng rộng ra** (P10–P90 5 tỷ trải 7.333 đ, so với 4.774 đ ở r3c) vì ba trục mới có trọng số thay cho ba điểm cố định. Tâm cũ của r3c nằm trong vùng mới.
- **Luật sổ (giá < tâm − 15%): KHÔNG đạt.** Không đủ điều kiện sleeve fear-buy §2.5 (giữ r2).
- **Control:** với ba trục mới đặt về đúng lựa chọn của r3c, mô hình tái lập đúng 25.165 / 22.936 / 25.008 / 27.710 (40 tr: 26.148).

## 1. Đính chính so với r3c — từng hạng mục skeptic r1

| # | Hạng mục skeptic | Bằng chứng độc lập | Xử lý ở rev4 | Δ tâm 5 tỷ |
|---|---|---|---|---|
| 1 | Loại BĐS đầu tư mới 166,9 khỏi base, trong khi XDCB cộng theo giá vốn (bất nhất) | TM10 Q3 tr.20: nguyên giá tăng 166,887 (Nhà 166,225; CSHT 0,662). TM5.10 H1 soát xét tr.23: H1 tăng 101,677 ⇒ Q3 tăng 65,210. Một phần chuyển từ XDCB: nhà xưởng KCN Châu Đức 60,55 → 6,09 (TM8 tr.18). Tài sản **đã vận hành và đang khấu hao**. Theo H1, 327,4 tỷ BĐS ĐT còn lại đang thế chấp. | **(a) vào base** theo luật V4(a), NPV 0 theo giá sổ. Phần lợi nhuận đã nằm trong N0 phải trừ để không đếm hai lần: DC = 101,7×6/9 + 65,2×1,5/9 = **78,7** (ước lượng: giả định tài sản đưa vào dần đều, sinh lời đúng r). Trục: {0; 88,2; 166,9}, trọng số 0,25/0,5/0,25. | **+1.707** |
| 2 | Ký quỹ dài hạn 147 trừ theo mệnh giá tới 2053, chưa có căn cứ | TM17 tr.23: đây là "Nhận ký quỹ, ký cược dài hạn" của khách thuê, 134,97 → 146,99 trong 9T. Không công bố điều khoản hoàn trả. Mốc trần 2053 theo NQ 76/2020. | **(b) kịch bản**: mệnh giá (khách rời sớm, 0,25) / PV 27 năm theo lãi huy động 12T 7,40% = 21,4 (0,5) / PV theo r = 4,8 (0,25). Mệnh giá là cận bảo thủ, còn trong base. | **+1.956** |
| 3 | N0 neo theo biên đỉnh chu kỳ | BQ `ticker_financial`, `rev4/calc/szl_gpm_hist_20261123.csv`: GPM 9T/26 là 38,97%; trung bình 2017Q1–2024Q4 (32 quý) là 33,23%. DT 9T 449,4 ⇒ N0 theo biên chu kỳ = **104,7** (N0 9T = 132,2). | **(a)+(b)**: lịch sử của chính SZL là cơ sở độc lập cho chiều giảm; cơ cấu dịch sang nhà xưởng là cơ sở cho chiều giữ. Không phân định được nên đặt trọng số **0,5/0,5** cho hai mức. Giữ hệ số ±12% quanh mỗi mức. | **−1.562** |
| 4 | DT tài chính loại 100% nhưng CP tài chính chỉ loại ×0,8 | Lãi vay đã được trừ qua nợ ròng | Loại 100% cả hai phía (đối xứng) | +131 |
| 5 | Ý kiến kiểm toán FY2025 chưa nêu | BCTC kiểm toán 2025 **không có trong src**. Thay thế gần nhất: báo cáo soát xét H1/2026 số 16/2026/BCSX-RSMHCM ngày 10/08/2026 của RSM Việt Nam (`png/h1_p06-07`), kết luận **chấp nhận toàn phần**, không có đoạn nhấn mạnh. | **(c) ý kiến FY2025 không kiểm chứng được** trong phiên. Đặt `audited_fy_missing = true` trong đề xuất sổ. | 0 |
| 6 | Tiền thuê đất hằng năm có thể tăng; 44,3 đã vào chi phí 9T chưa? | TM16 tr.23: khoản trích 44,265 **cuối kỳ = đầu năm** ⇒ không ghi chi phí trong 9T ⇒ không bị ×4/3. TM15 Q3 tr.22 và TM5.15 H1 tr.25: tiền thuê đất phát sinh H1 = 9T = 13,74 ⇒ ghi nhận một lần mỗi năm. | 44,3 giữ trừ ở base (nghĩa vụ chưa quyết toán). Chưa có thông báo đơn giá mới ⇒ **(b) độ nhạy**: +25% ⇒ −396; +50% ⇒ −792. | 0 (base) |
| 7 | Capex Long Phước còn ~513 chỉ dựa trên báo chí | Không có NQ HĐQT/ĐHĐCĐ trong src | Dự án tăng trưởng nên NPV 0, phần còn phải chi không vào base. **(c) không kiểm chứng được** tổng mức 920. Độ nhạy vượt vốn 20% phần còn lại (−102,6 tỷ) ⇒ **−2.041**. | 0 |
| 8 | Capex môi trường của KCN | TSCĐ H1 tr.22 (`png/h1_p25`): Nhà máy xử lý nước thải GĐ4 KCN Long Thành, nguyên giá 116,34, còn lại 93,06, còn 192 tháng ⇒ khoản capex tuân thủ lớn gần nhất **đã đầu tư** và đang khấu hao trong N0. Chi phí trả trước "CP kinh doanh NMXLNT" 1,29. | Capex tuân thủ tương lai chưa công bố ⇒ **(c) không kiểm chứng được**. Nằm trong trục capex duy trì/KH (±45/năm ⇒ ±6.482), không thêm khoản riêng vào base (luật V4(b): không có nguồn thì chuyển sang độ nhạy). | 0 |
| 9 | Mốc 2053 chỉ có căn cứ cho một phần đất | TM17: NQ 76/2020 phân bổ 2019–2053 cho phần đất cho thuê 2004–08 | Giữ trục thời hạn 27 năm/vĩnh viễn (0,75/0,25). Độ nhạy: chỉ 27 năm −116; chỉ vĩnh viễn +347. Giấy phép đất **(c) chưa đối chiếu**. | 0 |
| 10 | Giao dịch bên liên quan chưa định lượng | Vay BLQ đã nằm trong vay, tức trong nợ ròng. Trả trước người bán là vốn lưu động. | Không đổi base. HARD ABANDON (b) giữ ngưỡng 100 tỷ. | 0 |
| 11 | Holdco/chiết khấu khối trên SZC/SZB = 0 | — | Giữ base 0% (không có comp ánh xạ được). Độ nhạy holdco 10% ⇒ −851; 25% ⇒ −2.128. | 0 |
| 12 | Nguồn bị TRIM, không tái lập được | git `fc5bd02d9` | Khôi phục vào `rev4/restored/`, md5 trong LOCK. Lệnh tái lập ở cuối file. | — |
| 13 | Pháp lý SNZ sau 05/11 chưa tra | Web search 23/11: **không thấy** tin SZL bị thanh tra/khởi tố tháng 11/2026. Vụ khởi tố Trưởng BKS thuộc SNZ (công ty mẹ). Có tin cũ: SZL bị điều chỉnh quyết định phạt/truy thu thuế lên gần 14 tỷ ([baophapluat](https://doanhnhan.baophapluat.vn/sonadezi-long-thanh-szl-bi-dieu-chinh-phat-thue-so-tien-phai-nop-tang-vot-len-gan-14-ty-dong-82677.html)), không rõ ngày. | Chỉ là **WARNING**, không vào base (luật vụ án). Khoản thuế ~14 tỷ ≈ 290 đ/cp (ước lượng) nếu chưa được ghi nhận; **(c) chưa kiểm chứng được** khoản này đã hạch toán hay chưa. | 0 |

## 2. Độ nhạy (mỗi dòng đổi một trục so với base rev4; số từ `model_rev4_out.txt`)

| Biến thể | Tâm 5 tỷ | Δ | Nhãn 40 tr |
|---|---|---|---|
| **Base rev4** | **27.397** | 0 | TRONG |
| N0 chỉ theo 9T (biên hiện tại) | 28.959 | +1.562 | TRONG |
| N0 chỉ theo biên chu kỳ | 25.835 | −1.562 | TRONG |
| BĐS ĐT mới = 0 (đã nằm hết trong N0) | 25.689 | −1.707 | TRONG |
| BĐS ĐT mới = đủ giá vốn | 29.009 | +1.612 | TRONG |
| Ký quỹ DH theo mệnh giá | 25.441 | −1.956 | TRONG |
| Ký quỹ DH theo PV@r | 28.268 | +871 | TRONG |
| Thuê đất +25% / +50% | 27.001 / 26.605 | −396 / −792 | TRONG |
| Long Phước vượt vốn 20% phần còn lại | 25.356 | −2.041 | TRONG |
| Holdco 10% / 25% | 26.546 / 25.268 | −851 / −2.128 | TRONG |
| KTPL 8% / 5% | 28.049 / 28.657 | +652 / +1.260 | TRONG |
| Capex duy trì 0,5× KH (+45/năm) | 33.879 | +6.482 | **DƯỚI** |
| Capex duy trì 1,5× KH (−45/năm) | 20.915 | −6.482 | **TRÊN** |

**Ngưỡng nhãn ở cỡ 40 tr:**
- Sang TRÊN nếu dòng tiền thêm < −30,4 tỷ/năm (≈ capex duy trì ≥ 1,34× KH 90/năm), holdco > 52,7%, hoặc KTPL > 30,9%.
- Sang DƯỚI nếu dòng tiền thêm > +20,0 tỷ/năm (≈ capex duy trì ≤ 0,78× KH).
- Trục rộng nhất vẫn là capex duy trì: BCTC không tách capex duy trì khỏi capex mở rộng.

## 3. V1 — chi phí vốn; V2/D4 — dải Ke

- **r = 13,50%**, bằng neo 13,5% + 1,0 × (7,40% − 7,40%). Lãi huy động 12T hiệu dụng (`deposit_rate_vn`, as-of 06/11) là 7,40%; neo 03/11 cũng 7,40%.
- Độ nhạy theo β = 1: −100bp ⇒ tâm +3,6%; +100bp ⇒ −3,1%.
- Dải Ke nội địa 12,3–13,4%, chỉ để báo kèm (tâm vẫn dùng r V1): tâm 5 tỷ 28.582 (12,3%) / 27.489 (13,4%); cỡ 40 tr 29.699 / 28.563.
- Giá 27.700 tương ứng r ≈ 13,17%.

## 4. V3 — thanh khoản

Chiết khấu CK = σ√(Q/ADV250), với ADV trung vị 250 phiên đến 06/11 (giữ nguyên r3c):
- Cỡ 5 tỷ: CK 4,12%. Q/ADV250 1.084%, nằm ngoài vùng hiệu chỉnh nên chỉ dùng tham chiếu.
- Cỡ sleeve 40 tr: CK 0,37%. Chia ít nhất hai phiên (8,7% ADV250).

Giá trị trước CK (5 tỷ): xem `center_pre` trong `model_rev4_out.json`. Nhãn đặt theo giá trị **sau** CK. Sizing V8 (2–4% NAV/mã) chỉ là tham chiếu; DD không đề xuất lệnh.

## 5. V5 — 5F

`ADDENDUM_5F.md` (11/2026) mới dưới 12 tháng nên tái dùng: **NARROW / LOCATION**. Rủi ro số 1 là quỹ đất KCN Long Thành gần cạn cộng với đồng hồ thời hạn 2053.

Kiểm nhanh 23/11: không đổi tier. Bằng chứng mới là GPM 5 quý ≥ 38% so với trung bình 8 năm 33,2%. Đây là biên cao chưa chứng minh được tính bền, vì vậy N0 đặt trọng số 50/50 (§1 mục 3).

## 6. V6

**Không áp dụng ở rev4.** Chuỗi DD SZL chưa dựng hai nền V_ngắn/V_dài. Rev4 chỉ xử lý các hạng mục skeptic r1, không mở trục mới.

## 7. Mốc đổi nhận định (hai chiều) và HARD ABANDON

| Mốc | Ngày | Lên (→ DƯỚI) | Xuống (→ TRÊN) |
|---|---|---|---|
| BCTC Q4/2026 | 31/01/2027 | GPM cả năm ≥ 38% và Q4 giữ ⇒ dồn trọng số N0 về 9T (+1.562) | GPM Q4 < 34% ⇒ dồn về biên chu kỳ (−1.562) |
| BCTC kiểm toán 2026 + LCTT | 31/03/2027 | Capex duy trì ≤ 0,78× KH có số | Capex duy trì ≥ 1,34× KH; ý kiến kiểm toán ngoại trừ |
| Điều khoản ký quỹ khách thuê | khi có | Hoàn trả cuối hợp đồng ⇒ PV có cơ sở | Hoàn trả theo yêu cầu/sớm ⇒ về mệnh giá (−1.956) |
| Long Phước | 30/06/2027 | Hợp đồng thuê có giá | Vượt vốn > 920 có số (−2.041 ở mức 20%) |
| Đơn giá thuê đất mới (Luật Đất đai 2024) | khi có | — | Tăng > 50% (−792) |
| Lãi huy động 12T (β = 1) | hằng tháng | −100bp ⇒ +3,6% | +100bp ⇒ −3,1% |
| Thanh tra SNZ / thuế | — | — | Kết luận nêu tên SZL ⇒ nâng WARNING |

**HARD ABANDON** (giữ r2):
- (a) thanh tra/khởi tố chạm pháp nhân SZL hoặc tài sản KCN;
- (b) SZL cho bên liên quan vay hoặc trả trước không bảo đảm > 100 tỷ;
- (c) Long Phước bị thu hồi hoặc đình chỉ.

## 8. Còn mở

- Ý kiến kiểm toán FY2025 (BCTC kiểm toán 2025 không có trong src).
- NQ tổng mức Long Phước.
- Điều khoản hoàn trả ký quỹ.
- Giấy phép đất 2053.
- Đơn giá thuê đất mới.
- Khoản truy thu thuế ~14 tỷ: đã hạch toán hay chưa.
- DC 78,7 của BĐS ĐT là ước lượng theo thời điểm, BCTC không cho doanh thu theo tài sản.
- **Post-fix sau lần chạy đầu** (ghi ở `rev4/calc/LOCK_rev4_postfix.txt`): tiền thuê đất năm 18,3 → 13,74 (sửa lỗi ×4/3 với khoản ghi nhận một lần mỗi năm). Sửa này chỉ ảnh hưởng độ nhạy, base không đổi. Đã bổ sung ghi chú nguồn (BĐS H1, NMXLNT) trong assumptions.

- `bin/dd_assumptions_lint.py`: `assumptions_rev4.json` CHƯA theo schema `dd_assumptions_v1` (B4, 22/11) — chỉ cảnh báo (không `--strict`), vì file kế thừa khung r3/r3c; chuyển schema là việc riêng, không đổi số.

Không đặt lệnh, không sửa `kb/dd_price_zones.json`, không gửi email.

## Tái lập

```bash
cd SZL/rev4/calc
/home/trido/thanhdt/wc_venv/bin/python -I model_rev4.py > run1.txt; /home/trido/thanhdt/wc_venv/bin/python -I model_rev4.py > run2.txt; cmp run1.txt run2.txt   # trùng byte; = model_rev4_out.txt
md5sum -c <(grep -v '^#' LOCK_rev4_postfix.txt)      # assumptions + model + out sau post-fix
md5sum -c <(grep -v '^#' LOCK_rev4_prerun.txt)       # FAILED có chủ đích: assumptions_rev4.json, model_rev4.py (post-fix, xem §8)
```
