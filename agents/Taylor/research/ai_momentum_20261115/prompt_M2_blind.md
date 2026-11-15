# Prompt M2 — MÙ (deepseek qua bin/second_opinion.sh). KHÔNG thấy kết luận M1.
Giả thuyết mặc định cần phản bác: "Đợt tăng của mỗi mã dưới đây chỉ là dòng tiền/đầu cơ, không có lý
do cơ bản (NARRATIVE_ONLY)". Với TỪNG sự kiện trong gói, dựa CHỈ trên gói (dữ liệu ngày ≤ T; cấm web,
cấm dùng hiểu biết về giá sau T): cho `blind_driver` (cùng 6 nhãn của M1, UNKNOWN hợp lệ),
`blind_view_20s/60s` (CONT/REV/NO_VIEW), `evidence` (trỏ phần tử gói + ngày ≤ T).
Ghi kết quả dạng JSON list theo `schema_M2.json#blind`.
