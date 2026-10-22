# Livermore blind screen — kết quả (22/10/2026, PREREG md5 4d04b7ea5e26de662365795996d24476)

16 case (8 điểm chuyển DT5G |Δstate|>=2 + 8 ngày đối chứng), ẩn danh hoá, 1 lượt chạy duy nhất, chưa chọn lại gì.

| Nhóm | n | Hit | Brier | B1 động lượng | B2 DT5G-implied |
|---|---|---|---|---|---|
| TẤT CẢ | 16 | 10 | 0,231 | 8 | — |
| Transition | 8 | 5 | 0,226 | 4 | 5 |
| Đối chứng | 8 | 5 | 0,236 | 4 | — |
| Không nhận ra giai đoạn | 8 | 6 | 0,214 | 5 | 4 |
| Nhận ra giai đoạn (nhiễm) | 8 | 4 | 0,248 | 3 | 1 |

Theo tiêu chí PREREG (Brier<0,25 và hit>=max baseline): **SỐNG THÊM** — chỉ nghĩa là không bị loại sớm.

## Giới hạn PHẢI đọc cùng kết quả
- 10/16 so với đồng xu: P(X>=10)=0,227 — không khác ngẫu nhiên.
- 11/16 case (69%) thực tế tăng ⇒ baseline "luôn UP" (không có trong PREREG) được 11/16 > 10/16 của Livermore. Livermore nghiêng UP 10/16, p_up chỉ 0,42-0,60.
- Case transition: Livermore 5/8 = B2 5/8 = "luôn UP" 5/8. Không thêm thông tin so với DT5G ở mẫu này.
- 8/16 case agent tự nhận ra giai đoạn lịch sử dù đã ẩn danh (C03,05,07,09,11,12,15,16) ⇒ dữ liệu quá khứ bị nhiễm; nhóm không nhận ra mới sạch (6/8, n quá nhỏ).
- Chạy bằng subagent general-purpose đọc file định nghĩa (loại `livermore` chỉ nạp sau khi khởi động lại phiên); việc cấm công cụ khác chỉ bằng chỉ dẫn, không cưỡng chế được.
- n=16: chỉ loại được vô dụng rõ rệt, không chứng minh edge.

## Kết luận
Không loại, không xác nhận. Giá trị thật chỉ có thể đo bằng đọc SỐNG ghi sổ trước, chấm sau +20 phiên (cổng: >=12 lần chấm, phải hơn cả đồng xu lẫn "luôn UP" lẫn DT5G, nếu không thì giải thể vai).
Artifact: PREREG.md, build_cases.py, cases/, SEALED_truth.json, livermore_results.csv, score.py, scored.csv.
