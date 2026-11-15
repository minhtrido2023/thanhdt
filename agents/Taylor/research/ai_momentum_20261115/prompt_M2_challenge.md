# Prompt M2 — PHẢN BIỆN (sau khi đã ghi blind). Nhận gói + JSON của M1.
Tìm chỗ M1 SAI hoặc THIẾU: `missed[]` (yếu tố có trong gói mà M1 bỏ qua, kèm nguồn + ngày ≤ T,
`verifiable`=true chỉ khi trỏ được đúng phần tử gói), `disagree[]` (trường của M1 bạn không đồng ý +
vì sao + nguồn). Không tìm được ⇒ để mảng rỗng; bịa lỗi tệ hơn im lặng. JSON theo `schema_M2.json#challenge`.
