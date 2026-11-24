# SIP — rà lại DD đợt 1, nhóm A (24/11/2026, job Taylor_20261124_095514)

Nguồn: `REPORT_recheck_SIP.md` (md5 `d901852e…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `354ddca1…`; CONTROL: stdout trùng byte và JSON trùng nội dung với output r3) · skeptic `skeptic/r1.json` · `LEDGER_PROPOSAL_SIP.json` (rev4, selfcheck bản tạm: lỗi 0).

⚠ **Hạ tầng:** `assumptions_r3.json`, dữ liệu giá và output r2/r3 bị **xoá khỏi git** (TRIM 19/11). Recheck khôi phục chúng từ lịch sử vào `calc/mirror/`, md5 khớp LOCK. `assumptions_file` trong sổ đang trỏ tới file không còn.

## Bước 0
Không bị phủ:
- r: Δ = 0.
- RONIC = Ke (đã sửa ở r3).
- Không có tầng CK holding. NCI là trục; "chiết khấu quản trị 10%" chỉ là độ nhạy.

⇒ Chạy skeptic.

## (a) Lệch theo luật mới
- **D4:**
  - Thiếu dải Ke ⇒ bổ sung 57.744 / 54.720.
  - REPORT r3 chỉ ghi ±100bp ⇒ bổ sung ±50bp.
  - RONIC = Ke, không lệch.
- **D3:** hạ tầng môi trường KCN cho 937 ha + tiền thuê đất Nhà nước (G16) = **cần kiểm chứng**. Skeptic ước G16 ≈ −5,6% nếu khoảng 100 tỷ/năm; chưa có số.
- **E15:** **57.744 đ/cp (+6,02%)**. Chỉ là độ nhạy, nhãn vẫn TRONG.
- **E16:** nguyên văn **KHÔNG CHẮC (N hiệu dụng thấp, 1.88)**.
- **V6:** V_ngắn 40.547, V_dài 36.437, D 0,107, không cờ. Caveat: NP BQ chưa tách NCI.
- **V3 / V5:** đã đủ.
- **V8:** nếu xét mua thì 2% NAV (cờ tín dụng 6.016 tỷ).

## (b) Tâm / vùng / nhãn
| | r3 (sổ) | recheck | Δ |
|---|---|---|---|
| Tâm (sau CK 5 tỷ) | 54.466 | 54.466 | 0% |
| Vùng | 43.257–69.818 | không đổi | 0 |
| Nhãn @ 50.100 (06/11) | TRONG | TRONG | không đổi |

## (c) Phản biện
`skeptic/r1.json`: **INCONCLUSIVE (medium)**, 0,89 USD, md5 khớp. Cơ học đúng. Lệch hai chiều chưa giải:
- **Chiều quá CAO:**
  - G16 tiền thuê đất vắng mọi khối;
  - 12 tỷ/ha ròng không nguồn (khoảng 36% tâm);
  - ha cho thuê 9T26 đếm đôi để ngoài tâm (−900…−1.000);
  - tín dụng 6.016 tỷ, bên vay chưa định danh.
- **Chiều quá THẤP:**
  - VAT khấu trừ +3.123 để ngoài, trong khi tạm ứng +826 vào base: luật "base = sổ sách" áp một chiều;
  - NCI BCĐ 9,9% vs 20% (+3,2%).
- Net phần định lượng ≈ +4,8% quá thấp, đối lại G16 chưa định lượng.
- ⇒ **Sổ hạ CONFIRMED (backfill) → REFUTED_OPEN (rev4)**.

## (d) Việc mở
1. **G16:** đọc thuyết minh thuê đất (trả hàng năm hay một lần) và trừ PV vào base nếu trả hàng năm.
2. **VAT/DTL:** đưa vào base cho nhất quán với tạm ứng, hoặc bỏ cả hai.
3. **G12:** trừ ha cho thuê 9T26 vào base.
4. Tìm nguồn cho 12 tỷ/ha (biên cho thuê lại gần đây), hoặc mở rộng trục.
5. Định danh G1/G2 bên vay.
6. Ghi cơ sở số cổ phiếu.
7. Khôi phục file bị trim (hạ tầng).

## (e) Khuyến nghị lớp: **FULL (rev5)**
- Phần luật mới đổi tâm 0%, nhưng skeptic chỉ ra 3 mục định lượng được (VAT +5,7%, NCI +3,2%, G12 khoảng −1,8%) và 1 mục chưa định lượng (G16 khoảng −5,6%). Gộp lại có thể dịch tâm >5% ⇒ cần rev5 + phản biện đầy đủ.
- Không chạy thêm vòng trước khi có dữ liệu mới.
