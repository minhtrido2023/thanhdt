# ĐỀ XUẤT (.proposed — KHÔNG áp): dòng "so với gửi tiết kiệm" trong bảng hiệu suất
Chờ user duyệt (chạm báo cáo NĐT, §21/§31). Không file production nào bị sửa.

## Diff mô tả
1. **Module mới** `mike/bin/savings_hurdle.py` (hoặc root `savings_hurdle.py`): nâng `hurdle_pit.py` của GĐ0 thành module có selfcheck.
   `accrual_pct(d0, d1)` = Σ ngày lịch trong [d0,d1) của `deposit_rate_vn.effective_deposit_events_df()` / 365 (lãi đơn, bậc thang).
2. **`nav_period_returns.py::_assemble`**: thêm khối `savings` vào mỗi kỳ (`inception/wtd/mtd/day`), cạnh `benchmark`:
   `{"hurdle_pct": accrual_pct(p.from_date, p.to_date), "rate_basis": "max(Big4 12T online, CCTG 12T cao nhất Big4), PIT, lãi đơn act/365", "excess_vs_savings_pp": return_pct - hurdle_pct}`.
   Mốc ngày = đúng `from_date/to_date` của kỳ sổ đơn vị (cùng cách khối benchmark dùng `anchor_source`), KHÔNG tự chọn.
3. **`fund-unit-performance-policy-20261010.md`**: thêm mục "Mốc so sánh thứ 3: gửi tiết kiệm" + quy ước: PIT-bậc thang là số CÔNG BỐ; "phẳng 7,4%×ngày/365" chỉ dùng nội bộ.
4. **`report_delivery_gate.py::_check_benchmark_table`**: nếu kỳ có khối `savings` thì dòng tiết kiệm trong bảng phải khớp số script ±0,005pp (cùng cơ chế gate VN-Index hiện có).
5. Selfcheck: 01/07→11/11/2026 = 2,548% (PIT) — KHÔNG phải 2,70% (số 2,70% = 7,4% phẳng × 133/365; đã đo ở `hurdle_pit.py`).

## Rủi ro / điều kiện
- **§31**: bảng vẫn phải lấy `return_pct` từ `nav_period_returns.py`; dòng tiết kiệm lấy cùng JSON — tuyệt đối không tính tay trong báo cáo.
- **§21**: không đụng tỉ suất per-position; chỉ thêm cột cấp danh mục. Cổ tức đã nằm trong TWR; tiết kiệm KHÔNG trừ thuế (lãi tiền gửi cá nhân miễn TNCN) ⇒ so sánh sòng phẳng hơn VN-Index giá.
- **Chất lượng chuỗi**: Big-4 12T là 26 mốc tay đóng băng + CSV nối, KHÔNG phải chuỗi công bố theo ngày; trước 2019 không có nguồn thật. Kỳ báo cáo gần (2026) dựa trên mốc xác nhận web (6,8% → CCTG 7,5/7,4%).
- **Không mua được đúng lãi đó**: 7,4% là CCTG 12 tháng; kỳ 4 tháng rút sớm chỉ hưởng lãi không kỳ hạn thấp ⇒ hurdle là CHUẨN THAM CHIẾU thượng cận, không phải phương án thay thế khả thi tuyệt đối. Báo cáo phải ghi chú.
- **Khung pháp lý/truyền thông**: nhà đầu tư ngoài (SpaceX) thấy "thua tiết kiệm" — cần Wendy (legal-vn) rà cách diễn đạt trước khi vào mẫu; không nhắc ZaloPay trong báo cáo SpaceX.
- **Hành vi cảnh báo**: giữ CCTG cũ >45 ngày (cctg_held) làm hurdle không tự hạ — đúng hướng thận trọng nhưng có thể phóng đại hurdle khi lãi suất giảm; cần nhãn nguồn trong báo cáo.
- Tác dụng phụ lên `number-provenance-gate`: khối KB mới công bố số hurdle phải khai nguồn.
