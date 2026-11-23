# DD SZL (Sonadezi Long Thành, HOSE) — REV4b · 23/11/2026 · job `Taylor_20261123_003503` (resume `Taylor_20261123_050009`)

Bản này xử lý skeptic DD_GENERAL r2 (`skeptic/r2.json`, INCONCLUSIVE) chạy trên `REPORT_rev4.md`, đồng thời giữ toàn bộ phần đã xử lý skeptic r1. `REPORT_rev4.md` và `REPORT_r3c.md` giữ nguyên, không sửa.

**Nguồn**
- Toàn bộ nguồn được khôi phục từ git `fc5bd02d9` vào `rev4/restored/`:
  - `src/Q3_2026_hopnhat.pdf`, md5 `6ef6a005…`
  - `src/H1_2026_soatxet.pdf`, md5 `c36ddb57…`
- Ảnh trang dùng để đọc thuyết minh nằm ở `rev4/png/`.
- Mô hình ở `rev4/calc_b/model_rev4b.py`, giả định khoá ở `rev4/calc_b/assumptions_rev4b.json`.
- `rev4/calc_b/LOCK_rev4b_prerun.txt` được ghi **trước** lần chạy đầu. Hai lần chạy cho output trùng byte, `model_rev4b_out.txt` md5 `0b8bf1a6`.

**Mù giá**
- Giá 27.700 (06/11) đã biết từ r3/r3c. Rev4/rev4b **không truy vấn giá mới**.
- File giá cũ chỉ dùng cho chiết khấu thanh khoản (CK) và để gán nhãn. Không giả định nào được chọn theo giá.

## 0. Kết luận

| | r3c | rev4 (skeptic r2 INCONCLUSIVE) | **rev4b base** |
|---|---|---|---|
| Tâm, cỡ 5 tỷ (CK 4,12%) | 25.165 | 27.397 | **25.852** |
| P10 / P50 / P90, 5 tỷ | 22.936 / 25.008 / 27.710 | 23.812 / 27.335 / 31.145 | **22.290 / 25.840 / 29.534** |
| Tâm, cỡ 40 tr (CK 0,37%) | 26.148 | 28.468 | **26.862** |
| P10 / P50 / P90, 40 tr | 23.833 / 25.985 / 28.793 | 24.742 / 28.404 / 32.362 | **23.162 / 26.850 / 30.688** |
| % trọng số kết cục dưới giá 27.700 (5 tỷ / 40 tr) | 89,4% / 76,2% | 54,9% / 40,0% | 74,9% / 60,8% |
| Nhãn (5 tỷ tham chiếu / 40 tr hành động) | TRONG / TRONG | TRONG / TRONG | **TRONG / TRONG**. Giá cao hơn tâm 7,1% ở cỡ 5 tỷ, 3,1% ở cỡ 40 tr |

- **Cầu nối r3c → rev4b** (`model_rev4b_out.txt`), tổng **+687** (+2,7%):

  | Bước | Δ tâm 5 tỷ |
  |---|---|
  | r3c (control) | 25.165 |
  | + trục BĐS đầu tư mới | +1.707 |
  | + trục ký quỹ dài hạn 0,5 mệnh giá / 0,5 PV | +1.249 |
  | − lợi nhuận phi tiền mặt NQ 76 | −708 |
  | + trục N0 chuẩn hoá biên | −1.562 |
  | **rev4b** | **25.852** |

- **Control.** Đặt các trục mới về đúng lựa chọn của r3c thì tái lập đúng 25.165 / 22.936 / 25.008 / 27.710 (cỡ 40 tr: 26.148).
- **Luật sổ (giá < tâm − 15%) KHÔNG đạt.** Không đủ điều kiện sleeve fear-buy §2.5 (giữ nguyên như r2).
- Trước CK, tâm cỡ 5 tỷ là 26.961.

## 1. Đính chính so với rev4 (skeptic r2)

