# PAT r5 — áp dụng 7 mục (TRUNG THỰC). Tham chiếu dòng của `r5/assumptions_objective_r5.md` (A) và `r5/VALUATION_r5.md` (V)
Tâm: **trước CK 66.470 · sau CK 59.823 · cổng 50.850** (r4: 66.318 / 59.686 / 50.733).

| # | Yêu cầu | Mức | Nơi sửa | Ghi chú trung thực |
|---|---|---|---|---|
| 1 | q_B: bỏ luật chứng minh một chiều; trộn {0;.25;.40} | **ĐỦ** | A:3, A:32, A:56 (thay r4:29,51,53) | Dựng được trộn nên không dùng khoảng. Trọng số đều = phán đoán, báo tâm từng cây (69.581/66.057/63.772). Trộn ra 66.470, **không phải ~64.000** vì mục 3 (xem dưới). |
| 2 | Đảo giải phóng tồn kho về r2 | **ĐỦ** | A:40, A:48, A:70 (thay r4:37,45; V r4:13) | Không có bằng chứng mới độc lập ⇒ không giữ. Biến thể giữ chỉ ở độ nhạy; WARNING đã thêm (V mục WARNING). Số 39,4 và "UHY ngoại trừ" lấy từ dispatch, tôi chưa tự đo/xác minh; hệ số haircut 50% là quy ước độ nhạy. |
| 3 | MỘT cách đọc H1/26 | **ĐỦ, nhưng là lựa chọn có hệ quả** | A:32 (b), A:36, A:39, A:57 (thay r4:29(b),33,36,54) | Chọn "sạch" cho cả hai phía (tồn kho 30/06 ≈ bình thường; mua DLC H1 ≈ 2025). Đẩy tâm +4.800 (q=0) / +3.892 (trên trộn). Cách đọc "nhiễu" còn lại báo ở độ nhạy (62.578). Dispatch chưa chỉ định chiều nào — cần skeptic r5 bác/xác nhận. |
| 4 | Thay "tâm vững, dịch <1%" bằng phân tách | **ĐỦ** | V §1.4 | Số −4.826/+6.409 lấy từ skeptic r4/dispatch (chưa tự đo); số r4→r5 do tôi đo: −1.538/+4.800/−3.111 = +152. Độ tin cậy ghi "thấp". |
| 5 | Chồng bi quan cùng cơ sở | **ĐỦ** | V §1.5 | Trên r4 ra đúng 60.354 (khớp dispatch). Trên r5: 63.913. Báo thêm bản có T. |
| 6 | Tâm trước/sau CK 10%; cổng trên giá trị sau CK | **ĐỦ** | V đầu bài, §1.6; A §8 | Số GTGD (1,01/0,60 tỷ, 64 phiên) lấy từ dispatch, chưa tự truy vấn BQ vòng này. |
| 7 | Ghi chú sổ giá | **ĐỦ** | `ledger_notes_r5.md` | Không ghi `dd_price_zones.json`. |

Không đổi: r 13,5%, g 2%, nút T/P(A)/D(ô A bật B tắt)/cốc/điện/cước/P, tiền ròng. Không email.
Chạy: `cd calc_r5 && python3 model_r5.py && python3 bridge_sens_r5.py && python3 selfcheck_r5.py`.
