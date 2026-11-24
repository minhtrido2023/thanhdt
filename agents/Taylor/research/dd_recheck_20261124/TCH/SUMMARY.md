# TCH — rà lại DD đợt 1, nhóm A (24/11/2026, job Taylor_20261124_095514)

Nguồn: `REPORT_recheck_TCH.md` (md5 `80f8cd5e…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `d2d3bb14…`; CONTROL tái lập r3b 15.864 / 14.563 / 17.325 bằng assert) · skeptic `skeptic/r1.json` · `LEDGER_PROPOSAL_TCH.json` (selfcheck bản tạm: lỗi 0).

⚠ **Hạ tầng:** đầu vào r3b (`assumptions_r3b.json`, `calc_r3/*`, `_shared/wpct.py`, `SUMMARY.json`) bị **xoá khỏi git** ở `14ad1c925` (TRIM_DD 19/11). Recheck khôi phục chúng từ `fc5bd02d9` vào `calc/mirror/`, md5 khớp LOCK. Nhưng `assumptions_file` trong sổ đang trỏ tới thư mục không còn đủ file. Mike cân nhắc khôi phục tại chỗ.

## Bước 0
- **r:** không bị phủ.
- **CK holding:** có tầng holding (CRV 68,02%). Base 0% trùng đầu "lạc quan" của dải user chốt 0…+20%, nên base **không bị phủ** ⇒ chạy skeptic.
- Song song cũ 27% (tham chiếu HHS N=6, chạy trên r3) đã lạc hậu ⇒ thay bằng +20% trên r3b: **14.294 (−9,9%), nhãn TRONG**.

## (a) Lệch theo luật mới
- **D4:**
  - Thiếu dải Ke ⇒ bổ sung 16.270 / 15.897.
  - Thiếu bảng ±50/±100bp ⇒ bổ sung: −324 … +337 đ/cp.
  - RONIC: không áp (NAV hữu hạn).
- **D3:** NƠXH 20% / tiền SDĐ bổ sung = **cần kiểm chứng**. Skeptic xác nhận có phơi nhiễm (TM19 đặt cọc NOXH An Hải), chưa có số.
- **E15:** **16.270 đ/cp (+2,56%)**.
- **E16:** nguyên văn **KHÔNG CHẮC (trung tính…đắt)**.
- **V6:** V_ngắn 5.878. FCFE TTM −2.858,6 tỷ ⇒ chỉ V_ngắn (asset-play).
- **V3 / V5:** đã đủ.
- **V8:** không áp (FLOOR_FAIL).

## (b) Tâm / vùng / nhãn
| | r3b (sổ) | recheck | Δ |
|---|---|---|---|
| Tâm (sau CK 5 tỷ) | 15.864 | 15.864 | 0% |
| Vùng | 14.563–17.325 | không đổi | 0 |
| Nhãn @ 13.500 (06/11) | DƯỚI (không chắc) | DƯỚI (không chắc) | không đổi |

Ba lựa chọn riêng lẻ có cơ sở đều đưa nhãn về TRONG: CK +20%, biên kiểm toán 42,7%, y = 4.

## (c) Phản biện
`skeptic/r1.json`: **INCONCLUSIVE (medium)**, 0,85 USD, md5 khớp.
- Cơ học đúng: skeptic tái lập mọi số r/CK.
- Killer (giữ từ r2): biên 51,9% chưa soát xét vs 42,7% kiểm toán ⇒ 13.642 (−14%).
- Mục thiếu mới:
  - NƠXH/SDĐ bổ sung;
  - quỹ KTPL, khoảng −1,8%;
  - HTM 678,3 tỷ chưa xác minh, tới −4,2%.

## (d) Việc mở
1. Báo cáo soát xét 6T FY26 (AASC) cho biên theo dự án.
2. Định lượng NƠXH/SDĐ bổ sung theo dự án (BCTN25, quyết định dự án).
3. User xác nhận dải CK 0…+20% (chốt cho HHS) có áp cho TCH không, và base nằm ở đâu.
4. Xác minh đối tác HTM "Sài Gòn Tài Lộc" từ PDF gốc.
5. Khôi phục file r3b đã bị trim (hạ tầng).

## (e) Khuyến nghị lớp: **FULL (rev5 sau khi có soát xét 6T FY26 + user chốt CK)**
- Phần luật mới là MECH: tâm 0%, nhãn không đổi.
- Base INCONCLUSIVE hai vòng (r2, r1-recheck), và nhãn phụ thuộc hai tham số chưa đóng (biên gộp, CK holding).
- Không chạy thêm vòng skeptic trước khi có dữ liệu mới.