| # | Hạng mục skeptic r2 | Xử lý ở rev4b | Δ |
|---|---|---|---|
| r2-1 | **Killer.** Trục ký quỹ dồn 0,75 trọng số về phía PV dù không có điều khoản hoàn trả nào; phần tăng trong năm gắn với nhà xưởng, vốn là hợp đồng ngắn hơn | Trọng số **trung lập 0,5 mệnh giá / 0,5 PV theo lãi huy động** (bỏ nhánh PV@r). Bước ký quỹ giảm từ +1.956 xuống **+1.249**. Hai cực: chỉ mệnh giá 24.602; chỉ PV 27.101 | −707 so với rev4 |
| r2-2 | Mục #4 của rev4 (loại 100% CP tài chính) sai chiều. Doanh thu tài chính là cổ tức miễn thuế; lãi vay có lá chắn thuế 20% (thuế HH Q3 8,46 ≈ (78,47 − 36,76) × 20%) | **Trở lại ×0,8 như r3c.** N0_9M_RAW = 131,08, bằng r3c | −131 |
| r2-3 | Thiếu khoản 151,99 tỷ theo NQ 76/2020: lãi phi tiền mặt 5,846 tỷ/năm | TM17 Q3 tr.23: phải trả dài hạn khác giảm 157,834 → 151,988, tức −5,846 trong 9T, đúng một năm phân bổ. Đây là lợi nhuận phi tiền mặt (tiền đã thu từ 2004–08) ⇒ **trừ khỏi N0**: 5,846 × 4/3 × 0,8 = 6,24 ⇒ N0_9M = **124,84**. Giả định khoản này chịu thuế 20% (**không kiểm chứng được**). Độ nhạy nếu không chịu thuế: −177 | **−708** |
| r2-4 | Tiền thuê đất 13,74 ghi một lần/năm mà N0 vẫn ×4/3 (+~240) | Bảng thuế TM15 chỉ chứng minh **nghĩa vụ** phát sinh 13,74 trong H1 (= 9T), **không** chứng minh chi phí P&L được ghi một lần; doanh nghiệp có thể phân bổ theo tháng ⇒ **không sửa base** (điều chỉnh tăng chưa có cơ sở). Độ nhạy bỏ ×4/3: **+416** | 0 |
| r2-5 | Đơn giá thuê đất mới chỉ thử tới +50% | Thêm độ nhạy ×2: **−1.583**, nhãn 40 tr vẫn TRONG | 0 |
| r2-6 | Không ghi ngày phát hành cổ tức cổ phiếu làm cơ sở 48,199 tr cp | BQ `ticker_financial` OShares: 27,90 tr (2026Q2) → 48,20 tr (2026Q3) ⇒ phát hành trong Q3/2026. Số 48,199 tr khớp BCTC Q3 (skeptic r1). **Ngày chốt chính xác: không kiểm chứng được** trong phiên. Không ảnh hưởng tâm vì dùng số cổ phiếu cuối kỳ | 0 |
| r2-7 | Ý kiến kiểm toán FY2025 vắng | Vẫn **không kiểm chứng được**, vì BCTC kiểm toán 2025 không có trong src. Gần nhất có báo cáo soát xét H1/2026 RSM số 16/2026/BCSX-RSMHCM, ngày 10/08/2026: **chấp nhận toàn phần**. Đề xuất sổ đặt `audited_fy_missing = true` | — |

### Giữ từ rev4 (xử lý skeptic r1)

- **BĐS đầu tư mới 166,887**
  - Nguồn: TM10 Q3 tr.20. H1 tăng 101,677 (TM5.10 H1 tr.23), Q3 tăng 65,210. Một phần chuyển từ XDCB nhà xưởng Châu Đức (60,55 → 6,09).
  - Tài sản đã vận hành và đang khấu hao; 327,4 tỷ đang thế chấp.
  - Áp V4(a) NPV 0. Phần lợi nhuận đã nằm trong N0 ước lượng DC = 78,7 (giả định đưa vào dần đều, sinh lời đúng r).
  - Trục giá trị {0; 88,2; 166,9}, trọng số 0,25 / 0,5 / 0,25.
- **N0 chuẩn hoá biên**
  - GPM 9T là 38,97% (BQ); trung bình 2017–24 là 33,23% (32 quý). File: `szl_gpm_hist_20261123.csv`.
  - Skeptic r2 ghi BCTC cho 38,03%. Độ lệch giữa BQ và BCTC tương tự trong quá khứ nên khoảng chênh gần như không đổi.
  - N0 tính theo biên chu kỳ = 97,32. Hai mức N0 trọng số 0,5 / 0,5, hệ số ±12% quanh mỗi mức.
- **Khoản trích 44,265** (TM16): cuối kỳ = đầu năm, nên không vào chi phí 9T. Vẫn trừ ở base.
- **Capex môi trường**
  - Nhà máy xử lý nước thải GĐ4 KCN Long Thành, nguyên giá 116,34, còn lại 93,06 (TSCĐ H1 tr.22): đã đầu tư.
  - Capex tuân thủ tương lai chưa công bố ⇒ nằm trong trục capex duy trì.
