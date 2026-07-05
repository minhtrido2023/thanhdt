# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## R&D Q3 program (review 8L + V2.4/V2.5, plan file li-n-quan-n-thi-t-wondrous-zephyr.md, user duyệt 2026-07-05)

### Sự cố usage-limit 2026-07-05 (đã xử lý)
3 deep-research workflow Phase A (A2/A3/A5) bắn song song ~100 sub-agent/cái đã ăn hết usage-limit
5h chung tài khoản → khiến Taylor T2 (panel-ext H4/H5/H6) + T3 (DSR/PBO annex) fail ngay ("session
limit resets 2pm ICT"), KHÔNG được auto-queue vào bus/pending_resumes (cơ chế mục 6 không bắt được
ca này — cần điều tra thêm sau, không chặn tiến độ). Window đã reset (usage 4% lúc 14:55 ICT) →
đã dispatch lại T2=Taylor_20260705_075638, T3=Taylor_20260705_075644, có wrapper haiku nền chờ.
BÀI HỌC: từ nay KHÔNG bắn >1 deep-research workflow cùng lúc với dispatch Taylor headless đang
chạy — chúng ăn chung usage-limit tài khoản.

### Kết quả đã có (thật, verify được)
- **T1/H1 FSCORE bottom-exclusion**: FAIL ở tầng proxy → H1 ĐÓNG, không lên harness (Taylor_20260705_020935).
- **A2 quality-exclusion, A3 vol-managed, A5 EM/VN factor**: workflow "completed" nhưng lớp adversarial-verify
  bị usage-limit đánh sập TOÀN BỘ (hàng trăm lỗi "session limit" khi verify từng claim) → summary tự
  động ghi "all refuted" là ARTIFACT của lỗi hạ tầng, KHÔNG PHẢI nội dung sai. Raw claims vẫn trích
  nguồn thật (JFE/JF/ScienceDirect/JFQA — Barroso-Santa-Clara 2015, Cederburg 2020, Piotroski/Verdad
  exclusion-vs-tilt, Hanauer-Lauterbach EM value, momentum-VN 2007-2015 study...) — dùng làm literature
  grounding directional, KHÔNG cite như "verified fact". Không re-run 3 cái này (quá tốn, ~1.4M token/cái).
- **A1 multiple-testing/DSR**: đang chạy (wf_0746eead-02e), bắn riêng lẻ sau khi rút bài học trên.

### Còn lại theo plan
- A4 (lottery/MAX) + A6 (ML-limits): CHƯA bắn — bắn SAU KHI T2/T3 xong (tránh chồng usage lần nữa).
- Wave 1: H1 đã đóng (không cần harness). H3 (vol-managed BAL) chờ đọc xong A3 nội dung thật (dù
  verify-layer hỏng, nội dung Barroso-SC/Cederburg vẫn dùng được để thiết kế). H7 proxy, H8 audit —
  chưa bắn, chờ T2/T3 xong trước (ưu tiên panel-extension vì 3 hypothesis H4/H5/H6 phụ thuộc nó).
- Budget Taylor: đã dùng 3 dispatch thật (1 xong H1, 2 đang chạy lại T2/T3) trong ngân sách ≤16.