- **Long Phước**
  - Tổng mức 920 chỉ có từ báo chí, **không kiểm chứng được**. NPV 0.
  - Độ nhạy vượt vốn 20% phần còn lại: −2.041.
- **Pháp lý**
  - Web search 23/11 không thấy SZL bị thanh tra/khởi tố trong tháng 11/2026. Vụ khởi tố Trưởng BKS thuộc SNZ.
  - Tin cũ: quyết định phạt/truy thu thuế của SZL được điều chỉnh lên gần 14 tỷ ([baophapluat](https://doanhnhan.baophapluat.vn/sonadezi-long-thanh-szl-bi-dieu-chinh-phat-thue-so-tien-phai-nop-tang-vot-len-gan-14-ty-dong-82677.html)), không rõ ngày; ≈ 290 đ/cp (ước lượng). Chưa kiểm chứng được đã hạch toán hay chưa.
  - Chỉ là **WARNING**, không vào base.
- **Holdco SZC/SZB**: base 0%.
- **Mốc 2053**: trục thời hạn 27 năm / vĩnh viễn (0,75 / 0,25).

## 2. Độ nhạy (mỗi dòng đổi một trục so với base rev4b)

| Biến thể | Tâm 5 tỷ | Δ | Nhãn 5 tỷ / 40 tr |
|---|---|---|---|
| **Base rev4b** | **25.852** | 0 | TRONG / TRONG |
| N0 chỉ theo 9T | 27.414 | +1.562 | TRONG / TRONG |
| N0 chỉ theo biên chu kỳ | 24.290 | −1.562 | TRÊN / TRONG |
| BĐS ĐT mới = 0 | 24.144 | −1.707 | TRÊN / TRONG |
| BĐS ĐT mới = đủ giá vốn | 27.464 | +1.612 | TRONG / TRONG |
| Ký quỹ dài hạn theo mệnh giá | 24.602 | −1.249 | TRONG / TRONG |
| Ký quỹ dài hạn theo PV@lãi huy động | 27.101 | +1.249 | TRONG / TRONG |
| Ký quỹ theo trọng số rev4 (0,25 / 0,5 / 0,25, có PV@r) | 26.558 | +707 | TRONG / TRONG |
| Thuê đất +25% / +50% / ×2 | 25.456 / 25.060 / 24.269 | −396 / −792 / −1.583 | TRONG / TRONG |
| Thuê đất bỏ ×4/3 | 26.267 | +416 | TRONG / TRONG |
| NQ 76 không chịu thuế | 25.675 | −177 | TRONG / TRONG |
| Long Phước vượt vốn 20% | 23.811 | −2.041 | TRÊN / TRONG |
| Holdco 10% / 25% | 25.000 / 23.723 | −851 / −2.128 | TRONG, TRÊN / TRONG |
| KTPL 8% / 5% | 26.469 / 27.045 | +618 / +1.194 | TRONG / TRONG |
| Capex duy trì 0,5× KH (+45/năm) | 32.334 | +6.482 | DƯỚI / **DƯỚI** |
| Capex duy trì 1,5× KH (−45/năm) | 19.369 | −6.482 | TRÊN / **TRÊN** |
| Chỉ 27 năm / chỉ vĩnh viễn | 25.743 / 26.177 | −108 / +325 | TRONG / TRONG |

**Ngưỡng nhãn ở cỡ 40 tr (hành động):**
- **Sang TRÊN** khi có một trong các điều kiện:
  - dòng tiền thêm < −19,4 tỷ/năm (≈ capex duy trì ≥ 1,22× KH 90/năm);
  - holdco > 33,8%;
  - KTPL > 24,6%.
- **Sang DƯỚI** khi dòng tiền thêm > +30,7 tỷ/năm (≈ capex duy trì ≤ 0,66× KH).
- Trục rộng nhất vẫn là capex duy trì, vì BCTC không tách capex duy trì với capex mở rộng.

## 3. V1 / V2-D4 — chi phí vốn

- **r = 13,50%** = 13,5% + 1,0 × (7,40% − 7,40%), với lãi huy động 12T hiệu dụng (`deposit_rate_vn`) tại 06/11 và tại neo 03/11 đều là 7,40%.
- Độ nhạy lãi huy động (β = 1): −100bp ⇒ tâm **+3,6%**; +100bp ⇒ **−3,1%**.
- Dải Ke nội địa 12,3–13,4% (báo kèm; tâm vẫn dùng r theo V1):

  | | Ke 12,3% | Ke 13,4% |
  |---|---|---|
  | Tâm cỡ 5 tỷ | 26.970 | 25.938 |
  | Tâm cỡ 40 tr | 28.024 | 26.952 |

- Để tâm cỡ 5 tỷ bằng giá 27.700 cần r ≈ **11,61%**.

## 4. V3 — thanh khoản

- CK = σ√(Q/ADV250), ADV trung vị 250 phiên đến 06/11 (như r3c).
- Cỡ 5 tỷ: CK **4,12%**. Q/ADV250 = 1.084%, nằm ngoài vùng hiệu chỉnh nên chỉ dùng tham chiếu.
- Cỡ 40 tr: CK **0,37%**, chia ≥ 2 phiên (8,7% ADV250).
- Tâm cỡ 5 tỷ trước CK là 26.961; nhãn tính theo giá trị sau CK.
- V8 (2–4% NAV/mã) chỉ để tham chiếu; DD này không đề xuất lệnh.

## 5. V5 — 5F

- Tái dùng `ADDENDUM_5F.md` (lập 11/2026, chưa quá 12 tháng): **NARROW / LOCATION**.
- Rủi ro số 1: quỹ đất KCN Long Thành gần cạn, cộng đồng hồ 2053.
- Kiểm nhanh 23/11: không đổi tier. Biên cao 5 quý chưa chứng minh được tính bền ⇒ N0 đặt 50/50.

## 6. V6

**Không áp dụng.** Chuỗi DD SZL chưa dựng hai nền V_ngắn / V_dài; rev4b chỉ xử lý các hạng mục skeptic nêu.

## 7. Mốc đổi nhận định (hai chiều) và HARD ABANDON

| Mốc | Ngày | Lên (→ DƯỚI) | Xuống (→ TRÊN) |
|---|---|---|---|
| BCTC Q4/2026 | 31/01/2027 | GPM cả năm ≥ 38% ⇒ dồn N0 về mức 9T (+1.562) | GPM Q4 < 34% ⇒ dồn về biên chu kỳ (−1.562) |
| BCTC kiểm toán 2026 + LCTT | 31/03/2027 | Capex duy trì ≤ 0,66× KH, có số | Capex duy trì ≥ 1,22× KH; ý kiến kiểm toán ngoại trừ |
| Điều khoản ký quỹ khách thuê | khi có | Hoàn trả cuối hợp đồng/2053 ⇒ PV (+1.249) | Hoàn trả theo yêu cầu ⇒ mệnh giá (−1.249) |
| Long Phước | 30/06/2027 | Hợp đồng thuê có giá | Vượt vốn so với 920, có số |
| Đơn giá thuê đất mới | khi có | — | ×2 (−1.583) |
| Lãi huy động 12T | hằng tháng | −100bp ⇒ +3,6% | +100bp ⇒ −3,1% |
| Thanh tra SNZ / thuế | — | — | Kết luận nêu tên SZL ⇒ nâng mức WARNING |

**HARD ABANDON** (giữ như r2):
- (a) thanh tra/khởi tố chạm tới pháp nhân SZL hoặc tài sản KCN;
- (b) cho bên liên quan vay hoặc trả trước không bảo đảm > 100 tỷ;
- (c) Long Phước bị thu hồi hoặc đình chỉ.

## 8. Còn mở (không kiểm chứng được trong phiên)

- Ý kiến kiểm toán FY2025.
- Điều khoản hoàn trả ký quỹ.
- NQ về tổng mức đầu tư Long Phước.
- Giấy phép đất 2053.
- Đơn giá thuê đất mới.
- Khoản truy thu thuế ~14 tỷ.
- Cách ghi P&L của tiền thuê đất (một lần hay phân bổ) và thuế của NQ 76.
- Ngày phát hành cổ phiếu Q3.
- DC 78,7 là ước lượng.
- `bin/dd_assumptions_lint.py`: file giả định chưa theo schema `dd_assumptions_v1` (chỉ cảnh báo, không strict), vì kế thừa khung r3/r3c.

Không đặt lệnh, không sửa `kb/dd_price_zones.json`, không gửi email.

## Tái lập

```bash
cd SZL/rev4/calc_b
/home/trido/thanhdt/wc_venv/bin/python -I model_rev4b.py > run1.txt; /home/trido/thanhdt/wc_venv/bin/python -I model_rev4b.py > run2.txt; cmp run1.txt run2.txt   # = model_rev4b_out.txt (md5 0b8bf1a6)
md5sum -c <(grep -v '^#' LOCK_rev4b_prerun.txt)
```
